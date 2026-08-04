"""Email triage classifier. Reads Gmail, classifies with Vertex AI, and applies labels.

Runs as a Cloud Run Job, triggered by Cloud Scheduler.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone

from google import genai
from google.cloud import firestore, secretmanager
from google.genai import types
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

CATEGORIES = ["needs-reply", "fyi", "newsletter", "receipt"]


def log_event(event: str, **fields) -> None:
    """Structured JSON log line, parseable by Cloud Logging."""
    payload = {"event": event, "service": "email-classifier", **fields}
    print(json.dumps(payload))


def load_gmail_credentials(project_id: str, secret_name: str) -> Credentials:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
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


def classify(
    model_client: genai.Client,
    model_name: str,
    summary: dict,
) -> str:
    """Ask Gemini which category the message belongs to."""
    prompt = f"""You classify emails into one of these categories: {", ".join(CATEGORIES)}.

Email:
From: {summary["from"]}
Subject: {summary["subject"]}
Snippet: {summary["snippet"]}
Has unsubscribe header: {summary["is_newsletter"]}

Respond with one category name only. No explanation."""

    response = model_client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=10,
            temperature=0.0,
        ),
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


def process_messages(
    gmail,
    processed_ref,
    model_client: genai.Client,
    model_name: str,
    messages: list[dict],
    dry_run: bool,
) -> None:
    """Classify messages and mutate Gmail and Firestore only outside dry-run mode."""
    label_ids = {}
    if not dry_run:
        label_ids = {
            category: get_or_create_label(gmail, f"triage/{category}")
            for category in CATEGORIES
        }

    for msg in messages:
        try:
            summary = get_message_summary(gmail, msg["id"])
            category = classify(model_client, model_name, summary)

            if not dry_run:
                apply_label(gmail, msg["id"], label_ids[category])
                processed_ref.document(msg["id"]).set(
                    {
                        "category": category,
                        "classified_at": firestore.SERVER_TIMESTAMP,
                    }
                )

            log_event(
                "message_classified",
                message_id=msg["id"],
                category=category,
                dry_run=dry_run,
            )
        except Exception as e:
            log_event("message_failed", message_id=msg["id"], error=str(e), severity="ERROR")


def main() -> None:
    project_id = os.environ["GCP_PROJECT"]
    region = os.environ.get("GCP_REGION", "europe-west1")
    gmail_secret_name = os.environ["GMAIL_OAUTH_SECRET"]
    model_name = os.environ["GEMINI_MODEL"]
    dry_run = os.environ.get("DRY_RUN", "true").lower() == "true"
    limit = int(os.environ.get("LIMIT", "50"))

    log_event("run_started", project=project_id, dry_run=dry_run, limit=limit)

    creds = load_gmail_credentials(project_id, gmail_secret_name)
    gmail = build("gmail", "v1", credentials=creds, cache_discovery=False)

    db = firestore.Client(project=project_id)
    processed_ref = db.collection("processed_messages")
    processed_ids = {doc.id for doc in processed_ref.limit(1000).stream()}

    messages = fetch_unprocessed_messages(gmail, processed_ids, limit)
    log_event("messages_fetched", count=len(messages))

    with genai.Client(
        vertexai=True,
        project=project_id,
        location=region,
        http_options=types.HttpOptions(api_version="v1"),
    ) as model_client:
        process_messages(
            gmail,
            processed_ref,
            model_client,
            model_name,
            messages,
            dry_run,
        )

    log_event("run_completed", processed=len(messages))


if __name__ == "__main__":
    main()
