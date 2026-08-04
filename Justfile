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
    @python3 -m unittest discover -s scripts/tests
    @just audit-tutorial-catalog
    @just audit-layout
    @just audit-root-docs
    @just audit-junk
    @just audit-markdown-links
    @just audit-verification
    @just audit-syntax
    @just audit-data
    @just audit-terraform

update-tutorial-catalog:
    @python3 scripts/tutorial_catalog.py --write

audit-tutorial-catalog:
    @python3 scripts/tutorial_catalog.py

audit-layout:
    @python3 scripts/repository_checks.py layout

audit-root-docs:
    @python3 scripts/repository_checks.py root-docs

audit-junk:
    @python3 scripts/repository_checks.py junk

audit-markdown-links:
    @python3 scripts/repository_checks.py markdown-links

audit-verification:
    @python3 scripts/repository_checks.py verification

audit-syntax:
    @python3 scripts/repository_checks.py syntax

audit-data:
    @python3 scripts/repository_checks.py data

audit-terraform:
    @python3 scripts/repository_checks.py terraform

test-offline:
    @python3 scripts/run_offline_tests.py --kind offline

test-network:
    @python3 scripts/run_offline_tests.py --kind network
