NEW

# Implementation Proposal - Bridge Compliance Gate Project Metadata Requirement (WI-3314)

bridge_kind: implementation_proposal
Document: gtkb-bridge-compliance-project-metadata
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3314

target_paths: [".claude/hooks/bridge-compliance-gate.py", "tests/hooks/test_bridge_compliance_gate.py", "platform_tests/hooks/test_bridge_compliance_gate.py", ".claude/skills/bridge/SKILL.md", ".claude/skills/bridge-propose/SKILL.md"]

This NEW proposal implements `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` (v1, specified, landed 2026-05-14). Every implementation-targeting bridge proposal must include three machine-readable metadata lines: `Project Authorization: <auth-id>`, `Project: <project-id>`, and `Work Item: WI-NNNN`. The bridge-compliance-gate hook rejects Writes that lack these lines.

## Claim

Extend `.claude/hooks/bridge-compliance-gate.py` to detect when a bridge proposal Write is in scope (NEW/REVISED status; not a verdict file; bridge_kind not in the exempt set), and verify presence + format of the three metadata lines. Stale-authorization detection (live-state check against `project_authorizations`) is deferred to a sibling slice; this WI lands the metadata-presence requirement only.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB`. Bridge file at `E:\GT-KB\bridge\gtkb-bridge-compliance-project-metadata-001.md`. Targets at `E:\GT-KB\.claude\hooks\bridge-compliance-gate.py`, `E:\GT-KB\tests\hooks\test_bridge_compliance_gate.py`, `E:\GT-KB\platform_tests\hooks\test_bridge_compliance_gate.py`, `E:\GT-KB\.claude\skills\bridge\SKILL.md`, `E:\GT-KB\.claude\skills\bridge-propose\SKILL.md`. No `applications/` paths. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - source spec for this WI; v1 specified 2026-05-14.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - upstream authorization concept.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope schema referenced by the metadata lines.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; gate operates within it.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI-3314 is a tracked work_item.
- `SPEC-AUQ-POLICY-ENGINE-001` - bridge-compliance-gate is part of the policy engine surface.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive 2026-05-14.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved 5-spec batch including DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001.
- 2026-05-14 UTC, S350+: owner directive "Please proceed with parallel implementation proposals for as many backlog items as possible" - explicit authorization to file this NEW.

No new owner decision required.

## Requirement Sufficiency

Existing requirements sufficient. DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 v1 fully specifies the four clauses (PROJECT-METADATA-PRESENT, PROJECT-AUTH-LIVE-CHECK, VERDICT-FILES-EXCLUDED, NON-IMPLEMENTATION-EXEMPT). This WI lands PRESENT + EXCLUDED + EXEMPT; LIVE-CHECK is deferred to a follow-on slice (single-clause-per-slice ergonomic separation).

## Clause Scope Clarification (Not a Bulk Operation)

This is NOT a bulk operation. Exactly one work item (WI-3314) is the operative target. WI is an active member of project GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001 per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1 (hook upgrade) + IP-2 (template updates) + IP-3 (tests) scoped to a single thread file.

## Bridge INDEX Update Evidence

NEW filed at `bridge/gtkb-bridge-compliance-project-metadata-001.md`; new top-of-file entry prepended to `bridge/INDEX.md`.

## Proposed Scope

### IP-1: Add metadata-presence detection to bridge-compliance-gate.py

In `E:\GT-KB\.claude\hooks\bridge-compliance-gate.py`:

1. Detect bridge proposal Writes: file_path matches `bridge/<slug>-NNN.md`, first non-blank line is `NEW` or `REVISED`, and `bridge_kind:` header (when present) is NOT in `{spec_intake, governance_review, loyal_opposition_advisory}`.
2. For matching writes, scan the content for three required lines (case-sensitive):
   - `^Project Authorization: PAUTH-[A-Z0-9-]+$`
   - `^Project: [A-Z0-9-]+$`
   - `^Work Item: WI-\d+$`
3. If any are absent, emit `{"decision": "block", "reason": "BLOCKED (DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001/CLAUSE-PROJECT-METADATA-PRESENT): bridge proposal Write missing required metadata: [...]. Add the absent lines or set bridge_kind: spec_intake|governance_review|loyal_opposition_advisory if non-implementation."}`.
4. Verdict files (content starts with `GO`, `NO-GO`, or `VERIFIED`) are excluded from this check (CLAUSE-VERDICT-FILES-EXCLUDED).
5. Non-implementation proposals (CLAUSE-NON-IMPLEMENTATION-EXEMPT) self-declare via `bridge_kind:` header.

### IP-2: Update bridge proposal templates and helpers

In `E:\GT-KB\.claude\skills\bridge\SKILL.md` and `E:\GT-KB\.claude\skills\bridge-propose\SKILL.md`, add the three required metadata lines to the proposal template scaffolding. Update example proposals where present.

### IP-3: Spec status promotion

Promote `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` from `specified` to `implemented` after IP-1 + IP-2 land and tests pass. Note: CLAUSE-PROJECT-AUTH-LIVE-CHECK clause is deferred; full implementation comes from sibling WI later (status remains `implemented` with a known follow-on rather than `verified`).

## Specification-Derived Verification Plan

Tests in `tests/hooks/test_bridge_compliance_gate.py` (and platform_tests mirror):

| Clause | Test |
|---|---|
| PROJECT-METADATA-PRESENT | `test_bridge_proposal_missing_project_authorization_line_blocked` |
| PROJECT-METADATA-PRESENT | `test_bridge_proposal_missing_project_line_blocked` |
| PROJECT-METADATA-PRESENT | `test_bridge_proposal_missing_work_item_line_blocked` |
| PROJECT-METADATA-PRESENT | `test_bridge_proposal_all_three_metadata_lines_passes` |
| VERDICT-FILES-EXCLUDED | `test_verdict_file_go_no_metadata_passes` |
| VERDICT-FILES-EXCLUDED | `test_verdict_file_verified_no_metadata_passes` |
| NON-IMPLEMENTATION-EXEMPT | `test_bridge_kind_spec_intake_no_metadata_passes` |
| NON-IMPLEMENTATION-EXEMPT | `test_bridge_kind_loyal_opposition_advisory_no_metadata_passes` |

Test execution: `python -m pytest tests/hooks/test_bridge_compliance_gate.py platform_tests/hooks/test_bridge_compliance_gate.py -v`.

## Acceptance Criteria

- IP-1 metadata-presence detection landed; 8 tests PASS.
- IP-2 templates updated.
- IP-3 spec promoted to `implemented` with deferred-clause note.
- No regression in existing test_bridge_compliance_gate.py.
- Both preflights PASS for this bridge ID.

## Risks / Rollback

- Risk: existing in-flight bridge proposals filed before this gate lands will fail re-Writes. Mitigation: grandfather check by file-existence (if file already exists with prior format, allow Write without enforcing; only NEW first-Writes enforce).
- Risk: regex anchoring (`^...$`) is sensitive to line-ending normalization. Mitigation: use `re.MULTILINE` flag and accept `\r\n`.
- Rollback: revert IP-1 single-function-scope change.

## Recommended Commit Type

`feat` - adds new mechanical governance gate to bridge-compliance-gate. ~60 LOC net (hook code + tests).
