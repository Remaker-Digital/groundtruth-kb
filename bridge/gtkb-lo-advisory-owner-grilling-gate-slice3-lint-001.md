NEW

# gtkb-lo-advisory-owner-grilling-gate-slice3-lint - Implement Advisory Grilling Gate Lint

bridge_kind: prime_proposal
Document: gtkb-lo-advisory-owner-grilling-gate-slice3-lint
Version: 001
Author: Codex Prime Builder
Date: 2026-06-13T06:45:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: current Codex desktop session
author_model: GPT-5
author_model_version: 2026-06 runtime
author_model_configuration: Codex desktop, danger-full-access, approval policy never

Project Authorization: PAUTH-PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001-LO-ADVISORY-OWNER-GRILLING-GATE-IMPLEMENTATION
Project: PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001
Work Item: WI-3446

target_paths: ["scripts/advisory_grilling_gate_lint.py", "platform_tests/scripts/test_advisory_grilling_gate_lint.py", ".claude/settings.json", ".codex/hooks.json"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement Slice 3 of the LO Advisory Owner-Grilling Gate project: create `scripts/advisory_grilling_gate_lint.py`, register it as a warning-phase Stop hook for Claude and Codex, and add focused platform tests. The current `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` assertion run is failing 0/4; read-back shows those assertions grep real `INSIGHTS-*.md` advisory files for advisory-mode/gate markers, not the lint script itself.

This proposal is filed against the canonical project/work item (`PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001`, `WI-3446`) and active PAUTH. It should satisfy the implementation substance behind the later architecture-audit duplicate row `WORKLIST-ARCHITECTURE-IMPROVEMENT-P3-ADVISORY-GRILLING-GATE` once verified, but this implementation does not mutate that duplicate row. It does not implement Slice 2 (`WI-3445`) skill/checklist updates.

## Specification Links

- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` - states the owner-grilling gate principle for adopt/adapt Loyal Opposition advisories.
- `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` - specifies the deterministic advisory-shape detection, required gate heading, gate content enumeration, warning-phase behavior, and owner-waiver path implemented by this slice.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the work proceeds only through bridge review, GO, implementation-start authorization, post-implementation report, and Loyal Opposition verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links all governing requirements and explicitly distinguishes canonical `WI-3446` from the architecture-audit duplicate row.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the header includes PAUTH, project, work item, and inline JSON `target_paths`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification is derived from the linked GOV/DCL requirements and includes command evidence plus DCL assertion rerun.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - active PAUTH bounds mutation classes to script creation, hook config registration, and test creation.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the active PAUTH includes `WI-3446`, governing specs, allowed mutation classes, and forbidden operations.
- `GOV-STANDING-BACKLOG-001` - `WI-3446` is the durable standing-backlog item for Slice 3; the architecture P3 row is a later audit duplicate, not a replacement authority.

## Prior Deliberations

- `DELIB-S364-LO-ADVISORY-GRILLING-GATE-PROJECT-AUTH` - owner authorized the project and PAUTH covering all three slices, including `WI-3446`.
- `INTAKE-e226b05a` - original requirement intake for the LO Advisory Owner-Grilling Gate.
- `DELIB-20263159` - current-session owner directive/pacing record; included only for session context because it authorized continuing PB-actionable bridge/backlog work with a 3-minute inter-project pause.

## Owner Decisions / Input

No new owner decision is required before proposal review. The governing owner authorization already exists in `DELIB-S364-LO-ADVISORY-GRILLING-GATE-PROJECT-AUTH`, and active PAUTH `PAUTH-PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001-LO-ADVISORY-OWNER-GRILLING-GATE-IMPLEMENTATION` includes `WI-3446`, `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`, and `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001`.

The current owner session directive authorizes continuing PB-actionable backlog/bridge work, and the requested 3-minute pacing pause was completed before this proposal work began.

## Requirement Sufficiency

Existing policy requirements are sufficient for the warning-phase lint implementation. `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` defines the policy, `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` defines the machine-checkable contract, and `WI-3446` defines the Slice 3 implementation surface: script, warning-phase hook registration, and tests.

Important limitation for LO review: the live DCL assertion definitions are shallow repository-content checks over `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md`, not executable checks of the lint script. This proposal verifies the DCL contract through direct lint tests and hook registration. It does not claim that `gt assert --spec DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` will necessarily become green unless a real compliant advisory report exists or the DCL assertions are separately amended under formal artifact governance.

## Proposed Implementation

After Loyal Opposition GO and a successful implementation-start packet:

1. Add `scripts/advisory_grilling_gate_lint.py`.
2. Implement markdown scanning for `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` plus explicit file arguments for tests.
3. Detect advisory-shape files only when a `Mode: advisory report` variant appears in the first 20 lines and a classification section declares exactly one of `adopt`, `adapt`, `reject`, `defer`, or `monitor`.
4. For `adopt`/`adapt`, emit warning-phase findings when `## Required Prime Builder Owner-Grilling Gate` is missing or when the gate section lacks the three required content enumerations.
5. Honor `Grilling-gate waiver: <reason>` only when present under the classification/disposition section, and append waiver observations to `.gtkb-state/advisory-grilling-gate/waivers.jsonl`.
6. Register the script in the Claude and Codex Stop hooks as warning-phase, fail-open enforcement. Phase 2 blocking behavior remains out of scope and requires separate owner-approved bridge work.
7. Add `platform_tests/scripts/test_advisory_grilling_gate_lint.py` covering all five classifications, adopt/adapt pass/fail cases, non-advisory false positives, waiver behavior, and CLI/hook fail-open behavior.

## Specification-Derived Verification Plan

| Specification / Contract | Verification |
| --- | --- |
| `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` | `python -m pytest platform_tests/scripts/test_advisory_grilling_gate_lint.py -q --tb=short` covers advisory shape, classification, required gate heading, gate content enumeration, and waiver handling. |
| `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` | `python -m groundtruth_kb.cli assert --spec DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` is rerun and reported as diagnostic evidence. If it remains red, the post-implementation report must explicitly show whether the failure is caused by the DCL's real-report grep assertions rather than lint behavior. |
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` | Tests verify adopt/adapt advisories require the Prime Builder owner-grilling gate while reject/defer/monitor do not require it. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `python -m groundtruth_kb.cli projects authorizations PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001 --json` shows active PAUTH includes `WI-3446` and the allowed mutation classes. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-advisory-owner-grilling-gate-slice3-lint --json` returns `preflight_passed: true` and `missing_required_specs: []`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Phantom-spec sweep over every cited `GOV-*`/`DCL-*` id returns existing live specification rows. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-lo-advisory-owner-grilling-gate-slice3-lint --format json` reports no INDEX drift. |
| Code quality | `python -m ruff check scripts/advisory_grilling_gate_lint.py platform_tests/scripts/test_advisory_grilling_gate_lint.py` and `python -m ruff format --check scripts/advisory_grilling_gate_lint.py platform_tests/scripts/test_advisory_grilling_gate_lint.py` pass. |

## Current Evidence Snapshot

- `scripts/advisory_grilling_gate_lint.py` does not exist.
- `python -m groundtruth_kb.cli assert --spec DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` currently reports 1 spec with assertions, 0 passed, 1 failed, 0 skipped; the four nested assertion checks fail with zero matches across 778 files.
- Active PAUTH `PAUTH-PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001-LO-ADVISORY-OWNER-GRILLING-GATE-IMPLEMENTATION` includes `WI-3446`, allows `script_create`, `hook_config_registration`, and `test_create`, and forbids out-of-scope edits, credential changes, and release/deploy.
- `bridge/gtkb-lo-advisory-owner-grilling-gate-009.md` VERIFIED Slice 1 only; it explicitly left Slice 2/WI-3445 and Slice 3/WI-3446 open.

## Risk / Rollback

Primary risk is false positives in advisory detection. Mitigation: require both the mode header and classification section before treating a file as advisory-shaped; tests cover non-advisory files and all terminal classification states. Hook registration is warning-phase and fail-open, so a defect should surface without blocking authoring.

Second risk is verification ambiguity: the current MemBase assertion definitions may stay red even after the lint behavior is implemented correctly, because they grep live advisory report content rather than the script or tests. Mitigation: the implementation report must separate direct lint verification from `gt assert` diagnostic output. If LO requires live DCL assertion green as a condition of VERIFIED, the likely follow-on is a separate formal-artifact bridge to amend the DCL assertions or add an authentic advisory fixture/report under the appropriate report workflow. Rollback is a single revert of the script, tests, and two hook config edits.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-lo-advisory-owner-grilling-gate-slice3-lint` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`feat`: this adds a new deterministic lint and hook surface with tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
