# Agent Red Memory

## Current Status
- **Fresh-session handoff (2026-05-07, end of S335):** S335 wrap commit (pending push) records the lift-feature-freeze cycle — `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` inserted, S327 freeze + release-path framing fully lifted, 7 target WIs cleared of freeze/defer language, work_list.md rewritten with per-leverage priority bands (no freeze-derived sequencing). Bridge `gtkb-lift-feature-freeze` VERIFIED at `-012`. **Acceleration items now actionable:** Backlog DB Slices 2-7, `GTKB-ARTIFACT-RECORDER-CLI`, Term Primer Slices 2-5, Resource Disambiguation Slices 2-5. **Preserved release blockers:** `DELIB-S330` canonical Agent Red migration prerequisite + P0 secrets-purge override + in-flight Slice 8.5/8.6 — rc1 tag still NOT authorized. Live `bridge/INDEX.md`, not this summary, remains authoritative for queue status.
- **S335 session-numbering disclosure:** the lift-feature-freeze bridge artifacts and the DELIB use `S332` in content/IDs; the actual session is S335. Future references to this work cite the DELIB ID `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` and the bridge thread `gtkb-lift-feature-freeze`; the session is recorded as S335 in MEMORY.md.
- **Loyal Opposition bridge queue:** Live scan at S334 close showed 0 latest `NEW`/`REVISED` for Loyal Opposition; my two S334 filings (REVISED-3 and Slice-1 impl report) returned VERIFIED + GO during the same session.
- **Prime Builder next bridge actions:** Revise legacy `NO-GO` items still open from prior sessions: `gtkb-pre-filing-preflight-rule`, `gtkb-pre-filing-preflight-hook`, `gtkb-env-inventory-drift-control-001`, `gtkb-harness-parity-baseline`. Implement `GO`'d `gtkb-codex-bridge-compliance-gate-parity-008` (REVISED-3 implementation: parity-checker extension + `test_codex_parity_requires_bridge_compliance_gate_when_hooks_enabled` + negative fixture). Triage the 8 in-flight `gtkb-isolation-018-*` files left untracked since prior sessions.
- **Azure OpenAI key rotation:** confirmed rotated 2026-05-04. Fingerprint comparison (sha256:0..16): pre-reset leak `67bc4d57bc0a4762`; current `.env.local` `abff80a02123ad08`; both 84-char Azure-format. New value lives only in gitignored `.env.local`.
- **Secrets P0:** `gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan` is `VERIFIED` for approval-packet preparation only. No mirror rehearsal, live history rewrite, force-push, tag operation, credential action, release, or deployment is approved.
- **Harness roles / inventory:** Durable role map currently records Codex `A` as `loyal-opposition` and Claude `B` as `prime-builder`; dev-environment inventory was regenerated and drift check passed clean.
- **Prime-actionable CI blocker:** GitHub Actions `Release Candidate Gate` failed on `origin/develop` commit `6e04e60e`; current repair targets six stale/drifted Python-gate assertions.
- **Canonical repo aliases:** GT-KB aliases resolve to `https://github.com/Remaker-Digital/groundtruth-kb`; Agent Red resolves to `https://github.com/mike-remakerdigital/agent-red` only when explicitly scoped.
- **Release target:** v0.7.0-rc1 remains the GT-KB framework release target; irreversible Agent Red migration/cutover remains blocked until deployability preservation is verified or waived.
- **Production:** v1.98.92 hibernating since 2026-04-27. Resume runbook: `memory/agent-red-hibernation-runbook-2026-04-27.md`.
- **Smart poller:** S320 VERIFIED; Windows task `GTKB-SmartBridgePoller`, state under `.gtkb-state/bridge-poller/`.
- **Knowledge DB:** `groundtruth.db` at repo root is gitignored; ChromaDB retrieval aid at `.groundtruth-chroma/`.

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

