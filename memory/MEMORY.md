# Agent Red Memory

## Current Status
- **GroundTruth-KB project-resource aliases:** "the GitHub", "project GitHub", "repo", "the repo", "GitHub repo", and "GT-KB repo" resolve to configured URL https://github.com/Remaker-Digital/groundtruth-kb unless explicitly scoped otherwise. A local remote pointing elsewhere is configuration drift, not project identity. Agent Red is separate from GT-KB and resolves to https://github.com/mike-remakerdigital/agent-red only when explicitly scoped. See `memory/feedback_groundtruth_kb_canonical_project_urls.md`, `.claude/rules/project-resource-aliases.toml`, and `.claude/rules/canonical-terminology.md` "project-resource alias resolution".
- **Repo history policy:** preserving historical Git data is not required for the next corrective push that establishes the separated GroundTruth-KB and Agent Red repository identities. For that next push only, either remote may be wiped and pushed as a first release if that is the cleanest correction path. After that corrective push, use GitHub normally and preserve history in the usual way. This is not a standing instruction to perform destructive remote rewrites without an explicit execution request.
- **External resource registry:** `.claude/rules/project-resource-aliases.toml` maps casual resource terms to canonical URLs/identities; human-readable companion `memory/project_external_resource_registry.md`. Use it before interpreting "repo", "the GitHub", "CI", "PyPI", "SonarCloud", "Azure", "docs site", or other external-resource shorthand.
- **S330 GOVERNANCE GAP CAPTURED + 8 SPAWNED ARTIFACTS.** Slice 8.6 work was on Agent Red CI files at GT-KB root — IN VIOLATION of the now-explicit project-root-boundary topology. Owner-led audit identified 4 cross-cutting governance gaps; all captured in S330 as DELIBs: `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` (positive+negative capture-event visibility + full-text approve/reject), `DELIB-S330-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT` (Option C: write-time hook + Codex review-time check), `DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION` (LLM-classified + tiered retrieval), `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (5 binding topology rules; supersedes DELIB-0879). 8 spawned MemBase artifacts (4 GOV + 3 DCL + 1 IPR) all approved via AskUserQuestion + inserted v1: GOV-SPEC-CAPTURE-TRANSPARENCY-001, GOV+DCL-CROSS-CUTTING-REQUIREMENTS-{MECHANICAL-ENFORCEMENT-001,REGISTRY-001}, GOV+DCL-REQUIREMENTS-COLLECTION-HOOK-{001,CONTRACT-001}, GOV+DCL-AGENT-RED-NESTED-IN-APPLICATIONS-{001,CHECK-001}, IPR-REQUIREMENTS-COLLECTION-HOOK-001. Each has a formal-approval-packet at `.groundtruth/formal-artifact-approvals/2026-05-04-*.json`.
- **S330 SLICE 8.6 DISPOSITION (BLOCKED on ISOLATION-018).** Slice 8.6 acceptance is structurally blocked: my 12-commit Agent Red CI fix chain landed on the wrong target per the captured rules. The actual GT-KB v0.7.0-rc1 release happens on `Remaker-Digital/groundtruth-kb`, not via Agent Red CI workflows. Pre-migration state explicitly waivered by `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` (forthcoming) covering Agent-Red-files-at-GT-KB-root until ISOLATION-018 VERIFIED. Slice 8.6 commits exist on `Remaker-Digital/agent-red-customer-engagement` (de facto, current `origin`) and `mike-remakerdigital/agent-red develop` HEAD `84b2f8b0` (canonical Agent Red, force-pushed in S330). Both are now technically wrong-target work pending the migration that gives Agent Red files their proper home.
- **S331 ISOLATION-018 SCOPING GO'D (umbrella accepted; sub-slice work unblocked).** Pending-migration waiver DELIB created and ACTIVE: `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 in MemBase, owner-approved via AskUserQuestion, formal-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-migration-pending-waiver.json` (sha256 `be8497585b27a240...`), waiver bridge `bridge/gtkb-isolation-018-pending-migration-waiver-006.md` VERIFIED. Umbrella scoping bridge `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` GO'd: confirms 12 sub-slices 18.A through 18.L for the actual migration (NOT a vacated 18.B; original waiver-DELIB sub-slice was correctly moved to a precursor thread per Codex F2 cycle 1). 18.A is the inventory finalization (this scoping). 18.B onwards = actual file moves. v0.7.0-rc1 release path: complete sub-slices 18.B–18.L → push GT-KB framework changes to `Remaker-Digital/groundtruth-kb` → tag → publish.
- **S331 NEXT SESSION QUEUE (in priority order):** (1) Implement `gtkb-pre-filing-preflight-rule` GO at -002: edit `.claude/rules/file-bridge-protocol.md` to add the "Mandatory Pre-Filing Preflight Subsection" verbatim from the proposal; file post-impl REPORT for Codex VERIFIED. (2) Revise `gtkb-pre-filing-preflight-hook` NO-GO at -002 → -003: address F1 (preflight script reads disk file, not pending Write content; needs `--content-file` or stdin mode added to `scripts/bridge_applicability_preflight.py`) + F2 (Edit-payload reconstruction) + F3 (caching contradiction). May require splitting into a script-extension bridge thread first. (3) Begin sub-slice 18.B (PDF cluster move per ISOLATION-018 scoping) — first concrete migration work; uses the now-ACTIVE waiver to authorize touching Agent Red files at root. (4) S330 spawn-queue residual: `bridge/gtkb-cross-cutting-requirements-registry-001.md` (DCL-CROSS-CUTTING-REQUIREMENTS-REGISTRY-001 implementation) + `bridge/gtkb-requirements-collection-hook-001.md` (IPR-REQUIREMENTS-COLLECTION-HOOK-001 implementation) — independent of ISOLATION-018.
- **S330 PUSH STATUS:** Wrap commits NOT pushed. Owner directive after migration: push GT-KB to `Remaker-Digital/groundtruth-kb`, push Agent Red (after physical separation) to `mike-remakerdigital/agent-red`. Wrap commits land on `develop` of current `origin` (`Remaker-Digital/agent-red-customer-engagement`) for now; will be reconciled during ISOLATION-018.
- **S331 PUSH STATUS:** 0 commits pushed. Working tree carries: 9 untracked bridge files under `bridge/`, `memory/feedback_preflight_before_filing_bridge_proposals.md` (untracked + indexed in MEMORY.md), `.groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-migration-pending-waiver.json` (untracked), `bridge/INDEX.md` modifications, MEMORY.md modifications. DELIB inserted to `groundtruth.db` (gitignored). Note: S331 `origin` is `Remaker-Digital/groundtruth-kb` (corrected post-S330); commits + push are owner-explicit-action territory and not done in this session. The Agent-Red-files-at-GT-KB-root touch work performed in S331 (none — only platform-rule + bridge-thread + memory + KB-insert work) is governed by the now-ACTIVE pending-migration waiver per its WAIVER POLICY scope.
- **Active release target:** v0.7.0-rc1 — UNBLOCKED PATH: complete ISOLATION-018 file migration → push GT-KB framework changes (incl. version bump from Slice 8 + concurrent-test fix from Slice 8.6) to `Remaker-Digital/groundtruth-kb` → verify GT-KB framework CI green → tag v0.7.0-rc1 on GT-KB framework repo → publish to PyPI via `Release` workflow.
- **Branches:** `main` = production (v1.98.92, `6f857e89`). `develop` = active.
- **Production:** v1.98.92 HIBERNATING since 2026-04-27. Resume runbook: `memory/agent-red-hibernation-runbook-2026-04-27.md`.
- **Smart poller ACTIVE (S320 VERIFIED):** Windows Scheduled Task `GTKB-SmartBridgePoller` running. Doctor: `groundtruth-kb/src/groundtruth_kb/project/doctor.py:_check_smart_bridge_poller`. State at `.gtkb-state/bridge-poller/`.
- **CI:** Lint GREEN. Python tests partial. Security Scan + SonarCloud + Dependabot active.
- **GitHub:** Release v1.98.89 published. 3 open issues. Copilot Pro + CodeRabbit PRO active.
- **SonarCloud:** Org `mike-remakerdigital`. agent-red private. groundtruth public.
- **groundtruth-kb:** Local source `0.7.0rc1` (in-repo); PyPI tag `v0.6.1` no longer used in CI.
- **Knowledge DB:** `groundtruth.db` at repo root (gitignored since 2026-04-24, commit `23a54af3`). 2,105+ specs / 11,055+ tests / 710+ deliberations. ChromaDB at `.groundtruth-chroma/`.
- **Deliberation Archive (SPEC-2098):** ALL 6 PHASES COMPLETE. WI-3168 migration DONE.
- **Commercial Readiness:** 7/7 implemented; 4/7 verified. Remaining: SPEC-1831/1832/1833 at implemented.
- **Rate Limits:** 300 RPM/tenant, 10 RPM floor, platform admin exempt.
- **Release Plan:** Steps 1-3 COMPLETE. Step 4 (beta feedback) IN PROGRESS.

## Feedback Index
- [Worktree drift pattern](feedback_worktree_drift_pattern.md) — Don't work from `.claude/worktrees/*` branches behind develop. S307.
- [No hardcoded paths](feedback_no_hardcoded_paths.md) — Use relative/discovered paths or env vars; 5-category triage. S307.
- [Pedagogical comments](feedback_pedagogical_comments_standard.md) — Module docstrings + why-comments + rationale links. S307.
- [Prime Builder default role](feedback_prime_builder_default_role.md) — Always start as Prime Builder. S305.
- [Canonical content in active surfaces](feedback_canonical_content_in_active_surfaces.md) — Canonical terms in CLAUDE.md/AGENTS.md/.claude/rules/. S305.
- [Bridge autonomy](feedback_bridge_autonomy.md) — Never ask owner to sweep/check/repair bridge.
- [Poller autonomy](feedback_poller_autonomy.md) — Leave working pollers alone.
- [Poller circular dependency](feedback_poller_circular_dependency.md) — Bridge protocol can't self-heal a broken poller. S291.
- [Codex poller not hung](feedback_codex_poller_not_hung.md) — codex exec buffers stdout; check stderr. S292.
- [Prioritization by dependencies](feedback_prioritization_by_dependencies.md) — Bridge correctness P0; everything else by dependency graph.
- [Session-start CronCreate poller](feedback_interactive_poller_monitor.md) — MANDATORY at session start. S292.
- [Post-impl report hygiene](feedback_postimpl_report_hygiene.md) — Class-qualified pytest IDs. S299.
- [Session-start ORIENT block](feedback_session_start_orient_block.md) — 7-item ORIENT block, fixed format.
- [Iterate fast on main](feedback_iterate_fast_on_main.md) — GT-KB pre-production; merge+push frequently.
- [Quality-first autonomy](feedback_quality_first_autonomy.md) — Default to max-quality option autonomously.
- [Don't re-elicit on agreement](feedback_dont_re_elicit_on_agreement.md) — Owner quoting recommendation = approval. S302.
- [AskUserQuestion for ALL decisions](feedback_use_askuserquestion_for_all_decisions.md) — Use AskUserQuestion for every owner decision. S302.
- [No deferrals ever](feedback_no_deferrals_ever.md) — Never defer; max quality+completeness always. S302.
- [Instrument before rule-making](feedback_instrument_before_rule_making.md) — Hypothesize → instrument → backlog → decide. S302.
- [Verify git diff before reporting](feedback_verify_git_diff_before_reporting.md) — Edit success ≠ committed. S302.
- [Read INDEX comments before GO execution](feedback_read_index_comments_before_executing_go.md) — Scan INDEX.md HTML comments. S302.
- [Bridge drift pattern](feedback_bridge_drift_pattern.md) — Surgical revert, not rewrite. S304.
- [No lossy compression of agent I/O](feedback_no_lossy_compression.md) — Quality > cost. S311.
- [MCP verification required](feedback_mcp_verification_required.md) — Verify MCP capabilities end-to-end before depending on them. S311.
- [Don't formalize implicit principles](feedback_dont_formalize_implicit_principles.md) — Ask before auto-DELIB. S312.
- [Verify source before parallel proposals](feedback_verify_source_before_parallel_proposals.md) — Each parallel bridge needs source-verification gate. S313.
- [Avoid quoting decision-tracker fragments](feedback_avoid_quoting_decision_tracker_fragments.md) — Quoting matched fragments re-fires the detector. S328.
- [Bare ? = status update](feedback_question_mark_means_status_update.md) — Single "?" = owner status request. S328.
- [Status updates probe live INDEX + sub-agent state](feedback_status_updates_load_index_and_subagent_state.md) — Multi-agent env moves between turns. S328.
- [GroundTruth-KB canonical project URLs](feedback_groundtruth_kb_canonical_project_urls.md) — "the GitHub", "repo", and related aliases resolve to the configured GT-KB GitHub URL, not local remote drift.
- [Run preflight before filing bridge proposals](feedback_preflight_before_filing_bridge_proposals.md) — Before drafting any bridge proposal, run `python scripts/bridge_applicability_preflight.py` against the intended bridge-id; cite cross-cutting governance specs of the artifact type, not just topic-specific specs. S331.
- [Project external resource registry](project_external_resource_registry.md) — Canonical URLs/identities for external resources and alias resolution.

## Strategic Thesis
- [Pipeline vision](project_vision_statement.md) — Software factory: owner delivers specs, pipeline produces deployable SaaS.
- [Pipeline is the product](project_strategic_thesis.md) — Agent Red validates the pipeline; groundtruth-kb is the core IP.
- [No attachment to implementations](feedback_no_attachment.md) — Adopt better alternatives without hesitation.
- [GT-KB non-disruptive upgrade priority](project_gtkb_non_disruptive_upgrade_priority.md) — CTO env upgrades non-disruptively. S298.
- [GT-KB Azure SaaS Readiness vision](project_gtkb_azure_saas_readiness_vision.md) — 15 deficiencies, 7 workstreams. S298.

## Plan-of-Record
- [Production Readiness v1.98.92](project_plan_of_record.md) — 16-step plan. Steps 1-13, 15 COMPLETE. Step 14 blocked on carrier. Step 16 PENDING.
- **Production OPERATIONAL** v1.98.92. 1 tenant: Remaker Digital. minReplicas=2 (currently hibernating per S314).
- **Step 14:** E2E phone OTP smoke, blocked on toll-free carrier (App 346df3eb).
- **Step 16:** Spec hygiene remediation: 118 untested specs + 10,440/11,066 orphan tests. Deferred until post-production.
- **WI-3156:** deploy.py scaling enforcement.
- **Bridge infrastructure (S295 permanent fix):** `.claude/hooks/`, `.claude/settings.json`, `.claude/rules/bridge-essential.md`, ps1/vbs scripts tracked via `!`-negation in `.gitignore`. Commit `94392a1b`.

## Standing Operating Decisions
- **2026-04-09 - Bridge ownership:** For bridge runtime/protocol/poller/worker/handshake work, Codex implements; Prime reviews.
- **2026-04-09 - Bridge protocol model:** Asynchronous message passing; not all messages require replies.
- **2026-04-09 - Bridge restart bias:** Don't restart healthy bridge for state cleanup; only for concrete reason.

## Recent Sessions
Detailed session content lives in git history (commits referenced) and `bridge/*-NNN.md`. Single-line hooks here. For deeper context use `git log --oneline --grep=S<NNN>` or read the cited bridge files.

- S331: ISOLATION-018 scoping unblocked. Pending-migration waiver bridge thread completed full cycle (NO-GO → REVISED → GO → owner-approved DELIB body via AskUserQuestion → packet → MemBase insert v1 → 7 tests PASS → REPORT VERIFIED). DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER v1 ACTIVE; in-flight Agent Red root-file work now covered by cited exception. Umbrella scoping bridge: NEW → NO-GO -002 (F1+F2+F3) → REVISED -003 → NO-GO -004 (F1: 18.B inconsistency) → REVISED -005 → GO -006. 12 sub-slices 18.A through 18.L confirmed for actual file migration. Process retrospective: "all three" corrective for the cross-cutting-spec citation gap — feedback memory `memory/feedback_preflight_before_filing_bridge_proposals.md`, rule update bridge GO'd at `bridge/gtkb-pre-filing-preflight-rule-002.md`, hook upgrade bridge NO-GO at `bridge/gtkb-pre-filing-preflight-hook-002.md` (F1 high-severity: preflight script needs content-aware mode for pending Write content). 0 commits this session (working tree carries all changes; commit-and-push deferred to next session).
- S330: Slice 8.6 CI-failure triage Phase 1+2 (43 rows). CI seed script + fixture + workflow step + groundtruth-kb pin fix + 5 rehearse skips + row-36/37/38 loosened + relative-parts SKIP_DIRS fix + pip<26 pin + Docker Scout 2-CVE SARIF waiver. See `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-*.md`.
- S329: ISOLATION-017 Slices 5/6/7 VERIFIED + 2 NO-GO bridges closed via supersession + Slice 8 REVISED-1 awaiting Codex. ~30 commits. See `bridge/gtkb-isolation-017-slice{5,6,7}-*-2026-05-03-*.md`.
- S328: ISOLATION-017 Slice 4 VERIFIED + Slice 5 GO + wrap-prep. 0 commits. Slice 4: 12-version cycle / 4 NO-GO/REVISED rounds. work_list rows 28-31. Stop-hook disabled via `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0`.
- S327: 3 governance Slice 1s landed (Backlog DB / Term Primer / Term Disambiguation). Wrap commit `c73001b8`.
- S326: ISOLATION-017 Slices 1, 2, 2.5 VERIFIED. 16 commits. 8 Codex NO-GOs each catching real defects. New feedback: probe-live-state-before-quoting-counts. Slice 3 inherits 22-file deferred-registration obligation.
- S325: pre-S326 (see git history).
- S324: Priority elevation + dashboard-link cascade closed. ~50 commits. ISOLATION-016/017/018/019 sequence elevated.
- S323: pre-S324.
- S322: Triage + mojibake VERIFIED + Slice A spec-event-surfacer implemented (post-impl NO-GO concurrency). ~45 commits. AskUserQuestion adopted as primary primitive.
- S321: Governance foundation + hard-block hook LIVE + 25 KB specs + DA-backed. ~80 commits. Bridge-compliance-gate hook hard-blocks non-compliant Write/Edit.
- S320: Smart-poller activation + Phase 1 isolation TERMINALLY CLOSED. ~40 commits. Smart-poller VERIFIED at -012 (4 NO-GO/REVISED cycles).
- S319: Drift triage + DORA-001b Track 1. 11 commits. 3 bridge threads VERIFIED. Working tree fully clean.
- S318: Generator-hardening triad terminally closed. 19 commits. 5 threads VERIFIED. Lane achieves status:ok + violations:0.
- S317: Massive parallelization-driven cleanup. ~27 commits. 8 threads VERIFIED. ~80 carryover untracked files migrated into git. Telemetry-churn-policy.
- S316: 3 deletion-readiness manifests VERIFIED + application-isolation contract foundation (sub-slice 1 VERIFIED). E:\Claude-Playground archived. Lesson: explicit-destructive-action-authorization saved.
- S315: CRITICAL ROOT-ISOLATION REMEDIATION. `.claude/rules/project-root-boundary.md` filed. 104/104 auto-memory files migrated to `E:\GT-KB\memory\`. ~26 commits.
- S314: Wave 2 closure (10/11 VERIFIED + 1 NO-GO awaiting revision) + Agent Red 5-day hibernation executed. ~9 commits.
- S313: Wave 2 dense bridge cycle: 8 of 11 lanes shipped + 3 fix bridges VERIFIED. ~25 commits.
- S312: Wave 2 Stage B split-pattern cluster complete. Slices 4-5-6 VERIFIED. 2 new DELIBs (role-contract effectiveness + deterministic services principle). ~25 commits.
- S311: KB recovery (Drive-induced corruption) + Wave 2 foundation FULLY VERIFIED. `.driveignore` permanent fix. 2 new feedback memories. ~19 commits.
- S310: 5 threads VERIFIED. ADR-ISOLATION-APPLICATION-PLACEMENT-001. ~25 commits across develop + groundtruth-kb upstream.
- S309: 4 threads VERIFIED. GTKB-STARTUP-ENHANCEMENTS filed. P1 landed at `3caa034d`. 14 commits.
- S308: Bridge-poller halt directive. Filed three S309-carryover NO-GOs.
- S307: Worktree drift incident. No-hardcoded-paths + pedagogical-comments directives saved.
- S305-S306: ISOLATION Phase 3-7 baselines VERIFIED + Phase 8/9 plans VERIFIED. 4 new bridge threads + backlog hygiene. PROPOSAL-STANDARDS, DA-ENFORCEMENT, BACKLOG-DISCIPLINE programs scoped.
- S303-S304: Bridge restored. D3 azure-iac-skeleton VERIFIED. D4 azure-cicd-gates REVISED-2.
- S298-S300: v0.6.0 + v0.6.1 to PyPI. Tier A Phase A complete. Non-disruptive upgrade primitive.
- S294-S297: 4B mypy/coverage/docstrings to 39→0 / 70% / 85%. v0.5.0 Developer Preview.
- S288-S293: Phase 4 Spec Pipeline COMPLETE (8 features VERIFIED, 600 tests). Codex poller incident.
- S280-S287: Multiple PyPI releases, GT-KB docs Phases 0-8, deliberation archive C1-C6.
- S270-S279: v1.98.91-92 production deploy. ACS SMS. SonarCloud activation.
- S259-S269: ADR-004 canonical identity + bridge v3 + production incidents + P0 encryption incident. See `CLAUDE_ARCHIVE.md`.
- S258 and earlier: see `CLAUDE_ARCHIVE.md`.

## Protected Files (DO NOT MODIFY)
- `branding/logo/SVG/icon-master.svg`, `branding/logo/SVG/primary-logo-no-wordmark.svg`
- `branding/logo/PNG/icon-master.png`, `branding/logo/PNG/primary-logo-no-wordmark.png`

## Quick Reference
- **GroundTruth-KB GitHub URL:** https://github.com/Remaker-Digital/groundtruth-kb. Conversational aliases "the GitHub", "repo", "the repo", and "GitHub repo" resolve here unless explicitly scoped otherwise.
- **Resource aliases config:** `.claude/rules/project-resource-aliases.toml`; readable index `memory/project_external_resource_registry.md`.
- **Azure:** Subscription 4dce2122, ACR acragentredeastus.azurecr.io, Cosmos cosmos-agentred-eastus, KV kv-agentred-eastus, Redis redis-agentred-eastus (C1, TLS).
- **API Gateway:** agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io
- **Docs site:** https://agentredcx.com (GHA from main). **Storefront:** https://blanco-9939.myshopify.com/
- **Brand color:** #ff3621. **Email:** Titan SMTP primary, ACS fallback.
- **Knowledge DB:** `groundtruth.db` at repo root (gitignored) — SQLite, web UI localhost:8090, Python API `tools/knowledge-db/db.py`.
- **GroundTruth KB:** in-repo `groundtruth-kb/` (editable install via `requirements-test.txt`). PyPI `v0.6.1` no longer used in CI.
- **Scripts:** `seed_tenant.py` (9-phase), `upgrade_verification.py` (35 assertions), `test_pipeline.py` (13 phases, canonical E2E runner), `membase_ci_seed.py` (CI fixture seed S330).
- **Admin SPAs:** standalone (port 3300), shopify, provider (port 3400). All have `dev:mock` mode.
- **SPEC-1673:** Provider MUST NOT hold raw tenant API keys.

## Memory Files
- [project_backlog018_plan.md](project_backlog018_plan.md) — BACKLOG-018 plan (6 phases, 55 specs). DEFAULT work priority.
- [feedback_codex_bridge_protocol.md](feedback_codex_bridge_protocol.md) — Codex role, $20/mo budget, prime-bridge notification discipline.
- [testing-research.md](testing-research.md) — S210 research; AI-generated code testing; 4-phase guardrail plan.
- [feedback_artifact_boundaries.md](feedback_artifact_boundaries.md) — KB for project artifacts; MEMORY.md for operational patterns. S218.
- [feedback_docs_release_gated.md](feedback_docs_release_gated.md) — Public docs release-gated with same rigor as code. S218.
- [feedback_deploy_gate_token.md](feedback_deploy_gate_token.md) — Production deploy gate = env token. S218.
- [project_architecture_specs.md](project_architecture_specs.md) — Lightweight architecture spec tagging (GOV-21 pending). S219.
- [feedback_taxonomy_simplicity.md](feedback_taxonomy_simplicity.md) — Collapse `architecture` type into ADR/DCL.
- [feedback_bridge_protocol.md](feedback_bridge_protocol.md) — Near-real-time autonomous bridge exchange. 60s ack. S223.
- [project_groundtruth_lineage.md](project_groundtruth_lineage.md) — GroundTruth = evolution of membase-4-claude. S237.
- [canonical_vocabulary.md](canonical_vocabulary.md) — Interim definitions for MemBase/DA/MEMORY.md/GT-KB/Prime/LO. S299.
- [project_s299_governance_lessons.md](project_s299_governance_lessons.md) — S299: 3 gaps; 5 owner decisions pending S300.
- [project_cto_trial_onboarding_docs.md](project_cto_trial_onboarding_docs.md) — Weekend CTO deadline; scope bridge GO'd.
- [feedback_canonical_terminology_governance.md](feedback_canonical_terminology_governance.md) — Pre-proposal DA search MANDATORY. S299.
- [feedback_agent_red_is_adopter_not_author.md](feedback_agent_red_is_adopter_not_author.md) — Historical note from S299; superseded by owner correction 2026-05-04: Agent Red is a separate project, not part of GT-KB.
- [feedback_complexity_fragility.md](feedback_complexity_fragility.md) — Evaluate every proposal element for coupling/testability/maintenance. S253.
- [project_widget_roadmap_decisions.md](project_widget_roadmap_decisions.md) — 4 owner decisions for widget roadmap. S253.
- [feedback_collaboration_protocol.md](feedback_collaboration_protocol.md) — MANDATORY dev lifecycle. S254.
- [feedback_environment_safety.md](feedback_environment_safety.md) — Never modify production without explicit confirmation. S254.
- [feedback_owner_questions.md](feedback_owner_questions.md) — Owner questions are reasoning tests. S256.
- [feedback_build_process.md](feedback_build_process.md) — All builds via GitHub Actions only. S254.
- [project_control_surface_closeout.md](project_control_surface_closeout.md) — 5-phase plan. S253-S254.
- [feedback_tests_before_implementation.md](feedback_tests_before_implementation.md) — Tests MUST be written BEFORE implementation code. S255.

## References
- [Sarah Scenario (GT-KB UX Anchor)](reference_sarah_scenario.md) — 7-phase user journey (DOC-SARAH-SCENARIO).
- [UI Testing Tool Evaluation](reference_ui_testing_tools.md) — Chromatic + axe-core first.
- [Codex automation failure](project_codex_automation_failure.md) — Desktop automations silently fail.

## Project Knowledge (in Knowledge Database)
- **Cross-cutting lessons (85+):** `DOC-cross-cutting-lessons` — Python, API, Cosmos, build, testing, frontend, infra patterns.
- **Owner preferences (6):** `DOC-owner-preferences` — quality, process, product directives.
- **Shopify production deployment guide:** `DOC-141`.
- **Docs site deployment:** KB procedure `docs-site-deploy`.
- **Roadmap planning wiki:** `wiki/Roadmap-planning.md` — P1 COMPLETE. P2-P7 pending.
- **Protected behaviors:** PB-* specs in KB — machine-verifiable assertions checked at session start.
- [Production deploy approval](feedback_production_deploy_approval.md) — Require explicit "deploy to production" confirmation.
