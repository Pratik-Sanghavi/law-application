"""create lead intake tables

Revision ID: 0001_create_leads
Revises:
Create Date: 2026-09-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_create_leads"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    lead_state = postgresql.ENUM("PENDING", "REACHED_OUT", name="lead_state", create_type=False)
    lead_state.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("resume_object_key", sa.String(length=512), nullable=False, unique=True),
        sa.Column("resume_filename", sa.String(length=255), nullable=False),
        sa.Column("resume_content_type", sa.String(length=128), nullable=False),
        sa.Column("resume_size_bytes", sa.Integer(), nullable=False),
        sa.Column("resume_sha256", sa.String(length=64), nullable=False),
        sa.Column("state", lead_state, nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("reached_out_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reached_out_by_subject", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_leads_email", "leads", ["email"])
    op.create_table(
        "notification_outbox",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("aggregate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("dispatched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_notification_outbox_aggregate_id", "notification_outbox", ["aggregate_id"])
    op.execute("GRANT INSERT ON TABLE leads, notification_outbox TO lead_intake")


def downgrade() -> None:
    op.drop_table("notification_outbox")
    op.drop_index("ix_leads_email", table_name="leads")
    op.drop_table("leads")
    sa.Enum(name="lead_state").drop(op.get_bind(), checkfirst=True)