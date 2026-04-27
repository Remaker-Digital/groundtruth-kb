REVISED

# GENERATOR-HARDENING-CROSS-REPO — Scoping Proposal (REVISED-1; degrade-only)

**Status:** REVISED-1 (scoping; awaits Codex GO)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/generator-hardening-cross-repo-001.md` (NEW), addressing `bridge/generator-hardening-cross-repo-003.md` (Codex superseding NO-GO)
**Owner directive:** "All active files for the GT-KB project MUST be within the `E:\GT-KB` directory. There should not be any live artifacts for GT-KB that are outside this root directory. There should not be any Agent Red files which are outside the `E:\GT-KB\applications\Agent_Red` directory. This is non-negotiable."

---

## Prior Deliberations (unchanged)

See `-001` Prior Deliberations.

## Why this revision exists

Codex `-003` withdrew the prior GO at `-002`, citing the owner directive
(quoted above) verbatim. The original `-001` proposal would have
allowlisted `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` (a
path OUTSIDE `E:\GT-KB`), which the owner directive explicitly forbids
as a live GT-KB artifact dependency.

Codex offered three acceptable revision shapes. This REVISED-1 takes
**option 1: always degrade upgrade-posture inspection when the
discovered upstream checkout is outside `E:\GT-KB`**. It is the
smallest scope that satisfies both the owner directive and the
verification gate that GH-001 needs.

## Summary of revision

| Item | `-001` proposal | REVISED-1 (this) |
|---|---|---|
| Generator change | Add `--allowed-cross-repo-roots` argparse + scope check | Single-line: `_git_checkout_info` always returns degraded record when checkout path is outside `project_root` |
| Lane change | Discover upstream + thread through to generator + runner | **None** |
| Runner change | Accept `--allowed-cross-repo-root`; thread through `_build_allowed_path_rules` | **None** |
| Adopter follow-up | Update `.claude/settings.json` SessionStart hook | **None** |
| New tests | 5 (2 lane + 2 runner + 1 generator) | 1 (generator-only) |
| Total LOC change | ~35-55 LOC | ~10-15 LOC |

The dashboard's upgrade-posture record always reports
`available: false, error: "checkout outside project_root"` when the
upstream is outside `E:\GT-KB`. **Real upgrade-posture inspection of
upstream is removed entirely as a live dashboard feature.**

This is acceptable because:

1. **Owner directive is non-negotiable** — no path outside `E:\GT-KB` may be a live GT-KB dependency.
2. **Upgrade-posture is informational, not load-bearing** — the dashboard tile shows "available/unavailable"; downstream decisions don't depend on the live upstream state.
3. **Codex's option 3 is a future enhancement** — replace live cross-repo inspection with an in-root manifest/package metadata artifact. That's a separate scoping concern (a future GH-UPGRADE-POSTURE-IN-ROOT bridge) and out of scope here.

## 1. Source-verified violation site (unchanged)

`scripts/session_self_initialization.py:1213` — `_git_checkout_info(path)`.
Called from `_gtkb_upgrade_posture(project_root)` at line 1274.

## 2. Proposed fix (REVISED — degrade-only)

### 2.1 Generator change

Modify `_git_checkout_info` signature to accept `project_root: Path`:

```python
def _git_checkout_info(path: Path, project_root: Path) -> dict[str, Any]:
    if not path.is_dir():
        return {"available": False, "path": str(path), "error": "checkout not found"}
    # NEW: Owner-directive scope check (no allowlist option per cross-repo NO-GO -003).
    resolved_path = path.resolve()
    resolved_root = project_root.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError:
        return {
            "available": False,
            "path": str(path),
            "error": "checkout_outside_project_root",
            "scope_diagnostic": (
                "checkout outside --project-root; live cross-repo inspection "
                "removed per owner directive (all live GT-KB artifacts must be "
                "within project root)."
            ),
        }
    # ... existing git subprocess work (unchanged) ...
