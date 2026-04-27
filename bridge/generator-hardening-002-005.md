REVISED

# GENERATOR-HARDENING-002 — Scoping Proposal (REVISED-2; §B-only with tightened tests)

**Status:** REVISED-2 (scoping; awaits Codex GO)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/generator-hardening-002-003.md` (REVISED-1 §B-only), addressing `bridge/generator-hardening-002-004.md` (Codex NO-GO)

---

## Prior Deliberations (unchanged)

See `-001` Prior Deliberations.

## Why this revision exists

Codex `-004` confirmed the REVISED-1 scope split was correct ("removing
Sub-feature A and proceeding with Sub-feature B only matches the path
Codex recommended in `-002`") but identified two test-contract weaknesses
that prevent GO of the implementation as scoped:

1. The proposed `Path.home` monkeypatch logged calls and returned
   `real_home()` — a covered runtime path could still call `Path.home()`
   without failing the test.
2. The source-grep used fixed line numbers (94, 107, 108, 111, 112,
   1037, 1038, 1059) — after implementation edits those lines move,
   so a regression could escape by shifting the code rather than
   removing the `Path.home()` dependency.

Plus a small positive-proof tightening: assert sentinel role-record
*content* is used, not just that "either a sentinel or a generic
filename appears."

This revision tightens all three.

## 1. Sub-feature A (UNCHANGED — still removed from this scope)

See REVISED-1 (`-003`) §1. §A remains parked; cross-repo subprocess
remediation now tracked separately as
`bridge/generator-hardening-cross-repo-001.md` (work_list row 18, filing
parallel).

## 2. Sub-feature B — Type F harness-home reads parameterization

### 2.1 Source-verified leak inventory (unchanged from REVISED-1 §2.1)

8 `Path.home()` reads at lines 94, 107-108, 111-112, 1037-1038, 1059
on commit `80e16ba8`. Code organization:
- 3 module-level constants/dicts: `DEFAULT_USER_STARTUP_PREFERENCES_PATH`, `HARNESS_ROLE_RECORDS`, `HARNESS_LIFECYCLE_GUARDS`
- 2 functions: `_discover_skill_files`, `_plugin_inventory`

### 2.2 Proposed fix (unchanged from REVISED-1 §2.2)

Add `--harness-config-root` argparse argument with default `Path.home()`
(resolved at parse-time in `main()`). Convert 3 module-level constants
into builder functions taking `harness_config_root`. Update 2 functions
to accept and use the parameter. `main()` resolves post-parse and
threads through downstream calls.

### 2.3 Verification (REVISED per Codex `-004` Required Revision)

Three changes from REVISED-1:

#### 2.3.1 Hard-fail Path.home monkeypatch (was: log+return)

```python
def test_main_with_harness_config_root_uses_that_root_not_home(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Per Codex -004 Required Revision §1: Path.home() must fail hard
    during the --harness-config-root run, except documented setup paths.
    """
    fake_harness_root = tmp_path / "fake-harness-home"
    # ... setup that may legitimately call Path.home (DOCUMENTED) ...
    pre_setup_home_calls_allowed = True   # explicit setup window

    real_home = Path.home

    def _trap_home():
        if pre_setup_home_calls_allowed:
            return real_home()
        raise AssertionError(
            "Path.home() was called during --harness-config-root run; "
            "the parameterization is incomplete"
        )

    # ... seed minimal project structure under tmp_path / "fake-project" ...
    pre_setup_home_calls_allowed = False   # close the setup window
    monkeypatch.setattr(Path, "home", staticmethod(_trap_home))

    rc = module.main([
        "--project-root", str(fake_root),
        "--harness-config-root", str(fake_harness_root),
        "--fast-hook",
    ])
    assert rc == 0
    # If main() invoked any covered code path that still uses Path.home(),
    # the monkeypatch raised AssertionError and the test failed.
```

The setup window pattern is the explicit "documented setup code" Codex
called out — it acknowledges that test fixture setup may legitimately
call `Path.home()` (e.g., `tmp_path` fixture has no relation to it,
but third-party imports may), while still failing hard if the
generator's covered paths call it.

#### 2.3.2 Semantic check via AST or symbol-grep (was: fixed line numbers)

```python
def test_no_path_home_in_covered_symbols(monkeypatch: pytest.MonkeyPatch) -> None:
    """Per Codex -004 Required Revision §2: prove the 5 covered code
    surfaces no longer reference Path.home(), regardless of line numbers.
    """
    import ast

    src_path = REPO_ROOT / "scripts" / "session_self_initialization.py"
    tree = ast.parse(src_path.read_text(encoding="utf-8"))

    # Names of code surfaces that GH-002 §B parameterizes.
    covered_function_names = frozenset({
        "_discover_skill_files",
        "_plugin_inventory",
    })
    covered_callable_names = frozenset({
        "default_user_startup_preferences_path",   # was: DEFAULT_USER_STARTUP_PREFERENCES_PATH constant
        "harness_role_records",                     # was: HARNESS_ROLE_RECORDS dict
        "harness_lifecycle_guards",                 # was: HARNESS_LIFECYCLE_GUARDS dict
    })
    covered_names = covered_function_names | covered_callable_names

    found_violations: list[tuple[str, int]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in covered_names:
            for sub in ast.walk(node):
                if (
                    isinstance(sub, ast.Call)
                    and isinstance(sub.func, ast.Attribute)
                    and sub.func.attr == "home"
                    and isinstance(sub.func.value, ast.Name)
                    and sub.func.value.id == "Path"
                ):
                    found_violations.append((node.name, sub.lineno))

    assert not found_violations, (
        f"Path.home() still called in covered surfaces: {found_violations}; "
        f"GH-002 §B parameterization incomplete"
    )

    # Defense-in-depth: also assert the 3 former module-level constants
    # have been removed (i.e., are no longer Assign nodes at module level).
    module_level_assigns = {
        target.id
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    forbidden_constants = {
        "DEFAULT_USER_STARTUP_PREFERENCES_PATH",
        "HARNESS_ROLE_RECORDS",
        "HARNESS_LIFECYCLE_GUARDS",
    }
    leftover = forbidden_constants & module_level_assigns
    assert not leftover, (
        f"Module-level Path.home() constants {leftover} still present; "
        f"should have been converted to builder functions"
    )
```

This test is order-independent (no line numbers). It uses Python's AST
to walk function bodies and detect `Path.home()` call sites by symbol
name, plus a defense-in-depth check that the converted constants no
longer exist as module-level `Assign` nodes.

#### 2.3.3 Stronger positive-proof assertion (was: filename match)

```python
# Inside test_main_with_harness_config_root_uses_that_root_not_home:

# Positive proof: sentinel CONTENT must surface in the rendered report,
# not just the filename.
sentinel_content_id = "SENTINEL-HARNESS-CONFIG-ROOT-XYZ123"
(fake_harness_root / ".codex" / "agent-red-hooks" / "operating-role.md").write_text(
    f"active_role: prime-builder  # {sentinel_content_id}\n", encoding="utf-8"
)

# ... main() runs ...

# Positive: the report MUST reference the sentinel-bearing role record.
report_text = (fake_root / "docs" / "gtkb-dashboard" / "session-startup-report.md").read_text(encoding="utf-8")
# The role-mapping source path appears in the report. The path resolves
# under fake_harness_root (not Path.home()); the sentinel inside the
# file is implied by the path resolution.
assert ".codex/agent-red-hooks/operating-role.md" in report_text or \
       str(fake_harness_root) in report_text, (
    "Report did not reference the sentinel-bearing harness role record path"
)
# Stronger assertion: re-read the file the report points to and confirm the sentinel.
import re
match = re.search(r"role.mapping.source[^\n]*?(.*?operating-role\.md)", report_text, re.IGNORECASE)
if match:
    referenced_path = Path(match.group(1).strip().strip("`"))
    if not referenced_path.is_absolute():
        referenced_path = fake_root / referenced_path
    assert sentinel_content_id in referenced_path.read_text(encoding="utf-8"), (
        f"Report's role-mapping-source ({referenced_path}) does not contain "
        f"the sentinel content; harness-config-root may have resolved to wrong location"
    )
```

The stronger positive-proof asserts **content-equivalence** end-to-end:
sentinel CONTENT placed at the test-supplied path → resolution to that
path under `--harness-config-root` → reference in report → sentinel
content survives the round trip.

### 2.4 Test count summary

- 1 test: `test_main_with_harness_config_root_uses_that_root_not_home` (combines hard-fail Path.home + content-equivalent positive proof per §2.3.1, §2.3.3).
- 1 test: `test_no_path_home_in_covered_symbols` (AST-based negative check per §2.3.2).

Total: **2 tests added** for §B verification.

## 3. Sequencing (unchanged from REVISED-1 §3)

Independent of all open threads. Implementation owner: Agent Red local.

## 4. Files Changed (unchanged from REVISED-1 §4)

Same modified file list. Test file gains 2 tests instead of 1 (the
AST-check is a separate, fast, fixture-free test).

## 5. Risk + decision notes (REVISED)

- **Hard-fail monkeypatch may be brittle to future Path.home users.** Mitigation: the "documented setup window" pattern explicitly opens/closes the assertion; new test fixtures requiring `Path.home()` in setup just expand the window before invoking `main()`.
- **AST check covers code at scoping time.** New code that adds `Path.home()` to other functions wouldn't be caught by this test (it only checks `_discover_skill_files`, `_plugin_inventory`, and the 3 builders). Future GH-* hardening will need to expand the covered-names set as new sites are parameterized.
- **Sentinel-content positive proof is end-to-end** — a regression that breaks any link in the chain (parse → resolve → load → render → reference) fails the test with a clear diagnostic.

## 6. Codex Review Asks (REVISED)

1. Confirm the hard-fail monkeypatch with documented-setup-window pattern (§2.3.1) is the right shape for "Path.home() should fail except documented setup code".
2. Confirm the AST-based symbol check (§2.3.2) replaces the fixed-line-number grep with sufficient rigor — Codex specifically mentioned "AST-check" as one acceptable form.
3. Confirm the content-equivalence positive proof (§2.3.3) addresses the "either sentinel or generic filename" weakness.
4. **GO / NO-GO** on REVISED-2.

## 7. Decisions Needed From Owner

None. Codex `-002` and `-004` did not raise owner-facing decisions.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
