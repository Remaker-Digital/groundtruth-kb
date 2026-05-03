REVISED

# GTKB-GOV-TERM-PRIMER-STARTUP — Scoping Proposal (REVISED-2)

Author: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Status: REVISED (responding to Codex NO-GO at `-004.md`)

## Revision Rationale (REVISED-2)

Codex NO-GO at `-004.md` issued 1 P1 blocking finding (Prime-fixable). REVISED-1 (`-003.md`) correctly pivoted to dogfood-install architecture and resolved the prior 3 findings about path/architecture/source-model. The remaining issue:

- **F1** — `required_startup_terms` semantics reuse conflicts with existing doctor: the existing `_check_canonical_terminology()` validates that each term in `required_startup_terms` appears in EVERY entry of `required_files` (CLAUDE.md, AGENTS.md, MEMORY.md, etc.) — not in the primer file. Extending the list to 22 terms would force every startup file to contain all 22 terms. Resolved by adopting Codex's option 1: add a NEW field `required_primer_terms` (separate semantic) that targets the primer file specifically; preserve `required_startup_terms` semantics unchanged.

**Material changes from `-003.md`:**

- §"Change 1" TOML schema extension: adds NEW `required_primer_terms` field per profile; keeps existing `required_startup_terms` unchanged.
- `_check_canonical_terminology()` is EXTENDED (not reused-as-is) to evaluate the new `required_primer_terms` against primer file content; existing required_startup_terms semantics preserved.
- Test plan T2/T5/T6/T11 updated to assert dual-check semantics correctly.
- Acceptance criteria explicitly distinguishes the two coverage contracts.

All other sections unchanged from REVISED-1; carry forward.

## Origin

Owner directive 2026-05-02 (S327, third turn) — full verbatim text at `bridge/gtkb-gov-term-primer-startup-2026-05-02-001.md` §"Origin". 22-term minimum specified verbatim. Candidate Deliberation Archive entry: `DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE`.

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

1. **`.claude/rules/operating-model.md` §2** — canonical terminology source. Defines ~13 of 22 owner-required terms with allowed synonyms and forbidden uses. Authoritative for the terms it covers; multi-source attribution fills the gap.

2. **`.claude/rules/operating-model.md` §1** — operating-model framing for what an agent needs at session start. Constraint: primer must be available in immediate working context.

3. **`.claude/rules/file-bridge-protocol.md`** — bridge protocol mandatory linkage gate. Constraint: this proposal complies.

4. **`.claude/rules/project-root-boundary.md`** — all artifacts within `E:\GT-KB`. Constraint: primer file lands at `.claude/rules/canonical-terminology.md` in GT-KB checkout (matches scaffolded adopter pattern).

5. **`.claude/rules/deliberation-protocol.md`** — deliberation search + owner-directive archival. Constraint: this proposal includes Prior Deliberations.

6. **`AGENTS.md`** — currently has short glossary. Constraint: AGENTS.md glossary verified non-conflicting subset; reused as per-term source for terms it covers.

7. **`CLAUDE.md` § "Canonical Terminology"** — current session-start convention. Constraint: this proposal does not change CLAUDE.md's load model; primer auto-loads via `.claude/rules/*.md` convention.

8. **`GOV-19-A1`** — outside-in testing. Constraint: tests exercise public doctor surface (`gt project doctor`).

9. **`GOV-20`** — architecture decisions. Constraint: cross-cutting; IPR/CVR per slice.

10. **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** — repetitive AI plumbing is a defect. Constraint: primer load is deterministic via auto-load convention; regenerate is deterministic.

11. **`bridge/gtkb-bridge-poller-001-smart-poller-007.md`** — smart-poller dispatch. Constraint: dispatch prompt extension is ADDITIVE; preserves existing role-record + INDEX live-state instructions.

12. **`groundtruth-kb/templates/rules/canonical-terminology.md`** — live managed-rule template. Constraint: primer in GT-KB checkout is install of this template (extended for the dogfood case).

13. **`groundtruth-kb/templates/rules/canonical-terminology.toml`** — live profile-aware doctor config. Constraint: REVISED-2 ADDS new field `required_primer_terms` per profile (per Codex F1 option 1); preserves existing `required_startup_terms` semantics unchanged.

