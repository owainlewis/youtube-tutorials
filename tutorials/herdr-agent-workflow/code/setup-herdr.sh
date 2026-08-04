#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ./code/setup-herdr.sh [agent...]

Examples:
  ./code/setup-herdr.sh claude codex
  ./code/setup-herdr.sh claude codex pi opencode

What it does:
  - Checks whether herdr is installed.
  - Prints install commands if herdr is missing.
  - Installs Herdr integrations for the agents you pass.
  - Installs the Herdr skill globally with npx skills if npx is available.
  - Prints next steps.

It does not start Herdr or edit your shell config.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

agents=("$@")
if [[ ${#agents[@]} -eq 0 ]]; then
  agents=(claude codex)
fi

if ! command -v herdr >/dev/null 2>&1; then
  cat <<'EOF'
Herdr is not installed.

Linux or macOS:
  curl -fsSL https://herdr.dev/install.sh | sh

Homebrew:
  brew install herdr

mise:
  mise use -g herdr

Then restart your terminal if needed and run this script again.
EOF
  exit 1
fi

echo "Herdr version:"
herdr --version
echo

echo "Installing Herdr integrations..."
failed_agents=()
for agent in "${agents[@]}"; do
  echo "  herdr integration install ${agent}"
  if ! herdr integration install "${agent}"; then
    failed_agents+=("${agent}")
  fi
done

echo
echo "Integration status:"
herdr integration status || true

if [[ ${#failed_agents[@]} -gt 0 ]]; then
  echo
  echo "Some integrations did not install:"
  for agent in "${failed_agents[@]}"; do
    echo "  - ${agent}"
  done
  cat <<'EOF'

This usually means the agent is not installed yet, or its config directory does
not exist for the current user. Install the agent, run it once, then rerun this
script for that agent.
EOF
fi

echo
if command -v npx >/dev/null 2>&1; then
  echo "Installing Herdr skill globally for supported agents..."
  if ! npx skills add herdrdev/herdr --skill herdr -g; then
    cat <<'EOF'
The Herdr skill install failed.

Manual skill source:
  https://raw.githubusercontent.com/herdrdev/herdr/master/skills/herdr/SKILL.md
EOF
  fi
else
  cat <<'EOF'
npx was not found, so the Herdr skill was not installed.

Manual skill source:
  https://raw.githubusercontent.com/herdrdev/herdr/master/skills/herdr/SKILL.md
EOF
fi

cat <<'EOF'

Next steps:

1. Start Herdr from a project:
     cd /path/to/project
     herdr

2. Run an agent inside Herdr:
     claude
     codex

3. Detach and reattach:
     ctrl+b, then q
     herdr

4. Ask an agent to read the Herdr guide before helping you set it up:
     https://herdr.dev/agent-guide.md
EOF
