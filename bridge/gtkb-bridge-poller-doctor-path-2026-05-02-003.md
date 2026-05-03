REVISED

# Implementation Proposal — Smart-Poller Doctor-Path Fix (REVISED-1)

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Subject: Redirect `_check_bridge_poller` to read smart-poller state from its current output path; fix schema fields; add BOM-tolerant decode; reconcile rule-text drift in `.claude/rules/bridge-essential.md`.
Supersedes: `bridge/gtkb-bridge-poller-doctor-path-2026-05-02-001.md` (NEW), `-002.md` (NO-GO).

## Revision Rationale (REVISED-1)

Codex NO-GO at `-002.md` issued one blocking finding (F1: GOV-19 coverage mapped only to private helper) with explicit revision guidance. Direction (`_check_bridge_poller` redirect to `dispatch-state.json`, schema field fixes, BOM tolerance, narrow rule-text reconciliation) was approved.

Changes in this revision:
1. **Test Plan rewritten** to exercise the public `run_doctor(target, profile="dual-agent")` surface for spec-counted coverage. Helper-level tests are explicitly demoted to "Supplemental Internal Coverage" with non-substituting labels per `GOV-19-A1`.
2. **Acceptance Criteria expanded** to require public doctor surface coverage for the five behavior bands (fresh, warning, fail, missing-file warning, BOM tolerance) plus visible agent-mapping (claude→prime, codex→codex) in the public report.
3. **Verification Commands updated** to the repo-native, Windows-safe form Codex demonstrated in `-002.md` Non-Blocking Note 3: `uv run --project groundtruth-kb gt --config groundtruth.toml project doctor --dir . --profile dual-agent`. The pipe-to-grep form is removed.
4. Source-code change scope is unchanged (Codex Recommended Action: "The source-code change itself can stay narrow").

## Context

Owner directive 2026-05-02: "The smart-poller must be restored to full function." Live state probe (this session, 2026-05-02 06:05 UTC) shows the smart poller is running healthily — `wscript.exe` + `pythonw.exe bridge_poller_runner.py --interval 15`, single-instance lock at `.gtkb-state/bridge-poller/bridge-poller-runner.lock`, audit log writing every ~15s (4,030+ iterations × 15s ≈ 16.8h+ uptime since `2026-05-01T13:15:11Z` run-id), `dispatch-state.json` updated 2026-05-02T06:05:19+00:00.

`gt project doctor` for the live system reports two contradictory results in the same run:

- **PASS:** `_check_smart_bridge_poller` at `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1381` (the activation-chain check) sees the live smart poller.
- **FAIL:** `_check_bridge_poller(..., "claude")` and `_check_bridge_poller(..., "codex")` at `doctor.py:1830–1831` are reading retired/legacy state files written by the now-removed OS pollers (S308 halt, 2026-04-25). Those legacy files at `independent-progress-assessments/bridge-automation/logs/{claude,codex}-scan-status.json` have a UTF-8 BOM; the smart poller does not write to those paths at all.

The two checks are right about *different* surfaces. `_check_smart_bridge_poller` is current. `_check_bridge_poller` has stale path constants.

## Specification Links

1. **`.claude/rules/bridge-essential.md` §"Poller Enablement Contract"** — condition 3 ("`gt platform doctor` or an equivalent verification command reports the smart poller infrastructure healthy"). The doctor's per-agent freshness check is the mechanical predicate for this condition; today it FAILs against a healthy poller because of stale paths.
2. **`.claude/rules/bridge-essential.md` §"Operational Mode"** — current text says "Until the smart poller is available and functioning, bridge scans remain manual in both directions." Live state contradicts this. Reconciliation is in scope (narrow, per Codex Recommended Action).
3. **Umbrella bridge** `bridge/gtkb-bridge-poller-001-smart-poller-007.md` GO — the smart-poller program. This proposal is a follow-on cleanup, not a new sub-track.
4. **Activation bridge** `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-004.md` GO — activated the smart poller end-to-end. `_BRIDGE_STATUS_PATHS` was never migrated as part of this activation; this proposal closes that gap.
5. **`GOV-19` Outside-in testing** — KB row, `GOV-19-A1` assertion (verified by Codex `-002.md` line 41–45 query): "new spec-linked tests must exercise observable surfaces before being counted as coverage; internal unit tests are supplemental only." This revision aligns the test plan to that assertion.
6. **`GOV-20` Architecture decisions** — change is small enough to skip ADR/DCL; ships an IPR + CVR pair.
7. **Probed source-of-truth schemas** (live, this session, also confirmed by Codex Non-Blocking Note 1):
   - `.gtkb-state/bridge-poller/dispatch-state.json` schema_version 1: top-level `recipients.{prime,codex}` with fields `updated_at` (ISO8601 with timezone), `last_result` ∈ {`unchanged`, `no_pending`, dispatch-result-string}, `pending_count`, `raw_pending_count`, `filtered_terminal_count`, `signature`.
   - `.gtkb-state/bridge-poller/notifications/pending-bridge-action-{prime,codex}.json` schema_version 3 (informational; this proposal does not depend on it).
