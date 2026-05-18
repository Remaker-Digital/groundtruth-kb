REVISED

# Implementation Proposal - W4 Enforcement Calibration: Five Mechanical Bridge-Gate Fixes (GTKB-GOVERNANCE-CORRECTION-S358-W4)

bridge_kind: implementation_proposal
Document: gtkb-s358-w4-enforcement-calibration
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Session: S358

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Work Item: WI-3368

target_paths: ["scripts/bridge_applicability_preflight.py", "scripts/adr_dcl_clause_preflight.py", "config/governance/adr-dcl-clauses.toml", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/**", "platform_tests/hooks/**"]

## Revision Note

Version 005 (REVISED) supersedes the `-004` GO. The `-003` revision (four fixes) received a clean Codex GO at `-004` on 2026-05-18 with no blocking findings. Per owner directive (S358, 2026-05-18, "Fold into W4"), `-005` folds in a fifth mechanical-calibration fix discovered while filing `-003`: a placeholder-vocabulary over-match in `.claude/hooks/bridge-compliance-gate.py` that hard-blocks a fully concrete Specification Links section whenever its prose contains a placeholder-vocabulary word.

`-005` carries the four GO'd fixes (IP-1 through IP-4) UNCHANGED from `-003` and adds IP-5 (the fifth fix) plus its Specification Links coverage, verification-plan rows, acceptance criterion, risk entry, and option rationale. The prior IP-5 test cluster is renumbered IP-6 and extended to cover the fifth fix. `target_paths` are unchanged - the fifth fix modifies `.claude/hooks/bridge-compliance-gate.py` and its scaffold template, both already declared.

Superseding the `-004` GO is required, not optional: that GO authorizes only the four-fix scope, and a fifth fix landing inside W4 requires the W4 proposal itself to describe it - a fix implemented but absent from the GO'd proposal would fail post-implementation verification for exceeding GO'd scope. The owner was informed that folding the fifth fix in supersedes the `-004` GO and directed proceeding.

## Problem

The bridge protocol's mechanical preflight and gate surfaces produce false-positive NO-GO and hard-block outcomes. The first four defects were identified in the S358 governance-correction brief and account for roughly 44% of recent mechanical bridge churn; a fifth was discovered while filing this proposal's `-003` revision. Five distinct defects, each verified against the live code:

(1) Phantom-path harvesting. `scripts/bridge_applicability_preflight.py` defines `PATH_TOKEN_RE` (lines 41-43) as an unanchored pattern matching any `word/word`-shaped token. `extract_target_paths` (lines 150-168) parses declared `target_paths:` lines, then at lines 164-167 runs `PATH_TOKEN_RE.finditer` over the entire proposal body, adding every match to the path set with only an `http(s):` exclusion. Prose phrases such as `GO/NO-GO`, `prime-builder/loyal-opposition`, `and/or`, or `read/write` are harvested as if they were repository file paths and fed to `applies_when_paths_match`, triggering applicability rules for specs the proposal never touches.

(2) Bulk-ops clause over-fire. `config/governance/adr-dcl-clauses.toml` (lines 109-123) defines clause `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` with an `applies_when_content` alternation that includes the bare token `work[- ]item`, and `severity`/`enforcement_mode` both `blocking`. `scripts/adr_dcl_clause_preflight.py` line 175 promotes a clause to `must_apply` when `content_hit and triggers_hit >= 1` - so a single occurrence of the phrase "work item" anywhere in proposal prose forces this bulk-operations clause to `must_apply`, even for proposals that perform no bulk standing-backlog operation.

(3) Heading-detection hard-block. `.claude/hooks/bridge-compliance-gate.py` emits a `deny` (hard block) when its section scanners misdetect a section boundary. `_deny_reason_for_content` returns deny strings routed through `emit_deny` (main, line 880). A heading-format misdetection blocks the Write entirely - there is no softer `ask` disposition for this class, so an author cannot proceed even to correct the proposal.

(4) `MUTATING_COMMAND_RE` fragility. `scripts/implementation_start_gate.py` (lines 79-86) defines `MUTATING_COMMAND_RE` with a final alternative `(?<![:>-])>{1,2}(?![>&=])` intended to catch shell redirects. It also matches bare Python comparison operators and right-shift in any command string that embeds Python. `_is_mutating_command` (line 379) uses the regex as a gate predicate, so a benign command containing Python operator text is misclassified as a protected mutation and incurs the implementation-start authorization gate.

(5) Placeholder-vocabulary over-match. `.claude/hooks/bridge-compliance-gate.py` line 39 defines `SPEC_PLACEHOLDER_RE = re.compile(r"\b(?:tbd|todo|none|n/a|not applicable|no relevant)\b", re.IGNORECASE)`. `_has_concrete_spec_links` (lines 269-288) treats a `## Specification Links` section as concrete only when `not SPEC_PLACEHOLDER_RE.search(section_text)` - a `.search` that matches anywhere in the section. Because the regex matches bare English words that occur in legitimate citation-rationale prose, a Specification Links section carrying genuine `SPEC-`/`GOV-`/`DCL-`/`ADR-` citation tokens is hard-blocked as placeholder content when any rationale uses one. Observed live: the `-003` revision of this very proposal was hard-blocked on its first Write because a Specification Links bullet's prose contained one of those words; the prose had to be reworded to file the revision.

All five are false positives: each blocks or mis-flags work that is actually compliant, while none of the five is load-bearing for any genuine governance check.

## Claim

Calibrate each of the five surfaces so the false positive is removed without removing any genuine governance coverage:

(1) Anchor `PATH_TOKEN_RE` content harvesting to declared `target_paths` plus an enumerated set of known repository directories, porting the anchored pattern already proven in `scripts/implementation_start_gate.py` (lines 100-102). Prose `word/word` tokens no longer harvest as paths; declared paths and repo-rooted path mentions still do.

(2) Narrow `CLAUSE-VISIBILITY-BULK-OPS`'s content trigger to genuine bulk-operation phrasings, removing the bare `work[- ]item` token; and demote single-content-hit promotion in `adr_dcl_clause_preflight.py` line 175 from `must_apply` to advisory `may_apply`, so one content hit advises rather than blocks.

(3) Downgrade heading-format misdetection in `bridge-compliance-gate.py` from `deny` to `ask`, so a heading-format ambiguity surfaces a confirmation rather than hard-blocking the Write. Genuine missing-section and placeholder-content failures continue to `deny`.

(4) Replace the redirect-detecting regex alternative in `MUTATING_COMMAND_RE` with a `shlex`-token structural parser that distinguishes a shell redirection operator token from a `>` character occurring inside a quoted argument or embedded Python expression.

(5) Narrow the `_has_concrete_spec_links` placeholder-content check in `bridge-compliance-gate.py` so a `## Specification Links` section carrying genuine spec-link citation tokens is not rejected for containing a placeholder-vocabulary word in legitimate citation-rationale prose. The check still rejects a placeholder-only section.

No fix among the five relaxes a genuine governance check: each removes only the false-positive surface. Per-fix preservation tests lock the genuine-positive paths.

Relevance-closure and mechanical-enforcement preservation (per the `-002` NO-GO F1/F2): W4 preserves `DCL-SPEC-RELEVANCE-CLOSURE-001` - the applicability preflight remains a mechanical floor and reviewer relevance judgment remains the ceiling; IP-1's anchoring removes only phantom-path-driven spurious required-spec demands and never drops a genuine path-keyed spec, because declared `target_paths` and repo-rooted path mentions still harvest. W4 preserves `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` - genuine missing-section, placeholder-content, bulk-operation, and shell-redirect violations still hard-enforce after the calibration; IP-2 keeps full-trigger satisfaction at `must_apply`, IP-3 keeps genuinely-absent and placeholder sections at `deny`, IP-5 keeps a placeholder-only Specification Links section rejected, and the IP-6 preservation tests assert each genuine-positive path still blocks.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB`: `scripts/`, `config/governance/`, `.claude/hooks/`, `groundtruth-kb/templates/hooks/`, `platform_tests/scripts/`, and `platform_tests/hooks/`. This bridge proposal file resides under `E:\GT-KB\bridge\`. No target path and no output path is outside the GT-KB project root. No `applications/` path is touched.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - the bridge index and bridge verdict files are canonical workflow state; preflight and gate surfaces that false-positive obstruct that canonical workflow. Direct governing authority for keeping the bridge mechanical gates correct.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - the applicability preflight calibrated by W4 fix 1 is the mechanical enforcer of this DCL; calibrating it keeps the enforcer aligned with the requirement it serves. W4 fix 5 additionally calibrates `_has_concrete_spec_links` in the bridge-compliance gate - the write-time enforcer of this DCL - so it accepts a relevance-complete Specification Links section instead of rejecting one whose rationale prose contains a placeholder-vocabulary word. This proposal also carries concrete specification links per the DCL.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the clause preflight calibrated by W4 fix 2 is the mechanical enforcer of this DCL; the post-implementation report will carry a spec-to-test mapping and executed-test evidence.
- DCL-SPEC-RELEVANCE-CLOSURE-001 - bridge proposal spec linkage must be relevance-complete, not just non-empty. W4 fix 1 modifies `scripts/bridge_applicability_preflight.py`, the mechanical surface that enforces this DCL, and W4's `target_paths` include `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`, named in this DCL's source_paths. IP-1's anchoring removes phantom-path-driven spurious required-spec demands without weakening genuine relevance closure: declared `target_paths` and repo-rooted path mentions still harvest, so every genuine path-keyed spec still triggers; the preflight stays a mechanical floor and reviewer relevance judgment stays the ceiling.
- DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001 - all directives must be mechanically enforced, not documentation-only. W4 changes mechanical enforcement classifications (IP-2 demotes single-content-hit promotion to `may_apply`; IP-3 downgrades heading-misdetection from `deny` to `ask`; IP-5 narrows a placeholder-content check). W4 preserves hard mechanical enforcement for genuine violations: IP-2 keeps full-trigger satisfaction at `must_apply`, IP-3 keeps genuinely-absent and placeholder sections at `deny`, IP-5 keeps a placeholder-only Specification Links section rejected, and the IP-6 preservation tests assert each genuine-positive path still blocks.
- SPEC-AUQ-POLICY-ENGINE-001 - the bridge-compliance-gate (fixes 3 and 5) and the implementation-start gate (fix 4) participate in the deterministic AUQ policy engine; the calibration keeps these surfaces deterministic and correctly scoped.
- SPEC-AUQ-NO-LLM-CLASSIFIER-001 - all five fixes are deterministic (anchored regex, narrowed TOML trigger, deny-to-ask disposition change, shlex token parse, per-line placeholder evaluation); no fix introduces an LLM classifier.
- GOV-STANDING-BACKLOG-001 - W4 fix 2 calibrates the GOV-STANDING-BACKLOG-001 / CLAUSE-VISIBILITY-BULK-OPS clause so it fires on genuine bulk standing-backlog operations rather than on the bare phrase "work item".
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - this proposal carries the mandatory Project Authorization, Project, and Work Item header lines.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target files are in-root under `E:\GT-KB`; no application path is touched.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the defects and fixes are preserved as durable artifacts (WI-3368, this proposal, the regression tests, the post-implementation report).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, proposal, tests, and report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3368 moves through open, in-progress, and verified lifecycle states.

## Prior Deliberations

A Deliberation Archive search for bridge-gate calibration and preflight false-positive churn was performed. Relevant records:

- DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION - the owner-decision deliberation authorizing this combined governance-correction project, with W4 enforcement calibration as one of four workstreams. It records the owner directive, the W4-first sequencing, and the rationale that W4-first calibration reduces mechanical NO-GO churn on every subsequent proposal.
- DELIB-1851 - a prior Loyal Opposition NO-GO for ADR-evaluation enforcement scoping, cited in the `-002` review. It first flagged missing spec-coverage governance - including `DCL-SPEC-RELEVANCE-CLOSURE-001` - for proposal-time applicability/enforcement work. This proposal applies that prior finding to W4 by citing the relevance-closure and mechanical-enforcement DCLs explicitly.

No prior deliberation rejected or already addressed these five calibrations.

## Owner Decisions / Input

- 2026-05-17 UTC, S358: the owner directed standing up and running the combined governance-correction project, with W4 (enforcement calibration) sequenced first. The owner's S357 and S358 decisions - to supersede the project-completion spec via v2, to run the corrections as one combined project, to sequence W4 first for churn relief, and to retire PROJECT-GTKB-LO-OPPORTUNITY-RADAR - are captured in DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION (source_type=owner_conversation, outcome=owner_decision) and the project authorization PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION. The W1-W4 sequencing was collected via AskUserQuestion (owner answer: W4 first).
- 2026-05-18 UTC, S358: after `-003` was filed, Prime Builder surfaced a fifth bridge-gate false-positive - the placeholder-vocabulary over-match - discovered while filing `-003`, and presented two dispositions: fold it into W4, or handle it as a separate follow-up. The owner directed "Fold into W4". Prime Builder informed the owner that, because `-003` had since received the `-004` GO, folding the fifth fix in supersedes that GO; the owner directed proceeding. This `-005` revision executes that directive within the existing project authorization scope. No further owner decision is pending.

## Requirement Sufficiency

Existing requirements sufficient. The specifications the five mechanical surfaces enforce - DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, DCL-SPEC-RELEVANCE-CLOSURE-001, DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001, GOV-STANDING-BACKLOG-001, SPEC-AUQ-POLICY-ENGINE-001 - are already in force and are not changed by this proposal. W4 calibrates the enforcing tooling to match those existing requirements more precisely; it does not create, revise, or relax any requirement. No new or revised requirement is needed.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk standing-backlog operation. It is a five-fix mechanical calibration tracked by exactly one work item, WI-3368, an active member of PROJECT-GTKB-GOVERNANCE-CORRECTION-S358 under PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION. No work-item state inventory, bulk transition, or backlog cleanup is performed. The proposal references the phrase "work item" and "standing backlog" only to describe W4 fix 2, which recalibrates the CLAUSE-VISIBILITY-BULK-OPS clause itself - a single inventory-free formal-artifact change, not a bulk operation.

## Bridge INDEX Update Evidence

A REVISED entry for `gtkb-s358-w4-enforcement-calibration` is inserted at the top of that document's version list in `bridge/INDEX.md`, above the `GO: -004`, `REVISED: -003`, `NO-GO: -002`, and `NEW: -001` lines. No prior bridge file and no prior INDEX entry is deleted or rewritten; `-001` through `-004` remain on disk and in the index as the append-only audit trail.

## Proposed Scope

### IP-1: Anchor phantom-path harvesting in the applicability preflight

In `scripts/bridge_applicability_preflight.py`, replace the unanchored `PATH_TOKEN_RE` (lines 41-43) with an anchored pattern requiring an enumerated repo-directory prefix, ported from `scripts/implementation_start_gate.py` lines 100-102 (directory set: scripts, groundtruth-kb/src, groundtruth-kb/tests, platform_tests, tests, config, .claude/hooks, .codex/gtkb-hooks, .github, bridge, independent-progress-assessments, plus the exact filenames .claude/settings.json, .codex/hooks.json, pyproject.toml, groundtruth.toml). `extract_target_paths` continues to parse declared `target_paths:` lines verbatim (lines 150-163); only the content-harvest pass (lines 164-167) is anchored. A prose `word/word` token no longer matches; a declared or repo-rooted path mention still does, so every genuine path-keyed applicability rule still triggers.

### IP-2: Narrow the bulk-ops clause trigger and demote single-content-hit promotion

In `config/governance/adr-dcl-clauses.toml` (lines 109-123), narrow CLAUSE-VISIBILITY-BULK-OPS's `applies_when_content` to genuine bulk-operation phrasings - retain `standing backlog`, `backlog cleanup`, `bulk (transition|update|operation)`; remove the bare `work[- ]item` alternative. In `scripts/adr_dcl_clause_preflight.py` line 175, change the single-content-hit branch so that `content_hit and triggers_hit >= 1` yields `may_apply` (advisory) rather than `must_apply` (blocking); full-trigger satisfaction (`triggers_hit == triggers_total`) still yields `must_apply`. A proposal that merely mentions "work item" is no longer forced to satisfy bulk-ops evidence; a genuine bulk operation still must.

### IP-3: Downgrade heading-misdetection from deny to ask in the compliance gate

In `.claude/hooks/bridge-compliance-gate.py`, route heading-format-misdetection failures (the section-scanner boundary-ambiguity class) to `emit_ask` rather than `emit_deny`. Genuine failures - a section that is truly absent, or whose content is a rejected placeholder - continue to `emit_deny`. Apply the byte-identical change to the scaffold template `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`. This fix is complementary to, and distinct from, the separately GO'd `gtkb-bridge-compliance-gate-fenced-code-parser-fix` thread (WI-3336, PROJECT-GTKB-RELIABILITY-FIXES), which repairs fenced-code section-boundary parsing; that thread lands under its own work item. IP-3, IP-5, and the fenced-code-parser-fix thread all modify `bridge-compliance-gate.py`; they are non-conflicting in intent but must be sequenced (whichever lands later rebases).

### IP-4: Replace MUTATING_COMMAND_RE redirect detection with a shlex token parser

In `scripts/implementation_start_gate.py`, replace the regex redirect alternative `(?<![:>-])>{1,2}(?![>&=])` within `MUTATING_COMMAND_RE` (lines 79-86) with a `shlex`-based token scan: tokenize the command and treat a `>` or `>>` token as a redirect only when it is a standalone shell operator token, not a `>` character inside a quoted argument or embedded Python expression. The named-command alternatives in `MUTATING_COMMAND_RE` (set-content, out-file, git commit, and the rest) are unchanged. `_is_mutating_command` (line 379) and `_all_mutating_signal_is_null_sink_redirect` (line 351) consume the corrected detection.

### IP-5: Narrow the placeholder-content check in the bridge-compliance gate

In `.claude/hooks/bridge-compliance-gate.py`, `_has_concrete_spec_links` (lines 269-288) currently rejects a `## Specification Links` section whenever `SPEC_PLACEHOLDER_RE` (line 39) matches anywhere in the section text - a whole-section `.search`. `SPEC_PLACEHOLDER_RE` matches a small set of bare placeholder-vocabulary words. Narrow the check so a section carrying genuine `SPEC_LINK_TOKEN_RE` citation tokens is not rejected solely because a placeholder-vocabulary word appears in citation-rationale prose. Sound approach: evaluate the placeholder test per line, exempting any line that itself carries a genuine spec-link token (its prose is concrete-citation rationale); the section is placeholder-content only when a line WITHOUT any spec-link token is itself a placeholder. The existing requirement that the section carry at least one `SPEC_LINK_TOKEN_RE` match is retained. The exact predicate is settled in implementation; the invariant is that genuine concrete citations are accepted and a placeholder-only section is still rejected. Apply the byte-identical change to the scaffold template `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`. `_has_concrete_owner_decisions_section` already evaluates per line and is left unchanged.

### IP-6: Regression and preservation tests

Add regression and preservation test coverage under `platform_tests/scripts/` (preflight fixes 1, 2, 4) and `platform_tests/hooks/` (gate fixes 3 and 5), extending the existing preflight/gate test modules where present or adding new modules. One cluster per fix, each covering both the false-positive-removed path and the genuine-positive-preserved path:

- Fix 1: a prose `GO/NO-GO` token does not harvest as an applicability path; a declared `target_paths` entry and a repo-rooted `scripts/x.py` mention still harvest (the genuine-positive path that preserves relevance closure).
- Fix 2: a proposal mentioning only "work item" yields `may_apply` for CLAUSE-VISIBILITY-BULK-OPS; a genuine `bulk transition` proposal still yields `must_apply`.
- Fix 3: a heading-format ambiguity yields `ask`; a genuinely absent section and a placeholder-content section still yield `deny`.
- Fix 4: a command containing a Python `>` operator is not flagged mutating; a genuine `> file` redirect and the named-command mutations still are.
- Fix 5: a Specification Links section carrying genuine citation tokens passes `_has_concrete_spec_links` even when a rationale contains a placeholder-vocabulary word; a placeholder-only section with no genuine citation still fails.

### Out of scope

W4 does not implement the `gtkb-bridge-compliance-gate-fenced-code-parser-fix` thread (WI-3336) - that GO'd thread lands separately under its own work item. W4 does not change any genuine governance check, any spec content, or any gate's blocking behavior for true positives. No change to `bridge/INDEX.md` semantics, the cross-harness trigger, or the formal-artifact-approval gate.

## Specification-Derived Verification Plan

| Specification | Behavior verified | Test |
|---|---|---|
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Prose word/word tokens do not harvest as applicability paths | test_preflight_prose_slash_not_harvested |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Declared target_paths and repo-rooted path mentions still harvest | test_preflight_declared_and_rooted_paths_still_harvested |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | A Specification Links section with genuine citation tokens passes even when a rationale contains a placeholder-vocabulary word; a placeholder-only section still fails | test_compliance_gate_concrete_links_with_placeholder_word_passes, test_compliance_gate_placeholder_only_section_still_rejected |
| DCL-SPEC-RELEVANCE-CLOSURE-001 | IP-1 anchoring preserves relevance closure: declared target_paths and repo-rooted path mentions still harvest, so genuine path-keyed specs still trigger; only phantom prose tokens are dropped | test_preflight_declared_and_rooted_paths_still_harvested |
| GOV-STANDING-BACKLOG-001 | A proposal mentioning only "work item" yields may_apply, not must_apply | test_clause_work_item_phrase_is_advisory |
| GOV-STANDING-BACKLOG-001 | A genuine bulk-transition proposal still yields must_apply | test_clause_genuine_bulk_op_still_must_apply |
| GOV-FILE-BRIDGE-AUTHORITY-001 | A heading-format ambiguity yields ask, not deny | test_compliance_gate_heading_ambiguity_asks |
| GOV-FILE-BRIDGE-AUTHORITY-001 | A genuinely absent or placeholder section still yields deny | test_compliance_gate_absent_section_still_denies |
| SPEC-AUQ-POLICY-ENGINE-001 | A command containing a Python > operator is not flagged mutating | test_impl_start_gate_python_operator_not_mutating |
| SPEC-AUQ-POLICY-ENGINE-001 | A genuine shell redirect and named-command mutations are still flagged | test_impl_start_gate_genuine_redirect_still_mutating |
| DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001 | Genuine violations still hard-enforce after calibration: absent/placeholder section yields deny, genuine bulk operation yields must_apply, genuine shell redirect is flagged mutating, placeholder-only Specification Links section still rejected | test_compliance_gate_absent_section_still_denies, test_clause_genuine_bulk_op_still_must_apply, test_impl_start_gate_genuine_redirect_still_mutating, test_compliance_gate_placeholder_only_section_still_rejected |
| SPEC-AUQ-NO-LLM-CLASSIFIER-001 | All five calibrations are deterministic, with no LLM classifier introduced | full IP-6 cluster, deterministic fixtures |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Each fix carries both a false-positive-removed and a genuine-positive-preserved test | full IP-6 cluster |

Execution command:

`python -m pytest platform_tests/scripts/ platform_tests/hooks/ -v -k "preflight or clause or compliance_gate or implementation_start_gate"`

The post-implementation report will name the exact test modules and functions, re-run the existing bridge-compliance-gate and implementation-start-gate regression tests to confirm no regression, and run `ruff` over the changed files.

## Acceptance Criteria

- IP-1 through IP-6 landed.
- The applicability preflight no longer harvests prose `word/word` tokens as paths; declared and repo-rooted paths still harvest (relevance closure preserved per DCL-SPEC-RELEVANCE-CLOSURE-001).
- CLAUSE-VISIBILITY-BULK-OPS no longer fires `must_apply` on the bare phrase "work item"; genuine bulk operations still trigger it.
- A heading-format ambiguity in `bridge-compliance-gate.py` yields `ask`; genuinely missing or placeholder sections still yield `deny` (mechanical enforcement preserved per DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001).
- `MUTATING_COMMAND_RE` no longer false-positives on Python `>` operators; genuine redirects and named-command mutations still flag.
- `_has_concrete_spec_links` accepts a Specification Links section carrying genuine citation tokens even when a rationale contains a placeholder-vocabulary word; a placeholder-only section with no genuine citation still fails.
- The live `bridge-compliance-gate.py` and its scaffold-template copy remain byte-identical.
- The IP-6 test clusters pass; existing preflight/gate regression tests still pass; `ruff` is clean over the changed files.
- Both bridge preflights pass on the post-implementation report.

## Option Rationale

For IP-1, porting the proven anchored pattern from `implementation_start_gate.py` was selected over inventing a new anchoring scheme: the implementation-start gate already solved the identical prose-token problem with an enumerated-directory anchor, and reusing it keeps the two path harvesters consistent and avoids a second pattern to maintain.

For IP-2, the two-part fix (narrow the TOML trigger and demote single-hit promotion) was selected over either change alone: narrowing the trigger alone would still leave `must_apply` promotion on a single hit of any remaining phrase; demoting promotion alone would leave the bare `work[- ]item` token matching. Both are needed to remove the false positive while keeping genuine bulk operations blocking.

For IP-3, deny-to-ask was selected over silently passing the heading-ambiguity case: an `ask` preserves an owner-visible confirmation surface for a genuinely ambiguous heading while removing the hard block; silently passing would remove the signal entirely and weaken mechanical enforcement.

For IP-4, a shlex token parser was selected over further regex lookaround patching: the redirect-vs-operator ambiguity is structural - a `>` token's meaning depends on shell tokenization - and successive lookaround patches have repeatedly produced sibling false-positive classes; a token parser resolves the ambiguity at the right layer.

For IP-5, a per-line placeholder evaluation was selected over deleting the placeholder check entirely: the check still has value - it catches a section whose only content is a placeholder with no genuine citation - so the fix narrows its scope to non-citation lines rather than removing it.

## Risks / Rollback

- Risk: IP-1's anchored pattern misses a legitimate path mention using a directory not in the enumerated set. Mitigation: the enumerated set is ported verbatim from the implementation-start gate, which has operated on the same proposal corpus; declared `target_paths` are still parsed verbatim and are the authoritative path source. Covered by test_preflight_declared_and_rooted_paths_still_harvested.
- Risk: IP-2's trigger narrowing lets a genuine bulk operation escape `must_apply`. Mitigation: the retained phrasings are the genuine bulk-operation vocabulary; full-trigger satisfaction still yields `must_apply`. Covered by test_clause_genuine_bulk_op_still_must_apply.
- Risk: IP-3's deny-to-ask lets a malformed proposal through on an owner ask-confirmation. Mitigation: only the heading-format-ambiguity class moves to ask; genuinely absent and placeholder sections still deny. Covered by test_compliance_gate_absent_section_still_denies.
- Risk: IP-4's shlex parse mishandles an exotic command string. Mitigation: shlex is the standard shell tokenizer; the named-command alternatives are unchanged; a parse failure falls back conservatively to treating the command as non-redirect. Covered by test_impl_start_gate_genuine_redirect_still_mutating.
- Risk: IP-5's per-line placeholder check lets a genuinely placeholder-stubbed section through. Mitigation: a line is exempt from the placeholder test only when it carries a genuine `SPEC_LINK_TOKEN_RE` match; a placeholder line with no citation token still fails the section, and the whole-section `SPEC_LINK_TOKEN_RE` requirement is retained. Covered by test_compliance_gate_placeholder_only_section_still_rejected.
- Rollback: revert the affected files; each fix is self-contained with no schema, configuration-data, or migration dependency. IP-2's TOML change, IP-3's hook change, and IP-5's hook change are independently revertible.

## Recommended Commit Type

`fix` - all five changes repair false-positive behavior in mechanical bridge gates with no new capability surface. IP-4's shlex parser and IP-5's per-line evaluation are internal corrections of existing predicates, not new public interfaces.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
