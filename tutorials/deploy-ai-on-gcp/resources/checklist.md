# Starting a new GCP project for AI work

The order I run when I spin up a new GCP project for AI systems. Adapt the project ID, service name, and region.

## 1. Create the project

```bash
PROJECT_ID="your-service-prod"
gcloud projects create $PROJECT_ID \
  --name="Your Service" \
  --labels=service=your-service,environment=prod
```

Naming convention: `<service>-<environment>`. Always include the environment.

## 2. Link billing

```bash
gcloud billing projects link $PROJECT_ID \
  --billing-account=$BILLING_ACCOUNT_ID
```

Without billing, half the APIs you need won't enable.

## 3. Enable APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  cloudscheduler.googleapis.com \
  secretmanager.googleapis.com \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  --project=$PROJECT_ID
```

Don't pre-enable everything. Audit logs get noisier and cost rises.

## 4. Set the default region

```bash
gcloud config set project $PROJECT_ID
gcloud config set run/region europe-west1
gcloud config set compute/region europe-west1
```

Pin a region. Multi-region adds complexity and cost.

## 5. Initialise Firestore (if used)

```bash
gcloud firestore databases create \
  --location=europe-west1 \
  --type=firestore-native
```

Once per project. Cannot be undone without project deletion.

## 6. Create a notification channel

In the Cloud Console: **Monitoring → Alerting → Notification channels → Add new**. Add Slack (via webhook) or email. You'll need this when the first alert fires.

Copy the channel resource ID. You'll pass it into Terraform.

## 7. Create the Artifact Registry repo

```bash
gcloud artifacts repositories create your-service \
  --repository-format=docker \
  --location=europe-west1 \
  --description="Your service container images"
```

## 8. Add secrets

```bash
echo -n "$SECRET_VALUE" | gcloud secrets create your-secret \
  --replication-policy="automatic" \
  --data-file=-
```

Grant access at the secret level (in Terraform), not project level.

## 9. Build and push the first image

```bash
cd your-service
gcloud builds submit \
  --tag europe-west1-docker.pkg.dev/$PROJECT_ID/your-service/your-service:latest
```

## 10. Apply the Terraform

```bash
cd terraform
terraform init
terraform apply
```

The Terraform module creates the Cloud Run Job, scheduler, IAM, monitoring, and alerting in one apply.

## After this checklist

Project is ready to ship into. Now:

1. Copy `resources/AGENTS.md` into the target repo as `AGENTS.md`
2. Write the spec for the system you're building (`resources/spec.md`)
3. Start working with Codex

## What I do not do at this stage

- Set up VPC peering. Default network is fine until it isn't.
- Configure IAP. Cloud Run handles auth at the service level.
- Add organisation policies. Project-level constraints are enough for most work.
- Pre-create dashboards. Build them when you have data to look at.
