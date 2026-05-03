NEW

# GTKB-GOV-TERM-PRIMER-STARTUP — Scoping Proposal

Author: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Status: NEW (scoping; owner-directed)
Sibling to: `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-*.md` (separate scope per owner architectural call; not folded in)

## Origin

Owner directive 2026-05-02 (S327, third turn), verbatim:

> No, I'm not fully confident today.
>
> The terms are defined, but the loading path is too indirect. AGENTS.md has a short glossary, and .claude/rules/operating-model.md §2 has a good canonical terminology section. But startup does not consistently force a compact glossary into every agent's immediate working context, especially spawned/smart-poller sessions. That means an agent can know the words in a general English sense and still miss the GT-KB-specific meanings.
>
> Yes: we should load a glossary at session start.
>
> Recommended shape:
>
> - Create a short canonical GTKB-TERM-PRIMER.md or equivalent generated startup primer.
> - Source it from .claude/rules/operating-model.md §2.
> - Keep it compact: term, canonical meaning, allowed synonyms, forbidden/confusing uses.
> - Load it for both Prime Builder and Loyal Opposition startup.
> - Include it in smart-poller dispatch prompts, because headless spawned sessions are where drift is most likely.
> - Add a doctor/startup check that fails or warns if the active startup bundle omits the term primer.
>
> The minimum glossary should cover: GT-KB, GroundTruth-KB, GTKB, platform, application, hosted application, Agent Red, adopter, project, work item, backlog, specification, requirement, implementation proposal, implementation report, verification, MemBase, Deliberation Archive, dashboard, bridge, Prime Builder, and Loyal Opposition.
>
> This should probably be folded into GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH or tracked as a sibling item: GTKB-GOV-TERM-PRIMER-STARTUP. The goal is not more prose. The goal is to make term meaning deterministic at the moment an agent starts work.

This directive is a candidate Deliberation Archive entry: `DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE` (`source_type=owner_conversation`, `outcome=owner_decision`). Recording deferred to follow-on per `GOV-ARTIFACT-APPROVAL-001`.

**Architectural decision (Prime, justified):** **sibling**, not folded into `GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH`. The term primer's surfaces (generated MD file + startup loader + smart-poller dispatch prompt extension + doctor check) are operationally orthogonal to the backlog DB schema. Folding would inflate the backlog proposal's scope and couple two unrelated cutover paths.

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

1. **`.claude/rules/operating-model.md` §2** — source of canonical terminology that the primer extracts/summarizes. Primer must remain consistent with §2; §2 remains authoritative.
2. **`.claude/rules/operating-model.md` §1** — operating model framing for what an agent needs to know at session start.
3. **`.claude/rules/file-bridge-protocol.md`** — bridge protocol mandatory linkage gate.
4. **`.claude/rules/project-root-boundary.md`** — primer file lives within `E:\GT-KB`.
5. **`.claude/rules/deliberation-protocol.md`** — owner-directive archival obligation.
6. **`AGENTS.md`** — currently has a short glossary (per owner directive); primer either replaces or sources from that glossary.
7. **`CLAUDE.md` § "Working with This Project"** — current session-start rules; primer integrates here.
8. **`GOV-19-A1`** — outside-in testing (primer existence + content tested via public discovery, not internal helpers).
9. **`GOV-20`** — architecture decisions; this is a cross-cutting governance change, requires IPR/CVR.
10. **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** — primer load is deterministic plumbing (not AI-mediated terminology recall) and aligns with the principle.
11. **`bridge/gtkb-bridge-poller-001-smart-poller-007.md`** (umbrella) — smart-poller spawn dispatch is the highest-drift surface per owner directive; primer must be wired into dispatch prompts.
12. **`groundtruth-kb/templates/project/canonical-terminology.md`** — scaffolded canonical-terminology rule for adopter projects (much richer than §2). Reference for primer structure; reuse content where applicable.
13. **`groundtruth-kb/templates/project/canonical-terminology.toml`** — scaffolded TOML defining required-terms matrix for the doctor check; same pattern reused for the primer doctor check.

## Problem Statement

§2 of `operating-model.md` is canonical and auto-loaded as part of `.claude/rules/*.md`. But:

1. **Buried-in-rule-file effect.** §2 is one section of a longer rule file. Agents loading rule files have weaker pull toward §2 specifically than they would toward a dedicated `canonical-terminology.md` file with that exact name.
2. **Inconsistent across surfaces.**
   - `AGENTS.md` has its own short glossary.
   - `operating-model.md` §2 is more comprehensive but uses a different format.
   - The scaffolded `canonical-terminology.md` for adopter projects is richer than both.
   - GT-KB itself does NOT have `.claude/rules/canonical-terminology.md` — that file exists only as a template for adopter projects.
3. **Spawned/headless sessions worst-case.** Smart-poller dispatch prompts do not currently include §2 verbatim. Headless Codex/Prime spawns reconstruct terminology from scratch from rule files. This is the highest drift surface per owner observation.
4. **Term coverage gaps.** §2 covers ~13 terms; the owner-required minimum is ~22. Missing: GTKB (non-canonical alias), GroundTruth-KB (canonical hyphenated form), Agent Red (application instance), adopter (downstream consumer of GT-KB), bridge (file-bridge protocol surface), Prime Builder + Loyal Opposition (role names).
5. **Empirical drift evidence.** Even within this S327 session, I (Prime Builder) initially conflated `work_items` and `backlog_items` in the early backlog proposal draft; only the §"Authority Model" section in REVISED-1 made the distinction explicit. That's drift on a term I "knew" was loaded.

## Proposed Direction

A new compact, dedicated **term primer file** loaded explicitly at session start for both Prime Builder and Loyal Opposition harnesses, included in smart-poller dispatch prompts, with a doctor check enforcing presence and content currency.

### Primer file location and format

**Path:** `.claude/rules/canonical-terminology.md` (matches the scaffolded adopter pattern; extends it for GT-KB itself).

**Format:** compact term entries, one per term:

```markdown
### <Term>

**Canonical meaning:** <one sentence>
**Allowed synonyms:** <comma-separated, if any>
**Forbidden/confusing uses:** <e.g., "do not use 'X' to mean 'Y'">
**Source:** `.claude/rules/operating-model.md §2 <Term>` (authoritative)
```

Compact target: <150 LOC for the minimum 22-term coverage. The primer is an entry point and pointer; §2 remains authoritative for full definitions.

### Minimum glossary contents (owner-required)

22 terms verbatim from owner directive:

```
GT-KB, GroundTruth-KB, GTKB, platform, application, hosted application,
Agent Red, adopter, project, work item, backlog, specification, requirement,
implementation proposal, implementation report, verification, MemBase,
Deliberation Archive, dashboard, bridge, Prime Builder, Loyal Opposition
```

Term groupings (for primer organization):
- **Product identifiers** (4): GroundTruth-KB, GT-KB, GTKB, platform
- **Lifecycle entities** (4): application, hosted application, Agent Red, adopter, project
- **Work artifacts** (5): work item, backlog, specification, requirement, dashboard
- **Bridge artifacts** (3): bridge, implementation proposal, implementation report
- **Stores** (3): MemBase, Deliberation Archive, verification
- **Roles** (2): Prime Builder, Loyal Opposition

### Loading path

1. **Auto-load via `.claude/rules/*.md` convention.** Already in place; the primer file lands in that directory.
2. **Explicit reference in `CLAUDE.md` Session Start section.** Add a one-line directive: "Read `.claude/rules/canonical-terminology.md` at session start before applying any term-sensitive rule."
3. **Smart-poller dispatch prompt extension.** When the smart poller spawns a headless Prime/Codex session, the dispatch prompt embeds the primer verbatim (or a stable file reference + content hash). Modification to `groundtruth-kb/scripts/bridge_poller_runner.py` (already cited in row 22 of work_list).
4. **Codex harness (AGENTS.md).** Existing AGENTS.md short glossary either supersedes its content with a pointer to the primer, or is verified as a synonym-equivalent subset. Doctor check enforces consistency.
5. **Doctor check.** New `_check_canonical_terminology_primer` in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`:
   - Verifies primer file exists at `.claude/rules/canonical-terminology.md`.
   - Verifies primer covers all 22 owner-required terms (parses headers; matches against required-terms matrix in `canonical-terminology.toml`).
   - Verifies §2 of `operating-model.md` is the cited source for each term.
   - Verifies AGENTS.md glossary (if present) is a non-conflicting subset.
   - Status: `error` if primer missing or incomplete; `warning` on subset mismatches.

### CLI surface

```
gt term-primer show <term>           # Display the primer entry for a single term
gt term-primer list                  # List all primer terms
gt term-primer validate              # Run the doctor check
gt term-primer regenerate            # Regenerate primer from operating-model.md §2 (one-shot tool for governance evolution)
```

### Smart-poller integration

The smart-poller dispatch prompt currently references `bridge/INDEX.md`, the role record, and the actionable bridge file. The new contract:

```
DISPATCH PROMPT EXTENSION:
  Before processing the actionable bridge entry, read
  .claude/rules/canonical-terminology.md and use those definitions for any
  GT-KB-specific term in this session. Conflicts between general English
  meaning and the primer's canonical meaning resolve to the primer.
