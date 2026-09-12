"""remove retired notification outbox

Revision ID: 0002_remove_notification_outbox
Revises: 0001_create_leads
"""
from alembic import op
revision = "0002_remove_notification_outbox"
down_revision = "0001_create_leads"
branch_labels = None
depends_on = None
def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS notification_outbox")
def downgrade() -> None:
    pass