NEW

# GT-KB Bridge Implementation Report - gtkb-cli-list-subset-filters - 003

bridge_kind: implementation_report
Document: gtkb-cli-list-subset-filters
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-cli-list-subset-filters-002.md
Approved proposal: bridge/gtkb-cli-list-subset-filters-001.md
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-CLI-SUBSET-FILTERS-WI-4220
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-4220
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e8466-acc1-7923-b828-0ef7ab4a7758
author_model: GPT-5 Codex
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop app; Prime Builder role; local workspace E:\GT-KB
Recommended commit type: feat

## Implementation Claim

Implemented read-only subset controls for the MemBase-backed list surfaces named in `WI-4220`.

`gt projects list` now supports:

- `--limit N`
- repeatable `--id PROJECT-ID`
- `--status STATUS`
- repeatable `--contains TERM`

`gt backlog list` now supports:

- repeatable `--id WI-ID`
- `--project PROJECT`
- `--subproject SUBPROJECT`
- repeatable `--priority PRIORITY`
- repeatable `--resolution-status STATUS`
- repeatable `--stage STAGE`
- repeatable `--origin ORIGIN`
- repeatable `--component COMPONENT`
- repeatable `--contains TERM`
- `--limit N`

The existing JSON output shape remains a filtered list. Explicit project IDs can return terminal projects without `--all`; explicit work item IDs and explicit `--resolution-status` filters can return terminal work items without `--all`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

- 2026-06-01 owner directive: `The CLI should allow specification of a subset, rather than force direct SQLite queries.`
- `DELIB-S385-CLI-SUBSET-FILTERS-AUTHORIZATION` records authorization.
- `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-CLI-SUBSET-FILTERS-WI-4220` is the active project authorization.
- No additional owner decision was required during implementation.

## Prior Deliberations

- `bridge/gtkb-cli-list-subset-filters-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-cli-list-subset-filters-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `DELIB-S385-CLI-SUBSET-FILTERS-AUTHORIZATION` - owner-decision authorization for the CLI subset filters.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-STANDING-BACKLOG-001` | `groundtruth-kb/tests/test_cli_subset_list.py` proves operators can query compact project/backlog subsets through governed MemBase-backed CLI surfaces. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Tests seed MemBase projects/work items and verify subset output without direct operator SQLite queries. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The implementation keeps the owner requirement, work item, proposal, CLI behavior, and tests traceable through this report. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Filters expose lifecycle/status subsets including terminal project/work-item states only when explicitly requested. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Targeted pytest, bridge applicability preflight, clause preflight, ruff lint, and ruff format checks were executed and passed. |

## Commands Run

1. `python scripts/implementation_authorization.py begin --bridge-id gtkb-cli-list-subset-filters`
2. `python -m pytest groundtruth-kb/tests/test_cli_subset_list.py -q --tb=short`
3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-cli-list-subset-filters`
4. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-cli-list-subset-filters`
5. `python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_cli_subset_list.py`
6. `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_cli_subset_list.py`

## Observed Results

- Implementation authorization exited 0 and minted the packet for GO file `bridge/gtkb-cli-list-subset-filters-002.md`.
- Pytest after formatting: `5 passed in 2.54s`.
- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- Clause preflight: exit 0, evidence gaps in must-apply clauses: 0, blocking gaps: 0.
- Ruff check: `All checks passed!`.
- Ruff format check: `2 files already formatted`.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/tests/test_cli_subset_list.py`

Unrelated pre-existing dirty worktree files were not modified for this slice and are intentionally excluded from this implementation claim.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Justification: this adds new read-only CLI subset/filter capabilities plus targeted tests.

## Acceptance Criteria Status

- [x] `gt projects list --limit` returns bounded project subsets in existing sort order.
- [x] `gt projects list --id` can return a terminal project without `--all`.
- [x] `gt projects list --status` and repeatable `--contains` are implemented.
- [x] `gt backlog list --id` can return a terminal work item without `--all`.
- [x] `gt backlog list --resolution-status` can include terminal rows without `--all`.
- [x] `gt backlog list` metadata/text filters return compact JSON subsets.
- [x] Existing JSON output shape remains a filtered list.
- [x] No schema changes or mutating commands were added.

## Risk And Rollback

Residual risk: `--contains` is intentionally simple case-insensitive substring matching across selected text fields; if future operators need field-specific text search, that should be a separate discoverability enhancement.

Rollback: remove the new list-filter helper functions and Click options from `groundtruth-kb/src/groundtruth_kb/cli.py`, and remove `groundtruth-kb/tests/test_cli_subset_list.py`.

## Loyal Opposition Asks

1. Verify that subset listing goes through the MemBase-backed `gt projects list` and `gt backlog list` surfaces rather than requiring operator-side SQLite queries.
2. Verify that explicit terminal-subset behavior satisfies the owner directive.
3. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
