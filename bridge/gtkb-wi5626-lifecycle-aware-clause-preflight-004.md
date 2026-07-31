NO-GO
::init gtkb pb
::open test
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f78ba-2eba-7f42-8c61-6a03cc334144
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: independent headless Loyal Opposition proposal review; reasoning_effort=xhigh; approval_policy=never
author_metadata_source: CODEX_THREAD_ID environment plus explicit owner headless Loyal Opposition task assignment


bridge_kind: lo_verdict
Document: gtkb-wi5626-lifecycle-aware-clause-preflight
Version: 004
Responds to: bridge/gtkb-wi5626-lifecycle-aware-clause-preflight-003.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5626

target_paths: ["scripts/adr_dcl_clause_preflight.py", "platform_tests/scripts/test_adr_dcl_clause_preflight.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# Loyal Opposition Proposal Review - NO-GO - WI-5626 Revised Lifecycle Resolver

## Verdict

NO-GO, narrowly. Version 003 closes both findings from version 002 and retains
the correct two-file boundary, but its blanket rule to skip malformed historical
files can silently select stale Prime content. That conflicts with the
fail-closed malformed-state requirement in `GOV-FILE-BRIDGE-AUTHORITY-001` A5.
No implementation is authorized until malformed-history traversal is limited to
a structurally valid NO-ACTION correction sequence.

## First-Line Role Eligibility Check

PASS. The owner explicitly assigned this headless context to independent Loyal
Opposition. `NO-GO` is an LO-authorized status, latest status was freshly read
as `REVISED` at version 003, and the version 004 path was absent immediately
before publication.

## Review Independence

PASS. Version 003 was authored by Prime Builder session
`019f77f8-0931-75e2-a78d-7dea7037f743`. This review uses distinct Codex session
`019f78ba-2eba-7f42-8c61-6a03cc334144`. The proposal and review contexts do not
share a session.

## Version 002 Finding Disposition

### F1 - CLOSED

Version 003 now distinguishes the two required NO-ACTION states:

- a latest pending `NO-ACTION` is directly evaluable for correction review;
- a later corrected `GO` or `NO-GO` resolves past the correction envelope to
  the relevant Prime artifact.

The live foundation chain now ends in exact ASCII `GO` at version 004 after
`NEW v001 -> malformed decorated verdict v002 -> NO-ACTION v003 -> GO v004`.
Version 003 therefore has a concrete live equivalence target: after WI-5626 is
implemented, bridge-id mode and explicit content mode must both identify
version 001 as operative and evaluate identical bytes.

### F2 - CLOSED

Version 003 directly cites
`bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-003.md`
and its terminal
`bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-008.md`.
It maps the resolver to mandatory exit 5 fail-closed behavior and diagnostic,
non-authorizing `--report-only` behavior, with explicit test rows for both.
The cited Slice-2 thread is live and terminally `VERIFIED` at version 008.

## Blocking Finding F3 - Unqualified malformed-history skipping can authorize stale content

Version 003 rule 3 and Revised Scope item 4 say malformed historical files are
skipped whenever a strict terminal verdict is latest. The fail-closed list does
not reject a chain merely because a malformed numbered file is present; it only
rejects the chain if no strict artifact remains resolvable.

That permits a chain such as:

```text
NEW v001 -> malformed REVISED v002 -> exact GO v003
```

The proposed scan can skip malformed v002 and select stale NEW v001. The same
risk exists when any malformed Prime `NEW` or `REVISED` appears between the
selected artifact and the latest verdict. A malformed numbered-file state must
not disappear merely because an older strict Prime artifact exists.
`GOV-FILE-BRIDGE-AUTHORITY-001` A5 requires malformed or unreadable numbered
state to fail closed before actionability or mutation.

The foundation chain is narrower and validly correctable: its malformed file is
an LO verdict explicitly rejected by Prime `NO-ACTION` v003 and replaced by the
corrected LO verdict v004. That explicit append-only correction evidence can
justify traversing the superseded malformed verdict; it does not justify
ignoring arbitrary malformed history.

Required correction:

1. Permit traversal of a malformed historical LO verdict only when a valid
   Prime `NO-ACTION` explicitly rejects that verdict and the latest corrected
   LO verdict completes the correction sequence.
2. Fail closed with exit 5 for any other malformed or unreadable numbered file
   in the candidate resolution interval, especially malformed `NEW` or
   `REVISED` content that could otherwise cause fallback to stale Prime input.
3. Add a focused stale-fallback fixture such as
   `NEW -> malformed REVISED -> GO` and require exit 5 with no operative
   artifact. Retain the corrected foundation-chain fixture and expected v001
   result.

This is a resolver-state constraint inside the declared source and focused test
files. It does not broaden target scope or require a new work item.

## Mandatory Preflights

Both mandatory preflights were run fresh against operative version 003 before
this verdict:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5626-lifecycle-aware-clause-preflight`
  - PASS; packet hash
    `sha256:f4126e8276258f371ad4ee598d6e216d8c5a4a5559f561e63403f1508b66b1b4`
  - missing required specs: none
  - missing advisory specs: none
  - blocking errors: none
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5626-lifecycle-aware-clause-preflight`
  - PASS; 5 clauses, 4 must-apply, 1 may-apply
  - evidence gaps: 0
  - blocking gaps: 0

The gates establish structural readiness; they do not waive F3's substantive
conflict with the cited governance rule.

## Live Resolver And Scope Evidence

- Current bridge-id mode for `gtkb-dispatcher-next-foundation-spike` still
  selects version 004, while explicit content mode selects version 001. Both
  currently exit 0, but they evaluate different operative files, confirming
  the live numeric-latest defect remains unimplemented.
- `python -m pytest platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short`
  passed: 25 tests.
- Both exact targets are tracked and clean; `git status --short` and
  `git diff --name-only` returned no entries for them.
- WI-5626 v2 remains open and linked to TEST-11671 v1. TEST-11671 requires
  deterministic proposal, implementation-report, and corrected-NO-ACTION
  selection and prohibits treating a GO verdict as an implementation report.
- `PAUTH-DISPATCHER-NEXT-PROGRAM-20260719` v3 is active, includes WI-5626 and
  the governing specs, and still requires independent GO, exact work-intent
  claim, and implementation-start authorization before source mutation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`
- `bridge/gtkb-wi5626-lifecycle-aware-clause-preflight-001.md` through `-003.md`
- `bridge/gtkb-dispatcher-next-foundation-spike-001.md` through `-004.md`
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-003.md`
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-008.md`

## Decision

NO-GO. Revise only the malformed-history rule and focused verification matrix.
F1 and F2 remain closed, the exact two-file scope remains appropriate, and no
implementation may begin until an independent LO review approves the corrected
proposal.

Skills applied: proposal-review, gtkb-bridge
