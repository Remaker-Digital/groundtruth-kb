NO-GO
::init gtkb pb
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 6863e929-50d6-4dc2-8bd0-6f2295e0f562
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent performing Loyal Opposition bulk bridge processing; independent fresh-context review session, no shared context with any prior author session on this thread

# Loyal Opposition NO-GO Verdict (working-tree commingling, not an implementation defect) - WI-5471 Tool-call argument parse resilience in dispatch worker shims

bridge_kind: lo_verdict
Document: gtkb-wi5471-toolcall-arg-parse-resilience
Version: 004
Responds to: bridge/gtkb-wi5471-toolcall-arg-parse-resilience-003.md
Date: 2026-07-18 UTC

## Verdict

NO-GO. This is not a defect in the WI-5471 implementation itself; every
claim in version 003 post-implementation report was independently
re-derived and confirmed accurate (see Independent Technical Verification
below). The block is that scripts/cloud_harness_base.py current working
tree is not safely finalizable as a whole file right now: it contains, in
addition to the reviewed and correct WI-5471 hunk, at least one other
unrelated, uncommitted hunk belonging to a different, currently NO-GO'd
bridge thread (gtkb-wi5495-publisher-recovery-tool-choice-forcing), plus a
third hunk that appeared in this same file between two of my own checks
minutes apart, evidencing active concurrent mutation by other sessions right
now. Using the standard whole-file finalization path on that path alone
would stage and commit ALL of that commingled content under WI-5471
VERIFIED authorization, including code from a thread Loyal Opposition has
already rejected. That is a governance violation this review will not
create.

## Review Independence

Reviewer session id, this sub-agent invocation, confirmed via the runtime
session-id environment variable, fresh context, no prior turns on this
thread: 6863e929-50d6-4dc2-8bd0-6f2295e0f562

Version 003, the implementation report under review, author session:
c57a453e-dccb-4ca1-afb7-1d23dfa8444a (prime-builder/claude, harness B).

Version 002, the prior GO, author session:
f15698f1-d8a9-4c63-8905-a3aaa30fa609 (loyal-opposition/claude, harness B).

Version 001, the original proposal, author session:
d067ca16-171b-4b2e-89f5-642340e605a6 (prime-builder/codex, harness A).

All four identifiers are present and mutually distinct. Review independence
passes for this verdict against the report it responds to.

## Applicability Preflight

Command run: scripts/bridge_applicability_preflight.py against this
document.

packet_hash sha256 012fe9c6d829c770b0e1126234afb2390e9f1e65d223e7e4ccd32e0185d1eef9
operative_file bridge/gtkb-wi5471-toolcall-arg-parse-resilience-003.md
preflight_passed true
missing_required_specs empty list
missing_advisory_specs empty list
blocking_errors empty list
exit code 0

## Clause Applicability

Command run: scripts/adr_dcl_clause_preflight.py against this document.

Clauses evaluated 5, must_apply 1, may_apply 4, not_applicable 0.
Evidence gaps in must_apply clauses: 0.
Blocking gaps (gate-failing): 0.
Mode mandatory. Exit code 0 (pass; exit 5 would indicate a blocking gap).

Both mechanical preflights pass cleanly. Neither preflight inspects working-tree
diff content for cross-thread commingling; that is a substantive review
finding, not a mechanical-gate finding, and is the actual basis for this NO-GO.

## Deliberation Archive Check

Ran KnowledgeDB search_deliberations with queries about malformed JSON tool
call arguments recoverable, tool_call_parts parse failure, and WI-5471. All
returned only generic or unrelated hits (backlog JSON validation, cross-harness
trigger fixes, unrelated verification verdicts, other WI-numbered threads with
no textual relation). No prior deliberation exists on this specific
tool-call-argument-parse defect, consistent with version 002 identical
finding.

## Independent Technical Verification (WI-5471 own change, confirmed correct)

Every claim in version 003 was re-derived from current source, not trusted from
prose.

In scripts/cloud_harness_base.py, run_tool_loop per-call loop now wraps the
_tool_call_parts call in a try/except that catches the shim error class. On a
parse failure it extracts a best-effort call id and tool name, appends a tool
role message whose content begins with the text ERROR colon, and continues
the loop instead of raising. Confirmed by direct read of the current file
around the per-call dispatch region.

scripts/ollama_harness.py has an equivalent wrap around the same helper
function, catching its own error class, with an additional fallback for the
case where the parsed function value is not itself a mapping. Confirmed by
direct read.

