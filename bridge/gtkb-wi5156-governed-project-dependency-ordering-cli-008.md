REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6f8b-9fd7-7142-93a8-5696dca44d85
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript override ::init gtkb pb; WI-5156 implementation-report revision after NO-GO

# Implementation Report (REVISED) - WI-5156 governed project dependency ordering CLI

bridge_kind: implementation_report
Document: gtkb-wi5156-governed-project-dependency-ordering-cli
Version: 008
Date: 2026-07-18 UTC
Responds to NO-GO: bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-007.md
Responds to implementation report: bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-006.md
Responds to GO: bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-005.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5156
Recommended commit type: feat:

## Revision Scope

This REVISED report carries forward the complete WI-5156 implementation claim from version 006 and resolves the single blocking finding in version 007. No source, test, generated adapter, registry, MemBase, dispatcher configuration, or Git-history mutation was made after the NO-GO. The revision changes only the finalization contract so a VERIFIED commit cannot capture unrelated skill-projection changes that currently share four WI-5156 target files.

The dependency-ordering implementation remains the same implementation reviewed in version 007: Loyal Opposition independently re-ran the behavior suites, projection checks, ruff gates, evaluator, authorization evidence, and source-diff spot checks, and found no defect in the dependency-ordering source or tests. The only blocker was commit-scope safety for shared projection files.

## Resolution Of NO-GO@-007

Version 007 identified that four WI-5156 target files had whole-file hashes that no longer matched the version 006 report because unrelated skill-projection changes were present in the same files:

- `.codex/skills/MANIFEST.json`
- `.agent/skills/MANIFEST.json`
- `.api-harness/skills/MANIFEST.json`
- `config/agent-control/harness-capability-registry.toml`

This report removes the unsafe whole-file finalization request for those four files while preserving WI-5156's implementation claim. Loyal Opposition verification should finalize WI-5156 by one of these scoped paths:

1. If the sibling skill-projection changes have landed before verification, re-diff the four shared files and proceed only if the remaining delta from `HEAD` in each shared file is the WI-5156 `projects` entry.
2. If sibling changes are still dirty, use hunk-scoped finalization for the four shared files, including only the WI-5156 `projects` entry/hashes and excluding all unrelated entries. The other eleven WI-5156 target files may be whole-file included if their current diff remains WI-5156-only.

The WI-5156 hunks in the shared projection files are the `skill.projects` / `projects` entries changing the canonical projects skill hash from `b35a7e3cd6c2b4bd3976c15a2b0f78ec37b4663fbe2d5063047c77daf0c778c8` to `70d646b9b957ad00d39078328bd9aa8b069d503c85b0d40361352c82966f8dde`, plus the matching projects description update where that manifest includes descriptions.

The unrelated same-file entries observed during this revision are not claimed by WI-5156 and must not be included in a WI-5156 terminal commit: `lo-opportunity-radar`, `codex-report` / `loyal-opposition-report`, `kb-session-wrap`, `loyal-opposition-hygiene-assessment`, `gtkb-hygiene-reclaim`, and `managed-skill-adoption-review`.

## Specification Links

- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

- `DELIB-202666274` authorizes the bounded Assurance project scope carried by the active PAUTH.
- The owner-directed dispatcher configuration/troubleshooter hold remains preserved. This revision changed no dispatcher configuration.
- The owner-directed canonical-reference boundary remains preserved. This report relies on MemBase records, Deliberation Archive records, numbered bridge artifacts, governed source, and governed tests only.

## Prior Deliberations

- `DELIB-202666274`
- `DELIB-20260710-GTKB-MODERNIZATION-PROJECT-DEPENDENCY-ORDERING-DCL-APPROVAL`
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-FORMAL-LANGUAGE-DRAFT`
- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST`
- `DELIB-202666105` - prior bridge precedent for sequencing shared target files until predecessor verification/cleanliness is satisfied.
- `DELIB-202666301` - prior bridge precedent for exact hunk/path containment when a later thread depends on inherited or shared dirty paths.
- `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-004.md`
- `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-005.md`
- `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-006.md`
- `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-007.md`

## Specification-Derived Verification

| Requirement | Executed verification | Observed result |
| --- | --- | --- |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` PROJECT-DEP-A1/A2 | `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_project_dependency_ordering.py platform_tests\scripts\test_projects_cli.py platform_tests\scripts\test_projects_skill_adapter.py -q --tb=short`; isolated evaluator | Focused command: `31 passed`; evaluator: PASS for `PROJECT-DEP-A1` through `PROJECT-DEP-A5` |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` PROJECT-DEP-A3/A4/A5 | same focused command plus `groundtruth-kb\.venv\Scripts\python.exe scripts\check_project_dependency_ordering.py --json` | exact membership, readiness, non-authority, and modernization projection assertions all PASS |
| Cross-harness parity specs | `generate_codex_skill_adapters.py --check --update-registry`; `generate_antigravity_skill_adapters.py --check --update-registry`; `generate_api_skill_adapters.py --check` | Codex PASS (44 adapters current); Antigravity PASS (44 adapters current); API PASS (44 adapters current) |
| Code-quality gates | `ruff check` and `ruff format --check` on the six Python implementation/test targets | `All checks passed!`; `6 files already formatted` |
| Commit-scope safety | `git diff --check` on the fifteen WI-5156 targets plus manual diff review of shared projection files | exit 0 with line-ending warnings only; shared files contain separable WI-5156 `projects` hunks plus unrelated sibling skill entries that must be excluded from WI-5156 finalization |
| Project lifecycle adjacency | isolated `test_project_artifacts.py`, `test_projects_remove_item.py`, and `test_project_authorization.py` commands | `34 passed`; `17 passed`; `10 passed` |
| Live production dependency validation | `groundtruth-kb\.venv\Scripts\gt.exe projects dependencies validate --json` | exited 1 on the same pre-existing stale role-enhancement edge; WI-5156 evaluator remains PASS and version 007 already classified this as pre-existing external state |

