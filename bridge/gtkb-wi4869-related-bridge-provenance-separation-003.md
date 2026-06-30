NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f19c4-f49d-7283-8c0c-20fe4ec6fb98
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder session; approval_policy=never; filesystem=danger-full-access; owner init ::init gtkb pb
author_metadata_source: explicit implementation-report content

# GT-KB Bridge Implementation Report - gtkb-wi4869-related-bridge-provenance-separation - 003

bridge_kind: implementation_report
Document: gtkb-wi4869-related-bridge-provenance-separation
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4869-related-bridge-provenance-separation-002.md
Approved proposal: bridge/gtkb-wi4869-related-bridge-provenance-separation-001.md
Project: PROJECT-BACKLOG-TRIAGE-AND-HYGIENE
Work Item: WI-4869
Project Authorization: PAUTH-PROJECT-BACKLOG-TRIAGE-AND-HYGIENE-WI-4869-BRIDGE-LINK-RECONCILIATION
Implementation-start authorization: sha256:d8ab4d66b59e1057294fd2ca9591c0a516019e5121bbd04d043b7cad59937466
Recommended commit type: feat

## Implementation Claim

Implemented the approved WI-4869 separation between advisory/source provenance and implementation bridge linkage.

Bridge ADVISORY routing now stages the advisory bridge slug as candidate provenance (`provenance_bridge_thread`) instead of putting it in `related_bridge_threads`. Candidate promotion now writes `related_bridge_threads` into a work item only when the candidate explicitly marks that field as `related_bridge_threads_role = "implementation"`. Provenance-only bridge slugs remain traceable through the staged candidate event, `source_key`, `source_deliberation_query`, and `related_deliberation_ids`, but they no longer become implementation links that the verified-backlog reconciler must inspect.

The verified-backlog reconciler code already had the required canonical guard: mechanical resolution depends on canonical bridge `Work Item: WI-...` metadata and does not infer implementation linkage from prose or unrelated provenance fields. This implementation preserves that behavior and adds a focused regression proving `related_deliberation_ids` bridge provenance does not create a reconciliation candidate.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

- `DELIB-20266592` - active project authorization evidence for WI-4869.
- `DELIB-20260630-PROJECT-BTH-PB-AUTOPROCESS-APPROVAL` - owner authorization for Codex Prime Builder to process all active child work items in this project when governance gates pass.
- No new owner decision was required during implementation.

## Prior Deliberations

- `DELIB-20266206` - owner reconciliation decision that repaired the previously affected related_bridge_threads links and preserved recoverability from append-only history.
- `bridge/gtkb-wi4869-related-bridge-provenance-separation-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4869-related-bridge-provenance-separation-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-STANDING-BACKLOG-001` | `python -m pytest platform_tests/scripts/test_advisory_backlog_router.py platform_tests/scripts/test_advisory_candidate_promote.py platform_tests/scripts/test_bridge_verified_backlog_reconciler.py -q --tb=short` - PASS, 50 passed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Added tests covering bridge advisory provenance staging, promotion without related_bridge_threads, and reconciler non-candidacy for provenance-only bridge slugs; command above passed. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Implementation-start packet validated active project authorization, project, work item, GO file, and target paths before edits. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4869-related-bridge-provenance-separation` - PASS; `missing_required_specs: []`, `missing_advisory_specs: []`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Work intent claim acquired by this Prime Builder session; implementation-start authorization packet created; post-implementation report filed through helper-mediated bridge path. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All changed files are in-root under `E:\GT-KB` and within approved target paths. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Reconciler hook test updated to verify the current Codex batch-runner indirection still contains `scripts/bridge_verified_backlog_reconciler.py --apply --quiet`; focused suite passed. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `SPEC-AUQ-POLICY-ENGINE-001` | Candidate event and promotion tests prove owner-approved advisory promotion preserves provenance while avoiding false implementation linkage. |

## Commands Run

```text
python scripts/bridge_claim_cli.py claim gtkb-wi4869-related-bridge-provenance-separation --ttl-seconds 7200 --project-root E:\GT-KB
python scripts/implementation_authorization.py --project-root E:\GT-KB begin --bridge-id gtkb-wi4869-related-bridge-provenance-separation --expires-minutes 120
python -m pytest platform_tests/scripts/test_advisory_backlog_router.py platform_tests/scripts/test_advisory_candidate_promote.py platform_tests/scripts/test_bridge_verified_backlog_reconciler.py -q --tb=short
python -m ruff check scripts/advisory_backlog_router.py scripts/hygiene/advisory_candidate_promote.py scripts/bridge_verified_backlog_reconciler.py platform_tests/scripts/test_advisory_backlog_router.py platform_tests/scripts/test_advisory_candidate_promote.py platform_tests/scripts/test_bridge_verified_backlog_reconciler.py
python -m ruff format --check scripts/advisory_backlog_router.py scripts/hygiene/advisory_candidate_promote.py scripts/bridge_verified_backlog_reconciler.py platform_tests/scripts/test_advisory_backlog_router.py platform_tests/scripts/test_advisory_candidate_promote.py platform_tests/scripts/test_bridge_verified_backlog_reconciler.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4869-related-bridge-provenance-separation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4869-related-bridge-provenance-separation
```

## Observed Results

- Work-intent claim: PASS, acquired by session `019f19c4-f49d-7283-8c0c-20fe4ec6fb98` through `2026-06-30T20:46:36Z`.
- Implementation authorization: PASS, packet `sha256:d8ab4d66b59e1057294fd2ca9591c0a516019e5121bbd04d043b7cad59937466`, active PAUTH `PAUTH-PROJECT-BACKLOG-TRIAGE-AND-HYGIENE-WI-4869-BRIDGE-LINK-RECONCILIATION`.
- Pytest: PASS, `50 passed in 21.09s`.
- Ruff check: PASS, `All checks passed!`.
- Ruff format check: PASS, `6 files already formatted`.
- Applicability preflight: PASS, `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- Clause preflight: PASS, exit 0, `Evidence gaps in must_apply clauses: 0`, `Blocking gaps (gate-failing): 0`.

