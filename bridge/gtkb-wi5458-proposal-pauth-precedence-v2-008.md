GO
::init gtkb lo
::open test
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fac54-c55c-75c0-8332-d7fdaf03b20a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; transcript-resolved Loyal Opposition role; test activity
author_metadata_source: session envelope (worker_role_provenance)

# WI-5458 v2 Validated PAUTH Selection and Currentness — GO

bridge_kind: lo_verdict
Document: gtkb-wi5458-proposal-pauth-precedence-v2
Version: 008
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5458-proposal-pauth-precedence-v2-007.md
Reviewed proposal: bridge/gtkb-wi5458-proposal-pauth-precedence-v2-007.md

## Verdict Summary

**GO.** Version 007 closes the controlling version-006 authorization-coverage
defect without widening its three-file scope. The required restrictive
`included_work_item_ids` truth table now applies before ranking in automatic
and explicit selection modes, and the proposal maps each governing constraint
to discriminating tests.

## Finding Closure

| Finding | Result | Evidence |
| --- | --- | --- |
| Version-006 restrictive work-item coverage | Closed | One shared predicate enforces exclusion dominance; non-empty inclusion covers exactly listed work items without membership; only an empty list uses active-membership fallback. |
| Selection-path parity | Closed | Automatic and explicit modes share the predicate and carry the listed/nonmember, unlisted/member, empty-list/member, empty-list/nonmember, and exclusion matrices. |
| Denial side effects | Closed | Every denying branch is required to occur before membership, PAUTH, claim, packet, preflight, writer, or filesystem mutation. |
| Currentness/ranking safety | Closed | The best specificity cohort is fixed before stale pruning, with a global denial when that cohort empties rather than lower-rank broadening. |

The exact WI-5458 PAUTH is active and bounded to the declared source, CLI, and
test targets. The current focused baseline reports `20 passed` with only the
pre-existing pytest configuration warning. No protected implementation has
begun.

## Implementation Conditions

This GO authorizes only the three `target_paths` declared in version 007.
Before protected edits, the Prime Builder must acquire a fresh exact-session
claim and implementation-start packet, then re-evaluate the live collision set
for the overlapping WI-5560 GO thread as version 007 requires. Any newly
affected undeclared target or authorization drift requires re-filing rather than
in-place scope expansion.

## Non-Blocking Observation

`DELIB-20264663` is described in the proposal as authorization-currentness
support, although its archive content concerns project VERIFIED-completion
handling. The directly relevant DCL, the controlling predecessor verdict, and
the explicit currentness test matrix independently ground this proposal, so the
citation label does not block GO. Correct the citation description in the
implementation report or a later governed documentation pass.

## Prior Deliberations

- `DELIB-20266083` — owner decision establishing restrictive
  `included_work_item_ids` semantics used by the revised predicate.
- `DELIB-20263760` — prior Loyal Opposition review on project-membership
  validation posture.
- `DELIB-20264465` — validate candidate state before durable write.

No deliberation contradicts the bounded fail-closed design.

## Review Independence

Version 007 declares author session
`019f9329-a174-7763-8f7e-29679f39e6bd`; this Loyal Opposition review uses
`019fac54-c55c-75c0-8332-d7fdaf03b20a`. Author metadata is readable and the
session contexts are distinct.

## Methodology Trail

Read the numbered bridge chain through versions 001–007. Reviewed the shared
coverage predicate and target test matrix, verified the active bounded PAUTH
and focused baseline, ran both mandatory preflights, and searched the
Deliberation Archive for PAUTH inclusion and membership decisions. No protected
source, configuration, dispatcher, or external system was changed.

## Applicability Preflight

- packet_hash: `sha256:97145cf50640b8e84379be47ac152df47d954fa0c05ba4d5f3e483c34984e40d`
- bridge_document_name: `gtkb-wi5458-proposal-pauth-precedence-v2`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-007.md`
- operative_file: `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-007.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- candidate_evidence_hash: `sha256:de1edd694a2bc838257ed73eec3d2c04865c2141c114422e84880fef53c949b8`

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5458-proposal-pauth-precedence-v2`
- Operative file: `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-007.md`
- Clauses evaluated: 5
- must_apply: 3; may_apply: 2; not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Mandatory clause preflight exit: `0`

| Clause | Applicability | Evidence |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | must_apply | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes |

## Owner Decision / Input

No owner action is required. The governing inclusion semantics and bounded
PAUTH authority are already recorded; implementation remains subject to the
fresh claim and implementation-start gates.
