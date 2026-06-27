#!/bin/bash
# Stop hook script: runs linting + security checks before Claude can finish.
# Exit 0 = pass, Exit 2 = fail (Claude is blocked and must fix issues).
# Adapt this to your stack: swap ruff for eslint, brakeman for semgrep, etc.

cd "$(git rev-parse --show-toplevel)" || exit 0

errors=""

# ── Linting (only changed files, keeps it fast) ──
changed_rb=$(git diff --name-only --diff-filter=ACMR HEAD -- '*.rb' 2>/dev/null)
if [ -n "$changed_rb" ]; then
  output=$(bundle exec rubocop --force-exclusion $changed_rb 2>&1)
  if [ $? -ne 0 ]; then
    errors+="## RuboCop failures\n$output\n\n"
  fi
fi

changed_py=$(git diff --name-only --diff-filter=ACMR HEAD -- '*.py' 2>/dev/null)
if [ -n "$changed_py" ]; then
  output=$(ruff check $changed_py 2>&1)
  if [ $? -ne 0 ]; then
    errors+="## Ruff failures\n$output\n\n"
  fi
fi

# ── Security scanning (full app, intentional) ──
if [ -f "Gemfile" ]; then
  output=$(bundle exec brakeman --no-pager -q 2>&1)
  if [ $? -ne 0 ]; then
    errors+="## Brakeman security failures\n$output\n\n"
  fi
fi

# ── Tests (optional, uncomment if you want tests in the gate) ──
# output=$(python -m pytest --tb=short 2>&1)
# if [ $? -ne 0 ]; then
#   errors+="## Test failures\n$output\n\n"
# fi

# ── Debugging artifacts ──
found=$(grep -rn 'binding\.pry\|binding\.irb\|debugger\|byebug\|breakpoint()' app/ lib/ --include='*.rb' --include='*.py' 2>/dev/null)
if [ -n "$found" ]; then
  errors+="## Debugging statements left in code\n$found\n\n"
fi

if [ -n "$errors" ]; then
  echo -e "$errors"
  exit 2
fi

exit 0
