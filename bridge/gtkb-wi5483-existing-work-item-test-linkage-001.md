NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

# WI-5483 Governed Existing-Work-Item Linked-Test Transaction

bridge_kind: prime_proposal
Document: gtkb-wi5483-existing-work-item-test-linkage
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5483-EXISTING-WI-TEST-LINKAGE-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5483
Related Work Items: WI-5243, WI-5326
Related Test Artifacts: TEST-11575

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py", "groundtruth-kb/src/groundtruth_kb/db.py", "platform_tests/scripts/test_cli_backlog_add_work_item.py"]

implementation_scope: source | test | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

## Summary

Add one governed `gt backlog add-linked-test` transaction for an already
existing work item that has no linked test. The command creates exactly one
test, assigns it to one current test-plan phase, and appends one work-item
version carrying `source_test_id`, atomically and idempotently.

This closes the gap between the existing compound work-item creation command
and later hygiene normalization. It does not duplicate WI-5243's creation-time
`source_test_id` correction or WI-5326's atomic new-work-item transaction and
exact-pair repair. Implementation is hard-sequenced behind both predecessors.

## Claim

Prime Builder proposes a bounded four-file WI-5483 implementation slice. This
filing performs no source, test, MemBase, dispatcher, TAFE, harness, runtime,
Git, credential, deployment, or release mutation.

## Requirement Sufficiency

Existing requirements sufficient.

`GOV-12`, `GOV-13`, `SPEC-1496`, `GOV-STANDING-BACKLOG-001`, WI-5483,
TEST-11575, the active bounded PAUTH, and the predecessor threads define the
required behavior. No new owner choice or formal requirement is needed.

## Existing Capability And Gap

`gt backlog add-work-item` already creates a new work item, a new test, and a
phase assignment through
`groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py`. It cannot
operate on an existing work item.

The governed backlog update command can append a work-item version, but no
single transaction currently:

- verifies that one existing work item has no `source_test_id`;
- allocates and inserts one test;
- assigns that test to one current test-plan phase;
- appends the work-item version carrying the new test id; and
- rolls every effect back if any later write fails.

Direct database access or separate CLI calls would create a partial-state
window and are not acceptable substitutes.

## Hard Implementation-Start Gates

Even after independent GO, Prime Builder must not acquire an implementation
claim or run the implementation-start issuer until all of these are true:

1. WI-5243 has a terminal governed disposition and its creation-time
   `source_test_id` ownership is focused-finalized.
2. WI-5326 has a terminal governed disposition and its atomic
   work-item/test/phase ownership is focused-finalized.
3. `groundtruth-kb/src/groundtruth_kb/cli.py` is clean relative to committed
   HEAD.
4. `groundtruth-kb/src/groundtruth_kb/db.py` is clean relative to committed
   HEAD.
5. The other two exact targets remain clean relative to committed HEAD.
6. The bounded PAUTH remains active, this thread remains latest GO, and the
   exact claim plus schema-v3 implementation-start validations authorize all
   four paths.

Immediately before claim/start, Prime Builder must record the four SHA-256
baselines and return for renewed review on any dirty path, unexpected
predecessor state, or target drift. No foreign-hunk adoption is authorized.

## Proposed Command

```text
gt backlog add-linked-test \
  --work-item WI-NNNN \
  --test-title <title> \
  --test-type <assertion|e2e|integration|unit|manual> \
  --test-expected-outcome <text> \
  --test-plan-phase PHASE-NNN \
  --change-reason <reason> \
  [--test-spec-id SPEC-NNNN] \
  [--dry-run] \
  [--json]
```

The command defaults the test specification to the work item's
`source_spec_id`. It requires an explicit test specification when the work item
has no usable source specification.

## Proposed Scope

- Add an immutable request object and service operation beside the existing
  compound backlog creation service.
- Add the `gt backlog add-linked-test` command in `cli.py`.
- Validate the full request, attribution, current work item, current phase,
  phase `test_ids` representation, source specification, current
  `source_test_id`, and duplicate provenance before the first write.
- Allocate one monotonic test id using the same canonical allocation semantics
  as the existing compound service.
