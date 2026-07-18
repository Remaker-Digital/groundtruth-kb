NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder

# Implementation Proposal - Emit the complete modernization non-impairment disposition schema in proposal generators

bridge_kind: prime_proposal
Document: gtkb-wi5294-proposal-generator-nonimpairment-schema
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5294

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py", "groundtruth-kb/tests/test_cli_bridge_propose.py"]

implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Make both canonical proposal generators emit the complete current structured
`Intuitiveness/Non-Impairment Disposition` schema. The dispatchable
`file-implementation-proposal` path must generate concrete values that pass the
same compliance gate it invokes. The non-dispatchable `bridge propose` draft
path must seed every required field with explicit fill-in placeholders so an
author sees the full contract before attempting to file.

## Claim

WI-5294 is the narrow root repair for repeated fail-closed proposal filing.
Current dry runs for WI-5437 and WI-5334 pass applicability and clause
preflights, but live filing creates no bridge file because
`proposal_filing._build_content` omits the structured disposition while linking
`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`. Repairing the two canonical
generators once is safer and more complete than hand-authoring dependent
proposals around the missing schema.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
already defines the mandatory structured disposition, and the bridge compliance
gate is the executable schema authority. This proposal aligns the generators
with that existing contract; it does not weaken, bypass, or replace the gate.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5294, the active Authority Foundations project authorization, and the canonical NONIMPAIRMENT_REQUIRED_FIELDS contract in .claude/hooks/bridge-compliance-gate.py",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 plus the canonical bridge compliance gate schema and tests",
  "primary_route": "gt bridge file-implementation-proposal for dispatchable proposals and gt bridge propose for non-dispatchable drafts",
  "before_behavior": "Both generators omit the structured disposition; cross-cutting live filings fail only after otherwise successful preflights, and drafts do not reveal the complete required schema.",
  "after_behavior": "The live generator emits one concrete schema-valid disposition and the draft generator emits every schema key with explicit fill-in values that remain non-dispatchable until completed.",
  "self_descriptive_naming": "Generator helpers and test names use nonimpairment_disposition terminology and the exact canonical field names.",
  "obsolete_guidance_disposition": "No historical bridge record is rewritten; generated proposals cease relying on incomplete free-form guidance and use the current structured schema.",
  "history_preservation": "Existing bridge files and prior failed filing evidence remain append-only; this repair changes only future generated content.",
  "baseline": {
    "required_field_count": 15,
    "wi5437": "candidate preflights pass and live filing fails with section absent",
    "wi5334": "candidate preflights pass and live filing fails with section absent"
  },
  "expected_result": {
    "dispatchable": "A complete generated cross-cutting proposal passes the in-memory compliance audit and is filed exactly once.",
    "draft": "The draft contains schema_version plus all 15 mandatory fields and remains visibly incomplete until author judgment replaces placeholders.",
    "gate": "Missing, malformed, duplicate, empty, or placeholder disposition values continue to fail closed."
  },
  "rollback": "Revert only the four source and test files; never delete or rewrite bridge history created before or after the repair.",
  "hard_invariants": [
    "No bridge compliance rule is relaxed.",
    "No proposal is filed before credential, author metadata, applicability, clause, and compliance checks pass.",
    "No dispatcher, TAFE, harness, eligibility, role, Git index, commit, push, deployment, or credential state changes."
  ],
  "fail_closed_conditions": [
    "The canonical required-field set cannot be loaded or represented.",
    "Generated live values are empty, placeholders, malformed JSON, or schema-version incompatible.",
    "Candidate or live applicability and clause preflights fail.",
    "The target bridge file already exists or author metadata is unavailable."
  ],
  "essential_context_preservation": "Generated proposals retain project authorization, work-item linkage, target paths, requirement sufficiency, specification links, prior deliberations, owner decisions, verification mapping, acceptance criteria, risks, rollback, and file scope."
}
```

## In-Root Placement Evidence

- `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py` is inside `E:/GT-KB` and is the canonical dispatchable proposal filing service.
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py` is inside `E:/GT-KB` and is the canonical non-dispatchable proposal draft service.
- `platform_tests/groundtruth_kb/test_cli_bridge_propose.py` is inside `E:/GT-KB` and tests the live filing service.
- `groundtruth-kb/tests/test_cli_bridge_propose.py` is inside `E:/GT-KB` and tests the draft service.
- No application, external, credential, dispatcher, TAFE, harness, or bridge-history target is in scope.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - defines the structured disposition and fail-closed non-impairment contract.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - generated proposals must be mechanically evaluable before filing.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the bridge helper remains the governed publication route.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - generated proposals retain PAUTH, project, and work-item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - generated proposals retain concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation and verification remain mapped to governing specifications.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the generator exposes the durable artifact contract at authoring time.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - drafts remain non-dispatchable and live proposals remain review-gated.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the work item and proposal preserve traceable lifecycle evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation remains behind the active project PAUTH, independent GO, claim, and start packet.

