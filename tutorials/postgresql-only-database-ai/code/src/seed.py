"""Seed the documents table with sample data and real embeddings."""

import json
import os

import psycopg
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"
)
EMBEDDING_MODEL = "text-embedding-3-small"

client = OpenAI()

DOCUMENTS = [
    # --- Shipping & Delivery ---
    {
        "content": (
            "Nimbus Cloud standard shipping takes 5-7 business days within the "
            "continental US. Express shipping (2-3 business days) is available for "
            "$12.99. Overnight shipping is $24.99 and orders must be placed before "
            "2 PM ET for same-day dispatch. Alaska, Hawaii, and US territories "
            "require an additional 3-5 business days for all shipping methods."
        ),
        "metadata": {"source": "shipping-policy", "topic": "delivery-times"},
    },
    {
        "content": (
            "All Nimbus Cloud orders ship from our warehouse in Columbus, Ohio. "
            "Tracking numbers are emailed within 24 hours of shipment. If your "
            "tracking number shows no movement after 48 hours, contact support. "
            "We ship via USPS, UPS, and FedEx depending on package size and "
            "destination. Customers cannot select a specific carrier."
        ),
        "metadata": {"source": "shipping-policy", "topic": "tracking"},
    },
    {
        "content": (
            "International shipping is available to Canada, UK, EU, Australia, "
            "and Japan. Delivery takes 10-21 business days. International orders "
            "over $150 USD ship free. Customers are responsible for all customs "
            "duties and import taxes. Nimbus Cloud is not responsible for delays "
            "caused by customs processing."
        ),
        "metadata": {"source": "shipping-policy", "topic": "international"},
    },
    # --- Returns & Refunds ---
    {
        "content": (
            "Nimbus Cloud offers a 30-day return policy from the date of delivery. "
            "Items must be unused, in original packaging, and include all "
            "accessories. To start a return, log into your account and go to "
            "Order History > Request Return. A prepaid return label will be "
            "emailed within 1 business day. Return shipping is free for defective "
            "items. Non-defective returns are subject to a $5.99 return shipping fee."
        ),
        "metadata": {"source": "returns-policy", "topic": "return-process"},
    },
    {
        "content": (
            "Refunds are processed within 5-7 business days after we receive the "
            "returned item. Refunds are issued to the original payment method. "
            "Credit card refunds may take an additional 3-5 business days to "
            "appear on your statement. Store credit refunds are available "
            "instantly and include a bonus 10% credit on top of the refund amount."
        ),
        "metadata": {"source": "returns-policy", "topic": "refund-timeline"},
    },
    {
        "content": (
            "The following items are final sale and cannot be returned: gift "
            "cards, clearance items marked 'Final Sale', personalized or "
            "custom-engraved products, and items from the Nimbus Essentials "
            "subscription box. Opened software and digital downloads are "
            "non-refundable. If you received a defective final sale item, "
            "contact support for a replacement."
        ),
        "metadata": {"source": "returns-policy", "topic": "non-returnable"},
    },
    # --- Subscription & Billing ---
    {
        "content": (
            "Nimbus Cloud Pro costs $19.99/month or $199/year (save 17%). "
            "The plan includes unlimited cloud storage, priority support with "
            "4-hour response time, advanced analytics dashboard, API access "
            "with 10,000 requests/day, and early access to new features. "
            "The free tier includes 5 GB storage, community support, and "
            "basic analytics with a 7-day retention period."
        ),
        "metadata": {"source": "billing", "topic": "pricing"},
    },
    {
        "content": (
            "Nimbus Cloud Team costs $14.99/user/month (minimum 3 users) and "
            "includes everything in Pro plus shared workspaces, team admin "
            "console, SSO via SAML, audit logs, and 99.9% uptime SLA. "
            "Enterprise pricing starts at $49.99/user/month for 50+ users "
            "and adds dedicated account manager, custom integrations, on-premise "
            "deployment option, and 99.99% uptime SLA."
        ),
        "metadata": {"source": "billing", "topic": "team-pricing"},
    },
    {
        "content": (
            "You can cancel your Nimbus Cloud subscription at any time from "
            "Settings > Billing > Cancel Plan. Your access continues until the "
            "end of the current billing period. Annual plan customers who cancel "
            "within the first 30 days receive a full refund. After 30 days, "
            "annual plans are prorated. Data is retained for 90 days after "
            "cancellation, then permanently deleted."
        ),
        "metadata": {"source": "billing", "topic": "cancellation"},
    },
    {
        "content": (
            "Nimbus Cloud accepts Visa, Mastercard, American Express, and "
            "Discover. PayPal and Apple Pay are available in the US, UK, and "
            "Canada. We do not accept wire transfers for individual accounts. "
            "Enterprise accounts can pay by invoice with NET-30 terms. "
            "All prices are in USD. VAT is added for EU customers at checkout."
        ),
        "metadata": {"source": "billing", "topic": "payment-methods"},
    },
    # --- Account & Security ---
    {
        "content": (
            "To reset your Nimbus Cloud password, click 'Forgot Password' on "
            "the login page. A reset link valid for 1 hour will be sent to your "
            "registered email. If you don't receive it within 5 minutes, check "
            "your spam folder or contact support. For security, password resets "
            "invalidate all existing sessions across devices. Passwords must be "
            "at least 12 characters with one uppercase letter, one number, and "
            "one special character."
        ),
        "metadata": {"source": "account-help", "topic": "password-reset"},
    },
    {
        "content": (
            "Two-factor authentication (2FA) is available for all Nimbus Cloud "
            "accounts and required for Team and Enterprise plans. We support "
            "authenticator apps (Google Authenticator, Authy) and hardware "
            "security keys (YubiKey). SMS-based 2FA is not supported due to "
            "SIM-swap risks. Backup codes are generated when 2FA is enabled. "
            "Store them securely — support cannot bypass 2FA without backup codes."
        ),
        "metadata": {"source": "account-help", "topic": "two-factor-auth"},
    },
    {
        "content": (
            "To delete your Nimbus Cloud account, go to Settings > Account > "
            "Delete Account. You must first cancel any active subscriptions and "
            "download your data export. Account deletion is permanent and takes "
            "effect within 48 hours. All files, projects, and API keys are "
            "permanently removed. We retain billing records for 7 years per "
            "legal requirements but all personal data is anonymized."
        ),
        "metadata": {"source": "account-help", "topic": "account-deletion"},
    },
    # --- Product Features ---
    {
        "content": (
            "Nimbus Cloud Sync automatically backs up files from your Desktop, "
            "Documents, and Downloads folders. Sync runs every 5 minutes when "
            "changes are detected. File versioning keeps the last 30 versions "
            "of each file (Pro plan) or 10 versions (Free plan). You can restore "
            "previous versions from the web dashboard under Files > Version History. "
            "Maximum individual file size is 10 GB on Pro and 500 MB on Free."
        ),
        "metadata": {"source": "product-docs", "topic": "file-sync"},
    },
    {
        "content": (
            "Nimbus Cloud Spaces are shared collaboration folders. Any team "
            "member can create a Space and invite others with Viewer, Editor, "
            "or Admin permissions. Viewers can download files but cannot modify "
            "them. Editors can upload, rename, and delete files. Space Admins "
            "can manage members and permissions. Files in Spaces do not count "
            "toward individual storage quotas on Team and Enterprise plans."
        ),
        "metadata": {"source": "product-docs", "topic": "shared-spaces"},
    },
    {
        "content": (
            "The Nimbus Cloud API uses REST with JSON responses. Authentication "
            "is via Bearer token in the Authorization header. Rate limits are "
            "100 requests/minute for Free, 1,000/minute for Pro, and 10,000/minute "
            "for Enterprise. All API endpoints are documented at "
            "developers.nimbuscloud.com. SDKs are available for Python, "
            "JavaScript, Go, and Ruby."
        ),
        "metadata": {"source": "product-docs", "topic": "api"},
    },
    # --- Troubleshooting ---
    {
        "content": (
            "If Nimbus Cloud Sync is stuck on 'Preparing to sync', try these "
            "steps: 1) Right-click the Nimbus icon in your system tray and "
            "select 'Restart Sync'. 2) Check your internet connection. "
            "3) Ensure you have available storage space in your account. "
            "4) Clear the sync cache at Settings > Advanced > Clear Cache. "
            "5) Uninstall and reinstall the desktop app. If the issue persists "
            "after all steps, contact support with your sync log file from "
            "Help > Export Logs."
        ),
        "metadata": {"source": "troubleshooting", "topic": "sync-issues"},
    },
    {
        "content": (
            "Error code NC-4012 means your API key has been revoked or expired. "
            "Generate a new API key from Settings > Developer > API Keys. "
            "Error code NC-4029 indicates you've exceeded your rate limit — "
            "wait 60 seconds and retry. Error code NC-5003 is a temporary "
            "server issue on our end. Check status.nimbuscloud.com for "
            "ongoing incidents. If NC-5003 persists beyond 30 minutes, "
            "contact support."
        ),
        "metadata": {"source": "troubleshooting", "topic": "error-codes"},
    },
    {
        "content": (
            "If you're unable to upload files, verify the following: the file "
            "is under the size limit (500 MB Free, 10 GB Pro), the filename "
            "does not contain special characters (# % & { } \\ < > * ? / $ ! ' \" "
            ": @ + ` | =), and you have available storage space. ZIP files "
            "larger than 2 GB must be uploaded via the desktop app, not the "
            "web browser. Uploads over mobile data are limited to 100 MB per "
            "file to prevent excessive data usage."
        ),
        "metadata": {"source": "troubleshooting", "topic": "upload-issues"},
    },
    # --- Contact & Support ---
    {
        "content": (
            "Nimbus Cloud support is available via email at help@nimbuscloud.com "
            "and live chat on our website. Support hours are Monday-Friday "
            "8 AM - 8 PM ET for Free tier, and 24/7 for Pro, Team, and Enterprise "
            "customers. Average response time is 24 hours for email and under "
            "5 minutes for live chat during business hours. Enterprise customers "
            "have a dedicated Slack channel with their account team."
        ),
        "metadata": {"source": "support", "topic": "contact-info"},
    },
]


def get_embedding(text: str) -> list[float]:
    """Generate an embedding vector for the given text."""
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding


def seed():
    """Embed all documents and insert them into PostgreSQL."""
    conn = psycopg.connect(DATABASE_URL)

    # Generate embeddings for all documents in one batch
    texts = [doc["content"] for doc in DOCUMENTS]
    print(f"Generating embeddings for {len(texts)} documents...")
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    embeddings = [item.embedding for item in response.data]

    with conn.cursor() as cur:
        # Clear existing data
        cur.execute("DELETE FROM documents")

        for doc, embedding in zip(DOCUMENTS, embeddings):
            cur.execute(
                """
                INSERT INTO documents (content, metadata, embedding)
                VALUES (%s, %s::jsonb, %s::vector)
                """,
                (doc["content"], json.dumps(doc["metadata"]), str(embedding)),
            )

        conn.commit()

    conn.close()
    print(f"Seeded {len(DOCUMENTS)} documents with embeddings.")


if __name__ == "__main__":
    seed()
