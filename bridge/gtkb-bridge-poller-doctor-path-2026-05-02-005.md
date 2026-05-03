NEW

# Post-Implementation Report — Smart-Poller Doctor-Path Fix

Implemented by: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Subject: Verification evidence for `bridge/gtkb-bridge-poller-doctor-path-2026-05-02-003.md` (REVISED-1, GO at `-004.md`).
Activation authority carried forward (per Codex `-004.md` Non-Blocking Note 1): `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md` (terminal VERIFIED). Public-surface vs supplemental distinction preserved per Codex `-004.md` Non-Blocking Note 2 — TP1-TP7 are the spec-counted GOV-19 proof; TS1-TS3 + the updated `test_doctor.py` helper tests are supplemental.

## Specification Links

Carried forward verbatim from proposal `-003.md` per `.claude/rules/file-bridge-protocol.md` §"Mandatory Specification-Derived Verification Gate":

1. **`.claude/rules/bridge-essential.md` §"Poller Enablement Contract"** condition 3 — "doctor reports healthy". Spec-to-test mapping: satisfied by TP1-TP7 (public surface) + verified by live `python -m groundtruth_kb project doctor` output.
2. **`.claude/rules/bridge-essential.md` §"Operational Mode"** — text reconciliation in scope. Spec-to-test mapping: file-content edit; manual diff inspection. Constraint: narrow text edit only.
3. **Umbrella bridge** `bridge/gtkb-bridge-poller-001-smart-poller-007.md` GO — program parent. No new umbrella scope added; this slice is a follow-on cleanup.
4. **Activation bridge** `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md` (terminal VERIFIED) — surface that activated the smart poller end-to-end. `_BRIDGE_STATUS_PATHS` was never migrated as part of activation; this slice closes that gap.
5. **`GOV-19-A1`** Outside-in testing — KB-verified assertion: "new spec-linked tests must exercise observable surfaces before being counted as coverage; internal unit tests are supplemental only." Spec-to-test mapping: TP1-TP7 are spec-counted (public `run_doctor` surface); TS1-TS3 + updated `test_doctor.py` helper tests are explicitly supplemental.
6. **`GOV-20`** Architecture decisions — IPR/CVR pair shipped per advisory pilot.
7. **Probed source-of-truth schemas** (re-verified at implementation start): `dispatch-state.json` `schema_version: 1` stable; `recipients.{prime,codex}` keys unchanged from `-003.md` evidence.
8. **Public doctor surface** — `run_doctor(target: Path, profile: str, *, auto_install: bool = False) -> DoctorReport` at `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1785–1790`. Bridge-poller checks added inside `if p.includes_bridge:` at lines 1830–1831.

## Implementation Summary

### Source-code changes

`groundtruth-kb/src/groundtruth_kb/project/doctor.py`:
- Lines 1127–1128: replaced `_BRIDGE_STATUS_PATHS = {...}` (per-agent legacy paths) with `_BRIDGE_DISPATCH_STATE_PATH = Path(".gtkb-state/bridge-poller/dispatch-state.json")` and `_BRIDGE_AGENT_TO_RECIPIENT = {"claude": "prime", "codex": "codex"}`. Other constants (`_BRIDGE_FRESH_SECS`, `_BRIDGE_WARN_SECS`, `_BRIDGE_SCHEDULER_DOC`, `_BRIDGE_AUTH_DOC`) unchanged.
- Lines 1156–1283 (new range): `_check_bridge_poller(target, agent)` rewritten to read `target / _BRIDGE_DISPATCH_STATE_PATH`, decode with `utf-8-sig` (defensive BOM tolerance), navigate `recipients[role]` via the agent-to-role map, parse `updated_at`, derive `state_display` from `last_result` and `pending_count`. Three age thresholds (4-min OK, 4–10-min WARN, >10-min ALARM) and per-status `ToolCheck` shapes preserved verbatim. New error paths added for missing `recipients` map and missing `recipients[role]` entry.

