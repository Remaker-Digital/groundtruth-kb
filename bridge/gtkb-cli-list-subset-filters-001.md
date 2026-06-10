NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019e8466-acc1-7923-b828-0ef7ab4a7758
author_model: GPT-5 Codex
author_model_version: 2026-06-01
author_model_configuration: Codex desktop Prime Builder; approval_policy=never; sandbox=danger-full-access
author_metadata_source: explicit-codex-helper-call

bridge_kind: implementation_report
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-CLI-SUBSET-FILTERS-WI-4220
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-4220
target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_cli_subset_list.py"]

# GT-KB CLI List Subset Filters

## Summary

Add subset controls to the MemBase-backed CLI list surfaces so project and backlog rollups do not require direct SQLite queries or parsing full CLI JSON output. The immediate owner requirement is: the CLI should allow specification of a subset, rather than force direct SQLite queries.

## Owner Input

- 2026-06-01 owner directive: `The CLI should allow specification of a subset, rather than force direct SQLite queries.`
- Captured as MemBase work item `WI-4220` under `PROJECT-GTKB-DETERMINISTIC-SERVICES-001` / Discoverability before this proposal was filed.
- Authorization captured as `DELIB-S385-CLI-SUBSET-FILTERS-AUTHORIZATION` and `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-CLI-SUBSET-FILTERS-WI-4220`.

## Requirement Sufficiency

Existing requirements sufficient.

The owner directive plus `WI-4220` acceptance summary define the bounded CLI behavior: compact subset reads for project and backlog list output, with JSON preserved for machine consumers. No new formal specification is needed before implementation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation must proceed through live bridge GO before protected source/test changes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal cites governing specifications and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation report must map tests back to these requirements and run them.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner requirement is preserved as `WI-4220` before implementation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - CLI behavior, MemBase row, bridge proposal, tests, and report remain traceable.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - `WI-4220` remains an active candidate/work item until implementation and verification complete.
- `GOV-STANDING-BACKLOG-001` - backlog/project state must be read through governed MemBase-backed surfaces rather than unmanaged side channels.

## Proposed Implementation

1. Extend `gt projects list` with read-only subset options:
   - `--limit N` for top-N project views in existing sort order.
   - repeatable `--id PROJECT-ID` for explicit project subsets.
   - `--status STATUS` and repeatable `--contains TERM` for targeted exploration.
   - preserve existing `--json` output shape as a filtered list.
2. Extend `gt backlog list` with read-only subset options:
   - repeatable `--id WI-ID` for explicit status rollups.
   - `--project`, `--subproject`, repeatable `--priority`, `--resolution-status`, `--stage`, `--origin`, `--component`, and `--contains` filters.
   - `--limit N` for bounded output.
   - preserve explicit-ID and explicit-resolution-status behavior so terminal rows can be requested without forcing direct DB access.
3. Add focused CLI tests using temporary MemBase fixtures:
   - project list `--limit` returns the top subset in existing rank/name order.
   - project list explicit `--id` can return a terminal project.
   - backlog list explicit `--id` can return a terminal work item.
   - backlog list text/metadata filters produce compact JSON subsets.

## Out Of Scope

- No schema changes.
- No mutation commands.
- No project-status rollup redesign.
- No bridge/INDEX writer changes; those remain under `WI-3513`.

## Specification-Derived Verification Plan

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-cli-list-subset-filters` and include the clean result in the post-implementation report.
- `GOV-STANDING-BACKLOG-001` and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: run targeted CLI tests proving subset output uses MemBase-backed `gt projects list` and `gt backlog list` rather than direct SQLite access from the operator path.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: run `python -m pytest groundtruth-kb/tests/test_cli_subset_list.py -q --tb=short` after implementation and report exact results.
- Python code-quality gates: run `ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_cli_subset_list.py` and `ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_cli_subset_list.py` before filing the implementation report.

## Prior Deliberations

_No prior deliberations: this is a narrow owner-directed CLI discoverability gap discovered during live project/work-item rollup; the durable context is the owner directive captured in `WI-4220` plus `DELIB-S385-CLI-SUBSET-FILTERS-AUTHORIZATION`._
