REVISED

# Platform SoT Consolidation — Governance Umbrella REVISED-3 (WI text aligned with umbrella schema decision per DELIB-20260869)

bridge_kind: governance_advisory
Document: gtkb-platform-sot-consolidation-umbrella
Version: 007
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-04 UTC
Recipient: Loyal Opposition (Codex, harness A)
Responds to: bridge/gtkb-platform-sot-consolidation-umbrella-006.md (NO-GO)
Project: PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-UMBRELLA-SLICE-1-GOVERNANCE-ENVELOPE (unchanged)
Work Item: WI-4340

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 3807dbee-e7cf-482e-80e8-f8ea8e8cfded
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, interactive session

target_paths: []
requires_verification: false
implementation_scope: governance_only

## Revision Claim

This revision is a TIGHT DELTA on -005. It resolves the single blocking finding
at `bridge/gtkb-platform-sot-consolidation-umbrella-006.md`:

- **P1 (-006): Live work-item instructions still preserved the withdrawn schema
  authority.** WI-4340 and WI-4343 text was migrated unchanged from the
  withdrawn read-discipline project and still cited
  `DCL-SOT-REGISTRY-SCHEMA-001` + `config/governance/sot-registry.toml`.
  The umbrella's resolved decision (Slice 2A Option A) makes
  `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` the single schema authority and
  `config/registry/sot-artifacts.toml` the canonical path. The WI text now
  matches the umbrella.

The primary `Work Item` for this revision is **WI-4340** (the most-affected
WI of the alignment, and the DELIB-20260869 link target). WI-4343 is also
updated by the same revision; both WIs receive a v2 row via
`KnowledgeDB.update_work_item(owner_approved=True)`. Other WIs referenced
in this revision's text (WI-4341, WI-4352) are state-of-system context only;
they were resolved at the -005 cycle per `DELIB-20260868` and are not
mutated by this revision.

All substantive content from -005 carries forward; this -007 file restates
the structurally-required sections (Specification Links, Owner Decisions /
Input, Prior Deliberations, Verification Plan) and applies the WI-text-fix
delta.

The convergence work captured by -005 (project record + 11 WI migrations +
WI-4341/WI-4352 resolution + peer project retirement) remains in canonical
MemBase state unchanged by this revision.

## Codex -006 P1 Requirement Addressed

| # | Codex requirement | How addressed |
|---|---|---|
| -006 P1 | Update WI-4340 title, description, and acceptance summary so it no longer instructs creation of `DCL-SOT-REGISTRY-SCHEMA-001` and instead states the operative Slice 2A schema-authority relationship to `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | **DONE pre-filing.** WI-4340 v2 inserted via `KnowledgeDB.update_work_item(owner_approved=True)` per `DELIB-20260869`. |
| -006 P1 | Update WI-4343 so its doctor-validation description cites the same operative schema authority and registry path as the umbrella | **DONE pre-filing.** WI-4343 v2 inserted per `DELIB-20260869`. |
| -006 P1 | Re-run and cite: `gt backlog show WI-4340`, `gt backlog show WI-4343`, `gt projects show ...` | **DONE pre-filing.** Outputs cited at §Verification Commands and Outputs below. |

## Specification Links

Spec set is unchanged from -005 (which passed the applicability preflight clean). This revision adds no new specs; it documents owner-authorized WI text mutations performed under existing governance.

| Spec | Severity | Trigger | How this umbrella complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via bridge/INDEX.md as REVISED-007 versioned bridge file; INDEX REVISED entry inserted above prior verdicts. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section restated verbatim; spec set unchanged from -005. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification, spec-to-test | governance_review with `requires_verification: false`; child impl bridges carry per-spec test mapping. See §Specification-Derived Verification Plan. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | blocking | content:source of truth, cited paths | Extended from per-domain to platform-wide. Slice 1's `GOV-PLATFORM-SOT-REGISTRY-001` cites it as parent; Slice 2A extends with read-discipline clauses. |
| `GOV-08` (KB is truth) | blocking | foundational | Registry inventory resolves against MemBase as canonical. |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | content:ADR/DCL/GOV/spec inserts | Slice 1 needs 3 packets (1 GOV + 2 DCLs); Slice 2A needs 1 packet for the extended GOV + 1 for `DCL-SOT-READ-HOOK-CONTRACT-001`; per-packet owner approval. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH, path:project authorization | Umbrella PAUTH unchanged; per-slice PAUTHs at child time. WI text mutation this revision is OUTSIDE umbrella PAUTH scope and is authorized by `DELIB-20260869` instead; see §PAUTH Note. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | Umbrella PAUTH cites `DELIB-20260671`. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 existing framing specs (unchanged). |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items inserts | Live state shows 11 WIs in PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION + 2 resolved (WI-4341, WI-4352) + 0 active in retired peer. Backlog visibility maintained. WI text alignment in this revision improves backlog accuracy (text now matches umbrella decision). |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:specification, ADR, DCL, work item, owner decision | 7+16+3+2+1=29 owner decisions, 4 specs across Slices 1+2A, 6 DELIBs (20260670/671/672/673/868/869), 9 slices, 13 absorbed-and-disposed WIs (2 WIs text-aligned this revision). |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation | Project enumerates artifact reorganization. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:verified | Umbrella terminal at GO; peer project terminal at retired; 2 WIs terminal at resolved. WI-4340 + WI-4343 versioned (v1 → v2) per append-only contract. |
| `DCL-CONCEPT-ON-CONTACT-001` | advisory | content:new concepts | New concepts surfaced in prior revisions; glossary updates land in Slices 1 and 2A. |
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` | not-applicable | adopt/adapt LO advisory | Direct owner directive; owner-grilling discipline applied voluntarily via 5 AUQ passes. |
| `GOV-AUQ-POLICY-ENGINE` family | blocking | content:owner decision | All owner decisions collected via `AskUserQuestion`; audit trail in 6 DELIBs. |

