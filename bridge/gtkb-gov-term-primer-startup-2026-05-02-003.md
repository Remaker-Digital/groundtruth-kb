REVISED

# GTKB-GOV-TERM-PRIMER-STARTUP — Scoping Proposal (REVISED-1)

Author: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Status: REVISED (responding to Codex NO-GO at `-002.md`)

## Revision Rationale (REVISED-1)

Codex NO-GO at `-002.md` issued 3 P1 findings + 2 non-blocking notes. All findings root in a shared error: I assumed `templates/project/canonical-terminology.{md,toml}` exists as a separate adopter template, when in fact the live managed surface is at `templates/rules/canonical-terminology.{md,toml}` with a different schema, and there's a VERIFIED prior bridge thread (`gtkb-canonical-terminology-surface-implementation-012.md`) that established this architecture in S-pre-294.

**Architectural pivot in REVISED-1:** This proposal is reframed as a **dogfood install** of the existing managed canonical-terminology surface for GT-KB itself, NOT as a parallel "term primer" system. GT-KB ships the templates that get scaffolded to adopter projects (`.claude/rules/canonical-terminology.{md,toml}`), but the GT-KB checkout itself does not have those files installed. This proposal closes that dogfood gap and extends term coverage to the 22-term owner-required minimum via multi-source attribution.

**Material changes from `-001.md`:**

- **Architectural pivot:** dogfood install of existing surface, not new system. Replaces `_check_canonical_terminology_primer` with the existing `_check_canonical_terminology` (no parallel doctor check).
- **Path corrections:** all `templates/project/...` paths replaced with `templates/rules/...`. Live registry rows `rule.canonical-terminology` and `rule.canonical-terminology-config` cited.
- **Prior Deliberations:** new section with 7 prior canonical-terminology DELIBs.
- **Source model:** multi-source per term (operating-model §2 + AGENTS.md + role rules + others) rather than single-source from §2 (resolves F3 contradiction).
- **CLI surface:** removed standalone `gt term-primer ...` commands; reuse existing `gt project doctor` flow + add `gt term-primer regenerate` only as a thin generator wrapper.
- **Schema reuse:** existing profile-aware `[config.profiles.*]` + `required_startup_terms` schema is preserved; this proposal extends `required_startup_terms` lists to cover all 22 owner-required terms.
- **Smart-poller dispatch:** preserves existing role-record + INDEX live-state language; primer reference is ADDITIVE (per non-blocking note 1).
- **Doctor severity:** existing ERROR severity preserved (per non-blocking note 2); previous Open Decision §A removed.

## Origin

Owner directive 2026-05-02 (S327, third turn) — full verbatim text at `bridge/gtkb-gov-term-primer-startup-2026-05-02-001.md` §"Origin". Owner observed that startup loading is too indirect, smart-poller spawns are highest drift surface, and recommended: short canonical primer, sourced from `operating-model.md §2`, loaded for both Prime + LO startup, included in smart-poller dispatch prompts, with doctor check enforcing presence. Minimum 22-term coverage specified verbatim.

Candidate Deliberation Archive entry: `DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE` (`source_type=owner_conversation`, `outcome=owner_decision`).

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

1. **`.claude/rules/operating-model.md` §2** — canonical terminology source. Defines ~13 of the 22 owner-required terms with allowed synonyms and forbidden uses. Authoritative for the terms it covers; multi-source attribution fills the gap for terms it does not cover (F3 resolution below).

2. **`.claude/rules/operating-model.md` §1** — operating-model framing for what an agent needs at session start. Constraint: primer must be available in immediate working context, not buried in a longer rule file.

3. **`.claude/rules/file-bridge-protocol.md`** — bridge protocol mandatory linkage gate. Constraint: this proposal complies; smart-poller dispatch references the primer.

4. **`.claude/rules/project-root-boundary.md`** — all artifacts within `E:\GT-KB`. Constraint: primer file lands at `.claude/rules/canonical-terminology.md` in the GT-KB checkout (matches the scaffolded adopter pattern).

5. **`.claude/rules/deliberation-protocol.md`** — deliberation search + owner-directive archival. Constraint: this proposal includes Prior Deliberations; owner directive archives at Slice 1 close.

6. **`AGENTS.md`** — currently has a short glossary covering subset of terms. Constraint: AGENTS.md glossary verified non-conflicting subset of primer (Slice 4); reused as a per-term source for terms it covers (per F3 multi-source).

