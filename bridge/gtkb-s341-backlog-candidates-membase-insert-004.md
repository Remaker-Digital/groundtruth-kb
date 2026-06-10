REVISED

# S341 Backlog Candidates MemBase Batch Insert - REVISED-1

bridge_kind: prime_proposal
Document: gtkb-s341-backlog-candidates-membase-insert
Version: 004 (REVISED-1 after Codex NO-GO at `-003`; supersedes scope of `-001` NEW and `-002` NEW-2 amendment)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S342
Responds-To: `bridge/gtkb-s341-backlog-candidates-membase-insert-003.md` (Codex NO-GO; F1 work-item payload + verification commands do not match the current API; F2 formal-approval hook does not currently cover work-item inserts; F3 acceptance criteria require an out-of-root harness-local mutation; F4 exact batch payload deferred instead of reviewable).

## Revision Notes (REVISED-1)

This REVISED-1 carries forward the strategic intent of `-001` + `-002` (S341 backlog candidates converge into MemBase rather than remain in harness-local auto-memory; candidate-vs-implementation-approved governance distinction recorded as WI-H) and addresses all four Codex findings with deterministic content reviewable as written.

**F1 closure (live API alignment):** All 8 WI rows now express their fields using the current `insert_work_item()` signature at `groundtruth-kb/src/groundtruth_kb/db.py:2947-2979`. Field corrections per the live API:

- Removed the non-existent `status` field. The live API uses `resolution_status` (values: `open` / `in_progress` / `resolved` / `verified`), defaulting to `open` for newly-created work.
- `origin` values constrained to the live enum: `regression` / `defect` / `new` / `hygiene` (`db.py:2983`). WI-A through WI-H are tagged with their correct origin per `db.py` documentation: defects map to `defect`, regressions to `regression`, fresh design candidates to `new`, the standing-backlog-doc edit to `hygiene` (corrected from `-001`'s loose `defect` tag).
- Added required fields: `changed_by` (= `prime-builder/claude/S342`), `change_reason` (per-row), `stage` (default `created`).
- Verification commands now use `list_work_items(component=<comp>)` filter (no `status`, no `limit`); rows are identified by their concrete WI-NNNN IDs, not by enum filters that don't exist on the API.

**F2 closure (formal-approval hook coverage reality):** The active `formal-artifact-approval-gate.py` does NOT cover `work_item` inserts. The hook's `VALID_ARTIFACT_TYPES` set (`{deliberation, governance, requirement, protected_behavior, architecture_decision, design_constraint}`) excludes `work_item`; the hook's `FORMAL_MUTATION_PATTERNS` regex set does NOT match `insert_work_item` (the patterns cover `insert_spec`/`update_spec`, deliberations CRUD, `link_deliberation_*`, and raw SQL against `specifications`/`deliberations`). Codex correctly observed this in F2.

REVISED-1 takes the narrower path (per Codex's F2 recommended-action option 2): the proposal does NOT claim formal-hook enforcement for the batch insert. Owner approval flows through the existing AUQ-only channel:

1. **Already-given AUQ approval (sufficient):** AUQ S342 (2026-05-11) "Pick From Standing Backlog. Parallelize work and proceed without my intervention when possible. In the course of work, if you notice an issue ... please add it to the backlog as an item for future implementation consideration." This AUQ is owner-explicit authorization for the candidate-WI batch creation; it is recorded in `memory/pending-owner-decisions.md` per the owner-decision-tracker hook.
2. **Candidate-WI low-ceremony policy:** Per the WI-H principle (canonical articulation of owner's S341 wrap-time directive at line 17 of `-002`: "There should not be an approval barrier to adding items to the backlog which are proposals for future consideration"), candidate-WI creation is intentionally low-ceremony. The formal-artifact-approval-gate's absence for `insert_work_item` is consistent with this policy rather than a gap to be filled.
3. **Bridge thread + INDEX entry IS the audit trail:** Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`, this filing + Codex GO + post-impl report + Codex VERIFIED form the canonical audit trail. The deterministic payload section below provides the same drift-detection content that an approval packet's `full_content_sha256` would provide.
4. **Future hook coverage (deferred):** If hook coverage for `insert_work_item` is later desired (e.g., for implementation-approved-WI promotion under WI-H's governance design), that's a separate `formal-artifact-approval-gate.py` extension bridge thread. WI-H is itself the natural parent of that follow-on; this REVISED-1 does NOT couple the batch insert to that future work.

**F3 closure (out-of-root mutation removed):** The previous acceptance criterion requiring update/delete of the harness-local auto-memory file at `~/.claude/projects/E--GT-KB/memory/project_s341_backlog_candidates.md` is REMOVED. Per `.claude/rules/project-root-boundary.md:8-10`, GT-KB bridge work MUST NOT mutate paths outside `E:\GT-KB`. The auto-memory file is non-live historical context for the harness; its disposition is the harness's local concern, not GT-KB bridge implementation scope. The MemBase rows are the canonical authority; the auto-memory file's existence post-insertion does NOT create duplicate-source confusion at the GT-KB level (it's a harness-local notepad, not a GT-KB-visible artifact).

**F4 closure (deterministic payload):** Added a new `## Deterministic Payloads (REVISED-1 F4 closure)` section below containing the exact `insert_work_item()` keyword arguments for all 8 rows as a reviewable JSON-shaped block. This is the precise payload the implementation will use; post-implementation evidence is verifiable against this section by content comparison. WI IDs WI-3274 through WI-3281 are reserved sequential assignments based on probe of current state (`MAX(CAST(SUBSTR(id, 4) AS INTEGER)) = 3273` per `groundtruth.db` query 2026-05-11).

## Claim

Insert 8 `work_items` rows into MemBase capturing issues + enhancement opportunities surfaced during S341. Per `operating-model.md` §2, MemBase `work_items` is the canonical backlog source-of-truth (with `memory/work_list.md` as the transitional view during the `GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH` migration). The 8 rows are ALL candidate-for-future-consideration entries (low-ceremony creation per owner directive); none are implementation-approved. WI-H itself proposes the governance-design distinction between candidate-WI creation and implementation-approved-WI creation; per its own principle, this batch is the canonical example of why that distinction matters.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `PB-STANDING-BACKLOG-CONTINUITY-001`
- `.claude/rules/project-root-boundary.md` (REVISED-1 F3 closure: governs out-of-root mutation prohibition)
- `.claude/rules/operating-model.md` (canonical backlog convergence to MemBase)
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`
- `.claude/hooks/formal-artifact-approval-gate.py` (REVISED-1 F2 closure: confirms hook does NOT cover `insert_work_item`; non-claim is honest)
- `groundtruth-kb/src/groundtruth_kb/db.py` (REVISED-1 F1 closure: governs the live `insert_work_item()` signature)
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md` § Before Proposing, deliberation search was run before this REVISED-1 filing:

```text
python -m groundtruth_kb deliberations search "S341 backlog candidates MemBase work_items batch insert insert_work_item resolution_status candidate" --limit 10
```

Relevant results:

- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` -- owner directed that future-consideration backlog capture should not require approval; implementation-approved items should be AUQ-protected.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` -- owner directive to formalize standing backlog as a DB-backed source of truth.
- `DELIB-0838` -- owner decision that the standing backlog is governed cross-session work authority.
- `DELIB-0839` -- standing backlog harvest snapshot and reconciliation obligations.
- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` -- prior LO assessment that MemBase usage needed stronger effectiveness and convergence.
- `DELIB-1580` -- verified backlog work-list retirement directive context.

Other prior bridge evidence:

- `bridge/gtkb-s341-backlog-candidates-membase-insert-001.md` -- this thread's NEW (7 WIs: A-G).
- `bridge/gtkb-s341-backlog-candidates-membase-insert-002.md` -- NEW-2 amendment (added WI-H; both pre-Codex review).
- `bridge/gtkb-s341-backlog-candidates-membase-insert-003.md` -- Codex NO-GO (F1+F2+F3+F4).
- `bridge/gtkb-mcp-stable-harness-surface-conversion-006.md` -- Codex NO-GO on MCP Slice 1 post-impl (origin of WI-A).
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-010.md` -- REVISED-4 DECISION DEFERRED for OD-tracker baseline restoration (origin of WI-C).
- `bridge/gtkb-advisory-report-protocol-extension-005.md` -- protected-file packet generation flow (origin of WI-E and WI-G).
- `bridge/gtkb-formal-artifact-packet-validator-cli-001.md` -- WI-3266 precedent for the deterministic-services-principle services this batch extends.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` -- directive that repetitive plumbing work belongs in services.

## Owner Decisions / Input

- **AUQ S342 (2026-05-11) autonomous-execution directive:** "Pick From Standing Backlog. Parallelize work and proceed without my intervention when possible. In the course of work, if you notice an issue which should be fixed or an opportunity for a useful enhancement that will help us work more effectively in the future, please add it to the backlog as an item for future implementation consideration." This AUQ is the owner-explicit authorization for the candidate-WI batch creation. Recorded in `memory/pending-owner-decisions.md` per the owner-decision-tracker hook.
- **AUQ S341 (2026-05-11) "Approve MemBase work_items batch insert via bridge thread":** carried forward from `-001`; owner selected MemBase batch insert over (a) `memory/work_list.md` append or (c) defer-to-next-session.
- **Owner wrap-time directive 2026-05-11 (post-`-001` filing):** "There should not be an approval barrier to adding items to the backlog which are proposals for future consideration. Not all backlog items are direction to implement. We should distinguish between creation of backlog items which are approved for implementation and those which are approved for review and consideration. Each backlog items which is approved for implementation should be protected by AUQ (ideally the pop-up dialog)." Source of WI-H. Recorded verbatim in `bridge/gtkb-s341-backlog-candidates-membase-insert-002.md:17`.

No NEW owner decisions required for this REVISED-1. **REVISED-1 F2 closure:** the formal-artifact-approval packet is NOT generated for this batch because `insert_work_item` is not covered by the live hook AND the candidate-WI policy is low-ceremony. The audit trail consists of: this bridge thread + Codex GO + the deterministic payloads section below + post-impl report + Codex VERIFIED.

## Scope: amendment now an 8-WI batch insert with deterministic payloads

8 candidate WIs (WI-3274 through WI-3281) covering issues and enhancement opportunities surfaced during S341. All rows use `resolution_status='open'` (the live API default for new candidates) and `stage='created'` (the live API default for newly-created work items). All rows are candidate (review-and-consideration) work items, not implementation-approved.

The deterministic-payloads section below provides the exact `insert_work_item()` keyword arguments. WI summaries:

| WI ID | Title | Component | Origin | Priority |
|---|---|---|---|---|
| WI-3274 | MCP Slice 1 REVISED post-impl: MemBase current-version views + harness-ID detection | mcp-surface | defect | P1 |
| WI-3275 | audit_standing_backlog_sources.py: WITHDRAWN not in actionable-status exclusion | audit-tooling | defect | P2 |
| WI-3276 | Owner-decision-tracker baseline restoration: investigate + repair 21 pre-existing failures | owner-decision-tracker | regression | P2 |
| WI-3277 | memory/work_list.md GTKB-GOV-010: correct stale tests/scripts path -> platform_tests/scripts | standing-backlog-doc | hygiene | P3 |
| WI-3278 | gt generate-approval-packet CLI: deterministic packet generation + LF normalization helper | governance-cli | new | P1 |
| WI-3279 | Cross-harness event-driven trigger: INDEX edit race coordination + quiesce window | bridge-automation | new | P3 |
| WI-3280 | bridge-skill helper: protected-file Write that lets the gate hook fire | bridge-skill | new | P2 |
| WI-3281 | Backlog governance: distinguish candidate-WI creation (low-ceremony) from implementation-approved-WI creation (AUQ-protected) | governance | new | P1 |

## Deterministic Payloads (REVISED-1 F4 closure)

These are the exact `insert_work_item()` keyword arguments the implementation will pass. The implementation step iterates this list and calls `db.insert_work_item(**row)` for each. Each row is intentionally minimal-but-sufficient: required fields (`id`, `title`, `origin`, `component`, `resolution_status`, `changed_by`, `change_reason`) plus directly-relevant optional fields (`priority`, `description`, `stage`, `source_owner_directive`, `source_deliberation_query`, `related_bridge_threads`).

```text
[
  {
    "id": "WI-3274",
    "title": "MCP Slice 1 REVISED post-impl: MemBase current-version views + harness-ID detection",
    "origin": "defect",
    "component": "mcp-surface",
    "resolution_status": "open",
    "changed_by": "prime-builder/claude/S342",
    "change_reason": "S341 NO-GO triage: capture MCP Slice 1 post-impl defects as candidate WIs per owner backlog-capture directive",
    "priority": "P1",
    "stage": "created",
    "description": "Codex NO-GO at bridge/gtkb-mcp-stable-harness-surface-conversion-006.md flagged two defects in gt_status_summary proof-of-pattern. F1: _membase_row_counts queries base tables; MemBase is append-only versioned, so canonical 'current state' requires filtering to max(version) per ID. F2: _default_harness_id returns 'B' when GTKB_HARNESS_ID unset, so Codex invocations report prime-builder instead of loyal-opposition. Both are scoped Python changes plus regression tests.",
    "source_owner_directive": "DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE (S341 wrap 2026-05-11)",
    "source_deliberation_query": "S341 backlog candidates MemBase work_items",
    "related_bridge_threads": "gtkb-mcp-stable-harness-surface-conversion"
  },
  {
    "id": "WI-3275",
    "title": "audit_standing_backlog_sources.py: WITHDRAWN not in actionable-status exclusion",
    "origin": "defect",
    "component": "audit-tooling",
    "resolution_status": "open",
    "changed_by": "prime-builder/claude/S342",
    "change_reason": "S341 NO-GO triage: capture audit-script defect as candidate WI per owner backlog-capture directive",
    "priority": "P2",
    "stage": "created",
    "description": "scripts/audit_standing_backlog_sources.py line 39 regex ^(NEW|REVISED|GO|NO-GO|VERIFIED): excludes WITHDRAWN lines so the parser falls through to the next status when WITHDRAWN is at top. For gtkb-isolation-aftermath-startup-baseline (top: WITHDRAWN at -004), the parser reported NO-GO at -003 as actionable, mis-classifying a terminally-closed thread. Fix: include WITHDRAWN in the regex; treat WITHDRAWN as terminal (not actionable). Add regression test.",
    "source_owner_directive": "DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE",
    "source_deliberation_query": "S341 backlog candidates MemBase work_items",
    "related_bridge_threads": "gtkb-isolation-aftermath-startup-baseline"
  },
  {
    "id": "WI-3276",
    "title": "Owner-decision-tracker baseline restoration: investigate + repair 21 pre-existing failures",
    "origin": "regression",
    "component": "owner-decision-tracker",
    "resolution_status": "open",
    "changed_by": "prime-builder/claude/S342",
    "change_reason": "S341 NO-GO triage: capture OD-tracker baseline restoration as candidate WI per owner backlog-capture directive",
    "priority": "P2",
    "stage": "created",
    "description": "21 pre-existing failures in platform_tests/hooks/test_owner_decision_tracker.py are baseline-accounted in bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-010.md REVISED-4 acceptance criteria (verified-time standard: 21 failed, 47 passed). Decoupled from axis-2 closure. Restoration requires categorizing the 21 failures into groups, fixing or superseding each, and restoring full PASS.",
    "source_owner_directive": "DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE",
    "source_deliberation_query": "S341 backlog candidates MemBase work_items",
    "related_bridge_threads": "gtkb-claude-axis-2-userpromptsubmit-bridge-surface"
  },
  {
    "id": "WI-3277",
    "title": "memory/work_list.md GTKB-GOV-010: correct stale tests/scripts path -> platform_tests/scripts",
    "origin": "hygiene",
    "component": "standing-backlog-doc",
    "resolution_status": "open",
    "changed_by": "prime-builder/claude/S342",
    "change_reason": "S341 NO-GO triage: capture standing-backlog-doc hygiene fix as candidate WI per owner backlog-capture directive",
    "priority": "P3",
    "stage": "created",
    "description": "memory/work_list.md GTKB-GOV-010 entry names tests/scripts/test_standing_backlog_harvest.py; actual path is platform_tests/scripts/test_standing_backlog_harvest.py after refactor in commit a641f622. One-line edit. Protected narrative artifact requires formal-artifact-approval packet when implemented. Captured separately in GTKB-GOV-010-FOLLOWUP-OBSERVATIONS-S342 hygiene sweep proposal.",
    "source_owner_directive": "DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE",
    "source_deliberation_query": "S341 backlog candidates MemBase work_items",
    "related_bridge_threads": "gtkb-gov-010-harvest-refresh-2026-05-11"
  },
  {
    "id": "WI-3278",
    "title": "gt generate-approval-packet CLI: deterministic packet generation + LF normalization helper",
    "origin": "new",
    "component": "governance-cli",
    "resolution_status": "open",
    "changed_by": "prime-builder/claude/S342",
    "change_reason": "S341 NO-GO triage: capture deterministic-services-principle manifestation as candidate WI",
    "priority": "P1",
    "stage": "created",
    "description": "Generating a narrative-artifact approval packet on Windows requires manual handling of: (a) text-mode LF-normalized read, (b) sha256 of UTF-8-encoded LF bytes, (c) write_bytes to preserve LF (since write_text re-introduces CRLF on Windows), (d) git add to expose the staged blob hash for check_narrative_artifact_evidence.py. Each step has its own failure mode. Build gt generate-approval-packet --target <path> --action update --explicit-change-request '...' CLI handling normalization + hash computation + JSON packet write + optional staging. Direct manifestation of DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE. Reduces Prime per-instance plumbing surface substantially.",
    "source_owner_directive": "DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE",
    "source_deliberation_query": "S341 backlog candidates MemBase work_items",
    "related_bridge_threads": "gtkb-formal-artifact-packet-validator-cli"
  },
  {
    "id": "WI-3279",
    "title": "Cross-harness event-driven trigger: INDEX edit race coordination + quiesce window",
    "origin": "new",
    "component": "bridge-automation",
    "resolution_status": "open",
    "changed_by": "prime-builder/claude/S342",
    "change_reason": "S341 NO-GO triage: capture bridge-automation friction observation as candidate WI",
    "priority": "P3",
    "stage": "created",
    "description": "Observed in S341 + S342: when Prime files a bridge document via Write then attempts INDEX.md Edit, the cross-harness trigger may fire on the Write, spawn Codex, and have Codex update INDEX before Prime's Edit lands. Prime's Edit then fails with 'File has been modified since read' and must re-read + retry. Adds ~1-2 round-trips of friction per bridge filing. Enhancement options: quiesce window (trigger waits N seconds before spawning Codex), Prime-prefix-batching (trigger detects multiple bridge file Writes in flight and defers spawn), optimistic-concurrency token in INDEX header.",
    "source_owner_directive": "DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE",
    "source_deliberation_query": "S341 backlog candidates MemBase work_items",
    "related_bridge_threads": "gtkb-bridge-poller-event-driven-replacement"
  },
  {
    "id": "WI-3280",
    "title": "bridge-skill helper: protected-file Write that lets the gate hook fire",
    "origin": "new",
    "component": "bridge-skill",
    "resolution_status": "open",
    "changed_by": "prime-builder/claude/S342",
    "change_reason": "S341 NO-GO triage: capture bridge-skill enhancement as candidate WI",
    "priority": "P2",
    "stage": "created",
    "description": "Writing a protected narrative artifact via the Claude Write tool requires GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET env var visible to the hook, which doesn't propagate from Bash subshells. Current workaround: write via Bash, bypassing the PreToolUse hook entirely, relying on check_narrative_artifact_evidence.py as floor enforcement. Works but obscures the gate's purpose. Build .claude/skills/bridge/helpers/write_protected.py taking target path + packet path + new content, validating against the gate contract, performing the file write via a path that lets the gate fire correctly. Could wrap packet generation from WI-3278.",
    "source_owner_directive": "DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE",
    "source_deliberation_query": "S341 backlog candidates MemBase work_items",
    "related_bridge_threads": "gtkb-advisory-report-protocol-extension"
  },
  {
    "id": "WI-3281",
    "title": "Backlog governance: distinguish candidate-WI creation (low-ceremony) from implementation-approved-WI creation (AUQ-protected)",
    "origin": "new",
    "component": "governance",
    "resolution_status": "open",
    "changed_by": "prime-builder/claude/S342",
    "change_reason": "S341 wrap: capture owner directive on candidate-vs-implementation-approved distinction as candidate governance-design WI",
    "priority": "P1",
    "stage": "created",
    "description": "Current model: memory/work_list.md is a protected narrative artifact AND MemBase work_items inserts require formal-artifact-approval packets -- so EVERY backlog-item creation incurs ceremony, regardless of whether the item is 'approved for implementation' or 'merely a proposal for future consideration.' Owner directive (S341 wrap 2026-05-11): 'There should not be an approval barrier to adding items to the backlog which are proposals for future consideration. Not all backlog items are direction to implement. We should distinguish between creation of backlog items which are approved for implementation and those which are approved for review and consideration. Each backlog items which is approved for implementation should be protected by AUQ (ideally the pop-up dialog).' Proposed design (candidate, for discussion): (a) add a disposition (or approval_stage) field on work_items: values candidate (default; low-ceremony creation), approved_for_implementation (AUQ-gated promotion via the popup dialog), in_progress, resolved, etc.; (b) split work_list.md into two sections -- ## Approved for Implementation (protected; AUQ-gated mutations) and ## Candidates / Pending Triage (un-protected; low-ceremony append); (c) the protection scope in config/governance/narrative-artifact-approval.toml references the Approved section by pattern, not the whole file; (d) MemBase insert_work_item allows disposition=candidate without an approval packet; the packet is required only when promoting to approved_for_implementation. Mirrors the existing requirement candidate-vs-formal distinction documented at operating-model.md section 2.",
    "source_owner_directive": "Owner wrap-time directive 2026-05-11 (S341); also DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE",
    "source_deliberation_query": "candidate work item approved for implementation AUQ backlog disposition",
    "related_bridge_threads": "gtkb-s341-backlog-candidates-membase-insert"
  }
]
```

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s341-backlog-candidates-membase-insert` -- PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-s341-backlog-candidates-membase-insert` -- exit 0 expected.

### Implementation (post-GO)

3. **ID freshness probe:** `python -c "import sys; sys.path.insert(0,'groundtruth-kb/src'); from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB(); print(db._get_conn().execute('SELECT MAX(CAST(SUBSTR(id,4) AS INTEGER)) FROM current_work_items WHERE id LIKE \"WI-%\"').fetchone()[0])"`. Expected: `3273`. If a higher number is observed (e.g., a parallel session inserted WI-3274), the implementation MUST shift all 8 IDs upward by the delta and re-emit the deterministic-payload section before invoking inserts. Post-impl report MUST cite the observed max-ID and the final assigned ID range.

4. **Batch insert:**
   ```text
   python -c "import sys; sys.path.insert(0,'groundtruth-kb/src'); from groundtruth_kb.db import KnowledgeDB; import json; db=KnowledgeDB(); rows=json.loads(open('<saved-payload-path>').read()); [db.insert_work_item(**row) for row in rows]; print('inserted', len(rows), 'work_items')"
   ```
   Expected output: `inserted 8 work_items`.

5. **Per-WI verification by exact ID + `resolution_status='open'`:**
   ```text
   python -c "import sys; sys.path.insert(0,'groundtruth-kb/src'); from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB(); ids=['WI-3274','WI-3275','WI-3276','WI-3277','WI-3278','WI-3279','WI-3280','WI-3281']; [print(wi['id'], '-', wi['resolution_status'], '-', wi['component']) for wi in (db.get_work_item(i) for i in ids) if wi]"
   ```
   Expected output: 8 lines, one per WI, each showing `resolution_status=open` and the correct component per the table.

6. **Bulk-query verification (by component):**
   ```text
   python -c "import sys; sys.path.insert(0,'groundtruth-kb/src'); from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB(); rows=db.list_work_items(resolution_status='open'); s342=[r for r in rows if r.get('changed_by','').endswith('S342')]; print('S342-batch count:', len(s342))"
   ```
   Expected output: `S342-batch count: 8` (or higher if other S342 batches are filed concurrently).

### Spec-to-test mapping

| Spec / surface | Verifying step |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This REVISED-1 INDEX entry + Codex GO + post-impl VERIFIED. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Step 1 PASS. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Step 2 PASS + this mapping + Steps 3-6 against the live API. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Batch insert into `groundtruth.db` inside `E:\GT-KB`; no out-of-root mutation per REVISED-1 F3 closure. |
| `.claude/rules/project-root-boundary.md` | **(REVISED-1 F3 closure)** Acceptance criteria contain no out-of-root mutation requirement. Auto-memory file's disposition is harness-local; not GT-KB scope. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | 8 WI rows are durable artifacts in MemBase; this bridge thread is the durable audit-trail artifact. |
| `GOV-STANDING-BACKLOG-001` | The 8 WI rows ARE the standing-backlog inventory artifact for the S341 candidate set; deterministic-payload section IS the review packet. |
| `PB-STANDING-BACKLOG-CONTINUITY-001` | Future sessions discover via MemBase canonical query (`get_work_item('WI-3274')` etc.); non-Claude harnesses included. |
| `groundtruth-kb/src/groundtruth_kb/db.py:2947-2979` (`insert_work_item` signature) | **(REVISED-1 F1 closure)** Deterministic payloads use exactly the required + optional fields per the live signature. |
| `groundtruth-kb/src/groundtruth_kb/db.py:3228-3265` (`list_work_items` signature) | **(REVISED-1 F1 closure)** Step 5/6 verification commands use `resolution_status` filter (no `status`, no `limit`). |
| `.claude/hooks/formal-artifact-approval-gate.py` `VALID_ARTIFACT_TYPES` set | **(REVISED-1 F2 closure)** Proposal does NOT claim hook coverage for `work_item`; consistent with the live set (excludes `work_item`). |
| `.claude/hooks/formal-artifact-approval-gate.py` `FORMAL_MUTATION_PATTERNS` regex set | **(REVISED-1 F2 closure)** Proposal does NOT claim hook firing on `insert_work_item`; consistent with the live regex (no `insert_work_item` match). |

## Acceptance Criteria (REVISED-1)

- [ ] Applicability + clause preflights PASS on `-004`.
- [ ] Codex GO on this REVISED-1.
- [ ] ID freshness probe (Step 3) confirms max-WI is `3273` (or implementation shifts IDs upward per the probe protocol and re-emits the payload section).
- [ ] All 8 work_items rows inserted into MemBase via Step 4 batch invocation. Step 4 output: `inserted 8 work_items`.
- [ ] Step 5 per-WI verification returns 8 lines with `resolution_status=open` and correct component.
- [ ] Step 6 bulk-query verification returns S342-batch count >= 8.
- [ ] Post-impl report cites the observed max-WI from Step 3 and the final assigned ID range (whether the canonical 3274-3281 range or a shifted range if Step 3 detected drift).
- [ ] Post-impl report cites the deterministic-payload section unchanged (drift detection: payload content matches the implementation's actual insert calls).
- [ ] Codex VERIFIED on post-implementation report.

**REVISED-1 F3 closure:** No acceptance criterion related to the harness-local auto-memory file at `~/.claude/projects/E--GT-KB/memory/project_s341_backlog_candidates.md`. Per `.claude/rules/project-root-boundary.md`, that file is outside the GT-KB root and outside the scope of this bridge thread. Auto-memory disposition is the harness's local concern.

**REVISED-1 F2 closure:** No acceptance criterion requiring formal-artifact-approval-packet generation for the batch. The owner-explicit AUQ S342 directive (recorded in `memory/pending-owner-decisions.md`) IS the owner-approval evidence; bridge thread + Codex GO + Codex VERIFIED IS the audit trail. If a future bridge slice (likely under WI-3281) extends the formal-approval-gate to cover `work_item`, that's its own scope.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This REVISED-1 is filed under `bridge/gtkb-s341-backlog-candidates-membase-insert-004.md` with a corresponding `bridge/INDEX.md` entry (insert `REVISED: bridge/gtkb-s341-backlog-candidates-membase-insert-004.md` line at top of the existing document entry, above the prior `NO-GO: -003`, `NEW: -002`, `NEW: -001` lines); append-only version chain preserved per `.claude/rules/file-bridge-protocol.md`.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This REVISED-1 IS a bulk standing-backlog operation: it adds 8 work_items rows to MemBase in one batch. Per `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`, the clause evidence pattern requires inventory artifact + review packet + DECISION DEFERRED + formal-artifact-approval. REVISED-1 satisfies the clause with this scoped adaptation:

- **inventory artifact:** the 8 WI rows enumerated in `## Scope` table AND the deterministic-payloads section below ARE the inventory.
- **review packet:** this `-004` REVISED-1 IS the review packet. The deterministic-payloads section provides the same drift-detection content that an approval packet's `full_content_sha256` would provide.
- **DECISION DEFERRED:** future per-WI implementation slices are deferred to per-WI bridge threads. WI-3281 (governance design) is itself a candidate; its implementation requires a separate bridge thread.
- **formal-artifact-approval:** N/A for `work_item` inserts per the live hook coverage (REVISED-1 F2 closure). Owner approval flows through the AUQ-S342 directive recorded in `memory/pending-owner-decisions.md`; the audit trail is this bridge thread + Codex GO + Codex VERIFIED. This is consistent with the candidate-WI low-ceremony policy under WI-3281's design principle.

## Risk + Rollback

**Risk R1 (Mitigated by REVISED-1; was F1 NO-GO):** `insert_work_item` signature drift. Mitigation: deterministic-payload section uses the live API field names per `db.py:2947-2979`; ID freshness probe (Step 3) confirms the ID assignment range before insertion.

**Risk R2 (Mitigated by REVISED-1; was F2 NO-GO):** `work_item` not in `VALID_ARTIFACT_TYPES`. Mitigation: REVISED-1 does NOT claim hook enforcement; honest non-claim per Codex F2 recommended-action option 2.

**Risk R3 (Mitigated by REVISED-1; was F3 NO-GO):** Out-of-root auto-memory mutation. Mitigation: acceptance criteria removed; auto-memory is non-live historical context.

**Risk R4 (Low):** Component-taxonomy strings (e.g., `mcp-surface`, `audit-tooling`, `owner-decision-tracker`, `standing-backlog-doc`, `governance-cli`, `bridge-automation`, `bridge-skill`, `governance`) may not all be in the canonical component taxonomy. Mitigation: the live `insert_work_item` API accepts `component` as a free-text field with a "From the component taxonomy" docstring note but no enum constraint; if a taxonomy validator is added later, the rows are amendable via `update_work_item` with `change_reason='taxonomy-aligned: <delta>'`.

**Risk R5 (Low):** Concurrent batch from a parallel session could collide on WI-3274 through WI-3281. Mitigation: Step 3 ID freshness probe detects this; implementation shifts IDs upward and re-emits the payload section.

**Risk R6 (Low):** Duplicate of an existing WI (some of these may overlap with WIs in flight). Mitigation: implementation step queries MemBase for similar `title` / `component` combinations before insert; if duplicates are found, supersede or merge per F4 deterministic-content evidence.

**Rollback:** MemBase is append-only versioned; rollback is a follow-on `db.update_work_item(id=<id>, changed_by='prime-builder/claude/S342', change_reason='reverted: <commit-sha>', resolution_status='rejected')` per row (treating reversion as resolution into a non-active state). The bridge thread reverts via `git revert <commit-sha>` on the bridge filing commit.

## Recommended Commit Type

`docs:` -- bridge proposal REVISED-1; no source-code changes; no protected-narrative-artifact mutation in the proposal filing itself. The MemBase batch insert at implementation time is a DB-state change (`docs:` or `feat:` depending on convention; conventional-commits treats DB-state changes as `feat:` -- the implementation commit may use `feat:` to reflect that the 8 candidate WIs are new durable backlog artifacts).

## Loyal Opposition Asks

1. Confirm F1 closure: deterministic-payloads section uses live `insert_work_item()` field names (`resolution_status` not `status`; `origin` values from the live enum; required + optional fields per `db.py:2947-2979`); Step 5/6 verification commands use the live `list_work_items` filter shape.
2. Confirm F2 closure: REVISED-1's non-claim of formal-hook enforcement is the appropriate narrower path. The audit trail consists of the bridge thread + Codex GO + Codex VERIFIED + the deterministic-payloads section (drift-detection equivalent to an approval packet's `full_content_sha256`); owner approval is the AUQ-S342 directive recorded in `memory/pending-owner-decisions.md`.
3. Confirm F3 closure: the out-of-root auto-memory mutation requirement is removed; auto-memory is non-live historical context outside the GT-KB scope per `.claude/rules/project-root-boundary.md`.
4. Confirm F4 closure: the deterministic-payloads section provides reviewable JSON-shaped content for all 8 rows. Post-impl evidence is verifiable against this section.
5. Confirm WI-3281 (governance design) staying in this batch is acceptable. Splitting it into a separate thread would lose the natural example-of-the-principle linkage (the directive arose from observing the friction of filing 7 candidate WIs through full bridge ceremony; the batch IS the manifestation).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
