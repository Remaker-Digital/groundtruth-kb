NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f2955-5185-7063-9b1c-de683358bf8a
author_model: gpt-5
author_model_version: 5
author_model_configuration: Codex desktop Prime Builder; approval_policy=never; filesystem unrestricted; implementation_authorization=sha256:a22f06cd4eff798ccafd0b07dec16caa6565a8f5adeb24ecfc76993a02a4b661

# WI-5002 Codex Dotdir Sandbox ACL Correction - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5002-codex-dotdir-sandbox-acl-correction
Version: 003 (NEW; post-implementation report)
Date: 2026-07-04 UTC
Responds to GO: bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-002.md
Approved proposal: bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-001.md
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5002
Recommended commit type: fix

## Implementation Claim

Prime Builder implemented the approved WI-5002 `.codex/**` repair route. The implementation removed the live explicit Deny ACL blocker on `E:\GT-KB\.codex`, preserved/adds scoped Modify allow evidence for `CodexSandboxUsers` and the active Codex Windows identity, restored `.codex` helper writability from this Codex session, extended Codex dispatch readiness to fail closed on `.codex` ACL repair needs, proved the project-local role-reader route, and aligned the verify helper across `.claude`, `.codex`, and `.cursor`.

No broad sandbox bypass, `danger-full-access`, direct harness fallback, credential mutation, production deployment, out-of-root placement, or retired poller restoration was used.

## Authorization Evidence

- Owner implementation approval: `DELIB-20260703-WI5002-DOTDIR-SANDBOX-ACL-IMPLEMENTATION-APPROVED`.
- Work-intent claim after compaction/session renewal: rowid `29810`, session id `019f2955-5185-7063-9b1c-de683358bf8a`, `acting_role: prime-builder`, grace expiry `2026-07-04T03:55:24Z`.
- Implementation-start authorization packet: `sha256:a22f06cd4eff798ccafd0b07dec16caa6565a8f5adeb24ecfc76993a02a4b661`, expires `2026-07-04T04:45:24Z`.

## Files Changed

- `.claude/skills/verify/helpers/write_verdict.py`
- `.codex/skills/verify/helpers/write_verdict.py`
- `.cursor/skills/verify/helpers/write_verdict.py`
- `platform_tests/skills/test_verified_finalization_validation_hardening.py`
- `scripts/verify_codex_dispatch.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`
- `scripts/install_gt_path_shim.py`
- `platform_tests/scripts/test_install_gt_path_shim.py`
- `scripts/repair_codex_dotdir_acl.ps1`
- `platform_tests/scripts/test_repair_codex_dotdir_acl.py`

Runtime ACL metadata changed on `.codex/**`: explicit risky Deny ACEs were removed from `.codex`, and scoped Modify allow entries are present for `CodexSandboxUsers` and `DESKTOP-G6Q5ANI\micha`.

## Implementation Details

- Added `scripts/repair_codex_dotdir_acl.ps1` with `Check` and `Apply` modes, project-root `.codex` target validation, explicit risky Deny ACE detection/removal, current-identity and `CodexSandboxUsers` Modify allow reporting, recursive child checks, and JSON evidence.
- Fixed the ACL script's deny-removal persistence bug: `RemoveAccessRuleSpecific(...)` is a void call in this PowerShell/.NET path, so the script now marks the ACL as changed after calling it and persists via `SetAccessControl`.
- Extended `scripts/verify_codex_dispatch.py` to require the `.codex` add-dir, reject broad sandbox bypass flags, run the `.codex` ACL check on Windows, and include ACL readiness in `static_ok` and `dispatchable`.
- Preserved the local `gt` role-reader route by rendering launcher content through the project venv Python plus in-root `groundtruth-kb/src` on `PYTHONPATH`; verified that route with `python -m groundtruth_kb.cli harness roles`.
- Restored helper parity by copying the canonical `.claude/skills/verify/helpers/write_verdict.py` to `.codex` and `.cursor` after the ACL repair.
- Fixed helper claimed-path normalization so trailing punctuation is stripped consistently after token extraction, and preserved the dot-directory/subpath regression tests across all three helper copies.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Commands Run

```text
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\repair_codex_dotdir_acl.ps1 -Mode Apply -Json
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\repair_codex_dotdir_acl.ps1 -Mode Check -Json
groundtruth-kb\.venv\Scripts\python.exe scripts\verify_codex_dispatch.py --no-require-executable --json
$env:PYTHONPATH = 'E:\GT-KB\groundtruth-kb\src;' + $env:PYTHONPATH; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli harness roles
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_verify_codex_dispatch.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_install_gt_path_shim.py platform_tests\scripts\test_repair_codex_dotdir_acl.py platform_tests\skills\test_verified_finalization_validation_hardening.py -q --tb=short --basetemp .harness-tmp\pytest-wi5002-dotdir-acl
groundtruth-kb\.venv\Scripts\ruff.exe check scripts\verify_codex_dispatch.py scripts\install_gt_path_shim.py platform_tests\scripts\test_verify_codex_dispatch.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_install_gt_path_shim.py platform_tests\scripts\test_repair_codex_dotdir_acl.py platform_tests\skills\test_verified_finalization_validation_hardening.py .claude\skills\verify\helpers\write_verdict.py .codex\skills\verify\helpers\write_verdict.py .cursor\skills\verify\helpers\write_verdict.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts\verify_codex_dispatch.py scripts\install_gt_path_shim.py platform_tests\scripts\test_verify_codex_dispatch.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_install_gt_path_shim.py platform_tests\scripts\test_repair_codex_dotdir_acl.py platform_tests\skills\test_verified_finalization_validation_hardening.py .claude\skills\verify\helpers\write_verdict.py .codex\skills\verify\helpers\write_verdict.py .cursor\skills\verify\helpers\write_verdict.py
git diff --check -- .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py scripts/verify_codex_dispatch.py platform_tests/scripts/test_verify_codex_dispatch.py scripts/install_gt_path_shim.py platform_tests/scripts/test_install_gt_path_shim.py scripts/repair_codex_dotdir_acl.ps1 platform_tests/scripts/test_repair_codex_dotdir_acl.py platform_tests/skills/test_verified_finalization_validation_hardening.py
```

