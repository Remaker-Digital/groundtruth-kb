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

## How to Add an Entry

1. Add a new row under the latest date block (or start a new date block).
2. Fill: Area (Technical / Process / Product / Commercial), Finding (one sentence), Evidence (doc/code reference), Suggested action (brief), Status (Open / Resolved / Deferred).
3. When Mike resolves or defers an item, change Status in place; optionally add a one-line "Resolution" column or note in the same row.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
