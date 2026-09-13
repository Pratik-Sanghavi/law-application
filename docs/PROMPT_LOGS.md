# Representative Prompt Logs

This document contains representative, sanitized excerpts from the implementation sessions for the Lead Management Platform. It is intended to show the reasoning, scope decisions, and debugging approach used during development. Credentials, tokens, personal secrets, and raw customer data are excluded.

## 1. Scope and architecture

> Develop an application to support creating, getting and updating leads. A lead is a publicly available form for prospects to fill in with first name, last name, email, and resume/CV. After submission, notify the prospect and an attorney. Provide an authenticated internal UI where attorneys can review leads and mark them as reached out.

**Outcome:** The solution was split into a public Next.js lead form, a FastAPI intake service, an authenticated Next.js attorney dashboard, and a FastAPI attorney service. PostgreSQL stores lead metadata and workflow state; MinIO stores CVs; Keycloak provides OIDC authentication and role-based access; Mailgun sends transactional email.

## 2. Infrastructure-first decision

> We already use Postgres for data. First accumulate all common infrastructure before working on applications. We will also need internal users and database roles.

**Outcome:** Shared infrastructure was provisioned through Argo CD: CloudNativePG/PostgreSQL, MinIO, Keycloak, local container registry, and supporting namespaces. Database credentials were scoped to the intake service, attorney API, Keycloak, and the previously considered notification service.

## 3. Simplified notification design

> Cut down scope. We will not have a Temporal worker. Trigger email from the backends directly and wait for success with reasonable retries.

**Outcome:** The lead intake API persists the lead and CV first, then sends prospect acknowledgement and attorney-alert emails using Mailgun. Each delivery uses bounded retry logic. The v1 design intentionally does not claim exactly-once email delivery.

## 4. Private repository access for GitOps

> How do I configure Argo CD to watch private repositories?

**Outcome:** Argo CD repository credentials were configured separately from application manifests. Application definitions point to the private application and infrastructure repositories while credentials remain Kubernetes secrets rather than committed configuration.

## 5. Large CloudNativePG CRD reconciliation failure

> CustomResourceDefinition is invalid: metadata.annotations: Too long.

**Outcome:** The Argo CD application was configured to use server-side apply for the CloudNativePG chart. This avoids client-side apply annotations exceeding the Kubernetes annotation size limit when applying large CRDs.

## 6. Local image registry troubleshooting

> Failed to pull image from localhost:5000 through the registry mirror.

**Outcome:** Images are pushed to the local registry and also imported into the Docker Desktop Kubernetes node containerd cache. Deployments use `imagePullPolicy: IfNotPresent`, which keeps local development reliable when the registry mirror is unavailable.

## 7. OIDC callback and logout

> Invalid parameter: redirect_uri.

**Outcome:** The attorney web client uses a stable external base URL (`http://localhost:3001`) for redirect URI construction while using internal Kubernetes service URLs for server-to-server token exchange. Logout clears local session cookies, performs a `303 See Other`, and calls Keycloak's end-session endpoint before returning to the dashboard URL.

## 8. Public lead submission debugging

> The browser network panel shows `201 Created`, but the UI still says it could not submit the application.

**Outcome:** The API had successfully persisted the lead. The issue was client-side: the React event target was used after an asynchronous request. The handler now captures `FormData` synchronously before `await` and, after a successful response, immediately renders the confirmation screen. The intake API also sets explicit CORS rules for the local public UI origin.

## 9. Attorney dashboard freshness

> Refresh and marking a lead reached out do not show the new status unless using an incognito session.

**Outcome:** The attorney client fetches lead data with `cache: "no-store"`; the Next.js lead proxy fetch and response also disable caching. This makes the Refresh action and status update reflect the current PostgreSQL state in the same browser session.

## Validation checklist

- Public submission returns `201 Created` and creates a `PENDING` lead in PostgreSQL.
- Resume is stored in the private MinIO bucket.
- Prospect and attorney notification requests are sent through Mailgun.
- An authenticated attorney can list leads, download a CV, and transition a lead to `REACHED_OUT`.
- Attorney logout ends the local and Keycloak sessions.
- Public and attorney interfaces run from locally built images deployed through GitOps.