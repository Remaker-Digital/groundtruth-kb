NEW
::init gtkb lo
::open build

# GT-KB Bridge Implementation Report - gtkb-wi5326-atomic-work-item-test-linkage - 003

bridge_kind: implementation_report
Document: gtkb-wi5326-atomic-work-item-test-linkage
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5326-atomic-work-item-test-linkage-002.md
Approved proposal: bridge/gtkb-wi5326-atomic-work-item-test-linkage-001.md
Project Authorization: PAUTH-TREE-STABILIZATION-WI5326-ATOMIC-WORK-ITEM-TEST-LINKAGE-V2-20260717
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5326
Recommended commit type: fix

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope
author_metadata_source: explicit_interactive_session_metadata

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py", "groundtruth-kb/src/groundtruth_kb/db.py", "platform_tests/scripts/test_cli_backlog_add_work_item.py"]

## Implementation Claim

`gt backlog add-work-item` now performs complete request, specification,
phase, and phase-`test_ids` validation before the first row insert. Apply
acquires one `BEGIN IMMEDIATE` transaction, allocates both IDs through the
same `KnowledgeDB`, inserts the initial work-item version with
`source_test_id` already set, inserts the linked test, appends the requested
phase version, verifies all three readbacks, and commits once. Any exception,
including a final commit failure, rolls back every row and existing lifecycle
event.

The required DB writer methods accept an explicit `commit=False` while
retaining `commit=True` defaults for all existing callers. This change does
not add a test-plan-phase lifecycle event. The transaction atomically carries
the existing `wi_created` and `test_created` events; phase-version writes keep
their pre-existing no-event contract.

A separately named `gt backlog repair-work-item-test-link` command repairs
only one caller-supplied WI/test/phase tuple. It requires canonical IDs, exact
`Auto-created with <WI> via gt backlog add-work-item.` provenance, matching
specification, unclaimed one-to-one linkage, and unambiguous phase evidence.
Dry-run and apply share preflight, apply is atomic, and a fully repaired tuple
is a no-op. Tests exercise isolated versions of both named historical shapes,
`WI-5325`/`TEST-11462` and `WI-5456`/`TEST-11557`; no live historical pair was
repaired.

## Specification Links

- `GOV-12`
- `GOV-13`
- `GOV-STANDING-BACKLOG-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required.

`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes the
bounded defect-repair lifecycle while preserving PAUTH, bridge GO, claim,
implementation-start, independent verification, and focused-commit gates.
The active singleton PAUTH includes only WI-5326 and the five declared target
paths. No dispatcher configuration, TAFE/runtime, harness, credential,
deployment, release, Git-history, or external-system operation was performed.

## Prior Deliberations

- `bridge/gtkb-wi5326-atomic-work-item-test-linkage-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5326-atomic-work-item-test-linkage-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-011.md` - terminal VERIFIED shared-file predecessor; focused commit `434776ba`.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner authorization for bounded fleet-defect repair.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-12` | Focused pytest proves one initial WI version carries the allocated `source_test_id`, one test is created, two existing lifecycle events commit, and injected failures leave no rows or events. Result: 47 passed. |
| `GOV-13` | Focused pytest accepts null/list/JSON-list phase forms, rejects malformed/scalar/non-string/empty/noncanonical/duplicate forms in dry-run and apply, and proves the allocated test appears exactly once in a new phase version. Result: pass. |
| `GOV-STANDING-BACKLOG-001` | Canonical `gt backlog update WI-5326` created v5 with the independently confirmed 391/394 (99.2%) historical scope and explicit no-bulk-repair boundary; both named exact repair shapes run only in isolated fixtures. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge show ... --json --compact` reports latest GO v002; the matching PB claim and schema-v3 packet were live before protected edits; this report is filed append-only through the canonical helper. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `implementation_authorization.py begin` produced an authorized schema-v3 packet and `validate --target` returned authorized for all five paths. |
| `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` | `gt projects show-authorization ... --json` reports active singleton `included_work_item_ids=["WI-5326"]`; no other live work item was repaired or mutated. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Helper plan reports exactly five changed files and 1,805 excluded dirty paths; diff and status checks show no sixth implementation path. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The approved proposal carries all fourteen linked specifications; applicability preflight is executed against this completed report before filing. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Report header preserves the exact PAUTH/project/WI tuple and five target paths from the approved proposal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps every carried specification to executed evidence; pytest, Ruff, format, compile, CLI-help, and diff gates all pass. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5326 v5, TEST-11565, PAUTH, proposal, GO, implementation, source/tests, and this report remain separate durable linked artifacts. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Successful fixture operations create durable WI/test/phase artifacts atomically; denied, failed, and dry-run operations create none. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All five targets and every temporary test database are in-root platform paths; no adopter, archive, or external database is used. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | WI-5326 remains open and this report is NEW pending independent verification; no terminal status or commit is self-asserted. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cli_backlog_add_work_item.py -q --no-header --tb=short`
- `groundtruth-kb\.venv\Scripts\ruff.exe check groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\cli_backlog_add.py groundtruth-kb\src\groundtruth_kb\cli_backlog_add_work_item.py groundtruth-kb\src\groundtruth_kb\db.py platform_tests\scripts\test_cli_backlog_add_work_item.py`
- `groundtruth-kb\.venv\Scripts\ruff.exe format --check groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\cli_backlog_add.py groundtruth-kb\src\groundtruth_kb\cli_backlog_add_work_item.py groundtruth-kb\src\groundtruth_kb\db.py platform_tests\scripts\test_cli_backlog_add_work_item.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m py_compile groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\cli_backlog_add.py groundtruth-kb\src\groundtruth_kb\cli_backlog_add_work_item.py groundtruth-kb\src\groundtruth_kb\db.py platform_tests\scripts\test_cli_backlog_add_work_item.py`
- `git diff --check -- groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py groundtruth-kb/src/groundtruth_kb/db.py platform_tests/scripts/test_cli_backlog_add_work_item.py`
- `groundtruth-kb\.venv\Scripts\gt.exe backlog repair-work-item-test-link --help`
- `groundtruth-kb\.venv\Scripts\gt.exe bridge show gtkb-wi5326-atomic-work-item-test-linkage --json --compact`
- `groundtruth-kb\.venv\Scripts\gt.exe projects show-authorization PAUTH-TREE-STABILIZATION-WI5326-ATOMIC-WORK-ITEM-TEST-LINKAGE-V2-20260717 --json`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target <each exact target>`
- `groundtruth-kb\.venv\Scripts\gt.exe backlog update WI-5326 --status-detail <scope disclosure> --change-reason <reason> --json`
- `groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\impl_report_bridge.py plan gtkb-wi5326-atomic-work-item-test-linkage --compact`

