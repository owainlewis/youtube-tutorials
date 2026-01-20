# /design

Create a technical design document for $ARGUMENTS.

Write a design doc that answers: What are we building? Why this approach? What trade-offs did we consider?

## Structure

### 1. Overview
One paragraph summary. What is this? Why are we building it?

### 2. Context
Background information. What exists today? What problem are we solving?

### 3. Goals and Non-Goals

**Goals:**
- What this project will accomplish

**Non-Goals:**
- What this project explicitly won't do (and why)

### 4. Proposed Solution
High-level approach. Include a system diagram if helpful.

### 5. Technical Design

**Data Model:**
Key entities and their relationships.

**API Design:**
Main endpoints or interfaces (if applicable).

**Key Components:**
Major modules and their responsibilities.

### 6. Alternatives Considered
Other approaches we evaluated and why we chose this one.

### 7. Dependencies and Risks
External dependencies. What could go wrong? Mitigation strategies.

### 8. Acceptance Criteria
How do we know this is done? What does success look like?

---

Output to: `workspace/designs/$ARGUMENTS.md`

Keep it concise (1-3 pages for small features, 5-10 for larger ones). Focus on decisions and trade-offs, not implementation details.
