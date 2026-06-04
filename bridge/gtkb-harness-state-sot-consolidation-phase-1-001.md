NEW

# Phase-1 Harness-State SoT Consolidation — Governance Umbrella + Spec Drafts

bridge_kind: governance_review
Document: gtkb-harness-state-sot-consolidation-phase-1
Version: 001
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-04 UTC
Recipient: Loyal Opposition (Codex, harness A)
Project: PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION
Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION-HARNESS-STATE-SOT-CONSOLIDATION-PHASE-1-IMPLEMENTATION-ENVELOPE

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: ea180cec-1e77-4700-beed-cde3905bd344
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, interactive session

target_paths: []

requires_verification: false
implementation_scope: governance_only

## Why governance_review

This umbrella covers 13 Phase-1 WIs across 4 implementation slices. Each child impl bridge will declare its primary Work Item; the umbrella's deliverable is the design+governance contract Codex GOs on, then the children execute. Same structural reasoning as `bridge/gtkb-ollama-integration-phase-1-001.md` filed earlier in S408.

## Summary

Owner directive 2026-06-04: "please remove all non-SoT references to the harness state, registration, role, etc. There is too much clutter and fragmentation. There must be a single SoT and never cached or copied versions."

The umbrella seeks GO on:
1. **GOV-HARNESS-STATE-SOT-CONSOLIDATION-001** — designates 3 SoT surfaces (roles, identities, capabilities), establishes the single canonical reader entrypoint contract, enumerates retired paths.
2. **DCL-HARNESS-STATE-SOT-READER-CONTRACT-001** — mechanical reader-entrypoint discipline; direct file reads in committed code become assertion-failing.
3. **DCL-HARNESS-STATE-SOT-ASSERTION-001** — machine-checkable consistency assertions.
4. **Retire-spec** — declares `harness-state/role-assignments.json` retired; deletion authorized after referencer migration.
5. **PAUTH** already minted (rowid 122).

The 13 implementation WIs (WI-4327 … WI-4339) execute via four child bridges filed AFTER umbrella GO:
- `gtkb-harness-state-sot-consolidation-phase-1-foundation-001` — WI-4327 (spec inserts) + WI-4328 (canonical entrypoint) + WI-4329 (doctor check)
- `gtkb-harness-state-sot-consolidation-phase-1-rule-files-001` — WI-4330 (5 rule files) + WI-4331 (CLAUDE.md+AGENTS.md) + WI-4332 (overlay retire) + WI-4338 (glossary)
- `gtkb-harness-state-sot-consolidation-phase-1-scripts-source-001` — WI-4333 (12 scripts) + WI-4334 (4 source modules) + WI-4335 (4 configs) + WI-4337 (Codex parity audit) + WI-4339 (packet-builder audit)
- `gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-001` — WI-4336 (delete role-assignments.json), runs last

**Drift evidence motivating the project** (DELIB-20260669, session_harvest): live `harness-state/harness-registry.json` has A=`["loyal-opposition"]` single-role; legacy mirror `harness-state/role-assignments.json` has A=`["loyal-opposition","prime-builder"]` dual-role with stale 2026-06-02 "Antigravity unavailable" reason. Different operational stories from two files; 36+ active referencer paths.