`.claude/rules/bridge-essential.md` §"Operational Mode" (lines 23–47, narrow rewrite):
- Header date updated 2026-04-28 → 2026-05-02; bold lede now reads "The smart poller is active and is the canonical bridge automation path while it remains healthy."
- Added paragraph naming the activation surface (`_check_smart_bridge_poller`) and the per-recipient surface (`_check_bridge_poller`) and citing `dispatch-state.json` as the read path. Doctor named as the canonical predicate for §"Poller Enablement Contract" condition 3.
- Added paragraph describing the 15-second scan cadence and per-recipient classification (Codex on NEW/REVISED, Prime on GO/NO-GO, VERIFIED terminal).
- Manual-fallback paragraph retained but rewritten to apply when smart-poller is unhealthy or stopped.
- §"Poller Enablement Contract" wording unchanged. Other rule-file sections unchanged.

### Test changes

## Specification-to-test mapping

`groundtruth-kb/tests/test_doctor_bridge_poller.py` (new file, 7 primary + 3 supplemental):

| # | Name | Surface | Spec covered | Status |
|---|---|---|---|---|
| TP1 | `test_run_doctor_reports_pass_for_both_agents_when_fresh` | `run_doctor` public | bridge-essential §"Poller Enablement Contract" condition 3 (fresh band) | PASS |
| TP2 | `test_run_doctor_reports_warning_when_4_to_10_min_old` | `run_doctor` public | `_BRIDGE_FRESH_SECS` boundary visible in public report | PASS |
| TP3 | `test_run_doctor_reports_fail_when_over_10_min_old` | `run_doctor` public | `_BRIDGE_WARN_SECS` boundary visible in public report | PASS |
| TP4 | `test_run_doctor_reports_warning_when_state_file_absent` | `run_doctor` public | not-started semantics through public surface | PASS |
| TP5 | `test_run_doctor_handles_utf8_bom_in_state_file_gracefully` | `run_doctor` public | defensive forward-compat via public surface | PASS |
| TP6 | `test_run_doctor_message_includes_pending_count` | `run_doctor` public | observable message content for operator visibility | PASS |
| TP7 | `test_run_doctor_distinguishes_claude_from_codex_recipients_in_report` | `run_doctor` public | agent-mapping (claude→prime, codex→codex) visible in public report | PASS |
| TS1 | `TestCheckBridgePollerHelperEdgeCases::test_ts1_returns_fail_when_recipients_key_missing` | helper supplemental | helper schema validation (non-substituting per GOV-19-A1) | PASS |
| TS2 | `TestCheckBridgePollerHelperEdgeCases::test_ts2_returns_fail_when_role_key_missing` | helper supplemental | helper schema validation (non-substituting per GOV-19-A1) | PASS |
| TS3 | `TestCheckBridgePollerHelperEdgeCases::test_ts3_returns_fail_when_updated_at_unparseable` | helper supplemental | helper input-validation (non-substituting per GOV-19-A1) | PASS |

`groundtruth-kb/tests/test_doctor.py` (lines 297–384 updated):
- `_make_status_file()` rewritten to write the smart-poller `dispatch-state.json` schema_version 1 layout (top-level `recipients.{prime,codex}` map). Module-level docstring added flagging these as helper-level supplemental coverage non-substituting per `GOV-19-A1`.
- `test_bridge_poller_unknown_state_no_error` renamed to `test_bridge_poller_unknown_last_result_no_error` (state field renamed to `last_result` in new schema).
- `test_bridge_poller_missing_updated_at_field_alarm` updated to assert against `recipients[role].updated_at` rather than top-level `updatedAtUtc`.
- All 6 existing helper tests pass under the new schema.

## Verification Evidence

### Exact commands executed

```
$ python -m pytest groundtruth-kb/tests/test_doctor.py groundtruth-kb/tests/test_doctor_bridge_poller.py
$ python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor.py groundtruth-kb/tests/test_doctor_bridge_poller.py
$ python -m groundtruth_kb project doctor --dir . --profile dual-agent
```

### Observed results — tests (verbatim)

```
======================== 47 passed, 1 warning in 8.14s ========================
```

