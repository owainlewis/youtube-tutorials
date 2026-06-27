# AGENTS.md

Reference for Codex working in this repo.

## Repo

This repo is the engineering reference behind the [How I Deploy Real AI Systems With OpenAI Codex](#) video. It contains the architecture I use for production AI work on Google Cloud, plus two standalone example apps (email-classifier, proposal-generator) and a reference Terraform module.

The video's primary demo (a customer-support RAG application) lives in a separate repo, linked in the video description.

## Default stack for AI apps on GCP

- Runtime: Python 3.12 or Node 20 on Cloud Run / Cloud Run Jobs
- Inference: Vertex AI (Gemini Flash by default, Claude on Vertex when reasoning quality matters)
- Relational data: Cloud SQL Postgres
- Key-value / state: Firestore
- Blob storage: Cloud Storage
- Secrets: Secret Manager
- Scheduling: Cloud Scheduler
- Observability: Cloud Logging + log-based metrics + Cloud Monitoring alerting
- CI/CD: Cloud Build (single-environment), Cloud Deploy (multi-environment)
- Deployment config: Cloud Build YAML by default. Terraform is used in the email-classifier example as a reference.

## Region

`europe-west1`. Pin a region. Don't multi-region without explicit reason.

## Conventions

### Inference

- All production inference goes through Vertex AI. Never call Anthropic or OpenAI SDKs directly from production code.
- Reason: Vertex has a published SLA tied to the GCP agreement. Direct APIs (standard tier) have no contractual uptime commitment. Inference traffic also stays inside the project's IAM and VPC, with one bill and one observability stack.
- Default model: Gemini Flash. Step up to Pro only when measurably needed. Claude is also available via Vertex if reasoning quality requires it.
- Acceptable exception: day-zero access to a model not yet on Vertex. Rare, time-limited, document the reason.
- Set explicit `max_output_tokens` on every call.
- Log model name, prompt tokens, completion tokens, and latency for every inference.

### IAM

- Minimal scope, every time. No `roles/owner`, no `roles/editor`.
- Per-service service accounts. Naming: `<service>-sa`.
- Grant roles at the resource level when possible (specific secret, specific job), not project level.
- All IAM lives in declarative configuration (Cloud Build YAML or Terraform), not console clicks.

### Secrets

- All secrets in Secret Manager. Mount via env vars at runtime.
- Never commit, never log, never hardcode.
- Rotate quarterly minimum.

### Logging

- Structured JSON logging, one event per line.
- Standard fields: `event`, `service`, `timestamp` (auto), plus event-specific data.
- Print stdout. Cloud Run captures it.
- Severity via the `severity` field for ERROR/WARNING.
- No PII unless reviewed.

### Monitoring and alerting

- Every Cloud Run Job needs:
  - A log-based metric for ERROR-severity entries
  - An alerting policy on that metric
  - A notification channel
  - A Cloud Monitoring dashboard (JSON, checked into version control)
- Set monitoring up at the same time as the job, not after.
- Dashboards are JSON. Generate them from a description of what should be visible, then review and check in.

### Cost

- Cloud Run Jobs scale to zero. Default to that.
- Avoid persistent VMs unless workload genuinely justifies.
- Add `labels = { service = "<name>", environment = "<env>" }` for billing breakdowns.

### Deployment

- Build with Cloud Build, not local Docker.
- Tag images with git SHA, not `latest` (in production).
- Use Cloud Build for production deploys. `gcloud run jobs deploy` is fine for development iteration.

### Testing

- Local: pytest, run with `DRY_RUN=true` against a test inbox.
- Pre-deploy: run once with `LIMIT=5` to verify auth and connectivity.
- Post-deploy: tail logs for the first scheduled run.

## Out of scope (for the agent)

- Don't suggest GKE, Compute Engine, or App Engine.
- Don't suggest serverless functions for jobs that need >9 minutes.
- Don't draft Kubernetes YAML.
- Don't recommend third-party SaaS over GCP-native services without prompting.

## Starting a new feature

1. Read this file in full.
2. Read the relevant deployment config (Cloud Build YAML or, for the email-classifier example, Terraform under `terraform/`).
3. Ask clarifying questions about scope before writing code.
4. Write a spec under `docs/<feature>/spec.md` if the technical approach isn't obvious.
5. Implement, then update the deployment config.
6. Add or update monitoring before declaring done.