## Files Changed

- `scripts/advisory_backlog_router.py`
- `scripts/hygiene/advisory_candidate_promote.py`
- `platform_tests/scripts/test_advisory_backlog_router.py`
- `platform_tests/scripts/test_advisory_candidate_promote.py`
- `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py`

No change was required in `scripts/bridge_verified_backlog_reconciler.py`; the existing canonical Work Item metadata guard already satisfied the approved reconciler behavior, and the new regression test locks that in.

## Recommended Commit Type

- Recommended commit type: `feat`
- Rationale: this changes advisory promotion behavior and adds regression coverage for provenance/linkage separation.

```text
 .../scripts/test_advisory_backlog_router.py        |  3 ++
 .../scripts/test_advisory_candidate_promote.py     | 39 +++++++++++++++++++--
 .../test_bridge_verified_backlog_reconciler.py     | 40 ++++++++++++++++++++--
 scripts/advisory_backlog_router.py                 |  5 ++-
 scripts/hygiene/advisory_candidate_promote.py      | 15 +++++++-
 5 files changed, 96 insertions(+), 6 deletions(-)
```

## Acceptance Criteria Status

- Promoted bridge-advisory candidates remain traceable to their source advisory but their resulting work_items rows do not carry advisory slugs in `related_bridge_threads`: PASS. Bridge advisory candidates carry `provenance_bridge_thread`; promotion preserves that provenance and writes `related_bridge_threads = None` unless the role is explicitly `implementation`.
- Existing valid implementation-link behavior is preserved: PASS. Promotion has an explicit implementation-link path, and the verified-backlog reconciler test suite still passes all existing canonical metadata, umbrella, live-status, and parent-evidence cases.
- No direct SQLite/backlog bulk mutation is performed by the implementation: PASS. The router still stages append-only candidate events, and the promotion tool still uses `KnowledgeDB.insert_work_item` as before.

## Risk And Rollback

Residual risk is low. Existing legacy staged candidates that already carry bridge advisory slugs in `related_bridge_threads` without an explicit `related_bridge_threads_role = "implementation"` will no longer promote those slugs as implementation links. That is intentional for WI-4869 because unmarked advisory bridge slugs are provenance, not implementation linkage.

Rollback is a revert of the five changed source/test files. Bridge audit files remain append-only and must not be deleted.

## Loyal Opposition Asks

1. Verify that bridge ADVISORY provenance remains traceable but no longer populates `related_bridge_threads` on promoted work items.
2. Verify that the existing reconciler canonical Work Item metadata behavior remains intact.
3. Return VERIFIED if the implementation and evidence satisfy WI-4869, otherwise return NO-GO with findings.
