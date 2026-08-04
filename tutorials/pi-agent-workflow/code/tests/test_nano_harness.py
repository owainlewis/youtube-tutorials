import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


class FakeAnthropic:
    pass


sys.modules.setdefault("anthropic", types.SimpleNamespace(Anthropic=FakeAnthropic))
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda: None))

MODULE_PATH = Path(__file__).parents[1] / "nano-harness.py"
SPEC = importlib.util.spec_from_file_location("nano_harness", MODULE_PATH)
nano_harness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(nano_harness)


class NanoHarnessTests(unittest.TestCase):
    def setUp(self):
        nano_harness.LISTENERS = {}

    def test_read_file_returns_numbered_slice(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notes.txt"
            path.write_text("alpha\nbeta\ngamma\n")

            result = nano_harness.read_file(str(path), offset=1, limit=2)

        self.assertEqual(result, "     2\tbeta\n     3\tgamma")

    def test_edit_file_rejects_a_non_unique_match(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notes.txt"
            path.write_text("same\nsame\n")

            result = nano_harness.edit_file(str(path), "same", "changed")

            self.assertIn("matches 2 times", result)
            self.assertEqual(path.read_text(), "same\nsame\n")

    def test_listener_can_veto_an_event(self):
        @nano_harness.on("pre_tool")
        def reject(**_payload):
            return False

        self.assertFalse(nano_harness.emit("pre_tool", tool="bash", args={}))

    def test_agent_emits_turn_end_without_running_a_tool(self):
        events = []

        @nano_harness.on("turn_end")
        def record_turn_end():
            events.append("turn_end")

        response = types.SimpleNamespace(content=[], stop_reason="end_turn")
        messages = [{"role": "user", "content": "Explain this folder"}]

        with patch.object(nano_harness, "call_model", return_value=response):
            nano_harness.agent(messages)

        self.assertEqual(events, ["turn_end"])
        self.assertEqual(messages[-1]["role"], "assistant")


if __name__ == "__main__":
    unittest.main()
