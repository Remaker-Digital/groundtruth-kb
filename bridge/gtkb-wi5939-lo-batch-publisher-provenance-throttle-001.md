NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 5ce32d92-003b-4a04-a5f9-d3de2493c992
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal
Document: gtkb-wi5939-lo-batch-publisher-provenance-throttle
Version: 001
Date: 2026-08-05 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5939

target_paths: ["scripts/lo_batch_publish.py", "platform_tests/scripts/test_lo_batch_publish.py"]

# WI-5939 - Promote the LO batch verdict publisher to a tracked governed module with truthful runtime provenance, computed review-independence, and publication throttling

## Problem Statement

An untracked script at `.gtkb-state/_lo_publish_from_recs.py` publishes governed
Loyal Opposition verdicts. It correctly routes through the governed substrate -
it calls `publish_lo_verdict` (governed writer), `prepare_verdict_candidate`
(applicability preflight), and `acquire`/`release` (work-intent claims), and it
refuses to publish when the responded-to thread's latest status is not
actionable. That routing is sound and is preserved by this proposal.

The defects are that the verdict bodies it emits carry **templated provenance
rather than truthful runtime provenance**, the publish loop is unthrottled, and
the whole publisher lives on an **untracked runtime-state surface** with no
change control. Six behavioral defects, each observed in the current file:

| # | Defect | Location |
|---|---|---|
| 1 | `SESSION` is a hardcoded module constant, so every verdict claims one fixed author session regardless of which session published it | line 24 |
| 2 | Review independence is emitted as a **template string** asserting "Author session on {responds} differs from reviewer {SESSION}" - printed, never computed or verified | line 92 |
| 3 | `Date:` is hardcoded to `2026-08-02 UTC`, so publication dates are false for any later run | line 79 |
| 4 | `## Prior Deliberations` is hardcoded to a "no prior deliberations" line, templating away the mandatory deliberation search | line 105 |
| 5 | `os.environ["GTKB_HARNESS_NAME"] = "cursor"` is injected at import, so any process publishes as harness E | line 18 |
| 6 | `main()` iterates items in a tight loop with no serialization, backoff, or inter-publication delay | lines 178-186 |

Defect 6 is the mechanism behind the bridge-glob churn diagnosed during the
WI-5933 bridge-publication currentness livelock: continuous appends to the
`bridge/*-NNN.md` aggregate destabilized the publication generation, so
concurrent publishers could not obtain a current generation.

Defect 2 is the most serious. Review independence is the load-bearing guarantee
of the bridge protocol, and the protocol requires it to **fail closed** when
author session metadata is missing or unreadable. Here it is asserted as
boilerplate and never computed.

The seventh, structural defect is the surface itself: a load-bearing publisher of
governed artifacts living untracked in runtime state has no change control, no
review history, and no tracked provenance. This was confirmed mechanically - the
project-authorization gate refuses any governed mutation of
`.gtkb-state/_lo_publish_from_recs.py` with
`target_mutation_class_not_allowed: (runtime_state)`, because runtime state is
deliberately not a controlled implementation surface. Repairing the behavior
without moving the surface would leave the ungoverned property intact.

## Measured Impact

- **120** bridge verdict files carry the canned Prior Deliberations boilerplate.
- All **120** are attributed `author_identity: loyal-opposition/cursor/E`.
- They split across **two** hardcoded session values:
  `0cebac42-fd54-4389-9931-414b43929aca` (71 files) and
  `499b2c79-0288-4568-8ffc-2bfcaa91117d` (49 files).
- Every file in the 60-file `499b2c79` sample also carries the hardcoded
  `Date: 2026-08-02 UTC`.
- Of that 60-file sample: **40 GO**, **20 NO-GO**. GO verdicts authorize
  implementation.

Per owner decision (AUQ 2026-08-05), the underlying review work was genuine, so
the verdicts stand on substance and no re-review is required. Remediation of the
already-published audit trail is tracked separately as **WI-5940**. This proposal
covers only the publisher, so the defects stop recurring.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal must
  cite every relevant governing specification; this section discharges that
  obligation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - VERIFIED requires
  specification-derived tests; the Test Plan below maps each linked
  specification clause to a concrete test.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge files are the canonical append-only
  audit trail; provenance recorded in them must be truthful.
- `.claude/rules/file-bridge-protocol.md` section Review Independence Boundary -
  independence is determined by session context, and missing or unreadable
  author session metadata **fails closed**. Defect 2 violates the fail-closed
  requirement by asserting independence without computing it.
