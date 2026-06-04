NEW

author_identity: Codex Loyal Opposition bridge repair
author_harness_id: A
author_session_context_id: codex-lo-2026-06-04T18-33Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop, bridge-function repair under GO authorization

# Implementation Report - Mode-Switch Validator Hook Matcher Shape Fix

bridge_kind: implementation_report
Document: gtkb-mode-switch-validator-hook-matcher-shape-fix
Version: 003
Author: Codex Loyal Opposition bridge repair (harness A)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-mode-switch-validator-hook-matcher-shape-fix-002.md
Implementation Verdict Requested: VERIFIED

## Summary

Implemented the GO-scoped validator repair.

`validate_bridge_substrate()` now detects `cross_harness_bridge_trigger.py`
registrations through both supported hook shapes:

- flat event entries with a direct `command` key;
- nested matcher-wrapper entries whose command dicts live inside a wrapper
  `hooks` list.

The targeted test module now includes a nested matcher-wrapper fixture for both
`.claude/settings.json` and `.codex/hooks.json`.

After the source fix, the existing pending substrate transaction applied
through the canonical `gt mode apply-pending` path. The live bridge substrate is
now `cross_harness_trigger`.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py`
- `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py`
- `harness-state/bridge-substrate.json` via `gt mode apply-pending`
- `.gtkb-state/mode-switches/pending/20260604T181005Z-55543364.json` moved by
  the canonical command to
  `.gtkb-state/mode-switches/applied/20260604T181005Z-55543364.json`

## Spec-Derived Verification

### SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001

Command:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\groundtruth_kb\test_mode_switch_bridge_substrate_validation.py -q --tb=short --no-header -p no:cacheprovider
```

Observed result:

```text
collected 3 items
3 passed in 0.23s
```

### Static Check

Command:

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\mode_switch\validation.py platform_tests\groundtruth_kb\test_mode_switch_bridge_substrate_validation.py
```

Observed result:

```text
All checks passed!
```

Command:

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format groundtruth-kb\src\groundtruth_kb\mode_switch\validation.py platform_tests\groundtruth_kb\test_mode_switch_bridge_substrate_validation.py
```

Observed result:

```text
2 files left unchanged
```

### Substrate Application

Command:

```text
groundtruth-kb\.venv\Scripts\gt.exe mode apply-pending
```

Observed result:

```text
[
  {
    "pending_path": ".gtkb-state\\mode-switches\\pending\\20260604T181005Z-55543364.json",
    "applied": true,
    "error": null,
    "applied_path": ".gtkb-state\\mode-switches\\applied\\20260604T181005Z-55543364.json"
  }
]
```

Live substrate file after canonical application:

```json
{
  "applied_at": "2026-06-04T18:36:29.502876Z",
  "applied_by": "B",
  "substrate": "cross_harness_trigger"
}
```

### Bridge Dispatch Health

Command:

```text
groundtruth-kb\.venv\Scripts\gt.exe status --startup --json
```

Observed bridge-dispatch evidence:

```text
bridge-dispatch: PASS
dispatch_state.updated_at: 2026-06-04T18:36:56+00:00
.claude/settings.json cross_harness_trigger_registered: true
.codex/hooks.json cross_harness_trigger_registered: true
trigger_script_exists: true
```

Overall status remains `WARN` because of unrelated resource-registry/dashboard
state, not because of bridge dispatch.

## Residual Risk

This implementation was performed by Loyal Opposition under the bridge-function
repair exception after a GO verdict because the broken substrate was preventing
normal bridge dispatch. A separate verifier should review this report before
marking the thread VERIFIED.

## Owner Action Required

None.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
