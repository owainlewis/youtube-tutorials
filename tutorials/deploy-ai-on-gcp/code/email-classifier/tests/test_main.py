"""Credential-free checks for the email classifier workflow."""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest import mock


CODE_DIR = Path(__file__).resolve().parents[1]


def install_dependency_stubs() -> None:
    """Provide import-only stubs so the workflow can be tested without cloud SDKs."""
    google = types.ModuleType("google")
    genai = types.ModuleType("google.genai")
    genai_types = types.ModuleType("google.genai.types")
    cloud = types.ModuleType("google.cloud")
    firestore = types.ModuleType("google.cloud.firestore")
    secretmanager = types.ModuleType("google.cloud.secretmanager")
    oauth2 = types.ModuleType("google.oauth2")
    credentials = types.ModuleType("google.oauth2.credentials")
    googleapiclient = types.ModuleType("googleapiclient")
    discovery = types.ModuleType("googleapiclient.discovery")

    class GenerateContentConfig:
        def __init__(self, **values):
            self.values = values

    class HttpOptions:
        def __init__(self, **values):
            self.values = values

    genai.Client = object
    genai_types.GenerateContentConfig = GenerateContentConfig
    genai_types.HttpOptions = HttpOptions
    firestore.SERVER_TIMESTAMP = object()
    firestore.Client = object
    secretmanager.SecretManagerServiceClient = object
    credentials.Credentials = object
    discovery.build = object

    google.genai = genai
    google.cloud = cloud
    google.oauth2 = oauth2
    genai.types = genai_types
    cloud.firestore = firestore
    cloud.secretmanager = secretmanager
    oauth2.credentials = credentials
    googleapiclient.discovery = discovery

    sys.modules.update(
        {
            "google": google,
            "google.genai": genai,
            "google.genai.types": genai_types,
            "google.cloud": cloud,
            "google.cloud.firestore": firestore,
            "google.cloud.secretmanager": secretmanager,
            "google.oauth2": oauth2,
            "google.oauth2.credentials": credentials,
            "googleapiclient": googleapiclient,
            "googleapiclient.discovery": discovery,
        }
    )


install_dependency_stubs()
spec = importlib.util.spec_from_file_location("email_classifier", CODE_DIR / "main.py")
email_classifier = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(email_classifier)


class FakeProcessedRef:
    def __init__(self) -> None:
        self.document_calls: list[str] = []

    def document(self, message_id: str):
        self.document_calls.append(message_id)
        return mock.Mock()


class FakeModels:
    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.calls: list[dict] = []

    def generate_content(self, **arguments):
        self.calls.append(arguments)
        return types.SimpleNamespace(text=self.response_text)


class EmailClassifierTests(unittest.TestCase):
    def test_dry_run_performs_no_gmail_or_firestore_writes(self) -> None:
        processed_ref = FakeProcessedRef()

        with (
            mock.patch.object(email_classifier, "get_or_create_label") as create_label,
            mock.patch.object(email_classifier, "apply_label") as apply_label,
            mock.patch.object(
                email_classifier,
                "get_message_summary",
                return_value={"id": "message-1"},
            ),
            mock.patch.object(email_classifier, "classify", return_value="fyi"),
            mock.patch.object(email_classifier, "log_event"),
        ):
            email_classifier.process_messages(
                gmail=object(),
                processed_ref=processed_ref,
                model_client=object(),
                model_name="current-model",
                messages=[{"id": "message-1"}],
                dry_run=True,
            )

        create_label.assert_not_called()
        apply_label.assert_not_called()
        self.assertEqual(processed_ref.document_calls, [])

    def test_classify_uses_google_genai_request_shape(self) -> None:
        models = FakeModels("NEEDS-REPLY")
        client = types.SimpleNamespace(models=models)
        summary = {
            "id": "message-1",
            "from": "person@example.com",
            "subject": "Question",
            "snippet": "Can you help?",
            "is_newsletter": False,
        }

        category = email_classifier.classify(client, "current-model", summary)

        self.assertEqual(category, "needs-reply")
        self.assertEqual(models.calls[0]["model"], "current-model")
        self.assertIn("person@example.com", models.calls[0]["contents"])
        self.assertEqual(models.calls[0]["config"].values["temperature"], 0.0)

    def test_dependency_manifest_uses_google_genai(self) -> None:
        requirements = (CODE_DIR / "requirements.txt").read_text()
        source = (CODE_DIR / "main.py").read_text()

        self.assertIn("google-genai", requirements)
        self.assertIn("google-genai>=1.40.0", requirements)
        self.assertNotIn("google-cloud-aiplatform", requirements)
        self.assertNotIn("vertexai.generative_models", source)


if __name__ == "__main__":
    unittest.main()
