REVISED
author_identity: prime-builder/codex-automation
author_harness_id: A
author_session_context_id: 2026-06-29T20-42-31Z-prime-builder-A-4d6c23
author_model: GPT-5
author_model_version: codex-desktop
author_model_configuration: Codex desktop automation session; approval_policy=never; autonomous Prime Builder bridge dispatch

# WI-4888 Cursor Agent CLI Subcommand No-Window Revised Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4888-cursor-agent-cli-subcommand-no-window
Version: 005 (REVISED; post-implementation report)
Responds to NO-GO: bridge/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-004.md
Approved proposal: bridge/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-001.md
Prior implementation report: bridge/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-003.md
Recommended commit type: fix:

## Revision Claim

No source files were modified for this revision. Prime Builder rechecked the host runtime after the NO-GO and found that the Cursor Agent binary surface is now present and discoverable:

- `Get-Command agent` resolves `C:\Users\micha\AppData\Local\cursor-agent\agent.ps1`.
- `agent --help` exposes the required headless flags: `--print` and `--output-format`.
- `scripts/cursor_harness.py` resolves the Agent command to `C:\Users\micha\AppData\Local\cursor-agent\agent.CMD`.
- `gt bridge dispatch health --json` reports `health_status: PASS`.
- `gt bridge dispatch status --json` reports `health_status: PASS` and no `cursor_headless_cli_unavailable` runtime classification.

The remaining blocker is authentication, not binary discovery. A live Cursor harness smoke still fails with:

```text
Error: Authentication required. Please run 'agent login' first, or set CURSOR_API_KEY environment variable.
```

`agent status` reports:

```text
Not logged in
```

This auto-dispatched Prime Builder worker cannot interactively request owner credential action. Credential lifecycle is outside Codex scope; this report records the blocker rather than asking for login or credential changes in prose.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `WI-4888`

## Owner Decisions / Input

No new owner decision is requested in this auto-dispatched worker. The remaining action is an external Cursor Agent authentication state change (`agent login` or `CURSOR_API_KEY` availability). Per the GT-KB credential lifecycle rule, Codex does not ask Mike to rotate, create, or enter credentials; when credentials change, Mike updates the appropriate environment surface and Codex may validate them only when the task requires it and use is authorized.

## Prior Deliberations

- `bridge/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-001.md` - approved proposal.
- `bridge/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-002.md` - GO verdict.
- `bridge/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-003.md` - original post-implementation report.
- `bridge/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-004.md` - NO-GO verification verdict requiring a working headless Cursor Agent runtime.
- `bridge/gtkb-wi4881-headless-cursor-lo-dispatch-verdicts-004.md` - prior terminal Cursor headless dispatch thread.
- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - dispatcher issues remain release blockers.

## Finding Response

### Finding 1: Unmet Release-Readiness Runtime Blocker

Response: partially addressed and still blocked. The host now has a compatible `agent` executable surface on PATH, the harness resolver selects it, and dispatcher health no longer reports the earlier `cursor_headless_cli_unavailable` failure. End-to-end Cursor harness smoke still fails because the Cursor Agent is not authenticated. This means WI-4888 remains blocked for full runtime verification until the external Cursor Agent credential state is restored.

## Spec-Derived Verification Evidence

| Spec / governing surface | Executed verification evidence | Result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Work-intent claim `2026-06-29T20:44:37Z` for `gtkb-wi4888-cursor-agent-cli-subcommand-no-window`; latest live status was `NO-GO` before this revision. | Claim acquired; revision scoped to bridge artifact only. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, `ADR-DISPATCHER-ARCHITECTURE-001` | `gt bridge dispatch health --json`; `gt bridge dispatch status --json`. | Both report `health_status: PASS`; no live `cursor_headless_cli_unavailable` classification is present. |
| `DCL-DISPATCH-ENVELOPE-RULES-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | `agent --help`; resolver one-liner for `scripts/cursor_harness.py`; focused Cursor harness tests. | Agent CLI exposes `--print` and `--output-format`; resolver returns `agent.CMD`; `platform_tests/scripts/test_cursor_harness.py` passes. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`, `WI-4888` | Live smoke: `python scripts/cursor_harness.py --prompt "Reply with exactly OK." --timeout 60`; `agent status`. | Blocked: Cursor Agent reports authentication required and `Not logged in`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report carries forward linked specs, command evidence, and the unresolved blocker. | Verification should remain non-terminal until Cursor Agent authentication is available and a fresh smoke succeeds. |

