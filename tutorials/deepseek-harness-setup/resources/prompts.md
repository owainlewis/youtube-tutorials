# Build a DS Kanban plugin for the DeepSeek Harness

Build a web client plugin for the DeepSeek Harness that shows a kanban board of
**delegated work across every project**. The harness sidebar groups sessions by
folder and hides subagent-origin sessions entirely, so when a coordinator session
fans out to worker sessions you cannot see what those workers are doing. This
plugin is the view that fixes that.

## Package scaffolding

Create `dsh-client-ui-ds-kanban` with `lib/index.js` (host half) and
`lib/client.js` (browser half).

`package.json`:
```json
{
  "name": "dsh-client-ui-ds-kanban",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "main": "lib/index.js",
  "exports": {
    ".": "./lib/index.js",
    "./client": "./lib/client.js",
    "./package.json": "./package.json"
  },
  "dsh": {
    "client": {
      "inject": ["@deepseek-ai/dsh-client-locale", "@deepseek-ai/dsh-client-runtime"],
      "platform": "web"
    }
  },
  "peerDependencies": { "react": "^18.2.0" }
}
```

`lib/index.js` is deliberately empty. It exists so the plugin appears as a host
loader entry; the browser half ships via `exports["./client"]`:
```js
function apply() {}
export { apply };
```

`lib/client.js` uses the module-loader wrapper (CommonJS-style inside):
```js
window.__ModuleLoader__.load({
  id: "dsh-client-ui-ds-kanban",
  factory: (require) => {
    var module = { exports: {} };
    var exports = module.exports;
    Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
    let React = require("react");
    /* ... */
    exports.apply = apply;
    exports.inject = inject;
    return module.exports;
  }
});
```

Install into the web profile: add `"dsh-client-ui-ds-kanban": "file:<path>"` to
`~/.dsh/profiles/web/package.json` dependencies, and append to
`~/.dsh/profiles/web/cordis.patch.yml`:
```yaml
- insert:
    - id: ds-kanban
      name: dsh-client-ui-ds-kanban
```

## Traps that will cost you hours. Get these right first

1. **`exports.inject` is an ARRAY of service names, not a function.** Exporting
   `function inject(ctx) {}` fails at load with
   `cannot get property "slots" without inject`. Correct:
   `const inject = ["slots", "locale", "sessions", "workspaces"];`

2. **The session summary field is `id`, not `sessionId`.** Using `sessionId`
   silently yields undefined everywhere (blank React keys, `open(undefined)`).

3. **`updatedAt` is NOT an activity signal.** It advances only on `user/message`
   frames whose `source.kind === "user"`, meaning when *you* type. For a worker you
   never message directly it is effectively creation time. Never use it for
   "last active" or "running for N minutes". Use `subagentTiming` (below), and
   track blocked-duration yourself.

4. **Blank sessions must be filtered by the consumer.** The store carries one
   provisional blank ("New Session") row per workspace and leaves filtering to
   each view; the sidebar shows only the selected one. An unfiltered board grows
   a phantom card per empty project. Drop every `blank === true` batch that has
   no workers.

5. **Subagent sessions ARE in `list.byId` and `list.ids`.** The sidebar hides
   them with `origin !== "subagent"`. Do not skip `parentId` rows. That data is
   the entire point of this plugin.

6. **Worker titles are garbage.** The `title` projection for a delegated session
   is the opening words of its prompt ("You are a fresh, independent..."). The
   real name is `projectionValues.subagent.identity.label`
   (e.g. "Review internal/runner package"). Use it whenever `origin === "subagent"`.

7. **The theme token is `--dsw-alias-state-warn-primary`**, not `...-warning-...`.
   A wrong name silently falls back to your hardcoded literal and breaks dark mode.

8. **Do not build layering on `--dsw-alias-bg-module-platform`.** It is recessed
   against the page in light mode but elevated in dark, so any surface using it
   inverts between themes.

## Services and data

Declared via `inject`, reached as `ctx.<name>`:

- `ctx.sessions.list`: `ObservableSnapshot` with `getSnapshot()` / `subscribe(fn)`.
  Snapshot: `{ ids, byId, current, phase, subagentsByParent, jobsBySession }`.
- `ctx.sessions.open(id)`, `ctx.sessions.openSubagent(address)`,
  `ctx.sessions.subagentAddress(id)`.
- `ctx.workspaces.list`: snapshot `{ items, archivedSessionIds, ... }`;
  `WorkspaceView` = `{ workspaceId, title, path, createdAt, sessionIds }`.
- `ctx.locale.register(ns, { zh, en })`, `ctx.slots`, `ctx.effect(fn, label)`.

`SessionSummary`: `id`, `displayTitle`, `title?`, `cwd?`, `parentId?`,
`origin?: 'subagent'`, `running`, `pendingInteraction?: 'approval'|'plan-review'|'question'`,
`completed?`, `blank`, `updatedAt`, `projectionValues?`.

`projectionValues` carries live host projections (verify each is present; degrade
to hiding the field rather than showing a confident zero):
```
subagent        { identity: { label, mode, seq } }
subagentTiming  { settledMs, active?: { since, through } }
tokenUsage      { totals: { uncachedInputTokens, outputTokens, cacheReadTokens, cacheWriteTokens } }
contextPressure { pressureTokens, surfaceTokens, contextWindow }
sessionStats    { turns, steps, llmMs, toolMs, openStep, pendingCalls }
```

Active duration (the sanctioned derivation, same as `dsh-client-ui-subagent`):
```js
timing.active == null
  ? timing.settledMs
  : timing.settledMs + Math.max(0, (running ? now : timing.active.through) - timing.active.since)
```

## Derived model: the batch

The unit is a **batch**, not a session: one coordinator plus every session it
delegated to, on one card.

