REVISED
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex Desktop default reasoning

# Implementation Proposal REVISED - In-Source Provenance Anchors + Orphan-Citation Doctor

bridge_kind: prime_proposal
Document: gtkb-in-source-provenance-anchors-001-prop
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-05-20 UTC
Addresses: NO-GO at `bridge/gtkb-in-source-provenance-anchors-001-prop-002.md` (F1: original proposal was filed as an unnumbered bridge file; F2: verification targeted stale `tests/scripts/**`).

Project Authorization: PAUTH-PROJECT-GTKB-MEMBASE-EFFECTIVE-USE-MEMBASE-EFFECTIVE-USE-BATCH
Project: PROJECT-GTKB-MEMBASE-EFFECTIVE-USE
Work Item: GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "scripts/orphan_citation_audit.py", "platform_tests/scripts/test_orphan_citation_audit.py", ".claude/rules/in-source-citation-conventions.md", ".groundtruth/formal-artifact-approvals/2026-05-20-claude-rules-in-source-citation-conventions-md.json"]

## Revision Claim

This REVISED proposal preserves the original product goal while correcting the two Codex blockers. The live proposal is now a numbered bridge version that the canonical full-chain helper can load, and the implementation/test scope uses the live root test surface `platform_tests/scripts/test_orphan_citation_audit.py` instead of stale `tests/scripts/**`. It also incorporates the protected narrative-artifact approval-packet workflow for `.claude/rules/in-source-citation-conventions.md`, because `.claude/rules/*.md` creations are packet-gated by `config/governance/narrative-artifact-approval.toml`.

The deliverable remains a three-part implementation: document the anchor-only citation convention, add a doctor/audit invariant for orphan in-source anchors, and run a root-discoverable regression suite covering the parser, resolver, and current rule-file contract.

## In-Root Placement Evidence

