# DRAFT — to be filed as `bridge/gtkb-platform-sot-consolidation-umbrella-001.md`

> **Status:** DRAFT in notepad tier (`memory/`). Not yet filed as a bridge proposal.
> **Reason for delay:** `bridge/gtkb-impl-start-target-paths-preflight-008.md` is currently awaiting Loyal Opposition review; the impl-start-gate is blocking all writes to protected paths (including `bridge/`) until that thread resolves. When the gate clears:
> 1. Run pre-filing preflights (`bridge_applicability_preflight.py`, `adr_dcl_clause_preflight.py`).
> 2. Insert the owner-decision DELIB from `memory/sot_consolidation_owner_decisions_2026_06_04.md` and capture the `DELIB-NNNN` ID.
> 3. Mint umbrella PAUTH (Slice-1 scope only; deferring per-domain Slice PAUTHs to child bridges).
> 4. Acquire work-intent claim: `python scripts/bridge_claim_cli.py claim gtkb-platform-sot-consolidation-umbrella`.
> 5. Write this file (with the DELIB-ID substituted) as `bridge/gtkb-platform-sot-consolidation-umbrella-001.md`.
> 6. Edit `bridge/INDEX.md` to insert `Document: gtkb-platform-sot-consolidation-umbrella` + `NEW: bridge/gtkb-platform-sot-consolidation-umbrella-001.md` at the top.

---

NEW

# Platform SoT Consolidation — Governance Umbrella + Slice Sequence

bridge_kind: governance_review
Document: gtkb-platform-sot-consolidation-umbrella
Version: 001
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-04 UTC
Recipient: Loyal Opposition (Codex, harness A)
Project: PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-UMBRELLA-SLICE-1-GOVERNANCE-ENVELOPE (to be minted)

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 52868963-6210-4aa4-8add-d5b3751a3544
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, interactive session

target_paths: []
requires_verification: false
implementation_scope: governance_only

## Why governance_review

This umbrella covers a multi-slice project across 7 slices and dozens of WIs. Each child impl bridge declares its primary Work Item, owns its own PAUTH, and carries executable verification. The umbrella's deliverable is the design + governance contract Codex GOs on, then the children execute. Same structural reasoning as `bridge/gtkb-harness-state-sot-consolidation-phase-1-001.md` (which itself becomes Slice 2 of this umbrella).

## Summary

**Owner directive (2026-06-04):**

> Agent operating guidance and directives or other regularly referenced information are fragmented across multiple directories and artifacts. … We need to ensure that all non-ephemeral (durable, frequently used, change-controlled) data is stored in documented locations with tight version control and identification in the GT-KB artifacts registry. Please scan every known document in the project to find those which contain SoT or other frequently referenced data and propose a plan to consolidate and reconcile all SoT within a strict hierarchical structure that we can track (versioning, backups/install, health checks, etc).

