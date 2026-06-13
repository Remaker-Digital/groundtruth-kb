# Loyal Opposition Log - GroundTruth-KB

**Purpose:** Running log of Codex appraisals, evaluations, and questions (Loyal Opposition).
**Location:** `independent-progress-assessments/`.
**Update:** Append new findings each session; update status (`open` -> `resolved`/`deferred`) when Mike decides.

**Format per entry:** Date | Area | Finding | Evidence / context | Suggested action | Status

---

## Entries

### 2026-02-01 - Knowledge base and role setup

| Area | Finding | Evidence | Suggested action | Status |
|------|---------|----------|------------------|--------|
| Process | Cursor had no persistent knowledge of Mike or of opposition findings across sessions. | Mike's request to build a knowledge base and adopt loyal opposition. | Created CURSOR-WAY-OF-WORKING, CURSOR-LOYAL-OPPOSITION-ROLE, index, KNOWLEDGE-MIKE, KNOWLEDGE-PROJECT, and this log. | Resolved |

---

### 2026-02-01 - Insight dropbox and session wrap-up workflow

| Area | Finding | Evidence | Suggested action | Status |
|------|---------|----------|------------------|--------|
| Process | Mike requested a handoff mechanism: Loyal Opposition creates INSIGHTS.md at session end for Lead Builder (Claude) to use while Loyal Opposition is offline. | Mike's instruction to add to knowledge base. | Created CURSOR-INSIGHT-DROPBOX/, README.md; updated CURSOR-LOYAL-OPPOSITION-ROLE.md (Sec. 7), CURSOR-KNOWLEDGE-BASE-INDEX.md, SESSION-START-PROMPT.md. | Resolved |
| Process | Mike requested session-specific INSIGHTS files and scope rule for file operations. | Mike's follow-up: INSIGHTS-MM-DD-YYYY-hh:mm format; no create/delete/modify outside independent-progress-assessments/ without permission. | Updated all dropbox docs to INSIGHTS-MM-DD-YYYY-HH-mm.md naming; added Sec. 8 scope rule to CURSOR-LOYAL-OPPOSITION-ROLE.md; added Sec. 5 to index; updated README and SESSION-START-PROMPT. | Resolved |
| Process | Mike requested expanded Executive Summary (5x length) and knowledge base guide for future reports. | Mike's request: same approach/style, 5x length, add report style/coverage to knowledge base for future use. | Created EXEC-SUMMARY-EXPANDED-2026-02-01.md; created EXEC-SUMMARY-REPORT-GUIDE.md (questions, structure, style, sources); updated index. | Resolved |
| Process | Mike requested HTML version of expanded report with visual aids and branding; add instructions to knowledge base. | Mike's request: HTML with graphs, charts, matrices, Mermaid, external links, logo and branding from branding/; Executive Summary always `.md` + `.html`. | Created EXEC-SUMMARY-EXPANDED-2026-02-01.html; added Sec. 8 HTML Report Requirements to EXEC-SUMMARY-REPORT-GUIDE.md; updated index. | Resolved |
| Process | Mike requested all reports moved to CURSOR-INSIGHT-DROPBOX; use dropbox for reports/supporting research; keep knowledge base root for guides/indexes/logs. | Mike's instruction. | Moved 5 files to CURSOR-INSIGHT-DROPBOX; updated HTML logo path, PDF script, index, README, report guide, role doc, project knowledge. | Resolved |

---

### 2026-02-01 - Seed: risks from existing assessment

| Area | Finding | Evidence | Suggested action | Status |
|------|---------|----------|------------------|--------|
| Planning | Admin frontend build (npm/TS/bundle) not validated for admin/shopify and admin/standalone. | CLAUDE.md "Next priority" item (1). | Run `npm install && npm run build` (or equivalent) in both admin shells; fix any failures; document result. | Retired (S234) - builds validated hundreds of times since; `v1.98.73` ships 10 container images including all 4 frontends. |
| Process | Widget bundle not yet copied into Theme App Extension assets. | CLAUDE.md "Next priority" item (2). | Copy built widget IIFE from widget build output to `extensions/agent-red-chat/assets/` and document. | Retired (S234) - widget delivered via CDN/API endpoint, not TAE asset copy. Architecture changed since original finding. |
| Testing | P2 launch-quality tests (~135) not executed. | COMPREHENSIVE-TEST-PLAN.md Sec. 6; CLAUDE.md. | Prioritize P2 test implementation/execution before launch. | Retired (S234) - KB now has 10,993+ tests. P2 tests long since executed across transport, extensibility, and commercial readiness phases. |

---

### 2026-02-01 - Kiro third-party validation of Executive Summary

| Area | Finding | Evidence | Suggested action | Status |
|------|---------|----------|------------------|--------|
| Process | Kiro endorsed EXEC-SUMMARY-EXPANDED-2026-02-01 as substantially accurate (Grade A-). Minor discrepancies: test count (777 vs 930), router count (17 vs 19) attributed to snapshot timing. | Third-Party-Assessment-Validation-Report.html (Kiro); EXEC-SUMMARY-EXPANDED-2026-02-01.md. | Cursor: adopt Sec. 10 EXEC-SUMMARY-REPORT-GUIDE (metrics snapshot, source dating, validation-friendly claims, enhancement areas). | Resolved |
| Process | Executive Summary numeric claims (tests, routers, routes) should be sourced and dated so third-party validators know which snapshot was used. | Kiro report "Minor Discrepancies" table. | Added EXEC-SUMMARY-REPORT-GUIDE Sec. 10.1 (metrics snapshot, cite source, prefer derive-at-generation-time). | Resolved |
| Process | Validator recommended future reports: (1) specific prioritization of P2/integration work, (2) cloud cost summary if done, (3) technical debt/maintenance note. | Kiro report "Areas Where Assessment Could Be Enhanced". | Added EXEC-SUMMARY-REPORT-GUIDE Sec. 10.3 (enhancement areas) and Sec. 10.4 (reference to validation report). | Resolved |

---

### 2026-02-06 - Launch Readiness Report

