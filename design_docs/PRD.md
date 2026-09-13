# Lead Management Platform â€” Product Requirements Document

## Purpose

Provide a dependable intake flow for prospective legal clients and an internal workspace for attorneys to review and follow up with submitted leads.

## Users

- **Prospect:** submits their contact details and resume/CV through a public form.
- **Attorney:** signs in to review leads, access resumes, and record that they reached out.
- **Administrator:** has the same lead-management capabilities as an attorney and manages internal access in Keycloak.

## V1 requirements

### Public intake

- The public form collects exactly four required fields: first name, last name, email, and resume/CV.
- Accepted documents are PDF, DOC, and DOCX, limited to 10 MB.
- A valid submission creates a lead in `PENDING` state and persists its document securely.
- The system sends an acknowledgment email to the prospect and an intake notification to the configured attorney mailbox.
- The form is rate-limited at the ingress layer. CAPTCHA is out of scope for v1.

### Internal lead management

- The internal dashboard requires Keycloak login and allows only users with the `attorney` or `admin` role.
- Attorneys can search, filter, paginate, and inspect submitted leads.
- Lead details include all submitted data, document download access, delivery history, and outreach state.
- Leads have a one-way state transition from `PENDING` to `REACHED_OUT`.
- Marking a lead as reached out records the acting attorney and timestamp immediately.
- The attorney can send either a default future Mailgun-template outreach email or custom subject/body content to the prospect.

## Reliability and security

- The lead is accepted once its database transaction succeeds; email delivery continues asynchronously and is retried independently.
- Resumes remain private in object storage and are available only through authorized application endpoints.
- Internal identity, users, and roles are owned by Keycloak. There is no application-managed user table or public registration.
- Credentials and externally configurable values are supplied through Kubernetes secrets/configuration and never committed.

## Out of scope for v1

- Public internet exposure, ngrok, CAPTCHA, self-registration, lead reassignment, lead reopening, additional lead states, and local email emulation.
- Any final wording or design for the default attorney outreach Mailgun template.

## Success criteria

1. A prospect can submit a valid lead and CV through the public URL.
2. The lead and document remain available after pod restart.
3. The intake API waits for Mailgun delivery after persisting the lead and retries each email up to three times with exponential backoff. If delivery still fails, it returns an error while retaining the lead for manual follow-up.
4. An authenticated attorney can find a lead, download its CV, and mark it `REACHED_OUT`.
5. Unauthorized users cannot access internal leads, documents, or internal APIs.
