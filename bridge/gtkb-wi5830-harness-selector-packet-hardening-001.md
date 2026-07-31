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
Document: gtkb-wi5830-harness-selector-packet-hardening
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5830

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization_harness_selector.py", "platform_tests/scripts/test_implementation_authorization_packet_paths.py", "platform_tests/scripts/test_implementation_authorization.py"]
implementation_scope: worker_harness_selector_env_hardening_and_packet_path_disclosure_overwrite_protection
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5830 Implementation Proposal — Harness-Selector Env-Leakage Fix, Begin Packet-Path Disclosure, And Named-Packet Overwrite Protection

## Summary

Repair three coupled defects in the implementation-start surface of `scripts/implementation_authorization.py`, all evidenced verbatim in the dsv4pro-r3 harness-test transcript. (a) `_worker_harness_selector()` infers `codex` whenever `CODEX_HOME` is present in the environment — an installation marker, not a session marker — so a legitimately-declared Goose Prime Builder is pinned to the wrong harness envelope directory and fails provenance until the operator bypasses with `GTKB_HARNESS_NAME=goose`; the fix makes explicit declaration outrank installation-marker inference. (b) `begin` prints the packet JSON but never its file path, so the r3 Prime Builder searched the wrong directory, concluded "(none)", and after compaction re-ran `begin`; the fix prints the written packet path(s). (c) That re-run silently OVERWROTE packet #1 in the named cache (`by-bridge/<bridge-id>.json`), destroying audit evidence; the fix makes named-packet overwrites version/append into an append-only history instead of silently destroying the prior packet.

This proposal is filed as the next numbered bridge file `bridge/gtkb-wi5830-harness-selector-packet-hardening-001.md`, continuing the append-only versioned bridge file chain. No prior versions are deleted or rewritten; the numbered bridge files form the canonical append-only audit trail per GOV-FILE-BRIDGE-AUTHORITY-001, and dispatcher/TAFE bridge state plus these status-bearing numbered files remain the canonical workflow state.

## Problem Statement And Live Evidence (fresh reads, 2026-07-31)

All claims below were re-derived this session from the live worktree, `gt backlog show WI-5830 --json`, `gt projects show-authorization`, first-line bridge-chain reads, and the r3 transcript of record. Line numbers are current-worktree references.

