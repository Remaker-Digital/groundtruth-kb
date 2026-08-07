NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 7c5bf02a-db61-459e-9321-695a31696526
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: implementation_report
Document: gtkb-wi5951-authorization-scan-prefilter
Version: 003
Date: 2026-08-06 UTC
Responds to: bridge/gtkb-wi5951-authorization-scan-prefilter-002.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5951

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization_scan_prefilter.py"]

**No KB mutation.** This implementation performed no MemBase write and did not modify `groundtruth.db`.
**No approval-evidence work.** This implementation created no formal-artifact-approval packet and wrote no approval-packet path.

# WI-5951 - Implementation Report: target-path filter now precedes packet validation

## Verification Request

Post-implementation report for the `GO` at `bridge/gtkb-wi5951-authorization-scan-prefilter-002.md`
(Loyal Opposition, goose harness G, session `G-2026-08-06T20-01-18Z`). Implemented by an
independent session (`7c5bf02a-db61-459e-9321-695a31696526`, Claude harness B) under
implementation-start packet
`.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5951-authorization-scan-prefilter.json`.

## Root Boundary Compliance

All artifacts are in-root under `E:/GT-KB`. Both changed files are in-root platform paths and this
bridge file resides under `E:/GT-KB/bridge/`. No generated artifact was written outside the project
root. No `applications/` path was touched.

## Specification Links

Carried forward verbatim from `-001`; no link was added, dropped, or reinterpreted.

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority for this thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - discharged by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - discharged by the Spec-to-Test Mapping below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - platform surfaces only; no `applications/` path.
- `.claude/rules/codex-review-gate.md` - the implementation-start authorization gate whose resolution
  path this change makes tractable; its authorization semantics are preserved exactly.
- `.claude/rules/file-bridge-protocol.md` - the VERIFIED commit-finalization gate that was stalling.
- `.claude/rules/bridge-essential.md` - bridge integrity is the first duty.
- `.claude/rules/project-root-boundary.md` - in-root containment.
- `DELIB-202667721` - owner decision behind the whole-project authorization.

## Prior Deliberations

Carried forward from `-001` (WI-5658, WI-5659, WI-5762;
`bridge/gtkb-wi5279-project-authorization-bootstrap-lifecycle-004.md`;
`bridge/gtkb-wi5941-deterministic-release-deadline-test-008.md`;
`bridge/gtkb-wi5939-false-terminal-finalization-recovery-001.md`; `DELIB-202667721`;
`DELIB-202667526`).

Implementation-time search (`gt deliberations search "implementation authorization packet validation
performance scan" --limit 6`) surfaced no prior decision rejecting this approach. The nearest
adjacent record is `DELIB-202667723` (terminal-evidence-sufficient: expired implementation-start
packets remain valid evidence of implementation-time authority) - adjacent, not conflicting: this
change alters neither packet liveness semantics nor what an expired packet evidences. Also surfaced:
`DELIB-202667286` (WI-5554 preflight-evidence binding), `DELIB-202666875`.

## Requirement Sufficiency

Existing requirements sufficient, unchanged from `-001`. No requirement was created or revised.

## Implemented Change

### C1 - Filter before validating (as approved)

`scripts/implementation_authorization.py::_named_packets_authorizing_targets` now reads each named
packet's JSON directly, applies `_unauthorized_targets` to that raw packet, and skips immediately
when the packet does not authorize the candidate targets. `load_named_packet` - and therefore the
full `_validate_packet` -> `_packet_go_integrity` -> `resolve_bridge_lifecycle` ->
`bridge_dir.iterdir()` chain - now runs only for packets that survive the filter.

Post-filter, the surviving packet is still validated and the validated packet is re-checked against
the targets before it joins the match set. No packet can enter the result without full validation.

Corrupt or unreadable JSON is skipped via `except (OSError, json.JSONDecodeError): continue`,
preserving the previous `except AuthorizationError: continue` skip behaviour for the same inputs
(`load_named_packet` converted exactly those two failures into `AuthorizationError`).

Deliberate non-change: survivors are read twice (once raw for the filter, once inside
`load_named_packet`). Reusing the pre-parsed dict would require changing `load_named_packet`'s
contract, widening the blast radius of a governance-critical validator to save a single read on the
handful of packets that survive. The approved scope was a reordering; that is what was implemented.

