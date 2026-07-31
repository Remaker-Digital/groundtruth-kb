NEW
author_identity: prime-builder/codex-automation
author_harness_id: A
author_session_context_id: 2026-06-30T00-25-00Z-prime-builder-A-auto-dispatch
author_model: GPT-5
author_model_version: codex-desktop
author_model_configuration: Codex automated bridge dispatch; approval_policy=never; Prime Builder role

# WI-4885 Dispatch Topology Activation Repair Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4885-dispatch-topology-activation-repair
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4885-dispatch-topology-activation-repair-002.md
Approved proposal: bridge/gtkb-wi4885-dispatch-topology-activation-repair-001.md
Recommended commit type: fix:

## Implementation Claim

Prime Builder implemented the code-side repair available in this automated
worker: `scripts/verify_claude_dispatch.py` now supports the approved
`--json --live --timeout <seconds>` readiness command and returns bounded
runtime classification evidence instead of failing argument parsing.

The Claude probe preserves the prior static-readiness API while adding:

- rendered headless command construction from the harness registry template;
- Windows `CREATE_NO_WINDOW` subprocess protection for the live probe;
- timeout/error classification through `live_probe`, `ready`,
  `dispatchable_now`, and `first_failed_check`;
- CLI options `--live`, `--prompt`, and `--timeout`;
- tests for successful live output and fail-closed timeout behavior.

This report does not claim full dispatch topology terminal readiness. The live
runtime probes still expose non-code blockers:

- Cursor Agent remains unauthenticated even though the executable is found and
  `CURSOR_API_KEY` is visible to the probe.
- Antigravity `agy --print` exits `0` but produces no stdout and no recoverable
  run-correlated conversation response.
- Claude Code static readiness passes, but the new live probe times out under
  the bounded `--live --timeout 20` run.
- Dispatcher health is currently `WARN` because OpenRouter F has a recent
  runtime failure with one pending Loyal Opposition item.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-AUTOMATION-VALUE-VS-COST-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `WI-4885`

## Owner Decisions / Input

No new owner decision was required for this implementation report. The selected
auto-dispatch worker cannot collect interactive owner input. Remaining
readiness failures are recorded here as runtime blockers rather than prose
requests.

## Prior Deliberations

- `DELIB-20266276` - daemon-resilience program scope-lock and full-topology release-readiness authority.
- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - release-health directive that produced the prior Cursor quarantine.
- `DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626` - prior harden-first/go-live-later posture for Claude and Cursor headless collaboration.
- `bridge/gtkb-wi4885-dispatch-topology-activation-repair-001.md` - approved replacement proposal.
- `bridge/gtkb-wi4885-dispatch-topology-activation-repair-002.md` - Loyal Opposition GO verdict.
- `bridge/gtkb-wi4885-dispatch-topology-activation-012.md` - prior non-activatable GO chain superseded by this repair thread.
- `bridge/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-009.md` - sibling Cursor Agent blocker revision filed in the same dispatch session.

## Files Changed By This Worker

- `scripts/verify_claude_dispatch.py` - added bounded live readiness probing and CLI options.
- `platform_tests/scripts/test_verify_claude_dispatch.py` - added live success and timeout classification tests.
- `platform_tests/scripts/test_harness_parity_phase2.py` - formatted while running the approved format gate; the semantic fixture diff was already present in the dirty worktree before this worker's implementation.
- `bridge/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-009.md` - sibling WI-4888 blocker revision filed before this WI-4885 implementation report.

## Specification-Derived Verification Evidence

| Spec / governing surface | Executed verification evidence | Observed result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4885-dispatch-topology-activation-repair`; `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py status gtkb-wi4885-dispatch-topology-activation-repair`. | Latest status was `GO`; implementation packet hash `sha256:6dc07380f49552f1209da5dacde32014832486464aaffbac03d851ca53cfc4be`; work-intent claim was active. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Report carries forward proposal specs, Project Authorization, Project, Work Item, and target-path evidence. | Existing requirements remained sufficient; no new owner decision was needed. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, `ADR-DISPATCHER-ARCHITECTURE-001` | `groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status --json`; `groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch health --json`. | Dispatcher selects Codex/Cursor/Claude for Prime Builder and Ollama/OpenRouter/Antigravity for Loyal Opposition; health/status currently `WARN` due OpenRouter F runtime failure. |
| `DCL-DISPATCH-ENVELOPE-RULES-001`, `GOV-AUTOMATION-VALUE-VS-COST-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/verify_claude_dispatch.py --json --live --timeout 20`; `groundtruth-kb/.venv/Scripts/python.exe scripts/verify_antigravity_dispatch.py --recipient C --json --live --timeout 60`; `groundtruth-kb/.venv/Scripts/python.exe scripts/verify_cursor_dispatch.py --json --live --timeout 60`. | Claude live probe now classifies timeout; Antigravity live probe fails closed on zero stdout; Cursor fails closed on authentication. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`, `GOV-STANDING-BACKLOG-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/harness_parity_phase2.py --format json --strict`. | Exit `0`; `overall_status: WARN`; `unwaived_release_blocking_gap_count: 0`; remaining unwaived gaps are non-release-blocking event-source gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff check, ruff format check, live readiness probes, dispatch health/status, and this spec-to-test table. | Tests and code-quality gates pass; live topology remains non-terminal due runtime blockers. |

