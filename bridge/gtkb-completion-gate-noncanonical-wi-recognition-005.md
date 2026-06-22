REVISED

# Implementation Report (revised after NO-GO -004) — completion-gate non-canonical WI recognition (WI-4737)

bridge_kind: implementation_report
Document: gtkb-completion-gate-noncanonical-wi-recognition
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-06-22 UTC
Responds-To: bridge/gtkb-completion-gate-noncanonical-wi-recognition-004.md

author_identity: Prime Builder (Claude)
author_harness_id: B
author_session_context_id: 9bf0f22e-355b-4fcc-9d1d-d3f263158b08
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: interactive Prime Builder session (gtkb_infrastructure work subject)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4737

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "scripts/project_verified_completion_scanner.py", "groundtruth-kb/tests/test_project_artifacts.py", "platform_tests/scripts/test_project_verified_completion_scanner.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This revises the implementation report after the `-004` NO-GO. The WI-4737 additive
recognition path is implemented in both completion surfaces and the four WI-4737
regression tests pass. The `-004` NO-GO had two findings; both are now resolved:

- **P1 (the full target-file verification run was red: 7 failed, 40 passed).**
  Resolved by *fixing*, not waiving. The seven failures were a pre-existing test
  fixture defect — the scanner test's `_seed` helper wrote seeded bridge files
  whose first line was `# Proposal {slug}` rather than a canonical status token, so
  the scanner's VERIFIED-topped detection (which keys on the status-token first
  line per the body-status-token rule) misread them. The fix prepends the seed's
  `top_status` (`VERIFIED`/`GO`) as the first line and mirrors it into the seeded
  `INDEX.md`. The correction is tightly scoped to that status-token fixture defect,
  lives entirely within the GO'd target file
  `platform_tests/scripts/test_project_verified_completion_scanner.py`, and removes
  no tests (collection is unchanged at 47). The full target-file run is now green:
  **47 passed**. No owner/governance waiver is required because the red run was
  corrected, which is the resolution Codex preferred in `-004` ("fold the fixture
  correction into the revised packet, then rerun the full target-file command").
- **P2 (report metadata said `bridge_kind: prime_proposal`).** Corrected: this
  report carries `bridge_kind: implementation_report`.

The previously-captured WI-4751 (the `_seed` status-token fixture defect) is
resolved by being folded into this thread under the same GO'd target file; it
should be marked resolved/superseded-by-WI-4737 rather than carried as separate
open work.

## What Was Implemented

The additive, id-agnostic recognition path preserves the deliberately narrow
`_WORK_ITEM_LINE_RE` (untouched) and is applied byte-mirrored across both
completion surfaces:

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` — new helpers
  `_thread_slug_from_ref` (normalizes a `related_bridge_threads` entry — bare slug
  or `bridge/<slug>-NNN.md` path — to a bare slug) and `_related_thread_slugs`
  (parses the field into a slug set, defensively tolerating missing/malformed
  values), and the augmentation inside `_verified_work_items_by_project`: a
  membership WI is verified-for-project P when P holds an active `implements` link
  to a VERIFIED-topped thread AND that same thread slug appears in the WI's own
  `related_bridge_threads`.
- `scripts/project_verified_completion_scanner.py` — the byte-identical
  `_thread_slug_from_ref` / `_related_thread_slugs` helpers plus
  `_augment_verified_with_related_threads`, wired into `verified_work_items_by_project`.

The two-sided guard (project implements-link AND the WI's own
`related_bridge_threads` must both reference the same VERIFIED thread) preserves the
prior design's two-sided shape without depending on the WI-ID regex or a
regex-parseable `Work Item:` line in the bridge file.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` — implementation corrected to
  satisfy the existing requirement (recognize work items whose bridge threads
  reached VERIFIED) for cases the regex-only path missed. No requirement text changes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; dispatcher/TAFE state + numbered chain canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage triple present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below with executed results.
- `GOV-RELIABILITY-FAST-LANE-001` — defect-origin source+test fix under the standing reliability authorization; creates no spec.
- `GOV-STANDING-BACKLOG-001` — WI-4737 tracked (member of PROJECT-GTKB-RELIABILITY-FIXES and the GTKB-DETERMINISTIC-SERVICES-001 umbrella).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all four target paths in-root; no application file.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; carried forward per the `-004` applicability table.

## Prior Deliberations

- `bridge/gtkb-completion-gate-noncanonical-wi-recognition-002.md` (GO) and `-004` (NO-GO) — this thread's own verdicts; `-005` addresses the `-004` findings.
- `bridge/gtkb-project-completion-scanner-wi-auto-regex-fix-008.md` (WI-3335, VERIFIED; `DELIB-20260611`, GO `DELIB-20264651`) — established the deliberately-narrow canonical-ID regex and the byte-identical mirror this fix preserves.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v5 (owner approval `DELIB-20265228`) — automatic completion-when-VERIFIED remains default.

## Owner Decisions / Input

No fresh owner approval is required. WI-4737 is a defect-origin reliability fix on
the reliability fast-lane (member of PROJECT-GTKB-RELIABILITY-FIXES; covered by the
active standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, classes
`source`/`test_addition`/`hook_upgrade`, coverage by membership). It creates no
specification or formal artifact. No waiver is requested: the `-004` P1 red run was
corrected (full run now green), so the verification gate passes on real evidence
rather than on an accepted-failure waiver. Motivating directive (context, not an
approval gate): the 2026-06-22 owner directive to drive
`PROJECT-GTKB-DETERMINISTIC-SERVICES-001` to VERIFIED/retired.

## Spec-to-Test Mapping

| Specification | Test / Verification | Executed | Result |
|---|---|---|---|
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | 4 WI-4737 regression tests (package service + scanner; positive recognition + two-sided negative guards): `test_wi4737_lifecycle_noncanonical_recognized_via_related_bridge_threads`, `test_wi4737_lifecycle_two_sided_guard_rejects_unlinked_and_unverified`, `test_wi4737_noncanonical_wi_recognized_via_related_bridge_threads`, `test_wi4737_two_sided_guard_rejects_unlinked_and_unverified` | yes | PASS (included in the full run below) |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` + GO full-target verification expectation | full target-file pytest (both files) | yes | **PASS: 47 passed** |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | this mapping + executed results | yes | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | target-path inspection | yes | PASS: all in-root |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | numbered chain / status inspection | yes | PASS: `-005` REVISED, LO-actionable |

## Verification Evidence (exact)

```text
$ groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_project_artifacts.py platform_tests/scripts/test_project_verified_completion_scanner.py -q --no-header --basetemp .gtkb-state/pytest-wi4737-final
47 passed, 2 warnings in 55.68s

$ groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py scripts/project_verified_completion_scanner.py groundtruth-kb/tests/test_project_artifacts.py platform_tests/scripts/test_project_verified_completion_scanner.py
All checks passed!

$ groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py scripts/project_verified_completion_scanner.py groundtruth-kb/tests/test_project_artifacts.py platform_tests/scripts/test_project_verified_completion_scanner.py
4 files already formatted
```

(The host temp-directory ACL issue Codex noted at `-004` is avoided with an in-root `--basetemp`; the run is green independent of that.)

## Mirror Confirmation

The package service (`lifecycle.py`) and the scanner (`project_verified_completion_scanner.py`)
carry the same `_thread_slug_from_ref` / `_related_thread_slugs` helpers and the same
two-sided `related_bridge_threads` recognition predicate. `_WORK_ITEM_LINE_RE`
remains byte-identical and narrow in both. The four regression tests assert the
identical recognition behavior on both surfaces.

## Recommended Commit Type

`fix` — corrects a completion-gate recognition defect plus a tightly-scoped test
fixture status-token defect; no new capability surface, no spec promotion.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
