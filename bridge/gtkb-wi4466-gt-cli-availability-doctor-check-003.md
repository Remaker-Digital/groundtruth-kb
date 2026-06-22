NEW

bridge_kind: implementation_report
Document: gtkb-wi4466-gt-cli-availability-doctor-check
Version: 003
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: a460ee9e-4606-4e64-bd03-cd7eae14bdef
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder (resolved via ::init gtkb pb, harness B); explanatory output style; autonomous project-completion loop; model claude-opus-4-8[1m]
Date: 2026-06-22 UTC

Project Authorization: PAUTH-PROJECT-GTKB-COMMAND-SURFACE-COMPLETION-2026-06-22
Project: PROJECT-GTKB-COMMAND-SURFACE
Work Item: WI-4466
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/checks/gt_cli_availability.py", "platform_tests/scripts/test_check_gt_cli_availability.py"]
implementation_scope: source, test
requires_review: false
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

# WI-4466 Implementation Report: deterministic gt CLI availability doctor check

Post-implementation report for the GO at `bridge/gtkb-wi4466-gt-cli-availability-doctor-check-002.md`. Implements the -001 proposal exactly as approved — no scope change.

## Summary of work performed

Added a registered doctor check (ADR-REGISTRY-DISCOVERY-001) that gives `gt` a deterministic three-state availability verdict. Implementation-start packet `sha256:0c5bbefacd163ab1f3b7cb0fd4ad291778f630615c61fa35b48c0657bac7a39f` was created from the GO before mutation; writes were confined to the two approved `target_paths`. All GO boundary conditions are preserved: read-only check, no PATH mutation, no launcher placement, no install/bootstrap wiring, no subprocess launch, and **no edit to `doctor.run_doctor`** (the registry auto-discovers the new module).

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/project/checks/gt_cli_availability.py` — NEW. `@register_check("gt_cli_availability")` `check_gt_cli_availability(target) -> ToolCheck`: `pass` when `gt` is on PATH; `warning` when not on PATH but the canonical in-root venv launcher exists; `fail` when neither. Helper `_venv_gt_path(target, platform=None)` resolves the venv launcher path identically to `scripts/install_gt_path_shim.resolve_venv_gt_exe`.
- `platform_tests/scripts/test_check_gt_cli_availability.py` — NEW. 6 tests.

No other files were modified. No edit to `doctor.py`, no KB mutation, no config change.

## Specification Links (carried forward from -001)

- **GOV-STANDING-BACKLOG-001** — WI-4466 backlog authority; single-WI scope (`CLAUSE-VISIBILITY-BULK-OPS` `not_applicable`).
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — implemented under active `PAUTH-PROJECT-GTKB-COMMAND-SURFACE-COMPLETION-2026-06-22` (`source` + `test_addition`); the begin packet validated PAUTH coverage of WI-4466.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** + `.claude/rules/project-root-boundary.md` — both files in-root; the check resolves the in-root venv launcher relative path (`groundtruth-kb/.venv/Scripts/gt.exe` on Windows, `groundtruth-kb/.venv/bin/gt` on POSIX) and reads only.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — filed through the file bridge numbered chain.
- **ADR-REGISTRY-DISCOVERY-001** — the check is added through the dynamic registry; no `doctor.run_doctor` edit.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — links carried forward concretely.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — spec-to-test mapping + executed evidence below.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory).

## Spec-to-Test Mapping (all executed; all PASS)

| Acceptance criterion / GO-required evidence (WI-4466) | Test | Result |
|---|---|---|
| `gt` on PATH -> deterministic pass naming the path | `test_gt_on_path_passes` | PASS |
| Not on PATH + canonical in-root venv fallback present -> warning (functional via fallback) | `test_venv_fallback_warns` | PASS |
| Genuinely unavailable (neither) -> fail (missing CLI caught) | `test_unavailable_fails` | PASS |
| Dynamic registry discovery of `gt_cli_availability` | `test_check_is_registered` | PASS |
| Fallback path consistent with `scripts.install_gt_path_shim.resolve_venv_gt_exe` (no drift) | `test_fallback_path_matches_shim_generator` | PASS |
| Check is `required=False` (advisory developer-environment quality) | `test_check_is_advisory_required_false` | PASS |

## Verification Evidence (exact commands + observed results)

Run with the canonical venv interpreter (`groundtruth-kb/.venv/Scripts/python.exe`), per the GO's expectations:

```text
... -m pytest platform_tests/scripts/test_check_gt_cli_availability.py -q --tb=short
  => 6 passed, 1 warning in 7.06s
     (the single warning is the pre-existing repo-wide "Unknown config option: asyncio_mode" pytest warning, unrelated)

... -m ruff check groundtruth-kb/src/groundtruth_kb/project/checks/gt_cli_availability.py platform_tests/scripts/test_check_gt_cli_availability.py
  => All checks passed!

... -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/checks/gt_cli_availability.py platform_tests/scripts/test_check_gt_cli_availability.py
  => 2 files already formatted
```

Live integration confirmation (check invoked against the real project root): returned `status=pass`, `found=True`, message "gt on PATH at <user-PATH launcher under %USERPROFILE%\.local\bin\gt.CMD>". On this host `gt` resolves on PATH via a user-PATH launcher (the WI-4530-class shim), so the optimal `pass` path is exercised end-to-end; the `warning` and `fail` states are covered deterministically by the monkeypatched unit tests above.

## Advisory Note Response (ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001)

The GO asked the report to cite or explain the applicability-preflight's missing advisory spec `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`. It is **not citable because the spec row is genuinely absent from MemBase** — the applicability registry references the ID, but no such artifact exists to link. It is advisory-only and does not gate. The artifact-oriented-governance intent is satisfied by the two cited present specs **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** and **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001**: this slice codifies a per-session-rediscovered failure mode into a durable, tracked, machine-checkable invariant.

## Prior Deliberations (carried forward)

- `DELIB-20263239` — WI-4530 gt CLI PATH shim generator GO (the parent; this implements its deferred verification follow-on).
- `DELIB-CMD-SURFACE-RETIRE-DIRECTIVE-20260622` — owner directive authorizing the work.
- `DELIB-20263464` — WI-4395 sibling command-surface disposition (shared framing).
- `DELIB-20261489` — Discoverability CLI Slice 2 (confirms no scope overlap).

## Owner Decisions / Input

Authorized by durable owner-decision evidence; no new AskUserQuestion required.

- `DELIB-CMD-SURFACE-RETIRE-DIRECTIVE-20260622` — owner directive (session a460ee9e, 2026-06-22) to drive PROJECT-GTKB-COMMAND-SURFACE to VERIFIED/retired, recorded in `PAUTH-PROJECT-GTKB-COMMAND-SURFACE-COMPLETION-2026-06-22`.

## Recommended Commit Type

`feat:` — net-new capability (a registered doctor check + regression suite). Matches the diff (two new files, no repair of existing in-repo code).

## Risk / Rollback

- **Risk: low.** Net-new read-only registered check + tests. No PATH mutation, no subprocess launch, no install step, no out-of-root access, no `doctor.py` edit, no KB mutation. `required=False` + `warning` (not `fail`) when the venv fallback is present, so a normal checkout does not turn `gt project doctor` red.
- **Rollback:** delete the two new files; the registry auto-discovery means removal needs no `doctor.py` edit.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