All active target paths are under `E:\GT-KB`:

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\project\doctor.py`
- `E:\GT-KB\scripts\orphan_citation_audit.py`
- `E:\GT-KB\platform_tests\scripts\test_orphan_citation_audit.py`
- `E:\GT-KB\.claude\rules\in-source-citation-conventions.md`
- `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-20-claude-rules-in-source-citation-conventions-md.json`

No live dependency is created outside the project root. No Agent Red or `applications/` path is in scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - live bridge workflow state is governed by `bridge/INDEX.md`; this REVISED preserves prior versions and adds a numbered `REVISED:` line for the latest actionable proposal.
- `.claude/rules/file-bridge-protocol.md` - requires numbered bridge files, specification links, target-path metadata, requirement sufficiency, pre-filing preflight, and specification-derived verification.
- `.claude/rules/codex-review-gate.md` - implementation authorization does not weaken formal or narrative artifact approval gates.
- `.claude/rules/project-root-boundary.md` - all active files for GT-KB remain inside `E:\GT-KB`.
- `ADR-0001` - Three-Tier Memory Architecture; source comments cite durable anchors while rationale/history lives in MemBase and the Deliberation Archive.
- `GOV-08` - MemBase remains the canonical knowledge source for specifications.
- `SPEC-AUQ-POLICY-ENGINE-001` - the doctor surface remains the implementation venue for project health checks.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation and verification files remain in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites relevant governing surfaces and maps tests to those surfaces.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the post-implementation report must carry this mapping forward and execute the listed tests before VERIFIED.
- `GOV-STANDING-BACKLOG-001` - the work item is tracked in project authorization scope and is not a bulk standing-backlog operation.
- `GOV-ARTIFACT-APPROVAL-001` - `.claude/rules/in-source-citation-conventions.md` is a protected narrative artifact and requires explicit approval-packet evidence before protected write/commit.
- `PB-ARTIFACT-APPROVAL-001` - Prime Builder must preserve owner-visible approval evidence for protected artifact creation.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - the narrative-artifact gate and pre-commit floor verify packet presence and full-content hash coverage.
- `config/governance/narrative-artifact-approval.toml` - the active protected narrative-artifact registry; `.claude/rules/*.md` is protected with `action = "create"`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the convention, rule, bridge revision, and doctor behavior are durable artifacts with explicit lifecycle evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation preserves traceability from source anchors to specifications, bridge approvals, and deliberations.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - orphan discovery produces explicit active/deferred/verified lifecycle signals instead of hidden source-comment drift.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence for the project authorization that includes this work item.
- `bridge/gtkb-in-source-provenance-anchors-001-prop-001.md` - numbered historical copy of the original proposal content.
- `bridge/gtkb-in-source-provenance-anchors-001-prop-002.md` - Codex NO-GO whose findings are addressed here.

## Prior Deliberations

Read-only `KnowledgeDB.search_deliberations()` queries were run for:

- `GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001 in-source provenance anchors orphan citation doctor`
- `anchor-only source comments Deliberation Archive MemBase bridge DELIB`
- `narrative artifact approval .claude/rules in-source citation conventions`

Relevant records surfaced and carried forward:

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - project authorization context for the batch containing this work item.
- `DELIB-0975` - bridge INDEX/file-reference hygiene precedent surfaced by the provenance-anchor query.
- `DELIB-1300` - bridge INDEX phantom-reference and full-chain hygiene precedent.
- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` - MemBase effective-use assessment context for traceability and recovery work.
- `DELIB-1561`, `DELIB-1563`, `DELIB-1575`, and `DELIB-1577` - narrative-artifact approval and DA read-surface correction precedents relevant to `.claude/rules/*.md` protected writes.
- `DELIB-1901` - compressed narrative-artifact approval extension thread; protected narrative-artifact registry is steady-state.

No searched deliberation rejects the anchor-only source-comment convention. The changes in this REVISED are procedural corrections to bridge shape, test placement, and approval-packet handling.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved `PROJECT-GTKB-MEMBASE-EFFECTIVE-USE` project authorization including `GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001`.
- 2026-05-04 S332: owner requested the original anchor-only source-comment/backlog concept.
- 2026-05-20 UTC: owner asked Prime Builder to proceed from bridge work, parallelize where possible, and continue without input for as long as possible. This authorizes processing the latest `NO-GO` by filing a corrected REVISED proposal; it does not waive protected narrative-artifact approval.
- The full body of `.claude/rules/in-source-citation-conventions.md` has not yet been presented for explicit owner approval. If this proposal receives GO, implementation may draft the rule body and packet, but the protected write/commit remains blocked until an approval packet exists with `presented_to_user = true`, `transcript_captured = true`, `explicit_change_request`, and `full_content_sha256` matching the approved file body.

## Requirement Sufficiency

Existing requirements sufficient.

The work item describes the anchor-only convention and three anchor families. This revision does not introduce a new product requirement; it corrects bridge conformance, test placement, and protected-artifact approval handling.

## Clause Scope Clarification (Not a Bulk Operation)

This is not a bulk operation. It is one implementation proposal for one work item in `PROJECT-GTKB-MEMBASE-EFFECTIVE-USE`. Review-packet inventory: rule file, approval packet, doctor/audit code, one platform test module, implementation report, and verification evidence. No bulk standing-backlog mutation, batch spec promotion, batch retirement, or multi-item MemBase write is proposed.

Evidence tokens for clause/preflight visibility: inventory, formal-artifact-approval, approval_packet, narrative_artifact, action=create, presented_to_user, transcript_captured, explicit_change_request, full_content_sha256, work_item, implementation proposal, specification, ADR, DCL, GOV, verified, lifecycle.

## Findings Addressed

### F1 - P1 - The indexed proposal file is not protocol-versioned, so the canonical full-chain helper cannot load it

Resolved. The original unnumbered proposal has been preserved and refiled as `bridge/gtkb-in-source-provenance-anchors-001-prop-001.md`, and this completed revision will file as `bridge/gtkb-in-source-provenance-anchors-001-prop-003.md`. The `bridge/INDEX.md` entry is corrected so the historical `NEW` line points at the numbered `-001.md` file, and the latest actionable line will point at the numbered `-003.md` file.

### F2 - P1 - Verification uses the stale root `tests/scripts/**` surface

Resolved. `target_paths` now uses `platform_tests/scripts/test_orphan_citation_audit.py`. The verification plan runs `python -m pytest platform_tests/scripts/test_orphan_citation_audit.py -q --tb=short`, matching root pytest discovery and `.github/workflows/groundtruth-kb-tests.yml` coverage of `platform_tests/`.

## Scope Changes From -001

- Replaced stale `tests/scripts/test_orphan_citation_audit.py` with `platform_tests/scripts/test_orphan_citation_audit.py`.
- Added `.groundtruth/formal-artifact-approvals/2026-05-20-claude-rules-in-source-citation-conventions-md.json` to `target_paths` so implementation-start authorization includes the planned narrative-artifact approval packet.
- Added `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001`, `config/governance/narrative-artifact-approval.toml`, and the three artifact-oriented advisory specs to `## Specification Links`.
- Added an explicit approval-packet plan for the protected `.claude/rules/in-source-citation-conventions.md` creation.
- Reframed the audit script tests around root-discoverable `platform_tests/` execution and narrative-artifact pre-commit evidence.

No change to the product goal: source comments carry stable anchors only, while rationale and history remain in the Deliberation Archive and MemBase.

## Approval-Packet Plan for `.claude/rules/in-source-citation-conventions.md`

The packet is not pre-written by this proposal. It is implementation-time evidence that must be produced before the protected rule-file write is committed.

Packet location:

- `.groundtruth/formal-artifact-approvals/2026-05-20-claude-rules-in-source-citation-conventions-md.json`

Required schema fields per `config/governance/narrative-artifact-approval.toml`:

| Field | Planned Value |
|---|---|
| `artifact_type` | `"narrative_artifact"` |
| `artifact_id` | `"claude-rules-in-source-citation-conventions-md"` |
| `action` | `"create"` |
| `target_path` | `".claude/rules/in-source-citation-conventions.md"` |
| `source_ref` | `"bridge/gtkb-in-source-provenance-anchors-001-prop-003"` |
| `full_content` | verbatim final body of the proposed rule file |
| `full_content_sha256` | `sha256(full_content)` computed after final approval text is settled |
| `approval_mode` | `"approve"` or `"edit-and-approve"` |
| `presented_to_user` | `true` |
| `transcript_captured` | `true` |
| `explicit_change_request` | verbatim owner approval text for the full file body |
| `changed_by` | `"codex-prime-builder"` |
| `change_reason` | `"GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001; bridge thread gtkb-in-source-provenance-anchors-001-prop"` |

Implementation-time workflow:

1. Draft the full body of `.claude/rules/in-source-citation-conventions.md`.
2. Present the full body to the owner through the governed owner-decision channel.
3. Capture the approval response in `explicit_change_request`.
4. Compute `full_content_sha256` over the exact approved body.
5. Write the packet JSON.
6. Write the protected rule file with the approval-packet environment variable or flag available to the gate.
7. Stage the rule file and packet; run `python scripts/check_narrative_artifact_evidence.py --staged`; expect exit 0.
8. Run the negative case by staging the rule without its packet in an isolated test fixture or subprocess-controlled git index; expect the evidence check to reject.

## Proposed Scope

### IP-1: In-source citation convention rule

Create `.claude/rules/in-source-citation-conventions.md` as a protected narrative artifact. The rule documents these source-comment anchor patterns:

- `# Enforces: <SPEC-ID> v<N>` for functions/classes that implement a specification clause.
- `# See bridge/<thread>-<NNN>.md for approved scope` for implementation derived from a bridge GO.
- `# Source: DELIB-<ID>` for decisions whose rationale lives in the Deliberation Archive.

The convention is anchor-only in source. Rationale/history belongs in MemBase, Deliberation Archive records, and bridge documents, not in long inline prose.

### IP-2: Orphan-citation audit logic and doctor integration

Add reusable audit logic in `scripts/orphan_citation_audit.py` and wire a doctor-facing check from `groundtruth-kb/src/groundtruth_kb/project/doctor.py`. The logic scans tracked source/script/rule files for the three anchor families and resolves each referent:

- specification anchors resolve through MemBase spec lookup;
- bridge anchors resolve against numbered `bridge/<thread>-NNN.md` files;
- deliberation anchors resolve through Deliberation Archive lookup.

The initial doctor behavior reports orphan anchors and emits JSON-friendly detail without changing source files.

### IP-3: Root-discoverable tests

Create `platform_tests/scripts/test_orphan_citation_audit.py`. Tests cover pattern extraction, referent resolution, orphan reporting, doctor-surface behavior, rule-file content expectations, and narrative-artifact evidence checks.

## Specification-Derived Verification Plan

| Specification / scope | Verification step | Command |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` + `.claude/rules/file-bridge-protocol.md` | Numbered bridge chain loads without malformed latest proposal path | `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-in-source-provenance-anchors-001-prop --format markdown --preview-lines 1200` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` + `.claude/rules/project-root-boundary.md` | Confirm implementation files are in-root and lintable | `python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py scripts/orphan_citation_audit.py platform_tests/scripts/test_orphan_citation_audit.py` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight on the bridge thread | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-in-source-provenance-anchors-001-prop` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Clause preflight and spec-to-test traceability | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-in-source-provenance-anchors-001-prop` |
| `ADR-0001`, `GOV-08`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Anchor extraction and referent resolution tests | `python -m pytest platform_tests/scripts/test_orphan_citation_audit.py -q --tb=short` |
| `SPEC-AUQ-POLICY-ENGINE-001` | Doctor/audit JSON output covers orphan details and non-orphan pass cases | `python -m pytest platform_tests/scripts/test_orphan_citation_audit.py -q --tb=short` |
| `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001`, `config/governance/narrative-artifact-approval.toml` | Protected rule-file packet evidence positive case | Stage `.claude/rules/in-source-citation-conventions.md` and the packet; run `python scripts/check_narrative_artifact_evidence.py --staged`; expect exit 0 |
| `GOV-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` | Protected rule-file packet evidence negative case | In a fixture or subprocess-controlled git index, stage the rule without the packet; run `python scripts/check_narrative_artifact_evidence.py --staged`; expect rejection |

## Acceptance Criteria

1. `bridge/INDEX.md` latest status for this thread becomes `REVISED: bridge/gtkb-in-source-provenance-anchors-001-prop-003.md`, and the historical `NEW` line points at numbered `bridge/gtkb-in-source-provenance-anchors-001-prop-001.md`.
2. `show_thread_bridge.py` loads the numbered version chain containing `-001`, `-002`, and `-003` with no latest-path drift.
3. `.claude/rules/in-source-citation-conventions.md` is created only after a matching narrative-artifact approval packet exists.
4. `scripts/orphan_citation_audit.py` reports anchors and referent status in deterministic JSON.
5. `groundtruth-kb/src/groundtruth_kb/project/doctor.py` exposes the orphan-citation check through the existing doctor surface.
6. `platform_tests/scripts/test_orphan_citation_audit.py` passes under root pytest invocation.
7. Ruff check and format check pass for touched Python files.
8. Post-implementation report carries forward the spec-to-test mapping and exact observed command outputs.

## Bridge INDEX Update Evidence

This revision performs two bridge-state corrections:

- Corrects the historical `NEW` line from `bridge/gtkb-in-source-provenance-anchors-001-prop.md` to `bridge/gtkb-in-source-provenance-anchors-001-prop-001.md` after preserving the original body in the numbered file.
- Adds `REVISED: bridge/gtkb-in-source-provenance-anchors-001-prop-003.md` at the top of this document entry.

No bridge file is deleted. The original unnumbered file remains on disk as historical evidence, but the live canonical thread is now represented by numbered files.

## Pre-Filing Preflight Subsection

Before live filing, Prime Builder checks the completed candidate content against:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-in-source-provenance-anchors-001-prop --content-file .gtkb-state/bridge-revisions/drafts/gtkb-in-source-provenance-anchors-001-prop-003.md --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-in-source-provenance-anchors-001-prop --content-file .gtkb-state/bridge-revisions/drafts/gtkb-in-source-provenance-anchors-001-prop-003.md`

The helper-mediated live filing path reruns both candidate preflights before writing `bridge/gtkb-in-source-provenance-anchors-001-prop-003.md` and updating `bridge/INDEX.md`.

## Risk And Rollback

- Risk: baseline source comments may contain informal references that look like anchors. Mitigation: tests separate strict anchor patterns from prose, and initial audit reports baseline findings without auto-editing source.
- Risk: the protected rule-file approval packet blocks implementation while waiting on owner approval. Mitigation: the packet is explicitly in scope and the implementation can proceed through non-protected audit/test drafting until the protected write is the only remaining step.
- Risk: correcting the malformed historical `NEW` line could confuse readers who remember the unnumbered filename. Mitigation: this REVISED documents the correction, and the original unnumbered file remains on disk.
- Rollback: if the implementation is not accepted, remove the new audit script and doctor wiring in a follow-on bridge revision; leave bridge history intact. If the rule body is not approved, do not write `.claude/rules/in-source-citation-conventions.md`.

## Recommended Commit Type

`feat:` - adds a new provenance-anchor convention, audit/doctor capability, and tests.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
