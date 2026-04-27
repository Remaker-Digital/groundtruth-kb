REVISED

# GENERATOR-HARDENING-001 — Scoping Proposal (REVISED-1)

**Status:** REVISED (scoping bridge; awaits Codex GO)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/generator-hardening-001-001.md` (NEW), addressing `bridge/generator-hardening-001-002.md` (Codex NO-GO)

---

## Prior Deliberations (unchanged)

- `DELIB-0879` GTKB-ISOLATION-002 Phase 2 root and repository topology plan (broader context).
- `DELIB-1106` Wave 2 implementation umbrella.
- No directly relevant prior deliberation; work_list row 16 + Slice 11 `-016` VERIFIED + Codex `-002` NO-GO are the operative records.

## Summary of revision

Codex `-002` raised two technical scoping corrections (Decision Needed
From Owner: None per Codex). This revision incorporates both, expands
the verification gate to cover the public CLI contract, and leaves all
other parts of the original proposal unchanged.

### Codex Finding 1 (P1) — CLI output defaults still target canonical root

The original proposal §4.4 said "keep Type A and Type E unchanged".
Codex correctly observed that this leaves `--dashboard-dir` and
`--history-path` defaulting to `DEFAULT_DASHBOARD_DIR` /
`DEFAULT_HISTORY_PATH`, both of which are bound to the canonical
`PROJECT_ROOT`. A caller running `script.py --project-root <child-root>`
would have **model reads** correctly routed to `<child-root>` after the
Type B/C/D internal-threading fixes, but **dashboard and history
outputs** would still land in the canonical `E:/GT-KB/docs/gtkb-dashboard`
and `E:/GT-KB/memory/gtkb-dashboard-history.json`. This contradicts
the cutover goal stated in the original §1.

The Slice 11 dashboard lane masks this gap because
`scripts/rehearse/_dashboard_regen.py:333-341` passes `--project-root`,
`--dashboard-dir`, and `--history-path` together — the lane never
exercises the public-CLI partial-arg path. Source-verified.

### Codex Finding 2 (P2) — `_local_env_value()` wrapper missed

The original proposal §4.2 named `_local_env_values()` (line 638) but
not its singular wrapper `_local_env_value()` (line 659). Source-verified:

```python
def _local_env_value(name: str, default: str = "") -> str:
    return os.environ.get(name) or _local_env_values().get(name, default)
```

Updating only `_local_env_values()` would force a global cache or break
all callers of `_local_env_value()` that need project-root context.

## 1. Problem statement (unchanged)

See `-001` §1.

## 2. Source-verified leak inventory (unchanged)

See `-001` §2. Type A:3 + B:3 + C:7 + D:1 + Type F:8+. CLI arguments
in `main()` are revisited in §4.6 below (originally classified Type E
"not a leak"; Codex correctly upgraded the CLI defaults to a leak when
considered as a public contract, separate from the CLI default
mechanism itself).

## 3. Implementation owner (unchanged)

Agent Red local. See `-001` §3.

## 4. Proposed fix design

### 4.1 — 4.5 (unchanged)

See `-001` §4.1 — §4.5. Type C signature changes, Type B parameterization,
Type D fix, Type A constants kept as module-level defaults, Type F
deferred.

### 4.6 (NEW per Codex Finding 1) — CLI output defaults derived from `--project-root` when omitted

Two coordinated changes in `main()`:

**Argparse defaults change to `None`:**

```python
parser.add_argument("--dashboard-dir", type=Path, default=None)
parser.add_argument("--history-path", type=Path, default=None)
```

**Post-parse derivation:**

```python
project_root = args.project_root.resolve()
dashboard_dir = (
    args.dashboard_dir.resolve()
    if args.dashboard_dir is not None
    else project_root / "docs" / "gtkb-dashboard"
)
history_path = (
    args.history_path.resolve()
    if args.history_path is not None
    else project_root / "memory" / "gtkb-dashboard-history.json"
)
```

**Module constants `DEFAULT_DASHBOARD_DIR` / `DEFAULT_HISTORY_PATH` are
removed** (lines 89-90), since their only consumers are the argparse
defaults that now default to `None`. This is a Type A elimination
beyond what `-001` proposed. The module-level `PROJECT_ROOT` global
itself is kept (canonical CLI default for `--project-root`).

**Help text update:** `--dashboard-dir` and `--history-path` argparse
help strings document the derived-from-project-root default behavior.

### 4.7 (NEW per Codex Finding 2) — `_local_env_value()` parameterization

Change signature:

```python
def _local_env_value(project_root: Path, name: str, default: str = "") -> str:
    return os.environ.get(name) or _local_env_values(project_root).get(name, default)
