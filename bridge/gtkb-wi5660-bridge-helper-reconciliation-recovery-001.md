NEW
::init gtkb pb
::open build

# Defect-Fix Proposal - revise_bridge.py hardcodes stale bridge-propose helper path (should be gtkb-bridge-propose)

bridge_kind: prime_proposal
Document: gtkb-wi5660-bridge-helper-reconciliation-recovery
Version: 001
Date: 2026-07-24 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata


Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5660-RECONCILIATION-20260724
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5660

target_paths: [".claude/skills/gtkb-bridge/helpers/revise_bridge.py", ".codex/skills/gtkb-bridge/helpers/revise_bridge.py", ".goose/skills/gtkb-bridge/helpers/revise_bridge.py", "platform_tests/skills/test_bridge_revise_helper.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The live Claude helper contains an uncommitted pre-GO resolver hunk that
prefers the canonical gktb-bridge-propose writer and falls back to the
retired bridge-propose location. The hunk addresses the observed stale path,
but it is not implementation evidence and must not be attributed
retroactively.

The owner has selected reconciliation. This fresh chain will obtain a new
independent GO before changing any protected path, then deliver a complete
four-path parity repair: canonical helper, tracked Codex and Goose helper
adapters, and the focused test module. It preserves the existing hunk as
observed pre-GO baseline evidence until the authorized implementation replaces
or confirms it under the new transaction.

## Defect / Reproduction

1. The canonical, Codex, and Goose revise_bridge helpers historically load
   .claude/skills/bridge-propose/helpers/write_bridge.py.
2. That retired path is absent; the canonical writer is located under
   .claude/skills/gtkb-bridge-propose/helpers/write_bridge.py.
3. The current focused test module also imports the retired
   .claude/skills/bridge/helpers/revise_bridge.py path, so it cannot exercise
   the live helper or the advertised fallback behavior.
4. The pre-GO Claude hunk provides a resolver but leaves Codex and Goose
   adapters stale and omits isolated canonical-preferred and legacy-fallback
   regressions.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/skills/gtkb-bridge/helpers/revise_bridge.py`, `.codex/skills/gtkb-bridge/helpers/revise_bridge.py`, `.goose/skills/gtkb-bridge/helpers/revise_bridge.py`, `platform_tests/skills/test_bridge_revise_helper.py`.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - forbids retrospective authorization and
  requires a fresh GO, claim, implementation-start packet, and LO terminal
  verification before any source adoption.
- DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001 - requires equivalent working
  Codex and Goose helper behavior or a typed owner waiver; this proposal
  selects the parity-complete route.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 and
  DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - require the concrete
  governing links and PAUTH/project/WI metadata.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - requires isolated
  resolver behavior tests, adapter evidence, and focused execution.
- GOV-STANDING-BACKLOG-001 - makes WI-5660 the authoritative defect unit.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001,
  ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, and
  DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - require durable owner decision,
  provenance, implementation, report, and verification artifacts.

## Prior Deliberations

- `DELIB-20260724-WI5660-RECONCILIATION-AUTHORIZATION` - owner selects
  the fresh, parity-complete reconciliation path and rejects retroactive GO.
- `bridge/gtkb-wi5660-revise-bridge-helper-path-002.md` and
  `bridge/gtkb-wi5660-revise-bridge-propose-path-002.md` - independent
  NO-GO evidence identifying the pre-GO baseline, parity, formatting, and
  test-coverage defects this new thread must resolve.
- `DELIB-202667409` - Loyal Opposition Review — WI-5660 revise_bridge helper path repair
- `DELIB-202666962` - Loyal Opposition Corrected Verdict (review_no_action) - GO - WI-5337 Latest NO-GO Draft Claim State
- `DELIB-202665676` - Loyal Opposition Verdict -- NO-GO (scope-change revision accepted in principle; implementation still blocked)
- `DELIB-202666320` - Loyal Opposition Verdict - NO-GO (finalization-scoped) - WI-5113 Suppress Git console windows in VERIFIED finalization

## Owner Decisions / Input

- `DELIB-20260724-WI5660-RECONCILIATION-AUTHORIZATION` records the owner
  reconciliation decision in this session.
- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5660-RECONCILIATION-20260724`
  is active, includes only WI-5660 and the source/generated-adapter/test
  classes, and expressly forbids retroactive GO.

## Proposed Scope

1. After fresh GO and implementation-start, replace or confirm the observed
   Claude helper hunk as a new governed change. The resolver must prefer
   gktb-bridge-propose and select bridge-propose only when the canonical
   writer is absent; it must otherwise return the canonical expected path for
   its existing error behavior.
2. Regenerate or update only the tracked Codex and Goose helper adapters from
   the canonical repair. If the canonical generation path produces any path
   outside this four-path scope, stop, unstage, and request a revised proposal
   rather than hand-edit or absorb extra outputs.
3. Correct the focused test loader to the canonical gktb-bridge helper and
   add isolated temporary-root tests proving canonical preference, legacy
   fallback, and missing-both deterministic failure. Add adapter checks that
   no tracked helper resolves the absent bare bridge-propose writer.
4. Preserve the current hunk as pre-GO observation until new implementation
   evidence exists. Do not stage, format, commit, or call it authorized before
   the current claim and implementation-start packet.
5. The stale Codex SKILL prose pointer is excluded from this four-path
   helper-runtime repair and remains for its separately sequenced adapter
   regeneration work; it cannot be used to waive helper parity.

## Requirement Sufficiency

Existing requirements sufficient. WI-5660, the two NO-GO findings,
DELIB-20260724-WI5660-RECONCILIATION-AUTHORIZATION, and the active PAUTH
define the required reconciliation, parity, and verification behavior. No new
or revised requirement is needed before implementation.

## Cross-Harness Disposition

- Claude: the canonical helper is the source of behavior and is repaired only
  under fresh GO and implementation-start authorization.
- Codex: the tracked gktb-bridge helper adapter receives the same resolver
  behavior through the canonical generation path or an exact scoped output.
- Goose: the tracked gktb-bridge helper adapter receives the same resolver
  behavior through the canonical generation path or an exact scoped output.
- Cursor, Antigravity, API harness, Ollama, and OpenRouter: no tracked
  revise_bridge helper target is declared for this capability. No behavioral
  waiver is claimed; the scoped parity assertion applies to the three
  declared helper implementations only.

## Bridge Filing

This is the next numbered, versioned file for a fresh recovery thread at
bridge/gtkb-wi5660-bridge-helper-reconciliation-recovery-001.md. It is
append-only and does not alter the previous NO-GO chains or their files.


## Specification-Derived Verification Plan

| Requirement / property | Verification | Expected result |
| --- | --- | --- |
| Canonical resolver | Focused test uses a temporary root containing both writers | gktb-bridge-propose wins |
| Legacy compatibility | Focused test removes canonical writer but provides bridge-propose | legacy writer is selected only then |
| Missing writers | Focused test provides neither writer | canonical expected path is returned and normal load failure remains explicit |
| Cross-harness helper parity | Import or inspect all three tracked helpers after canonical generation | none resolves the absent bare writer when canonical exists |
| Live test loader | python -m pytest platform_tests/skills/test_bridge_revise_helper.py -q | Pass |
| Managed-adapter check | Canonical adapter generator plus exact git diff --name-only scope check | only the two declared adapter helper files are generated |
| Quality | python -m ruff check and python -m ruff format --check on the four targets | Pass |
| Hygiene | git diff --check, bridge applicability preflight, and ADR/DCL clause preflight | Pass with no blocking gaps |

## Acceptance Criteria

1. No bridge-revision helper uses the absent bare bridge-propose writer when
   the canonical gtkb-bridge-propose writer exists.
2. The canonical helper, tracked Codex adapter, and tracked Goose adapter
   provide the same canonical-preferred resolver behavior.
3. The focused test imports the live canonical helper and proves both
   canonical and legacy branches in isolation.
4. The pre-GO hunk is not treated as retroactively authorized; the final
   implementation has a fresh GO, claim, packet, commit, report, and LO
   verification chain.
5. Only the declared four paths change; generator spillover, unrelated dirty
   files, and historical bridge artifacts remain excluded.

## Risks / Rollback

The main risk is accidentally committing the observed pre-GO hunk as if it
were already approved. The current hunk is baseline evidence only; the new
claim and implementation packet must precede every changed-file stage.
Another risk is adapter-generation spillover or a missing full-skill document
repair; the scoped generator check must stop on extra paths, and the excluded
Codex SKILL prose pointer remains separately sequenced rather than silently
waived.

Rollback is a single exact four-path revert after an implementation commit.
Never rewrite preceding bridge files, the owner decision, or unrelated
worktree changes.

## Files Expected To Change

- `.claude/skills/gtkb-bridge/helpers/revise_bridge.py`
- `.codex/skills/gtkb-bridge/helpers/revise_bridge.py`
- `.goose/skills/gtkb-bridge/helpers/revise_bridge.py`
- `platform_tests/skills/test_bridge_revise_helper.py`

## Recommended Commit Type

`fix`