- `config/agent-control/SESSION-STARTUP-INDEX.md` section Session-context review
  independence (normative) - the controlling normative block for that rule.
- `.claude/rules/codex-review-gate.md` section Review Independence Gate -
  same-session review is self-review and must not receive GO or VERIFIED;
  missing author-session metadata fails closed.
- `.claude/rules/deliberation-protocol.md` - mandatory deliberation search before
  reviewing; defect 4 templates that obligation away.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - state claims must derive from fresh
  canonical reads rather than cached or templated substitutes; hardcoded session
  and date constants are templated substitutes for runtime state.
- `.claude/rules/bridge-essential.md` - bridge integrity is the top-priority
  duty; unthrottled publication that destabilizes the publication generation is
  a bridge-integrity defect.
- `.claude/rules/codex-decision-ledger.md` (2026-04-29, tracked-surface bias) -
  load-bearing surfaces belong in tracked, versioned locations because
  AI-driven work pays its dominant cost in drift, not documentation effort.
  This is the specification basis for promoting rather than repairing in place.
- `DELIB-202667721` - owner decision behind the whole-project authorization
  cited in the metadata above.

## Prior Deliberations

- `DELIB-202667526` - "Live concurrency evidence from leader-session disposition
  filings under fleet load": lock convoying on the control-plane lock and the
  platform-wide single-active-publication-capability constraint. Establishes
  that publication is a serialized, contended resource, which is why an
  unthrottled publisher (defect 6) is harmful.
- `bridge/gtkb-wi5933-bridge-publication-currentness-livelock-001.md` / `-002.md`
  - the currentness livelock this publisher's churn exposed, and the
  emergency-bootstrap repair that fixed the reader side. This proposal addresses
  the writer-side half that was left open.
- WI-5869 (registry lock acquisition backoff + jitter + typed timeout) and
  WI-5881 (reservation claim-fence CAS primitive) - follow-on concurrency work
  already landed in this area. The throttling design below composes with those
  mechanisms rather than duplicating them.

## Requirement Sufficiency

Existing requirements sufficient. The review-independence fail-closed rule, the
truthful-provenance obligation, the deliberation-search obligation, and the
tracked-surface bias are all already specified in the artifacts cited above.
This proposal brings an existing publisher into conformance with them; it
introduces no new requirement.

## Proposed Change

All changes are confined to the declared `target_paths`.

### C0 - Promote to a tracked governed module (structural defect)

Create `scripts/lo_batch_publish.py` as the tracked, change-controlled home for
this capability, carrying the corrected behavior in C1-C5. The existing
`.gtkb-state/_lo_publish_from_recs.py` is thereby superseded. Because runtime
state is not a governed mutation surface, this proposal does **not** modify or
delete that file; its removal is an owner action recorded as a follow-on hygiene
step. The governed module preserves the existing input JSON schema so current
recs files keep working.

### C1 - Runtime session provenance (defects 1, 5)

Resolve the publishing session id from the runtime envelope/environment using
the same precedence the governed author-metadata loader uses. Fail closed with a
clear error when it cannot be resolved. Do not inject `GTKB_HARNESS_NAME` at
import; resolve harness identity from the runtime envelope and fail closed on
mismatch. No session-id literal remains in the module.

### C2 - Computed review independence (defect 2)

Replace the templated independence sentence with a computed check: read the
responded-to artifact's `author_session_context_id`, compare it to the resolved
publishing session, and

