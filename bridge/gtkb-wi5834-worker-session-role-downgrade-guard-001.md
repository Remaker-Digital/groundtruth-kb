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
Document: gtkb-wi5834-worker-session-role-downgrade-guard
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5834

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "platform_tests/scripts/test_session_envelope_runtime.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Guard the worker-session document against interactive-role downgrade by fallback writes

## Problem - reproduced live, not theoretical

On 2026-07-31 an interactive Prime Builder session lost its owner-granted role
mid-work. Session `b34d5b84-5746-4eee-bd95-b6eeb3e70715` (harness B) had
declared Prime Builder through the canonical init keyword, and its per-session
document correctly recorded:

```
role_resolved:                              prime-builder
worker_role_provenance.role_resolution_source: transcript_init_keyword
role_resolution.authority_mode:             interactive_transcript
```

That same document was later rewritten in place to:

```
role_resolved:                              loyal-opposition
worker_role_provenance.role_resolution_source: session_resolver_fallback
role_resolution.authority_mode:             worker_session_document
```

The session could no longer mint `go_implementation` work-intent claims -
`bridge_claim_cli.py` refused with *"session 'b34d5b84-...' resolves to worker
session document role 'loyal-opposition' (not prime-eligible)"* - and could
therefore not obtain an implementation-start packet for any GO'd work. Owner
authority granted by transcript was revoked by a background write, with no
error, no prompt, and no audit signal. Recovery required the owner to
re-declare the init keyword.

## Root cause - one unguarded assignment

`groundtruth-kb/src/groundtruth_kb/session/envelope.py`,
`ensure_worker_session()`. When the per-session document already exists and is
open, the function overwrites role and provenance unconditionally from the
**incoming** `role_source`, never consulting the provenance already recorded on
that document:

```python
current["role_asserted"] = role
current["role_resolved"] = role
current["role"] = role
current["role_resolution"] = _role_resolution(..., role=role, role_source=role_source)
current["worker_role_provenance"] = _worker_role_provenance(..., role=role, role_source=role_source)
write_current(project_root, resolved_name, current)
```

The upstream caller supplies that `role_source` in
`scripts/session_self_initialization.py`:

```python
role_source = (
    "dispatcher_composition" if dispatch_run_id
    else ("transcript_init_keyword" if role_profile_explicit else "session_resolver_fallback")
)
```

`role_profile_explicit` is False on any turn that does not itself carry the
init keyword. So **any** re-run of session self-initialization against an
already-open interactive session resolves `role_profile` to the durable
registry role (`loyal-opposition` for harness B) and writes it over the
established interactive role. A second concurrent session is one trigger
(observed: `f91a3228-0ed7-4d21-a2a7-65e40d706ef8` opened 2026-07-31T06:29:16Z
on the same harness) but is not required.

This inverts the documented authority model. `_role_resolution()` in the same
module already declares that the durable registry role is *"headless dispatch
routing and interactive fallback only; non-overriding when a transcript-defined
interactive role is present"* - the data model says non-overriding, and this
write path overrides it.

It also contradicts the controlling owner directive. `DELIB-202667524`
Decision 1 (CF-01/CF-02) requires that unresolved identity **fail closed**
rather than fall back to the durable registry role. This path does the
opposite, and additionally downgrades a role that was already resolved.

## Proposed Change

### G1 - refuse interactive-role downgrade (the blocking fix)

In `ensure_worker_session()`, before the in-place role overwrite: if the
existing open document's `worker_role_provenance.role_resolution_source` is an
**interactive source** and the incoming `role_source` is
`session_resolver_fallback`, preserve the recorded role, provenance, and
`role_resolution` block; do not overwrite. Non-role fields
(`init_keyword` when explicitly supplied, resource selection) continue to
refresh as today.

The interactive-source set reuses the vocabulary already established in
`groundtruth-kb/src/groundtruth_kb/modernization/workflow.py`:

```python
INTERACTIVE_ROLE_SOURCES = frozenset({
    "interactive_transcript_explicit",
    "owner_init_keyword",
    "transcript_init_keyword",
})
```

