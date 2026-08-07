NEW
::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-07T14-51-23Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;build activity
author_metadata_source: explicit_interactive_session_metadata

# GT-KB Bridge Implementation Report - gtkb-wi6009-harness-parity-projection-coverage - 003

bridge_kind: implementation_report
Document: gtkb-wi6009-harness-parity-projection-coverage
Version: 003
Responds to: bridge/gtkb-wi6009-harness-parity-projection-coverage-002.md
Approved proposal: bridge/gtkb-wi6009-harness-parity-projection-coverage-001.md
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-6009
Recommended commit type: feat:

## Implementation Claim

Implemented WI-6009 "Harness parity projection coverage" as two surgical edits to
`scripts/check_harness_parity.py`, plus two focused tests.

- **Change (A) — explicit harness scope honored unconditionally.** The lifecycle
  filter in `check_harness_parity` previously dropped any harness whose
  lifecycle class was `suspended` before comparison could run. It is now:
  `if lifecycle == "suspended" and not explicit_harness: continue`. When
  `--harness <name>` names a single harness, that harness is evaluated
  regardless of lifecycle status. Default `--all` behavior is unchanged. This
  restores the detector's ability to observe drift on a suspended harness under
  manual-only operation (the condition under which lifecycle no longer predicts
  which harnesses are doing work).

- **Change (B) — canonical-versus-adapter tree comparison.** Added
  `HARNESS_ADAPTER_SKILLS_ROOT` (a harness -> adapter skills-tree root map,
  canonical `.claude/skills` exempted) and `_projection_drift_extras()`, which
  compares the canonical skill-name set against each evaluated harness's adapter
  tree and emits two new WARN row kinds:
  - `MISSING_PROJECTION` — canonical skill absent from the harness adapter tree.
  - `UNTRACKED_SURFACE` — adapter-tree skill absent from canonical (a projection
    target exceeding its source).
  These rows are merged into the report's `extras` (only when no hard errors).
  Severity is deliberately `WARN` (not `FAIL`) so the checker does not fail on
  arrival; the corpus is not yet clean because `gtkb-skill-rollout` remains
  undeclared/unprojected (remediation is WI-6008, out of scope).

Behavior confirmed with `python scripts/check_harness_parity.py --harness goose --markdown`:
the `Harnesses:` line is now populated (`goose`), and the report surfaces
`MISSING_PROJECTION gtkb-skill-rollout` plus `UNTRACKED_SURFACE gtkb-codex-report`
and `gtkb-kb-work-item`, with overall status `WARN` and exit code 0.

This implementation performs no KB/MemBase mutation: it changes only the two
source/test target paths declared above and does not write to `groundtruth.db`
or any MemBase/Deliberation-Archive surface. `kb_mutation_in_scope` remains
`false` as declared in the approved proposal.

## Specification Links

- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

No new owner decision is required by this implementation report. The proposal
carried three owner directives from the 2026-08-07 session transcript (common
baseline via projection; raise work items rather than duplicate; manual-only
operation with legacy FE dispatcher/daemon disabled) — all remain satisfied and
carried forward. The severity question (eventual FAIL promotion of the new rows)
is explicitly deferred to the WI-6008 follow-on as stated in the approved proposal.

## Prior Deliberations

- `bridge/gtkb-wi6009-harness-parity-projection-coverage-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi6009-harness-parity-projection-coverage-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` | `python scripts/check_harness_parity.py --harness goose --markdown` -> `Harnesses: goose`, `MISSING_PROJECTION gtkb-skill-rollout`, `UNTRACKED_SURFACE gtkb-codex-report`, `UNTRACKED_SURFACE gtkb-kb-work-item`, overall `WARN`, exit 0. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Change (A) restores evaluation of an explicitly-named harness; covered by new `test_explicit_harness_scope_evaluates_suspended_harness` (passed). |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | Undetected projection drift now surfaces as WARN rows across adapter trees; covered by new `test_projection_drift_reports_missing_and_untracked_surfaces` (passed). |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `_projection_drift_extras` derives the canonical set from `.claude/skills/*` (`inventory_project_skills` semantics); verified via the two new tests and the live `--harness goose` run. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Report filed as the append-only `-003` of the numbered bridge chain via the governed `impl_report_bridge.py` helper. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the full specification-link set from the approved proposal. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header carries Project Authorization / Project / Work Item triple (`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730`, `PROJECT-GTKB-HOUSEKEEPING-HARDENING`, `WI-6009`). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Spec-derived tests executed: `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q --tb=short` -> 45 passed, 1 failed (pre-existing, see Observed Results). |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation proceeded under active PAUTH v2 plus live bridge `GO` (`-002`) plus implementation-start packet and matching work-intent claim (session `G-2026-08-07T14-51-23Z`). |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | No bridge bypass: only the two target paths were mutated under the GO + claim + implementation-start. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both target paths are inside `E:/GT-KB`; nothing under `applications/` was touched. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Drift is recorded as durable work items (WI-6007/WI-6008/WI-6011), not session context. |
| `GOV-STANDING-BACKLOG-001` | The drift captures remain in the MemBase backlog; this implements WI-6009 without absorbing WI-6008. |

