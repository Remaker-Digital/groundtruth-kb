NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code proposal-author worker dispatched under the parallel-operation mandate DELIB-202667735; this filing is a Prime Builder proposal-authoring act (envelope pb); the parent interactive session's resolver fallback reports loyal-opposition; authoring-only scope - no implementation, commit, or review in this session

bridge_kind: prime_proposal
Document: gtkb-wi5824-protected-commit-checker-null-safety-ordering
Version: 001
Date: 2026-07-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5824

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]
implementation_scope: checker_null_safety_state_ordering_and_transaction_local_terminal_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5824 Implementation Proposal — Protected-Commit Checker: Null-Safe Capability Clearance and Transaction-Local Terminal-Evidence Ordering

## Summary

Repair two P0 defects in the pre-commit protected-path checker `scripts/check_protected_commit_authorization.py` that broke governed VERIFIED finalization on 2026-07-30: (a) `_bridge_publication_capability_clearance` parses `consumed_at` before checking `capability_state`, so a `recovery_required` capability row with `consumed_at = NULL` crashes the whole pre-commit hook with an uncaught `AttributeError` instead of cleanly denying — this rolled back the only true VERIFIED finalization attempt of 2026-07-30 (dsv4pro-r2b-008, 23:41:31Z); and (b) writing a VERIFIED verdict makes the thread terminal in the live worktree chain, which the same commit's protected-path evaluation reads as "the implementation phase for this proposal is closed", invalidating the GO packet evidence for the implementation paths staged inside the same atomic finalize-verified transaction. An owner-authorized hot-patch for (a) is already live-uncommitted in the worktree; this proposal formalizes it through the governed cycle (retroactive governance per the emergency-bootstrap exception class) and proposes the permanent state-first fix plus the transaction-local terminal-evidence ordering fix, with regression tests for both.

This proposal is filed as the next numbered bridge file `bridge/gtkb-wi5824-protected-commit-checker-null-safety-ordering-001.md`, continuing the append-only versioned bridge file chain. No prior versions are deleted or rewritten; the numbered bridge files form the canonical append-only audit trail per GOV-FILE-BRIDGE-AUTHORITY-001, and dispatcher/TAFE bridge state plus these status-bearing numbered files remain the canonical workflow state.

## Problem Evidence (fresh canonical reads, 2026-07-30/31)

All claims below were re-derived this session from the live worktree, git HEAD, MemBase (`gt backlog show WI-5824 --json`), and the code of record.

### Defect (a): null-unsafe capability clearance, state check ordered after timestamp parse

1. **HEAD code.** At git HEAD, `_bridge_publication_capability_clearance` (defined at line 1993; timestamp block near line 2032) runs:

   ```python
   try:
       parse_iso(capability["expires_at"])
       parse_iso(capability["consumed_at"])
   except (TypeError, ValueError):
       return False, "bridge publication capability has incomplete or invalid timestamps"
   ```

   before any `capability_state` check. The state checks — `compensated` deny (lines 2039-2044) and `capability_state != "consumed"` deny (lines 2045-2046) — come after.
2. **Crash mechanism.** `parse_iso` (`scripts/implementation_authorization.py` lines 158-159) begins `value[:-1] + "+00:00" if value.endswith("Z") else value`. For `consumed_at = None` (the stored value on minted and `recovery_required` rows, which by definition have not consumed), `None.endswith` raises `AttributeError: 'NoneType' object has no attribute 'endswith'` — which the `except (TypeError, ValueError)` clause does not catch. The pre-commit hook dies with a traceback instead of returning the clean deny; the enclosing finalize-verified transaction fails and the helper rolls the verdict back.
3. **Incident evidence (r2b-008, 2026-07-30 23:41:31Z).** Per the WI-5824 defect record (fresh `gt backlog show WI-5824` this session): the crash "rolled back the only true VERIFIED attempt of 2026-07-30 (dsv4pro-r2b-008, 23:41:31Z)" with the verbatim failure class `AttributeError NoneType endswith`. Corroborating live state: the `gtkb-wi5808-harness-probe-dsv4pro-r2b` chain on disk ends at `-007` (REVISED) — no `-008` file exists, consistent with the fail-closed helper removing the rolled-back verdict.
4. **Hot-patch already live-uncommitted.** `git --no-optional-locks diff scripts/check_protected_commit_authorization.py` shows exactly one hunk (worktree vs HEAD):

   ```diff
   @@ -2027,8 +2027,12 @@ def _bridge_publication_capability_clearance(
        # expires_at bounds mint-to-consume use. Once consumed, the immutable row is
        # archival commit evidence and remains valid after that short publication TTL.
   +    # consumed_at is null on minted/recovery_required rows; parse_iso requires a
   +    # string and must not AttributeError before the incomplete-timestamp deny.
        try:
            parse_iso(capability["expires_at"])
   +        if capability["consumed_at"] is None:
   +            raise TypeError("consumed_at is null")
            parse_iso(capability["consumed_at"])
        except (TypeError, ValueError):
            return False, "bridge publication capability has incomplete or invalid timestamps"
   ```

   This hot-patch was applied in-session on 2026-07-30 (~23:5x UTC) under an explicit owner override of live WI-5441 NO-GO discipline covering this module, during the r2b-008 incident, to unblock finalization immediately. It is existing worktree state requiring retroactive governance — see § Retroactive Governance of the Live Hot-Patch below.

