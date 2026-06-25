NEW

# Startup-disclosure open-work-items metric: show subject-scoped AND raw counts

bridge_kind: prime_proposal
Document: gtkb-startup-open-work-items-metric-raw-count
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: claude-prime-interactive-may29-hygiene-drive-20260625
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; Prime Builder role (harness B); explanatory output style; may29-hygiene retirement drive

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-3327

target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization.py"]

implementation_scope: source,test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-3327 records that the startup-disclosure "open MemBase work items" metric
reads as a total when it is actually a subject-scoped count (the work item filed
it as "reported 3 vs actual 139 open"). Investigation confirms the metric layer
is correct but the *render* is ambiguous:

- `scripts/session_self_initialization.py` already computes BOTH
  `metrics["membase"]["open_work_items"]` (the work-subject-scoped open count, via
  `_is_dashboard_subject_scope`, line ~1241) AND
  `metrics["membase"]["raw_open_work_items"]` (the all-subjects open count, line
  ~1242).
- But the two disclosure render sites show only the scoped value:
  - startup disclosure line ~4614:
    `f"- {subject_label} open MemBase work items: {metrics['membase'].get('open_work_items')}"`
  - wrap-up report line ~5216:
    `f"- Open MemBase work items: {metrics['membase'].get('open_work_items')}"`

So the displayed count (e.g., 15 under `gtkb_infrastructure` scope) reads as the
total even though the all-subjects open count is much larger. This is a clarity
defect, not a computation defect: the raw count is already available and simply
not shown.

This proposal renders BOTH counts with a clarifying parenthetical, mirroring the
existing disambiguation precedent one line above (line ~4615 already labels the
contention metric "dashboard-scoped ... non-authoritative for queue state"). No
metric computation changes.

## Proposed Change

1. `scripts/session_self_initialization.py` (source): at the two render sites,
   render the subject-scoped count plus the raw all-subjects count when the raw
   value is present, e.g.
   `open MemBase work items: 15 (subject-scoped; 139 across all subjects)`.
   When `raw_open_work_items` is absent or equals the scoped value, omit the
   parenthetical (graceful `.get()` fallback so existing render fixtures that
   carry only `open_work_items` continue to render without `None`).
2. `platform_tests/scripts/test_session_self_initialization.py` (test_addition):
   update the render fixture that currently supplies
   `"membase": {"open_work_items": 0}` (line ~2429) to also supply
   `raw_open_work_items`, and add a regression assertion that, when the scoped
   and raw counts differ, the rendered disclosure shows both values and labels
   the displayed one as subject-scoped.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` — Governs the fresh-session startup
  disclosure and its project-state metrics; this proposal corrects an ambiguous
  metric render in that disclosure.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — State claims (including displayed open
  work-item counts) must be accurate and unambiguous; showing the raw count
  prevents a subject-scoped value from being misread as the total.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — Requires this source/test change to move
  through the governed file bridge with GO before implementation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Requires this
  proposal to cite governing requirements rather than implied process memory.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Requires explicit
  linkage to the active project, work item, and project authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Requires the
  implementation report to include verification derived from the cited
  requirements (the updated/added test).
- `GOV-STANDING-BACKLOG-001` — WI-3327 is a standing-backlog hygiene item under
  PROJECT-GTKB-MAY29-HYGIENE.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — The active May29 Hygiene
  bounded-implementation authorization includes WI-3327 and allows `source` and
  `test_addition` mutation classes.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — The open-work-items subject-scope
  filter is exactly the platform-vs-application (GT-KB-infrastructure vs Agent
  Red) boundary this ADR governs; the change preserves that scope distinction
  and surfaces it in the disclosure rather than collapsing scoped and raw counts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — Converts the observed startup-metric
  ambiguity (WI-3327) into a durable, tested render correction.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — Favors a reviewable, regression-
  tested artifact change over an untracked tweak to the disclosure text.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — The recurring "3 vs 139" confusion
  crosses the threshold from observation into a tracked, fixed artifact.

## Prior Deliberations

- `WI-3465` (resolved) "Reconcile work_list.md vs MemBase work_items counts in
  session-startup metrics" — prior startup-metric count reconciliation; this
  proposal continues that lineage at the render layer.
- `WI-3466` (resolved) "Fix vestigial Agent Red scope filter naming on GT-KB
  MemBase work-item count" — prior work on the subject-scope filter that produces
  the scoped-vs-raw distinction this proposal surfaces.
- `WI-3409` startup-disclosure label-format contract — the in-code comment at
  `scripts/session_self_initialization.py:~4618` records that the
  Testing/tool-rollup label format is a contract checked by
  `platform_tests/scripts/test_session_self_initialization.py`; this proposal
  preserves the "open MemBase work items: <n>" prefix and appends a parenthetical
  suffix in the same non-breaking style.
- _No prior bridge deliberation specifically resolves the scoped-vs-raw render
  ambiguity for the open-work-items line; this is the first proposal targeting
  it._

## Owner Decisions / Input

- AskUserQuestion (2026-06-25): owner directed "File WI-3327" as part of the
  PROJECT-GTKB-MAY29-HYGIENE retirement drive (tail-disposition decision
  "File WI-3327, defer WI-4771"). This authorizes filing this proposal.

No further owner decision is required for implementation: the active project
authorization
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23`
includes WI-3327 and permits the `source` and `test_addition` mutation classes
this change uses.