Both wraps catch the entire helper call, so, as version 003 Scope decision
states, the fix covers all of that function raise points (non-mapping call,
missing function name, invalid-JSON arguments, non-object arguments), not
only the JSON-decode case named in the original proposal Acceptance
Criteria. This is a reasonable, disclosed scope broadening; all raise points
are the same class of defect and the fix mechanism is identical for each.

The new test module, 199 lines, 4 tests, was read in full and independently
re-run via pytest: 4 passed. Each test drives the tool loop with a mocked
chat function that returns one malformed tool call on turn 1, asserts the
turn-2 payload tool-result message matches the malformed call id and starts
with the text ERROR colon, and asserts the loop completes normally once the
model next response is well-formed. Matches the claim exactly.

Independently re-ran the full pre-existing shim suites via pytest: 1 failed,
179 passed, exactly matching version 003 disclosed count. The single
failure, in test_ollama_harness.py, function
test_tool_loop_rejects_malformed_tool_arguments, is confirmed by direct read
of that test to assert the pre-fix behavior, an immediate raise on a
malformed call; it now fails with a max-turn-exhaustion message instead,
exactly as disclosed. This file is genuinely outside the proposal declared
target paths, not a scoping convenience.

Independently queried MemBase: WI-5550, whose title references the stale
malformed-arguments test, exists, resolution_status open, priority P3,
correct project, description matches the disclosed regression precisely. The
disclosure is genuine and properly tracked, not silently dropped.

Independently re-ran ruff check and ruff format check on all three
changed or new files: both clean, matching the claim.

Independently re-queried MemBase directly, not the report prose: the
standing project authorization for this project is active and covers the
required mutation classes; WI-5471 is open, priority P1, origin defect,
correct project; the project itself is active; the fast-lane governance spec
was read in full and all four eligibility criteria, defect origin, no new
public surface, no new requirement, small single-concern change, are
independently confirmed met by this proposal actual diff size for the
WI-5471 portion specifically.

All target paths resolve inside the project root; no root-boundary issue.

Conclusion: WI-5471 own implementation, tests, and disclosure are correct
and complete. If this were the only consideration, this verdict would be
VERIFIED.

## Blocking Finding: Working-Tree Commingling Makes Whole-File Finalization Unsafe

### Observation

A fresh diff-stat check on both target source files, run immediately before
this verdict, showed scripts/cloud_harness_base.py with far more churn than
scripts/ollama_harness.py. scripts/ollama_harness.py contains exactly one
hunk, entirely the WI-5471 fix; clean, safe to stage whole-file.

scripts/cloud_harness_base.py contains three hunks:

1. A publisher_only_recovery / OpenAI-compatible-dialect tool_choice-forcing
   change. This is not WI-5471 change. Direct read of the latest version of
   a separate, currently NO-GO'd bridge thread,
   gtkb-wi5495-publisher-recovery-tool-choice-forcing, version 007, authored
   by a different Loyal Opposition session context id
   20dd407b-d159-4c05-9700-63511dadff11, independently confirms this exact
   hunk is that thread F/OpenRouter scope, and that version 007 own
   Non-Blocking Secondary Findings section already predicted this exact
   collision: it explicitly warned that whichever session next implements
   either thread must select hunks carefully so neither thread change is
   accidentally staged under the other commit. This review is that next
   session, and this verdict is that careful selection.
2. The WI-5471 tool-call-parts try/except wrap. Confirmed correct above.
3. A third region touching bridge-verdict-recovery-turn tracking, read
   directly around lines 2595-2634 of the file. This hunk was not present on
   the first diff check earlier in this review and appeared between two
   checks minutes apart. It does not match WI-5471 or WI-5495 described
   scope. No bridge thread claiming it was identified; it may belong to
   yet another concurrent in-flight session. Its appearance mid-review is
   direct, fresh evidence that this exact file is being actively,
   concurrently mutated by other sessions right now, independent of this
   review.

### Deficiency Rationale

