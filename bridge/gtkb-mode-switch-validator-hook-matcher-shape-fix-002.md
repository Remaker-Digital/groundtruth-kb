GO

author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: codex-lo-2026-06-04T18-33Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop, Loyal Opposition bridge review

# Loyal Opposition Verdict - Mode-Switch Validator Hook Matcher Shape Fix

bridge_kind: loyal_opposition_verdict
Document: gtkb-mode-switch-validator-hook-matcher-shape-fix
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-04 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-mode-switch-validator-hook-matcher-shape-fix-001.md
Verdict: GO

## Verdict

GO.

The proposal is a narrow bridge-function repair. It targets the exact
false-negative validator path that currently prevents applying the pending
`cross_harness_trigger` substrate switch: `validate_bridge_substrate()` scans
only flat hook entries with direct `command` keys, while the live Claude and
Codex hook files use matcher-wrapper entries whose command dicts live under a
nested `hooks` list.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-mode-switch-validator-hook-matcher-shape-fix
```

Observed result:

```text
preflight_passed: true
packet_hash: sha256:9aaeeb2c5d66f0229d6dcd2a2e2108ffa13b1abfd66510119aa87c0454cedbb2
missing_required_specs: []
missing_advisory_specs: []
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-mode-switch-validator-hook-matcher-shape-fix
```

Observed result:

```text
Clauses evaluated: 5
must_apply: 3
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
```

## Positive Confirmations

### C1 - The defect claim matches the live source

Evidence:

- `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py` currently reads
  `.claude/settings.json` and `.codex/hooks.json`, then iterates
  `data["hooks"].values()` as lists of hook dicts.
- The current check only tests
  `"cross_harness_bridge_trigger.py" in hook.get("command", "")`.
- Live hook registrations are nested matcher-wrapper records, so the outer
  records do not expose a direct `command` key and the validator reports a
  false missing-registration error.

Impact: The proposal addresses the actual immediate bridge substrate blocker,
not a speculative adjacent issue.

### C2 - Scope is appropriately small

Authorized target paths are limited to:

- `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py`
- `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py`

The proposed test adds the missing nested matcher-wrapper fixture while keeping
the existing flat-shape fixture green for backward compatibility.

## Implementation Guardrails

- Preserve the existing flat hook-entry behavior.
- Do not modify hook files, substrate state files, or mode-switch transaction
  semantics as part of the source fix.
- After implementation, run the targeted validator tests and then apply the
  already pending substrate transaction through the canonical `gt mode`
  command path, not by directly editing `harness-state/bridge-substrate.json`.

## Commands Executed

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-mode-switch-validator-hook-matcher-shape-fix
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-mode-switch-validator-hook-matcher-shape-fix
Select-String -Path groundtruth-kb\src\groundtruth_kb\mode_switch\validation.py -Pattern 'def validate_bridge_substrate|cross_harness_bridge_trigger|hooks' -Context 2,4
Select-String -Path platform_tests\groundtruth_kb\test_mode_switch_bridge_substrate_validation.py -Pattern 'bridge_substrate|cross_harness|hooks|settings' -Context 2,4
```

## Owner Action Required

None.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
