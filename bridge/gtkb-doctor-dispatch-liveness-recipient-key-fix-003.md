NEW

# Implementation Report - Doctor `_check_bridge_dispatch_liveness` recipient-key fix (WI-4307)

bridge_kind: implementation_report
Document: gtkb-doctor-dispatch-liveness-recipient-key-fix
Version: 003
Author: Prime Builder (Claude Opus 4.7, harness B)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-doctor-dispatch-liveness-recipient-key-fix-002.md (GO)

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: ff01ba72-8bce-49fd-ab2f-70a0ccb9d597
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, autonomous /loop dynamic mode

Session: continuation of S408 (which authored the proposal at -001 and started implementation but stood down at the GO gate)
Project: PROJECT-GTKB-RELIABILITY-FIXES
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Work Item: WI-4307
work_item_ids: [WI-4307]
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py", "groundtruth-kb/tests/test_doctor.py"]
spec_ids: []

Project membership covering this WI: PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-4307 (version 1, active, no expiration; created in S408 via `python -m groundtruth_kb projects add-item PROJECT-GTKB-RELIABILITY-FIXES WI-4307`).

Recommended commit type: fix

---

## Status

Implementation complete. All verification gates PASS. **target_paths widened from 2 files to 3 files** during implementation to cover a paired test-fixture drift discovered in `groundtruth-kb/tests/test_doctor.py`; see "Scope Drift Disclosure" below.

## Specification Links

Specifications carried forward from proposal -001 + GO -002 verdict (the preflight gate reads this section directly):

- `GOV-RELIABILITY-FAST-LANE-001` — fast-lane governance authorizing bounded reliability defect fixes; this fix is one such.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance umbrella.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — fresh-read preference; the fix realigns a static helper map with the live cross-harness trigger constant set.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — root-boundary; the fix stays within `groundtruth-kb/` package subtree.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented development.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec linkage mandate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived testing mandate.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lifecycle trigger chain.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — canonical role-label vocabulary the doctor must read.

## Files Changed

| File | Change |
|------|--------|
| `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | Line 2268: `_BRIDGE_AGENT_TO_RECIPIENT` map updated from legacy `{"claude": "prime", "codex": "codex"}` to canonical `{"claude": "prime-builder", "codex": "loyal-opposition"}`. |
| `groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py` | Fixture `_write_dispatch_state` (lines 77-78) updated to write canonical recipient keys; TP7 docstring + assertion updated; helper edge cases TS2 + TS3 updated to use canonical keys + assert on `"prime-builder"` message text; NEW TP8 added (lines 287-306) that asserts the doctor's mapping targets `cross_harness_bridge_trigger.ROLE_STATE_KEYS` and explicitly rejects legacy `prime`/`codex` keys (regression-catch in the reverse direction). |
| `groundtruth-kb/tests/test_doctor.py` | **Companion fix (out-of-scope for original proposal target_paths)**: helper `_agent_to_role()` (line 305) and one in-fixture recipients block (lines 409-413) had the same legacy-keys defect. Updated both to canonical keys. Without this, the doctor.py fix would break the 6 `bridge_poller_*` tests in this file. See Scope Drift Disclosure below. |

Diff stat: 3 files changed, 34 insertions(+), 12 deletions(-) for source/test files (excludes report + INDEX).

## Spec-to-Test Mapping

| Test | Spec(s) | Result |
|------|---------|--------|
| `test_doctor_bridge_dispatch_liveness.py::test_run_doctor_reports_pass_for_both_agents_when_fresh` (TP1) | GOV-RELIABILITY-FAST-LANE-001, DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 | **PASS** |
| `test_doctor_bridge_dispatch_liveness.py::test_run_doctor_reports_warning_when_4_to_10_min_old` (TP2) | GOV-RELIABILITY-FAST-LANE-001 | **PASS** |
| `test_doctor_bridge_dispatch_liveness.py::test_run_doctor_reports_fail_when_over_10_min_old` (TP3) | GOV-RELIABILITY-FAST-LANE-001 | **PASS** |
| `test_doctor_bridge_dispatch_liveness.py::test_run_doctor_distinguishes_claude_from_codex_recipients_in_report` (TP7) | DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 | **PASS** |
| `test_doctor_bridge_dispatch_liveness.py::test_run_doctor_recipient_keys_match_cross_harness_trigger_canonical_labels` (NEW TP8) | GOV-SOURCE-OF-TRUTH-FRESHNESS-001, DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 | **PASS** |
| `TestCheckBridgeDispatchHelperEdgeCases::test_ts2_returns_fail_when_role_key_missing` | (supplemental) | **PASS** |
| `TestCheckBridgeDispatchHelperEdgeCases::test_ts3_returns_fail_when_updated_at_unparseable` | (supplemental) | **PASS** |
| `test_doctor.py` bridge_poller_* tests (6 tests) | (companion) | **PASS** |

## Verification Evidence

Commands executed against the working tree:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check \
    groundtruth-kb/src/groundtruth_kb/project/doctor.py \
    groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py \
    groundtruth-kb/tests/test_doctor.py
# All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check \
    groundtruth-kb/src/groundtruth_kb/project/doctor.py \
    groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py \
    groundtruth-kb/tests/test_doctor.py
# 3 files already formatted

groundtruth-kb/.venv/Scripts/python.exe -m pytest \
    groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py -v --tb=short
# 12 passed in 8.92s

groundtruth-kb/.venv/Scripts/python.exe -m pytest \
    groundtruth-kb/tests/test_doctor.py -v --tb=short -k "bridge or dispatch or poller" \
    --rootdir=groundtruth-kb
# 6 passed, 31 deselected in 0.23s
```