### Defect (b): VERIFIED-closes-phase ordering defeats same-transaction finalization

5. **Phase-closure derivation.** `_validate_packet` (`scripts/implementation_authorization.py` lines 2540-2596) derives post-GO chain state from the live versioned bridge-file chain via `bridge_entry` — which reads the worktree, including a just-written, not-yet-committed VERIFIED verdict — and raises: `"Bridge thread is VERIFIED (terminal at {entry.latest_path}); the implementation phase for this proposal is closed. File a new bridge proposal for further work on this surface."` (lines 2580-2585). `list_named_packets` (line 2801) marks any packet failing `_validate_packet` as `valid=False` carrying that error.
6. **Checker consumption.** The checker's route-1 clearance (`_load_live_go_evidence`, line 1335) consumes `list_named_packets`; once the verdict file exists in the worktree, the GO packet that authorized the staged implementation paths flips to invalid with exactly the phase-closure error — before the commit that would make the terminal state durable. Route 2 (`_load_verified_evidence`) reads terminal evidence only from the pinned HEAD commit (line 1486: "terminal VERIFIED evidence cannot be read without a pinned HEAD commit"), so a same-transaction verdict is invisible to it by design. Route 3 (`_load_transaction_verified_evidence`, line 1746, landed 2026-07-20) exists for exactly this scenario but did not clear the 2026-07-30 finalizations: its packet/PAUTH revalidation and chain-derivation path still evaluates against post-write ambient state rather than honoring the transaction-local terminal evidence first.
7. **Live evidence (wi5759, wi5758).** The WI-5824 record quotes the wi5759 VERIFIED-004 evidence: "git commit failed with exit 1 ... Bridge thread is VERIFIED (terminal ...); the implementation phase for this proposal is closed". Live aftermath, fresh-read this session: `bridge/gtkb-wi5759-ruff-gate-staged-blob-004.md` (VERIFIED, with a helper-generated `## Commit Finalization Evidence` section whose Same-transaction path set names the chain files plus `scripts/check_ruff_format.py` and `platform_tests/scripts/test_check_ruff_format.py`) sits uncommitted while `.gtkb-state/auto-finalize-sweep/sweep.jsonl` repeats `"action": "skip", "reason": "verified impl not committed: platform_tests/scripts/test_check_ruff_format.py, scripts/check_ruff_format.py"` from 2026-07-30T23:53:45Z through 2026-07-31T02:23:05Z; the wi5758 thread shows the same wedge. The denial class is also on the historical record at `bridge/gtkb-wi4894-storm-watchdog-pythonw-output-repair-002.md` line 135 (legitimate deny of post-terminal mutation — behavior that must be preserved).
8. **Prior independent diagnosis of the same family.** `bridge/gtkb-wi5441-registry-db-schema-009.md` (NO-GO, 2026-07-24) already recorded: "The failure is a bridge-finalization/checker defect, not a defect in `db.py` or its focused tests. ... This prevents valid transaction-local VERIFIED evidence for the two protected implementation paths."

## Retroactive Governance of the Live Hot-Patch

