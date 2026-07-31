NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; transcript-defined PB role; no direct harness contact

# Implementation Proposal - Cross-harness proposal linkage enforcement

bridge_kind: prime_proposal
Document: gtkb-wi5409-cross-harness-proposal-linkage-gate
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5409-PROPOSAL-LINKAGE-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5409

target_paths: [".claude/skills/bridge-propose/helpers/write_bridge.py", ".codex/skills/bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py", "platform_tests/skills/test_bridge_propose_helper.py"]

implementation_scope: source and test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Close the cross-harness proposal-filing bypass exposed when `gtkb-research-clean-branch-publication` cited `WI-5403` under `PROJECT-GTKB-TREE-STABILIZATION-WORKTREE-FINALIZATION`, although authoritative MemBase assigns `WI-5403` to the dispatcher black-box project for applicability target-scope separation. The mismatched proposal was written, dispatched, and reviewed because the generic helper path does not invoke the compliance audit that the Codex-specific path already invokes.

Move the existing in-memory audit into the generic publication path before work-intent acquisition or numbered-file creation. No dispatcher, TAFE, worker, lease, routing, eligibility, runtime, credential, release, deployment, or push state changes.

## Claim

Prime Builder proposes a bounded `WI-5409` implementation that makes every projected bridge-propose helper fail closed on the same live project/PAUTH/work-item membership contract.

## Requirement Sufficiency

Existing requirements are sufficient. `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` already requires a matching tuple; the defect is incomplete enforcement parity across helper entry points.

## In-Root Placement Evidence

All four target paths are within `E:\GT-KB`. The canonical helper and its Codex projection are currently byte-identical and clean; the scaffold template and focused test are also clean before implementation.

## Specification Links

- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the cited PAUTH, project, and work item to resolve to active matching MemBase state.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires governed numbered-file publication and role-correct authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links before review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires mapped executed evidence before VERIFIED.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires identical enforcement semantics across active harness projections.
- `ADR-CROSS-HARNESS-PARITY-001` - requires canonical/template/projection consistency.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires helper-level enforcement when native hooks are absent or bypassed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the observed mismatch to be preserved as WI-5409 and TEST-11520 before repair.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - keeps defect, proposal, implementation, test, and verdict evidence linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps proposal, implementation, and verification distinct.
- `GOV-STANDING-BACKLOG-001` - keeps the detected defect visible until verified.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform helper repair in the GT-KB root.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - permits bounded carriers for newly observed fleet and bridge defects while preserving all ordinary gates.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` - preserves the earlier proposal-standards collision-gate context; WI-5409 is the newly observed cross-harness enforcement gap.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes this bounded repair program.
- Active authorization `PAUTH-DISPATCHER-BLACK-BOX-WI5409-PROPOSAL-LINKAGE-20260717` includes only WI-5409 and permits bridge, metadata, source, test, and governance-evidence work while forbidding dispatcher mutation, external-system mutation, destructive cleanup, credential lifecycle, Git history rewrite, push, deployment, and release.

## Proposed Scope

1. Invoke `_run_bridge_compliance_audit` in `propose_bridge` after credential handling and author-metadata normalization, but before file-existence mutation, work-intent acquisition, directory creation, or file write.
2. Preserve the existing Codex non-bypass audit and make the canonical `.claude`, `.codex`, and scaffold-template helpers behaviorally identical.
3. Add focused tests proving a compliance denial creates no file and acquires no work-intent claim, while a passing proposal retains exactly one claim/write/release sequence.
4. Preserve prior-deliberation seeding, credential scan/redaction, author metadata, append-only collision checks, and every non-proposal route.

## Cross-Harness Disposition

- **Claude Code B:** the canonical `.claude` helper gains the existing compliance audit before generic proposal publication; no native-hook or role behavior changes.
- **Codex A:** the `.codex` helper remains byte-identical to the canonical helper, and the existing `propose_bridge_codex_non_bypass` behavior is preserved.
- **Antigravity C:** the generic helper path that allowed the observed mismatched proposal now receives the same audit; proposal capability remains available when metadata is valid.
- **Cursor E:** no Cursor LO execution or governed-verdict publication path changes; Cursor does not gain proposal authority.
- **Ollama D, OpenRouter F, and Alibaba H:** provider LO adapters and dispatcher routes are untouched; any future projected Prime proposal use receives the same helper-level validation without eligibility, model, cap, or lifetime changes.
- No typed waiver is requested. Behavioral parity is required for every helper projection and scaffold adopter.

## Specification-Derived Verification

| Specification | Verification | Expected result |
| --- | --- | --- |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python -m pytest platform_tests/skills/test_bridge_propose_helper.py platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py -q --tb=short` | Mismatched project/WI membership is denied before publication; matching membership passes. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python -m pytest platform_tests/skills/test_bridge_propose_helper_work_intent.py -q --tb=short` | Compliance denial creates no file and no work-intent residue; passing publication keeps one claim lifecycle. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, `ADR-CROSS-HARNESS-PARITY-001` | `python scripts/generate_codex_skill_adapters.py --update-registry --check` plus direct SHA-256 comparison of canonical/Codex helpers | Projection parity passes and helper bytes match. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m ruff check` and `python -m ruff format --check` on the four target paths where applicable | Focused source/test quality gates pass. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Focused unit test invokes `propose_bridge` directly with the audit stubbed to deny | Direct helper call fails closed independently of native hook delivery. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `gt backlog show WI-5409 --json` and `gt tests show TEST-11520` | The hygiene WI and linked integration test remain present and open until verified. |

## Acceptance Criteria

- A status-bearing proposal whose `Project` and `Work Item` lack active matching MemBase membership raises `BridgeComplianceError` and creates no bridge file or work-intent residue.
- A correctly linked proposal still writes once after compliance, credential, provenance, and work-intent checks.
- Canonical, Codex, and scaffold helper implementations retain parity.
- Existing helper, work-intent, membership-gate, Ruff, and adapter-parity tests pass.
- No active worker, dispatcher/TAFE state, harness eligibility, runtime, lease, Git index, push, deployment, or release state changes.

## Risks / Rollback

The risk is accidentally making the generic helper unusable for valid proposals or acquiring a claim before denial. Ordering and focused tests make both fail closed. Rollback reverts only the exact helper/template/test hunks; bridge and MemBase audit evidence remains append-only.

## Files Expected To Change

- `.claude/skills/bridge-propose/helpers/write_bridge.py`
- `.codex/skills/bridge-propose/helpers/write_bridge.py`
- `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`
- `platform_tests/skills/test_bridge_propose_helper.py`

## Recommended Commit Type

`fix`
