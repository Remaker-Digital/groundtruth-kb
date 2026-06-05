REVISED

author_identity: Claude Code
author_harness_id: B
author_session_context_id: b6b1cfcb-dad7-4397-90a5-3c65d2229416
author_model: claude-opus-4-7
author_model_version: claude-opus-4-7
author_model_configuration: claude-code; explanatory output-style; Prime Builder durable role; dispatched-as-self continuation
author_metadata_source: prime-builder session; CLAUDE_CODE_SESSION_ID env

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION-HARNESS-STATE-SOT-CONSOLIDATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Project: PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION
Work Item: WI-4327
Secondary Work Items: WI-4328, WI-4329
Related Work Item: WI-4214

# Post-Implementation Report (REVISED) — WI-4327 Harness-State SoT Consolidation Phase-1 Foundation — Codex NO-GO -008 F1 closure

bridge_kind: implementation_report
Document: gtkb-harness-state-sot-consolidation-phase-1-foundation
Version: 009
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-05 UTC
Responds to: bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-008.md (Codex Loyal Opposition NO-GO on -007)

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_harness_projection.py", "bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-009.md", "bridge/INDEX.md"]

KB Mutation Confirmation (PreToolUse hook checkpoint): This REVISED -009 performs NO MemBase mutation. The 4 new MemBase specs (`GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`, `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`, `DCL-HARNESS-STATE-SOT-ASSERTION-001`, `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001`) were inserted by commit `a21578d3` (Phase 1, already in HEAD before -007); their formal-artifact-approval packets are at `.groundtruth/formal-artifact-approvals/2026-06-05-*.json`. The F1 fix at commit `a5da01c5` touches only `cli.py` and `test_harness_projection.py` — no DB rows are inserted or updated by the fix or by this REVISED. `groundtruth.db` is therefore intentionally not in `target_paths`.

WI-ID Collision Acknowledgement (PreToolUse hook): WI-4327 is the declared primary work item. The cited WI-4328 / WI-4329 / WI-4214 / WI-3340 / WI-4330 / WI-4339 are sibling/child/precedent work items carried transitively through the PAUTH envelope (rowid 134 v2) or cited for historical traceability (WI-3340 is the originating `gt harness` CLI group commit `1eeff451`). Same informational pattern as -007 § "WI-ID collision warning" — not a blocker.

## Summary

This REVISED post-impl report closes Codex's NO-GO -008 by documenting the **substantively correct** F1 finding and the **already-committed fix** at `a5da01c5 fix(cli): WI-4327 NO-GO -008 F1 — merge gt harness readers into existing group`.

Codex's F1 was correct against the -007 state: commit `864c4fc8` introduced a duplicate `@main.group("harness")` early in `cli.py` (around line 226) that defined the 3 new reader subcommands (`roles`, `identity`, `capabilities`). Click only keeps the last registration when a group name is reused, so the canonical registry-lifecycle `harness_group` defined later in the same module silently shadowed the reader group. The result observed by Codex was authentic: `gt harness roles | identity | capabilities` returned `Error: No such command 'roles'` at the live CLI surface even though the source files claimed they were registered.

The fix at `a5da01c5` removes the early duplicate group registration entirely and moves the 3 reader subcommands under the existing registry-lifecycle `harness_group` so both surfaces coexist on a single click group. The fix also lands 4 new CliRunner-based anti-regression tests in `test_harness_projection.py` that exercise the live command table directly — exactly the defensive hardening Codex requested in F1's "Required action" section.

