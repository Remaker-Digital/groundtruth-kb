NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code proposal-author worker dispatched under the DELIB-202667735 parallel-operation mandate; ambient native session bba2e933 with a healthy transcript-resolved prime-builder envelope; authoring-only scope - no implementation, commit, or review in this session


bridge_kind: prime_proposal
Document: gtkb-wi5815-per-session-envelope-claim-isolation
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5815

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "scripts/session_self_initialization.py", "scripts/gtkb_session_id.py", "scripts/bridge_claim_cli.py", "platform_tests/scripts/test_session_envelope_identity_isolation.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_gtkb_session_id.py"]
implementation_scope: session_identity_isolation_and_claim_ambient_hardening
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5815 Implementation Proposal — Per-Session Envelope and Claim Identity Isolation

## Summary

Make one session id mean one session, everywhere identity or role authority is resolved. Tonight's parallel-operation program (DELIB-202667735) surfaced five distinct identity incidents in a single evening, all traceable to three structural defects in the session-envelope/claim identity chain: (1) the SessionStart resolver fallback silently demotes a persisted transcript role at process-restart boundaries, violating DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001; (2) `gt session envelope open` can only mint a NEW timestamped session id — it cannot reissue or refresh the envelope document for an EXISTING session id, so identity repair mints stray envelopes instead of healing the real one; and (3) shared mutable current-envelope surfaces (`harness-state/<harness>/session-envelope.json`, `.claude/session/envelope.json`) plus cross-harness ambient env-var resolution let concurrent and delegated sessions adopt one another's identities, breaking review-independence discrimination. This proposal delivers per-session envelope documents keyed by the native session id as the sole identity/role authority, a transcript-role persistence guard, an envelope reissue operation for existing session ids, mint-collision and cross-harness-adoption rejection, and claim-CLI refusal to resolve ambient identity across harness boundaries.

This proposal is filed as the next numbered bridge file `bridge/gtkb-wi5815-per-session-envelope-claim-isolation-001.md`, continuing the append-only versioned bridge file chain. No prior versions are deleted or rewritten; the numbered bridge files form the canonical append-only audit trail per GOV-FILE-BRIDGE-AUTHORITY-001, and dispatcher/TAFE bridge state plus these status-bearing numbered files remain the canonical workflow state.

## Problem Statement And Live Evidence (fresh reads, 2026-07-31)

All claims below were re-derived this session from the live worktree, fresh `gt backlog show WI-5815 --json` / `gt projects authorizations` reads, fresh envelope-document reads, and first-line status-token reads of the cited bridge chains. Line numbers are current-worktree references.

### Tonight's five identity incidents

