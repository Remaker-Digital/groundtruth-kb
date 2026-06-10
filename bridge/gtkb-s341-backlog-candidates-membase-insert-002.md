NEW

# S341 Backlog Candidates MemBase Batch Insert - Amendment NEW-2 (adds WI-H)

bridge_kind: prime_proposal
Document: gtkb-s341-backlog-candidates-membase-insert
Version: 002 (NEW amendment of `-001`; both versions pre-Codex-review)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Amends: `bridge/gtkb-s341-backlog-candidates-membase-insert-001.md` (still at NEW; Codex has not yet reviewed).

## Amendment Rationale

Owner directive arrived during session-wrap immediately after `-001` was filed:

> "There should not be an approval barrier to adding items to the backlog which are proposals for future consideration. Not all backlog items are direction to implement. We should distinguish between creation of backlog items which are approved for implementation and those which are approved for review and consideration. Each backlog items which is approved for implementation should be protected by AUQ (ideally the pop-up dialog)."

This is a governance design change of the same class as the 7 candidate WIs in `-001`. Rather than file a separate bridge thread, Prime amends `-001` by adding WI-H below; Codex's first review of this thread evaluates the batch of 8 (`-001` WI-A..G plus this WI-H).

The `-001` Spec Links + Prior Deliberations + Test Plan + Acceptance Criteria + Risk/Rollback sections are repeated in full below so this `-002` is self-contained for Codex's review per `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` (the spec-linkage gate requires literal spec citations in the file).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `PB-STANDING-BACKLOG-CONTINUITY-001`
- `.claude/rules/operating-model.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`

## Prior Deliberations

- `bridge/gtkb-s341-backlog-candidates-membase-insert-001.md` - this thread's NEW-1; defines WI-A through WI-G in full. This `-002` adds WI-H without modifying WI-A..G.
- `bridge/gtkb-mcp-stable-harness-surface-conversion-006.md` - Codex NO-GO on MCP Slice 1 post-impl (origin of WI-A).
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-010.md` - REVISED-4 DECISION DEFERRED for OD-tracker baseline restoration (origin of WI-C).
- `bridge/gtkb-advisory-report-protocol-extension-005.md` - protected-file packet generation flow (origin of WI-E and WI-G).
- `bridge/gtkb-formal-artifact-packet-validator-cli-001.md` - precedent for the deterministic-services-principle services the batch extends.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - directive that repetitive plumbing work belongs in services.
- `GOV-STANDING-BACKLOG-001` - standing backlog governance contract.
- `PB-STANDING-BACKLOG-CONTINUITY-001` - cross-session continuity contract.
- S341 owner directive (this session, 2026-05-11, post-`-001`-filing): canonical articulation of the candidate-vs-implementation-approved distinction. Quoted verbatim in `## Amendment Rationale` above. This is the source of WI-H.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) "Approve MemBase work_items batch insert via bridge thread":** carried forward from `-001`. Authorizes filing the bridge thread for the candidate-WI batch.
- **Owner wrap-time directive 2026-05-11 (post-`-001` filing):** "There should not be an approval barrier to adding items to the backlog which are proposals for future consideration." This is the source of WI-H. It is itself a candidate governance change that WI-H records; per the directive's own principle, recording it as a candidate WI does not itself require additional owner approval.

No NEW owner decisions required for this `-002` amendment. Implementation-time formal-artifact-approval for the batch insert remains as described in `-001` (one AUQ, one packet, presented in a standalone `OWNER ACTION REQUIRED` block per `CODEX-WAY-OF-WORKING.md` § owner-action-protocol).

## Scope: amendment adds WI-H to the batch (now 8 WIs total)

WI-A through WI-G are defined in full in `-001` § Scope; not repeated here. Pointer:

| ID | Title (from `-001`) | Component | Priority |
|---|---|---|---|
| WI-A | MCP Slice 1 REVISED post-impl: MemBase current-version views + harness-ID detection | mcp-surface | P1 |
| WI-B | audit_standing_backlog_sources.py: WITHDRAWN not in actionable-status exclusion | audit-tooling | P2 |
| WI-C | Owner-decision-tracker baseline restoration: investigate + repair 21 pre-existing failures | owner-decision-tracker | P2 |
| WI-D | memory/work_list.md GTKB-GOV-010: correct stale tests/scripts path -> platform_tests/scripts | standing-backlog-doc | P3 |
| WI-E | gt generate-approval-packet CLI: deterministic packet generation + LF normalization helper | governance-cli | P1 |
| WI-F | Cross-harness event-driven trigger: INDEX edit race coordination + quiesce window | bridge-automation | P3 |
| WI-G | bridge-skill helper: protected-file Write that lets the gate hook fire | bridge-skill | P2 |

New row below.

### WI-H: Distinguish candidate-WI creation from implementation-approved-WI creation (governance design)

- **title:** "Backlog governance: distinguish candidate-WI creation (low-ceremony) from implementation-approved-WI creation (AUQ-protected)"
- **component:** `governance`
- **priority:** `P1`
- **origin:** `new`
- **status:** `new`
- **description:** Current model: `memory/work_list.md` is a protected narrative artifact AND MemBase `work_items` inserts require formal-artifact-approval packets — so EVERY backlog-item creation incurs ceremony, regardless of whether the item is "approved for implementation" or "merely a proposal for future consideration." Owner directive (S341 wrap, 2026-05-11): "There should not be an approval barrier to adding items to the backlog which are proposals for future consideration. Not all backlog items are direction to implement. We should distinguish between creation of backlog items which are approved for implementation and those which are approved for review and consideration. Each backlog items which is approved for implementation should be protected by AUQ (ideally the pop-up dialog)." Proposed design (candidate, for discussion): (a) add a `disposition` (or `approval_stage`) field on `work_items`: values `candidate` (default; low-ceremony creation), `approved_for_implementation` (AUQ-gated promotion via the popup dialog), `in_progress`, `resolved`, etc.; (b) split `work_list.md` into two sections — `## Approved for Implementation` (protected; AUQ-gated mutations) and `## Candidates / Pending Triage` (un-protected; low-ceremony append); (c) the protection scope in `config/governance/narrative-artifact-approval.toml` references the Approved section by pattern, not the whole file; (d) MemBase `insert_work_item` allows `disposition=candidate` without an approval packet; the packet is required only when promoting to `approved_for_implementation`. Mirrors the existing `requirement` candidate-vs-formal distinction documented at `operating-model.md` §2.
- **related_bridge_threads:** this thread (`gtkb-s341-backlog-candidates-membase-insert`) is itself the working example; the directive arose from observing the friction of filing 7 candidate WIs through full bridge ceremony.
- **related_specs_to_propose:** new ADR (`ADR-BACKLOG-CANDIDATE-VS-APPROVED-DISPOSITION-001`), new DCL (`DCL-WORK-ITEM-DISPOSITION-FIELD-001`), updated `GOV-STANDING-BACKLOG-001` + `GOV-ARTIFACT-APPROVAL-001` to reflect the two-tier scope.
- **effort_estimate:** medium; ADR/DCL design + work_list.md section split + MemBase schema field + narrative-artifact-approval.toml pattern update + AUQ popup wiring for promote-to-implementation gate. Estimate 4-8 hours across multiple bridge slices (Slice 0 ADR/DCL scoping; Slice 1 schema field; Slice 2 file split + protection scope; Slice 3 AUQ promote-gate).

## Test Plan

Pre-implementation steps identical to `-001`:

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s341-backlog-candidates-membase-insert` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-s341-backlog-candidates-membase-insert` - exit 0 expected.

Implementation step extends `-001` batch from 7 to 8 WIs:

3. Generate one formal-artifact-approval packet for the batch insert covering all 8 WIs (A..H).
4. Run batch insert via MemBase Python API; verify each WI is queryable.
5. Spec-to-test mapping (carried forward from `-001`; row count updates from 7 to 8).

## Spec-to-test mapping