- Perform test insertion, phase-version insertion, and work-item-version
  insertion in one database transaction.
- Update the work item only through an append-only new version; do not rewrite
  an existing row.
- Return the current exact successful result on an idempotent rerun when the
  same work item, test provenance, phase, and expected content already match.
- Reject an existing conflicting `source_test_id`, duplicate test provenance
  with different content or phase, unknown work item, missing source spec,
  unknown phase, malformed phase test ids, invalid test type, empty required
  text, and injected write failure.
- Make dry-run execute the same parsing, lookup, validation, duplicate, and
  conflict checks while suppressing all writes.
- Keep `gt backlog add-work-item` behavior unchanged.
- Do not implement WI-5243 or WI-5326 inside this slice.
- Do not inspect or mutate dispatcher configuration, dispatcher runtime state,
  TAFE, harness configuration, worker eligibility, routing, credentials, Git
  history, deployment, release state, or any path outside the four exact
  targets.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION; WI-5483; TEST-11575",
  "canonical_authority": "GOV-12; GOV-13; GOV-STANDING-BACKLOG-001; SPEC-1496",
  "primary_route": "gt backlog add-linked-test --work-item WI-NNNN --test-title <title> --test-type <type> --test-expected-outcome <text> --test-plan-phase PHASE-NNN --change-reason <reason>",
  "before_behavior": "No governed single transaction can create and link a missing test for one already-existing work item.",
  "after_behavior": "One self-descriptive command validates and atomically creates the test, phase membership, and source_test_id work-item version.",
  "self_descriptive_naming": "add-linked-test and ExistingWorkItemLinkedTestRequest describe the actor-visible operation and object boundary.",
  "obsolete_guidance_disposition": "Direct KnowledgeDB use and multiple independent CLI mutations are not supported recovery routes.",
  "history_preservation": "Existing work-item, test, and phase versions remain append-only; the command adds one new version where required.",
  "baseline": {
    "required_predecessors": [
      "WI-5243 terminal focused-finalized",
      "WI-5326 terminal focused-finalized"
    ],
    "linked_verification": "TEST-11575",
    "target_count": 4
  },
  "expected_result": {
    "success": "Exactly one test, one phase version, and one work-item version are committed atomically.",
    "idempotent_rerun": "No new rows; the command returns the existing exact linkage.",
    "denial": "No rows are changed.",
    "injected_failure": "The transaction rolls back every attempted effect."
  },
  "rollback": {
    "instructions": "Governed revert of only the four WI-5483 implementation targets.",
    "verification": "Run the full focused compound-backlog CLI test module and confirm existing add-work-item behavior is unchanged."
  },
  "hard_invariants": [
    "One invocation targets exactly one existing work item and one test-plan phase.",
    "All validation and duplicate checks complete before the first write.",
    "The three row effects commit or roll back together.",
    "Work-item and phase history is append-only.",
    "No direct production database, dispatcher, TAFE, harness, Git, credential, release, or deployment mutation occurs outside the command's explicit transaction."
  ],
  "fail_closed_conditions": [
    "The work item or phase is unknown.",
    "The work item already has a conflicting source_test_id.",
    "The source specification is missing or invalid.",
    "The phase test_ids representation is malformed.",
    "Duplicate provenance exists with conflicting content or phase.",
    "Attribution cannot be resolved.",
    "Any database write or readback fails."
  ],
  "essential_context_preservation": "The result retains work-item id, test id, phase id, source specification, changed-by attribution, change reason, dry-run state, and idempotency disposition."
}
```

## Specification Links

- `GOV-12`
- `GOV-13`
- `SPEC-1496`
- `SPEC-1603`
- `SPEC-1605`
- `GOV-STANDING-BACKLOG-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes the
  bounded WI-5483 carrier and governed proposal while retaining every later
  exact gate.
- `bridge/gtkb-wi5326-atomic-work-item-test-linkage-001.md` is the canonical
  predecessor proposal for atomic new-work-item creation and exact-pair
  recovery. WI-5483 begins only after that ownership is terminally finalized.
