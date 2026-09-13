# Lead Management Platform

This application fulfils the lead-intake assignment: a public Next.js form creates a `PENDING` lead with a CV, sends notifications through Mailgun, and an authenticated attorney dashboard can review the lead and mark it `REACHED_OUT`. The APIs are FastAPI services. Kubernetes manifests for the workload are in `kubernetes/`; shared platform services are managed by the sibling `common_infra` repository through Argo CD.

## Why these platform services

| Service | Responsibility in this application | Why it fits |
| --- | --- | --- |
| **Keycloak** | Authenticates the internal attorney dashboard and API; issues OIDC tokens with `attorney` and `admin` roles. | The prospect form must remain public, but lead data and CVs are sensitive. Keycloak provides a standard OIDC login, centralized users and role-based access control without adding password storage or a bespoke user table to the application. The API verifies signed tokens and enforces the roles before it exposes leads, resumes, or the state transition. |
| **MinIO** | Stores CV/resume objects in the private `lead-resumes` bucket. PostgreSQL stores only the object key and file metadata. | Files are not a good fit for relational rows: object storage handles binary uploads independently of lead records and is easier to scale, back up, and retain. The bucket is internal-only and is accessed with a narrowly scoped S3 credential; the app streams a resume only after the attorney API has authorized the caller. MinIO gives the local Kubernetes environment an S3-compatible implementation, so the same storage interface can later point to managed S3. |
| **CloudNativePG / PostgreSQL** | Persists lead identity, contact data, CV metadata, state, timestamps, and the attorney who completed outreach. | Lead creation and the one-way `PENDING` → `REACHED_OUT` change require durable, transactional state and straightforward querying for the internal list. CloudNativePG makes PostgreSQL a Kubernetes-native, declaratively managed service with persistent storage. Separate database roles for intake, attorney API, and Keycloak limit access by service; Keycloak also has its own database, so application APIs never touch identity data directly. |

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

### Prerequisites

Install and start Docker, a Kind cluster, `kubectl`, Helm, and the Argo CD CLI or UI. Clone this repository beside [`common_infra`](../common_infra). This local setup uses the shared PostgreSQL/CloudNativePG, MinIO, Keycloak, and application-secret manifests from `common_infra`; do not commit real Mailgun or production credentials.

### 1. Start the local registry and shared platform

From the `common_infra` repository:

```powershell
.\local-registry\setup.ps1
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm upgrade --install argocd argo/argo-cd --namespace argocd --create-namespace
kubectl apply -f .\argocd\root-application.yaml
```

Argo CD then reconciles CloudNativePG/PostgreSQL, MinIO, Keycloak, and the law-application secret and workload applications. Check that the dependencies are ready before continuing:

```powershell
kubectl get pods -n database
kubectl get pods -n minio
kubectl get pods -n keycloak
kubectl get pods -n law-application
```

### 2. Build and publish the application images

From this repository, build the tags referenced by `kubernetes/` and publish them to the local registry:

```powershell
docker build -t localhost:5000/law/lead-intake-api:0.1.5 .\services\lead-intake-api
docker build -t localhost:5000/law/attorney-api:0.1.1 .\services\attorney-api
docker build -t localhost:5000/law/public-web:0.2.5 .\apps\public-web
docker build -t localhost:5000/law/attorney-web:0.2.3 .\apps\attorney-web

docker push localhost:5000/law/lead-intake-api:0.1.5
docker push localhost:5000/law/attorney-api:0.1.1
docker push localhost:5000/law/public-web:0.2.5
docker push localhost:5000/law/attorney-web:0.2.3
```

For a direct local deployment instead of waiting for Argo CD reconciliation:

```powershell
kubectl apply -k .\kubernetes
kubectl rollout status deployment/lead-intake-api -n law-application
kubectl rollout status deployment/attorney-api -n law-application
```

### 3. Open the application

In separate PowerShell windows, forward the local services:

```powershell
kubectl port-forward -n law-application svc/public-web 3000:3000
kubectl port-forward -n law-application svc/lead-intake-api 8000:8000
kubectl port-forward -n law-application svc/attorney-web 3001:3001
kubectl port-forward -n keycloak svc/keycloak 8082:8082
```

Open `http://localhost:3000` to submit a lead and `http://localhost:3001` for the attorney dashboard. The public web app defaults to the locally forwarded intake API at port 8000. The dashboard redirects to Keycloak at port 8082; use a seeded user with the `attorney` or `admin` realm role.

After submitting a lead, verify the full workflow in the attorney dashboard: log in, confirm the lead appears, download its CV, and mark it `REACHED_OUT`.
