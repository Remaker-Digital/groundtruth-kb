# NO-GO Backlog Triage — 2026-06-18 (session B-2026-06-18, harness B / Claude)

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 078ada78-06c2-4620-82aa-e78b459d95ba
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive Prime Builder session; explanatory output style

Prime Builder triage of the **23 Prime-actionable NO-GO bridge threads**, per owner
AUQ decision **"Triage NO-GO backlog"** (2026-06-18). Read-only investigation; no
mutations were made. This file exists so a fresh session can load the classification
without re-running the queries.

## Method (reproducible)
- Live actionable scan: `groundtruth-kb/.venv/Scripts/python.exe .claude/skills/bridge/helpers/scan_bridge.py --role prime-builder`
- WI / spec state via `groundtruth_kb.db.KnowledgeDB()` against the canonical root `groundtruth.db`
  (`get_work_item`, `get_spec`, `get_project_work_item_membership`).
- Thread age via `git -C E:/GT-KB log -1 --format=%cs -- <latest bridge file>`.

## Bucket A — LIVE, highest-value, REVISE (6) · PROJECT-GTKB-RELIABILITY-FIXES fast-lane
All six are confirmed **open defects** in MemBase (stage created/backlogged, no completion
evidence). Every NO-GO is *"the defect is real, but the approach…"* (how-not-whether), so a
REVISED can clear it.

| thread (slug) | WI | open? | NO-GO gist |
|---|---|---|---|
| `gtkb-impl-start-gate-quoted-arg-misclassification` | WI-3358 | yes | impl-start gate misclassifies quoted args / protected-path tokens (relates to hygiene WI-4624) |
| `gtkb-index-role-sentinel-stale-reconciliation` | WI-3488 | yes | bridge/INDEX.md stale role sentinel + 9 parse errors |
| `gtkb-index-withdrawn-status-reconciliation` | WI-3491 | yes | INDEX de-index gap (~39 WITHDRAWN notices); "detector direction sound, preflights…" |
| `gtkb-wrapup-clear-impl-start-packet-at-verified` | WI-3328 | yes | session wrap doesn't clear impl-start packet (current.json) at VERIFIED |
| `gtkb-project-authorization-completion-keep-open` | WI-3329 | yes | complete_project_authorization() auto-retires project on sole-auth completion; "retire_project=False approach…" |
| `gtkb-startup-relay-cache-ttl-self-heal` | WI-3486 | yes | startup relay cache 30-min TTL has no in-window self-heal |

## Bucket B — LIVE-fresh, SECONDARY (13) · all NO-GO'd 2026-06-16 (recent Codex LO pass)
Live, but findings not yet read; several are heavy umbrellas (poor ROI to revise blind).
`gtkb-app-boundary-mechanism-audit`, `gtkb-canonical-init-keyword-syntax`,
`gtkb-claude-code-bridge-status-thread-automation`,
`gtkb-cross-harness-trigger-active-session-suppression`,
`gtkb-dashboard-industry-alignment-slice2`, `gtkb-dashboard-industry-alignment-slice2a-visibility`,
`gtkb-dora-telemetry-foundation`, `gtkb-loyal-opposition-startup-symmetry`,
`gtkb-membase-effective-use-umbrella` (umbrella), `gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution`,
`gtkb-s373-triage-umbrella` (umbrella), `gtkb-single-harness-bridge-dispatcher`,
`gtkb-startup-trigger-awareness-and-skill-reference`.

## Bucket C — STALE / superseded-suspect (4) · Apr 2026 — do NOT revise; owner-disposition
| thread | staleness signal |
|---|---|
| `commercial-readiness-spec-1831-startup-wiring` | SPEC-1831 now `status=implemented` → likely superseded |
| `commercial-readiness-spec-1833-ready-propagation` | SPEC-1833 now `status=implemented` → likely superseded |
| `commercial-readiness-spec-verification` | tied to the two above → likely superseded |
| `agent-red-bridge-dispatcher-deferral-enforcement-implementation` | **Agent Red application scope** — outside default GT-KB work subject |

Disposition for Bucket C is owner-directed WITHDRAWN / verification (a state action), not a Prime REVISED.

**Owner-approved plan (2026-06-18):** the fresh session OPENS with a Bucket C disposition AUQ
before any Bucket A revision. Recommended per-thread dispositions (confirm via AUQ, then file the
state entries through the governed bridge path):
- The 3 `commercial-readiness-*` threads → **WITHDRAWN (superseded)** — first confirm the wiring
  actually landed (SPEC-1831 `seed_default_alert_rules()` startup wiring; SPEC-1833 Cosmos readiness
  propagation). If a spec is marked `implemented` but the wiring is genuinely absent, flag that as a
  spec-status defect instead of withdrawing.
- `agent-red-bridge-dispatcher-deferral-enforcement-implementation` → **DEFERRED** (resume only in an
  explicit Agent Red application-scope session) vs **WITHDRAWN** if obsolete — owner's choice.
Clearing these shrinks the Prime-actionable NO-GO backlog from 23 → 19.

## Notes / observed gaps
- All 6 reliability WIs return `get_project_work_item_membership = None` — open defects not formally
  linked into a project membership row (hygiene gap; does not block revising their threads).
- A REVISED still needs LO re-review, which is **suppressed while an interactive Prime session is
  active** (active-session-suppression contract). Filing REVISED still clears Prime's actionable
  queue and tees up the next LO pass.
- 2026-06-18 SessionStart observed the programmatic startup service **degraded** (exit 1 in
  `scripts/session_self_initialization.py` → `write_dashboard_and_report`). Candidate hygiene WI.
