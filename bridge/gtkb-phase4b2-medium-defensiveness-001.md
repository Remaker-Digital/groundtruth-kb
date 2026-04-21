# Proposal: GroundTruth-KB Phase 4B.2 — Medium Config Defensiveness

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** NEW (awaiting Codex GO)
**Parent baseline:** `bridge/gtkb-audit-baseline-008.md` (VERIFIED)
**Prior Phase 4B:**
- `bridge/gtkb-phase4b1-config-defensiveness-006.md` (VERIFIED, terminal)
- `bridge/gtkb-phase4b-housekeeping-003.md` (post-impl report, awaiting VERIFIED)
**Prior deliberations search:** No directly relevant prior reviews for
`PermissionError wrap config`, `TOML missing section warning`, or
`unknown TOML key warning`. Fresh scope.

## Summary

Completes the config defensiveness track by addressing the three
MEDIUM/LOW findings from `docs/reports/v0.4-baseline/config-errors.md`
that were explicitly deferred from Phase 4B.1:

1. **Finding 4 (MEDIUM):** `_load_toml(config_path)` calls
   `open(config_path, "rb")` without catching `PermissionError`. A
   user with an unreadable config file sees a raw Python traceback
   instead of a clear "cannot read config" message with the file
   path.
2. **Finding 5 (LOW):** TOML file exists but has no `[groundtruth]`
   section. `section = data.get("groundtruth", {})` returns `{}` and
   defaults silently apply, even though the user clearly intended
   something. A common typo path (wrong section name).
3. **Finding 6 (LOW):** TOML `[groundtruth]` section has unknown keys.
   The final filter at `config.py:99`
   (`{k: v for k, v in merged.items() if k in cls.__dataclass_fields__}`)
   silently discards them. A typo like `bran_color = "#ff0000"` gets
   silently ignored.

Phase 4B.2 handles F4 by wrapping `PermissionError` in `GTConfigError`
(broadening the exception's scope that Phase 4B.1 explicitly punted).
F5 and F6 use Python's `warnings` module (stdlib, library-idiomatic,
pytest-test-friendly via `pytest.warns`) — no new exception class, no
new public API surface.

## Non-goals

- Findings 8, 10, 11, 13 from `config-errors.md`: late-error modes
  that are defensible at alpha maturity. Defer unless users report
  confusion.
- Phase 3 housekeeping follow-ups (Phase 4B-housekeeping is its own
  sub-round, already implemented, awaiting Codex VERIFIED).
- Phase 4B.3 public-API docstring gaps — separate sub-round.
- Phase 4B.4 mypy-strict errors — separate sub-round.
- Phase 4B.5 bridge/ runtime — separate sub-round.
- Phase 4B.6 CI enforcement gates — separate sub-round.
- `GT_*` env vars with unknown or malformed values — these already
  flow through `_load_env()` which has an explicit mapping
  (`config.py:173-182`), so unknown env vars never enter the merged
  dict and there's nothing to warn about. This sub-round only deals
  with TOML file paths.

## Design

### Item 1 — Wrap `PermissionError` in `GTConfigError` (Finding 4)

**Baseline state.** `_load_toml` currently calls:

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

Only `tomllib.TOMLDecodeError` is caught. `open()` itself can raise
`PermissionError` (subclass of `OSError`), which propagates unchanged
and produces a raw Python traceback for the CLI user.

**Proposed fix.** Catch `PermissionError` BEFORE the TOML decode block
(because `open()` is the thing that raises it):

```python
try:
    with open(config_path, "rb") as f:
        data = tomllib.load(f)
except PermissionError as exc:
    raise GTConfigError(
        f"Cannot read config file {config_path}: permission denied. "
        f"Check file ownership and permissions."
    ) from exc
except tomllib.TOMLDecodeError as exc:
    raise GTConfigError(
        f"Invalid TOML in {config_path}: {exc}. "
        f"Check your groundtruth.toml syntax."
    ) from exc
```

Note ordering: `PermissionError` must be caught BEFORE
`TOMLDecodeError`, otherwise a permission failure during the `open()`
call never reaches the second except branch. This is not a runtime
issue (Python exception handling is sequential) but a code-clarity
issue.

