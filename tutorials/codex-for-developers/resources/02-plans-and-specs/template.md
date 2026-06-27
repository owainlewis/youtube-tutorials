# Lightweight Implementation Spec

Use this when you want a short spec for Codex to implement against.

This is not meant to be a long design document.

It is just enough structure to make the change reviewable.

---

**Goal:**
What should be true when this is done? One or two sentences.

**Context:**
Which files, modules, or services are relevant? What does the current behavior look like?

**Acceptance criteria:**
What must be true for this to be correct? Be specific enough that you could write a test for each point.

- [ ] ...
- [ ] ...

**Tests:**
What command should Codex run to verify the work? Or what test should it add?

```bash
just test
# or
pytest tests/api/test_users.py -x
```

**Constraints:**
What should it avoid changing? What patterns must it follow?

**Non-goals:**
What adjacent work should it leave alone?