1. **Installation-marker inference.** `_worker_harness_selector()` (`scripts/implementation_authorization.py` lines 2150-2161) resolves, in order: explicit `GTKB_HARNESS_NAME`; dispatch run (`GTKB_BRIDGE_POLLER_RUN_ID` → `None`); `CLAUDE_CODE_SESSION_ID`/`CLAUDECODE` → `claude`; then `CODEX_THREAD_ID` **or `CODEX_HOME`** → `codex` (line 2159). `CODEX_HOME` is a workstation-persistent configuration-directory pointer present in every shell on a Codex-installed machine; it is evidence that Codex is installed, not that the current session is Codex.
2. **Wrong-envelope pinning.** `finalize_implementation_start_packet` passes the selector result to `resolve_worker_role_provenance` (line 2213). With a harness name supplied, the resolver (`groundtruth-kb/src/groundtruth_kb/session/envelope.py` lines 522-551) pins document lookup to `harness-state/<harness>/session-envelopes/<session>.json` and, when that harness directory contains envelopes but none matches the current session, raises "Worker role provenance session id does not match the current session." (lines 543-544). Only when the selector returns `None` does the harness-agnostic exact-session-document scan (lines 553-575) run — the branch that would have found the declared Goose envelope by session id.
3. **The r3 failure on record.** `harness-test-transcripts/dsv4pro-r3-final.json` records the verbatim rejection, repeatedly (transcript lines 2043, 2063, 2147, 2196, 2280, 2364 ff.): `session 'G-2026-07-30T19-27-10Z' resolves to worker session document rejected: Worker role provenance session id does not match the current session. (not prime-eligible)`. The Goose session was legitimately declared; `CODEX_HOME` leakage selected `codex` and validated the wrong envelope directory. The recorded bypass was `GTKB_HARNESS_NAME=goose` (WI-5830 description, fresh read).
4. **Packet path never printed.** The `begin` CLI (lines 3198-3214) writes the named-cache packet and the `current.json` active pointer, then prints only the bare packet JSON (line 3213). Neither `.gtkb-state/implementation-authorizations/current.json` (`DEFAULT_PACKET_RELATIVE_PATH`, line 31) nor `.gtkb-state/implementation-authorizations/by-bridge/<bridge-id>.json` (`packet_path_for_bridge`, line 292) appears in the output. The r3 Prime Builder searched the wrong directory, concluded "(none)", and after compaction re-created the packet.
5. **Silent overwrite, audit loss.** `write_packet` (lines 2128-2132) and `write_named_packet` (lines 2135-2147) both call `path.write_text(...)` unconditionally. The r3 transcript records packet #1 for `gtkb-wi5808-harness-probe-dsv4pro-r3` with `created_at 2026-07-30T22:58:59Z` (transcript line 8856; named path quoted at line 8972) and packet #2 with `created_at 2026-07-30T23:10:22Z` (line 9356) written to the same paths — packet #1's evidence bytes are unrecoverable. The named cache's own docstring (lines 292-296) positions it as the surface that "survive[s] overwrites of the `current.json` active pointer", yet it does not survive a same-bridge re-mint.
6. **Legitimate re-mint exists.** The wi5827 implementation report (`bridge/gtkb-wi5827-post-nogo-refiling-protocol-reconciliation-003.md`, Commands Executed) records a governed re-mint of a live packet after an identity-wedge heal — so a hard refusal to re-run `begin` would wedge a recovery flow already on record. Overwrite protection must version/append, not refuse re-mint.
7. **Sibling ambient surface.** Session-id resolution has its own ambient-inference precedence (`scripts/gtkb_session_id.py` `BRIDGE_WORK_INTENT_ORDER`, lines 78-88, dispatch-run-first), analyzed in the wi5827 identity-wedge evidence. That tuple contains no `CODEX_HOME` entry and is NOT touched by this proposal; the fix here is confined to harness selection.

## Proposed Design

Three slices, all inside `scripts/implementation_authorization.py`, function-scoped to the selector and packet-write/CLI-emission surfaces only.

### Slice A — Selector hardening: explicit declaration outranks installation-marker inference

Remove `CODEX_HOME` from the inference disjunction at line 2159; `CODEX_THREAD_ID` (a per-session marker) remains the sole codex inference signal. All other branches are unchanged: explicit `GTKB_HARNESS_NAME` still wins outright; dispatch runs still return `None`; Claude session markers still infer `claude`. With no session-scoped marker present the selector now returns `None`, which routes `resolve_worker_role_provenance` into its existing harness-agnostic exact-session-document scan — the declaration surface. A legitimately-declared Goose Prime Builder (envelope at `harness-state/goose/session-envelopes/<session>.json`) then validates with no `GTKB_HARNESS_NAME` bypass, regardless of `CODEX_HOME` presence. No change to `groundtruth_kb.session.envelope` and no change to `gtkb_session_id.py` precedence tuples.

### Slice B — `begin` prints the packet file path(s)

On the durable write path, `begin` emits a single JSON document that includes the written paths, recommended shape:

```json
{"packet": { ...canonical packet... }, "packet_paths": {"named": "<abs by-bridge path>", "active_pointer": "<abs current.json path>", "superseded_preserved": "<history path or null>"}}
```

`--no-write` keeps the current bare-packet output (nothing is written, so no path claim), and the error shape (`{"authorized": false, ...}`) is unchanged. The on-disk packet files remain byte-canonical (no new keys), so `packet_hash` semantics and on-disk hash verification are untouched. A repo search this session found the only machine consumers of `begin` success stdout are the assertions in `platform_tests/scripts/test_implementation_authorization.py` (e.g., lines 1024-1039), which are updated in-scope; `activate` output is deliberately left unchanged (candidate follow-on).

### Slice C — Named-packet overwrite protection: version/append, never silently destroy

