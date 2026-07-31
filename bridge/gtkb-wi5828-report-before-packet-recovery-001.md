NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code proposal-author worker dispatched under the DELIB-202667735 parallel-operation mandate; this filing is a Prime Builder proposal-authoring act (envelope pb); the parent interactive session's resolver fallback reports loyal-opposition; authoring-only scope - no implementation, commit, or review in this session

bridge_kind: prime_proposal
Document: gtkb-wi5828-report-before-packet-recovery
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5828

target_paths: ["scripts/implementation_authorization.py", "scripts/bridge_work_intent_registry.py", "scripts/bridge_claim_cli.py", "platform_tests/scripts/test_implementation_authorization_report_recovery.py", "platform_tests/scripts/test_implementation_authorization_pre_packet_cure.py"]
implementation_scope: report_before_packet_recovery_and_governed_pre_packet_cure
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5828 Implementation Proposal — Lawful Recovery From the Report-Before-Packet Dead End, and a Governed Pre-Packet Mutation Cure

## Summary

Two defects, one causal chain.

**Defect 1 — the dead end.** Once a Prime Builder files a post-GO implementation report, the thread's latest status becomes `NEW` (or `REVISED`), and three independent locks close simultaneously: the lifecycle resolver stops exposing the GO'd proposal/GO pair, `approved_files_for_go()` raises `found latest status NEW`, and a fresh work-intent claim can only be minted at kind `draft`. From that moment until a Loyal Opposition verdict lands, there is no lawful way to obtain an implementation-start packet for the thread — including for the express purpose of curing a defect the reviewer has not yet even reported. The only escape observed in practice during the `gtkb-wi5808-harness-probe-dsv4pro-r3` run was moving append-only numbered bridge files aside to `.md.hold` so the resolver would not see them (four or more times). That workaround hides canonical audit state from the resolver and is the single behavior this proposal must render permanently unnecessary.

**Defect 2 — the ungoverned cure ritual.** The `NO-GO` at `bridge/gtkb-wi5808-harness-probe-dsv4pro-r3-004.md` established the correct governance rule — a late packet does not retroactively authorize a pre-packet mutation window — and then prescribed the remedy as *"re-touch both target paths so mutations occur while the packet is loadable."* That prescription is a manual re-dating ritual with no artifact, no evidence, and no way for a later verifier to distinguish a legitimate cure from a substantive post-review edit. It also cannot be executed at all while Defect 1 holds, because it requires a live packet the dead end forbids.

This proposal delivers both halves: **(i)** an explicit, opt-in, fail-closed `begin` recovery mode for a self-authored post-GO report, modeled byte-for-byte on the existing `_report_no_go_resumption_authority` precedent; and **(ii)** a governed `cure-pre-packet-mutations` subcommand that performs the re-dating deterministically, refuses to alter a single content byte, and emits a durable audit record naming every path it re-dated. No file-move pattern is sanctioned anywhere in this design.

This proposal is filed as `bridge/gtkb-wi5828-report-before-packet-recovery-001.md`, continuing the append-only versioned bridge file chain. No prior version is deleted, moved, or rewritten; the status-bearing numbered files are the canonical audit trail under GOV-FILE-BRIDGE-AUTHORITY-001.

## Problem Statement And Live Evidence (fresh reads, 2026-07-31)

Every claim below was re-derived this session from the live worktree code of record, fresh `gt backlog show WI-5828 --json` / `gt tests show TEST-11784 --json` / `gt projects show-authorization` reads, and direct first-line status-token reads of the numbered bridge files. Line numbers are current-worktree references.

### The three locks

1. **Lock 1 — the resolver withholds implementation authority.** In `scripts/bridge_lifecycle_resolver.py`, `_ordinary_resolution()` sets `implementation_artifact` and `implementation_verdict` only when `latest_status == "GO"` or when the latest status is a resumable report-level `NO-GO` (lines 506-539). With chain `... GO → NEW(report)`, the latest status is `NEW`, so both fields resolve to `None`.
2. **Lock 2 — `approved_files_for_go()` refuses.** In `scripts/implementation_authorization.py`, the resolver-managed branch (lines 508-523) returns the pair only when both resolver fields are present; otherwise it raises `Implementation authorization requires a GO in the bridge chain; latest GO or resumable post-GO NO-GO is required; found latest status NEW`. That is the exact string recorded in the WI-5828 description. Note the diagnostic asymmetry: the legacy chain-walk branch below it (lines 536-541) emits the far more useful `Post-implementation report is awaiting Loyal Opposition review`, but resolver-managed threads — that is, all live threads — never reach it.
3. **Lock 3 — the claim cannot upgrade past draft.** In `scripts/bridge_work_intent_registry.py`, `_claim_values()` mints `CLAIM_KIND_GO_IMPLEMENTATION` only under the string equality `if _latest_status(slug, project_root=project_root) == "GO"` (line 862); every other chain state falls through to the `CLAIM_KIND_DRAFT` return (lines 885-905). A draft claim is then rejected downstream by `finalize_implementation_start_packet()` (lines 2194-2205), which admits only `CLAIM_KIND_GO_IMPLEMENTATION`, `CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP`, or a draft claim carrying report-level `NO-GO` resumption authority.

