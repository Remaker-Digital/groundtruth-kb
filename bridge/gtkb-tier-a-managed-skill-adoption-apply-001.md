NEW

# Implementation Proposal - Complete Tier A Managed-Skill Adoption Apply (GTKB-GOV-001)

bridge_kind: implementation_proposal
Document: gtkb-tier-a-managed-skill-adoption-apply
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-GOV-001

target_paths: ["groundtruth-kb/src/groundtruth_kb/adoption/tier_a_registry.py", "groundtruth-kb/src/groundtruth_kb/cli_adoption.py", "groundtruth-kb/tests/test_tier_a_adoption.py"]

This NEW proposal completes the Tier A managed-skill adoption apply: finalizes the upstream GT-KB managed artifact registry for Tier A hooks, rules, skills, settings, and gitignore exceptions, plus an apply CLI that adopter projects use to install/reconcile their inventory.

## Claim

Build the upstream Tier A registry as a structured manifest (TOML) + an apply CLI that reads an adopter project's current state, compares against the registry, and either (a) installs missing managed artifacts, (b) reports project-owned overrides, or (c) reports explicit rejections with rationale. Replaces the pending `gtkb-skills-tier-a-adoption-apply` thread referenced in the WI description.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-GTKB-ADOPTION-ENFORCEMENT-001` - source spec for adoption work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - managed artifacts framing.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `SPEC-AUQ-POLICY-ENGINE-001` - CLI surface.
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

Existing requirements sufficient. WI-3308 description + GOV-GTKB-ADOPTION-ENFORCEMENT-001 specify the registry + apply pattern.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-ADOPTER-EXPERIENCE per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 (registry) + IP-2 (CLI) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Tier A managed artifact registry

`groundtruth-kb/src/groundtruth_kb/adoption/tier_a_registry.py` (Python loader) + `groundtruth-kb/data/tier_a_registry.toml` (manifest):

Manifest entries enumerate Tier A artifacts: rule files (`.claude/rules/file-bridge-protocol.md`, `bridge-essential.md`, etc.), hooks (`bridge-compliance-gate.py`, `formal-artifact-approval-gate.py`, etc.), skills (`bridge/SKILL.md`, etc.), settings keys, and gitignore exceptions. Each entry includes: artifact_path, content_sha256 (pinned version), description, install_target (where in adopter), update_policy (managed | project-owned-override-allowed | locked).

### IP-2: gt adoption apply CLI

`groundtruth-kb/src/groundtruth_kb/cli_adoption.py`:

```python
@adoption.command("apply")
@click.option("--adopter-root", required=True)
@click.option("--dry-run", is_flag=True)
@click.option("--report-only", is_flag=True)
def apply(adopter_root, dry_run, report_only):
    # Compare registry vs adopter state
    # Plan: install_missing, update_outdated, leave_project_owned, leave_rejected
    # Execute or dry-run
```

### IP-3: Tests

Tests cover: registry loading, drift detection, plan generation, dry-run output, apply effects on temp adopter.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Registry loads from TOML | `test_tier_a_registry_loads` |
| Drift detected when adopter missing artifact | `test_drift_detected_missing_artifact` |
| Project-owned override respected | `test_project_owned_override_skipped` |
| Plan dry-run prints actions without applying | `test_dry_run_no_side_effects` |
| Apply installs missing artifacts | `test_apply_installs_missing` |
| Apply preserves project-owned content | `test_apply_preserves_project_owned` |

Run: `python -m pytest groundtruth-kb/tests/test_tier_a_adoption.py -v`.

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; 6 tests PASS.
- Both preflights PASS.
- Manifest enumerates at least 10 Tier A artifacts (real coverage).

## Risks / Rollback

- Risk: pinned content_sha256 drifts when upstream artifact changes. Mitigation: registry update is a discrete owner-approved operation; not auto-bumped.
- Rollback: remove the registry + CLI; adopter projects continue with manual artifact management.

## Recommended Commit Type

`feat` - new adoption infrastructure. ~200 LOC + manifest + tests.
