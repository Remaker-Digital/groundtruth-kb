# Active Work List

**Owner pre-approval:** Proceed through this list autonomously. For each item:
propose via bridge → wait for Codex GO → implement → post-impl report → wait for Codex VERIFIED → commit → drop from list.

Do not wait for owner approval between items. Continue unsupervised.

---

## Next Actionable Items (hand-maintained; automation tracked under GTKB-GOV-BACKLOG-DISCIPLINE)

Updated: 2026-04-24 (S306).

| # | ID | Status | Blocks / blocked by | Next step |
|---|---|---|---|---|
| 1 | `GTKB-ISOLATION-015` **Slice 2** | awaiting Codex VERIFIED | Blocks `GTKB-ISOLATION-016`. Slice 1 VERIFIED 2026-04-24. Slice 2 implemented 2026-04-24 at `bridge/gtkb-isolation-015-slice2-work-subject-set-004.md` GO. | Codex reviewing post-impl report. |
| 2 | `GTKB-DASHBOARD-002` Slice 2.1 (visibility) | DONE pending VERIFIED | Depends on `GTKB-DASHBOARD-002` scoping VERIFIED (GO 2026-04-24 at `slice2-002.md`). No new data ingest. Implemented 2026-04-24 at `bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-006.md` GO (swimlane generator + work-subject selector + writer-side `current_work_subject` contract). | Codex reviewing post-impl report. |
| 3 | `GTKB-DASHBOARD-002` Slice 2.2 (metrics) | ready | Parallel to 2.1; independent schema change. GO condition from `slice2-002.md` F2: pin authoritative coverage/security sources (Dependabot vs pip-audit; Docker Scout scope). | File `gtkb-dashboard-industry-alignment-slice2b-metrics` implementation bridge with pinned source contract. |
| 4 | `GTKB-DASHBOARD-002` Slice 2.3 (integration) | blocked | Blocked on owner notifier-default choice (email / Slack / Teams / none). GO condition from `slice2-002.md` F2: justify any new `ci_runs` persistence against existing `testing_service_integrations`. | File `gtkb-dashboard-industry-alignment-slice2c-integration` after owner decides §5.5 notifier default. |
| 5 | `GTKB-DORA-001` | awaiting Codex VERIFIED | Blocks `GTKB-DORA-001b` and `GTKB-DORA-002`. Implemented 2026-04-24 at `bridge/gtkb-dora-telemetry-foundation-006.md` GO; post-impl report at `-007`. | Codex reviewing post-impl report. |
| 5a | `GTKB-DORA-001b` | blocked | Prerequisite for `GTKB-DORA-002`. Depends on `GTKB-DORA-001` VERIFIED. | File authoritative-deployment-source proposal after `-001` VERIFIED. |
| 6 | `GTKB-GOV-PROPOSAL-STANDARDS` Slice 1 | GO (upstream impl underway) | REVISED-9 GO'd at `bridge/gtkb-gov-proposal-standards-slice1-020.md` on 2026-04-24. Blocks its own Slice 2/3/4 + `GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1`. | Upstream implementation in `groundtruth-kb/`; Agent Red adopts via `gt project upgrade` after upstream VERIFIED. |
| 7 | `GTKB-GOV-DA-ENFORCEMENT` | passive tracking | Owned upstream on `groundtruth-kb` `main`. | No local action. Adopts via `gt project upgrade` after upstream VERIFIED. |

Standing governance items (`GTKB-GOV-001` through `GTKB-GOV-010`, minus
`-007` PAUSED and `-009` VERIFIED) and `GTKB-CORE-001` / `GTKB-MASS-001`
remain below. They are not mechanically sequenced against the items above
until `GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1` lands the structured
field block with typed `depends_on`.

**Known tracking-freshness caveat:** "TOP" as a priority value is
currently overloaded across ~10 entries below (many are historical artifacts
from earlier sessions). The 5-row table above reflects the current actionable
ordering; the file-wide priority text is not trustworthy until
`GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1` mechanically validates it.

---

## Completed During Current Session

### GTKB-GOV-000 — DONE — Implement strict formal artifact approval gate with scoped auto-approval mode

**Priority:** TOP. Owner decision `DELIB-0835` and formal records `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, `ADR-ARTIFACT-FORMALIZATION-GATE-001`, and `DCL-ARTIFACT-APPROVAL-HOOK-001` require GT-KB artifact formalization to bias toward strict review, full native-format display, approval or acknowledgement evidence, and rich auditability.

**Outcome:** implemented a tracked `PreToolUse` hook at `.claude/hooks/formal-artifact-approval-gate.py`, registered it in `.claude/settings.json`, added manual approval and scoped auto-approval packet validation, and wired `tests/hooks/test_formal_artifact_approval_gate.py` into `scripts/release_candidate_gate.py`.

**Regression visibility:** `tests/hooks/test_formal_artifact_approval_gate.py` covers blocked unapproved writes, approved writes, scoped auto-approval writes, and rejection of auto-approval flows that omit transcript capture. `tests/scripts/test_groundtruth_governance_adoption.py` verifies the hook registration, MemBase records, work-list record, and release-candidate gate wiring.

**Verification:** formal records promoted to `verified` after implementation. Approval packet: `.groundtruth/formal-artifact-approvals/2026-04-20-strict-gov-enforcement-verified.json`.

### GTKB-GOV-000A — DONE — Add Codex hook parity package and Windows-aware verifier

**Priority:** TOP follow-on to `GTKB-GOV-000`. Owner accepted the Codex runtime limitation that hooks are currently disabled on Windows, while directing that strict GOV enforcement still be made mechanically active to the extent possible for Codex.

**Outcome:** added tracked Codex hook intent at `.codex/config.toml` and `.codex/hooks.json`, registering the same formal artifact approval `PreToolUse` gate for future/non-Windows Codex hook runtimes. Added `scripts/check_codex_hook_parity.py` as the mechanically active Windows fallback verifier.

**Regression visibility:** `tests/scripts/test_codex_hook_parity.py` verifies the Codex package and documents the Windows runtime limitation. `tests/scripts/test_groundtruth_governance_adoption.py` verifies the package is present, not git-ignored, and wired into the release-candidate gate. `scripts/release_candidate_gate.py` now runs `check_codex_hook_parity.py` before the governance pytest lane.

**Decision capture:** owner acknowledgement recorded as `DELIB-0836`. Approval packet: `.groundtruth/formal-artifact-approvals/2026-04-20-codex-hook-parity-decision.json`.

### GTKB-GOV-000B — DONE — Audit and formalize session decisions across artifacts

**Priority:** TOP follow-on to owner request. Owner asked to ensure all decisions, directives, and principles in this session were identified and applied to their respective artifacts.

**Outcome:** added `DELIB-0837` and MemBase records `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`, `GOV-GTKB-ADOPTION-ENFORCEMENT-001`, `GOV-ACTING-PRIME-BUILDER-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`, `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`, `GOV-AGENT-RED-GTKB-CONFORMANCE-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, and `GOV-SESSION-FORMALIZATION-AUDIT-001`.

**Regression visibility:** `tests/scripts/test_groundtruth_governance_adoption.py` verifies the new MemBase records, the DELIB-to-spec mapping, the audit entry, and rule references.

**Approval packet:** `.groundtruth/formal-artifact-approvals/2026-04-20-session-formalization-audit-batch.json`.

### GTKB-GOV-000C — DONE — Formalize standing backlog as governed cross-session work authority

**Priority:** TOP follow-on to owner approval. Owner approved formalizing the standing backlog and asked whether the formalized artifact will be treated in the same way specifications are.

**Outcome:** added `DELIB-0838` and MemBase records `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001`, and `DCL-STANDING-BACKLOG-SCHEMA-001`.

**Clarification:** the standing backlog governance contract is treated like other formal GT-KB specifications: represented in MemBase, linked to DA, cited in rules, regression-tested, and release-gate visible. Individual backlog entries remain queue/work items unless separately promoted to GOV, SPEC, PB, ADR, DCL, or another formal artifact type.

**Regression visibility:** `tests/scripts/test_groundtruth_governance_adoption.py` verifies the standing backlog records, the `DELIB-0838` decision, rule references, and work-list continuity evidence.

**Approval packet:** `.groundtruth/formal-artifact-approvals/2026-04-20-standing-backlog-formalization.json`.

### GTKB-GOV-000D - DONE - Formalize artifact-oriented development governance

**Priority:** TOP follow-on to owner approval. Owner directive 2026-04-22: default system behavior should be oriented toward artifacts and plans, with the AI biased toward capturing deliberations, adding planned work to the standing backlog, treating agreed plans as artifacts, and starting sessions by examining artifact state.

**Outcome:** added `DELIB-0874` and MemBase records `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`. Updated `independent-progress-assessments/CODEX-STANDING-PRIORITIES.md` with a session-loaded Artifact-Oriented Governance directive covering capture thresholds, lifecycle states, and non-intrusive confirmation flows.

**Clarification:** artifact-oriented governance is a default interpretation stance, not permission to mutate formal artifacts without approval. Brainstorming remains lightweight until it becomes a decision, plan, requirement, risk, procedure, review finding, or accepted future work. Formal GOV, SPEC, PB, ADR, DCL, and Deliberation Archive mutations still require applicable approval evidence.

**Regression visibility:** `tests/scripts/test_groundtruth_governance_adoption.py` verifies the new MemBase records, `DELIB-0874`, the approval packet, the standing-priorities directive, and this work-list continuity evidence.

**Approval packet:** `.groundtruth/formal-artifact-approvals/2026-04-22-artifact-oriented-governance.json`.

### GTKB-GOV-011 - DONE - Implement session self-initialization dashboard, startup disclosure, and proactive wrap-up

**Priority:** TOP. Owner directive `DELIB-0840` and records `GOV-SESSION-SELF-INITIALIZATION-001`, `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`, `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`, and `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` required fresh sessions to self-initialize with explicit role, governance, dashboard, priority, and token-budget context. Owner directive `DELIB-0841` and records `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001`, `PB-SESSION-WRAP-UP-PROACTIVE-001`, and `DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001` added proactive session wrap-up guidance and priority engagement.

**Outcome:** implemented `scripts/session_self_initialization.py`, which generates a startup model, live local dashboard (`docs/gtkb-dashboard/index.html`), dashboard data (`docs/gtkb-dashboard/dashboard-data.json`), startup report, proactive wrap-up report, and bounded time-series KPI history (`memory/gtkb-dashboard-history.json`). `.claude/settings.json` now registers `SessionStart` and `Stop` lifecycle hooks. `.codex/hooks.json` carries matching Codex hook intent, with Windows runtime limitations covered by `scripts/check_codex_hook_parity.py`. The startup report presents the role being assumed, enabled skills, plug-ins, directives, hooks, governance stance, live project dashboard link, three top priority user actions, and token-budget reduction options. The proactive wrap-up report draws attention to priorities across project dimensions and points to `.claude/skills/kb-session-wrap/SKILL.md` without performing mutating wrap-up operations automatically.

**Regression visibility:** `tests/scripts/test_session_self_initialization.py` verifies startup disclosure text, dashboard-link availability, KPI inventory, top-three action selection, wrap-up reporting, and token-budget/reduction-option reporting. `tests/scripts/test_codex_hook_parity.py`, `tests/scripts/test_groundtruth_governance_adoption.py`, and `tests/scripts/test_release_candidate_gate.py` verify lifecycle hook intent and release-gate wiring. Approval packets: `.groundtruth/formal-artifact-approvals/2026-04-20-session-lifecycle-engagement-principle.json` and `.groundtruth/formal-artifact-approvals/2026-04-20-gtkb-gov-011-implementation-verification.json`.

### AR-DASH-001 — DONE — Correct dashboard scope to Agent Red product state

**Priority:** TOP. Owner clarification 2026-04-20: the dashboard should show the Agent Red project, with GT-KB treated retroactively as pre-existing implementation infrastructure used to implement Agent Red.

**Outcome:** updated `scripts/session_self_initialization.py` so the generated dashboard is titled "Agent Red Project Dashboard", carries `agent_red_v1` scope metadata, filters primary KPI counts through an Agent Red scope classifier, excludes GT-KB framework/upstream work from primary dashboard metrics, and reports GT-KB only in a subordinate "Implementation Infrastructure" section. Historical Agent Red project rows are backfilled from `groundtruth.db` version history with `scope_confidence="agent_red_inferred"`; current live rows use `scope_confidence="agent_red_current_heuristic"`. Mixed-scope pre-existing dashboard history rows are no longer reused.

**Historical harvest:** `memory/gtkb-dashboard-history.json` now contains Agent Red-scoped historical rows from `2026-02-26` through the current session. The rendered dashboard currently exposes 56 session points and 54 calendar-day points. Historical rows intentionally leave unavailable operational metrics as `None` rather than inventing drift, release-blocker, or bridge-contention history.

**Regression visibility:** `tests/scripts/test_session_self_initialization.py` asserts the Agent Red title, scope metadata, historical backfill rows, infrastructure/product separation, and exclusion of upstream GT-KB dashboard priorities. `tests/scripts/test_groundtruth_governance_adoption.py` continues to verify dashboard artifact presence and release-gate wiring.

**Verification:** `python -m pytest tests\scripts\test_session_self_initialization.py -q --tb=short` passed. `python -m pytest tests\scripts\test_groundtruth_governance_adoption.py -q --tb=short` passed with one unrelated ChromaDB deprecation warning. Browser runtime verification found 6 tiles, 5 signals, 8 sparklines, 2 composite lines, 160 heatmap cells, 56 session points, 54 calendar-day points, and 0 page errors.

**Formal artifact note:** no DA/GOV/SPEC/PB/ADR/DCL records were created or mutated in this implementation pass. The owner clarification is enforced in code, tests, dashboard data, and this standing-backlog record; formal canonical promotion remains available as a separate approval-gated follow-up if desired.

### GTKB-GOV-005 - DONE - Reconcile live bridge GO/NO-GO entries into standing backlog dispositions

**Priority:** TOP. Standing backlog source audit found six latest bridge entries with `GO` or `NO-GO` status in `bridge/INDEX.md`.

**Outcome:** reconciled every live bridge entry into an explicit standing-backlog disposition without mutating the file-bridge audit trail:

- `gtkb-azure-cicd-gates` `GO` is assigned to `GTKB-GOV-009` for execution or owner-approved supersession/deferment in the `groundtruth-kb` checkout.
- `agent-red-bridge-dispatcher-deferral-enforcement` `GO` is scope-only and is superseded by the follow-on implementation thread tracked by `GTKB-GOV-008`; it does not authorize direct implementation.
- `agent-red-bridge-dispatcher-deferral-enforcement-implementation` `NO-GO` is assigned to `GTKB-GOV-008` for a revised implementation bridge covering shared parser status recognition, guard tests, generated-wrapper verification, and owner-decision gates.
- `commercial-readiness-spec-1831-startup-wiring` `NO-GO` is assigned to `GTKB-GOV-007` for a revised bridge that seeds the alert-engine/provider-admin rule store or formally revises the spec.
- `commercial-readiness-spec-verification` `NO-GO` is assigned to `GTKB-GOV-007` for a revised SPEC-1832 bridge covering post-auth middleware 403 audit, SPEC-1837 archival semantics, and exact post-apply KB assertions.
- `commercial-readiness-spec-1833-ready-propagation` `NO-GO` is assigned to `GTKB-GOV-007` for a revised bridge requiring exact HTTP 503 readiness behavior, cache-isolated route tests, and no premature `verified` promotion while concurrency remains unresolved.

**Evidence report:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STANDING-BACKLOG-BRIDGE-DISPOSITIONS-2026-04-20.md`.

**Regression visibility:** `scripts/audit_standing_backlog_sources.py` still reports the live bridge entries by design; child backlog items `GTKB-GOV-007`, `GTKB-GOV-008`, and `GTKB-GOV-009` preserve actionability until the underlying bridge threads are revised, executed, deferred, or superseded.

### GTKB-GOV-006 - DONE - Close Agent Red release-readiness blocker list

**Priority:** TOP. `memory/release-readiness.md` listed governed release blockers that had to be closed, explicitly deferred with owner approval, or superseded before a production GO.

**Outcome:** owner-disposition blockers for credential lifecycle, secret-history purge, and release-branch provenance were closed. The commercial durability scope question was resolved as in-scope, then implemented with durable commercial-state persistence and secure tenant backup/restore support for Shopify, Stripe, integration framework state, and action-executor HITL state.

**Regression visibility:** `scripts/release_candidate_gate.py` now includes the commercial durability tests. Local non-deploying release gate passed with frontend skipped: `python scripts/release_candidate_gate.py --skip-frontend`.

### GTKB-GOV-012 - DONE - Enforce Prime Builder / Loyal Opposition proposal and verification gates across GT-KB applications

**Priority:** TOP for the 2026-04-22 Prime Builder session. Owner directive 2026-04-22 required the established Prime Builder / Loyal Opposition development pattern to be mechanically enforced or strongly encouraged for all applications developed with GT-KB.

**Outcome:** the portable file-bridge proposal/gate slice completed the governed bridge lifecycle: proposal `bridge/gtkb-proposal-verification-gates-001.md`, Loyal Opposition `GO` in `bridge/gtkb-proposal-verification-gates-002.md`, post-implementation reports in `bridge/gtkb-proposal-verification-gates-003.md` and `bridge/gtkb-proposal-verification-gates-005.md`, a `NO-GO` in `bridge/gtkb-proposal-verification-gates-004.md`, and final `VERIFIED` in `bridge/gtkb-proposal-verification-gates-006.md`.

**Post-verification spec-status review:** `gt bridge spec-review --scope protocol` now surfaces the affected governance records `GOV-GTKB-ADOPTION-ENFORCEMENT-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`, `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`, and `GOV-AGENT-RED-GTKB-CONFORMANCE-001`. Existing MemBase and regression-test evidence show those records are already `verified`; no formal GOV/SPEC mutation was made in this backlog cleanup pass.

**Evidence report:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-GOV-012-POST-VERIFIED-STATUS-REVIEW-2026-04-22.md`.

**Residual gate visibility:** `gt bridge gate --require-verified --scope protocol --json` still fails on older protocol entries with latest non-verified states. Current notable continuation items include `gtkb-mass-adoption-first-commit-package` awaiting renewed Loyal Opposition review and `gtkb-core-spec-intake` at scope GO. `gtkb-azure-cicd-gates` is now `VERIFIED` at `bridge/gtkb-azure-cicd-gates-010.md`, and `gtkb-core-spec-intake-phase3b-answer` is also `VERIFIED`. These are not regressions in `GTKB-GOV-012`; the remaining non-verified entries are bridge-continuation work items for `GTKB-MASS-001` and `GTKB-CORE-001`.

## Active Items

**Owner directive 2026-04-23:** treat the overall application/GT-KB isolation
program as the current standing-backlog priority. Until `GTKB-ISOLATION-019`
is complete or the owner explicitly pauses or reprioritizes the program,
non-isolation items below are deferred except for bridge or governance work
that directly unblocks the isolation program.

### GTKB-ISOLATION-010 - DONE - Execute Phase 7 foundation slice: work-subject state and resolved-root guardrails

**Status:** DONE 2026-04-23 (S305). **VERIFIED** at
`bridge/gtkb-work-subject-root-enforcement-implementation-020.md`. Superseded
by `GTKB-ISOLATION-015` which continues Phase 7 integration beyond the
foundation slice.

**Priority (historical):** TOP. This was the first concrete execution slice
already entered on the live bridge in
`bridge/gtkb-work-subject-root-enforcement-implementation-001.md`,
and it should lead the queue because later environment, service, control-plane,
overlay, and migration work need stable work-subject state, root
classification, and startup/hook language first.

**Required outcome:** obtain bridge GO, implement, verify, and Loyal
Opposition-verify the narrow Phase 7 foundation slice: canonical
`.claude/session/work-subject.json` state, one-window legacy migration and
alias support, resolved-root classification for application/current-repo
bridge-governance/GT-KB product targets, subject-aware mutation guardrails, and
startup/hook/report language changes from `focus` to `work subject`.

**Regression visibility:** targeted checks in
`tests/hooks/test_workstream_focus.py`,
`tests/scripts/test_session_self_initialization.py`, and
`tests/scripts/test_codex_hook_parity.py`, followed by broader `tests/hooks/`
and `tests/scripts/` lanes once the focused slice is green.

### GTKB-ISOLATION-011 - DONE - Implement Phase 3 environment boundary baseline

**Status:** DONE 2026-04-23 (S305). **VERIFIED**; Windows drive-letter
compose-bind fix landed via REVISED-1. See
`bridge/gtkb-environment-boundary-baseline-implementation-*` thread.

**Priority (historical):** TOP after `GTKB-ISOLATION-010`.

**Bridge status:** originally proposal filed in
`bridge/gtkb-environment-boundary-baseline-implementation-001.md`;
subsequently GO'd, implemented, and VERIFIED through the REVISED cycle.

**Required outcome:** submit, obtain GO for, and land the first Phase 3
execution slice: static environment policy checker, root identity probe, safe
devcontainer/Codespaces defaults, Docker context hardening, CI subject-scope
audit, dependency-mode reporting, and bounded escape-hatch schema.

**Regression visibility:** tests must reject broad mounts, Docker socket usage,
privileged containers, GT-KB product credentials in app lanes, root-escape
writes, and unlabeled product-release claims from app CI.

### GTKB-ISOLATION-012 - DONE - Implement Phase 4 scoped GT-KB service boundary baseline

**Status:** DONE 2026-04-23 (S305). **VERIFIED** at
`bridge/gtkb-scoped-service-boundary-baseline-implementation-010.md`
(narrowed to single `dashboard.summary.read` op after 4 NO-GO rounds).

**Priority (historical):** TOP after `GTKB-ISOLATION-011`.

**Required outcome:** submit, obtain GO for, and land the first Phase 4
execution slice: scoped operation schema, app-scoped GT-KB client,
service-side GOV guard reuse, read-only dashboard summary path, DA/MemBase
app-scope layer, governed release/deployment request flow, offline/stale
protocol, and doctor/preflight checks that remove raw GT-KB DB/root access from
ordinary app flows.

**Regression visibility:** tests must prove app-subject sessions cannot perform
product-scope writes, cannot emit combined app/product green claims, and cannot
fall back silently to raw DB/root authority.

### GTKB-ISOLATION-013 - DONE - Implement Phase 5 control-plane registry and safe projection baseline

**Status:** DONE 2026-04-23 (S305). **VERIFIED** — Phase 5 first slice
landed (three-operation typed registry). Later typed
`work_subject.set` handler still open under `GTKB-ISOLATION-015` Slice 2.

**Priority (historical):** TOP after `GTKB-ISOLATION-012`.

**Required outcome:** submit, obtain GO for, and land the first Phase 5
execution slice: typed operation registry, dry-run/diff/audit/rollback
foundation, app-root allowlisted `dashboard.refresh`, bounded Markdown
operations, projection preview/apply staging, harness topology registry,
role-slot-aware bridge/control records, and pause/resume/restart request
records.

**Regression visibility:** tests must reject arbitrary path/script execution,
path traversal, unmanaged projection changes, stale counterpart topology, and
bridge writes from the wrong role slot.

### GTKB-ISOLATION-014 - DONE - Implement Phase 6 overlay and snapshot baseline

**Status:** DONE 2026-04-23 (S305). **VERIFIED** at
`bridge/gtkb-session-overlay-baseline-implementation-006.md` (required an
ImportError-not-ModuleNotFoundError fix for direct-script SessionStart).

**Priority (historical):** TOP after `GTKB-ISOLATION-013`.

**Required outcome:** submit, obtain GO for, and land the first Phase 6
execution slice: overlay manifest library, overlay builder, startup/dashboard
visibility, scanner exclusions, projection preview overlay integration,
promotion dry-run/apply through the typed registry, and retention cleanup
confined to validated overlay roots.

**Regression visibility:** tests must prove overlays are non-authoritative,
source-hashed, stale-detecting, excluded from canonical scanners by default,
and unable to copy credentials or raw `groundtruth.db` into session context.

### GTKB-ISOLATION-015 - Complete full Phase 7 work-subject/root enforcement (Slice 1 VERIFIED; Slice 2 remaining)

**Status:** **Slice 1 VERIFIED** 2026-04-24 (S306) at
`bridge/gtkb-isolation-015-phase7-full-integration-016.md`. **Slice 2
implemented 2026-04-24 (S307)** via
`bridge/gtkb-isolation-015-slice2-work-subject-set-004.md` (GO); post-impl
report filed as a new version on that thread. `GTKB-ISOLATION-015` closes
when Slice 2 VERIFIED.

**Priority:** **TOP NEXT on the isolation chain** (after Phases 3-6 + Phase
7 foundation + Phase 7 Slice 1 all VERIFIED). Unblocks `GTKB-ISOLATION-016`
Phase 8 execution.

**Required outcome:** after the Phase 3 through Phase 6 execution slices land,
submit and execute the remaining Phase 7 integration work: subject-labeled
startup/dashboard/readiness/test outputs, typed control-plane
subject/mode/session controls, overlay-aware but non-authoritative context
handling, bridge live-state writer/validator safety, Codex/Claude parity
checks, and upstream GT-KB delivery requirements for clean adopters.

**Regression visibility:** tests must prove subject-labeled outputs, live
`bridge/INDEX.md` fresh-read authority, invalid transition rejection, stale
counterpart detection, and split application vs GT-KB verification lanes.

**Slice split (established at bridge `gtkb-isolation-015-phase7-full-integration-007` REVISED-3, GO at `-008`):**

- **Slice 1 (Agent Red Tooling) — delivered via this bridge:** §A
  subject-labeled startup / readiness / test outputs, §B bridge live-state
  writer/validator (`scripts/gtkb_bridge_writer.py`), §C overlay-aware
  startup status, §E multi-harness counterpart-state detection. Post-impl
  report filed as `bridge/gtkb-isolation-015-phase7-full-integration-009.md`.
- **Slice 2 (Typed control-plane handler) — separate bridge under the same
  WI:** §D typed `work_subject.set` control-plane handler with input
  schema, timing semantics, dry-run, apply, audit, and rollback. Filed as
  a new bridge once Slice 1 is VERIFIED. `GTKB-ISOLATION-015` closes when
  Slice 2 is VERIFIED.
- **§F (Upstream GT-KB clean-adopter delivery) — routed to
  `GTKB-ISOLATION-017`:** AGENTS.md template, hook templates, and
  `gt project init/upgrade/doctor` packaging are delivered through the
  existing Phase 9 adopter-packaging backlog item. No new bridge or WI
  required.

**Execution note:** the completed Phase 1 through Phase 7 planning records
remain below as the governing design baseline for the execution queue above.

### GTKB-GOV-DA-ENFORCEMENT - Mechanical enforcement of Deliberation Archive citation discipline (re-routed to upstream)

**Priority:** passive tracking behind upstream
`gtkb-da-governance-completeness-implementation` (in `groundtruth-kb`
repo). Owner-directed 2026-04-24 during the S306 DA-effectiveness audit.

**Problem statement:** `.claude/rules/deliberation-protocol.md` mandates
Prime Builder pre-proposal DELIB search + citation in a `## Prior
Deliberations` section, pre-review DELIB search by Loyal Opposition, and
immediate archival of owner decisions as `source_type=owner_conversation`.
Audit evidence (S306, 2026-04-24): 0 of 7 Prime proposals in this session
cited DELIBs; only 1 `owner_conversation` DELIB captured despite ≥3 owner
decisions; only 12% of DELIBs have `work_item_id` linkage and 18% have
`spec_id` linkage. The protocol lives in a read-on-demand rules file with
no mechanical enforcement.

**Routing decision (2026-04-24, bridge `gtkb-gov-da-enforcement-slice1`
`-002` NO-GO + `-003` REVISED-1):** the initially proposed Agent
Red-local pre-commit hook (`.claude/hooks/require-prior-deliberations.py`)
was withdrawn because:

1. Pre-commit enforcement fires too late — the bridge INDEX entry makes
   a proposal reviewable BEFORE any commit step, so commit-time gates
   miss the hot-loop. The correct surface is author-time
   `UserPromptSubmit`.
2. GT-KB already has the canonical enforcement artifacts reserved under
   `gtkb-da-governance-completeness-implementation`: `delib-preflight-gate.py`
   stub at `templates/hooks/`, registry entries in
   `templates/managed-artifacts.toml` with settings registrations on
   `UserPromptSubmit` + `PostToolUse`, scaffold tests in
   `tests/test_scaffold_settings.py`. Prior bridge decision
   `agent-red-session-wrap-automation-004.md` rules this work must route
   through that thread to avoid duplicate authority.
3. The proposed wiring file (`scripts/pre_commit/run_quality_guardrails.py`)
   does not exist in either Agent Red or groundtruth-kb.