```

Implementation: extend the dispatch-prompt template in `groundtruth-kb/scripts/bridge_poller_runner.py` to include the primer reference and (configurable) primer content hash for staleness detection.

## Test Plan

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification-Derived Verification Gate, tests derive from the linked specs:

| # | Test | Spec link | Asserts |
|---|---|---|---|
| T1 | `test_canonical_terminology_primer_exists` | this proposal §"Loading path" | Primer file exists at `.claude/rules/canonical-terminology.md` |
| T2 | `test_primer_covers_minimum_required_terms` | owner directive (verbatim 22 terms) | Primer headers (`### <Term>`) cover all 22 owner-required terms exactly |
| T3 | `test_primer_cites_operating_model_section_2` | rule item 1 (§2 source) | Each term entry cites `.claude/rules/operating-model.md §2 <Term>` as authoritative source |
| T4 | `test_primer_format_per_term` | this proposal §"Format" | Each term entry has the four required subsections (Canonical meaning / Allowed synonyms / Forbidden uses / Source) |
| T5 | `test_doctor_check_fails_when_primer_missing` | this proposal §"Doctor check" | `_check_canonical_terminology_primer` returns `error` status when primer file is renamed or absent |
| T6 | `test_doctor_check_warns_on_term_coverage_gap` | this proposal §"Doctor check" | If a primer entry is removed for a required term, doctor returns `warning` (or `error` per Open Decision §A) |
| T7 | `test_primer_consistent_with_operating_model_section_2` | rule item 1 | Doctor check parses both files and asserts primer's "Canonical meaning" lines do not contradict §2's authoritative definitions |
| T8 | `test_smart_poller_dispatch_prompt_includes_primer` | this proposal §"Smart-poller integration" | The dispatch-prompt template emitted by `bridge_poller_runner.py` contains the primer reference (via fixture-based assertion) |
| T9 | `test_agents_md_glossary_non_conflicting` | rule item 6 (AGENTS.md) | If AGENTS.md has a glossary, doctor verifies its terms are a non-conflicting subset of primer (warning level, since AGENTS.md is Codex-side and may evolve independently) |
| T10 | `test_regenerate_command_produces_idempotent_output` | this proposal §"CLI surface" `regenerate` | `gt term-primer regenerate` twice in succession produces byte-identical output (idempotent generation) |
| T11 | `test_regression_no_existing_terminology_loss` | rule items 1, 12, 13 | After primer lands, all terms currently in §2 + scaffolded `canonical-terminology.md` (template) are present in primer; nothing dropped |
| T12 | `test_release_candidate_gate_includes_primer_check` | rule item 9 (GOV-20) | The release-candidate gate runs `gt term-primer validate` before passing |

## Acceptance Criteria

- Primer file `.claude/rules/canonical-terminology.md` exists with all 22 owner-required terms in the specified format.
- Doctor check `_check_canonical_terminology_primer` registered and passes.
- Smart-poller dispatch prompts include primer reference (verified by T8).
- AGENTS.md glossary either updated to point at primer or verified non-conflicting subset.
- `gt term-primer ...` CLI commands implemented per §"CLI surface".
- T1-T12 pass.
- Release-candidate gate runs `gt term-primer validate`.
- IPR + CVR documents per `GOV-20`.
- `DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE` archived.
- Ruff + lint clean on all touched files.

## Risk and Rollback

