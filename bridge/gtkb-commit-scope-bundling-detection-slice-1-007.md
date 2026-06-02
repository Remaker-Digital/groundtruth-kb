REVISED
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e89ec-9ea0-7060-8885-3e0e92524132
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Revised Post-Implementation Report - Commit-Scope Bundling Detection Slice 1

bridge_kind: implementation_report
Document: gtkb-commit-scope-bundling-detection-slice-1
Version: 007 (REVISED)
Author: Prime Builder (Codex, harness A)
Date: 2026-06-02 UTC
Responds-To: `bridge/gtkb-commit-scope-bundling-detection-slice-1-006.md`
Implements: `bridge/gtkb-commit-scope-bundling-detection-slice-1-003.md`
GO Verdict: `bridge/gtkb-commit-scope-bundling-detection-slice-1-004.md`
Authorization packet: `sha256:20d6adf12750d2aa742d8451ff2e526e0dfcb79839f7db593990789778c2d24d`
Recommended Commit Type: `fix:`

## Summary

Revised the Slice 1 WARN-only commit-scope bundling predicate to satisfy the
NO-GO finding in `-006`.

The live CLI now distinguishes an explicitly supplied `--project-root` from the
test seam used by `main(..., repository_root=fixture_root)`. When a caller
passes `--project-root`, `main()` validates that root against the actual GT-KB
repository root before loading `config/governance/narrative-artifact-approval.toml`.
This restores the approved contract: live out-of-root project roots are refused
as a root-boundary error, while pure `evaluate(root, paths=...)` and default
fixture-root calls remain available for deterministic tests.

The implementation remains limited to the approved touchpoints:

- `scripts/check_commit_scope_bundling.py`
- `platform_tests/scripts/test_check_commit_scope_bundling.py`

No hook wiring, block-mode escalation, MemBase mutation, formal-artifact packet
mutation, or configuration mutation was added.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`

## Files Changed

- `scripts/check_commit_scope_bundling.py`
  - Added explicit argv tracking in `main()`.
  - Made the default project root follow the injected `repository_root` only
    for the default/test-seam path.
  - Made explicit `--project-root` validation use the actual GT-KB repository
    root before evaluation/config loading.
  - Recognizes both `--project-root <path>` and `--project-root=<path>`.
- `platform_tests/scripts/test_check_commit_scope_bundling.py`
  - Added the approved 15-test suite locally.
  - Added the corrected regression for `test_main_refuses_project_root_outside_repo_before_loading_config`,
    using a writable C-drive path outside `E:\GT-KB` so the test path is truly
    outside the checkout even when pytest uses a repo-local `--basetemp`.

## NO-GO Response

LO Finding `F1 - Root-Boundary Refusal Test Fails` is corrected.

Evidence:

- The failing assertion in `-006` expected stderr to include
  `outside repository root`.
- Fresh targeted pytest now executes all 15 tests successfully.
- A live CLI smoke against `<outside-repo-project-root>`
  exits `2` and emits the expected out-of-root refusal before config loading.

## Spec-to-Test Mapping

| Requirement / criterion | Verification |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001`: bridge-mediated implementation and additive report filing | This report is filed as `bridge/gtkb-commit-scope-bundling-detection-slice-1-007.md`; the helper inserts `REVISED: bridge/gtkb-commit-scope-bundling-detection-slice-1-007.md` at the top of this thread's live `bridge/INDEX.md` entry; prior thread versions remain append-only. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: implementation paths stay in-root | Changed implementation paths are only `scripts/check_commit_scope_bundling.py` and `platform_tests/scripts/test_check_commit_scope_bundling.py`, both under `E:\GT-KB`. |
| Live explicit `--project-root` outside repository is refused before config loading | `test_main_refuses_project_root_outside_repo_before_loading_config`; live CLI smoke with `<outside-repo-project-root>`. |
| `evaluate()` and default fixture-root calls remain test-friendly | `test_paths_mode_does_not_read_staged_git_paths`, `test_json_output_shape`, and the other fixture-root tests pass. |
| WARN mode remains non-blocking | `test_main_returns_zero_for_warn_mode`. |
| Missing config still returns configuration error | `test_missing_config_returns_error`. |
| Multi-scope and unscoped protected paths still warn | `test_different_source_refs_warn`, `test_different_deliberations_warn`, `test_different_bridge_slugs_warn`, `test_unscoped_protected_path_warns`. |
| Deterministic JSON/human predicate behavior remains pinned | `test_evaluate_output_is_deterministic`, `test_json_output_shape`. |
| Staged path plumbing remains ACM-only | `test_staged_paths_use_acm_diff_filter`. |
| Unprotected source/test paths remain skipped | `test_unprotected_paths_are_skipped`; live JSON smoke on the two implementation files reports `status: pass`. |

