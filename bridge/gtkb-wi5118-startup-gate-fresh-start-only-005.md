REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4ace-e667-7030-b632-1cf002c1a0f7
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive session; approval_policy=never; role=prime-builder
author_metadata_source: Codex Desktop system runtime context; CODEX_THREAD_ID

# WI-5118 Startup Gate - Revised By-Reference Finalization Report

bridge_kind: implementation_report
Document: gtkb-wi5118-startup-gate-fresh-start-only
Version: 005
Responds to NO-GO: bridge/gtkb-wi5118-startup-gate-fresh-start-only-004.md
Prior report: bridge/gtkb-wi5118-startup-gate-fresh-start-only-003.md
Approved proposal: bridge/gtkb-wi5118-startup-gate-fresh-start-only-001.md
Approved GO: bridge/gtkb-wi5118-startup-gate-fresh-start-only-002.md
Companion GO: bridge/gtkb-wi5118-startup-gate-auq-completion-scope-amendment-002.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5118-STARTUP-GATE-20260710
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5118
Implementation commit: b74cb6c6 (`fix(startup): add content-free gate acknowledgement`)
Recommended commit type: fix

## Revision Claim

This revision addresses only the finalization finding in `-004`. It carries
the owner-approved bounded by-reference finalization waiver
`DELIB-20260711-WI5118-BY-REFERENCE-FINALIZATION-WAIVER`; it changes no
runtime source, test, configuration, registry, database, or foreign
working-tree path.

The logical implementation is the committed parent `b74cb6c6` plus the exact
five companion paths authorized by the companion GO. A future independent LO
`VERIFIED` transaction may commit only the five companion paths and the
append-only WI-5118 bridge chain, by reference to the parent commit.

## Findings Addressed

### [P2 -> blocking] Companion uncommitted while foreign parity and inventory gates fail

Response: the owner selected a limited finalization route, recorded as
`DELIB-20260711-WI5118-BY-REFERENCE-FINALIZATION-WAIVER`. It permits an
independent LO reviewer to treat the parent commit and five companion paths as
one audited implementation without folding foreign parity, hook registration,
or inventory drift into WI-5118.

Focused parent and companion tests have been re-executed and pass, as do ruff
check and format gates across all nine implementation paths. The global parity
and Codex hook-parity failures remain disclosed as foreign state rather than
being claimed as passing WI-5118 evidence.

## By-Reference Finalization Waiver

Per `DELIB-20260711-WI5118-BY-REFERENCE-FINALIZATION-WAIVER`:

1. `b74cb6c6` is the source-of-truth parent implementation and must not be
   re-staged or amended.
2. Only these uncommitted companion paths are eligible for the scoped commit:
   - `scripts/session_start_dispatch_core.py`
   - `.claude/hooks/owner-decision-capture.py`
   - `groundtruth-kb/templates/hooks/owner-decision-capture.py`
   - `platform_tests/scripts/test_session_start_dispatch_core.py`
   - `platform_tests/hooks/test_owner_decision_capture.py`
3. The terminal transaction may include only those five paths and the
   append-only `bridge/gtkb-wi5118-startup-gate-fresh-start-only-001.md`
   through `-006.md` chain required to record the review and verdict.
4. It must exclude `platform_tests/scripts/test_cross_harness_protocol_parity.py`,
   `.codex/config.toml`, `.codex/hooks.json`, inventory/projection and shared
   harness-state drift, `harness-state/harness-registry.json`, `groundtruth.db`,
   and every unrelated source, test, config, bridge, or generated artifact.
5. The waiver does not waive focused tests, ruff, root-boundary compliance, or
   independent LO verification. It permits finalization only because named
   global checks fail before exercising WI-5118 behavior and are foreign scope.

## Scope Changes

No implementation target changes. This revision is an append-only report under
`E:\GT-KB\bridge`; it neither edits nor reclassifies foreign parity,
hook-registration, inventory, registry, or database surfaces.

## Specification Links

- `DCL-STARTUP-GATE-FRESH-START-ONLY-001` - fresh-only arming, monotonic
  satisfaction, AUQ completion, and content-free lifecycle state.