**Required outcome:** implementation is owned upstream. Agent Red
receives the enforcement through GT-KB scaffold + upgrade, not via a
local hook. When the upstream thread
`gtkb-da-governance-completeness-implementation` VERIFIED, Agent Red
runs `gt project upgrade` (or equivalent) to pull the hooks, which then
fire on this repo's `UserPromptSubmit` / `PostToolUse` events per the
managed-artifacts.toml registrations.

**Interim Agent Red override:** none planned by default. If the owner
decides an interim local override is needed before upstream lands, it
would be filed as a new bridge proposal (candidate approach: extend the
existing `.claude/hooks/formal-artifact-approval-gate.py` which already
runs on `UserPromptSubmit`). Not scheduled at time of this entry.

**Tracking (updated 2026-04-24 per bridge `-008` NO-GO F1):** upstream
`gtkb-da-governance-completeness-implementation-016` **GO recorded
2026-04-18** (no blocking findings), per `release-notes-0.6.1.md:140` and
`.implementation-log-gtkb-da-governance-completeness.md:3-5` in the
`groundtruth-kb` repo. Implementation is **active on `main`** (prior
checks were on `feature/ownership-matrix` but the work has since advanced
to `main` with additional landing commits per
`.implementation-log-gtkb-da-governance-completeness.md:691-710,2548-2556`);
implementation surface is still outstanding. Agent Red is **awaiting
upstream implementation completion + VERIFIED**, not awaiting the GO.

**Regression visibility (deferred to upstream):** upstream scaffold
tests already assert the hook presence. Post-upgrade Agent Red sessions
will see DELIB search/citation enforcement on `UserPromptSubmit` and
owner-decision archival on `PostToolUse`.

### GTKB-DASHBOARD-001 - DONE - Dashboard industry-alignment Slice 1

**Status:** **VERIFIED** 2026-04-24 (S306) at
`bridge/gtkb-dashboard-industry-alignment-slice1-008.md`. Filed,
implemented, reviewed, and closed in a single session. Unblocks
`GTKB-DASHBOARD-002`.

**Priority (historical):** filed + implemented 2026-04-24 on owner
direction after the S306 dashboard review.

**Required outcome:** three-item slice delivered per bridge
`gtkb-dashboard-industry-alignment-slice1-006` GO:

1. Progressive-enhancement landing page at `docs/gtkb-dashboard/index.html`
   with fetch-driven KPI snapshot + age badge + explicit open-live button;
   no auto-redirect. Dark-mode fallback via `prefers-color-scheme`.
2. Per-panel freshness secondary value (target `F`) on every stat panel
   except "Refresh Age" itself, sourced from the existing
   `SELECT ... FROM refresh_runs` pattern already used by the generator.
3. Alert-rule skeleton under
   `docs/gtkb-dashboard/grafana/provisioning/alerting/` anchored to
   authoritative `current_metrics` keys (`release_blockers`,
   `ci_testing_failing`) and the `refresh_runs` freshness SQL. Validator
   test asserts exact literals and runs a live refresh fixture to prove
   the keys are actually emitted by the pipeline.

**Regression visibility:** `tests/scripts/test_gtkb_dashboard_grafana.py`
4 panel tests; `tests/scripts/test_gtkb_dashboard_alerting.py` 7 tests
covering structure, exact-literal anchoring, schema-anchored SQL, and
live-emission proof.

**Slice 2/3 follow-ons:** filed if approved — bridge swimlane panel,
work-subject selector, coverage/security/CI panels, alert-notifier
wiring (Slice 2); SLO/error-budget, flow metrics, PR/branch health,
incident/MTTR (pending `gtkb-dora-telemetry-foundation`), remote
exposure, WCAG audit (Slice 3).

### GTKB-DASHBOARD-002 - Dashboard industry-alignment Slice 2 (scoped into 2.1 / 2.2 / 2.3)

**Priority:** after `GTKB-DASHBOARD-001` VERIFIED. Scoping proposal
`bridge/gtkb-dashboard-industry-alignment-slice2-001.md` GO'd at `-002.md`
on 2026-04-24. Sub-slice breakdown below is the approved scope; each
sub-slice ships as its own implementation bridge.

**Approved sub-slice breakdown (from `slice2-001.md` §2, GO'd at `slice2-002.md`):**

- **Slice 2.1 — Visibility (no new data ingest).** Thread:
  `gtkb-dashboard-industry-alignment-slice2a-visibility`. Deliverables:
  bridge-state swimlane panel (per-thread latest status + age-in-state)
  and work-subject selector (Application vs GT-KB scope toggle). Status:
  **ready** — no external dependencies, reuses Slice 1 refresh pipeline.
- **Slice 2.2 — Metrics ingest (new data sources).** Thread:
  `gtkb-dashboard-industry-alignment-slice2b-metrics`. Deliverables:
  coverage trend panel (line + branch, over time) and security posture
  panel (open CVEs via Dependabot / pip-audit / Docker Scout). Status:
  **ready** — parallel to 2.1, independent schema change. GO condition
  from `slice2-002.md` Finding 2: implementation bridge must pin
  authoritative fetch/persist paths (no assumption of local `.coverage`
  or `coverage.xml`; explicit Dependabot-vs-pip-audit authority; Scout
  auth/source or deferred).
- **Slice 2.3 — External integration.** Thread:
  `gtkb-dashboard-industry-alignment-slice2c-integration`. Deliverables:
  CI workflow embed (GitHub Actions latest-runs) and alert-routing
  notifier wiring (email / Slack / Teams). Status: **blocked on owner
  notifier-default decision** (`slice2-001.md` §5.5). GO condition from
  `slice2-002.md` Finding 2: implementation bridge must justify any new
  `ci_runs` persistence against the existing `testing_service_integrations`
  / GitHub-run model already persisted by
  `scripts/session_self_initialization.py:1786-2053` and
  `scripts/gtkb_dashboard/refresh_dashboard_db.py:519-568`.

**Sequencing:** 2.1 and 2.2 can ship in either order or in parallel. 2.3
waits on owner notifier choice; 2.3 does not block 2.1 or 2.2.

**Regression visibility (per sub-slice bridge):** each extends
`tests/scripts/test_gtkb_dashboard_grafana.py` and
`tests/scripts/test_gtkb_dashboard_alerting.py` with pinned assertions
against authoritative pipeline outputs; 2.2 carries a schema-migration
non-regression test; 2.3 carries contract tests against the Grafana
alerting API fixtures. Each sub-slice bridge declares its own full
verification matrix at filing time.

### GTKB-DASHBOARD-003 - Dashboard industry-alignment Slice 3 (SLO, flow metrics, PR health, incident/MTTR, remote exposure, WCAG)

**Priority:** after `GTKB-DASHBOARD-002` VERIFIED and after
`GTKB-DORA-001` lands the prerequisite telemetry.

**Required outcome:** SLO / error-budget model with burn-rate alerts; flow
metrics with WIP aging; branch / PR health panel; incident / on-call /
MTTA / MTTR panel (depends on `incidents` table from `GTKB-DORA-001`);
remote read-only dashboard exposure path (snapshot URL or auth gateway);
WCAG 2.1 AA accessibility audit applying the same bar the app's CI already
gates.

**Regression visibility:** SLO burn-rate alert fires against fixture data;
flow metrics recomputed from live refresh history; PR panel reads GitHub
Actions / GraphQL; incident panel schema + backfill tests;
`tests/scripts/test_gtkb_dashboard_alerting.py` extended for notifier
contract; a11y audit reported against declared WCAG 2.1 AA criteria.

### GTKB-DORA-001 - DORA telemetry foundation (deployable_change + rollback/hotfix linkage + incidents table)

**Priority:** blocks any honest DORA panel (`GTKB-DORA-002`). Filed as
follow-on to the Slice 1 NO-GO `-002` Finding 3 (current
`delivery_timeline_events` has 3 production rows, 0 with commit linkage,
no rollback/hotfix linkage, no incidents table — DORA four keys cannot be
computed without fabricating semantics).

**Required outcome:** extend `scripts/gtkb_dashboard/schema.sql` with a
`deployable_change` identity column on `delivery_timeline_events` linking
commits to deployments; add rollback / hotfix linkage columns marking which
prior deploy a rollback targets; add an `incidents` table with
detect / mitigate / close timestamps and incident-to-deploy linkage;
extend `scripts/gtkb_dashboard/refresh_dashboard_db.py` to populate the new
columns; backfill existing events where possible.

**Regression visibility:** schema migration test; refresh-pipeline test
emits the new columns for sample events; fixture tests for each of the
four DORA keys' input shapes (deployment frequency, lead time, change
failure rate, MTTR) so downstream `GTKB-DORA-002` can compute honestly.

### GTKB-DORA-002 - DORA four-keys panels (consumer of GTKB-DORA-001)

**Priority:** after `GTKB-DORA-001` VERIFIED. Strictly no DORA panels
before the telemetry foundation lands.

**Required outcome:** four stat panels computing deployment frequency
(last 30d), lead time for changes (median, last 30 deploys), change
failure rate (% requiring hotfix or rollback within 24h, last 90d), and
MTTR (median incident-detect to incident-close, last 90d). Nulls with
annotations where data is insufficient; no fabrication.

**Regression visibility:** extends `test_gtkb_dashboard_grafana.py` with
pinned assertions for the four panels; fixture-refresh against a seeded
telemetry DB confirms each query returns the expected shape.

### GTKB-DASHBOARD-RETENTION - Dashboard history retention policy (contingent)

**Priority:** contingent — only filed if `MAX_HISTORY=200` at
`scripts/gtkb_dashboard/refresh_dashboard_db.py:346-349` ever proves
insufficient for a diagnostic or review workflow. Currently bounds history
to ~10 hours at the 3-minute snapshot cadence, which suffices for all
observed use cases.

**Required outcome (if triggered):** add env-configurable
`GTKB_DASHBOARD_HISTORY_MAX_ROWS` and optional time-based
`GTKB_DASHBOARD_HISTORY_RETENTION_DAYS` expiry in `_append_snapshot`;
preserve the row cap as the primary bound; document the new env knobs in
`docs/gtkb-dashboard/grafana/README.md`.

**Regression visibility:** boundary test proves snapshots within the
retention window are preserved exactly and older ones are removed.

### GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1 - Backlog schema linter + bridge→backlog citation gate (upstream-routed)

**Priority:** file after the current S306 governance bundle
(`GTKB-GOV-PROPOSAL-STANDARDS` + `GTKB-GOV-DA-ENFORCEMENT`) has at least
Slice 1 VERIFIED. Owner-approved 2026-04-24 after the S306
DA-effectiveness + backlog-usage audit.

**Problem statement (from S306 audit):**

| Weak-use pattern observed | Evidence |
|---|---|
| Bridge filed before backlog entry exists | `gtkb-gov-da-enforcement-slice1-001` cited `GTKB-GOV-DA-ENFORCEMENT (new standing-backlog item)` — entry was created *in the same commit*, not before. |
| Follow-on items buried in parent prose | Slice 2/3/4 of DASHBOARD-001 and PROPOSAL-STANDARDS existed only in parent-entry narrative until owner asked; 8 items promoted to top-level this session. |
| State never transitions automatically | `GTKB-ISOLATION-015` stayed "in flight" through 16 bridge rounds with no automatic state change. |
| DONE entries accumulate | ~40% of `work_list.md` is DONE at time of filing. |
| Dependencies aspirational | "after GTKB-DORA-001" is prose; nothing refuses work that violates the order. |

**Required outcome (upstream, as new managed hook family parallel to
`hook.bridge-proposal-standards`):**

- `hook.backlog-cite-gate` — pre-commit + `PreToolUse(Write,Edit)` hook:
  every `bridge/*-001.md` NEW file must carry a `**Work item:** <ID>`
  line; `<ID>` must exist in `work_list.md` **before** the commit lands
  (not in the same commit). Escape hatch: `[backlog-exempt: <reason>]`
  commit-message tag with audit-log write.
- `hook.backlog-schema-linter` — pre-commit hook validating every
  `work_list.md` entry has required fields (`status`, `priority`,
  `filed`, `last_changed`) with enum values, unique IDs, and resolvable
  `depends_on` references. Rejects commits that introduce drift.
- Structured field block per entry (to enable A3 validation): consistent
  5-field header after the entry title.
- `work_list.md` split into active + `work_list_done.md` archive so
  session-start only loads active entries.
- Top-of-file TOC table listing `| ID | Status | Priority | Title |
  Depends on |` for all active items, auto-regenerated on edit.

**Regression visibility (deferred to upstream):** upstream scaffold
tests assert hook presence; upstream hook tests cover citation-gate
behavior (existing-ID pass, new-same-commit-ID rejected, exempt tag
permitted with audit-log side effect) and schema-linter behavior
(missing field, wrong enum, unresolved `depends_on`, duplicate ID).

### GTKB-GOV-BACKLOG-DISCIPLINE-SLICE2 - Backlog state automation + ordering-freshness enforcement (upstream-routed)

**Priority:** file after `GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1` VERIFIED.

**Required outcome (upstream):**

- `hook.backlog-last-changed` — `PostToolUse(Write,Edit)` on
  `work_list.md`: if an entry body changed but `last_changed` did not,
  auto-update it. Agents don't have to remember.
- Bridge state transition automation: when a bridge post-impl `NEW` file
  is filed referencing a backlog entry, auto-set entry
  `status: awaiting-verification`. When the thread reaches `VERIFIED`,
  auto-set `status: done` and move the entry to `work_list_done.md`.
  Implementation: script run by the same session-start / bridge-poller
  path that does other bridge maintenance.
- Dependency-violation warning: when a bridge `NEW` proposal references
  an entry whose `depends_on` is not yet `done`, surface a warning (not
  a block). Prevents silent ordering mistakes.
- **Ordering-freshness validation (added per owner S306 direction):**
  - Session-start / pre-commit check flags any entry whose `status` is
    `in-flight` or `ready` but whose latest referenced bridge thread
    has since reached `VERIFIED`. Caught the stale "TOP after Phase 3
    VERIFIED" state for `GTKB-ISOLATION-011` through `-014` and the
    "in flight" state on `GTKB-DASHBOARD-001` in the S306 audit. Would
    have prevented ~10 minutes of manual hygiene.
  - Flags entries whose `priority:` text still says "TOP after X" when
    X is now `done`. Auto-suggest rewrite (still blocks commit pending
    human confirm — never silently rewrites priority text).
  - Flags "TOP" overload: if more than N entries carry priority=`TOP`
    simultaneously, warn and require the author to resolve sub-ordering
    before committing.
  - Regenerates the top-of-file "Next Actionable Items" table on commit
    (sorted by typed priority + dependency graph). Drift between the
    table and the structured field blocks fails the commit.