The three locks are independent, so relieving any one alone leaves the dead end intact. All three must be addressed together, which is why this proposal spans two source modules plus the claim CLI.

### The dead-end window is bounded and real

The window opens when the report is filed and closes when a Loyal Opposition verdict lands. In `gtkb-wi5808-harness-probe-dsv4pro-r3` the chain runs `NEW(-001) → GO(-002) → NEW(-003 report) → NO-GO(-004)`, verified this session by first-line reads of all four numbered files. Between `-003` and `-004` the thread was wedged: `begin` was unreachable, and the `.md.hold` file moves happened inside precisely that window. Once `-004` (a report-level `NO-GO`) landed, `latest_is_resumable_report_no_go` became true and `begin` worked again — which is why the wedge is easy to miss in postmortem: the evidence of the dead end disappears the moment the reviewer responds.

### The GO is not superseded by the report

This is the load-bearing correctness fact for Slice A, and it is asserted by the module's own docstring. `_post_go_chain_state()` (lines 355-377) states: *"A revised proposal always precedes its GO in the bridge lifecycle (proposals are revised, then GO'd), so any NEW/REVISED filed after a GO is a post-implementation report, never a superseding proposal."* The GO at `-002` therefore still authorizes exactly the proposal it approved and exactly the `target_paths` that proposal declared, regardless of whether a report has since been filed. Slice A does not confer authority the GO withheld; it restores access to authority the GO already conferred.

### The precedent for a narrow recovery already exists in the code

`_report_no_go_resumption_authority()` (lines 437-494) is the template: a fail-closed, provenance-carrying helper that lets a `draft` claim authorize implementation start in exactly one narrow chain state, verified against fresh numbered-file evidence (`Responds to:` matching, `bridge_kind` check, version-number resolution), and recorded as immutable `resumption_authority` provenance inside the finalized packet (lines 2254-2255, 2277-2278). Slice A is the sibling of that helper for the report-awaiting-review state. Similarly, `CLAIM_KIND_NO_ACTION_CORRECTION` (registry line 50, validator `_validate_no_action_correction_request`, CLI subcommand at `scripts/bridge_claim_cli.py` lines 266-287) is the working precedent for adding one explicit, validated claim kind without disturbing the default claim path.

### The cure prescription has no artifact today

The `-004` `NO-GO` compared filesystem write times against `implementation_start.finalized_at` (`2026-07-30T23:10:22Z`) and blocked `VERIFIED` on that basis. The consumer of that timestamp inside the module is `assess_packet_terminal_evidence()` (line 2645 parses `finalized_at`). Nothing in the repository performs, records, or attests a cure: a manual re-touch is byte-indistinguishable from a substantive post-review edit, so a reviewer who accepts one can never be sure which one occurred. That ambiguity is the governance defect, not the re-dating itself.

## Proposed Design

Four slices. Slices A, B, C together deliver half (i) — the recovery mode. Slice D delivers half (ii) — the governed cure.

### Slice A — Opt-in report-recovery authority in `approved_files_for_go()` (implementation_authorization.py)

New helper `_report_awaiting_review_recovery_authority(project_root, bridge_id, session_id)` — the sibling of `_report_no_go_resumption_authority()`, sharing its shape and its fail-closed discipline. It returns provenance only when **every** condition holds against fresh numbered-file reads:

1. The chain contains a GO, and the post-GO statuses classify as `awaiting_review` under the unmodified `_post_go_chain_state()`.
2. No newer GO exists after the pinned GO (the existing `_packet_go_integrity()` invariant, re-derived here rather than reused, to stay disjoint from the WI-5694 surface).
3. The topmost post-GO artifact parses as `bridge_kind: implementation_report` via the existing `proposal_bridge_kind()`.
4. **Self-authorship:** the report's `author_session_context_id` equals the session id requesting recovery. A report authored by a different session is *not* recoverable by this session — that thread belongs to its author and to the reviewer, and this is the clause that keeps recovery from becoming a cross-session implementation bypass.
5. The GO'd proposal resolves and its `target_paths` are extractable; recovery never widens the authorized path set by even one entry.

