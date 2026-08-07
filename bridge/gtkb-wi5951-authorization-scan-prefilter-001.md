NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 5ce32d92-003b-4a04-a5f9-d3de2493c992
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal
Document: gtkb-wi5951-authorization-scan-prefilter
Version: 001
Date: 2026-08-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5951

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization_scan_prefilter.py"]

**No KB mutation.** This proposal performs no MemBase write and does not modify `groundtruth.db`.
**No approval-evidence work.** This proposal creates no formal-artifact-approval packet and writes no approval-packet path.

# WI-5951 - Apply the target-path filter before packet validation in authorization scanning

## Root Boundary Compliance

All artifacts are in-root under `E:/GT-KB`. Both declared targets are in-root paths and this bridge file resides under `E:/GT-KB/bridge/`. No generated artifact is written outside the project root.

## Problem Statement

`scripts/implementation_authorization.py::_named_packets_authorizing_targets` (line 3123) validates every named packet before checking whether the packet is even relevant:

```
for path in sorted(by_bridge_dir.glob("*.json")):
    bridge_id = path.stem
    try:
        packet = load_named_packet(project_root, bridge_id)      # full integrity validation
    except AuthorizationError:
        continue
    if not _unauthorized_targets(packet, normalized_targets):    # cheap path comparison
        matches.append(packet)
```

`load_named_packet` runs `_validate_packet`, which reaches `_packet_go_integrity` -> `bridge_entry` -> `bridge_lifecycle_resolver.resolve_bridge_lifecycle`. That resolver calls `_exact_version_paths`, which performs `bridge_dir.iterdir()` across the entire bridge directory and `path.resolve(strict=True)` per entry.

`_unauthorized_targets` delegates to `path_authorized(packet, target)` and is a **pure function of the packet dict**. It requires no validation, and it discards nearly every packet. Running it after the expensive step, rather than before, is the whole defect.

### Measured cost (2026-08-06)

| Quantity | Value |
| --- | --- |
| named packets under `by-bridge/` | 603 |
| files in `bridge/` | 15,043 |
| approximate filesystem operations per invocation | ~9,000,000 |

Both multiplicands grow monotonically - packets accumulate per bridge thread, files accumulate per bridge version - so the cost increases with every governed cycle.

### Observed symptoms, all tracing to this defect

1. `platform_tests/scripts/test_implementation_start_gate.py` **times out** rather than completing. Its NO-GO at `bridge/gtkb-wi5279-project-authorization-bootstrap-lifecycle-004.md` diagnosed 41 failures from stale `Version:` fixtures; that diagnosis is no longer the operative failure. Captured stack: `_named_packets_authorizing_targets` -> `load_named_packet` -> `_validate_packet` -> `_packet_go_integrity` -> `bridge_entry` -> `resolve_bridge_lifecycle` -> `_exact_version_paths` -> `bridge_dir.iterdir()`.
2. The WI-5939 VERIFIED finalization ran roughly twelve minutes before failing at the protected-commit gate.
3. The WI-5941 finalization stalled twice, each time leaving an uncommitted VERIFIED file that the reviewing session had to discard to avoid a false-terminal chain.
4. The WI-5939 protected-commit failure output printed a 603-line sequence of `pre-filtered: authorizes none of the N candidate path(s)` messages - that is this loop, printing one line per irrelevant packet.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority for this thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - discharged by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Test Plan maps each preserved clause to a test.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - platform surfaces only; no `applications/` path.
- `.claude/rules/codex-review-gate.md` - the implementation-start authorization gate whose resolution path this change makes tractable; its authorization semantics are preserved exactly.
- `.claude/rules/file-bridge-protocol.md` - the VERIFIED commit-finalization gate that currently stalls.
- `.claude/rules/bridge-essential.md` - bridge integrity is the first duty; a finalization path that cannot complete is a bridge-integrity defect.
- `.claude/rules/project-root-boundary.md` - in-root containment.
- `DELIB-202667721` - owner decision behind the whole-project authorization.

## Prior Deliberations

