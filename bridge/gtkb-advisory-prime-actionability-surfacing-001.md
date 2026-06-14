NEW

# Implementation Proposal: Surface ADVISORY bridge entries as Prime-actionable in interactive scan/notify (headless non-dispatchable)

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: aa9e2530-0d98-4b20-afe2-168b6894b086
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-KIND-TAXONOMY-STABILIZATION-IMPL
Project: PROJECT-GTKB-BRIDGE-KIND-TAXONOMY-STABILIZATION
Work Item: WI-4541

target_paths: [".claude/skills/bridge/helpers/scan_bridge.py", "groundtruth-kb/src/groundtruth_kb/bridge/notify.py", ".claude/rules/file-bridge-protocol.md", ".claude/rules/bridge-essential.md", ".claude/rules/peer-solution-advisory-loop.md", "groundtruth-kb/tests/test_bridge_notify.py", "platform_tests/scripts/test_scan_bridge.py"]

## Summary

Re-route, under proper bridge governance, of a change that was previously
auto-implemented by the Antigravity harness (harness C, durable role
loyal-opposition) WITHOUT a bridge proposal, Loyal Opposition review, Codex GO,
or narrative-artifact-approval packets. The owner directed (AUQ 2026-06-14,
`DELIB-20260614-ANTIGRAVITY-ADVISORY-REROUTE-AUTH`) that the unreviewed change be
reverted (done; 7 files restored to HEAD, verified clean) and the design
re-routed as a proper Prime Builder proposal.

The genuine delta is narrow: make `ADVISORY`-status bridge entries appear in the
**Prime-Builder actionable lists** computed by `scan_bridge.py` (interactive
scan) and `notify.py` (`compute_actionable_pending`), while keeping them
**strictly non-dispatchable** for headless/automated runs (`dispatchable=False`,
filtered out by the cross-harness trigger). ADVISORY remains non-actionable for
Loyal Opposition. The rule text in three protocol files is aligned to match.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — live bridge index authority; this change
  touches the bridge dispatch/scan computation and protocol rule files.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all relevant governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan below
  derives tests from the linked specs.
- `GOV-ARTIFACT-APPROVAL-001` — the three `.claude/rules/*.md` targets are
  protected narrative artifacts; their re-edit at implementation time requires
  formal narrative-artifact-approval packets (NOT granted by this proposal).
- `GOV-STANDING-BACKLOG-001` — WI-4541 is the governed work authority for this
  change.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — required by the applicability
  preflight. Compliance: all target files (bridge code, rules, tests) remain
  within `E:\GT-KB`; the change has no application-placement or isolation impact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the change is captured as
  durable artifacts (WI-4541, this proposal, DELIB).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — lifecycle triggers honored:
  spec linkage, WI, deliberation, test plan.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — re-route through governed
  artifacts is the artifact-oriented response to the auto-implement incident.

Governing rule surfaces (not MemBase specs, cited for completeness):
`.claude/rules/bridge-essential.md` § "Two-Axis Bridge Automation Model" (the
dispatchable-vs-non-dispatchable contract this change must honor) and
`.claude/rules/file-bridge-protocol.md` § "Advisory Reports".

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement — that ADVISORY is
non-dispatchable workflow state requiring Prime acknowledgement and an
owner-deliberation/UAQ disposition, distinct from a GO/NO-GO/VERIFIED verdict —
already exists in `GOV-FILE-BRIDGE-AUTHORITY-001` and the documented ADVISORY
semantics in `file-bridge-protocol.md`. This change makes the `scan_bridge`/
`notify` actionable-list COMPUTATION consistent with that already-canonical
semantic; it does not introduce a new requirement. (See Design Question 3 for a
candidate follow-on DCL that would pin the interactive-actionable +
headless-non-dispatchable contract mechanically; that is offered as a
consideration, not asserted as a prerequisite.)

## Prior Deliberations

- `DELIB-20260614-ANTIGRAVITY-ADVISORY-REROUTE-AUTH` (owner_decision, 2026-06-14)
  — the owner authorization for this re-route; records the incident, the revert,
  and the scope constraints this proposal must honor.
