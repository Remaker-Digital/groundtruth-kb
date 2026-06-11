NEW

bridge_kind: prime_proposal
Document: gtkb-cheap-draft-linter
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — autonomous scheduled session
Date: 2026-06-11

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4437
Project Authorization: PAUTH-DRAFTLINTER-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: f2bde760-42de-44f1-aae6-eee14d7ee5a7
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: autonomous scheduled session (keep-working-pb), Prime Builder

target_paths: ["scripts/draft_lint.py", "platform_tests/scripts/test_draft_lint.py"]

---

# Cheap-model draft-linter — Post-Implementation Report

Implementation report for `gtkb-cheap-draft-linter`, GO at
`bridge/gtkb-cheap-draft-linter-002.md`. WI-4437 of PROJECT-FABLE-INVESTIGATION
(campaign-support tooling). Implemented by Prime Builder harness B (Opus 4.8)
under impl-start packet
`sha256:e29291c51e6c3af2707406d853e827ff661246c9721073aa7e6d2058c8d3125e`
(created from the live `GO` at `-002`; expires 2026-06-11T13:10:51Z).

## Summary

The GO'd deterministic draft-linter is implemented end-to-end as two net-new,
read-only files. `scripts/draft_lint.py` runs the six specified checks
(cited-path resolution, HYG-id match, phantom-spec, required-section presence,
placeholder detection, GOV-18 concrete-assertion floor) over a cheap-model draft
body and emits PASS/FAIL JSON with per-check findings; exit 0 when no check FAILs,
1 otherwise. `platform_tests/scripts/test_draft_lint.py` exercises a PASS and a
FAIL branch for every check, plus an AST-based read-only contract test
(DELIB-S312) asserting the linter performs no file writes, no MemBase mutation,
and imports no mutating module. The linter is advisory to the author's drafting
step; it does not write, does not mutate MemBase, is not wired into any bridge
hook, and does not replace Opus finalization or Codex review — exactly the GO
constraints.

## Specification Links

