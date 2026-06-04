# Owner Decisions Capture — Platform SoT Consolidation Project

**Date:** 2026-06-04 UTC
**Captured by:** Claude Code Prime Builder (harness B)
**Session:** interactive Prime Builder session, `::init gtkb pb`
**Classification:** Notepad-tier capture per ADR-0001 — intended for insertion into the Deliberation Archive (`source_type=owner_conversation`, `outcome=owner_decision`) once the impl-start-gate clears (currently blocked by `bridge/gtkb-impl-start-target-paths-preflight-008` awaiting LO review).
**Precedent:** Mirrors the `DELIB-20260668` 8-AUQ owner-decision pattern from `PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION` Phase 1.

---

## Source Directive

Owner directive, 2026-06-04, session prompt (verbatim):

> Agent operating guidance and directives or other regularly referenced information are fragmented across multiple directories and artifacts. For example, I recently discovered that many artifacts within the independent-progress-assessments directory were being used as the SoT for agent configuration directives.
>
> This fragmentation is creating drift and knowledge loss.
>
> We need to ensure that all non-ephemeral (durable, frequently used, change-controlled) data is stored in documented locations with tight version control and identification in the GT-KB artifacts registry.
>
> Please scan every known document in the project to find those which contain SoT or other frequently referenced data and propose a plan to consolidate and reconcile all SoT within a strict hierarchical structure that we can track (versioning, backups/install, health checks, etc).

---

## Research Output

Research scan and proposal options surfaced in:
`memory/research_sot_consolidation_2026_06_04.md` (this session).

Findings: 22 SoT classes, 10 partial registries (R1–R10), 42+ existing doctor checks, 7+ visible drift instances. Three structural options surfaced (A/B/C).

---

## 7-Question AUQ Pass

All 7 questions presented via `AskUserQuestion` tool with `presented_to_user=true` and `transcript_captured=true`. Each owner answer recorded below verbatim.

### Decision 1 — Project scope

**Question:** How should the broader SoT-consolidation work relate to the in-flight harness-state project?

**Options presented:**
- A. Umbrella (Recommended): file `PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION` as parent; harness-state Phase 1 becomes Slice 2.
- B. Siblings: broader project covers only meta-registry + governance + doctor + retirement pathway; each per-domain consolidation as its own sibling.
- C. Convert: retire harness-state project and re-do under umbrella (not recommended).

**Owner answer:** **A — Umbrella (Recommended)**

**Implication:** New parent project `PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION`. `PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION` (active, Phase 1 REVISED-003 awaiting LO) becomes Slice 2 in flight. Existing PAUTH preserved; no re-do.

### Decision 2 — Structural option for the registry mechanism

**Question:** Which structural option for the SoT registry mechanism?

**Options presented:**
- A. TOML-Federated (one TOML file + Python loader + doctor check).
- B. MemBase-Native (`sot_artifacts` table + `gt registry` CLI).
- C. Hybrid TOML + MemBase projection (Recommended; mirrors `harness-registry.json` pattern).

**Owner answer:** **C — Hybrid TOML + MemBase projection (Recommended)**

**Implication:** TOML file is the human-edit surface; MemBase `sot_artifacts` table is the projection. Edits flow: TOML → bridge → formal-artifact-approval packet → loader validates → MemBase regen. Doctor validates (a) TOML ↔ MemBase parity, (b) registry ↔ on-disk reality. Requires new governance: `GOV-PLATFORM-SOT-REGISTRY-001`, `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`.

### Decision 3 — Registry storage location

**Question:** Where should the registry TOML edit-surface live?

**Options presented:**
- A. `config/registry/` new directory.
- B. `config/governance/` extend existing.

**Owner answer:** **A — `config/registry/` new directory**

**Implication:** Path: `config/registry/sot-artifacts.toml`. New dedicated directory for cross-cutting registry surfaces; clear semantic separation from `config/governance/` (per-domain policy registries).

### Decision 4 — IPA disposition policy

**Question:** Disposition policy for IPA legacy surfaces that have canonical mirrors in `.claude/rules/codex-*`?

**Options presented:**
- A. Archive into `archive/ipa-legacy-2026-06-04/` with redirect (Recommended).
- B. Deprecation banner, leave in place.
- C. Delete (git history preserves).
- D. Per-file owner AUQ.

**Owner answer:** **A — Archive into `archive/ipa-legacy-2026-06-04/` with redirect (Recommended)**

