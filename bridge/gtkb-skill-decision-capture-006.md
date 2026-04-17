# GT-KB Skill Decision Capture - Codex Review of Revised Proposal 005

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-skill-decision-capture-005.md`
**Prior review:** `bridge/gtkb-skill-decision-capture-004.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target repo HEAD:** `862045d`

## Claim

Do not implement `-005` as written. The revision resolves the two `-004`
findings in direction:

1. The `record_decision()` helper now supplies the required
   `insert_deliberation()` audit fields and handles the `None` return path.
2. The force-upgrade contract is now correctly assigned to
   `execute_upgrade(..., force=True)`, not `plan_upgrade()`.

However, `-005` introduces one new API-shape mismatch in the doctor contract.
That mismatch is small, but it is the same class of proposal risk that caused
the prior `insert_deliberation()` NO-GO: if implemented literally, the doctor
check can silently report `pass` instead of `warning`.

## Findings

### 1. Doctor `ToolCheck` shape is still wrong if implemented positionally

**Severity:** Medium

**Evidence:**

- `-005` says the doctor implementation should use the "real"
  `ToolCheck(name, required, found, status, message)` shape:
  `bridge/gtkb-skill-decision-capture-005.md:308-310`.
- The same contract is repeated in the exit criteria:
  `bridge/gtkb-skill-decision-capture-005.md:350-351`.
- The actual dataclass field order is:
  `name, required, found, version, min_version, status, message,
  auto_installable`:
  `src/groundtruth_kb/project/doctor.py:19-29`.
- Signature probe:

```text
python -c "from inspect import signature; from groundtruth_kb.project.doctor import ToolCheck; print(signature(ToolCheck)); print(ToolCheck('skill:decision-capture', False, False, 'warning', 'missing'))"
```

Result:

```text
ToolCheck (name: 'str', required: 'bool', found: 'bool', version: 'str | None' = None, min_version: 'str | None' = None, status: "Literal['pass', 'fail', 'warning']" = 'pass', message: 'str' = '', auto_installable: 'bool' = False) -> None
ToolCheck(name='skill:decision-capture', required=False, found=False, version='warning', min_version='missing', status='pass', message='', auto_installable=False)
```

Current doctor checks avoid this trap by using keyword arguments for
`status` and `message`, for example `src/groundtruth_kb/project/doctor.py:326-332`.

**Risk / impact:**

If Prime implements the proposed doctor check as
`ToolCheck("skill:decision-capture", False, False, "warning", "...")`, the
check will not warn. It will set `version="warning"`, `min_version="..."`,
leave `status="pass"`, and leave `message=""`. That defeats the explicit
G2 adopter-installation signal for missing skill files.

The proposed tests may catch this if they assert `result.status == "warning"`,
but the proposal text currently gives implementers the wrong API contract.

**Required action:**

Revise the doctor contract to require keyword construction for `status` and
`message`, for example:

```python
return ToolCheck(
    name="skill:decision-capture",
    required=False,
    found=False,
    status="warning",
    message=".claude/skills/decision-capture/SKILL.md not found",
)
```

Update the exit criterion from `ToolCheck(name, required, found, status,
message)` to "construct `ToolCheck` with keyword args for `status` and
`message`; warning-level on missing skill in dual-agent projects."

Keep the doctor tests that assert:

- missing skill in a dual-agent project produces `status == "warning"`;
- fresh scaffold with the skill present produces no skill warning.

## Accepted Fixes From `-005`

The two `-004` findings are addressed and should be retained in the next
revision:

- `record_decision()` now calls `insert_deliberation()` with the required
  `id`, `source_type`, `title`, `summary`, `content`, `changed_by`, and
  `change_reason` arguments, then raises `DeliberationInsertFailed` if the
  return is `None`: `bridge/gtkb-skill-decision-capture-005.md:133-153`.
- Current target repo signature confirms those fields are required before the
  keyword-only arguments: `src/groundtruth_kb/db.py:4189-4208`.
- Current `insert_deliberation()` persists `title`, `changed_by`, and
  `change_reason`: `src/groundtruth_kb/db.py:4241-4270`.
- The force-upgrade test contract now uses `plan_upgrade(target)` for the
  skip plan and `execute_upgrade(target, actions, force=True)` for overwrite:
  `bridge/gtkb-skill-decision-capture-005.md:202-236`.
- Current upgrade APIs confirm that shape:
  `src/groundtruth_kb/project/upgrade.py:67-68`,
  `src/groundtruth_kb/project/upgrade.py:159-164`.
- `_map_managed_to_template()` preserving skill subdirectories via
  `removeprefix(".claude/skills/")` is the right direction:
  `bridge/gtkb-skill-decision-capture-005.md:266-274`.

## Review Target Responses

1. **Title parameter design:** GO. Keeping `title` explicit is acceptable.
   It maps cleanly to the current `insert_deliberation()` signature and lets
   list-view and detail-summary text diverge when useful.
2. **`changed_by` literal:** GO. Keep
   `"prime-builder/decision-capture-skill"` because it preserves both actor
   and tool attribution.
3. **`DeliberationInsertFailed` placement:** GO. Module-local is appropriate
   for this template helper; no public API expansion is needed.
4. **Minimal `SKILL.md` content:** GO for Phase A. A frontmatter plus
   three-section outline is enough for this infrastructure bridge, provided
   the helper contract and tests carry the safety guarantees.

## Verification Performed

Target repo evidence checks:

```text
git rev-parse --short HEAD
862045d

python -c "from inspect import signature; from groundtruth_kb.db import KnowledgeDB; from groundtruth_kb.project.upgrade import plan_upgrade, execute_upgrade; from groundtruth_kb.project.doctor import ToolCheck; print(signature(KnowledgeDB.insert_deliberation)); print(signature(plan_upgrade)); print(signature(execute_upgrade)); print(signature(ToolCheck)); print(ToolCheck('skill:decision-capture', False, False, 'warning', 'missing'))"
```

Targeted tests:

```text
python -m pytest tests/test_upgrade.py -q --tb=short
10 passed, 1 warning in 0.19s

python -m pytest tests/test_deliberations.py -q --tb=short
70 passed, 1 warning in 27.92s

python -m pytest tests/test_doctor.py -q --tb=short
29 passed, 1 warning in 1.25s
```

## Decision Needed From Owner

None. Prime should post `gtkb-skill-decision-capture-007.md` as `REVISED`
with only the doctor `ToolCheck` construction contract corrected.
