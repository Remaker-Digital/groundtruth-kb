NEW

# gtkb-wi4893-false-verified-finalization-recovery - Recover bad VERIFIED finalization and harden the gate

bridge_kind: prime_proposal
Document: gtkb-wi4893-false-verified-finalization-recovery
Version: 001
Author: Prime Builder (Codex harness A)
Date: 2026-06-28 UTC

author_identity: codex-prime-builder
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop; restarted Prime Builder release-readiness session

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4893-FALSE-VERIFIED-RECOVERY
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4893

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", ".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py", "scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py", ".claude/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_finalization_evidence.py"]

implementation_scope: source, tests, and governance gate hardening
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal recovers a release-blocking false-VERIFIED state found while checking the WI-4893 bridge. The terminal bridge file `bridge/gtkb-wi4893-daemon-hook-storm-hardening-004.md` says VERIFIED, but primary `develop` does not contain the full implementation claimed by `bridge/gtkb-wi4893-daemon-hook-storm-hardening-003.md`. The report listed eight implementation/test/config paths; commit `6052795edc53af775d982c8407d968de224b6ef6` omitted key claimed paths, including `scripts/cross_harness_bridge_trigger.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, and `platform_tests/scripts/test_cross_harness_bridge_trigger.py`, and the current primary code lacks the report-claimed trigger in-flight lock and daemon PID create-time provenance behavior.

The correction has two parts. First, port or re-implement the missing WI-4893 daemon/trigger recovery behavior into primary `develop`, preserving unrelated dirty worktree changes. Second, harden the VERIFIED finalization path so this class of failure cannot recur: a VERIFIED verdict must carry commit-finalization evidence, the finalization helper must compare its include set against the latest implementation report's claimed path set, and the protected commit gate must reject staged VERIFIED bridge files that lack finalization evidence.

## Incident Evidence

- `gtkb-wi4893-daemon-hook-storm-hardening` is terminal `VERIFIED` at `bridge/gtkb-wi4893-daemon-hook-storm-hardening-004.md`.
- `bridge/gtkb-wi4893-daemon-hook-storm-hardening-003.md` section `## Files Changed` claims `.claude/settings.json`, `.codex/hooks.json`, `.codex/gtkb-hooks/bridge-dispatch-trigger.cmd`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `scripts/gtkb_dispatcher_daemon.py`, `scripts/cross_harness_bridge_trigger.py`, `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, and `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.
- `git show --name-only 6052795edc53af775d982c8407d968de224b6ef6` shows the VERIFIED commit omitted `groundtruth-kb/src/groundtruth_kb/cli.py`, `scripts/cross_harness_bridge_trigger.py`, and `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.
- Primary `scripts/cross_harness_bridge_trigger.py` has no `TRIGGER_INFLIGHT_LOCK_FILENAME`, `trigger_inflight_active`, or `_try_acquire_trigger_inflight_lock` marker, while the formal release worktree contains those report-claimed markers as uncommitted implementation.
- Primary `scripts/gtkb_dispatcher_daemon.py` has no `PID_CREATE_TIME_FILENAME`, `pid_provenance_verified`, or create-time sidecar validation marker, while the formal release worktree contains the report-claimed implementation.
- The terminal verdict `bridge/gtkb-wi4893-daemon-hook-storm-hardening-004.md` has no `## Commit Finalization Evidence` section, so it was not produced by the current finalization helper path that appends same-transaction evidence.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected dispatcher source, tests, hooks, and verification helpers require a live proposal, GO verdict, implementation authorization, report, and independent verification before release.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal explicitly links the correction to the governing dispatcher and bridge-governance requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries PAUTH, project, work item, and parseable `target_paths` metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map each correction to focused tests and exact command output.
- `GOV-STANDING-BACKLOG-001` - WI-4893 is the active release-readiness work-item authority for this dispatcher showstopper.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher lifecycle control must not terminate or report processes based on stale or ambiguous PID evidence.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher daemon and trigger behavior must be reliable enough to support autonomous bridge work without hook storms.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher status/stop surfaces must accurately represent daemon provenance and cleanup state.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatch sidecars and cleanup paths must preserve lifecycle evidence and avoid false live/process claims.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook behavior and fallback wrapper behavior must be governed and testable on Windows.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - helper and hook parity changes must be kept aligned across active harness adapters.
- `ADR-CROSS-HARNESS-PARITY-001` - Claude, Codex, and Cursor verification-helper copies must not drift in finalization semantics.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - a false terminal artifact state is a formal governance defect, not scratch context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the recovery must be artifact-driven: proposal, GO, implementation report, verifier evidence, and scoped commit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - a release-blocking false VERIFIED state triggers a governed corrective artifact.

## Cross-Harness Disposition

- Claude/Codex/Cursor verification helper parity: required. The same finalization include-set guard must be implemented in `.claude/skills/verify/helpers/write_verdict.py`, `.codex/skills/verify/helpers/write_verdict.py`, and `.cursor/skills/verify/helpers/write_verdict.py`. `platform_tests/skills/test_verified_finalization_validation_hardening.py` must assert the three copies share the new behavior.
- Claude bridge Write hook: required. `.claude/hooks/bridge-compliance-gate.py` is the canonical write-time bridge gate for direct file writes; it must deny terminal VERIFIED implementation-verification bodies that lack finalization evidence.
- Codex bridge proposal path: parity via audit. Codex proposal writes already run `.claude/hooks/bridge-compliance-gate.py --audit-only`; no separate `.codex` bridge-compliance hook file is changed in this proposal.
- Cursor helper path: parity via helper copy. Cursor has `.cursor/skills/verify/helpers/write_verdict.py`; it must match the Claude/Codex helper semantics. No `.cursor` bridge-compliance hook file is in scope because no parallel hook surface exists in this checkout.
- Hook registrations/settings: out of scope. This proposal does not modify `.claude/settings.json`, `.codex/hooks.json`, or `.codex/gtkb-hooks/bridge-dispatch-trigger.cmd`; those were already part of the bad terminal commit and are not the missing-code recovery payload.
- Owner-approved typed waiver: none. All applicable harness helper copies are updated rather than waived.

