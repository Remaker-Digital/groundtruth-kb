REVISED

# Implementation Proposal - Bridge Compliance Gate Project Metadata Requirement - REVISED-1 (WI-3314)

bridge_kind: prime_proposal
Document: gtkb-bridge-compliance-project-metadata
Version: 003
Responds to: bridge/gtkb-bridge-compliance-project-metadata-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3314

target_paths: [".claude/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py", ".claude/skills/bridge/SKILL.md", ".claude/skills/bridge-propose/SKILL.md"]

This REVISED-1 addresses the NO-GO at `bridge/gtkb-bridge-compliance-project-metadata-002.md`:

- **F1 (P1/blocking)** - Source DCL has a deferred blocking clause but original proposal still promoted the whole DCL to `implemented` → **closed** by adopting the Option-B path (metadata-only enabling slice; status promotion removed; explicit "DCL remains not fully implemented; LIVE-CHECK deferred to sibling thread").
- **F2 (P2)** - Test paths named non-existent files → **closed** by relocating to live test surface `platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py` (new file co-located with existing `test_bridge_compliance_gate_hard_block_workspace.py` and `test_codex_bridge_compliance_gate.py`), explicitly scoped as a NEW test surface for this specific clause set.

## Claim

This is a **metadata-presence enabling slice** for `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`. It lands 3 of the DCL's 4 clauses (`CLAUSE-PROJECT-METADATA-PRESENT`, `CLAUSE-VERDICT-FILES-EXCLUDED`, `CLAUSE-NON-IMPLEMENTATION-EXEMPT`). The 4th clause, `CLAUSE-PROJECT-AUTH-LIVE-CHECK`, is **explicitly deferred** to the sibling thread `gtkb-bridge-compliance-wi-project-membership` (WI-3315) which is the natural host for the live MemBase authorization lookup. **No DCL status promotion in this slice.**

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - source spec; this slice lands 3 of 4 clauses.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - upstream authorization concept.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope schema referenced by metadata lines.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage required.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3314 tracked.
- `SPEC-AUQ-POLICY-ENGINE-001` - bridge-compliance-gate is part of the policy engine surface.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive 2026-05-14 establishing this WI.
- `bridge/gtkb-bridge-compliance-project-metadata-002.md` - NO-GO under remediation by this REVISED-1.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved the 5-spec batch including `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`.
- 2026-05-15 UTC, S350+: owner directive "Proceed with REVISED-1: WI-3314" (resolves DECISION-0593).

No new owner decision required by this REVISED-1; the fix path narrows scope rather than expanding it.

## Requirement Sufficiency

Existing requirements sufficient. The source DCL fully specifies all 4 clauses; this slice scopes itself to 3 by explicit deferral of LIVE-CHECK.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI (WI-3314); member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1 (hook upgrade for 3 clauses) + IP-2 (template updates) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

REVISED filed at `bridge/gtkb-bridge-compliance-project-metadata-003.md`; `REVISED:` line prepended to existing `Document: gtkb-bridge-compliance-project-metadata` entry. Prior `NO-GO: -002` and `NEW: -001` lines preserved. Append-only audit trail intact.

## Proposed Scope (narrowed; metadata-only enabling slice)

### IP-1: Three-clause metadata-presence detection in bridge-compliance-gate.py

In `E:\GT-KB\.claude\hooks\bridge-compliance-gate.py`, add detection for the 3 clauses this slice covers:

1. Detect bridge proposal Writes: file_path matches `bridge/<slug>-NNN.md`, first non-blank line is `NEW` or `REVISED`, and `bridge_kind:` (when present) is NOT in `{spec_intake, governance_review, loyal_opposition_advisory}`.
2. Scan content for the three required metadata lines (regex, MULTILINE):
   - `^Project Authorization: PAUTH-[A-Z0-9-]+$`
   - `^Project: [A-Z0-9-]+$`
   - `^Work Item: (?:WI-\d+|GTKB-[A-Z0-9-]+|WORKLIST-[A-Z0-9-]+)$`
3. On any absent line, emit `{"decision": "block", "reason": "BLOCKED (DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001/CLAUSE-PROJECT-METADATA-PRESENT): bridge proposal Write missing required metadata: [...]. Set bridge_kind: spec_intake|governance_review|loyal_opposition_advisory for non-implementation."}`.
4. `CLAUSE-VERDICT-FILES-EXCLUDED`: when content first non-blank line starts with `GO`, `NO-GO`, or `VERIFIED`, skip the metadata check.
5. `CLAUSE-NON-IMPLEMENTATION-EXEMPT`: when `bridge_kind:` header is in the exempt set, skip the metadata check.

