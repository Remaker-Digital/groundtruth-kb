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
Document: gtkb-wi5664-provenance-valid-config-baseline-capture
Version: 003
Responds to: bridge/gtkb-wi5664-provenance-valid-config-baseline-capture-002.md
Date: 2026-07-24 UTC

Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5664
target_paths: ["config/agent-control/gtkb-auto-finalization-sweep.md", "config/agent-control/gtkb-review-gate.md", "config/agent-control/gtkb-file-bridge-protocol.md", "config/agent-control/gtkb-loyal-opposition.md", "config/agent-control/gtkb-command-surface.toml"]

# WI-5664 Configuration Baseline — Exact-Byte EOF Disposition

## Revision Disposition

Implementation stopped before commit because `git diff --cached --check`
reported exactly one diagnostic:

```text
config/agent-control/gtkb-command-surface.toml:151: new blank line at EOF.
```

The candidate was immediately unstaged. All five approved hashes, 38 rule
projections, and 14 focused tests still pass. This revision does not normalize
the byte because the two trailing LF bytes are inherited identically from both
authoritative comparison inputs.

## Claim

Capture the same five exact baseline inputs approved in version 001, with a
narrow explicit disposition for the single inherited EOF diagnostic. The
command-surface candidate, tracked canonical input, and packaged registry
mirror are each 6,910 bytes, end in `20 66 61 6C 73 65 0A 0A`, and have the
same SHA-256:
`51c195520d03b37474759676f0b1f676f60c992f17683221dfc0d29228c27b35`.

Removing one LF would break byte equality and the approved hash. Therefore the
implementation must preserve the exact bytes and treat only that one
path-and-line diagnostic as an inherited baseline exception. Any other
`git diff --check` output remains blocking.

## Requirement Sufficiency

Existing requirements are sufficient with this exact-byte disposition. No
source/configuration semantics or projection direction changes.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

- `DELIB-202667193` remains the owner authorization for this bounded sweep
  slice and its per-slice gates.
- No new owner decision is required; this revision preserves rather than
  changes the three equal baseline copies.

## Prior Deliberations

- `bridge/gtkb-wi5664-provenance-valid-config-baseline-capture-001.md` — exact
  five-file/hash proposal.
- `bridge/gtkb-wi5664-provenance-valid-config-baseline-capture-002.md` — GO and
  independent hash/projection/test confirmation.
- `bridge/gtkb-wi5664-config-baseline-recovery-004.md` — terminal NO-ACTION
  directing this fresh provenance-valid chain.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Baseline integrity | Recompute all five SHA-256 values | Exact version-001 matrix |
| Command-surface equality | Compare size, hash, and tail bytes across candidate, tracked canonical input, and package mirror | All three are identical |
| Projection discipline | `generate_rule_compatibility_projections.py --check` | 38 projections current |
| Focused behavior | Run projection and command-surface modules | 14 tests pass |
| Scoped diff hygiene | Run `git diff --cached --check` after exact staging | Exactly the documented command-surface EOF diagnostic and no other output |
| Scope isolation | Inspect cached path list and commit | Exactly five declared paths |

## Acceptance Criteria

- All five exact hashes remain unchanged from version 001.
- The three command-surface copies remain byte-identical.
- Projection check and 14 focused tests pass without mutation.
- The only allowed diff-check diagnostic is
  `gtkb-command-surface.toml:151: new blank line at EOF`; any additional
  diagnostic fails closed.
- Exactly the five declared inputs enter the commit.

## Risks / Rollback

The narrow exception could conceal unrelated whitespace if matched broadly.
Verification must match the exact path, line, message, length, tail bytes, and
SHA-256 above. Rollback is a separately governed five-file revert; historical
bridge files remain append-only.

## Recommended Commit Type

`chore`
