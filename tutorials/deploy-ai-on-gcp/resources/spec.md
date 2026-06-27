# Spec: AI Proposal Generator

A web app that turns discovery-call notes into a structured v1 proposal in the firm's voice.

The AI generates the *thinking* sections (situation, scope, deliverables). Standard terms, pricing model, and firm boilerplate are configuration. Pricing and dates are filled in by the human.

## Goal

Paste meeting notes, get a v1 proposal in under 30 seconds. Match the firm's voice from a stored past-proposal example. Save to Postgres for status tracking and history. Export to PDF or Markdown.

## What success looks like

- A user pastes notes, presses Generate, and a full structured proposal renders within 30 seconds
- The output reads in the firm's voice (not generic AI tone)
- No pricing, payment terms, or commitment dates are AI-generated
- Past proposals are listed in a sidebar with status pills (draft / sent / accepted / declined)
- Click any past proposal to reload it
- One-click export to PDF (browser print) and copy as Markdown

## Stack

- **Frontend:** Next.js App Router, TypeScript, Tailwind. Cloud Run service, public.
- **Backend:** Python 3.12, FastAPI. Cloud Run service, private (frontend SA invokes via IAM).
- **Database:** Cloud SQL Postgres 15.
- **Inference:** Vertex AI, `gemini-2.5-pro`, JSON mode.
- **Secrets:** Secret Manager (DB password, any external API keys).
- **Region:** `europe-west1`.

## Repository layout

```
proposal-generator/
├── frontend/
│   ├── src/app/page.tsx              # main form + result view
│   ├── src/app/proposals/[id]/page.tsx
│   ├── src/app/config/page.tsx       # firm config editor
│   ├── src/components/ProposalCard.tsx
│   ├── src/components/Sidebar.tsx
│   ├── src/lib/api.ts
│   ├── package.json
│   └── Dockerfile
├── backend/
│   ├── app/main.py                   # FastAPI entrypoint
│   ├── app/routes/proposals.py
│   ├── app/routes/config.py
│   ├── app/services/generation.py    # Vertex call + JSON parsing
│   ├── app/services/db.py
│   ├── app/models/proposal.py
│   ├── app/models/config.py
│   ├── app/prompts/system.md         # generation instructions
│   ├── app/prompts/voice_example.md  # the few-shot proposal
│   ├── pyproject.toml
│   └── Dockerfile
└── schema.sql
```

## Three categories of proposal content

The split is the keystone of this design.

| Category | Source | Example fields |
|---|---|---|
| AI-generated | Per-proposal LLM call from notes | situation_appraisal, scope, deliverables |
| Configuration | Firm-level, stored once | payment_terms, standard_exclusions, firm_responsibilities |
| Human-filled | Per-proposal, manually | investment (price), start_date, duration |

The AI does the thinking. Configuration handles firm boilerplate. The human owns the deal terms.

## Inputs (per-proposal)

```python
class ProposalRequest(BaseModel):
    client_name: str | None = None        # AI extracts from notes if missing
    meeting_notes: str                     # required, max 10_000 chars
    project_type: str | None = None        # one of PROJECT_TYPES
    budget_hint: str | None = None         # one of BUDGET_HINTS
```

`PROJECT_TYPES = ["SaaS", "Internal Tool", "Data Pipeline", "AI Integration", "Other"]`
`BUDGET_HINTS = ["Under £5k", "£5–15k", "£15–50k", "£50k+"]`

## AI-generated sections

The model returns this JSON. All fields required, no nulls in this block.

```json
{
  "client_name": "string",
  "project_title": "string",
  "situation_appraisal": "1–2 paragraphs",
  "whats_at_stake": "1 paragraph",
  "current_challenges": [
    {"title": "string", "description": "string"}
  ],
  "objectives": ["string"],
  "scope": {
    "summary": "1 paragraph",
    "features": [{"title": "string", "description": "string"}]
  },
  "how_it_works": ["string"],
  "technical_approach": {
    "summary": "1 paragraph",
    "components": [{"component": "string", "technology": "string"}]
  },
  "delivery_plan": [
    {"phase": "string", "title": "string", "tasks": ["string"]}
  ],
  "deliverables": ["string"],
  "project_specific_exclusions": ["string"],
  "success_criteria": ["string"],
  "client_responsibilities": ["string"]
}
```

Counts: 4–6 challenges, 4–6 objectives, 5–10 features, 5–10 how-it-works steps, 1–3 phases, 5–8 deliverables, 4–6 success criteria, 2–5 client responsibilities, 0–6 project-specific exclusions.

## Configuration

Single-row table in v1. Editable via `/config` UI. Backend uses the active row at generation time. A snapshot is saved on every proposal so historical proposals don't break if config changes.

