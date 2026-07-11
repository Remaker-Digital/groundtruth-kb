NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4ace-e667-7030-b632-1cf002c1a0f7
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive session; approval_policy=never; role=prime-builder
author_metadata_source: Codex Desktop system runtime context; CODEX_THREAD_ID

# GT-KB Bridge Implementation Report - WI-5118 startup-input gate fresh-start-only

bridge_kind: implementation_report
Document: gtkb-wi5118-startup-gate-fresh-start-only
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5118-startup-gate-fresh-start-only-002.md
Companion GO: bridge/gtkb-wi5118-startup-gate-auq-completion-scope-amendment-002.md
Approved proposal: bridge/gtkb-wi5118-startup-gate-fresh-start-only-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5118-STARTUP-GATE-20260710
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5118
Recommended commit type: fix:

## Implementation Claim

WI-5118's implementation is present in the workspace and its focused
state-transition coverage passes. Commit `b74cb6c6` delivers the parent
content-free lifecycle-state repair: no prompt preview is persisted, matching
completed-AUQ acknowledgements clear only their own guard, and satisfied state
cannot wedge ordinary tool use.

The independently GO-approved companion adds the missing AUQ event path:
`scripts/session_start_dispatch_core.py` supplies only a canonical session UUID
to the startup guard environment, while the canonical Claude PostToolUse hook
acknowledges a completed `AskUserQuestion` by session ID only. Its generated
template is byte-identical. No owner prompt or AUQ-answer content is sent to,
or stored by, the acknowledgement path.

The remaining five companion paths are deliberately unstaged because the
shared worktree's mandatory pre-commit inventory gate is currently blocked by
unrelated harness-state/inventory drift. This is not a claim of readiness for
VERIFIED; this report requests an independent disposition of the recorded
external finalization blockers.

## Specification Links

- `DCL-STARTUP-GATE-FRESH-START-ONLY-001`
- `GOV-SESSION-SELF-INITIALIZATION-001`
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

- `DELIB-202666076` authorizes the bounded WI-5118 fresh-start-only
  remediation under the parent PAUTH.
- `DELIB-20260710-WI5118-PAUTH-SCOPE-AMENDMENT-APPROVAL` authorizes the exact
  five-path SessionStart/AUQ-completion expansion carried by the companion GO.
- No new owner decision is asserted by this report. The blocked finalization
  must not be bypassed by sweeping `groundtruth.db`,
  `harness-state/harness-registry.json`, or another session's inventory work.

## Prior Deliberations

- `bridge/gtkb-wi5118-startup-gate-fresh-start-only-001.md` - approved parent
  proposal.
- `bridge/gtkb-wi5118-startup-gate-fresh-start-only-002.md` - parent GO and
  its binding verification conditions.
- `bridge/gtkb-wi5118-startup-gate-auq-completion-scope-amendment-002.md` -
  independent GO for the exact five-path AUQ carrier and acknowledgement scope.
- `DELIB-202666019` - WI-5083 continuation behavior preserved while the
  remaining AUQ-completion defect is addressed.

## Specification-Derived Verification

