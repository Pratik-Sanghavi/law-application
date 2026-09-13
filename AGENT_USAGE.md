# Coding-agent usage

I used Codex as a collaborative coding agent for repository inspection, implementation support, documentation drafting, and review. Its most useful role was accelerating the mechanical work: tracing configuration across the FastAPI services, Next.js applications, Kubernetes manifests, and the separate `common_infra` repository; drafting the design rationale; and turning the verified deployment configuration into runnable commands.

I delegated bounded tasks to the agent: locating the Keycloak, MinIO, CloudNativePG, Mailgun, image, and service configuration; checking that documentation matched the manifests; and preparing focused README/runbook edits. I retained responsibility for the product decisions and review: the public form remains unauthenticated, the attorney workspace is role-protected, resumes stay private behind the application API, and `PENDING` can only move to `REACHED_OUT`. I also reviewed every proposed change as a diff before treating it as part of the submission.

