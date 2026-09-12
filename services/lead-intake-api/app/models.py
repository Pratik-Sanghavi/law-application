import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class LeadState(str, enum.Enum):
    PENDING = "PENDING"
    REACHED_OUT = "REACHED_OUT"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    resume_object_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    resume_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    resume_content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    resume_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    resume_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    state: Mapped[LeadState] = mapped_column(Enum(LeadState, name="lead_state"), nullable=False, default=LeadState.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    reached_out_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reached_out_by_subject: Mapped[str | None] = mapped_column(String(255))
