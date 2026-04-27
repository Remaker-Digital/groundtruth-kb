NEW

# GENERATOR-HARDENING-CROSS-REPO — Scoping Proposal

**Status:** NEW (scoping; awaits Codex GO)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Parent program:** New work_list row 18 (`GENERATOR-HARDENING-CROSS-REPO`)
**Predecessors:** GH-001 thread (commit `80e16ba8` reduced violations 17→1; post-impl REVISED-1 NO-GO at `-008` requires this bridge to land before GH-001 can close)
**Companion:** GH-002 REVISED-1 §B-only (Type F harness-home reads, separate concern, in REVISED-2 cycle)
**Implementation owner:** Agent Red local (touches `scripts/session_self_initialization.py` + `scripts/rehearse/_dashboard_regen.py` + `scripts/rehearse/_dashboard_regen_runner.py`)

---

## Prior Deliberations

- `DELIB-1106` (Wave 2 implementation umbrella) applies for the rehearsal lane changes.
- Codex `-002` of GH-002 identified the co-design problem: generator-only allowlist won't satisfy runner-side enforcement.
- Codex `-008` of GH-001 made this bridge a prerequisite for GH-001 close.
- No prior deliberation directly addresses cross-repo subprocess in the audit-hook lane.

## 0. Why this exists

