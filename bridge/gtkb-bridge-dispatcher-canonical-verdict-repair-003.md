REVISED

# Canonical Verdict Repair for Stalled Bridge Dispatch - Revised Scope

bridge_kind: prime_proposal
Document: gtkb-bridge-dispatcher-canonical-verdict-repair
Version: 003 (REVISED)
Responds to: bridge/gtkb-bridge-dispatcher-canonical-verdict-repair-002.md

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-keep-working-2026-06-18T14-20Z
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: codex-desktop-automation

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4652

target_paths: ["scripts/audit_orphan_verdict_files.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "scripts/cross_harness_bridge_trigger.py", ".claude/hooks/bridge-compliance-gate.py", ".codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py", ".codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_audit_orphan_verdict_files.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py", "platform_tests/scripts/test_codex_bridge_compliance_gate.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py", "platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py"]

implementation_scope: bridge_dispatch_canonical_verdict_repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision keeps the urgent repair direction from `-001` and resolves the
NO-GO scope findings in `-002`.

The revised implementation scope now explicitly covers the Codex write-adapter
paths that can otherwise bypass the canonical Claude bridge-compliance hook for
noncanonical `bridge/*.lo-verdict.md` writes. It also broadens orphan
reconciliation from "verdict token on line 1" to all live
`bridge/*.lo-verdict.md` artifacts that are verdict-shaped by filename and
content, including heading-first artifacts. Finally, it treats the existing
VERIFIED orphan detector as baseline evidence and limits new work to the
reconciliation, write-path guard, and dispatch-health/liveness deltas.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered `bridge/<slug>-NNN.md` files are
  the authoritative workflow surface; noncanonical `.lo-verdict.md` files must
  not close, suppress, or satisfy canonical bridge threads.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher health and liveness must
  reflect whether bridge work produces canonical progress, not only whether a
  configured receiver exists.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - selected bridge work must reach a
  receiver that can produce the expected canonical bridge artifact or record a
  deterministic failure.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revised
  proposal links all bridge, dispatch, adapter, and verification requirements
  that constrain the implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes
  project authorization, project, work item, and target path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report
  must map each linked requirement to focused tests and executed command
  evidence.
- `GOV-STANDING-BACKLOG-001` - `WI-4652` is the durable backlog authority for
  this canonical orphan-verdict repair, with related liveness/harness WIs cited
  only as supporting context.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - orphan verdict files are lifecycle
  drift artifacts requiring explicit reconciliation or archival, not silent
  treatment as live authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation and repair
  artifacts remain inside the GT-KB project root.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the repair preserves durable
  numbered bridge artifacts rather than relying on transient worker outputs or
  noncanonical files.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the repair preserves lifecycle state
  and artifact evidence through explicit bridge and backlog records.
- `.claude/rules/file-bridge-protocol.md` - governs the append-only numbered
  bridge chain and Prime/LO state transitions.
- `.claude/rules/codex-review-gate.md` - requires bridge review and valid
  implementation-start authorization before protected source, hook, config,
  test, or KB mutations.
- `.claude/rules/project-root-boundary.md` - all target paths and generated
  repair evidence remain under `E:\GT-KB`.

## Prior Deliberations

- `bridge/gtkb-bridge-dispatcher-canonical-verdict-repair-001.md` - initial
  proposal establishing the repair direction and live failure evidence.
- `bridge/gtkb-bridge-dispatcher-canonical-verdict-repair-002.md` - NO-GO
  requiring Codex adapter target coverage, all-`.lo-verdict.md` reconciliation
  coverage, and a clear baseline-vs-delta boundary.
- `DELIB-20260618-WI4639-SCOPE-ALL-INTERACTIVE-VERDICT-PATHS` - owner decision
  that WI-4639 covers all interactive verdict-authoring paths; relevant because
  this proposal deliberately leaves interactive verdict seeding in WI-4639 and
  addresses only LLM/dispatcher noncanonical `.lo-verdict.md` emission and
  guard coverage.
- `bridge/gtkb-orphan-verdict-file-detector-004.md` - VERIFIED baseline
  detector for verdict-token-first orphan files. This revision builds on that
  baseline instead of claiming it as new work.
- `WI-4620` - related liveness defect: no-output or killed LO provider launches
  must become observable failures that unblock retry/fallback.
- `WI-4646` - related Ollama stdout Unicode crash, already implementation-filed
  and awaiting canonical LO verification.
- `WI-4648` - related LLM-as-LO harness noncanonical verdict path. This repair
  handles the path as part of canonical verdict write prevention and dispatch
  liveness; broader verdict-prior-deliberations seeding remains with WI-4648
  and WI-4639.
- `WI-4652` - controlling May29 Hygiene work item for reconciling the current
  orphan `.lo-verdict.md` files that block canonical bridge progress.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`
  (`DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`) authorizes proposing
  implementation for all unimplemented work items linked to
  `PROJECT-GTKB-MAY29-HYGIENE`.
- The active Hygiene PB automation directive asks Prime Builder to continue
  May29 Hygiene work autonomously through the bridge protocol.
- `bridge/gtkb-bridge-dispatcher-canonical-verdict-repair-002.md` states no
  additional owner action is required; Prime Builder can revise under existing
  May29 Hygiene authorization.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` already
defines numbered bridge files as the canonical handoff surface, the dispatch
service specifications already require observable progress and deterministic
failure recording, and the May29 project authorization covers implementation
proposals for unimplemented May29 Hygiene work items. The revision narrows and
corrects target authorization; it does not create a new bridge protocol or a new
formal requirement.

## Findings Addressed

### F1 - P1 - Codex adapter targets are missing, so the noncanonical verdict-write path remains open

Response: accepted. The revised `target_paths` now include:

- `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py`
- `.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py`
- `platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py`
- `platform_tests/scripts/test_codex_bridge_compliance_gate.py`

The verification plan now requires tests proving Codex apply_patch and Bash
adapter payloads for `bridge/*.lo-verdict.md` are routed into the canonical
bridge-compliance gate and denied as noncanonical verdict writes unless the
write is represented as the next numbered `bridge/<slug>-NNN.md` bridge file.

### F2 - P1 - Reconciliation coverage is too narrow for the live `.lo-verdict.md` corpus

Response: accepted. The revised scope states that all live
`bridge/*.lo-verdict.md` files are in reconciliation/archival analysis scope,
including heading-first verdict artifacts. The implementation must not depend
only on a first-nonblank-line status token. It must inspect filename shape plus
content signals such as `Verdict: GO`, `Verdict: NO-GO`,
`Verdict: VERIFIED`, or Loyal Opposition verdict headings, while avoiding false
positives for non-verdict markdown under `bridge/`.

### F3 - P2 - The proposal should separate already-VERIFIED detector scope from new repair scope

Response: accepted. This revision treats `scripts/audit_orphan_verdict_files.py`
and `platform_tests/scripts/test_audit_orphan_verdict_files.py` as existing
VERIFIED baseline from `gtkb-orphan-verdict-file-detector`. New implementation
scope is limited to:

- extending audit/reconciliation coverage to all `.lo-verdict.md` artifacts;
- adding guard coverage in Claude and Codex write paths;
- preventing LLM harnesses from treating noncanonical verdict files as
  authoritative;
- making dispatch health/liveness fail or degrade when canonical numbered
  verdict progress does not occur.

## Scope Changes From Version 001

Added implementation target paths:

- `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py`
- `.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py`
- `platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py`
- `platform_tests/scripts/test_codex_bridge_compliance_gate.py`

Clarified scope:

- all `bridge/*.lo-verdict.md` files are in reconciliation/archival analysis
  scope, not only status-token-first files;
- existing orphan detector behavior is baseline evidence, not new work to
  re-claim;
- repair output remains append-only and governed; existing `.lo-verdict.md`
  content may be used as evidence but is not formal verdict authority.

No database schema migration, production deployment, credential handling, or
alternate queue runtime is introduced.

## Spec-Derived Verification Plan

Expected focused verification:

```text
python -m pytest platform_tests/scripts/test_audit_orphan_verdict_files.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py platform_tests/scripts/test_codex_bridge_compliance_gate.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py -q --tb=short
python -m ruff check scripts/audit_orphan_verdict_files.py scripts/ollama_harness.py scripts/openrouter_harness.py scripts/cross_harness_bridge_trigger.py .claude/hooks/bridge-compliance-gate.py .codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py .codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_audit_orphan_verdict_files.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py platform_tests/scripts/test_codex_bridge_compliance_gate.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py
python -m ruff format --check scripts/audit_orphan_verdict_files.py scripts/ollama_harness.py scripts/openrouter_harness.py scripts/cross_harness_bridge_trigger.py .claude/hooks/bridge-compliance-gate.py .codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py .codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_audit_orphan_verdict_files.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py platform_tests/scripts/test_codex_bridge_compliance_gate.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py
python scripts/audit_orphan_verdict_files.py --json
python .claude/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json
gt bridge dispatch health --json
```

Spec-to-test mapping:

- `GOV-FILE-BRIDGE-AUTHORITY-001`: hook and adapter tests prove direct
  `bridge/*.lo-verdict.md` writes are intercepted and denied, and only numbered
  `bridge/<slug>-NNN.md` files affect canonical scan state.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`: dispatch tests prove a worker exit
  or killed worker with no canonical numbered verdict/status change is recorded
  as no progress and can trigger retry/fallback or degraded health.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`: harness tests prove LO workers are
  instructed and guarded to write the next canonical numbered verdict only, and
  do not treat existing `.lo-verdict.md` files as sufficient authority.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: orphan audit/reconciliation tests
  prove all live `.lo-verdict.md` variants, including heading-first verdicts,
  are classified for reconciliation/archival analysis without misclassifying
  ordinary bridge markdown.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the implementation report
  must include observed command outputs for all tests above and map them back
  to this plan.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: implementation evidence must preserve
  canonical numbered bridge state and explicit artifact lifecycle handling,
  rather than silently deleting or trusting noncanonical verdict files.

Additional required test cases:

- status-token-first `.lo-verdict.md` is detected;
- heading-first `.lo-verdict.md` containing `Verdict: GO`, `Verdict: NO-GO`,
  `Verdict: VERIFIED`, or a Loyal Opposition verdict heading is detected;
- non-verdict markdown under `bridge/` is not misclassified;
- post-reconciliation audit state leaves no live `.lo-verdict.md` artifact that
  can be mistaken for canonical bridge authority;
- Codex apply_patch adapter forwards `bridge/*.lo-verdict.md` candidate writes
  to the canonical bridge-compliance gate;
- Codex Bash adapter forwards `bridge/*.lo-verdict.md` candidate writes to the
  canonical bridge-compliance gate;
- the canonical gate denies noncanonical `.lo-verdict.md` verdict writes and
  accepts the proper numbered `bridge/<slug>-NNN.md` path when other bridge
  requirements are satisfied.

## Pre-Filing Preflight Subsection

Candidate preflights for this completed revision passed before live filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-dispatcher-canonical-verdict-repair --content-file .gtkb-state/bridge-revisions/drafts/gtkb-bridge-dispatcher-canonical-verdict-repair-003.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-dispatcher-canonical-verdict-repair --content-file .gtkb-state/bridge-revisions/drafts/gtkb-bridge-dispatcher-canonical-verdict-repair-003.md
```

Observed:

- Applicability preflight packet hash:
  `sha256:913d88eaea83aeac436d94532d6c76b480691e5392a26551b8a9aa3390e0c2a7`
- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- Clause preflight exited 0 with zero blocking gaps.

## Acceptance Criteria

1. The proposal receives LO `GO` with Codex adapter paths and tests in scope.
2. Implementation can block or route all direct `bridge/*.lo-verdict.md` write
   attempts through Claude Write/Edit and Codex Bash/apply_patch adapter paths.
3. Reconciliation/audit logic covers every live `bridge/*.lo-verdict.md`
   artifact, including heading-first verdict artifacts, without misclassifying
   ordinary bridge markdown.
4. Existing VERIFIED detector behavior remains baseline evidence; the new
   implementation delta is clear in code, tests, and the implementation report.
5. Dispatch health/liveness degrades or fails when a selected LO worker exits,
   is killed, or otherwise completes without producing canonical numbered
   verdict progress.
6. No formal bridge verdict authority is assigned to `.lo-verdict.md` files;
   they are evidence inputs only.

## Risk And Rollback

Risk is moderate because this touches write-path adapters, bridge guard logic,
LLM harness prompting/handling, dispatch liveness, and bridge health reporting.
The scope is still bounded to in-root bridge infrastructure and tests, with no
database schema migration, deployment, credentials, or alternate queue runtime.

Rollback is a normal revert of the implementation commit. Any reconciliation
output filed as numbered bridge state remains append-only bridge history and
must be superseded with a later numbered bridge file rather than deleted.

## Recommended Commit Type

`fix` - repairs a live bridge-dispatcher and bridge-write-authority failure mode
without adding a new user-facing workflow.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
