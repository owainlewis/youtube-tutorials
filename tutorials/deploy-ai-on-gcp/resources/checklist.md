# Starting A New GCP Project For The Email Classifier

This is the opt-in cloud setup for the checked-in email classifier. Every command in this checklist changes Google Cloud state. Creating a project, linking billing, enabling APIs, storing images, calling a model, and deploying resources can incur charges.

Use a dedicated test project. Run the [safe local validation path](../LESSON.md#verify-the-terraform-without-a-cloud-account) before this checklist.

Set explicit values from the repository root:

```bash
export PROJECT_ID="your-service-test"
export BILLING_ACCOUNT_ID="000000-000000-000000"
export REGION="europe-west1"
export SERVICE_NAME="email-classifier"
export REPOSITORY_NAME="email-classifier"
export GMAIL_SECRET_NAME="gmail-oauth-token"
export GMAIL_CREDENTIALS_FILE="/absolute/path/to/authorized-user.json"
```

## 1. Create The Project

```bash
gcloud projects create "${PROJECT_ID}" \
  --name="Email Classifier Test" \
  --labels=service=email-classifier,environment=test
```

## 2. Link Billing

```bash
gcloud billing projects link "${PROJECT_ID}" \
  --billing-account="${BILLING_ACCOUNT_ID}"
```

Confirm the selected billing account in the Cloud Console before enabling services.

## 3. Configure Cost Alerts

Create budget alerts for this test project and send them to an actively monitored address before creating billable resources. Standard budgets alert you but do not automatically stop general usage or spending. Follow the current [Google Cloud budget documentation](https://cloud.google.com/billing/docs/how-to/budgets).

Use the [Google Cloud Pricing Calculator](https://cloud.google.com/products/calculator) for the selected region and expected workload. Recheck the estimate when the model, traffic, schedule, storage, or logging changes.

## 4. Enable The Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  cloudscheduler.googleapis.com \
  secretmanager.googleapis.com \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  gmail.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  --project="${PROJECT_ID}"
```

Enable only APIs the workload uses. Recheck this list when the architecture changes.

## 5. Set The Project And Region

```bash
gcloud config set project "${PROJECT_ID}"
gcloud config set run/region "${REGION}"
gcloud config set compute/region "${REGION}"
```

## 6. Initialise Firestore

The classifier uses Firestore to record processed message IDs outside dry-run mode.

```bash
gcloud firestore databases create \
  --location="${REGION}" \
  --type=firestore-native
```

Review the current Firestore database management and deletion guidance before changing an existing project.

## 7. Create A Notification Channel

In the Cloud Console, open **Monitoring > Alerting > Notification channels**. Create an email or other actively monitored channel. Copy its full resource ID into `notification_channel_ids` in `code/terraform/terraform.tfvars` before planning.

## 8. Create The Artifact Registry Repository

```bash
gcloud artifacts repositories create "${REPOSITORY_NAME}" \
  --repository-format=docker \
  --location="${REGION}" \
  --description="Email classifier container images" \
  --project="${PROJECT_ID}"
```

## 9. Store Gmail OAuth Credentials

The application expects OAuth authorized-user JSON with a valid refresh token. A placeholder string will not work. Complete Google's [Gmail Python quickstart](https://developers.google.com/workspace/gmail/api/quickstart/python) with the Gmail modify scope, then use the resulting authorized-user JSON for this test account.

The JSON should contain the fields used by `Credentials.from_authorized_user_info`, including `client_id`, `client_secret`, `refresh_token`, and `token_uri`. Keep the file outside this repository. Do not print it or put its contents in shell history.

For a new secret:

```bash
test -f "${GMAIL_CREDENTIALS_FILE}"
gcloud secrets create "${GMAIL_SECRET_NAME}" \
  --replication-policy="automatic" \
  --data-file="${GMAIL_CREDENTIALS_FILE}" \
  --project="${PROJECT_ID}"
```

If the secret already exists, add a version instead:

```bash
gcloud secrets versions add "${GMAIL_SECRET_NAME}" \
  --data-file="${GMAIL_CREDENTIALS_FILE}" \
  --project="${PROJECT_ID}"
```

## 10. Build And Push The Image

```bash
gcloud builds submit tutorials/deploy-ai-on-gcp/code/email-classifier \
  --project="${PROJECT_ID}" \
  --tag "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${SERVICE_NAME}:latest"
```

## 11. Plan And Apply The Paused Dry Run

```bash
cd tutorials/deploy-ai-on-gcp/code/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit every placeholder. Keep DRY_RUN="true" and scheduler_paused=true.
terraform init
terraform plan
```

Read the complete plan. Check the project, region, image, service accounts, IAM grants, notification channel, `DRY_RUN`, and `scheduler_paused` values. Only then:

```bash
terraform apply
```

The example keeps the scheduler paused. The job will not run on its hourly schedule yet.

## 12. Run One Dry Run Manually

This command executes the job and can incur model and cloud usage charges. With `DRY_RUN=true`, it must not create or apply Gmail labels and must not write processed-message state to Firestore.

```bash
gcloud run jobs execute "${SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --wait
```

Inspect the execution logs. Confirm the selected messages, categories, model, errors, and usage before allowing writes.

## 13. Enable Writes And Scheduling

Only after the dry run is correct, edit `terraform.tfvars`:

```hcl
environment_variables = {
  # Keep the existing values, then change this one.
  DRY_RUN = "false"
}

scheduler_paused = false
```

Review and apply the change:

```bash
terraform plan
terraform apply
```

This enables Gmail label creation, Gmail label changes, Firestore writes, and scheduled executions.

## 14. Clean Up The Test

From `tutorials/deploy-ai-on-gcp/code/terraform`, review and run:

```bash
terraform plan -destroy
terraform destroy
```

Then inspect the project and billing report for resources created outside this Terraform state, including Firestore, the Artifact Registry repository, image data, secret versions, and build data.

## After This Checklist

1. Copy `resources/AGENTS.md` into the target repository as `AGENTS.md` and adapt it.
2. Keep architecture and deployment constraints beside the code.
3. Move repeat deployments into a reviewed CI identity instead of relying on interactive commands.