8. **Public doctor surface** — `run_doctor(target: Path, profile: str, *, auto_install: bool = False) -> DoctorReport` at `doctor.py:1785–1790`. Bridge-poller checks added inside `if p.includes_bridge:` at lines 1830–1831. CLI exposes `gt project doctor` per Codex `-002.md` line 47 citation (`groundtruth-kb/src/groundtruth_kb/cli.py:846–864`).
9. **Prior Deliberations search:** Codex ran `uv run --project groundtruth-kb gt --config groundtruth.toml deliberations search "smart poller doctor health check" --limit 5` in `-002.md` Prior Deliberations section; result: no matching deliberations. Active prior context is the umbrella `-007` and activation `-004` cited above.

## Scope

### In-scope (unchanged from `-001`)

Files modified:
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — replace `_BRIDGE_STATUS_PATHS` (lines 1127–1130) with a single `_BRIDGE_DISPATCH_STATE_PATH` constant pointing at `.gtkb-state/bridge-poller/dispatch-state.json`. Modify `_check_bridge_poller(target, agent)` (lines 1156–1266) to (a) read the single dispatch-state file, (b) map `agent` argument values "claude"→"prime" and "codex"→"codex" via `_BRIDGE_AGENT_TO_RECIPIENT` dict, (c) read `recipients[role].updated_at` instead of top-level `updatedAtUtc`, (d) derive `state_display` from `last_result` and `pending_count`, (e) decode with `utf-8-sig` for forward-compatibility, (f) preserve all three age thresholds and result statuses. Touch is confined to the bridge smart-poller liveness block (lines 1125–1266).
- `.claude/rules/bridge-essential.md` — narrow update to §"Operational Mode" acknowledging that the smart poller is now active and that the doctor health check is the canonical predicate; preserve §"Poller Enablement Contract" wording.
- Existing tests under `groundtruth-kb/tests/` covering the per-agent bridge-poller check — probed during implementation and updated in the same commit, or replaced with a new test file `groundtruth-kb/tests/test_doctor_bridge_poller.py` if no public-surface coverage exists today.

Documents (per GOV-20):
- `IPR-BRIDGE-POLLER-DOCTOR-PATH-001` — pre-implementation review.
- `CVR-BRIDGE-POLLER-DOCTOR-PATH-001` — post-impl proof.

### Out-of-scope (unchanged from `-001`)

- Row 22 GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT.
- Row 23 GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR.
- Umbrella P3 invoker design and P7-P8 Agent-Red adopter follow-up tracks.
- Other doctor-flagged failures (DA harvest 0/6, missing hooks, `canonical-terminology.toml`, `scanner-safe-writer.py`, product-scope writability, `work_list.md` heuristic flags, deprecated `workstream-focus.py`).
- Adding new dispatch-stalled checks or per-agent notification checks (feature additions).

## Implementation Plan (unchanged from `-001`)

1. Probe `_BRIDGE_STATUS_PATHS` callers across `groundtruth-kb/` (grep) — should be zero callers outside `_check_bridge_poller` itself; reported in post-impl.
2. Probe existing tests for `_check_bridge_poller` / public bridge-poller behavior — exact test files reported in post-impl.
3. Replace constants:
   ```python
   _BRIDGE_DISPATCH_STATE_PATH = Path(".gtkb-state/bridge-poller/dispatch-state.json")
   _BRIDGE_AGENT_TO_RECIPIENT = {"claude": "prime", "codex": "codex"}
   ```
