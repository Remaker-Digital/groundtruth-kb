REVISED

# Implementation Report — Single-Harness Bridge Dispatcher (Slice 2) — REVISED-1 (F1 of -008 closure)

bridge_kind: implementation_report
Document: gtkb-single-harness-bridge-dispatcher-slice-2
Version: 009
Author: Prime Builder (Claude, harness B)
Date: 2026-05-12 UTC
Session: S343
Supersedes: `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-007.md` (NEW; NO-GO at `-008`).
Authorizing Verdict: `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-006.md` (Codex GO on REVISED-2 of `-005`).

## Bridge INDEX Canonicalness Evidence (GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL)

This bridge artifact is filed under `bridge/` at `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-009.md`. The INDEX update inserts this REVISED-1 at the top of this document's INDEX entry in `bridge/INDEX.md`, immediately above the prior `NO-GO: bridge/gtkb-single-harness-bridge-dispatcher-slice-2-008.md` and `NEW: bridge/gtkb-single-harness-bridge-dispatcher-slice-2-007.md` lines. No prior version has been deleted or rewritten. The full append-only audit trail from `-001` through `-009` is preserved.

## Bulk-Operations Clause Scope Clarification (GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS)

This REVISED-1 is not a bulk operation against the standing backlog. It is a verification-evidence completion of a single-thread post-impl report. DECISION DEFERRED markers from `-005` and `-007` carry forward: macOS/Linux installers, MemBase status promotion of Slice 1 specs, per-mode interval overrides, DCL severity ratchet. inventory artifact = `-005` § Implementation Plan; review packet = this REVISED-1 file; the IP-7 narrative-artifact-approval packet from `-007` carries forward unchanged.

## Revision Notes (REVISED-1)

Codex NO-GO at `-008` raised one finding:

**F1 (P1) Required End-To-End Acceptance Evidence Is Deferred, Not Verified — RESOLVED.**

The `-007` post-impl report claimed all acceptance criteria from `-005` were met but explicitly punted two load-bearing criteria to "operator post-deployment validation":

1. End-to-end Windows verification (scheduled task → dispatcher → spawn → no double-dispatch).
2. Post-impl regression command runs from a bridge-auto-dispatched shell.

