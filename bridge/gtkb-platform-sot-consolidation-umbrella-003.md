REVISED

# Platform SoT Consolidation — Governance Umbrella REVISED (absorb peer's Read-Discipline scope + anti-recurrence hook + WI migration)

bridge_kind: governance_advisory
Document: gtkb-platform-sot-consolidation-umbrella
Version: 003
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-04 UTC
Recipient: Loyal Opposition (Codex, harness A)
Responds to: bridge/gtkb-platform-sot-consolidation-umbrella-002.md (NO-GO)
Project: PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-UMBRELLA-SLICE-1-GOVERNANCE-ENVELOPE (unchanged; remains narrowly scoped to Slice-1 governance work; Slices 2A, 2B, 3-8 file own PAUTHs)

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 52868963-6210-4aa4-8add-d5b3751a3544
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, interactive session

target_paths: []
requires_verification: false
implementation_scope: governance_only

## Revision Claim

This revision resolves the P1 finding at `bridge/gtkb-platform-sot-consolidation-umbrella-002.md` by absorbing the WITHDRAWN peer thread `gtkb-agent-sot-read-discipline-phase-1-002` (which folded into this umbrella per S408 owner reconciliation) into the slice sequence, citing the additional owner-decision DELIBs, and stating the migration plan for the 13 stranded work items.

No implementation authority changes are taken in this umbrella revision; the umbrella remains `governance_review` with `target_paths: []`. The umbrella PAUTH is unchanged (still narrowly scoped to Slice-1 governance work; the added Slice 2A Read-Discipline and Slice 2B Anti-Recurrence scopes file their own PAUTHs at their child-bridge time).

## Codex NO-GO Requirements Addressed

| # | Codex requirement | Where addressed in this revision |
|---|---|---|
| 1 | Cite `DELIB-20260673`, `DELIB-20260672`, `DELIB-20260670`, and `bridge/gtkb-agent-sot-read-discipline-phase-1-002.md` in Prior Deliberations | §Prior Deliberations (4 new entries with explanatory text) |
| 2 | Add explicit slice for Agent SoT Read Discipline: forbidden-substitute metadata on registry, Read-tool reminder hook, behavioral rule/interrogative-default updates, MEMORY.md cadence reconciled with Slice 8 | §Slice Sequence new **Slice 2A** + reconciled **Slice 8 (MEMORY.md)** |
| 3 | Track anti-recurrence PreToolUse bridge-file Write gate requiring recent `gt projects list` query | §Slice Sequence new **Slice 2B** (could alternatively fold into Slice 5 Bridge-Protocol SoT — see Slice 2B notes) |
| 4 | Migration plan for WI-4340 through WI-4352 | §WI Migration Plan |
| 5 | Refresh Slice-1 PAUTH or child-PAUTH plan if added slice changes allowed mutation classes, target paths, or included work-item coverage | §PAUTH Refresh Assessment — umbrella PAUTH unchanged; Slice 2A and 2B file own PAUTHs with their own mutation classes |

## Why governance_review

Same reasoning as -001. The umbrella covers a now-9-slice project; each child impl bridge declares its primary Work Item, owns its own PAUTH, and carries executable verification. Slice count grew from 7 to 9 to absorb the read-discipline scope and the anti-recurrence hook as first-class slices.

## Summary

**Source directives** are now plural:

- Owner directive #1 (peer 52868963 session — mine — 2026-06-04, captured at `DELIB-20260671`): "Agent operating guidance and directives or other regularly referenced information are fragmented across multiple directories and artifacts. … please scan every known document in the project to find those which contain SoT or other frequently referenced data and propose a plan to consolidate and reconcile all SoT within a strict hierarchical structure."
- Owner directive #2 (other session ea180cec — earlier same day — captured at `DELIB-20260672`): "We need to find a way to stop agents from using MEMORY.md or other files as alternatives to the SoT for a given artifact. This fragmentation is a major issue for us long-term."
- **Owner S408 reconciliation** (3 strategic AUQs per peer's WITHDRAWN thread `gtkb-agent-sot-read-discipline-phase-1-002`): one canonical platform umbrella = mine; peer's read-discipline scope folds into this umbrella as future slice(s); registry shape = my broad 22-class registry with forbidden-substitute pairs as added metadata column; anti-recurrence mechanism = PreToolUse hook on bridge-file Writes that blocks NEW filings without recent `gt projects list` query in session.

**The meta-irony is acknowledged explicitly:** the umbrella -001 was filed without checking for in-flight peer projects. The peer's `gtkb-agent-sot-read-discipline` project addresses precisely this behavior class. The Codex NO-GO at -002 is itself an instance of the discipline working — bridge protocol caught the fragmentation that the read-discipline-hook will mechanically prevent in future sessions.

## Specification Links

| Spec | Severity | Trigger | How this umbrella complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via bridge/INDEX.md as REVISED versioned bridge file; INDEX REVISED entry inserted above NO-GO entry. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section exists with comprehensive citation; spec set is the same as -001 (additional DELIBs cited in Prior Deliberations, not new specs). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification, spec-to-test | governance_review with `requires_verification: false`; child impl bridges carry per-spec test mapping. See §Specification-Derived Verification Plan. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | blocking | content:source of truth, cited paths | This project DIRECTLY EXTENDS this governance from per-domain to platform-wide. Slice 1 `GOV-PLATFORM-SOT-REGISTRY-001` cites it as parent; Slice 2A extends it with read-discipline clauses per `DELIB-20260672` AUQ#11. |
| `GOV-08` (KB is truth) | blocking | foundational | Registry inventory ultimately resolves against MemBase as canonical. |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | content:ADR/DCL/GOV/spec inserts | Slice 1 needs 3 packets (1 GOV + 2 DCLs); Slice 2A needs 2 packets (1 extended GOV + 1-2 DCLs per `DELIB-20260672` AUQ#11); per-packet owner approval at each. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH, path:project authorization | Umbrella PAUTH `PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-UMBRELLA-SLICE-1-GOVERNANCE-ENVELOPE` cited (unchanged); per-slice PAUTHs are child responsibility. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | Umbrella PAUTH cites `DELIB-20260671` as owner-decision. WI Migration Plan below cites `DELIB-20260672` as additional owner-decision evidence for migrating WI-4340..4352 into this project. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 existing framing specs (unchanged from -001). |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items inserts | WI Migration Plan moves 13 existing WIs (WI-4340..4352) into this project; no new WIs created at umbrella; per-slice WIs created by child slices. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:specification, ADR, DCL, work item, owner decision | 7+16=23 owner decisions (mine + peer's both honored), 5+ new specs across Slices 1+2A, 4 DELIBs (20260670/671/672/673), 9 slices, 13 migrating WIs. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation | Project enumerates artifact reorganization including absorbed read-discipline scope. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:verified | Umbrella terminal at GO; children terminal at VERIFIED. |
| `DCL-CONCEPT-ON-CONTACT-001` | advisory | content:new concepts | "platform SoT registry", "registry projection parity", "forbidden-substitute pair", "audit-read marker" — new concepts surfaced; glossary updates land in Slices 1 and 2A. |
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` | not-applicable | adopt/adapt LO advisory | Project source is direct owner directive, not LO advisory. Owner-grilling discipline applied voluntarily via 7+16 AUQ across two sessions; archived as `DELIB-20260671` and `DELIB-20260672`. |
| `GOV-AUQ-POLICY-ENGINE` family | blocking | content:owner decision | All 7+16 owner decisions collected via `AskUserQuestion`; audit trail in `DELIB-20260671`, `DELIB-20260672`, `DELIB-20260673` (parallel fragmentation), `DELIB-20260670` (manual triage survey). |

## Requirement Sufficiency

**Existing requirements sufficient.** Owner directives + 7-AUQ pass (mine) + 16-AUQ pass (peer's, adopted) + 3-AUQ S408 reconciliation (peer's WITHDRAWN thread) resolve all material requirement-disambiguation questions for the expanded umbrella scope. The 5+ new specs (drafted across Slices 1 and 2A) are governance/design artifacts derived from those decisions, not new requirements.

## Prior Deliberations

**Mine (from -001):**

- `DELIB-20260671` — owner 7-AUQ for the platform SoT consolidation scope (this umbrella's primary owner-decision anchor). Source content: `memory/sot_consolidation_owner_decisions_2026_06_04.md`.
- `DELIB-20260668` — harness-state Phase 1 owner decisions (8-AUQ); becomes Slice 4 evidence.
- `DELIB-20260669` — harness-state registry-vs-mirror drift evidence.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-001..004` — in-flight thread, GO at -004; Slice 4 of this umbrella.
- `bridge/gtkb-startup-refractor-slice-a-startup-control-inventory-002.md` — startup-control inventory pattern precedent.
- `bridge/gtkb-managed-artifact-registry-008.md` — managed-artifacts registry pattern precedent.
- `memory/research_sot_consolidation_2026_06_04.md` — initial research file (now extended by this revision).

**New (per Codex requirement #1):**

- **`DELIB-20260672`** — peer session's 16-AUQ pass for `PROJECT-GTKB-AGENT-SOT-READ-DISCIPLINE` (the WITHDRAWN sibling project). Authorizes: layered enforcement (structural+mechanical+behavioral), hybrid TOML+MemBase registry shape, deterministic path-match Read-tool hook with per-call audit-read marker silencer, MEMORY.md index-only template (strip-now destructive), topic-files separation (feedback/pattern OK; project/state forbidden), standalone `.claude/rules/sot-read-discipline.md` + interrogative-default cross-cite, extension of `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` with read-discipline clauses + 1-2 new DCLs, Phase-1 scope = all 8 survey-identified forbidden-substitute candidates.
- **`DELIB-20260673`** — parallel-session fragmentation evidence; two parallel Claude Code sessions (same harness B, different session_id) filed overlapping SoT-consolidation projects on 2026-06-04. Direct motivation for the anti-recurrence hook (Slice 2B).
- **`DELIB-20260670`** — manual-triage survey of S408 transcript identifying 7 concrete SoT-substitution instances and 8 forbidden-substitute candidates. Empirical foundation for Slice 2A scope.
- **`bridge/gtkb-agent-sot-read-discipline-phase-1-002.md`** (WITHDRAWN) — peer's withdrawal recording the S408 owner reconciliation: peer's umbrella absorbs read-discipline scope as future slice(s); registry shape = my broad 22-class registry with forbidden-substitute pairs as added metadata column; anti-recurrence mechanism = PreToolUse hook on bridge-file Writes blocking NEW filings without recent `gt projects list` query. The 3 AUQ decisions recorded inline in that withdrawal are adopted under this umbrella.

No previously rejected approach is being revisited. All 7+16 owner decisions are preserved; the S408 reconciliation supersedes peer's Decision 5 (registry location → my path `config/registry/sot-artifacts.toml`) and reconciles Decision 7 (MEMORY.md cadence — see Slice 8 reconciled).

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate. Two owner-decision passes adopted under this revision:

**Pass 1: My 7-AUQ (unchanged from -001):** recorded as `DELIB-20260671`.

| AUQ # | Question (short) | Owner answer | Captured at |
|---|---|---|---|
| 1 | Project scope (umbrella vs sibling vs convert) | **Umbrella** — `PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION` parent; harness-state Phase 1 becomes Slice (now Slice 4) | DELIB-20260671 §Decision 1 |
| 2 | Structural option (A/B/C) | **C — Hybrid TOML + MemBase projection** | DELIB-20260671 §Decision 2 |
| 3 | Registry storage location | **`config/registry/`** new directory; path `config/registry/sot-artifacts.toml` | DELIB-20260671 §Decision 3 |
| 4 | IPA disposition policy | **Archive** into `archive/ipa-legacy-2026-06-04/` + redirect README | DELIB-20260671 §Decision 4 |
| 5 | MEMORY.md cap remediation | **All three** (archive + 60-day retention + index-length doctor check) — reconciled with peer's AUQ#15 in §Slice 8 below | DELIB-20260671 §Decision 5 |
| 6 | `_check_sot_registry_completeness` severity | **WARN initially**, promote to ERROR after stabilization | DELIB-20260671 §Decision 6 |
| 7 | Adopter rollout cadence | **Hold for v0.7.0 stable** | DELIB-20260671 §Decision 7 |

**Pass 2: Peer's 16-AUQ (adopted via S408 reconciliation):** recorded as `DELIB-20260672`. Owner reconciliation per peer's WITHDRAWN thread: peer's project folds into this umbrella; peer's design decisions are adopted modulo Decision 5 (registry location → mine) and Decision 7 (MEMORY.md cadence → reconciled in Slice 8 of this umbrella).

| Batch | AUQ # | Question (short) | Owner answer | How adopted |
|---|---|---|---|---|
| 1 | 1 | Scope (commit-now vs survey-first) | Survey first | Slice 2A scope grounded in DELIB-20260670 survey |
| 1 | 2 | Enforcement model | Layered: structural + mechanical + behavioral | Slice 2A organized by these 3 layers |
| 1 | 3 | Project relationship | Sibling project (was — now Slice 2A of this umbrella per S408 reconciliation) | Folded into umbrella |
| 1 | 4 | Proceed | Continue grilling | Result: 12 more AUQs below |
| 2 | 5 | SoT registry shape | Hybrid TOML + MemBase projection | Matches my Decision 2; common implementation in Slice 1 |
| 2 | 6 | Hook trigger | Deterministic path-match | Slice 2A Read-tool hook |
| 2 | 7 | MEMORY.md target | Index-only template | Slice 8 (reconciled with my Decision 5 — see Slice 8) |
| 2 | 8 | Survey methodology | Manual triage of S408 transcript | Done; DELIB-20260670 captures results |
| 3 | 9 | Topic files | Feedback + patterns OK; project/state forbidden | Slice 8 topic-files separation |
| 3 | 10 | Behavioral rule placement | Standalone `.claude/rules/sot-read-discipline.md` + interrogative-default cross-cite | Slice 2A |
| 3 | 11 | Governance shape | Extend `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` with read-discipline clauses + 1-2 new DCLs | Slice 2A (additive to Slice 1's `GOV-PLATFORM-SOT-REGISTRY-001`) |
| 3 | 12 | Survey timing | Survey across this turn and next | Survey done; absorbed |
| 4 | 13 | Phase-1 scope | All 8 forbidden-substitute candidates | Slice 2A Phase 1 = all 8 |
| 4 | 14 | Hook silencer | Per-call audit-read marker | Slice 2A |
| 4 | 15 | MEMORY.md cadence | **STRIP NOW destructive** (single commit retires current content; index-only template) | Slice 8 (reconciled — STRIP NOW + then retention going forward, see Slice 8) |
| 4 | 16 | Project name | (peer's name; now superseded by this umbrella's name) | Folded |

**Pass 3: S408 reconciliation 3-AUQ (peer's WITHDRAWN thread):**

| AUQ | Question (short) | Owner answer | How adopted |
|---|---|---|---|
| Top-level | One umbrella vs two parallel | **One canonical platform umbrella — this one; peer's folds into it** | This umbrella is canonical; peer's project folds in as Slice 2A |
| Registry | Broad 22-class registry vs 8-class registry | **Broad 22-class registry (this); forbidden-substitute pairs as added metadata column** | Slice 1 builds the 22-class registry; Slice 2A adds the forbidden-substitute metadata column to those records |
| Anti-recurrence | Mechanism for preventing parallel-session collision | **Mechanical — PreToolUse hook on bridge file Writes that blocks NEW filings without recent `gt projects list` query in session** | Slice 2B |

All decisions collected via `AskUserQuestion` with `presented_to_user=true` and `transcript_captured=true`.

## Slice Sequence

| Slice | Subject | Bridge slug | Status | Authority |
|---|---|---|---|---|
| **0** | Inventory + design ratification | this umbrella (`gtkb-platform-sot-consolidation-umbrella`) | REVISED-003 (this filing) | direct owner directive + reconciliation |
| **1** | Governance scaffolding: `GOV-PLATFORM-SOT-REGISTRY-001`, `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`, `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`, registry TOML scaffold at `config/registry/sot-artifacts.toml`, MemBase `sot_artifacts` table, `gt registry` CLI subcommand, `_check_sot_registry_completeness` doctor at WARN. **Per-record schema includes a `forbidden_substitutes` column (string list, optional) populated by Slice 2A** — schema is forward-compatible with Slice 2A. | `gtkb-platform-sot-consolidation-slice-1-governance-001` | TO BE FILED post-umbrella GO | new GOV/DCLs + formal-artifact-approval packets; umbrella PAUTH covers |
| **2A** | **Read-Discipline** (NEW from peer's project): populate `forbidden_substitutes` metadata on Slice-1 registry records for 8 survey-identified pairs (`DELIB-20260670`); add Read-tool PreToolUse hook with per-call audit-read marker silencer (`DELIB-20260672` AUQ#6/14); add `.claude/rules/sot-read-discipline.md` standalone rule + interrogative-default extension in `prime-builder-role.md` (AUQ#10); extend `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` with read-discipline clauses + 1-2 new DCLs (`DCL-SOT-REGISTRY-SCHEMA-001`/`DCL-SOT-READ-HOOK-CONTRACT-001` per AUQ#11); strip rule-file state-prose (per peer's WI-4348). | `gtkb-platform-sot-consolidation-slice-2a-read-discipline-001` | TO BE FILED post-umbrella GO | new owner-decision evidence in `DELIB-20260672`; new PAUTH at child-bridge time |
| **2B** | **Anti-Recurrence Hook** (NEW from S408 reconciliation): PreToolUse hook on bridge-file Writes (`bridge/<slug>-NNN.md`) that BLOCKS NEW filings (proposals introducing a new Document) unless the session has run `gt projects list` (or equivalent) within last N minutes; intent is to prevent parallel sessions filing overlapping projects. Slice 2B can alternatively fold into Slice 5 (Bridge-Protocol SoT) if Codex prefers fewer slices — owner reconciliation AUQ#3 left mechanism placement open ("may be its own slice OR included with Read-Discipline"). This revision proposes standalone Slice 2B for clearest causation, but Codex may NO-GO with "merge with Slice 5" without prejudice. | `gtkb-platform-sot-consolidation-slice-2b-anti-recurrence-001` (or merged into Slice 5) | TO BE FILED post-umbrella GO | `DELIB-20260673` (parallel-fragmentation evidence) + S408 reconciliation AUQ#3 |
| **3** | Startup-control SoT — finishes `GTKB-STARTUP-REFRACTOR-001` outstanding slices; deprecates `config/agent-control/CONTROL-MAP.md`, `REVIEW-MODE-SETUP.md` | `gtkb-startup-refractor-slice-c-overlays-001` (or successor) | TBD per startup-refractor sequence | extends existing project |
| **4** | Harness-state SoT (in flight) | `gtkb-harness-state-sot-consolidation-phase-1-*` (existing; GO at -004) | GO-004 | existing PAUTH preserved (`PAUTH-PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION-...-IMPLEMENTATION-ENVELOPE`) |
| **5** | Bridge-protocol SoT — registers `bridge/INDEX.md`, `.gtkb-state/work-intent/`, dispatch-state, claim contract with health-check pointers; deprecates `.claude/rules/bridge-poller-canonical.md` stub; may absorb Slice 2B anti-recurrence hook | `gtkb-platform-sot-consolidation-slice-5-bridge-protocol-001` | TBD | new |
| **6** | IPA legacy retirement — archive IPA Codex operating contracts to `archive/ipa-legacy-2026-06-04/`; leave redirect README; preserve `CODEX-INSIGHT-DROPBOX/` as live LO advisory channel | `gtkb-platform-sot-consolidation-slice-6-ipa-retirement-001` | TBD | new + per-file owner AUQ if any file has non-obvious value |
| **7** | Adopter scaffolding — extend `groundtruth-kb/templates/managed-artifacts.toml` to scaffold the SoT registry into adopter projects; doctor check ports to adopter; gates on v0.7.0 stable per owner decision 7 | `gtkb-platform-sot-consolidation-slice-7-adopter-001` | TBD (v0.7.0 stable) | new |
| **8** | **MEMORY.md + Topic-Files Reconciliation** — single destructive commit strips current MEMORY.md content (peer's AUQ#15 strip-now), applies index-only template (peer's AUQ#7), separates topic files into allowed (`memory/feedback_*.md`, `memory/pattern_*.md`) and forbidden (`memory/project_*.md`, `memory/state_*.md`) (peer's AUQ#9), THEN establishes ongoing 60-day retention doctor check + index-length doctor check (my Q5). Strip-now resets state; retention+index governs steady-state. NOT a conflict — sequencing makes both compatible. | `gtkb-platform-sot-consolidation-slice-8-memory-reconciled-001` | TBD | new; combines both owner-decision sources `DELIB-20260671` Q5 + `DELIB-20260672` AUQ#7/9/15 |

Per-slice PAUTHs and per-slice work items remain child-bridge responsibilities. The umbrella authorizes the sequencing and the governance contract; the umbrella PAUTH is unchanged (narrowly scoped to Slice-1 governance work only); Slices 2A, 2B, 3, 5, 6, 7, 8 file their own PAUTHs.

## WI Migration Plan

The 13 stranded work items (`WI-4340` through `WI-4352`) currently in `PROJECT-GTKB-AGENT-SOT-READ-DISCIPLINE` migrate into `PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION` after umbrella GO.

**Migration mechanism:** `gt projects add-item PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION WI-NNNN` for each + `gt projects remove-item PROJECT-GTKB-AGENT-SOT-READ-DISCIPLINE WI-NNNN` for each. Membership state changes; the WI rows themselves are unchanged. Owner-decision authority: `DELIB-20260672` (peer's 16-AUQ pass) carried forward + S408 reconciliation top-level AUQ.

**Slice mapping for migrated WIs (preserved scope; folded under new slices):**

| WI | Title (short) | Migrates to umbrella slice |
|---|---|---|
| WI-4340 | 3 spec inserts: extend `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` + 2 DCLs | Slice 2A |
| WI-4341 | SoT registry hybrid (TOML + MemBase) | **Resolved by Slice 1** (structurally subsumed). Owner-AUQ-required to confirm WI-4341 should be retired vs converted to "populate registry rows" follow-on. **See §Open Owner Decision.** |
| WI-4342 | Read-tool PreToolUse hook | Slice 2A |
| WI-4343 | doctor check `_check_sot_read_discipline` | Slice 2A (sibling to Slice 1's `_check_sot_registry_completeness`) |
| WI-4344 | new rule file `.claude/rules/sot-read-discipline.md` | Slice 2A |
| WI-4345 | interrogative-default extension in `prime-builder-role.md` | Slice 2A |
| WI-4346 | MEMORY.md strip+template | Slice 8 |
| WI-4347 | topic-files separation | Slice 8 |
| WI-4348 | rule-file state-prose strip | Slice 2A |
| WI-4349 | assertions | Slice 2A + Slice 1 |
| WI-4350 | glossary | Slice 2A + Slice 1 |
| WI-4351 | Codex parity | Slice 2A |
| WI-4352 | registry-extension process | **Resolved by Slice 1** (structurally subsumed). Owner-AUQ-required. **See §Open Owner Decision.** |

**Project retirement:** After all 13 WIs are migrated (and the umbrella reaches GO), `PROJECT-GTKB-AGENT-SOT-READ-DISCIPLINE` is retired via `gt projects retire PROJECT-GTKB-AGENT-SOT-READ-DISCIPLINE` with a terminal version citing the umbrella absorption. Peer's PAUTH (`PAUTH-PROJECT-GTKB-AGENT-SOT-READ-DISCIPLINE-AGENT-SOT-READ-DISCIPLINE-PHASE-1-IMPLEMENTATION-ENVELOPE`) was already revoked at peer's WITHDRAWN filing; no further PAUTH action needed.

## Open Owner Decision

**WI-4341 and WI-4352 disposition:** Both items are structurally subsumed by Slice 1's governance scaffolding (Slice 1 builds the registry AND its extension process). Two paths:

- **A.** Retire WI-4341 and WI-4352 as "subsumed by Slice 1" after umbrella GO; no migration; backlog auto-resolves.
- **B.** Migrate as "populate registry rows from forbidden-substitute survey" (WI-4341 → Slice 2A WI) and "read-discipline-process extension" (WI-4352 → Slice 2A WI).

This is a minor open question — both paths are defensible. **Owner will be asked via AskUserQuestion before WI migration executes.** This umbrella does NOT presume an answer; the migration plan above lists Path A as default but flags both items as owner-AUQ-required.

## PAUTH Refresh Assessment

**Umbrella PAUTH** (`PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-UMBRELLA-SLICE-1-GOVERNANCE-ENVELOPE`): **unchanged**. The umbrella PAUTH was narrowly scoped to Slice-1 governance work; Slice 1's scope and mutation classes are unchanged by this revision (the registry record schema is forward-compatible with Slice 2A's `forbidden_substitutes` column addition, but the column is OPTIONAL and Slice 1 doesn't need to populate it). Adding Slice 2A and Slice 2B does NOT change Slice 1's authority.

**Per-slice PAUTHs** (for Slices 2A, 2B, 3, 5, 6, 7, 8): minted at each child-bridge time. Required mutation classes:

| Slice | New mutation classes needed | Owner-decision evidence |
|---|---|---|
| 2A | `governance_artifact_insert`, `rule_addition`, `hook_addition`, `source_addition`, `config_update`, `test_addition` | `DELIB-20260672` |
| 2B | `hook_addition`, `config_update`, `test_addition` | `DELIB-20260673` + S408 reconciliation AUQ#3 |
| 5 | `governance_artifact_insert`, `source_addition`, `config_update`, `test_addition` | `DELIB-20260671` Q1+Q2 |
| 6 | `file_archive_move`, `redirect_readme_add`, `governance_artifact_insert` | `DELIB-20260671` Q4 |
| 7 | `scaffold_template_addition`, `doctor_check_extension`, `test_addition` | `DELIB-20260671` Q7 |
| 8 | `file_content_replace` (MEMORY.md strip), `file_archive_move`, `hook_addition` (retention doctor check), `governance_artifact_insert` | `DELIB-20260671` Q5 + `DELIB-20260672` AUQ#7/9/15 |

## Specification-Derived Verification Plan

This umbrella remains `governance_review` with `target_paths: []` and `requires_verification: false`. Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, the actual spec-to-test mapping lives in each child slice. The umbrella's verification is structural:

- **Slice 1 must verify:** `GOV-PLATFORM-SOT-REGISTRY-001` inserted with `presented_to_user=true`; `config/registry/sot-artifacts.toml` exists and loads without `InvalidArtifactRecord`; MemBase `sot_artifacts` table exists; `gt registry list` returns bootstrap inventory; `_check_sot_registry_completeness` runs at WARN.
- **Slice 2A must verify:** `forbidden_substitutes` column added to `sot_artifacts` registry rows; 8 pairs populated; Read-tool PreToolUse hook emits SoT-redirect system-reminders on path match; per-call audit-read marker silencer suppresses correctly; `.claude/rules/sot-read-discipline.md` exists and is auto-loaded; interrogative-default extension references SoT registry; `_check_sot_read_discipline` doctor check runs.
- **Slice 2B must verify:** PreToolUse hook on bridge-file Writes blocks NEW filings without recent `gt projects list` query; legitimate filings (with query) succeed; bypass mechanism exists for emergencies (e.g., bridge-protocol-repair sessions per `.claude/rules/bridge-essential.md` owner-pre-approval clause).
- **Slices 3–8** carry per-spec verification matrices when filed.
- **Umbrella terminal:** GO on this REVISED-003.

## Risk and Rollback

**Risk** is moderate-to-high. The umbrella now spans 9 slices and absorbs two parallel owner directives. Specific risks:

- **Bootstrapping (unchanged):** Slice 1 self-registration still required.
- **Drift between TOML and MemBase projection (unchanged):** Slice 1 contract.
- **Slice 2A scope sprawl:** 6 mutation classes; 4+ source files; 1 new rule + interrogative-default edit + 1 GOV-extension + 1-2 DCLs. Splittable into 2A-1 (read-discipline-specs) and 2A-2 (read-discipline-hook+rule) if Codex prefers.
- **Slice 2B governance:** the anti-recurrence hook blocks legitimate work-flows that haven't run `gt projects list`. Mitigation: bypass mechanism with reason logging; doctor check verifies hook is not stuck; emergency-disable path via owner directive.
- **MEMORY.md strip-now blast radius:** the destructive strip in Slice 8 will affect all future sessions' auto-memory references. Reversible via git, but session continuity will rebuild from a smaller index for ~5 sessions. Owner has explicitly approved this via `DELIB-20260672` AUQ#15.
- **Meta-irony continued:** this revision itself was drafted without consulting the cross-harness trigger's behavior in real-time; the cross-harness trigger dispatched a parallel session that briefly held the claim. The anti-recurrence hook would have flagged this. Recommendation: file Slice 2B early in implementation sequence, before Slices 3+.

**Rollback** is straightforward. If LO NO-GOs the REVISED-003, the umbrella stays at NO-GO at -002; the in-flight harness-state Phase 1 (Slice 4) continues under its own PAUTH unaffected. The 13 WIs remain in `PROJECT-GTKB-AGENT-SOT-READ-DISCIPLINE` unchanged.

## Pre-Filing Preflight Subsection

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-platform-sot-consolidation-umbrella
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-platform-sot-consolidation-umbrella
```

Will be run by Codex on this file after INDEX update; both expected to pass (the spec set is unchanged from -001 which passed clean).

## Recommended Commit Type

`docs`: governance umbrella revision; no source mutation, no test mutation, no canonical artifact mutation. The 4 new DELIBs cited are already in MemBase (peer's 3 + mine).

## Recommended Outcome

**GO** for the REVISED-003 umbrella, with child slices following the §Slice Sequence table.

LO is asked to verify:

1. Slice sequence (9 slices) is coherent and child slices are tractable.
2. All 5 NO-GO requirements addressed (cross-reference §Codex NO-GO Requirements Addressed table).
3. WI migration plan is sound; the 2 open owner decisions (WI-4341, WI-4352 disposition) are appropriately deferred.
4. PAUTH refresh assessment is correct (umbrella PAUTH unchanged; per-slice PAUTHs cover new scope).
5. Slice 8 MEMORY.md reconciliation correctly sequences strip-now + retention+index-discipline as compatible (not conflicting).
6. The meta-irony (Codex NO-GO catching the same fragmentation pattern the umbrella addresses) is acknowledged and structurally addressed via Slice 2B.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
