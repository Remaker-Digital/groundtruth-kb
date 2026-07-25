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


# Provenance-Valid Configuration Baseline Capture — WI-5664

bridge_kind: prime_proposal
Document: gtkb-wi5664-provenance-valid-config-baseline-capture
Version: 001
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5664

target_paths: ["config/agent-control/gtkb-auto-finalization-sweep.md", "config/agent-control/gtkb-review-gate.md", "config/agent-control/gtkb-file-bridge-protocol.md", "config/agent-control/gtkb-loyal-opposition.md", "config/agent-control/gtkb-command-surface.toml"]

## Claim

The prior gtkb-wi5664-config-baseline-recovery chain is terminally VERIFIED
only as a correct NO-ACTION: its v001 author provenance was unreadable before
any file mutation. This new chain carries the same observed five configuration
baseline inputs with fresh PB provenance. After independent GO and a successful
packet, it may stage and commit only these exact bytes. It does not repair
stale references, choose a synchronization direction, or reuse the historical
GO as authority.

## Requirement Sufficiency

Existing requirements sufficient. WI-5664 and DELIB-202667193 authorize this
bounded configuration slice; the fresh chain repairs authority provenance only.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

## Prior Deliberations

- DELIB-202667193 — independent GO, claim, implementation-start, and terminal
  verification remain mandatory for sweep slices.
- bridge/gtkb-wi5664-config-baseline-recovery-003.md — required a fresh
  provenance-valid proposal rather than an historical metadata rewrite.
- bridge/gtkb-wi5664-config-baseline-recovery-004.md — VERIFIED only the
  predecessor NO-ACTION and directed this exact recovery path.

## Owner Decisions / Input

No new owner decision is required. These files are capture candidates only;
this proposal does not authorize projection or package synchronization.

## Ownership And Hash Matrix

| Capture input | Authority/mirror relation | SHA-256 |
| --- | --- | --- |
| config/agent-control/gtkb-auto-finalization-sweep.md | canonical rule; one-way projection to .claude/rules/auto-finalization-sweep.md | 00bf3e301056b03e2f8f29e9db9883271706431789292590bee29a51d7214b21 |
| config/agent-control/gtkb-review-gate.md | canonical rule; one-way projection to .claude/rules/codex-review-gate.md | e71113033c49833aaa99b3b8199d0de36fa0c67f6b2ea07e6470fa2fe821bed1 |
| config/agent-control/gtkb-file-bridge-protocol.md | canonical rule; one-way projection to .claude/rules/file-bridge-protocol.md | b336537a026eae4339c7c2ae36ffce7d4b0787658a394d4c8884f39e93695f7d |
| config/agent-control/gtkb-loyal-opposition.md | canonical rule; one-way projection to .claude/rules/loyal-opposition.md | 82100953a26a5be9d232bc3732da45589a83b0185c30436378f22afe752aff60 |
| config/agent-control/gtkb-command-surface.toml | renamed capture of command-surface.toml; package mirror is groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/command-surface.toml | 51c195520d03b37474759676f0b1f676f60c992f17683221dfc0d29228c27b35 |

All hashes were recomputed at filing. Rule projections are not authorities.
The command-surface equality check is an acceptance precondition, not permission
to synchronize a mismatch.

## Implementation And Verification Plan

1. After independent GO, acquire the matching claim and issue
   implementation_authorization.py begin. Stop before staging if the packet,
   hash matrix, or projection/package assertion fails.
2. Recompute all five hashes, run generate_rule_compatibility_projections.py
   --check, the focused projection and command-surface tests, and git diff
   --check for exactly these five paths.
3. Confirm the staged path set is exactly the five declared inputs, commit only
   that packet-authorized set, and file a committed implementation report for
   independent LO review.

## Specification-Derived Verification Mapping

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Bridge authority | Fresh PB proposal, independent GO, claim, packet | No untracked baseline byte is staged early. |
| Baseline integrity | Five SHA-256 checks | Each candidate matches the observed matrix exactly. |
| Projection discipline | compatibility check and focused tests | Projection mismatch fails closed without synchronization. |
| Scope isolation | cached path list and diff check | Only the five inputs enter the commit. |

## Acceptance Criteria

- Only the five declared baseline inputs are committed and byte-match the matrix.
- Projection check and focused test suite pass without output mutation.
- A matrix mismatch fails closed and routes synchronization separately.
- Stale skill-reference repair remains a later independently reviewed proposal.

## Risks And Rollback

Capturing unknown untracked bytes could canonize the wrong direction. Exact
hashes, ownership assertions, and pre-commit checks fail closed. Any rollback is
a separate governed five-file revert and never rewrites historical bridge files.

## Recommended Commit Type

chore
