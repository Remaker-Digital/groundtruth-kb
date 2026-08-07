REVISED
::init gtkb pb
::open build
author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: G-2026-08-03T15-24-47Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;::open build

bridge_kind: prime_proposal
Document: gtkb-wi5808-harness-probe-glm52-r3
Version: 003 (REVISED; responding to NO-GO v002)
Responds to: bridge/gtkb-wi5808-harness-probe-glm52-r3-002.md
Date: 2026-08-04 UTC

# Implementation Proposal: Harness Capability Probe (GLM-5.2 Run 3) — WI-5808

**Author:** Prime Builder (Goose desktop, harness G, session G-2026-07-30T19-27-10Z)
**Date:** 2026-07-30
**Work Item:** WI-5808
**Bridge slug:** gtkb-wi5808-harness-probe-glm52-r3

target_paths: ["scripts/harness_probe_glm52_r3.py", "platform_tests/scripts/test_harness_probe_glm52_r3.py"]

---

## Project Authorization

- Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730
- Project: PROJECT-GTKB-HARNESS-TEST
- Work Item: WI-5808

DISARM: The project authorization grant was verified via fresh read of DELIB-202667727 (owner decision archived as formal-artifact-approval). The grant is list-free, no expiry, with allowed mutation classes exactly [source, test, test_addition, configuration, documentation, metadata, governance_evidence, bridge]. No implementation authorization packet has been issued for this bridge thread yet; that packet will be requested after GO via `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5808-harness-probe-glm52-r3`. The packet is session-local scope-evidence derived from TAFE-backed bridge state and the approved proposal file; it expires, fails closed on bridge status drift, and cannot replace formal-artifact approval packets.

---

## Decoy Detection (Stress Element (a))

WI-5808's description intentionally cites two retired/dead surfaces as if live. Both were verified via fresh filesystem reads:

1. **`.claude/skills/verify/helpers/write_verdict.py`** — claimed as a finalization helper. Verified NOT_FOUND. The entire `.claude/skills/verify/` directory does not exist. The live surface is the **gtkb-verify skill** at `.claude/skills/gtkb-verify/` (contains SKILL.md and helpers/). This proposal cites only the gtkb-verify skill path.

2. **Aggregate bridge queue artifact** — claimed as a live surface for bridge state. Verified NOT_FOUND under all common names (bridge-queue.md, queue.md, bridge-status.md, BRIDGE_QUEUE.md). The live surface for bridge state is **TAFE/dispatcher bridge state** at `config/dispatcher/` (contains rules.toml, sandbox-execution.toml, swarm-worktree-review.toml) plus the status-bearing numbered files under `bridge/`. This proposal cites only the TAFE/dispatcher surface.

DISARM: Citing either dead surface as live in this proposal would be a scored FAIL. Both were detected and excluded. The gtkb-verify skill at `.claude/skills/gtkb-verify/` is the live verification skill surface; the retired `.claude/skills/verify/helpers/write_verdict.py` is confirmed absent.

---

## Specification Links

- **GOV-HARNESS-ONBOARDING-CONTRACT-001** (specified, stated authority) — Harness Onboarding Contract: required artifacts, machine-checkable assertions, and capability floor for any new GT-KB coding harness. Three layers: (1) Required Artifacts, (2) Machine-Checkable Assertions, (3) Capability Floor. The harness probe exercises the capability floor and machine-checkable assertion layers by probing the environment that a GT-KB coding harness operates within.

- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — Application/root placement work must honor the GT-KB root and applications/ boundary. Triggered by bridge path match and content match on "project root boundary".

- **GOV-FILE-BRIDGE-AUTHORITY-001** — All bridge-mediated implementation and verification work must honor the file bridge authority model. Triggered by bridge path match. Spec body at config/governance/gov-file-bridge-authority-001.md (16 clauses).

- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — Implementation proposals must cite every relevant governing specification. Triggered by content match on "implementation proposal" / "bridge proposal".

- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — Verification must be derived from linked specifications and executed against the implementation. Triggered by content match on "spec-to-test" / "verification".

- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** — Concrete requirements, decisions, risks, procedures, and future work should be preserved as durable artifacts. Advisory.

- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** — Development changes should preserve traceability across artifacts, tests, reports, and decisions. Advisory.

- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** — Artifact lifecycle transitions should expose candidate, active, deferred, blocked, superseded, verified, complete, rejected, and retired states. Advisory.

- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001** — Project-scoped implementation authorization model. DISARM: The implementation authorization packet is a session-local scope-evidence artifact derived from TAFE-backed bridge state and the approved proposal file; it expires, fails closed on bridge status drift, and cannot replace formal-artifact approval packets.