## Prior Deliberations

- `DELIB-202666274` - owner-authorized project-level modernization implementation authority while preserving bridge and mechanical gates.
- `DELIB-S334-BOUNDED-KNOWLEDGE-COMPLEXITY-OWNER-DECISION` - proposals should expose bounded, discoverable context rather than requiring authors to discover hidden fields through failed writes.
- `DELIB-2708` - prior bridge-propose review required managed scaffold/template surfaces to stay aligned with live helper behavior.

## Owner Decisions / Input

- `DELIB-202666274` authorizes the Authority Foundations project scope without waiving independent GO, implementation-start, or VERIFIED.
- Owner directive: work authorization is project-scoped rather than per-work-item, subject to the listed mechanical exceptions.
- Owner directive: CLI inadequacy must be handled as a work item through the bridge, not bypassed.
- Owner directive: flaws and omissions must be added to the hygiene backlog and work should continue where possible.

## Proposed Scope

- Add one canonical disposition-builder representation shared or mirrored by the two generator paths without weakening the compliance gate.
- Make `file-implementation-proposal` emit exactly one fenced JSON object containing `schema_version: 1`, `applicability`, and every field in the canonical required set with concrete request-derived values.
- Make `bridge propose --kind implementation` expose the same complete field set with explicit author-fill placeholders in its non-dispatchable draft.
- Add tests that compare both generated surfaces to the canonical field contract and prove the live body passes the non-impairment audit when complete.
- Add tests proving draft placeholders remain visible and incomplete content still fails closed.
- Preserve current project linkage, specification autoload, requirement sufficiency, prior deliberation, owner-decision, credential scan, author metadata, and preflight behavior.
- Do not mutate the compliance hook, dispatcher, TAFE, harness state, eligibility, bridge history, Git index, commits, deployment, release, or credentials.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Assert both generators contain schema version 1 and the exact canonical 15-field set; run the compliance gate against a complete live-generated body and incomplete draft variants. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Prove generated JSON parses deterministically and candidate/live preflights evaluate the generated proposal without manual field discovery. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run existing bridge proposal CLI tests and confirm publication still uses the governed writer with no direct bridge write path. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Retain and assert PAUTH, Project, Work Item, and inline target_paths metadata. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Retain the existing generated specification-link assertions and add the non-impairment governing spec assertion. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the two focused proposal-generator test modules and report exact results in the implementation report. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Assert the non-dispatchable draft exposes the complete durable decision schema before filing. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Prove dry-run writes nothing, draft mode writes only under `.gtkb-state`, and live mode writes only after all gates pass. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Confirm work-item, project, owner-decision, prior-deliberation, and verification sections remain present. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Validate the implementation-start gate against the exact four target paths before any protected mutation. |

## Acceptance Criteria

- `gt bridge file-implementation-proposal` can file a complete cross-cutting modernization proposal without a `section absent` non-impairment failure.
- `gt bridge propose --kind implementation` emits `schema_version` and every canonical required field with explicit fill-in values.
- The focused live-filer and draft-generator tests pass, including exact field-set parity and fail-closed incomplete-content cases.
- Ruff check and format checks pass on all four files.
- Candidate and live applicability and ADR/DCL preflights pass with no missing required specifications.
- No unrelated worktree bytes, bridge history, dispatcher/TAFE/harness state, eligibility, roles, Git index, commits, pushes, deployments, releases, or credentials are changed.

## Risks / Rollback

Risk is moderate because proposal generation is a governance gate entrypoint.
The primary risks are schema drift between the hook and generators, accidentally
turning draft placeholders into filing-valid values, or generating vague values
that technically parse but do not preserve author judgment. Tests must compare
the exact field set and exercise the same audit code used during filing.

Rollback is a revert of only the four source and test files. Existing bridge
files are append-only and must not be deleted or rewritten.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py`
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`
- `platform_tests/groundtruth_kb/test_cli_bridge_propose.py`
- `groundtruth-kb/tests/test_cli_bridge_propose.py`

## Recommended Commit Type

`fix`