The hot-patch in evidence item 4 was an emergency repair of governance infrastructure whose defect was blocking the governance protocol itself: the pre-commit checker — the commit-time enforcement layer every governed finalization depends on — was crashing, and no governed cycle could land a fix through a gate that dies with a traceback mid-evaluation. This matches the sanctioned-conditions shape of `.claude/rules/governance-emergency-bootstrap-protocol.md` (the emergency-bootstrap exception class): (1) a foundational governance subsystem (a registered commit gate) was broken with an active failure; (2) the normal bridge path was blocked by the very defect being repaired; (3) the change was the minimal repair (a two-line null guard). The owner authorized the hot-patch in-session, overriding live WI-5441 NO-GO discipline covering this module (transcript-evidenced; see Owner Decisions / Input).

This proposal is the formalization vehicle: the implementation phase commits the permanent form of the fix (subsuming the interim hot-patch) through the full governed cycle — LO GO, implementation-start packet, regression tests, implementation report, independent VERIFIED with atomic finalization — closing the audit-trail obligation. Per protocol clause (c), the in-session owner override must also be captured retroactively as a Deliberation Archive owner-decision record; that capture is an owner-visible KB mutation outside this implementation's scope (`kb_mutation_in_scope: false`) and is flagged as a required companion action for the owner/leader session through the governed decision-capture path.

## Proposed Design

### Fix A — state-first, null-safe capability clearance (`_bridge_publication_capability_clearance`)

1. **Reorder state before timestamps.** Evaluate the `capability_state` clauses before any `consumed_at` handling: the compensated/failed deny and the `capability_state != "consumed"` deny (which names the actual state, e.g. `"bridge publication capability is not consumed ('recovery_required')"`) move ahead of the timestamp block. A `recovery_required` or minted row then denies cleanly and precisely on state, never reaching `consumed_at` parsing. `expires_at` validation is retained where it is (it bounds mint-to-consume use and applies to all rows).
2. **Null-safe timestamp validation retained as defense in depth.** For rows that reach the consumed path, `consumed_at` must be a non-null string that parses; a `None` or non-string value yields the existing clean deny "bridge publication capability has incomplete or invalid timestamps". Guaranteed property: no input row shape can escape this function as an uncaught exception. The implementation may express the guard as an explicit `isinstance(..., str)` check or a null-tolerant parse wrapper; tests lock the behavior, not the construction.
3. **Hot-patch subsumption.** The permanent form preserves the hot-patch's observable guarantee (clean deny, no traceback, on null `consumed_at`) and supersedes its interim raise-TypeError construction. Committing this function through the governed cycle formalizes the currently uncommitted worktree state.

### Fix B — transaction-local terminal-evidence ordering

**Behavior contract:** when the staged transaction contains exactly one valid VERIFIED candidate for bridge id X — valid per the existing `_load_transaction_verified_evidence` validation chain (Git-added candidate, Commit Finalization Evidence manifest equal to the staged path set, strict lifecycle resolution to the candidate, resolver-approved chain, evidence anchors, snapshot compliance audit, review independence, finalized implementation-start packet bound to the chain) — then phase-closure conclusions derived from that same in-transaction verdict must not deny the transaction's staged implementation paths. Transaction-local terminal evidence is honored before phase closure is derived.

**Mechanism (implementation to select within this contract; tests lock behavior, not mechanism):**

- *Pre-transaction chain-state derivation:* when evaluating packet validity for a bridge id whose staged transaction includes that thread's VERIFIED candidate, derive the post-GO chain state as of the pre-transaction state (excluding staged in-transaction verdict files), so the GO packet remains valid evidence until the commit that lands the terminal verdict; and/or
- *Evaluation-order short-circuit:* compute and honor the fully validated transaction-local clearance for affected paths before phase-closure-derived packet errors from the same thread's in-transaction verdict can contribute a blocking finding, ensuring route 3's own packet/PAUTH revalidation does not consult post-write ambient chain state in a way that defeats it.

**Fail-closed preservation (explicit non-goals of the relaxation):**

- No staged VERIFIED candidate → behavior byte-identical to today.
- More than one live VERIFIED candidate in the transaction → deny unchanged.
- Manifest/staged-set mismatch, non-added candidate, self-review, invalid chain, absent/unbound packet → deny unchanged.
- Committed-terminal threads keep denying new post-terminal mutations exactly as today (the wi4894-002 denial class is a regression-tested invariant, not collateral).
- Verdicts for a different bridge id never affect another thread's packet evaluation.