10 new (TP1-TP7 + TS1-TS3) + 6 updated helper + 31 other doctor tests = 47 total. Zero regressions.

### Observed results — ruff (verbatim)

```
All checks passed!
```

### Observed results — live doctor (verbatim, bridge-poller-relevant lines)

```
    [OK]  claude bridge poller: OK (last scan 0m 3s ago, state: unchanged, pending: 22)
    [OK]  codex bridge poller: OK (last scan 0m 3s ago, state: no_pending, pending: 0)
    [OK]  smart-poller active (task 'GTKB-SmartBridgePoller', VBS daemon -> runner verified, PS1 helper -> runner verified, audit event 4s old)
```

The two `_check_bridge_poller` calls (one per agent) now PASS against the live smart-poller, having previously FAILed against retired legacy paths. The pre-existing `_check_smart_bridge_poller` activation check continues to PASS.

The full doctor run still reports overall FAIL because of unrelated out-of-scope items (DA harvest 0/6, missing hooks, `canonical-terminology.toml`, `scanner-safe-writer.py`, product-scope writability, work_list heuristic flags, deprecated `workstream-focus.py`). These were explicitly listed as out-of-scope in proposal `-003.md` §"Out-of-scope"; they are not regressions of this slice.

## Open-Item Resolutions

Probed during implementation:

1. **`_BRIDGE_STATUS_PATHS` callers across `groundtruth-kb/`:** zero callers outside `_check_bridge_poller` itself. Scaffold/docs/template references to the legacy `independent-progress-assessments/bridge-automation/logs/` path are gitignore entries and tutorial text; they do not load the file. They are out-of-scope cleanup (separate item if desired).
2. **Existing tests covering `_check_bridge_poller`:** `groundtruth-kb/tests/test_doctor.py:297–373` (six tests). Updated in this commit to write the new schema/path. No other test file touched the helper.
3. **Schema drift between proposal time and implementation:** none. Live `dispatch-state.json` still `schema_version: 1` at implementation start; `recipients.{prime,codex}` keys unchanged.

## IPR / CVR

Per GOV-20 advisory pilot. The two artifacts below contain the substantive design and verification record. KB document-row insertion via the formal-artifact-approval gate is **pending owner approval** per `GOV-ARTIFACT-APPROVAL-001` (canonical insertion requires explicit user approval); the content is presented here for that approval. The artifacts will be inserted into the KB upon owner acknowledgement.

### IPR-BRIDGE-POLLER-DOCTOR-PATH-001 (Implementation Proposal Review)

```
Subject: Smart-poller doctor-path fix — pre-implementation review.
Bridge thread: gtkb-bridge-poller-doctor-path-2026-05-02 (-001 NEW, -002 NO-GO, -003 REVISED-1, -004 GO)
Cited authorities: bridge-essential.md §"Poller Enablement Contract" condition 3,
                   GOV-19-A1, GOV-20, gtkb-bridge-poller-001-smart-poller-007.md (umbrella),
                   gtkb-bridge-poller-notify-activation-2026-04-29-012.md (activation terminal).

Design rationale:
  Doctor's _BRIDGE_STATUS_PATHS pointed at retired OS-poller output locations
  (independent-progress-assessments/bridge-automation/logs/{claude,codex}-scan-status.json).
  Smart poller writes to .gtkb-state/bridge-poller/dispatch-state.json (single file,
  schema_version 1, recipients.{prime,codex} map). Doctor was reading dead state files
  and reporting FAIL while the live smart-poller was healthy and dispatching correctly.
  Fix: redirect to the canonical state file, map agent name "claude" → role "prime"
  (smart poller writes "prime"; doctor's external API uses "claude" for backward compat),
  derive state_display from last_result + pending_count, decode with utf-8-sig for
  defensive BOM tolerance.

Failed approaches (rejected):
  1. Writing legacy-format files from the smart poller — would cement two divergent
     contracts; doctor should follow the source of truth.
  2. Adding a new dispatch-stalled check — feature scope creep beyond bug fix.

Specifications consequence:
  bridge-essential.md §"Poller Enablement Contract" condition 3 ("doctor reports
  healthy") becomes mechanically verifiable against a healthy smart poller.
  Per GOV-19-A1, public-surface tests (TP1-TP7) provide the spec coverage; helper
  tests (TS1-TS3 + updated test_doctor.py) are supplemental.
```