`write_named_packet` gains an overwrite guard: when the target named packet exists and its bytes differ from the new packet, the existing bytes are first preserved to an append-only history location `.gtkb-state/implementation-authorizations/by-bridge/<bridge-id>.history/<UTC-timestamp>-<sha256-8>.json`, then the new packet is written; the preserved path is surfaced through the Slice B `superseded_preserved` field. A byte-identical rewrite creates no history entry. If history preservation fails, the write fails closed (`AuthorizationError`) and the existing packet is left untouched — the "refuse silent overwrite" component. `current.json` (`write_packet`) remains an active pointer overwritten by design; the named cache plus history becomes the durable audit surface that actually survives same-bridge re-mints. No packet-dict mutation occurs anywhere, so `packet_hash` computation is untouched.

### Rejected alternatives

- **Hard refusal when a live packet exists.** Would wedge the legitimate re-mint recovery flow on record (wi5827 -003 re-mint after the identity-wedge heal). Versioning preserves audit evidence without blocking recovery. Rejected.
- **Trailing plain-text path lines after the packet JSON.** Breaks the single-JSON-document stdout contract the existing tests assert (`json.loads` over full stdout). Rejected.
- **Presentation-only keys inside the packet dict (hash-exempt underscore keys).** Requires teaching `packet_hash` to ignore reserved keys — hash-semantics blast radius for a display concern. Rejected in favor of the nested wrapper; raised as a review question.
- **Adding per-harness env markers (e.g., `GOOSE_SESSION_ID`) instead of removing `CODEX_HOME`.** Perpetuates unbounded env inference per onboarded harness; the harness-agnostic declaration scan already exists and scales with GOV-HARNESS-ONBOARDING-CONTRACT-001 onboarding. Rejected.
- **Removing env inference entirely (selector returns `None` unless `GTKB_HARNESS_NAME` set).** Changes behavior for live Claude/Codex interactive sessions that rely on session-scoped inference to disambiguate multi-envelope states (existing `test_selected_prime_document_wins_over_same_session_lo_document` semantics). The narrow installation-marker removal suffices for the recorded defect. Rejected.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — required (blocking) — this proposal's own specification-linkage obligation; this section is authored in the backticked-bullet form directly under the h2 heading that both the applicability preflight and the strict `begin`-time extractor accept.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — required (blocking) — WI-5830's `source_spec_id`; the harness onboarding contract whose capability floor a newly-onboarded harness (Goose, harness G) exercised when the selector misidentified it; the fix makes selection declaration-driven rather than vendor-env-driven.
- `GOV-SESSION-ROLE-AUTHORITY-001` — required (blocking) — explicit worker envelopes are the role/provenance authority; this proposal restores the envelope-declaration path as the operative selector when no session-scoped marker exists.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — required (blocking) — governs the project-scoped authorization chain (`implementation_authorization.py`) whose `begin` path this proposal hardens; the PAUTH triple in the header proceeds under it.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — required (blocking) — audit-trail durability authority; Slice C extends the same never-silently-destroy discipline to implementation-start packet evidence, and the numbered bridge chain of this thread stays append-only.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — required (blocking) — governs downstream verification; the Specification-to-Test Mapping below is the derivation record the Loyal Opposition verifier executes against.
- `GOV-ARTIFACT-APPROVAL-001` — required (blocking) — no formal MemBase artifact is mutated by this implementation; bridge artifacts and the PAUTH chain remain under the approval gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — required (blocking) — root-boundary containment: every target path is in-root under `E:\GT-KB` (`scripts/`, `platform_tests/`); the history directory is under `.gtkb-state/`; no application subtree and no out-of-root dependency is touched.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory — the selector and packet gates are mechanical enforcement layers; this proposal repairs their evidence-accuracy without weakening any gate.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — advisory — all evidence in this proposal derives from fresh canonical reads (live worktree code, `gt backlog show`, `gt projects show-authorization`, bridge first-line reads, transcript of record) made this session.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory — packet-path disclosure and history preservation convert error-prone agent rediscovery (searching for packets by hand) into deterministic service output.
- `SPEC-1662` — advisory — assertion quality: the tests below assert behavioral outcomes (selector results, provenance resolution, stdout path fields, history byte-preservation), not structural presence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory — packet history entries are durable evidence artifacts rather than transient session state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory — traceability: `superseded_preserved` disclosure ties re-mints to their preserved predecessors.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory — defect-origin WI lifecycle transitions for WI-5830 follow the recorded trigger classifications.
- `GOV-STANDING-BACKLOG-001` — advisory — WI-5830 in MemBase is the sole work authority for this proposal; no parallel authority is created.
- Deliberations cited: `DELIB-202667735`, `DELIB-202667730`, `DELIB-202667731`, `DELIB-202667726`.

