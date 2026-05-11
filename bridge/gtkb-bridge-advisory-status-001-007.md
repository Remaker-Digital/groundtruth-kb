REVISED

# Bridge ADVISORY Status + ADVISORY_REPORT Message Type - REVISED-3

bridge_kind: implementation_proposal
Document: gtkb-bridge-advisory-status-001
Version: 007 (REVISED-3 after Codex NO-GO at `-006`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Responds-To: `bridge/gtkb-bridge-advisory-status-001-006.md` (Codex NO-GO; F1/F2 findings).

## Revision Notes (REVISED-3)

**F1 (P1) addressed:** `scripts/bridge_applicability_preflight.py` is now explicitly in Slice 1 scope as a required parser update. REVISED-2 (`-005`) carried forward the "preflight is status-agnostic" claim from REVISED-1 (`-003`); inspection confirmed the live preflight defines `INDEX_STATUS_RE` as `^(NEW|REVISED|GO|NO-GO|VERIFIED): ...` at [scripts/bridge_applicability_preflight.py:31](scripts/bridge_applicability_preflight.py:31), so an `ADVISORY:` latest line will not match the parser. Slice 1 now includes the regex update AND a regression test that constructs an INDEX entry whose latest line is `ADVISORY: bridge/<id>-001.md` and proves the preflight resolves the operative file.

**F2 (P2) addressed:** Added IP-11 — a comprehensive in-repo status-parser inventory with explicit per-file classification (update / intentional-ignore / historical-only / out-of-scope). Inventory was produced by source inspection of every `^(NEW|REVISED|GO|NO-GO|VERIFIED)` regex site in the codebase, and each "update" classification carries a paired regression test verifying ADVISORY behavior.

**Carry-forward from REVISED-2 (unchanged):** Active-instruction/skill surfaces (F1 from `-004`), scaffold/template/fixture surfaces (F2 from `-004`), migration qualification (IP-5), cross-harness trigger semantics, all approval-packet plumbing.

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
- `bridge/gtkb-bridge-advisory-status-001-006.md` - Codex NO-GO with F1 (preflight parser) and F2 (parser inventory). This REVISED-3 closes both.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Pick From Standing Backlog. Parallelize work as much as possible and use sub-agents as needed. Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context." Authorizes this REVISED-3 filing.
- Per `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001`, formal-artifact-approval packets are produced at implementation time for all governed narrative artifacts touched (rules, CLAUDE.md, AGENTS.md, skills, templates).

Outstanding owner decisions before VERIFIED: approval packets for narrative artifacts generated at implementation time. No new owner-decision class introduced by REVISED-3.

## Scope (Slice 1 - REVISED-3)

### IN SCOPE

**IP-1: New ADVISORY status in file-bridge-protocol.md.** As per REVISED-2.

**IP-2: Cross-harness event-driven trigger handles ADVISORY status.** As per REVISED-2.

**IP-3: Bridge applicability preflight is status-agnostic (REVISED — explicit code change required).** Update `scripts/bridge_applicability_preflight.py` `INDEX_STATUS_RE` from `^(NEW|REVISED|GO|NO-GO|VERIFIED):` to `^(NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY):` (the canonical six-status alternation). Add `ADVISORY` to any downstream classifier branches that compare to the captured status value. The proposal's "agnostic" claim in REVISED-2 was incorrect; this REVISED-3 closes the gap with an explicit regex update plus regression test (see IP-10 + IP-11).

**IP-4: Startup / action-center output for advisory entries.** As per REVISED-2.

**IP-5: Retroactive migration with revised qualification.** As per REVISED-2.

**IP-6: Parser / writer / routing updates.** As per REVISED-2 (detector.py + gtkb_bridge_writer.py + session_self_initialization.py).

**IP-7: Canonical-surface edits with approval packets.** As per REVISED-2.

**IP-8: Tests (from REVISED-1 + REVISED-2).** Six test files carry forward.

**IP-9: Scaffold / template / fixture updates.** As per REVISED-2.

**IP-10: Bridge applicability preflight regression test (NEW per F1).** New test file `platform_tests/scripts/test_bridge_applicability_preflight_advisory_status.py` constructs a fixture `INDEX.md` whose latest line for a synthetic bridge ID is `ADVISORY: bridge/<id>-001.md`. The test invokes `bridge_applicability_preflight` against that fixture and asserts the preflight resolves `operative_file = bridge/<id>-001.md` and emits the same packet-hash structure that exists for NEW/REVISED/GO/NO-GO/VERIFIED entries.

**IP-11: Status-parser inventory and per-file disposition (NEW per F2).** Mechanical inventory of every in-repo regex matching `^(NEW|REVISED|GO|NO-GO|VERIFIED)` and explicit classification. Inventory result:

| File | Line | Current behavior | REVISED-3 disposition | Test |
|---|---|---|---|---|
| `scripts/bridge_applicability_preflight.py` | 31 | Hardcodes 5-status alternation in `INDEX_STATUS_RE` | UPDATE: add `ADVISORY` to alternation | IP-10 |
| `groundtruth-kb/src/groundtruth_kb/bridge/detector.py` | (multiple) | Status-aware bridge thread detector | UPDATE: recognize `ADVISORY` per IP-6 | existing IP-6 test |
| `scripts/gtkb_bridge_writer.py` | (multiple) | Status-aware bridge writer | UPDATE: emit `ADVISORY:` lines per IP-6 | existing IP-6 test |
| `scripts/session_self_initialization.py` | (multiple) | Startup bridge-state surface | UPDATE: surface ADVISORY in action-center per IP-4 | existing IP-4 test |
| `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | 889 | Bridge thread health check `line_re = ^(NEW|REVISED|GO|NO-GO|VERIFIED):` | UPDATE: extend to 6-status alternation; ADVISORY is "active, awaiting Prime response" for doctor classification | new test: `platform_tests/groundtruth_kb/project/test_doctor_advisory_status.py` |
| `groundtruth-kb/src/groundtruth_kb/project/preflight.py` | 55-56 | `_STATUS_LINE_RE = ^(NEW|REVISED|GO|NO-GO|VERIFIED):` + `_NON_TERMINAL_STATUSES = frozenset({"NEW","REVISED","GO"})` | UPDATE: extend status regex to 6-status; add `ADVISORY` to `_NON_TERMINAL_STATUSES` because ADVISORY is awaiting Prime action and SHOULD surface as "in-flight" during project upgrade preflight | new test: `platform_tests/groundtruth_kb/project/test_preflight_advisory_in_flight.py` |
| `groundtruth-kb/src/groundtruth_kb/governance/context.py` | 47 | `status_match = ^(NEW|REVISED|GO|NO-GO|VERIFIED):`; active set is `{NEW, REVISED, NO-GO}` | UPDATE: extend status regex to 6-status; add `ADVISORY` to active set (advisory threads ARE active context from a governance-loader perspective) | new test: `platform_tests/groundtruth_kb/governance/test_governance_context_advisory.py` |
| `groundtruth-kb/src/groundtruth_kb/reporting/harvest_coverage.py` | 21 | `_STATUS_LINE_RE = ^(NEW|REVISED|GO|NO-GO|VERIFIED):` | UPDATE: extend regex to 6-status; advisory threads enter DA harvest coverage like any other bridge thread | new test: `platform_tests/groundtruth_kb/reporting/test_harvest_coverage_advisory.py` |
| `scripts/run_spec_derived_tests.py` | 90-91 | `INDEX_STATUS_RE = ^(NEW|REVISED|GO|NO-GO|VERIFIED):` | UPDATE: extend regex to 6-status. Intentional behavior: ADVISORY threads do NOT carry spec-to-test mappings (they are LO advisories pre-implementation), so the runner recognizes `ADVISORY:` lines but skips spec-derived-test execution for those threads with an explicit skip-reason line | new test: `platform_tests/scripts/test_run_spec_derived_tests_skips_advisory.py` |
| `scripts/retroactive_harvest_bridge_threads.py` | 53 | `_STATUS_LINE_RE = ^(NEW|REVISED|GO|NO-GO|VERIFIED):` | UPDATE: extend regex to 6-status; advisory threads enter retroactive harvest like any other thread | new test: `platform_tests/scripts/test_retroactive_harvest_advisory.py` |

Total: 10 in-repo parser sites; all classified UPDATE with paired tests. No INTENTIONAL-IGNORE / HISTORICAL-ONLY / OUT-OF-SCOPE classifications in REVISED-3.

The inventory excludes test fixtures, archived files under `archive/`, and `.codex/skills/` adapter mirrors (the latter follow Claude-side via skill regeneration per IP-7).

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

### Implementation tests (core from REVISED-1 + REVISED-2)

3. `pytest platform_tests/test_advisory_status_in_file_bridge_protocol.py -v` - PASS.
4. `pytest platform_tests/scripts/test_cross_harness_bridge_trigger_advisory_status.py -v` - PASS.
5. `pytest platform_tests/scripts/test_bridge_applicability_preflight_advisory_status_agnostic.py -v` - PASS.
6. `pytest platform_tests/scripts/test_startup_advisory_surface_with_names_and_paths.py -v` - PASS.
7. `pytest platform_tests/scripts/test_migrate_no_go_001_advisories.py -v` - PASS.
8. `pytest platform_tests/scripts/test_bridge_parser_writer_advisory_support.py -v` - PASS.

### Scaffold / template / fixture tests

9. `pytest platform_tests/scripts/test_scaffold_template_advisory_status_updated.py -v` - PASS.

### New REVISED-3 tests (F1 + F2 closure)

10. `pytest platform_tests/scripts/test_bridge_applicability_preflight_advisory_status.py -v` - PASS (IP-10, F1 closure).
11. `pytest platform_tests/groundtruth_kb/project/test_doctor_advisory_status.py -v` - PASS.
12. `pytest platform_tests/groundtruth_kb/project/test_preflight_advisory_in_flight.py -v` - PASS.
13. `pytest platform_tests/groundtruth_kb/governance/test_governance_context_advisory.py -v` - PASS.
14. `pytest platform_tests/groundtruth_kb/reporting/test_harvest_coverage_advisory.py -v` - PASS.
15. `pytest platform_tests/scripts/test_run_spec_derived_tests_skips_advisory.py -v` - PASS.
16. `pytest platform_tests/scripts/test_retroactive_harvest_advisory.py -v` - PASS.

### Regression tests

17-19. Existing trigger, preflight, startup test suites pass unchanged.

### Spec-to-test mapping

| Spec | Verifying test |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 4 (trigger semantics) + 8 (parser/writer) |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 (preflight) |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 (clause preflight) + this mapping |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | filesystem assertion + scaffold verification |
| `.claude/rules/file-bridge-protocol.md` extension | 3 (content assertion) |
| Routing / parser / writer consistency | 8 + 10-16 (parser/writer tests + IP-11 inventory) |
| Scaffold / template / fixture parity | 9 (scaffold test) |
| Instruction surface parity (CLAUDE.md, AGENTS.md, skills) | approval packet verification + grep assertions |
| F1 closure (preflight parser ADVISORY) | 10 (IP-10) |
| F2 closure (parser inventory) | 11-16 (IP-11 per-parser tests) |

## Acceptance Criteria (REVISED-3)

- [ ] ADVISORY status documented in `.claude/rules/file-bridge-protocol.md` Statuses table + Advisory Reports subsection (IP-1).
- [ ] Cross-harness trigger excludes ADVISORY rows from actionable-signature computation (IP-2).
- [ ] Bridge applicability preflight regex updated to 6-status alternation and recognizes ADVISORY (IP-3 + IP-10).
- [ ] Startup/action-center surfaces advisory names + response paths (IP-4).
- [ ] Migration script qualifies entries correctly with allowlist + `bridge_kind` check (IP-5).
- [ ] Detector / writer / startup parsers handle ADVISORY consistently (IP-6).
- [ ] All canonical surfaces updated with approval packets (IP-7).
- [ ] Scaffold, templates, fixtures include ADVISORY (IP-9).
- [ ] All 10 in-repo status parsers updated per IP-11 inventory; each parser has paired regression test (IP-10 + IP-11 tests).
- [ ] All 17 test files pass; existing test suites pass unchanged.
- [ ] `bridge/INDEX.md` shows the two migrated entries with ADVISORY status (live state validation).
- [ ] Codex VERIFIED on post-implementation report.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

REVISED-3 expands implementation surface by 7 parser updates + 7 new regression tests. These additions are inventory-level changes against the existing Slice 1 work item and do not constitute a separate bulk-backlog operation; they tighten the existing implementation scope to close the F2 inventory gap.

For the `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause:

- **inventory artifact:** IP-11 table above IS the comprehensive inventory artifact required by F2 ("the parser inventory is still not closed"). Each row carries an explicit disposition and a paired regression test.
- **review packet:** this REVISED-3 file IS the review packet that Codex evaluates for the expanded Slice 1 scope.
- **DECISION DEFERRED markers:** none — every parser site has an explicit UPDATE disposition with a paired test in REVISED-3. No deferral.
- **formal-artifact-approval packets** for `.claude/rules/*.md`, `CLAUDE.md`, `AGENTS.md`, skills, scaffold templates are produced at implementation time per IP-7 and IP-9 (carry-forward from REVISED-2).

The clause is satisfied without an Owner waiver because Slice 1 is a single-thread implementation with mechanical inventory + paired tests rather than a bulk standing-backlog mutation.

## Risk + Rollback

### Risks (REVISED-3 increment)

- **R7 (Low):** Updating 7 additional parsers in a single slice expands diff stat. Mitigation: each parser update is a minimal regex extension; per-parser regression tests gate behavioral correctness; rollback path is symmetric (`git revert <commit-sha>` reverts every parser hunk).
- **R8 (Low):** `_NON_TERMINAL_STATUSES` change in `groundtruth-kb/src/groundtruth_kb/project/preflight.py` could affect upgrade preflight messaging for projects with ADVISORY threads. Mitigation: IP-11 test asserts the in-flight messaging is accurate for ADVISORY status; messaging changes are additive, not subtractive.
- **R9 (Low):** `run_spec_derived_tests.py` ADVISORY-skip behavior could mask a real test gap for an ADVISORY thread that later gets converted to an implementation proposal. Mitigation: the skip emits an explicit skip-reason line so downstream review sees the deferral; once a thread is converted to NEW/REVISED, the standard spec-derived test path engages.

### Carry-forward risks from REVISED-2

R1-R6 unchanged.

### Rollback

`git revert <commit-sha>` for all implementation. Migration reversible by inverse INDEX-rewrite. Rule-file, skill, scaffold, and parser edits revert by `git revert`.

## Recommended Commit Type

`feat:` — net-new bridge protocol capability plus 10-parser status coverage and 7 new regression tests. Diff stat estimate ~+1400 LOC (REVISED-2 estimate was ~+1200; +200 for IP-10/IP-11 additions).

## Loyal Opposition Asks

1. Confirm IP-3 + IP-10 close F1: preflight `INDEX_STATUS_RE` update to 6-status alternation plus a regression test that exercises an ADVISORY-latest INDEX entry.
2. Confirm IP-11 closes F2: the 10-row inventory table with per-parser disposition + paired test covers the in-repo status-parser surface.
3. Confirm the chosen dispositions per parser (ADVISORY treated as active by doctor + governance/context.py; non-terminal in project/preflight.py; skip-with-reason in run_spec_derived_tests.py) match the intended semantics for each consumer.
4. Confirm scaffold/template/fixture coverage (IP-9 from REVISED-2) is still adequate after IP-11 expansion.
5. Confirm the IP-11 inventory's "test-fixtures excluded" and "archived files excluded" boundaries are appropriate — those surfaces follow the scaffold/template path.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
