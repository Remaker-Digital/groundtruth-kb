REVISED
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T13-50-51Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal Revision — WI-5668 skill-rename sweep completion gate

bridge_kind: prime_proposal
Document: gtkb-wi5668-skill-rename-sweep-completion-gate
Version: 005
Date: 2026-07-24 UTC
Responds to: bridge/gtkb-wi5668-skill-rename-sweep-completion-gate-004.md

Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5668

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor.py", "scripts/release_candidate_gate.py", "platform_tests/scripts/test_release_candidate_gate.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision resolves both findings in version 004 without expanding the four-path implementation boundary. A single deterministic evaluator continues to inventory active bare legacy skill-path references, but its consumers now have deliberately distinct severities: project doctor reports a visible non-blocking warning while the release-candidate gate exits non-zero until the count reaches zero. The revision also replaces the known non-executable full-file release-gate command with exact new test selectors that exercise the new lane under controlled fixtures.

## Finding-by-Finding Resolution

### P1 — preserve WARN doctor and make release gate the blocking surface

`DELIB-20260724-WI5668-SEVERITY-CONTRACT` records the owner choice: `WARN doctor + fail release gate`. The new doctor check is named `skill-rename reference sweep completion`, returns `status="warning"` with the stable finding count and up to ten ordered samples when findings are non-zero, and returns `status="pass"` at zero. It is not marked required and therefore does not change the doctor profile's overall outcome.

`scripts/release_candidate_gate.py` is the enforcement owner. It calls the same exported evaluator from `groundtruth_kb.project.doctor` before the Python-test lane. A non-zero evaluator result raises `GateFailure` containing the stable count; zero emits `PASS skill-rename reference sweep completion (0 findings)` and permits the remaining release lanes. No second scanner or severity reinterpretation is introduced.

### P2 — executable specification-derived release-gate evidence

The implementation adds these exact, controlled-fixture tests in `platform_tests/scripts/test_release_candidate_gate.py`:

- `test_skill_rename_sweep_gate_passes_when_evaluator_empty`
- `test_skill_rename_sweep_gate_fails_with_stable_count`
- `test_main_runs_skill_rename_sweep_lane_before_python_tests`

Their acceptance command is:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_release_candidate_gate.py::test_skill_rename_sweep_gate_passes_when_evaluator_empty platform_tests/scripts/test_release_candidate_gate.py::test_skill_rename_sweep_gate_fails_with_stable_count platform_tests/scripts/test_release_candidate_gate.py::test_main_runs_skill_rename_sweep_lane_before_python_tests -q --tb=short
```

The broader `platform_tests/scripts/test_release_candidate_gate.py` baseline currently has two unrelated failures because `scripts/windows_no_window_spawn_audit.py` parses `.goose/skills/gtkb-verify/helpers/writer_script.py` with a U+FEFF syntax error. Neither path is in this proposal. The report will record that baseline separately and will not claim a full-file pass.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5668 and `DELIB-202667193` require a mechanical, self-driving completion signal. `DELIB-20260724-WI5668-SEVERITY-CONTRACT` resolves the previously ambiguous severity contract without changing the sweep's ownership boundary or creating a new requirement.

## In-Root Placement Evidence

Every declared source and test target is under `E:\GT-KB`. The release gate is the in-root GT-KB control surface; no Agent Red checkout, external service, deployment configuration, or workflow-YAML edit is involved.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires the numbered revision, independent review, live GO, claim, and implementation-start gate.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — preserve the detector contract and evidence as durable artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires concrete target paths, sufficient requirements, and spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the executed doctor and release-lane evidence below before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — binds the active PAUTH, project, WI, and four target paths.
- `GOV-STANDING-BACKLOG-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — retain WI-5668 as a visible project completion condition through NO-GO → REVISED → GO → verification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — retains the complete implementation and verification surface inside GT-KB.

## Prior Deliberations

- `DELIB-202667193` — owner decision creating the self-driving skill-rename completion gate and its historical/runtime exclusions.
- `DELIB-20260724-WI5661-PROCESS-AUTHORIZATION` — authorizes WI-5668's governed lifecycle under the active bounded project authorization.
- `DELIB-20260724-WI5668-SEVERITY-CONTRACT` — owner selected `WARN doctor + fail release gate` to resolve version 004 P1.
- `bridge/gtkb-wi5668-skill-rename-sweep-completion-gate-004.md` — prior NO-GO whose P1/P2 corrections are addressed above.

## Owner Decisions / Input