**Owner-Grilling-Gate (per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`):** This umbrella isn't from an LO advisory (the gate fires for `adopt`/`adapt` LO advisories only). It IS from a direct owner directive whose 8-AUQ grilling-pass owner-decision evidence is archived as DELIB-20260668 with full `presented_to_user=true` and `transcript_captured=true` per `GOV-ARTIFACT-APPROVAL-001` discipline.

**Explicit Phase 1 boundary:** EXCLUDED — `harness-state/bridge-substrate.json` (separate WI-4326 / DELIB-20260665), modification of role state VALUES (cleanup is read-path only), adding new harnesses, weakening existing role assertions.

## Specification Links

| Spec | Severity | Trigger | How this umbrella complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via bridge/INDEX.md as NEW versioned bridge file; INDEX entry inserted after Write. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section exists with comprehensive citation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification, spec-to-test | governance_review with `requires_verification: false`; child impl bridges carry per-spec test mapping. See §Specification-Derived Verification Plan. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/ | Doctor check WI-4329 + source module migrations WI-4334 touch `groundtruth-kb/src/groundtruth_kb/project/doctor.py` and `mode_switch/*.py` — all in-tree, root-bounded. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | blocking | content:cited paths, content:source of truth | This project DIRECTLY EXTENDS the SoT freshness governance to the harness-state surface. New GOV cites GOV-SOURCE-OF-TRUTH-FRESHNESS-001 as parent authority. |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | content:ADR/DCL/GOV/spec inserts | 4 formal-artifact-approval packets needed for the new GOV + 2 DCLs + retire-spec; generated after umbrella GO + owner per-packet approval. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH, path:project authorization | PAUTH-PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION-... (v1, rowid 122) cited. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH cites DELIB-20260668 as owner-decision, includes 13 WIs + 5 framing specs + 6 allowed mutations + 5 forbidden operations. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 approved framing specs. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | blocking | path:harness-state/**, content:role | Project touches harness-state/* paths; preserves role portability semantic — the cleanup is about READ DISCIPLINE, not state changes. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | advisory | content:role, content:harness-registry | Session-stated role override semantic continues to read role-set membership through the canonical entrypoint. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:specification, ADR, DCL, work item, owner decision | 13 WIs, 4 new specs, 2 DELIBs, 1 owner directive — fully artifact-routed. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation | Project enumerates artifact reorganization (SoT + entrypoint + retired-paths inventory). |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:verified | Umbrella terminal at GO; children terminal at VERIFIED. |
| `DCL-CONCEPT-ON-CONTACT-001` | advisory | content:new concepts | "canonical reader entrypoint", "retired paths inventory" — new concepts surfaced in spec drafts; glossary updates land via WI-4338. |
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` | not-applicable | adopt/adapt LO advisory | Project source is direct owner directive, not LO advisory. Gate doesn't fire; owner-grilling discipline applied voluntarily via 8-AUQ pass anyway, archived as DELIB-20260668. |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items inserts | 13 Phase-1 WIs inserted as canonical backlog rows; project membership recorded; PAUTH includes work-item-id list. |

## Requirement Sufficiency

**Existing requirements sufficient.** Owner directive + 8 AUQ decisions in DELIB-20260668 resolve all material requirement-disambiguation questions. The 4 new specs drafted below are governance/design artifacts derived from those decisions, not new requirements.

## Prior Deliberations

- **`DELIB-20260668`** (this turn, S408, `owner_conversation`, `outcome=owner_decision`) — Project owner-decision DELIB with 8 AUQ Q+A pairs. DIRECT OWNER-DECISION ANCHOR.
- **`DELIB-20260669`** (this turn, S408, `session_harvest`, `outcome=informational`) — Stale legacy mirror vs canonical registry drift evidence. DIRECT MOTIVATION FOR THE PROJECT.
- **`DELIB-20260665`** (S408 earlier, `owner_conversation`, `outcome=informational`) — Substrate-revisit DELIB. Surfaced the larger fragmentation pattern; led to this project.
- **`DELIB-20260602-BRIDGE-SIGNAL-SUBSTRATE-STATE-ONLY`** (2026-06-02) — Owner affirmation of intentional substrate inactivity at logging-policy level. Adjacent governance.
- **Commit `c9e1efa7`** (2026-06-01) — "Configure Claude-offline bridge mode per owner directive". Set substrate=none, suspended B, recorded the dual-role mirror state that now diverges from canonical.
- **Bridge thread `gtkb-retire-role-assignments-mirror-slice-1-seed-repoint`** — earlier Slice 1 work that marked the mirror "orphan" but didn't delete it. This project is the follow-through.

_No prior deliberations: rejected — multiple direct precedents cited above._

## Owner Decisions / Input

8 AUQ answers archived as `DELIB-20260668` (`source_type=owner_conversation`, `outcome=owner_decision`, `presented_to_user=true`, `transcript_captured=true`, `approved_by=owner`).

- **AUQ#1 — Scope:** Roles + identities + capabilities (3 surfaces).
- **AUQ#2 — SoT contract:** Mechanical single entrypoint.
- **AUQ#3 — Mirror fate:** Delete entirely (clean cut).
- **AUQ#4 — Governance depth:** Heavy (GOV + 2 DCLs + retire-spec).
- **AUQ#5 — Overlay rule files:** Retire `harness-state/{claude,codex}/operating-role.md` entirely.
- **AUQ#6 — PAUTH:** One project PAUTH (minted v1, rowid 122).
- **AUQ#7 — Cadence:** Sliced — governance scaffold first, then per-domain children.
- **AUQ#8 — Drift DELIB:** Separate `session_harvest` DELIB (filed as DELIB-20260669).

## Phase 1 WI Roster + Child Bridge Mapping

| WI | Title (short) | Child Bridge |
|----|---------------|--------------|
| WI-4327 | Insert 4 specs (GOV + 2 DCLs + retire-spec) | foundation |
| WI-4328 | Canonical reader entrypoint module | foundation |
| WI-4329 | Doctor `_check_harness_state_sot_consistency` | foundation |
| WI-4330 | 5 `.claude/rules/*.md` files | rule-files |
| WI-4331 | CLAUDE.md + AGENTS.md | rule-files |
| WI-4332 | Retire 2 overlay rule files | rule-files |
| WI-4338 | Glossary updates in canonical-terminology.md | rule-files |
| WI-4333 | 12 scripts → canonical entrypoint | scripts-source |
| WI-4334 | 4 `groundtruth_kb` source modules | scripts-source |
| WI-4335 | 4 config files | scripts-source |
| WI-4337 | Codex-side parity audit (`.codex/`) | scripts-source |
| WI-4339 | 8 packet-builder script audit | scripts-source |
| WI-4336 | Delete `harness-state/role-assignments.json` | mirror-retirement (final) |

## Proposed Specification Drafts

### GOV-HARNESS-STATE-SOT-CONSOLIDATION-001

**Type:** `governance`. **Status:** `specified`.

**Title:** Harness State Source-of-Truth Consolidation — three SoT surfaces, single canonical reader entrypoint, retired paths.

**Contract:** GroundTruth-KB harness state is exclusively governed by three SoT files:

1. **Roles SoT:** `harness-state/harness-registry.json` — MemBase projection per `REQ-HARNESS-REGISTRY-001`. Records each harness's role-set + status + capability ref + version.
2. **Identities SoT:** `harness-state/harness-identities.json` — installation-stable harness-name → ID map.
3. **Capabilities SoT:** `config/agent-control/harness-capability-registry.toml` — per-harness capability fingerprint.

All readers MUST access these SoTs through one canonical entrypoint:

- **Python:** `groundtruth_kb.harness_projection.{read_roles, read_identity, read_capabilities}`
- **Shell:** `gt harness list|role <id>|capability <name>` CLI subcommands

Direct file reads of these three SoTs in committed code are FORBIDDEN except inside the canonical entrypoint module itself (which IS the canonical reader).

**Retired paths:** `harness-state/role-assignments.json` is retired per the companion retire-spec; deletion authorized after referencer migration. `harness-state/{claude,codex}/operating-role.md` overlay rule files are retired (deletion authorized).

**Extends:** `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`. This GOV is the harness-state-specific instantiation of the general source-of-truth freshness governance.

**Severity:** blocking (asserted via doctor + machine-checkable assertions in DCL-HARNESS-STATE-SOT-ASSERTION-001).

**Assertions:**
- Grep absent: no committed code references `role-assignments.json` (except as historical record in bridge files, audit archives, formal-artifact-approval packets).
- Grep absent: no committed code outside `groundtruth_kb.harness_projection` reads harness-state/*.json or harness-capability-registry.toml directly.
- File-existence: canonical entrypoint module exists and exports the three documented functions.

**Related:** `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` (this proposal), `DCL-HARNESS-STATE-SOT-ASSERTION-001` (this proposal), retire-spec (this proposal), `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (parent).

---

### DCL-HARNESS-STATE-SOT-READER-CONTRACT-001

**Type:** `design_constraint`. **Status:** `specified`. **Affected by:** `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`.

**Title:** Mechanical reader-entrypoint discipline for harness-state SoTs.

**Constraint:** Every reader of harness-state roles, identities, or capabilities MUST go through the canonical entrypoint:

- Python imports use `from groundtruth_kb.harness_projection import read_roles, read_identity, read_capabilities`.
- Shell scripts use `gt harness {list, role, capability}` subcommands.
- Direct `json.load(open("harness-state/harness-registry.json"))` style reads are FORBIDDEN in committed code (except inside the canonical entrypoint module).
- TOML reads via `tomllib.load(open("config/agent-control/harness-capability-registry.toml"))` likewise FORBIDDEN outside the entrypoint.

**Enforcement:** Static-grep assertion + doctor `_check_harness_state_sot_consistency` (3-layer check from WI-4329). The doctor FAILs on grep matches for retired-path references or out-of-entrypoint reads.

**Severity:** blocking. Direct file reads recreate the exact fragmentation this project retires.

**Assertions:**
- Grep absent: `harness-state/harness-registry.json` OR `harness-state/role-assignments.json` mentioned outside of: bridge files, audit archives, formal-artifact-approval packets, `groundtruth_kb.harness_projection`, and this DCL.
- Code-check: `groundtruth_kb.harness_projection` defines `read_roles`, `read_identity`, `read_capabilities`.
- Code-check: `gt harness list` subcommand returns canonical state.

---

### DCL-HARNESS-STATE-SOT-ASSERTION-001

**Type:** `design_constraint`. **Status:** `specified`. **Affected by:** `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`.

**Title:** Machine-checkable consistency assertions for harness-state SoTs and retired paths.

**Constraint:** The following assertions MUST evaluate against the live repository state and MUST PASS:

1. **No retired-path references in code paths.** Grep across `scripts/`, `groundtruth-kb/src/`, `config/`, `.claude/rules/`, `CLAUDE.md`, `AGENTS.md` for `role-assignments` returns 0 matches.
2. **No out-of-entrypoint direct reads.** Grep for `json.load.*harness-state/` and `tomllib.load.*harness-capability-registry.toml` outside `groundtruth_kb.harness_projection` returns 0 matches.
3. **Canonical entrypoint exists and exports documented functions.** Code-check confirms `groundtruth_kb.harness_projection.read_roles`, `read_identity`, `read_capabilities` are callable.
4. **Retired paths are physically absent** (after WI-4336 deletion completes): `harness-state/role-assignments.json` does not exist; `harness-state/{claude,codex}/operating-role.md` do not exist.
5. **3 SoT files parse and pass schema validation.** `harness-registry.json`, `harness-identities.json`, `harness-capability-registry.toml` all load without error.

**Severity:** blocking. Failures reported as doctor FAIL + assertion run record.

**Enforcement:** Assertions field on this DCL evaluated by `gt assert`. Doctor `_check_harness_state_sot_consistency` rolls them up in platform health output.

---

### Retire-spec for harness-state/role-assignments.json

**Type:** `governance` (sub-type: retirement spec). **Status:** `specified`.

**Title:** Retire `harness-state/role-assignments.json` legacy mirror.

**Decision:** `harness-state/role-assignments.json` is retired. The file is deleted from the tree after all referencer paths have migrated to the canonical reader entrypoint (per WI-4330 → WI-4339).

**Rationale:** Live drift evidence captured in DELIB-20260669: registry has A=`["loyal-opposition"]` single-role; mirror has A=`["loyal-opposition","prime-builder"]` dual-role with stale "Antigravity unavailable" reason from 2026-06-02. Two files; different operational stories; 36+ active referencers. Per AUQ#3 clean-delete decision, no preservation path (no generated mirror, no deprecated-header).

**Authorization:** This retire-spec authorizes the deletion in WI-4336 after migration. Prior to that WI, referencer migration MUST be complete (per `forbid: delete_active_referencer_without_migration` in the project PAUTH).

**Successor:** All read access flows through `groundtruth_kb.harness_projection` (canonical entrypoint) reading from `harness-state/harness-registry.json` (canonical roles SoT).

**Assertions:**
- File-absent: `harness-state/role-assignments.json` does not exist post-WI-4336.
- Grep absent: no live code references the retired path.

**Related:** `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` (parent), `DELIB-20260669` (drift evidence), bridge thread `gtkb-retire-role-assignments-mirror-slice-1-seed-repoint` (earlier orphan-marking work).

## Proposed Protected-File Edits (Summary)

Concrete diffs are drafted in the rule-files child bridge (`gtkb-harness-state-sot-consolidation-phase-1-rule-files-001`) post-umbrella-GO. Summary of intent:

- **5 `.claude/rules/*.md` files** — drop every "(legacy mirror at `harness-state/role-assignments.json` is an orphan compatibility surface per Slice 1 retirement; not authoritative)" parenthetical. Replace with citation of the canonical entrypoint where state semantics matter.
- **`CLAUDE.md`** — role-precedence paragraph drops the dual-source narrative; cites only the SoT path.
- **`AGENTS.md`** — analogous treatment.
- **`harness-state/claude/operating-role.md` + `harness-state/codex/operating-role.md`** — DELETED per AUQ#5.
- **`.claude/rules/canonical-terminology.md`** — glossary entries for "role assignment", "harness identity", "operating role" updated to cite the SoT path + canonical entrypoint exclusively. Per `DCL-CONCEPT-ON-CONTACT-001`, the new concept "canonical reader entrypoint" gets its own glossary entry.

## Child Bridges Filed After Umbrella GO

### Child 1 — `gtkb-harness-state-sot-consolidation-phase-1-foundation-001`

- bridge_kind: `implementation_proposal` | Primary WI: WI-4327 | Bundled: WI-4328, WI-4329
- target_paths: 4 approval packets, `groundtruth-kb/src/groundtruth_kb/harness_projection.py` (extend), `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (extend), `tests/groundtruth_kb/test_harness_projection.py`, `tests/groundtruth_kb/test_doctor_sot.py`, `gt` CLI subcommand wiring.
- Verification: 4 specs exist; entrypoint module imports cleanly; doctor sub-checks PASS; pytest passes.
- Commit type: `feat:` (new module + new doctor check + new CLI subcommands; net-new capability surface).

### Child 2 — `gtkb-harness-state-sot-consolidation-phase-1-rule-files-001`

- bridge_kind: `implementation_proposal` | Primary WI: WI-4330 | Bundled: WI-4331, WI-4332, WI-4338
- target_paths: 5 `.claude/rules/*.md` + CLAUDE.md + AGENTS.md + 2 overlay deletions + canonical-terminology.md, plus 8 narrative-artifact-approval packets.
- Verification: grep returns 0 hits on `role-assignments` in target rule files; canonical-terminology doctor check PASSes.
- Commit type: `refactor:` (no behavior change; prose cleanup).

### Child 3 — `gtkb-harness-state-sot-consolidation-phase-1-scripts-source-001`

- bridge_kind: `implementation_proposal` | Primary WI: WI-4333 | Bundled: WI-4334, WI-4335, WI-4337, WI-4339
- target_paths: 12 scripts + 4 source modules + 4 config files + `.codex/` audit reports + packet-builder script audit reports.
- Verification: grep absent for `role-assignments` and direct-file reads outside entrypoint; all existing tests pass.
- Commit type: `refactor:` (read-path migration; no behavior change).

### Child 4 — `gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-001`

- bridge_kind: `implementation_proposal` | Primary WI: WI-4336
- target_paths: deletion of `harness-state/role-assignments.json`.
- Verification: file deleted; assertions in DCL-HARNESS-STATE-SOT-ASSERTION-001 pass; `forbid: delete_active_referencer_without_migration` is satisfied (children 2 + 3 must VERIFIED first).
- Commit type: `chore:` (file deletion, no code change beyond the removal).

**Recommended Child Ordering:** foundation → rule-files → scripts-source → mirror-retirement. The mirror cannot be deleted until all referencers are migrated; otherwise the impl-start-gate or doctor will catch broken references.

## Specification-Derived Verification Plan (for this Umbrella)

This umbrella's deliverable is the design + governance contract; it does NOT carry executable verification. Children carry per-WI verification.

| Source | Verification | PASS criterion |
|--------|--------------|---------------|
| GOV-HARNESS-STATE-SOT-CONSOLIDATION-001 + 2 DCLs + retire-spec drafts | Codex review of each draft body for internal consistency, contract clarity, alternatives | Codex GO with no NO-GO findings on the spec drafts |
| Protected-file edits summary | Codex review of intent (concrete diffs in child) | Codex GO with no NO-GO findings on the cleanup scope |
| PAUTH envelope | Codex review of scope + allowed/forbidden mutations | Codex confirms scope appropriate |
| Drift-evidence DELIB-20260669 | Codex confirms drift is real + project addresses it | Codex acknowledges drift evidence in verdict |
| Per-cluster impl | Each child's §Spec-Derived Verification Plan | Cross-reference |

## Recommended Commit Type

`refactor:` — Phase 1 is read-path cleanup + governance scaffolding; no new product capability + no bug fix. The umbrella's commit is documentation-style; children land actual code + protected-file changes (mostly `refactor:` with foundation child as `feat:` for the new entrypoint module).

## Risk / Rollback

### Risks (umbrella-scope)

1. **Codex NO-GO on spec drafts.** Most likely on GOV-HARNESS-STATE-SOT-CONSOLIDATION-001 (large surface) or DCL-HARNESS-STATE-SOT-READER-CONTRACT-001 (strict mechanical enforcement). _Mitigation:_ revise per findings; refile REVISED `-003`.
2. **Codex challenges retire-spec for the mirror.** Possible if Codex believes the legacy mirror serves an undocumented role (e.g., external tools). _Mitigation:_ DELIB-20260669 drift evidence is the response; if Codex finds undocumented external readers, revise to generated-mirror path instead (but that contradicts AUQ#3 — would need re-grilling).
3. **Codex objects to mechanical reader contract scope (DCL-001).** Possible if Codex finds non-Python readers (e.g., hooks written in PowerShell that read role-assignments) without easy entrypoint access. _Mitigation:_ extend canonical entrypoint to include subprocess-friendly `gt harness` CLI; document in DCL.

### Risks (cascade to children)

4. **Foundation child's canonical entrypoint design too restrictive.** If `read_roles` doesn't expose enough flexibility (e.g., legacy callers wanted JSON dicts not normalized objects), downstream children block. _Mitigation:_ foundation child surfaces caller-survey first; entrypoint design reflects discovered patterns.
5. **Inter-child dependencies.** Foundation must land before rule-files (rule files cite the entrypoint module by name). Rule-files + scripts-source must land before mirror-retirement (mirror can't delete with live referencers).
6. **Doctor `_check_harness_state_sot_consistency` causes false-PASSes on stale state during migration.** _Mitigation:_ doctor check is added in foundation child but reports WARN (not FAIL) until WI-4336 lands; promoted to FAIL after mirror retirement.

### Rollback

If umbrella NO-GO'd: empty target_paths means nothing to revert; file REVISED `-003`.

If a child later NO-GO'd or fails verification: per-child revert; re-file REVISED.

If Phase 1 wrong-direction: revert all 4 children; reinstate role-assignments.json from git history; retire the 3 new specs with `supersedes_reason`; revoke PAUTH; note in DELIB-20260669 that the drift was accepted as policy state going forward.

## Applicability Preflight

(Appended after `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1`.)

## Clause Applicability

(Appended after `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1`.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
