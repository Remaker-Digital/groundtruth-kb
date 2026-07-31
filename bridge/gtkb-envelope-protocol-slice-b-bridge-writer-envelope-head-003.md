REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: A-2026-07-17T10-20-39Z
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop interactive session; Prime Builder; approval_policy=never; session_id=A-2026-07-17T10-20-39Z

Document: gtkb-envelope-protocol-slice-b-bridge-writer-envelope-head
Version: 003
Author: Prime Builder / Codex
Date: 2026-07-17
bridge_kind: prime_proposal
implementation_scope: envelope-protocol-slice-b-bridge-writer-envelope-head
kb_mutation_in_scope: false
target_paths: ["scripts/gtkb_bridge_writer.py", "scripts/bridge_thread_files.py", ".claude/hooks/bridge-compliance-gate.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", ".codex/skills/bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/scripts/test_bridge_thread_files.py", "platform_tests/skills/test_bridge_propose_helper.py", "platform_tests/hooks/test_bridge_compliance_gate_envelope_head.py"]
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL
Work Item: WI-5374

# Revised Implementation Proposal: Envelope Protocol Slice B Bridge Writer Envelope Head

## Revision Claim

This revision responds to `bridge/gtkb-envelope-protocol-slice-b-bridge-writer-envelope-head-002.md` NO-GO.

The only blocking defect in `001` was stale sequencing evidence: it anticipated Slice A `VERIFIED` at `004` before that verdict existed. That is now corrected. Slice A is actually terminal:

```json
{
  "slice_a_latest_path": "bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-011.md",
  "slice_a_latest_status": "VERIFIED",
  "slice_a_commit": "0080b60d docs(envelope): verify slice a canonical insertion",
  "wi_5373_status": "resolved after actual independent LO VERIFIED"
}
```

This `003` revision carries forward the technical scope of `001` and changes only the baseline/provenance/order-of-work evidence required by `002`.

## Summary

Implement the Slice B bridge writer cutover for artifact-head envelope lines on new dispatchable bridge artifacts. The Body Status-Token Rule remains unchanged: the bridge status token stays on line 1. For dispatchable status-bearing artifacts whose status has a ratified responder-role mapping, the writer materializes fixed envelope lines on lines 2 and 3:

```text
<STATUS>
::init gtkb <responder-role>
::open <activity>
```

This slice does not implement packet composition, dispatcher prompt injection, session-startup loading, subject-scope enforcement, cache behavior, or cleanup. It creates the writer/gate foundation required by later slices.

## Cross-Harness Disposition

This proposal touches harness-facing bridge helper and hook surfaces. Claude and Codex bridge-propose helper behavior must remain equivalent for envelope materialization and validation. The canonical skill template must be updated with the same helper behavior so regenerated harness adapters do not regress. Weak-hook harness fallback behavior is not implemented in this slice; `DELIB-20260717-ENVELOPE-WEAK-HOOK-FALLBACK-POLICY` remains carried forward for Slice D.

## Requirement Sufficiency