7. **`CLAUDE.md` § "Working with This Project" + § "Canonical Terminology"** — current session-start convention. Constraint: this proposal does not change CLAUDE.md's load model; the primer file auto-loads via `.claude/rules/*.md` convention with no CLAUDE.md change required.

8. **`GOV-19-A1`** — outside-in testing. Constraint: tests exercise the public doctor surface (`gt project doctor`), not internal helpers.

9. **`GOV-20`** — architecture decisions. Constraint: cross-cutting; IPR/CVR per slice.

10. **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** — repetitive AI plumbing is a defect. Constraint: primer load is deterministic via file existence + auto-load convention; primer regeneration is deterministic via `gt term-primer regenerate`.

11. **`bridge/gtkb-bridge-poller-001-smart-poller-007.md`** (umbrella) — smart-poller dispatch prompt template. Constraint: dispatch prompt extension is ADDITIVE; preserves existing role-record + INDEX live-state instructions per Codex `-002.md` non-blocking note 1.

12. **`groundtruth-kb/templates/rules/canonical-terminology.md`** *(corrected path per F1)* — live managed-rule template scaffolded to adopter projects. Constraint: primer is an extension of this template (not a parallel artifact). GT-KB checkout install file at `.claude/rules/canonical-terminology.md`.

13. **`groundtruth-kb/templates/rules/canonical-terminology.toml`** *(corrected path per F1)* — live managed-rule profile-aware doctor config. Constraint: primer extends the existing `required_startup_terms` lists to cover the 22 owner-required terms; schema (profile-aware `[config.profiles.*]` blocks) is preserved unchanged.

14. **`groundtruth-kb/templates/managed-artifacts.toml`** registry rows `rule.canonical-terminology` and `rule.canonical-terminology-config` *(per F1)* — managed-rule registry contract. Constraint: primer install for GT-KB itself uses the same registry rows; no new registry surface created.

15. **`groundtruth-kb/src/groundtruth_kb/project/doctor.py`** `_check_canonical_terminology()` *(per F2)* — existing doctor check loaded via `run_doctor()`. Constraint: this proposal REUSES this check; does NOT create a parallel `_check_canonical_terminology_primer`. The check already enforces required_startup_terms presence at ERROR severity per profile.

16. **`groundtruth-kb/tests/test_doctor_canonical_terminology.py`** *(per F2)* — existing test surface covering profile matrix at lines 49-219. Constraint: extended (not replaced) to cover the 22-term GT-KB-checkout primer.

17. **`bridge/gtkb-canonical-terminology-surface-implementation-012.md`** (VERIFIED) *(per F2)* — prior architecture decision. Constraint: this proposal carries forward the registry-backed Option B contract; does NOT propose alternative architecture.

18. **`GOV-ARTIFACT-APPROVAL-001`** — formal-artifact approval contract. Constraint: any change to `templates/rules/canonical-terminology.{md,toml}` is a managed-rule template change requiring formal approval per the existing approval-packet contract; Slice 1 carries this packet.

## Prior Deliberations (per Codex F2)

Per `.claude/rules/deliberation-protocol.md`. Relevant prior deliberations identified:

- **`DELIB-0722` / `DELIB-1180`** — prior `gtkb-canonical-terminology-surface-implementation` bridge thread. **Preserved.** This proposal builds on the verified Option B architecture (`gtkb-canonical-terminology-surface-implementation-012.md`); does NOT propose alternative.
- **`DELIB-GTKB-IDP-TERMINOLOGY`** — owner decision that GT-KB is formally an Internal Developer Platform; IDP terminology used across docs/reports/adopter materials. **Preserved.** Primer term entries align with IDP framing (e.g., `application` defined per IDP semantics).
- **`DELIB-1138`, `DELIB-1016`, `DELIB-1017`, `DELIB-1018`, `DELIB-1019`** — prior bridge/review history for GT-KB IDP terminology formalization. **Preserved.** This proposal does not reopen those decisions; it extends term coverage to the 22-term primer set.
- **`DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE`** (this session, candidate; archival pending) — directly motivates this proposal.

**Differentiation:** No prior deliberation already approves a 22-term primer at the GT-KB-checkout level. The prior thread settled the architecture (registry-backed managed rules under `templates/rules/`); this proposal extends that architecture's term coverage and dogfoods the install for GT-KB itself.

## Problem Statement

