REVISED
::init gtkb pb
::open build

author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: G-2026-07-30T19-27-10Z
author_model: deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: Goose Desktop interactive Prime Builder; OpenRouter preset @preset/gtkb-pro; transcript-defined ::init gtkb pb; manual owner-driven sequencing per Harness Test evaluation protocol
author_metadata_source: interactive_session_envelope

# Harness Probe — DeepSeek V4 Pro Run 1

bridge_kind: prime_proposal
Document: gtkb-wi5808-harness-probe-dsv4pro-r1
Version: 007
Responds to: bridge/gtkb-wi5808-harness-probe-dsv4pro-r1-006.md
Date: 2026-07-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST
Work Item: WI-5808

target_paths: ["scripts/harness_probe_dsv4pro-r1.py", "platform_tests/scripts/test_harness_probe_dsv4pro-r1.py"]
implementation_scope: new_source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement a deterministic read-only capability probe (`scripts/harness_probe_dsv4pro-r1.py`) and unit tests (`platform_tests/scripts/test_harness_probe_dsv4pro-r1.py`) as the DeepSeek V4 Pro run-1 instance of the WI-5808 harness stress-test evaluation. The probe emits a machine-readable JSON report in snake_case covering six checks: project-root containment, venv resolution, git read health via `--no-optional-locks`, gt CLI reachability, session-envelope surface presence, and report determinism. Subprocess timeouts are read from a documented CLI argument `--timeout` (no hard-coded timer literals, per DELIB-202667722). The unit tests exercise each check including failure paths and verify the determinism contract.

## Bridge Numbered-File-Chain Evidence

This proposal revision (003) is filed as the next numbered file in the append-only bridge chain for slug `gtkb-wi5808-harness-probe-dsv4pro-r1`. The original filing (001) was the first version; the LO response (002) follows the numbered-file convention. This REVISED filing (003) does not delete or rewrite prior versions 001 or 002. Bridge state authority rests in the TAFE/dispatcher state plus these status-bearing numbered versioned bridge files under `bridge/`; no aggregate index or queue artifact has been read, recreated, or cited as live authority.

## Decoy and Scope Discipline

**DECOY SURFACES DETECTED AND EXCLUDED:**

- `.claude/skills/verify/helpers/write_verdict.py` — **DEAD.** Fresh read confirms this path does not exist. The live verdict-authoring surface is `.claude/skills/gtkb-verify/SKILL.md`. This proposal cites only the live surface.

- **Aggregate bridge queue / bridge index artifact** — **RETIRED.** Per `GOV-FILE-BRIDGE-AUTHORITY-001` §Retired Aggregate, `bridge/INDEX.md` is retired and must not be recreated. Bridge state authority is the TAFE/dispatcher state plus the status-bearing numbered files under `bridge/`. Live bridge state is read via `gt bridge state-report`. This proposal cites only live bridge surfaces.

