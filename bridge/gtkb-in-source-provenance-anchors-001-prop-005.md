REVISED
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-29-prime-builder-in-source-provenance-revised-2
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; interactive Prime Builder session

# Implementation Proposal REVISED-2 - In-Source Provenance Anchors + Orphan-Citation Doctor (Non-Protected Slice)

bridge_kind: implementation_proposal
Document: gtkb-in-source-provenance-anchors-001-prop
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-05-29 UTC
Responds-To: `bridge/gtkb-in-source-provenance-anchors-001-prop-004.md` (NO-GO)

Project Authorization: PAUTH-PROJECT-GTKB-MEMBASE-EFFECTIVE-USE-MEMBASE-EFFECTIVE-USE-BATCH
Project: PROJECT-GTKB-MEMBASE-EFFECTIVE-USE
Work Item: GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "scripts/orphan_citation_audit.py", "platform_tests/scripts/test_orphan_citation_audit.py"]

Recommended commit type: feat

## Revision Claim

This REVISED-2 implements the directive recorded as NO-GO `-004`'s actionable resolution: **split the protected narrative-artifact rule-file work from the non-protected audit+doctor work**, and authorize only the non-protected slice in this proposal. The protected rule-file creation (`.claude/rules/in-source-citation-conventions.md` plus its `.groundtruth/formal-artifact-approvals/` packet) is deferred to a separate follow-on bridge that will require an owner-approved formal-artifact packet per `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001`.

Changes vs `-003`:

- **Removed from `target_paths`**: `.claude/rules/in-source-citation-conventions.md`, `.groundtruth/formal-artifact-approvals/2026-05-20-claude-rules-in-source-citation-conventions-md.json`.
- **Removed from scope**: any creation of the protected rule file or its approval packet in this slice.
- **Retained from `-003`**: the doctor invariant addition (`groundtruth-kb/src/groundtruth_kb/project/doctor.py`), the audit script (`scripts/orphan_citation_audit.py`), the platform tests (`platform_tests/scripts/test_orphan_citation_audit.py`), and all spec linkage / preflight evidence.

### Audit operability without the rule file

The orphan-citation audit can operate without the protected rule file because it detects citation anchors that do not resolve to known artifact IDs in MemBase or the bridge/deliberation surfaces. The rule file *codifies the convention* but the audit *enforces resolvability* — these are independent. The audit's findings will document any anchor styles encountered; the future protected slice will adopt the codified convention based on observed patterns.

### Follow-on bridge for the protected rule slice

A separate bridge `gtkb-in-source-citation-conventions-rule-creation` (or similar slug) will:

1. Present the proposed `.claude/rules/in-source-citation-conventions.md` body for owner approval via AskUserQuestion.
2. On approval, create the `.groundtruth/formal-artifact-approvals/<date>-claude-rules-in-source-citation-conventions-md.json` packet with `presented_to_user = true`, `transcript_captured = true`, `explicit_change_request`, and `full_content_sha256` matching the approved body.
3. Write the protected rule file with the gate satisfied.

That follow-on bridge is out of scope for this slice and remains BLOCKED on the owner-approval packet per the standard protected-narrative-artifact workflow.

## In-Root Placement Evidence

All active target paths are under `E:\GT-KB`:

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\project\doctor.py`
- `E:\GT-KB\scripts\orphan_citation_audit.py`
- `E:\GT-KB\platform_tests\scripts\test_orphan_citation_audit.py`

No live dependency is created outside the project root. No Agent Red or `applications/` path is in scope. No protected narrative-artifact surface is touched in this slice.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - live bridge workflow state is governed by `bridge/INDEX.md`; this REVISED-2 preserves prior versions and adds a numbered `REVISED:` line for the latest actionable proposal.
- `.claude/rules/file-bridge-protocol.md` - numbered bridge files, specification links, target-path metadata, requirement sufficiency, pre-filing preflight, specification-derived verification.
- `.claude/rules/codex-review-gate.md` - implementation authorization does not weaken formal or narrative artifact approval gates; this slice respects that by excluding all protected paths.
- `.claude/rules/project-root-boundary.md` - all active files for GT-KB remain inside `E:\GT-KB`.
- `ADR-0001` - Three-Tier Memory Architecture; source comments cite durable anchors while rationale/history lives in MemBase and the Deliberation Archive.
- `GOV-08` - MemBase remains the canonical knowledge source for specifications.
- `SPEC-AUQ-POLICY-ENGINE-001` - the doctor surface remains the implementation venue for project health checks.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation and verification files remain in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites relevant governing surfaces and maps tests to those surfaces.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the post-implementation report must carry this mapping forward and execute the listed tests before VERIFIED.
- `GOV-STANDING-BACKLOG-001` - the work item is tracked in project authorization scope and is not a bulk standing-backlog operation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - active project authorization remains in force.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this header includes Project Authorization, Project, and Work Item lines.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the convention, doctor behavior, and audit results are durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation preserves traceability from source anchors to specifications.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - orphan discovery produces explicit active/deferred/verified lifecycle signals instead of hidden source-comment drift.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence for the project authorization that includes this work item.

NOT cited in this slice (intentionally deferred to the protected follow-on bridge):

- `GOV-ARTIFACT-APPROVAL-001`
- `PB-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `config/governance/narrative-artifact-approval.toml`

