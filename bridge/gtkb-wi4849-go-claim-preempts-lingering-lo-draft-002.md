GO

# Loyal Opposition Verdict — GO — WI-4849 GO Claim Preempts Lingering LO Draft

bridge_kind: lo_verdict
Document: gtkb-wi4849-go-claim-preempts-lingering-lo-draft
Version: 002
Author: Loyal Opposition (claude, harness B)
Date: 2026-07-05 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4849-go-claim-preempts-lingering-lo-draft-001.md (NEW; prime_proposal; prime-builder/codex; harness A; author session 019f3170-d706-77d3-b3e1-be39d47f3eda)

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-05T21-44-51Z-loyal-opposition-B-0347e1
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition

## Verdict Summary

GO. The proposal repairs a real, code-confirmed post-GO handoff defect with a
correctly-scoped, minimally-invasive design. The change is confined to the
work-intent claim-acquisition predicate; it preserves `go_implementation`
exclusivity, preserves role-eligibility fail-closed behavior, preserves the
implementation-start packet coupling, and is coherent with the existing WI-4534
role guard and WI-4996 begin-time overlap guard rather than fighting either.
Both mechanical preflights pass on the operative `-001` file. Review
independence holds (author harness A / prime-builder; this reviewer harness B /
loyal-opposition, unrelated dispatch session). The three named regression test
files exist and are the correct homes. Owner authorization for the Batch A2
continuation is real and on-disk. Four non-blocking implementer refinements are
recorded below; none rises to a NO-GO.

## Review Independence

This verdict is issued from a dispatcher-spawned Loyal Opposition session
(harness B / claude; dispatch run `2026-07-05T21-44-51Z-loyal-opposition-B-0347e1`).
The proposal author session context (`019f3170-d706-77d3-b3e1-be39d47f3eda`;
prime-builder/codex; harness A) is unrelated to this reviewer session context,
so the same-session self-review bar (config/agent-control/SESSION-STARTUP-INDEX.md
§ Session-context review independence) does not apply. Author session metadata is
present and readable. Role confirmed from `harness-state/harness-registry.json`:
harness A role-set `{prime-builder}`, harness B role-set `{loyal-opposition}`.

## Premise Verification (live source, this session)

The proposal's premise was independently confirmed against live source, not
accepted on assertion:

- **Defect is real.** `scripts/bridge_work_intent_registry.py` `acquire()`
  line 554: `if not _is_expired(existing, now=now) and existing["session_id"] != session_id: return False`.
  This blanket-rejects ANY unexpired different-session holder regardless of
  `claim_kind`. A lingering LO `draft` claim (default TTL `DEFAULT_DRAFT_TTL_SECONDS`
  = 600s, line 22) therefore blocks a Prime `go_implementation` acquire on the
  same slug after `GO`, exactly as described.
- **Claim-kind is computed from live bridge status.** `_claim_values()`
  (line 395) sets `claim_kind = CLAIM_KIND_GO_IMPLEMENTATION` only when
  `_latest_status(...) == "GO"` (line 407), else `CLAIM_KIND_DRAFT`. The design's
  "compute incoming kind from live bridge status" is consistent with the existing
  helper.
- **`go_implementation` exclusivity is lock-serialized.** `acquire()` runs under
  `BEGIN IMMEDIATE` (line 549), so two Primes racing to preempt the same lingering
  draft are serialized: the first replaces the draft with its `go_implementation`
  claim; the second then sees an existing NON-draft (`go_implementation`) holder,
  fails the "existing is non-GO draft" predicate, and is denied. The critical
  safety invariant is preserved by the existing lock; the design does not weaken it.
- **Coherence with the WI-4534 role guard (line 558-569).** Because any claim on
  a GO-latest thread is forced to `go_implementation` kind, and an LO is not
  Prime-eligible, an LO can never legitimately acquire a fresh claim once status
  is `GO`. The only LO claim that can linger in the GO window is one acquired
  during NEW/REVISED review that has not released/expired — precisely WI-4849's
  target. This proves there is no legitimate LO claim to protect in the GO window,
  so preempting a lingering draft is safe.
- **No data loss.** A `draft` work-intent claim is a pure concurrency reservation
  (row in `work_intent_claims`: slug, session_id, ttl). `INSERT OR REPLACE`
  replacing it discards only a stale reservation. Rollback is a single source/test
  revert; the proposal mutates no schema or durable bridge history.

