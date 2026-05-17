GO

# Loyal Opposition Review - Worktree cwd / Project-Root Resolution in Bridge Governance Hooks (WI-3353)

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-17 UTC
Reviewed proposal: `bridge/gtkb-governance-hook-worktree-root-resolution-005.md`
Prior response: `bridge/gtkb-governance-hook-worktree-root-resolution-004.md`

## Claim

GO. The `-005` revision is a narrow target-path correction after the prior GO. It correctly replaces the non-existent `tests/scripts/test_cross_harness_bridge_trigger.py` target with the real in-root `platform_tests/scripts/test_cross_harness_bridge_trigger.py` path in the proposal metadata, IP-7 scope bullet, and verification command.

The worktree-aware root-resolution design approved in `-004` is unchanged. The project/work-item/authorization tuple still resolves correctly, the direct bridge-compliance gate checks pass against the operative `-005` proposal, and the mandatory applicability and clause preflights pass.

Prime Builder may implement IP-1 through IP-7 within the `-005` `target_paths` after creating a fresh implementation-start authorization packet from this GO.

## Review Scope

Reviewed:

- `bridge/INDEX.md` live entry for `gtkb-governance-hook-worktree-root-resolution`
- `bridge/gtkb-governance-hook-worktree-root-resolution-001.md`
- `bridge/gtkb-governance-hook-worktree-root-resolution-002.md`
- `bridge/gtkb-governance-hook-worktree-root-resolution-003.md`
- `bridge/gtkb-governance-hook-worktree-root-resolution-004.md`
- `bridge/gtkb-governance-hook-worktree-root-resolution-005.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/loyal-opposition.md`
- `.claude/rules/report-depth-prime-builder-context.md`
- `.groundtruth/formal-artifact-approvals/2026-05-16-wi-3353-dedicated-project-authorization.json`
- live MemBase views in `groundtruth.db`
- direct bridge-compliance gate functions in `.claude/hooks/bridge-compliance-gate.py`
- target path existence checks for the corrected and stale cross-harness trigger test paths

## Findings

No blocking findings.

### F1 Closure - The target-path correction is valid and in-root

Observation: `-005` corrects the cross-harness trigger regression test target from `tests/scripts/test_cross_harness_bridge_trigger.py` to `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.

Evidence:

- `bridge/gtkb-governance-hook-worktree-root-resolution-005.md:16` lists `platform_tests/scripts/test_cross_harness_bridge_trigger.py` in `target_paths`.
- `bridge/gtkb-governance-hook-worktree-root-resolution-005.md:20` to `:24` explains the `-003` path defect and states that only the metadata line, IP-7 bullet, and verification command changed.
- `bridge/gtkb-governance-hook-worktree-root-resolution-005.md:145` lists the corrected IP-7 bullet.
- `bridge/gtkb-governance-hook-worktree-root-resolution-005.md:164` lists the corrected pytest command.
- `Test-Path platform_tests/scripts/test_cross_harness_bridge_trigger.py` returned `True`.
- `Test-Path tests/scripts/test_cross_harness_bridge_trigger.py` returned `False`.
- The other existing target paths resolved in-root. `platform_tests/hooks/test_bridge_compliance_gate_worktree_root.py` does not exist yet, which is acceptable because `-005` proposes it as a new test file under an authorized target path.

Impact: The implementation-start authorization packet can now be minted against the real file surface. The gate-blocking mismatch that prevented implementation under `-003` is closed without broadening scope.

Recommended action: Proceed under this revised target-path surface. Do not use the stale `tests/scripts/...` path.

### F2 Confirmation - Project, work item, and PAUTH linkage still pass

Observation: The `-005` revision keeps the same project metadata as `-003`; the prior `-002` blocker remains repaired.

Evidence:

- Direct import of `.claude/hooks/bridge-compliance-gate.py` and call to `_wi_project_membership_gap(content, Path.cwd())` for `bridge/gtkb-governance-hook-worktree-root-resolution-005.md` returned `None`.
- Direct call to `_deny_reason_for_content(cwd_path=Path.cwd(), file_path='bridge/gtkb-governance-hook-worktree-root-resolution-005.md', content=content, run_pending_preflight=False)` returned `None`.
- `current_project_work_item_memberships` contains active row `PWM-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-3353`, project `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, work item `WI-3353`, source `wi-3353-membership-repair`, changed at `2026-05-16T23:47:55+00:00`.
- `current_project_authorizations` contains active `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WORKTREE-ROOT-RESOLUTION`, project `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, `included_work_item_ids=["WI-3353"]`, `expires_at=NULL`.

Impact: The proposal no longer conflicts with `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` or the bridge-compliance gate's project-linkage enforcement.

Recommended action: Preserve the duplicate-project cleanup as separate follow-up work, as already scoped out in `-005`.

## Specification and Test Mapping Review

The revision preserves the governing specification links approved in `-004`, including `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

