NEW

# gtkb-wi5186-lo-startup-gate-clear — Clear the fresh LO relay gate after validated disclosure

bridge_kind: prime_proposal
Document: gtkb-wi5186-lo-startup-gate-clear
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-11 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4ea0-6326-78a1-a2f4-775fd98d66ce
author_model: GPT-5.5
author_model_version: Codex desktop
author_model_configuration: reasoning=xhigh; approval_policy=never; interactive Prime Builder session

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5186

target_paths: ["scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/scripts/test_lo_startup_text.py"]

implementation_scope: source-and-tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Fix WI-5186 in the shared startup-input-gate handler. A genuinely fresh LO
init-keyword relay already directs default LO to verify live bridge state and
process actionable `NEW`/`REVISED` work, but the handler leaves
`startup_response_pending` true and thereby blocks the required bridge read and
the governed verdict writer until a second owner message.

Introduce a structured, failure-aware relay result: only a validated
owner-visible disclosure relay may clear the pending state, using the auditable
reason `lo_startup_relay`. Default LO may then execute its required same-turn
startup action. PB/non-LO stays pending. Advisory LO may live-scan and report,
but remains opt-in for auto-processing and verdict writing. A missing, stale,
malformed, or wrong-shape relay cache remains pending and visibly reports the
relay failure.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires this source/test change to await an independent LO GO and implementation-start claim.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires complete concrete specification linkage for this proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the PAUTH, project, and WI metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the implementation report to carry executed spec-derived test evidence.
- `GOV-STANDING-BACKLOG-001` — WI-5186 is a member of `PROJECT-GTKB-RELIABILITY-FIXES`, covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.
- `DCL-STARTUP-GATE-FRESH-START-ONLY-001` — governs the LO-only successful-relay clear, PB/non-LO blocking, advisory opt-in, audit reason, failure retention, and harness parity.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` — requires visible validated disclosure before LO continuation and failure-safe pending retention.
- `GOV-SESSION-SELF-INITIALIZATION-001` — requires LO startup instructions to be performed from live bridge state rather than merely displayed.
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` — preserves explicit startup disclosure before discretionary work.
- `SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001` — preserves real-SessionStart-only input-gate arming semantics.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — preserves interactive role-token handling and headless-dispatch separation.
- `ADR-CROSS-HARNESS-PARITY-001` — requires a declared disposition for the shared hook behavior across applicable harnesses.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — preserves the governing artifact lifecycle from owner decision through independent verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — governs the distinct proposal, implementation, report, and verification artifacts in this reliability fix.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — requires the owner decision and durable work-item/specification evidence used here.

## Prior Deliberations

- `DELIB-20260711-LO-FRESH-INIT-GATE-CLEAR` — owner selected Option C: clear only the successful fresh LO relay gate while retaining PB focus gating and advisory opt-in.
- `DELIB-20260711-LO-FRESH-INIT-GATE-DCL-AMENDMENT` — owner selected amendment of the existing startup-gate DCL and reconciliation of the relay DCL.
- `DELIB-20260711-LO-FRESH-INIT-GATE-DCL-EXACT-APPROVAL` — owner approved the exact reviewed DCL content; it explicitly withholds implementation authorization pending this separate proposal, GO, and claim.

## Owner Decisions / Input

The owner selected the implementation contract in
`DELIB-20260711-LO-FRESH-INIT-GATE-CLEAR`; the DCL-carrier and exact amendment
approval are recorded in `DELIB-20260711-LO-FRESH-INIT-GATE-DCL-AMENDMENT` and
`DELIB-20260711-LO-FRESH-INIT-GATE-DCL-EXACT-APPROVAL`. Project membership
`PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-5186` places this WI under standing
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`. Those decisions authorize this
proposal, not implementation: source/test edits still require independent LO
GO and a matching implementation-start claim.

## Requirement Sufficiency

Existing requirements are sufficient. The approved DCL amendments supply the
previously missing fresh-LO continuation rule, and the listed startup, relay,
and role-resolution specifications bound the implementation and its tests. No
new requirement is needed before implementation.

## Spec-Derived Verification Plan

| Specification | Test or verification | Expected result |
| --- | --- | --- |
| `DCL-STARTUP-GATE-FRESH-START-ONLY-001` | New focused cases in `platform_tests/hooks/test_workstream_focus.py` | Successful fresh default/advisory LO relay clears with `lo_startup_relay`; default LO permits `gt` state/writer-shaped calls; PB remains blocked; failed relay remains pending. |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | Focused hook tests plus `platform_tests/scripts/test_lo_startup_text.py` | Relay exposes full disclosure before continuation; failure is visible and never clears; advisory remains scan/report-only with no auto-process or verdict instruction. |
| `GOV-SESSION-SELF-INITIALIZATION-001` | `platform_tests/scripts/test_lo_startup_text.py` and session-startup suites | Default LO instruction requires live bridge verification and actionable processing; advisory asks before switch. |
| `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` and `SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001` | Focused hook tests | Fresh PB still receives disclosure-first pending behavior and real SessionStart arming remains scoped. |
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` | Existing targeted role-marker/init-keyword tests | Explicit LO role-token behavior remains unchanged outside the relay clear. |
| `ADR-CROSS-HARNESS-PARITY-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/check_codex_hook_parity.py` | Codex wrapper remains parity-aligned with the shared Claude/Codex handler. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-STANDING-BACKLOG-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Bridge chain, PAUTH/membership evidence, implementation-start packet, both proposal preflights, and post-implementation report | Each required artifact gate remains satisfied; the report carries the final spec-to-test evidence for LO verification. |

Run the focused suites, then both ruff gates over the changed source/tests. The
post-implementation report will record complete commands and results.

## Cross-Harness Disposition

`scripts/workstream_focus.py` is the shared handler imported by the Claude
hook wrapper and invoked by the Codex hook wrapper. The behavior is therefore
implemented once for both surfaces: validated LO relay clears, PB/non-LO and
relay-failure behavior remains blocked, and advisory remains opt-in. No typed
waiver is requested. `scripts/check_codex_hook_parity.py` is mandatory
verification; no wrapper/configuration file is in scope unless that check finds
an actual parity drift.

## Risk / Rollback

The primary risk is clearing too early and treating an unavailable or displaced
cache as a rendered disclosure. The implementation must derive the clear from a
structured success result, not message text or a speculative cache read, and
the regression suite must prove failure retains the gate. The change is narrow;
reverting the single implementation change restores the prior gated behavior.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5186-lo-startup-gate-clear`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — it restores an already-mandated fresh LO startup action that the input
gate currently prevents.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
