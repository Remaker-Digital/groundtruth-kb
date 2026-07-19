NO-GO
::init gtkb pb
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 211b1f8c-4852-4f93-8aa0-127e2517b7b9
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent, independent Loyal Opposition review session, spawned from recurring owner-authorized watch cycle (Ollama/OpenRouter provider-reliability chain and bridge/TAFE/dispatcher governance infrastructure)

# Loyal Opposition Review - gtkb-wi5603-ipa-advisory-envelope-semantics - NO-GO

bridge_kind: lo_verdict
Document: gtkb-wi5603-ipa-advisory-envelope-semantics
Version: 002
Reviewed at: 2026-07-18T23:25:00Z
Responds to: bridge/gtkb-wi5603-ipa-advisory-envelope-semantics-001.md

## Review Independence

Reviewer `author_session_context_id`: `211b1f8c-4852-4f93-8aa0-127e2517b7b9` - confirmed via this session's own scratchpad path binding and via the work-intent claim registry's environment-derived `session_id` on the claim acquired for this review (`rowid: 33314`, `acquired_at: 2026-07-18T23:11:03Z`).

Author `author_session_context_id` (from -001 header): `8e0b4e69-e221-4d23-9bfd-e5d9591e66f2`.

These are distinct session contexts. This review was conducted by a freshly-spawned, independent sub-agent session with no shared memory, continuity, or prior context with the authoring session. No self-review condition exists under `.claude/rules/file-bridge-protocol.md` "Review Independence Boundary" or `.claude/rules/codex-review-gate.md` "Review Independence Gate".

## Duplicate/Overlap Check

`gtkb-wi5602-ipa-governance-gate-cleanup` (also latest-NEW, same project/investigation) was inspected for overlap. Its `target_paths` (`scripts/controlled_artifact_paths.py`, `scripts/implementation_authorization.py`, `groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py`, `platform_tests/scripts/test_controlled_artifact_paths.py`, `platform_tests/scripts/test_protected_mutation_guard.py`) share zero files with WI-5603's targets, and its concern (governance gates mechanically *permitting* writes into the retired directory) is materially different from WI-5603's concern (stale required phrasing in advisory-envelope semantic markers, plus a live test regression). Not a duplicate; both are legitimate sibling work items from the same WI-5492 follow-on investigation. (Note for Prime Builder, non-blocking: WI-5602 cites the identical mismatched `Project Authorization:` line addressed in Finding 1 below, so both can likely be corrected together.)

## Independent Re-Derivation Performed

All claims below were re-derived fresh in this session, not taken from the proposal's narrative, the orchestrating prompt's characterization, or any cached summary:

1. `git log -1 --format="%H %ci" aab90256` - confirmed the commit exists.
2. `python -m pytest platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py -q --tb=short` - run fresh; reproduced exactly 2 failed / 2 passed, matching the proposal's claim (`test_test11418_role_and_startup_scaffolds_teach_advisory_bridge_semantics`, `test_test11419_deliberation_and_build_profiles_teach_advisory_progression`, both failing on `['CODEX-INSIGHT-DROPBOX', 'non-canonical session evidence']`).
3. `git status --short` (full worktree) and `git diff` on `groundtruth-kb/src/groundtruth_kb/session/envelope.py` - confirmed an unrelated uncommitted change exists in one target file (git-probe timeout/toplevel-validation logic, unrelated to the stale-phrase lines), and confirmed dozens of other unrelated dirty files across the tree consistent with heavy concurrent activity. Lines 65-66 and 86-87 (the proposal's cited `PRELOAD_STATES` lines) are unaffected by that unrelated diff.
4. Direct grep/read of all 5 `target_paths` at current on-disk state:
   - `groundtruth-kb/src/groundtruth_kb/activity/profiles.py` line 52 - stale phrase confirmed present verbatim.
   - `groundtruth-kb/src/groundtruth_kb/session/envelope.py` lines 65-66, 86-87 - stale phrase confirmed present verbatim (both `PRELOAD_STATES["deliberation"]` and `["build"]`).
   - v1 registry `activity-disposition-profiles.toml` - stale `"CODEX-INSIGHT-DROPBOX"` (lines 87, 153), stale `history_state.sources` line (98, 165), stale guardrail line (117, 188) all confirmed present exactly as described.
   - v1 registry `system-interface-map.toml` line 103 - stale `role_permissions` text confirmed present verbatim; top-level (already-corrected) equivalent confirmed to read the proposed replacement text verbatim.
   - `platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py` `_assert_required_semantics` `required_fragments` - confirmed the 3 stale mandatory substrings exactly as cited.
   - Top-level `config/agent-control/activity-disposition-profiles.toml` - confirmed already carries the "is retired; do not read from or recreate it" phrasing at lines 115, 184 (the pattern this proposal mirrors).
5. `git show --stat aab90256` and `git log --oneline -- config/agent-control/SESSION-STARTUP-INDEX.md` (and the other 3 top-level files) - see Finding 2.
6. `KnowledgeDB.get_work_item('WI-5603')` - confirmed exists, `origin=regression`, `priority=P1`, `stage=backlogged`, matching the proposal's Specification-Derived Verification row.
7. `gt projects show PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE` - confirmed project active, WI-5603 listed as a member, and confirmed both cited PAUTHs' status.
8. `KnowledgeDB.get_project_authorization(...)` on both `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30` (cited) and `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5492-IPA-RETIREMENT-2026-07-18` (not cited) - see Finding 1.
9. `KnowledgeDB.get_spec(...)` on all 10 cited `Specification Links` entries plus `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - all FOUND live in MemBase with non-empty status.
10. `db.search_deliberations(...)` (4 queries) plus direct reads of both cited `DELIB-*` IDs - both exist; no additional directly-on-point prior deliberation surfaced beyond what -001 already cites and what Finding 1's evidence trail below identifies via direct bridge-file inspection.
11. `grep -rl` for the cited mismatched PAUTH ID across `bridge/` plus targeted reads of `bridge/gtkb-retire-ipa-refs-rules-skills-001.md` through `-005.md` - see Finding 1.
12. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5603-ipa-advisory-envelope-semantics` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5603-ipa-advisory-envelope-semantics` (exit code confirmed 0) - both pass; see sections below.
13. `python -m py_compile scripts/gtkb_bridge_writer.py` - compiled cleanly at time of writing this verdict.

## Findings

### Finding 1 (blocking) - Cited Project Authorization is a scope mismatch, repeating a defect already NO-GO'd once in this exact lineage

**Observation:** -001 declares `Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30`. Direct read via `KnowledgeDB.get_project_authorization(...)` shows this PAUTH's `authorization_name` is `"Project-level approval-state retirement bounded implementation"` and its `scope_summary` is: "Bounded project-level authorization for PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE to retire live/load-bearing individual work-item approval-state authority. Covers updates to directives, skills/adapters, helpers, startup/doctor/backlog logic, deterministic scans, tests, and required governance evidence so project authorization, not WI approval state, is the approval source." This text is specifically and exclusively about retiring the MemBase `work_items.approval_state` field as an authority mechanism (matching `.claude/rules/backlog-approval-state.md` and its own `owner_decision_deliberation_id`, `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT`). It contains no language covering redirection of stale `independent-progress-assessments` references. Its `included_work_item_ids` is `None` (no WI enumeration), so it only mechanically validates for WI-5603 via `implementation_authorization.py`'s loose fallback (`_work_item_in_project_or_descendant`) - bare project-membership, not scope congruency.

**Deficiency Rationale:** `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` (a spec whose subject matter directly governs the PAUTH mechanism this proposal relies on) explicitly states: "A project authorization may not authorize... work outside the cited project scope unless a separate approval gate authorizes those actions" and "Backlog membership alone is not implementation authorization." WI-5603 being a member of `PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE` is therefore explicitly insufficient by the governing spec's own text; the cited PAUTH's own bounded scope must cover the work, and it does not. This is not a hypothetical concern: the *identical* defect (same PAUTH ID, same project, same underlying WI-5492 follow-on lineage) was found and issued as a **blocking** finding by an independent Loyal Opposition review against the direct predecessor thread, `bridge/gtkb-retire-ipa-refs-rules-skills-004.md` ("Finding 1 (blocking) - Cited Project Authorization does not substantively cover WI-5492's scope"), which -001 itself cites in its own `Prior Deliberations` section ("bridge/gtkb-retire-ipa-refs-rules-skills-001.md through -012.md (VERIFIED)"). That review's own evidence trail is essentially identical to the evidence independently re-derived above, down to the same `scope_summary` quotation. The predecessor thread was corrected in `-005` by switching the operative `Project Authorization:` line to `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5492-IPA-RETIREMENT-2026-07-18` (confirmed live: `included_work_item_ids: ["WI-5492"]`, `owner_decision_deliberation_id: DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT` - the same deliberation -001 already cites in its own `Owner Decisions / Input` section). That corrected PAUTH does **not** cover WI-5603 either (its `included_work_item_ids` enumerates only `WI-5492`), so simply switching the citation to it, unmodified, would not close this finding - WI-5603 is a distinct work item discovered as a follow-on regression, not WI-5492 itself.

**Risk/Impact:** If left uncorrected, the bridge audit trail for WI-5603 asserts an authorization basis that does not substantively hold up under independent scrutiny, exactly the erosion-of-evidentiary-value risk the predecessor review already flagged project-wide. The mechanical preflights cannot catch this class of defect (both preflights below pass cleanly for -001, confirming they only check citation presence/format, not scope congruency).

**What is NOT wrong:** The underlying owner-authorization basis for WI-5603 is not actually missing. `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT` is a real, on-topic, already-live `owner_conversation`/`owner_decision` record that directly authorizes exactly this class of redirect/sync work, and it is already correctly cited in -001's `Owner Decisions / Input` section. The defect is narrowly the `Project Authorization:` metadata line, not an absence of owner authorization. None of the 5 proposed file edits need to change - they are independently confirmed correct (see Independent Re-Derivation Performed, item 4).

**Proposed Solution / Enhancement (either path closes this finding, matching the precedent's own resolution options):**
1. Drop or correct the `Project Authorization:` line so it no longer cites a PAUTH whose scope does not cover this work, and rely on `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT` (already present in `Owner Decisions / Input`) as the sole/primary owner-authorization basis; or
2. Amend `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5492-IPA-RETIREMENT-2026-07-18` to add `WI-5603` (and, if Prime Builder chooses to batch the fix, `WI-5602`) to its `included_work_item_ids`, or mint a new WI-5603-scoped PAUTH mirroring the established sibling pattern already used elsewhere in this same project for same-day WI-5492 follow-on work (e.g. `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5584-CANONICAL-CONFIG-DECONTAMINATION-2026-07-18`, `-WI-5590-...`, `-WI-5592-...`, `-WI-5596-...`), then refile citing that corrected/new PAUTH.

**Option Rationale:** Path 1 is lower-effort and mirrors the resolution the identical predecessor defect actually used as its first-listed option; path 2 mirrors the pattern this same project already applies to every other same-day WI-5492 follow-on thread and keeps the audit trail maximally explicit. Either is a metadata-only correction with no code/test changes required, so a REVISED resubmission should be low-friction.

### Finding 2 (non-blocking, P3) - Problem Statement misattributes the commit that corrected the 4 top-level narrative surfaces

**Observation:** -001's Problem Statement states the 4 top-level files (`SESSION-STARTUP-INDEX.md`, `PRIME-BUILDER-STARTUP-OVERLAY.md`, `LOYAL-OPPOSITION-STARTUP-OVERLAY.md`, top-level `activity-disposition-profiles.toml`) were corrected "committed at `aab90256`."

**Deficiency Rationale:** `git show --stat aab90256` does not touch any of those 4 files (it touched `.claude/rules/*.md`, `AGENTS.md`, `CLAUDE.md`, and various bridge/deliberation artifacts instead). `git log --oneline` on each of the 4 files shows the actual correcting commit is `64897bd7` ("chore(governance): WI-5492 retire IPA references in config/gitignore/script batch VERIFIED", 2026-07-18 01:44:36 -0700) - an earlier, separate WI-5492 commit. `aab90256` ("docs(gtkb): retire obsolete ipa references", 2026-07-18 10:27:27 -0700) is real and WI-5492-related, but corrected a different file set.

**Risk/Impact:** Low. The substantive claim (the 4 top-level files are already corrected) is independently verified TRUE by direct file inspection; only the specific commit-SHA attribution is wrong. Does not affect the acceptance criteria, the correctness of the 5 proposed edits, or the confirmed test-regression evidence.

**Proposed Solution:** Correct the citation to `64897bd7` in any resubmission or the eventual post-implementation report.

**Option Rationale:** Trivial fix; flagged for audit-trail accuracy per this project's demonstrated sensitivity to precise commit attribution (see Finding 1's precedent thread, which turned on exactly this kind of precise-evidence scrutiny).

### Finding 3 (non-blocking, hygiene) - Unfilled helper-scaffold placeholder left in filed proposal

**Observation:** The `### Helper-suggested candidates` sub-section under `## Prior Deliberations` still contains the raw unfilled instruction text `_No prior deliberations: <fill in reason before filing>._`, even though genuine Prior Deliberations entries are present above it (2 DELIB IDs + 2 bridge thread series).

**Deficiency Rationale:** This does not trigger `.claude/rules/codex-review-gate.md`'s "Prior Deliberations Section Requirement" NO-GO condition (that gate fires only when the section is absent/empty AND no justification line is present; concrete entries exist here), but it is helper-scaffold leftover that should not have survived into a filed proposal.

**Proposed Solution:** Delete the unfilled sub-section (or fill/remove it) before future filings; a simple authoring-checklist item, not a functional defect.

## Prior Deliberations (this review)

- `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT` - confirmed live; cited correctly by -001.
- `DELIB-20260718-WI5492-NARRATIVE-PACKET-APPROVAL` - confirmed live; cited correctly by -001.
- `bridge/gtkb-retire-ipa-refs-rules-skills-001.md` through `-012.md` (VERIFIED) - confirmed live; -004 in this chain is the direct precedent for Finding 1 above and was independently re-derived from live MemBase/PAUTH records, not merely quoted from -001's citation list.
- `bridge/gtkb-retire-ipa-refs-skill-projections-001.md` through `-005.md` - confirmed live; not independently re-read in depth for this review (out of scope; no bearing on WI-5603's target_paths).
- `db.search_deliberations()` run against 4 queries (advisory-envelope semantic markers IPA phrasing; WI-5603; independent-progress-assessments retirement test regression; PAUTH scope mismatch approval-state) surfaced no additional directly-on-point deliberation beyond the above.

## Applicability Preflight

- packet_hash: `sha256:8adc59137919c8fda9ce7073799b4b02a236b00e305071a1ceb8835c177a8fee`
- candidate_evidence_hash: sha256:61d2093bdfdcddee5fb528966f96e541da1078a539749ce6c1a7fe95c1b9096c
- bridge_document_name: `gtkb-wi5603-ipa-advisory-envelope-semantics`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5603-ipa-advisory-envelope-semantics-001.md`
- operative_file: `bridge/gtkb-wi5603-ipa-advisory-envelope-semantics-001.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | yes | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | yes | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | yes | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | yes | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | yes | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | yes | doc:*, path:bridge/** |

## Clause Applicability

- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code confirmed: `0` (pass)

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

Blocking Gaps: none from the mechanical clause preflight. Finding 1's blocking status above is an independent Loyal Opposition judgment (per `.claude/rules/loyal-opposition.md` and the precedent at `gtkb-retire-ipa-refs-rules-skills-004.md`), not a mechanical clause-preflight failure - consistent with that precedent's own observation that "the mechanical preflights cannot catch this class of defect."

## Verdict

**NO-GO.** Finding 1 is blocking: the cited `Project Authorization:` line does not substantively cover WI-5603's scope, repeating a defect already identified and corrected once in this exact bridge lineage. The 5 proposed file edits themselves are independently verified correct, low-risk, and exactly mirror an already-approved pattern (WI-5492); the confirmed active test regression (2 of 4 sub-tests failing, reproduced fresh) is real and matches the proposal's claim. Resubmit as REVISED with either remediation path from Finding 1 applied (no code/test changes required), and Findings 2-3 corrected if convenient. Upon a corrected `Project Authorization:` citation (or its removal in favor of the already-cited `DELIB-20260717-...` deliberation), this proposal is otherwise well-evidenced and ready for GO.