4. Rewrite `_check_bridge_poller` body to read the single state file once, navigate `recipients[role]`, parse `updated_at`, compute `age_secs`, return per-agent `ToolCheck`. Use `path.read_bytes().decode("utf-8-sig")` for BOM tolerance.
5. Update message strings to surface `last_result` and `pending_count` (e.g., "state: unchanged, pending: 21").
6. Update / add tests per the revised Test Plan (below).
7. Reconcile `.claude/rules/bridge-essential.md` §"Operational Mode" — narrow text edit only.
8. File IPR-BRIDGE-POLLER-DOCTOR-PATH-001 (pre-implementation) and CVR-BRIDGE-POLLER-DOCTOR-PATH-001 (post-implementation) per GOV-20 advisory pilot.
9. Run `uv run --project groundtruth-kb gt --config groundtruth.toml project doctor --dir . --profile dual-agent` to confirm per-agent PASS against the live poller; capture full output in the post-impl report.

## Test Plan (REVISED — outside-in via `run_doctor`)

Tests live in `groundtruth-kb/tests/test_doctor_bridge_poller.py` (or extend the existing test file identified during implementation probe).

Each primary test calls `run_doctor(fixture_target, profile="dual-agent")`, then filters the returned `DoctorReport.checks` by `ToolCheck.name` (`"Claude bridge poller"` and `"Codex bridge poller"` per `_check_bridge_poller` line 1169) and asserts the observable status/message. **These are the spec-counted tests for `GOV-19-A1` purposes.**

### Primary tests (public `run_doctor` surface — GOV-19 spec coverage)

| # | Test | Spec / behavior covered | Surface exercised |
|---|---|---|---|
| TP1 | `test_run_doctor_reports_pass_for_both_agents_when_fresh` | `bridge-essential.md` §"Poller Enablement Contract" condition 3 | `run_doctor(fixture, "dual-agent")` against fixture with `recipients.{prime,codex}.updated_at` set to now → both per-agent checks have `status="pass"` |
| TP2 | `test_run_doctor_reports_warning_when_4_to_10_min_old` | `_BRIDGE_FRESH_SECS` boundary visible in public report | fixture with `updated_at` 5 minutes ago → both per-agent checks have `status="warning"` in `DoctorReport.checks` |
| TP3 | `test_run_doctor_reports_fail_when_over_10_min_old` | `_BRIDGE_WARN_SECS` boundary visible in public report | fixture with `updated_at` 15 minutes ago → both per-agent checks have `status="fail"` |
| TP4 | `test_run_doctor_reports_warning_when_state_file_absent` | not-started semantics through public surface | empty state dir → both per-agent checks have `status="warning"`, message references `_BRIDGE_SCHEDULER_DOC` |
| TP5 | `test_run_doctor_handles_utf8_bom_in_state_file_gracefully` | defensive forward-compat via public surface | fixture with `﻿`-prefixed valid JSON → public report shows expected status (not a parse failure) |
| TP6 | `test_run_doctor_message_includes_pending_count` | observable message content for operator visibility | fixture with `pending_count=21` → at least one per-agent message in `DoctorReport.checks` contains "pending: 21" |
| TP7 | `test_run_doctor_distinguishes_claude_from_codex_recipients_in_report` | agent-mapping (claude→prime, codex→codex) visible to operator | fixture with `prime.updated_at` fresh and `codex.updated_at` 15 minutes old → public report shows `"Claude bridge poller"` PASS and `"Codex bridge poller"` FAIL (or equivalent state difference) |

### Supplemental internal coverage (helper-level — non-substituting per GOV-19-A1)

These tests are explicitly **not counted as primary GOV-19 coverage**; they exercise edge cases of `_check_bridge_poller` directly that are awkward to reach via the public surface alone (e.g., schema-shape regressions). They are kept to prevent regressions on internal contract behavior.

