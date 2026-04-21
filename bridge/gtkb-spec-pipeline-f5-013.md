# F5: Requirement Intake Pipeline — REVISED v7

**Revision:** Addresses 2 conditions from NO-GO bridge/gtkb-spec-pipeline-f5-012.md

---

## Changes From v6

| Condition | Resolution |
|-----------|-----------|
| 1. Malformed settings.local.json can crash doctor | Added try/except for `json.JSONDecodeError` and `OSError` in `_check_settings_classifiers()`. Returns warning ToolCheck naming the file and error. Added malformed-settings doctor test. |
| 2. `gt project upgrade` does not manage `intake-classifier.py` | Added `intake-classifier.py` to `_MANAGED_HOOKS` in upgrade planner. Settings swap remains manual (documented). Added upgrade test. |

---

## Content Parsing, Storage Contract (unchanged)

Intake API parses `json.loads(d["content"])` internally. Storage uses `owner_conversation`/`deferred|owner_decision|no_go`.

## Settings Template (unchanged)

New projects get `intake-classifier.py` in `UserPromptSubmit`.

## Project Doctor — Settings Classifier Check (updated in v7)

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
    
    upsub_hooks = settings.get("hooks", {}).get("UserPromptSubmit", [])
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

**Defensive handling covers:**
- Missing file → warning (cannot verify)
- Unreadable file (OSError) → warning naming error
- Invalid JSON → warning naming parse error
- Non-dict top-level → warning
- Non-list UserPromptSubmit → warning
- Non-dict entries in array → silently skipped (only dict entries inspected)

## Upgrade Planner Integration (NEW in v7)

**File:** `src/groundtruth_kb/project/upgrade.py`

Add `intake-classifier.py` to the `_MANAGED_HOOKS` set:

```python
_MANAGED_HOOKS = {
    "assertion-check.py",
    "spec-classifier.py",
    "intake-classifier.py",   # Added by F5
    "destructive-gate.py",
    "credential-scan.py",
    "scheduler.py",
}
```

**Effect:** `gt project upgrade` will copy `intake-classifier.py` from templates to `.claude/hooks/` if it's missing. This ensures the hook file is present on disk after upgrade. The settings swap (activating `intake-classifier.py` instead of `spec-classifier.py` in settings) remains a manual step, documented in the upgrade guide.

**Why not auto-swap settings:** The upgrade planner manages file presence, not settings content. Auto-editing `settings.local.json` would be a new capability with higher risk (could break customized hook configurations). The doctor check surfaces the issue; the docs explain the fix.

**Non-bridge profile handling:** Current upgrade planning narrows managed hooks for non-bridge profiles (upgrade.py:84-95). `intake-classifier.py` should be in the base set alongside `spec-classifier.py` since both are available to all profiles. The profile narrowing logic selects from `_MANAGED_HOOKS` by name — it already includes `spec-classifier.py` in the non-bridge narrowed set. Add `intake-classifier.py` to the same narrowed set.

## Template Docs and Upgrade Guidance (unchanged + expanded)

Upgrade docs now reference `gt project upgrade` as the first step:

1. Run `gt project upgrade` — copies `intake-classifier.py` to `.claude/hooks/` if missing
2. In `.claude/settings.local.json`, replace `spec-classifier.py` with `intake-classifier.py` in `UserPromptSubmit`
3. Run `gt doctor` — verify classifier check passes (should show "Active classifier: intake-classifier.py")
4. Test with `gt intake list`

## Revised Test Plan (16 cases)

### Intake API (8 tests — unchanged)
1-8: Classification, capture, confirm, reject, list-pending, cross-session, roundtrip (same as v6)

### Scaffold & Doctor (6 tests — expanded in v7)
9. **Scaffold activation** — New project → settings references `intake-classifier.py` only; both hook files on disk
10. **Doctor: only intake active** — settings has `intake-classifier.py` → pass
11. **Doctor: only spec active** — settings has `spec-classifier.py` → pass (legacy)
12. **Doctor: both active** — settings has both → warning naming both
13. **Doctor: neither active** — settings has no classifier → warning
14. **Doctor: malformed settings** — `settings.local.json` contains invalid JSON → warning with parse error message, doctor does NOT crash

### Upgrade (2 tests — NEW in v7)
15. **Upgrade copies intake hook** — Existing project without `intake-classifier.py` → run upgrade → `intake-classifier.py` present in `.claude/hooks/`
16. **Upgrade preserves existing hooks** — Existing project with `spec-classifier.py` already present → run upgrade → both files present, settings unchanged

---

*Submitted by: S287-Prime*
*Revision: v7 — addresses NO-GO bridge/gtkb-spec-pipeline-f5-012.md*
