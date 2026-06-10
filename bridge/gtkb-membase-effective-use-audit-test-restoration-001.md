NEW
author_identity: Prime Builder (Codex)
author_harness_id: A
author_session_context_id: codex-desktop-2026-06-01-gtkb-pb
author_model: GPT-5
author_model_version: codex-session-2026-06-01
author_model_configuration: default-reasoning
author_metadata_source: explicit-codex-session

bridge_kind: prime_proposal
Document: gtkb-membase-effective-use-audit-test-restoration
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-MEMBASE-EFFECTIVE-USE-MEMBASE-EFFECTIVE-USE-BATCH
Project: PROJECT-GTKB-MEMBASE-EFFECTIVE-USE
Work Item: GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY
target_paths: ["platform_tests/scripts/test_membase_effective_use_audit.py"]

# Implementation Proposal - MemBase Effective Use Audit Test Restoration

## Claim

Restore the focused regression test file for `groundtruth_kb.membase_effective_use_audit` and fix the age-filter test expectation discovered during local verification. This is a test-only correction for the already-implemented MemBase effective-use recovery audit module.

## Prior Deliberations

- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` - source owner-directed recovery assessment for MemBase effective-use gaps.
- `DELIB-0874` - artifact-oriented governance context carried by the recovery work item.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - project authorization basis for `PROJECT-GTKB-MEMBASE-EFFECTIVE-USE`.

## Requirement Sufficiency

Existing requirements sufficient. The existing recovery requirements already require verified non-phantom bridge evidence and tests for the recovery surfaces; this proposal restores missing local regression coverage for one verified test surface without adding product behavior or new canonical-artifact semantics.

## Scope

- Add or correct `platform_tests/scripts/test_membase_effective_use_audit.py`.
- Cover `parse_bridge_index`, verified-state mismatch detection, verified-spec suppression, duplicated canonical content detection, deliberation-draft candidate detection, age filtering for scanned-spec lenses, and markdown report writing.
- No source-module changes.
- No bridge/INDEX reconciliation beyond this proposal's normal lifecycle.
- No MemBase project, work-item, or specification mutation.

## Specification Links

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves durable verification evidence for artifact-oriented work.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - uses the file bridge before protected implementation edits.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal carries concrete project/work-item/spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - maps the verified audit behavior to executable regression tests.

## Files Expected To Change

- `platform_tests/scripts/test_membase_effective_use_audit.py`

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---:|---|---|---|
| CQ-SECRETS-001 | Yes | Test fixtures use synthetic bridge/spec IDs only; no credential-shaped fixtures. | Source review + credential scan by bridge helper | n/a |
| CQ-PATHS-001 | Yes | Tests use `tmp_path` and package imports; no absolute host paths. | `python -m pytest platform_tests/scripts/test_membase_effective_use_audit.py -q --tb=short` | n/a |
| CQ-CONSTANTS-001 | Yes | No production constants added; expected strings stay local to focused test assertions. | Source review | n/a |
| CQ-DOCS-001 | N/A | n/a | n/a | No user-facing behavior or API docs change. |
| CQ-COMPLEXITY-001 | Yes | Each test is small and covers one audit lens or writer behavior. | Source review | n/a |
| CQ-TESTS-001 | Yes | The proposal is a test restoration and expands coverage for the existing audit module. | Targeted pytest command above | n/a |
| CQ-LOGGING-001 | N/A | n/a | n/a | Test-only file. |
| CQ-SECURITY-001 | Yes | Tests avoid network/auth surfaces and run entirely inside temp directories. | Source review | n/a |
| CQ-VERIFICATION-001 | Yes | Targeted pytest, focused MemBase recovery pytest group, ruff check, and ruff format check. | Commands in Specification-Derived Verification | n/a |

## Specification-Derived Verification

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: run `python -m pytest platform_tests/scripts/test_membase_effective_use_audit.py -q --tb=short`.
- Recovery audit remains test-covered without source mutation: run `python -m pytest platform_tests/scripts/test_membase_effective_use_audit.py groundtruth-kb/tests/test_intake.py groundtruth-kb/tests/test_spec_intake_helper.py groundtruth-kb/tests/test_spec_event_surfacer.py groundtruth-kb/tests/test_core_spec_intake.py platform_tests/groundtruth_kb/test_spec_auto_backlog.py -q --tb=short`.
- Formatting and lint stay clean: run `python -m ruff check platform_tests/scripts/test_membase_effective_use_audit.py` and `python -m ruff format --check platform_tests/scripts/test_membase_effective_use_audit.py`.

## Risk And Rollback

Risk is low because the change is test-only. If the test proves inconsistent with the existing implementation contract, revise the test rather than changing production code under this bridge. Rollback is deleting the test file before merge if Loyal Opposition finds the restored coverage out of scope.

## Decision Needed From Owner

None. This is test-only restoration under the existing MemBase effective-use recovery authorization.