- No prior Deliberation Archive record found in the required search rejects an
  existing-work-item-only linked-test transaction.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` is the owner
  decision behind
  `PAUTH-DISPATCHER-BLACK-BOX-WI5483-EXISTING-WI-TEST-LINKAGE-20260717`.
- The active dispatcher configuration hold remains binding. This proposal
  neither requires nor authorizes dispatcher configuration or runtime
  mutation.
- The canonical-reference boundary is preserved: this proposal relies only on
  MemBase, Deliberation Archive records, numbered bridge artifacts, governed
  source, and governed tests.

## Specification-Derived Verification Plan

| Specification | Required executed verification |
| --- | --- |
| `GOV-12` | Prove one existing work item receives exactly one linked test and a new `source_test_id` version. |
| `GOV-13` | Prove the test is assigned to one current phase in the same transaction and no orphan is possible. |
| `SPEC-1496` | Assert every preserved work-item field remains unchanged except version, `source_test_id`, attribution, and change reason. |
| `SPEC-1603` | Assert the created test id appears in current phase membership after commit and never after rollback. |
| `SPEC-1605` | Exercise phase-version append semantics and preserve the canonical phase grouping. |
| `GOV-STANDING-BACKLOG-001` | Confirm WI-5483 and TEST-11575 remain the durable implementation and verification authority. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Validate exact GO, claim, implementation-start packet, four targets, report, and independent verification. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Preserve work item, test, phase, proposal, report, and verdict linkage. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live applicability preflights with the complete linked set. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry this complete map into the report with exact commands and observed results. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Validate PAUTH, project, work item, related work, test artifact, and exact target headers. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Validate the active singleton PAUTH and schema-v3 implementation-start evidence. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Prove only bridge, metadata, governance evidence, source, and test classes are used. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Revalidate PAUTH, predecessors, claim, and target cleanliness at start and report time. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Prove no protected mutation occurs before latest GO and exact start authorization. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Read current WI-5243/WI-5326 terminal evidence and clean target baselines before mutation. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run the existing add-work-item test suite unchanged plus all new command cases. |
| `GOV-WORK-TREE-HYGIENE-001` | Record four pre/post hashes, exact diff inventory, and zero foreign-hunk adoption. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm all changes remain in-root GT-KB platform source/tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run exact authorization validation and both Ruff gates from the Codex/Windows surface. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Prove successful action creates durable artifacts and denied/dry-run actions create none. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Preserve NEW to GO to report to independent VERIFIED lifecycle. |

## Acceptance Criteria

- Success creates exactly one current test, one new phase version containing
  the test id, and one new work-item version carrying that id, in one commit.
- Idempotent rerun with identical provenance returns the current linkage and
  creates zero rows.
- Conflicting existing `source_test_id`, conflicting duplicate provenance,
  unknown work item, unknown or malformed phase, missing source spec, invalid
  test fields, unresolved attribution, and injected failures create zero rows.
- Dry-run returns the same allocation/validation/idempotency disposition used
  by apply and creates zero rows.
- Existing `gt backlog add-work-item` behavior and tests remain unchanged.
- The focused module, adjacent backlog CLI suites, scoped `ruff check`,
  `ruff format --check`, and `git diff --check` pass.
- The implementation report proves WI-5243/WI-5326 terminalization and clean
  four-file baselines before mutation.

## Applicability Preflight

Candidate applicability executed against this completed proposal and reported
`preflight_passed: true`, `missing_required_specs: []`,
`missing_advisory_specs: []`, and `blocking_errors: []`.

## Clause Applicability

The mandatory clause preflight executed against this completed proposal and
reported five clauses evaluated, four `must_apply`, one `may_apply`, zero
evidence gaps in `must_apply` clauses, zero blocking gaps, and exit code zero.

## Risks / Rollback

Risk is moderate because the transaction mutates three canonical artifact
families. Full prevalidation, one database transaction, append-only versions,
readback, idempotency, and injected-failure coverage contain that risk.

Rollback is a governed revert of only the four implementation targets. MemBase
history created by a successfully verified production invocation is
append-only and must be corrected through later governed versions, not deleted.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py`
- `groundtruth-kb/src/groundtruth_kb/db.py`
- `platform_tests/scripts/test_cli_backlog_add_work_item.py`
