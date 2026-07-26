ADVISORY
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: dbc5c1cd-13f2-4ff8-81a5-a80c06799bae
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: governance_advisory
Document: gtkb-wi5688-doctor-skill-rename-sweep-crash
Version: 001
Author: Prime Builder (Claude) — owner-directed advisory; advisories are role-agnostic per DELIB-202667454
Date: 2026-07-25

## Source

Session `dbc5c1cd-13f2-4ff8-81a5-a80c06799bae` (2026-07-25), Prime Builder (Claude).
Work Item: **WI-5688** (origin=defect, priority P1, component=doctor).

Owner AUQ decision (2026-07-25): route this crash to WI-5441/Codex so the repair
lands inside WI-5441's existing `doctor.py` scope rather than as a competing edit.

Related bridge threads:

- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-004.md` — the
  active `GO` whose `target_paths` already include
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py`.
- `bridge/gtkb-wi5678-genericize-advisory-role-framing-008.md` — `NO-GO` finding
  F1, which is blocked by exactly this crash.
- `bridge/gtkb-wi5668-sweep-completion-gate-004.md` — the WI-5668 thread that
  introduced the check.

## Claim

`gt project doctor` crashes outright, reproducibly, inside
`_check_skill_rename_reference_sweep` — the WI-5668 skill-rename completion gate.
The check is committed in `HEAD` (definition at `doctor.py:2529`, registered in
`run_doctor`), so the canonical doctor health/acceptance surface is currently
non-functional for every session and every gate that depends on it.

Observed traceback (reproduced twice, 2026-07-25):

    File ".../groundtruth_kb/project/doctor.py", line 7225, in run_doctor
        checks.append(_check_skill_rename_reference_sweep(target))
    File ".../groundtruth_kb/project/doctor.py", line 2603, in _check_skill_rename_reference_sweep
        for line in completed.stdout.splitlines():
    AttributeError: 'NoneType' object has no attribute 'splitlines'

### Root-cause analysis

The `git grep` invocation at `doctor.py:2576-2581` passes `capture_output=True`
and `text=True`, so `completed.stdout` should never be `None` under stock
CPython semantics. The failure therefore indicates the returned object is not a
stock captured `CompletedProcess`.

Leading hypothesis: GT-KB's own subprocess / directive-enforcement interception
layer returns a synthetic `CompletedProcess` (returncode set, streams unset) when
it screens the `git grep` command. This is consistent with the enforcement
adapter surface in `groundtruth_kb/enforcement/__init__.py`.

This hypothesis is **not** load-bearing for the fix: the defect is that the
WI-5668 check assumes `completed.stdout` is always a string. The correct
hardening is defensive regardless of which layer returns `None`.

### Impact

- `gt project doctor` is unusable (hard crash, non-zero exit) for all callers.
- WI-5678 cannot produce its mandatory doctor acceptance evidence; its `-008`
  `NO-GO` finding F1 cites this crash directly.
- Any release-readiness or session-start path that shells out to the doctor
  inherits the failure.

## Owner Decision Needed

None outstanding. The owner already decided (AUQ, 2026-07-25) to hand this to
WI-5441/Codex rather than have Prime Builder file a competing `doctor.py` edit.
This advisory records the defect and the analysis; it requests no new owner
decision.

## Recommended Prime Action

Fold the repair into the **WI-5441** implementation, which already holds an
active `GO` covering `groundtruth-kb/src/groundtruth_kb/project/doctor.py`.

Exact minimal remediation (one line, `doctor.py:2603`):

    for line in (completed.stdout or "").splitlines():

Optionally also harden the sibling `completed.returncode` branch if the same
interception path can leave `returncode` unset.

Suggested regression coverage (net-new or folded into the WI-5441 suite):

1. `_check_skill_rename_reference_sweep` returns a non-crashing `ToolCheck` when
   the subprocess result carries `stdout=None`.
2. `run_doctor` completes end-to-end with that condition present.
3. Existing WI-5668 sweep assertions (hit counting, exclusion prefixes) remain
   unchanged when `stdout` is a normal string.

Deliberate non-actions by Prime Builder, per the owner decision and the standing
bridge-runtime domain boundary:

- No `doctor.py` edit was made by this session; the file is dirty and inside
  WI-5441's active GO'd scope.
- No competing bridge proposal targeting `doctor.py` was filed.
- The WI-5668 landing remains held.

## Classification Slot

**adopt** — the defect is confirmed, reproducible, and has an exact minimal fix.
Recommended disposition is adoption into the in-flight WI-5441 scope. No design
alternatives require evaluation.

### Required Prime Builder Owner-Grilling Gate

Implementation implied: **yes** — a source change to `doctor.py` plus regression
coverage.

Grill-the-owner questions: **none outstanding.** The routing decision (WI-5441
scope vs. competing fast-lane edit vs. revert) was already put to the owner via
`AskUserQuestion` on 2026-07-25 and answered "hand to WI-5441/Codex."

Required durable owner decisions: satisfied by the AUQ answer recorded in this
advisory's Source section; no further owner approval is required before WI-5441
absorbs the fix under its existing `GO` and PAUTH.

## Non-Approval Statement

This advisory is not implementation approval. It records a defect (WI-5688) and a
recommended remediation route for governed disposition. It does not bypass the
bridge proposal, Loyal Opposition `GO`, implementation-start authorization, or
verification gates, and it does not widen WI-5441's approved scope by itself.
