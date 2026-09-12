import logging
from datetime import datetime,timezone
from uuid import uuid4
from botocore.exceptions import BotoCoreError,ClientError
from fastapi import APIRouter,File,Form,HTTPException,Request,UploadFile,status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.core.mailer import MailgunDeliveryError
from app.core.uploads import read_and_validate_resume
from app.models import Lead,LeadState
from app.schemas import LeadCreated,LeadInput
logger=logging.getLogger(__name__); router=APIRouter()
@router.get("/healthz")
async def healthz(): return {"status":"ok"}
@router.get("/readyz")
async def readyz(request:Request):
    try:
        async with request.app.state.session_factory() as session: await session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc: raise HTTPException(503,"database unavailable") from exc
    return {"status":"ready"}
@router.post("/v1/leads",response_model=LeadCreated,status_code=status.HTTP_201_CREATED)
async def create_lead(request:Request,first_name:str=Form(...),last_name:str=Form(...),email:str=Form(...),resume:UploadFile=File(...)):
    lead_input=LeadInput(first_name=first_name,last_name=last_name,email=email); document=await read_and_validate_resume(resume,request.app.state.settings.max_resume_bytes); lead_id=uuid4(); object_key=f"leads/{lead_id}/resume"; uploaded=False
    try:
        await request.app.state.storage.put(object_key,document.content,document.content_type); uploaded=True
        async with request.app.state.session_factory() as session:
            async with session.begin():
                lead=Lead(id=lead_id,first_name=lead_input.first_name,last_name=lead_input.last_name,email=str(lead_input.email).lower(),resume_object_key=object_key,resume_filename=document.filename,resume_content_type=document.content_type,resume_size_bytes=len(document.content),resume_sha256=document.sha256,state=LeadState.PENDING); session.add(lead); await session.flush(); created_at=lead.created_at or datetime.now(timezone.utc)
    except (BotoCoreError,ClientError) as exc: raise HTTPException(502,"resume storage unavailable") from exc
    except SQLAlchemyError as exc:
        if uploaded:
            try: await request.app.state.storage.delete(object_key)
            except (BotoCoreError,ClientError): logger.exception("resume cleanup failed")
        raise HTTPException(503,"lead service unavailable") from exc
    try: await request.app.state.mailer.send_submission(lead.first_name,lead.last_name,lead.email)
    except MailgunDeliveryError as exc: raise HTTPException(502,"lead accepted but email delivery failed") from exc
    return LeadCreated(id=lead_id,state=LeadState.PENDING.value,created_at=created_at)