**Regression visibility (deferred to upstream):** upstream regression
that seeds entries with mis-transitioned states and asserts the
automation corrects them; dependency-violation warning fires on a
fixture where a parent is in-flight; ordering-freshness validator fires
on a fixture where a status=`in-flight` entry's bridge thread has reached
`VERIFIED`; TOP-overload warning fires when `N+1` entries carry
`priority=TOP`; next-actions table is regenerated deterministically from
the structured field blocks.

### GTKB-GOV-PROPOSAL-STANDARDS - Mechanical enforcement of proposal structure (upstream-routed)

**Priority:** parallel to upstream
`gtkb-da-governance-completeness-implementation`; adoption follows next
`gt project upgrade` after upstream VERIFIED. Filed 2026-04-24 after
applying the routing lesson from the withdrawn `GTKB-GOV-DA-ENFORCEMENT`
slice.

**Problem statement:** 11 of 14 NO-GO findings this S306 session would
have been caught by mechanical checks on proposal structure — missing
scope boundaries, TBD cells in Verification Matrix, unverified test
claims, wrong follow-on WI IDs, non-existent path names, forked
enforcement families. None of `.claude/rules/file-bridge-protocol.md` or
the observed structure (Verification Matrix / Files Touched /
Out-of-Scope / Decision-Needed / Cross-NO-GO Discipline / Test Evidence)
is mechanically enforced. A documentation-only rule does not survive
high-velocity proposal drafting.

**Routing decision (2026-04-24, filed bridge
`gtkb-gov-proposal-standards-slice1-001`):** implementation owned
upstream in `groundtruth-kb` as a new managed artifact
`hook.bridge-proposal-standards`, paralleling the existing
`hook.bridge-compliance-gate`, `hook.delib-preflight-gate`, and
`hook.owner-decision-capture` family. Agent Red does not own any new
hook file; it receives enforcement through `gt project upgrade` when
upstream VERIFIED.

**Adoption contract (REVISED-9 GO'd at
`bridge/gtkb-gov-proposal-standards-slice1-020.md` on 2026-04-24):**

- **Event model:** two separate managed-hook registrations — (1)
  `PreToolUse` on `Write` as the authoritative pre-block for new-file
  authoring, validating `tool_input.content` directly; (2) `PostToolUse`
  on `Edit` as the authoritative final-state gate for edits, reading
  post-edit disk content via `_resolve_edit_path(file_path, cwd)` which
  resolves relative `tool_input.file_path` against payload `cwd`
  (mirrors `templates/hooks/delib-search-tracker.py:215,330`). Absolute
  paths pass through unchanged. Advisory `UserPromptSubmit` hook is a
  separate non-authoritative file.
- **Body-status-token rule:** forward-looking MUST in
  `templates/rules/file-bridge-protocol.md` — newly authored
  `bridge/<slug>-NNN.md` files begin their body with exactly one of
  `NEW`/`REVISED`/`GO`/`NO-GO`/`VERIFIED`. Files whose current first
  body line is non-canonical are grandfathered (hook `emit_pass` with
  diagnostic); heading-first or blank-first-line new-file writes BLOCK.
- **Post-impl discriminator:** metadata-driven via
  `parse_bridge_metadata(content).bridge_kind == "implementation_report"`
  → requires `## Test Evidence` section containing a fenced pytest
  block matching `\d+\s+passed`. Closes the -014 F1 loophole where a
  later `Edit` could add `bridge_kind: implementation_report` without
  adding the evidence section.
- **Output-builder addition:** new `emit_block_post(reason: str) -> None`
  helper in `src/groundtruth_kb/governance/output.py` emitting
  `{"decision": "block", "reason": ...}` (PostToolUse structured block
  shape, distinct from `emit_deny`'s PreToolUse
  `hookSpecificOutput.permissionDecision="deny"` shape). Preserves the
  canonical "no hook constructs raw JSON dicts directly" rule.
- **Bypass:** env var `GTKB_PROPOSAL_STANDARDS_BYPASS=<reason>` OR
  content marker `<!-- bridge-standards-exempt: <reason> -->` in the
  first 100 lines; audit log at
  `.claude/audit/proposal-standards-bypass.log`. Applies to both Write
  and PostToolUse(Edit) block paths.
- **Windows `.codex` fallback parity:** standalone
  `scripts/check_bridge_proposal_standards.py` accepting
  `--event write --path <target>` or
  `--event edit --path <target> [--cwd <cwd>]`; shares the
  `_resolve_edit_path` helper with the hook. 22-fixture parity test
  (16 Write + 6 PostToolUse(Edit), including the two new
  `cwd`-resolution fixtures added in REVISED-9 per -018 F2).
- **Zero shared-parser drift:** the hook consumes `parse_bridge_metadata`,
  `BRIDGE_KINDS`, `_blocking_metadata_violations` read-only; only
  `governance/output.py` is mutated upstream, and only additively
  (new function, no signature change to existing helpers).

**Follow-on slices (filed after Slice 1 VERIFIED):**

- `gtkb-gov-proposal-standards-slice2` — test-claim re-run verifier
  (parses claimed pytest output blocks in post-impl reports and re-runs
  the same commands, failing when real output diverges).
- `gtkb-gov-proposal-standards-slice3` — work-item-ID collision gate
  (cross-references proposed follow-on WI IDs against `work_list.md` to
  prevent routing to an already-assigned slot, e.g. Phase 7 `-006`
  caught routing §D to -016 which was already Phase 8).
- `gtkb-gov-proposal-standards-slice4` — `/gtkb-propose` skill that
  scaffolds a compliant proposal from a slug + scope dimensions,
  running `search_deliberations()` and injecting DELIB-IDs before the
  author writes any prose.

**Tracking:** awaiting upstream `groundtruth-kb` bridge filing + GO /
VERIFIED on the new hook artifact.

**Regression visibility (deferred to upstream):** upstream scaffold
tests will assert hook presence; upstream hook tests will cover the
section-requirement table enumerated in the Slice 1 proposal.

### GTKB-GOV-PROPOSAL-STANDARDS-SLICE2 - Test-claim re-run verifier

**Priority:** filed after `GTKB-GOV-PROPOSAL-STANDARDS` Slice 1 VERIFIED.

**Required outcome:** extend the upstream `hook.bridge-proposal-standards`
family with a verifier that parses claimed `pytest` output blocks in
post-implementation reports and re-runs the same commands in a fixture
environment, failing the pre-commit gate when the real output diverges
from the claimed output. Would have caught Phase 7 `-009`'s "44 tests
pass" stale claim (live was "7 failed, 16 passed").

**Regression visibility:** upstream regression that seeds a stale claim
and asserts the verifier rejects it.

### GTKB-GOV-PROPOSAL-STANDARDS-SLICE3 - Work-item-ID collision gate

**Priority:** filed after `GTKB-GOV-PROPOSAL-STANDARDS` Slice 1 VERIFIED.

**Required outcome:** pre-review hook that cross-references any
`GTKB-ISOLATION-NNN` / `GTKB-DASHBOARD-NNN` / `GTKB-GOV-NNN` mention
in a proposal against `memory/work_list.md` entries. Flags collisions
where a proposal routes deferred work to an ID already assigned to a
different item. Would have caught Phase 7 `-005`'s routing of §D to
`GTKB-ISOLATION-016` (already Phase 8 execution).

**Regression visibility:** test that a proposal citing an already-assigned
ID triggers the gate; aligned routing passes.

### GTKB-GOV-PROPOSAL-STANDARDS-SLICE4 - /gtkb-propose scaffolding skill

**Priority:** filed after `GTKB-GOV-PROPOSAL-STANDARDS` Slice 1 VERIFIED.
Lower priority than Slices 2-3 since it is convenience rather than
enforcement.

**Required outcome:** interactive skill `/gtkb-propose` that walks Prime
through a compliant proposal scaffold — slug + work-item name + slice
number + optional scope dimensions. Runs `search_deliberations()` and
injects relevant DELIB-IDs into a `## Prior Deliberations` stub.
Pre-populates all required sections with TODO placeholders. Emits a
self-review checklist before finalizing the file. Adopts upstream via
GT-KB skill scaffold.

**Regression visibility:** skill invocation test seeded with fixtures;
output file matches the required-section contract enforced by
`hook.bridge-proposal-standards`.

### GTKB-ISOLATION-001 - DONE - Create detailed Phase 1 plan: artifact authority and dependency matrix

**Priority:** TOP. Owner directive 2026-04-22: application-subject sessions must be unable by default to alter GT-KB product artifacts, while GT-KB-subject sessions may retain broader access where needed. This is the first planning phase in the application/GT-KB isolation program.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`. Completed plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md`. Deliberation capture: `DELIB-0878`.

**Outcome:** completed the detailed Phase 1 authority matrix plan. The plan defines the durable matrix schema, conventional and GT-KB authority categories, a preliminary Agent Red authority matrix, owner-decision-pending rows, implementation steps, verification mapping, risk mitigations, and dependencies into Phases 2-9.

**Required outcome:** create a detailed implementation plan for the authority matrix that classifies each GT-KB/App dependency as parent GT-KB product artifact, scoped GT-KB service, application-local governed state, session overlay, dashboard/control-plane operation, or host/container/development-environment boundary. The plan must include path/capability ownership, subject labels, owner-decision-pending legacy exceptions, and recommended authority for bridge, backlog, release-readiness, tests, DA, MemBase, hooks, rules, skills, dashboard, overlays, containers, dev environments, and CI. Apply the industry-alignment critique in the plan source: prefer conventional names, least privilege, workspace trust, generated configuration, controller reconciliation, provenance, and subject-scoped CI over novel GT-KB-only terminology.

**Regression visibility:** evidence gathered from upstream GT-KB ownership resolver/classify-tree output, `groundtruth.toml`, `tools/knowledge-db/groundtruth.toml`, `.claude/settings.json`, `.codex/hooks.json`, `.env.example`, `docker-compose.yml`, `.github/workflows/*`, `requirements-local.txt`, `requirements-test.txt`, `scripts/workstream_focus.py`, `scripts/session_self_initialization.py`, `tests/hooks/test_workstream_focus.py`, and `tests/scripts/test_groundtruth_governance_adoption.py`. This phase was planning only and did not move application or GT-KB files.

### GTKB-ISOLATION-002 - DONE - Create detailed Phase 2 plan: project root and repository topology

