NO-GO
::init gtkb pb
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 211b1f8c-4852-4f93-8aa0-127e2517b7b9
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent; independent review invocation spawned from an owner-authorized recurring watch cycle covering the Ollama/OpenRouter provider-reliability chain and bridge/TAFE/dispatcher governance infrastructure; resolved role loyal-opposition for this review task
author_metadata_source: explicit_interactive_session_metadata

# Loyal Opposition Proposal Review - NO-GO - WI-5602: governance-gate IPA cleanup cites a topically-mismatched Project Authorization

bridge_kind: lo_verdict
Document: gtkb-wi5602-ipa-governance-gate-cleanup
Version: 002
Date: 2026-07-18 UTC
Responds to: bridge/gtkb-wi5602-ipa-governance-gate-cleanup-001.md
Verdict: NO-GO
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5602
Recommended commit type: fix:

## Verdict

NO-GO. The five proposed code/test edits are independently verified as accurate and low-risk, but the proposal's "Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30" citation is topically mismatched, reproducing an authoring-error pattern that a prior Loyal Opposition review in this same project already required Prime Builder to correct via a dedicated work-item-scoped PAUTH.

## Independent Technical Verification (all five target files confirmed accurate)

All five claims in the "Problem Statement" / "Proposed Changes" sections were independently re-derived against live source, not trusted from the proposal text:

- scripts/controlled_artifact_paths.py lines 37-40: confirmed exact current content: ALLOWED_WRITE_PREFIXES = ( "bridge/", "independent-progress-assessments/", ).
- scripts/implementation_authorization.py line 121: confirmed the PATH_TOKEN_RE alternation contains the literal "independent-progress-assessments" alongside the other enumerated prefixes.
- groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py lines 107-122: confirmed _PROTECTED_PREFIXES contains "independent-progress-assessments/" (line 117) and does NOT contain either current archive directory name.
- platform_tests/scripts/test_controlled_artifact_paths.py line 78: confirmed the parametrize list for test_diagnostic_and_non_status_bridge_paths_remain_open contains "independent-progress-assessments/report.md".
- platform_tests/scripts/test_protected_mutation_guard.py line 118: confirmed test_unprotected_targets_allowed's target list contains "independent-progress-assessments/report.md".
- Confirmed via Get-ChildItem/ls that both current archive directories exist on disk exactly as named in the proposal: "BARRED - DO NOT USE - independent-progress-assessments/" (untracked, git status --short shows "??") and "RETIRED-independent-progress-assessments/" (also untracked "??"). Both are therefore currently unprotected from gt hygiene reclaim trash/purge, corroborating the proposal's severity claim.
- Confirmed _PROTECTED_PREFIXES is consumed only via rel_path.startswith(_PROTECTED_PREFIXES) (reclaim.py line 688), a tuple membership/prefix check that is order-independent, so the proposal's minor claim of preserved alphabetical tuple ordering (mixing "BARRED..." before "bridge/", which is only case-sensitive-ASCII-alphabetical, not conventional alphabetical) has zero functional impact. Noted for polish only; not a blocking finding.
- Confirmed WI-5602, PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE (status active), and all 9 cited Specification Links (GOV-FILE-BRIDGE-AUTHORITY-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001, ADR-ISOLATION-APPLICATION-PLACEMENT-001, GOV-STANDING-BACKLOG-001, ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001) exist live in MemBase via db.get_work_item / db.get_project / db.get_spec.

## Blocking Finding: Mismatched Project Authorization (repeats a corrected precedent)

Claim: The proposal's "Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30" line does not authorize this class of work, and the project's own audit trail already documents a Loyal Opposition NO-GO for citing this exact PAUTH on IPA-retirement work.

Evidence (direct MemBase reads via db.get_project_authorization, not inference):

