NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop; transcript role ::init gtkb pb; Default mode; PowerShell; project root E:\GT-KB
author_metadata_source: explicit current Codex session metadata plus active implementation-start packet

bridge_kind: implementation_report
Document: gtkb-wi5116-per-thread-finalization-repair
Version: 003
Author: Prime Builder Codex A
Date: 2026-07-16 UTC
Responds to: bridge/gtkb-wi5116-per-thread-finalization-repair-002.md

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5116

target_paths: ["scripts/per_thread_finalization_repair.py", "platform_tests/scripts/test_per_thread_finalization_repair.py", "docs/procedures/per-thread-finalization-repair.md"]
Recommended commit type: fix

## Summary

Implemented the GO-approved, report-only per-thread finalization repair planner and runbook. The new CLI groups current dirty bridge paths by thread, derives terminal status from the numbered bridge chain, uses the existing `implementation_authorization.extract_target_paths` parser for VERIFIED report scope, and emits fail-closed classes for dirty targets, missing scope, in-flight bridge chains, excluded active handoff programs, and mixed provenance.

The tool has no mutation flags and reports `"mutation_capabilities": []`.

## Files Changed

- `scripts/per_thread_finalization_repair.py`
- `platform_tests/scripts/test_per_thread_finalization_repair.py`
- `docs/procedures/per-thread-finalization-repair.md`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

- `DELIB-202666274` backs the active Tree Stabilization PAUTH used for this implementation.
- Owner directive in Codex session `019f6bf6-3e6d-7761-be14-fb894a0e84d2`: "Open a bridge proposal for a bounded per-thread finalization-repair tool/runbook."

## Implementation Notes

- The CLI uses the canonical `worktree_finalization_triage.build_plan()` source so counts use expanded untracked paths (`--untracked-files=all`) rather than collapsed directory counts.
- Tests use isolated git repositories and constructed bridge chains, not live-tree counts.
- The runbook states that actual finalization remains a one-thread operation through the approved finalizer path or an independently reviewed equivalent; the new planner does not stage, commit, delete, push, mutate dispatcher state, update PAUTH, or author bridge statuses.
- The sample live run excluded WI-5320, WI-5328, and WI-5330 as requested by the handoff boundary.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python -m pytest platform_tests/scripts/test_per_thread_finalization_repair.py -q --tb=short` | yes | Passes fixture tests that derive lifecycle status from numbered bridge files and refuse in-flight `NEW` chains. |
| `GOV-WORK-TREE-HYGIENE-001` | `python -m pytest platform_tests/scripts/test_per_thread_finalization_repair.py -q --tb=short` | yes | Passes dirty-target, missing-scope, shared-target, and unattributed-path STOP tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5116-per-thread-finalization-repair --expires-minutes 60` | yes | Start packet issued for exactly the three approved target paths under active PAUTH. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `python scripts/per_thread_finalization_repair.py --format json --exclude-wi WI-5320 --exclude-wi WI-5328 --exclude-wi WI-5330` | yes | Output reports `"read_only": true` and `"mutation_capabilities": []`; no mutation flags exist. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python .claude/skills/bridge/helpers/impl_report_bridge.py plan gtkb-wi5116-per-thread-finalization-repair --compact` | yes | Latest status was `GO`; report path computed as `bridge/gtkb-wi5116-per-thread-finalization-repair-003.md`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Report carries forward the GO'd proposal's Specification Links. | yes | The implementation report lists all cited governing surfaces. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_per_thread_finalization_repair.py -q --tb=short` | yes | 8 focused tests passed. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `python scripts/bridge_claim_cli.py claim gtkb-wi5116-per-thread-finalization-repair --ttl-seconds 7200`; `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5116-per-thread-finalization-repair --expires-minutes 60` | yes | Claim and implementation-start packet were acquired before target-file writes. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Proposal and report filing use governed bridge helpers. | yes | Proposal was filed via bridge-propose helper; this report is filed via `impl_report_bridge.py file`. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Runbook plus report preserve the repair process as an artifact. | yes | Procedure document added under `docs/procedures/`. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Implementation report records owner directive, PAUTH, tests, and STOP classes. | yes | Evidence is in this report. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The sprawl repair is represented by proposal, GO, implementation report, and later verification. | yes | Bridge lifecycle is preserved. |

## Commands Executed

```text
python scripts/bridge_claim_cli.py claim gtkb-wi5116-per-thread-finalization-repair --ttl-seconds 7200
```

Result: claim acquired for session `019f6bf6-3e6d-7761-be14-fb894a0e84d2`; latest bridge status `GO`; grace expiry `2026-07-16T19:23:46Z`.

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5116-per-thread-finalization-repair --expires-minutes 60
```

Result: packet `sha256:c984527a0d906af0e31f3b381a43c80330a1c5c5c429ca36a6e11b5a77fab37b`; target paths are the three approved files.

```text
python -m pytest platform_tests/scripts/test_per_thread_finalization_repair.py -q --tb=short
```

Result: 8 passed.

```text
python -m ruff check scripts/per_thread_finalization_repair.py platform_tests/scripts/test_per_thread_finalization_repair.py
```

Result: All checks passed.

```text
python -m ruff format --check scripts/per_thread_finalization_repair.py platform_tests/scripts/test_per_thread_finalization_repair.py
```

Result: 2 files already formatted.

```text
python scripts/per_thread_finalization_repair.py --format json --exclude-wi WI-5320 --exclude-wi WI-5328 --exclude-wi WI-5330
```

Observed summary:

```json
{
  "classification": {
    "excluded_active_program": 11,
    "in_flight_bridge_chain": 49,
    "mixed_provenance_stop": 1,
    "terminal_verified_blocked_dirty_targets": 9,
    "terminal_verified_blocked_missing_scope": 3,
    "terminal_verified_repair_candidate": 1,
    "terminal_withdrawn_or_nonverified_documentation": 5
  },
  "source_dirty_paths": 1517,
  "source_actuator_actions": {
    "auto_drop_byte_identical": 5,
    "auto_ignore": 24,
    "manual_owner_review": 1441,
    "safe_commit": 10,
    "skip": 37
  },
  "read_only": true,
  "mutation_capabilities": []
}
```

The single current repair candidate from that live run was `gtkb-wi4567-bridge-proposal-filing-service`; all other current VERIFIED cases remained blocked or STOP-classified.

## Acceptance Status

- Report-only CLI exists and emits deterministic JSON/markdown plans.
- In-flight statuses are STOP-classified and not treated as implementation-finalizable.
- Dirty target paths and missing target scope are blocked.
- Explicit `--exclude-wi` values classify active external handoff work as excluded.
- The runbook states the one-thread, one-finalization-commit invariant and STOP conditions.
- Focused tests verify supported and unsafe classes.

## Risk / Rollback

Risk remains that an operator could misread any planner as permission to commit. The implementation mitigates this with no mutation flags, explicit STOP classes, empty mutation capabilities, and a runbook that routes actual commits through the approved finalization path.

Rollback is a scoped revert of:

- `scripts/per_thread_finalization_repair.py`
- `platform_tests/scripts/test_per_thread_finalization_repair.py`
- `docs/procedures/per-thread-finalization-repair.md`

Bridge proposal/report/verdict files are append-only audit artifacts and should not be deleted by rollback.
