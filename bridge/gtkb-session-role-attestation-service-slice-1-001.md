NEW
::init gtkb lo
::open build

# gtkb-session-role-attestation-service-slice-1 (Slice 1) — Init-bound role attestation service replacing session-document role resolution

bridge_kind: prime_proposal
Document: gtkb-session-role-attestation-service-slice-1
Version: 001
Author: Prime Builder (harness B)
Date: 2026-08-13 UTC

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: c78a4e67-7799-4284-b540-72ede394027f
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via the canonical init keyword

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6213

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/**/*.py", "groundtruth-kb/src/groundtruth_kb/bridge/**/*.py", "scripts/_kb_attribution.py", "scripts/session_self_initialization.py", "platform_tests/**/*.py", "groundtruth.db", ".groundtruth/formal-artifact-approvals/**"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

GT-KB resolves session role authority by reading a persisted per-session
document. `DCL-SESSION-ROLE-RESOLUTION-001` v8 (`specified`, verified in MemBase
this session) forbids exactly that, naming "open/closed session document",
"per-harness projection", "current pointer", "registry role", "vendor identity"
and "archive" as prohibited resolution inputs. The specifications that would
justify the document — `ADR-ENVELOPE-META-MODEL-001` v3 and
`DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` v5 — are `superseded`, and
`GOV-SESSION-ROLE-AUTHORITY-001` v6 is `retired`. All six statuses were confirmed
by direct MemBase reads before this proposal was drafted.

This is therefore conformance repair, not redesign: the runtime is executing
retired and superseded specifications while a live design constraint forbids the
behavior. Slice 1 implements the attestation service DCL v8 specifies and
repoints every role-sensitive consumer at it. It is the first of four ordered
slices; the ordering is load-bearing because the session documents are currently
the only role source, so removing them before the replacement exists would break
verdict filing, proposal filing, claims and handoff simultaneously — leaving no
lawful way to file the verdict reporting the breakage.

The cost of the current state is not theoretical. During Loyal Opposition session
`d8d674a0-fb43-4a1f-80c8-579eb51fecc2` the defect made it impossible for a
correctly-initialized reviewer to file any verdict, and then made it impossible
to record that finding, because MemBase authorship was itself gated on an open
session document.

## Scope

In scope for Slice 1:

1. An append-only role-attestation store. An attestation records the
   session-envelope ID, normalized role, source event, issuer, timestamp and
   evidence digest, and carries no session lifecycle, activity, claim,
   implementation, wrap or handoff state (DCL v8 § Initial role, clauses 2-3).
2. Creation of the initial attestation in the same atomic transaction as the
   immutable session-init binding, driven by the mandatory role token in an exact
   `::init <subject> <role>` (DCL v8 § Initial role, clause 1). The four valid
   exact-init forms create a matching attestation; every invalid init creates
   none.
3. One canonical resolver taking a session-envelope ID (obtained through
   `DCL-INIT-BOUND-SESSION-IDENTITY-001`) and an operation time, returning one
   effective role plus attestation evidence, or a typed failure. No fallback
   authority of any kind participates.
4. Repointing the role-sensitive consumers: verdict filing, proposal filing,
   work-intent claims, implementation start, and MemBase authorship attribution.
   Each persists the evidence reference it used (DCL v8 § Operation-time
   behavior).
5. Append-only owner-directed role change: a new attestation against the same ID
   that never re-runs init, mutates the binding, or rewrites a prior attestation,
   and that cannot make one session context an independent reviewer of its own
   earlier work.

6. One MemBase mutation: insertion of the new attestation ADR under `GOV-20`,
   recording the decision, its context, the rejected alternatives and its
   consequences. `groundtruth.db` is therefore declared in `target_paths` and
   `kb_mutation_in_scope` is `true`. The ADR carries its own per-artifact approval
   packet under `GOV-ARTIFACT-APPROVAL-001`; the project authorization does not
   substitute for it. No other MemBase record is created, versioned or retired by
   this slice — in particular the retirement of the two superseded specs is Slice
   3 work, not Slice 1 work.

Explicitly out of scope for Slice 1, deferred to the ordered follow-on slices:
close-side harvest and removal of `archive_session_envelope` (Slice 2); purge of
object references from code and canonical narrative plus formal retirement of the
two superseded specs (Slice 3); deletion of the on-disk object trees (Slice 4).
Also out of scope: F8 / WI-6212, which is independent of the object model and
carried separately.

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` v8 (`specified`) — the live constraint this
  proposal implements verbatim. Supplies the attestation contract, the forbidden
  resolution inputs, the operation-time behavior, and the six required executable
  acceptance criteria this proposal's verification plan maps onto.
- `DCL-INIT-BOUND-SESSION-IDENTITY-001` v1 (`specified`) — supplies the one exact
  session-envelope ID the resolver keys on; Slice 1 consumes it and must not
  introduce a second identity source.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v4 (`specified`) — defines the exact
  init forms that trigger attestation creation, and establishes the init keyword
  as the only session opener.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v4 (`specified`) — bridge authority and
  audit-trail durability that the current defect defeats; verdict and proposal
  filing are two of the consumers being repointed.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 — governs this
  proposal's own obligation to cite every relevant governing specification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 — governs the
  project/work-item/authorization linkage recorded in the header block above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 — requires the
  spec-to-test mapping below and forbids `VERIFIED` on any linked specification
  lacking executed test coverage.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5 (`specified`) — state claims derive from
  fresh canonical reads rather than mutable filesystem residue; the current
  document-based resolution is precisely such residue, pruned by other processes.
- `GOV-20` v2 — Architecture Decision Governance. The owner directed that the
  attestation model be recorded as a new ADR; that ADR is authored under this
  governance and carries its own approval packet.
- `GOV-ARTIFACT-APPROVAL-001` v4 — the new attestation ADR and the eventual
  retirement of the two superseded specs each require their own per-artifact
  approval packet. Class authorization does not substitute.
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` v1 — this proposal derives from an
  `adapt`-classified advisory, so the gate answers recorded below are a
  precondition of filing.
- `GOV-STANDING-BACKLOG-001` v5 — WI-6213 is the governing backlog item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the attestation evidence reference each
  consumer persists is what keeps authorship and role provenance durable rather
  than transient; F10's fabricated `author_identity` fallback is a direct
  violation this slice removes.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability across artifacts, tests,
  reports and decisions must survive the resolver change; the attestation evidence
  reference is the traceability carrier.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — this slice relies on the `specified` /
  `superseded` / `retired` lifecycle states of the six governing specs, and Slice 3
  performs the retirement transitions those states imply.

## Prior Deliberations

- `DELIB-20265225` (2026-06-18) — the transcript defines the session envelope and
  the declared role must survive compaction; states that the dependent resolution
  behavior "is a defect to correct, not a designed choice to supersede." This is
  the most load-bearing citation: it is why Slice 1 is conformance repair rather
  than a change of direction, and it predates the advisory by fourteen months.
- `DELIB-20265897` (2026-06-25) — ratified the `::wrap` / `::close` mechanical
  harvest model. Slice 1 must not regress it; specifically, authorship must
  remain available during and after harvest, which is the F3 defect.
- `DELIB-20260806011917` — purge-before-probative-language directive. Governs the
  removal method in Slice 3 and constrains Slice 1 not to add counter-instruction
  text in place of removal.
- `DELIB-20260813-GRILLING-GATE-ANSWERS-SESSION-OBJECT-AND-PROJECTION` — the
  owner-grilling-gate answers authorizing this proposal's scope; enumerated under
  Owner Decisions / Input below.
- `DELIB-20260813-OWNER-AUTH-VERDICT-PATH-EMERGENCY-REPAIR` — owner authorization
  for the interim `verdict_filing.py` harness-name repair that Slice 1 supersedes.
- `DELIB-20260813-VERIFIED-COMMIT-GATE-RETIREMENT` — a sibling owner decision from
  the same session. Distinct concern (the commit-first gate), but it touches the
  same verdict-filing path, so the two must not be implemented in conflict.

Differs from all prior deliberations in that none of them implemented the
attestation service; they established the direction, the defect classification
and the harvest model. No prior deliberation proposed and no prior verdict
rejected an attestation-based resolver, so this proposal revisits no rejected
approach.

## Owner Decisions / Input

This proposal derives from an `adapt`-classified Loyal Opposition advisory and
therefore depends on owner approval. Gate answers were collected via
`AskUserQuestion` in the filing session and archived at
`DELIB-20260813-GRILLING-GATE-ANSWERS-SESSION-OBJECT-AND-PROJECTION`. The answers
governing Slice 1:

1. **Slice 1 scope** — "Build DCL v8 as specified, one cycle." The owner rejected
   an interim adapter on the reasoning that, with no attestation store yet, an
   adapter must still read the session document; it centralises the forbidden
   input rather than removing it and becomes throwaway code Slice 3 must purge.
   This proposal implements the full service accordingly.
2. **Spec disposition** — "Retire both + new attestation ADR." Both superseded
   specs are retired as part of this work, and the attestation model is recorded
   as a new ADR under `GOV-20`. The retirements land in Slice 3 so the record
   changes when the runtime does; the ADR is authored alongside Slice 1 because it
   records this decision.
3. **Deletion timing** — "Confirm: slice 4 waits for 1-3." Non-canonical objects
   remain on disk through Slice 1; this proposal deletes none.
4. **Interim repair** — "Keep tracked until Slice 1 supersedes." The
   `verdict_filing.py` harness-name stopgap stays in place and is removed by this
   slice when attestation replaces harness-name resolution. Correction of record:
   the advisory states that file is untracked; it is tracked, committed in
   `c8c9cd68c`.
5. **Purge breadth** — "Delete outright." Recorded here because it constrains
   Slice 3; no deletions occur in Slice 1.

Owner authorization for the bounded project scope is
`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
(list-free whole-project, active, owner decision `DELIB-202667732`), which covers
all active member work items including WI-6213 without a work-item allowlist.

## Requirement Sufficiency

**Existing requirements sufficient.** `DCL-SESSION-ROLE-RESOLUTION-001` v8
specifies the attestation contract, the resolution semantics, the forbidden
inputs, the operation-time behavior and six executable acceptance criteria at a
level sufficient to implement and test without further requirement capture.
`DCL-INIT-BOUND-SESSION-IDENTITY-001` v1 supplies the identity binding, and
`SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v4 supplies the triggering syntax. No new
or revised requirement is needed before implementation.

The one artifact this slice adds to the record — the attestation ADR under
`GOV-20` — documents a decision the owner has already made; it is a decision
record, not a new requirement, and it carries its own approval packet under
`GOV-ARTIFACT-APPROVAL-001`.

## Spec-Derived Verification Plan

Each DCL v8 acceptance clause maps to at least one executable test. Tests are new
unless marked. Interpreter is the repo venv for reproducible evidence:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/ -q --no-header
```

| Linked spec / clause | Test | Expected result |
|---|---|---|
| DCL v8 acceptance 1 — valid init creates attestation, invalid creates none | `test_role_attestation_init_binding.py::test_four_valid_exact_init_forms_create_attestation` and `::test_invalid_init_creates_no_attestation` | Each of the four valid exact-init forms yields exactly one attestation with matching normalized role; every malformed init yields zero. |
| DCL v8 acceptance 1 — atomicity with the identity binding | `test_role_attestation_init_binding.py::test_attestation_and_binding_are_one_transaction` | Induced failure during attestation write leaves no session-init binding; the pair is all-or-nothing. |
| DCL v8 acceptance 2 — no forbidden fallback participates | `test_role_attestation_resolver.py::test_no_fallback_source_participates` | With a valid attestation absent and a session document, registry role, active-role marker, environment role, current pointer and archive all present and mutually contradictory, the resolver raises a typed failure rather than returning any of them. |
| DCL v8 § Forbidden resolution inputs | `test_role_attestation_resolver.py::test_resolution_reads_no_session_document` | Resolution performs zero reads under any `session-envelopes` path (asserted by filesystem-access instrumentation, not by inspection). |
| DCL v8 acceptance 3 — concurrent contexts isolated | `test_role_attestation_resolver.py::test_concurrent_pb_and_lo_contexts_isolated` | Two attestations under distinct IDs resolve to their own roles under interleaved access; neither observes the other. |
| DCL v8 acceptance 4 — missing / duplicate / conflicting / tampered fail visibly | `test_role_attestation_resolver.py::test_defective_fixtures_fail_visibly` (parametrized over the four fixture classes) | Each raises a distinct typed error with a cooperative-governance diagnostic; no implicit repair and no substitute attestation is created. |
| DCL v8 acceptance 5 — owner-directed role change appends | `test_role_attestation_role_change.py::test_role_change_appends_without_mutating_identity` and `::test_role_change_does_not_permit_same_context_review` | A second attestation is appended against the same ID; the binding is unchanged; a terminal GO/NO-GO/VERIFIED attempt from the same context after a role change is refused. |
| DCL v8 § Operation-time behavior — consumers persist evidence refs | `test_role_attestation_consumers.py` (parametrized over verdict filing, proposal filing, claims, implementation start, authorship) | Each consumer resolves via the service and persists the attestation evidence reference it used. |
| F3 regression — authorship survives wrap | `test_role_attestation_consumers.py::test_authorship_available_after_wrap` | A MemBase write succeeds after `::wrap`; the current failure mode ("Worker role provenance requires an open session envelope") does not occur. |
| DCL v8 acceptance 6 — adapt/retire dependent tests | Existing suites for cross-session isolation, exact-session attribution, running-harness authorship and fail-visible mismatch | Adapted and passing; tests requiring worker-session documents or marker precedence are retired with the retirement recorded in the implementation report. |
| `DCL-INIT-BOUND-SESSION-IDENTITY-001` | `test_role_attestation_init_binding.py::test_resolver_consumes_identity_binding_id` | The resolver keys on the ID supplied by the identity binding; no second identity source is introduced. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | End-to-end: file a verdict and a proposal through the governed path under attestation | Both succeed from a non-goose harness without `GTKB_HARNESS_NAME`, which is the failure the advisory reproduced. |
| Regression floor | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/ -q --no-header` plus `ruff check` and `ruff format --check` on changed files | No new failures against the pre-change baseline, which the implementation report records explicitly. Both ruff gates run separately per the file-bridge protocol. |

Baseline note: the repository currently carries a known stale-test failure
population (WI-6222, ~76 failures across three clusters with one root cause). The
implementation report will record the pre-change and post-change counts so that
pre-existing failures are not attributed to this slice and, equally, are not used
to mask a regression introduced by it.

## Risk / Rollback

**Primary risk — Slice 1 touches the only working role source.** Every
role-sensitive operation depends on resolution, so a defect here blocks verdict
filing, proposal filing, claims and implementation start at once. This is the
exact failure mode the slice ordering exists to prevent, and Slice 1 is the slice
where it is possible. Mitigation: the session documents are not deleted in this
slice (Slice 4 does that, per the owner's confirmed ordering), so the prior path
remains physically present and restorable for the duration.

**Secondary risk — silent degradation rather than visible failure.** The advisory
notes that deleting `harness-state` previously produced a parity FAIL reporting
total role-coverage collapse while MemBase held every role intact, and that
clearing the envelope directory left the platform apparently operating normally.
Absence in this subsystem has historically been swallowed or mis-reported.
Mitigation: DCL v8 requires typed failure rather than fallback, and the
verification plan asserts fail-visible behavior over four defective fixture
classes rather than only the happy path.

**Tertiary risk — conflict with the sibling verdict-filing change.**
`DELIB-20260813-VERIFIED-COMMIT-GATE-RETIREMENT` also modifies the verdict-filing
path. Mitigation: sequencing is explicit — whichever lands first, the second
rebases onto it, and the implementation report names the ordering actually used.

**Rollback.** Single-commit revert. Slice 1 is additive plus consumer repointing:
the attestation store and resolver are new modules, and the consumer changes are
call-site substitutions. Reverting the commit restores document-based resolution
because the documents and the reader are still present until Slice 4. No data
migration is performed, so there is no partially-migrated state to reconcile.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-session-role-attestation-service-slice-1`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat` — the slice adds a new attestation store, a new canonical resolver and new
test suites, and repoints five consumer call sites. It is net-new capability, not
maintenance; `chore` or `refactor` would misrepresent the diff to
commit-history-driven tooling per the Conventional Commits discipline in the
file-bridge protocol.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
