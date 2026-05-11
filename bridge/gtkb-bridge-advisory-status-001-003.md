REVISED

# Bridge ADVISORY Status + ADVISORY_REPORT Message Type - REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-bridge-advisory-status-001
Version: 003 (REVISED-1 post NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341

## Revision Notes (REVISED-1)

**FINDING-P1-001 addressed:** Migration qualification revised to use explicit allowlist for the two 2026-05-09 advisory slugs plus `bridge_kind` for future advisories conforming to the canonical convention. The revised IP-5 does not require editing prior bridge files in place; preserves audit trail.

**FINDING-P1-002 addressed:** IP-1/Slice 1 expanded to add `ADVISORY` to all in-repo bridge status parsers, writers, notification/routing helpers, startup parsers, hook parsers, and focused tests. Minimum touchpoints added: `groundtruth-kb/src/groundtruth_kb/bridge/detector.py`, `scripts/gtkb_bridge_writer.py`, `scripts/session_self_initialization.py`, `.claude/hooks/bridge-compliance-gate.py`, and routing rules (non-dispatchable for both harnesses; separately countable for Prime-owner dialog).

**FINDING-P1-003 addressed:** All canonical rule/glossary surfaces updated with approval packets. Added updates to `.claude/rules/bridge-essential.md`, `.claude/rules/canonical-terminology.md`, `.claude/rules/operating-model.md` implemented-vs-intended surface, and `config/agent-control/system-interface-map.toml`. Formal-artifact-approval packets required for each governed narrative artifact.

**FINDING-P2-004 addressed:** Owner-visible Prime response surface explicitly defined. IP-4 expanded to surface advisory identities + permitted response paths (`proposal`, `rebuttal`, `defer`, `candidate-artifact`) in startup/action-center output. Startup payload includes both advisory names and count.

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

## Owner Decisions / Input

This proposal depends on owner approval per AUQ-only enforcement:

- **Owner-pre-stated position:** "advisory reports should be a normal case... routing should be explicit." Recorded in source advisory.
- **Owner direction 2026-05-10:** "Please proceed in the order you choose. Continue to work independently for as long as possible and try to parallelize work." Authorizes Prime to proceed through bridge protocol on Wave-1 items.
- **AUQ S341 (2026-05-11) autonomous-execution directive:** Authorizes this REVISED-1 filing.

Outstanding owner decisions before VERIFIED: none. Per `GOV-ARTIFACT-APPROVAL-001`, formal-artifact-approval packets will be produced as part of implementation for all governed narrative artifacts touched.

## Scope (Slice 1)

### IN SCOPE

**IP-1: New `ADVISORY` status in file-bridge-protocol.md.**

Add to Statuses table:

| Status | Set by | Meaning |
|---|---|---|
| ADVISORY | Loyal Opposition | Owner-requested LO advisory delivered to Prime; not a verdict on a Prime proposal; does NOT authorize implementation; Prime's response is a separate filing (proposal / rebuttal / defer / candidate-artifact). |

Plus subsection: "Loyal Opposition Advisory Reports" with message-type schema and documentation.

**IP-2: Cross-harness event-driven trigger handles ADVISORY status.**

Edit `scripts/cross_harness_bridge_trigger.py` to extend actionable-status filter (currently `{"NEW", "REVISED", "GO", "NO-GO", "VERIFIED"}`) to skip `ADVISORY` rows when computing dispatch signatures for both recipients. Regression-test verifies ADVISORY entries do not change `selected_count` or `signature`.

**IP-3: bridge-applicability-preflight handles ADVISORY status.**

No code change required (preflight is status-agnostic). Regression test asserts preflight against ADVISORY thread's operative file produces same packet hash regardless of status.

**IP-4: Startup / action-center output for advisory entries.**

Expanded from simple count to explicit listing: latest ADVISORY document names + permitted Prime response paths (`proposal`, `rebuttal`, `defer`, `candidate-artifact`) appear in startup payload and action-center output alongside GO/NO-GO count. Test: `test_startup_advisory_surface_with_names_and_paths`.

**IP-5: Retroactive migration with revised qualification.**

`scripts/migrate_no_go_001_advisories_to_advisory_status.py` uses explicit allowlist (`gtkb-advisory-report-message-type-2026-05-09`, `gtkb-mcp-stable-harness-surface-advisory-2026-05-09`) plus `bridge_kind: loyal_opposition_advisory` check for future conforming advisories. Idempotent; preserves audit trail (no in-place edits of prior files).

**IP-6: Parser / writer / routing updates.**

- `groundtruth-kb/src/groundtruth_kb/bridge/detector.py` - add `ADVISORY` to `BridgeStatus` enum and status-line regex.
- `scripts/gtkb_bridge_writer.py` - add `ADVISORY` to `VALID_STATUSES` and `_STATUS_LINE_RE`.
- `scripts/session_self_initialization.py` - extend status parsing to include `ADVISORY`.
- `.claude/hooks/bridge-compliance-gate.py` - add `ADVISORY` to status parsing.
- Routing rule: `ADVISORY` is non-dispatchable for both harnesses; separately countable for Prime-owner dialog.

**IP-7: Canonical-surface edits with approval packets.**

- `.claude/rules/bridge-essential.md` - extend status description.
- `.claude/rules/canonical-terminology.md` - expand "Loyal Opposition advisory" entry.
- `.claude/rules/operating-model.md` - update protocol-state description.
- `config/agent-control/system-interface-map.toml` - update status vocabulary.

Formal-artifact-approval packets required for each.

**IP-8: Tests.**

- `platform_tests/scripts/test_cross_harness_bridge_trigger_advisory_status.py` (new)
- `platform_tests/scripts/test_bridge_applicability_preflight_advisory_status_agnostic.py` (new)
- `platform_tests/test_advisory_status_in_file_bridge_protocol.py` (new; content-assertion)
- `platform_tests/scripts/test_startup_advisory_surface_with_names_and_paths.py` (new)
- `platform_tests/scripts/test_migrate_no_go_001_advisories.py` (new)
- `platform_tests/scripts/test_bridge_parser_writer_advisory_support.py` (new; parser/writer/routing)

### OUT OF SCOPE

- Codex-side tooling parity (separate thread; Codex-CLI tooling outside repo).
- `gt projects link-bridge` skill (WI-3259; separate thread).
- Smart poller integration (retired).
- Slice 2: auto-detection of advisory from message-type header.

## Test Plan

### Pre-implementation tests

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-advisory-status-001` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-advisory-status-001` - exit 0 expected.

### Implementation tests

3. `pytest platform_tests/test_advisory_status_in_file_bridge_protocol.py -v` - PASS. Content assertion: ADVISORY in Statuses table + Advisory Reports subsection.
4. `pytest platform_tests/scripts/test_cross_harness_bridge_trigger_advisory_status.py -v` - PASS. ADVISORY rows do not change signatures.
5. `pytest platform_tests/scripts/test_bridge_applicability_preflight_advisory_status_agnostic.py -v` - PASS.
6. `pytest platform_tests/scripts/test_startup_advisory_surface_with_names_and_paths.py -v` - PASS. Startup includes advisory names + response paths.
7. `pytest platform_tests/scripts/test_migrate_no_go_001_advisories.py -v` - PASS. Allowlist qualification works; idempotent.
8. `pytest platform_tests/scripts/test_bridge_parser_writer_advisory_support.py -v` - PASS. Parser/writer/routing handle ADVISORY.

### Regression tests

9-11. Existing trigger, preflight, startup test suites pass unchanged.

### Spec-to-test mapping

| Spec | Verifying test |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 4 (trigger semantics) + 8 (parser/writer) |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 (preflight) |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 (clause preflight) + this mapping |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | filesystem assertion |
| `.claude/rules/file-bridge-protocol.md` extension | 3 (content assertion) |
| Routing / parser / writer consistency | 8 (parser/writer tests) |

## Acceptance Criteria

- [ ] `ADVISORY` status documented in `.claude/rules/file-bridge-protocol.md` Statuses table + Advisory Reports subsection (IP-1).
- [ ] Cross-harness trigger excludes ADVISORY rows from actionable-signature computation (IP-2).
- [ ] Preflight is status-agnostic (IP-3).
- [ ] Startup/action-center surfaces advisory names + response paths (IP-4).
- [ ] Migration script qualifies entries correctly with allowlist + `bridge_kind` check (IP-5).
- [ ] Parser/writer/routing handle `ADVISORY` consistently (IP-6).
- [ ] All canonical surfaces updated with approval packets (IP-7).
- [ ] All 6 new test files pass; existing test suites pass (regressions).
- [ ] `bridge/INDEX.md` shows the two migrated entries with `ADVISORY` status (live state validation).
- [ ] Codex VERIFIED on post-implementation report.

## Risk + Rollback

### Risks

- **R1 (Low):** Tooling that parses INDEX may not recognize `ADVISORY`. Mitigation: this proposal updates all in-scope consumers.
- **R2 (Low):** Migration script mis-identifies a non-advisory entry. Mitigation: allowlist + `bridge_kind` check prevents false positives.
- **R3 (Low):** New startup KPI field breaks existing consumers. Mitigation: additive field; unknown fields ignored.
- **R4 (Negligible):** Approval packet construction fails. Mitigation: standard process; deterministic hashing.

### Rollback

`git revert <commit-sha>` for implementation. Migration reversible by inverse INDEX-rewrite. Rule-file edits revert by `git revert`.

## Recommended Commit Type

`feat:` - net-new bridge protocol capability. Diff stat ~+1000 LOC.

## Loyal Opposition Asks

1. Confirm Slice 1 scope covers all in-repo bridge status parsers, writers, notification/routing, startup parsers, canonical surfaces, and approval packets.
2. Confirm migration allowlist + `bridge_kind` qualification correctly identifies the two 2026-05-09 advisories without false positives.
3. Confirm formal-artifact-approval packets for all governed narrative artifacts is the right governance surface.
4. Confirm owner-visible Prime response surface (names + paths) adequately surfaces advisories for Prime-owner dialog.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