`approved_files_for_go()` gains an optional keyword-only parameter `recovery_authority: dict | None = None`. When it is `None` — which is every existing call site — behavior is byte-identical to today, including the resolver-managed `found latest status NEW` raise and the legacy-branch `awaiting Loyal Opposition review` raise. The existing suite in `platform_tests/scripts/test_implementation_authorization.py` is the regression lock for that identity and is deliberately **not** in this proposal's `target_paths`: if any assertion there needs to change, that is a defect in this design, not a licensed edit.

`begin` gains one additive flag, `--recover-report-before-packet`. Only that flag causes the recovery helper to run. The minted packet carries a `report_recovery_authority` block (report path and version, GO path and version, both author session ids, and the recovery timestamp) so the eventual implementation report and the Loyal Opposition verifier see the recovery explicitly and can audit it.

### Slice B — An explicit `report_recovery` claim kind (bridge_work_intent_registry.py)

New constant `CLAIM_KIND_REPORT_RECOVERY = "report_recovery"` plus validator `_validate_report_recovery_request(slug, project_root, acting_role, session_id)`, registered as an explicit-kind branch inside `_claim_values()` alongside the existing bootstrap and no-action-correction branches. The validator requires `acting_role == "prime-builder"` and re-runs the Slice A eligibility check from fresh numbered-file state, so a recovery claim cannot exist for a thread that is not actually wedged.

The implicit default paths are untouched: the `== "GO"` go-implementation branch (line 862) and the fall-through draft return (lines 885-905) keep their current semantics exactly. This is the whole least-privilege point of Slice B — nothing that is a draft claim today silently becomes an implementation claim tomorrow.

### Slice C — Accept the new kind at finalization (implementation_authorization.py) and expose it (bridge_claim_cli.py)

`finalize_implementation_start_packet()` adds `CLAIM_KIND_REPORT_RECOVERY` to its accepted claim-kind set (lines 2194-2205) **only when** the packet carries a matching `report_recovery_authority` block whose report path, GO path, and session id agree with the live claim record; a mismatch fails closed. `scripts/bridge_claim_cli.py` gains one thin subcommand `claim-report-recovery` and one handler `cmd_claim_report_recovery`, delegating to the existing `_cmd_claim_with_kind()` with the new kind. No existing handler, parser, or signature is modified.

### Slice D — `cure-pre-packet-mutations`: the governed replacement for the re-touch ritual

New subcommand:

```text
python scripts/implementation_authorization.py cure-pre-packet-mutations --bridge-id <slug> --path <p> [--path <p> ...] [--responds-to bridge/<slug>-NNN.md]
```

Fail-closed preconditions (ALL required):

1. A named implementation-start packet for the slug loads, validates under the existing `_validate_packet()` path, and is unexpired at the moment of the cure — the cure cannot manufacture the authorization it depends on.
2. The resolved work-intent claim is held by the acting session and is of an implementation-bearing kind (`go_implementation`, `project_authorization_bootstrap`, or the Slice B `report_recovery`).
3. Every `--path` is authorized by the packet's `target_path_globs` via the existing `path_authorized()`. An unauthorized path aborts the whole invocation; the cure is all-or-nothing.
4. Every `--path` exists and is a regular file. No path may be under `bridge/`: the cure never touches the numbered chain.
5. **Content invariance is enforced, not promised.** The sha256 of each file is captured before and after; the helper only updates modification time (no content write), and a post-condition assertion re-hashes and aborts on any difference.

Effect: each path's modification time is set to the cure timestamp, which falls strictly inside the live packet window, and a durable record is written to `.gtkb-state/impl-auth-cures/<bridge-id>/<UTC-timestamp>-<sha8>.json` containing: the packet hash, the packet's `finalized_at` and `expires_at`, the acting session id, the work-intent claim fields, the optional `--responds-to` verdict path that prescribed the cure, and per path the relative path, the invariant sha256, the prior modification time, and the new modification time.

The record is the point. After a cure, the implementation report cites the record; the verifier's existing modification-time-versus-`finalized_at` comparison — the exact check that produced the `-004` `NO-GO` — passes *with an explicit statement of why*, instead of passing because someone silently re-touched a file. The helper makes re-dating visible, auditable, and attributable; it does not make pre-packet mutation acceptable, and it deliberately cannot alter what was written.

