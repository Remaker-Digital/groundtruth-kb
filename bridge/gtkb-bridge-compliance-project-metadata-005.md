REVISED

# Implementation Proposal - Bridge Compliance Gate Project Metadata Requirement - REVISED-2 (WI-3314)

bridge_kind: prime_proposal
Document: gtkb-bridge-compliance-project-metadata
Version: 005
Responds to: bridge/gtkb-bridge-compliance-project-metadata-004.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3314

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py", ".claude/skills/bridge/SKILL.md", ".claude/skills/bridge-propose/SKILL.md", ".codex/skills/bridge/SKILL.md", ".codex/skills/bridge-propose/SKILL.md", ".codex/skills/MANIFEST.json"]

This REVISED-2 addresses the NO-GO at `bridge/gtkb-bridge-compliance-project-metadata-004.md`. The -004 verdict confirmed REVISED-1 closed both prior substantive findings (no-DCL-promotion + correct test paths). The two new findings are `target_paths` completeness issues:

- **F1 (P1)** — Active hook `.claude/hooks/bridge-compliance-gate.py` has a packaged template twin `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`; `test_bridge_compliance_gate_hard_block_workspace.py` asserts their hashes are equal → **closed** by adding the template path to `target_paths` + IP-3 keeps both files byte-identical.
- **F2 (P1)** — Canonical `.claude/skills/bridge*/SKILL.md` edits require regenerating the `.codex/skills/*` adapters → **closed** by adding the 3 adapter/manifest paths to `target_paths` + IP-4 runs `generate_codex_skill_adapters.py --update-registry --check`.

The narrowed no-DCL-promotion posture from REVISED-1 is carried forward unchanged.

## Claim

