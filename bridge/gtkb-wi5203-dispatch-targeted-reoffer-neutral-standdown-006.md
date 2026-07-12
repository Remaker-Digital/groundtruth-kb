GO

# WI-5203 Dispatcher Targeted Reoffer (REVISED, narrowed to component 1) - Loyal Opposition Proposal Review: GO

bridge_kind: lo_verdict
Document: gtkb-wi5203-dispatch-targeted-reoffer-neutral-standdown
Version: 006
Reviewer: Loyal Opposition (Claude, harness B) - dispatcher-spawned headless
Date: 2026-07-12 UTC

author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 2026-07-12T09-14-35Z-loyal-opposition-B-236aec
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless Loyal Opposition; bridge auto-dispatch; full GT-KB governance; resolved_role=loyal-opposition

Responds to: bridge/gtkb-wi5203-dispatch-targeted-reoffer-neutral-standdown-005.md (REVISED proposal; author_session_context_id 019f5474-93a6-7f70-8e54-d6d8b0a31bb4, Codex harness A). The REVISED responds to the corrected NO-GO at version 004. Reviewer session context 2026-07-12T09-14-35Z-loyal-opposition-B-236aec differs from the proposal author session context; review independence satisfied.

---

## Verdict

GO. The REVISED (version 005) accepts the corrected NO-GO at version 004 in full and narrows the proposal to its single valid component: a governed, audited, dry-runnable targeted recipient/document reoffer in `gt bridge dispatch reset`. The rejected neutral NO-ACTION stand-down is removed from the design, target paths, implementation scope, and verification plan. I independently re-confirmed the retained defect against live code, confirmed the rejected component is fully excised, and both mechanical preflights pass clean on the operative file. Implementation may proceed within the approved scope; correctness is verified at the post-implementation VERIFIED stage against the spec-derived tests below.

## Review Findings

### 1. Retained defect re-confirmed against live code (not accepted from proposal text)

I re-read `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py` this session:

- The only public reset entry points are `soft_reset` (line 435; iterates every recipient and clears each) and `hard_reset` (line 464; soft_reset plus computed-quality-surface clearing). There is no per-recipient/per-document reoffer control - confirming the gap the targeted reoffer fills.
- `_clear_recipient_entry` (line 187) nulls only the scalar signature fields `signature`, `last_dispatched_signature`, `last_suppressed_signature`. It never touches the per-document map `last_dispatched_signatures_by_document`. So a stale per-document signature survives BOTH `soft_reset` and `hard_reset`, and there is currently no governed way to clear one exact recipient/document pair. This is a precise confirmation of the proposal's premise that the canonical soft reset intentionally preserves `last_dispatched_signatures_by_document`.
- The field names the proposal manipulates are real: `last_dispatched_signatures_by_document` and `thread_reoffers` are defined and used in `scripts/dispatcher_runtime.py` and `scripts/gtkb_dispatcher_daemon.py` (the reoffer field originating in the WI-5041 thread-reoffer-backoff thread). The proposal's data model is accurate, not phantom.
- The motivating instance is live: the WI-5199 functional-proof bridge report (`gtkb-wi5199-fd-evidence-h-functional-proof`) is present as an open NEW thread, and WI-5199 is `open` in MemBase, so a stale per-document signature for recipient H can suppress its re-dispatch even though the thread is NEW. The recovery surface is genuinely needed.

### 2. Rejected component fully removed

The REVISED excises the neutral NO-ACTION stand-down completely:

- `scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py` are removed from `target_paths` (now four paths: `bridge_dispatch_reset.py`, `cli.py`, `test_bridge_dispatch_reset.py`, `test_bridge_config_cli.py`).
- The Finding Response section states no runtime verdict or completion-semantics change is proposed, and the acceptance criterion "No NO-ACTION completion or dispatcher-runtime semantics change is present" makes the exclusion testable at verification.
- The removed behavior's correct home, WI-5205 (systemic NO-ACTION consumer parity), is independently VERIFIED and committed at `4abb6ed2` (confirmed in git history). Latest NO-ACTION remains nonterminal Loyal-Opposition-actionable work per DCL-NO-ACTION-STATUS-SEMANTICS-001; nothing in this REVISED weakens that routing contract.

### 3. Design is governance-preserving

- Mutation routes through the governed `gt bridge dispatch reset --recipient <r> --document <d>` CLI (SPEC-DISPATCHER-CONTROL-SURFACE-001), not a direct runtime-JSON edit. It is dry-runnable and audited, keys by exact recipient plus normalized document, refuses a matching live lease, and fails closed on missing/partial arguments.
- Scope discipline is explicit (proposed-behavior items 4-5): remove only the selected document's `last_dispatched_signatures_by_document` entry and its top-level `thread_reoffers` record, clearing aggregate signature fields only when they can suppress the selected document, and preserving every unrelated recipient, per-document signature, launch ledger (WI-5208 dispatch_id-keyed), `last_launch`, `last_attempt`, and failure/backoff/circuit field.

### Non-blocking observations (carried forward; do not gate GO)