- refuse to publish when they are equal (self-review), and
- refuse to publish when author session metadata is missing or unreadable
  (fail closed, per the protocol's explicit requirement),

emitting the actual compared values into the verdict body as evidence instead of
a boilerplate assertion.

### C3 - Runtime date (defect 3)

Derive `Date:` from the current UTC date at publication time.

### C4 - Honest deliberation-search disclosure (defect 4)

Stop hardcoding the "no prior deliberations" line. Either carry a per-item
`prior_deliberations` field supplied by the reviewing session, or emit an
explicit disclosure that no deliberation search was performed by this transport.
The verdict must not claim a search result it did not obtain.

### C5 - Serialization and throttling (defect 6)

Publish items one at a time with a bounded inter-publication delay and backoff on
contention, composing with the existing control-plane lock rather than competing
with it. Surface throttling decisions in the run output.

## Test Plan (specification-derived)

New tests in `platform_tests/scripts/test_lo_batch_publish.py`:

| Test | Derived from | Asserts |
|---|---|---|
| T1 | file-bridge-protocol Review Independence Boundary | publishing is refused when the resolved session equals the responded-to artifact's `author_session_context_id` (self-review) |
| T2 | same, fail-closed clause; codex-review-gate Review Independence Gate | publishing is refused when the responded-to artifact has missing/unreadable author session metadata |
| T3 | GOV-SOURCE-OF-TRUTH-FRESHNESS-001; GOV-FILE-BRIDGE-AUTHORITY-001 | emitted `author_session_context_id` equals the runtime session; no hardcoded UUID literal remains in the module |
| T4 | GOV-FILE-BRIDGE-AUTHORITY-001 | emitted `Date:` equals the current UTC date; no hardcoded date literal remains |
| T5 | deliberation-protocol | the body does not assert a deliberation-search result that was not obtained |
| T6 | bridge-essential; DELIB-202667526 | multi-item publication is serialized with bounded delay/backoff, not unthrottled back-to-back publication |
| T7 | codex-decision-ledger tracked-surface bias | the governed module exists at the tracked path and is importable without depending on any `.gtkb-state` path |

Commands to be executed and reported in the implementation report:

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_lo_batch_publish.py -q
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/lo_batch_publish.py platform_tests/scripts/test_lo_batch_publish.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/lo_batch_publish.py platform_tests/scripts/test_lo_batch_publish.py
```

Regression protection for the surrounding publication path:

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_publication_finalization_atomicity.py platform_tests/scripts/test_bridge_work_intent_registry.py -q
```

## Acceptance Criteria

1. `scripts/lo_batch_publish.py` exists as a tracked module and carries the
   capability; no `.gtkb-state` path is required for it to run.
2. No hardcoded session-id or date literal remains in the module.
3. Review independence is computed from the responded-to artifact and fails
   closed on equality or on missing/unreadable author metadata.
4. The verdict body never asserts a deliberation-search result that was not
   obtained.
5. Multi-item publication is serialized with bounded delay/backoff.
6. T1-T7 pass; `ruff check` and `ruff format --check` pass on both target files.
7. The existing publication regression suites continue to pass.

## Risk and Rollback

- **Risk: the publisher becomes stricter and refuses runs that previously
  succeeded.** Intended behavior change - the refusals are exactly the cases
  where provenance could not be established truthfully. Mitigation: error
  messages state which check failed and which runtime value was missing.
- **Risk: throttling slows bulk publication.** Accepted; publication is a
  serialized contended resource per `DELIB-202667526`, and unthrottled
  publication is what destabilized the aggregate generation.
- **Risk: two publishers coexist until the owner removes the superseded copy.**
  Mitigation: the superseded file is untouched and inert unless explicitly
  invoked; the follow-on hygiene step records its removal.
- **Rollback:** both target paths are new files. Rollback is deletion of the two
  new files; no existing tracked file is modified, so there is no in-place
  regression surface.

## Owner Decisions / Input

- **AUQ 2026-08-05 (next lane):** owner selected "P0: close the rogue-publish
  hole", directing this work ahead of the Slice B resolver fix and the harness
  parity program.
- **AUQ 2026-08-05 (verdict provenance):** owner selected "Genuine review;
  metadata is the bug" - the findings content in the recs JSON was real review
  work; the 120 already-published verdicts stand on substance and require no
  re-review. This scoped the present proposal to the publisher only and moved
  the audit-trail correction to WI-5940.
- **AUQ 2026-08-05 (script disposition):** owner initially selected "Fix
  provenance + throttle in place".
- **AUQ 2026-08-05 (target surface, superseding the preceding item):** after the
  project-authorization gate mechanically refused any governed mutation of the
  `runtime_state` path, owner selected "Promote to tracked source". That decision
  is the authority for C0 and for the `target_paths` declared above, and it
  supersedes the earlier in-place selection.
- **`DELIB-202667721`** - owner decision establishing the list-free whole-project
  authorization cited in the metadata, which covers all active member work items
  of PROJECT-GTKB-HOUSEKEEPING-HARDENING (WI-5939 included) while still requiring
  this full governed cycle.

## Recommended Commit Type

`feat:` - this adds a net-new tracked module (`scripts/lo_batch_publish.py`) plus
its test module. Although the behavior originates in an existing untracked
script, the diff introduces a new governed capability surface, which the
Conventional Commits discipline classifies as `feat:` rather than `fix:`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