**Priority:** TOP after `GTKB-ISOLATION-001`. Owner proposed GT-KB root `E:\Development\GroundTruth-KB\` and application root `E:\Development\GroundTruth-KB\Applications\Agent_Red\`, with ordinary downstream users opening only the application project.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`. Completed plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-002-PHASE2-ROOT-TOPOLOGY-PLAN-2026-04-22.md`. Deliberation capture: `DELIB-0879`.

**Outcome:** completed the detailed Phase 2 topology plan. The plan recommends separate GT-KB and application repositories with package/service consumption, permits a common parent folder only as a workspace container, rejects monorepo/submodule defaults, defines Codex/Claude/VS Code/CI/git/worktree policy, specifies root-boundary verification tests, and defines the non-destructive Agent Red migration rehearsal shape.

**Required outcome:** create a detailed implementation plan comparing parent-plus-subdirectory, separate repositories, monorepo-with-root-enforcement, and package-only GT-KB consumption. The plan must specify Codex/Claude project configuration, git/worktree/submodule policy, hard-boundary verification, migration staging, and rollback.

**Regression visibility:** evidence confirms Agent Red and GT-KB are already separate Git repositories, while Agent Red still contains GT-KB governed/runtime surfaces. The plan explicitly states that Codex/Claude project selection is not a security sandbox and later phases must test local harness, path traversal, dependency mode, git boundary, and CI boundary behavior.

### GTKB-ISOLATION-003 - DONE - Create detailed Phase 3 plan: host, container, and development environment isolation

**Priority:** TOP after `GTKB-ISOLATION-002`.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`. Completed plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-003-PHASE3-ENVIRONMENT-ISOLATION-PLAN-2026-04-23.md`.

**Outcome:** completed the detailed Phase 3 environment isolation plan. The plan defines application-subject, GT-KB-subject, and migration-rehearsal environment authority profiles; covers local harnesses, IDE/workspace trust, devcontainers, Codespaces, Docker/Compose, CI, deployment tooling, secrets, dependency mode, and owner-approved escape hatches; identifies current Agent Red evidence and risk points; and defines a verification matrix for local harness, devcontainer, Docker/Compose, and CI boundaries.

**Required outcome:** create a detailed implementation plan for isolating application-subject development environments from GT-KB product artifacts across local harnesses, dev containers, remote development environments, Docker/Compose, CI, and deployment tooling. Cover filesystem read/write boundaries, application-only project roots, devcontainer/Codespaces lifecycle commands and mounts, workspace trust, container hardening, app-scoped secrets, CI working directories, read-only dependency mounts, and explicit owner-approved escape hatches.

**Regression visibility:** application-subject environments must not receive parent GT-KB write access by default. The plan must explicitly test local harness, dev container, Docker/Compose, and CI boundaries, and must forbid privileged containers, Docker socket mounts, broad host bind mounts, and GT-KB product/admin secrets unless a later owner decision grants a scoped exception.

### GTKB-ISOLATION-004 - DONE - Create detailed Phase 4 plan: scoped GT-KB service boundary

**Priority:** TOP after `GTKB-ISOLATION-003`.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`. Completed plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-004-PHASE4-SCOPED-SERVICE-BOUNDARY-PLAN-2026-04-23.md`.

**Outcome:** completed the detailed Phase 4 scoped service boundary plan. The plan rejects raw all-powerful database/root authority for ordinary application sessions; defines typed scoped operations for dashboard reads, Deliberation Archive, MemBase, bridge, release/deployment requests, credentials, upgrade/scaffold requests, and offline/degraded mode; requires service-side GOV enforcement independent of harness hooks; and defines a verification matrix proving application sessions cannot mutate product records or combine application and GT-KB product readiness claims.

**Required outcome:** create a detailed implementation plan for scoped GT-KB services that application sessions can use without broad parent-root or raw database authority. Cover dashboard reads, app-scoped Deliberation Archive append/query, app-scoped MemBase operations, release/deployment requests, credential scope, offline/degraded mode, and service-side GOV enforcement.

**Regression visibility:** the plan must reject raw all-powerful database connection strings for ordinary app sessions unless a later owner decision explicitly accepts that risk.

### GTKB-ISOLATION-005 - DONE - Create detailed Phase 5 plan: dashboard control plane and programmatic operations

**Priority:** TOP after `GTKB-ISOLATION-004`.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`. Completed plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-005-PHASE5-DASHBOARD-CONTROL-PLANE-PLAN-2026-04-23.md`.

**Outcome:** completed the detailed Phase 5 dashboard control-plane plan. The plan defines a typed operation registry, app-root path and capability allowlists, scoped Markdown operations, deterministic projection of behavior-defining Markdown into subject-specific AI-facing files, durable mode and work-subject flows, harness topology and bridge role-slot requirements, session pause/resume/restart-request controls, dry-run/diff/audit/rollback behavior, authentication and authorization scopes, and GOV/formal-approval boundaries.

**Required outcome:** create a detailed implementation plan for GT-KB dashboard/web control-plane operations that can act on application-local files without granting ordinary application sessions broad GT-KB product authority. Cover typed operation registry, app-root path allowlists, selected Markdown add/remove/scan/normalize tools, minimal executable projection of behavior-defining Markdown into subject-specific AI-facing startup files, durable mode toggle flow, harness topology registry, Prime Builder/Loyal Opposition bridge role slots, work-subject toggles, pause/resume/restart AI session controls, dry-run/diff preview, audit logs, rollback records, authentication, and GOV/formal-approval boundaries.

**Regression visibility:** application-subject sessions must not be able to use the dashboard/control plane to mutate GT-KB product artifacts. Arbitrary path inputs and arbitrary script execution must be denied by default; mode and session-control changes must declare whether they apply immediately or only to the next session. Projection scripts must be product-controlled, reproducible from canonical policy sources, source-hashed, audited, and tested to reduce startup conditional context without deleting mandatory subject/root/GOV enforcement text. The plan must explicitly avoid using projection to remove ordinary AI judgment from application work. Mode/projection operations must not proceed until the target harness, project root, bridge role slot, and single-harness versus dual-harness topology are resolved.

### GTKB-ISOLATION-006 - DONE - Create detailed Phase 6 plan: session overlay and snapshot mechanism

**Priority:** TOP after `GTKB-ISOLATION-005`.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`. Completed plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-006-PHASE6-SESSION-OVERLAY-SNAPSHOT-PLAN-2026-04-23.md`.

**Outcome:** completed the detailed Phase 6 session overlay and snapshot plan. The plan defines copy-only non-authoritative overlays, an app-local overlay root and manifest schema, copy eligibility and denied sources, refresh and stale-detection semantics, promotion-only writeback, generated-projection relationships, canonical-versus-overlay scanner behavior, retention cleanup, implementation slices, and tests proving overlays are non-authoritative and cannot be mistaken for canonical GT-KB product records.

**Required outcome:** create a detailed implementation plan for copy-only session overlays. The plan must define which artifacts may be copied, where overlays live, when refresh occurs, how source hashes and authority metadata are recorded, how stale overlays are detected, and how proposed changes are promoted instead of silently written back to GT-KB.

**Regression visibility:** include tests proving overlays are non-authoritative, no parent artifact is moved, stale snapshots are flagged, and copied artifacts cannot be mistaken for canonical GT-KB product records.

### GTKB-ISOLATION-007 - DONE - Create detailed Phase 7 plan: work subject and root enforcement

**Priority:** TOP after `GTKB-ISOLATION-006`.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`, proposal `bridge/gtkb-session-work-subject-001.md`, revised planning bridge `bridge/gtkb-session-work-subject-003.md`, and Loyal Opposition GO `bridge/gtkb-session-work-subject-004.md`. Completed plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md`.

**Outcome:** completed the detailed Phase 7 work-subject and root-enforcement plan after Phases 3 through 6 were completed. The plan separates operating role, work subject, root, and bridge role slot; defines durable app-local subject state and command precedence; integrates resolved-root mutation guardrails, startup/dashboard scoping, readiness/test scoping, hook parity, Phase 5 control-plane operations, Phase 6 overlay status, multi-harness role awareness, and upstream GT-KB packaging requirements. It remains planning only; implementation still requires a later concrete bridge-approved implementation proposal or explicit owner supersession.

**Required outcome:** create a detailed implementation plan integrating `work subject application` and `work subject GT-KB` with root-boundary checks, startup priority scoping, release-readiness scoping, test scoping, mutation guardrails, hook parity, dashboard/control-plane session controls, durable mode projection, multi-harness role awareness, generated subject-specific AI-facing startup instruction files, and deterministic bridge index handling. The bridge portion must include a scripted writer/validator that fresh-reads live `bridge/INDEX.md`, rejects cached or stale bridge state, validates role/status transitions, computes the next bridge file number from live index plus disk, writes the response file before inserting the status line, preserves the audit trail, and verifies post-write live state. The plan may revise the existing work-subject bridge proposal after root/service/control-plane/overlay requirements are clear.

**Regression visibility:** application-subject sessions must block or warn before mutating GT-KB product paths; readiness and test reports must label the active subject and must not combine application and GT-KB green claims. Bridge implementation tests must cover stale index rejection, next-number calculation, invalid transition rejection, existing-file collision, concurrent index change, and post-write live-state verification.

### GTKB-ISOLATION-008 - DONE - Create detailed Phase 8 plan: Agent Red migration rehearsal

**Priority:** TOP after `GTKB-ISOLATION-015`.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`. Completed plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md`.

**Authorization:** `bridge/gtkb-isolation-phases-8-9-planning-scope-004.md` (GO).

**Outcome:** completed the detailed Phase 8 Agent Red migration rehearsal plan. The plan defines a zero-destructive rehearsal that emits preview artifacts (dry-run inventory, path-rewrite map, CI command inventory, bridge/backlog/release-readiness split previews, production-effects map, rollback manifest) into the target child root without mutating the legacy mixed root, production deployments, or the GT-KB product root. It treats every one of the 16 mixed-state surfaces from the inventory Interdependency Classification table with a named action (move, copy, split, stay, regenerate, deprecate), Phase 1 authority classification, transformation recipe, rollback behavior, and post-migration verification. Surface 11 (`.claude/hooks/workstream-focus.py`) is recorded as already retired/absent per the GO informational note. The plan binds all seven inventory-required coverage items and the four inventory-required exit criteria to concrete rehearsal artifacts and acceptance checks. It remains planning only; actual rehearsal execution is `GTKB-ISOLATION-016` and requires its own implementation bridge.

**Required outcome:** create a detailed implementation plan for a non-destructive Agent Red extraction/migration rehearsal from the legacy mixed root into the selected application root. Include path rewrites, imports, CI/test command updates, dashboard/DB path handling, bridge/backlog split, production deployment effects, and rollback.

**Regression visibility:** require dry-run inventory and verification before any move. No destructive cleanup or production-affecting change is authorized by this planning item.

### GTKB-ISOLATION-009 - DONE - Create detailed Phase 9 plan: downstream adopter packaging and validation

**Priority:** TOP after `GTKB-ISOLATION-008`.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`. Completed plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md`.

**Authorization:** `bridge/gtkb-isolation-phases-8-9-planning-scope-004.md` (GO).

**Outcome:** completed the detailed Phase 9 downstream adopter packaging and validation plan. The plan binds adopter tooling to the approved entrypoints `gt project init` and `gt project upgrade` (no standalone `gt application scaffold` entrypoint), centers the managed artifact registry as the declarative source of truth for adopter-owned vs product-owned artifacts, expands `gt project doctor`/preflight checks to detect isolation violations (including a negative-presence check for the retired `.claude/hooks/workstream-focus.py`), specifies a clean-adopter test suite under GT-KB `tests/adopter/` with outside-in assertions driven by the registry, specifies documentation and example projects under GT-KB `docs/` and `examples/`, and binds every inventory-required coverage and exit criterion to a concrete deliverable and acceptance check. Open decisions for the implementation bridge include mandatory-vs-opt-in isolation for existing adopters, which GT-KB release ships the tooling, and whether Agent Red becomes a minimized Phase 9 example. It remains planning only; actual productization is `GTKB-ISOLATION-017` and requires its own implementation bridge.

**Required outcome:** create a detailed implementation plan for making the isolation model a GT-KB product capability. Cover `gt project init`, `gt project upgrade`, managed artifact registry changes, `gt project doctor`/preflight checks, clean-adopter tests, application-only project-root documentation, and examples.

**Regression visibility:** clean adopters must default to application subject, must not expose GT-KB product artifacts for mutation from app-only roots, and must retain functioning app-local governance state.

### GTKB-ISOLATION-016 - Execute non-destructive Agent Red migration rehearsal

**Priority:** TOP after `GTKB-ISOLATION-015` **closes (Slice 2 VERIFIED)**.
Phase 8 execution requires the full Phase 7 work-subject/root enforcement
to land — not merely the Phase 8 plan (`GTKB-ISOLATION-009` which is DONE).
Historical priority line pointed at `-009`; corrected 2026-04-24 per S306
backlog hygiene pass.

**Required outcome:** after the Phase 8 and Phase 9 plans are complete, run the
approved non-destructive rehearsal from the legacy mixed root into the selected
child application root, emit dry-run inventory and path rewrites, prove split
bridge/backlog/dashboard/DB handling, preserve rollback/removal records, and
verify Agent Red behavior from the child directory without mutating GT-KB
product root or production environments.

**Regression visibility:** rehearsal stays zero-destructive by default. Verify
application-only CI/test/startup/dashboard lanes separately from GT-KB product
lanes and capture exact pre/post path maps.

### GTKB-ISOLATION-017 - Implement downstream adopter packaging and clean-adopter validation

**Priority:** TOP after `GTKB-ISOLATION-016`.

**Required outcome:** land the Phase 9 productization work: `gt project init`
and `gt project upgrade` defaults for application subject, managed artifact
registry updates, doctor/preflight isolation checks, clean-adopter fixtures,
application-only project-root documentation, and examples that preserve
app-local governance state while denying GT-KB product mutations from app-only
roots.

**Regression visibility:** clean-adopter tests must prove safe defaults,
functioning app-local governed state, isolated bridge/readiness/test labeling,
and upgrade/rollback behavior from a clean project root.

### GTKB-ISOLATION-018 - Execute Agent Red child-directory cutover

**Priority:** TOP after `GTKB-ISOLATION-017`.

**Required outcome:** after successful rehearsal evidence and the required owner
approval for the migration window, perform the actual Agent Red extraction into
the selected child application root, rewrite runtime/config/test/CI/deployment
paths, split mixed-root bridge/backlog/state surfaces appropriately, preserve
rollback, and leave the legacy mixed-root path either frozen or clearly
decommissioned.

**Regression visibility:** final cutover evidence must show the app root
operates without default GT-KB product write authority, the GT-KB product root
remains independently runnable, and no production deployment effect occurs
without separate approval.

### GTKB-ISOLATION-019 - Close the isolation program with final verification and backlog cleanup

**Priority:** TOP after `GTKB-ISOLATION-018`.

**Required outcome:** prove the program complete end to end: application-only
sessions default to the child root and application subject, GT-KB product
artifacts remain outside ordinary app mutation scope, clean-adopter packaging
works, remaining mixed-root debts are either removed or explicitly deferred, and
non-isolation backlog items can resume with the new root/service/control-plane/
overlay defaults in place.

**Regression visibility:** run and record separated application and GT-KB
verification lanes, clean-adopter validation, cutover smoke checks, and a
standing-backlog audit that confirms no missing isolation follow-on items
remain.

### GTKB-MASS-001 - Execute GT-KB mass-adoption readiness plan

**Priority:** deferred behind the isolation-program queue by owner directive
2026-04-23. Owner directive 2026-04-20 still stands for GT-KB mass adoption,
but the later owner directive makes completion of the overall application/GT-KB
isolation program the standing priority until `GTKB-ISOLATION-019` is complete
or the owner explicitly reprioritizes this item.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-MASS-ADOPTION-READINESS-PLAN-2026-04-20.md`.

**Required outcome:** make GT-KB ready for scoped commit, review-branch push, merge, and mass adoption by executing the ordered readiness program:

1. classify dirty worktree paths and isolate the first commit scope,
2. run the next fresh-session startup acceptance test,
3. close or owner-disposition release blockers,
4. apply or defer GT-KB scaffold/adoption drift,
5. repair failing or stale testing/tool integrations,
6. run clean-adopter install/startup/dashboard/upgrade/rollback tests,
7. push only scoped evidence-backed commits,
8. merge only after required CI and owner decisions are green or formally deferred.

**Next-session acceptance gate:** test session startup first. A fresh session must present role/governance context, a usable dashboard link, directly actionable session-focus choices, Agent Red dashboard scope with GT-KB as infrastructure, top-of-page dated delivery timeline, and tool-integration remediation guidance before substantive work begins. The startup must not present the invalid `app://-/index.html?hostId=local` dashboard link.

**Regression visibility:** use `tests/scripts/test_session_self_initialization.py`, `tests/scripts/test_groundtruth_governance_adoption.py`, `tests/scripts/test_release_candidate_gate.py`, `scripts/release_candidate_gate.py`, browser verification of `docs/gtkb-dashboard/index.html`, and the clean-adopter test matrix described in the plan report. Keep this item at the top until the plan report's commit/merge/push and mass-adoption criteria are satisfied or explicitly superseded.

### GTKB-CORE-001 - Make core application specification intake default GT-KB behavior

**Priority:** TOP. Owner directive 2026-04-22: use Agent Red specifications as the worked example for a reusable baseline set of requirements that should exist for any similar application, then ensure GT-KB repeatedly prompts for missing input and clarity after initialization until those core specifications are created. Once the core specifications are complete, prompting must cease.

