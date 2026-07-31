NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b34d5b84-5746-4eee-bd95-b6eeb3e70715
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; transcript-resolved role prime-builder via ::init gtkb pb; CF-10 serialization leadership held per DELIB-20260730-CF10-LEADER-GRANT-B34D5B84
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5723-session-resolver-fallback-removal
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5723

target_paths: ["scripts/session_self_initialization.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/modernization/workflow.py", "platform_tests/scripts/test_modernization_end_to_end_workflow.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation: this proposal performs no MemBase mutation and no
`groundtruth.db` write, insert, edit, or lifecycle change.

# WI-5723 narrow slice — remove `session_resolver_fallback` from the session-envelope write path

## Problem — reproduced live

On 2026-07-31 an interactive Prime Builder session lost owner-granted
authority mid-work. Session `b34d5b84-5746-4eee-bd95-b6eeb3e70715` had
declared Prime Builder via the canonical init keyword and its session document
recorded `role_resolved: prime-builder` /
`role_resolution_source: transcript_init_keyword`. That document was later
rewritten in place to `role_resolved: loyal-opposition` /
`role_resolution_source: session_resolver_fallback`. The session could no
longer mint `go_implementation` claims and could not obtain an
implementation-start packet for any GO'd work. Recovery required the owner to
re-declare the init keyword.

## Root cause

**One producer.** `scripts/session_self_initialization.py:7659-7663`:

```python
dispatch_run_id = os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID") or None
role_source = (
    "dispatcher_composition"
    if dispatch_run_id
    else ("transcript_init_keyword" if role_profile_explicit else "session_resolver_fallback")
)
```

`role_profile_explicit` is true only when `--role-profile` or a matching
`GTKB_BRIDGE_DISPATCH_KEYWORD` is supplied. Otherwise `role_profile` is set
from `discover_role_profile()`, which reads the **durable registry role**. So
`session_resolver_fallback` never travels alone — it always carries the
registry role in place of the session's actual role. The label is the symptom;
the substituted role value is the defect.

**Unguarded application.** `groundtruth-kb/src/groundtruth_kb/session/envelope.py`,
`ensure_worker_session()`: when the document already exists and is open, all
five role fields (`role_asserted`, `role_resolved`, `role`,
`role_resolution`, `worker_role_provenance`) are overwritten unconditionally
from the incoming `role_source`, with no comparison against the provenance
already recorded.

**Trigger.** The write is gated on `startup_emit_requested`, whose only live
invoker is the SessionStart dispatch core. It therefore fires at SessionStart
and SessionStart-like boundaries (resume, compaction) — not on every prompt.
The observed sequence: SessionStart #1 creates the document with the registry
role; the owner types `::init gtkb pb` and `workstream-focus.py` rewrites it
to `prime-builder`/`transcript_init_keyword`; a resume or compaction fires
SessionStart #2; line 7662 recomputes the registry role plus the fallback and
silently reverts it.

**Empirical scale.** 414 currently-open envelopes carry the fallback, and
their (harness, role) distribution matches the durable registry almost
exactly — 372 `claude`/`loyal-opposition`, 19 `codex`/`prime-builder`, 15
`cursor`/`loyal-opposition` — confirming the fallback reproduces the registry
role rather than any session-declared role.

## Governing direction

- `WI-5723` D1: there should not be a `session_resolver_fallback` at all.
- `DELIB-202667530` (2026-07-29): the explicit direction used to initialize
  the session envelope is canonical and supersedes all other information
  related to assigned role; superseded on contact is "any resolution path
  that outranks the session envelope's explicit init direction with any other
  source."
- `DELIB-202667524` Decision 1 (CF-01/CF-02): unresolved identity must FAIL
  CLOSED rather than fall back to the durable registry role.

`DCL-SESSION-ROLE-RESOLUTION-001` is cited here as **governing intent only**.
Its v7 approval packet is defective per the WI-5679 v016 NO-GO finding F1
(the packet omits the changed `assertions` field and the DCL still cites a
retired GOV). This proposal does **not** claim v7 as satisfied prerequisite
evidence; packet repair remains with WI-5718.

## Proposed Change

### C1 — remove the fallback at the producer (the actual fix)

In `scripts/session_self_initialization.py`, when neither `dispatch_run_id`
nor `role_profile_explicit` is present, **skip the `ensure_worker_session`
call entirely** rather than writing a fabricated role. Delete the
`session_resolver_fallback` literal.

This is safe at this call site: the return value is already discarded, and the
startup report renders `role_profile` independently, so no startup rendering
depends on the write. Resumed sessions are no longer overwritten and the
transcript role survives. Fresh sessions have no envelope until the owner
declares one, and downstream consumers fail closed through
`resolve_worker_role_provenance` with "Worker role provenance is missing for
the current session" — already the documented contract.

### C2 — defense-in-depth guard at the applier

In `envelope.py` `ensure_worker_session()`, refuse to overwrite a recorded
**interactive** role source (`transcript_init_keyword`, `owner_init_keyword`,
`interactive_transcript_explicit`) with a non-interactive incoming source on
an already-open document. C1 removes the only current producer; C2 ensures
that no future or hand-written caller can reintroduce the downgrade through
one of the five other `ensure_worker_session` call sites.

### C3 — fail closed on any residual value

Delete `session_resolver_fallback` from `TRUSTED_WORKER_ROLE_SOURCES` in
`modernization/workflow.py` so any envelope still carrying it fails closed at
the trust gate.

**Correcting a claim from the withdrawn `gtkb-wi5834-...-001`:** that filing
asserted removing the entry "would break headless dispatch." That is not
supported by the code. `scripts/dispatcher_runtime.py` sets
`env["GTKB_BRIDGE_POLLER_RUN_ID"] = dispatch_id` before spawn, so a dispatched
worker always takes the `dispatcher_composition` branch and can never produce
the fallback. The dispatcher additionally pre-creates the document with
`role_source="dispatcher_composition"`, and two gates
(`check_dispatched_role_bootstrap.py`, `check_modernization_release_candidate.py`)
already hard-reject anything other than `dispatcher_composition` for
dispatched workers. Dispatch cannot regress from C3.

### C4 — tests

- Update `test_modernization_end_to_end_workflow.py::test_registry_fallback_role_cannot_override_registry_default`:
  it currently asserts the message `"role is not active"`, which is only
  reachable if the fallback *passes* the trust gate. After C3 the trust gate
  fires first, so the expected message changes. Its mirror
  (`test_interactive_transcript_role_overrides_registry_default`) is
  preserved unchanged.
- Swap the fixture literal in `test_session_self_initialization.py` and
  `test_session_envelope_cli_provenance.py` (no assertion change; the latter
  asserts only `subject`).
- **New regression test:** a SessionStart occurring after `::init` must not
  revert the transcript-declared role. No such test exists today, which is
  why this defect shipped.

### Out of scope

- WI-5723's broader removal of worker-facing directives to consult
  TAFE/dispatcher configuration — a later slice.
- The shared per-harness singleton and `.claude/session/envelope.json`
  projection collision — owned by `WI-5749`/`WI-5747`.
- Backfill of the 414 existing fallback-bearing envelopes. They are inert:
  `_validate_worker_role_provenance` requires the provenance `session_id` to
  equal the current session id, and session ids are not reused, so a stale
  document can never authorize a future session.
- Ad-hoc provenance values in ~12 open envelopes — captured separately as
  `WI-5835` per owner decision.

## Requirement Sufficiency

Existing requirements sufficient. `WI-5723` D1, `DELIB-202667530`, and
`DELIB-202667524` Decision 1 already determine the required behavior. No new
or revised requirement is needed; this restores conformance.

## Specification-Derived Verification

| Requirement | Verification | Expected result |
| --- | --- | --- |
| C1 removes the producer | Grep for the literal across the tree | Zero occurrences outside tests and this thread |
| C1 preserves transcript role across SessionStart | New regression test: declare role, simulate SessionStart re-run without keyword | `role_resolved` and provenance unchanged |
| C1 fresh session fails closed | SessionStart with no prior document and no keyword | No envelope written; `resolve_worker_role_provenance` raises "missing for the current session" |
| C2 blocks non-interactive overwrite | Open document with each of the 3 interactive sources; attempt overwrite with a non-interactive source | Recorded role and provenance preserved in all 3 |
| C2 permits owner re-declaration | Interactive document; incoming `transcript_init_keyword` with a different role | Role changes |
| C2 permits dispatcher composition | Interactive document; incoming `dispatcher_composition` | Not suppressed |
| C3 residual envelopes fail closed | Envelope carrying the removed value through `_resolve_workflow_actor` | Raises at the trust gate |
| Dispatch unaffected | `test_dispatcher_runtime` suite; confirm `GTKB_BRIDGE_POLLER_RUN_ID` set before spawn | Dispatched workers still resolve `dispatcher_composition` |
| No regression | Full session-envelope and modernization-workflow suites | All pass |

Commands to be executed and reported in the implementation report:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_envelope_cli_provenance.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_end_to_end_workflow.py platform_tests/scripts/test_session_envelope_runtime.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/session_self_initialization.py groundtruth-kb/src/groundtruth_kb/session/envelope.py groundtruth-kb/src/groundtruth_kb/modernization/workflow.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/session_self_initialization.py groundtruth-kb/src/groundtruth_kb/session/envelope.py groundtruth-kb/src/groundtruth_kb/modernization/workflow.py
```

## Acceptance Criteria

1. The `session_resolver_fallback` literal is removed from the producer.
2. An unresolved role writes no envelope rather than a fabricated one.
3. A SessionStart after `::init` does not revert the transcript role, proven
   by a new regression test.
4. All three interactive sources are protected from non-interactive overwrite.
5. Owner re-declaration and dispatcher composition still change the role.
6. Any residual envelope carrying the removed value fails closed.
7. Dispatched workers are unaffected.
8. Existing session-envelope and modernization suites pass.
9. Only the six declared target paths are modified.

## Bridge Chain Discipline

Filed as `bridge/gtkb-wi5723-session-resolver-fallback-removal-001.md`, the
first numbered file of a fresh append-only chain. No prior versioned bridge
file is deleted, rewritten, or renumbered; later versions append with a
canonical status token and an exact `Responds to:` link.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-202667524` Decision 1 (CF-01/CF-02) — unresolved identity must fail closed.
- `DELIB-202667530` — the explicit init direction is canonical and supersedes competing resolution paths.
- `DELIB-20260730-CF10-LEADER-GRANT-B34D5B84` — CF-10 leadership under which the defect was reproduced.
- `bridge/gtkb-wi5834-worker-session-role-downgrade-guard-002.md` — this session's WITHDRAWN filing; establishes that WI-5834 was a duplicate and records the corrected dispatch finding.
- `WI-5749` / `WI-5750` / `WI-5568` / `WI-5747` — the pre-existing carriers for the shared-pointer and role-revert symptoms; this slice fixes the producer they all depend on.
- `WI-5679` — stale ambient session id (adjacent, different mechanism; under CF-01 halt). This proposal does **not** adopt its clause C2 cross-session projection resolution, which WI-5723 flags as in tension with D1.
- `WI-5718` — owns the `DCL-SESSION-ROLE-RESOLUTION-001` v7 packet repair.
- `WI-5835` — ad-hoc envelope provenance hygiene, split out by owner decision.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner directive, 2026-07-31: "The role flip problem needs an urgent fix."
- Owner AskUserQuestion, 2026-07-31: selected **"Narrow slice of WI-5723"** as the carrier and scope over full WI-5723 scope or re-homing WI-5749/WI-5750.
- Owner AskUserQuestion, 2026-07-31: selected **"Investigate dependents first, then propose"**; that investigation is the basis of the dependency analysis above and corrected the withdrawn thread's dispatch claim.
- Owner AskUserQuestion, 2026-07-31: selected **"Accept — fail closed"**, explicitly accepting that a session which never issues `::init` will have no envelope and cannot mint claims until it declares a role.
- Owner AskUserQuestion, 2026-07-31: selected **"Separate hygiene item"** for ad-hoc provenance values, captured as `WI-5835`.
- Implementation authority is inherited from the active list-free whole-project PAUTH cited in the header.

## Risk And Rollback

Principal risk is the accepted ergonomic delta: a session that never declares
a role cannot mint claims. The owner accepted this explicitly; it is the
intended fail-closed posture and is the behavior CF-01 directs.

Secondary risk is over-suppression in C2 refusing a legitimate role change;
mitigated by scoping the guard to non-interactive incoming sources only, with
positive tests asserting owner re-declaration and dispatcher composition still
change the role.

Rollback is reversion of the six target files through a separately governed
transaction. No historical bridge file, MemBase row, project state, or session
document is mutated, so reverting restores prior behavior exactly.

## Recommended Commit Type

`fix` — repairs silent revocation of owner-granted session authority.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
