NEW

# Implementation Proposal - Bridge Citation Freshness Preflight (WI-3267)

bridge_kind: implementation_proposal
Document: gtkb-bridge-citation-freshness-preflight
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-3267

target_paths: ["scripts/bridge_citation_freshness_preflight.py", "tests/scripts/test_bridge_citation_freshness_preflight.py"]

This NEW proposal adds a preflight that warns when a bridge proposal cites another bridge thread by version that has since been superseded. Per WI-3267: my `gtkb-advisory-report-protocol-extension-001` cited `gtkb-bridge-advisory-status-001` as 'REVISED-3 at -007' but it was already NO-GO at -008 by review time, triggering F1 NO-GO.

## Claim

A new preflight scans bridge proposal content for cross-thread version citations (regex pattern `bridge/<slug>-NNN.md` or `<status>-N at -NNN`), looks up each in `bridge/INDEX.md` to determine current latest version, and warns when the cited version is not the latest.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge INDEX is canonical state; this preflight enforces that.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage; citation freshness extends this.
- `SPEC-AUQ-POLICY-ENGINE-001` - preflight is part of policy engine surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI-3267 tracked.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-BRIDGE-PROTOCOL-RELIABILITY authorization including this WI.

## Requirement Sufficiency

Existing requirements sufficient. WI-3267 description specifies the preflight + observed-defect motivation.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 + IP-2 single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Citation freshness preflight script

`scripts/bridge_citation_freshness_preflight.py`:

CLI: `python scripts/bridge_citation_freshness_preflight.py --bridge-id <id>`.

Logic:
1. Read the proposal at `bridge/<bridge-id>-NNN.md` (latest version).
2. Extract all citation patterns:
   - `bridge/<slug>-NNN.md` (full path with version)
   - `(?:NEW|REVISED|GO|NO-GO|VERIFIED)(?:-\d+)? at -(\d+)` patterns near `<slug>` references
3. For each cited (slug, version), look up the slug in `bridge/INDEX.md` to determine the current latest version.
4. If cited version != latest, emit warning entry in output JSON: `{cited_slug, cited_version, latest_version, severity: "warn"}`.
5. Render as markdown table in `Citation Freshness` section.
6. Exit 0 (advisory, non-blocking).

### IP-2: Tests

Tests verify: matching cited version (no warning), stale cited version (warning), multi-citation proposal (multiple warnings), citation to slug not in INDEX (gracefully reported).

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Matching version: no warning | `test_matching_version_no_warning` |
| Stale version: warning emitted | `test_stale_version_warning` |
| Multi-citation: per-citation warnings | `test_multi_citation_warnings` |
| Slug not in INDEX: graceful handling | `test_slug_not_in_index_handled` |
| Markdown output schema | `test_markdown_section_emitted` |
| JSON output schema | `test_json_output_schema` |

Run: `python -m pytest tests/scripts/test_bridge_citation_freshness_preflight.py -v`.

## Acceptance Criteria

- IP-1, IP-2 landed; 6 tests PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: citations sometimes intentionally reference historical versions (e.g., "NO-GO at -002" in REVISED-1 context). Mitigation: severity is advisory, not blocking; reviewer judges relevance.
- Rollback: remove the script.

## Recommended Commit Type

`feat` - new preflight tool. ~80 LOC.
