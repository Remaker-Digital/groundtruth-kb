NEW

# Implementation Proposal - Agent Red Deployability Preservation Gate (WI-3248)

bridge_kind: prime_proposal
Document: gtkb-agent-red-deployability-preservation-gate
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH-P0-DEPLOYABILITY-GATE
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: WI-3248

target_paths: ["groundtruth-kb/src/groundtruth_kb/adoption/deployability_preservation_gate.py", "scripts/adopter_deployability_check.py", "tests/scripts/test_adopter_deployability_check.py"]

This NEW proposal implements `WI-3248` (P0): the GT-KB-side preservation gate that runs before any irreversible adopter migration / cutover / extraction / deletion / restructuring. The gate verifies the adopter remains deployable, maintainable, and enhanceable — preventing migrations from silently breaking the adopter's release path.

## Claim

Build a `gt adopter deployability-check` command + library function that runs against a target adopter root and asserts: (a) release-candidate path is intact (RC-gate skill present + runnable in dry-run), (b) Python language gate satisfied (project's declared `python_requires` resolvable), (c) frontend build path intact (if applicable per project metadata), (d) test suite collects without errors. Returns PASS/FAIL with per-check diagnostic.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - source spec cited by the WI; the gate is artifact-oriented governance over adopters.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness frames adopter deployability.
- `GOV-GTKB-ADOPTION-ENFORCEMENT-001` - adopter framework.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `SPEC-AUQ-POLICY-ENGINE-001` - CLI surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root; the gate operates on adopter roots which may be under `applications/`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI-3248 tracked.
- `DELIB-S350-BATCH6-P0P1-AUTHORIZATION` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH6-P0P1-AUTHORIZATION` - batch-6 owner authorization (P0/P1 amendment).
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - parent ADOPTER-EXPERIENCE authorization.

## Owner Decisions / Input

- 2026-05-15 UTC, S350+: owner directive "I authorize the remaining P0/P1. Please continue to parallelize the implementation proposals and work through the backlog."

## Requirement Sufficiency

Existing requirements sufficient. WI-3248 description specifies the 4 verification checks (release-candidate path, Python gate, frontend build, test suite collection).

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One P0 WI; member of PROJECT-GTKB-ADOPTER-EXPERIENCE per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-15-batch6-p0p1-amendments.json`. Review-packet inventory: IP-1 (gate library) + IP-2 (CLI) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Deployability preservation gate library

`groundtruth-kb/src/groundtruth_kb/adoption/deployability_preservation_gate.py`:

```python
@dataclass
class DeployabilityCheckResult:
    name: str
    status: str  # PASS | FAIL | SKIP | WARN
    detail: str

def check_adopter_deployability(adopter_root: Path) -> list[DeployabilityCheckResult]:
    return [
        check_rc_gate(adopter_root),
        check_python_gate(adopter_root),
        check_frontend_build_path(adopter_root),
        check_test_suite_collects(adopter_root),
    ]
```

Each sub-check is read-only / dry-run only — no actual builds or deploys. Returns FAIL with diagnostic on broken state.

### IP-2: CLI surface

`scripts/adopter_deployability_check.py`: CLI wrapper. `python scripts/adopter_deployability_check.py --adopter-root <path> [--json]`. Exit 0 if all PASS or SKIP; non-zero if any FAIL.

### IP-3: Tests

Tests cover fixture adopter scenarios: healthy adopter (all PASS), broken RC-gate (FAIL), missing Python requires (FAIL), missing frontend (SKIP if no frontend declared), broken test suite (FAIL).

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Healthy adopter all PASS | `test_healthy_adopter_all_pass` |
| Broken RC-gate FAIL | `test_broken_rc_gate_fails` |
| Missing python_requires FAIL | `test_missing_python_gate_fails` |
| Missing frontend gracefully SKIP | `test_no_frontend_skip` |
| Broken test suite collection FAIL | `test_broken_test_collection_fails` |
| Exit code reflects results | `test_cli_exit_code` |
| JSON output schema | `test_cli_json_schema` |

Run: `python -m pytest tests/scripts/test_adopter_deployability_check.py -v`.

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; 7 tests PASS.
- Both preflights PASS.
- Gate is intended to be called BEFORE any migration WI begins implementation (operational contract documented in proposal text).

## Risks / Rollback

- Risk: false-negative on healthy adopter (gate misclassifies). Mitigation: per-check diagnostic + WARN tier for edge cases.
- Risk: false-positive on broken adopter (gate passes broken state). Mitigation: clear FAIL conditions documented per check; spot-check against Agent Red.
- Rollback: remove library + script.

## Recommended Commit Type

`feat` - new P0 governance gate. ~150 LOC + tests.
