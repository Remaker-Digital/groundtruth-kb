# GroundTruth-KB Platform Memory

### Current Status

- **2026-06-14 (S440, PB-CC-B AUTONOMOUS SEEDING LOOP):** Dispositioned the PROJECT-GTKB-RELIABILITY-FIXES batch (11 seeded, 5 closed already-fixed) + started the PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY compliance/dispatch batch (new PAUTH; WI-3439/4396 seeded, WI-3448 closed). Sweep commit 8908b6a (43 files). 8 owner AUQs captured as DELIBs. WI-3384 pending. Env defect: venv lacks pytest-timeout (pyproject addopts breaks `python -m pytest`).
- **2026-06-13 (C, Antigravity LO):** Verification & clearing of release candidate path. Running security & quality checks on local Windows 11 environment.
- **2026-06-12 (A-2026-06-12T22-59-14Z, CODEX LO WRAP):** Clean bridge scan. Verified gtkb-fab-03-membase-backup-011 (VERIFIED). WI-4481 index atomic-write repair filed as ADVISORY.
- **2026-06-12 (S436, FABLE PROGRAM DRIVE):** Drove PROJECT-FABLE-INVESTIGATION loop termination (21 FAB threads VERIFIED). Handed off TAFE program drive.
- **2026-06-12 (S434, HYGIENE SWEEP TRIAGE):** Triaged 36k findings (all FP or verified-stable).
- **2026-06-12 (S433, AUTO-DISPATCH RE-ENABLED):** Ollama/OpenRouter fixes VERIFIED. Watchdog off; cross-harness auto-dispatch active.
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
- [Weight peer review by reliability](feedback_peer_review_weighting_by_reliability.md) — Canon-verify lower-capability/relayed peer input (e.g. Gemini); convergence across reasoners ≠ correctness. 2026-06-12.
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
- **2026-04-09 - Bridge restar## Recent Sessions
Detailed session content lives in git history (commits referenced) and `bridge/*-NNN.md`. For sessions prior to S398, see [memory/CLAUDE_ARCHIVE.md](CLAUDE_ARCHIVE.md).

