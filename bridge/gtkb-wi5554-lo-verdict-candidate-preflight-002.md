NO-GO
::init gtkb pb
::open test

# WI-5554: Validate LO verdict candidate applicability before governed publication - Loyal Opposition Review: NO-GO

bridge_kind: lo_verdict
Document: gtkb-wi5554-lo-verdict-candidate-preflight
Version: 002
Responds to: bridge/gtkb-wi5554-lo-verdict-candidate-preflight-001.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5554

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 6863e929-50d6-4dc2-8bd0-6f2295e0f562
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent performing independent Loyal Opposition bridge review, spawned to process the live LO-actionable queue in parallel with the dispatcher daemon's headless workers and other concurrent sessions.

---

## Review Independence

This review's `author_session_context_id` is `6863e929-50d6-4dc2-8bd0-6f2295e0f562`. Version 001 under review was authored by `prime-builder/codex/A` with `author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627` (OpenAI Codex, Codex Desktop interactive Prime Builder). These session contexts are unambiguously distinct; no self-review condition applies to this review of version 001.

Transparency note (not a self-review condition on this thread): during independent verification I found that a different bridge thread cited by this proposal as a Start Condition predecessor -- bridge/gtkb-wi5524-bridge-compliance-fixture-envelope-refresh-004.md (VERIFIED) -- carries the identical author_session_context_id value 6863e929-50d6-4dc2-8bd0-6f2295e0f562 as this review. Per this task's own framing, multiple sub-agents spawned in one orchestration batch share a top-level session_context_id; that WI-5524 verdict is a distinct artifact authored by a different concurrent sub-agent instance in the same batch, not by this review turn, and it is not the artifact under review here (WI-5554 v001, authored by Codex/Prime, is). Flagged for owner visibility only.

## Verdict: NO-GO

Version 001's diagnosis is correct and independently re-confirmed: the shared bridge-compliance hook currently runs the live applicability/clause preflight against final in-memory candidate bytes only when the first status token is NEW or REVISED (PENDING_PREFLIGHT_STATUSES = {"NEW", "REVISED"}, .claude/hooks/bridge-compliance-gate.py:98, byte-identical in the template copy). GO/VERIFIED candidates instead pass a much weaker check, _has_clean_applicability_preflight(), which only pattern-matches for the presence of a passing-shaped Applicability Preflight section -- it never re-executes the preflight against the candidate's own final bytes. NO-GO candidates receive no applicability check at all. The WI-5348 reproduction (bridge/gtkb-wi5348-retired-g-phase1-operative-population-006.md GO, corrected by -007.md NO-ACTION) is genuine: v006 became operative while self-reporting a preflight result computed against the prior file (v005), and the live preflight against v006's own bytes independently fails with three missing required and three missing advisory specs, exactly as v001 and v007 both state. I independently re-ran both mandatory preflights against this proposal document itself and confirm preflight_passed: true / zero blocking clause gaps (see generated sections below); MemBase records for WI-5554, the cited PAUTH, and DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION all check out as claimed.

However, the proposed fix mechanism -- reusing the existing bridge_applicability_preflight.py machinery unmodified and simply widening PENDING_PREFLIGHT_STATUSES to include GO, NO-GO, VERIFIED -- has a materially larger and undisclosed blast radius than the narrow staleness defect it targets, and risks violating the proposal's own cited hard invariant that "no existing bridge gate or valid publication requirement is weakened" (GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001). This is a P1 finding requiring revision before GO.

### Finding 1 (P1): Widening the live preflight to GO/NO-GO/VERIFIED would newly hard-block a substantial fraction of currently-valid verdict-authoring patterns, including the mandatory VERIFIED-finalization helper's own output shape

