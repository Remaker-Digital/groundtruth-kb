NEW
::init gtkb pb
::open build
bridge_kind: prime_proposal
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code headless proposal-author worker; parallel-operation program per DELIB-202667523; resolved role prime-builder for this filing

# Implementation Proposal - Terminal-Evidence-Sufficient Packet Validation in the Packet Validator (WI-5694, Cycle 1 of 3)

Document: gtkb-wi5694-terminal-evidence-packet-validator
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-07-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5694

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization_terminal_evidence.py"]

Scope confirmation: this proposal performs no MemBase mutation and no groundtruth.db write during filing; it mints no implementation-start packet and confers no mutation authority; filing it authorizes nothing. This proposal performs no approval-evidence work; it requires no approval packets. All proposed changes are confined to the two `target_paths` files inside `E:\GT-KB`.

---

## Problem

Owner authority-model decision `DELIB-202667723` (AUQ evidence `AUQ-20260730-PACKET-EXPIRY-AUTHORITY-MODEL`, 2026-07-30) established TERMINAL-EVIDENCE-SUFFICIENT packet validation: an EXPIRED implementation-start authorization packet remains valid EVIDENCE that implementation authority existed, provided (a) the packet was live when the implementation mutations occurred and (b) no competing work-intent claim contests the thread. The packet TTL retains ONLY its active-authority-bounding function (the WI-4532 invariant is unchanged). The decision retroactively cures the measured 514/515 expired-packet population (99.8%, census 2026-07-30); packets already expired at implementation time stay invalid; contested packets stay invalid.

The current validator cannot express that distinction. In `scripts/implementation_authorization.py` (verified at HEAD):

- `_validate_packet` (lines 2499-2567) hard-rejects any packet whose `expires_at` has passed ("Implementation authorization packet has expired", lines 2507-2508). The same clause serves both active mutation gating AND evidence consultation - there is no evidence-classification path at all.
- `_validate_packet` is the sole validity predicate for `load_packet` (line 2570), `load_named_packet` (line 2584), `activate_packet` (line 2603), and `list_named_packets` (line 2616). Every consumer therefore sees an expired packet as unconditionally invalid.
- `list_named_packets` rows report `valid=False` with the expiry error for the entire cured population, and `list_named_packets_compact` (line 2664) then OMITS those rows from its `packets` payload entirely (`invalid_packets_omitted`), so downstream evidence consumers cannot even see that a durable implementation-start packet exists for a thread.
- `validate_targets` (line 2792, the CLI `validate` subcommand) resolves packets exclusively through the same predicate; this is CORRECT for mutation gating (TTL bounds active authority per WI-4532) and must stay unchanged.

Consequence (the WI-5694 P0 defect class): a legitimate independent Loyal Opposition VERIFIED finalization is blocked when the Prime implementation-start packet expires during the review window even though the reviewed implementation and its controlling GO remain exact. Three completed fix-band implementations (wi5757, wi5760, wi5784) were unverifiable for exactly this reason per `DELIB-202667723`.

## Cycle Scoping (mandated by WI-5694 status_detail)

WI-5694's status_detail and `DELIB-202667723` § Implementation scope mandate that the three enforcement surfaces each land through their OWN bridge cycle. This proposal is CYCLE 1 of 3 and covers ONLY the packet validator (`scripts/implementation_authorization.py`, the validate and list paths) plus the four-case regression suite. Explicitly OUT OF SCOPE for this cycle, each landing in its own later bridge cycle with its own proposal, independent GO, and verification:

1. Verification-workflow packet consultation (the workflow surfaces that consult packet state at verification time) - LATER CYCLE 2.
2. Protected-commit/finalization expiry checks that currently fail closed on expiry - LATER CYCLE 3.

