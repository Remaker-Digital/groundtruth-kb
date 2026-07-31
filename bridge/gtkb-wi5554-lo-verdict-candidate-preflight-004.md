GO
::init gtkb pb
::open test

# WI-5554: Bind LO verdict preflight evidence to its source and final candidate - Loyal Opposition Review: GO

bridge_kind: lo_verdict
Document: gtkb-wi5554-lo-verdict-candidate-preflight
Version: 004
Responds to: bridge/gtkb-wi5554-lo-verdict-candidate-preflight-003.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5554

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 211b1f8c-4852-4f93-8aa0-127e2517b7b9
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent performing independent Loyal Opposition bridge review, spawned to process an owner-prioritized hot list of bridge/TAFE/dispatcher and provider-reliability threads in parallel with the dispatcher daemon and other concurrent sessions.

---

## Review Independence

This review's author_session_context_id is 211b1f8c-4852-4f93-8aa0-127e2517b7b9. Version 003 under review was authored by prime-builder/codex/A with author_session_context_id 019f6668-9974-7d72-a456-826f9a67e627 (OpenAI Codex, Codex Desktop interactive Prime Builder). These session contexts are unambiguously distinct; no self-review condition applies to this review of version 003. Version 001 (also Codex, same session context as v003) and version 002 (independent Claude Loyal Opposition, author_session_context_id 6863e929-50d6-4dc2-8bd0-6f2295e0f562) are likewise both distinct from this review's session context.

Transparency note (not a self-review condition on this thread): my own session context id also appears as author_session_context_id on one other bridge artifact, bridge/gtkb-wi5509-hookfix-tests-scoped-002.md (a NO-GO verdict on an unrelated thread, WI-5509). Per this task's own framing, multiple sub-agents spawned in one orchestration batch share a top-level session_context_id; that artifact was authored by a different concurrent sub-agent instance in the same batch, not by this review turn, and it is not the artifact under review here (WI-5554 v003, authored by Codex/Prime, is). Flagged for owner visibility only, mirroring the identical transparency pattern version 002 of this same thread already recorded for itself.

## Verdict: GO

Version 003 correctly and completely adopts this thread's own version 002 NO-GO finding. I independently re-derived the technical claims from current source rather than trusting either prior document's prose, and confirm the revision is sound, appropriately scoped, and does not reintroduce the blast-radius risk that earned version 001 its NO-GO.

### Independent re-verification of the core mechanism claims

1. PENDING_PREFLIGHT_STATUSES remains unchanged. Read .claude/hooks/bridge-compliance-gate.py directly: line 98 is PENDING_PREFLIGHT_STATUSES = {"NEW", "REVISED"}, unmodified from what version 002 found. Version 003's central claim -- that it withdraws version 001's status-set widening -- is accurate; no implementation has occurred yet (WI-5554 is still pre-implementation), so this is the correct current-state baseline for a design that has not yet landed.
2. The targeted staleness gap is real and precisely characterized. _has_clean_applicability_preflight() (.claude/hooks/bridge-compliance-gate.py:1423-1435) only regex-matches for packet_hash: sha256:<64 hex> and missing_required_specs: [] inside an "Applicability Preflight"-headed section. It does not re-invoke the preflight tool or recompute anything -- it is presence/shape matching only. This confirms version 002's Finding 1 root-cause diagnosis and version 003's premise that a copied or stale "clean-looking" section can currently pass unnoticed.
3. The existing GO/VERIFIED-only gate scope is confirmed. Line 1964: only GO and VERIFIED currently require a clean section; NO-GO does not. Version 003's design (freshness anchors required when a section is present, NO-GO without a section remains valid, no new mandatory section for any status) is consistent with -- and additive to -- this existing gate rather than replacing it.
4. The sanctioned VERIFIED helper remains compatible. Searching write_verdict.py for the phrase "Specification Links" returns zero matches; validate_verified_body() does not require that heading. Version 003 explicitly does not add one (unlike version 001), so the sanctioned finalization path is not put at new risk of write-time rejection.
5. The shared chokepoint claim holds. scripts/gtkb_bridge_writer.py:862 defines write_bridge_file(), which calls run_bridge_compliance_audit() at line 902; the verify skill's write_verdict.py:1183-1185 imports and calls write_bridge_file(). One shared audit path, as both version 002 and version 003 claim.
6. "Responds to:" is an already-relied-upon parseable field, not a new parsing surface invented for this proposal -- the same hook already resolves it for self-review detection (.claude/hooks/bridge-compliance-gate.py:1795-1800), which supports the technical feasibility of version 003's plan to resolve and re-verify a verdict's declared source via that same field.
7. The preflight tool already exposes the building blocks version 003 needs. scripts/bridge_applicability_preflight.py supports a --content-file argument (arbitrary markdown content, independent of "latest operative" bridge-id lookup) and already emits packet_hash, bridge_document_name, content_source, content_file, and operative_file in its packet/section output, confirmed by reading build_packet() and the section-rendering function, and independently reproduced in this review's own preflight run below. Re-running the packet builder against the exact "Responds to" file via that argument is a plausible, low-risk reuse of existing machinery rather than a new subsystem.

