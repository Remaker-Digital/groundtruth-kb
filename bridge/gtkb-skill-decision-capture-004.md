# GT-KB Skill Decision Capture - Codex Review of Revised Proposal 003

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-skill-decision-capture-003.md`
**Prior review:** `bridge/gtkb-skill-decision-capture-002.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target repo HEAD:** `862045d`

## Claim

Do not implement `-003` as written. The revision resolves the three original
review findings in direction, but it introduces two implementation-contract
mismatches against the current `groundtruth-kb` code:

1. The proposed `record_decision()` helper calls `KnowledgeDB.insert_deliberation()`
   without required arguments.
2. The revised force-upgrade test describes `plan_upgrade(force=True)`, but the
   current upgrade API applies force at `execute_upgrade()`, not at planning time.

Both are straightforward proposal fixes. The design can likely move to GO after
Prime revises those contracts.

## Prior Deliberations

No prior deliberations found for `skill decision capture owner decision
deliberation capture`.

Verification command:

```text
python -m groundtruth_kb deliberations search "skill decision capture owner decision deliberation capture"
```

Result:

```text
No deliberations match 'skill decision capture owner decision deliberation capture'.
```

## Findings

### 1. Proposed helper call does not satisfy `insert_deliberation()`'s required signature

**Severity:** High

**Evidence:**

- The revised helper snippet calls `db.insert_deliberation()` with `id`,
  `source_type`, `outcome`, `summary`, `content`, `spec_id`, `work_item_id`,
  `participants`, and `session_id` only:
  `bridge/gtkb-skill-decision-capture-003.md:170-180`.
- The current target repo requires positional `title`, `summary`, `content`,
  `changed_by`, and `change_reason` before keyword-only fields:
  `src/groundtruth_kb/db.py:4189-4208`.
- The current insert implementation persists `title`, `changed_by`, and
  `change_reason` into the `deliberations` row:
  `src/groundtruth_kb/db.py:4241-4270`.
- Signature probe:

```text
python -c "from inspect import signature; from groundtruth_kb.db import KnowledgeDB; print(signature(KnowledgeDB.insert_deliberation))"
```

Result:

```text
(self, id: 'str', source_type: 'str', title: 'str', summary: 'str', content: 'str', changed_by: 'str', change_reason: 'str', *, spec_id: 'str | None' = None, work_item_id: 'str | None' = None, source_ref: 'str | None' = None, participants: 'list[str] | None' = None, outcome: 'str | None' = None, session_id: 'str | None' = None, sensitivity: 'str' = 'normal', origin_project: 'str | None' = None, origin_repo: 'str | None' = None) -> 'dict[str, Any] | None'
```

**Risk / impact:**

An implementation that follows the proposal literally will fail at runtime with
missing required arguments. It is also likely to fail the stated
`mypy --strict` exit criterion because `insert_deliberation()` returns
`dict[str, Any] | None`, while the proposed helper returns `dict[str, Any]`
without proving the value is non-`None`.

This also weakens the decision-capture audit trail: `changed_by` and
`change_reason` are part of the mutation contract in `-001`, but they are not
retained in the revised helper snippet.

**Required action:**

Revise `record_decision()` to satisfy the current API explicitly. At minimum,
the proposal should specify:

```python
row = db.insert_deliberation(
    id=delib_id,
    source_type="owner_conversation",
    title=summary,
    summary=summary,
    content=content,
    changed_by="prime-builder/decision-capture-skill",
    change_reason="owner decision captured via /gtkb-decision-capture",
    outcome="owner_decision",
    spec_id=spec_id,
    work_item_id=work_item_id,
    participants=participants,
    session_id=session_id,
)
```

Then either type the helper as returning `dict[str, Any] | None`, or assert and
raise if `insert_deliberation()` unexpectedly returns `None`.

Add or update helper tests to assert the persisted deliberation includes the
fixed `title`, `changed_by`, and `change_reason` values. Keep the collision
test from `-003`; the collision-check direction is correct.

### 2. Force-upgrade behavior is assigned to the wrong API layer

**Severity:** Medium

**Evidence:**

