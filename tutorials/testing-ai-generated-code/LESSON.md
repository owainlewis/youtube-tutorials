# How I Test AI-Generated Code

Companion repo for the video. Everything you need to set up a testing workflow with AI coding agents.

## The Problem

AI agents write code that looks correct, passes a quick glance, and then breaks in ways you don't expect. Without tests, the agent is relying on its own judgment about whether the code is correct. That judgment is sometimes wrong.

Tests give the agent a closed feedback loop. Write code, run the tests, see what failed, fix it. The agent can actually verify its own work.

## Why Testing Matters More With AI Agents

Two reasons we write tests:

1. **Correctness.** The code does what it's meant to do right now.
2. **Regressions.** Changes to one part of the codebase don't break something else.

AI agents make both worse. They make dozens of changes across your codebase in a single session. They're focused on the task in front of them and have no idea they just broke authentication in another file. Tests are your insurance.

```mermaid
flowchart LR
    subgraph without["Without Tests"]
        direction LR
        A1[Agent writes code] --> A2[Looks right] --> A3[Ships] --> A4[Breaks in production]
    end
    subgraph with_tests["With Tests"]
        direction LR
        B1[Agent writes code] --> B2[Runs tests] --> B3[Sees failure] --> B4[Fixes it] --> B5[Confirmed working]
    end

    style A4 fill:#f87171,color:#fff,stroke:#f87171
    style B5 fill:#34d399,color:#fff,stroke:#34d399
```

## The Testing Pyramid

```mermaid
graph TD
    EVALS["Evals - non-deterministic AI output"] --> E2E["E2E Tests - full user flows"]
    E2E --> INTEGRATION["Integration Tests - components together"]
    INTEGRATION --> UNIT["Unit Tests - single functions (most tests here)"]

    style EVALS fill:#a78bfa,color:#fff,stroke:#a78bfa
    style E2E fill:#f27a3a,color:#fff,stroke:#f27a3a
    style INTEGRATION fill:#3b6ce8,color:#fff,stroke:#3b6ce8
    style UNIT fill:#34d399,color:#fff,stroke:#34d399
```

## What to Test

| Test This | Skip This |
|-----------|-----------|
| Business logic (scoring, pricing, access rules) | Framework boilerplate (does FastAPI return 200?) |
| Complex conditionals with multiple branches | Library behavior (does `json.loads` work?) |
| Data transformations (reshape input to output) | Mocks testing mocks |
| Edge cases AI consistently misses (nulls, boundaries) | Simple CRUD with no custom logic |

**The rule:** "Am I testing my logic or someone else's code?" If someone else's, skip it.

## Test-First vs Test-After

### Test-After (common approach)

Write code first, then write tests to verify. Better than no tests. But with AI agents, if you say "write tests for this code," the agent reads the code and writes tests that pass the current behavior. It's grading its own homework.

The stat: AI-generated code with 100% test coverage scored **4% on mutation testing**. Every line executed. Every test green. Caught almost nothing.

### Test-First (TDD)

Write the test first. The test describes what the code *should* do. Then write the code to make it pass.

```mermaid
flowchart LR
    R["🔴 Red\nWrite test\nIt fails"] --> G["🟢 Green\nMinimum code\nto pass"] --> RF["🔵 Refactor\nClean up\nTests keep it honest"] --> R

    style R fill:#f87171,color:#fff,stroke:#f87171
    style G fill:#34d399,color:#fff,stroke:#34d399
    style RF fill:#3b6ce8,color:#fff,stroke:#3b6ce8
```

With AI agents, this gives the agent a concrete target and prevents over-engineering.

## The Workflow

The key insight: **you decide what to test, the agent handles the red-green cycle.** One well-directed prompt beats two separate ones.

```mermaid
flowchart TD
    YOU["👤 You decide what to test"] --> PROMPT["Write a prompt focused on risk"]
    PROMPT --> TDD["Agent runs red-green-refactor"]
    TDD --> RED["🔴 Writes test, confirms it fails"]
    RED --> GREEN["🟢 Implements minimum code to pass"]
    GREEN --> REFACTOR["🔵 Cleans up"]
    REFACTOR --> SUITE["Runs full test suite"]
    SUITE --> CHECK{Regressions?}
    CHECK -->|No| NEXT["Next test"]
    CHECK -->|Yes| FIX["Fixes regression"]
    FIX --> SUITE

    style YOU fill:#3b6ce8,color:#fff,stroke:#3b6ce8
    style RED fill:#f87171,color:#fff,stroke:#f87171
    style GREEN fill:#34d399,color:#fff,stroke:#34d399
    style NEXT fill:#34d399,color:#fff,stroke:#34d399
```

### Example Prompt

Direct the agent toward **risk**, not coverage. Tell it what could go wrong, not which functions to test.

```
/tdd

Read the spec at .ai/specs/auth.md

Implement the auth service. Think about what could actually go wrong.
Focus on behaviours where a bug would be a security vulnerability.
Don't test library functions (bcrypt, secrets). Test our decisions
and security risks.
```

The `/tdd` skill handles the red-green cycle automatically. You handle what to test.

### The Principle

If you say "write tests and implement this feature," you've handed over the most important decision: **what to test**. The agent will test everything because it has no judgment about what matters in your system. You do.

Research backs this up: targeted TDD reduced regressions by 70%. Vague "do TDD" instructions made things worse (regressions went from 6% to 10%).

## CLAUDE.md Testing Config

