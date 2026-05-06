NEW

# Implementation Report - GTKB-AUQ-POLICY-GATES-001

**Author:** Prime Builder (Codex, harness A)
**Date:** 2026-05-06
**Type:** Post-implementation report
**Backlog item:** `GTKB-AUQ-POLICY-GATES-001`
**Proposal authority:** `bridge/gtkb-auq-policy-gates-001-003.md`
**Review authority:** `bridge/gtkb-auq-policy-gates-001-004.md` (`GO`)

---

## Claim

The narrowed first AUQ policy-gate slice is implemented. It adds a central
deterministic policy registry, policy engine, CLI dry-run/check surface,
approval-receipt validation primitives, and tests. It does not install commit,
push, platform-write, or hook adapters.

## Implemented Changes

- Added root-contained registry `config/agent-control/auq-policy-gates.toml`.
- Added `groundtruth_kb.policy` with registry parsing, deterministic decisions,
  path/scope checks, and approval-receipt validation.
- Added `gt policy check --action <action> --scope <scope> --paths <path> --json`.
- Implemented outcomes `ALLOW`, `WARN`, `ASK`, and `DENY`.
- Implemented receipt validation for action mismatch, scope mismatch, path
  mismatch, registry-hash mismatch, missing expiry, and expired receipts.
- Modeled candidate `commit`, `push`, and `platform-write` action classes as
  inert registry data with `adapter_installed = false`.

## Files Changed

- `config/agent-control/auq-policy-gates.toml`
- `groundtruth-kb/src/groundtruth_kb/policy/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/policy/engine.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/tests/test_policy_gates.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this report is filed under the active bridge
  lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation
  follows the approved proposal and linked requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification below maps
  tests to requirements.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - registry entries and receipts are
  durable, inspectable artifacts with explicit states.
- `GOV-REQUIREMENTS-COLLECTION-HOOK-001` and
  `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` - requirements/spec mutation
  actions return bounded `ASK` options.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - classification is
  deterministic code, not repeated agent judgment.
- `DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION` -
  `ASK` outcomes provide two to three bounded options.
- `.claude/rules/project-root-boundary.md` and
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - archive paths and
  application/platform path mismatches are blocked.

## Spec-To-Test Map

| Requirement | Evidence |
|---|---|
| Registry parses deterministically and rejects bad outcomes | `tests/test_policy_gates.py::test_policy_registry_parses_candidate_actions`; `test_invalid_registry_outcome_rejected` |
| Engine has no LLM/API dependency | `tests/test_policy_gates.py::test_policy_engine_has_no_llm_or_network_dependency` |
| `ALLOW`, `WARN`, `ASK`, and `DENY` behavior | `tests/test_policy_gates.py::test_policy_outcomes_cover_allow_warn_ask_and_deny` |
| ASK options are bounded to two to three choices | `test_policy_outcomes_cover_allow_warn_ask_and_deny` |
| Requirements/spec mutation asks without receipt | `test_policy_outcomes_cover_allow_warn_ask_and_deny` |
| Valid receipts allow the scoped ASK action | `tests/test_policy_gates.py::test_valid_receipt_turns_ask_into_allow` |
| Receipt mismatch/expiry validation | `tests/test_policy_gates.py::test_receipt_validation_rejects_mismatches_and_expiry` |
| Platform path in application scope is denied | `tests/test_policy_gates.py::test_application_scope_platform_path_is_denied` |
| Archive paths are denied | `tests/test_policy_gates.py::test_archive_path_is_denied` |
| CLI JSON and exit behavior | `tests/test_policy_gates.py::test_policy_cli_json_exit_behavior` |
| No commit/push/platform-write adapters installed | `test_policy_registry_parses_candidate_actions` asserts `adapter_installed = false` for all three |

## Verification

```powershell
cd E:\GT-KB\groundtruth-kb
python -m pytest tests/test_policy_gates.py tests/test_cli.py -q --tb=short
# 44 passed, 1 warning

python -m ruff check src/groundtruth_kb/policy src/groundtruth_kb/cli.py tests/test_policy_gates.py
# All checks passed.

python -m ruff format --check src/groundtruth_kb/policy src/groundtruth_kb/cli.py tests/test_policy_gates.py
# 4 files already formatted
```

The warning is the existing upstream ChromaDB deprecation warning imported by
the broad CLI regression lane.

## Applicability Preflight

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-auq-policy-gates-001
```

- operative_file: `bridge/gtkb-auq-policy-gates-001-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Risk / Impact

- No hook registrations were added.
- No commit, push, or platform-write behavior changes were installed.
- Candidate entries for commit, push, and platform-write are policy data only.
- CLI `ASK` exits with code 2; `DENY` exits with code 3; `ALLOW` and `WARN`
  exit with code 0.
- Registry loading searches for the root-contained TOML from the current working
  directory and its parents; explicit `--registry` can override it for tests or
  future packaging work.

## Recommended Action

Loyal Opposition should verify the central engine, registry, CLI, receipt
validation, no-LLM/no-adapter claims, and mapped tests.

## Decision Needed From Owner

None.
