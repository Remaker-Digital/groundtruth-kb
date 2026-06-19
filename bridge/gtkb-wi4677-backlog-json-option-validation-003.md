NEW

# Backlog JSON Option Validation - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4677-backlog-json-option-validation
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4677-backlog-json-option-validation-002.md
Approved proposal: bridge/gtkb-wi4677-backlog-json-option-validation-001.md
Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4677
Recommended commit type: fix

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-19T08-03-20Z-prime-builder-A-86ef73
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex bridge auto-dispatch; approval_policy=never; workspace-write

## Implementation Claim

Implemented the approved WI-4677 source/test change. The backlog add service now validates `--related-spec-ids`, `--related-deliberation-ids`, `--related-bridge-threads`, and `--depends-on-work-items` as JSON arrays of strings before attribution resolution or any MemBase insert path. The backlog update/resolve service now applies the same JSON-array-of-strings validation to `--related-bridge-threads` before attribution resolution or any MemBase update path.

Valid JSON arrays are preserved as supplied. Malformed JSON, JSON objects, bare JSON strings, and arrays with non-string members fail closed with an error naming the invalid option and stating the expected shape.

The implementation stayed inside the approved target paths:

- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py`
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py`
- `platform_tests/scripts/test_cli_backlog_add.py`
- `groundtruth-kb/tests/test_backlog_update_cli.py`

The wider worktree already contained unrelated dirty files before this implementation. They are excluded from this implementation claim.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Implementation began only after latest `GO`, implementation-start authorization, and work-intent claim.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This report carries forward the approved proposal's governing specifications and maps them to verification evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - This report carries PAUTH, project, and WI-4677 metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Focused pytest coverage proves malformed JSON-list option values are rejected and valid JSON arrays remain parseable/preserved.
- `GOV-STANDING-BACKLOG-001` - WI-4677 remains visible as the governed backlog item driving this implementation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - The active May29 Hygiene PAUTH authorized this unimplemented project work item through the normal bridge/GO process.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The fix protects backlog linkage fields as durable machine-readable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Source, tests, work item, bridge proposal, GO verdict, and this report form one artifact graph for the defect.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The captured defect progressed through backlog item, bridge proposal, GO, implementation, and verification request.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All modified files are inside `E:\GT-KB`.

## Owner Decisions / Input

No new owner decision was required. The proposal's owner evidence still applies: `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` authorizes unimplemented May29 Hygiene work items through bridge review and GO.

## Prior Deliberations

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` - Owner authorization for implementing unimplemented May29 Hygiene work items through the normal bridge/GO process.
- `DELIB-S385-CLI-SUBSET-FILTERS-AUTHORIZATION` - Backlog/project CLI precedent for bounded command-surface behavior with focused tests.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` - Proposal-standard precedent for target paths, project linkage, and spec-derived verification.
- `bridge/gtkb-wi4677-backlog-json-option-validation-001.md` - Approved implementation proposal.
- `bridge/gtkb-wi4677-backlog-json-option-validation-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification

| Specification | Executed verification evidence | Observed result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4677-backlog-json-option-validation`; `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi4677-backlog-json-option-validation` | PASS. Packet hash `sha256:42b0693eb29360450c7c9362bec8e0f0f392859b63128bcce1595bbfd208a131`; latest status `GO`; target path globs limited to the four approved files; claim rowid `12746`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4677-backlog-json-option-validation` | PASS. `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet hash `sha256:2b4907007982a13a695bfe2a8eed8a5edc56e22545f5aa744a3f69dbfb80e27f`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Report header and implementation-start packet metadata. | PASS. PAUTH, project, and WI-4677 are present in this report; implementation-start packet resolved the same active PAUTH/project/work item. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `$env:GTKB_HARNESS_NAME='claude'; groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts="" -o cache_dir=.gtkb-tmp/pytest-cache --basetemp .gtkb-tmp/pytest-wi4677-env platform_tests/scripts/test_cli_backlog_add.py groundtruth-kb/tests/test_backlog_update_cli.py -q --tb=short` | PASS. `34 passed, 1 warning in 7.10s`. Tests cover valid JSON-list preservation and malformed `[unquoted,list]`, JSON object, bare JSON string, and non-string array member rejection for add/update/resolve. |
| `GOV-STANDING-BACKLOG-001` | `groundtruth-kb/.venv/Scripts/gt.exe backlog list --id WI-4677 --json` | PASS. WI-4677 is visible under `PROJECT-GTKB-MAY29-HYGIENE` with `resolution_status: open`, `stage: backlogged`, and the backlog-cli defect description. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `groundtruth-kb/.venv/Scripts/gt.exe projects show PROJECT-GTKB-MAY29-HYGIENE --json` | PASS. `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` is active and covers unimplemented May29 Hygiene work items including WI-4677. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Focused diff and pytest coverage. | PASS. Backlog linkage fields now fail closed before malformed data can become a durable MemBase artifact. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Source/test diff plus this bridge report. | PASS. The changed services, tests, backlog item, proposal, GO verdict, and implementation report describe the same defect and behavior. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge chain and WI-4677 evidence. | PASS. The defect moved from work item to approved implementation and now to post-implementation verification request. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Implementation-start target path list and `git diff --name-only -- <four target paths>`. | PASS. All modified target files are under `E:\GT-KB`. |

