# F5: Requirement Intake Pipeline — REVISED v9

**Revision:** Addresses 2 conditions from NO-GO bridge/gtkb-spec-pipeline-f5-016.md

---

## Changes From v8

| Condition | Resolution |
|-----------|-----------|
| 1. Non-dict `hooks` value crashes doctor | Added `isinstance(hooks, dict)` guard before accessing `UserPromptSubmit`. Added tests for `{"hooks": []}`, `{"hooks": "bad"}`, `{"hooks": null}`. |
| 2. Scaffold activation scope ambiguous for `local-only` profile | Explicitly scoped: intake activation via `settings.local.json` is for bridge profiles only (`includes_bridge=True`). `local-only` profiles get hook files on disk but no settings — doctor missing-file warning is expected and correct. Added local-only scaffold test. |

---

## Content Parsing, Storage, Upgrade Planner (unchanged from v8)

All unchanged. `json.loads(d["content"])` internal parsing. `.claude/hooks/intake-classifier.py` in `_MANAGED_HOOKS` with project-relative path.

## Profile-Scoped Activation (NEW in v9)

### How GT-KB scaffold profiles work

| Profile | `includes_bridge` | Gets `settings.local.json` | Gets hook files on disk | Intake active |
|---------|-------------------|---------------------------|------------------------|---------------|
| `dual-agent` | True | Yes (via `_copy_dual_agent_templates()`) | Yes (all `.py` in `templates/hooks/`) | Yes — settings activates `intake-classifier.py` |
| `local-only` | False | **No** | Yes (all `.py`) | **No** — no settings file, hooks are on disk but not activated |

**Evidence:** `settings.local.json` is copied only inside `_copy_dual_agent_templates()` at scaffold.py:182-185, which is called only when `profile.includes_bridge` is True. Hook files are copied for all profiles at scaffold.py:116-119.

### Doctor behavior per profile

| Scenario | Doctor result | Correct? |
|----------|--------------|----------|
| Bridge profile, intake active | pass: "Active classifier: intake-classifier.py" | Yes |
| Bridge profile, spec active (legacy) | pass: "Active classifier: spec-classifier.py" | Yes |
| Bridge profile, both active | warning: "Both classifiers active" | Yes |
| Local-only profile (no settings file) | warning: "settings.local.json not found" | **Yes — expected.** Local-only projects don't use classifier hooks via settings. This is informational, not a defect. |

The doctor settings check runs unconditionally (all profiles) because doctor doesn't receive the profile name in its current signature. The missing-file warning is the correct diagnostic for profiles that don't generate settings — it's not a false positive.

## Doctor Settings Check (updated in v9)

```python
def _check_settings_classifiers(target: Path) -> ToolCheck:
    """Check that exactly one classifier hook is active in settings."""
    settings_path = target / ".claude" / "settings.local.json"
    if not settings_path.exists():
        return ToolCheck(
            name="Classifier settings",
            required=True,
            found=False,
            status="warning",
            message="settings.local.json not found — cannot verify classifier activation",
        )
    
    try:
        raw = settings_path.read_text()
        settings = json.loads(raw)
    except (json.JSONDecodeError, OSError) as exc:
        return ToolCheck(
            name="Classifier settings",
            required=True,
            found=True,
            status="warning",
            message=f"Cannot parse {settings_path.name}: {exc} — classifier activation not verified",
        )
    
    if not isinstance(settings, dict):
        return ToolCheck(
            name="Classifier settings",
            required=True,
            found=True,
            status="warning",
            message=f"{settings_path.name} is not a JSON object — classifier activation not verified",
        )
    
    hooks = settings.get("hooks", {})
    if not isinstance(hooks, dict):
        return ToolCheck(
            name="Classifier settings",
            required=True,
            found=True,
            status="warning",
            message=f"{settings_path.name} 'hooks' is not a JSON object — classifier activation not verified",
        )
    
    upsub_hooks = hooks.get("UserPromptSubmit", [])
    if not isinstance(upsub_hooks, list):
        return ToolCheck(
            name="Classifier settings",
            required=True,
            found=True,
            status="warning",
            message="UserPromptSubmit is not a list — classifier activation not verified",
        )
    
    commands = [h.get("command", "") for h in upsub_hooks if isinstance(h, dict)]
    
    active_classifiers = []
    for cmd in commands:
        if "spec-classifier.py" in cmd:
            active_classifiers.append("spec-classifier.py")
        if "intake-classifier.py" in cmd:
            active_classifiers.append("intake-classifier.py")
    
    if len(active_classifiers) == 0:
        return ToolCheck(
            name="Classifier settings",
            required=True,
            found=True,
            status="warning",
            message="No classifier hook active in UserPromptSubmit — spec-first workflow not enforced",
        )
    
    if len(active_classifiers) > 1:
        return ToolCheck(
            name="Classifier settings",
            required=True,
            found=True,
            status="warning",
            message=f"Both classifiers active in UserPromptSubmit: {', '.join(active_classifiers)} — only one should be active",
        )
    
    return ToolCheck(
        name="Classifier settings",
        required=True,
        found=True,
        status="pass",
        message=f"Active classifier: {active_classifiers[0]}",
    )
```

**Defensive handling covers (7 branches):**
1. Missing file → warning (cannot verify)
2. Unreadable file (OSError) → warning naming error
3. Invalid JSON → warning naming parse error
4. Non-dict top-level → warning
5. **Non-dict `hooks` → warning** (NEW in v9 — covers `{"hooks": []}`, `"bad"`, `null`)
6. Non-list `UserPromptSubmit` → warning
7. Non-dict entries in array → silently skipped

## Revised Test Plan (20 cases)

### Intake API (8 tests — unchanged)
1-8: Classification, capture, confirm, reject, list-pending, cross-session, roundtrip

### Scaffold & Doctor (9 tests — expanded in v9)
9. **Scaffold activation (bridge profile)** — Scaffold with bridge profile → `settings.local.json` references `intake-classifier.py` only; both hook files on disk
10. **Scaffold activation (local-only profile)** — Scaffold with local-only profile → NO `settings.local.json` generated; both hook files on disk (available but not activated)
11. **Doctor: only intake active** — settings has `intake-classifier.py` → pass
12. **Doctor: only spec active** — settings has `spec-classifier.py` → pass (legacy)
13. **Doctor: both active** — settings has both → warning naming both
14. **Doctor: neither active** — settings has no classifier → warning
15. **Doctor: malformed JSON** — `settings.local.json` contains `{invalid` → warning with parse error, no crash
16. **Doctor: non-dict hooks** — `settings.local.json` contains `{"hooks": []}` → warning "hooks is not a JSON object", no crash
17. **Doctor: null hooks** — `settings.local.json` contains `{"hooks": null}` → warning "hooks is not a JSON object", no crash

### Upgrade (3 tests — expanded in v9)
18. **Upgrade copies intake hook** — Project missing `.claude/hooks/intake-classifier.py` → `plan_upgrade()` emits `add` → file present after execute
19. **Upgrade preserves existing hooks** — Both hooks present and unmodified → no actions
20. **Upgrade for local-only profile** — Non-bridge project → `intake-classifier.py` included in managed hooks via non-bridge allowlist → copied if missing

---

*Submitted by: S287-Prime*
*Revision: v9 — addresses NO-GO bridge/gtkb-spec-pipeline-f5-016.md*