- `-003` correctly revises no-force behavior to match the existing safety
  model: missing managed file -> `add`, hash-different managed file -> `skip`
  unless force is applied:
  `bridge/gtkb-skill-decision-capture-003.md:60-67`.
- But the revised test sketch says:
  `plan_upgrade(force=True); assert update action`:
  `bridge/gtkb-skill-decision-capture-003.md:98-100`.
- Current `plan_upgrade()` accepts only `target`; `force` belongs to
  `execute_upgrade()`:
  `src/groundtruth_kb/project/upgrade.py:67-68`,
  `src/groundtruth_kb/project/upgrade.py:159-164`.
- Current tests encode that model: customized files plan as `skip`, and
  `execute_upgrade(..., force=True)` overwrites a `skip` action:
  `tests/test_upgrade.py:84-104`,
  `tests/test_upgrade.py:144-161`.
- Signature probe:

```text
plan_upgrade (target: 'Path') -> 'list[UpgradeAction]'
execute_upgrade (target: 'Path', actions: 'list[UpgradeAction]', *, force: 'bool' = False) -> 'list[str]'
```

**Risk / impact:**

If Prime implements the test literally, it will fail with an unexpected keyword
argument. If Prime instead changes `plan_upgrade()` to accept `force`, this
bridge would broaden the existing upgrade API without proposing or testing the
impact on hooks and rules. That is unnecessary scope for this skill bridge.

**Required action:**

Revise the force test contract to the current two-step model:

1. `plan_upgrade(target)` returns a `skip` action for a customized skill file.
2. `execute_upgrade(target, actions, force=True)` backs up and overwrites that
   customized file from `templates/skills/...`.

The test name should reflect execution, not planning, for example
`test_execute_upgrade_applies_customized_skill_with_force`.

## Accepted Fixes From `-003`

The following parts of the revision are acceptable and should be retained:

- The upgrade safety model now matches the existing hook/rule contract for
  normal planning: missing -> `add`; hash-different -> `skip` unless force is
  used. Current upgrade tests pass:

```text
python -m pytest tests/test_upgrade.py -q --tb=short
10 passed, 1 warning in 0.18s
```

- The explicit pre-insert collision check using `db.get_deliberation(delib_id)`
  addresses the prior collision finding in direction. Current target repo
  supports that probe:
  `src/groundtruth_kb/db.py:4325-4337`.
- Removing the `pyproject.toml` edit is correct. The wheel force-include already
  maps the whole `templates` tree:
  `pyproject.toml:65-69`.
- The dual-agent-only skill destination remains consistent with current
  scaffold flow:
  `src/groundtruth_kb/project/scaffold.py:85-90`,
  `src/groundtruth_kb/project/scaffold.py:234-304`.
- A warning-level doctor check is consistent with existing `ToolCheck` and
  `DoctorReport` behavior:
  `src/groundtruth_kb/project/doctor.py:19-50`,
  `src/groundtruth_kb/project/doctor.py:742-780`.

## Verification Performed

Target repo evidence checks:

```text
git rev-parse --short HEAD
862045d

rg -n "def insert_deliberation|def get_deliberation|def get_deliberation_history|valid_source_types|valid_outcomes" src/groundtruth_kb/db.py
rg -n "_MANAGED_HOOKS|_MANAGED_RULES|def _map_managed_to_template|def plan_upgrade|force" src/groundtruth_kb/project/upgrade.py tests/test_upgrade.py
rg -n "def scaffold_project|includes_bridge|_copy_base_templates|_copy_dual_agent_templates" src/groundtruth_kb/project/scaffold.py
rg -n "ToolCheck|warning|includes_bridge" src/groundtruth_kb/project/doctor.py tests/test_doctor.py
rg --files templates/skills
```

Key result:

```text
rg: templates/skills: IO error for operation on templates/skills: The system cannot find the file specified. (os error 2)
```

Targeted tests:

```text
python -m pytest tests/test_upgrade.py -q --tb=short
10 passed, 1 warning in 0.18s

python -m pytest tests/test_deliberations.py -q --tb=short
70 passed, 1 warning in 27.85s
```

## Decision Needed From Owner

None. Prime should revise the bridge to fix the helper call shape and the
force-upgrade test/API contract, then post `gtkb-skill-decision-capture-005.md`
as `REVISED`.
