window.__ModuleLoader__.load({
	id: "dsh-client-ui-ds-kanban",
	factory: (require) => {
		var module = { exports: {} };
		var exports = module.exports;
		Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
		let React = require("react");
		//#region DS Kanban - delegated work across all projects
		/**
		* Theme tokens, every name verified against ui-theme's design-platform.css.
		* The harness defines all of these on `body` and swaps them wholesale under
		* `body[data-ds-dark-theme]`, so referencing the token IS the dark-mode
		* support; the literal fallbacks are a safety net that should never fire.
		*
		* Surfaces copy the recipe the harness already uses for its own cards
		* (`border-l2` + `bg-layer-3` + 12px radius) and rows (`8px` radius,
		* `interactive-bg-hover` on hover), so this view sits inside the existing
		* visual language rather than beside it.
		*
		* Elevation is deliberate. In light mode base/layer-1/layer-3 are all white
		* and separation comes from BORDERS; in dark mode they are distinct greys and
		* separation comes from FILLS. `bg-module-platform` is not used: it is
		* recessed against the page in light but elevated in dark, so any surface
		* built on it inverts between themes. Columns sit on `bg-layer-1` and cards on
		* `bg-layer-3`, which keeps the card above its column in dark mode and lets
		* borders carry the separation in light, where both resolve to white.
		*/
		const TOK = {
			bgBase: "var(--dsw-alias-bg-base, #ffffff)",
			bgCol: "var(--dsw-alias-bg-layer-1, #ffffff)",
			bgCard: "var(--dsw-alias-bg-layer-3, #ffffff)",
			bgInset: "var(--dsw-alias-interactive-bg-hover, rgba(38,49,72,.06))",
			label: "var(--dsw-alias-label-primary, #0b1220)",
			label2: "var(--dsw-alias-label-secondary, #46536b)",
			label3: "var(--dsw-alias-label-tertiary, #6b7891)",
			dim: "var(--dsw-alias-label-dimmed, #c3cbd8)",
			hair: "var(--dsw-alias-border-l1, rgba(0,0,0,.04))",
			border: "var(--dsw-alias-border-l2, rgba(0,0,0,.1))",
			border3: "var(--dsw-alias-border-l3, rgba(0,0,0,.12))",
			accent: "var(--dsw-alias-state-business-primary, #4d6bfe)",
			error: "var(--dsw-alias-state-error-primary, #dc2626)",
			warn: "var(--dsw-alias-state-warn-primary, #f59e0b)",
			ok: "var(--dsw-alias-state-success-primary, #22c55e)",
			shadow: "var(--dsw-shadow-lv1, 0 2px 4px 0 rgba(0,0,0,.05))",
			shadow2: "var(--dsw-shadow-lv2, 0 4px 12px 0 rgba(0,0,0,.02), 0 2px 8px 0 rgba(0,0,0,.04))",
			ease: ".16s var(--ds-ease-in-out, cubic-bezier(.4,0,.2,1))"
		};
		const STATE_COLOR = { blocked: TOK.error, running: TOK.accent, done: TOK.ok, idle: TOK.border3, archived: TOK.border3 };
		/** Live states earn a coloured card stripe; quiet ones stay neutral. */
		const LIVE_STATE = { blocked: true, running: true, done: true };
		const STATE_TEXT = { blocked: "waiting on you", running: "running", done: "finished", idle: "idle", archived: "archived" };
		/** Triage order: the top row is always the thing to act on. */
		/**
		* Column order, left to right. Blocked leads because this is a triage board
		* and the left edge is where the eye lands first. The three live states then
		* end at Done, so with the default filters the board reads as a conventional
		* Blocked -> Running -> Done kanban; the two quiet states are off by default
		* and append to the right when asked for.
		*/
		const STATE_RANK = { blocked: 0, running: 1, done: 2, idle: 3, archived: 4 };
		/** Filter chip order, and the short words used on chips and project tallies. */
		const FILTER_ORDER = ["blocked", "running", "done", "idle", "archived"];
		const STATE_LABEL = { blocked: "Blocked", running: "Running", done: "Done", idle: "Idle", archived: "Archived" };
		/**
		* The harness type scale, taken from the shipped components: each size is
		* paired with a fixed pixel line-height (11/16, 12/18, 13/20, 18/28) and
		* weight 500 does nearly all the work - 600 appears only on headings at
		* 15px and above. Emphasis is carried by COLOUR, not by heavier weight,
		* which is why nothing here goes to 700.
		*/
		const T11 = { fontSize: "11px", lineHeight: "16px" };
		const T12 = { fontSize: "12px", lineHeight: "18px" };
		const T13 = { fontSize: "13px", lineHeight: "20px" };
		const FONT = "var(--dsw-font-family, inherit)";
		/** Scrollbars in the harness are themed through these per-container vars. */
		const SCROLL = {
			"--dsh-scrollbar-thumb": "var(--dsw-alias-scrollbar-bg-l2)",
			"--dsh-scrollbar-thumb-hover": "var(--dsw-alias-scrollbar-hover-l2)"
		};
		/** Context-fill thresholds, shared by the card bars and the header stats. */
		const PRESSURE_WARN = .65;
		const PRESSURE_HIGH = .85;
		/** `pendingInteraction` outranks `running`: a session on an approval is stalled, not working. */
		function stateOf(s) {
			if (s == null) return "idle";
			if (s.pendingInteraction != null) return "blocked";
			if (s.running === true) return "running";
			if (s.completed === true) return "done";
			return "idle";
		}
		//#endregion
		//#region Projection readers - every one degrades to undefined when absent
		// `subagentTiming` and `tokenUsage` are known to ride list rows (ui-subagent
		// reads them there). `sessionStats`, `contextPressure` and `subagent` live in
		// the same open `values` record and are very likely present, but nothing here
		// depends on them: a missing projection hides its field and nothing else.
		function proj(s) { return (s && s.projectionValues) || {}; }
		/**
		* Active working time. NOT `updatedAt`, which advances only on user/message
		* frames whose source is the user - for a worker you never message directly
		* that stamp is effectively its creation time.
		*/
		function activeMs(s, now) {
			const t = proj(s).subagentTiming;
			if (t == null || typeof t.settledMs !== "number") return undefined;
			if (t.active == null) return t.settledMs;
			const since = typeof t.active.since === "number" ? t.active.since : undefined;
			if (since === undefined) return t.settledMs;
			const end = s.running === true ? now : (typeof t.active.through === "number" ? t.active.through : now);
			return t.settledMs + Math.max(0, end - since);
		}
		function tokensOf(s) {
			const u = proj(s).tokenUsage;
			const t = u == null ? undefined : (u.totals || u);
			if (t == null) return undefined;
			const n = (t.uncachedInputTokens || 0) + (t.outputTokens || 0) + (t.cacheReadTokens || 0) + (t.cacheWriteTokens || 0);
			return n > 0 ? n : undefined;
		}
		function stepsOf(s) {
			const st = proj(s).sessionStats;
			return st != null && typeof st.steps === "number" ? st.steps : undefined;
		}
		/** Context fill as 0..1, so a worker about to degrade is visible before it does. */
		function pressureOf(s) {
			const c = proj(s).contextPressure;
			if (c == null || !c.contextWindow) return undefined;
			const used = typeof c.pressureTokens === "number" ? c.pressureTokens : c.surfaceTokens;
			if (typeof used !== "number") return undefined;
			return Math.max(0, Math.min(1, used / c.contextWindow));
		}
		/** Which tool is in flight right now: separates "thinking" from "wedged on a long build". */
		function pendingToolOf(s) {
			const st = proj(s).sessionStats;
			const calls = st == null ? undefined : st.pendingCalls;
			if (calls == null || typeof calls !== "object") return undefined;
			const vals = Object.values(calls);
			if (vals.length === 0) return undefined;
			for (const v of vals) {
				if (typeof v === "string" && v) return v;
				if (v && typeof v === "object") {
					const n = v.name || v.tool || v.toolName;
					if (n) return n;
				}
			}
			return "tool running";
		}
		/**
		* A worker's real task name. The `title` projection for a delegated session is
		* the opening words of its prompt ("You are a fresh, independent..."), so the
		* subagent descriptor is the only human-readable label available.
		*/
		function labelOf(s) {
			if (s == null) return "";
			if (s.origin === "subagent") {
				const d = proj(s).subagent;
				const l = d && d.identity && d.identity.label;
				if (l) return l;
			}
			if (s.blank === true) return "New Session";
			if (s.displayTitle) return s.displayTitle;
			if (s.title) return s.title;
			return s.id ? s.id.slice(0, 12) : "";
		}
		function projectOf(s, titleBySession) {
			const named = titleBySession.get(s.id);
			if (named) return named;
			if (!s.cwd) return "";
			const parts = s.cwd.split(/[\\/]/).filter(Boolean);
			return parts.length ? parts[parts.length - 1] : s.cwd;
		}
		//#endregion
		//#region Formatting
		function fmtTokens(n) {
			if (n == null) return "";
			if (n < 1e3) return String(n);
			if (n < 1e6) return (n / 1e3 >= 100 ? Math.round(n / 1e3) : Math.round(n / 100) / 10) + "K";
			return (n / 1e6 >= 100 ? Math.round(n / 1e6) : Math.round(n / 1e5) / 10) + "M";
		}
		function fmtMs(ms) {
			if (ms == null) return "";
			const sec = Math.floor(ms / 1000);
			if (sec < 60) return sec + "s";
			if (sec < 3600) return (Math.round(sec / 6) / 10) + "m";
			if (sec < 86400) return (Math.round(sec / 360) / 10) + "h";
			return Math.floor(sec / 86400) + "d";
		}
		function fmtAgo(at, now) {
			if (!at) return "";
			const sec = Math.max(0, Math.floor((now - at) / 1000));
			if (sec < 60) return sec + "s";
			if (sec < 3600) return Math.floor(sec / 60) + "m";
			if (sec < 86400) return Math.floor(sec / 3600) + "h";
			return Math.floor(sec / 86400) + "d";
		}
		//#endregion
		/**
		* Walk delegation lineage to the batch the user actually started. A broken
		* chain leaves the worker standing alone rather than vanishing.
		*/
		function rootOf(summary, byId) {
			let cur = summary;
			const seen = new Set();
			while (cur.origin === "subagent" && cur.parentId != null && !seen.has(cur.id)) {
				seen.add(cur.id);
				const parent = byId[cur.parentId];
				if (parent == null) return cur.id;
				cur = parent;
			}
			return cur.id;
		}
		/**
		* Records what the session list itself cannot report: when a session BECAME
		* blocked, and when it last changed at all. The runtime dedupes summary
		* objects, so a changed identity is a real activity heartbeat. Runs at plugin
		* scope so the history accrues whether or not the board is on screen.
		*/
		function createActivityTracker(sessions) {
			const state = new Map();
			let prev = {};
			const sync = () => {
				const byId = sessions.list.getSnapshot().byId || {};
				const now = Date.now();
				for (const id of Object.keys(byId)) {
					const s = byId[id];
					let rec = state.get(id);
					if (rec === undefined) {
						rec = { blockedSince: undefined, lastChangeAt: now };
						state.set(id, rec);
					} else if (prev[id] !== undefined && prev[id] !== s) rec.lastChangeAt = now;
					if (s.pendingInteraction != null) { if (rec.blockedSince === undefined) rec.blockedSince = now; }
					else rec.blockedSince = undefined;
				}
				for (const id of Array.from(state.keys())) if (byId[id] === undefined) state.delete(id);
				prev = byId;
			};
			sync();
			return { sync, get: (id) => state.get(id) };
		}
		/** Required services: slot contribution, dictionaries, and the two list feeds. */
		const inject = [
			"slots",
			"locale",
			"sessions",
			"workspaces"
		];
		/**
		* Browser half of DS Kanban. One sidebar-footer entry opening a triage list
		* of delegated work across ALL projects.
		*
		* The unit is the BATCH: one coordinator plus every session it delegated to,
		* on one row. That is what the workspace sidebar cannot give - it groups by
		* folder and hides subagent-origin rows entirely, surfacing only a
		* running-descendant count, so a worker blocked on an approval is invisible.
		* Rows are ranked rather than columned: status is a 3-way flag a colour
		* already carries, so the width goes to work data instead.
		*/
		function apply(ctx) {
			const sessions = ctx.sessions;
			const workspaces = ctx.workspaces;
			const activity = createActivityTracker(sessions);
			ctx.effect(() => sessions.list.subscribe(activity.sync), "ds-kanban: activity tracking");
			ctx.effect(() => ctx.locale.register("mission-control", {
				zh: { "view.missionControl": "DS 看板" },
				en: { "view.missionControl": "DS Kanban" }
			}), "ds-kanban: dictionaries");
			function DsKanbanAction() {
				const [open, setOpen] = React.useState(false);
				const [snap, setSnap] = React.useState(readSnapshot);
				const [now, setNow] = React.useState(() => Date.now());
				const [states, setStates] = React.useState({ blocked: true, running: true, done: true, idle: false, archived: false });
				const [grouped, setGrouped] = React.useState(true);
				const [override, setOverride] = React.useState({});
				React.useEffect(() => {
					const onChange = () => { activity.sync(); setSnap(readSnapshot()); };
					const unsubs = [sessions.list.subscribe(onChange), workspaces.list.subscribe(onChange)];
					return () => { for (const fn of unsubs) fn(); };
				}, []);
				React.useEffect(() => {
					if (!open) return;
					const onKey = (e) => { if (e.key === "Escape") setOpen(false); };
					document.addEventListener("keydown", onKey);
					return () => document.removeEventListener("keydown", onKey);
				}, [open]);
				React.useEffect(() => {
					if (!open) return;
					setNow(Date.now());
					const tick = setInterval(() => setNow(Date.now()), 15000);
					return () => clearInterval(tick);
				}, [open]);
				function readSnapshot() {
					const byId = sessions.list.getSnapshot().byId || {};
					const ws = workspaces.list.getSnapshot();
					const archivedSet = new Set(ws.archivedSessionIds || []);
					const titleBySession = new Map();
					for (const w of ws.items || []) {
						for (const sid of w.sessionIds || []) titleBySession.set(sid, w.title);
					}
					const batches = new Map();
					const ensure = (s) => {
						let b = batches.get(s.id);
						if (b == null) { b = { coordinator: s, workers: [] }; batches.set(s.id, b); }
						return b;
					};
					const all = Object.values(byId);
					for (const s of all) if (s.origin !== "subagent") ensure(s);
					for (const s of all) {
						if (s.origin !== "subagent") continue;
						const root = byId[rootOf(s, byId)];
						const b = root != null && root.origin !== "subagent" ? ensure(root) : ensure(s);
						if (b.coordinator.id === s.id) continue;
						b.workers.push({ summary: s, state: stateOf(s) });
					}
					const rows = [];
					let sessionCount = 0;
					for (const b of batches.values()) {
						// A blank session has an empty log: it is the per-workspace provisional
						// "New Session" row, and the store carries one for EVERY workspace,
						// leaving the filtering to each consumer. An unfiltered board grows a
						// phantom card per empty project. None of them are work, so none of
						// them belong here - only a blank that has somehow already delegated
						// stays, so its workers are never orphaned.
						if (b.coordinator.blank === true && b.workers.length === 0) continue;
						sessionCount += 1 + b.workers.length;
						b.workers.sort((x, y) => (STATE_RANK[x.state] - STATE_RANK[y.state]) || labelOf(x.summary).localeCompare(labelOf(y.summary)));
						b.coordinatorState = stateOf(b.coordinator);
						b.blockedCount = (b.coordinatorState === "blocked" ? 1 : 0) + b.workers.filter((w) => w.state === "blocked").length;
						b.doneCount = b.workers.filter((w) => w.state === "done").length;
						// The batch inherits its worst member: one blocked worker stalls the
						// whole batch, and you are the thing it is stalled on.
						let worst = b.coordinatorState;
						for (const w of b.workers) if (STATE_RANK[w.state] < STATE_RANK[worst]) worst = w.state;
						if (archivedSet.has(b.coordinator.id)) b.state = "archived";
						else b.state = worst;
						const stamps = [b.coordinator].concat(b.workers.map((w) => w.summary))
							.map((s) => { const r = activity.get(s.id); return r && r.blockedSince; })
							.filter((v) => v != null);
						b.blockedSince = stamps.length ? Math.min.apply(null, stamps) : undefined;
						const changes = [b.coordinator].concat(b.workers.map((w) => w.summary))
							.map((s) => { const r = activity.get(s.id); return r ? r.lastChangeAt : 0; });
						b.lastChangeAt = changes.length ? Math.max.apply(null, changes) : 0;
						b.project = projectOf(b.coordinator, titleBySession) || "No project";
						rows.push(b);
					}
					rows.sort((a, b) => {
						const d = STATE_RANK[a.state] - STATE_RANK[b.state];
						if (d !== 0) return d;
						if (a.state === "blocked") return (a.blockedSince || 0) - (b.blockedSince || 0);
						return b.lastChangeAt - a.lastChangeAt;
					});
					const counts = {};
					for (const r of rows) counts[r.state] = (counts[r.state] || 0) + 1;
					// Project sections ranked the way rows are: whichever project holds the
					// most urgent work leads, so the top of the page stays actionable.
					const byProject = new Map();
					for (const r of rows) {
						let g = byProject.get(r.project);
						if (g == null) { g = { project: r.project, rows: [], counts: {}, lastChangeAt: 0 }; byProject.set(r.project, g); }
						g.rows.push(r);
						g.counts[r.state] = (g.counts[r.state] || 0) + 1;
						if (r.lastChangeAt > g.lastChangeAt) g.lastChangeAt = r.lastChangeAt;
					}
					const groups = Array.from(byProject.values()).sort((a, b) => {
						const ra = Math.min.apply(null, a.rows.map((r) => STATE_RANK[r.state]));
						const rb = Math.min.apply(null, b.rows.map((r) => STATE_RANK[r.state]));
						return (ra - rb) || (b.lastChangeAt - a.lastChangeAt);
					});
					const delegated = rows.filter((r) => r.workers.length > 0).length;
					return { rows, groups, counts, sessionCount, batchCount: rows.length, delegated, titleBySession, attention: counts.blocked || 0 };
				}
				const openSession = (id) => {
					const address = typeof sessions.subagentAddress === "function" ? sessions.subagentAddress(id) : undefined;
					if (address != null) sessions.openSubagent(address);
					else sessions.open(id);
				};
				const jump = (id) => { setOpen(false); openSession(id); };
				const isOpenRow = (b) => override[b.coordinator.id] !== undefined ? override[b.coordinator.id] : b.blockedCount > 0;
				const button = React.createElement(
					"button",
					{
						style: {
							display: "flex", alignItems: "center", gap: "8px", width: "100%", boxSizing: "border-box",
							padding: "6px 8px", borderRadius: "8px", cursor: "pointer", textAlign: "left",
							color: TOK.label, background: "transparent", border: "1px solid " + TOK.border,
							fontFamily: FONT, ...T12, fontWeight: 500, transition: "background " + TOK.ease
						},
						onMouseEnter: (e) => { e.currentTarget.style.background = TOK.bgInset; },
						onMouseLeave: (e) => { e.currentTarget.style.background = "transparent"; },
						onClick: () => setOpen(true),
						"aria-haspopup": "dialog",
						"aria-expanded": open,
						title: "Delegated work across all projects"
					},
					React.createElement("span", { style: { width: "8px", height: "8px", borderRadius: "2px", background: snap.attention > 0 ? TOK.error : TOK.accent, flex: "none" } }),
					React.createElement("span", { style: { flex: 1 } }, "DS Kanban"),
					snap.attention > 0 ? React.createElement("span", { style: { color: TOK.error, ...T11, fontWeight: 500, fontVariantNumeric: "tabular-nums" } }, snap.attention) : null
				);
				if (!open) return button;
				const meta = (text, key, strong) => React.createElement("span", { key, style: { ...T11, color: strong ? TOK.label2 : TOK.label3, fontWeight: 500, whiteSpace: "nowrap" } }, text);
				/** Context fill bar; hidden entirely when the projection is absent. */
				const bar = (frac, key) => frac == null ? null : React.createElement("span", { key, title: "context " + Math.round(frac * 100) + "% full", style: { display: "inline-flex", alignItems: "center", gap: "4px" } },
					React.createElement("span", { style: { width: "32px", height: "3px", borderRadius: "999px", background: TOK.bgInset, overflow: "hidden", display: "inline-block" } },
						React.createElement("span", { style: { display: "block", width: Math.max(2, Math.round(frac * 100)) + "%", height: "100%", borderRadius: "999px", background: frac > PRESSURE_HIGH ? TOK.error : frac > PRESSURE_WARN ? TOK.warn : TOK.label3 } })),
					React.createElement("span", { style: { color: frac > PRESSURE_HIGH ? TOK.error : TOK.label3, ...T11, fontVariantNumeric: "tabular-nums" } }, Math.round(frac * 100) + "%"));
				const workerRow = (w) => {
					const s = w.summary;
					const ms = activeMs(s, now);
					const tool = w.state === "running" ? pendingToolOf(s) : undefined;
					const rec = activity.get(s.id);
					return React.createElement("div", {
						key: s.id,
						onClick: () => jump(s.id),
						title: s.id,
						style: { display: "flex", alignItems: "center", gap: "8px", padding: "6px 8px", cursor: "pointer", userSelect: "none", ...T12, borderRadius: "8px", transition: "background " + TOK.ease },
						onMouseEnter: (e) => { e.currentTarget.style.background = TOK.bgInset; },
						onMouseLeave: (e) => { e.currentTarget.style.background = "transparent"; }
					},
						React.createElement("span", { style: { width: "6px", height: "6px", borderRadius: "50%", flex: "none", marginLeft: "3px", background: LIVE_STATE[w.state] ? STATE_COLOR[w.state] : "transparent", border: LIVE_STATE[w.state] ? "none" : "1.5px solid " + TOK.border3 } }),
						React.createElement("span", { style: { color: TOK.label, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", flex: 1, minWidth: 0 } }, labelOf(s)),
						w.state === "blocked" ? meta("waiting" + (rec && rec.blockedSince ? " " + fmtAgo(rec.blockedSince, now) : "") + " · " + (s.pendingInteraction || ""), "b", true) : null,
						tool ? meta(tool, "t") : null,
						ms != null ? meta(fmtMs(ms), "d") : null,
						bar(pressureOf(s), "p"),
						tokensOf(s) != null ? meta(fmtTokens(tokensOf(s)), "k") : null);
				};
				const batchCard = (b) => {
					const c = b.coordinator;
					const expanded = isOpenRow(b);
					const proj0 = projectOf(c, snap.titleBySession);
					const totalMs = [c].concat(b.workers.map((w) => w.summary)).map((s) => activeMs(s, now)).filter((v) => v != null).reduce((a, v) => a + v, 0);
					const totalTok = [c].concat(b.workers.map((w) => w.summary)).map(tokensOf).filter((v) => v != null).reduce((a, v) => a + v, 0);
					const totalSteps = [c].concat(b.workers.map((w) => w.summary)).map(stepsOf).filter((v) => v != null).reduce((a, v) => a + v, 0);
					const tool = b.coordinatorState === "running" ? pendingToolOf(c) : undefined;
					const metrics = [];
					if (totalMs > 0) metrics.push(fmtMs(totalMs) + " active");
					if (totalSteps > 0) metrics.push(totalSteps + " steps");
					if (totalTok > 0) metrics.push(fmtTokens(totalTok) + " tok");
					const dots = b.workers.slice(0, 14).map((w, i) => React.createElement("span", {
						key: w.summary.id || i,
						title: labelOf(w.summary) + " — " + STATE_TEXT[w.state],
						onClick: (e) => { e.stopPropagation(); jump(w.summary.id); },
						style: { width: "7px", height: "7px", borderRadius: "50%", flex: "none", cursor: "pointer", background: LIVE_STATE[w.state] ? STATE_COLOR[w.state] : "transparent", border: LIVE_STATE[w.state] ? "none" : "1.5px solid " + TOK.border3 }
					}));
					return React.createElement("div", {
						key: c.id,
						onMouseEnter: (e) => { e.currentTarget.style.boxShadow = TOK.shadow2; },
						onMouseLeave: (e) => { e.currentTarget.style.boxShadow = TOK.shadow; },
						style: { opacity: b.state === "archived" ? .6 : 1, background: TOK.bgCard, border: "1px solid " + TOK.border, borderLeft: "2px solid " + (LIVE_STATE[b.state] ? STATE_COLOR[b.state] : TOK.border3), borderRadius: "12px", marginBottom: "8px", boxShadow: TOK.shadow, transition: "box-shadow " + TOK.ease + ", border-color " + TOK.ease }
					},
						React.createElement("div", { style: { padding: "10px 12px" } },
							React.createElement("div", { style: { display: "flex", alignItems: "flex-start", gap: "8px" } },
								b.workers.length > 0
									? React.createElement("span", {
										onClick: () => setOverride((p) => { const n = { ...p }; n[c.id] = !expanded; return n; }),
										title: expanded ? "Collapse workers" : "Expand workers",
										style: { cursor: "pointer", color: TOK.label3, ...T11, flex: "none", userSelect: "none" }
									}, expanded ? "▾" : "▸")
									: React.createElement("span", { style: { width: "9px", flex: "none" } }),
								React.createElement("span", {
									onClick: () => jump(c.id),
									title: c.id,
									style: { ...T12, fontWeight: 500, color: TOK.label, cursor: "pointer", overflowWrap: "anywhere", flex: 1, minWidth: 0 }
								}, labelOf(c))),
							!grouped && proj0
								? React.createElement("div", { style: { marginTop: "5px" } },
									React.createElement("span", { style: { background: TOK.hover, color: TOK.label2, borderRadius: "999px", padding: "2px 8px", ...T11, fontWeight: 500 } }, proj0))
								: null,
							b.state === "blocked" || tool
								? React.createElement("div", { style: { marginTop: "5px", ...T11, fontWeight: 500, color: b.state === "blocked" ? TOK.error : TOK.label3 } },
									b.state === "blocked"
										? (b.blockedCount > 1 ? b.blockedCount + " blocked" : "blocked") + (b.blockedSince ? " " + fmtAgo(b.blockedSince, now) : "")
										: tool)
								: null,
							b.workers.length > 0
								? React.createElement("div", { style: { display: "flex", alignItems: "center", gap: "4px", marginTop: "6px", flexWrap: "wrap" } },
									dots,
									b.workers.length > 14 ? React.createElement("span", { key: "more", style: { ...T11, color: TOK.label3 } }, "+" + (b.workers.length - 14)) : null,
									React.createElement("span", { key: "n", style: { marginLeft: "auto", ...T11, color: TOK.label3, fontWeight: 500, fontVariantNumeric: "tabular-nums" } }, b.doneCount + "/" + b.workers.length))
								: null,
							metrics.length > 0
								? React.createElement("div", { title: metrics.join(" · "), style: { marginTop: "6px", ...T11, color: TOK.label3, fontVariantNumeric: "tabular-nums", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" } }, metrics.join(" · "))
								: null,
							pressureOf(c) != null
								? React.createElement("div", { style: { marginTop: "5px" } }, bar(pressureOf(c), "p"))
								: null),
						expanded && b.workers.length > 0
							? React.createElement("div", { style: { borderTop: "1px solid " + TOK.hair, borderRadius: "0 0 11px 11px", padding: "4px 6px 6px" } }, b.workers.map(workerRow))
							: null);
				};
				const show = (r) => states[r.state] === true;
				const visible = snap.rows.filter(show);
				const sections = grouped
					? snap.groups.map((g) => ({ project: g.project, counts: g.counts, rows: g.rows.filter(show) })).filter((g) => g.rows.length > 0)
					: [{ project: undefined, counts: snap.counts, rows: visible }];
				/** One toggle per state, always showing its true total even while filtered out. */
				const filters = FILTER_ORDER.map((k) => {
					const n = snap.counts[k] || 0;
					const on = states[k] === true;
					const muted = n === 0 && !on;
					return React.createElement("button", {
						key: k,
						onClick: () => setStates((prev) => { const next = { ...prev }; next[k] = !on; return next; }),
						title: n + " " + STATE_TEXT[k],
						style: {
							display: "inline-flex", alignItems: "center", gap: "6px", fontFamily: "inherit",
							border: "1px solid " + (on ? TOK.border : TOK.hair), background: on ? TOK.bgInset : "transparent",
							color: muted ? TOK.dim : on ? TOK.label : TOK.label3,
							borderRadius: "999px", padding: "3px 10px", cursor: "pointer",
							...T12, fontWeight: 500, opacity: muted ? .5 : 1, transition: "background " + TOK.ease + ", border-color " + TOK.ease
						}
					},
						React.createElement("span", { style: { width: "6px", height: "6px", borderRadius: "50%", flex: "none", background: LIVE_STATE[k] ? STATE_COLOR[k] : "transparent", border: LIVE_STATE[k] ? "none" : "1.5px solid " + TOK.border3 } }),
						STATE_LABEL[k],
						React.createElement("span", { style: { color: TOK.label3, fontWeight: 500, fontVariantNumeric: "tabular-nums" } }, n));
				});
				/** Per-project tally: non-zero states only, in triage order. */
				const tally = (counts) => FILTER_ORDER.filter((k) => (counts[k] || 0) > 0).map((k) =>
					React.createElement("span", { key: k, style: { color: k === "blocked" ? TOK.error : TOK.label3, fontWeight: k === "blocked" ? 700 : 500 } },
						counts[k] + " " + STATE_LABEL[k].toLowerCase()));
				const sectionHead = (g) => g.project === undefined ? null : React.createElement("div", {
					style: { display: "flex", alignItems: "center", gap: "8px", margin: "16px 2px 7px", flexWrap: "nowrap" }
				},
					React.createElement("span", { style: { ...T12, fontWeight: 500, color: TOK.label, flex: "none" } }, g.project),
					React.createElement("span", { style: { height: "1px", background: TOK.border, flex: 1, minWidth: "18px" } }),
					React.createElement("span", { style: { ...T11, display: "inline-flex", gap: "8px", flex: "none" } }, tally(g.counts)));
				/** The enabled states, in triage order, are the board's columns. */
				const columns = FILTER_ORDER.filter((k) => states[k] === true);
				// `stretch` keeps every column the same height as the tallest in its lane;
				// the ungrouped board additionally fills the viewport, so columns always
				// read as full-height lanes rather than shrink-wrapped boxes.
				// An empty column still has to be visible - "nothing is blocked" IS the
				// information - but three empty live columns should not take half the board.
				// Emptiness is judged across ALL lanes, so every swimlane gets the same
				// template and the columns stay aligned down the page.
				const columnEmpty = {};
				for (const k of columns) columnEmpty[k] = !visible.some((r) => r.state === k);
				const gridStyle = {
					display: "grid",
					gridTemplateColumns: columns.map((k) => columnEmpty[k] ? "minmax(96px, .32fr)" : "minmax(210px, 1fr)").join(" ") || "1fr",
					gap: "10px",
					alignItems: "stretch"
				};
				if (!grouped) gridStyle.height = "100%";
				/** One swimlane: the same column set, holding only this project's batches. */
				const laneGrid = (g, withHeaders) => React.createElement("div", { style: gridStyle },
					columns.map((k) => {
						const items = g.rows.filter((r) => r.state === k);
						return React.createElement("div", {
							key: k,
							style: {
								display: "flex", flexDirection: "column", minWidth: 0,
								minHeight: grouped ? "128px" : 0,
								background: TOK.bgCol, border: "1px solid " + TOK.hair,
								borderRadius: "12px", padding: "10px"
							}
						},
							withHeaders
								? React.createElement("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center", margin: "0 2px 9px", ...T11, fontWeight: 500, color: TOK.label2, flex: "none" } },
									React.createElement("span", { style: { display: "inline-flex", alignItems: "center", gap: "6px" } },
										React.createElement("span", { style: { width: "6px", height: "6px", borderRadius: "50%", background: LIVE_STATE[k] ? STATE_COLOR[k] : "transparent", border: LIVE_STATE[k] ? "none" : "1.5px solid " + TOK.border3 } }),
										STATE_LABEL[k]),
									React.createElement("span", { style: { color: TOK.label3, fontVariantNumeric: "tabular-nums" } }, items.length))
								: null,
							React.createElement("div", { style: { flex: 1, minHeight: 0, overflowY: grouped ? "visible" : "auto", ...SCROLL } },
								items.length === 0
									? React.createElement("div", { style: { ...T11, color: TOK.dim, height: "100%", minHeight: "48px", display: "flex", alignItems: "center", justifyContent: "center" } }, "none")
									: items.map(batchCard)));
					}));
				// Every figure below comes from a projection carried on the session row.
				// Coverage is not guaranteed, so each total tracks whether it saw any data
				// and its cell disappears rather than reporting a confident zero.
				const flat = [];
				for (const b of snap.rows) { flat.push(b.coordinator); for (const w of b.workers) flat.push(w.summary); }
				let nRunning = 0, nBlocked = 0, nNear = 0, sumMs = 0, sumTok = 0, sawMs = false, sawTok = false;
				for (const sx of flat) {
					const stx = stateOf(sx);
					if (stx === "running") nRunning++;
					else if (stx === "blocked") nBlocked++;
					const p = pressureOf(sx);
					if (p != null && p > PRESSURE_HIGH) nNear++;
					const ms = activeMs(sx, now);
					if (ms != null) { sumMs += ms; sawMs = true; }
					const tk = tokensOf(sx);
					if (tk != null) { sumTok += tk; sawTok = true; }
				}
				const statCell = (value, caption, tone) => React.createElement("div", { key: caption, style: { display: "flex", flexDirection: "column", gap: "2px", minWidth: 0 } },
					React.createElement("span", { style: { ...T13, fontWeight: 500, color: tone || (value === 0 ? TOK.label3 : TOK.label), fontVariantNumeric: "tabular-nums" } }, value),
					React.createElement("span", { style: { ...T11, color: TOK.label3, whiteSpace: "nowrap" } }, caption));
				const statRow = React.createElement("div", {
					style: { display: "flex", gap: "24px", flexWrap: "wrap", alignItems: "flex-start", padding: "0 2px 12px", marginBottom: "12px", borderBottom: "1px solid " + TOK.hair, flex: "none" }
				}, [
					statCell(nBlocked, nBlocked === 1 ? "waiting on you" : "waiting on you", nBlocked > 0 ? TOK.error : undefined),
					statCell(nRunning, "running now"),
					nNear > 0 ? statCell(nNear, "near context limit", TOK.warn) : null,
					statCell(snap.batchCount, snap.batchCount === 1 ? "batch" : "batches"),
					statCell(snap.delegated, "delegating"),
					statCell(snap.sessionCount, snap.sessionCount === 1 ? "session" : "sessions"),
					sawMs ? statCell(fmtMs(sumMs), "agent time") : null,
					sawTok ? statCell(fmtTokens(sumTok), "tokens") : null
				].filter(Boolean));
				const legend = ["blocked", "running", "done", "idle"].map((s) => React.createElement("span", { key: s, style: { display: "inline-flex", alignItems: "center", gap: "4px" } },
					React.createElement("span", { style: { width: "6px", height: "6px", borderRadius: "50%", background: LIVE_STATE[s] ? STATE_COLOR[s] : "transparent", border: LIVE_STATE[s] ? "none" : "1.5px solid " + TOK.border3 } }),
					STATE_TEXT[s]));
				return React.createElement(React.Fragment, null,
					button,
					React.createElement("div", {
						role: "dialog",
						"aria-label": "DS Kanban",
						style: { position: "fixed", inset: "0", zIndex: 1000, background: TOK.bgBase, display: "flex", flexDirection: "column", padding: "20px 22px", boxSizing: "border-box", fontFamily: FONT, color: TOK.label, ...SCROLL }
					},
						React.createElement("div", { style: { display: "flex", alignItems: "baseline", gap: "12px", marginBottom: "12px", flexWrap: "wrap", flex: "none" } },
							React.createElement("h2", { style: { margin: 0, fontSize: "18px", lineHeight: "28px", fontWeight: 600 } }, "DS Kanban"),
							React.createElement("span", { style: { flex: 1 } }),
							React.createElement("button", {
								onClick: () => setOpen(false),
								onMouseEnter: (e) => { e.currentTarget.style.background = TOK.bgCol; e.currentTarget.style.color = TOK.label; },
								onMouseLeave: (e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = TOK.label2; },
								style: { appearance: "none", border: "1px solid " + TOK.border, background: "transparent", color: TOK.label2, borderRadius: "8px", padding: "4px 12px", cursor: "pointer", ...T12, fontWeight: 500, fontFamily: FONT, transition: "background " + TOK.ease + ", color " + TOK.ease }
							}, "Close")),
						statRow,
						React.createElement("div", { style: { display: "flex", alignItems: "center", gap: "6px", marginBottom: "8px", flexWrap: "wrap", flex: "none" } },
							filters,
							React.createElement("span", { style: { flex: 1, minWidth: "8px" } }),
							React.createElement("button", {
								onClick: () => setGrouped(!grouped),
								style: { appearance: "none", border: "1px solid " + (grouped ? TOK.border : TOK.hair), background: grouped ? TOK.bgInset : "transparent", color: grouped ? TOK.label : TOK.label3, borderRadius: "999px", padding: "3px 10px", cursor: "pointer", ...T12, fontFamily: FONT, fontWeight: 500, transition: "background " + TOK.ease + ", border-color " + TOK.ease }
							}, (grouped ? "\u2713  " : "") + "Group by project")),
						React.createElement("div", { style: { flex: 1, minHeight: 0, overflowY: grouped ? "auto" : "hidden", ...SCROLL } },
							sections.length === 0
								? React.createElement("div", { style: { color: TOK.dim, ...T13, padding: "12px 2px" } },
									snap.batchCount === 0 ? "No sessions yet." : "Nothing matches the selected states.")
								: sections.map((g, i) => React.createElement("div", { key: g.project || "__all__", style: grouped ? undefined : { height: "100%" } }, sectionHead(g), laneGrid(g, true)))),
						React.createElement("div", { style: { display: "flex", alignItems: "center", gap: "10px", marginTop: "10px", flexWrap: "wrap", flex: "none", ...T11, color: TOK.label3 } },
							React.createElement("span", null, visible.length + " of " + snap.batchCount + " batches shown"),
							React.createElement("span", { style: { flex: 1 } }),
							React.createElement("span", { style: { display: "inline-flex", alignItems: "center", gap: "10px" } },
								React.createElement("span", { key: "cap", style: { color: TOK.dim } }, "workers"),
								legend))));
			}
			ctx.slots.inject("sidebar.footer.action", () => ctx.slots.register({
				name: "sidebar.footer.action",
				id: "ds-kanban",
				locale: "mission-control"
			}, DsKanbanAction));
		}
		exports.apply = apply;
		exports.inject = inject;
		return module.exports;
	}
});
