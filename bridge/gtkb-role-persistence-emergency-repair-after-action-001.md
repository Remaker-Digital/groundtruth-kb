NEW
::init gtkb pb
::open build
bridge_kind: operational_state_change
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code emergency-repair worker; owner authorization DELIB-202667742
author_metadata_source: explicit_interactive_session_metadata

Document: gtkb-role-persistence-emergency-repair-after-action
Version: 001
Date: 2026-07-31 UTC

# After-Action: Emergency Repair of Interactive Role Persistence

This entry is an audit record under
`.claude/rules/governance-emergency-bootstrap-protocol.md` clause (b). It is
`WITHDRAWN` so it is preserved permanently in the append-only bridge audit trail
without entering any actionable queue. It is not a proposal and requests no verdict.

## Owner Authorization

`DELIB-202667742`, recorded at
`.gtkb-state/owner-decisions/20260731-role-persistence-emergency-repair.md`.
Owner directive: "Fix this now. I authorize you to bypass all blocking GOV and
perform an emergency repair to resolve this once and for all."

## Specification Links

- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` -- the violated constraint;
  clauses `CLAUSE-PERSISTENCE-ACROSS-BOUNDARIES`, `CLAUSE-AGENT-HINT-NOT-LOCK`,
  `CLAUSE-NO-DURABLE-REGISTRY-MUTATION`, `CLAUSE-DISPATCHER-SOT-FOR-DISPATCH`.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` -- the persistence decision.
- `GOV-SESSION-ROLE-AUTHORITY-001` -- durable vs session-stated authority split.
- `DCL-SESSION-ROLE-RESOLUTION-001` -- deterministic role-resolution table.
- `SPEC-1662` (GOV-18) -- assertion quality standard; the standard whose absence
  allowed the constraint's self-certifying assertions.
- `GOV-ARTIFACT-APPROVAL-001` -- formal-artifact approval evidence for the MemBase
  mutation described below.
- `GOV-FILE-BRIDGE-AUTHORITY-001` -- append-only bridge audit-trail discipline.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` -- specification-linkage
  discipline; cited because this record is filed on the bridge surface it governs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` -- spec-derived testing discipline;
  satisfied here by the behavioral regression module described below, though no
  `VERIFIED` verdict is sought.

## Prior Deliberations

- `DELIB-202667742` -- the owner emergency-repair authorization for this work.
- The owner-decision record cites `DELIB-202667524` / `DELIB-202667530` as the
  prior deliberations on unresolved-identity fail-closed handling, and WI-5815 as
  the live per-session identity isolation work item.
- Prior bridge threads on the same surface, preserved for lineage:
  `bridge/gtkb-wi5723-session-resolver-fallback-removal-001.md` and `-002`,
  `bridge/gtkb-wi5834-worker-session-role-downgrade-guard-001.md` and `-002`,
  `bridge/gtkb-wi5679-session-role-keying-continuity-*`,
  `bridge/gtkb-lo-role-resolution-fallback-privilege-escalation-advisory-001.md`.

## The Defect

`DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` requires that an explicit-direction
role established in an interactive transcript persist across compaction, resume,
and contiguous SessionStart-like boundaries, changing only when the owner
explicitly changes it, and that the registry role be a fallback hint rather than a
lock. The runtime implemented neither clause.

Verbatim producing expression, `scripts/session_self_initialization.py`
(line 7659 at the time of repair):

```python
role_source = (
    "dispatcher_composition"
    if dispatch_run_id
    else ("transcript_init_keyword" if role_profile_explicit else "session_resolver_fallback")
)
ensure_worker_session(
    project_root,
    harness_name=runtime_harness_name,
    harness_id=args.harness_id,
    session_id=worker_session_id,
    role=role_profile,
    role_source=role_source,
    ...
)
```

At a SessionStart-like boundary neither a dispatch composition nor a fresh init
keyword is present, so `role_profile` came from `discover_role_profile(...)` (the
durable registry) and `ensure_worker_session` then overwrote `role`,
`role_asserted`, and `role_resolved` unconditionally. The per-session role marker
recording the owner-declared role was never consulted at that boundary.

Live evidence captured at the start of this repair:

- `harness-state/claude/session-envelopes/bba2e933-5d36-4c5b-ad04-08a653c8700f.json`
  -- role/role_asserted/role_resolved `loyal-opposition`,
  `worker_role_provenance.role_resolution_source = "session_resolver_fallback"`,
  re-issued `2026-07-31T19:30:28Z`.
- `.claude/session/role-bba2e933-5d36-4c5b-ad04-08a653c8700f.json` -- role
  `prime-builder`, `source: "init_keyword"`, written `2026-07-31T06:21:41Z`. The
  transcript-declared role was captured and then ignored on re-issue.
