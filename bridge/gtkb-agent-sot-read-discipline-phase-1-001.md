NEW

# Phase-1 Agent SoT-Read Discipline — Governance Umbrella + Spec Drafts

bridge_kind: governance_review
Document: gtkb-agent-sot-read-discipline-phase-1
Version: 001
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-04 UTC
Recipient: Loyal Opposition (Codex, harness A)
Project: PROJECT-GTKB-AGENT-SOT-READ-DISCIPLINE
Project Authorization: PAUTH-PROJECT-GTKB-AGENT-SOT-READ-DISCIPLINE-AGENT-SOT-READ-DISCIPLINE-PHASE-1-IMPLEMENTATION-ENVELOPE

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

This umbrella covers 13 Phase-1 WIs across 4 implementation slices (structural / mechanical / behavioral / assertion). Each child impl bridge declares its primary Work Item; the umbrella's deliverable is the design+governance contract Codex GOs on, then children execute. Same structural reasoning as the two sibling umbrellas filed earlier in S408 (ollama, SoT-consolidation).

## Summary

Owner directive 2026-06-04 (S408): "We need to find a way to stop agents from using MEMORY.md or other files as alternatives to the SoT for a given artifact. This fragmentation is a major issue for us long-term."

This project addresses the agent BEHAVIOR pattern that produces fragmentation. Sibling `PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION` (also filed S408; umbrella at GO -004) cleans up one specific artifact class (harness state); this project layers a discipline contract on top to prevent the same pattern from recurring across all artifact classes.