1. **(a) SessionStart resolver-fallback role demotion.** The leader interactive session's per-session envelope `harness-state/claude/session-envelopes/bba2e933-5d36-4c5b-ad04-08a653c8700f.json` carried a transcript-persisted `prime-builder` role (`::init gtkb pb`). At a process-restart boundary, the SessionStart path re-stamped it with the durable registry role: provenance issued `2026-07-31T02:51:26Z`, `role_resolution_source: session_resolver_fallback`, role demoted to `loyal-opposition` (the harness-B registry role — fresh read confirms `durable_registry_role: loyal-opposition` in the document's `role_resolution` block). Every `go_implementation` claim was blocked (`_go_implementation_eligible` requires document role `prime-builder`) until the owner re-sent `::init gtkb pb`; the healed document now shows `transcript_init_keyword` provenance re-issued `2026-07-31T06:21:41Z`. Code path: `scripts/session_self_initialization.py` lines 7639-7673 — the `role_source` ternary at line 7662 emits `session_resolver_fallback` whenever the role came from `discover_role_profile` (registry), and `ensure_worker_session` (`groundtruth-kb/src/groundtruth_kb/session/envelope.py` lines 698-750) unconditionally overwrites `role_asserted`/`role_resolved`/`role`/`role_resolution`/`worker_role_provenance` on the existing open document (lines 728-744). Note also that at SessionStart an explicit `--role-profile` argument is deliberately NOT treated as an override on the emit path (`if args.role_profile and not startup_emit_requested`, line 7618), so absent a dispatch keyword env the registry is the only role source — the demotion is structural, not incidental.
2. **(b) Split-brain: hook identity vs claim-registry identity.** Write-time hooks resolve the session id ambiently via `BRIDGE_WORK_INTENT_ORDER` (native Claude UUID from `CLAUDE_CODE_SESSION_ID`) and enforce `holder.session_id == hook_session_id` (`.claude/hooks/bridge-compliance-gate.py` lines 743-760). The claim registry resolves claim-role authority from the exact validated per-session document (`scripts/bridge_work_intent_registry.py` `_resolve_worker_role`, lines 754-781, via `resolve_worker_role_provenance`). After incident (a) demoted the native-UUID document, `go_implementation` claims under the native UUID were rejected, while repair attempts produced only repaired `B-<timestamp>` envelopes whose ids the hooks would never resolve — `holder == hook-session` became unsatisfiable in both directions, wedging the WI-5824 and WI-5827 implementation starts (their GO'd chains `bridge/gtkb-wi5824-protected-commit-checker-null-safety-ordering-*`, `bridge/gtkb-wi5827-bridge-lifecycle-metadata-normalization-*`, `bridge/gtkb-wi5827-post-nogo-refiling-protocol-reconciliation-*` were live at the time) until the owner re-sent `::init gtkb pb`.
3. **(c) Mint-only envelope open.** `gt session envelope open` exposes no `--session-id` option (fresh `--help` read this session); `open_session` with `session_id=None` always mints `_session_id(harness_id, opened_at)` — a fresh timestamped id per call (`envelope.py` lines 367-368, 390). There is no operation that reissues or refreshes the envelope document for an EXISTING session id. Tonight's repair attempts therefore minted two stray envelopes — `harness-state/claude/session-envelopes/B-2026-07-31T03-17-55Z.json` and `B-2026-07-31T06-14-04Z.json` — both still `status: open` with `init_keyword: ::init gtkb pb` on fresh read. They are cleanup targets of this proposal.
4. **(d) Shared envelope projection across Goose runs.** The WI-5808 evaluation showed all Goose runs adopting one session id: `G-2026-07-30T19-27-10Z` across dsv4pro r1/r2/r3 and even a Qwen proposal, so sibling runs carry identical `author_session_context_id` and claim records attribute foreign work to the leader — review-independence discrimination is broken for Goose sessions (WI-5815 defect description; TEST-11771). The r3 consequence on record: a compliant Prime Builder was converted into a pre-packet violator, NO-GO'd at `bridge/gtkb-wi5808-harness-probe-dsv4pro-r3-004.md` (fresh first-line read: `NO-GO`). The shared per-harness current file `harness-state/goose/session-envelope.json` and the minting behavior in (c) are the enabling surfaces.
5. **(e) Stale singular envelope hijacking role resolution.** A stale singular Loyal Opposition envelope (session `b34d5b84-5746-4eee-bd95-b6eeb3e70715`) hijacked role resolution mid-implementation during the WI-5824 cycle (WI-5824 report datapoint), healed only via the WI-4540 per-session role marker. The hazard is live right now: fresh read shows `harness-state/claude/session-envelope.json` still carries `session_id: b34d5b84-...` while the active leader session is `bba2e933-...` — the shared current slot is stale at this moment. The same shared-slot race was independently documented by Cursor LO in `bridge/cleanup-evidence/wi5733-unreceipted-publication-incident-20260729/gtkb-lo-shared-envelope-projection-cross-harness-race-advisory-001.md` (P1: concurrent harnesses stomp `.claude/session/envelope.json`; attribution fails closed or, worse, mis-attributes).

### Structural code findings (fresh reads)

- `write_current` (`envelope.py` lines 589-602) writes three surfaces on every envelope mutation: the authoritative per-session document, the shared per-harness `session-envelope.json`, and the `.claude/session/envelope.json` projection. The per-session document layer exists and `resolve_worker_role_provenance` (lines 522-586) prefers it, but a legacy fallback branch (lines 566-575) still reads shared `*/session-envelope.json` files as role authority for any harness that has no exact-match session document, and lifecycle consumers (`ensure_current`, `route_prompt_resources`, `open_topic`, `close_topic`, `close_current_topic`, `close_session`) still key entirely off the shared current file.
- `ensure_worker_session` (lines 698-750) is the only refresh path for an existing session document, and it overwrites role state unconditionally — there is no persistence guard distinguishing a `session_resolver_fallback` refresh from an owner-directed transcript change.
- `scripts/bridge_claim_cli.py` `_resolve_session_id` (lines 80-90) resolves ambient identity across the full `BRIDGE_WORK_INTENT_ORDER` with no harness-boundary check: a non-Claude session whose environment carries an inherited `CLAUDE_CODE_SESSION_ID`/`CLAUDE_SESSION_ID` (delegated spawn, shell inheritance, or leader-adjacent process) silently claims as the leader session. `scripts/gtkb_session_id.py` resolves values only — it does not report which env var supplied the id, so no caller can currently enforce a harness boundary.
- `scripts/bridge_work_intent_registry.py` `_worker_harness_selector` (lines 734-751) correctly treats harness name as a document selector, never role authority; the registry surface itself is sound and is NOT modified by this proposal.

## Proposed Design

Five slices. Identity/role authority becomes exclusively the per-session envelope document keyed by the native session id; every other surface is a projection, a cache, or a routing label.

### Slice A — Envelope identity isolation and reissue (`envelope.py`, `cli_session_handoff.py`)

1. **Transcript-role persistence guard (fixes incident a; makes DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001 mechanical).** `ensure_worker_session` becomes source-aware: when the existing open document's `worker_role_provenance.role_resolution_source` is `transcript_init_keyword` and the incoming refresh's `role_source` is `session_resolver_fallback`, the refresh MUST NOT overwrite the persisted role, role fields, or provenance. Instead it preserves the transcript state and appends a `suppressed_demotions` audit entry (`attempted_role`, `attempted_source`, `at` UTC timestamp) to the document. Incoming sources `transcript_init_keyword` (owner re-declared) and `dispatcher_composition` (headless dispatch owns its worker documents) continue to overwrite exactly as today. The guard lives in the envelope module so every caller (SessionStart, CLI, future surfaces) inherits it.
2. **Reissue for an existing session id (fixes incident c).** `gt session envelope open` gains `--session-id <id>`: (i) when the exact per-session document exists and is `open`, the operation reissues/refreshes that document in place — same session id, no new document minted; (ii) when the document exists and is `closed`, fail closed with guidance (closed sessions are terminal; open a new session); (iii) when no document exists, create one bound to exactly that id (subject to the same host-binding corroboration rules that govern host-bound opens for harnesses that have them). The module-level primitive is a reissue-aware path through `open_session`/`ensure_worker_session`; the CLI is a thin binding.
3. **Mint-collision rejection (uniqueness enforcement, fixes the reuse arm of incident d).** When `open_session` mints a fresh `{harness_id}-{opened_at}` id and the target document path already exists with `status: open`, fail closed (`EnvelopeError`) with reissue guidance. Minting never silently adopts or overwrites another session's open document, and no retry/uniquifier loop is introduced (zero new timer or retry literals per DELIB-202667722).
4. **Cross-harness adoption rejection.** Opening or ensuring with an explicit session id whose existing open document carries a different `harness_id`/`harness_name` fails closed. One session document belongs to one harness identity for its lifetime.
5. **Session-id-keyed close.** `gt session envelope close --session-id <id>` closes the exact per-session document (archive + `status: closed` via the existing `close_session` machinery, generalized to take a session id instead of implicitly operating on the shared current). This is the governed instrument for the Slice-E stray-envelope remediation and for closing any non-current session without touching the shared slot.

### Slice B — Role-authority de-projection (`envelope.py`)

1. **Projection marking.** `write_current` stamps the shared per-harness `session-envelope.json` copy with `"current_projection": true` and an `"authoritative_path"` field pointing at the per-session document (the `.claude/session/envelope.json` projection already carries `projection_authoritative`/`authoritative_path`). Role-authority readers reject any envelope carrying `current_projection: true`.
2. **Legacy fallback narrowing.** The legacy branch of `resolve_worker_role_provenance` (lines 566-575) that reads shared `*/session-envelope.json` files is narrowed to fire only for a harness with NO per-session documents at all (a pure pre-migration installation), and never for a document stamped `current_projection: true`. For every harness with a `session-envelopes/` directory in use, the exact document is the only role authority — a stale singular envelope (incident e) can no longer compete.
3. **Lifecycle consumers prefer the exact document.** `ensure_current` resolves the ambient session id (`BRIDGE_WORK_INTENT_ORDER`) and, when the exact per-session document exists and is open, operates on it; the shared current file is a fallback only when no ambient session id resolves. `route_prompt_resources`, `open_topic`, `close_topic`, `close_current_topic`, and `close_session` inherit this through `ensure_current`/parameterization. The shared files continue to be WRITTEN for compatibility readers; they simply stop being READ as identity or role authority.

### Slice C — SessionStart resolver persistence (`scripts/session_self_initialization.py`)

At the WI-5171 callsite (lines 7639-7673): before calling `ensure_worker_session` with `role_source="session_resolver_fallback"`, load the existing worker document for the resolved session id; when it is open with `transcript_init_keyword` provenance, thread the persisted transcript role through to the startup disclosure and role-profile selection instead of the registry role, so the session's reported role matches its document-authoritative role. The Slice-A guard is the enforcement layer; this callsite change makes SessionStart honest about it (disclosure, focus-menu shape, and marker writes all follow the persisted role). No change to dispatcher-composition or explicit-keyword behavior.

### Slice D — Cross-harness ambient hardening (`scripts/gtkb_session_id.py`, `scripts/bridge_claim_cli.py`)

1. **Source-reporting resolver (additive).** `scripts/gtkb_session_id.py` gains `SESSION_ID_ENV_HARNESS_FAMILY` — a frozen mapping from every member of `SESSION_ID_ENV_VARS` to a harness family (`claude`, `codex`, `cursor`, `antigravity`, and `goose` once WI-5812 lands `GOOSE_SESSION_ID`) or to `neutral` (`GTKB_BRIDGE_POLLER_RUN_ID`, `GTKB_INHERITED_SESSION_ID`, `GTKB_SESSION_ID`) — plus `resolve_session_id_with_source(...)` returning the resolved value together with the supplying env var (or none for explicit input). Both are additive, stdlib-only, and side-effect free, preserving the module's hook-safe contract; the existing drift-lock test is extended so every membership entry MUST have a family classification (the same recurrence-guard pattern that froze membership).
2. **Claim-CLI refusal across harness boundaries (fixes the adoption arm of incident d).** `bridge_claim_cli._resolve_session_id` uses the source-reporting resolver: when the active harness identity is determinable (explicit `GTKB_HARNESS_NAME`, or the same unambiguous native-marker detection the registry's `_worker_harness_selector` uses) AND the env var that supplied the ambient session id belongs to a DIFFERENT harness family, the CLI fails closed with actionable guidance (pass `--session-id` explicitly, or correct the environment). Neutral vars and explicit `--session-id` are unaffected — dispatched workers (`GTKB_BRIDGE_POLLER_RUN_ID`-first) and deliberate inheritance (`GTKB_INHERITED_SESSION_ID`, `GTKB_SESSION_ID`) keep their documented semantics. A non-Claude session can no longer silently claim as the Claude leader because a `CLAUDE_*` id leaked into its environment.

### Slice E — Stray-envelope remediation (runtime state; no source targets)

Using the Slice-A session-id-keyed close, close the two stray open envelopes minted during tonight's repair attempts (`B-2026-07-31T03-17-55Z`, `B-2026-07-31T06-14-04Z`) with a wrap outcome recording them as stray reissue artifacts. Nothing is deleted — `close_session` archives and marks closed, preserving the audit trail. The implementation report carries before/after evidence. These are unprotected runtime-state documents written by ordinary envelope operations; no additional target-path authorization is required, and the remediation is executed only through the governed CLI.

### Rejected alternatives

- **Delete the shared current-envelope files and the `.claude/session/envelope.json` projection outright.** Breaks unknown compatibility readers mid-migration and turns a role-authority fix into a repo-wide consumer audit. Rejected in favor of marked non-authoritative projections plus narrowed legacy fallback; full retirement is a follow-on candidate once consumers are provably per-session.
- **Uniquify colliding minted ids (suffix or retry loop).** Hides real collisions, invites divergent id conventions, and adds retry literals against the DELIB-202667722 timer discipline. Rejected — mint collisions fail closed with reissue guidance.
- **Blanket cross-harness ambient blocking in every resolver (hooks included).** The write-time hooks run inside the parent harness where ambient resolution is the designed behavior; blanket blocking risks bricking interactive flows for a boundary that only becomes dangerous at claim creation. Rejected — enforcement is scoped to the claim-CLI resolution boundary first, with registry-level refusal listed as a review question.
- **Let the registry remember pre-demotion role history (accept a demoted document by consulting prior provenance).** Role authority must remain the validated current document per GOV-SESSION-ROLE-AUTHORITY-001; historical-state adjudication inside the claim registry would create a second authority. Rejected — the fix is to stop the demotion at the document layer (Slice A), not to teach the registry to second-guess documents.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` — required (blocking) — WI-5815's `source_spec_id`; the explicit-worker-envelope role-authority split whose worker-document arm this proposal completes: per-session documents become the sole role authority and shared projections are mechanically excluded.
- `DCL-SESSION-ROLE-RESOLUTION-001` — required (blocking) — the deterministic role-resolution contract (dispatcher composition vs explicit worker boundaries); Slices A/C implement its precedence mechanically, including the fallback's non-authority over persisted transcript roles.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` — required (blocking) — transcript role persists across compaction/resume/SessionStart-like boundaries until the owner changes it; the Slice-A persistence guard is this constraint made mechanical (incident a is its recorded violation).
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` — required (blocking) — the persistence decision record the guard operationalizes.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` — required (blocking) — per-harness authoritative state with non-authoritative projections; Slice B enforces the projection/authority boundary this DCL declares.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — required (blocking) — `author_session_context_id` provenance depends on per-session identity isolation; shared-id adoption (incident d) is a provenance-integrity failure this proposal closes.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — required (blocking) — per-session identity is part of the capability floor for non-Claude harnesses; the uniqueness/adoption enforcement here is the platform-side complement to WI-5812's Goose identity chain.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — required (blocking) — claim/holder discipline and the append-only numbered bridge chain; the claim-CLI hardening protects the holder-identity invariant the bridge protocol depends on.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — required (blocking) — this proposal proceeds under the active list-free PAUTH cited in the header; the PAUTH replaces neither GO, claim, nor packet.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — required (blocking) — this proposal's linkage obligation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — required (blocking) — governs downstream verification; satisfied by the Specification-to-Test Mapping below.
- `GOV-ARTIFACT-APPROVAL-001` — required (blocking) — no formal MemBase artifact is mutated by this implementation; bridge artifacts and the PAUTH chain remain under the approval gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — required (blocking) — root-boundary containment: every target path is in-root under `E:\GT-KB` (`groundtruth-kb/src/`, `scripts/`, `platform_tests/`); no application subtree and no out-of-root dependency is touched.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` — advisory — interactive session-role authority is separate from durable harness roles; context for the transcript-vs-registry split.
- `ADR-ENVELOPE-META-MODEL-001` — advisory — envelope anatomy the per-session documents conform to.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory — every fix here converts a narrative persistence/isolation rule into write-time mechanical enforcement.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — advisory — all evidence derives from fresh canonical reads made this session; the design removes a class of stale-substitute reads (shared projections as authority).
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` — advisory — harness identity/role reads stay on canonical readers; no new harness-state surface is created (per-session documents already exist).
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory — reissue and session-id-keyed close convert manual envelope repair (which minted strays) into deterministic service surfaces.
- `SPEC-1662` — advisory — assertion quality: tests below assert behavioral outcomes (role survival, id identity, rejection reasons), not structural presence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory — durable-artifact framing of the corrections program.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory — traceability across proposal, tests, report, and decisions.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory — defect-origin WI lifecycle transitions for WI-5815 follow the recorded trigger classifications.
- `GOV-STANDING-BACKLOG-001` — advisory — WI-5815 in MemBase is the sole work authority for this proposal.
- Deliberations cited: `DELIB-202667735`, `DELIB-202667730`, `DELIB-202667731`, `DELIB-202667726`, `DELIB-202667722`.

## Prior Deliberations

- **DELIB-202667735** — Delegated proposal authoring and unblock-implementation mandate with parallel-operation program: the owner mandate under which this proposal-author worker files this NEW entry; the mandate's own operation surfaced incidents (a)-(c).
- **DELIB-202667730** — Harness Test final synthesis: consolidates the nine-run evaluation evidence including the shared Goose session id (`G-2026-07-30T19-27-10Z` across r1/r2/r3), the identical `author_session_context_id` on sibling runs, and the dsv4pro-r3 pre-packet violation (NO-GO at `-004`) that motivate WI-5815.
- **DELIB-202667731** — Owner decision (AUQ-20260730-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-GRANT): the list-free whole-project authorization recorded as PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730 under which this proposal is filed.
- **DELIB-202667726** — Program pause + Harness Test program directive: WI-5815's `source_owner_directive`; the originating owner mandate for the Harness Test program whose evaluation runs produced this defect record.
- **DELIB-202667722** — Timer and throttle governance: relaxed-first bias, registry visibility, no new hard-coded timer values — honored by this design (zero new timer/retry/interval literals; the rejected uniquifier-retry alternative was rejected partly on this ground).
- **Shared-envelope advisory thread** — `bridge/cleanup-evidence/wi5733-unreceipted-publication-incident-20260729/gtkb-lo-shared-envelope-projection-cross-harness-race-advisory-001.md` (Cursor LO, P1): independent documentation of the shared-projection cross-harness race (Claude PB envelope stomping the Cursor LO projection; `resolve_changed_by` failing closed; manual restore as defective workaround). Slice B is the durable fix it called for.
- **Delegated-subagent provenance advisory thread** — `bridge/gtkb-advisory-delegated-subagent-session-provenance-inheritance-001.md` through `-004.md` (latest `GO`): the delegated-spawn provenance-inheritance class WI-5815's description links; Slice D's harness-boundary refusal addresses its ambient-inheritance arm at the claim boundary.
- All deliberation, specification, work-item, and test IDs cited anywhere in this proposal were verified this session by exact-id lookup against the live MemBase (`groundtruth.db`); the evidence bridge chains and envelope documents were verified by direct fresh reads of the numbered files and runtime state.

## Owner Decisions / Input

1. **DELIB-202667735** — the owner's delegated proposal-authoring and unblock-implementation mandate for the parallel-operation program authorizes this worker to file this NEW proposal for WI-5815. Authoring-only: this filing performs no implementation, no commit, and no review.
2. **DELIB-202667731 / AUQ-20260730-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-GRANT** — the owner's list-free whole-project grant (PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730) covers WI-5815 as a member work item. Per the PAUTH scope summary, this work item still requires its own full governed cycle: this proposal, independent Loyal Opposition GO carrying complete Clause Applicability evidence, fresh work-intent claim, implementation-start packet, exact target-path enforcement, implementation report, and independent VERIFIED with governed atomic finalization.
3. No additional owner decision is required to review this proposal. This proposal does not itself authorize implementation.

## Requirement Sufficiency

**Existing requirements sufficient.** The WI-5815 defect description (fresh-read verified via `gt backlog show WI-5815 --json`), GOV-SESSION-ROLE-AUTHORITY-001, DCL-SESSION-ROLE-RESOLUTION-001, DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001, DCL-SESSION-ENVELOPE-DURABILITY-001, GOV-HARNESS-ONBOARDING-CONTRACT-001, the GOV-12 test anchor TEST-11771, and the DELIB-202667730 synthesis fully constrain this implementation. No new or revised specification is required before implementation.

## Specification-Derived Verification Plan (Spec-to-Test Mapping)

MemBase test record `TEST-11771` ("Concurrent Goose sessions carry distinct, self-owned session identities") is the spec-derived test anchor created with WI-5815 per GOV-12. New behavioral tests land in `platform_tests/scripts/test_session_envelope_identity_isolation.py` (new module); existing suites are extended where the behavior they lock changes.

| Requirement source | Test | Behavior asserted |
|---|---|---|
| DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001 / incident (a) | `test_fallback_refresh_cannot_demote_transcript_role` | An open document with `transcript_init_keyword` PB provenance refreshed with `role_source=session_resolver_fallback` and a differing registry role keeps role `prime-builder`, keeps transcript provenance, and records a `suppressed_demotions` entry |
| DCL-SESSION-ROLE-RESOLUTION-001 | `test_dispatcher_and_transcript_sources_still_overwrite` | `dispatcher_composition` and a fresh `transcript_init_keyword` refresh overwrite role state exactly as today (no persistence over-reach) |
| GOV-SESSION-ROLE-AUTHORITY-001 / incident (b) | `test_native_uuid_claim_role_survives_sessionstart_boundary` | After a simulated SessionStart fallback refresh, `_resolve_worker_role` for the native-UUID session still returns `prime-builder` and a `go_implementation` claim is grantable (extends `platform_tests/scripts/test_bridge_work_intent_registry.py`) |
| Incident (c) / DCL-SESSION-ENVELOPE-DURABILITY-001 | `test_reissue_binds_existing_open_document_without_minting` | `envelope open --session-id <existing-open-id>` refreshes the exact document in place: same session id, unchanged `opened_at`, no new document under `session-envelopes/` (extends `platform_tests/scripts/test_session_envelope_cli_provenance.py`) |
| Incident (c) | `test_reissue_of_closed_or_unsafe_session_fails_closed` | Reissue against a closed document, and any unsafe session-id token, fail closed with guidance |
| Uniqueness enforcement / TEST-11771 | `test_open_mint_collision_fails_closed` | Minting a fresh id whose document already exists open raises `EnvelopeError` with reissue guidance; no overwrite, no adoption, no uniquifier |
| TEST-11771 / incident (d) | `test_explicit_session_id_cross_harness_adoption_rejected` | Ensuring/opening with an explicit session id whose open document belongs to a different harness identity fails closed |
| TEST-11771 / incident (d) | `test_claim_cli_refuses_cross_harness_ambient_identity` | With `GTKB_HARNESS_NAME=goose` and only `CLAUDE_CODE_SESSION_ID` in the environment, `bridge_claim_cli` claim resolution fails closed with guidance; neutral vars (`GTKB_BRIDGE_POLLER_RUN_ID`, `GTKB_SESSION_ID`, `GTKB_INHERITED_SESSION_ID`) and explicit `--session-id` still resolve |
| Incident (e) / DCL-SESSION-ENVELOPE-DURABILITY-001 | `test_exact_document_beats_shared_projection_and_singular_envelope` | With a stale shared `session-envelope.json` (different session id / role) present, role resolution and `ensure_current`-backed lifecycle operations bind the exact ambient-session document; a `current_projection: true` envelope is never role authority |
| Slice B narrowing | `test_legacy_fallback_only_for_pre_migration_harness` | The legacy shared-file fallback fires only for a harness with no per-session documents at all and validating provenance; otherwise it is inert |
| WI-4540 composition | `test_per_session_marker_is_cache_only` | Marker files under `.claude/session/role-*.json` never override the exact document's role (extends `platform_tests/scripts/test_session_envelope_runtime.py`) |
| Drift-lock (recurrence guard) | family-map completeness test | Every member of `SESSION_ID_ENV_VARS` has exactly one harness-family classification; `resolve_session_id_with_source` agrees with `resolve_session_id` on value for every documented order (extends `platform_tests/scripts/test_gtkb_session_id.py`) |
| GOV-FILE-BRIDGE-AUTHORITY-001 | zero-bridge-write property | No envelope/claim operation in the new tests writes anything under `bridge/` (asserted on the fixture tree) |

## Acceptance Criteria

1. `ruff check` and `ruff format --check` pass clean on every changed Python file (both are separate gates).
2. `python -m pytest platform_tests/scripts/test_session_envelope_identity_isolation.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_gtkb_session_id.py -q --tb=short` passes green.
3. Incident-(a) regression closed: the fallback-demotion sequence reproduced in tests cannot demote a transcript role; the suppressed-demotion audit entry is present.
4. Incident-(c) regression closed: reissue binds the existing id; the mint path fails closed on open-document collision; no test or fixture path ever produces a second document for the same logical session.
5. Incident-(d) regression closed: cross-harness ambient claim resolution fails closed; cross-harness explicit-id adoption of an open document fails closed.
6. Incident-(e) regression closed: a stale shared/singular envelope never wins role authority over the exact per-session document; shared current files are stamped `current_projection: true`.
7. The diff introduces zero new hard-coded timer, interval, retry, or throttle literals (DELIB-202667722).
8. `scripts/gtkb_session_id.py` remains stdlib-only with no import-time side effects (hook-safe contract preserved); additions are purely additive relative to the WI-5812 diff.
9. Stray-envelope remediation evidence in the implementation report: `B-2026-07-31T03-17-55Z` and `B-2026-07-31T06-14-04Z` closed via the governed session-id-keyed close; zero envelope documents deleted.
10. No envelope or claim operation writes under `bridge/`; dispatcher/TAFE bridge state is untouched by this implementation.

## Risk And Rollback

- **Compatibility risk (Slice B).** Some reader may depend on the shared current file as authority. Mitigated: shared files are still written (marked), only role-authority and identity reads change; the legacy fallback remains for pure pre-migration harness dirs; targeted suites plus the envelope runtime suite guard the consumers named in this proposal. Residual unknown readers surface as test failures at implementation time and are enumerated in the report.
- **Over-persistence risk (Slice A guard).** A genuinely-stale transcript role could persist past its useful life. Mitigated: the guard yields only to explicit owner re-declaration or dispatcher composition — exactly the DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001 contract; the suppressed-demotion audit trail makes every suppressed overwrite visible; the owner's `::init` remains the universal correction instrument.
- **Boundary-refusal friction risk (Slice D).** A legitimate cross-harness workflow could be blocked at claim time. Mitigated: explicit `--session-id` and the three neutral env vars remain fully functional; the refusal message names both remedies; headless dispatch (`GTKB_BRIDGE_POLLER_RUN_ID`-first) is unaffected.
- **Concurrent-thread risk.** WI-5812 (GO'd, implementation pending) shares `scripts/gtkb_session_id.py` and the Goose identity flow; wi5568 (non-terminal) touches `cli_session_handoff.py`. See the Coordination Note — sequencing plus function-scoped disjoint diffs.
- **Rollback** is the exact revert of the five source files and the test modules. The stray-envelope closures are archived state transitions (reversible by reissue if ever needed); no MemBase mutation, no dispatcher/TAFE state, and no bridge chain file is touched.

## Coordination Note (sequencing constraints, not scope)

1. **WI-5812** (`bridge/gtkb-wi5812-goose-governed-filing-attestation-003.md`, GO at `-004`, implementation pending) explicitly reserves per-session uniqueness enforcement, reuse/collision rejection, and claim-CLI ambient hardening for WI-5815 and mints per-spawn Goose ids (`GOOSE_SESSION_ID`, one spawn = one id) in its Slice D. WI-5815 implementation is sequenced strictly AFTER WI-5812 lands. Shared file `scripts/gtkb_session_id.py`: WI-5812 edits the membership set and order tuples; WI-5815 adds a new family map and a new resolver function — disjoint hunks; the implementing session re-baselines and includes `GOOSE_SESSION_ID → goose` in the family map once it exists.
2. **wi5568** (`bridge/gtkb-wi5568-session-envelope-host-binding-repair-*`, latest `NO-GO` at `-004`, non-terminal) repairs envelope-open host binding in `cli_session_handoff.py`. WI-5815's `--session-id` reissue option composes with host bindings (an explicit id must match the host-bound env where a binding exists) and is option-additive. Whichever thread lands second re-baselines; if wi5568 is revised into conflict, the implementing session surfaces it in the report rather than silently merging.
3. **WI-4540** per-session role markers are cache only and are not modified; the deterministic precedence in this proposal (exact document → transcript persistence → registry fallback; markers/projections never authority) is the composition contract.
4. **WI-5824 / WI-5827** chains are motivating evidence only; no surface overlap.

## DISARM — KB Mechanics

This proposal creates and modifies source and test files only, plus governed runtime-state transitions (stray-envelope closures) executed through the CLI it introduces. No MemBase records, specifications, ADRs, DCLs, GOV records, work items, Deliberation Archive entries, or other KB-governed artifacts are created, updated, or retired by this work. The `kb_mutation_in_scope: false` flag accurately reflects that; citations of DELIB, spec, WI, and TEST IDs in this proposal are read-only references, not mutations.

## DISARM — Packet Mechanics

The implementation-start packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-wi5815-per-session-envelope-claim-isolation`, run only after an independent Loyal Opposition GO) is session-local implementation-scope evidence. It is not a formal artifact under GOV-ARTIFACT-APPROVAL-001 and requires no separate approval packet; it derives from TAFE/dispatcher bridge state, the approved proposal file, and the GO verdict file, expires, and fails closed on bridge status drift. The PAUTH triple cited in this proposal's header supplies the project-authorization evidence the packet validator consumes; it never broadens `target_paths` and never replaces the live latest-GO requirement, the fresh work-intent claim, or the packet itself.

## Recommended Commit Type

Recommended commit type: fix — repairs a defect cluster (identity demotion, mint-only repair, shared-identity adoption) with regression coverage; the reissue/close surfaces are remediation plumbing for the same defect class, not a new capability surface.

## Loyal Opposition Review Questions

1. Is fail-closed mint-collision rejection the right posture, or should a deterministic disambiguation (never a retry loop) be preferred for the second-resolution `{harness_id}-{opened_at}` collision window?
2. Should the legacy shared-projection fallback in `resolve_worker_role_provenance` be removed outright in this WI rather than narrowed to pre-migration harness dirs?
3. Is the claim-CLI resolution boundary the right sole home for cross-harness ambient refusal, or should `bridge_work_intent_registry.claim()` also refuse when env-source evidence is available?
4. Is the `suppressed_demotions` audit field sufficient mechanical evidence for DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001, or should suppressed demotions also surface in the SessionStart disclosure?
5. Is the Slice-E stray-envelope closure correctly scoped as governed runtime-state remediation inside this WI, or should it be deferred to a separate hygiene pass?

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