Nothing under `bridge/` is written, moved, renamed, or removed by any slice in this proposal.

### Which arm of half (i) is least-privilege: recovery mode, and why

WI-5828 offers an alternative arm — a write-time gate that refuses to file an implementation report when no live packet exists. It is superficially the more conservative choice, because a refusal grants no new authority while a recovery mode opens a new state in which packets can be minted. Read against the code, the conclusion inverts on four grounds:

1. **The recovery mode grants no new authority.** Per `_post_go_chain_state()`'s own docstring (quoted above), a post-GO `NEW` is a report, never a superseding proposal. The GO's authorization over its proposal and its `target_paths` is unchanged by the report's existence. Slice A restores access to an authority that already exists and narrows it further with a self-authorship clause the current code does not even have. The write-time gate, by contrast, changes what is *provable* about mutation ordering only for the harness surfaces it actually intercepts.
2. **The write-time gate cannot be enforced uniformly across harnesses.** `propose_bridge_codex_non_bypass()` exists precisely because `apply_patch` on the Codex surface is not covered by the bridge-compliance PreToolUse hook, and DCL-CROSS-HARNESS-ENFORCEMENT-001 governs that asymmetry. A gate that binds one harness and not another produces the worst outcome: the disciplined harness is blocked from recording what happened while the uncovered harness proceeds unrecorded.
3. **Its failure mode points at the anti-pattern.** Under GOV-FILE-BRIDGE-AUTHORITY-001 the numbered chain is the canonical audit trail. A gate whose refusal message is effectively *"do not file that report"* pressures the actor toward not recording, filing out of band, or moving files aside — the `.md.hold` class of behavior this work exists to eliminate.
4. **It cures nothing already wedged.** Threads that reach the dead-end state before the gate ships stay wedged forever, and the gate offers no exit. The recovery mode is the only arm that de-wedges an existing chain without touching a bridge file.

The gate arm is therefore rejected **for this scope**, not dismissed: as a purely advisory, non-blocking warning at report-filing time it would have real diagnostic value. Its implementation surface (`.claude/hooks/bridge-compliance-gate.py`, `.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py`, and their template twins) is currently claimed by the non-terminal `gtkb-work-intent-registry-prime-write-integration` thread, so scoping it here would create a fourth serialization conflict for a secondary benefit. It is named below as a follow-on candidate rather than smuggled into this proposal's `target_paths`.

### Rejected alternatives

- **Moving numbered bridge files aside (`.md.hold`) to unwedge the resolver.** Hides canonical append-only state from every consumer, breaks GOV-FILE-BRIDGE-AUTHORITY-001, and produces a chain whose recorded history differs from the history the actor operated under. Rejected outright and by construction: after Slice A there is no state in which it is the only exit.
- **Implicitly treating `awaiting_review` as resumable inside `_post_go_chain_state()`.** A one-line change that would silently grant implementation authority in every awaiting-review thread, for every session, with no self-authorship check and no packet-visible provenance. Maximum blast radius for the same user-visible outcome. Rejected.
- **Widening the `_claim_values()` go-implementation branch to accept post-GO report states.** Same objection at the claim layer: it converts draft claims into implementation claims implicitly, across all threads, including threads mid-review by another session. Rejected in favor of the explicit Slice B kind.
- **Letting the cure helper edit file content while re-dating.** Would make the helper a laundering device for post-review substantive edits. Rejected; content invariance is asserted by pre/post hashing and the invocation aborts on any difference.
- **Curing by re-writing identical bytes rather than updating modification time.** Equivalent in effect, strictly worse in risk (a partial write can corrupt a file the packet authorized but the cure was never meant to change). Rejected.
- **A blanket owner waiver for pre-packet mutation windows.** Would retire the `-004` governance finding rather than serve it. Rejected; the finding is correct and this proposal is built to satisfy it.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — required (blocking) — the WI-5828 source specification; operation-time authorization bounds are exactly what the dead end makes unobtainable and what the cure helper restores evidence for.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — required (blocking) — append-only numbered bridge file chain authority; every slice is designed to leave the chain untouched, and eliminating the file-move workaround is this proposal's primary service to it.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — required (blocking) — governs the project-scoped authorization chain whose begin path Slices A through C extend; the PAUTH triple in the header proceeds under it.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — required (blocking) — this proposal's own linkage obligation; the recovery path preserves the GO'd proposal as the sole source of authorized paths and links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — required (blocking) — governs downstream verification; the Specification-to-Test Mapping below is the derivation record the Loyal Opposition verifier executes against.
- `GOV-ARTIFACT-APPROVAL-001` — required (blocking) — no formal MemBase artifact is created, updated, or retired by this implementation, so no per-artifact approval evidence is required beyond the bridge and PAUTH chain.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — required (blocking) — root-boundary containment: every target path is in-root under the mandatory GT-KB project root, and the cure record directory is in-root runtime evidence; no application subtree and no out-of-root dependency is touched.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory — the recovery and cure paths are mechanical, fail-closed gates rather than procedural guidance, and the write-time-gate arm was assessed against this specification's two-layer model.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — advisory — the decisive argument against the write-time-gate arm is its uneven coverage across harness submission surfaces; the chosen arm lives in shared CLI code that every harness invokes identically.
- `GOV-10` — advisory — the regression tests exercise exposed production interfaces (the helper functions, the CLI subcommands, and the packet payload) rather than private state.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — advisory — every eligibility check re-derives state from fresh numbered-file and packet reads at the moment of use; no cached chain state is trusted.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory — Slice D converts a manual, undocumented ritual prescribed in prose into a deterministic service that emits its own evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory — the cure record and the packet recovery block are durable artifacts rather than transient session context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory — traceability: the recovery block and cure record tie proposal, GO, report, cure, and verification into one auditable graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory — defect-origin lifecycle transitions for WI-5828 follow the recorded trigger classifications.
- `GOV-STANDING-BACKLOG-001` — advisory — WI-5828 is the sole work authority for this proposal; no parallel authority is created.
- `SPEC-1662` — advisory — assertion quality: the tests below assert behavioral outcomes such as accept and reject classifications, packet payload fields, and byte-level file invariance, not structural presence.
- `SPEC-1830` — advisory — operational procedures must be code: the prose cure prescription recorded in the dsv4pro-r3 verdict becomes an executable subcommand.
- Deliberations cited: `DELIB-202667735`, `DELIB-202667731`, `DELIB-202667730`, `DELIB-202667726`, `DELIB-202667723`.

