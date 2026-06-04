# Research: SoT Consolidation & Platform-Wide Artifact Registry

**Date:** 2026-06-04
**Author:** Claude Code Prime Builder (harness B)
**Session role:** Prime Builder (interactive, via `::init gtkb pb`)
**Classification:** Research / advisory — *non-canonical* operational notepad per ADR-0001. Informs a future bridge proposal / project envelope; not itself a governance artifact.
**Source request:** Owner directive, 2026-06-04, in active session: "scan every known document in the project to find those which contain SoT or other frequently referenced data and propose a plan to consolidate and reconcile all SoT within a strict hierarchical structure that we can track (versioning, backups/install, health checks, etc)."
**Owner deliberation shape (AUQ this turn):** Owner picked "Advisory/research report first (no bridge yet)" → this artifact.

---

## TL;DR

GT-KB already has substantial SoT-tracking infrastructure, but it's **fragmented across ~9 partial registries** at different tiers (template / config / runtime / database / narrative). There is **no top-level cross-cutting Artifact Registry** that lists every SoT class and asserts on-disk reality matches the registered inventory. The owner's request is to build that umbrella.

This report:

1. Inventories the SoT classes found (§2).
2. Inventories existing partial registries (§3).
3. Inventories the doctor health-check surface (§4).
4. Identifies the drift sources the owner is fighting (§5).
5. Identifies the gaps a platform-wide registry would fill (§6).
6. Proposes 3 structural options (§7) and recommends Option C (hybrid TOML+MemBase, mirroring the `harness-registry.json` precedent).
7. Recommends a phased PROJECT envelope (§8) that **umbrellas the in-flight `PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION`** rather than competing with it.
8. Open owner decisions (§9).

A small set of concrete consolidation candidates is in §10.

---

## 1. Method & Caveats

**Scope.** Tracked files under `E:\GT-KB`, excluding `archive/`, `.claude/worktrees/`, `applications/Agent_Red/admin/node_modules/`, and `.gtkb-state/` (transient runtime). MemBase content was inferred from tracked schema files, terminology references, and CLAUDE.md's artifact-type table — direct DB queries were not run because the impl-start-gate is currently blocking Bash (bridge thread `gtkb-impl-start-target-paths-preflight-008` is awaiting LO review; see §11).

**Tools used.** `Read`, `Grep`, `Glob`. Read-only. No mutations to canonical artifacts. This file itself lands in `memory/` (notepad tier per ADR-0001), which the `kb-not-markdown` hook explicitly permits.

**Pending owner decision.** `DECISION-1019` (substrate=none investigation) is independent of this work and is not blocking.

---

## 2. SoT Classes Inventoried

Each row is an SoT *class*, not a single file. Filenames are illustrative; the class is the role the artifact plays.