```sql
CREATE TABLE firm_config (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  firm_name TEXT NOT NULL,
  firm_legal_name TEXT NOT NULL,
  firm_contact_email TEXT NOT NULL,
  standard_exclusions JSONB NOT NULL DEFAULT '[]'::jsonb,
  firm_responsibilities JSONB NOT NULL DEFAULT '[]'::jsonb,
  payment_terms TEXT NOT NULL,
  running_costs_note TEXT,
  document_classification TEXT NOT NULL DEFAULT 'Confidential',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

Voice example (the past proposal used as a few-shot) lives in `backend/app/prompts/voice_example.md` rather than the database. Edit the file, redeploy, voice changes everywhere. Out of scope to put it in the DB for v1.

## Human-filled fields

```sql
investment_amount NUMERIC,        -- nullable
investment_currency TEXT,         -- nullable, default 'GBP'
start_date DATE,                  -- nullable
duration_weeks INTEGER,           -- nullable
version TEXT NOT NULL DEFAULT '1.0'
```

These render in the UI as clearly-marked placeholder cards saying *"Fill in manually"* until populated.

## Schema

```sql
CREATE TABLE proposals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- inputs
  client_name TEXT NOT NULL,
  meeting_notes TEXT NOT NULL,
  project_type TEXT,
  budget_hint TEXT,

  -- AI output
  ai_content JSONB NOT NULL,

  -- snapshot of firm_config at generation time
  config_snapshot JSONB NOT NULL,

  -- human-filled
  investment_amount NUMERIC,
  investment_currency TEXT DEFAULT 'GBP',
  start_date DATE,
  duration_weeks INTEGER,
  version TEXT NOT NULL DEFAULT '1.0',

  -- pipeline
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'accepted', 'declined')),

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_proposals_status ON proposals(status, created_at DESC);
CREATE INDEX idx_proposals_client ON proposals(LOWER(client_name));
CREATE INDEX idx_proposals_created ON proposals(created_at DESC);
```

## API

| Method | Path | Purpose |
|---|---|---|
| POST | `/proposals` | Generate from notes, return full proposal with null human fields |
| GET | `/proposals` | List recent, filter by status, paginated (default 20) |
| GET | `/proposals/:id` | Load one |
| PATCH | `/proposals/:id` | Update status or human-filled fields |
| DELETE | `/proposals/:id` | Soft delete (set `status='archived'` or hard delete; agent decides) |
| GET | `/config` | Load active firm config |
| PATCH | `/config` | Update firm config (creates new active row, marks previous inactive) |
| GET | `/healthz` | Liveness check |

`POST /proposals` request body:

```json
{
  "client_name": "Sadler Recruitment",
  "meeting_notes": "...",
  "project_type": "AI Integration",
  "budget_hint": "£5–15k"
}
```

Response: full proposal record (id, ai_content, config_snapshot, all null human fields, status='draft').

## Generation pipeline

```
POST /proposals
  ↓
Validate input (Pydantic)
  ↓
Load active firm_config from DB
  ↓
Load system prompt from app/prompts/system.md
  ↓
Load voice example from app/prompts/voice_example.md
  ↓
Build full prompt: system instructions + voice example + user input
  ↓
Call Vertex AI gemini-2.5-pro with response_mime_type="application/json"
  ↓
Parse JSON. On failure: retry once with stricter instructions; if still fails, return 500.
  ↓
Insert row in proposals (ai_content, config_snapshot, defaults for human fields, status='draft')
  ↓