Introducing no new vocabulary is deliberate - the fix must not fork the
provenance taxonomy.

**Why preserve rather than raise.** Failing the call hard would break session
self-initialization on every ordinary turn of an interactive session, since
that path legitimately re-runs without the init keyword. Preserving the
established role *is* the fail-closed outcome for the authority question:
authority does not silently change. The conflict is surfaced (G2) rather than
swallowed.

### G2 - surface the refused downgrade

When G1 suppresses a downgrade, append a structured entry to the document's
existing diagnostics surface recording: the incoming role and source, the
preserved role and source, and the timestamp. This makes a previously silent
event auditable and gives WI-5679/WI-5580 investigators a signal to correlate
against. No new file, no new state directory.

### Explicitly out of scope

- **The per-harness singleton.** `write_current()` also writes
  `harness-state/<harness>/session-envelope.json` and the
  `.claude/session/envelope.json` projection, both last-writer-wins across
  concurrent sessions on one harness. That shared-pointer collision is a real
  contributing surface and is recorded on WI-5834, but redesigning it is a
  larger change than this urgent fix warrants and belongs with WI-5580's
  cross-harness collision scope. G1 makes the observed authority loss
  impossible regardless of which session last wrote the shared pointer, which
  is the property that matters for the reported incident.
- **Removing `session_resolver_fallback` from
  `TRUSTED_WORKER_ROLE_SOURCES`.** That constant is consumed by dispatcher
  composition paths; distrusting the source wholesale would break headless
  dispatch. This proposal blocks the *downgrade*, not the source.
- **Retroactive repair** of any document already downgraded. The one observed
  instance was corrected by owner re-declaration before this filing.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-SESSION-ROLE-AUTHORITY-001` establishes
the durable-versus-session-stated authority split that this defect violates;
`DCL-SESSION-ROLE-RESOLUTION-001` supplies the deterministic resolution table;
`DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` requires the transcript-defined
role to persist across contiguous session boundaries until the owner changes
it - which is exactly the invariant broken here. No new or revised requirement
is needed; this restores conformance to requirements that already exist.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` - durable vs session-stated authority split; the durable role must not override a transcript-defined interactive role.
- `DCL-SESSION-ROLE-RESOLUTION-001` - deterministic role-resolution table this write path must honor.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - the transcript-defined role persists until the owner explicitly changes it; the observed downgrade violates this directly.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` - decision record for interactive override precedence.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` - persistence decision this guard enforces.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - provenance contract governing `worker_role_provenance`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - claim/implementation-start gating that the downgrade blocked.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - authority derives from the active list-free whole-project PAUTH cited above.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - PAUTH, membership, and operations revalidated immediately before mutation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass GO, claim, start packet, report, or verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH/Project/Work Item declared above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing specification linked to concrete behavior.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification plan below maps each requirement to executed evidence.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - deterministic, fails safe, fully testable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - both target paths are in-root.

## Specification-Derived Verification

| Requirement | Verification | Expected result |
| --- | --- | --- |
| G1 blocks the exact observed downgrade | Open a document with role `prime-builder` / `transcript_init_keyword`; call `ensure_worker_session` with role `loyal-opposition` / `session_resolver_fallback` | Document retains `prime-builder` and `transcript_init_keyword`; `authority_mode` stays `interactive_transcript` |
| G1 covers every interactive source | Repeat for `owner_init_keyword` and `interactive_transcript_explicit` | Downgrade refused in all three cases |
| G1 does not block legitimate owner role change | Existing `transcript_init_keyword` document; incoming role `loyal-opposition` with source `transcript_init_keyword` | Role changes to `loyal-opposition` - owner re-declaration still works |
| G1 does not block dispatcher composition | Existing interactive document; incoming source `dispatcher_composition` | Not suppressed; existing dispatch behavior preserved |
| G1 does not affect fresh sessions | No existing document; incoming `session_resolver_fallback` | Normal open path; fallback role applied as today |
| G1 does not affect closed documents | Existing document with `status != "open"` | Normal re-open path unchanged |
| G2 records the refusal | Trigger a suppressed downgrade | Diagnostics entry present with incoming role/source, preserved role/source, timestamp |
| Provenance taxonomy unforked | Grep for interactive-source set definition | Exactly one definition reused; no second vocabulary introduced |
| No regression | Full existing session-envelope suites | All pass |
| End-to-end claim eligibility | After a suppressed downgrade, resolve worker role provenance and attempt a `go_implementation` claim | Claim remains prime-eligible |