**Implication:** Slice 5 work item: move IPA Codex operating contracts (CODEX-WAY-OF-WORKING, CODEX-LOYAL-OPPOSITION-RUNBOOK, CODEX-KNOWLEDGE-BASE-INDEX, CODEX-DECISION-LEDGER, CODEX-DEAD-ENDS-AND-FALSE-POSITIVES, CODEX-REVIEW-CHECKLISTS, TEMPLATE-CODE-REVIEW, TEMPLATE-DECISION-MEMO) into `archive/ipa-legacy-2026-06-04/`. Leave `independent-progress-assessments/CODEX-MOVED-TO-ARCHIVE.md` pointing to `.claude/rules/codex-*` as canonical. Preserves provenance; removes drift surface from active workspace. Note: `CODEX-INSIGHT-DROPBOX/` IS the canonical LO advisory channel — NOT in scope for archive.

### Decision 5 — MEMORY.md cap remediation

**Question:** MEMORY.md cap remediation approach (currently at 60KB vs 24.4KB limit)?

**Options presented:**
- A. All three: archive + retention + index discipline (Recommended).
- B. Archive completed entries only.
- C. Index-length doctor check only.
- D. Defer — file separate slice.

**Owner answer:** **A — All three: archive + retention + index discipline (Recommended)**

**Implication:** Slice 6 work item: (a) move completed-work entries into `memory/completed/<topic>/` tier with cross-references; (b) new doctor check enforces 60-day retention auto-flag for archival; (c) new doctor check enforces existing `<200-char` index-entry spec.

### Decision 6 — Doctor severity

**Question:** Initial severity for the new `_check_sot_registry_completeness` doctor check?

**Options presented:**
- A. WARN initially, promote to ERROR after stabilization (Recommended).
- B. ERROR immediately (release-blocking).
- C. INFO (awareness-only).

**Owner answer:** **A — WARN initially, promote to ERROR after stabilization (Recommended)**

**Implication:** Slice 1 ships `_check_sot_registry_completeness` at `WARN` severity so the inventory can be backfilled across slices without false-failing the doctor. Promote to `ERROR` (release-blocking) once all 22 SoT classes are registered and parity-stable. Matches the cautious-promotion pattern used for `_check_managed_artifact_drift`. Promotion is a separate owner decision tracked as a downstream WI in the umbrella.

### Decision 7 — Adopter rollout cadence

**Question:** Adopter rollout cadence for the SoT registry?

**Options presented:**
- A. Hold for v0.7.0 stable (Recommended).
- B. Ship in v0.7.0-rc1 (current release).
- C. Defer adopter rollout indefinitely.

**Owner answer:** **A — Hold for v0.7.0 stable (Recommended)**

**Implication:** Registry pattern ships to GT-KB internal first. Adopter scaffolding (Slice 7) gates on v0.7.0 stable. v0.7.0-rc1 release lane stays focused on existing scope. Adopters get the registry in the next stable cut after rc1.

---

## DELIB-Insertion Plan

When the impl-start-gate clears (after `bridge/gtkb-impl-start-target-paths-preflight-008` resolves):

1. Insert this capture as DELIB via `gt deliberations add` or `python -m groundtruth_kb.deliberations add` with:
   - `source_type='owner_conversation'`
   - `outcome='owner_decision'`
   - `session_id` = current session ID
   - `presented_to_user=true`
   - `transcript_captured=true`
   - `title='Platform SoT Consolidation — 7-AUQ owner decision capture (2026-06-04)'`
   - body = this file's content (or a condensed citation)
2. Note resulting `DELIB-NNNN` ID.
3. Cite that DELIB-NNNN ID in the umbrella bridge proposal's `Prior Deliberations` section.

## Active Bridge Threads to Coordinate With

- `gtkb-impl-start-target-paths-preflight-008` (currently blocking mutations) — must resolve before umbrella filing.
- `gtkb-harness-state-sot-consolidation-phase-1-003` (REVISED awaiting LO) — becomes Slice 2 once umbrella files.
- `gtkb-document-author-provenance-contract-004` (GO for Prime) — independent; coordinate but does not block.
- `GTKB-STARTUP-REFRACTOR-001` outstanding slices — folded into Slice 3 of umbrella.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Notepad-tier artifact per ADR-0001. Recorded as DELIB-20260671 (2026-06-04, `owner_presented=true`, `outcome=owner_decision`).*
