REVISED
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T14-36-38Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal — WI-5661 governed recovery for all six live skill-rename breaks

bridge_kind: prime_proposal
Document: gtkb-wi5661-terminal-verdict-recovery
Version: 003
Responds to: bridge/gtkb-wi5661-terminal-verdict-recovery-002.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5661-SKILL-RENAME-LIVE-BREAK-20260724
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5661

target_paths: ["scripts/gtkb_bridge_writer.py", ".claude/hooks/bridge-axis-2-surface.py", "config/hooks/gtkb-bridge-axis-2-surface.py", "scripts/per_thread_finalization_repair.py", "scripts/harness_parity_phase2.py", "scripts/verify_antigravity_dispatch.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/scripts/test_bridge_axis_2_surface.py", "platform_tests/scripts/test_per_thread_finalization_repair.py", "platform_tests/scripts/test_harness_parity_phase2.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

This revision recovers the full six-finding WI-5661 scope without treating the
untracked VERIFIED artifact as terminal evidence. It first establishes
attributable ownership of the pre-existing worktree changes, then repairs every
original source finding together with a named regression test. The dual AXIS-2
hook route is narrowed to the canonical
.claude/skills/gtkb-bridge/helpers/scan_bridge.py in both copies: no retained
legacy fallback is permitted.

## Claim

Prime Builder proposes a claim-protected recovery sequence for the six
WI-5651 skill-rename live breaks. This revision itself authorizes no source
mutation: source work remains blocked until the predecessor artifacts and
current dirty hunks are reconciled, a clean attributable baseline is recorded,
and Loyal Opposition issues a fresh GO.

## Requirement Sufficiency

Existing requirements sufficient. WI-5661, its active project authorization,
the cited governance specifications, and the preserved predecessor chain are
sufficient to govern the reconciliation and a later bounded implementation.
No new requirement is required before Loyal Opposition reviews this revision;
the implementation-start preconditions remain the separate hunk-reconciliation
record, fresh GO, and active implementation claim.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- ADR-CODEX-HOOK-PARITY-FALLBACK-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001

## Prior Deliberations And Evidence

- DELIB-20260724-WI5661-PROCESS-AUTHORIZATION authorizes governed processing,
  not a bypass of review, source scope, or verification.
- DELIB-202667193 retains per-slice Loyal Opposition GO and VERIFIED gates.
- bridge/gtkb-wi5661-skill-rename-live-breaks-003.md is the predecessor
  partial implementation report; it deferred the config mirror, parity, and
  Antigravity-anchor findings.
- bridge/gtkb-wi5661-skill-rename-live-breaks-004.md is an untracked,
  file-only VERIFIED artifact with no Commit Finalization Evidence. It is
  evidence to preserve, not terminal closure.
- The predecessor implementation claim for
  gtkb-wi5661-skill-rename-live-breaks is expired. No active claim is
  inferred from the current dirty worktree bytes.

## Governed Reconciliation Sequence

1. Preserve both predecessor bridge files unchanged. Record their false-terminal
   defect by reference; do not delete, stage, amend, or rely on the untracked
   -004.md verdict.
2. Quarantine the current un-attributed source state:
   .claude/hooks/bridge-axis-2-surface.py,
   scripts/gtkb_bridge_writer.py,
   scripts/harness_parity_phase2.py, and
   scripts/per_thread_finalization_repair.py are modified;
   config/hooks/gtkb-bridge-axis-2-surface.py is untracked. The affected
   test and migration-worktree inputs must likewise be treated as external
   until their owner and hunk provenance are recorded.
3. Before implementation, obtain a governed reconciliation artifact that
   identifies each retained hunk, its originating claim, and its reviewed
   target path; otherwise restore only under a separate approved recovery.
   This WI-5661 proposal does not assert a clean baseline and does not
   authorize a path-based sweep or unrelated routing changes.
4. After the reconciliation is independently reviewed and a fresh GO plus
   implementation claim exist, repair the six source findings and only the
   mapped tests below. The implementation report must identify the resulting
   immutable commit and the exact changed paths before an LO finalizer is run.

## Proposed Implementation After GO

- Update scripts/gtkb_bridge_writer.py to resolve the live gtkb-verify
  finalizer helper; preserve all unrelated responder-routing hunks outside this
  WI.
- Make .claude/hooks/bridge-axis-2-surface.py load only
  .claude/skills/gtkb-bridge/helpers/scan_bridge.py; remove the segmented
  .claude / skills / bridge / helpers / scan_bridge.py fallback because the
  legacy helper does not exist and cannot provide compatibility.
- Make config/hooks/gtkb-bridge-axis-2-surface.py use the same canonical
  direct helper path. This restores M004's contiguous
  hook-bridge-axis-helper-route adaptation without changing the WI-5640 alias
  catalog or adding a broad retained compatibility alias.
- Update scripts/per_thread_finalization_repair.py,
  scripts/harness_parity_phase2.py, and
  scripts/verify_antigravity_dispatch.py for the remaining original live
  skill-rename breaks, including the canonical harness-registry fixture
  contract.
- Add focused tests only in the declared test files. In particular, the AXIS-2
  regression must assert both hook copies select the canonical helper and that
  no legacy segmented fallback expression can return. This prevents a future
  M004 ADAPTATION_NOT_APPLICABLE mismatch without claiming that WI-5661
  rewrites WI-5640's migration scanner.

## Cross-Harness Disposition

- Claude: the tracked AXIS-2 hook and its config source-of-record remain a
  coupled pair and use one canonical managed helper path.
- Codex: no Codex hook or adapter behavior changes; bridge writer and
  finalization tests retain their existing role and finalization gates.
- Antigravity: only the shared verdict-anchor resolver changes, verified by
  the declared dispatch tests; no harness-local scratch or runtime state is
  authoritative.
- Other harnesses: the shared parity registry and provider-finalizer behavior
  are verified through the declared shared tests. No typed waiver is requested.

## Specification-Derived Verification Plan

| Finding | Source target | Test target and selector | Required assertion |
| --- | --- | --- | --- |
| Provider finalizer path | scripts/gtkb_bridge_writer.py | platform_tests/scripts/test_gtkb_bridge_writer.py::test_provider_finalizer_uses_gtkb_verify_helper | Provider finalization resolves the live gtkb-verify helper and fails closed for no other path. |
| AXIS-2 source and mirror | .claude/hooks/bridge-axis-2-surface.py, config/hooks/gtkb-bridge-axis-2-surface.py | platform_tests/scripts/test_bridge_axis_2_surface.py::test_t13_hook_and_config_use_canonical_helper_without_legacy_segmented_fallback | Both copies use the identical canonical direct path; no legacy split-path fallback remains. |
| Per-thread repair import | scripts/per_thread_finalization_repair.py | platform_tests/scripts/test_per_thread_finalization_repair.py::test_terminal_verified_clean_targets_is_candidate and a new stale-helper regression in that file | Import and candidate evaluation use the canonical managed helper path. |
| Harness parity registry | scripts/harness_parity_phase2.py | platform_tests/scripts/test_harness_parity_phase2.py::test_report_includes_candidate_work_items_for_unwaived_gaps and ::test_wi4926_provider_readiness_contract_is_documented_and_registered | Fixture creates the canonical registry filename and parity output is stable. |
| Antigravity verdict anchors | scripts/verify_antigravity_dispatch.py | platform_tests/scripts/test_verify_antigravity_dispatch.py::test_inspect_verdict_anchor_guard_detects_helper_coverage and ::test_evaluate_readiness_reports_verdict_anchor_guard | Verdict-anchor guard locates the canonical gtkb-verify helper. |

After the mapped tests pass, run:

    groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_bridge_axis_2_surface.py platform_tests/scripts/test_per_thread_finalization_repair.py platform_tests/scripts/test_harness_parity_phase2.py platform_tests/scripts/test_verify_antigravity_dispatch.py -q --tb=short
    groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/gtkb_bridge_writer.py .claude/hooks/bridge-axis-2-surface.py scripts/per_thread_finalization_repair.py scripts/harness_parity_phase2.py scripts/verify_antigravity_dispatch.py
    groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/gtkb_bridge_writer.py .claude/hooks/bridge-axis-2-surface.py scripts/per_thread_finalization_repair.py scripts/harness_parity_phase2.py scripts/verify_antigravity_dispatch.py
    python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5661-terminal-verdict-recovery
    python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5661-terminal-verdict-recovery

## Acceptance Criteria

- The predecessor -003.md and untracked -004.md are named, preserved, and
  never used as terminal or commit-finalization evidence.
- All six original findings have a concrete source path, test path, selector,
  expected assertion, and immutable reviewed commit; none are silently
  deferred.
- Both AXIS-2 hook copies use only the canonical gtkb-bridge helper path;
  the legacy segmented fallback is absent.
- The WI-5661 diff contains no unapproved responder-routing hunk, no unrelated
  migration-scanner change, and no un-attributed worktree bytes.
- All mapped tests, Ruff lint, and Ruff format checks pass before an
  independently authored LO VERIFIED transaction.

## Risks And Rollback

The primary risk is misattributing pre-existing dirty hunks to this recovery.
Fail closed until their provenance is independently reconciled. Rollback is a
separate governed revert of only the immutable recovery commit; numbered bridge
history and quarantined predecessor evidence remain append-only.

## Owner Decisions / Input

No additional owner decision is requested. The current task is blocked on
governed hunk reconciliation and independent Loyal Opposition review, not a
preference choice.

## Recommended Commit Type

fix
