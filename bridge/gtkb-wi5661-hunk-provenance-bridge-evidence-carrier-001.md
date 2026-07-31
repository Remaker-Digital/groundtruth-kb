NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata


# Hunk-Provenance Bridge Evidence Carrier — WI-5661

bridge_kind: prime_proposal
Document: gtkb-wi5661-hunk-provenance-bridge-evidence-carrier
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5661-SKILL-RENAME-LIVE-BREAK-20260724
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5661

target_paths: ["bridge/gtkb-wi5661-hunk-provenance-bridge-evidence-carrier-003.md"]

## Claim

The historical `gtkb-wi5661-hunk-provenance-reconciliation` chain is
non-dispatchable: its original PB author role is unreadable and its sole
prospective report path is classified as documentation, outside the active
WI-5661 PAUTH. This carrier creates no source authority. After independent GO,
it may create exactly one bridge-native evidence report, an allowed `bridge`
mutation, which classifies the observed dirty hunks without staging or changing
them.

## Requirement Sufficiency

Existing requirements sufficient. The owner-directed WI-5661 fast-lane scope,
active PAUTH, and prior NO-GO findings define this report-only prerequisite; a
separate proposal remains required for any live-break source repair.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-20260724-WI5661-PROCESS-AUTHORIZATION` — permits the bounded WI-5661 recovery sequence but not a bridge bypass.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — keeps independent GO and evidence gates in the fast lane.

## Owner Decisions / Input

No new owner decision is needed. This corrects only the carrier's provenance
and PAUTH classification, without expanding the approved WI-5661 scope.

## Read-Only Observed Evidence

The future report may inspect but must not list as target, stage, modify,
reformat, commit, or rollback: `.claude/hooks/bridge-axis-2-surface.py`,
`config/hooks/gtkb-bridge-axis-2-surface.py`, `scripts/gtkb_bridge_writer.py`,
`scripts/harness_parity_phase2.py`, `scripts/per_thread_finalization_repair.py`,
`scripts/verify_antigravity_dispatch.py`, and the related focused test paths.

## Proposed Scope

1. After GO, claim, and a successful implementation-start packet, write only
   `bridge/gtkb-wi5661-hunk-provenance-bridge-evidence-carrier-003.md` as a
   strict `NEW` `implementation_report` with real PB author metadata.
2. Record each observed path's diff fingerprint, hunk count, current bridge or
   owner disposition, and exact prerequisite for a future source proposal.
3. Prove the index contains only the bridge report, and never request terminal
   verification for source work from this evidence-only carrier.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Bridge / PAUTH control | Fresh carrier GO, claim, packet, and target-class decision | Only bridge-native report mutation is authorized. |
| Hunk provenance | `git diff --numstat` and `git diff --check` over each observed path | Durable evidence identifies foreign work without changing it. |
| Scope isolation | `git diff --cached --name-only` before report handoff | Only the declared carrier report is staged. |
| Future repair separation | LO review of the report | No report outcome supplies source authority. |

## Acceptance Criteria

- The fresh carrier has readable PB provenance and an exact PAUTH-allowed
  bridge target.
- Its sole later report classifies observed hunks without source/test/config
  mutation or staging.
- A future source repair still requires its own proposal, GO, packet, and
  independent verification.

## Risks And Rollback

The risk is treating observed changes as approved implementation. The exact
bridge-only target and index check fail closed. A later rollback can affect only
the carrier report, never a foreign source hunk or prior bridge artifact.

## Recommended Commit Type

docs
