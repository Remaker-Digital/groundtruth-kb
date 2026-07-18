NEW
::init gtkb lo
::open build

# WI-5326 Atomic Work-Item/Test Linkage and Exact Repair

bridge_kind: prime_proposal
Document: gtkb-wi5326-atomic-work-item-test-linkage
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never

Project Authorization: PAUTH-TREE-STABILIZATION-WI5326-ATOMIC-WORK-ITEM-TEST-LINKAGE-V2-20260717
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5326
Related Work Items: WI-5156, WI-5325, WI-5456, WI-5470

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py", "groundtruth-kb/src/groundtruth_kb/db.py", "platform_tests/scripts/test_cli_backlog_add_work_item.py"]

implementation_scope: source | test | governed MemBase transaction repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Make `gt backlog add-work-item` satisfy its documented GOV-12/GOV-13
contract as one atomic operation. Today the command opens separate
`KnowledgeDB` handles and commits the work item, test, and phase version
independently. A malformed existing phase `test_ids` value can therefore fail
after the work item and test have committed. On the successful path, the new
work item is also inserted before the test ID is allocated, so its
`source_test_id` remains null even though the command reports a linked test.

The corrected command must preflight every request, work-item field, target
specification, phase, and phase `test_ids` representation used by apply. It
must then allocate both IDs and create the initial work-item row with the
allocated test ID, the test row, and the requested phase version through one
database connection and one transaction. One document actor is resolved
before the transaction. Any exception rolls back all rows and lifecycle
events.

Add a separately named governed CLI repair operation for exact historical
pairs. The caller must supply one work-item ID, one test ID, and one phase ID.
The operation may append a work-item version containing `source_test_id` and,
when needed, a phase version containing that test ID only when canonical
provenance proves the explicit pair was created by `gt backlog add-work-item`.
It must be idempotent and fail before mutation on missing, conflicting,
ambiguous, already-claimed, or malformed evidence. It must not scan for
candidates or perform a bulk backfill.

Implementation is sequenced behind terminal disposition of WI-5156 and any
other active owner of `groundtruth-kb/src/groundtruth_kb/cli.py` or
`groundtruth-kb/src/groundtruth_kb/db.py`. This proposal grants no authority
to absorb, overwrite, stage, or finalize foreign hunks.

## Scope and Invariants

- Preserve existing command options and output fields for
  `gt backlog add-work-item`; adding linkage evidence is additive.
- Run the same phase `test_ids` parser and all request validation during
  dry-run and apply. Accept `null`, a list of unique canonical test IDs, or a
  JSON string encoding that list. Reject malformed JSON, non-list values,
  non-string members, empty IDs, and duplicates before any insert.
- Use one `KnowledgeDB` connection. Allocate work-item and test IDs within the
  transaction and refuse any collision before insertion.
- Extend only the required DB insert methods with caller-owned transaction
  support while keeping their current commit-by-default behavior for all
  existing callers.
- Insert the work item's initial version with `source_test_id` equal to the
  allocated test ID. Do not create a second work-item version on the normal
  success path.
- Commit the work item, test, phase version, and their lifecycle events once.
  Roll back all of them if validation, allocation, insert, event recording, or
  readback fails.
- The repair operation requires exact explicit IDs and the original
  `Auto-created with <WI> via gt backlog add-work-item.` test provenance.
  It rejects a test already linked to another work item, a work item already
  linked to another test, a mismatched specification or phase, unknown IDs,
  and any noncanonical or ambiguous evidence.
- Repair dry-run performs every validation used by apply and reports the exact
  append-only versions it would add. A fully repaired pair is a no-op and
  creates no extra versions or events.
- The repair proving cases are `WI-5325`/`TEST-11462` and
  `WI-5456`/`TEST-11557`; implementation and tests must use isolated fixtures
  and must not repair the live records until a later exact owner-approved
  invocation is separately authorized.
- No direct SQLite maintenance, schema change, broad backfill, dispatcher,
  TAFE, harness, bridge-state, claim, lease, credential, Git, deployment,
  release, or external-system mutation is in scope.

## Specification Links