Drop this into your project's `CLAUDE.md` to set the testing baseline for every session:

```markdown
## Testing

- Run tests with: `uv run pytest tests/ -x`
- Use red-green TDD for new features with business logic
- Write tests for: business logic, complex conditionals, data transformations, edge cases
- Do NOT write tests for: framework boilerplate, library behavior, simple CRUD
- After implementation, run the full test suite to check for regressions
- If tests fail, fix the code, not the tests (unless the test is genuinely wrong)
```

## Example: Good Test vs Bad Test

### Good: Tests business logic

```python
def test_scorer_zero_experience_perfect_skills():
    """Candidate with no experience but perfect skill match
    should still score above 0.5 because skills outweigh tenure."""
    candidate = Candidate(years_experience=0, skills=["python", "fastapi", "postgresql"])
    job = Job(required_skills=["python", "fastapi", "postgresql"])

    score = calculate_score(candidate, job)

    assert score > 0.5
    assert score < 1.0  # Not a perfect score without experience
```

### Good: Tests a security boundary

```python
def test_recruiter_cannot_see_other_recruiters_candidates():
    """Data isolation: recruiter A should never see recruiter B's candidates."""
    recruiter_a = create_recruiter("alice@company.com")
    recruiter_b = create_recruiter("bob@company.com")
    candidate = create_candidate(recruiter_id=recruiter_b.id)

    response = client.get("/candidates", headers=auth_headers(recruiter_a))

    assert candidate.id not in [c["id"] for c in response.json()]
```

### Bad: Tests the framework

```python
def test_health_endpoint_returns_200():
    """This tests FastAPI, not your code."""
    response = client.get("/health")
    assert response.status_code == 200
```

### Bad: Tests a mock

```python
def test_sends_email(mock_smtp):
    """This tests that the mock was called, not that email actually works."""
    send_welcome_email("user@example.com")
    mock_smtp.send.assert_called_once()
    # When the real SMTP server rejects the email, this test still passes.
```

## The Live Demo Workflow

What I show in the video, step by step:

### Cycle 1: Auth

```
Prompt: "Write a test that verifies a user with the wrong password gets a 401."
-> Agent writes test -> Run -> Red (or Green if auth works, which locks in the behavior)
```

### Cycle 2: Scorer Edge Case

```
Prompt: "Write a test for when a candidate has zero experience but perfect skill matches."
-> Agent writes test -> Run -> Red
-> Agent implements -> Run -> Green
-> Run full suite -> No regressions
```

### Cycle 3: Data Isolation

```
Prompt: "Write a test that recruiter A cannot see recruiter B's candidates."
-> Agent writes test -> Run -> Red (no tenant filtering exists)
-> Agent adds scoping to query -> Run -> Green
```

### The Skip

"I'm not going to write a test for this CRUD endpoint. It's standard FastAPI. A test here would just be testing that FastAPI works."

## Key Stats

| Stat | Source |
|------|--------|
| AI-generated tests: 100% coverage, 4% mutation score | HumanEval-Java study |
| AI-authored PRs: 75% more logic errors than human PRs | CodeRabbit, Dec 2025 |
| Targeted TDD: 70% regression reduction | TDAD paper (arXiv) |
| Vague TDD instructions: regressions increased from 6% to 10% | TDAD paper (arXiv) |

## Files in This Repo

```
testing-ai-generated-code/
├── README.md              # This file
├── resources/slides/slides.html # Branded slide deck for the video
├── prompts/
│   ├── test-first.md      # Prompt 1: Write the test (with wrong vs right examples)
│   ├── make-it-pass.md    # Prompt 2: Make it pass
│   ├── single-prompt.md   # Combined approach for smaller tasks
│   └── claude-md.md       # CLAUDE.md testing config (Python, TS, Ruby)
└── examples/
    ├── COMPARISON.md       # Before vs after comparison table
    ├── good-tests.py       # Examples of useful tests
    ├── bad-tests.py        # Examples of wasteful tests
    ├── trivial-tests/      # Before: implementation-focused prompt
    │   ├── auth_service.py     # The implementation
    │   └── test_auth_service.py # 7 tests, mostly testing libraries
    └── better-tests/       # After: risk-focused prompt
        ├── auth_service.py     # The improved implementation
        └── test_auth_service.py # 6 tests, all proving real requirements
```

## The /tdd Skill

The live demo uses the `/tdd` skill from the Blueprint plugin. It enforces red-green-refactor automatically: write a failing test, implement the minimum to pass, clean up, repeat. Every test must justify its existence.

Install it:
```bash
/plugin marketplace add owainlewis/blueprint
/plugin install blueprint@owainlewis-blueprint
```

Then use it:
```
/tdd

Read the spec at .ai/specs/auth.md
Implement the auth service. Think about what could actually go wrong.
Don't test library functions. Test our decisions and security risks.
```

The skill handles the red-green cycle. You handle what to test.

See the full skill: [Blueprint TDD Skill](https://github.com/owainlewis/blueprint/blob/main/skills/tdd/SKILL.md)

## Related

- [How I Review AI-Generated Code](../ai-code-review/) - The companion video on code review
- [Blueprint plugin](https://github.com/owainlewis/blueprint) - Full SDLC workflow including TDD skill
- [Agent Skills by Addy Osmani](https://github.com/addyosmani/agent-skills) - Comprehensive collection of Claude Code skills including a detailed TDD skill with the Prove-It Pattern, test pyramid, DAMP over DRY, and anti-patterns guide
