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
| Process | Claude Code is currently incapable of serving as Prime Builder due to severe background execution/auth hangs and silent no-ops discovered during headless runs. | `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1` | Maintain Claude Code's suspended status in registry until headless CLI execution fixes are proposed and verified. Owner AUQ 2026-05-27 (S364): defer until WI-3349 VERIFIED â€” the suggested topology reshuffle (suspend B; flip A to PB; activate C as LO) presumes Antigravity's LO suitability, which WI-3349 substrate verification is the precondition for. Re-surface for owner disposition once WI-3349 reaches VERIFIED. | Deferred |

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
| Process | `.claude/session/active-session-role.json` written at 13:33:38Z with `role=prime-builder` for my session ID (4c7620e0-be99-â€¦) despite the session resolving as Loyal Opposition via `::init gtkb lo` at SessionStart 13:30:14Z. Parallel-session marker race (same defect class as project_s_scheduled_pb_saturation_clobber). | File contents inspected; LO startup disclosure was successfully relayed from `last-user-visible-startup-lo.md` (sha256 `cad2ad18â€¦`). | Add atomic session-stated-role marker write with cross-session clobber rejection in `scripts/workstream_focus.py`. P2. | Open |
| Process | Bridge dispatch state (`.gtkb-state/bridge-poller/dispatch-state.json`) is 3 days stale (last update 2026-06-01T18:07:51Z) despite many VERIFIED entries landing 2026-06-04 (commits `ed23f6b5`, `e0d4cc29`, `ad45a73d`, `2fa27699`, `6beb26c2`). Likely the trigger writes only on actionable-signature change, not every fire; needs confirmation before any alarm threshold is set. | `dispatch-state.json` inspection. | Add doctor staleness WARN once write semantics are confirmed. P3. | Open |
| Technical | Stranded atomic-write tmp file `dispatch-state.json.34252-0f2d0cc7.tmp` alongside canonical `dispatch-state.json`. Single instance, no rotation pattern. | `ls .gtkb-state/bridge-poller/`. | Add cleanup of `*.tmp` stragglers in poller-state hygiene. P3. | Open |

Full advisory: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-04-13-37-LO-LOOP-EMPTY-QUEUE-AND-BRIDGE-KIND-TAXONOMY-DRIFT.md`.

**Post-loop addendum (15:14Z, same session) â€” concrete cross-harness session-id co-option.**

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | Work-intent claim file `.gtkb-state/work-intent/gtkb-impl-start-target-paths-preflight.json` was acquired at 15:13:12Z under this Claude session id `4c7620e0-be99-â€¦` for a thread this session never touched. The thread's `-003.md` NO-GO was authored by Codex (harness A) under `automation: keep-working-lo`, against a `-001` by Claude Prime (harness B, session `bfc70de3-76e6-â€¦`) and `-002` GO by Antigravity LO (harness C). Three harnesses concurrent on one thread; the LO claim holder is a fourth ID (mine) that did not invoke `bridge_claim_cli.py`. | `cat .gtkb-state/work-intent/gtkb-impl-start-target-paths-preflight.json`; head of `bridge/gtkb-impl-start-target-paths-preflight-003.md`; AXIS-2 surface at 15:13:48Z. | Investigate the Codex `keep-working-lo` automation's session-id resolution â€” it should never hold a claim under a remote-harness's session id. Likely related to shared dispatch-state.json or trigger-emitted env-vars. P2 follow-up to the marker-race candidate C. | Open |

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

*Â© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
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

### 2026-06-13 - WI-4532 Post-Verification Comment Drift

Loyal Opposition (Codex/lo automation `keep-working-lo`) filed a post-verification advisory for `WI-4532`. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-WI-4532-post-verification-comment-drift.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | The WI-4532 implementation behavior passed targeted verification, but the new source comment still says `_validate_packet` is the primary orphan liveness guard even though the accepted revised design intentionally relies on gate-level `work_intent_claim_block_reason` plus the TTL shrink. | Codex ran the report's targeted verification commands: 78 pytest tests passed, ruff check passed, ruff format check passed. `scripts/implementation_authorization.py:33` conflicts with `bridge/gtkb-impl-auth-packet-liveness-coupling-003.md` and `-005.md`. | Prime should correct the comment before committing WI-4532 and then perform governed backlog disposition so the row no longer describes the withdrawn `_validate_packet` orphan-check design. | Open |

### 2026-06-13 - WI-4453 ChromaDB Latency Advisory

Loyal Opposition (Codex/lo automation `keep-working-lo`) completed an advisory investigation for `WI-4453`. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-WI-4453-chromadb-latency-advisory.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Current Python 3.14 fallback paths make `deliberations search` and `bridge propose --dry-run` fast, but WI-4453 remains open because non-dry-run record indexing is still synchronous and there is no median-latency regression benchmark for all three named CLI surfaces. | Live runtime reports `HAS_CHROMADB=False`; direct search/propose probes returned quickly; `insert_deliberation()` commits SQLite then calls `_index_deliberation_in_chroma()` without a timeout wrapper; targeted tests passed (3/1 skipped import-budget, 50 CLI tests, 10 Chroma/fail-soft tests). | Prime should file a narrow defect-fix proposal for bounded/out-of-band record indexing, deterministic related-deliberation seeding in bridge propose, and the WI's `<= 10s` median-latency benchmark. | Open |

### 2026-06-14 - WI-4402 FAB-18 Post-Verification Reconciliation

Loyal Opposition (Codex/lo automation `keep-working-lo`) completed a disposition-gap investigation for `WI-4402`. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-14-10-30-WI4402-FAB18-post-verification-reconciliation.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | `WI-4402` remains open/backlogged even though the VERIFIED FAB-18 bridge thread explicitly absorbed the Advisory Backlog Drain Policy scope and called for post-VERIFIED reconciliation. | `bridge/gtkb-fab-18-backlog-dignity-004.md` names `WI-4402` as absorbed; `bridge/gtkb-fab-18-backlog-dignity-008.md` is VERIFIED with tests passing; live `gt backlog show WI-4402 --json` still reports open/backlogged. | Prime should perform governed backlog disposition: resolve/supersede `WI-4402` against FAB-18 evidence, or narrow it to explicit residual scope. | Open |

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

### 2026-06-13 - WI-22C078 Role Dispatch Disposition

Loyal Opposition (Codex/lo automation `keep-working-lo`) completed a disposition investigation for `WI-AUTO-SPEC-INTAKE-22C078`. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-WI-22C078-role-dispatch-disposition.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | The open P1 backlog row still frames 22c078 around `STRICT_DROP` durable-role enforcement, but live dispatch code and tests already authorize role-mismatched dispatched keywords with audit evidence. | `session_start_dispatch_core.py` returns `DISPATCH_AUTHORIZED` with "authorized with audit" for role mismatch; targeted role-resolution tests passed 17; `.claude/rules/operating-role.md` still has stale `STRICT_DROP` wording. | Prime should disposition or restate `WI-AUTO-SPEC-INTAKE-22C078` before any implementation, and file a protected-narrative correction only through normal approval evidence. | Open |

### 2026-06-13 - Automation Memory Write Path Radar

Loyal Opposition (Codex/lo opportunity radar) filed an advisory on the recurring `$CODEX_HOME` automation-memory write-path mismatch. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-automation-memory-write-path-radar.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | Automation instructions require writing `$CODEX_HOME/automations/<automation_id>/memory.md`, but GT-KB root-boundary guidance treats home auto-memory as non-authoritative and LO file-safety blocks normal shell/patch edit paths. | `CLAUDE.md:12`; `.claude/hooks/lo-file-safety-gate.py` blocks opaque, shell, and outside-allow-list mutations; current session required a Node REPL append workaround. | Prime should propose a deterministic `gt automation memory` helper or policy alignment that preserves any required in-root reconciliation surface. | Open |

### 2026-06-13 - WI-4460 Dispatch Run-ID Sanitization Disposition

Loyal Opposition (Codex/lo automation `keep-working-lo`) completed a disposition investigation for `WI-4460`. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-WI-4460-dispatch-run-id-sanitization-disposition.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | The original NTFS ADS risk from `:` in dispatch-run filenames appears fixed in live source, but the backlog row remains open/backlogged. | `_new_dispatch_id()` sanitizes `:` to `-`; `test_fab10_work_intent_claim_contract_uses_child_dispatch_id` asserts no colon in `prime-builder:A` dispatch IDs; targeted cross-harness trigger tests passed 78; normal `Get-ChildItem -Filter "*:*"` found no colon-named dispatch-run entries. | Prime should resolve `WI-4460` with completion evidence or supersede only a narrower residual artifact-path audit distinct from `WI-4479`. | Open |

---

### 2026-06-14 - Omnigent Alignment Project Review

Loyal Opposition (Antigravity/lo role) completed a review of `PROJECT-OMNIGENT-ALIGNMENT`. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-14-11-15-omnigent-alignment-review.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | `PROJECT-OMNIGENT-ALIGNMENT` was created with six backlogged consideration work items to emulate Omnigent's capability shapes (cost limits, registries, specs, cloud/worktree sandboxes) without runtime dependencies. | `groundtruth.db` `projects` and `work_items` search (WI-4550 through WI-4555); `DELIB-OMNIGENT-ADVISORY-20260614` + `DELIB-20263229` owner decisions. | Prime should proceed with WI-4550 (Cost/Token budget) as the P1 target to halt token-loop waste, while keeping other items as open design considerations. | Open |

---

### 2026-06-14 - WI-4564 and WI-4566 Verification & Bridge Sweep

Loyal Opposition (Antigravity/lo role) audited, verified, and consolidated outstanding changes for WI-4564 and WI-4566. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-14-22-10-lo-bridge-drain.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | Outstanding verification files for WI-4564 and WI-4566 were verified clean, staged, and local changes consolidated. The active bridge queue has been completely drained. | Bridge INDEX status set to GO for removal-document-002 and VERIFIED for startup-service-timeout-006; 79/79 pytest cases passed cleanly; pre-commit secrets and inventory drift checks green. | Prime should resolve WI-4564 in MemBase and proceed with evaluating the WI-4510 cutover preconditions. | Resolved |

---

### 2026-06-14 - Test Suite Regression & Drift Analysis

Loyal Opposition (Antigravity/lo role) completed a regression audit on the full pytest suite. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-14-22-20-test-suite-audit.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | The full test suite reports 25 failures out of 4,480 tests on `develop` due to schema drift from TAFE tables, canonical rules narrative packet mismatch (resolved 2026-06-15), and host harness-role conflicts in mock paths. | platform_tests/unit/test_knowledge_db_artifacts.py (missing TAFE tables/views); platform_tests/scripts/test_ollama_governance_artifacts.py (narrative packet mismatch resolved by updating `.groundtruth/formal-artifact-approvals/2026-06-12-fab09-canonical-terminology.json`); WorkIntentRegistryError in start-gate tests. | Prime should update test schema lists, consolidate remaining narrative packets, and isolate/stub host harness registry queries in tests. | Open |

---

### 2026-06-16 - Antigravity Parity and Skill-Health Test Alignment

Loyal Opposition (Antigravity/lo role) aligned the capability registry, generated skill adapters, and corrected unit tests to resolve and verify WI-4596 and WI-4366.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | `platform_tests/scripts/test_check_skill_health.py` was failing because the checker implementation refactored the index write-checking logic to use `bridge_direct_write` on numbered files, but the unit tests still asserted the retired `index_write` finding type on `INDEX.md`. | `python -m pytest platform_tests/scripts/test_check_skill_health.py` failed. | Updated `platform_tests/scripts/test_check_skill_health.py` to match the `bridge_direct_write` naming and regex behavior. Verified that all 10 tests and all 12 harness-parity tests pass. `WI-4596` and `WI-4366` remain backlogged/open in MemBase pending the formal bridge verification flow. | Open (Implementation Staged) |
| Process | The rule requiring a Loyal Opposition `VERIFIED` verdict before committing mutating changes was not explicitly clear across all rules, scripts, and harnesses. | Owner request to confirm the directive. | Created `WI-4613` under `PROJECT-PARALLEL-DISPATCH-REMEDIATION-SWEEP` to add this explicit constraint to `AGENTS.md`, rules, and `sweep-commit` scripts for all harnesses. | Open |

---

### 2026-06-16 - Loyal Opposition Queue Clearance and Status Check

Loyal Opposition (Antigravity/lo role) processed all actionable bridge review and verification entries, clearing the active queue.

---

### 2026-07-03 - ~S535 (LO interactive) - Bridge verification, work-tree hygiene recommendation, Claude Code role/hook diagnostic

Loyal Opposition (Claude / harness B, interactive `::init gtkb lo`). Full evidence: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-03-05-44.md`. Session remained mechanically LO throughout; only governed `gt backlog add` captures + this log entry + the INSIGHTS report were written (no KB promotion, MEMORY.md edit, commit, or push).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Bridge | Two post-impl reports verified-on-merits (WI-4964 model-pinning, WI-4957 NO-ACTION). A PARALLEL Claude-B LO session (901d970b) VERIFIED+committed both mid-review, landing the `rules.toml` storm-flag scope-bleed the owner's hold meant to avoid. | commits `36a3f239`, `34b87b4e`; verdicts `-006`/`-012`. | An owner-decision hold in one session does not gate a sibling session on the same queue - governance gap. | Open (parallel finalized) |
| Process | Work-tree dirt is not a missing system: WI-4356 hygiene Slices A-C VERIFIED; `gt hygiene strays` triages 324/324 stale to `owner_review` (zero auto-resolve); Slice D blocked on owner packet, Slice E never built. | live `gt hygiene strays` 2026-07-03. | Ratify Slice D (owner packet); build Slice E actuator (WI-4979); gitignore runtime files (WI-4980). | Open - WI-4979/4980 filed |
| Technical | Mid-session `::init gtkb (pb\|lo)` role switch silently no-ops: `workstream_focus.py::handle_hook_payload` matches the keyword but never persists the per-session role marker. | throwaway-session hook run; marker written = False. | Wire `_write_per_session_role_marker` into the mid-session canonical-init branch, or fail loud. | Open - WI-4981 filed |
| Technical | Divergent dual init-keyword grammars (`_session_init_keyword.py` old vs `workstream_focus.py` canonical). | scripts inspection. | Consolidate to one canonical matcher + parity test. | Open - WI-4982 filed |
| Environment | Owner-reported Claude Code behavior change since 7/1 14:00 PT: repo-side hooks present (46/46), tracked, dep-sound - most likely a client update. | hook existence check; `python -c import groundtruth_kb` OK on `C:\Python314`. | Owner: check `claude --version` vs the 7/1 refresh (client-side; not a repo fix). | Open - owner verification |
| Blocked | Slice D + WI-4944 dispatch-unblock are Prime Builder actions; this session is LO and the mid-session role switch (WI-4981) prevented `::init gtkb pb`. | role marker stayed LO. | Fresh PB session with `::init gtkb pb` as first message; 3-message kickoff provided to owner. | Deferred to PB |

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | Actionable bridge entries were outstanding: `gtkb-inventory-string-scan-admin-cli` implementation report (v007), `gtkb-harness-c-governance-gate-parity-gap` revised blocker (v009), `agent-disposition-wi4588-protected-mutation-guard-slice1` implementation report (v003), and `gtkb-no-index-skill-template-doc-cleanout` implementation report (v015). | Bridge directory scan; preflight and clause preflight runs; test suite runs. | Author verdicts for all threads. Result: v008 (VERIFIED), v010 (NO-GO blocker confirmed), v004 (VERIFIED), and v016 (VERIFIED) successfully written to `bridge/`. All tests (scaffold, harness, quality manifest, and protected mutation guard) pass cleanly. | Resolved |