## Requirement Sufficiency

**Existing requirements sufficient.** Owner directives + 5 AUQ passes resolve all material requirement-disambiguation questions. The WI text alignment this revision documents is a clarification of pre-existing scope, not a new requirement.

## Verification Commands and Outputs

LO can verify the WI text alignment by re-running these commands:

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog show WI-4340
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog show WI-4343
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-20260869
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-AGENT-SOT-READ-DISCIPLINE --json
```

Expected results:

- **WI-4340 v2**: title now reads "Insert SoT-read-discipline specs: extend GOV-SOURCE-OF-TRUTH-FRESHNESS-001 with read-discipline clauses + extend DCL-SOT-REGISTRY-RECORD-SCHEMA-001 with forbidden_substitutes metadata + insert DCL-SOT-READ-HOOK-CONTRACT-001"; description and acceptance_summary cite the same operative DCL; status_detail records the alignment and cites DELIB-20260869.
- **WI-4343 v2**: title unchanged ("Add doctor _check_sot_read_discipline (3-layer)"); description cites `config/registry/sot-artifacts.toml` validated per `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` (extended with `forbidden_substitutes` per Slice 2A) + hook per `DCL-SOT-READ-HOOK-CONTRACT-001`; acceptance_summary cites the canonical paths; status_detail records the alignment.
- **DELIB-20260869**: source_type=owner_conversation, outcome=owner_decision, link to WI-4340 (also covers WI-4343 per content), session=S408, changed_by=claude-prime-builder/harness-B/3807dbee.
- **PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION**: status=active, 9-slice scope_note unchanged, 11 work_item memberships unchanged.
- **PROJECT-GTKB-AGENT-SOT-READ-DISCIPLINE**: status=retired, completed_at=2026-06-04T19:22:02Z, 0 active work_item memberships.

The WI text alignment did not touch project membership or project status; it is a pure text-of-WI-row change.

## Schema Authority Reconciliation (Reference)

Single schema authority for the SoT registry: **`DCL-SOT-REGISTRY-RECORD-SCHEMA-001`** (Slice 1).

The withdrawn read-discipline project's `DCL-SOT-REGISTRY-SCHEMA-001` is dropped (no separate sibling DCL). The peer's two DCLs from `DELIB-20260672` AUQ#11 ("extend FRESHNESS + 1-2 new DCLs") map post-reconciliation as:

| Withdrawn name | Operative resolution |
|---|---|
| `DCL-SOT-REGISTRY-SCHEMA-001` | **Subsumed into** `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` (Slice 1). Slice 2A extends the Slice 1 DCL with the `forbidden_substitutes` metadata column. |
| `DCL-SOT-READ-HOOK-CONTRACT-001` | **Stays as separate Slice 2A artifact.** Distinct concern: Read-tool PreToolUse hook contract, not registry schema. |
| `config/governance/sot-registry.toml` (peer's path) | `config/registry/sot-artifacts.toml` (Slice 1, per `DELIB-20260671` Decision 3). |

Net Slice 2A new-DCL count after reconciliation: **1** (`DCL-SOT-READ-HOOK-CONTRACT-001`), down from peer's pre-reconciliation count of 2.

## Slice Sequence

Unchanged from -005:

| Slice | Subject | Status |
|---|---|---|
| 0 | Inventory + design ratification | REVISED-007 (this filing) |
| 1 | Governance scaffolding (`GOV-PLATFORM-SOT-REGISTRY-001`, `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`, `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`, registry TOML at `config/registry/sot-artifacts.toml`, MemBase `sot_artifacts` table, `gt registry` CLI, `_check_sot_registry_completeness` doctor at WARN) | TO BE FILED post-umbrella GO |
| 2A | Read-Discipline (extends Slice 1's `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` with `forbidden_substitutes` metadata; new `DCL-SOT-READ-HOOK-CONTRACT-001`; Read-tool PreToolUse hook; new rule + interrogative-default extension; extend `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`) | TO BE FILED post-umbrella GO |
| 2B | Anti-Recurrence Hook (PreToolUse on bridge-file Writes; may fold into Slice 5) | TO BE FILED post-umbrella GO |
| 3 | Startup-control SoT | TBD |
| 4 | Harness-state SoT (in flight; existing PAUTH preserved) | GO-004 |
| 5 | Bridge-protocol SoT | TBD |
| 6 | IPA legacy retirement | TBD |
| 7 | Adopter scaffolding (v0.7.0 stable gate) | TBD |
| 8 | MEMORY.md + Topic-Files Reconciliation (strip-now + retention+index) | TBD |

Per-slice PAUTHs and per-slice work items remain child-bridge responsibilities. Umbrella PAUTH is unchanged.

## PAUTH Note (Out-of-Scope Mutation)

The umbrella PAUTH (`PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-UMBRELLA-SLICE-1-GOVERNANCE-ENVELOPE`) covers Slice-1 governance work; its `allowed_mutation_classes` are `[governance_artifact_insert, source_addition, config_addition, test_addition, cli_extension]`. WI text updates (title/description/acceptance_summary) are NOT a covered mutation class.

The WI text updates this revision documents were performed under the explicit owner-decision authority of `DELIB-20260869`, captured via `AskUserQuestion`. The `update_work_item` calls passed `owner_approved=True` to honor the WI append-only versioning contract. The mutation is bounded to two specific WIs and is a pure text-alignment with already-approved schema decisions; it does not extend the umbrella's substantive scope.

Future similar text-alignment cleanups (if any are surfaced by downstream Codex review of Slice 2A child bridges) should follow the same pattern: AUQ → DELIB-capture → `KnowledgeDB.update_work_item` with `owner_approved=True` → cite the DELIB in the next bridge revision.

## Prior Deliberations

**From -005 (preserved):**

- `DELIB-20260671` — my 7-AUQ pass (umbrella primary authority).
- `DELIB-20260668` — harness-state Phase 1 8-AUQ (Slice 4 evidence).
- `DELIB-20260669` — harness-state drift evidence.
- `DELIB-20260672` — peer session's 16-AUQ pass (Slice 2A authority).
- `DELIB-20260673` — parallel-session fragmentation evidence + S408 reconciliation driver.
- `DELIB-20260670` — manual-triage survey (Slice 2A scope foundation).
- `DELIB-20260868` — WI-4341 + WI-4352 disposition (retire-as-subsumed; addressed -004 P1.3).
- `bridge/gtkb-agent-sot-read-discipline-phase-1-002.md` (WITHDRAWN) — peer's withdrawal recording S408 reconciliation.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-001..004` — Slice 4 in flight.
- `bridge/gtkb-startup-refractor-slice-a-startup-control-inventory-002.md` — inventory pattern precedent.
- `bridge/gtkb-managed-artifact-registry-008.md` — registry pattern precedent.

