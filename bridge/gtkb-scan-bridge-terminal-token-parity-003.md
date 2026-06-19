REVISED

# Revise Scan Bridge Terminal Token Parity Scope

bridge_kind: prime_proposal
Document: gtkb-scan-bridge-terminal-token-parity
Version: 003
Author: Codex Prime Builder automation
Date: 2026-06-19 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: keep-working-pb-20260619-scan-bridge-terminal-token-parity-revised
author_model: gpt-5-codex
author_model_version: GPT-5 family
author_model_configuration: Codex desktop automation session; Prime Builder; automation_id=keep-working

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4675

target_paths: [".claude/skills/bridge/helpers/scan_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py", "platform_tests/scripts/test_scan_bridge.py"]

implementation_scope: source_and_tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Claim

This revision responds to `bridge/gtkb-scan-bridge-terminal-token-parity-002.md`.
The `NO-GO` was correct: the initial proposal listed only the live Codex bridge
scan helper and its focused test. That left the managed template source outside
the implementation envelope, allowing the live helper to be fixed while scaffold
or upgrade output remained stale.

This revision adds `groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py`
to `target_paths` and makes active/template parity an acceptance condition.

## Summary

WI-4675 captures a deterministic drift between the canonical bridge notify
terminal-kind token set and the bridge scan helper token set. A focused rerun of
`platform_tests/scripts/test_scan_bridge.py` failed because
`groundtruth_kb.bridge.notify._KIND_TERMINAL_TOKENS` includes
`implementation_report`, `post_implementation`, and `post_impl`, while the
bridge scan helper's `_KIND_TERMINAL_TOKENS` omits them.

The implementation should update both the live helper and the managed template
helper so latest `GO` entries for post-implementation/report bridge kinds are
suppressed consistently from Prime Builder actionable scans. The canonical
source remains `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`; this
proposal does not authorize changing the canonical notify token set.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the bridge queue scan determines role-actionable bridge work and must not route terminal report/verdict states as PB implementation work.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation must carry executable tests proving canonical notify/scan parity.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal cites all governing surfaces and concrete target paths, including the managed template source identified by LO.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision remains linked to `WI-4675`, `PROJECT-GTKB-MAY29-HYGIENE`, and the active project authorization.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active May29 Hygiene authorization permits proposing implementation for this unimplemented hygiene work item.
- `GOV-STANDING-BACKLOG-001` - WI-4675 is a captured hygiene backlog defect and remains open until acceptance-clean.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - managed Codex skill/template surfaces must not drift when the live helper behavior changes.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are inside `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the drift is preserved as durable bridge/backlog work instead of an untracked local patch.

## Owner Decisions / Input

No new owner decision is required. `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`
authorizes Prime Builder to propose implementation for all unimplemented work
items linked to `PROJECT-GTKB-MAY29-HYGIENE`. This revision stays within that
authorization and preserves the LO review gate before implementation.

## Prior Deliberations

- `bridge/gtkb-scan-bridge-terminal-token-parity-001.md` - initial Prime Builder proposal for WI-4675.
- `bridge/gtkb-scan-bridge-terminal-token-parity-002.md` - LO `NO-GO` requiring managed template helper coverage.
- `bridge/gtkb-suppress-non-activatable-go-from-pb-scan-003.md` and `bridge/gtkb-suppress-non-activatable-go-from-pb-scan-004.md` - implementation-report/malformed-verdict evidence that exposed the missing terminal-kind token parity.
- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` - active owner authorization for May29 Hygiene implementation proposals.

## Requirement Sufficiency

Existing requirements are sufficient.

WI-4675 states the concrete parity defect; the LO `NO-GO` identifies the missing
managed-template target path; existing bridge-authority, project-linkage,
verification, and parity requirements are sufficient to implement the narrow
helper/test repair.

## Proposed Scope

1. Add `implementation_report`, `post_implementation`, and `post_impl` to the
   live bridge scan helper terminal-kind token set.
2. Apply the same token update to the managed template helper.
3. Extend focused test coverage so canonical notify tokens, live scan-helper
   tokens, and managed-template scan-helper tokens remain aligned.
4. Keep `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` out of scope unless
   implementation evidence proves the canonical token set itself is wrong.

## Files Expected To Change

- `.claude/skills/bridge/helpers/scan_bridge.py`
- `groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py`
- `platform_tests/scripts/test_scan_bridge.py`

## Out Of Scope

- No change to `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`.
- No MemBase mutation.
- No rewrite or deletion of historical malformed bridge verdict/report files.
- No broader bridge scanner routing change beyond terminal-kind token parity.

## Specification-Derived Verification Plan

| Specification / rule | Proposed verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `platform_tests/scripts/test_scan_bridge.py` verifies report/post-implementation terminal kinds are not exposed as PB implementation work. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest passes for the scan bridge helper tests, including canonical notify parity. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | The test suite or a focused assertion verifies the live helper and managed template helper terminal-token sets match. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Bridge applicability and ADR/DCL clause preflights pass on this revised proposal and on the implementation report. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only` for the implementation is limited to the three in-root target paths plus the bridge report. |

Minimum verification commands after implementation:

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; .venv\Scripts\python.exe -m pytest -o addopts="" --basetemp .gtkb-state\pytest-runs\scan-bridge-terminal-token-parity platform_tests/scripts/test_scan_bridge.py -q --tb=short
.venv\Scripts\python.exe -m ruff check .claude/skills/bridge/helpers/scan_bridge.py groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py platform_tests/scripts/test_scan_bridge.py
.venv\Scripts\python.exe -m ruff format --check .claude/skills/bridge/helpers/scan_bridge.py groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py platform_tests/scripts/test_scan_bridge.py
```

## Acceptance Criteria

- Live bridge scan helper terminal-kind tokens match canonical notify terminal-kind tokens.
- Managed template bridge scan helper terminal-kind tokens match the live helper.
- `platform_tests/scripts/test_scan_bridge.py` passes.
- Ruff lint and format checks pass for all target paths.
- No canonical notify token changes are made unless separately justified and approved.

## Risk And Rollback

Risk is low. The change is a narrow token-list synchronization plus tests. The
main regression risk is suppressing a bridge kind that should remain PB
actionable; using the canonical notify token set as the source of truth controls
that risk. Rollback is a normal revert of the two helper updates and focused
test changes.

## Recommended Commit Type

`fix:` - this corrects a bridge routing parity defect.