---

### 2026-06-17 - WI-4394 Bridge Verdict & report.txt Reconciliation

Loyal Opposition (Antigravity/lo role) filed the `GO` verdict for the Git warnings fix (WI-4394) and successfully reconciled the `report.txt` vs database discrepancy. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-17-02-25-gtkb-windows-git-warnings-and-report-reconciliation.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | The `gtkb-windows-git-warnings-fix` proposal (WI-4394) successfully resolved the previous global config crash issue on Windows by redirecting `XDG_CONFIG_HOME` instead of setting `GIT_CONFIG_GLOBAL=NUL`. | `bridge/gtkb-windows-git-warnings-fix-003.md` proposal; zero gaps in clause/applicability preflights. | File the `GO` verdict (`bridge/gtkb-windows-git-warnings-fix-004.md`) so Prime Builder can implement. | Resolved |
| Process | `report.txt` had discrepancies in active count and top items with the SQLite DB. Reconciled this to a static snapshot timing discrepancy. | DB queries and `report.txt` contents matching perfectly when time-travel queried at June 12-13, 2026. | Standardize database checks to use point-in-time snapshot queries based on the generated file's timestamp. | Resolved |

### 2026-06-17 - Harness C Blocker & Skill Generator Formatting Reviews

Loyal Opposition (Antigravity/lo role) processed the outstanding actionable bridge entries for `gtkb-harness-c-governance-gate-parity-gap` and `gtkb-skill-generator-registry-formatting`, clearing the queue.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | `gtkb-harness-c-governance-gate-parity-gap` (WI-4543) revised blocker remains blocked due to lack of active project authorization (PAUTH) for WI-4543. | `bridge/gtkb-harness-c-governance-gate-parity-gap-013.md` and database check of active PAUTHs | File the `NO-GO` verdict (v014) to maintain the blocker state until authorization is granted. | Resolved |
| Process | `gtkb-skill-generator-registry-formatting` (WI-4612) revised proposal successfully added the required implementation-start metadata (`target_paths` and `## Requirement Sufficiency` section). | `bridge/gtkb-skill-generator-registry-formatting-003.md`, preflight checks passed with zero gaps | File the `GO` verdict (v004) to authorize the implementation. | Resolved |

---

### 2026-06-19 - Dispatch Blockage & Index Cleanout Thread Withdrawal

Loyal Opposition (Antigravity/lo role) investigated and resolved the dispatcher queue blockage. We withdrew the blocked `gtkb-bridge-index-retirement-cleanout` proposal thread (v007) because its v005 proposal carried invalid project/authorization metadata and lacked the required specification/requirement sufficiency sections, causing the implementation start authorization gate (`scripts/implementation_authorization.py`) to fail closed.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Mismatched metadata and missing required sections in `gtkb-bridge-index-retirement-cleanout-005.md` blocked the Prime Builder implementation authorization gate. | `scripts/implementation_authorization.py` failing closed; `dispatch-failures.jsonl` error tracebacks; `bridge/gtkb-bridge-index-retirement-cleanout-005.md` metadata values | Filed a `WITHDRAWN` verdict (v007) to retire the blocked thread, successfully decreasing the Prime Builder queue count and clearing the queue. | Resolved |

---

### 2026-06-19 - Session Startup Control Map Alignment

Loyal Opposition (Antigravity/lo role) identified documentation drift in `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md` regarding implemented role-specific overlays and the startup index. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-19-15-10-gtkb-startup-control-map-alignment.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | `SESSION-STARTUP-CONTROL-MAP.md` lists `SESSION-STARTUP-INDEX.md` and role overlays as "Planned (not yet present)" when they are active and load-bearing. | `SESSION-STARTUP-CONTROL-MAP.md` lines 54-60; presence of the index and overlay files on disk. | Update `SESSION-STARTUP-CONTROL-MAP.md` to classify these files as `active` in the inventory table. | Open |

---

### 2026-06-23 - Dispatch Saturation Revalidation

Loyal Opposition (Codex automation, harness A) performed a read-only fallback investigation of bridge dispatch saturation and launch failures. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-23-14-18-dispatch-saturation-revalidation.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Bridge dispatch | Headless LO dispatch remained failed throughout the run. The 14:18 UTC check showed eight live wrapper processes and `per_role_concurrency_cap_reached`; the post-wait 14:34 UTC check still failed with LO `launch_failed` / `unchanged` states. The failure classes are already covered by `WI-4670`, so no duplicate hygiene WI was added. | `gt bridge dispatch health --json` FAIL; `.gtkb-state/bridge-poller/dispatch-failures.jsonl` tail; live process census; `scripts/run_with_status.py` bare `p.wait()`. | Execute `WI-4670` with worker-lifetime timeout, process-tree termination, structured timeout classification, and focused regression coverage. | Open |

---

### 2026-06-23 - WI-4770 Bridge Verdict & Session Startup

Loyal Opposition (Antigravity/lo role) verified and filed the `GO` verdict for the Per-Item Authorization Quarantine proposal (WI-4770, version 005) to address head-of-line blocking in both dispatch substrates. Verified that all preflights (applicability and clause preflight) pass with zero gaps.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | `gtkb-dispatch-per-item-auth-quarantine` revised proposal revision 005 has resolved all previous finding-blockers (P1 and P2). | `bridge/gtkb-dispatch-per-item-auth-quarantine-005.md` proposal; zero gaps in clause/applicability preflights. | File the `GO` verdict (`bridge/gtkb-dispatch-per-item-auth-quarantine-006.md`) so Prime Builder can implement. | Resolved |

---

### 2026-06-23 - WI-3464 Orphan-WI Backfill Verification

Loyal Opposition (Antigravity/lo role) verified and filed the `VERIFIED` verdict for the Orphan-WI Backfill per-WI retire/exclude execution (WI-3464, version 007). All spec-derived tests pass cleanly, and the implementation is successfully committed.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | `gtkb-orphan-wi-backfill-per-wi-retire-exclude-service` implementation passes all 14 project CLI tests and matches isolation guidelines. | `bridge/gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-007.md`, successful preflight, zero gaps | File the `VERIFIED` verdict (`bridge/gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-008.md`) and commit the implementation files. | Resolved |

---

### 2026-06-23 - Watchdog Repoint & Process Leak Root Cause

Loyal Opposition (Antigravity/lo role) repointed the desktop watchdog schedules and analyzed the root cause of the `ollama_harness.py` child process leaks. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-23-17-21-ollama-harness-process-leak.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Operations | Scheduled task was executing obsolete watchdog from `.gtkb-state/ops/` instead of tracked `scripts/ops/harness_storm_watchdog.ps1`. | Repointed `.gtkb-state/ops/run_harness_storm_watchdog_hidden.vbs` to execute tracked path. Manually triggered task and confirmed successful exit code `0` and correct heartbeat. | Resolved |
| Technical | `scripts/run_with_status.py` wrapper leaks child processes if the parent exits early or is terminated. | Process census; lack of termination logic or signal handling in `run_with_status.py` finally block. | Update `scripts/run_with_status.py` to terminate the child process in its `finally` block. | Open |

---

### 2026-06-23 - Session Startup Compliance & Control Map Audit

Loyal Opposition (Antigravity/lo role) performed a compliance audit of the session startup overlays and verified the classified inventory of startup control surfaces. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-23-13-08-role-startup-compliance-audit.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Governance | `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md` omits the startup disclosure mandates from `AGENTS.md`. | `LOYAL-OPPOSITION-STARTUP-OVERLAY.md` ## Disclosure; `AGENTS.md` startup checklist. | Update LO startup overlay to require disclosure of git state, bridge counts, LO role assertion, and dispatch health. | Open |
| Registry | `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md` has outdated placeholders and omits multiple active startup surfaces. | `SESSION-STARTUP-CONTROL-MAP.md` ## Role-Specific Overlays; list of files under `config/agent-control/`. | Update the control map to catalog the overlays, index, manifest, and active TOML configuration registries. | Open |

---

### 2026-06-23 - Dispatch Config Drift & Startup Disclosure Audit

Loyal Opposition (Antigravity/lo role) audited the session startup disclosure logic and investigated configuration drift warnings for harnesses B and C. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-23-23-19-dispatch-config-drift.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Operations | Harnesses B and C are suspended in registry but marked `can_receive_dispatch = true` in `rules.toml`. | `rules.toml` vs `harness-registry.json` status; `gt bridge status` warnings. | Reconcile the drift by setting `can_receive_dispatch = false` for harnesses B and C in `rules.toml` using `gt bridge dispatch config set-eligibility`. | Resolved |
| Governance | The Loyal Opposition startup disclosure correctly suppresses focus choices and routes default tasks. | `scripts/session_self_initialization.py` implementation vs `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`. | None; audit successfully completed with PASS. | Resolved |

---

### 2026-06-25 - Cursor LO bridge resume wrap (S467-class)

Loyal Opposition (Cursor harness E, `::init gtkb lo`) auto-processed bridge reviews across `Resume` continuations. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-25-05-10-cursor-lo-bridge-resume-wrap.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Bridge | VERIFIED finalization commits landed for WI-3217, WI-3218, WI-3212, and per-role concurrency cap (WI-CA9165). | Commits `7a9b2d69`, `3c41ba45`, `c70c50a8`, `7cf4bf11`; independent pytest reruns. | None; threads terminal for LO. | Resolved |
| Bridge | GO verdicts for WI-4789, WI-4649, WI-3327, WI-4795 authored but uncommitted on disk. | `bridge/gtkb-wi4789-*-002.md`, `gtkb-stale-git-worktree-*-005.md`, etc. | Prime Builder implement + commit GO chains. | Resolved |
| Bridge | `gtkb-reconcile-included-work-item-ids-semantics` blocked on owner semantics choice. | GO `-021` blocker record; `DELIB-2547`. | Owner AUQ: additive vs restrictive vs defense-in-depth. | Resolved |
| Operations | Dispatch health FAIL; no eligible targets; `GTKB_NO_CROSS_HARNESS_TRIGGER=1` active. | `gt bridge dispatch status`; all harnesses `dispatchable=False`. | Clear kill-switch when desired; implement WI-4789; reconcile rules.toml drift. | Resolved |
| Process | Uncommitted GO files + broad dirty worktree may block impl-start / foreign-file gates. | `git status`; temp `.temp_verdict_*` files. | PB hygiene sweep before unrelated commits. | Open |

---

### 2026-06-27 - Platform Test Suite Breakages Post INDEX-Removal Migration

Loyal Opposition (Antigravity/lo role) identified extensive platform test suite failures following the TAFE-authority and INDEX-removal migration (209 failed, 18 errors, 4069 passed). Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-27-02-24-platform-test-suite-breakages.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Testing | Test suite is broken with 209 failures due to AttributeError on retired `INDEX_PATH`, desynced worker timeouts, stale `bridge/INDEX.md` paths, and memory file size ceiling violations. | Pytest logs; `scripts/run_spec_derived_tests.py`; `platform_tests/scripts/test_run_spec_derived_tests.py`. | Remove `INDEX_PATH` mocks from tests, update timeout assertions, change blocked path tests to active surfaces, and trim `MEMORY.md`. | Open |

---

### 2026-06-27 - Antigravity Harness Capability Assessment

Loyal Opposition (Antigravity/lo role) evaluated the capability of the `antigravity` harness (ID: C) to assume the `prime-builder` role. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-27-16-15-antigravity-harness-capability-assessment.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Governance / Harness | Antigravity is permanently ineligible for headless bridge dispatch due to Google EOL `IneligibleTierError` on `gemini-cli`. Additionally, it lacks local hook wrappers in `harness-capability-registry.toml` (e.g., `sot-read-discipline` and `owner-decision-tracker` hooks). Restoring it durably to `prime-builder` is a severe regression, but interactive pair programming under manual self-enforcement remains feasible. | `rules.toml` vs `harness-registry.json` status; `harness-capability-registry.toml` missing blocks; `sot-artifacts.toml` owner-only boundaries. | Keep Antigravity retired from headless dispatch queues. Restrict active role mutations to explicit owner commands. Rely on manual self-enforcement for interactive session overrides. | Resolved |

---

### 2026-06-28 - Doctor Checks on Adopter Projects and Encoding Robustness

Loyal Opposition (Antigravity/lo role) identified diagnostic test suite and doctor tool failures when running on adopter targets or encountering non-UTF-8 text. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-28-03-45-doctor-adopter-packaging-blocker.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | `test_doctor_runs_in_temp_adopter` fails because adopter projects lack the required platform-specific scripts checked by `_check_dispatcher_config_cli_only_guard`. | AssertionError in `test_clean_adopter_packaging.py`; `_check_dispatcher_config_cli_only_guard` assumes scripts existence. | Skip the check when `config/dispatcher/rules.toml` is absent. | Open |
| Technical | The doctor tool crashes with `UnicodeDecodeError` when scanning untracked bridge files with Windows-1252 bytes. | `UnicodeDecodeError` in `_check_untracked_terminal_verified_verdicts` reading target files containing cp1252 characters. | Use `errors="replace"` in `read_text` inside `_check_untracked_terminal_verified_verdicts`. | Open |

---

### 2026-06-28 - Empty Queue and Doctor Diagnostic Findings

