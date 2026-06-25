NEW
author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: 2026-06-25T04-52-00Z-prime-builder-E-f7a3b2
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive Prime Builder; bridge-clearance loop

# GT-KB Bridge Implementation Report - gtkb-startup-open-work-items-metric-raw-count - 003

bridge_kind: implementation_report
Document: gtkb-startup-open-work-items-metric-raw-count
Version: 003
Date: 2026-06-25 UTC
Responds to: bridge/gtkb-startup-open-work-items-metric-raw-count-002.md
Approved proposal: bridge/gtkb-startup-open-work-items-metric-raw-count-001.md
Recommended commit type: fix

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-3327

target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization.py"]
implementation_scope: source,test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Implementation Claim

Implemented the render-clarity fix approved at `-002` for WI-3327. Added
`_format_open_work_items_count()` and wired it at both disclosure sites:

- `_render_current_project_state` (startup disclosure)
- `render_wrapup_notice` (wrap-up report)

When `raw_open_work_items` is present and differs from the subject-scoped
`open_work_items`, the line now shows both counts with an explicit
`(subject-scoped; N across all subjects)` parenthetical. When raw is absent or
equal, the prior single-count render is preserved.

Added two regression tests asserting the dual-count label in startup and wrap-up
render paths. No metric computation changes.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` - startup disclosure metric clarity.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - unambiguous displayed counts.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered bridge chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project/PAUTH/WI metadata.
- `GOV-STANDING-BACKLOG-001` - WI-3327 backlog member.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - May29 Hygiene PAUTH.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - scoped vs raw subject boundary.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - durable tested artifact change.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `GOV-SESSION-SELF-INITIALIZATION-001` | `test_render_current_project_state_open_work_items_shows_raw_count` | yes | PASS |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_render_wrapup_notice_open_work_items_shows_raw_count` | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | targeted pytest + ruff | yes | PASS |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | ruff check + ruff format on changed files | yes | PASS |

## Verification Evidence

```text
python -m pytest platform_tests/scripts/test_session_self_initialization.py::test_render_current_project_state_open_work_items_shows_raw_count platform_tests/scripts/test_session_self_initialization.py::test_render_wrapup_notice_open_work_items_shows_raw_count -q --tb=short
# 2 passed

python -m ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py
# All checks passed!

python -m ruff format --check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py
# 2 files already formatted
```

Implementation-start packet: `gtkb-startup-open-work-items-metric-raw-count`
(session `2026-06-25T04-52-00Z-prime-builder-E-f7a3b2`).

## Loyal Opposition Verification Request

Independent **VERIFIED** in a separate session context. Re-run targeted pytest and
ruff above.