| # | SoT class | Authority spec / rule | Storage | Versioning | Change-control mechanism | Health check today |
|---|---|---|---|---|---|---|
| 1 | Canonical specs / WIs / tests / procedures / DA / projects / PAUTHs | `GOV-08` (KB is truth); `GOV-ARTIFACT-APPROVAL-001` | `groundtruth.db` (SQLite) | Append-only per `UNIQUE(id,version)` | `gt` CLI + `groundtruth_kb` Python API; formal-artifact approval packets | `_check_db_schema`, `_check_orphan_citations`, assertion hook (SessionStart) |
| 2 | Canonical narrative rules | `GOV-ARTIFACT-APPROVAL-001`, narrative-artifact-approval-gate.py | `CLAUDE.md`, `AGENTS.md`, `.claude/rules/*.md`, application CLAUDE-*.md | Git-tracked; protected-path gate | `narrative-artifact-approval-gate.py` + per-artifact packet | `_check_rules`, narrative-artifact-approval gate (Write-time) |
| 3 | Canonical glossary | `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`, `DCL-CONCEPT-ON-CONTACT-001` | `.claude/rules/canonical-terminology.md` (+ `.toml` matrix) | Git-tracked + doctor matrix | Manual edit + per-term Tier A/B/C policy | `_check_canonical_terminology` + `_check_canonical_terms_registry` |
| 4 | Operating model (soft authority) | Cited by `loyal-opposition.md`, `AGENTS.md` | `.claude/rules/operating-model.md` | Git-tracked | Owner-approved bridge proposal + formal-artifact-approval packet | None (rule-cited soft authority, no mechanical enforcement) |
| 5 | Bridge protocol workflow state | `GOV-FILE-BRIDGE-AUTHORITY-001` + `.claude/rules/file-bridge-protocol.md` | `bridge/INDEX.md` + `bridge/*.md` | Append-only versioned files | Direct Write (gated by `bridge-compliance-gate.py`) | `_check_file_bridge_setup` |
| 6 | Bridge claim/work-intent | `bridge/INDEX.md` claim contract | `.gtkb-state/work-intent/*.json` (gitignored runtime) | Single-writer with TTL | `scripts/bridge_claim_cli.py` (`scripts/bridge_work_intent_registry.py`) | claim-presence enforced by `bridge-compliance-gate.py` |
| 7 | Bridge dispatch state | trigger script contract | `.gtkb-state/bridge-poller/dispatch-state.json` (gitignored runtime) | Overwrite, single writer per recipient | `scripts/cross_harness_bridge_trigger.py` | `_check_bridge_dispatch_liveness`, `_check_cross_harness_trigger` |
| 8 | Harness identity registry | `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`, `GOV-ACTING-PRIME-BUILDER-001` | `harness-state/harness-identities.json` (git-tracked) | Owner-only via `scripts/harness_identity.py set --owner-requested` | Explicit identity-change op | `_check_role_set_topology_consistency` (cross-checks identity vs role) |
| 9 | Harness role registry | `GOV-HARNESS-ROLE-PORTABILITY-001` + `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (Path 2) | `harness-state/harness-registry.json` (canonical, MemBase projection) | Append in MemBase; projection regenerated | `gt mode set-role` transaction component | `_check_role_set_topology_consistency`, `_check_single_harness_dispatcher_when_required` |
| 10 | Legacy role mirror (ORPHAN) | Slice 1 retirement | `harness-state/role-assignments.json` | Frozen at retirement | None — orphan compatibility surface | NONE (still on disk; being retired by Phase-1 SoT consolidation) |
| 11 | Bridge substrate state | `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`, `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | `harness-state/bridge-substrate.json` (git-tracked) | Transaction-mutated via `gt mode set-bridge-substrate` | `single_harness_bridge_automation.py` | indirect via dispatcher health checks |
| 12 | Capability parity registry | rule-cited soft authority | `config/agent-control/harness-capability-registry.toml` | Manual edit + SHA-256 pinned per adapter | Manual TOML edit; SHA must match adapter source | (none discovered; SHA verification appears manual) |
| 13 | Startup-surface inventory | `GOV-SESSION-SELF-INITIALIZATION-001` | `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md` | Markdown classified table | Bridge proposal + manual edit | `test_session_startup_control_map.py` |
| 14 | Role-capability manifest | `GOV-SESSION-SELF-INITIALIZATION-001` | `config/agent-control/ROLE-CAPABILITY-MANIFEST.md` | Markdown | Manual edit | (none discovered) |
| 15 | System-interface map (bridge automation axes) | `bridge-essential.md` § Two-Axis Bridge Automation Model | `config/agent-control/system-interface-map.toml` | TOML | Manual edit (owner-approved bridge proposal for new entries) | (none discovered) |
| 16 | AUQ policy gates | `SPEC-AUQ-POLICY-ENGINE-001` | `config/agent-control/auq-policy-gates.toml` | TOML | Manual edit | indirect via `owner-decision-tracker.py` |
| 17 | Project resource aliases | `.claude/rules/canonical-terminology.md` §project-resource alias | `config/agent-control/project-resource-aliases.toml` | TOML | Manual edit | (none discovered) |
| 18 | Governance policy registries (8 files) | various GOV/DCL specs | `config/governance/*.toml` (spec-applicability, adr-dcl-clauses, narrative-artifact-approval, lo-file-safety, assertion-runs-retention, protected-artifact-inventory-drift, spec-coherence-rules, hygiene-sweep-patterns) | TOML | Manual edit | partial — some files have dedicated drift checks |
| 19 | Managed-artifacts registry | rule-cited from `templates/` + `_check_managed_artifact_drift` | `groundtruth-kb/templates/managed-artifacts.toml` (67 records) + `templates/scaffold-ownership.toml` | TOML with lifecycle axes | Bridge proposal + Python loader validation (`InvalidArtifactRecord`) | `_check_managed_artifact_drift`, `_check_settings_hook_registration_drift`, `test_managed_registry.py` |
| 20 | Session state markers (runtime) | `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`, `.claude/rules/operating-role.md` | `.claude/session/work-subject.json`, `.claude/session/active-session-role.json` (gitignored) | Overwrite, single writer | `scripts/workstream_focus.py`, `scripts/session_role_resolution.py` | `_check_session_role_marker_validity`, `_check_session_role_marker_session_id_alignment` |
| 21 | Operational notepad (NON-canonical) | ADR-0001 (explicitly NOT SoT) | `memory/MEMORY.md`, `memory/*.md` | Git-tracked | Free-form edit | indirect (MEMORY.md size cap warned in startup) |
| 22 | Pending owner decisions | hook-managed | `memory/pending-owner-decisions.md` | Append + resolve | `.claude/hooks/owner-decision-tracker.py` | `_check_untriaged_prose_decisions`, `_check_auq_coverage` |