Return full record
```

## System prompt

`backend/app/prompts/system.md` contains hard rules for the AI:

- Output JSON matching the schema. No prose outside JSON.
- Never generate dollar/pound amounts, dates, or commitment timelines.
- Use plain language. No marketing words (no "leverage," "synergy," "enable," "empower," "unlock," "world-class," "best-in-class").
- Active voice. Short paragraphs. 2–4 lines max per paragraph.
- Concrete numbers in the body where the notes support them (team size, headcount, dates mentioned).
- Direct framing. Avoid hedging.
- Match the voice and structure of the example proposal exactly.

## Voice example

`backend/app/prompts/voice_example.md` contains one full past proposal in markdown, used as a one-shot example. The agent prepends this to every generation request.

The example file is the single source of voice control. To change how proposals sound across the firm, edit this file.

**The repo ships with a fictional voice example.** The shipped file is for a made-up client (Nightingale Software) at a placeholder firm. It demonstrates the structure and tone but is intentionally generic. Replace it locally with one of your own real (or anonymised) past proposals before any production use. Real client work belongs in your own deployment, not in a public repo.

To keep your real example out of git, add `voice_example.local.md` to `.gitignore` and load that file instead in your private deployment, or just edit `voice_example.md` and don't push the change.

## Render targets

**Web view (`/proposals/:id`):**
- Header: client name, project title, version, date
- AI sections rendered as cards: situation, what's at stake, challenges, objectives, scope, how it works, technical approach, delivery plan, deliverables, exclusions, success criteria, client responsibilities
- Configuration sections rendered from `config_snapshot`: firm responsibilities, standard exclusions, payment terms, running costs note
- Human-filled cards: investment, timeline. Show "Fill in manually" if null.
- Action bar: status dropdown, Download PDF, Copy Markdown, Edit human fields

**PDF:** Browser-native. A print-only stylesheet hides the action bar and sidebar. `window.print()` triggered from the Download button.

**Markdown:** Serialise the structured data into a markdown template. Frontend function. No backend involvement.

## Frontend pages

- `/`: main form + result view (post-generation)
- `/proposals/:id`: load and render any past proposal
- `/config`: edit firm config

Sidebar (visible on `/` and `/proposals/:id`): list of recent proposals (last 20), status pill, click to load.

## Decisions

- **Vertex AI Gemini 2.5 Pro with JSON mode.** Reason: structured-output reliability and voice quality. Flash is acceptable but voice quality drops noticeably.
- **Configuration in Postgres, single active row.** Reason: simplest single-tenant model. Multi-tenant later.
- **Config snapshot saved on every proposal.** Reason: changes to firm_config don't retroactively break historical proposals.
- **AI never generates pricing, dates, or commitments.** Reason: legal/business liability, and config-driven boilerplate scales better.
- **Browser-native PDF (window.print).** Reason: zero backend dependencies for the MVP. Backend rendering can come later.
- **No streaming response.** Reason: one-shot generation, simpler architecture.
- **Voice example as a file, not in the DB.** Reason: voice is global. File-based makes it part of the deploy artifact, not user-editable in the UI.
- **Single Postgres for everything.** Reason: no service split needed at this scale.
- **Frontend on Cloud Run public, backend on Cloud Run private.** Reason: standard service-to-service IAM pattern, smaller attack surface than a single combined service.

## Invariants

- The AI must never produce a currency amount in any field.
- The AI must never produce calendar dates or weekday commitments. Phrases like "within X weeks" are acceptable; "starting June 5" is not.
- Every row in `proposals` has a non-null `config_snapshot`.
- Standard exclusions from config are appended to `project_specific_exclusions` at render time, not at generation time.
- Status transitions are strict: draft → sent → (accepted | declined). UI must enforce this.
- The voice example file must exist at deploy time. If missing, generation returns 500 with a clear error.

## Out of scope (v1)

- Authentication / login
- Multi-tenant / multiple firms
- Voice or audio transcription
- Knowledge base / RAG over past proposals
- Section-level regeneration with diff/undo
- Inline field editing on the result page (use Markdown copy + edit elsewhere)
- Email integration / sending
- Backend PDF rendering with custom branding
- Win/loss analytics dashboard
- Integration with Fathom, Granola, Fireflies, HubSpot, Salesforce, PandaDoc
- Pricing recommendation logic

## Open questions for the agent

1. **PostgreSQL connection pattern.** Use the Cloud SQL Auth Proxy via the Python connector (`cloud-sql-python-connector`) with `pg8000` or `psycopg`. Confirm choice when implementing.
2. **Frontend → backend auth.** The frontend Cloud Run service account holds `roles/run.invoker` on the backend service. Frontend mints an ID token and passes it as a Bearer header. Confirm this pattern when wiring up.
3. **Soft vs hard delete.** Spec says `DELETE` is soft. Confirm with the user; if hard delete is acceptable, simplify.
4. **Markdown serialisation format.** A reasonable default is in `frontend/src/lib/markdown.ts`. Use sentence case headings, bullet lists, no front matter unless requested.

## Acceptance tests

The build is done when:

1. `terraform apply` provisions all infrastructure.
2. The frontend at `/` accepts a paste, calls `/proposals`, and renders a structured result.
3. The result includes all 13 AI-generated sections plus all configuration sections.
4. No currency amount or date appears anywhere in `ai_content` for a generated proposal.
5. The status dropdown updates the proposal's status and persists.
6. Reloading the page shows recent proposals in the sidebar with correct status pills.
7. Download PDF produces a clean print-styled document.
8. Copy Markdown copies a complete markdown serialisation to the clipboard.
9. The `/config` page loads, shows the firm config, and saves changes.
10. Cloud Logging shows structured JSON entries for every generation request.
11. The Cloud Monitoring dashboard renders all four tiles populated.
12. Deliberately failing the backend triggers the alerting policy and a Slack notification.
