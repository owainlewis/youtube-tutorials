# Tutorial Verification

The repository has 15 tutorials with tracked files under `code/`.

Each one belongs to one class:

- **Runnable** means the tutorial contains a program or demo with documented
  install, run, test, and reset steps.
- **Snippet-only** means the code supports the lesson but is not a standalone
  application. Its check validates the useful local boundary.
- **Infrastructure-only** means the primary artifact describes infrastructure.
  Its default check is static and never deploys resources.

The machine-readable inventory is
[`scripts/tutorial_verification.json`](../scripts/tutorial_verification.json).
Repository checks require every code-bearing tutorial to appear there. They
also verify that runnable documentation headings still exist.

## Complete Matrix

| Tutorial | Class | Default proof |
| --- | --- | --- |
| 6 Types of RAG | Runnable | Unit tests cover the six retrieval strategies with fake model and database boundaries. |
| AI Agent Memory | Runnable | Standard-library unit tests cover local memory utilities. |
| AI Code Review | Snippet-only | A temporary Git repository proves the template install and deterministic stop hook. |
| DeepSeek Harness | Snippet-only | Node syntax checks validate the host and browser plugin modules without starting the harness. |
| Deploy AI on GCP | Infrastructure-only | Terraform formatting and classifier dry-run unit tests run without a deployment. |
| Docker Sandboxes | Runnable | A local HTTP server unit test runs without Docker. |
| Herdr Agent Workflow | Snippet-only | Shell parsing and the setup helper's usage path run without installing integrations. |
| Intent-Based Classification | Runnable | Unit tests cover routing policy and the out-of-scope path without a model. |
| Micro Agents | Runnable | Unit tests mock YouTube clients and cover parsing, dispatch, failures, and upload termination. |
| Micro Neo | Runnable | Go tests and `go vet` cover the agent loop, tools, workspace boundary, and terminal events. |
| Nano Agent | Runnable | Pytest uses provider fakes and covers the loop, tools, configuration, events, and listeners. |
| Pi Agent Workflow | Runnable | Standard-library tests replace the model SDK and cover the teaching harness boundaries. |
| Pi Coding Agent Guide | Snippet-only | A Node script parses configuration and checks the copyable extension resources. |
| PostgreSQL for RAG | Runnable | A static verifier checks Python, SQL, Compose, and configuration agreement without services. |
| Testing AI-Generated Code | Snippet-only | Standard-library unit tests prove the focused session policy example. |

## Run The Matrix

Install these local tools before running the complete repository check:

- Python 3.12 or newer
- Go 1.23 or newer
- Node.js 22 or newer
- Terraform
- `uv`
- `just`

Then run this from the repository root:

```bash
just check
```

To run only the tutorial commands:

```bash
just test-offline
```

The default matrix needs no API keys, cloud credentials, Docker daemon,
database, or paid service. Tests replace external calls with fakes or fixtures.
The first run may download declared test dependencies through `uv`.

`just check-dependencies` is separate. It resolves current Python dependencies
without writing lockfiles into tutorial folders.
