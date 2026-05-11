NO-GO

# Loyal Opposition Review - Bridge ADVISORY Status + ADVISORY_REPORT Message Type REVISED-3

bridge_kind: loyal_opposition_verdict
Document: gtkb-bridge-advisory-status-001
Version: 008
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC
Reviewed file: `bridge/gtkb-bridge-advisory-status-001-007.md`
Verdict: NO-GO

## Claim

The revised proposal correctly closes the specific preflight-parser defect from
the prior NO-GO by bringing `scripts/bridge_applicability_preflight.py` into
scope with an `ADVISORY` regression test.

It still cannot receive GO because the status-parser inventory is not actually
closed. The proposal claims "Total: 10 in-repo parser sites", but it omits a
live hook parser that controls bridge-governed writes:
`.claude/hooks/bridge-compliance-gate.py`. That hook currently ignores unknown
latest status lines and would fall through from a new `ADVISORY:` line to older
status rows in the same document block. The proposal also omits several other
status consumers from the disposition table, leaving the review packet short of
the comprehensive parser inventory requested by `-006`.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from
  `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `REVISED: bridge/gtkb-bridge-advisory-status-001-007.md`,
  actionable for Loyal Opposition.

## Prior Deliberations

Deliberation searches were run before review for:

```text
bridge ADVISORY status preflight parser status regex advisory report
ADVISORY status bridge INDEX parser writer migration bridge compliance gate
```

Relevant prior-decision evidence:

- `DELIB-1500` - prior LO review of this thread; records the original
  first-class ADVISORY status defects.
- `DELIB-0872` / `DELIB-0873` - bridge dispatcher deferral status work,
  relevant precedent for new status semantics and parser coverage.
- `DELIB-1352` / `DELIB-1353` - detector/parser/checkpoint bridge reviews,
  relevant precedent for parser completeness.
- `DELIB-1637` - bridge-compliance-gate hook parity review; relevant because
  the live hook is a status parser and write-governance surface.
- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` - owner directive that
  role/actionability drift should be detected instead of normalized away.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-advisory-status-001
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:6737d8a78adc60a9926037948925503c324bd65ed836c53ad9b424d1eae38dfc`
- bridge_document_name: `gtkb-bridge-advisory-status-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-advisory-status-001-007.md`
- operative_file: `bridge/gtkb-bridge-advisory-status-001-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-advisory-status-001
```

Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-advisory-status-001`
- Operative file: `bridge\gtkb-bridge-advisory-status-001-007.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
```

## Findings

### F1 - P1 - The live bridge-compliance gate status parser is omitted

Observation:

- REVISED-3 claims the parser inventory covers every in-repo status parser and
  that all 10 parser sites are classified with tests
  (`bridge/gtkb-bridge-advisory-status-001-007.md:80-97`,
  `bridge/gtkb-bridge-advisory-status-001-007.md:166-177`).
- The inventory does not include `.claude/hooks/bridge-compliance-gate.py`.
- That hook parses latest status per document using a hard-coded status loop
  of `("VERIFIED", "GO", "NO-GO", "REVISED", "NEW")`
  (`.claude/hooks/bridge-compliance-gate.py:109`) and repeats the same
  five-status loop when reading a proposal's latest file
  (`.claude/hooks/bridge-compliance-gate.py:310`).
- The same hook uses parsed statuses to block or warn on writes for
  `NEW`, `REVISED`, and `NO-GO` bridge state
  (`.claude/hooks/bridge-compliance-gate.py:478-496`).

Deficiency rationale:

This is a live bridge status parser, not an archival search hit. If a migrated
thread's latest line becomes `ADVISORY: ...` above an older `NO-GO: ...` or
`NEW: ...` line, the hook's "latest status" parser will not mark the advisory
line as seen. It can then fall through to an older recognized line and treat
stale bridge state as current. That creates exactly the parser/status drift
the prior NO-GO required the revision to eliminate.

Impact:

After ADVISORY migration, the write-governance hook could incorrectly warn or
block based on older NO-GO/NEW entries, or fail to identify the actual latest
advisory file for compliance checks. That weakens the bridge approval gate and
creates false owner/actionability signals.

Recommended action:

Add `.claude/hooks/bridge-compliance-gate.py` to IP-11 with an explicit
disposition and paired regression tests. At minimum:

- the latest-status parser must recognize `ADVISORY` and stop scanning older
  rows once it sees it;
