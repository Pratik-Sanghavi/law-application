# Run locally

This guide runs the application on a local Kind Kubernetes cluster. It uses the shared services defined in the sibling `common_infra` repository: CloudNativePG/PostgreSQL, MinIO, Keycloak, and application configuration/secrets.

## Prerequisites

Install Docker, [Kind](https://kind.sigs.k8s.io/), `kubectl`, and Helm. Start Docker, then create or select a Kind cluster:

```sh
kind create cluster
kubectl cluster-info
```

Clone `law-application` and `common_infra` as sibling directories. Provide valid local Mailgun configuration through the `common_infra` application-secret manifests; never commit a real Mailgun API key or production credentials.

## 1. Start the registry and shared platform

From the `common_infra` repository, create an S3/Docker-compatible registry that is reachable both from your host and the Kind nodes:

```sh
if ! docker inspect kind-registry >/dev/null 2>&1; then
  docker run -d --restart=always -p 127.0.0.1:5000:5000 --network kind --name kind-registry registry:2
fi
docker network connect kind kind-registry 2>/dev/null || true
kubectl apply -f local-registry/local-registry-hosting.yaml

helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm upgrade --install argocd argo/argo-cd --namespace argocd --create-namespace
kubectl apply -f argocd/root-application.yaml
```

Argo CD reconciles CloudNativePG/PostgreSQL, MinIO, Keycloak, and the application configuration. Wait for the dependencies to become ready:

```sh
kubectl get pods -n database
kubectl get pods -n minio
kubectl get pods -n keycloak
kubectl get pods -n law-application
```

## 2. Build and publish the application images

From the `law-application` repository, build and push the tags currently referenced by `kubernetes/`:

```sh
docker build -t localhost:5000/law/lead-intake-api:0.1.5 services/lead-intake-api
docker build -t localhost:5000/law/attorney-api:0.1.1 services/attorney-api
docker build -t localhost:5000/law/public-web:0.2.5 apps/public-web
docker build -t localhost:5000/law/attorney-web:0.2.3 apps/attorney-web

docker push localhost:5000/law/lead-intake-api:0.1.5
docker push localhost:5000/law/attorney-api:0.1.1
docker push localhost:5000/law/public-web:0.2.5
docker push localhost:5000/law/attorney-web:0.2.3
```

Apply the application directly for local development (or let Argo CD reconcile its tracked Git revision):

```sh
kubectl apply -k kubernetes/
kubectl rollout status deployment/lead-intake-api -n law-application
kubectl rollout status deployment/attorney-api -n law-application
```

## 3. Open the application

Run each command in a separate terminal:

```sh
kubectl port-forward -n law-application svc/public-web 3000:3000
kubectl port-forward -n law-application svc/lead-intake-api 8000:8000
kubectl port-forward -n law-application svc/attorney-web 3001:3001
kubectl port-forward -n keycloak svc/keycloak 8082:8082
```

Open `http://localhost:3000` to submit a lead and `http://localhost:3001` for the attorney dashboard. The public web app uses the locally forwarded intake API at port 8000. The dashboard redirects to Keycloak at port 8082; sign in with a seeded user assigned the `attorney` or `admin` role.

Verify the end-to-end flow: submit a lead and CV, confirm both Mailgun notifications are delivered, sign in as an attorney, confirm the lead is listed, download its CV, then mark it `REACHED_OUT`.
