GO
::init gtkb pb
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 415d99a7-2445-4075-806f-ef339ba9fdfe
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent performing Loyal Opposition bulk bridge processing (independent review session spawned for a single named bridge thread)

# Loyal Opposition Review - GO

Document: gtkb-retire-ipa-refs-config-gitignore
Bridge entry: bridge/gtkb-retire-ipa-refs-config-gitignore-001.md (NEW)
bridge_kind: lo_verdict
Responds to: bridge/gtkb-retire-ipa-refs-config-gitignore-001.md
Reviewed at: 2026-07-17 UTC

## Applicability Preflight

- packet_hash: `sha256:73e22b5e27863d84de50d1fab2a97eb6af8e07fab5fb5b53df39b7f14c746e0c`
- bridge_document_name: `gtkb-retire-ipa-refs-config-gitignore`
- preflight_passed: `true`
- declared_target_paths: [".gitignore", "config/agent-control/CONTROL-MAP.md", "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md", "config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md", "config/agent-control/REVIEW-MODE-SETUP.md", "config/agent-control/SESSION-STARTUP-INDEX.md", "config/agent-control/activity-disposition-profiles.toml", "config/agent-control/declarative-agent-role-manifest.yaml", "config/agent-control/system-interface-map.toml", "config/governance/document-author-provenance.toml", "config/governance/evidence-freshness-boundaries.toml", "config/governance/hygiene-baseline-registry.toml", "config/governance/hygiene-sweep-patterns.toml", "config/governance/lo-file-safety.toml", "scripts/advisory_backlog_router.py"]
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- Command: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-retire-ipa-refs-config-gitignore`
- Exit code: 0

### adr_dcl_clause_preflight.py

- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Command: `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-retire-ipa-refs-config-gitignore`
- Exit code: 0 (pass)

Both mandatory preflights pass clean on the operative `-001` file.

## Prior Deliberations

No prior deliberation directly addresses this exact bridge thread. Independent search_deliberations() queries for "independent-progress-assessments retirement", "obsolete reference purge", "gitignore dead pattern removal", and "lo-file-safety allow_patterns" surfaced the following relevant precedent (the proposal's own Prior Deliberations list is mostly generic auto-linked noise - DELIB-0001, DELIB-0016, DELIB-0370 are unrelated boilerplate hits, not substantive precedent):

- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` - the owner directive establishing PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE as a standing obligation on significant changes. Confirms the project's charter genuinely covers "purge references to a thing that was just retired," which is exactly this batch's shape.
- `DELIB-202666069` (NO-GO) / `DELIB-202666068` (GO) - WI-5114 scratch-ignore .gitignore EOL/durability thread. Different defect class (line-ending normalization vs. dead-block removal) but establishes that .gitignore edits in this repository are reviewed for durability, not just correctness. Noted as an implementation-time reminder below, not a blocker.

## Independent Verification (not taken on trust)

### Problem premise - confirmed real

- Test-Path E:\GT-KB\independent-progress-assessments returns False. The directory is genuinely deleted.
- Grepped all 15 declared target_paths directly for the literal string independent-progress-assessments. All 15 contain live references:
  - config/governance/lo-file-safety.toml lines 7-9: 3 allow_patterns entries pointing into the deleted directory (plus memory/MEMORY.md at line 10, which the proposal correctly says to retain).
  - config/governance/document-author-provenance.toml line 6: one dead governed_surfaces glob.
  - config/governance/hygiene-sweep-patterns.toml lines 112 and 392: 2 dead exclude-pattern entries.
  - config/governance/hygiene-baseline-registry.toml lines 13, 26 (citation source_reports, annotate-only per file's own "DO NOT silently mutate" frozen-baseline header) and line 740 (HYG-060 finding title - confirmed this is itself an historical finding about the old directory's file-count debt, correctly left untouched per the proposal's plan).
  - config/governance/evidence-freshness-boundaries.toml lines 78-79 (citation_only_patterns entry) and lines 96/103/110/117/124/131/138 (7 blocker_families.evidence_path entries, B1-B7, all citing the same one now-deleted file) - matches the proposal's "7 evidence_path citations to one deleted source" claim exactly.
  - .gitignore lines 313-347: the full retired-directory ignore block (header comment through final pattern). Note: this is closer to ~30-35 lines including the section-header comment and inline explanatory comments, not literally "21 lines" as the proposal's prose states. Minor prose-accuracy nit, not a scope problem - the block is unambiguous and fully identified either way.
  - scripts/advisory_backlog_router.py line 5 (docstring prose) and line 53 (DROPBOX_RELATIVE code constant, real runtime value). Read collect_dropbox_advisories() (line 284): it does "if not dropbox.is_dir(): return advisories" before globbing, i.e. it already fails safe on a missing directory - confirms "runtime behavior is unchanged" is literally true. Confirmed the proposal's scope boundary (touch the docstring only, leave DROPBOX_RELATIVE's value alone) is not just conservative but necessary: platform_tests/scripts/test_advisory_backlog_router.py has 8+ test functions that build a fake tmp_path / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" fixture and exercise router.run(source="dropbox", ...) against it. Changing DROPBOX_RELATIVE's literal value would break every one of those tests; leaving it alone (as scoped) does not.
  - config/agent-control/{CONTROL-MAP,REVIEW-MODE-SETUP}.md: confirmed the claimed pre-existing ALL-CAPS path-drift bug is real - both files list independent-progress-assessments/CODEX-WAY-OF-WORKING.md etc. as "Startup Directives" when the real live files are .claude/rules/codex-way-of-working.md (lowercase, hyphenated) and siblings. This drift predates the directory's deletion.
  - config/agent-control/{SESSION-STARTUP-INDEX,PRIME-BUILDER-STARTUP-OVERLAY,LOYAL-OPPOSITION-STARTUP-OVERLAY}.md, activity-disposition-profiles.toml (4 refs), declarative-agent-role-manifest.yaml, system-interface-map.toml: all confirmed present and consistent with the proposal's description (dropbox-qualifier prose, non-authoritative-evidence framing).

