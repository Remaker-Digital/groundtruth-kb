REVISED

# GTKB-GOV-TERM-DISAMBIGUATION-MECHANICAL — Scoping Proposal (REVISED-1)

Author: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Status: REVISED (responding to Codex NO-GO at `-002.md`)

## Revision Rationale (REVISED-1)

Codex NO-GO at `-002.md` issued 4 P1 findings, all Prime-fixable. All four root in shared errors with the primer proposal: wrong template paths and missed prior canonical-terminology thread.

- **F1** — Wrong canonical terminology config path (`templates/project/...` doesn't exist; live path is `templates/rules/...`) AND wrong schema (existing config is profile-aware `[config.profiles.*]`, not `[term."..."]`). Resolved by adopting the live path AND introducing a sibling policy file rather than redefining the existing schema.
- **F2** — Prior canonical-terminology bridge history omitted. Resolved with new Prior Deliberations section.
- **F3** — Dependency on the still-NO-GO term-primer sibling is not safe. Resolved by making this proposal self-contained: defines its own minimum term set, source path, and schema contract independent of primer state. Primer GO is *preferable* but not blocking.
- **F4** — Open implementation-critical decisions not pinned. Resolved by pinning §A through §G as proposal requirements with concrete defaults; remaining open items become genuinely-open vs. proposal-pinned.

**Material changes from `-001.md`:**

- All `templates/project/canonical-terminology.toml` references replaced with sibling policy file `groundtruth-kb/templates/rules/canonical-terminology-policy.toml` (composes with existing config; no schema collision).
- Prior Deliberations section added.
- Self-contained schema contract removes primer dependency.
- Open Decisions §A-§G pinned to defaults; pinned values become proposal requirements.

## Origin

Owner directive 2026-05-02 (S327, fourth turn) — full verbatim text at `bridge/gtkb-gov-term-disambiguation-mechanical-2026-05-02-001.md` §"Origin". Owner observed chronic vagueness in canonical-vs-common term use; requested structural mechanical fix that disambiguates specific artifact / class of artifact / procedure / general English.

Candidate Deliberation Archive entry: `DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE`.

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

1. **`.claude/rules/operating-model.md` §2** — canonical terminology with allowed synonyms and forbidden uses. Constraint: this proposal mechanically enforces the forbidden-use rules (e.g., "Forbidden: using 'backlog' as synonym for 'ignore list'") that §2 declares but does not enforce.

2. **`.claude/rules/file-bridge-protocol.md`** — bridge protocol mandatory linkage gate. Constraint: proposal compliance.

3. **`.claude/rules/project-root-boundary.md`** — all artifacts within `E:\GT-KB`. Constraint: policy file lands at `groundtruth-kb/templates/rules/canonical-terminology-policy.toml` and `.claude/rules/canonical-terminology-policy.toml`.

4. **`.claude/rules/deliberation-protocol.md`** — owner-directive archival; deliberation-search obligation. Constraint: this proposal includes Prior Deliberations.

5. **`GOV-ARTIFACT-APPROVAL-001`** — formal-artifact approval contract. Constraint: new policy file is a managed-rule template requiring formal approval; Slice 1 carries the packet.

6. **`GOV-19-A1`** — outside-in testing. Constraint: tests exercise hook public surface, not internal helpers.

7. **`GOV-20`** — architecture decisions; cross-cutting. Constraint: IPR/CVR per slice.

8. **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** — repetitive AI plumbing is a defect. Constraint: this proposal converts term-disambiguation from prompt-time recall to lint-time enforcement.

9. **`groundtruth-kb/templates/rules/canonical-terminology.toml`** *(corrected path per F1)* — existing profile-aware doctor config with `[config.profiles.*]` and `required_startup_terms`. Constraint: this proposal does NOT modify this file's schema; it composes with it via a sibling policy file (Change 1 below).

10. **`groundtruth-kb/templates/rules/canonical-terminology.md`** *(corrected path per F1)* — existing managed-rule glossary. Constraint: term entries here are the source-of-truth for which terms have policies; the new policy file declares enforcement metadata for each.

11. **`bridge/gtkb-canonical-terminology-surface-implementation-012.md`** (VERIFIED) *(per F2)* — prior architecture decision establishing registry-backed Option B contract under `templates/rules/`. Constraint: this proposal does not contradict; it extends with a sibling policy file using the same managed-rule pattern.

12. **`groundtruth-kb/templates/managed-artifacts.toml`** *(per F1)* — existing registry. Constraint: new policy file gets a new registry row `rule.canonical-terminology-policy` following the same pattern as the existing two terminology rows (`rule.canonical-terminology` and `rule.canonical-terminology-config`).

13. **`.claude/hooks/`** — existing hook infrastructure (formal-artifact-approval-gate, bridge-compliance-gate, etc.). Constraint: new lint hooks follow existing patterns; reuse `bridge-compliance-gate.py` for bridge-specific extension rather than creating a new bridge-targeted hook.

14. **`bridge/gtkb-bridge-poller-001-smart-poller-007.md`** — smart-poller dispatch. Constraint: lint must run on dispatch-spawned headless sessions; T10 verifies.

15. **`bridge/gtkb-gov-term-primer-startup-2026-05-02-003.md`** (sibling REVISED-1) — primer proposal (currently REVISED, not GO). Constraint: this proposal is **decoupled** per F3 — defines its own minimum term set independent of primer state. Primer GO is preferable but not blocking.

16. **`bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-005.md`** (sibling REVISED-2) — backlog proposal where "backlog" is the running case study. Constraint: this proposal's lint enforcement applies to canonical "Backlog" usage in subsequent backlog-program proposals.

## Prior Deliberations (per Codex F2)

Per `.claude/rules/deliberation-protocol.md`:

- **`DELIB-0722` / `DELIB-1180`** — prior `gtkb-canonical-terminology-surface-implementation` thread. **Preserved + extended.** This proposal does NOT contradict the verified Option B architecture; it extends with a sibling policy file using the same managed-rule pattern.
- **`DELIB-1179`, `DELIB-1018`, `DELIB-1017`, `DELIB-0804`** — earlier canonical-terminology bridge thread context. **Preserved.** No prior decision rejects per-term enforcement metadata; the existing schema simply doesn't have it.
- **`DELIB-S324-OM-DELTA-0004-CHOICE`** — backlog ordering semantics. **Preserved.** Not directly relevant to term disambiguation per se, but referenced because "ordering" is itself a candidate canonical-vs-common term.
- **`DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT`** — flags MemBase/backlog/bridge source fragmentation. **Built on.** Term disambiguation is one mechanical contributor to fragmentation prevention.
- **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** — supports converting AI recall/plumbing to deterministic services. **Built on.** This proposal is exactly such a conversion.
- **`DELIB-1404`** — candidate-vs-approved spec wording. **Preserved.** Not modified; that distinction is a separate semantic concern handled by `status` enums, not by lexical form.
- **`DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE`** + **`DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE`** + **`DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE`** (this session, candidates pending archival) — coupled motivations.

**Differentiation:** No prior deliberation already establishes per-term disambiguation policy + enforcement hook architecture. This proposal introduces new mechanism; it does NOT contradict the verified canonical-terminology thread — it extends it.

## Problem Statement (unchanged from -001.md, abridged)

§2 of `operating-model.md` defines forbidden uses (e.g., 'using "backlog" as synonym for "ignore list"') with no mechanical enforcement. Definitions exist; usage rules don't. Three failure modes need disambiguating: specific artifact / class / procedure / + general English. Empirical drift evidence in this S327 session: I conflated `work_items` and `backlog_items`; cited wrong paths in primer/disambiguation proposals despite existing VERIFIED architecture. Smart-poller spawns + bridge-protocol gap + forbidden-use violations all undetected.

## Proposed Direction (REVISED-1)

A 3-tier disambiguation policy declared in a sibling policy file `canonical-terminology-policy.toml`, enforced by a single PostToolUse lint hook + extension to the existing `bridge-compliance-gate.py` hook. **Self-contained:** minimum term set defined here independently of primer state.

### Change 1 — Sibling policy file (resolves F1)

`groundtruth-kb/templates/rules/canonical-terminology-policy.toml` (new managed-rule template, registered as `rule.canonical-terminology-policy` in `managed-artifacts.toml`):

```toml
# Canonical-terminology disambiguation policy. Composes with canonical-terminology.toml.
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

[meta]
version = "1.0.0"
# Source-of-truth term list: canonical-terminology.md (sibling glossary).
# This file declares per-term enforcement metadata.

[defaults]
# Pinned per Codex `-002.md` F4:
tier_b_severity_in_bridge_proposals = "error"        # block in bridge proposals
tier_b_severity_elsewhere = "warn"                    # warn in other writes
tier_c_strictness = "strict"                          # demonstrative + canonical word + no ID = flag
forbidden_uses_severity = "error"                     # always block
sentence_initial_capitalization = "ignore"            # ignore for Tier B detection
file_level_disable_marker = "<!-- term-disambiguation: off -->"
override_syntax = "{!common: <term>}"

[term."backlog"]
disambiguation_tier = "B"
specific_id_prefix = "BL"
override_alias = "{!common: backlog}"

[term."MemBase"]
disambiguation_tier = "A"
distinctive_form = "MemBase"

[term."GT-KB"]
disambiguation_tier = "A"
distinctive_form = "GT-KB"

# ... per-term entries for each canonical term in canonical-terminology.md
```

The 3-tier policy:
- **Tier A — Distinctive form:** unique lexical form (e.g., `MemBase`, `GT-KB`, `Deliberation Archive`, `Prime Builder`). Lint flags wrong-casing/wrong-hyphenation.
- **Tier B — Capitalization disambiguates:** common English homonym (e.g., `backlog` vs `Backlog`). Lint flags lowercase canonical-term in canonical contexts (severity per `[defaults]`).
- **Tier C — ID citation for instances:** specific instance reference must include canonical ID (e.g., `BL-0001`). Lint flags bare canonical-term + demonstrative + no nearby ID.

### Change 2 — Self-contained minimum term set (resolves F3)

This proposal's lint reads the term list from `canonical-terminology-policy.toml` itself. The minimum required terms (from S327 owner directive verbatim 22 terms) are declared in the policy file regardless of primer state. If the primer reaches GO, the same 22 terms exist in both surfaces (primer for definitions; policy for enforcement metadata) — no contradiction. If the primer remains REVISED, this proposal still ships with self-contained term coverage.

### Change 3 — Single lint hook + bridge-compliance-gate extension

Two enforcement surfaces:

**Hook 1 — `term-disambiguation-lint.py`** (new PostToolUse hook for Edit/Write):
- Loads `canonical-terminology-policy.toml`.
- Scans tool output content for canonical terms.
- Tier A: regex on distinctive form; flags misspellings.
- Tier B: regex + heuristic; flags lowercase-canonical-term in canonical contexts. Severity per `[defaults]` (warn elsewhere; error in bridges per Hook 2).
- Tier C: heuristic detecting "the X" + canonical term + no ID nearby.
- Honors override syntax `{!common: <term>}` and file-level `<!-- term-disambiguation: off -->`.

**Hook 2 — `bridge-compliance-gate.py` extension** (existing hook; add a check):
- When write target is a `bridge/*.md` file, escalate Tier B violations from warn to error.
- Existing bridge-compliance-gate already runs on bridge writes; adds the disambiguation check after the existing spec-linkage check.
- Reuses Hook 1's logic; differs only in severity escalation.

### Pinned defaults (resolves F4)

Per Codex F4, Open Decisions §A-§G in `-001.md` are pinned as proposal requirements:

- §A → Tier B severity: `warn` elsewhere; `error` in bridge proposals (middle option).
- §B → Override syntax: `{!common: <term>}`.
- §C → Tier C strictness: strict (any "the X" + canonical + no ID = flag).
- §D → Forbidden-use severity: `error` always (always block).
- §F → Sentence-initial capitalization: ignore for Tier B detection.
- §G → File-level disable: `<!-- term-disambiguation: off -->` marker.
- §E (backfill scope) → audit-only (Slice 6); no rewrites.

These pinned defaults are recorded in `[defaults]` of the policy file. Owner can change them via the standard formal-artifact-approval flow per `GOV-ARTIFACT-APPROVAL-001`.

## Test Plan (REVISED-1)

| # | Test | Spec link | Asserts |
|---|---|---|---|
| T1 | `test_canonical_terminology_policy_toml_exists_and_validates` | rule items 9 + 12 + Change 1 | New file at `groundtruth-kb/templates/rules/canonical-terminology-policy.toml`; registered as `rule.canonical-terminology-policy` in `managed-artifacts.toml`; `[defaults]` has all 7 pinned values; per-term entries cover the 22-term minimum |
| T2 | `test_term_lint_hook_registered_in_settings` | rule item 13 | `term-disambiguation-lint.py` registered as PostToolUse hook for Edit and Write |
| T3 | `test_tier_A_distinctive_form_flagged` | §"Tier A" | Edit producing `Membase` (wrong cap) flagged; `MemBase` (correct) passes |
| T4 | `test_tier_B_capitalization_canonical_context` | §"Tier B" + pinned default §A | Edit producing "the backlog has 27 items" inside a bridge proposal blocked (error); same content in non-bridge file warned (not blocked) |
| T5 | `test_tier_B_lowercase_general_context_passes` | §"Tier B" | Edit producing "we have a backlog of customer requests" in non-canonical context does not flag |
| T6 | `test_tier_C_bare_canonical_with_demonstrative_flagged` | §"Tier C" + pinned default §C | Edit producing "the spec we just landed" (specific reference, no ID) flagged; "the SPEC-1234 spec we just landed" passes |
| T7 | `test_override_syntax_suppresses_lint` | §"Override syntax" + pinned default §B | Edit using `{!common: backlog}` does not trigger lint even when content matches Tier B violation patterns |
| T8 | `test_bridge_compliance_gate_extended_blocks_on_tier_B_violation` | rule item 13 + Hook 2 | Bridge proposal with lowercase canonical term gets blocked; non-bridge writes with same content get warned |
| T9 | `test_forbidden_uses_explicitly_blocked` | rule item 1 (operating-model.md §2 forbidden_uses) + pinned default §D | Edit producing phrase matching a `forbidden_uses` entry blocked regardless of severity setting |
| T10 | `test_lint_runs_in_smart_poller_spawned_sessions` | rule item 14 | Headless dispatch-spawned session has the lint hook active |
| T11 | `test_existing_canonical_terminology_thread_preserved` | rule item 11 | After landing, the verified `gtkb-canonical-terminology-surface-implementation-012` evidence still resolves; existing `_check_canonical_terminology` doctor check unaffected |
| T12 | `test_existing_artifacts_not_retroactively_blocked` | §"Out of Scope" backfill | Pre-existing artifacts with Tier B violations remain untouched (grandfather); only NEW writes are gated |
| T13 | `test_release_candidate_gate_runs_disambiguation_audit_report` | rule item 7 | Release-candidate gate runs `gt term-disambiguation audit` and includes the report in release evidence |
| T14 | `test_DELIB_S327_term_disambiguation_directive_archived` | rule item 4 | After Slice 1 close, `DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE` archived per `GOV-ARTIFACT-APPROVAL-001` |
| T15 | `test_sentence_initial_capitalization_ignored` | pinned default §F | Sentence-initial "Backlog items must be reviewed." in non-canonical context does not flag (sentence-start cap is mandatory English; not a canonical-vs-common signal) |
| T16 | `test_file_level_disable_marker_works` | pinned default §G | File starting with `<!-- term-disambiguation: off -->` is exempt from lint |
| T17 | `test_self_contained_term_set_independent_of_primer_state` | Codex F3 + Change 2 | This proposal's lint operates correctly when primer is REVISED (i.e., not yet GO); term set declared in policy file, not derived from primer |

## Acceptance Criteria

- New policy file `templates/rules/canonical-terminology-policy.toml` created with 22-term minimum + pinned `[defaults]`.
- Registry row `rule.canonical-terminology-policy` added to `managed-artifacts.toml`.
- New lint hook `term-disambiguation-lint.py` registered + tested.
- `bridge-compliance-gate.py` extended for Tier B escalation.
- All 7 pinned defaults present and tested (T4, T6, T7, T9, T15, T16; §B implicit in T7).
- Override syntax + file-level disable working.
- Smart-poller dispatch sessions inherit the lint hook (T10).
- Existing canonical-terminology thread evidence intact (T11).
- T1-T17 pass.
- IPR + CVR per `GOV-20`.
- Slice 1 policy file change carries approval packet per `GOV-ARTIFACT-APPROVAL-001`.
- `DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE` archived (T14).
- Ruff + lint clean.

## Risk and Rollback

- **Risk: lint produces too much noise.** Mitigation: severity-tunable per term in `[defaults]`; default warn elsewhere; backfill audit (Slice 6) reports drift volume.
- **Risk: false positives in non-canonical contexts.** Mitigation: hook discriminates by file path. Tier B lint runs only on canonical-context writes by default.
- **Risk: override syntax becomes graffiti.** Mitigation: usage tracked; doctor check reports density.
- **Risk: capitalization conflicts with sentence-start cap.** Mitigation: T15 pinned default §F.
- **Risk: smart-poller doesn't inherit hook.** Mitigation: T10 fixture-based assertion.
- **Risk: backward-incompatibility.** Mitigation: T12 grandfather clause.
- **Rollback:** revert hook registrations + policy file + registry row + bridge-compliance-gate change. Existing canonical-terminology surface unchanged.

## Sequencing

1. **Slice 1 — Policy file + schema.** New `canonical-terminology-policy.toml` with 22-term minimum + pinned defaults; registry row; formal-artifact-approval packet. T1.
2. **Slice 2 — Lint hook (warn-only mode).** `term-disambiguation-lint.py`; PostToolUse Edit/Write; default warn. T2-T7 + T15-T16.
3. **Slice 3 — Bridge-compliance-gate extension.** Tier B escalation in bridge proposals. T8 + T9.
4. **Slice 4 — Smart-poller dispatch integration.** Hook in dispatch sessions. T10. Composes with primer Slice 3 (when primer GO lands).
5. **Slice 5 — Backfill audit + release-gate.** `gt term-disambiguation audit` reports existing-artifact drift; release-gate runs the audit. T12 + T13.
6. **Slice 6 — Doctor check + audit reporting.** Doctor verifies policy completeness; audit reports filed. T14 + T17.

## Open Decisions (REVISED-1: significantly trimmed; defaults pinned)

§A through §G are PINNED in `[defaults]` per F4. Owner can change via formal-artifact-approval flow.

Genuinely-open (require owner direction if Prime can't pin):

§H. **Smart-poller dispatch composition with primer.** When primer Slice 3 dispatch extension lands AND this proposal Slice 4 lands: the dispatch prompt grows. Configurable content-hash references vs full inclusion. Suggest: full inclusion at <2KB total; content-hash references beyond. Token-budget-driven default.

§I. **`gt term-disambiguation` CLI command surface.** `audit` is required (Slice 5). Other commands (`show <term>`, `policy <term>`, `validate`)? Suggest minimal: `audit` + `validate` only.

## Out of Scope

- Implementation of Slices 1-6.
- Backfill rewrites (audit-only per pinned default §E).
- Cross-language disambiguation.
- Voice/audio surfaces.
- The term primer itself — sibling proposal `GTKB-GOV-TERM-PRIMER-STARTUP`.
- Modifying existing `canonical-terminology.toml` schema (this proposal introduces a sibling, not a modification).

## Spec-to-test mapping (summary)

- operating-model.md §2 → T9 (forbidden-uses enforcement)
- file-bridge-protocol.md → T8 (bridge-compliance-gate extension)
- project-root-boundary.md → T1 (in-root paths)
- deliberation-protocol.md → T14 (DELIB archival), Prior Deliberations satisfies search obligation
- GOV-ARTIFACT-APPROVAL-001 → T14
- GOV-19-A1 → T2, T8 (outside-in via hook public surface)
- GOV-20 → IPR/CVR per slice
- DELIB-S312 → T13
- canonical-terminology.toml → T11 (preserved unchanged)
- canonical-terminology.md → T1 (term list source)
- gtkb-canonical-terminology-surface-implementation-012 → T11
- managed-artifacts.toml → T1 (new registry row)
- .claude/hooks/ → T2, T8, T10
- gtkb-bridge-poller-001-smart-poller-007 → T10
- primer sibling proposal → T17 (decoupling verified)
- backlog sibling proposal → T4, T6 (case study)
- Owner directive (verbatim) → T1 (tier coverage), T3-T7 + T15-T16 (mechanical enforcement)

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
