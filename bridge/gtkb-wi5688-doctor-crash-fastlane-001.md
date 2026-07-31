NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: de7aad12-9b24-41c8-849c-de48e349ff62
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code headless worker; manual dispatch by leader session per DELIB-202667523; resolved role prime-builder

Document: gtkb-wi5688-doctor-crash-fastlane
Version: 001
Author: Prime Builder (Claude, harness B) — manual-dispatch worker session under DELIB-202667523
Date: 2026-07-28

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5688

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_doctor_skill_rename_sweep.py"]

Source advisory: bridge/gtkb-wi5688-doctor-skill-rename-sweep-crash-001.md

# Fast-Lane Defect Proposal — Fix `gt project doctor` Crash in `_check_skill_rename_reference_sweep` (WI-5688)

## Summary

`gt project doctor` crashes outright with
`AttributeError: 'NoneType' object has no attribute 'splitlines'` at
`groundtruth-kb/src/groundtruth_kb/project/doctor.py:2603` inside
`_check_skill_rename_reference_sweep` (the WI-5668 skill-rename completion
gate). This proposal requests approval for the exact one-line defensive fix
identified in the source advisory, plus a regression test for the
`stdout=None` condition. Proposal only — no implementation has been performed;
implementation follows a `GO`.

This thread is the canonical advisory-conversion child of
`bridge/gtkb-wi5688-doctor-skill-rename-sweep-crash-001.md`: the advisory
converts into a normal `NEW` proposal on its own thread citing the advisory as
source.

## Defect

Re-verified at current HEAD state of
`groundtruth-kb/src/groundtruth_kb/project/doctor.py`:

- The `git grep` subprocess invocation at lines 2576-2581 passes
  `capture_output=True` and `text=True`.
- At line 2602-2603, when `completed.returncode == 0`, the code iterates
  `completed.stdout.splitlines()` with no guard.
- Observed at runtime (reproduced twice on 2026-07-25, per the source
  advisory and WI-5688): `completed.stdout` is `None`, raising
  `AttributeError: 'NoneType' object has no attribute 'splitlines'` and
  crashing `run_doctor` (registration site `doctor.py` `run_doctor`, call at
  the `_check_skill_rename_reference_sweep(target)` append).

Root cause (per the source advisory analysis): under stock CPython
semantics `capture_output=True, text=True` guarantees a string `stdout`; the
observed `None` indicates a synthetic `CompletedProcess` returned by an
interception layer (leading hypothesis: the GT-KB subprocess /
directive-enforcement adapter). The hypothesis is not load-bearing for the
fix: the defect is that the WI-5668 check assumes `completed.stdout` is always
a string, and the correct hardening is defensive regardless of which layer
returns `None`.

Impact:

- `gt project doctor` is a canonical health and acceptance surface; the crash
  makes it unusable (hard crash, non-zero exit) for every caller.
- WI-5678 cannot produce its mandatory doctor acceptance evidence
  (`bridge/gtkb-wi5678-genericize-advisory-role-framing-008.md` finding F1
  cites this crash directly).
- Any release-readiness or session-start path that shells out to the doctor
  inherits the failure.

Regression provenance: introduced by WI-5668
(`bridge/gtkb-wi5668-sweep-completion-gate-004.md` thread).

## Proposed Change

Exactly one source line, `doctor.py:2603`:

Before:

    for line in completed.stdout.splitlines():

After:

    for line in (completed.stdout or "").splitlines():

Behavior: when `stdout` is `None` (or empty), the sweep iterates zero lines
and the check reports its normal zero-hit result instead of crashing. For
normal string `stdout`, semantics are byte-identical.

Deliberate scope exclusion: the source advisory's optional sibling
hardening of the `completed.returncode` branch is NOT included. No
`returncode`-related failure has been observed, and fast-lane discipline
favors the minimal single-concern change. If that condition is ever observed
it is a separate defect work item.

Plus one regression test addition (see test plan) in
`platform_tests/scripts/test_doctor_skill_rename_sweep.py`.

## Fast-Lane Eligibility (GOV-RELIABILITY-FAST-LANE-001)

All four eligibility criteria hold for WI-5688:

1. Origin is `defect` (WI-5688 `origin=defect`, P1, component=doctor) — never
   `new`.
