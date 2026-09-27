# First Implementation Prompt

Use this after choosing the deployment target described in the lesson.

```text
Read LESSON.md and the repository instructions. Build the first local slice of
Sanctuary Hotel, a fictional hotel's support assistant, using Python and Google ADK.
Use Agents CLI through the coding assistant where supported by the installed
version. Explain the generated code and check the commands before using them.

Start with the guest-guide lookup and one end-to-end chat turn. Store guide
sections and server-owned conversation state in PostgreSQL. Return source links
with answers and a clear fallback when no supporting information is found.
Use parameterized queries, bounded tool results, and server-only model access.

Use fictional data. Do not connect real guest records, deploy cloud resources,
or add booking or payment functionality in this local slice. Never put credentials
in browser code or source control.

Before coding, define acceptance criteria and verification commands. Provide
credential-free tests with model/tool fixtures, plus a separately documented
integration check for the real model. Test missing evidence, session isolation,
and a failed model request. Clearly distinguish fixtures from live responses.

Keep runnable files under code/. Document install, run, test, and reset commands
there. Update the repository verification manifest and run the required checks.
```
