REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop Prime Builder session; approval_policy=never; sandbox=danger-full-access

# GT-KB Bridge Revision - WI-4885 Dispatch Topology Activation

bridge_kind: prime_revision
Document: gtkb-wi4885-dispatch-topology-activation
Version: 011
Responds to NO-GO: bridge/gtkb-wi4885-dispatch-topology-activation-010.md
Prior revision: bridge/gtkb-wi4885-dispatch-topology-activation-009.md
Approved proposal: bridge/gtkb-wi4885-dispatch-topology-activation-001.md
Prior GO: bridge/gtkb-wi4885-dispatch-topology-activation-002.md
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4885
target_paths: ["groundtruth.db", "harness-state/harness-registry.json", "config/dispatcher/rules.toml", "harness-state/bridge-substrate.json", "config/harness-parity/phase2-waivers.toml", "scripts/cursor_harness.py", "scripts/verify_cursor_dispatch.py", "scripts/verify_antigravity_dispatch.py", "scripts/cross_harness_bridge_trigger.py", "scripts/harness_parity_phase2.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_harness_parity_phase2.py", "platform_tests/scripts/test_verify_cursor_dispatch.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py"]
Recommended commit type: fix:

## Requirement Sufficiency

Existing requirements sufficient.

The owner has resolved the decision blocker carried by versions 003 through 010. Cursor, Antigravity, and Claude Code must not remain release waivers. This revision supersedes the blocked hold posture with a bounded remediation plan: install or use the current vendor headless tools, repair GT-KB readiness wrappers where local proof shows a wrapper defect, remove waiver treatment from the release gate, and activate each harness only after its readiness probe proves real non-interactive work delivery.

This revision does not itself mutate protected dispatcher configuration or source. It requests Loyal Opposition GO for the implementation slice needed to make the waiver removal executable.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires role-correct bridge lifecycle and a live GO before protected mutations.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires complete governing specification linkage for implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed tests mapped to the linked specifications before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatch targets must be selected through the centralized dispatcher and must be runnable.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher topology changes must use governed dispatcher control surfaces.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatch envelopes must route to eligible, role-correct, non-duplicative targets.
- `GOV-SESSION-ROLE-AUTHORITY-001` - role records govern dispatch routing; interactive role hints do not replace dispatcher authority.
- `DCL-SESSION-ROLE-RESOLUTION-001` - harness role resolution must preserve dispatcher and session-role boundaries.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher state, target eligibility, and runtime proof are architectural release surfaces.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness requires governed verification of release-blocking infrastructure.
- `GOV-AUTOMATION-VALUE-VS-COST-001` - automated dispatch must avoid silent no-op or wasteful repeated launches.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - non-identical harness surfaces may use equivalent fallback mechanics when native parity is unavailable.
- `GOV-STANDING-BACKLOG-001` - release-blocking follow-up items must be tracked instead of left as scratch state.

## Prior Deliberations

- `DELIB-20266276` - daemon-resilience program scope-lock and full-topology release-readiness authority.
- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - release-health directive that produced the prior Cursor quarantine.
- `DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626` - prior harden-first/go-live-later posture for Claude and Cursor headless collaboration.
- `bridge/gtkb-wi4888-release-health-cursor-quarantine-budget-config-004.md` - VERIFIED quarantine entry now superseded by the new owner instruction.
- `bridge/gtkb-wi4885-dispatch-topology-activation-010.md` - latest NO-GO requiring owner direction before topology activation.

## Owner Decisions / Input

- 2026-06-29 owner instruction: "Disregard all past waivers or restrictions on all harnesses. Antigravity is not waived. Claude Code is not waived. Please research and resolve the Cursor and Antigravity dispatchability outage."
- 2026-06-29 owner instruction: "If we need to download additional Gemini CLI or Cursor CLI packages in order to get those harnesses working please do so. I approve adding any missing tools or packages or binaries."

## Investigation Evidence

### Cursor

