NEW

# WI-4978 Helper Compliance Audit Chokepoint

bridge_kind: prime_proposal
Document: gtkb-wi4978-helper-compliance-audit-chokepoint
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-05 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4978-BATCH-A2-20260705
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4978

target_paths: ["scripts/gtkb_bridge_writer.py", ".codex/skills/bridge-propose/helpers/write_bridge.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py", ".codex/skills/bridge/helpers/revise_bridge.py", ".claude/skills/bridge/helpers/revise_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py", ".codex/skills/bridge/helpers/impl_report_bridge.py", ".claude/skills/bridge/helpers/impl_report_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/skills/test_bridge_propose_helper.py", "platform_tests/skills/test_bridge_revise_helper.py", "platform_tests/skills/test_bridge_impl_report_helper.py"]

implementation_scope: source/test/hook-parity/governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4978 captures a defense-in-depth hole in bridge helper filing paths. The Codex `propose_bridge_codex_non_bypass()` path already runs `.claude/hooks/bridge-compliance-gate.py --audit-only` against in-memory content before writing. However, sibling helper paths for revisions and implementation reports write through lower-level subprocess/file helpers; those paths can bypass the Write-tool hook and may persist bridge content that is missing mandatory elements such as `## Requirement Sufficiency`.

This proposal closes the bypass at the helper-routed bridge write chokepoint. Helper-managed bridge writes must run the same bridge-compliance audit used by the Codex proposal path before any numbered bridge file is written. Valid bridge verdict/report/proposal content continues to pass; invalid helper content fails before disk mutation. The implementation must preserve existing credential scanning, evidence-anchor checks, author metadata validation, version-conflict checks, and latest-status checks.

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - mandatory proposal elements must be mechanically enforced across helper write paths, not only by human review.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - status-bearing numbered bridge files are canonical workflow state and must not be written through a weaker path.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Batch A2 PAUTH permits this bounded helper/source/test fix but does not replace LO review or implementation-start authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization and helper convenience do not bypass the bridge gate.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation must stay within the named WI-4978 helper/writer/test envelope.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries PAUTH, project, and work-item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the mandatory bridge-governance and cross-harness surfaces that constrain the work.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation verification must map mandatory-element enforcement to focused tests and command output.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - the bridge helper behavior must be consistent across Claude, Codex, templates, and headless helper routes.
- `ADR-CROSS-HARNESS-PARITY-001` - helper parity changes must avoid divergent behavior between harness copies.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - generated/template parity must be preserved or explicitly justified.
- `GOV-STANDING-BACKLOG-001` - WI-4978 must reach terminal state only with durable bridge and verification evidence.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - implementation must inspect current helper code paths and tests rather than rely on the historical WI text alone.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - this repair preserves the defect, proposal, implementation report, and verification evidence as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - helper behavior changes are captured in bridge/test artifacts rather than informal session state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - a helper write attempt is the lifecycle trigger where malformed bridge artifacts must be stopped.

## Prior Deliberations

- `WI-4978` backlog text - observed after `gtkb-wi4977-headless-dispatch-stability-003` was filed without `## Requirement Sufficiency`; LO caught it at review, but the helper path had already persisted the malformed artifact.
- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner authorized continuing Batch A2 high-priority reliability fixes through governed bridge work.
- `.groundtruth/formal-artifact-approvals/2026-07-05-DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE.json` - approval packet for that owner decision; scoped here by PAUTH and LO review.
- `bridge/gtkb-wi4977-headless-dispatch-stability-004.md` - NO-GO context that exposed the missing Requirement Sufficiency defense-in-depth hole.
- `bridge/gtkb-pre-filing-preflight-hook-*` lineage - established mechanical proposal preflight/compliance expectations for bridge authoring paths.

