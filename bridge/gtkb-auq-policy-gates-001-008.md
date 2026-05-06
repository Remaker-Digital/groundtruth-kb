NO-GO

# Loyal Opposition Verification - GTKB-AUQ-POLICY-GATES-001 Post-NO-GO Fix

Reviewed: 2026-05-06
Subject: `bridge/gtkb-auq-policy-gates-001-007.md`
Prior response: `bridge/gtkb-auq-policy-gates-001-006.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

I reviewed the post-NO-GO fix report, reran the targeted tests, reran the full-tree strict type-check gate that previously blocked verification, inspected the receipt-loading implementation, and probed malformed receipt behavior.

## Verification Executed

- `python -m pytest tests/test_policy_gates.py tests/test_cli.py -q --tb=short` from `groundtruth-kb` -> PASS, `44 passed, 1 warning`.
- `python -m pytest tests/test_full_tree_type_checks.py::test_full_tree_mypy_strict_is_clean -q --tb=short` from `groundtruth-kb` -> PASS, `1 passed, 1 warning`.
- `python -m ruff check src/groundtruth_kb/policy src/groundtruth_kb/cli.py tests/test_policy_gates.py` from `groundtruth-kb` -> PASS.
- `python -m ruff format --check src/groundtruth_kb/policy src/groundtruth_kb/cli.py tests/test_policy_gates.py` from `groundtruth-kb` -> PASS, `4 files already formatted`.
- `python -c "from groundtruth_kb.policy.engine import validate_receipt; print(validate_receipt([], action='requirements-update', scope='platform', paths=(), registry_hash='sha256:x'))"` from `groundtruth-kb` -> FAIL with `AttributeError: 'list' object has no attribute 'get'`.

## Applicability Preflight

- packet_hash: `sha256:d720c0340381f2dc16811064ba52dc7616f3bf87b892fb691a216e559f127e5b`
- bridge_document_name: `gtkb-auq-policy-gates-001`
- operative_file: `bridge/gtkb-auq-policy-gates-001-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Finding

### F1 - Receipt JSON is cast, not validated, so malformed receipts can crash the policy gate

Severity: P1

Evidence:

- `bridge/gtkb-auq-policy-gates-001-006.md` required `load_receipt()` to validate/cast the parsed JSON before returning.
- The follow-up report says the fix is `return cast(dict[str, Any], json.loads(...))`.
- The live implementation at `groundtruth-kb/src/groundtruth_kb/policy/engine.py:252` to `:256` still returns the parsed JSON through `cast(dict[str, Any], ...)` without checking that the parsed value is actually a dictionary.
- `validate_receipt()` immediately calls `receipt.get(...)` at `groundtruth-kb/src/groundtruth_kb/policy/engine.py:161`. A list or other non-dict value therefore raises instead of producing an invalid receipt result.
- Direct runtime probe with `validate_receipt([])` reproduces `AttributeError: 'list' object has no attribute 'get'`.

Risk / impact:

The type gate is now green, but the policy gate still accepts malformed receipt data at the loader boundary and can crash instead of denying or rejecting the receipt. This is a governance/action-authorization surface; malformed approval evidence must fail closed with a deterministic invalid-receipt result or a user-facing CLI error, not an unhandled exception.

Required action:

Make `load_receipt()` validate that decoded JSON is an object before returning it. Acceptable fixes include returning `None` for non-object receipts plus a deterministic invalid-receipt reason, or raising `ValueError` that the CLI catches and reports as a controlled error. Add a regression test for a JSON receipt file containing a non-object value such as `[]`, then rerun:

```text
python -m pytest tests/test_policy_gates.py tests/test_cli.py -q --tb=short
python -m pytest tests/test_full_tree_type_checks.py::test_full_tree_mypy_strict_is_clean -q --tb=short
python -m ruff check src/groundtruth_kb/policy src/groundtruth_kb/cli.py tests/test_policy_gates.py
python -m ruff format --check src/groundtruth_kb/policy src/groundtruth_kb/cli.py tests/test_policy_gates.py
```

## Verdict

NO-GO. The previous mypy blocker is fixed, but verification remains blocked until malformed receipt JSON fails closed instead of crashing the policy gate.

File bridge scan: 1 entry processed.

