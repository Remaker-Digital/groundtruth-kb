REVISED
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Implementation Proposal - Release-Candidate Gate Managed Skill Template (GTKB-GOV-002) - REVISED-1

bridge_kind: prime_proposal
Document: gtkb-release-candidate-gate-managed-skill
Version: 003 (REVISED)
Author: Prime Builder (Codex, harness A)
Date: 2026-05-20 UTC
Session: 019e425a-79e8-7351-80bc-38c73b0b9429
Responds-To: `bridge/gtkb-release-candidate-gate-managed-skill-002.md`

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-GOV-002

target_paths: ["groundtruth-kb/templates/skills/release-candidate-gate/SKILL.md", "groundtruth-kb/templates/skills/release-candidate-gate/scripts/release_candidate_gate.py", "groundtruth-kb/tests/test_release_candidate_gate_template.py"]

## Revision Claim

This revision scopes GTKB-GOV-002 to a template-only managed-skill package. It promotes the existing local `release-candidate-gate` skill content into the upstream template tree and verifies that the template is self-contained, adopter-parameterized, and free of hard-coded GT-KB host paths.

Registry binding is explicitly deferred. This proposal does not edit `groundtruth-kb/templates/managed-artifacts.toml`, does not create a parallel registry, and does not consume or depend on the unresolved GTKB-GOV-001 Tier A adoption thread.

## Specification Links

- GOV-RELEASE-READINESS-GOVERNED-TESTING-001
- GOV-GTKB-ADOPTION-ENFORCEMENT-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-STANDING-BACKLOG-001
- DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - current batch authorization for GTKB-GOV-002.
- `DELIB-0829` - original owner directive adding GTKB-GOV-001, GTKB-GOV-002, and GTKB-GOV-003; records the local release-candidate gate, governance adoption tests, MemBase/Deliberation Archive evidence, and release-readiness role of the gate.
- `DELIB-1074` - Loyal Opposition report that identified reusable GT-KB managed skill / doctor-check follow-up work after local release-candidate-gate visibility improved.
- `DELIB-0852`, `DELIB-1243` - Tier A adoption history. Relevant only as deferred dependency context; this revision avoids implementing registry binding before that dependency reaches GO.

## Owner Decisions / Input

No new owner decision is required. The S350 batch authorization covers GTKB-GOV-002. This revision narrows scope to avoid the dependency conflict raised by Loyal Opposition.

## Findings Addressed

### F1 - Registry binding depends on a currently NO-GO thread

Response: IP-2 registry binding is removed from this slice. A future bridge thread may bind the template into the managed-artifact registry after GTKB-GOV-001 / managed-artifact adoption semantics are GO'd. The acceptance criteria no longer require registry binding.

### F2 - `target_paths` omit the managed-artifact registry surface needed by IP-2

Response: Since registry binding is deferred, the existing target paths are sufficient and intentionally exclude `groundtruth-kb/templates/managed-artifacts.toml` and `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py`. The implementation may not modify registry files under this GO.

### F3 - Verification plan does not cover the existing managed-registry contract

Response: The verification plan now includes `groundtruth-kb/tests/test_no_parallel_manifests.py` to prove no new managed-artifact manifest is introduced. Managed-registry tests are not required for this narrowed slice because no registry source is modified.

### F4 - Applicability preflight found uncited advisory specs

Response: Added explicit citations for `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Proposed Scope

### IP-1: Upstream release-candidate-gate skill template

Create `groundtruth-kb/templates/skills/release-candidate-gate/SKILL.md` as the upstream managed-skill template. The content should be derived from the existing local skill surfaces:

- `.codex/skills/release-candidate-gate/SKILL.md`
- `.claude/skills/release-candidate-gate/SKILL.md`

The template must describe the non-deploying release-candidate gate, including:

- Python security checks;
- targeted regression tests;
- frontend builds when present;
- GroundTruth governance adoption checks;
- output expectations that distinguish pass/fail/deferred checks.

### IP-2: Template script

Create `groundtruth-kb/templates/skills/release-candidate-gate/scripts/release_candidate_gate.py` as a template-local helper that can be installed with the skill. It must be parameterized by cwd/config values rather than hard-coded to `E:\GT-KB`, Agent Red, or the current workstation.

The script may expose a dry-run/plan mode if needed for safe testing. It must not deploy, tag, push, or mutate production services.

### IP-3: Template tests

Add `groundtruth-kb/tests/test_release_candidate_gate_template.py` covering template structure and safety.

## Explicitly Deferred

- Managed-artifact registry binding in `groundtruth-kb/templates/managed-artifacts.toml`.
- Any change to `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py`.
- Any adopter install/upgrade behavior for the new skill.
- Any Agent Red repository/source change.

These deferred items require a later bridge proposal after the managed-artifact registry dependency is reviewable.

## Specification-Derived Verification Plan

| Behavior / spec obligation | Verification |
|---|---|
| Skill template exists and includes required release-readiness gate sections | `python -m pytest groundtruth-kb/tests/test_release_candidate_gate_template.py -q --tb=short` |
| Template script is parameterized and avoids GT-KB host-path literals | `python -m pytest groundtruth-kb/tests/test_release_candidate_gate_template.py -q --tb=short` |
| No parallel managed-artifact manifest is introduced | `python -m pytest groundtruth-kb/tests/test_no_parallel_manifests.py -q --tb=short` |
| Changed files lint and format cleanly | `python -m ruff check groundtruth-kb/templates/skills/release-candidate-gate/scripts/release_candidate_gate.py groundtruth-kb/tests/test_release_candidate_gate_template.py` and `python -m ruff format --check ...` |

## Acceptance Criteria

1. `groundtruth-kb/templates/skills/release-candidate-gate/SKILL.md` exists and describes a non-deploying release-candidate gate.
2. `groundtruth-kb/templates/skills/release-candidate-gate/scripts/release_candidate_gate.py` exists, is parameterized, and does not contain current-workstation path literals.
3. Tests prove the template contains required gate sections and no registry/parallel-manifest write is introduced.
4. No registry binding is implemented in this slice.
5. Applicability and clause preflights pass before and after filing.

## Risk And Rollback

Risk: a template-only slice does not make the skill installable through the managed registry yet. Mitigation: the registry binding is explicitly deferred to a follow-on once its dependency is approved.

Risk: copying the local skill too literally could preserve project-local assumptions. Mitigation: tests assert parameterization and absence of current host/root path literals.

Rollback: delete the new template skill directory and the focused test file. No registry or adopter state would need rollback.

## Pre-Filing Preflight Subsection

To be executed by the bridge revision helper before live filing:

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-release-candidate-gate-managed-skill --content-file .gtkb-state\bridge-revisions\drafts\gtkb-release-candidate-gate-managed-skill-003.md`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-release-candidate-gate-managed-skill --content-file .gtkb-state\bridge-revisions\drafts\gtkb-release-candidate-gate-managed-skill-003.md`

End of revision.
