# Voice Example (Fictional — Replace Before Production Use)

> **This file is the few-shot example the AI generator uses to match your firm's voice.**
>
> The proposal below is fictional. The client, project, and pricing are made up.
>
> Before shipping, replace this file with one of your own past proposals (anonymised if needed). The AI copies the cadence, structure, and tone of whatever's in this file. Garbage in, garbage out.

---

[Your Firm]
Customer Insights Platform
Fixed-Scope Build — Feedback Aggregation System

**Prepared for:** Nightingale Software (fictional)
**Prepared by:** [Your Name], [Your Firm]
**Date:** [Date]
**Version:** 1.0
**Classification:** Confidential

## Situation Appraisal

Nightingale Software's growth has come from a strong product and an active customer base. The challenge is that customer feedback is now arriving across too many channels for any one person to track. Support tickets, sales notes, NPS surveys, in-app feedback, and inbound emails all contain useful signal, but the signal is being lost because nobody has time to read it all.

This project delivers a customer insights platform that pulls feedback from each source, classifies and clusters it, and surfaces themes weekly. You stop missing signal. The product team gets a clean view of what customers are actually saying.

## What's at Stake

A growing SaaS business that doesn't read its own customer feedback eventually ships features customers don't want and misses ones they're asking for. Nightingale already has the channels in place. What's missing is the layer that turns raw feedback into something the team can act on. Every week without it is a week of insight being lost.

## Current Challenges

- **Feedback is scattered across five channels with no central view.** Support reads tickets, sales reads sales notes, product reads NPS. Nobody reads everything.
- **Cross-channel themes are invisible.** Issues that appear in three places at once don't get spotted because no one cross-references the channels.
- **Manual triage is the first thing to slip when busy.** Reading and tagging feedback by hand takes hours per week and stops happening when the team is under pressure.
- **No record of what feedback led to what decision.** Product decisions are made without a clear trail back to the customer voice that prompted them.
- **No searchable archive.** Past feedback is functionally unsearchable because it lives in five different tools.

## Objectives

- Pull feedback from all five sources into a single store on a regular schedule
- Classify and cluster feedback automatically so themes surface without manual review
- Generate a weekly report showing top themes, sentiment, and recommended actions
- Make every piece of feedback searchable across the team
- Run reliably with minimal ongoing intervention

## Scope

### What We're Building

A hosted customer insights platform that aggregates feedback from five sources, classifies and clusters it with AI, and produces a weekly report. The team gets a clean dashboard showing what customers are saying right now, plus a searchable archive of every piece of feedback.

- **Multi-source ingestion** — Zendesk, Salesforce, NPS surveys, in-app feedback, and inbound email, refreshed every six hours
- **AI classification** — every piece of feedback gets a category, sentiment score, and theme
- **Weekly themes report** — top themes, frequency, sentiment trends, recommended actions
- **Searchable archive** — full-text search across all feedback, filterable by source, sentiment, theme, date
- **Action item tracking** — themes can be marked as "noted," "in progress," or "shipped"
- **Slack integration** — weekly reports posted to a configurable channel

### How It Works

1. The pipeline runs every six hours, pulling new feedback from each source
2. New items are deduplicated and stored in Postgres
3. AI classifies each item (category, sentiment, theme)
4. Items are clustered into themes weekly
5. A weekly report is generated and posted to Slack
6. The team reviews the dashboard, marks themes for action, and tracks progress over time

## Technical Approach

The system is a Python backend with a web frontend, connected to a Postgres database. Scheduled jobs handle ingestion, classification, and report generation. The interface is built for the product team, not engineers.

| Component | Technology |
|---|---|
| Ingestion | Python scheduled jobs, source-specific adapters |
| Classification | Vertex AI Gemini |
| Storage | PostgreSQL |
| Frontend | Next.js dashboard |
| Reports | Markdown to Slack via webhook |
| Hosting | Cloud Run + Cloud SQL on Google Cloud |

## Delivery Plan

### Week 1 — Ingestion and Classification

- Build adapters for the five feedback sources
- Set up scheduled ingestion every six hours
- Build the classification pipeline (category, sentiment, theme)
- Set up Postgres schema and deduplication

### Week 2 — Dashboard and Reports

- Build the web dashboard (themes view, archive, search)
- Build the weekly report generator
- Wire Slack integration
- Deploy, test end to end, handover

## Deliverables

- Working customer insights platform deployed on a live domain, accessible from any device
- Five working source adapters running on a regular schedule
- AI classification pipeline running automatically on all new feedback
- Web dashboard with themes, archive, and search
- Weekly Slack reports posted to a configurable channel
- Documented codebase in a private Git repository transferred on completion
- Setup guide and handover walkthrough

## Explicit Exclusions

- **Outbound responses.** The system surfaces feedback. It does not reply to customers.
- **Custom sentiment training.** Uses the model's built-in classifier, not a fine-tune on Nightingale's data.
- **Salesforce write-back.** Feedback is read from Salesforce. Nothing is written back.
- **Mobile app.** The dashboard is responsive on mobile browsers but is not a native app.
- **Custom analytics dashboards beyond the core themes view.**

## Success Criteria

- The team can see, in under a minute, what customers are talking about this week
- All five feedback channels are ingested without manual intervention
- Themes appearing across multiple channels are visible and ranked
- Weekly reports arrive in Slack reliably
- The product team uses it instead of reading individual channels

## Joined Accountability

### Nightingale Will:

- Provide API access for each of the five feedback sources
- Be available for a check-in at the end of Week 1 to validate classification quality
- Provide feedback on the first weekly report

### [Your Firm] Will:

- Deliver a working system within the two-week timeline
- Keep all data confidential
- Produce a clean, handover-ready codebase with no dependencies on [Your Firm] infrastructure
- Flag scope risks as soon as identified
- Provide a walkthrough on completion

## Investment

| | |
|---|---|
| Two weeks development | £6,000 |
| **Total (excl. VAT)** | **£6,000** |

Includes: full system build, deployment, hosting setup, documentation, handover walkthrough.

Fixed price. Fixed scope. No hourly billing, no scope creep.

## Payment Terms

- 50% on acceptance of this proposal: £3,000
- 50% on completion and handover: £3,000

## Timeline

Two weeks from agreed start date. Two rounds of feedback included during the build.

## Monthly Running Costs

No monthly fees for the first six months. After six months, running costs are reviewed based on actual usage. Current estimate is under £30/month covering hosting, AI tokens, and operational costs.

Any work beyond the scope above will be quoted and agreed in writing before proceeding.

## Next Steps

1. Review this proposal and confirm the scope looks right
2. Reply to confirm you are happy to proceed
3. Agree a start date
4. Invoice issued for the 50% deposit
5. Build begins

---

[Your Name]
[Email]
[Your Firm]
