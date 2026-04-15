# GroundTruth-KB Phase 4B Plan

**Status:** ACTIVE — Phase 4B.7 in flight
**Created:** 2026-04-15 (S295)
**Baseline:** `docs/reports/v0.4-baseline/SUMMARY.md` (Phase 4A audit, 2026-04-14)
**Target exit:** Phase 4B complete when all Phase 4A baseline targets are met or explicitly deferred.

## What this document is

An explicit, numbered plan for the Phase 4B quality/hardening sub-rounds. It
replaces the implicit convention of naming sub-rounds as-they-come (4B.1,
4B.2, etc. inferred from commit messages and bridge entries) with a single
document that enumerates what is done, what is in flight, and what is
proposed next. Any new sub-round should be added here before a bridge
proposal is drafted.

Phase 4A (measurement baseline) is tracked separately in
`docs/reports/v0.4-baseline/SUMMARY.md`. Phase 4B consumes those baseline
numbers and drives them to their agreed targets.

## Baseline metrics (from Phase 4A, at `993f31b` / v0.4.0)

| Dimension | Baseline | 4B Target | Covering sub-round(s) |
|---|---|---|---|
| Line coverage (`pytest-cov`) | 51% | 70% line / 55% branch | 4B.8 (proposed) |
| Docstring coverage (whole package) | 60.42% | 80% | 4B.9 (proposed) |
| Public API docstring coverage | 81.63% | 95% | **4B.3 — DONE** (100% achieved) |
| `mypy --strict` errors | 169 | 0 on public API + bridge/ + helpers + intake/runtime | **4B.4 + 4B.5a + 4B.5b + 4B.7** |
| Broad exception sites | 31 (3 "needs review") | 3 flagged sites resolved or commented | 4D (proposed) |
| Logging infrastructure | 0 `logging` use in src/ | `logging.getLogger(__name__)` in bridge/db paths | 4C (proposed) |
| Config `GTConfig.load()` error paths | 13 failure modes, 2 silent | Findings 2, 3 fixed | **4B.1 — DONE** |

## Sub-round ledger

### Done (VERIFIED and merged to main)

| # | Sub-round | Scope | Commit | Bridge entry |
|---|---|---|---|---|
| **4B.1** | Config defensiveness | `GTConfigError` wrapping `FileNotFoundError` and `TOMLDecodeError` in `config.py`; findings 2 and 3 from Phase 4A | `2510f1d` | `gtkb-phase4b1-config-defensiveness-006` |
| **4B-housekeeping** | Cross-cutting hygiene | Anthropic `sk-ant-api*` redaction; `__main__.py`; 4 exit-code tables; `actions/checkout@v4→v6` across 8 workflows | `b41ab8f` | `gtkb-phase4b-housekeeping-004` |
| **4B.2** | Medium defensiveness | `PermissionError` wrap in `GTConfigError`; missing-section warning; unknown-keys warning; findings 4, 5, 6 from Phase 4A | `249cdd4` | `gtkb-phase4b2-medium-defensiveness-004` |
| **4B.3** | Public API docstrings | 27 `KnowledgeDB` + `GateRegistry` docstrings to 100%; regression guard `tests/test_public_api_docstrings.py` | `8151ed2` | `gtkb-phase4b3-public-api-docstrings-004` |
| **4B.4** | mypy --strict public API | 48 errors closed in `db.py`, `config.py`, `cli.py`, `gates.py`; insert/update return types widened to `dict[str, Any] \| None`; regression guard `tests/test_public_api_type_checks.py` | 4B.4 merge | `gtkb-phase4b4-mypy-strict-public-api-004` |
| **4B.5a** | bridge/ runtime annotations | ~52 annotative mypy errors closed in `bridge/` (missing `-> None`, typed parameters, `cast()` at well-defined boundaries) | `e15ceaf` + `efd0282` followup | `gtkb-phase4b5a-bridge-annotations-006` |
| **4B.5b** | Internal helpers mypy | 40 errors across 5 internal helper modules; CI regression guard via `tests/test_internal_helpers_type_checks.py` | `4870e7d` + `31d2c39` | `gtkb-phase4b5b-internal-helpers-mypy-007` |
| **4B.6** | CI enforcement gates | `mypy --strict` CI workflow step; per-file coverage gates (db.py 68% / cli.py 68% / config.py 80% / gates.py 92%); docstring-coverage ratchet 50→51 | `31d2c39` | `gtkb-phase4b6-ci-enforcement-gates-010` |
| **4B.7** | Residual mypy --strict | Closed 39 `mypy --strict` errors across 5 files (`bridge/poller.py` 17, `bridge/worker.py` 10, `intake.py` 7, `bridge/runtime.py` 4, `bridge/context.py` 1). Six fix patterns: (A) `sys.platform == "win32"` file-lock imports + `BinaryIO \| None` narrowing; (B) `**cast(Any, popen_kwargs)` at 3 subprocess sites; (C) None-guard error-dicts at 7 `intake.py` sites; (D) two `TypedDict` summary shapes in `poller.py` + `cast(dict[str, Any], summary)` at returns; (E) misc narrowing in `runtime.py`/`context.py`; (F) `event_batch: dict[str, Any]` forward declaration at `worker.py:581`. Added `tests/test_full_tree_type_checks.py` (640 tests, +2 from 638) and direct `mypy --strict` CI workflow step. Implementation by headless Sonnet session (82 turns / 9.3 min), committed by Prime Opus after Codex verification | `f59dad4` | `gtkb-phase4b7-residual-mypy-strict-010` VERIFIED |

