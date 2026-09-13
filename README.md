# Lead Management Platform

This application fulfils the lead-intake assignment: a public Next.js form creates a `PENDING` lead with a CV, sends notifications through Mailgun, and an authenticated attorney dashboard can review the lead and mark it `REACHED_OUT`. The APIs are FastAPI services. Kubernetes manifests for the workload are in `kubernetes/`; shared platform services are managed by the sibling `common_infra` repository through Argo CD.

## Why these platform services

| Service | Responsibility in this application | Why it fits |
| --- | --- | --- |
| **Keycloak** | Authenticates the internal attorney dashboard and API; issues OIDC tokens with `attorney` and `admin` roles. | The prospect form must remain public, but lead data and CVs are sensitive. Keycloak provides a standard OIDC login, centralized users and role-based access control without adding password storage or a bespoke user table to the application. The API verifies signed tokens and enforces the roles before it exposes leads, resumes, or the state transition. |
| **MinIO** | Stores CV/resume objects in the private `lead-resumes` bucket. PostgreSQL stores only the object key and file metadata. | Files are not a good fit for relational rows: object storage handles binary uploads independently of lead records and is easier to scale, back up, and retain. The bucket is internal-only and is accessed with a narrowly scoped S3 credential; the app streams a resume only after the attorney API has authorized the caller. MinIO gives the local Kubernetes environment an S3-compatible implementation, so the same storage interface can later point to managed S3. |
| **CloudNativePG / PostgreSQL** | Persists lead identity, contact data, CV metadata, state, timestamps, and the attorney who completed outreach. | Lead creation and the one-way `PENDING` → `REACHED_OUT` change require durable, transactional state and straightforward querying for the internal list. CloudNativePG makes PostgreSQL a Kubernetes-native, declaratively managed service with persistent storage. Separate database roles for intake, attorney API, and Keycloak limit access by service; Keycloak also has its own database, so application APIs never touch identity data directly. |
| **Mailgun** | Sends the post-submission acknowledgement to the prospect and the new-lead alert to the attorney mailbox. | It is a managed transactional email API, so the application does not need to operate SMTP infrastructure or store email credentials in code. The intake API calls Mailgun only after it has persisted the lead and CV, and retries each message up to three times with exponential backoff. A final email failure does not delete the accepted lead; manual attorney follow-up is the deliberate v1 fallback rather than claiming exactly-once delivery. |

## How the pieces work together

```text
Prospect -> public Next.js -> lead-intake FastAPI -> PostgreSQL (lead metadata)
                                            |-> MinIO (private CV)
                                            `-> Mailgun (prospect + attorney emails)

Attorney -> Keycloak OIDC -> attorney Next.js -> attorney FastAPI
                                                  |-> PostgreSQL (read/update state)
                                                  `-> MinIO (authorized CV download)
```

The split keeps the public write path deliberately small and prevents direct public access to either the database or object storage. The authenticated API, rather than MinIO, is the CV download boundary.

## Related documentation

- [Product requirements](docs/PRD.md)
- [High-level design](docs/HLD.md)
- [Application Kubernetes manifests](kubernetes/)

## Run locally

Follow the cross-platform [local run guide](RUN_LOCAL.md).