## Observed Results

- Focused pytest: 47 passed; one pre-existing unknown `asyncio_mode` warning.
- Success creates one WI, one test, one phase version, and exactly the existing `wi_created` plus `test_created` events. The initial WI version carries the returned test ID.
- Injected failures after work-item insert, test insert, phase insert, final readback, and final commit leave work-item, test, phase-version, and pipeline-event counts unchanged.
- Strict phase parser accepts null, canonical lists, and JSON-encoded canonical lists; dry-run and apply reject malformed JSON, scalar, non-string, empty, whitespace-altered, noncanonical, and duplicate IDs before mutation.
- Exact repair dry-run/apply/no-op passes for isolated `WI-5325`/`TEST-11462` and `WI-5456`/`TEST-11557` shapes. Wrong provenance, conflicting WI linkage, another WI claimant, and another phase membership fail without mutation.
- Ruff lint: all checks passed. Ruff format: five files already formatted. `py_compile`: exit 0. `git diff --check`: exit 0 with only Git LF-to-CRLF notices.
- Repair CLI help exposes only exact `--work-item`, `--test`, `--test-plan-phase`, `--change-reason`, `--dry-run`, and `--json` controls; there is no discovery or bulk mode.
- Bridge readback: latest GO at v002. PAUTH readback: active, singleton WI-5326, allowed bridge/metadata/source/test/governance-evidence classes, and forbidden dispatcher/external/release operations.
- WI-5326 v5 now durably records 391/394 (99.2%) null-linkage scope and that no bulk backfill or live repair is authorized.
- Candidate-content applicability preflight: pass; no missing required specs, no missing advisory specs, and no blocking errors.
- Mandatory ADR/DCL clause preflight: four must-apply clauses, zero evidence gaps, and zero blocking gaps.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py`
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py`
- `groundtruth-kb/src/groundtruth_kb/db.py`
- `platform_tests/scripts/test_cli_backlog_add_work_item.py`

Excluded out-of-scope dirty paths: 1805.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: the change repairs partial-write and missing-link behavior in an existing governed command and adds its exact recovery route.

```text
     groundtruth-kb/src/groundtruth_kb/cli.py           |  47 +++
     .../src/groundtruth_kb/cli_backlog_add.py          |  11 +-
     .../groundtruth_kb/cli_backlog_add_work_item.py    | 431 ++++++++++++++++-----
     groundtruth-kb/src/groundtruth_kb/db.py            |  16 +-
     .../scripts/test_cli_backlog_add_work_item.py      | 378 ++++++++++++++++++
     5 files changed, 773 insertions(+), 110 deletions(-)
```

## Acceptance Criteria Status

- PASS: dry-run and apply execute the same complete request, specification, phase, and strict `test_ids` validation.
- PASS: success uses one actor, one `KnowledgeDB`, one immediate transaction, and one final commit.
- PASS: the initial WI version links the allocated test; the same test is created and assigned to the requested phase.
- PASS: five injected failure points roll back every new artifact row and existing lifecycle event.
- PASS: existing DB callers retain commit-by-default behavior; transaction suppression is explicit and used only by the compound writer/repair.
- PASS: the exact repair command requires caller-supplied WI/test/phase IDs, exact provenance, one-to-one nonconflict, and unambiguous phase evidence; it has no scan or bulk mode.
- PASS: both named historical pair shapes pass dry-run/apply/idempotent-no-op fixtures; conflicting evidence fails closed.
- PASS: no new phase lifecycle event was introduced; the existing `wi_created` and `test_created` events commit atomically.
- PASS: the 391/394 blast radius and no-bulk boundary are durable in WI-5326 v5.
- PASS: WI-5156 is terminal/focused-finalized, the five-file pre-start baseline was clean, all checks pass, and no foreign hunk was adopted.

## Risk And Rollback

Residual risk is concentrated in shared low-level DB commit ownership. The
new keyword remains default-true, and focused tests prove existing seed
callers persist immediately while compound operations can hold one
transaction. Strict phase parsing intentionally turns malformed legacy data
into an actionable fail-before-write error. Exact repair intentionally rejects
uncertain provenance rather than guessing.

Rollback is a separately governed focused revert of only the five
implementation files listed below. Numbered bridge artifacts, WI-5326 v5,
TEST-11565, and any later independently authorized live repair remain
append-only and are not deleted or rewritten. No live historical repair was
performed by this implementation.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