## Prior Deliberations

- **DELIB-202667735** — Delegated proposal authoring and unblock-implementation mandate with parallel-operation program: the owner mandate under which this proposal-author worker files this NEW entry.
- **DELIB-202667730** — Harness Test final synthesis: consolidates the evaluation evidence, including the dsv4pro-r3 provenance failures and packet re-creation incident that motivate WI-5830.
- **DELIB-202667731** — Owner decision (AUQ-20260730-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-GRANT): the list-free whole-project authorization recorded as PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730 under which this proposal is filed.
- **DELIB-202667726** — Program pause + Harness Test program directive: the originating owner mandate for the Harness Test program whose evaluation runs produced this defect record.
- All deliberation, specification, work-item, and test IDs cited anywhere in this proposal were verified this session by exact-id lookup against the live MemBase (`groundtruth.db`); the evidence bridge chains were verified by direct first-line status-token reads of the numbered files.

## Owner Decisions / Input

1. **DELIB-202667735** — the owner's delegated proposal-authoring and unblock-implementation mandate for the parallel-operation program authorizes this worker to file this NEW proposal for WI-5830. Authoring-only: this filing performs no implementation, no commit, and no review.
2. **DELIB-202667731 / AUQ-20260730-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-GRANT** — the owner's list-free whole-project grant (PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730, fresh-verified `status: active` with `included_work_item_ids: null` this session) covers WI-5830 as a member work item. Per the PAUTH scope summary, this work item still requires its own full governed cycle: this proposal, independent Loyal Opposition GO carrying complete Clause Applicability evidence, fresh work-intent claim, implementation-start packet, exact target-path enforcement, implementation report, and independent VERIFIED with governed atomic finalization.
3. No additional owner decision is required to review this proposal. This proposal does not itself authorize implementation.

## Requirement Sufficiency

**Existing requirements sufficient.** The WI-5830 defect description (fresh-read verified via `gt backlog show WI-5830 --json`), GOV-HARNESS-ONBOARDING-CONTRACT-001, GOV-SESSION-ROLE-AUTHORITY-001, GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, GOV-FILE-BRIDGE-AUTHORITY-001, and the DELIB-202667730 diagnosis evidence fully constrain this implementation. No new or revised specification is required before implementation.

## Specification-Derived Verification Plan (Spec-to-Test Mapping)

MemBase test record `TEST-11786` ("Selector honors explicit harness declaration and packets are overwrite-protected") is the spec-derived test anchor created with WI-5830 per GOV-12. Its outcome contract: **explicit declaration outranks CODEX_HOME inference; begin output includes the packet file path; re-running begin for a live packet versions rather than overwrites.** Selector tests extend the existing `platform_tests/scripts/test_implementation_authorization_harness_selector.py`; packet-path/overwrite tests land in `platform_tests/scripts/test_implementation_authorization_packet_paths.py` (new module, same conventions); stdout-consumer assertions are updated in `platform_tests/scripts/test_implementation_authorization.py`.

