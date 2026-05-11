REVISED

# Bridge ADVISORY Status + ADVISORY_REPORT Message Type - REVISED-4

bridge_kind: implementation_proposal
Document: gtkb-bridge-advisory-status-001
Version: 009 (REVISED-4 after Codex NO-GO at `-008`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S342
Responds-To: `bridge/gtkb-bridge-advisory-status-001-008.md` (Codex NO-GO; F1/F2 findings on incomplete parser inventory).

## Revision Notes (REVISED-4)

**F1 (P1) addressed:** Added `.claude/hooks/bridge-compliance-gate.py` to IP-11 inventory with UPDATE disposition. The hook's status loop at `:109` and `:310` (`("VERIFIED", "GO", "NO-GO", "REVISED", "NEW")`) is extended to recognize `ADVISORY`. ADVISORY top-of-stack status is parsed as the latest entry (stops the scan at the first matched status, exactly as VERIFIED stops it). Critically, `PENDING_PREFLIGHT_STATUSES` at `:28` (currently `{"NEW", "REVISED"}`) is INTENTIONALLY UNCHANGED: ADVISORY is an LO-authored meta-status that does NOT require Prime-side preflight gating (it is non-implementation/non-actionable for Prime per `.claude/rules/file-bridge-protocol.md` § Advisory Reports). A new paired regression test asserts the hook recognizes ADVISORY at top-of-stack and does NOT fall through to stale older entries, AND does NOT route ADVISORY through the preflight-pending gate.

**F2 (P2) addressed:** Expanded IP-11 inventory from 10 sites to 17 sites by adding the six F2 status-consumer call sites. Each new site carries an explicit disposition (UPDATE / INTENTIONALLY-IGNORE / OUT-OF-SCOPE) with rationale. The IP-11 inventory is now closed against both regex-based parsers AND status-set-membership consumers; F2's "broader status-consumer search" surface is now fully classified.

**Inventory expansion summary:**
- 4 sites get UPDATE disposition (parser must recognize ADVISORY): `bridge-compliance-gate.py:109,310`, `operating_state.py:419`, `audit_standing_backlog_sources.py:39` (regex only), `wrap_scan_consistency.py:46`.
- 2 sites get INTENTIONALLY-IGNORE disposition (ADVISORY out of curated set): `audit_standing_backlog_sources.py:15` (ACTIONABLE set; ADVISORY is meta-governance not "actionable work"), `audit_gtkb_triad_completeness.py:256` (terminal-status filter; ADVISORY not terminal), `notify.py:76-77` (smart-poller actionable sets; ADVISORY non-actionable like VERIFIED).
- 1 site gets OUT-OF-SCOPE disposition (different conceptual surface): `routing.py:26-27` (Prime/Codex authorship partition; ADVISORY is orthogonal harness-level meta-status).

**Carry-forward from REVISED-3 (unchanged):** IP-1 through IP-10 + the original IP-11 ten parser sites; all spec links; preflight passes; the migration qualification + cross-harness trigger semantics; approval-packet plumbing.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/operating-model.md`
- `config/agent-control/system-interface-map.toml`

## Prior Deliberations

- `bridge/gtkb-advisory-report-message-type-2026-05-09-001.md` - source LO advisory; this proposal implements Slice-1 scope.
- `bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09-001.md` - second LO advisory using NO-GO@001 transport; migration covers it.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-006.md` (VERIFIED) - two-axis bridge automation model. ADVISORY is Axis-2-routable (non-dispatchable).
- `DELIB-0880` - bridge/INDEX.md is authoritative; LO has permanent bridge-function repair authority.
- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` - owner directive on role/actionability drift detection.
- `bridge/gtkb-bridge-advisory-status-001-006.md` - Codex NO-GO with F1 (preflight parser) and F2 (parser inventory); REVISED-3 closed F1 (preflight) but did not fully close F2.
- `bridge/gtkb-bridge-advisory-status-001-008.md` - Codex NO-GO with F1 (bridge-compliance-gate.py omitted from REVISED-3 inventory) and F2 (six additional status-consumer call sites unclassified); REVISED-4 closes both.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive** carried forward from REVISED-3: authorizes proposal iteration.
- **AUQ S342 (2026-05-11) backlog-priorities directive** — "Please proceed with Backlog priorities. Parallelize work and proceed without my intervention when possible. In the course of work, if you notice an issue which should be fixed or an opportunity for a useful enhancement that will help us work more effectively in the future, please add it to the backlog as an item for future implementation consideration." Authorizes this REVISED-4 filing.
- Per `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001`, formal-artifact-approval packets are produced at implementation time for all governed narrative artifacts touched (rules, CLAUDE.md, AGENTS.md, skills, templates).

Outstanding owner decisions before VERIFIED: approval packets for narrative artifacts generated at implementation time. No new owner-decision class introduced by REVISED-4.

## Scope (Slice 1 - REVISED-4)

### IN SCOPE

**IP-1 through IP-10:** As per REVISED-3, unchanged.

**IP-11 (EXPANDED in REVISED-4): Status-parser AND status-consumer inventory with per-file disposition.** The original IP-11 in REVISED-3 covered 10 regex-based parser sites. REVISED-4 extends the inventory to include the bridge-compliance-gate.py hook + six broader status-consumer call sites identified by Codex `-008`. Final inventory has 17 sites:

#### IP-11 Inventory (UPDATE disposition — parser/hook must recognize ADVISORY)

| File | Line(s) | Current behavior | REVISED-4 disposition | Test |
|---|---|---|---|---|
| `scripts/bridge_applicability_preflight.py` | 31 | `INDEX_STATUS_RE` 5-status alternation | UPDATE: add `ADVISORY` | IP-10 (carried) |
| `groundtruth-kb/src/groundtruth_kb/bridge/detector.py` | (multiple) | Status-aware bridge thread detector | UPDATE per IP-6 | existing IP-6 test |
| `scripts/gtkb_bridge_writer.py` | (multiple) | Status-aware bridge writer | UPDATE per IP-6 | existing IP-6 test |
| `scripts/session_self_initialization.py` | (multiple) | Startup bridge-state surface | UPDATE per IP-4 | existing IP-4 test |
| `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | 889 | `line_re = ^(NEW|REVISED|GO|NO-GO|VERIFIED):` | UPDATE: 6-status; ADVISORY is "active, awaiting Prime response" | `test_doctor_advisory_status.py` (REVISED-3) |
| `groundtruth-kb/src/groundtruth_kb/project/preflight.py` | 55-56 | `_STATUS_LINE_RE` + `_NON_TERMINAL_STATUSES` `{NEW,REVISED,GO}` | UPDATE: 6-status regex; add `ADVISORY` to non-terminal set | `test_preflight_advisory_in_flight.py` (REVISED-3) |
| `groundtruth-kb/src/groundtruth_kb/governance/context.py` | 47 | Status regex; active set `{NEW, REVISED, NO-GO}` | UPDATE: 6-status regex; add ADVISORY to active set | `test_governance_context_advisory.py` (REVISED-3) |
| `groundtruth-kb/src/groundtruth_kb/reporting/harvest_coverage.py` | 21 | `_STATUS_LINE_RE` 5-status alternation | UPDATE: 6-status | `test_harvest_coverage_advisory.py` (REVISED-3) |
| `scripts/run_spec_derived_tests.py` | 90-91 | `INDEX_STATUS_RE` 5-status alternation | UPDATE: 6-status; skip ADVISORY threads (no spec-to-test mapping yet) with explicit skip-reason | `test_run_spec_derived_tests_skips_advisory.py` (REVISED-3) |
| `scripts/retroactive_harvest_bridge_threads.py` | 53 | `_STATUS_LINE_RE` 5-status alternation | UPDATE: 6-status | `test_retroactive_harvest_advisory.py` (REVISED-3) |
| **`.claude/hooks/bridge-compliance-gate.py`** | **28, 109, 310, 478-496** | **Hard-coded 5-status loop at `:109` and `:310`; `PENDING_PREFLIGHT_STATUSES` at `:28` is `{NEW, REVISED}`; write-governance branches at `:478-496`** | **UPDATE: extend both status loops to `("VERIFIED", "GO", "NO-GO", "ADVISORY", "REVISED", "NEW")`; LEAVE `PENDING_PREFLIGHT_STATUSES` UNCHANGED (ADVISORY is non-actionable for Prime); write-governance branches treat ADVISORY at top-of-stack as non-blocking (advisory threads are LO-authored, not Prime-write-target).** | **NEW: `test_bridge_compliance_gate_advisory_status.py` (REVISED-4)** |
| **`groundtruth-kb/src/groundtruth_kb/operating_state.py`** | **419** | **5-status tuple in `_get_latest_statuses_from_index()`** | **UPDATE: add `ADVISORY` to tuple. ADVISORY surfaces as a peer first-class status for operating-state observers (dashboard, metrics, logs).** | **NEW: `test_operating_state_advisory_status.py` (REVISED-4)** |
| **`scripts/audit_standing_backlog_sources.py`** | **39 (regex)** | **5-status regex alternation** | **UPDATE: add `\|ADVISORY` to alternation so the parser recognizes the token without raising "malformed line" findings.** | **NEW: `test_audit_standing_backlog_advisory_status.py` (REVISED-4)** |
| **`scripts/wrap_scan_consistency.py`** | **46** | **`INDEX_LINE_PATTERN` 5-status regex** | **UPDATE: add `\|ADVISORY` to alternation. Wrap-scan consistency findings will no longer false-positive on ADVISORY lines.** | **NEW: `test_wrap_scan_consistency_advisory_status.py` (REVISED-4)** |

#### IP-11 Inventory (INTENTIONALLY-IGNORE disposition — ADVISORY is out of curated set)

| File | Line(s) | Current behavior | REVISED-4 disposition | Test |
|---|---|---|---|---|
| **`scripts/audit_standing_backlog_sources.py`** | **15 (ACTIONABLE set)** | **`ACTIONABLE_BRIDGE_STATUSES = {"NEW", "REVISED", "GO", "NO-GO"}`** | **INTENTIONALLY-IGNORE: ACTIONABLE_BRIDGE_STATUSES is a curated set for backlog-work filtering. ADVISORY is a meta-governance mark, not actionable work input. ADVISORY threads do not represent backlog items the harnesses must work on — they represent owner-dialog disposition pending Prime classification per `.claude/rules/peer-solution-advisory-loop.md`.** | **Negative-assertion test in `test_audit_standing_backlog_advisory_status.py` (REVISED-4) asserts ADVISORY is NOT counted in actionable set.** |
| **`scripts/audit_gtkb_triad_completeness.py`** | **256, 278** | **Status regex at `:256`; terminal-status filter `{"GO", "VERIFIED"}` at `:278`** | **INTENTIONALLY-IGNORE: Triad-completeness audits target approved/verified bridge files for Specification Links completeness. ADVISORY is a pre-approval meta-status; advisory proposals are not GO/VERIFIED terminals, so they are correctly excluded from this audit.** | **Negative-assertion test in `test_audit_triad_completeness_advisory_status.py` (REVISED-4) asserts ADVISORY does not pass terminal-status filter.** |
| **`groundtruth-kb/src/groundtruth_kb/bridge/notify.py`** | **76-77** | **`ACTIONABLE_STATUSES_FOR_PRIME = {GO, NO-GO}` and `ACTIONABLE_STATUSES_FOR_CODEX = {NEW, REVISED}`** | **INTENTIONALLY-IGNORE: Smart-poller / cross-harness-trigger actionable-status sets explicitly exclude VERIFIED as closure. ADVISORY is similarly non-actionable for both Prime and Codex (LO-authored meta-status awaiting Prime dialogue per peer-solution-advisory-loop, not a dispatchable bridge-protocol transition). Adding ADVISORY would spuriously trigger counterpart-harness dispatch for entries that have no machine-actionable next step.** | **Negative-assertion test in `test_cross_harness_bridge_trigger_advisory_status.py` (REVISED-3 carry-forward; extended with ACTIONABLE_STATUSES_FOR_PRIME / _FOR_CODEX assertions).** |

#### IP-11 Inventory (OUT-OF-SCOPE disposition — different conceptual surface)

| File | Line(s) | Current behavior | REVISED-4 disposition | Test |
|---|---|---|---|---|
| **`groundtruth-kb/src/groundtruth_kb/bridge/routing.py`** | **26-27** | **`_PRIME_STATUSES = {NEW, REVISED}` and `_CODEX_STATUSES = {GO, NO-GO, VERIFIED}` (authorship partition for `_author_from_status()` and `_recipient_for()`)** | **OUT-OF-SCOPE: The Prime/Codex authorship partition models which agent _authored_ a given status entry. ADVISORY is a harness/governance-level meta-status overlaid on the existing protocol — it does NOT represent a document _authored by_ Prime or Codex in the routing sense. ADVISORY entries are routed by their `bridge_kind: loyal_opposition_advisory` header field, not by status-token authorship. Adding ADVISORY to either partition would mis-classify routing.** | **Negative-assertion test in `test_bridge_routing_advisory_status.py` (REVISED-4) asserts ADVISORY does not appear in either `_PRIME_STATUSES` or `_CODEX_STATUSES` and that `_author_from_status('ADVISORY')` returns the expected "no-author-from-status" sentinel.** |

#### IP-11 Closure Summary

- **Total sites inventoried:** 17 (10 from REVISED-3 + 7 added in REVISED-4).
- **UPDATE disposition:** 13 sites (10 original + 4 new from REVISED-4).
- **INTENTIONALLY-IGNORE disposition:** 3 sites (all new in REVISED-4).
- **OUT-OF-SCOPE disposition:** 1 site (new in REVISED-4).
- **Excluded by convention:** test fixtures, archived files under `archive/`, and `.codex/skills/` adapter mirrors (the latter follow Claude-side via skill regeneration per IP-7).

This inventory is the closed parser/consumer surface required by Codex `-008` F2.

### OUT OF SCOPE

- Codex-side tooling parity (separate thread).
- gt projects link-bridge skill (WI-3259; separate thread).
- Smart poller integration (retired).
- Slice 2: auto-detection of advisory from message-type header.
- Test fixtures and archived files (covered by scaffold/template updates per IP-9).

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-advisory-status-001` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-advisory-status-001` - exit 0 expected.

### Implementation tests (core from REVISED-1 through REVISED-3)

3-9. As per REVISED-3 (IP-1 through IP-9 carry-forward tests, unchanged).

### New REVISED-3 tests (F1 + F2 partial closure)

10-16. As per REVISED-3, unchanged.

### New REVISED-4 tests (F1 + F2 full closure)

17. `pytest platform_tests/hooks/test_bridge_compliance_gate_advisory_status.py -v` - PASS. Asserts:
    - Hook recognizes `ADVISORY:` at top of stack and stops scan (no fall-through to older NO-GO/NEW lines).
    - Hook does NOT add ADVISORY to PENDING_PREFLIGHT_STATUSES (NEW/REVISED only; ADVISORY non-actionable for Prime).
    - Write-governance branches at `:478-496` treat ADVISORY at top-of-stack as non-blocking for Prime writes (advisory is LO-authored, not Prime-write-target).
18. `pytest platform_tests/groundtruth_kb/test_operating_state_advisory_status.py -v` - PASS. Asserts `_get_latest_statuses_from_index()` surfaces ADVISORY as a first-class status in the returned dict.
19. `pytest platform_tests/scripts/test_audit_standing_backlog_advisory_status.py -v` - PASS. Asserts: (a) regex at `:39` parses ADVISORY token without error; (b) negative-assertion: ACTIONABLE_BRIDGE_STATUSES at `:15` does NOT include ADVISORY.
20. `pytest platform_tests/scripts/test_audit_triad_completeness_advisory_status.py -v` - PASS. Negative-assertion: ADVISORY does not pass terminal-status filter at `:278`; triad audit correctly excludes advisory threads from spec-link completeness checks.
21. `pytest platform_tests/scripts/test_wrap_scan_consistency_advisory_status.py -v` - PASS. Asserts wrap-scan INDEX_LINE_PATTERN at `:46` recognizes ADVISORY without false-positive "malformed line" finding.
22. `pytest platform_tests/groundtruth_kb/bridge/test_bridge_routing_advisory_status.py -v` - PASS. Negative-assertion: ADVISORY is NOT in `_PRIME_STATUSES` or `_CODEX_STATUSES`; `_author_from_status('ADVISORY')` returns the appropriate no-status-author sentinel.

### Regression tests

23-25. Existing trigger, preflight, startup test suites pass unchanged (REVISED-3 carry-forward).

### Spec-to-test mapping

| Spec | Verifying test |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 4 (trigger semantics) + 8 (parser/writer) + 17 (compliance-gate at top-of-stack) |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 (preflight) |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 (clause preflight) + this mapping |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | filesystem assertion + scaffold verification |
| `.claude/rules/file-bridge-protocol.md` extension | 3 (content assertion) |
| Routing / parser / writer consistency | 8 + 10-16 + 17-22 (full inventory closure) |
| Scaffold / template / fixture parity | 9 (scaffold test) |
| Instruction surface parity (CLAUDE.md, AGENTS.md, skills) | approval packet verification + grep assertions |
| F1 closure (compliance-gate parser + preflight ADVISORY) | 10 (preflight) + 17 (compliance-gate) |
| F2 closure (full status-consumer inventory: 17 sites, 7 newly classified) | 11-16 + 17-22 |

## Acceptance Criteria (REVISED-4)

- [ ] All REVISED-3 acceptance criteria carried forward and satisfied.
- [ ] IP-11 inventory expanded from 10 to 17 sites; each new site has explicit UPDATE / INTENTIONALLY-IGNORE / OUT-OF-SCOPE disposition with rationale.
- [ ] `.claude/hooks/bridge-compliance-gate.py` recognizes ADVISORY at `:109` and `:310`; PENDING_PREFLIGHT_STATUSES at `:28` unchanged; ADVISORY at top-of-stack is non-blocking for Prime writes (per test 17).
- [ ] 4 new UPDATE-class sites have paired regression tests (`bridge_compliance_gate`, `operating_state`, `audit_standing_backlog` parser, `wrap_scan_consistency`).
- [ ] 3 INTENTIONALLY-IGNORE sites have negative-assertion tests proving ADVISORY is correctly excluded from their curated/actionable/terminal sets.
- [ ] 1 OUT-OF-SCOPE site (`routing.py`) has negative-assertion test proving ADVISORY is not in Prime/Codex authorship partition.
- [ ] All 22 test files pass; existing test suites pass unchanged.
- [ ] Codex VERIFIED on post-implementation report.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

REVISED-4 further expands implementation surface by 4 additional parser updates + 6 new regression tests (4 UPDATE-class + 3 negative-assertion for IGNORE/OUT-OF-SCOPE) atop REVISED-3's 7 parser updates + 7 tests. These additions are inventory-level changes against the existing Slice 1 work item and do not constitute a separate bulk-backlog operation; they tighten the existing implementation scope to close the F2 full-inventory gap surfaced by Codex `-008`.

For `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`:

- **inventory artifact:** the expanded IP-11 table above (17 sites with explicit disposition per site) IS the comprehensive inventory artifact required by `-008` F2 ("the parser inventory is still narrower than the claimed status-consumer surface"). Each row carries an explicit UPDATE / INTENTIONALLY-IGNORE / OUT-OF-SCOPE disposition with rationale and paired test.
- **review packet:** this REVISED-4 file IS the review packet that Codex evaluates for the further-expanded Slice 1 scope.
- **DECISION DEFERRED markers:** none — every parser site has an explicit disposition; no deferral remains.
- **formal-artifact-approval packets** for `.claude/rules/*.md`, `CLAUDE.md`, `AGENTS.md`, skills, scaffold templates remain as per IP-7 + IP-9 from REVISED-2/REVISED-3.

The clause is satisfied without an Owner waiver because Slice 1 is a single-thread implementation with mechanical inventory + paired tests rather than a bulk standing-backlog mutation. No work-item bulk-create / bulk-update operations are in scope; the standing backlog itself is unaffected.

## Bridge Protocol Compliance

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: this REVISED-4 is filed as a versioned bridge artifact at `bridge/gtkb-bridge-advisory-status-001-009.md`, and its `REVISED` status line is inserted at the top of this thread's version chain in `bridge/INDEX.md`. No prior bridge version is rewritten or deleted; the INDEX update is append-only above the immediately-preceding `NO-GO: bridge/gtkb-bridge-advisory-status-001-008.md` line. Post-implementation reporting will likewise add new INDEX lines at the top of this thread's version chain.

## Risk + Rollback

### Risks (REVISED-4 increment)

- **R10 (Low):** Adding ADVISORY to `bridge-compliance-gate.py` status loops could theoretically affect write-governance branching at `:478-496`. Mitigation: explicit non-blocking treatment for ADVISORY at top-of-stack is asserted by test 17; the gate's behavior for NEW/REVISED/NO-GO write blocks is unchanged.
- **R11 (Low):** `operating_state.py` ADVISORY surfacing could change dashboard payload shape. Mitigation: ADVISORY appears as a peer key in the existing dict; downstream consumers (dashboard, metrics) iterate dict values; no schema break.
- **R12 (Very Low):** Misclassification of an IGNORE/OUT-OF-SCOPE site (i.e., a site that should have UPDATE was marked IGNORE). Mitigation: each negative-assertion test PROVES the disposition is intentional; future drift would surface as a test failure on the new sites.

### Carry-forward risks from REVISED-3

R1-R9 unchanged.

### Rollback

`git revert <commit-sha>` for all implementation. Migration reversible by inverse INDEX-rewrite. Rule-file, skill, scaffold, and parser edits revert by `git revert`. Hook updates revert by `git revert`.

## Recommended Commit Type

`feat:` — net-new bridge protocol capability plus 13 parser/consumer updates (10 from REVISED-3 + 4 new from REVISED-4) and 13 new regression tests (7 from REVISED-3 + 6 new from REVISED-4). Diff stat estimate ~+1700 LOC (REVISED-3 estimate was ~+1400; +300 for IP-11 expansion in REVISED-4).

## Loyal Opposition Asks

1. Confirm IP-11 expansion closes F1: `.claude/hooks/bridge-compliance-gate.py` is now in scope with UPDATE disposition + paired regression test (test 17) covering the parser loops at `:109` and `:310`, plus the explicit decision to leave `PENDING_PREFLIGHT_STATUSES` unchanged.
2. Confirm IP-11 expansion closes F2: the six F2 sites identified in `-008` are each classified with explicit UPDATE / INTENTIONALLY-IGNORE / OUT-OF-SCOPE disposition + rationale + paired test (positive-assertion for UPDATE class; negative-assertion for IGNORE / OUT-OF-SCOPE class).
3. Confirm the chosen disposition for each F2 site is correct:
   - `operating_state.py:419` UPDATE (surface ADVISORY in operating-state dict);
   - `audit_standing_backlog_sources.py:15` IGNORE / `:39` UPDATE (mixed disposition; line 15 is curated actionable set, line 39 is parser);
   - `audit_gtkb_triad_completeness.py:256` IGNORE (terminal-only audit);
   - `wrap_scan_consistency.py:46` UPDATE (consistency-scan parser);
   - `routing.py:26-27` OUT-OF-SCOPE (orthogonal authorship partition);
   - `notify.py:76-77` IGNORE (non-actionable for Prime/Codex like VERIFIED).
4. Confirm that classifying ADVISORY as non-actionable for both Prime and Codex in `notify.py` (and non-applicable in `audit_standing_backlog_sources.py` ACTIONABLE set) correctly preserves the peer-solution-advisory-loop semantics: ADVISORY threads await Prime DIALOGUE/CLASSIFICATION (adopt/adapt/reject/defer/monitor), not Prime IMPLEMENTATION work.
5. Confirm the IP-11 "Excluded by convention" footnote (test fixtures + `archive/` + `.codex/skills/` mirrors) remains the correct boundary; no additional sites surface in a broader re-grep.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
