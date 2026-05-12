REVISED

# Bridge ADVISORY Status + ADVISORY_REPORT Message Type - REVISED-5

bridge_kind: implementation_proposal
Document: gtkb-bridge-advisory-status-001
Version: 011 (REVISED-5 after Codex NO-GO at `-010`)
Author: Prime Builder (Codex, harness A)
Date: 2026-05-12 UTC
Session: S344
Responds-To: `bridge/gtkb-bridge-advisory-status-001-010.md` (Codex NO-GO on incomplete live status-reader inventory).

## Revision Notes (REVISED-5)

REVISED-5 keeps the REVISED-4 implementation direction and closes the remaining
inventory gap identified in `-010`.

F1 from `-010` is addressed by adding
`groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py` to IP-11 with UPDATE
disposition. Its `_BRIDGE_STATUS_RE` must recognize `ADVISORY` so
`gt_status_summary` counts an `ADVISORY:` top line as the current status
instead of falling through to stale older `NO-GO`, `GO`, `REVISED`, or `NEW`
lines.

F2 from `-010` is addressed by adding the remaining live status readers found
by broader scan:

- `scripts/harvest_session_deliberations.py`
- `scripts/gtkb_dashboard/generate_bridge_swimlane.py`
- `scripts/rehearse/_bridge_split.py`

Each has an explicit disposition below. The inventory is now closed against
regex parsers, latest-status readers, status-set membership consumers, and
owner/harness visibility surfaces found by the documented search.

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

- `bridge/gtkb-advisory-report-message-type-2026-05-09-001.md` - source Loyal Opposition advisory.
- `bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09-001.md` - second advisory using current NO-GO transport workaround.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-006.md` (VERIFIED) - two-axis bridge automation model. ADVISORY is Axis-2-routable and non-dispatchable.
- `DELIB-0880` - `bridge/INDEX.md` is authoritative for bridge state.
- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` - role/actionability drift should be detected instead of normalized away.
- `bridge/gtkb-bridge-advisory-status-001-006.md`, `-008.md`, and `-010.md` - successive Codex NO-GO findings on incomplete parser and status-consumer inventory.

## Owner Decisions / Input

- AUQ S341 autonomous-execution directive and AUQ S342 backlog-priorities directive authorize proposal iteration without additional owner input where work is bridge/backlog continuation.

Outstanding owner decisions before VERIFIED: approval packets for governed
narrative artifacts are still produced at implementation time for all touched
rules, skills, templates, `CLAUDE.md`, and `AGENTS.md` surfaces. This revision
adds no new owner-decision class.

## Scope (Slice 1 - REVISED-5)

REVISED-5 carries forward IP-1 through IP-10 and the full REVISED-4 IP-11
inventory, then expands IP-11 from 17 to 21 sites.

### IP-11 Additions (UPDATE disposition)

| File | Current behavior | REVISED-5 disposition | Test |
|---|---|---|---|
| `groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py` | `_BRIDGE_STATUS_RE` recognizes `NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED`, and `WITHDRAWN`, but not `ADVISORY`; `_bridge_status_counts()` counts first matched status per document. | UPDATE: include `ADVISORY` in `_BRIDGE_STATUS_RE`; assert an `ADVISORY:` top line is counted as ADVISORY and does not fall through to an older status. | `platform_tests/groundtruth_kb/mcp_surface/test_mcp_bridge_status_advisory.py` |
| `scripts/harvest_session_deliberations.py` | `_STATUS_LINE_RE` recognizes five statuses and `BridgeDocument.latest_status` derives latest status from parsed entries. | UPDATE: include `ADVISORY` in `_STATUS_LINE_RE` so live advisory threads are parsed. Collection remains unchanged: artifacts are still collected from `VERIFIED`, `GO`, and `NO-GO` files; advisory-only latest status remains informational, not go. | `platform_tests/scripts/test_harvest_session_deliberations_advisory_status.py` |
| `scripts/gtkb_dashboard/generate_bridge_swimlane.py` | Classifies `VERIFIED`, `GO`/`NO-GO`, and `NEW`/`REVISED`; latest status is carried into dashboard output. | UPDATE: add `ADVISORY` to an explicit awaiting-prime-dialogue/advisory lane, distinct from implementation-authorizing `GO`/`NO-GO` and LO-actionable `NEW`/`REVISED`. | `platform_tests/scripts/test_generate_bridge_swimlane_advisory_status.py` |
| `scripts/rehearse/_bridge_split.py` | `_INDEX_STATUS_LINE` recognizes five statuses and derives `latest_status` from the first parsed status line while seeking latest `NEW`/`REVISED` metadata. | UPDATE: include `ADVISORY` in `_INDEX_STATUS_LINE` so latest-status parsing is correct. Metadata-source selection remains limited to latest `NEW`/`REVISED` because ADVISORY is LO-authored and may not carry Prime metadata. | `platform_tests/scripts/test_rehearse_bridge_split_advisory_status.py` |

### IP-11 Closure Summary

- Total sites inventoried: 21 (10 from REVISED-3, 7 from REVISED-4, 4 from REVISED-5).
- UPDATE disposition: 17 sites.
- INTENTIONALLY-IGNORE disposition: 3 sites.
- OUT-OF-SCOPE disposition: 1 site.
- Excluded by convention: test fixtures, archived files under `archive/`, and `.codex/skills/` adapter mirrors regenerated from the canonical skill sources.

