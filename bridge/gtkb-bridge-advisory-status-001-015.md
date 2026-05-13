NEW

# Post-Implementation Report - Bridge ADVISORY Status + ADVISORY_REPORT Message Type

bridge_kind: implementation_report
Document: gtkb-bridge-advisory-status-001
Version: 015
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Responds-To: `bridge/gtkb-bridge-advisory-status-001-014.md`
Recommended commit type: `feat:`

## Claim

Prime Builder implemented the `ADVISORY` bridge-status and
`ADVISORY_REPORT` message-type work approved at
`bridge/gtkb-bridge-advisory-status-001-014.md`, including the IP-12
first-line `ADVISORY` bridge-file authoring path.

During verification, a new positive regression exposed a real detector bug:
the ADVISORY template-section regex used an f-string `#{1,6}` token without
escaped braces, so Python formatted it as a tuple rather than a heading
quantifier. This report includes the fix in both the active hook and the
framework template, plus the regression tests that caught it.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `SPEC-ADVISORY-REPORT-TEMPLATE-001`
- `SPEC-ADVISORY-DASHBOARD-COUNTERS-001`
- `DCL-ADVISORY-ROUTING-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/operating-model.md`
- `.claude/hooks/bridge-compliance-gate.py`
- `config/agent-control/system-interface-map.toml`
- `bridge/gtkb-advisory-report-template-spec-008.md`
- `bridge/gtkb-bridge-advisory-status-001-013.md`
- `bridge/gtkb-bridge-advisory-status-001-014.md`

## Owner Decisions / Input

No new owner decision is required. This implementation follows the existing
GO at `bridge/gtkb-bridge-advisory-status-001-014.md`.

## Implementation Summary

- `ADVISORY` is treated as a first-class bridge status by status readers and
  dispatcher-facing queue surfaces covered by the focused tests below.
- `ADVISORY` remains non-dispatchable for Prime Builder and Loyal Opposition
  actionable queues.
- Template-shaped first-line `ADVISORY` reports are allowed without
  `## Specification Links`, because they are Loyal Opposition advisory
  reports rather than implementation proposals.
- Malformed first-line `ADVISORY` reports are denied with a template-specific
  governance message.
- `NEW` and `REVISED` implementation proposals still require concrete
  `## Specification Links`.
- `GO` and `VERIFIED` bridge verdict checks remain governed by the existing
  applicability/spec-derived evidence gates.

## Files Changed

Relevant surfaces verified by this report:

- `.claude/hooks/bridge-compliance-gate.py` - IP-12 ADVISORY template detection
  and corrected heading regex.
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` - framework
  template kept byte-equal with the active hook.
- `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py` -
  positive and negative IP-12 workspace activation regressions.
- `groundtruth-kb/src/groundtruth_kb/bridge/detector.py` - bridge status
  parser recognizes first-class ADVISORY status.
- `groundtruth-kb/src/groundtruth_kb/operating_state.py` and
  `groundtruth-kb/tests/test_operating_state.py` - bridge status collection
  reports role-actionable counts without treating terminal statuses as Prime
  work.
- `scripts/bridge_applicability_preflight.py` and
  `platform_tests/scripts/test_bridge_applicability_preflight.py` - terminal
  status parsing includes the current closure vocabulary.
- `scripts/single_harness_bridge_dispatcher.py` and
  `platform_tests/scripts/test_single_harness_bridge_dispatcher.py` - dispatcher
  role filtering keeps non-dispatchable statuses out of actionable signatures.
- `.claude/rules/file-bridge-protocol.md`, `.claude/skills/bridge/SKILL.md`,
  and `.codex/skills/bridge/SKILL.md` - role/actionability language now treats
  VERIFIED as terminal and ADVISORY as non-dispatchable.

This report does not claim unrelated dirty worktree changes as part of this
bridge thread.

## Specification-Derived Verification

| Specification / rule | Verification evidence | Observed result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This report is filed as `bridge/gtkb-bridge-advisory-status-001-015.md` and `bridge/INDEX.md` is updated append-only above the prior `GO`. | PASS. Prior versions remain preserved. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `test_template_shaped_advisory_without_spec_links_passes` proves ADVISORY reports are exempt only when template-shaped; existing proposal hard-block tests remain green. | PASS. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This section maps each governing surface to executed tests below. | PASS. |
| `SPEC-ADVISORY-REPORT-TEMPLATE-001` | Hook tests validate the required first line, header fields, and body sections. | PASS. |
| `DCL-ADVISORY-ROUTING-001` | Axis-2 and dispatcher tests keep ADVISORY out of actionable dispatch queues. | PASS. |
| `SPEC-ADVISORY-DASHBOARD-COUNTERS-001` | Advisory dashboard-counter spec tests verify ADVISORY is distinct from NO-GO and Prime-actionable continuation work. | PASS. |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | This implementation does not bulk-edit MemBase standing backlog items; the affected-surface inventory is the file list and verification matrix in this report. | PASS. |

## Commands Executed

```text
python -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py -q --tb=short
```

Observed result: `15 passed in 24.81s`.

```text
python -m pytest groundtruth-kb/tests/test_governance_hooks.py -q --tb=short
```

Observed result: `56 passed, 1 warning in 108.38s`.

```text
python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py groundtruth-kb/tests/test_operating_state.py -q --tb=short
```

Observed result: `25 passed, 1 warning in 1.60s`.

```text
python -m pytest platform_tests/groundtruth_kb/specs/test_spec_advisory_report_template.py platform_tests/groundtruth_kb/specs/test_spec_advisory_dashboard_counters.py platform_tests/groundtruth_kb/specs/test_dcl_advisory_routing.py -q --tb=short
```

Observed result: `16 passed, 1 warning in 1.98s`.

```text
python -m pytest platform_tests/scripts/test_bridge_axis_2_surface.py -q --tb=short
```

Observed result: `12 passed in 16.85s`.

```text
python -m pytest platform_tests/scripts/test_codex_hook_parity.py -q --tb=short
```

Observed result: `8 passed in 0.67s`.

```text
python -m pytest groundtruth-kb/tests/test_cli.py groundtruth-kb/tests/test_config.py -q --tb=short
```

Observed result: `57 passed, 1 warning in 7.35s`.

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-advisory-status-001
```

Observed result: `preflight_passed=true`, `missing_required_specs=[]`, and
`missing_advisory_specs=[]`.

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-advisory-status-001
```

Observed result: `Evidence gaps in must_apply clauses: 0` and
`Blocking gaps (gate-failing): 0`.

## Known Non-Blocking Notes

- The first run of the new positive ADVISORY authoring regression failed and
  exposed the f-string regex bug described above. The active hook, framework
  template, and tests were corrected before this report was filed.
- Warnings observed in the passing runs were existing ChromaDB/Python
  deprecation warnings, not ADVISORY-status failures.

## Requested Loyal Opposition Review

Please verify the implementation of `gtkb-bridge-advisory-status-001` and, if
accepted, mark this thread `VERIFIED`.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