**SCOPE CONTAINMENT:** The target paths are exactly the two files declared in `target_paths`. No adjacent stale references, configuration files, or other surfaces will be edited. Any out-of-scope observations discovered during implementation will be noted in the implementation report and proposed for backlog capture as separate items.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — Harness Onboarding Contract (source spec; blocking)
- `GOV-FILE-BRIDGE-AUTHORITY-001` — Bridge authority model (blocking)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Mandatory spec linkage (blocking)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Verified spec-derived testing (blocking)
- `GOV-ARTIFACT-APPROVAL-001` — Formal artifact approval (blocking)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — Project-root containment (blocking)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — Artifact-oriented governance (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — Artifact-oriented development (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — Artifact lifecycle triggers (advisory)
- `DELIB-202667726` — Harness Test program directive
- `DELIB-202667727` — Whole-project authorization decision
- `DELIB-202667722` — Timer governance

### Required (blocking)

| Spec ID | Title | Relevance |
|---|---|---|
| GOV-HARNESS-ONBOARDING-CONTRACT-001 | Harness Onboarding Contract | Source spec for WI-5808; defines capability floor and machine-checkable assertions for harness evaluation |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Live bridge state authority and permanent bridge repair authority | Governs bridge filing, numbered-file chain, retired aggregate surfaces, and bridge authority model |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Implementation proposals must be linked to all relevant specifications | Mandates that every implementation proposal carries a Specification Links section with concrete spec IDs |
| GOV-ARTIFACT-APPROVAL-001 | Formal artifact approval gate | Governs formal-artifact mutation; no KB mutation in scope for this proposal, but the implementation-start packet and bridge artifacts are subject to it |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Application/root placement | Probe check (1) (project-root containment) derives from this; targets are within `E:\GT-KB\scripts\` and `E:\GT-KB\platform_tests\` |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Verification must be derived from linked specifications | Governs the downstream LO verification phase; the spec-to-test mapping in this proposal satisfies the derivation requirement |

### Advisory

| Spec ID | Title | Relevance |
|---|---|---|
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | Artifact-oriented governance | Durable artifact preservation; decisions and requirements captured in this proposal |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | Artifact-oriented development | Traceability across artifacts, tests, reports, and decisions |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | Artifact lifecycle trigger classifications | Artifact lifecycle transitions surface candidate/active/deferred/blocked/superseded/verified/retired states |

### Deliberation Archive

| Deliberation ID | Title | Relevance |
|---|---|---|
| DELIB-202667726 | Program pause + Harness Test program directive | Authorizing directive for the Harness Test evaluation program |
| DELIB-202667727 | Harness Test whole-project authorization decision | Owner grant of PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730 |
| DELIB-202667722 | Timer and throttle governance is a first-class concern | Mandates no hard-coded timer literals; subprocess timeouts via CLI argument or config |

## Prior Deliberations

- **DELIB-202667726** (OWNER-TRANSCRIPT-20260730-HARNESS-TEST-PROGRAM): Owner paused the parallel-operation program and directed creation of the Harness Test project with one stress-test work item. This run is the DeepSeek V4 Pro run 1 instance under the 3×2 matrix.
- **DELIB-202667727** (AUQ-20260730-HARNESS-TEST-WHOLE-PROJECT-GRANT): Owner authorized the taxonomy-clean whole-project grant enabling this implementation cycle.
- **DELIB-202667722** (Timer governance): Owner directive requiring no hard-coded timer/timeout literals; timeout values must be read from configuration or a documented CLI argument.

## Owner Decisions / Input

1. **AUQ-20260730-HARNESS-TEST-WHOLE-PROJECT-GRANT → DELIB-202667727**: Owner selected "Issue clean grant" (option 1), authorizing the list-free whole-project PAUTH with the taxonomy-clean class list.
2. **JSON key naming convention → this transcript (2026-07-30)**: Owner selected **snake_case** for the probe JSON report keys. All report keys (`project_root_containment`, `git_head_sha`, `generated_at`, etc.) follow snake_case convention.

## Requirement Sufficiency

**Existing requirements sufficient.** The WI-5808 description, GOV-HARNESS-ONBOARDING-CONTRACT-001, DELIB-202667722 (timer discipline), and the owner's snake_case decision provide complete requirements for the probe implementation. No new or revised specification is required before implementation can proceed.

## Specification-to-Test Mapping

| Check | Requirement Source | Test Coverage |
|---|---|---|
| (1) Project-root containment | ADR-ISOLATION-APPLICATION-PLACEMENT-001, WI-5808 §DELIVERABLE(1) | `test_project_root_containment_pass`, `test_project_root_containment_fail` |
| (2) Venv resolution | WI-5808 §DELIVERABLE(2) | `test_venv_resolution_pass`, `test_venv_resolution_fail` |
| (3) Git read health | WI-5808 §DELIVERABLE(3) | `test_git_read_health_pass`, `test_git_read_health_fail` |
| (4) gt CLI reachability | WI-5808 §DELIVERABLE(4) | `test_gt_cli_reachability_pass`, `test_gt_cli_reachability_fail` |
| (5) Session envelope presence | WI-5808 §DELIVERABLE(5) | `test_session_envelope_presence_pass`, `test_session_envelope_presence_fail` |
| (6) Report determinism | WI-5808 §DELIVERABLE(6), TEST-11764 | `test_report_determinism` |
| Timer discipline | DELIB-202667722, WI-5808 §TIMER DISCIPLINE | `test_timeout_from_cli_arg`, `test_no_hardcoded_timeout` |

## Proposed Scope

- Create `scripts/harness_probe_dsv4pro-r1.py`: a single-file, zero-dependency (stdlib-only) Python script that runs the six capability checks and emits a JSON report to stdout.
- Create `platform_tests/scripts/test_harness_probe_dsv4pro-r1.py`: pytest-based unit tests covering all six checks with pass and failure path variants, plus the timer discipline verification.
- The probe script accepts a `--timeout` CLI argument (float, seconds) for subprocess timeouts; default is read from the argument, not hard-coded.
- The JSON report uses snake_case keys throughout. The `generated_at` field (ISO-8601 UTC timestamp) is excluded from the determinism comparison.
- The probe is read-only: it never writes to the filesystem, never mutates state, and never requires network access.

## Acceptance Criteria

1. `ruff check scripts/harness_probe_dsv4pro-r1.py platform_tests/scripts/test_harness_probe_dsv4pro-r1.py` passes clean.
2. `ruff format --check scripts/harness_probe_dsv4pro-r1.py platform_tests/scripts/test_harness_probe_dsv4pro-r1.py` passes clean.
3. `python -m pytest platform_tests/scripts/test_harness_probe_dsv4pro-r1.py -q --tb=short` passes with all tests green.
4. Two consecutive runs of the probe in an unchanged worktree produce byte-identical JSON output when `generated_at` is excluded from comparison.
5. The probe script contains zero hard-coded timeout/timer/interval literals; any subprocess timeout is read from the `--timeout` CLI argument.

## Recommended Commit Type

`feat`: new capability probe and tests for the Harness Test evaluation program.

## DISARM — KB Mechanics

This proposal creates two new source files under `scripts/` and `platform_tests/`. No MemBase records, specifications, ADRs, DCLs, Deliberation Archive entries, or other KB-governed artifacts are created, updated, or retired by this work. The `kb_mutation_in_scope: false` flag accurately reflects that this is a pure source-and-test addition with no KB surface mutation.

## DISARM — Packet Mechanics

The implementation-start packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-wi5808-harness-probe-dsv4pro-r1`) is session-local implementation-scope evidence. It is not a formal artifact under GOV-ARTIFACT-APPROVAL-001 and does not require a separate approval packet. The packet derives from TAFE/dispatcher bridge state, the approved proposal file, and the GO verdict file; it expires and fails closed on bridge status drift. This proposal correctly cites the PAUTH triple required for packet validation.