**Current default confirmation:** this is **not mechanically the current GT-KB default behavior yet**. Current GT-KB `gt project init` accepts scaffold options but does not ask the core application specification questions by default; `ScaffoldOptions.spec_scaffold` defaults to `None`; `scaffold_project()` only inserts generated specs when an explicit spec scaffold config is supplied. This backlog item records the approved target behavior, not an already-shipped default.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CORE-SPEC-BASELINE-EVALUATION-2026-04-22.md` and `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CORE-SPEC-INTAKE-IMPLEMENTATION-PLAN-2026-04-22.md`.

**Phase 0 approval evidence:** Owner approved proceeding on 2026-04-22 after the Phase 0 bridge proposal `bridge/gtkb-core-spec-intake-001.md` was filed. Approval packet: `.groundtruth/formal-artifact-approvals/2026-04-22-core-spec-intake-phase0.json`. MemBase formalization: `DELIB-0875`, `SPEC-CORE-INTAKE-001`, `SPEC-CORE-INTAKE-002`, `ADR-CORE-INTAKE-001`, and `DCL-CORE-INTAKE-001`. Current formal status is `specified`; this records the approved target and compatibility policy, not completed implementation.

**Required outcome:** GT-KB provides a persisted core application specification intake loop that is active for newly initialized projects by default, with an explicit opt-out for automation or unusual cases. The loop must ask one missing core-spec question at a time, capture answers with owner-stated provenance or confirmation-needed status, continue across sessions while required slots remain missing/inferred/unclear, and stop once every required slot is owner-stated or explicitly not applicable.

**Baseline slots:** product identity, application type, tenancy/provider administration, user/role model, data classification, compliance obligations, security posture, reliability/SLO posture, external integrations, AI usage, operational/release path, and explicit non-goals.

**Multi-session execution plan:**

1. Phase 0 - Governance and compatibility: propose/approve formal SPEC/ADR/DCL records, settle default-vs-opt-in policy, and preserve backward-compatibility constraints.
2. Phase 1 - Core slot catalog: add stable package-level slot definitions, handles, prompt text, required fields, and not-applicable semantics.
3. Phase 2 - Completion evaluator: inspect persisted MemBase evidence and return each slot as `missing`, `inferred`, `needs_clarity`, `stated`, or `not_applicable`.
4. Phase 3 - CLI surface: add deterministic `gt core-specs status`, `gt core-specs next-question`, and answer/intake flow suitable for tests and hooks.
5. Phase 4 - Integration: wire `gt project init`, `gt project doctor`, session-start hooks, and dashboard/startup reports to surface the next missing core-spec question without blocking concrete owner tasks.
6. Phase 5 - Documentation and adoption evidence: update CLI/bootstrap/user-journey docs, run clean-adopter tests, preserve existing scaffold tests, and record final default-behavior evidence.

**Regression visibility:** upstream GT-KB tests must prove fresh projects start incomplete, owner-stated answers stop prompting per slot, explicit not-applicable stops prompting per slot, inferred candidates do not stop prompting, all-complete state suppresses prompting, existing minimal/full scaffold behavior is not accidentally broken, and non-interactive automation has a no-prompt path. Agent Red release-gate visibility should include a standing backlog/dashboard signal until GT-KB upstream implementation and clean-adopter verification are complete.

### GTKB-GOV-001 — Complete Agent Red Tier A managed-skill adoption apply

**Priority:** TOP. Owner directive 2026-04-19: adopt and enforce, to the extent possible, all GroundTruth-KB governance specifications, skills, subsystems, and integrations available to Agent Red.

**Required outcome:** finish the pending `gtkb-skills-tier-a-adoption-apply` thread or supersede it with an owner-approved direct apply record. Confirm all GroundTruth-KB v0.6.1 Tier A managed hooks, rules, skills, settings registrations, and gitignore exceptions are either adopted, explicitly rejected with rationale, or recorded as project-owned overlays.

**Regression visibility:** keep `tests/scripts/test_groundtruth_governance_adoption.py` in the release-candidate gate and extend it for every newly adopted managed artifact.

### GTKB-GOV-002 — Promote Agent Red release-candidate gate into the GT-KB managed skill/doctor model

**Priority:** TOP. Candidate skill identified during release-readiness hardening: `.claude/skills/release-candidate-gate/SKILL.md` now exists locally for Agent Red, but it is not yet an upstream GroundTruth-KB managed skill or doctor/readiness plugin.

**Required outcome:** add an upstream GT-KB bridge/work item for a reusable release-candidate gate skill or doctor check that downstream adopters can install through the managed artifact registry. It should cover security scans, dependency audit, targeted regression suites, frontend builds, DA/MemBase update evidence, and Python-version proof.

**Regression visibility:** upstream GT-KB tests should prove scaffold/install/upgrade behavior; Agent Red tests should prove the local gate remains wired into CI.

### GTKB-GOV-003 — Add an Agent Red governance-adoption doctor check

**Priority:** TOP. Candidate integration identified during this pass: Agent Red can verify GT-KB adoption through tests, but there is no first-class `gt project doctor` or plugin-style command that reports adopter drift across `groundtruth.toml`, `.claude` hooks/rules/skills, workflow gates, and KnowledgeDB gate plugins.

**Required outcome:** implement or request an upstream GT-KB doctor/readiness check for adopter drift, including managed-vs-project-owned dispositions and local-only settings such as `.claude/settings.local.json`.

**Regression visibility:** add fixture-based GT-KB tests for drift detection and keep Agent Red's release gate invoking the local adoption test until the upstream doctor is available.

### GTKB-GOV-004 — Complete MemBase work-item harvest into standing backlog snapshots

**Priority:** TOP. Standing backlog source audit found `groundtruth.db` still has 1994 open work items, 14 new, 4 in_progress, 8 unresolved, 1 blocked, 17 specified, 1 created, and 1 deferred work item. These cannot be pasted wholesale into `memory/work_list.md` without making the backlog unusable, but they must be reconciled into backlog snapshots or a structured GT-KB work queue.

**Required outcome:** classify non-terminal MemBase work items into active release blockers, grouped backlog snapshots, obsolete/superseded rows, or separately governed work streams. Start with P0/P1 rows and reconcile `WI-1515`, `WI-1567` through `WI-1569`, `WI-1637`, and `WI-3026` through `WI-3027` explicitly.

**Regression visibility:** keep `scripts/audit_standing_backlog_sources.py` and `tests/scripts/test_standing_backlog_harvest.py` in the release-candidate gate until an upstream GT-KB doctor/check replaces them.

### GTKB-GOV-007 - PAUSED - Revise commercial readiness NO-GO tracks for SPEC-1831, SPEC-1832, and SPEC-1833

**Priority:** PAUSED by the bridge index note dated 2026-04-18. Live commercial readiness NO-GO entries require revised proposals before implementation, but the three commercial-readiness sub-track threads are paused indefinitely until the owner explicitly unpauses them.

**Required outcome:** file or obtain revised bridge proposals that satisfy the latest NO-GO findings, then implement only after GO. Preserve owner-decision and KB-promotion discipline.

**Regression visibility:** bridge entries remain visible through `scripts/audit_standing_backlog_sources.py`; affected tests must cover the revised route, middleware, retention, and alert-engine contracts.

### GTKB-GOV-008 — Repair bridge dispatcher deferral enforcement

**Priority:** TOP. Live bridge dispatcher deferral enforcement implementation is NO-GO because the shared freshness parser still ignores `DEFERRED`, status recognition is duplicated across parser paths, generated-wrapper handling conflicts with ignored output policy, and owner-only mute authority decisions are not recorded.

**Required outcome:** revise the implementation bridge to update shared parser/guard logic, parity-test scanner status vocabularies, verify generated wrapper regeneration without committing ignored outputs, and record explicit owner decisions for option selection/status name/mute authority or keep those behind an owner-decision gate.

**Regression visibility:** PowerShell bridge-automation tests must prove muted/deferred entries suppress dispatch for `NEW`, `REVISED`, `GO`, and `NO-GO` snapshots without suppressing unrelated entries.

### GTKB-GOV-009 — Await GT-KB Azure CI/CD gates verification

**Priority:** TOP. `gtkb-azure-cicd-gates` is latest `VERIFIED` at `bridge/gtkb-azure-cicd-gates-010.md` after Prime Builder fixed the D4 scaffold-only Azure CI/CD generated-doc defect. The generated federated-identity setup guide now instructs environment-subject credentials for `staging-plan`, `staging`, `production-plan`, and `production`, and the regression test proves `refs/tags/v*` is absent from the explicit credential guide.

**Required outcome:** the D4 Azure CI/CD bridge thread is now verified at `bridge/gtkb-azure-cicd-gates-010.md`. Ordinary staging of the broader first-commit package remains gated on fresh Loyal Opposition review of the latest `gtkb-mass-adoption-first-commit-package` package artifact; do not stage upstream Azure CI/CD changes as a standalone package outside that coordinated review.

**Regression visibility:** upstream GT-KB tests now cover template path equality, no-overwrite behavior, OIDC input/env contract, environment usage, production environment-subject federated-identity guidance, absence of `refs/tags/v*` in the explicit credential guide, and actionlint workflow validation.

### GTKB-GOV-010 — Maintain standing backlog harvest audit as release-gate input

**Priority:** TOP. The standing backlog cannot be considered fully populated without a repeatable harvest check over bridge status, MemBase work items, release-readiness blockers, and independent progress artifacts.

**Required outcome:** keep `scripts/audit_standing_backlog_sources.py`, `tests/scripts/test_standing_backlog_harvest.py`, and `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STANDING-BACKLOG-HARVEST-2026-04-20.md` current until GT-KB provides a first-class standing-backlog doctor. Future sessions should update the harvest report or supersede it with a structured snapshot when source counts change materially.

**Regression visibility:** release-candidate gate runs the standing backlog harvest test.

### ℹ️ DA-gov dispatch loop — escalation OBSOLETE (resolved by owner action 2026-04-18)

**Spawn-5 escalation (A/B/C) is obsolete.** The owner has effectively chosen
Option B implicitly: GT-KB is now on `main` and `gtkb-da-governance-completeness-implementation-016`
is in active iterative implementation per the fast-iterate posture
(`memory/feedback_iterate_fast_on_main.md`, S300). Two commits have already
landed:

- **`4e54c0b`** — §B.1 refactor (event-aware structured-merge planner/apply via
  shared `_compute_target_event_list` helper).
- **`f5b0051`** — Phase 2: 5 governance hook stubs + 9 registry records
  (registry expanded 42→51, including the 4 new `settings-hook-registration`
  rows that opt into BOTH upgrade enforcement AND doctor enforcement per §A
  of `-015`).

**Remaining work** (per the f5b0051 commit message + `-015` §-numbering):
real hook logic, doctor integration (§B.3/§B.4), §B.2 13+1 test cases
(especially cases 12/13 interleaved-unmanaged), and Phases 1-10 specs/tests
(redaction routing, source-ref validation, LO-report backfill, transcript
extractor, owner-decision capture full impl, GOV-09 capture, backfill
framework, session wrap gate, dogfooding). Approximately 100+ new tests
across ~10 test files; ~8-12 follow-up commits expected.

**Capped-spawn behavior:** the auto-poller will continue to dispatch the
GO until `-017 NEW` (post-impl report) lands. Future capped spawns should
append abbreviated entries to `groundtruth-kb/.implementation-log-gtkb-da-governance-completeness.md`
(spawn-54 entry has the corrected state baseline) and not attempt next-slice
implementation work — the owner's iterative landings on main handle the
cohesive multi-file slices naturally.

Full corrected status chain: see spawn-54 entry in
`groundtruth-kb/.implementation-log-gtkb-da-governance-completeness.md`.

### Forward-work ordering reference (GO'd 2026-04-17)

**Authoritative ordering:** `bridge/post-phase-a-prioritization-003.md` (plan) + `-004.md` (Codex GO).
The plan is the ordering reference for all post-Phase-A work. Each numbered item still requires
its own bridge proposal and review cycle per `.claude/rules/codex-review-gate.md`.

**Tier 1 (immediate, visible to CTO, blocks downstream):**
1. **A1 — `gtkb-bridge-spawn-revalidation`** (small; spawn pre-execution INDEX revalidation guard).
2. **B1 — Agent Red CTO cleanup** (20 commits ahead, CI red on SonarCloud, 19 dirty files to classify).
3. **C1 — `gtkb-managed-artifact-registry`** (closes live Gap 2.8; blocks C2-C8 only; NOT a dependency of D1/D2).

**Tier 2 (parallelizable after Tier 1):**
4. **C2 — `gtkb-upgrade-pre-flight-checks`** (requires C1).
5. **D1 + D2 — Azure spec scaffold + ADR template activation** (independent of C1; can run parallel with C1 — owner priority choice).
6. **E1 — `gtkb-skills-tier-a-adoption-001`** (Agent Red adoption of Tier A deliverables).

**Tier 3 (dependency-gated):** C3+C4, D3+D4, F2 (POR 16.D orphan test), F4 (SPEC-1831/1832/1833 verify), B4 (`wiki/Scaling-Analysis.md` hygiene).

**Tier 4 (planned/deferred):** F1 (POR 14, blocked on carrier), C5-C8, D5→D6→D7, F3 (POR 16.E), B2, B3.

**Tier 5 (long-term):** F6 (Zero-Knowledge Phase 4).

**Codex conditions to carry forward (from `-004.md`):**
- **A1 child bridge must:** (a) make revalidation rule role-specific (Codex = NEW/REVISED match; Prime = GO/NO-GO match); (b) NOT treat `NO-GO` as terminal for Prime (Prime on NO-GO writes REVISED — see `.claude/rules/file-bridge-protocol.md:60-63`); (c) identify live wrapper set explicitly (including whether `*-noconsole.generated.ps1` files are source-of-truth, deployment artifacts, or both); (d) include an integration test that mutates `bridge/INDEX.md` between snapshot selection and spawn execution and proves the stale spawn aborts without modifying any bridge file.
- **B4 child bridge must:** stay scoped as documentation-hygiene around `wiki/Scaling-Analysis.md`; must NOT reopen WI-3171 implementation scope unless new evidence shows a live scaling mismatch.
- **If Prime ever proposes C2 before C1** despite the matrix, that is an explicit owner override of the registry-first recommendation, not a default technical plan.

**Owner override still open:** whether D1+D2 should be pulled into Tier 1 alongside A1+B1+C1 for an Azure-focused CTO demonstration. Default plan recommends Tier 2 placement; owner may elevate.

### Owner-directed backlog addition (2026-04-17): Claude Design GUI exploration

**Priority placement:** Deferred until the current active priorities above are complete or explicitly paused by owner. Once the current priority stack is clear, focus on taking best advantage of Claude Design for Agent Red GUI work.

**Proposed bridge/workstream name:** `agent-red-claude-design-gui-refresh-intake`

**Initial scope (exploration and process design, not implementation):**
- Define how Agent Red's current GUI can be captured for Claude Design using screenshots, route inventory, component inventory, state inventory, design-token notes, and selected source-context directories.
- Define the Claude Design project brief and context package for improving Agent Red GUIs.
- Define the design handoff packet format: exported prototype/HTML/PDF/PPTX/screenshots, component inventory, state matrix, responsive behavior, accessibility notes, open owner decisions, and Claude Code handoff boundaries.
- Define how GT-KB should register design artifacts, visual specs, ADRs, acceptance criteria, and review evidence.
- Define automated GUI verification requirements for Claude Design-derived work: Playwright screenshots, visual baselines, review gallery, axe/accessibility checks, keyboard navigation, semantic DOM assertions, and state-matrix coverage.
- Define Loyal Opposition review gates so Claude Design output becomes binding only after export, GT-KB registration, bridge review, and visual/a11y verification.

**Explicit non-scope until later GO:** no GUI redesign implementation, no production UI changes, no direct Claude Design to production handoff, and no bypass of Prime/Codex bridge review.

### CTO readiness (Agent Red full cleanup)
**GT-KB CI fix (4C regression) ✅ VERIFIED + PUSHED.** Bridge `gtkb-4c-ci-regression-fix-004`. Commit `a3fa4d2` on GT-KB main. All 6 GitHub CI workflows green.

**SMS OTP hardening ✅ VERIFIED (not pushed).** Bridge `agent-red-sms-otp-hardening-008`. Commit `468ec1c7` on develop. 4 files: `src/chat/identity_preprocessor.py`, `src/multi_tenant/widget_otp_verification.py`, `tests/chat/test_identity_preprocessor.py`, `tests/unit/test_widget_otp_verification.py`. 77 target tests pass, 3 `assert_awaited_once()` guards. Provisioning display-name rewrite split to future separate bridge (Codex-002 flagged tenant-isolation risk with cross-partition `STARTSWITH` query).

**Agent Red remaining CTO-prep work** (not yet scoped into bridge proposals):
- 16 commits on develop ahead of origin (includes `468ec1c7` SMS hardening)
- Dirty worktree beyond 4 SMS files (docs, bridge/*, memory, groundtruth.db, ~480 files)
- CI failing on develop at GitHub (last push was several commits back)
- Deferred provisioning display-name rewrite (`src/integrations/provisioning.py` + 2 test files, needs tenant-isolation review)
- Wiki currency review (Codex flagged as stale relative to current April work)

### GT-KB Operational Skills Tier A (Phase A scope GO'd 2026-04-17)
**Status:** Scope GO at bridge `gtkb-operational-skills-tier-a-004`. Scope-level post-implementation tracking report filed at `-005` (NEW, S299) — all six authorized bridges filed in dependency order, G1-G5 review gates propagated, verdict requested. 6 implementation bridges tracked separately. Phase A targets `groundtruth-kb` v0.6.0 — 1 canonical module + 1 PreToolUse hook + 3 skills + 1 metrics collector.

Six implementation bridges (strict dependency order per GO Condition 3):
1. **`gtkb-credential-patterns-canonical`** — **✅ VERIFIED S298** at `-010`. Commit `862045d` on GT-KB main (local, not pushed): 6 files, +1442/-63, tests 969→1074 (+105), ruff/mypy --strict/full-suite all pass. Non-blocking audit caveat from Codex: fixture has set-equality with pre-migration source but not order-equality (subagent reordered PII entries to end). Recommended non-blocking follow-up: either restore order or document content-set comparison basis. #1 is done; #2, #4 in revision; #3, #5 blocked.
2. **`gtkb-hook-scanner-safe-writer`** — **✅ VERIFIED S298** at `-012`. Two commits on GT-KB main: `b5e5c6c` (original delivery, 7 files +1619/-25) + `37a88cc` (post-impl fix per `-010` NO-GO: same-version missing-file repair via `_plan_missing_managed_files`, pattern_description formally non-contractual in schema v1, full-repo ruff format). 1114 tests pass total (+40 from Tier A #2), mypy --strict clean, ruff check + format clean on full repo. 3 proposal NO-GO cycles (002/004/006) → REVISED-1/-2/-3 → GO at -008. Post-impl VERIFY took 2 rounds (-010 NO-GO + -012 VERIFIED). Unblocks #3, #5. Non-disruptive-upgrade primitive `_plan_missing_managed_files` now available for skills (#4) and future managed-file classes.
3. **`gtkb-skill-bridge-propose`** — **✅ VERIFIED S298** at `-008`. Commit `0a60054` on GT-KB main: 9 files, +1274/-1, tests 1134→1161 (+27), mypy --strict/ruff/full-suite all pass. 2 NO-GO cycles (002/004) → REVISED-1/-2 → GO at -006 → committed → VERIFIED at -008. Autonomous -001 draft; Prime took over on -003 REVISED after #4 VERIFIED. Pattern: skill helper does credential-only scan + overlap-safe redact (outermost-label merging via `_normalize_hit_intervals`) + atomic INDEX update with 2-attempt retry; no Force bypass path (helper-based writes are outside scanner-safe-writer's Write-tool scope, documented). Unblocks #5 mutation-gate pattern.
4. **`gtkb-skill-decision-capture`** — **✅ VERIFIED S298** at `-012` (no findings). Commit `d9325c9` on GT-KB main: 9 files, +821/-7, tests 1114→1134 (+20), ruff/mypy --strict/full-suite all pass. Wheel contents verified: both skill files ship. 4 proposal NO-GO cycles (002/004/006/008) + 4 REVISED (003/005/007/009) → GO at -010 → committed → VERIFIED. `_MANAGED_SKILLS` pattern established; skills + doctor integration + non-disruptive upgrade path now operational. Unblocks #3 skill-bridge-propose.
5. **`gtkb-skill-spec-intake`** — `/gtkb-spec-intake` skill with confirm-before-mutate contract. Blocked on #3 (mutation-gate pattern).
6. **`gtkb-phase-a-metrics-collector`** — `scripts/collect_phase_a_metrics.py` + fixtures. Consumes `.claude/hooks/scanner-safe-writer.log` JSONL schema v1 from #2. Can parallel #3-5; deferred to last so collector sees real bridge data.

GO review gates from `-004` that each implementation bridge must satisfy:
- **G1** (High, #1): derive credential-pattern inventory from source, not from proposal counts.
- **G2** (High, first skill bridge): make skill scaffold and adopter installation explicit (skills packaged + copied like hooks).
- **G3** (Medium, all): treat GO as authorizing **six** (not five) implementation bridges; normalize counts in reports.
- **G4** (Medium, #5): use valid deliberation outcome (`deferred` exists today; `pending_confirmation` requires schema/API migration).
- **G5** (Medium, #2+#6): scanner-deny record schema must be a stable interface agreed between hook and collector.

Follow-up bridge after v0.6.0 ships: `gtkb-skills-tier-a-adoption-001` (Agent Red adoption of the five deliverables).

### POR Steps 16.D-16.E — Spec hygiene remediation (16.A/B/C complete)
**Status:** 16.A/16.B/16.C all COMPLETE + VERIFIED (umbrella at `por-step16c-implemented-untested-remediation-004`, 2026-04-17). Remaining: **16.D** orphan test rationalization (~10,440 tests, largest sub-phase), **16.E** exit verification (untested-spec count ≤ 6 + orphan-test count ≤ 100).

### Zero-Knowledge Architecture (Phase 4, longer-term)
4 specs (SPEC-1843/1844/1644/1840), 5 implementation phases, ~6-8 sessions. Prerequisites: POR Step 16 substantially complete.

### Minor GT-KB fixes (investigated 2026-04-17 — both resolved/non-issues)
- ~~delib-search-tracker UserPromptSubmit docstring mismatch~~ — **RESOLVED**: scaffold.py:332 correctly registers under `PostToolUse`, matching the docstring. Stale note.
- ~~settings.local.json flat hook format~~ — **NON-ISSUE**: template is permissions-only; all hooks go through `_write_settings_json()` with proper nested format. Comment at scaffold.py:277 ("settings.local.json with bridge hooks") is cosmetic misnomer but has no functional impact. Not worth bridge-proposal cycle.

## Completed

### S301 ✓

- [ ] **E1 Tier A adoption — Apply phase (δ+ε)** — IN FLIGHT at S301 wrap. Thread: `gtkb-skills-tier-a-adoption-apply-001..007`. 3 NO-GO cycles; REVISED-3 at `-007` awaiting Codex review as of 08:24:34 PDT. Pattern across NO-GOs: AR's deny-default `.gitignore` keeps colliding with GT-KB's tracked-artifacts assumption; REVISED-3 adds §A.2 gitignore exceptions for all 28 registry paths + §A.2.5 evidence proof (git check-ignore must return NOT-IGNORED for all 19 A1 paths + receipt probe) + §B.0 resolve_receipt_mode must return tracked (hard gates). Owner decisions (2026-04-18) pinned into the bridge: clean-tree = δ3 side-branch `e1-apply` via `git worktree add`; per-file-skip = (a) copy-aside+restore; A2 dispositions = 6 adopt-overwrite + 3 reject-keep-local. No Agent Red source writes until Codex GO on the implementation bridge.
- [x] **E1 Tier A adoption — Prepare phase (α+β+γ)** — VERIFIED at `gtkb-skills-tier-a-adoption-prepare-008`. Agent Red is now a formal GT-KB adopter: `groundtruth.toml` committed at `d4db57cd` on develop (profile=dual-agent, scaffold_version=0.6.1, cloud_provider=azure). Full reconciliation table produced with 32 rows classified: 23 A1-adopt (19 missing managed files via dry-run + 3 settings-merge + 1 gitignore-append), **9 A2-conflict** requiring owner disposition before Apply (5 hooks + 4 rules that exist in Agent Red but diverge from the 0.6.1 registry templates), 0 A3-reject. Proposed A2 dispositions: 6 `adopt-overwrite` (credential-scan, spec-classifier, bridge-essential, deliberation-protocol, file-bridge-protocol, loyal-opposition — registry is canonical source) + 3 `reject-keep-local` (assertion-check, destructive-gate, scheduler — AR-specific customizations; scheduler flagged for potential future GT-KB registry refinement as bridge-automation-not-governance). Prepare scope was scope-GO'd at `-002` with 6 resolutions + 4 findings; implementation bridge went through TWO NO-GO/REVISED cycles before GO at `-006` (NO-GOs caught: filename collision, missed existing-file drift reconciliation, PowerShell-incompatible command). Live §B.6 output at draft time confirmed Codex's -002 F2 temp-dir simulation: the 9 file-diverge rows would have been invisible without the explicit all-FileArtifact pass. Implementation commit `d4db57cd`; thread version count 8 (001 NEW + 002 NO-GO + 003 REV-1 + 004 NO-GO + 005 REV-2 + 006 GO + 007 NEW + 008 VERIFIED). Apply bridge (δ+ε) is the next phase, awaiting owner decisions on clean-tree strategy (recommended δ3 side-branch) + apply-mechanism for 3 `reject-keep-local` rows (no per-file skip flag exists in `gt project upgrade --apply`).
- [x] **GT-KB C2 upgrade pre-flight checks (Area 5)** — VERIFIED at `gtkb-upgrade-pre-flight-checks-implementation-004` with zero blocking findings. Commit `94f8495` on GT-KB main (pushed). 6 files, +992/-10: new `src/groundtruth_kb/project/preflight.py` module, new `enumerate_scaffold_outputs` pure API in `scaffold.py`, new `MalformedSettingsError` exception + `_has_malformed_settings_skip` helper + `_NON_MUTATING_ACTION_KINDS` frozenset in `upgrade.py`, typed `warning` + `informational` action Literal extension, CLI filter for non-mutating rows + `--ignore-inflight-bridges` flag + exit code 4 for malformed settings. Implements Area 5.2 (bridge in-flight awareness) + 5.3 (halt-before-write on malformed settings.json) + 5.6 (scaffold coverage delta report). 29 new tests (`tests/test_preflight_checks.py`) covering all 5 Codex conditions (C1 structural filter at CLI layer, C2 halt-before-git ordering, C3 latest-status-only parsing with older-under-terminal regression, C4 pure read-only enumerator with byte-snapshot proof, C5 CLI labels + flag wiring). Explicitly deferred: Area 5.1 branch/unpushed policy checks + 5.5 profile change detection. Excluded: Area 6 settings-merge (separate future bridge). Bridge thread: 4 versions total (scope -001 NEW → -002 GO; impl -001 NEW → -002 GO → post-impl -003 NEW → -004 VERIFIED). Full suite: 1385 → 1414 tests. Non-blocking Codex note: direct `execute_upgrade([warning])` library calls still run git preconditions before `_apply_file_actions` (structural fix is CLI-layer per approved design; not a documented library API contract).
- [x] **GT-KB rollback-receipts Phase 3 — `execute_upgrade` payload-branch-and-merge + receipt** — VERIFIED at bridge `gtkb-rollback-receipts-016` (zero blocking findings). Commit `4bc4bb5` on GT-KB main, pushed. 5 files, +693/-13. Adds `_require_git_repo` + `_require_clean_tree` preflight, short-lived `gt-upgrade-payload-<id>` branch, `git merge --no-ff` producing real merge commit, post-merge receipt write (tracked mode creates separate receipt commit at HEAD; HEAD~1 is merge commit). Removes `.bak` backup writes per `-014` condition 5. Adds 3 new exception types (`NotAGitRepositoryError`, `DirtyWorkingTreeError`, `MergeFailedError`) with CLI error wrapping in `project_upgrade`. 7 new Phase 3 integration tests: not-git-repo, dirty-tree, tracked-end-to-end (topology + all 9 receipt fields), revert-m1-reverts-only-payload (proves the rollback primitive), filesystem-end-to-end, no-bak-invariant, noop-payload-skips-receipt. Wrapped 15 existing `execute_upgrade` call sites in 4 test files with `_setup_git_for_upgrade` helper (11 via concurrent gov-completeness commit `d630b20` which adopted my helper). Full suite: 1356 passed (was 1209 at S300 wrap); mypy --strict clean; ruff clean. Phase 4 post-impl report filed at `-015`; VERIFIED at `-016`. Thread fully closed: 16 versions, 7 NO-GOs, 1 GO, 1 VERIFIED. Breaking change: `gt project upgrade --apply` now requires a clean git work tree.

### S297 ✓

- [x] **Agent Red SMS OTP hardening** — VERIFIED at bridge `agent-red-sms-otp-hardening-008`. Commit `468ec1c7` on develop. 4 files (2 src + 2 tests), 77 target tests pass with 3 `assert_awaited_once()` guards. Fixes silent-failure bug where `_send_sms()` returning False was silently treated as success. Bridge iterations: 8 versions (1 NEW + 1 NO-GO proposal, 1 REVISED, 1 GO, 1 NEW post-impl, 1 NO-GO post-impl, 1 REVISED post-impl, VERIFIED).
- [x] **GT-KB CI regression fix (4C)** — VERIFIED at bridge `gtkb-4c-ci-regression-fix-004`. Commit `a3fa4d2` on GT-KB main, pushed to GitHub. Added empty `tests/__init__.py` for `from tests._print_guard` import resolution on Linux CI. All 6 GT-KB CI workflows green (Docs Check, Docs, Docstring Coverage, CI, SonarCloud, CodeQL, Security).
- [x] **POR Step 16.C — Implemented-untested remediation (4 streams)** — VERIFIED at bridge `por-step16c-implemented-untested-remediation-004`. All 4 sub-streams VERIFIED: Stream A (151 α') at -010, Stream B (4 ζ') at -006, Stream C (4 β') at -004, Stream D (34 γ'+δ') at -010. 193-spec reconciliation: 151+4+4+34=193 ✓. Classifier transition: 193→38. 38 hygiene WIs (WI-3185..WI-3218, WI-3221..WI-3224). 122 A1 test updates + 68 test inserts (A3 49, B 18, C 1). 0 spec-status mutations. DELIB-0714 archives consolidated results.
- [x] **POR Step 16.B — Methodology review** — VERIFIED at `por-step16b-methodology-review-006`. 193 implemented-untested requirements partitioned into 5 categories via `classify_16b_candidates.py` (α' 151, β' 4, γ' 19, δ' 15, ζ' 4). Option B (multi-stream remediation) chosen per DELIB-0713.
- [x] **POR Step 16.A — Verified spec closure** — VERIFIED at bridge `por-step16a-verified-spec-closure-010`. Invariant passes (0 violations with owner-approved SPEC-GTKB-SCOPE exception), 7 hygiene WIs open, DELIB-0711 archived, 1686/1686 assertions pass. 10 bridge versions (3 proposal NO-GO + GO + 2 verification NO-GO + VERIFIED).
- [x] **GT-KB Phase 4C — Structured logging migration** — Committed `b1c3359` on GT-KB main. 12 files, +582/-123. New `_logging.py` with split-level defaults (CLI=WARNING, bridge=INFO), `_setup_bridge_logging()` with no-raise fallback, shared `tests/_print_guard.py` (single source of truth for CI + pytest). 989 → 988 tests (+19). Bonus: fixed latent COV_CORE_* Windows mypy crash in `test_public_api_type_checks.py`. Bridge `gtkb-phase4c-structured-logging-016` VERIFIED (4 proposal NO-GO + GO + 2 post-impl NO-GO + VERIFIED).
- [x] **GT-KB Phase 4D — Broad exception governance** — Committed `23cdf09` on GT-KB main. 9 files, +176/-34. Narrowed 2 sites (db.py IntegrityError, launcher.py Windows), removed 1 redundant handler (launcher.py Unix), annotated 21 non-reraising broad catches with `# intentional-catch:` markers. New `tests/test_exception_markers.py` AST-based CI gate (4 tests). Final inventory: 28 handlers (7 exempt re-raise + 21 annotated + 0 unmarked). Bridge `gtkb-phase4d-broad-exception-review-008` VERIFIED.

