NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code proposal-author worker dispatched under the DELIB-202667735 parallel-operation mandate; this filing is a Prime Builder proposal-authoring act (envelope pb); authoring-only scope - no implementation, commit, or review in this session

bridge_kind: prime_proposal
Document: gtkb-wi5829-claim-lifecycle-report-filing
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5829

target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/scripts/test_claim_lifecycle_report_filing.py"]
implementation_scope: claim_lifecycle_release_or_downgrade_at_report_filing
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5829 Implementation Proposal — End the go_implementation Claim's Blocking Power When the Implementation Report Publishes

## Summary

A Prime Builder `go_implementation` work-intent claim outlives the implementation-report filing it exists to protect and then blocks Loyal Opposition verdict publication for tens of minutes. The claim's protected window is definitionally the thread's `GO`-latest state; the moment the PB's implementation report publishes as the next numbered entry (`NEW`), that window is over — but the claim row stays live until its deadline+grace expiry (30+10 minutes, up to 2h10m with extensions), and every LO publication route requires acquiring or holding the thread claim. During the 2026-07-30 Harness Test evaluation runs this produced ad-hoc `*_when_clear.py` poller scripts in `.gtkb-state/lo-verdicts/` and two manual owner "Release your claim" interventions. This proposal binds the claim lifecycle to published thread state: (A-1) the governed bridge writer releases or downgrades a `go_implementation` claim on successful implementation-report publication regardless of holder-session equality, and (A-2) the claim registry's acquire path treats a foreign `go_implementation` claim as non-blocking once the thread's latest status is no longer `GO`. Both candidate mechanisms named in WI-5829 are presented below with a concrete recommendation grounded in the code reading; a live `GO`-window claim continues to block foreign acquisition exactly as today.

This proposal is filed as the next numbered bridge file `bridge/gtkb-wi5829-claim-lifecycle-report-filing-001.md`, continuing the append-only versioned bridge file chain. No prior versions are deleted or rewritten; the numbered bridge files form the canonical append-only audit trail per GOV-FILE-BRIDGE-AUTHORITY-001, and dispatcher/TAFE bridge state plus these status-bearing numbered files remain the canonical workflow state.

## Problem Statement And Live Evidence (fresh reads, 2026-07-31)

All claims below were re-derived this session from the live worktree, the code of record, `gt backlog show WI-5829 --json`, `gt projects authorizations PROJECT-GTKB-HARNESS-TEST-CORRECTIONS --json`, and direct reads of the on-disk evidence artifacts. Line numbers are current-worktree references.

