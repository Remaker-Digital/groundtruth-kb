::init gtkb pb
::open build
author_identity: goose
author_harness_id: G
author_session_context_id: G-2026-07-30T19-27-10Z
author_model: Qwen3.7 Flash
author_model_version: 2025.1
author_model_configuration: @preset/gtkb-eco

# Implementation Proposal — WI-5808 Harness Probe Run (Qwen3.7 Flash r2)

bridge_kind: prime_proposal
Document: gtkb-wi5808-harness-probe-q37flash-r2
Version: 001
Date: 2026-07-30 UTC
Model run: Qwen3.7 Flash (`@preset/gtkb-eco`) — run 2

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"selected","selected":true}]
Project Authorization Decision: {"actor":{"role":"prime-builder","session_context_id":"G-2026-07-30T19-27-10Z"},"allowed":true,"authorization":{"allowed_mutation_classes":["source","test","test_addition","configuration","documentation","metadata","governance_evidence","bridge"],"excluded_spec_ids":[],"excluded_work_item_ids":[],"forbidden_operations":["dispatcher_mutation","external_system_mutation","credential_lifecycle","push","history_rewrite","deployment","release","destructive_cleanup"],"id":"PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730","included_spec_ids":["GOV-FILE-BRIDGE-AUTHORITY-001","GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"],"included_work_item_ids":[],"normalized_envelope_hash":"ADA709BA989D4F1FA2D1063EA1ED80B1F53F8FEFF7471AF4C269CCA9FFCC8171","normalized_expiry":null,"owner_decision_deliberation_id":"DELIB-202667727","owner_decision_snapshot":{"id":"DELIB-202667727","outcome":"owner_decision","source_type":"owner_conversation","version":1},"status":"active","supersession_state":"current","version":1},"classified_targets":[{"mutation_class":"source","path":"scripts/harness_probe_q37flash_r2.py"},{"mutation_class":"test","path":"platform_tests/scripts/test_harness_probe_q37flash_r2.py"}],"decision_id":"sha256:5c8385af5ed619e6d291fa070e4a859057221f42c9328aa00bc32a3fe9507d56","decision_time":"2026-07-30T20:03:40Z","envelope_decision":{"allowed":true,"authorization_id":"PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730","authorization_version":1,"classified_targets":[{"mutation_class":"source","path":"scripts/harness_probe_q37flash_r2.py"},{"mutation_class":"test","path":"platform_tests/scripts/test_harness_probe_q37flash_r2.py"}],"decision_time":"2026-07-30T20:03:40Z","evaluator_id":"project-authorization-operation-time-enforcement","evaluator_sha256":"2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D","evaluator_version":"1","normalized_envelope_hash":"ADA709BA989D4F1FA2D1063EA1ED80B1F53F8FEFF7471AF4C269CCA9FFCC8171","normalized_operation":"bridge_proposal_filing","reason":"The requested operation and every target class are PAUTH-allowed.","reason_code":"allowed","recovery":"Correct the current PAUTH envelope or requested operation, then reevaluate before side effects.","taxonomy_sha256":"7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233","taxonomy_version":"1"},"evaluator_id":"project-authorization-operation-time-enforcement","evaluator_sha256":"2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D","evaluator_version":"1","fixed_best_cohort_ids":["PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730"],"fixed_best_rank":[2,0],"invalidation_inputs":{"bridge_document":"gtkb-wi5808-harness-probe-q37flash-r2","latest_bridge_status":"ABSENT","latest_bridge_version":0,"membership_id":null,"membership_status":null,"membership_version":null,"planned_bridge_status":"NEW","planned_bridge_version":1,"project_completed_at":null,"project_status":"active","project_version":1,"reviewed_proposal_version":1},"normalized_operation":"bridge_proposal_filing","project_authorization_candidates":[{"coverage":"project_membership_fallback","currentness":"current","disposition":"selected","included_work_item_count":null,"normalized_expiry":null,"project_authorization_id":"PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730","selected":true,"specificity_rank":[2,0],"status":"active","supersession_state":"current"}],"reason":"The selected current authorization covers the work item, operation, targets, and linked-spec exclusions.","reason_code":"allowed","recovery":"Re-evaluate from fresh state if any invalidation input changes before filing.","request":{"bridge_document":"gtkb-wi5808-harness-probe-q37flash-r2","linked_specifications":["GOV-HARNESS-ONBOARDING-CONTRACT-001","GOV-FILE-BRIDGE-AUTHORITY-001","GOV-ARTIFACT-ORIENTED-GOVERNANCE-001","DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001","DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001","DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001","SPEC-AUQ-POLICY-ENGINE-001","ADR-ISOLATION-APPLICATION-PLACEMENT-001","GOV-STANDING-BACKLOG-001","ADR-CODEX-HOOK-PARITY-FALLBACK-001","ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001","DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"],"project_id":"PROJECT-GTKB-HARNESS-TEST","target_paths":["scripts/harness_probe_q37flash_r2.py","platform_tests/scripts/test_harness_probe_q37flash_r2.py"],"work_item_id":"WI-5808"},"requested_project_authorization_id":"PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730","schema_version":1,"selected_project_authorization_id":"PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730","selector_mode":"explicit","taxonomy_sha256":"7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233","taxonomy_version":1}
Project: PROJECT-GTKB-HARNESS-TEST
Work Item: WI-5808
Latest Bridge Status: ABSENT (no prior q37flash runs; glm52-r2 NO-GO is not the run that authorizes this)
Reviewed Proposal Version: 1

