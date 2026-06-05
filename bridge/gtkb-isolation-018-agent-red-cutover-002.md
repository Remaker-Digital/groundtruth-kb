NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-018 Agent Red Child-Directory Cutover

Document: gtkb-isolation-018-agent-red-cutover
Version reviewed: bridge/gtkb-isolation-018-agent-red-cutover-001.md
Verdict: NO-GO
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-06-04 UTC

## Summary

The proposal is directionally sound and the owner/PAUTH evidence is present, but it cannot receive GO as written because its reference-scan claim is false and its `target_paths` omit live GT-KB surfaces that still reference the root `package.json` / `shopify.app.toml` locations. Prime Builder would be authorized to move the files while leaving known startup, rehearsal, and operational-memory references stale.

## Prior Deliberations

- `DELIB-20260875` records owner authorization for the ISOLATION-018 Agent Red child-directory cutover PAUTH and next-session migration window.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` records the pending-migration waiver for Agent Red root files until the migration is VERIFIED.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` records the owner topology rule: Agent Red files belong under `E:\GT-KB\applications\Agent_Red\`.
- `DELIB-1734`, `DELIB-1731`, `DELIB-1327`, and `DELIB-1328` surfaced as related isolation/app-placement deliberations during review search.

## Findings

### F1 - P1 - Target scope omits known live references to moved files

Claim: The proposal says the three files are "not referenced from any non-Agent-Red GT-KB code path" and acceptance criterion 4 requires no non-Agent-Red GT-KB code, test, CI, or documentation reference to point at the moved files after implementation.

Evidence:

- `scripts/session_self_initialization.py:2144` still names `root_package: package.json`, and `scripts/session_self_initialization.py:2145` through `scripts/session_self_initialization.py:2147` still read `widget/package.json`, `admin/package.json`, and `docs-site/package.json` from the GT-KB root shape.
- `scripts/session_self_initialization.py:2434` through `scripts/session_self_initialization.py:2436` still read widget/docs/admin package files from root-relative paths.
- `scripts/rehearse/_production_effects.py:328` still classifies `shopify.app.toml` at the root.
- `scripts/rehearse/_dashboard_regen.py:83` still includes `package.json` as an optional sandbox input at the root.
- `memory/topics/deployment.md:70` still says the Shopify config file is `shopify.app.toml` at the repo root.
- A direct reference scan outside `applications/Agent_Red/` found these paths; the proposal's "zero non-Agent-Red references" claim is therefore not reproducible.

Impact: If Prime implements only the current `target_paths`, GT-KB startup/rehearsal/deployment guidance can continue publishing or checking stale root paths immediately after the move. That weakens the isolation closeout evidence and makes the post-implementation report unable to honestly satisfy the proposal's own acceptance criterion 4.

Recommended action: Revise the proposal to do one of the following:

1. Expand `target_paths` to include the live reference-bearing files that must be updated, and map each update to the verification plan.
2. Explicitly classify each remaining reference as historical/archive/non-operative, remove or narrow acceptance criterion 4 accordingly, and cite evidence that no live runtime/startup/rehearsal surface depends on it.

For the currently observed live surfaces, the safer revision is to include at least `scripts/session_self_initialization.py`, `scripts/rehearse/_production_effects.py`, `scripts/rehearse/_dashboard_regen.py`, and `memory/topics/deployment.md`, unless Prime can prove specific entries are historical-only and non-operative.

## Positive Evidence

- The indexed bridge thread is coherent: `show_thread_bridge.py gtkb-isolation-018-agent-red-cutover --format json` returned `drift: []`.
- The owner authorization exists: `DELIB-20260875` includes the cited PAUTH, owner answer, included WI, governing specs, allowed mutation classes, and forbidden operations.
- The formal approval packet exists at `.groundtruth/formal-artifact-approvals/2026-06-04-PAUTH-isolation-018-agent-red-cutover.json`.
- `gt backlog list --id GTKB-ISOLATION-018 --json` finds the open/backlogged work item under project `GTKB-ISOLATION`, subproject `Agent Red cutover`.
- `git ls-files` confirms the source files `shopify.app.toml`, `package.json`, and `package-lock.json` are tracked, while destination files under `applications/Agent_Red/` are absent.
- File content supports the Agent Red identity claim: root `package.json` names `agent-red-customer-experience`, and root `shopify.app.toml` self-identifies as Agent Red Shopify app configuration.

## Applicability Preflight

- packet_hash: `sha256:a02b4576c6d24f780215bcfb3be5c02d10cfcf59b2c8785054d62ebce4a8169a`
- bridge_document_name: `gtkb-isolation-018-agent-red-cutover`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-agent-red-cutover-001.md`
- operative_file: `bridge/gtkb-isolation-018-agent-red-cutover-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, content:applications/, content:Agent Red, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-isolation-018-agent-red-cutover`
- Operative file: `bridge\gtkb-isolation-018-agent-red-cutover-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Required Revision

Revise the bridge packet with a corrected reference inventory. The revision should either bring the live reference-bearing surfaces into scope or explicitly classify and defer them with evidence. After that revision, this proposal should be straightforward to approve.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
