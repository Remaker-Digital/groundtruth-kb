NEW

# Implementation Proposal - W4 Enforcement Calibration: Four Mechanical Bridge-Gate Fixes (GTKB-GOVERNANCE-CORRECTION-S358-W4)

bridge_kind: implementation_proposal
Document: gtkb-s358-w4-enforcement-calibration
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC
Session: S358

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Work Item: WI-3368

target_paths: ["scripts/bridge_applicability_preflight.py", "scripts/adr_dcl_clause_preflight.py", "config/governance/adr-dcl-clauses.toml", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/**", "platform_tests/hooks/**"]

## Problem

The bridge protocol's mechanical preflight and gate surfaces produce false-positive NO-GO and hard-block outcomes that, per the S358 governance-correction brief, account for roughly 44% of recent mechanical bridge churn. Four distinct defects, each verified against the live code:

(1) Phantom-path harvesting. `scripts/bridge_applicability_preflight.py` defines `PATH_TOKEN_RE` (lines 41-43) as an unanchored pattern matching any `word/word`-shaped token. `extract_target_paths` (lines 150-168) parses declared `target_paths:` lines, then at lines 164-167 runs `PATH_TOKEN_RE.finditer` over the entire proposal body, adding every match to the path set with only an `http(s):` exclusion. Prose phrases such as `GO/NO-GO`, `prime-builder/loyal-opposition`, `and/or`, or `read/write` are harvested as if they were repository file paths and fed to `applies_when_paths_match`, triggering applicability rules for specs the proposal never touches.

(2) Bulk-ops clause over-fire. `config/governance/adr-dcl-clauses.toml` (lines 109-123) defines clause `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` with an `applies_when_content` alternation that includes the bare token `work[- ]item`, and `severity`/`enforcement_mode` both `blocking`. `scripts/adr_dcl_clause_preflight.py` line 175 promotes a clause to `must_apply` when `content_hit and triggers_hit >= 1` - so a single occurrence of the phrase "work item" anywhere in proposal prose forces this bulk-operations clause to `must_apply`, even for proposals that perform no bulk standing-backlog operation.

(3) Heading-detection hard-block. `.claude/hooks/bridge-compliance-gate.py` emits a `deny` (hard block) when its section scanners misdetect a section boundary. `_deny_reason_for_content` returns deny strings routed through `emit_deny` (main, line 880). A heading-format misdetection blocks the Write entirely - there is no softer `ask` disposition for this class, so an author cannot proceed even to correct the proposal.

(4) `MUTATING_COMMAND_RE` fragility. `scripts/implementation_start_gate.py` (lines 79-86) defines `MUTATING_COMMAND_RE` with a final alternative `(?<![:>-])>{1,2}(?![>&=])` intended to catch shell redirects. It also matches bare Python comparison operators and right-shift in any command string that embeds Python. `_is_mutating_command` (line 379) uses the regex as a gate predicate, so a benign command containing Python operator text is misclassified as a protected mutation and incurs the implementation-start authorization gate.

All four are false positives: each blocks or mis-flags work that is actually compliant, while none of the four is load-bearing for any genuine governance check.

## Claim

Calibrate each of the four surfaces so the false positive is removed without removing any genuine governance coverage:

(1) Anchor `PATH_TOKEN_RE` content harvesting to declared `target_paths` plus an enumerated set of known repository directories, porting the anchored pattern already proven in `scripts/implementation_start_gate.py` (lines 100-102). Prose `word/word` tokens no longer harvest as paths; declared paths and repo-rooted path mentions still do.

(2) Narrow `CLAUSE-VISIBILITY-BULK-OPS`'s content trigger to genuine bulk-operation phrasings, removing the bare `work[- ]item` token; and demote single-content-hit promotion in `adr_dcl_clause_preflight.py` line 175 from `must_apply` to advisory `may_apply`, so one content hit advises rather than blocks.

(3) Downgrade heading-format misdetection in `bridge-compliance-gate.py` from `deny` to `ask`, so a heading-format ambiguity surfaces a confirmation rather than hard-blocking the Write. Genuine missing-section and placeholder-content failures continue to `deny`.

(4) Replace the redirect-detecting regex alternative in `MUTATING_COMMAND_RE` with a `shlex`-token structural parser that distinguishes a shell redirection operator token from a `>` character occurring inside a quoted argument or embedded Python expression.

None of the four changes relaxes a genuine governance check: each removes only the false-positive surface. Per-fix preservation tests lock the genuine-positive paths.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB`: `scripts/`, `config/governance/`, `.claude/hooks/`, `groundtruth-kb/templates/hooks/`, `platform_tests/scripts/`, and `platform_tests/hooks/`. This bridge proposal file resides under `E:\GT-KB\bridge\`. No target path and no output path is outside the GT-KB project root. No `applications/` path is touched.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - the bridge index and bridge verdict files are canonical workflow state; preflight and gate surfaces that false-positive obstruct that canonical workflow. Direct governing authority for keeping the bridge mechanical gates correct.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - the applicability preflight calibrated by W4 fix 1 is the mechanical enforcer of this DCL; calibrating it keeps the enforcer aligned with the requirement it serves. This proposal also carries concrete specification links per the DCL.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the clause preflight calibrated by W4 fix 2 is the mechanical enforcer of this DCL; the post-implementation report will carry a spec-to-test mapping and executed-test evidence.
- SPEC-AUQ-POLICY-ENGINE-001 - the bridge-compliance-gate (fix 3) and the implementation-start gate (fix 4) participate in the deterministic AUQ policy engine; the calibration keeps these surfaces deterministic and correctly scoped.
- SPEC-AUQ-NO-LLM-CLASSIFIER-001 - all four fixes are deterministic (anchored regex, narrowed TOML trigger, deny-to-ask disposition change, shlex token parse); none introduces an LLM classifier.
- GOV-STANDING-BACKLOG-001 - W4 fix 2 calibrates the GOV-STANDING-BACKLOG-001 / CLAUSE-VISIBILITY-BULK-OPS clause so it fires on genuine bulk standing-backlog operations rather than on the bare phrase "work item".
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - this proposal carries the mandatory Project Authorization, Project, and Work Item header lines.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target files are in-root under `E:\GT-KB`; no application path is touched.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the defects and fixes are preserved as durable artifacts (WI-3368, this proposal, the regression tests, the post-implementation report).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, proposal, tests, and report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3368 moves through open, in-progress, and verified lifecycle states.

## Prior Deliberations

A Deliberation Archive search for bridge-gate calibration and preflight false-positive churn was performed. Relevant prior record:

- DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION - the owner-decision deliberation authorizing this combined governance-correction project, with W4 enforcement calibration as one of four workstreams. It records the owner directive, the W4-first sequencing, and the rationale that W4-first calibration reduces mechanical NO-GO churn on every subsequent proposal.

No prior deliberation rejected or already addressed these four calibrations.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-1851` — seed=search; bridge_thread; Loyal Opposition Review - GTKB ADR-Evaluation Enforcement Program (Scoping)
- DA: `DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` — seed=search; owner_conversation; Owner decision - authorize and scope the S358 combined governance-correction pro
- DA: `DELIB-1525` — seed=search; bridge_thread; Loyal Opposition Verification - Owner-Decision Tracker Pattern Bounds + AUQ Reso
- DA: `DELIB-1817` — seed=search; bridge_thread; Loyal Opposition Verification - Rehearse Driver Wave Banner Cosmetic
- DA: `DELIB-1853` — seed=search; bridge_thread; Loyal Opposition Review - GTKB Spec Lifecycle Schema Migration

## Owner Decisions / Input

- 2026-05-17 UTC, S358: the owner directed standing up and running the combined governance-correction project, with W4 (enforcement calibration) sequenced first. The owner's S357 and S358 decisions - to supersede the project-completion spec via v2, to run the corrections as one combined project, to sequence W4 first for churn relief, and to retire PROJECT-GTKB-LO-OPPORTUNITY-RADAR - are captured in DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION (source_type=owner_conversation, outcome=owner_decision) and the project authorization PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION. The W1-W4 sequencing was collected via AskUserQuestion (owner answer: W4 first). No further owner decision is pending for the W4 fixes themselves; implementation proceeds on Codex GO within the project authorization scope.

## Requirement Sufficiency

Existing requirements sufficient. The specifications the four mechanical surfaces enforce - DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-STANDING-BACKLOG-001, SPEC-AUQ-POLICY-ENGINE-001 - are already in force and are not changed by this proposal. W4 calibrates the enforcing tooling to match those existing requirements more precisely; it does not create, revise, or relax any requirement. No new or revised requirement is needed.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk standing-backlog operation. It is a four-fix mechanical calibration tracked by exactly one work item, WI-3368, an active member of PROJECT-GTKB-GOVERNANCE-CORRECTION-S358 under PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION. No work-item state inventory, bulk transition, or backlog cleanup is performed. The proposal references the phrase "work item" and "standing backlog" only to describe W4 fix 2, which recalibrates the CLAUSE-VISIBILITY-BULK-OPS clause itself - a single inventory-free formal-artifact change, not a bulk operation.

## Bridge INDEX Update Evidence

A NEW entry for `gtkb-s358-w4-enforcement-calibration` is inserted at the top of `bridge/INDEX.md`, below the header comments and above the first existing Document entry, by the bridge-propose helper. No prior bridge file and no prior INDEX entry is deleted or rewritten; the append-only audit trail is preserved.

## Proposed Scope

### IP-1: Anchor phantom-path harvesting in the applicability preflight

In `scripts/bridge_applicability_preflight.py`, replace the unanchored `PATH_TOKEN_RE` (lines 41-43) with an anchored pattern requiring an enumerated repo-directory prefix, ported from `scripts/implementation_start_gate.py` lines 100-102 (directory set: scripts, groundtruth-kb/src, groundtruth-kb/tests, platform_tests, tests, config, .claude/hooks, .codex/gtkb-hooks, .github, bridge, independent-progress-assessments, plus the exact filenames .claude/settings.json, .codex/hooks.json, pyproject.toml, groundtruth.toml). `extract_target_paths` continues to parse declared `target_paths:` lines verbatim (lines 150-163); only the content-harvest pass (lines 164-167) is anchored. A prose `word/word` token no longer matches; a declared or repo-rooted path mention still does.

### IP-2: Narrow the bulk-ops clause trigger and demote single-content-hit promotion

In `config/governance/adr-dcl-clauses.toml` (lines 109-123), narrow CLAUSE-VISIBILITY-BULK-OPS's `applies_when_content` to genuine bulk-operation phrasings - retain `standing backlog`, `backlog cleanup`, `bulk (transition|update|operation)`; remove the bare `work[- ]item` alternative. In `scripts/adr_dcl_clause_preflight.py` line 175, change the single-content-hit branch so that `content_hit and triggers_hit >= 1` yields `may_apply` (advisory) rather than `must_apply` (blocking); full-trigger satisfaction (`triggers_hit == triggers_total`) still yields `must_apply`. A proposal that merely mentions "work item" is no longer forced to satisfy bulk-ops evidence.

### IP-3: Downgrade heading-misdetection from deny to ask in the compliance gate

In `.claude/hooks/bridge-compliance-gate.py`, route heading-format-misdetection failures (the section-scanner boundary-ambiguity class) to `emit_ask` rather than `emit_deny`. Genuine failures - a section that is truly absent, or whose content is a rejected placeholder (tbd, todo, n/a, none, not applicable, no relevant) - continue to `emit_deny`. Apply the byte-identical change to the scaffold template `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`. This fix is complementary to, and distinct from, the separately GO'd `gtkb-bridge-compliance-gate-fenced-code-parser-fix` thread (WI-3336, PROJECT-GTKB-RELIABILITY-FIXES), which repairs fenced-code section-boundary parsing; that thread lands under its own work item. The two changes touch the same hook and must be sequenced (whichever lands second rebases); they do not conflict in intent.

### IP-4: Replace MUTATING_COMMAND_RE redirect detection with a shlex token parser

In `scripts/implementation_start_gate.py`, replace the regex redirect alternative `(?<![:>-])>{1,2}(?![>&=])` within `MUTATING_COMMAND_RE` (lines 79-86) with a `shlex`-based token scan: tokenize the command and treat a `>` or `>>` token as a redirect only when it is a standalone shell operator token, not a `>` character inside a quoted argument or embedded Python expression. The named-command alternatives in `MUTATING_COMMAND_RE` (set-content, out-file, git commit, and the rest) are unchanged. `_is_mutating_command` (line 379) and `_all_mutating_signal_is_null_sink_redirect` (line 351) consume the corrected detection.

### IP-5: Regression and preservation tests

Add regression and preservation test coverage under `platform_tests/scripts/` (preflight fixes 1, 2, 4) and `platform_tests/hooks/` (gate fix 3), extending the existing preflight/gate test modules where present or adding new modules. One cluster per fix, each covering both the false-positive-removed path and the genuine-positive-preserved path:

- Fix 1: a prose `GO/NO-GO` token does not harvest as an applicability path; a declared `target_paths` entry and a repo-rooted `scripts/x.py` mention still harvest.
- Fix 2: a proposal mentioning only "work item" yields `may_apply` for CLAUSE-VISIBILITY-BULK-OPS; a genuine `bulk transition` proposal still yields `must_apply`.
- Fix 3: a heading-format ambiguity yields `ask`; a genuinely absent section and a placeholder-content section still yield `deny`.
- Fix 4: a command containing a Python `>` operator is not flagged mutating; a genuine `> file` redirect and the named-command mutations still are.

### Out of scope

W4 does not implement the `gtkb-bridge-compliance-gate-fenced-code-parser-fix` thread (WI-3336) - that GO'd thread lands separately under its own work item. W4 does not change any genuine governance check, any spec content, or any gate's blocking behavior for true positives. No change to `bridge/INDEX.md` semantics, the cross-harness trigger, or the formal-artifact-approval gate.

## Specification-Derived Verification Plan

| Specification | Behavior verified | Test |
|---|---|---|
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Prose word/word tokens do not harvest as applicability paths | test_preflight_prose_slash_not_harvested |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Declared target_paths and repo-rooted path mentions still harvest | test_preflight_declared_and_rooted_paths_still_harvested |
| GOV-STANDING-BACKLOG-001 | A proposal mentioning only "work item" yields may_apply, not must_apply | test_clause_work_item_phrase_is_advisory |
| GOV-STANDING-BACKLOG-001 | A genuine bulk-transition proposal still yields must_apply | test_clause_genuine_bulk_op_still_must_apply |
| GOV-FILE-BRIDGE-AUTHORITY-001 | A heading-format ambiguity yields ask, not deny | test_compliance_gate_heading_ambiguity_asks |
| GOV-FILE-BRIDGE-AUTHORITY-001 | A genuinely absent or placeholder section still yields deny | test_compliance_gate_absent_section_still_denies |
| SPEC-AUQ-POLICY-ENGINE-001 | A command containing a Python > operator is not flagged mutating | test_impl_start_gate_python_operator_not_mutating |
| SPEC-AUQ-POLICY-ENGINE-001 | A genuine shell redirect and named-command mutations are still flagged | test_impl_start_gate_genuine_redirect_still_mutating |
| SPEC-AUQ-NO-LLM-CLASSIFIER-001 | All four calibrations are deterministic, no LLM classifier introduced | full IP-5 cluster, deterministic fixtures |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Each fix carries both a false-positive-removed and a genuine-positive-preserved test | full IP-5 cluster |

Execution command:

`python -m pytest platform_tests/scripts/ platform_tests/hooks/ -v -k "preflight or clause or compliance_gate or implementation_start_gate"`

The post-implementation report will name the exact test modules and functions, re-run the existing bridge-compliance-gate and implementation-start-gate regression tests to confirm no regression, and run `ruff` over the changed files.

## Acceptance Criteria

- IP-1 through IP-5 landed.
- The applicability preflight no longer harvests prose `word/word` tokens as paths; declared and repo-rooted paths still harvest.
- CLAUSE-VISIBILITY-BULK-OPS no longer fires `must_apply` on the bare phrase "work item"; genuine bulk operations still trigger it.
- A heading-format ambiguity in `bridge-compliance-gate.py` yields `ask`; genuinely missing or placeholder sections still yield `deny`.
- `MUTATING_COMMAND_RE` no longer false-positives on Python `>` operators; genuine redirects and named-command mutations still flag.
- The live `bridge-compliance-gate.py` and its scaffold-template copy remain byte-identical.
- The IP-5 test clusters pass; existing preflight/gate regression tests still pass; `ruff` is clean over the changed files.
- Both bridge preflights pass on the post-implementation report.

## Option Rationale

For IP-1, porting the proven anchored pattern from `implementation_start_gate.py` was selected over inventing a new anchoring scheme: the implementation-start gate already solved the identical prose-token problem with an enumerated-directory anchor, and reusing it keeps the two path harvesters consistent and avoids a second pattern to maintain.

For IP-2, the two-part fix (narrow the TOML trigger and demote single-hit promotion) was selected over either change alone: narrowing the trigger alone would still leave `must_apply` promotion on a single hit of any remaining phrase; demoting promotion alone would leave the bare `work[- ]item` token matching. Both are needed to remove the false positive while keeping genuine bulk operations blocking.

For IP-3, deny-to-ask was selected over silently passing the heading-ambiguity case: an `ask` preserves an owner-visible confirmation surface for a genuinely ambiguous heading while removing the hard block; silently passing would remove the signal entirely.

For IP-4, a shlex token parser was selected over further regex lookaround patching: the redirect-vs-operator ambiguity is structural - a `>` token's meaning depends on shell tokenization - and successive lookaround patches have repeatedly produced sibling false-positive classes; a token parser resolves the ambiguity at the right layer.

## Risks / Rollback

- Risk: IP-1's anchored pattern misses a legitimate path mention using a directory not in the enumerated set. Mitigation: the enumerated set is ported verbatim from the implementation-start gate, which has operated on the same proposal corpus; declared `target_paths` are still parsed verbatim and are the authoritative path source. Covered by test_preflight_declared_and_rooted_paths_still_harvested.
- Risk: IP-2's trigger narrowing lets a genuine bulk operation escape `must_apply`. Mitigation: the retained phrasings are the genuine bulk-operation vocabulary; full-trigger satisfaction still yields `must_apply`. Covered by test_clause_genuine_bulk_op_still_must_apply.
- Risk: IP-3's deny-to-ask lets a malformed proposal through on an owner ask-confirmation. Mitigation: only the heading-format-ambiguity class moves to ask; genuinely absent and placeholder sections still deny. Covered by test_compliance_gate_absent_section_still_denies.
- Risk: IP-4's shlex parse mishandles an exotic command string. Mitigation: shlex is the standard shell tokenizer; the named-command alternatives are unchanged; a parse failure falls back conservatively to treating the command as non-redirect. Covered by test_impl_start_gate_genuine_redirect_still_mutating.
- Rollback: revert the affected files; each fix is self-contained with no schema, configuration-data, or migration dependency. IP-2's TOML change and IP-3's hook change are independently revertible.

## Recommended Commit Type

`fix` - all four changes repair false-positive behavior in mechanical bridge gates with no new capability surface. IP-4's shlex parser is an internal correction of an existing predicate, not a new public interface.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
