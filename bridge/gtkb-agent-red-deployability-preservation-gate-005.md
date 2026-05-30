NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-desktop-2026-05-19-agent-red-deployability-slice1
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: reasoning=medium; collaboration_mode=Default
author_metadata_source: Codex desktop session environment

# Implementation Report - Agent Red Deployability Preservation Gate Slice 1 Partial - 005

bridge_kind: implementation_report
Document: gtkb-agent-red-deployability-preservation-gate
Version: 005
Author: Prime Builder (Codex harness A)
Date: 2026-05-19 UTC
Responds to GO: bridge/gtkb-agent-red-deployability-preservation-gate-004.md
Approved proposal: bridge/gtkb-agent-red-deployability-preservation-gate-003.md
Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH-P0-DEPLOYABILITY-GATE
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: WI-3248
Recommended commit type: feat:

## Implementation Claim

Implemented the approved partial Slice 1 deployability preservation gate in the three authorized target paths:

- `groundtruth-kb/src/groundtruth_kb/adoption/deployability_preservation_gate.py`
- `scripts/adopter_deployability_check.py`
- `platform_tests/scripts/test_adopter_deployability_check.py`

The library now emits a `DeployabilityReport` with `coverage="partial"`, `full_clearance=false`, accurate `covered_specs` and `deferred_specs`, a `partial_clearance_warning`, and four read-only checks: RC-gate dry-run, Python 3.12 declaration, frontend build metadata, and pytest collection. The root CLI exposes `--adopter-root` and `--json`; its help text states this is partial Slice 1 coverage and names all four deferred proofs. No Agent Red repository files or adopter product files were modified.

## Specification Links

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-GTKB-ADOPTION-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `SPEC-DEPLOY-SOURCE-BUILD-001`
- `SPEC-DEPLOY-RC-GATE-PYTHON-3-12-001`
- `SPEC-DEPLOY-CONTAINER-BUILD-001`
- `SPEC-DEPLOY-FRONTEND-BUNDLES-001`
- `SPEC-DEPLOY-WORKFLOW-INPUTS-001`
- `SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001`
- `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`

## Owner Decisions / Input

This implementation carries forward the owner authorization cited in the proposal: `DELIB-S350-BATCH6-P0P1-AUTHORIZATION` authorized WI-3248 under `PROJECT-GTKB-ADOPTER-EXPERIENCE`. No new owner decision was required because this implementation stays within the Loyal Opposition GO and the approved target paths.

## Prior Deliberations

- `DELIB-S350-BATCH6-P0P1-AUTHORIZATION` - owner approval for the remaining P0/P1 work including WI-3248.
- `DELIB-0319` - Agent Red deployability and release-path concern history.
- `DELIB-0327` - artifact-lane and release-path context.
- `bridge/gtkb-agent-red-deployability-preservation-gate-003.md` - approved revised proposal.
- `bridge/gtkb-agent-red-deployability-preservation-gate-004.md` - Loyal Opposition GO authorizing this partial Slice 1 only.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-DEPLOY-RC-GATE-PYTHON-3-12-001` | `test_healthy_adopter_all_pass`, `test_broken_rc_gate_fails`, and `test_missing_python_gate_fails` verify the RC-gate dry-run and Python 3.12 declaration checks. |
| `SPEC-DEPLOY-FRONTEND-BUNDLES-001` | `test_healthy_adopter_all_pass` and `test_no_frontend_skip` verify frontend build metadata PASS and no-frontend SKIP behavior. |
| `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001` | `test_broken_test_suite_collection_fails` verifies pytest collection failures surface as a FAIL freshness signal; full evidence aggregation remains deferred. |
| `SPEC-AUQ-POLICY-ENGINE-001` | `test_cli_exit_code` verifies CLI exit status and `test_cli_json_schema_partial_coverage` verifies JSON output and help text. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The seven named tests execute the proposal's spec-to-test mapping and assert `coverage`, `covered_specs`, `deferred_specs`, and `full_clearance=false`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This report is filed through the bridge implementation-report helper after live INDEX inspection. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md` | Target paths are inside `E:\GT-KB`; implementation did not read or write live Agent Red repository files outside the root. |
| `SPEC-DEPLOY-SOURCE-BUILD-001`, `SPEC-DEPLOY-CONTAINER-BUILD-001`, `SPEC-DEPLOY-WORKFLOW-INPUTS-001`, `SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001` | Explicitly deferred in report schema, CLI help, and tests. This Slice 1 PASS cannot be interpreted as full deployability clearance. |

## Commands Run

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-agent-red-deployability-preservation-gate
python -m pytest platform_tests/scripts/test_adopter_deployability_check.py -v --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/adoption/deployability_preservation_gate.py scripts/adopter_deployability_check.py platform_tests/scripts/test_adopter_deployability_check.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/adoption/deployability_preservation_gate.py scripts/adopter_deployability_check.py platform_tests/scripts/test_adopter_deployability_check.py
python scripts/adopter_deployability_check.py --help
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate
python -m ruff check .
python -m ruff format --check .
```

## Observed Results

- Implementation authorization opened successfully for `gtkb-agent-red-deployability-preservation-gate`; target path globs matched the three approved files.
- `python -m pytest platform_tests/scripts/test_adopter_deployability_check.py -v --tb=short`: 7 passed.
- Targeted `python -m ruff check ...`: All checks passed.
- Targeted `python -m ruff format --check ...`: 3 files already formatted.
- `python scripts/adopter_deployability_check.py --help`: exit 0; help says "Partial Slice 1 coverage only" and lists the deferred `SPEC-DEPLOY-SOURCE-BUILD-001`, `SPEC-DEPLOY-CONTAINER-BUILD-001`, `SPEC-DEPLOY-WORKFLOW-INPUTS-001`, and `SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001` proofs.
- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- Clause preflight: exit 0; 0 blocking gaps.
- Repo-wide `python -m ruff check .`: exit 1 with the existing baseline of 2088 unrelated errors.
- Repo-wide `python -m ruff format --check .`: exit 1 with the existing baseline of 1121 unrelated files requiring formatting.

The repo-wide ruff failures are outside this implementation's approved target paths and were not modified by this work. The scoped implementation files are lint-clean and format-clean.

## Acceptance Criteria Status

- IP-1, IP-2, IP-3 landed: satisfied.
- Seven tests in `platform_tests/scripts/test_adopter_deployability_check.py` PASS: satisfied.
- Library report carries `coverage="partial"` plus accurate covered/deferred specs: satisfied and asserted by tests.
- CLI help states partial Slice 1 and names deferred proofs: satisfied and asserted by tests plus direct `--help` run.
- Both preflights PASS: satisfied.
- Slice 1 PASS cannot be mistaken for full deployability clearance: satisfied by `full_clearance=false`, `partial_clearance_warning`, deferred proof lists, library docstring, CLI help, and tests.
- Repo-wide ruff clean: not satisfied by the existing repository baseline; scoped target paths are clean.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/adoption/deployability_preservation_gate.py` - new partial Slice 1 gate library and report schema.
- `scripts/adopter_deployability_check.py` - new root CLI wrapper.
- `platform_tests/scripts/test_adopter_deployability_check.py` - seven spec-derived tests for library, CLI, JSON schema, and help text.

## Risk And Rollback

Residual risk is limited to false-positive or false-negative classification in the new read-only checks. The schema and CLI deliberately preserve partial-coverage warnings so future sessions cannot use this as full deployability clearance. Rollback is to remove the three new files above; no MemBase rows, Agent Red repository files, or adopter product files were mutated.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the partial Slice 1 implementation satisfies the approved proposal, otherwise return NO-GO with findings.
