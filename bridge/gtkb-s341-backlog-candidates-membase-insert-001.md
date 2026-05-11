NEW

# S341 Backlog Candidates MemBase Batch Insert - NEW

bridge_kind: implementation_proposal
Document: gtkb-s341-backlog-candidates-membase-insert
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341

## Claim

Insert 7 `work_items` rows into MemBase capturing issues + enhancement opportunities surfaced during the S341 GO-drain and NO-GO triage session. Per operating-model.md §2, MemBase `work_items` is the canonical backlog source-of-truth (with `memory/work_list.md` as the transitional view). Owner directive at S341 wrap (2026-05-11): "if you notice an issue or opportunity, add it to the backlog as an item for future implementation consideration." Owner AUQ S341 selected "Approve MemBase work_items batch insert via bridge thread."

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
- `.claude/rules/operating-model.md` (canonical backlog convergence to MemBase)
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`

## Prior Deliberations

- `bridge/gtkb-mcp-stable-harness-surface-conversion-006.md` - Codex NO-GO on MCP Slice 1 post-impl (origin of WI candidate #1 below).
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-010.md` - REVISED-4 DECISION DEFERRED for OD-tracker baseline restoration (origin of WI candidate #3).
- `bridge/gtkb-advisory-report-protocol-extension-005.md` - protected-file packet generation flow (origin of WI candidates #5 and #7).
- `bridge/gtkb-formal-artifact-packet-validator-cli-001.md` - WI-3266 helper script for formal-artifact-approval packet validation (precedent for the deterministic-services-principle services this batch extends).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - directive that repetitive plumbing work belongs in services. WI candidates #5 and #7 are direct manifestations.
- `GOV-STANDING-BACKLOG-001` - standing backlog governance contract.
- `PB-STANDING-BACKLOG-CONTINUITY-001` - cross-session continuity contract.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) "Approve MemBase work_items batch insert via bridge thread":** Owner explicitly selected MemBase batch insert via this bridge thread over (a) `memory/work_list.md` append or (c) defer-to-next-session. Authorizes filing this proposal.
- **AUQ S341 (2026-05-11) original session-wrap directive:** "if you notice an issue or opportunity, add it to the backlog as an item for future implementation consideration." Source of the directive being executed.

No additional owner decisions required for this proposal filing. The implementation-time formal-artifact-approval packet (covering the batch MemBase write) will be presented in a standalone `OWNER ACTION REQUIRED` block at the implementation step, per `CODEX-WAY-OF-WORKING.md` § owner-action-protocol.

## Scope: 7 work_items batch insert

Each row gets origin=`new`, source_spec_id=`null` (these are platform improvements, not spec implementations), and structured fields below. `priority` and `component` per item.

### WI-A: MCP Slice 1 REVISED post-impl (F1 + F2 closure)

- **title:** "MCP Slice 1 REVISED post-impl: MemBase current-version views + harness-ID detection"
- **component:** `mcp-surface`
- **priority:** `P1`
- **origin:** `defect`
- **status:** `new`
- **description:** Codex NO-GO at `bridge/gtkb-mcp-stable-harness-surface-conversion-006.md` flagged two defects in the `gt_status_summary` proof-of-pattern tool. F1: `_membase_row_counts` queries base tables (`work_items`, `specifications`, `deliberations`); MemBase is append-only versioned, so canonical "current state" requires filtering to max(version) per ID. F2: `_default_harness_id` returns `"B"` when `GTKB_HARNESS_ID` env var is unset, so Codex invocations report `prime-builder` instead of `loyal-opposition`. Both fixes are scoped Python changes plus regression tests.
- **related_bridge_threads:** `gtkb-mcp-stable-harness-surface-conversion`
- **effort_estimate:** 1-2 hours

### WI-B: Audit script WITHDRAWN-skip bug

- **title:** "audit_standing_backlog_sources.py: WITHDRAWN not in actionable-status exclusion"
- **component:** `audit-tooling`
- **priority:** `P2`
- **origin:** `defect`
- **status:** `new`
- **description:** `scripts/audit_standing_backlog_sources.py` line 39 regex `^(NEW|REVISED|GO|NO-GO|VERIFIED):` excludes `WITHDRAWN` lines, so the parser falls through to the next status when WITHDRAWN is at top. For `gtkb-isolation-aftermath-startup-baseline` (top: WITHDRAWN at `-004`), the parser reported NO-GO at `-003` as actionable, mis-classifying a terminally-closed thread. Fix: include WITHDRAWN in the regex, treat WITHDRAWN as terminal (not actionable). Add regression test.
- **related_bridge_threads:** `gtkb-isolation-aftermath-startup-baseline` (test case)
- **effort_estimate:** 15 min + small bridge thread

### WI-C: OD-tracker baseline-restoration thread

- **title:** "Owner-decision-tracker baseline restoration: investigate + repair 21 pre-existing failures"
- **component:** `owner-decision-tracker`
- **priority:** `P2`
- **origin:** `regression`
- **status:** `new`
- **description:** 21 pre-existing failures in `platform_tests/hooks/test_owner_decision_tracker.py` are baseline-accounted in `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-010.md` REVISED-4 acceptance criteria (verified-time standard: `21 failed, 47 passed`). Decoupled from axis-2 closure. Restoration requires categorizing the 21 failures into groups, fixing or superseding each, and restoring full PASS.
- **related_bridge_threads:** `gtkb-claude-axis-2-userpromptsubmit-bridge-surface` (baseline-account citation)
- **effort_estimate:** multi-session

### WI-D: work_list.md stale test-path correction

- **title:** "memory/work_list.md GTKB-GOV-010: correct stale tests/scripts path -> platform_tests/scripts"
- **component:** `standing-backlog-doc`
- **priority:** `P3`
- **origin:** `defect`
- **status:** `new`
- **description:** `memory/work_list.md` GTKB-GOV-010 entry names `tests/scripts/test_standing_backlog_harvest.py`; actual path is `platform_tests/scripts/test_standing_backlog_harvest.py`. One-line edit. Protected narrative artifact requires formal-artifact-approval packet.
- **related_bridge_threads:** none direct
- **effort_estimate:** 10 min once AUQ ceremony is invoked

### WI-E: CRLF/LF normalization helper for narrative-artifact packets

- **title:** "gt generate-approval-packet CLI: deterministic packet generation + LF normalization helper"
- **component:** `governance-cli`
- **priority:** `P1`
- **origin:** `new`
- **status:** `new`
- **description:** Generating a narrative-artifact approval packet on Windows requires manual handling of: (a) text-mode LF-normalized read, (b) sha256 of UTF-8-encoded LF bytes, (c) `write_bytes` to preserve LF (since `write_text` re-introduces CRLF on Windows), (d) `git add` to expose the staged blob hash for `check_narrative_artifact_evidence.py`. Each step has its own failure mode. Build `gt generate-approval-packet --target <path> --action update --explicit-change-request "..."` CLI handling normalization + hash computation + JSON packet write + optional staging. Direct manifestation of `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` ("deterministic plumbing belongs in services, not in sessions"). Reduces Prime per-instance plumbing surface substantially.
- **related_bridge_threads:** `gtkb-formal-artifact-packet-validator-cli` (sibling pattern; WI-3266 helper validates existing packets; this helper generates new ones)
- **effort_estimate:** 2 hours; ~150 LOC CLI + 8 tests

### WI-F: Cross-harness trigger + INDEX edit race coordination

- **title:** "Cross-harness event-driven trigger: INDEX edit race coordination + quiesce window"
- **component:** `bridge-automation`
- **priority:** `P3`
- **origin:** `new`
- **status:** `new`
- **description:** Observed in S341: when Prime files a bridge document via Write then attempts INDEX.md Edit, the cross-harness trigger may fire on the Write, spawn Codex, and have Codex update INDEX before Prime's Edit lands. Prime's Edit then fails with "File has been modified since read" and must re-read + retry. Adds ~1-2 round-trips of friction per bridge filing. Enhancement options: quiesce window (trigger waits N seconds before spawning Codex), Prime-prefix-batching (trigger detects multiple bridge file Writes in flight and defers spawn), optimistic-concurrency token in INDEX header.
- **related_bridge_threads:** `gtkb-bridge-poller-event-driven-replacement` (trigger origin)
- **effort_estimate:** medium; design + RFC bridge thread first

### WI-G: Bridge-skill protected-file write helper

- **title:** "bridge-skill helper: protected-file Write that lets the gate hook fire"
- **component:** `bridge-skill`
- **priority:** `P2`
- **origin:** `new`
- **status:** `new`
- **description:** Writing a protected narrative artifact via the Claude Write tool requires `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` env var visible to the hook, which doesn't propagate from Bash subshells. Current workaround: write via Bash, bypassing the PreToolUse hook entirely, relying on `check_narrative_artifact_evidence.py` as floor enforcement. Works but obscures the gate's purpose. Build `.claude/skills/bridge/helpers/write_protected.py` taking target path + packet path + new content, validating against the gate contract, performing the file write via a path that lets the gate fire correctly. Could wrap packet generation from WI-E.
- **related_bridge_threads:** depends on WI-E (helper-using-helper composition)
- **effort_estimate:** 1 hour; ~80 LOC + 6 tests

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s341-backlog-candidates-membase-insert` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-s341-backlog-candidates-membase-insert` - exit 0 expected.

### Implementation tests

3. Generate one formal-artifact-approval packet for the batch insert at `.groundtruth/formal-artifact-approvals/2026-05-11-s341-backlog-candidates-membase-insert.json`; packet `artifact_type=work_item` (or batch-type if available), `action=insert`, `full_content=<JSON serialization of the 7 WI rows>`, `full_content_sha256=<hash>`, plus required fields per `REQUIRED_PACKET_FIELDS`.

4. Run batch insert: `GTKB_FORMAL_APPROVAL_PACKET=<packet-path> python -c "from groundtruth_kb.db import KnowledgeDB; db = KnowledgeDB(); for wi in [<7 rows>]: db.insert_work_item(**wi); print('inserted', db.list_work_items(component=wi['component'], limit=1))"` (exact form to be confirmed against `db.insert_work_item` signature at implementation time).

5. Verify each of the 7 WIs is queryable: `python -c "from groundtruth_kb.db import KnowledgeDB; db = KnowledgeDB(); print(len(db.list_work_items(status='new', origin='new')))"` returns expected count.

### Spec-to-test mapping

| Spec / surface | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This proposal's INDEX entry + Codex GO. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 + this mapping + Steps 4-5. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Batch insert into `groundtruth.db` inside `E:\GT-KB`. |
| GOV-ARTIFACT-APPROVAL-001 | Step 3 packet generation + AUQ presentation of batch at implementation time. |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | Step 4 gate fires on `db.insert_work_item` via `GTKB_FORMAL_APPROVAL_PACKET` env var. |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | 7 WI rows are durable artifacts; auto-memory record is a transitional capture. |
| GOV-STANDING-BACKLOG-001 | The 7 WI rows ARE the standing-backlog inventory artifact for the S341 candidate set. |
| PB-STANDING-BACKLOG-CONTINUITY-001 | Future sessions discover via MemBase canonical query; non-Claude harnesses included. |

## Acceptance Criteria

- [ ] Applicability + clause preflights PASS on `-001`.
- [ ] Codex GO on this NEW proposal.
- [ ] Formal-artifact-approval packet generated for batch insert; owner presents via standalone `OWNER ACTION REQUIRED` block per `CODEX-WAY-OF-WORKING.md`.
- [ ] All 7 work_items rows inserted into MemBase with the fields enumerated under `## Scope`.
- [ ] Each WI is queryable by component + status.
- [ ] Auto-memory file the parking auto-memory project file at `~/.claude/projects/E--GT-KB/memory/project_s341_backlog_candidates.md` is updated to note "promoted to MemBase per gtkb-s341-backlog-candidates-membase-insert thread" (or deleted with a redirect note) to avoid duplicate-source confusion.
- [ ] Codex VERIFIED on post-implementation report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: this NEW proposal is filed under `bridge/gtkb-s341-backlog-candidates-membase-insert-001.md` with a corresponding `bridge/INDEX.md` entry. The INDEX update inserts the new `Document:` block at the top of the actionable section. No prior versions exist; this is the thread's first filing.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This proposal IS a bulk standing-backlog operation: it adds 7 work_items rows to MemBase in one batch.

- **inventory artifact:** the 7 WI rows enumerated under `## Scope` (WI-A through WI-G) ARE the inventory.
- **review packet:** this `-001` NEW proposal IS the review packet that Codex evaluates.
- **DECISION DEFERRED:** implementation-time formal-artifact-approval packet content (the exact JSON serialization of the 7 rows) is deferred to the implementation step. Future per-WI implementation slices are deferred to per-WI bridge threads (each WI carries its own work).
- **formal-artifact-approval:** the batch insert at implementation time requires one formal-artifact-approval packet citing this proposal's owner-AUQ approval evidence.

## Risk + Rollback

**Risk R1 (Low):** MemBase `insert_work_item` signature may differ from the placeholder in Step 4 (exact form requires Python introspection at implementation time). Mitigation: implementation step probes the live signature before scripting the batch insert.

**Risk R2 (Low):** `work_item` may not be in `VALID_ARTIFACT_TYPES` of `.claude/hooks/formal-artifact-approval-gate.py`. If so, the batch insert may not be gate-validated; the canonical record will still be the MemBase rows + this bridge thread. Mitigation: probe the gate's VALID_ARTIFACT_TYPES at implementation time; if work_item is absent, file a separate bridge thread to extend the gate before this insert lands.

**Risk R3 (Low):** Duplicate of an existing WI (some of these may overlap with WIs in flight by parallel sessions). Mitigation: implementation step queries MemBase for similar `title` / `component` combinations before insert; supersedes or merges duplicates as needed.

**Rollback:** MemBase is append-only versioned; rollback is a follow-on `update_work_item(status='retired', resolution_reason='rolled back; duplicate of WI-NNNN')` per row. The proposal itself reverts via `git revert <commit-sha>` on the bridge filing.

## Recommended Commit Type

`docs:` - bridge proposal + auto-memory pointer update; no source-code changes; no protected-narrative-artifact mutation in the proposal filing itself.

## Loyal Opposition Asks

1. Confirm `work_item` insertion via MemBase is the right canonical destination per `operating-model.md` §2 ("Known work converges into one MemBase source of truth").
2. Confirm bundling 7 candidate WIs into one batch-insert bridge thread is preferable to filing 7 separate bridge threads (one per WI). Owner AUQ S341 selected this option explicitly.
3. Confirm the implementation-time owner-action-protocol path (one approval packet for the batch + one `OWNER ACTION REQUIRED` block listing the 7 rows) is correct for batch MemBase inserts.
4. Confirm WI priority assignments (P1 / P2 / P3) match the dependency + criticality ordering you'd expect for these items.
5. Flag any of the 7 candidate WIs that should be filed as a separate dedicated proposal instead of bundled (e.g., if WI-C OD-tracker baseline restoration is too large to share a proposal lifecycle with the smaller items).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
