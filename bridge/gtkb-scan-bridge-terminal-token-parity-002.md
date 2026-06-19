NO-GO

# Loyal Opposition Review - gtkb-scan-bridge-terminal-token-parity - 002

bridge_kind: review_verdict
Document: gtkb-scan-bridge-terminal-token-parity
Version: 002
Author: Loyal Opposition (Codex automation)
Date: 2026-06-19 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-scan-bridge-terminal-token-parity-001.md
author_identity: loyal-opposition/codex/A
author_harness_id: A
author_session_context_id: codex-keep-working-lo-20260619T0200Z
author_model: gpt-5-codex
author_model_version: GPT-5 family
author_model_configuration: Codex desktop automation session; approval_policy=never; workspace E:\GT-KB

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4675

## Verdict

NO-GO.

The defect is real, the work item is valid, and the focused parity test fails
exactly as described. The proposal is not ready because its `target_paths`
exclude the managed template source for the helper. A fix that edits only the
live `.claude` helper can satisfy `platform_tests/scripts/test_scan_bridge.py`
while leaving GT-KB scaffold/upgrade output stale.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge helper changes need complete governed target scope.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must prove the live helper and managed template source remain aligned with canonical notify routing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal must cite and cover all relevant governed source surfaces.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this review remains linked to `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`, `PROJECT-GTKB-MAY29-HYGIENE`, and `WI-4675`.
- `GOV-STANDING-BACKLOG-001` - WI-4675 remains open until the bridge-helper parity defect is acceptance-clean.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this drift must be fixed across durable helper/template/test artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all proposed target paths remain inside `E:\GT-KB`.

## Evidence

- `python -m groundtruth_kb.cli backlog list --id WI-4675 --json` confirms
  WI-4675 is open/backlogged under `PROJECT-GTKB-MAY29-HYGIENE`.
- `python scripts\bridge_applicability_preflight.py --content-file bridge\gtkb-scan-bridge-terminal-token-parity-001.md --json`
  passed with packet hash
  `sha256:8ee3b500fb617f0b66f1ebe75e666151817371f8bdc452fe76f5c1167a7fd9b8`,
  missing required specs `[]`, and missing advisory specs `[]`.
- `python scripts\adr_dcl_clause_preflight.py --content-file bridge\gtkb-scan-bridge-terminal-token-parity-001.md`
  passed with 5 clauses evaluated, 3 `must_apply`, 0 evidence gaps, and 0
  blocking gaps.
- `platform_tests/scripts/test_scan_bridge.py` imports the live helper from
  `.claude/skills/bridge/helpers/scan_bridge.py`.
- `groundtruth-kb/templates/managed-artifacts.toml:524-525` maps
  `template_path = "skills/bridge/helpers/scan_bridge.py"` to
  `target_path = ".claude/skills/bridge/helpers/scan_bridge.py"`.
- `rg -n "KIND_TERMINAL|implementation_report|post_impl|post_implementation" ...`
  shows both `.claude/skills/bridge/helpers/scan_bridge.py` and
  `groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py` lack
  `implementation_report`, `post_implementation`, and `post_impl`, while
  `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` contains all three.

## Verification Command

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; python -m pytest -o addopts= --basetemp E:\GT-KB\.gtkb-tmp\pytest-scan-bridge-parity-lo-20260619T0203Z platform_tests\scripts\test_scan_bridge.py -q --tb=short
```

Observed result:

```text
1 failed, 20 passed in 19.24s
FAILED platform_tests/scripts/test_scan_bridge.py::test_terminal_tokens_parity_with_canonical_notify
Extra items in the right set: 'post_impl', 'implementation_report', 'post_implementation'
```

## Required Revision

Revise the proposal before implementation:

1. Add `groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py` to
   `target_paths`, or explicitly justify why the managed template source should
   remain stale. The current evidence does not support leaving it stale.
2. Update the proposed scope so both the live helper and the managed template
   helper mirror `groundtruth_kb.bridge.notify._KIND_TERMINAL_TOKENS`.
3. Add or extend verification so scaffold/upgrade parity cannot regress. At
   minimum, the focused `platform_tests/scripts/test_scan_bridge.py` test must
   pass, and the revised plan should include a template/live parity check or a
   scaffold/upgrade test that proves the template copy is not stale.
4. Keep `groundtruth_kb.bridge.notify` out of scope unless Prime Builder finds
   evidence that the canonical token set itself is wrong.

## Owner Action Required

None.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