## Prior Deliberations

All records below were verified this session by exact-id lookup against the live knowledge database; no citation is inferred from memory or from a summary.

- **DELIB-202667735** — Delegated proposal authoring and unblock-implementation mandate with the parallel-operation program: the owner mandate under which this proposal-author worker files this NEW entry.
- **DELIB-202667731** — Harness Test Corrections whole-project authorization decision: the list-free grant recorded as PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730 under which this proposal is filed.
- **DELIB-202667730** — Harness Test final synthesis: the consolidated evaluation evidence, including the dsv4pro-r3 run in which the report-before-packet dead end was hit and the append-only file-move workaround was used.
- **DELIB-202667726** — Program pause plus Harness Test program directive: the originating owner mandate for the program whose evaluation runs produced this defect record.
- **DELIB-202667723** — Terminal-evidence-sufficient decision for expired implementation-start packets: the nearest prior reasoning about packet-window semantics and what an expired packet does and does not prove. Slice D is deliberately aligned with it — the cure requires a live packet window and never claims authority from an expired one.
- **Bridge precedent, `bridge/gtkb-wi5808-harness-probe-dsv4pro-r3-004.md`** — the Loyal Opposition `NO-GO` establishing that a late packet does not retroactively authorize a pre-packet mutation window, and prescribing the re-touch remedy that Slice D replaces with a governed helper. Verified this session by direct read of the numbered file; chain first-line status tokens confirmed as `NEW`, `GO`, `NEW`, `NO-GO` across `-001` through `-004`.

## Owner Decisions / Input

1. **DELIB-202667735** — the owner's delegated proposal-authoring and unblock-implementation mandate for the parallel-operation program authorizes this worker to file this NEW proposal for WI-5828. Authoring-only: this filing performs no implementation, no commit, and no review.
2. **DELIB-202667731 / AUQ-20260730-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-GRANT** — the owner's list-free whole-project grant (PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730) covers WI-5828 as a member work item. Per that authorization's recorded scope, this work item still requires its own full governed cycle: this proposal, independent Loyal Opposition GO carrying complete Clause Applicability evidence, a fresh work-intent claim, an implementation-start packet, exact target-path enforcement, an implementation report, and independent VERIFIED through governed atomic finalization.
3. No additional owner decision is required to review this proposal, and this proposal does not itself authorize implementation.

## Requirement Sufficiency

**Existing requirements sufficient.** The WI-5828 defect description (fresh-read verified), TEST-11784's recorded expected outcome, DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001, GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, GOV-FILE-BRIDGE-AUTHORITY-001, and the `-004` `NO-GO` finding together fully constrain this implementation. No new or revised specification is required before implementation.