| # | Test | Behavior covered | Surface exercised |
|---|---|---|---|
| TS1 | `test_check_bridge_poller_returns_fail_when_recipients_key_missing` | helper schema validation | direct `_check_bridge_poller` call with fixture missing `recipients` → `status="fail"` |
| TS2 | `test_check_bridge_poller_returns_fail_when_role_key_missing` | helper schema validation | direct call with fixture missing `recipients.prime` → `status="fail"` |
| TS3 | `test_check_bridge_poller_handles_unparseable_updated_at` | helper input-validation | direct call with malformed `updated_at` string → `status="fail"` |

The supplemental tests' file location should make their non-substituting status visible — either inside a class named `class TestCheckBridgePollerHelperEdgeCases` (with a docstring noting GOV-19-A1 supplemental status) or in a sibling file `test_doctor_bridge_poller_helper.py` with an opening module docstring.

## Verification Commands (REVISED — Windows-safe, repo-native)

The post-implementation report will include exact commands and observed output:

- `uv run --project groundtruth-kb gt --config groundtruth.toml project doctor --dir . --profile dual-agent` — full doctor run; confirm `Claude bridge poller: OK` and `Codex bridge poller: OK` lines against the live smart-poller (per Codex `-002.md` Non-Blocking Note 3).
- `uv run --project groundtruth-kb pytest groundtruth-kb/tests/test_doctor_bridge_poller.py -v` (or the existing test file path identified during implementation probe).
- `uv run --project groundtruth-kb pytest groundtruth-kb/tests/test_doctor_*.py -v` — regression sweep across all doctor tests.
- `uv run --project groundtruth-kb ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_bridge_poller.py`.

## Risk and Rollback (unchanged from `-001`)

- **Risk: schema drift between proposal time and implementation.** `dispatch-state.json` `schema_version: 1` is stable today (Codex confirmed in `-002.md` Non-Blocking Note 1); if the smart-poller bumps schema_version between proposal and impl, the implementation must read the bumped fields. Mitigation: implementation re-probes the live schema as the first step.
- **Risk: legacy paths still referenced elsewhere.** Mitigation: implementation greps for `claude-scan-status` / `codex-scan-status` repo-wide; reports findings; either updates them in the same commit or files them as separate items.
- **Rollback:** revert the implementation commit; original behavior returns. No DB schema changes; no bridge-protocol-level dependencies.

## Acceptance Criteria (REVISED — public-surface explicit)

A post-implementation report shall be filed when ALL of the following hold:
- `uv run --project groundtruth-kb gt --config groundtruth.toml project doctor --dir . --profile dual-agent` reports per-agent `Claude bridge poller: OK` and `Codex bridge poller: OK` against the live smart-poller. Output captured verbatim in post-impl.
- TP1–TP7 (primary, public-surface) pass under `uv run --project groundtruth-kb pytest`.
- TS1–TS3 (supplemental, helper-level) pass — included as additional coverage, not as the GOV-19-A1 spec proof.
- Existing doctor tests still pass (regression sweep).
- Ruff clean on modified and new files.
- IPR-BRIDGE-POLLER-DOCTOR-PATH-001 and CVR-BRIDGE-POLLER-DOCTOR-PATH-001 inserted via the formal-artifact-approval gate.
- `.claude/rules/bridge-essential.md` §"Operational Mode" reconciled to current state with no other text changes.

**Public-surface coverage requirements (per Codex `-002.md` Required Revision):**
- Public doctor coverage for fresh (TP1), warning (TP2), stale/fail (TP3), missing-file warning (TP4), and BOM-tolerant valid JSON (TP5) behavior.
- Both `claude` and `codex` agent mappings visible through the public doctor report (TP7).
- Helper-level schema validation tests (TS1–TS3) only as additional coverage, not as the sole `GOV-19-A1` proof.

## Open Items (unchanged from `-001`)

- Exact existing test file(s) covering bridge-poller behavior at the public surface (probe at implementation start).
- Any non-doctor callers of `_BRIDGE_STATUS_PATHS` legacy paths (probe is one grep).
- Whether `dispatch-state.json` schema_version 1 has a bump in flight (probe at implementation start).

## Deliberation Capture

This proposal (and its `-001`/`-002` predecessors) is the substantive design record for the doctor-path fix. The IPR/CVR pair captures the schema migration. No pre-implementation owner decisions are required.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
