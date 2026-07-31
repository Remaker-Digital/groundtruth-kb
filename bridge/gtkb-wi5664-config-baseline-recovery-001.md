NEW
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default;thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata


# Implementation Proposal — WI-5664 provenance-valid configuration baseline recovery

bridge_kind: prime_proposal
Document: gtkb-wi5664-config-baseline-recovery
Version: 001
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5664

target_paths: ["config/agent-control/gtkb-auto-finalization-sweep.md", "config/agent-control/gtkb-review-gate.md", "config/agent-control/gtkb-file-bridge-protocol.md", "config/agent-control/gtkb-loyal-opposition.md", "config/agent-control/gtkb-command-surface.toml"]

implementation_scope: configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Create a fresh authorization chain to capture exactly five known untracked
configuration baseline inputs. The predecessor capture chain is immutable
historical evidence but cannot issue an implementation packet because its v001
Prime Builder author-role metadata is unreadable. This proposal does not
rewrite that chain or repair stale references.

## Claim

After an independent recovery GO and successful packet for this slug, Prime
Builder will stage and commit only the five files at the hash values recorded
below. Any byte drift, projection/package mismatch, expanded staged set, or
failed check aborts the capture. No projection, package snapshot, source rule,
or test mutation is authorized.

## Requirement Sufficiency

Existing requirements sufficient. WI-5664 and `DELIB-202667193` authorize the
bounded skill-rename sweep; the separate recovery chain is necessary only to
restore valid implementation-start provenance for the baseline capture.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202667193` — bounded sweep slices retain independent GO, claim,
  implementation-start, and VERIFIED gates.
- `DELIB-20260724-WI5661-PROCESS-AUTHORIZATION` — lifecycle processing remains
  mandatory for WI-5664.
- `bridge/gtkb-wi5664-config-baseline-capture-006.md` — requires this fresh
  append-only recovery rather than any historical metadata rewrite.

## Owner Decisions / Input

No new owner decision is required. The five bytes are capture candidates only;
this proposal does not choose a source/projection synchronization direction.

## Ownership And Hash Matrix

| Capture input | Authority/mirror relation | SHA-256 |
| --- | --- | --- |
| `config/agent-control/gtkb-auto-finalization-sweep.md` | canonical rule; one-way projection to `.claude/rules/auto-finalization-sweep.md` | `00bf3e301056b03e2f8f29e9db9883271706431789292590bee29a51d7214b21` |
| `config/agent-control/gtkb-review-gate.md` | canonical rule; one-way projection to `.claude/rules/codex-review-gate.md` | `e71113033c49833aaa99b3b8199d0de36fa0c67f6b2ea07e6470fa2fe821bed1` |
| `config/agent-control/gtkb-file-bridge-protocol.md` | canonical rule; one-way projection to `.claude/rules/file-bridge-protocol.md` | `b336537a026eae4339c7c2ae36ffce7d4b0787658a394d4c8884f39e93695f7d` |
| `config/agent-control/gtkb-loyal-opposition.md` | canonical rule; one-way projection to `.claude/rules/loyal-opposition.md` | `82100953a26a5be9d232bc3732da45589a83b0185c30436378f22afe752aff60` |
| `config/agent-control/gtkb-command-surface.toml` | renamed capture of `config/agent-control/command-surface.toml`; package mirror is `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/command-surface.toml` | `51c195520d03b37474759676f0b1f676f60c992f17683221dfc0d29228c27b35` |

Rule projections are not authorities. The command-surface three-way equality is
an acceptance precondition, not permission to synchronize any mismatch.

## Implementation And Verification Plan

1. Acquire a recovery claim and run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5664-config-baseline-recovery`; stop if no current packet issues.
2. Recompute the five SHA-256 values and verify all projection/package equality claims in the matrix.
3. Run `python scripts/generate_rule_compatibility_projections.py --check` and:

```text
python -m pytest platform_tests/scripts/test_generate_rule_compatibility_projections.py platform_tests/scripts/test_command_surface_disposition.py -q --tb=short
```

4. Run `git diff --check` for the exact five paths, both bridge preflights, and
   verify the staged set contains no extra path.
5. Commit only the five packet-authorized inputs; then file a committed
   implementation report for independent LO review.

The known aggregate package-snapshot failure remains out of scope and is not
used as acceptance evidence.

## Pre-Filing Preflight

- `python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/wi5664-baseline-recovery-001.md` passed with packet hash `sha256:4dc852a976c57e82cd6de55457f25786542f42089939016b7544dded2b39e971`, no missing required/advisory specifications, and no blocking errors.
- `python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/wi5664-baseline-recovery-001.md` passed: three must-apply clauses, zero evidence gaps, and zero blocking gaps.

## Specification-Derived Verification Mapping

| Requirement | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Fresh GO, host-bound claim, successful packet, and exact five-file protected commit. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Recovery proposal/report applicability and mandatory clause preflights. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Projection check, targeted 14-test suite, SHA-256 matrix, and scoped diff check. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Exact observed five-file baseline and commit preserve prior untracked content as explicit governed evidence. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | No terminal claim until the five-file commit and independent LO review exist. |

## Acceptance Criteria

- Only the five declared baseline inputs are committed and byte-match the matrix.
- Rule projection check and the named targeted test suite pass without output mutation.
- A matrix mismatch fails closed and routes future synchronization separately.
- Stale skill-reference repair remains a later, independently reviewed proposal.

## Risks And Rollback

Capturing unknown untracked bytes can canonize the wrong direction. Exact hashes,
the ownership matrix, and pre-commit checks make that fail closed. A later
rollback is a separate governed revert limited to the baseline commit; it never
rewrites historical bridge evidence.

## Recommended Commit Type

chore