1. **A foreign go_implementation claim blocks all acquisition.** `_claim_operation()` (`scripts/bridge_work_intent_registry.py` lines 953-966) returns `None` (blocked) for a different-session acquire against any unexpired, unlapsed claim unless `_can_preempt_lingering_draft()` applies — and that preemption runs only one way (an incoming `go_implementation` claim may replace a non-`go_implementation` claim, lines 923-928). A live foreign `go_implementation` claim therefore blocks every other session's `acquire`, including an LO session trying to take the draft claim it needs to publish a verdict.
2. **The claim outlives its purpose by construction.** The GO branch of `_claim_values()` (lines 862-884) sets `ttl_expires_at` to deadline+grace (`GO_IMPLEMENTATION_DEADLINE_SECONDS` 30 min + `GO_IMPLEMENTATION_GRACE_SECONDS` 10 min, extensible to `GO_IMPLEMENTATION_MAX_HOLD_SECONDS` 2 h; module constants at lines 26-29). After the implementation report publishes, the thread's latest status is `NEW`, so the registry itself already declares the timer meaningless — `extend()` refuses with "implementation timer no longer applies" (lines 1213-1216) and `maybe_auto_extend()` no-ops (line 1316) — yet the row remains a live blocker until wall-clock expiry: `_is_lapsed_go_implementation()` (lines 361-365) checks only grace expiry, and `claim_status()` reports `lapsed_go_implementation` only when the latest status is still `GO` (line 715). A post-report `go_implementation` claim is neither expired, nor lapsed, nor reported as stale — it is simply dead weight that blocks.
3. **The at-filing release is exact-holder-only and fails silent on identity drift.** `write_bridge_file()` (`scripts/gtkb_bridge_writer.py`) releases the thread claim after successful publication (lines 1310-1316 typed path; 1332-1344 non-typed path) via `_release_claim(project_root, document_name, publication.session_id)`, where `publication.session_id` derives from the filed content's author metadata (`_publication_author_session`). The registry `release()` primitive (`scripts/bridge_work_intent_registry.py` lines 1330-1348) deliberately deletes only an exact session match and treats a foreign holder as "authoritative and must never be deleted by this caller" — a silent no-op. When the `go_implementation` claim holder's session id differs from the report's author session id (the shared-envelope / ambient-identity drift class WI-5815 documents: sibling runs carrying identical or leader-adopted session ids), the release silently does nothing and the claim persists.
4. **Every LO publication route is gated on the claim.** The provider verdict path `publish_lo_verdict()` (`scripts/gtkb_bridge_writer.py` lines 1383-1387) hard-requires the publishing LO session to hold the active claim: "provider verdict requires an active claim" / "held by another session". The helper filing path `_acquire_bridge_work_intent()` (`.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py` lines 178-202) raises "Bridge work-intent for thread ... is held by session ... until ..." for a foreign holder. A persisted PB claim therefore blocks LO verdict publication on all governed routes until expiry or manual intervention.
5. **The workarounds are on disk.** `.gtkb-state/lo-verdicts/` contains the ad-hoc waiter pollers verified this session: `file_dsv4pro_r1_go_when_clear.py` (module docstring "Wait for PB go_implementation claim to lapse, then GO dsv4pro-r1-005"; `wait_for_claim_window()` polls `bridge_claim_cli.py status` under a 45-minute deadline), `file_dsv4pro_r1_go008_when_clear.py`, `file_dsv4pro_r2b_go_when_clear.py`, `file_dsv4pro_r2b_nogo006_when_clear.py`, and `file_dsv4pro_r3_nogo004_when_clear.py` (r3's claim-window blocking). The WI-5829 defect record additionally documents two manual owner "Release your claim" interventions (r1, r2b) during the same runs (owner messages ~23:07:50Z in the program evidence). An LO harness writing bespoke pollers to wait out a finished PB's claim — and an owner hand-unblocking reviews — is precisely the manual plumbing GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001 says belongs in a deterministic service.
6. **The registry already encodes the correct semantic — everywhere except the blocking decision.** `lapsed_go_implementation_claims()` (lines 1351-1373) skips threads whose latest status is not `GO`; `extend()` refuses them; `claim_status()` annotates against latest status. The one place that ignores published thread state is `_claim_operation()`, the acquire-blocking decision. This proposal closes that asymmetry.

## Proposed Design

WI-5829 names two fix candidates. Both are presented; the recommendation and its rationale follow. All lifecycle writes introduced here go through the registry's existing `_run_write_transaction()` bounded-retry path (the WI-5784 plumbing) — no second write discipline is added.

### Mechanism A (recommended) — bind claim lifecycle to published thread state

**A-1: Writer release/downgrade hook at report publication.** In `write_bridge_file()`, after a successful publication (post-`consume_bridge_publication_capability` in the typed path; the `elif release_claim:` branch in the non-typed path), when the just-published status is a Prime-side entry that supersedes the GO window (`NEW` or `REVISED`) and the thread's current holder is a `go_implementation` claim, end that claim's blocking power **regardless of holder-session equality**. The existing exact-holder release still runs first and fully covers the same-session case; the new hook covers the identity-drift case that today no-ops silently. Default disposition: **downgrade** the row to a new non-blocking `CLAIM_KIND_REPORT_OBSERVER` kind rather than delete it — the row keeps the original `session_id` and `acquired_at` (implementation provenance) and records `downgraded_at` plus `downgrade_reason` (two additive columns via the registry's existing `_ensure_schema` additive-column migration). Nothing under `bridge/` is written by the hook; a failed downgrade is fail-soft for the filing (the report publication stands; the acquire-time backstop A-2 still unblocks LO).

**A-2: Acquire-time staleness backstop in the registry.** `_claim_operation()` treats a foreign `go_implementation` claim as non-blocking — exactly like expired/lapsed rows — when the thread's latest bridge status is no longer `GO` (a "status-superseded" claim). Implemented as a helper `_is_status_superseded_go_implementation(record, latest_status)` consulted in `acquire()`'s pre-read decision and re-checked inside the write transaction (the transaction re-reads the exact row per the WI-5784 discipline; `acquire()` already computes `_latest_status` via `_claim_values`, so no extra filesystem scan is added). `claim_status()` gains a `status_superseded_go_implementation` field so operators and any remaining waiters can see the state directly. This backstop covers filing paths that bypass the writer hook, crashed filings, and historical rows — and it is the reason A needs no timer: the staleness condition is the published thread state itself.

**Observer-kind semantics (A-1 support).** `_claim_operation()` allows any session's acquire to replace a `report_observer` claim (generalizing `_can_preempt_lingering_draft` into a non-blocking-kind replacement check); `current_claimed_bridge_id()` ignores observer claims when resolving a session's claimed bridge for packet lookup. `publish_lo_verdict()`'s holder check is deliberately unchanged: LO must still acquire the claim — the fix is that acquisition now succeeds the moment the report is on the chain.

**Serialization invariant preserved.** While the thread's latest status is `GO` (implementation window live), a foreign `go_implementation` claim blocks exactly as today. Nothing in A weakens the single-implementer window; A only ends the claim's power when the window has already closed on the chain.

### Mechanism B (alternative) — LO verdict publication exempt from PB claim holds

Exempt LO verdict publication from foreign PB claim holds: either skip the holder requirement in `publish_lo_verdict()` when the latest status is `NEW`/`REVISED` and the blocking claim is a foreign `go_implementation` claim, or introduce a `CLAIM_KIND_LO_VERDICT` that may preempt a foreign `go_implementation` claim under that same condition. Risk profile, from the code reading: (a) unconditioned, the exemption breaks the implementation-window serialization the claim exists to provide (an LO could publish into a thread mid-implementation, colliding with the PB's imminent report version); (b) conditioned on latest ∈ {`NEW`, `REVISED`}, its correctness core converges to A-2 — but embedded only in the provider-verdict path, leaving `_acquire_bridge_work_intent()` (the helper route the r1/r2b waiter scripts actually used) still blocked, so B would have to be re-implemented per publication route; (c) it widens the verdict-publication authority surface, which A leaves untouched.

### Recommendation

**Mechanism A, with both sub-mechanisms.** It is the least-privilege option: it changes no rule about who may publish what; it only ends a claim whose protected window has already closed on the append-only chain. It is event-driven — zero new timer, interval, retry, or throttle literals (DELIB-202667722; the `GO_IMPLEMENTATION_*` constants are not moved or retuned here, that externalization belongs to WI-5806). It unblocks every LO route at the single acquire choke point rather than per-route. And the downgrade disposition preserves the audit trail instead of silently deleting a foreign session's row. Conditioned-B's correct core is subsumed by A-2. Within A, the downgrade-vs-outright-release sub-choice is presented as LO review question 1; downgrade is recommended for provenance continuity.

### Rejected alternatives

- **Shorten the go_implementation TTL / grace.** Timer-tuning does not remove the class (any window long enough to implement in is long enough to block LO after filing) and contradicts the DELIB-202667722 relaxed-first, config-only timer directive. Rejected.
- **LO force-release CLI (manual or scripted).** Canonizes the `*_when_clear.py` / owner-intervention workaround instead of eliminating it; adds a foreign-row deletion authority with no published-state condition. Rejected.
- **Unconditioned Mechanism B.** Breaks implementation-window serialization; see above. Rejected as primary; conditioned core subsumed by A-2.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — required (blocking) — WI-5829's `source_spec_id`; the claim system serves bridge-protocol integrity, and the fix binds claim lifecycle to the append-only numbered chain state; nothing under `bridge/` is written, rewritten, or deleted by the lifecycle change.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — required (blocking) — governs the project-scoped authorization chain in which the work-intent claim participates; the PAUTH triple in the header proceeds under it and the claim/packet relationship (`current_claimed_bridge_id`) is preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — required (blocking) — this proposal's own linkage obligation; the Specification Links section is authored in backticked-bullet form directly under the h2 heading and verified pre-filing with the impl-auth extractor.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — required (blocking) — governs downstream verification; the Specification-to-Test Mapping below is the derivation record the Loyal Opposition verifier executes against, anchored on TEST-11785.
- `GOV-ARTIFACT-APPROVAL-001` — required (blocking) — no formal MemBase artifact is created, mutated, or retired by this implementation; the additive claim-registry schema columns are runtime coordination state, not governed artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — required (blocking) — root-boundary containment: every target path is in-root under `E:\GT-KB` (`scripts/`, `platform_tests/`); no application subtree and no out-of-root dependency is touched.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory — the fix is a write-time mechanical enforcement change (writer hook + registry gate), not an agent-discipline convention; the blocking decision becomes mechanically consistent with published thread state.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory — replaces ad-hoc waiter pollers and manual owner interventions with a deterministic, event-driven lifecycle rule.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — advisory — all evidence in this proposal derives from fresh canonical reads (live worktree code, `gt backlog show`, `gt projects authorizations`, on-disk waiter scripts) made this session; the staleness rule itself derives claim state from fresh chain reads rather than cached timers.
- `SPEC-1662` — advisory — assertion quality: the tests below assert behavioral outcomes (acquire results, downgrade records, publication unblocking), not structural presence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory — the downgrade disposition preserves the implementation-provenance record as a durable artifact rather than deleting it.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory — traceability: the downgraded observer row ties the implementing session, the report publication event, and the LO verdict window together in the durable coordination record.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory — defect-origin WI lifecycle transitions for WI-5829 follow the recorded trigger classifications.
- `GOV-STANDING-BACKLOG-001` — advisory — WI-5829 in MemBase is the sole work authority for this proposal; no parallel authority is created.
- Deliberations cited: `DELIB-202667735`, `DELIB-202667731`, `DELIB-202667730`, `DELIB-202667726`, `DELIB-202667722`.

## Prior Deliberations

- **DELIB-202667735** — Delegated proposal authoring and unblock-implementation mandate with parallel-operation program: the owner mandate under which this proposal-author worker files this NEW entry.
- **DELIB-202667731** — Owner decision (AUQ-20260730-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-GRANT): the list-free whole-project authorization recorded as PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730 under which this proposal is filed (fresh-verified this session: status `active`, `included_work_item_ids: null`, no expiry).
- **DELIB-202667730** — Harness Test final synthesis: consolidates the evaluation evidence, including the r1/r2b/r3 claim-window blocking episodes and the corrections-project creation that produced WI-5829.
- **DELIB-202667726** — Program pause + Harness Test program directive: the originating owner mandate for the Harness Test program whose evaluation runs produced this defect record.
- **DELIB-202667722** — Timer and throttle governance is a first-class concern (relaxed-first bias, registry visibility, no hard-coded values): constrains this fix to an event-driven design with zero new timer literals; timer externalization itself is WI-5806 scope.
- All deliberation, specification, work-item, and test IDs cited anywhere in this proposal were verified this session by exact-id lookup against the live MemBase (`groundtruth.db`); the evidence waiter scripts were verified by direct on-disk reads.

## Owner Decisions / Input

1. **DELIB-202667735** — the owner's delegated proposal-authoring and unblock-implementation mandate for the parallel-operation program authorizes this worker to file this NEW proposal for WI-5829. Authoring-only: this filing performs no implementation, no commit, and no review.
2. **DELIB-202667731 / AUQ-20260730-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-GRANT** — the owner's list-free whole-project grant (PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730) covers WI-5829 as a member work item. Per the PAUTH scope summary, this work item still requires its own full governed cycle: this proposal, independent Loyal Opposition GO carrying complete Clause Applicability evidence, fresh work-intent claim, implementation-start packet, exact target-path enforcement, implementation report, and independent VERIFIED with governed atomic finalization.
3. The two manual owner "Release your claim" interventions recorded in the WI-5829 defect description are treated as incident evidence, not as standing owner authorization for manual claim release; this proposal removes the need for them.
4. No additional owner decision is required to review this proposal. This proposal does not itself authorize implementation.

## Requirement Sufficiency

**Existing requirements sufficient.** The WI-5829 defect description (fresh-read verified via `gt backlog show WI-5829 --json`), GOV-FILE-BRIDGE-AUTHORITY-001, GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, the DELIB-202667722 timer-governance directive, and the DELIB-202667730 evaluation evidence fully constrain this implementation. No new or revised specification is required before implementation.

## Specification-Derived Verification Plan (Spec-to-Test Mapping)

MemBase test record `TEST-11785` ("LO verdict publication is not blocked by a stale post-report go_implementation claim", auto-created with WI-5829 per GOV-12) is the spec-derived test anchor. Its outcome sentence is the program acceptance statement: **"After a PB files its implementation report, LO verdict publication proceeds without manual claim release."** New tests land in `platform_tests/scripts/test_claim_lifecycle_report_filing.py` (new module) plus targeted additions to the two existing suites; the untouched timebox/auto-extend/role-eligibility suites remain green as regression locks.

| Requirement source | Test | Behavior asserted |
|---|---|---|
| TEST-11785 / WI-5829 | `test_lo_acquire_succeeds_after_report_filing` | End-to-end fixture: GO'd thread; PB session X holds `go_implementation`; implementation report (`NEW`) publishes with author session Y != X (the silent-no-op release case); an LO session Z `acquire` succeeds immediately after filing with no manual release and no waiting |
| WI-5829 (A-1) / GOV-FILE-BRIDGE-AUTHORITY-001 | `test_writer_downgrades_go_claim_on_report_publication` | After `write_bridge_file` publishes a `NEW`/`REVISED` entry, a foreign `go_implementation` claim on the thread is downgraded to `report_observer` with `downgraded_at`/`downgrade_reason` recorded; the same-session case still releases exactly as today; no `bridge/` file is written by the hook |
| WI-5829 (A-2) | `test_acquire_treats_status_superseded_claim_as_nonblocking` | With latest status `NEW` (report filed), a foreign `go_implementation` claim does not block `acquire`; the in-transaction re-read applies the same staleness decision |
| WI-5829 (serialization invariant) | `test_live_go_window_still_blocks_foreign_acquire` | With latest status `GO` and an unexpired foreign `go_implementation` claim, `acquire` still returns False — the implementation window is not weakened |
| WI-5829 (observer semantics) | `test_observer_claim_replaceable_and_ignored_for_packet_resolution` | Any session's `acquire` may replace a `report_observer` claim; `current_claimed_bridge_id` ignores observer claims |
| WI-5829 (operator visibility) | `test_claim_status_reports_status_superseded` | `claim_status` reports `status_superseded_go_implementation: true` for a post-report `go_implementation` claim |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | existing suites as regression locks | `platform_tests/scripts/test_go_impl_claim_timebox.py`, `test_work_intent_auto_extend.py`, `test_work_intent_role_eligibility.py`, and the existing `test_bridge_work_intent_registry.py` / `test_gtkb_bridge_writer.py` suites remain green: deadline/grace/extension math, auto-extend, role eligibility, and exact-holder release for the same-session case are unchanged |
| DELIB-202667722 (event-driven constraint) | acceptance criterion 4 (diff inspection) | The diff introduces zero new hard-coded timer, interval, retry, or throttle literals; `GO_IMPLEMENTATION_*` constants are untouched |

## Acceptance Criteria

1. `ruff check` and `ruff format --check` pass clean on every changed Python file (both are separate gates).
2. `python -m pytest platform_tests/scripts/test_claim_lifecycle_report_filing.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_gtkb_bridge_writer.py -q --tb=short` passes green, and `platform_tests/scripts/test_go_impl_claim_timebox.py`, `test_work_intent_auto_extend.py`, `test_work_intent_role_eligibility.py`, and `test_bridge_claim_cli.py` remain green.
3. TEST-11785 outcome demonstrated mechanically: in the end-to-end fixture, LO acquisition and verdict-path eligibility succeed immediately after report publication with no manual claim release, including when the report's author session id differs from the claim holder's.
4. The diff introduces zero new hard-coded timer, interval, retry, or throttle literals; the `GO_IMPLEMENTATION_*` constants are neither moved nor retuned (WI-5806 scope).
5. A live `GO`-window foreign `go_implementation` claim still blocks acquisition (serialization invariant test green).
6. The lifecycle change writes nothing under `bridge/`; in every fixture the chain files are byte-identical before and after the downgrade/release hook runs.
7. All registry writes introduced by this change flow through the existing `_run_write_transaction()` bounded-retry path.

## Risk And Rollback

- **Foreign-row mutation risk.** A-1 downgrades (and the same-session path deletes) a claim row the filing session does not hold. Mitigated: the downgrade fires only after a successful, capability-consumed publication of the superseding chain entry for that exact thread; the row is converted, not deleted; provenance fields are preserved and the downgrade is recorded on the row itself; the disposition is tested for both the mismatch and same-session cases.
- **Serialization-weakening risk.** Ending claims early could race a live implementation. Mitigated: both mechanisms key strictly off published thread state — the blocking power ends only when the chain already shows the window closed (`NEW`/`REVISED` published). The live-`GO` blocking test locks the invariant.
- **Concurrent-sibling risk.** WI-5815 (P0) is being proposed concurrently for the identity-resolution root cause, and WI-5784's registry retry plumbing is in the worktree awaiting its verification cycle. See the Coordination Note — implementation is sequenced after WI-5784's cycle finalizes, and this proposal's edits are function-scoped to the staleness/downgrade surface, disjoint from the retry transaction plumbing and from WI-5815's envelope/identity surfaces.
- **Rollback** is the exact revert of the two source files and the test modules. The two additive registry columns are backward-compatible (additive `_ensure_schema` migration; absent values read as NULL and downgrade behavior simply stops); no MemBase governed table, no dispatcher/TAFE state, and no bridge chain file is touched.

## Coordination Note (sequencing constraints, not scope)

- **WI-5784 (claim-registry lock hardening; thread awaiting verification).** The bounded-retry write plumbing (`WORK_INTENT_WRITE_*` constants, `_run_write_transaction`) is present in the current worktree registry code with its bridge cycle not yet finalized. WI-5829 implementation MUST be sequenced after that cycle lands. This proposal adds no second write discipline: every new registry write reuses `_run_write_transaction`. If the landed WI-5784 diff moves or renames a touched function, the implementing session re-baselines line references before editing and notes the re-baseline in the implementation report.
- **WI-5815 (P0 per-session envelope isolation; sibling proposal in flight).** Identity drift is the root cause of the silent exact-holder release no-op; WI-5815 fixes identity resolution, WI-5829 makes the claim lifecycle robust to residual mismatch regardless. The two are complementary, not alternatives. Expected file surfaces are disjoint (envelope/claim-CLI ambient resolution vs. registry blocking decision + writer hook); if WI-5815's approved `target_paths` intersect `scripts/bridge_work_intent_registry.py`, the later-GO'd thread re-baselines on the earlier landing.
- **WI-5806 / DELIB-202667722 (timer externalization; claim-max-hold pair first).** This proposal deliberately adds no tunable and does not externalize or retune `GO_IMPLEMENTATION_*`; the packet-TTL/claim-max-hold invariant pair remains WI-5806's first externalization slice. The event-driven design here reduces the behavioral load on those timers (they stop doing LO-unblocking duty) without changing their values.

## DISARM — KB Mechanics

This proposal creates and modifies source and test files only. This implementation performs no MemBase mutation, no KB write, and no groundtruth.db change. No MemBase records, specifications, ADRs, DCLs, GOV records, work items, Deliberation Archive entries, or other KB-governed artifacts are created, updated, or retired by this work. The `work_intent_claims` table is runtime coordination state (additive columns only), not a governed artifact class. The `kb_mutation_in_scope: false` flag accurately reflects a pure source-and-test change; citations of DELIB, spec, WI, and TEST IDs in this proposal are read-only references, not mutations. The `groundtruth.db` references above are read-only provenance citations, not write targets, so `groundtruth.db` is correctly absent from `target_paths`.

## DISARM — Packet Mechanics

The implementation-start packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-wi5829-claim-lifecycle-report-filing`, run only after an independent Loyal Opposition GO) is session-local implementation-scope evidence. It is not a formal artifact under GOV-ARTIFACT-APPROVAL-001 and requires no separate approval packet; it derives from TAFE/dispatcher bridge state, the approved proposal file, and the GO verdict file, expires, and fails closed on bridge status drift. The PAUTH triple cited in this proposal's header supplies the project-authorization evidence the packet validator consumes; it never broadens `target_paths` and never replaces the live latest-GO requirement, the fresh work-intent claim, or the packet itself.

## Recommended Commit Type

Recommended commit type: fix — repairs a defect (a coordination claim outliving the state it protects and blocking the counterpart role's governed publication) with regression coverage; the observer downgrade is remediation plumbing for the same defect class, not a new capability surface.

## Loyal Opposition Review Questions

1. Within Mechanism A, is downgrade-to-`report_observer` (provenance-preserving, two additive columns) the right disposition, or is outright release plus an audit-log line (no schema addition) preferable?
2. Should the A-1 writer hook fire on every successful thread publication, or only on `NEW`/`REVISED` (the statuses that supersede a GO window) as proposed?
3. Is confining the A-2 staleness decision to `acquire`/`claim_status` the right blast radius, or should `current_holder` itself filter status-superseded claims (wider, affects `publish_lo_verdict`'s holder check and packet resolution)?
4. Is any residual case better served by conditioned Mechanism B (LO-verdict exemption in `publish_lo_verdict` only), given that A-2 subsumes its correctness core at the acquire choke point?

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