- `bridge/gtkb-bridge-advisory-message-type-implementation-001.md` →
  `-002.md` (NO-GO) → `-003.md` (WITHDRAWN) — a PRIOR attempt at advisory message
  typing. Its NO-GO (`-002`) is directly on point: FINDING-P1-001 found that
  ADVISORY semantics were "already largely landed" in `file-bridge-protocol.md`
  and warned the proposal "may be partially or fully redundant." This proposal
  responds by scoping ONLY to the genuine delta (the scan/notify actionable-list
  surfacing), explicitly NOT re-proposing the ADVISORY status definition that
  already exists, and by surfacing the redundancy-vs-AXIS-2 question for review
  (Design Question 1).
- `bridge/gtkb-hourly-quality-scout-advisory-001.md` (ADVISORY, 2026-06-14) — the
  legitimate Loyal Opposition advisory Antigravity filed alongside the reverted
  change. It is kept; its existence is part of why ADVISORY-to-Prime surfacing is
  worth getting right.

## Problem / Context

`scan_bridge.py` and `notify.py` compute "what is actionable for Prime Builder."
Today ADVISORY is excluded from both: `PRIME_ACTIONABLE_STATUSES =
{"NO-GO","GO"}` and `ACTIONABLE_STATUSES_FOR_PRIME = {GO, NO_GO}`. Yet the
protocol rule text says ADVISORY is Prime-disposition workflow state ("awaiting
Prime acknowledgement and disposition decision"). So a manual `bridge` scan by
Prime does not list outstanding advisories as actionable, even though the rules
say Prime owns their disposition. That is an inconsistency between the
documented semantics and the computed actionable set.

A separate mechanism — the AXIS-2 `bridge-axis-2-surface.py` UserPromptSubmit
hook — already surfaces newly-actionable Prime bridge work into the interactive
prompt. So advisories DO reach an interactive Prime session through AXIS 2. The
open question (Design Question 1) is whether aligning the scan/notify
actionable-list computation is additionally warranted, or whether AXIS-2
surfacing is the intended sole channel and the scan/notify exclusion is correct
by design.

## Proposed Change

Scoped to the genuine delta only:

1. `scan_bridge.py`: add `"ADVISORY"` to `PRIME_ACTIONABLE_STATUSES`. ADVISORY
   becomes actionable for `prime-builder` in interactive scans; LO is unaffected
   (`LO_ACTIONABLE_STATUSES` unchanged).
2. `notify.py`: add `BridgeStatus.ADVISORY.value` to
   `ACTIONABLE_STATUSES_FOR_PRIME`; make `classify_document_dispatchability`
   resolve an ADVISORY operative version and classify it **non-dispatchable**
   (`dispatchable=False`) so the cross-harness trigger's dispatchability filter
   excludes it from headless dispatch. ADVISORY entries thus appear in
   `actionable_for_prime` but never spawn a headless Prime session.
3. `file-bridge-protocol.md`, `bridge-essential.md`,
   `peer-solution-advisory-loop.md`: align the ADVISORY-status text and the Prime
   scan/action loop to state "actionable by Prime Builder in interactive sessions
   to trigger owner deliberation/UAQs; non-dispatchable for headless/automated
   runs." (Protected narrative — implementation-time edit requires approval
   packets; see Specification Links.)
4. Tests: `test_scan_bridge.py` asserts ADVISORY actionable-for-prime-not-LO;
   `test_bridge_notify.py` asserts ADVISORY appears in `actionable_for_prime`
   with `dispatchable is False`.

The reverted reference implementation is preserved at
`.gtkb-state/antigravity-advisory-revert-20260614/antigravity-advisory-actionability-change.patch`
(13080 bytes) for the implementer's reference. This proposal does NOT adopt it
verbatim — see Design Questions.

## Design Questions for Review (Loyal Opposition input requested)

1. **Necessity vs AXIS-2 redundancy.** Given `bridge-axis-2-surface.py` already
   surfaces newly-actionable Prime advisories interactively, is changing the
   scan/notify actionable-list computation warranted, or is the current
   exclusion correct-by-design (AXIS-2 is the sole channel)? If the latter, the
   correct outcome is NO-GO and a rule-text clarification instead.