## Commands Run

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4885-dispatch-topology-activation-repair
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py status gtkb-wi4885-dispatch-topology-activation-repair
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verify_claude_dispatch.py platform_tests/scripts/test_verify_cursor_dispatch.py platform_tests/scripts/test_verify_antigravity_dispatch.py platform_tests/scripts/test_harness_parity_phase2.py -q --tb=short --basetemp .gtkb-state/pytest-tmp/wi4885-rerun
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/verify_claude_dispatch.py platform_tests/scripts/test_verify_claude_dispatch.py scripts/verify_cursor_dispatch.py scripts/verify_antigravity_dispatch.py scripts/harness_parity_phase2.py platform_tests/scripts/test_verify_cursor_dispatch.py platform_tests/scripts/test_verify_antigravity_dispatch.py platform_tests/scripts/test_harness_parity_phase2.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/verify_claude_dispatch.py platform_tests/scripts/test_verify_claude_dispatch.py scripts/verify_cursor_dispatch.py scripts/verify_antigravity_dispatch.py scripts/harness_parity_phase2.py platform_tests/scripts/test_verify_cursor_dispatch.py platform_tests/scripts/test_verify_antigravity_dispatch.py platform_tests/scripts/test_harness_parity_phase2.py
groundtruth-kb/.venv/Scripts/python.exe scripts/verify_claude_dispatch.py --json
groundtruth-kb/.venv/Scripts/python.exe scripts/verify_claude_dispatch.py --json --live --timeout 20
groundtruth-kb/.venv/Scripts/python.exe scripts/verify_antigravity_dispatch.py --recipient C --json --live --timeout 60
groundtruth-kb/.venv/Scripts/python.exe scripts/verify_cursor_dispatch.py --json --live --timeout 60
groundtruth-kb/.venv/Scripts/python.exe scripts/harness_parity_phase2.py --format json --strict
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status --json
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch health --json
git diff --check -- scripts/verify_claude_dispatch.py platform_tests/scripts/test_verify_claude_dispatch.py platform_tests/scripts/test_harness_parity_phase2.py bridge/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-009.md
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4885-dispatch-topology-activation-repair --content-file .gtkb-state/bridge-impl-reports/drafts/gtkb-wi4885-dispatch-topology-activation-repair-003.completed.md --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4885-dispatch-topology-activation-repair --content-file .gtkb-state/bridge-impl-reports/drafts/gtkb-wi4885-dispatch-topology-activation-repair-003.completed.md
```

## Observed Results

- Focused pytest: `37 passed, 1 warning in 5.08s`; warning was pytest cache path creation contention under `.pytest_cache`.
- Ruff check: `All checks passed!`
- Ruff format check: `8 files already formatted`.
- Static Claude readiness: exit `0`; `ready: true`; `dispatchable_now: true`; resolved executable `C:\Users\micha\.local\bin\claude.EXE`.
- Live Claude readiness: exit `1`; `dispatchable: true`; `dispatchable_now: false`; timeout after `20.0` seconds for the rendered Claude print-mode command using prompt text `Reply with READY only.`, `--add-dir E:\GT-KB`, and `--output-format json`.
- Live Antigravity readiness: exit `1`; `dispatchable_now: false`; `returncode=0`; `stdout_bytes=0`; `output_recovered=false`.
- Live Cursor readiness: exit `1`; `dispatchable_now: false`; Cursor Agent command `C:\Users\micha\AppData\Local\cursor-agent\agent.CMD`; auth status `unauthenticated`; `cursor_api_key_available=true`.
- Harness parity strict: exit `0`; `overall_status: WARN`; `unwaived_release_blocking_gap_count: 0`; `active_waiver_count: 2`; `retired_waiver_count: 6`.
- Dispatch health/status: `WARN` due `loyal-opposition:F` runtime failure (`subprocess_execution_failed`, exit code `1`) and pending count `1`; no Cursor binary-discovery failure is present.
- `git diff --check`: clean.

## Acceptance Criteria Status

- [x] Non-activatable prior `GO` is superseded by an activatable repair thread.
- [x] Implementation-start authorization succeeds for the repair thread.
- [x] Claude readiness probe supports the approved `--json --live` CLI surface.
- [x] Claude live probe fails closed with bounded timeout classification instead of argument parsing failure.
- [x] Focused readiness tests and code-quality gates pass.
- [x] Harness parity strict has no unwaived release-blocking gaps.
- [ ] Cursor Agent live smoke succeeds.
- [ ] Antigravity live prompt probe returns recoverable stdout.
- [ ] Claude live prompt probe completes within the bounded timeout.
- [ ] Dispatch health/status is fully `PASS` without runtime failures.

## Pre-Filing Preflight Subsection

Candidate-content preflights were run before filing this live `NEW` bridge
implementation report. Expected acceptable result is:

- Applicability preflight: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`.
- ADR/DCL clause preflight: exit `0`; no blocking gaps.

## Risk And Rollback

Risk is limited to overstating runtime readiness. This report explicitly does
not claim full closure while Cursor, Antigravity, Claude, and OpenRouter runtime
evidence remain non-terminal.

Rollback for the code change is to revert `scripts/verify_claude_dispatch.py`
and `platform_tests/scripts/test_verify_claude_dispatch.py`. Rollback is not
needed for `bridge/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-009.md`
because the bridge chain is append-only.

## Loyal Opposition Ask

Verify the Claude readiness probe repair and the executed evidence. Keep the
thread non-terminal unless Loyal Opposition accepts the remaining runtime
blockers as outside the scope of this repair report.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
