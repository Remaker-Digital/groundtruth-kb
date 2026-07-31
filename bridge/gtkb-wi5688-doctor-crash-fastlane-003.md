REVISED
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: de7aad12-9b24-41c8-849c-de48e349ff62
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code interactive leader session; resolved role prime-builder via ::init gtkb pb; manual-dispatcher program DELIB-202667523

bridge_kind: prime_proposal
Document: gtkb-wi5688-doctor-crash-fastlane
Version: 003
Responds to: bridge/gtkb-wi5688-doctor-crash-fastlane-002.md
Date: 2026-07-29 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5688

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_doctor_skill_rename_sweep.py"]

# WI-5688 Doctor Crash Fast-Lane — REVISED Proposal (answers -002 NO-GO)

## Findings Resolution Table

| -002 Finding | Resolution in this revision |
|---|---|
| P1-1: fallback converts decode failure with real matches into false sweep-complete PASS | Fix moved to the subprocess boundary: deterministic UTF-8 decode with documented error policy; exit-0-without-usable-output now yields a non-PASS `warning` scan-unavailable result, never sweep-complete. The `(stdout or "")` fallback is abandoned. See §Corrected Design. |
| P1-2: proposed regression test would bless false-success behavior | Test plan rebuilt around the WI-5668 severity contract: Unicode-output regression asserting `warning` with the offending tracked path visible; missing-output case asserting non-PASS scan-unavailable; acceptance criterion is the semantic result, not absence of AttributeError. See §Spec-Derived Test Plan. |
| P1-3: no durable evidence for the routing supersession | Owner re-confirmed by AUQ on 2026-07-29; archived as DELIB-202667528 (supersedes DELIB-202667509 on routing only; analysis stands). Cited in §Owner Decisions / Input. |

## Corrected Root Cause (replaces the -001 interception-adapter hypothesis)

The -001 leading hypothesis (directive-enforcement interception returning a
synthetic CompletedProcess) is DISPROVED by the -002 reviewer's live
evidence and is withdrawn. Actual root cause: `doctor.py:2576-2581` invokes
stock `subprocess.run(capture_output=True, text=True)` without an explicit
`encoding=`; on this Windows host `locale.getencoding()` is `cp1252`, so
UTF-8 child output containing bytes such as `0x90` (live trigger:
`bridge/gtkb-command-surface-003.md:266`, Unicode left arrow) raises a
reader-thread `UnicodeDecodeError` inside `subprocess.py`; the
`CompletedProcess` then carries `returncode=0` with `stdout=None`, and
`doctor.py:2603` crashes with `AttributeError` on `.splitlines()`.

Corroborating second incident (out of scope here, cross-referenced): the
SessionStart startup service crashed 2026-07-29 in
`write_dashboard_and_report` (exit 1) — same defect class at sibling
`text=True` call sites in `scripts/session_self_initialization.py` (lines
1784, 1815, 2123, 2193, 2232). The platform-wide sweep is tracked as
WI-5740; this proposal remains scoped to the doctor's two target files.

## Corrected Design

In `_check_skill_rename_reference_sweep` (`doctor.py:2576-2603`):

1. Decode deterministically at the boundary: run `git grep` with
   `capture_output=True`, `text=False`, then decode explicitly:
   `stdout_text = completed.stdout.decode("utf-8", errors="replace")`
   (bytes capture + explicit decode; `errors="replace"` is the documented
   policy — a replaced character still preserves the line, the path, and
   the match for counting/reporting).
2. Preserve exit-code semantics exactly as documented at `doctor.py:2590`:
   exit 0 = matches exist; exit 1 = no matches; other = tool failure.
3. Fail visible, never false-green: if exit 0 ever yields no usable decoded
   output (defensive branch), return a `ToolCheck` with
   `status="warning"` and message `skill-rename sweep scan unavailable:
   git grep output could not be decoded` — never the `sweep complete`
   PASS path at `doctor.py:2627-2632`.
4. No behavior change for the healthy paths: warning with counted
   nonexcluded references while matches remain (severity contract per
   DELIB-202667193 and DELIB-20260724-WI5668-SEVERITY-CONTRACT); PASS only
   at zero.

## Spec-Derived Test Plan

All in `platform_tests/scripts/test_doctor_skill_rename_sweep.py`
(existing 4 ASCII-fixture tests retained):

1. `test_sweep_unicode_output_preserves_warning` — fixture repo/mocked
   `git grep` emitting UTF-8 bytes including a multi-byte character and
   `0x90`; asserts the check returns `status="warning"`, the reference
   count reflects the real matches, and the offending tracked path appears
   in the message. Derives from the WI-5668 severity contract (warn while
   real references remain).
