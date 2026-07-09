NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 2026-07-04T01-16-12Z-prime-builder-A-a70c75
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex headless Prime Builder; approval_policy=never; model_reasoning_effort=xhigh; sandbox=workspace-write; dispatch_id=2026-07-04T01-16-12Z-prime-builder-A-a70c75

# WI-5002 Codex Headless Add-Dir Invocation Repair - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5002-codex-headless-add-dir-invocation
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5002-codex-headless-add-dir-invocation-002.md
Approved proposal: bridge/gtkb-wi5002-codex-headless-add-dir-invocation-001.md
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5002
Recommended commit type: fix

## Implementation Claim

This is a staged implementation report, not a VERIFIED-ready completion claim.
The stage-one Codex headless invocation repair is complete:

- MemBase harness registry version `49` was appended for harness `A`.
- `harness-state/harness-registry.json` was regenerated from MemBase and now projects Codex headless argv with `--add-dir .codex`.
- `scripts/verify_codex_dispatch.py` now fails static readiness unless Codex headless argv exposes an in-root `.codex` add-dir and omits `--dangerously-bypass-approvals-and-sandbox`.
- `platform_tests/scripts/test_verify_codex_dispatch.py` and `platform_tests/scripts/test_dispatcher_runtime.py` now cover the `.codex` add-dir requirement and dispatcher command rendering.

The final helper parity step is still blocked in this already-running Codex worker. Two direct attempts to copy the canonical helper into `.codex/skills/verify/helpers/write_verdict.py` failed with `Access to the path 'E:\GT-KB\.codex\skills\verify\helpers\write_verdict.py' is denied.` This matches the approved two-dispatch path: this worker was launched before the corrected `--add-dir .codex` argv could take effect.

## Implementation Authorization Evidence

- Implementation-start command: `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi5002-codex-headless-add-dir-invocation`
- Observed result: exit 0; `latest_status: GO`; `packet_hash: sha256:db584113ab7acd6199fdfafcc6a6ea8d95342df647aed0d2ee8403e6fba26126`; active PAUTH `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES`; target path globs matched the GO proposal.
- Work-intent command: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi5002-codex-headless-add-dir-invocation`
- Observed result: exit 0; rowid `29793`; session id `2026-07-04T01-16-12Z-prime-builder-A-a70c75`; `claim_kind: go_implementation`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - Codex PB dispatch must complete approved work without manual intervention.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - the fix must not use direct harness-to-harness fallback or a different harness as Codex's writer.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex-specific hook/sandbox gaps must be handled mechanically and audibly.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - helper behavior must not diverge across Claude, Codex, and Cursor after the sandbox route is repaired.
- `ADR-CROSS-HARNESS-PARITY-001` - generated/adapted harness surfaces must preserve behavior parity.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - proposal, implementation, and verification must use the numbered bridge chain and dispatcher-backed state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete governing specs, target paths, and requirement sufficiency are cited before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work item, and target paths are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must prove the changed invocation and the subsequent `.codex` write path.
- `GOV-STANDING-BACKLOG-001` - WI-5002 remains the canonical backlog item for this blocker.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the failed route and corrected route are preserved as durable bridge evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the implementation preserves evidence for rejected broader sandbox routes.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - repeated blocked dispatches triggered this corrected lifecycle step.

## Owner Decisions / Input

- Owner decision `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` authorizes bounded work items and implementation authorization records needed to restore stable unattended bridge processing.
- Project authorization `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES` authorizes this WI-5002 repair scope.
- No new owner decision was required or requested in this headless worker.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner directed stable unattended bridge processing, Codex as PB, Claude/Ollama as LO, and no direct harness fallback.
- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-001.md` - replacement proposal with the explicit two-dispatch completion path.
- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-002.md` - Loyal Opposition GO verdict approving the narrow add-dir route.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/verify_codex_dispatch.py --no-require-executable --json` returned `static_ok: true`, `dispatchable: true`, and `codex_helper_add_dir_ok: true` for harness `A`. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | `platform_tests/scripts/test_verify_codex_dispatch.py` includes a negative test for `--dangerously-bypass-approvals-and-sandbox`; `ruff check` found no direct harness fallback change in the touched files. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | The failed `Copy-Item` attempts against `.codex/skills/verify/helpers/write_verdict.py` are preserved as mechanical evidence that this worker still lacks the newly projected `.codex` write root. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`; `ADR-CROSS-HARNESS-PARITY-001` | Not satisfied in this worker: SHA-256 for `.codex/skills/verify/helpers/write_verdict.py` remains `9B342375416890D3D3A905DDDEB4EB3C416118565314E118D3A13437963BBD05`, while `.claude` and `.cursor` are `E2FFEFBF5ADFBFE8582FCE8A0352422A5C91C688FC405EB9E0690F99ED4D0976`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Live scan showed latest status `GO`; implementation authorization packet was created before protected mutations; this report is filed as the next numbered bridge version. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Not satisfied for final verification: focused pytest run reported `177 passed, 4 failed`; the failures are helper-parser parity tests, and the `.codex` helper copy remains blocked. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli harness roles`
  - Fallback used because `groundtruth-kb/.venv/Scripts/gt.exe` is absent in this checkout.
  - Observed result after mutation: harness `A` projected as version `49` with `--add-dir`, `.codex`.
- `groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli harness set-invocation-surface --harness A --surface headless --value-json <json> --reason 'WI-5002 add .codex writable root to Codex headless dispatch argv'`
  - Observed result: exit 0; harness `A` version `49`.
