# PostgreSQL RAG sample

The complete setup and explanation live in [../LESSON.md](../LESSON.md).

From this directory, run the credential-free check with:

```bash
python3 verify_offline.py
```

Run the optional Docker database check with:

```bash
./verify_database.sh
```

The database check starts the local Compose service and verifies the extension, table, indexes, SQL function, and seed rows. It does not call OpenAI.
