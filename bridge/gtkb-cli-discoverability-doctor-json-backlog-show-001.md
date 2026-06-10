NEW

# Implementation Proposal - CLI Discoverability: gt project doctor --json + gt backlog show (WI-3262)

bridge_kind: prime_proposal
Document: gtkb-cli-discoverability-doctor-json-backlog-show
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3262

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_cli_doctor.py", "groundtruth-kb/tests/test_cli_backlog.py"]

This NEW proposal adds two CLI verbs that the 2026-05-10 session wrote ad-hoc Python scripts for — operationalizing the Deterministic Services Principle by promoting common probes from session-Python to durable CLI surfaces.

## Claim

Two additions:
1. `gt project doctor --json` flag: existing `gt project doctor` emits markdown; add JSON output mode for tooling consumption (dashboard, scanners, regression tests).
2. `gt backlog show <wi-id>`: new subcommand to display a single work item's record (description, links, history) in human and JSON formats. Replaces ad-hoc `db.get_work_item(...)` Python scripts.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - umbrella governance.
- `SPEC-AUQ-POLICY-ENGINE-001` - CLI surfaces extend the policy engine.
- `GOV-STANDING-BACKLOG-001` - `gt backlog show` is a read-side counterpart to backlog management.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - principle this manifests.
- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - principle definition.
- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` - batch-3 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner directive "Please continue with the next priority project" - authorizes this NEW.

## Requirement Sufficiency

Existing requirements sufficient. WI-3262 description identifies the two specific CLI surfaces and the symptom (ad-hoc Python proliferation).

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-DETERMINISTIC-SERVICES-001 per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch3-deterministic-services-authorization.json`. Review-packet inventory: IP-1 (doctor JSON) + IP-2 (backlog show) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed at `bridge/gtkb-cli-discoverability-doctor-json-backlog-show-001.md`; new top entry prepended.

## Proposed Scope

### IP-1: gt project doctor --json

In `groundtruth-kb/src/groundtruth_kb/project/doctor.py` + cli.py, add `--json` flag to existing doctor command:

```python
@project.command()
@click.option("--json", "json_output", is_flag=True)
def doctor(json_output):
    results = run_all_checks()
    if json_output:
        click.echo(json.dumps([asdict(r) for r in results], indent=2))
    else:
        render_markdown(results)
```

Schema for JSON output: list of `{check_name, status, severity, message, evidence}` objects. Stable schema for downstream consumers.

### IP-2: gt backlog show <wi-id>

In `groundtruth-kb/src/groundtruth_kb/cli.py`:

```python
@backlog.command("show")
@click.argument("wi_id")
@click.option("--json", "json_output", is_flag=True)
def backlog_show(wi_id, json_output):
    wi = db.get_work_item(wi_id)
    if not wi:
        raise click.ClickException(f"Work item not found: {wi_id}")
    if json_output:
        click.echo(json.dumps(wi, indent=2, default=str))
    else:
        render_wi_markdown(wi)
```

Includes: id, title, status, stage, priority, project_name, source_spec_id, description, change history (last 3 versions).

### IP-3: Tests + no spec promotion

Tests cover: doctor --json schema, doctor markdown preservation (regression), backlog show found/not-found cases, --json mode for both.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| doctor --json emits valid JSON | `test_doctor_json_emits_valid_json` |
| doctor --json schema is stable | `test_doctor_json_schema` |
| doctor markdown still works | `test_doctor_markdown_default_preserved` |
| backlog show prints WI | `test_backlog_show_prints_wi` |
| backlog show --json emits JSON | `test_backlog_show_json_mode` |
| backlog show on missing WI fails | `test_backlog_show_missing_wi_fails` |
| backlog show includes history | `test_backlog_show_includes_history_versions` |

Run: `python -m pytest groundtruth-kb/tests/test_cli_doctor.py groundtruth-kb/tests/test_cli_backlog.py -v`.

## Acceptance Criteria

- IP-1 doctor JSON landed; 3 tests PASS.
- IP-2 backlog show landed; 4 tests PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: JSON schema changes could break downstream consumers. Mitigation: version the schema; document in --help.
- Rollback: revert flag additions; existing commands unchanged.

## Recommended Commit Type

`feat` - new CLI flags + subcommand. ~70 LOC.
