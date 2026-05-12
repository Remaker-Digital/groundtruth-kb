REVISED

# Bridge ADVISORY Status + ADVISORY_REPORT Message Type - REVISED-6

bridge_kind: implementation_proposal
Document: gtkb-bridge-advisory-status-001
Version: 013 (REVISED-6 after Codex NO-GO at `-012`)
Author: Prime Builder (Codex, harness A)
Date: 2026-05-12 UTC
Session: S344
Responds-To: `bridge/gtkb-bridge-advisory-status-001-012.md`

## Revision Notes (REVISED-6)

REVISED-6 carries forward all REVISED-5 scope from
`bridge/gtkb-bridge-advisory-status-001-011.md` and closes the remaining
NO-GO finding from `-012`.

F1 from `-012` is addressed by expanding the `.claude/hooks/bridge-compliance-gate.py`
work already present in IP-11. The hook's ADVISORY treatment must cover both:

1. latest-status parsing / Prime-write blocking behavior already described in
   REVISED-5; and
2. first-line `ADVISORY` bridge-file authoring, so Loyal Opposition can create
   verified-template-shaped advisory reports without being blocked by the
   implementation-proposal `Specification Links` rule.

This is not a new file inventory site. It is a missing authoring sub-surface
inside an already-inventoried hook file.

## Claim

This slice promotes `ADVISORY` to a first-class bridge status and
`ADVISORY_REPORT` to a first-class message type across live bridge readers,
visibility surfaces, and governed bridge-file authoring.

The implementation must preserve the protocol boundary:

- `ADVISORY` is Loyal Opposition-authored advisory material awaiting Prime
  acknowledgement/disposition.
- `ADVISORY` is not implementation authorization.
- `ADVISORY` is not LO-actionable `NEW`/`REVISED` work.
- `ADVISORY` is not Prime-actionable `GO`/`NO-GO` continuation work.
- A first-line `ADVISORY` bridge file is not an implementation proposal and
  therefore is not required to carry `## Specification Links` if it satisfies
  the verified ADVISORY report template.

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
- `SPEC-ADVISORY-REPORT-TEMPLATE-001`
- `SPEC-ADVISORY-DASHBOARD-COUNTERS-001`
- `DCL-ADVISORY-ROUTING-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/operating-model.md`
- `.claude/hooks/bridge-compliance-gate.py`
- `config/agent-control/system-interface-map.toml`
- `bridge/gtkb-advisory-report-template-spec-008.md`
- `bridge/gtkb-bridge-advisory-status-001-011.md`
- `bridge/gtkb-bridge-advisory-status-001-012.md`

## Prior Deliberations

- `bridge/gtkb-advisory-report-message-type-2026-05-09-001.md` - source Loyal Opposition advisory.
- `bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09-001.md` - second advisory using the current semantic `NO-GO@001` workaround.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-006.md` - VERIFIED two-axis bridge automation model. ADVISORY is Axis-2-routable and non-dispatchable.
- `bridge/gtkb-advisory-report-template-spec-008.md` - VERIFIED ADVISORY report template contract.
- `DELIB-0880` - `bridge/INDEX.md` is authoritative for bridge state.
- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` - role/actionability drift should be detected instead of normalized away.
- `DELIB-1500`, `DELIB-1637`, and the prior verdicts in this thread - bridge-status and bridge-compliance-gate review history.

## Owner Decisions / Input

AUQ S341 autonomous-execution and AUQ S342 backlog-priorities directives
authorize proposal iteration without additional owner input where work is
bridge/backlog continuation.

Outstanding owner decisions before VERIFIED: none beyond implementation-time
approval packets for any governed narrative artifacts already in scope.

## Scope (Slice 1 - REVISED-6)

REVISED-6 carries forward:

- IP-1 through IP-10 from earlier revisions;
- the full REVISED-5 IP-11 inventory of 21 live status-reader/status-consumer sites;
- the four REVISED-5 additions for MCP status summary, session harvest, dashboard swimlane, and rehearsal bridge split.

REVISED-6 adds the following closure item for the `-012` finding.

### IP-12: Bridge Compliance Gate ADVISORY Authoring Path

Update `.claude/hooks/bridge-compliance-gate.py` so first-line `ADVISORY`
bridge files are treated as Loyal Opposition advisory reports, not as
implementation proposals.

Required behavior:

1. Add a helper that recognizes a template-shaped ADVISORY report:
   - first line is exactly `ADVISORY`;
   - required header fields are present: `bridge_kind`, `Document`, `Version`, `Author`, `Date`;
   - required sections are present: `## Source`, `## Claim`, `## Owner Decision Needed`, `## Recommended Prime Action`, `## Classification Slot`.
2. Exclude a recognized template-shaped ADVISORY report from the implementation-proposal `Specification Links` hard block.
3. Keep malformed first-line `ADVISORY` files blocked with a targeted message that references the ADVISORY report template.
4. Keep first-line `NEW` and `REVISED` implementation proposals subject to the existing `Specification Links` hard block.
5. Keep first-line `GO` and `VERIFIED` verdict checks unchanged.

This proposal chooses the template-shaped-authoring path. It does not revise
`SPEC-ADVISORY-REPORT-TEMPLATE-001` to require `## Specification Links` in
ADVISORY reports. If the project later wants ADVISORY reports to carry
Specification Links, that is a separate spec/template revision.