§2 of `operating-model.md` is canonical and auto-loaded. The existing managed canonical-terminology surface (under `templates/rules/`) is VERIFIED and scaffolds to adopter projects. But:

1. **GT-KB checkout doesn't dogfood its own canonical-terminology surface.** Bash check `find .claude/rules -name "canonical-terminology*"` returns empty. The platform that ships the rules to adopters does not itself have those rules installed. Lost dogfooding catches drift in adopter installs but not in platform self-sessions.
2. **`required_startup_terms` lists are short.** The existing TOML profile-aware lists carry 3-5 terms each (per `templates/rules/canonical-terminology.toml` lines 14-39). Owner-required minimum is 22 terms — covers product identifiers (GT-KB, GroundTruth-KB, GTKB), Agent Red as application instance, adopter, plus full role/lifecycle/artifact set.
3. **Smart-poller dispatch doesn't include the primer.** Headless dispatch reconstructs terminology from rule files alone. Per `bridge/gtkb-bridge-poller-001-smart-poller-007.md`, dispatch prompts reference role-record + INDEX live state; no terminology reference.
4. **Empirical drift evidence in this very session.** Prime Builder (me) initially cited the wrong template path (`templates/project/...`) in `-001.md` despite the VERIFIED prior thread establishing `templates/rules/...`. That's the same drift class the primer targets.

## Proposed Direction (REVISED-1)

**Three concrete changes** to existing infrastructure (no new infrastructure):

### Change 1 — Install primer for GT-KB checkout (Slice 1)

Create `.claude/rules/canonical-terminology.md` and `.claude/rules/canonical-terminology.toml` in the GT-KB checkout itself, populated from the existing managed-rule templates with extended term coverage. This is a dogfood install: the GT-KB checkout becomes a consumer of its own scaffolded artifact, exercising the same install path adopters use.

The .toml extends `required_startup_terms` per profile to cover all 22 owner-required terms:

```toml
# Excerpt — full file at templates/rules/canonical-terminology.toml + GT-KB-extended terms.
[config.profiles.dual-agent]
required_startup_terms = [
    # Existing (preserved):
    "MemBase", "Deliberation Archive", "MEMORY.md", "Prime Builder", "Loyal Opposition",
    # New (per S327 owner directive — 22-term minimum):
    "GT-KB", "GroundTruth-KB", "GTKB", "platform", "application", "hosted application",
    "Agent Red", "adopter", "project", "work item", "backlog", "specification",
    "requirement", "implementation proposal", "implementation report", "verification",
    "dashboard", "bridge"
]
missing_severity = "ERROR"
```

The .md primer entries follow the existing managed-rule format (per `templates/rules/canonical-terminology.md`), with multi-source attribution per term (Change 2).

### Change 2 — Multi-source attribution per term (Slice 1, resolves F3)

Each primer entry declares its authoritative source. Sources are governed; no fabrication. Term-to-source mapping:

| Source | Terms |
|---|---|
| `operating-model.md` §2 | application, project, platform, hosted application, work item, backlog, specification, requirement, implementation proposal, implementation report, verification, MemBase, Deliberation Archive, dashboard |
| `AGENTS.md` short glossary | bridge, Prime Builder, Loyal Opposition |
| `prime-builder-role.md` + `loyal-opposition.md` rules | Prime Builder, Loyal Opposition (role-detail definitions) |
| `DELIB-GTKB-IDP-TERMINOLOGY` + `CLAUDE.md` | GT-KB, GroundTruth-KB, GTKB, adopter |
| Application-specific (Agent Red identity in CLAUDE.md) | Agent Red |

Each primer entry header includes the source citation (e.g., `**Source:** operating-model.md §2 "application"` or `**Source:** DELIB-GTKB-IDP-TERMINOLOGY + CLAUDE.md "Application Identity"`). T3 (renamed) verifies citation presence; T7 (renamed) verifies non-contradiction with the source.

### Change 3 — Smart-poller dispatch additive extension (Slice 3)

Per Codex `-002.md` non-blocking note 1: dispatch prompt template at `groundtruth-kb/scripts/bridge_poller_runner.py` lines 268-300 currently references role-record + `bridge/INDEX.md` live state. Extension is ADDITIVE — adds primer reference (one paragraph + content hash) without removing existing instructions. Fixture-based test (T8) asserts BOTH the primer reference AND the role-record/INDEX instructions remain present.

## Test Plan (REVISED-1)