2. No new public API, CLI surface, or behavior beyond removing the defect —
   the change is a defensive expression inside an existing private check
   function.
3. No new or revised requirement or specification is required (see
   Requirement Sufficiency).
4. Small and single-concern: 1 source file, 1 changed line, plus 1 test file
   with one added regression case — far under the ~3 files / ~150 net lines
   guide.

Mechanism satisfied: WI-5688 is an active member of
PROJECT-GTKB-RELIABILITY-FIXES (membership record
`PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-5688`, status active) and is therefore
covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (status active,
no expiry, allowed mutation classes `source` + `test_addition`; this change
uses exactly those classes) through active project membership. Per the spec,
this fix requires no per-fix deliberation record, requires no per-fix project
authorization, and requires no formal-artifact-approval packet; bridge review,
GO, implementation-start packet, post-implementation report, and VERIFIED are
all preserved unchanged. This proposal performs no approval-evidence work.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — governing fast-lane governance path for
  this small defect fix; eligibility argued above; preserved gates honored by
  this thread.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol and audit-trail
  authority; this proposal is filed through the governed bridge path as a
  fresh advisory-conversion thread.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project-scoped
  implementation authorization chain; the PAUTH cited in the metadata lines
  supplies owner-approval evidence for this bounded scope, additive to the
  bridge `GO` gate.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the machine-readable
  Project Authorization / Project / Work Item metadata lines above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section
  cites every relevant governing specification for the proposed change.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — included spec of the standing
  PAUTH; the defect, analysis, routing history, and repair are preserved as
  durable artifacts (WI-5688, the source advisory, this proposal).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — placement constraint on the
  `groundtruth-kb/src/groundtruth_kb/project/**` target path; this change
  edits platform code in place and moves nothing across the
  platform/application boundary.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — `VERIFIED` for this
  thread is conditional on the spec-derived tests in the test plan below
  being created/identified and executed against the implementation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — durable-artifact-graph model;
  this thread links WI-5688, the advisory, the routing deliberations, and
  the standing PAUTH rather than relying on session memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lifecycle-state discipline for the
  superseded-routing narrative in Prior Deliberations (the WI-5441 route is
  explicitly marked superseded with the trigger and reconciliation evidence,
  not silently dropped).

Test derivation from linked specifications is stated in the
Specification-Derived Test Plan section below.

## Prior Deliberations

- `DELIB-202667509` — owner decision (AUQ, 2026-07-25) routing WI-5688 into
  WI-5441's then-active `GO` scope for `doctor.py`. Superseded on routing
  only: WI-5441 reached terminal `VERIFIED` at its v020 without absorbing
  this repair (WI-5688 v2 status_detail, owner-directed 2026-07-28 routing
  reconciliation), so the WI-5441 route is no longer executable authority.
  The defect analysis and minimal-fix content of that decision remain valid
  and are adopted here.
- `DELIB-202667523` — owner decision (2026-07-29 transcript): integrated
  parallel-operation program mandate and manual-dispatcher operating model.
  This worker session was dispatched by the leader session under that
  mandate; the mandate explicitly preserves the bridge protocol
  (proposal -> independent LO GO -> claim -> implementation-start packet ->
  implementation -> report -> independent VERIFIED).
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — owner decision establishing
  `GOV-RELIABILITY-FAST-LANE-001` and the standing authorization
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` this proposal relies on.
- `DELIB-202667445` — Loyal Opposition review (NO-GO) on the WI-5668 sweep
  completion gate revision; context for the check this fix hardens.
- Source advisory: `bridge/gtkb-wi5688-doctor-skill-rename-sweep-crash-001.md`
  (ADVISORY, 2026-07-25) — reproduction, traceback, root-cause analysis, and
  the exact one-line remediation adopted by this proposal.

Advisory-chain note: the source advisory thread remains at `ADVISORY` with no
successor version filed there, because the typed bridge lifecycle forbids an
`ADVISORY -> NEW` transition on the same thread; the resolver author-role
defect surfaced during the first filing attempt is captured in MemBase as a
program work item, and this fresh child thread is the canonical
advisory-conversion route.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- AUQ 2026-07-25 (archived as `DELIB-202667509`): owner originally chose
  "hand to WI-5441/Codex" over a competing fast-lane edit. That answer is
  superseded on routing only — WI-5441 terminated `VERIFIED` at v020 without
  absorbing the repair, per the owner-directed 2026-07-28 stale-routing
  reconciliation recorded on WI-5688 v2 ("needs its own bounded proposal").
- AUQ 2026-07-28: owner fast-lane authorization — WI-5688 proceeds as its own
  bounded fast-lane defect proposal under `GOV-RELIABILITY-FAST-LANE-001`,
  covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` through active
  membership in `PROJECT-GTKB-RELIABILITY-FIXES` (no per-fix authorization
  required per the standing fast-lane mechanism).
