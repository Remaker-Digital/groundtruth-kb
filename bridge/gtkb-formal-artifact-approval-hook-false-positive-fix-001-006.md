NEW

# Implementation Report - Formal Artifact Approval Hook False Positive Fix

Implemented by: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Proposal: `bridge/gtkb-formal-artifact-approval-hook-false-positive-fix-001-004.md`
GO: `bridge/gtkb-formal-artifact-approval-hook-false-positive-fix-001-005.md`

## Claim

Implemented the approved false-positive correction for `.claude/hooks/formal-artifact-approval-gate.py`.

The hook no longer treats every occurrence of `scripts/harvest_session_deliberations.py` in raw shell text as a formal artifact mutation. Instead, it preserves the existing direct formal-artifact mutation patterns and adds command-aware script handling:

- `scripts/harvest_session_deliberations.py` is gated only when invoked with `--apply`.
- `--help` and default dry-run invocations are not formal mutations.
- `archive_claude_design_handoff.py` and `backfill_lo_reports.py` remain gated when invoked, except help flags.
- Merely mentioning a gated script path inside session-prompt handoff text no longer triggers this formal-artifact gate.

## Files Changed

- `.claude/hooks/formal-artifact-approval-gate.py`
- `platform_tests/hooks/test_formal_artifact_approval_gate.py`

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Spec-To-Test Mapping

| Specification | Verification |
|---|---|
| `GOV-ARTIFACT-APPROVAL-001` | Existing tests still prove direct formal deliberation writes block without a packet and valid manual/auto packets allow formal writes. New harvester `--apply` test proves formal mutation mode remains blocked. |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | Existing packet-validation tests still prove native-format approval evidence is required for formal writes. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | New session-prompt handoff regression proves supporting-record text is not misclassified as a formal artifact mutation. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | New help/dry-run/apply tests prove diagnostic lifecycle operations are unblocked while apply-mode mutation remains blocked. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | New tests preserve owner-visible formal mutation gates while narrowing only the supporting-record false positive. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This report is filed in live `bridge/INDEX.md` as the authoritative bridge state. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Implementation remained within the linked proposal and approved `target_paths`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | All mapped focused tests were executed and passed. |

## Verification Commands

```text
python -m pytest platform_tests/hooks/test_formal_artifact_approval_gate.py -q --tb=short
python -m ruff check .claude/hooks/formal-artifact-approval-gate.py platform_tests/hooks/test_formal_artifact_approval_gate.py
python -m ruff format --check .claude/hooks/formal-artifact-approval-gate.py platform_tests/hooks/test_formal_artifact_approval_gate.py
python scripts/harvest_session_deliberations.py --help
```

## Observed Results

- `python -m pytest platform_tests/hooks/test_formal_artifact_approval_gate.py -q --tb=short`: `12 passed, 1 warning`.
- `python -m ruff check .claude/hooks/formal-artifact-approval-gate.py platform_tests/hooks/test_formal_artifact_approval_gate.py`: `All checks passed!`
- `python -m ruff format --check .claude/hooks/formal-artifact-approval-gate.py platform_tests/hooks/test_formal_artifact_approval_gate.py`: `2 files already formatted`.
- `python scripts/harvest_session_deliberations.py --help`: exited `0` and displayed argparse help. This was the live diagnostic path that previously hit the false-positive block.

## Acceptance Status

- `--help` on the harvester script is not treated as a formal artifact mutation: satisfied.
- Default read-only/dry-run harvester invocation without `--apply` is not blocked solely because of the script path: satisfied by unit regression.
- Harvester `--apply` remains blocked without a valid formal approval packet: satisfied by unit regression.
- A session-prompt insertion command that mentions the harvester script in prompt text is not blocked by this hook solely because of that mention: satisfied by unit regression.
- Existing direct formal artifact mutation blocking remains intact: satisfied by existing and passing packet-gate tests.

## Risk / Rollback

Residual risk is that another raw-text false positive exists in a direct API regex outside the harvester-script path. That is outside this approved scope. Rollback is reverting the two approved target files to their prior broad-match behavior.