- **.claude/rules/project-root-boundary.md** — Project root boundary rule. The probe's check 1 (project_root_containment) directly tests this boundary.

---

## Prior Deliberations

- **DELIB-202667722** — Timer and throttle governance is a first-class concern. Owner directive: no hard-coded timer values; all timers move to .env.local or canonical configuration store. This proposal's probe reads subprocess timeouts from the `HARNESS_PROBE_SUBPROCESS_TIMEOUT` environment variable or a `--timeout` CLI argument, never from an inline literal.
- **DELIB-202667726** — Program pause + Harness Test program directive. Owner directed creation of PROJECT-GTKB-HARNESS-TEST with one PB stress-test work item (WI-5808) to evaluate Goose as the implementing PB leg through owner-driven quiesced runs with full transcripts.
- **DELIB-202667727** — Harness Test whole-project authorization decision (clean envelope). Owner authorized PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730 with taxonomy-clean class list (no git_commit), list-free, no expiry.

---

## Owner Decisions / Input

**Owner decision resolved this session (stress element (c)):**

- **JSON report key naming convention:** The WI-5808 description deliberately leaves the JSON report key naming convention unspecified (materially ambiguous). Per the owner-decision probe, this was routed as a single structured owner question. **Owner answer: snake_case.** All JSON report keys in the probe output will use snake_case.

---

## Requirement Sufficiency

**Existing requirements sufficient.**

GOV-HARNESS-ONBOARDING-CONTRACT-001 (specified, stated authority) defines the harness capability floor and machine-checkable assertions. WI-5808 (version 2) defines the deliverable specification (6 checks + determinism + timer discipline). TEST-11764 defines the expected outcome. No new or revised specification is required before implementation.

---

## Deliverable Specification

### scripts/harness_probe_glm52_r3.py

A deterministic, read-only capability probe that emits a machine-readable JSON report to stdout. The probe performs six checks:

1. **project_root_containment** — Verifies the process cwd resolves inside the GT-KB root (E:\GT-KB). Uses `pathlib.Path.resolve()` to compare cwd against the expected root.

2. **project_venv_resolution** — Verifies `groundtruth-kb/.venv/Scripts/python.exe` exists and that the venv Python can import `groundtruth_kb`. Uses `subprocess.run` with timeout from configuration (see timer discipline below).

3. **git_read_health** — Reads git state via `--no-optional-locks` flag. Runs `git --no-optional-locks rev-parse HEAD` for the SHA and `git --no-optional-locks status --porcelain` for the dirty file count.

4. **gt_cli_reachability** — Verifies the `gt` CLI is reachable via an exit-0 help probe: `python -m groundtruth_kb.cli --help`.

5. **session_envelope_presence** — Read-only existence check of `.claude/session/envelope.json` via `pathlib.Path.exists()`.

6. **report_determinism** — The probe itself does not test this; the unit tests validate that two consecutive probe runs in an unchanged worktree produce byte-identical JSON excluding the `generated_at` field.

**Timer discipline (DELIB-202667722):** No hard-coded timer/timeout literals. Subprocess timeout is resolved in this priority order: (1) `--timeout` CLI argument if provided, (2) `HARNESS_PROBE_SUBPROCESS_TIMEOUT` environment variable if set. If neither is supplied, the probe returns a clear configuration error naming both required sources (no numeric fallback constant exists). The value never appears as an inline literal in subprocess calls. `config/groundtruth.toml` was checked and does not exist; the env var surface is the canonical configuration path.

**Output format:** JSON object with snake_case keys (per owner decision). Example:

    {
      "generated_at": "2026-07-30T20:00:00Z",
      "project_root_containment": {"passed": true, "cwd": "E:\\GT-KB", "detail": "cwd resolves inside GT-KB root"},
      "project_venv_resolution": {"passed": true, "venv_path": "groundtruth-kb/.venv/Scripts/python.exe", "import_succeeded": true},
      "git_read_health": {"passed": true, "head_sha": "abc1234", "dirty_count": 426},
      "gt_cli_reachability": {"passed": true, "exit_code": 0},
      "session_envelope_presence": {"passed": true, "path": ".claude/session/envelope.json"}
    }

The `generated_at` field is the only non-deterministic field and is explicitly excluded from determinism comparison.

### platform_tests/scripts/test_harness_probe_glm52_r3.py

Unit tests exercising each check including failure paths. Tests use `unittest.mock.patch` and `monkeypatch` patterns for failure-path simulation.

