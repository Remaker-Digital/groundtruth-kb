REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; bounded WI-5282 revision; dispatcher and TAFE deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

# Revised Implementation Proposal - WI-5282 PAUTH owner-decision evidence gate

bridge_kind: prime_proposal
Document: gtkb-wi5282-pauth-owner-decision-evidence-gate
Version: 009
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5282-pauth-owner-decision-evidence-gate-008.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5282

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_project_authorization.py", "platform_tests/scripts/test_cli_backlog_authorize_implementation.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Restore the still-open P0 WI-5282 implementation proposal under the current
project authorization. The implementation will reject non-owner deliberations
before any PAUTH append, accept canonical owner decisions, expose a read-only
invalid-evidence audit/quarantine classification, and preserve the existing
`gt backlog authorize-implementation` fail-closed contract.

This revision does not implement, resolve, close, revoke, or rewrite a PAUTH.
No KB mutation occurs in this proposal. Implementation may begin only after an
independent GO, a matching current-session claim, and a successful schema-v3
implementation-start packet for these exact five targets.

## Findings Addressed

### Finding 1 - Complete specification-derived verification evidence

Response: this revision restores
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` and the three advisory
artifact-oriented-governance citations omitted by v007. The concrete
spec-to-test mapping below covers rejection before write, canonical owner
acceptance, read-only audit/quarantine behavior, append-only preservation, and
both project and backlog CLI regressions.

### Finding 2 - Replace the revoked project authorization

Response: the operative authorization is now the list-free, active, unexpired
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715` v1.
Its `included_work_item_ids` and `excluded_work_item_ids` are both null, so
active direct project membership covers WI-5282. It allows `source` and `test`
mutations and forbids dispatcher mutation, external-system mutation,
credentials, destructive cleanup, commit/history rewrite, push, deployment,
and release. The v001/v007 authorization ending in `-PROJECT-SCOPE` is revoked
v3 and is not cited as current authority.

The replacement PAUTH cites
`DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION`, whose canonical
record is `source_type=owner_conversation`, `outcome=owner_decision`. Legacy
WI-5282 `approval_state=unapproved` is noncontrolling under the owner's
project-level inheritance decision; it is not used as an implementation gate.

### Finding 3 - Restore a current target-bound implementation proposal

Response: the original five in-root targets are restored unchanged. All five
are tracked and clean at proposal currentness review. No active WI-5282 claim
or foreign live-claim overlap existed before drafting; Prime Builder acquired
the required draft claim for this exact thread. Operation-time authority must
be evaluated again after a new independent GO and before any target mutation;
this proposal itself supplies no start packet or source authority.

## Requirement Sufficiency

Existing requirements sufficient. WI-5282 and the linked current
specifications already define the defect and the fail-closed, append-only,
spec-derived acceptance boundary. This revision introduces no new formal
requirement and does not amend project scope.

## In-Root Placement And Currentness Evidence

All declared targets are within `E:\GT-KB`, tracked, and clean. Current
worktree SHA-256 values at audit time were:

| Target | Worktree SHA-256 |
| --- | --- |
| `groundtruth-kb/src/groundtruth_kb/db.py` | `F30A24F1785B23BBDF70BAB6AF9958F49FD40B1EB285BD31D598A12E99D506F7` |
| `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` | `025984E09244F1CBD5D09DF3E756DFF3FF66E65CF49E4ABB521F6F126703CDBE` |
| `groundtruth-kb/src/groundtruth_kb/cli.py` | `CE2C2942F75C22101D9B17E77E9D1EA1F7E27892F272073C9A0C48B51A75C853` |
| `platform_tests/scripts/test_project_authorization.py` | `71C9B91EAE79D0B8AA9BDA4C9A7C8850D8F649D78A7153620DE2452215975DFF` |
| `platform_tests/scripts/test_cli_backlog_authorize_implementation.py` | `7A35AEC53BD4C8373113BB6126AEC497F5FE42823D66474199C0D8B81DD951B2` |

Before implementation, Prime Builder must repeat the exact-path clean/current
hash check, claim/overlap check, project/PAUTH readback, applicability and
clause gates, and schema-v3 implementation-start validation. Drift fails
closed and returns the thread for revision or sequencing.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires bounded active project authority and owner evidence for PAUTH creation.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires current PAUTH evaluation at the operation boundary.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires deterministic evaluation of PAUTH evidence and state.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct append-only bridge authority.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires exact project, PAUTH, work item, and target metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires complete governing specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed specification-derived verification evidence.
- `GOV-ARTIFACT-APPROVAL-001` - constrains formal PAUTH creation and mutation to valid approval evidence.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires intuitive behavior and preservation of valid authorization flows.
- `SPEC-AUQ-POLICY-ENGINE-001` - governs canonical owner-input evidence and fail-closed decision handling.
- `GOV-STANDING-BACKLOG-001` - preserves WI-5282's MemBase backlog authority and lifecycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires durable governed lifecycle evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves artifact-oriented, append-only correction semantics.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires the PAUTH defect to proceed through the governed artifact lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps the platform authorization service out of adopter application scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - preserves cross-harness enforcement expectations for governed writes.