### S295 ✓

- [x] **GT-KB Phase 4B.8 — Line coverage 54% → 70.04% + branch gate** — 3 commits on GT-KB main: `0e15b90` (174 new tests across 11 files + CI `--cov-fail-under=70` gate + CHANGELOG), `9d68b23` (mypy subprocess env cleanup for latent COV_CORE_* pytest-cov crash on Windows, exit 3221225477 STATUS_ACCESS_VIOLATION — surfaced during 4B.8 full-suite run), `bfdd226` (ruff format blank line caught by post-impl NO-GO). Bridge thread `gtkb-phase4b8-line-coverage-001` → `-014 VERIFIED` (5 NO-GO rounds + 1 post-impl NO-GO, each revealing a different inventory or verification gap: combined-vs-stmt math, hallucinated API names, `| head -25` truncation, cached context.py inventory, incomplete AST import-hygiene check, missing ruff format blank line). **First headless spawn hit the 15-minute timeout** writing 174 tests at 82 turns and was killed mid-verification; Prime Opus completed verification in a live session (no timeout) and diagnosed the mypy-under-coverage crash as a bonus. Final global metrics: combined 70.04%, statements 73.28%, branches 61.16%. Suite: 640 → 814. phase-4b-plan.md updated in `cea14c4`.
- [x] **GT-KB Phase 4B.7 — Residual `mypy --strict` errors (39 → 0)** — commit `f59dad4` on GT-KB main. Closed 39 errors across 5 files (`bridge/poller.py` 17, `bridge/worker.py` 10, `intake.py` 7, `bridge/runtime.py` 4, `bridge/context.py` 1) via six fix patterns (A: `sys.platform` file-lock imports + `_fh: BinaryIO \| None` narrowing; B: `**cast(Any, popen_kwargs)` at 3 subprocess sites; C: None guard + error-dict at 7 intake sites; D: two TypedDict summary accumulators + `cast(dict[str, Any], summary)` returns; E: misc runtime/context narrowing; F: `event_batch: dict[str, Any]` forward decl at `worker.py:581`). Added `tests/test_full_tree_type_checks.py` (638→640 tests) and direct `mypy --strict` CI workflow step. Bridge thread `gtkb-phase4b7-residual-mypy-strict-001` → `-010 VERIFIED` (7 Prime revisions, 3 NO-GO rounds, 1 autonomous headless Sonnet implementation at 82 turns / 9.3 min, 1 Prime commit). Prime Builder discovered Pattern D misdiagnosis (config dict vs summary accumulators) in `-002` and Pattern A/D mypy non-compliance (`os.name` not narrowed, TypedDict not implicitly widened) in `-004` — every subsequent pattern was empirically `mypy --strict` verified before proposal. Methodology lesson captured: never propose a fix pattern without running it through mypy against a standalone snippet first.
- [x] **GT-KB phase-4b-plan.md updated** — commit `ff6988b` on GT-KB main. 4B.7 moved from "In flight" to "Done" table with commit SHA `f59dad4`.
- [x] **Bridge infrastructure permanent fix** — commit `94392a1b` on develop. Rewrote `.gitignore` blanket excludes to content-level with `!`-negations; tracked `.claude/hooks/poller-freshness.py` (hardened worktree-safe, fail-loud), `.claude/settings.json` (project-level `UserPromptSubmit` hook registration), `.claude/rules/bridge-essential.md` (top-priority mandate), and 9 PowerShell + 2 VBS scheduled-task scripts under `independent-progress-assessments/bridge-automation/`. Closes S290-S292 silent-outage window and S294 worktree-blindness root cause. 15 files, +2048/-2.
- [x] **Monitor timestamp enhancement** — commit `5eb0421e` on develop. Prepended local-time `[HH:mm:ss]` to each line emitted by `watch-bridge-scan.ps1`, derived from each status file's own `updatedAtUtc` via `.ToLocalTime()`.
- [x] **Phase 4B plan tracking** — commit `8dafc62` on GT-KB main. Created `docs/reports/phase-4b-plan.md` enumerating sub-rounds 4B.1-4B.6 (Done), 4B.7 (In Flight), 4B.8/4B.9/4C/4D (Proposed) with change protocol.
- [x] **POR Step 16 added** — commit `bb41a59e` on develop. Added post-production spec hygiene remediation step to `docs/plans/PLAN-OF-RECORD-production-readiness.md` (5 phases, exit criteria).
- [x] **Plan artifacts reconciled** — commit `9b8d57fd` on develop. POR file header bumped v3 → v4, Version 6 → 7, target v1.98.91 → v1.98.92 ACHIEVED; work_list.md brought current from S289 to S295 with all missing sub-round history.
- [x] **MEMORY.md refresh** — updated Current Status + added S295 Recent Sessions entry (user auto-memory, not committed to git).

