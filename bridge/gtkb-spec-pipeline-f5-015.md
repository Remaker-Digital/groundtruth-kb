# F5: Requirement Intake Pipeline — REVISED v8

**Revision:** Addresses 1 condition from NO-GO bridge/gtkb-spec-pipeline-f5-014.md

---

## Changes From v7

| Condition | Resolution |
|-----------|-----------|
| 1. `_MANAGED_HOOKS` entry uses bare filename instead of project-relative path | Changed to `.claude/hooks/intake-classifier.py` matching upgrade.py's contract. Added to non-bridge profile narrowing allowlist alongside `spec-classifier.py`. |

---

## Content Parsing, Storage, Settings Template, Doctor (unchanged from v7)

All unchanged. Intake API parses `json.loads(d["content"])` internally. Doctor catches `JSONDecodeError`/`OSError` on malformed settings. Mandatory single-classifier check.

## Upgrade Planner Integration (corrected in v8)

**File:** `src/groundtruth_kb/project/upgrade.py`

### 1. Add to `_MANAGED_HOOKS` (line 27-33)

```python
_MANAGED_HOOKS = [
    ".claude/hooks/assertion-check.py",
    ".claude/hooks/spec-classifier.py",
    ".claude/hooks/intake-classifier.py",   # Added by F5
    ".claude/hooks/destructive-gate.py",
    ".claude/hooks/credential-scan.py",
    ".claude/hooks/scheduler.py",
]
```

**Format:** Project-relative path starting with `.claude/hooks/`. This allows `_map_managed_to_template()` (upgrade.py:57-63) to map it to `hooks/intake-classifier.py` in the templates directory. The mapping works because it checks `managed.startswith(".claude/hooks/")` and extracts the basename.

### 2. Add to non-bridge profile narrowing (line 84-95)

```python
if not profile.includes_bridge:
    managed = [
        h
        for h in managed
        if h.split("/")[-1]
        in {
            "assertion-check.py",
            "spec-classifier.py",
            "intake-classifier.py",   # Added by F5
        }
    ]
```

**Effect:** Non-bridge profiles (which don't need `destructive-gate.py`, `credential-scan.py`, or `scheduler.py`) still get `intake-classifier.py` managed during upgrades, alongside `assertion-check.py` and `spec-classifier.py`.

### 3. Upgrade execution flow

When `plan_upgrade()` runs for a project missing `intake-classifier.py`:
1. `mfile = ".claude/hooks/intake-classifier.py"` → `project_path = target / ".claude/hooks/intake-classifier.py"`
2. `project_path.exists()` → False
3. `_map_managed_to_template(mfile)` → `"hooks/intake-classifier.py"`
4. Template exists in `templates/hooks/intake-classifier.py` → action: `add`
5. `execute_upgrade()` copies template to project path

Settings swap (activating intake in `UserPromptSubmit`) remains manual — documented in upgrade guide.

## Revised Test Plan (16 cases — unchanged from v7 except clarification)

### Intake API (8 tests — unchanged)
1-8: Classification, capture, confirm, reject, list-pending, cross-session, roundtrip

### Scaffold & Doctor (6 tests — unchanged from v7)
9-14: Scaffold activation, doctor only-intake/only-spec/both/neither/malformed

### Upgrade (2 tests — clarified in v8)
15. **Upgrade copies intake hook** — Existing project without `.claude/hooks/intake-classifier.py` → `plan_upgrade()` returns an `add` action for `.claude/hooks/intake-classifier.py` → `execute_upgrade()` copies from `templates/hooks/intake-classifier.py` → file present after upgrade
16. **Upgrade preserves existing hooks** — Existing project with both `spec-classifier.py` and `intake-classifier.py` already present and unmodified → `plan_upgrade()` returns no action for either (template hash matches) → settings unchanged

---

*Submitted by: S287-Prime*
*Revision: v8 — addresses NO-GO bridge/gtkb-spec-pipeline-f5-014.md*