- `GOV-12` - requires every newly created work item to have the test created by the same governed operation and linked through `source_test_id`.
- `GOV-13` - requires the new test to belong to the requested test-plan phase at creation, not in a later best-effort step.
- `GOV-STANDING-BACKLOG-001` - requires work-item/test linkage and repair evidence to remain in canonical MemBase rather than ad hoc files or direct database maintenance.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - keeps proposal, review, implementation report, and independent verdict in the numbered bridge chain.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires WI-5326 to remain inside its bounded active project authorization.
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` - prevents this singleton authorization from being reused for other transaction or backlog repairs.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - limits implementation to the declared work item, mutation classes, and five target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this transaction behavior and its tests to trace to canonical requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the project, PAUTH, and work-item tuple to remain mechanically valid.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the linked TEST-11565 cases and focused executable suite before VERIFIED.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - keeps the defect, test, PAUTH, proposal, implementation, verdict, and any exact live repair as distinct durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires the original partial-write and null-linkage evidence to remain reconstructable through the artifact graph.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps every implementation, fixture, and verification path inside the GT-KB platform root and excludes adopter or external databases.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps WI-5326 open until implementation, independent verification, and focused finalization are complete.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes bounded carriers and proposals for defects discovered while driving the active bridge/TAFE/harness goal, while preserving every later implementation gate.
- `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-005.md` and its GO at version 006 - introduced the deterministic GOV-12/GOV-13 compound writer whose atomicity and linkage contract this proposal corrects.
- `WI-5326` and `TEST-11565` - retain the observed `WI-5325`/`TEST-11462` partial-write reproduction, the later successful-path null-`source_test_id` evidence, and the required transaction/repair outcomes.
- `WI-5156` - owns current shared `cli.py` and `db.py` transaction-capability hunks; terminal disposition is a hard sequence prerequisite before WI-5326 implementation starts.

## Owner Decisions / Input

No new owner decision is required. The owner-directed active program requires
all discovered bridge/TAFE/harness defects and derived blockers to reach a
genuine terminal state.
`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` permits this bounded
proposal carrier. Active singleton authorization
`PAUTH-TREE-STABILIZATION-WI5326-ATOMIC-WORK-ITEM-TEST-LINKAGE-V2-20260717`
includes only WI-5326 and the fourteen cited specifications. Protected
implementation remains gated on independent GO, exact work intent,
implementation-start authorization, and terminal shared-file ownership.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-12` already requires work-item/test
creation linkage, and `GOV-13` already requires phase membership at test
creation. Their combination requires one complete result rather than three
independently committed best-effort writes. The defect is missing transactional
enforcement and an exact governed repair route for rows produced by the
defective command, not a missing product or governance requirement.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5326; TEST-11565; WI-5325/TEST-11462 and WI-5456/TEST-11557 reproductions",
  "canonical_authority": "GOV-12; GOV-13; GOV-STANDING-BACKLOG-001",
  "primary_route": "gt backlog add-work-item plus one explicitly named exact-pair repair command",
  "before_behavior": "The command commits three independent writes and leaves source_test_id null; a late phase parse failure leaves partial rows",
  "after_behavior": "Dry-run and apply share preflight, success commits all four relationships once, and any failure rolls back everything",
  "self_descriptive_naming": "transaction, source_test_id, work_item_id, test_id, phase_id, and repair distinguish creation from exact recovery",
  "obsolete_guidance_disposition": "Existing command syntax and GOV-12/GOV-13 guidance remain authoritative; the implementation is brought into conformance",
  "history_preservation": "Historical partial rows remain unchanged unless named in a separately authorized exact repair invocation",
  "baseline": "Temporary-database reproduction of malformed phase data and successful creation with null work_items.source_test_id",
  "expected_result": "One success transaction creates one linked work item, one test, and one phase version; injected failures leave no new rows or events",
  "rollback": "A separately governed focused revert removes only the WI-5326 source and test hunks",
  "hard_invariants": "No broad backfill; no direct database bypass; no foreign hunk capture; commit-by-default compatibility for existing DB callers",
  "fail_closed_conditions": "Malformed phase data, ID collision, unknown or mismatched repair IDs, conflicting linkage, ambiguous provenance, shared-file ownership, or missing governance gate",
  "essential_context_preservation": "Output and evidence retain actor, exact IDs, phase, dry-run/apply state, no-op state, versions, and rollback diagnostics"
}
```

## Spec-Derived Verification Plan

`TEST-11565` and the focused integration module must demonstrate:

| Governing requirement | Verification | Expected result |
|---|---|---|
| `GOV-12` | Create one work item through the CLI and read back both current rows. | Exactly one work item and one test exist; the initial work-item version has `source_test_id` equal to the returned test ID; the test cites the requested specification and original WI provenance. |
| `GOV-13` | Read the requested phase after success; test null, JSON-string, and list input forms; test malformed, scalar, non-string, empty, and duplicate members. | The same returned test ID is present exactly once after success; every invalid representation fails in dry-run and apply before any row or event is added. |
| `GOV-12`; `GOV-13` | Inject failures at work-item insert, test insert/event, phase insert/event, readback, and final commit. | Work-item, test, phase-version, and lifecycle-event counts remain byte-for-byte unchanged after every failure. |
| `GOV-STANDING-BACKLOG-001` | Exercise repair dry-run/apply/no-op against isolated fixtures for the two named historical pair shapes. | Only the explicit pair is linked, one append-only WI version and at most one phase version are added atomically, and a second invocation adds nothing. |
| `GOV-STANDING-BACKLOG-001` | Test unknown IDs, mismatched test provenance/specification/phase, test claimed by another WI, WI linked to another test, ambiguous evidence, and malformed phase data. | Each case exits nonzero before mutation with an actionable reason; no candidate scan or unrelated row change occurs. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`; `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Run applicability and implementation-start preflights against this exact proposal, PAUTH, WI, and target set. | Filing is reviewable; protected work cannot start before independent GO or while WI-5156/another owner retains shared target hunks. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run both mandatory proposal preflights and resolve every cited ID with the in-root canonical CLI. | Project linkage is exact, clause gaps are zero, and no cited specification is absent. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Execute the focused pytest module, Ruff check/format, `py_compile`, and diff checks below. | Every mapped case passes before an independent VERIFIED verdict can be authored. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Inspect WI-5326, TEST-11565, PAUTH, bridge chain, start packet, report, verdict, and focused commit. | The observed failures, correction, and terminal evidence remain reconstructable and WI-5326 is not resolved early. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve the five declared targets and run all fixtures against temporary in-root test databases. | No adopter, archive, external database, or out-of-root artifact is read as authority or mutated. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Inspect live dispatcher/TAFE state and the numbered bridge chain before each lifecycle transition. | Only the role-authorized latest status drives review, implementation, and verification. |

Required command evidence:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cli_backlog_add_work_item.py -q --no-header --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py groundtruth-kb/src/groundtruth_kb/db.py platform_tests/scripts/test_cli_backlog_add_work_item.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py groundtruth-kb/src/groundtruth_kb/db.py platform_tests/scripts/test_cli_backlog_add_work_item.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py groundtruth-kb/src/groundtruth_kb/db.py platform_tests/scripts/test_cli_backlog_add_work_item.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py groundtruth-kb/src/groundtruth_kb/db.py platform_tests/scripts/test_cli_backlog_add_work_item.py
```

