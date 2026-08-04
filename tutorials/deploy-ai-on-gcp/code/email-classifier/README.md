# Email triage classifier

This is the supporting material for the video: Email triage classifier.

Cloud Run Job that reads new Gmail messages, classifies each into `needs-reply / fyi / newsletter / receipt` using Vertex AI Gemini, and applies the matching Gmail label.

## What it does

1. Reads unread inbox messages from the last 24 hours
2. Filters out IDs Firestore has already seen
3. Sends headers and the snippet to the configured Vertex AI Gemini model for classification
4. Applies a `triage/<category>` Gmail label
5. Records the message ID in Firestore so it isn't re-classified next run

Runtime and cost depend on message volume, model choice, region, retries, log volume, and current Google Cloud pricing. Measure a dry run, then estimate the real workload with the [Google Cloud Pricing Calculator](https://cloud.google.com/products/calculator).

## Local run

This is a credentialed dry run. It contacts Secret Manager, Firestore, Gmail, and Vertex AI, so usage charges can apply. Use a test project and test inbox. Configure [Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc#local-dev) with access to that project first.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env with your project ID and secret name

set -a && source .env && set +a
python main.py
```

`DRY_RUN=true` skips creating or applying labels and skips writing to Firestore. It is the default. Use it while you verify auth and classification quality. Change it to `false` only after reviewing dry-run logs.

## Credential-Free Checks

From this directory, run the unit checks without installing cloud SDKs:

```bash
python3 -m unittest discover -s tests -v
```

To prove a fresh dependency set still provides the documented Google Gen AI SDK imports, use `uv` without creating a project lockfile:

```bash
uv run --no-project --with-requirements requirements.txt \
  python -c 'import main; from google import genai; assert hasattr(genai.Client, "__enter__")'
```

Neither command needs Google Cloud credentials or contacts Gmail, Vertex AI, or Firestore.

## Production Deploy

See the [main lesson](../../LESSON.md) and the [Terraform module](../terraform/) before deploying.

The following commands require Google Cloud credentials and a billing account. They build and push an image, then the Terraform apply can create billable resources. Set the variables explicitly and review the Terraform plan first:

```bash
export PROJECT_ID="your-test-project-id"
export REGION="europe-west1"

gcloud builds submit \
  --project="${PROJECT_ID}" \
  --tag "${REGION}-docker.pkg.dev/${PROJECT_ID}/email-classifier/email-classifier:latest"

cd ../terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars to match the test project and image above.
terraform init
terraform plan
terraform apply
```

`terraform apply` is an opt-in deployment step. It is not part of the safe local verification path. The example keeps `DRY_RUN=true` and the scheduler paused. Follow the [deployment checklist](../../resources/checklist.md) to run the job once, inspect the logs, and enable writes and scheduling as a separate change.

## Environment variables

| Variable | Purpose |
|---|---|
| `GCP_PROJECT` | GCP project ID |
| `GCP_REGION` | Region for Vertex AI calls (default `europe-west1`) |
| `GMAIL_OAUTH_SECRET` | Name of the Secret Manager secret containing the Gmail OAuth token |
| `GEMINI_MODEL` | Required current model ID from Vertex AI Model Garden |
| `DRY_RUN` | If `true` or omitted, classify without creating labels or persisting state |
| `LIMIT` | Max messages per run (default 50) |

## Customising

The classification rule is a single prompt in `main.py`. Edit `CATEGORIES` and the prompt body to suit your inbox. Common variants:

- Add `client-email` and route those to a Linear inbox via webhook
- Add `urgent` for messages mentioning specific keywords
- Replace categories with sender-based routing (work / personal / promotional)

Start with a small category set. It is easier to evaluate before you add more routing rules.

Model IDs and retirement dates change. Check the current [Vertex AI model lifecycle](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions) before setting `GEMINI_MODEL`.

This sample uses the [Google Gen AI SDK](https://cloud.google.com/vertex-ai/generative-ai/docs/sdks/overview), not the removed `vertexai.generative_models` module.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