Existing requirements are sufficient. Slice A inserted the canonical authority set and received independent LO `VERIFIED` at `bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-011.md`. `WI-5373` was resolved only after that VERIFIED verdict. The owner-ratified B-records plus the 2026-07-17 AskUserQuestion decisions provide the bounded operative requirements for this writer slice.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5374; bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-011.md VERIFIED; DELIB-20260717-ENVELOPE-LEGACY-ROUTING-MIGRATION-POLICY; DELIB-20260717-ENVELOPE-WEAK-HOOK-FALLBACK-POLICY; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE",
  "canonical_authority": "ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001, DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001, DCL-BRIDGE-DISPATCHER-ENVELOPE-READONLY-001, DCL-ACTIVITY-DISPOSITION-PROFILE-001, GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, and GOV-FILE-BRIDGE-AUTHORITY-001.",
  "primary_route": "Bridge GO, implementation-start packet, scoped writer/gate/helper implementation, spec-derived tests, post-implementation report, and independent Loyal Opposition VERIFIED.",
  "before_behavior": "New bridge files carry a line-1 status token and author metadata, but do not have canonical ::init or ::open artifact-head envelope lines. Readers derive actionability from the status token and legacy bridge fields.",
  "after_behavior": "New dispatchable bridge files produced by governed writers carry line-1 status, line-2 ::init gtkb responder-role, and line-3 ::open activity. Existing files without envelope lines remain grandfathered by absence and continue to route through status fallback.",
  "self_descriptive_naming": "The writer helper, compliance gate, tests, bridge slug, and work item use envelope-head or bridge-writer naming tied to Slice B.",
  "obsolete_guidance_disposition": "Historical bridge files are not rewritten. Non-dispatchable ADVISORY, DEFERRED, and WITHDRAWN role derivation remains explicitly deferred because Slice A authority does not assign responder-role mapping for those statuses.",
  "history_preservation": "All existing bridge files, Deliberation Archive records, Slice A bridge history, and MemBase authority records remain append-only. This slice ratchets new writer output only.",
  "baseline": {
    "work_item": "WI-5374 open/backlogged",
    "slice_a_terminal": "bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-011.md VERIFIED",
    "legacy_bridge_files": "grandfathered by absence"
  },
  "expected_result": {
    "new_dispatchable_files": "status token remains line 1; ::init gtkb responder-role line 2; ::open activity line 3",
    "reader_compatibility": "legacy no-envelope bridge files continue status-token fallback routing",
    "runtime_effect": "No packet composition, dispatcher prompt injection, startup loading, scope hard-block, cache, cleanup, release, credential, or external-system mutation"
  },
  "rollback": {
    "instructions": "Before VERIFIED, revert the scoped writer/gate/helper/test edits through the normal worktree and file a revised bridge report. After VERIFIED, correct through a governed follow-on bridge thread rather than rewriting bridge history.",
    "verification": "Rerun the Slice B focused pytest targets and bridge preflights after rollback or correction."
  },
  "hard_invariants": [
    "Body status token remains line 1",
    "Envelope lines occupy only fixed lines 2 and 3 for statuses with formal responder-role mapping",
    "Reader fallback preserves pre-cutover bridge files without envelope lines",
    "Slice A VERIFIED is complete before Slice B GO",
    "No implementation without independent Slice B GO and implementation-start packet",
    "No historical bridge rewrite"
  ],
  "fail_closed_conditions": [
    "Mismatched status-to-::init responder role",
    "Invalid or unknown ::open activity value",
    "Attempt to materialize envelope lines for a status without formal responder-role mapping",
    "Bridge-compliance audit denial",
    "Cross-harness helper drift not accounted for in tests"
  ],
  "essential_context_preservation": "Preserve Slice A authority IDs, owner AUQ decision IDs, PAUTH, WI-5374 linkage, and the grandfathered-by-absence migration ratchet in code comments or tests only where needed to prevent future drift."
}
```

## Owner Decisions / Input

- `DELIB-20260716-ENVELOPE-GRILL-B1-INIT-RESPONDER-SEMANTICS`: `::init` in bridge envelope lines names the responder role for the next actor.
- `DELIB-20260716-ENVELOPE-GRILL-B2-LINE-AUTHORING-AUTHORITY`: governed bridge writers own line authoring, validation, and materialization.
- `DELIB-20260716-ENVELOPE-GRILL-B3-PLACEMENT-STATUS-FIRST`: the status token stays line 1; envelope lines occupy fixed lines 2 and 3.
- `DELIB-20260716-ENVELOPE-GRILL-B9-MODERNIZATION-CHILD`: implement through the envelope protocol modernization child project.
- `DELIB-20260717-ENVELOPE-LEGACY-ROUTING-MIGRATION-POLICY`: thread ratchet after Slice B; no historical rewrite.
- `DELIB-20260717-ENVELOPE-WEAK-HOOK-FALLBACK-POLICY`: weak-hook fallback receipt/pointer policy is later-slice scope, not Slice B implementation.
- `DELIB-20260717-ENVELOPE-SLICE-A-FORMAL-PACKAGE-APPROVAL`: Slice A canonical authority package was approved and later independently VERIFIED at `bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-011.md`.

## Prior Deliberations

- `bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-011.md` - independent LO VERIFIED for Slice A.
- `bridge/gtkb-envelope-protocol-slice-b-bridge-writer-envelope-head-001.md` - original Slice B proposal.
- `bridge/gtkb-envelope-protocol-slice-b-bridge-writer-envelope-head-002.md` - NO-GO for stale Slice A baseline.
- `DELIB-20260710-GTKB-RUNTIME-CHARTER-SESSION-ROLE-ENVELOPE`
- `DELIB-20260716-ENVELOPE-GRILL-B1-INIT-RESPONDER-SEMANTICS`
- `DELIB-20260716-ENVELOPE-GRILL-B2-LINE-AUTHORING-AUTHORITY`
- `DELIB-20260716-ENVELOPE-GRILL-B3-PLACEMENT-STATUS-FIRST`
- `DELIB-20260716-ENVELOPE-GRILL-B5-PACKET-HOOK-INJECTION`
- `DELIB-20260716-ENVELOPE-GRILL-B6-TTL-STABLE-FRAME-FETCH-CACHE`
- `DELIB-20260716-ENVELOPE-GRILL-B8-SCOPE-STAGED-HARD-BLOCK`
- `DELIB-20260716-ENVELOPE-GRILL-B9-MODERNIZATION-CHILD`
- `DELIB-20260717-ENVELOPE-LEGACY-ROUTING-MIGRATION-POLICY`
- `DELIB-20260717-ENVELOPE-PACKET-BUDGET-POLICY`
- `DELIB-20260717-ENVELOPE-WEAK-HOOK-FALLBACK-POLICY`
- `DELIB-20260717-ENVELOPE-DISPATCHER-POINTER-PROMPT-SCOPE`

## Specification Links

- `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001`
- `DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001`
- `DCL-BRIDGE-DISPATCHER-ENVELOPE-READONLY-001`
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`
- `SPEC-TOPIC-ENVELOPE-ROUTER-001`
- `DCL-TOPIC-ENVELOPE-ROUTING-001`
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `.claude/rules/file-bridge-protocol.md`

