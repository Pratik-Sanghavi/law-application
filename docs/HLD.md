# Lead Management Platform â€” High-Level Design

## Architecture

The platform is deployed to the local Kubernetes cluster through Argo CD. `common_infra` owns shared components and watches this repository's `kubernetes/` path; this repository owns the lead application workloads only.

```text
Prospect -> apply.law.local -> public Next.js -> lead-intake-api -> PostgreSQL (leads)
                                                     |                  |
                                                     v                  v
                                                   MinIO          transactional outbox
                                                                          |
Attorney -> attorney.law.local -> attorney Next.js -> attorney-api ------+-> Temporal worker -> Mailgun
             |                       |                   |
             +-> auth.law.local -----+-------------------+-> Keycloak OIDC
```

## Components

- **Traefik:** local ingress, hostname routing, and public intake rate limiting.
- **Public Next.js app:** renders the four-field lead form and submits multipart content to the intake API.
- **Lead intake API (FastAPI):** validates fields and document restrictions, streams uploads to MinIO, creates `PENDING` leads, and writes an outbox event in the same PostgreSQL transaction.
- **Attorney Next.js app:** Keycloak-authenticated dashboard for lead search, details, document access, and outreach.
- **Attorney API (FastAPI):** validates Keycloak bearer tokens/roles, exposes lead read APIs, authorizes document streams, and records the `PENDING` to `REACHED_OUT` action.
- **Temporal worker:** dedicated non-HTTP deployment that starts workflows from outbox records and performs retryable Mailgun delivery.
- **PostgreSQL / CloudNativePG:** persistent lead records, audit/outreach records, delivery state, and the transactional outbox.
- **MinIO:** persistent private CV object storage using a `lead-resumes` bucket.
- **Keycloak:** source of truth for internal users and `attorney`/`admin` realm roles; it uses its own isolated database.
- **Mailgun:** sole outbound email provider for prospect acknowledgements, attorney intake alerts, and outreach email. `attorney@mail.pratiksanghavi.in` is a sending identity only; attorney alerts and reply-to traffic are statically forwarded to `sanghavipratikr@gmail.com` until a real shared mailbox exists.

## Data and permissions

### Lead data

`leads` stores a UUID, first name, last name, normalized email, CV object metadata, state, timestamps, and reached-out actor metadata. `lead_events`/`outreach` retain immutable activity metadata. `notification_outbox` and delivery records support idempotent dispatch and retry tracking.

### Database access

- The intake API has a dedicated database principal limited to creating leads and their related upload/outbox records.
- The attorney API uses a separate principal for lead reads, state updates, and outreach audit records.
- The Temporal worker uses a dedicated principal restricted to the notification/outbox and minimum lead contact data it needs.
- Keycloak uses its own database and credential; neither application API accesses Keycloak's database.

## API surface

- `POST /v1/leads`: public multipart submission; returns a created lead identifier and accepted state.
- `GET /v1/leads`: attorney/admin list endpoint with search, state filter, and pagination.
- `GET /v1/leads/{id}`: attorney/admin lead detail.
- `GET /v1/leads/{id}/resume`: authenticated, authorized CV stream; MinIO is never directly exposed.
- `POST /v1/leads/{id}/reach-out`: attorney/admin-only one-way transition, including either default-template selection or custom email subject/body.

## Workflows

1. Intake writes the lead and `lead-submitted` outbox event atomically.
2. The worker idempotently starts a Temporal workflow that emails the prospect acknowledgement and forwards the attorney intake alert to `sanghavipratikr@gmail.com` through Mailgun. The Mailgun sender identity is not treated as a mailbox.
3. An attorney's reach-out action updates the state and writes an outreach event/outbox event atomically.
4. A second idempotent workflow sends the selected default-template or custom Mailgun email. The state remains `REACHED_OUT` even if delivery must retry; workflow/delivery status provides visibility.

## Deployment and local access

- Images are pushed to `localhost:5000` and pulled in-cluster from `kind-registry:5000`.
- The app manifests live under `kubernetes/` and are reconciled by the existing Argo CD watcher.
- Local hostnames are `apply.law.local`, `attorney.law.local`, and `auth.law.local`; developer hosts-file mappings point them at the local ingress endpoint.
- Required secrets include PostgreSQL credentials, Keycloak bootstrap/client configuration, MinIO credentials, Mailgun API key/domain/sender, and universal attorney intake address.

## Failure handling

- Invalid form data and unsupported files are rejected before storage.
- Upload/database failures return an error and do not create a partial lead.
- Mailgun failures do not discard accepted leads; Temporal retries them and records status.
- Duplicate outbox processing is prevented with stable workflow IDs and persisted event status.