No `isinstance(raw, dict)` guard was added. A packet file whose JSON parses to a non-dict raised an
unhandled `AttributeError` before this change (inside `_validate_packet`) and still does (now inside
`_unauthorized_targets`). Adding a guard would have been a behaviour change beyond the approved
scope; it is disclosed here rather than taken.

### Files changed

| File | Change | Lines |
| --- | --- | --- |
| `scripts/implementation_authorization.py` | `_named_packets_authorizing_targets` reordering + docstring | +34, -0 |
| `platform_tests/scripts/test_implementation_authorization_scan_prefilter.py` | new test module (T1-T5 + 2 boundary cases) | new file, 7 tests |

## Spec-to-Test Mapping

| Spec / requirement | Test | Result |
| --- | --- | --- |
| Authorization-gate semantics: match set unchanged (`.claude/rules/codex-review-gate.md`) | `test_t1_match_set_identical_to_validate_then_filter` | PASS |
| No relaxation: authorizing-but-invalid packet rejected (`.claude/rules/codex-review-gate.md`) | `test_t2_authorizing_packet_failing_validation_is_never_returned` | PASS |
| No over-rejection: valid authorizing packet returned (`.claude/rules/codex-review-gate.md`) | `test_t3_valid_authorizing_packet_is_returned` | PASS |
| WI-5951 defect: non-authorizing packets skip validation | `test_t4_non_authorizing_packets_skip_full_validation`, `test_t4b_no_validation_at_all_when_nothing_authorizes` | PASS |
| Corrupt-input parity | `test_t5_corrupt_packet_json_is_skipped_without_raising`, `test_t5b_missing_by_bridge_directory_returns_empty` | PASS |
| Bridge finalization path completes (`.claude/rules/file-bridge-protocol.md`, `.claude/rules/bridge-essential.md`) | `platform_tests/scripts/test_implementation_start_gate.py` completes in 110.52s (previously timed out) | REPORTED AS MEASURED - see Acceptance Criteria 5 |

T1 uses `_reference_validate_then_filter`, an in-test reproduction of the pre-change body, as the
equality oracle - so the assertion is genuine set-equality against the old algorithm, not a restated
expectation. T4 asserts on a recorded list of `bridge_id` values submitted to validation, because the
defect is invisible in the return value and observable only in work performed; T4 fails against the
pre-change code (all 27 fixture packets would be validated).

## Commands Executed

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_authorization_scan_prefilter.py -q
  -> 7 passed, 1 warning in 0.31s

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py -q
  -> 163 passed, 1 warning in 30.43s

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_start_gate.py -q
  -> 4 failed, 206 passed, 2 warnings in 110.52s (0:01:50); exit 1

groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization_scan_prefilter.py
  -> All checks passed!  (exit 0)

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization_scan_prefilter.py
  -> 2 files already formatted  (exit 0)
```

Supporting measurement, captured before the change on this session's live tree:

```
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi5951-authorization-scan-prefilter
  -> exit 0, elapsed 94.7s