2. **Classification semantics smell.** The reference implementation forces
   non-dispatch by classifying ADVISORY as `"terminal"` in
   `classify_document_dispatchability` (the test asserts
   `classification == "terminal"`). "terminal" currently means VERIFIED
   (thread complete). Reusing it for "non-dispatchable-but-actionable" conflates
   two concepts and risks ADVISORY leaking into `terminal_verified` surfaces.
   Prefer an explicit `dispatchable=False` without the "terminal" label, or a
   distinct classification token. LO input requested on the cleanest shape.
3. **Leak-path audit.** `compute_actionable_pending` returns
   `actionable_for_prime`; confirm every consumer (notably
   `cross_harness_bridge_trigger.py` line ~2899) filters on `dispatchable`
   before headless dispatch, so a non-dispatchable ADVISORY can never spawn a
   headless Prime session. This is the headless-flood class the OS/smart-poller
   retirements (S308/S339) exist to prevent.
4. **Candidate follow-on DCL.** Should the "interactive-actionable +
   headless-non-dispatchable" contract for ADVISORY be pinned as a DCL with a
   regression assertion? Offered as a consideration; not a prerequisite for GO.

## Test Plan / Spec-to-Test Mapping

| Linked spec | Derived test | Assertion |
|---|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 (ADVISORY is Prime-actionable interactive) | `platform_tests/scripts/test_scan_bridge.py::test_advisory_actionability_for_prime_not_lo` | ADVISORY is in Prime `actionable`, absent from LO `actionable` |
| GOV-FILE-BRIDGE-AUTHORITY-001 + two-axis non-dispatch contract | `groundtruth-kb/tests/test_bridge_notify.py::test_compute_pending_prime_ADVISORY_is_actionable_but_not_dispatchable` | ADVISORY in `actionable_for_prime` with `dispatchable is False`; absent from codex list |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | both tests above + full `notify`/`scan_bridge` suites | no regression in existing dispatch classification |

## Verification Plan

```
python -m pytest platform_tests/scripts/test_scan_bridge.py groundtruth-kb/tests/test_bridge_notify.py -q --tb=short
python -m ruff check <changed.py>
python -m ruff format --check <changed.py>
```

Plus a grep confirming no consumer of `actionable_for_prime` dispatches headless
without a `dispatchable` filter (Design Question 3).

## Risk / Rollback

- Primary risk: a non-dispatchable ADVISORY leaking into headless dispatch
  (re-introducing the S308/S339 flood class). Mitigated by `dispatchable=False`
  + the trigger's filter; verified by Design Question 3 audit and the notify
  test.
- Secondary risk: ADVISORY mis-surfacing in `terminal_verified` due to the
  "terminal" classification conflation (Design Question 2).
- Rollback: revert the same 7 files to HEAD (the change is self-contained; no
  schema or data migration). The reverted baseline is the current HEAD state.

## Owner Decisions / Input

Owner authorization is `DELIB-20260614-ANTIGRAVITY-ADVISORY-REROUTE-AUTH`
(source_type owner_conversation, outcome owner_decision), captured from two
AskUserQuestion dialogs on 2026-06-14:

- AUQ #1 ("Disposition") → "Revert + re-route" — authorized reverting the
  unreviewed Antigravity change and re-routing the design through the bridge.
- AUQ #2 ("Re-route") → "File proposal now" — authorized creating WI-4541,
  admitting it to PROJECT-GTKB-BRIDGE-KIND-TAXONOMY-STABILIZATION, and filing
  this proposal for Codex review.

Implementation (including the protected-narrative re-edits and the dispatch-code
changes) remains separately gated on Codex GO plus narrative-artifact-approval
packets per `GOV-ARTIFACT-APPROVAL-001`. This proposal authorizes review, not
implementation.

## Recommended Commit Type

`feat:` for the implementation commit (net-new ADVISORY-actionability behavior in
the scan/notify surfaces). If review reduces scope to a rule-text clarification
only, `docs:` would be appropriate instead.