**Non-canonical-but-still-on-disk surfaces (drift candidates):**

| Surface | Status | What replaces it |
|---|---|---|
| `independent-progress-assessments/CODEX-*.md` (operating contracts, runbooks) | Legacy — mirrored to `.claude/rules/codex-*` | `.claude/rules/codex-*` is canonical; IPA versions are provenance only |
| `independent-progress-assessments/PHASE-*-PLAN.md`, board memos, exec briefs | Historical record | None — historical |
| `independent-progress-assessments/CONTROL-SURFACE-PHASE-*-PLAN.md`, `BRIDGE-RESPONSIVENESS-LEDGER*` | Historical | Active control map is `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md` |
| `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` + `*.json` | LO advisory dropbox (live) | This *is* the canonical LO advisory surface; not drift |
| `independent-progress-assessments/_source_proposal_copy.docx`, `*.pdf`, `*.dotx` | Proposal-template artifacts | Document-author-provenance contract (active bridge thread) |
| `config/agent-control/CONTROL-MAP.md` | Marked `deprecated` by SESSION-STARTUP-CONTROL-MAP.md | `SESSION-STARTUP-CONTROL-MAP.md` is canonical |
| `config/agent-control/REVIEW-MODE-SETUP.md` | Marked `deprecated` | Same as above |
| `harness-state/role-assignments.json` | Orphan compatibility mirror | `harness-state/harness-registry.json` (canonical MemBase projection); being retired by `PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION` Phase-1 mirror-retirement child |
| `.claude/rules/bridge-poller-canonical.md` | Self-described DEPRECATED (Slice 4 smart-poller retirement) | `.claude/rules/bridge-essential.md` § Operational Mode |
| `memory/agent-red-hibernation-*`, `memory/slice-4-smart-poller-retirement-continuation.md`, several `phase_X_*_draft.md` | Stale notepad pages | (cleanup candidates) |

---

## 3. Existing Partial Registries

Catalogued for §6 gap analysis. Each is "registry-shaped" — a structured inventory of records with per-record metadata — but each is scoped to one domain.

| # | Registry | Scope | Records | Mechanism |
|---|---|---|---|---|
| R1 | `groundtruth.db` MemBase tables | spec / WI / test / procedure / DA / project / PAUTH / assertion-run / etc. | thousands | SQLite append-only |
| R2 | `groundtruth-kb/templates/managed-artifacts.toml` | scaffold/upgrade/doctor lifecycle for hooks/rules/skills/files/settings/gitignore | 67 records | TOML + Python loader + 3 lifecycle axes + `InvalidArtifactRecord` validation + tested via `test_managed_registry.py` |
| R3 | `groundtruth-kb/templates/scaffold-ownership.toml` | sibling ownership-glob records (priority-keyed) | ~10+ | TOML + `OwnershipGlobArtifact` dataclass; merged with R2 by `_load_all_artifacts()` |
| R4 | `config/agent-control/harness-capability-registry.toml` | capability parity across Claude/Codex/Antigravity harnesses | dozens | TOML with SHA-256 pinned adapters |
| R5 | `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md` | startup-control surfaces | ~20 | Markdown classified table (4 lifecycle states) |
| R6 | `config/agent-control/ROLE-CAPABILITY-MANIFEST.md` | role-grouped capability inventory | ~40 | Markdown |
| R7 | `config/agent-control/system-interface-map.toml` | bridge automation surfaces (Axis-1/Axis-2 classification) | small | TOML |
| R8 | `config/governance/*.toml` (8 files) | per-domain governance policy registries | scattered | TOML, per-domain |
| R9 | `harness-state/*.json` | runtime role/identity/substrate state | 4 files | JSON + MemBase projection for the canonical role registry |
| R10 | `bridge/INDEX.md` + `bridge/*.md` | bridge workflow state | ~200 entries | append-only markdown |

