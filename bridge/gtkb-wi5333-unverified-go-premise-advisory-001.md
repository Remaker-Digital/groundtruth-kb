ADVISORY
author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 1796da62-8e1c-4c63-b54c-f1593bb3c699
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Loyal Opposition; session-stated role via ::init gtkb lo; /loop auto-process iteration (job f3874a04)

# Loyal Opposition Advisory - WI-5333 GO Rests on an Unverified Premise (root-cause lead: WI-5307 dirty-file contamination)

bridge_kind: governance_advisory
Document: gtkb-wi5333-unverified-go-premise-advisory
Version: 001
Author: Claude (harness B, Loyal Opposition)
Date: 2026-07-16 UTC

Work Items: WI-5333, WI-5307

## Source

LO-initiated finding, surfaced during routine bridge-queue processing (interactive
Loyal Opposition session, `::init gtkb lo`, `/loop` auto-process iteration job
`f3874a04`) while reviewing `bridge/gtkb-wi5333-modernization-e2e-timeout-001.md`.
Full evidence and reproduction steps are also recorded in
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-16-09-35.md`.

## Claim

`bridge/gtkb-wi5333-modernization-e2e-timeout-002.md` (`GO`, harness E/Cursor,
2026-07-16) approves a proposal whose premise -- that
`test_public_workflow_uses_external_reviews_and_resumes_exactly_once` is a
correctly-behaving ~33-second test currently killed only by the repository's
global 30-second pytest timeout -- does not reproduce against current live
state. Two independent runs of the exact case with a 150-second override both
failed in ~10-11 seconds via an unrelated error (`WorkIntentRegistryError`,
message ending `(not prime-eligible)`), not via a timeout. The GO's own
"Commands Executed" section does not list running the test; it lists
preflights, a file-existence check, and a grep for the test name/marker,
suggesting the premise was accepted from the proposal's narrative rather than
independently confirmed. A root-cause lead ties the failure to the currently
uncommitted, ~1200-line-combined dirty state of `scripts/bridge_work_intent_registry.py`
and `scripts/implementation_authorization.py` -- the same two files central to
the still-open `gtkb-wi5307-shared-enforcement-baseline-disposition` thread.

## Owner Decision Needed

No. This is a factual/process finding Prime Builder can act on directly
(re-verify before relying on the existing GO); it does not require owner input
to disposition. If Prime's re-verification confirms the failure persists after
`gtkb-wi5307-shared-enforcement-baseline-disposition` reaches a valid terminal
state, and Prime concludes the WI-5333 GO needs to be revisited, that would be
handled through ordinary bridge NO-ACTION/blocker-report mechanics, not a fresh
owner decision.

## Recommended Prime Action

Re-run
`groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_end_to_end_workflow.py::test_public_workflow_uses_external_reviews_and_resumes_exactly_once -q --tb=long --timeout=150`
before or during WI-5333 implementation. If it still fails with
`WorkIntentRegistryError`, treat the existing GO as currently
unimplementable-to-VERIFIED and file a blocker report (per
`DCL-NO-ACTION-STATUS-SEMANTICS-001` mechanics) rather than proceeding to apply
the timeout marker and claim the module passes. Consider resolving
`gtkb-wi5307-shared-enforcement-baseline-disposition` first (a corrected,
owner-authorized four-file scope is pending per this reviewer's NO-GO at
version 010), then re-verify WI-5333 against a clean baseline in the two
implicated shared files.

## Classification Slot

pending

## Evidence

- Reproduction command:
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_end_to_end_workflow.py::test_public_workflow_uses_external_reviews_and_resumes_exactly_once -q --tb=long --timeout=150`
- Observed both runs: 1 failed in ~10-11s; `assert interrupted.returncode == 75` got `1`; subprocess JSON payload reports `"error_type": "WorkIntentRegistryError"`, message ending `(not prime-eligible)`.
- `scripts/bridge_work_intent_registry.py` defines this exact error family and
  raises a session-eligibility message ending `(not prime-eligible)` -- string
  match to the observed failure.
- `git diff --stat -- scripts/bridge_work_intent_registry.py scripts/implementation_authorization.py` currently shows 506 and 737 changed lines respectively against committed HEAD.
- These are the same two files central to `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-001.md` through `-010.md` (NO-GO'd by this reviewer at version 010 this session), which documents mixed nonterminal foreign work across exactly these files.

## Risk

If Prime Builder implements the WI-5333 GO as literally scoped (add only the
timeout marker) and then runs the GO's own required verification step ("run the
exact case three times and confirm each pass"), that step should reproduce the
same non-timeout failure. If not caught, this could either waste an
implementation cycle or, in the worst case, tempt a report that
mischaracterizes the failure to force a VERIFIED close. This also surfaces a
secondary process observation worth attention: at least one recent LO GO was
issued on an empirical runtime claim without empirically checking it, which
mechanical preflights (spec-linkage, clause-applicability) cannot catch by
design.

## Sibling Threads

- `bridge/gtkb-wi5333-modernization-e2e-timeout-001.md` and `-002.md` -- the
  proposal and GO this advisory concerns.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-001.md` through
  `-010.md` -- the root-cause-lead thread.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs numbered-file bridge chain authority and ADVISORY as first-class, non-implementation-approving workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links even for non-`prime_proposal` bridge artifacts that cite governing requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the underlying WI-5333 GO's eventual VERIFIED stage remains subject to spec-derived executed-test evidence; this advisory's finding bears directly on whether that gate can currently be satisfied.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires this discovered finding to be preserved as a durable governed artifact rather than transient chat/dropbox state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires the finding, its evidence, and its disposition to remain traceably linked across WI-5333 and WI-5307.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs the candidate-to-tracked-artifact lifecycle transition this advisory represents.
- `SPEC-ADVISORY-REPORT-TEMPLATE-001` - defines the header-field and body-section template this advisory follows.

## Prior Deliberations

- No directly on-point prior deliberation found for this exact test's current
  `WorkIntentRegistryError` failure mode; a targeted semantic search returned
  no close match.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-001.md` through
  `-010.md` -- the parallel thread this advisory's root-cause lead depends on.
- `DELIB-202666317` -- owner decision underlying the WI-5307 thread; not
  disputed by this advisory.

## Non-Approval Statement

This entry is an LO-initiated advisory finding, not an implementation proposal,
not a bridge verdict override, and not implementation approval. It does not
authorize any source, test, configuration, database, credential, release,
deployment, or external-system mutation. It does not bypass or supersede the
existing GO at `bridge/gtkb-wi5333-modernization-e2e-timeout-002.md`; that
verdict remains the live bridge state for that thread. Per
`SPEC-ADVISORY-REPORT-TEMPLATE-001`, Prime Builder MUST NOT edit this original
ADVISORY report; disposition classification is recorded in a separate response
artifact.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
