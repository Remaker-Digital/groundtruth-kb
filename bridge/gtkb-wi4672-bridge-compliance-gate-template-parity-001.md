NEW

# Bridge Compliance Gate Template Parity

bridge_kind: prime_proposal
Document: gtkb-wi4672-bridge-compliance-gate-template-parity
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-19 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-19T07-29-00Z-prime-builder-A-keep-working
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; Hygiene PB

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4672

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py"]

implementation_scope: hook_template_and_test_parity
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4672 captures a focused May29 Hygiene defect: the active bridge-compliance hook and the packaged scaffold template hook have drifted apart. The focused regression `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py::test_hook_matches_template_or_documented_divergence` fails because `.claude/hooks/bridge-compliance-gate.py` and `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` no longer have matching SHA-256 hashes.

This proposal asks for a narrow bridge-authorized parity repair. The implementation should compare the live active hook and the packaged template, decide whether byte-identical sync or an explicitly documented intentional divergence is correct, then update the smallest necessary files and focused tests so adopter/scaffold hook behavior cannot lag behind the active workspace hook unnoticed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Hook, template, and test mutations must wait for an approved bridge `GO` and a live implementation-start packet.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal carries concrete governing specification links for the hook/template change.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The proposal carries active PAUTH, project id, and WI-4672 metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification must prove parity is restored or the divergence is intentionally documented and tested.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - The active May29 Hygiene authorization covers unimplemented May29 work items such as WI-4672.
- `GOV-STANDING-BACKLOG-001` - WI-4672 is a governed backlog item and its closure must remain visible through backlog and bridge evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The active hook, scaffold template, tests, and bridge evidence must remain one coherent artifact graph.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The fix should preserve durable source/test/bridge alignment rather than treating the failing parity test as disposable.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The captured regression is being advanced from hygiene backlog to bridge-reviewed implementation scope.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All target paths are inside the GT-KB project root.

## Prior Deliberations

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` - Owner authorization for implementing unimplemented May29 Hygiene work items through the normal bridge/GO process.
- `DELIB-2169` - Archived GroundTruth-KB bridge-compliance-gate parity thread, latest VERIFIED, establishing prior expectation that active and packaged gate surfaces remain aligned.
- `DELIB-20263759` - Loyal Opposition NO-GO for WI-3315 found that bridge-compliance hook changes must include the packaged template when the parity regression expects byte-identical copies.
- `DELIB-20263237` - Loyal Opposition GO for WI-3439 carried forward the same deployment-copy parity expectation for bridge-compliance-gate changes.
- Focused search `gt deliberations search "bridge-compliance-gate template active hook parity WI-4672 WI-4308" --limit 10 --json` found prior parity and template-scope records, but no earlier WI-4672-specific bridge thread.

## Owner Decisions / Input

No new owner decision is required. Mike's automation instruction for this run explicitly asks PB to continue hygiene work, and active May29 Hygiene PAUTH authorizes proposals for unimplemented May29 work items. Implementation still requires Loyal Opposition `GO` before any target file mutation.

## Requirement Sufficiency

Existing requirements sufficient.

WI-4672 defines the failing test, the two hook/template files whose hashes differ, the acceptance direction, and the regression command. The implementation is bounded to restoring or intentionally documenting hook/template parity and proving the chosen behavior with focused tests. No new architecture decision, formal specification, or project authorization is required.

## Implementation Scope

Approved investigation and source changes after GO:

- Inspect `.claude/hooks/bridge-compliance-gate.py` and `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` from the current worktree before editing, because both may have unrelated concurrent changes.
- If the copies should be identical, sync the packaged template to the active hook or the active hook to the packaged template, preserving the intended latest bridge-compliance behavior.
- If a divergence is intentional, add explicit machine-checkable documentation or test allowances that explain and bound the divergence.
- Keep the fix scoped to bridge-compliance-gate parity; do not add unrelated hook behavior.

Approved test changes after GO:

- Update or extend `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py` so the parity expectation is executable and fails on future unintended drift.
- Add no broad test rewrites unless the existing parity test already provides the necessary coverage.

Out of scope:

- No bridge-rule semantic expansion beyond restoring/documenting parity.
- No changes to dispatcher routing, project authorization semantics, or implementation-start packet validation.
- No formal DA, GOV, SPEC, PB, ADR, or DCL mutation.
- No cleanup of unrelated dirty worktree changes.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Do not add credential-shaped fixtures or environment values; hook/template sync should be pure source/test text. | Bridge helper credential scan and changed-file review. | |
| CQ-PATHS-001 | Yes | Keep mutations inside the declared in-root hook/template/test paths. | Implementation-start packet and `git diff --name-only` scoped to target paths. | |
| CQ-COMPLEXITY-001 | Yes | Prefer byte-identical sync or one narrow documented-divergence allowance over new hook abstractions. | Focused parity test and source review. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing hook constants and test helpers; avoid duplicate parser literals unless the active hook already owns them. | Ruff and focused test review. | |
| CQ-SECURITY-001 | Yes | Preserve the stricter bridge-compliance behavior while syncing template deployment copies; do not weaken hard-block paths. | Existing hard-block regression tests plus parity test. | |
| CQ-DOCS-001 | N/A | | | No user-facing documentation surface change is expected unless divergence documentation is required by the implementation choice. |
| CQ-TESTS-001 | Yes | Keep or strengthen the focused parity test and run the existing bridge-compliance hook regression target. | Pytest command listed in the verification plan. | |
| CQ-LOGGING-001 | N/A | | | No runtime logging or telemetry changes are in scope. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest plus Ruff check and Ruff format check before filing the implementation report. | Commands listed in the verification plan. | |

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`: after LO `GO`, run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4672-bridge-compliance-gate-template-parity`; expected PASS with only the listed hook/template/test target paths authorized.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4672-bridge-compliance-gate-template-parity`; expected PASS with no missing required or advisory specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: inspect bridge header metadata; expected PASS with PAUTH, project, and WI-4672 present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py -q --tb=short`; expected PASS proving hook/template parity is restored or the intentional divergence is executable.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: run `groundtruth-kb/.venv/Scripts/gt.exe projects authorizations PROJECT-GTKB-MAY29-HYGIENE --json`; expected PASS with active PAUTH still valid for WI-4672.
- `GOV-STANDING-BACKLOG-001`: run `groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-4672 --history --json`; expected PASS with WI-4672 visible under May29 Hygiene and linked from report evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: inspect the implementation report and target diff; expected PASS showing active hook, template hook, tests, backlog row, and bridge chain all describe the same parity rule.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`: inspect tests and bridge report; expected PASS showing source, tests, backlog item, and bridge evidence remain aligned.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: inspect bridge chain plus WI-4672 history; expected PASS showing the lifecycle transition from captured defect to implemented/verified work is recorded.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: inspect target paths and run clause preflight; expected PASS with all target paths inside the GT-KB project root.

Additional checks:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4672-bridge-compliance-gate-template-parity
```

## Risk / Rollback

Risk is moderate only because the active hook and template are already dirty in the current worktree. The implementation must read those changes before editing and must not overwrite unrelated harness or user work. Behavior risk is low if the final state is byte-identical parity; intentional divergence carries higher future-maintenance risk and should be selected only when the source evidence requires it.

Rollback is a single commit revert of the source/test change plus withdrawal or NO-GO handling through the bridge if verification fails.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi4672-bridge-compliance-gate-template-parity`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