## Commands Run

- `python -m py_compile scripts/check_harness_parity.py` -> success.
- `python scripts/check_harness_parity.py --harness goose --markdown` -> `Harnesses: goose`; `MISSING_PROJECTION gtkb-skill-rollout`; `UNTRACKED_SURFACE gtkb-codex-report`; `UNTRACKED_SURFACE gtkb-kb-work-item`; overall `WARN`; exit code 0.
- `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q --tb=short -k "suspended_harness or projection_drift"` -> 2 passed.
- `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q --tb=short` -> 45 passed, 1 failed.
- `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q --tb=short` (baseline, committed HEAD without this change, via `git stash`) -> 43 passed, 1 failed (same pre-existing failure).

## Observed Results

- Compile: clean.
- Live checker on `--harness goose`: the previously-empty `Harnesses:` line is now `goose` (change A verified), and the projection-drift rows appear as designed (change B verified), at WARN severity with exit 0.
- New focused tests both pass:
  - `test_explicit_harness_scope_evaluates_suspended_harness` (change A).
  - `test_projection_drift_reports_missing_and_untracked_surfaces` (change B).
- Full test file: 45 passed / 1 failed. The single failure is
  `test_repository_registry_covers_project_skills`, which fails on the
  pre-existing `gtkb-skill-rollout` `EXTRA` row (the skill exists in canonical
  `.claude/skills` but is undeclared in the capability registry). This is the
  known dirty corpus owned by WI-6008, which the approved proposal explicitly
  scopes out. I verified this failure exists identically on the committed
  baseline (43 passed / 1 failed before my change), so it is NOT a regression
  introduced by WI-6009.

## Files Changed

- `platform_tests/scripts/test_check_harness_parity.py`
- `scripts/check_harness_parity.py`

Excluded out-of-scope dirty paths: 772.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: The diff adds or changes skill, script, or platform capability surfaces.

```text
     .../scripts/test_check_harness_parity.py           | 79 +++++++++++++++++++++
     scripts/check_harness_parity.py                    | 81 +++++++++++++++++++++-
     2 files changed, 158 insertions(+), 2 deletions(-)
```

## Acceptance Criteria Status

- [x] Change (A): explicit `--harness` scope evaluates a suspended harness (verified live + test).
- [x] Change (B): canonical-vs-adapter tree comparison emits `MISSING_PROJECTION` and `UNTRACKED_SURFACE` WARN rows (verified live + test).
- [x] Severity stays WARN, not FAIL (exit 0), so no gate flips on arrival.
- [x] No adapter regenerated, no stale directory removed, no registry entry added (all out of scope).
- [x] No regression introduced: the one failing test is pre-existing (WI-6008), confirmed against committed baseline.

## Risk And Rollback

- **Residual risk (low):** Reporting volume grows for adapter trees not recently
  inspected. Kept at WARN so no gate flips. The `.goose` stale directories
  (`gtkb-codex-report`, `gtkb-kb-work-item`) are flagged but not removed; their
  removal is out of scope (WI-6008 / separate cleanup).
- **Rollback:** Both changed files are plain source + test edits. Reverting
  `scripts/check_harness_parity.py` and `platform_tests/scripts/test_check_harness_parity.py`
  to HEAD fully restores prior behavior. Bridge audit files remain append-only
  and are not reverted.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.

---

When you are finished working, close your session envelope by invoking ::wrap.
