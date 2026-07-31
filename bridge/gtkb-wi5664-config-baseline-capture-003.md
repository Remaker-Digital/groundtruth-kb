REVISED
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T14-47-11Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal — WI-5664 explicit configuration ownership baseline

bridge_kind: prime_proposal
Document: gtkb-wi5664-config-baseline-capture
Version: 003
Responds to: bridge/gtkb-wi5664-config-baseline-capture-002.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5664

target_paths: ["config/agent-control/gtkb-auto-finalization-sweep.md", "config/agent-control/gtkb-review-gate.md", "config/agent-control/gtkb-file-bridge-protocol.md", "config/agent-control/gtkb-loyal-opposition.md", "config/agent-control/gtkb-command-surface.toml"]

implementation_scope: configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Capture exactly five currently untracked configuration inputs without changing
their reference content. This revision records the authority, projection or
package relation, and observed SHA-256 for every input before any future
skill-reference repair is considered.

## Claim

Prime Builder proposes a baseline-only transaction. No skill reference,
projection generator, package snapshot, or test is edited in this slice. A
mismatch against the declared ownership matrix fails closed rather than being
silently synchronized.

## Requirement Sufficiency

Existing requirements sufficient. WI-5664, the active project authorization,
the WI-5640 rule-projection policy, and the observed tracked sources establish
the bounded capture contract. No owner decision is required before review.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

## Ownership And Parity Matrix

| Captured path | Authority and direction | Synchronized projection/package mirror | Current SHA-256 | Parity proof and mismatch disposition |
| --- | --- | --- | --- | --- |
| config/agent-control/gtkb-auto-finalization-sweep.md | Canonical rule authority; generator renders it one-way to .claude/rules/auto-finalization-sweep.md | .claude/rules/auto-finalization-sweep.md; no package snapshot | 00bf3e301056b03e2f8f29e9db9883271706431789292590bee29a51d7214b21 | Get-FileHash equality plus python scripts/generate_rule_compatibility_projections.py --check; mismatch blocks capture. |
| config/agent-control/gtkb-review-gate.md | Canonical rule authority; one-way projection | .claude/rules/codex-review-gate.md; no package snapshot | e71113033c49833aaa99b3b8199d0de36fa0c67f6b2ea07e6470fa2fe821bed1 | Same check; mismatch blocks capture. |
| config/agent-control/gtkb-file-bridge-protocol.md | Canonical rule authority; one-way projection | .claude/rules/file-bridge-protocol.md; scaffold template is independent and excluded, not a synchronized package mirror | b336537a026eae4339c7c2ae36ffce7d4b0787658a394d4c8884f39e93695f7d | Same check; mismatch blocks capture. |
| config/agent-control/gtkb-loyal-opposition.md | Canonical rule authority; one-way projection | .claude/rules/loyal-opposition.md; scaffold template is independent and excluded, not a synchronized package mirror | 82100953a26a5be9d232bc3732da45589a83b0185c30436378f22afe752aff60 | Same check; mismatch blocks capture. |
| config/agent-control/gtkb-command-surface.toml | Renamed capture of the existing tracked config/agent-control/command-surface.toml authority; it is not a rule projection | config/agent-control/command-surface.toml and groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/command-surface.toml | 51c195520d03b37474759676f0b1f676f60c992f17683221dfc0d29228c27b35 | Three-way Get-FileHash equality and command-surface tests; any mismatch fails closed and requires a separately scoped source/mirror decision. |

The four .claude/rules files are projections, not authorities: the projection
generator explicitly reads canonical config inputs and never reads a retained
projection as authority. This capture does not mutate either side.

## Exact Verification Evidence

Observed before proposal filing:

    python scripts/generate_rule_compatibility_projections.py --check
    Rule compatibility projections: PASS (38 projections current)

    groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_generate_rule_compatibility_projections.py platform_tests/scripts/test_command_surface_disposition.py -q --tb=short
    14 passed, 1 warning

The known aggregate package-snapshot suite is intentionally not used as
acceptance evidence because it has an unrelated baseline failure. No new test
is necessary for this capture-only slice: the declared existing tests exercise
the actual projection renderer, drift check, canonical override behavior, and
command-surface loader/disposition contract.

## Specification-Derived Verification Plan

    python scripts/generate_rule_compatibility_projections.py --check
    groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_generate_rule_compatibility_projections.py platform_tests/scripts/test_command_surface_disposition.py -q --tb=short
    python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5664-config-baseline-capture
    python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5664-config-baseline-capture
    git diff --check -- config/agent-control/gtkb-auto-finalization-sweep.md config/agent-control/gtkb-review-gate.md config/agent-control/gtkb-file-bridge-protocol.md config/agent-control/gtkb-loyal-opposition.md config/agent-control/gtkb-command-surface.toml

## Acceptance Criteria

- Only the five declared untracked inputs are introduced in the later
  implementation commit; their bytes equal the matrix fingerprints.
- The projection check passes without regenerating any output.
- The two declared test modules pass; the known unrelated aggregate baseline
  failure is neither hidden nor attributed to WI-5664.
- Any source/projection/package mismatch fails closed and is deferred to a
  later, independently reviewed correction proposal.

## Risks And Rollback

Capturing unknown bytes could canonize the wrong direction. The explicit matrix
prevents that for rule projections and preserves command-surface ambiguity as a
hard stop. Rollback is a separate governed revert of only the baseline commit.

## Owner Decisions / Input

No additional owner input is required. This revised baseline is prerequisite
evidence, not approval to repair the stale references.

## Recommended Commit Type

chore