## Requirement Sufficiency

Existing requirements are sufficient. WI-3327, the active May29 Hygiene project
authorization, `GOV-SESSION-SELF-INITIALIZATION-001`, and
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001` provide enough direction for a render-clarity
fix plus regression test. No new or revised requirement is needed.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | No credential material; counts and labels only. | Credential scan on the diff. |  |
| CQ-PATHS-001 | Yes | Edits limited to the two declared target paths. | `git diff --name-only` matches target_paths. |  |
| CQ-COMPLEXITY-001 | Yes | Render change is a small f-string + a graceful `.get()` fallback; no new control complexity. | Diff review. |  |
| CQ-CONSTANTS-001 | N/A | No runtime constants changed. | Diff review. | Label text only. |
| CQ-SECURITY-001 | N/A | No security-relevant surface. | Diff review. | Disclosure text only. |
| CQ-DOCS-001 | Yes | The clarifying label is self-documenting; no separate doc needed. | Render output review. |  |
| CQ-TESTS-001 | Yes | Add/extend a regression test asserting both counts render. | `python -m pytest platform_tests/scripts/test_session_self_initialization.py`. |  |
| CQ-LOGGING-001 | N/A | No logging changes. | Diff review. | N/A. |
| CQ-VERIFICATION-001 | Yes | Exact commands + observed results captured in the implementation report. | LO reproduces the pytest + ruff runs. |  |

## Spec-Derived Verification Plan

- `GOV-SESSION-SELF-INITIALIZATION-001` and `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`:
  Render the startup disclosure with a fixture where scoped != raw and assert the
  output line shows both the scoped count and the raw all-subjects count with a
  subject-scoped label. Command:
  `python -m pytest platform_tests/scripts/test_session_self_initialization.py -q`.
  Expected result: pass, including the new both-counts assertion.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: The implementation report
  carries the spec-to-test mapping (this section) and the executed pytest +
  `ruff check` + `ruff format --check` evidence for the two changed files.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: Inspect with
  `gt bridge show gtkb-startup-open-work-items-metric-raw-count`. Expected
  result: latest status `NEW`, intact version chain.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` /
  `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: `gt projects show
  PROJECT-GTKB-MAY29-HYGIENE` confirms WI-3327 membership and the active bounded
  authorization covering `source` + `test_addition`.
- Root boundary: `git diff --name-only` limited to
  `scripts/session_self_initialization.py` and
  `platform_tests/scripts/test_session_self_initialization.py` (both in-root).

## Risk / Rollback

Risk is low: a label-render change plus a regression test, no metric computation
or behavior change. The main risk is breaking the existing startup-disclosure
format contract checked by
`platform_tests/scripts/test_session_self_initialization.py`; the change
preserves the "open MemBase work items: <n>" prefix and appends a parenthetical
suffix in the same non-breaking style used for the WI-3409 queried_repo suffix
and the line-4615 contention disambiguation. Rollback is a single-commit revert.

## Recommended Commit Type

`fix:` — corrects a misleading startup-disclosure metric render (a defect in the
displayed value's clarity), with an accompanying regression test.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
