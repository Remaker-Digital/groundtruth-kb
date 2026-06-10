NEW
author_identity: Prime Builder (Codex)
author_harness_id: A
author_session_context_id: 019e9f42-2f94-7a63-bb19-acc957702b65
author_model: GPT-5 Codex
author_model_version: 2026-06-06
author_model_configuration: Codex desktop; Prime Builder; owner-directed reliability fix; high reasoning
author_metadata_source: explicit Codex bridge filing metadata

# Implementation Proposal: Codex Wrap/Topic Hook Uses Canonical Startup Lifecycle Guard

bridge_kind: prime_proposal
Document: gtkb-codex-wrapup-startup-gate-guard-sot
Version: 001

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4389
target_paths: [".codex/gtkb-hooks/session_wrapup_trigger_dispatch.py", "platform_tests/scripts/test_session_wrapup_trigger_dispatch.py", "platform_tests/scripts/test_codex_hook_parity.py"]

## Summary

Owner-visible evidence from a parallel Prime Builder agent shows the agent
correctly found a live, authorized `GO` bridge item, then aborted before
implementation because `GTKB-STARTUP-INPUT-GATE` believed startup disclosure
was still awaiting the owner follow-up message. The in-root canonical Codex
lifecycle guard under `harness-state/codex/session-lifecycle-guard.json` is
clear, but the Codex wrap/topic hook still reads the legacy runtime file at
`.codex/gtkb-hooks/session-lifecycle-guard.json`.

This proposal repairs that missed source-of-truth consumer. The Codex
`session_wrapup_trigger_dispatch.py` hook should resolve its startup input gate
from the canonical harness-state guard by default, preserve the existing
`GTKB_LIFECYCLE_GUARD_PATH` override seam for tests and alternate harnesses,
and stop treating stale legacy `.codex/gtkb-hooks/session-lifecycle-guard.json`
state as authoritative.

## Bridge Filing Evidence

This proposal is filed as a versioned bridge artifact under `bridge/` and will
be inserted into `bridge/INDEX.md` as the latest `NEW` line for `Document:
gtkb-codex-wrapup-startup-gate-guard-sot`. No prior bridge version is deleted
or rewritten. The proposal is routed through the helper-mediated Codex
non-bypass bridge write path.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the bridge and `bridge/INDEX.md` are the
  workflow source of truth for proposal, implementation, report, and
  verification state.
- `GOV-RELIABILITY-FAST-LANE-001` - the work is a small single-concern
  reliability defect fix under the active reliability-fixes project.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner-visible defect is captured
  as `WI-4389` before implementation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the fix preserves traceability from
  owner directive to work item, proposal, tests, and implementation report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the defect moves through explicit
  backlog, proposal, implementation, report, and verification lifecycle states.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  cites the governing specifications and maps acceptance to tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation
  verification must carry forward the linked specs and executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the required project
  authorization, project, and work-item metadata lines are present above.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` - `WI-4389` is under
  `PROJECT-GTKB-RELIABILITY-FIXES`, whose standing authorization covers this
  source/test/hook repair class.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook behavior and fallback
  parity must remain explicit and mechanically checked.
- `.claude/rules/project-root-boundary.md` - all live GT-KB files and target
  paths remain under `E:\GT-KB`.

## Requirement Sufficiency

Existing requirements are sufficient. The durable role/startup model already
places harness-local lifecycle guard state under `harness-state/<harness>/`.
The active project instructions identify `harness-state/harness-identities.json`
and `harness-state/harness-registry.json` as persistent role authority, and the
live startup code already uses `harness-state/codex/session-lifecycle-guard.json`
for the canonical Codex startup guard. This slice does not create a new
requirement; it aligns one missed Codex hook consumer with that existing
source-of-truth placement.

## Prior Deliberations

- `DELIB-1531` - Loyal Opposition startup symmetry review; relevant because it
  identified temporally incoherent startup lifecycle state as a recurring
  startup failure mode.
- `DELIB-1522` - startup trigger awareness and parallel automation guidance;
  relevant because this defect occurs in an autonomous/parallel startup and
  bridge-dispatch context.
- `bridge/harness-state-authority-migration-2026-04-27-008.md` - prior
  verified migration evidence that lifecycle guard authority moved into
  harness-state surfaces.
- `bridge/gtkb-startup-relay-pretooluse-read-exemption-004.md` and
  `bridge/gtkb-startup-relay-truncation-fix-refile-012.md` - verified prior
  fixes in the same startup-input-gate family.
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md`,
  `bridge/gtkb-bridge-active-session-autodrain-008.md`, and
  `bridge/gtkb-bridge-parallel-session-collision-006.md` - verified bridge
  session/parallelism repairs showing this is a recurring class of stale or
  split control-plane state, not a one-off transcript anomaly.

