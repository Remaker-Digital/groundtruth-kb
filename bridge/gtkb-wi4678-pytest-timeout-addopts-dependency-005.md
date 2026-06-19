REVISED

# WI-4678 Pytest Timeout Addopts Dependency - revised post-implementation report

bridge_kind: implementation_report
Document: gtkb-wi4678-pytest-timeout-addopts-dependency
Version: 005 (REVISED; post-implementation report after NO-GO)
Responds to NO-GO: bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-004.md
Responds to GO: bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-002.md
Approved proposal: bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-001.md
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019edf53-e293-7301-9ff4-804d66e54b90
author_model: GPT-5
author_model_version: 2026-06-19 Codex desktop
author_model_configuration: Codex Desktop automation run; autonomous Prime Builder loop; approval_policy=never; sandbox=danger-full-access; network=enabled
Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4678
target_paths: ["pyproject.toml", "groundtruth-kb/pyproject.toml", "groundtruth-kb/uv.lock", "platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py"]
Recommended commit type: fix:

## Implementation Claim

The WI-4678 implementation is complete. The previous blocked implementation
report at `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-003.md`
correctly identified the missing managed dependency, but the auto-dispatched
sandbox could not run the managed dependency toolchain. This run completed the
same approved scope from a network/cache-capable Prime Builder context.

Changes made:

- Added `pytest-timeout>=2.3` to the GroundTruth-KB `dev` optional dependency
  group in `groundtruth-kb/pyproject.toml`.
- Ran the managed `uv add --optional dev "pytest-timeout>=2.3"` toolchain from
  `groundtruth-kb/`, using a workspace-local `UV_CACHE_DIR`, which updated
  `groundtruth-kb/uv.lock` and installed `pytest-timeout==2.4.0` into the
  GroundTruth-KB venv.
- Added `platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py`, a
  structural regression test that ties the root `--timeout=30` addopt to the
  managed dev dependency declaration, the lockfile package entry, and runtime
  importability of `pytest_timeout`.
- Left the root `pyproject.toml` timeout policy unchanged.
- Introduced no `-o addopts=""` workaround in committed files.

## Findings Addressed

### Finding 1 - managed dependency toolchain blocked in auto-dispatch workspace sandbox

Addressed. This run used the live Prime Builder workspace with network access
and a workspace-local uv cache at `.gtkb-tmp/uv-cache-wi4678`. The managed
toolchain invocation succeeded, generated the lockfile delta, and installed the
plugin into `groundtruth-kb/.venv`. The required collect-only command now
collects and shows the active `timeout-2.4.0` pytest plugin instead of failing
on an unrecognized `--timeout=30` option.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required. Implementation remains within the active
project authorization
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`, backed by
`DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`.

## Prior Deliberations

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` - owner authorization
  for implementing unimplemented May29 Hygiene work items through the normal
  bridge/GO process.
- `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-001.md` - approved
  implementation proposal.
- `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-002.md` - Loyal
  Opposition GO verdict authorizing implementation.
- `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-003.md` - prior blocked
  implementation report.
- `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-004.md` - Loyal
  Opposition NO-GO requiring the dependency, lockfile, venv install, and
  structural regression test to be completed.
- `bridge/gtkb-wi4672-bridge-compliance-gate-template-parity-003.md` - prior
  implementation evidence of the `--timeout=30` rejection.
- `bridge/gtkb-wi4677-backlog-json-option-validation-003.md` - prior
  implementation evidence of the same missing timeout plugin condition.

## Pre-Filing Preflight Subsection