### Test-breakage check (not mentioned in the proposal - performed independently)

Grepped platform_tests/ for every target file's basename plus independent-progress-assessments/governed_surfaces/allow_patterns/source_reports across ~20 candidate test files. Findings:

- test_document_author_metadata.py::test_config_loads_live_contract only asserts "bridge/**/*.md" in config.governed_surfaces and ".claude/worktrees/**" in config.exclusions - does not assert the IPA glob is present, so removing it does not break this test.
- test_gtkb_hygiene_investigation.py line 120 asserts len(registry.source_reports) == 2 - a count, not content. This mechanically requires the implementation to annotate (not delete) the 2 hygiene-baseline-registry.toml source_reports entries, exactly as the proposal's own plan states. Good corroboration that "annotate, don't delete" is the correct (and here, test-enforced) approach.
- test_activity_disposition_profiles.py, test_session_startup_index.py, test_session_startup_control_map.py, test_system_interface_map.py, test_evidence_freshness_boundary.py, test_lo_file_safety_gate_role_resolution.py: none reference independent-progress-assessments or the specific fields being edited. Low breakage risk.

No test surface found that would be broken by the proposed scope. This check is not in the proposal's own verification plan and is worth Prime Builder folding into the implementation report's test evidence.

### Standing backlog conflict check (required by loyal-opposition.md "Backlog Conflict & Future Work Review")

db.list_work_items(resolution_status="open") (411 open items) scanned for references to the 15 target files. Two genuine same-file overlaps with other backlogged (not yet implemented) work items, both judged non-blocking:

- WI-5264 ("Teach Advisory Proposal semantics in deliberation and build activity envelopes") explicitly lists config/agent-control/activity-disposition-profiles.toml as an expected implementation surface for adding new Advisory Proposal guidance content. This proposal only removes a dead "dropbox" qualifier phrase from 4 existing lines in the same file. Different edit, same file - low direct-conflict risk, but the WI-5264 implementer should be aware this file will already have moved.
- WI-5379 ("Envelope Protocol Slice G: cleanup, documentation, and SoT reconciliation") explicitly lists "SESSION-STARTUP-INDEX, role overlays, system-interface-map inventory" as future touchpoints - three of this proposal's 15 target files. WI-5379's own description says to "extend in-flight WI-5310/5314/5328/5335 rather than duplicating them"; the same courtesy should extend to this WI-5492 slice once it lands, so the eventual WI-5379 implementer does not redo the specific IPA-citation fix landed here.

Per the rule's stated remedy ("bring forward backlog work planned for the future, or add the related work to the scope of an existing future project"), neither overlap blocks this narrowly-scoped proposal; both are recorded here so the WI-5264 and WI-5379 implementers inherit the context instead of rediscovering it.

### Project authorization - independently verified, with a scope-precision finding

db.get_project_authorization("PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30") confirms: status=active, project_id=PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE (itself status=active), expires_at=null, included_work_item_ids=null, excluded_work_item_ids=null. db.get_work_item("WI-5492") confirms project_name="GTKB Obsolete Reference Purge", stage=backlogged, resolution_status=open. Read validate_project_authorization_row() in scripts/implementation_authorization.py (lines 1082-1153): with included_work_item_ids empty, validation falls through to _work_item_in_project_or_descendant, i.e. project membership, not scope_summary text, is the mechanical gate. WI-5492 passes that gate.

