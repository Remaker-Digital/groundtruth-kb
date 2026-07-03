NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex interactive Prime Builder; implementation-start packet sha256:18958788a237e19c9c8baf3ab019155eb6b56e349f09c3d0d47a0dc27aaac0f7

# Implementation Report - gtkb-wi4929-codex-sessionstart-timeout-alignment - 013

bridge_kind: implementation_report
Document: gtkb-wi4929-codex-sessionstart-timeout-alignment
Version: 013 (NEW; implementation report after resumed post-GO NO-GO)
Date: 2026-07-03 UTC
Responds to: bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-012.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4929

target_paths: [".codex/gtkb-hooks/run_py_no_window.py", "platform_tests/scripts/test_codex_no_window_timeout_alignment.py"]
implementation_scope: source,test_addition,hook_upgrade
requires_verification: true
kb_mutation_in_scope: false

## Implementation Claim

WI-4929 is implemented. The Codex no-window Python hook wrapper now gives `.codex/gtkb-hooks/session_start_dispatch.py` the same startup-service timeout budget used by `scripts/session_start_dispatch_core.py` when no explicit `GTKB_CODEX_HOOK_CHILD_TIMEOUT_SECONDS` override is present, while preserving the short 10 second default for ordinary hook children.

The implementation stays within the approved two-file scope from `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-005.md` and GO `-006`:

- `.codex/gtkb-hooks/run_py_no_window.py`
- `platform_tests/scripts/test_codex_no_window_timeout_alignment.py`

## Implementation Details

- Imported `STARTUP_SERVICE_TIMEOUT_ENV` and `STARTUP_SERVICE_TIMEOUT_SECONDS` from `scripts/session_start_dispatch_core.py`, keeping the SessionStart timeout budget tied to the shared startup-service authority.
- Added `_is_session_start_dispatch_command()` so only commands targeting `session_start_dispatch.py` under `gtkb-hooks` receive the longer startup budget.
- Added `_startup_dispatch_timeout_seconds()` with the same valid/invalid/non-positive fallback behavior as the core startup-service timeout resolver.
- Changed `_run_child()` to pass the child command into `_child_timeout_seconds(command)` so timeout choice can be command-specific.
- Added focused regression tests covering default SessionStart timeout, startup-service env override, invalid override fallback, ordinary-child default preservation, and explicit wrapper override precedence.

## Implementation Authorization Evidence

- Work-intent claim: `python scripts\bridge_claim_cli.py claim gtkb-wi4929-codex-sessionstart-timeout-alignment --session-id 019f247b-4dc8-7b32-a2ab-25839614d33f --ttl-seconds 3600`
  - Observed: acquired claim for `gtkb-wi4929-codex-sessionstart-timeout-alignment`, acting_role `prime-builder`, project `PROJECT-GTKB-RELIABILITY-FIXES`, expires `2026-07-03T17:08:41Z`.
- Implementation authorization: `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi4929-codex-sessionstart-timeout-alignment --session-id 019f247b-4dc8-7b32-a2ab-25839614d33f`
  - Observed: authorized packet `sha256:18958788a237e19c9c8baf3ab019155eb6b56e349f09c3d0d47a0dc27aaac0f7`, GO file `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-006.md`, latest status `NO-GO`, active PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, targets exactly the two approved files.

## Specification Links

- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Specification-Derived Verification

| Spec | Verification | Observed result |
| --- | --- | --- |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_codex_no_window_timeout_alignment.py -q --tb=short` | `7 passed`; proves `session_start_dispatch.py` receives 150.0 seconds by default and startup-service override values when present. |
| `GOV-RELIABILITY-FAST-LANE-001` | Confirmed implementation remains a small defect/reliability fix under two approved target paths. | Scope unchanged from GO `-006`; no public API/CLI/deployment changes. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start packet command above. | Authorized true; active PAUTH and active WI membership accepted. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Implementation-start packet command above. | Packet contains active project, active PAUTH, WI-4929, and exact target paths. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | File this report as the next numbered bridge file through the governed Codex bridge writer. | This report is intended to become `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-013.md` with status `NEW`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Machine-readable `Project Authorization`, `Project`, `Work Item`, and `target_paths` lines are present above. | Present. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Focused wrapper tests import the live Codex no-window wrapper and exercise its timeout resolver. | `7 passed`; ordinary child default remains 10.0 seconds and explicit wrapper override still wins. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report carries spec-to-test mapping plus exact command evidence. | Present in this section. |

## Commands Executed

```text
groundtruth-kb\.venv\Scripts\ruff.exe check .codex/gtkb-hooks/run_py_no_window.py platform_tests/scripts/test_codex_no_window_timeout_alignment.py
```

Observed result: `All checks passed!`

```text
groundtruth-kb\.venv\Scripts\ruff.exe format --check .codex/gtkb-hooks/run_py_no_window.py platform_tests/scripts/test_codex_no_window_timeout_alignment.py
```

Observed result: `2 files already formatted`

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_codex_no_window_timeout_alignment.py -q --tb=short
```

Observed result: `7 passed, 1 warning in 0.18s`

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_session_start_dispatch_core.py -q --tb=short
```

Observed result: `9 passed, 1 warning in 0.12s`

Additional diagnostic, non-gating for this WI:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_session_start_dispatch_core.py platform_tests/scripts/test_workstream_focus_hook_parity.py -q --tb=short
```

Observed result: `14 passed, 2 failed, 1 warning`. The two failures are pre-existing parity-fixture expectations in `platform_tests/scripts/test_workstream_focus_hook_parity.py` that still look for literal `workstream-focus` entries in `.codex/hooks.json`; current hooks route through `run_py_no_window --batch ...`. That drift is outside WI-4929's approved two-file timeout scope and was not changed here.

## Acceptance Status

- SessionStart child gets startup-service headroom by default: met.
- Ordinary children keep short wrapper timeout: met.
- Explicit `GTKB_CODEX_HOOK_CHILD_TIMEOUT_SECONDS` override remains authoritative: met.
- Focused regression coverage added: met.
- Ruff check and format check pass on changed files: met.
- Shared startup-service timeout core remains green: met.

## Files Changed

- `.codex/gtkb-hooks/run_py_no_window.py`
- `platform_tests/scripts/test_codex_no_window_timeout_alignment.py`

## Risks / Rollback

Risk is low. The longer timeout is conditional on launching `session_start_dispatch.py`; ordinary hook children still default to 10 seconds. Rollback is a normal revert of the two changed files plus removal of this implementation report from future reliance; bridge files themselves remain append-only.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing owner decision for reliability fast-lane work under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-005.md` - approved REVISED proposal with active PAUTH/project metadata.
- `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-006.md` - GO authorizing implementation.
- `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-012.md` - latest NO-GO confirming the approved fix remained unimplemented and that the GO remains the valid technical scope.

## Pre-Filing Preflight Subsection

Candidate preflights were run against this completed report content before live filing:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4929-codex-sessionstart-timeout-alignment --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-wi4929-codex-sessionstart-timeout-alignment-013.completed.md
```

Observed applicability result:

- packet_hash: `sha256:4e6d556446d77684102580d65e99db1eeb36b3e1b20a2f3f76e50a400bc850b6`
- content_source: `pending_content`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4929-codex-sessionstart-timeout-alignment --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-wi4929-codex-sessionstart-timeout-alignment-013.completed.md
```

Observed clause result:

- must_apply: 3
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Exit code: 0