- Bucket each `origin === "subagent"` summary under its **root** ancestor by
  walking `parentId` until a non-subagent session. Guard the walk with a `seen`
  set (cycles must fail soft) and, if a parent summary is missing, let the worker
  stand alone rather than vanish into an unrenderable key.
- Per-session state: `pendingInteraction != null` → `blocked` (it outranks
  `running`: a session on an approval is stalled, not working); else `running`;
  else `completed` → `done`; else `idle`.
- **Batch state = the worst state among the coordinator and all its workers.**
  One blocked worker stalls the whole batch, and you are what it is stalled on.
  An archived coordinator overrides everything.
- Track two things the session list cannot report, in a plugin-scope subscriber
  so history accrues whether or not the board is open: when a session *became*
  blocked, and when its summary object last changed identity (the runtime dedupes
  summaries, so a changed identity is a genuine activity heartbeat).

## UI

Register into the `sidebar.footer.action` slot (`kind: "list"`, `scope: "root"`):
```js
ctx.slots.inject("sidebar.footer.action", () => ctx.slots.register({
  name: "sidebar.footer.action", id: "ds-kanban", locale: "<ns>"
}, Component));
```
The entry renders a sidebar button (with a red count of batches needing you) that
opens a full-screen `role="dialog"` overlay, closable with Escape.

Overlay contents, top to bottom:

1. **Title row**: "DS Kanban" + Close.
2. **Stat strip**: `waiting on you` (red when > 0), `running now`,
   `near context limit` (only rendered when > 0), `batches`, `delegating`,
   `sessions`, `agent time`, `tokens`. Zero values drop to tertiary colour so
   non-zero ones read first. Cells whose projection is absent disappear entirely.
   Label the duration "agent time", never "elapsed". Summing per-session time
   across parallel workers is not wall clock.
3. **Filter chips**, one per state, always showing the true total even when that
   state is switched off. Defaults: Blocked, Running, Done on; Idle, Archived off.
   Plus a "Group by project" toggle that shows a ✓ when active.
4. **Board**: columns are the enabled states in the order
   `Blocked → Running → Done → Idle → Archived`. Blocked leads because this is a
   triage surface and the left edge is where the eye lands; with the default
   filters this reads as a conventional Blocked/Running/Done board ending in Done.
   With grouping on, each project is a swimlane with a header and per-state tally,
   lanes ranked so the project holding the most urgent work leads.
5. **Footer**: "N of M batches shown" and a legend prefixed "workers".

**Columns must be full height** (`alignItems: stretch`, and `height: 100%` when
ungrouped), but an **empty column shrinks** to `minmax(96px, .32fr)` while a
populated one takes `minmax(210px, 1fr)`. Judge emptiness across all lanes so
every swimlane shares one template and columns stay aligned. Empty columns still
render, centred and muted. "Nothing is blocked" is information.

**Card**: left border stripe in the state colour (neutral for quiet states),
disclosure chevron with a permanent gutter so titles align even on cards with no
workers, title, project chip (only when not grouped), blocked/tool line, a row of
clickable worker dots with a `done/total` ratio, a metrics line
(`active · steps · tok`, `nowrap` with ellipsis and full text on hover), and a
context-fill bar. Expanding shows one row per worker with its real label, state,
active time, context bar and tokens. Clicking any dot or row opens that session.
Prefer `subagentAddress(id)` → `openSubagent(address)`, falling back to `open(id)`.
Archived cards render at 60% opacity.

## Design system. Match the harness, do not invent

Read these from `@deepseek-ai/dsh-client-ui-theme/lib/styles/design-platform.css`
and the shipped `*/lib/client.js` bundles rather than guessing.

- Dark mode is `body[data-ds-dark-theme]` swapping token values wholesale, so
  **referencing a token IS the dark-mode support**. Every colour must come from a
  `var(--dsw-alias-*)`; no raw hex outside a `var()` fallback.
- Surfaces: page `bg-base`, column `bg-layer-1`, card `bg-layer-3` + `border-l2`
  + 12px radius. In light mode these are all white and borders carry the
  separation; in dark they are distinct greys.
- Type scale, always size paired with a pixel line-height: **11/16, 12/18, 13/20,
  18/28**. **Weight 500 for nearly everything**; 600 only on headings 15px+.
  Emphasis comes from colour, never from heavier weight. No letter-spacing, no
  uppercase.
- Radii 8 (rows) / 12 (cards, columns) / 999 (pills). Gaps and padding on the
  2/4/6/8/10/12 grid; rows `6px 8px`, cards `10px 12px`, pills `2px 8px`.
- Shadows `var(--dsw-shadow-lv1)`, lifting to `lv2` on card hover. Never animate
  `borderColor` on the card. It repaints all four sides and erases the state stripe.
- Transitions `.16s var(--ds-ease-in-out)`.
- Set `--dsh-scrollbar-thumb` / `--dsh-scrollbar-thumb-hover` on every scroll
  container, as the harness cards do.
- `font-family: var(--dsw-font-family)`.

## Acceptance checks

- `exports.inject` is an array; the plugin loads with no loader error.
- Every `var(--...)` name referenced exists in the theme stylesheet, and every
  alias token is defined in both the light and dark blocks.
- No raw colour outside a `var()` fallback; every `fontSize` paired with a
  `lineHeight`; weights limited to 500 and 600.
- A depth-3 delegation chain folds into one batch with 3 workers.
- An orphaned worker (missing parent summary) still appears; a lineage cycle
  terminates.
- Absent and malformed `projectionValues` render without throwing, hiding the
  affected fields.
- Three empty projects produce zero cards and zero lanes, and do not inflate the
  session count.
- Empty columns shrink; every swimlane receives an identical column template.
