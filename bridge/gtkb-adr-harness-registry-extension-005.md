NEW

# Post-Implementation Report: ADR-SINGLE-HARNESS-OPERATING-MODE-001 v2 - Harness Registry Architecture (WI-3343)

bridge_kind: implementation_report
Document: gtkb-adr-harness-registry-extension
Version: 005 (NEW; post-implementation report for the GO at bridge/gtkb-adr-harness-registry-extension-004.md)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: REQ-HARNESS-REGISTRY-001; DELIB-2079 Q11
Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3343
target_paths: [".gtkb-state/adr-drafts/adr-single-harness-operating-mode-001-v2.md", "groundtruth.db", ".groundtruth/formal-artifact-approvals/**"]
Recommended commit type: docs:

## Summary

The GO'd proposal at bridge/gtkb-adr-harness-registry-extension-003.md (Codex GO at -004) is implemented. A new version (v2) of ADR-SINGLE-HARNESS-OPERATING-MODE-001 was inserted into MemBase through the governed gt spec update path. v2 extends the operating-mode topology ADR to record the harness-registry architecture - the MemBase-backed harnesses table, its generated hot-path projection, the gt harness CLI, the four-state lifecycle FSM, registry-driven cross-harness dispatch, and the SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 mode-switch transaction boundary. The v1 role-set topology decision, Failed Approaches, Rejected Alternatives, and Consequences are preserved verbatim; v1 remains independently retrievable as version 1 under MemBase append-only versioning.

## Recommended Commit Type

docs: - the change is an architecture-decision record update. It adds one append-only ADR version row to groundtruth.db plus its formal-artifact-approval packet; no code, capability, hook, or behavior surface is added or changed. This matches the recommended commit type in the GO'd proposal.

## Specification Links

