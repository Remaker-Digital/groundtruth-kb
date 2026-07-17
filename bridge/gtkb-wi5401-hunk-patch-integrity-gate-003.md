NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: 5
author_model_configuration: OpenAI Codex desktop interactive; reasoning=xhigh; approval_policy=never
author_metadata_source: codex-inline-non-bypass-writer

# Implementation Report - WI-5401 Hunk Patch Integrity Gate

bridge_kind: implementation_report
Document: gtkb-wi5401-hunk-patch-integrity-gate
Version: 003
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5401-HUNK-PATCH-INTEGRITY-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5401

target_paths: [".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py", "platform_tests/scripts/test_gtkb_bridge_writer.py"]

Responds to GO: bridge/gtkb-wi5401-hunk-patch-integrity-gate-002.md
Approved proposal: bridge/gtkb-wi5401-hunk-patch-integrity-gate-001.md

## Summary

Implemented the WI-5401 hunk-patch integrity gate across the VERIFIED finalizer helper projections and the shared provider bridge writer. Filed hunk artifacts are now validated from exact stored bytes before report acceptance or terminal finalization can rely on them: declared SHA-256 and byte size are checked when report metadata supplies them, patch path parsing uses raw bytes for Git headers, and corrupt or non-Git-applyable hunk artifacts fail closed.

The implementation preserves existing valid text and binary patch support, provider include-set coverage, same-path hygiene, disposable-index finalization, and helper parity across Claude Code, Codex, and Cursor projections.

## Implementation Claim

- Latest bridge status before implementation/reporting: `GO` at `bridge/gtkb-wi5401-hunk-patch-integrity-gate-002.md`.
- Live work-intent claim: `go_implementation`, rowid `32115`, session `019f6668-9974-7d72-a456-826f9a67e627`, `expired: false`, TTL/grace through `2026-07-17T11:06:56Z`.
- Implementation-start evidence: `.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5401-hunk-patch-integrity-gate.json`, created `2026-07-17T09:57:07Z`, expires `2026-07-17T11:57:07Z`.
- Packet hash: `sha256:af0c2bb05d36f0f6d08fd999e8e244270a2f57ad7e05fac78a8086772e0f67d3`.
- Pre-start packet hash: `sha256:215c55a47556b9e0428a87b52ee3ea89061185971a4a84a0330d8c1b9e384549`.
- Scope stayed inside the exact six approved `target_paths`; no bridge runtime, TAFE runtime, dispatcher runtime, database, credential, deployment, release, or unrelated worktree mutation is included in this report.

## Files Changed

- `.claude/skills/verify/helpers/write_verdict.py`
  - Added exact hunk-patch SHA-256 and byte-size metadata validation.
  - Reworked patch path parsing to inspect raw Git header bytes and fail closed on malformed/non-UTF-8 path headers.
  - Added disposable-index forward/reverse `git apply --check` validation before hunk patches can satisfy include coverage.
- `.codex/skills/verify/helpers/write_verdict.py`
  - Kept byte-for-byte parity with the Claude helper projection.
- `.cursor/skills/verify/helpers/write_verdict.py`
  - Kept byte-for-byte parity with the Claude helper projection.
- `scripts/gtkb_bridge_writer.py`
  - Added provider-side exact hunk-patch metadata validation, raw-byte path parsing, and forward/reverse Git applyability checks before hunk artifacts can cover modified includes.
- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`
  - Added regression coverage for declared size mismatch, declared SHA-256 mismatch, and corrupt/non-applyable hunk artifacts failing without committing a VERIFIED verdict.
  - Updated the existing apply-failure expectation to the new fail-closed Git-applyability diagnostic.
- `platform_tests/scripts/test_gtkb_bridge_writer.py`
  - Added provider coverage for declared size mismatch and corrupt/non-applyable hunk artifact rejection while preserving the existing binary patch coverage test.

Diff stat for the six approved targets: `6 files changed, 706 insertions(+), 59 deletions(-)`.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes the project-bound repair family.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5401-HUNK-PATCH-INTEGRITY-20260717` is active for `WI-5401` and the exact target inventory in this report.
- No new owner decision, waiver, credential action, release, deployment, destructive cleanup, or Git history operation is requested by this implementation report.

## Spec-To-Test Mapping