**Key observation:** R2+R3 (managed-artifacts) is the closest existing precedent for what the owner is asking for — it has lifecycle axes, an enforced loader, a doctor check, and a test that asserts the exact record count. But its **scope is scaffolded artifacts**, not platform-wide SoT.

---

## 4. Doctor Health-Check Surface (Today)

`groundtruth-kb/src/groundtruth_kb/project/doctor.py` defines **42+ `_check_*` functions**. Relevant clusters for SoT integrity:

- **Registry-drift checks:** `_check_managed_artifact_drift`, `_check_settings_hook_registration_drift`, `_check_canonical_terms_registry`
- **Reference-validity checks:** `_check_orphan_citations`, `_check_active_legacy_root_references`, `_check_uncited_owner_input_bridges`
- **Role/state checks:** `_check_role_set_topology_consistency`, `_check_single_harness_dispatcher_when_required`, `_check_session_role_marker_validity`
- **Bridge checks:** `_check_file_bridge_setup`, `_check_bridge_dispatch_liveness`, `_check_cross_harness_trigger`
- **Skill-presence checks:** `_check_skill_present`, `_check_bridge_propose_skill_present`, `_check_spec_intake_skill_present`, `_check_codex_skill_load_health`
- **Boundary checks:** `_check_external_harness_exec_boundary`, `_check_scanner_safe_writer_drift`
- **Health-of-DA checks:** `_check_da_harvest_coverage`, `_check_standing_backlog_health`

**Conclusion:** the doctor surface is extensive and already enforces many SoT contracts. The gap is **a single doctor check that asserts the registry-of-registries is exhaustive** — i.e., that no SoT class exists in the repo without a corresponding registered entry.

---

## 5. Drift Sources the Owner Is Fighting

Concrete instances the owner has flagged or that are visible:

1. **IPA being treated as SoT.** Owner directly identified this: `independent-progress-assessments/` still contains operating contracts (CODEX-*) that are *mirrored* into `.claude/rules/codex-*`. The mirror direction is unclear without inspection. CONTROL-MAP.md still cites the IPA versions. → drift.
2. **Legacy mirror still on disk.** `harness-state/role-assignments.json` shows divergent state from `harness-registry.json` (different role-set for harness A) — `PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION` Phase-1 is actively retiring it. → drift in flight.
3. **Two control maps.** `config/agent-control/CONTROL-MAP.md` (deprecated) and `SESSION-STARTUP-CONTROL-MAP.md` (active) both exist. The deprecated one still cites IPA paths. → drift.
4. **Two bridge-poller rules.** `.claude/rules/bridge-poller-canonical.md` is a self-described DEPRECATED stub (smart-poller retirement Slice 4); `.claude/rules/bridge-essential.md` is the canonical authority. → drift in flight.
5. **Capability parity registry has no health check.** `harness-capability-registry.toml` SHA-pins adapters but no doctor check enforces SHA freshness on `.codex/` / `.agent/` adapter files. → drift risk.
6. **`memory/` accumulates stale research notes.** ~23 markdown files; multiple appear to be completed drafts that should be archived or deleted. → drift accumulation.
7. **Auto-memory limit exceeded.** MEMORY.md warning at session start: "MEMORY.md is 60KB (limit: 24.4KB) — index entries are too long. Only part of it was loaded." → mechanical drift indicator.

---

## 6. Gap Analysis — What's Missing

For a platform-wide registry to do what the owner is asking, **6 things are missing**:

1. **Cross-cutting inventory.** No single source lists all 22 SoT classes (§2) plus all 10 partial registries (§3). The closest is SESSION-STARTUP-CONTROL-MAP.md, but it's scoped to *startup-surfaces*.

2. **Governance authority.** No GOV-* spec currently says "every SoT class MUST be registered; un-registered SoT is a defect." `GOV-08` and `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` are closest but operate at conceptual rather than registry level.

