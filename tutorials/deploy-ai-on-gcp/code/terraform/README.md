# Reference Terraform Module: Scheduled AI Cloud Run Job

This module is a starting point for the checked-in email classifier sample. Review and adapt it before using it in a Google Cloud project.

## What It Describes

- Cloud Run Job
- Cloud Scheduler trigger
- Separate job and scheduler service accounts
- Required APIs
- Selected IAM bindings for Vertex AI, Firestore, Secret Manager, and job invocation
- Log-based failure metric and alerting policy
- Optional Cloud Monitoring dashboard

## Safe Local Validation

From the repository root:

```bash
terraform -chdir=tutorials/deploy-ai-on-gcp/code/terraform fmt -check -diff
bash tutorials/deploy-ai-on-gcp/code/terraform/validate.sh
```

The script copies the module to a temporary directory, initializes the Google provider there, validates the configuration, and removes the generated files. It does not need Google Cloud credentials and does not create resources.

## Before A Cloud Plan

Planning and applying this module requires credentials and an active billing account. Applying it can create billable resources.

- Use a dedicated test project.
- Build and push the container image first.
- Replace every placeholder in `terraform.tfvars`.
- Create any referenced Secret Manager secrets and notification channels.
- Review the project, region, image, schedule, IAM grants, and cost drivers.
- Keep `DRY_RUN="true"` and `scheduler_paused=true` for the first deployment.
- Use the [Google Cloud Pricing Calculator](https://cloud.google.com/products/calculator) for your region and workload.
- Configure [budgets and alerts](https://cloud.google.com/billing/docs/how-to/budgets). Standard budget alerts do not stop general spending.

## Opt-In Deployment

From this directory:

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars for your test project.
terraform init
terraform plan
```

Read the complete plan before deciding whether to create anything. Only then:

```bash
terraform apply
```

The example creates the scheduler in a paused state. Follow the [deployment checklist](../../resources/checklist.md) to execute one dry run manually, inspect its logs, and make a separate reviewed change before enabling writes or the schedule.

Remove the managed resources after a disposable test:

```bash
terraform destroy
```

Check the project afterwards for resources created outside this Terraform state.

## Defaults To Review

- Service accounts use `<service>-sa` and `<service>-scheduler-sa` names.
- Resources use `service` and `environment` labels.
- The default region is `europe-west1`.
- The scheduler is paused by default.
- The example environment sets `DRY_RUN` to `true`.
- The job timeout, retries, CPU, and memory come from variables.
- The alert policy fires when the log-based failure metric crosses its configured threshold.

## What It Does Not Do

- create a Firestore database
- create Secret Manager secret values
- build or push the container image
- create notification channels
- grant `roles/owner` or `roles/editor`

See the [main lesson](../../LESSON.md) for the architecture, safety model, and current primary documentation.

Licensed under the [MIT License](../../../../LICENSE).
