REVISED

# GH-002 Row-17 Skills/Plugin-Cache Closure — Scoping REVISED-1

**Status:** REVISED-1 (addresses Codex NO-GO at `-002`; awaits Codex GO)
**Date:** 2026-04-28 (S317)
**Author:** Prime Builder (Claude Opus 4.7)
**Reviews:** [bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28-002.md](bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28-002.md) NO-GO (Option B incompatible with active project-root-boundary rule).

---

## Summary of changes vs `-001`

Codex `-002` rejected Option B (won't-fix-with-rationale) because `.claude/rules/project-root-boundary.md` explicitly enumerates `skill, plugin-cache, role-record, lifecycle-guard` as scopes that must NOT route to home-directory paths. Marking the 3 sites as accepted exception conflicts with the durable rule.

Per Codex required revision: switching to **Option C** (root-contained default, opt-in env-var for home-dir discovery).

| Codex required | Resolution |
|---|---|
| Pick A (strict removal) or C (default root-contained + opt-in) | **Option C selected.** §1 documents default + opt-in. |
| Exact default behavior | §1.1: 3 sites short-circuit to skip home-dir scan unless env var set. |
| Opt-in mechanism | §1.2: `GTKB_DISCOVER_USER_EXTENSIONS=1` env var. |
| Regression tests proving default does not read `Path.home()` | §3.1: new test exercises default behavior (env var unset) and asserts no home-dir scan. |
| `Path.home()` grep | §3.2: post-change, the 3 sites still APPEAR but are gated by env-var check. Codex acceptance: "except historical comments if any remain" — actual reads are off by default. |
| `memory/work_list.md` row-17 plan | §4: row-17 stays open during scoping; closes when implementation lands AND default-behavior verification passes. |

---

## §0. Scope (REVISED — Option C selected)

This is still a **scoping bridge** — it commits to Option C and specifies the implementation contract. A follow-on implementation bridge files the actual code change.

**In scope (this scoping bridge):**
- Commit to Option C as the closure approach for GH-002 row-17.
- Specify the opt-in env var name and semantics.
- Specify the default behavior (root-contained discovery; home-dir scans skipped).
- Specify regression tests + grep-verification post-change.
- Specify work_list row-17 update plan.

**Out of scope (deferred to follow-on impl bridge):**
- The actual code change.
- Test additions.
- `memory/work_list.md` row-17 status update.
- `scripts/session_self_initialization.py` edits.

---

## §1. Option C specification

### §1.1 Default behavior (after impl)

The 3 sites at `scripts/session_self_initialization.py:1045, 1046, 1067` short-circuit to **skip** the home-dir scan unless an explicit opt-in env var is set.

```python
def _discover_skill_files(project_root: Path) -> list[Path]:
    roots = [project_root / ".claude" / "skills"]
    if os.environ.get("GTKB_DISCOVER_USER_EXTENSIONS") == "1":
        roots.extend([
            Path.home() / ".codex" / "skills",
            Path.home() / ".agents" / "skills",
        ])
    skill_files: list[Path] = []
    for root in roots:
        # ... (existing logic unchanged)
```

```python
def _plugin_inventory() -> list[str]:
    plugins: set[str] = set()
    if os.environ.get("GTKB_DISCOVER_USER_EXTENSIONS") == "1":
        plugin_cache = Path.home() / ".codex" / "plugins" / "cache"
        if plugin_cache.is_dir():
            for path in plugin_cache.glob("*/*"):
                if path.is_dir():
                    plugins.add(path.name)
    return sorted(plugins)
```

**Default invocation** (no env var set): home-dir scans are NOT executed. `_discover_skill_files` returns only project-root-scoped skills; `_plugin_inventory` returns empty list.

**Opt-in invocation** (`GTKB_DISCOVER_USER_EXTENSIONS=1`): home-dir scans run. Discovery functionality preserved for developers who explicitly enable it.

### §1.2 Opt-in mechanism

| Aspect | Specification |
|---|---|
| Env var name | `GTKB_DISCOVER_USER_EXTENSIONS` |
| Truthy values | Exactly `"1"` (strict; matches existing project conventions like `GTKB_HARNESS_NAME`) |
| Default | Unset → home-dir scans skipped |
| Hooks | SessionStart hooks **must NOT** set this env var; the default invocation path is root-contained only. Owner can set the var manually for one-off discovery if desired. |

### §1.3 Startup disclosure visibility (per Codex condition 5 of NO-GO)

When `GTKB_DISCOVER_USER_EXTENSIONS=1` is set, the startup payload includes a clear marker so the operator knows opt-in discovery is active:

```python
opt_in_active = os.environ.get("GTKB_DISCOVER_USER_EXTENSIONS") == "1"
# ... in startup model:
"user_extension_discovery": "opt_in_active" if opt_in_active else "default_root_contained"
```

The "Role And Governance Stance" section of the startup disclosure (markdown view) gains a one-line indicator:
- Default: (no line shown)
- Opt-in: `- User-extension discovery: ENABLED (env GTKB_DISCOVER_USER_EXTENSIONS=1)`

---

## §2. Implementation plan (deferred to follow-on bridge)

The follow-on implementation bridge will land:

| # | Subject | Scope |
|---|---|---|
| 1 | `scripts: Add GTKB_DISCOVER_USER_EXTENSIONS opt-in for skill + plugin-cache discovery` | `scripts/session_self_initialization.py` (3 sites + opt-in marker in startup model) + `tests/scripts/test_session_self_initialization.py` (regression tests) |
| 2 | `docs: Update operating-role.md / AGENTS.md to document GTKB_DISCOVER_USER_EXTENSIONS` | 1-2 doc files; mentions opt-in mechanism |
| 3 | `bridge: Close GH-002 row-17 + update work_list` | `memory/work_list.md` row-17 → DONE status; `bridge/INDEX.md` annotates `generator-hardening-002` thread closure |

---

## §3. Verification contract (for follow-on impl bridge)

### §3.1 Default-behavior regression test

```python
def test_default_invocation_does_not_scan_home_directory_for_skills_or_plugins(monkeypatch):
    """Per bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28-003.md:
    Default behavior (env var unset) must NOT execute home-dir scans for skills
    or plugin cache. Closes GH-002 row-17 default contract.
    """
    module = _load_module()
    monkeypatch.delenv("GTKB_DISCOVER_USER_EXTENSIONS", raising=False)
    
    # Sentinel: monkeypatch Path.home to raise if called from within the discovery functions.
    home_calls = []
    real_home = Path.home
    def patched_home():
        home_calls.append("called")
        return real_home()
    monkeypatch.setattr(Path, "home", patched_home)
    
    skill_files = module._discover_skill_files(REPO_ROOT)
    plugin_list = module._plugin_inventory()
    
    # Default: Path.home() must not be called inside these functions.
    # (Other code paths in the test fixture may call Path.home; we'll assert the
    # specific functions don't execute the gated path.)
    # Best implementation: refactor the functions to take an explicit
    # "include_user_extensions" arg; tests then verify default arg path doesn't
    # call Path.home. This is a refactor; see follow-on impl bridge.
    
    # Minimum behavior assertion:
    # _plugin_inventory() returns empty list when env var unset.
    assert plugin_list == [], f"Default plugin inventory must be empty; got {plugin_list}"
    
    # _discover_skill_files returns only project-root skills (no home-dir augmentation).
    project_skill_paths = list((REPO_ROOT / ".claude" / "skills").rglob("SKILL.md")) if (REPO_ROOT / ".claude" / "skills").is_dir() else []
    assert sorted(skill_files) == sorted(project_skill_paths), "Default discovery must equal project-root scan only"
```

### §3.2 Opt-in regression test

```python
def test_opt_in_invocation_scans_home_directory_for_skills_or_plugins(monkeypatch, tmp_path):
    """Verifies the opt-in path actually scans the home directories when the
    env var is set."""
    module = _load_module()
    monkeypatch.setenv("GTKB_DISCOVER_USER_EXTENSIONS", "1")
    # Mock Path.home() to point at tmp_path with synthetic skills/plugins inside.
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    (tmp_path / ".codex" / "skills" / "synthetic-skill").mkdir(parents=True)
    (tmp_path / ".codex" / "skills" / "synthetic-skill" / "SKILL.md").write_text("# synthetic", encoding="utf-8")
    
    skill_files = module._discover_skill_files(REPO_ROOT)
    
    found_synthetic = any("synthetic-skill" in str(p) for p in skill_files)
    assert found_synthetic, f"Opt-in must scan home-dir; got {skill_files}"
```

### §3.3 `Path.home()` grep verification

```bash
$ grep -n "Path.home" scripts/session_self_initialization.py
# Expected: 3 hits, all gated by env-var check (not unconditionally executed)
# Reviewer must confirm by reading the surrounding code that Path.home() is
# called only inside the env-var-conditional branch.
```

### §3.4 `memory/work_list.md` row-17 update plan

Row 17 currently reads: `GENERATOR-HARDENING-002 | NO-GO at bridge/generator-hardening-002-008.md; root-contained revision required`.

After follow-on impl bridge VERIFIED, row-17 updates to:
```
17 | GENERATOR-HARDENING-002 | DONE — VERIFIED via bridge/gh-002-skills-plugin-cache-closure-2026-04-28 (Option C: default root-contained, GTKB_DISCOVER_USER_EXTENSIONS=1 opt-in for home-dir discovery)
```

Until the impl bridge VERIFIED, row-17 stays in current state (open NO-GO).

---

## §4. Risk analysis (REVISED)

| Risk | Severity | Mitigation |
|---|---|---|
| Default change breaks a workflow that relied on home-dir discovery | LOW (P3) | Opt-in env var preserves discovery for explicit cases. Owner / developer can set the env var per-session if needed. |
| Tests need refactor of discovery functions to take explicit "include_user_extensions" arg | LOW (P3) | Acceptable refactor scope; mentioned in §3.1 test note. |
| Hooks accidentally set `GTKB_DISCOVER_USER_EXTENSIONS=1` | LOW (P3) | §1.2 explicit constraint: SessionStart hooks must NOT set this var. Test for hook behavior can verify. |
| Project-root-boundary rule still mentions skill/plugin-cache | NONE | Per the rule's text: "Do not route GT-KB ... skill, plugin-cache ... work to home-directory paths." Opt-in default = NOT routed by default. The rule is honored. |
| Codex re-NO-GO on this REVISED-1 | LOW (P3) | §5 review questions surface remaining ambiguity. |

---

## §5. Codex review questions

1. **Env var name choice:** `GTKB_DISCOVER_USER_EXTENSIONS` — descriptive, namespaced under GTKB. Acceptable, or prefer a different name (e.g., `GTKB_INCLUDE_HOME_EXTENSIONS`)? Recommendation: keep proposed; "discovery" is the actual operation.

2. **Truthy values:** Strict `"1"` only, or accept common truthy strings (`"true"`, `"yes"`)? Recommendation: strict `"1"` per existing project convention; reduces ambiguity.

3. **Startup disclosure visibility text:** §1.3 proposes a one-line marker when opt-in is active. Acceptable for the scoping commitment, or should the actual text be drafted in this scoping bridge? Recommendation: defer text drafting to impl bridge.

4. **§3.1 test refactor scope:** The test sketch suggests refactoring the functions to take an `include_user_extensions` arg for cleaner testing. Acceptable scope expansion, or should tests work via env-var only without function-signature change? Recommendation: env-var only — minimal change; tests can monkeypatch the env var.

5. **Work_list row-17 status update timing:** Should this scoping bridge update row-17 to "scoping in flight; impl pending"? Recommendation: no — leave row-17 as-is until impl VERIFIED (§3.4). Avoids premature status churn.

---

## §6. Owner directive compliance

- Project root boundary: ✓ Option C honors the rule (default root-contained); opt-in is explicit owner choice.
- Bridge protocol: ✓ REVISED-1 of scoping; awaits GO.
- `feedback_no_hardcoded_paths.md`: ✓ env var is parameterization, not hard-coding.
- `feedback_scope_reduction_as_no_go_response.md`: ✓ scope reduced from "broad accept-as-exception" to "default-secure with opt-in"; tighter than `-001`'s Option B.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
