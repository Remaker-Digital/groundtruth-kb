NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-2026-06-03-deferred-authority-parser-followup
author_model: GPT-5 Codex
author_model_version: 2026-06-03 runtime
author_model_configuration: Codex Desktop automation keep-working
author_metadata_source: explicit Codex proposal metadata

# Implementation Proposal - DEFERRED Implementation-Start Parser Follow-Up

bridge_kind: prime_proposal
Document: gtkb-deferred-authority-implementation-start-parser-followup
Version: 001
Recommended commit type: `fix:`
Date: 2026-06-03 UTC

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-GOV-008

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py"]

## Implementation Claim

Authorize the narrow parser and test correction required by `bridge/gtkb-deferred-authority-protocol-alignment-009.md`. The parent DEFERRED alignment report cannot be verified while `scripts/implementation_authorization.py` can skip a latest indexed `DEFERRED` row and treat an older `GO` as implementation authority.

This proposal does not reopen broad DEFERRED semantics. It only adds `DEFERRED` to the implementation-start authority parser's indexed status vocabulary and adds focused fail-closed tests for latest `DEFERRED` above older `GO`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` is canonical queue state and implementation-start authorization must read latest status correctly.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links governing specifications before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map this parser fix to executed tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - `DEFERRED` is an explicit artifact lifecycle status whose non-actionability must be preserved.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decisions and bridge lifecycle state must remain durable and auditable.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation must align source, tests, and bridge evidence with accepted lifecycle semantics.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `AGENTS.md` Mandatory Project Root Boundary - all live GT-KB authority and verification files remain inside `E:\GT-KB`.
- `bridge/gtkb-deferred-authority-protocol-alignment-009.md` - Loyal Opposition NO-GO requiring this parser follow-up before parent verification.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-VERSIONED-DEFERRED-FILE` - owner decision that indexed `DEFERRED` lines point to versioned bridge files.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-DEFERRED-ONLY-NO-SLUG-MUTE` - owner decision to use indexed `DEFERRED`, not a sidecar mute registry.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-OWNER-ONLY-DEFERRAL-AUTHORITY` - owner-only set/clear authority makes fail-closed parsing material.

## Prior Deliberations

- `DELIB-20260602-GLOSSARY-CLI-SCAN-VERSIONED-DEFERRED-FILE`
- `DELIB-20260602-GLOSSARY-CLI-SCAN-DEFERRED-ONLY-NO-SLUG-MUTE`
- `DELIB-20260602-GLOSSARY-CLI-SCAN-OWNER-ONLY-DEFERRAL-AUTHORITY`
- `bridge/gtkb-bridge-dispatcher-deferral-enforcement-repair-006.md`
- `bridge/gtkb-deferred-authority-protocol-alignment-009.md`

## Owner Decisions / Input

No new owner decision is required. The owner already selected indexed, versioned `DEFERRED` status with owner-only set/clear authority. This proposal implements the missing parser propagation needed for that decision to remain safe at implementation-start.

## Requirement Sufficiency

Existing requirements sufficient.

The owner decisions and bridge finding cited above are sufficient for this narrow parser and test correction. No new requirement or policy choice is introduced.

## Findings Addressed

### FINDING-P1-001 - Implementation-start bridge parser still omits DEFERRED

Response plan: update both active status-line regexes in `scripts/implementation_authorization.py` to recognize `DEFERRED` as an indexed bridge status. Add tests proving that `parse_bridge_index()` records latest `DEFERRED`, per-bridge validation enforces matching filenames for `DEFERRED`, authorization creation fails closed when latest `DEFERRED` sits above older `GO`, and implementation-start blocks protected edits when a packet's bridge becomes latest `DEFERRED`.

## Proposed Implementation Plan

1. Add `DEFERRED` to the two status-line regexes used by `parse_bridge_index()` and `_validate_bridge_index_for()`.
2. Add focused parser and authorization tests in `platform_tests/scripts/test_implementation_authorization.py`.
3. Add or extend focused start-gate coverage in `platform_tests/scripts/test_implementation_start_gate.py`.
4. Do not change owner-decision authority, bridge writer behavior, deferral set/clear commands, templates, rule files, MemBase rows, or unrelated bridge status semantics.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Avoid credentials and local secret values. | Staged secret scan. | |
| CQ-PATHS-001 | Yes | Keep all live files under `E:\GT-KB`. | Diff path review. | |
| CQ-COMPLEXITY-001 | Yes | Keep changes to parser vocabulary and focused tests. | Diff review and targeted pytest. | |
| CQ-CONSTANTS-001 | Yes | Preserve existing parser style unless a local status constant exists. | Targeted parser tests. | |
| CQ-SECURITY-001 | Yes | Fail closed when latest `DEFERRED` blocks implementation-start. | Authorization and start-gate tests. | |
| CQ-DOCS-001 | N/A |  |  | Parser and test change only. |
| CQ-TESTS-001 | Yes | Add parser, authorization, and start-gate regressions. | Targeted pytest. | |
| CQ-LOGGING-001 | N/A |  |  | No logging surface change. |
| CQ-VERIFICATION-001 | Yes | Implementation report must include command evidence and spec-to-test mapping. | Bridge report review. | |

## Specification-Derived Verification Plan

Run focused authorization and start-gate tests:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_implementation_authorization.py platform_tests\scripts\test_implementation_start_gate.py -q --tb=short
```

Run targeted quality checks:

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\implementation_authorization.py platform_tests\scripts\test_implementation_authorization.py platform_tests\scripts\test_implementation_start_gate.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\implementation_authorization.py platform_tests\scripts\test_implementation_authorization.py platform_tests\scripts\test_implementation_start_gate.py
```

Run bridge and staged safety checks before commit:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-deferred-authority-implementation-start-parser-followup
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-deferred-authority-implementation-start-parser-followup
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb secrets scan --staged --redacted --fail-on verified-provider
python scripts\check_dev_environment_inventory_drift.py --staged --allow-review-evidence
python scripts\check_narrative_artifact_evidence.py --staged
python scripts\check_ruff_format.py --staged
git diff --cached --check
```

## Acceptance Criteria

- `scripts/implementation_authorization.py` recognizes indexed `DEFERRED` rows in both parse and per-bridge validation paths.
- Latest `DEFERRED` above older `GO` prevents new implementation authorization packet creation.
- A previously issued packet fails validation after its bridge becomes latest `DEFERRED`.
- The implementation-start gate blocks protected edits when current bridge authority is latest `DEFERRED`.
- No behavior changes are made outside the three target paths.

## Risk And Rollback

Risk: adding `DEFERRED` to parser vocabulary may surface existing deferred threads that were previously skipped. That is intended fail-closed behavior.

Risk: tests may expose more duplicated status regexes. If they are active implementation-start authority surfaces inside target paths, fix them in this slice; otherwise report them as follow-up.

Rollback: revert the implementation commit. The change is parser and test only and does not mutate MemBase, external systems, or owner-decision records.
