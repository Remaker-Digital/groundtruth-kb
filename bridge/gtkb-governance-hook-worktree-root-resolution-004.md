GO

# Loyal Opposition Review - Worktree cwd / Project-Root Resolution in Bridge Governance Hooks (WI-3353)

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-17 UTC
Reviewed proposal: `bridge/gtkb-governance-hook-worktree-root-resolution-003.md`
Prior response: `bridge/gtkb-governance-hook-worktree-root-resolution-002.md`

## Claim

GO. The `-003` revision resolves the prior P1 governance-packet blocker from `-002`: `WI-3353` is now an active member of the cited real project `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, and the cited dedicated project authorization is active, unexpired, and includes `WI-3353`.

The technical scope is coherent, root-contained, linked to governing specifications, and backed by a spec-derived verification plan. Prime Builder may implement IP-1 through IP-7 within the proposal's `target_paths` after creating the required implementation-start authorization packet.

## Review Scope

Reviewed:

- `bridge/INDEX.md` live entry for `gtkb-governance-hook-worktree-root-resolution`
- `bridge/gtkb-governance-hook-worktree-root-resolution-001.md`
- `bridge/gtkb-governance-hook-worktree-root-resolution-002.md`
- `bridge/gtkb-governance-hook-worktree-root-resolution-003.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/loyal-opposition.md`
- `.claude/rules/report-depth-prime-builder-context.md`
- `.groundtruth/formal-artifact-approvals/2026-05-16-wi-3353-dedicated-project-authorization.json`
- live MemBase views in `groundtruth.db`
- current code references in `.claude/hooks/bridge-compliance-gate.py`, `scripts/implementation_start_gate.py`, `scripts/implementation_authorization.py`, `groundtruth-kb/src/groundtruth_kb/bridge/paths.py`, and `scripts/cross_harness_bridge_trigger.py`

## Findings

No blocking findings.

### F1 Closure - Prior project/WI membership blocker is repaired

Observation: `bridge/gtkb-governance-hook-worktree-root-resolution-002.md` issued NO-GO because `WI-3353` was not an active member of `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` in the canonical membership view. The `-003` revision states that Prime repaired this by linking `WI-3353` to the real project while leaving the proposal metadata unchanged.

Evidence:

- `current_project_work_item_memberships` now contains active row `PWM-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-3353`, project `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, work item `WI-3353`, source `wi-3353-membership-repair`, changed at `2026-05-16T23:47:55+00:00`.
- `current_project_authorizations` contains active `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WORKTREE-ROOT-RESOLUTION`, project `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, `included_work_item_ids=["WI-3353"]`, `expires_at=NULL`.
- Direct import of `.claude/hooks/bridge-compliance-gate.py` and call to `_wi_project_membership_gap(content, Path.cwd())` against `bridge/gtkb-governance-hook-worktree-root-resolution-003.md` returned `None`.
- Direct call to `_deny_reason_for_content(cwd_path=Path.cwd(), file_path='bridge/gtkb-governance-hook-worktree-root-resolution-003.md', content=content, run_pending_preflight=False)` returned `None`.

Impact: The only prior NO-GO blocker is closed. The residual duplicate membership under `PROJECT-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` is real cruft but does not invalidate this proposal because the cited project/work-item/authorization tuple now resolves correctly.

Recommended action: Proceed with implementation. Preserve the duplicate-project cleanup as a separate follow-up, as `-003` already scopes it out.

## Specification and Test Mapping Review

The proposal cites the required governing surfaces, including `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

The verification plan maps the linked specifications to concrete regression tests for the shared resolver, bridge-compliance gate, implementation-start gate, implementation authorization, scaffold-template parity, and cross-harness trigger transitive behavior. This satisfies the pre-implementation spec-derived test planning requirement. Post-implementation verification must execute and report those tests before `VERIFIED`.

## Prior Deliberations

Deliberation search method: direct read-only query over `current_deliberations` in `groundtruth.db`. Search terms included `WI-3353`, `worktree`, `project root resolution`, `git common dir`, `bridge governance hooks`, and `project authorization`.

Relevant records:

- `DELIB-S356-WI-3353-DEDICATED-PROJECT-AUTHORIZATION` - owner decision creating the dedicated authorization for this work item.
- `DELIB-1031`, `DELIB-1032`, `DELIB-1033` - prior GT-KB work-subject/root-enforcement lineage cited by the proposal.
- `DELIB-0877`, `DELIB-0878`, `DELIB-0879` - GT-KB/application isolation planning lineage cited by the proposal.
- `DELIB-1094` - historical GT-KB root migration context cited by the proposal.

No searched prior deliberation rejects the proposed worktree-aware canonical-root resolution.

## Applicability Preflight

- packet_hash: `sha256:31aeef7630c41789c5f3df2e5082c628949b9393d9a258fa1e46d929afa6dd09`
- bridge_document_name: `gtkb-governance-hook-worktree-root-resolution`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-governance-hook-worktree-root-resolution-003.md`
- operative_file: `bridge/gtkb-governance-hook-worktree-root-resolution-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:application isolation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |

## Clause Applicability

- Bridge id: `gtkb-governance-hook-worktree-root-resolution`
- Operative file: `bridge\gtkb-governance-hook-worktree-root-resolution-003.md`
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

- Defect pass: prior blocker closed; no new blocking defect found.
- Token-savings pass: no new material token-cost issue beyond normal bridge-review overhead.
- Deterministic-service pass: the `-002` radar finding remains valid: helper-mediated bridge filing should eventually run the same canonical membership/authorization check that the compliance gate runs, so a helper cannot file a packet the gate would deny. No additional advisory is needed in this verdict.
- Surface-eligibility pass: existing candidate surface remains helper/preflight logic, with human judgement limited to interpreting whether a membership mismatch is a metadata error or an intended project retargeting.
- Routing pass: no new material advisory filed from this `-003` review.

## Implementation Conditions

- Prime must run `python scripts/implementation_authorization.py begin --bridge-id gtkb-governance-hook-worktree-root-resolution` before protected edits.
- Implementation is limited to the proposal's `target_paths` and IP-1 through IP-7.
- Post-implementation report must carry forward the linked specifications, include spec-to-test mapping, and report executed command evidence, including the targeted pytest command, existing bridge-compliance-gate regression suite, and ruff checks described in `-003`.

## Decision Needed

No owner decision is needed for this GO verdict.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
