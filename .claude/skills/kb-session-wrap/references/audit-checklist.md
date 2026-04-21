# Audit Session Checklist

Every 5th session is an **audit session** (S185, S190, S195, ...). Add these extra steps to the standard wrap-up.

## 1. Stale Work Item Review

Close any WIs open > 3 sessions without progress:

```python
open_wis = db.get_open_work_items()
for wi in open_wis:
    created = wi.get('created_at', '')
    print(f"  {wi['id']}: {wi['title']} (created: {created})")
```

## 2. Assertion Coverage

Check `assertion_coverage` metric from quality dashboard:

```python
summary = db.get_summary()
coverage = summary.get('assertions_total', 0)
passed = summary.get('assertions_passed', 0)
print(f"Assertion coverage: {passed}/{coverage}")
```

## 3. Spec Drift Detection

Flag any implemented specs without tests:

```python
untested = db.get_untested_specs()
for s in untested:
    if s['status'] == 'implemented':
        print(f"  DRIFT: {s['id']} implemented but no tests")
```

## 4. Procedure Freshness

Flag procedures not verified in > 10 sessions:

```python
procedures = db.list_op_procedures()
for p in procedures:
    print(f"  {p['id']}: {p['title']} [verified: {p.get('last_verified_at', 'never')}]")
```

## 5. MEMORY.md Size Management

Ensure Recent Sessions doesn't exceed ~20 entries. Archive older ones to CLAUDE_ARCHIVE.md.
