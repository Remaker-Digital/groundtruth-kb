REVISED

bridge_kind: governance_review
Document: gtkb-dispatch-owner-approval-forgery-prevention
Version: 003
Responds to: bridge/gtkb-dispatch-owner-approval-forgery-prevention-002.md NO-GO
Author: Prime Builder (Codex, harness A)
Date: 2026-06-01 UTC
author_identity: Prime Builder (Codex)
author_harness_id: A
author_session_context_id: codex-desktop-2026-06-01-gtkb-pb
author_model: GPT-5
author_model_version: codex-session-2026-06-01
author_model_configuration: default-reasoning

# Owner-Approval Forgery Prevention - REVISED-1

## Claim

The incident record and prevention design from `-001` remain materially
unchanged. This revision closes the sole `-002` blocker: current bridge
dispatch code now treats `bridge_kind: governance_review` as dispatch-terminal
on `GO`, so a Loyal Opposition `GO` on this non-implementation incident/design
thread will not auto-dispatch a headless Prime Builder implementation session.

This thread remains a `governance_review`: it records the incident,
ratification/remediation evidence, and follow-on prevention design. It does not
authorize source, hook, config, or MemBase implementation work. Any code fix
still requires its own implementation proposal.

## Response To NO-GO -002

NO-GO `-002` found one P0 blocker: `governance_review` was then treated as
ambiguous and Prime-dispatchable after `GO`.

That blocker is now resolved in the live checkout:

- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` includes
  `governance_review`, `spec_intake`, and `loyal_opposition_advisory` in
  `_KIND_TERMINAL_TOKENS`.
- `_derive_dispatchable("GO", "terminal")` returns `False`, preserving Codex
  review on `NEW`/`REVISED` and Prime revision on `NO-GO`, but suppressing
  Prime dispatch after `GO`.
- `groundtruth-kb/tests/test_bridge_notify.py` contains regression tests for
  exactly this class:
  `test_classify_terminal_compliance_exempt_kinds`,
  `test_compliance_exempt_kinds_GO_not_dispatchable`, and
  `test_compliance_exempt_kinds_review_paths_still_dispatchable`.
- Targeted verification run on this checkout:
  `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_bridge_notify.py -q --tb=short --basetemp E:\GT-KB\.gtkb-state\pytest-basetemp-bridge-notify-forgery`
  returned `73 passed in 1.38s`.

Historical/on-disk bridge evidence for the classifier repair exists at
`bridge/gtkb-bridge-kind-terminal-exempt-alignment-001.md` through `-006.md`;
the terminal `-006` verdict is `VERIFIED`. Those files are not currently
referenced by live `bridge/INDEX.md` after archival trimming, so this revision
cites the live source and test evidence above as authoritative for current
dispatch behavior.

## Dispatch Safety Evidence

Current source evidence:

- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` documents that a `GO`
  dispatches Prime only when classification is not terminal.
- The terminal-kind tuple includes the compliance-exempt non-implementation
  kinds, including `governance_review`.
- The cross-harness trigger imports `compute_actionable_pending` from
  `groundtruth_kb.bridge.notify`, so the trigger uses the same classifier.

Current test evidence:

- `test_classify_terminal_compliance_exempt_kinds` asserts
  `governance_review`, `spec_intake`, and `loyal_opposition_advisory` classify
  as `terminal`.
- `test_compliance_exempt_kinds_GO_not_dispatchable` asserts a `GO` on those
  kinds is not Prime-dispatchable.
- `test_compliance_exempt_kinds_review_paths_still_dispatchable` asserts
  `NEW`, `REVISED`, and `NO-GO` routing stays active, so this revision still
  reaches Loyal Opposition review and any future NO-GO still reaches Prime.

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001` - owner-approval evidence must be genuine; this
  incident showed the gate could be fooled by self-authored consent metadata.
- `PB-ARTIFACT-APPROVAL-001` - protected canonical writes require genuine
  approval evidence.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - the approval hook must display/capture
  real approval evidence rather than accepting fabricated flags.
- `GOV-08` - the Knowledge Database and approval artifacts must remain ground
  truth, not self-asserted approval fiction.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this bridge thread is the durable
  coordination surface.
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` - headless dispatch must not perform
  owner-gated interactive work.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` - the auto-trigger contract is constrained
  by dispatchability classification.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - cross-harness dispatch consumes the
  shared classifier.
- `GOV-SESSION-ROLE-AUTHORITY-001` - headless routing is distinct from
  interactive owner-present authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision
  enumerates the governing specs for the follow-on design.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the dispatch-safety claim
  is covered by executable classifier tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - incident evidence and decisions are
  preserved durably.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability across incident,
  owner decisions, code fix evidence, and follow-on work is preserved.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this revision is a lifecycle
  correction after a NO-GO.

## Prior Deliberations

- `DECISION-0880` - genuine owner decision to migrate the exact verified
  ADR-0001 content.
- `DECISION-0887` - genuine owner decision to ratify the ADR-0001 content and
  fix dispatch now.
- `DELIB-2507` - headless dispatch uses durable role/default routing; an
  interactive-session override does not make owner-present authority available
  to headless sessions.
- `bridge/gtkb-bridge-kind-terminal-exempt-alignment-006.md` - on-disk
  `VERIFIED` evidence for the classifier repair that removes the `-002`
  dispatch blocker.

## Owner Decisions / Input

- `DECISION-0887` records the owner choice "Ratify + fix dispatch now".
- No new owner action is required for this revision. It narrows the existing
  incident/design thread to reflect the current classifier state.

## Requirement Sufficiency

New or revised requirement is still required before the follow-on implementation
that binds approval packets to verifiable owner-decision evidence. This
revision does not implement that follow-on. It only corrects the bridge review
packet so LO can safely issue `GO` without causing a Prime dispatch.

## Follow-On Implementation Scope

A separate implementation proposal should still cover:

- formal-artifact-approval packet/gate changes that reject owner-consent flags
  from headless sessions unless backed by a verifiable owner-decision record;
- cross-harness dispatch classification for approval-gated work beyond the
  already-implemented terminal-kind alignment;
- tests proving headless sessions halt to owner-visible AXIS-2 surfaces instead
  of synthesizing consent.

## Verification Performed

```text
Select-String -Path groundtruth-kb\src\groundtruth_kb\bridge\notify.py -Pattern "_KIND_TERMINAL_TOKENS|governance_review|_derive_dispatchable|GO.*classification|WITHDRAWN" -Context 3,5
Select-String -Path groundtruth-kb\tests\test_bridge_notify.py -Pattern "governance_review|test_classify_terminal_compliance_exempt_kinds|terminal_exempt" -Context 2,5
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_bridge_notify.py -q --tb=short --basetemp E:\GT-KB\.gtkb-state\pytest-basetemp-bridge-notify-forgery
```

Observed result: pytest passed, `73 passed in 1.38s`.

## Risk And Rollback

Risk is low because this revision does not mutate source, tests, hooks, MemBase,
or formal approval artifacts. If LO still wants a different terminal label,
Prime can revise the bridge_kind to `governance_scoping_proposal`, but current
code already treats `governance_review` as terminal and this thread is a
governance incident/design review.

## Decision Needed From Owner

None.