Metadata-presence enabling slice for `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — lands 3 of 4 clauses (`CLAUSE-PROJECT-METADATA-PRESENT`, `CLAUSE-VERDICT-FILES-EXCLUDED`, `CLAUSE-NON-IMPLEMENTATION-EXEMPT`); defers `CLAUSE-PROJECT-AUTH-LIVE-CHECK` to sibling WI-3315. The hook change is applied to BOTH the active hook and its packaged template (preserving the parity test), and the canonical skill edits are propagated to the generated Codex adapters. **No DCL status promotion in this slice.**

## In-Root Placement Evidence

All 8 target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - source spec; this slice lands 3 of 4 clauses.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - upstream authorization concept.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope schema referenced by metadata lines.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex skill-adapter parity contract (governs IP-4).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage required.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3314 tracked.
- `SPEC-AUQ-POLICY-ENGINE-001` - bridge-compliance-gate is part of the policy engine surface.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive 2026-05-14 establishing WI-3314.
- `bridge/gtkb-bridge-compliance-project-metadata-002.md` - first NO-GO (F1 deferred-clause/promotion + F2 test paths; both closed by REVISED-1).
- `bridge/gtkb-bridge-compliance-project-metadata-004.md` - second NO-GO (target_paths completeness; closed by this REVISED-2).

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved the 5-spec batch including `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`.
- 2026-05-15 UTC, S350+: owner directive "Continue your focus on getting WI-3314, WI-3315, WI-3312, WI-3313 to VERIFIED."

No new owner decision required by this REVISED-2; the fix expands `target_paths` to cover files the acceptance criteria already implied.

## Requirement Sufficiency

Existing requirements sufficient. The source DCL fully specifies all 4 clauses; this slice scopes to 3 by explicit deferral of LIVE-CHECK.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI (WI-3314); member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1 (active hook) + IP-2 (templates) + IP-3 (hook-template parity) + IP-4 (Codex adapter regen) + IP-5 (tests) single thread.

## Bridge INDEX Update Evidence

REVISED filed at `bridge/gtkb-bridge-compliance-project-metadata-005.md`; `REVISED:` line prepended. Prior `NO-GO: -004`, `REVISED: -003`, `NO-GO: -002`, `NEW: -001` lines all preserved. Append-only audit trail intact.

## Proposed Scope

### IP-1: Three-clause metadata-presence detection in the active hook

In `E:\GT-KB\.claude\hooks\bridge-compliance-gate.py`, add detection for the 3 clauses this slice covers (unchanged from REVISED-1):

1. Detect bridge proposal Writes: file_path matches `bridge/<slug>-NNN.md`, first non-blank line is `NEW` or `REVISED`, and `bridge_kind:` (when present) is NOT in `{spec_intake, governance_review, loyal_opposition_advisory}`.
2. Scan content for the three required metadata lines (regex, MULTILINE):
   - `^Project Authorization: PAUTH-[A-Z0-9-]+$`
   - `^Project: [A-Z0-9-]+$`
   - `^Work Item: (?:WI-\d+|GTKB-[A-Z0-9-]+|WORKLIST-[A-Z0-9-]+)$`
3. On any absent line, emit `{"decision": "block", "reason": "BLOCKED (DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001/CLAUSE-PROJECT-METADATA-PRESENT): bridge proposal Write missing required metadata: [...]."}`.
4. `CLAUSE-VERDICT-FILES-EXCLUDED`: when content first non-blank line starts with `GO`, `NO-GO`, `VERIFIED`, or `WITHDRAWN`, skip the metadata check.
5. `CLAUSE-NON-IMPLEMENTATION-EXEMPT`: when `bridge_kind:` header is in the exempt set, skip the metadata check.

**This slice does NOT implement `CLAUSE-PROJECT-AUTH-LIVE-CHECK`.** The DCL remains `specified` after this slice; the live-check clause lands in sibling WI-3315.

### IP-2: Apply the identical change to the packaged hook template (F1 closure)

Apply the byte-identical IP-1 change to `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`. The two files must remain hash-equal.

### IP-3: Hook-template parity preservation (F1 closure)

After IP-1 + IP-2, the active hook and the template hook have identical content. The existing `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py` parity test (`ACTIVE_HOOK` vs `TEMPLATE_HOOK` hash equality, lines 24-25 + 52-59) continues to pass with no test modification.

### IP-4: Codex skill-adapter regeneration (F2 closure)

After editing the canonical `.claude/skills/bridge/SKILL.md` and `.claude/skills/bridge-propose/SKILL.md` (IP-5 below), run:

```text
python scripts/generate_codex_skill_adapters.py --update-registry --check
```

This regenerates `.codex/skills/bridge/SKILL.md`, `.codex/skills/bridge-propose/SKILL.md`, and updates `.codex/skills/MANIFEST.json`. The `--check` flag asserts the adapters are in sync after regeneration. All 3 generated paths are in `target_paths`.

### IP-5: Update canonical bridge proposal template scaffolding

In `.claude/skills/bridge/SKILL.md` and `.claude/skills/bridge-propose/SKILL.md`, add the three required metadata lines (`Project Authorization:`, `Project:`, `Work Item:`) to the proposal template scaffold so author-time compliance is the default. Document the `bridge_kind:` exempt values. IP-4's regeneration propagates these edits to the Codex adapters.

### IP-6: Tests (new file)

Create `platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py` (new file; not regression of any existing file). Co-located with `test_bridge_compliance_gate_hard_block_workspace.py`.

### IP-7: No spec promotion in this slice

`DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` status remains `specified`. Promotion happens only after `CLAUSE-PROJECT-AUTH-LIVE-CHECK` also lands via WI-3315.

## Specification-Derived Verification Plan

New test file `platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py`:

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
| VERDICT-FILES-EXCLUDED | `test_verdict_file_withdrawn_no_metadata_passes` |
| NON-IMPLEMENTATION-EXEMPT | `test_bridge_kind_spec_intake_no_metadata_passes` |
| NON-IMPLEMENTATION-EXEMPT | `test_bridge_kind_loyal_opposition_advisory_no_metadata_passes` |
| NON-IMPLEMENTATION-EXEMPT | `test_bridge_kind_governance_review_no_metadata_passes` |

Verification commands:
- `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py -v`
- `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py -v` (parity regression — must still pass)
- `python scripts/generate_codex_skill_adapters.py --update-registry --check` (adapter sync — must exit 0)

## Acceptance Criteria

- IP-1 + IP-2: 3-clause detection in BOTH `.claude/hooks/bridge-compliance-gate.py` and `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`, byte-identical.
- IP-3: `test_bridge_compliance_gate_hard_block_workspace.py` parity test PASSES unmodified.
- IP-4: `generate_codex_skill_adapters.py --update-registry --check` exits 0; `.codex/skills/*` adapters + MANIFEST.json in sync.
- IP-5: canonical skill template scaffolding updated.
- IP-6: new test file lands with 12 tests; all PASS.
- IP-7: `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` remains `specified`.
- No regression in `test_bridge_compliance_gate_hard_block_workspace.py` or `test_codex_bridge_compliance_gate.py`.
- Both preflights PASS.

## Risks / Rollback

- Risk: hook-template drift if IP-1 and IP-2 diverge. Mitigation: IP-3 parity test catches any divergence; apply the identical patch to both.
- Risk: Codex adapter regeneration may surface unrelated drift in `.codex/skills/`. Mitigation: `--check` flag fails loudly; if pre-existing drift exists, scope it as a separate finding rather than absorbing it.
- Rollback: revert IP-1/IP-2 (parallel single-function-scope changes); regenerate adapters from reverted canonical; delete new test file.

## Recommended Commit Type

`feat` - adds new mechanical governance gate (3 clauses) across active hook + template + Codex adapters; ~50 LOC hook x2 + skill-doc edits + ~150 LOC tests. No spec status promotion.