```

That 94.7s is the pre-change cost of a single packet mint on the live 603-packet / 15k-file tree, and
is offered as independent corroboration of the `-001` cost model rather than as an acceptance
criterion.

## Acceptance Criteria Check

| # | Criterion | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Match set unchanged for equivalent inputs | MET | T1 set-equality against the reference implementation |
| 2 | No packet failing validation is returned, even when it authorizes | MET | T2 (returns empty list, and asserts validation was still attempted) |
| 3 | Valid authorizing packets still returned | MET | T3 |
| 4 | Full validation not performed for non-authorizing packets | MET | T4, T4b |
| 5 | `test_implementation_start_gate.py` completes without timeout; result reported as measured | MET (completes); result reported: **4 failed, 206 passed in 110.52s** | See Residual Failures below |
| 6 | `test_implementation_authorization.py` shows no regression | MET | 163 passed, 0 failed |
| 7 | Both ruff gates pass on changed files | MET | `ruff check` exit 0; `ruff format --check` exit 0 |

## Residual Failures in test_implementation_start_gate.py (criterion 5, reported as measured)

The suite no longer times out. Four tests fail, all with one identical root cause:

```
AttributeError: module 'scripts.bridge_work_intent_registry' has no attribute
'WorkIntentAuthorizationError'. Did you mean: 'WorkIntentWriteContentionError'?
```

- `test_work_intent_acquire_denial_creates_no_claim`
- `test_work_intent_extension_denial_leaves_claim_unchanged`
- `test_work_intent_renew_denial_leaves_go_claim_unchanged`
- `test_work_intent_reclassify_denial_leaves_draft_claim_unchanged`

Evidence that these are pre-existing and independent of this change:

1. The module's actual exception surface is
   `MalformedBridgeStatusError`, `ReservationClaimFenceError`, `WorkIntentDatabaseError`,
   `WorkIntentRegistryError`, `WorkIntentWriteContentionError` - `WorkIntentAuthorizationError`
   does not exist. This is test/source drift in the work-intent registry, not authorization scanning.
2. Neither `scripts/bridge_work_intent_registry.py` nor
   `platform_tests/scripts/test_implementation_start_gate.py` is modified by this session
   (`git status --short` returns empty for both), and neither is in this thread's `target_paths`.
3. The failing symbol is unreachable from `_named_packets_authorizing_targets`.

This is disclosed rather than fixed: repairing it is outside the approved `target_paths` and belongs
in its own governed thread. Recommend Loyal Opposition treat it as a disclosed pre-existing defect
and, if it agrees, that a follow-on work item be filed for the work-intent-registry test drift.

## Disclosures

1. **Peer-thread hook warning.** The `PreToolUse` governance hook flagged
   `bridge/gtkb-wi5178-governed-predecessor-closure` (latest `NO-GO` at `-008`, 2026-07-18) as a
   NO-GO thread touching this module. That NO-GO was read in full before implementing. Its block is
   dependency ordering against then-live peer claims on the WI-5178 24-path envelope - explicitly
   "not rejected on its merits ... not a design defect" - and it contains no finding against the
   change implemented here. The mechanical operation-time gate concurred: the implementation-start
   packet for this thread minted successfully (exit 0), which is the control that would have denied
   a genuine live peer-claim conflict.
2. **Startup-input-gate cross-session block hit mid-implementation.** Tool use was blocked once by
   `BLOCKED (GTKB-STARTUP-INPUT-GATE)` while this session was mid-implementation, with no action by
   this session that should have armed it. Direct read of
   `harness-state/claude/session-lifecycle-guard.json` showed `armed_at: 2026-08-06T20:34:57Z`,
   `armed_source: startup` - a *sibling* Claude session's SessionStart writing the harness-keyed
   (not session-keyed) guard file. This is a second empirical instance of the defect already filed
   as `bridge/gtkb-lifecycle-guard-concurrent-session-collision-001.md` (ADVISORY, 2026-07-18), and
   the first observed in the *blocking* direction with the arming event captured in the state file
   rather than inferred. The block self-cleared on retry, consistent with that advisory. Recorded
   here as corroborating evidence for that open advisory; no remediation attempted or in scope, and
   the guard was not edited or bypassed.
3. **Canonical scanner cost.** `.claude/skills/gtkb-bridge/helpers/scan_bridge.py --role
   prime-builder` calls `create_authorization_packet` for every GO thread as an eager activatability
   check. On the live tree this did not complete within 40+ minutes of CPU. This change reduces the
   per-call cost substantially but does not address the O(GO-threads) sweep itself. Out of scope
   here; flagged for backlog capture per the strategic self-improvement directive.

## Risk and Rollback

- Residual risk that an authorization decision changed: mitigated by T1 (set-equality against the
  old algorithm) and T2/T3 (both rejection directions), plus 163 passing existing authorization
  tests.
- Rollback: revert `scripts/implementation_authorization.py`; the new test file is additive and can
  be deleted independently.

## Owner Decisions / Input

Carried forward from `-001`; no new owner decision was required or taken for this implementation.

- **AUQ 2026-08-06 (quadratic scan defect):** owner selected "Fix it now under a new proposal",
  authorizing this proposal and its implementation after review.
- **AUQ 2026-08-06 (path-lock deadlock):** owner selected "I drive WI-5279 to terminal"; investigating
  that thread surfaced this defect as the operative blocker.
- **`DELIB-202667721`** - owner decision behind the whole-project authorization covering WI-5951.

## Recommended Commit Type

`perf:` - the change alters no behaviour and no authorization outcome; it removes redundant work from
the resolution path. Diff is +34 lines in one function plus one additive test module, consistent with
a performance change rather than `feat:` (no new capability surface) or `fix:` (no previously-broken
behaviour is corrected - the outcome was always right, only the cost was wrong).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
