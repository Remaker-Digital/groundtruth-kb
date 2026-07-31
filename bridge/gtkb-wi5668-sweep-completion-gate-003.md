NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c685e1d2-4271-4679-8ceb-70491ed1d6a9
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Document: gtkb-wi5668-sweep-completion-gate
Version: 003
bridge_kind: implementation_report
Responds to: bridge/gtkb-wi5668-sweep-completion-gate-002.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5668
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_doctor_skill_rename_sweep.py"]

# WI-5668 — Post-Implementation Report: sweep completion-gate doctor check

## Summary

Implemented the GO'd WI-5668 proposal (`-001`, GO at `-002` by Antigravity-C): a deterministic
`gt project doctor` completion gate for the GTKB-SKILL-RENAME-REFERENCE-SWEEP program. Added
`_check_skill_rename_reference_sweep(target)` to `doctor.py`, registered it in the bridge-checks
block, and added `platform_tests/scripts/test_doctor_skill_rename_sweep.py` (4 tests, all pass).
`required=False` (warning-only) per the proposal, so it never hard-blocks an unrelated release while
the multi-slice sweep is in flight.

**LO routing note:** route this verification to Codex-A or Antigravity-C, NOT provider harnesses
D/F/H (their VERIFIED finalizer is broken). See the § Commit Finalization Plan — `doctor.py` is
entangled with an unrelated concurrent change and requires a hunk-patched commit.

## Specification Links (carried forward from -001)

- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — the deterministic completion signal this check realizes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the bridge/verify skill tooling whose canonical references this gate enforces.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — the sweep standing PAUTH.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal/report spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the spec-derived unit test for the check.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — in-root, platform-only (`groundtruth-kb/src`, `platform_tests`); no `applications/<child>` subtree touched.

## Implemented Changes

### `_check_skill_rename_reference_sweep` (doctor.py, after `_check_untracked_terminal_verified_verdicts`)

- Derives the bare pre-rename name set from the current `.claude/skills/gtkb-<name>` dirs (self-maintaining; no hardcoded list; adapts to future renames).
- Scans tracked files via `git grep -n -E` for `skills/<bare>/` and `"skills" / "<bare>"` forms, invoked through `subprocess` directly (not `_run_cmd`) because `git grep` returns exit 1 on no-match, which `_run_cmd` cannot distinguish from an error; exit `>1` maps to `info`.
- Excludes `bridge/`, `RETIRED-*`, `BARRED-*`, `archive/`, `archive-*`, `.gtkb-state/` (append-only / historical / runtime trees that intentionally retain bare references).
- Returns `ToolCheck(required=False)`: `warning` with count + up to 8 sample `path:line` while count > 0; `pass` at 0; `info` when no `.claude/skills/`, no gtkb- dirs, or git unavailable.
- Registered in the `if p.includes_bridge:` checks block, adjacent to the anchor check.

### `platform_tests/scripts/test_doctor_skill_rename_sweep.py` (net-new)

4 tests: warns-while-ref-remains (+ offending path in the message), passes-at-zero, exclusions-honored, self-maintaining-derivation (no gtkb- dirs → info). Seeded references are built from constructed `f"...{bare}..."` strings so the test's own tracked source never literally carries a matchable `skills/<bare>/` segment and cannot inflate a real-repo doctor run.

## Spec-to-Test Mapping

| Concern / Spec | Test / Command | Result |
|---|---|---|
| Warns while refs remain / `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` | `test_warns_while_bare_reference_remains` | PASS |
| Passes at zero | `test_passes_when_no_bare_reference` | PASS |
| Exclusions honored | `test_excluded_trees_do_not_count` | PASS |
| Self-maintaining derivation | `test_self_maintaining_derivation_no_gtkb_dirs` | PASS |
| Code quality / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `ruff check` + `ruff format --check` on both files | PASS |

## Commands Executed

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_doctor_skill_rename_sweep.py -q
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_doctor_skill_rename_sweep.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <same two files>
```

## Observed Results

- `pytest`: **4 passed**.
- `ruff check`: **All checks passed**.
- `ruff format --check`: **2 files already formatted**.

## Commit Finalization Plan (hunk-patch required)

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` carries an **unrelated concurrent change**
  (skill-presence path fixes, ~L3912-4029) from the file-move-rename session — NOT WI-5668. VERIFIED
  finalization MUST **hunk-patch ONLY my two hunks** (the new `_check_skill_rename_reference_sweep`
  function ~L2528 + the single registration line ~L7147), leaving the concurrent change uncommitted.
- `platform_tests/scripts/test_doctor_skill_rename_sweep.py`: net-new, clean — direct include.

## Recommended Commit Type

Recommended commit type: `feat:` — net-new doctor check plus its test (additive completion-enforcement capability; no behavior change to existing checks).

## Owner Decisions / Input

- Owner AUQ 2026-07-24 (session `c58a8564-bed2-41d4-851b-075b84e86797`, archived as `DELIB-202667193`): "full self-driving harness," which explicitly includes a mechanical completion gate that stays loud until the sweep is done; owner then directed "kick off WI-5668."
- Continuation directive (session `c685e1d2-4271-4679-8ceb-70491ed1d6a9`, 2026-07-24): advance the highest-priority actionable slice WI under the sweep PAUTH via the normal bridge protocol.

## Prior Deliberations

- `DELIB-202667193` — owner decisions establishing the self-driving harness and this completion gate.
- `DELIB-202667105` (rollout v003 GO) / `DELIB-202667106` (rollout NO-GO) — the authoritative gtkb- rename this gate enforces.
- `DELIB-FAB19-REMEDIATION-20260610` — deterministic hygiene-detector expansion precedent (owner-approved detectors wired into the health surface); this check follows that pattern.

## Root-Boundary / In-Root Placement

All changed paths are within `E:\GT-KB` (`groundtruth-kb/src`, `platform_tests`). Platform-only; no `applications/<child>` subtree touched.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
