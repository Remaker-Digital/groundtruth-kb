# F5: Requirement Intake Pipeline — REVISED v6

**Revision:** Addresses 1 condition from NO-GO bridge/gtkb-spec-pipeline-f5-010.md

---

## Changes From v5

| Condition | Resolution |
|-----------|-----------|
| 1. Both-active classifier detection is advisory and untested | Made settings-level classifier check mandatory in doctor. Doctor reads `settings.local.json` and warns if both `spec-classifier.py` and `intake-classifier.py` appear in `UserPromptSubmit`. Added 3 doctor tests for the dual-classifier scenario. |

---

## Content Parsing, Storage Contract, Hook Template Files (unchanged from v5)

- Intake API parses `json.loads(d["content"])` internally
- Storage uses `owner_conversation`/`deferred` for pending, `owner_decision` for confirmed, `no_go` for rejected
- Both hook files copied to disk by scaffold; active hook determined by `settings.local.json`

## Settings Template (unchanged from v5)

New projects get `intake-classifier.py` in `UserPromptSubmit`. `spec-classifier.py` available on disk as fallback.

## Project Doctor — Mandatory Classifier Guard (updated in v6)

### Hook File Presence Check (existing behavior, updated)

```python
def _check_hooks(target: Path, profile_name: str) -> ToolCheck:
    hooks_dir = target / ".claude" / "hooks"
    # ...existing directory check...
    required_hooks = {"assertion-check.py"}
    classifier_hooks = {"spec-classifier.py", "intake-classifier.py"}
    
    # Require at least one classifier hook file on disk
    if not present.intersection(classifier_hooks):
        missing.add("spec-classifier.py or intake-classifier.py")
    # ...rest of existing logic...
```

### Settings Activation Check (NEW — mandatory)

```python
def _check_settings_classifiers(target: Path) -> ToolCheck:
    """Check that exactly one classifier hook is active in settings.
    
    Reads .claude/settings.local.json and inspects UserPromptSubmit commands.
    """
    settings_path = target / ".claude" / "settings.local.json"
    if not settings_path.exists():
        return ToolCheck(
            name="Classifier settings",
            required=True,
            found=False,
            status="warning",
            message="settings.local.json not found — cannot verify classifier activation",
        )
    
    settings = json.loads(settings_path.read_text())
    upsub_hooks = settings.get("hooks", {}).get("UserPromptSubmit", [])
    commands = [h.get("command", "") for h in upsub_hooks]
    
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
            message=f"Both classifiers active in UserPromptSubmit: {', '.join(active_classifiers)} — only one should be active to avoid double classification",
        )
    
    return ToolCheck(
        name="Classifier settings",
        required=True,
        found=True,
        status="pass",
        message=f"Active classifier: {active_classifiers[0]}",
    )
```

**Integration:** `_check_settings_classifiers()` is called alongside `_check_hooks()` in the doctor's check list. It is a mandatory check (not advisory).

**Why warning, not failure, for both-active:** The project can still function with both classifiers — it's a degraded mode, not a broken state. But it's a loud warning that surfaces in `gt doctor` output, not a silent skip. This matches the existing doctor pattern where non-critical-but-wrong states are warnings.

## Template Docs and Upgrade Guidance (unchanged from v5)

- `docs/reference/templates.md`: both hooks in reference table, intake as default, spec as legacy
- `docs/guides/upgrading.md`: 4-step upgrade (copy file, swap settings, run doctor, test)

## Revised Test Plan (13 cases)

### Intake API (8 tests — unchanged from v5)
1. **Directive classification** — "MUST" keyword; classification=directive, confidence > 0.8
2. **Exploration classification** — "what if" phrasing; classification=exploration, confidence < 0.5
3. **Capture persistence** — Capture → verify deliberation with valid source_type/outcome/JSON content
4. **Confirm flow** — Capture + confirm → outcome='owner_decision', spec created
5. **Reject flow** — Capture + reject → outcome='no_go', rejection_reason set
6. **List pending with JSON parsing** — 2 intake candidates + 1 free-text + 1 malformed JSON → `list_pending()` returns exactly 2
7. **Cross-session persistence** — Capture in session A; list in session B; still pending
8. **List pending roundtrip** — Insert → list_deliberations → filter logic; candidate appears

### Scaffold & Doctor (5 tests — expanded in v6)
9. **Scaffold activation** — Scaffold new project → `settings.local.json` references `intake-classifier.py`, does NOT reference `spec-classifier.py`; both hook files exist on disk
10. **Doctor: only intake active** — `settings.local.json` has `intake-classifier.py` in `UserPromptSubmit`, both hook files on disk → doctor passes (status=pass, message names intake)
11. **Doctor: only spec active** — `settings.local.json` has `spec-classifier.py` in `UserPromptSubmit` → doctor passes (legacy project, still valid)
12. **Doctor: both classifiers active** — `settings.local.json` has both `spec-classifier.py` AND `intake-classifier.py` in `UserPromptSubmit` → doctor returns warning with message naming both classifiers
13. **Doctor: neither classifier active** — `settings.local.json` has no classifier in `UserPromptSubmit` → doctor returns warning about unenforced spec-first workflow

---

*Submitted by: S287-Prime*
*Revision: v6 — addresses NO-GO bridge/gtkb-spec-pipeline-f5-010.md*