14. **`groundtruth-kb/templates/managed-artifacts.toml`** registry rows `rule.canonical-terminology` + `rule.canonical-terminology-config`. Constraint: REVISED-2 reuses these rows; no new registry surface.

15. **`groundtruth-kb/src/groundtruth_kb/project/doctor.py`** `_check_canonical_terminology()` — existing doctor check. Constraint per Codex F1: REVISED-2 EXTENDS this check to evaluate `required_primer_terms` against primer file content; preserves existing `required_startup_terms` evaluation against `required_files` content. Single check; two coverage contracts.

16. **`groundtruth-kb/tests/test_doctor_canonical_terminology.py`** — existing test surface (lines 49-219 cover profile matrix). Constraint: extended (not replaced) to cover dual-check semantics; existing tests preserved.

17. **`bridge/gtkb-canonical-terminology-surface-implementation-012.md`** (VERIFIED) — prior architecture decision establishing registry-backed Option B. Constraint: this proposal carries forward; does NOT propose alternative.

18. **`GOV-ARTIFACT-APPROVAL-001`** — formal-artifact approval contract. Constraint: Slice 1 changes to `templates/rules/canonical-terminology.{md,toml}` carry approval packet.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`. Relevant prior deliberations:

- **`DELIB-0722` / `DELIB-1180`** — prior `gtkb-canonical-terminology-surface-implementation` thread. **Preserved.** Builds on verified Option B architecture; does NOT propose alternative.
- **`DELIB-GTKB-IDP-TERMINOLOGY`** — owner decision that GT-KB is formally an Internal Developer Platform. **Preserved.** Primer entries align with IDP framing.
- **`DELIB-1138`, `DELIB-1016`, `DELIB-1017`, `DELIB-1018`, `DELIB-1019`** — prior bridge/review history for IDP terminology. **Preserved.** No reopening.
- **`DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE`** (this session, candidate; archival pending Slice 1) — directly motivates this proposal.

**Differentiation:** No prior deliberation already approves a 22-term primer at GT-KB-checkout level. Prior thread settled architecture; this proposal extends term coverage and dogfoods install for GT-KB itself.

## Problem Statement

§2 of `operating-model.md` is canonical and auto-loaded. The existing managed canonical-terminology surface is VERIFIED and scaffolds to adopter projects. But: (1) GT-KB checkout doesn't dogfood its own canonical-terminology surface; (2) `required_startup_terms` lists are short (3-5 terms per profile); owner-required minimum is 22; (3) smart-poller dispatch doesn't include primer reference; (4) empirical drift evidence — I cited wrong template paths in `-001.md` despite VERIFIED prior thread.

## Proposed Direction (REVISED-2)

Three concrete changes to existing infrastructure:

### Change 1 — Install primer for GT-KB checkout + add `required_primer_terms` field (Slice 1)

Create `.claude/rules/canonical-terminology.{md,toml}` in GT-KB checkout. The .toml ADDS a NEW field per profile (resolves F1 option 1):

```toml
# Excerpt — full file at templates/rules/canonical-terminology.toml + GT-KB extensions.

[config.profiles.dual-agent]
# UNCHANGED: existing semantic — these terms must appear in required_files content.
required_files = ["CLAUDE.md", "AGENTS.md", "MEMORY.md", ".claude/rules/deliberation-protocol.md"]
required_startup_terms = ["MemBase", "Deliberation Archive", "MEMORY.md", "Prime Builder", "Loyal Opposition"]
missing_severity = "ERROR"

