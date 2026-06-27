# Bad Lightweight Spec Example

This is what most people write. The result is unpredictable output that wastes your review time.

---

**The bad spec:**

> "Add a health check endpoint"

**What's wrong:**

- No file location. Codex will guess where to put it.
- No response format. You might get `{"healthy": true}` instead of `{"status": "ok"}`.
- No test requirement. You may get no test at all.
- No constraints. Codex might add a database ping, an import you don't want, or a new dependency.
- No pattern reference. It won't follow your existing router structure.

**The result:**

You get code that technically works but doesn't match your conventions, has no test,
and requires a round of follow-up corrections that a good brief would have prevented.

Write the good version first. It takes 3 minutes. It saves 20.