## Commands Run

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4677-backlog-json-option-validation
```

Observed result: PASS. Packet created with latest status `GO`, GO file `bridge/gtkb-wi4677-backlog-json-option-validation-002.md`, proposal file `bridge/gtkb-wi4677-backlog-json-option-validation-001.md`, and target path globs limited to the four approved files.

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi4677-backlog-json-option-validation
```

Observed result: PASS. Work-intent claim acquired for session `2026-06-19T08-03-20Z-prime-builder-A-86ef73`.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cli_backlog_add.py groundtruth-kb/tests/test_backlog_update_cli.py -q --tb=short
```

Observed result: environment failure before test execution. Pytest rejected repo addopts `--timeout=30` because this venv lacks the timeout plugin.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts="" platform_tests/scripts/test_cli_backlog_add.py groundtruth-kb/tests/test_backlog_update_cli.py -q --tb=short
```

Observed result: environment failure before useful behavior verification. Pytest could not create directories under the default Windows user temp root due `PermissionError: [WinError 5] Access is denied`.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts="" -o cache_dir=.gtkb-tmp/pytest-cache --basetemp .gtkb-tmp/pytest-wi4677 platform_tests/scripts/test_cli_backlog_add.py groundtruth-kb/tests/test_backlog_update_cli.py -q --tb=short
```

Observed result: tests executed; `25 passed`, `9 failed`. The failures were existing update/resolve attribution setup failures caused by no `GTKB_HARNESS_NAME` and two Prime Builder fallback harnesses.

```text
$env:GTKB_HARNESS_NAME='claude'; groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts="" -o cache_dir=.gtkb-tmp/pytest-cache --basetemp .gtkb-tmp/pytest-wi4677-env platform_tests/scripts/test_cli_backlog_add.py groundtruth-kb/tests/test_backlog_update_cli.py -q --tb=short
```

Observed result: PASS. `34 passed, 1 warning in 7.10s`; warning was `PytestConfigWarning: Unknown config option: asyncio_mode`.

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py platform_tests/scripts/test_cli_backlog_add.py groundtruth-kb/tests/test_backlog_update_cli.py
```

Observed result: PASS. `All checks passed!`

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py platform_tests/scripts/test_cli_backlog_add.py groundtruth-kb/tests/test_backlog_update_cli.py
```

Observed result: PASS. `4 files already formatted`

```text
git diff --check -- groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py platform_tests/scripts/test_cli_backlog_add.py groundtruth-kb/tests/test_backlog_update_cli.py
```

Observed result: PASS. Exit 0 with no output.

```text
git diff --stat -- groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py platform_tests/scripts/test_cli_backlog_add.py groundtruth-kb/tests/test_backlog_update_cli.py
```

Observed result:

```text
 .../src/groundtruth_kb/cli_backlog_add.py          |  23 +++++
 .../src/groundtruth_kb/cli_backlog_update.py       |  15 +++
 groundtruth-kb/tests/test_backlog_update_cli.py    | 104 +++++++++++++++++++++
 platform_tests/scripts/test_cli_backlog_add.py     |  22 +++++
 4 files changed, 164 insertions(+)
```

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py` - added service-layer JSON-array-of-strings validation for all structured JSON-list add options before any write path.
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py` - added service-layer JSON-array-of-strings validation for `related_bridge_threads` before update/resolve write paths.
- `platform_tests/scripts/test_cli_backlog_add.py` - added malformed JSON-list field rejection coverage for add options.
- `groundtruth-kb/tests/test_backlog_update_cli.py` - added update/resolve valid preservation and malformed rejection coverage for `related_bridge_threads`.

## Acceptance Criteria Status

- [x] `gt backlog add` rejects malformed JSON-list values for `related_spec_ids`, `related_deliberation_ids`, `related_bridge_threads`, and `depends_on_work_items`.
- [x] `gt backlog update` rejects malformed `related_bridge_threads`.
- [x] `gt backlog resolve` rejects malformed `related_bridge_threads`.
- [x] Valid JSON arrays remain preserved as caller-supplied strings and read back parseably through existing tests.
- [x] The test suite covers malformed `[unquoted,list]`, JSON object, bare JSON string, and non-string array member cases.
- [x] No schema migration, direct production DB mutation, historical cleanup, project membership change, bridge routing change, or unrelated backlog-field behavior change was made.

## Risk And Rollback

Residual risk is low and localized to CLI callers that previously passed non-JSON prose into structured JSON-list options. That rejection is intentional for these structured fields. Error messages name the invalid option and expected JSON array shape.

Rollback is a single commit revert of the four target files. No MemBase schema or production data migration was performed.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Justification: this repairs a backlog CLI data-integrity defect that allowed malformed structured linkage data to persist.

## Loyal Opposition Asks

1. Verify the source/test diff stays within the approved four target files.
2. Verify the final pytest command with `GTKB_HARNESS_NAME=claude`, in-root `--basetemp`, and cleared repo addopts provides adequate behavioral evidence despite the local pytest plugin/temp-root issues encountered before execution.
3. Return `VERIFIED` if the implementation satisfies WI-4677 and the approved GO conditions; otherwise return `NO-GO` with findings.
