NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never
author_metadata_source: Codex Prime Builder session; .gtkb-state/bridge-author-metadata/current.json

bridge_kind: implementation_report
Document: gtkb-wi-4477-ollama-readiness-autostart
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-06-13 UTC
Responds-To: bridge/gtkb-wi-4477-ollama-readiness-autostart-002.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4477
Recommended commit type: feat

target_paths: ["scripts/verify_ollama_dispatch.py", "scripts/ops/install_ollama_autostart_task.ps1", "platform_tests/scripts/test_ollama_dispatch.py", "platform_tests/scripts/test_verify_ollama_dispatch.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_ollama.py"]

# Implementation Report - WI-4477 Ollama Readiness Autostart

## Implementation Claim

Implemented the approved bounded Ollama readiness/autostart visibility slice.
The dispatch-readiness helper now emits structured autostart warning evidence
without treating missing autostart as a hard readiness failure when the daemon
and configured model are currently reachable. The `gt project doctor` Ollama
check now warns when `/api/tags` is unreachable and when no Windows scheduled
task or service matching Ollama is detected. A guarded operator script was
added for registering a user-logon scheduled task that runs `ollama serve`;
the script was not executed.

## Files Changed

- `scripts/verify_ollama_dispatch.py`
- `scripts/ops/install_ollama_autostart_task.ps1`
- `platform_tests/scripts/test_ollama_dispatch.py`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/tests/test_doctor_ollama.py`
- `bridge/INDEX.md`
- `bridge/gtkb-wi-4477-ollama-readiness-autostart-001.md`
- `bridge/gtkb-wi-4477-ollama-readiness-autostart-002.md`
- `bridge/gtkb-wi-4477-ollama-readiness-autostart-003.md`

Unrelated dirty workspace files reported by the helper plan are not claimed by
this implementation.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-OLLAMA-HARNESS-ADOPTION-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Implementation Details

- Added `evaluate_ollama_autostart()` to `scripts/verify_ollama_dispatch.py`.
  It performs a read-only Windows PowerShell probe for scheduled tasks or
  services whose names match Ollama, supports injected command runners for
  tests, and returns structured warning evidence.
- Extended `evaluate_dispatch_readiness()` so missing autostart appears in a
  `warnings` array and `autostart` payload. This preserves the approved
  boundary: missing autostart warns but does not make `ready=false` when
  `/api/tags` is reachable and the configured model is advertised.
- Added human-readable `[WARN]` readiness output for autostart warnings.
- Added `scripts/ops/install_ollama_autostart_task.ps1` with
  `SupportsShouldProcess`, task-name/path parameters, executable resolution,
  existing-task guard, `-Force` support, and user-logon `ollama serve` task
  registration. The implementation did not run this script.
- Extended `groundtruth-kb/src/groundtruth_kb/project/doctor.py` so the Ollama
  doctor check reports `L4b: Ollama /api/tags unreachable` and `L5: Ollama
  autostart not detected` warnings. Existing fixture tests set explicit skip
  env vars for hermetic checks; new tests opt back in.
- Added regression tests for autostart parsing, warning-not-blocking readiness,
  doctor API-unreachable warning, doctor missing-autostart warning, installer
  guard strings, and existing Ollama readiness fallback behavior.

## Spec-to-Test Mapping

| Specification | Verification |
| --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed paths are all under `E:\GT-KB` and limited to the approved platform target paths. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation-start packet created from latest GO before edits; target paths match the proposal. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal preflight passed before implementation; report carries project/work metadata and spec links forward. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, fallback tests, ruff lint, ruff format-check, and PowerShell parser checks executed with observed results below. |
| `ADR-OLLAMA-HARNESS-ADOPTION-001`, `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `DCL-OLLAMA-TOOL-PARITY-GATE-001`, `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`, `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` | Readiness and doctor tests verify routing/tool readiness is preserved, API reachability is visible, and host autostart is diagnostic only. |
| `GOV-STANDING-BACKLOG-001`, `GOV-RELIABILITY-FAST-LANE-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | No bulk backlog mutation performed; bridge/advisory/work-item linkage is preserved and WI closure remains deferred until VERIFIED. |

## Verification Commands

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi-4477-ollama-readiness-autostart
```

Observed result: PASS. Packet hash
`sha256:276aafb69bfeb345702843469bedfb3d1d522faac4d8548dc4e150c40cfe628b`;
latest status `GO`; target path globs were the six approved target paths.

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_verify_ollama_dispatch.py groundtruth-kb\tests\test_doctor_ollama.py -q --tb=short
```

Observed result: PASS, `45 passed in 0.81s`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_ollama_dispatch.py::test_trigger_resolves_active_ollama_only_when_readiness_passes platform_tests\scripts\test_ollama_dispatch.py::test_trigger_fails_closed_when_ollama_readiness_fails platform_tests\scripts\test_ollama_dispatch.py::test_registered_ollama_without_role_is_not_selected -q --tb=short
```

Observed result: PASS, `3 passed in 0.27s`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\verify_ollama_dispatch.py groundtruth-kb\src\groundtruth_kb\project\doctor.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_verify_ollama_dispatch.py groundtruth-kb\tests\test_doctor_ollama.py
```

Observed result: PASS, `All checks passed!`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\verify_ollama_dispatch.py groundtruth-kb\src\groundtruth_kb\project\doctor.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_verify_ollama_dispatch.py groundtruth-kb\tests\test_doctor_ollama.py
```

Observed result: PASS, `5 files already formatted`.

```text
[System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path -LiteralPath scripts\ops\install_ollama_autostart_task.ps1), [ref]$tokens, [ref]$errors)
```

Observed result: PASS, `PowerShell parser: OK`.

### Non-Decisive Selector Attempt

The proposal listed a broad cross-trigger selector:

```text
python -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short -k "ollama and readiness"
```

Observed result: `0 selected`; this selector does not match current test names.
I did not count it as verification evidence. The fallback/readiness contract was
verified by the exact `platform_tests/scripts/test_ollama_dispatch.py` tests
listed above. A broader `-k "ollama"` run in
`platform_tests/scripts/test_cross_harness_bridge_trigger.py` selected two tests
outside the approved target scope and both failed on pre-existing expected
summary-shape keys; that file was not in the approved target paths and is not
claimed by this implementation.

## Acceptance Criteria Status

- PASS: API unreachable remains a hard readiness failure via the existing
  `/api/tags` check.
- PASS: missing autostart is warning-only when daemon/model readiness is good.
- PASS: `gt project doctor` surfaces API-unreachable and missing-autostart as
  WARN findings.
- PASS: the scheduled-task installer script is tracked, guarded, and parser
  validated; it was not executed.
- PASS: existing fallback behavior still resolves or blocks Ollama based on
  readiness and preserves the `ollama_dispatch_not_ready` path.
- PASS: ruff lint and format checks passed for changed Python files.

## Residual Risk / Rollback

Residual risk is operational: the autostart script exists but has not been run,
so this implementation makes missing autostart visible and operator-installable
rather than changing the host immediately. Rollback is a normal revert of the
six target files plus this bridge report if Loyal Opposition rejects the
implementation.

## Recommended Work Item Closure

If Loyal Opposition records VERIFIED, resolve `WI-4477` with this bridge thread
as completion evidence. No work-item state mutation is claimed before VERIFIED.
