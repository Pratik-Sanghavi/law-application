from datetime import datetime, timezone
from uuid import UUID
import boto3
from botocore.config import Config
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy import select, text
from app.core.auth import current_attorney
from app.core.config import get_settings
from app.models import Lead, LeadState
from app.schemas import LeadPage, LeadResponse, LeadStateUpdate

router = APIRouter()
@router.get("/healthz")
async def healthz(): return {"status": "ok"}
@router.get("/readyz")
async def readyz(request: Request):
    async with request.app.state.sessions() as session: await session.execute(text("SELECT 1"))
    return {"status": "ready"}
@router.get("/v1/leads", response_model=LeadPage)
async def list_leads(request: Request, offset: int = 0, limit: int = 50, _: dict = Depends(current_attorney)):
    limit = min(max(limit, 1), 100)
    async with request.app.state.sessions() as session: rows = (await session.scalars(select(Lead).order_by(Lead.created_at.desc()).offset(offset).limit(limit + 1))).all()
    return {"items": rows[:limit], "next_offset": offset + limit if len(rows) > limit else None}
@router.get("/v1/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: UUID, request: Request, _: dict = Depends(current_attorney)):
    async with request.app.state.sessions() as session: lead = await session.get(Lead, lead_id)
    if not lead: raise HTTPException(404, "Lead not found")
    return lead
@router.get("/v1/leads/{lead_id}/resume")
async def download_resume(lead_id: UUID, request: Request, _: dict = Depends(current_attorney)):
    async with request.app.state.sessions() as session: lead = await session.get(Lead, lead_id)
    if not lead: raise HTTPException(404, "Lead not found")
    s = get_settings(); client = boto3.client("s3", endpoint_url=s.s3_endpoint, region_name=s.s3_region, aws_access_key_id=s.s3_access_key, aws_secret_access_key=s.s3_secret_key, config=Config(signature_version="s3v4"))
    try: obj = client.get_object(Bucket=s.s3_bucket, Key=lead.resume_object_key)
    except Exception as exc: raise HTTPException(502, "Resume storage unavailable") from exc
    return Response(content=obj["Body"].read(), media_type=lead.resume_content_type, headers={"Content-Disposition": f'attachment; filename="{lead.resume_filename}"'})
@router.patch("/v1/leads/{lead_id}/state", response_model=LeadResponse)
async def update_state(lead_id: UUID, body: LeadStateUpdate, request: Request, claims: dict = Depends(current_attorney)):
    if body.state != LeadState.REACHED_OUT.value: raise HTTPException(422, "Only transition to REACHED_OUT is allowed")
    async with request.app.state.sessions() as session:
        async with session.begin():
            lead = await session.get(Lead, lead_id, with_for_update=True)
            if not lead: raise HTTPException(404, "Lead not found")
            if lead.state != LeadState.PENDING: raise HTTPException(409, "Lead has already been reached out to")
            lead.state = LeadState.REACHED_OUT; lead.reached_out_at = datetime.now(timezone.utc); lead.reached_out_by_subject = claims.get("sub")
        await session.refresh(lead)
    return lead