NEW
::init gtkb lo
::open build

# gtkb-wi5476-related-work-item-collision-classification - Distinguish governed relationships from WI collisions

bridge_kind: prime_proposal
Document: gtkb-wi5476-related-work-item-collision-classification
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5476-RELATED-WI-COLLISION-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5476
Related Work Items: WI-5474

target_paths: ["scripts/bridge_proposal_wi_id_collision_check.py", "platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py", "platform_tests/hooks/test_bridge_proposal_wi_id_collision_gate.py"]

implementation_scope: source | test | bridge proposal diagnostics
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Teach the advisory bridge proposal work-item collision checker to distinguish
validated `Related Work Items` metadata from accidental foreign work-item
references. Today any existing work-item ID other than the declared
`Work Item:` is reported as a collision. That makes a proposal with an
intentional predecessor or dependency look the same as one that accidentally
cites the wrong implementation carrier.

The defect reproduced while validating WI-5474. Its proposal intentionally
relates WI-5362, which exposed the missing restore operation, and WI-5421,
which owns the predecessor Git lifecycle baseline. The checker labels both as
collisions even when they are declared on the established
`Related Work Items:` line. The hook is advisory, but a warning that fires on
correct metadata trains authors and reviewers to ignore the warning that
should identify a genuine identity collision.

## Scope

Limit the correction to the existing deterministic checker and two additive
focused test modules. The PreToolUse hook source remains unchanged because it
already consumes the checker's result and formatter. No bridge file parser,
proposal writer, dispatcher, TAFE, runtime, claim, lease, eligibility,
harness, credential, Git, deployment, release, or external-system behavior is
modified.

## Implementation

- Parse the established case-sensitive metadata forms:
  `Related Work Items: WI-1234, WI-1235` and
  `related_work_items: ["WI-1234", "WI-1235"]`.
- Accept only canonical `WI-[0-9]+` values. Preserve declaration order for
  diagnostics while comparing normalized sets for consistency.
- When both forms are present, require identical sets. Empty values,
  malformed JSON, non-string members, duplicates, the declared work item
  itself, unknown MemBase IDs, or contradictory sets produce explicit
  relationship errors and cannot suppress collision findings.
- Classify each cited ID as the declared work item, a validated related work
  item, an actionable collision, or an unknown non-MemBase reference.
  Existing foreign IDs outside validated relationship metadata remain
  collisions exactly as today.
- Preserve the existing `declared_work_item`, `cited_ids`, `collisions`, and
  `has_collisions` result contract. Add deterministic relationship records and
  relationship errors without changing the meaning of existing collision
  fields.
- Make strict mode exit nonzero when an actionable collision or relationship
  error exists. A proposal containing only the declared work item and valid
  related IDs exits zero.
- Format validated relationships and actionable collisions separately. The
  hook emits no warning for valid related-only content and, when an extra
  collision exists, identifies only that collision as actionable while
  retaining related-work context.
- Keep the checker and hook read-only. MemBase lookup validates identity but
  creates no work item, relationship, bridge, cache, or runtime state.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires bridge proposal diagnostics to preserve the numbered-file authority model and remain non-mutating context rather than alternate queue state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires proposal identity and related-work diagnostics to remain precise enough for mechanical specification linkage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - preserves the singular declared implementation work item while allowing separately classified relationship context.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires TEST-11573 and both focused test modules to execute before independent VERIFIED.
- `GOV-STANDING-BACKLOG-001` - requires every validated related ID to resolve against current MemBase rather than free-form Markdown alone.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires a more actionable warning without weakening fail-closed handling of malformed or ambiguous metadata.
- `GOV-WORK-TREE-HYGIENE-001` - requires the correction to leave unrelated dirty work and bridge content untouched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - keeps the validator finding, WI-5476, TEST-11573, proposal, implementation evidence, and verdict as durable linked artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires the relationship classification and exact observed false positive to remain reconstructable.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps proposal filing, implementation, report, independent verification, and finalization as distinct transitions.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes bounded PAUTH carriers and governed proposals for newly discovered bridge, TAFE, dispatcher, and harness defects or enhancements while preserving every later gate.
- WI-5474 - provides the concrete related-predecessor proposal that reproduced the false-positive classification without any live bridge or target mutation.

## Owner Decisions / Input

