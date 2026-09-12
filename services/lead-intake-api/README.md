# Lead intake API

Public FastAPI endpoint for creating a `PENDING` lead and storing its CV privately in MinIO.

The API accepts only PDF, DOC, and DOCX files up to 10 MB. It inserts a `lead-submitted` event into PostgreSQL in the same transaction as the lead record; the Temporal worker will consume that outbox event later.

Environment is injected by Kubernetes secrets/config maps. Migrations are intentionally run by the `attorney_api` database owner, not this service.