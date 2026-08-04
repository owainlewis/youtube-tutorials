from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "check_python_dependencies.py"
SPEC = importlib.util.spec_from_file_location("check_python_dependencies", SCRIPT_PATH)
assert SPEC and SPEC.loader
check_python_dependencies = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_python_dependencies)


class PythonDependenciesTest(unittest.TestCase):
    def test_compile_command_includes_extras_and_dependency_groups(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                """[project]
name = "example"
version = "0.1.0"
dependencies = ["example>=1.0"]

[project.optional-dependencies]
feature = ["feature>=1.0"]

[dependency-groups]
dev = ["pytest>=9.0.2"]
"""
            )
            output = root / "requirements.txt"

            command = check_python_dependencies.compile_command(pyproject, output)

        self.assertIn("--all-extras", command)
        self.assertIn("--python-version", command)
        self.assertIn(f"{pyproject}:dev", command)
        self.assertEqual(command[command.index("--output-file") + 1], str(output))


if __name__ == "__main__":
    unittest.main()
