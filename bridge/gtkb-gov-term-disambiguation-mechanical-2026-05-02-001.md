NEW

# GTKB-GOV-TERM-DISAMBIGUATION-MECHANICAL — Scoping Proposal

Author: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Status: NEW (scoping; owner-directed)
Sibling to: `bridge/gtkb-gov-term-primer-startup-2026-05-02-001.md` (provides definitions); `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-*.md` (case-study term: "backlog")

## Origin

Owner directive 2026-05-02 (S327, fourth turn), verbatim:

> Please proceed with proposing a structural, mechanical fix for this chronically vague and inconsistent use of terms. It is essential that every agent session be able to discern between a words common-use meaning and its use in a session as a reference to a specific artifact, class of artifact or procedure. We try to keep our usage of terms aligned with the general-use language, in terms of broad meaning and intent, but some terms - "backlog" is a prime example - are referring to an explicit artifact in the context of an explicit process (or set of related processes). The nuance is critical.

Candidate Deliberation Archive entry: `DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE` (`source_type=owner_conversation`, `outcome=owner_decision`).

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

1. **`.claude/rules/operating-model.md` §2** — canonical terminology source; defines forbidden uses for several terms (e.g., "Forbidden: using 'backlog' as a synonym for 'ignore list'"). This proposal mechanically enforces those forbidden-use rules.
2. **`.claude/rules/file-bridge-protocol.md`** — bridge protocol mandatory linkage gate.
3. **`.claude/rules/project-root-boundary.md`** — all artifacts within `E:\GT-KB`.
4. **`.claude/rules/deliberation-protocol.md`** — owner-directive archival; deliberation-search obligation before proposing.
5. **`GOV-ARTIFACT-APPROVAL-001`** — formal-approval contract; relevant because the proposed `canonical-terminology.toml` schema extension is a formal artifact requiring owner approval.
6. **`GOV-19-A1`** — outside-in testing.
7. **`GOV-20`** — architecture decisions; this is cross-cutting governance, requires IPR/CVR.
8. **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** — repetitive AI plumbing is a defect; term disambiguation is exactly such plumbing when done by-prompt instead of by-rule. This proposal converts disambiguation from prompt-time to lint-time.
9. **`bridge/gtkb-gov-term-primer-startup-2026-05-02-001.md`** — the primer (sibling proposal) provides definitions; this proposal provides usage enforcement. Tightly coupled but separable.
10. **`bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-003.md`** — the backlog proposal is the running case study. Both this proposal and the backlog proposal touch the term "backlog"; this proposal disambiguates its uses.
11. **`groundtruth-kb/templates/project/canonical-terminology.toml`** (scaffolded) — existing pattern for required-terms matrix; extended in Slice 1 with usage-tier metadata.
12. **`.claude/hooks/`** — existing hook infrastructure (formal-artifact-approval-gate, bridge-compliance-gate, etc.); this proposal adds two new hooks following existing patterns.
13. **`bridge/gtkb-bridge-poller-001-smart-poller-007.md`** — smart-poller dispatch; lint must run on dispatch-spawned sessions, not just interactive ones.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md` lines 13-17, deliberation search ran before this proposal. Relevant prior deliberations:

- **`DELIB-0838`** (standing backlog as governed cross-session work authority) — establishes that "backlog" has a canonical artifact sense in GT-KB. This proposal preserves DELIB-0838's authority semantics and adds mechanical enforcement of correct-vs-incorrect uses of the word.
- **`DELIB-0839`** (standing backlog harvest snapshot and reconciliation) — touches on usage of "backlog" across snapshot/dashboard/markdown surfaces, which is a fragmentation surface this proposal addresses (via consistent canonical-vs-common rules across all writing surfaces).
- **`DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT`** — flags "MemBase/backlog/bridge source fragmentation" as a primary effectiveness gap. Term disambiguation is one mechanical contributor to fragmentation prevention.
- **`DELIB-S324-OM-DELTA-0004-CHOICE`** (backlog ordering semantics) — establishes that backlog ordering has specific GT-KB-canonical semantics distinct from general English "ordering"; this proposal makes that distinction visible at write-time.
- **`DELIB-1404`** (candidate specification statements as backlog-advisory material) — hinges on the distinction between "candidate" and "approved" specifications, which is itself a term-disambiguation surface this proposal generalizes.
- **`DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE`** (this session, prior turn) — directly motivates why "backlog" needs disambiguation mechanism; the backlog formalization will create a `backlog_items` artifact class that must be distinguished from general-English "backlog" prose.
- **`DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE`** (this session, prior turn) — provides the definitions this proposal enforces. Tight coupling: the primer and the disambiguation mechanism ship together.

How this proposal differs from / builds on prior decisions:

- **Builds on** DELIB-0838, DELIB-0839, DELIB-S324-OM-DELTA-0004-CHOICE: takes their canonical-term commitments and operationalizes them in lint hooks.
- **Builds on** DELIB-S319 fragmentation finding: term-fragmentation is one of several surfaces; this proposal closes one specific drift class.
- **Coupled with** DELIB-S327-TERM-PRIMER-STARTUP: primer is necessary input; this proposal is enforcement.
- **Does NOT supersede** DELIB-1404: this proposal handles disambiguation; the candidate-vs-approved spec distinction is a separate semantic concern handled by `status` enums, not by lexical form.

## Problem Statement

§2 of `operating-model.md` defines canonical terms with allowed synonyms and forbidden uses. But:

1. **Definitions exist; usage rules don't.** §2 gives definitions but doesn't define when an agent must qualify a term to disambiguate canonical-vs-common. "Update the backlog" could mean (a) add to memory/work_list.md, (b) add to the future `backlog_items` table, (c) add to a session-local todo, (d) the general English concept of pending work.
2. **Empirical drift evidence in this very session.** Prime Builder (me) initially conflated `work_items` and `backlog_items` in the early backlog proposal draft. The §"Authority Model" section in REVISED-1 finally made the distinction explicit. That conflation happened despite §2 being loaded at session start. Proof that definitions alone are insufficient.
3. **Smart-poller spawn drift.** Headless dispatch sessions reconstruct usage rules from scratch. Even with the term primer (sibling proposal), there's no mechanism that catches usage errors at write-time — an agent can read the primer correctly and still write ambiguous prose.
4. **Bridge-protocol gap.** `Specification Links` requirement enforces ID citation for specifications cited as governing. But canonical-term USES in proposal body prose are not gated.
5. **Three failure modes to disambiguate, not one.** A single canonical word can refer to:
   - A specific artifact instance (e.g., "BL-0027 backlog item")
   - A class of artifact (e.g., "backlog items" as a type)
   - A procedure (e.g., "backlog review process")
   - Plus the general English sense
   Different mechanisms suit different modes.
6. **Forbidden-use violations go undetected.** `operating-model.md` §2 lists forbidden uses (e.g., 'using "backlog" as a synonym for "ignore list"') with no mechanical enforcement. The forbidden-use rules are aspirational rather than enforced.

## Proposed Direction

A three-tier disambiguation policy declared in canonical-terminology.toml, enforced by two new hooks (write-time lint + bridge-time gate), with owner-tunable severity per term and explicit override syntax for intentional common-use.

### The 3-tier disambiguation policy

Each canonical term in canonical-terminology.toml declares one of three tiers:

**Tier A — Distinctive form:** the canonical term has a unique lexical form that is unambiguous (multi-word, hyphenated, or mid-word capitalization). Examples: `MemBase`, `GT-KB`, `Deliberation Archive`, `Prime Builder`, `Loyal Opposition`, `groundtruth.toml`.

- **Rule:** the exact distinctive form (case-sensitive, hyphenation-sensitive) must be used when referring to the canonical concept.
- **Common-English alternative:** typically the canonical term has no common-English homograph; use a different word for the general concept (e.g., "knowledge base" for the general concept; `MemBase` for the GT-KB store).
- **Lint:** flag misspellings, wrong capitalization, or wrong hyphenation (e.g., `MemBase` vs `Membase`, `GT-KB` vs `GT KB`, `Prime Builder` vs `prime builder` when referring to the role).

**Tier B — Capitalization disambiguates:** the canonical term is a common English word with both senses in active use. Examples: `backlog`, `specification`, `review`, `verification`, `application`, `dashboard`, `bridge`.

- **Rule:** Capitalize the term (Title Case for single words, e.g., "Backlog"; canonical multi-word phrasing for longer terms, e.g., "Implementation Proposal") when referring to the canonical concept; use lowercase for general English use.
- **Examples:**
  - "Update the Backlog" — canonical sense (the standing backlog authority).
  - "we have a backlog of customer requests" — general sense.
  - "file an Implementation Proposal" — canonical (bridge artifact).
  - "the proposal needs work" — general (or specific via Tier C below).
- **Lint:** flag lowercase canonical-term use in contexts that are clearly canonical (e.g., bridge proposals, KB writes, ADR/DCL/SPEC documents). Owner-tunable severity (per Open Decision §A).

**Tier C — ID citation for specific instances:** when referring to a specific artifact instance, the canonical ID must accompany the term. Examples: `SPEC-1234`, `BL-0001`, `DELIB-NNNN`, `WI-NNNN`.

- **Rule:** specific-instance references must include the canonical ID. The canonical word can accompany the ID for readability (Tier B rule still applies to the word).
- **Examples:**
  - "Backlog item BL-0001" — Tier B Backlog + Tier C BL-0001.
  - "the BL-0001 row" — Tier C alone is sufficient.
  - "the spec we discussed" — fails Tier C if the speaker intended a specific spec; OK if the general concept.
- **Lint:** flag bare canonical-term uses in contexts where a specific instance is clearly being referenced (heuristic: presence of demonstratives "the", "this", "that" + canonical term + no ID nearby).

### Override syntax for intentional common-use

When an agent intentionally uses a canonical term in its general-English sense within a context that would otherwise trigger lint, an explicit override marker suppresses the lint:

```
{!common: backlog}        — explicit common-use marker
{!common: review}
```

Or HTML-comment marker for prose-heavy contexts:

```
<!-- canonical:common --> backlog <!-- /canonical -->
```

Or simpler: prefix with `~` (tilde):

```
~backlog (general sense)
```

Open Decision §B picks the syntax.

### Mechanical enforcement components

Two new hooks following existing patterns:

**Hook 1 — `term-disambiguation-lint.py` (PostToolUse, Edit/Write).**
- Scans Edit/Write tool outputs for canonical terms per the policy file.
- Tier A: regex-based detection of canonical lexical forms; flags incorrect spellings/casings/hyphenations.
- Tier B: regex + heuristic; flag lowercase canonical-term use in canonical contexts (bridge proposals, KB writes, formal artifacts). Defer to owner severity per Open Decision §A.
- Tier C: heuristic; flag bare canonical terms with demonstratives but no ID citation nearby (within configurable token window).
- Output: warnings (default) or blocks (severity=high).
- Honor override syntax (Open Decision §B).

**Hook 2 — `bridge-term-disambiguation-gate.py` (extension to existing `bridge-compliance-gate.py`).**
- Runs only on bridge proposal writes.
- Stricter than the general lint: blocks (rather than warns) on Tier B violations within bridge proposal bodies.
- Honors override syntax.
- Reports violations by line number for actionable revision.

**Schema extension to canonical-terminology.toml:**

```toml
[term."backlog"]
canonical_meaning = "The ordered set of active and candidate work for an application or platform."
allowed_synonyms = ["work_list", "the work list", "standing backlog"]
forbidden_uses = ["ignore list", "deprecated"]
disambiguation_tier = "B"   # capitalization disambiguates
specific_id_prefix = "BL"   # for Tier C citation
severity = "warn"            # owner-tunable per term