`target_paths` deliberately excludes every cycle-2/cycle-3 surface. This cycle makes the validator and list surfaces CLASSIFY terminal evidence correctly; it does not by itself unblock verification flows (that is cycle 2 consuming this cycle's API).

## Proposed Changes

All changes are confined to the two `target_paths` files. The evidence assessment added here is read-only: it confers no mutation authority, mints no packet, performs no MemBase mutation and no groundtruth.db write, and never modifies packet files or bridge artifacts.

### Change 1 - Refactor `_validate_packet` into shared integrity clauses plus an unchanged active-authority path

Extract the integrity clauses of `_validate_packet` (hash check; pinned `go_file` present in the versioned chain with status still `GO`; no newer superseding `GO`) into an internal helper consumed by two callers:

- The existing active-authority path (`_validate_packet` public behavior) stays byte-identical: expiry hard-reject retained, `awaiting_review`/`terminal`/`deferred`/`no_action` chain-state rejections retained, PAUTH operation-time check retained. `load_packet`, `load_named_packet`, `activate_packet`, `validate_targets`, and the CLI `validate` subcommand keep today's exact semantics - TTL keeps bounding ACTIVE mutation authority per the WI-4532 invariant.
- A new terminal-evidence assessment path (Change 2) reuses the same integrity clauses so the two paths cannot drift.

### Change 2 - New public evidence API: `assess_packet_terminal_evidence(project_root, bridge_id) -> dict`

Loads the by-bridge named packet and classifies it as historical evidence per `DELIB-202667723`. Returned payload: `bridge_id`, `evidence_valid`, `expired`, `live_at_implementation`, `contested`, `chain_state`, `active_valid` (the unchanged `_validate_packet` outcome as a boolean), and `reasons` (populated on rejection). Evidence-validity clauses, ALL required:

- E1 hash integrity: `packet_hash(packet) == packet["packet_hash"]` (unchanged clause).
- E2 live-at-implementation: the packet is a durably finalized schema-v3 implementation-start packet (`implementation_start` block present per `finalize_implementation_start_packet`, lines 2123-2239) whose `implementation_start.finalized_at` parses and satisfies `finalized_at <= expires_at`. Rationale: every protected mutation routes through the implementation-start gate, which requires a LIVE packet at each mutation, so gate-passed mutations are bounded within the live window by construction; a durable in-window start is the strongest deterministic evidence available that the packet was live when the implementation mutations occurred. A packet with no `implementation_start` block (never durably started) or with `finalized_at > expires_at` is REJECTED - the expired-before-implementation case that `DELIB-202667723` keeps invalid.
- E3 pinned-GO integrity: the packet's `go_file` is still present in the thread chain with status `GO`, and no newer `GO` supersedes it (same clauses as today's validator).
- E4 chain-state handling: `awaiting_review` and `terminal` (VERIFIED) chain states are the expected habitat of evidence consultation and are reported in `chain_state` WITHOUT rejection - those two rejections in the active path are resume-mutation guards, inapplicable here because the evidence assessment confers no mutation authority. `deferred` and `no_action` chain states fail closed (`evidence_valid=False`) pending owner/reviewer resolution.
- E5 uncontested: `bridge_work_intent_registry.current_holder(bridge_id)` returns either no active holder or a holder whose `session_id` equals the packet's `implementation_start.session_id`. An active holder from a DIFFERENT session marks the thread contested and REJECTS (the contested case `DELIB-202667723` keeps invalid). A registry read error fails closed with a recorded reason - evidence validity is a positive claim, and unreadable contest state must not default to valid.

The assessment does NOT re-run the PAUTH operation-time evaluation against live authorization state: the packet's embedded `implementation_start.project_authorization_decision` is the recorded operation-time decision made when authority was actually exercised (enforcement already ran at every operation gate per `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`), and re-evaluating a historical grant at assessment time would wrongly reject evidence after routine PAUTH supersession (for example, the batch grants superseded by the list-free grant `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`). Flagged as review question Q2.

### Change 3 - List surfaces carry evidence classification

- `list_named_packets` rows gain three additive fields: `evidence_valid: bool`, `evidence_error: str | None`, and `expired: bool`. The existing `valid` field keeps its exact current meaning (active mutation authority) and its exact current computation.
- `list_named_packets_compact` gains an `evidence_valid_count` summary field, and its `packets` payload additionally includes rows that are evidence-valid but not active-valid, marked `"evidence_only": true`. No currently emitted row is removed and no existing field is renamed, so existing consumers filtering on `valid` see byte-compatible behavior for the rows they already receive.
- The CLI `list` and `list --compact` outputs carry the new fields automatically through the existing JSON serialization; no new subcommand and no new flags are added in this cycle.

Interpretation note: WI-5694 status_detail names "implementation_authorization.py validate/list" as this cycle's surface. The "validate" amendment is the shared-validator refactor plus the evidence mode it enables; the `validate` subcommand's mutation-gating semantics are deliberately byte-identical, because `DELIB-202667723` explicitly retains TTL's active-authority-bounding function.

### Timer discipline (one-line coordination note)