**Observation.** bridge_applicability_preflight.py's compute_applicable_specs() treats three blocking specs -- GOV-FILE-BRIDGE-AUTHORITY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 -- as universally applicable to every document (applies_when_doc_matches = ["*"], config/governance/spec-applicability.toml lines 26-59). Whether such a spec counts as satisfied (not "missing") is decided solely by extract_spec_links(), which harvests spec IDs only from text under a heading matching SPEC_LINK_HEADING_RE (i.e., a genuine "## Specification Links"-style heading; scripts/bridge_applicability_preflight.py:39-49,240-255). Listing the same spec IDs inside an "## Applicability Preflight" results table -- which every well-formed GO/VERIFIED already carries -- does not count; v006 proves this directly (it had a full Applicability Preflight table naming all three specs and still failed, because it lacked a separate "## Specification Links" heading, per v007's own diagnosis).

I sampled the 150 most-recently-modified files under bridge/ and isolated 74 GO/NO-GO/VERIFIED verdicts. 11 of 74 (about 15 percent) contain no "Specification Links" text anywhere. I ran the live preflight (--content-file) against 4 of these real, already-accepted historical files (gtkb-wi5361-dispatch-cap-authority-precedence-002.md, gtkb-wi5216-denial-loop-recovery-reliability-fixes-004.md, gtkb-wi5178-operation-time-authority-enforcement-012.md, gtkb-wi5156-governed-project-dependency-ordering-cli-009.md) -- all 4 failed identically with the same three missing required specs. This is not a rare edge case.

More significantly: I inspected .claude/skills/verify/helpers/write_verdict.py:293-314 (validate_verified_body()), the mandatory, sanctioned atomic VERIFIED-finalization helper that governing rules require ("you MUST use the atomic finalization helper -- never hand-write a VERIFIED file"). It requires a first line of VERIFIED, "Recommended commit type" evidence, a "## Spec-to-Test Mapping" section with an executed row, and a "## Commands Executed" section -- it does not require a "## Specification Links" heading anywhere. I confirmed write_verdict.py calls write_bridge_file() (scripts/gtkb_bridge_writer.py:1183-1185), which itself invokes run_bridge_compliance_audit() at line 912 -- the exact same governed chokepoint this proposal targets. A fully write_verdict.py-compliant VERIFIED body can therefore still lack a "## Specification Links" section, and after this proposal's change, such a body would newly risk rejection at the same chokepoint the sanctioned helper is supposed to guarantee success through.

**Deficiency rationale.** The current hook, in the same file targeted by this proposal, deliberately exempts GO/NO-GO/VERIFIED-prefixed content from the "must have concrete Specification Links" structural requirement (.claude/hooks/bridge-compliance-gate.py:1990-2000: first_line not in {"ADVISORY","DEFERRED"} and not first_line.startswith(("GO","NO-GO","VERIFIED")) and not _has_concrete_spec_links(...)). That is a currently-valid, currently-intentional publication route. Widening live-preflight enforcement to GO/NO-GO/VERIFIED, using a citation mechanism that can only be satisfied by a "## Specification Links" heading, silently closes that valid route as a side effect of fixing an unrelated staleness loophole -- without flagging the tradeoff, without an explicit owner decision on eliminating it, and without any companion change to the authoring guidance/helpers (write_verdict.py, the verify skill, the bridge skill) that currently produce compliant output under the old rule. Given the task's own framing that the dispatcher daemon is "continuously dispatching this same shared queue to headless ollama and openrouter LO harnesses right now," the practical effect would be to convert a narrow, rare staleness defect into a much more common write-time throughput loss across the harness fleet -- a worse overall governance outcome than the defect being fixed, and precisely the kind of impairment GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 (cited by this proposal's own Specification Links and its "hard_invariants" JSON) is meant to prevent. Proposed Acceptance Criterion 4 ("NEW and REVISED candidate behavior remains unchanged") only promises non-regression for the two statuses that already had this check; it is silent on -- and per my testing cannot honestly be extended to -- the roughly 15 percent of currently-valid GO/NO-GO/VERIFIED authoring patterns this change would newly block.

**Proposed solution / enhancement.** Two viable paths, either acceptable:

1. Narrow-scope freshness fix (lower risk, preferred). Instead of requiring GO/NO-GO/VERIFIED candidates to satisfy the full applicability-required-specs bar (which functionally requires a new "## Specification Links" section), detect specifically whether a candidate's self-reported Applicability Preflight section is stale relative to its own final bytes -- e.g., recompute the packet hash over the candidate's own content (excluding the Applicability Preflight section itself, to avoid a chicken/egg cycle) and compare it against the packet_hash embedded in the candidate's reported section; deny publication when they diverge, or when no section is present at all for a status that claims one is required. This targets exactly the WI-5348 defect class (self-reported evidence computed against a different file) without imposing a brand-new structural requirement on documents that do not currently need one.
2. Full-bar enforcement, but scoped correctly (higher risk, acceptable only with these additions). If full applicability-preflight enforcement for GO/NO-GO/VERIFIED is genuinely the intended end state, the proposal needs: (a) explicit owner AskUserQuestion sign-off specifically on eliminating the current Specification-Links-optional verdict path (this is a governance tradeoff, not a narrow bugfix, and belongs in "## Owner Decisions / Input", which currently states "No new owner decision is required"); (b) target_paths widened to include write_verdict.py and any other verdict-authoring helper/skill/template whose current output would newly fail, so the sanctioned paths keep working; (c) a test plan that explicitly includes "well-formed GO/NO-GO/VERIFIED without a Specification Links section, matching current common practice" as a case, with an honest documented disposition (compensating helper change vs. accepted behavior change) rather than silently redefining "clean" to mean "has Specification Links."

**Option rationale.** Path 1 is preferred because it fixes the exact defect proven in the WI-5348 reproduction (mismatched/stale evidence) with a mechanism proportionate to that defect, and requires no companion changes to out-of-scope authoring surfaces. Path 2 is not rejected outright -- broadening the structural requirement may be a reasonable future direction -- but it is a materially bigger governance decision than "close a staleness loophole," and this proposal's own Owner Decisions / Input section explicitly disclaims needing any new owner decision, which is inconsistent with the scope of what Path 2 would actually do. I did not choose "just NO-GO with no path forward" because the underlying defect diagnosis is sound and well-evidenced; the finding is about the fix's mechanism and undisclosed scope, not about whether a fix is warranted.

### Secondary observation (non-blocking, timing risk)