- S440-PB-CC-B-20260614 (2026-06-14; Claude Code B): Autonomous backlog-seeding loop (interactive Prime authoring NEW proposals; swarm implements after GO). Reliability batch (PROJECT-GTKB-RELIABILITY-FIXES, PAUTH batch-1/2) fully dispositioned: SEEDED WI-4464/4480/4441/4527/4512/4519/4521/4524/4522/4528/4530; CLOSED already-fixed WI-4479/4483/4514/4412/4523 (owner GOV-15 AUQs + DELIBs — verify-first triage found them resolved by post-filing registry/config/swarm fixes). Bridge-compliance batch: created PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001 (owner AUQ, DELIB-2026-06-14-BRIDGE-PROTOCOL-COMPLIANCE-DISPATCH-BATCH-ADMISSION; source+test+hook_upgrade+config) admitting WI-3439/3448/4396/3384; SEEDED WI-3439 (Requirement-Sufficiency presence check) + WI-4396 (route work_intent_already_held out of dispatch-failures.jsonl); CLOSED WI-3448 (already-fixed by body-status-token rule, Slice 1); WI-3384 (CLAUSE-IN-ROOT disclosure false-positive) STILL OPEN, next to seed. Swarm implemented/VERIFIED many seeds (WI-4480 VERIFIED; WI-4530/4528/4519/4522/4527 to post-impl). Sweep commit 8908b6a (43 files, +5407/-180; 9 scratch files excluded). LESSONS: (1) propose_bridge auto-injects a "### Helper-suggested candidates / _No prior deliberations: <fill in reason>_" placeholder after substantive Prior Deliberations — strip post-file (re-claim first). (2) clause-preflight CLAUSE-VISIBILITY-BULK-OPS fires on every GOV-STANDING-BACKLOG-001 cite — add single-WI disambiguator (regex matches inventory|review-packet|DECISION DEFERRED|formal-artifact-approval). (3) CLAUSE-IN-ROOT detector refutes ANY out-of-root path literal in a proposal body (even disclosure) — never put literal C:\Users\…/\tmp\… in proposal bodies. ENV DEFECT: groundtruth-kb/.venv lacks pytest-timeout so `python -m pytest` fails on pyproject addopts `--timeout=30` (workaround `-o addopts=""`). Seed toolkit in .gtkb-state/drafts/ (_file_proposal.py, _read_wi.py, _read_cluster_candidates.py, _read_active_projects.py, _admit_*.py, _close_*.py).
- S439-PB-CC-B-20260614 (2026-06-14; Claude Code B): Closed WI-4542/4509/4441 (VERIFIED→resolved; GOV-15 gate is origin-aware — defect/regression need --owner-approved, origin=new resolves autonomously); landed DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001, drove TAFE WI-4546 reconciliation→GO@-004; filed WI-4559 (handoff-generator hardcodes harness-C archive). Handoff: .claude/session/handoff-B-2026-06-14T16-26-36Z.md. Next: WI-4540 marker fix (GO@-004, unblocks interactive go_implementation) → WI-4546 TAFE oracle (GO@-004).
- S438-PB-CC-B-20260613 (2026-06-13; Claude Code B): Implemented WI-4504 Telemetry & WI-4505 Stuck Flow fixes.
- S437-PB-CC-B-20260613 (2026-06-13; Claude Code B): Drove fab-04 to VERIFIED, initiated time-box & claim-gate specs.
- S435-PB-CC-B-20260612 (2026-06-12; Claude Code B): TAFE program appraisal & Phase 0 drive.
- S434-PB-AG-C-20260612 (2026-06-12; Antigravity C): General maintenance & hygiene sweep triage.
- S433-PB-CC-B-20260612 (2026-06-12; Claude Code B): Re-enabled auto-dispatch trigger.
- S432-PB-CC-B-20260612 (2026-06-12; Claude Code B): Closed WI-4472 (concurrency cap) via multi-session collision.
- S379-PB-AG-C-20260611 (2026-06-11; Antigravity C): Achieved full capability parity for Antigravity.
- S431-PB-AG-C-20260610 (2026-06-10; Antigravity C): Resolved isolation advisory preflight blocks.
- S430-PB-CC-B-20260610 (2026-06-10; Claude B): Executed hygiene investigation & chartered Fable Investigation.
- S429-PB-AG-C-20260610 (2026-06-10; Antigravity C): hygiene investigation findings finalization and wrap-up.
- S428-PB-CC-B-20260610 (2026-06-10; Claude B): Rewrote hygiene investigation prompt & repaired bridge index.
- S427-LO-AG-C-20260609 (2026-06-09; Antigravity C): Compliance audit finding 7 failing platform specs.
- S426-PB-AG-C-20260609 (2026-06-09; Antigravity C): Verified all active Prime Builder items, ran tests, session wrap.
- S425-LO-AG-C-20260609 (2026-06-09; Antigravity C): Audited & verified 8 post-implementation reports.
- S424-PB-AG-C-20260609 (2026-06-09; Antigravity C): Generalized headless dispatch trigger limits.
- S423-PB-AG-3293a57b (2026-06-09; Antigravity C): Revised 9 active NO-GO proposals on the bridge.
- S420-CODEX-WRAP-20260605 (2026-06-05; Codex A): Committed harness-state SoT Phase-1 rule-files.
- S403 (2026-06-04; Claude Code B): Resolved pending owner decisions.
- S399 (2026-06-03; Claude Code B): Read-only PB session; status reports on incomplete projects.
- S398-PB-CC-bbf81f79 (2026-06-03; Claude Code B): Closed gtkb-claude-code-session-id-env-var-gap bridge thread.
- S20260603-WRAP (2026-06-03): Keep Working PB wrap captured after local-only Prime handoffs.
- S382 (2026-06-01; Claude B): Closed Codex GO on role-enhancement review depth methodology.
- S20260601 (2026-06-01): Codex bridge automation wrap.
- S352 addendum (2026-05-31): Governance-chain mechanical enforcement closed.
- S352 (2026-05-31): Bridge monitoring wrap.
- S350 (2026-05-31): Topology-misreport investigation + operating-mode-transaction proposal.
- S349 (2026-05-31): Self-diagnostic leak-closure and backlog hygiene bridge cycle.
- S348 (2026-05-30): Session wrap knowledge collection upgraded, verified.
- S347 (2026-05-30): Project-scoped implementation authorization.
- S339 (2026-05-29): Loyal Opposition bridge reviews continued.
- S338 (2026-05-29): Smart-poller token-cost regression mitigated.
- S337 (2026-05-29): canonical_terms backing registry seeded on production DB.
- S335 (2026-05-28): S327 release-path freeze + release-path framing fully lifted.
- S334 (2026-05-28): Develop resync via owner-approved reset.
- S333 (2026-05-28): Codex Loyal Opposition bridge queue cleared.
- S331 (2026-05-27): ISOLATION-018 scoping unblocked.
- S330 (2026-05-27): Slice 8.6 CI-failure triage Phase 1+2.
- S329 (2026-05-26): ISOLATION-017 Slices 5/6/7 VERIFIED.
- S328 (2026-05-26): ISOLATION-017 Slice 4 VERIFIED + Slice 5 GO.
- S327 (2026-05-25): 3 governance Slice 1s landed.
- S326 (2026-05-25): ISOLATION-017 Slices 1, 2, 2.5 VERIFIED.

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
