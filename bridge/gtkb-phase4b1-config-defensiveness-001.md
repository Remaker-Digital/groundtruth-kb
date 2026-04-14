# Proposal: GroundTruth-KB Phase 4B.1 — Config Error-Path Defensiveness

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** NEW (awaiting Codex GO)
**Parent baseline:** `bridge/gtkb-audit-baseline-008.md` (VERIFIED)
**Baseline evidence:** `docs/reports/v0.4-baseline/config-errors.md` findings 2 and 3
**Prior deliberations search:** No directly relevant prior reviews.
Semantic search for `GTConfig`, `config.py error`, `TOML decode`, and
`config defensiveness` returned only loosely-related G3a and WI-3162
deliberations. Phase 4A's `config-errors.md` is the first focused audit of
`GTConfig.load()`'s error surface.

## Summary

Phase 4A identified two high-priority silent failure modes in
`GTConfig.load()`:

- **Finding 2 (HIGH):** `_load_toml(config_path)` silently returns `{}` when
  the caller passes an explicit `config_path` that does not exist. The CLI
  happens to guard this with `click.Path(exists=True)` on the `--config`
  option, but programmatic callers of `GTConfig.load(config_path=...)` get
  default values with no warning.
- **Finding 3 (MEDIUM):** `_load_toml(config_path)` opens the file and calls
  `tomllib.load(f)` without a try/except. Invalid TOML propagates as a raw
  `tomllib.TOMLDecodeError` with no context pointing at the config file.

Phase 4B.1 fixes both findings with a minimal, surgical change. It is the
first concrete Phase 4B sub-round and follows the tests-first discipline.

## Non-goals (out of scope)

- Finding 4 (permission denied): related but platform-dependent; defer to
  Phase 4B.2 bundled with the other MEDIUM defensiveness items.
- Findings 5, 6, 8, 10, 11, 13: low-priority late-fail or silent-ignore
  modes. Defer until users report confusion.
- Surfacing items from Phase 3 (`sk-ant-api03-*` redaction,
  `src/groundtruth_kb/__main__.py`, `actions/checkout@v5`, exit-code table
  expansion): separate housekeeping track, not bundled here.
- `src/groundtruth_kb/db.py`, CLI commands, CI workflows, and any file
  under `docs/reports/v0.4-baseline/` remain untouched.

## Design

### New exception type

Add a typed exception so library callers have a single type to catch for
any config-load failure that isn't a plain filesystem miss:

```python
class GTConfigError(Exception):
    """Raised when GroundTruth KB cannot load a configuration file.

    Distinct from :class:`FileNotFoundError` (which is raised when a
    user-specified ``config_path`` does not exist) — this exception wraps
    lower-level parser or permission errors with a message that identifies
    the offending file.
    """
```

This matches the existing precedent set by `GovernanceGateError`, which is
already exported from `groundtruth_kb.__all__`. The public API grows from
14 symbols to 15.

### Finding 2 fix

In `_load_toml(config_path: Path | None)`:

```python
def _load_toml(config_path: Path | None) -> dict:
    """Load values from groundtruth.toml.

    Raises:
        FileNotFoundError: When ``config_path`` is explicitly supplied but
            the file does not exist. Auto-discovery (``config_path is None``)
            still returns ``{}`` when no config is found, per the historical
            contract for "exploration mode."
        GTConfigError: When the file exists but contains invalid TOML.
    """
    if config_path is None:
        discovered = _find_config()
        if discovered is None:
            return {}
        config_path = discovered
    elif not config_path.exists():
        raise FileNotFoundError(
            f"GroundTruth config file not found: {config_path}. "
            f"Check the --config path or create the file."
        )
    # ... rest of the function (with Finding 3 fix below)
```

The key behavioral change: when `config_path` is None, auto-discovery falls
back to defaults as before. When `config_path` is explicitly supplied by a
caller, a missing file is now a hard error. This is strictly more
defensive and matches the principle-of-least-surprise for explicit paths.

### Finding 3 fix

Wrap the `tomllib.load()` call:

```python
    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise GTConfigError(
            f"Invalid TOML in {config_path}: {exc}. "
            f"Check your groundtruth.toml syntax."
        ) from exc
```

The original exception is chained via `from exc` so debuggers and traceback
readers can still see the underlying decoder error.

### `__init__.py` export

Add `GTConfigError` to `src/groundtruth_kb/__all__` between `GTConfig` and
`KnowledgeDB`:

```python
__all__ = [
    "GTConfig",
    "GTConfigError",     # NEW
    "KnowledgeDB",
    "GateRegistry",
    "GovernanceGate",
    "GovernanceGateError",
    ...
]
```

Import line in `__init__.py`:

```python
from groundtruth_kb.config import GTConfig, GTConfigError
```

## Test plan (tests-first)

Add **6 new tests** to `tests/test_config.py`, all satisfying the
tests-first rule before any implementation:

| # | Test name | Asserts |
|---|---|---|
| 1 | `test_explicit_config_path_nonexistent_raises` | `GTConfig.load(config_path=tmp_path / "missing.toml")` raises `FileNotFoundError`; the message contains the path |
| 2 | `test_explicit_config_path_nonexistent_message_contains_hint` | The `FileNotFoundError` message contains `"--config"` or `"Check"` as a recovery hint |
| 3 | `test_invalid_toml_raises_gtconfigerror` | A `tmp_path` file with `"invalid toml = ["` triggers `GTConfigError` |
| 4 | `test_invalid_toml_error_chains_original` | The `GTConfigError.__cause__` is a `tomllib.TOMLDecodeError` |
| 5 | `test_invalid_toml_message_contains_path` | The `GTConfigError` message contains the file path |
| 6 | `test_gtconfigerror_is_public_api` | `groundtruth_kb.GTConfigError` is importable and `is GTConfig.__module__.__dict__.get("GTConfigError") or similar`; exists in `groundtruth_kb.__all__` |

Plus **regression coverage** — re-run the existing 9 `test_config.py` tests
to prove the happy paths and the `test_missing_toml_uses_defaults` (auto-
discover, nothing found → defaults) case are unchanged.

### Test file touchpoints

- `tests/test_config.py` (existing file) — add 6 tests after the existing
  test suite. New imports: `pytest`, `groundtruth_kb.GTConfigError`.

## Implementation sequence

Strict tests-first discipline:

1. **Write tests** (new file state): Add 6 tests to `tests/test_config.py`.
2. **Run tests — expect failure**: `python -m pytest tests/test_config.py`
   should show 6 failures (missing `GTConfigError`, missing guards) and
   9 pre-existing passes.
3. **Implement**: Add `GTConfigError` class, fix `_load_toml`, export from
   `__init__.py`.
4. **Run tests — expect 15 pass**: 9 existing + 6 new.
5. **Run full suite — expect 630 pass**: 624 (post-Phase-3) + 6 new.
6. **Run ruff + ruff format + docs CLI coverage**: all green.
7. **Update docs**: `docs/reference/configuration.md` adds an "Exceptions"
   section documenting `GTConfigError` and the `FileNotFoundError`
   behavior. `CHANGELOG.md` adds an Unreleased → Added/Changed entry.
8. **Commit in 3 chunks** (tests, impl, docs). STOP for push approval.

## Committed file touchpoints

Expected diff scope:

| File | Change | Lines |
|---|---|---|
| `tests/test_config.py` | +6 tests, +imports | ~80 added |
| `src/groundtruth_kb/config.py` | +exception class, +guards, +try/except | ~25 added, ~3 changed |
| `src/groundtruth_kb/__init__.py` | +1 import, +1 line in `__all__` | ~2 added |
| `docs/reference/configuration.md` | +Exceptions section | ~40 added |
| `CHANGELOG.md` | +Unreleased entry | ~10 added |

Total: 5 files, approximately 160 lines added, 3 lines changed, 0 existing
tests removed. **No changes to `db.py`, CLI, workflows, `pyproject.toml`, or
any file under `docs/reports/v0.4-baseline/`.**

## Version bump question (owner decision)

This change introduces:

- **A new public API symbol** (`GTConfigError`). Semver: MINOR addition.
- **A behavior change in a previously-documented function.** Programmatic
  callers relying on the silent-defaults behavior for a missing
  `config_path` will now see a `FileNotFoundError`. Semver: technically
  BREAKING for those callers, but no-one should have been relying on this
  bug.

**Proposed version:** `0.5.0` (minor bump to signal the API addition) at
next release. The version bump itself is NOT part of this sub-round's
scope — it lands when the owner is ready to cut a release, and the
CHANGELOG.md entry is staged as `[Unreleased]` until then. Phase 4B.1 is
merge-only; no PyPI release is required to call this sub-round done.

## Verification steps Codex will run after implementation

Per the Phase 3 template:

1. `git log --oneline` — expect 3 new commits on top of `98463bc`.
2. `git show --stat` on each — expect touchpoints above.
3. `python -m pytest tests/test_config.py -q` — expect 15 passed.
4. `python -m pytest -q --tb=short -p no:cacheprovider` — expect 630 passed.
5. `python -m ruff check .` — expect green.
6. `python -m ruff format --check .` — expect green.
7. `python scripts/check_docs_cli_coverage.py` — expect green.
8. `python -c "import groundtruth_kb; print('GTConfigError' in groundtruth_kb.__all__)"`
   — expect `True`.
9. `python -c "from groundtruth_kb import GTConfig; GTConfig.load(config_path=__import__('pathlib').Path('/no/such/file'))"`
   — expect `FileNotFoundError` with the message starting
   `"GroundTruth config file not found:"`.

## Risks and mitigations

1. **Caller relies on silent-defaults.** No known caller in this codebase
   does, and the CLI already uses `click.Path(exists=True)` so the CLI
   surface is unaffected. External downstream callers would get a clean
   `FileNotFoundError` instead of confusing default values — a strictly
   better UX. Mitigation: document in CHANGELOG and configuration.md.
2. **`tomllib.TOMLDecodeError` class path differs on Py < 3.11** (where
   we fall back to `tomli`). The existing `try/except ImportError`
   aliases `tomllib = tomli`, so `tomllib.TOMLDecodeError` resolves to
   `tomli.TOMLDecodeError` on Py 3.10. Both libraries expose the same
   error class under the same attribute name. Mitigation: none needed,
   existing alias handles it. CI matrix covers 3.11–3.13 so the path
   is exercised.
3. **Python 3.10 compat claim is already in pyproject but not in the
   CI matrix.** Not in scope for this sub-round — a separate proposal
   should decide whether to add 3.10 to CI or drop it from pyproject.
4. **Changelog entry is in `[Unreleased]`, not `[0.5.0]`.** The Phase
   4A baseline recommends batching multiple 4B sub-rounds into a single
   release. Phase 4B.1 stages its changelog line under `[Unreleased]`
   so 4B.2, 4B.3 etc can pile up before the next PyPI publish.
5. **Scope creep temptation.** The audit also flagged findings 4, 5, 6
   in the same file. Explicitly deferred to 4B.2 to keep the review
   size small and the test count auditable.

## Standing checkpoint

Per the bridge protocol:

- NO code written yet — this is the initial proposal.
- Tests will be written FIRST, failing, then implementation lands.
- After implementation, all 4 local gates (ruff, format, pytest, docs
  coverage) will be green before committing.
- Commits will be local-only until owner push approval.
- Post-implementation report will request Codex VERIFIED.

Awaiting Codex review.

## Appendix A: Why not fold surfacing items into this proposal?

Phase 3 surfaced four small housekeeping items:

- Anthropic `sk-ant-api03-*` pattern missing from `_REDACTION_PATTERNS`
- `src/groundtruth_kb/__main__.py` missing (breaks `python -m groundtruth_kb`)
- Exit-code tables missing for 4 CLI commands in `docs/reference/cli.md`
- `actions/checkout@v4` → `@v5` upgrade (GitHub deprecation)

These are legitimate but touch three different surfaces (db.py pattern
list, new file, docs-only, .github/workflows/*). Bundling them with
config defensiveness would balloon the review scope and diffuse the
Phase 4B.1 goal. They should land in a separate "Phase 4B housekeeping"
proposal that Prime can submit in parallel once 4B.1 is VERIFIED.

## Appendix B: Proposed Phase 4B roadmap (reminder, not part of scope)

This proposal implements only 4B.1. The full Phase 4B sub-round plan
from `docs/reports/v0.4-baseline/SUMMARY.md`:

| Sub-round | Focus | Status |
|---|---|---|
| **4B.1** | Config defensiveness (Findings 2+3) | **THIS PROPOSAL** |
| 4B.2 | Medium defensiveness (Findings 4, 5, 6) | not yet proposed |
| 4B.3 | 27 public-API docstring gaps in `KnowledgeDB`/`GateRegistry` | not yet proposed |
| 4B.4 | Public-API type annotations — close `mypy --strict` on exported symbols | not yet proposed |
| 4B.5 | `bridge/` runtime sub-rounds (biggest quality gap) | not yet proposed |
| 4B.6 | CI enforcement gates (`--cov-fail-under`, `interrogate --fail-under`, `mypy --strict`) | not yet proposed |
| 4B-housekeeping | Phase 3 surfacing items (4 small fixes) | not yet proposed |

The owner may interleave sub-rounds or reorder as needed. Each is its own
bridge thread.

End of proposal. Awaiting Codex GO / NO-GO.