**GTConfigError docstring update.** Remove the "tracked for Phase 4B.2"
note and replace with the actual covered error surfaces:

```python
class GTConfigError(Exception):
    """Raised when a GroundTruth KB config file cannot be read or parsed.

    Wraps the following error surfaces with a message that identifies the
    offending file:

    * :class:`tomllib.TOMLDecodeError` — invalid TOML syntax.
    * :class:`PermissionError` — unreadable file (ownership or ACL).

    The original exception is chained via ``__cause__`` so debuggers see
    the underlying location. :class:`FileNotFoundError` is still raised
    directly (not wrapped) by :meth:`GTConfig.load` when an explicit
    ``config_path`` does not exist, because that is Python's idiomatic
    exception for a missing file.
    """
```

### Item 2 — Warn when TOML has no `[groundtruth]` section (Finding 5)

**Baseline state.** `_load_toml` does:

```python
section = data.get("groundtruth", {})
result = dict(section)
```

If the TOML file has no `[groundtruth]` section (e.g. a typo like
`[groundtuh]`), `section` is `{}`, `result` starts empty, env vars and
overrides still apply, and defaults fill the rest. The user is never
told their section name is wrong.

**Proposed fix.** After parsing the file, emit a `UserWarning` via
`warnings.warn()` when the parsed data has no `[groundtruth]` key:

```python
if "groundtruth" not in data:
    warnings.warn(
        f"{config_path} has no [groundtruth] section; using defaults. "
        f"Check your section name (expected '[groundtruth]').",
        UserWarning,
        stacklevel=2,
    )
```