Commands to be executed and reported in the implementation report:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_envelope_cli_provenance.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_envelope_cli_choice.py platform_tests/scripts/test_session_topic_envelope_router.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_session_envelope_runtime.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_session_envelope_runtime.py
```

## Acceptance Criteria

1. A `session_resolver_fallback` write cannot replace an interactive-sourced
   role on an open session document.
2. All three interactive sources are protected.
3. Owner re-declaration via an interactive source still changes the role.
4. `dispatcher_composition` writes are unaffected.
5. Fresh-session and closed-document paths are unaffected.
6. Each suppressed downgrade is recorded in the document's diagnostics.
7. No new provenance vocabulary is introduced.
8. The existing session-envelope test suites pass.
9. Only the two declared target paths are modified.

## Prior Deliberations

- `DELIB-202667524` Decision 1 (CF-01/CF-02) - controlling owner directive that unresolved identity must fail closed rather than fall back to the durable registry role. This proposal implements the non-downgrade half of that intent for already-resolved sessions.
- `DELIB-20260730-CF10-LEADER-GRANT-B34D5B84` - the CF-10 leadership grant under which the session that reproduced this defect was operating.
- `WI-5834` (this work item) - carries the full reproduction record and mechanism analysis.
- `WI-5679` - worker-session document resolves against a stale ambient session id after restart. Adjacent: same subsystem and same end symptom (blocked `go_implementation` claims), different mechanism (wrong document selected, versus correct document overwritten). Not superseded by this proposal.
- `WI-5580` - cross-harness session-envelope collisions. Owns the per-harness singleton / shared-projection collision surface explicitly excluded above.
- `WI-5718` - retired session-role authority purge; related role-authority cleanup.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner directive, 2026-07-31, session `b34d5b84-5746-4eee-bd95-b6eeb3e70715`: *"The role flip problem needs an urgent fix."* That directive selects this work and its priority.
- Owner AskUserQuestion, same session, immediately prior: presented with the role flip and three options, the owner selected **"You restore my Prime Builder role"** and separately **"Stop the loop"**. The restore has been performed by the owner via re-declaration; this proposal addresses the underlying defect rather than the individual recovery.
- Implementation authority is inherited from the active list-free whole-project PAUTH cited in the header, per the owner's standing rule that work items inherit approval from the parent project.
- No new owner decision is requested by this proposal.

## Risk And Rollback

The principal risk is over-suppression: a guard that refuses a *legitimate*
role change would strand a session in a stale role. This is mitigated by
scoping the guard to exactly one incoming source
(`session_resolver_fallback`); every interactive source and
`dispatcher_composition` continue to write normally, and three dedicated
positive tests assert that owner re-declaration and dispatcher composition
still change the role.

Secondary risk is masking: with the downgrade suppressed silently, a genuine
role-resolution problem could go unnoticed. G2 exists precisely to prevent
that - each suppression is recorded.

Rollback is reversion of the two target files through a separately governed
transaction. No historical bridge file, MemBase row, project state, or session
document is mutated by this change, so reverting restores prior behavior
exactly.

## Bridge Chain Discipline

This proposal is filed as `bridge/gtkb-wi5834-worker-session-role-downgrade-guard-001.md`,
the first numbered file of a fresh append-only chain. A fresh slug is used
deliberately: numbered bridge files are immutable, and several existing
role-authority threads are currently unresolvable by the strict lifecycle
resolver, so continuing one of them would strand this urgent fix. No prior
versioned bridge file is deleted, rewritten, or renumbered by this filing, and
every later version of this thread will append as the next numbered file with
a canonical status token and an exact `Responds to:` link to its predecessor.

## Recommended Commit Type

`fix` - repairs silent revocation of owner-granted session authority; adds no
new capability surface.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
