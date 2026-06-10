VERIFIED

# GH-002 Skills/Plugin-Cache Closure Scoping - Codex Verification

**Status:** VERIFIED
**Date:** 2026-04-28
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28-005.md`

bridge_kind: lo_verdict
work_item_ids: []
spec_ids: []
target_project: agent-red
implementation_scope: startup-hook
requires_review: false
requires_verification: false

---

## Verdict

VERIFIED.

Commit `cffd00df` implements the approved Option C closure path: default
startup discovery is root-contained, and user-home skill/plugin-cache discovery
is available only through explicit `GTKB_DISCOVER_USER_EXTENSIONS=1` opt-in.

## Verification Evidence

Targeted regression tests:

```powershell
python -m pytest tests/scripts/test_session_self_initialization.py::test_default_invocation_does_not_scan_home_directory_for_skills_or_plugins tests/scripts/test_session_self_initialization.py::test_opt_in_invocation_scans_home_directory_for_skills_and_plugins tests/scripts/test_session_self_initialization.py::test_startup_payload_marks_user_extension_discovery_state -q
```

Result:

```text
3 passed
```

Ruff:

```powershell
python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py --select E,F
```

Result:

```text
All checks passed!
```

Remaining `Path.home()` calls:

```text
scripts/session_self_initialization.py:1057: Path.home() / ".codex" / "skills"
scripts/session_self_initialization.py:1058: Path.home() / ".agents" / "skills"
scripts/session_self_initialization.py:1081: plugin_cache = Path.home() / ".codex" / "plugins" / "cache"
```

All three executable calls are inside the opt-in path:

- skill paths are added only inside `if _user_extension_discovery_opt_in():`
- plugin cache is reached only after `if not _user_extension_discovery_opt_in(): return sorted(plugins)`
- `_user_extension_discovery_opt_in()` returns true only when
  `GTKB_DISCOVER_USER_EXTENSIONS == "1"`

Search for `GTKB_DISCOVER_USER_EXTENSIONS` found only read/description sites in
`scripts/session_self_initialization.py`; no hook or default config sets the
variable.

Manual model checks:

```text
default: user_extension_discovery=default_root_contained
default: skills_source=project .claude/skills (root-contained default per project-root-boundary)
default: plugins_source=default root-contained (no plugin cache scan; opt-in via GTKB_DISCOVER_USER_EXTENSIONS=1)

opt-in: user_extension_discovery=opt_in_active
opt-in: skills_source=project .claude/skills plus opt-in local harness skill directories
opt-in: plugins_source=opt-in local harness plugin cache via GTKB_DISCOVER_USER_EXTENSIONS=1
```

The default case remains root-contained. The opt-in state is explicit.

## Notes

Commit `cffd00df` also updates `scripts/guardrails/assertion-baseline.json` as
assertion-ratchet bookkeeping. `memory/work_list.md` row 17 was correctly left
unchanged until after this verification.

## Responses To Prime Questions

1. **Skills count default behavior:** Acceptable. The count should reflect what
   was actually scanned.
2. **GH-002 row-17 closure:** Use a separate scoped commit for the work-list
   status update and any generator-hardening close-out bridge audit.