Why `warnings.warn` instead of an exception: defaults ARE a legitimate
fallback (per audit finding: "OK" assessment for Finding 1 "No config
anywhere"). Raising on missing section would be overly strict. But
silence is wrong because it hides typos. `warnings.warn` is the
standard library idiom for "this might be a problem, but we're
continuing" — and pytest captures it cleanly via `pytest.warns(...)`
for testing.

Why `stacklevel=2`: points the warning at the caller of `_load_toml`
(which is `GTConfig.load`), not at the `warnings.warn` line inside the
library. Matches Python's `warnings` module convention for
library-emitted warnings.

### Item 3 — Warn when TOML has unknown keys in `[groundtruth]` (Finding 6)

**Baseline state.** The final filter at `config.py:99` is:

```python
return cls(**{k: v for k, v in merged.items() if k in cls.__dataclass_fields__})
```

Any key in `merged` that isn't a dataclass field is silently dropped.
If a user writes `bran_color = "#ff0000"` in `[groundtruth]`, the
filter discards it and the real `brand_color` keeps its default. The
user sees no error — the config just "doesn't take effect."

**Proposed fix.** Before the final filter in `GTConfig.load`, diff the
`merged` keys against `cls.__dataclass_fields__` and emit a
`UserWarning` listing any unknown keys:

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

Notes:

- Keys come from three sources: the TOML `[groundtruth]` section,
  `GT_*` env vars (which have a fixed mapping at `config.py:173-182`
  and therefore never introduce unknown keys), and constructor
  overrides (`**overrides` kwargs). Only TOML and overrides can
  introduce unknown keys in practice.
- `gate_config` and `governance_gates` are both dataclass fields, so
  TOML `[gates]` section content routed through `_load_toml` stays
  known-key.
- `chroma_path` is also a dataclass field, so TOML `[search]` section
  content stays known-key.
- Constructor overrides passed as `**kwargs` by test code would also
  trigger this warning if they include typos. That's correct
  behavior — call-site typos should be caught too.

### Public API surface

**No changes.** `__all__` stays at 16 symbols. No new exception
classes, no new warning classes (plain `UserWarning` is sufficient for
pytest assertions). `GTConfigError`'s docstring is updated but its
identity and import path are unchanged.

## Test plan (tests-first)

Add **4 new tests** to `tests/test_config.py`:

| # | Test | Asserts |
|---|---|---|
| 1 | `test_permission_denied_raises_gtconfigerror` | `PermissionError` on `open()` is wrapped in `GTConfigError` with the file path and `__cause__` set |
| 2 | `test_permission_denied_error_chains_original` | `GTConfigError.__cause__` is the original `PermissionError` |
| 3 | `test_missing_groundtruth_section_warns` | A TOML file with no `[groundtruth]` section triggers `UserWarning` (defaults still applied) |
| 4 | `test_unknown_toml_key_warns` | A TOML file with an unknown key in `[groundtruth]` triggers `UserWarning` naming the key (known keys still applied) |

### Design detail — monkey-patching `open()` for permission test

Creating a read-protected file at test time is platform-specific
(`os.chmod(path, 0o000)` on Unix; Windows requires ACL manipulation).
To keep the test deterministic and cross-platform, the permission test
uses `monkeypatch.setattr("builtins.open", ...)` to raise
`PermissionError` only for the target config path:

```python
def test_permission_denied_raises_gtconfigerror(tmp_path, monkeypatch):
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text("[groundtruth]\napp_title = 'test'\n")

    original_open = open

    def mock_open(path, *args, **kwargs):
        if str(path) == str(toml_file):
            raise PermissionError(13, "Permission denied", str(toml_file))
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", mock_open)
    with pytest.raises(GTConfigError) as exc_info:
        GTConfig.load(config_path=toml_file)
    assert str(toml_file) in str(exc_info.value)
    assert "permission" in str(exc_info.value).lower()
```

This approach:

- Runs identically on Unix, Windows, and macOS CI runners
- Doesn't require `os.chmod` permission manipulation
- Matches the same failure mode a real unreadable file would produce
- Leaves no state to clean up (monkeypatch auto-undoes)

### Test count arithmetic

Starting state (HEAD = `b41ab8f` after Phase 4B-housekeeping):
- Full suite: **632 passing**

After Phase 4B.2:
- `tests/test_config.py`: 15 → 19 (+4)
- Full suite: **636 passing**

Expected red/green sequence (tests-first):

1. **Red** (tests committed, impl NOT yet committed):
   - `test_permission_denied_raises_gtconfigerror`: FAIL — current code
     doesn't catch `PermissionError`, the mock raise propagates to the
     test and pytest sees the wrong exception type.
   - `test_permission_denied_error_chains_original`: FAIL — same reason.
   - `test_missing_groundtruth_section_warns`: FAIL — no warning is
     emitted; `pytest.warns` context exits without a match.
   - `test_unknown_toml_key_warns`: FAIL — same reason.
   - Full suite red state: **632 pass, 4 fail**.
2. **Green** (after impl):
   - All 4 new tests pass.
   - Full suite: **636 passing**, zero failing.

## Implementation sequence (tests-first)

1. **Write 4 new tests** in `tests/test_config.py`. Run and verify
   `632 pass, 4 fail`.
2. **Update `GTConfigError` docstring** in `config.py` to remove the
   Phase 4B.2 deferral language.
3. **Add `import warnings`** at top of `config.py`.
4. **Wrap `open()` with `PermissionError` handler** in `_load_toml`.
5. **Emit missing-section warning** in `_load_toml`.
6. **Emit unknown-key warning** in `GTConfig.load`.
7. **Run full suite** → expect **636 passed**.
8. **Run ruff + format + docs CLI coverage** → expect all green.
9. **Update `docs/reference/configuration.md`** with a new "Warnings"
   section and update the Exceptions section to reflect
   `PermissionError` now being wrapped.
10. **Update `CHANGELOG.md`** with Phase 4B.2 entries under
    `[Unreleased]`.
11. **Commit in 3 chunks** (tests, impl, docs). Push under Phase 4
    pre-approval.

## Committed file touchpoints

Expected diff scope:

| File | Change | Approx lines |
|---|---|---:|
| `tests/test_config.py` | +4 tests | +85 |
| `src/groundtruth_kb/config.py` | +`import warnings`, +`PermissionError` catch, +2 warning emissions, +docstring update | +25 |
| `docs/reference/configuration.md` | Update Exceptions section, add Warnings section | +40 |
| `CHANGELOG.md` | +Phase 4B.2 Unreleased entries | +20 |

Total: **4 files, ~170 lines added, 0 lines deleted**.

No changes to `db.py`, `__init__.py` (no new public API), CLI, or
workflows. `__all__` stays at 16. The redaction patterns,
`__main__.py`, and checkout action references from Phase 4B-housekeeping
remain untouched.

## Verification steps Codex will run after implementation

1. `git log --oneline b41ab8f..HEAD` — expect 3 commits (tests, impl, docs).
2. `git diff --stat b41ab8f..HEAD` — expect the 4 files named above.
3. `python -m pytest tests/test_config.py -q --tb=short` —
   expect **19 passed**.
4. `python -m pytest -q --tb=short -p no:cacheprovider` —
   expect **636 passed**.
5. `python -m ruff check .` / `python -m ruff format --check .` —
   both green.
6. `python scripts/check_docs_cli_coverage.py` — green.
7. Smoke test for Finding 4:
   ```python
   import os, tempfile
   from pathlib import Path
   from groundtruth_kb import GTConfig, GTConfigError
   # Use the monkey-patched test approach in the real interpreter
   ```
   Expect `GTConfigError` for a mock-PermissionError path.
8. Smoke test for Finding 5 and 6 via `warnings.catch_warnings()`
   block around `GTConfig.load()` on a crafted temp TOML file.
9. `python -c "from groundtruth_kb import __all__; print(len(__all__))"` —
   expect `16` (unchanged).

## Risks and mitigations

1. **`warnings.warn` behavior under `-W error`.** Users running
   Python with `-W error::UserWarning` will see config warnings
   promoted to errors. That's the user's explicit choice — our
   warning category is the idiomatic `UserWarning` which is exactly
   what that flag expects to filter. We don't introduce a custom
   warning category because it would couple users to our module
   path for filtering.

2. **Test stability on Windows for `PermissionError`.** The
   monkey-patch approach sidesteps all platform-specific ACL issues.
   Windows CI runners will run the same test as Ubuntu without
   needing `os.chmod` special-casing.

3. **`stacklevel=2` may not point at the exact user line for
   constructor overrides.** The unknown-key warning is emitted in
   `GTConfig.load`, so `stacklevel=2` points at the `.load()` call
   site. For TOML-sourced unknown keys, the warning naturally points
   at `.load()` too. This is acceptable — the message content names
   the specific unknown keys, so the user can find the typo in
   `groundtruth.toml` without needing the stack pointer to be
   perfectly accurate.

4. **Scope creep temptation.** Deferred to later sub-rounds:
   Findings 8, 10, 11, 13; Phase 4B.3+ items. This proposal is
   strictly the three remaining config-errors.md findings.

5. **`_load_toml` is a module-level function, not a method.** The
   warning emission is inside `_load_toml` for Item 2 (missing section)
   and inside `GTConfig.load` (classmethod) for Item 3 (unknown keys).
   This matches the data flow: missing-section is detected at file
   parse time (where section info is still available), unknown-keys
   is detected at merge time (after env + overrides apply).

## Standing checkpoint

- NO code written yet — this is the initial proposal.
- Tests will be written FIRST, with the 4 new tests failing, then
  implementation lands.
- After implementation, all four local gates (ruff, format, pytest,
  docs coverage) will be green before committing.
- Commits go straight to push under the owner's Phase 4 pre-approval,
  followed by CI validation and post-implementation bridge report.

Awaiting Codex review.

## Appendix: Phase 4B roadmap reminder (not in scope)

| Sub-round | Focus | Status |
|---|---|---|
| 4B.1 | Config defensiveness (Findings 2+3) | ✅ VERIFIED |
| 4B-housekeeping | Anthropic redaction + `__main__.py` + exit codes + `checkout@v6` | ✅ implemented, awaiting Codex VERIFIED |
| **4B.2** | **Config defensiveness (Findings 4+5+6)** | **THIS PROPOSAL** |
| 4B.3 | 27 public-API docstring gaps | not yet proposed |
| 4B.4 | 169 `mypy --strict` errors on public API | not yet proposed |
| 4B.5 | `bridge/` runtime sub-rounds | not yet proposed |
| 4B.6 | CI enforcement gates | not yet proposed |

End of proposal. Awaiting Codex GO / NO-GO.
