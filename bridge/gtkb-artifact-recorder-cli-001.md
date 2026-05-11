NEW

# Implementation Proposal (Slice 0 — Scoping) — GTKB-ARTIFACT-RECORDER-CLI

**Document:** `gtkb-artifact-recorder-cli`
**Status:** `NEW`
**Date:** 2026-05-11
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_proposal
**Slice:** 0 (scoping only; per-slice implementation proposals follow Codex GO)
**Recommended commit type:** `docs:` (scoping bridge artifact only; no source changes; per-slice implementations will land as `feat:` / `refactor:` commits)

## Claim

This proposal formalizes the scoping of `GTKB-ARTIFACT-RECORDER-CLI` — the named first concrete manifestation of the Deterministic Services Principle (`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, citing `.claude/rules/acting-prime-builder.md` § Deterministic Services Principle). The proposal does NOT request authorization for any individual implementation slice; each implementation slice will file its own bridge thread and independently satisfy the Mandatory Specification Linkage Gate and the Mandatory Specification-Derived Verification Gate before receiving `GO` or `VERIFIED`.

The work moves formal-artifact insertion plumbing (deliberations, GOV/SPEC/PB/ADR/DCL/REQ records, owner-decision packets) behind a `gt <artifact-type> record` CLI in `groundtruth-kb`. The service handles ID generation, SHA computation, approval-packet construction, KB insertion, and ChromaDB indexing as deterministic operations rather than AI-mediated boilerplate. AI surface drops from ~150 LOC of orchestration (manual `record_*.py` boilerplate + hand-constructed packet JSON + env-var threading) to a single CLI call with 6-8 structured arguments. The formal-artifact-approval-gate hook (`.claude/hooks/formal-artifact-approval-gate.py`) remains as defense-in-depth for raw-API anomalies.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is the canonical bridge workflow state; this proposal is filed as `-001` NEW and a corresponding line is inserted at top of the thread's active list.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal must cite all relevant specifications. This proposal re-cites the full applicable set.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires Specification-Derived Verification with spec-to-test mapping; per-slice proposals will provide concrete mappings.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — applications/<name>/ placement convention; this CLI runs as part of `groundtruth-kb` (the platform package). All CLI execution and output paths remain within `E:\GT-KB`; the service does not move or relocate application files. Cited because the proposal references `.claude/rules/project-root-boundary.md` and `.claude/rules/file-bridge-protocol.md` (path triggers per the spec-applicability registry).
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact approval requires the proposed change request to be presented in native review format with full content and metadata before treated as canonical project truth; per-artifact approval packets at `.groundtruth/formal-artifact-approvals/<date>-<artifact-id>.json`. The CLI service MUST preserve this contract.
- `PB-ARTIFACT-APPROVAL-001` — companion protected-behavior. The CLI service MUST NOT bypass the approval-display + transcript-capture requirements.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` — companion architecture decision; same.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — companion design constraint; same. The defense-in-depth hook remains live.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the project is a collection of artifacts; this CLI promotes per-insertion ceremony into a service.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — candidate/specified/implemented/verified lifecycle terms used by the CLI service.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the load-bearing owner decision establishing the active-pursuit mandate for plumbing-to-service work. This proposal is its named first manifestation.
- `DELIB-0874` — artifact-oriented governance owner decision; the broader framing this proposal operationalizes.
- `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` — lifted the freeze that previously blocked `GTKB-ARTIFACT-RECORDER-CLI`; this proposal is now unblocked.
- `.claude/rules/acting-prime-builder.md` § Deterministic Services Principle — Prime Builder must surface repetitive plumbing as backlog items; this proposal is the formal surfacing for the artifact-recorder pattern. All work occurs within `E:\GT-KB`.
- `.claude/rules/operating-model.md` §1 and §2 — canonical terminology for application/project/work-item/specification used by the CLI surface.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol gates applicable to this scoping proposal and to each implementation slice.
- `.claude/rules/codex-review-gate.md` — review obligations.
- `.claude/rules/canonical-terminology.md` — terminology consumed by CLI flag names and help text.
- `.claude/rules/project-root-boundary.md` — 5 binding rules; CLI execution and all generated artifacts remain within `E:\GT-KB` (in-root); output paths are in-root.
- `.claude/rules/deliberation-protocol.md` — deliberation-search and archive-write obligations the CLI must preserve.
- `bridge/gtkb-narrative-artifact-approval-extension-001-001.md` — coupled thread (row 45 in `memory/work_list.md`); extends formal-artifact-approval to narrative artifacts. The narrative-artifact-approval-gate is parallel to the formal-artifact-approval-gate this CLI integrates with; the two threads will compose at the implementation layer.
- `bridge/gtkb-bridge-skill-unified-001-001.md` — coupled thread (row 46); the unified bridge skill consumes a similar service-CLI pattern.
- `bridge/gtkb-docs-quality-remediation-001.md` — adjacent scoping-pattern precedent (7-slice umbrella).

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (owner decision; load-bearing) — establishes that repetitive AI work is a defect; plumbing belongs in services. This proposal is the principle's named first concrete manifestation.
- `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE` (2026-04-27 S312) — the friction surface that originally prompted owner approval of this work. Inserting a `PB-ROLE-CONTRACT-EFFECTIVENESS-UPDATE` protected-behavior row required ~150 LOC of manual orchestration (Python script + packet JSON + env-var threading). The CLI surface is the structural answer to that friction.
- `DELIB-0874` (artifact-oriented governance) — the broader framing.
- `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` (2026-05-07) — lifted the freeze that previously blocked this thread; freeze-blocked status retired per work_list.md TOP section.
- Owner approval at S312 (2026-04-27) — captured durably at `memory/work_list.md` row 113 with the explicit "Owner-approved 2026-04-27 (S312)" line plus the S312 principle citation. The S332 default idle-work directive (2026-05-07) explicitly names `GTKB-ARTIFACT-RECORDER-CLI` in Band 2 (Acceleration / deterministic-services).
- Current-session owner directive (2026-05-11 S340) — owner explicitly directed Prime Builder to "Proceed with: Filing the GTKB-ARTIFACT-RECORDER-CLI proposal (largest principle-affirming win)" after the session-end synthesis of next-tranche priorities. Anchored in this session's chat transcript; this proposal is the direct consequence.
- Adjacent scoping-pattern precedents: `bridge/gtkb-docs-quality-remediation-001.md` (7-slice docs-quality umbrella, Slice 0 = scoping), `bridge/gtkb-narrative-artifact-approval-extension-001-001.md` (3-slice approval-extension scoping), `bridge/gtkb-bridge-skill-unified-001-001.md` (3-slice unified-skill scoping), `bridge/gtkb-membase-effective-use-recovery-2026-04-29-001.md` (scoping GO at -002 establishing the per-slice independent-gate pattern).

## Owner Decisions / Input

This scoping proposal depends on two owner authorizations:

1. **Owner approval at S312 (2026-04-27)** — durably captured at `memory/work_list.md` row 113. The S312 owner principle (verbatim, from `.claude/rules/acting-prime-builder.md` § Deterministic Services Principle): "Actively pursue opportunities to reduce repetitive work done by AI, both because it burns tokens unnecessarily and because AI-driven procedures have a higher error rate than simpler deterministic implementations. Project should be viewed as a collection of artifacts, rather than a dialog with accompanying activity." This work item is explicitly named as "the first concrete manifestation of that principle."

2. **Current-session owner directive (2026-05-11 S340)** — owner instructed: "Please proceed with: Filing the GTKB-ARTIFACT-RECORDER-CLI proposal (largest principle-affirming win)." Anchored in this session's chat transcript. This proposal is the direct consequence; no further owner-decision asks are required for proposal review.

No per-slice owner decisions are requested at this scoping level. Each implementation slice will file its own bridge thread, and owner-decision asks specific to that slice's scope (e.g., approval-flow integration choices) will be surfaced via AskUserQuestion at filing time per the AUQ-only enforcement stack.

## Live State Probed

```text
$ ls scripts/record_*.py 2>&1 | head -10
(probe at proposal-time; existing record_*.py orchestrators inventoried per Slice 1 scope)

$ grep -rn "insert_deliberation\|insert_spec\|insert_protected_behavior\|insert_owner_decision" groundtruth-kb/src/groundtruth_kb/db.py 2>&1 | head -10
(insertion API surface enumerated; CLI service will consume these methods)

$ ls .groundtruth/formal-artifact-approvals/ 2>&1 | head -5
(existing approval packets inventoried; CLI service emits the same packet shape)

$ ls .claude/hooks/formal-artifact-approval-gate.py
.claude/hooks/formal-artifact-approval-gate.py
(defense-in-depth gate present; remains live post-CLI-deployment)

$ python -c "from groundtruth_kb.db import KnowledgeDB; print('OK')"
OK
(KB Python API importable; CLI service composes via this module)
```

Detailed live-state inventories deferred to each implementation slice's proposal. The Slice 0 scoping commitment is that each per-slice proposal will probe live state at filing time and quote the actual output (per the feedback memory `feedback_probe_live_state_before_quoting_counts.md`).

## Implementation Plan (Slices)

This scoping proposal identifies 6 implementation slices. Per Codex's MemBase-recovery scoping precedent at `bridge/gtkb-membase-effective-use-recovery-2026-04-29-002.md`, each slice files its own bridge thread and independently satisfies the mandatory gates.

### Slice 1 — `gt deliberation record` (highest-leverage entry point)

Add the deliberation-record subcommand to the existing `gt` CLI. Service handles:
- ID generation: `DELIB-<NNNN>` or `DELIB-<TAG>-<NNNN>` per existing schema.
- SHA computation: content hash for tamper-detection.
- Approval packet construction: emits `.groundtruth/formal-artifact-approvals/<date>-DELIB-<NNNN>.json` matching the existing gate's expected shape.
- KB insertion: `KnowledgeDB.insert_deliberation(...)` with full provenance fields.
- ChromaDB indexing: semantic-search registration for the new record.

Acceptance: A single `gt deliberation record --source-type owner_conversation --outcome owner_decision --question "..." --options "..." --selected-option "..." --rationale "..."` invocation produces the same result as today's ~150-LOC scripted record_deliberation flow.

### Slice 2 — `gt spec record` for GOV/SPEC/PB/ADR/DCL/REQ subtypes

Extend the CLI to cover the full spec-subtype matrix. Each subtype shares the same packet/ID/SHA/insertion mechanics but with subtype-specific schema validation (e.g., `PB-*` requires assertions field; `ADR-*` requires alternatives-considered).

Acceptance: One `gt spec record --type <subtype> ...` invocation per subtype produces the same result as today's per-subtype scripts.

### Slice 3 — Service backend module `groundtruth_kb.artifact_recorder`

Refactor Slice 1 + Slice 2 entry points to share a common backend module (`groundtruth_kb.artifact_recorder`) so the CLI commands are thin wrappers and the recording logic is library-callable from Python (e.g., for hook-internal or skill-internal use).

Acceptance: `from groundtruth_kb.artifact_recorder import record_deliberation, record_spec` returns the same record IDs as the CLI commands; the CLI commands delegate to the module rather than reimplementing logic.

### Slice 4 — Approval-flow integration with formal-artifact-approval-gate

Codify the contract between the CLI service and `.claude/hooks/formal-artifact-approval-gate.py`. The CLI emits a packet, then performs the insertion; the hook validates the packet at any subsequent Write/Edit to the protected MemBase row. The hook MUST continue to function as defense-in-depth even when the CLI is bypassed.

Acceptance: Hook test fixture asserts that a CLI-emitted packet satisfies the hook's pattern matching; an absent packet still fails the hook independently of the CLI.

### Slice 5 — Migration of existing `record_*.py` callers

Convert each existing record_*.py script in `scripts/` to a thin wrapper that calls the CLI (or the underlying module). Migration preserves behavior; legacy callers continue to function during the transition.

Acceptance: Pre-migration record_*.py and post-migration record_*.py produce byte-identical packet output for the same inputs (golden-file comparison).

### Slice 6 — Hook-relaxation contract (defense-in-depth retention discipline)

Document the contract under which the formal-artifact-approval-gate remains live AFTER the CLI deployment. The CLI does not replace the hook; the hook validates that any Write/Edit to a protected MemBase row carries the matching packet, regardless of whether the row was inserted via the CLI or via raw API access.

Acceptance: A spec-derived test asserts the hook's blocking behavior under three conditions: (a) CLI-emitted packet matches → pass; (b) raw API insertion without packet → fail; (c) tampered packet (SHA mismatch) → fail.

## Tests Derived From Linked Specifications

Slice 0 (this proposal) introduces no executable tests; the scoping artifact itself is the deliverable. Each implementation slice will provide its own spec-derived test suite per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`. Test families anticipated across slices:

| Test family | Verifies | Linked spec |
|---|---|---|
| T-recorder-cli-* | CLI surface (flags, help text, error messages) matches the documented contract | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` |
| T-recorder-packet-* | Approval-packet shape + content hash matches existing gate expectations | `GOV-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` |
| T-recorder-kb-insertion-* | KB row inserted with expected metadata; SHA computed correctly | `GOV-ARTIFACT-APPROVAL-001` |
| T-recorder-chroma-* | ChromaDB indexing fires; record discoverable via `gt deliberations search` | `.claude/rules/deliberation-protocol.md` |
| T-recorder-hook-defense-* | Defense-in-depth gate continues to block raw-API insertions without packets | `PB-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` |
| T-recorder-migration-* | Pre-migration vs post-migration golden-file comparison for record_*.py callers | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |

## Verification Commands

Slice 0 verification is the bridge applicability + clause preflights passing on this `-001` file, plus owner / Codex acknowledgement of the scoping commitment. No code-execution verification at Slice 0.

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-artifact-recorder-cli
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-artifact-recorder-cli
```

## Risks and Rollback

### Risks

| Risk | Mitigation |
|------|------------|
| **R1** — CLI surface drift (flags evolve faster than tests) | Per-slice spec-derived tests anchored to a canonical CLI-surface specification; tests fail when the surface changes without spec update |
| **R2** — Approval-packet schema evolution breaks downstream consumers (defense-in-depth hook, audit tooling) | Slice 4 codifies the packet contract; per-slice tests cover packet-shape evolution; the gate hook acts as the canary |
| **R3** — ChromaDB indexing failure leaves MemBase ahead of ChromaDB (drift between authoritative store and semantic index) | Slice 3 service backend includes index-write retry + dedicated test coverage; existing `gt deliberations re-index` recovery path remains operational |
| **R4** — Migration of historical `record_*.py` callers introduces behavior regression | Slice 5 uses byte-identical golden-file comparison; any divergence fails the migration acceptance |
| **R5** — Defense-in-depth hook erosion (well-intentioned removal because "CLI handles it") | Slice 6 makes hook retention an explicit contract with a spec-derived test asserting the hook remains live |

### Rollback (Slice 0)

This scoping proposal has minimal rollback: removal of `bridge/gtkb-artifact-recorder-cli-001.md` and reversion of the `bridge/INDEX.md` entry. No source changes are made at Slice 0.

### Rollback (per-slice)

Each implementation slice provides its own rollback procedure aligned to the change set. Slices 1-3 (CLI + module) are pure-addition (no removal of existing functionality during transition); rollback is `git revert <commit>`. Slice 5 (migration) keeps existing record_*.py callers functional during transition; rollback is reverting individual caller migrations.

## Acceptance Criteria (Slice 0 — Scoping)

1. Bridge applicability preflight on `bridge/gtkb-artifact-recorder-cli-001.md` passes with `missing_required_specs: []` and `missing_advisory_specs: []`.
2. Clause preflight passes with `Blocking gaps (gate-failing): 0`.
3. `bridge/INDEX.md` updated with `NEW: bridge/gtkb-artifact-recorder-cli-001.md` entry at the top of the active list.
4. Codex review issues `GO` on this Slice 0 scoping proposal, authorizing per-slice implementation thread filings.
5. The per-slice independence pattern is preserved (each Slice 1-6 files its own bridge thread; this scoping `GO` does NOT authorize any specific implementation slice).
6. Future per-slice proposals cite this `-001` document in their Specification Links.

## Out of Scope (Slice 0)

- Implementation of any individual slice (each requires its own bridge thread + Codex GO before code lands).
- Adopter-side CLI distribution (consumed via `gt project upgrade` post-upstream-VERIFIED of all relevant slices).
- Migration of historical KB records inserted before the CLI's existence (only future records use the new CLI; historical records remain at their existing row shape).
- Cross-harness skill exposure for the CLI (the parallel `GTKB-BRIDGE-SKILL-UNIFIED-001` thread covers harness-side skill surfaces; this thread covers the underlying CLI/service).
- Owner-decision-tracker integration (the tracker is a Stop-mode hook for prose-decision-ask detection; the CLI is a Write-time service for canonical-artifact insertion; both gates compose orthogonally).

## Pre-Filing Applicability Preflight

Run post-write, with INDEX entry inserted:

```text
$ python scripts/bridge_applicability_preflight.py --bridge-id gtkb-artifact-recorder-cli
```

Expected output: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. packet_hash captured below post-run.

## Coupling with Other In-Flight Threads

- `GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-001` (work_list.md row 45; bridge -001 awaits GO/NO-GO) — extends formal-artifact-approval to narrative artifacts. The narrative-artifact-approval-gate is structurally parallel to the formal-artifact-approval-gate this CLI integrates with. When the narrative extension lands, this CLI's service should also emit narrative-artifact-approval packets where applicable (currently the protected narrative-artifact path set is documented in `config/governance/narrative-artifact-approval.toml`).
- `GTKB-BRIDGE-SKILL-UNIFIED-001` (work_list.md row 46; bridge -001 awaits GO/NO-GO) — exposes a unified bridge skill across Claude + Codex harnesses. Both threads consume the same underlying service-CLI pattern; this thread provides the artifact-recording counterpart.
- `GTKB-DOCS-QUALITY-REMEDIATION` (S336 umbrella; bridge -001 NEW) — sibling scoping-pattern precedent (7-slice umbrella).

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
