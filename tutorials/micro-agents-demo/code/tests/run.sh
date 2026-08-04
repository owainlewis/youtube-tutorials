#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
uv run --isolated python -m unittest discover -s tests -v
