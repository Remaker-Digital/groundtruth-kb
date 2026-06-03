NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-2026-06-03-project-membership-inventory-tool-implementation
author_model: GPT-5 Codex
author_model_version: 2026-06-03 runtime
author_model_configuration: Codex Desktop automation keep-working
author_metadata_source: explicit Codex implementation metadata

# Implementation Report - Project Membership Reconciliation Slice 1 Inventory Tool

bridge_kind: implementation_report
Document: gtkb-project-membership-reconciliation-slice-1-inventory-tool
Version: 003
Responds-To: `bridge/gtkb-project-membership-reconciliation-slice-1-inventory-tool-002.md`
Approved proposal: `bridge/gtkb-project-membership-reconciliation-slice-1-inventory-tool-001.md`
Recommended commit type: `chore:`
Date: 2026-06-03 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: GTKB-GOV-004

## Implementation Claim

Implemented the approved read-only inventory/source-test slice.

Added `scripts/inventory_project_membership_reconciliation.py`, a deterministic CLI that opens `groundtruth.db` through a read-only SQLite URI, fresh-reads MemBase current-state views, classifies every non-terminal work item exactly once, and emits JSON or Markdown dry-run inventory output.

Added `platform_tests/scripts/test_inventory_project_membership_reconciliation.py`, a synthetic current-state fixture covering all nine required primary classifications, exactly-once failure handling, JSON/Markdown rendering, output-path behavior, and CLI stdout behavior.

The implementation does not include any apply/mutate mode and does not call project lifecycle mutation services, write to `groundtruth.db`, create/retire/reorder projects, add memberships, retire work items, file owner decisions, or file generated bridge proposals.

## Files Changed

- `scripts/inventory_project_membership_reconciliation.py`
- `platform_tests/scripts/test_inventory_project_membership_reconciliation.py`

Runtime smoke artifacts were written under `.gtkb-state/project-membership-reconciliation/` and are not committed source artifacts.

Bridge filing evidence: the implementation-report helper inserted `NEW: bridge/gtkb-project-membership-reconciliation-slice-1-inventory-tool-003.md` at the top of this document's `bridge/INDEX.md` entry without deleting or rewriting prior versions.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - backlog/project visibility and bulk-operation discipline.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` - MemBase is the canonical backlog/project data authority.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` - backlog/project data must use governed schema/current-state semantics.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project-scoped implementation authorization applies.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - allowed mutation classes match the implementation: `cli_extension` and `test_addition`.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization did not bypass bridge review or verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this report carries forward Project Authorization, Project, and Work Item metadata.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` - the inventory surfaces membership reconciliation candidates without mutating memberships.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - runtime counts and classifications come from fresh canonical reads.
- `DCL-REPORTING-SURFACE-FRESH-READ-001` - generated JSON and Markdown output identifies fresh current-state views as source authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation was performed under the linked GO proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps specs to executed verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - future project creation, membership, retirement, duplicate disposition, and dependency changes remain separate lifecycle events.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - source, tests, and durable bridge evidence are aligned.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge INDEX remains the canonical proposal/review state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation targets remain inside `E:\GT-KB`.

## Owner Decisions / Input

No new owner input was needed. The implementation uses the active governance-hardening PAUTH and stays within the GO conditions. Future live membership insertion, project creation, work-item retirement, duplicate disposition, dependency mutation, owner-decision packet filing, or generated bridge filing still requires separate authorization.

## Specification-Derived Verification Mapping

| Requirement | Verification |
|---|---|
| `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` / `DCL-STANDING-BACKLOG-DB-SCHEMA-001`: use MemBase current-state authority. | CLI reads `current_work_items`, `current_projects`, `current_project_work_item_memberships`, and `current_project_dependencies` through read-only SQLite; tests assert source-authority metadata. |
| `GOV-STANDING-BACKLOG-001` / `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`: inventory must classify backlog/project membership state without bulk mutation. | Tests cover all nine classifications and live smoke reports zero omitted and duplicate rows. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` / `DCL-REPORTING-SURFACE-FRESH-READ-001`: counts must be fresh, not copied from the 2026-06-02 report. | Live JSON/Markdown smoke runs read the current database and report 974 non-terminal work items with current classification counts. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`: only `cli_extension` and `test_addition` mutation classes are used. | Changed files are exactly the approved script and test file. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: mutation/disposition events remain separate. | CLI has no apply mode and report states follow-on mutation slices remain separate. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: linked requirements need executable evidence. | Focused pytest, ruff check, ruff format, and live CLI smoke commands below. |

## Commands Run

```text
python scripts\implementation_authorization.py begin --bridge-id gtkb-project-membership-reconciliation-slice-1-inventory-tool
```

Observed result: authorization packet created for the two approved target paths with packet hash `sha256:f34b96832e6e426ac83f3890f76f0b0af7c0b3da24e2a914c046fb8aaa0cbb30`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_inventory_project_membership_reconciliation.py -q --tb=short
```

Observed result: `4 passed in 0.39s`.

```text
groundtruth-kb\.venv\Scripts\ruff.exe check scripts\inventory_project_membership_reconciliation.py platform_tests\scripts\test_inventory_project_membership_reconciliation.py
```

Observed result: `All checks passed!`

```text
groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts\inventory_project_membership_reconciliation.py platform_tests\scripts\test_inventory_project_membership_reconciliation.py
```

Observed result: `2 files already formatted`.

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\inventory_project_membership_reconciliation.py --format json --output-json .gtkb-state\project-membership-reconciliation\inventory.json
groundtruth-kb\.venv\Scripts\python.exe scripts\inventory_project_membership_reconciliation.py --format markdown --output-markdown .gtkb-state\project-membership-reconciliation\inventory.md
```

Observed result: both live smoke commands exited 0.

Live JSON summary:

```json
{
  "classification_counts": {
    "already_active_project_member": 196,
    "dangling_or_terminal_project_membership": 6,
    "dependency_blocked_candidate": 59,
    "existing_project_candidate_exact": 0,
    "existing_project_candidate_weak": 82,
    "needs_manual_triage": 0,
    "new_project_candidate_cluster": 627,
    "obsolete_or_duplicate_candidate": 4,
    "single_wi_project_candidate": 0
  },
  "duplicate_inventory_rows": 0,
  "omitted_non_terminal_work_items": 0,
  "total_non_terminal_work_items": 974
}
```

## Acceptance Criteria Status

- `scripts/inventory_project_membership_reconciliation.py` exists and is a read-only CLI: met.
- `platform_tests/scripts/test_inventory_project_membership_reconciliation.py` covers all nine primary classifications, duplicate/omission failure handling, JSON rendering, Markdown rendering, and optional output-path behavior: met.
- The CLI fresh-reads current MemBase state at runtime and does not rely on 2026-06-02 report counts as constants: met.
- Every non-terminal work item is represented exactly once in JSON inventory: met in tests and live smoke (`duplicate_inventory_rows: 0`, `omitted_non_terminal_work_items: 0`).
- Output separates exact, weak, new-project, obsolete/duplicate, terminal/dangling membership, dependency-blocked, and manual-triage rows: met.
- No live project/work-item/database mutation path exists in this slice: met.
- Follow-on mutation slices still require separate authorization: preserved.

## Risk And Rollback

Risk: conservative heuristics may classify some rows as weak/new-project candidates that a human would later resolve differently. That is acceptable for this dry-run slice because the output is advisory inventory only.

Rollback: revert the source/test commit and this append-only report. Runtime artifacts under `.gtkb-state/project-membership-reconciliation/` can be discarded; they are not committed source artifacts and do not mutate MemBase.
