NEW
author_identity: codex
author_harness_id: A
author_session_context_id: 019edcec-7b7d-7890-94ee-0f7aa92d9070
author_model: gpt-5-codex
author_model_version: gpt-5-codex Codex Desktop runtime; backend revision not exposed
author_model_configuration: Codex Desktop automation Prime Builder run; approval_policy=never; filesystem=danger-full-access; shell=powershell

# GT-KB Bridge Implementation Report - gtkb-bridge-thread-read-cli - 003

bridge_kind: implementation_report
Document: gtkb-bridge-thread-read-cli
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-bridge-thread-read-cli-002.md
Approved proposal: bridge/gtkb-bridge-thread-read-cli-001.md
Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4634
Recommended commit type: feat:

## Implementation Claim

Implemented the approved read-only bridge inspection surface for WI-4634:

- Added `groundtruth_kb.bridge.read_commands` with pure filesystem readers for numbered bridge chains.
- Added `gt bridge show SLUG [--json]` to render one thread's latest status and version chain.
- Added `gt bridge threads --wi WI-ID [--json]` to list threads that cite a work item in any version and report a metadata coverage caveat.
- Added focused tests covering status-tokenless versions, work-item matching across versions, malformed WI exit code 2, JSON output, not-found behavior, help registration, and reuse of the project lifecycle `Work Item:` regex.

The commands are read-only, stay under the configured project root, do not open MemBase, and do not mutate bridge state.

## Specification Links

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-FILE-BRIDGE-PROTOCOL-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `.claude/rules/sot-read-discipline.md`
- `.claude/rules/canonical-terminology.md`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`

## Owner Decisions / Input

No new owner decision is required. This implementation carries forward the active project authorization `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`, owner decision `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`, for `PROJECT-GTKB-MAY29-HYGIENE` / `WI-4634`.

## Prior Deliberations

- `bridge/gtkb-bridge-thread-read-cli-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-bridge-thread-read-cli-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `bridge/gtkb-bridge-convenience-verbs-008.md` - prior verified skill-side bridge thread inspection capability.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - owner directive to move repetitive inspection work into deterministic services.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-FILE-BRIDGE-PROTOCOL-001` | `test_show_thread_includes_status_tokenless_versions` verifies latest-first version-chain rendering and legacy status-tokenless inclusion; live `gt bridge show gtkb-bridge-thread-read-cli --json` returned the current two-version GO/NEW chain. |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `test_threads_for_work_item_matches_any_version_and_reports_coverage` verifies deterministic work-item-to-thread lookup without manual grep; live `gt bridge threads --wi WI-4634 --json` found the active thread plus withdrawn duplicate and reported coverage counts. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `.claude/rules/sot-read-discipline.md` | Tests exercise direct in-root `bridge/*.md` reads and include status-tokenless versions instead of relying on cached queue summaries or status-gated dispatch readers. |
| `.claude/rules/canonical-terminology.md` | Command names and JSON fields use bridge thread, work item, latest status, and version chain terminology. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All changed implementation/test files are in-root target paths authorized by the GO packet. |
| `GOV-STANDING-BACKLOG-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start packet `sha256:c3835cb7a80e302f46430eed255bcb9821c98b0c277d74aee8e674dd192e03f8` was minted for `WI-4634` under the active May29 Hygiene project authorization before edits. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff lint, ruff format, live CLI smoke checks, report applicability preflight, and ADR/DCL clause preflight were executed and are recorded below. |

## Commands Run

- `python scripts\bridge_claim_cli.py claim gtkb-bridge-thread-read-cli`
- `python scripts\implementation_authorization.py begin --bridge-id gtkb-bridge-thread-read-cli`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_read_commands.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_read_commands.py -q --tb=short -o addopts=`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\bridge\read_commands.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_bridge_read_commands.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\bridge\read_commands.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_bridge_read_commands.py`
- `gt bridge show gtkb-bridge-thread-read-cli --json`
- `gt bridge threads --wi WI-4634 --json`
- `python .claude\skills\bridge\helpers\impl_report_bridge.py plan gtkb-bridge-thread-read-cli`

## Observed Results

- Work-intent claim acquired as `go_implementation`, rowid `10508`, session `019edcec-7b7d-7890-94ee-0f7aa92d9070`.
- Implementation-start packet created: `sha256:c3835cb7a80e302f46430eed255bcb9821c98b0c277d74aee8e674dd192e03f8`; latest status `GO`; proposal `bridge/gtkb-bridge-thread-read-cli-001.md`; GO `bridge/gtkb-bridge-thread-read-cli-002.md`; target paths exactly the three implementation/test files.
- First pytest command failed before collection because the repo default addopts inject unsupported `--timeout=30` in this environment. The rerun with `-o addopts=` passed: `6 passed, 1 warning in 7.97s`.
- Ruff check passed: `All checks passed!`.
- Ruff format check passed: `3 files already formatted`.
- `gt bridge show gtkb-bridge-thread-read-cli --json` returned `latest_status: GO`, `version_count: 2`, and the expected latest-first chain for `-002` and `-001`.
- `gt bridge threads --wi WI-4634 --json` returned `match_count: 2`: active `gtkb-bridge-thread-read-cli` and withdrawn `gtkb-bridge-thread-read-cli-commands`; coverage caveat reported `572` of `1067` threads carry Work Item metadata.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_bridge_read_commands.py`

No other dirty or staged workspace files are part of this implementation report.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: adds a new CLI read capability surface plus a new implementation module and focused regression tests.

## Acceptance Criteria Status

- [x] `gt bridge show SLUG` prints the full version chain latest-first and `--json` emits the documented shape; unknown slug exits `1`.
- [x] `gt bridge threads --wi WI-NNNN` lists threads citing the WI in any version and returns a thread-level `coverage_caveat`; empty match exits `0`; malformed WI exits `2`.
- [x] Commands are read-only and do not mutate bridge or MemBase state.
- [x] `bridge --help` lists `show` and `threads` in focused CLI tests.
- [x] Focused pytest, ruff check, and ruff format check passed for the changed files.

## Risk And Rollback

Residual risk is low. The implementation touches one shared CLI file, one new read-only bridge helper module, and one focused test file. Rollback is a scoped revert of those three paths and the bridge implementation report; no database schema, bridge state reader, or dispatch state is changed by the commands.

## Loyal Opposition Asks

1. Verify the implementation against the approved proposal and the executed command evidence above.
2. Return VERIFIED if the implementation satisfies `WI-4634`; otherwise return NO-GO with specific findings.
