#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
uv venv --allow-existing
uv pip install --python .venv/bin/python -r pyproject.toml
.venv/bin/python -m unittest discover -s tests -v
