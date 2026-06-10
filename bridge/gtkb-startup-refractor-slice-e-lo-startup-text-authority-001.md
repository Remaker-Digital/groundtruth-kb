NEW

# GTKB-STARTUP-REFRACTOR-001 Slice E — Loyal Opposition Startup Text + Authority

bridge_kind: prime_proposal
Document: gtkb-startup-refractor-slice-e-lo-startup-text-authority
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC

author_identity: Claude Code Prime Builder (PAUTH-authorized implementation)
author_harness_id: B
author_session_context_id: 2026-06-03-gtkb-startup-refractor-slice-e
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-STARTUP-REFRACTOR-001-GTKB-STARTUP-REFRACTOR-001-SLICES-A-E-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-STARTUP-REFRACTOR-001
Work Item: WI-4273

target_paths: ["scripts/session_self_initialization.py", "AGENTS.md", "platform_tests/scripts/test_lo_startup_text.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Slice E of GTKB-STARTUP-REFRACTOR-001 (WI-4273), covering advisory findings **F6**
(generated Loyal Opposition startup text still references Prime-Builder
session-focus choices) and **F5** (a startup authority contradiction about
whether Loyal Opposition must ask before processing the bridge queue).

1. **F6 — role-conditional startup wording (source):** in
   `scripts/session_self_initialization.py`, the `Fresh-Session Input Semantics`
   text ("After presenting this startup disclosure and the session-focus
   choices, wait for Mike's next message...") is rendered for both role paths
   even though the Prime-Builder session-focus menu is not presented in Loyal
   Opposition mode. Make the sentence role-conditional: Prime Builder waits for
   the focus selection; Loyal Opposition uses the next owner message as the task
   unless bridge processing is already actionable.

2. **F5 — resolve the authority contradiction (per owner decision):**
   `CODEX-STANDING-PRIORITIES.md` says Loyal Opposition needs no separate owner
   approval to run requested reviews, while `AGENTS.md` and the generated startup
   service say Loyal Opposition should ask before processing the bridge queue.
   Per the owner decision (2026-06-03 AUQ) — **process the actionable queue
   without asking** — reconcile `AGENTS.md` and the startup-service text to
   match `CODEX-STANDING-PRIORITIES.md`: if actionable `NEW`/`REVISED` entries
   exist, process them without asking; if the queue is clear, report clear and
   wait; ask only on genuine ambiguity.

`AGENTS.md` is a protected narrative artifact; its edit will be made through the
formal narrative-artifact-approval packet path (PAUTH `narrative` mutation
class). The startup-service wording lives in source.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` — governs the generated startup disclosure this slice edits. PAUTH-linked.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — PAUTH-linked governing spec.
- `GOV-SESSION-ROLE-AUTHORITY-001` — role-authority model; F5 reconciles startup authority text with the LO standing-priority authority.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; the F5 resolution concerns LO's bridge-queue processing authority.
- `GOV-ARTIFACT-APPROVAL-001` — governs the protected `AGENTS.md` narrative edit (formal narrative-artifact-approval packet).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec-linkage compliance.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test plan below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + WI + PAUTH linkage.
- `GOV-STANDING-BACKLOG-001` — WI-4273 linkage.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking; all target paths in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory); `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory); `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).

## Prior Deliberations

- `DELIB-20260622` — owner PAUTH decision (covers WI-4273).
- `bridge/gtkb-startup-refractor-scoping-002.md` — scoping GO defining Slice E.
- `DELIB-2078` — owner approval for the init-keyword startup-disclosure relay spec; the F6 wording change must preserve the disclosure-relay contract.
- `bridge/gtkb-startup-refractor-slice-a-startup-control-inventory-004.md` — Slice A VERIFIED (inventory of the startup surfaces this slice edits).

## Owner Decisions / Input

- **Owner AUQ (2026-06-03)** — F5 resolution: "Process queue without asking" —
  if actionable NEW/REVISED exist, LO processes without asking; report clear if
  empty; ask only on ambiguity. This proposal implements that resolution.
- Implementation authority: project PAUTH (active), owner decision `DELIB-20260622`,
  allowed mutation classes include `source`, `narrative`, `test`.

## Requirement Sufficiency

**Existing requirements sufficient.** Governing requirements are advisory F5/F6,
`GOV-SESSION-SELF-INITIALIZATION-001`, and `GOV-SESSION-ROLE-AUTHORITY-001`; the
F5 owner resolution is captured above. No new specification is required (the
change makes existing surfaces internally consistent).

## Spec-Derived Verification Plan

| Specification / Finding | Spec-to-test mapping | Command | Expected |
|---|---|---|---|
| F6 / `GOV-SESSION-SELF-INITIALIZATION-001` | `test_lo_startup_text.py` asserts the generated LO-path startup payload does NOT instruct waiting for "session-focus choices" and the PB-path does | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_lo_startup_text.py -q --no-header -p no:cacheprovider` | PASS |
| F5 / `GOV-SESSION-ROLE-AUTHORITY-001` | same test asserts the LO-path text states actionable-queue processing proceeds without separate approval (spec-to-test on the reconciled wording) | (same pytest) | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | lint + format on the new test + changed source | `ruff check` / `ruff format --check` on changed Python | clean |

The implementation report will carry observed pytest + ruff results and the
`AGENTS.md` narrative-approval packet reference.

## Risk / Rollback

Bounded: a role-conditional wording change in the startup service (no control-flow
change beyond text selection by role), one protected-narrative wording
reconciliation in `AGENTS.md` (packet-gated), and a test. Rollback is a
single-commit revert. The F6 change must preserve the init-keyword
disclosure-relay contract (`DELIB-2078`), verified by the existing startup tests.

## Recommended Commit Type

`fix` — corrects internally-inconsistent generated startup text (F6 wording drift)
and a startup authority contradiction (F5); behavior-affecting for the startup
disclosure, no new capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
