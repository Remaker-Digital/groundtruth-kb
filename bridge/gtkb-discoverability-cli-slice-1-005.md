NEW
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Post-Implementation Report - GT-KB Discoverability CLI Slice 1

bridge_kind: implementation_report
Document: gtkb-discoverability-cli-slice-1
Version: 005
Author: Prime Builder (Codex harness A)
Date: 2026-05-20 UTC
Implements: `bridge/gtkb-discoverability-cli-slice-1-004.md`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation followed the live bridge GO and this report advances the bridge lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report cites the approved governing specs and target scope.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - implementation authorization resolved the approved project/work item linkage for WI-3262.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - tests below map to the approved acceptance criteria.
- `GOV-STANDING-BACKLOG-001` - `gt backlog show` reads the canonical MemBase work_items backlog without mutating it.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation outputs are in-root under `E:\GT-KB\groundtruth-kb\`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the new CLI surfaces emit structured artifacts instead of requiring ad-hoc Python inspection.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - discoverability data is exposed through governed CLI surfaces.

## Claim

Slice 1 is implemented. `gt project doctor --json` now emits the existing `format_doctor_report_json` schema while preserving non-zero exit behavior for failing doctor reports. `gt backlog show <work-item-id>` now provides human-readable and JSON detail for one MemBase work item, with optional version history.

## Changed Files

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/tests/test_cli_discoverability.py`

The `cli.py` working tree already contained unrelated dirty edits before this slice. This slice's intentional changes in that file are limited to the `project doctor --json` option, `_format_work_item_detail`, and the `backlog show` subcommand. All outputs are under `E:\GT-KB`.

## Implementation Notes

- Added `--json` to `gt project doctor`; the human-output path is unchanged when the flag is absent.
- Added `gt backlog show WORK_ITEM_ID [--json] [--history]`.
- Missing work items raise `ClickException("Work item not found: <id>")`.
- Added ten spec-derived tests in `groundtruth-kb/tests/test_cli_discoverability.py`.

## Specification-Derived Verification

| Requirement | Verification evidence |
|---|---|
| `gt project doctor --json` emits parseable schema v1 JSON | `test_doctor_json_flag_emits_schema_v1_envelope` and live smoke `project doctor --json` parsed successfully. |
| Doctor JSON preserves fail exit behavior | `test_doctor_json_exits_nonzero_when_overall_fail`; live smoke parsed JSON while actual checkout doctor exited `1`, consistent with fail status. |
| Doctor human output remains unchanged without `--json` | `test_doctor_without_json_preserves_human_output`. |
| `gt backlog show <id>` emits full human work-item detail | `test_backlog_show_emits_work_item_record`; live `gt backlog show WI-3262` printed the expected record. |
| `gt backlog show <id> --json` emits parseable current-row JSON | `test_backlog_show_json_flag_emits_dict`; live `gt backlog show WI-3262 --json` parsed successfully. |
| `--history` emits newest-first version chain | `test_backlog_show_with_history_includes_version_chain`; live `gt backlog show WI-3262 --history` showed `v1`. |
| `--json --history` emits `{current, history}` | `test_backlog_show_json_with_history_emits_current_and_history_keys`. |
| Unknown IDs fail clearly | `test_backlog_show_missing_id_raises_clickexception`, `test_backlog_show_unknown_id_exits_nonzero`, and live `gt backlog show WI-9999 --json` exited `1`. |

## Verification Commands

Authorization:

```text
python scripts\implementation_authorization.py begin --bridge-id gtkb-discoverability-cli-slice-1
```

Result: latest bridge status `GO`, project authorization active, packet hash `sha256:4558c315a169aa95e466e93b6ebf222c0d80e5fb27e9843e600530347f8fbce3`.

Focused spec-derived tests:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m pytest groundtruth-kb/tests/test_cli_discoverability.py -q --tb=short
```

Result: `10 passed in 1.61s`.

Existing CLI regression lane:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m pytest groundtruth-kb/tests/test_cli.py groundtruth-kb/tests/test_cli_projects.py groundtruth-kb/tests/test_cli_deliberations.py groundtruth-kb/tests/test_cli_discoverability.py -q --tb=short
```

Result: `73 passed, 1 warning in 17.56s`.

Lint and format:

```text
python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_cli_discoverability.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_cli_discoverability.py
```

Results: `All checks passed!`; `2 files already formatted`.

CLI smoke checks:

```text
$env:PYTHONPATH='groundtruth-kb/src'; $payload = & python -m groundtruth_kb project doctor --dir . --json; $doctorExit = $LASTEXITCODE; $null = ConvertFrom-Json -InputObject ($payload -join "`n"); "OK doctor_json_parse exit=$doctorExit"
```

Result: `OK doctor_json_parse exit=1`. The JSON parsed; exit 1 reflects the live checkout doctor status.

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb backlog show WI-3262
```

Result: printed the WI-3262 record with title, priority, project, subproject, stage, status detail, description, and acceptance summary.

```text
$env:PYTHONPATH='groundtruth-kb/src'; $payload = & python -m groundtruth_kb backlog show WI-3262 --json; $showExit = $LASTEXITCODE; $null = ConvertFrom-Json -InputObject ($payload -join "`n"); "OK backlog_json_parse exit=$showExit"
```

Result: `OK backlog_json_parse exit=0`.

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb backlog show WI-3262 --history
```

Result: printed the WI-3262 record plus newest-first version history.

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb backlog show WI-9999 --json; "exit=$LASTEXITCODE"
```

Result: exit `1`, `Error: Work item not found: WI-9999`.

Whitespace:

```text
git diff --check -- groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_cli_discoverability.py
```

Result: exit 0, no output.

## Broad Regression Sweep

Command:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m pytest groundtruth-kb/tests -q --tb=short
```

Result: `2235 passed, 27 failed, 1 skipped, 1 warning in 460.15s`.

The 27 failures are outside this slice's touched behavior and cluster around existing scaffold golden drift, bridge import hygiene, bridge-propose helper expectations, broad-exception marker policy, mypy strict gates, harness registration FSM tests, ownership/registry snapshots, policy gate expectation drift, public API docstrings/type checks, and registry coverage. The narrower CLI regression lane above passes.

## Residual Risk

The implementation is read-only against MemBase. The main residual risk is that the full package suite is already red for unrelated project-wide gates, so this slice relies on focused tests, existing CLI regression tests, lint/format, and live smoke checks for closure until those broader gates are repaired by their own bridge work.
