REVISED
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T13-26-04Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata


# Implementation Proposal Revision — WI-5664 canonical rules and command-surface skill references

bridge_kind: prime_proposal
Document: gtkb-wi5664-rules-config-skill-reference-repair
Version: 003
Date: 2026-07-24 UTC
Responds to: bridge/gtkb-wi5664-rules-config-skill-reference-repair-002.md

Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5664

target_paths: ["config/agent-control/gtkb-auto-finalization-sweep.md", ".claude/rules/auto-finalization-sweep.md", "config/agent-control/gtkb-review-gate.md", ".claude/rules/codex-review-gate.md", "config/agent-control/gtkb-file-bridge-protocol.md", ".claude/rules/file-bridge-protocol.md", "config/agent-control/gtkb-loyal-opposition.md", ".claude/rules/loyal-opposition.md", "config/agent-control/command-surface.toml", "config/agent-control/gtkb-command-surface.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/command-surface.toml", "groundtruth-kb/tests/test_context_manifest.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# Bridge Revision Draft - gtkb-wi5664-rules-config-skill-reference-repair

intended_live_path: `bridge/gtkb-wi5664-rules-config-skill-reference-repair-003.md`
responds_to: `bridge/gtkb-wi5664-rules-config-skill-reference-repair-002.md`

## Revision Claim

This revision answers the `002` P1 finding by reducing WI-5664 to the twelve
authoritative source, generated-projection, package-snapshot, and focused-test
paths that actually contain a bare pre-rename skill-directory reference. It
classifies every target and names the generator or synchronization route that
owns its parity. No policy, command semantics, or bridge lifecycle behavior is
changed: each correction only adds the `gtkb-` prefix to a renamed skill path.

## Requirement Sufficiency

Existing requirements are sufficient. `WI-5664`, its active PAUTH, the
file-reference migration ledger, the generated-rule policy, and the governing
specifications below define the complete repair and verification boundary. This
revision does not request a new requirement or mutate formal artifacts.

## In-Root Placement Evidence

Every declared target is under `E:\GT-KB`. The packaged registry target is a
GT-KB platform resource inside this checkout, not an external adopter or
Agent Red dependency.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — preserves role-correct proposal filing and
  the live-GO implementation boundary.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — retain the governed lifecycle for
  the bounded backlog artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — supplies concrete
  governing requirements and spec-derived tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the focused
  regeneration and snapshot-parity evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — binds this revision to
  `GTKB-SKILL-RENAME-REFERENCE-SWEEP`, `WI-5664`, and its active PAUTH.
- `GOV-STANDING-BACKLOG-001` and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — keep the standing-backlog work-item
  boundary intact.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — limits the slice to the GT-KB
  platform, not an adopter application.

## Prior Deliberations

- `DELIB-20260724-WI5661-PROCESS-AUTHORIZATION` — records owner authorization
  for the governed skill-rename repair workflow and the manual Loyal Opposition
  review lane.
- `DELIB-20260724-EXPANDED-TWELVE-WI-DELIVERY` — records the owner's request to
  drive this twelve-work-item set through VERIFIED without waiting between
  independent review lanes.

## Owner Decisions / Input

- `PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION`
  explicitly covers `WI-5664` in project
  `GTKB-SKILL-RENAME-REFERENCE-SWEEP`.
- The owner selected the manual Loyal Opposition review route. This revision
  requires a fresh independent LO review; no new owner decision is required.

## Findings Addressed

### Finding

**P1 — the original proposal mixed canonical, mirror, and registry targets
without an ownership map or focused parity proof.**

Response: this revision replaces the broad 21-path declaration with the exact
stale-reference inventory below. It changes canonical configuration first,
regenerates only the four owned rule projections, synchronizes the
command-surface triplet through its migration route, and adds a test that
isolates the command-surface package snapshot from an unrelated existing
`activity-disposition-profiles.toml` baseline mismatch.

## Scope Changes

### Exact stale-reference inventory and ownership

| Target | Bare reference(s) | Classification | Owner and update route | Proof |
| --- | --- | --- | --- | --- |
| `config/agent-control/gtkb-auto-finalization-sweep.md` | `skills/verify` at line 62 | canonical rule | edit canonical, then run `scripts/generate_rule_compatibility_projections.py` | generator `--check` and its focused platform test |
| `.claude/rules/auto-finalization-sweep.md` | `skills/verify` at line 62 | generated compatibility projection | generated only from its canonical counterpart; no independent semantics | generator `--check` |
| `config/agent-control/gtkb-review-gate.md` | `skills/verify` at 130; `skills/bridge-propose` at 168 | canonical rule | edit canonical, then regenerate projection | generator `--check` and focused platform test |
| `.claude/rules/codex-review-gate.md` | same two references at 130 and 168 | generated compatibility projection | `scripts/generate_rule_compatibility_projections.py` | generator `--check` |
| `config/agent-control/gtkb-file-bridge-protocol.md` | `skills/verify` at 178 | canonical rule | edit canonical, then regenerate projection | generator `--check` and focused platform test |
| `.claude/rules/file-bridge-protocol.md` | same reference at 178 | generated compatibility projection | `scripts/generate_rule_compatibility_projections.py` | generator `--check` |
| `config/agent-control/gtkb-loyal-opposition.md` | `skills/verify` at 160 | canonical rule | edit canonical, then regenerate projection | generator `--check` and focused platform test |
| `.claude/rules/loyal-opposition.md` | same reference at 160 | generated compatibility projection | `scripts/generate_rule_compatibility_projections.py` | generator `--check` |
| `config/agent-control/command-surface.toml` | `skills/bridge-propose` at 63; `skills/proposal-review` at 64 | canonical command-surface input | edit source; the route is recorded by move/rename manifest row 76 and consumed by `scripts/command_surface_disposition.py` | command-surface disposition test and focused package-snapshot test |
| `config/agent-control/gtkb-command-surface.toml` | same two references at 63–64 | retained synchronized configuration mirror | checked-in compatibility mirror designated by manifest row 76; update it in the same exact-content change | exact byte parity with canonical source |
| `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/command-surface.toml` | same two references at 63–64 | checked-in packaged v1 registry snapshot | package-resource synchronization from the canonical input is enforced by `test_context_manifest.py`; no independent consumer semantics | focused package-snapshot test |
| `groundtruth-kb/tests/test_context_manifest.py` | no stale path; test-only target | spec-derived regression test | add a dedicated assertion for the command-surface source/snapshot equality | focused test selector |

The four `.claude/rules` files are all generated compatibility projections;
`config/file-reference-migration/wi5640.toml` is the rule-projection policy and
requires 38 projections to remain current. The three command-surface files are
currently byte-identical. The existing aggregate context-manifest snapshot test
has an unrelated baseline failure on
`config/agent-control/activity-disposition-profiles.toml`, so the new focused
assertion must prove the `command-surface.toml` member independently rather than
masking that unrelated defect.

### Explicit non-scope

The initial proposal's `CONTROL-MAP`, startup bootstrap, knowledge-base-index,
role-capability-manifest, and other listed configuration files contain no bare
pre-rename skill-directory reference and are removed from this scope. Generated
Codex adapters (`.codex/skills/**`), templates, and package projections outside
the declared command-surface snapshot remain reserved for their owning work
items and generators.

## Pre-Filing Preflight Subsection

Candidate applicability and clause preflights must both pass before this draft
is filed. The live equivalents must pass after filing and before implementation
authorization is requested.

## Verification Plan

| Requirement | Focused evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | candidate and live applicability/clause preflights for this revision |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_generate_rule_compatibility_projections.py platform_tests/scripts/test_command_surface_disposition.py -q --tb=short`; `groundtruth-kb/.venv/Scripts/python.exe -m pytest --rootdir=groundtruth-kb --override-ini=testpaths=tests groundtruth-kb/tests/test_context_manifest.py::test_packaged_v1_command_surface_snapshot_matches_source_checkout -q --tb=short` |
| rule projection authority | `python scripts/generate_rule_compatibility_projections.py --check` must report all 38 projections current |
| command-surface source/snapshot parity | the new focused context-manifest test compares exactly the canonical and packaged `command-surface.toml` bytes, and `platform_tests/scripts/test_command_surface_disposition.py` preserves semantic parsing behavior |

## Risk And Rollback

Risk is bounded to stale documentation/configuration references and generated
mirror drift. The implementation must edit the four canonical rule inputs,
regenerate their owned mirrors, update the canonical command-surface input,
synchronize its two declared mirrors through the stated route, and make the
focused test prove that snapshot. If a generator or synchronization check shows
additional affected files, implementation stops for a revised proposal rather
than attributing undeclared files to WI-5664.

Rollback is a scoped revert of only the declared canonical, generated,
synchronized, and test paths under separate authorization, followed by the
same regeneration and parity checks. Numbered bridge artifacts and PAUTH remain
append-only evidence and are never deleted.
