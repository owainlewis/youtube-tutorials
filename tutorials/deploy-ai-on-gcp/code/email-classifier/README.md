# Email triage classifier

This is the supporting material for the video: Email triage classifier.

Cloud Run Job that reads new Gmail messages, classifies each into `needs-reply / fyi / newsletter / receipt` using Vertex AI Gemini, and applies the matching Gmail label.

## What it does

1. Reads unread inbox messages from the last 24 hours
2. Filters out IDs Firestore has already seen
3. Sends headers + snippet to Gemini Flash for classification
4. Applies a `triage/<category>` Gmail label
5. Records the message ID in Firestore so it isn't re-classified next run

Runtime per invocation: ~30 seconds for 50 messages. Cost: cents per month.

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env with your project ID and secret name

set -a && source .env && set +a
python main.py
```

`DRY_RUN=true` skips applying labels and writing to Firestore. Use it for the first few runs while you verify auth and classification quality.

## Production deploy

See the parent `README.md` and the Terraform module in `../terraform/`.

Quick version:

```bash
gcloud builds submit \
  --tag europe-west1-docker.pkg.dev/$PROJECT_ID/email-classifier/email-classifier:latest

cd ../terraform
terraform apply
```

## Environment variables

| Variable | Purpose |
|---|---|
| `GCP_PROJECT` | GCP project ID |
| `GCP_REGION` | Region for Vertex AI calls (default `europe-west1`) |
| `GMAIL_OAUTH_SECRET` | Name of the Secret Manager secret containing the Gmail OAuth token |
| `GEMINI_MODEL` | Model ID (default `gemini-2.0-flash-001`) |
| `DRY_RUN` | If `true`, classify but don't apply labels or persist state |
| `LIMIT` | Max messages per run (default 50) |

## Customising

The classification rule is a single prompt in `main.py`. Edit `CATEGORIES` and the prompt body to suit your inbox. Common variants:

- Add `client-email` and route those to a Linear inbox via webhook
- Add `urgent` for messages mentioning specific keywords
- Replace categories with sender-based routing (work / personal / promotional)

The simpler the rule, the better Gemini Flash performs. Don't over-engineer.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