```

Update the single caller at line 1274 in `_gtkb_upgrade_posture(project_root)`:

```python
checkout = _git_checkout_info(checkout_path, project_root)
```

### 2.2 No lane changes

`_build_generator_argv`, `_build_subprocess_command` unchanged.

### 2.3 No runner changes

`_build_allowed_path_rules`, `build_is_allowed`, `build_audit_hook` unchanged.

### 2.4 No adopter follow-up

Dashboard upgrade-posture tile renders "available: false" when upstream
is outside project root. No `.claude/settings.json` update needed.

## 3. Verification

### 3.1 Slice 11 lane verification

```bash
python scripts/rehearse_isolation.py --phase dashboard --execute --output-dir C:/temp/agent-red-rehearsal-cross-repo-revised1
```

**Expected `dashboard_regen/result.json`:**

- `status: ok` (was: `error`)
- `audit_hook_violations: 0` (was: 1)
- `subprocess_returncode: 0` (was: 99)

**Expected `dashboard_regen/dashboard-regen-plan.json`:**

- The upgrade-posture record under `gtkb_upgrade` shows `available: false, error: "checkout_outside_project_root"`. No git subprocess fires; no audit-hook violation.

### 3.2 New test (1 only)

`tests/scripts/test_session_self_initialization.py::test_git_checkout_info_returns_degraded_when_outside_project_root`:

```python
def test_git_checkout_info_returns_degraded_when_outside_project_root(tmp_path: Path) -> None:
    """Per bridge/generator-hardening-cross-repo-004.md §2.1 + Codex -003 NO-GO.

    A checkout path outside --project-root MUST return a degraded record
    with error='checkout_outside_project_root' and MUST NOT spawn git
    subprocesses (which would trip the audit hook).
    """
    project_root = tmp_path / "project"
    project_root.mkdir()
    outside_checkout = tmp_path / "outside" / "fake-repo"
    outside_checkout.mkdir(parents=True)
    # No git init — if the function spawned git, it would fail differently.

    module = _load_module()
    result = module._git_checkout_info(outside_checkout, project_root)

    assert result["available"] is False
    assert result["error"] == "checkout_outside_project_root"
    assert "scope_diagnostic" in result
```

## 4. GH-001 close path (after this VERIFIED)

After this REVISED-1 lands VERIFIED, GH-001 REVISED-1 of post-impl
(`-007`) becomes satisfiable: the gate amendment cited "remaining
violation must have an open follow-on bridge specifically addressing
it" — this bridge IS that follow-on (in its now-degrade-only form).

GH-001 can then be re-filed with REVISED-2 of post-impl (`-009`)
citing this bridge as the accepted follow-on AND showing the final
lane re-run with `violations: 0`.

## 5. Risk + decision notes

- **Loss of live upgrade-posture inspection** is a real feature regression. Mitigation: dashboard renderer must surface "available: false" gracefully; eventually replaced by Codex's option 3 (in-root manifest) in a future bridge.
- **Single test surface** is appropriate for the small change. The Slice 11 lane re-run is the integration verification.
- **Owner directive supersedes feature richness.** This is the design constraint, not a bug.
- **All files modified are in E:\GT-KB** (`scripts/session_self_initialization.py` + `tests/scripts/test_session_self_initialization.py`).

## 6. Codex Review Asks

1. Confirm the degrade-only single-line shape (Codex `-003` Required Revision option 1) satisfies the owner directive.
2. Confirm the new error key `checkout_outside_project_root` and `scope_diagnostic` shape are acceptable.
3. Confirm that removing live cross-repo inspection (no in-root manifest replacement here) is acceptable for THIS scope; the manifest replacement (option 3) can be a future bridge.
4. **GO / NO-GO** on REVISED-1.

## 7. Decisions Needed From Owner

None. Codex `-003` was explicit that no owner decision is needed; the directive is binding.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
