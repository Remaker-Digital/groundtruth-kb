NEW
author_identity: prime-builder/codex-automation
author_harness_id: A
author_session_context_id: 019f1153-9110-7fc2-9d51-42a1e383cf07
author_model: gpt-5-codex
author_model_version: 2026-06-19
author_model_configuration: Codex desktop automation session; approval_policy=never; autonomous Prime Builder

# WI-4888 Cursor Agent CLI Subcommand No-Window Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4888-cursor-agent-cli-subcommand-no-window
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-002.md
Approved proposal: bridge/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-001.md
Implementation commit: 8365119b4
Recommended commit type: fix:

## Implementation Claim

Implemented a scoped Cursor harness launcher fix and tests under the approved target paths:

- `scripts/cursor_harness.py`
- `platform_tests/scripts/test_cursor_harness.py`

The harness now builds a command vector instead of a single executable string, preserves standalone `agent` resolution when present, and only falls back to `cursor agent` when `cursor agent --help` exposes a headless print/output interface (`--print`/`-p` and `--output-format`). It also applies Windows no-window subprocess creation flags to both Cursor help probing and harness execution.

Live smoke testing found the installed Cursor launcher at `C:\Users\micha\AppData\Local\Programs\cursor\resources\app\bin\cursor.cmd` advertises an `agent` subcommand in top-level help, but `cursor agent --help` still prints the top-level `cursor.exe [options][paths...]` help and does not expose `--print` or `--output-format`. The implementation therefore fails closed on this host instead of routing GT-KB dispatch prompts through the GUI/Electron path.

This report does not claim full WI-4888 closure. The code-side guard is complete, but the local runtime remains blocked until a standalone `agent` executable is installed or the local Cursor CLI exposes a real headless `cursor agent --print --output-format` surface.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `WI-4888`

## Owner Decisions / Input

No new owner decision was required for the code change. The remaining runtime blocker is environmental: this workstation currently has no standalone `agent` executable on PATH, and the installed Cursor CLI does not expose the required headless print/output options under `cursor agent`.

## Prior Deliberations

- `bridge/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `bridge/gtkb-wi4881-headless-cursor-lo-dispatch-verdicts-004.md` - prior terminal VERIFIED Cursor headless dispatch thread; local CLI behavior has since drifted.
- `WI-4888` - open full-topology go-live acceptance item requiring real-harness smoke before release.
- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - dispatcher issues must be resolved before release.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live GO existed in `bridge/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-002.md`; work-intent claim was current; implementation authorization listed the WI-4888 packet as valid with the approved target globs. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Applicability preflight passed; ADR/DCL clause preflight passed with zero blocking gaps; this report carries linked specs, command evidence, and the residual runtime blocker. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, `ADR-DISPATCHER-ARCHITECTURE-001` | Focused dispatcher config tests still pass; live dispatcher status still reports the old `prime-builder:E` `cursor_headless_cli_unavailable` runtime failure because no fresh successful Cursor smoke can be produced on the current installation. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Cursor harness command building remains bounded by timeout and now fails closed when no headless Agent surface is available. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Focused Cursor harness tests cover standalone `agent`, safe `cursor agent` fallback, rejection of top-level-only Cursor launcher help, command shape, explicit override handling, and Windows no-window flags. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`, `WI-4888` | Release readiness remains blocked for Cursor E on this host until the external headless Agent CLI exists and a fresh smoke succeeds. |

## Commands Run

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4888-cursor-agent-cli-subcommand-no-window`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4888-cursor-agent-cli-subcommand-no-window`
- `python -m pytest platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short`
- `python -m ruff check scripts/cursor_harness.py platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_bridge_dispatch_config.py`
- `python -m ruff format --check scripts/cursor_harness.py platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_bridge_dispatch_config.py`
- `git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check -- scripts/cursor_harness.py platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_bridge_dispatch_config.py`
- `Get-Command cursor; cursor agent --help | Select-String -Pattern '--output-format|--print|Usage: cursor.exe|Subcommands|agent'`
- `python -c "import importlib.util; spec=importlib.util.spec_from_file_location('cursor_harness','scripts/cursor_harness.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(m._cursor_supports_agent_subcommand('C:/Users/micha/AppData/Local/Programs/cursor/resources/app/bin/cursor.cmd'))"`
- `python scripts/cursor_harness.py --prompt "Reply with exactly OK." --timeout 30`
- `python -c "import json, subprocess, pprint; p=subprocess.run(['python','-m','groundtruth_kb.cli','bridge','dispatch','status','--json'],capture_output=True,text=True,check=True); d=json.loads(p.stdout); pprint.pp({'health_status':d.get('health_status'),'health_findings':d.get('health_findings'),'runtime_classifications':d.get('runtime_classifications')})"`
- `git commit --amend --no-edit`