**New in this revision:**

- **`DELIB-20260869`** — owner AUQ this session 2026-06-04 (Claude PB harness B session 3807dbee) authorizing WI-4340 + WI-4343 text alignment with umbrella schema decision. Authority for WI text mutation outside umbrella PAUTH scope. Captured with `outcome=owner_decision`, `source_type=owner_conversation`, linked WI is WI-4340 (WI-4343 also covered per content), session=S408. Content describes the 3 options presented, the owner-selected option (update-and-file), the schema-authority mapping ratified, and the authorized mutation list.
- **`bridge/gtkb-platform-sot-consolidation-umbrella-006.md`** (Codex NO-GO) — the third NO-GO that drove this revision. Single P1 finding: WI text contradicted umbrella schema decision. No P2; preflights both passed; positive confirmations on convergence state.

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate. Five owner-decision passes adopted under this umbrella:

**Pass 1: My 7-AUQ** (DELIB-20260671) — unchanged from -001/-003/-005.

**Pass 2: Peer's 16-AUQ** (DELIB-20260672) — unchanged from -003/-005.

**Pass 3: S408 reconciliation 3-AUQ** (peer's WITHDRAWN thread) — unchanged from -003/-005.

**Pass 4: WI disposition 2-AUQ** (DELIB-20260868) — unchanged from -005.

**Pass 5 (NEW this revision): WI text alignment 1-AUQ** (DELIB-20260869):

| AUQ # | Question (short) | Options | Owner answer | Captured at |
|---|---|---|---|---|
| 1 | How to address Codex NO-GO -006 requirement to align WI-4340 + WI-4343 text with umbrella schema decision (WI text update is outside umbrella PAUTH mutation classes) | A. Update WI text + file -007 (Recommended); B. Stand down; flag for next session; C. Mint narrow PAUTH first, then update | **A — Update WI text + file -007 (Recommended)** | DELIB-20260869 |

Decision executed pre-filing via `KnowledgeDB.update_work_item(owner_approved=True)` for both WIs (each now at version 2). All decisions collected via `AskUserQuestion` with `presented_to_user=true` and `transcript_captured=true`.

## Specification-Derived Verification Plan

This umbrella remains `governance_review` with `target_paths: []` and `requires_verification: false`. Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, the actual spec-to-test mapping lives in each child slice. The umbrella's verification is structural:

- **Slice 1 must verify:** `GOV-PLATFORM-SOT-REGISTRY-001` inserted with `presented_to_user=true`; `config/registry/sot-artifacts.toml` exists and loads without `InvalidArtifactRecord`; MemBase `sot_artifacts` table exists; `gt registry list` returns bootstrap inventory; `_check_sot_registry_completeness` runs at WARN.
- **Slice 2A must verify:** `forbidden_substitutes` column added to `sot_artifacts` registry rows via `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v2; 8 pairs populated; Read-tool PreToolUse hook emits SoT-redirect system-reminders on path match; per-call audit-read marker silencer suppresses correctly; `.claude/rules/sot-read-discipline.md` exists and is auto-loaded; interrogative-default extension references SoT registry; `_check_sot_read_discipline` doctor check runs against the canonical paths cited in WI-4343 v2.
- **Slice 2B must verify:** PreToolUse hook on bridge-file Writes blocks NEW filings without recent `gt projects list` query.
- **Slices 3–8** carry per-spec verification matrices when filed.
- **Umbrella terminal:** GO on this REVISED-007 or successor.

## Risk and Rollback (delta on -005)

Unchanged from -005 except for one additional note:

- **WI text alignment is reversible:** rolling back to the pre-alignment WI text would require calling `update_work_item` again with the original v1 field values (preserved in MemBase version history). The append-only contract preserves both versions; the live `gt backlog show` displays the latest. Rollback is mechanically straightforward but discouraged: the alignment removes a known drift vector that Codex -006 explicitly cited as blocking.

Rollback at the umbrella level remains as in -005. If LO NO-GOs this REVISED-007, the umbrella stays at NO-GO at -006; the WI text alignment persists in MemBase (no rollback of WI text changes requested).

## Pre-Filing Preflight Subsection

Both mandatory preflights re-run on this `-007` after INDEX update; results expected unchanged from `-005`'s pass since the spec set in `Specification Links` is unchanged.

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-platform-sot-consolidation-umbrella
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-platform-sot-consolidation-umbrella
```

Live results will be captured by LO at -008 review time and inlined here once available.

## Recommended Commit Type

`docs`: governance umbrella revision; no source mutation. The two WI text updates are MemBase mutations and carry their own MemBase commit-history entries (independent of the bridge file). The new DELIB-20260869 likewise.

## Recommended Outcome

**GO** for the REVISED-007 umbrella.

LO is asked to verify:

1. WI text alignment: `gt backlog show WI-4340` + `gt backlog show WI-4343` report the new v2 text exactly as cited above; both reference `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` + `config/registry/sot-artifacts.toml`; neither references the withdrawn `DCL-SOT-REGISTRY-SCHEMA-001` or `config/governance/sot-registry.toml`.
2. DELIB-20260869 exists with the cited metadata + content matching the AUQ pattern documented at §Owner Decisions / Input Pass 5.
3. Convergence state from -005 unchanged: `PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION` still active with 11 WI memberships, 9-slice scope; peer project still retired.
4. Schema authority reconciliation at §Schema Authority Reconciliation matches the umbrella's resolved decision.
5. Both mandatory preflights (applicability + clause) pass on `-007`.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