No new owner decision is required.
`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes this
bounded enhancement carrier. Active singleton authorization
`PAUTH-DISPATCHER-BLACK-BOX-WI5476-RELATED-WI-COLLISION-20260717` includes
only WI-5476, the five PAUTH specifications, and the three declared targets.
It permits proposal filing now and protected source/test implementation only
after independent GO, an exact claim, and implementation-start authorization.

## Requirement Sufficiency

Existing requirements sufficient. The bridge project-linkage contract already
distinguishes one declared implementation work item, while the repository has
an established `Related Work Items` metadata surface for contextual
relationships. The defect is that the advisory checker ignores that explicit
metadata. No new authority, role, lifecycle, or work-item relationship policy
is required.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5476; TEST-11573; deterministic validation of the WI-5474 proposal",
  "canonical_authority": "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001; DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001; GOV-FILE-BRIDGE-AUTHORITY-001",
  "primary_route": "scripts/bridge_proposal_wi_id_collision_check.py and the existing advisory PreToolUse hook",
  "before_behavior": "Every existing foreign work-item ID is labeled a collision even when declared in established Related Work Items metadata",
  "after_behavior": "Validated related IDs are reported as relationship context, while only undeclared existing foreign IDs and invalid relationship metadata are actionable",
  "self_descriptive_naming": "related_work_items, validated_related_ids, relationship_errors, and collisions expose distinct classes",
  "obsolete_guidance_disposition": "No alternate checker or suppression list is created; the existing checker gains the missing classification",
  "history_preservation": "Proposal text, bridge files, work items, tests, hook payloads, and prior warning evidence remain unchanged",
  "baseline": "WI-5474 declares WI-5362 and WI-5421 as related predecessors and the current checker reports both as collisions",
  "expected_result": "The same proposal reports two validated relationships and zero collisions; adding one undeclared existing WI produces exactly one collision and strict nonzero exit",
  "rollback": "A separately governed focused revert removes only WI-5476 source and additive tests",
  "hard_invariants": "Never infer relationships from free-form prose; never suppress unknown or malformed metadata; never mutate MemBase, bridge, dispatcher, TAFE, runtime, harness, Git, credential, external, deployment, or release state",
  "fail_closed_conditions": "Malformed JSON, invalid ID shape, unknown related ID, self-reference, duplicate ID, contradictory metadata forms, or an undeclared existing foreign ID prevents a clean strict result",
  "essential_context_preservation": "Output retains the declared WI, every cited ID, validation source, normalized related set, relationship errors, actionable collision set, and stable exit behavior"
}
```

## Spec-Derived Verification Plan

`TEST-11573` and the focused tests must demonstrate:

| Governing requirement | Verification | Expected result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run the checker and hook against temporary proposal content without writing a bridge file. | Diagnostics are read-only and do not become queue, status, or relationship authority. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Test one declared WI, valid human-readable metadata, valid JSON metadata, both matching, and one extra existing foreign ID. | The declared WI remains singular; valid relationships are separate; the extra ID alone is a collision. |
| `GOV-STANDING-BACKLOG-001` | Seed or point tests at an isolated MemBase fixture containing declared, related, and foreign IDs. | Only current known IDs can become validated relationships; unknown metadata fails closed. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Test malformed JSON, non-string members, duplicates, self-reference, contradictory forms, strict exit, JSON output, Markdown output, and hook context. | Every metadata ambiguity is actionable; valid related-only content is quiet; adding a collision produces one precise warning. |
| `GOV-WORK-TREE-HYGIENE-001` | Fingerprint proposal and repository fixture files around checker and hook execution. | No file, index, bridge, cache, or MemBase mutation occurs. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Inspect WI-5476, TEST-11573, PAUTH, bridge chain, implementation-start packet, report, verdict, and focused commit. | The false-positive provenance and corrected classification remain reconstructable through distinct governed states. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run both focused test modules, Ruff check/format, `py_compile`, proposal preflights, and `git diff --check`. | All mapped cases pass before independent VERIFIED. |

Required command evidence:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py platform_tests/hooks/test_bridge_proposal_wi_id_collision_gate.py -q --no-header --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_proposal_wi_id_collision_check.py platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py platform_tests/hooks/test_bridge_proposal_wi_id_collision_gate.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/bridge_proposal_wi_id_collision_check.py platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py platform_tests/hooks/test_bridge_proposal_wi_id_collision_gate.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile scripts/bridge_proposal_wi_id_collision_check.py platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py platform_tests/hooks/test_bridge_proposal_wi_id_collision_gate.py
git diff --check -- scripts/bridge_proposal_wi_id_collision_check.py platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py platform_tests/hooks/test_bridge_proposal_wi_id_collision_gate.py
```

## Acceptance Criteria

- Valid `Related Work Items:` and `related_work_items:` metadata classify
  known foreign IDs as relationships, not collisions.
- Both metadata forms may coexist only when their normalized sets agree.
- Malformed, empty, unknown, self, duplicate, non-string, or contradictory
  relationship metadata is explicit and makes strict mode fail.
- Existing foreign IDs outside validated metadata remain actionable
  collisions, and unknown free-form IDs cannot be promoted to relationships.
- Existing result fields remain backward-compatible. New JSON and Markdown
  fields separate validated relationships, relationship errors, and
  actionable collisions deterministically.
- The existing hook emits no context for related-only content and emits one
  focused warning when an undeclared collision or relationship error exists.
- Checker and hook execution remain read-only and all focused checks pass.

## Risk / Rollback

The main risk is over-classifying free-form references as relationships and
thereby hiding a real wrong-WI proposal. The implementation therefore trusts
only exact anchored metadata, validates every related ID against MemBase, and
keeps ambiguity actionable. A secondary risk is breaking existing consumers
of the result object; existing fields and collision semantics remain intact,
with additive relationship fields and tests for both JSON and Markdown output.

Rollback is a separately governed focused revert of the WI-5476 source hunk
and two additive tests. It does not rewrite any proposal, bridge chain,
work-item record, or prior warning evidence.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5476-related-work-item-collision-classification`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(bridge)`: this removes a deterministic false-positive class from an
existing bridge proposal diagnostic while retaining fail-closed collision
behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
