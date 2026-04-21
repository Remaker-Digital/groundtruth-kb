# Promote Specification: Validation Rules

## Status Lifecycle

```
specified  -->  implemented  -->  verified
    |              |              |
  retired        retired        retired
```

- **specified -> implemented:** Code exists that satisfies the spec.
- **implemented -> verified:** Tests pass AND assertions pass against live system.
- **any -> retired:** Spec is no longer relevant (owner approval required -- GOV-02).

## Validation: specified -> implemented

1. **Code exists:** Search the codebase for implementation evidence.
   ```python
   for a in assertions:
       if a.get('type') == 'grep':
           # Run grep against target file -- must return >= min_count
           pass
   ```

2. **Assertions pass:** Run all machine-verifiable assertions.
   - `type: grep` -- `grep -c "<pattern>" "<target>"` must return >= min_count
   - `type: exists` -- `test -f "<target>"` must succeed

3. **No blocking work items:**
   ```python
   open_wis = [w for w in db.list_work_items(resolution_status="open")
               if w.get('source_spec_id') == spec_id]
   ```

## Validation: implemented -> verified

All requirements from `specified -> implemented` PLUS:

1. **Tests exist:** At least one test linked to this spec (GOV-12).
   ```python
   tests = db.get_tests_for_spec(spec_id)
   # Must have len(tests) >= 1
   ```

2. **Tests pass:** All linked tests must have `last_result = 'pass'`.
   ```python
   failing = [t for t in tests if t.get('last_result') != 'pass']
   # Must have len(failing) == 0
   ```

3. **Live verification:** At least one test exercised production interfaces (GOV-10).

## Validation: any -> retired

- **GOV-02:** Owner approval is REQUIRED. Do not retire without explicit approval.
- Record the reason for retirement in `change_reason`.

## Promotion Blocked Template

```
PROMOTION BLOCKED
  Spec: SPEC-XXXX
  Current: specified -> Target: implemented
  Blockers:
    - 2/3 assertions FAIL
    - 1 open work item (WI-XXXX)
  Action: Fix blockers, then retry
```

Do NOT promote. Instead, create work items for each blocker using `/kb-work-item`.