| # | Test | Spec link | Asserts |
|---|---|---|---|
| T1 | `test_gt_kb_checkout_has_canonical_terminology_md_installed` | rule items 4 + 12 + 17 | `.claude/rules/canonical-terminology.md` exists in GT-KB checkout (dogfood install) |
| T2 | `test_required_startup_terms_cover_22_owner_minimum` | owner directive (verbatim 22 terms) | Each profile in `.claude/rules/canonical-terminology.toml` `required_startup_terms` covers all 22 owner-required terms |
| T3 (rewritten per F3) | `test_primer_term_entries_cite_source` | rule item 1 + multi-source policy | Each term entry in `.claude/rules/canonical-terminology.md` includes a `**Source:**` citation pointing at one of the governed sources |
| T4 | `test_primer_format_per_term` | §"Change 2" multi-source | Each term entry has the 3 required subsections (Canonical meaning / Allowed synonyms / Source) |
| T5 | `test_existing_doctor_check_passes_on_gt_kb_self` | rule item 15 (`_check_canonical_terminology`) | `gt project doctor` run on the GT-KB checkout itself reports `[OK] Canonical-terminology surface OK` |
| T6 | `test_doctor_check_fails_when_primer_missing` | rule item 15 | Renaming `.claude/rules/canonical-terminology.md` causes existing doctor check to return ERROR (already supported by the existing check; T6 verifies on the GT-KB-extended profile) |
| T7 (rewritten per F3) | `test_primer_term_entry_does_not_contradict_source` | rule item 1 | Doctor parses primer + cited source; for each term, primer's "Canonical meaning" semantic-matches source's definition (matching policy in Slice 1 design — substring or exact-quote allowed) |
| T8 | `test_smart_poller_dispatch_prompt_includes_primer_AND_preserves_existing` | rule item 11 + Codex `-002.md` non-blocking note 1 | Fixture-based assertion on dispatch-prompt template asserts BOTH (a) primer reference present AND (b) role-record instruction present AND (c) `bridge/INDEX.md` live-state instruction present |
| T9 | `test_agents_md_glossary_non_conflicting` | rule item 6 | AGENTS.md terms are subset of primer; no contradicting definitions; warning level (per Codex `-002.md` non-blocking note 2 — handled by existing severity, not new gate) |
| T10 | `test_regenerate_command_idempotent` | §"Change 2" multi-source | `gt term-primer regenerate` twice produces byte-identical output |
| T11 | `test_existing_canonical_terminology_thread_preserved` | rule item 17 (verified prior thread) | After landing, `gtkb-canonical-terminology-surface-implementation-012` evidence (registry rows, doctor check, scaffold tests) still resolves; test_doctor_canonical_terminology.py existing 15+ tests still pass |
| T12 | `test_release_candidate_gate_runs_doctor_with_terminology_check` | rule item 9 (GOV-20) | Release-candidate gate runs `gt project doctor` (which includes `_check_canonical_terminology`) before passing |
| T13 | `test_DELIB_S327_term_primer_directive_archived` | rule item 5 (deliberation-protocol) | After Slice 1 close, `DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE` archived |
| T14 | `test_GOV_ARTIFACT_APPROVAL_packet_admits_template_changes` | rule item 18 | Slice 1 changes to `templates/rules/canonical-terminology.{md,toml}` are admitted by `formal-artifact-approval-gate.py` only when the approval packet at `.groundtruth/formal-artifact-approvals/2026-MM-DD-term-primer-slice1.json` is present |

## Acceptance Criteria

- `.claude/rules/canonical-terminology.md` and `.toml` installed in GT-KB checkout (dogfood).
- `required_startup_terms` covers all 22 owner-required terms per profile.
- Each primer term entry cites its governed source.
- Existing `_check_canonical_terminology` doctor check passes on GT-KB self.
- Smart-poller dispatch prompt extended additively (T8 verifies preservation).
- AGENTS.md glossary verified non-conflicting subset.
- T1-T14 pass; existing 15+ canonical-terminology tests still pass (T11).
- `gt term-primer regenerate` thin wrapper implemented; idempotent (T10).
- IPR + CVR per `GOV-20`.
- Slice 1 template changes carry approval packet per `GOV-ARTIFACT-APPROVAL-001`.
- `DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE` archived (T13).
- Ruff + lint clean.

## Risk and Rollback

