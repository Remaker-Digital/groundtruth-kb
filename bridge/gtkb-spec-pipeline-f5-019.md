# F5: Requirement Intake Pipeline — REVISED v10

**Revision:** Addresses 1 condition from NO-GO bridge/gtkb-spec-pipeline-f5-018.md

---

## Changes From v9

| Condition | Resolution |
|-----------|-----------|
| 1. Local-only projects get permanent warning for expected missing settings | Scoped `_check_settings_classifiers()` to bridge profiles only, matching the existing `if p.includes_bridge:` pattern at doctor.py:480-498. Local-only projects skip the check entirely — no false warning. Added local-only regression test. Corrected the v9 claim that doctor doesn't receive profile (it does, at doctor.py:464-466). |

---

## Content Parsing, Storage, Upgrade Planner, Hook Templates (unchanged)

All unchanged from v8/v9.

## Doctor Integration — Profile-Scoped (corrected in v10)

### Where the check is added in `run_doctor()` (doctor.py:464-506)

```python
def run_doctor(target: Path, profile: str, *, auto_install: bool = False) -> DoctorReport:
    p = get_profile(profile)
    checks: list[ToolCheck] = []

    # ... system tools (lines 474-489) ...

    # Project-level checks
    checks.append(_check_groundtruth_toml(target))
    checks.append(_check_db_schema(target))
    checks.append(_check_hooks(target, profile))
    checks.append(_check_rules(target, profile))

    if p.includes_bridge:
        checks.append(_check_file_bridge_setup(target))
        checks.append(_check_settings_classifiers(target))  # F5: added here

    # ... auto-install, report (lines 500-506) ...
```

**Why scoped to `includes_bridge`:** Only bridge profiles generate `settings.local.json` via `_copy_dual_agent_templates()` (scaffold.py:182-185). The classifier settings check is meaningful only when settings exist by design. Local-only profiles never generate this file, so checking for it would produce a permanent false warning.

**Pattern match:** This follows the existing doctor scoping pattern where `_check_file_bridge_setup()`, `_check_claude_code()` are already gated by `p.includes_bridge` (doctor.py:480-481 and doctor.py:497-498).

### `_check_settings_classifiers()` (unchanged from v9)

The function itself is unchanged — all 7 defensive branches remain:
1. Missing file → warning
2. Unreadable file (OSError) → warning
3. Invalid JSON → warning
4. Non-dict top-level → warning
5. Non-dict `hooks` → warning
6. Non-list `UserPromptSubmit` → warning
7. Non-dict entries in array → silently skipped

Within bridge profiles, these warnings are all legitimate diagnostics of misconfigured settings. None of them are false positives because bridge profiles are expected to have a valid `settings.local.json`.

## Revised Test Plan (21 cases)

### Intake API (8 tests — unchanged)
1-8: Classification, capture, confirm, reject, list-pending, cross-session, roundtrip

### Scaffold (2 tests)
9. **Scaffold activation (bridge profile)** — Bridge scaffold → `settings.local.json` references `intake-classifier.py` only; both hook files on disk
10. **Scaffold activation (local-only profile)** — Local-only scaffold → NO `settings.local.json`; both hook files on disk

### Doctor — Bridge Profile (7 tests)
11. **Doctor: only intake active** → pass
12. **Doctor: only spec active** → pass (legacy)
13. **Doctor: both active** → warning naming both
14. **Doctor: neither active** → warning
15. **Doctor: malformed JSON** → warning with parse error, no crash
16. **Doctor: non-dict hooks** (`{"hooks": []}`) → warning "hooks is not a JSON object", no crash
17. **Doctor: null hooks** (`{"hooks": null}`) → warning "hooks is not a JSON object", no crash

### Doctor — Local-Only Profile (1 test — NEW in v10)
18. **Doctor: local-only no false warning** — Fresh `local-only` scaffold → `run_doctor(target, "local-only")` → report does NOT contain a `Classifier settings` check at all (check not added to list). Overall status is not degraded by absence of settings file.

### Upgrade (3 tests — unchanged from v9)
19. **Upgrade copies intake hook** → `plan_upgrade()` emits `add` → file present
20. **Upgrade preserves existing hooks** → both present and unmodified → no actions
21. **Upgrade for local-only profile** → `intake-classifier.py` in non-bridge allowlist → copied if missing

---

*Submitted by: S287-Prime*
*Revision: v10 — addresses NO-GO bridge/gtkb-spec-pipeline-f5-018.md*
