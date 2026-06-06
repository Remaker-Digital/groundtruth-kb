REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-owner-pb-gtkb-dispatcher-config-validation
author_model: GPT-5 Codex
author_model_version: 2026-06-06
author_model_configuration: reasoning=high

bridge_kind: implementation_proposal
Document: gtkb-dispatcher-config-cli-whole-candidate-validation
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH-MODE-CONFIG-TRANSACTIONS
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001
target_paths: ["groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/harness_roles.py", ".claude/rules/operating-role.md", "platform_tests/groundtruth_kb/test_mode_switch_invariants.py", "platform_tests/groundtruth_kb/test_mode_switch_transaction.py", "platform_tests/groundtruth_kb/test_mode_switch_pending.py", "platform_tests/groundtruth_kb/cli/test_harness_cli.py", "platform_tests/scripts/test_harness_roles.py", "platform_tests/scripts/test_session_self_initialization_topology_derive.py", "platform_tests/scripts/test_single_harness_governance_artifacts.py"]

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Do not touch credentials or environment values. | Helper credential scan and diff review. | n/a |
| CQ-PATHS-001 | Yes | Mutate only target_paths. | `git diff --name-only -- <target paths>`. | n/a |
| CQ-COMPLEXITY-001 | Yes | Replace auto-selection with small in-memory candidate validation helper; avoid dispatcher redesign. | Focused source review and tests. | n/a |
| CQ-CONSTANTS-001 | Yes | Reuse existing role/status tokens and `RolePartitionViolation` semantics. | Source review. | n/a |
| CQ-SECURITY-001 | Yes | Fail closed when candidate configuration is invalid; do not weaken dispatch eligibility gates. | Rejection tests. | n/a |
| CQ-DOCS-001 | Yes | Correct stale operating-role language that claims active-target gating and complementary reassignment. | Rule-file tests. | n/a |
| CQ-TESTS-001 | Yes | Add/update transaction, CLI, helper, and rule regression tests. | Targeted pytest commands. | n/a |
| CQ-LOGGING-001 | Yes | Preserve transaction audit behavior for accepted updates; rejected candidates write no audit/persisted state. | Audit and rejection tests. | n/a |
| CQ-VERIFICATION-001 | Yes | Run targeted pytest plus ruff check/format-check. | Commands listed in implementation report. | n/a |

# REVISED Implementation Proposal: Dispatcher Config CLI Whole-Candidate Validation

## Revision Claim

Prime Builder adopts the mechanically well-formed technical proposal from `bridge/gtkb-dispatcher-config-cli-whole-candidate-validation-001.md` and corrects the procedural authorship defect identified in `bridge/gtkb-dispatcher-config-cli-whole-candidate-validation-002.md`. The implementation direction, target paths, specification links, acceptance criteria, and verification plan remain substantively unchanged.

## Findings Addressed

### F1 (P1): Prime Builder adoption required before GO

Response: addressed. This revision is authored as `prime-builder/codex/A` under Mike's explicit 2026-06-06 owner directive: "You need to take ownership of this thread and drive it through to VERIFIED", followed by "You are Prime Builder." That session-level direction supersedes the prior B-only adoption path for this thread without mutating the durable harness registry.

## Summary

Correct the role/configuration CLI semantics after the owner's 2026-06-06 dispatcher clarification. The bridge is a dispatcher: dispatch target selection is based on harness dispatch availability plus the role and subject in the session envelope and first topic envelope. The default role recorded on a harness is informative fallback metadata, not a self-service selector that should cause the CLI to choose complementary role holders, pick topics, or rewrite unrelated harnesses.

The current implementation violates that model. `groundtruth_kb.mode_switch.transaction._apply_active_role_assignment` sets the requested harness role, then selects a complementary holder with `_existing_holder` or `_first_active`, rewrites every active harness role, and can suspend active harnesses it did not choose. `scripts/harness_roles.py:set_harness_role` contains a parallel auto-selection path. `gt harness set-role` additionally blocks non-active targets even though a non-active harness default role can be useful informative metadata and does not make the harness dispatchable.

Replace the auto-selection behavior with a single candidate-configuration validation step: apply only the requested role metadata update in memory, validate the whole resulting dispatcher-relevant configuration, and reject the update before audit or persistence when the candidate leaves the dispatcher invalid.

## Prior Deliberations

