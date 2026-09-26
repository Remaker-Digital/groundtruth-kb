// GT-KB Home, browser side (DeepSeek Harness client module; owner rulings D58, D59).
// Hand-written in the shell's module format on the shell's own React and UI primitives: no build step, no bundled
// dependency. Every GT-KB control is one call on the host's authenticated /gtkb channel, which runs one fixed `gt`
// command; the pages are Settings sections next to the shell's own (General, Models, Plugins, Agent presets).
window.__ModuleLoader__.load({
	id: "@gtkb/dsh-home",
	factory: (require) => {
		var module = { exports: {} };
		var exports = module.exports;
		Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
		const { jsx, jsxs } = require("react/jsx-runtime");
		const React = require("react");
		let ui = {};
		try {
			ui = require("@deepseek-ai/dsh-client-ui-primitives");
		} catch {
			ui = {};
		}
		const MARK = "/gtkb-home/mark.svg";
		const ATTRIBUTION = "GT-KB by Remaker Digital · Built on DeepSeek Harness (MIT License)";
		const TONE = { ok: "#2e9e5b", warn: "#c98a14", error: "#d4412e", info: "inherit" };
		const STATUS_TONE = { PASS: "ok", running: "ok", WARN: "warn", UNKNOWN: "warn", unknown: "warn", FAIL: "error", stopped: "error" };
		const DOT = { ok: "done", warn: "warning", error: "error", busy: "ongoing" };
		const PAGE = { display: "flex", flexDirection: "column", gap: 12, padding: "4px 2px" };
		const TABLE = { borderCollapse: "collapse", width: "100%", fontSize: 13 };
		const CELL = { padding: "6px 8px", verticalAlign: "middle" };
		const ROW = { borderTop: "1px solid rgba(128,128,128,0.25)" };
		const CARD = { display: "flex", alignItems: "center", gap: 12, padding: "10px 12px", borderRadius: 8, border: "1px solid rgba(128,128,128,0.3)" };

		// ---- shell primitives, with plain fallbacks if a future shell stops exporting one ----
		function Button(props) {
			if (ui.Button) return jsx(ui.Button, props);
			const { variant, icon, ...rest } = props;
			return jsx("button", { type: "button", ...rest });
		}
		function Dot({ tone }) {
			if (ui.StateDot) return jsx(ui.StateDot, { state: DOT[tone] ?? "warning" });
			return jsx("span", { "aria-hidden": true, style: { color: TONE[tone] ?? TONE.warn, fontSize: 10 }, children: "●" });
		}
		function Dialog({ open, title, description, onClose, footer, children }) {
			if (!open) return null;
			if (ui.Modal) return jsx(ui.Modal, { open, title, description, onClose, closeLabel: "Close", footer, children });
			return jsx("div", {
				role: "dialog",
				"aria-modal": true,
				"aria-label": title,
				style: { position: "fixed", inset: 0, background: "rgba(0,0,0,0.45)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 },
				children: jsxs("div", {
					style: { background: "Canvas", color: "CanvasText", padding: 20, borderRadius: 10, width: "min(560px, 92vw)" },
					children: [
						jsx("div", { style: { fontWeight: 600, fontSize: 16, marginBottom: 6 }, children: title }),
						description ? jsx("div", { style: { fontSize: 13, opacity: 0.8, marginBottom: 12 }, children: description }) : null,
						children,
						jsx("div", { style: { display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 16 }, children: footer }),
					],
				}),
			});
		}

		// ---- one call on the host's /gtkb channel; failures come back as text, never as a thrown error ----
		async function gtkb(ctx, endpoint, payload) {
			try {
				const result = await ctx.connection.rpc.call("/gtkb", endpoint, payload ?? {});
				return result.ok ? { ok: true, value: result.value } : { ok: false, message: result.error?.message || `${endpoint} failed` };
			} catch (error) {
				return { ok: false, message: error instanceof Error ? error.message : String(error) };
			}
		}
		function useGtkb(ctx, endpoint) {
			const [state, setState] = React.useState({ loading: true });
			const load = React.useCallback(async () => {
				setState((previous) => ({ data: previous.data, loading: true }));
				const result = await gtkb(ctx, endpoint);
				setState(result.ok ? { data: result.value } : { data: undefined, error: result.message });
			}, [endpoint]);
			React.useEffect(() => { load(); }, [load]);
			return [state, load];
		}
		function when(value) {
			const time = Date.parse(value ?? "");
			return Number.isNaN(time) ? String(value ?? "") : new Date(time).toLocaleString();
		}
		function brief(value) {
			if (value === undefined || value === null) return "";
			const text = typeof value === "string" ? value : JSON.stringify(value);
			return text.length > 400 ? `${text.slice(0, 400)}…` : text;
		}

		// ---- shared page furniture ----
		function PageHeader({ title, subtitle, onRefresh, busy }) {
			return jsxs("div", {
				style: { display: "flex", alignItems: "center", gap: 12 },
				children: [
					jsx("img", { src: MARK, alt: "", width: 36, height: 36, style: { borderRadius: 6 } }),
					jsxs("div", { children: [
						jsx("div", { style: { fontWeight: 600, fontSize: 16 }, children: title }),
						jsx("div", { style: { fontSize: 12, opacity: 0.7 }, children: subtitle }),
					] }),
					onRefresh ? jsx("div", { style: { marginLeft: "auto" }, children: jsx(Button, { variant: "outline", disabled: busy, onClick: onRefresh, children: busy ? "Reading…" : "Refresh" }) }) : null,
				],
			});
		}
		function Notice({ notice }) {
			if (!notice) return null;
			return jsx("div", {
				role: notice.tone === "error" ? "alert" : "status",
				style: { color: TONE[notice.tone] ?? "inherit", fontSize: 13, whiteSpace: "pre-wrap", overflowWrap: "anywhere" },
				children: notice.text,
			});
		}
		function Attribution() {
			return jsxs("div", { style: { fontSize: 11, opacity: 0.6, marginTop: 8 }, children: [
				ATTRIBUTION,
				" · ",
				jsx("a", { href: "/gtkb-home/notices", target: "_blank", rel: "noopener noreferrer", children: "License notices" }),
			] });
		}

		// ---- GT-KB: status and the dashboard ----
		function DashboardCard({ evidence }) {
			if (!evidence || !evidence.grafana_url) return null;
			return jsxs("div", {
				style: CARD,
				children: [
					jsxs("div", { children: [
						jsx("div", { style: { fontWeight: 600 }, children: "GT-KB dashboard" }),
						jsx("div", { style: { fontSize: 12, opacity: 0.75 }, children: evidence.last_refresh ? `Last refreshed ${when(evidence.last_refresh)}` :"Not refreshed yet. Start the dashboard on the GT-KB services page." }),
					] }),
					jsxs("div", { style: { marginLeft: "auto", display: "flex", gap: 14, fontSize: 13 }, children: [
						jsx("a", { href: evidence.grafana_url, target: "_blank", rel: "noopener noreferrer", children: "Open dashboard" }),
						evidence.refresh_url ? jsx("a", { href: evidence.refresh_url, target: "_blank", rel: "noopener noreferrer", children: "Overview page" }) : null,
					] }),
				],
			});
		}
		function StatusPage({ ctx }) {
			const [state, load] = useGtkb(ctx, "status");
			const rows = state.data?.components ?? [];
			const dashboard = rows.find((row) => row.name === "dashboard")?.evidence;
			const subtitle = state.data ? `Overall ${state.data.overall_status} · ${when(state.data.captured_at)}` :(state.loading ? "Reading gt status…" : "");
			return jsxs("div", {
				style: PAGE,
				children: [
					jsx(PageHeader, { title: "GT-KB status", subtitle, onRefresh: load, busy: state.loading }),
					jsx(Notice, { notice: state.error ? { tone: "error", text: state.error } : null }),
					jsx(DashboardCard, { evidence: dashboard }),
					jsx("table", { style: TABLE, children: jsx("tbody", { children: rows.map((row) => jsxs("tr", {
						style: ROW,
						children: [
							jsx("td", { style: { ...CELL, width: 18 }, children: jsx(Dot, { tone: STATUS_TONE[row.status] ?? "warn" }) }),
							jsx("td", { style: { ...CELL, fontWeight: 500, whiteSpace: "nowrap" }, children: row.name }),
							jsx("td", { style: { ...CELL, color: TONE[STATUS_TONE[row.status]] ?? "inherit", fontWeight: 600 }, children: row.status }),
							jsx("td", { style: { ...CELL, opacity: 0.85, overflowWrap: "anywhere" }, children: row.detail }),
						],
					}, row.name)) }) }),
					jsx(Attribution, {}),
				],
			});
		}

		// ---- GT-KB services: start and stop ----
		const SERVICES = {
			authority: { title: "Authority", stop: "Governed sessions, the effect gate and GT-KB status reads fail until it is started again. Its logon task stays paused until then." },
			home: { title: "Home", stop: null },
			dashboard: { title: "Dashboard", stop: "The dashboard refresh service and Grafana stop; the dashboard links do not open until it is started again." },
			ollama: { title: "Ollama", stop: "Local models are unavailable until it is started again. Its logon task stays paused until then." },
			postgresql: { title: "PostgreSQL", stop: "The gtkb-postgresql Windows service stops (this usually needs an administrator). The authority cannot read or write until PostgreSQL runs again." },
		};
		function ServicesPage({ ctx }) {
			const [state, load] = useGtkb(ctx, "services/status");
			const [confirming, setConfirming] = React.useState(null);
			const [busy, setBusy] = React.useState(null);
			const [notice, setNotice] = React.useState(null);
			const run = React.useCallback(async (name, action) => {
				setConfirming(null);
				setBusy(name);
				setNotice({ tone: "info", text: `${action === "start" ? "Starting" : "Stopping"} ${SERVICES[name]?.title ?? name}…` });
				const result = await gtkb(ctx, `services/${action}`, { name });
				setBusy(null);
				if (!result.ok) {
					setNotice({ tone: "error", text: result.message });
				} else if (action === "start" ? result.value.started : result.value.stopped) {
					setNotice({ tone: "ok", text: `${SERVICES[name]?.title ?? name} ${action === "start" ? "started" : "stopped"}.` });
				} else {
					setNotice({ tone: "warn", text: `${SERVICES[name]?.title ?? name}: ${brief(result.value.detail)}` });
				}
				load();
			}, [load]);
			const rows = Array.isArray(state.data) ? state.data : [];
			const pending = confirming ? SERVICES[confirming] ?? { title: confirming, stop: "" } : null;
			return jsxs("div", {
				style: PAGE,
				children: [
					jsx(PageHeader, { title: "GT-KB services", subtitle: "Start or stop the services GT-KB runs on this computer.", onRefresh: load, busy: state.loading || busy !== null }),
					jsx(Notice, { notice: state.error ? { tone: "error", text: state.error } : notice }),
					jsx("table", { style: TABLE, children: jsx("tbody", { children: rows.map((row) => jsxs("tr", {
						style: ROW,
						children: [
							jsx("td", { style: { ...CELL, width: 18 }, children: jsx(Dot, { tone: busy === row.name ? "busy" : STATUS_TONE[row.state] ?? "warn" }) }),
							jsx("td", { style: { ...CELL, fontWeight: 500, whiteSpace: "nowrap" }, children: SERVICES[row.name]?.title ?? row.name }),
							jsx("td", { style: { ...CELL, whiteSpace: "nowrap" }, children: busy === row.name ? "working…" : row.state }),
							jsx("td", { style: { ...CELL, opacity: 0.8, fontSize: 12, overflowWrap: "anywhere" }, children: row.detail }),
							jsx("td", { style: { ...CELL, textAlign: "right", whiteSpace: "nowrap" }, children: row.name === "home" ? jsx("span", { style: { fontSize: 12, opacity: 0.7 }, children: "this page" })
								: row.can_stop ? jsx(Button, { variant: "outline", disabled: busy !== null, onClick: () => setConfirming(row.name), children: "Stop" })
								: row.can_start ? jsx(Button, { variant: "primary", disabled: busy !== null, onClick: () => run(row.name, "start"), children: "Start" })
								: null }),
						],
					}, row.name)) }) }),
					jsx(Dialog, {
						open: pending !== null,
						title: pending ? `Stop ${pending.title}?` : "",
						description: pending?.stop ?? "",
						onClose: () => setConfirming(null),
						footer: jsxs(React.Fragment, { children: [
							jsx(Button, { variant: "outline", autoFocus: true, onClick: () => setConfirming(null), children: "Cancel" }),
							jsx(Button, { variant: "primary", onClick: () => run(confirming, "stop"), children: "Stop" }),
						] }),
					}),
					jsx(Attribution, {}),
				],
			});
		}

		// ---- GT-KB configuration: the live operational controls, changed through preview then apply ----
		function ConfigurationPage({ ctx }) {
			const [state, load] = useGtkb(ctx, "controls/show");
			const [drafts, setDrafts] = React.useState({});
			const [proposal, setProposal] = React.useState(null);
			const [busy, setBusy] = React.useState(false);
			const [notice, setNotice] = React.useState(null);
			const controls = Object.values(state.data?.controls ?? {});
			const preview = async (controlId) => {
				setBusy(true);
				setNotice(null);
				const result = await gtkb(ctx, "controls/propose", { control_id: controlId, value: drafts[controlId].trim() });
				setBusy(false);
				if (result.ok) setProposal({ controlId, diff: result.value });
				else setNotice({ tone: "error", text: result.message });
			};
			const apply = async () => {
				const { controlId, diff } = proposal;
				setBusy(true);
				const result = await gtkb(ctx, "controls/apply", { handle: diff.handle, expected_sha256: diff.before_sha256 });
				setBusy(false);
				setProposal(null);
				if (result.ok) {
					setDrafts((previous) => {
						const next = { ...previous };
						delete next[controlId];
						return next;
					});
					setNotice({ tone: "ok", text: result.value.changed ? `${controlId} updated. It takes effect at the next operation that reads it.` : "Nothing changed." });
				} else {
					setNotice({ tone: "error", text: `${result.message}\nRefresh, then preview the change again.` });
				}
				load();
			};
			const changes = proposal ? Object.entries(proposal.diff.controls ?? {}) : [];
			return jsxs("div", {
				style: PAGE,
				children: [
					jsx(PageHeader, {
						title: "GT-KB configuration",
						subtitle: state.data ? `Operational controls · ${state.data.source_reference}` : (state.loading ? "Reading gt controls show…" : ""),
						onRefresh: load,
						busy: state.loading || busy,
					}),
					jsx(Notice, { notice: state.error ? { tone: "error", text: state.error } : notice }),
					jsx("table", { style: TABLE, children: jsxs("tbody", { children: [
						jsxs("tr", { style: { fontSize: 11, opacity: 0.65, textAlign: "left" }, children: [
							jsx("th", { style: CELL, children: "Control" }),
							jsx("th", { style: CELL, children: "Value" }),
							jsx("th", { style: CELL, children: "Allowed" }),
							jsx("th", { style: CELL, children: "" }),
						] }),
						...controls.map((control) => {
							const current = String(control.value);
							const draft = drafts[control.control_id];
							const edited = draft !== undefined && draft.trim() !== current;
							return jsxs("tr", {
								style: ROW,
								children: [
									jsxs("td", { style: CELL, title: control.rationale, children: [
										jsx("div", { style: { fontWeight: 500, fontFamily: "ui-monospace, monospace", fontSize: 12 }, children: control.control_id }),
										jsx("div", { style: { fontSize: 12, opacity: 0.75 }, children: control.description }),
									] }),
									jsx("td", { style: { ...CELL, whiteSpace: "nowrap" }, children: jsxs("label", { children: [
										jsx("input", {
											"aria-label": `${control.control_id} value`,
											value: draft ?? current,
											inputMode: "decimal",
											size: 8,
											disabled: busy,
											onChange: (event) => setDrafts((previous) => ({ ...previous, [control.control_id]: event.target.value })),
											style: { font: "inherit", padding: "2px 6px", width: "7em" },
										}),
										jsx("span", { style: { marginLeft: 6, fontSize: 12, opacity: 0.75 }, children: control.unit }),
									] }) }),
									jsx("td", { style: { ...CELL, fontSize: 12, opacity: 0.75, whiteSpace: "nowrap" }, children: `${control.minimum} – ${control.maximum}` }),
									jsx("td", { style: { ...CELL, textAlign: "right" }, children: edited ? jsx(Button, { variant: "primary", disabled: busy, onClick: () => preview(control.control_id), children: "Preview" }) : null }),
								],
							}, control.control_id);
						}),
					] }) }),
					jsx(Dialog, {
						open: proposal !== null,
						title: "Apply this configuration change?",
						description: "GT-KB validated the complete proposed controls file, including its bounds and invariants. Applying replaces the live file only if it has not changed since this preview.",
						onClose: () => setProposal(null),
						footer: jsxs(React.Fragment, { children: [
							jsx(Button, { variant: "outline", autoFocus: true, disabled: busy, onClick: () => setProposal(null), children: "Cancel" }),
							jsx(Button, { variant: "primary", disabled: busy, onClick: apply, children: busy ? "Applying…" : "Apply" }),
						] }),
						children: jsx("div", { style: { fontSize: 13 }, children: changes.map(([id, change]) => jsxs("div", {
							style: { padding: "6px 0" },
							children: [
								jsx("div", { style: { fontFamily: "ui-monospace, monospace", fontSize: 12 }, children: id }),
								jsx("div", { children: `${change.before?.value ?? "—"} → ${change.after?.value ?? "—"} ${change.after?.unit ?? change.before?.unit ?? ""}` }),
							],
						}, id)) }),
					}),
					jsx(Attribution, {}),
				],
			});
		}

		// ---- brand ----
		function BrandMark({ size }) {
			const px = size ?? 24;
			return jsx("img", { src: MARK, alt: "Remaker Digital", width: px, height: px, style: { display: "block", borderRadius: 4 } });
		}
		// The owner's call (2026-09-25): only "GT-KB" beside the mark, at the sidebar's own brand size and on one line; the
		// two-line name with "by Remaker Digital" was too large for the sidebar header and was cut off.
		function BrandName() {
			return jsx("span", { style: { fontWeight: 600, letterSpacing: "0.02em", whiteSpace: "nowrap" }, children: "GT-KB" });
		}
		function HeroMark({ size }) {
			const px = size ?? 72;
			return jsx("img", { src: MARK, alt: "GT-KB by Remaker Digital", width: px, height: px, style: { borderRadius: 10 } });
		}

		// The layout projects "<session title> — DeepSeek Harness" into document.title from a hard-coded product name; the
		// host rewrites the index title, and this observer keeps the product name GT-KB's whenever the shell sets it.
		const UPSTREAM_PRODUCT = "DeepSeek Harness";
		const PRODUCT = "GT-KB Home";
		function keepProductTitle() {
			const retitle = () => {
				if (document.title.includes(UPSTREAM_PRODUCT)) document.title = document.title.replace(UPSTREAM_PRODUCT, PRODUCT);
			};
			const titleElement = document.querySelector("title") ?? document.head.appendChild(document.createElement("title"));
			const observer = new MutationObserver(retitle);
			observer.observe(titleElement, { childList: true, characterData: true, subtree: true });
			retitle();
			return () => observer.disconnect();
		}

		// The conversation hero's headline is upstream's slogan: a locale string with no slot (pinned bundle:
		// t("hero.headline") in a span whose module class ends in "_headlineText"), and the locale service refuses a
		// second dictionary for a namespace it already holds. The owner titles it "GroundTruth Knowledge Base"
		// (2026-09-25). This observer sets the text node's value in place, so React keeps its own node, in any locale.
		const HEADLINE = "GroundTruth Knowledge Base";
		const UPSTREAM_HEADLINES = new Set(["Into the Unknown", "探索未至之境"]);
		function keepHeroHeadline() {
			const retitle = () => {
				for (const span of document.querySelectorAll('span[class*="_headlineText"]')) {
					const text = span.firstChild;
					if (text && text.nodeType === 3 && UPSTREAM_HEADLINES.has(text.nodeValue)) text.nodeValue = HEADLINE;
				}
			};
			const observer = new MutationObserver(retitle);
			observer.observe(document.body, { childList: true, characterData: true, subtree: true });
			retitle();
			return () => observer.disconnect();
		}

		const SECTIONS = [
			{ id: "gtkb", order: 1, label: "GT-KB", page: StatusPage },
			{ id: "gtkb-services", order: 2, label: "GT-KB services", page: ServicesPage },
			{ id: "gtkb-configuration", order: 3, label: "GT-KB controls", page: ConfigurationPage },
		];
		const inject = ["slots", "connection"];
		function apply(ctx) {
			ctx.effect(keepProductTitle, "gtkb-home: product title");
			ctx.effect(keepHeroHeadline, "gtkb-home: hero headline");
			ctx.slots.inject("sidebar.brand.mark", () => ctx.slots.inject("sidebar.brand.name", function* () {
				yield ctx.slots.register({ name: "sidebar.brand.mark" }, BrandMark);
				yield ctx.slots.register({ name: "sidebar.brand.name" }, BrandName);
			}));
			ctx.slots.inject("conversation.hero.brand.mark", () => ctx.slots.register({ name: "conversation.hero.brand.mark" }, HeroMark));
			ctx.slots.inject("settings.section", function* () {
				for (const section of SECTIONS) {
					const Page = section.page;
					yield ctx.slots.register(
						{ name: "settings.section", id: section.id, order: section.order, label: () => section.label },
						function GtkbSection() { return jsx(Page, { ctx }); },
					);
				}
			});
		}
		exports.apply = apply;
		exports.inject = inject;
		return module.exports;
	}
});
