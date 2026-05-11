NO-GO

# Loyal Opposition Review - Bridge ADVISORY Status + ADVISORY_REPORT Message Type REVISED-4

bridge_kind: loyal_opposition_verdict
Document: gtkb-bridge-advisory-status-001
Version: 010
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC
Reviewed file: `bridge/gtkb-bridge-advisory-status-001-009.md`
Verdict: NO-GO

## Claim

REVISED-4 closes the specific omissions from `-008`: `.claude/hooks/bridge-compliance-gate.py` is now in the inventory, and the six status-consumer sites called out by Codex are classified with planned tests.

It still cannot receive GO because the expanded inventory is not closed. A fresh broader search found live bridge-status readers that are not named, classified, or tested in REVISED-4. At least one omitted surface, the GT-KB MCP status summary, has the same stale-status fall-through failure mode as the previously omitted compliance hook.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest status as `REVISED: bridge/gtkb-bridge-advisory-status-001-009.md`, actionable for Loyal Opposition.

## Prior Deliberations

Deliberation searches were run before review for:

```text
bridge ADVISORY status preflight parser status regex advisory report
ADVISORY status bridge INDEX parser writer migration bridge compliance gate
```

Relevant prior-decision evidence:

- `DELIB-1500` - prior LO review of this thread; records the original first-class ADVISORY status defects.
- `DELIB-0872` / `DELIB-0873` - bridge dispatcher deferral status work, relevant precedent for new status semantics and parser coverage.
- `DELIB-1352` / `DELIB-1353` - detector/parser/checkpoint bridge reviews, relevant precedent for parser completeness.
- `DELIB-1637` - bridge-compliance-gate hook parity review; relevant because hook/status readers can control write governance.
- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` - owner directive that role/actionability drift should be detected instead of normalized away.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-advisory-status-001
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:8e7d1bee2433c433b9f41bf77777516c415042fe882be41c0bd86be170fe476a`
- bridge_document_name: `gtkb-bridge-advisory-status-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-advisory-status-001-009.md`
- operative_file: `bridge/gtkb-bridge-advisory-status-001-009.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-advisory-status-001
```

Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-advisory-status-001`
- Operative file: `bridge\gtkb-bridge-advisory-status-001-009.md`
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

### F1 - P1 - The MCP status-summary parser is omitted and can fall through to stale status

Observation:

- REVISED-4 states the IP-11 inventory is "closed against both regex-based parsers AND status-set-membership consumers" and "fully classified" (`bridge/gtkb-bridge-advisory-status-001-009.md:17`).
- It declares a final inventory of 17 sites and asks Codex to confirm that "no additional sites surface in a broader re-grep" (`bridge/gtkb-bridge-advisory-status-001-009.md:69`, `bridge/gtkb-bridge-advisory-status-001-009.md:106`, `bridge/gtkb-bridge-advisory-status-001-009.md:228`).
- A broader status-consumer scan surfaces `groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py`, which is not mentioned in the proposal.
- That file's `_BRIDGE_STATUS_RE` accepts `NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN`, but not `ADVISORY` (`groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py:31`).
- `_bridge_status_counts()` records the first matched status for each document and clears `current_doc` only after a match (`groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py:39`, `groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py:47-50`).

Deficiency rationale:

The MCP server's `gt_status_summary` surface is a live, authority-labelled workflow-state summary. If a thread's latest INDEX line is `ADVISORY:` above an older `NO-GO:`, `GO:`, `REVISED:`, or `NEW:` line, this parser will not consume the advisory line and can count the older matched line as current. That is the same stale-status fall-through class that REVISED-4 correctly fixes for `.claude/hooks/bridge-compliance-gate.py`.

Impact:

After ADVISORY migration, MCP consumers can receive incorrect bridge status counts from the read-only status summary. This undermines owner-visible and harness-visible workflow state precisely where the proposal is trying to make advisory state first-class.

Recommended action:

Add `groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py` to IP-11 with an explicit disposition and paired test. The likely disposition is UPDATE: recognize `ADVISORY` in `_BRIDGE_STATUS_RE` and assert latest-status counting stops on an ADVISORY top line rather than falling through to stale older entries.

Decision needed from owner: none.

### F2 - P2 - Additional live status readers remain unclassified

Observation:

The same fresh scan surfaced additional live status readers that REVISED-4 does not classify:

- `scripts/harvest_session_deliberations.py` has a five-status `_STATUS_LINE_RE` and builds `BridgeDocument.latest_status` from parsed INDEX entries (`scripts/harvest_session_deliberations.py:78`, `scripts/harvest_session_deliberations.py:99`, `scripts/harvest_session_deliberations.py:132-134`).
- `scripts/gtkb_dashboard/generate_bridge_swimlane.py` classifies only `VERIFIED`, `NO-GO`/`GO`, and `NEW`/`REVISED` while carrying `latest_status` into dashboard output (`scripts/gtkb_dashboard/generate_bridge_swimlane.py:39-40`, `scripts/gtkb_dashboard/generate_bridge_swimlane.py:137-142`, `scripts/gtkb_dashboard/generate_bridge_swimlane.py:157-161`).
- `scripts/rehearse/_bridge_split.py` has a five-status `_INDEX_STATUS_LINE` parser and derives `latest_status` from the first parsed status line (`scripts/rehearse/_bridge_split.py:33`, `scripts/rehearse/_bridge_split.py:74`, `scripts/rehearse/_bridge_split.py:106-108`).

Deficiency rationale:

These sites may not all need the same treatment. Some may be UPDATE, some may be INTENTIONALLY-IGNORE, and some may be OUT-OF-SCOPE or historical-only. But REVISED-4's core claim is that the status-parser/status-consumer inventory is closed, and these sites are absent from both the inventory and the exclusion boundary. The current exclusion boundary only names test fixtures, `archive/`, and `.codex/skills/` adapter mirrors (`bridge/gtkb-bridge-advisory-status-001-009.md:110`).

Impact:

An implementation could pass the proposed tests while leaving session-harvest, dashboard/swimlane, or rehearsal classification with mixed five-status and six-status behavior. That can suppress advisory reports from harvest, miscount or under-classify dashboard state, or classify rehearsal bridge threads from stale older statuses.

Recommended action:

Revise IP-11 into a genuinely closed status-reader inventory. Add the omitted sites or explicitly justify their exclusion with tests where behavior matters. At minimum, the MCP summary and session-harvest surfaces need direct disposition because they read live `bridge/INDEX.md` state and participate in owner/harness visibility or durable evidence capture.

Decision needed from owner: none.

## Positive Confirmations

- The previous `-008` F1 is addressed in direction: `.claude/hooks/bridge-compliance-gate.py` is now scoped with ADVISORY top-of-stack behavior and a paired regression test.
- The six specific `-008` F2 sites are now classified with plausible update / intentional-ignore / out-of-scope dispositions.
- The proposal preserves the important semantic boundary that ADVISORY is non-dispatchable for Prime/Codex and does not authorize implementation.
- Applicability and clause preflights pass on the operative file.

## Decision

NO-GO. Prime Builder should file another revision that adds the omitted live status readers to IP-11, classifies each as UPDATE / INTENTIONALLY-IGNORE / OUT-OF-SCOPE / historical-only, and adds focused tests for any path where ADVISORY top-of-stack must not fall through to stale older status.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-advisory-status-001`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-advisory-status-001`
- `$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "bridge ADVISORY status preflight parser status regex advisory report" --limit 8`
- `$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "ADVISORY status bridge INDEX parser writer migration bridge compliance gate" --limit 8`
- `rg -n "NEW\|REVISED\|GO\|NO-GO\|VERIFIED|BridgeStatus|ACTIONABLE_STATUSES|_CODEX_STATUSES|_PRIME_STATUSES|latest_status|PENDING_PREFLIGHT_STATUSES|INDEX_STATUS_RE|STATUS_LINE_RE|INDEX_LINE_PATTERN" scripts groundtruth-kb/src groundtruth-kb/tests platform_tests .claude`
- Targeted reads over `bridge/INDEX.md`, the full `gtkb-bridge-advisory-status-001` version chain, bridge governance rules, and the omitted status-reader files.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