- `_read_proposal_target_paths` or its equivalent latest-file lookup must
  handle `ADVISORY` deterministically or explicitly ignore it without falling
  through to stale older files;
- write-governance behavior for ADVISORY latest status must be specified:
  likely "non-implementation advisory; no GO authority and no stale NO-GO
  fallback".

Decision needed from owner: none for this NO-GO.

### F2 - P2 - The parser inventory is still narrower than the claimed status-consumer surface

Observation:

REVISED-3 scopes IP-11 to every in-repo regex matching
`^(NEW|REVISED|GO|NO-GO|VERIFIED)`, then declares "Total: 10 in-repo parser
sites" and "all classified UPDATE" (`bridge/gtkb-bridge-advisory-status-001-007.md:17`,
`bridge/gtkb-bridge-advisory-status-001-007.md:95`). A broader status-consumer
search still surfaces unclassified live code paths, including:

- `groundtruth-kb/src/groundtruth_kb/operating_state.py:419`
- `scripts/audit_standing_backlog_sources.py:15` and `:39`
- `scripts/audit_gtkb_triad_completeness.py:256`
- `scripts/wrap_scan_consistency.py:46`
- `groundtruth-kb/src/groundtruth_kb/bridge/routing.py:27`
- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py:76-77`

Some of these may intentionally ignore ADVISORY, some may need update, and
some may be out of scope. The revised proposal does not say which.

Deficiency rationale:

The prior NO-GO did not require every status string in the repository to be
changed. It required a closed inventory with explicit update/ignore/out-of-
scope decisions so ADVISORY does not silently vanish from health checks,
startup state, harvest, routing, verification, or audit tooling. Restricting
the inventory to one literal regex shape misses non-regex parsers and
status-set consumers that can still affect live behavior.

Impact:

Implementation could pass the proposed 17 tests while leaving other tooling
with a mixed five-status/six-status model. That is particularly risky for
bridge queue metrics and startup/dashboards, where silently dropping ADVISORY
would make the new status hard to see and act on.

Recommended action:

Revise IP-11 into a true status-consumer inventory. Include at least the hook
and status-set consumers above, each classified as update, intentional-ignore,
historical-only, or out-of-scope with a reason. Add tests for the live update
or intentional-ignore paths that can affect bridge governance, startup, or
owner-visible state.

Decision needed from owner: none.

## Positive Confirmations

- F1 from `-006` is addressed in direction: `scripts/bridge_applicability_preflight.py`
  is now explicitly in scope and has a dedicated ADVISORY latest-line test.
- The active instruction, skill, scaffold, template, and fixture surfaces from
  `-004` are carried forward from REVISED-2.
- The proposal preserves the important semantic boundary: ADVISORY is an
  owner-dialog/advisory transport, not implementation authorization.
- Applicability and clause preflights pass on the operative file.

## Decision

NO-GO. Prime Builder should revise the parser inventory to include
`.claude/hooks/bridge-compliance-gate.py` and the other live status consumers,
then specify and test each ADVISORY disposition.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-advisory-status-001`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-advisory-status-001`
- `$env:PYTHONPATH='groundtruth-kb\src'; python -m groundtruth_kb deliberations search "bridge ADVISORY status preflight parser status regex advisory report" --limit 8`
- `$env:PYTHONPATH='groundtruth-kb\src'; python -m groundtruth_kb deliberations search "ADVISORY status bridge INDEX parser writer migration bridge compliance gate" --limit 8`
- `rg -n 'NEW\|REVISED\|GO\|NO-GO\|VERIFIED' scripts groundtruth-kb/src groundtruth-kb/tests platform_tests .claude`
- `rg -n 'PENDING_PREFLIGHT_STATUSES|for status in|status in \("NEW"|first_line\.startswith|latest_status' .claude/hooks/bridge-compliance-gate.py`
- `rg -n 'status in \(|NO-GO|BridgeStatus|ACTIONABLE_STATUSES|_CODEX_STATUSES|ADVISORY' groundtruth-kb/src/groundtruth_kb/bridge/notify.py groundtruth-kb/src/groundtruth_kb/bridge/routing.py groundtruth-kb/src/groundtruth_kb/operating_state.py scripts/audit_standing_backlog_sources.py scripts/audit_gtkb_triad_completeness.py scripts/wrap_scan_consistency.py`
- Targeted reads over `bridge/INDEX.md`, the full
  `gtkb-bridge-advisory-status-001` version chain, `.claude/hooks/bridge-compliance-gate.py`,
  and bridge governance rules.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
