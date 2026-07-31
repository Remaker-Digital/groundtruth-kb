NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# GT-KB Bridge Implementation Report - gtkb-wi5688-doctor-crash-fastlane - 005

bridge_kind: implementation_report
Document: gtkb-wi5688-doctor-crash-fastlane
Version: 005
Responds to: bridge/gtkb-wi5688-doctor-crash-fastlane-004.md
Approved proposal: bridge/gtkb-wi5688-doctor-crash-fastlane-003.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5688
Recommended commit type: fix:
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_doctor_skill_rename_sweep.py"]
kb_mutation_in_scope: false

## Implementation Claim

Implemented the approved Windows-safe subprocess boundary for the doctor skill-
rename sweep check. The check now captures `git grep` output as bytes and decodes
UTF-8 explicitly with replacement, so non-ASCII tracked content cannot crash the
doctor through the host `cp1252` default. Exit-code semantics remain unchanged:
exit 0 reports real matches, exit 1 alone reaches the zero-reference PASS path,
and other exit codes remain tool failures.

The exit-0 defensive branch now returns a visible `warning` when no usable output
is available and never claims `sweep complete`. Three focused regressions cover
Unicode output with a real offending path, missing exit-0 output, and the exit-1
zero state. Only the two GO-authorized paths changed; no bridge predecessor,
MemBase record, dispatcher configuration, DCL, registry, or Git state was mutated.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `SPEC-1662`
- `GOV-10`
- `GOV-12`
- `GOV-07`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `DCL-SOT-READ-HOOK-CONTRACT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required. The implementation carries forward
`DELIB-202667528`, which confirms the WI-5688 fast-lane route and supersedes
`DELIB-202667509` on routing only; `DELIB-202667193` and
`DELIB-20260724-WI5668-SEVERITY-CONTRACT`, which require warning while real
references remain; and the standing Reliability Fixes authorization backed by
`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`.

## Prior Deliberations

- `bridge/gtkb-wi5688-doctor-crash-fastlane-003.md` - approved corrected implementation proposal.
- `bridge/gtkb-wi5688-doctor-crash-fastlane-004.md` - Loyal Opposition GO authorizing the exact two-path implementation.
- `bridge/gtkb-wi5688-doctor-crash-fastlane-002.md` - root-cause and false-green corrections adopted in full.
- `DELIB-202667528` - owner routing confirmation for the fast lane.
- `DELIB-202667193` and `DELIB-20260724-WI5668-SEVERITY-CONTRACT` - warning-until-zero behavior.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-RELIABILITY-FAST-LANE-001` | Exact two-file repair; focused 7-test suite, Ruff, format, and diff checks pass. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_sweep_exit0_without_usable_output_is_not_pass` proves unreadable evidence produces warning rather than a false PASS; live direct check reports 711 references. |
| `SPEC-1662` | Three meaningful regressions assert status, count/path visibility, and absence of the false `sweep complete` claim. |
| `GOV-10` | Tests exercise the production `_check_skill_rename_reference_sweep` function and a live checkout probe executes the same check against `E:\\GT-KB`. |
| `GOV-12` | WI-5688 adds the three proposal-required regression tests while retaining the four existing tests. |
| `GOV-07` | Source mutation followed the approved v003/v004 bridge chain, exact-session claim, and schema-v3 implementation-start packet. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | The enforcement check remains fail-visible and returns warning with the live 711-reference count instead of crashing or returning false green. |
| `DCL-SOT-READ-HOOK-CONTRACT-001` | Direct live probe reads current tracked repository evidence through the production check and reports the current count. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Schema-v3 packet names the active standing PAUTH, WI-5688, and exactly the two changed targets. |
| `ADR-CROSS-HARNESS-PARITY-001` | Byte capture plus explicit UTF-8 decoding removes dependence on the Windows process locale used by different harnesses. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | v004 GO, exact GO-implementation claim, start packet, scoped implementation, and this append-only report preserve the bridge handoff. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | No `applications/` path changed; source and tests remain in canonical platform locations. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Every specification linked by approved v003 is carried forward and mapped here. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Seven focused tests pass; Unicode, missing-output, and true-zero branches map directly to the approved criteria. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI, project, PAUTH, proposal, GO, claim, start packet, code/tests, and report form the durable governed chain. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The defect is preserved as executable regressions and implementation evidence rather than conversation-only knowledge. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | GO, claim, operation-time authorization, and start activation preceded mutation; this report routes independent verification. |

## Commands Run

- `groundtruth-kb\\.venv\\Scripts\\python.exe -m pytest platform_tests\\scripts\\test_doctor_skill_rename_sweep.py -v --tb=short`
- `groundtruth-kb\\.venv\\Scripts\\python.exe -m pytest platform_tests\\scripts\\test_doctor_skill_rename_sweep.py -q --tb=short`
- `groundtruth-kb\\.venv\\Scripts\\ruff.exe check groundtruth-kb\\src\\groundtruth_kb\\project\\doctor.py platform_tests\\scripts\\test_doctor_skill_rename_sweep.py`
- `groundtruth-kb\\.venv\\Scripts\\ruff.exe format --check groundtruth-kb\\src\\groundtruth_kb\\project\\doctor.py platform_tests\\scripts\\test_doctor_skill_rename_sweep.py`
- `git diff --check -- groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_doctor_skill_rename_sweep.py`
- Direct live checker probe: `_check_skill_rename_reference_sweep(Path.cwd())` through the project virtualenv.
- `groundtruth-kb\\.venv\\Scripts\\gt.exe project doctor` - full live acceptance rerun; result recorded below.
- Packet inspection: `Get-Content -LiteralPath .gtkb-state\\implementation-authorizations\\by-bridge\\gtkb-wi5688-doctor-crash-fastlane.json`.

## Observed Results

- Focused suite: `7 passed, 1 warning in 1.51s`; post-format rerun: `7 passed, 1 warning in 1.55s`. The sole warning is the pre-existing unknown `asyncio_mode` pytest option.
- Ruff check: `All checks passed!`; format: `2 files already formatted`; diff check: exit 0.
- Direct live production check: exit 0; `warning`; `711 pre-rename bare skill-dir reference(s) remain`; first live offending paths are reported and no traceback occurs.
- Full live `gt project doctor`: completed without traceback and emitted the
  required `[WARN] 711 pre-rename bare skill-dir reference(s) remain` result.
  The command exited 1 because the live repository has unrelated pre-existing
  doctor failures (including the duplicate-SoT lock baseline, disabled/stale
  dispatcher health, cross-harness asymmetries, degraded deliberation index,
  and prior-session ORIENT gap); none is in the approved WI-5688 scope.
- Final SHA-256: doctor source `E20D1E7D5E15359A294527767B169F43750F77B0A7CFF7E791F782E0AB4960D7`; focused tests `3D7835AFAC9690BB6CCF68496FFE72173996FE06665A05D36B9E1DF1E85A7D61`.
- Implementation-start packet: `.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5688-doctor-crash-fastlane.json`, created `2026-07-29T13:19:46Z`, packet hash `sha256:912911fb0893e9371bbc1ccda8154db639a485e9ef51ad1b0949719d6a10b9e6`; operation-time decision `allowed=true` for the exact source and test targets.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `platform_tests/scripts/test_doctor_skill_rename_sweep.py`

Filing-plan observation: 72 out-of-scope dirty paths were excluded. The live
shared-worktree count is intentionally not asserted as stable.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: 2 files changed, +60/-2. This is a localized repair to one existing doctor subprocess boundary plus three regressions; it adds no new module, command, skill, hook, or capability surface.

```text
     .../src/groundtruth_kb/project/doctor.py           | 15 ++++++-
     .../scripts/test_doctor_skill_rename_sweep.py      | 47 ++++++++++++++++++++++
     2 files changed, 60 insertions(+), 2 deletions(-)
