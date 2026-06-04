NEW
author_identity: Codex Prime Builder automation
author_harness_id: A
author_session_context_id: 019e933c-8522-75e1-bf57-0fcb06fd8a89
author_model: GPT-5
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; user-assigned Prime Builder; workspace-write
author_metadata_source: keep-working automation environment

# GT-KB Bridge Implementation Report - gtkb-impl-start-gate-pretooluse-restore - 006

bridge_kind: implementation_report
Document: gtkb-impl-start-gate-pretooluse-restore
Version: 006 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-impl-start-gate-pretooluse-restore-005.md
Approved proposal: bridge/gtkb-impl-start-gate-pretooluse-restore-004.md
Recommended commit type: fix:

## Implementation Claim

Implemented the full-matcher restoration approved by GO `-005`.

`.claude/settings.json` now registers `.claude/hooks/implementation-start-gate.py` in the existing `Write|Edit|MultiEdit|Bash` PreToolUse group with `lo-file-safety-gate.py`. The under-scoped `Write|Edit` registration is removed, so the implementation-start gate is present only on the full mutation-surface matcher required by the parity contract.

## Authorization Evidence

- `python scripts\implementation_authorization.py begin --bridge-id gtkb-impl-start-gate-pretooluse-restore`
- Result: packet minted successfully for GO `bridge/gtkb-impl-start-gate-pretooluse-restore-005.md`.
- Packet hash: `sha256:30edd616ce8818f1be55e31eed763dedc7d50ea0d5576b4867a632fb660da0a2`.
- Authorized target path: `.claude/settings.json`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `.claude/rules/codex-review-gate.md`
- `.claude/hooks/implementation-start-gate.py`
- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_hook_registration_parity.py`

## Owner Decisions / Input

No new owner decision was required. This implementation follows the approved corrective GO at `bridge/gtkb-impl-start-gate-pretooluse-restore-005.md`, which authorized only `.claude/settings.json`.

## Prior Deliberations

- `DELIB-S358-IMPL-START-GATE-REGISTRATION-REMOVAL`
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`
- `bridge/gtkb-impl-start-gate-pretooluse-restore-004.md`
- `bridge/gtkb-impl-start-gate-pretooluse-restore-005.md`

## Bridge Filing Evidence

This implementation report is filed as `bridge/gtkb-impl-start-gate-pretooluse-restore-006.md`. The helper inserted a `NEW: bridge/gtkb-impl-start-gate-pretooluse-restore-006.md` row at the top of the `gtkb-impl-start-gate-pretooluse-restore` entry in `bridge/INDEX.md`. Prior bridge versions were not deleted or rewritten.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | The approved implementation-start gate is registered on the full mutation-surface matcher; structural check confirmed it is in group 2 only. |
| `GOV-RELIABILITY-FAST-LANE-001` | Diff is a surgical `.claude/settings.json` hook move/addition; no source, CLI, public API, deployment, credential, or MemBase mutation. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Durable bridge implementation report records the implementation and verification evidence. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Registration restores the gate path that reads live implementation-authorization packets for protected mutations. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the linked specs from the approved REVISED proposal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused parity test and structural JSON checks passed. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Defect-class WI now has REVISED -> GO -> implementation report chain. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Proposal, GO, implementation evidence, and pending verification are represented as bridge artifacts. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target path is platform-root `.claude/settings.json`; no `applications/` paths changed. |
| `.claude/rules/codex-review-gate.md` | Implementation restores the mechanical implementation-start gate registration described by the rule. |
| `.claude/hooks/implementation-start-gate.py` | Wrapper script unchanged; settings registration now points at it on the full matcher. |
| `scripts/implementation_start_gate.py` | Shared gate logic unchanged; registration now routes all approved mutation surfaces to it. |
| `platform_tests/scripts/test_hook_registration_parity.py` | Focused parity pytest on `platform_tests\scripts\test_hook_registration_parity.py` passed: 2 tests passed. |

## Commands Run

```text
python scripts\implementation_authorization.py begin --bridge-id gtkb-impl-start-gate-pretooluse-restore
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_hook_registration_parity.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -c "import json; json.load(open('.claude/settings.json', encoding='utf-8')); print('JSON valid')"
groundtruth-kb\.venv\Scripts\python.exe -c "import json; s=json.load(open('.claude/settings.json', encoding='utf-8')); g2=s['hooks']['PreToolUse'][1]; g3=s['hooks']['PreToolUse'][2]; assert g2['matcher']=='Write|Edit|MultiEdit|Bash'; assert any('implementation-start-gate' in h['command'] for h in g2['hooks']), 'gate missing from group 2'; assert not any('implementation-start-gate' in h['command'] for h in g3['hooks']), 'gate still in group 3'; print('OK: gate in group 2 only')"
```

## Observed Results

- Authorization packet minted successfully with target path `.claude/settings.json`.
- Parity test passed: `2 passed in 0.14s`.
- JSON validity check printed `JSON valid`.
- Structural check printed `OK: gate in group 2 only`.

## Files Changed

- `.claude/settings.json`

## Acceptance Criteria Status

- [x] Run implementation authorization begin for `gtkb-impl-start-gate-pretooluse-restore`.
- [x] Move `implementation-start-gate.py` to the `Write|Edit|MultiEdit|Bash` matcher group.
- [x] Remove `implementation-start-gate.py` from the narrower `Write|Edit` matcher group.
- [x] Run focused parity test.
- [x] Run structural verification proving the hook is in group 2 only.

## Risk And Rollback

Residual risk is limited to Claude-side runtime hook behavior that Codex cannot directly exercise through its own tool layer. The repo parity test and structural JSON check cover the approved registration contract.

Rollback is one JSON edit: remove the `implementation-start-gate.py` hook entry from the `Write|Edit|MultiEdit|Bash` group in `.claude/settings.json`. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the `.claude/settings.json` hook registration against the approved full-matcher scope.
2. Verify the command evidence above satisfies the GO `-005` implementation constraints.
