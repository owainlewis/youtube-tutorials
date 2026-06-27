# Good Lightweight Spec Example

---

**Goal:**
Add a `/health` endpoint to the FastAPI app that returns `{"status": "ok"}` with a 200 status code.

**Context:**
The app entry point is `src/api/main.py`. Existing routes are in `src/api/routers/`. Follow the pattern in `src/api/routers/users.py` for how routers are structured and registered.

**Acceptance criteria:**
- [ ] `GET /health` returns `{"status": "ok"}` with HTTP 200
- [ ] The endpoint is registered in `main.py` using the same pattern as existing routers
- [ ] A test exists at `tests/api/test_health.py` that calls the endpoint and asserts the response

**Tests:**
```bash
pytest tests/api/test_health.py -x
```

**Constraints:**
Do not modify any existing routers or tests. Do not add any new dependencies.

**Non-goals:**
Do not add authentication, metrics, or database checks to the health endpoint. Keep it simple.