The combined process `pytest groundtruth-kb\tests\test_project_artifacts.py groundtruth-kb\tests\test_projects_remove_item.py platform_tests\scripts\test_project_authorization.py -q --tb=short` reproduced the known cross-file state leakage documented in version 007: `test_projects_remove_item.py::test_cli_remove_item_invokes_service` failed only after `test_project_artifacts.py` ran first. Each file passes in isolation, matching the established WI-5156 verification methodology.

## Pre-Filing Candidate Preflights

- Applicability preflight against this candidate content: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; `blocking_errors: []`.
- Mandatory clause preflight against this candidate content: clauses evaluated `5`; `must_apply: 3`; evidence gaps in must-apply clauses `0`; blocking gaps `0`; exit `0`.

## Commands Executed For This Revision

- `groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\revise_bridge.py plan gtkb-wi5156-governed-project-dependency-ordering-cli`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5156-governed-project-dependency-ordering-cli`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5156-governed-project-dependency-ordering-cli`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_project_dependency_ordering.py platform_tests\scripts\test_projects_cli.py platform_tests\scripts\test_projects_skill_adapter.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\check_project_dependency_ordering.py --json`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\generate_codex_skill_adapters.py --check --update-registry`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\generate_antigravity_skill_adapters.py --check --update-registry`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\generate_api_skill_adapters.py --check`
- `groundtruth-kb\.venv\Scripts\gt.exe projects dependencies validate --json`
- `groundtruth-kb\.venv\Scripts\ruff.exe check groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py scripts\check_project_dependency_ordering.py groundtruth-kb\tests\test_project_dependency_ordering.py platform_tests\scripts\test_projects_cli.py`
- `groundtruth-kb\.venv\Scripts\ruff.exe format --check groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py scripts\check_project_dependency_ordering.py groundtruth-kb\tests\test_project_dependency_ordering.py platform_tests\scripts\test_projects_cli.py`
- `git diff --check -- <fifteen WI-5156 targets>`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_project_artifacts.py groundtruth-kb\tests\test_projects_remove_item.py platform_tests\scripts\test_project_authorization.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_projects_remove_item.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_project_artifacts.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_project_authorization.py -q --tb=short`

## Finalization Scope

The expected WI-5156 commit scope remains the fifteen target files listed in version 006, but the four shared projection files must be finalized by exact hunk isolation unless sibling skill-projection changes have already landed and the reviewer re-confirms a WI-5156-only diff:

- whole-file eligible if still WI-5156-only: `groundtruth-kb/src/groundtruth_kb/db.py`, `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `scripts/check_project_dependency_ordering.py`, `groundtruth-kb/tests/test_project_dependency_ordering.py`, `platform_tests/scripts/test_projects_cli.py`, `.claude/skills/projects/SKILL.md`, `.codex/skills/projects/SKILL.md`, `.agent/skills/projects/SKILL.md`, `.cursor/skills/projects/SKILL.md`, `.api-harness/skills/projects/SKILL.md`.
- hunk-scoped unless re-confirmed clean: `.codex/skills/MANIFEST.json`, `.agent/skills/MANIFEST.json`, `.api-harness/skills/MANIFEST.json`, `config/agent-control/harness-capability-registry.toml`.

## Acceptance Criteria Status

- PASS: canonical dependency direction and complete append-only lifecycle are exposed through the governed `gt projects dependencies` CLI.
- PASS: invalid edges, cycles, duplicates, lifecycle transitions, and transaction failures append no affected version.
- PASS: project membership reorder is exact-set, version-revalidated, and all-or-nothing.
- PASS: readiness is complete and blocks only the declared gate without granting implementation authority.
- PASS: the isolated evaluator reports exactly five current outer assertions, all PASS.
- PASS: all canonical and generated project skill surfaces are current.
- PASS: finalization guidance now prevents WI-5156 from bundling unrelated sibling skill-projection changes.

## Risk / Rollback

Risk is now limited to terminal commit construction over shared projection files. The source/test implementation has already been independently corroborated. Rollback remains a scoped revert of the fifteen WI-5156 target files and their bridge/report artifacts; numbered bridge audit files are append-only and must not be deleted.