**Owner-grilling pass (per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` discipline — voluntarily applied; the gate fires only for adopt/adapt LO advisories, but the discipline applies broadly to project-envelope filing):** 7-AUQ pass conducted in session 2026-06-04 with all 7 decisions captured at `memory/sot_consolidation_owner_decisions_2026_06_04.md`. To be inserted as DELIB-NNNN once impl-start-gate clears.

**Research basis:** `memory/research_sot_consolidation_2026_06_04.md` (this session) — inventories 22 SoT classes, 10 partial registries, 42+ existing doctor checks, 7+ visible drift instances.

The umbrella seeks GO on:

1. **New governance specs (to be drafted post-GO, per Slice 1):**
   - `GOV-PLATFORM-SOT-REGISTRY-001` — declares every SoT class MUST be registered; un-registered SoT is a defect; extends `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` and `GOV-08`.
   - `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` — TOML edit-surface MUST match MemBase projection; drift is assertion-failing.
   - `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` — per-record schema for `{domain, lifecycle, storage_path, authority_spec_id, mutation_api, versioning_policy, backup_policy, health_check_function, owner_role, depends_on}`.
2. **Slice sequence** (umbrella authorizes the sequencing; per-slice PAUTHs are child responsibilities).
3. **IPA disposition policy** (owner decision 4): archive into `archive/ipa-legacy-2026-06-04/` with redirect README at `independent-progress-assessments/CODEX-MOVED-TO-ARCHIVE.md`.
4. **MEMORY.md cap remediation policy** (owner decision 5): archive completed-work tier + 60-day retention doctor check + index-length doctor check.
5. **Doctor severity policy** (owner decision 6): `WARN` initially for `_check_sot_registry_completeness`; promotion to `ERROR` is a separate downstream WI.
6. **Adopter rollout policy** (owner decision 7): registry pattern is GT-KB internal until v0.7.0 stable; adopter scaffolding gates on stable cut.

**Explicit boundary:** EXCLUDED — modification of canonical SoT data values (the registry tracks artifacts, not their contents); v0.7.0-rc1 release-lane work (registry is GT-KB-internal until v0.7.0 stable per owner decision 7); per-domain consolidation execution (delegated to child slices); adopter rollout (Slice 7 only).

## Specification Links

| Spec | Severity | Trigger | How this umbrella complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via bridge/INDEX.md as NEW versioned bridge file; INDEX entry inserted after Write. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section exists with comprehensive citation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification, spec-to-test | governance_review with `requires_verification: false`; child impl bridges carry per-spec test mapping. See §Specification-Derived Verification Plan. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | blocking | content:source of truth, cited paths | This project DIRECTLY EXTENDS this governance from per-domain (harness-state) to platform-wide. New `GOV-PLATFORM-SOT-REGISTRY-001` cites GOV-SOURCE-OF-TRUTH-FRESHNESS-001 as parent authority. |
| `GOV-08` (KB is truth) | blocking | foundational | Registry inventory ultimately resolves against MemBase as canonical; this project doesn't weaken KB-as-truth, it extends the tracking discipline TO MemBase records that are themselves SoT classes. |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | content:ADR/DCL/GOV/spec inserts | 3 formal-artifact-approval packets needed for the new GOV + 2 DCLs; generated after umbrella GO + owner per-packet approval per Slice 1. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH, path:project authorization | Umbrella PAUTH (to be minted) cited; per-slice PAUTHs are child responsibility. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | Umbrella PAUTH will cite this DELIB as owner-decision, include the slice sequence as scope, enumerate forbidden operations (registry-record-content mutation vs registry-membership mutation are distinct). |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH will cite the 3 new framing specs (or, pre-GO, the operating-model + GOV-SOURCE-OF-TRUTH-FRESHNESS-001 anchor). |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items inserts | Per-slice WIs inserted as canonical backlog rows; project membership recorded; umbrella PAUTH includes slice WI list. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:specification, ADR, DCL, work item, owner decision | 7 owner decisions, 3 new specs (to be drafted), 1 DELIB (to be inserted), 7 slice projects/sub-projects, multiple WIs — fully artifact-routed. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation | Project enumerates artifact reorganization (registry + governance + doctor + retired-paths inventory + adopter scaffolding). |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:verified | Umbrella terminal at GO; children terminal at VERIFIED. |
| `DCL-CONCEPT-ON-CONTACT-001` | advisory | content:new concepts | "platform SoT registry", "registry projection parity", "SoT class lifecycle" — new concepts surfaced in spec drafts; glossary updates land via a Slice-1 WI. |
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` | not-applicable | adopt/adapt LO advisory | Project source is direct owner directive, not LO advisory. Gate doesn't fire; owner-grilling discipline applied voluntarily via 7-AUQ pass, captured in `memory/sot_consolidation_owner_decisions_2026_06_04.md`. |
| `GOV-AUQ-POLICY-ENGINE` family (AUQ-only enforcement stack) | blocking | content:owner decision | 7 in-scope owner decisions collected via `AskUserQuestion` (not prose); audit trail in `memory/sot_consolidation_owner_decisions_2026_06_04.md`. |

## Requirement Sufficiency

**Existing requirements sufficient.** Owner directive + 7 AUQ decisions resolve all material requirement-disambiguation questions for the umbrella scope. The 3 new specs (GOV + 2 DCLs) drafted in Slice 1 are governance/design artifacts derived from those decisions, not new requirements.

## Prior Deliberations

- `DELIB-NNNN` (to be assigned) — owner decision record for the 7-AUQ platform SoT consolidation scope. Source content: `memory/sot_consolidation_owner_decisions_2026_06_04.md`.
- `DELIB-20260668` — owner decision record for the 8-AUQ harness-state SoT consolidation scope (the precedent this umbrella generalizes).
- `DELIB-20260669` — session-harvest drift evidence for registry vs legacy mirror divergence (harness-state-specific; cited as evidence pattern for cross-domain drift).
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-001.md` (NEW) and `-002.md` (NO-GO) and `-003.md` (REVISED, awaiting LO) — the in-flight thread that becomes Slice 2 of this umbrella.
- `bridge/gtkb-startup-refractor-slice-a-startup-control-inventory-002.md` (GO) — established the inventory + lifecycle classification pattern this umbrella generalizes to platform-wide SoT.
- `bridge/gtkb-managed-artifact-registry-008.md` (Codex GO) — established the managed-artifacts.toml registry + loader + lifecycle-axes + doctor-check pattern this umbrella applies to platform-wide SoT.
- `memory/research_sot_consolidation_2026_06_04.md` — research file (notepad tier) that scoped the work; inventories 22 SoT classes + 10 partial registries + 42+ doctor checks + 7+ drift sources + 3 structural options.

No previously rejected approach is being revisited. The 3 structural options (A: TOML-only, B: MemBase-only, C: Hybrid) were surfaced in the research file; owner selected C explicitly via AUQ.

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate. The 7-AUQ owner decisions authorizing this umbrella:

| AUQ # | Question (short) | Owner answer | Captured at |
|---|---|---|---|
| 1 | Project scope (umbrella vs sibling vs convert) | **Umbrella** — `PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION` parent; harness-state Phase 1 becomes Slice 2 | `memory/sot_consolidation_owner_decisions_2026_06_04.md` §Decision 1 |
| 2 | Structural option (A/B/C) | **C — Hybrid TOML + MemBase projection** | §Decision 2 |
| 3 | Registry storage location | **`config/registry/`** new directory; path `config/registry/sot-artifacts.toml` | §Decision 3 |
| 4 | IPA disposition policy | **Archive** into `archive/ipa-legacy-2026-06-04/` + redirect README | §Decision 4 |
| 5 | MEMORY.md cap remediation | **All three** (archive + 60-day retention + index-length doctor check) | §Decision 5 |
| 6 | `_check_sot_registry_completeness` severity | **WARN initially**, promote to ERROR after stabilization | §Decision 6 |
| 7 | Adopter rollout cadence | **Hold for v0.7.0 stable** | §Decision 7 |

All 7 decisions collected via `AskUserQuestion` tool with `presented_to_user=true` and `transcript_captured=true`. Capture file is notepad-tier pending DELIB insertion (impl-start-gate currently blocking; see Operational Constraints below).

## Slice Sequence (Umbrella-Authorized)

| Slice | Subject | Bridge slug | Status | Authority |
|---|---|---|---|---|
| **0** | Inventory + design ratification | this umbrella | NEW (this filing) | direct owner directive |
| **1** | Governance scaffolding: `GOV-PLATFORM-SOT-REGISTRY-001`, `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`, `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`, registry TOML scaffold at `config/registry/sot-artifacts.toml`, MemBase `sot_artifacts` table, `gt registry` CLI, `_check_sot_registry_completeness` doctor at WARN | `gtkb-platform-sot-consolidation-slice-1-governance-001` | TO BE FILED | new GOV/DCLs + formal-artifact-approval packets |
| **2** | Harness-state SoT (in flight) | `gtkb-harness-state-sot-consolidation-phase-1-*` (existing) | REVISED-003 awaiting LO | existing PAUTH preserved |
| **3** | Startup-control SoT — finishes `GTKB-STARTUP-REFRACTOR-001` outstanding slices; deprecates `config/agent-control/CONTROL-MAP.md`, `REVIEW-MODE-SETUP.md` | `gtkb-startup-refractor-slice-c-overlays-001` (or successor) | TBD per startup-refractor sequence | extends existing project |
| **4** | Bridge-protocol SoT — registers `bridge/INDEX.md`, `.gtkb-state/work-intent/`, dispatch-state, claim contract with health-check pointers; deprecates `.claude/rules/bridge-poller-canonical.md` stub | `gtkb-platform-sot-consolidation-slice-4-bridge-protocol-001` | TBD | new |
| **5** | IPA legacy retirement — execute owner decision 4: archive IPA Codex operating contracts to `archive/ipa-legacy-2026-06-04/`; leave redirect README; preserve `CODEX-INSIGHT-DROPBOX/` as live LO advisory channel | `gtkb-platform-sot-consolidation-slice-5-ipa-retirement-001` | TBD | new + per-file owner AUQ if any file has non-obvious value |
| **6** | `memory/` cleanup — execute owner decision 5: archive completed-work tier; new 60-day retention doctor check; new index-length doctor check | `gtkb-platform-sot-consolidation-slice-6-memory-remediation-001` | TBD | new |
| **7** | Adopter scaffolding — extend `groundtruth-kb/templates/managed-artifacts.toml` to scaffold the SoT registry into adopter projects; doctor check ports to adopter; gates on v0.7.0 stable per owner decision 7 | `gtkb-platform-sot-consolidation-slice-7-adopter-001` | TBD (v0.7.0 stable) | new |

Per-slice PAUTHs and per-slice work items are child-bridge responsibilities. The umbrella authorizes the sequencing and the governance contract, NOT the per-slice implementation work.

## Specification-Derived Verification Plan

This umbrella is governance-review-only with `target_paths: []` and `requires_verification: false`. Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, the actual spec-to-test mapping lives in each child slice's bridge proposal and implementation report. The umbrella's verification is structural:

- Slice 1 must verify: `GOV-PLATFORM-SOT-REGISTRY-001` is inserted with `presented_to_user=true`; `config/registry/sot-artifacts.toml` exists and loads without `InvalidArtifactRecord`; MemBase `sot_artifacts` table exists; `gt registry list` returns the bootstrap inventory; `_check_sot_registry_completeness` runs at WARN and reports the registered-vs-discovered gap accurately.
- Slice 2 verification continues per existing `gtkb-harness-state-sot-consolidation-phase-1-*` thread.
- Slices 3–7 carry their own per-spec verification matrices when filed.
- Umbrella terminal: GO on this proposal.

## Risk and Rollback

**Risk** is moderate. The umbrella generalizes an existing pattern (managed-artifacts.toml + harness-state Phase 1) to a wider scope. Specific risks:

- **Bootstrapping:** the SoT registry is itself an SoT class. Slice 1 must self-register the registry first to avoid the "who watches the watchmen" gap. Plan: registry's row 1 is itself.
- **Drift between TOML and MemBase projection.** Mitigated by `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` and the doctor check (TOML ↔ MemBase parity assertion).
- **Slice scope creep.** Each slice should land in <50 days of LO-Codex review cycle; if a slice grows beyond that, split.
- **Active bridge conflicts.** The in-flight `gtkb-harness-state-sot-consolidation-phase-1-003` and `gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-007` continue under their own PAUTHs. Umbrella does not interfere with them; they become Slices 2 and 3 retroactively.
- **MEMORY.md cap remediation may break the auto-memory index temporarily.** Mitigated by Slice 6 sequencing: archive first, retention check second, index-length check third. Each step is independently reversible via git.

**Rollback** is straightforward at the umbrella level. If LO NO-GOs the umbrella, the in-flight slice (harness-state Phase 1) continues under its own PAUTH unaffected; no other slice has been filed yet. If LO GOs the umbrella but a later slice is problematic, the umbrella is preserved and the problematic slice is revised; no rollback of the umbrella is required.

## Operational Constraints (at time of drafting)

- **impl-start-gate blocking writes.** `bridge/gtkb-impl-start-target-paths-preflight-008.md` is currently awaiting Loyal Opposition review; the gate blocks all mutations to protected paths (including `bridge/`) until that thread resolves. This draft lives in `memory/` (notepad tier, unblocked) pending filing. See the header banner for the filing checklist.
- **Pre-filing preflights must pass.** When ready to file:

  ```text
  python scripts/bridge_applicability_preflight.py --bridge-id gtkb-platform-sot-consolidation-umbrella --content-file <this-file>
  python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-platform-sot-consolidation-umbrella --content-file <this-file>
  ```

  Expected: `preflight_passed: true`, `missing_required_specs: []`, no blocking clause gaps.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight Subsection, both preflights must pass before filing. Expected result documented above.

## Recommended Outcome

**GO** for the governance umbrella, with child slices following the §Slice Sequence table.

LO is asked to verify:

1. Slice sequence is coherent and child slices are tractable.
2. Authority chain `GOV-08` → `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` → `GOV-PLATFORM-SOT-REGISTRY-001` (Slice 1) is sound.
3. Umbrella does not block the in-flight harness-state Phase 1 (which becomes Slice 2 with no re-do).
4. Owner-decision evidence in `Owner Decisions / Input` section is adequate (it's notepad-tier pending DELIB insertion; LO may NO-GO requesting DELIB insertion first if the impl-start-gate has cleared by review time).
5. Risk and rollback assessment is reasonable.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*DRAFT — not yet filed as a bridge proposal. Notepad-tier per ADR-0001.*