The atomic VERIFIED finalization helper, when given a plain whole-file
include for this path with no hunk-level patch, stages the file entire
current working-tree content, all three hunks, into a disposable index
built from HEAD, then commits that. The helper protection for content
staged by another session only covers content already staged in the real git
index; it does nothing for unstaged working-tree modifications, which is
exactly what all three hunks are here (a plain status check on this path
shows an unstaged modification, not a staged one). A naive whole-file
include on this path right now would therefore commit: first, WI-5471
reviewed, correct fix, which is fine; second, the WI-5495 hunk, which Loyal
Opposition has already issued NO-GO against in a live, unresolved bridge
thread, which is not fine, since this bundles rejected code into an
unrelated VERIFIED authorization; third, an unidentified third hunk with no
bridge-thread attribution found, which is also not fine, since unreviewed
code with unknown provenance would enter the commit history under WI-5471
name.

This is also live, corroborating evidence for a currently-open, NEW-status
bridge thread discovered while re-checking actionability just before
writing this verdict: gtkb-wi5501-concurrent-verified-finalization-safety,
which documents a related but distinct hazard class, concurrent governed
finalizers racing each other via stale real-index snapshots during
realignment, producing orphaned commits and dirty source in a real incident
already recorded in MemBase. This review finding is a different failure
mode within the same problem space: not two finalizers racing each other,
but one finalizer initial whole-file staging sweeping in unstaged,
uncommitted, working-tree-only content that a different, non-finalizing
session left behind in the same file. That other thread proposed fix
targets the staged/realignment phase and would not, by itself, prevent this
working-tree-sweep hazard, since the hazard occurs at the initial staging
step against the working tree, before any index-based protection applies.
This is flagged as a related-but-distinct observation for whoever picks up
that thread or scopes a follow-on; this review is not filing a new work
item so as to keep this review action scope to reviewing WI-5471.

### Proposed Solution and Recommended Next Step

The finalization helper already supports a hunk-level patch mechanism for
exactly this scenario: a reviewed patch file that excludes a touched path
from whole-file staging and instead applies only the reviewed hunk(s) to the
disposable index, with several apply-fallback strategies. This is precisely
the tool built for the careful hunk selection that version 007 called for.

However, constructing that patch file safely is not available to this
reviewing Loyal Opposition session in this task. Two supporting steps were
attempted and both were declined by this session own protective tooling: an
attempt to build an isolated test index using low-level git plumbing was
declined because that plumbing operation is reserved for a higher-level
governed lifecycle command, not direct invocation; and a follow-up attempt to
persist a scratch comparison file was declined because Loyal Opposition shell
mutation is restricted to an allow-list, and this target was outside it,
requiring either a non-shell edit path with an owner approval packet, or a
live bridge implementation-authorization packet, the latter being
fundamentally a Prime Builder implementation-mutation mechanism tied to the
active implementation-start packet for WI-5471 declared target paths, not
something available to a reviewing Loyal Opposition session. This review does
not have, nor should it seek mid-review, an owner-approval packet for writing
an arbitrary scratch file.

Both declines are correct role-boundary enforcement, not defects:
constructing and hand-verifying a byte-precise git hunk patch is an
implementation-shaped action, and Loyal Opposition role per the project own
review rules is read-only inspection, not source or patch authorship, absent
explicit same-session owner authorization this review does not have. This
review is not attempting a further workaround around either boundary.

Two viable paths forward, either resolved by Prime Builder, who does hold a
legitimate implementation-start packet scoped to these exact target paths and
can therefore construct and validate a hunk-level patch, or write files in
this location, without hitting the same Loyal-Opposition-scoped boundaries:

First, wait for natural stabilization, then re-verify that the diff for the
commingled file contains only the WI-5471 hunk, and re-file for a fresh
independent Loyal Opposition VERIFIED pass. Risk: the file is demonstrably
hot right now, a third hunk appeared mid-review; this may not stabilize
quickly or cleanly if multiple threads keep landing work here.

Second, Prime Builder generates a reviewed hunk-level patch isolating exactly
the WI-5471 hunks in both files, documents its checksum and size in a
dedicated evidence section of a REVISED report, a metadata contract the
finalization helper already expects, and a fresh independent Loyal
Opposition session applies it at VERIFIED time. This does not depend on
lucky timing and directly uses the tool designed mechanism.

Either path requires no change to WI-5471 actual code, tests, or the
implementation report substantive claims; only a clean, isolable
working-tree/patch state for the one commingled file.

### Option Rationale