## Acceptance Criteria

- Dry-run and apply execute the same complete request, spec, phase, and
  `test_ids` validation before mutation.
- Success uses one actor, connection, and transaction and creates exactly one
  work-item version with the allocated `source_test_id`, one test, and one
  requested phase version.
- Any injected failure rolls back every row and lifecycle event created by the
  invocation.
- Existing DB callers retain commit-by-default behavior; transaction
  suppression is explicit and confined to the compound writer.
- The exact repair command accepts only caller-supplied WI/test/phase IDs,
  proves canonical original-command provenance and nonconflict, and never
  scans or backfills.
- Repair dry-run and apply share validation; successful repair is atomic; a
  fully repaired pair is an idempotent no-op.
- The five-file boundary is exact, all focused checks pass, and no shared
  source implementation starts before WI-5156 and other target owners are
  terminal.

## Risk / Rollback

The main risk is changing commit behavior in shared low-level DB methods. The
implementation must preserve `commit=True` defaults and test an ordinary
existing caller for each changed method. A second risk is repairing the wrong
historical relationship. The repair route therefore requires exact IDs,
canonical original-command provenance, one-to-one nonconflict, a dry-run, and
no discovery or bulk mode. A third risk is mixing WI-5156's current shared
transaction hunks into this item; implementation remains blocked until those
hunks have terminal ownership evidence.

Rollback is a separately governed focused revert of only the WI-5326 hunks in
the five declared files. It must not rewrite the bridge chain, discard
WI-5156 or other foreign hunks, delete historical rows, or reverse any
separately authorized exact repair already applied to live MemBase.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5326-atomic-work-item-test-linkage`; no prior version
is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered
file chain are the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(backlog)` - the change closes demonstrated partial-write and missing-link
defects in an existing governed command without adding a new authority or
bulk maintenance workflow.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