- `WI-5658` (protected-commit checker performance), `WI-5659` (checker verified-evidence prefilter), and `WI-5762` (PAUTH accumulation doctor) - open work in this territory, indicating the cost is known but unresolved at current scale. This proposal addresses the specific ordering defect rather than superseding them.
- `bridge/gtkb-wi5279-project-authorization-bootstrap-lifecycle-004.md` - the NO-GO whose stated fixture diagnosis this evidence supersedes.
- `bridge/gtkb-wi5941-deterministic-release-deadline-test-008.md` - records the two finalization stalls.
- `bridge/gtkb-wi5939-false-terminal-finalization-recovery-001.md` - the false-terminal recovery caused by the same stall class.
- `DELIB-202667526` - publication as a serialized contended resource.

## Requirement Sufficiency

Existing requirements sufficient. The authorization semantics this change preserves are already specified by the implementation-start gate and the bridge protocol; nothing about which packets authorize which paths changes. No new requirement is implied.

## Proposed Change

Single behavioural change, confined to `_named_packets_authorizing_targets`.

### C1 - Filter before validating

Read each packet file's JSON directly (the same cheap read `load_named_packet` performs first), apply `_unauthorized_targets` to that raw packet, and skip immediately when the packet does not authorize the candidate targets. Call `load_named_packet` - and therefore the full integrity validation - only for packets that survive the filter.

Corrupt or unreadable JSON is skipped exactly as today, preserving the existing `AuthorizationError` continue semantics.

### Why this is safe

The filter is a pure function of packet content, and a packet failing it was discarded by the current code anyway - its validation result never influenced the outcome. Every packet that survives the filter still receives full `load_named_packet` validation before being returned, so no unvalidated packet can ever authorize a mutation. The returned set is identical; only the work done to compute it changes.

This is a reordering, not a relaxation. No validation is removed, no expiry or drift check is skipped, and no authorization decision changes.

## Test Plan (specification-derived)

New tests in `platform_tests/scripts/test_implementation_authorization_scan_prefilter.py`:

| Test | Derived from | Asserts |
| --- | --- | --- |
| T1 | authorization-gate semantics | for a fixture set of packets, the returned match set is identical before and after the change |
| T2 | authorization-gate semantics (no relaxation) | a packet that authorizes the targets but fails validation (expired or drifted) is still rejected and never returned |
| T3 | authorization-gate semantics (no over-rejection) | a valid packet authorizing the targets is still returned |
| T4 | WI-5951 defect | full validation is not invoked for packets that do not authorize the candidate targets, asserted by counting validation calls |
| T5 | corrupt-input parity | a corrupt-JSON packet is skipped without raising, as today |

Commands to be executed and reported:

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_authorization_scan_prefilter.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_start_gate.py -q
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization_scan_prefilter.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization_scan_prefilter.py
```

`test_implementation_start_gate.py` currently times out; its completion is the primary end-to-end evidence and its result will be reported as measured, including the elapsed time, whatever the outcome.

## Acceptance Criteria

1. The match set returned by `_named_packets_authorizing_targets` is unchanged for equivalent inputs (T1).
2. No packet that fails validation is returned, even when it authorizes the targets (T2).
3. Valid authorizing packets are still returned (T3).
4. Full validation is not performed for non-authorizing packets (T4).
5. `test_implementation_start_gate.py` completes without timeout, and its pass/fail result is reported as measured.
6. `test_implementation_authorization.py` shows no regression.
7. Both ruff gates pass on the changed files.

## Risk and Rollback

- **Risk: an authorization decision changes.** This is the material risk for a governance-critical gate. Mitigated by T1-T3, which assert set-equality and both rejection directions, and by the reordering argument above: rejected packets never contributed to the result.
- **Risk: the surviving timeout has an additional cause.** Criterion 5 deliberately reports the measured result rather than asserting a pass, so a remaining defect is disclosed rather than masked.
- **Risk: raw-JSON reads diverge from `load_named_packet`'s parse.** Mitigated by using the same read-and-parse step, and by T5 preserving corrupt-input behaviour.
- **Rollback:** revert `scripts/implementation_authorization.py`; the new test file is additive.

## Owner Decisions / Input

- **AUQ 2026-08-06 (quadratic scan defect):** owner selected "Fix it now under a new proposal", authorizing this proposal and its implementation after review.
- **AUQ 2026-08-06 (path-lock deadlock):** owner selected "I drive WI-5279 to terminal"; investigating that thread surfaced this defect as the operative blocker.
- **`DELIB-202667721`** - owner decision behind the whole-project authorization covering WI-5951.

## Recommended Commit Type

`perf:` - the change alters no behaviour or authorization outcome; it removes redundant work from the resolution path.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