## Specification-Derived Verification Plan (Spec-to-Test Mapping)

MemBase test record `TEST-11784` ("Begin succeeds or fails lawfully when a self-authored report tops a GO chain") is the spec-derived anchor created with WI-5828 under GOV-12. Its recorded expected outcome has three conjuncts, and the mapping below is organized to discharge each one explicitly:

- **Conjunct 1** — with chain `GO → NEW(report)`, `begin` succeeds under the documented recovery mode;
- **Conjunct 2** — or the report filing is blocked upfront when no live packet exists;
- **Conjunct 3** — the pre-packet cure path is a governed helper with audit evidence, not manual file moves.

Conjunct 1 is the arm this proposal implements; Conjunct 2 is discharged by the recorded rejection rationale above plus an explicit test asserting that filing remains unblocked and that recovery is the sanctioned path; Conjunct 3 is discharged by Slice D and its evidence assertions.

New tests land in `platform_tests/scripts/test_implementation_authorization_report_recovery.py` and `platform_tests/scripts/test_implementation_authorization_pre_packet_cure.py`. Existing modules are regression locks and are not modified.

| Requirement source | Test | Behavior asserted |
|---|---|---|
| TEST-11784 conjunct 1 / DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001 | `test_recovery_mode_mints_packet_for_self_authored_report` | Tmp fixture chain `NEW → GO → NEW(report)` authored by the acting session: `begin` without the flag fails as today; `begin --recover-report-before-packet` with a `report_recovery` claim mints a packet whose `target_path_globs` equal the GO'd proposal's declared set exactly |
| TEST-11784 conjunct 1 / GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | `test_recovery_packet_carries_provenance` | The minted packet contains a `report_recovery_authority` block naming report path and version, GO path and version, both author session ids, and the recovery timestamp; the packet hash validates over the whole payload |
| WI-5828 (self-authorship narrowing) | `test_recovery_rejects_foreign_authored_report` | A post-GO report whose `author_session_context_id` differs from the acting session fails closed even with the flag and a claim present |
| WI-5828 (fail-closed matrix) | `test_recovery_rejects_non_report_artifact`, `test_recovery_rejects_newer_go`, `test_recovery_rejects_terminal_verified`, `test_recovery_rejects_deferred`, `test_recovery_rejects_no_action`, `test_recovery_rejects_missing_author_metadata` | Each disqualifying chain or metadata state fails closed with a distinct message; missing or unreadable author metadata never resolves to eligible |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 (default-path identity) | `test_default_begin_behavior_unchanged` | Without the flag, `approved_files_for_go()` raises the same message for the same chains as before the change, for both resolver-managed and legacy-branch fixtures |
| GOV-10 / SPEC-1662 (claim layer) | `test_report_recovery_claim_kind_requires_wedged_chain`, `test_report_recovery_claim_requires_prime_builder_role` | The Slice B validator refuses a recovery claim on a thread that is not in the wedged state, and refuses a non-Prime-Builder acting role; the implicit draft and go-implementation branches keep their current outcomes for unchanged inputs |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 (finalization) | `test_finalize_rejects_recovery_claim_without_matching_authority` | A `report_recovery` claim whose thread, report path, or session id disagrees with the packet's recovery block fails closed at finalization |
| TEST-11784 conjunct 3 / DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001 | `test_cure_redates_authorized_paths_under_live_packet` | With a live packet, `cure-pre-packet-mutations` moves each authorized path's modification time to fall inside the packet window, and the packet-window comparison that produced the `-004` finding then passes for those paths |
| TEST-11784 conjunct 3 / GOV-FILE-BRIDGE-AUTHORITY-001 | `test_cure_writes_audit_record_and_touches_no_bridge_file` | The cure record exists under the cure evidence directory and names every re-dated path with its invariant hash and prior/new modification times; every file under the fixture's `bridge/` directory is byte-identical and modification-time-identical before and after |
| WI-5828 (content invariance) | `test_cure_preserves_content_bytes` | Every cured file's sha256 is identical before and after; a fixture in which content would change aborts the invocation and leaves all paths untouched |
| WI-5828 (cure fail-closed matrix) | `test_cure_rejects_expired_packet`, `test_cure_rejects_unauthorized_path`, `test_cure_rejects_bridge_path`, `test_cure_rejects_missing_claim`, `test_cure_is_all_or_nothing` | Expired packet, path outside `target_path_globs`, any path under `bridge/`, absent or foreign claim, and any single rejected path each abort the whole invocation with nothing re-dated |
| TEST-11784 conjunct 2 / DCL-CROSS-HARNESS-ENFORCEMENT-001 | `test_report_filing_remains_unblocked_and_recovery_is_the_sanctioned_path` | Filing a post-GO report is not blocked by this change (the write-time-gate arm is not implemented), and the recovery path is reachable immediately afterward — the recorded discharge of conjunct 2's alternative arm |

