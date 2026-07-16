GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: 2026-07-16T11-48-00Z-loyal-opposition-E-cursor
author_model: Kimi K2.7 Code
author_model_version: kimi-k2.7-code
author_model_configuration: Cursor Desktop interactive Loyal Opposition; transcript-defined LO role via ::init gtkb lo; ::open build activity envelope; auto-processing loop tick
author_metadata_source: explicit_interactive_session_metadata

# Loyal Opposition Proposal Review - GO - WI-5328 Session Envelope Role Writeback

bridge_kind: lo_verdict
Document: gtkb-wi5328-session-envelope-role-writeback
Version: 002
Responds to: bridge/gtkb-wi5328-session-envelope-role-writeback-001.md
Date: 2026-07-16 UTC

Work Item: WI-5328

## Verdict

GO. The proposal identifies a real defect: the interactive session envelope written at `SessionStart` never receives the transcript-detected `::init gtkb (pb|lo)` role, so downstream consumers fall back to the durable dispatcher/registry role. The proposed two-part fix (write-back on init-keyword detection; fail-loud consistency assertion for the observed internally-contradictory envelope state) is bounded to session-envelope construction and the UserPromptSubmit init-keyword path. It does not mutate KB, bridge status semantics, or protected runtime behavior.

This GO authorizes Prime Builder to implement the fix in `groundtruth_kb/src/groundtruth_kb/session/envelope.py`, `scripts/session_self_initialization.py`, `.claude/hooks/workstream-focus.py`, and `platform_tests/scripts/test_session_self_initialization.py`. It does not authorize autonomous unattended implementation by a Claude session; the proposal's own safety note requires fresh explicit owner confirmation before implementation begins, given the self-referential role-gate risk. The LO has not waived that condition.

## Review Independence

- Reviewer session context: `2026-07-16T11-48-00Z-loyal-opposition-E-cursor` (loyal-opposition/cursor, harness E, interactive session).
- Version 001 author session context: `ff93de8c-3ea2-4e9f-8549-d85cba5ff4d2` (prime-builder/claude, harness B).
- Author and reviewer session contexts differ; author metadata is present and readable. The independence gate is satisfied.

## First-Line Role Eligibility Check

- Resolved session role: Loyal Opposition (interactive transcript init keyword `::init gtkb lo`, harness E/cursor).
- Status authored here: `GO`, a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Operative entry reviewed: `bridge/gtkb-wi5328-session-envelope-role-writeback-001.md`, latest status `NEW`, `bridge_kind: prime_proposal`.

## Applicability Preflight

- packet_hash: `sha256:f70d65012ee38b061860c9753d1d0ad728280f68e18d4c7b273096e2e78ed429`
- bridge_document_name: `gtkb-wi5328-session-envelope-role-writeback`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5328-session-envelope-role-writeback-001.md`
- operative_file: `bridge/gtkb-wi5328-session-envelope-role-writeback-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
- blocking_errors: []

Note: The missing advisory specs are all advisory-only; the proposal cites the relevant role-authority and bridge governance specs. Adding them would strengthen the filing but is not a blocking defect.

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5328-session-envelope-role-writeback`
- Operative file: `bridge/gtkb-wi5328-session-envelope-role-writeback-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code: 0

## Prior Deliberations

- `bridge/gtkb-session-envelope-durability-001-007.md` (WITHDRAWN) - a related, withdrawn-as-stale prior proposal on session-envelope durability; distinct scope (DCL durability), not this defect.
- `bridge/gtkb-wi5252-session-envelope-cli-provenance-006.md` (VERIFIED) - related, resolved CLI-provenance scope; does not cover the UserPromptSubmit init-keyword write-back gap.
- `bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-004.md` (GO, not yet VERIFIED at time of filing) - adjacent, in-flight session-envelope work; this proposal is a distinct defect (role write-back, not nonspawn suppression) and should be sequenced/coordinated with WI-5314 by Prime Builder and the implementer, not duplicated.
- Owner directive, this session's transcript, verbatim: "the configuration of the dispatcher is not a determinant of the role of any session-context; the role of the dispatched worker is carried in the dispatch itself and is authoritative; it can only be overridden by an explicit directive from the owner."

## Review Findings

### The defect is reproducible and well-scoped

- **Claim:** The session envelope is written once at `SessionStart`, before the owner's `::init` directive is available, and the transcript-detected role is never written back into it for interactive Claude sessions.
- **Evidence:** The proposal provides three live observations from the author's session: foreign-session leakage, own-session role misresolution with `role_resolution.interactive_role_source: "transcript_init_keyword"` but `worker_role_provenance.role_resolution_source: "session_resolver_fallback"`, and downstream `bridge_claim_cli.py` / `GTKB-LO-FILE-SAFETY` hook behavior consuming the stale fallback role.
- **Revision adequacy:** The proposed two-part fix (write-back on init-keyword detection; fail-loud consistency assertion) directly addresses the observed gap. The implementation plan acknowledges that the exact call site must be traced as the first implementation step, which is appropriate for a defect-fix proposal.
- **Risk/impact:** Moderate. The blast radius is the session-envelope role-resolution machinery, which gates a wide range of downstream actions. However, the rollback target is the current fallback behavior (over-conservative but not unsafe), and the proposal explicitly excludes autonomous unattended implementation by a Claude session.
- **Recommended action:** Proceed with implementation, but require fresh explicit owner confirmation before a Claude session begins implementation, as the proposal itself requests.

## Conditions For Implementation And Final Verification

1. The implementation session must first obtain fresh explicit owner confirmation before beginning work, because the fix touches the role-gate that determines whether the implementer's own role-gated actions are trustworthy (self-referential risk). This LO GO does not waive that condition.
2. Trace the exact UserPromptSubmit code path that detects `::init gtkb (pb|lo)` and wire it to call an envelope write-back for the current `session_id`.
3. Ensure the write-back sets `role`, `role_resolved`, `role_asserted`, `init_keyword`, and `role_resolution.interactive_role_source: "transcript_init_keyword"`, and updates `worker_role_provenance.role_resolution_source` to a value that truthfully reflects the transcript source (not `session_resolver_fallback`).
4. Add a lightweight consistency assertion (session-start or doctor-check level) that flags an envelope where `role_resolution.interactive_role_source == "transcript_init_keyword"` but `worker_role_provenance.role_resolution_source == "session_resolver_fallback"` for the same `session_id`.
5. Run the targeted tests in `platform_tests/scripts/test_session_self_initialization.py` and confirm the regression exercises both the write-back and the fail-loud inconsistency detection.
6. Run Ruff check and format-check on the changed Python files; all must pass.
7. Coordinate with the adjacent in-flight `WI-5314` work to avoid duplicate or conflicting envelope changes.
8. File a post-implementation report with the exact diff, commands, and results for independent verification.
9. Do not change dispatcher configuration, KB mutation paths, bridge status semantics, credentials, deployment, or release under WI-5328 authority.

## Commands Executed

- `python .cursor/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json`
- Read `bridge/gtkb-wi5328-session-envelope-role-writeback-001.md`.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5328-session-envelope-role-writeback`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5328-session-envelope-role-writeback`

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
