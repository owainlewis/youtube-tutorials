# Spec-Driven Development: It's Simpler Than You Think

Everyone's overcomplicating spec-driven development. PRDs, design docs, spec deltas, Gherkin scenarios, OpenSpec, SpecKit...

It's a plan and a checklist. That's it.

## The Traditional Workflow

Before AI, every serious engineering org built software the same way:

| Step | What | Example |
|------|------|---------|
| 1. Problem | Identify the issue | "Users can't delete notes" |
| 2. Plan | Design doc / RFC / Tech spec | Why + What + How |
| 3. Tasks | Break it down | "Add delete button", "Create dialog" |
| 4. Code | Build it | Implementation |

Google calls the plan a "Design Doc." Amazon calls it "Working Backwards." Stripe calls it an "RFC." Startups call it a "Tech Spec."

It's all the same thing wearing different hats.

## The Insight

**AI doesn't replace this workflow. AI accelerates it.**

The problem with most AI coding right now? People skip to step 4.

"Hey Claude, build me authentication."

That's asking the AI to figure out the problem, make the plan, decide the tasks, AND write the code — all from one sentence. It guesses. It guesses wrong.

But when you give AI a clear plan? It's exceptional. Execution that used to take days now takes minutes.

## The Simple Truth

For AI-assisted development, you need two files:

```
.ai/features/add-note-deletion/
├── plan.md    # The plan (why + what + how)
└── tasks.md   # The checklist (what to build)
```

That's the whole system.

- `plan.md` is your design doc. Documentation for future you.
- `tasks.md` is your execution checklist. AI checks these off as it works.

## Quick Start

### 1. Install the commands

```bash
cp -r commands/* ~/.claude/commands/
```

### 2. Create CLAUDE.md in your project

```markdown
# Project Name

## Patterns
- FastAPI for endpoints
- Pydantic for validation
- SQLAlchemy for database

## Rules
- Use uv for packages
- Tests required for new features
```

### 3. Use the workflow

```bash
/spec Add user authentication    # Creates plan.md + tasks.md
# Review the plan
# Implement: "read .ai/features/user-auth and implement, updating checkboxes"
/review                          # Review the code
/commit                          # Commit with a good message
```

## The Commands

### /spec

Creates a plan and task list for a feature.

```
/spec Add hybrid search with pgvector
```

Creates `.ai/features/pgvector-hybrid-search/`:

**plan.md:**
```markdown
# PGVector Hybrid Search

## Why
We need semantic search for our knowledge base. Pure keyword search misses
relevant results when users phrase things differently. Hybrid search combines
vector similarity with full-text search for better recall.

## What Changes
- Add pgvector extension to PostgreSQL
- Create embeddings table with vector column
- Implement hybrid search combining vector + keyword scoring

## How
- Use pgvector (1536 dims for text-embedding-3-small)
- Full-text via PostgreSQL tsvector and ts_rank
- RRF (Reciprocal Rank Fusion) for combining results

## Files Affected
- `docker-compose.yml` - pgvector image
- `src/db/schema.sql` - documents table with vector column
- `src/services/search.py` - hybrid search implementation
- `src/api/routes/search.py` - /search endpoint
```

**tasks.md:**
```markdown
# Tasks: PGVector Hybrid Search

## Infrastructure
- [ ] Update docker-compose to use pgvector/pgvector:pg16
- [ ] Create migration to enable pgvector extension
- [ ] Create documents table with vector(1536) column
- [ ] Add HNSW index for vector search

## Data Layer
- [ ] Create embeddings service (OpenAI text-embedding-3-small)
- [ ] Implement vector_search using cosine similarity
- [ ] Implement keyword_search using ts_rank
- [ ] Implement hybrid_search with RRF

## API Layer
- [ ] Create /search POST endpoint
- [ ] Create /documents POST for ingestion

## Verification
- [ ] Hybrid outperforms keyword-only on test queries
- [ ] Search latency < 100ms
```

### /review

Reviews code like a senior engineer.

```
/review src/components/NoteCard.tsx
```

### /commit

Generates a commit message that explains WHY, not just WHAT.

```
/commit
```

## FAQ

### "Claude Code has planning mode. Why files?"

Planning mode is ephemeral — it disappears after your session. Files persist. They're version controlled. A new engineer can read them six months later.

Planning mode is thinking out loud. Files are documentation.

### "Isn't this just waterfall?"

Waterfall is months of planning before writing code. This is five minutes.

The plan is 15 lines. Think of it as a sketch, not a blueprint. You can change it. You probably will. But starting with a sketch beats starting with nothing.

### "When do I need more than this?"

| Situation | What you need |
|-----------|---------------|
| Bug fix | Nothing — just fix it |
| Small feature (1-2 files) | Maybe nothing |
| Medium feature (3-5 files) | plan.md + tasks.md |
| Large feature (5+ files) | Full spec, maybe split into multiple |
| Team with reviews | Consider OpenSpec for spec deltas |
| Compliance/audit | Formal requirements, traceability |

Start simple. Add complexity only when you hit a wall.

## The Mapping

| Traditional | AI Workflow |
|-------------|-------------|
| Design Doc / PRD / RFC | `plan.md` |
| JIRA tickets / Subtasks | `tasks.md` |
| Engineer coding | AI execution |

Same workflow. Faster execution.

## Key Takeaways

1. **It's the same workflow.** Problem → Plan → Tasks → Code. AI accelerates step 4.

2. **Two files.** plan.md (the thinking) + tasks.md (the checklist).

3. **The plan is documentation.** Not just for AI — for future you.

4. **Start simple.** You probably don't need OpenSpec, Gherkin, or formal requirements.

5. **Stop overcomplicating it.**