- **Risk: extending `required_startup_terms` breaks existing adopter projects** that have shorter required-term lists in their installed `.claude/rules/canonical-terminology.toml`. Mitigation: existing adopters have copies of the older list; their doctor reads their local file. Only NEW scaffolds and `gt project upgrade` get the extended list. Upgrade behavior: append-only (new terms added; existing entries preserved).
- **Risk: multi-source attribution drifts.** Mitigation: T7 doctor non-contradiction check; T10 regenerate is idempotent; CI runs both.
- **Risk: smart-poller dispatch prompt grows materially.** Mitigation: primer reference uses content hash (not full inclusion) when full size exceeds prompt budget. Configurable.
- **Risk: dogfood install creates spurious test failures because GT-KB checkout has different file layout than scaffolded adopters.** Mitigation: T5 + T11 explicitly run on GT-KB self; doctor check already supports `harness-memory` profile for non-standard layouts.
- **Rollback:** revert `.claude/rules/canonical-terminology.{md,toml}` install; smart-poller dispatch revert; existing managed-rule template at `templates/rules/` unchanged. Adopter-side behavior unaffected.

## Sequencing

1. **Slice 1 — Dogfood install + extended term coverage.** Create `.claude/rules/canonical-terminology.{md,toml}` in GT-KB checkout from extended templates; multi-source attribution per term; formal-artifact-approval packet for template changes. T1-T7 + T11 + T14.
2. **Slice 2 — Regenerate CLI command.** `gt term-primer regenerate` thin wrapper that re-derives primer content from sources. T10.
3. **Slice 3 — Smart-poller dispatch additive extension.** Per `-002.md` non-blocking note 1. T8.
4. **Slice 4 — AGENTS.md glossary reconciliation.** Verified subset OR reduced to pointer at primer. T9.
5. **Slice 5 — Release-candidate gate.** `gt project doctor` already in gate; just verify terminology check is not skipped. T12 + T13.

## Open Decisions

§A (REMOVED — resolved by Codex `-002.md` non-blocking note 2: existing ERROR severity for missing required terms is already in place and inherits to extended terms).

§B. **AGENTS.md fate.** (i) Pointer-only at primer, (ii) Verified subset retained for Codex-specific framing, (iii) Generated from primer. Suggest (ii) — minimum disruption; T9 already handles non-conflict.

§C. **Regeneration cadence.** On every source-edit (auto-trigger via hook) vs. owner-triggered. Suggest both.

§D. **Multi-source attribution policy file format.** The source-to-term mapping (Change 2 table) lives in `templates/rules/canonical-terminology.toml` as a new `[sources]` section, OR as a separate `.claude/rules/canonical-terminology-sources.toml`. Suggest extending existing TOML (one config file, not two).

§E. **`DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE` archival timing.** Suggest Slice 1 close.

## Out of Scope

- Implementation of Slices 1-5 (each lands its own bridge with code + tests).
- Restructuring `operating-model.md` §2. Section 2 remains authoritative; this proposal extracts but does not modify.
- Cross-application term primers. Per-application overlays (e.g., Agent Red specifics) are future slices.
- Auto-fixing terminology in existing artifacts. Drift in old artifacts is preserved as historical evidence.

## Spec-to-test mapping (summary)

- operating-model.md §2 → T3, T7 (multi-source attribution + non-contradiction)
- operating-model.md §1 → T5 (loading at session start via existing doctor)
- file-bridge-protocol.md → all (proposal compliance with linkage gate)
- project-root-boundary.md → T1, T11 (in-root install)
- deliberation-protocol.md → T13 (DELIB archival)
- AGENTS.md → T9 (non-conflicting subset)
- CLAUDE.md → T1, T11 (load model unchanged)
- GOV-19-A1 → T2, T5 (outside-in via doctor)
- GOV-20 → IPR/CVR per slice
- DELIB-S312 → T10 (regenerate idempotent)
- bridge/gtkb-bridge-poller-001-smart-poller-007.md → T8 (additive dispatch)
- templates/rules/canonical-terminology.md + .toml → T1, T2, T11
- templates/managed-artifacts.toml registry rows → T1, T11
- src/.../doctor.py `_check_canonical_terminology` → T5, T6, T11
- tests/test_doctor_canonical_terminology.py → T11 (existing tests preserved)
- gtkb-canonical-terminology-surface-implementation-012 → T11 (verified prior thread)
- GOV-ARTIFACT-APPROVAL-001 → T14 (Slice 1 approval packet)
- Owner directive (verbatim 22 terms) → T2

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