## Acceptance Criteria

1. `ruff check` and `ruff format --check` pass clean on every changed Python file; these are separate gates and both are run before the implementation report is filed.
2. `python -m pytest platform_tests/scripts/test_implementation_authorization_report_recovery.py platform_tests/scripts/test_implementation_authorization_pre_packet_cure.py -q --tb=short` passes green.
3. Regression locks pass green **without modification**: `platform_tests/scripts/test_implementation_authorization.py`, `platform_tests/scripts/test_bridge_work_intent_registry.py`, `platform_tests/scripts/test_bridge_claim_cli.py`, `platform_tests/scripts/test_work_intent_role_eligibility.py`, and `platform_tests/scripts/test_implementation_authorization_terminal_evidence.py`. Any required edit to these modules invalidates the disjointness claim in the Sequencing section and must be surfaced rather than absorbed.
4. Default-path identity: with no `--recover-report-before-packet` flag, `begin` output and error strings are unchanged for every existing fixture.
5. No slice writes, moves, renames, or removes any file under `bridge/`; the cure test asserts this at byte and modification-time level.
6. The diff introduces zero new hard-coded timer, interval, retry, or throttle literals; all window and lifetime values continue to come from existing configured constants.
7. Every new rejection path emits a distinct, actionable message that names the missing condition and the sanctioned next step.
8. The resolver-managed diagnostic in `approved_files_for_go()` names the recovery path when the chain is in the wedged state, so the dead end is self-documenting at the moment it is hit.

## Risk And Rollback

- **Authority-widening risk.** Mitigated by opt-in flag, an explicit claim kind, self-authorship matching, unchanged `target_paths` derivation, packet-visible provenance, finalization cross-check, and a full fail-closed rejection matrix. The default path is byte-identical to today and is regression-locked by an unmodified existing suite.
- **Cure-abuse risk.** Mitigated by live-packet requirement, implementation-bearing claim requirement, path-authorization check, `bridge/` exclusion, all-or-nothing semantics, and pre/post hash invariance enforced as a post-condition. The helper cannot alter content, cannot reach unauthorized paths, and cannot run without the authorization it is meant to evidence.
- **Reviewer-trust risk.** A governed cure could be mistaken for a licence to mutate before authorization. Mitigated by making the cure record mandatory reading for verification: the record states that a cure occurred and which paths it re-dated, so a verifier sees strictly more than they see today, when the same re-dating leaves no trace at all.
- **Concurrent-modification risk.** `scripts/implementation_authorization.py` is contested by three other threads; see the Sequencing section. This is a live instance of the serialization problem the corrections program exists to address, and it is stated rather than minimized.
- **Rollback** is the exact revert of the three source files and deletion of the two new test modules. Cure records and recovery blocks under `.gtkb-state/` are inert runtime evidence without the consuming code; no MemBase record, no dispatcher state, and no bridge chain file is touched by any slice.

## Sequencing And Coordination (constraint, not scope)

`scripts/implementation_authorization.py` is currently the single most contested file in the program. Verified this session by first-line status reads and `target_paths` reads of the numbered files:

| Thread | Latest status | Declared surface in the shared file |
|---|---|---|
| `gtkb-wi5694-terminal-evidence-packet-validator` | `REVISED` (non-terminal) | `assess_packet_terminal_evidence()`, `list_named_packets()`, `list_named_packets_compact()`, `_packet_go_integrity()`, `_validate_packet()` |
| `gtkb-wi5823-impl-auth-spec-links-extractor-alignment` | `GO` | `extract_spec_links()`, a new level-aware section-body helper, a new `amend-proposal` subcommand, and a narrow extraction-failure consult inside `begin` |
| `gtkb-wi5830-harness-selector-packet-hardening` | `GO` | `_worker_harness_selector()`, `write_named_packet()`, and the `begin` stdout emission shape |
| **WI-5828 (this proposal)** | — | `approved_files_for_go()`, new `_report_awaiting_review_recovery_authority()`, the claim-kind acceptance set inside `finalize_implementation_start_packet()`, and a new `cure-pre-packet-mutations` subcommand |

