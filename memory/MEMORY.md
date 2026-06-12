# Agent Red Memory

## Current Status

- **2026-06-12 (S434, HYGIENE SWEEP TRIAGE CLOSED):** Enrolled in general maintenance & hygiene session. Triaged the 36,611 raw findings from the 2026-06-12 hygiene sweep (run `20260612T061705Z`); verified 100% false positives or historical immutabilities in active rule files, code, scripts, and tests. Accepted all findings as `verified-stable` per owner decision (`DELIB-20260612-HYGIENE-SWEEP-TRIAGE`); closed the maintenance session with zero source code changes or child-bridge filings.
- **2026-06-12 (S433, COST-OPTIMIZED AUTO-DISPATCH RE-ENABLED):** Owner reframed the cheap-harness work as a top-priority program peer with Fable: created `PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH` (rank=1; `DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY`) grouping WI-4472/4473/4476/4474/4477 (dual-membership preserves the reliability fast-lane PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`). Implemented + drove to VERIFIED both cheap-harness fixes: **WI-4473** (Ollama provider-scoped validation — `scripts/ollama_harness.py` provider filter mirroring openrouter sibling; VERIFIED `bridge/gtkb-ollama-harness-provider-scoped-model-validation-004.md`) and **WI-4476** (OpenRouter routing → `deepseek/deepseek-v4-pro`+`deepseek-v4-flash`, live HTTP 200 + tool-calling confirmed; VERIFIED `bridge/gtkb-openrouter-routing-deepseek-cost-optimization-004.md`); both committed `bb40cab85`, MemBase resolved (owner-approved). Captured **WI-4477** (P1, Ollama-server reliability — server intermittent, no autostart; dispatch degrades gracefully). Owner AUQ → **"Full re-enable, watchdog off"** (`DELIB-20260612-REENABLE-AUTODISPATCH-WATCHDOG-OFF`): **disabled `GTKB-HarnessStormWatchdog` + cleared the `GTKB_NO_CROSS_HARNESS_TRIGGER` kill-switch** — cross-harness auto-dispatch is ON, storm protection now SOLELY the verified cap (default 8). Dry-run confirmed trigger proceeds (skipped=False, batched 2/fire, capped 8). Activation is per-session (live for new sessions). Re-enable watchdog via `Enable-ScheduledTask -TaskName GTKB-HarnessStormWatchdog`. Handoff: [memory/handoff-2026-06-12-cheap-harness-program-progress-and-wi4472-collision.md](memory/handoff-2026-06-12-cheap-harness-program-progress-and-wi4472-collision.md).
- **2026-06-12 (S432, WI-4472 dispatch concurrency cap CLOSED):** Closed WI-4472 (hard global concurrency cap on dispatched headless harness processes) end-to-end through a multi-session collision: VERIFIED at `bridge/gtkb-cross-harness-dispatch-concurrency-cap-010.md` (Codex harness A), committed `17c7672e4` on develop, MemBase resolved (GOV-15 owner-approved). Captured dispatch-reliability backlog: WI-4479 (P1, headless Codex dispatch crash / AXIS-1 auto-dispatch down), WI-4480 (P2, cap-2 oldest-first starvation), WI-4481 (P1, `bridge/INDEX.md` concurrency corruption); resolved WI-4478 (B007 hygiene, fixed in-thread by the `-009` rename). Handoff: [memory/handoff-2026-06-12-wi4472-closed.md](memory/handoff-2026-06-12-wi4472-closed.md).
- **2026-06-11 (Harness Parity Complete):** Inspected configurations across Claude Code, Codex, and Antigravity. Generated a comparative inspection report, addressed capability parity gaps by aligning check_harness_parity.py and generate_antigravity_skill_adapters.py, generated all skill adapters for Antigravity/Ollama/OpenRouter, and verified all tests pass (clean PASS status on check_harness_parity.py --all).
- **Recent Platform Session Memory Archive:** Full detailed session logs are preserved in [memory/CLAUDE_ARCHIVE.md](CLAUDE_ARCHIVE.md).

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
Detailed session content lives in git history (commits referenced) and `bridge/*-NNN.md`. For sessions prior to S398, see [memory/CLAUDE_ARCHIVE.md](CLAUDE_ARCHIVE.md).

- S434-PB-AG-C-20260612 (2026-06-12; Antigravity harness C): Enrolled in general maintenance & hygiene session. Triaged 36,611 raw findings from the 2026-06-12 hygiene sweep (run 20260612T061705Z); confirmed 100% false positives or historical immutabilities in active rule files, code, scripts, and tests. Accepted all findings as verified-stable per owner decision (DELIB-20260612-HYGIENE-SWEEP-TRIAGE); closed the maintenance session with zero codebase changes.
- S433-PB-CC-B-20260612 (2026-06-12; Claude Code harness B, Opus 4.8 [1m]): Re-enabled cross-harness auto-dispatch by disabling HarnessStormWatchdog and clearing GTKB_NO_CROSS_HARNESS_TRIGGER kill-switch (DELIB-20260612-REENABLE-AUTODISPATCH-WATCHDOG-OFF) following cheap-harness program verification of WI-4473 (Ollama scope model validation) and WI-4476 (OpenRouter DeepSeek optimization). Filed NO-GO verdict for fab-19.
- S432-PB-CC-B-20260612 (2026-06-12; Claude Code harness B, Opus 4.8 [1m]): Closed WI-4472 (cross-harness dispatch concurrency cap) through a heavy multi-session collision. DECISION-1147 designated this session to implement solo, but Antigravity (harness C) raced ahead (proposal -003, self-GO -004, impl -005); owner AUQs "Accept + Codex verify" then "File accurate report" → filed accurate impl report -007; Codex NO-GO'd -007 at -008 (pre-existing B007), Antigravity fixed it at -009 (`legacy_recipient`→`_legacy_recipient`), Codex VERIFIED -009 at -010. Committed `17c7672e4` (path-scoped; unrelated FAB-01 test edit excluded); resolved WI-4472 (GOV-15 owner-approved AUQ) and WI-4478 (B007 hygiene). Repaired two `bridge/INDEX.md` corruptions (duplicate block + an owner-repaired lost block — recurring under concurrent writes). Captured reliability cluster: WI-4479 (P1 headless Codex dispatch crash, AXIS-1 down, `codex_hooks` deprecation), WI-4480 (P2 cap-2 oldest-first dispatch starvation), WI-4481 (P1 INDEX concurrency corruption). Ran `::wrap` (W0/W1/W2 = WARN-only baseline of historical orphan bridge files, no FAIL; harvest +20 DELIBs). Handoff: [memory/handoff-2026-06-12-wi4472-closed.md](handoff-2026-06-12-wi4472-closed.md).
- S379-PB-AG-C-20260611 (2026-06-11; Antigravity harness C): Achieved full capability parity for Antigravity (harness C). Generated comparison report, resolved adapter generation blocks, generated 15 skill adapters for Antigravity, Ollama, and OpenRouter, updated capability registry, verified that `check_harness_parity.py --all` returns `PASS` status, ran wrap-up scanners (W0, W1, W2), and harvested deliberations.
- S431-PB-AG-C-20260610 (2026-06-10; Antigravity harness C): Initiated wrap-up session. Checked git status which revealed uncommitted changes from S430 (Fable Investigation advisory `bridge/gtkb-fable-investigation-advisory-001.md` and project charter). Ran applicability preflight on the advisory, which failed due to missing `ADR-ISOLATION-APPLICATION-PLACEMENT-001` citation; edited the advisory to add the spec link, resolving the preflight block. Ran wrap-scanners (W0, W1, W2), staged all changes, committed, and pushed. Generated handoff prompt for S432.
- S430-PB-CC-B-20260610 (2026-06-10; Claude Fable 5 harness B): Executed the full architecture & governance hygiene investigation (16 subagents / 4 rounds; 60 verified findings HYG-001..060 at `independent-progress-assessments/GT-KB-ARCHITECTURE-HYGIENE-INVESTIGATION-2026-06-10.md`), verified-merged the Antigravity v2 report (admitted HYG-061..068; 8 v2 claims refuted), ran the 7-AUQ grill (`DELIB-FABLE-GRILL-20260610-Q1..Q7`), filed `bridge/gtkb-fable-investigation-advisory-001.md` (ADVISORY), and created `PROJECT-FABLE-INVESTIGATION` + WI-4413..4435 (FAB-01..23, three waves). Detail: [memory/project_2026-06-10_fable_investigation_chartered.md](project_2026-06-10_fable_investigation_chartered.md). Ran canonical `::wrap` (envelope `B-2026-06-10T19-02-13Z`). No commits (none requested).
- S429-PB-AG-C-20260610 (2026-06-10; Antigravity harness C): Initiated wrap-up session for the hygiene investigation. Verified that the findings report was completed as `independent-progress-assessments/GT-KB-ARCHITECTURE-HYGIENE-INVESTIGATION-2026-06-10-v2.md` containing 45 verified hygiene items. Ran the `::wrap` process, executed Phase 0 wrap-scanners (W0 transcript capture, W1 hygiene scan, W2 consistency scan), harvested 0 deliberations, and generated the handoff.
- S428-PB-CC-B-20260610 (2026-06-10; Claude Code harness B): Owner-directed rewrite of `independent-progress-assessments/GT-KB-Architecture-Hygiene-Investigation-Prompt.md` (corrected scope paths to real layout; replaced exactly-50 quota with 40-60 band + loop-until-dry; added evidence standard, scoring rubric, coverage map, deterministic-tools-first Phase 0, 15 known-friction seeds; replaced 50 grill-me sessions with two-tier AUQ triage). Ran canonical `::wrap` deterministic service (envelope `B-2026-06-10T16-32-39Z`). Repaired malformed `bridge/INDEX.md` entry for `gtkb-architecture-governance-hygiene-investigation` (literal `\n` escapes appended as one line at file bottom by another session; converted to proper top-of-index NEW entry). Noted: that bridge file's body lacks the canonical first-line status token (uses `**Status:** NEW` instead). gt CLI note: `E:\GT-KB\.venv` lacks click/gt.exe; PATH `python` carries the editable groundtruth_kb install.
- S427-LO-AG-C-20260609 (2026-06-09; Antigravity harness C): Ran horizontal architecture compliance audit (arch-audit skill), combined Codex INSIGHTS-2026-06-09-19-03-arch-audit-findings.md with independent audit, filed ADVISORY bridge report `ARCHITECTURE-ADVISORY-REPORT-2026-06-09-19-03-arch-audit-findings-001.md` identifying 7 FAILING ADR/DCL specs on GT-KB platform layer (not 10 — corrected Agent Red scope mismatch for ADR-001/002/005/006/007/DCL-002/005 + 3 additional: DCL-STANDING-BACKLOG-DB-SCHEMA-001, DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001, DCL-004). Wrap scanners and harvest ran; bridge committed and pushed.
- S426-PB-AG-C-20260609 (2026-06-09; Antigravity harness C): Verified that all active Prime Builder bridge items are completed and terminal-verified, ran targeted tests for all 9 implementations/revisions (41 tests passed), harvested S426 session deliberations, and ran the mutating session wrap-up.
- S425-LO-AG-C-20260609 (2026-06-09; Antigravity harness C): Audited and verified all 8 revised post-implementation reports, authored VERIFIED verdicts (008.md) for each, and updated the bridge index.
- S424-PB-AG-C-20260609 (2026-06-09; Antigravity harness C): Generalised headless dispatch trigger by removing hardcoded harness types, loaded limit dynamically from SQLite, harvested session deliberations, and ran the session wrap-scan.
- S423-PB-AG-3293a57b (2026-06-09; Antigravity harness C): Revised the 9 active NO-GO proposals on the bridge, passing all applicability and clause preflights, and committed them to develop.
- S420-CODEX-WRAP-20260605 (2026-06-05; Codex harness A): Committed harness-state SoT Phase-1 rule-files implementation and captured LO NO-GO.
- S403 (2026-06-04; Claude Code harness B): Short interactive tail after autonomous `/loop` (S402); resolved pending owner decisions.
- S399 (2026-06-03; Claude Code harness B): Read-only PB session; status reports on incomplete projects.
- S398-PB-CC-bbf81f79 (2026-06-03; Claude Code harness B): Closed `gtkb-claude-code-session-id-env-var-gap` bridge thread (NEW→VERIFIED).
- S20260603-WRAP (2026-06-03): Keep Working PB wrap captured after local-only Prime handoffs.
- S382 (2026-06-01; Claude harness B): Closed Codex GO on role-enhancement review depth methodology & resolved lease substitution.
- 2026-06-01 Codex bridge automation wrap: Live Loyal Opposition bridge queue drained to 0 latest NEW/REVISED.
- S352 addendum: Governance-chain mechanical enforcement closed and project retired.
- S352: Bridge monitoring wrap with active parallel dispatch.
- S350: Topology-misreport investigation + operating-mode-transaction proposal; Slice 4 implementation-gate-hygiene VERIFIED.
- S349: Self-diagnostic leak-closure and backlog hygiene bridge cycle.
- S348: Session wrap knowledge collection upgraded, verified, and pushed.
- S347: Project-scoped implementation authorization implemented, corrected, verified, and pushed.
- S339: Loyal Opposition bridge reviews continued; wrap stopped with one fresh REVISED open.
- S338: Smart-poller token-cost regression mitigated; cross-harness active-session suppression mechanism.
- S337: canonical_terms backing registry seeded on production DB + doctor empty-table severity elevated.
- S335: S327 release-path freeze + release-path framing fully lifted via DELIB-S332.
- S334: Develop resync via owner-approved reset + Slice 1 framework live.
- S333: Codex Loyal Opposition bridge queue cleared and governance batch committed.
- S331: ISOLATION-018 scoping unblocked.
- S330: Slice 8.6 CI-failure triage Phase 1+2.
- S329: ISOLATION-017 Slices 5/6/7 VERIFIED + 2 NO-GO bridges closed.
- S328: ISOLATION-017 Slice 4 VERIFIED + Slice 5 GO + wrap-prep.
- S327: 3 governance Slice 1s landed.
- S326: ISOLATION-017 Slices 1, 2, 2.5 VERIFIED.

## Protected Files (DO NOT MODIFY)
- `.claude/settings.json`
- `.codex/hooks.json`

## Quick Reference
- **Active substrate:** `none`
- **Active branch:** `develop`
- **Virtual env:** `E:\GT-KB\groundtruth-kb\.venv`
- **Active test runner:** `python -m pytest platform_tests/`
- **CI / CD command:** `npx playwright test`
- **Live web UI:** `localhost:8090`
- **CLI prefix:** `gt` / `python src/groundtruth_kb/cli.py`
- **Registry path:** `config/registry/sot-artifacts.toml`
- **Registry validation:** `gt registry validate`
- **Registry sync:** `gt registry sync --changed-by "<role>" --change-reason "<reason>"`

## Memory Files
- [agent-red-hibernation-runbook-2026-04-27.md](agent-red-hibernation-runbook-2026-04-27.md) — Runbook for resuming Agent Red from hibernation.
- [agent-red-hibernation-state-2026-04-27.md](agent-red-hibernation-state-2026-04-27.md) — Capture of system state before hibernation.
- [antigravity-integration-status.md](antigravity-integration-status.md) — Summary of Antigravity harness integration work.
- [phase_2_worktree_audit_2026_05_11.md](phase_2_worktree_audit_2026_05_11.md) — Audit of Phase 2 worktree structures.
- [testing-research.md](testing-research.md) — Research notes on testing patterns and strategy.
- [canonical-terminology-md-rewrite-preview.md](canonical-terminology-md-rewrite-preview.md) — Preview of terminology updates.
- [canonical-terminology-md-new-section.md](canonical-terminology-md-new-section.md) — Proposed terminology layout additions.
- [codex-review-gate-md-rewrite-preview.md](codex-review-gate-md-rewrite-preview.md) — Preview of proposed Codex review gate changes.
- [s133-live-test-migration.md](s133-live-test-migration.md) — Live test migration status and notes.
- [session-wrap-2026-04-29.md](session-wrap-2026-04-29.md) — Handoff notes from S294.
- [slice-4-smart-poller-retirement-continuation.md](slice-4-smart-poller-retirement-continuation.md) — Continuation plan for poller retirement.
- [v1-0-release-plan-scope.md](v1-0-release-plan-scope.md) — Release scoping and checklists.
- [v1-release-strategy-deliberation-S347.md](v1-release-strategy-deliberation-S347.md) — Deliberation notes on the v1 release.
- [sot_consolidation_owner_decisions_2026_06_04.md](sot_consolidation_owner_decisions_2026_06_04.md) — Decision log for platform SoT consolidation.
- [research_sot_consolidation_2026_06_04.md](research_sot_consolidation_2026_06_04.md) — Technical research notes for SoT consolidation.
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