- Harness B durable registry role `["loyal-opposition"]` -- the value the fallback
  wrote.

Why it survived: the DCL sat at status `specified` with five `grep_absent`
assertions over documentation files. Those assertions pass whether or not the
mandated behavior exists, so the constraint reported green continuously while
unimplemented, and no work item cited it.

## The Repair

`groundtruth-kb/src/groundtruth_kb/session/envelope.py` (+112 lines, additive):

- New `transcript_declared_role(project_root, session_id, *, envelope=None)`
  returns `(role, role_source)` when the session context already carries an
  owner-declared interactive role. Evidence order: the prior worker document's
  `role_resolution_source`, then the per-session role marker. The marker branch is
  what lets the role survive a boundary that re-creates the document or that has
  already overwritten it.
- `ensure_worker_session` consults that resolver before the create/refresh branch
  when, and only when, `role_source` is a registry-derived fallback. Explicit new
  owner direction still changes the role, and `dispatcher_composition` is untouched
  (`CLAUSE-DISPATCHER-SOT-FOR-DISPATCH`).
- The durable registry is never read for authority here and never written
  (`CLAUSE-NO-DURABLE-REGISTRY-MUTATION`); a regression test asserts registry bytes
  are unchanged.
- Fail-safe: every read/parse error in the resolver returns `None`, so any failure
  degrades to prior behavior. A role-resolution repair must never make a session
  unstartable.

`scripts/session_self_initialization.py` was deliberately NOT modified by this
repair; the fallback role source it emits is the trigger the resolver keys on.

## Assertion Upgrade (MemBase mutation)

This work DOES mutate MemBase. `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` was
updated from v1 to v3:

- v2 -- replaced the five documentation-only `grep_absent` assertions with six
  `grep` assertions that bind behavior: `def transcript_declared_role` and
  `if role_source in REGISTRY_FALLBACK_ROLE_SOURCES` in `envelope.py` (the second
  proves the resolver is wired, not merely defined), plus four assertions pinning
  named tests in the new regression module. One documentation assertion is retained
  as a supplement, not as the verification. All 7 assertions PASS.
- v3 -- status promoted `specified` -> `implemented`. NOT promoted to `verified`:
  this repair has no independent Loyal Opposition verification.

Formal-artifact approval evidence per `GOV-ARTIFACT-APPROVAL-001`, both citing
`DELIB-202667742`:

- `.groundtruth/formal-artifact-approvals/20260731-dcl-interactive-session-role-persistence-001.json`
- `.groundtruth/formal-artifact-approvals/20260731-dcl-interactive-session-role-persistence-001-promotion.json`

The promotion was initially blocked by the approval gate; the gate was satisfied
with a packet rather than bypassed. Verbatim gate output:

```
BLOCKED (GOV-ARTIFACT-APPROVAL-001): formal artifact mutation requires full
native-format display and approval evidence. Command matches a formal artifact
write path but does not reference GTKB_FORMAL_APPROVAL_PACKET or
--formal-approval-packet, and no matching on-disk packet could be auto-discovered
from --content-file + artifact id.
```

## Regression Test

`platform_tests/scripts/test_dcl_interactive_session_role_persistence.py`, 12
tests, all passing. Coverage: persistence across a fallback re-issue; persistence
when the document is re-created; recovery when a fallback overwrite already
happened; persistence across repeated boundaries; the negative case (no owner
declaration still resolves to the registry fallback); explicit owner role change;
dispatcher composition unaffected; registry bytes unmutated; and fail-safe handling
of corrupt, foreign, unknown-role, and non-transcript markers.

A negative control was run to prove the tests are not self-certifying: with the
resolver disabled, `test_transcript_role_survives_document_recreation` and
`test_transcript_role_is_recovered_after_a_fallback_overwrite` fail as expected.

## Gates Run

- `ruff check` -- PASS on both changed files (separate gate).
- `ruff format --check` -- PASS on both changed files (separate gate; the test
  module was reformatted once, then re-checked).