### In flight

*(None — 4B.7 landed; 4B.8 is next but not yet proposed.)*

### Proposed (post-4B.7)

| # | Sub-round | Scope | Baseline target |
|---|---|---|---|
| **4B.8** | Line coverage | Drive line coverage from 51% → 70% and branch coverage from (baseline TBD) → 55%. Focus on high-value paths first: `bridge/` runtime (currently 0% per 4A baseline), `intake.py`, `reconciliation.py`. Per-file coverage gates from 4B.6 ratchet upward as modules pass new thresholds. | Phase 4A §Coverage |
| **4B.9** | Whole-package docstrings | Drive whole-package docstring coverage from 60.42% → 80%. Public API is already at 100% (from 4B.3). Remaining work is in internal helpers, `bridge/`, and the `intake`/`reconciliation` modules. Docstring-coverage ratchet from 4B.6 increments each PR. | Phase 4A §Docstrings |
| **4C** | Structured logging | Introduce `logging.getLogger(__name__)` in `bridge/` and `db.py` paths; replace silent failures with `logger.warning`/`logger.error`; preserve `click.echo` for CLI user-facing output (unchanged). CI gate: `grep` guard ensures new code doesn't regress to bare `print()` in `src/`. | Phase 4A §Logging |
| **4D** | Broad-exception review | Review the 3 "needs review" `except Exception` sites flagged in Phase 4A; for each, either narrow to specific exception classes, or add an explicit `# intentional-catch: <rationale>` comment. CI gate: new `except Exception` sites without the marker comment fail the commit gate. | Phase 4A §Exceptions |

## Change protocol

1. **Before proposing a new sub-round**, add it to the "Proposed" table in
   this file with a target baseline metric and proposed exit criterion.
2. **Before drafting the bridge proposal**, run `mypy --strict` (or the
   equivalent gate for the sub-round's metric) against a standalone snippet
   that replicates the fix pattern. Paste the result into the bridge proposal
   as an empirical verification appendix.
3. **When a sub-round lands on main**, move it from "In flight" or "Proposed"
   to the "Done" table with its merge commit SHA and bridge entry ID.
4. **When all entries in the "Proposed" table move to "Done"**, Phase 4B is
   complete. Phase 4C (structured logging) has been pre-listed in the
   proposed table; whether it becomes Phase 4B.10 or its own Phase 4C is a
   naming decision that can be made when 4B.9 closes.

## Cross-references

- Phase 4A measurement baseline: `docs/reports/v0.4-baseline/SUMMARY.md`
- Bridge entries: `bridge/gtkb-phase4b*-*.md` in the Agent Red repository
- Change log: `CHANGELOG.md` `[Unreleased]` and `[0.4.0]` sections
- CI workflow: `.github/workflows/ci.yml` (direct `mypy --strict` step added in 4B.6, widened to full tree in 4B.7)

## © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