- Before installation, `python scripts/verify_cursor_dispatch.py --json` failed at `headless Cursor Agent CLI`: no standalone `agent` or `cursor-agent` command was found.
- The installed GUI command using the Cursor `agent` subcommand plus print/output-format flags emitted Electron/Chromium unknown-option warnings and no stdout, so the GUI launcher is not sufficient dispatch evidence.
- The official Cursor Agent installer downloaded from `https://cursor.com/install?win32=true` installed `%LOCALAPPDATA%\cursor-agent`.
- After installation and PATH augmentation, `agent --help` exposes Cursor Agent print mode, output-format, trust, workspace, mode, and force/trust options required for headless dispatch.
- After installation, `python scripts/verify_cursor_dispatch.py --json` reports `ready: true`; `dispatchable_now` remains false because registry/config still carry `can_receive_dispatch=false` and the verifier is Loyal-Opposition-role-specific.
- `agent status` reports `Not logged in`; `agent models` reports authentication required. Cursor activation must fail closed until `agent status --format json` or an equivalent probe proves authentication.
- Owner GUI verification on 2026-06-29 confirms Cursor interactive sessions are healthy and responsive. The remaining blocker is therefore the headless agent authentication/dispatch surface, not model reachability.

### Antigravity

- The legacy `gemini` CLI remains installed, but its non-interactive prompt mode fails for this account path with an unsupported-client message directing migration to Antigravity.
- The official Antigravity installer downloaded from `https://antigravity.google/cli/install.ps1` installed `%LOCALAPPDATA%\agy\bin\agy.exe`.
- `agy --help` confirms the current non-interactive CLI surface is Antigravity print/prompt mode, with timeout, model, workspace-directory, and permission-skip options.
- An `agy` print-mode smoke prompt authenticates via keyring and reaches the backend, but returns exit 0 with no stdout.
- Antigravity's local conversation SQLite store contains the smoke prompt and response string `READY` after the no-stdout run, proving model output exists locally even though print mode did not write it to stdout.
- Logs show repeated attempts to access `/Users/micha/.gemini/antigravity-cli/brain/.../transcript.jsonl` on Windows while the actual app data directory is `C:\Users\micha\.gemini\antigravity-cli`.
- Owner GUI verification on 2026-06-29 confirms Antigravity interactive sessions are healthy and responsive. The remaining blocker is therefore the Windows `agy` print-mode / dispatch-output surface, not model reachability.

### Claude Code

- `claude --version` reports `2.1.183 (Claude Code)`.
- Claude Code non-interactive prompt mode did not return within the quick readiness window and required termination of the exact probe process. Claude Code is therefore not release-dispatchable until a bounded readiness probe proves non-interactive completion.
- Owner GUI verification on 2026-06-29 confirms Claude Code interactive sessions are healthy and responsive. The remaining blocker is therefore the headless Claude Code dispatch surface, not service reachability or account limits.

## Findings Addressed

### Hold for owner decision

Response: resolved. The owner explicitly rejected the prior waiver/hold posture. The implementation must now remove or fail the waiver treatment rather than preserving release readiness through waived gaps.

### Cursor quarantine

Response: partially resolved by package installation. The missing Cursor Agent binary has been installed and the static readiness probe passes. Remaining work is authentication detection and governed dispatcher activation after live output proof.

### Antigravity retirement and Gemini CLI incompatibility

Response: accepted and revised. The Antigravity dispatch path must move off the legacy `gemini` CLI. The implementation may introduce a GT-KB `agy` wrapper that accepts the same prompt/skill contract as other harness wrappers, captures stdout when available, and fails closed or recovers from the local conversation store only when it can prove the response belongs to the current prompt/run.

### Claude Code suspension

Response: accepted as an unwaived release blocker. The implementation may add or tighten a bounded Claude readiness probe, but must not mark Claude receive-capable until headless completion is proven.

## Proposed Implementation Scope

1. Install/use current official headless binaries:
   - Cursor Agent via `%LOCALAPPDATA%\cursor-agent\agent.cmd` or PATH `agent`.
   - Antigravity via `%LOCALAPPDATA%\agy\bin\agy.exe` or PATH `agy`.
2. Update GT-KB wrapper/readiness logic:
   - Make Cursor readiness role-aware and authentication-aware; avoid requiring Loyal Opposition role when the registry assigns Cursor Prime Builder.
   - Add or update an Antigravity headless wrapper around `agy` print mode with hidden Windows process launch, bounded timeout, explicit prompt/run correlation, stdout capture, and a fail-closed fallback for the observed no-stdout Windows print-mode defect.
   - Add or update a bounded Claude Code readiness probe so hanging non-interactive prompt runs classify as release-blocking failures instead of silent waivers.
3. Update the dispatcher/harness registry through governed CLI surfaces, not hand edits:
   - Activate Cursor receive eligibility only after authentication and live output proof.
   - Replace Antigravity's legacy `gemini` argv with the current `agy` wrapper and activate receive eligibility only after live output proof.
   - Keep Claude Code unwaived but non-dispatchable until live readiness passes.