- `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json` records owner approval of the deterministic bridge and operating-mode transaction requirement. Acceptance criterion 2 requires validation against authoritative role, bridge, and session-state artifacts before durable writes.
- `bridge/gtkb-operating-mode-transaction-001-006.md` implemented the deterministic mode-switch transaction surface and cited the same validation-before-write contract.
- `bridge/gtkb-active-status-capability-gate-registry-dispatch-001.md` and `bridge/gtkb-active-status-capability-gate-lifecycle-substrate-001.md` formalized role/status/capability orthogonality and active dispatch eligibility.
- `bridge/gtkb-active-status-capability-gate-harness-lifecycle-retention-001.md` intentionally preserved non-active role metadata while keeping dispatch eligibility gated on active status and event capability.
- Owner directive in this session, 2026-06-06: the bridge configuration CLI should perform one internal validity check over the whole configuration, should not select harnesses for roles or topics, and must reject updates that leave the bridge dispatcher with an invalid configuration.
- Owner directive in this session, 2026-06-06: Codex is Prime Builder for this thread and should take ownership through verification.

## Owner Decisions / Input

- 2026-05-13 owner AUQ approved `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`; approval packet is `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json`.
- 2026-06-06 owner directive in the current Codex request clarifies the dispatcher model: harness default role is informative fallback metadata, dispatch target selection comes from availability plus session/topic envelope role and subject, and configuration updates must be rejected if the whole candidate dispatcher configuration is invalid.
- 2026-06-06 owner directive in this chat assigns the current Codex session to Prime Builder ownership for this bridge thread: "You need to take ownership of this thread and drive it through to VERIFIED" and "You are Prime Builder."

No production deployment, credential action, MemBase mutation, or formal GOV/SPEC/ADR/DCL/PB mutation is proposed. This is a scoped source/test/rule correction under existing project authorization and direct owner thread ownership.

## Specification Links

- SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001
- REQ-HARNESS-REGISTRY-001
- ADR-SINGLE-HARNESS-OPERATING-MODE-001
- ADR-ROLE-STATUS-ORTHOGONALITY-001
- DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001
- GOV-HARNESS-ROLE-PORTABILITY-001
- GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-ENVELOPE-001
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-SESSION-ROLE-AUTHORITY-001
- DCL-SESSION-ROLE-RESOLUTION-001

## Requirement Sufficiency

Existing requirements are sufficient.

The owner directive clarifies the intended interpretation of the already-approved deterministic transaction requirement: validation is over the candidate authoritative configuration, not an invitation for the CLI to synthesize or select unrelated roles. `REQ-HARNESS-REGISTRY-001`, `ADR-SINGLE-HARNESS-OPERATING-MODE-001`, `ADR-ROLE-STATUS-ORTHOGONALITY-001`, and `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` already define role/status/capability orthogonality and active dispatch eligibility. No new formal spec or MemBase mutation is required for this scoped implementation; the proposal updates code/tests and the operating-role instruction surface to match the clarified dispatcher semantics.

## Scope

In scope:

- Add an in-memory whole-candidate role partition validator, likely `verify_role_document_partition(role_document)`, and have `verify_active_role_partition(project_root)` delegate to it after loading the projection.
- Change `groundtruth_kb.mode_switch.transaction.apply_role_switch` so the role update mutates only the named harness role metadata in the candidate map. It must not select a complementary role holder, suspend other harnesses, infer a topology, or rewrite unrelated active harness roles to make the update pass.
- Run the whole-candidate validator before audit writing, DB writes, projection regeneration, or session-state writes. Convert `RolePartitionViolation` into `TransactionValidationError(axis="role")` so rejected candidates leave state unchanged.
- Change `gt harness set-role` so it no longer pre-rejects registered or suspended harnesses solely because they are non-active. Non-active default role metadata may be updated when the resulting active dispatcher partition remains valid. Unknown or retired harness handling remains fail-closed.
- Align `scripts/harness_roles.py:set_harness_role` with the same no-auto-selection semantics or route it through the canonical transaction path so legacy helper use cannot reintroduce the old behavior.
- Update `.claude/rules/operating-role.md` to describe default role as informative fallback metadata and to remove the active-target/complementary-reassignment language. The rule should state that dispatch target selection is performed by the dispatcher using availability plus the session/topic envelope, not by the configuration CLI.
- Update tests that currently expect auto-demotion or active-only `set-role` rejection to expect whole-candidate rejection or non-active metadata update.

Out of scope:

