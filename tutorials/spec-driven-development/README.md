# Spec-Driven Development

## What is Spec-Driven Development?

Spec-driven development is writing a plan before you write code. You describe what you're building, why, and how — then you (or an AI) implement it.

It's the same workflow engineers at Google, Amazon, and Stripe have used for decades. The only difference: AI executes the plan instead of (or alongside) you.

## What Problem Does It Solve?

Most people use AI coding tools like this:

```
"Hey Claude, add user authentication"
```

The AI guesses what you want. It picks a random auth library. It puts files in weird places. It doesn't match your patterns. You spend more time fixing its work than you saved.

**The problem:** You're asking AI to think AND execute from a single sentence.

**The solution:** Separate thinking from execution. You think (write a plan). AI executes (writes the code).

When you give AI a clear plan, it's exceptional. When you don't, it guesses.

## What's In This Repo?

Slash commands for Claude Code that implement spec-driven development:

| Command | What it does |
|---------|--------------|
| `/spec` | Creates a plan + task checklist for a feature |
| `/task` | Implements a single task from the checklist |
| `/review` | Reviews code like a senior engineer |
| `/commit` | Generates a commit message |

Plus examples you can reference:
- `examples/pgvector-hybrid-search/` — RAG infrastructure setup
- `examples/ai-chat-endpoint/` — Streaming chat API

---

## The Core Idea

Two files. That's the whole system.

```
.ai/features/my-feature/
├── plan.md    # Why + What + How
└── tasks.md   # Checklist for execution
```

**plan.md** captures your thinking. Why are we building this? What changes? What's the approach?

**tasks.md** is the checklist. AI works through it, checking boxes as it goes.

---

## Quick Start

### 1. Install the commands

```bash
cp -r commands/* ~/.claude/commands/
```

### 2. Use it

```bash
/spec Add hybrid search with pgvector
```

This creates `.ai/features/pgvector-hybrid-search/` with:
- `plan.md` — the plan
- `tasks.md` — the checklist

Then implement:

```
Read .ai/features/pgvector-hybrid-search and implement it.
Update the checkboxes in tasks.md as you complete each task.
```

---

## Example

Here's what `/spec Add hybrid search with pgvector` generates:

**plan.md:**
```markdown
# PGVector Hybrid Search

## Why
We need semantic search for our knowledge base. Pure keyword search
misses relevant results. Hybrid search combines vector similarity
with full-text search for better recall.

## What Changes
- Add pgvector extension to PostgreSQL
- Create embeddings table with vector column
- Implement hybrid search combining vector + keyword scoring

## How
- Use pgvector (1536 dims for text-embedding-3-small)
- Full-text via PostgreSQL tsvector
- RRF (Reciprocal Rank Fusion) for combining results

## Files Affected
- `docker-compose.yml` - pgvector image
- `src/db/schema.sql` - documents table
- `src/services/search.py` - hybrid search
- `src/api/routes/search.py` - /search endpoint
```

**tasks.md:**
```markdown
# Tasks: PGVector Hybrid Search

## Infrastructure
- [ ] Update docker-compose to use pgvector/pgvector:pg16
- [ ] Create migration to enable pgvector extension
- [ ] Create documents table with vector(1536) column

## Data Layer
- [ ] Create embeddings service
- [ ] Implement vector_search
- [ ] Implement keyword_search
- [ ] Implement hybrid_search with RRF

## API Layer
- [ ] Create /search POST endpoint
- [ ] Create /documents POST for ingestion

## Verification
- [ ] Hybrid outperforms keyword-only
- [ ] Search latency < 100ms
```

---

## Why Two Files?

**Why not one file?**

The plan is documentation — it should stay clean. The tasks get modified during execution (checkboxes). Separating them keeps the plan readable.

**Why not just use Claude's planning mode?**

Planning mode is ephemeral. When your session ends, the plan disappears. Files persist. They're version controlled. A new engineer can read them six months later.

**Isn't this just waterfall?**

Waterfall is months of planning. This is five minutes.

The plan is 15 lines. It's a sketch, not a blueprint.

---

## When Do You Need This?

| Situation | What to do |
|-----------|------------|
| Bug fix | Just fix it |
| Tiny feature (1 file) | Probably skip it |
| Real feature (3+ files) | Write a plan |
| Complex feature (5+ files) | Definitely write a plan |

Rule of thumb: if you'd write a JIRA ticket for it, write a plan.

---

## The Commands

### /spec

Creates plan.md + tasks.md for a feature.

```
/spec Add user authentication with OAuth
```

### /task

Implements a single task from tasks.md.

```
/task .ai/features/user-auth "Add OAuth callback handler"
```

### /review

Reviews code for simplicity, clarity, and bugs.

```
/review src/services/auth.py
```

### /commit

Generates a commit message explaining WHY, not just WHAT.

```
/commit
```

---

## How It Maps to Traditional Engineering

| Traditional | Spec-Driven |
|-------------|-------------|
| Design Doc / PRD / RFC | `plan.md` |
| JIRA subtasks | `tasks.md` |
| Engineer writes code | AI writes code |

Same workflow. Faster execution.
