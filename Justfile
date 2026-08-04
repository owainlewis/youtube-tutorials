set shell := ["bash", "-euo", "pipefail", "-c"]

default:
    @just --list

new-tutorial slug title:
    @case "{{slug}}" in *[!a-z0-9-]*|"") echo "Slug must use lowercase letters, numbers, and hyphens only."; exit 1 ;; esac
    @dir="tutorials/{{slug}}"; \
      if [ -e "$dir" ]; then echo "$dir already exists."; exit 1; fi; \
      mkdir -p "$dir/code" "$dir/resources" "$dir/resources/slides"; \
      cp tutorials/_templates/LESSON.md "$dir/LESSON.md"; \
      cp tutorials/_templates/resources/prompts.md "$dir/resources/prompts.md"; \
      touch "$dir/code/.gitkeep" "$dir/resources/.gitkeep" "$dir/resources/slides/.gitkeep"; \
      python3 -c 'from pathlib import Path; import sys; d=Path(sys.argv[1]); title=sys.argv[2]; readme=f"# {title}\n\nThis is the supporting material for the video: {title}.\n\n## Start Here\n\n- Read the lesson: [LESSON.md](./LESSON.md)\n- Browse code samples: [code/](./code/)\n- Browse resources: [resources/](./resources/)\n- Browse slides: [resources/slides/](./resources/slides/)\n\n## Go Deeper\n\nTo go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).\n"; (d/"README.md").write_text(readme); lesson=d/"LESSON.md"; lesson.write_text(lesson.read_text().replace("# Lesson Title", "# "+title, 1))' "$dir" "{{title}}"; \
      echo "Created $dir"

check:
    @git diff --check
    @just audit-tutorial-catalog
    @just audit-layout
    @just audit-root-docs
    @just audit-junk

update-tutorial-catalog:
    @python3 scripts/tutorial_catalog.py --write

audit-tutorial-catalog:
    @python3 scripts/tutorial_catalog.py

audit-layout:
    @python3 -c 'from pathlib import Path; allowed={"README.md","LESSON.md","resources","code"}; bad=[(t, allowed-{p.name for p in t.iterdir()}, {p.name for p in t.iterdir()}-allowed) for t in sorted(Path("tutorials").iterdir()) if t.is_dir() and ((allowed-{p.name for p in t.iterdir()}) or ({p.name for p in t.iterdir()}-allowed))]; [print(f"{t}\\n  missing: {sorted(m)}\\n  extra: {sorted(e)}") for t,m,e in bad]; raise SystemExit(1 if bad else 0)' && echo "Tutorial layout OK."

audit-root-docs:
    @bad="$(find tutorials -mindepth 2 -maxdepth 2 -type f -name '*.md' ! -name README.md ! -name LESSON.md | sort)"; \
      if [ -n "$bad" ]; then echo "$bad"; echo "Move tutorial root reference docs into resources/."; exit 1; fi; \
      echo "Tutorial root docs OK."

audit-junk:
    @git ls-files | rg '(^|/)(\.venv|venv|__pycache__|\.pytest_cache|\.ruff_cache|\.mypy_cache|\.DS_Store|\.git/|node_modules|dist/|build/|\.lsp|\.clj-kondo|\.ipynb_checkpoints|uv\.lock$|.*\.log$|\.env$|\.env\.local$)' && { echo "Tracked junk found."; exit 1; } || echo "No tracked junk found."
