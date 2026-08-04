set shell := ["bash", "-euo", "pipefail", "-c"]

default:
    @just --list

new-tutorial slug title:
    @python3 scripts/scaffold_tutorial.py {{quote(slug)}} {{quote(title)}}

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

check-dependencies:
    @python3 scripts/check_python_dependencies.py
