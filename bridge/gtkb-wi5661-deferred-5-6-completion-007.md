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

bridge_kind: prime_proposal
Document: gtkb-wi5661-deferred-5-6-completion
Version: 007
Responds to: bridge/gtkb-wi5661-deferred-5-6-completion-006.md
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5661-SKILL-RENAME-LIVE-BREAK-20260724
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5661
target_paths: ["scripts/harness_parity_phase2.py", "scripts/verify_antigravity_dispatch.py", "platform_tests/scripts/test_harness_parity_phase2.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py"]

# WI-5661 Deferred Findings 5–6 — SoT-Corrected Scope

## Revision Disposition

Implementation stopped before staging when a post-GO authority check found
that version 005 incorrectly called
`config/agent-control/gtkb-harness-capability-registry.toml` canonical. The
authoritative SoT registry at `config/registry/sot-artifacts.toml:379-385`
declares the tracked unprefixed
`config/agent-control/harness-capability-registry.toml`. The prefixed file is
currently untracked and cannot become a live runtime dependency through this
WI-5661 slice.

The invalid capability-registry filename changes were removed from the
candidate. No source or test byte was staged or committed. This revision keeps
only the actual managed-skill rename repairs and requests fresh independent
review before any commit.

## Claim

Complete deferred findings 5 and 6 without changing capability-registry
authority. Finding 5 updates only managed-skill path literals in
`_bridge_write_path_status` and its direct `.api-harness/skills/gtkb-bridge`
fixture. Finding 6 updates the Codex/Claude `gtkb-verify` verdict-anchor paths
and their direct fixtures.

## Corrected Scope

- `scripts/harness_parity_phase2.py`: keep
  `CAPABILITY_REGISTRY_PATH = config/agent-control/harness-capability-registry.toml`
  and keep both provider-status evidence strings unprefixed; update only the
  managed bridge/verify skill surface map to `gtkb-*` names.
- `platform_tests/scripts/test_harness_parity_phase2.py`: keep both capability
  registry fixtures/readers unprefixed; update only the API managed-skill
  fixture from `skills/bridge` to `skills/gtkb-bridge`.
- `scripts/verify_antigravity_dispatch.py`: update the two verdict helper
  anchors to `.codex/.claude/skills/gtkb-verify/helpers/write_verdict.py`.
- `platform_tests/scripts/test_verify_antigravity_dispatch.py`: update the
  coupled helper fixtures and assertions to the same two paths.

No registry content, SoT metadata, generated adapter, dispatcher state,
provider runtime, bridge history, or untracked prefixed registry file is in
scope.

## Requirement Sufficiency

Existing requirements are sufficient after this authority correction. The
active singleton PAUTH, WI-5661, SoT registry, and linked bridge/test
requirements define a complete four-path repair.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

- `DELIB-20260724-WI5661-PROCESS-AUTHORIZATION` authorizes governed WI-5661
  completion while retaining every bridge and authorization gate.
- `DELIB-202667193` requires live-break-first processing with per-slice GO and
  VERIFIED.
- No new owner decision is required; this revision narrows an incorrect
  implementation assumption to the existing SoT.

## Prior Deliberations

- `bridge/gtkb-wi5661-deferred-5-6-completion-005.md` — prior four-path
  proposal, now corrected only for capability-registry authority.
- `bridge/gtkb-wi5661-deferred-5-6-completion-006.md` — GO whose registry-path
  premise was invalidated by the SoT registry inspection.
- `DELIB-202667410` and `DELIB-202667418` — fixture completeness and
  foreign-hunk isolation remain applicable.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| SoT registry authority | Inspect `config/registry/sot-artifacts.toml:379-385` and both source/test diffs | Only the unprefixed tracked registry path remains |
| Managed-skill rename | Focused `test_harness_parity_phase2.py` | `gtkb-bridge` surfaces resolve without changing registry authority |
| Verdict anchor repair | Focused `test_verify_antigravity_dispatch.py` | Both `gtkb-verify` anchors are detected |
| Combined contract | Run both focused modules together | 38 tests pass |
| Hunk isolation | Build a mapping-only patch against HEAD and compare cached versus unstaged diffs | Only the corrected literals enter the commit |
| Quality | Ruff check and format-check on the four targets | Pass without absorbing unrelated bytes |

Read-only corrected-candidate evidence before filing: the combined suite
passes `38 passed, 1 warning`; Ruff check passes. The candidate is not staged
or committed and still requires a fresh GO and implementation-start snapshot.

## Acceptance Criteria

- The tracked unprefixed capability registry remains the only runtime/test
  authority used by these four files.
- Managed bridge/verify skill surfaces resolve through `gtkb-*` paths.
- The two focused modules pass together, with no test weakening.
- Only a reviewed mapping-only patch for the four declared paths is committed.

## Risks / Rollback

The primary risk is accidentally coupling a skill-directory rename to an
untracked registry rename. The SoT assertion and explicit negative path check
fail closed. Rollback is a governed revert of only the eventual four-path
commit; bridge history remains append-only.

## Recommended Commit Type

`fix`