## Design Assessment

The preemption predicate as stated (latest `GO` + incoming `go_implementation` +
Prime-eligible + existing holder is a non-GO draft/review claim) is correctly
scoped, and the enumerated negative controls (Proposed Implementation item 2 +
Acceptance Criteria) are the right ones:

- Active peer `go_implementation` holder is NOT preemptable — preserved.
- Non-Prime caller cannot acquire via the preemption path — preserved
  (the line-564 role guard must still fire in the preemption branch).
- Latest status not `GO` (e.g., a `REVISED` thread back in LO's court) does not
  enable preemption — preserved, and correct: a claim on a REVISED thread is
  legitimate LO work.
- draft-vs-draft is unaffected (only an incoming `go_implementation` may preempt).
- A lapsed peer `go_implementation` (past deadline+grace) is ALREADY replaceable
  via existing expiry semantics (`ttl_expires_at` = grace-expiry, line 419), so
  the new path correctly scopes to non-GO drafts and leaves the lapsed case to
  the existing logic.

`acquire()` is the single choke point; no other function in the module makes a
claim-grant decision (`extend`/`release` require same session; `current_holder`
/`claim_status`/`same_role_project_holder` are read-only), so the change surface
is correct and complete.

## Sibling-Overlap / Swarm Check

A large swarm is active (many untracked/modified files), so I checked for
conflicting or duplicating in-flight work on the target surface:

- **Both target source files are clean in the working tree** (`git diff` and
  `git diff --cached` on `scripts/bridge_work_intent_registry.py` and
  `scripts/implementation_authorization.py` are empty). No sibling has an
  uncommitted edit to `acquire()`; the premise holds against live HEAD with no
  edit conflict.
- **WI-4996 (`gtkb-wi4996-target-path-dispatch-serialization`, VERIFIED at -006)**
  touches `scripts/implementation_authorization.py` but a DIFFERENT concern
  (cross-slug `target_paths` overlap serialization: `target_patterns_overlap`,
  `cross_claim_path_collision_reason`, begin-time collision block). WI-4849 is
  same-slug claim-kind preemption in `bridge_work_intent_registry.py acquire()`.
  Different functions, different concerns — and they COMPOSE as layered guards:
  WI-4849 gets Prime the claim; WI-4996's begin-time guard still prevents `begin`
  when paths collide cross-slug. No conflict. (See advisory A1.)
- Git history for `bridge_work_intent_registry.py` shows the relevant lineage
  (WI-4534 role guard `4912cc97`, timebox `d036c338`, WI-4868 role isolation
  `67cf0cc1`, WI-4658 failsoft-parse, WI-4957 NO-ACTION `34b87b4e`) but NO commit
  already implementing preemption. The defect is live and unclaimed.

## Specification Linkage & Test Derivation

The `Specification Links` section cites the governing surfaces
(`GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
`PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`,
`DCL-CROSS-HARNESS-ENFORCEMENT-001`, `DCL-SPEC-RELEVANCE-CLOSURE-001`,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, and the artifact-oriented
governance set). The `Spec-Derived Verification Plan` table maps each governing
surface to a specific test file and behavior, and the "Minimum verification
commands after GO" block gives exact pytest + `ruff check` + `ruff format --check`
invocations. The three referenced test files all exist and are the correct homes:

- `platform_tests/scripts/test_bridge_claim_cli.py` (present)
- `platform_tests/scripts/test_implementation_authorization.py` (present)
- `platform_tests/scripts/test_work_intent_role_eligibility.py` (present)

Test derivation is adequate for GO. The implementation report must show the exact
command output for those three tests plus BOTH ruff gates (check AND
format --check are separate gates) per the linked
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

## Owner Authorization Evidence

The `Owner Decisions / Input` section is substantive (not placeholder). The cited
approval packet exists on disk at
`.groundtruth/formal-artifact-approvals/2026-07-05-DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE.json`
and records a genuine owner decision: the owner approved continuing the
high-priority queue "until all 43 are resolved," beginning with Batch A2, while
EXPLICITLY preserving every gate ("does not bypass ... bridge GO, work-intent
claims, implementation-start target-path checks, spec-derived verification,
post-implementation reporting, or Loyal Opposition verification"). WI-4849
follows exactly that governed path. PAUTH currency/coverage for
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4849-BATCH-A2-20260705` is validated
mechanically and fail-closed at Prime's `implementation_authorization.py begin`,
which is the correct enforcement point — a GO does not itself authorize mutation.

## Applicability Preflight

- packet_hash: `sha256:2df3f4d5da70aef48bdb5ff78f2d73605ae8bc768a91024521354b077e8b6d60`
- bridge_document_name: `gtkb-wi4849-go-claim-preempts-lingering-lo-draft`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-wi4849-go-claim-preempts-lingering-lo-draft-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation); exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

Both preflights were run this session with
`groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4849-go-claim-preempts-lingering-lo-draft`
and `... scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4849-go-claim-preempts-lingering-lo-draft`
(exit 0). No missing required specs; no blocking clause gaps.

## Prior Deliberations

- No archived deliberation matches the claim-preemption topic — searched
  `search_deliberations()` this session for "work-intent claim preemption
  go_implementation lingering LO draft", "WI-4849 post-GO handoff claim block
  prime implementation-start", and "per-slug work intent claim exclusivity
  concurrency control bridge"; all returned no matches. This is a novel repair,
  not a revisit of a previously rejected approach.
- The proposal's cited intake records (`INTAKE-5a61f299` claim-gated
  implementation-start, `INTAKE-e7d44d40` GO-implementation timebox,
  `INTAKE-3bf4889e` LO-controlled dispatch hold) frame the surrounding claim
  semantics; the design preserves all three.
- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` (owner authorization; approval
  packet on disk) authorizes the Batch A2 continuation under which this proposal
  is filed.

## Prime Builder Implementation Context

The proposal's `Proposed Implementation` (items 1-4) and `Spec-Derived
Verification Plan` are sufficient to implement against. Objective: make
`acquire()` claim-kind-aware for the lingering-draft case only. Evidence paths:
`scripts/bridge_work_intent_registry.py` `acquire()` (line 529+) and
`_claim_values`/`_resolve_go_implementation_eligibility`. Verification: the three
named tests + both ruff gates (commands in the proposal). Rollback: single revert
of the source/test diff. The advisory notes below are refinements to fold into
implementation; they are NOT blockers.

## Advisory Notes for Prime Builder (non-blocking)

- **A1 — Preserve WI-4996's begin-time guard.** `scripts/implementation_authorization.py`
  now carries WI-4996's begin-time `cross_claim_path_collision_reason` /
  `create_authorization_packet(session_id=...)` collision block (VERIFIED,
  committed to HEAD). WI-4849 item 3 is conservative ("keep begin coupled to the
  current session's claim; diagnostic-only"), which is correct — do NOT regress
  or remove WI-4996's collision block when touching `implementation_authorization.py`.
  The two are complementary layered guards. If item 3 requires no substantive
  change, leaving `implementation_authorization.py` untouched (only listed in
  target_paths) is acceptable.
- **A2 — Pin return-vs-raise for the non-Prime preemption attempt.** When a
  non-Prime session attempts to preempt a lingering draft on a GO-latest thread,
  the incoming kind is `go_implementation` but the caller fails role-eligibility.
  Today a plain different-session holder yields `return False` (line 554) while a
  no-holder non-Prime `go_implementation` acquire RAISES `WorkIntentRegistryError`
  (line 566). Decide deliberately which the preemption branch does and add a test
  that pins it, so the negative-control behavior does not silently drift.
  Acceptance criterion 3 is satisfied either way ("cannot acquire"), but the
  choice should be explicit and tested.
- **A3 — Compute claim values once.** The preemption check needs the incoming
  `claim_kind` (via `_latest_status`/`_claim_values`, a filesystem status read
  under the `BEGIN IMMEDIATE` lock). Compute `values` once and reuse for the
  `INSERT OR REPLACE` rather than reading latest-status twice inside the lock.
  Minor efficiency, not correctness.
- **A4 — Add the role-guard coherence test.** Add an explicit negative test that
  an LO (loyal-opposition) session cannot acquire ANY claim on a GO-latest thread
  (existing WI-4534 behavior) AND cannot preempt via the new path. This pins the
  interaction that makes the whole design safe and guards against a future change
  that loosens the role gate in the preemption branch.

## Verdict

GO. Implement per the proposal within the WI-4849 source/test envelope, fold in
advisory notes A1-A4, then file the post-implementation report with the three
named tests' output and BOTH ruff gates. Recommended commit type: `fix:`
(concurs with the proposal — repairs a concrete post-GO handoff defect with no
new user-facing feature surface).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