[term."MemBase"]
canonical_meaning = "The authoritative append-only/versioned knowledge database for governed records."
allowed_synonyms = ["Knowledge Database", "KB", "groundtruth.db"]
forbidden_uses = ["ChromaDB", "memory/MEMORY.md"]
disambiguation_tier = "A"
distinctive_form = "MemBase"
specific_id_prefix = ""      # MemBase itself is singular, not instanced
severity = "error"           # misspellings of distinctive forms are harder errors
```

## Test Plan

| # | Test | Spec link | Asserts |
|---|---|---|---|
| T1 | `test_canonical_terminology_toml_has_disambiguation_tier_per_term` | this proposal §"Schema extension" | Every term in canonical-terminology.toml has a `disambiguation_tier` field set to A, B, or C |
| T2 | `test_term_lint_hook_registered_in_settings` | rule item 12 (.claude/hooks/) | `term-disambiguation-lint.py` is registered as PostToolUse hook for Edit and Write tools |
| T3 | `test_tier_A_distinctive_form_flagged` | this proposal §"Tier A" | Edit producing `Membase` (wrong cap) flagged; `MemBase` (correct) passes |
| T4 | `test_tier_B_capitalization_canonical_context` | this proposal §"Tier B" | Edit producing "the backlog has 27 items" inside a bridge proposal flagged at warn severity (or block per Open Decision §A); "the Backlog has 27 items" passes |
| T5 | `test_tier_B_lowercase_general_context_passes` | this proposal §"Tier B" | Edit producing "we have a backlog of customer requests" in non-canonical-context (e.g., a chat-only response) does not flag |
| T6 | `test_tier_C_bare_canonical_with_demonstrative_flagged` | this proposal §"Tier C" | Edit producing "the spec we just landed" (specific reference, no ID) flagged; "the SPEC-1234 spec we just landed" passes |
| T7 | `test_override_syntax_suppresses_lint` | this proposal §"Override syntax" | Edit using the override marker (per Open Decision §B selection) does not trigger lint even when content matches Tier B/C violation patterns |
| T8 | `test_bridge_compliance_gate_extended_blocks_on_tier_B_violation` | this proposal §"Hook 2" | Bridge proposal containing lowercase canonical term ("backlog" without override) gets blocked, not warned |
| T9 | `test_owner_tunable_severity_per_term` | this proposal §"Schema extension" `severity` field | Setting `severity = "error"` for a Tier B term escalates the lint from warn to block |
| T10 | `test_lint_runs_in_smart_poller_spawned_sessions` | rule item 13 (smart-poller) | Headless dispatch-spawned session has the lint hook active; verified via fixture-based assertion in dispatch-prompt template |
| T11 | `test_forbidden_uses_explicitly_blocked` | rule item 1 (operating-model.md §2 forbidden_uses) | Edit producing a phrase matching a `forbidden_uses` entry (e.g., "backlog as ignore list") is blocked regardless of severity setting |
| T12 | `test_existing_artifacts_not_retroactively_blocked` | this proposal §"Out of scope" backfill | Pre-existing artifacts with Tier B violations remain untouched (grandfather clause); only NEW writes are lint-gated |
| T13 | `test_release_candidate_gate_runs_disambiguation_audit_report` | rule item 7 (GOV-20) | Release-candidate gate runs `gt term-disambiguation audit` and includes the report in release evidence |
| T14 | `test_DELIB_S327_term_disambiguation_directive_archived` | rule item 4 (deliberation-protocol) | After Slice 1 close, the owner directive is archived as `DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE` |

## Acceptance Criteria

- canonical-terminology.toml extended with `disambiguation_tier`, `specific_id_prefix`, and `severity` fields per term.
- All 22+ owner-required terms (per primer proposal) have non-empty disambiguation_tier values.
- `term-disambiguation-lint.py` PostToolUse hook registered and tested.
- `bridge-compliance-gate.py` extended (or new sibling hook) with Tier-B-blocks-on-bridges enforcement.
- Override syntax implemented and tested.
- Smart-poller dispatch sessions inherit the lint hook (T10).
- Doctor check `_check_term_disambiguation_policy_complete` registered.
- T1-T14 pass.
- IPR + CVR documents per slice per `GOV-20`.
- `DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE` archived per `GOV-ARTIFACT-APPROVAL-001`.
- Ruff + lint clean on all touched files.

## Risk and Rollback

- **Risk: lint produces too much noise; agents/owner ignore warnings.** Mitigation: severity-tunable per term; default severity is `warn`; owner can promote to `error` for chronically-drifted terms; backfill audit (Slice 6) reports drift volume so owner can prioritize.
- **Risk: lint produces false positives in chat-only responses (non-canonical contexts).** Mitigation: hook discriminates by file path (canonical contexts: `bridge/`, KB writes, ADR/DCL/SPEC files; non-canonical: chat outputs, ephemeral tasks). Tier B lint runs only on canonical-context writes by default.
- **Risk: override syntax becomes graffiti.** Mitigation: override usage tracked; doctor check reports overall override density; high density warns about possible policy mismatch.
- **Risk: capitalization rule conflicts with sentence-start capitalization.** Mitigation: lint distinguishes sentence-initial cap (which doesn't carry canonical-vs-common signal) from mid-sentence cap (which does). Test T4-T5 cover this.
- **Risk: smart-poller spawn doesn't actually inherit the hook.** Mitigation: T10 fixture-based assertion runs as part of the regular test suite; release-gate dependency.
- **Risk: backward-incompatible with existing artifacts.** Mitigation: grandfather clause (T12); only NEW writes are gated; backfill is opt-in via `gt term-disambiguation audit --rewrite-suggestions`.
- **Rollback:** revert hook registrations + canonical-terminology.toml schema extension + doctor check. Existing primer remains in place; lint becomes inactive; behavior reverts to current state.

## Sequencing (proposed slices)

1. **Slice 1 — Schema extension.** Extend canonical-terminology.toml with disambiguation_tier, specific_id_prefix, severity per term. Includes successor `DCL-TERM-DISAMBIGUATION-POLICY-001` recording the tiered policy. Pre-implementation only; needs `GOV-ARTIFACT-APPROVAL-001` packet.
2. **Slice 2 — Lint hook (warn-only mode).** Implement `term-disambiguation-lint.py`; register PostToolUse for Edit/Write; default severity `warn`. T1-T7.
3. **Slice 3 — Override syntax + Tier C heuristics.** Implement override marker per Open Decision §B; refine Tier C demonstrative-detection heuristic. T7 + T6.
4. **Slice 4 — Bridge-compliance-gate extension.** Tier B violations block in bridge proposals. T8 + T11.
5. **Slice 5 — Smart-poller dispatch integration.** Lint hook included in dispatch-spawned sessions. T10. Composes with `GTKB-GOV-TERM-PRIMER-STARTUP` Slice 3 (primer in dispatch prompts).
6. **Slice 6 — Backfill audit + release-gate integration.** `gt term-disambiguation audit` reports existing-artifact drift; release-gate runs the audit. T12 + T13.
7. **Slice 7 — Doctor check + AGENTS.md integration.** Doctor verifies policy completeness; AGENTS.md references the disambiguation rules. T9 + T14.

## Open Decisions

§A. **Default severity for Tier B violations.** Options: `warn` (default ship; owner promotes per term), `error` for bridge-proposal contexts only and `warn` elsewhere (current proposal default), `error` everywhere from day one. Suggest the middle option — it makes bridge proposals strict while letting other writes settle.

§B. **Override syntax.** Three candidates:
  - (i) `{!common: <term>}` — Markdown-friendly, custom; new syntax to learn.
  - (ii) `<!-- canonical:common --> <term> <!-- /canonical -->` — HTML-comment-based, verbose but uses existing markdown comment infrastructure.
  - (iii) `~<term>` — terse but conflicts with existing markdown convention for strikethrough in some renderers.
  Suggest (i) — cleanest balance; new syntax but easy to grep for.

§C. **Tier C demonstrative heuristic strictness.** Strict ("the X" + canonical term + no ID = always flag) or lax (require additional context cues). Suggest start strict; loosen if false-positive rate is high.

§D. **Forbidden-use enforcement severity.** Forbidden uses (e.g., "backlog as ignore list") are explicit drift; should they always block, or be tunable like Tier B? Suggest always block — they're explicit policy violations.

§E. **Backfill scope.** Existing artifacts:
  - (i) Grandfather (no retroactive lint).
  - (ii) Audit-only (one-time scan + report; no rewrites).
  - (iii) Audit + suggested rewrites (advisory).
  Suggest (ii) for Slice 6; (iii) is a future enhancement.

§F. **Capitalization rule for sentence-initial canonical terms.** "Backlog items must be reviewed." — sentence-start capitalization is mandatory in English regardless of canonical/common. Heuristic: ignore sentence-initial position for Tier B detection. Confirm acceptable.

§G. **Owner override of policy at the file level.** Some files (e.g., chat-rendered transcripts, customer-facing copy) may need to disable the lint entirely. Mechanism: `<!-- term-disambiguation: off -->` file-level marker. Suggest yes; integrates with override syntax (§B).

## Out of scope (this proposal)

- Implementation of Slices 1-7 (each lands its own bridge with code + tests).
- Backfill rewrites of existing artifacts (Slice 6 reports only; rewrites are a future opt-in slice).
- Cross-language disambiguation (non-English terms; not currently a GT-KB concern).
- Voice/audio surfaces (capitalization is text-only; voice transcripts handled separately if/when audio becomes a project surface).
- The term primer itself — provided by sibling proposal `GTKB-GOV-TERM-PRIMER-STARTUP`.

## Spec-to-test mapping (summary)

- `.claude/rules/operating-model.md` §2 → T1, T11 (canonical terms + forbidden-uses sourced from §2)
- `.claude/rules/file-bridge-protocol.md` → T8 (bridge-compliance-gate extension)
- `.claude/rules/project-root-boundary.md` → all (in-root paths)
- `.claude/rules/deliberation-protocol.md` → T14 (DELIB archival), Prior Deliberations section satisfies search obligation
- `GOV-ARTIFACT-APPROVAL-001` → T14 + Slice 1 acceptance (formal-artifact approval for DCL-TERM-DISAMBIGUATION-POLICY-001)
- `GOV-19-A1` → T2, T8 (outside-in via hook public surface)
- `GOV-20` → IPR/CVR per slice
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` → T13 (release-gate audit converts disambiguation from prompt-time to lint-time)
- `bridge/gtkb-gov-term-primer-startup-2026-05-02-001.md` → all (primer provides definitions; this proposal enforces usage)
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-003.md` → T4, T6 (running case study)
- Scaffolded `canonical-terminology.toml` → T1 (schema extension pattern)
- `.claude/hooks/` infrastructure → T2, T8, T10 (hook registration + integration)
- `bridge/gtkb-bridge-poller-001-smart-poller-007.md` → T10 (dispatch inheritance)
- Owner directive (verbatim) → T1 (tier coverage), T3-T7 (mechanical enforcement of disambiguation), T11 (forbidden-uses enforcement)

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
