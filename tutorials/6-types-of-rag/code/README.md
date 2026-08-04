# Code for 6 Types of RAG

The main [lesson](../LESSON.md) explains the six strategies and their tradeoffs.

Run the credential-free tests:

```bash
python3 -m unittest discover -s tests -v
```

For the live examples, install without creating a lockfile:

```bash
uv venv
uv pip install --python .venv/bin/python -e .
cp .env.example .env
docker compose up -d
.venv/bin/python src/seed.py
```

Run a strategy with `.venv/bin/python src/<example>.py`. Reset with:

```bash
docker compose down --volumes
rm -rf .venv
rm -f .env
```
