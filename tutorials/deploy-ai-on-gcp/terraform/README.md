# Reference Terraform module: scheduled AI Cloud Run Job

This is the supporting material for the video: Reference Terraform module: scheduled AI Cloud Run Job.

A drop-in module for any scheduled AI automation on GCP.

## What it creates

- Cloud Run Job
- Cloud Scheduler trigger
- Two service accounts (job + scheduler) with minimum-scope IAM
- Required APIs enabled
- Log-based metric counting ERROR-severity logs from the job
- Alerting policy that fires on the metric
- Cloud Monitoring dashboard (executions, errors, duration, recent logs), toggle with `enable_dashboard`

## Use

```bash
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars

terraform init
terraform plan
terraform apply
```

## Before you apply

- The image must already exist in Artifact Registry. Push it first with `gcloud builds submit`.
- Notification channels must exist before referencing them. Create one in Cloud Console (Monitoring → Alerting → Notification channels) and copy its full resource ID.
- Any secrets in `accessible_secrets` must already exist in Secret Manager.

## Conventions baked in

- Service accounts named `<service>-sa` and `<service>-scheduler-sa`
- Labels `service = <name>` and `environment = <env>` on the job
- Region defaults to `europe-west1`
- Job timeout 600s, max retries 1, memory 512Mi
- Failure threshold 0 (alert on first error)

Override any of these via variables.

## What this module does not do

- Doesn't create a Firestore database (do that once, manually, per project)
- Doesn't manage Secret Manager secret values (use `gcloud secrets create` separately)
- Doesn't push container images (use Cloud Build)
- Doesn't grant `roles/owner` or `roles/editor` to anything

If you need a service or feature beyond this module, fork it. Don't bloat the reference.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