- `Copy-Item -LiteralPath '.claude\skills\verify\helpers\write_verdict.py' -Destination '.codex\skills\verify\helpers\write_verdict.py' -Force`
  - Observed result before and after registry update: exit 1; access denied for `.codex/skills/verify/helpers/write_verdict.py`.
- `groundtruth-kb/.venv/Scripts/ruff.exe format scripts/verify_codex_dispatch.py platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py`
  - Observed result: `3 files left unchanged`.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/verify_codex_dispatch.py --no-require-executable --json`
  - Observed result: `static_ok: true`; `dispatchable: true`; `codex_helper_add_dir: ".codex"`; `forbidden_flags_present: []`.
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/skills/test_verified_finalization_validation_hardening.py -q --tb=short --basetemp .harness-tmp/pytest-wi5002-add-dir`
  - Observed result: `177 passed, 4 failed, 3 warnings`.
- `groundtruth-kb/.venv/Scripts/ruff.exe check platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/skills/test_verified_finalization_validation_hardening.py scripts/verify_codex_dispatch.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py`
  - Observed result: `All checks passed!`
- `groundtruth-kb/.venv/Scripts/ruff.exe format --check platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/skills/test_verified_finalization_validation_hardening.py scripts/verify_codex_dispatch.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py`
  - Observed result: `6 files already formatted`.

## Observed Results

Stage-one invocation repair is successful:

- `harness-state/harness-registry.json` now contains harness `A` headless argv ending in `--add-dir`, `.codex`.
- The generated projection timestamp is `2026-07-04T01:22:00Z`.
- `scripts/verify_codex_dispatch.py --no-require-executable --json` reports `static_ok: true` and `dispatchable: true`.
- The Codex readiness and dispatcher runtime tests covering this change passed inside the focused pytest run.

Remaining blockers:

- Current worker still cannot write `.codex/skills/verify/helpers/write_verdict.py`.
- Helper parity remains incomplete because `.codex` hash differs from `.claude` and `.cursor`.
- Focused pytest failures:
  - `test_claimed_repo_path_parser_preserves_dot_directories[claude]`
  - `test_claimed_repo_path_parser_preserves_dot_directories[codex]`
  - `test_claimed_repo_path_parser_preserves_dot_directories[cursor]`
  - `test_claimed_repo_path_parser_does_not_extract_subpath_suffix[codex]`

## Files Changed By This Run

- `groundtruth.db`
- `harness-state/harness-registry.json`
- `scripts/verify_codex_dispatch.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Related Dirty Scope Observed But Not Completed By This Run

The worktree already contains broader helper-parity edits, including `.claude/skills/verify/helpers/write_verdict.py`, `.cursor/skills/verify/helpers/write_verdict.py`, and `platform_tests/skills/test_verified_finalization_validation_hardening.py`. This worker did not broaden the repair into those paths beyond the active focused verification. The Codex helper path remains unchanged because the sandbox denied the write.

## Helper Hashes

- `.claude/skills/verify/helpers/write_verdict.py`: `E2FFEFBF5ADFBFE8582FCE8A0352422A5C91C688FC405EB9E0690F99ED4D0976`
- `.codex/skills/verify/helpers/write_verdict.py`: `9B342375416890D3D3A905DDDEB4EB3C416118565314E118D3A13437963BBD05`
- `.cursor/skills/verify/helpers/write_verdict.py`: `E2FFEFBF5ADFBFE8582FCE8A0352422A5C91C688FC405EB9E0690F99ED4D0976`

## Recommended Commit Type

- Recommended commit type: `fix`
- Diff-stat justification: this is a bounded repair to broken Codex headless dispatch configuration and readiness verification. It intentionally avoids broad sandbox bypass and direct harness fallback.

## Acceptance Criteria Status

- [x] Harness `A` headless argv preserves `--model gpt-5.5`.
- [x] Harness `A` headless argv preserves `approval_policy="never"`.
- [x] Harness `A` headless argv preserves `model_reasoning_effort="xhigh"`.
- [x] Harness `A` headless argv preserves `--sandbox workspace-write`.
- [x] Harness `A` headless argv now includes an in-root `.codex` add-dir.
- [x] Harness `A` headless argv does not include `--dangerously-bypass-approvals-and-sandbox`.
- [x] Harness `A` headless argv does not include `--sandbox danger-full-access`.
- [ ] `.codex/skills/verify/helpers/write_verdict.py` write succeeds from Codex.
- [ ] `.codex`, `.claude`, and `.cursor` helper hashes match.
- [ ] Full spec-derived verification passes.

## Risk And Rollback

Rollback for the completed stage-one change is to restore harness `A` invocation surface to the prior headless argv in MemBase and regenerate `harness-state/harness-registry.json`. The risk of the current staged state is low: it adds only `.codex` as an extra writable root while preserving `workspace-write` and forbidding broad bypass flags. The next Codex PB dispatch should be launched with the updated argv and can attempt the `.codex` helper copy again.

## Loyal Opposition Asks

1. Treat this report as a staged invocation-repair report, not a final completion claim.
2. Do not record `VERIFIED` yet unless the review scope intentionally accepts only stage-one invocation repair.
3. If final helper parity remains required, return `NO-GO` with direction for the next Codex PB dispatch to retry the `.codex` helper write using the newly projected `--add-dir .codex` surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
