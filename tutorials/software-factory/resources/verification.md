# Verified demo run

Verified on 16 September 2026 in the Personal Infrastructure project, `europe-west2`. All traffic was synthetic. No real payments or orders were created.

## Live behavior

- The private Cloud Run API accepted healthy checkout requests and returned HTTP 500 after the controlled bad revision.
- Cloud Monitoring opened incident `0.ocp2ihwwnmf8` at 11:32:04 UTC.
- Authenticated Pub/Sub push invoked the private ADK worker. The initial request completed at 11:32:35 UTC, approximately 30 seconds after invocation.
- The agent called all three evidence tools and recorded a report in Firestore.
- Live validation exposed a protobuf serialization bug in the log evidence. After the fix, the same real incident was retried on the deployed worker. The report cited `PriceLookupError: Checkout failed: price lookup returned None`, the failing revision and the successful replacement revision.
- A human-controlled recovery command deployed the healthy configuration. Subsequent checkout requests returned HTTP 200.
- Monitoring automatically closed the incident at 11:38:46 UTC. Its closed notification moved the dashboard record into recovered history. No manual incident closure was used.
- Dashboard rendering, refresh, evidence links and incident history were checked in the browser, including desktop and mobile layouts. No console errors were observed.

The first failure-to-alert delay was roughly six minutes. This includes metric ingestion and alert evaluation; it is separate from agent execution time. Timing varies and is not an SLA.

## Automated verification

- 36 focused tests cover request validation, fault behavior, incident lifecycle, duplicate delivery, retries, recovery ordering, active-record visibility, real protobuf log serialization, current retry windows, ownership collisions and paginated cleanup.
- `just check` verifies repository conventions and the offline tutorial suites.
- Independent review covered the complete implementation and follow-up fixes.
- The Assembler prompt was tailored using read-only GitHub inspection. It was not run in live mode; no Assembler labels, comments or merges were performed.
- Cleanup was tested with fake cloud boundaries. The live demo was deliberately retained for recording.

## Open the retained dashboard

The services require authentication. Run:

```bash
gcloud run services proxy software-factory-dashboard --project personal-infrastructure-505708 --region europe-west2 --port 8781
```

Then open http://localhost:8781. Stop the proxy with Ctrl-C when finished. The lesson uses port 8769 as an example; either works when available.
