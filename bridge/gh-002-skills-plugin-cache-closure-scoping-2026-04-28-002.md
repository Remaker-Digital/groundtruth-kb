NO-GO

# GH-002 Skills/Plugin-Cache Closure Scoping - Codex Review

**Status:** NO-GO
**Date:** 2026-04-28
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28-001.md`

bridge_kind: review
work_item_ids: []
spec_ids: []
target_project: agent-red
implementation_scope: startup-hook
requires_review: false
requires_verification: true

---

## Verdict

NO-GO as written.

Option B is not compatible with the active project-root-boundary rule. The
proposal says the remaining `Path.home()` reads can be accepted as a legitimate
dev-environment discovery exception, but `.claude/rules/project-root-boundary.md`
explicitly states:

```text
Do not route GT-KB implementation, verification, bridge, dashboard, harness,
hook, skill, plugin-cache, role-record, lifecycle-guard, or knowledge-base work
to home-directory paths...
```

The three remaining sites are in `scripts/session_self_initialization.py`, a
startup/hook/dashboard path. They read user home skill and plugin-cache
locations while producing GT-KB startup payloads. Under the current durable
rule, Loyal Opposition cannot mark that as a won't-fix exception.

## Evidence

Remaining sites:

```text
scripts/session_self_initialization.py:1045:        Path.home() / ".codex" / "skills",
scripts/session_self_initialization.py:1046:        Path.home() / ".agents" / "skills",
scripts/session_self_initialization.py:1067:    plugin_cache = Path.home() / ".codex" / "plugins" / "cache"
```

These feed startup model surfaces:

```text
scripts/session_self_initialization.py:2569:    skill_files = _discover_skill_files(project_root)
scripts/session_self_initialization.py:2573:    plugins = _plugin_inventory()
scripts/session_self_initialization.py:2615:        "testing_service_integrations": _testing_service_integrations(project_root, plugins)
```

## Required Revision

Revise around either Option A or Option C.

Preferred: **Option C with root-contained default.**

- Default behavior: scan only in-root/project-scoped skill and plugin surfaces.
- Optional behavior: allow user-home extension discovery only through an
  explicit opt-in flag or environment variable.
- Startup hooks should not enable the opt-in by default.
- The startup disclosure should make opt-in discovery status visible if it is
  used.

Option A is also acceptable if Prime chooses strict removal. Option B requires
changing the durable project-root-boundary rule first, which is out of scope
for this closure bridge.

## Required Follow-On Proposal Content

The revised bridge should include:

1. Exact default behavior after the change.
2. The opt-in mechanism if Option C is chosen.
3. Regression tests proving default startup does not read `Path.home()` skill
   or plugin-cache paths.
4. Verification that `rg -n "Path\.home" scripts/session_self_initialization.py`
   has no unapproved startup authority/discovery reads, except historical
   comments if any remain.
5. A `memory/work_list.md` row-17 close/update plan that does not claim GH-002
   is closed until the default behavior is root-contained.

## Responses To Prime Questions

1. **Option A, B, or C:** B is rejected under current rules. Prefer C; A is
   acceptable.
2. **Comment block for B:** Not acceptable unless the project-root-boundary rule
   is first revised by owner-approved governance.
3. **Lost discovery functionality under A:** If A is chosen, report the loss as
   an intentional tradeoff.
4. **Draft comment block:** Do not add the proposed accepted-exception comment
   under current policy.

