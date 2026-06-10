NEW

# Implementation Proposal - Governance-Adoption Doctor Check (GTKB-GOV-003)

bridge_kind: prime_proposal
Document: gtkb-governance-adoption-doctor-check
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-GOV-003

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_adoption_drift.py"]

This NEW proposal adds a `gt project doctor` check that reports adopter drift across `groundtruth.toml`, `.claude` hooks/rules/skills, workflow gates, and KnowledgeDB gate plugins. Provides a first-class adopter health signal beyond test passing.

## Claim

Extend the existing doctor with a `check_adoption_drift` function that: (1) loads the Tier A registry (per GTKB-GOV-001), (2) compares adopter's actual installed artifacts against the registry's expected content_sha256 + presence, (3) classifies each artifact as managed-current, managed-outdated, project-owned-override, or missing, (4) emits per-artifact severity (INFO/WARN/FAIL).

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-GTKB-ADOPTION-ENFORCEMENT-001` - adoption enforcement contract.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release-readiness; adoption drift is release-relevant.
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

Existing requirements sufficient. Sibling WI-3308 (Tier A registry) is the prerequisite; this WI consumes it for drift reporting.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-ADOPTER-EXPERIENCE per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 + IP-2 single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: check_adoption_drift in doctor.py

In `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, add:

```python
def check_adoption_drift(project_root: Path) -> CheckResult:
    """Check adopter artifacts against Tier A registry."""
    registry = load_tier_a_registry()
    drift_entries = []
    for entry in registry:
        actual_path = project_root / entry.install_target
        if not actual_path.exists():
            drift_entries.append(("missing", entry.artifact_path, "FAIL" if entry.update_policy == "locked" else "WARN"))
            continue
        actual_sha = hashlib.sha256(actual_path.read_bytes()).hexdigest()
        if actual_sha != entry.content_sha256:
            severity = "WARN" if entry.update_policy == "project-owned-override-allowed" else "FAIL"
            drift_entries.append(("outdated_or_override", entry.artifact_path, severity))
    return CheckResult(name="adoption_drift", status=...)
```

Wire into `gt project doctor` output.

### IP-2: Tests

Tests cover: clean adopter (no drift), missing artifact (FAIL or WARN per policy), modified artifact (override or outdated), .claude/settings.local.json detection (local-only setting).

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Clean adopter reports no drift | `test_clean_adopter_no_drift` |
| Missing locked artifact reports FAIL | `test_missing_locked_artifact_fails` |
| Missing optional artifact reports WARN | `test_missing_optional_warns` |
| Modified artifact with override-allowed reports WARN | `test_modified_with_override_warns` |
| Modified artifact locked reports FAIL | `test_modified_locked_fails` |
| settings.local.json detected as local-only | `test_settings_local_json_detected` |

Run: `python -m pytest groundtruth-kb/tests/test_doctor_adoption_drift.py -v`.

## Acceptance Criteria

- IP-1 check landed; 6 tests PASS.
- Both preflights PASS.
- Output included in `gt project doctor` default mode.

## Risks / Rollback

- Risk: false-positive drift on adopters with legitimate but undocumented local customizations. Mitigation: project-owned overrides explicitly supported by registry.
- Risk: depends on GTKB-GOV-001 registry landing first. Mitigation: gate enabled only when registry available; falls back to silent skip otherwise.
- Rollback: remove the check function; doctor continues with existing checks.

## Recommended Commit Type

`feat` - new doctor check. ~80 LOC + tests.