The verification plan remains specification-derived and now names the correct cross-harness trigger test file. Post-implementation verification must execute and report the targeted pytest command, existing bridge-compliance-gate regression suite, and ruff checks described in `-005`.

## Prior Deliberations

Deliberation search note: a direct read-only `current_deliberations` query was attempted during this review, but the implementation-start gate blocked the shell command as a protected mutation against an unrelated terminal bridge thread. Because `-005` is only a target-path correction to the already reviewed `-003` proposal, this verdict carries forward the relevant deliberation search from `-004` and independently reviewed the formal approval packet for the owner decision that created the WI-3353 dedicated PAUTH.

Relevant records:

- `DELIB-S356-WI-3353-DEDICATED-PROJECT-AUTHORIZATION` - owner decision creating the dedicated authorization for this work item.
- `DELIB-1031`, `DELIB-1032`, `DELIB-1033` - prior GT-KB work-subject/root-enforcement lineage cited by the proposal.
- `DELIB-0877`, `DELIB-0878`, `DELIB-0879` - GT-KB/application isolation planning lineage cited by the proposal.
- `DELIB-1094` - historical GT-KB root migration context cited by the proposal.

No reviewed prior deliberation rejects the proposed worktree-aware canonical-root resolution or this `-005` path correction.

## Applicability Preflight

- packet_hash: `sha256:2f161757e674d81d79421fed8f43d0d293deaed72fdc289793b66d68a920f9be`
- bridge_document_name: `gtkb-governance-hook-worktree-root-resolution`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-governance-hook-worktree-root-resolution-005.md`
- operative_file: `bridge/gtkb-governance-hook-worktree-root-resolution-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:application isolation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |

## Clause Applicability

- Bridge id: `gtkb-governance-hook-worktree-root-resolution`
- Operative file: `bridge\gtkb-governance-hook-worktree-root-resolution-005.md`
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

Slice 2 mandatory gate note: clauses with `enforcement_mode = "blocking"` and `must_apply` applicability fail the gate when evidence is absent and no owner waiver is cited. No clause gaps were reported here.

## Opportunity Radar

- Defect pass: no blocking defect found; the path discrepancy is corrected in `-005`.
- Token-savings pass: no material token-cost issue found beyond normal bridge-review overhead.
- Deterministic-service pass: the implementation-start gate already caught the stale target path before implementation. No new advisory is warranted from this narrow review.
- Surface-eligibility pass: if this repeats, the likely surface is a bridge-proposal target-path linter that distinguishes existing files from intentionally new files.
- Routing pass: no separate advisory filed under this auto-dispatch scope.

## Implementation Conditions

- Prime must run `python scripts/implementation_authorization.py begin --bridge-id gtkb-governance-hook-worktree-root-resolution` before protected edits.
- Implementation is limited to the `-005` `target_paths` and IP-1 through IP-7.
- `platform_tests/hooks/test_bridge_compliance_gate_worktree_root.py` is authorized as a new test file under the approved target paths.
- Post-implementation report must carry forward the linked specifications, include spec-to-test mapping, report executed command evidence, and use the corrected `platform_tests/scripts/test_cross_harness_bridge_trigger.py` path.

## Decision Needed

No owner decision is needed for this GO verdict.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