## Owner Decisions / Input

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved continuing the high-priority queue through governed implementation/disposition work.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4978-BATCH-A2-20260705` - active Batch A2 authorization for WI-4978 helper source, tests, and governance evidence.

No additional owner decision is required. This proposal still requires Loyal Opposition `GO` and an implementation-start packet before protected mutation.

## Requirement Sufficiency

Existing requirements sufficient.

Existing bridge rules and mechanical-enforcement specifications already require `Requirement Sufficiency`, project-linkage metadata, specification links, owner-decision sections when applicable, body status tokens, and cross-harness dispositions where triggered. WI-4978 is a helper-route enforcement defect, not a new policy question.

## Proposed Implementation

1. Add or expose a shared helper-level bridge-compliance audit function that invokes `.claude/hooks/bridge-compliance-gate.py --audit-only` with the candidate bridge file path and in-memory content, matching the existing Codex proposal helper payload shape.
2. Route helper-managed numbered bridge writes through that audit before disk mutation. The preferred chokepoint is `scripts/gtkb_bridge_writer.write_bridge_file()` because revision, implementation-report, and verdict helpers already use it; if implementation shows that a caller writes outside the chokepoint, update that caller or document why it is already protected.
3. Preserve existing gates and ordering:
   - credential scanning still runs in proposal/revision/report helpers before write;
   - bridge-compliance audit runs before the file exists on disk;
   - evidence-anchor validation and author metadata validation remain enforced;
   - existing conflict/latest-status checks still fail closed.
4. Keep the Codex proposal helper's explicit non-bypass behavior. If duplicate audit calls would become noisy, refactor it to reuse the shared audit primitive rather than removing the protection.
5. Update Claude, Codex, and template helper copies together where direct helper code changes are required; do not introduce divergent mandatory-element semantics.

## Cross-Harness Disposition

Target paths touch shared bridge helpers under `.claude/`, `.codex/`, and `groundtruth-kb/templates/`. The intended outcome is parity, not a harness-specific exception:

- Claude helper path: either receives the same shared audit through `scripts/gtkb_bridge_writer.py` or an identical direct call where it bypasses the writer.
- Codex helper path: retains the explicit `propose_bridge_codex_non_bypass()` audit and gains the same protection for revise/report helper routes.
- Template path: mirrors the live helper changes so regenerated/adopted installations receive the same enforcement.
- No waiver is requested for cross-harness parity.

## Spec-Derived Verification Plan

| Governing surface | Required behavior | Verification |
| --- | --- | --- |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` and `GOV-FILE-BRIDGE-AUTHORITY-001` | Helper-routed writes fail before disk write when mandatory bridge-compliance elements are absent. | `platform_tests/scripts/test_gtkb_bridge_writer.py` adds a malformed proposal/revision fixture missing `## Requirement Sufficiency` and asserts no numbered file is written. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Valid content with concrete specification links still passes. | Existing and new writer/helper positive tests continue to write valid bridge files. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001`, `ADR-CROSS-HARNESS-PARITY-001`, and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Claude, Codex, and template helper copies share the same mandatory-element behavior. | Focused helper tests cover Codex helper paths; static or parity assertions cover mirrored helper/template code where existing tests support it. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Helper convenience cannot bypass bridge compliance; PAUTH does not authorize malformed bridge writes. | `platform_tests/skills/test_bridge_revise_helper.py` and `platform_tests/skills/test_bridge_impl_report_helper.py` assert invalid completed content is rejected before live file creation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries exact test and lint evidence. | Post-implementation report includes pytest and ruff command output. |

Minimum verification commands after GO:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/skills/test_bridge_propose_helper.py platform_tests/skills/test_bridge_revise_helper.py platform_tests/skills/test_bridge_impl_report_helper.py -q --tb=short --basetemp .gtkb-state/pytest-tmp-wi4978
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/gtkb_bridge_writer.py .codex/skills/bridge-propose/helpers/write_bridge.py .claude/skills/bridge-propose/helpers/write_bridge.py groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py .codex/skills/bridge/helpers/revise_bridge.py .claude/skills/bridge/helpers/revise_bridge.py groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py .codex/skills/bridge/helpers/impl_report_bridge.py .claude/skills/bridge/helpers/impl_report_bridge.py groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/skills/test_bridge_propose_helper.py platform_tests/skills/test_bridge_revise_helper.py platform_tests/skills/test_bridge_impl_report_helper.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/gtkb_bridge_writer.py .codex/skills/bridge-propose/helpers/write_bridge.py .claude/skills/bridge-propose/helpers/write_bridge.py groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py .codex/skills/bridge/helpers/revise_bridge.py .claude/skills/bridge/helpers/revise_bridge.py groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py .codex/skills/bridge/helpers/impl_report_bridge.py .claude/skills/bridge/helpers/impl_report_bridge.py groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/skills/test_bridge_propose_helper.py platform_tests/skills/test_bridge_revise_helper.py platform_tests/skills/test_bridge_impl_report_helper.py
```

## Acceptance Criteria

- A helper-routed attempt to write a malformed implementation proposal or revision missing `## Requirement Sufficiency` fails before creating `bridge/<slug>-NNN.md`.
- Valid revision, implementation-report, verdict, and proposal helper writes still succeed.
- Existing evidence-anchor and author-metadata gates still run and their tests remain green.
- Claude/Codex/template helper behavior remains aligned, with no new harness-specific bypass.
- No KB rows, credentials, deployments, destructive cleanup, broad status mutation, or bridge-history rewrite is performed.

## Risk / Rollback

Risk is moderate because `write_bridge_file()` is a high-traffic bridge chokepoint. The mitigation is focused regression coverage for malformed and valid artifacts, plus preserving existing caller-side checks. Rollback is a single revert of the helper/writer/test diff; bridge audit files remain append-only and no schema change is proposed.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4978-helper-compliance-audit-chokepoint`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` because the eventual diff closes a concrete bridge-helper enforcement defect.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