## Prior Deliberations

- `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION` - canonical owner-conversation/owner-decision evidence for the active list-free project PAUTH.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` - direct project PAUTH, not legacy work-item approval state, controls implementation approval.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` - project-scoped approval does not waive proposal, GO, claim, packet, report, or verification gates.

## Owner Decisions / Input

- The owner approved project-level implementation authorization inheritance for
  all active direct member WIs and explicitly pulled that governance change
  forward. WI-5282 is an active direct member of the active Authority
  Foundations project.
- Active authorization
  `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715`
  records the bounded project approval backed by
  `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION`.
- No new owner approval is required to file this bounded revision. Every normal
  implementation and independent-review gate remains mandatory.

## Proposed Scope

1. Add one shared owner-decision-evidence validator in the project
   authorization data/service path. For creation and any authorization version
   that changes `owner_decision_deliberation_id`, require a current canonical
   deliberation whose `source_type=owner_conversation` and
   `outcome=owner_decision`, unless a future governed specification explicitly
   registers another equivalent. Reject missing, reviewer-authored,
   bridge-thread, GO, NO-GO, deferred, informational, or superseded evidence
   before opening the PAUTH append transaction.
2. Invoke the shared validator from `gt projects authorize` through the
   lifecycle/data path and preserve typed, exact denial text. Validation failure
   must append no PAUTH row and create no completion guard or other side effect.
3. Preserve `gt backlog authorize-implementation` behavior by ensuring its
   existing and fresh-AUQ paths reach the same shared validator. Fresh AUQ
   evidence remains valid only after its canonical owner-conversation,
   owner-decision deliberation is recorded by that governed command.
4. Extend the read-only project-authorization listing/audit surface to report
   active authorizations whose cited deliberation fails the shared predicate.
   Mark the returned classification as `quarantine_required` with the exact
   reason and governed-reissue route. The audit must not revoke, supersede,
   rewrite, repair, or append PAUTH or deliberation rows.
5. Preserve every historical authorization version and current valid
   authorization path. Existing invalid active records remain visible as
   append-only evidence pending separately governed reissue; this slice does
   not automatically change their status.

## Explicit Non-Scope

- No automatic revocation, supersession, rewrite, migration, deletion, or
  reissue of existing PAUTH or deliberation records.
- No direct SQLite access or ad hoc database mutation outside the canonical
  service path.
- No change to project membership, project status, PAUTH records, work-item
  status, dispatcher/TAFE state, harness configuration, credentials, Git
  history, deployment, release, or external systems.
- No widening beyond the five declared targets and no weakening of exact GO,
  claim, operation-time authorization, schema-v3 packet, report, independent
  verification, or separately governed finalization gates.

## Specification-Derived Verification Plan