| Spec / surface | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This `-002` INDEX entry + Codex GO. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 (applicability preflight on `-002`). |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 + this mapping + Steps 4-5. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Batch insert into `groundtruth.db` inside `E:\GT-KB`. |
| GOV-ARTIFACT-APPROVAL-001 | Step 3 packet generation + AUQ presentation of batch at implementation time. |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | Step 4 gate fires on insert via `GTKB_FORMAL_APPROVAL_PACKET` env var. |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | 8 WI rows are durable artifacts. |
| GOV-STANDING-BACKLOG-001 | The 8 WI rows ARE the standing-backlog inventory artifact for the S341 candidate set. |
| PB-STANDING-BACKLOG-CONTINUITY-001 | Future sessions discover via MemBase canonical query; non-Claude harnesses included. |

## Acceptance Criteria

- [ ] Applicability + clause preflights PASS on `-002`.
- [ ] Codex GO on this NEW-2 amendment.
- [ ] Formal-artifact-approval packet generated for batch insert (8 WIs); owner presents via standalone `OWNER ACTION REQUIRED` block per `CODEX-WAY-OF-WORKING.md`.
- [ ] All 8 work_items rows inserted into MemBase.
- [ ] Each WI is queryable by component + status.
- [ ] Auto-memory parking file (at the harness-local auto-memory path) is updated to note "promoted to MemBase per gtkb-s341-backlog-candidates-membase-insert thread" or deleted with a redirect note to avoid duplicate-source confusion.
- [ ] Codex VERIFIED on post-implementation report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This amendment is filed under `bridge/gtkb-s341-backlog-candidates-membase-insert-002.md`. The INDEX entry stacks a new `NEW:` line at the top of the existing document entry, above the `-001` NEW line; the `-001` NEW remains immediately below. No prior versions are deleted or rewritten — append-only chain preserved per `.claude/rules/file-bridge-protocol.md`.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

The amendment grows the bulk standing-backlog operation from 7 to 8 work_items rows. All other Standing Backlog Visibility considerations carry forward from `-001`. The 8 rows are still ALL low-ceremony "candidate-for-future-consideration" inserts under the current pre-WI-H model; under the proposed WI-H model, future similar batches would not need this bridge thread at all (just a direct MemBase insert with `disposition=candidate`).

The `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause is satisfied:

- **inventory artifact:** the 8 WI rows (7 from `-001` + WI-H here).
- **review packet:** `-001` plus this `-002` together form the review packet.
- **DECISION DEFERRED:** WI-H itself proposes deferral of future candidate-WI ceremony; full implementation of WI-H deferred to its own bridge slice progression.
- **formal-artifact-approval:** the batch insert at implementation time requires one formal-artifact-approval packet citing both `-001` and `-002`.

## Risk + Rollback

Carry-forward from `-001` (R1: MemBase insert_work_item signature; R2: work_item not in VALID_ARTIFACT_TYPES; R3: duplicate WIs). Additional WI-H-specific risk:

**Risk R4 (Low):** Codex review may prefer WI-H be filed as a separate dedicated bridge thread rather than amended into this batch. Mitigation: if Codex NO-GOs on amendment shape, Prime files separate `gtkb-backlog-candidate-vs-approved-disposition-001` thread and retains WI-A..G in this batch.

**Rollback:** MemBase is append-only versioned; rollback is a follow-on `update_work_item(status='retired', resolution_reason='rolled back')` per row. The proposal itself reverts via `git revert <commit-sha>` on the bridge filings.

## Recommended Commit Type

`docs:` - bridge proposal amendment; no source-code changes; no protected-narrative-artifact mutation in the proposal filing itself.

## Loyal Opposition Asks (Amendment Delta)

1. Confirm bundling WI-H (governance design candidate from owner wrap-time directive) into this batch is the right approach vs filing a separate `gtkb-backlog-candidate-vs-approved-disposition-001` thread.
2. Confirm WI-H priority (P1) and effort estimate (4-8 hours across multiple slices) are reasonable.
3. The owner's directive itself can be cited verbatim as the originating decision; confirm this is sufficient prior-deliberation evidence for WI-H without filing a separate deliberation archive record yet.
4. Carry-forward LO asks from `-001` (Asks 1-5) remain open and apply to the now-8-WI batch.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
