NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; transcript-defined ::init gtkb pb; ::open build; approval_policy=never
author_metadata_source: explicit_current_codex_thread_metadata

# WI-5393 Implementation Report: Pytest Recursion Exclusions

bridge_kind: implementation_report
Document: gtkb-wi5393-pytest-recursion-exclusions
Version: 003
Date: 2026-07-16 UTC

Responds to GO: bridge/gtkb-wi5393-pytest-recursion-exclusions-002.md
Approved proposal: bridge/gtkb-wi5393-pytest-recursion-exclusions-001.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5393

target_paths: ["pyproject.toml", "platform_tests/governance/test_platform_tests_rename.py"]

## Implementation Claim

WI-5393 is implemented. The root pytest config now carries the approved recursion exclusions `norecursedirs = [".*", "pytest-tmp-*"]`, preventing default collection from entering hidden runtime state and pytest temporary trees. `platform_tests` remains the canonical default test root.

The implementation adds `test_pyproject_norecursedirs_preserves_platform_collection` to parse `[tool.pytest.ini_options]` and assert that `platform_tests` remains collected, the exact two runtime recursion exclusions are present, and neither `platform_tests` nor the Agent Red test tree is excluded by default.

## Implementation-Start Evidence

- Live bridge state before implementation: latest `GO` at `bridge/gtkb-wi5393-pytest-recursion-exclusions-002.md`.
- Work-intent claim: `python scripts/bridge_claim_cli.py status gtkb-wi5393-pytest-recursion-exclusions` reported claim kind `go_implementation`, session `019f6668-9974-7d72-a456-826f9a67e627`, rowid `31803`, `expired: false`, latest bridge status `GO`.
- Implementation-start packet: `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5393-pytest-recursion-exclusions --session-id 019f6668-9974-7d72-a456-826f9a67e627 --expires-minutes 60` emitted schema version `3`, packet hash `sha256:04c5d1148621f70e891183287099de4240ccb3923fe0b56b6963848a797bea5e`, proposal file `bridge/gtkb-wi5393-pytest-recursion-exclusions-001.md`, GO file `bridge/gtkb-wi5393-pytest-recursion-exclusions-002.md`, and target path globs exactly `pyproject.toml` and `platform_tests/governance/test_platform_tests_rename.py`.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - protected configuration dirt must have exact ownership, review, testing, and finalization rather than aggregate capture.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - collection optimization must not hide platform tests or weaken release evidence.
- `DCL-GTKB-INDEPENDENT-TEST-SUITE-001` - platform-owned tests remain the independent GT-KB acceptance surface.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - the configuration and its effect require deterministic, executable evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project authorization does not waive GO, claim, start, verification, or Git gates.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - live authority is rechecked before protected edits.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - independent GO and VERIFIED are mandatory.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - adopter application tests remain outside the default platform test collection boundary unless explicitly scoped.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requirements are explicitly linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, WI, and exact targets are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - review maps config behavior to executable compatibility evidence.
- `GOV-STANDING-BACKLOG-001` - WI-5393 durably owns the discovered RC blocker.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - candidate, work item, proposal, test, report, verdict, and finalization remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - VERIFIED and physical finalization are separate required lifecycle states.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - docs-review disposition and compatibility evidence are preserved as durable artifacts.

## Owner Decisions / Input

No new owner decision was required. This implementation carries forward `DELIB-202666274` and the approved PAUTH/project/work-item scope. Git staging, commit, push, release, deployment, cleanup, credentials, dispatcher, TAFE, harness routing, roles, and eligibility remain outside this implementation report.

## Prior Deliberations