The following candidate-content preflights were run against
`.gtkb-state/bridge-revisions/drafts/gtkb-wi4678-pytest-timeout-addopts-dependency-005.md`
before live filing:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4678-pytest-timeout-addopts-dependency --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4678-pytest-timeout-addopts-dependency-005.md --json` - PASS; `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4678-pytest-timeout-addopts-dependency --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4678-pytest-timeout-addopts-dependency-005.md` - PASS; 5 clauses evaluated, 4 must-apply clauses, 0 blocking gaps.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Acquired work-intent claim for `gtkb-wi4678-pytest-timeout-addopts-dependency`; `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4678-pytest-timeout-addopts-dependency` passed and produced packet `sha256:57e18d2417a4ffe913506f2c5fd28e69e6c1855061c53e6a92dbb3e824ff7b20`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python -m groundtruth_kb backlog show WI-4678 --json` showed `resolution_status: open`, `stage: backlogged`, and project `PROJECT-GTKB-MAY29-HYGIENE`; the implementation packet confirmed the active May29 PAUTH. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate applicability preflight passed with no missing required or advisory specs. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report carries `Project Authorization`, `Project`, `Work Item`, and machine-readable `target_paths` metadata. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py -q --tb=short --no-header` passed 1 test; `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py --collect-only -q` collected 15 tests and showed plugin `timeout-2.4.0` active. |
| `GOV-STANDING-BACKLOG-001` | `WI-4678` remains linked to `PROJECT-GTKB-MAY29-HYGIENE` for bridge verification and later backlog resolution. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | The root timeout policy and Agent Red ignore were not changed; the collect-only verification ran from the GT-KB root and retained the root pytest config. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The recurring workaround is resolved through a governed dependency/test artifact and bridge report. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The dependency contract is now durable in `pyproject.toml`, `uv.lock`, and a structural regression test. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This REVISED report moves the NO-GO lifecycle forward with concrete implementation and verification evidence. |

## Commands Run

- `$env:UV_CACHE_DIR='E:\GT-KB\.gtkb-tmp\uv-cache-wi4678'; uv add --optional dev "pytest-timeout>=2.3"` from `groundtruth-kb/` - PASS; resolved packages, updated lockfile, installed `pytest-timeout==2.4.0`.
- `groundtruth-kb/.venv/Scripts/python.exe -c "import importlib.util; print(importlib.util.find_spec('pytest_timeout'))"` - PASS; returned a module spec from `groundtruth-kb/.venv/Lib/site-packages/pytest_timeout.py`.
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py -q --tb=short --no-header` - PASS; 1 passed, 1 warning.
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py --collect-only -q` - PASS; 15 tests collected, plugin `timeout-2.4.0` active, 1 warning.
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py` - PASS.
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py` - PASS.
- `git diff --check -- groundtruth-kb/pyproject.toml groundtruth-kb/uv.lock platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py` - PASS.

## Observed Results

The defect is fixed. The GroundTruth-KB venv now recognizes the root
`--timeout=30` addopt because `pytest-timeout` is installed and declared in the
managed dev dependency surface. The previously blocked collect-only command
now prints:

```text
plugins: anyio-4.13.0, cov-7.1.0, timeout-2.4.0
timeout: 30.0s
collected 15 items
```

Both pytest commands emitted the pre-existing warning:
`PytestConfigWarning: Unknown config option: asyncio_mode`. That warning is
outside WI-4678 scope and does not block the timeout-addopts fix.

## Files Changed

- `groundtruth-kb/pyproject.toml`
- `groundtruth-kb/uv.lock`
- `platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py`
- `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-005.md`

No committed source file clears pytest addopts with `-o addopts=""`.

## Recommended Commit Type

- Recommended commit type: `fix:`

## Acceptance Criteria Status

- [x] `pytest-timeout` added to the GroundTruth-KB dev extra in `groundtruth-kb/pyproject.toml`.
- [x] `groundtruth-kb/uv.lock` updated by the managed `uv` toolchain.
- [x] `pytest-timeout` installed in the GroundTruth-KB virtual environment.
- [x] Structural regression test added at `platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py`.
- [x] Focused pytest command passes without `-o addopts=""`.
- [x] Previously blocked collect-only command accepts `--timeout=30` and collects tests without `-o addopts=""`.
- [x] No workaround clearing addopts was introduced.

## Risk And Rollback

Risk is limited to the dev/test dependency surface. The package is declared only
in the GroundTruth-KB `dev` optional dependency group and does not alter runtime
dependencies or the root timeout policy. Rollback is to revert the implementation
commit, restoring `groundtruth-kb/pyproject.toml`, `groundtruth-kb/uv.lock`, and
`platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py`; bridge files
remain append-only audit evidence.

## Loyal Opposition Asks

1. Verify that the implementation satisfies the WI-4678 GO and closes the
   NO-GO in `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-004.md`.
2. Return `VERIFIED` if the dependency, lockfile, venv install, and regression
   test evidence satisfy the approved proposal.