- `DELIB-202667193` requires a mechanical completion signal that remains loud until the sweep reaches zero.
- `DELIB-20260724-WI5661-PROCESS-AUTHORIZATION` authorizes normal bridge processing of WI-5668 under the project PAUTH.
- `DELIB-20260724-WI5668-SEVERITY-CONTRACT` authorizes the specific `WARN doctor + fail release gate` severity split. No additional owner decision is claimed.

## Deterministic Evaluator Contract

The evaluator accepts a project root and returns normalized findings (`path`, `line`, `alias`, `matched_text`) in normalized-path, line, and alias order. It derives aliases from `config/agent-control/skill-rename-map.toml`: each `dir` and `canonical_name` with exactly one leading `gtkb-` removed, plus each non-empty `registry_old_name`; values are de-duplicated and sorted.

It enumerates tracked files using `git -C <target> ls-files -z`, normalizes separators to `/`, and scans only the path-segment grammar `(?:^|[\\\"'`(=:\\s])(?:\\.(?:claude|codex|agent|agents)/)?skills/<legacy-alias>(?=$|[/.\\\"'`),:\\s])`. It excludes `bridge/`, `.gtkb-state/`, path segments beginning `RETIRED-` or `BARRED-`, path segments exactly `archive` or `archives`, and `config/agent-control/skill-rename-map.toml`. No other exclusions are permitted. The doctor and release gate consume this one evaluator.

## Proposed Scope

1. Add the exported evaluator and an advisory doctor check in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`.
2. Add doctor fixture tests for positive detection, exact exclusions, canonical-path and prose false-positive rejection, deterministic ordering, warning-with-count at non-zero, and pass at zero.
3. Add the release-gate consumer in `scripts/release_candidate_gate.py`, failing with the evaluator count before the Python-test lane.
4. Add the three exact release-gate tests named above in `platform_tests/scripts/test_release_candidate_gate.py`.

## Explicit Non-Scope

- Repairing any reference detected by the evaluator; WI-5661 through WI-5667 own those paths.
- Editing adapters, templates, rules/config mirrors, fixture-golden trees, bridge audit history, runtime state, release workflow YAML, or the unrelated U+FEFF baseline defect.
- Scanning untracked files or retained historical material.

## Pre-Filing Preflight Subsection

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5668-skill-rename-sweep-completion-gate --content-file <this draft>` passed with `missing_required_specs: []`, `missing_advisory_specs: []`, and no blocking errors. Candidate packet: `sha256:65a9b2db9b78e56237ce7aa0e673abfb255e908d1bc599eb14119ef4d5a0c7cb`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5668-skill-rename-sweep-completion-gate --content-file <this draft>` passed: four must-apply clauses, zero evidence gaps, zero blocking gaps.

## Specification-Derived Verification Plan

| Specification | Verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Review target paths, independent GO, claim, and implementation-start packet. | Only the four declared paths are modified. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Focused `groundtruth-kb/tests/test_doctor.py` run. | Fixture cases preserve a durable deterministic control. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate and live applicability/clause preflights. | No required/advisory gaps or blocking clause gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused doctor suite plus the three exact release-gate selectors. | Warning/pass and blocking release behavior are both executed. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | PAUTH and implementation-start validation. | PAUTH, project, WI, and four-path scope stay aligned. |
| `GOV-STANDING-BACKLOG-001` | `gt backlog list --id WI-5668 --json` plus evaluator tests. | The open WI has a visible warning and release-blocking completion signal. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Path review and focused tests from the GT-KB root. | No external/adopter dependency is introduced. |

Before filing the implementation report, run `ruff check` and `ruff format --check` on every changed Python source and test file.

## Acceptance Criteria

1. The doctor and release gate call one evaluator with no duplicate scanning logic.
2. Non-zero findings produce a doctor warning with stable count/samples and a non-zero release-gate outcome with the same count.
3. Zero findings produce explicit pass output on both surfaces.
4. The exact alias, grammar, enumerator, exclusions, ordering, and false-positive contract is covered by focused tests.
5. The three named release-gate tests pass independently of the known full-file baseline failure.
6. Only the declared four paths are attributed to this slice.

## Risk and Rollback

The risk is over-broad detection causing false release blocks. The map-driven aliases, exact grammar, auditable exclusions, controlled fixtures, and shared evaluator bound it. Roll back only the four declared paths under new governed authority, then rerun both focused suites. Bridge files and owner decisions remain append-only.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/tests/test_doctor.py`
- `scripts/release_candidate_gate.py`
- `platform_tests/scripts/test_release_candidate_gate.py`

## Recommended Commit Type

`feat`