3. **Per-record metadata schema.** Existing registries vary in fields (managed-artifacts has lifecycle/upgrade/ownership; capability has SHA; control-map has classification). A registry-of-registries would need a unified schema for: `{domain, lifecycle, storage_path, authority_spec_id, mutation_api, versioning_policy, backup_policy, health_check_function, owner_role, depends_on}`.

4. **Doctor check.** No `_check_sot_registry_completeness` exists. Pattern would mirror `_check_managed_artifact_drift` but at the meta level.

5. **Retirement pathway.** When a surface is deprecated (e.g., CONTROL-MAP.md, role-assignments.json, bridge-poller-canonical.md), no consistent retirement mechanism exists. Each retirement is currently a bespoke bridge thread.

6. **Adopter inheritance.** Adopter projects inherit a subset of GT-KB surfaces via scaffold. A platform-wide SoT registry would need to define which records adopter projects also need.

---

## 7. Three Structural Options

### Option A — TOML-Federated Registry

**Shape:**
- One new TOML file: `config/registry/sot-artifacts.toml`.
- Each row points to a domain registry (R1–R10 from §3) or, for atomic classes, the storage path directly.
- Three lifecycle axes (`active` / `deprecated` / `archive` / `generated`), reusing the `SESSION-STARTUP-CONTROL-MAP.md` classification.
- New Python loader `groundtruth_kb.project.sot_registry` analogous to `managed_registry`.
- New doctor check `_check_sot_registry_completeness` asserts each registered domain registry exists on disk and validates.
- New governance spec `GOV-PLATFORM-SOT-REGISTRY-001` declares the contract.

**Pros:**
- Builds directly on existing TOML/loader/doctor pattern (`managed-artifacts.toml` is the precedent).
- Lowest cognitive load: one file, git-diffable, human-readable.
- No new MemBase schema work.

**Cons:**
- One more file to maintain by hand.
- Risk it becomes another partial registry if not paired with the right doctor enforcement.
- Edits to it are not in the audit-trail tier of MemBase (just git history).

### Option B — MemBase-Native Registry

**Shape:**
- New MemBase table `sot_artifacts` (or extend `documents` with `type=sot_registry_entry`).
- All records inserted via `gt registry record` CLI with formal-artifact-approval packets.
- TOML/config files become projections (or stay as edit-surfaces, with MemBase as the authoritative inventory).
- Queryable: `gt registry list --domain bridge`, `gt registry validate`, `gt registry diff`.
- Doctor: `_check_sot_registry_completeness` queries MemBase + walks filesystem to find unregistered SoT.

**Pros:**
- Queryable, append-only versioned, ties into existing `assertion_runs` + DA + Deliberation Archive surfaces.
- Mutation is governed (matches `GOV-ARTIFACT-APPROVAL-001` discipline).
- Cross-references between SoT registry entries and the specs/WIs/projects that authorize them are first-class.

**Cons:**
- Schema work + new CLI surface.
- Bootstrapping concern: the registry is itself an SoT class, so it must self-register.
- Less git-diffable; reviewers can't see the registry change in a PR diff (would have to run `gt registry diff`).

### Option C — Hybrid (TOML + MemBase Projection) — RECOMMENDED

**Shape:**
- TOML at `config/registry/sot-artifacts.toml` is the **human-edit surface** (low-friction, git-diffable, owner-readable).
- MemBase `sot_artifacts` table is the **projection** (mirror of `harness-state/harness-registry.json` ← MemBase pattern).
- Edits flow: TOML edit → bridge proposal → formal-artifact-approval packet → loader validates → MemBase projection regenerated → commit.
- Doctor check validates **two things**: (a) TOML ↔ MemBase parity (no drift between edit-surface and projection); (b) registry ↔ on-disk reality (no unregistered SoT class).
- New governance spec `GOV-PLATFORM-SOT-REGISTRY-001` + DCL `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`.

**Pros:**
- Matches the established **harness-registry pattern** (Slice 1 retirement of the role-assignments mirror; `harness-registry.json` is itself a MemBase projection).
- Preserves edit-ergonomics (TOML is reviewable in PRs) AND queryability (`gt registry list`).
- Drift between edit-surface and projection is mechanically detectable.
- Authority chain is clean: extend `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` → `GOV-PLATFORM-SOT-REGISTRY-001` → per-domain DCLs.