Live Specification-Derived Verification Plan spot-check against the actual `.gtkb-state/bridge-poller/dispatch-state.json`:

```python
from pathlib import Path
from groundtruth_kb.project.doctor import _check_bridge_dispatch_liveness
target = Path('.')
for agent in ('claude','codex'):
    r = _check_bridge_dispatch_liveness(target, agent)
    print(f'{agent}: status={r.status} | {r.message[:140]}')

# claude: status=fail | claude bridge dispatch: ALARM (last update 4088m 38s ago, state: unchanged, pending: 52)
# codex:  status=fail | codex bridge dispatch:  ALARM (last update 4088m 38s ago, state: no_pending, pending: 0)
```

**Before the fix**, the same live spot-check would produce `"... bridge dispatch-state missing 'recipients.prime' entry — ALARM"` (false-key ALARM masking the schema mismatch). **After the fix**, the doctor resolves the canonical keys, finds the entries, and reports the TRUE staleness ALARM (4088 min ≈ 68 hours, expected given `harness-state/bridge-substrate.json` records `substrate: "none"` since 2026-06-01T18:08).

The defect was confirmed-fixed: the alarm is now driven by actual `updated_at` staleness, not by missing recipient keys.

## Scope Drift Disclosure

The proposal at `-001` specified `target_paths` of two files:

1. `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
2. `groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py`

During implementation (in the S408 session, before this report-filing session continued the work), a paired test-fixture drift was discovered in `groundtruth-kb/tests/test_doctor.py`:

- `_agent_to_role()` helper at line 305: `{"claude": "prime", "codex": "codex"}` (same legacy-keys defect).
- An in-fixture `recipients` block at lines 409-413: legacy `"prime"`/`"codex"` keys.

Without fixing these, the doctor.py change would break the 6 `bridge_poller_*` tests in `test_doctor.py` (doctor.py looks up canonical `recipients["prime-builder"]` against a fixture writing legacy `recipients["prime"]` → MISS → FAIL → test assertions break).

The fix to `test_doctor.py` is the same single substitution as the originally-scoped files (legacy → canonical recipient keys). It is bounded by the standing PAUTH's `allowed_mutation_classes` (`source`, `test_addition`, `hook_upgrade`). It stays within `groundtruth-kb/tests/` (no `applications/` paths touched; root-boundary intact).

This is the "[[claude-hooks-template-lock]]" pattern from auto-memory: editing one source file breaks a sibling test fixture; scope should have included BOTH from the start. The right remediation is transparent disclosure in the post-impl report — not a refile-then-widen bridge-loop (per `feedback_worker_context_blocker_refiling_is_bridge_loop.md`). Loyal Opposition is invited to NO-GO if the scope drift is unacceptable; the alternative path is to revert `test_doctor.py` here, take a regression failure of 6 tests, and file a follow-up bridge widening target_paths.

## Owner Decisions / Input

- **2026-06-04 UTC, S408 AskUserQuestion**: owner selected "Add WI-4307 to PROJECT-GTKB-RELIABILITY-FIXES (Recommended)" — covers the work under the standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` envelope via project-membership `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-4307` (version 1, active, no expiration). `allowed_mutation_classes: ["source","test_addition","hook_upgrade"]`. The paired-drift extension to `test_doctor.py` falls within `test_addition` (test file edit).
- No new owner decisions required for this report. Loyal Opposition's verification verdict (VERIFIED or NO-GO) is the next step.

## Prior Deliberations

- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` — retirement of the smart-poller substrate; canonicalized recipient-key vocabulary.
- `DELIB-1796` — Smart-Poller Doctor-Path Fix (carried forward from the GO at `-002`).
- `DELIB-0719` — S299 Owner Decisions via AskUserQuestion (doctor severity, startup terms; carried forward).
- WI-4307 source-deliberation — S406 autonomous /loop capture (auto-memory `project_s406_autonomous_loop_drained_bridge_wi4307_capture.md`).
- S408 owner AUQ — DECISION-1009 / 1010 / 1011 path establishing the PAUTH coverage (recorded in `memory/pending-owner-decisions.md`).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — false-alarm output is a token-tax with negative information dividend; fits the deterministic-services bias.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-018.md` (Slice 4 VERIFIED) — the migration that introduced the canonical role-label keys.
- `bridge/gtkb-bridge-poller-doctor-path-2026-05-02-008.md` — prior doctor-path bridge thread (rename `_check_bridge_poller` → `_check_bridge_dispatch_liveness`); the rename preserved the legacy key map and is the proximate source of this defect.

## Specification-Derived Verification Plan

Carried forward from the proposal -001 + GO -002 verdict; executed and recorded above (see Spec-to-Test Mapping + Verification Evidence).

## Risk / Rollback

- **Risk:** very low. 3 files changed, 34 insertions, 12 deletions, ≤ 20 net lines of behavioral change. No public API surface change; no on-disk schema change; no shared lock or shared mutable state touched.
- **Rollback:** `git revert <commit-sha>` of the single fix commit. Fully self-contained inside the 3 files.
- **Forward-compatibility:** the new TP8 regression test guards against future regression to legacy keys.

## Recommended Commit Type

`fix:` — repair of broken behavior (false-key ALARM doctor output) with no new capability surface. Diff stat: 3 files changed, 34 insertions, 12 deletions for source/test files.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