- `DELIB-202666274` - supplies project-scoped modernization Assurance authority while retaining bridge and mechanical Git gates.
- Owner directive, 2026-07-16 - inventory ownership for all worktree dirt and finalize only independently verified scopes with exact authority.
- `bridge/gtkb-wi5393-pytest-recursion-exclusions-001.md` - approved proposal.
- `bridge/gtkb-wi5393-pytest-recursion-exclusions-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Governing surface | Executed verification evidence | Result |
| --- | --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | `git diff --stat -- pyproject.toml platform_tests/governance/test_platform_tests_rename.py`; `git diff --numstat -- pyproject.toml platform_tests/governance/test_platform_tests_rename.py`; `git diff --check -- pyproject.toml platform_tests/governance/test_platform_tests_rename.py` | Exact two-path diff only; 14 insertions and 1 deletion; whitespace check passed. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | `python -m pytest platform_tests/governance/test_platform_tests_rename.py -q --tb=short`; `python -m pytest --collect-only platform_tests -q --tb=short` | Focused module passed; collect-only found 7,403 platform tests under the canonical root. |
| `DCL-GTKB-INDEPENDENT-TEST-SUITE-001` | Parsed-config regression asserts `platform_tests` remains in `testpaths` and is absent from `norecursedirs` | Independent platform suite remains discoverable by default. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | New parsed TOML assertion verifies `norecursedirs == [".*", "pytest-tmp-*"]` | Configuration effect is executable and exact. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start packet evidence above | PAUTH was necessary evidence but did not replace GO, claim, target bounds, report, or verification. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Live claim and schema-v3 implementation-start packet hash `sha256:04c5d1148621f70e891183287099de4240ccb3923fe0b56b6963848a797bea5e` | Operation-time authority matched the latest GO and exact targets. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Numbered proposal, GO, and report chain plus live report preflights | Filing remains append-only and role-correct. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Parsed-config regression asserts `applications/Agent_Red/tests` remains absent from default `testpaths` and absent from `norecursedirs` | The GT-KB platform test root remains separate from the reference adopter application test tree. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate report preflights listed below | No missing required or advisory specs before filing. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header metadata in proposal, packet, and this report | PAUTH, project, work item, and target paths are machine-readable. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table plus executed test and collect-only evidence | Every linked requirement has executed evidence. |
| `GOV-STANDING-BACKLOG-001` | Work remains tied to WI-5393 | The discovered release-candidate blocker remains durable backlog work, not a hidden tree edit. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Work item, PAUTH, proposal, GO, config hunk, test hunk, and report are linked | Artifact-first repair flow is preserved. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This `NEW` implementation report advances the GO to independent verification without premature terminal closure | Lifecycle state remains explicit. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Docs-review disposition and compatibility evidence are recorded in the bridge chain | Governance evidence is durable. |

## Commands Run

- `python -m pytest platform_tests/governance/test_platform_tests_rename.py -q --tb=short`
- `python -m pytest --collect-only platform_tests -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check pyproject.toml platform_tests/governance/test_platform_tests_rename.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check pyproject.toml platform_tests/governance/test_platform_tests_rename.py`
- `git diff --check -- pyproject.toml platform_tests/governance/test_platform_tests_rename.py`
- `git diff --stat -- pyproject.toml platform_tests/governance/test_platform_tests_rename.py`
- `git diff --numstat -- pyproject.toml platform_tests/governance/test_platform_tests_rename.py`

## Observed Results

- Focused pytest: `4 passed, 2 skipped in 2.01s`.
- Collect-only probe: `7403 tests collected in 12.60s`.
- Ruff lint: `All checks passed!`
- Ruff format: `1 file already formatted`.
- `git diff --check`: exit 0, no whitespace errors.
- Scoped diff stat: `2 files changed, 14 insertions(+), 1 deletion(-)`.
- Scoped numstat: `13  0  platform_tests/governance/test_platform_tests_rename.py`; `1  1  pyproject.toml`.

## Files Changed

- `pyproject.toml` - carries the approved `norecursedirs = [".*", "pytest-tmp-*"]` config hunk and removes one terminal blank line.
- `platform_tests/governance/test_platform_tests_rename.py` - adds the parsed-config regression for runtime recursion exclusions and platform-suite discoverability.
- Bridge audit artifacts in this thread: `bridge/gtkb-wi5393-pytest-recursion-exclusions-001.md`, `bridge/gtkb-wi5393-pytest-recursion-exclusions-002.md`, and this report version `003`.

## Hunk Attribution

The `pyproject.toml` hunk pre-existed this session as the approved candidate configuration dirt described by WI-5393. This session did not broaden it; it verified the exact two exclusion patterns and preserved the one terminal blank-line normalization already present in the diff. The test hunk in `platform_tests/governance/test_platform_tests_rename.py` is this session's implementation work after the live GO, matching claim, and implementation-start packet.

The broad worktree contains unrelated foreign changes, but none are adopted by this report.

## Acceptance Criteria Status

- PASS: root pytest config retains `platform_tests` and the exact two recursion exclusions.
- PASS: focused config test and representative platform collect-only probe pass.
- PASS: no public documentation is affected; this is internal pytest discovery configuration only.
- PASS: exact diff is limited to `pyproject.toml` and `platform_tests/governance/test_platform_tests_rename.py`.
- PENDING LO: independent VERIFIED and mechanical finalization remain required before terminal closure.

## Recommended Commit Type

Recommended commit type: `test:`

Diff-stat justification: the implementation changes pytest configuration plus a regression test for test discovery behavior.

## Pre-Filing Preflight Subsection

Before filing this report, Prime Builder runs:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5393-pytest-recursion-exclusions --content-file .gtkb-state/bridge-impl-reports/drafts/gtkb-wi5393-pytest-recursion-exclusions-003.md --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5393-pytest-recursion-exclusions --content-file .gtkb-state/bridge-impl-reports/drafts/gtkb-wi5393-pytest-recursion-exclusions-003.md`

Observed candidate result: applicability preflight passed with `missing_required_specs: []` and `missing_advisory_specs: []`; clause preflight evaluated 5 clauses, found 3 `must_apply`, found 0 evidence gaps in `must_apply` clauses, and exited 0. The live filed report is rechecked after helper filing.

## Risk And Rollback

Residual risk is overbroad exclusion hiding real tests. The exact patterns, parsed-config assertion, and collect-only evidence constrain that risk. Rollback is a governed two-path hunk revert; bridge files and packet evidence remain append-only audit history.

## Loyal Opposition Asks

1. Verify the two-path implementation against the linked specifications and executed evidence.
2. If satisfied, return `VERIFIED` through the canonical finalizer with exactly the WI-5393 target paths and bridge thread files in the verified path set.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