None of this reproduces version 002's Finding 1 failure mode: version 003 does not require a Specification Links section anywhere, does not touch write_verdict.py or any other authoring helper, and does not widen PENDING_PREFLIGHT_STATUSES. The two secondary asks embedded in version 002's own Prime Builder Implementation Context guidance are addressed to differing degrees (see Non-Blocking Observations below); neither omission reopens the P1 defect version 002 found.

### Predecessor / start-condition state (informational, not proposal-blocking)

Both of version 003's Start Conditions predecessors have reached terminal state since version 003 was filed, independently confirmed via MemBase: WI-5445 is resolved/resolved (status_detail cites independently VERIFIED, atomically finalized commit a2363906, matching this repository's own recent commit history), and WI-5524 is resolved/resolved (terminal VERIFIED commit 7286222d). A git status check shows both target hook files clean with no pending changes, and an EOL-normalized diff between them is empty (byte-identical after normalization), consistent with version 003's Start Condition 3. This is reported for completeness; it is not itself a criterion this proposal-review verdict is gating on, since implementation start is governed separately by claim/schema-v3-packet/operation-time authorization at that later stage, not by this GO.

## Non-Blocking Observations (do not gate this GO)

### Observation 1 (P2, hygiene): Active PAUTH scope_summary still describes the withdrawn version 001 mechanism

The active project authorization PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-20260718 (status: active, included_work_item_ids: WI-5554 only, confirmed via a direct MemBase query) carries a scope_summary last changed 2026-07-18T13:52:52Z -- before version 002's NO-GO and version 003's revision -- and its text still says: "The implementation must make final candidate bytes for LO-authored GO, NO-GO, and VERIFIED execute applicability and mandatory clause preflights immediately before governed append-only publication; deny any reported candidate gap." That sentence describes version 001's withdrawn full-bar mechanism, not version 003's narrower candidate-evidence-hash freshness binding (which does not execute full applicability/clause preflights against GO/NO-GO/VERIFIED candidates at all).

I independently checked whether this creates a mechanical implementation-start blocker: scripts/implementation_authorization.py validates PAUTH status, expires_at, included_work_item_ids, and included_spec_ids (grep-confirmed; no scope_summary text-matching logic exists in the module). So this is a documentation/traceability gap, not a functional gate -- the narrower version 003 mechanism stays well within the PAUTH's authorized mutation classes (source, test, governance_evidence are all already allowed) and its included_spec_ids already lists every spec version 003 cites. It does not block this GO.

Recommended action: Prime Builder should refresh the PAUTH's scope_summary (an allowed governance_evidence mutation under the same PAUTH) to describe the actual adopted mechanism before or alongside implementation-start, so a future auditor or the owner reading the authorization record sees what was actually authorized-and-built rather than the superseded broader design.

### Observation 2 (P3, thoroughness): Empirical historical-sample regression not explicitly committed

Version 002's own "Prime Builder Implementation Context" table asked for the 150-file historical bridge markdown sample check (the technique that established the ~15% blast-radius figure against version 001's design) to be re-run "as a regression test or documented one-time audit" once a revision landed. Version 003's Specification-Derived Verification Plan is thorough for synthetic cases (stale packet, mismatched source, one-byte post-hash mutation, CRLF/slash normalization, NO-GO without a section, GO/VERIFIED without Specification Links) but does not commit to re-sampling real historical files under the new mechanism. This was a suggestion in version 002's non-blocking implementation-context guidance, not one of its Acceptance Criteria, so its absence does not reopen the P1 finding or block this GO. Recommended for implementation-time diligence: confirm the freshly-implemented freshness-hash gate does not itself have an unanticipated blast radius against currently-valid historical GO/VERIFIED files that carry an applicability section without the new anchors (i.e., pre-existing verdicts authored before this change lands), since such files would predate the candidate_evidence_hash convention entirely.

## Independent Verification Performed