4. Update harness parity and release-readiness evaluation:
   - Remove active release waiver treatment for Cursor, Antigravity, and Claude Code.
   - Convert any remaining failure into explicit release-blocking findings or concrete work-item proposals.
5. Preserve no-window guarantees for every process launch.

## Verification Plan

| Specification | Test or verification command |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `gt bridge dispatch config --json`; `gt bridge dispatch status --json`; `gt bridge dispatch health --json` after activation. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Verify dispatcher eligibility changes are made through `gt bridge dispatch config ...` or canonical harness projection commands, with audit output captured in the implementation report. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Focused dispatcher tests covering multi-target Prime Builder and Loyal Opposition selection without waived Cursor/Antigravity/Claude gaps. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Tests for wrapper parity: Cursor, Antigravity, and Claude readiness probes classify missing auth, missing binary, timeout, no stdout, and success distinctly. |
| `GOV-AUTOMATION-VALUE-VS-COST-001` | Regression tests ensure no repeated silent launches occur for no-output or unauthenticated harnesses. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `python scripts/harness_parity_phase2.py --format json --strict` must fail while any unwaived dispatchability gap remains and pass only after proof-backed activation or explicit owner-approved blocker disposition. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The implementation report must carry these spec links forward and include exact observed outputs for the focused tests plus live readiness probes. |

Focused commands expected after implementation:

```powershell
python scripts\verify_cursor_dispatch.py --json --live
python scripts\verify_antigravity_dispatch.py --recipient C --json --live
python scripts\verify_claude_dispatch.py --json --live
python -m pytest platform_tests\scripts\test_verify_cursor_dispatch.py platform_tests\scripts\test_verify_antigravity_dispatch.py platform_tests\scripts\test_harness_parity_phase2.py -q --tb=short
python -m ruff check scripts\cursor_harness.py scripts\verify_cursor_dispatch.py scripts\verify_antigravity_dispatch.py scripts\cross_harness_bridge_trigger.py scripts\harness_parity_phase2.py platform_tests\scripts\test_verify_cursor_dispatch.py platform_tests\scripts\test_verify_antigravity_dispatch.py platform_tests\scripts\test_harness_parity_phase2.py
python -m ruff format --check scripts\cursor_harness.py scripts\verify_cursor_dispatch.py scripts\verify_antigravity_dispatch.py scripts\cross_harness_bridge_trigger.py scripts\harness_parity_phase2.py platform_tests\scripts\test_verify_cursor_dispatch.py platform_tests\scripts\test_verify_antigravity_dispatch.py platform_tests\scripts\test_harness_parity_phase2.py
gt bridge dispatch health --json
```

## Pre-Filing Preflight Subsection

This completed revision is being filed through `.codex/skills/bridge/helpers/revise_bridge.py file`, which runs:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4885-dispatch-topology-activation --content-file <candidate> --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4885-dispatch-topology-activation --content-file <candidate>`

The helper must refuse to file this revision if either candidate-content preflight fails.

## Risk And Rollback

Risk: Cursor Agent may remain unauthenticated after installation. Rollback is to leave Cursor non-dispatchable and report an explicit release blocker rather than a waiver.

Risk: Antigravity `agy` print mode may continue returning no stdout on Windows. Rollback is to keep Antigravity non-dispatchable and file the upstream/runtime blocker with captured logs and conversation-store evidence; do not route bridge work to it until the wrapper proves output correlation.

Risk: Claude Code may keep hanging in headless mode. Rollback is to keep Claude non-dispatchable and fail the release-health gate with a bounded timeout finding.

Risk: Activating multiple targets can reintroduce console-window or launch storms. Rollback is to revert only dispatcher eligibility through the governed control surface and keep wrapper source changes for diagnosis.

## Acceptance Criteria

- Cursor Agent binary is installed and discovered without relying on the GUI launcher.
- Cursor live readiness distinguishes unauthenticated state from binary absence and does not mark dispatchable until a real response is produced.
- Antigravity uses the current `agy` CLI path instead of legacy `gemini`.
- Antigravity readiness either produces stdout or proves a response through a run-correlated fallback; otherwise it fails closed as an unwaived release blocker.
- Claude Code hanging headless execution is classified by a bounded readiness probe.
- Harness parity strict mode no longer passes because of Cursor, Antigravity, or Claude Code waivers.
- Dispatcher health remains PASS only when every selected target is actually runnable.
