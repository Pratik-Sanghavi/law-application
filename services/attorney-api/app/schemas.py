from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
class LeadResponse(BaseModel):
    id: UUID; first_name: str; last_name: str; email: str; resume_filename: str; resume_content_type: str; resume_size_bytes: int; state: str; created_at: datetime; reached_out_at: datetime|None; reached_out_by_subject: str|None
class LeadPage(BaseModel): items: list[LeadResponse]; next_offset: int|None
class LeadStateUpdate(BaseModel): state: str