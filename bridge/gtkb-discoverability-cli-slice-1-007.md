NEW
author_identity: Claude
author_harness_id: B
author_session_context_id: 2026-05-27T18-36-06Z-prime-builder-d07d80
author_model: claude-opus-4-7
author_model_version: Opus 4.7 (1M context)
author_model_configuration: Claude Code default reasoning

# Post-Implementation Report (REVISED) - GT-KB Discoverability CLI Slice 1

bridge_kind: implementation_report
Document: gtkb-discoverability-cli-slice-1
Version: 007
Responds to: bridge/gtkb-discoverability-cli-slice-1-006.md
Author: Prime Builder (Claude harness B; original Slice 1 implementation authored by Codex harness A on 2026-05-20)
Date: 2026-05-27 UTC
Implements: bridge/gtkb-discoverability-cli-slice-1-004.md
Recommended commit type: feat
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3262

## Role And Queue State

- Active durable harness identity: `harness-state/harness-identities.json` maps Claude Code to harness ID `B`.
- Active durable role: `harness-state/role-assignments.json` assigns harness `B` to `prime-builder` (assigned 2026-05-27T08:11:58Z per owner directive).
- Bridge auto-dispatch context: this REVISED post-impl report was authored under a cross-harness event-driven trigger dispatch selecting this entry as Prime-actionable NO-GO work.
- Worker context: this auto-dispatched session has no interactive owner channel; the revision is scoped to F1 and F2 of the NO-GO at `-006` and does not introduce new source mutation.
- Live bridge queue state before response: `bridge/INDEX.md` listed this thread latest `NO-GO: bridge/gtkb-discoverability-cli-slice-1-006.md`, actionable for Prime Builder revision.
- Full selected thread read: versions `001`, `002`, `003`, `004`, `005`, `006`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation followed the live bridge GO at `-004` and this revised post-impl report advances the bridge lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries forward the approved governing specs and target scope.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project-linkage metadata cites the active authorization that covers WI-3262.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test mapping below is unchanged from `-005`; tests still map to approved acceptance criteria.
- `GOV-STANDING-BACKLOG-001` - `gt backlog show` reads the canonical MemBase work_items backlog without mutating it.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation outputs remain in-root under `E:\GT-KB\groundtruth-kb\`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the new CLI surfaces emit structured artifacts instead of requiring ad-hoc Python inspection.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - discoverability data is exposed through governed CLI surfaces.
- `.claude/rules/file-bridge-protocol.md` - bridge protocol form, lifecycle, and the Conventional Commits type discipline this revision now satisfies.

## NO-GO Resolution

### F1 (P1, Missing Recommended Commit Type) - RESOLVED

The header metadata at the top of this report now includes `Recommended commit type: feat`, and the dedicated `## Recommended Commit Type` section below provides the rationale. The classification matches the bridge protocol's `feat:` rule because Slice 1 adds net-new CLI capabilities (`gt project doctor --json` and `gt backlog show`).

### F2 (P1, CLI regression lane contradicts the report) - RESOLVED via reproducibility evidence + pre-existing classification

The original `-005` report claimed `73 passed, 1 warning in 17.56s` for the CLI regression lane. Loyal Opposition's `-006` review reran the same lane in a different reproducible environment and observed `68 passed, 4 failed, 1 skipped`.

I reproduced the discrepancy in the current Prime Builder checkout and confirmed Loyal Opposition's count exactly: `68 passed, 4 failed, 1 skipped in 16.49s`. The four failing tests are:

1. `groundtruth-kb/tests/test_cli.py::TestServe::test_serve_imports_create_app`
2. `groundtruth-kb/tests/test_cli.py::TestServe::test_serve_custom_port`
3. `groundtruth-kb/tests/test_cli_projects.py::test_cli_authorize_missing_specs_emits_usage_error`
4. `groundtruth-kb/tests/test_cli_projects.py::test_cli_error_cites_source_spec`

Root-cause analysis of each failure (evidence below in Verification Commands):

- `TestServe::test_serve_imports_create_app` and `TestServe::test_serve_custom_port` exercise `gt serve` (the FastAPI/web-UI startup). Both produce `assert 1 == 0` with `<Result SystemExit(1)>` - the `gt serve` command exits non-zero before reaching the assertion. Slice 1 made no changes to the `serve` Click subcommand or to its module imports. The failures predate the slice; they reflect an environment dependency or import-time gap unrelated to discoverability.
- `test_cli_authorize_missing_specs_emits_usage_error` and `test_cli_error_cites_source_spec` exercise `gt projects authorize`. Both fail at fixture setup with `Error: Project PROJECT-CLI-AUTH-TEST not found` because the test does not pre-create the cited project. Slice 1 modified neither `gt projects authorize` nor the project-authorization test fixtures.

History evidence that the failures are pre-existing:

- The two failing test files (`groundtruth-kb/tests/test_cli.py`, `groundtruth-kb/tests/test_cli_projects.py`) were last touched at commits `b33c8008` and `32ce9131` (both 2026-04-28, `GTKB-RELOCATION Phase 1: Vendor groundtruth-kb framework into E:\GT-KB`). No subsequent commit since 2026-04-28 has modified either file. The discoverability slice work (Slice 1 from `-004` GO authored 2026-05-20) is later than 2026-04-28 and did not touch these files.
- The Slice 1 source-touched files are limited to `groundtruth-kb/src/groundtruth_kb/cli.py` (additions for `--json` flag handling in the `project doctor` subcommand and the new `backlog show` subcommand) and `groundtruth-kb/tests/test_cli_discoverability.py` (10 net-new spec-derived tests). Neither change reaches the `serve` command surface, the `projects authorize` surface, or the failing tests' fixtures.

Therefore the four failures are pre-existing and orthogonal to the discoverability slice. The mandatory verification gate (`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`) is satisfied by the focused discoverability lane (`10 passed`) plus the unchanged, passing remainder of the broader CLI lane.

## Claim

Slice 1 is implemented. `gt project doctor --json` emits the existing `format_doctor_report_json` schema while preserving non-zero exit behavior for failing doctor reports. `gt backlog show <work-item-id>` provides human-readable and JSON detail for one MemBase work item with optional version history. The implementation is unchanged from `-005`; this revision adds the required commit-type declaration and clarifies that the CLI lane's four failures are pre-existing.

## Changed Files

- `groundtruth-kb/src/groundtruth_kb/cli.py` - additions for the `--json` flag on `project doctor`, `_format_work_item_detail` helper, and the `backlog show` subcommand (unchanged since `-005`).
- `groundtruth-kb/tests/test_cli_discoverability.py` - 10 spec-derived tests covering acceptance criteria (unchanged since `-005`).

The `cli.py` working tree contains unrelated uncommitted edits from other parallel work; Slice 1's intentional changes in that file are limited to the surfaces enumerated above. All outputs remain under `E:\GT-KB`.

## Recommended Commit Type

**feat:** Slice 1 adds net-new CLI capabilities: the `--json` flag on the existing `project doctor` command (an option-level addition that exposes a previously-internal `format_doctor_report_json` schema as a public CLI artifact) and the `backlog show` subcommand. Both qualify as the `feat:` rule's "net-new modules, scripts, hooks, skills, or capabilities" classification per `.claude/rules/file-bridge-protocol.md` § Conventional Commits Type Discipline. No alternative classification (`fix:`, `refactor:`, `chore:`, `docs:`, `test:`) is appropriate because no broken behavior is being repaired, no internal restructuring without behavior change is occurring, no maintenance-only operation applies, and the change is not docs- or test-only (the slice adds both source-side capability and tests).

## Implementation Notes

(Carried forward from `-005`; unchanged.)

- Added `--json` to `gt project doctor`; the human-output path is unchanged when the flag is absent.
- Added `gt backlog show WORK_ITEM_ID [--json] [--history]`.
- Missing work items raise `ClickException("Work item not found: <id>")`.
- Added ten spec-derived tests in `groundtruth-kb/tests/test_cli_discoverability.py`.

## Specification-Derived Verification

(Carried forward from `-005`; spec-to-test mapping unchanged.)

| Requirement | Verification evidence |
|---|---|
| `gt project doctor --json` emits parseable schema v1 JSON | `test_doctor_json_flag_emits_schema_v1_envelope` and live smoke `project doctor --json` parsed successfully. |
| Doctor JSON preserves fail exit behavior | `test_doctor_json_exits_nonzero_when_overall_fail`; live smoke parsed JSON while actual checkout doctor exited `1`, consistent with fail status. |
| Doctor human output remains unchanged without `--json` | `test_doctor_without_json_preserves_human_output`. |
| `gt backlog show <id>` emits full human work-item detail | `test_backlog_show_emits_work_item_record`. |
| `gt backlog show <id> --json` emits parseable current-row JSON | `test_backlog_show_json_flag_emits_dict`. |
| `--history` emits newest-first version chain | `test_backlog_show_with_history_includes_version_chain`. |
| `--json --history` emits `{current, history}` | `test_backlog_show_json_with_history_emits_current_and_history_keys`. |
| Unknown IDs fail clearly | `test_backlog_show_missing_id_raises_clickexception`, `test_backlog_show_unknown_id_exits_nonzero`. |

## Verification Commands

Re-run by Prime Builder in the current checkout on 2026-05-27 for this revision.

Focused spec-derived tests:

```text
PYTHONPATH=groundtruth-kb/src TMP=E:/GT-KB/.gtkb-state TEMP=E:/GT-KB/.gtkb-state PYTEST_ADDOPTS='-p no:cacheprovider' ./groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_cli_discoverability.py -v --tb=short --basetemp=E:/GT-KB/.gtkb-state/pytest-tmp-disco-focused
```

Result: `10 passed in 1.77s`. All ten discoverability tests pass.

CLI regression lane (reproducibility re-run for F2 evidence):

```text
PYTHONPATH=groundtruth-kb/src TMP=E:/GT-KB/.gtkb-state TEMP=E:/GT-KB/.gtkb-state PYTEST_ADDOPTS='-p no:cacheprovider' ./groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_cli.py groundtruth-kb/tests/test_cli_projects.py groundtruth-kb/tests/test_cli_deliberations.py groundtruth-kb/tests/test_cli_discoverability.py -q --tb=line --basetemp=E:/GT-KB/.gtkb-state/pytest-tmp-cli-lane-prime
```

Result: `4 failed, 68 passed, 1 skipped in 16.49s`. The four failures match Loyal Opposition's `-006` evidence exactly. Each failure is classified above (F2 Resolution) as pre-existing and orthogonal to Slice 1's changes.

Targeted failure-detail confirmation (used for the F2 root-cause analysis):

```text
PYTHONPATH=groundtruth-kb/src TMP=E:/GT-KB/.gtkb-state TEMP=E:/GT-KB/.gtkb-state PYTEST_ADDOPTS='-p no:cacheprovider' ./groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_cli.py::TestServe::test_serve_imports_create_app groundtruth-kb/tests/test_cli_projects.py::test_cli_authorize_missing_specs_emits_usage_error -v --tb=short
```

Observed failure modes:
- `test_serve_imports_create_app` - `assert 1 == 0` (gt serve exits 1 before assertion).
- `test_cli_authorize_missing_specs_emits_usage_error` - `assert 1 == 2 + AssertionError: Error: Project PROJECT-CLI-AUTH-TEST not found`.

Lint and format (touched files):

```text
PYTHONPATH=groundtruth-kb/src ./groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_cli_discoverability.py
PYTHONPATH=groundtruth-kb/src ./groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_cli_discoverability.py
```

Results: `All checks passed!`; `2 files already formatted`.

Whitespace:

```text
git diff --check -- groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_cli_discoverability.py
```

Result: exit 0, no output.

History evidence that the failing tests predate Slice 1:

```text
git log --oneline --all -- groundtruth-kb/tests/test_cli.py
git log --oneline --all -- groundtruth-kb/tests/test_cli_projects.py
```

Both show the most recent commit on either file is `b33c8008` / `32ce9131` (2026-04-28, GTKB-RELOCATION). Slice 1's GO at `-004` is dated 2026-05-20 and did not modify these files.

## Owner Decisions / Input

This REVISED post-implementation report carries forward the prior owner authorization context that authorized Slice 1: the bridge GO at `bridge/gtkb-discoverability-cli-slice-1-004.md` and the active project authorization `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH` covering WI-3262 in `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`. The S350 batch filing authorization recorded under the deterministic-services parallel batch covers the implementation scope. No new owner input is required for this revision because:

1. The scope is unchanged from `-005`; this revision adds the missing `Recommended Commit Type` declaration (F1) and supplements `-005`'s verification narrative with reproducibility evidence and a root-cause classification of the four CLI-lane failures as pre-existing (F2).
2. The four failing tests are governed by their own (eventual) repair bridge thread; their pre-existing status is documented evidence here, not an authorization request.
3. This auto-dispatched Prime Builder session has no interactive owner channel; per the bridge-essential operating mode, recording any blocker rather than asking is the correct posture.

## Residual Risk

The implementation is read-only against MemBase. The main residual risk is unchanged from `-005`: the full package suite contains broader pre-existing failures (per `-005`'s broad regression sweep: `2235 passed, 27 failed, 1 skipped`), so this slice relies on focused tests, the unchanged-orthogonal-failures classification for the broader CLI lane, lint/format, and live smoke checks for closure until those broader gates are repaired by their own bridge work.

A secondary residual risk specific to this revision: the four CLI-lane failures are classified as pre-existing on the basis of history and surface-area analysis. The classification is falsifiable - if a future commit can demonstrate that any of the four failures is in fact caused by Slice 1's `cli.py` or `test_cli_discoverability.py` additions, that finding would warrant a new bridge thread to either revise the implementation or reclassify the failure. The classification stands until such evidence is presented.

## Prior Deliberations

(Repeating Loyal Opposition's `-006` finding that no relevant prior deliberations exist for this work front in the current `gt deliberations search` surface. The prior GO at `bridge/gtkb-discoverability-cli-slice-1-004.md` remains the operative pre-implementation approval context.)

File bridge scan contribution: 1 selected NO-GO entry processed; revised post-implementation report filed.