The remaining Slice 11 audit-hook violation post-GH-001 is a single
`subprocess.Popen.cwd = E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
event from `_git_checkout_info` inspecting the upstream `groundtruth-kb`
checkout. This is **legitimate cross-repo work by design** — the
upgrade-posture feature reads the upstream's branch/sha/dirty state to
surface upgrade-readiness in the dashboard.

The fix requires changes at **three layers** that all share the same
allowlist contract:

1. **Generator** (`scripts/session_self_initialization.py`): `_git_checkout_info` must skip-and-degrade when the checkout path is outside both `--project-root` AND `--allowed-cross-repo-roots`.
2. **Lane** (`scripts/rehearse/_dashboard_regen.py`): `_build_generator_argv` must pass `--allowed-cross-repo-roots` to the generator; `_build_subprocess_command` must pass the SAME paths to the runner.
3. **Runner** (`scripts/rehearse/_dashboard_regen_runner.py`): `_build_allowed_path_rules` must accept additional cross-repo-root prefixes from a new CLI arg; `build_is_allowed` and `build_audit_hook` flow them through.

Single-layer fixes don't work because each layer enforces independently:
generator filters its OWN call to `_git_checkout_info`; runner filters
ALL subprocess CWDs at the audit-hook level. Both must see the same
allowlist.

## 1. Source-verified architecture

### 1.1 Generator side (already partially identified in GH-002 §A)

`scripts/session_self_initialization.py:1213` — `_git_checkout_info(path)`
runs `git branch/rev-parse/remote/status` subprocesses with `cwd=path`.
Called from `_gtkb_upgrade_posture(project_root)` at line 1274 with
`checkout_path` derived from either:

- `package_path.parents[2]` — upstream editable-install location (e.g., `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`)
- `project_root.parent / "groundtruth-kb"` — sibling-directory fallback

### 1.2 Lane side (new context this bridge surfaces)

`scripts/rehearse/_dashboard_regen.py:333-350` — `_build_generator_argv(sandbox_root)`
currently passes 8 args to the generator:

```python
return [
    "--project-root", str(sandbox_root),
    "--dashboard-dir", str(sandbox_root / "docs" / "gtkb-dashboard"),
    "--history-path", str(sandbox_root / "memory" / "gtkb-dashboard-history.json"),
    "--role-record-path", str(sandbox_root / ".claude" / "rules" / "operating-role.md"),
    "--lifecycle-guard-path", str(sandbox_root / ".claude" / "session" / "lifecycle-guard.json"),
    "--harness-name", "claude",
    "--skip-bridge-maintenance",
    "--fast-hook",
]
```

`scripts/rehearse/_dashboard_regen.py:353-374` — `_build_subprocess_command(legacy_root, sandbox_root, violations_path)`
wraps the generator argv with the runner's argv (`--legacy-script`,
`--legacy-root`, `--sandbox-root`, `--violations-out`).

### 1.3 Runner side

`scripts/rehearse/_dashboard_regen_runner.py:62-130` —
`_build_allowed_path_rules(legacy_root, sandbox_root)` builds the
allowlist:

- Python runtime prefixes (`sys.base_prefix`, `sys.prefix`, site-packages, USER_SITE, sys.path entries NOT under legacy_root)
- `sandbox_root` (recursive prefix rule)
- Per-file legacy code allowlist (8 exact files)

`build_is_allowed(legacy_root, sandbox_root)` (line 171) and
`build_audit_hook(legacy_root, sandbox_root, ...)` (line 220) both
take `legacy_root` and `sandbox_root` only. There is no current path
for additional allowed prefixes.

## 2. Proposed three-layer fix

### 2.1 Generator (Layer 1)

Add new argparse argument:

```python
parser.add_argument(
    "--allowed-cross-repo-roots",
    type=Path,
    nargs="*",
    default=None,
    help=(
        "Optional list of additional repository roots that the upgrade-posture "
        "feature may inspect via git subprocess (e.g., the upstream groundtruth-kb "
        "checkout adjacent to this adopter project). When omitted or empty, "
        "_git_checkout_info skips paths outside --project-root and emits a "
        "degraded record. The same paths must be passed to the audit-hook runner "
        "if the generator is invoked under audit (e.g., Slice 11 rehearsal lane)."
    ),
)
```

Modify `_gtkb_upgrade_posture(project_root)` signature to accept
`allowed_cross_repo_roots: list[Path] | None = None`. Modify
`_git_checkout_info(path)` to accept the same parameter and skip when
`path` is outside both `project_root` AND every entry in
`allowed_cross_repo_roots`:

```python
def _git_checkout_info(
    path: Path,
    project_root: Path,
    allowed_cross_repo_roots: list[Path] | None = None,
) -> dict[str, Any]:
    if not path.is_dir():
        return {"available": False, "path": str(path), "error": "checkout not found"}
    # New: cross-repo scope check
    resolved_path = path.resolve()
    if not _is_relative_to(resolved_path, project_root.resolve()):
        allowed = allowed_cross_repo_roots or []
        if not any(_is_relative_to(resolved_path, r.resolve()) for r in allowed):
            return {
                "available": False,
                "path": str(path),
                "error": "cross_repo_path_not_in_allowlist",
                "scope_diagnostic": "checkout outside --project-root and --allowed-cross-repo-roots",
            }
    # ... existing git subprocess work ...
```

`main()` resolves the allowlist post-parse and threads through to
`_gtkb_upgrade_posture`.

### 2.2 Lane (Layer 2)

Modify `_dashboard_regen.py` to discover the upstream checkout and
pass it consistently to both layers:

```python
def _discover_upstream_checkout_for_allowlist() -> list[Path]:
    """Discover the upstream groundtruth-kb checkout for the cross-repo allowlist.

    Uses the same logic as _gtkb_upgrade_posture's checkout discovery but
    returns the path for allowlist injection rather than for git inspection.
    """
    # Mirror the existing logic at session_self_initialization.py:1267-1273
    # ... return [resolved upstream path] or [] if not discoverable
```

```python
def _build_generator_argv(sandbox_root: Path, cross_repo_roots: list[Path]) -> list[str]:
    argv = [
        # ... existing args ...
    ]
    if cross_repo_roots:
        argv.extend(["--allowed-cross-repo-roots", *(str(r) for r in cross_repo_roots)])
    return argv


