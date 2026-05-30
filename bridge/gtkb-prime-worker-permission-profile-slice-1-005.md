NEW
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Post-Implementation Report - Prime Worker Permission Profile Slice 1

bridge_kind: prime_builder_post_implementation_report
Document: gtkb-prime-worker-permission-profile-slice-1
Version: 005
Author: Prime Builder (Codex harness A)
Date: 2026-05-20 UTC
Implements: `bridge/gtkb-prime-worker-permission-profile-slice-1-004.md`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation started from the live latest `GO` bridge state and preserves bridge dispatch authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed files and report artifacts are under `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries forward the approved proposal's governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification below maps each behavior to executed tests and smokes.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - dispatch-state and bridge artifacts remain the durable traceability surfaces.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - behavior, tests, and bridge report remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the bridge lifecycle advances to post-implementation report for verification.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - the dispatched prompt first line remains unchanged.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` - command flags do not alter prompt emitter authority or canonical mode.
- `GOV-ARTIFACT-APPROVAL-001` - no protected formal narrative artifact was edited.
- `GOV-STANDING-BACKLOG-001` - no bulk backlog or MemBase mutation occurred.
- `.claude/rules/bridge-essential.md` - the cross-harness trigger remains the active dispatch substrate.
- `.claude/rules/prime-builder-role.md` - spawned Prime workers receive authoring tools but not owner-interaction tools.
- `.claude/rules/file-bridge-protocol.md` - report follows file bridge protocol.
- `.claude/rules/codex-review-gate.md` - implementation-start authorization was obtained before source/test edits.

## Claim

Slice 1 is implemented. `_harness_command()` still builds the base argv from `target.invocation_surfaces`, preserving the fail-closed data-driven registry contract. For Claude headless workers only, it now applies the approved permission profile overlay:

```text
--permission-mode acceptEdits --allowed-tools "Read Edit Write Glob Grep Bash TodoWrite NotebookEdit"
```

The Codex branch remains semantically unchanged and receives no permission flags. The overlay is intentionally excluded for non-Claude command handles.

## Changed Files

- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`

No harness-state registry, MemBase, formal artifact, or runtime dispatch-state schema changes were made.

## Implementation Notes

- Added `CLAUDE_WORKER_ALLOWED_TOOLS`.
- Updated `_harness_command()` docstring to document the narrow approved Claude permission overlay and the excluded tool classes.
- Appended `--permission-mode acceptEdits` and `--allowed-tools <authoring list>` only when `target.command_handle == "claude"` and the registry template did not already specify those flags.
- Added command-shape tests proving:
  - Claude branch has `acceptEdits`;
  - Claude allow-list includes `Read`, `Edit`, `Write`, `Glob`, `Grep`, `Bash`, `TodoWrite`, and `NotebookEdit`;
  - Claude allow-list excludes `AskUserQuestion`, `WebFetch`, `WebSearch`, and `mcp__*`;
  - Codex branch remains unchanged;
  - prompt first line remains `::init gtkb <mode>`;
  - permission flags apply only to Claude.

## Exact Command Shape

Command-shape smoke:

```text
claude_cmd=['claude', '-p', '::init gtkb pb\nProceed.', '--add-dir', 'E:\\GT-KB', '--output-format', 'json', '--permission-mode', 'acceptEdits', '--allowed-tools', 'Read Edit Write Glob Grep Bash TodoWrite NotebookEdit']
codex_cmd=['codex', 'exec', '::init gtkb pb\nProceed.', '--cd', 'E:\\GT-KB']
```

## Specification-Derived Verification

| Spec / requirement | Verification evidence |
|---|---|
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - first-line prompt invariant | `test_harness_command_preserves_init_keyword_first_line` passed; command smoke shows prompt unchanged. |
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` - command flags do not alter emitter authority | Same test plus `test_harness_command_codex_unchanged` and exact command smoke. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` - dispatch command changes do not change bridge routing semantics | Full trigger suite passed: 45 tests. Diagnose reported overall `HEALTHY`. |
| `.claude/rules/prime-builder-role.md` - workers can use authoring tools but not owner-interaction tools | Allow-list include/exclude tests passed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all targets in-root | Changed files are under `E:\GT-KB\scripts\` and `E:\GT-KB\platform_tests\scripts\`; report is under `E:\GT-KB\bridge\`. |
| `GOV-STANDING-BACKLOG-001` - not a bulk backlog operation | No MemBase or backlog mutation was performed. |

## Verification Commands

Authorization:

```text
python scripts\implementation_authorization.py begin --bridge-id gtkb-prime-worker-permission-profile-slice-1
```

Observed: latest bridge status `GO`; proposal file `bridge/gtkb-prime-worker-permission-profile-slice-1-003.md`; GO file `bridge/gtkb-prime-worker-permission-profile-slice-1-004.md`; packet hash `sha256:1c30e800e0ace2e2eddbb9789fab1ef9e4b96633ecd816e8bfd582a6ee84a6c3`.

Focused command-shape tests:

```text
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short -k "harness_command"
```

Observed: `8 passed, 37 deselected`.

Full trigger suite:

```text
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
```

Observed: `45 passed`.

Ruff and diff checks:

```text
python -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
python -m ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
git diff --check -- scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py
```

Observed: ruff check passed; format check passed; diff check passed.

Diagnose:

```text
python scripts\cross_harness_bridge_trigger.py --diagnose
```

Observed: `HEALTHY`; both recipients currently suppressed by active-session detection by design, with dispatch state current.

Command-shape smoke:

```text
@'
import importlib.util
import sys
from pathlib import Path

script = Path('scripts/cross_harness_bridge_trigger.py').resolve()
spec = importlib.util.spec_from_file_location('cross_harness_bridge_trigger_smoke', script)
mod = importlib.util.module_from_spec(spec)
sys.modules['cross_harness_bridge_trigger_smoke'] = mod
spec.loader.exec_module(mod)
root = Path('E:/GT-KB')
prompt = '::init gtkb pb\nProceed.'
claude = mod.DispatchTarget(
    needed_role_label='prime-builder',
    harness_id='B',
    command_handle='claude',
    canonical_mode='pb',
    invocation_surfaces={'headless': {'argv': ['claude', '-p', '{{PROMPT}}', '--add-dir', '{{PROJECT_ROOT}}', '--output-format', 'json']}},
)
codex = mod.DispatchTarget(
    needed_role_label='loyal-opposition',
    harness_id='A',
    command_handle='codex',
    canonical_mode='lo',
    invocation_surfaces={'headless': {'argv': ['codex', 'exec', '{{PROMPT}}', '--cd', '{{PROJECT_ROOT}}']}},
)
print('claude_cmd=' + repr(mod._harness_command(claude, prompt, root)))
print('codex_cmd=' + repr(mod._harness_command(codex, prompt, root)))
'@ | python -
```

Observed: command output shown in `## Exact Command Shape`.

## Manual End-To-End Smoke

I did not file a dummy NEW bridge item or force a live worker dispatch for this slice. That would create artificial bridge work and fight the current active-session suppression state. `--diagnose` shows the trigger is healthy and suppressed by design while active sessions are present. End-to-end spawned-worker delivery remains explicitly assigned to Slice 4; this slice verifies command construction deterministically and keeps the live trigger state healthy.

## Residual Risk

The implementation reconciles the older proposal wording with the current data-driven dispatch architecture by applying a narrow Claude overlay after registry template substitution rather than replacing registry-driven command building. This preserves the WI-3344 fail-closed projection behavior while satisfying the approved Prime-worker permission profile.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