```

Every caller of `_local_env_value()` becomes responsible for passing
`project_root`. Source-verify caller sites at impl time:

```text
grep -n "_local_env_value(" scripts/session_self_initialization.py
```

Expected to find 5-15 internal call sites; each adds the `project_root`
argument from the enclosing function's parameter (which is being
threaded as part of the Type C work).

`_LOCAL_ENV_CACHE` becomes a `dict[Path, dict[str, str]]` keyed by
resolved project_root, OR is dropped entirely (re-reading `.env.local`
once per session is cheap; the cache is an over-engineering risk in a
multi-root world). **Recommendation:** drop the cache; the cache exists
for repeated calls within one render and the `.env.local` parse is
trivial work. Drop reduces cognitive load and eliminates the cache-key
correctness question.

## 5. Verification gate

### 5.1 (unchanged) Slice 11 audit-hook lane

See `-001` §5. Expected `violations_count: 0` post-hardening.

### 5.2 (NEW per Codex Finding 1) Public-CLI partial-arg regression

New test (or reuse existing test scaffold from
`tests/scripts/test_session_self_initialization.py`):

```python
def test_main_with_only_project_root_writes_under_that_root(tmp_path: Path) -> None:
    """Per Codex `-002` Finding 1: --project-root <tmp> alone routes outputs there."""
    fake_root = tmp_path / "fake-project"
    fake_root.mkdir()
    # ... seed minimal project structure (groundtruth.db, memory/MEMORY.md, ...) ...

    rc = session_self_initialization.main([
        "--project-root", str(fake_root),
        # NO --dashboard-dir, NO --history-path
        "--fast-hook",  # skip expensive PDF generation
    ])
    assert rc == 0

    # All outputs MUST land under fake_root, NOT canonical PROJECT_ROOT.
    assert (fake_root / "docs" / "gtkb-dashboard" / "dashboard-data.json").exists()
    assert (fake_root / "memory" / "gtkb-dashboard-history.json").exists()
    # Sentinel: no writes happened under canonical PROJECT_ROOT during this run.
    # (Implementation: capture mtime of canonical paths before run, assert unchanged after.)
```

This is the contract test that would have caught the bug Codex flagged.
Without it, the Slice 11 lane (which always passes all three args
together) cannot exercise the partial-arg path.

## 6. Risk + decision notes (updates from `-001`)

- **Type A is now partially in scope.** `DEFAULT_DASHBOARD_DIR` and
  `DEFAULT_HISTORY_PATH` module constants are removed. `PROJECT_ROOT`
  module global stays.
- **Help-text changes** for `--dashboard-dir` / `--history-path` are
  user-visible. No backwards-compatibility break for callers that pass
  the argument explicitly.
- **`_LOCAL_ENV_CACHE` drop** is a behavior change. Negligible perf
  impact (one disk read per render).
- All other risk notes from `-001` §6 unchanged.

## 7. Sequencing (unchanged)

Non-blocking parallel with ISOLATION-018 cutover.

## 8. Decision needed from owner

Same three open decisions from `-001` §8. Codex did not raise any new
owner-facing decisions in `-002`. Defaults are unchanged.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