## Proposed Change

1. Add a shared bridge envelope-head normalization path used by governed bridge writers before compliance audit and disk write.
2. Derive `::init gtkb lo` for `NEW`, `REVISED`, and `NO-ACTION`; derive `::init gtkb pb` for `GO`, `NO-GO`, and `VERIFIED`.
3. Materialize `::open` from the closed activity vocabulary. The default mapping for Slice B is `build` for Prime-authored implementation proposals/reports and unknown dispatchable bridge kinds, `test` for Loyal Opposition verdicts and verification responses, and an explicit caller-supplied activity when valid.
4. Validate existing envelope lines when present. Fail closed on status-role mismatch, malformed `::init`, invalid activity, or an attempt to materialize a status without formal responder-role mapping.
5. Preserve legacy fallback for pre-cutover files with no envelope lines. `scripts/bridge_thread_files.py` must continue to read line-1 status from historical files.
6. Extend bridge-compliance audit coverage so new dispatchable status-bearing bridge content is denied when required envelope lines are missing or inconsistent after this slice lands.
7. Update the canonical Claude helper, Codex helper, and skill template copy together so bridge proposal publication does not drift across harness surfaces.

Non-dispatchable `ADVISORY`, `DEFERRED`, and `WITHDRAWN` remain outside mandatory envelope materialization in this slice because the Slice A DCL responder-role table does not assign them.

## Acceptance Criteria

- New governed bridge files for statuses `NEW`, `REVISED`, `NO-ACTION`, `GO`, `NO-GO`, and `VERIFIED` carry status line 1, `::init gtkb <role>` line 2, and `::open <activity>` line 3.
- The governed writer rejects a hand-authored `::init` line whose role disagrees with the line-1 status token.
- The governed writer rejects an invalid or unknown `::open` activity.
- Bridge-compliance denies new dispatchable status-bearing bridge content that omits or contradicts the required envelope head.
- Existing bridge files without envelope lines remain readable and route by line-1 status fallback.
- Claude helper, Codex helper, and template helper behavior stay aligned or tests fail.
- No source, hook, helper, or test implementation occurs before LO `GO` and an implementation-start packet.

## Specification-Derived Verification

- `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001` -> unit tests assert canonical three-line artifact head shape and no status-token displacement.
- `DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001` -> writer tests assert status-to-responder-role mapping, fixed lines 2-3, invalid role rejection, and legacy migration ratchet by absence.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` -> writer tests assert valid activity vocabulary and invalid activity rejection.
- `GOV-FILE-BRIDGE-AUTHORITY-001` -> bridge-compliance tests assert writer/gate publication chokepoints still block malformed bridge artifacts before disk mutation.
- `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` -> helper tests assert Claude, Codex, and template bridge-propose helper behavior remains equivalent.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` -> proposal/report evidence documents no historical rewrite, no packet/runtime scope creep, and rollback path.

Planned commands after implementation:

```powershell
python -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_bridge_thread_files.py platform_tests/skills/test_bridge_propose_helper.py platform_tests/hooks/test_bridge_compliance_gate_envelope_head.py -q --tb=short
python -m ruff check scripts/gtkb_bridge_writer.py scripts/bridge_thread_files.py .claude/hooks/bridge-compliance-gate.py .claude/skills/bridge-propose/helpers/write_bridge.py .codex/skills/bridge-propose/helpers/write_bridge.py groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_bridge_thread_files.py platform_tests/skills/test_bridge_propose_helper.py platform_tests/hooks/test_bridge_compliance_gate_envelope_head.py
python -m ruff format --check scripts/gtkb_bridge_writer.py scripts/bridge_thread_files.py .claude/hooks/bridge-compliance-gate.py .claude/skills/bridge-propose/helpers/write_bridge.py .codex/skills/bridge-propose/helpers/write_bridge.py groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_bridge_thread_files.py platform_tests/skills/test_bridge_propose_helper.py platform_tests/hooks/test_bridge_compliance_gate_envelope_head.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-envelope-protocol-slice-b-bridge-writer-envelope-head
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-protocol-slice-b-bridge-writer-envelope-head
```

## Implementation Boundaries

- No packet CLI, cache, token-budget enforcement, or dispatcher prompt injection in Slice B.
- No session-startup index, role overlay, glossary, or system-interface-map update in Slice B except if tests reveal an unavoidable direct dependency; those surfaces are planned later slices.
- No historical rewrite of existing bridge files.
- No hard-block subject-scope enforcement.
- No credential, release, production deployment, external-system mutation, Git push, or destructive cleanup.
