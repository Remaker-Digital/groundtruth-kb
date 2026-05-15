NEW

# Implementation Proposal - In-Source Provenance Anchors + Orphan-Citation Doctor (GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001)

bridge_kind: implementation_proposal
Document: gtkb-in-source-provenance-anchors-001-prop
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-MEMBASE-EFFECTIVE-USE-MEMBASE-EFFECTIVE-USE-BATCH
Project: PROJECT-GTKB-MEMBASE-EFFECTIVE-USE
Work Item: GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "scripts/orphan_citation_audit.py", "tests/scripts/test_orphan_citation_audit.py", ".claude/rules/in-source-citation-conventions.md"]

This NEW proposal lands the in-source citation convention + an orphan-citation doctor invariant. Per owner request S332: anchor-only in source (stable refs to specs/bridge/DELIB), with rationale + history living in the Deliberation Archive (semantic search via ChromaDB).

## Claim

Three-part deliverable: (1) document the anchor-only citation convention as a rule file; (2) add a doctor check that finds source-code anchor citations whose referenced spec/bridge/DELIB no longer exists in MemBase or bridge/; (3) audit script that produces a report of all current in-source anchors and their resolution status.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `ADR-0001` - three-tier memory; DA is rationale/history store.
- `GOV-08` - KB is truth.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `GOV-ARTIFACT-APPROVAL-001` - rule file is protected narrative artifact.
- `SPEC-AUQ-POLICY-ENGINE-001` - doctor surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-MEMBASE-EFFECTIVE-USE authorization including this WI.
- 2026-05-04 S332: original owner backlog-addition request.

## Requirement Sufficiency

Existing requirements sufficient. WI description specifies the anchor-only convention + 3 anchor patterns.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-MEMBASE-EFFECTIVE-USE per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 (rule) + IP-2 (doctor check) + IP-3 (audit script) + IP-4 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: In-source citation conventions rule

`.claude/rules/in-source-citation-conventions.md` (new narrative artifact; requires `narrative-artifact-approval` packet):

Documents 3 anchor patterns:
- `# Enforces: <SPEC-ID> v<N>` (function or class enforcing a specification)
- `# See bridge/<thread>-<NNN>.md for approved scope` (implementation derived from bridge GO)
- `# Source: DELIB-<ID>` (decision rationale in Deliberation Archive)

Convention: comments cite anchors only. Rationale + history lives in DA records, not source comments. Code reviews prefer cited DA records over inline prose explanations.

### IP-2: Orphan-citation doctor check

In `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, add `check_orphan_citations()`:
1. grep all source files for anchor patterns.
2. For each anchor, resolve the referenced ID:
   - SPEC-ID → `db.get_spec(id)` returns row?
   - bridge thread → `bridge/<thread>-NNN.md` files exist?
   - DELIB-ID → `db.get_deliberation(id)` returns row?
3. Report orphans (anchor exists in source but referent absent).

### IP-3: Audit script

`scripts/orphan_citation_audit.py`: CLI version of IP-2 with JSON output. Useful for CI integration.

### IP-4: Tests

Tests cover: anchor pattern matching, referent resolution, orphan detection, rule file presence.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| `Enforces:` anchor detected | `test_enforces_anchor_detected` |
| `See bridge/` anchor detected | `test_bridge_anchor_detected` |
| `Source: DELIB-` anchor detected | `test_delib_anchor_detected` |
| Resolved anchor: no orphan flag | `test_resolved_anchor_no_orphan` |
| Unresolved spec anchor flagged | `test_unresolved_spec_anchor_flagged` |
| Unresolved DELIB anchor flagged | `test_unresolved_delib_anchor_flagged` |
| Rule file documents 3 patterns | `test_rule_file_documents_patterns` |
| Doctor check exit-code on orphans | `test_doctor_exit_code_on_orphans` |

Run: `python -m pytest tests/scripts/test_orphan_citation_audit.py -v`.

## Acceptance Criteria

- IP-1 rule landed with narrative-artifact-approval packet.
- IP-2, IP-3, IP-4 landed; 8 tests PASS.
- Initial audit on current repo emits report; orphan count documented.
- Both preflights PASS.

## Risks / Rollback

- Risk: existing source comments may have inconsistent citation patterns (free-form text). Mitigation: doctor reports orphans but doesn't block on baseline pre-rule citations; only newly-added anchors are subject to orphan-detection severity.
- Risk: rule introduces friction to writing source comments. Mitigation: convention is opt-in for new code; existing comments unaffected.
- Rollback: remove rule file + doctor check; audit script can stay as opt-in tool.

## Recommended Commit Type

`feat` - new convention + doctor surface. ~120 LOC + rule markdown + tests.