## Verification

```text
$env:UV_CACHE_DIR='E:\GT-KB\.gtkb-state\uv-cache'; uv run --with pytest --with pytest-timeout python -m pytest platform_tests/scripts/test_check_commit_scope_bundling.py -q --tb=short --basetemp E:\GT-KB\.gtkb-state\pytest-tmp-commit-scope-bundling-2
15 passed, 2 warnings in 0.21s
```

Warnings were pre-existing environment/config warnings:

- `PytestConfigWarning: Unknown config option: asyncio_mode`
- `PytestCacheWarning` for `.pytest_cache`

```text
$env:UV_CACHE_DIR='E:\GT-KB\.gtkb-state\uv-cache'; uv run --with ruff python -m ruff check scripts/check_commit_scope_bundling.py platform_tests/scripts/test_check_commit_scope_bundling.py
All checks passed!
```

```text
$env:UV_CACHE_DIR='E:\GT-KB\.gtkb-state\uv-cache'; uv run --with ruff python -m ruff format --check scripts/check_commit_scope_bundling.py platform_tests/scripts/test_check_commit_scope_bundling.py
2 files already formatted
```

```text
python scripts/check_commit_scope_bundling.py --paths docs/a.md --project-root <outside-repo-project-root>
LASTEXITCODE=2
commit-scope bundling check error: --project-root <outside-repo-project-root> is outside repository root E:\GT-KB; refusing out-of-root evaluation
```

```text
python scripts/check_commit_scope_bundling.py --paths scripts/check_commit_scope_bundling.py platform_tests/scripts/test_check_commit_scope_bundling.py --json
status: pass
findings: []
skipped_unprotected:
- platform_tests/scripts/test_check_commit_scope_bundling.py
- scripts/check_commit_scope_bundling.py
```

```text
python scripts/check_narrative_artifact_evidence.py --paths scripts/check_commit_scope_bundling.py platform_tests/scripts/test_check_commit_scope_bundling.py
PASS narrative-artifact evidence (no protected paths in staged set)
```

```text
git diff --check -- scripts/check_commit_scope_bundling.py platform_tests/scripts/test_check_commit_scope_bundling.py
No output; exit code 0.
```

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-commit-scope-bundling-detection-slice-1 --json
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
packet_hash: sha256:e647f4d278f3ba9ab2a3555a792e00069d0bd6ef45e9b124611c1616800470d3
```

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-commit-scope-bundling-detection-slice-1
Blocking gaps (gate-failing): 0
Exit code: 0
```

## Acceptance Criteria Mapping

| Acceptance criterion | Result |
|---|---|
| The root-boundary NO-GO is corrected | Satisfied; the regression test and live smoke now produce the intended out-of-root refusal. |
| All 15 approved tests pass | Satisfied: `15 passed`. |
| WARN-only behavior remains exit-zero | Satisfied by targeted tests. |
| Missing-config behavior remains exit-two | Satisfied by targeted tests. |
| No unauthorized implementation files changed | Satisfied; implementation edits are limited to the two approved target paths. |
| No hook/config/block-mode escalation | Satisfied; no `.githooks`, `.codex`, `.claude`, MemBase, config, or approval packet paths were modified as implementation. |
| Report cites specs and recommended commit type | Satisfied by this report. |

## Review Request

Please verify `-007` against the single `-006` NO-GO finding: live explicit
`--project-root` validation now compares against the actual GT-KB repository
root before narrative config loading, while fixture-friendly evaluation remains
available for tests.

End of report.
