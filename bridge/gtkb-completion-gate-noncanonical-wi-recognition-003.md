NEW

# Implementation Report — completion-gate id-agnostic recognition path (WI-4737)

bridge_kind: prime_proposal
Document: gtkb-completion-gate-noncanonical-wi-recognition
Version: 003
Responds-To: bridge/gtkb-completion-gate-noncanonical-wi-recognition-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-06-22 UTC

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

Implemented the GO'd (`-002`) additive, id-agnostic recognition path. The
completion gate now recognizes a membership work item as verified-for-project
when **(a)** the project holds an active `relationship='implements'` link to a
thread that is **(b)** VERIFIED-topped, and **(c)** that thread is named in the
work item's own `related_bridge_threads` field. The deliberately-narrow
`_WORK_ITEM_LINE_RE` is unchanged; the existing regex path is unchanged and
remains primary; the new path only adds recognitions. The change is mirrored
across both completion surfaces.

## Changes (per target path)

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
  - Added `import json`.
  - Added two module-level helpers `_thread_slug_from_ref` and
    `_related_thread_slugs` (normalize a `related_bridge_threads` entry — bare
    slug or `bridge/<slug>-NNN.md` path — into a set of slugs; defensive parse).
  - Augmented `ProjectLifecycleService._verified_work_items_by_project`: after
    the unchanged regex path, for each project compute the VERIFIED-topped
    implements-linked slugs (via the existing `_latest_bridge_thread_statuses`)
    and add any active-member WI whose `related_bridge_threads` intersects that
    set.
- `scripts/project_verified_completion_scanner.py`
  - Added the byte-identical `_thread_slug_from_ref` / `_related_thread_slugs`
    helpers (the file already imports `json`).
  - Added `_latest_bridge_thread_statuses` (mirror of the lifecycle method) and
    `_augment_verified_with_related_threads` (opens a read-only DB only when at
    least one VERIFIED implements-linked thread exists, since `scan()` closes
    its own DB before calling `verified_work_items_by_project`; signature of the
    public function is unchanged so all callers — `scan`, `cli_backlog_status`,
    tests — are unaffected).
  - Wired the augmentation into `verified_work_items_by_project` after the
    unchanged regex path.
- `groundtruth-kb/tests/test_project_artifacts.py` — added IP-3 tests
  (`test_wi4737_lifecycle_noncanonical_recognized_via_related_bridge_threads`
  positive + `test_wi4737_lifecycle_two_sided_guard_rejects_unlinked_and_unverified`
  negative).
- `platform_tests/scripts/test_project_verified_completion_scanner.py` — added
  IP-4 tests
  (`test_wi4737_noncanonical_wi_recognized_via_related_bridge_threads` positive +
  `test_wi4737_two_sided_guard_rejects_unlinked_and_unverified` negative).

## Mirror Confirmation

The recognition logic is mirrored. `_thread_slug_from_ref` and
`_related_thread_slugs` are byte-identical in both files. The decision predicate
is identical in both surfaces: a WI is added iff it is an active member AND
`_related_thread_slugs(wi.related_bridge_threads) & {VERIFIED implements-linked
slugs}` is non-empty. The only structural difference is DB acquisition
(lifecycle uses the long-lived `self.db`; the scanner opens a short-lived
read-only `KnowledgeDB` because `scan()` has already closed its own), which does
not change the recognition decision.

## Specification Links (carried forward from -001)

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` — implementation corrected to
  satisfy the existing requirement (recognize WIs whose threads reached
  VERIFIED) for the id-agnostic case; no requirement text changed.
- `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`;
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-RELIABILITY-FAST-LANE-001`;
  `GOV-STANDING-BACKLOG-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.
- Advisory (carried forward per the -002 note): `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` —
  the WI-4737 defect, this thread, and the regression tests are linked artifacts
  preserving traceability; the fix corrects governed tooling without weakening it.

## Spec-to-Test Mapping

| Linked spec | Test(s) | Result |
|---|---|---|
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | `test_wi4737_lifecycle_noncanonical_recognized_via_related_bridge_threads` (package) + `test_wi4737_noncanonical_wi_recognized_via_related_bridge_threads` (scanner) | PASS — a non-canonical-id member WI whose VERIFIED implements-linked thread carries no parseable `Work Item:` line is recognized and the authorization completes |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (guard) | `test_wi4737_lifecycle_two_sided_guard_rejects_unlinked_and_unverified` (package) + `test_wi4737_two_sided_guard_rejects_unlinked_and_unverified` (scanner) | PASS — a WI citing a VERIFIED-but-unlinked thread, or an implements-linked-but-GO thread, is NOT recognized |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | the four tests above are the spec-to-test mapping | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | all four target paths in-root, no application file | confirmed |

## Verification Evidence

Targeted run of the four new WI-4737 tests:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest \
  platform_tests/scripts/test_project_verified_completion_scanner.py::test_wi4737_noncanonical_wi_recognized_via_related_bridge_threads \
  platform_tests/scripts/test_project_verified_completion_scanner.py::test_wi4737_two_sided_guard_rejects_unlinked_and_unverified \
  groundtruth-kb/tests/test_project_artifacts.py::test_wi4737_lifecycle_noncanonical_recognized_via_related_bridge_threads \
  groundtruth-kb/tests/test_project_artifacts.py::test_wi4737_lifecycle_two_sided_guard_rejects_unlinked_and_unverified \
  --no-header
→ 4 passed
```