**Sequencing requirement.** WI-5828 implementation MUST be sequenced after those three threads reach terminal state. This proposal is filed now so the design is reviewable in parallel; its implementation-start packet must not be minted until the contested threads have landed.

**Declared disjointness.** The function surfaces above do not intersect. WI-5828 does not touch `extract_spec_links()`, any section-body helper, `_worker_harness_selector()`, `write_named_packet()`, `_packet_go_integrity()`, `_validate_packet()`, `assess_packet_terminal_evidence()`, or either list surface. WI-5828 does not modify `_post_go_chain_state()`, `_report_no_go_resumption_authority()`, or `create_authorization_packet()`.

**The one genuinely shared region** is the subparser registration block inside `main()`, which WI-5823 (`amend-proposal`), WI-5830 (`begin` output), and this proposal (`cure-pre-packet-mutations`, plus the additive `--recover-report-before-packet` flag on `begin`) all extend. All three extensions are additive registrations rather than edits to existing arguments, so they compose; but the implementing session MUST re-baseline every line reference in this proposal against the landed state of the shared file before editing, and MUST record the re-baseline in the implementation report. In `scripts/bridge_claim_cli.py` the analogous shared region is the subcommand block, contested by the non-terminal `gtkb-work-intent-registry-prime-write-integration` thread; the same re-baseline discipline applies, and the same additive-only constraint holds.

**Honest note.** Four threads queued behind one file, each waiting on the others, is exactly the serialization cost this corrections program was chartered to reduce — and this proposal both suffers from it and adds to it. The disjointness declaration above is a mitigation, not a solution. Whether the shared file should be decomposed so that authorization-state resolution, packet lifecycle, extraction, and CLI surfaces can evolve independently is a real architectural question that this proposal deliberately does not answer, and that is raised as review question 4 below.

## Follow-On Candidates (not in scope, not authorized here)

- An advisory, non-blocking warning at report-filing time when no live packet exists for the slug — the write-time-gate arm reduced to diagnostics. Blocked today by contested hook surfaces and by uneven cross-harness coverage under DCL-CROSS-HARNESS-ENFORCEMENT-001.
- Decomposition of `scripts/implementation_authorization.py` along the four surfaces enumerated in the Sequencing table, to remove the serialization bottleneck at its source.

## DISARM — KB Mechanics

This work performs no MemBase mutation. This implementation creates and modifies source and test files only, and it requires no KB write of any kind. No specification, ADR, DCL, GOV record, work item, test record, or Deliberation Archive entry is created, revised, superseded, or retired by this work. The `kb_mutation_in_scope: false` flag accurately reflects a pure source-and-test change. Every specification, deliberation, work-item, and test identifier cited in this proposal is a read-only reference verified by exact-id lookup.

## DISARM — Packet Mechanics

The implementation-start packet minted by `begin` for this slug is session-local implementation-scope evidence. It is not a formal artifact under GOV-ARTIFACT-APPROVAL-001, and no separate approval packet is written, inserted, or otherwise created for it; it derives from live bridge state, the approved proposal file, and the GO verdict file, it expires, and it fails closed on bridge status drift. The PAUTH triple cited in this proposal's header supplies the project-authorization evidence the packet validator consumes; it never broadens `target_paths` and never replaces the live latest-GO requirement, the fresh work-intent claim, or the packet itself. The cure record introduced by Slice D is runtime audit evidence written under the state directory; it authorizes nothing on its own and is likewise not an approval artifact.

## Recommended Commit Type

Recommended commit type: fix — this repairs a defect class (an unrecoverable authorization dead end plus an ungoverned manual remedy) and replaces an ad-hoc ritual with governed, tested behavior. The new subcommand and claim kind are remediation plumbing for that defect, not a new product capability.

## Loyal Opposition Review Questions

1. Is the self-authorship clause (recovery available only to the session that authored the post-GO report) the right narrowing, or should recovery instead be gated on the work-intent claim holder, allowing a legitimate successor session after a compaction or handoff to recover a thread it did not author?
2. Should the `report_recovery` claim kind carry a shorter lifetime than an ordinary implementation claim, given that its chain state is by definition mid-review — and if so, should that lifetime derive from an existing configured constant rather than a new one?
3. Is a cure record under the state directory sufficient evidence, or should a cure be required to appear as an explicit named section in the subsequent implementation report before a verifier may accept a re-dated path?
4. Given four threads serialized behind `scripts/implementation_authorization.py`, should decomposition of that module be raised as its own work item now, or does the additive-only discipline declared above make the queue tolerable for this program's remaining scope?

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
