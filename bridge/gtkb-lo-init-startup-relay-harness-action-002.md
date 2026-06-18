GO

bridge_kind: lo_verdict
Document: gtkb-lo-init-startup-relay-harness-action
Version: 002
Author: Loyal Opposition (Codex, session envelope ::init gtkb lo)
Date: 2026-06-18 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-lo-init-startup-relay-harness-action-001.md
Verdict: GO
Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4440

# Loyal Opposition Review - LO Init Relay Harness Action

## Verdict Summary

GO.

The proposal is approved for implementation. It targets the exact failure mode observed in this session family: an LO init-keyword path can relay startup disclosure and then stop, leaving the required harness-only LO startup action - live bridge verification plus default processing of actionable NEW/REVISED bridge work - undone. The scope is appropriately role-specific and preserves Prime Builder focus-gathering and advisory-mode opt-in behavior.

No blocking findings.

## Evidence Reviewed

- Proposal: `bridge/gtkb-lo-init-startup-relay-harness-action-001.md`.
- Target paths: `scripts/workstream_focus.py`, `scripts/session_self_initialization.py`, `platform_tests/hooks/test_workstream_focus.py`, `platform_tests/scripts/test_session_self_initialization.py`.
- Current session evidence: this Codex session resolved as LO through the per-session marker, while the legacy single-file marker was absent. That makes the relay/follow-through behavior directly relevant to the current dispatcher repair lane.
- Live dispatcher context: LO dispatch remains unhealthy with pending review work, so a reliable interactive LO follow-through path is necessary.

## Findings

No blockers.

Advisory A1: Keep the cache-read-only startup relay guard intact. The implementation should change what LO is instructed to do after disclosure relay, not bypass the relay cache protections.

Advisory A2: The Prime Builder path must remain conservative: PB disclosure/focus-menu startup should still wait for owner focus or an unambiguous concrete task.

## Prior Deliberations

- `WI-4440` - captured the relay-stop defect.
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-010.md` - earlier VERIFIED startup-symmetry baseline; this proposal handles the residual live relay-follow-through defect.
- `bridge/gtkb-startup-relay-pretooluse-read-exemption-005.md` and `bridge/gtkb-startup-relay-truncation-fix-refile-012.md` - relay mechanics that must be preserved.

## Applicability And Clause Preflights

Applicability preflight passed for `gtkb-lo-init-startup-relay-harness-action`:

- packet hash: `sha256:cf899208637c3c124b518a1ebb095e3d76be17098da379c0ac6026e7421aa2b1`
- missing required specs: none
- missing advisory specs: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` only

ADR/DCL clause preflight passed:

- clauses evaluated: 5
- must_apply: 4
- may_apply: 1
- blocking gaps: 0

## Required Implementation Evidence

Prime Builder should file a post-implementation report with:

- tests proving LO default init-keyword relay includes follow-through to live bridge scan / auto-process instructions after disclosure;
- tests proving `init gtkb advisory` remains opt-in advisory mode and asks before auto-processing;
- tests proving PB startup still waits for owner focus or a concrete mapped task;
- tests or source assertions that live TAFE/dispatcher state and versioned bridge files remain the only queue authority;
- focused pytest over `platform_tests/hooks/test_workstream_focus.py`, `platform_tests/scripts/test_session_self_initialization.py`, and `platform_tests/scripts/test_session_init_keyword_matching.py` as applicable;
- ruff check and format checks for all changed files.

## Residual Risk

The main risk is accidentally making Prime Builder startup proceed into tool work without owner focus. Keep the implementation role/mode-specific and test PB, LO-default, and LO-advisory separately.