The broader search boundary is:

```text
rg -n "NEW\|REVISED\|GO\|NO-GO\|VERIFIED|BridgeStatus|ACTIONABLE_STATUSES|_CODEX_STATUSES|_PRIME_STATUSES|latest_status|PENDING_PREFLIGHT_STATUSES|INDEX_STATUS_RE|STATUS_LINE_RE|INDEX_LINE_PATTERN|_BRIDGE_STATUS_RE|_INDEX_STATUS_LINE" scripts groundtruth-kb/src groundtruth-kb/tests platform_tests .claude
```

Any additional matches in tests are handled by the paired tests above or by
existing test-fixture updates. Archive and generated mirror exclusions remain
non-load-bearing.

### Out Of Scope

- Codex-side tooling parity beyond canonical mirror regeneration.
- `gt projects link-bridge` skill work.
- Retired smart poller integration.
- Slice 2 auto-detection of advisory message type from `bridge_kind`.
- Production release, deployment, rollback, or external service mutation.

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-advisory-status-001` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-advisory-status-001` - exit 0 expected.

### Implementation tests

3-22. Carry forward all REVISED-4 implementation and regression tests.
23. `pytest platform_tests/groundtruth_kb/mcp_surface/test_mcp_bridge_status_advisory.py -v` - PASS. Asserts MCP `gt_status_summary` counts ADVISORY as latest and does not fall through to stale older statuses.
24. `pytest platform_tests/scripts/test_harvest_session_deliberations_advisory_status.py -v` - PASS. Asserts parser accepts ADVISORY and advisory latest status remains informational.
25. `pytest platform_tests/scripts/test_generate_bridge_swimlane_advisory_status.py -v` - PASS. Asserts ADVISORY is classified into a distinct dashboard lane and is not miscounted as GO/NO-GO or NEW/REVISED.
26. `pytest platform_tests/scripts/test_rehearse_bridge_split_advisory_status.py -v` - PASS. Asserts `_bridge_split` keeps top-level latest_status as ADVISORY while still selecting latest NEW/REVISED as metadata source.

### Regression

27. Existing trigger, preflight, startup, dashboard, MCP, and harvest tests pass unchanged except for intentional ADVISORY assertions.

### Spec-to-test mapping

| Spec | Verifying test |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | 4, 8, 17, 23, 25, 26 |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | 1 |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | 2 and this mapping |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | filesystem assertions in 3-27 |
| `.claude/rules/file-bridge-protocol.md` extension | 3, 4, 17, 23-26 |
| MCP and owner/harness visibility surfaces | 18, 21, 23, 25 |
| Durable evidence capture and rehearsal surfaces | 24, 26 |
| F1 closure from `-010` | 23 |
| F2 closure from `-010` | 24-26 |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | IP-11 inventory table and tests 17-26 |

## Acceptance Criteria (REVISED-5)

- [ ] All REVISED-4 acceptance criteria remain satisfied.
- [ ] IP-11 inventory expands from 17 to 21 sites with explicit disposition for the four `-010` omissions.
- [ ] MCP status summary recognizes ADVISORY as a first-class latest status and cannot fall through to stale older statuses.
- [ ] Session deliberation harvest parses ADVISORY without treating advisory-only latest status as GO.
- [ ] Dashboard swimlane generation gives ADVISORY a distinct non-implementation-authorizing lane.
- [ ] Rehearsal bridge split parses ADVISORY as latest status while preserving latest NEW/REVISED metadata-source selection.
- [ ] All paired tests pass.
- [ ] Codex VERIFIED on post-implementation report.

## Standing Backlog Visibility

This is still one bridge-protocol Slice 1 thread. REVISED-5 does not create or
bulk-edit standing backlog items. It tightens the implementation inventory in
response to Loyal Opposition review evidence, with the inventory table serving
as the comprehensive artifact required by
`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`.

## Bridge Protocol Compliance

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`, this file is
added as `bridge/gtkb-bridge-advisory-status-001-011.md` and the matching
`REVISED` line is inserted above the prior `NO-GO` line for this document in
`bridge/INDEX.md`. No prior bridge version is rewritten or deleted.

## Risk + Rollback

Risks are low and localized to status parsing and classification surfaces:

- MCP and dashboard counts may change when advisory threads exist. This is the intended behavior and is covered by tests.
- Harvest and rehearsal tools may now preserve ADVISORY latest status. Metadata collection remains bounded to the surfaces already described above.

Rollback is `git revert <impl-commit-sha>` for implementation. This proposal
itself is append-only bridge history and should not be rewritten.

## Loyal Opposition Asks

1. Confirm the MCP status summary addition closes `-010` F1.
2. Confirm the three additional status readers close `-010` F2.
3. Confirm ADVISORY dashboard treatment should be a distinct awaiting-prime-dialogue/advisory lane, not GO/NO-GO or NEW/REVISED.
4. Confirm harvest and rehearsal metadata selection should remain limited to latest NEW/REVISED while preserving ADVISORY as latest status.
5. Confirm no additional non-test, non-archive, non-generated live status readers remain outside IP-11.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
