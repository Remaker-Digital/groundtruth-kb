REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# WI-5660 Bridge Revision Helper Reconciliation — Corrected Authorization

bridge_kind: prime_proposal
Document: gtkb-wi5660-bridge-helper-reconciliation-recovery
Version: 005
Responds to: bridge/gtkb-wi5660-bridge-helper-reconciliation-recovery-004.md
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5660-RECONCILIATION-20260724
Project Authorization Version: 2
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5660

target_paths: [".claude/skills/gtkb-bridge/helpers/revise_bridge.py", ".codex/skills/gtkb-bridge/helpers/revise_bridge.py", ".goose/skills/gtkb-bridge/helpers/revise_bridge.py", "platform_tests/skills/test_bridge_revise_helper.py"]

## Revision Claim

The governed PAUTH has been revised in place to version 2 using only registered
operation-time vocabulary. It now permits `configuration` and `test`, which
classify all four declared targets, and replaces the invalid forbidden labels
with registered prohibitions. This proposal therefore restores an executable
authorization path without broadening the owner-selected four-path outcome.

No protected implementation has begun. The existing unstaged Claude helper
hunk remains pre-GO observed evidence and is not retroactively attributed.
Codex, Goose, and the focused test remain clean at proposal time. A fresh
independent GO, current claim, and successful implementation-start packet are
still mandatory before any target mutation or staging.

## Findings Addressed

### P1 — Unregistered authorization vocabulary

PAUTH v1 permitted the unregistered mutation labels `generated_adapter` and
`test_addition` and forbade the unregistered operation labels `retroactive_go`
and `unrelated_worktree_changes`. PAUTH v2 permits only registered
`configuration` and `test` classes. It forbids only registered
`credential_lifecycle`, `destructive_cleanup`, `dispatcher_mutation`,
`external_system_mutation`, `git_history_rewrite`, `git_push`,
`production_deployment`, and `release` operations.

### P1 — Target classification gap

The canonical, Codex, and Goose managed-skill helper targets classify as
`configuration`; the focused regression module classifies as `test`. Both are
now explicitly permitted. The PAUTH remains limited to WI-5660 and the exact
four paths declared above.

## Requirement Sufficiency

Existing requirements are sufficient. The owner decision
`DELIB-20260724-WI5660-RECONCILIATION-AUTHORIZATION` already selects a fresh,
parity-complete reconciliation and rejects retroactive attribution. Version 004
explicitly states that no new owner decision is required; the correction is an
append-only authorization vocabulary repair under that same decision.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001
- DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-STANDING-BACKLOG-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

## Prior Deliberations

- `DELIB-20260724-WI5660-RECONCILIATION-AUTHORIZATION` — owner selects
  the fresh four-path parity reconciliation and rejects retroactive GO.
- Versions 003 and 004 — preserve the operation-time denial and independently
  identify every invalid vocabulary and classification defect corrected here.
- `WI-5311` — separately tracks the systemic authorization-taxonomy creation
  defect; this bounded record correction does not claim that control-plane
  defect is resolved.

## Owner Decisions / Input

No new owner decision is required. PAUTH v2 implements the existing owner
decision using registered vocabulary and retains all substantive boundaries.

## Proposed Scope

1. After fresh GO, claim, and a successful implementation-start packet, repair
   the canonical resolver so it prefers
   `.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py`, uses the
   legacy `.claude/skills/bridge-propose/helpers/write_bridge.py` only when the
   canonical writer is absent, and otherwise returns the canonical expected
   path so the existing explicit load failure remains deterministic.
2. Regenerate or exactly project the same resolver behavior to only the
   tracked Codex and Goose helper adapters. If the canonical generator emits
   any path outside this four-path scope, stop without staging spillover.
3. Correct the focused test loader to the live canonical gtkb-bridge helper and
   add isolated temporary-root tests for canonical preference, legacy fallback,
   missing-both behavior, and cross-harness helper parity.
4. Preserve all unrelated dirty worktree content, bridge history, generated
   surfaces, and the pre-existing staged WI-5661 evidence carrier.

## Cross-Harness Disposition

- Claude is the canonical helper behavior source.
- Codex and Goose receive matching tracked helper projections.
- Cursor, Antigravity, API harness, Ollama, and OpenRouter have no declared
  tracked `revise_bridge.py` target in this slice; no unmanaged surface is
  created or changed.

## Pre-Filing Preflight Subsection

The governed revision helper must run applicability and mandatory ADR/DCL
clause preflights against this completed candidate. Filing is prohibited on
any missing required spec or blocking clause gap.

## Implementation And Verification Plan

1. Re-read PAUTH v2, acquire a fresh claim, and run
   `scripts/implementation_authorization.py begin` for this exact thread.
   Require `authorized: true` before any protected effect.
2. Preserve the four target preimages and isolate the implementation from all
   foreign hunks. Stage exactly the declared four-path transaction.
3. Run
   `python -m pytest platform_tests/skills/test_bridge_revise_helper.py -q --tb=short -pno:cacheprovider`.
4. Run Ruff check and format-check on the four targets, `git diff --check`,
   and an exact staged-path assertion.
5. Commit only the governed slice, then file an implementation report with
   commit-finalization evidence for independent terminal review.

## Specification-Derived Verification Mapping

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Operation-time authorization | PAUTH v2 show plus fresh begin packet | Registered classes only; `authorized: true`. |
| Canonical resolver | Temporary root containing both writers | gtkb-bridge-propose writer wins. |
| Legacy compatibility | Canonical absent, legacy present | Legacy writer is selected only then. |
| Missing writers | Neither writer present | Canonical expected path is returned and load failure remains explicit. |
| Cross-harness parity | Inspect/import all three tracked helpers | Equivalent resolver behavior in Claude, Codex, and Goose. |
| Focused regression | Focused pytest command | Pass. |
| Scope isolation | Cached path list and diff checks | Exactly four authorized paths; no foreign hunk. |

## Acceptance Criteria

- A fresh implementation-start packet reports `authorized: true` against
  PAUTH version 2 before any protected implementation effect.
- No helper resolves the absent bare writer when the canonical writer exists.
- Claude, Codex, and Goose provide matching resolver behavior.
- The focused tests prove canonical, fallback, missing-both, and parity cases.
- Only the exact four declared paths are committed; the observed pre-GO hunk
  is adopted only as a new governed implementation after GO and packet.
- Independent LO verification, not this proposal, determines VERIFIED.

## Scope Changes

No implementation path or behavioral scope changes from version 001. This
revision only records PAUTH version 2, corrects the canonical `gtkb-` spelling,
and makes the operation-time gate and classification evidence explicit.

## Risk And Rollback

The principal risks are retroactively absorbing the observed canonical hunk or
accepting generator spillover. Fresh authorization, exact preimage/path checks,
and scoped staging fail closed on either condition. Rollback is a separately
governed exact four-path revert; bridge history and unrelated worktree content
are never rewritten.

## Recommended Commit Type

fix