Full target-file run:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_project_artifacts.py platform_tests/scripts/test_project_verified_completion_scanner.py -q --no-header
→ 7 failed, 40 passed
```

Lint + format (all four target paths):

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check  <4 target paths>  → All checks passed!
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <4 target paths>  → 4 files already formatted
```

## Pre-Existing Failures Disclosure (NOT introduced by this change)

The 7 failures in the full run are **pre-existing** and **unrelated to WI-4737**.
All 7 live in `platform_tests/scripts/test_project_verified_completion_scanner.py`
and stem from the `_seed` helper (line ~65) writing each bridge fixture with
`# Proposal {slug}` as its first line and NO canonical first-line status token,
relying on an INDEX `VERIFIED:` line. Per the mandatory body-status-token rule
(`.claude/rules/file-bridge-protocol.md`), `status_from_bridge_file` reads the
first non-blank line and returns `None` for these fixtures, so the regex
completion path yields empty for them.

Proof of pre-existing nature (stash test, 2026-06-22): with this change's two
source files stashed (HEAD versions of `lifecycle.py` + the scanner), the SAME 7
tests fail, plus the new positive scanner test (expected — HEAD has no
augmentation):

```text
git stash push -- <lifecycle.py> <scanner.py>
pytest platform_tests/scripts/test_project_verified_completion_scanner.py → 8 failed, 7 passed
git stash pop
```

The failing set is identical to the live run (the 8th HEAD failure is the new
positive test, which my change makes pass). This change is purely additive to
the regex path and can only ADD to the verified set, never empty it; it does not
touch `_seed`, `status_from_bridge_file`, or `_verified_thread_work_items`.

Scope discipline: per the `-002` GO ("add only the proposed
related-bridge-thread recognition path"), I did NOT modify the stale `_seed`
fixture under this thread. The fixture defect is captured as **WI-4751** (P2,
PROJECT-GTKB-RELIABILITY-FIXES) with the precise failing-test list and the
one-line fix (prepend `{top_status}\n\n` to the `_seed` bridge-file content).
The sibling helper `_seed_completion_env` in `test_project_artifacts.py` does
NOT have the defect, which is why all package-layer lifecycle tests (including
the two new ones) pass. If the reviewer prefers a green full-file run as a
verification condition, I will fold WI-4751's one-line fixture fix into a
REVISED on reviewer direction.

## Owner Decisions / Input

No fresh owner approval required. Reliability fast-lane defect fix under the
active standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
(source + test_addition by project membership); creates no specification and no
formal artifact. Motivating owner directive (context, not an approval gate): the
2026-06-22 owner directive to drive `PROJECT-GTKB-DETERMINISTIC-SERVICES-001` to
VERIFIED/retired, during which WI-4737 was captured.

## Prior Deliberations (carried forward from -001)

- `gtkb-project-completion-scanner-wi-auto-regex-fix` (WI-3335, VERIFIED;
  `DELIB-20260611` / GO `DELIB-20264651`) — established the deliberately narrow
  canonical regex and the mirrored-surface design this report preserves.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v5 (`DELIB-20265228`) —
  automatic completion-when-VERIFIED remains the default; this change restores
  that default's reach to id-agnostic work items without altering v5 semantics.

## Recommended Commit Type

`fix` — corrects a completion-gate recognition defect in existing platform code;
two source files augmented additively plus four regression tests; no new
capability surface, no spec promotion.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