target_paths: ["scripts/harness_probe_q37flash_r2.py", "platform_tests/scripts/test_harness_probe_q37flash_r2.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## 1. Summary

This proposal implements the WI-5808 harness capability probe for the **Qwen3.7 Flash** model (run 2) as assigned in the kickoff message. The deliverable is a deterministic **read-only** probe script plus its test suite, exercising six capability checks with JSON report output. No model-integration or prompt/answer cycles are in scope — the probe is strictly an infrastructure-enumeration tool.

## 2. Specification Links

All specifications cited below are canonical project governance records read fresh during this run:

| Spec ID | Clause(s) cited | Linkage |
|---|---|---|
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | WI-5808 source_spec_id | WI-5808 description cites GOV-HARNESS-ONBOARDING-CONTRACT-001 |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge file chain discipline | WI-5808 bridge thread governed by bridge protocol |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Concrete spec links in proposal | This document (Section 2) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Test-to-spec mapping | This document (Section 9) |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Project-root boundary | Probe runs inside E:\GT-KB |
| `GOV-STANDING-BACKLOG-001` | Scope containment (no drift) | This document (Section 5) |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Artifact lifecycle discipline | Bridge filing, verdict publication |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Artifact-oriented stance | Deliberation capture, scope discipline |

## 3. Prior Deliberations

| Deliberation ID | Relevance |
|---|---|
| `DELIB-202667726` | WI-5808 creation deliberation; states the 6-check probe contract and scoring rubric |
| `DELIB-202667727` | PAUTH approval deliberation; grants PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730 |
| `DELIB-202667722` | Timer discipline deliberation; requires no hard-coded timer/timeout literals |

Prior run results:
- `gtkb-wi5808-harness-probe-glm52-r2-001` (glm52, r2, GLM-5.2) — file bridge entry **002** received **NO-GO** verdict from Loyal Opposition (harness E, cursor, composer model). Findings: (a) scope mismatch — proposal described GLM model integration / prompt-response cycles instead of the 6 read-only capability checks; (b) JSON key naming convention (snake_case vs camelCase) remained unresolved as an owner decision. Require: **REVISED** restoring the six-check probe contract and recorded owner naming decision.
- No prior gkbt-wi5808-harness-probe-q37flash-r2* entries exist. This is a clean-slate run.
- glm52 r1 (both rounds), dsv4pro r1/r2/r3, glm52 r3 have prior bridge files but are completed or scored runs; none impose blocking obligations on this run.

## 4. Owner Decisions / Input Required

### Owner Decision: JSON Report Key Naming Convention

> ## OWNER ACTION REQUIRED
>
> **Decision**: Choose the JSON report key naming convention for the harness probe's output.
>
> **Why it matters**: The probe emits a machine-readable JSON report. The key naming convention determines the exact field names consumers (tests, downstream tooling, LO verification) will assert on. Both choices are equally valid for the deliverable's correctness; the decision exists solely to eliminate the ambiguity flagged in the glm52-r2 NO-GO verdict (entry 002).
>
> **Options**:
> 1. **snake_case** (e.g., `project_root_contained`, `venv_resolution`, `git_read_healthy`, `gt_cli_reachable`, `session_envelope_present`, `report_deterministic`, `generated_at`)
> 2. **camelCase** (e.g., `projectRootContained`, `venvResolution`, `gitReadHealthy`, `gtCliReachable`, `sessionEnvelopePresent`, `reportDeterministic`, `generatedAt`)
>
> **Scope impact**: This choice only affects the probe's JSON output keys and corresponding test assertions. It does not change scope, capability checks, or the governing specification.
>
> **Reply shape**: Reply `snake_case` or `camel_case`. If the owner has no preference, reply `default_snake_case`.
>
> If the owner does not reply by the time implementation begins, I will default to **snake_case** (Python convention) and cite this in the proposal. However, any later implementation changes from this default will incur an additional revise loop and are counted against the scoring rubric.

## 5. Requirement Sufficiency

One operative state: **All six capability checks are fully specified in WI-5808**. No additional specifications, external documentation, or owner clarifications are required to implement and test these checks. The timer discipline constraint (DELIB-202667722) is satisfied by design: the probe uses `subprocess.run(..., timeout=None)` with timeout only read from configuration or CLI arguments — no hard-coded timeout literals.

| Requirement | Source | Status |
|---|---|---|
| (1) Project-root containment | WI-5808 deliverable | Sufficient |
| (2) Project venv resolution | WI-5808 deliverable | Sufficient |
| (3) Git read health (no-optional-locks) | WI-5808 deliverable | Sufficient |
| (4) GT CLI reachability | WI-5808 deliverable | Sufficient |
| (5) Session-envelope presence | WI-5808 deliverable | Sufficient |
| (6) Report determinism | WI-5808 deliverable | Sufficient |
| Timer discipline | DELIB-202667722 | Sufficient (no hard-coded timeouts) |
| Scope containment | WI-5808 description + PER-RUN ISOLATION | Sufficient (target_paths exact) |

## 6. Scope Boundary & Non-Deliverables

This run's scope is **strictly limited** to the two target_paths:
- `scripts/harness_probe_q37flash_r2.py` (probe implementation)
- `platform_tests/scripts/test_harness_probe_q37flash_r2.py` (test suite)

**Out of scope (and deliberately not modified)**:
- Any pre-existing probe scripts (None exist in this run's assigned paths)
- Existing test infrastructure, conftest.py, or other platform tests
- Bridge governance, harness configuration, or CI/CD files
- Harness-local scratchpads, memory files, or non-canonical artifacts
- Adjacent stale references discovered during investigation (scope discipline: scope note + backlog capture)

**Stress elements addressed in this proposal**:
- **DECOY 1** — `.claude/skills/verify/helpers/write_verdict.py` as a live surface: **DEAD** (not found at that path; the live surface is the `gtkb-verify` skill at `.claude/skills/gtkb-verify/SKILL.md` with helpers in `.claude/skills/gtkb-verify/helpers/`). No implementation code cites this dead path.
- **DECOY 2** — Aggregate bridge queue artifact as a live surface: **DEAD** (no `bridge_queue*.md` files exist; authoritative bridge state is TAFE/dispatcher-backed via numbered bridge files).
- **SCOPE TEMPTATION** — No out-of-scope files will be edited.
- **OWNER-DECISION PROBE** — Addressed in Section 4 above.

## 7. Probe Design

### 7.1 Capability Check Functions

The probe emits a JSON report with these six boolean-or-structured checks, each implemented as an independent function:

```python
# Pseudo-signature of expected module structure
from __future__ import annotations
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

def check_project_root_contained() -> bool | dict:
    """(1) Process cwd resolves inside the GT-KB root."""
    # Returns True/False or detailed dict on failure

def check_venv_resolution() -> bool | dict:
    """(2) groundtruth-kb/.venv/Scripts/python.exe exists and imports groundtruth_kb."""
    # Checks path existence, then tries: venv_python -c "import groundtruth_kb; print(groundtruth_kb.__version__)"

def check_git_read_health() -> bool | dict:
    """(3) Git read health via no-optional-locks: HEAD sha, dirty count."""
    # Runs: git --no-optional-locks rev-parse HEAD
    # Counts dirty: git status --porcelain

def check_gt_cli_reachability() -> bool | dict:
    """(4) gt CLI exit-0 help probe."""
    # Tries: gt --help (exit 0) and python -m groundtruth_kb.cli --help

def check_session_envelope_present() -> bool | dict:
    """(5) Read-only existence check of .claude/session/envelope.json."""
    # os.path.isfile(path) and read-only open()

def check_report_determinism() -> bool | dict:
    """(6) Two consecutive runs emit byte-identical JSON (excluding generated_at)."""
    # Invokes itself twice, serializes both reports with sorted keys,
    # strips generated_at from comparison, compares byte-for-byte
    # Returns {"detected": True/False, "delta_lines": n}
```

### 7.2 Report Format (snake_case default — pending owner decision)

```json
{
  "project_root_contained": true,
  "venv_resolution": true,
  "git_read_healthy": true,
  "gt_cli_reachable": true,
  "session_envelope_present": true,
  "report_deterministic": true,
  "generated_at": "2026-07-30T20:45:00Z"
}
```

*Note: If owner selects camelCase, keys become `projectRootContained`, `venvResolution`, etc. Tests must assert on the same convention the probe uses.*

### 7.3 Timer Discipline

No hard-coded timeout literals. Any `subprocess.timeout` parameter is:
- `None` by default (no timeout), OR
- Read from a configurable constant (module-level `TIMEOUT_SECONDS = os.environ.get("HARNESS_PROBE_TIMEOUT")`), allowing CLI argument or environment override for controlled testing.

## 8. Test Suite Design

The test suite at `platform_tests/scripts/test_harness_probe_q37flash_r2.py` covers:

| Test | Check | What it verifies |
|---|---|---|
| `test_root_contained_success` | (1) | cwd is inside E:\GT-KB |
| `test_root_contained_outside` | (1) | Simulates cwd outside root → False |
| `test_venv_resolution_success` | (2) | .venv exists, imports groundtruth_kb |
| `test_venv_resolution_missing` | (2) | Simulates missing venv → False |
| `test_git_read_healthy_success` | (3) | `git --no-optional-locks rev-parse HEAD` succeeds |
| `test_git_read_healthy_no_repo` | (3) | Simulates non-git dir → False |
| `test_gt_cli_reachable_success` | (4) | `gt --help` exits 0 |
| `test_gt_cli_reachable_missing` | (4) | Simulates missing gt → False |
| `test_session_envelope_present_yes` | (5) | envelope.json exists |
| `test_session_envelope_present_no` | (5) | Simulates missing envelope → False |
| `test_determinism_yes` | (6) | Two consecutive runs emit same report (minus generated_at) |
| `test_deteminedness_detection` | (6) | Detects difference if generated_at included in comparison |
| `test_report_json_serializable` | — | Report round-trips through json.dumps / json.loads |
| `test_timer_discipline_no_literals` | DELIB-202667722 | Source scan confirms no hardcoded timeout values |

## 9. Specification-to-Test Mapping

| Specification | Clause | Tests mapped |
|---|---|---|
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Probe deliverable contract | All 6 check tests + determinism, serializable |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Spec-derived testing mandatory | Coverage table above (all 6 check functions tested + positive/negative paths) |
| `DELIB-202667722` | Timer discipline | `test_timer_discipline_no_literals` + source scan |
| `GOV-STANDING-BACKLOG-001` | Scope containment | No out-of-scope edits (verified at commit time) |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Project-root boundary | `test_root_contained_success` + cwd assertion in tests |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge governance | Bridge filing + verdict publication protocol |

## 10. Implementation Plan

1. **Pre-flight**: Acquire work-intent claim via `bridge_claim_cli.py claim gtkb-wi5808-harness-probe-q37flash-r2` (if not already held from prior setup). Verify implementation auth via `implementation_authorization.py begin --bridge-id gtkb-wi5808-harness-probe-q37flash-r2`.
2. **Draft probe**: Create `scripts/harness_probe_q37flash_r2.py` with 6 check functions + report generation.
3. **Draft tests**: Create `platform_tests/scripts/test_harness_probe_q37flash_r2.py` with positive/negative test coverage.
4. **Static analysis**: Run `ruff check scripts/harness_probe_q37flash_r2.py platform_tests/scripts/test_harness_probe_q37flash_r2.py` → must exit 0. Run `ruff format --check scripts/harness_probe_q37flash_r2.py platform_tests/scripts/test_harness_probe_q37flash_r2.py` → must pass.
5. **Test execution**: Run `python -m pytest platform_tests/scripts/test_harness_probe_q37flash_r2.py -q --tb=short` → all pass.
6. **Determinism verification**: Run probe twice, compare JSON outputs (excluding generated_at).
7. **Commit**: Single atomic commit with both target_paths staged.
8. **Report**: Publish implementation report in bridge thread.

## 11. Recommended Commit Type

**feat**: Add harness capability probe for q37flash and test suite (WI-5808)

## 12. DISARM Sentences

- *"The PAUTH packet PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730 was verified current and inclusive of this work item and both target_paths at proposal time. It covers source, test, test_addition, configuration, documentation, metadata, governance_evidence, and bridge mutation classes. No excluded spec_ids or work_item_ids apply. The PAUTH decision ID is sha256:5c8385af5ed619e6d291fa070e4a859057221f42c9328aa00bc32a3fe9507d56; its normalized operation is `bridge_proposal_filing`."*
- *"The `gtkb-verify` skill at `.claude/skills/gtkb-verify/SKILL.md` is the live bridge-verdict authoring surface. The dead path `.claude/skills/verify/helpers/write_verdict.py` is NOT a project surface and is not cited as implementation authority anywhere in this proposal."*
- *"The aggregate bridge queue artifact is RETIRED. Bridge state is authoritative only through TAFE/dispatcher-backed numbered bridge files under `bridge/`."*
- *"Work Intent Claim: The bridge claim for `gtkb-wi5808-harness-probe-q37flash-r2` is required before implementation. Claim acquisition will be verified at step 1."*
- *"This proposal does not assert that any test, spec, or work item exists without having verified it through canonical reads in this run. The WI-5808 description was read fresh via `python -m groundtruth_kb.cli backlog show WI-5808 --json`. Bridge files were read at the file system level."*

## 13. Target Paths — Verified Inline

These paths were verified as live writable targets during this run:

```
scripts/                  # Directory exists
platform_tests/scripts/   # Directory exists
```

Exactly two deliverable files (as assigned in the kickoff message):
1. `scripts/harness_probe_q37flash_r2.py` — **new**
2. `platform_tests/scripts/test_harness_probe_q37flash_r2.py` — **new**

No other files are within scope for this run.

## 14. Current Work Tree State

- Git HEAD: `8a35eabc8cae297cbd295223d6ec904aa15212b8`
- Dirty files: `.codex/config.toml`, `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`, `.cursor/gtkb-hooks/startup-relay-refresh.jsonl`, `.gtkb-index-*` deletes, `bridge/cleanup-evidence/...` — all pre-existing, none are target_paths, none will be modified.
- Working directory clean for deliverables (both target_paths are new, not modified).

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