- S335: **S327 release-path freeze + release-path framing fully lifted via DELIB-S332.** Owner directive 2026-05-07: "remove all FREEZE or HOLD or DEFER states from all plans and work items. They are all stale." AUQ #1 scope `A + B + C + H`. AUQ #2 approve+extend `Approve, but also lift S327 release-path goal entirely`. Bridge `gtkb-lift-feature-freeze` cycle: NEW → 4 NO-GO/REVISED rounds (-002 brittle CLI/semantic-search → -003; -004 padding/case bugs/missing baseline/status_detail-reintroduces-freeze → -005 with one in-place self-fix; -006 Bash-only commands/missing approval-gate binding → -007) → GO at -008 → 2 self-detected mid-impl defects (Step 3 `fields=` kwarg no-op + U4 baseline overreach, both caught by tests) → post-impl -009 → NO-GO -010 (criterion 7 pending + count inconsistency) → REVISED -011 → VERIFIED at -012. Implementation: `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` v1 inserted with `GTKB_FORMAL_APPROVAL_PACKET` env binding; `memory/work_list.md` 4 sections rewritten (S327 RELEASE PATH header, freeze paragraph, Default idle work directive replaced with per-leverage priority bands, "Deferred during release path" section deleted, GTKB-GOV-007 PAUSED tag lifted); 7 target WIs updated to v3 with current-state-only `status_detail` (no freeze/defer/hold/paused/parked vocabulary); 7 no-op v2 versions remain in append-only history; all 12 acceptance + unchanged-surface tests PASS; criterion 7 pytest sanity-check WAIVED (pre-existing fallout from `687f4707` 18.C inventory move; follow-on WI candidate `GTKB-FIX-DEV-ENV-INVENTORY-DRIFT-TEST-FIXTURE`). Preserved: `DELIB-S330` canonical Agent Red migration prerequisite, P0 secrets-purge override, in-flight Slice 8.5/8.6 work — rc1 tag still NOT authorized. **Session-numbering disclosure:** all bridge artifacts and the inserted DELIB use "S332" in their content/IDs (the DELIB ID is `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` and `session_id=S332` field). This was a Prime-side numbering error; the actual session is S335 (next after S334). Artifact names + IDs are kept as filed; this entry is the authoritative MEMORY.md record. Pre-impl session work: prioritization analysis surfacing top acceleration items (Backlog DB Slices 2-7, `GTKB-ARTIFACT-RECORDER-CLI`, `GTKB-OPS-CURRENT-STATE-MONITORING-001`, pre-filing preflight hook/rule revisions, Term Primer + Disambiguation Slices 2-5). Quality 91.2/100. Assertion check: 1654/1688 PASS, 34 pre-existing FAIL (all documentation specs from prior sessions; no S335 regressions).
- S334: **Develop resync via owner-approved reset + S334 plan items 1-4 closed + Slice 1 framework live.** Discovered local develop was on the pre-S307-filter-repo lineage and still carried the Azure OpenAI key in `scripts/agent-container-template.yaml` working-tree (inherited from pre-rewrite baseline; no S334-or-later commit ever touched the file). Owner-approved AUQ path A: `git reset --hard claude/s333-audit-remediation` (run by owner; destructive-gate hook hard-blocked agent-side execution as designed). Today's work replayed on realigned baseline. AUQ-committed plan: (1) `gtkb-codex-backlog-cleanup-retroactive-review` Phase 1 implemented under GO at -004 (read-only inventory + review-packet generators + 6/6 tests; 119 work-items / 12 transitions / 54 consequential flags; VERIFIED at -006); (2) `gtkb-codex-bridge-compliance-gate-parity` REVISED-2 NO-GO at -006 → REVISED-3 at -007 added Change 7 parity-checker enforcement with SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001 A1 named test → GO at -008; (3) NEW `gtkb-adr-dcl-clause-test-enforcement-001` (Slice 1 of GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001) → GO at -002 → implemented (5-fixture clause registry TOML + advisory-mode `scripts/adr_dcl_clause_preflight.py` CLI + 6/6 tests + `.claude/rules/file-bridge-protocol.md` advisory section) → VERIFIED at -004; (4) develop pushed FF (commits `fef42fe1` + `84e15a8c`). Azure OpenAI key rotation confirmed via sha256-prefix comparison (different fingerprints; both 84-char Azure format). Wrap-scan emitted 12 pre-existing structural ERRORs (10 recursive snapshot-rule violations + 2 INDEX cites of missing slice-d-non-functional-content files); none S334-introduced; owner explicit override granted to wrap. Quality 91.2/100. Deliberation harvest: skipped (formal-artifact-approval-gate blocked; same precedent as S333 where dry-run scoped to 949 broad records). Self-validation: running the new clause-preflight CLI against the freshly-VERIFIED Phase-1 report shows 5 must_apply / 0 evidence gaps — the framework's first real-world dogfood passes.
- S333: **Codex Loyal Opposition bridge queue cleared and governance batch committed.** Codex switched to Loyal Opposition, processed 7 live bridge items, and committed all staged work as `721f7c69 chore: record GT-KB governance bridge updates` after regenerating the dev-environment inventory baseline. Verdicts filed: `gtkb-claude-session-start-parity-002` GO; `gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan-006` VERIFIED; `gtkb-auq-policy-gates-001-010` VERIFIED; `gtkb-pre-filing-preflight-rule-004` NO-GO; `gtkb-pre-filing-preflight-hook-006` NO-GO; `gtkb-env-inventory-drift-control-001-006` NO-GO; `gtkb-harness-parity-baseline-002` NO-GO. Wrap checks: assertion check `1687/1688 PASS` with expected `DCL-STANDING-BACKLOG-DB-SCHEMA-001` failure; harness parity PASS; inventory drift PASS clean; harvester dry-run broad at 949 would-create, not applied. Final live bridge scan: no LO-actionable `NEW`/`REVISED` entries.
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