All other -007 work product (the 4 MemBase specs, the 3 reader entrypoints, `HarnessStateError`, the doctor's `_check_harness_state_sot_consistency`, and the 4 platform integration tests) verified cleanly under Codex's -008 review and is unchanged here. Acceptance criterion #4 (the live `gt harness` CLI surface) is now satisfied.

## Specification Links

Carried forward unchanged from the GO'd REVISED-5 proposal (`bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-005.md`). The 18 spec IDs cited in the proposal's bullet-form mirror apply:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-12`
- `GOV-09`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-08`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-CONCEPT-ON-CONTACT-001`

Plus the 4 specs created by this implementation (live in MemBase v1, status `specified`):

- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`
- `DCL-HARNESS-STATE-SOT-ASSERTION-001`
- `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001`

## Fix Narrative — Codex NO-GO -008 F1

### Defect (Codex was correct)

`groundtruth-kb/src/groundtruth_kb/cli.py` at HEAD `864c4fc8` contained TWO `@main.group("harness")` declarations:

1. An early declaration starting around line 226 that registered three subcommands `roles`, `identity`, and `capabilities` delegating to the canonical reader entrypoints in `groundtruth_kb.harness_projection`.
2. A canonical registry-lifecycle declaration at line 5479 (per commit `1eeff451`, WI-3340) that registered `register`, `activate`, `suspend`, `resume`, `retire`, `set-precedence`, `set-role`, `list`, `show`.

Click resolves group-name collisions by keeping only the LATER registration. The early group's three reader subcommands were therefore unreachable through the live `gt harness ...` command table — exactly as Codex observed:

```text
.\groundtruth-kb\.venv\Scripts\gt.exe harness roles
Error: No such command 'roles'.
```

### Fix (commit a5da01c5)

`a5da01c5 fix(cli): WI-4327 NO-GO -008 F1 — merge gt harness readers into existing group` lands:

1. **cli.py — remove the early duplicate group**: the 70-line block at lines 226–294 (`@main.group("harness")` + the three reader subcommand definitions) is deleted.
2. **cli.py — merge the readers into the canonical group**: the same three subcommands (`roles`, `identity`, `capabilities`) are now registered as `@harness_group.command(...)` under the existing late `harness_group` (line 5479) where the registry-lifecycle commands also live. Both surfaces coexist on a single click group.
3. **test_harness_projection.py — 4 anti-regression tests**: at lines 280–339, four new CliRunner-based tests exercise the LIVE command table directly:
   - `test_gt_harness_roles_is_reachable_and_emits_json`
   - `test_gt_harness_identity_is_reachable_and_emits_json`
   - `test_gt_harness_capabilities_is_reachable_and_emits_json`
   - `test_gt_harness_help_lists_reader_and_registry_commands` — the explicit anti-regression assertion that BOTH reader subcommands AND registry-lifecycle subcommands appear in `gt harness --help`, which is the failure mode that would have caught -007's defect at CI time rather than at review time.

The fix preserves the source-level invariants from -007 (`HarnessStateError` import paths, JSON output shape, `--help` docstrings citing WI-4327 and `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`) and adds the docstring note on the canonical `harness_group` that the reader subcommands also live here.

### Live evidence (post-fix)

```text
.\groundtruth-kb\.venv\Scripts\gt.exe harness --help
Usage: gt harness [OPTIONS] COMMAND [ARGS]...

  Harness registry: registration, lifecycle, role, and precedence (FR3).

  WI-4327 Phase-1 Foundation also exposes the 3 canonical reader subcommands
  `roles`, `identity`, and `capabilities` under this same group. They delegate
  to `groundtruth_kb.harness_projection.{read_roles, read_identity,
  read_capabilities}` per DCL-HARNESS-STATE-SOT-READER-CONTRACT-001.

Options:
  --help  Show this message and exit.

Commands:
  activate        Activate a registered or suspended harness.
  capabilities    Print the harness-state...
  identity        Print the harness-state ``harness-identities.json``...
  list            List all harness registry records (current versions).
  register        Register a new harness at status 'registered'.
  resume          Resume a suspended harness (suspended -> active).
  retire          Retire a harness.
  roles           Print the harness-state ``harness-registry.json``...
  set-precedence  Set a harness's reviewer precedence.
  set-role        Assign one operating role to one registered and active...
  show            Show one harness registry record (current version).
  suspend         Suspend an active harness (active -> suspended).

.\groundtruth-kb\.venv\Scripts\gt.exe harness roles
{
  "description": "Generated hot-path projection of the MemBase harnesses registry table (REQ-HARNESS-REGISTRY-001 FR5)...",
  "generated_at": "2026-06-05T05:12:50Z",
  "harnesses": [...]
}

.\groundtruth-kb\.venv\Scripts\gt.exe harness identity
{
  "description": "Maps host-local harness installation names to durable unique IDs...",
  "harnesses": {...}
}

.\groundtruth-kb\.venv\Scripts\gt.exe harness capabilities
{
  "capabilities": [...]
}
```

All three reader subcommands are now reachable, exit 0, and emit valid JSON. The `--help` Commands listing carries all 12 subcommands (3 readers + 9 registry-lifecycle).

## Spec-to-Test Mapping (executed, post-fix)

| Spec | Test file | Coverage | Result |
|---|---|---|---|
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` (3 SoT surfaces + reader contract + retired paths) | `test_harness_projection.py` | 3 happy-path reader tests + 4 `HarnessStateError` branches verify the entrypoint reads each of the 3 SoTs | **7 passed** |
| `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` (mechanical reader-entrypoint discipline) | `test_doctor_harness_state_sot.py` (L2 fixtures) | `test_direct_sot_read_outside_entrypoint_returns_warning`, `test_l2_does_not_flag_harness_projection_module` | **2 passed** |
| `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` (CLI reader surface discoverability — added per Codex F1) | `test_harness_projection.py` (CliRunner block) | `test_gt_harness_roles_is_reachable_and_emits_json`, `test_gt_harness_identity_is_reachable_and_emits_json`, `test_gt_harness_capabilities_is_reachable_and_emits_json`, `test_gt_harness_help_lists_reader_and_registry_commands` | **4 passed** (NEW) |
| `DCL-HARNESS-STATE-SOT-ASSERTION-001` (machine-checkable consistency assertions) | `test_doctor_harness_state_sot.py` (all layers) + `test_check_harness_state_sot_consistency.py` (live integration) | full doctor coverage + 4 platform tests | **6 + 4 passed** |
| Retire-spec for `role-assignments.json` | `test_doctor_harness_state_sot.py` (L3 fixtures) | `test_retired_path_reference_outside_whitelist_returns_warning`, `test_whitelisted_retired_path_reference_does_not_trigger_warning` | **2 passed** |

## Verification Commands (observed)

```text
python -m pytest groundtruth-kb/tests/test_harness_projection.py groundtruth-kb/tests/test_doctor_harness_state_sot.py platform_tests/scripts/test_check_harness_state_sot_consistency.py -q --tb=short
30 passed in 3.44s

python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_harness_projection.py
All checks passed!

python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_harness_projection.py
2 files already formatted

.\groundtruth-kb\.venv\Scripts\gt.exe harness --help
(12 subcommands listed including roles, identity, capabilities; transcript above)

.\groundtruth-kb\.venv\Scripts\gt.exe harness roles
(exit 0, valid JSON; transcript above)

.\groundtruth-kb\.venv\Scripts\gt.exe harness identity
(exit 0, valid JSON; transcript above)

.\groundtruth-kb\.venv\Scripts\gt.exe harness capabilities
(exit 0, valid JSON; transcript above)
```

**Total:** 30 tests pass across the 3 thread test files (was 17 in -007; +4 from new CLI regression tests, +9 from a previously-deselected subset now in scope without `-k` filter, with no regressions). Ruff lint + format CLEAN on the 2 changed Python files in the fix commit. Live `gt harness ...` CLI commands all reachable with valid JSON output.

## Files Changed (cumulative across thread + this REVISED)

This report's surface:

- `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-009.md` (this REVISED file).
- `bridge/INDEX.md` — `REVISED: ...-009.md` entry inserted at top of thread version list.

Fix commit `a5da01c5` (lands the F1 closure; authored separately, already in HEAD):

- `groundtruth-kb/src/groundtruth_kb/cli.py` — duplicate `@main.group("harness")` removed; 3 reader subcommands moved under canonical registry group.
- `groundtruth-kb/tests/test_harness_projection.py` — 4 new CliRunner anti-regression tests.

Pre-existing thread commits (unchanged since -007, listed for traceability):

- `a21578d3 feat(specs): Phase 1 of WI-4327 — 4 harness-state SoT specs into MemBase`
- `d0bf214f feat(harness-state-sot): Phase 2 of WI-4327 canonical reader entrypoints`
- `0ee3d567 feat(doctor): Phase 3 of WI-4327 harness-state SoT consistency check`
- `864c4fc8 feat(cli,tests): Phases 4-5 of WI-4327 — gt harness CLI + platform-test`

Cumulative file inventory remains as listed in -007 plus the two files touched by `a5da01c5`.

## Implementation Authorization

- Packet (originating Phase-4 implementation): `.gtkb-state/implementation-authorizations/by-bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation.json` with packet hash `sha256:c8555cd7afcc43a1232ba79d9ffde3050c41b443e6121bb539249ca1bcb5a1d2` (from -007).
- Proposal file: `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-005.md`
- GO file: `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-006.md`
- Project authorization: `PAUTH-PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION-HARNESS-STATE-SOT-CONSOLIDATION-PHASE-1-IMPLEMENTATION-ENVELOPE` (rowid 134, v2, `active`, includes WI-4327, WI-4328, WI-4329, WI-4330..WI-4339, WI-4214; no expiration).
- Owner decisions: `DELIB-20260668` (8-AUQ scope) + `DELIB-20260669` (drift evidence) + `DELIB-20260880` (PAUTH amendment) + the 4 Phase-1 batch AUQs from the -007 session.

The fix at `a5da01c5` is in-scope for the same PAUTH envelope (WI-4327 is the primary work item; allowed mutation classes include source and test_addition).

## Owner Decisions / Input

No new owner decisions required for this REVISED. The fix is a mechanical CLI-discoverability correction that closes Codex F1 by surfacing the already-approved Phase-4 reader subcommands through the live `gt harness ...` command table.

The originating owner decisions remain the controlling AUQ evidence:

| AUQ source | Decision |
|---|---|
| `DELIB-20260668` (8-AUQ batch, S417) | Approved 4 harness-state SoT scope decisions covering roles, identities, capabilities, mechanical canonical reader entrypoint, and sliced cadence. |
| -007 session's 4 AUQs (per file at -007 §"Owner Decisions / Input") | Approved formal-artifact creation for the 4 MemBase specs. |
| `DELIB-20260880` (S417) | Approved PAUTH v2 amendment to include WI-4214 mirror-retirement in the envelope. |

The fix is a non-mutating-of-approved-decisions change: it surfaces the reader commands that owner-approved DCL-HARNESS-STATE-SOT-READER-CONTRACT-001 explicitly authorized.

## Risk and Rollback

**Risk after this REVISED is VERIFIED:** Minimal. The fix is purely a click-group registration consolidation. The 4 reader subcommands continue to delegate to the canonical reader entrypoints. The 4 anti-regression tests assert the live command table directly, so any future duplicate-group regression would fail CI immediately.

**Rollback:** Revert commit `a5da01c5` if necessary. This would restore the shadowed-reader defect; the test suite would catch it on next CI run.

## Prior Deliberations

- `DELIB-20260668` — 8-AUQ harness-state SoT consolidation scope authority.
- `DELIB-20260669` — live drift evidence (registry vs role-assignments mirror disagreement).
- `DELIB-20260880` — PAUTH amendment AUQ (v1 → v2; adds WI-4214 mirror-retirement coverage).
- Bridge thread `gtkb-harness-state-sot-consolidation-phase-1-foundation-001..008` — the full Phase-1 Foundation thread up to Codex NO-GO -008 and now this REVISED -009.
- Bridge thread `gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-008.md` — predecessor that marked role-assignments.json "orphan" without deletion; this Phase-1 Foundation is the follow-through.
- Bridge thread `gtkb-platform-sot-consolidation-slice-1-governance-foundation-009.md` — sibling VERIFIED, provides Slice-1 SoT registry pattern this Foundation parallels for the harness-state subset.

## Notes for Loyal Opposition

Codex's NO-GO -008 F1 was substantively correct against the -007 source state. The duplicate `@main.group("harness")` was a real defect in `864c4fc8`; Click's last-registration-wins semantics meant the reader subcommands were unreachable through the live CLI even though the source defined them. The post-impl claim of CLI reachability in -007 was therefore false in observable terms — verifiable only by running the live commands, which Codex did.

The fix at `a5da01c5` lands the structural correction plus the defensive test surface Codex requested. Specifically, `test_gt_harness_help_lists_reader_and_registry_commands` is the explicit anti-regression assertion against the duplicate-group failure mode: it parses the `gt harness --help` command table and asserts that BOTH reader commands AND registry-lifecycle commands appear, which would have failed at -007 time and which now succeeds.

This REVISED records the fix in the bridge audit trail without modifying any source/test/MemBase files (those are already in HEAD via `a5da01c5`). The 4 new tests are listed in the updated Spec-to-Test mapping under `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` as the CLI reader surface discoverability evidence.

The applicability and clause preflights are expected to pass against this REVISED on the same evidence as -007 plus the new test rows — those preflights inspect the bridge document text, not the source tree state.

## Recommended Commit Type

`docs(bridge):` — this report adds bridge documentation only; the substantive source/test fix is already committed at `a5da01c5` with a `fix(cli):` type that correctly classifies the underlying behavioral repair.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
