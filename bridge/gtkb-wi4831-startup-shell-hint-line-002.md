GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-lo-autoproc-2026-06-25h
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive Loyal Opposition auto-process

bridge_kind: proposal_review
Document: gtkb-wi4831-startup-shell-hint-line
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-25 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4831-startup-shell-hint-line-001.md
Project Authorization: PAUTH-WI-4831-STARTUP-SHELL-HINT-001
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-4831
Recommended commit type: feat

## Separation Check

Proposal `-001` author session `d40d99d8-b006-4dd8-8e9d-bce8371a1e4b` (harness B); this Cursor LO session is independent — not self-review.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4831-startup-shell-hint-line`

- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4831-startup-shell-hint-line`

- Clauses evaluated: 5; must_apply blocking gaps: 0; exit 0.

## Review Summary

Proposal is **additive, narrowly scoped, and owner-authorized**. A single `[Shell]` line on the canonical SessionStart governance template removes recurring per-session rediscovery of PowerShell `gt` invocation and `PYTHONPATH=groundtruth-kb/src` for project Python. The runtime `.claude/hooks/session-start-governance.py` shim delegates via `runpy` to the template — editing the template is the correct single edit point.

## Claim Verification

| Claim | Result | Evidence |
|---|---|---|
| Owner authorization | pass | `DELIB-20266110` packet present; owner chose "Implement the doc line now" |
| Spec linkage | pass | `GOV-SESSION-SELF-INITIALIZATION-001` + DCL linkage/testing specs cited; preflights clean |
| Requirement sufficiency | pass | Proposal documents existing-requirements-sufficient with startup token-reduction clause |
| Target paths | pass | `groundtruth-kb/templates/hooks/session-start-governance.py`; new test under `platform_tests/hooks/` (pattern matches existing hook tests) |
| Shim delegation | pass | `.claude/hooks/session-start-governance.py` is 18-line `runpy` delegate to template |
| Verification plan | pass | Subprocess hook test asserting `[Shell]`, `PowerShell`, `PYTHONPATH` in `additionalContext` |
| Scope boundary | pass | Claude-harness scoped; Codex parity explicitly deferred |

## Residual Risks (implementation-time)

- Hint text should name the **canonical** venv path `groundtruth-kb/.venv/Scripts/python.exe` (both root `.venv` and package venv exist on this host; only the latter is the documented GT-KB toolchain path).
- Governance pending-branch copy still says "pending Codex review" — out of slice; do not expand scope unless filing a separate WI.

## Prior Deliberations

- `DELIB-20266110` — owner AUQ authorizing implement-now path for WI-4831 shell hint.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — eliminate recurring AI rediscovery of conventions.

## Verdict

**GO.** Implement per `-001` change detail and verification plan.

Skills applied: proposal-review, bridge