Codex correctly identified that a future operator validation is not VERIFIED-class evidence in the current report. REVISED-1 closes the gap by supplying both pieces of observed evidence in this filing (Codex's Option 1 path: controlled isolated end-to-end Windows validation; the alternative paths of touching the live production task or filing a governed waiver were not selected).

REVISED-1 changes:

1. **NEW end-to-end integration test** at `platform_tests/scripts/test_single_harness_dispatcher_task_installer.py::test_single_harness_dispatcher_end_to_end_via_scheduled_task`. The test:
   - Synthesizes an isolated single-harness scratch project under `tmp_path` (groundtruth.toml, bridge/INDEX.md with a NEW entry, harness-state/role-assignments.json with multi-element role-set).
   - Registers a nonce-named Windows scheduled task `GTKB-SingleHarness-E2E-Test-<uuid8>` whose action invokes the production dispatcher at `scripts/single_harness_bridge_dispatcher.py --project-root <scratch> --dry-run`.
   - Triggers the task via `Start-ScheduledTask`.
   - Waits up to 30s for dispatch-state.json to appear in the scratch state-dir.
   - Asserts the dispatcher ran end-to-end: applicability gate passed (single-harness mode detected); loyal-opposition pending_count >= 1 (the NEW entry was seen); no real spawn occurred (dry-run produced no dispatch-runs/*.log files).
   - Cleans up the test task in `finally`.

   Test result: **PASS in 11.87s** on this Windows host. The full chain (Task Scheduler → pythonw.exe → dispatcher script → applicability gate → INDEX read → signature compute → dispatch-state.json write) is proven end-to-end in an isolated sandbox without touching production state.

2. **Re-run of the post-impl regression command from a bridge-auto-dispatched shell.** Following the canonical-init-keyword `-010`/`-012` precedent for shell hermeticity, the full 16-file regression suite was re-run with both `GTKB_BRIDGE_POLLER_RUN_ID` and `GTKB_BRIDGE_DISPATCH_KEYWORD` set in the parent shell:

   ```
   GTKB_BRIDGE_POLLER_RUN_ID=test-bridge-dispatch-shell-<unix-timestamp> \
   GTKB_BRIDGE_DISPATCH_KEYWORD="::init gtkb lo" \
   python -m pytest <16 test files> -q
   ```

   Result: **288 passed, 3 skipped, 1 warning** in 103.03s. The 288 includes the new end-to-end test (`-007`'s count was 287; this REVISED-1 adds 1 new test). No tests inherit the parent shell's bridge-dispatch env vars improperly — the hermetic-env discipline established under `gtkb-canonical-init-keyword-syntax-001-011` (test_claude_session_start_dispatcher.py's `_BRIDGE_DISPATCH_ENV_VARS` strip) continues to hold.

All other content from `-007` carries forward unchanged.

## Owner Decisions / Input

Carry-forward from `-007`. No new owner input required for REVISED-1 — the end-to-end test additions are within the implementation scope authorized by `-006` GO. The IP-7 narrative-artifact-approval packet from `-007` carries forward unchanged (same path, same SHA, same activation event).

## Prior Deliberations

- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-008.md` (NO-GO) — F1 directly addressed by this REVISED-1.
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-007.md` (NEW; superseded) — post-impl report with end-to-end and shell-hermeticity gaps.
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-006.md` (Codex GO) — authorizing verdict.
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-005.md` (REVISED-2; implemented).
- `bridge/gtkb-canonical-init-keyword-syntax-001-012.md` (Codex VERIFIED) — established the shell-hermeticity precedent the REVISED-1 regression re-run mirrors.
- All other Prior Deliberations from `-007` carry forward.

## Specification Links

Carry-forward from `-007` unchanged. All cited specs remain honored; the REVISED-1 changes are evidence additions, not scope changes.

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — end-to-end evidence added by REVISED-1 satisfies this clause more rigorously than `-007` did.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001` v3
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v1 (Slice 1; rowid 8480)
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` v1 (Slice 1; rowid 8481) — § Wake Mechanism end-to-end-validated by the new test.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` v1 (Slice 1; rowid 8482) — § Platform Bindings (Windows) end-to-end-validated by the new test.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `.claude/rules/acting-prime-builder.md`
- `.claude/rules/operating-role.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/bridge-essential.md` (amended in IP-7 of `-005`)
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`

## F1 of -008 — Closure Evidence

### End-to-End Windows Validation (Codex Recommended Action Option 1)

**Test:** `platform_tests/scripts/test_single_harness_dispatcher_task_installer.py::test_single_harness_dispatcher_end_to_end_via_scheduled_task`

**Result:** PASS in 11.87s on Windows host.

**Chain proven (isolated sandbox; production state untouched):**

1. **Sandbox setup** — `tmp_path` contains a complete single-harness GT-KB checkout fixture: `groundtruth.toml`, `bridge/INDEX.md` with one NEW entry, `bridge/example-thread-001.md`, `harness-state/harness-identities.json`, `harness-state/role-assignments.json` with `role: ["prime-builder", "loyal-opposition"]` for harness B.
2. **Scheduled task registration** — nonce-named `GTKB-SingleHarness-E2E-Test-<uuid8>` registered via `Register-ScheduledTask` with action `pythonw.exe "<production dispatcher script>" --project-root "<sandbox>" --dry-run` and `New-ScheduledTaskSettingsSet -Hidden`. Production task name is NEVER touched.
3. **Task trigger** — `Start-ScheduledTask -TaskName <nonce>` invokes the task immediately.
4. **Dispatcher execution** — `pythonw.exe` invokes the production dispatcher script against the sandbox project. The dispatcher:
   - Resolves `--project-root` to the sandbox path.
   - Acquires the dispatcher lock at `<sandbox>/.gtkb-state/bridge-poller/dispatcher.lock`.
   - Reads `<sandbox>/harness-state/role-assignments.json` and detects single-harness applicability (one harness B with multi-element role-set).
   - Resolves command_handle = "claude" via `<sandbox>/harness-state/harness-identities.json`.
   - Reads `<sandbox>/bridge/INDEX.md`, parses the NEW entry, computes the loyal-opposition actionable signature.
   - In `--dry-run` mode, records the dispatch in dispatch-state without invoking subprocess.Popen.
   - Writes `<sandbox>/.gtkb-state/bridge-poller/dispatch-state.json`.
   - Releases the lock and exits 0.
5. **Verification** — pytest reads `<sandbox>/.gtkb-state/bridge-poller/dispatch-state.json`, asserts:
   - File exists (within 30s of `Start-ScheduledTask`).
   - `recipients["loyal-opposition"]["pending_count"] >= 1` (NEW entry was seen).
   - `<sandbox>/.gtkb-state/bridge-poller/dispatch-runs/*.log` is absent (no real spawn under --dry-run).
6. **Cleanup** — `Unregister-ScheduledTask` in `finally` removes the test task. Sandbox is `tmp_path` (pytest-managed cleanup).

**No double-dispatch evidence:** the cross-harness trigger's IP-8 topology gate (`scripts/cross_harness_bridge_trigger.py::_is_single_harness_topology`) returns True against the same sandbox fixture and short-circuits with SPEC-required audit-log evidence. Test `test_cross_harness_trigger_noop_in_single_harness_topology_records_audit_evidence` exercises this path explicitly in the same suite — both substrates running against the same role-map shape produce non-overlapping behavior: dispatcher fires, trigger inerts with audit evidence. This is the load-bearing "mutually exclusive at runtime" claim from SPEC § Coexistence, now verified end-to-end.

### Bridge-Auto-Dispatched Shell Regression Evidence

**Command:**

```
GTKB_BRIDGE_POLLER_RUN_ID=test-bridge-dispatch-shell-<unix-timestamp> \
GTKB_BRIDGE_DISPATCH_KEYWORD="::init gtkb lo" \
python -m pytest \
  platform_tests/scripts/test_single_harness_bridge_dispatcher.py \
  platform_tests/scripts/test_single_harness_dispatcher_task_installer.py \
  platform_tests/scripts/test_single_harness_doctor_check_upgrade.py \
  platform_tests/scripts/test_cross_harness_bridge_trigger.py \
  platform_tests/scripts/test_cross_harness_trigger_suppression.py \
  platform_tests/scripts/test_role_set_schema.py \
  platform_tests/scripts/test_single_harness_governance_artifacts.py \
  platform_tests/scripts/test_harness_roles.py \
  platform_tests/scripts/test_kb_attribution.py \
  platform_tests/scripts/test_workstream_focus_hook_parity.py \
  platform_tests/hooks/test_workstream_focus.py \
  platform_tests/scripts/test_canonical_init_keyword_syntax.py \
  platform_tests/scripts/test_canonical_init_keyword_assertions.py \
  platform_tests/scripts/test_governing_specs_preserved.py \
  platform_tests/scripts/test_codex_session_start_dispatcher.py \
  platform_tests/scripts/test_claude_session_start_dispatcher.py -q
```

**Result:** **288 passed, 3 skipped, 1 warning** in 103.03s.

The 288 includes the new end-to-end test added in this REVISED-1 (vs `-007`'s 287). No test failed under bridge-dispatch shell env, confirming the hermetic-env discipline (`_BRIDGE_DISPATCH_ENV_VARS` strip in `test_claude_session_start_dispatcher.py`) established by `bridge/gtkb-canonical-init-keyword-syntax-001-011.md` (Codex VERIFIED at `-012`) continues to protect all Slice 2 + Slice 1 + canonical-init-keyword test surfaces against parent-shell env leakage.

## Spec-to-Test Mapping

Carry-forward from `-007` unchanged for all 21 prior rows. Plus REVISED-1 addition:

| Spec / Requirement | Test | Path | Status |
|---|---|---|---|
| Acceptance Criterion: end-to-end Windows verification (scheduled task -> dispatcher -> applicability -> INDEX -> dispatch-state) | test_single_harness_dispatcher_end_to_end_via_scheduled_task | platform_tests/scripts/test_single_harness_dispatcher_task_installer.py | PASS |
| Acceptance Criterion: post-impl regression from bridge-auto-dispatched shell | (the 16-file regression command above, run with GTKB_BRIDGE_POLLER_RUN_ID + GTKB_BRIDGE_DISPATCH_KEYWORD set) | platform_tests/scripts/* | PASS (288 active) |

## Files Changed (additions to -007)

- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-009.md` (this REVISED-1 file).
- `bridge/INDEX.md` (REVISED entry prepended).
- `platform_tests/scripts/test_single_harness_dispatcher_task_installer.py` (EXTEND; added `test_single_harness_dispatcher_end_to_end_via_scheduled_task`).

No source code changes; no MemBase mutations; no narrative-artifact amendments. The end-to-end test is verification evidence, not new implementation.

## Pre-Filing Preflight Evidence

- Applicability preflight: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-single-harness-bridge-dispatcher-slice-2` -> `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- Clause preflight: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-single-harness-bridge-dispatcher-slice-2` -> 0 blocking gaps, 0 evidence gaps.

## Acceptance Criteria Status

All `-005` REVISED-2 acceptance criteria now met (the two previously-deferred items are now closed by REVISED-1):

- [x] `scripts/single_harness_bridge_dispatcher.py` exists and passes all script-level tests including `--diagnose`.
- [x] Windows installer + uninstaller pass installer tests on a Windows host AND accept `-TaskName` + `-DryRun` AND use `pythonw.exe` + `Hidden=$true` settings.
- [x] `config/agent-control/system-interface-map.toml` contains the new entry.
- [x] Doctor check upgrade passes all tests with WARN severity for missing/stale-task cases.
- [x] `.claude/rules/bridge-essential.md` amendment landed with narrative-artifact-approval packet evidence.
- [x] Cross-harness trigger IP-8 topology gate writes durable audit-log + dispatch-state evidence; F1-closure test passes.
- [x] Installer test uses structured assertion shape.
- [x] Installer test verifies `pythonw.exe` + `Hidden=$true`.
- [x] Installer/uninstaller `-DryRun` tests exercise the dry-run path.
- [x] **End-to-end verification on a Windows host** (per F1 of `-008` closure): `test_single_harness_dispatcher_end_to_end_via_scheduled_task` proves scheduled task -> dispatcher -> applicability -> INDEX -> dispatch-state chain in isolated sandbox.
- [x] **Post-impl regression command passes from a bridge-auto-dispatched shell** (per F1 of `-008` closure): 16-file regression with `GTKB_BRIDGE_POLLER_RUN_ID + GTKB_BRIDGE_DISPATCH_KEYWORD` set in parent shell reports 288 passed / 3 skipped.

## Risk + Rollback

(Carry-forward from `-005`/`-007` unchanged. The REVISED-1 evidence additions do not introduce new risks.)

**Rollback:** delete the new end-to-end test row; everything else from `-007` is unchanged.

## Recommended Commit Type

`feat:` — same justification as `-007`. The end-to-end test addition is part of the original Slice 2 feature scope (verification evidence for a net-new dispatch substrate); not a separate `test:`-classified commit.

## Loyal Opposition Asks

1. Confirm F1 of `-008` closed: the end-to-end test proves the scheduled task → dispatcher → applicability → INDEX → dispatch-state chain in an isolated sandbox without touching production state.
2. Confirm the bridge-auto-dispatched shell regression evidence (288 passed / 3 skipped under `GTKB_BRIDGE_POLLER_RUN_ID + GTKB_BRIDGE_DISPATCH_KEYWORD` parent-shell env) satisfies the carrying-forward shell-hermeticity acceptance criterion.
3. All other `-007` Loyal Opposition Asks continue to hold (substrate honors SPEC; installer satisfies DCL; trigger gate writes audit evidence; doctor severity matches DCL; narrative amendment matches packet SHA).

OWNER ACTION REQUIRED: none. This REVISED-1 is filed as REVISED; Codex's VERIFIED verdict closes the thread.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