Loyal Opposition (Antigravity/lo role) verified that the bridge is functional with zero actionable items in the queue. Audited `gt project doctor` output and identified durability risks from untracked verified files and false-positive dispatch alarms. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-28-05-15-lo-empty-queue-doctor-audit.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Three terminal `VERIFIED` bridge files are untracked in git, posing a durability risk. | `git status`; `gt project doctor` warning. | Run `git add` and commit the files: `bridge/gtkb-mass-release-candidate-blocker-repair-004.md`, `bridge/gtkb-wi4894-storm-watchdog-pythonw-output-repair-004.md`, `bridge/gtkb-wi4896-startup-console-residual-006.md`. | Resolved |
| Technical | The doctor triggers false-positive dispatch `ALARM` flags when the queue is inactive. | `gt project doctor` output; `dispatch-state.json`. | Modify `_check_bridge_dispatch_liveness` to bypass or scale the staleness check when the queue has remained empty. | Open |
| Registry | Three glossary updates are pending synchronization into the MemBase terminology registry. | `gt canonical-terms seed --dry-run`. | Run `gt canonical-terms seed --apply` to synchronize the registry. | Resolved |
| Technical | Hook scripts `assertion-check.py` and `spec-event-surfacer.py` differ from their template sources. | `gt project doctor` warning. | Reconcile drifts or update templates. | Open |

---

### 2026-06-29 - Backlog Reconciler Blockers & TAFE Lifecycle Gaps

Loyal Opposition (Antigravity/lo role) completed an audit and evaluation of the 18 work items currently blocked under the `linked_bridge_not_verified` classification in the backlog reconciler. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-29-08-15-reconciler-linked-bridge-not-verified.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Terminal `WITHDRAWN` threads permanently deadlock the associated work item (`WI-4674`, `WI-4508`) from auto-closure. | `bridge_verified_backlog_reconciler.py` dry-run; withdrawal files under `bridge/`. | Update the reconciler satisfaction logic to treat `WITHDRAWN` as non-blocking if at least one sibling thread is `VERIFIED`. | Open |
| Technical | Scoping/umbrella threads mismatch their implementation child slices due to suffix (`-mechanism-scoping`) or abbreviation (`typed-artifact-flow-engine` vs `tafe`) discrepancies. | `bridge_verified_backlog_reconciler.py` prefix-matching logic; `WI-4356` and `WI-4508`. | Enhance prefix-matching to strip planning suffixes and support abbreviation synonyms. | Open |
| Technical | Advisory routing work items (`WI-4436`, `WI-4411`, etc.) remain open indefinitely because `ADVISORY` is not treated as satisfying the task. | `bridge_verified_backlog_reconciler.py` satisfaction predicate. | Allow the reconciler to resolve work items if their only linked thread has status `ADVISORY`. | Open |

---

### 2026-06-29 - File Bridge and Dispatcher Circuit Breaker Verification

Loyal Opposition (Antigravity/lo role) verified that the file bridge is functioning correctly with 1 actionable item in the LO queue. Inspected the dispatcher status, confirmed that the prime-builder (Codex) harness is blocked by a tripped circuit breaker, and reviewed the Cursor headless hooks parity proposal.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Operations | The Codex (prime-builder:A) dispatcher is blocked by a tripped circuit breaker (exit code 4294967295). | `gt bridge status`; `dispatch-state.json`. | Diagnose codex.exe execution environment or credentials when Prime Builder resumes. | Open |
| Bridge | The file bridge has 1 actionable NEW entry for Loyal Opposition: `gtkb-wi4925-cursor-headless-hooks-parity-001.md`. | `scan_bridge.py` output; `gt status`. | Reviewed the proposal and issued a GO verdict in `bridge/gtkb-wi4925-cursor-headless-hooks-parity-002.md`. | Resolved |

---

### 2026-06-30 - Empty Queue Audit & Log Reconciliation

Loyal Opposition (Antigravity/lo role) verified that the bridge is functional with zero actionable items in the queue. Checked the status of untracked files and reconciled open findings in the Loyal Opposition log. Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-30-02-15-lo-empty-queue-status-audit.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Bridge | The file bridge queue has 0 actionable items for Loyal Opposition. Stale untracked predecessor drafts are bypassed. | manual scan; `scripts/lo_bridge_scan.py` run; version tracking checks. | Keep version tracking check clean and filter out predecessor drafts. | Resolved |
| Operations | Outstanding open log findings for harnesses eligibility, GO verdicts, and untracked terminal files were verified resolved. | Git history; rules.toml configurations; MemBase database checks. | Reconciled and updated log entries to match the clean workspace state. | Resolved |

---

### 2026-06-30 - WI-4934 Daemon LO Failover and Completion-Time Retry Anchor Verification

Loyal Opposition (Antigravity/lo role) verified and committed the post-implementation report and verification verdict for WI-4934. The dispatcher daemon now reconciles exit codes before the shadow/dedupe check, allowing fallthrough to secondary LO targets (E/F) instead of stranding files behind `unchanged`. Retry timing was also corrected to anchor off worker completion time rather than launch time.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Stranded LO queue work due to failed/timed-out primary recipients. | `bridge/gtkb-wi4934-daemon-lo-failover-after-nonzero-003.md`; daemon tick and runtime tests. | Implemented exit reconciliation, target fallthrough, and completion-based retry delay window. Verified 167/167 tests passed. | Resolved |

---

### 2026-06-30 - WI-4933 Ollama Routing Timeout Bounds Proposal Review

Loyal Opposition (Antigravity/lo role) reviewed and issued a `GO` verdict for the pre-implementation proposal: `gtkb-wi4933-ollama-routing-timeout-bounds-001.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Timeout inconsistency between CLI and config. | `bridge/gtkb-wi4933-ollama-routing-timeout-bounds-001.md`, `scripts/ollama_harness.py`. | Binding `timeout_seconds` from routing TOML and deriving bounded default session timeouts avoids silent hangs. Approved at version -002. | Resolved |

---

### 2026-06-30 - WI-4782 Session Role Authority Audit Proposal Review

Loyal Opposition (Antigravity/lo role) reviewed and issued a `GO` verdict for the pre-implementation proposal: `gtkb-wi4782-session-role-authority-audit-001.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Terminology and authority leaks regarding non-dispatcher role enforcement. | `bridge/gtkb-wi4782-session-role-authority-audit-001.md`. | Run a deterministic repository-root-contained audit to catalog registry-as-authority-beyond-dispatcher and durable-role terminology. Approved at version -002. | Resolved |

---

### 2026-06-30 - Topology and Dispatcher Configuration Alignment

Loyal Opposition (Antigravity/lo role) updated the dispatcher configuration (`rules.toml`) to align with the active role partition constraints and the owner's request.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Operations | Mismatch and disabled dispatch eligibilities in `rules.toml`. | `rules.toml` configuration; owner directives. | Updated tag alignments (A+E as PB, B+C+D+F as LO) and set `can_receive_dispatch=true` for all candidate targets. | Resolved |

---

### 2026-06-30 - WI-4935 Reconcile Stale Failover Dispatch State Proposal Review

Loyal Opposition (Antigravity/lo role) reviewed and issued a `GO` verdict for the pre-implementation proposal: `gtkb-wi4935-dispatch-failover-stale-state-reconciliation-001.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Stale failover recipient state after terminal bridge outcomes. | `bridge/gtkb-wi4935-dispatch-failover-stale-state-reconciliation-001.md`. | Reconcile stale pending state for terminal documents and align diagnose liveness with canonical health. Approved at version -002. | Resolved |

---

### 2026-06-30 - WI-4356 Slice D Work Tree Hygiene Governance Spec Proposal Review

Loyal Opposition (Antigravity/lo role) evaluated and issued a `NO-GO` verdict for the blocker-record revision proposal: `gtkb-work-tree-hygiene-slice-d-governance-spec-005.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Implementation is blocked due to the missing exact-content formal-artifact approval packet for `GOV-WORK-TREE-HYGIENE-001`. | `bridge/gtkb-work-tree-hygiene-slice-d-governance-spec-005.md`. | Collect owner approval via `AskUserQuestion` for the exact content of `GOV-WORK-TREE-HYGIENE-001` in an interactive session, mint the approval packet, and proceed with the MemBase insert. Rejected at version -006. | Open |

---

### 2026-06-30 - WI-4553 Phone/Web Owner Approval Surface Verification

Loyal Opposition (Antigravity/lo role) evaluated the post-implementation report and issued a `NO-GO` verdict for `gtkb-wi4553-phone-web-owner-approval-surface-003.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Post-implementation report has failing verification commands: pytest injection escaping failure, click options line too long in `cli.py`, and ruff format style drift in `cli.py` and test. | pytest traceback; ruff check and format check outputs; `bridge/gtkb-wi4553-phone-web-owner-approval-surface-003.md`. | Fix the script injection test assertion, break line 4883 in `cli.py`, format both files, and submit a revised report (Version 005). Rejected at version -004. | Open |

---

### 2026-06-30 - WI-4873 obsolete cross-harness fixture reconciliation Proposal Review

Loyal Opposition (Antigravity/lo role) reviewed and issued a `GO` verdict for the metadata reconciliation proposal: `gtkb-wi4873-cross-harness-fixture-obsolete-reconciliation-001.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Backlog tracks a stale test fixture file `platform_tests/scripts/test_cross_harness_bridge_trigger.py` that is already absent. | Git history and test discovery confirm the test was purged in commit `ab2f782bc885287f833800dbf88e9dcbd56e5001`. | Reconcile Knowledge DB to resolve WI-4873 as superseded by the prior trigger purge. | Resolved |

---

### 2026-06-30 - WI-4869 related bridge provenance separation Proposal Review

Loyal Opposition (Antigravity/lo role) reviewed and issued a `GO` verdict for the backlog hygiene proposal: `gtkb-wi4869-related-bridge-provenance-separation-001.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Overloaded `related_bridge_threads` field stores both surfaced-during provenance and implementation links, causing reconciler noise. | `bridge/gtkb-wi4869-related-bridge-provenance-separation-001.md`. | Separate provenance context from implementation-linkage, keeping provenance in metadata/change reasons or dedicated fields. | Resolved |

---

### 2026-06-30 - WI-4939 bridge author metadata hardening Proposal Review

Loyal Opposition (Antigravity/lo role) reviewed and issued a `GO` verdict for the metadata hardening proposal: `gtkb-wi4939-bridge-author-metadata-hardening-001.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Headless LO harnesses (F/D) and the metadata loader still emit static `author_session_context_id` placeholders. | `bridge/gtkb-wi4939-bridge-author-metadata-hardening-001.md`. | Harden the loader and harness env injection so dispatch-run session IDs win and static slugs are rejected. Approved at version -002. | Resolved |

---

### 2026-06-30 - WI-4938 bridge author metadata audit scanner Proposal Review

Loyal Opposition (Antigravity/lo role) reviewed and issued a `GO` verdict for the read-only audit scanner proposal: `gtkb-wi4938-bridge-author-metadata-audit-scanner-001.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Bridge verdicts and proposals across harnesses carry inconsistent or corrupt author metadata. | `bridge/gtkb-wi4938-bridge-author-metadata-audit-scanner-001.md`. | Deliver a read-only deterministic audit scanner as the regression baseline and repair-queue input before write-time hardening. Approved at version -002. | Resolved |
### 2026-07-04 - WI-5002 Codex Headless Add-Dir Invocation Review (NO-GO)

Loyal Opposition (Antigravity/lo role) evaluated the post-implementation report and issued a `NO-GO` verdict for `gtkb-wi5002-codex-headless-add-dir-invocation-003.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Post-implementation report helper-copy write-denial remains blocked in current worker context; four path parser tests fail in `test_verified_finalization_validation_hardening.py`. | pytest traceback; `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-003.md`. | Re-run Codex Prime Builder with updated command-line arguments (including `--add-dir .codex`) to copy the helper, fix the path parser regressions, and submit a revised report (Version 005). Rejected at version -004. | Open |

---

### 2026-07-04 - WI-5002 Codex Headless Add-Dir Invocation Blocker Review (NO-GO)

