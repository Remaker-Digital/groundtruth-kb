NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 2026-07-04T01-59-46Z-prime-builder-A-49c4fa
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex headless Prime Builder; approval_policy=never; model_reasoning_effort=xhigh; sandbox=workspace-write; dispatch_id=2026-07-04T01-59-46Z-prime-builder-A-49c4fa

# WI-5002 Codex Dotdir Sandbox ACL Correction

bridge_kind: prime_proposal
Document: gtkb-wi5002-codex-dotdir-sandbox-acl-correction
Version: 001
Date: 2026-07-04 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5002

target_paths: [".codex/**", ".claude/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py", "scripts/verify_codex_dispatch.py", "platform_tests/scripts/test_verify_codex_dispatch.py", "scripts/install_gt_path_shim.py", "platform_tests/scripts/test_install_gt_path_shim.py", "scripts/repair_codex_dotdir_acl.ps1", "platform_tests/scripts/test_repair_codex_dotdir_acl.py"]

implementation_scope: codex-sandbox-acl, harness-helper-parity, local-cli-shim, tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Proposal Claim

The latest WI-5002 add-dir repair thread is `NO-GO` at `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-006.md`. Loyal Opposition accepted that the static Codex invocation repair is present, but rejected another add-dir-only retry because `.codex/**` remains unwritable under Codex due to explicit NTFS Deny ACLs and the active sandbox still treats the hidden helper path as outside the writable project boundary.

This proposal replaces identical retries with a bounded correction plan:

1. add an idempotent Windows ACL repair/check script for `.codex/**` that removes explicit Deny ACEs for Codex sandbox identities while preserving the in-root project boundary, `workspace-write`, and the `CodexSandboxUsers` Modify allow entry;
2. extend Codex dispatch readiness verification so `.codex` helper writes fail static readiness when ACL/sandbox metadata still blocks the approved helper path;
3. restore a project-local role-reader shim path for `gt harness roles` so headless dispatch prompts do not depend on ambient bare `gt`;
4. align `.codex/skills/verify/helpers/write_verdict.py` with the canonical `.claude` and `.cursor` helper copies after the ACL repair; and
5. rerun the focused dispatch/helper/parser tests and ruff gates before filing any implementation report.

The implementation must not use `--dangerously-bypass-approvals-and-sandbox`, must not switch Codex to `danger-full-access`, must not ask another harness to write `.codex/**`, and must not use owner manual copy as a workaround.

## Requirement Sufficiency

Existing requirements sufficient. WI-5002, the active project authorization, the add-dir NO-GO chain, and the cited dispatch/parity/bridge specifications already define the required behavior: Codex Prime Builder must be able to complete approved in-root `.codex/**` helper writes through its own governed headless route without broad sandbox bypass or direct harness fallback.

No new owner decision is required to file this proposal. If Loyal Opposition determines that changing `.codex/**` ACL metadata exceeds the active PAUTH, it should return `NO-GO` with that authorization finding rather than approving implementation.

## In-Root Placement Evidence

All proposed source, test, helper, and runtime metadata targets remain inside `E:\GT-KB`:

- `.codex/**`
- `.claude/skills/verify/helpers/write_verdict.py`
- `.cursor/skills/verify/helpers/write_verdict.py`
- `platform_tests/skills/test_verified_finalization_validation_hardening.py`
- `scripts/verify_codex_dispatch.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`
- `scripts/install_gt_path_shim.py`
- `platform_tests/scripts/test_install_gt_path_shim.py`
- `scripts/repair_codex_dotdir_acl.ps1`
- `platform_tests/scripts/test_repair_codex_dotdir_acl.py`