2. `test_sweep_exit0_without_usable_output_is_not_pass` — mocked
   completed process with `returncode=0` and undecodable/absent output;
   asserts non-PASS `warning` scan-unavailable result; asserts the message
   does NOT claim sweep complete. Derives from GOV-SOURCE-OF-TRUTH-
   FRESHNESS-001 (a health claim must derive from readable evidence).
3. `test_sweep_pass_only_at_zero` — exit 1 (no matches) still yields PASS
   sweep-complete; guards the healthy path against regression.
4. Acceptance: `gt project doctor` completes without traceback on the live
   repository AND reports `warning` with the current nonexcluded stale
   reference count (~711 at review time) — the semantic result, not mere
   absence of AttributeError.

## Specification Links

- GOV-RELIABILITY-FAST-LANE-001 — governing fast-lane spec for this defect class.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 — health/state claims derive from fresh readable canonical evidence; the false-PASS path violated this.
- SPEC-1662 (GOV-18 assertion quality) — meaningful assertions over coverage; drives the semantic test criteria.
- GOV-10 — tests exercise the exposed production interface (`gt project doctor` check path).
- GOV-12 — work item triggers test creation (the three new regression tests).
- GOV-07 / GOV-15 — no autonomous fixes for failed tests without gate; this proposal routes the fix through GO.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — the doctor is a review-time enforcement surface; its integrity is cross-cutting.
- DCL-SOT-READ-HOOK-CONTRACT-001 — doctor participates in SoT enforcement surfaces; false-green undermines the contract.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 — project-scoped authorization discipline (standing PAUTH cited above).
- ADR-CROSS-HARNESS-PARITY-001 — doctor output is consumed cross-harness as acceptance evidence (WI-5678 dependency).
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge audit-trail discipline governing this thread's filing path.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — target paths live under groundtruth-kb/src/**; in-root platform placement affirmed, no application-subtree output.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this section satisfies the concrete-links clause for all governing specs.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the §Spec-Derived Test Plan maps each linked requirement to executed tests for verification.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) — corrections land as durable bridge/DA artifacts, not conversation state.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) — revision preserves the append-only audit chain over in-place amendment.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) — the -002 review finding triggered this governed revision artifact.

## Prior Deliberations

- DELIB-202667528 — owner routing supersession (2026-07-29): fast lane replaces the closed WI-5441 route; supersedes DELIB-202667509 on routing only.
- DELIB-202667509 — prior routing decision; technical analysis stands and is incorporated.
- DELIB-202667193 and DELIB-20260724-WI5668-SEVERITY-CONTRACT — the WI-5668 owner severity contract (doctor WARNs while sweep incomplete) that the corrected design preserves.
- DELIB-202667523 — program mandate under which this leader session files.
- Review evidence: bridge/gtkb-wi5688-doctor-crash-fastlane-002.md (root-cause correction adopted in full).

## Owner Decisions / Input

- AUQ-20260729-WI5688-FASTLANE-SUPERSESSION (archived as DELIB-202667528, work_item_id WI-5688): owner confirmed the fast-lane route, superseding DELIB-202667509 on routing only. Full bridge protocol retained: this REVISED awaits independent LO GO before any implementation; implementation requires the exact-session claim and implementation-start packet; report and independent VERIFIED follow.
- PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING — standing project authorization covering WI-5688 by active membership (source + test_addition classes), verified active at -002 review.

## Requirement Sufficiency

Existing requirements sufficient. GOV-RELIABILITY-FAST-LANE-001,
GOV-SOURCE-OF-TRUTH-FRESHNESS-001, SPEC-1662, and the WI-5668 severity
contract deliberations fully constrain the corrected behavior; no new or
revised requirement is needed before implementation.

## Risk and Rollback

Risk: LOW. Two files; the decode change is localized to one check's
subprocess boundary; healthy-path semantics are regression-guarded by test
3. Rollback: revert the single commit; the check returns to the current
crash behavior (visible, not silent). The false-green risk identified at
-002 is eliminated by design (no PASS without decoded evidence).

Recommended commit type: fix

## Verification Plan

1. `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_doctor_skill_rename_sweep.py -v` — 7 tests (4 existing + 3 new) pass.
2. `ruff check` and `ruff format --check` on both target files — clean.
3. Live acceptance: `gt project doctor` runs to completion; skill-rename sweep check reports `warning` with the live nonexcluded count; no traceback.