- New regression module -- 12 passed.
- Baseline before the change: `test_session_envelope_runtime.py`,
  `test_session_self_initialization.py`, `test_session_envelope_cli_provenance.py`
  = 4 failed, 156 passed. After the change the same suites plus the new module were
  run during a window in which a concurrent session had left
  `envelope.py` in a transient `NameError` state
  (`INTERACTIVE_ROLE_SOURCES` referenced with its definition removed), producing 3
  additional failures attributable to that session, not to this repair. This repair
  was verified in isolation instead: the exact intended commit content (HEAD plus
  only this repair's hunks) was reconstructed and the full regression module run
  against it, 12 passed / 0 failed, with `ruff check` and `ruff format --check`
  clean. The concurrent session subsequently removed its own hunks, and the
  worktree file now contains only this repair's 112 additive lines.

## Live-Case Verification

Against the real artifacts for session `bba2e933-5d36-4c5b-ad04-08a653c8700f`:

- Read-only: `transcript_declared_role(<project root>, <session id>)` returns
  `('prime-builder', 'transcript_init_keyword')`.
- Replica: the real worker document, role marker, harness identity, and harness
  registry were copied into a temporary root and the fallback re-issue performed;
  the re-issued document resolves `prime-builder` with
  `role_resolution_source = transcript_init_keyword`, and the registry file bytes
  are unchanged. The live shared projection was deliberately not written because
  other sessions read it.
- The live worker document itself now reads `prime-builder` /
  `transcript_init_keyword`, issued `2026-07-31T20:27:34Z`, having been
  `loyal-opposition` / `session_resolver_fallback` at `19:30:28Z`. Attribution
  caveat: that flip occurred while a concurrent session was also editing this
  surface, so it is not claimed here as proof produced solely by this repair. The
  isolated and replica results above are the controlled evidence.

## Bypass Scope Used

Bypassed under `DELIB-202667742`: the propose/GO/implement bridge cycle for this
repair, the work-intent claim gate, the implementation-start authorization packet
gate, and the role-eligibility gate (the defect itself, which denies this session).

Not bypassed and honored throughout: credential scanning, the project-root boundary
(all work inside `E:\GT-KB`), append-only bridge audit-trail discipline (no bridge
file modified or deleted), and truthful reporting.

Two further gates fired and are recorded verbatim rather than silently bypassed.

1. A PreToolUse governance hook, twice, on edits to `envelope.py`:

```
[Governance] Bridge proposal for this module has NO-GO status. Review Codex
findings at bridge/gtkb-wi5269-activity-envelope-authority-validators before
implementing.
```

That thread is real (`bridge/gtkb-wi5269-activity-envelope-authority-validators-008.md`,
latest status `NO-GO`) but belongs to unrelated work (WI-5269 activity-envelope
authority validators). The bridge cycle is inside the authorized bypass.

2. The git execution-boundary gate, on `git read-tree` and again on a command
string containing git verbs:

```
BLOCKED (GTKB-GIT-LIFECYCLE): direct `git read-tree` is not an authorized
execution boundary. Use the canonical `python -m groundtruth_kb.git_lifecycle`
operation so current authority, scope binding, quiescence, recovery, and evidence
are enforced at effect time.
```

The canonical `create` / `attach` / `preserve` flow creates and switches a
work-item branch, which is unsafe while other sessions are active on the current
branch, so the commit was attempted through a pathspec-limited `git commit` with
hooks enabled (no `--no-verify`, so credential scanning would still run).

## Commit Status: NOT COMMITTED (blocked, not forced)

No commit SHA can be recorded. `git add` and `git commit` fail on a stale index
lock that predates this session:

```
fatal: Unable to create 'E:/GT-KB/.git/index.lock': File exists.
```

Evidence that it is stale rather than contended: the file is 0 bytes, its mtime is
`2026-07-31 16:21:28Z` (over four hours before this repair began) and never changed
across eight retries at 25-second intervals, and no `git` process is running. It
therefore blocks commits for every session, not only this one.

Deleting shared repository state was judged outside the authorized bypass list,
which covers governance process gates, not repository-state surgery, and Git's own
guidance requires certainty that no git process is active. The repair was left
complete and verified in the worktree rather than forced through.

To land it, clear the stale lock (owner action, or the governed
`python -m groundtruth_kb.git_lifecycle recover` path) and then run, from the
project root:

```
git add -- platform_tests/scripts/test_dcl_interactive_session_role_persistence.py \
  .groundtruth/formal-artifact-approvals/20260731-dcl-interactive-session-role-persistence-001.json \
  .groundtruth/formal-artifact-approvals/20260731-dcl-interactive-session-role-persistence-001-promotion.json
git commit -- groundtruth-kb/src/groundtruth_kb/session/envelope.py \
  platform_tests/scripts/test_dcl_interactive_session_role_persistence.py \
  .groundtruth/formal-artifact-approvals/20260731-dcl-interactive-session-role-persistence-001.json \
  .groundtruth/formal-artifact-approvals/20260731-dcl-interactive-session-role-persistence-001-promotion.json
```

Commit subject:
`fix(session): persist transcript-declared interactive role across session boundaries (DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001)`

`scripts/session_self_initialization.py` carries an unrelated concurrent session's
edit and must NOT be included.

The MemBase assertion upgrade and the DCL promotion are already durable; they do
not depend on the commit.

## Follow-On

The owner-offered read-only audit of every DCL at status `specified` whose
assertions are documentation-only greps remains open. That set is, by construction,
the platform's blind spot: constraints that report green whether or not they are
real. WI-5815 is the natural home.