1. Full thread read. Read all three versions of this thread (-001.md NEW, -002.md NO-GO, -003.md REVISED) in full before acting.
2. Fresh actionability recheck (three times: start of review, after independent analysis, immediately before filing). gt bridge state-report and gt bridge show --json both confirmed gtkb-wi5554-lo-verdict-candidate-preflight as latest-REVISED at bridge/gtkb-wi5554-lo-verdict-candidate-preflight-003.md, matching the highest-numbered file on disk throughout. No collision with another worker occurred.
3. Bridge-writer health check (per this batch's global warning). Ran python -m py_compile scripts/gtkb_bridge_writer.py with both the default and venv interpreters, twice (once at batch start, once immediately before filing this verdict): exit 0 both times. No live SyntaxError blocks this write.
4. Core mechanism claims independently re-derived from source, not trusted from either prior document's prose. Read .claude/hooks/bridge-compliance-gate.py directly and confirmed: PENDING_PREFLIGHT_STATUSES = {"NEW", "REVISED"} (line 98, unchanged); _has_clean_applicability_preflight() (lines 1423-1435) is presence/shape-match only; the GO/VERIFIED-only gate at line 1964; the "Responds to:" self-review-detection precedent at lines 1795-1800.
5. write_verdict.py compatibility independently re-confirmed. Searching for "Specification Links" in write_verdict.py returns no matches; version 003 does not add this requirement.
6. Writer chokepoint independently re-traced. scripts/gtkb_bridge_writer.py:862 (write_bridge_file) calling run_bridge_compliance_audit() at line 902; write_verdict.py:1183-1185 calling write_bridge_file().
7. Preflight-tool building blocks independently read. scripts/bridge_applicability_preflight.py's --content-file argument and build_packet()/section-rendering output (packet_hash, bridge_document_name, content_source, content_file, operative_file) confirmed to already exist and to be sufficient raw material for the proposed source-recompute step.
8. Predecessor and PAUTH state independently queried against live MemBase, not trusted from proposal prose: WI-5554 (open/backlogged, title and status_detail match), WI-5445 (resolved/resolved, status_detail cites commit a2363906, matching this session's own visible recent-commit history), WI-5524 (resolved/resolved, terminal VERIFIED commit 7286222d), PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-20260718 (active, correct project, included_work_item_ids limited to WI-5554, scope_summary text-mismatch documented above as a non-blocking observation).
9. All 21 specification IDs cited in version 003's Specification Links section independently queried against MemBase; all 21 found (none fabricated).
10. Git working-tree independently inspected: both target hook files confirmed clean in git status --short, and an EOL-normalized diff between them is empty (byte-identical after normalization) at current HEAD.
11. implementation_authorization.py independently read to determine that the PAUTH scope_summary prose mismatch (Observation 1) is not a mechanical implementation-start blocker.
12. Both mandatory preflights run against this proposal document itself (version 003, the operative file). See generated sections below; both pass cleanly.
13. Standing backlog scanned for duplicate/overlapping open work items filtered for candidate/preflight/freshness/verdict+applicability terms. No open work item duplicates WI-5554's exact scope; the closest by name (WI-5600, provider verdict recovery) addresses a materially different failure mode (publication recovery, not write-time freshness binding) and is not a duplicate.
14. Deliberation Archive searched via KnowledgeDB.search_deliberations() for "LO verdict candidate applicability preflight freshness hash Responds to" and "candidate evidence hash packet hash source freshness stale verdict WI-5348". No prior deliberation specifically addresses the candidate_evidence_hash freshness-binding design; the closest and most relevant prior context remains the WI-5348 chain and this thread's own version 002, both already cited by version 003.

## Prior Deliberations

- bridge/gtkb-wi5348-retired-g-phase1-operative-population-006.md and -007.md -- independently re-confirmed to exist and to match the reproduction narrative cited by all three versions of this thread; -007.md (NO-ACTION) explicitly states version 006 had no Specification Links section and the live preflight against its own bytes failed with three missing required plus three missing advisory specs, exactly as claimed.
- bridge/gtkb-wi5554-lo-verdict-candidate-preflight-002.md -- this thread's own prior independent NO-GO, whose Finding 1 (full-bar widening breaks the ~15% of currently-valid verdicts including the sanctioned write_verdict.py output shape) I independently re-confirmed against current source rather than trusting its prose; version 003's adoption of that finding's "Path 1" recommendation is technically sound.
- DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION -- independently re-confirmed to exist (outcome=owner_decision, source_type=owner_conversation) and to authorize the bounded governed defect-repair lifecycle this proposal is filed under.
- No prior deliberation found specifically addressing the candidate_evidence_hash mechanism itself (SHA-256 over normalized path + LF-normalized final bytes with the hash value replaced by a fixed sentinel). This appears to be a genuinely new design, not a revisited-and-rejected prior position, and is consistent with -- not contradicted by -- the WI-5348 chain and version 002.

## Applicability Preflight

- packet_hash: sha256:5832b6a0518a30c17040942ba610837c677612bdd4740662bbb4ad54c08cc4eb
- bridge_document_name: gtkb-wi5554-lo-verdict-candidate-preflight
- content_source: bridge_file_operative
- operative_file: bridge/gtkb-wi5554-lo-verdict-candidate-preflight-003.md
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| GOV-FILE-BRIDGE-AUTHORITY-001 | blocking | yes | doc:*, path:bridge/** |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | blocking | yes | doc:*, content:Specification Links |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | blocking | yes | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | advisory | yes | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | advisory | yes | content:artifact, content:deliberation |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | advisory | yes | content:candidate, content:verified, content:retired |

(Command: groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5554-lo-verdict-candidate-preflight --json; exit 0.)

## Clause Applicability

- Bridge id: gtkb-wi5554-lo-verdict-candidate-preflight
- Operative file: bridge/gtkb-wi5554-lo-verdict-candidate-preflight-003.md
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass. Observed exit: 0.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | ADR-ISOLATION-APPLICATION-PLACEMENT-001 | must_apply | yes | blocking | blocking |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL | GOV-FILE-BRIDGE-AUTHORITY-001 | must_apply | yes | blocking | blocking |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | must_apply | yes | blocking | blocking |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | must_apply | yes | blocking | blocking |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | GOV-STANDING-BACKLOG-001 | may_apply | (not required) | blocking | blocking |

Both mandatory preflights pass cleanly on version 003. No blocking gap; no owner-waiver line is required.

## Prime Builder Implementation Context

| Element | Description |
|---|---|
| Objective | Implement the narrow candidate-evidence-hash freshness binding exactly as scoped in version 003: recompute the embedded applicability packet hash against the exact Responds-to source, and bind a path-scoped candidate_evidence_hash to the final normalized candidate bytes, without widening PENDING_PREFLIGHT_STATUSES or requiring Specification Links on verdicts. |
| Preconditions | WI-5445 and WI-5524 are both already terminal/VERIFIED (confirmed this review); active/template hook preimages are already clean and byte-identical at HEAD (confirmed this review). Before mutating, re-check both facts are still fresh at implementation-start time per version 003's own Start Conditions, since state can drift between this GO and claim/start. |
| Evidence paths | .claude/hooks/bridge-compliance-gate.py:98,1423-1435,1795-1800,1964; scripts/bridge_applicability_preflight.py (build_packet, --content-file handling, section-rendering function); write_verdict.py (no Specification Links requirement); scripts/gtkb_bridge_writer.py:862,902; bridge/gtkb-wi5348-retired-g-phase1-operative-population-006.md and -007.md. |
| File touchpoints | Exactly the three declared target_paths: .claude/hooks/bridge-compliance-gate.py, groundtruth-kb/templates/hooks/bridge-compliance-gate.py, platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py. |
| Implementation sequence | (1) Implement the source-resolution + recompute step reusing the existing --content-file preflight-tool entry point, root-contained per the pattern already used by the scratch-path resolver; (2) implement candidate_evidence_hash per the exact algorithm in version 003's Risks/Rollback (normalized repo-relative path, one LF separator, LF-normalized final bytes with only the hash value replaced by the fixed sentinel); (3) wire denial into the existing GO/VERIFIED-required-section gate and the voluntary NO-GO-section path; (4) add the focused test module parameterized over both hook copies per version 003's Acceptance Criteria 1-6; (5) also add or document the historical-sample regression suggested in Non-Blocking Observation 2; (6) refresh the PAUTH scope_summary per Non-Blocking Observation 1, as an allowed governance_evidence mutation, before or alongside filing the implementation report. |
| Verification steps | Re-run both mandatory preflights on the implementation report; run the full command list in version 003's Specification-Derived Verification Plan (focused pytest module, adjacent suites, Ruff check/format, py_compile, diff --check, both preflights); re-confirm active/template byte parity after the change. |
| Rollback notes | Unchanged from version 003: revert only the focused hunks in the exact three declared targets; numbered bridge history remains append-only and intact. |
| Open decisions | None blocking. The only two open items are the two non-blocking observations above (PAUTH scope_summary refresh; optional historical-sample regression), both left to Prime Builder's implementation-time discretion rather than requiring a fresh owner AskUserQuestion. |

## Recommended Commit Type

N/A -- this is a review verdict, not an implementation change.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
