---
name: research
description: "Research video ideas for a topic and add them to the Airtable content pipeline."
---

# Research Skill

Generate video ideas for a given topic and push them into Airtable.

## Airtable Configuration

Update these with your own base and table IDs:

- Base: [Your Base Name] ([your-base-id])
- Table: [Your Table Name] ([your-table-id])

## Process

1. Research the given topic using web search to understand the current landscape
2. Identify gaps — what questions are unanswered, what demos are missing
3. Generate 10 video ideas with titles optimized for YouTube (6-8 words, under 50 characters)
4. Assign each idea to the most relevant content category
5. Use the Airtable MCP to create records in the table
6. Set Status to "Idea" for all new records
7. Use typecast: true when creating records so select values are matched by name
8. Return a summary table of what was added

## Title Guidelines

- 6-8 words, under 50 characters
- Sentence case (capitalize first word and proper nouns only)
- Simple words a child could read aloud
- One subject per title
- "How I" is stronger than "How to"
- Parenthetical kickers add a second hook: (+ my setup), (honest take), (from scratch)
