NEW

# Canonical Verdict Repair for Stalled Bridge Dispatch

bridge_kind: prime_proposal
Document: gtkb-bridge-dispatcher-canonical-verdict-repair
Version: 001
Author: Prime Builder / Codex
Date: 2026-06-18 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-automation-keep-working-2026-06-18T06-45Z
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop automation session; Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4652

target_paths: ["scripts/audit_orphan_verdict_files.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "scripts/cross_harness_bridge_trigger.py", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_audit_orphan_verdict_files.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py", "platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py"]

implementation_scope: bridge_dispatch_canonical_verdict_repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair the current bridge dispatcher stall caused by noncanonical LO verdict
files such as `bridge/gtkb-ollama-harness-utf8-output-003.lo-verdict.md`.
The live scanner only treats `bridge/<slug>-NNN.md` as canonical, while at
least one LO worker treats `.lo-verdict.md` files as already-authoritative and
therefore exits 0 without writing the required numbered verdict. This leaves
canonical threads latest `NEW`, keeps LO work pending, and can freeze Prime
Builder implementation reports that are waiting for `VERIFIED` or `NO-GO`.

This proposal authorizes a bounded repair: add a deterministic orphan-verdict
reconciliation mode, hard-block future noncanonical direct bridge verdict
writes, make LLM harnesses and dispatcher liveness fail closed when no numbered
verdict is produced, and make dispatch health report runtime/orphan failures
instead of topology-only `PASS`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the numbered bridge-file chain is the authoritative workflow surface; `.lo-verdict.md` files must not close or suppress canonical threads.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — dispatcher health and liveness must reflect whether bridge work is actually progressing, not only whether a configured receiver exists.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` — selected bridge work must reach a receiver that can produce the expected canonical bridge artifact or report a deterministic failure.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal links the bridge, dispatch, and verification requirements that govern the implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal includes project authorization, project, work item, and target path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the implementation report must map each change to focused tests and executed commands.
- `GOV-STANDING-BACKLOG-001` — `WI-4652` and related liveness/harness WIs preserve the observed defect before implementation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — orphan verdict files are lifecycle-drift artifacts requiring explicit reconciliation, not silent treatment as live authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all implementation and repair artifacts remain inside the GT-KB project root.

## Prior Deliberations

- `INTAKE-f8bc08a3` — dispatcher/bridge CLI is the primary mutating UI for GT-KB artifact operations; this repair keeps bridge state canonical rather than introducing an alternate queue.
- `INTAKE-e584f460` — all live agent mutations are bridge-first by default; this proposal preserves the bridge-first gate while fixing the worker path that emitted noncanonical verdict files.
- `INTAKE-b4928376` — bridge review eligibility is harness-agnostic; the repair should accept valid LO evidence from any authorized LO harness only after it is represented in the canonical numbered chain.
- `INTAKE-a815f782` — dispatch suppression must be scoped per bridge document; liveness handling should not keep suppressing a document whose last launch produced no canonical status change.
- `DELIB-WI4510-CUTOVER-PROPOSAL-RECONCILE-20260614` — precedent for reconciling duplicate/stale bridge state by selecting the canonical state surface and withdrawing or archiving obsolete representations.
- `WI-4620` — related defect: no-output or killed LO provider launches must become observable failures that unblock fallback/retry.
- `WI-4646` — related defect: Ollama stdout Unicode crash was already implemented but is still awaiting canonical LO verification.
- `WI-4648` — related defect: LLM-as-LO harness verdict authoring currently drives noncanonical `.lo-verdict.md` output.
- `WI-4652` — controlling work item for the three current orphan `.lo-verdict.md` files blocking canonical bridge scans.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`
  (`DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`) authorizes proposing
  implementation for all unimplemented work items linked to
  `PROJECT-GTKB-MAY29-HYGIENE`.
- The 2026-06-18 owner directive asks Prime Builder to execute the bridge
  dispatcher repair work now and continue until it is functioning correctly.
- No additional owner decision is required before LO review. Protected source,
  hook, and config mutations still require LO `GO` plus an implementation-start
  packet.

## Requirement Sufficiency

Existing requirements are sufficient. The file bridge authority requirement
already defines numbered `bridge/<slug>-NNN.md` files as the canonical handoff
surface; dispatch-service requirements already require observable worker
progress; and May29 Hygiene authorization covers implementation proposals for
unimplemented work items in this project. This is a repair to existing bridge
and dispatcher behavior, not a new bridge protocol.