These specs remain relevant to the deferred protected rule-file slice; this REVISED-2 does not invoke them because it does not create any protected narrative artifact.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - project authorization context for the batch containing this work item.
- `DELIB-0975` - bridge INDEX / file-reference hygiene precedent surfaced by the provenance-anchor query.
- `DELIB-1300` - bridge INDEX phantom-reference and full-chain hygiene precedent.
- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` - MemBase effective-use assessment context for traceability and recovery work.
- `bridge/gtkb-in-source-provenance-anchors-001-prop-002.md` (NO-GO) and `-003.md` (REVISED) - prior numbering and test-lane corrections.
- `bridge/gtkb-in-source-provenance-anchors-001-prop-004.md` (NO-GO) - the operative NO-GO this REVISED-2 addresses by scope-splitting.

Narrative-artifact approval precedents (`DELIB-1561`, `DELIB-1563`, `DELIB-1575`, `DELIB-1577`, `DELIB-1901`) are intentionally NOT carried forward here; they apply to the deferred protected follow-on slice.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved `PROJECT-GTKB-MEMBASE-EFFECTIVE-USE` project authorization including `GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001`.
- 2026-05-04 S332: owner requested the original anchor-only source-comment / backlog concept.
- 2026-05-29 UTC: owner directive recorded in session continuation message: "split non-protected audit slice from protected rule-file slice (latter needs owner packet)." This REVISED-2 implements that directive verbatim.

No new owner AskUserQuestion is required for this non-protected slice. The protected follow-on slice will require an owner approval packet via AskUserQuestion when filed.

## Requirement Sufficiency

Existing requirements sufficient.

The work item describes the anchor-only convention and the orphan-citation audit. This REVISED-2 narrows scope to the non-protected portion (doctor + audit + tests). The narrowed scope does not introduce a new product requirement; it implements a subset of the existing requirement and defers the protected portion to a follow-on bridge.

## Clause Scope Clarification (Not a Bulk Operation)

This is not a bulk operation. It is one implementation proposal for one work item in `PROJECT-GTKB-MEMBASE-EFFECTIVE-USE`. Review-packet inventory: doctor.py addition, audit script, one platform test module, implementation report, and verification evidence. No bulk standing-backlog mutation, batch spec promotion, batch retirement, or multi-item MemBase write is proposed.

Evidence tokens for clause / preflight visibility: inventory, work_item, implementation proposal, specification, ADR, DCL, GOV, verified, lifecycle.

## Findings Addressed

### F1 (from -004) - P1 - Protected narrative-artifact creation blocked on missing owner approval evidence

Resolved by **scope-split**. This REVISED-2 removes from `target_paths` both `.claude/rules/in-source-citation-conventions.md` and the planned `.groundtruth/formal-artifact-approvals/` packet. The protected rule-file work is explicitly deferred to a separate future bridge (`gtkb-in-source-citation-conventions-rule-creation` or similar) that will:

1. Present the full proposed rule body for owner approval via AskUserQuestion.
2. Create the corresponding approval packet only after owner approval.
3. Write the protected rule file with the gate satisfied.

This slice does not request, draft, or write the protected rule file or its packet.

## Proposed Scope

### IP-1: Orphan-citation audit script

Add `scripts/orphan_citation_audit.py`:

1. Scan source files (Python, Markdown) for citation anchors like `SPEC-NNNN`, `GOV-NNN`, `DCL-NNN`, `ADR-NNN`, `PB-NNN`, `REQ-NNN`, `DELIB-NNNN`, `WI-NNNN`, `bridge/<thread>-NNN.md`.
2. Resolve each anchor against MemBase rows (specs, deliberations, work items) and bridge file existence on disk.
3. Emit JSON with `orphans` (anchors that don't resolve), `resolved` (count by category), `scanned_files`.
4. Exit non-zero if orphan anchors are found.
5. Read-only; no DB or file mutation.

### IP-2: Doctor invariant addition

Update `groundtruth-kb/src/groundtruth_kb/project/doctor.py` to add a check `_check_orphan_citations` that:

1. Invokes the audit script as a subprocess.
2. Reports any orphan citations as a doctor finding (severity WARN by default; configurable to FAIL via config).
3. Counts findings in the doctor's standard rollup.

### IP-3: Platform tests

Add `platform_tests/scripts/test_orphan_citation_audit.py` covering:

1. Audit detects an orphan citation (anchor not in MemBase + not on disk).
2. Audit resolves a known-good citation (SPEC-NNNN that exists in MemBase).
3. Audit JSON output shape is stable.
4. Audit exit code is non-zero on orphans, zero on clean tree.
5. Doctor check invokes the audit and surfaces orphans as findings.

## Explicitly Out of Scope

- Creation of `.claude/rules/in-source-citation-conventions.md` (deferred to protected follow-on bridge).
- Creation of any `.groundtruth/formal-artifact-approvals/*.json` packet (deferred).
- Modification of any existing source file's citation anchors (audit reports; does not rewrite).
- Bulk standing-backlog operation (this is one work item).
- Promotion of any spec status.

## Specification-Derived Verification Plan

| Behavior / spec obligation | Verification |
|---|---|
| Audit detects orphan citations | `python -m pytest platform_tests/scripts/test_orphan_citation_audit.py -q --tb=short` |
| Audit resolves known-good citations | `python -m pytest platform_tests/scripts/test_orphan_citation_audit.py -q --tb=short` |
| Audit JSON shape is stable | `python -m pytest platform_tests/scripts/test_orphan_citation_audit.py -q --tb=short` |
| Audit exit code reflects orphan presence | `python -m pytest platform_tests/scripts/test_orphan_citation_audit.py -q --tb=short` |
| Doctor invokes the audit and surfaces findings | `python -m pytest platform_tests/scripts/test_orphan_citation_audit.py -q --tb=short` |
| Changed files lint and format cleanly | `python -m ruff check scripts/orphan_citation_audit.py platform_tests/scripts/test_orphan_citation_audit.py groundtruth-kb/src/groundtruth_kb/project/doctor.py` and `python -m ruff format --check ...` |

## Acceptance Criteria

1. `scripts/orphan_citation_audit.py` exists and is read-only.
2. `groundtruth-kb/src/groundtruth_kb/project/doctor.py` has a new `_check_orphan_citations` that invokes the audit.
3. `platform_tests/scripts/test_orphan_citation_audit.py` covers detection, resolution, JSON shape, exit code, and doctor invocation.
4. No protected narrative artifact is created in this slice.
5. No `.groundtruth/formal-artifact-approvals/` packet is created in this slice.
6. Applicability and clause preflights pass before and after filing.
7. (Pending Codex) Re-GO on this REVISED-2 at `-006`.

## Risk And Rollback

Risk: audit may produce noisy WARN findings on first run due to legacy uncoded anchor styles. Mitigation: doctor severity is WARN by default (not FAIL); a future slice may raise to FAIL after the codified convention rule lands and existing anchors are reviewed.

Risk: doctor subprocess invocation may add latency to doctor runs. Mitigation: audit is read-only and runs in <1 second on the current repo; doctor's overall timing budget is not at risk.

Rollback: delete the audit script, the doctor check addition (revert that function from `doctor.py`), and the platform tests. No protected artifact rollback is required (no protected artifact created).

## Pre-Filing Preflight Subsection

To be executed before submission for review:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-in-source-provenance-anchors-001-prop`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-in-source-provenance-anchors-001-prop`

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause preflight exit 0.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