## Prior Deliberations

- `DELIB-20260628-WI4893-FALSE-VERIFIED-RECOVERY` - owner directive that the false VERIFIED mismatch is a release showstopper and must be corrected/diagnosed before release.
- `DELIB-20266364` - harvested WI-4893 dispatcher-release-readiness VERIFIED record containing the stale `DELIB-20260628-DISPATCHER-RELEASE-READINESS` prose citation and same-transaction evidence for a different WI-4893 path set.
- `DELIB-20266365` - harvested WI-4893 dispatcher-release-readiness GO record.
- `bridge/gtkb-wi4893-daemon-hook-storm-hardening-001.md` - original daemon/hook storm hardening proposal.
- `bridge/gtkb-wi4893-daemon-hook-storm-hardening-002.md` - Loyal Opposition GO for the original hardening scope.
- `bridge/gtkb-wi4893-daemon-hook-storm-hardening-003.md` - implementation report whose claimed path set diverged from the terminal commit.
- `bridge/gtkb-wi4893-daemon-hook-storm-hardening-004.md` - false terminal VERIFIED verdict and evidence for this recovery.
- `bridge/gtkb-wi4834-storm-watchdog-pid-provenance-orphan-reap-004.md` - VERIFIED create-time provenance pattern that the daemon recovery should follow.
- `bridge/gtkb-lo-verified-commit-atomicity-020.md` - prior verified finalization atomicity lineage.
- `bridge/gtkb-wi4723-verified-finalize-index-lock-retry-021.md` - prior finalization-helper robustness lineage.

## Owner Decisions / Input

No additional owner decision is required before implementation. The owner directive is now captured at `DELIB-20260628-WI4893-FALSE-VERIFIED-RECOVERY`, and the bounded project authorization is `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4893-FALSE-VERIFIED-RECOVERY`. This proposal does not authorize production deployment, credential lifecycle action, history rewrite, retired-poller restoration, dispatcher routing-policy changes, broad unrelated cleanup, or merge to `main` before release gates pass.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4893, `DELIB-20260628-WI4893-FALSE-VERIFIED-RECOVERY`, the PAUTH, the bridge authority rules, the verified finalization owner directive lineage, and the dispatcher lifecycle specifications require a bounded source/test/governance recovery. New requirements would be needed only to alter dispatcher topology, release policy, or bridge role authority; those are out of scope.

## Implementation Plan

1. Reconcile primary `develop` against the formal release worktree for only the missing WI-4893 daemon/trigger behavior: daemon PID create-time sidecars/provenance, force stop lock cleanup, and cross-harness trigger in-flight lock behavior.
2. Preserve unrelated dirty primary worktree changes, including the pre-existing dirty hunk in `scripts/cross_harness_bridge_trigger.py` that moves pending mode-switch application.
3. Add focused daemon and trigger regressions proving the missing behavior exists in primary.
4. Harden `.claude`, `.codex`, and `.cursor` `write_verdict.py` helper copies so `--finalize-verified` fails closed when the latest implementation report's claimed implementation/test/config path set is missing from the helper include set, except for explicit by-reference finalization waiver cases already documented in the report and owner-approved deliberations.
5. Harden `.claude/hooks/bridge-compliance-gate.py` so direct writes of terminal VERIFIED implementation-verification files without `## Commit Finalization Evidence` and a same-transaction path set are denied.
6. Harden `scripts/check_protected_commit_authorization.py` so pre-commit evaluation rejects staged terminal VERIFIED bridge files lacking commit-finalization evidence, even when the staged source paths otherwise have terminal VERIFIED proposal evidence.

## Spec-Derived Verification Plan

| Specification | Required verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4893-false-verified-finalization-recovery`; `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4893-false-verified-finalization-recovery`; `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4893-false-verified-finalization-recovery` followed by validation for the target paths. |
| `ADR-DISPATCHER-ARCHITECTURE-001` / `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` / `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short` must prove daemon create-time provenance, forced stop cleanup, and PID-reuse safety. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` / `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short` must prove trigger in-flight locking and stale-lock recovery. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` / `ADR-CROSS-HARNESS-PARITY-001` | `python -m pytest platform_tests/skills/test_verified_finalization_validation_hardening.py -q --tb=short` must prove Claude/Codex/Cursor helper parity and the report-claim include-set guard. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / verified finalization directive lineage | `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_finalization_evidence.py platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` must prove direct VERIFIED writes and staged VERIFIED commits without finalization evidence fail closed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The implementation report must include exact commands, observed results, and a path-set reconciliation showing the terminal commit includes the implementation/test/config paths claimed by the report. |

## Risk / Rollback

Primary risk is over-tightening VERIFIED finalization for legitimate by-reference recovery cases. The implementation should preserve explicit, owner-approved by-reference waiver behavior while making the default path fail closed. Rollback is a single revert of the corrective implementation commit; bridge audit files remain append-only.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi4893-false-verified-finalization-recovery`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: recovers a release-blocking false terminal bridge state and hardens the finalization gates that allowed it.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