| Governing surface | Executed evidence | Result |
| --- | --- | --- |
| `DCL-STARTUP-GATE-FRESH-START-ONLY-001` | `test_workstream_focus.py` covers fresh arm, ordinary clear, matching/mismatching AUQ acknowledgement, repeat acknowledgement, resumed state, and content-free serialization. | PASS: 75 passed, 3 skipped, 1 deselected. |
| `GOV-SESSION-SELF-INITIALIZATION-001` | `test_session_self_initialization_startup_gate_rearm.py` exercises lifecycle re-arm behavior. | PASS: 6 included in the combined 27 passed. |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | `test_session_start_dispatch_core.py` checks valid, absent, and malformed session IDs and strips stale inherited guard IDs. | PASS: 18 included in the combined 27 passed. |
| Parent AUQ-completion condition and companion scope GO | `test_owner_decision_capture.py` checks completed vs incomplete AUQ handling and canonical/template byte parity. | PASS: 3 included in the combined 27 passed. |
| `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Required global parity test and Codex hook-parity checker were run. | BLOCKED by unrelated active harness-topology and Codex-hook configuration drift, detailed below. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Both parent and companion claims were held by this Prime session; each implementation authorization `begin` succeeded before its protected edits. | PASS. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries the parent and companion governing specifications forward with a clause-to-command/result mapping. | PASS. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | The parent latest GO, companion GO, matching claims, and governed implementation-report writer are cited and used. | PASS. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused specification-derived suites and separate lint/format gates were run on all changed Python paths. | PASS for source-level coverage; finalization remains blocked. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All implementation paths are in `E:\GT-KB`; the companion was independently proposed and GO-approved before implementation. | PASS. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\hooks\test_workstream_focus.py -q --tb=short --basetemp .harness-tmp\wi5118-parent-full -k "not test_detect_counterpart_state_uses_project_root_paths_when_provided"`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_session_self_initialization_startup_gate_rearm.py platform_tests\scripts\test_session_start_dispatch_core.py platform_tests\hooks\test_owner_decision_capture.py -q --tb=short --basetemp .harness-tmp\wi5118-combined`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check` on the nine parent-plus-companion changed Python paths.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check` on the same nine paths.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_protocol_parity.py -q --tb=short --basetemp .harness-tmp\wi5118-parity`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\check_codex_hook_parity.py`
- Staged-scope safety gates: `scripts\scan_secrets.py --staged`, `scripts\check_narrative_artifact_evidence.py --staged`, `scripts\check_ruff_format.py --staged`, and `scripts\check_protected_commit_authorization.py --staged`.

## Observed Results

- Parent focused lifecycle suite: `75 passed, 3 skipped, 1 deselected`.
  The deselected baseline assertion assumes the pytest base temp is outside the
  project; mandatory `--basetemp .harness-tmp\...` necessarily places it under
  `E:\GT-KB` and is unrelated to WI-5118 behavior.
- Combined lifecycle, SessionStart, and PostToolUse suite: `27 passed`.
- `ruff check` and `ruff format --check`: PASS on all nine changed Python
  paths.
- Staged secret scan: 0 potential secrets. Narrative evidence, ruff-format,
  and protected-commit authorization gates: PASS.

## External Finalization Blockers

1. `platform_tests/scripts/test_cross_harness_protocol_parity.py` currently
   fails 2 of 7 tests before exercising a WI-5118-specific parity assertion:
   live dispatchable harnesses are `{'B', 'H'}` while that concurrently changed
   test expects `{'A', 'C', 'D', 'F'}`; its identity expectation also omits
   live `G` and `H`. The test has an active foreign two-line diff and the
   corresponding `harness-state` changes are not WI-5118 scope.
2. `scripts/check_codex_hook_parity.py` fails on unrelated Codex configuration:
   `[features].hooks = true`, formal-approval and workstream PreToolUse entries,
   UserPromptSubmit lifecycle registration, and role-aware wrap-up dispatch are
   absent from `.codex/config.toml`/`.codex/hooks.json`. Neither file is an
   approved WI-5118 target.
3. The mandatory pre-commit inventory check fails when the companion's
   `.claude/hooks/owner-decision-capture.py` is staged because the shared live
   inventory differs from its committed baseline at `harnesses`,
   `repo_configured_surfaces`, and `role_by_harness_compatibility`. Adding
   bridge evidence cannot clear this independent material-drift block. No
   inventory, registry, or database artifact was staged or altered for this
   report.

## Files Changed

Committed parent slice (`b74cb6c6`):

- `scripts/workstream_focus.py`
- `scripts/session_self_initialization.py`
- `platform_tests/hooks/test_workstream_focus.py`
- `platform_tests/scripts/test_session_self_initialization_startup_gate_rearm.py`

Uncommitted companion slice, authorized by the companion GO:

- `scripts/session_start_dispatch_core.py`
- `.claude/hooks/owner-decision-capture.py`
- `groundtruth-kb/templates/hooks/owner-decision-capture.py`
- `platform_tests/scripts/test_session_start_dispatch_core.py`
- `platform_tests/hooks/test_owner_decision_capture.py`

The original wrapper targets `.codex/gtkb-hooks/session_start_dispatch.py` and
`.claude/hooks/session_start_dispatch.py` do not need a direct edit: both reach
the shared SessionStart core. Their global parity evidence is nevertheless
blocked by item 1 above.

## Risk And Rollback

The contained implementation is reversible by reverting `b74cb6c6` and the
five companion paths as one scoped change after the shared-tree gate is clean.
No owner content was added to lifecycle state. The current risk is governance
and finalization accuracy, not a claimed behavioral regression: a commit or
VERIFIED verdict before the global parity and inventory gates become clean
would misrepresent the repository state.

## Loyal Opposition Asks

1. Review the source-level WI-5118 evidence and the independently GO-approved
   companion scope.
2. Do not issue VERIFIED while the required parity and finalization gates fail.
   Issue an evidence-based NO-GO that preserves the focused passing evidence
   and identifies the owning topology/inventory repair route, unless live state
   has changed and the listed commands now pass.

## Recommended Commit Type

Recommended commit type: `fix:`. The work repairs the fresh-start-only
startup-input gate and its AUQ-completion acknowledgement path; it adds no new
product capability.