- `DELIB-202667523` (owner decision): explicit per-access approval for the
  leader session's manual cross-harness/worker fan-out that dispatched this
  proposal-drafting task; it does not waive any bridge gate, and this thread
  claims none of its gates waived.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements are
`GOV-RELIABILITY-FAST-LANE-001` (the fast-lane mechanism and its preserved
gates) and the WI-5668-established behavior contract of
`_check_skill_rename_reference_sweep` (warn while bare pre-rename references
remain, pass at zero, honor the exclusion set, derive bare names from current
`gtkb-` skill dirs — as exercised by the existing spec-derived tests in
`platform_tests/scripts/test_doctor_skill_rename_sweep.py`). The fix restores
that specified behavior in the `stdout=None` condition without adding,
changing, or requiring any new or revised requirement or specification.

## Specification-Derived Test Plan

| Linked specification / contract | Derived test | File | Status |
|---|---|---|---|
| WI-5668 sweep behavior contract: warn while a bare reference remains | `test_warns_while_bare_reference_remains` | `platform_tests/scripts/test_doctor_skill_rename_sweep.py` | existing; must remain green (proves no behavior change for string stdout) |
| WI-5668 sweep behavior contract: pass at zero references | `test_passes_when_no_bare_reference` | same file | existing; must remain green |
| WI-5668 sweep behavior contract: exclusion prefixes do not count | `test_excluded_trees_do_not_count` | same file | existing; must remain green |
| WI-5688 defect condition: check must not crash when the subprocess result carries `stdout=None` | NEW regression case (e.g. `test_none_stdout_does_not_crash`): monkeypatch the `subprocess.run` used by `_check_skill_rename_reference_sweep` to return a `CompletedProcess`-shaped object with `returncode=0` and `stdout=None`; assert the function returns a non-crashing `ToolCheck` (no `AttributeError`) with a well-formed status | same file | to be added with the fix |
| `GOV-RELIABILITY-FAST-LANE-001` preserved-gates clauses | procedural evidence in this bridge thread: metadata lines, LO review/GO, implementation-start packet, post-impl report, VERIFIED | this thread | procedural (not a code test) |

Verification commands (implementation phase, venv interpreter only):

    E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_doctor_skill_rename_sweep.py -q
    E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_doctor_skill_rename_sweep.py
    E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_doctor_skill_rename_sweep.py

Acceptance evidence: a live `gt project doctor` invocation completing without
`AttributeError` in `_check_skill_rename_reference_sweep` (end-to-end
confirmation of the WI-5688 impact removal, unblocking WI-5678's acceptance
evidence).

## Acceptance Criteria

1. `doctor.py:2603` reads `for line in (completed.stdout or "").splitlines():`
   and no other source line changes.
2. New `stdout=None` regression case passes.
3. All existing tests in `platform_tests/scripts/test_doctor_skill_rename_sweep.py`
   pass unchanged.
4. `gt project doctor` completes without the WI-5688 `AttributeError`.
5. Ruff lint and format gates pass on both changed files.

## Risk / Rollback

- Risk: minimal. The change is a defensive expression on one line. When
  `stdout` is `None` the sweep sees zero output lines — equivalent to the
  established `git grep` no-match result — and reports normally instead of
  crashing. For every normal string `stdout`, behavior is unchanged
  (guaranteed by the existing test suite remaining green).
- Failure mode if wrong: worst case, a genuinely captured output stream that
  is `None` would report zero hits rather than sweep findings; the sweep is a
  non-required (`required=False`) advisory check, so this cannot mask a
  blocking failure.
- Rollback: single-commit revert of the fix commit (one source line + one
  test case); no data, schema, config, or state migration involved.

## Recommended Commit Type

Recommended commit type: fix

Rationale: repairs broken behavior (crash) with no new capability surface.
