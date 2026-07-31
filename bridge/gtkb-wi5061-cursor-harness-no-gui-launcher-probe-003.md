NEW

# GT-KB Bridge Implementation Report - gtkb-wi5061-cursor-harness-no-gui-launcher-probe - 003

bridge_kind: implementation_report
Document: gtkb-wi5061-cursor-harness-no-gui-launcher-probe
Version: 003 (NEW; post-implementation report)
Date: 2026-07-06 UTC
Author: Prime Builder (Codex, harness A)

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-06T21-09-04Z-prime-builder-A-6186df
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex headless auto-dispatch; resolved role prime-builder

Responds to GO: bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-002.md
Approved proposal: bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5061
Recommended commit type: fix:

## Implementation Claim

Implemented the approved fail-closed Cursor launcher probe fix in the scoped
target paths:

- `scripts/cursor_harness.py`
  - Added a standalone-agent executable allowlist for the `agent --help`
    capability probe.
  - Made `_cursor_supports_agent_subcommand` return `False` without invoking
    `subprocess.run` when the candidate executable name is `cursor`,
    `cursor.cmd`, or `cursor.exe`.
  - Made `CURSOR_AGENT_BIN` fail closed immediately when it points at a Cursor
    GUI launcher, with guidance to use a standalone `agent` or `cursor-agent`
    executable.
  - Removed the fallback that searched PATH for `cursor`, `cursor.cmd`, and
    `cursor.exe` and then probed `agent --help`.
- `platform_tests/scripts/test_cursor_harness.py`
  - Updated the prior GUI-launcher fallback test to assert fail-closed behavior.
  - Added coverage proving GUI launcher names do not trigger the subprocess
    capability probe.
  - Preserved coverage for standalone agent, direct Windows cursor-agent
    commands, and wrapper fallbacks.

The broad repository worktree was already dirty before this dispatch. This
report claims only the two approved target paths above. A pre-existing dirty
hunk in `scripts/cursor_harness.py` that sets `GTKB_AUTHOR_MODEL*` environment
defaults is not part of this WI-5061 implementation claim.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` - small, low-risk reliability defect fix filed
  under the project's standing authorization.
- `GOV-HARNESS-ISOLATION-001` - harnesses are clients confined to bridge and
  `gt` CLI surfaces; the cursor shim must not open the vendor GUI IDE as a side
  effect of command-resolution.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority for this
  proposal, GO, and implementation report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal and
  report carry forward governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, Work Item,
  and Project Authorization linkage are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification derives from
  the linked headless/harness-isolation behavior.
- `GOV-STANDING-BACKLOG-001` - WI-5061 is the governing backlog authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) - owner-reported defect is
  preserved through durable WI and bridge artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) - artifact-oriented
  development stance for the proposal/report chain.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) - lifecycle trigger for the
  owner-reported defect capture.

## Owner Decisions / Input

No new owner decision is required by this implementation report. It carries
forward the proposal's owner evidence:

- Owner reported that the Cursor desktop UI had launched unexpectedly several
  times and was manually exited.
- Owner selected "Suspend cursor/E now + file the fix" through AskUserQuestion
  during the proposal session.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` authorizes this reliability
  fast-lane work item by active project membership.

## Prior Deliberations

- `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT` - owner
  requirement that Windows launches be headless.
- `INTAKE-c60bf094` - "Prohibit direct harness-to-harness invocation"; related
  harness-discipline lineage now formalized as `GOV-HARNESS-ISOLATION-001`.
- `bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-001.md` - approved
  implementation proposal carried forward.
- `bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-002.md` - Loyal
  Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-RELIABILITY-FAST-LANE-001` | Targeted unit and readiness tests passed for the low-risk defect fix: `platform_tests/scripts/test_cursor_harness.py` and `platform_tests/scripts/test_verify_cursor_dispatch.py` reported 32 passed. |
| `GOV-HARNESS-ISOLATION-001` | `test_resolve_agent_command_rejects_cursor_gui_override_without_probe`, `test_cursor_agent_subcommand_support_refuses_gui_launcher_without_probe`, and `test_resolve_agent_command_does_not_probe_cursor_gui_launcher_fallback` assert that GUI launcher names do not get invoked as agent probes. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation proceeded from live latest `GO` at `bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-002.md`; `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5061-cursor-harness-no-gui-launcher-probe` created authorization packet `sha256:49eb3772673dbd653d7bf9e5e9b4cbe5ab175bd603c4689eeeb55177de2d0143`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the proposal's linked specifications and maps them to executed evidence. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header metadata carries forward `Project Authorization`, `Project`, and `Work Item` from the approved proposal and GO verdict. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Tests directly cover the specified fail-closed behavior: absent standalone agent plus GUI launcher availability raises `CursorHarnessError` without probing `cursor`/`cursor.cmd`/`cursor.exe`. |
| `GOV-STANDING-BACKLOG-001` | Work remains tied to `WI-5061` in the report header and bridge thread. |
| Advisory artifact-governance surfaces | The durable bridge chain preserves the owner report, proposal, GO verdict, implementation evidence, and verification request. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi5061-cursor-harness-no-gui-launcher-probe`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi5061-cursor-harness-no-gui-launcher-probe`
- With `TMP=E:\GT-KB\.tmp` and `TEMP=E:\GT-KB\.tmp`:
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_verify_cursor_dispatch.py -q --no-header`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cursor_harness.py platform_tests/scripts/test_cursor_harness.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cursor_harness.py platform_tests/scripts/test_cursor_harness.py`

## Observed Results

- Implementation authorization succeeded for latest `GO`, target paths
  `scripts/cursor_harness.py` and `platform_tests/scripts/test_cursor_harness.py`.
- Work-intent claim acquired for session
  `2026-07-06T21-09-04Z-prime-builder-A-6186df`.
- Targeted pytest rerun with workspace temp directory: `32 passed, 2 warnings in
  4.99s`. The warnings were the existing `PytestConfigWarning: Unknown config
  option: asyncio_mode` and a cache-path warning for
  `E:\GT-KB\.pytest_cache\v\cache\nodeids`.
- Earlier pytest attempts using the default user temp directory were blocked by
  `PermissionError: [WinError 5] Access is denied:
  'C:\Users\micha\AppData\Local\Temp\pytest-of-micha'`. The passing rerun used
  an in-workspace temp directory to avoid that host-local permission issue.
- Ruff lint: `All checks passed!`
- Ruff format check: `2 files already formatted`

## Files Changed

Claimed by this WI-5061 implementation:

- `scripts/cursor_harness.py`
- `platform_tests/scripts/test_cursor_harness.py`

Bridge/report artifact filed by this step:

- `bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-003.md`

Pre-existing unrelated dirty worktree content remains outside this report's
implementation claim and was not reverted.

## Acceptance Criteria Status

- [x] Cursor GUI launcher names are never probed with `agent --help`.
- [x] Missing standalone Cursor agent fails closed with `CursorHarnessError`
  instead of falling back to the GUI launcher.
- [x] Existing standalone-agent command-resolution paths remain covered.
- [x] Approved targeted tests and code-quality checks passed.

## Risk And Rollback

Residual risk is limited to environments that previously relied on a GUI
`cursor` launcher doubling as a headless agent CLI. That behavior is the defect
this thread intentionally removes; those environments must install or configure
a standalone `agent` or `cursor-agent` executable via PATH or `CURSOR_AGENT_BIN`.

Rollback is a single revert of the two claimed source/test file changes. Bridge
audit files remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed
   command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved
   proposal, otherwise return NO-GO with findings.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
