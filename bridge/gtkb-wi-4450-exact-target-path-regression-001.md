NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never
author_metadata_source: Codex Prime Builder session; .gtkb-state/bridge-author-metadata/current.json

bridge_kind: prime_proposal
Document: gtkb-wi-4450-exact-target-path-regression
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4450
target_paths: ["platform_tests/scripts/test_implementation_start_gate.py"]

# WI-4450 Exact Target Path Regression Proposal

## Claim

Add a focused regression test proving an implementation-start authorization packet whose `target_paths` contains a literal exact file path authorizes writes to that exact file path. This resolves WI-4450 by making the currently-passing behavior durable and reviewable without changing production gate code.

## Scope

- Add one test to `platform_tests/scripts/test_implementation_start_gate.py`.
- The test creates a temporary bridge thread with `target_paths: ["config/governance/hygiene-baseline-registry.toml"]`, mints an implementation-start packet, and asserts an `apply_patch` mutation to that exact path is allowed.
- No production source, hook registration, configuration, or database mutation is in implementation scope.

No KB mutation: this implementation changes only the listed test file; the project/work-item metadata above is proposal linkage, not an implementation mutation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation must proceed through the file bridge and remain within the approved `target_paths` envelope.
- `GOV-RELIABILITY-FAST-LANE-001` - the active reliability fast-lane PAUTH covers small reliability fixes for active project members.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal declares concrete specification linkage and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification is the focused regression test plus the adjacent existing authorization/gate tests.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation remains bounded by a GO verdict and implementation-start packet.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing owner-approved reliability fast-lane authorization for small defect/reliability fixes in `PROJECT-GTKB-RELIABILITY-FIXES`.
- `DELIB-20260882` - owner-approved implementation-start gate parser hygiene scope, adjacent to this exact target-path regression surface.
- No contrary prior deliberation was found during current local evidence review; WI-4450 is a targeted regression-coverage closure for behavior that already passes in the current gate.

## Requirement Sufficiency

Existing requirements sufficient.

## Implementation Plan

1. Add `test_exact_file_target_path_authorizes_exact_protected_file` to `platform_tests/scripts/test_implementation_start_gate.py`.
2. Reuse existing `_write_thread`, `_proposal`, `auth`, and `gate` fixtures/helpers where possible.
3. Keep the assertion narrow: a literal exact `config/governance/hygiene-baseline-registry.toml` target path must authorize an `apply_patch` update to the same normalized path.

## Specification-Derived Verification Plan

- `python -m pytest platform_tests/scripts/test_implementation_start_gate.py::test_exact_file_target_path_authorizes_exact_protected_file -q --tb=short`
- `python -m pytest platform_tests/scripts/test_implementation_start_gate.py::test_authorization_accepts_bold_target_paths_metadata platform_tests/scripts/test_implementation_start_gate.py::test_requirement_sufficiency_are_sufficient_allows_gate_authorization platform_tests/scripts/test_implementation_authorization.py::test_create_authorization_packet_accepts_target_paths_heading_proposal -q --tb=short`
- `python -m ruff check platform_tests/scripts/test_implementation_start_gate.py`
- `python -m ruff format --check platform_tests/scripts/test_implementation_start_gate.py`

## Acceptance Criteria

- A regression test fails if exact-file `target_paths` entries stop authorizing the exact same normalized path.
- Existing wildcard and heading-form target-path tests still pass.
- Ruff check and format-check pass for the modified test file.
- The post-implementation report includes command output, exact file changed, and WI-4450 resolution recommendation.

## Conventional Commit Type

`test`