```

## Acceptance Criteria Status

- [x] `git grep` output is captured as bytes and decoded explicitly as UTF-8 with `errors="replace"`.
- [x] Exit 0 remains the match-present path; exit 1 alone reaches zero-reference PASS; other exit codes remain failures.
- [x] Exit 0 without usable decoded output returns non-PASS warning and never claims `sweep complete`.
- [x] Unicode live-reference output returns warning, preserves the count, and identifies the offending tracked path.
- [x] All seven focused tests, Ruff check, Ruff format check, and scoped diff check pass.
- [x] Full `gt project doctor` completes without traceback and reports warning with the live 711-reference count; unrelated existing checks keep the aggregate doctor result at FAIL.
- [x] Exactly the two approved paths changed; no MemBase, DCL, dispatcher, registry, bridge predecessor, or Git-state mutation occurred.

## Risk And Rollback

Residual risk is limited to invalid UTF-8 bytes being rendered with replacement
characters in diagnostic context. The complete matching line, path, and match
count remain available, and absent output cannot produce PASS. Rollback is a
focused revert of only the two implementation paths after preserving this
append-only report and any independent verdict; do not touch excluded foreign
dirty paths or rewrite bridge history.

## Pre-Filing Preflight Subsection

- Candidate applicability preflight: PASS; `preflight_passed: true`,
  `missing_required_specs: []`, `missing_advisory_specs: []`,
  `warnings.unclassified_target_paths: []`, and `blocking_errors: []`.
- Candidate clause preflight: PASS; 5 clauses evaluated, 3 `must_apply`,
  2 `may_apply`, 0 evidence gaps in must-apply clauses, 0 blocking gaps,
  exit 0.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and exact command evidence.
2. Confirm the live Unicode warning remains fail-visible and the zero-reference PASS is reachable only on `git grep` exit 1.
3. Return VERIFIED if the report and implementation satisfy approved v003/v004, otherwise return NO-GO with concrete findings.