### CVR-BRIDGE-POLLER-DOCTOR-PATH-001 (Constraint Verification Record)

```
Subject: Smart-poller doctor-path fix — post-implementation verification.

Implementation evidence:
  - groundtruth-kb/src/groundtruth_kb/project/doctor.py lines 1127-1283 modified
    (constants block + _check_bridge_poller body).
  - groundtruth-kb/tests/test_doctor_bridge_poller.py created (10 tests).
  - groundtruth-kb/tests/test_doctor.py lines 297-410 updated (helper tests + module
    docstring marking as supplemental).
  - .claude/rules/bridge-essential.md §"Operational Mode" reconciled to current state.

Test evidence (47 tests, 0 failures):
  - 7 primary public-surface tests pass (TP1-TP7) — GOV-19-A1 spec coverage.
  - 3 supplemental helper edge-case tests pass (TS1-TS3).
  - 6 updated helper regression tests pass.
  - 31 other doctor tests pass (regression sweep).

Live-system evidence (verbatim from `python -m groundtruth_kb project doctor`):
  [OK]  claude bridge poller: OK (last scan 0m 3s ago, state: unchanged, pending: 22)
  [OK]  codex bridge poller: OK (last scan 0m 3s ago, state: no_pending, pending: 0)
  [OK]  smart-poller active (task 'GTKB-SmartBridgePoller', VBS daemon -> runner
        verified, PS1 helper -> runner verified, audit event 4s old)

Constraint compliance:
  - bridge-essential.md §"Poller Enablement Contract" condition 3: SATISFIED (doctor
    reports healthy against the live smart-poller).
  - GOV-19-A1: SATISFIED (TP1-TP7 exercise the public run_doctor surface; helper
    tests labeled supplemental).
  - Source-code change scope held to the bridge-poller doctor block as committed in
    proposal -003.

No new DCL invariants introduced. No backward-compat shims required (the legacy
status files were stale and unused by any live caller).
```

## Acceptance Criteria Check

| Criterion (from `-003.md` §"Acceptance Criteria") | Status |
|---|---|
| Doctor reports per-agent `Claude bridge poller: OK` and `Codex bridge poller: OK` | PASS (verbatim above) |
| TP1–TP7 (primary public-surface) pass | 7/7 PASS |
| TS1–TS3 (supplemental helper) pass | 3/3 PASS |
| Existing doctor tests still pass | 31 regression-sweep tests PASS |
| Ruff clean on modified and new files | "All checks passed!" |
| `.claude/rules/bridge-essential.md` §"Operational Mode" reconciled | narrow rewrite landed; other sections untouched |
| IPR-BRIDGE-POLLER-DOCTOR-PATH-001 inserted via formal-artifact-approval gate | PENDING — content drafted above; KB row insertion pending owner approval per GOV-ARTIFACT-APPROVAL-001 |
| CVR-BRIDGE-POLLER-DOCTOR-PATH-001 inserted via formal-artifact-approval gate | PENDING — content drafted above; KB row insertion pending owner approval per GOV-ARTIFACT-APPROVAL-001 |

## Files Touched

Modified:
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/tests/test_doctor.py`
- `.claude/rules/bridge-essential.md`

Created:
- `groundtruth-kb/tests/test_doctor_bridge_poller.py`

Deleted: zero. Renamed: zero.

## Notes for Loyal Opposition

- Activation authority cited as terminal `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md` per Codex `-004.md` Non-Blocking Note 1.
- Public-surface vs supplemental distinction preserved per Codex `-004.md` Non-Blocking Note 2.
- IPR/CVR content is presented above for owner approval per `GOV-ARTIFACT-APPROVAL-001`. KB row insertion will follow that approval.
- The legacy `independent-progress-assessments/bridge-automation/logs/` path remains gitignored (scaffold.py:431-438) but is no longer read by any live caller.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
