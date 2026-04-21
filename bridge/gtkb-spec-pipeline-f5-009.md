# F5: Requirement Intake Pipeline — REVISED v5

**Revision:** Addresses 1 condition from NO-GO bridge/gtkb-spec-pipeline-f5-008.md

---

## Changes From v4

| Condition | Resolution |
|-----------|-----------|
| 1. Scaffold wiring for `intake-classifier.py` not specified or tested | Specified 4 adoption changes: settings template, doctor hook check, template docs, and upgrade guidance. Added scaffold activation test. |

---

## Deliberation Content Parsing (unchanged from v4)

Intake API parses `json.loads(d["content"])` internally. No GT-KB core (`_row_to_dict`) change.

## Storage Contract (unchanged from v4)

| Intake state | source_type | outcome | content (JSON) |
|-------------|-------------|---------|----------------|
| Captured (pending) | `owner_conversation` | `deferred` | `{"intake_type": "requirement_candidate", "intake_status": "pending", ...}` |
| Confirmed (promoted) | `owner_conversation` | `owner_decision` | `{"intake_type": "requirement_candidate", "intake_status": "confirmed", "confirmed_spec_id": "SPEC-NNNN", ...}` |
| Rejected | `owner_conversation` | `no_go` | `{"intake_type": "requirement_candidate", "intake_status": "rejected", ...}` |

## Hook Adoption Chain (NEW in v5)

### 1. Settings Template Update

**File:** `templates/project/settings.local.json`

Replace `spec-classifier.py` with `intake-classifier.py` in the `UserPromptSubmit` hooks:

```json
"UserPromptSubmit": [
  {
    "command": "python .claude/hooks/intake-classifier.py"
  },
  {
    "command": "python .claude/hooks/scheduler.py"
  }
]
```

**Why replace rather than add alongside:** Only one classifier hook should be active at a time. Running both would double-classify owner input. The settings template defines what NEW projects get. Existing projects opt in via the upgrade path (see below).

### 2. Hook Template Files

**Keep:** `templates/hooks/spec-classifier.py` — unchanged, available as fallback for projects that don't want intake.

**Add:** `templates/hooks/intake-classifier.py` — new hook that calls the intake API.

**Scaffold behavior (scaffold.py:116-119):** The existing `for src in (templates / "hooks").glob("*.py")` copies ALL hook .py files to `.claude/hooks/`. Both hook files will be present on disk. The ACTIVE hook is determined by `settings.local.json`, not by file presence. This is the existing pattern — scaffold copies all hooks, settings activates the subset needed.

### 3. Project Doctor Update

**File:** `src/groundtruth_kb/project/doctor.py:305`

Current required hooks: `{"assertion-check.py", "spec-classifier.py"}`

Change to accept exactly one classifier hook:

```python
required_hooks = {"assertion-check.py"}
classifier_hooks = {"spec-classifier.py", "intake-classifier.py"}
# Require at least one classifier hook is present
if not present.intersection(classifier_hooks):
    missing.add("spec-classifier.py or intake-classifier.py")
# Warn if both are active in settings (not just present on disk)
```

The doctor checks file PRESENCE, not settings activation. Since scaffold copies both hooks, doctor should require at least one classifier hook exists, not demand a specific one. A separate advisory check can warn if both classifiers appear in the `UserPromptSubmit` settings array.

### 4. Template Docs and Upgrade Guidance

**File:** `docs/reference/templates.md` (update hooks section)

Add `intake-classifier.py` to the hooks reference table:

| Hook | Event | Purpose | Default |
|------|-------|---------|---------|
| `spec-classifier.py` | `UserPromptSubmit` | Static spec-first workflow enforcement | Legacy (pre-intake) |
| `intake-classifier.py` | `UserPromptSubmit` | Structured requirement intake + spec-first enforcement | Default for new projects |
| `assertion-check.py` | `SessionStart` | Run assertion health check | Required |

**File:** `docs/guides/upgrading.md` (new section or update existing)

Upgrade steps for existing projects:
1. Ensure `intake-classifier.py` exists in `.claude/hooks/` (copy from templates if missing)
2. In `.claude/settings.local.json`, replace `spec-classifier.py` with `intake-classifier.py` in `UserPromptSubmit`
3. Verify with `gt doctor` — should show no hook warnings
4. Test with `gt intake list` — should return empty list (no pending candidates)

**Key constraint:** At no point should both classifiers be active in `UserPromptSubmit`. The upgrade replaces one with the other; it does not add a second entry.

## Revised Test Plan (10 cases)

1. **Directive classification** — "MUST" keyword; classification=directive, confidence > 0.8
2. **Exploration classification** — "what if" phrasing; classification=exploration, confidence < 0.5
3. **Capture persistence** — Capture candidate; verify deliberation with source_type='owner_conversation', outcome='deferred', content is valid JSON with intake_type='requirement_candidate'
4. **Confirm flow** — Capture + confirm; verify outcome updated to 'owner_decision', spec created, content has confirmed_spec_id
5. **Reject flow** — Capture + reject; verify outcome updated to 'no_go', content has rejection_reason
6. **List pending with JSON parsing** — Create 2 intake candidates + 1 regular deferred deliberation with free-text + 1 with malformed JSON; verify `list_pending()` returns exactly 2 intake candidates
7. **Cross-session persistence** — Capture in session A; list in session B; verify still pending
8. **List pending roundtrip** — Insert deliberation → `list_deliberations()` → filter logic; verify candidate appears (proves `content` is a parseable string in returned rows)
9. **Scaffold activation** — Run scaffold for new project; read generated `settings.local.json`; assert `UserPromptSubmit` references `intake-classifier.py` and does NOT reference `spec-classifier.py`; assert both hook files exist on disk
10. **Doctor accepts either classifier** — Project with only `intake-classifier.py` → doctor passes; project with only `spec-classifier.py` → doctor passes; project with neither → doctor warns

---

*Submitted by: S287-Prime*
*Revision: v5 — addresses NO-GO bridge/gtkb-spec-pipeline-f5-008.md*
