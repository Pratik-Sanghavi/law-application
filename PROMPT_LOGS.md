# Planning Session Excerpts

Selected verbatim excerpts from the local planning session that initiated this application. Editorial omissions are marked with `[...]`; credentials, tokens, and private operational data are excluded.

Source transcript: `C:\Users\Pratik Sanghavi\.codex\sessions\2026\09\12\rollout-2026-09-12T11-49-25-01a096f3-f52b-7b32-8524-7b91dd8dc3da.jsonl`.

## Problem statement and planning constraints

**User**

> Develop an application to support creating, getting and updating leads. A lead is a form PUBLICLY available for prospects to fill in, the required fields include,
>
> first name
>
> last name
>
> email
>
> resume / CV
>
> Once the lead is submitted by a prospect, the application will send emails to both the prospect and an attorney inside the company.
>
> In addition, the application powers an internal UI guarded by auth to render a list of leads with all the information filled in by the prospect. Each lead also has a state, it starts with a PENDING state and transitions to REACHED_OUT when marked manually by an attorney after he / she reaches out to the prospect.
>
> Tech Requirements
>
> Create a system design to fulfill the above requirements
>
> Develop the web app & APIs E2E using coding agents of your choice
>
> The APIs need to be implemented using FastAPI and the web app using NextJS
>
> Add a storage to persist data and integrate with an email service
>
> Properly structure the code similar to how you would for a production level repo This is the problem statement and tech requirements. What I'm thinking is using mailgun and minio for the resume storage. We're in the plan mode. In the law application repository create a new folder for all the design documentation. We will write the PRD and HLD. Please lets first clarify scope. We already use postgres for the data. What i want is for us to first accumulate all the common infra before we start working on the applications themselves. Remember internal ui is guarded by auth so we'll have a set of internal users as well in addition to the public form to gather leads so the schema will evolve that way. Lets first clarify my thought process

**Assistant**

> I'll keep this at the infrastructure-and-design stage for now: first ground the existing `law-application` repository and shared platform, then pin down product boundaries before proposing the PRD/HLD and infrastructure plan. I won't create files or deploy anything while we're in plan mode.

## Initial architecture agreement

**Assistant**

> The platform has no ingress controller, Keycloak, MinIO, or mail component yet. PostgreSQL and Temporal are healthy, so the clean plan is to add the remaining shared services to `common_infra`, then build application code only after those contracts are documented.
>
> One platform decision matters for proper separation: use the existing CloudNativePG cluster but give each stateful service its own database and credentials—`law_leads` for the FastAPI service and `keycloak` for Keycloak—rather than sharing the existing generic `app` user.

**Assistant**

> That split makes sense, with one important refinement:
>
> - `lead-intake-api` is anonymous and gets only the `leads` database credential; it creates leads, stores the CV in MinIO, and starts the Temporal notification workflow.
> - `attorney-api` requires a Keycloak access token and gets its own `leads` database credential for read/update operations. It does not need direct credentials to Keycloak's user database—Keycloak owns identity storage and embeds the attorney/admin role in OIDC tokens.
> - Keycloak alone connects to its own `keycloak` database. We disable public self-registration and create internal users administratively.
>
> That delivers the separation you want without letting either application API read password hashes or Keycloak tables.

## Proposed implementation plan

**Assistant**

> Build a local Kubernetes-hosted lead platform with:
>
> - Public Next.js form for first name, last name, email, and CV upload.
> - Separate internal Next.js attorney dashboard protected by Keycloak OIDC.
> - Two FastAPI services: a least-privilege public intake API and an authenticated attorney API.
> - PostgreSQL lead data, private MinIO CV storage, Mailgun email delivery, and Temporal-based reliable notification workflows.
> - Argo CD deployment from `law-application/kubernetes`, while `common_infra` continues to own shared infrastructure and the Argo watcher.
>
> Before application code, create `law-application/docs/PRD.md` and `law-application/docs/HLD.md`, then provision all shared dependencies in `common_infra`.

## Plan-to-implementation transition

**User**

> lets add this in a docs folder in the law application: C:\Users\Pratik Sanghavi\Desktop\Projects\k8s_projects\law-application

**Assistant**

> I can add `docs/PRD.md` and `docs/HLD.md` under `law-application` once we leave Plan Mode. The proposed plan already specifies their contents; Plan Mode prevents me from creating files yet.

**User**

> lets leave plan mode then...

**Assistant**

> I'll create the design docs in `law-application` now, based on the agreed architecture, and leave application implementation for the next step.

## Later scope correction

**User**

> also lets cut down scope. We won't have a temporal worker. Rather lets just trigger the email from the backends itself and then wait for success (retry reasonably). We will also update the HLD/PRD as needecxd

The implemented design follows this later scope decision: the intake API sends email directly with bounded retries rather than using a Temporal worker.