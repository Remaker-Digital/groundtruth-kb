# Emergency Harness Registrar / Dispatcher Conformance Plan

Date: 2026-05-19
Role: Prime Builder emergency repair
Owner decision: DELIB-S359-GOVERNANCE-SUSPENSION-HARNESS-ROLE-REPAIR-2026-05-19

## Emergency Scope

Mike suspended normal GT-KB governance and bridge operation for the narrow purpose
of correcting foundational harness registrar, dispatcher, and review-context
isolation defects. This plan documents the Prime Builder repair path. The repair
continues without waiting for bridge review because the bridge/role machinery is
the defective surface under correction.

Credential safety, project-root boundaries, and release/deploy approvals remain
in force. The temporary suspension applies only to normal bridge review gating
and role-governance sequencing that would otherwise prevent the repair.

## Clarified Requirements

1. Harness registration is separate from operating-role assignment.
2. Harness activation and suspension are single-command lifecycle operations;
   they do not unregister the harness.
3. A harness may be suspended by owner declaration or by non-operating
   detection.
4. Role assignment is a single command assigning one role to one registered and
   active harness.
5. Exactly one active harness must be assigned Prime Builder.
6. Exactly one active harness must be assigned Loyal Opposition.
7. Prime Builder and Loyal Opposition must be assigned to different active
   harnesses when more than one active harness exists.
8. No session context may review a document created in the same session context;
   all reviews require an unrelated session context.
9. Every bridge artifact must carry accurate author identity, model, model
   version, and model configuration metadata for future audits. Missing or
   placeholder runtime metadata must fail closed rather than be guessed.

## Implementation Plan

1. Stop unsafe active-session bridge auto-drain while the emergency suspension is
   active, and prevent dual-role active sessions from auto-draining LO review
   work.
2. Make registration role-free: `gt harness register` records identity and
   capabilities only; roles are assigned later.
3. Make `gt harness activate` handle both `registered -> active` and
   `suspended -> active`, preserving `resume` only as a compatibility alias.
4. Make `gt harness suspend` a single command with an explicit suspension cause
   (`owner-declared` or `non-operating-detected`).
5. Recompute role assignments after lifecycle transitions:
   - no inactive harness may retain PB or LO;
   - one active harness receives both PB and LO;
   - two or more active harnesses receive exactly one PB and exactly one LO on
     distinct active harnesses.
6. Replace the old "promote to PB and make every other harness LO" behavior with
   `gt harness set-role --harness <id> --role <prime-builder|loyal-opposition>`.
7. Update topology and invariant checks to compute over active harnesses only.
8. Add same-session review protection to bridge writer validation when session
   metadata is present, and suppress the auto-drain path that caused a dual-role
   active session to review its own NEW/REVISED work.
9. Reconcile the live harness registry projection so Codex `A` is the single
   active harness with both PB and LO while Claude `B` remains suspended with no
   role.
10. Add authoritative bridge author/runtime metadata enforcement:
    - helper-mediated bridge writes insert metadata from explicit runtime
      values, environment, or `.gtkb-state/bridge-author-metadata/current.json`;
    - direct bridge writes are denied by the bridge compliance gate when the
      required audit fields are missing or placeholders;
    - bridge-propose, revise, and implementation-report helper paths use the
      same fail-closed metadata contract.

## Verification Plan

- `python -m pytest platform_tests/hooks/test_bridge_stop_drain.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_bridge_author_metadata.py -q --tb=short`
- `python -m pytest platform_tests/hooks/test_bridge_author_metadata_gate.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py -q --tb=short`
- `python -m pytest platform_tests/skills/test_bridge_propose_helper.py platform_tests/skills/test_bridge_revise_helper.py platform_tests/skills/test_bridge_impl_report_helper.py -q --tb=short`
- `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/groundtruth_kb/cli/test_harness_cli.py -q --tb=short`
- Targeted live-state check of `harness-state/harness-registry.json` after
  reconciliation.

## Residual Risk

The metadata repair fails closed when authoritative model/version/configuration
values are not available. That protects audit integrity but means any harness
startup path that cannot surface accurate runtime metadata must be updated
before it can file bridge artifacts. Direct shell write detection remains
pattern-based in the Codex Bash adapter; helper-mediated writes and direct
Write/Edit payloads are covered mechanically.

## Implementation Completed

Completed during the emergency suspension:

- Added a local governance suspension marker at
  `.gtkb-state/governance-suspension.json` and made
  `.claude/hooks/bridge-stop-drain.py` suppress auto-drain while that marker is
  active.
- Prevented dual-role active sessions from auto-draining LO review work
  (`NEW`/`REVISED`) because same-session authorship cannot be excluded in that
  path.
- Made `gt harness register` role-free; the deprecated hidden `--role` option
  now fails if used.
- Made `gt harness activate` cover both registered and suspended harnesses.
- Added `gt harness suspend --cause owner-declared|non-operating-detected`.
- Added DB-level role reconciliation after lifecycle transitions: inactive
  harnesses carry no operating roles; one active harness carries PB+LO; multiple
  active harnesses have exactly one PB and exactly one LO on distinct active
  harnesses.
- Changed `gt harness set-role` to require `--role
  prime-builder|loyal-opposition` and assign that role only to an active
  harness.
- Updated topology and invariant checks to compute over active harnesses only.
- Added metadata-aware same-session review rejection to
  `scripts/gtkb_bridge_writer.py` for helper-mediated LO review writes.
- Added `scripts/bridge_author_metadata.py` as the shared fail-closed
  author/runtime metadata contract for bridge artifacts.
- Made `scripts/gtkb_bridge_writer.py`, the bridge-propose helper, the
  bridge-revision helper, and the post-implementation-report helper insert or
  validate required bridge author metadata before live filing.
- Made `.claude/hooks/bridge-compliance-gate.py` and the scaffold template deny
  bridge artifacts whose status is `NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED`,
  or `ADVISORY` when author identity, harness ID, session-context ID, model,
  model version, or model configuration is missing or placeholder-like.
- Updated the Codex bridge-compliance Bash adapter fixtures and generated
  harness capability registry checksum after the canonical bridge-propose helper
  changed.
- Reconciled live harness state: Codex `A` is the only active harness and holds
  both PB and LO; Claude `B` is suspended with no role; Antigravity `C` is
  registered with no role.

## Verification Completed

- `python -m py_compile ...` on touched runtime modules: PASS.
- `python -m pytest platform_tests/hooks/test_bridge_stop_drain.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py -q --tb=short`: PASS, 174 passed, 3 skipped, 2 xfailed.
- `python -m ruff check ...`: PASS.
- `python -m ruff format --check ...`: PASS.
- `python -m pytest platform_tests/hooks/test_bridge_stop_drain.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py platform_tests/hooks/test_bridge_compliance_gate_worktree_root.py platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/hooks/test_bridge_compliance_gate_fenced_code.py platform_tests/hooks/test_bridge_author_metadata_gate.py platform_tests/scripts/test_codex_bridge_compliance_gate.py platform_tests/scripts/test_bridge_author_metadata.py platform_tests/skills/test_bridge_revise_helper.py platform_tests/skills/test_bridge_impl_report_helper.py platform_tests/skills/test_bridge_propose_helper.py -q --tb=short`: PASS, 303 passed, 3 skipped, 2 xfailed.
- `python scripts/generate_codex_skill_adapters.py --update-registry --check`:
  PASS, 32 adapters current.
- Live invariant check: `RolePartitionSummary(prime_builder_id='A',
  loyal_opposition_id='A', active_harness_ids=('A',))`.