## Commands Run

```text
Get-Command cursor -ErrorAction SilentlyContinue | Format-List *
Get-Command agent -ErrorAction SilentlyContinue | Format-List *
cursor agent --help
agent --help
agent status
python scripts/cursor_harness.py --prompt "Reply with exactly OK." --timeout 60
python -m pytest platform_tests/scripts/test_cursor_harness.py -q --tb=short
python -m pytest platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short
python -m ruff check scripts/cursor_harness.py platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_bridge_dispatch_config.py
python -m ruff format --check scripts/cursor_harness.py platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_bridge_dispatch_config.py
gt bridge dispatch health --json
gt bridge dispatch status --json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4888-cursor-agent-cli-subcommand-no-window --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4888-cursor-agent-cli-subcommand-no-window
```

Commands were run through `groundtruth-kb/.venv/Scripts/python.exe` and `groundtruth-kb/.venv/Scripts/gt.exe` where applicable.

## Observed Results

- Cursor launcher: `cursor.cmd` exists, and `cursor agent --help` still prints top-level Cursor GUI help.
- Cursor Agent binary: `agent.ps1` exists at `C:\Users\micha\AppData\Local\cursor-agent\agent.ps1`.
- Cursor Agent help: `agent --help` exposes `--print` and `--output-format`.
- Cursor harness resolver: `_resolve_agent_command()` returns `['C:\\Users\\micha\\AppData\\Local\\cursor-agent\\agent.CMD']`.
- Live smoke: failed with authentication required.
- Agent auth status: `Not logged in`.
- Focused Cursor tests: `18 passed, 1 warning in 0.18s`.
- Combined Cursor plus dispatcher-config tests: `22 passed`, then `38` dispatcher-config setup errors due `PermissionError: [WinError 5] Access is denied: 'C:\\Users\\micha\\AppData\\Local\\Temp\\pytest-of-micha'`; this is host temp setup, not a Cursor harness assertion failure.
- Ruff check: `All checks passed!`
- Ruff format: `3 files already formatted`.
- Dispatcher health: `PASS`.
- Dispatcher status: `PASS`; live runtime classifications contain only D/F/A entries and no Cursor headless CLI failure.
- Bridge applicability preflight on the prior operative report: `preflight_passed: true`; `missing_required_specs: []`; packet hash `sha256:f34c0107b9182d6c41278e773e64378ae2ee1bab53566e194b1c83105046753a`.
- ADR/DCL clause preflight on the NO-GO operative file: exit `0`; `must_apply: 2`; evidence gaps in must_apply clauses `0`; blocking gaps `0`.

## Acceptance Criteria Status

- [x] Cursor Agent executable is now discoverable on PATH.
- [x] Cursor Agent exposes the required headless `--print` and `--output-format` interface.
- [x] Cursor harness resolver selects the Agent executable rather than GUI-only `cursor agent` fallback.
- [x] Focused Cursor harness tests pass.
- [x] Dispatcher health/status no longer reports `cursor_headless_cli_unavailable`.
- [ ] Live Cursor harness smoke succeeds.
- [ ] Cursor Agent authentication is available to this GT-KB runtime.

## Pre-Filing Preflight Subsection

Candidate-content preflights were run before filing the live `REVISED` bridge file:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4888-cursor-agent-cli-subcommand-no-window --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-005.completed.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4888-cursor-agent-cli-subcommand-no-window --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-005.completed.md
```

Applicability result:

- packet_hash: `sha256:f75fdedd20c0fc0fc6649bfd30ef55897de4f109e5002bd6b3738381dfe95efb`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

Clause result:

- clauses evaluated: `5`
- must_apply: `3`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit: `0`

## Risk And Rollback

Risk is limited to overstating readiness. This revision explicitly does not claim full closure because the authentication-gated live smoke failed.

Rollback is not applicable for this bridge-only revision; no source files were changed.

## Loyal Opposition Ask

Keep the thread non-terminal unless a reviewer accepts dispatcher health plus binary discovery as sufficient. Prime Builder's recommendation is to retain `NO-GO` until Cursor Agent authentication is restored and a fresh `scripts/cursor_harness.py` smoke succeeds.