- REQ-HARNESS-REGISTRY-001 - the harness registry requirement whose architecture the ADR new version records.
- DELIB-2079 - owner-decided Antigravity Integration design; Q11 decided the architecture is recorded by a new version of this ADR, not a new ADR.
- DELIB-2080 - role-portability amendment (FR9); the registry preserves portable harness-assigned roles.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - the existing ADR; v1 is superseded by the v2 new version inserted by this implementation.
- GOV-HARNESS-ROLE-PORTABILITY-001 - role portability across harnesses; carried into the v2 Spec Linkage.
- GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 - multi-harness role configuration; carried into the v2 Spec Linkage.
- SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 - harness role/topology mutation is an operating-mode-switch transaction; the v2 ADR records that the gt harness set-role surface goes through the deterministic transaction component or a named successor service with equivalent validation, audit, and effective-state semantics.
- GOV-ARTIFACT-APPROVAL-001 - formal-artifact-approval discipline; the ADR new version was inserted with an owner-approval packet.
- DCL-ARTIFACT-APPROVAL-HOOK-001 - the approval-gate hook contract the gt spec update path satisfies.
- GOV-FILE-BRIDGE-AUTHORITY-001 - this work proceeds through the file bridge; bridge/INDEX.md remains canonical workflow state.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this report carries forward every relevant governing specification from the proposal.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification is derived from the linked specifications and executed against the implementation; the spec-to-test mapping and observed results are below.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - durable artifact preservation (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability across artifacts and decisions (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - artifact lifecycle state transitions (advisory).

## Prior Deliberations

- DELIB-2079 - the owner-decided Antigravity Integration design. Q11 decided the architecture is recorded by a new version of ADR-SINGLE-HARNESS-OPERATING-MODE-001, not a new dedicated ADR. The inserted v2 text records this in its Context (v2) and Rejected Alternative 4.
- DELIB-2080 - the role-portability amendment (FR9); the v2 Spec Linkage records that the registry preserves portable harness-assigned roles and the single-prime-builder invariant.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 v1 - the operating-mode topology decision extended by this version. Its role-set decision, failed approaches, rejected alternatives, and consequences are reproduced verbatim in v2 (verified below).
- bridge/gtkb-adr-harness-registry-extension-002.md - the prior NO-GO. Its single finding F1 (omission of SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001) was closed in -003 and is reflected in the inserted v2 text's Mode-Switch Transaction Boundary section.

## Owner Decisions / Input

The ADR v2 content is a formal artifact; GOV-ARTIFACT-APPROVAL-001 required explicit owner approval of the proposed content before insertion. After the Codex GO at -004, Prime Builder presented the full proposed v2 ADR text to the owner in-transcript and asked for formal-artifact approval via AskUserQuestion.

- AUQ question: "Approve the ADR-SINGLE-HARNESS-OPERATING-MODE-001 v2 text above for insertion into MemBase via gt spec update?"
- Owner answer: "Approve as drafted".
- The gt spec update insertion recorded this as AUQ evidence identifier S361-WI-3343-ADR-SINGLE-HARNESS-OPERATING-MODE-001-v2 in the formal-artifact-approval packet, with presented_to_user=true, transcript_captured=true, approved_by=owner.

The project PROJECT-HARNESS-REGISTRY-REFACTOR and the decision to record the architecture by a new ADR version (DELIB-2079 Q11) were owner-decided in the 2026-05-16 eleven-question clarification interview; the work is authorized under PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION (status active; scope WI-3337 through WI-3344).

## Clause Scope Clarification (Not a Bulk Operation)

This implementation produced a single new version of one ADR. It is not a bulk standing-backlog operation: it did not resolve, retire, promote, batch-mutate, or produce an inventory of work items. GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS - which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for the bulk action - is not applicable. The single work item cited (WI-3343) is this report's own implementing work item under the mandatory project-linkage metadata. The owner-approval packet referenced above is the per-artifact formal-artifact-approval packet for the ADR, not a bulk-action approval.

## What Was Implemented

IP-1 - Draft the v2 ADR content. The v1 ADR description was retrieved from MemBase. The v2 text was drafted at .gtkb-state/adr-drafts/adr-single-harness-operating-mode-001-v2.md: the entire v1 description is reproduced verbatim as a contiguous prefix, followed by a "=== Version 2 Extension: Harness Registry Architecture ===" block. The extension records the harnesses table (authoritative append-only store), the harness-state/harness-registry.json generated projection, the gt harness CLI with its nine subcommands, the four-state lifecycle FSM (registered -> active <-> suspended -> retired), data-driven cross-harness dispatch, and the SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 mode-switch transaction boundary. It adds two Failed Approaches (file-based JSON does not scale; reading the table on the SessionStart hot path), two Rejected Alternatives (new dedicated ADR; file-as-authority), an implemented-vs-intended split, and the v2 Spec Linkage. The architecture surfaces were verified live before drafting: the gt harness CLI subcommands, the harness-state/harness-registry.json projection structure, and the current registry records (harness A codex/loyal-opposition/active, harness B claude/prime-builder/active).

IP-2 - Present for formal-artifact approval. The full v2 text was presented to the owner in-transcript and approved via AskUserQuestion (see Owner Decisions / Input).

IP-3 - Insert through the governed path. After approval, the v2 version was inserted with python -m groundtruth_kb spec update (the module form of gt spec update; the gt console script is not on this harness's shell PATH). A --dry-run validated the packet first; the live run inserted version 2. The gt spec update path self-wrote the formal-artifact-approval packet.

IP-4 - Verification. Confirmed in the Spec-To-Test Mapping and Verification Commands sections below.

## Spec-To-Test Mapping

| Spec / governing surface | Verification | Result |
| --- | --- | --- |
| REQ-HARNESS-REGISTRY-001 / DELIB-2079 Q11 | Content review confirms the v2 ADR records the registry architecture (table, projection, CLI, FSM, data-driven dispatch); get_spec retrieval confirms the new version is live. | PASS - live version 2; registry-architecture markers present in the live description. |
| SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 | Content review of the inserted v2 ADR confirms it explicitly records that the gt harness set-role surface still goes through the deterministic transaction component or a named successor service with equivalent validation/audit/effective-state semantics. | PASS - "operating-mode-switch transaction" and "SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001" both present in the live v2 description. |
| GOV-ARTIFACT-APPROVAL-001 / DCL-ARTIFACT-APPROVAL-HOOK-001 | The formal-artifact-approval packet exists with presented_to_user=true, approved_by=owner, and full_content_sha256 matching the inserted ADR content. | PASS - packet at .groundtruth/formal-artifact-approvals/2026-05-18-ADR-SINGLE-HARNESS-OPERATING-MODE-001-v2.json; sha 5f820bb9...; live description sha equal. |
| ADR-SINGLE-HARNESS-OPERATING-MODE-001 v1 preservation | An assertion confirms the v1 role-set topology decision text is present unchanged in v2. | PASS - the entire v1 description is contained verbatim in v2; the v1 role-set decision sentence and Failed/Rejected markers are present. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This report carries the spec-to-test mapping plus the executed verification commands and observed results. | PASS - see Verification Commands And Observed Results. |

## Verification Commands And Observed Results

1. Dry-run packet validation: python -m groundtruth_kb spec update --id ADR-SINGLE-HARNESS-OPERATING-MODE-001 --content-file .gtkb-state/adr-drafts/adr-single-harness-operating-mode-001-v2.md (with --change-reason, --auq-id, --auq-answer, --owner-presented, --approved-by owner) --dry-run --json.
   Result: dry_run true; from_version 1; to_version 2; approval packet full_content_sha256 5f820bb98c9ef317c4002b3f7909545d854a9c1fe7c517327bb444ac45182f46; merged_fields ["description"].

2. Live insert: the same command without --dry-run.
   Result: updated true; row rowid 8506; version 2; type architecture_decision; status specified. PostToolUse hook confirmed KB-SPEC-EVENT: ADR-SINGLE-HARNESS-OPERATING-MODE-001 v2 -- updated.

3. Content and preservation verification (Python get_spec / get_spec_history against groundtruth.db):
   - Live version: 2; status specified; type architecture_decision.
   - sha256 of the live description equals the packet full_content_sha256 (5f820bb98c9ef317c4002b3f7909545d854a9c1fe7c517327bb444ac45182f46): equal.
   - The full v1 description is contained verbatim in the v2 description: true.
   - The v1 role-set decision sentence ("Role records (harness-state/role-assignments.json) carry role as a JSON list ...") is present in v2: true.
   - v1 Failed/Rejected markers ("pre-DispatchTarget", "DELIB-1511") present in v2: true.
   - Mode-switch boundary ("operating-mode-switch transaction" plus "SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001") recorded in v2: true.
   - Registry architecture markers ("harnesses table", "harness-registry.json", the FSM transition string, the CLI subcommand list) present in v2: true.
   - Total ADR versions: 2 (v1 preserved append-only).

4. Approval packet: .groundtruth/formal-artifact-approvals/2026-05-18-ADR-SINGLE-HARNESS-OPERATING-MODE-001-v2.json written (18244 bytes); fields presented_to_user true, transcript_captured true, approved_by owner, action update, source_ref ADR-SINGLE-HARNESS-OPERATING-MODE-001@v1, changed_by gt-cli.

5. Doctor harness/role-set checks (python -m groundtruth_kb project doctor):
   - [OK] cross-harness event-driven trigger active.
   - [OK] role-set wire form valid (2 list-form, 0 legacy-scalar).
   - [OK] single-harness dispatcher not applicable (multi-harness topology).
   The doctor also reports unrelated pre-existing FAIL/WARN items (bridge dispatch-state recipients entries; DA harvest coverage; product-scope write-path; work_list.md heuristics). These pre-date and are independent of an ADR text-record update - inserting an ADR version row cannot affect bridge dispatch-state files or harvest coverage - and are out of WI-3343 scope. They are surfaced here for transparency, not as regressions introduced by this implementation.

## Acceptance Criteria

- [x] Loyal Opposition returned GO on the proposal (-004).
- [x] The proposed v2 ADR content was presented to the owner and explicitly approved via AskUserQuestion before insertion.
- [x] The new ADR version was inserted through gt spec update with a valid formal-artifact-approval packet.
- [x] The v1 role-set topology decision is preserved unchanged in v2.
- [x] The v2 ADR records the registry architecture (table, projection, gt harness CLI, FSM, data-driven dispatch).
- [x] The v2 ADR records the mode-switch-transaction boundary for harness role/topology mutation per SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.
- [x] The doctor's harness/role-set checks pass after the ADR update.
- [x] This post-implementation report carries observed verification results.
- [ ] Loyal Opposition returns VERIFIED - pending this review.

## Applicability Preflight

The applicability preflight was run against this report via `--content-file` prior to filing the INDEX entry:

`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-adr-harness-registry-extension --content-file bridge/gtkb-adr-harness-registry-extension-005.md`

- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: sha256:cf8f5ab4afbb6dac81ffb53ce3348aae84ad58dde9257f891a0e7e462ec881b6
- content_source: pending_content (bridge/gtkb-adr-harness-registry-extension-005.md)

All applicable cross-cutting specs are cited in this report's Specification Links. Blocking: DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-FILE-BRIDGE-AUTHORITY-001. Advisory: ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001.

## Clause Applicability

The ADR/DCL clause preflight was run against this report via `--content-file` prior to filing the INDEX entry:

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-harness-registry-extension --content-file bridge/gtkb-adr-harness-registry-extension-005.md`

- Clauses evaluated: 5 (must_apply: 4, may_apply: 1, not_applicable: 0)
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code: 0 (pass)

| Clause | Applicability | Evidence found |
|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | may_apply | non-gating; in-root confirmed below |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL | must_apply | yes |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | must_apply | yes |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | must_apply | yes |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | must_apply | yes |

Project root boundary: all artifacts produced or referenced by this implementation - the v2 ADR row in groundtruth.db, its formal-artifact-approval packet under .groundtruth/formal-artifact-approvals/, the transient draft under .gtkb-state/adr-drafts/, and this report under bridge/ - are within the E:\GT-KB project root. No artifact outside E:\GT-KB was created, read as a live dependency, or required.

## Risk And Rollback

Risk R1 (v2 drops or alters v1 content): closed - the entire v1 description is contained verbatim in v2 (verified) and v1 remains retrievable as version 1 under append-only versioning.

Risk R2 (approval-packet / content mismatch): closed - the live description sha256 equals the packet full_content_sha256.

Risk R3 (v2 overclaims implemented capability): mitigated - the v2 text carries an explicit "Implemented vs intended" split distinguishing live surfaces from in-progress call-site migration.

Rollback: append-only versioning keeps v1 as the prior retrievable version; a corrective new version would supersede a flawed v2 rather than rewriting history. The transient draft content-file can be discarded with no effect on canonical state.

## Loyal Opposition Asks

1. Confirm the inserted v2 ADR records the harness-registry architecture and the SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 mode-switch boundary as required by the GO'd proposal.
2. Confirm the v1 role-set topology decision is preserved unchanged in v2.
3. Confirm the formal-artifact-approval packet satisfies GOV-ARTIFACT-APPROVAL-001 (presented_to_user, transcript_captured, approved_by=owner, content-hash match).
4. Confirm the verification evidence is adequate for an ADR artifact, or recommend additional checks.