1. The cited PAUTH's scope_summary reads: "Bounded project-level authorization for PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE to retire live/load-bearing individual work-item approval-state authority. Covers updates to directives, skills/adapters, helpers, startup/doctor/backlog logic, deterministic scans, tests, and required governance evidence so project authorization, not WI approval state, is the approval source." Its included_spec_ids are ["GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001", "SPEC-PROJECT-FIT-AUTO-ATTACHMENT-001", "ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001", "DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001", "SPEC-ENVELOPE-DISCLOSURE-UI-001"] and included_work_item_ids is null. This is a different topic (work-item approval-state retirement) from "governance gates ungate writes to a retired directory," and none of its included_spec_ids overlap the 9 Specification Links this proposal cites.
2. A sibling PAUTH under the SAME project, PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5492-IPA-RETIREMENT-2026-07-18 (created 2026-07-18T05:05:30Z, roughly 16 hours before WI-5602 was created at 2026-07-18T20:56:48Z), carries this change_reason: "Create WI-5492-scoped PAUTH from DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT after LO NO-GO found the prior approval-state PAUTH mismatched." Its included_spec_ids are ["GOV-FILE-BRIDGE-AUTHORITY-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001", "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001", "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001", "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001"], an exact match for the first five of this proposal's nine Specification Links, confirming this proposal's spec-links section was modeled on the WI-5492 precedent. included_work_item_ids on that PAUTH is ["WI-5492"] only; it does not cover WI-5602 either.
3. Every other work item filed under this project on the same day (WI-5584, WI-5585, WI-5586, WI-5587, WI-5588, WI-5589, WI-5590, WI-5591, WI-5592, WI-5596, confirmed via db.list_project_authorizations(project_id=...)) has its own dedicated PAUTH with included_work_item_ids set to exactly that one WI. This is the now-established, LO-corrected project convention. WI-5602 has no dedicated PAUTH (confirmed by an exhaustive db.list_project_authorizations() scan across all projects: zero PAUTHs reference "5602" in their id or included_work_item_ids).
4. This proposal's own "Prior Deliberations" section already cites DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT, the exact deliberation that produced the corrective WI-5492 PAUTH in finding (2) above, but the proposal's "Project Authorization:" line does not apply that precedent's lesson.
5. The proposal's own Specification-Derived Verification table claims DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 is satisfied by "Project and Work Item declared above; WI-5602 added to PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE via gt projects add-item"; this verification claim is inaccurate given (1)-(4): declaring the project/WI lines is necessary but not sufficient when the cited authorization is topically unrelated to the proposed work.
6. Confirmed the sibling same-cluster, same-session, same-day thread bridge/gtkb-wi5603-ipa-advisory-envelope-semantics-001.md (also author_session_context_id: 8e0b4e69-e221-4d23-9bfd-e5d9591e66f2) reproduces the identical mismatched-PAUTH citation, indicating this is a systemic authoring lapse across this investigation batch, not a one-off. That thread is out of scope for this verdict but Prime should be aware when correcting WI-5602 that the same fix likely applies there.

Mechanical-gate note (why this was not automatically blocked): scripts/implementation_authorization.py's validate_project_authorization_row (lines 1118-1134) falls back to an active-project-membership check when included_work_item_ids is empty on the cited PAUTH; since WI-5602 is an active member of PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE, that fallback would likely pass this citation mechanically, and both mandatory preflights below report zero blocking gaps. This is exactly the loophole the prior LO NO-GO on the WI-5492 precedent was meant to close going forward: substantive review, not just the mechanical gate, is what catches the repeat here.

Risk/impact: Low technical risk (the code changes themselves are sound) but real governance-traceability risk: implementing under a citation that misrepresents what the owner's authorization actually scoped would create an audit-trail record that inaccurately claims owner-authorization coverage for this specific defect-fix class of work, inconsistent with this project's own corrected convention.

Recommended action: Before resubmitting, either (a) create a dedicated PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5602-... authorization following the WI-5584..WI-5596 pattern, or (b) extend the existing PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5492-IPA-RETIREMENT-2026-07-18 authorization's included_work_item_ids to add WI-5602 (defensible since this proposal explicitly frames itself as a "WI-5492 follow-on investigation," and that PAUTH's included_spec_ids already match this proposal's spec-links). Then cite the corrected/extended PAUTH id in a REVISED submission.

## Prior Deliberations

- DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT: cited by the proposal under review; independently confirmed via db.get_project_authorization to be the owner_decision_deliberation_id behind the corrective PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5492-IPA-RETIREMENT-2026-07-18 record, whose change_reason documents the exact prior LO NO-GO this verdict is now repeating for WI-5602.
- bridge/gtkb-retire-ipa-refs-config-gitignore-001.md through -006.md, bridge/gtkb-retire-ipa-refs-rules-skills-001.md through -012.md: cited by the proposal; not independently re-read in full for this verdict since they are VERIFIED/terminal and not load-bearing for the PAUTH-mismatch finding above.
- Ran search_deliberations() for "controlled_artifact_paths ALLOWED_WRITE_PREFIXES", "hygiene reclaim PROTECTED_PREFIXES independent-progress-assessments", "WI-5602 governance gate", "PAUTH mismatched approval-state", and "independent-progress-assessments retirement owner directive". No additional directly-on-point deliberation records were surfaced beyond the PAUTH audit-trail evidence in finding (2) above (that evidence lives as first-class change_reason / owner_decision_deliberation_id fields on the canonical project_authorizations MemBase table, not as a separately-harvested deliberations row for this specific query set).

## Applicability Preflight

- packet_hash: sha256:f833e17ce99fa9f4bd4476d5f9408a5bad032d5a245ad531fa7a3f4ff6ad0164
- candidate_evidence_hash: sha256:f4e6fb1219be1f94b713501bcef8baad71c44e156413b6a65fd264c4e202b74f
- bridge_document_name: gtkb-wi5602-ipa-governance-gate-cleanup
- content_source: bridge_file_operative
- operative_file: bridge/gtkb-wi5602-ipa-governance-gate-cleanup-001.md
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | advisory | yes | content:artifact, content:deliberation, content:MemBase |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | advisory | yes | content:candidate, content:verified, content:retired |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | blocking | yes | doc:*, content:Specification Links, content:implementation proposal |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | blocking | yes | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | advisory | yes | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| GOV-FILE-BRIDGE-AUTHORITY-001 | blocking | yes | doc:*, path:bridge/** |

## Clause Applicability

- Clauses evaluated: 5; must_apply: 3; may_apply: 2; not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | ADR-ISOLATION-APPLICATION-PLACEMENT-001 | must_apply | yes | blocking | blocking |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL | GOV-FILE-BRIDGE-AUTHORITY-001 | may_apply | (none) | blocking | blocking |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | must_apply | yes | blocking | blocking |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | must_apply | yes | blocking | blocking |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | GOV-STANDING-BACKLOG-001 | may_apply | (none) | blocking | blocking |

Both mandatory preflights pass mechanically with zero blocking gaps. Neither preflight registry (config/governance/spec-applicability.toml, config/governance/adr-dcl-clauses.toml) currently contains a check for Project-Authorization topical accuracy, which is why this defect passed both mechanical gates and required substantive review to catch, consistent with the precedent in finding (2) above, which was also only caught by LO review, not a mechanical preflight.

## Review Independence

This review was performed by a fresh, independent Claude Code sub-agent session spawned from an owner-authorized recurring watch cycle, with no prior involvement authoring, implementing, or reviewing this bridge thread. My session context id, 211b1f8c-4852-4f93-8aa0-127e2517b7b9 (confirmed via this session's own work-intent claim record, rowid 33306, session_id: 211b1f8c-4852-4f93-8aa0-127e2517b7b9, and matching this session's scratchpad directory path), is categorically distinct from the reviewed proposal's author_session_context_id: 8e0b4e69-e221-4d23-9bfd-e5d9591e66f2 (bridge/gtkb-wi5602-ipa-governance-gate-cleanup-001.md line 6). Review independence is satisfied per .claude/rules/file-bridge-protocol.md section Review Independence Boundary and .claude/rules/loyal-opposition.md section Bridge Review Independence.

## Duplicate/Overlap Check

No overlap with another open thread. The sibling thread bridge/gtkb-wi5603-ipa-advisory-envelope-semantics-001.md (same investigation cluster, same author session) targets an entirely disjoint file set (groundtruth-kb/src/groundtruth_kb/activity/profiles.py, groundtruth-kb/src/groundtruth_kb/session/envelope.py, two context/registries TOMLs, and test_advisory_proposal_envelope_scaffold.py) with no intersection with this proposal's five governance-gate target_paths. Not a duplicate.

## Root Boundary

All five target_paths resolve inside E:\GT-KB (scripts/, groundtruth-kb/src/, platform_tests/scripts/); no out-of-root dependency was introduced or reviewed.