This proposal introduces no new hard-coded timer values, does not alter `DEFAULT_EXPIRY_MINUTES`, and only reads the existing `expires_at`/`finalized_at` stamps; the coupled externalization of the packet-TTL + claim-max-hold pair proceeds separately as WI-5806 under `DELIB-202667722` (timers are first-class; relaxed-first bias).

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - WI-5694's source spec; project-authorization bounds are enforced at every operation gate. The evidence assessment relies on that operation-time enforcement having run when authority was exercised, and changes no operation gate.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project-scoped implementation authorization; this work proceeds under the cited active list-free PAUTH plus this proposal's bridge `GO`. PAUTH metadata does not broaden `target_paths` and does not replace the live latest-`GO` requirement.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does not bypass bridge controls; the evidence rule validates history and never resurrects mutation authority.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the PAUTH envelope fields consumed by the validator remain explicit and append-only; this cycle reads them, never writes them.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the append-only versioned bridge chain is the audit substrate the evidence clauses (E3, E4) read; the validator remains read-only over `bridge/`.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - the terminal-evidence rule is delivered as mechanical validator behavior with regression tests, not as prose guidance.
- `GOV-17` - automation script modification approval gate: `scripts/implementation_authorization.py` is a governed automation script; modification authority is this proposal's `GO` under the cited PAUTH.
- `GOV-12` - work item creation triggers test creation; the four-case regression suite is WI-5694's derived test surface for this cycle.
- `GOV-10` - the regression tests exercise the exposed production interfaces (`assess_packet_terminal_evidence`, `_validate_packet` consumers, `list_named_packets`, `list_named_packets_compact`, and the CLI `list`/`validate` paths) through the existing module-load harness.
- `SPEC-1662` (GOV-18) - assertion quality: tests assert behavioral outcomes (accept/reject classifications, field values), not structure.
- `SPEC-1830` - operational procedures must be code: evidence classification becomes validator code, not a conversational review procedure.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - the assessment is a deterministic, read-only service function with stable outputs for fixed inputs.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section satisfies the mandatory proposal spec-linkage constraint; the verification plan maps each link to derived tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the eventual `VERIFIED` is conditional on creation and execution of the spec-derived tests T1-T4; the implementation report will carry the executed commands and observed results.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner decision, its AUQ evidence, and this cycle's classification behavior are preserved as durable artifacts (deliberation, bridge chain, validator code, tests), not transient chat state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - project memory is a durable artifact graph; the evidence assessment reconnects expired-packet history to the verification graph instead of dropping it.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the evidence payload exposes explicit classification states (`evidence_valid`, `contested`, `chain_state`) rather than collapsing lifecycle distinctions into a single invalid flag.

Tests derive from these links as mapped in the verification plan below.

## Prior Deliberations

- `DELIB-202667723` - the controlling owner decision: terminal-evidence-sufficient packet validation; four required regression cases; per-surface bridge cycles; WI-4532 invariant unchanged.
- `DELIB-202667722` - timer-governance first-class directive: relaxed-first bias, no new hard-coded timer values; TTL externalization proceeds separately (WI-5806 first pair).
- `DELIB-202667724` - owner authorization of the list-free whole-project PAUTH under which this cycle proceeds (P0 cohort including WI-5694).
- `DELIB-202667533` - AT-01 commit-first finalization ordering; untouched by this cycle and explicitly preserved by `DELIB-202667723`.
- `DELIB-202667532` - program north-star simplification bias cited by the owner decision's rationale (removing a timer from the evidence path entirely).
- `DELIB-202667523` - integrated parallel-operation program mandate and manual-dispatcher operating model (this filing is a fan-out worker product).

## Owner Decisions / Input

- `AUQ-20260730-PACKET-EXPIRY-AUTHORITY-MODEL` - the owner AskUserQuestion selecting "Terminal-evidence-sufficient", archived as `DELIB-202667723` (source `owner_conversation`, outcome `owner_decision`, work item WI-5694). This decision defines the exact acceptance/rejection semantics this cycle implements and mandates the four regression cases and the per-surface cycle split.
- `DELIB-202667724` - owner authorization decision issuing `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730` (status `active`, list-free), covering WI-5694 through active project membership. Per CLAUDE.md session-start rules, items already authorized by recorded owner decision need no fresh approval to enter the bridge protocol.
- No further owner decision is required to review this proposal; implementation proceeds only on bridge `GO` plus an implementation-start authorization packet.

## Requirement Sufficiency

Existing requirements sufficient. `DELIB-202667723` (owner-decided behavior semantics including the four mandatory regression cases), WI-5694's status_detail (authoritative cycle scoping), `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` (operation-time enforcement the evidence rule relies on), and `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` (authorization chain) fully determine the required behavior. No new or revised requirement is needed before implementation.

## Verification Plan (Spec-Derived Test Mapping)

New file `platform_tests/scripts/test_implementation_authorization_terminal_evidence.py`, following the existing suite's conventions (`platform_tests/scripts/test_implementation_authorization.py`: importlib module-load `auth_module` fixture, isolated tmp_path project roots, fixture bridge chains and fixture work-intent registry state; live store and live MemBase untouched). The four owner-mandated cases are T1-T4:

| # | Test (owner-mandated case) | Derives from |
|---|---|---|
| T1 | Expired-but-live-at-implementation ACCEPT: schema-v3 packet with `finalized_at < expires_at < now`, uncontested fixture registry - `assess_packet_terminal_evidence` returns `evidence_valid=True`, `expired=True`, `live_at_implementation=True`; `list_named_packets` row shows `valid=False` (active) with `evidence_valid=True`; compact output carries the row as `evidence_only=true` | DELIB-202667723 case 1; GOV-10; SPEC-1662 |
| T2 | Expired-before-implementation REJECT: (a) `finalized_at > expires_at`; (b) packet with no `implementation_start` block - both yield `evidence_valid=False` with `live_at_implementation=False` and a reason naming the failed clause | DELIB-202667723 case 2 |
| T3 | Contested REJECT: fixture registry holds an active claim for the thread from a DIFFERENT session - `evidence_valid=False`, `contested=True`; the identical fixture minus the competing claim flips to `evidence_valid=True` (pinpoints the contested clause); registry read error also yields `evidence_valid=False` with a recorded reason | DELIB-202667723 case 3 |
| T4 | Live-packet behavior unchanged: an unexpired packet passes `load_named_packet`/`validate_targets` exactly as today; an expired packet is still rejected on the active-authority path with "Implementation authorization packet has expired"; `list` `valid` semantics unchanged; `DEFAULT_EXPIRY_MINUTES` remains 120 and no new timer literal is introduced | DELIB-202667723 case 4; WI-4532 invariant; DELIB-202667722; GOV-17 |

Commands (implementation report will carry observed output):

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_authorization_terminal_evidence.py platform_tests/scripts/test_implementation_authorization.py -q`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization_terminal_evidence.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization_terminal_evidence.py`

The full existing `test_implementation_authorization.py` suite is executed unmodified as the byte-compatibility regression net for the active-authority path.

## Acceptance Criteria

1. `assess_packet_terminal_evidence` classifies all four owner-mandated cases exactly as `DELIB-202667723` requires (T1-T3), and its payload carries `evidence_valid`, `expired`, `live_at_implementation`, `contested`, `chain_state`, `active_valid`, `reasons`.
2. The active-authority path is byte-identical: every existing `_validate_packet` rejection (including expiry) still fires for `load_packet`, `load_named_packet`, `activate_packet`, `validate_targets`, and CLI `validate` (T4); the full existing suite passes unmodified.
3. `list_named_packets` rows carry `evidence_valid`/`evidence_error`/`expired` with `valid` unchanged; `list --compact` adds `evidence_valid_count` and `evidence_only` rows without removing or renaming any existing row or field (T1).
4. No cycle-2/cycle-3 surface is touched: the diff is confined to the two `target_paths` files.
5. `ruff check` and `ruff format --check` pass on both changed files; no new hard-coded timer value is introduced.

## Risk and Rollback

- Risk: the E2 proxy (durable in-window `finalized_at` plus the mutation-gate liveness invariant) admits a packet whose mutations somehow bypassed the gate. Contained: the assessment confers no authority - consumers (cycle 2/3) still run their own governed flows; and gate-bypassing mutations are a distinct defect class already fail-closed elsewhere. Posed as review question Q3.
- Risk: evidence fields on list output confuse existing consumers. Contained: additive fields only; `valid` computation untouched; compact rows that exist today are byte-compatible.
- Risk: contested-detection false negatives after claim TTL expiry (an abandoned competing claim no longer registers as a holder). Accepted per `DELIB-202667723`: contest is defined by an ACTIVE competing claim; historical released/expired claims do not contest.
- Rollback: single-commit revert of the two files. No schema migration (packet schema untouched; list fields additive), no MemBase rollback (nothing written), no state cleanup.

Recommended commit type: fix - this cycle repairs the P0 defect class of WI-5694 (origin `defect`): the validator misclassifies legitimate historical authority evidence as invalid. The new assessment function and additive list fields are the repair vehicle for existing defective classification behavior, not a new capability surface; the test file is the mandated regression net for the repaired behavior.

## Review Questions for Loyal Opposition

1. Q1: In evidence mode, is failing closed on `deferred` and `no_action` chain states the correct conservative choice, or should `no_action` (Prime-contested verdict) alone fail closed while `deferred` is reported informationally?
2. Q2: Is relying on the packet's embedded `implementation_start.project_authorization_decision` (rather than re-running the PAUTH operation-time evaluator at assessment time) the correct evidence semantics, given routine PAUTH supersession would otherwise retroactively invalidate history?
3. Q3: Is `finalized_at <= expires_at` plus the mutation-gate liveness invariant a sufficient mechanical proxy for "live when the implementation mutations occurred" for this cycle, or must cycle 1 also cross-check external mutation timestamps?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