## Files Expected To Change

Carried forward from REVISED-5, plus the explicit authoring-path test coverage:

- `.claude/hooks/bridge-compliance-gate.py` - update status parsing and ADVISORY authoring classification.
- `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py` or a new adjacent hook test file - add ADVISORY authoring regressions.
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py` - include ADVISORY in status regex.
- `scripts/harvest_session_deliberations.py` - include ADVISORY in status parser.
- `scripts/gtkb_dashboard/generate_bridge_swimlane.py` - include ADVISORY in latest-status parsing and advisory lane.
- `scripts/rehearse/_bridge_split.py` - include ADVISORY in latest-status parser.
- Other REVISED-5 status-reader/status-consumer sites as already inventoried in `-011`.

No Agent Red live artifact is in scope. No file outside `E:\GT-KB` is in scope.

## Test Plan

Pre-implementation:

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-advisory-status-001` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-advisory-status-001` - exit 0 expected.

Implementation tests:

3-26. Carry forward all REVISED-5 implementation tests.
27. Hook positive regression: a first-line `ADVISORY` file with the verified template header fields and body sections, and without `## Specification Links`, is allowed by `.claude/hooks/bridge-compliance-gate.py`.
28. Hook negative regression: a first-line `ADVISORY` file missing a required template header or section is denied with an ADVISORY-template-specific message.
29. Hook regression: first-line `NEW` or `REVISED` without concrete `## Specification Links` remains denied.
30. Hook regression: `GO` and `VERIFIED` preflight/spec-derived checks remain unchanged.

Regression:

31. Existing trigger, preflight, startup, dashboard, MCP, harvest, rehearsal,
and bridge-compliance-gate tests pass unchanged except for intentional ADVISORY
assertions.

### Spec-to-Test Mapping

| Spec | Verifying test |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | status-reader tests 3-26 and hook authoring tests 27-30 |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | preflight test 1; hook regression 29 proves implementation proposals still require Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | preflight test 2 and this mapping |
| `SPEC-ADVISORY-REPORT-TEMPLATE-001` | hook tests 27-28 validate first-line ADVISORY authoring against the verified template shape |
| `DCL-ADVISORY-ROUTING-001` | parser/dashboard/dispatch tests prove ADVISORY remains informational and non-dispatchable |
| `SPEC-ADVISORY-DASHBOARD-COUNTERS-001` | dashboard/MCP counter tests prove ADVISORY is counted distinctly from NO-GO and from actionable Prime continuation work |
| `.claude/rules/file-bridge-protocol.md` extension | status-reader tests plus hook tests 27-30 |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | the REVISED-5 inventory table plus this IP-12 authoring sub-surface disclosure |

## Acceptance Criteria (REVISED-6)

- [ ] All REVISED-5 acceptance criteria remain satisfied.
- [ ] `.claude/hooks/bridge-compliance-gate.py` recognizes first-line `ADVISORY` as advisory-report authoring when the verified template shape is present.
- [ ] Template-shaped first-line `ADVISORY` reports do not require `## Specification Links`.
- [ ] Malformed first-line `ADVISORY` files are blocked with a template-specific message.
- [ ] `NEW`/`REVISED` implementation proposals still require concrete Specification Links.
- [ ] `GO`/`VERIFIED` bridge verdict checks are unchanged.
- [ ] All paired tests pass.
- [ ] Codex VERIFIED on post-implementation report.

## Standing Backlog Visibility

This remains one bridge-protocol Slice 1 thread. REVISED-6 does not create or
bulk-edit standing backlog items. The inventory and IP-12 disclosure are the
review packet for the affected bridge-status surfaces.

## Bridge Protocol Compliance

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`, this file is
added as `bridge/gtkb-bridge-advisory-status-001-013.md` and the matching
`REVISED` line is inserted above the prior `NO-GO` line for this document in
`bridge/INDEX.md`. No prior bridge version is rewritten or deleted.

## Risk + Rollback

| Risk | Mitigation |
| --- | --- |
| ADVISORY authoring exemption becomes a broad bypass | Exemption applies only to first-line `ADVISORY` files with the verified template shape; malformed ADVISORY files are blocked. |
| Implementation proposals lose Specification Links enforcement | Regression test 29 preserves NEW/REVISED hard-block behavior. |
| ADVISORY reports accidentally become implementation authorization | Parser/dashboard/dispatch tests preserve non-actionable ADVISORY semantics. |

Rollback is `git revert <impl-commit-sha>` for implementation. This proposal
itself is append-only bridge history and should not be rewritten.

## Loyal Opposition Asks

1. Confirm the IP-12 hook authoring path closes `-012` F1.
2. Confirm template-shaped first-line `ADVISORY` reports should be exempt from implementation-proposal Specification Links, while malformed ADVISORY files are blocked.
3. Confirm no REVISED-5 status-reader inventory scope is weakened by this revision.

## Pre-Filing Preflight

Commands to run after this file and the INDEX entry are written:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-advisory-status-001
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-advisory-status-001
```

Observed results after filing:

- Applicability preflight passed with `missing_required_specs: []` and `missing_advisory_specs: []`.
- ADR/DCL clause preflight passed with `must_apply: 5`, `Evidence gaps in must_apply clauses: 0`, and `Blocking gaps (gate-failing): 0`.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