Finding (non-blocking, disclosure-only): this PAUTH's own scope_summary and authorization_name ("Project-level approval-state retirement bounded implementation... to retire live/load-bearing individual work-item approval-state authority") describe a different sub-initiative than this batch (redirecting retired-directory citations). Read the PAUTH's own authorizing deliberation, DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT: the owner directive there is "Approval scope in GT-KB is project-level only... Work items are automatically approved for implementation when their parent project is approved... Individual work items do not have an approval state." That is precisely the philosophy that makes a project-level (non-item-restricted) PAUTH a valid authority for any active member work item of its project, even one filed after the PAUTH and describing different subject matter than the PAUTH's own scope prose. Separately and independently, DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT (source_type=owner_conversation, outcome=owner_decision, dated today) is real, on-point, and directly authorizes exactly this: "The independent-progress-assessments directory is retired and all of its contents are deleted... Preserve needed durable information only in MemBase, the Deliberation Archive, or canonical bridge artifacts." Between the structural PAUTH validity and this specific on-point owner decision, authorization for this batch is sound. Recommendation for Prime Builder (non-blocking): a future obsolete-reference-purge PAUTH batch would be clearer audit evidence with either a scope_summary broadened to name "obsolete reference purge" generally, or citation of a PAUTH whose prose actually matches the work (the sibling PAUTH-...-IMPLEMENTATION-2026-06-25 PAUTH is topically closer but structurally excludes WI-5492 via its populated included_work_item_ids list, so it could not have been cited instead).

### Working-tree state

git status --short -- against all 15 declared target paths shows only .gitignore as dirty, pre-existing, uncommitted. git diff -- .gitignore shows the dirty hunk is near line 514 (WI-5325 harness-state/*/session-envelope* ignore patterns) - a different section of the file than the retired-directory block at lines 313-347 this proposal will touch. No line-level collision, but Prime Builder must scope the eventual implementation commit to only the IPA-block removal (per bridge-essential.md "Scoped commits only" invariant) and not sweep in the unrelated pre-existing WI-5325 hunk. The wider repository working tree also carries a large volume of unrelated pre-existing dirty/deleted bridge files and one dispatcher-config file (config/dispatcher/rules.toml) from other concurrent work; none of that is in this proposal's target_paths and none of it was touched during this review.

## Review Assessment

| Criterion | Status | Notes |
|-----------|--------|-------|
| Bridge root-boundary compliance | PASS | All 15 target paths confirmed under E:\GT-KB |
| Problem premise | PASS | Independently verified: directory deleted, all 15 files contain live references |
| Project authorization | PASS (with disclosed scope-precision nit) | Structurally valid; see finding above |
| Work item | PASS | WI-5492, matches KB record, open/backlogged |
| Owner decision evidence | PASS | DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT independently read, on-point |
| Target paths / in-root evidence | PASS | 15 paths, all confirmed on disk |
| Spec links | PASS | 12 specs linked; preflight found zero missing required/advisory specs |
| Spec-derived verification plan | PASS | Table maps every linked spec to a verification method |
| Backlog conflict check | PASS (2 disclosed, non-blocking) | WI-5264, WI-5379 share target files; narrow/complementary, not duplicative |
| Test-breakage risk | PASS | Independently checked ~20 test files; none broken by declared scope |
| Scope discipline | PASS | advisory_backlog_router.py DROPBOX_RELATIVE explicitly and correctly left out of scope; frozen HYG-060 baseline correctly left untouched |
| Risks/rollback | PASS | Source-only revert; append-only bridge/PAUTH artifacts correctly excluded from rollback |
| Recommended commit type | Minor nit | feat is arguably miscategorized - diff is dead-reference removal/annotation plus one security-relevant allow-list narrowing (lo-file-safety.toml), not a net-new capability. chore or fix would fit the Conventional Commits discipline in file-bridge-protocol.md better. Non-blocking; Prime may revise at implementation-report time. |

## Notable positive finding

Removing the 3 dead allow_patterns entries from config/governance/lo-file-safety.toml is not merely cosmetic: those entries currently grant Loyal Opposition write permission into the deleted independent-progress-assessments/CODEX-INSIGHT-DROPBOX/** tree. Leaving them in place would let an agent write a file that recreates part of the retired directory, directly contradicting DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT's explicit "do not... recreate... the retired surface" instruction. This is a real gap-closure, not just hygiene.

## Verdict

**GO** - The proposal's problem premise is independently confirmed against live file content (not taken on trust), both mandatory preflights pass clean with zero blocking gaps, the project authorization and owner-decision evidence are independently verified sound, a standing-backlog conflict check found two disclosed non-blocking overlaps, and an independent test-breakage sweep across ~20 candidate test files found no defect. The proposed edits are conservative (annotate historical citations rather than delete them, narrow allow-lists rather than widen them, explicitly exclude the one path that would have broken 8+ existing tests) and one of the fifteen edits closes a real write-permission gap into the retired directory. Prime Builder may proceed with implementation once the work-intent claim is acquired, scoping the .gitignore commit to exclude the unrelated pre-existing WI-5325 hunk already dirty in the working tree.
