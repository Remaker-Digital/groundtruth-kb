NO-GO

# Loyal Opposition Review - Worktree cwd / Project-Root Resolution in Bridge Governance Hooks (WI-3353)

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-16 16:31 America/Los_Angeles
Reviewed proposal: `bridge/gtkb-governance-hook-worktree-root-resolution-001.md`
Verdict: NO-GO

## Claim

NO-GO. The proposed technical direction is coherent, and the mandatory bridge preflights pass, but the proposal's own live project/work-item linkage fails the canonical bridge-compliance gate. `WI-3353` is not an active member of the cited project `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` in `current_project_work_item_memberships`. Because the proposal also cites `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`, and because `.claude/hooks/bridge-compliance-gate.py` hard-blocks this condition, Prime must repair the project membership or revise the metadata before implementation can receive GO.

This is a governance-packet blocker, not a rejection of the worktree-aware root-resolution design.

## Review Scope

Reviewed:

- `bridge/gtkb-governance-hook-worktree-root-resolution-001.md`
- `bridge/INDEX.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`
- `.claude/hooks/bridge-compliance-gate.py`
- `scripts/implementation_start_gate.py`
- `scripts/implementation_authorization.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/paths.py`
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
- `scripts/cross_harness_bridge_trigger.py`
- `groundtruth.db` read-only views: `current_project_authorizations`, `current_project_work_item_memberships`, `current_work_items`, `current_projects`, `current_deliberations`

## Findings

### F1 - P1 - The cited work item is not an active member of the cited project

Observation: The proposal cites:

- `Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WORKTREE-ROOT-RESOLUTION`
- `Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- `Work Item: WI-3353`

The PAUTH exists and is active, and its `included_work_item_ids` contains `WI-3353`. However, the canonical membership table has no active row for `WI-3353` under `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`. Instead, `WI-3353` is active under duplicate project id `PROJECT-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, apparently produced from the compatibility `current_work_items.project_name` value.

Evidence:

- Proposal metadata: `bridge/gtkb-governance-hook-worktree-root-resolution-001.md:12`, `:13`, `:14`.
- Bridge-compliance gate requires membership first: `.claude/hooks/bridge-compliance-gate.py:309`, `:325`, `:334`, `:338`.
- Read-only DB check:
  - `SELECT ... FROM current_project_work_item_memberships WHERE work_item_id='WI-3353' AND project_id='PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY'` returned `[]`.
  - `SELECT ... WHERE work_item_id='WI-3353'` returned `('PWM-PROJECT-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-3353', 'PROJECT-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY', 'WI-3353', 'active')`.
  - `SELECT ... FROM current_project_authorizations WHERE id='PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WORKTREE-ROOT-RESOLUTION'` returned active status and `included_work_item_ids=["WI-3353"]`.
- Direct canonical gate check on the operative proposal returned:
  - `[Governance] Bridge proposal fails the live work-item/project membership check: wi-not-found-in-project. Cited WI=WI-3353, Project=PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY, Project Authorization=PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WORKTREE-ROOT-RESOLUTION.`

Impact: If Loyal Opposition issued GO, the audit trail would approve a proposal whose own canonical compliance gate denies it. That undermines `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001/CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP` and lets a helper-filed proposal bypass the same project/WI chain the implementation claims to repair.

Recommended action: Before resubmission, repair MemBase state so `WI-3353` is an active member of the real project `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, or revise the proposal/project authorization metadata so all three surfaces point to the same active project. Do not retarget the work to the duplicate `PROJECT-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` project without an explicit governance rationale; that duplicate appears to be compatibility backfill fallout, not the owner-selected project. After repair, rerun the canonical gate check against the operative proposal and cite the passing evidence in the REVISED file.

## Checks That Passed

- The selected bridge entry is still latest `NEW` in live `bridge/INDEX.md`.
- The proposal includes in-root `target_paths` and the required `Requirement Sufficiency`, `Specification Links`, `Owner Decisions / Input`, prior deliberation, acceptance, risk/rollback, and spec-derived verification sections.
- The live hook and scaffold template are currently byte-identical by SHA-256, matching the proposal's scaffold-synchronization premise.
- Code inspection confirms the technical defect mechanics:
  - `groundtruth-kb/src/groundtruth_kb/bridge/paths.py:71` still resolves via `git rev-parse --show-toplevel`.
  - `.claude/hooks/bridge-compliance-gate.py:325`, `:676`, and `:803` use `cwd_path` for project-state access.
  - `scripts/implementation_start_gate.py:94` to `:98` trusts `payload["project_root"]` or `payload["cwd"]`.
  - `scripts/implementation_authorization.py:100` to `:103` defaults to `Path(__file__).resolve().parent.parent`.
  - `scripts/cross_harness_bridge_trigger.py:134` delegates to `groundtruth_kb.bridge.paths.resolve_project_root()`.

## Prior Deliberations

Deliberation search method: direct read-only query over `current_deliberations`, because the `gt` console entry point was unavailable in the ambient shell and direct `python -m groundtruth_kb.cli` lacked `click` in the ambient Python. Search terms included `WI-3353`, `worktree`, `project root resolution`, `git common dir`, `bridge governance hooks`, and `project authorization`.

Relevant records:

- `DELIB-S356-WI-3353-DEDICATED-PROJECT-AUTHORIZATION` directly authorizes the dedicated PAUTH for this work and states that the authorization does not bypass bridge review, target paths, implementation-start packets, or verification.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` records the owner directive that work flows through specifications, projects, work items, and bridge dispatch; this supports rejecting a proposal whose WI/project linkage is not mechanically true.
- `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` establishes that project authorization reduces repeated owner approval overhead but preserves per-proposal Loyal Opposition review and implementation-start controls.
- No relevant prior deliberation found that rejects the proposed worktree-aware root-resolution design.

## Applicability Preflight

- packet_hash: `sha256:ecad10502da9a6d7b3d1a235496bc40d9dee734afb707b41bd833aa9c7aefb4a`
- bridge_document_name: `gtkb-governance-hook-worktree-root-resolution`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-governance-hook-worktree-root-resolution-001.md`
- operative_file: `bridge/gtkb-governance-hook-worktree-root-resolution-001.md`
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
- Operative file: `bridge\gtkb-governance-hook-worktree-root-resolution-001.md`
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

- Defect pass: material blocker F1 above.
- Token-savings pass: no material token-cost issue beyond normal bridge-review overhead.
- Deterministic-service pass: this review exposed a helper/preflight gap. The bridge-propose helper path can file a proposal that the canonical bridge-compliance gate denies. Candidate replacement surface: a deterministic helper or preflight step that runs the same membership/authorization check against the canonical project root before `INDEX.md` mutation.
- Surface eligibility: likely `gt bridge propose` / bridge-propose helper, with residual human judgement limited to deciding whether a failed membership means "repair project homing" or "revise proposal metadata."
- Routing: captured in this NO-GO because it directly explains how this thread reached actionable state despite the gate failure. No separate advisory file was created under this auto-dispatch's selected-entry scope.

## Decision Needed

No owner decision is needed from Loyal Opposition at this point. Prime Builder needs to repair or revise the project/WI linkage and file a REVISED proposal.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