def _build_subprocess_command(
    legacy_root: Path,
    sandbox_root: Path,
    violations_path: Path,
    cross_repo_roots: list[Path],
) -> list[str]:
    cmd = [
        sys.executable,
        str(runner),
        "--legacy-script", str(legacy_script),
        "--legacy-root", str(legacy_root),
        "--sandbox-root", str(sandbox_root),
        "--violations-out", str(violations_path),
    ]
    if cross_repo_roots:
        cmd.extend(["--allowed-cross-repo-root", *(str(r) for r in cross_repo_roots)])
    cmd.extend(["--", *_build_generator_argv(sandbox_root, cross_repo_roots)])
    return cmd
```

### 2.3 Runner (Layer 3)

Modify `_dashboard_regen_runner.py:62` `_build_allowed_path_rules(legacy_root, sandbox_root, allowed_cross_repo_roots)`:

```python
def _build_allowed_path_rules(
    legacy_root: Path,
    sandbox_root: Path,
    allowed_cross_repo_roots: list[Path] | None = None,
) -> list[tuple[str, Path]]:
    # ... existing logic ...
    rules.append(("prefix", sandbox_root))
    # NEW: cross-repo allowlist
    for cross_repo_root in (allowed_cross_repo_roots or []):
        rules.append(("prefix", _resolve(cross_repo_root)))
    # Per-file legacy code allowlist (unchanged)
    rules.extend([...])
    return rules
