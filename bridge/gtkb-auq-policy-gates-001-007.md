NEW

# Post-NO-GO Fix Report - GTKB-AUQ-POLICY-GATES-001

Reported by: Prime Builder (Codex, harness A)
Date: 2026-05-06
Authority: latest Loyal Opposition NO-GO at
`bridge/gtkb-auq-policy-gates-001-006.md`
Requested bridge disposition: `VERIFIED`

## Claim

The AUQ policy-gates NO-GO finding is addressed. The policy engine now passes
the repository's strict full-tree mypy gate and the AUQ slice's targeted policy
verification still passes.

Fix applied:

- `groundtruth-kb/src/groundtruth_kb/policy/engine.py`: `load_receipt()` casts
  the parsed JSON value to `dict[str, Any]` before returning it.

No hook adapter, commit adapter, push adapter, platform-write adapter, GitHub
setting, branch protection rule, credential action, release action, or external
repository mutation was performed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this follow-up report is filed in
  `bridge/` and registered in `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report
  carries forward the approved implementation packet and the cited NO-GO
  finding.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the corrected evidence
  includes the exact full-tree strict type gate that blocked verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the policy registry, receipts, and
  NO-GO disposition remain durable governed artifacts.
- `.claude/rules/project-root-boundary.md` and
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the fix is inside the GT-KB
  platform package and does not touch Agent Red application work.

## NO-GO Finding Disposition

### F1 - The policy engine fails the full-tree strict mypy gate

Status: fixed.

Loyal Opposition failure:

```text
src/groundtruth_kb/policy/engine.py:256: error: Returning Any from function
declared to return "dict[str, Any] | None" [no-any-return]
```

Prime correction:

```python
return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))
```

The correction preserves the existing receipt-loading behavior while satisfying
the function's declared type contract.

## Specification-Derived Verification

| Test ID | Spec coverage | Procedure | Result |
|---|---|---|---|
| T-policy-1 | AUQ policy registry, engine, CLI, and receipt behavior | `python -m pytest tests/test_policy_gates.py tests/test_cli.py -q --tb=short` from `groundtruth-kb` | PASS - 44 passed, 1 warning |
| T-mypy-1 | NO-GO F1 / full-tree strict type gate | `python -m pytest tests/test_full_tree_type_checks.py::test_full_tree_mypy_strict_is_clean -q --tb=short` from `groundtruth-kb` | PASS - 1 passed, 1 warning |
| T-lint-1 | Changed policy and CLI surfaces | `python -m ruff check src/groundtruth_kb/policy src/groundtruth_kb/cli.py tests/test_policy_gates.py` from `groundtruth-kb` | PASS |
| T-format-1 | Changed policy and CLI formatting | `python -m ruff format --check src/groundtruth_kb/policy src/groundtruth_kb/cli.py tests/test_policy_gates.py` from `groundtruth-kb` | PASS - 4 files already formatted |

The warning is the existing upstream ChromaDB deprecation warning seen in the
broad CLI and type-check lanes.

## Acceptance Criteria

- Central deterministic AUQ policy registry/engine remains implemented.
- `gt policy check` targeted behavior remains green.
- Receipt validation remains green.
- Commit, push, platform-write, and hook adapters remain uninstalled in this
  first slice.
- Full-tree strict mypy gate is green for the policy engine.

## Changed Files

- `groundtruth-kb/src/groundtruth_kb/policy/engine.py`
- `bridge/gtkb-auq-policy-gates-001-007.md`
- `bridge/INDEX.md`

## Decision Needed From Owner

None.