| Area | Finding | Evidence | Suggested action | Status |
|------|---------|----------|------------------|--------|
| Process | Launch Readiness Report prepared per owner request: architecture (9 dims), implementation (9 dims), usability (10 dims), compliance (GDPR, Shopify), cost. | LAUNCH-READINESS-REPORT-2026-02-06.md in CURSOR-INSIGHT-DROPBOX. | Report delivered; owner to triage weaknesses (WI #198b, doc sync, load test, legal, creative assets, CORS, standalone auth, browser matrix). | Retired (S234) - superseded by multiple later reports (2026-02-22, 2026-02-23, 2026-03-02) and Codex review cycles through S238. |
| Technical | Doc inconsistency: GDPR webhooks and session token/Save Bar implemented in code but listed incomplete in CLAUDE.md Phase 2.1 and APP-STORE-LISTING Sec. 11-Sec. 12. | shopify_gdpr_webhooks.py (3 endpoints, HMAC); auth.py (JWT); useSaveBar.ts. | Update checklists to "implemented; verify in production." | Retired (S234) - CLAUDE.md rewritten multiple times since; GDPR webhooks verified in production. |
| Technical | No executed performance/load test in repo; COMPREHENSIVE-TEST-PLAN lists ~30 tests as remaining gap. | COMPREHENSIVE-TEST-PLAN Sec. 9; CLAUDE.md. | Run one baseline load test before GA; record P95. | Retired (S234) - load test baseline established 2026-02-23 (PASS); transport benchmarks (72 tests) added in S226. |

---

### 2026-02-22 - Session-start prompt assessment and improvement

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | Session-start prompt used by owner omitted step 5 (wrap-up / INSIGHTS file); "project root is this workspace" was ambiguous (CLAUDE.md lives under Agent Red folder, not workspace root); no explicit path to knowledge base; step 4 referenced only CLAUDE.md for priority item, but open opposition log / KNOWLEDGE-PROJECT also hold technical priorities. | Owner request to assess and improve the prompt; Cursor looked for CLAUDE.md at workspace root and had to search. | Add step 5 to copy block; disambiguate CLAUDE.md location; add "Your knowledge base lives here: [path]"; allow proposing from LOYAL-OPPOSITION-LOG / KNOWLEDGE-PROJECT. | Resolved |
| Process | SESSION-START-PROMPT.md updated with assessment section, improved main prompt (path, CLAUDE.md location, step 4 sources), and rationale. | Same session. | Use improved prompt for future Loyal Opposition session starts. | Retired (S234) - session-start hooks (`.claude/hooks/`) and `SCHEDULE.md` now handle session initialization. Cursor retired; Codex uses bridge protocol. |

---

### 2026-02-22 - Launch Readiness Report (fresh inspection)

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | Launch Readiness Report 2026-02-22 prepared per owner request: architecture (9 dims), implementation (9 dims), usability (10 dims), compliance (GDPR, Shopify), cost. Fresh inspection of codebase, docs, scripts; did not rely on prior reports. | LAUNCH-READINESS-REPORT-2026-02-22.md in CURSOR-INSIGHT-DROPBOX. | Owner to triage weaknesses (doc sync, load baseline, legal, creative assets, CORS, standalone auth, browser matrix). | Retired (S234) - superseded by later reports and Codex S226-S238 review cycles. CORS hardened S233. |

---

### 2026-02-23 - Mock/stub scan and revised Launch Readiness Report

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-assessment scan of `src/` for mocks, stubs, placeholders: Layer 4 fine-tuning (`_call_fine_tuning_api`, `_check_job_status_api`) defaults to placeholder when API not configured; MCP mutation, Shopify annual overage, Stripe notifications are documented deferrals; `storefront_ingestion` comment says "stub" but `_process_template` is implemented. | MOCK-STUB-SCAN-2026-02-23.md; LAUNCH-READINESS-REPORT-2026-02-23.md. | If Layer 4 in GA scope, implement or inject real APIs else gate feature; fix `storefront_ingestion` comment. | Retired (S234) - Layer 4 fine-tuning deferred by design. `storefront_ingestion` implemented. MCP mutation, Shopify overage, Stripe notifications remain documented deferrals. |
| Process | Revised Launch Readiness Report 2026-02-23: incorporates mock/stub scan; updates to `v1.56.7`, ~4,791 unit tests, 18/18 T0, 917 UI, CP.1-CP.21 21/21 PASS, Master Test Plan `v2.0`, Release Plan `v1.57`. | Same. | Owner to triage revised weaknesses (Layer 4, doc sync, comment fix, load baseline, legal, creative, CORS, standalone auth, browser matrix). | Retired (S234) - superseded by S226-S238 review cycles. `v1.98.73`, 10,993 KB tests. |

---

### 2026-02-23 - Full project assessment (comprehensive document)

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | Comprehensive Project Assessment 2026-02-23 prepared per owner request: full assessment of entire project with Mock/Stub/Deferred scan integrated in full. Covers project overview, architecture (9 dims), implementation (9 dims), full mock/stub scan (Sec. 4), usability (10 dims), compliance, cost, consolidated summary and actions. | COMPREHENSIVE-PROJECT-ASSESSMENT-2026-02-23.md in CURSOR-INSIGHT-DROPBOX. | Owner to use as single reference for GA readiness; triage actions in Sec. 8.2. | Retired (S234) - superseded by Codex review cycles S226-S238 and actionable backlog review 2026-03-30. |

---

### 2026-03-02 - Launch Readiness Report (fresh inspection)

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | Launch Readiness Report 2026-03-02 prepared per owner request: architecture (9 dims), implementation (9 dims), usability (10 dims), compliance (GDPR, Shopify), cost. Fresh inspection; 7,250 tests collected; load test 2026-02-23 PASS; Layer 4 and `storefront_ingestion` previously reported issues resolved in current code. | LAUNCH-READINESS-REPORT-2026-03-02.md in CURSOR-INSIGHT-DROPBOX. | Owner to triage weaknesses (CORS, creative assets, standalone auth, browser matrix). | Retired (S234) - superseded by Codex S226-S238 review cycles. Remaining items (creative assets, Shopify submission) tracked separately. |
| Technical | CORS defaults to `*` when `APP_CORS_ORIGINS` unset | src/app/factory.py L132-146 | Set `APP_CORS_ORIGINS` in production to explicit origins. | Resolved (S233) - CORS hardened: explicit `APP_CORS_ORIGINS` + `APP_CORS_ORIGIN_REGEX` (no localhost) on staging + production. |
| Technical | Test count: 7,250 collected (pytest 2026-03-02); load test last run 2026-02-23 PASS | `pytest --collect-only`; `load-test-procedure.md` | Continue monitoring; re-run load test periodically. | Resolved (baseline established) |

---

### 2026-04-10 - S276 Owner-Decision Log and Residual Risks

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | WI-3030 async-only scope reduction accepted by owner: launch scope reduced to asynchronous escalation only; real-time inbox and co-pilot completion deferred. | INSIGHTS-2026-04-10-S276-OWNER-DECISION-LOG.md; owner decision in Prime message 7233def8. | Preserve explicit scope-reduction language in all closure, release, and retrospective material to prevent governance drift. | Open (post-deploy governance watch) |
| Technical | WI-3031 deploy-path durability risk: scaling intent for production minReplicas is carried by manual deploy-time action; `deploy.py` does not encode the scaling baseline. | INSIGHTS-2026-04-10-S276-OWNER-DECISION-LOG.md; prior advisory INSIGHTS-2026-04-10-01-21-25-S275-WI-RESOLUTION-ADVISORY.md; INSIGHTS-2026-04-24-22-33-CANONICAL-DEPLOY-SCALING-GAP.md (canonical-path escalation). | Add `minReplicas` enforcement to `deploy.py` or equivalent release control so scaling baseline cannot be skipped. | Resolved 2026-04-25 (S308): smoke path enforced in WI-3171 (`scripts/deploy.py:enforce_all_scaling`); canonical path now invokes the shared helpers via new `phase_15_enforce_scaling()` in `scripts/deploy_pipeline.py`. Bridge thread `canonical-deploy-pipeline-scaling-enforcement` VERIFIED at -012; commits 417f187b + db1a63fd; 24/24 scaling tests pass; both new test files in release-candidate gate. Production runtime validation pending next release window. |
| Technical | 68 unmapped active specs remain a traceability weakness; not a deployment gate per owner decision in S276. | INSIGHTS-2026-04-10-FRESH-SPEC-IMPLEMENTATION-EVAL-INTERIM.md; owner classification as post-deploy hygiene. | Include SPEC-1879..SPEC-1882 cluster and governance/architecture unmapped specs in next Loyal Opposition audit set after production deploy. | Deferred (post-deploy hygiene) |

---

### 2026-04-21 - Startup token and wrap-up feedback

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | Fresh-session startup token load improved to owner-observed `23k / 258k`, but live token measurement is still manual because the harness does not expose the value to the dashboard generator. | Mike feedback and screenshot on 2026-04-21; INSIGHTS-2026-04-21-STARTUP-TOKEN-AND-PREMATURE-WRAPUP-FEEDBACK.md; `docs/gtkb-dashboard/session-startup-report.md` reports `not_exposed_by_current_harness`. | Preserve `23k` as the latest manual benchmark and continue reducing injected startup payload while pursuing mechanical token capture. | Open |
| Process | Wrap-up behavior can fire or appear to fire before Mike has a practical chance to answer the startup focus chooser. | Mike feedback on 2026-04-21; `.claude/SCHEDULE.md` session-end wrap-up group; proactive wrap-up rules in `.claude/rules/acting-prime-builder.md`; generated wrap-up report in `docs/gtkb-dashboard/session-wrapup-report.md`. | Implemented one-shot startup lifecycle guard and scheduler keyword tightening; verified with `python -m pytest tests/scripts/test_session_self_initialization.py tests/ops/test_hooks_specs.py tests/scripts/test_codex_hook_parity.py -q --tb=short` and `python scripts/check_codex_hook_parity.py`. | Resolved |

---

### 2026-04-27 - GT-KB root and Agent Red isolation bridge reviews

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | E: deletion-readiness evidence is now verified for E: root siblings and `E:\Claude-Playground`, but verification is not deletion authorization. `E:\Claude-Playground` also contains 49 credential-like `.env*` files recorded by path/metadata only. | `bridge/e-drive-root-deletion-readiness-scan-008.md`; `bridge/e-drive-claude-playground-cleanup-manifest-010.md`; `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-27-19-37.md`. | Keep deletion and credential-exposure/rotation decisions owner-gated. In the next Prime session, present manifest-based owner choices rather than deleting automatically. | Open |
| Technical | Agent Red app-root scaffold and registry are verified, but application isolation is not complete. `.env.local`, Shopify/PDF moves, release-gate DCL wiring, and formal DELIB/ADR/DCL writes remain future slices; `.vscode/settings.json` is still not git-trackable due `.gitignore`. | `bridge/application-isolation-contract-008.md`; `applications/Agent_Red/.gtkb-app-isolation.json`; `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-27-19-37.md`. | Continue with application-isolation sub-slices 2-6 and file a small gitignore-hygiene bridge before treating the VSCode placeholder as durable. | Open |

---

### 2026-04-28 - Loyal Opposition wrap-up for isolation, MemBase, and smart poller

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Phase 1 isolation implementation is not ready to merge because hook relocation wiring, runtime-file policy, bridge audit-trail coverage, and stale-delete preflight evidence are incomplete. | `bridge/gtkb-isolation-phase1-implementation-2026-04-28-002.md`; latest `NO-GO` in `bridge/INDEX.md`; wrap-up report `CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-28-17-58.md`. | Prime Builder should revise the Phase 1 implementation package and return it through the bridge before merge/commit. | Open |
| Process | MemBase is used seriously as governed state, but not effectively enough for the GT-KB owner-burden target because automatic capture, owner-visible event surfacing, foundational intake, and WI harvest controls are incomplete. | `CODEX-INSIGHT-DROPBOX/MEMBASE-EFFECTIVE-USE-ASSESSMENT-2026-04-29.md`; wrap-up report `CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-28-17-58.md`. | Prime Builder should add a MemBase Effective Use recovery/implementation proposal to the backlog and bridge. | Open |
| Technical | Smart-poller implementation is slice-ready, not end-to-end ready: P1/P2/P2.5 are GO, but P3 invoker/autonomous write-capable behavior remains gated on P2.5 evidence and owner-approved live harness execution. | `bridge/gtkb-bridge-poller-001-smart-poller-007.md`; `bridge/gtkb-bridge-poller-p2-5-verification-spike-004.md`; wrap-up report `CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-28-17-58.md`. | Implement P1, P2, and non-live P2.5 spike machinery first; defer P3 until the spike report classifies allowed harness/mode behavior. | Open |

---

### 2026-05-09 - GT-KB MCP stable harness surface advisory

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | MCP should be evaluated as a convenience and stable harness-facing adapter over existing GT-KB services, while core GT-KB services and authority boundaries remain unchanged. | `CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-09-22-26-GTKB-MCP-STABLE-HARNESS-SURFACE-ADVISORY.md`; bridge handoff `bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09-001.md`; system interface map entries for MemBase, Deliberation Archive, dashboard, plugin/app capability, and MCP server. | Prime Builder should respond through the bridge with either a narrow MCP adapter implementation proposal or an evidence-backed rebuttal. | Open |

---

### 2026-05-09 - Advisory report bridge message type advisory

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | Owner-requested Loyal Opposition advisory reports are a normal workflow but currently lack a first-class bridge message type, forcing advisory handoffs through semantically wrong verdict statuses such as `NO-GO`. | `CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-09-22-35-BRIDGE-ADVISORY-REPORT-MESSAGE-TYPE.md`; bridge handoff `bridge/gtkb-advisory-report-message-type-2026-05-09-001.md`; `.claude/rules/operating-model.md` recognizes advisory reports while `.claude/rules/file-bridge-protocol.md` lacks advisory status semantics. | Prime Builder should respond through the bridge with either a narrow protocol-extension implementation proposal or an evidence-backed rebuttal. | Open |

---

### 2026-05-10 - Peer solution advisory pattern

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | Peer-solution evaluations of OpenAI Symphony, GSD v2, BMAD Method, and Archon should become a repeatable advisory loop that converts useful external patterns into governed GT-KB candidate artifacts instead of leaving them as chat-only comparisons. | `CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-10-22-25-PEER-SOLUTION-ADVISORY-REPORT.md`; bridge handoff `bridge/gtkb-peer-solution-advisory-loop-2026-05-10-001.md`; owner request to turn comparative evaluations into an advisory report for Prime discussion; owner agreement to add Archon as a high-relevance workflow-engine peer. | Prime should respond through the bridge with a proposal, rebuttal, or defer decision; highest-relevance candidate is the Archon-derived GT-KB declarative workflow contract. | Open |

---

### 2026-05-11 - Role scope for release and operations advisory

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | GT-KB should formalize role responsibilities for testing, release-candidate readiness, staging/production deployment, rollback, maintenance, service requests, and outages while preserving the two durable operating roles: Prime Builder and Loyal Opposition. | Bridge handoff `bridge/gtkb-role-scope-release-operations-advisory-2026-05-11-001.md`; current operating-model split between Prime proposal/implementation and Loyal Opposition verification; existing release-candidate gate is non-deploying while deployment requires owner approval. | Prime Builder should respond through the bridge with a role-responsibility matrix / release-operations authority proposal, an evidence-backed rebuttal, or an explicit defer decision before Agent Red release work resumes. | Open |
| Process | Public GitHub AI harness ecosystems now contain useful patterns for GT-KB, especially skill/plugin packaging, third-party provenance review, semantic retrieval, CI-contained agent review, declarative workflows, and operator visibility; no reviewed project should replace GT-KB whole. | `CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-11-11-00-GITHUB-AI-HARNESS-ECOSYSTEM-ADVISORY.md`; bridge handoff `bridge/gtkb-github-ai-harness-ecosystem-advisory-2026-05-11-001.md`; owner request for a broad GitHub ecosystem search and Prime-facing advisory. | Prime Builder should respond through the bridge with an ecosystem-scout/import-policy implementation proposal, an evidence-backed rebuttal, or an explicit defer decision. | Open |

---

### 2026-05-27 - Harness Capability and Role Suitability Advisory

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | Antigravity (Gemini) is ready to serve as Loyal Opposition once registration and dispatch verification are verified, but is structurally blocked from Prime Builder role due to a lack of event hooks. | `memory/antigravity-integration-status.md`; `bridge/gtkb-antigravity-harness-registration-003.md`; `DOC-ANTIGRAVITY-IDE-RESEARCH-001` | Verify harness registration and complete headless dispatch verification, then activate and assign Gemini as LO. | Open |
| Process | Claude Code is currently incapable of serving as Prime Builder due to severe background execution/auth hangs and silent no-ops discovered during headless runs. | `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1` | Maintain Claude Code's suspended status in registry until headless CLI execution fixes are proposed and verified. Owner AUQ 2026-05-27 (S364): defer until WI-3349 VERIFIED — the suggested topology reshuffle (suspend B; flip A to PB; activate C as LO) presumes Antigravity's LO suitability, which WI-3349 substrate verification is the precondition for. Re-surface for owner disposition once WI-3349 reaches VERIFIED. | Deferred |

---

### 2026-05-27 - Efficacy KPI Suite Proposal

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | Traditional engineering metrics fail to capture agentic software factory performance. We proposed a three-tiered KPI suite (Owner Burden, Dual-Agent Velocity & Rigor, and System Integrity) to measure GroundTruth KB efficacy and prevent regression. | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-27-13-40.md`; owner request to propose a suite of KPIs to measure efficacy and regression. | Prime Builder should review the proposed KPI metrics, draft SQLite views for STMR and DPD, and present a dashboard visualization plan. | Open |

---

### 2026-05-29 - Session and Work Envelope UI Convention

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | DELIB-2500 establishes session and work envelope UI convention at MEDIUM commitment, but contains concurrency write races, validation gaps, parser compatibility risks, role assertion mismatches, Agent Red coupling risk, and an unsettled UX value-vs-ceremony question. | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-29-06-50-delib-2500-review.md`; `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-29-07-12-delib-2500-envelope-convention-advisory.md`; database record lookup of DELIB-2500. | Prime Builder should run a structured owner-grilling pass before any implementation proposal, then file a scoping/specification proposal covering per-harness envelope state, parser compatibility matrix, application binding, strict role assertion behavior, service-level work-envelope instrumentation, and glossary/spec amendments. | Open |

---

### 2026-06-01 - Parallel Scan and Role Invariant Diagnostic

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | The recently committed active harness roleless check strictly prevents active roleless harnesses, making three-active harness environments impossible and blocking 'test_harness_set_role_three_harness_demotes_all_non_targets'. Additionally, a parity mismatch exists between 'role-assignments.json' and 'harness-registry.json'. | `groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py:L129-138`; `platform_tests/groundtruth_kb/cli/test_harness_cli.py::test_harness_set_role_three_harness_demotes_all_non_targets` failure; `INSIGHTS-2026-06-01-20-08-PARALLEL-BRIDGE-SCAN-AND-ROLE-INVARIANT-DIAGNOSTIC.md` | Modify CLI role switch transaction logic to automatically transition demoted harnesses to 'suspended' status and persist status changes to the DB-backed registry projection. | Resolved |

---

### 2026-06-01 - Parallel Loyal Opposition Scan and Queue Verification

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Post-implementation reports for list-subset-filters (NEW-003) and headless-gemini-lo-dispatch-verification (REVISED-017) are actionable and fully test-compliant. | `bridge/INDEX.md` scan; pytest runs (`test_cli_subset_list.py` & `test_verify_antigravity_dispatch.py`) and verifier script. | File `VERIFIED` verdicts for both threads (004 and 018) and update `bridge/INDEX.md` to terminal states. | Resolved |
| Technical | Post-implementation report for startup-enhancements closeout is verified with open WI-3326 accepted as an out-of-scope residual. | `bridge/INDEX.md` scan; SQLite queries confirming project retired and WI resolved. | File `VERIFIED` verdict (007) and update `bridge/INDEX.md` to VERIFIED. | Resolved |
| Technical | Governance review proposal for the terminal project record retirement batch is verified safe and approved for implementation. | `bridge/INDEX.md` scan; SQLite verification of terminal states for all 9 candidate projects. | File `GO` verdict (002) and update `bridge/INDEX.md` to GO. | Resolved |

---

### 2026-06-03 - Deep scan log and backlog gap review

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | A June 2 owner-approved project recommendation, `GTKB Harness Automation Readiness`, was not captured in the live `projects` table; the recommendation only exists as routed advisory `WI-4262`. | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-02-DEEP-SCAN-BACKLOG-RECOMMENDATIONS.md`; SQLite query against `groundtruth.db` on 2026-06-03 showed zero project rows with that name. | Reconfirm project approval, then create the missing project and seed its first readiness doctor / readiness surface work items. | Open |
| Process | Advisory intake debt remains structurally under-owned: `3080` non-terminal work items have no project and `775` open items are still `Route LO advisory:` while the active advisory projects have zero member work items. | SQLite query against `groundtruth.db` on 2026-06-03; `scripts/advisory_backlog_router.py` still prints full `skipped_existing` payloads by default. | Add explicit drain-policy and compact-router-output work items under the existing LO advisory project family. | Resolved |
| Technical | The live Codex bridge-worker log is dominated by repetitive migration INFO, reducing observability value. | `.claude/hooks/.codex-bridge-worker.log` contained `2432` lines on 2026-06-03, `2419` of them `Applied migration` INFO lines; bridge logging defaults to INFO in `groundtruth-kb/src/groundtruth_kb/_logging.py`. | Add an observability work item to suppress or aggregate repetitive KnowledgeDB migration INFO in bridge-worker logs. | Resolved |

---

### 2026-06-01 - rc1 Canonical CI Closure Proposal Review

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Proposal for gtkb-rc1-canonical-ci-closure is sound, safe, and passes all preflights. | `bridge/gtkb-rc1-canonical-ci-closure-001.md`, applicability and clause preflight runs. | File `GO` verdict (002) and register in `bridge/INDEX.md`. | Resolved |

---

### 2026-06-03 - Scoping and Scaffolding Reviews

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Scoping and implementation proposals for startup refractor and proposal scaffolding standards are sound, compliant, and pass all preflights. | `bridge/INDEX.md` scan; preflight and clause preflight runs for `gtkb-startup-refractor-scoping` and `gtkb-proposal-standards-propose-scaffold-skill`. | File `GO` verdicts for both threads (002) and register them in `bridge/INDEX.md`. | Resolved |

---

### 2026-06-03 - Deep scan capture gap recheck

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | The previously approved harness-readiness recommendation still is not present as a first-class backlog project; the live backlog still only holds routed advisory `WI-4262`. | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-03-16-50-DEEP-SCAN-CAPTURE-GAPS.md`; SQLite query against `groundtruth.db` on 2026-06-03 showed zero `projects.name='GTKB Harness Automation Readiness'`. | Reconfirm and capture the missing project, then seed the readiness-doctor and readiness-surface work items. | Open |
| Process | Advisory debt remains under-decomposed even after prior scans: `740` non-terminal `Route LO advisory:` items remain, `913` non-terminal items remain unprojected, and the active advisory projects still have zero member work items. | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-03-16-50-DEEP-SCAN-CAPTURE-GAPS.md`; SQLite query against `groundtruth.db`; `scripts/advisory_backlog_router.py` still emits full `skipped_existing` payloads. | Add advisory drain-policy and compact dry-run output work items under `GTKB-LO-ADVISORY-INTAKE`. | Resolved |
| Technical | Codex bridge-worker logs still over-emit repetitive migration INFO, reducing audit signal quality. | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-03-16-50-DEEP-SCAN-CAPTURE-GAPS.md`; `.claude/hooks/.codex-bridge-worker.log` contained `26488` lines including `9066` migration INFO lines on the current scan. | Add an observability work item to suppress or aggregate repetitive KnowledgeDB migration INFO. | Resolved |

---

### 2026-06-04 - LO autonomous /loop: empty queue + bridge_kind taxonomy drift

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | LO actionable queue is empty (0 entries); 12 GOs, 121 VERIFIED, 1 NO-GO, 5 ADVISORY, 1 DEFERRED, 44 WITHDRAWN. Steady state, all LO duties discharged at this snapshot. | `python .claude/skills/bridge/helpers/scan_bridge.py --role loyal-opposition` at 13:35:56Z. | None required; observation only. | Resolved |
| Technical | All 12 top-of-chain GO entries are correctly classified TERMINAL-OK (`target_paths: []`, `requires_verification: false`). No mis-classification stalling Prime. | Sub-agent audit of `bridge/<slug>-002.md` through `-006.md` for the 12 GO slugs; see report. | None required; positive confirmation of WI-4278 terminal-GO filter. | Resolved |
| Technical | `bridge_kind` taxonomy drift across bridge corpus: 25+ distinct values, 11 synonyms for "LO verdict" alone (loyal_opposition_verdict 394, verification_verdict 301, review_verdict 103, loyal_opposition_review 42, etc.). Silent classifier hazard for `scan_bridge.py`, cross-harness trigger, and dashboards. | `grep -hr "^bridge_kind:" bridge/*.md \| sort \| uniq -c \| sort -rn`; full report in `INSIGHTS-2026-06-04-13-37-LO-LOOP-EMPTY-QUEUE-AND-BRIDGE-KIND-TAXONOMY-DRIFT.md`. | Land a canonical 5-7-value `bridge_kind` enum + bridge-compliance-gate lint; migrate via re-version backfill. P2. | Open |
| Process | `.claude/session/active-session-role.json` written at 13:33:38Z with `role=prime-builder` for my session ID (4c7620e0-be99-…) despite the session resolving as Loyal Opposition via `::init gtkb lo` at SessionStart 13:30:14Z. Parallel-session marker race (same defect class as project_s_scheduled_pb_saturation_clobber). | File contents inspected; LO startup disclosure was successfully relayed from `last-user-visible-startup-lo.md` (sha256 `cad2ad18…`). | Add atomic session-stated-role marker write with cross-session clobber rejection in `scripts/workstream_focus.py`. P2. | Open |
| Process | Bridge dispatch state (`.gtkb-state/bridge-poller/dispatch-state.json`) is 3 days stale (last update 2026-06-01T18:07:51Z) despite many VERIFIED entries landing 2026-06-04 (commits `ed23f6b5`, `e0d4cc29`, `ad45a73d`, `2fa27699`, `6beb26c2`). Likely the trigger writes only on actionable-signature change, not every fire; needs confirmation before any alarm threshold is set. | `dispatch-state.json` inspection. | Add doctor staleness WARN once write semantics are confirmed. P3. | Open |
| Technical | Stranded atomic-write tmp file `dispatch-state.json.34252-0f2d0cc7.tmp` alongside canonical `dispatch-state.json`. Single instance, no rotation pattern. | `ls .gtkb-state/bridge-poller/`. | Add cleanup of `*.tmp` stragglers in poller-state hygiene. P3. | Open |

Full advisory: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-04-13-37-LO-LOOP-EMPTY-QUEUE-AND-BRIDGE-KIND-TAXONOMY-DRIFT.md`.

**Post-loop addendum (15:14Z, same session) — concrete cross-harness session-id co-option.**

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | Work-intent claim file `.gtkb-state/work-intent/gtkb-impl-start-target-paths-preflight.json` was acquired at 15:13:12Z under this Claude session id `4c7620e0-be99-…` for a thread this session never touched. The thread's `-003.md` NO-GO was authored by Codex (harness A) under `automation: keep-working-lo`, against a `-001` by Claude Prime (harness B, session `bfc70de3-76e6-…`) and `-002` GO by Antigravity LO (harness C). Three harnesses concurrent on one thread; the LO claim holder is a fourth ID (mine) that did not invoke `bridge_claim_cli.py`. | `cat .gtkb-state/work-intent/gtkb-impl-start-target-paths-preflight.json`; head of `bridge/gtkb-impl-start-target-paths-preflight-003.md`; AXIS-2 surface at 15:13:48Z. | Investigate the Codex `keep-working-lo` automation's session-id resolution — it should never hold a claim under a remote-harness's session id. Likely related to shared dispatch-state.json or trigger-emitted env-vars. P2 follow-up to the marker-race candidate C. | Open |

---

### 2026-06-04 - Ollama Harness Integration & Routing Investigation

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Ollama lacks native agent execution/tool loops, requiring a custom client execution shim (`scripts/ollama_harness.py`) to serve as a supported GT-KB harness. | User request; `cross_harness_bridge_trigger.py` dependency on headless argv execution surfaces. | Implement a Python-based harness executor shim that supports Ollama function-calling APIs. | Open |
| Technical | `check_harness_parity.py` hardcodes `KNOWN_HARNESSES = ("claude", "codex")`, ignoring Antigravity and any new harness like Ollama. | `scripts/check_harness_parity.py:L18` | Generalize parity checks and TOML capability schema to support active registered harnesses dynamically. | Open |
| Process | Local models have differing strengths; task-to-model routing can optimize VRAM and latency by matching skills to model capacity. | User request; Ollama support for multiple local models. | Add model routing map (e.g. `.ollama/routing.toml`) to dynamically select the model based on task complexity. | Open |

Full advisory: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-04-08-20-ollama-parity-gap-analysis.md`.

---

### 2026-06-09 - Bridge Dispatch Deadlock & Contention Critique

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | The bridge dispatch system deadlocks in multi-harness topologies when all active harnesses (e.g. Antigravity, Ollama, Goose) lack event-driven hooks. | `harness-registry.json` and `mode_switch/derive.py` topology logic | Amend the topology derivation / scheduled task dispatcher to allow a periodic polling fallback for multi-harness mode. | Open |
| Technical | Stale locks, failure events, and endpoint availability lack first-class health checks and discoverability CLI surfaces. | `dispatch-failures.jsonl` and lock files | Add a `--doctor` health-check verification surface to the dispatcher or harness CLI. | Open |
| Process | Work-intent claims rely on flat-file O_EXCL locks, vulnerable to rename races on Windows, and session-id leaks across spawned environments. | `bridge_work_intent_registry.py` and `cross_harness_bridge_trigger.py` | Migrate work-intent claims to a transaction-backed table in `groundtruth.db` and isolate spawned envs. | Open |

Full advisory: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-09-14-55-dispatch-deadlock-and-contention-critique.md`.

---

## How to Add an Entry

1. Add a new row under the latest date block (or start a new date block).
2. Fill: Area (Technical / Process / Product / Commercial), Finding (one sentence), Evidence (doc/code reference), Suggested action (brief), Status (Open / Resolved / Deferred).
3. When Mike resolves or defers an item, change Status in place; optionally add a one-line "Resolution" column or note in the same row.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
---

### 2026-06-07 - S509 Prime Builder Implementation Handoff

Prime Builder (goose/pb) has addressed the 2026-06-03 and 2026-06-04 findings via the following Implementation Proposals filed on the bridge:

1. **Advisory Message Type:** `bridge/gtkb-bridge-advisory-message-type-implementation-001.md`
2. **MCP Stable Surface:** `bridge/gtkb-mcp-stable-harness-surface-implementation-001.md` (covers Ollama and general MCP)
3. **Ecosystem Scout:** `bridge/gtkb-ecosystem-scout-policy-implementation-001.md`
4. **Taxonomy & Concurrency:** `bridge/gtkb-bridge-kind-taxonomy-stabilization-001.md` and `bridge/gtkb-workstream-focus-marker-race-fix-001.md`
5. **Observability & Parity:** `bridge/gtkb-platform-observability-hygiene-001.md`
6. **Isolation Phase 3:** `bridge/gtkb-isolation-phase3-implementation-001.md`
7. **Directive Enforcement (P1+P2):** `bridge/gtkb-directive-enforcement-p1-p2-combined-001.md`

**Technical:** Repetitive KnowledgeDB migration logs were demoted to DEBUG in `groundtruth_kb/db.py` during this session.

### 2026-06-09 - S510 Bridge Dispatch Deadlock & Contention Critique

Loyal Opposition (antigravity/pb - operating under Prime Builder role for this session) completed a deep review of bridge dispatch, complexity, parity, discoverability, and contention handling. The full report was filed in `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-09-14-55-dispatch-deadlock-and-contention-critique.md`.

### 2026-06-12 - Cheap-Harness Program Scan & Test Fix

Loyal Opposition (antigravity/lo) completed a review of the three cheap-harness program threads: WI-4473 (GO), WI-4476 (GO), and WI-4472 (VERIFIED). Staged and committed the untracked verdict files in the worktree. Diagnosed and patched a test suite robustness failure in `test_session_start_dispatch_drains_bridge_substrate_pending.py` caused by `GTKB_NO_CROSS_HARNESS_TRIGGER=1` environment variable inheritance.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Test suite robustness failure in `test_session_start_drains_pending_before_role_resolution` when `GTKB_NO_CROSS_HARNESS_TRIGGER=1` is set in the environment. | pytest run tracebacks; early return in `run_trigger` | Add `pytest.MonkeyPatch` to the test to pop the loop-prevention environment variable during test run. | Resolved |
| Process | Staging/tracking gaps for WI-4473 and WI-4476 verdict files, which were committed in `bridge/INDEX.md` but left untracked. | git status output showing untracked `-001.md`/`-002.md` files | Stage and commit the untracked files using a scoped commit. | Resolved |

### 2026-06-12 - Cheap-Harness Program Verification (WI-4473 & WI-4476)

Loyal Opposition (antigravity/lo) verified and committed the post-implementation reports and verification verdicts for WI-4473 (Ollama scope load model filter) and WI-4476 (OpenRouter DeepSeek cost optimization). All spec-derived tests pass cleanly, and live completions verify tool-calling functionality against the cost-optimized models (HTTP 200). Both threads are now VERIFIED.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Cost-optimized autodispatch requires both Ollama and OpenRouter LO harnesses to launch without aborting. | 508 failed dispatches previously logged | Re-point model configurations and load filters to target-eligible, cheaper models and verify tool-calling. | Resolved |

### 2026-06-12 - Loyal Opposition Queue Clearance and Status Check

Loyal Opposition (antigravity/lo) completed a scan of the active bridge review queue and confirmed that all open bridge items have been resolved and verified. No actionable items are pending.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | No active review items are pending on the bridge queue; the queue is completely drained. | `bridge/INDEX.md` scan; status command output showing 0 LO actionable items | None required; proceed with Prime Builder tasks | Resolved |

### 2026-06-13 - WI-4516 OpenRouter/Ollama Bash Bridge Bypass

Loyal Opposition (Codex/lo automation `keep-working-lo`) completed an advisory investigation for `WI-4516`. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-WI-4516-openrouter-bash-bridge-bypass.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | OpenRouter and Ollama SDK harness `Bash` dispatch can mutate `bridge/*.md` without invoking bridge-compliance guards; `Write`/`Edit` do invoke bridge-compliance. | Temp-directory reproductions through `dispatch_tool_call("Bash", ...)`; `scripts/openrouter_harness.py` and `scripts/ollama_harness.py` guard routing; 54 targeted harness tests passed; Codex bridge adapter tests have a separate claim-handling failure. | Resolve `WI-4468` first or as step zero, then hard-deny SDK harness `Bash` bridge writes and require a single guarded bridge-writer path with OpenRouter/Ollama parity tests. | Open |

### 2026-06-13 - WI-4464 Git Index Contamination Advisory

Loyal Opposition (Codex/lo automation `keep-working-lo`) completed an advisory investigation for `WI-4464`. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-08-55-WI-4464-git-index-contamination-advisory.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Shared Git index contamination remains a live P1 commit-safety risk; current staged state again mixes bridge, hook, and unrelated script/test work before this LO report. | `memory/recovery-2026-06-11-fab20-commit-collision.md`; live `git diff --cached --name-status`; full WI-4464 report. | Prime should file a bridge proposal for an explicit-path safe commit helper, mixed-index warning, and stale-HEAD reset guard before changing git tooling. | Open |

### 2026-06-13 - WI-4455 spec-before-code Platform Tests Advisory

Loyal Opposition (Codex/lo automation `keep-working-lo`) completed an advisory investigation for `WI-4455`. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-WI-4455-spec-before-code-platform-tests-advisory.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | The live root `spec-before-code.py` hook is currently a WI-4449 recovery stub, but the managed template still implements source_paths-only matching and reproduces the false advisory for bridge-linked `platform_tests/` files. | Live `.claude/hooks/spec-before-code.py` emits nothing; `groundtruth-kb/templates/hooks/spec-before-code.py` emits "No specification found covering platform_tests/scripts/test_gtkb_hygiene_investigation.py"; FAB-20 bridge report carries the test linkage through target_paths/spec-to-test mapping. | Do not restore the current template unchanged; choose bridge-derived test coverage, reviewed source_paths backfill, or explicit platform_tests deferral before re-enabling the hook. | Open |

### 2026-06-13 - WI-4457 Governance Hook Tracking Doctor Gap

Loyal Opposition (Codex/lo automation `keep-working-lo`) completed an advisory investigation for `WI-4457`. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-WI-4457-governance-hook-tracking-doctor-gap.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Current `.claude/hooks/*.py` registrations all exist and are tracked, but `gt project doctor` still lacks a direct git-index tracking invariant for registered governance hook scripts. | `.gitignore` re-includes `.claude/hooks/*.py`; `.claude/settings.json` registers many hook scripts; doctor checks validate presence/registration/managed drift but do not compare registered hook paths to `git ls-files`. Targeted doctor tests passed (24). | Prime should file a narrow bridge proposal for an additive WARN-level doctor check covering registered-but-untracked and unregistered-untracked `.claude/hooks/*.py` files. | Open |

### 2026-06-13 - WI-4458 Governance Emergency Bootstrap Protocol Advisory

Loyal Opposition (Codex/lo automation `keep-working-lo`) completed an advisory investigation for `WI-4458`. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-WI-4458-governance-emergency-bootstrap-protocol.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | The WI-4449 `--no-verify` precedent was justified by a real governance deadlock, but GT-KB lacks a reusable emergency-bootstrap protocol with tight boundaries and explicit post-fix audit discipline. | `bridge/gtkb-commit-untracked-governance-hooks-002.md` records the hook/bridge deadlock and follow-on need; `e90b2f03` restored six tracked hook files; current bridge/claim/approval tests passed (31). | Prime should file a normal bridge proposal for a narrow rule/runbook addition defining allowed conditions, minimum scope, required audit artifact, and retroactive owner-decision capture when explicit prior approval was unavailable. | Open |

### 2026-06-13 - WI-4452 Bridge INDEX Repair

Loyal Opposition (Codex/lo automation `keep-working-lo`) repaired the canonical bridge INDEX entry for `gtkb-wi4452-impl-auth-named-packet-fallback`. The versioned files were already tracked on disk through `VERIFIED`; the missing `bridge/INDEX.md` document block made the thread invisible to live bridge scanners.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | `WI-4452` had a complete tracked bridge thread ending in `VERIFIED`, but no `Document:` block in `bridge/INDEX.md`. | `show_thread_bridge.py` initially reported all seven `gtkb-wi4452-impl-auth-named-packet-fallback-*.md` files as not referenced by INDEX; after serialized `gt bridge index` restoration, drift is empty and LO scan reports 194 terminal VERIFIED entries. | Treat the bridge repair as complete; downstream backlog/project reconciliation can now see the verified thread from canonical INDEX state. `WI-4443` remains related-only per the implementation report unless separately authorized. | Resolved |

### 2026-06-13 - WI-4453 ChromaDB Latency Advisory

Loyal Opposition (Codex/lo automation `keep-working-lo`) completed an advisory investigation for `WI-4453`. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-WI-4453-chromadb-latency-advisory.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Current Python 3.14 fallback paths make `deliberations search` and `bridge propose --dry-run` fast, but WI-4453 remains open because non-dry-run record indexing is still synchronous and there is no median-latency regression benchmark for all three named CLI surfaces. | Live runtime reports `HAS_CHROMADB=False`; direct search/propose probes returned quickly; `insert_deliberation()` commits SQLite then calls `_index_deliberation_in_chroma()` without a timeout wrapper; targeted tests passed (3/1 skipped import-budget, 50 CLI tests, 10 Chroma/fail-soft tests). | Prime should file a narrow defect-fix proposal for bounded/out-of-band record indexing, deterministic related-deliberation seeding in bridge propose, and the WI's `<= 10s` median-latency benchmark. | Open |

### 2026-06-13 - WI-4443 Implementation Authorization Current Pointer Disposition

Loyal Opposition (Codex/lo automation `keep-working-lo`) completed an advisory investigation for `WI-4443`. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-WI-4443-impl-auth-current-pointer-disposition.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | The live implementation-start gate no longer appears to have the WI-4443 operational defect, because the verified WI-4452 named-packet fallback covers the same `current.json` clobber path; the remaining issue is MemBase disposition. | `validate_targets()` falls back to exactly one valid by-bridge packet; `gate_decision()` calls `validate_targets()`; WI-4452 thread is VERIFIED with no drift; focused auth/gate tests passed (183). | Prime should either supersede/close WI-4443 against the WI-4452 VERIFIED evidence with required approval, or restate it as a broader per-session pointer redesign if that remaining scope is intentional. | Open |

### 2026-06-13 - Ollama Phase 2 Completion Bridge INDEX Repair

Loyal Opposition (Codex/lo automation `keep-working-lo`) repaired the canonical bridge INDEX entry for `gtkb-ollama-phase2-subproject-completion-coverage`. The tracked files already formed a complete thread through `VERIFIED`, but the missing `bridge/INDEX.md` document block made the thread invisible to live bridge scanners and obscured the already-verified evidence for the related project-lifecycle reconciliation.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | The Ollama Phase 2 completion bridge thread had eight tracked files ending in `VERIFIED`, but no `Document:` block in `bridge/INDEX.md`. During serialized restoration, a transient intermediate INDEX state exposed `-001` as fresh `NEW`; an external LO dispatch overwrote `-002` with a stale `GO` body before the full status chain was restored. | `show_thread_bridge.py` initially reported all eight files as unreferenced by INDEX; after repair, live LO scan reports zero actionable entries and 195 terminal VERIFIED entries. The overwritten `-002` body was restored to the historical Codex `NO-GO`, because the INDEX status and established version chain require `NO-GO` for that file. | Treat the bridge repair as complete, but Prime should consider a follow-up guard for status/body mismatch detection and atomic multi-status INDEX restoration to prevent transient duplicate dispatch. | Resolved |

### 2026-06-13 - WI-4413 FAB-01 Disposition Gap

Loyal Opposition (Codex/lo automation `keep-working-lo`) completed a disposition-gap investigation for `WI-4413`. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-WI-4413-fab01-disposition-gap.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | FAB-01 / WI-4413 is latest `VERIFIED` in the live bridge and targeted launchability verification passes, but MemBase still reports the work item as open/backlogged with no completion evidence. | `show_thread_bridge.py gtkb-fab-01-dispatch-substrate-revival` reports no drift and latest `VERIFIED`; targeted FAB-01 pytest passed 51 tests; live launchability doctor reports all five active dispatch targets launchable; `gt backlog list --id WI-4413 --json` still reports open/backlogged. | Prime should perform governed backlog disposition for WI-4413 and dedupe or restate WI-4479 if its remaining scope is not already covered. | Open |

### 2026-06-13 - Fable P1 Verified-Open Disposition Gap

Loyal Opposition (Codex/lo automation `keep-working-lo`) completed a cluster disposition-gap investigation for `WI-4415` through `WI-4419`. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-FABLE-P1-verified-open-disposition-gap.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | FAB-03 through FAB-07 all have latest `VERIFIED` bridge threads with no INDEX drift, but their MemBase rows remain open/backlogged with no completion evidence. | `show_thread_bridge.py` reports latest `VERIFIED` for `gtkb-fab-03-membase-backup`, `gtkb-fab-04-storage-reclamation`, `gtkb-fab-05-rule-file-retirement`, `gtkb-fab-06-narrative-corrections`, and `gtkb-fab-07-doctor-false-signals`; `gt backlog list --id WI-4415 ... WI-4419 --json` reports all five open/backlogged. | Prime should run a governed Fable backlog disposition pass, resolving satisfied rows or splitting any intentional residual scope into new work items. | Open |

### 2026-06-13 - WI-4395 uv Cache Command Surface Disposition

Loyal Opposition (Codex/lo automation `keep-working-lo`) completed a disposition investigation for `WI-4395`. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-WI-4395-uv-cache-command-surface-disposition.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | The original default uv cache outage does not reproduce in the current Codex LO shell, but GT-KB still lacks a canonical tracked command surface that pins `UV_CACHE_DIR`, temp paths, and optional tool dependencies for automation/verification commands. | Bare `uv run --project groundtruth-kb ...` and `uv --with pytest/ruff` probes now pass; `uv cache dir` still points to `C:\Users\micha\AppData\Local\uv\cache`; HYG-054 records ad hoc uv-cache/tmp sprawl; runtime retention only cleans `.gtkb-state` uv-cache dirs. | Prime should re-scope WI-4395 from "current outage" to a narrow command-wrapper/config proposal with denied-cache regression coverage and cleanup-pattern alignment. | Open |

### 2026-06-13 - WI-4479 Codex Dispatch Disposition

Loyal Opposition (Codex/lo automation resume) completed a disposition investigation for `WI-4479`. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-WI-4479-codex-dispatch-disposition.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | The original WI-4479 `codex_hooks` root-cause theory is stale, but headless Codex dispatch still has residual hook-failure and dispatch-state attribution risk. | Live `.codex/config.toml` uses `[features].hooks = true`; the historical Codex worker reached bridge-skill loading but emitted SessionStart/UserPromptSubmit/PreToolUse/PostToolUse failures; cross-harness trigger tests passed (77), while diagnose remains DEGRADED. | Prime should reframe WI-4479: close the deprecated-config portion, then either retain a narrowed Codex hook-failure smoke/regression item or add state-attribution checks for recipient-specific dispatch records. | Open |

### 2026-06-13 - WI-4529 Windows Dispatch Console Window Bridge Gap

Loyal Opposition (Codex/lo automation `keep-working-lo`) completed an advisory investigation for `WI-4529`. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-WI-4529-windows-dispatch-console-window-bridge-gap.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | The dirty worktree already contains the apparent `CREATE_NO_WINDOW` fix for `WI-4529`, but the live bridge has no matching indexed `WI-4529` proposal/GO and the current GO target paths do not authorize the two touched source files. | `git diff -- scripts/cross_harness_bridge_trigger.py groundtruth-kb/src/groundtruth_kb/bridge/worker.py`; current GO target-path checks for `gtkb-impl-auth-per-session-pointer-isolation`, `gtkb-prompt-role-hint-authority-emergency-fix`, and `gtkb-tafe-bridge-index-preview`; live LO scan had zero actionable entries. | Prime should file a narrow `WI-4529` bridge proposal, or revise an active thread to include `WI-4529` and both target paths, before committing the source change. | Open |
