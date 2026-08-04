from __future__ import annotations

import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "run_offline_tests.py"
SPEC = importlib.util.spec_from_file_location("run_offline_tests", SCRIPT_PATH)
assert SPEC and SPEC.loader
run_offline_tests = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(run_offline_tests)


class OfflineTestRunnerTest(unittest.TestCase):
    def test_default_matrix_includes_offline_and_static_entries(self) -> None:
        entries = {
            "static": {"kind": "static"},
            "network": {"kind": "network"},
            "offline": {"kind": "offline"},
        }

        selected = run_offline_tests.selected_entries(entries, "offline")

        self.assertEqual([slug for slug, _ in selected], ["offline", "static"])

    def test_network_matrix_stays_separate(self) -> None:
        entries = {
            "offline": {"kind": "offline"},
            "network": {"kind": "network"},
        }

        selected = run_offline_tests.selected_entries(entries, "network")

        self.assertEqual([slug for slug, _ in selected], ["network"])

    def test_empty_optional_matrix_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "verification.json"
            manifest.write_text(
                json.dumps({"tutorials": {"offline": {"kind": "offline"}}})
            )
            output = io.StringIO()

            with patch.object(run_offline_tests, "MANIFEST_PATH", manifest):
                with redirect_stdout(output):
                    result = run_offline_tests.run("network")

        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue(), "No network tutorial checks are configured.\n")


if __name__ == "__main__":
    unittest.main()
