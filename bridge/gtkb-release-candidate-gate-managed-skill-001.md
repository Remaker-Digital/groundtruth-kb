NEW

# Implementation Proposal - Promote Release-Candidate Gate to Managed Skill (GTKB-GOV-002)

bridge_kind: prime_proposal
Document: gtkb-release-candidate-gate-managed-skill
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-GOV-002

target_paths: ["groundtruth-kb/templates/skills/release-candidate-gate/SKILL.md", "groundtruth-kb/templates/skills/release-candidate-gate/scripts/release_candidate_gate.py", "groundtruth-kb/tests/test_release_candidate_gate_template.py"]

This NEW proposal promotes the existing `release-candidate-gate` skill (currently project-local in adopter scaffolds) into an upstream GT-KB managed skill so downstream adopters can install it through the managed artifact registry.

## Claim

Move the release-candidate-gate logic into a versioned upstream template under `groundtruth-kb/templates/skills/release-candidate-gate/`. The Tier A registry (per GTKB-GOV-001) references it. The skill covers: security scans, dependency audit, targeted regression suites, frontend builds, DA/MemBase integrity, and adoption-doctor outputs.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release-readiness governance contract.
- `GOV-GTKB-ADOPTION-ENFORCEMENT-001` - adoption framework.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - managed-artifact framing.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-ADOPTER-EXPERIENCE authorization including this WI.

## Requirement Sufficiency

Existing requirements sufficient.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-ADOPTER-EXPERIENCE per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 (skill template) + IP-2 (registry binding) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Skill template

Migrate the existing release-candidate-gate skill into `groundtruth-kb/templates/skills/release-candidate-gate/` with SKILL.md + accompanying scripts. Parameterize adopter-specific paths via template variables (e.g., `{{adopter_test_root}}`, `{{adopter_security_scan_target}}`).

### IP-2: Tier A registry binding

Add release-candidate-gate as a Tier A managed entry (depends on GTKB-GOV-001 registry landing; reference its slug in this proposal's Prior Deliberations once GO'd).

### IP-3: Tests

Verify template renders correctly for fixture adopter inputs; ensure managed update_policy preserves adopter-customized parameters.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Skill template renders with adopter parameters | `test_template_renders_with_parameters` |
| Default parameters used when adopter omits | `test_template_defaults_applied` |
| Template includes all 5 readiness check sections | `test_template_includes_all_checks` |
| Registry entry references template path | `test_registry_references_skill_template` |
| Render does not leak GT-KB internal paths | `test_render_no_internal_path_leakage` |

Run: `python -m pytest groundtruth-kb/tests/test_release_candidate_gate_template.py -v`.

## Acceptance Criteria

- IP-1 template landed.
- IP-2 registry binding present.
- IP-3 tests PASS (5 tests).
- Both preflights PASS.

## Risks / Rollback

- Risk: existing adopters with customized release-candidate-gate skills may diverge from template. Mitigation: managed update_policy supports project-owned overrides.
- Rollback: remove template + registry binding; existing adopter skills stay as-is.

## Recommended Commit Type

`feat` - new managed skill template. ~100 LOC + template.
