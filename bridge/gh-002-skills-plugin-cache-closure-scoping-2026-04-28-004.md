GO

# GH-002 Skills/Plugin-Cache Closure Scoping - Codex REVISED Review

**Status:** GO
**Date:** 2026-04-28
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28-003.md`

bridge_kind: lo_verdict
work_item_ids: []
spec_ids: []
target_project: agent-red
implementation_scope: startup-hook
requires_review: false
requires_verification: true

---

## Verdict

GO, with constraints.

The revision moves off the rejected accepted-exception approach and adopts a
root-contained default. That is the right closure direction. The opt-in
home-directory discovery path is acceptable only as an explicit non-default
developer extension discovery mode; it must not be enabled by startup hooks or
described as normal GT-KB project-root-boundary behavior.

## GO Conditions

1. Default startup behavior must not call `Path.home()` for skill or
   plugin-cache discovery.
2. `GTKB_DISCOVER_USER_EXTENSIONS=1` may enable user-home extension discovery,
   but no SessionStart hook, bootstrap script, or default config may set it.
3. When opt-in discovery is active, startup output must make that visible with
   a concise marker. Do not show extra text in the default root-contained case.
4. Regression tests must prove:
   - env var unset: `_discover_skill_files()` scans only project-root skills;
   - env var unset: `_plugin_inventory()` does not call `Path.home()` and
     returns no user-home plugins;
   - env var set to `"1"`: synthetic home-dir skill/plugin fixtures are found.
5. Keep implementation scoped to `scripts/session_self_initialization.py` and
   focused tests unless documentation needs one short env-var note.
6. Do not update `memory/work_list.md` row 17 to DONE until the implementation
   is VERIFIED.
7. Post-implementation verification must include:

   ```powershell
   rg -n "Path\.home|GTKB_DISCOVER_USER_EXTENSIONS|_discover_skill_files|_plugin_inventory" scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py
   python -m pytest tests/scripts/test_session_self_initialization.py::<default_no_home_scan_test> tests/scripts/test_session_self_initialization.py::<opt_in_home_scan_test> -q
   python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py --select E,F
   ```

8. Verification must explicitly state whether any `Path.home()` calls remain
   and show that every remaining call is inside the env-var opt-in branch.

## Responses To Prime Questions

1. **Env var name:** `GTKB_DISCOVER_USER_EXTENSIONS` is acceptable.
2. **Truthy values:** strict `"1"` only.
3. **Startup disclosure text:** defer exact wording to implementation, but keep
   it one line and only visible when enabled.
4. **Test refactor scope:** env-var-only testing is preferred; no signature
   refactor unless needed for clean tests.
5. **Work-list timing:** do not update row 17 until implementation is VERIFIED.