# NEW (REVISED-2): per-profile primer-content coverage.
# These terms must appear in `.claude/rules/canonical-terminology.md` (the primer file).
required_primer_terms = [
    # Existing 5 startup terms (also required to appear in primer):
    "MemBase", "Deliberation Archive", "MEMORY.md", "Prime Builder", "Loyal Opposition",
    # New (per S327 owner directive — completing the 22-term minimum):
    "GT-KB", "GroundTruth-KB", "GTKB", "platform", "application", "hosted application",
    "Agent Red", "adopter", "project", "work item", "backlog", "specification",
    "requirement", "implementation proposal", "implementation report", "verification",
    "dashboard", "bridge"
]
primer_missing_severity = "ERROR"
primer_path = ".claude/rules/canonical-terminology.md"
```

The `required_startup_terms` set is intentionally minimal (terms required to appear in EVERY startup file like CLAUDE.md/AGENTS.md). The `required_primer_terms` set is the 22-term primer-content coverage. The two coverage contracts are independent: a term in `required_primer_terms` does NOT need to appear in CLAUDE.md unless it's also in `required_startup_terms`.

### Change 2 — Multi-source attribution per term (Slice 1, unchanged from REVISED-1)

Each primer entry declares its authoritative source:

| Source | Terms |
|---|---|
| `operating-model.md` §2 | application, project, platform, hosted application, work item, backlog, specification, requirement, implementation proposal, implementation report, verification, MemBase, Deliberation Archive, dashboard |
| `AGENTS.md` short glossary | bridge, Prime Builder, Loyal Opposition |
| Role rules (`prime-builder-role.md` + `loyal-opposition.md`) | Prime Builder, Loyal Opposition (role-detail definitions) |
| `DELIB-GTKB-IDP-TERMINOLOGY` + `CLAUDE.md` | GT-KB, GroundTruth-KB, GTKB, adopter |
| Application identity (`CLAUDE.md` § "Application Identity") | Agent Red |

### Change 3 — Smart-poller dispatch additive extension (Slice 3)

Per Codex `-002.md` non-blocking note 1: dispatch prompt extension is ADDITIVE. Adds primer reference (one paragraph + content hash) without removing existing role-record + INDEX live-state instructions. T8 fixture asserts BOTH new and existing references remain present.

### Change 4 — Doctor check extension (Slice 1, REVISED-2 explicit)

Existing `_check_canonical_terminology()` is extended to:
1. Continue evaluating `required_startup_terms` against `required_files` content (UNCHANGED behavior).
2. Additionally evaluate `required_primer_terms` against the file at `primer_path` (NEW behavior).
3. Both contracts emit at their own severity: `missing_severity` for startup, `primer_missing_severity` for primer.
4. The check is a single function with two coverage contracts; no parallel doctor check.

## Test Plan (REVISED-2)

| # | Test | Spec link | Asserts |
|---|---|---|---|
| T1 | `test_gt_kb_checkout_has_canonical_terminology_md_installed` | rule items 4 + 12 + 17 | `.claude/rules/canonical-terminology.md` exists in GT-KB checkout |
| T2 (REVISED-2) | `test_required_primer_terms_cover_22_owner_minimum` | owner directive + Codex F1 option 1 | Each profile in `.claude/rules/canonical-terminology.toml` has `required_primer_terms` covering all 22 owner-required terms; existing `required_startup_terms` unchanged from prior values |
| T3 | `test_primer_term_entries_cite_source` | rule item 1 + multi-source policy | Each term entry includes `**Source:**` citation pointing at one of the governed sources |
| T4 | `test_primer_format_per_term` | §"Change 2" multi-source | Each term entry has 3 required subsections (Canonical meaning / Allowed synonyms / Source) |
| T5 (REVISED-2) | `test_existing_doctor_check_extended_evaluates_both_contracts` | rule item 15 (Codex F1 option 1) | `gt project doctor` on GT-KB self: (a) reports OK on `required_startup_terms` against CLAUDE.md/AGENTS.md/MEMORY.md (existing semantics, unchanged); (b) reports OK on `required_primer_terms` against `.claude/rules/canonical-terminology.md` (new semantic) |
| T6 (REVISED-2) | `test_doctor_fails_when_primer_missing_a_required_term` | rule item 15 | Removing one term entry from primer file causes existing doctor to return ERROR with `primer_missing_severity` (not `missing_severity`) |
| T6b (REVISED-2) | `test_doctor_does_not_force_22_terms_into_startup_files` | Codex F1 (the failure mode being avoided) | Removing all 22 primer-only terms from CLAUDE.md (terms not in `required_startup_terms`) does NOT cause doctor failure; existing semantics preserved |
| T7 | `test_primer_term_entry_does_not_contradict_source` | rule item 1 | Doctor parses primer + cited source; semantic-match policy enforced |
| T8 | `test_smart_poller_dispatch_prompt_includes_primer_AND_preserves_existing` | rule item 11 | Fixture asserts BOTH primer reference + role-record + INDEX live-state instructions present |
| T9 | `test_agents_md_glossary_non_conflicting` | rule item 6 | AGENTS.md terms subset of primer; warning level |
| T10 | `test_regenerate_command_idempotent` | §"Change 2" | `gt term-primer regenerate` twice → byte-identical output |
| T11 (REVISED-2) | `test_existing_canonical_terminology_thread_preserved_under_extension` | rule item 17 | After REVISED-2 lands, ALL existing 15+ tests in `test_doctor_canonical_terminology.py` still pass (existing `required_startup_terms` semantics preserved); new tests T2/T5/T6/T6b cover the extension |
| T12 | `test_release_candidate_gate_runs_doctor` | rule item 9 | Release-candidate gate runs `gt project doctor` |
| T13 | `test_DELIB_S327_term_primer_directive_archived` | rule item 5 | After Slice 1 close, `DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE` archived |
| T14 | `test_GOV_ARTIFACT_APPROVAL_packet_admits_template_changes` | rule item 18 | Slice 1 template changes admitted by `formal-artifact-approval-gate.py` only when approval packet present |

## Acceptance Criteria

- `.claude/rules/canonical-terminology.{md,toml}` installed in GT-KB checkout.
- `required_primer_terms` field added per profile in TOML; covers all 22 owner-required terms.
- Existing `required_startup_terms` semantics preserved unchanged.
- `_check_canonical_terminology()` extended to evaluate both contracts; passes on GT-KB self for both.
- Smart-poller dispatch additive (T8).
- AGENTS.md non-conflicting subset.
- T1-T14 + T6b pass; existing 15+ canonical-terminology tests still pass (T11).
- IPR + CVR per `GOV-20`.
- Slice 1 template changes carry approval packet.
- `DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE` archived (T13).
- Ruff + lint clean.

## Risk and Rollback

- **Risk: extending TOML schema breaks existing doctor.** Mitigation: new field `required_primer_terms` is additive; missing-key default is empty list (no-op); existing-profile installs unaffected. T11 verifies no regression.
- **Risk: existing adopter projects lose terminology coverage when their `canonical-terminology.toml` is older.** Mitigation: `gt project upgrade` migrates the new field; old adopters get a doctor warning until upgrade.
- **Risk: doctor extension introduces bug in existing path.** Mitigation: existing 15+ tests run unmodified (T11); extension is additive code only.
- **Rollback:** revert `required_primer_terms` field + doctor extension + primer install. Existing semantics fully preserved.

## Sequencing

1. **Slice 1** — TOML schema extension + doctor extension + primer install + multi-source attribution + formal-artifact-approval packet. T1-T7 + T11 + T14.
2. **Slice 2** — `gt term-primer regenerate` thin wrapper. T10.
3. **Slice 3** — Smart-poller dispatch additive extension. T8.
4. **Slice 4** — AGENTS.md glossary reconciliation. T9.
5. **Slice 5** — Release-candidate gate. T12 + T13.

## Open Decisions

§B. **AGENTS.md fate.** (i) Pointer at primer, (ii) Verified subset retained, (iii) Generated from primer. Suggest (ii) — minimum disruption.
§C. **Regeneration cadence.** Auto-trigger via hook + owner-triggered. Suggest both.
§D. **Multi-source attribution policy file format.** Embed in `canonical-terminology.toml` `[sources]` section vs. separate file. Suggest single file.
§E. **`DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE` archival timing.** Slice 1 close.

## Out of Scope

- Implementation of Slices 1-5.
- Restructuring `operating-model.md` §2.
- Cross-application term primers.
- Auto-fixing terminology in existing artifacts.

## Spec-to-test mapping (summary)

- operating-model.md §2 → T3, T7
- operating-model.md §1 → T5
- file-bridge-protocol.md → all
- project-root-boundary.md → T1, T11
- deliberation-protocol.md → T13
- AGENTS.md → T9
- CLAUDE.md → T1, T11
- GOV-19-A1 → T2, T5
- GOV-20 → IPR/CVR
- DELIB-S312 → T10
- bridge/gtkb-bridge-poller-001-smart-poller-007.md → T8
- templates/rules/canonical-terminology.{md,toml} → T1, T2, T11
- templates/managed-artifacts.toml → T1, T11
- doctor.py `_check_canonical_terminology` → T5, T6, T6b, T11 (extension; existing semantics preserved)
- tests/test_doctor_canonical_terminology.py → T11
- gtkb-canonical-terminology-surface-implementation-012 → T11
- GOV-ARTIFACT-APPROVAL-001 → T14
- Owner directive (verbatim 22 terms) → T2

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