| Requirement | Concrete test or command | Required observation |
| --- | --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `GOV-ARTIFACT-APPROVAL-001`; `SPEC-AUQ-POLICY-ENGINE-001` | Add project-service/CLI tests using a `source_type=bridge_thread`, `outcome=no_go` deliberation and invoke `gt projects authorize`. | Typed rejection names the invalid provenance before mutation; PAUTH row count and completion-guard count remain unchanged. |
| Same requirements | Add positive tests with `source_type=owner_conversation`, `outcome=owner_decision`. | `gt projects authorize` succeeds and records the exact owner decision while preserving normal PAUTH fields. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Exercise create and owner-decision-changing amendment paths with valid and invalid evidence. | Every operation re-evaluates current deliberation semantics; invalid evidence produces no new authorization version. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Add read-only audit/list tests containing valid and invalid active PAUTH fixtures. | Invalid rows report `quarantine_required` plus reason/reissue route; database content and version counts are byte/row-count unchanged after audit. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; `SPEC-AUQ-POLICY-ENGINE-001` | Extend `platform_tests/scripts/test_cli_backlog_authorize_implementation.py` for existing valid owner evidence, fresh AUQ evidence, invalid reviewer verdict evidence, and dry-run. | Valid existing and fresh-AUQ routes still succeed; invalid evidence and dry-run remain fail-closed/no-write. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `GOV-FILE-BRIDGE-AUTHORITY-001` | Run applicability and mandatory clause preflights against the exact candidate and filed v009. | Missing required/advisory specs and blocking clause gaps are all empty. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_cli_backlog_authorize_implementation.py -q --tb=short` | Focused project and backlog authorization suites pass, with executed results recorded in the implementation report. |
| Python quality and importability | `python -m ruff check <changed Python targets>`; `python -m ruff format --check <changed Python targets>`; `python -m py_compile <changed source targets>` | All commands exit 0 against the exact changed files. |

The implementation report must record the pre/post PAUTH row/version counts for
negative and read-only audit cases, exact commands, observed results, final
target hashes, and a complete linked-spec-to-executed-test map. Assertions that
only inspect exception text without proving no append are insufficient.

## Acceptance Criteria

- `gt projects authorize` rejects a bridge-thread/NO-GO deliberation as owner
  evidence before any PAUTH or completion-guard append.
- Canonical owner-conversation/owner-decision evidence remains accepted.
- Any authorization version that changes owner-decision evidence applies the
  same current-provenance predicate and fails without a new version on invalid
  evidence.
- The read-only audit/list surface reports invalid active PAUTH evidence with
  `quarantine_required`, exact reason, and governed-reissue guidance while
  making no KB change.
- Existing invalid history remains append-only and visible; no automatic
  revoke, rewrite, supersession, or reissue occurs.
- `gt backlog authorize-implementation` valid existing-decision and fresh-AUQ
  paths continue to pass; invalid reviewer-verdict evidence remains rejected
  before authorization mutation.
- Focused tests, lint, format, compile, applicability, and clause gates pass and
  are reported with observed results before independent verification.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "primary_route": "Use one shared canonical owner-decision provenance validator for project and backlog authorization paths before any PAUTH append.",
  "baseline": "The project authorization writer accepts an existing deliberation identifier without proving canonical owner-conversation and owner-decision semantics; invalid active rows can be inventoried only through ad hoc analysis.",
  "before_behavior": "A reviewer-authored bridge-thread NO-GO deliberation can be supplied as PAUTH owner-decision evidence, and callers lack one read-only typed quarantine classification for invalid active evidence.",
  "after_behavior": "Both authorization routes reject non-owner evidence before mutation, accept canonical owner decisions, and expose a read-only quarantine-required audit result without rewriting append-only history.",
  "canonical_authority": "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, GOV-ARTIFACT-APPROVAL-001, SPEC-AUQ-POLICY-ENGINE-001, and the active Authority Foundations project PAUTH.",
  "essential_context_preservation": "Preserve valid project and backlog authorization flows, every historical PAUTH version, exact owner-decision identifiers, project membership, independent bridge review, claim, schema-v3 start, implementation-report, and verification gates.",
  "obsolete_guidance_disposition": "The revoked PROJECT-SCOPE PAUTH is retained only as history and is not treated as current authority; no command or valid evidence route is retired by this proposal.",
  "history_preservation": "All PAUTH, deliberation, backlog, bridge, claim, packet, report, and verdict history remains append-only; invalid active evidence is reported for governed reissue and is never rewritten automatically.",
  "provenance": "WI-5282, active direct Authority Foundations membership, PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715 v1, DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION, physical bridge versions 001-008, and the exact five-target currentness cohort.",
  "self_descriptive_naming": "Owner-decision evidence validator, quarantine_required classification, rejection-before-write results, and governed-reissue guidance name the rule and outcome directly across service and CLI surfaces.",
  "expected_result": "Focused service and CLI tests prove typed rejection before append, canonical owner-decision acceptance, read-only quarantine reporting, no-write negative paths, and unchanged valid backlog authorization behavior.",
  "hard_invariants": [
    "No invalid owner-decision evidence creates a PAUTH version or completion guard.",
    "No read-only audit revokes, supersedes, rewrites, repairs, or appends authorization or deliberation state.",
    "No implementation target outside the exact five-path cohort is changed.",
    "Dispatcher, TAFE, credential, deployment, release, push, history rewrite, and destructive cleanup remain out of scope."
  ],
  "fail_closed_conditions": [
    "The deliberation is missing, noncurrent, or lacks canonical owner-conversation and owner-decision provenance.",
    "The active direct project, list-free PAUTH, exact target hashes, claim, overlap, applicability, clause, or schema-v3 start gates drift.",
    "A negative-path test cannot prove PAUTH and completion-guard row counts are unchanged.",
    "The audit path would mutate or obscure historical authorization evidence."
  ],
  "rollback": "Revert only the separately approved five-target source/test implementation; never delete or rewrite bridge, PAUTH, deliberation, or backlog history."
}
```

The same concept—owner-decision evidence—has one predicate across project and
backlog authorization routes. Rejections state the observed source type and
outcome plus the required provenance. The audit explains why a row is
quarantined and how governed reissue occurs, without silently changing history.
No valid command is renamed or removed, and JSON output remains deterministic.

## Risks / Rollback

The main risk is rejecting a historically accepted but non-owner deliberation
that callers treated as sufficient. This is the intended fail-closed change;
tests must distinguish canonical owner evidence from reviewer verdicts and
prove the rejection occurs before append. A second risk is an audit that
accidentally mutates or obscures historical state; row/version-count assertions
and explicit read-only implementation prevent that.

Rollback reverts only the approved source/test changes through a separately
governed change. It never deletes bridge versions, PAUTH versions,
deliberations, or other audit history. After rollback, rerun the focused suites
and preflights and report the restored behavior.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_project_authorization.py`
- `platform_tests/scripts/test_cli_backlog_authorize_implementation.py`

## Recommended Commit Type

`fix`