### S292 ✓ (deferred from earlier)

- [x] **Codex autonomous verification batch** — VERIFIED 3 of 4 in-flight items: `poller-emergency-repair` (S291 audit trail), `s291-phase1.5-verified-spec-audit` (98 target specs), `poller-batch-size-cap` (S291 Claude-side cap). `test-artifact-integrity-investigation` NO-GO'd at -004, REVISED -005 autonomously.

### S291 ✓

- [x] **GT-KB Phase 4B.6** — CI enforcement gates (mypy --strict workflow step + per-file coverage gates db.py 68% / cli.py 68% / config.py 80% / gates.py 92% + docstring ratchet 50→51). Commit `31d2c39` on GT-KB main.
- [x] **Spec hygiene S291 batch** — `spec-hygiene-untested-verified-008` VERIFIED (9 backend/widget/pricing specs), `spec-hygiene-spa-investigation-008` + `spec-hygiene-spa-remediation-006` VERIFIED (10 SPA Control Plane specs), Phase 1.5 categorization VERIFIED (98 phantom-evidence specs identified).
- [x] **Claude poller emergency repair** — fixed `$MAX_ITEMS_PER_SPAWN:` one-line PowerShell syntax error that caused 6-hour silent outage. Direct foreground edit.
- [x] **Observability mirror** — `Write-ScanStatus` function + `claude-scan-status.json` at 6 hook points to match `codex-scan-status.json` schema.

### S290 ✓

- [x] **GT-KB v0.4.0 shipped to PyPI** — commit `993f31b` via self-gating `publish.yml` workflow.
- [x] **GT-KB Phase 4A audit baseline** — 10 files committed, baseline metrics published at `docs/reports/v0.4-baseline/SUMMARY.md`. Target commit `83312a0`.
- [x] **GT-KB Phase 4B.1** — config defensiveness (`GTConfigError` wrapping `FileNotFoundError` + `TOMLDecodeError`). Commit `2510f1d`.
- [x] **GT-KB Phase 4B-housekeeping** — Anthropic API-key redaction + `__main__.py` + 4 exit-code tables + `actions/checkout@v4→v6` across 8 workflows. Commit `b41ab8f`.
- [x] **GT-KB Phase 4B.2** — medium defensiveness (PermissionError wrap + missing-section warning + unknown-keys warning). First autonomous headless Sonnet session. Commit `249cdd4`.
- [x] **GT-KB Phase 4B.3** — 27 `KnowledgeDB` + `GateRegistry` public API docstrings to 100% + regression guard. Commit `8151ed2`.
- [x] **GT-KB Phase 4B.4** — mypy --strict public API: 48 errors closed in `db.py` (42), `config.py` (3), `cli.py` (8); insert/update return types widened to `dict[str, Any] | None`; regression guard `tests/test_public_api_type_checks.py`.
- [x] **Poller repair epic** — OAuth token cascade diagnosed + persistent token fix + 90-min → 15-min spawn timeout + Windows toast notifications + file-lock bug fix.

### S289 ✓

## Owner Actions Pending

- [x] Create Chromatic project at chromatic.com + set CHROMATIC_PROJECT_TOKEN GitHub secret (WI-3165) — DONE S285

## Completed (S289)

- [x] **GT-KB Phase 4: F6 Spec Scaffold + F8 Provenance Reconciliation + assertions depth guard** — committed `87e7bd7` on `groundtruth-kb` main, VERIFIED at `bridge/gtkb-phase4-implementation-012.md`
  - F6: new `spec_scaffold.py` (scaffold_specs, SpecScaffoldConfig, ScaffoldReport); `ScaffoldOptions.spec_scaffold` optional integration into `scaffold_project()`; `gt scaffold specs` CLI; 10 tests
  - F8: new `reconciliation.py` (ReconciliationReport + 5 detectors: orphaned_assertions, stale_specs, authority_conflicts, duplicate_specs, expired_provisionals); `gt kb reconcile` CLI with per-detector flags + `--all`; 28 tests (27 detector + 1 CLI smoke)
  - Shared: `_extract_assertion_targets()` gained `depth: int = 0` kwarg with `_MAX_COMPOSITION_DEPTH` guard; 1 regression test in `test_impact.py`
  - Totals: 561 → 600 tests pass, ruff clean, docs CLI coverage clean
  - Review cycle: 5 Prime revisions (v1-v5), 4 Codex NO-GOs, GO at -010, NEW post-impl at -011, VERIFIED at -012
  - Phase 4 completes the entire 8-feature GT-KB Spec Pipeline (F1-F8) started in S286 — the spec pipeline is now fully functional
- [x] **INDEX.md retirement patch (S289 mid-session)** — retired 9 stale/subsumed GT-KB spec-pipeline entries (gtkb-f1f8-cross-check, gtkb-spec-pipeline-f1..f8) from `bridge/INDEX.md` to stop the Prime Builder OS poller from re-firing headless `claude.exe` every 3 minutes on already-completed GO entries. Bridge files remain on disk.
- [x] **Poller autonomy memory** — saved `feedback_poller_autonomy.md` capturing owner directive: "If the poller is working, leave it alone" — mitigate race concerns with fast writes, not shutdown.

## Completed (S285)

- [x] WI-3168 — Migrate knowledge.db to groundtruth.db at repo root (8b9a1def, 11 Codex review rounds, VERIFIED -026)
- [x] WI-3142 — Credential scan narrowing — KB resolved (committed S281)
- [x] WI-3165 — Chromatic CI activation — KB resolved, CI green, 14 snapshots (committed S281 + cb3f2af5)
- [x] WI-3166 — Axe-core CI — KB resolved (committed S282)
- [x] WI-3167 — Playwright baselines — KB resolved (committed S282)
- [x] WI-3169 — Wiki path audit, 6 pages updated (wiki ce2cde8)
- [x] WI-3170 — Transport governance import fix (ae6a6f02)

## Completed (S284)

- [x] GT-kb docs completion — ALL PHASES COMPLETE, Codex VERIFIED (016), committed (0fe21c9), tagged v0.3.0

## Completed (S283)

- [x] Deliberation Archive C3 — Session-wrap harvest script (705 deliberations, 55 bridge threads created)
- [x] Deliberation Archive C4 — Health metrics script + /check-deliberations skill (5 metrics, PASS/WARN/FAIL)
- [x] Deliberation Archive C5 — WI-3159 collision repair + WI-3169 + DOC-DELIB-COMPLETION
- [x] NO-GO fix: test_deliberation_search.py (16 tests, 10/10 known-answer, 100% top-3)
- [x] NO-GO fix: GT-kb v0.2.1 text_match contract test (69/69 pass)
- [x] Requirements updated to GT-kb v0.2.1