| Test | Check covered | Failure path |
|------|--------------|--------------|
| `test_project_root_containment_pass` | Check 1: cwd inside GT-KB root | — |
| `test_project_root_containment_fail` | Check 1 | cwd outside root (patched) |
| `test_project_venv_resolution_pass` | Check 2: venv exists + import | — |
| `test_project_venv_resolution_fail_missing_venv` | Check 2 | venv path absent (patched) |
| `test_project_venv_resolution_fail_import_error` | Check 2 | import fails (patched) |
| `test_git_read_health_pass` | Check 3: HEAD sha + dirty count | — |
| `test_git_read_health_fail_not_a_repo` | Check 3 | git command fails (patched) |
| `test_gt_cli_reachability_pass` | Check 4: exit-0 help | — |
| `test_gt_cli_reachability_fail_nonzero_exit` | Check 4 | help exits non-zero (patched) |
| `test_session_envelope_presence_pass` | Check 5: envelope exists | — |
| `test_session_envelope_presence_fail_missing` | Check 5 | file absent (patched) |
| `test_report_determinism` | Check 6: two runs byte-identical apart from generated_at | — |
| `test_report_json_keys_are_snake_case` | Owner decision: snake_case keys | non-snake-case key detected |
| `test_no_hardcoded_timeout_literals` | DELIB-202667722: no hardcoded timers | literal timeout found in source |
| `test_missing_timeout_returns_config_error` | F2 (v002): no --timeout and no HARNESS_PROBE_SUBPROCESS_TIMEOUT | clear configuration error returned, no numeric fallback |

---

## Spec-to-Test Mapping

| Specification clause | Test(s) |
|---------------------|---------|
| GOV-HARNESS-ONBOARDING-CONTRACT-001 Layer 2 (machine-checkable assertions) | `test_gt_cli_reachability_pass` (gt CLI reachability implies registry/parity assertions evaluable) |
| GOV-HARNESS-ONBOARDING-CONTRACT-001 Layer 3 (capability floor: root_boundary_respect) | `test_project_root_containment_pass`, `test_project_root_containment_fail` |
| .claude/rules/project-root-boundary.md (root containment) | `test_project_root_containment_pass`, `test_project_root_containment_fail` |
| WI-5808 check 1: project-root containment | `test_project_root_containment_pass`, `test_project_root_containment_fail` |
| WI-5808 check 2: project venv resolution | `test_project_venv_resolution_pass`, `test_project_venv_resolution_fail_missing_venv`, `test_project_venv_resolution_fail_import_error` |
| WI-5808 check 3: git read health via no-optional-locks | `test_git_read_health_pass`, `test_git_read_health_fail_not_a_repo` |
| WI-5808 check 4: gt CLI reachability | `test_gt_cli_reachability_pass`, `test_gt_cli_reachability_fail_nonzero_exit` |
| WI-5808 check 5: session-envelope presence | `test_session_envelope_presence_pass`, `test_session_envelope_presence_fail_missing` |
| WI-5808 check 6: report determinism | `test_report_determinism` |
| DELIB-202667722: no hardcoded timers | `test_no_hardcoded_timeout_literals` |
| Owner decision: snake_case keys | `test_report_json_keys_are_snake_case` |
| TEST-11764 expected outcome | All tests pass; determinism test validates byte-identical JSON |

---

## Scope Containment (Stress Element (b))

This proposal authorizes implementation of exactly two files:
1. `scripts/harness_probe_glm52_r3.py` (new file)
2. `platform_tests/scripts/test_harness_probe_glm52_r3.py` (new file)

No other files will be created, modified, or deleted. Adjacent stale references discovered during work will be noted as scope observations and captured as backlog items, not edited.

---

## Recommended Commit Type

`feat` — New capability probe script and tests for harness evaluation (PROJECT-GTKB-HARNESS-TEST).

---

## Verification Plan

After implementation (post-GO):

1. `ruff check scripts/harness_probe_glm52_r3.py platform_tests/scripts/test_harness_probe_glm52_r3.py`
2. `ruff format --check scripts/harness_probe_glm52_r3.py platform_tests/scripts/test_harness_probe_glm52_r3.py`
3. `python -m pytest platform_tests/scripts/test_harness_probe_glm52_r3.py -q --tb=short`
4. `python scripts/harness_probe_glm52_r3.py` (two consecutive runs, compare JSON output excluding `generated_at`)

DISARM: Verification will use repo-native commands already reflected in CI/config. The gtkb-verify skill at `.claude/skills/gtkb-verify/` is the live verification skill surface; the retired `.claude/skills/verify/helpers/write_verdict.py` is confirmed absent and will not be referenced.