Out-of-root user PATH placement, production deployment, credential mutation, retired poller restoration, and direct harness invocation remain out of scope.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - Codex PB dispatch must complete approved work without manual intervention or repeated identical retries.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - the repair must not use direct harness-to-harness fallback or another harness as Codex's `.codex/**` writer.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex-specific hook/sandbox gaps must be handled mechanically and audibly.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - helper behavior must not diverge across Claude, Codex, and Cursor after the sandbox boundary is repaired.
- `ADR-CROSS-HARNESS-PARITY-001` - generated/adapted harness helper surfaces must preserve behavior parity.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all active implementation and evidence paths remain inside the GT-KB root.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this follow-on proposal, implementation, and verification must use the numbered bridge chain and dispatcher-backed state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete governing specs, target paths, and requirement sufficiency are cited before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work item, and target paths are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must prove the ACL repair, helper write, role-reader shim, parity hashes, and focused tests.
- `GOV-STANDING-BACKLOG-001` - WI-5002 remains the canonical work item for the Codex hidden helper-surface blocker.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the failed add-dir-only route and corrected route are preserved as durable bridge evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - rejected broader sandbox and direct-fallback alternatives remain explicit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - repeated blocked dispatches triggered this corrected lifecycle step.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner directed stable unattended bridge processing, Codex as PB, Claude/Ollama as LO, and no direct harness fallback.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-003.md`, `-005.md`, `-007.md`, and `-009.md` - repeated Codex `.codex/**` write-denial reports.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-010.md` - Loyal Opposition accepted that identical Codex retries should stop until the write boundary changes.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-001.md` through `-007.md` - prior blocked attempts and the quarantined hidden helper write-boundary route.
- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-001.md` - replacement proposal for the `.codex` add-dir route.
- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-002.md` - Loyal Opposition GO approving the narrow add-dir route with conditions.
- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-003.md` - staged implementation report from the worker launched before add-dir could take effect.
- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-004.md` - NO-GO instructing the next worker to prove `.codex` writes, helper parity, parser fixes, and focused tests.
- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-005.md` - revised report proving the add-dir surface was present but `.codex` writes remained blocked.
- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-006.md` - current NO-GO instructing Prime Builder to stop add-dir-only retries and propose a sandbox/ACL, local shim, or equivalent correction plan.

## Owner Decisions / Input

- Owner decision `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` authorizes bounded work items and implementation authorization records needed to restore stable unattended bridge processing.
- Project authorization `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES` authorizes WI-5002 harness-helper and dispatcher-modernization repair work while forbidding direct harness fallback, broad sandbox bypass, credential mutation, production deployment, and retired poller restoration.
- No new owner decision is requested in this headless dispatch. If the ACL metadata correction requires additional owner approval, Loyal Opposition should mark that as a `NO-GO` authorization gap.

## Proposed Scope

The implementation may:

- inspect `.codex/**` ACLs and sandbox writability from an in-root script;
- add an idempotent Windows ACL repair/check script, preferably `scripts/repair_codex_dotdir_acl.ps1`, with a check-only mode and an apply mode;
- remove explicit Deny ACEs inherited on `.codex/**` only for the Codex sandbox identities that are blocking writes, while preserving in-root workspace-write constraints and `CodexSandboxUsers` Modify allow behavior;
- extend `scripts/verify_codex_dispatch.py` and focused tests to report `.codex` ACL/helper-write readiness, in addition to the existing add-dir and prohibited-flag checks;
- extend `scripts/install_gt_path_shim.py` or its tests so the project-local role-reader path expected by dispatch can be generated or validated without ambient bare `gt`;
- align `.codex/skills/verify/helpers/write_verdict.py` with the canonical `.claude` and `.cursor` helper copies after the ACL repair; and
- update the focused helper parser tests only as needed to prove the already-identified trailing-punctuation and subpath-suffix regressions are fixed consistently across helper copies.

The implementation must not:

- grant broad write access outside `E:\GT-KB`;
- change Codex to `danger-full-access`;
- add `--dangerously-bypass-approvals-and-sandbox`;
- route the `.codex/**` write through Claude, Cursor, Antigravity, Ollama, OpenRouter, or any other harness;
- mutate credentials, production deployment config, or retired poller assets; or
- claim VERIFIED until `.codex`, `.claude`, and `.cursor` helper hashes match and the focused tests pass.

## Cross-Harness Disposition

- Claude Code / harness B: `.claude/skills/verify/helpers/write_verdict.py` remains the canonical verify helper source. It may change only if the parser correction requires a canonical helper edit, and any such edit must be propagated byte-for-byte to Codex and Cursor before parity is claimed.
- Codex / harness A: `.codex/**` ACL repair and `.codex/skills/verify/helpers/write_verdict.py` alignment are the primary implementation target. Codex must perform its own approved `.codex/**` write after the ACL repair; another harness must not write `.codex/**` on Codex's behalf.
- Cursor / harness E: `.cursor/skills/verify/helpers/write_verdict.py` may be updated only to keep byte-identical behavior with the canonical Claude and Codex helper copies.
- Antigravity / harness C: no invocation, helper, hook, or configuration change is proposed.
- Ollama / harness D: no invocation, helper, hook, or configuration change is proposed.
- OpenRouter / harness F: no invocation, helper, hook, or configuration change is proposed.
- Waivers: none requested. Broad sandbox bypass, `danger-full-access`, direct harness-to-harness fallback, and owner manual copy remain rejected alternatives.

## Specification-Derived Verification Plan

The implementation report must include exact commands, observed outputs, helper hashes, and spec-to-test mapping for:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/verify_codex_dispatch.py --no-require-executable --json
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_install_gt_path_shim.py platform_tests/scripts/test_repair_codex_dotdir_acl.py platform_tests/skills/test_verified_finalization_validation_hardening.py -q --tb=short --basetemp .harness-tmp/pytest-wi5002-dotdir-acl
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/verify_codex_dispatch.py scripts/install_gt_path_shim.py platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_install_gt_path_shim.py platform_tests/scripts/test_repair_codex_dotdir_acl.py platform_tests/skills/test_verified_finalization_validation_hardening.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/verify_codex_dispatch.py scripts/install_gt_path_shim.py platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_install_gt_path_shim.py platform_tests/scripts/test_repair_codex_dotdir_acl.py platform_tests/skills/test_verified_finalization_validation_hardening.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py
```

Required assertions:

- Codex headless argv still includes `--model gpt-5.5`, `approval_policy="never"`, `model_reasoning_effort="xhigh"`, `--sandbox workspace-write`, and an in-root `.codex` add-dir.
- Codex headless argv still omits `--dangerously-bypass-approvals-and-sandbox` and `danger-full-access`.
- `.codex/**` no longer has explicit Deny ACL entries that block Codex sandbox write/delete to the approved helper target.
- `CodexSandboxUsers` or the active Codex sandbox identity has sufficient Modify/write rights for `.codex/skills/verify/helpers/write_verdict.py`.
- Codex can copy or otherwise update `.codex/skills/verify/helpers/write_verdict.py` from the canonical `.claude` helper in a dispatcher-launched Prime Builder session.
- The project-local role-reader path expected by dispatch works for `harness roles`, or the implementation records an approved equivalent path with a clear compatibility rationale.
- `.claude/skills/verify/helpers/write_verdict.py`, `.codex/skills/verify/helpers/write_verdict.py`, and `.cursor/skills/verify/helpers/write_verdict.py` have identical SHA-256 hashes after helper alignment.
- The helper parser no longer retains trailing punctuation on dot-directory paths and no longer extracts partial suffixes from diff-stat lines.

## Acceptance Criteria

- [ ] Codex can write `.codex/skills/verify/helpers/write_verdict.py` from its own dispatcher-launched Prime Builder route without broad sandbox bypass or direct harness fallback.
- [ ] The ACL repair/check is idempotent, scoped to `.codex/**`, and produces machine-readable or plainly copyable evidence for the implementation report.
- [ ] Codex dispatch readiness fails closed when `.codex` helper writes remain blocked by ACL/sandbox metadata.
- [ ] A project-local `gt harness roles` entrypoint is available for dispatcher prompts without relying on ambient bare `gt`.
- [ ] `.claude`, `.codex`, and `.cursor` verify helpers are byte-identical after alignment.
- [ ] Focused pytest, ruff check, and ruff format gates pass for the changed source, script, test, and helper paths.

## Risk And Rollback

Risk: ACL repair can accidentally broaden `.codex/**` write access if implemented as a blunt reset. Mitigation: the script must be scoped to `.codex/**`, remove only the Deny ACEs that block Codex sandbox write/delete, preserve the in-root project boundary, and expose check-only evidence before apply.

Risk: a project-local CLI shim can create confusion with ambient `gt`. Mitigation: the implementation must prove the expected project-local path and document whether it is a true `gt.exe` console script or an approved local equivalent. It must not depend on user PATH state.

Risk: helper parity changes can drift across harness copies. Mitigation: run the focused helper parser tests across Claude, Codex, and Cursor copies and record SHA-256 hashes in the implementation report.

Rollback for source/test changes is a normal git revert of the approved file set. If ACL changes are applied and need rollback, restore `.codex/**` ACL inheritance from the pre-apply ACL snapshot recorded by the repair script. Bridge files remain append-only and must not be deleted.

## Pre-Filing Preflight Subsection

Pre-filing checks to run before live filing:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5002-codex-dotdir-sandbox-acl-correction --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-001.md --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5002-codex-dotdir-sandbox-acl-correction --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-001.md
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_proposal_wi_id_collision_check.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-001.md --strict
```

Observed pre-filing result:

- Applicability preflight: exit 0; `preflight_passed: true`; `packet_hash: sha256:4030642fe0a38a67aaf75840c465eb197ee950d65ca8a43cd13aa4e59229b158`; `missing_required_specs: []`; `missing_advisory_specs: []`.
- ADR/DCL clause preflight: exit 0; `Blocking gaps (gate-failing): 0`.
- WI collision check: exit 0; `has_collisions: false`; only declared work item `WI-5002` was found.

## Recommended Commit Type

fix - this is a bounded repair for broken Codex headless `.codex/**` write capability, role-reader availability, and helper parity for an existing WI-5002 blocker.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