```

`build_is_allowed`, `build_audit_hook` propagate the parameter.
The runner's argparse adds `--allowed-cross-repo-root` (nargs="*").

### 2.4 Shared resolution

The lane discovers the upstream checkout via the same heuristic the
generator uses. The lane passes the resolved paths to BOTH the generator
(via `--allowed-cross-repo-roots`) AND the runner (via
`--allowed-cross-repo-root` in the runner arg list). Both layers see
identical paths.

## 3. Verification

### 3.1 Lane re-run after implementation

```bash
python scripts/rehearse_isolation.py --phase dashboard --execute --output-dir C:/temp/agent-red-rehearsal-cross-repo-verify
```

**Expected `dashboard_regen/result.json`:**

- `status: ok` (was: `error`)
- `audit_hook_violations: 0` (was: 1)
- `subprocess_returncode: 0` (was: 99)

**Expected `dashboard_regen/dashboard-regen-plan.json`:**

- The upgrade-posture record under `gtkb_upgrade` has REAL branch/sha/dirty status from the upstream checkout (not the degraded `cross_repo_path_not_in_allowlist` shape that absent-allowlist would produce).

### 3.2 Two new tests (lane-level)

`tests/scripts/test_rehearse_dashboard_regen.py` (or equivalent):

- `test_lane_passes_cross_repo_roots_to_both_generator_and_runner` — asserts the lane's argv builders include the cross-repo path in BOTH the generator-bound args AND the runner-bound args.
- `test_lane_with_no_upstream_checkout_passes_empty_allowlist` — asserts graceful behavior when no upstream is discoverable (e.g., adopter without sibling-directory upstream).

### 3.3 Two new tests (runner-level)

`tests/scripts/test_dashboard_regen_runner.py`:

- `test_build_is_allowed_accepts_cross_repo_path` — paths inside `allowed_cross_repo_roots` should pass `is_allowed`.
- `test_audit_hook_does_not_fire_on_cross_repo_subprocess_with_allowlist` — full subprocess simulation; subprocess.Popen.cwd inside an allowed cross-repo root does not produce a violation entry.

### 3.4 One new test (generator-level)

`tests/scripts/test_session_self_initialization.py`:

- `test_git_checkout_info_returns_degraded_record_when_path_outside_allowlist` — proves the generator-side scope check.

### 3.5 GH-001 close after this VERIFIED

After this bridge VERIFIED, GH-001 REVISED-1-of-post-impl `-007` becomes
satisfiable: the gate amendment cited "remaining violation must have an
open follow-on bridge specifically addressing it" — this bridge IS that
follow-on. GH-001 can then be re-filed with a REVISED-2 of post-impl
(`-009`) citing this bridge as the accepted follow-on AND showing the
final lane re-run with `violations: 0`.

## 4. Risk + decision notes

- **Three-layer change is invasive.** Five function signatures change (generator: `_gtkb_upgrade_posture`, `_git_checkout_info`; lane: `_build_generator_argv`, `_build_subprocess_command`; runner: `_build_allowed_path_rules`, `build_is_allowed`, `build_audit_hook`). All internal-only; no external API surface.
- **Discovery logic duplicated** between generator's `_gtkb_upgrade_posture` (line 1267-1273) and lane's `_discover_upstream_checkout_for_allowlist`. Could refactor to shared helper, but cross-module dependency adds coupling. Defer refactor unless Codex requests.
- **Adopter follow-up minimal.** Default behavior unchanged (no allowlist = no cross-repo access = degraded record). Adopter SessionStart hook needs `--allowed-cross-repo-roots <upstream-path>` only if the adopter wants live upgrade-posture inspection. Documentation update only.
- **Per Codex `-002` of GH-002 review ask 4:** ".claude/settings.json adopter follow-up clarification". For THIS bridge: `.claude/settings.json` SessionStart hook command line update is a **separate post-verification adopter commit**, NOT in scope of this implementation bridge. The implementation here makes the new flag work; the adopter chooses to use it or not.

## 5. Files Changed

### 5.1 Modified

- `scripts/session_self_initialization.py` (~5-10 LOC: argparse arg + scope check + `_gtkb_upgrade_posture` signature + `main()` post-parse resolution)
- `scripts/rehearse/_dashboard_regen.py` (~20-30 LOC: `_discover_upstream_checkout_for_allowlist` + signature changes + argv builders)
- `scripts/rehearse/_dashboard_regen_runner.py` (~10-15 LOC: `_build_allowed_path_rules` signature + factory propagation + argparse arg)

### 5.2 New tests (5 total)

- 2 lane-level (`test_rehearse_dashboard_regen.py` or equivalent)
- 2 runner-level (`test_dashboard_regen_runner.py`)
- 1 generator-level (`test_session_self_initialization.py`)

### 5.3 No KB/governance/spec changes

## 6. Sequencing

- **Independent of GH-002 REVISED-2** (Type F is unrelated).
- **Independent of all bridge-poller threads.**
- **Hard prerequisite for GH-001 close** per Codex `-008`.
- **Implementation owner: Agent Red local** (all 3 affected files are in Agent Red, not upstream).

## 7. Codex Review Asks

1. Confirm the three-layer co-design (generator + lane + runner) addresses the architectural concern from GH-002 `-002` Finding 1.
2. Confirm the lane is the right discovery point (vs. having the runner discover its own allowlist, or having an env var).
3. Confirm `_discover_upstream_checkout_for_allowlist` should mirror `_gtkb_upgrade_posture`'s discovery heuristic vs. being its own discovery (e.g., explicit env var `GTKB_UPSTREAM_CHECKOUT_PATH`).
4. Confirm 5 new tests is the right depth (or recommend more/fewer).
5. Confirm `.claude/settings.json` adopter update is correctly out of scope here (separate post-VERIFIED adopter commit).
6. **GO / NO-GO.**

## 8. Decisions Needed From Owner

After Codex GO, before implementation:

1. **Discovery heuristic for the lane.** Three options:
   - (a) Mirror generator heuristic (`_gtkb_package_info` → `package_path.parents[2]`, fallback to `project_root.parent / "groundtruth-kb"`). Default per this proposal.
   - (b) Environment variable (`GTKB_UPSTREAM_CHECKOUT_PATH`). Simpler but requires adopter setup.
   - (c) Both, with explicit env var overriding heuristic.
2. **Adopter follow-up timing.** When this bridge VERIFIED, the `.claude/settings.json` SessionStart hook command line could be updated to add `--allowed-cross-repo-roots E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb` (so normal session startup also gets real upgrade-posture). Default per this proposal: yes, in a separate small post-VERIFIED commit.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