- Implementing a new batch role/topology transaction. This proposal may identify it as future work if users need atomic multi-harness swaps without invalid intermediate states.
- Implementing a default-topic dimension. The owner noted default topic is possible; this slice only prevents current role/config CLI surfaces from selecting topics or role holders.
- Changing dispatcher recipient resolution beyond preserving existing active/status/capability gates.
- Changing harness lifecycle activate/suspend/resume/retire reconciliation behavior except where needed to keep `set-role` tests coherent. If lifecycle reconciliation also auto-selects roles, capture it as a follow-up unless the implementation proves it is inseparable.
- MemBase mutation, formal spec mutation, production deployment, or credential changes.

## Scope Changes

No technical scope changes from `bridge/gtkb-dispatcher-config-cli-whole-candidate-validation-001.md`. This revision changes proposal authorship/procedure only and adds the owner directive assigning this Codex session as Prime Builder for the thread.

## Acceptance Criteria

- A role/config CLI update changes only the explicitly requested harness role metadata in its candidate state; unrelated harness role/status fields are unchanged by the transaction.
- A candidate that leaves the active dispatcher configuration invalid is rejected before audit, DB/projection, or session-state writes.
- A valid non-active harness default-role metadata update can succeed without making that harness dispatchable.
- The legacy `scripts/harness_roles.py` set-role helper no longer selects complementary role holders or rewrites unrelated harnesses.
- `.claude/rules/operating-role.md` no longer tells agents that `set-role` selects complementary assignments or gates the target on active status.
- Existing validation against role, bridge, and session-state artifacts remains in place.
- Targeted pytest, ruff check, and ruff format-check pass.

## Pre-Filing Preflight Subsection

Planned pre-filing gates for this completed revision:

- `python scripts/check_code_quality_baseline_parity.py .gtkb-state/bridge-revisions/drafts/gtkb-dispatcher-config-cli-whole-candidate-validation-003.md`
- `python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-dispatcher-config-cli-whole-candidate-validation-003.md --json`
- `python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-dispatcher-config-cli-whole-candidate-validation-003.md`

The bridge revision helper will re-run the filing gates before writing the live `REVISED` file and updating `bridge/INDEX.md`.

## Specification-Derived Verification Plan

- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`: transaction tests prove validation happens before durable writes and rejected candidates leave no audit or registry mutation.
- `REQ-HARNESS-REGISTRY-001`: CLI tests prove `gt harness set-role` mutates registry role metadata through the canonical transaction path and preserves projection consistency.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001`: tests prove topology is derived from the resulting map rather than selected by the CLI.
- `ADR-ROLE-STATUS-ORTHOGONALITY-001` and `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001`: invariant tests prove non-active role metadata is allowed while active dispatcher partition uniqueness remains enforced.
- `GOV-HARNESS-ROLE-PORTABILITY-001`: tests keep canonical role tokens limited to `prime-builder` and `loyal-opposition`, independent of vendor harness type.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: proposal, GO, implementation report, and verification stay in the bridge thread and `bridge/INDEX.md`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: implementation report must carry this spec-to-test mapping with observed command results.

Targeted command plan:

- `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_invariants.py platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/groundtruth_kb/test_mode_switch_pending.py -q --tb=short`
- `python -m pytest platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_harness_roles.py platform_tests/scripts/test_session_self_initialization_topology_derive.py platform_tests/scripts/test_single_harness_governance_artifacts.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/mode_switch groundtruth-kb/src/groundtruth_kb/cli.py scripts/harness_roles.py platform_tests/groundtruth_kb/test_mode_switch_invariants.py platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/groundtruth_kb/test_mode_switch_pending.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_harness_roles.py platform_tests/scripts/test_session_self_initialization_topology_derive.py platform_tests/scripts/test_single_harness_governance_artifacts.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/mode_switch groundtruth-kb/src/groundtruth_kb/cli.py scripts/harness_roles.py platform_tests/groundtruth_kb/test_mode_switch_invariants.py platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/groundtruth_kb/test_mode_switch_pending.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_harness_roles.py platform_tests/scripts/test_session_self_initialization_topology_derive.py platform_tests/scripts/test_single_harness_governance_artifacts.py`

## Risk And Rollback

Risk: removing auto-selection means one-command PB/LO swaps may be rejected because the intermediate candidate has duplicate or missing active roles. That is intended fail-closed behavior under the clarified dispatcher model. Mitigation: document the behavior and capture a separate batch-configuration transaction if operators need atomic multi-harness swaps. Rollback restores the prior auto-selection helpers and tests; bridge artifacts remain append-only.