**Cons:**
- Two surfaces means more moving parts during initial implementation.
- Requires the projection regen step in scaffold + upgrade flows.

`★ Insight ─────────────────────────────────────`
Option C is *not* novel — it reuses the architectural pattern Slice 1 of `gtkb-retire-role-assignments-mirror` established for harness-state. That pattern works because the TOML/JSON file is the human-edit surface, MemBase is the canonical projection, and a deterministic regen op + parity check holds them in sync. Applying the same pattern at the meta level (registry of registries) is a small generalization of existing precedent, not a new architecture.
`─────────────────────────────────────────────────`

**Recommendation:** **Option C.** Builds on existing pattern, gives both ergonomics and governance, and the drift-detection mechanism is well-understood from harness-state work.

---

## 8. Proposed Project Sequencing

**Critical observation:** A project already exists for this work, narrowly scoped.

- `PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION` (Phase 1, bridge `gtkb-harness-state-sot-consolidation-phase-1-001..003`) is consolidating SoT for ONE domain (harness-state) with 13 WIs across 4 child bridges. Owner directive that started it: "please remove all non-SoT references to the harness state, registration, role, etc."
- Today's directive widens that to "every known document in the project."

**Two ways to handle this:**

- **A. Umbrella the existing project under a broader one.** New `PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION` becomes the parent; `PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION` becomes Slice 1 in flight. No re-do.
- **B. Run the broader project as a sibling.** New `PROJECT-GTKB-SOT-REGISTRY` covers ONLY the meta-registry + governance + doctor check + retirement pathway. Each per-domain consolidation runs as its own sibling project (harness-state already one; startup-control already one via `GTKB-STARTUP-REFRACTOR-001`).

**Recommendation:** **Option A (umbrella).** Avoids duplicating the framing work; treats the harness-state thread as the first concrete consolidation slice; the broader registry codifies the pattern that subsequent domain projects follow.

### Proposed slice sequence (assuming Option C + Umbrella)

| Slice | Subject | Work items (estimate) | Authority |
|---|---|---|---|
| **0** | Inventory + design ratification | this report → bridge proposal | `GOV-09` + this advisory |
| **1** | Governance scaffolding: `GOV-PLATFORM-SOT-REGISTRY-001`, `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`, registry TOML scaffold, MemBase table, `gt registry` CLI, doctor check | 5–8 WIs | New GOV/DCL + formal-artifact-approval packets |
| **2** | Inherits in-flight `PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION` Phase 1 (no re-do) — harness-state SoT | 13 WIs (already in flight) | existing PAUTH |
| **3** | Startup-control SoT — finishes `GTKB-STARTUP-REFRACTOR-001` outstanding slices (deprecate CONTROL-MAP.md, REVIEW-MODE-SETUP.md) | 3–5 WIs | extends existing project |
| **4** | Bridge-protocol SoT — registers `bridge/INDEX.md`, `.gtkb-state/work-intent/`, dispatch-state with health-check pointers; deprecates `bridge-poller-canonical.md` stub | 4–6 WIs | new |
| **5** | IPA legacy retirement — archive Codex operating contracts that are mirrored to `.claude/rules/codex-*`; document `CODEX-INSIGHT-DROPBOX/` as the canonical LO advisory channel (not drift); decide PHASE-*-PLAN / board-memo retirement | 5–8 WIs | new + owner AUQ per-file |
| **6** | `memory/` cleanup — retire stale drafts; resolve MEMORY.md size cap (the 60KB warning); fold completed-work entries into project-* topic files | 3–5 WIs | new |
| **7** | Adopter scaffolding — extend `managed-artifacts.toml` to scaffold the SoT registry into adopter projects; doctor check ports to adopter | 3–5 WIs | new |

---

## 9. Open Owner Decisions (for AUQ when project envelope is filed)