**This umbrella seeks GO on:**
1. **Extended `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`** (new version, not new top-level GOV per AUQ#11) — adds read-discipline clauses to the existing freshness governance.
2. **`DCL-SOT-REGISTRY-SCHEMA-001`** — hybrid TOML source-of-truth + MemBase projection schema per AUQ#5.
3. **`DCL-SOT-READ-HOOK-CONTRACT-001`** — Read-tool PreToolUse hook contract with deterministic path-match (AUQ#6) and per-call audit-read marker silencer (AUQ#14).
4. **New rule file `.claude/rules/sot-read-discipline.md`** + **extension to `.claude/rules/prime-builder-role.md`** interrogative-default section (both per AUQ#10).
5. **MEMORY.md index-only template** + **strip-now-destructive cadence** (AUQ#7 + AUQ#15).
6. **PAUTH** already minted (v1, rowid 124).

**Empirical foundation:** `DELIB-20260670` manual-triage of S408 transcript surfaced 7 concrete substitution instances + 4 cross-cutting patterns + 8 forbidden-substitute candidates. Pattern A (rule-files-quoting-state) dominates 5/7 instances; Pattern B (always-loaded-salience) underlies most failures; Pattern C (audit-reads-need-silencer) shapes the hook contract; Pattern D (structural-fix-wins) motivates MEMORY.md restructure.

**Triggering instance:** my own confused-substrate analysis earlier in S408 — I asserted "cross-harness trigger auto-dispatches" from rule-file prose without verifying live state. Owner challenge → live-state evidence → substrate-revisit DELIB → SoT-consolidation project → this project. Direct causal chain.

**The 13 Phase-1 WIs (WI-4340 … WI-4352) execute via four child bridges:**
- `gtkb-agent-sot-read-discipline-phase-1-foundation-001` — WI-4340 (3 spec inserts) + WI-4341 (SoT registry) + WI-4342 (Read-tool hook) + WI-4343 (doctor check) + WI-4349 (assertions)
- `gtkb-agent-sot-read-discipline-phase-1-behavioral-001` — WI-4344 (standalone rule) + WI-4345 (interrogative-default extension) + WI-4350 (glossary)
- `gtkb-agent-sot-read-discipline-phase-1-structural-001` — WI-4346 (MEMORY.md strip+template) + WI-4347 (topic-files split) + WI-4348 (rule-file state-prose strip)
- `gtkb-agent-sot-read-discipline-phase-1-parity-001` — WI-4351 (Codex parity) + WI-4352 (registry-extension process)

**Explicit Phase 1 boundary:** EXCLUDED — harness-state surfaces (sibling project), modifying MemBase write side (this is read-discipline only), retiring `memory/feedback_*.md` or `memory/pattern_*.md` (preserved per AUQ#9), Codex-side hook installation (audit only Phase 1; replication after stability).

## Specification Links

| Spec | Severity | Trigger | How this umbrella complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via bridge/INDEX.md as NEW versioned bridge file. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification, spec-to-test | governance_review with `requires_verification: false`; children carry per-spec test mapping. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/ | Doctor check WI-4343 touches `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — in-tree, root-bounded. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | blocking | content:cited paths, content:source of truth | DIRECT PARENT — this project EXTENDS this GOV with read-discipline clauses. New version inserted via WI-4340 per AUQ#11. |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | content:ADR/DCL/GOV/spec inserts | 3 formal-artifact-approval packets needed (GOV extension + 2 new DCLs); generated after umbrella GO + owner per-packet approval. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH | PAUTH (v1, rowid 124) cited. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH cites DELIB-20260672, 13 WIs, 5 framing specs, 6 allowed mutations, 5 forbidden ops. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 approved framing specs. |
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` | not-applicable | adopt/adapt LO advisory | Direct owner directive, not LO advisory. 16-AUQ grilling discipline applied anyway; archived as DELIB-20260672. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:owner decision, specification, DCL, work item | 16 owner decisions, 13 WIs, 3 new/extended specs, 5 DELIBs cited. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation, MemBase | All Phase-1 surfaces are artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:verified, retired | Children land at VERIFIED; current MEMORY.md content retires under strip-now cadence. |
| `DCL-CONCEPT-ON-CONTACT-001` | advisory | content:new concepts | New concepts surfaced: "SoT registry", "forbidden substitute", "audit-read marker". Glossary updates land via WI-4350. |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items inserts | 13 Phase-1 WIs inserted as canonical backlog rows; PAUTH includes work-item-id list. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | advisory | path:harness-state/**, content:role | Mentioned in survey instances but harness-state surfaces are out-of-scope (sibling project). |
| `GOV-SESSION-ROLE-AUTHORITY-001` | advisory | content:role, content:harness-registry | Same — sibling-project territory. |

## Requirement Sufficiency

**Existing requirements sufficient.** Owner directive + 16 AUQ decisions in DELIB-20260672 + empirical survey in DELIB-20260670 resolve all material requirement-disambiguation questions. The 3 new/extended specs drafted below are governance/design artifacts derived from these inputs, not new requirements.

## Prior Deliberations

- **`DELIB-20260672`** (this turn, S408, `owner_conversation`, `outcome=owner_decision`) — Project owner-decisions DELIB. 16 AUQ Q+A. DIRECT OWNER-DECISION ANCHOR.
- **`DELIB-20260670`** (S408 earlier, `session_harvest`, `outcome=informational`) — Manual-triage survey of S408 transcript. EMPIRICAL FOUNDATION.
- **`DELIB-20260668`** (S408 earlier, `owner_conversation`, `outcome=owner_decision`) — Sibling project (SoT-consolidation) owner decisions.
- **`DELIB-20260669`** (S408 earlier, `session_harvest`, `outcome=informational`) — Sibling project's drift-evidence DELIB.
- **`DELIB-20260665`** (S408 earlier, `owner_conversation`, `outcome=informational`) — Substrate-revisit DELIB. The S408 incident that surfaced the broader fragmentation pattern.
- **`DELIB-20260602-BRIDGE-SIGNAL-SUBSTRATE-STATE-ONLY`** (2026-06-02) — Owner affirmation of intentional substrate inactivity. Adjacent governance context.
- **Sibling project bridges:** `gtkb-harness-state-sot-consolidation-phase-1-001` (NEW at S408; progressed to GO -004). Same shape; addresses harness-state file class.
- **Earlier project bridge:** `gtkb-ollama-integration-phase-1-001` (NEW at S408; GO -004). Same umbrella+children pattern.

_No prior deliberations: rejected — extensive direct precedent cited above._

## Owner Decisions / Input

16 AUQ answers archived as `DELIB-20260672` (`source_type=owner_conversation`, `outcome=owner_decision`, `presented_to_user=true`, `transcript_captured=true`, `approved_by=owner`). Summary table; full Q+A in the DELIB body.

| # | Decision | Authority |
|---|----------|-----------|
| 1 | Scope determined empirically by survey (not pre-committed) | B1-Q1 |
| 2 | Enforcement = layered (structural + mechanical + behavioral) | B1-Q2 |
| 3 | Sibling project (not extension of SoT-consolidation) | B1-Q3 |
| 4 | Continue grilling before drafting | B1-Q4 |
| 5 | SoT registry = hybrid TOML source + MemBase projection | B2-Q1 |
| 6 | Hook trigger = deterministic path-match on forbidden_substitutes | B2-Q2 |
| 7 | MEMORY.md target = index-only (1-page session-index) | B2-Q3 |
| 8 | Survey methodology = manual triage of S408 transcript | B2-Q4 |
| 9 | Topic files = feedback+patterns OK, project/state forbidden | B3-Q1 |
| 10 | Behavioral rule placement = both standalone + interrogative-default cross-cite | B3-Q2 |
| 11 | Governance = extend GOV-SOURCE-OF-TRUTH-FRESHNESS-001 + 1-2 DCLs | B3-Q3 |
| 12 | Survey + scope across this turn and next, one more grilling batch | B3-Q4 |
| 13 | Phase 1 scope = all 8 forbidden-substitute candidates | B4-Q1 |
| 14 | Hook silencer = per-call intent marker | B4-Q2 |
| 15 | MEMORY.md cadence = strip-now destructive single commit | B4-Q3 |
| 16 | Project name = PROJECT-GTKB-AGENT-SOT-READ-DISCIPLINE (no counter-proposal received; treated as confirmed) | B4-Q4 |

## Phase 1 WI Roster + Child Bridge Mapping

| WI | Title (short) | Child Bridge | Layer |
|----|---------------|--------------|-------|
| WI-4340 | Insert 3 spec drafts (extend GOV + 2 DCLs) | foundation | mechanical |
| WI-4341 | Hybrid SoT registry (TOML + MemBase projection) | foundation | mechanical |
| WI-4342 | Read-tool PreToolUse hook | foundation | mechanical |
| WI-4343 | Doctor `_check_sot_read_discipline` | foundation | mechanical |
| WI-4349 | Machine-checkable assertions | foundation | mechanical |
| WI-4344 | `.claude/rules/sot-read-discipline.md` (standalone) | behavioral | behavioral |
| WI-4345 | Extend prime-builder-role.md interrogative-default | behavioral | behavioral |
| WI-4350 | Glossary entries in canonical-terminology.md | behavioral | behavioral |
| WI-4346 | MEMORY.md strip + index-only template | structural | structural |
| WI-4347 | Topic-files separation (retire project_*.md) | structural | structural |
| WI-4348 | Strip current-state prose from .claude/rules/*.md | structural | structural |
| WI-4351 | Codex-side parity audit | parity | follow-on |
| WI-4352 | Document registry-extension process | parity | follow-on |

## Proposed Specification Drafts

### GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (extended; new version)

**Type:** `governance`. **Status:** `specified` (at version bump).

**Title:** Source-of-Truth Freshness (with read-discipline extension).

**Existing contract (preserved):** Avoid cached copies; prefer fresh reads. Reporting surfaces re-read SoT at request time.

**NEW read-discipline clauses (added in this version):**

1. **Single SoT per artifact-type.** Every artifact class has exactly one canonical Source of Truth. The canonical SoT is recorded in `config/governance/sot-registry.toml` (schema per `DCL-SOT-REGISTRY-SCHEMA-001`).

2. **Forbidden substitutes.** Each SoT registry entry MAY list `forbidden_substitute_paths` — non-SoT files that agents have been observed to read as alternatives. Reading a forbidden substitute path for a current-state question is a discipline violation.

3. **Read intent classification.** Reads fall into three classes:
   - *current-state*: "what is the value of X right now?" → MUST go through canonical SoT (via canonical reader entrypoint where applicable, or by reading the SoT file directly).
   - *mechanics*: "how does X work?" → rule files / documentation are appropriate primary sources.
   - *audit/history*: "what changed in X, when, why?" → any path with explicit audit-read marker (see hook contract DCL).

4. **MEMORY.md and topic-files scope.** `MEMORY.md` is the operational session notepad per ADR-0001; it MUST NOT contain canonical-state-shaped content. `memory/*.md` topic files MAY contain feedback rules + patterns; MUST NOT contain project/session/WI state summaries.

5. **Rule-file content discipline.** `.claude/rules/*.md` files describe mechanics + protocol + governance. They MAY cite SoT paths and explain semantics. They MUST NOT quote current state values that drift independently of the rule file's edit history.

6. **Enforcement.** Mechanical: PreToolUse hook on Read tool emits SoT-redirect reminders per `DCL-SOT-READ-HOOK-CONTRACT-001`. Structural: MEMORY.md template + topic-file separation. Behavioral: `.claude/rules/sot-read-discipline.md` + prime-builder-role.md interrogative-default extension. Assertion: doctor `_check_sot_read_discipline` + grep-style assertions.

**Severity:** blocking (asserted via doctor; failures reported as discipline violations).

**Assertions:**
- Grep absent: canonical-state-shaped content in `MEMORY.md` per index-only template.
- Grep absent: `memory/project_*.md` files (retired).
- File-existence: `config/governance/sot-registry.toml` exists with valid schema.
- File-existence: `.claude/hooks/sot-read-discipline.py` registered in `.claude/settings.json` PreToolUse Read.
- File-existence: `.claude/rules/sot-read-discipline.md` exists.

**Related:** `DCL-SOT-REGISTRY-SCHEMA-001`, `DCL-SOT-READ-HOOK-CONTRACT-001` (both this proposal); `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` (sibling).

---

### DCL-SOT-REGISTRY-SCHEMA-001

**Type:** `design_constraint`. **Status:** `specified`.
**Affected by:** `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`.

**Title:** Hybrid TOML+MemBase SoT registry schema.

**Constraint:** The SoT registry is implemented as a hybrid: `config/governance/sot-registry.toml` is the authoritative source-of-truth; a MemBase projection table `sot_registry` mirrors it for dashboard/audit access. The TOML schema is:

```
schema_version = 1

[[entries]]
artifact_type = "<snake_case key>"          # required, unique
canonical_sot_path = "<path or canonical entrypoint>"  # required
query_command = "<gt CLI subcommand>"       # optional but recommended
forbidden_substitute_paths = [<path>, ...]  # required list (may be empty)
audit_read_silencer_marker = "audit-read:<artifact_type>"  # required; per-call marker pattern
description = "<one-line>"                  # required for docs
```

**Initial entries (8 candidates from DELIB-20260670):**

| `artifact_type` | `canonical_sot_path` | Forbidden substitutes |
|---|---|---|
| `harness_roles` | `harness-state/harness-registry.json` via `groundtruth_kb.harness_projection.read_roles` | `harness-state/role-assignments.json`; `.claude/rules/operating-role.md` prose; `MEMORY.md` role mentions |
| `harness_identities` | `harness-state/harness-identities.json` via `read_identity` | rule-file/MEMORY mentions |
| `bridge_substrate` | `harness-state/bridge-substrate.json` | `.claude/rules/bridge-essential.md` substrate-state prose |
| `bridge_automation_status` | live dispatch-state JSONL + `.codex/hooks.json` + `.claude/settings.json` registrations | `.claude/rules/bridge-essential.md` automation prose |
| `project_state` | MemBase `projects` + `current_project_work_item_memberships` via `gt projects show` / `gt backlog list` | `MEMORY.md` "Projects" section; `memory/project_*.md` |
| `session_history` | MemBase `session_*` tables | `MEMORY.md` "Recent Sessions" |
| `module_api_surface` | Actual module source files | Rule-file paraphrases of module structure |
| `cached_sessionstart_payloads` | Live MemBase + doctor | `.claude/hooks/last-user-visible-startup-*.md` after relay |

**Severity:** blocking. Schema violations fail dispatch-time validation in the hook and doctor.

**Enforcement:** TOML parsed at hook PreToolUse; doctor regenerates MemBase projection; doctor validates schema + entry consistency.

**Assertions:**
- Grep: `sot-registry.toml` contains `schema_version = 1`.
- Code-check: every `[[entries]]` table has all required fields.
- Doctor: MemBase projection matches TOML content modulo regeneration timestamp.

---

### DCL-SOT-READ-HOOK-CONTRACT-001

**Type:** `design_constraint`. **Status:** `specified`.
**Affected by:** `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`.

**Title:** Read-tool PreToolUse hook contract.

**Constraint:** `.claude/hooks/sot-read-discipline.py` registered in `.claude/settings.json` as a PreToolUse hook on the Read tool. Behavior:

1. **Trigger:** Fires before every Read tool invocation.
2. **Match:** Reads `config/governance/sot-registry.toml`; checks whether the Read's target path appears in ANY entry's `forbidden_substitute_paths`.
3. **Silencer check:** If the surrounding agent context (current prompt + recent agent output buffer) contains the marker for the matched entry's `audit_read_silencer_marker` (e.g., `audit-read:harness_roles`), the hook is silent — agent has attested intent.
4. **System-reminder:** On match without silencer, hook emits a system-reminder including: the matched path, the canonical SoT path/entrypoint, the audit-read marker pattern if the read is legitimate, and a one-line rationale.
5. **Non-blocking:** Hook is informational. It does NOT block the Read; the read proceeds normally. The system-reminder educates the agent for the current and future calls.
6. **Fail-open:** Registry parse errors, file-missing, etc. → hook emits warning to stderr and proceeds; never breaks the Read.

**Audit-read marker format:** `audit-read:<artifact_type>` where `<artifact_type>` matches a registry entry's `artifact_type` field. Multiple markers allowed in one context. Markers persist within the current agent turn.

**Severity:** blocking (asserted via doctor — hook registration must be present in `.claude/settings.json`; hook script must be executable; tests cover both match-emits-reminder and marker-silences scenarios).

**Enforcement:** Doctor `_check_sot_read_discipline` includes hook-registration check; pytest covers hook behavior.

**Assertions:**
- Code-check: `.claude/hooks/sot-read-discipline.py` exists.
- Grep: `.claude/settings.json` PreToolUse Read array contains the hook path.
- Test: `tests/scripts/test_sot_read_discipline_hook.py` covers match + silencer + fail-open cases.

## Proposed Protected-File Edits (Summary)

Concrete diffs land in the behavioral and structural child bridges. Summary of intent:

- **NEW `.claude/rules/sot-read-discipline.md`** — standalone rule documenting the SoT contract, read-intent classes, audit-read marker, and per-call silencer pattern. Cross-cites prime-builder-role.md interrogative-default.
- **`.claude/rules/prime-builder-role.md`** — add "Interrogative default for state reads" subsection parallel to existing "Interrogative default for owner factual claims"; cross-cites the standalone rule.
- **`MEMORY.md`** — replaced (single commit, destructive per AUQ#15) with index-only template: (1) Current session focus, (2) Handoff context, (3) Operational reminders, (4) Canonical state pointers section with `gt` CLI navigation.
- **`memory/project_*.md` and similar state-summary files** — retired (audit + delete; any genuinely canonical content migrated to MemBase first).
- **`memory/feedback_*.md` and `memory/pattern_*.md`** — preserved per AUQ#9; auto-memory index updated to only reference these.
- **`.claude/rules/*.md`** — audit for current-state prose (e.g., "B is Prime Builder", "substrate is none"); rewrite to mechanics-description-only with SoT-path citations for verification.
- **`.claude/rules/canonical-terminology.md`** — new glossary entries for SoT registry, forbidden substitute, audit-read marker, canonical reader entrypoint.

## Child Bridges Filed After Umbrella GO

### Child 1 — foundation (mechanical layer)

- bridge_kind: `implementation_proposal` | Primary WI: WI-4340 | Bundled: WI-4341, WI-4342, WI-4343, WI-4349
- target_paths: 3 approval packets (extended GOV + 2 new DCLs), `config/governance/sot-registry.toml` (new), `.claude/hooks/sot-read-discipline.py` (new), `.claude/settings.json` (hook registration edit), `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (extend), `tests/groundtruth_kb/test_doctor_sot_read.py`, `tests/scripts/test_sot_read_discipline_hook.py`.
- Verification: 3 specs exist; hook fires on test scenarios; doctor sub-checks PASS; assertions PASS.
- Commit type: `feat:` (new mechanical infrastructure).

### Child 2 — behavioral

- bridge_kind: `implementation_proposal` | Primary WI: WI-4344 | Bundled: WI-4345, WI-4350
- target_paths: `.claude/rules/sot-read-discipline.md` (new), `.claude/rules/prime-builder-role.md` (extend interrogative-default), `.claude/rules/canonical-terminology.md` (glossary), 3 narrative approval packets.
- Verification: rule file exists; prime-builder-role.md has new subsection; glossary entries present; doctor canonical-terminology check PASSes.
- Commit type: `docs:` (rule documentation — but see Recommended Commit Type discussion below).

### Child 3 — structural

- bridge_kind: `implementation_proposal` | Primary WI: WI-4346 | Bundled: WI-4347, WI-4348
- target_paths: `MEMORY.md` (single destructive overwrite), `memory/project_*.md` (deletions after audit), `.claude/rules/*.md` (state-prose strips), narrative approval packets.
- Verification: grep returns 0 hits on canonical-state-shaped content in MEMORY.md; `memory/project_*.md` files absent; rule files cite SoT paths for state queries; doctor structural-layer check PASSes.
- Commit type: `refactor:` (no behavior change; content restructure).

### Child 4 — parity + process

- bridge_kind: `implementation_proposal` | Primary WI: WI-4351 | Bundled: WI-4352
- target_paths: `.codex/` audit reports, registry-extension process documentation appended to `.claude/rules/sot-read-discipline.md`.
- Verification: `.codex/` audit complete (either replicated hook or follow-on WI captured); process documentation present; doctor cross-harness parity check PASSes.
- Commit type: `chore:` (audit + process docs).

**Recommended Child Ordering:** foundation → behavioral → structural → parity. Foundation lands the registry + hook (so structural child has assertions to validate against); behavioral lands the rules (so structural child's MEMORY.md template references them); structural lands last as the most disruptive change; parity finalizes Codex side.

## Specification-Derived Verification Plan (for this Umbrella)

This umbrella's deliverable is the design + governance contract; it does NOT carry executable verification. Children carry per-WI verification.

| Source | Verification | PASS criterion |
|--------|--------------|---------------|
| Extended GOV-SOURCE-OF-TRUTH-FRESHNESS-001 + 2 new DCLs | Codex review of each draft for internal consistency, contract clarity | Codex GO with no NO-GO findings |
| Protected-file edits summary | Codex review of intent + child-bridge diff scope | Codex GO with no NO-GO findings |
| PAUTH envelope | Codex review of scope + allowed/forbidden mutations | Codex confirms scope appropriate |
| Empirical foundation (DELIB-20260670 survey) | Codex confirms survey is grounded + 8 candidates are well-chosen | Codex acknowledges survey in verdict |
| Per-cluster impl | Each child's §Spec-Derived Verification Plan | Cross-reference |

## Recommended Commit Type

`refactor:` — Phase 1 is read-path discipline + governance scaffolding. The foundation child adds new mechanical infrastructure (`feat:`) but the project as a whole is behavior + content restructure. Umbrella's own commit is `docs:`; the foundation child specifically commits `feat:` for the hook + doctor + registry.

## Risk / Rollback

### Risks (umbrella-scope)

1. **Codex NO-GO on extended GOV.** Possible — extending an active GOV is structurally riskier than inserting a new one. _Mitigation:_ versioning is append-only; revert is "promote previous version back" if the extension is rejected.
2. **Codex NO-GO on hook contract.** Most likely concern: blocking vs informational, fail-open behavior. Owner explicitly picked informational per AUQ#14 silencer design. _Mitigation:_ reaffirm in revision.
3. **MEMORY.md restructure risk.** Strip-now-destructive cadence loses historical project-state snapshots. _Mitigation:_ AUQ#15 was explicit; this is owner-accepted. Pre-strip audit migrates any canonical content to MemBase per the structural child's verification step.

### Risks (cascade to children)

4. **Foundation child's hook fires on legitimate audit reads without markers.** Until agents adopt the audit-read marker pattern, noise rate may be high. _Mitigation:_ hook is non-blocking + informational; agents learn over a few sessions.
5. **Structural child's MEMORY.md change is highly visible.** Every future session SessionStart will see the new index-only template. Owner may want to see it before commit. _Mitigation:_ structural child explicitly surfaces the new template for owner review at GO time.
6. **Inter-child dependencies.** Foundation → behavioral → structural → parity. Foundation hook can't reliably emit reminders until registry exists; behavioral rules can't reference structural changes until they exist; etc.

### Rollback

If umbrella NO-GO'd: empty target_paths; revise REVISED `-003`.

If a child later fails verification: per-child revert; re-file REVISED.

If Phase 1 is later judged wrong-direction: revert structural changes (re-create MEMORY.md from git history); retire 2 new DCLs and revert GOV-SOURCE-OF-TRUTH-FRESHNESS-001 to previous version; deactivate hook registration; revoke PAUTH.

## Applicability Preflight

(Appended after `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-agent-sot-read-discipline-phase-1`.)

## Clause Applicability

(Appended after `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-agent-sot-read-discipline-phase-1`.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
