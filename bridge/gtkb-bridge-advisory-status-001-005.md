REVISED

# Bridge ADVISORY Status + ADVISORY_REPORT Message Type - REVISED-2

bridge_kind: implementation_proposal
Document: gtkb-bridge-advisory-status-001
Version: 005 (REVISED-2 post NO-GO at -004)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341

## Revision Notes (REVISED-2)

**F1 (P1) Active Instruction And Skill Surfaces addressed:** Slice 1 now includes full scope of active root/harness instruction and generated skill surfaces. Added to touchpoints: `CLAUDE.md` (update Review/Verify/GO/NO-GO/Verified statement and ADVISORY description), `AGENTS.md` (extend Loyal Opposition actionability to ADVISORY; define non-dispatchable and owner-dialog nature), `.claude/skills/bridge/SKILL.md` and `.codex/skills/bridge/SKILL.md` (update lifecycle model to include ADVISORY status; define as Loyal Opposition-authored non-dispatchable). IP-7 expanded to include skill-text regeneration and narrative-artifact-approval packets for both harness skills (skill definitions are governed surfaces per operating-model). These amendments prevent fresh harness sessions and skill-driven bridge operations from applying the old five-state model.

**F2 (P2) Scaffold And Template Surfaces addressed:** Slice 1 now includes the platform scaffold, templates, and baseline test fixtures that carry the bridge vocabulary into new installs. Added to IP-7 and touchpoints: `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` (update five-status hardcode to six-status including ADVISORY), `groundtruth-kb/templates/rules/canonical-terminology.md` (update bridge-status vocabulary), `groundtruth-kb/tests/test_bridge_detector.py` and `groundtruth-kb/tests/fixtures/bridge_index_live_snapshot.md` (update fixture headers to include ADVISORY). New implementation item IP-9 created for scaffold/template updates; new test added to platform_tests: `test_scaffold_template_advisory_status_updated.py`.

**From REVISED-1 (unchanged):** Migration qualification (IP-5), parser/writer/routing updates (IP-6), canonical-surface edits with approval packets (core surfaces per REVISED-1 IP-7), cross-harness trigger semantics, preflight agnosticism. All counts and test references carry forward from REVISED-1 unless explicitly revised above.

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
- NO-GO at -004 (F1: active instruction surfaces; F2: scaffold/templates) - addressed in this revision.

## Owner Decisions / Input

This proposal cites the S341 autonomous-execution directive and the standing owner approval:

- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog" + "Please continue with items 1-5". Authorizes REVISED-2 filing.
- Per `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001` (S341 F1 salience-gap lesson), formal-artifact-approval packets will be produced as part of implementation for all governed narrative artifacts touched.

Outstanding owner decisions before VERIFIED: approval packets for narrative artifacts (CLAUDE.md, AGENTS.md, skills, rules, templates) generated at implementation time.

## Scope (Slice 1 - REVISED)

### IN SCOPE

**IP-1: New ADVISORY status in file-bridge-protocol.md.** As per REVISED-1.

**IP-2: Cross-harness event-driven trigger handles ADVISORY status.** As per REVISED-1.

**IP-3: bridge-applicability-preflight handles ADVISORY status.** As per REVISED-1.

**IP-4: Startup / action-center output for advisory entries.** As per REVISED-1.

**IP-5: Retroactive migration with revised qualification.** As per REVISED-1.

**IP-6: Parser / writer / routing updates.** As per REVISED-1.

**IP-7: Canonical-surface edits with approval packets (REVISED - scope expanded).** Core surfaces from REVISED-1 plus active instruction and skill surfaces:

- `.claude/rules/bridge-essential.md` - extend status description.
- `.claude/rules/canonical-terminology.md` - expand "Loyal Opposition advisory" entry.
- `.claude/rules/operating-model.md` - update protocol-state description.
- `config/agent-control/system-interface-map.toml` - update status vocabulary.
- `CLAUDE.md` - update Review/Verify transition language and ADVISORY definition.
- `AGENTS.md` - add ADVISORY actionability exception for Loyal Opposition; define non-dispatchable nature.
- `.claude/skills/bridge/SKILL.md` - update lifecycle model; define ADVISORY as Loyal Opposition-authored, non-dispatchable.
- `.codex/skills/bridge/SKILL.md` - update lifecycle model; define ADVISORY as non-dispatchable.

Formal-artifact-approval packets required for each protected narrative artifact.

**IP-8: Tests (from REVISED-1).** Six test files per REVISED-1 carry forward.

**IP-9: Scaffold / template / fixture updates (NEW).**

- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` - update five-status hardcode to include ADVISORY.
- `groundtruth-kb/templates/rules/canonical-terminology.md` - update status vocabulary.
- `groundtruth-kb/tests/test_bridge_detector.py` - add ADVISORY to detector tests.
- `groundtruth-kb/tests/fixtures/bridge_index_live_snapshot.md` - add ADVISORY to fixture headers.
- New test: `platform_tests/scripts/test_scaffold_template_advisory_status_updated.py`.

### OUT OF SCOPE

- Codex-side tooling parity (separate thread).
- gt projects link-bridge skill (WI-3259; separate thread).
- Smart poller integration (retired).
- Slice 2: auto-detection of advisory from message-type header.

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-advisory-status-001` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-advisory-status-001` - exit 0 expected.

### Implementation tests (core from REVISED-1)

3. `pytest platform_tests/test_advisory_status_in_file_bridge_protocol.py -v` - PASS.
4. `pytest platform_tests/scripts/test_cross_harness_bridge_trigger_advisory_status.py -v` - PASS.
5. `pytest platform_tests/scripts/test_bridge_applicability_preflight_advisory_status_agnostic.py -v` - PASS.
6. `pytest platform_tests/scripts/test_startup_advisory_surface_with_names_and_paths.py -v` - PASS.
7. `pytest platform_tests/scripts/test_migrate_no_go_001_advisories.py -v` - PASS.
8. `pytest platform_tests/scripts/test_bridge_parser_writer_advisory_support.py -v` - PASS.

### New tests (F1 + F2 coverage)

9. `pytest platform_tests/scripts/test_scaffold_template_advisory_status_updated.py -v` - PASS. Scaffold, templates, fixtures include ADVISORY in six-status vocabulary.

### Regression tests

10-12. Existing trigger, preflight, startup test suites pass unchanged.

### Spec-to-test mapping

| Spec | Verifying test |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 4 (trigger semantics) + 8 (parser/writer) |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 (preflight) |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 (clause preflight) + this mapping |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | filesystem assertion + scaffold verification |
| `.claude/rules/file-bridge-protocol.md` extension | 3 (content assertion) |
| Routing / parser / writer consistency | 8 (parser/writer tests) |
| Scaffold / template / fixture parity | 9 (new comprehensive test) |
| Instruction surface parity (CLAUDE.md, AGENTS.md, skills) | approval packet verification + grep assertions |

## Acceptance Criteria

- [ ] ADVISORY status documented in `.claude/rules/file-bridge-protocol.md` Statuses table + Advisory Reports subsection (IP-1).
- [ ] Cross-harness trigger excludes ADVISORY rows from actionable-signature computation (IP-2).
- [ ] Preflight is status-agnostic (IP-3).
- [ ] Startup/action-center surfaces advisory names + response paths (IP-4).
- [ ] Migration script qualifies entries correctly with allowlist + `bridge_kind` check (IP-5).
- [ ] Parser/writer/routing handle ADVISORY consistently (IP-6).
- [ ] All canonical surfaces updated with approval packets: core rules, CLAUDE.md, AGENTS.md, skills, templates (IP-7, IP-9).
- [ ] Scaffold, templates, fixtures include ADVISORY in bridge status vocabulary (IP-9).
- [ ] All 7 test files pass (6 from REVISED-1 + 1 new scaffold test); existing test suites pass.
- [ ] bridge/INDEX.md shows the two migrated entries with ADVISORY status (live state validation).
- [ ] Codex VERIFIED on post-implementation report.

## Risk + Rollback

### Risks

- **R1 (Low):** Tooling that parses INDEX may not recognize ADVISORY. Mitigation: this proposal updates all in-scope consumers including scaffold.
- **R2 (Low):** Migration script mis-identifies a non-advisory entry. Mitigation: allowlist + `bridge_kind` check prevents false positives.
- **R3 (Low):** New startup KPI field breaks existing consumers. Mitigation: additive field; unknown fields ignored.
- **R4 (Negligible):** Approval packet construction fails. Mitigation: standard process; deterministic hashing.
- **R5 (Low):** Skill regeneration fails or creates syntax errors. Mitigation: standard skill-authoring process; tests verify syntax.
- **R6 (Low):** Platform scaffold changes break new installs. Mitigation: comprehensive test coverage; regression tests on scaffold output.

### Rollback

`git revert <commit-sha>` for all implementation. Migration reversible by inverse INDEX-rewrite. Rule-file, skill, scaffold edits revert by `git revert`.

## Recommended Commit Type

`feat:` - net-new bridge protocol capability plus platform distribution updates. Diff stat ~+1200 LOC.

## Loyal Opposition Asks

1. Confirm Slice 1 scope now covers all in-repo bridge status parsers, writers, notification/routing, startup parsers, canonical surfaces, active instruction surfaces (CLAUDE.md, AGENTS.md), skills, scaffold, templates, and approval packets.
2. Confirm migration allowlist + `bridge_kind` qualification correctly identifies the two 2026-05-09 advisories without false positives.
3. Confirm formal-artifact-approval packets for all governed narrative artifacts (rules, CLAUDE.md, AGENTS.md, skills, templates) is the right governance surface.
4. Confirm owner-visible Prime response surface (names + paths) adequately surfaces advisories for Prime-owner dialog.
5. Confirm scaffold/template/fixture updates prevent platform distribution drift and new-install inconsistency.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