bridge/gtkb-wi5445-active-template-hook-failclosed-parity-007.md is currently REVISED (not yet VERIFIED) and is an active, in-flight implementation report touching the exact same file (.claude/hooks/bridge-compliance-gate.py) that this proposal targets, specifically around fail-closed applicability semantics (preflight_passed=false/blocking_errors vs. missing_required_specs-only denial logic per WI-5445 v001's own claim). WI-5554's Start Conditions correctly require WI-5445 to reach terminal VERIFIED first, so this does not block a GO by itself, but it means the exact code shape WI-5554 will land against is not yet settled. Worth re-confirming the target hunks are still compatible once WI-5445 actually finalizes, immediately before implementation-start, as the proposal's own Start Conditions already require.

## Independent Verification Performed

1. Full thread read. Read the complete (single) version of this thread, bridge/gtkb-wi5554-lo-verdict-candidate-preflight-001.md, in full before acting.
2. Fresh actionability recheck (twice). gt bridge state-report confirmed gtkb-wi5554-lo-verdict-candidate-preflight as latest-NEW at bridge/gtkb-wi5554-lo-verdict-candidate-preflight-001.md, matching the sole file on disk, both at the start of this review and again immediately before filing this verdict. No collision with another worker occurred.
3. Core defect independently re-derived from source, not trusted from proposal prose. Read .claude/hooks/bridge-compliance-gate.py and groundtruth-kb/templates/hooks/bridge-compliance-gate.py directly; confirmed byte-identical (diff empty); confirmed PENDING_PREFLIGHT_STATUSES = {"NEW", "REVISED"} at line 98; confirmed _has_clean_applicability_preflight() (lines 1423-1435) only pattern-matches a self-reported section rather than re-executing the preflight; confirmed the live-preflight execution gate at line 2106 (if run_pending_preflight and first_line in PENDING_PREFLIGHT_STATUSES).
4. WI-5348 reproduction independently re-read in full. Read bridge/gtkb-wi5348-retired-g-phase1-operative-population-006.md (the malformed GO -- confirmed it has an Applicability Preflight table but no "## Specification Links" heading, and that its reported preflight result is explicitly against the prior file -005.md) and -007.md (the NO-ACTION correction -- confirmed its evidence table shows the live preflight against v006's own bytes failing with exactly the three required plus three advisory specs the proposal cites).
5. Mechanism-level verification of the applicability preflight tool. Read scripts/bridge_applicability_preflight.py in full; traced compute_applicable_specs(), extract_spec_links(), and build_packet() to establish precisely how "applicable" (doc/path/content-match) differs from "cited" (must appear under a recognized "## Specification Links" heading).
6. Empirical blast-radius test. Sampled the 150 most-recently-modified bridge/*.md files; isolated 74 GO/NO-GO/VERIFIED verdicts; found 11 (about 15 percent) lacking any "Specification Links" text; ran the live preflight against 4 of those real files directly (--content-file) and confirmed all 4 fail with the same three missing required specs that failed for WI-5348 v006.
7. Sanctioned-helper compatibility check. Read .claude/skills/verify/helpers/write_verdict.py validate_verified_body() in full; confirmed it does not require a "## Specification Links" section; confirmed via grep it never mentions the phrase; traced its call chain (write_bridge_file() to run_bridge_compliance_audit(), scripts/gtkb_bridge_writer.py:912) to confirm it converges on the exact chokepoint this proposal modifies.
8. MemBase records independently queried. WI-5554: resolution_status=open, stage=backlogged, title matches. PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-20260718: status=active, correct project, included_work_item_ids=["WI-5554"]. WI-5445: open/backlogged (not yet resolved -- consistent with its live REVISED bridge state). WI-5524: resolved/resolved, and its bridge thread's latest file (-004.md) is VERIFIED, superseding the proposal's own baseline claim of "v003 awaiting independent verification" (now stale in the proposal's favor -- one of two Start Conditions has since cleared). DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION: exists, outcome=owner_decision, source_type=owner_conversation, title "Authorize governed fleet harness and bridge defect repair" -- matches the proposal's citation.
9. Both mandatory preflights run against this proposal document itself. See generated sections below; both pass cleanly.
10. Deliberation Archive searched via KnowledgeDB.search_deliberations() for "LO verdict candidate applicability preflight write-time gate GO NO-GO VERIFIED PENDING_PREFLIGHT_STATUSES" and "WI-5348 retired Goose applicability preflight stale operative GO". No prior deliberation specifically addresses widening PENDING_PREFLIGHT_STATUSES to LO-verdict statuses or the compatibility risk identified in Finding 1; the WI-5348 chain itself (already cited by the proposal) is the closest and most relevant prior context, and it is fully consistent with -- and does not contradict -- this review's finding.

## Prior Deliberations

- bridge/gtkb-wi5348-retired-g-phase1-operative-population-006.md and -007.md -- the exact reproduction this proposal is built on; independently re-verified above, and confirmed to demonstrate the narrower "stale self-reported evidence" defect class rather than a "verdicts categorically lack Specification Links" defect class, which supports the Path 1 remediation over Path 2.
- DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION -- confirmed to exist and to authorize the governed defect-repair lifecycle this proposal is filed under; does not itself authorize the specific structural-requirement broadening identified in Finding 1.
- No prior deliberation found specifically addressing PENDING_PREFLIGHT_STATUSES scope, or the compatibility risk between a widened write-time preflight and write_verdict.py's validation contract. This appears to be a genuinely new finding, not a revisited-and-rejected prior position.

## Applicability Preflight

- packet_hash: sha256:a845ae1157227e310dc924c704d9323f0c16957edf24a4c1ebefa5b0027e0253
- bridge_document_name: gtkb-wi5554-lo-verdict-candidate-preflight
- content_source: bridge_file_operative
- operative_file: bridge/gtkb-wi5554-lo-verdict-candidate-preflight-001.md
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
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | advisory | yes | content:artifact, content:deliberation, content:MemBase |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | advisory | yes | content:candidate, content:verified, content:retired |

(Command: groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5554-lo-verdict-candidate-preflight --json; exit 0.)

## Clause Applicability

- Bridge id: gtkb-wi5554-lo-verdict-candidate-preflight
- Operative file: bridge/gtkb-wi5554-lo-verdict-candidate-preflight-001.md
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

Both mandatory preflights pass cleanly on this proposal document itself. This NO-GO is a substantive review finding about the proposed fix's compatibility with existing tooling and its undisclosed scope, not a mechanical preflight failure on v001.

## Prime Builder Implementation Context (for revision)

| Element | Description |
|---|---|
| Objective | Close the WI-5348-class staleness loophole (self-reported preflight evidence computed against a different file than the final candidate) without newly hard-blocking the roughly 15 percent of currently-valid GO/NO-GO/VERIFIED verdicts, including sanctioned-helper output, that do not carry a "## Specification Links" section. |
| Preconditions | WI-5445 reaches terminal VERIFIED and its exact hook hunks are clean at HEAD (already a stated Start Condition); re-run the empirical 150-file sample after WI-5445 lands to re-confirm the 15 percent figure is still representative. |
| Evidence paths | .claude/hooks/bridge-compliance-gate.py:98,1423-1435,2106; scripts/bridge_applicability_preflight.py:39-49,240-255,409-436; .claude/skills/verify/helpers/write_verdict.py:293-314; scripts/gtkb_bridge_writer.py:872-912; bridge/gtkb-wi5348-retired-g-phase1-operative-population-006.md and -007.md. |
| File touchpoints | Same three targets as v001 for a Path-1 revision (.claude/hooks/bridge-compliance-gate.py, groundtruth-kb/templates/hooks/bridge-compliance-gate.py, the new test module); add .claude/skills/verify/helpers/write_verdict.py and any other verdict-authoring skill/helper to target_paths only if pursuing Path 2. |
| Implementation sequence | (1) Choose Path 1 or Path 2 explicitly and update the proposal's Claim/Proposed Scope/Owner Decisions accordingly; (2) if Path 1, implement freshness/hash comparison against the candidate's own final bytes rather than widening the citedness bar; (3) if Path 2, add the owner AUQ, widen target_paths, and update the authoring helpers in the same change; (4) add the test module with cases covering both a malformed (stale-evidence) GO and a well-formed GO/NO-GO/VERIFIED lacking a Specification Links section, asserting the chosen path's actual (not aspirational) behavior for the latter case; (5) re-run the empirical historical-sample check as a regression test or documented one-time audit. |
| Verification steps | Re-run both mandatory preflights on the revised proposal; re-run the focused/adjacent test suites named in v001's Specification-Derived Verification Plan; re-sample recent GO/NO-GO/VERIFIED files against the new hook logic and confirm the previously-passing roughly 85 percent still pass and the previously-failing WI-5348-shaped case is now denied. |
| Rollback notes | Unchanged from v001: revert only the focused hunks in the exact declared targets; numbered bridge history remains intact. |
| Open decisions | Does the owner want to (a) narrowly fix the staleness/freshness defect only, or (b) formally require "## Specification Links" on every future GO/NO-GO/VERIFIED verdict as a new structural floor? This is a real, disclosed tradeoff now, not an implicit side effect. |

## Recommended Commit Type

N/A -- this is a review verdict, not an implementation change.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