| Requirement source | Test | Behavior asserted |
|---|---|---|
| GOV-HARNESS-ONBOARDING-CONTRACT-001 / TEST-11786 | `test_codex_home_alone_does_not_select_codex` | With only `CODEX_HOME` set (no session-scoped marker), `_worker_harness_selector()` returns `None` |
| GOV-SESSION-ROLE-AUTHORITY-001 / TEST-11786 | `test_declared_goose_provenance_resolves_despite_codex_home` | Goose worker-session envelope declared for the current session + `CODEX_HOME` set + no `GTKB_HARNESS_NAME`: `finalize_implementation_start_packet` resolves goose prime-builder provenance (explicit declaration outranks `CODEX_HOME` inference; the r3 rejection no longer reproduces) |
| TEST-11786 (session-marker regression) | `test_codex_thread_id_still_selects_codex` | `CODEX_THREAD_ID` alone still selects `codex`; explicit `GTKB_HARNESS_NAME` still outranks everything |
| GOV-SESSION-ROLE-AUTHORITY-001 (precedence lock) | existing `test_implementation_authorization_harness_selector.py` suite | All existing selector/provenance behaviors unchanged (the suite's `CODEX_HOME`-independent assertions remain green without edits) |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 / TEST-11786 | `test_begin_stdout_includes_packet_paths` | `begin` success stdout is a single JSON document whose `packet_paths.named` and `packet_paths.active_pointer` equal the real written paths; `--no-write` and error shapes unchanged |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | updated success-path assertions in `test_implementation_authorization.py` | Canonical packet inside the wrapper still satisfies `packet_hash` recomputation and byte-equals both on-disk packet files |
| GOV-FILE-BRIDGE-AUTHORITY-001 / TEST-11786 | `test_rerun_begin_versions_previous_packet` | Re-running `begin` for a bridge id with a live differing named packet preserves the prior packet byte-identically in the history location before writing, and discloses `superseded_preserved`; re-running with byte-identical content creates no history entry |
| TEST-11786 (fail-closed) | `test_history_preservation_failure_blocks_overwrite` | When history preservation fails, `write_named_packet` raises `AuthorizationError` and the existing named packet is untouched |
| SPEC-1662 | all new tests | Assertions are behavioral (returned values, resolved provenance, real paths, byte comparisons), not structural |

## Acceptance Criteria

1. `ruff check` and `ruff format --check` pass clean on every changed Python file (both are separate gates).
2. `python -m pytest platform_tests/scripts/test_implementation_authorization_harness_selector.py platform_tests/scripts/test_implementation_authorization_packet_paths.py platform_tests/scripts/test_implementation_authorization.py -q --tb=short` passes green.
3. The r3 reproduction case (declared Goose envelope + `CODEX_HOME` set, no bypass) resolves prime-builder provenance instead of raising "Worker role provenance session id does not match the current session."
4. `begin` success stdout contains the named packet path and active-pointer path; on-disk packet files remain byte-canonical with no new keys.
5. Same-bridge re-mint never destroys prior packet bytes: the history entry byte-equals the pre-existing named packet in every overwrite test.
6. The diff introduces zero new hard-coded timer, interval, retry, or throttle literals.
7. `scripts/gtkb_session_id.py` (including `BRIDGE_WORK_INTENT_ORDER`), `groundtruth_kb.session.envelope`, and all other `section_body`/selector-adjacent surfaces outside the three declared slices are unchanged.

## Risk And Rollback

- **Selector-narrowing risk.** A Codex session exposing `CODEX_HOME` but not `CODEX_THREAD_ID` would no longer infer `codex`; it falls to the declaration scan, which still resolves a single matching session document by session id, and fails closed on genuine ambiguity — the same fail-closed posture the resolver already implements. Residual behavior change is limited to sessions that were previously mis-served by installation-marker inference.
- **Stdout-shape risk.** The success-path wrapper changes `begin` stdout shape. Fresh repo search found no machine consumer outside the in-scope test module; error and `--no-write` shapes are unchanged; the shape question is put to Loyal Opposition explicitly below.
- **History-growth risk.** History entries accrue only on same-bridge re-mints with differing bytes — a rare recovery flow; entries live under `.gtkb-state/` as regenerable-evidence-class runtime state, eligible for future hygiene-reclaim policy, none in scope here.
- **Rollback** is the exact revert of the one source file and the test modules. History directories are inert evidence without the consuming code; no MemBase mutation, no dispatcher/TAFE state, and no bridge chain file is touched.

## Coordination Note — Sequencing Constraint (not scope)

`scripts/implementation_authorization.py` is targeted by two other live cycles: the WI-5694 cycle-1 thread (`gtkb-wi5694-terminal-evidence-packet-validator`, latest status `NO-GO` at `-004` by fresh first-line read — non-terminal, revision pending) and the GO'd WI-5823 thread (`gtkb-wi5823-impl-auth-spec-links-extractor-alignment`, latest status `GO` at `-002` by fresh first-line read — implementation pending). **WI-5830 implementation MUST be sequenced strictly AFTER both threads are terminal.** To keep eventual diffs disjoint, this proposal is function-scoped to `_worker_harness_selector`, `write_named_packet`, and the `begin` stdout emission; WI-5694 touches validate/list surfaces and WI-5823 touches the extractor/amendment surfaces. If the landed diffs have moved or renamed a touched function, the implementing session re-baselines line references before editing and notes the re-baseline in the implementation report.

## Coordination Note — WI-5815 Sibling (identity isolation)

WI-5815 (P0, same project; per-session envelope isolation and claim-CLI ambient hardening for non-Claude harnesses, TEST-11771) is being proposed concurrently. The two are complementary, not overlapping: WI-5815 governs envelope **creation** and claim-time identity for harness G; WI-5830 governs envelope **selection** at `begin` time plus packet audit surfaces. `groundtruth_kb.session.envelope` is deliberately NOT in this proposal's `target_paths`. If WI-5815's implementation lands changes to `resolve_worker_role_provenance` or the envelope path helpers first, the WI-5830 implementer re-verifies Slice A's `None`-branch assumption (harness-agnostic exact-session-document scan) against the landed code before editing, and records that re-verification in the implementation report.

## DISARM — KB Mechanics

This proposal creates and modifies source and test files only. No MemBase records, specifications, ADRs, DCLs, GOV records, work items, Deliberation Archive entries, or other KB-governed artifacts are created, updated, or retired by this work. The `kb_mutation_in_scope: false` flag accurately reflects a pure source-and-test change; citations of DELIB, spec, WI, and TEST IDs in this proposal are read-only references, not mutations.

## DISARM — Packet Mechanics

The implementation-start packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-wi5830-harness-selector-packet-hardening`, run only after an independent Loyal Opposition GO and after the sequencing constraint above is satisfied) is session-local implementation-scope evidence. It is not a formal artifact under GOV-ARTIFACT-APPROVAL-001 and requires no separate approval packet; it derives from TAFE/dispatcher bridge state, the approved proposal file, and the GO verdict file, expires, and fails closed on bridge status drift. The PAUTH triple cited in this proposal's header supplies the project-authorization evidence the packet validator consumes; it never broadens `target_paths` and never replaces the live latest-GO requirement, the fresh work-intent claim, or the packet itself.

## Recommended Commit Type

Recommended commit type: fix — repairs recorded defects (wrong-envelope selection from installation-marker leakage, undiscoverable packet paths, audit-destroying silent overwrite) with regression coverage; the history surface is remediation plumbing for the same defect class, not a new capability surface.

## Loyal Opposition Review Questions

1. Is the nested `{"packet": ..., "packet_paths": ...}` success-stdout wrapper the right compatibility posture, or should Loyal Opposition prefer a presentation-only hash-exempt key (rejected above for hash-semantics blast radius) or a stderr side channel?
2. Is removing only `CODEX_HOME` the right narrowing, or should `CLAUDECODE` (per-process, session-scoped in current evidence) also be reclassified as inference-ineligible in the same slice?
3. Is the per-bridge history directory (`<bridge-id>.history/<UTC-ts>-<sha8>.json`) preferable to a single append-only `<bridge-id>.history.jsonl`, given hygiene-reclaim and audit-read ergonomics?
4. Should `activate` disclose paths in the same wrapper shape now, or remain a follow-on as proposed?

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
