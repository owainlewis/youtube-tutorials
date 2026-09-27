# Development setup and build walkthrough

This guide starts with the preserved website and prepares a coding assistant to
build the hotel agent. The backend and deployment are still planned. The CLI
commands below do not turn the saved website into a working AI application by
themselves.

Documentation checked on 27 September 2026. Local checks used Agents CLI 1.7.0
and Google Cloud CLI 549.0.0. The scaffold command succeeded in a temporary
directory with cloud checks skipped. Authentication, paid model calls, and deployment
have not been run as part of this documentation change.

## 1. Preview the starting point

From the repository root:

```bash
cd tutorials/hotel-support-agent/code
python3 -m http.server 8773 --bind 127.0.0.1 --directory website
```

Open http://127.0.0.1:8773/. The concierge is a scripted UI mockup. Keep it as the
visual reference while building the backend. Use a second terminal for setup.

## 2. Install the development prerequisites

The recording path is macOS. Install Python 3.11 or newer, Node.js, and uv using
their official installers: [Python](https://www.python.org/downloads/),
[Node.js](https://nodejs.org/en/download), and
[uv](https://docs.astral.sh/uv/getting-started/installation/).

From any directory, check:

```bash
python3 --version
node --version
uv --version
```

Expect a version from each command. Restart the terminal if an installer changed
PATH. No Google credentials are needed to serve the static design.

## 3. Install Google Cloud CLI

Use Google's [installation guide](https://docs.cloud.google.com/sdk/docs/install-sdk).
For macOS, select the archive for your processor (Apple silicon ARM64 or Intel
x86_64). Extract it outside the repository. Open a terminal in the directory
containing the extracted `google-cloud-sdk` folder and run:

```bash
./google-cloud-sdk/install.sh
```

Accept the PATH setup, restart the terminal, then check:

```bash
gcloud version
```

Expect a Google Cloud SDK version. This tutorial does not require an AI Studio
API key. Linux and Windows users should follow the matching installer on the
same official page.

## 4. Select a dedicated project and sign in

Use a project you own or are authorized to use, with billing configured before
paid API calls. Choose a supported model region before recording. Replace both
example values below with your actual project ID and selected region.

Run from any directory. Create the named configuration once; on later visits use
`gcloud config configurations activate hotel-support-agent` instead.

```bash
gcloud config configurations create hotel-support-agent
gcloud init
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-east1"
gcloud config set project "$GOOGLE_CLOUD_PROJECT"
gcloud config get-value project
```

In `gcloud init`, sign in and choose the dedicated project. Confirm the final
printed project ID before changing cloud resources. A separate gcloud
configuration helps isolate CLI settings; it does not create a project or a
separate billing account. See [gcloud initialization](https://docs.cloud.google.com/sdk/docs/initialize).

## 5. Authenticate the local application

The CLI's account and the credentials read by Python libraries are separate.
Use Application Default Credentials (ADC) for the local agent:

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project "$GOOGLE_CLOUD_PROJECT"
export GOOGLE_GENAI_USE_VERTEXAI=TRUE
```

The browser sign-in stores ADC outside the repo. The quota-project step needs
permission to consume services in that project. Keep the SDK environment variable
spelling exactly as shown even when describing the platform by its current name.
Avoid printing access tokens while recording. Cloud Run will later use a service
identity rather than your local user credentials.

Model invocation also needs the model API enabled and appropriate IAM permissions.
An authorized project administrator can enable the model API with:

```bash
gcloud services enable aiplatform.googleapis.com --project "$GOOGLE_CLOUD_PROJECT"
```

Use the narrow model-access permissions required by your project, not Owner as a
shortcut. Calendar access is a separate integration: later share only the demo
calendar with the application identity and use read-only Calendar scope. Cloud
ADC alone does not grant access to a private calendar.

Sources: [ADC login](https://docs.cloud.google.com/sdk/gcloud/reference/auth/application-default/login)
and [Agents CLI authentication](https://google.github.io/agents-cli/guide/authentication/).

## 6. Install Agents CLI and coding-agent skills

Run this from the tutorial's `code` directory. Preview setup first:

```bash
uvx google-agents-cli setup --dry-run
uvx google-agents-cli setup
agents-cli --version
agents-cli --help
```

Setup installs the CLI and skills into detected coding assistants. Its default
skill installation is global; inspect the preview before proceeding. Use the
coding assistant's installed-skills view to verify that
`google-agents-cli-workflow` is available. Reopen the assistant if needed.
The assistant itself still needs its own sign-in or subscription.

If `agents-cli` is missing after installation, follow uv's PATH guidance and
restart the terminal. The package is `google-agents-cli`; the command is
`agents-cli`. ADK is the Python framework used by the generated application.

Source: [Agents CLI getting started](https://google.github.io/agents-cli/guide/getting-started/).

## 7. Inspect a generated starter without overwriting the design

Use a separate scratch directory. In the recording, ask the coding assistant to
run and explain these commands. The scratch project is for inspecting generated
files, not a second repository inside this tutorial.

```bash
HOTEL_SCRATCH_DIR=$(mktemp -d)
cd "$HOTEL_SCRATCH_DIR"
agents-cli create hotel-agent --prototype --deployment-target cloud_run --session-type in_memory --skip-checks --yes
cd hotel-agent
agents-cli install
agents-cli playground
```

Expect a generated project and a local playground URL printed by the CLI. The
prototype deliberately starts with in-memory sessions; that is insufficient for
our deployed design. `--skip-checks` skips scaffold-time cloud validation, not
runtime authentication. Model requests can still fail or incur usage charges.
Read the generated environment configuration and select a model available to
your project/region before testing it. Do not copy generated `.env`, lockfiles,
caches, or nested Git metadata into this teaching repository.

This is a starter inspection workflow, not a claim that the hotel backend exists.
Scaffold creation was tested with 1.7.0. Dependency installation and playground
startup were checked in CLI help only; cloud behavior remains unverified.
The online reference also lists `cmd-info`, which was absent from the installed
1.7.0 command set, so this walkthrough does not depend on it.
Source: [CLI reference](https://google.github.io/agents-cli/cli/).

## 8. Build the hotel workflow through the coding assistant

Return to the tutorial folder. Give the assistant the
[implementation prompt](./prompts.md), the existing `code/website/` files, and
[lesson architecture](../LESSON.md#proposed-architecture). Build in this order:

1. Add the Python API and ADK agent. Prove one guide answer with a source link.
2. Add local PostgreSQL guide content and persistent, server-owned sessions.
3. Add calendar lookup against fictional events in one demo calendar. Test empty
   results, time zones, and timeouts separately.
4. Add confirmed host requests with an idempotency key and a staff-only list.
5. Replace the widget's scripted responses with streaming API output. Keep the
   visual design, but remove fixture-only room/date assumptions.
6. Run deterministic tool tests and the lesson's evaluation cases. Compare manual
   verdicts with a judge and report model usage separately from infrastructure.
7. After settling Cloud Run versus managed Agent Runtime, generate and review
   deployment configuration. Configure Cloud SQL, service identity, secrets,
   limits, and tracing before running the deployment command.
8. Repeat the guest journey on the cloud URL, inject a calendar failure, inspect
   its trace, and verify the handoff persists after an application restart.

Each step should produce a working slice before continuing. Record the exact
commands, output, chosen model, and observed failures as implementation proceeds.
Do not present this sequence as an already completed cloud deployment. A custom
FastAPI website and persistent data need integration beyond the default scaffold.

## Troubleshooting and cleanup

| Symptom | Check |
| --- | --- |
| `agents-cli` not found | uv tool PATH and a fresh terminal; compare package name with command name. |
| Missing ADC | Complete application-default login; CLI login alone is not enough. |
| 403 from model | Selected project, model API, billing, IAM, model access and region. |
| Calendar lookup denied | Calendar API, read-only scope, and access to that specific calendar. |
| Playground works but website is static | Expected until step 8 connects the widget to the backend. |
| Conversation disappears on restart | In-memory starter sessions must be replaced before deployment. |

Stop preview/playground servers with Ctrl-C. New conversation resets the static
widget. The scratch starter is disposable; remove only the directory recorded in
`HOTEL_SCRATCH_DIR` after inspecting it. No cloud deployment is performed by this
guide's scaffold command. If you later provision resources, record the exact
resources and their teardown instructions with that implementation; deleting a
Cloud Run service alone will not remove Cloud SQL or stored build artifacts.
