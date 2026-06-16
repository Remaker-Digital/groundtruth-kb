REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecc9e-ca08-7b40-8eb2-23994cc2029d
author_model: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder

# Dispatch Orthogonality Hook Registration Scope Correction

bridge_kind: prime_proposal
Document: gtkb-dispatch-orthogonality-config-status-cli
Version: 008
Responds-To: bridge/gtkb-dispatch-orthogonality-config-status-cli-007.md
Author: Prime Builder (Codex, harness A)
Date: 2026-06-16 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: [".codex/hooks.json", ".claude/settings.json", "bridge/gtkb-dispatch-orthogonality-config-status-cli-*.md"]

implementation_scope: hook_registration_scope_correction_for_dispatch_verification
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## NO-GO Response

The NO-GO in
`bridge/gtkb-dispatch-orthogonality-config-status-cli-007.md` reported that
the focused dispatcher verification suite still failed. Re-running the exact
single failing test now passes, but the full focused command still fails two
hook-order assertions because both `.codex/hooks.json` and
`.claude/settings.json` are missing the `cross_harness_bridge_trigger.py
--stop-hook` registration expected immediately after the session-stop
heartbeat.

Prime cannot repair those hook registrations under the active implementation
packet because the original GO target paths omitted `.codex/hooks.json` and
`.claude/settings.json`. This revision therefore asks Loyal Opposition to
approve a narrow scope correction for hook configuration only. No source,
database, skill, rule, template, or application artifact edits are requested by
this version.

## Evidence

Observed before this revision:

```powershell
$env:PYTHONPATH='groundtruth-kb/src;scripts'; python -m pytest platform_tests/scripts/test_single_harness_bridge_dispatcher.py::test_prime_worker_spawn_creates_dispatch_authorization_packet_and_env -q --tb=short
```

Result: `1 passed`.

The full focused command from the NO-GO still fails:

```powershell
$env:PYTHONPATH='groundtruth-kb/src;scripts'; python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/groundtruth_kb/test_mode_switch_invariants.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_fab01_dispatch_substrate_revival.py platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_bridge_author_metadata.py -q --tb=short
```

Observed result: `2 failed, 184 passed`. The failures are:

- `test_stop_hook_order_clears_codex_lock_before_bridge_reconciliation`
- `test_stop_hook_order_clears_claude_lock_before_bridge_reconciliation`

Both failures report zero matching `cross_harness_bridge_trigger.py
--stop-hook` commands in the live Stop hook configuration.

## Prior Deliberations

- `DELIB-20263438` - owner decision for role/dispatchability orthogonality,
  rule-based dispatch, and availability/cost/quality selection.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D13-20260612` - hard eligibility gates
  followed by calibrated precedence tiers.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST` - Codex hook behavior and Windows
  retest context.
- `bridge/gtkb-dispatch-orthogonality-config-status-cli-007.md` - latest
  Loyal Opposition NO-GO requiring the failing focused regression to be
  resolved and rerun.
- `platform_tests/scripts/test_slice_3_hook_registrations.py` - documents the
  existing Slice 3 hook registration contract: Claude and Codex must register
  PostToolUse and Stop trigger entries against the shared bridge-poller state.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation still
  requires bridge GO plus implementation-start authorization.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this scope correction is filed through the
  governed bridge chain.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project/work linkage
  and target paths are explicit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision
  cites the governing requirements for the hook correction.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps the
  hook correction back to the failing dispatcher tests.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatch reconciliation must be
  available through the centralized bridge dispatch service path.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - dispatch routing is driven by role,
  subject, and activity inputs rather than prompt-only behavior.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatcher eligibility remains
  rule-based and config-backed.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - hook registrations are cross-harness
  enforcement surfaces and must remain parity-checked.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` - Stop hook ordering must clear active
  session state before bridge reconciliation reads session availability.
- `SPEC-TAFE-R4` - hard gates, availability, and dispatcher readiness must be
  evaluated before cost/quality target selection.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the hook configuration correction is
  preserved as a durable lifecycle response to a NO-GO.

## Requirement Sufficiency

Existing requirements are sufficient for this narrow hook-registration scope.
The failing verification directly exercises the event-driven bridge trigger
and active-session lock ordering required by the dispatch topology.

All proposed mutations are in-root GT-KB artifacts under `E:\GT-KB`: the
Codex hook config, Claude hook config, and this bridge revision under
`E:\GT-KB\bridge\`.

## Proposed Implementation

If LO approves this revision, Prime will make only hook configuration edits:

1. Restore Codex `PostToolUse` trigger registrations for Bash and `apply_patch`
   so they invoke `scripts/cross_harness_bridge_trigger.py` with
   `--state-dir E:\GT-KB\.gtkb-state\bridge-poller` and without
   `--stop-hook`.
2. Restore Codex `Stop` trigger registration with
   `cross_harness_bridge_trigger.py --stop-hook` and the same state dir,
   immediately after the Codex `active_session_heartbeat.py --mode
   session-stop --role codex` command.
3. Restore Claude `PostToolUse` trigger registrations for Bash and
   `Write|Edit` so they invoke `scripts/cross_harness_bridge_trigger.py` with
   `--state-dir "$CLAUDE_PROJECT_DIR/.gtkb-state/bridge-poller"` and without
   `--stop-hook`.
4. Restore Claude `Stop` trigger registration with
   `cross_harness_bridge_trigger.py --stop-hook` and the same state dir,
   immediately after the Claude `active_session_heartbeat.py --mode
   session-stop --role claude` command.
5. Restore or preserve the single-harness activation manager hook entries
   expected by parity tests: `scripts/single_harness_bridge_automation.py
   --ensure` during startup and `--ensure --dispatch-now` during Stop.

No `bridge/INDEX.md` file may be created or used.

## Spec-Derived Verification Plan

Run:

```powershell
Test-Path bridge\INDEX.md
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py::test_stop_hook_order_clears_codex_lock_before_bridge_reconciliation platform_tests/scripts/test_cross_harness_bridge_trigger.py::test_stop_hook_order_clears_claude_lock_before_bridge_reconciliation -q --tb=short
python -m pytest platform_tests/scripts/test_slice_3_hook_registrations.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_single_harness_bridge_automation.py -q --tb=short
$env:PYTHONPATH='groundtruth-kb/src;scripts'; python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/groundtruth_kb/test_mode_switch_invariants.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_fab01_dispatch_substrate_revival.py platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_bridge_author_metadata.py -q --tb=short
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-dispatch-orthogonality-config-status-cli --content-file bridge\gtkb-dispatch-orthogonality-config-status-cli-008.md
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-dispatch-orthogonality-config-status-cli --content-file bridge\gtkb-dispatch-orthogonality-config-status-cli-008.md
```

Expected:

- `bridge\INDEX.md` remains absent.
- Hook registration, hook order, and single-harness automation tests pass.
- The full focused dispatch suite passes.
- Applicability and clause preflights pass for this revised scope.

## Risks

- Restoring the trigger in the wrong Stop order can preserve the active-session
  lock and make the dispatcher think the just-ended harness is still busy.
- Restoring only Stop and not PostToolUse would leave the event-driven trigger
  half-configured and fail Slice 3 parity tests.
- Restoring only cross-harness trigger entries and not single-harness
  automation entries would leave single-harness dispatch degraded.

## Rollback

Revert the hook-config edits in `.codex/hooks.json` and
`.claude/settings.json`. Do not recreate `bridge/INDEX.md`.
