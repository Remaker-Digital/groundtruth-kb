NEW

# GT-KB Bridge Implementation Report - gtkb-codex-skill-path-prefers-repo-local-adapters - 003

bridge_kind: implementation_report
Document: gtkb-codex-skill-path-prefers-repo-local-adapters
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-codex-skill-path-prefers-repo-local-adapters-002.md
Approved proposal: bridge/gtkb-codex-skill-path-prefers-repo-local-adapters-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4364
Recommended commit type: fix:

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019eeefd-99e6-7670-9956-f3bb46003309
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation Auto-builder

## Implementation Claim

Implemented the approved WI-4364 defect fix in commit `0d3df1ec0` (`fix: prefer repo codex skill adapters`).

The startup skill-discovery path now keeps the default root-contained behavior unchanged, and under `GTKB_DISCOVER_USER_EXTENSIONS=1` it resolves Codex skills through a Codex-specific preference order:

1. `project_root/.codex/skills`
2. `Path.home()/.codex/skills`

For Codex skill-name collisions, the in-root adapter wins and the home copy is not included in the resolved skill list. Codex skills that resolve only from the home-directory copy are surfaced in the startup model as `codex_skill_fallbacks`. Existing opt-in `.agents/skills` scanning remains available and unchanged.

## Implementation-Start Evidence

- Claim command: `python scripts/bridge_claim_cli.py claim gtkb-codex-skill-path-prefers-repo-local-adapters`
- Claim result: acquired for session `019eeefd-99e6-7670-9956-f3bb46003309` at `2026-06-22T11:13:43Z`.
- Authorization command: `python scripts/implementation_authorization.py begin --bridge-id gtkb-codex-skill-path-prefers-repo-local-adapters`
- Authorization result: authorized `true`; packet hash `sha256:25d2e50de73563674e8ab0e1a4a5b9e9c744db9e0375a25f4d3de1d136c765fe`; expires `2026-06-22T13:13:43Z`.
- Authorized target globs:
  - `scripts/session_self_initialization.py`
  - `platform_tests/scripts/test_session_self_initialization.py`

## Code Quality Baseline

- Before implementation, `git status --short -- scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py bridge/gtkb-codex-skill-path-prefers-repo-local-adapters-*.md` returned no output, so the approved target paths were clean.
- The wider worktree had unrelated staged and unstaged changes, including bridge artifacts from other threads and the WI-3489 report filed earlier in this run. They were not modified or reverted.
- Commit creation used a path-limited commit:
  - `git commit -m "fix: prefer repo codex skill adapters" --only -- scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py`
- The path-limited commit hook scanned only the two staged implementation files, found zero secrets, passed inventory drift, passed narrative-artifact evidence, passed ruff-format staged-file checks, and produced commit `0d3df1ec0`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the Codex `bridge` skill resolution path is a bridge-function reliability surface.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - skill discovery now prefers the governed in-root Codex adapters over transient home-directory copies.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the approved proposal cited the relevant governing specifications for the change.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps each linked specification to executed verification evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this report carries the project authorization, project, and work item linkage from the approved proposal.
- `SPEC-AUQ-POLICY-ENGINE-001` - the implementation relied on standing owner/project authorization and introduced no new owner-decision surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to in-root startup infrastructure and platform tests.
- `GOV-STANDING-BACKLOG-001` - WI-4364 is a standing-backlog work item under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the implementation applies prefer-canonical/report-fallback discipline to Codex skill resolution.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - resolution preference is anchored to artifact-backed in-root adapters.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - skill discovery now follows the in-root adapter lifecycle before falling back to home-directory surfaces.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - standing authorization for small reliability/defect fixes.
- `DELIB-20265457` - owner AUQ authorizing the open `PROJECT-GTKB-RELIABILITY-FIXES` proposal batch.
- No new owner decision was required during implementation.

## Prior Deliberations

- `bridge/gtkb-codex-skill-path-prefers-repo-local-adapters-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-codex-skill-path-prefers-repo-local-adapters-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `DELIB-20265446` - prior Codex skill adapter packaging context.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing reliability fast-lane direction for this class of defect fix.
- `DELIB-20265457` - owner AUQ authorizing the reliability-fixes proposal batch.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation was selected from live latest `GO`; claim and implementation-start authorization succeeded; post-implementation report filed as the next numbered bridge version through the helper path. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `test_codex_skill_discovery_prefers_in_root_adapter_over_home` verifies the in-root Codex adapter wins over a home-directory copy. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward all approved proposal specification links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short` executed the full startup self-initialization test file after formatting: `76 passed in 142.06s`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Project authorization, project, and work item metadata are present in this report and match the implementation-start packet. |
| `SPEC-AUQ-POLICY-ENGINE-001` | No AUQ behavior changed; implementation proceeded under existing PAUTH and GO evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed files are inside `E:\GT-KB`: `scripts/session_self_initialization.py` and `platform_tests/scripts/test_session_self_initialization.py`; no `applications/` or out-of-root paths were touched. |
| `GOV-STANDING-BACKLOG-001` | Live backlog query before selection showed WI-4364 as an open P2 defect; this report names WI-4364 and the reliability-fixes project. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `test_codex_skill_home_only_resolution_reported_as_fallback` verifies home-only Codex skill resolution is visible through startup model `codex_skill_fallbacks`. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `_resolved_codex_skill_files` records resolved skill paths from artifact roots, not whichever duplicate is encountered last. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `test_default_invocation_does_not_scan_home_directory_for_skills_or_plugins` also asserts `_codex_skill_fallbacks` is empty without calling `Path.home()` in the default branch. |

## Commands Run

```text
python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short
python -m ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py
python -m ruff format --check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py
python -m ruff format scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py
python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short
python -m ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py
python -m ruff format --check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py
```

## Observed Results

- First full startup self-initialization run before formatting: `76 passed in 148.32s`.
- Initial ruff check: `All checks passed!`
- Initial ruff format check requested reformatting of `scripts/session_self_initialization.py`.
- Formatter result: `1 file reformatted, 1 file left unchanged`.
- Final ruff check: `All checks passed!`
- Final ruff format check: `2 files already formatted`.
- Final full startup self-initialization run after formatting: `76 passed in 142.06s`.

## Files Changed

- `scripts/session_self_initialization.py`
- `platform_tests/scripts/test_session_self_initialization.py`

## Commit

- `0d3df1ec0` - `fix: prefer repo codex skill adapters`

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: the diff repairs Codex skill-resolution fallback behavior and adds focused regression coverage; it does not add a new public CLI or external API surface.

## Acceptance Criteria Status

- [x] With opt-in discovery active, in-root `.codex/skills` adapters are included and preferred over home-directory copies of the same skill name.
- [x] Codex skills that resolve only from home-directory `.codex/skills` are surfaced in startup model `codex_skill_fallbacks`.
- [x] Default behavior remains root-contained: no home-directory scan, no `Path.home()` call, empty fallback list.
- [x] Full targeted pytest passes; `ruff check` and `ruff format --check` are clean on both changed files.

## Risk And Rollback

Residual risk is low: the implementation is confined to startup skill discovery and tests. Rollback is to revert commit `0d3df1ec0`; no migration, schema, or configuration change is involved.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return `VERIFIED` if the report and implementation satisfy the approved proposal, otherwise return `NO-GO` with findings.