1. **Project scope.** Umbrella the existing `PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION` under a broader project, or run as siblings?
2. **Structural option.** Option A (TOML-only) / B (MemBase-only) / C (Hybrid, recommended)?
3. **Registry storage location.** `config/registry/sot-artifacts.toml` or `config/governance/sot-artifacts.toml` (extend the existing governance-registry directory)?
4. **IPA disposition.** For each legacy class in IPA — archive into `archive/`? delete? leave with deprecation banner pointing to canonical mirror?
5. **MEMORY.md cap remediation.** This research itself is going to make the cap worse — fold completed-work memory entries into a separate `memory/completed/` tier? Set a retention/auto-archive policy?
6. **Doctor severity.** Should `_check_sot_registry_completeness` be `ERROR` (release-blocking) or `WARN`? Recommendation: `WARN` during Slice 1, promote to `ERROR` after the inventory has stabilized.
7. **Adopter rollout cadence.** Ship registry to adopter projects in v0.7.0-rc1 (current release), or hold for v0.7.0 stable?

---

## 10. Concrete Consolidation Candidates (start small)

If/when this is approved, these are the cleanest first targets (low blast radius, clear drift evidence):

1. **`config/agent-control/CONTROL-MAP.md`** → mark deprecated banner, point to `SESSION-STARTUP-CONTROL-MAP.md`, or delete. (Already classified `deprecated` in newer map; just needs the retirement op.)
2. **`config/agent-control/REVIEW-MODE-SETUP.md`** → same as above.
3. **`.claude/rules/bridge-poller-canonical.md`** → already self-described DEPRECATED; needs retirement.
4. **`harness-state/role-assignments.json`** → already in-flight under harness-state Phase 1 mirror-retirement child.
5. **IPA Codex operating contracts** (`CODEX-WAY-OF-WORKING.md`, `CODEX-LOYAL-OPPOSITION-RUNBOOK.md`, `CODEX-KNOWLEDGE-BASE-INDEX.md`, `CODEX-DECISION-LEDGER.md`, `CODEX-DEAD-ENDS-AND-FALSE-POSITIVES.md`, `CODEX-REVIEW-CHECKLISTS.md`) — verify mirrors in `.claude/rules/codex-*` are byte-equivalent or owner-approved divergent; archive IPA versions.
6. **`memory/agent-red-hibernation-*.md`** (2026-04-27 dated) — completed; archive or delete.
7. **`memory/slice-4-smart-poller-retirement-continuation.md`** — smart-poller is retired; this is stale.
8. **`memory/phase_2_worktree_audit_2026_05_11.md`, `memory/phase-1/2/3-*-draft.md`** — completed drafts; archive.

---

## 11. Operational Notes

- **Bash gating:** During this scan, the impl-start-gate blocked all Bash because bridge thread `gtkb-impl-start-target-paths-preflight-008` is awaiting LO review. This affected my ability to query MemBase directly. Findings about MemBase tables were inferred from CLAUDE.md's artifact-type list + tracked schema files. **Action when ready:** rerun the registry-scoping bridge proposal *after* the preflight thread resolves so we have full Bash + scripts access for accurate baselines.
- **Active bridge threads to coordinate with:**
  - `gtkb-impl-start-target-paths-preflight-008` (awaiting LO)
  - `gtkb-harness-state-sot-consolidation-phase-1-003` (REVISED, awaiting LO verdict)
  - `gtkb-document-author-provenance-contract-004` (GO for Prime)
  - `GTKB-STARTUP-REFRACTOR-001` outstanding slices

---

## 12. Out of Scope

- DECISION-1019 (substrate=none investigation) — independent.
- The active proposal-preflight thread itself.
- Application-side (Agent Red) SoT — that's `applications/Agent_Red/` and follows the platform/application isolation contract (`ADR-APPLICATION-ISOLATION-CONTRACT-001`). Adopter inheritance is Slice 7.
- v0.7.0-rc1 release work — this should land before or after the rc1 cut, owner decision.

---

## 13. Recommended Next Action

When ready to proceed, file a bridge proposal:

- Slug: `gtkb-platform-sot-consolidation-umbrella-001` (or pick a shorter slug)
- `bridge_kind: governance_review` (no source mutations in umbrella)
- `target_paths: []`
- Cite this research file as a Prior Deliberation
- Mint a PAUTH covering the umbrella + Slice-1 governance work, scoped to `config/registry/`, `groundtruth-kb/src/groundtruth_kb/project/`, `config/governance/`, `bridge/`, MemBase governance/spec inserts
- 8-AUQ-style owner-grilling pass on the 7 open decisions in §9 (per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` discipline even though this isn't an LO advisory)
- Slice-1 child bridges follow umbrella GO

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Notepad-tier artifact per ADR-0001. Not canonical.*
