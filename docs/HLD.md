# Lead Management Platform ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â High-Level Design

## Architecture

The platform is deployed to the local Kubernetes cluster through Argo CD. `common_infra` owns shared components and watches this repository's `kubernetes/` path; this repository owns the lead application workloads only.

```text
Prospect -> apply.law.local -> public Next.js -> lead-intake-api -> PostgreSQL (leads)
                                                     |                  |
                                                     v                  v
                                                   MinIO          direct Mailgun delivery
                                                                          |
Attorney -> attorney.law.local -> attorney Next.js -> attorney-api ------+-> Mailgun
             |                       |                   |
             +-> auth.law.local -----+-------------------+-> Keycloak OIDC
```

## Components

- **Traefik:** local ingress, hostname routing, and public intake rate limiting.
- **Public Next.js app:** renders the four-field lead form and submits multipart content to the intake API.
- **Lead intake API (FastAPI):** validates fields and document restrictions, streams uploads to MinIO, creates `PENDING` leads, then delivers the prospect acknowledgement and attorney alert directly through Mailgun.
- **Attorney Next.js app:** Keycloak-authenticated dashboard for lead search, details, document access, and outreach.
- **Attorney API (FastAPI):** validates Keycloak bearer tokens/roles, exposes lead read APIs, authorizes document streams, and records the `PENDING` to `REACHED_OUT` action.
- **PostgreSQL / CloudNativePG:** persistent lead records and outreach records.
- **MinIO:** persistent private CV object storage using a `lead-resumes` bucket.
- **Keycloak:** source of truth for internal users and `attorney`/`admin` realm roles; it uses its own isolated database.
- **Mailgun:** sole outbound email provider for prospect acknowledgements, attorney intake alerts, and outreach email. `attorney@mail.pratiksanghavi.in` is a sending identity only; attorney alerts and reply-to traffic are statically forwarded to `sanghavipratikr@gmail.com` until a real shared mailbox exists.

## Data and permissions

### Lead data

`leads` stores a UUID, first name, last name, normalized email, CV object metadata, state, timestamps, and reached-out actor metadata. `lead_events`/`outreach` retain immutable activity metadata. Email delivery state is not persisted in v1.

### Database access

- The intake API has a dedicated database principal limited to creating leads and uploads.
- The attorney API uses a separate principal for lead reads, state updates, and outreach audit records.
- Keycloak uses its own database and credential; neither application API accesses Keycloak's database.

## API surface

- `POST /v1/leads`: public multipart submission; returns a created lead identifier and accepted state.
- `GET /v1/leads`: attorney/admin list endpoint with search, state filter, and pagination.
- `GET /v1/leads/{id}`: attorney/admin lead detail.
- `GET /v1/leads/{id}/resume`: authenticated, authorized CV stream; MinIO is never directly exposed.
- `POST /v1/leads/{id}/reach-out`: attorney/admin-only one-way transition, including either default-template selection or custom email subject/body.

## Workflows

1. Intake persists the lead and CV, then waits for Mailgun to deliver both emails. Each message is retried three times with exponential backoff.
2. A final email failure returns an error but intentionally does not delete the accepted lead; an attorney can follow up manually. This is a v1 trade-off: delivery is not durable or exactly-once.
3. An attorney transition records `REACHED_OUT` and its actor/timestamp.

## Deployment and local access

- Images are pushed to `localhost:5000` and pulled in-cluster from `kind-registry:5000`.
- The app manifests live under `kubernetes/` and are reconciled by the existing Argo CD watcher.
- Local hostnames are `apply.law.local`, `attorney.law.local`, and `auth.law.local`; developer hosts-file mappings point them at the local ingress endpoint.
- Required secrets include PostgreSQL credentials, Keycloak bootstrap/client configuration, MinIO credentials, Mailgun API key/domain/sender, and universal attorney intake address.

## Failure handling

- Invalid form data and unsupported files are rejected before storage.
- Upload/database failures return an error and do not create a partial lead.
- Mailgun failures do not discard accepted leads; the intake request returns an error after three attempts and requires manual follow-up.
- No background worker or durable retry queue is in scope for v1.