### Explicitly out of scope

- Recovery of the currently wedged wi5758/wi5759 finalizations (their uncommitted VERIFIED verdicts and implementation paths) — a separate recovery lane; this fix removes the defect for future finalizations and re-runs.
- Any change to `scripts/implementation_authorization.py`, the governed publication writer, dispatcher/TAFE state, or capability minting/consume flows.
- Any mutation of existing bridge chain files, MemBase records, or the WI-5441 threads.
- No new timers, intervals, retries, or throttle literals (DELIB-202667722).

## WI-5441 Coordination Note

`_bridge_publication_capability_clearance` was authored by the WI-5441 thread `gtkb-wi5441-bridge-publication-capability-commit-clearance` (VERIFIED at `-010`). Separate WI-5441 threads whose declared target scope includes `scripts/check_protected_commit_authorization.py` hold live NO-GO state: `gtkb-wi5441-registry-control-plane-reverse-coverage` (latest `-012`, NO-GO) and its `-v2` successor (latest `-002`, NO-GO); the `-v4` successor chain completed (VERIFIED at `-006`). This proposal acknowledges that live NO-GO state explicitly and coordinates rather than bypasses: WI-5824 is a distinct defect-origin work item under a distinct PAUTH, scoped strictly to the two defects above; it does not act on, revive, resolve, or supersede any WI-5441 verdict or scope. The owner's in-session override of that NO-GO discipline applied to the emergency hot-patch only and is being formalized here. Any future WI-5441 successor work touching this function must rebase on the WI-5824 outcome; the LO reviewer is asked to confirm this boundary (Review Questions, item 4).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail and finalization durability authority; the checker enforces terminal-VERIFIED commit discipline this WI repairs; WI-5824 `source_spec_id`. (required)
- `GOV-ARTIFACT-APPROVAL-001` — approval-gate authority; retroactive owner-approval capture obligation for the emergency hot-patch; PAUTH included spec. (required)
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the protected-commit checker is a commit-time mechanical enforcement layer; a crashing or self-defeating gate violates the two-layer defense contract this spec mandates. (required)
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project-level authorization chain under which this proposal proceeds; the checker consumes its packet evidence. (required)
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — operation-time PAUTH enforcement the checker implements; Fix B must preserve it. (required)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal's specification-linkage obligation. (required)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — governs downstream verification; satisfied by the Specification-to-Test Mapping below. (required)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — root-boundary containment; both target paths are in-root platform surfaces (`scripts/`, `platform_tests/`). (required)
- `SPEC-1662` — assertion quality: tests assert behavioral outcomes (clean deny text, cleared/deny classifications), not structural presence. (advisory)
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — the checker is a deterministic service; repairs keep it pure and caller-driven. (advisory)
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — all evidence above derives from fresh canonical reads this session. (advisory)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — incident, hot-patch, and formalization preserved as durable artifacts, not session context. (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability across incident evidence, proposal, tests, and verdicts. (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — defect-origin WI lifecycle transitions for WI-5824. (advisory)
- `GOV-STANDING-BACKLOG-001` — WI-5824 in MemBase is the sole work authority for this repair. (advisory)

## Prior Deliberations

- **DELIB-202667735** — Delegated proposal authoring and unblock-implementation mandate with role-transition plan: the owner mandate under which this proposal-author worker files this NEW proposal.
- **DELIB-202667731** — Harness Test Corrections whole-project authorization decision (AUQ-20260730-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-GRANT): the list-free grant recorded as PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730.
- **DELIB-202667730** — Harness Test final synthesis: the evaluation program whose finalization attempts surfaced both defects; chartered the corrections project carrying WI-5824.
- **DELIB-202667726** — Program pause + Harness Test program directive: originating owner mandate for the program and its corrections follow-on.
- **DELIB-202667723** — Terminal-evidence-sufficient: expired implementation-start packets remain valid evidence of implementation-time authority — the same "evidence at the time of the act, not ambient state now" principle Fix B applies to same-transaction terminal evidence.
- **DELIB-202667722** — Timer and throttle governance: no new hard-coded timer values; this design introduces none.
- **Bridge-file evidence (not yet DELIB-harvested):** r2b-008 rollback (WI-5824 record; chain ends at `bridge/gtkb-wi5808-harness-probe-dsv4pro-r2b-007.md`); wi5759 phase-closure wedge (`bridge/gtkb-wi5759-ruff-gate-staged-blob-004.md` + sweep log); prior family diagnosis at `bridge/gtkb-wi5441-registry-db-schema-009.md`.

## Owner Decisions / Input

1. **DELIB-202667731 / AUQ-20260730-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-GRANT**: the owner issued the taxonomy-clean, list-free whole-project implementation authorization for PROJECT-GTKB-HARNESS-TEST-CORRECTIONS member work items, including WI-5824. It authorizes this proposal-review-implementation cycle; it does not waive independent Loyal Opposition GO, the fresh work-intent claim, the implementation-start packet, exact target-path enforcement, the implementation report, or independent VERIFIED with governed atomic finalization.
2. **In-session owner override authorizing the hot-patch (transcript-evidenced, 2026-07-30 ~23:5x UTC)**: during the r2b-008 incident the owner explicitly authorized the immediate null-guard hot-patch to `scripts/check_protected_commit_authorization.py`, overriding the live WI-5441 NO-GO discipline covering this module. This decision is currently transcript-evidenced only; per `.claude/rules/governance-emergency-bootstrap-protocol.md` clause (c) and `GOV-ARTIFACT-APPROVAL-001` it must be captured retroactively as a Deliberation Archive owner-decision record through the governed decision-capture path (owner-visible; outside this implementation's scope). This proposal treats the override as the owner-approval evidence for the pre-existing worktree state it formalizes.
3. **DELIB-202667735**: the delegated-authoring mandate under which this worker files; no additional owner decision is required to review this proposal. This proposal does not itself authorize implementation.

## Requirement Sufficiency

**Existing requirements sufficient.** The WI-5824 defect record (fresh-read via `gt backlog show WI-5824 --json`, including both defect mechanisms and their incident evidence), `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`, `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, the emergency-bootstrap protocol, and DELIB-202667722/202667723 fully constrain this implementation. No new or revised specification is required before implementation.

## Specification-to-Test Mapping

All tests land in `platform_tests/scripts/test_check_protected_commit_authorization.py`, following the module's existing conventions (direct helper-function tests near the existing `_bridge_publication_capability_clearance` coverage at ~line 3233; end-to-end `tmp_path` git-fixture tests per the registry-commit test family at ~line 2980).

| Requirement source | Behavior under test | Test |
|---|---|---|
| WI-5824 (a) / GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 | `recovery_required` row with `consumed_at = NULL` → clean deny naming the capability state; no exception of any kind escapes | `test_capability_clearance_denies_cleanly_on_null_consumed_at` |
| WI-5824 (a) — state-first ordering | minted / non-consumed rows deny on state before any `consumed_at` parsing occurs | `test_capability_clearance_checks_state_before_consumed_timestamp` |
| WI-5824 (a) — normal path preserved | consumed row with valid timestamps → existing clearance/deny outcomes byte-identical (including staged-digest match) | `test_capability_clearance_consumed_row_normal_path_unchanged` |
| WI-5824 (a) — defense in depth | `None`/non-string `expires_at` or `consumed_at` on a consumed row → clean "incomplete or invalid timestamps" deny, no traceback | `test_capability_clearance_non_string_timestamps_deny_cleanly` |
| WI-5824 (b) / GOV-FILE-BRIDGE-AUTHORITY-001 | end-to-end fixture: staged implementation paths + fresh same-transaction VERIFIED verdict with Commit Finalization Evidence and bound finalized packet → protected-path phase evaluation passes (exit 0; paths cleared) | `test_finalize_verified_same_transaction_phase_evaluation_passes` |
| WI-5824 (b) — fail-closed floor | committed-terminal thread + newly staged mutation of its target paths → denied exactly as today (wi4894-002 denial class) | `test_committed_terminal_thread_still_denies_new_mutations` |
| WI-5824 (b) — fail-closed floor | two live VERIFIED candidates in one transaction → denied | `test_transaction_local_multiple_verified_candidates_denied` |
| WI-5824 (b) — fail-closed floor | manifest ≠ staged set → denied | `test_transaction_local_manifest_mismatch_denied` |
| DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001 | Fix B does not weaken PAUTH operation-time validation: a transaction-local candidate with an unbound/absent packet is denied | `test_transaction_local_unbound_packet_denied` |
| SPEC-1662 / regression floor | full existing checker suite green, unchanged | `python -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` |

## Acceptance Criteria

1. A `recovery_required` (or any non-consumed) capability row with `consumed_at = NULL` produces a clean structured deny; no traceback can escape `_bridge_publication_capability_clearance` for any row shape.
2. Consumed rows with valid timestamps flow through the existing clearance logic unchanged.
3. The end-to-end finalize-verified fixture — implementation paths + same-transaction VERIFIED verdict + finalization evidence + bound packet staged together — passes phase evaluation and exits 0.
4. Committed-terminal denial, multi-candidate denial, manifest-mismatch denial, and packet-binding denial behave exactly as before (fail-closed floor regression-locked).
5. `ruff check` and `ruff format --check` pass clean on both target files (separate gates).
6. `python -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` passes green with zero regressions.
7. The committed diff introduces no new timer, interval, retry, or throttle literals, and the worktree hot-patch hunk is subsumed (no residual uncommitted delta on this function).

## Risk and Rollback

- **Risk: over-relaxation of phase closure (Fix B).** Mitigated: the relaxation is conditioned on the full existing transaction-local validation chain (exactly-one added candidate, manifest equality, strict lifecycle, approved chain, review independence, bound finalized packet); every non-conforming shape keeps today's deny, and the fail-closed floor is regression-locked by four dedicated tests.
- **Risk: message/ordering drift consumers (Fix A).** Reordering changes the deny message for non-consumed null-timestamp rows from a timestamp deny to the more precise state deny. Both are deny outcomes of the same function; no caller branches on the message text (fresh-read: callers consume only the boolean). Tests lock the new precedence.
- **Risk: interaction with the live wedged threads.** This change does not touch wi5758/wi5759 state; their recovery re-runs simply stop hitting the ordering defect once the fix lands.
- **Rollback:** exact revert of the two target files. No MemBase mutation, no dispatcher/TAFE state, no bridge chain files, no schema changes. Note the pre-fix baseline for this function is the hot-patched worktree state, itself preserved verbatim in this proposal's evidence.

## DISARM — KB Mechanics

This proposal creates and modifies source and test files only. No MemBase records, specifications, ADRs, DCLs, work items, Deliberation Archive entries, or other KB-governed artifacts are created, updated, or retired by this implementation; `kb_mutation_in_scope: false` is accurate. The retroactive owner-decision capture for the hot-patch override (Owner Decisions item 2) is a governed companion action for the owner/leader session, not performed by this implementation. All DELIB and spec citations here are read-only references.

## DISARM — Packet Mechanics

The implementation-start packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-wi5824-protected-commit-checker-null-safety-ordering`, run only after an independent Loyal Opposition GO) is session-local implementation-scope evidence. It is not a formal artifact under GOV-ARTIFACT-APPROVAL-001 and requires no separate approval packet; it derives from TAFE/dispatcher bridge state, this proposal, and the GO verdict; it expires and fails closed on bridge status drift. The PAUTH triple in this proposal's header supplies the project-authorization evidence the packet validator consumes; it never broadens `target_paths` and never replaces the live latest-GO requirement.

## Recommended Commit Type

Recommended commit type: fix — repairs broken checker behavior (crash on null timestamp; self-defeating phase-closure ordering) with regression tests; no new capability surface.

## Loyal Opposition Review Questions

1. Fix A ordering: is state-before-timestamps the correct precedence, and is the retained null-safe timestamp guard sufficient defense in depth for future row shapes?
2. Fix B contract: does conditioning the phase-closure relaxation on the complete existing transaction-local validation chain preserve every fail-closed property you would enforce, and is the pre-transaction chain-state derivation the mechanism you would prefer over the evaluation-order short-circuit?
3. Retroactive governance: does this proposal's treatment of the live-uncommitted hot-patch (emergency-bootstrap exception class; formalization through this cycle; retroactive DA capture flagged as a companion obligation) satisfy the audit-trail requirements, or should the after-action record take a different artifact form?
4. WI-5441 boundary: confirm this proposal's scope does not collide with, revive, or bypass the live WI-5441 NO-GO threads covering this module, and that the coordination note's rebase obligation is the right disposition.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