## Observed Results

- ACL apply removed the live risky Deny ACEs and added the missing active-identity allow. A same-session post-apply rerun reported `exit: 0`, `needs_repair: false`, `risky_deny_count: 0`, `errors_count: 0`, `checked_count: 174`.
- Final ACL check reported `CodexSandboxUsers.allow_present: true` and `current_identity.allow_present: true` for `DESKTOP-G6Q5ANI\micha`.
- Codex dispatch verifier returned exit 0 with `static_ok: true`, `dispatchable: true`, `codex_helper_add_dir_ok: true`, `codex_dotdir_acl_ok: true`, `checked_count: 174`, and no forbidden flags.
- Project-local role-reader command returned exit 0 and printed the harness registry; harness `A` remains `harness_name: codex`, `role: ["prime-builder"]`, headless argv includes `--sandbox workspace-write`, `--add-dir .codex`, `approval_policy="never"`, and `model_reasoning_effort="xhigh"`.
- Focused pytest result: `202 passed, 1 warning in 22.61s`; the warning is the pre-existing pytest config warning for unknown `asyncio_mode`.
- Ruff check result: `All checks passed!`
- Ruff format result: `10 files already formatted`.
- `git diff --check` returned exit 0; output contained only CRLF working-copy warnings.

## Helper Hashes

All three verify helper copies are byte-identical after Codex wrote `.codex/skills/verify/helpers/write_verdict.py` from the canonical `.claude` helper:

```text
.claude/skills/verify/helpers/write_verdict.py  3E87BDBEE3B5DEA7C260C0EB7508FE732BB3E6A23B164409C63D1886F6E0D3D4
.codex/skills/verify/helpers/write_verdict.py   3E87BDBEE3B5DEA7C260C0EB7508FE732BB3E6A23B164409C63D1886F6E0D3D4
.cursor/skills/verify/helpers/write_verdict.py  3E87BDBEE3B5DEA7C260C0EB7508FE732BB3E6A23B164409C63D1886F6E0D3D4
```

## Specification-Derived Verification Plan

| Spec / surface | Executed verification evidence |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `scripts\verify_codex_dispatch.py --no-require-executable --json` returned `static_ok: true` and `dispatchable: true`. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | `.codex` helper was written directly from this Codex session after ACL repair; no other harness fallback or manual owner copy was used. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `scripts/repair_codex_dotdir_acl.ps1` emits machine-readable ACL evidence and Codex verifier now reports `codex_dotdir_acl`. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` / `ADR-CROSS-HARNESS-PARITY-001` | Helper SHA-256 hashes match across `.claude`, `.codex`, and `.cursor`; parser tests run against every helper copy. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All changed source/test/helper/report paths are inside `E:\GT-KB`; ACL script refuses a target other than in-root `.codex`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Work-intent claim rowid `29810` and implementation packet `sha256:a22f06cd4eff798ccafd0b07dec16caa6565a8f5adeb24ecfc76993a02a4b661` preceded protected mutations. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff check, ruff format check, ACL check, helper hashes, dispatch verifier, and role-reader smoke evidence are recorded above. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This bridge report preserves the corrected route and supersedes the failed add-dir-only retry chain. |

## Acceptance Criteria Status

- [x] Codex can write `.codex/skills/verify/helpers/write_verdict.py` from its own approved session without broad sandbox bypass or direct harness fallback.
- [x] The ACL repair/check is idempotent, scoped to `.codex/**`, and produces JSON evidence.
- [x] Codex dispatch readiness fails closed when `.codex` ACL repair remains needed, covered by `test_evaluate_readiness_fails_when_codex_dotdir_acl_needs_repair`.
- [x] The project-local role-reader path works through venv Python plus in-root `PYTHONPATH`; `harness roles` returned the live registry.
- [x] `.claude`, `.codex`, and `.cursor` verify helpers are byte-identical after alignment.
- [x] Focused pytest, ruff check, and ruff format gates pass for the changed source, script, test, and helper paths.

## Residual Risk And Rollback

Residual risk is limited to `.codex` ACL metadata and the approved helper/readiness surfaces. Rollback for source/test/helper changes is a normal git revert of the files listed above. If ACL metadata rollback is required, restore the previous `.codex` ACL from operating-system ACL backup or owner-selected policy; do not reintroduce the explicit risky Deny ACEs unless a follow-on bridge proposal deliberately authorizes that.

Bridge files are append-only and must not be deleted.

## Loyal Opposition Asks

1. Verify that the ACL repair is sufficiently scoped to `.codex/**` and does not broaden write access outside the GT-KB root.
2. Verify that Codex dispatch readiness now fails closed on `.codex` ACL repair needs while passing on the live repaired tree.
3. Verify helper parity and parser behavior across `.claude`, `.codex`, and `.cursor`.
4. Return `VERIFIED` if the implementation satisfies the approved proposal; otherwise return `NO-GO` with concrete findings.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
