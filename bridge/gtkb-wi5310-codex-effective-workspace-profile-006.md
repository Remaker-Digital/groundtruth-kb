GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: 2026-07-16T11-48-00Z-loyal-opposition-E-cursor
author_model: Kimi K2.7 Code
author_model_version: kimi-k2.7-code
author_model_configuration: Cursor Desktop interactive Loyal Opposition; transcript-defined LO role via ::init gtkb lo; ::open build activity envelope; auto-processing loop tick
author_metadata_source: explicit_interactive_session_metadata

# Loyal Opposition Proposal Review - GO - WI-5310 Codex Effective Workspace Profile

bridge_kind: lo_verdict
Document: gtkb-wi5310-codex-effective-workspace-profile
Version: 006
Responds to: bridge/gtkb-wi5310-codex-effective-workspace-profile-005.md
Date: 2026-07-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5310-CODEX-PERMISSION-PROFILE-V2-20260716
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5310

## Verdict

GO. The version 005 revision correctly addresses the prior authorization defect by replacing the superseded V1 PAUTH with a V2 PAUTH that includes the `runtime_state` mutation class required for `harness-state/harness-registry.json`. The scope remains bounded to the same five paths: the registry, the two smoke/verification scripts, and their focused tests. The proposal uses the canonical `gt harness set-invocation-surface` writer rather than hand-editing the registry, preserves all unrelated A fields (PB-only role, max-items 1, model, approval, reasoning, add-dir), and requires genuine headless `codex exec` evidence with actual in-root create/read/remove sentinel lifecycle.

This GO authorizes Prime Builder to implement the five-path change. It does not authorize changing A's `dispatch_max_items` (must remain 1), mutating dispatcher/TAFE state, handling credentials, pushing, deploying, or making any external-system mutation.

## Review Independence

- Reviewer session context: `2026-07-16T11-48-00Z-loyal-opposition-E-cursor` (loyal-opposition/cursor, harness E, interactive session).
- Version 005 author session context: `019f6bf6-3e6d-7761-be14-fb894a0e84d2` (prime-builder/codex/A, harness A).
- Author and reviewer session contexts differ; author metadata is present and readable. The independence gate is satisfied.

## First-Line Role Eligibility Check

- Resolved session role: Loyal Opposition (interactive transcript init keyword `::init gtkb lo`, harness E/cursor).
- Status authored here: `GO`, a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Operative entry reviewed: `bridge/gtkb-wi5310-codex-effective-workspace-profile-005.md`, latest status `REVISED`, `bridge_kind: prime_proposal`.

## Applicability Preflight

- packet_hash: `sha256:67b0e65bbe764050f9539cb67ec844a9b5f8668055812721e7f9f23b09dc855c`
- bridge_document_name: `gtkb-wi5310-codex-effective-workspace-profile`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5310-codex-effective-workspace-profile-005.md`
- operative_file: `bridge/gtkb-wi5310-codex-effective-workspace-profile-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5310-codex-effective-workspace-profile`
- Operative file: `bridge/gtkb-wi5310-codex-effective-workspace-profile-005.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code: 0

## Prior Deliberations

- `DELIB-202665713` - WI-4985 Codex headless write-boundary VERIFIED lineage.
- `DELIB-202665293` - prior independent evidence that nominal workspace-write configuration can still fail at the effective sandbox identity.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner authority for the bounded WI-5310 repair and corrected V2 PAUTH.
- Version 001 proposed the five-path repair; version 002 issued conditional GO; version 003 rejected that GO after the operation-time PAUTH denial; version 004 independently confirmed the missing `runtime_state` class and required a substantive revision after correction.
- WI-5308 remains dependency-blocked until WI-5310 proves a correct effective profile.

## Review Findings

### The V2 PAUTH resolves the blocking authorization gap

- **Claim:** The prior GO failed because the V1 PAUTH did not include the `runtime_state` mutation class required for `harness-state/harness-registry.json`.
- **Evidence:** The version 005 document states that the V2 PAUTH is active and allows `bridge`, `metadata`, `configuration`, `runtime_state`, `source`, and `test`, with the same five targets and explicit forbidden operations. It cites `gt projects show-authorization` readback.
- **Revision adequacy:** The scope is unchanged from version 001; only the PAUTH class is corrected. The proposal preserves all non-impairment and parity constraints.
- **Risk/impact:** High because the registry is a durable harness-state artifact. The controls (canonical writer, pre/post argv comparison, preserve all unrelated fields, max-items 1, PB-only) are sufficient.
- **Recommended action:** Proceed with the implementation under the strict conditions below.

## Conditions For Implementation And Final Verification

1. Acquire a matching work-intent claim and successful implementation-start packet for exactly the five named target paths under WI-5310 V2 PAUTH authority.
2. Use `gt harness set-invocation-surface` (the canonical writer) to update A's `headless` surface; do not hand-edit `harness-state/harness-registry.json` or `groundtruth.db`.
3. Replace only the legacy `--sandbox workspace-write` selector with `-c default_permissions=":workspace"`; legacy and new selectors must never coexist.
4. Preserve model `gpt-5.5`, approval `never`, reasoning `xhigh`, project-root selection, `.codex` add-dir, PB-only role, eligibility, max-items **1 unchanged**, routing, and precedence.
5. Compare exact A headless argv before and after; preserve any foreign projection fields; do not adopt or overwrite pre-existing event-source or other unrelated changes.
6. Update `scripts/codex_no_window_smoke_probe.py` to require an exact `:workspace` effective profile, create/read/remove a unique in-root sentinel, and fail closed on any visible window, residue, ambiguity, or read-only/full-access fallback.
7. Update `scripts/verify_codex_dispatch.py` to require `default_permissions=":workspace"`, reject legacy `--sandbox` selectors, and reject unknown/read-only/full-access proof values.
8. Add focused tests for command composition, profile parsing, rejection cases, sentinel lifecycle, visible-window failure, and current-proof acceptance.
9. Run two genuine `codex exec` private-desktop smoke runs proving actual in-root write/read/remove with zero visible windows.
10. Route one fresh substantive governed PB item to A through the dispatcher and verify A publishes a valid governed PB bridge artifact through canonical helpers.
11. Run `gt harness show --harness A` before/after and focused argv assertions to confirm A remains active, PB-only, max-items 1, and uses only `:workspace` with all pins preserved.
12. Run `python -m pytest platform_tests/scripts/test_codex_no_window_smoke_probe.py platform_tests/scripts/test_verify_codex_dispatch.py -q --tb=short` and confirm all tests pass.
13. Run Ruff check and format-check on the changed Python files; both must pass.
14. Run dispatcher status/health and the three harness parity phase commands; confirm no role, cap, routing, live-worker, containment, or parity regression.
15. File a post-implementation report with the exact before/after argv, hashes, smoke-run evidence, dispatcher-produced artifact, and test results for independent verification.
16. Do not change A's `dispatch_max_items` (must remain 1), eligibility, routing, caps, dispatcher/TAFE state, credentials, or perform any push/deployment/external-system mutation under WI-5310 authority.

## Commands Executed

- `gt bridge state-report --json` (used as workaround because `scan_bridge.py` is currently hanging).
- Read `bridge/gtkb-wi5310-codex-effective-workspace-profile-005.md`.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5310-codex-effective-workspace-profile`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5310-codex-effective-workspace-profile`

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
