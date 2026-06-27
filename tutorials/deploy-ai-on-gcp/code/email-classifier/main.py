"""Email triage classifier. Reads new Gmail messages, classifies via Vertex AI Gemini, applies labels.

Runs as a Cloud Run Job, triggered by Cloud Scheduler.
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone

from google.cloud import firestore, secretmanager
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from vertexai.generative_models import GenerativeModel
import vertexai


PROJECT_ID = os.environ["GCP_PROJECT"]
REGION = os.environ.get("GCP_REGION", "europe-west1")
GMAIL_SECRET_NAME = os.environ["GMAIL_OAUTH_SECRET"]
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-001")
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"
LIMIT = int(os.environ.get("LIMIT", "50"))

CATEGORIES = ["needs-reply", "fyi", "newsletter", "receipt"]


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("email-classifier")


def log_event(event: str, **fields) -> None:
    """Structured JSON log line, parseable by Cloud Logging."""
    payload = {"event": event, "service": "email-classifier", **fields}
    print(json.dumps(payload))


def load_gmail_credentials() -> Credentials:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{GMAIL_SECRET_NAME}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    creds_json = json.loads(response.payload.data.decode("utf-8"))
    return Credentials.from_authorized_user_info(creds_json)


def fetch_unprocessed_messages(service, processed_ids: set[str], limit: int) -> list[dict]:
    """Return up to `limit` recent messages we haven't processed yet."""
    since = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y/%m/%d")
    query = f"in:inbox after:{since}"
    response = service.users().messages().list(userId="me", q=query, maxResults=limit).execute()
    candidates = response.get("messages", [])
    return [m for m in candidates if m["id"] not in processed_ids]


def get_message_summary(service, message_id: str) -> dict:
    """Fetch enough of a message to classify it."""
    msg = service.users().messages().get(
        userId="me",
        id=message_id,
        format="metadata",
        metadataHeaders=["From", "Subject", "List-Unsubscribe"],
    ).execute()
    headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
    return {
        "id": message_id,
        "from": headers.get("From", ""),
        "subject": headers.get("Subject", ""),
        "snippet": msg.get("snippet", ""),
        "is_newsletter": "List-Unsubscribe" in headers,
    }


def classify(model: GenerativeModel, summary: dict) -> str:
    """Ask Gemini which category the message belongs to."""
    prompt = f"""You classify emails into one of these categories: {", ".join(CATEGORIES)}.

Email:
From: {summary["from"]}
Subject: {summary["subject"]}
Snippet: {summary["snippet"]}
Has unsubscribe header: {summary["is_newsletter"]}

Respond with one category name only. No explanation."""

    response = model.generate_content(
        prompt,
        generation_config={"max_output_tokens": 10, "temperature": 0.0},
    )
    label = response.text.strip().lower()
    if label not in CATEGORIES:
        log_event("classification_invalid", message_id=summary["id"], raw=label)
        return "fyi"
    return label


def get_or_create_label(service, name: str) -> str:
    """Return Gmail label ID, creating it if missing."""
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    for label in labels:
        if label["name"] == name:
            return label["id"]
    created = service.users().labels().create(userId="me", body={"name": name}).execute()
    return created["id"]


def apply_label(service, message_id: str, label_id: str) -> None:
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": [label_id]},
    ).execute()


def main() -> None:
    log_event("run_started", project=PROJECT_ID, dry_run=DRY_RUN, limit=LIMIT)

    vertexai.init(project=PROJECT_ID, location=REGION)
    model = GenerativeModel(MODEL_NAME)

    creds = load_gmail_credentials()
    gmail = build("gmail", "v1", credentials=creds, cache_discovery=False)

    db = firestore.Client(project=PROJECT_ID)
    processed_ref = db.collection("processed_messages")
    processed_ids = {doc.id for doc in processed_ref.limit(1000).stream()}

    messages = fetch_unprocessed_messages(gmail, processed_ids, LIMIT)
    log_event("messages_fetched", count=len(messages))

    label_ids = {cat: get_or_create_label(gmail, f"triage/{cat}") for cat in CATEGORIES}

    for msg in messages:
        try:
            summary = get_message_summary(gmail, msg["id"])
            category = classify(model, summary)

            if not DRY_RUN:
                apply_label(gmail, msg["id"], label_ids[category])
                processed_ref.document(msg["id"]).set({
                    "category": category,
                    "classified_at": firestore.SERVER_TIMESTAMP,
                })

            log_event("message_classified", message_id=msg["id"], category=category, dry_run=DRY_RUN)
        except Exception as e:
            log_event("message_failed", message_id=msg["id"], error=str(e), severity="ERROR")

    log_event("run_completed", processed=len(messages))


if __name__ == "__main__":
    main()