No prior deliberation found rejects using `harness-state/codex` as the canonical
Codex lifecycle guard location. The proposal narrows to one missed consumer.

## Owner Decisions / Input

Owner directive on 2026-06-06: "Please inspect transcripts and determine if
this is a recurring problem. If it is, please propose a solution and work the
fix(es) through to VERIFIED."

This proposal follows that directive. It requires no credential lifecycle
action, production deployment, formal specification mutation, or owner action
before implementation. The active reliability fast-lane standing authorization
is `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.

## Investigation Findings

1. The active parallel Prime Builder thread selected a latest authorized `GO`
   bridge item, then reported that implementation could not start because
   `GTKB-STARTUP-INPUT-GATE` blocked all shell commands as stale
   "awaiting owner next message" state.
2. The canonical in-root guard at
   `harness-state/codex/session-lifecycle-guard.json` is clear:
   `discard_next_user_prompt: false` and `startup_response_pending: false`.
3. The legacy ignored guard at `.codex/gtkb-hooks/session-lifecycle-guard.json`
   still exists as mutable runtime state and can carry stale startup fields.
4. `scripts/workstream_focus.py` and `scripts/session_self_initialization.py`
   already route Codex lifecycle guard reads/writes to
   `harness-state/codex/session-lifecycle-guard.json`.
5. `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` still hard-codes
   `OUT_DIR / "session-lifecycle-guard.json"`, making it a missed consumer of
   the canonical harness-state migration.

## Proposed Implementation

1. Replace the module-level legacy `LIFECYCLE_GUARD_PATH = OUT_DIR /
   "session-lifecycle-guard.json"` with a small `_lifecycle_guard_path()`
   helper.
2. `_lifecycle_guard_path()` should first honor `GTKB_LIFECYCLE_GUARD_PATH`
   when set, using `Path(...).expanduser().resolve()`.
3. When no override is present, it should return
   `PROJECT_ROOT / "harness-state" / HARNESS_NAME /
   "session-lifecycle-guard.json"`.
4. `_startup_input_gate_active()` should read `_lifecycle_guard_path()` with
   UTF-8-sig tolerance, matching the guard's existing JSON shape.
5. Add focused regression tests proving stale legacy state is ignored and
   canonical pending state still blocks.
6. Extend the Codex hook parity test so future hook changes cannot reintroduce
   the legacy `.codex/gtkb-hooks/session-lifecycle-guard.json` source of truth.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Do not introduce credential fixtures; lifecycle guard JSON uses only boolean state. | Bridge helper credential scan and focused source review. | |
| CQ-PATHS-001 | Yes | Keep all target paths under `E:\GT-KB` and use root-relative path construction. | Applicability preflight, target path review, and parity check. | |
| CQ-COMPLEXITY-001 | Yes | Add one small path resolver helper; no state-machine rewrite. | Ruff plus focused tests. | |
| CQ-CONSTANTS-001 | Yes | Reuse `PROJECT_ROOT`, `HARNESS_NAME`, and `GTKB_LIFECYCLE_GUARD_PATH`; avoid duplicating guard strings beyond tests. | Code review and parity assertion. | |
| CQ-SECURITY-001 | Yes | Preserve fail-closed behavior for canonical active startup state; do not broaden shell or filesystem permissions. | Positive and negative startup-gate tests. | |
| CQ-DOCS-001 | N/A | No public CLI, API, or user docs surface changes. | Scope review. | Internal hook repair only. |
| CQ-TESTS-001 | Yes | Add two focused hook tests and one parity assertion. | Targeted pytest and `check_codex_hook_parity.py`. | |
| CQ-LOGGING-001 | N/A | No new logging behavior. | Source review. | The hook only emits existing context responses. |
| CQ-VERIFICATION-001 | Yes | Map each cited behavior to executed tests in the post-implementation report. | Targeted pytest, ruff, format-check, and parity command evidence. | |

## Spec-Derived Test Plan

- Add `test_startup_input_gate_uses_harness_state_guard_not_legacy_codex_guard`
  to `platform_tests/scripts/test_session_wrapup_trigger_dispatch.py`. It
  should create a stale legacy guard with active values plus a clear canonical
  `harness-state/codex` guard, then assert `_startup_input_gate_active()` is
  false and `_lifecycle_guard_path()` resolves to the canonical guard.
- Add `test_startup_input_gate_blocks_when_canonical_guard_is_active` to the
  same file. It should create only a canonical active guard and assert
  `_startup_input_gate_active()` is true.
- Extend `platform_tests/scripts/test_codex_hook_parity.py` so the wrap/topic
  hook text must contain `_lifecycle_guard_path` and `harness-state`, and must
  not contain the legacy `OUT_DIR / "session-lifecycle-guard.json"` guard
  assignment.
- Run `python -m pytest platform_tests/scripts/test_session_wrapup_trigger_dispatch.py platform_tests/scripts/test_codex_hook_parity.py -q --tb=short`.
- Run `python -m ruff check .codex/gtkb-hooks/session_wrapup_trigger_dispatch.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py platform_tests/scripts/test_codex_hook_parity.py`.
- Run `python -m ruff format --check .codex/gtkb-hooks/session_wrapup_trigger_dispatch.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py platform_tests/scripts/test_codex_hook_parity.py`.
- Run `python scripts/check_codex_hook_parity.py --project-root E:\GT-KB`.

## Acceptance Criteria

1. The Codex wrap/topic hook reads canonical startup lifecycle state from
   `harness-state/codex/session-lifecycle-guard.json` by default.
2. `GTKB_LIFECYCLE_GUARD_PATH` remains available for tests and alternate
   harness wiring.
3. A stale `.codex/gtkb-hooks/session-lifecycle-guard.json` cannot suppress
   wrap/topic dispatch when the canonical guard is clear.
4. Canonical active `discard_next_user_prompt` or `startup_response_pending`
   state still blocks as before.
5. Targeted pytest, ruff, and Codex hook parity checks pass.
6. Post-implementation report carries forward the linked specs, the executed
   commands, observed results, and receives Loyal Opposition `VERIFIED`.

## Clause Scope Clarification

This is a single-defect source/test/hook repair. It is not a bulk backlog
operation, not a formal artifact mutation, not a project lifecycle mutation,
not a schema migration, and not a deployment. No formal-artifact-approval
packet is required. All target paths are under `E:\GT-KB`.

## Files Expected To Change

- `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`
- `platform_tests/scripts/test_session_wrapup_trigger_dispatch.py`
- `platform_tests/scripts/test_codex_hook_parity.py`

## Risk and Rollback

Risk is low and localized to Codex wrap/topic dispatch suppression. The main
risk is accidentally weakening the startup input gate. The regression tests
cover both sides: stale legacy clear-path behavior and canonical active block
behavior. Rollback is to revert the three target files, which restores the
legacy hook behavior and reopens the stale-guard defect.

## Pre-Filing Preflight

Pending-content preflights will be run before live filing:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-codex-wrapup-startup-gate-guard-sot --content-file .gtkb-state/bridge-propose-drafts/gtkb-codex-wrapup-startup-gate-guard-sot-001.md`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-codex-wrapup-startup-gate-guard-sot --content-file .gtkb-state/bridge-propose-drafts/gtkb-codex-wrapup-startup-gate-guard-sot-001.md`

The live bridge helper will also run the Codex non-bypass bridge-compliance
audit before writing `bridge/gtkb-codex-wrapup-startup-gate-guard-sot-001.md`.

## Recommended Commit Type

`fix:` - repairs a stale startup lifecycle guard source-of-truth consumer.