## Observed Results

- Applicability preflight: `preflight_passed: true`; `missing_required_specs: []`; packet hash `sha256:a0711ad9dcaaafbb91653baba071c3d09357b7d2f29260d97a94fcce29d8f724`.
- ADR/DCL clause preflight: mandatory mode; clauses evaluated 5; must_apply 2; evidence gaps in must_apply clauses 0; blocking gaps 0; exit 0.
- Pytest: 56 passed in 1.71s.
- Ruff check: `All checks passed!`
- Ruff format check: `3 files already formatted`.
- Diff whitespace check: exit 0 with CR-at-EOL allowed for existing CRLF-indexed files.
- Local Cursor evidence: `Get-Command cursor` resolves `C:\Users\micha\AppData\Local\Programs\cursor\resources\app\bin\cursor.cmd`; `cursor agent --help` shows top-level `Usage: cursor.exe [options][paths...]`, `Subcommands`, and `agent`, but no `--print` or `--output-format`.
- Resolver evidence: `_cursor_supports_agent_subcommand(...cursor.cmd)` returned `False`.
- Live harness smoke: failed closed with `cursor_harness: Cursor Agent CLI not found. Ensure standalone agent is on PATH, install a Cursor CLI that supports cursor agent --print --output-format, or set CURSOR_AGENT_BIN.`
- Dispatcher status: `health_status: WARN`; old recent-run `prime-builder:E` failure still reports `failure_class=cursor_headless_cli_unavailable` because the external headless Agent surface is unavailable.
- Commit: `[develop 8365119b4] fix: support Cursor agent subcommand dispatch`; 2 files changed, 153 insertions, 32 deletions.

## Files Changed

- `scripts/cursor_harness.py` - resolves command vectors, probes `cursor agent --help` for headless print/output support before using Cursor fallback, applies no-window creation flags, and fails closed with actionable guidance.
- `platform_tests/scripts/test_cursor_harness.py` - extends coverage for standalone `agent`, safe Cursor fallback, top-level-only Cursor help rejection, explicit override handling, command shape, and Windows no-window flags.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: this repairs Cursor harness dispatch selection and prevents a false-positive GUI/Electron launch path.

```text
 platform_tests/scripts/test_cursor_harness.py | 116 ++++++++++++++++++++++----
 scripts/cursor_harness.py                     |  69 +++++++++++----
 2 files changed, 153 insertions(+), 32 deletions(-)
```

## Acceptance Criteria Status

- [x] Cursor E command resolution now fails closed with a precise actionable message when no standalone `agent` or headless `cursor agent` surface is available.
- [x] The harness does not treat top-level Cursor help text as proof of a usable Agent print interface.
- [x] The Cursor harness subprocess path carries Windows no-window flags under GT-KB control.
- [x] Focused Cursor harness and dispatcher config tests pass.
- [ ] Dispatcher health does not yet clear `cursor_headless_cli_unavailable`; the installed Cursor CLI lacks the external headless Agent surface needed for a successful fresh smoke.
- [ ] Full WI-4888 release-readiness closure remains blocked until the external Cursor Agent CLI/runtime is corrected outside these target paths.

## Risk And Rollback

Residual risk is that future Cursor versions may expose a valid headless `cursor agent` help surface with different option names. The current check intentionally fails closed until the headless print/output contract is unambiguous.

Rollback is path-local: revert commit `8365119b4`, restoring the previous standalone-`agent`-only resolver and tests. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify commit `8365119b4` for the implemented fail-closed launcher hardening and no-window behavior.
2. Confirm whether this partial implementation should be returned as `NO-GO` for unmet runtime acceptance, or accepted as a verified code-side fix with a separate external Cursor Agent runtime blocker.
3. If returning `NO-GO`, cite the remaining action as installation or availability of a real headless Cursor Agent CLI (`agent` on PATH or working `cursor agent --print --output-format`) before WI-4888 can close.
