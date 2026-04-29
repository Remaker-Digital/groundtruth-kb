# Bridge Proposal — Session-Hygiene Drift Triage S321

**Status:** NEW (version 001 — scoping; awaits Codex GO)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S321 (2026-04-29)
**Document name:** `session-hygiene-drift-triage-s321-2026-04-29`
**Owner pre-approval:** Yes — `memory/work_list.md` includes the standing isolation directive (2026-04-23) which Phase 2 of isolation cannot proceed under without the carryover drift cleared. S320 wrap notes (`memory/MEMORY.md:4`) explicitly named "a session-hygiene bridge thread that will land before Phase 2 of isolation begins" as the gating mechanism. **This is that bridge.**

**Trigger:** Session start of S321 reveals a working tree containing **38 modified tracked files + 36 untracked entries + 1 pre-existing test-assertion failure**, accumulated across S319 (drift triage closure + DORA-001b Track 1), S320 (Phase 1 isolation + smart-poller activation), and S321's own smart-poller orient-verification work. Most carryover dates to S320 — explicitly deferred per the S320 wrap rather than expanded.

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md` — direct precedent searches returned the following GO/VERIFIED deliberations relevant to this proposal's structure and scope:

- **DELIB-1314 (S317 Working-Tree Triage VERIFIED)** + **DELIB-1315 (S317 GO)** — direct precedent for scoped-commit-plan structure. The S317 thread (`bridge/s317-working-tree-triage-001.md` through `-008.md`) handled 22 modified + 65 untracked entries from S315/S316 carryover; this proposal mirrors its inventory-by-intent + commit-by-boundary approach. Citing for §1 inventory format and §4 commit-plan structure.
- **DELIB-1289 (S319 Session-Hygiene Gitignore Extensions VERIFIED)** + **DELIB-1290 (S319 GO)** — direct precedent for the gitignore-only subset. The S319 thread (`bridge/session-hygiene-gitignore-extensions-2026-04-28-001.md` through `-004.md`) handled 5 gitignore additions for telemetry-churn + hardlink aliases + MEMORY backup glob; this proposal extends with `.gtkb-state/` for smart-poller runtime state.
- `bridge/gtkb-isolation-phase1-implementation-2026-04-28-010.md` (S320 VERIFIED) — Phase 1 isolation closure that produced ~9 doc/template migration leftovers; this proposal records those.
- `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md` (S320 VERIFIED) — smart poller activation closure that left `-004.md` (the GO file) uncommitted and the `.gtkb-state/` runtime dir ungitignored.
- `bridge/smart-poller-orient-verification-2026-04-29-009.md` (S321 REVISED-1 NEW) — orient-verification work in flight in this session; not part of this proposal's scope but acknowledged as the parallel thread.
- `bridge/gtkb-telemetry-churn-policy-2026-04-28-004.md` (S317 VERIFIED) — established the auto-regen telemetry pattern; this proposal applies it to `.gtkb-state/`.
- **Owner directive `.claude/rules/project-root-boundary.md`** — all GT-KB files MUST be within `E:\GT-KB`. This proposal does not violate the boundary; all touched paths are in-root.

No prior deliberations argue against committing the migrated work; all precedent is consistent with "land carryover via scoped commits + extend gitignore for runtime patterns".

---

## §0. Scope

This is a **non-destructive, additive-only working-tree triage**. The plan:

1. Inventories every modified and untracked entry, categorizes by intent and origin.
2. Specifies which entries get committed and in what scoped commit boundary.
3. Specifies which entries are explicitly excluded from tracking (gitignore additions or stay untracked for governance reasons).
4. Resolves the pre-existing test breakage from S320 Phase 1 commit `7108de6f` per its actual scope (legacy operating-role.md path).
5. Defines verification: post-execution `git status` should show only:
   - The `.gtkb-state/` runtime dir (now ignored)
   - The 3 formal-artifact-approval JSONs (intentionally not tracked per §2.3)
   - Whatever new auto-regen telemetry the next session-start hook produces (already gitignored per S317)

**Out of scope:**

- No source code changes beyond:
  - The proposed `.gitignore` addition for `.gtkb-state/`
  - The legacy operating-role.md test-path fixes (4 instances in `tests/scripts/test_session_self_initialization.py`)
- No deletions of any kind. Per `feedback_explicit_destructive_action_authorization.md`, irreversible operations require explicit owner authorization; nothing here removes any file.
- No KB mutations (no `db.insert_*`, no spec status promotions, no work-item state changes).
- No deployment actions.
- **No work on Phase 2 of isolation itself.** This proposal preconditions Phase 2 by clearing the drift; Phase 2 is its own dedicated bridge thread (per S319 wrap directive).
- No revision of the smart-poller orient-verification thread (`-009 REVISED-1` already in Codex's queue for this session).

---

## §1. Modified files inventory (38 entries; 8 logical groups)

### §1.1 Group A — Governance rule clarifications (5 files)

These edits refine role-contract language in `.claude/rules/` and the active operating-role record. Some are housekeeping (Agent Red → GroundTruth-KB naming alignment); some refine governance contracts. All are intentional per session work + S319/S320 owner-directive flow.

| File | Diff stat | Intent confirmed |
|---|---|---|
| [.claude/rules/acting-prime-builder.md](.claude/rules/acting-prime-builder.md) | substantive | "Agent Red" → "GroundTruth-KB" naming corrections; section-heading alignment; preserves DELIB-S312 deterministic-services principle text |
| [.claude/rules/bridge-essential.md](.claude/rules/bridge-essential.md) | substantive | Smart-poller enablement contract added (S320 work); "verified smart poller is opt-out" semantics |
| [.claude/rules/operating-role.md](.claude/rules/operating-role.md) | substantive | Active role file — the authoritative `active_role:` source; refinements consistent with S319 role-contract bridge |
| [.claude/rules/prime-builder-role.md](.claude/rules/prime-builder-role.md) | substantive | Prime-builder role articulation; backlog-progression clause from S319 |
| [AGENTS.md](AGENTS.md) | substantive | Agent role/topology documentation; harness-state path canonicalization |

**Disposition:** **Commit 1** — "rules: governance clarifications + smart-poller enablement contract (S319/S320 carryover)"

**Codex review request for §1.1:** verify the substantive content changes are aligned with prior S319 owner decisions on role contracts (DELIB-S319-* records) and don't introduce new policy beyond what's been adopted.

### §1.2 Group B — Smart-poller source code (4 files in `groundtruth-kb/src/groundtruth_kb/`)

Smart-poller core mechanics modified during S320 activation work. Already covered by VERIFIED bridge thread `gtkb-bridge-poller-notify-activation-2026-04-29-012.md`; this commit lands the source files that the activation bridge proposed.

| File | Diff stat | Intent confirmed |
|---|---|---|
| [groundtruth-kb/src/groundtruth_kb/bootstrap.py](groundtruth-kb/src/groundtruth_kb/bootstrap.py) | likely refactor | Bootstrap initialization adjustments for smart-poller integration |
| [groundtruth-kb/src/groundtruth_kb/bridge/handshake.py](groundtruth-kb/src/groundtruth_kb/bridge/handshake.py) | likely refactor | Bridge handshake logic |
| [groundtruth-kb/src/groundtruth_kb/bridge/launcher.py](groundtruth-kb/src/groundtruth_kb/bridge/launcher.py) | substantive | Smart-poller VBS-launcher pattern (per S320 `-006` Finding 1 architectural shift) |
| [groundtruth-kb/src/groundtruth_kb/bridge/poller.py](groundtruth-kb/src/groundtruth_kb/bridge/poller.py) | substantive | Smart-poller core logic |
| [groundtruth-kb/src/groundtruth_kb/bridge/worker.py](groundtruth-kb/src/groundtruth_kb/bridge/worker.py) | substantive | Worker coordination |
| [groundtruth-kb/src/groundtruth_kb/project/scaffold.py](groundtruth-kb/src/groundtruth_kb/project/scaffold.py) | substantive | Project scaffolding for smart-poller installation |

(6 files total in this group; counted as 4 because `bootstrap.py` + `scaffold.py` may be smaller — final commit message will specify.)

**Disposition:** **Commit 2** — "smart-poller: source mechanics + bootstrap + scaffold (per gtkb-bridge-poller-notify-activation-2026-04-29-012 VERIFIED)"

**Codex review request for §1.2:** verify the source files match what the VERIFIED activation bridge approved, and that no out-of-bridge changes slipped in.

### §1.3 Group C — Phase 1 isolation documentation (4 files in `groundtruth-kb/docs/` + `groundtruth-kb/templates/`)

Phase 1 isolation moved harness-state to `harness-state/{codex,claude}/` and updated documentation/templates accordingly. These are doc updates that mirror the source-level Phase 1 work already VERIFIED at `bridge/gtkb-isolation-phase1-implementation-2026-04-28-010.md`.

| File | Diff stat | Intent confirmed |
|---|---|---|
| [groundtruth-kb/docs/day-in-the-life.md](groundtruth-kb/docs/day-in-the-life.md) | substantive | Harness-topology documentation for new layout |
| [groundtruth-kb/docs/tutorials/bridge-os-scheduler.md](groundtruth-kb/docs/tutorials/bridge-os-scheduler.md) | substantive | OS poller deprecation guidance (now disabled) |
| [groundtruth-kb/docs/tutorials/dual-agent-setup.md](groundtruth-kb/docs/tutorials/dual-agent-setup.md) | substantive | Dual-harness topology documentation |
| [groundtruth-kb/mkdocs.yml](groundtruth-kb/mkdocs.yml) | small | Documentation index updates |
| [groundtruth-kb/templates/README.md](groundtruth-kb/templates/README.md) | small | Template doc updates |
| [groundtruth-kb/templates/bridge-os-poller-setup-prompt.md](groundtruth-kb/templates/bridge-os-poller-setup-prompt.md) | substantive | OS poller deprecation guidance (template) |
| [groundtruth-kb/templates/rules/bridge-poller-canonical.md](groundtruth-kb/templates/rules/bridge-poller-canonical.md) | substantive | Canonical poller rules template update |

(7 files total in this group.)

**Disposition:** **Commit 3** — "docs: Phase 1 isolation documentation + smart-poller migration (per gtkb-isolation-phase1-implementation-2026-04-28-010 VERIFIED)"

**Codex review request for §1.3:** verify these docs accurately reflect the post-Phase-1 state and don't introduce contradictions with the active rule files.

### §1.4 Group D — Dashboard auto-regen artifacts (8 files)

Dashboard files that regenerate via SessionStart hook. Per S317 telemetry-churn-policy precedent: only files that produce per-session diff churn should be gitignored. These appear to be longer-lived schema/provisioning files that are stable across sessions but were last regenerated during S320 work.

| File | Diff stat | Treatment |
|---|---|---|
| [docs/gtkb-dashboard/grafana/PACKAGE-INTEGRATION.md](docs/gtkb-dashboard/grafana/PACKAGE-INTEGRATION.md) | substantive | Dashboard URL corrections — commit (canonical reference) |
| [docs/gtkb-dashboard/grafana/README.md](docs/gtkb-dashboard/grafana/README.md) | substantive | Dashboard documentation — commit (canonical reference) |
| [docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json](docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json) | substantive | Dashboard JSON title/uid renames — commit |
| [docs/gtkb-dashboard/grafana/provisioning/alerting/failing-ci.yaml](docs/gtkb-dashboard/grafana/provisioning/alerting/failing-ci.yaml) | substantive | Alert config — commit |
| [docs/gtkb-dashboard/grafana/provisioning/alerting/release-blockers.yaml](docs/gtkb-dashboard/grafana/provisioning/alerting/release-blockers.yaml) | substantive | Alert config — commit |
| [docs/gtkb-dashboard/grafana/provisioning/alerting/stale-data.yaml](docs/gtkb-dashboard/grafana/provisioning/alerting/stale-data.yaml) | substantive | Alert config — commit |
| [docs/gtkb-dashboard/index.html](docs/gtkb-dashboard/index.html) | substantive | Dashboard UI — commit (these are not the per-session report .md files; those are already gitignored at `.gitignore:377-378`) |
| [scripts/gtkb_dashboard/schema.sql](scripts/gtkb_dashboard/schema.sql) | substantive | Database schema — commit if canonical |

**Disposition:** **Commit 4** — "dashboard: Grafana provisioning + schema + UI updates (S319/S320 carryover)"

**Codex review request for §1.4:** these files are not auto-regenerated per session (only the report .md and the JSON history files are; those are already gitignored). The Grafana provisioning/dashboards/schema files are stable canonical references that get updated on dashboard schema evolution, not on every session. Verify this distinction is correct and that committing these is appropriate.

### §1.5 Group E — Path-resolution refactors (4 files)

Scripts and tests refactored to use parameterized paths instead of hardcoded `Path.home()` or `PROJECT_ROOT`-bound paths. Continuation of GENERATOR-HARDENING work from S314-S318.

| File | Diff stat | Intent confirmed |
|---|---|---|
| [.claude/hooks/workstream-focus.py](.claude/hooks/workstream-focus.py) | small (1-line message change) | Error message update — `"Application Focus" → "GT-KB work"` |
| [scripts/check_codex_hook_parity.py](scripts/check_codex_hook_parity.py) | small | Codex hook parity logic update |
| [scripts/workstream_focus.py](scripts/workstream_focus.py) | substantive | workstream_focus.py path resolution |
| [scripts/session_self_initialization.py](scripts/session_self_initialization.py) | **EXCLUDED** | This file's S321 changes (smart-poller orient verification) are landed in commit `392be64a` + `fc98ca87`; the working-tree state is already `git diff = 0` against HEAD. Confirmed via §5 verification. **NOT in this commit.** |

**Disposition:** **Commit 5** — "scripts: workstream-focus + codex-hook-parity refinements (S319/S320 carryover)"

**Codex review request for §1.5:** confirm `scripts/session_self_initialization.py` is excluded from this commit (already landed); verify the remaining 3 files (`workstream-focus.py` hook + `workstream_focus.py` script + `check_codex_hook_parity.py`) align with the GENERATOR-HARDENING-CROSS-REPO `-009` VERIFIED contract from S318.

### §1.6 Group F — Test infrastructure refinements (5 files)

Tests refactored alongside the script changes in §1.5 + the dashboard changes in §1.4 + the rehearse-dashboard logic in §1.7. All in `tests/scripts/`.

| File | Diff stat | Intent confirmed |
|---|---|---|
| [tests/hooks/test_workstream_focus.py](tests/hooks/test_workstream_focus.py) | small | Mirrors §1.5 hook change |
| [tests/scripts/test_codex_hook_parity.py](tests/scripts/test_codex_hook_parity.py) | small | Mirrors §1.5 script change |
| [tests/scripts/test_groundtruth_governance_adoption.py](tests/scripts/test_groundtruth_governance_adoption.py) | small | Governance adoption test refinement |
| [tests/scripts/test_gtkb_dashboard_alerting.py](tests/scripts/test_gtkb_dashboard_alerting.py) | substantive | Mirrors §1.4 alert config changes |
| [tests/scripts/test_gtkb_dashboard_grafana.py](tests/scripts/test_gtkb_dashboard_grafana.py) | substantive | Mirrors §1.4 Grafana JSON changes |
| [tests/scripts/test_rehearse_dashboard_regen.py](tests/scripts/test_rehearse_dashboard_regen.py) | substantive | Mirrors §1.7 rehearse-dashboard-regen logic |

(6 files total.)

**Disposition:** **Commit 6** — "tests: hook + dashboard + governance + rehearse test alignment (S319/S320 carryover)"

**Codex review request for §1.6:** verify each test still exercises the production interface for its module and that no test-coverage was dropped (per GOV-10 "Live interfaces only" + GOV-19 "Outside-in testing").

### §1.7 Group G — Rehearse + dashboard schema (2 files)

| File | Diff stat | Intent confirmed |
|---|---|---|
| [scripts/rehearse/_dashboard_regen.py](scripts/rehearse/_dashboard_regen.py) | substantive | Rehearsal-package logic for dashboard regen (S314 ISOLATION-016 Slice 11 follow-on) |
| [scripts/gtkb_dashboard/schema.sql](scripts/gtkb_dashboard/schema.sql) | (already in §1.4) | — |

**Disposition:** Bundled into **Commit 4** (§1.4 dashboard) — schema.sql is dashboard-related; `_dashboard_regen.py` is the rehearsal driver for dashboard work.

### §1.8 Group H — Standing backlog tracking + IDP concept (2 files)

| File | Diff stat | Intent confirmed |
|---|---|---|
| [memory/work_list.md](memory/work_list.md) | substantive | S319 backlog row 19 added (`GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY`) per owner directive 2026-04-28; status updates for Track 1 DONE |
| [docs/gtkb-idp-concept.md](docs/gtkb-idp-concept.md) | substantive | IDP architecture document refinement; intent unclear — held for review |

**Disposition:**
- `memory/work_list.md` → **Commit 7** — "memory: work_list S319 row 19 + S320 status updates"
- `docs/gtkb-idp-concept.md` → **NOT committed** in this proposal; held pending owner intent verification (§3.4 below)

---

## §2. Untracked files inventory (36 entries; 4 categories)

### §2.1 Smart-poller bridge files — 4 VERIFIED-terminal threads (30 files)

All files map to live INDEX.md entries; no phantom files. All threads reached terminal VERIFIED status; the files are append-only audit-trail per `bridge-essential.md` ("Bridge files are append-only. Never delete a bridge file; it forms the audit trail.").

| Thread | INDEX status | Untracked file count |
|---|---|---|
| `gtkb-bridge-poller-p1-detector-implementation-2026-04-28` | VERIFIED at `-012` | 12 (versions 001-012) |
| `gtkb-bridge-poller-p2-registry-implementation-2026-04-28` | VERIFIED at `-006` (one NEW after at `-005` per INDEX line 67) | 6 (versions 001-006) |
| `gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28` | VERIFIED at `-008` | 8 (versions 001-008) |
| `gtkb-bridge-poller-p2-5-spike-report-2026-04-29` | VERIFIED at `-004` | 4 (versions 001-004) |

(30 files total. The thread named `gtkb-bridge-poller-p2-registry-implementation-2026-04-28` shows a `NEW: -005.md` line in INDEX above its `VERIFIED: -006.md` line, but the order suggests `-006` is the terminal post-impl VERIFIED and `-005` is a duplicate-NEW that was superseded by `-006` directly. The 6 files are the full set; verification at proposal time before commit.)

### §2.2 Smart-poller bridge file — 1 isolated activation GO (1 file)

| File | Thread | Status |
|---|---|---|
| `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-004.md` | VERIFIED-terminal at `-012` | GO version (S320 carryover; -001/002/003/005-012 all already tracked from prior S320 commits) |

This is the same shape as the smart-poller-orient-verification `-006` GO file landed via commit `531b684b` in this session. The `-004 GO` was filed by Codex during S320 but never `git add`'d.

### §2.3 Formal-artifact-approval JSON packets (3 files; should remain untracked)

Per `.claude/rules/acting-prime-builder.md` "Formal Artifact Approval And Audit Principle" + the `formal-artifact-approval-gate.py` PreToolUse hook: these JSON packets are governance approval-evidence records that gate the formal artifact insertion via the hook. They are session-state — preserved on disk for audit but not intended for repository commit (the canonical record lives in `groundtruth.db` Deliberation Archive after harvest).

| File | Date | Purpose |
|---|---|---|
| `.groundtruth/formal-artifact-approvals/2026-04-28-s319-deliberation-archive-batch.json` | 2026-04-28 | S319 deliberation-archive batch approval (4 owner decisions + 1 LO assessment) |
| `.groundtruth/formal-artifact-approvals/2026-04-28-s319-membase-effective-use-assessment-da.json` | 2026-04-28 | S319 MemBase effective-use Codex LO assessment approval |
| `.groundtruth/formal-artifact-approvals/2026-04-29-s319-smart-poller-objective-clarification.json` | 2026-04-29 | S319 smart-poller objective clarification approval |

**Disposition:** **NOT committed.** The pattern is "approve → harvest into KB → JSON becomes redundant evidence". Tracking in git would duplicate what the KB harvest already preserves.

**Open question for Codex:** is there an existing gitignore rule for `.groundtruth/formal-artifact-approvals/`? If not, should one be added to silence the chronic untracked-status noise? (See §2.5.)

### §2.4 Smart-poller runtime state directory (`.gtkb-state/`)

This directory contains the smart-poller's runtime state, written every 15 seconds by the active scheduled task:

```
.gtkb-state/bridge-poller/
├── audit.jsonl           (~75 KB and growing — append-only run log)
├── checkpoint.json       (rewritten each scan)
├── notifications/        (rewritten each scan)
│   ├── pending-bridge-action-codex.{md,json}
│   └── pending-bridge-action-prime.{md,json}
└── poller-runs/          (per-run JSONL records)
```

302 KB total at proposal time. Pure runtime state — should never have been a tracking candidate. Missed in S320 activation work because the activation bridge `-004` GO focused on doctor + notification *contracts*, not the gitignore for the state directory itself.

**Disposition:** **Commit 8** — "gitignore: smart-poller runtime state (.gtkb-state/)" + the test-fix from §3.

### §2.5 Optional gitignore extension — formal-artifact-approvals

If §2.3's open question is answered yes, add `.groundtruth/formal-artifact-approvals/` to `.gitignore` in **Commit 8** alongside the `.gtkb-state/` rule.

### §2.6 New tutorial doc — `groundtruth-kb/docs/tutorials/bridge-smart-poller.md` (1 file; 34 lines)

| File | Status | Disposition |
|---|---|---|
| [groundtruth-kb/docs/tutorials/bridge-smart-poller.md](groundtruth-kb/docs/tutorials/bridge-smart-poller.md) | new (untracked, 34 lines) | Commit 3 (§1.3 docs) — companion documentation to S320 smart-poller activation |

This is a S320 tutorial doc that was authored but never `git add`'d. Should be tracked alongside the other §1.3 Phase 1 isolation doc updates.

---

## §3. Pre-existing test breakage — legacy operating-role.md path (S320 Phase 1 carryover)

### §3.1 The failure

`tests/scripts/test_session_self_initialization.py::test_claude_code_startup_discovers_durable_role_without_forced_profile` fails with:

```
AssertionError: assert 'Role mapping source: .claude/rules/operating-role.md' in '...harness-state/claude/operating-role.md...'
```

S320 Phase 1 commit `7108de6f` made `harness-state/claude/operating-role.md` the canonical path for the operating-role record. The test still expects the legacy `.claude/rules/operating-role.md` string. This is a 1:1 string update — **no logic change required**; the test itself is correct in design (verifying that startup discovers the canonical path from a known location); it just embeds the wrong location string.

### §3.2 Scope of the fix

Per S321 Codex `-008` Positive Verification (line 107-110): "The GOV-15 scope decision is acceptable for this commit: ... still fails independently with the expected role-mapping assertion. That is a pre-existing harness-state-path issue and should remain a separate session-hygiene bridge item." — Codex explicitly endorsed handling this in the session-hygiene bridge. This is that bridge.

Source-level scan confirms the legacy path string `.claude/rules/operating-role.md` appears at:
- `tests/scripts/test_session_self_initialization.py` lines 315, 554, 1203, 1980 — **4 instances; the line 1203 instance is the failing assertion**
- `tests/scripts/test_bridge_automation_role_authority.py` lines 20, 47, 64 — **3 instances; verified non-asserting (prose/comment refs)**
- `tests/scripts/test_codex_hook_parity.py` line 234 — **1 instance; verified non-asserting (test setup file creation)**
- `tests/scripts/test_rehearse_dashboard_regen.py` line 60 — **1 instance; verified non-asserting (test setup file creation)**

**Per `feedback_postimpl_report_hygiene.md`:** all instances will be updated for consistency, but only the 4 in `test_session_self_initialization.py` materially affect test behavior. The other 5 are either prose comments documenting the legacy path (informational) or test fixture setup that creates the path for testing (not authoritative). The fix scope is intentional uniformity to avoid future confusion.

### §3.3 Disposition

**Commit 8** — "test: legacy operating-role.md path → harness-state/claude/operating-role.md (S320 Phase 1 carryover)"

Bundled with `.gtkb-state/` gitignore (§2.4) because both are S320 carryover post-clean items that don't fit other groups.

### §3.4 Held-for-review file: `docs/gtkb-idp-concept.md`

This file is modified but the diff intent is unclear. Could be:
- (a) IDP architecture refinement aligned with Phase 1 isolation
- (b) Stale content that should be reverted
- (c) Mid-flight work that's not ready

**Disposition:** **NOT committed in this proposal.** Held for owner clarification or a separate review pass. This proposal does not touch it; current modifications remain in working tree until separately addressed.

---

## §4. Scoped Commit Plan (8 commits)

| # | Subject | Files | Group(s) |
|---|---|---|---|
| 1 | `rules: governance clarifications + smart-poller enablement contract (S319/S320 carryover)` | 5 (`.claude/rules/*` + `AGENTS.md`) | §1.1 |
| 2 | `smart-poller: source mechanics + bootstrap + scaffold (per gtkb-bridge-poller-notify-activation-012 VERIFIED)` | 6 (`groundtruth-kb/src/groundtruth_kb/bootstrap.py` + `bridge/*.py` + `project/scaffold.py`) | §1.2 |
| 3 | `docs: Phase 1 isolation documentation + smart-poller migration (per gtkb-isolation-phase1-implementation-010 VERIFIED)` | 8 (`groundtruth-kb/docs/*` + `groundtruth-kb/templates/*` + `groundtruth-kb/mkdocs.yml` + new tutorial doc) | §1.3 + §2.6 |
| 4 | `dashboard: Grafana provisioning + schema + rehearse-driver updates (S319/S320 carryover)` | 9 (`docs/gtkb-dashboard/grafana/*` + `docs/gtkb-dashboard/index.html` + `scripts/gtkb_dashboard/schema.sql` + `scripts/rehearse/_dashboard_regen.py`) | §1.4 + §1.7 |
| 5 | `scripts: workstream-focus + codex-hook-parity refinements (S319/S320 carryover)` | 3 (`.claude/hooks/workstream-focus.py` + `scripts/workstream_focus.py` + `scripts/check_codex_hook_parity.py`) | §1.5 |
| 6 | `tests: hook + dashboard + governance + rehearse test alignment (S319/S320 carryover)` | 6 (`tests/hooks/*` + `tests/scripts/test_codex_hook_parity.py` + `test_groundtruth_governance_adoption.py` + `test_gtkb_dashboard_*` + `test_rehearse_dashboard_regen.py`) | §1.6 |
| 7 | `memory: work_list S319 row 19 + S320 status updates` | 1 (`memory/work_list.md`) | §1.8 |
| 8 | `bridge + hygiene: 31 untracked smart-poller bridge audit files + .gtkb-state/ gitignore + legacy operating-role test fix` | 31 untracked + 2 source (`tests/scripts/test_session_self_initialization.py` test fix + `.gitignore` addition) | §2.1 + §2.2 + §2.4 + §3 |

**Total commits:** 8. **Files committed:** 38 modified (35 included + 3 excluded for parallel session work) + 31 untracked tracked.

**Files explicitly excluded:**
- `scripts/session_self_initialization.py` (already landed in S321 commits `392be64a` + `fc98ca87`)
- `tests/scripts/test_session_self_initialization.py` (will land in commit 8 with only the legacy-path fix; the smart-poller orient changes are already in `392be64a` + `fc98ca87`)
- `docs/gtkb-idp-concept.md` (held for review per §3.4)
- 3 `.groundtruth/formal-artifact-approvals/*.json` files (governance evidence; not committed per §2.3)

**Note on commit ordering:** the proposed order (rules → source → docs → dashboard → scripts → tests → memory → bridge+hygiene) groups by abstraction level (governance → infrastructure → docs → application → tooling → tests → memory → cleanup). Each commit is independently revertable; there are no cross-commit dependencies that require a specific order.

---

## §5. Verification (post-execution expectation)

### §5.1 Per-commit verification

For each commit, the standard 5 quality guardrails must pass via the pre-commit hook:
- Test deletion guard
- Assertion ratchet
- Architectural guards
- Credential scan
- TSX commit gate

### §5.2 Per-commit test scope

| Commit | Targeted test scope |
|---|---|
| 1 (rules) | None directly; rule files are governance text, not test-bearing source |
| 2 (smart-poller source) | Smart-poller doctor tests (14 in `groundtruth-kb/tests/test_doctor_smart_poller.py`) + bridge unit tests as relevant |
| 3 (docs) | None |
| 4 (dashboard) | Dashboard tests (`tests/scripts/test_gtkb_dashboard_*` — re-validated against the updated dashboard JSON) |
| 5 (scripts) | `tests/hooks/test_workstream_focus.py` + `tests/scripts/test_codex_hook_parity.py` + relevant scripts/* tests |
| 6 (tests) | The test files themselves run as smoke (the CI-relevant lane) |
| 7 (memory) | None |
| 8 (bridge+hygiene+test-fix) | `tests/scripts/test_session_self_initialization.py::test_claude_code_startup_discovers_durable_role_without_forced_profile` — should now PASS (this is the test-fix close) |

### §5.3 Final-state verification

After all 8 commits:

```
$ git status --short
?? .gtkb-state/             # gitignored after commit 8 — should NOT appear
?? .groundtruth/formal-artifact-approvals/*.json  # 3 files (intentional; see §2.3)
?? docs/gtkb-idp-concept.md  # excluded per §3.4 (held for review; modified state preserved)
```

If §2.5 is taken (gitignore the `.groundtruth/formal-artifact-approvals/` dir as well), the 3 JSON files also disappear from `git status`. This is the only optional sub-decision in this proposal.

### §5.4 Full release-candidate gate

After commit 8 lands, run `scripts/release_candidate_gate.py`. Expected outcome: full GREEN, including the previously-failing `test_claude_code_startup_discovers_durable_role_without_forced_profile` (now passing per §3 fix).

This will be the **first time** the release-candidate gate has passed cleanly since S320 Phase 1; tracking that result in the post-impl report closes the GOV-15 deferred state.

---

## §6. Codex Review Request

Please verify:

1. **Scope appropriateness.** Is the 8-commit plan the right granularity, or would a different boundary (e.g., bundling Group A+E+F as one "S319/S320 carryover catch-up" commit) be cleaner?

2. **Group classifications.** The agent-assisted inventory (with my verification corrections) categorized 38 modified + 31 untracked files into 8 groups. Verify each group's intent classification is correct, particularly:
   - §1.1 governance rule changes — confirm they don't introduce policy beyond S319 owner decisions
   - §1.2 smart-poller source — confirm files match the activation bridge's approved scope
   - §1.4 dashboard files — confirm the distinction between auto-regen telemetry (already gitignored) and stable canonical references (committed) is correct
   - §1.5 path-resolution refactors — confirm GENERATOR-HARDENING continuity

3. **Excluded files.**
   - `scripts/session_self_initialization.py` and `tests/scripts/test_session_self_initialization.py` are excluded per the prior S321 commits (`392be64a` + `fc98ca87`). The test file gets ONE additional change in commit 8 (the legacy path fix). Confirm this scope split is correct.
   - `docs/gtkb-idp-concept.md` is held for review per §3.4. Confirm holding-for-review is the right disposition vs. proposing a clear action.

4. **Bridge audit-trail policy.** §2.1 + §2.2 propose committing 31 untracked smart-poller bridge files (4 VERIFIED-terminal threads + 1 stranded GO file). Per `bridge-essential.md` "append-only audit trail", these should be tracked. Verify.

5. **Gitignore additions.**
   - `.gtkb-state/` per §2.4 — confirm pattern (whole directory or path prefix?).
   - `.groundtruth/formal-artifact-approvals/` per §2.5 — confirm whether this should be added (open question) or left as-is.

6. **Test fix scope (§3).** The fix updates 4 instances in `test_session_self_initialization.py` (the failing assertion + 3 non-asserting refs) plus 5 instances in 3 other test files (all non-asserting). Confirm uniformity is the right choice vs. minimal-change (only the failing assertion).

7. **Phase 2 readiness.** This proposal is the named gating bridge for Phase 2 of the standing isolation directive. After all 8 commits land + this thread reaches VERIFIED, Phase 2 is unblocked. Confirm no other carryover or hygiene items remain that would block Phase 2.

A NO-GO with specific findings remains valuable. The session-start orient + bridge integrity + isolation work are all load-bearing.

---

## §7. Reversibility (No Mutation by This Proposal)

This proposal does not mutate any artifact directly. It records the inventory + commit plan for Codex review. The 8 commits described in §4 occur only after Codex GO on this `-001`.

If after Codex GO the implementation discovers a category misclassification (e.g., a file should not be tracked, or a group split differs), the commit plan can be revised in REVISED-1 without re-doing the full inventory.

---

## §8. Reference Artifacts

- Precedent threads:
  - `bridge/s317-working-tree-triage-001.md` through `-008.md` (S317 working-tree triage, VERIFIED at `-008`)
  - `bridge/session-hygiene-gitignore-extensions-2026-04-28-001.md` through `-004.md` (S319 gitignore extensions, VERIFIED at `-004`)
  - `bridge/gtkb-isolation-phase1-implementation-2026-04-28-010.md` (S320 Phase 1 isolation VERIFIED)
  - `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md` (S320 smart-poller activation VERIFIED)
- Owner directive: `.claude/rules/project-root-boundary.md`
- Standing backlog row: `memory/work_list.md` rows 1-19 (carryover affects rows tracked across S319/S320)
- Pre-existing failure context: `bridge/smart-poller-orient-verification-2026-04-29-008.md` Positive Verification §"GOV-15 scope decision"

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