- **Risk: primer drifts from §2.** Mitigation: T7 doctor check enforces non-contradiction; CI runs the check; `regenerate` command produces primer from §2 deterministically.
- **Risk: §2 evolves and primer regeneration is forgotten.** Mitigation: doctor check + content-hash detection in smart-poller dispatch flags staleness.
- **Risk: smart-poller dispatch prompt size grows materially.** Mitigation: primer is compact (<150 LOC target); content-hash reference allowed when full inclusion is too large.
- **Risk: AGENTS.md glossary diverges intentionally for Codex-specific reasons.** Mitigation: doctor check is `warning` for AGENTS.md mismatches (Open Decision §B), allowing intentional Codex-side extensions while flagging unintentional drift.
- **Rollback:** revert primer file, doctor-check registration, and smart-poller dispatch extension. §2 remains authoritative as before; loss is the dedicated primer surface.

## Sequencing (proposed slices)

1. **Slice 1 — Primer file + doctor check.** Generate `.claude/rules/canonical-terminology.md` from §2; implement `_check_canonical_terminology_primer`; T1-T7 + T11. Ships standalone.
2. **Slice 2 — CLI commands.** `gt term-primer show/list/validate/regenerate`. T10.
3. **Slice 3 — Smart-poller dispatch integration.** Extend dispatch-prompt template; verify via fixture. T8.
4. **Slice 4 — AGENTS.md glossary reconciliation.** Update AGENTS.md to point at primer or document its intentional subset. T9.
5. **Slice 5 — Release-candidate gate integration.** Add `gt term-primer validate` to the gate. T12.

## Open Decisions

§A. **Doctor check severity for term-coverage gap.** `warning` (allows operation; flags drift) or `error` (blocks)? Suggest: `error` for owner-required minimum 22; `warning` for additions beyond.

§B. **AGENTS.md glossary fate.** (i) Reduce to a pointer at the primer, (ii) Verify subset and keep current content for Codex-specific framing, (iii) Generate AGENTS.md glossary from primer (deterministic). Suggest (iii) — symmetry with `gt term-primer regenerate`.

§C. **Primer regeneration cadence.** On every §2 edit (auto-trigger via hook), or owner-triggered (`gt term-primer regenerate` manually), or both? Suggest both, with the hook as defense-in-depth.

§D. **Inclusion of scaffolded `canonical-terminology.md` content.** The scaffolded template (linked spec item 12) is richer than §2. Should the GT-KB primer source from §2 only, or merge with the scaffolded template content? Suggest: source from §2 (authoritative); cite the scaffolded template as a downstream consumer that must stay synchronized.

§E. **`DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE` archival timing.** Same pattern as backlog directive: archive at Slice 1 close per `GOV-ARTIFACT-APPROVAL-001`.

## Out of scope (this proposal)

- Implementation of Slices 1-5 (each lands its own bridge with code + tests).
- Restructuring §2 itself. The primer is an extracted, compact mirror; §2 remains the authoritative source and is unchanged by this proposal.
- Cross-application term primers. If Agent Red or other adopters want their own primer with application-specific extensions, that's a per-application slice; the GT-KB primer is the framework version.
- Auto-fixing terminology in existing artifacts. Drift in old artifacts is preserved as historical evidence; only NEW writes are gated.

## Spec-to-test mapping (summary)

- `.claude/rules/operating-model.md` §2 → T3, T7, T11 (source authority preserved)
- `.claude/rules/operating-model.md` §1 → T1 (loading at session start)
- `.claude/rules/file-bridge-protocol.md` → all (proposal compliance with linkage gate)
- `.claude/rules/project-root-boundary.md` → all (in-root path)
- `.claude/rules/deliberation-protocol.md` → archival of S327 directive (Slice 1 close)
- `AGENTS.md` → T9 (glossary non-conflict)
- `CLAUDE.md` § "Working with This Project" → T1 (session-start integration)
- `GOV-19-A1` → T1, T2, T8 (outside-in via doctor + dispatch surfaces)
- `GOV-20` → IPR/CVR per slice
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` → T10 (regeneration is deterministic)
- `bridge/gtkb-bridge-poller-001-smart-poller-007.md` → T8 (dispatch integration)
- Scaffolded `canonical-terminology.md` template → T11 (no terminology loss in regeneration)
- Owner directive (verbatim 22 terms) → T2 (coverage), T6 (gap detection)

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