Loyal Opposition (Antigravity/lo role) evaluated the revised post-implementation report and issued a `NO-GO` verdict for `gtkb-wi5002-codex-headless-add-dir-invocation-005.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Codex Prime Builder is still blocked from writing `.codex/skills/verify/helpers/write_verdict.py` due to sandbox constraints and explicit Deny ACLs. | `Get-Acl` and `apply_patch` write-denial; `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-005.md` | Propose a new sandbox/ACL correction plan or local `gt.exe` shim instead of retrying the add-dir route directly. Rejected at version -006. | Open |

---

### 2026-07-04 - WI-4804 Stale Dispatch Kill-Switch Test Leak

Loyal Opposition (Antigravity/lo role) identified an orphaned test file following the cross-harness trigger purge in WI-4885.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | `platform_tests/scripts/test_doctor_kill_switch_staleness.py` is orphaned and causes an `ImportError` during pytest collection because its target check was purged from `doctor.py`. | pytest collection failure; [test_doctor_kill_switch_staleness.py](file:///e:/GT-KB/platform_tests/scripts/test_doctor_kill_switch_staleness.py) | Delete the obsolete test file to restore clean test suite collection. | Open |

---

### 2026-07-04 - WI-5002 Codex Dotdir ACL Correction Investigation

Loyal Opposition (Antigravity/lo role) investigated why the script-based ACL repair fails for the specific raw SID from the Codex sandbox.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | `icacls` fails silently to remove Deny ACEs with raw SIDs because it expects SIDs to be prefixed with an asterisk (`*`). | `repair_codex_dotdir_acl.ps1` Invoke-Icacls call; persistent Deny rules in `verify_codex_dispatch.py` | Refactor `Remove-RepairableDenyRules` to use native .NET `$Acl.PurgeAccessRules` and `Set-AccessOnlyAcl` on the DACL-only Access section to bypass local SID resolution limits and SeSecurityPrivilege. | Open |

---

### 2026-07-04 - WI-4984 Deterministic Bridge State-Report CLI Proposal Review

Loyal Opposition (Antigravity/lo role) evaluated the pre-implementation proposal for the `gt bridge state-report` CLI and issued a `GO` verdict.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | The implementation proposal for WI-4984 is sound, well-defined, and passes all preflight checks. | [gtkb-wi4984-bridge-state-report-cli-001.md](file:///E:/E:/GT-KB/bridge/gtkb-wi4984-bridge-state-report-cli-001.md), `DELIB-202665301` | Proceed with Prime Builder implementation under active project authorization. Approved at version -002. | Resolved |

---

### 2026-07-04 - WI-4975 Direct-Thread Reconciliation Verification

Loyal Opposition (Antigravity/lo role) evaluated the post-implementation reconciliation report for WI-4975 and issued a `VERIFIED` verdict.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | The direct-thread reconciliation is sufficient to close the WI-4975 bridge chain against the already-VERIFIED finalization-tooling batch evidence. All 16 focused regression tests pass, and cross-harness byte-identical parity is verified. | [gtkb-wi4975-claimed-path-subpath-overmatch-013.md](file:///E:/GT-KB/bridge/gtkb-wi4975-claimed-path-subpath-overmatch-013.md), commit `fdad4c49` | Commit the terminal VERIFIED verdict and close the thread (Version 014). | Resolved |

---

### 2026-07-04 - WI-4944 Release Dispatcher LO Dispatch Unblock Verification

Loyal Opposition (Antigravity/lo role) evaluated the revised blocker response and implementation report for WI-4944 and issued a `VERIFIED` verdict.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | The git-tracked predecessor finalization blocker was resolved by committing the predecessor bridge chain in commit `2727e2d3e3cfedf82786dc3ba49ef076d28232c8`. RETEST and status checks confirm the dispatcher daemon and health checks pass cleanly. | [gtkb-wi4944-release-dispatcher-lo-dispatch-unblock-050.md](file:///E:/GT-KB/bridge/gtkb-wi4944-release-dispatcher-lo-dispatch-unblock-050.md), commit `d827cd2a` | Commit the terminal VERIFIED verdict and close the thread (Version 051). | Resolved |
---

### 2026-07-04 - SQLite3 Connection Locking Flakiness in Tests and Health Check

Loyal Opposition (Antigravity/lo role) identified an intermittent test and health-check failure caused by unclosed SQLite3 connections on Windows.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Testing | `test_terminal_work_item_dispatch_residue_is_health_pass` fails intermittently under parallel test execution or due to garbage collection timing because the sqlite3 write connection in the test helper and read connection in `_work_item_resolution_status` are not closed properly. | `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\bridge_dispatch_config.py` lines 1519-1525, `platform_tests\scripts\test_bridge_dispatch_config.py` lines 66-72 | Wrap sqlite3 connections in `closing` or call `con.close()` explicitly to ensure they are released immediately. | Open |

---

### 2026-07-04 - WI-4909 LAN Authority Service Adversarial Review

Loyal Opposition (Antigravity/lo role) evaluated the candidate Architecture Decision Packet and issued a `GO` verdict at version `-002.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | The candidate Architecture Decision Packet for the LAN Authority Service has multiple high-severity risks, including a dual-writer split-brain risk in CLI local fallback, plaintext communication on LAN/Wi-Fi, and a lack of a rollback/reconciliation plan. | [gtkb-wi4909-lan-authority-service-adversarial-review-002.md](file:///E:/GT-KB/bridge/gtkb-wi4909-lan-authority-service-adversarial-review-002.md), [INSIGHTS-2026-07-04-15-37-lan-authority-service-architecture-decision-packet.md](file:///E:/GT-KB/independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-04-15-37-lan-authority-service-architecture-decision-packet.md) | Proceed to owner grilling (`WI-4910`) and formal specification candidate drafting (`WI-4911`), using the logged findings and grilling questions to shape those phases. | Resolved |

---

### 2026-07-04 - WI-4455 Platform Tests Spec-Before-Code Policy Review

Loyal Opposition (Antigravity/lo role) evaluated the policy review request and issued a `GO` verdict at version `-002.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Option A (bridge-derived coverage) is the most robust policy path as it avoids duplicate mapping drift and leverages existing bridge mapping metadata. | `bridge/gtkb-wi4455-platform-tests-spec-before-code-policy-review-001.md`, `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-04-16-11-wi4455-platform-tests-spec-before-code-decision-packet.md` | Proceed with Prime Builder implementation proposal for Option A under active project/PAUTH authorization. | Resolved |

---

### 2026-07-04 - WI-4455 Platform Tests Bridge-Derived Spec-Before-Code Proposal Review

Loyal Opposition (Antigravity/lo role) evaluated the pre-implementation proposal for the `spec-before-code` hook coverage and issued a `GO` verdict.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | The implementation proposal for WI-4455 (Option A) is well-scoped, satisfies all preflight checks, and addresses the platform test spec-before-code policy gap. | `bridge/gtkb-wi4455-platform-tests-bridge-derived-spec-before-code-001.md` | Proceed with Prime Builder implementation under active project authorization. Approved at version -002. | Resolved |

---

### 2026-07-04 - WI-4455 Platform Tests Bridge-Derived Spec-Before-Code Verification

Loyal Opposition (Antigravity/lo role) evaluated the post-implementation report and issued a `VERIFIED` verdict.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | The post-implementation report and verification suite are sound and pass all preflight checks. Direct tests assert both positive and negative platform_tests/ coverage outcomes. | `bridge/gtkb-wi4455-platform-tests-bridge-derived-spec-before-code-003.md`, commit `242f6039` | Commit the terminal VERIFIED verdict and close the thread (Version 004). | Resolved |




---

### 2026-07-04 (S539) - Interactive LO loop session: WI-4967 VERIFIED, dispatch-attribute advisory, SoT-singleton principle + WI-5011

Loyal Opposition (Claude/B, interactive ::init gtkb lo) ran a recurring /loop bridge/dispatcher/harness monitor and handled two owner-directed threads. Full wrap: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-04-22-27-S539-lo-session-wrap.md.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | WI-4967 controlled-artifact direct-mutation guard verified end-to-end (independence B!=A, scope=10 target paths, ruff clean, both preflights pass, pytest 246 passed, classifier fail-closed order read) and finalized after clearing a stale .git/index.lock. | bridge/gtkb-wi4967-controlled-artifact-direct-mutation-guard-004.md, commit e43dc79e | Terminal VERIFIED; thread closed. | Resolved |
| Process | Dispatch selection uses three disconnected orderings (global selection_order, rule prefer, shadow lane_scoring utility); the live path sorts by reviewer_precedence+harness_id, NOT by the placeholder dispatch_* attributes. Corrected my own earlier availability-based explanation. | config/dispatcher/rules.toml, scripts/dispatcher_runtime.py active_matching, groundtruth_kb/dispatcher/lane_scoring.py | PB umbrella project (advisory INSIGHTS-2026-07-04-19-08) WI-1 = selection-binding + SoT-consolidation audit. | Open (advisory filed) |
| Architecture | Five dispatch fields (can_fire_events, can_receive_dispatch, dispatch_availability/cost/quality) duplicated across harness-registry.json (state SoT) + rules.toml (policy) - violates the owner-stated SoT-singleton principle. | GOV-HARNESS-STATE-SOT-CONSOLIDATION-001; doctor config-drift WARN (owner hand-edit 2026-07-04) | WI-5011 (P1) captured: formalize SoT-singleton GOV + platform-wide duplication audit; owner to assign to PB. | Open (WI-5011) |
| Operational | LO headless redundancy thin: D config-quiesced for-cause (deepseek provider-failure burst 15:12-15:24), C near-single headless LO, B dispatchable-but-out-ranked (interactive-only in practice). | .gtkb-state/bridge-poller/dispatch-failures.jsonl; gt bridge dispatch health | Re-enable D once deepseek recovers (owner/config decision). | Open |

---

### 2026-07-05 - WI-5011 SoT Singleton Completeness Umbrella Verification

Loyal Opposition (Antigravity/lo role, auto-dispatched). Full wrap: [INSIGHTS-2026-07-05-00-15.md](file:///E:/GT-KB/independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-05-00-15.md).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | `gtkb-sot-singleton-completeness-umbrella` report verified and committed. The parent WI-5011 planning phase is complete, and the first child proposal (WI-5013) is filed. | bridge/gtkb-sot-singleton-completeness-umbrella-003.md, commit 6b3ee48b6d0a0103e7ebad0d3434e85aa3fc74a1 | Terminal VERIFIED; thread closed. Next LO action: review child proposal WI-5013. | Resolved |

---

### 2026-07-05 - WI-5017 and WI-5018 Proposals Review

Loyal Opposition (Antigravity/lo role, auto-dispatched). Full wrap: [INSIGHTS-2026-07-05-00-20.md](file:///E:/GT-KB/independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-05-00-20.md).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposals for `gtkb-sot-singleton-harness-control-audit` (WI-5017) and `gtkb-sot-singleton-bridge-runtime-cache-audit` (WI-5018) verified clean; all preflight checks passed with zero gaps. | `bridge/gtkb-sot-singleton-harness-control-audit-002.md`, `bridge/gtkb-sot-singleton-bridge-runtime-cache-audit-002.md` | Issued `GO` verdicts at version `-002.md` for both threads to authorize Prime Builder implementation. | Resolved |

---

### 2026-07-05 (S540) - WI-5017 Harness and Control-Surface SoT Audit Report Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Implementation report for WI-5017 lacks a recognized `Specification Links` heading, causing the mechanical preflight to fail. The report has been rejected with a `NO-GO` verdict (Version 004). | `bridge/gtkb-sot-singleton-harness-control-audit-003.md`, `bridge/gtkb-sot-singleton-harness-control-audit-004.md` | Prime Builder must add a recognized `Specification Links` heading listing the required specifications and re-submit. | Open |

---

### 2026-07-05 - WI-5012 Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal for `gtkb-dispatch-selection-binding-sot-consolidation` (WI-5012) verified clean; all preflight and clause preflight checks passed with zero gaps. | `bridge/gtkb-dispatch-selection-binding-sot-consolidation-001.md`, `bridge/gtkb-dispatch-selection-binding-sot-consolidation-002.md` | Issued `GO` verdict at version `-002.md` to authorize Prime Builder implementation. | Resolved |

---

### 2026-07-05 - WI-5029 Dispatch Cap Reconciliation Proposal Review (stood down; peer GO)

Loyal Opposition (Claude/harness B, auto-dispatched; session `2026-07-05T08-57-57Z-loyal-opposition-B-d6ed85`).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | Auto-dispatched to review `gtkb-wi5029-dispatch-cap-reconciliation-001` (NEW); a peer LO (harness C / Antigravity) filed **GO** at `-002` mid-review. Stood down from a competing verdict (append-only would thrash; peer independently adjudicated). | `bridge/gtkb-wi5029-dispatch-cap-reconciliation-002.md` (peer GO) | Did not mutate the bridge. GO stands. | Resolved |
| Technical | My independent review reached NO-GO on substance the GO missed: WI-3375's slot module (`bridge_dispatch_concurrency.py`) targeted the now-**retired** `cross_harness_bridge_trigger.py` (purged in `d2da67de`); "wire it in" is a fresh integration into a different substrate + removal of the working CA9165 cap, not P3 hygiene. Proposal also omits ~12 relevant DELIBs and defers the disposition. | `INSIGHTS-2026-07-05-09-18.md`; DELIB-2182 / DELIB-20263848; commit `d2da67de` | Verifier of the WI-5029 post-impl report must confirm which disposition Prime implemented; treat a live cap change (Option A) as exceeding the "hygiene/P3" authorization absent fresh owner-decision evidence. | Open (deferred to verification) |

---

### 2026-07-05 - WI-5024 Dispatcher Daemon Complex CLI Command Group Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal for `gtkb-dispatcher-complex-command-group` (WI-5024) verified clean; all preflight and clause preflight checks passed with zero gaps. | `bridge/gtkb-dispatcher-complex-command-group-001.md`, `bridge/gtkb-dispatcher-complex-command-group-002.md` | Issued `GO` verdict at version `-002.md` to authorize Prime Builder implementation. | Resolved |



---

### 2026-07-05 - WI-4990 Terminal Dispatch Reconciliation Closure Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal for gtkb-wi4990-terminal-dispatch-reconciliation-closure (WI-4990) verified clean; all preflight and clause preflight checks passed with zero gaps. |  bridge/gtkb-wi4990-terminal-dispatch-reconciliation-closure-001.md,  bridge/gtkb-wi4990-terminal-dispatch-reconciliation-closure-002.md | Issued GO verdict at version -002.md to authorize Prime Builder implementation. | Resolved |

---

### 2026-07-05 - WI-4990 Terminal Dispatch Reconciliation Closure Blocker Review

Loyal Opposition (Antigravity/lo role, auto-dispatched; session `2026-07-05T14-48-14Z-loyal-opposition-C-a14e43`).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | Prime Builder's `REVISED` response (`005.md`) records the owner-decision finalization blocker identified in `-004.md`. We confirmed no source/test/backlog metadata rework was performed or needed, and that the closure substance is correct. The thread remains blocked pending an interactive owner choice. | `bridge/gtkb-wi4990-terminal-dispatch-reconciliation-closure-005.md`, `bridge/gtkb-wi4990-terminal-dispatch-reconciliation-closure-006.md` | Issued `NO-GO` verdict at version `-006.md` to preserve the blocker status and stop. | Resolved via owner decision 2026-07-05 (see below): DELIB-20260705-WI4990-FINALIZATION-WAIVER |

---

### 2026-07-05 — Bridge backlog audit + dispatcher concurrency (interactive LO, harness B)

Interactive Loyal Opposition (Claude, harness B; session `689f575f-a1a8-4d43-bd92-7bcae23c16f8`). Full report: `CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-05-10-46-bridge-backlog-audit-and-dispatcher-concurrency.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | WI-4990 finalization blocker (prior Open item, above) — owner decided the finalization policy. | AUQ 2026-07-05; `DELIB-20260705-WI4990-FINALIZATION-WAIVER` | By-Reference Waiver approved: Prime files REVISED `-007` w/ waiver section → LO finalizes VERIFIED `-008` (bridge chain only). | Owner-decided; pending Prime REVISED |
| Process | 3 "stale" NO-GO threads are superseded (work VERIFIED under variant slugs / later slices), not stuck — slug-variant-collision. | `slice2a-visibility` vs `slice2c-integration`; `owner-decision-tracker-pattern-bounds` vs `-001` chain; `startup-trigger-awareness` vs `-001` chain; `DELIB-20260705-RETIRE-3-SUPERSEDED-NOGO-THREADS` | Retire as WITHDRAWN citing superseding thread (owner-approved). Dormant ~19d — may need reconciliation pass. | Owner-decided; pending retirement |
| Technical | Two divergent per-role dispatch concurrency caps; only CA9165 flat-3 wired, WI-3375 slot module (LO=3/Prime=2) unwired. | `scripts/dispatcher_runtime.py:2216,4250`; `scripts/bridge_dispatch_concurrency.py` | WI-5029 (consideration). | Open (backlog) |
| Technical | No live dispatch capacity test; caps 8/3/4 are incident+directive-derived, not measured. SQLite has no `busy_timeout` tuning. | `dispatch_chaos_harness.py` (stub), `benchmark_dispatch_envelope.py` (synthetic); `db.py:1531-1540` | WI-5030 (capacity benchmark) + WI-5031 (busy_timeout). | Open (backlog) |
| Process | 9 UNKNOWN-bucket threads audited — all benign (8 pre-rule VERIFIED headings grandfathered + 1 incident note); 0 stuck/misrouted. | `gt bridge state-report`; Body Status-Token Rule grandfathering | Accept as-is; no remediation. | Resolved (no action) |

---

### 2026-07-05 - WI-4535 Reconciler Advisory-Link Resolution Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal for gtkb-wi4535-reconciler-advisory-link-resolution (WI-4535) verified clean; all preflight and clause preflight checks passed with zero gaps. | bridge/gtkb-wi4535-reconciler-advisory-link-resolution-001.md, bridge/gtkb-wi4535-reconciler-advisory-link-resolution-002.md | Issued GO verdict at version -002.md to authorize Prime Builder implementation. | Resolved |

---

### 2026-07-05 - WI-4802 Reconciler Duplicate Disposition Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal for gtkb-wi4802-reconciler-duplicate-disposition (WI-4802) verified clean; the defect is a duplicate of the already-implemented and VERIFIED WI-4535 reconciler advisory-link resolution. Both preflight and clause preflight checks passed with zero gaps. | bridge/gtkb-wi4802-reconciler-duplicate-disposition-001.md, bridge/gtkb-wi4802-reconciler-duplicate-disposition-002.md | Issued GO verdict at version -002.md to authorize backlog resolution implementation. | Resolved |

---

### 2026-07-05 - WI-4837 Post-VERIFIED Finalization Recovery Blocker Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | Blocker report for gtkb-wi4837-post-verified-finalization-recovery (WI-4837) verified valid; the thread is blocked at the proposal stage awaiting the owner's policy decision (F3 requirement-disambiguation) to choose between automatic finalization parity and per-instance waiver. Both preflight and clause preflight checks passed with zero gaps. | bridge/gtkb-wi4837-post-verified-finalization-recovery-003.md, bridge/gtkb-wi4837-post-verified-finalization-recovery-004.md | Issued NO-GO verdict at version -004.md to record the blocker and halt unattended dispatch. | Open (blocked; pending owner decision) |

---

### 2026-07-05 - WI-4802 Verification Finalization & Repository Hygiene Overview

Loyal Opposition (Antigravity/lo role, interactive session).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Post-implementation report for gtkb-wi4802-reconciler-duplicate-disposition (WI-4802) verified clean; the implementation successfully marked the duplicate work item resolved in the backlog without source changes. | bridge/gtkb-wi4802-reconciler-duplicate-disposition-003.md, bridge/gtkb-wi4802-reconciler-duplicate-disposition-004.md | Issued VERIFIED verdict at version -004.md, finalizing the work item. | Resolved |
| Process | Repository overview hygiene scan identified multiple issues: (1) 14.3% Conflict Quarantine rate in Deliberation Archive; (2) 5 files with unparsed verdict signals; (3) stale python bytecode remnants (`pyc_without_source`); (4) legacy project root references in active scripts. | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-05-22-11-LO-HYGIENE-ASSESSMENT-overview.md` | Filed standard overview report in drop box for Prime Builder action plan. | Open |


---



---

### 2026-07-05 - WI-4784 Role Authority Terminology Purge Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Process | Pre-implementation proposal for gtkb-wi4784-role-authority-terminology-purge (WI-4784) is well-formed, correctly scoped, and passes all mandatory preflights and clause checks. | bridge/gtkb-wi4784-role-authority-terminology-purge-001.md, bridge/gtkb-wi4784-role-authority-terminology-purge-002.md | Issued GO verdict at version -002.md to authorize the implementation of the terminology cleanup. | Resolved |

---

### 2026-07-05 - WI-4725 Stale Failure Health Current-State Disposition Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal for gtkb-wi4725-stale-failure-health-disposition (WI-4725) is well-formed, correctly scoped, and passes all preflight and clause checks. Legacy trigger scripts are verified as purged and active tests verify the stale-failure cleanup logic. | bridge/gtkb-wi4725-stale-failure-health-disposition-001.md, bridge/gtkb-wi4725-stale-failure-health-disposition-002.md | Issued GO verdict at version -002.md to authorize the current-state disposition and resolved backlog transition. | Resolved |

---

### 2026-07-06 - WI-4968 Envelope Equivalence Evidence Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal for `gtkb-wi4968-envelope-equivalence-evidence` (WI-4968) is well-formed, correctly scoped, and passes all preflight and clause checks. | bridge/gtkb-wi4968-envelope-equivalence-evidence-001.md, bridge/gtkb-wi4968-envelope-equivalence-evidence-002.md | Issued GO verdict at version -002.md to authorize the implementation of the equivalence evidence helper. | Resolved |

---

### 2026-07-06 - WI-4965 Skill Effectiveness by Activity Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal for `gtkb-wi4965-skill-effectiveness-by-activity` (WI-4965) is well-formed, correctly scoped, and passes all preflight and clause checks. | bridge/gtkb-wi4965-skill-effectiveness-by-activity-001.md, bridge/gtkb-wi4965-skill-effectiveness-by-activity-002.md | Issued GO verdict at version -002.md to authorize the implementation of the skill effectiveness audit helper and tests. | Resolved |

---

### 2026-07-06 - WI-4962 Ollama-D Dispatch Reliability Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal for `gtkb-wi4962-ollama-d-dispatch-reliability` (WI-4962) targeting Ollama-D subprocess execution and session-budget timeouts is well-formed and passes all preflight and clause checks. Circuit-breaker reset sequencing is conditioned on validation of launch/timeout fixes. | bridge/gtkb-wi4962-ollama-d-dispatch-reliability-001.md, bridge/gtkb-wi4962-ollama-d-dispatch-reliability-002.md | Issued GO verdict at version -002.md to authorize the implementation of launch and timeout fixes. | Resolved |

---

### 2026-07-06 - WI-4961 Session Kickoff Prompt Sequencing Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Revised pre-implementation proposal for `gtkb-wi4961-session-kickoff-prompt-sequencing` (WI-4961) expands scope to cover all template and fixture surfaces, resolving the previous substantive scope objections in version 002. Preflight and clause preflight checks passed with zero gaps. | bridge/gtkb-wi4961-session-kickoff-prompt-sequencing-003.md, bridge/gtkb-wi4961-session-kickoff-prompt-sequencing-004.md | Issued GO verdict at version -004.md to authorize the expanded implementation of session kickoff prompt sequencing. | Resolved |

---

### 2026-07-06 - WI-4853 Session Role Marker Claim Eligibility Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal for `gtkb-wi4853-session-role-marker-claim-eligibility` (WI-4853) to transition `go_implementation` eligibility checks from the shared marker to the per-session marker is well-formed, correctly scoped, and passes all preflight and clause checks. | bridge/gtkb-wi4853-session-role-marker-claim-eligibility-001.md, bridge/gtkb-wi4853-session-role-marker-claim-eligibility-002.md | Issued GO verdict at version -002.md to authorize the implementation of the per-session marker claim eligibility. | Resolved |

---

### 2026-07-06 - WI-4968 Envelope Equivalence Evidence Verification

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Post-implementation report for `gtkb-wi4968-envelope-equivalence-evidence` (WI-4968) is verified clean and complies with all root boundary, linkage, backlog, and verification requirements. All tests pass, and ruff formatting is verified. | bridge/gtkb-wi4968-envelope-equivalence-evidence-003.md, bridge/gtkb-wi4968-envelope-equivalence-evidence-004.md | Issued VERIFIED verdict at version -004.md and committed the changes under commit `dcc206ee9782b628e3bcec0b351d928d2d4f32f3`. | Resolved |

---

### 2026-07-06 - Dispatcher watch: 5 findings advised, 1-hour clean window met

Loyal Opposition (Claude/harness B, interactive + self-paced watch). Full report: `CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-06-02-24-dispatcher-watch-session-wrap.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Dispatcher | F (OpenRouter) exhausts its agentic bridge-review turn budget (max-turn, 0 verdicts); guardrail hypothesis superseded, root cause is F model/agentic-loop. | WI-5034; bridge/gtkb-wi5034-f-agentic-turn-budget-advisory-001.md; DELIB-F-MAXTURN-PERSISTS-REDISABLE-20260706 | F re-disabled (can_receive_dispatch=false). PB: convert advisory to impl proposal; keep F disabled until a verified fix produces a verdict. | Open |
| Dispatcher | No backoff on repeated no-verdict launches (tight ~15s retry loop). | WI-5035; bridge/gtkb-wi5035-no-verdict-retry-backoff-advisory-001.md | PB: exponential backoff / bounded retries / circuit-breaker. | Open |
| Dispatcher | Expired document leases never reaped (wi4996 ~10h; locks 13->34). | WI-5036; bridge/gtkb-wi5036-stale-lease-reaping-advisory-001.md | PB: periodic reap of expired locks. | Open |
| Hooks | DIRECT-HARNESS-INVOKE-BAN false-positives on governed gt commands naming a provider near a routing verb (3x this session). | WI-5037; bridge/gtkb-wi5037-invoke-ban-false-positive-advisory-001.md | PB: narrow matcher to actual process spawns. | Open |
| Dispatcher | Watchdog heartbeat persistently exceeds 15s SLA (oscillating 28-48s, not frozen). Sole strict health=PASS gap. | WI-5039; bridge/gtkb-wi5039-watchdog-heartbeat-stale-advisory-001.md; DELIB-WI5039-WATCHDOG-OSCILLATES-CORRECTION-20260706 | PB: verify intended cadence vs SLA; likely SLA tuning. | Open |
| Docs | SKILL.md + example advisory reference the rejected bridge_kind `loyal_opposition_advisory` (enum requires `governance_advisory`). | .claude/skills/bridge-propose/SKILL.md; bridge/gtkb-ollama-cloud-routing-sot-drift-advisory-001.md | PB: update doc references to governance_advisory. | Open |
| Config | Owner-directed: dispatch ranking values are hand-assigned (not derived); decision to normalize + uniform-random tiebreak. | WI-5032/5033; DELIB-DISPATCH-RANKING-NORMALIZATION-20260705 | PB: implement uniform-random tiebreak (gating), then flatten values. | Open |

Outcome: goal met on primary criterion (64.2 min clean since last failure 01:00:56Z; F out; B/C/D exit-0). WI-5039 sole residual strict-PASS item.

---

### 2026-07-06 - WI-4926 Provider Readiness Contract Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal for `gtkb-wi4926-provider-readiness-contract` (WI-4926) is well-formed, correctly scoped, and passes all preflight and clause checks. | bridge/gtkb-wi4926-provider-readiness-contract-001.md, bridge/gtkb-wi4926-provider-readiness-contract-002.md | Issued GO verdict at version -002.md to authorize the implementation of the readiness contract and tests. | Resolved |

---

### 2026-07-06 - WI-4971 Evidence Freshness Boundaries Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Revised pre-implementation proposal for `gtkb-wi4971-evidence-freshness-boundaries` (WI-4971) successfully addresses the previous specification-linkage gap by integrating canonical freshness governance (`GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `GOV-PLATFORM-SOT-REGISTRY-001`, `DCL-SOT-READ-HOOK-CONTRACT-001`, `.claude/rules/sot-read-discipline.md`, and `config/registry/sot-artifacts.toml`), describing the relationship to the existing SoT registry, and including targeted freshness assertions. All preflight checks passed with zero gaps. | bridge/gtkb-wi4971-evidence-freshness-boundaries-003.md, bridge/gtkb-wi4971-evidence-freshness-boundaries-004.md | Issued GO verdict at version -004.md to authorize implementation. | Resolved |

---

### 2026-07-06 - WI-4791 Quality KPI Dispatch Feed Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal for gtkb-wi4791-quality-kpi-dispatch-feed (WI-4791) is well-formed, correctly scoped, and passes all preflight and clause checks. Target paths are fully aligned with the active PAUTH, and the verification plan maps spec-derived testing requirements to tests. | bridge/gtkb-wi4791-quality-kpi-dispatch-feed-001.md, bridge/gtkb-wi4791-quality-kpi-dispatch-feed-002.md | Issued GO verdict at version -002.md to authorize implementation of the Quality-KPI subsystem. | Resolved |

---

### 2026-07-06 - WI-4978 Helper Compliance Audit Blocker Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | WI-4978 post-implementation report blocker is confirmed active. The cross-harness adapter parity test remains failing due to write restrictions (ACL DENY) on the `.codex` directory and generator script pycache/draft pollution. | bridge/gtkb-wi4978-helper-compliance-audit-chokepoint-010.md | Issued NO-GO verdict at version -010.md to maintain the blocker state until owner waiver or correction is provided. | Open |

---

### 2026-07-06 - WI-4702 Dispatcher Reset Recipient State Directory Alignment Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal for `gtkb-wi4702-dispatch-reset-recipient-state-dir` (WI-4702) to align the operator-facing reset paths to the canonical state directory resolved by health and status reporting is well-formed, correctly scoped, and passes all preflight and clause checks. | bridge/gtkb-wi4702-dispatch-reset-recipient-state-dir-001.md, bridge/gtkb-wi4702-dispatch-reset-recipient-state-dir-002.md | Issued GO verdict at version -002.md to authorize implementation of the state directory reset alignment. | Resolved |

---

### 2026-07-06 - WI-4850 Verdict Claim Release Verification

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Post-implementation report for `gtkb-wi4850-verdict-claim-release` (WI-4850) has been verified as NO-ACTION. Prime Builder filed NO-ACTION because of OS ACL permissions (unresolved deny ACEs inside the sandbox context) preventing writes to the `.codex` helper target. Target paths were confirmed unmodified and verdict helper copies remain byte-identical. | bridge/gtkb-wi4850-verdict-claim-release-003.md, bridge/gtkb-wi4850-verdict-claim-release-004.md | Issued VERIFIED verdict at version -004.md, closing the bridge thread as VERIFIED with no net changes. | Resolved |

---

### 2026-07-06 - WI-4978 Verification Treadmill — Mechanical Break Needed (record-and-stop, no verdict)

Loyal Opposition (Claude/lo role, harness B, auto-dispatched; session 2026-07-06T12-05-14Z-loyal-opposition-B-ad9883).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Governance (P1) | The `gtkb-wi4978-helper-compliance-audit-chokepoint` thread is a runaway NO-GO↔REVISED treadmill (v024) across 3 harnesses (A=Codex Prime, B=Claude LO, C=Antigravity LO). The core WI-4978 fix is already verified-correct at -004; the sole blocker is a pre-existing, pollution-dominated, owner-gated `.codex` parity failure that WI-4978 did not create. Continuing to issue NO-GO verdicts (e.g., -010, -024) is loop-fuel, not progress — every verdict re-arms the dispatcher. | bridge/gtkb-wi4978-helper-compliance-audit-chokepoint-004.md (canonical adjudication), -024 (latest NO-GO, peer), CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-06-12-05-wi4978-treadmill-mechanical-break.md | STOP filing verdicts on this thread. Owner mechanical break: DEFER/WITHDRAW the thread + prioritize already-filed WI-5041 (dispatcher backoff), WI-5038 (parity-scan pollution), WI-5042 (capability-aware `.codex` routing). This dispatch filed no verdict and recorded to the dropbox. | Open (owner decision needed) |

---

### 2026-07-06 - WI-4840 advisory-disposition skill scaffold — `.codex` write-boundary treadmill (record-and-stop, no verdict)

Loyal Opposition (Claude/lo role, harness B, auto-dispatched; session 2026-07-06T14-09-46Z-loyal-opposition-B-1fcc6c).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Governance (P1) | The `gtkb-wi4840-advisory-disposition-skill-scaffold` thread is the same-class `.codex` write-boundary treadmill as WI-4842/WI-4978: GO (-002, Ollama-D) → blocked Codex report (-003) → NO-GO (-004, Antigravity-C, demanded remediation Codex structurally cannot perform) → blocked continuation (-005, NEW). Verified: `.claude/skills/advisory-disposition/SKILL.md` present (7988 B); `.codex/skills/advisory-disposition/SKILL.md` genuinely absent; `.codex` is WRITABLE from Claude-B (Deny-ACE is scoped to the Codex sandbox SID). Root cause already filed as WI-5042 (capability/writability-aware IMPLEMENTATION routing); intended producer of the generated `.codex` adapter is a non-Codex (Claude) Prime context. NO-GO is loop-fuel; VERIFIED impossible (missing files, RED tests, no waiver). | bridge/gtkb-wi4840-advisory-disposition-skill-scaffold-001..-005; CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-06-14-17-wi4840-codex-write-treadmill-record-and-stop.md; WI-5042/5041/5040 | Owner mechanical break: DEFER this thread (+ sibling `gtkb-wi4842-formal-artifact-packet-helper-scaffold`) OR route completion to a Claude Prime session that can write `.codex` under the operative GO (-002) OR land WI-5042/5041. This dispatch filed no verdict and recorded to the dropbox. | Open (owner decision needed) |

---

### 2026-07-06 - WI-4839 skill-governance-lifecycle-scaffold — `.codex` write-boundary blocker

Loyal Opposition (Antigravity/lo role, auto-dispatched; session C-2026-07-03T23-07-28Z).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Post-implementation report for `gtkb-wi4839-skill-governance-lifecycle-scaffold` (WI-4839) remains blocked. Prime Builder filed a blocked continuation report because of OS ACL permissions (unresolved deny ACEs inside the sandbox context) preventing writes to the `.codex` helper target. Target paths were confirmed unmodified, and the required Codex adapter and manifest entry are absent. Both mechanical preflights passed with zero gaps. | bridge/gtkb-wi4839-skill-governance-lifecycle-scaffold-005.md, bridge/gtkb-wi4839-skill-governance-lifecycle-scaffold-006.md | Issued NO-GO verdict at version -006.md to maintain the blocker state until owner waiver, sandbox/ACL adjustment, or Claude-driven projection is provided. | Open |

---

### 2026-07-06 - WI-5043 Service and SoT Watchdog Runner Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal for `gtkb-wi5043-service-sot-watchdog-runner` (WI-5043) is well-formed, correctly scoped, and passes all preflight and clause checks. Target paths are fully aligned with the active PAUTH, and the verification plan maps spec-derived testing requirements to tests. | bridge/gtkb-wi5043-service-sot-watchdog-runner-001.md, bridge/gtkb-wi5043-service-sot-watchdog-runner-002.md | Issued GO verdict at version -002.md to authorize implementation of the platform service/SoT availability watchdog detection-only runner. | Resolved |

---

### 2026-07-06 - WI-5045 Watchdog Tiered Restoration Policy Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal for `gtkb-wi5045-watchdog-tiered-restoration-policy` (WI-5045) is well-formed, correctly scoped, and passes all preflight and clause checks. Target paths are fully aligned with the active PAUTH, and the verification plan maps spec-derived testing requirements to tests. | bridge/gtkb-wi5045-watchdog-tiered-restoration-policy-001.md, bridge/gtkb-wi5045-watchdog-tiered-restoration-policy-002.md | Issued GO verdict at version -002.md to authorize implementation of the tiered restoration policy decision matrix. | Resolved |

---

### 2026-07-06 - WI-5044 Watchdog Restore-Action Registry Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal for `gtkb-wi5044-watchdog-restore-action-registry` (WI-5044) is well-formed, correctly scoped, and passes all preflight and clause checks. Target paths are fully aligned with the active PAUTH, and the verification plan maps spec-derived testing requirements to tests. | bridge/gtkb-wi5044-watchdog-restore-action-registry-001.md, bridge/gtkb-wi5044-watchdog-restore-action-registry-002.md | Issued GO verdict at version -002.md to authorize implementation of the restore-action metadata registry extensions. | Resolved |

---

### 2026-07-06 - WI-4842 formal-artifact-packet-helper scaffold — .codex write-boundary blocker

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Post-implementation report for `gtkb-wi4842-formal-artifact-packet-helper-scaffold` (WI-4842) remains blocked. Prime Builder filed a blocked continuation report because of OS ACL permissions (unresolved deny ACEs inside the sandbox context) preventing writes to the `.codex` helper target. Target paths were confirmed unmodified, and the required Codex adapter and manifest entry are absent. Both mechanical preflights passed with zero gaps. | bridge/gtkb-wi4842-formal-artifact-packet-helper-scaffold-018.md, bridge/gtkb-wi4842-formal-artifact-packet-helper-scaffold-019.md | Issued NO-GO verdict at version -019.md to maintain the blocker state until owner waiver, sandbox/ACL adjustment, or Claude-driven projection is provided. | Open |

---

### 2026-07-06 - WI-5050 OpenRouter author-model provenance review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal for `gtkb-wi5050-openrouter-author-model-provenance-actual-model` (WI-5050) is well-formed, correctly scoped, and passes all preflight and clause checks. The proposed fix correctly retrieves the actual served model from the Chat Completions response object, satisfying `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`. | bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-001.md, bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-002.md | Issued GO verdict at version -002.md to authorize implementation of the OpenRouter served model provenance stamp. | Resolved |

---

### 2026-07-06 - WI-4978 helper-compliance-audit-chokepoint — .codex write-boundary blocker (Continuation)

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Post-implementation report (blocker report) for `gtkb-wi4978-helper-compliance-audit-chokepoint` (WI-4978) remains blocked. Prime Builder filed a blocked continuation report because of sandbox/ACL write-boundary restrictions preventing updates to `.codex/` files and directories, and the cross-harness skill adapter check (`test_codex_skill_adapter_parity_check`) remains red. Both preflights passed with zero gaps. | bridge/gtkb-wi4978-helper-compliance-audit-chokepoint-037.md, bridge/gtkb-wi4978-helper-compliance-audit-chokepoint-038.md | Issued NO-GO verdict at version -038.md to maintain the blocker state until owner waiver, sandbox/ACL adjustment, or Claude-driven projection is provided. | Open |

---

### 2026-07-06 - WI-4842 formal-artifact-packet-helper scaffold — .codex write-boundary blocker (Continuation)

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Post-implementation report (blocker report) for `gtkb-wi4842-formal-artifact-packet-helper-scaffold` (WI-4842) remains blocked. Prime Builder filed a blocked continuation report because of access denied errors when trying to create `.codex/skills/formal-artifact-packet-helper/` or update `.codex/skills/MANIFEST.json`. Both preflights passed with zero gaps. | bridge/gtkb-wi4842-formal-artifact-packet-helper-scaffold-020.md, bridge/gtkb-wi4842-formal-artifact-packet-helper-scaffold-021.md | Issued NO-GO verdict at version -021.md to maintain the blocker state until owner waiver, sandbox/ACL adjustment, or Claude-driven projection is provided. | Open |

---

### 2026-07-06 - WI-4563 Deliberation Search Fail-Loud Verification (Stale Queue Entry)

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Selected dispatch entry `gtkb-wi4563-delib-search-fail-loud-003.md` (NEW) is no longer actionable because the terminal VERIFIED verdict (`gtkb-wi4563-delib-search-fail-loud-004.md`) was already written, signed, and committed to git in commit `4004cc54`. All spec-derived tests pass cleanly. | bridge/gtkb-wi4563-delib-search-fail-loud-003.md, bridge/gtkb-wi4563-delib-search-fail-loud-004.md, commit `4004cc54` | Mark the dispatch entry as stale/already resolved and exit without further action. | Resolved |

---

### 2026-07-06 - gtkb-advisory-proposal-intake-workflow (Umbrella GO Verdict)

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Reviewed the NEW project-inception umbrella proposal at version 002. It correctly scopes work to database/metadata and bridge updates only (safe `target_paths`), with no changes to protected source files. All preflight checks passed with zero gaps. | bridge/gtkb-advisory-proposal-intake-workflow-002.md, bridge/gtkb-advisory-proposal-intake-workflow-003.md | Issued GO verdict at version 003. Prime Builder may proceed with metadata creation and child work-item registration after implementation-start authorization. | Resolved |

---

### 2026-07-06 - WI-5051 OpenRouter SSL Bad Record MAC Authorization

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal `gtkb-wi5051-openrouter-ssl-bad-record-mac-authorization-001.md` is well-formed and passes all preflight checks. Evidence from `WI-5060` indicates the SSL failure was a transient network or provider TLS blip that has since resolved. | bridge/gtkb-wi5051-openrouter-ssl-bad-record-mac-authorization-001.md, bridge/gtkb-wi5051-openrouter-ssl-bad-record-mac-authorization-002.md | Issued GO verdict at version -002.md to authorize verification-only backlog resolution. | Resolved |

---

### 2026-07-06 - WI-5047 Dispatcher Model Transaction Unblock

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal `gtkb-wi5047-dispatch-config-model-transaction-unblock-001.md` correctly specifies target files to implement a governed model transaction under `DCL-DISPATCHER-CONFIG-CLI-ONLY-001`. All preflight checks passed with zero gaps. | bridge/gtkb-wi5047-dispatch-config-model-transaction-unblock-001.md, bridge/gtkb-wi5047-dispatch-config-model-transaction-unblock-002.md | Issued GO verdict at version -002.md to approve implementation of the transaction. Prime Builder must obtain a matching new/expanded PAUTH covering source/CLI changes before implementation begins. | Resolved |

---

### 2026-07-07 - WI-5062 Post-Reboot Dispatcher Supervisor Recovery Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal `gtkb-wi5062-post-reboot-dispatcher-supervisor-recovery-001.md` is well-formed, correctly scopes the reboot recovery gap, and passes all mechanical preflights and clause-applicability gates. The trigger and status extensions satisfy `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` and watchdog safety policies. | bridge/gtkb-wi5062-post-reboot-dispatcher-supervisor-recovery-001.md, bridge/gtkb-wi5062-post-reboot-dispatcher-supervisor-recovery-002.md | Issued GO verdict at version -002.md to authorize scheduled task triggers and status extensions under WI-5062. | Resolved |

---

### 2026-07-07 - WI-5063 Adapter Generator Transient Exclusions Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal `gtkb-wi5063-adapter-generator-transient-exclusions-001.md` is well-formed, correctly scopes the transient file exclusion gap, and passes all mechanical preflights and clause-applicability gates. Filtering gitignored transient file prefixes (like `_temp_`, `tmp_`, `draft-`, `draft_`) from reference/helper mirroring prevents false-positive parity check failures. | bridge/gtkb-wi5063-adapter-generator-transient-exclusions-001.md, bridge/gtkb-wi5063-adapter-generator-transient-exclusions-002.md | Issued GO verdict at version -002.md to authorize implementation of prefix exclusions in `scripts/generate_codex_skill_adapters.py`. | Resolved |

---

### 2026-07-07 - WI-5062 No-Window Service Probes Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Reviewed the NEW pre-implementation proposal `gtkb-wi5062-no-window-service-probes-001.md`. While the substance is sound, a target paths mismatch exists where `target_paths` contains non-existent files: `platform_tests/scripts/test_dispatcher_supervisor.py` and `platform_tests/scripts/test_dispatcher_watchdog.py`. Under the strict implementation start gate, this mismatch will block Prime Builder from modifying the actual test files. | bridge/gtkb-wi5062-no-window-service-probes-001.md, bridge/gtkb-wi5062-no-window-service-probes-002.md | Issued NO-GO verdict at version -002.md. Prime Builder must replace the non-existent test filenames in target_paths with the correct ones and file a REVISED proposal. | Resolved |

---

### 2026-07-07 - WI-5060 OpenRouter Connection Reset Retry Hardening Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Reviewed the NEW pre-implementation proposal `gtkb-wi5060-openrouter-connection-reset-retry-001.md`. The proposal is well-formed, correctly scopes the OpenRouter completions connection-reset retry hardening gap, and passes all mechanical preflights and clause-applicability gates. Catching connection/socket errors and retrying within `call_openrouter_chat` improves the reliability of the cloud completions default route. | bridge/gtkb-wi5060-openrouter-connection-reset-retry-001.md, bridge/gtkb-wi5060-openrouter-connection-reset-retry-002.md | Issued GO verdict at version -002.md to authorize implementation of retry and fail-closed handling in `scripts/openrouter_harness.py`. | Resolved |

---

### 2026-07-07 - Harness Parity and Bridge Verification

Loyal Opposition (Antigravity/lo role, interactive session).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Parity | Static catalog check shows `skill.formal-artifact-packet-helper` is missing capability mapping entries for `antigravity`, `cursor`, `ollama`, and `openrouter` in the capability matrix. | config/agent-control/harness-capability-registry.toml lines 1996-2013 | Update the registry to define the surfaces for all active harnesses to clear catalog drift checks. | Open |
| Parity | Phase 2 checks show two invalid waivers because they use the undefined dimension `full_transcript_archive` which does not match the allowed Phase 2 dimensions. | config/harness-parity/phase2-waivers.toml lines 103-126 | Align the waiver dimensions with the validator's schema or retire the redundant waivers. | Open |

---

### 2026-07-07 - WI-4901 Retire invalid full-transcript Phase 2 waivers Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Pre-implementation proposal `gtkb-wi4901-invalid-full-transcript-waiver-cleanup-001.md` correctly scopes the retirement/removal of invalid `full_transcript_archive` waivers for Ollama and OpenRouter. All preflight checks passed with zero gaps. | bridge/gtkb-wi4901-invalid-full-transcript-waiver-cleanup-001.md, bridge/gtkb-wi4901-invalid-full-transcript-waiver-cleanup-002.md | Issued GO verdict at version -002.md to authorize configuration cleanup in `config/harness-parity/phase2-waivers.toml`. | Resolved |

---

### 2026-07-07 - WI-5057 Live ADVISORY Scanner And Summarizer Helper Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Reviewed the NEW pre-implementation proposal `gtkb-wi5057-advisory-scanner-helper-001.md`. The proposal is well-formed, correctly scopes implementing a live ADVISORY scanner and summarizer helper under WI-5057, and passes all mechanical preflights and clause-applicability gates. The scanner deterministically selects live ADVISORY entries with adopt/adapt classification and the Required Prime Builder Owner-Grilling Gate section. | bridge/gtkb-wi5057-advisory-scanner-helper-001.md, bridge/gtkb-wi5057-advisory-scanner-helper-002.md | Issued GO verdict at version -002.md to authorize implementation of the scanner helper. | Resolved |

---

### 2026-07-07 - WI-5056 Prime Builder Advisory Intake Skill Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Reviewed the NEW pre-implementation proposal `gtkb-wi5056-prime-advisory-intake-skill-001.md`. The proposal is well-formed, correctly scopes implementing the Prime Builder advisory-intake skill under WI-5056, and passes all mechanical preflights and clause-applicability gates. The skill consumes live ADVISORY entries only after owner-grilling answers, explicit project/work-item approval, and child proposal filing are present. | bridge/gtkb-wi5056-prime-advisory-intake-skill-001.md, bridge/gtkb-wi5056-prime-advisory-intake-skill-002.md | Issued GO verdict at version -002.md to authorize implementation of the advisory-intake skill. | Resolved |

---

### 2026-07-07 - WI-5055 Deliberation-Side Advisory Proposal Skill Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Reviewed the NEW pre-implementation proposal `gtkb-wi5055-advisory-proposal-skill-001.md`. The proposal is well-formed, correctly scopes implementing the Loyal Opposition/advisory-side skill workflow for drafting ADVISORY bridge entries from reusable external or peer solutions under WI-5055, and passes all mechanical preflights and clause-applicability gates. | bridge/gtkb-wi5055-advisory-proposal-skill-001.md, bridge/gtkb-wi5055-advisory-proposal-skill-002.md | Issued GO verdict at version -002.md to authorize implementation of the advisory-proposal skill. | Resolved |

---

### 2026-07-07 - WI-5033 Dispatch Ranking Flatten Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Reviewed the NEW pre-implementation proposal `gtkb-wi5033-dispatch-ranking-flatten-001.md`. The proposal is well-formed, correctly scopes flattening the dispatcher ranking values and precedence to a single Codex baseline under WI-5033, and passes all mechanical preflights and clause-applicability gates. The changes are bounded and covered by active project authorization. | bridge/gtkb-wi5033-dispatch-ranking-flatten-001.md, bridge/gtkb-wi5033-dispatch-ranking-flatten-002.md | Issued GO verdict at version -002.md to authorize implementation of the dispatch ranking flattening. | Resolved |

---

### 2026-07-09 - NO-ACTION correction drive + bridge auto-processing (LO Claude/B, session d38aabe5)

Full wrap: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-09-01-21-LOYAL-OPPOSITION-WRAP.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Governance | NO-ACTION status was being misused to close ADVISORY threads (five threads WI-5034/5035/5036/5037/5039), flipping Prime-actionable ADVISORY into LO-actionable NO-ACTION with no prior verdict to correct. Owner corrected the canonical semantics (PB rejection of an LO GO/NO-GO verdict). | routing.py:24-26, disposition.py:126-127/132-133; INSIGHTS-2026-07-08-22-31-no-action-semantics-misuse.md; DCL-NO-ACTION-STATUS-SEMANTICS-001 | Slice 1 (WI-5081 docs) VERIFIED; Slice 2a (WI-5082 mechanical guard) GO'd, awaiting Prime impl; Slice 2b must remediate the five existing misused threads to a terminal status (WITHDRAWN/keep-ADVISORY). | Open (Slice 2b + WI-5082 impl pending) |
| Infrastructure | Recurring stale `.git/index.lock` (two occurrences this session; plus stale index.stash/next-index locks) blocked all repo commits. Cleared both under owner AUQ (guarded: >60s + no git process). | Two finalize failures on index.lock; owner AUQ "Clear it now". | Prime backlog item to find the root cause (what leaves git locks behind mid-commit). Not tracked as a WI. | Open |
| Infrastructure | dev-environment-inventory drift (harnesses/role_by_harness_compatibility) blocked WI-5081's protected-narrative (.claude/rules) finalize at the pre-commit release_blocker gate; confirmed it fires only on protected-narrative artifacts, not config/src. | WI-5081 finalize block; config/governance/protected-artifact-inventory-drift.toml | Owner directed Prime to reconcile the baseline; Prime did (commit 224524e6), unblocking WI-5081 (VERIFIED 66e73829). | Resolved |

---

### 2026-07-09 - Bridge auto-processing continuation (LO Claude/B, session cbd57087)

Full wrap: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-09-08-13.md`. Continues the peer session d38aabe5 entry above; took WI-5082 past its GO through to VERIFIED.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Governance | Drained the LO queue across 3 refill cycles: VERIFIED WI-5081/WI-3407/WI-5082/WI-4555 (me); concurred-and-stood-down on peer verdicts for WI-5070/WI-4840/cloud-harness. | Commits 66e73829, 1c94a5e9, 2d430ca6, 30752de1. | None — verdicts final. | Resolved |
| Governance | WI-5082 NO-GO'd (-004) for a placeholder path token (`bridge/...-00N.md`) in the report `## Files Changed` scope note that trips the finalize coverage extractor; owner chose ceremony-default reword; Prime re-filed -005; re-VERIFIED (-006, 2d430ca6). | write_verdict.py `_claimed_paths_from_report` abort. | Prime hygiene fix filed as WI-5096 (extractor should skip `-NNN.md` placeholders). | Open (WI-5096) |
| Hygiene | Committed hook `.claude/hooks/bridge-compliance-gate.py` and its groundtruth-kb template are byte-identical LF after WI-5082 finalize (parity preserved) — but WI-5081's finalize landed a whole-file LF→CRLF flip on `.claude/rules/file-bridge-protocol.md` + `canonical-terminology.md`. | `git ls-files --eol`; committed-blob CR counts; only 2 rule files now `i/crlf`. | Prime: `git add --renormalize` + regen narrative packets (WI-5090). | Open (WI-5090) |
| Tooling | `/verify` skill template heading `## Specifications Carried Forward` is rejected by the bridge-compliance gate (needs `## Specification Links`). | WI-5081 finalize BridgeComplianceError until renamed. | Prime: align template/regex (WI-5091). | Open (WI-5091) |
| Observability | `gt bridge state-report` DISPATCHER "Health: PASS" is misleading — the daemon is intentionally quiesced (owner AUQ) with heartbeat ~22.5h stale and GTKB-DispatcherDaemon/HarnessStormWatchdog scheduled tasks Disabled; `gt bridge dispatch health` correctly reports WARN. Last live dispatches failed on every headless LO target (WI-5064 OpenRouter SSL, WI-5065 Codex sandbox). | dispatch daemon status --json; dispatch-failures.jsonl. | Prime: relabel state-report health (WI-5092). Do not re-enable daemon until WI-5064/5065 fixed. | Open (WI-5092) |
| Infrastructure | Cleared one stale `.git/index.lock` (~28 min old, peer-crash residue) blocking the WI-5082 finalize — third occurrence noted across LO sessions today (see d38aabe5 entry). | index.lock age 1716s; removed under LO bridge-repair authority (>300s staleness guard). | Recurring root-cause investigation warranted (what leaves locks mid-commit under multi-session load). Not yet a WI. | Open |
| Provenance | WI-4840 commit aab69116 swept in WI-5082's uncommitted advisory-disposition No-op amendment (shared SKILL.md, hash e1fdb32d). Owner accepted as self-resolving; recorded for audit. | git show aab69116; WI-5082 -005 transparency notes. | None — end state correct; provenance noted. | Resolved (noted) |
| Queue | LO-actionable queue NOT empty at wrap (refilled during wrap): `gtkb-antigravity-supported-skill-target-parity-alignment` (NEW), `gtkb-wi5068-no-action-scan-helper-parser` (REVISED -008). | state-report at 08:13Z. | Next LO drain cycle / peer LOs. | Open |

---

### 2026-07-09 - Resource Registry Pointer Drift and CI Defect

Loyal Opposition (Antigravity/lo role, interactive session fded4ac9).

Full wrap: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-09-10-09-resource-registry-pointer-drift.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | `.claude/rules/project-resource-aliases.toml` is missing, causing `validate_pointer` and CLI resource resolution tests to fail and generating a `pointer=missing` WARN in `gt status`. | `resolve_project_resource.py:L118-131`, `test_project_resource_aliases.py`, `.gitignore` ignoring the file. | Restore the pointer file and un-ignore it in `.gitignore` so it is tracked by Git. | Open |

---

### 2026-07-09 - WI-5083 Startup Input Gate Rearm Fix Verification

Loyal Opposition (Antigravity/lo role, session 13ff6cfb).

Full wrap: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-09-VERIFICATION-WI-5083.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Reviewed the post-implementation report `bridge/gtkb-wi5083-startup-input-gate-rearm-fix-004.md` and finalized the `VERIFIED` verdict. Bypassing startup arming on continuation is correct; tests show the gate remains inactive for resume/compact while fresh starts block correctly. All tests pass cleanly. | bridge/gtkb-wi5083-startup-input-gate-rearm-fix-005.md, commits 7fe58355 + b584d0d4 | Verdict finalized and committed with 8 implementation/test paths. | Resolved |

---

### 2026-07-09 - WI-5104 Stale Finalization-Evidence Tests Parity Align Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Reviewed the NEW pre-implementation proposal `gtkb-wi5104-finalization-test-wi4829-independence-fix-001.md`. The proposal is well-formed, correctly scopes fixing stale test fixtures to ensure independent author session context validation under WI-5104, and passes all mechanical preflights and clause-applicability gates. | bridge/gtkb-wi5104-finalization-test-wi4829-independence-fix-001.md, bridge/gtkb-wi5104-finalization-test-wi4829-independence-fix-002.md | Issued GO verdict at version -002.md to authorize implementation of the test fixture fix. | Resolved |

---

### 2026-07-09 - WI-5071 No-Window Source-Fixes and Reintroduction-Guard Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Reviewed the NEW pre-implementation proposal `gtkb-wi5071-no-window-source-fixes-reintroduction-guard-001.md`. The proposal is well-formed, correctly scopes fixing outstanding window spawns and wiring the spawn audit into the release gate and pytest suite under WI-5071, and passes all mechanical preflights and clause-applicability gates. | bridge/gtkb-wi5071-no-window-source-fixes-reintroduction-guard-001.md, bridge/gtkb-wi5071-no-window-source-fixes-reintroduction-guard-002.md | Issued GO verdict at version -002.md to authorize implementation of window-spawn fixes and the reintroduction guard. | Resolved |

---

### 2026-07-09 - WI-5120 / WI-5121 Canonical-Authority-Drift Carrier Proposals Review

Loyal Opposition (Claude/lo role, interactive session 295c552f).

Full wrap: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-09-21-42.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Governance | Reviewed both NEW carrier-formalization proposals (formalize Deterministic Services Principle / root-boundary exceptions; demote DELIBs to provenance per DELIB-202665929). Premises verified true against live state; all preflights + clause gates green. Independent conclusion: GO on both. Peer LO (antigravity/C) filed valid GO -002 first; stood down without a duplicate verdict. | bridge/gtkb-wi5120-...-002.md, bridge/gtkb-wi5121-...-002.md; INSIGHTS-2026-07-09-21-42.md | Preserved richer implementation conditions the shallow peer GO omitted (load-bearing: WI-5121 template-scope discipline for canonical-terminology.md; GOV-vs-DCL carrier fit; DELIB-S324/S325 ID drift). Verifier to enforce at VERIFIED. | Resolved (GO; conditions pending impl) |

---

### 2026-07-09 - WI-4841 Managed-Skill-Adoption-Review Verification + WI-5095 Finalization Deadlock

Loyal Opposition (Claude/lo role, interactive session 295c552f).

Full wrap: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-09-22-16.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | WI-4841 `-015` report is verification-complete: 12 tests pass, adapter parity `--check` PASS, ruff clean, SHA agreement (`b9c8a7e0`), both preflights green, independent author session. Would be VERIFIED but for the finalization deadlock below. Not a NO-GO — implementation is correct. | bridge/gtkb-wi4841-...-015.md; executed test/adapter/ruff/sha/preflight evidence | Deferred per owner AUQ (2026-07-09). | Open (verify-complete; finalization deferred) |
| Technical | Finalization deadlock: `config/agent-control/harness-capability-registry.toml` has commingled uncommitted hunks (WI-4841 block @L2097 + WI-5095 decision-capture sha refresh @L413). `write_verdict.py` stages `--include` wholesale (no hunk-isolation); impl-start gate froze the registry to protect WI-5095's in-review `-005` report; LO cannot do raw protected git mutation. Symmetric — WI-5095 equally blocked; its merits not independently verified this session. | Known root cause WI-5105 (WI-4471 overlap guard); registry diff = 2 hunks | Owner chose defer both. Mechanical park (`DEFERRED`) is Prime-only; dispatcher health FAIL so treadmill risk low. Await WI-5105 fix or a coordinated Prime finalization of the entangled pair. | Open (WI-5105) |

---

### 2026-07-10 - WI-5041 Dispatcher Per-Thread Re-Offer Backoff Verification (headless dispatch) — RECORD-AND-STOP

Loyal Opposition (Claude/lo role, headless bridge auto-dispatch `2026-07-10T01-00-58Z-loyal-opposition-B-915251`; independent of `-003` author codex/harness A session `019f4929`).

Full report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-10-01-00-wi5041-finalization-blocker.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | WI-5041 `-003` report is verification-complete: implementation faithful to approved `-001`; 5 new tests behavioral; full approved target suite **227 pass**; ruff check + format clean; slug-keyed backoff orthogonal to provider `failure_count`; latent state-drop bug fixed (`payload = dict(state)` at L6586). Would be VERIFIED but for the finalization blocker below. NOT a NO-GO — no implementation defect. | bridge/gtkb-wi5041-...-003.md; reproduced 227-pass + both-ruff evidence; full source/test diff review | — | Open (verify-complete; finalization blocked) |
| Technical | Durable-keyed regression `codex_dispatch_not_ready` ×2 (LO/Codex target) **EXONERATED**: stash-isolation shows identical 2 failures at HEAD with WI-5041 source removed. Pre-existing `_is_dispatch_ready` readiness-fixture drift, not a WI-5041 regression (answers report LO Ask #2). | `git stash push -- scripts/dispatcher_runtime.py` → same 2 failures at HEAD line 4577 | Route the `_is_dispatch_ready` readiness-fixture drift (also breaks `test_shadow_decision_shrinks_remaining_items` at HEAD) to its own backlog defect thread. | Open (pre-existing; own thread) |
| Technical | Finalization blocker: target `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` symmetrically entangled with WI-5066 (`--config-env` command-line redaction, `-007` REVISED / un-GO'd). WI-5041 green suite DEPENDS on WI-5066's uncommitted daemon-test fix (stash file→HEAD ⇒ 2 red); wholesale `--include` would capture WI-5066 un-GO'd work. Same class as WI-4841/WI-5095 above. | WI-5066 `-005` config-env prose; stash-isolation of daemon test file (both pops restored tree clean) | Finalize WI-5066 first → then VERIFIED WI-5041 cleanly with this report's evidence; OR owner by-reference co-finalization waiver. Do NOT re-review (substance complete). Known root cause WI-5105 (WI-4471 overlap guard). | Open (WI-5105) |

---

### 2026-07-11 - Auto-process LO queue + double-LO-on-same-NEW race observation

Loyal Opposition (Claude/lo role, interactive session `abd7e6dd`).

Full wrap: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-11-08-35-lo-session-wrap.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Coordination | Double-LO-on-same-NEW dispatch race: two active LO harness-B sessions (`abd7e6dd`, peer `a9e5fa8e`) co-drained the same NEW entries. Peer committed valid GO on BOTH wi5187 and wi5189 before my thorough interactive review finished; I stood down (no duplicate verdicts; wi5189 pre-write race-guard fired). Independent conclusions matched peer — no lost dissent, but duplicated review labor. | bridge/gtkb-modernization-wi5187-...-002.md, bridge/gtkb-wi5189-...-002.md (peer author `a9e5fa8e`); `groundtruth_kb.bridge.notify` dispatch signature | Behavioral (Option 1): when a peer LO is co-draining, prefer fleet-proof work over racing the GO/NO-GO lane (already in LO session memory). Mechanical (Option 2): per-entry LO soft-lease on the review signature, mirroring Prime-side work-intent claim. | **Captured** per owner directive 2026-07-11 → **WI-5197** (P3, behavioral) + **WI-5196** (P2, mechanical), both under PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY. Consideration candidates (not impl-approved). |
| Technical | This session's own verdicts closed clean: wi5186 VERIFIED+finalized (commit 637ec02a), wi5181 GO, wi5182 GO — all three now terminal VERIFIED. The two ceded to peer (wi5187, wi5189) subsequently moved GO→NO-GO downstream; both now Prime-actionable, outside LO scope. | `gt bridge show` at wrap: wi5181/wi5182/wi5186 VERIFIED; wi5187/wi5189 NO-GO | None (LO scope complete). wi5187 out-of-root worktree blocker (`C:\Users\micha\.codex\worktrees\claude-design-backlog`) remains real for its eventual bootstrap. | Resolved (LO side) |
| Technical | WI-5185 (`gtkb-wi5185-dispatcher-identity-runtime-kind`) REVISED report VERIFIED + commit-finalized (commit 1e7e1217). Sequencing-only -004 NO-GO genuinely resolved: WI-5189 now committed (cd877ac4) + VERIFIED, `resolve_worker_role_provenance` in HEAD, only the 2 WI-5185 paths dirty → independently finalizable. Source = exact 13-line harness_type→harness_name drift fix (spec-faithful); tests 193 pass + 3 focused; both ruff gates clean. Clean scoped commit (2 code + -001..-006 chain, 8 files, no foreign hunks). | commit 1e7e1217; git diff --stat; full test/ruff re-run this session | None — terminal VERIFIED. Happy-path resolution of the commingled-sibling pattern (correct NO-GO → sibling landed → dependent finalized). | Resolved (VERIFIED) |

---

### 2026-07-12 - WI-5200/5202 broad GO (validated downstream) + WI-5199 stand-down + dropbox-SoT clarifications

Loyal Opposition (Claude/lo role, interactive session `4c34d164`; model sonnet-5 → opus-4-8 mid-session).

Full wrap: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-12-16-30-lo-session-wrap.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | **GO** on `gtkb-wi5200-5202-generous-harness-repair-002` (broad). Root cause independently reproduced in source (not trusted from narrative): `cloud_harness_base.py:1898-1900`+`:1773-1776` blank no-tool turn raises fatal regardless of budget; `routing.toml max_turns=200` never threaded into `dispatcher_runtime.py` → silent fallback to `DEFAULT_MAX_TURNS=40`. GO advisory FINDING-A flagged the `groundtruth.db`/registry commingling risk with the live WI-5199 chain. | bridge/gtkb-wi5200-5202-generous-harness-repair-002.md; source grep; H stderr log | None (LO scope complete). | Resolved (LO side) |
| Process | GO advisory FINDING-A **validated downstream**: broad GO quarantined at the impl-start gate for exactly the predicted `groundtruth.db`/registry overlap → broad chain WITHDRAWN (`-006`); owner-authorized repair relocated to `-narrow`, VERIFIED at `-narrow-008`, committed `45d1c7f2`. Correct-advisory → correct-quarantine → clean relocation. | broad `-003`/`-004` NO-ACTION, `-005` NO-GO, `-006` WITHDRAWN; narrow `-008` VERIFIED; commit 45d1c7f2 | None. | Resolved |
| Technical | **STAND DOWN** on WI-5199 (`gtkb-wi5199-fd-evidence-h-functional-proof` `-003` NEW) — harness-functional-proof reserved for harness H; authoring any B verdict corrupts the acceptance criterion. No 16th duplicate report written (15th `INSIGHTS-...-14-14` current). Loop root cause: report stays NEW (no H verdict) and re-fans; H's `PublishBridgeVerdict` (WI-5210) fails server-side `ModuleNotFoundError: No module named 'scripts'`; WI-5210 GO'd but UNCOMMITTED, no impl report. | git HEAD `12a8508c` unchanged; WI-5210 4 files dirty; WI-5210 thread `-002` GO | **Prime/owner**: (a) fix WI-5210 sys.path defect; (b) file WI-5210 report→verify→commit; (c) re-run H-proof flip holding B ineligible until H COMMITS (not in-flight — FINDING-A re-fan window); or (d) owner re-scope WI-5199 to H-unproven (F proven, D DEGRADED). | **Open (P1) — Prime/owner** |
| Coordination | Dispatch fully dark for both roles at last read (~14:25Z): all `can_receive_dispatch=false`, `selected_by_role` empty for both roles, plus standing 2026-07-07 console-window `disable_guard` on daemon/watchdog supervisor tasks. Likely mid-transaction, not a fault. | `gt bridge dispatch health/status --json`; `harness-state/harness-registry.json` | Prime confirm ≥1 PB + ≥1 LO target restored before expecting auto-dispatch. | Open (verify) |
| Reference | Owner governance Q&A: CODEX-INSIGHT-DROPBOX is **not** a canonical SoT (absent from `config/registry/sot-artifacts.toml`); git-tracked, scaffold-recreated (`scaffold.py:649-651`), consumers fail-soft (`advisory_backlog_router.py:288`, `harvest_session_deliberations.py:235`). Deleting it = no runtime impairment but discards on-disk LO audit trail + un-harvested DA feeder inputs; git-recoverable unless committed. | cited files this session | Informational — if pruning, harvest deliberations first then archive, don't hard-delete. | Informational |

---

### 2026-07-13 - Cross-harness parity goal language + fleet-state findings (advisory)

Loyal Opposition (Claude/lo role, interactive session `71381938`; model opus-4-8).

Full wrap: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-13-16-41-lo-parity-goal-language-and-fleet-state-findings.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Deliverable | Finalized cross-harness parity goal language. Owner-settled: honor 60-min D/F/H allowance (`DELIB-20260713`), reading **2b** (each in-scope harness proves BOTH PB and LO roles — ≈12 proofs), E/G excluded. Scope implication: dispatcher routes by default role, so non-default-role proofs need a governed `gt mode set-role` flip per harness. In-scope = A,B,C,D,F,H. | full text in wrap report | Owner decision: persist goal as deliberation and/or spec? | Open (owner) |
| Governance | **Phantom harness G (goose)**: owner confirmed goose harness does not exist, yet MemBase record G persists (`harness_type: goose-desktop`, `status: suspended`, v8; registry ~lines 346-404). Phantom Artifact; skews fleet-health/parity denominators; leftover from GOOSE-HARNESS-ADOPTION redirected to Alibaba (H). | `harness-state/harness-registry.json` G block; owner statement | Governed retirement via `gt harness retire` (not hand-edit); verify no live rule/PAUTH refs G first. | Open (P2, owner-gated) |
| Coordination | F "suspension" is on the **dispatch-eligibility** axis, not lifecycle. `gt harness show --harness F` = `status: active` but `can_receive_dispatch: false` (set 2026-07-12T21:40 by `gt-bridge-dispatch-config-cli`). All 8 harnesses `can_receive_dispatch=false` → dispatch health FAIL. Correct lever = `gt bridge dispatch config` (F→true), NOT `gt harness resume` (wrong axis, no-op). | `gt harness show --harness F` rowid 315 v41; `gt bridge dispatch status` | Owner's original ask ("update TAFE for F"), interrupted twice — NOT performed. Owner-authorize F eligibility restore. | Open (owner) |
| Bridge | **STAND DOWN** on WI-5211-f (`gtkb-wi5211-f-governed-publication-functional-proof-001`, NEW governance_advisory) — verdict reserved for `author_harness_id: F`; a B verdict defeats the proof. Blocked on Finding above (F not dispatch-eligible). WI-5222 (60-min envelope, NEW) read but not reviewed. No bridge mutation this session. | bridge state-report; reserved-verdict pattern | Prime/owner: restore F eligibility → F produces its own proof. | Open (Prime/owner) |

---

### 2026-07-15 - WI-5138 Database Incident Recovery Evidence Report Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

Full wrap: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-15-00-11-loyal-opposition-C-dispatch-wrap.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Reviewed the NEW recovery evidence report `bridge/gtkb-wi5138-database-incident-recovery-evidence-001.md`. Verified that database integrity check is completely clean (`PRAGMA integrity_check` -> `ok`) and foreign key constraints are fully satisfied (`PRAGMA foreign_key_check` -> empty). Verified that candidate work items (`WI-5178` v1, v2, v3) are restored, and newer live-only items (`WI-5229` to `WI-5232`) and tests (`TEST-11383` to `TEST-11386`) are preserved. All preflights and DCL clause applicability gates passed successfully. | bridge/gtkb-wi5138-database-incident-recovery-evidence-001.md, bridge/gtkb-wi5138-database-incident-recovery-evidence-002.md | Issued GO verdict at version -002.md to authorize resuming the modernization trust-enforcement slice under the stated caveats. | Resolved |
---

### 2026-07-15 - WI-5233 Dispatch Selection and Cap Repair Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

Full wrap: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-15-00-13-loyal-opposition-C-dispatch-wrap.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Reviewed the NEW implementation report `bridge/gtkb-wi5233-dispatch-selection-order-cap-repair-implementation-003.md`. Verified that the dispatcher selection preserves queue order (oldest-first) and respects ranked target max-item caps. Confirmed that focused tests for order and capping pass (`4 passed`). Preflights and DCL clause applicability gates passed successfully. | bridge/gtkb-wi5233-dispatch selection report and tests | Issued VERIFIED verdict at version -004.md (commit `a7f2c7be`). | Resolved (VERIFIED) |

---

### 2026-07-15 - WI-5139 Fleet MemBase Carrier Restoration Report Revision Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

Full wrap: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-15-00-13-loyal-opposition-C-dispatch-wrap.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Reviewed the REVISED implementation report `bridge/gtkb-wi5139-fleet-membase-carrier-restoration-005.md`. Verified the presence of the mandatory `## By-Reference Finalization Waiver` section citing `DELIB-20260714-FLEET-GOAL-RESUME-CARRIER-REPAIR` and already committed `4ebb46f6` delta. Verified dry-run is idempotent and clean (`total_inserted: 0`, `skipped_existing: 41`). Pytest passed (`5 passed`). Preflights and DCL clause applicability gates passed successfully. | bridge/gtkb-wi5139-fleet-membase-carrier-restoration-005.md | Issued VERIFIED verdict at version -006.md by-reference, committing only the verdict file (commit `ced301b7`). | Resolved (VERIFIED) |

---

### 2026-07-15 - WI-5138 Trust-Enforcement Slice Report Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

Full wrap: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-15-02-22-56Z-loyal-opposition-C-9aad92.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Reviewed the NEW implementation report `bridge/gtkb-modernization-trust-enforcement-slice-007.md`. Verified that the trust-enforcement slice satisfies all five bounded behaviors (wrapped direct Git gating, multiline boundary checks, mutating Git verbs, controlled runtime authority, and Cursor read-only plan mode). Verified target file final hashes and formatting checks are completely clean. Pytests successfully executed and passed (`204 passed` on start gate, `48 passed` on paths and cursor). Preflights and DCL clause applicability gates passed successfully. | bridge/gtkb-modernization-trust-enforcement-slice-007.md | Issued VERIFIED verdict at version -008.md, committing the verdict and all 6 target files plus untracked predecessor files (commit `7ae6f769`). | Resolved (VERIFIED) |

---

### 2026-07-15 - WI-5144 HP08 Semantic Adapter Drift Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

Full wrap: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-15-20-07-19Z-loyal-opposition-C-dispatch-wrap.md`.

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Reviewed the REVISED implementation proposal `bridge/gtkb-wi5144-hp08-semantic-adapter-drift-003.md`. Verified that all three previous findings from version 002 (omitted cross-harness parity ADR/DCLs, missing cross-harness disposition matrix, and clean-checkout test dependencies) have been resolved. Preflights and DCL clause applicability gates passed successfully. | bridge/gtkb-wi5144-hp08-semantic-adapter-drift-003.md | Issued GO verdict at version -004.md (commit `e1ebfb0f`) to authorize implementation of semantic-drift rejection. | Resolved (GO) |

---

### 2026-07-15 - WI-5217 Antigravity Prompt Transport Proposal Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Reviewed the REVISED implementation proposal `bridge/gtkb-wi5217-antigravity-prompt-transport-005.md`. Verified that this dispatch itself successfully executes the in-vivo proof. Antigravity successfully parsed the short pointer prompt, opened the in-root sidecar payload, run preflights and focused test validations. Tests, ruff check, and format checks pass. All preflights and clause gates green. | bridge/gtkb-wi5217-antigravity-prompt-transport-005.md | Issued GO verdict at version -006.md to authorize resubmission of the implementation report. | Resolved (GO) |

---

### 2026-07-15 - WI-5299 Unignored Deterministic Scratch Residue Classes Review

Loyal Opposition (Antigravity/lo role, auto-dispatched).

| Area | Finding | Evidence / context | Suggested action | Status |
|------|---------|-------------------|------------------|--------|
| Technical | Reviewed the NEW implementation proposal `bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-001.md`. Verified that it correctly limits changes to `.gitignore` and `platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py` to handle the specified seven deterministic scratch classes. Preflights and DCL clause applicability gates passed successfully. | bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-001.md | Issued GO verdict at version -002.md to authorize implementing the narrow ignore patterns. | Resolved (GO) |