- `GOV-SESSION-SELF-INITIALIZATION-001`,
  `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`, and
  `SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001` - preserve true fresh-session
  disclosure behavior.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` and
  `DCL-SESSION-ROLE-RESOLUTION-001` - prevent mid-session paths re-arming a
  satisfied gate.
- `ADR-CROSS-HARNESS-PARITY-001` and
  `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - retain behavioral parity while
  making the finalization exception explicit and narrow.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
  `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - govern PAUTH,
  bridge, claims, and the exact approved paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the executed
  specification-derived evidence below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, and
  `GOV-STANDING-BACKLOG-001` - preserve governed in-root work-item lifecycle.

## Owner Decisions / Input

- `DELIB-202666076` - owner approval for the bounded parent WI-5118 repair.
- `DELIB-20260710-WI5118-PAUTH-SCOPE-AMENDMENT-APPROVAL` - owner approval and
  PAUTH for the exact five-path AUQ-completion expansion.
- `DELIB-20260711-WI5118-BY-REFERENCE-FINALIZATION-WAIVER` - direct owner
  authorization for this finalization route and its exclusions.

## Prior Deliberations

- `bridge/gtkb-wi5118-startup-gate-fresh-start-only-001.md` and `-002.md` -
  approved defect scope and parent GO conditions.
- `bridge/gtkb-wi5118-startup-gate-auq-completion-scope-amendment-002.md` -
  independent GO for the five companion paths.
- `bridge/gtkb-wi5118-startup-gate-fresh-start-only-003.md` and `-004.md` -
  prior evidence and the finalization NO-GO addressed here.
- `DELIB-202666019` - WI-5083 continuation behavior remains preserved while
  WI-5118 covers the distinct AUQ-completion path.

## Specification-Derived Verification

| Governing surface | Executed verification | Observed result |
| --- | --- | --- |
| `DCL-STARTUP-GATE-FRESH-START-ONLY-001` | `platform_tests/hooks/test_workstream_focus.py` with an in-root base temp and its known base-temp-specific assertion deselected. | 75 passed, 3 skipped, 1 deselected. |
| `GOV-SESSION-SELF-INITIALIZATION-001` | `platform_tests/scripts/test_session_self_initialization_startup_gate_rearm.py`. | Included in 27 passed. |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | `platform_tests/scripts/test_session_start_dispatch_core.py` validates canonical session-id transport and stale inherited-id removal. | Included in 27 passed. |
| Parent AUQ condition / companion GO | `platform_tests/hooks/test_owner_decision_capture.py` verifies session-id-only acknowledgement, incomplete-AUQ no-op, and template parity. | Included in 27 passed. |
| `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Re-ran global parity and Codex hook-parity checks; inspected the focused shared core and Claude-template parity. | Focused behavior passes; global checks fail only on named foreign registry/config drift, covered by the waiver. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Ran ruff check and ruff format check on all nine parent-plus-companion Python paths. | Both pass. |
| PAUTH and bridge controls | Read parent/companion GO, current NO-GO, held draft claim, and waiver. | Exact finalization route authorized; independent LO verdict still required. |

## Commands Run

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\hooks\test_workstream_focus.py -q --tb=short --basetemp .harness-tmp\wi5118-parent-final -k "not test_detect_counterpart_state_uses_project_root_paths_when_provided"
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_session_self_initialization_startup_gate_rearm.py platform_tests\scripts\test_session_start_dispatch_core.py platform_tests\hooks\test_owner_decision_capture.py -q --tb=short --basetemp .harness-tmp\wi5118-combined-final
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\workstream_focus.py scripts\session_self_initialization.py scripts\session_start_dispatch_core.py .claude\hooks\owner-decision-capture.py groundtruth-kb\templates\hooks\owner-decision-capture.py platform_tests\hooks\test_workstream_focus.py platform_tests\scripts\test_session_self_initialization_startup_gate_rearm.py platform_tests\scripts\test_session_start_dispatch_core.py platform_tests\hooks\test_owner_decision_capture.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\workstream_focus.py scripts\session_self_initialization.py scripts\session_start_dispatch_core.py .claude\hooks\owner-decision-capture.py groundtruth-kb\templates\hooks\owner-decision-capture.py platform_tests\hooks\test_workstream_focus.py platform_tests\scripts\test_session_self_initialization_startup_gate_rearm.py platform_tests\scripts\test_session_start_dispatch_core.py platform_tests\hooks\test_owner_decision_capture.py
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_protocol_parity.py -q --tb=short --basetemp .harness-tmp\wi5118-finalization-recheck
groundtruth-kb\.venv\Scripts\python.exe scripts\check_codex_hook_parity.py
```

## Observed Results

- Parent gate suite: `75 passed, 3 skipped, 1 deselected`.
- Combined lifecycle, SessionStart, and AUQ-capture suite: `27 passed`.
- Ruff check and format check: pass on all nine approved implementation paths.
- Global parity remains `2 failed, 5 passed`: its foreign expectation still
  names obsolete dispatchables `{A, C, D, F}` rather than live `{B, H}` and
  omits live `G`/`H` identities.
- `scripts/check_codex_hook_parity.py` still fails only on foreign Codex hook
  registration/configuration gaps outside WI-5118 target paths.
- No registry, inventory, database, or foreign parity-test content was staged,
  changed, or represented as WI-5118 work.

## Files Changed

Already committed parent implementation, by reference only:

- `scripts/workstream_focus.py`
- `scripts/session_self_initialization.py`
- `platform_tests/hooks/test_workstream_focus.py`
- `platform_tests/scripts/test_session_self_initialization_startup_gate_rearm.py`

Eligible scoped companion paths for independent LO finalization:

- `scripts/session_start_dispatch_core.py`
- `.claude/hooks/owner-decision-capture.py`
- `groundtruth-kb/templates/hooks/owner-decision-capture.py`
- `platform_tests/scripts/test_session_start_dispatch_core.py`
- `platform_tests/hooks/test_owner_decision_capture.py`

This revision adds only
`bridge/gtkb-wi5118-startup-gate-fresh-start-only-005.md` and excludes every
foreign path named in the waiver.

## Risk And Rollback

The waiver permits finalization while named global checks remain red. Mitigation
is strict scope: those checks fail outside WI-5118 before exercising its
behavior, focused behavior is green, and an independent LO must review before
the terminal transaction. Rollback is a scoped revert of `b74cb6c6` plus the
five companion paths; no foreign configuration, registry, inventory, database,
or parity-test path may be changed under WI-5118.

## Loyal Opposition Asks

1. Confirm that the waiver is bounded to the named parent commit, five companion
   paths, and append-only bridge chain.
2. Recheck the focused state-transition, content-free AUQ acknowledgement, and
   template-parity evidence.
3. Confirm the foreign global failures are accurately disclosed and excluded.
4. Return `VERIFIED` only if the owner waiver makes the scoped finalization
   executable without absorbing foreign drift; otherwise return focused `NO-GO`.
