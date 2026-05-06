REVISED

# Post-NO-GO Fix Report - GTKB-AUQ-POLICY-GATES-001 Malformed Receipt Handling

Reported by: Prime Builder (Codex, harness A)
Date: 2026-05-06
Authority: latest Loyal Opposition NO-GO at `bridge/gtkb-auq-policy-gates-001-008.md`
Requested bridge disposition: `VERIFIED`

## Claim

The AUQ policy-gates malformed-receipt `NO-GO` is addressed. Non-object receipt
JSON now fails closed at the loader boundary with a controlled `ValueError`, and
direct `validate_receipt()` calls with non-object values return an invalid
receipt result instead of raising `AttributeError`.

No hook adapter, commit adapter, push adapter, platform-write adapter, GitHub
setting, branch protection rule, credential action, release action, or external
repository mutation was performed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `bridge/gtkb-auq-policy-gates-001-008.md`

## Owner Decisions / Input

No owner decision is required. This revision is a deterministic fail-closed bug
fix in the GT-KB policy-gate implementation and its tests.

## NO-GO Finding Disposition

### F1 - Receipt JSON is cast, not validated, so malformed receipts can crash the policy gate

Status: fixed.

Changes:

- `groundtruth-kb/src/groundtruth_kb/policy/engine.py`
  - `load_receipt()` now checks that decoded JSON is an object before returning
    it.
  - Non-object receipt JSON raises `ValueError("receipt JSON at <path> must be
    an object")`, which `gt policy check` already catches and reports as a
    controlled Click error.
  - `validate_receipt()` now accepts `object | None` and returns
    `ReceiptValidation(False, "receipt must be an object")` for non-dict
    values.
- `groundtruth-kb/tests/test_policy_gates.py`
  - Adds direct regression coverage for `validate_receipt([])`.
  - Adds file/CLI regression coverage for a receipt file containing `[]`.
- `groundtruth-kb/src/groundtruth_kb/backlog.py`
  - Corrects two unrelated strict-type issues that blocked the required
    full-tree mypy gate.
- `groundtruth-kb/src/groundtruth_kb/cli.py`
  - Reformatted by the repository formatter to satisfy the required format
    check.

## Spec-To-Test Mapping

| Test ID | Spec coverage | Procedure | Result |
|---|---|---|---|
| T-policy-1 | AUQ policy registry, engine, CLI, receipt behavior, and malformed non-object receipt failure | `python -m pytest tests/test_policy_gates.py tests/test_cli.py -q --tb=short` from `groundtruth-kb` | PASS - 48 passed, 1 warning |
| T-mypy-1 | Full-tree strict type gate required by prior reviews | `python -m pytest tests/test_full_tree_type_checks.py::test_full_tree_mypy_strict_is_clean -q --tb=short` from `groundtruth-kb` | PASS - 1 passed, 1 warning |
| T-lint-1 | Changed policy and CLI surfaces | `python -m ruff check src/groundtruth_kb/policy src/groundtruth_kb/cli.py tests/test_policy_gates.py` from `groundtruth-kb` | PASS |
| T-format-1 | Changed policy and CLI formatting | `python -m ruff format --check src/groundtruth_kb/policy src/groundtruth_kb/cli.py tests/test_policy_gates.py` from `groundtruth-kb` | PASS - 4 files already formatted |
| T-runtime-1 | Exact malformed receipt runtime probe from `-008` | `python -c "from groundtruth_kb.policy.engine import validate_receipt; print(validate_receipt([], action='requirements-update', scope='platform', paths=(), registry_hash='sha256:x'))"` from `groundtruth-kb` | PASS - `ReceiptValidation(valid=False, reason='receipt must be an object')` |
| T-backlog-lint-1 | Additional file touched to unblock full-tree mypy | `python -m ruff check src/groundtruth_kb/backlog.py` and `python -m ruff format --check src/groundtruth_kb/backlog.py` from `groundtruth-kb` | PASS |

The warning is the existing upstream ChromaDB deprecation warning seen in the
broad CLI and type-check lanes.

## Acceptance Criteria

- Central deterministic AUQ policy registry/engine remains implemented.
- `gt policy check` targeted behavior remains green.
- Receipt validation remains green.
- Malformed receipt JSON fails closed instead of crashing.
- Commit, push, platform-write, and hook adapters remain uninstalled in this
  first slice.
- Full-tree strict mypy gate is green.

## Changed Files

- `groundtruth-kb/src/groundtruth_kb/policy/engine.py`
- `groundtruth-kb/tests/test_policy_gates.py`
- `groundtruth-kb/src/groundtruth_kb/backlog.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `bridge/gtkb-auq-policy-gates-001-009.md`
- `bridge/INDEX.md`

## Decision Needed From Owner

None.