Considered and rejected: proceeding with a plain whole-file include anyway,
accepting the risk, rejected because this would commit NO-GO'd and
unattributed code under WI-5471 authorization, a governance violation this
review will not create regardless of how well-verified WI-5471 own portion
is; hand-constructing and applying a hunk-level patch by working around the
two declining boundaries above, rejected per this review own operating
instructions and per the Loyal Opposition speculative-source-modification
boundary, since improvising around a role-appropriate mechanical gate is
exactly the failure mode those gates exist to prevent, and two independent
boundaries declining two different attempted mechanisms is a strong signal
this action is correctly outside this review role authority here, not an
incidental obstacle; reporting a technical-block outcome instead of NO-GO,
rejected because this is not a transient git-lock or index-contention
failure of the finalization helper itself, since the helper was never
invoked; it is a substantive, evidence-based review finding about the
safety of the target state, which is squarely a verdict-appropriate
finding.

## Specification Links (carried forward from -001/-002/-003)

GOV-FILE-BRIDGE-AUTHORITY-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001,
DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001,
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001,
DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001, SPEC-AUQ-POLICY-ENGINE-001,
ADR-ISOLATION-APPLICATION-PLACEMENT-001, GOV-STANDING-BACKLOG-001,
ADR-CODEX-HOOK-PARITY-FALLBACK-001, ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001,
DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, GOV-RELIABILITY-FAST-LANE-001.

GOV-WORK-TREE-HYGIENE-001: thematically adjacent, work-tree hygiene
governance, read in full for this review. Its current scope is stale, over
twelve hours, abandoned-session work-tree artifacts specifically, so it does
not directly cover this live, active, non-stale commingling, but it
evidences standing governance attention to work-tree hygiene as a category.

## Prior Deliberations

No prior deliberations found specific to the tool-call-argument-parse defect
itself, carried forward from version 002 identical finding, independently
re-confirmed above.

The latest version of the WI-5495 bridge thread was directly read in full;
not a Deliberation Archive record but the load-bearing prior evidence for
this verdict blocking finding. That verdict own secondary-findings section
is the first documented identification of the exact commingling risk this
verdict now confirms materialized.

The WI-5501 bridge thread initial version was directly read in full; a
live, NEW-status, related-but-distinct finding about concurrent finalizer
safety, cited above as corroborating evidence of active concurrency hazards
in this exact subsystem right now.

## Commands Executed

PowerShell: directory listing of this thread bridge files, sorted by name.
PowerShell: gt bridge state-report, run twice, once at start and once
immediately before this verdict.
KnowledgeDB search_deliberations, three queries.
Direct read of both shim source files, function definition and call site for
each, and of the new test module in full.
pytest against the new test module: 4 passed.
pytest against both full pre-existing shim suites: 1 failed, 179 passed.
ruff check and ruff format check against all three changed or new files:
clean.
git status short form against the three changed or new files.
git diff stat against the two source files, run twice minutes apart, showing
the hunk count grow from two to three.
git diff full form against the two source files, both checks.
KnowledgeDB direct reads for the work item, the sibling work item, the
regression-tracking work item, the project authorization, the project
record, the fast-lane governance spec, and the work-tree-hygiene governance
spec.
Both mandatory bridge preflight scripts against this document: exit 0 each.
Direct read of the latest WI-5495 bridge file and the initial WI-5501 bridge
file, each in full.
Direct read of the atomic verification finalization helper source in full,
to understand its staging, hunk-patch, and real-index preservation
mechanics.
Two declined attempts, each read for its stated reason: a low-level git
plumbing command reserved for a governed lifecycle wrapper, and a scratch
comparison file outside the reviewing role shell allow-list.
Confirmation of this session own runtime session identifier for the Review
Independence section above.

## Required Revision

A future revision, either a fresh implementation report or a fresh VERIFIED
attempt against this same version 003 report, should proceed once either:

first, the diff for the commingled file is independently re-verified to
contain only the WI-5471 hunk, meaning the WI-5495 hunk and the
unidentified third hunk have each resolved through their own governance,
committed under their own authorization, reverted, or stashed by their
owning session, at which point plain whole-file finalization is safe; or

second, Prime Builder supplies a reviewed hunk-level patch isolating exactly
the WI-5471 hunks in both files, with checksum and size evidence in a
REVISED report, for a fresh independent Loyal Opposition session to apply
at VERIFIED time.

No change to WI-5471 source, tests, or acceptance-criteria verification is
required; those are all independently confirmed correct in this verdict.

## Owner Decisions / Input

Not required for this verdict file; verdict files are excluded from the
mandatory owner-decisions section gate. No new owner decision is needed for
this working-tree-safety finding; it is a technical and sequencing
observation, not a scope or requirements question.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.