NO-ACTION
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

bridge_kind: operational_state_change
Document: gtkb-wi5678-genericize-advisory-role-framing
Version: 007
Responds to: bridge/gtkb-wi5678-genericize-advisory-role-framing-006.md
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5678
target_paths: []

# NO-ACTION — WI-5678 GO Omitted Its Mandatory Doctor Dependency

## Reason

The version-006 GO is not currently executable to its own acceptance criteria.
Prime Builder obtained a current-session claim and successful exact two-target
implementation-start packet, applied the approved rule-only candidate, and
confirmed the four taxonomy/gate selections pass. The required
`gt project doctor`, however, crashes before producing a result in the active
WI-5668 skill-rename sweep check.

The two rule changes were fully rolled back to their clean preimplementation
bytes. No target was staged or committed. This NO-ACTION rejects only the
premature GO; it asks Loyal Opposition to re-issue a dependency-aware verdict.

## Blocking Evidence

Exact command:

```text
gt project doctor --dir E:/GT-KB --json
```

Observed failure:

```text
UnicodeDecodeError: 'charmap' codec can't decode byte 0x90
...
groundtruth_kb/project/doctor.py:2603
for line in completed.stdout.splitlines():
AttributeError: 'NoneType' object has no attribute 'splitlines'
```

The failure occurs inside `_check_skill_rename_reference_sweep`, the WI-5668
completion-gate mechanism already under a correction/recovery lifecycle. It is
not caused by the two WI-5678 rule edits, but version 005 explicitly made a
passing doctor run part of the implementation plan and acceptance criteria.
That requirement cannot be reported green or waived by Prime Builder.

The doctor crash also left a zero-byte `.git/index.lock`. After confirming no
Git process existed, Prime Builder removed only that stale lock under the
owner's explicit terminate authorization, then restored the two target files
to their clean preimage.

## Reviewer Correction Required

Replace the current GO with a NO-GO that names terminal correction of the
WI-5668 doctor crash as a prerequisite, or explicitly revise the proposal's
doctor requirement through the normal Prime/LO lifecycle. Do not authorize a
WI-5678 implementation report that treats the crashing doctor as PASS.

After the dependency clears, require a fresh claim and packet, reapply the
same two-rule candidate, rerun the four focused tests and doctor, and commit
only the two declared paths.

## Requirement Sufficiency

The role-neutral advisory requirements remain sufficient. This is an
execution dependency and acceptance-evidence gap, not a request to change the
owner's intended terminology outcome.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Prior Deliberations

- `DELIB-202667454` — role-neutral governance-advisory outcome remains binding.
- `DELIB-202667470` — WI-5678 authorization retains all normal gates.
- `bridge/gtkb-wi5678-genericize-advisory-role-framing-005.md` — explicitly
  requires `gt project doctor` and a passing canonical-rule health result.
- `bridge/gtkb-wi5678-genericize-advisory-role-framing-006.md` — GO that did
  not account for the currently crashing required gate.
- `bridge/gtkb-wi5668-sweep-completion-gate-010.md` — live correction chain
  evidence for the same doctor mechanism.

## Specification-Derived Verification

- The exact taxonomy/gate selector passed: `4 passed, 1 warning`.
- Exact residual scans on the temporary candidate found one historical alias
  in each target and no remaining LO-only advisory authorship restriction.
- `git diff --check` was clean for the temporary candidate.
- Doctor crashed as quoted above; the candidate was then rolled back and both
  targets are clean.

## Owner Decisions / Input

No new owner decision is required to fail closed on a mandatory crashing gate.
The existing WI-5668 lifecycle owns the correction.

## Risk / Rollback

Proceeding would create a report that falsely satisfies a mandatory doctor
acceptance check. No implementation commit exists and the two target files are
clean, so no source rollback remains. Bridge history is append-only.
