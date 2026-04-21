# Post-Implementation Report: GroundTruth-KB Phase 4B.2 Medium Config Defensiveness

**Document:** `gtkb-phase4b2-medium-defensiveness`
**Author:** Prime Builder (Claude Sonnet 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** NEW (awaiting Codex VERIFIED)
**Based on GO:** `bridge/gtkb-phase4b2-medium-defensiveness-002.md`
**Baseline:** `b41ab8f` (groundtruth-kb main before this work)
**Final HEAD:** `249cdd4` (groundtruth-kb main, 3 commits)

## Implementation Summary

All three deferred config-defensiveness findings from `docs/reports/v0.4-baseline/config-errors.md`
have been implemented under the conditions specified in the GO review.

### Finding 4 (MEDIUM): PermissionError wrapped in GTConfigError

**File:** `src/groundtruth_kb/config.py`

Added `PermissionError` catch **before** the `TOMLDecodeError` catch in `_load_toml()`:

```python
except PermissionError as exc:
    raise GTConfigError(
        f"Cannot read config file {config_path}: permission denied. "
        f"Check file ownership and permissions."
    ) from exc
```

- Message includes the config path and a permissions hint (Condition 2 ✓)
- Original `PermissionError` chained via `__cause__` (Condition 2 ✓)
- `FileNotFoundError` still raised directly (not broadened to generic OSError) (Condition 2 ✓)
- `GTConfigError` docstring rewritten to document both wrapped surfaces (Condition 2 ✓)

### Finding 5 (LOW): Warning for missing [groundtruth] section

**File:** `src/groundtruth_kb/config.py` — in `_load_toml()` after `tomllib.load()`

```python
if "groundtruth" not in data:
    warnings.warn(
        f"{config_path}: no [groundtruth] section found. "
        f"Core GroundTruth settings will use env vars and defaults; "
        f"[gates] and [search] sections, if present, are still applied. "
        f"Check your section name if this is unexpected.",
        UserWarning,
        stacklevel=3,
    )
```

- Wording explicitly says `[gates]` and `[search]` sections remain active (Condition 3 ✓)
- `stacklevel=3` from `_load_toml` → `GTConfig.load` → user call site (Condition 4 ✓)
  - Verified by test output: warning correctly points at `cli.py:50` (the `GTConfig.load()` call)
  rather than inside library code

### Finding 6 (LOW): Warning for unknown keys in [groundtruth] section

**File:** `src/groundtruth_kb/config.py` — in `GTConfig.load()` before the final filter

```python
known_fields = set(cls.__dataclass_fields__.keys())
unknown_keys = sorted(k for k in merged if k not in known_fields)
if unknown_keys:
    warnings.warn(
        f"groundtruth config has unknown keys that will be ignored: "
        f"{unknown_keys}. Check for typos in your groundtruth.toml.",
        UserWarning,
        stacklevel=2,
    )
```

- Names the specific unknown key(s) (Condition 5 ✓)
- Keys from `[gates]` and `[search]` sections map to `governance_gates`, `gate_config`,
  `chroma_path` — all are known dataclass fields and never appear in `unknown_keys` (Condition 5 ✓)
- `stacklevel=2` from `GTConfig.load` → user call site (Condition 4 ✓)

## Conditions Check (from GO -002.md)

| # | Condition | Status |
|---|-----------|--------|
| 1 | Tests-first sequence — red state documented | ✓ |
| 2 | PermissionError wrapped in GTConfigError with path + hint + __cause__ | ✓ |
| 3 | Missing-section warning does not imply whole file ignored | ✓ |
| 4 | Warning stacklevel points at external GTConfig.load() call | ✓ |
| 5 | Unknown-key warning names key(s); does not warn for [gates]/[search] values | ✓ |
| 6 | Docs updated: Exceptions section + new Warnings section | ✓ |
| 7 | Verification gate executed (see below) | ✓ |

## Red State (Condition 1)

Commit `0119462` — tests only, implementation not yet landed:

```
15 passed, 4 failed
FAILED tests/test_config.py::test_permission_denied_raises_gtconfigerror
FAILED tests/test_config.py::test_permission_denied_error_chains_original
FAILED tests/test_config.py::test_missing_groundtruth_section_warns
FAILED tests/test_config.py::test_unknown_toml_key_warns
```

All 4 new tests failed as expected, for the correct reasons:
- Tests 1+2: `PermissionError` propagated raw instead of being caught
- Tests 3+4: `DID NOT WARN` — no warnings emitted

## Verification Gate Results (Condition 7)

```text
python -m pytest tests/test_config.py -q --tb=short
-> 19 passed (15 → 19, exactly +4)

python -m pytest -q --tb=short -p no:cacheprovider
-> 636 passed, 1 warning (632 → 636, exactly +4)
   Only remaining warning: pre-existing chromadb DeprecationWarning (asyncio)

python -m ruff check .
-> All checks passed!

python -m ruff format --check .
-> 69 files already formatted

python scripts/check_docs_cli_coverage.py
-> All documentation checks passed.

python -c "from groundtruth_kb import __all__; print(len(__all__))"
-> 16 (unchanged)
```

## Additional Finding: Latent Test Bug Fixed

Running the full suite surfaced a pre-existing bug in `tests/test_reconciliation.py`:
`TestReconcileCLI::test_gt_kb_reconcile_all_runs_every_detector` was writing
`[core]` instead of `[groundtruth]` in its TOML fixture. Our new missing-section
warning pointed at `cli.py:50` (the `GTConfig.load()` call) and made the issue
visible. The section name was corrected to `[groundtruth]` in the implementation
commit. The test still passes and now loads `db_path` correctly from the TOML.

## Commits

```
git log --oneline b41ab8f..HEAD
249cdd4 docs: Phase 4B.2 — update Exceptions section, add Warnings section
eb3c6a8 feat(config): Phase 4B.2 — PermissionError wrap + TOML section warnings
0119462 test(config): Phase 4B.2 tests-first — permission, missing section, unknown keys
```

## Diff Summary

```
git diff --stat b41ab8f..HEAD
 CHANGELOG.md                    | 26 +++++++++
 docs/reference/configuration.md | 43 ++++++++++++--
 src/groundtruth_kb/config.py    | 59 +++++++++++++++----
 tests/test_config.py            | 105 ++++++++++++++++++++++++++++++++++++++-
 tests/test_reconciliation.py    |  2 +-
 5 files changed, 216 insertions(+), 19 deletions(-)
```

Note: 5 files touched (vs 4 predicted) because the reconciliation bug fix
is included. The reconciliation test change is a net-zero test-count effect.

## Public API Surface

- `__all__` = 16 (unchanged — no new public symbols)
- `GTConfigError` identity and import path unchanged
- `import warnings` added to `config.py` (stdlib, no new dependency)

## Awaiting Codex VERIFIED
