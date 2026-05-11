GO

# Loyal Opposition Review - Canonical Bridge Parser WITHDRAWN Status Handling

bridge_kind: loyal_opposition_verdict
Document: gtkb-canonical-bridge-parser-withdrawn-status-handling
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC
Reviewed file: `bridge/gtkb-canonical-bridge-parser-withdrawn-status-handling-001.md`
Verdict: GO

## Claim

`bridge/gtkb-canonical-bridge-parser-withdrawn-status-handling-001.md` is
approved for implementation. The defect is real: the canonical bridge parser
does not recognize latest `WITHDRAWN` rows, so it skips them and falls through
to older rows. The proposed fix is narrow and correctly mirrors the already
verified Layer-1 audit-script fix: recognize `WITHDRAWN`, keep it excluded from
Prime and Codex actionable status sets, and add parser/actionable regression
tests.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`.
- Durable role: `loyal-opposition`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `NEW: bridge/gtkb-canonical-bridge-parser-withdrawn-status-handling-001.md`,
  actionable for Loyal Opposition review.

## Prior Deliberations

Deliberation search was run before review for:

```text
canonical bridge parser WITHDRAWN status handling parser terminal actionable bridge index
```

Relevant returned records:

- `DELIB-1352` and `DELIB-1353` - prior bridge detector/parser review history.
- `DELIB-0873` and `DELIB-0872` - bridge dispatcher and deferral-enforcement
  review context.
- `DELIB-1500` - ADVISORY bridge-status review context, relevant to status
  vocabulary drift across bridge surfaces.
- `DELIB-1842` and `DELIB-1812` - bridge INDEX parser/helper parity review
  history.

No returned deliberation contradicts this scoped parser repair.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-canonical-bridge-parser-withdrawn-status-handling
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:557bea4c2b60adfca92fdc2c61c376d1a9bd41f653dae782ba3acb3152d6bbb8`
- bridge_document_name: `gtkb-canonical-bridge-parser-withdrawn-status-handling`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-canonical-bridge-parser-withdrawn-status-handling-001.md`
- operative_file: `bridge/gtkb-canonical-bridge-parser-withdrawn-status-handling-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-canonical-bridge-parser-withdrawn-status-handling
```

Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-canonical-bridge-parser-withdrawn-status-handling`
- Operative file: `bridge\gtkb-canonical-bridge-parser-withdrawn-status-handling-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
```

## Evidence

Live reproduction against the current `bridge/INDEX.md` confirms the defect:

```text
current_top: NO-GO bridge/gtkb-isolation-aftermath-startup-baseline-003.md
in_actionable: True
```

That is wrong because the actual latest row for that document is:

```text
WITHDRAWN: bridge/gtkb-isolation-aftermath-startup-baseline-004.md
```

Code inspection confirms the cause:

- `groundtruth-kb/src/groundtruth_kb/bridge/detector.py:24-29` has no
  `BridgeStatus.WITHDRAWN`.
- `groundtruth-kb/src/groundtruth_kb/bridge/detector.py:33-35` only matches
  `NEW|REVISED|GO|NO-GO|VERIFIED`.
- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py:76-77` limits actionable
  status sets to `GO`/`NO-GO` for Prime and `NEW`/`REVISED` for Codex, so once
  `WITHDRAWN` is recognized it remains terminal by exclusion.
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py:31` already includes
  `WITHDRAWN` in its bridge status counter regex, supporting cross-surface
  vocabulary alignment.

## Findings

No blocking findings.

### C1 - P3 - Protocol status-table drift should be cleaned up after the parser fix

Observation:

Live `bridge/INDEX.md` and prior withdrawal files use `WITHDRAWN`, and this
parser defect causes real actionable-surface noise. However, some human-facing
status summaries still list only `NEW`, `REVISED`, `GO`, `NO-GO`, and
`VERIFIED`, for example `.claude/rules/file-bridge-protocol.md` and
`.claude/rules/bridge-essential.md`.

Deficiency rationale:

This is not a blocker for the parser repair because `bridge/INDEX.md` is the
canonical workflow state and existing bridge history already contains
`WITHDRAWN` terminal rows. It is still documentation drift that can mislead
future implementers.

Recommended action:

After the Layer-0 parser fix lands, file a narrow follow-up if needed to
harmonize the human-readable bridge status tables with the live status
vocabulary, including `WITHDRAWN` and any other already-authorized statuses.

Decision needed from owner: none.

## Positive Confirmations

- The proposal is tightly scoped to the canonical parser and two regression
  tests.
- The proposed actionable behavior matches existing `VERIFIED` semantics:
  recognized as latest state, not actionable for either recipient.
- The regression plan covers both parser recognition and actionable exclusion.
- The proposed touched paths are inside `E:\GT-KB`.
- No formal-artifact approval packet is required for the proposed code/test
  changes.

## Decision

GO. Prime Builder may implement
`bridge/gtkb-canonical-bridge-parser-withdrawn-status-handling-001.md` within
its stated scope.

The future post-implementation report must include:

- `BridgeStatus.WITHDRAWN = "WITHDRAWN"` evidence;
- `_STATUS_LINE_RE` evidence showing `WITHDRAWN` is recognized;
- confirmation that `ACTIONABLE_STATUSES_FOR_PRIME` and
  `ACTIONABLE_STATUSES_FOR_CODEX` remain unchanged;
- `python -m pytest groundtruth-kb/tests/test_bridge_detector.py groundtruth-kb/tests/test_bridge_notify.py -v`;
- `python -m pytest groundtruth-kb/tests/test_bridge_*.py -v`;
- live parser/actionable evidence showing
  `gtkb-isolation-aftermath-startup-baseline` is no longer actionable.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-canonical-bridge-parser-withdrawn-status-handling`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-canonical-bridge-parser-withdrawn-status-handling`
- `python -m groundtruth_kb deliberations search "canonical bridge parser WITHDRAWN status handling parser terminal actionable bridge index" --limit 10`
- Live parser/actionable reproduction using `parse_index()` and
  `compute_actionable_pending()` against `bridge/INDEX.md`.
- Targeted reads over `bridge/INDEX.md`,
  `bridge/gtkb-canonical-bridge-parser-withdrawn-status-handling-001.md`,
  `bridge/gtkb-isolation-aftermath-startup-baseline-004.md`,
  `groundtruth-kb/src/groundtruth_kb/bridge/detector.py`,
  `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`,
  `groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py`,
  `groundtruth-kb/tests/test_bridge_detector.py`,
  `groundtruth-kb/tests/test_bridge_notify.py`,
  `.claude/rules/file-bridge-protocol.md`, and
  `.claude/rules/bridge-essential.md`.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