| Spec | Evidence |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | `git status --short -- <six approved targets>` showed only the six WI-5401 target files dirty; `git diff --check -- <six approved targets>` exited 0 with CRLF warnings only. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Thread state remained latest `GO` at `bridge/gtkb-wi5401-hunk-patch-integrity-gate-002.md`; this report is a Prime-authored `NEW` implementation report for version `003`. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The implementation adds source and regression tests plus this bridge implementation report carrying forward linked specifications, owner/PAUTH evidence, and observed verification results. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python .codex\skills\bridge\helpers\impl_report_bridge.py plan gtkb-wi5401-hunk-patch-integrity-gate --compact` carried forward the proposal's linked specification set and reported next version `003`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | New and affected tests were executed: 7 targeted hunk-integrity tests passed; the full finalizer test file passed 31/31. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Report includes `Project Authorization`, `Project`, `Work Item`, and exact `target_paths`; claim status reports `expired: false` for the same thread/session. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Owner/PAUTH evidence is explicitly listed; no new owner decision is embedded or implied. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All changed paths are inside `E:\GT-KB` platform/harness/test surfaces and do not resolve to Agent Red or another adopter application. |
| `GOV-STANDING-BACKLOG-001` | Work is bound to MemBase work item `WI-5401` under `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING`. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Codex helper projection was updated in parity with Claude and Cursor helper projections; no Codex-only fallback behavior was introduced. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Exact-byte artifact integrity evidence is now enforced by deterministic helper/provider checks rather than accepted as narrative-only evidence. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The bridge implementation report preserves the lifecycle transition from proposal `GO` to implementation `NEW` awaiting LO verification. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Projection parity command returned sizes `[52118, 52118, 52118]`, `claude==codex True`, and `claude==cursor True`. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Named implementation-start packet covers exactly the six target paths and active PAUTH `PAUTH-DISPATCHER-BLACK-BOX-WI5401-HUNK-PATCH-INTEGRITY-20260717`. |

## Commands Executed

```powershell
python scripts\bridge_claim_cli.py status gtkb-wi5401-hunk-patch-integrity-gate
```

Observed result: exit 0; claim kind `go_implementation`, session `019f6668-9974-7d72-a456-826f9a67e627`, `expired: false`, latest bridge status `GO`.

```powershell
python scripts\implementation_authorization.py validate --target .claude\skills\verify\helpers\write_verdict.py
python scripts\implementation_authorization.py validate --target .codex\skills\verify\helpers\write_verdict.py
python scripts\implementation_authorization.py validate --target .cursor\skills\verify\helpers\write_verdict.py
python scripts\implementation_authorization.py validate --target scripts\gtkb_bridge_writer.py
python scripts\implementation_authorization.py validate --target platform_tests\scripts\test_lo_verified_commit_atomicity.py
python scripts\implementation_authorization.py validate --target platform_tests\scripts\test_gtkb_bridge_writer.py
```

Observed result: exit 0 for all six targets; each target reported `authorized: true`.

```powershell
python -m py_compile .claude\skills\verify\helpers\write_verdict.py .codex\skills\verify\helpers\write_verdict.py .cursor\skills\verify\helpers\write_verdict.py scripts\gtkb_bridge_writer.py platform_tests\scripts\test_lo_verified_commit_atomicity.py platform_tests\scripts\test_gtkb_bridge_writer.py
```

Observed result: exit 0.

```powershell
python -m ruff check .claude\skills\verify\helpers\write_verdict.py .codex\skills\verify\helpers\write_verdict.py .cursor\skills\verify\helpers\write_verdict.py scripts\gtkb_bridge_writer.py platform_tests\scripts\test_lo_verified_commit_atomicity.py platform_tests\scripts\test_gtkb_bridge_writer.py
```

Observed result: exit 0; `All checks passed!`.

```powershell
python -m ruff format --check .claude\skills\verify\helpers\write_verdict.py .codex\skills\verify\helpers\write_verdict.py .cursor\skills\verify\helpers\write_verdict.py scripts\gtkb_bridge_writer.py platform_tests\scripts\test_lo_verified_commit_atomicity.py platform_tests\scripts\test_gtkb_bridge_writer.py
```

Observed result: exit 0; `6 files already formatted`.

```powershell
git diff --check -- .claude\skills\verify\helpers\write_verdict.py .codex\skills\verify\helpers\write_verdict.py .cursor\skills\verify\helpers\write_verdict.py scripts\gtkb_bridge_writer.py platform_tests\scripts\test_lo_verified_commit_atomicity.py platform_tests\scripts\test_gtkb_bridge_writer.py
```

Observed result: exit 0; warnings only that Git may replace LF with CRLF in `.cursor/skills/verify/helpers/write_verdict.py` and `platform_tests/scripts/test_lo_verified_commit_atomicity.py`.

```powershell
python -m pytest platform_tests\scripts\test_lo_verified_commit_atomicity.py::test_hunk_patch_declared_size_mismatch_fails_before_verdict platform_tests\scripts\test_lo_verified_commit_atomicity.py::test_hunk_patch_declared_sha_mismatch_fails_before_verdict platform_tests\scripts\test_lo_verified_commit_atomicity.py::test_corrupt_hunk_patch_fails_without_committing_verdict platform_tests\scripts\test_lo_verified_commit_atomicity.py::test_binary_hunk_patch_finalization_commits_reviewed_binary_include_only platform_tests\scripts\test_gtkb_bridge_writer.py::test_provider_hunk_coverage_recognizes_binary_patch_diff_git_header platform_tests\scripts\test_gtkb_bridge_writer.py::test_provider_hunk_coverage_rejects_declared_size_mismatch platform_tests\scripts\test_gtkb_bridge_writer.py::test_provider_hunk_coverage_rejects_corrupt_patch -q --tb=short
```

Observed result: exit 0; `7 passed in 15.51s`.

```powershell
python -m pytest platform_tests\scripts\test_lo_verified_commit_atomicity.py -q --tb=short
```

Observed result: exit 0; `31 passed in 85.79s`.

```powershell
python -m pytest platform_tests\scripts\test_gtkb_bridge_writer.py -q --tb=short
```

Observed result: exit 1; `13 passed`, `6 failed`. The failures are in pre-existing broad bridge-writer unit fixtures that invoke live bridge-compliance gate behavior with placeholder project/PAUTH metadata or fixture self-review metadata:

- `test_write_bridge_file_creates_numbered_file_with_metadata` failed with live `authorization-not-found` for placeholder fixture project/PAUTH metadata.
- `test_write_bridge_file_rejects_malformed_proposal_before_disk_write` failed on the same live authorization check before reaching the expected `Requirement Sufficiency` assertion.
- `test_write_bridge_file_accepts_pre_metadata_content_when_injection_skipped` and three parametrized verdict fixtures failed with live self-review verdict blocking.

The three WI-5401 provider hunk-coverage tests in this file passed in the targeted command above. This report does not claim the broad bridge-writer file is green; it records the unrelated live-gate fixture failures as residual verification risk.

```powershell
python -c "from pathlib import Path; paths=['.claude/skills/verify/helpers/write_verdict.py','.codex/skills/verify/helpers/write_verdict.py','.cursor/skills/verify/helpers/write_verdict.py']; data=[Path(p).read_bytes() for p in paths]; print('sizes', [len(b) for b in data]); print('claude==codex', data[0]==data[1]); print('claude==cursor', data[0]==data[2])"
```

Observed result: exit 0; `sizes [52118, 52118, 52118]`, `claude==codex True`, `claude==cursor True`.

## Acceptance Criteria Result

- Malformed or corrupt WI5222-style hunk artifacts are rejected before report acceptance or terminal finalization: PASS, covered by `test_corrupt_hunk_patch_fails_without_committing_verdict` and `test_provider_hunk_coverage_rejects_corrupt_patch`.
- Declared digest or size mismatches between report metadata and exact stored patch bytes are rejected fail-closed: PASS, covered by `test_hunk_patch_declared_size_mismatch_fails_before_verdict`, `test_hunk_patch_declared_sha_mismatch_fails_before_verdict`, and `test_provider_hunk_coverage_rejects_declared_size_mismatch`.
- Valid exact-byte text and binary patches still pass existing hunk finalization and provider-publication paths: PASS for targeted binary hunk finalizer and provider coverage tests.
- Provider bridge writer refuses modified includes whose hunk artifact is malformed, byte-mismatched, or not Git-applyable while preserving same-path hygiene: PASS for targeted provider coverage.
- Claude, Codex, and Cursor verify-helper projections remain behaviorally aligned and focused tests pass: PASS by byte parity and targeted/finalizer test evidence.

## Residual Risk

The full `platform_tests/scripts/test_gtkb_bridge_writer.py` file still has six failures caused by broad unit fixtures depending on live bridge-compliance gate state for placeholder project/PAUTH and self-review metadata. Those failures are not introduced by the WI-5401 hunk-patch integrity code path, but they prevent reporting the proposal's broad two-file pytest command as fully passing. Loyal Opposition should decide whether this is an implementation-blocking verification gap or a separate test-fixture isolation defect.

## Rollback

Rollback is a normal revert of the six changed source/test paths. Bridge files, claim records, implementation-start packets, and project authorization evidence are append-only audit artifacts and must not be deleted as rollback.

## Recommended Commit Type

Recommended commit type: `feat:`. This implementation adds a new fail-closed hunk artifact integrity enforcement capability across the verified-finalizer and provider-publication surfaces.