**This slice does NOT implement `CLAUSE-PROJECT-AUTH-LIVE-CHECK`.** The DCL remains `specified`, not `implemented`, after this slice. The live-check clause lands in sibling thread `gtkb-bridge-compliance-wi-project-membership` (WI-3315).

### IP-2: Update bridge proposal template scaffolding

In `.claude/skills/bridge/SKILL.md` and `.claude/skills/bridge-propose/SKILL.md`, add the three required metadata lines to the proposal template scaffold so author-time compliance is the default. Document the `bridge_kind:` exempt values.

### IP-3: Tests (new file; not regression of existing test_bridge_compliance_gate.py)

Create `platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py` (new file; not regression). The existing test surface lives at `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py` (Owner Decisions / Input enforcement) and `platform_tests/scripts/test_codex_bridge_compliance_gate.py` (Codex side). This proposal adds a third focused test file scoped to the 3 clauses this slice lands. No regression of existing test files; **no `test_bridge_compliance_gate.py` plain-named file is created**.

### IP-4: No spec promotion in this slice

`DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` status remains `specified`. Per F1 remediation, this slice does NOT promote the DCL to `implemented`. The DCL transitions to `implemented` only after `CLAUSE-PROJECT-AUTH-LIVE-CHECK` is also landed via sibling WI-3315 (or its successor).

## Specification-Derived Verification Plan

New test file: `platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py`:

| Clause | Test |
|---|---|
| PROJECT-METADATA-PRESENT | `test_bridge_proposal_missing_project_authorization_line_blocked` |
| PROJECT-METADATA-PRESENT | `test_bridge_proposal_missing_project_line_blocked` |
| PROJECT-METADATA-PRESENT | `test_bridge_proposal_missing_work_item_line_blocked` |
| PROJECT-METADATA-PRESENT | `test_bridge_proposal_all_three_metadata_lines_passes` |
| PROJECT-METADATA-PRESENT | `test_bridge_proposal_metadata_accepts_wi_gtkb_worklist_id_formats` |
| VERDICT-FILES-EXCLUDED | `test_verdict_file_go_no_metadata_passes` |
| VERDICT-FILES-EXCLUDED | `test_verdict_file_verified_no_metadata_passes` |
| VERDICT-FILES-EXCLUDED | `test_verdict_file_no_go_no_metadata_passes` |
| NON-IMPLEMENTATION-EXEMPT | `test_bridge_kind_spec_intake_no_metadata_passes` |
| NON-IMPLEMENTATION-EXEMPT | `test_bridge_kind_loyal_opposition_advisory_no_metadata_passes` |
| NON-IMPLEMENTATION-EXEMPT | `test_bridge_kind_governance_review_no_metadata_passes` |

**Out of scope (deferred to WI-3315 sibling):** tests for inactive authorization, expired authorization, stale authorization, wrong-project authorization, non-covering authorization. The DCL's `CLAUSE-PROJECT-AUTH-LIVE-CHECK` is explicitly deferred.

Test execution: `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py -v` per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

## Acceptance Criteria

- IP-1 three-clause detection landed in `.claude/hooks/bridge-compliance-gate.py`.
- IP-2 template updates in both `bridge/SKILL.md` and `bridge-propose/SKILL.md`.
- IP-3 new test file `platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py` lands with 11 tests; all PASS.
- IP-4: DCL status remains `specified` post-implementation; no promotion.
- No regression in existing `test_bridge_compliance_gate_hard_block_workspace.py` or `test_codex_bridge_compliance_gate.py`.
- Both preflights PASS for this REVISED-1.
- Post-impl report explicitly records the deferred-clause + sibling-thread reference.

## Risks / Rollback

- Risk: existing in-flight bridge proposals (filed pre-gate-active) won't have the metadata lines. Mitigation: gate fires only on `bridge/<slug>-NNN.md` Write events; existing files are unaffected.
- Risk: regex anchoring on `^...$` sensitive to line-ending normalization. Mitigation: use `re.MULTILINE` flag and accept `\r\n`.
- Rollback: revert IP-1 single-function-scope change; new test file deletion.

## Recommended Commit Type

`feat` - adds new mechanical governance gate (3 clauses of the source DCL); ~50 LOC hook code + ~150 LOC tests. No spec status promotion in this commit.
