# Add Project Description Field

## Why
Users need to add context about their projects beyond just the title.

## What
Nullable description field on Projects, editable in detail view, shown on cards.

## Context
- `prisma/schema.prisma` — Project model
- `src/app/projects/[id]/ProjectDetail.tsx` — auto-save pattern for title
- `src/components/projects/ProjectCard.tsx` — card layout

## Constraints
**Must not:** Add rich text editing (plain textarea only)

## Tasks

### T1: Schema + Types + API
**Do:** Add `description String?` to Project model, update TS types, include in PATCH route (also fix: `whyWatch`/`whatTheyLearn` aren't being saved)
**Files:** `prisma/schema.prisma`, `src/types/index.ts`, `src/app/api/projects/[id]/route.ts`
**Verify:** `bunx prisma migrate dev && bun run build`

### T2: UI
**Do:** Add description textarea to Details tab (auto-save on blur), show truncated on ProjectCard
**Files:** `src/app/projects/[id]/ProjectDetail.tsx`, `src/components/projects/ProjectCard.tsx`
**Verify:** Manual: Create project → add description → refresh → verify persists → check card shows it

## Done
- [ ] `bun run build` passes
- [ ] Description survives page refresh
- [ ] Card shows truncated description