The implementation must not treat existing `.lo-verdict.md` files as formal
verdict authority. They may be used only as evidence for a deterministic
reconciliation path that writes or archives artifacts through governed code
after LO approves this proposal.

## In-Root Placement Evidence

All implementation targets and generated artifacts are under `E:\GT-KB`.
The filed bridge proposal will be `E:\GT-KB\bridge\gtkb-bridge-dispatcher-canonical-verdict-repair-001.md`.
Any canonical reconciliation output will be a numbered file under
`E:\GT-KB\bridge\`; any archived orphan evidence must remain under an in-root
state or report directory, not outside the GT-KB project root.

## Spec-Derived Verification Plan

Expected focused verification:

```text
python -m pytest platform_tests/scripts/test_audit_orphan_verdict_files.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py -q --tb=short
python -m ruff check scripts/audit_orphan_verdict_files.py scripts/ollama_harness.py scripts/openrouter_harness.py scripts/cross_harness_bridge_trigger.py .claude/hooks/bridge-compliance-gate.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_audit_orphan_verdict_files.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py
python -m ruff format --check scripts/audit_orphan_verdict_files.py scripts/ollama_harness.py scripts/openrouter_harness.py scripts/cross_harness_bridge_trigger.py .claude/hooks/bridge-compliance-gate.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_audit_orphan_verdict_files.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py
python scripts/audit_orphan_verdict_files.py --json
python .claude/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json
gt bridge dispatch health --json
```

Spec-to-test mapping:

- `GOV-FILE-BRIDGE-AUTHORITY-001`: tests prove direct `bridge/*.lo-verdict.md`
  writes are rejected and only numbered `bridge/<slug>-NNN.md` files affect
  canonical scan state.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`: dispatch tests prove a worker exit
  with no canonical verdict/status change is recorded as no progress and
  eligible for retry/fallback instead of healthy/unchanged.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`: harness tests prove LO workers are
  instructed and guarded to write the next canonical numbered verdict only.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: orphan audit tests prove validated
  orphan evidence can be reconciled or archived deterministically and that the
  audit exits clean after repair.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the implementation report
  must include the executed command outputs above and map them to this plan.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Do not add credentials or credential-shaped samples; preserve existing credential-scan gates. | Ruff plus bridge helper credential scan before filing; implementation report must note no secrets added. | |
| CQ-PATHS-001 | Yes | Keep all writes inside the project root; canonical verdict repair output stays under `bridge/` or in-root runtime/archive state. | In-root placement evidence plus focused path tests. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing status-token, version-file, and dispatch-state constants where available. | Ruff and focused tests for status/path handling. | |
| CQ-DOCS-001 | Yes | Update prompts/help text only where needed to explain canonical numbered verdict behavior. | Focused harness prompt tests. | |
| CQ-COMPLEXITY-001 | Yes | Keep reconciliation and liveness checks small and deterministic; avoid introducing an alternate queue runtime. | Ruff and focused unit tests for each helper path. | |
| CQ-TESTS-001 | Yes | Add or extend tests for orphan repair, noncanonical write denial, dispatch no-progress handling, health degradation, and harness Unicode/canonical-write behavior. | Pytest command listed above. | |
| CQ-LOGGING-001 | Yes | Report no-progress/orphan findings as structured dispatch health/liveness findings, not silent PASS. | Dispatch trigger and CLI health tests. | |
| CQ-SECURITY-001 | Yes | Preserve bridge guard denial for unauthorized bridge writes and avoid shell mutation of bridge files. | Hook tests and helper-mediated writes only. | |
| CQ-VERIFICATION-001 | Yes | Implementation report must include command outputs mapped to the spec-derived verification plan. | LO verification of report evidence. | |

## Risk / Rollback

Risk is moderate because the change touches the bridge worker/dispatcher path
and the bridge write guard. The scope is still bounded: no production
deployment, credential handling, database schema migration, or alternate queue
runtime is introduced. Rollback is a single revert of the implementation commit;
any orphan-verdict reconciliation output is append-only canonical bridge state
and must be superseded by a follow-up numbered bridge file rather than deleted.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-bridge-dispatcher-canonical-verdict-repair`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs a live bridge-dispatcher failure mode without adding a new
user-facing workflow.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