Carried forward from `-001` (GO'd at `-002`):

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle authority for this report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs
  cited (carried forward).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the spec-to-test mapping +
  command evidence below satisfy this gate.
- `GOV-STANDING-BACKLOG-001` — WI-4437 is the governed backlog authority.
- `SPEC-1662` (GOV-18 assertion quality) — check 6 enforces that a draft's
  verification section carries at least one concrete (non-rubber-stamp) assertion.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all created artifacts remain in-root
  under `E:\GT-KB`; no application-placement boundary is touched (see Isolation
  Placement Compliance below).

Governing principle (non-spec): `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` —
repetitive mechanical checking belongs in a deterministic service; the read-only
contract test encodes this as an executable invariant.

## Isolation Placement Compliance

All created artifacts remain within the GT-KB root `E:\GT-KB`: `scripts/draft_lint.py`
and `platform_tests/scripts/test_draft_lint.py` are both in-root. No file was
created or required outside `E:\GT-KB`; the linter reads only repo-relative paths
under the project root and the in-root canonical MemBase (`groundtruth.db`),
opened read-only. No application-placement boundary is touched (no application
subtree artifact created or moved).

## Prior Deliberations

- `DELIB-DRAFTLINTER-20260610` — owner agreement to build the deterministic
  draft-linter as the top QA measure for the cheap-drafting workflow, with the
  no-rubber-stamp / no-review-bypass rules.
- `bridge/gtkb-fable-investigation-advisory-001.md` — campaign charter (the cheap
  drafting workflow this gate protects).
- `bridge/gtkb-cheap-draft-linter-001.md` — the GO'd proposal whose target paths,
  six checks, and verification plan this report implements.
- `bridge/gtkb-cheap-draft-linter-002.md` — the GO with implementation constraints
  honored below.

## Owner Decisions / Input

The implemented work is bounded by the owner decision captured in
`DELIB-DRAFTLINTER-20260610` (collected via `AskUserQuestion` on 2026-06-10): the
owner agreed to build the deterministic draft-linter first, as an author-side QA
floor that augments — never replaces — Opus finalization and Codex Loyal
Opposition `GO`. No new owner decision was required for implementation: the `GO`
at `-002` is the per-cluster authorization moment, and the work stays inside the
GO'd `target_paths` and the `PAUTH-DRAFTLINTER-20260610` mutation classes
(`source`, `test_addition`).

## Requirement Sufficiency

Existing requirements sufficient (carried forward from `-001`). The linter
operationalizes `SPEC-1662` (GOV-18) and `DELIB-S312` for the cheap-drafting
workflow; it introduces no new requirement.

## Files Changed

**Created (2):**

- `scripts/draft_lint.py` (≈230 lines) — the read-only deterministic linter:
  six checks, JSON report, `lint()` pure-function core, and a `main()` CLI taking
  a draft file (or stdin), optional `--hyg-ids` baseline, `--new-paths` exemptions,
  and a read-only `--db` (defaults to the in-root canonical MemBase). The
  phantom-spec check opens MemBase with a `mode=ro` URI and queries
  `current_specifications` (the latest-version view); it degrades to a `skip`
  status (never a crash) when the DB is absent or unreadable.
- `platform_tests/scripts/test_draft_lint.py` (14 tests) — PASS + FAIL branch per
  check on crafted fixtures, an in-memory fixture DB for the phantom-spec check
  (keeping it independent of the live `groundtruth.db`), an end-to-end CLI
  exit-code test, and the AST read-only contract test.

No existing file was modified; no MemBase row was written.

## Spec-Derived Verification Plan (with observed results)

| Spec / requirement | Derived test | Result |
|---|---|---|
| `SPEC-1662` (GOV-18 assertion quality) | `test_assertion_floor_fail_on_rubber_stamp` (prose-only verification FAILs check 6); `test_assertion_floor_pass_on_concrete` (a `pytest … 5/5 PASS` body passes) | PASS |
| `DELIB-S312` (deterministic, read-only) | `test_linter_is_read_only` — AST asserts no write-mode `open`, no `.write`/`.writelines`/`.truncate`, no mutating SQL literal, no `subprocess`/`shutil`/`os` import | PASS |
| phantom-spec correctness | `test_phantom_spec_fail` (a non-existent id FAILs check 3); the clean draft's real ids pass; `test_phantom_spec_skip_when_db_missing` (no crash) | PASS |
| HYG-id integrity | `test_hyg_id_match_fail` (stray id FAILs); `test_hyg_id_skip_without_baseline` | PASS |
| cited-path resolution | `test_cited_path_resolution_fail` (hallucinated path FAILs); `test_cited_path_target_paths_exempt` (declared new path exempt) | PASS |
| required sections | `test_required_sections_fail` (missing Risk section FAILs) | PASS |
| placeholder detection | `test_placeholder_fail` (`TBD`); `test_placeholder_template_fail` (`<topic>`) | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/test_draft_lint.py` + `ruff check`/`format --check` | PASS |

### Commands and observed results

Interpreter: `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe` (Python 3.14.0).

- `python -m pytest platform_tests/scripts/test_draft_lint.py -q` → **14 passed in 0.41s**.
- `python -m ruff check scripts/draft_lint.py platform_tests/scripts/test_draft_lint.py`
  → **All checks passed!**
- `python -m ruff format --check scripts/draft_lint.py platform_tests/scripts/test_draft_lint.py`
  → **2 files already formatted**.
- `python scripts/draft_lint.py bridge/gtkb-fab-08-slot-leak-fix-001.md --hyg-ids "HYG-053,HYG-022"`
  (real cheap-drafted proposal, against the canonical in-root MemBase) →
  `"ok": true`, **6/6 checks pass**, exit 0 (acceptance criterion 3 evidence: a
  clean, actionable report on a real draft, including a live phantom-spec query
  that confirmed every cited spec id resolves).

## Acceptance Criteria — Status

1. `scripts/draft_lint.py` runs the 6 checks and emits PASS/FAIL JSON; read-only —
   **MET** (read-only proven by the AST contract test).
2. The test exercises PASS + FAIL for each check; all pass; ruff-clean — **MET**
   (14 passed; ruff check + format clean).
3. Running it on the validated FAB-08 Qwen draft produces a clear, actionable
   report — **MET** (6/6 pass JSON on `bridge/gtkb-fab-08-slot-leak-fix-001.md`).

## GO Implementation-Constraint Compliance (`-002`)

- Did NOT wire the linter into any bridge hook or preflight infrastructure. ✓
- Did NOT make linter PASS a substitute for Opus finalization or Codex review
  (the module docstring states this explicitly; it is an author-side check). ✓
- Kept the linter read-only: no MemBase writes, no proposal rewrites, no draft
  mutation (enforced mechanically by `test_linter_is_read_only`). ✓
- Stayed inside the GO'd `target_paths` (the two files) and the PAUTH mutation
  classes (`source`, `test_addition`). ✓

## Bridge Protocol Compliance

This report is filed as `bridge/gtkb-cheap-draft-linter-003.md` and its `NEW`
status line is inserted at the top of the `gtkb-cheap-draft-linter` entry in
`bridge/INDEX.md`, which remains the canonical bridge workflow state. The
append-only version chain is preserved (`-001` NEW → `-002` GO → `-003` NEW
report); no prior bridge file was modified or deleted.

## Backlog Visibility

This report performs no bulk backlog operation. WI-4437 remains the single
governed work item; its resolution to a terminal lifecycle state is deferred to a
post-`VERIFIED` operational step (an inventory/backlog-state reconciliation), not
performed in this implementation.

## Recommended Commit Type

`feat:` — net-new deterministic QA service + its test. Diff stat: 2 files created,
0 modified, 0 deleted.

## Risk and Rollback

- **Risk:** check 1 (cited-path) or check 3 (phantom-spec) could false-positive on
  a legitimate token; both report *which* token failed so the author adjudicates,
  and the linter is advisory to Opus finalization, not a hard bridge block in this
  slice. Check 3 degrades to `skip` (never an error) when MemBase is unavailable.
- **Rollback:** delete `scripts/draft_lint.py` + `platform_tests/scripts/test_draft_lint.py`;
  the cheap-drafting workflow reverts to manual Opus QA. No other surface is touched.
