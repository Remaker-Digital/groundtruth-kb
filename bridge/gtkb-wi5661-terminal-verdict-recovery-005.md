REVISED
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T15-05-59Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal — WI-5661 six live-break recovery after hunk reconciliation

bridge_kind: prime_proposal
Document: gtkb-wi5661-terminal-verdict-recovery
Version: 005
Responds to: bridge/gtkb-wi5661-terminal-verdict-recovery-004.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5661-SKILL-RENAME-LIVE-BREAK-20260724
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5661

target_paths: ["scripts/gtkb_bridge_writer.py", ".claude/hooks/bridge-axis-2-surface.py", "config/hooks/gtkb-bridge-axis-2-surface.py", "scripts/per_thread_finalization_repair.py", "scripts/harness_parity_phase2.py", "scripts/verify_antigravity_dispatch.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/scripts/test_bridge_axis_2_surface.py", "platform_tests/scripts/test_per_thread_finalization_repair.py", "platform_tests/scripts/test_harness_parity_phase2.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py"]

implementation_scope: source | tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Recover all six original live skill-rename breaks only after the separately
reviewed hunk-provenance reconciliation establishes a clean attributable
baseline. This proposal preserves the false terminal chain by reference and
does not authorize source mutation until its reconciliation prerequisite is
terminally completed.

## Claim

Prime Builder proposes the eventual six-finding source/test repair, not a
reconciliation bypass. No target listed here may be edited, staged, or
attributed until the dependency below has a helper-backed terminal audit
commit, a fresh LO GO on this version, and a new implementation claim.

## Requirement Sufficiency

Existing requirements sufficient. The exact WI-5661 PAUTH, the governing
bridge/testing constraints, DELIB-20260724-WI5661-PROCESS-AUTHORIZATION, and
DELIB-202667193 govern the later bounded repair. No new owner decision is
requested for this revision.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001

## Mandatory Ordered Reconciliation Dependency

- Dependency bridge: bridge/gtkb-wi5661-hunk-provenance-reconciliation-001.md
- Scope: predecessor live-breaks -003/-004, the six dirty/untracked source
  paths, and the dirty bridge-writer test path.
- Completion predicate: an independent LO helper-backed VERIFIED artifact and
  commit must identify every hunk as owned by a governed slice, restored under
  its own authority, or retained in an explicit quarantine. It must preserve
  the untracked false terminal artifacts without staging them and establish a
  clean, attributable baseline for every target in this proposal.
- Ordering: until that predicate is met, this proposal is non-implementable.
  A future LO review may not issue a source GO merely because this proposal
  names a technical solution.

## Predecessor Preservation

- bridge/gtkb-wi5661-skill-rename-live-breaks-003.md and -004.md are
  untracked predecessor evidence. They remain quarantined, are never terminal
  proof, and are never staging input for this source recovery.
- The original live-breaks claim is expired. No present dirty byte is inferred
  to be WI-5661-owned from that expired claim.

## Proposed Implementation After Dependency And GO

- scripts/gtkb_bridge_writer.py resolves the live gtkb-verify finalizer and
  preserves status-first verdict bodies while adding attested author metadata.
  Unrelated responder-routing hunks are excluded.
- Both AXIS-2 hook copies load only
  .claude/skills/gtkb-bridge/helpers/scan_bridge.py. The legacy split-path
  bridge fallback is removed; no retained compatibility alias is added.
- scripts/per_thread_finalization_repair.py, scripts/harness_parity_phase2.py,
  and scripts/verify_antigravity_dispatch.py use canonical managed skill
  locations and canonical registry fixtures.
- No WI-5640 policy/interpreter rewrite or fixture capture is included.

## Concrete Test Map

| Finding | Test path and selector to add or update | Required assertion |
| --- | --- | --- |
| Provider finalizer and status-first metadata | platform_tests/scripts/test_gtkb_bridge_writer.py::test_provider_publisher_preserves_status_first_and_injects_attested_metadata | A metadata-free LO body beginning NO-GO remains status-first; all trusted author fields are injected; canonical gtkb-verify helper is selected. |
| AXIS-2 source and mirror | platform_tests/scripts/test_bridge_axis_2_surface.py::test_t13_hook_and_config_use_canonical_helper_without_legacy_segmented_fallback | Both copies use the exact canonical direct helper path and no split legacy fallback expression remains. |
| Per-thread finalization import | platform_tests/scripts/test_per_thread_finalization_repair.py::test_wi5661_repair_uses_canonical_gtkb_verify_helper | Candidate evaluation resolves the canonical managed helper. |
| Harness parity registry | platform_tests/scripts/test_harness_parity_phase2.py::test_wi5661_parity_fixture_uses_canonical_registry_filename | Fixture materializes gtkb-harness-capability-registry.toml and the parity report remains stable. |
| Antigravity verdict anchors | platform_tests/scripts/test_verify_antigravity_dispatch.py::test_inspect_verdict_anchor_guard_detects_helper_coverage and ::test_evaluate_readiness_reports_verdict_anchor_guard | Both guard paths locate canonical gtkb-verify helpers. |

After implementation, run the five declared test modules, Ruff check/format on
all declared Python sources/tests, bridge applicability and ADR/DCL preflights,
and a scoped diff check. The implementation report must record the immutable
commit and no deferred original finding.

## Acceptance Criteria

- The reconciliation dependency is terminally completed before source mutation.
- All six original live breaks are repaired with the mapped selectors; none is
  deferred.
- The two AXIS-2 copies use canonical-only helper paths and the segmented
  legacy fallback cannot return.
- The source/test commit contains no unrelated bridge routing or foreign dirty
  hunk.
- Independent LO finalization is helper-mediated and includes Commit
  Finalization Evidence.

## Cross-Harness Disposition

Claude gets coupled canonical AXIS-2 source/mirror behavior; Codex and other
providers retain status-first governed verdict publication; Antigravity gets
canonical verdict-anchor discovery. No generated adapter or runtime scratch
surface is changed outside the declared paths.

## Risks And Rollback

The primary risk is false ownership of pre-existing dirty bytes. The terminal
reconciliation dependency fails closed first. Rollback is a separate governed
revert of the later clean source/test commit; predecessor bridge evidence
remains append-only and quarantined.

## Owner Decisions / Input

- DELIB-20260724-WI5661-PROCESS-AUTHORIZATION retains review, claim, and
  finalization gates.
- DELIB-202667193 retains per-slice GO and VERIFIED gates for the skill-rename
  sweep.

## Recommended Commit Type

fix