- Canonical record still over-scopes. WI-5203's `description` and the PAUTH `scope_summary` both still enumerate BOTH original defects, including the rejected neutral stand-down. Because the REVISED scope is a proper subset of that authorization, the project-linkage gate is satisfied and this does not gate GO - the same disposition the version-004 NO-GO assigned this observation. Recommendation for the implementation cycle: narrow the WI-5203 description through the governed backlog update so the canonical work record matches the accepted targeted-reoffer-only scope and does not continue to authorize the rejected design.
- Verifier guidance, field location: the implementation must clear `last_dispatched_signatures_by_document` at its true nesting (per-recipient, inside the recipient entry) and `thread_reoffers` at top level, matching the dispatcher-runtime/daemon schema. The VERIFIED-stage tests must assert byte-equivalence of every unrelated field per the acceptance criteria, not just the target document's removal.
- Verifier guidance, linked test: the proposal cites `TEST-11357`; the verifier should confirm that test exists and maps to the targeted-reoffer behavior (a MemBase `get_work_item` read did not surface a test link on WI-5203, likely a schema/accessor artifact rather than a genuine absence).
- Verifier guidance, lease refusal: the module already exposes `read_live_leases` / `_lease_is_live`; the new targeted reoffer must return `lease_held` and change nothing when the exact document has a live lease (proposed-behavior item 3, acceptance criterion 3).

## Specification Links (carried forward from proposal 005)

- SPEC-DISPATCHER-CONTROL-SURFACE-001 - governed CLI mutation over direct JSON edits.
- SPEC-CENTRALIZED-DISPATCH-SERVICE-001 - deterministic eligibility and operator-safe recovery.
- DCL-NO-ACTION-STATUS-SEMANTICS-001 - forbids the removed neutral stand-down; preserves corrected-verdict routing.
- GOV-FILE-BRIDGE-AUTHORITY-001 - role-correct append-only artifacts.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - complete spec linkage.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - project/WI/PAUTH/target-path linkage.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - spec-derived test execution before VERIFIED.
- GOV-STANDING-BACKLOG-001 - WI-5203/TEST-11357 tracked.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - traceable artifact graph.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 and DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - preserve the split from rejected semantics to the narrow lifecycle repair.

## Prior Deliberations

- DELIB-202666184 (this thread) - the corrected NO-GO at version 004 that this REVISED accepts; the REVISED's Finding Response maps 1:1 to its required corrections. Verified present via deliberation search.
- DELIB-202666183 (this thread) - the superseded version-002 GO. Verified present.
- DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS (owner decision) - the canonical NO-ACTION semantics under which component 2 was rejected; the REVISED honors it by removing that component.
- DELIB-202666173 (owner decision) - owner-directed six-harness governed proof plus correction of every discovered defect; authorizes the retained reoffer repair.
- DELIB-202666172 (owner decision) - authorizes the WI-5199 H functional-proof sequence the targeted reoffer serves.
- WI-5205 / commit 4abb6ed2 - the independently VERIFIED consumer-parity repair that correctly re-homed the rejected component.
- No conflicting prior decision found that would make the narrowed targeted-reoffer design non-compliant.

## Applicability Preflight

- packet_hash: `sha256:c1b95d8095956a5186db527896c697533c4ddb618d0f085d7e25a2c74f44c75e`
- bridge_document_name: `gtkb-wi5203-dispatch-targeted-reoffer-neutral-standdown`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-wi5203-dispatch-targeted-reoffer-neutral-standdown-005.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

- Clauses evaluated: 5 (must_apply: 3, may_apply: 2, not_applicable: 0)
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Clause preflight exit code: 0 (mandatory-gate pass)

| Clause | Applicability | Evidence |
| --- | --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL | must_apply | yes |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | must_apply | yes |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | must_apply | yes |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | may_apply | (not required) |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | may_apply | (not required) |

## Verification Expectations (post-implementation)

The post-implementation report must carry forward the spec links and provide executed evidence for:

1. `gt bridge dispatch reset --recipient <r> --document <d>` dry-run then apply: removes only the selected document's per-document signature and thread-reoffer entry, preserves unrelated recipient/document state byte-equivalently (including the WI-5208 dispatch_id-keyed launch ledger), and refuses a matching live lease (returns `lease_held`, changes nothing). (SPEC-DISPATCHER-CONTROL-SURFACE-001)
2. Missing recipient/document and partial argument pairs fail closed with deterministic JSON/CLI outcomes; existing soft/hard reset behavior remains compatible. (SPEC-CENTRALIZED-DISPATCH-SERVICE-001)
3. No dispatcher-runtime verdict or completion-semantics change is present (the rejected component stays out). (DCL-NO-ACTION-STATUS-SEMANTICS-001)
4. Only the LO reviewer writes GO/NO-GO/VERIFIED and Prime writes only NEW/REVISED/report states. (GOV-FILE-BRIDGE-AUTHORITY-001)
5. The exact pytest, `ruff check`, and `ruff format --check` commands in the proposal's verification plan execute clean against the implementation, with command-level output. (DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001)

Recommended commit type: `fix` (accepted) - adds a missing governed recovery operation for a demonstrated suppression defect; no new user-facing capability surface beyond the recovery flag.

## Review Independence

REVISED proposal author session context 019f5474-93a6-7f70-8e54-d6d8b0a31bb4 (Codex, harness A) differs from this reviewer session context 2026-07-12T09-14-35Z-loyal-opposition-B-236aec (Claude, harness B). Independent review satisfied. The prior version-002 GO and version-004 NO-GO were authored by two other Claude-B session contexts; a third Claude-B session reviewing the REVISED across distinct session contexts is the designed flow, not self-review.

## Root Boundary

All four target paths are in-root under the GT-KB project root and none touch the shared WI-5199 state (`groundtruth.db`, `harness-state/harness-registry.json`). project-root-boundary compliant.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
