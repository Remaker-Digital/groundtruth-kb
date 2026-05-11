# Active Work List

> **Backlog source-of-truth status (2026-05-06):** this file is now a
> compatibility/human-readable backlog view. The canonical backlog is MemBase
> `current_work_items` / append-only `work_items`; all 75 table and legacy
> active-section items in this file have been migrated or enriched there by `gt backlog migrate-work-list`.
> New backlog access should use `gt backlog list` or direct MemBase reads, not
> manual edits to this markdown table.

**Owner pre-approval:** Proceed through this list autonomously. For each item:
propose via bridge → wait for Codex GO → implement → post-impl report → wait for Codex VERIFIED → commit → drop from list.

Do not wait for owner approval between items. Continue unsupervised.

---

## TOP — Active workstreams

**S327 freeze + release-path framing lifted 2026-05-07 (S332):** `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` is fully superseded by `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING`. Backlog DB Slices 2-7, Term Primer Slices 2-5, and Resource Disambiguation Slices 2-5 may now advance. `GTKB-ARTIFACT-RECORDER-CLI` is no longer freeze-blocked. rc1 sequencing is open. Preserved release blockers: P0 secrets-purge override + `DELIB-S330` canonical Agent Red migration prerequisite + Slice 8.5/8.6 in-flight bridge work — these remain authoritative on rc1 tag authorization.

**P0 security override 2026-05-05:** `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` is the controlling incident workstream until current-file purge, generated-artifact redaction, and inspection-before-commit enforcement are in place. This override groups existing security scan, credential-pattern, release-gate, startup/settings credential-safety, and Agent Red credential-scan adoption work under one parent item without burying the incident inside CI cleanup or Agent Red migration. It temporarily outranks the isolation sequence below; resume the release path after the P0 containment gates are implemented and verified.

**Owner top-priority directive 2026-05-06:** `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001` is added as a top-priority governance item for Prime Builder pickup. Advisory report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/ADR-DCL-CLAUSE-TEST-ENFORCEMENT-ADVISORY-2026-05-06.md`. Intent: convert ADR/DCL use from citation-oriented linkage into clause-level applicability discovery and pass/fail review predicates for proposals and implementation verification. Prime Builder should file the normal bridge proposal for this item before lower-priority governance or release-hardening work; do not let it be buried as passive advisory context.

**Default idle work directive 2026-05-07 (S332, supersedes 2026-05-06 directive):** when Mike has not supplied a different session task, both Prime Builder and Loyal Opposition default to per-leverage prioritization driven by reliability + acceleration value, not freeze-derived sequencing. Loyal Opposition reviews/verifies the highest-priority `NEW`/`REVISED` bridge entry; Prime Builder revises `NO-GO` entries or implements `GO` entries. Recommended priority bands (top to bottom): (1) **P0 / preserved release blockers** — `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT`, `DELIB-S330` canonical Agent Red migration prerequisite, in-flight Slice 8.5/8.6 bridge work; (2) **Acceleration / deterministic-services** — `GTKB-ARTIFACT-RECORDER-CLI`, Backlog DB Slices 2-7 (DDL migration onward), `GTKB-OPS-CURRENT-STATE-MONITORING-001` follow-on, `GTKB-PRE-FILING-PREFLIGHT-HOOK`/`GTKB-PRE-FILING-PREFLIGHT-RULE` (NO-GO awaiting revision), Term Primer Slices 2-5, Resource Disambiguation Slices 2-5; (3) **Governance-loop tightening** — `GTKB-CODEX-BRIDGE-COMPLIANCE-GATE-PARITY` GO awaiting Prime move, `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT` Slice 2, `GTKB-AUQ-POLICY-GATES-001` awaiting VERIFIED, `GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY` (data hygiene); (4) **Reliability hardening** — platform CI coverage broadening, evaluation-module waiver retirement, pip-installed adopter UX, dashboard follow-on slices. Mike may elevate any item explicitly; this directive is non-prescriptive between bands.

**Documentation-quality remediation umbrella filed 2026-05-07 (S336):** Prime Builder filed `GTKB-DOCS-QUALITY-REMEDIATION` slice 0 (scoping only) at `bridge/gtkb-docs-quality-remediation-001.md`, NEW. The umbrella converts Loyal Opposition NO-GO findings F1–F8 in `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-07-06-39-GTKB-DOCUMENTATION-QUALITY-REVIEW.md` (root README repo-identity drift, red docs CI, broken beginner commands/API examples, version incoherence across 0.6.0/0.6.1/0.7.0rc1, retired-OS-poller-as-current bridge docs, hidden MkDocs nav entries, unsanitized internal reports under `docs/reports/`, missing markdownlint config) into seven implementation slices ordered per the LO recommended sequence (root README → docs CI → executable beginner docs → version coherence → bridge automation docs → nav/archival → markdownlint). Owner authorized via S336 AskUserQuestion answer "Full 8-finding remediation"; per-slice proposals each require their own Codex GO before implementation. Awaiting Loyal Opposition GO or NO-GO on slice-0 scoping.

**Release-plan progress 2026-05-06:** Prime Builder filed security Slice 2 proposal `NEW` at `bridge/gtkb-secrets-purge-and-commit-enforcement-slice2-ci-prepush-001.md`, covering broad CI scan coverage, tracked pre-push/range enforcement, redacted `--all-refs` inventory, candidate-high triage, and release-gate hardening; awaiting Loyal Opposition `GO` or `NO-GO`. Prime Builder filed Slice 8.6 `REVISED` at `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-009.md`, citing active `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` and passing applicability preflight with no missing specs; awaiting Loyal Opposition `VERIFIED` or `NO-GO`. Prime Builder filed Slice 8.5 `REVISED` at `bridge/gtkb-isolation-017-slice-8-5-ci-green-003.md`, using the same DELIB-scoped de facto CI evidence while keeping rc1 tag authorization blocked pending canonical migration. Prime Builder also revised `AGENT-RED-REPO-MIGRATION-001` at `bridge/agent-red-repo-migration-001-003.md` as read-only inventory only, with external repository mutation out of scope; awaiting Loyal Opposition `GO` or `NO-GO`.

**Security progress update 2026-05-06:** Slice 2 is now implemented and filed as `bridge/gtkb-secrets-purge-and-commit-enforcement-slice2-ci-prepush-003.md`. It adds broad redacted CI secret-scan workflow coverage, tracked pre-push range enforcement, `gt secrets scan --all-refs`, release-gate hardening, and focused tests. The redacted current tracked scan still reports 0 verified-provider findings; the all-local-refs scan reports 23 verified-provider-class historical findings, so Slice 3 planning is filed at `bridge/gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan-001.md`. Any destructive history rewrite remains blocked pending Loyal Opposition review and explicit owner approval.

**Slice 8.5 progress update 2026-05-06:** Slice 8.5 is now implemented and filed as `bridge/gtkb-isolation-017-slice-8-5-ci-green-005.md`; awaiting Loyal Opposition `VERIFIED` or `NO-GO`. `memory/release-readiness.md` B6 now records five successful de facto CI runs under `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`, and `v0.7.0-rc1` remains unauthorized pending canonical migration and canonical CI.

**Agent Red migration inventory update 2026-05-06:** Read-only inventory is implemented and filed as `bridge/agent-red-repo-migration-001-005.md`; awaiting Loyal Opposition `VERIFIED` or `NO-GO`. Inventory found canonical and de facto `develop` currently point to the same head (`84b2f8b0`), canonical `main` is 136 commits behind de facto `main`, and canonical CI is still not fully green because SonarCloud/Security Scan have canonical-repo configuration failures.

**Platform CI coverage update 2026-05-06:** Dedicated `groundtruth-kb/tests/` CI coverage is implemented. Loyal Opposition returned `NO-GO` at `bridge/gtkb-ci-coverage-for-platform-001-006.md` because the workflow's target lane was red on a strict-mypy `no-any-return` in `groundtruth-kb/src/groundtruth_kb/policy/engine.py`; Prime fixed that regression and filed `bridge/gtkb-ci-coverage-for-platform-001-007.md` with fresh local evidence (`2054 passed, 1 skipped`). New workflow `.github/workflows/groundtruth-kb-tests.yml` runs the GT-KB platform pytest lane on `groundtruth-kb/**` changes and manual dispatch. Existing `groundtruth-kb` format drift remains recorded as residual and was not bulk-formatted in this workflow-only item.

**Evaluation-module investigation update 2026-05-06:** Read-only investigation is implemented and filed as `bridge/gtkb-evaluation-module-restoration-001-005.md`; awaiting Loyal Opposition `VERIFIED` or `NO-GO`. Investigation found root `evaluation/` deletion at `c9fc7216` removed 10 files, current failure surface includes two unwaived `tests/evaluation/*` collection errors plus the two waived performance tests, and implementation remains blocked on owner path choice plus missing DELIB archive repair/supersession.

**Pip-installed adopter UX update 2026-05-06:** Minimal installed-wheel host-root fix is implemented and filed as `bridge/gtkb-pip-install-adopter-ux-001-005.md`; awaiting Loyal Opposition `VERIFIED` or `NO-GO`. Source checkouts keep strict `--gt-kb-root` equality; installed wheels accept explicit adopter host roots and default to cwd. Installed-wheel smokes passed for explicit `--gt-kb-root` and no-explicit-root cwd default command shapes.

**Slice 5.5 overlay refresh/disposability update 2026-05-06:** Chroma overlay regeneration is implemented and filed as `bridge/gtkb-isolation-017-slice-5-5-overlay-tests-005.md`; awaiting Loyal Opposition `VERIFIED` or `NO-GO`. New public API/CLI `groundtruth_kb.project.chroma.regenerate()` and `gt project chroma regenerate` rebuild `.groundtruth-chroma/` from `groundtruth.db`, enforce adopter/root boundaries, preserve dry-run and JSON planning surfaces, and expose explicit optional-dependency skip behavior.

**Operating-state monitoring update 2026-05-06:** Deterministic operating-state collector is implemented and filed as `bridge/gtkb-ops-current-state-monitoring-001-005.md`; awaiting Loyal Opposition `VERIFIED` or `NO-GO`. New `gt status` surface supports JSON/startup/component-filter output, dashboard refresh writes `operating_state_components` from the same collector, and startup rendering uses the same bounded collector payload without LLM/API calls.

**AUQ policy-gates update 2026-05-06:** Central deterministic AUQ policy-gate first slice is implemented. Loyal Opposition returned `NO-GO` at `bridge/gtkb-auq-policy-gates-001-006.md` because strict mypy found a `no-any-return` in `groundtruth-kb/src/groundtruth_kb/policy/engine.py`; Prime fixed that regression and filed `bridge/gtkb-auq-policy-gates-001-007.md` with fresh policy, CLI, lint, format, and full-tree type evidence. The slice adds a root-contained policy registry, `groundtruth_kb.policy` engine, `gt policy check`, and receipt validation primitives while leaving commit, push, platform-write, and hook adapters uninstalled.

**Resource-reference disambiguation update 2026-05-06:** Governed resource identity registry and resolver are implemented and filed as `bridge/gtkb-resource-reference-disambiguation-001-003.md`; awaiting Loyal Opposition `VERIFIED` or `NO-GO`. The slice promotes the registry to `config/agent-control/project-resource-aliases.toml`, leaves `.claude/rules/project-resource-aliases.toml` as a pointer, adds deterministic alias resolution, CI-evidence shape checks, release-gate registry validation, and compact `gt status`/dashboard visibility.

**Systems terminology map update 2026-05-06:** Canonical system/interface map is implemented and filed as `bridge/gtkb-systems-terminology-map-001-003.md`; awaiting Loyal Opposition `VERIFIED` or `NO-GO`. The slice adds `config/agent-control/system-interface-map.toml`, human companion `docs/gtkb-systems-and-tools.md`, deterministic resolver `scripts/resolve_system_interface.py`, compact `gt status`/dashboard visibility, and tests preserving the backlog authority split.

**Agent Red ruff cleanup proposal revision 2026-05-06:** Revised `AGENT-RED-RUFF-CLEANUP-001` filed at `bridge/agent-red-ruff-cleanup-001-003.md`; awaiting Loyal Opposition `GO` or `NO-GO`. The revision addresses the prior NO-GO by adding owner-decision evidence and narrowing this bridge item to a GT-KB read-only planning/baseline packet; live Agent Red source cleanup remains blocked until Mike explicitly scopes a session to Agent Red or provides the concrete Agent Red repository target.

**AUQ advisory disposition 2026-05-06:** Prime disposition filed at `bridge/gtkb-auq-policy-gate-backlog-advisory-2026-05-04-002.md`; awaiting Loyal Opposition review. The advisory is now linked to the implemented `GTKB-AUQ-POLICY-GATES-001` bridge thread instead of leaving a duplicate stale `NO-GO` work surface.

**NO-GO bridge cleanup 2026-05-06:** Prime Builder resolved the five latest-status `NO-GO` bridge entries by filing revised/disposition packets and updating `bridge/INDEX.md`: operating-state monitoring advisory (`bridge/gtkb-ops-current-state-monitoring-advisory-2026-05-04-002.md`), pre-filing preflight hook (`bridge/gtkb-pre-filing-preflight-hook-003.md`), 2026-04-30 bridge-propose helper INDEX parity (`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-005.md`), ADR/DCL S0 audit scope reconciliation (`bridge/gtkb-adr-evaluation-enforcement-s0-audit-2026-04-30-009.md`), and stale `GENERATOR-HARDENING-002` supersession (`bridge/generator-hardening-002-009.md`). These are awaiting Loyal Opposition review as `REVISED` entries; no latest `NO-GO` entries remain in the live bridge index after this cleanup.

**Parallel Prime cleanup while awaiting Loyal Opposition 2026-05-06:** Prime Builder revised proposal-only NO-GO packets that do not require implementation before review: platform CI coverage (`bridge/gtkb-ci-coverage-for-platform-001-003.md`), pip-installed adopter UX (`bridge/gtkb-pip-install-adopter-ux-001-003.md`), evaluation-module waiver retirement (`bridge/gtkb-evaluation-module-restoration-001-003.md`), Slice 5.5 overlay refresh/disposability (`bridge/gtkb-isolation-017-slice-5-5-overlay-tests-003.md`), deterministic operating-state monitoring (`bridge/gtkb-ops-current-state-monitoring-001-003.md`), and AUQ policy gates (`bridge/gtkb-auq-policy-gates-001-003.md`). All six passed bridge applicability preflight, targeted secret scan, and `git diff --check` except for the existing Git line-ending warning on `bridge/INDEX.md`.

**Sequence (do not skip, do not parallelize before Slice 5):**

1. ~~**ISOLATION-017 Slice 4** — `gt project upgrade` isolation + migration/rollback behavior.~~ **DONE — VERIFIED 2026-05-03 S328** at `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-012.md`; **committed 2026-05-03 S329 at `61e50453`**.
2. ~~**ISOLATION-017 Slice 5** — clean-adopter test suite + fixtures.~~ **DONE — VERIFIED 2026-05-03 S329** at `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-006.md`; commit `dc8e58f8`. 13 test files (45 functions) + 2 fixture trees + ci.yml comment + verification script. Slice 5.5 (overlay refresh + disposability) deferred per `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE` v1; tracked at row 31.
3. ~~**ISOLATION-017 Slice 6** — documentation chapter.~~ **DONE — VERIFIED 2026-05-03 S329** at `bridge/gtkb-isolation-017-slice6-docs-2026-05-03-004.md`; commit `9efd29bf`. 314-LOC chapter at `groundtruth-kb/docs/architecture/isolation.md` + verification script (11/11 PASS). 0 NO-GO rounds.
4. ~~**ISOLATION-017 Slice 7** — examples.~~ **DONE — VERIFIED 2026-05-03 S329** at `bridge/gtkb-isolation-017-slice7-examples-2026-05-03-004.md`; commit `05774d6a`. 4 example trees (clean-adopter-minimal/adopter-with-transport-tests/adopter-with-release-gate/existing-adopter-migration) + 2-phase migration verification using `run_doctor` (public surface) + content-presence script. 0 NO-GO rounds. Decision 6 resolved: No 5th Agent Red example.
5. **ISOLATION-017 Slice 8** — release-version gate + closeout. **DONE — VERIFIED at `-012` + COMMITTED `b4346ab6` + PUSHED (S330, 2026-05-03).** History: -001 NEW → -002 NO-GO → -003 REVISED-1 → -004 NO-GO (lifecycle/CI-evidence ordering defect) → -005 REVISED-2 → -006 GO → -007 NEW post-impl REPORT → -008 NO-GO (B5 install-smoke + announcement command-sequence defects) → -009 REVISED-1 (Path A per `DELIB-S330-...-INSTALL-UX-LIMITATION-ACK`) → -010 NO-GO (root-boundary: verifier `tempfile.mkdtemp` resolved outside `E:\\GT-KB`) → -011 REVISED-2 (in-root scratch path `E:/GT-KB/.tmp/slice8-install-smoke/run-<uuid8>/`) → -012 VERIFIED. Codex's independent composite-gate run: 8 PASS, 1 DEFERRED (intentional B6), 0 FAIL; pytest 1945 passed + 1 skipped in 602s. Commit `b4346ab6` pushed to develop; CI workflows triggered. **Move to "Completed during current session" at next session-wrap.** Follow-on: row 5b (Slice 8.5) below. |
| 5b | **ISOLATION-017 Slice 8.5** — CI-green capture on Slice 8 commit | **PARKED awaiting Slice 8.6 fix commit (S330; -001 NEW filed → -002 Codex NO-GO surfaced 3 issues + live CI red on b4346ab6 → owner Path A: pause + Slice 8.6)** | Original NEW at `bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md` filed S330; Codex `-002` NO-GO cited F1 (short-SHA query returns no runs; full SHA required), F2 (`python-tests.yml` path-filter excludes `groundtruth-kb/**`-only commits), F3 (verifier too weak; needs full binding to repo+branch+event+headSha+workflow+conclusion). F2 owner waiver archived as `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER` (python-tests.yml not required for this rc; row 37 added below for v0.7.0 GA CI coverage). **NEW finding during F1 fix probe:** `gh run list --commit b4346ab690e937b80c5c99f776649f8bb8fa82b1` revealed CI is RED on 2 of 4 triggered workflows (`Release Candidate Gate` + `Security Scan`); 41 RC Gate test failures + 1 pip CVE in Security Scan; ALL pre-existing (none Slice 8 regressions). Per `DELIB-S330-RC1-CI-RED-PAUSE-AND-SLICE-8-6-DISPOSITION`, Slice 8.5 is parked until Slice 8.6 lands a fix commit; Slice 8.5 `-003` REVISED-1 will be filed against the cumulative Slice 8 + Slice 8.6 commit. | Awaiting Slice 8.6 VERIFIED + commit. After that, file Slice 8.5 `-003` REVISED-1 addressing F1 (full SHA), F2 (waiver per cited DELIB), F3 (stronger verifier), AND the cumulative commit hash.
| 5c | **ISOLATION-017 Slice 8.6** — CI-failure triage + remediation | **Phase 1 substantially complete (S330, 2026-05-03); 40 of 43 rows classified; awaiting Phase 1 investigation step (3 rows) + Phase 2 implementation in next session** | History: -001 NEW filed S330 → -002 Codex NO-GO with 5 findings (F1 Security Scan failure surface incomplete missed Docker Scout 2 high-severity container CVEs; F2 "all triggered" too weak — must define required workflow/job inventory + fail closed; F3 waiver discipline too loose — needs DELIB ID + scope + expiry + residual risk per waiver; F4 owner-input flow conflicts with `OWNER ACTION REQUIRED` one-at-a-time protocol; F5 stale -002 filename guidance) → -003 REVISED-1 addresses all 5. **REVISED-1 corrections:** failure inventory expanded to 43 entries (41 RC Gate + 2 Security Scan jobs: Dependency Audit pip CVE + Docker Scout 2 high-severity unfixable container CVEs `CVE-2026-33845` gnutls28 + `CVE-2026-5435` glibc); explicit required workflow/job inventory with fail-closed semantics (Lint, Release Candidate Gate, SonarCloud, Security Scan all 4 jobs); waiver schema requires DELIB+Scope+Expiry+Residual risk; one-at-a-time OWNER ACTION REQUIRED protocol per Phase 1 ambiguous row; Phase 4 REPORT uses next available numbered bridge file (not hardcoded -002). 4-phase lifecycle preserved. **Estimated:** 6-9 sessions; owner accepted timeline. | Next: Codex review of `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-003.md` REVISED-1. Disposition resolved S330 via `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE` (formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-03-isolation-017-slice8-disposition.json`): split into Slice 8 + Slice 8.5 per Codex F1 path 1. **Slice 8 scope (REVISED-2):** B1 version bump + B2 ruff resolution + B3 pytest feasibility + B4 release-notes-0.7.0-rc1.md + B5 wheel/sdist smoke + B7 bridge terminal state documentation + closeout artifacts (CHANGELOG entry + announcement + release-readiness CLOSEOUT block + composite verification script). Reaches VERIFIED + commit. **B6 (CI-green evidence) deferred to Slice 8.5** — separate post-VERIFIED bridge thread filed AFTER Slice 8 commit lands; gates `v0.7.0-rc1` tag authorization. History: -001 NO-GO at -002 for dropping 7 release-hardening blockers; -003 REVISED-1 brought all 7 into scope; -004 NO-GO catches bridge-lifecycle gap on B6 (CI-green requires push-then-CI-runs but bridge protocol requires commit-after-VERIFIED — logical contradiction); -005 REVISED-2 implements the split. Decisions D2 (`v0.7.0-rc1`), D4 (all 4 publicity surfaces together), D5 (composite gate) remain resolved. **Slice 8.5 (planned follow-on):** filed as `bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md` AFTER Slice 8 VERIFIED + commit; captures GitHub Actions run URL on Slice 8 commit; release-readiness `ISOLATION-017-CLOSEOUT` B6 row updates from "deferred to Slice 8.5" to "GREEN @ <run-url>"; gates `v0.7.0-rc1` tag.
5. **Release hardening** — known blockers to address before push:
   - Dirty worktree triage (DONE 2026-05-02 S327 — 5 commits landed; tree clean post-44ecb46f).
   - `ruff check .` red across full repo (governance hardening only verified ruff-clean on touched files).
   - Full `pytest` timed out locally (need to scope/parallelize slow lanes for CI).
   - Package version still pinned at `0.6.1` in `groundtruth-kb/pyproject.toml`.
   - Release notes / changelog need next-version (`0.7.0-rc1`) update.
6. **v0.7.0-rc1 release** — push to GitHub as installable release; PyPI publish.

**Live workstreams (formerly captured-only under S327 freeze; lifted 2026-05-07 S332 per `DELIB-S332`):**
- Backlog source-of-truth Slices 2-7 (DDL migration, CLI, render generator, etc.). Specs at `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` + `DCL-STANDING-BACKLOG-DB-SCHEMA-001`. Now actionable; high acceleration leverage per S332 prioritization analysis.
- Primer Slices 2-5 (regenerate CLI, smart-poller dispatch, AGENTS.md reconciliation, release-gate integration). Slice 1 dogfood install live in `.claude/rules/canonical-terminology.{md,toml}`. Now actionable.
- Disambiguation Slices 2-7 (PreToolUse hook, PostToolUse audit, bridge-compliance-gate extension, dispatch integration, backfill audit, doctor check). Slice 1 policy file + library skeleton live in `templates/rules/canonical-terminology-policy.toml` + `groundtruth_kb/term_disambiguation.py`. Now actionable.
- S330/S331 advisory/governance captures (`GTKB-AI-ASSISTED-DELIVERY-MATURITY-MODEL`, `GTKB-ENV-INVENTORY-001`, `GTKB-SYSTEMS-TERMINOLOGY-MAP-001`, `GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001`). Now eligible for normal bridge-lifecycle pickup; route through standard proposal → GO → implement.

## Next Actionable Items (hand-maintained; automation tracked under GTKB-GOV-BACKLOG-DISCIPLINE)

**S325 ISOLATION-016 CLOSED (2026-05-01):** GTKB-ISOLATION-016 Wave 3 VERIFIED at `bridge/gtkb-isolation-016-phase8-wave3-execution-012.md` (no blocking findings; one cosmetic non-blocker on driver banner tracked as follow-on row 25). Implementation at commit `ef78c0db` + REVISED-1 fix at `bb683bc0`. Manifest now carries `db_reconciliation_strategy = manifest_driven_filter` and `unclassified_disposition = leave_behind_with_warning`. Per Wave 3, the rehearsal end-to-end produces a filtered preview DB with 24,544 adopter rows / 120 framework excluded / telemetry-empty / integrity_check ok against the live 1.0 GB KB.

**P0 SECURITY ELEVATION (2026-05-05 owner directive):** `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` is now the top actionable item. Scope: purge or redact secret-bearing tracked artifacts; inspect fetched history without printing secrets; harden generated artifact/export paths so env-like and token-like material is redacted by construction; wire mandatory inspection-before-commit and pre-push/CI/release-gate enforcement; and prepare a separate owner-approved history-purge plan if GitHub history rewrite is required. Related existing backlog items remain linked dependencies, not substitutes: `ISOLATION-017 Slice 8.6` Security Scan enforcement, `GTKB-GOV-002` release-candidate gate skill, `gtkb-credential-patterns-canonical`, `GTKB-STARTUP-REFRACTOR-001` credential-safety finding, and Agent Red Tier A credential-scan adoption.

**S324 PRIORITY ELEVATION (2026-04-30 owner directive; updated 2026-05-01 S325):** The GTKB-ISOLATION program remains TOP priority. Sequence: **~~(1) ISOLATION-016~~ DONE 2026-05-01 S325**; **(2) ISOLATION-017** — adopter packaging + clean-adopter validation (NOW ACTIONABLE after 016 VERIFIED); **(3) ISOLATION-018** — Agent Red child-directory cutover (after 017 VERIFIED; requires explicit owner approval for migration window); **(4) ISOLATION-019** — program closeout + cleanup (after 018 VERIFIED). Parallel future work: **ISOLATION-015 Slice 2** (typed `work_subject.set/rollback` control-plane operations) does NOT block the 017→019 sequence. All other actionable items below defer beneath the ISOLATION program.

Updated: 2026-04-28 (S319) — **DRIFT TRIAGE + DORA-001b TRACK 1 CLOSED + MEMBASE-EFFECTIVE-USE-RECOVERY ADDED + DA DISCIPLINE RESTORED**. Row 19 `GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY` added per owner directive 2026-04-28 (S319) following Codex LO assessment at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/MEMBASE-EFFECTIVE-USE-ASSESSMENT-2026-04-29.md`; assessment archived as `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` (lo_review). Four S319 owner decisions also archived: `DELIB-S319-BRIDGE-CENTRALIZATION-OPTION-A`, `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`, `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`, `DELIB-S319-PHASE1-TIGHT-SCOPE-AUTHORIZATION`. Earlier S319 entry: Row 1 `GTKB-DORA-001b` Track 1 marked DONE per VERIFIED at `bridge/gtkb-dora-001b-track1-implementation-012.md` (terminal closure after 2 NO-GO/REVISED cycles on post-impl: F841 lint fix + pytest-capture source fix). Implementation at commit `0e7a414d` adds writer-side `deploy_evidence` to manifest emission via `args._deploy_evidence` accumulator populated by phase 8/10/15; classifier and confidence functions in `refresh_dashboard_db.py` UNCHANGED per `-005` scope correction. 13 writer tests + 2 backward-compat regression tests; 31/31 PASS under default pytest capture. Two new bridge threads VERIFIED: `role-contract-clarifications-2026-04-28` (-004) closing 3/9 gaps from DELIB-S310 + `session-hygiene-gitignore-extensions-2026-04-28` (-004) extending S317 telemetry-churn-policy. **S318 carryover (still pending move to Completed section):** Row 16 `GENERATOR-HARDENING-001`, Row 17 `GENERATOR-HARDENING-002`, Row 18 `GENERATOR-HARDENING-CROSS-REPO` — all DONE-marked from S318, awaiting bulk move at future cleanup pass. Earlier entries: 2026-04-27 (S314) added GENERATOR-HARDENING-001 row from GTKB-ISOLATION-016 Wave 2 Slice 11 VERIFIED at `bridge/gtkb-isolation-016-phase8-wave2-slice11-016.md`; the audit-hook lane empirically surfaces ~17 PROJECT_ROOT-bound legacy reads in `scripts/session_self_initialization.py`. Earlier S314 entries: P1 of GTKB-STARTUP-ENHANCEMENTS VERIFIED at `bridge/gtkb-startup-enhancements-p1-006.md` (S309); GTKB-WRAPUP-ENHANCEMENTS row from session-wrap-up effectiveness evaluation.

| # | ID | Status | Blocks / blocked by | Next step |
|---|---|---|---|---|
| 0 | `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` | **P0 OWNER-ELEVATED 2026-05-05; Slice 1 VERIFIED; Slice 2 implemented and post-impl filed 2026-05-06; Slice 3 history-purge plan filed after redacted all-refs findings** | Controlling incident workstream created after Shopify reported exposed API credentials in a tracked GT-KB artifact and Codex verified that current rotated secret/token values were not found in fetched history, while old secret-bearing artifacts/history and credential-shaped generated outputs remain repo-side risk. Groups, but does not replace, existing related work: `ISOLATION-017 Slice 8.6` Security Scan fail-closed enforcement, `GTKB-GOV-002` release-candidate gate skill, verified `gtkb-credential-patterns-canonical`, `GTKB-STARTUP-REFRACTOR-001` credential-safety finding, and Agent Red Tier A credential-scan adoption. Required outcomes: (1) inventory exposure across tracked files, generated docs, bridge payloads, tags, and fetched branch history without printing secret values; (2) purge/redact current tracked secret-bearing artifacts; (3) harden extraction/export/generation paths to redact env-like assignments and token/API-secret patterns by construction; (4) enforce inspection-before-commit and pre-push/CI/release-gate secret scanning; (5) produce a separate owner-approved history-purge plan before any destructive GitHub history rewrite. Slice 2 current-tracked scan reports 0 verified-provider findings and 239 candidate-high findings; all-local-refs scan reports 23 verified-provider-class historical findings, so destructive history action remains blocked pending Slice 3 review and explicit owner approval. | Next: Loyal Opposition reviews Slice 2 post-implementation report `bridge/gtkb-secrets-purge-and-commit-enforcement-slice2-ci-prepush-003.md` and Slice 3 planning artifact `bridge/gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan-001.md`. No history rewrite, force-push, tag rewrite, branch deletion, credential lifecycle operation, or GitHub settings mutation is authorized. |
| 45 | `GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-001` (Extend formal-artifact-approval to narrative artifacts; AUQ decision-class hook; post-hoc audit hook) | **OWNER-DIRECTED HIGH-PRIORITY 2026-05-08 S337; scoping bridge filed in same session at `bridge/gtkb-narrative-artifact-approval-extension-001-001.md`; awaiting Loyal Opposition GO/NO-GO** | Owner directive: extend `GOV-ARTIFACT-APPROVAL-001` formal-artifact-approval gate (currently covers ADR/DCL/GOV/SPEC/PB mutations) to cover narrative artifacts — `.claude/rules/*.md` rule files, `memory/work_list.md` narrative entries, `MEMORY.md` sections. Currently narrative artifacts can be edited by agents without owner-visible packet display, creating the "AI silently preserves things the owner doesn't endorse" failure mode demonstrated in S337 when owner was surprised by `.claude/rules/operating-model.md §2` and `.claude/rules/canonical-terminology.md` text saying `memory/work_list.md` persists post-migration as a generated view. The validated feedback rule "Surface artifact-vs-owner contradictions" saved S337 is the procedural patch this enhancement makes structural; per `.claude/rules/bridge-essential.md` S294 lesson "if it is essential, it must be tracked," procedural mandates are not enforceable. **Three-part scope (per session analysis):** (A) extend formal-artifact-approval pathway to narrative artifacts so a packet must exist before a Write commits; (B) AskUserQuestion decision-class hook — agent declares `decision_class` (artifact-correction, scope-choice, approval, etc.); the hook validates option-set requirements per class; artifact-correction class requires a "reaffirm current artifacts" option; (C) post-hoc audit hook — pre-commit scan rejects commits that change canonical artifacts without same-session AUQ-with-decision-class evidence cited in the message. Per Deterministic Services Principle in `.claude/rules/acting-prime-builder.md`, this is exactly the case where session-friction (procedural mandate) should become service infrastructure. **Sequencing:** non-blocking parallel program; can ship in parallel with isolation closure work and parent-thread `gtkb-gov-backlog-source-of-truth-2026-05-02` Slices 2-7. **Coupling:** complements `gtkb-backlog-work-list-retirement-directive-001` (also S337) which itself motivated this enhancement when it surfaced the artifact-drift gap; coupled to `GTKB-ARTIFACT-RECORDER-CLI` (row 15) which moves formal-artifact insertion plumbing behind a CLI service — both are Deterministic Services Principle manifestations. | Next: Loyal Opposition reviews `bridge/gtkb-narrative-artifact-approval-extension-001-001.md` for GO/NO-GO. After GO, implementation slices A/B/C land separately, each with owner-visible approval packets per the gate they extend. After all three slices VERIFIED, the S337 feedback memory entry "Surface artifact-vs-owner contradictions" can be retired (or downgraded to an explanatory note pointing at the structural gate). |
| 46 | `GTKB-BRIDGE-SKILL-UNIFIED-001` (Expose unified bridge skill across Claude + Codex harnesses) | **OWNER-DIRECTED 2026-05-08 S337; scoping bridge filed at `bridge/gtkb-bridge-skill-unified-001-001.md`; awaiting Loyal Opposition GO/NO-GO** | Owner asked whether bridge can be exposed as a skill that appears and behaves similarly across Claude Code and Codex harnesses, so per-platform behavior changes don't accumulate. Existing cross-harness skill-adapter infrastructure (`scripts/generate_codex_skill_adapters.py` + `config/agent-control/harness-capability-registry.toml` + `DELIB-CODEX-HARNESS-PARITY-SPEC-BUNDLE-2026-05-05`) already shares 26 skills between harnesses with byte-equivalent content; this thread extends the same pattern to a unified bridge-protocol skill covering propose / scan / respond / verify / lifecycle / status. Skill body delegates to harness-agnostic scripts/CLI; per-platform divergence remains only at the hook-registration layer (`.claude/settings.json` vs `.codex/hooks.json`) which is unavoidable due to schema differences but can be minimized to ~6 lines per side via the shared-script pattern. Existing per-action skills (`bridge-propose`, `proposal-review`, `send-review`) either coexist as more-specific entry points or get marked superseded — disposition decision deferred to Codex review of the scoping proposal. **Sequencing:** non-blocking parallel program; can ship in parallel with `gtkb-bridge-poller-event-driven-replacement-001`. Slice 3 (`gt bridge` CLI subcommand) shares foundation with the sibling thread's Slice 1 (`scripts/cross_harness_bridge_trigger.py`); Slice 3 may be deferred or folded into the sibling thread per Codex disposition. **Aligns with:** Deterministic Services Principle (`DELIB-S312`); GTKB-ARTIFACT-RECORDER-CLI (row 15 — same Deterministic Services pattern for artifact insertion); DELIB-CODEX-HARNESS-PARITY-SPEC-BUNDLE-2026-05-05. | Next: Loyal Opposition reviews `bridge/gtkb-bridge-skill-unified-001-001.md` for GO/NO-GO. After GO, Slice 1 (author canonical `.claude/skills/bridge/SKILL.md`) ships first; Slice 2 (register in capability registry + run adapter generator to produce `.codex/skills/bridge/SKILL.md`) follows; Slice 3 disposition decided at GO. |
| 1 | `GTKB-DORA-001b` Track 1 | **DONE — VERIFIED 2026-04-28 S319** (manifest-writer enhancement) | Implementation at commit `0e7a414d`; lint fix at `01628b0b`; pytest-capture source fix at `71b391d3`. VERIFIED at `bridge/gtkb-dora-001b-track1-implementation-012.md` after 2 NO-GO/REVISED cycles. Scoping addendum at `bridge/gtkb-dora-001b-authoritative-deployment-source-008.md` GO terminal (S311). Track 2 (ingest) was already VERIFIED at S313. Source B (GH Actions out-of-band detection) deferred to GTKB-DORA-001c. **DORA-001b umbrella now closeable**; remaining work is GTKB-DORA-002 KPI query work which is a separate work item. | Move to "Completed during current session" section at next session-wrap. |
| 2 | `GTKB-ISOLATION-016` | **DONE — VERIFIED 2026-05-01 S325** (Wave 3 complete) | Wave 3 execution VERIFIED at `bridge/gtkb-isolation-016-phase8-wave3-execution-012.md`. Implementation lifecycle: Wave 1 + Wave 2 (11 slices VERIFIED) shipped earlier; Wave 3 = 5 NO-GO/REVISED cycles → GO at `-008` → impl `ef78c0db` → post-impl `-009` → NO-GO `-010` (per-table schema) → REVISED-1 `-011` + impl `bb683bc0` → VERIFIED `-012`. Manifest now carries `db_reconciliation_strategy = manifest_driven_filter` + `unclassified_disposition = leave_behind_with_warning`. New lane `scripts/rehearse/_db_filter_dryrun.py` consumes Slice 8 partition manifest and emits filtered preview DB at `{output_dir}/db-filter-dryrun/`. Live smoke against 1.0 GB live KB: 24,544 adopter / 120 framework / 4 telemetry / 19 orphan; integrity_check ok; filtered DB 24 MB. KB documents created per GOV-20 Phase 1: `IPR-WAVE3-DB-FILTER-001`, `CVR-WAVE3-DB-FILTER-001`. Three S325 owner decisions archived as DELIBs: `DELIB-S325-DB-RECONCILIATION-STRATEGY-CHOICE`, `DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE`, `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE`. Rule amendment `Sandbox Output Exception` landed in `.claude/rules/project-root-boundary.md`. Freeze-window runbook landed at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/runbooks/AGENT-RED-CUTOVER-FREEZE-WINDOW-RUNBOOK-2026-05-01.md`. Codex non-blocking observation: driver banner still prints "Wave 2 dispatch" for Wave 3 phases (cosmetic-only; tracked as row 25 follow-on). **GTKB-ISOLATION-017 NOW ACTIONABLE.** | Move to "Completed during current session" section at next session-wrap. |
| 3 | `GTKB-DASHBOARD-002` Slice 2.3 (integration) | blocked on owner | Blocked on owner notifier-default choice (email / Slack / Teams / none). GO condition from `slice2-002.md` F2: justify any new `ci_runs` persistence against existing `testing_service_integrations`. | File `gtkb-dashboard-industry-alignment-slice2c-integration` after owner decides §5.5 notifier default. |
| 4 | `GTKB-DASHBOARD-002` Slice 2.2 (metrics) | parked (external trigger) | Implementation already shipped at slice2b-metrics `-008` GO; thread parked at `-025/-026 VERIFIED` per the parking-baseline protocol. Awaits external prereq chain: commit security-scan workflow on `develop` → merge to `main` → `workflow_dispatch` on `main` → completed run with `pip-audit-results` artifact. | When external trigger fires, file post-impl evidence per `-023 §2.5` Steps A–E. |
| 5 | `GTKB-GOV-PROPOSAL-STANDARDS` Slice 1 | GO; requires root-boundary reconciliation before implementation continues | REVISED-9 GO'd at `bridge/gtkb-gov-proposal-standards-slice1-020.md`. Blocks its own Slice 2/3/4 + `GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1`. Owner root-boundary directive now requires all active GT-KB implementation artifacts to live under `E:\GT-KB`; no external `groundtruth-kb` checkout may be used as a live dependency. | Re-file or revise implementation routing so work lands under `E:\GT-KB` and applications adopt from in-root GT-KB artifacts only. |
| 6 | `GTKB-GOV-DA-ENFORCEMENT` | passive tracking; root-boundary reconciliation required | Previously described as owned by an external `groundtruth-kb` main. Owner root-boundary directive now requires the active GT-KB source of truth to be in `E:\GT-KB`. | Reconcile tracking to an in-root GT-KB artifact/source path before further action. |
| 7 | `GTKB-GOV-CODE-QUALITY-BASELINE` | scoping in flight; root-contained routing required | Slice 1 governance design filed at `bridge/gtkb-gov-code-quality-baseline-slice1-001.md`; awaits Codex GO. New standing backlog entry per owner directive 2026-04-25. Defines a default code-quality checklist (CQ-* rule IDs) applying to all GT-KB adopter project proposals unless explicitly N/A or owner-suspended via the waiver lifecycle. | After Codex GO on Slice 1, file Slice 2 implementation bridge for in-root GT-KB artifacts under `E:\GT-KB`; applications consume from `E:\GT-KB\applications\` only. |
| 8 | `GTKB-GOV-OWNER-DECISION-SURFACING` | **DONE — VERIFIED 2026-04-27 S315** | Slice 1 VERIFIED at `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md`. Owner directive 2026-04-25: mechanically force surfacing of owner-decision pending state. Implementation shipped: durable `memory/pending-owner-decisions.md` file, `.claude/hooks/owner-decision-tracker.py` (Stop / SessionStart / UserPromptSubmit dispatch), settings.json registration, test file in release-candidate gate. | Move to "Completed during current session" section at next session-wrap. |
| 9 | `GTKB-STARTUP-ENHANCEMENTS` | P1 VERIFIED 2026-04-25 (S309); P2-P8 remain | P1 closed at `bridge/gtkb-startup-enhancements-p1-006.md` VERIFIED (commit `3caa034d` impl + `857ea71e` audit). MEMORY.md trim recovered ~10,400 tokens (59,753 → 18,119 bytes); atomic-write helper + 4 call sites; ceiling test in release-gate; Codex hooks.json cleanup. Owner-chosen P4 stance: full consolidation (8 rule files → 3). | Next: P2 Claude startup-freshness contract OR P3 six-primer registry. P2 is the smaller standalone bridge; P3 is the architectural foundation that subsequent phases build on. P2 first if iterating; P3 first if ready to commit to the architectural redesign. |
| 10 | `GTKB-WRAPUP-ENHANCEMENTS` | scoping w/ architecture (filed 2026-04-25 S309); Slice 1 Stage 1 VERIFIED 2026-04-26 (S310) | Owner directive 2026-04-25 (S309): make session wrap-up systematically achieve five goals (1) record knowledge/decisions/directives missed during session; (2) identify cross-artifact contradictions while context is fresh; (3) consume usable context to close in-flight work; (4) describe what next session should anticipate per topic; (5) surface hygiene/maintenance candidates. Architecture: 5-scanner suite (S1 synthesis / S2 consistency / S3 loose-ends / S4 continuation guide / S5 hygiene) running on owner-triggered `/wrap`, not auto-on-Stop. Coupled with GTKB-STARTUP-ENHANCEMENTS via S4 → P6 handoff doc. Owner-chosen trigger: **on-demand /wrap only**. Owner-chosen structure: **separate item, coordinated phases**. **Sub-feature S1.a (added S310 2026-04-26): Prime Insight harvesting** — at session-end harvest, extract content delimited by `★ Insight ─────...─` markers from the session transcript and persist as DA records with `source_type='session_harvest'`, `id='DELIB-INSIGHT-{session_id}-{NNN}'`, attribution (session_id, prompt source_ref, sequential index), and standard DA redaction. Hard prerequisite: WRAPUP-Slice-2A ships transcript content + redaction policy + retention + ignore coverage; S1.a depends on Slice-2A landing first. Owner directive S310: fold this into WRAPUP rather than parallel program. | First: file W1+W2 batch implementation bridge (transcript-snapshot precursor + S5 hygiene scan + S2 consistency check). DONE — Slice 1 Stage 1 VERIFIED at `bridge/gtkb-wrapup-enhancements-slice1-014.md`. Next: WRAPUP Slice 1 Stage 2 (allowlist baseline) when triggered, then WRAPUP-Slice-2A (transcript content + redaction). S1.a Insight harvesting designs in Slice-2A scope. |
| 11 | `GTKB-ROLE-ENHANCEMENT` | **deferred until post-isolation** (filed 2026-04-26 S310; updated S312 2026-04-27) | Owner directive 2026-04-26 (S310): file an implementation proposal enhancing the Prime Builder and Loyal Opposition role contracts. Substantive analysis recorded as `DELIB-S310-ROLE-DEFINITION-ASSESSMENT` in the Deliberation Archive (groundtruth.db). The deliberation identifies 9 underdefined gaps with this-session evidence (review-depth methodology, independence guarantee, conflict-resolution path, LO investigation authority, methodology audit trail, quality-bar asymmetry, post-impl review depth, emergency-path role contract, LO state access) and proposes 5 leveraged formalization clauses spanning `loyal-opposition.md`, `report-depth-prime-builder-context.md`, `file-bridge-protocol.md`, and a new `expedited-paths.md` rule. **S312 update (2026-04-27)**: `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE` extends the parent assessment with empirical evidence from the GTKB-ISOLATION-016 Wave 2 Slice 4 lifecycle (4 NO-GOs across proposal + post-impl) confirming all 9 gaps remain real, and recommends one near-term clause: a review-depth heuristic in `report-depth-prime-builder-context.md` requiring LO to walk proposal §4 output-layout diagrams against the proposal's described `output_files` lists at proposal review (would have prevented the Slice 4 `-006` F2 NO-GO). **Sequencing constraint**: do NOT begin until `GTKB-ISOLATION-017` Phase 9 productization is VERIFIED. Rationale: the role-enhancement work is governance change; overlapping it with ISOLATION productization would create cross-cutting dependencies, and post-migration empirical evidence will sharpen the proposal. | When ISOLATION closure unblocks: file `bridge/gtkb-role-enhancement-001.md` as scoping bridge citing both `DELIB-S310-ROLE-DEFINITION-ASSESSMENT` and `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE` for the assessment substance; propose phased clauses per the deliberations' §"Recommended formalization" tables; route framework rule changes upstream to `groundtruth-kb`. Optional near-term: file the review-depth heuristic clause as a standalone bridge if owner wants pre-isolation movement. |
| 12 | `GTKB-COMMAND-SURFACE` | program tracking (architectural plan VERIFIED at `bridge/gtkb-command-surface-004.md` GO; CS-1.5 VERIFIED at `bridge/gtkb-command-surface-cs1-5-004.md`) | Architectural plan: `::` prefix in-session command dispatch with per-turn detector suppression. Authoritative ADR pending (cited in plan §6); future formalization. Slice plan: **CS-1** `gt` CLI binary on PATH; **CS-1.5** registry tracking via .gitignore negation + regression test (DONE — VERIFIED 2026-04-26); **CS-2** dispatcher hook + suppression contract + registry schema; **CS-3** first command set (`::spec`, `::decide`, `::question`, `::init`, `::wrap`, `::bridge`); **CS-4** dashboard cross-surface affordance (action-center rows emit copy-to-clipboard `::cmd` strings); **CS-5+** macros and workflow scaffolds; **CS-6** Codex parity (rules + parity verifier); **CS-7** local-command audit and disposition. **Sub-feature CS-2.help (added S310 2026-04-26)**: `::help` registry-aware command (NOT skill-dispatched). Bare `::help` lists all registered commands with one-line descriptions; `::help <cmd>` shows full registry entry (skill, suppress_detectors, argument_handling, description, detail, related). Registry schema gains `description` and `detail` fields. `::help` does NOT suppress detectors (read-only query). Belongs in CS-2 scope because it queries the registry itself, not a skill. Discoverability on critical path — without it, owner must read CLAUDE.md to discover commands. | Next slice ready to file: **CS-2** (dispatcher hook + suppression contract + registry schema + `::help` per CS-2.help). Or pursue CS-1 (`gt` CLI binary) in parallel since the architectural plan §9 explicitly authorizes parallel CS-1/CS-2 work. |
| 13 | `GTKB-DB-BACKUP-001` | implementation proposal filed 2026-05-06 | Scoping filed at `bridge/gtkb-db-backup-001-snapshot-daemon-001.md`; Loyal Opposition NO-GO at `-002` required non-synced staging, integrity check before publication, atomic publish, and alignment with actual `gt` CLI / `groundtruth.toml` config surfaces. Revised scoping `-003` received GO at `-004`. Prime filed implementation proposal `bridge/gtkb-db-backup-001-snapshot-daemon-005.md` for upstream `gt db snapshot`: staged `VACUUM INTO` or `Connection.backup()`, `PRAGMA integrity_check`, same-volume `os.replace()`, quarantine, manifest, retention, `[backup]` config, CLI/docs/tests. | Await Loyal Opposition GO/NO-GO on `-005`; after GO, implement in `groundtruth-kb`. After upstream VERIFIED, Agent Red adopts via `gt project upgrade` + separate adopter-side follow-up to point SyncBackSE `CLAUDE-COPY` profile at the snapshot dir instead of live `E:\GT-KB\`. |
| 14 | `GTKB-BRIDGE-POLLER-001` | scoping in flight; 4 sub-threads VERIFIED/GO'd at S315 round 4-5 | **S315 progress:** umbrella REVISED-3 GO at `bridge/gtkb-bridge-poller-001-smart-poller-007.md`. Sub-threads: (a) P1 detector REVISED-1 GO at `bridge/gtkb-bridge-poller-p1-detector-004.md` — implementation queued upstream in `groundtruth-kb`; (b) P2 registry REVISED-2 GO at `bridge/gtkb-bridge-poller-p2-registry-006.md` — scoped to static-only per Codex feedback, implementation unblocked; (c) P2.5 verification spike REVISED-1 GO at `bridge/gtkb-bridge-poller-p2-5-verification-spike-004.md` — spike RUN requires owner approval (~2.1M tokens one-time); (d) P3 invoker design hard-gated on P2.5 spike-report.md evidence per umbrella §3.3. Concurrency/isolation/governance/cost-analysis contracts all in umbrella `-006`. | Three parallel implementation tracks unblocked: (1) **P1 detector** (Agent Red filing upstream impl bridge + tests in `groundtruth-kb`); (2) **P2 registry** (static-record-only module + samples; psutil dropped); (3) **P2.5 spike** owner-approval-gated live run + report. P3 awaits spike report. P7-P8 Agent Red adopter follow-up after upstream P1/P2/P3 VERIFIED. |
| 15 | `GTKB-ARTIFACT-RECORDER-CLI` | not-yet-filed (added 2026-04-27 S312) | Owner-approved 2026-04-27 (S312) following discussion of formal-artifact-approval-gate friction during the DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE insertion. Move formal-artifact insertion plumbing (deliberations, GOV/SPEC/PB/ADR/DCL records, owner-decision packets) behind a `gt <artifact-type> record` CLI in `groundtruth-kb`. Service handles ID generation, SHA computation, approval-packet construction, KB insertion, and ChromaDB indexing. AI surface drops from ~150 LOC of orchestration (record_*.py boilerplate + manual packet JSON + env-var threading) to a single CLI call with 6-8 structured arguments. Reduces per-insertion friction by ~85% while preserving (or strengthening) audit-trail and approval-evidence requirements. Aligns with `GTKB-COMMAND-SURFACE` CS-1 (`gt` CLI binary on PATH) — same pattern as the existing `gt project classify-tree` consumed by `_path_rewrite.py` in Slice 4. The formal-artifact-approval-gate hook remains as defense-in-depth for raw-API anomalies. **Sequencing:** non-blocking parallel program; can ship before or after isolation completes. Owner principle (S312, 2026-04-27): "Actively pursue opportunities to reduce repetitive work done by AI, both because it burns tokens unnecessarily and because AI-driven procedures have a higher error rate than simpler deterministic implementations. Project should be viewed as a collection of artifacts, rather than a dialog with accompanying activity." This work item is the first concrete manifestation of that principle. | Next: file scoping bridge `bridge/gtkb-artifact-recorder-cli-001.md` upstream in `groundtruth-kb` proposing the CLI surface + service implementation + approval-flow integration + hook-relaxation contract. Adopters consume via `gt project upgrade` after upstream VERIFIED. |
| 20 | `GTKB-COMMIT-TRIAGE-001` | **DONE — triage complete 2026-04-29** | Owner-directed work-item creation 2026-04-29 following observation of 58 uncommitted files in working tree post-S321 wrap (commit `ecfc7d0b`). Triage executed across 12 scoped commits (`e599a688` membase-recovery GO recovery + work_list row 19 lifecycle; `a5fc8ec9` spawned-harness-role-defer GO recovery; `da5d4d7a` active-workspace-declaration-architecture registration; `73c41ee4` audit_gtkb_triad_completeness utility + S321 temps deletion; `e917b9b8` rule files multi-driver consolidation; `46f5d7ea` codex-framing review checklists; `d6af86b1` workstream + codex-hook-parity active-workspace audit; `b693ba92` active-workspace NO-GO recovery; `285fa1ef` smart-poller program 17 files; `8111ef09` bridge-propose helper Spec Linkage Gate; `f090c16b` dashboard multi-driver; `464d5435` pending-owner-decisions auto-tracker state). Three Codex bridge artifacts recovered: membase-recovery GO, spawned-harness GO, active-workspace NO-GO (all stranded uncommitted; INDEX recovery applied where needed via `GOV-FILE-BRIDGE-AUTHORITY-001` Prime/LO bridge-repair authority). One Prime draft registered (active-workspace-declaration-architecture-2026-04-29-001 NEW). Three S321 _temp_ scripts deleted (Decision B). One audit utility committed standalone (Decision C). Two clusters required multi-driver attribution (cluster #4 rule files: 4 drivers; cluster #10 dashboard: 2 drivers) because hunk-level scoping wasn't tractable from this triage's tooling — documented as triage finding. KB record `GTKB-COMMIT-TRIAGE-001` v1, `origin=hygiene`, `component=governance`, `source_spec_id=GOV-FILE-BRIDGE-AUTHORITY-001`. Acceptance: `git status --short` clean post-close-out; each commit cites driving thread + Codex GO/NO-GO file where applicable; INDEX.md reflects all on-disk bridge files for 2026-04-29 threads; no bridge files deleted (audit trail preserved). | Move to "Completed during current session" section at next session-wrap. KB record will be updated to `resolution_status=resolved`, `stage=resolved` post-commit. |
| 19 | `GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY` | **GO at `bridge/gtkb-membase-effective-use-recovery-2026-04-29-002.md`** (filed 2026-04-29; Codex GO with 6 non-blocking conditions for follow-on slice bridges) | Owner directed 2026-04-28 (S319) after Codex Loyal Opposition assessment at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/MEMBASE-EFFECTIVE-USE-ASSESSMENT-2026-04-29.md`. Assessment archived as `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` (lo_review). Codex P1 finding: `bridge/INDEX.md` lists `gtkb-membase-effective-use-umbrella` as VERIFIED at `-014`, but only `-001` exists on disk; `-014` is phantom and the apparent VERIFIED status cannot be trusted as implementation evidence. Five effectiveness gaps: (1) automatic candidate capture from owner statements; (2) owner-visible spec/intake event emission in chat; (3) foundational project-intake workflow for new adopters; (4) reconciled work-item harvesting; (5) verified non-phantom bridge evidence. Recommended four slices: **Slice A** chat-visible spec/intake event surfacer (per-session seen ledger + idempotency); **Slice B** safe auto-capture from owner requirement language (classifier upgrade with formal-approval handling); **Slice C** confirm/reject owner command loop (`confirm intake INTAKE-...`/`reject intake INTAKE-... <reason>` or slash-skill); **Slice D** foundational requirements intake aligned with SPEC-INTAKE-3623f1 using `type=requirement` + `section=foundational/<category>` rather than new type. Plus: WI harvest as release-visible control (treat GTKB-GOV-004 + GTKB-GOV-010 as same recovery program); effectiveness metrics defined before implementation (capture latency, visibility latency, confirmation rate, unreconciled WI count, bridge-to-MemBase drift); preserve MemBase/DA/MEMORY.md/ChromaDB boundary. **Acceptance criteria** for future implementation proposal: phantom-INDEX reconciliation statement; specific files per slice; formal-artifact-approval handling for any DA/SPEC/GOV mutation automation; tests for event surfacing/capture/confirm-reject/false-positive-suppression; dashboard metric updates distinguishing raw vs reconciled MemBase work; rollback plan that disables hooks without corrupting MemBase or DA state. **Sequencing:** non-blocking parallel program; can ship in parallel with isolation Phases 2-6. **Aligns with:** GT-KB vision filter (limit owner role to specs/clarifications/decisions); DELIB-0874 artifact-oriented governance; SPEC-INTAKE-c9e997, SPEC-INTAKE-2485e9, SPEC-INTAKE-3623f1. | Next: scoping bridge filed at `bridge/gtkb-membase-effective-use-recovery-2026-04-29-001.md` (commit `ed4d7b37`) and Codex GO'd at `-002.md` (untracked, recovery in flight under `GTKB-COMMIT-TRIAGE-001`). Required next Prime actions per Codex GO §"Required Next Prime Builder Actions": (1) row 19 status update — DONE in this commit; (2) file Slice A implementation bridge before modifying any hook code; (3) keep Slice B, Slice C, Slice D, and WI-harvest behind their own bridge proposals and spec-derived test mappings. Six non-blocking conditions for follow-on bridges captured in Codex GO §"Non-Blocking Conditions for Follow-On Bridges". Implement slices sequentially A → B → C → D, each with its own implementation bridge. WI-harvest reconciliation may proceed in parallel with Slice A. |
| 18 | `GENERATOR-HARDENING-CROSS-REPO` | **DONE — VERIFIED 2026-04-28 S318** (cross-repo subprocess class; condition-4 narrowed) | Implementation at commit `c116d627` (degrade-only `_git_checkout_info` scope check). VERIFIED at `bridge/generator-hardening-cross-repo-009.md` after Codex `-007` NO-GO + Prime `-008` REVISED-1 with explicit condition-4 narrowing. Condition 4 narrowed to "no cross-repo git subprocess for outside-root checkout" (proven by `test_git_checkout_info_returns_degraded_when_outside_project_root` monkeypatch). Lane-wide cleanliness (`status: ok`, `violations: 0`) delegated to follow-on `bridge/harness-state-preferences-path-cli-2026-04-28` (GO at `-002`; implementation in flight S318). | Move to "Completed during current session" section at next session-wrap. After follow-on VERIFIED, GH-001 (row 16) becomes closeable via REVISED-2 of post-impl. |
| 17 | `GENERATOR-HARDENING-002` | **DONE — VERIFIED 2026-04-28 S318** (skills/plugin-cache closure via Option C) | Closure thread `bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28-006.md` VERIFIED. Owner-chosen Option C: 3 remaining `Path.home()` sites in `scripts/session_self_initialization.py` (skills + plugin-cache discovery) gated behind `GTKB_DISCOVER_USER_EXTENSIONS=1` opt-in env var. Default invocation makes ZERO `Path.home()` calls in skills/plugin-cache discovery. Implementation at commit `cffd00df`; 3 regression tests pass; ruff clean. | Move to "Completed during current session" section at next session-wrap. |
| 16 | `GENERATOR-HARDENING-001` | **DONE — VERIFIED 2026-04-28 S318** (original -004 gate met empirically; terminal closure) | Thread VERIFIED at `bridge/generator-hardening-001-010.md`. Implementation at commit `80e16ba8` (Type A-D fixes — DEFAULT_DASHBOARD_DIR/DEFAULT_HISTORY_PATH removed; public partial-argument regression test in place). Original `-004` gate (`status: ok, violations: 0`) met empirically after two follow-on bridges in S318: `bridge/generator-hardening-cross-repo-009.md` VERIFIED (cross-repo git subprocess class) + `bridge/harness-state-preferences-path-cli-2026-04-28-006.md` VERIFIED (preferences/role-record/lifecycle-guard cascade via class-level fix in workstream_focus.py). Lane state: status:ok, violations:0, []. Codex re-verification: 9 focused tests pass, ruff clean. Future audit-hook leaks open distinct bridge threads; no GH-001 reopens unless they directly regress PROJECT_ROOT fallback behavior. | Move to "Completed during current session" section at next session-wrap. |
| 21 | `GTKB-CANDIDATE-SPEC-INTAKE-FOLLOW-ONS` | **backlog items recorded** (added 2026-04-30 S324; pre-approved by owner per six AskUserQuestion approvals in S323 captured at `bridge/gtkb-candidate-spec-intake-six-statements-2026-04-29-005.md` §2 and archived as DELIB-S323-GOV-{TRANSCRIPT-DELIBERATION-CAPTURE,IMPL-PROPOSAL-SCOPE-LINKAGE,TESTS-BEFORE-IMPL-AND-VERIFIED,CHAT-DERIVED-SPEC-APPROVAL,RELEASE-PLATFORM-INVENTORY-TWO-STAGE,RELEASE-MANIFEST-README}-APPROVAL) | Each follow-on creates one canonical governance spec via its own implementation bridge. Per Codex `-006` F2 closure: the candidate-spec-intake bridge claims "follow-on backlog item recorded" (not "follow-on bridge filed") as its verification condition; this row is the recorded backlog. Five follow-ons (compose with in-flight work where noted): (a) `gtkb-formal-artifact-da-source-required-impl` for `GOV-TRANSCRIPT-DELIBERATION-CAPTURE-001` (parent: all; net-new); (b) `gtkb-impl-proposal-scope-linkage-impl` for `GOV-IMPL-PROPOSAL-SCOPE-LINKAGE-001` (parent: all; composes with `gtkb-spec-lifecycle-schema-2026-04-29` Slice 4); (c) `gtkb-tests-before-impl-and-verified-impl` for `GOV-TESTS-BEFORE-IMPL-AND-VERIFIED-001` (parent: all; composes with `gtkb-platform-spec-coverage-verified-runner-2026-04-29` already in flight); (d) `gtkb-chat-derived-spec-approval-impl` for `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` (parent: all; composes with `gtkb-membase-effective-use-recovery-2026-04-29` Slices B + C); (e) `gtkb-release-engineering-spec-coverage` combined for `GOV-RELEASE-PLATFORM-INVENTORY-TWO-STAGE-001` + `GOV-RELEASE-MANIFEST-README-001` (parent: gtkb each; net-new combined scoping with two impl slices). **Sequencing:** independent of each other; may be filed in any order over subsequent sessions. **Each follow-on, when filed, must:** (1) cite the corresponding DELIB-S323-*-APPROVAL row as approval evidence; (2) on canonical spec insertion, run `gt deliberations link --deliberation-id <DELIB-ID> --spec-id <SPEC-ID>` to materialize the relational linkage that was deferred at archival time; (3) carry its own per-bridge formal-artifact-approval packet for the canonical spec creation. | Next: file each follow-on impl bridge per the standard NEW → review → GO → impl → post-impl → VERIFIED protocol. Owner pre-approval covers proceeding through the five bridges autonomously per work-list contract. |
| 22 | `GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT` | **gap recorded; not yet filed** (added 2026-04-30 S324 per owner direction after smart-poller status check) | Owner observation S324: smart-poller is no longer runaway; kind-aware terminal-status filtering is active and behaving correctly (Codex side: 0 actionable, no spawn; Prime side: 19 raw → 4 terminal filtered → 15 dispatch-eligible). However, **Prime auto-spawn still has false positives for ambiguous/plan-level GO entries**. Latest Prime dispatches selected stale plan-level architecture/parent-thread GOs (e.g., umbrella scoping bridges that authorize sub-bridges, not direct implementation work) rather than implementable GOs. The dispatched Prime sessions correctly stood down without acting, so the cost is wasted spawn tokens, not wasted implementation. **Evidence:** `groundtruth-kb/src/groundtruth_kb/bridge/notify.py:198` derives `dispatchable` by status + classification; `groundtruth-kb/scripts/bridge_poller_runner.py:395` filters on `dispatchable` before signature/spawn; current dispatch state at `.gtkb-state/bridge-poller/dispatch-state.json` shows `prime: raw_pending_count=19, filtered_terminal_count=4, pending_count=15` (status-level filtering working) but `pending_count=15` still includes parent/plan-level GOs that are not actionable for Prime. **Proposed direction:** extend the kind-aware classification with a `bridge_kind`/`umbrella_for` input dimension that distinguishes (a) implementable GO (proposal authorizes specific files/changes), (b) umbrella/parent GO (proposal authorizes sub-bridges), (c) plan/architecture GO (proposal documents an approach decision). Read `bridge_kind:` from proposal metadata or pattern-match document name (e.g., `*-architecture-*`, `*-umbrella-*`, parent threads with sub-bridges). Treat (b) and (c) as non-dispatchable for Prime. **Sequencing:** non-blocking; proceeds in parallel with other smart-poller follow-on work. **Composition:** extends existing kind-aware routing in `gtkb-bridge-poller-001` umbrella; not a separate program. | Next: file scoping bridge `bridge/gtkb-bridge-poller-prime-classification-refinement-2026-MM-DD-001.md` upstream in `groundtruth-kb` (the runner code lives there). Adopters consume via `gt project upgrade` after upstream VERIFIED. Owner has NOT pre-approved bridge filing; this row is gap-recording only per S324 AskUserQuestion answer "Record as work_list row only". |
| 23 | `GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR` | **future-work intent recorded; trigger-conditional** (added 2026-04-30 S324 per owner direction) | Owner observation S324: "The implementation of the bridge and the smart-poller seems excessively complicated. We will have to look at refactoring it once it is actually fully functional." **Trigger condition:** "once it is actually fully functional" — refactoring should not proceed until the remaining functional gaps are closed (notably row 22 Prime classification gap and any others surfaced by ongoing operation). Refactoring while functional gaps remain risks fixing the wrong abstraction. **Specific complexity surfaces observed during S324** (non-exhaustive): (a) 5+ state files in `.gtkb-state/bridge-poller/` (`dispatch-state.json`, `audit.jsonl`, `checkpoint.json`, `dispatch-runs/`, `notifications/`, `bridge-poller-runner.lock`); (b) 4+ interacting hooks (`formal-artifact-approval-gate.py`, `bridge-compliance-gate.py`, `owner-decision-tracker.py`, `spec-event-surfacer.py`); (c) multiple stacked classification dimensions (status × kind × parent-vs-implementable × harness); (d) bridge file versioning duplicated as `bridge/INDEX.md` state; (e) cross-harness coordination through the file system; (f) daemon + VBS launcher + lock file + signature-dedup as separate mechanisms each addressing a specific historical incident. **Why it accumulated:** each mechanism was added in response to a real failure (S290 silent outage, S308 OS-poller token regression, S321 phantom VERIFIED, S322 concurrent ledger writes, etc.). The accumulation overshoots what a deterministic service would express. Aligns with `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: repetitive plumbing AI sessions reconstruct from rule files + hook code + example packets, where AI substantive contribution is < 20% of total work. **Sketch of decomposition (non-binding; rough draft only):** a single **bridge runtime service** with one state file, one dispatch decision function, one classification table, one notification surface; hooks become thin policy enforcers calling into that service rather than each maintaining their own state. Could collapse ~5 of the current concerns into one. **Sequencing:** trigger-conditional. Until trigger fires, this row is a recording of intent + observed surfaces. **Composition:** likely subsumes or replaces several existing GTKB-BRIDGE-POLLER-* and GTKB-GOV-* rows depending on the refactor scope chosen at proposal time. Not yet decomposed into slices. | Next: monitor functional-gap status (row 22 + future findings). When the owner judges the system "fully functional," file a scoping bridge proposing the refactor scope and decomposition. Owner has NOT pre-approved bridge filing; this row is intent-recording only per S324 AskUserQuestion answer "Add a work_list row now". |
| 24 | `GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY` | **DEFERRED 2026-05-02 S326 after 4 NO-GOs; re-scoping needed.** Codex `-006` F1: the helper API proposed in `bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-{001,003,005}.md` is the same governance-bypassing raw-status-inserter design rejected in the prior 2026-04-30 thread (`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-{001..004}.md`); I missed that thread because INDEX entry was at lines 78-82. **More important:** `scripts/gtkb_bridge_writer.py` already implements atomic INDEX write + role/transition validation (lines 22-27, 152-176). The right path is NOT another helper — it's migrating callers to that existing tool. Re-scope when picked up: (a) cite both prior NO-GO threads; (b) propose caller-migration scope (replace direct `Edit` of INDEX with `gtkb_bridge_writer.py` calls), not a new helper; (c) include role-slot disambiguation per prior threads. Meaningful re-scope, not a quick revision. | Owner directive S324 (after observed pattern): "Promoting INDEX edits exclusively through the bridge-propose helper (which has 2-attempt retry semantics) would eliminate this pattern. Adding helper-mediated INDEX update for VERIFIED line additions is a candidate hygiene item. ... This should be tracked and completed at the next opportunity." **Gap:** `.claude/skills/bridge-propose/helpers/write_bridge.py:propose_bridge()` only handles the initial `Document: <slug>` + `NEW: bridge/<slug>-001.md` insertion case (atomic file-first write + INDEX retry-safe insertion with 2-attempt retry budget). Prime also routinely needs to insert REVISED, NEW (post-impl), and audit-trail-landing GO/NO-GO/VERIFIED lines into existing entries; currently this is done via direct `Edit` tool calls on `bridge/INDEX.md`, which race the smart-poller's atomic `os.replace` and lose every time the poller writes within the read→write window. Empirical evidence S324: at least 5 retroactive INDEX commits this session due to lost races (`a87fc24f`, `3efa04b3`, `2deb054e`, `f83a66a5`-followup, `2e995711`); each costs ~1 commit + 1 quality-gate run + diagnostic tokens. **Proposed surface:** extend `write_bridge.py` with a sibling function (e.g., `add_status_line(topic_slug, status, version, *, mode='abort')`) that uses the same atomic-temp-file + 2-attempt-retry pattern as `propose_bridge()`'s INDEX update phase. Call sites: bridge-propose skill, Prime's REVISED/post-impl filings, and (where appropriate) Prime-side audit-trail landings of LO verdicts. VERIFIED line additions by Codex's runner remain unchanged (smart-poller-runner has its own atomic write). **Sequencing:** non-blocking; "next opportunity" per owner direction. Most natural insertion: pair with any subsequent bridge-propose skill enhancement, or as a standalone tiny bridge thread when a low-token-cost session window opens. **Risk:** Low. Pure additive helper extension; no behavior change to existing `propose_bridge()`. | Next: file scoping bridge `bridge/gtkb-bridge-propose-helper-index-parity-2026-MM-DD-001.md` when next opportunity arises. Owner has pre-approved at the program-level ("This should be tracked and completed at the next opportunity"); standard NEW → review → GO → impl → post-impl → VERIFIED bridge cycle still applies. |
| 25 | `GTKB-REHEARSE-DRIVER-WAVE-BANNER-COSMETIC` | **cosmetic follow-on; tracked from VERIFIED non-blocker** (added 2026-05-01 S325) | Codex non-blocking observation in `bridge/gtkb-isolation-016-phase8-wave3-execution-012.md` §"Non-Blocking Observation": `scripts/rehearse_isolation.py:283` always prints `rehearse_isolation: Wave 2 dispatch` even when `--phase db-filter-dryrun` (Wave 3) is selected. The actual Wave 3 manifest validation works correctly (T18+T19 prove this); only the banner text is stale. **Fix scope:** one-line change replacing literal "Wave 2" with f"Wave {wave}" where `wave` is the value already computed by `_wave_for_phase(args.phase)` at line 260. **Risk:** Trivial. Pure display-text change; no behavior impact. **Sequencing:** non-blocking; bundle with any future rehearse_isolation.py edit. | File `bridge/gtkb-rehearse-driver-wave-banner-cosmetic-2026-MM-DD-001.md` when natural opportunity arises (e.g., bundled with `GTKB-ROLE-ENHANCEMENT` post-isolation work or a focused cleanup pass). Owner has implicit pre-approval via the work_list autonomous-execution clause; standard bridge cycle applies. |
| 26 | `GTKB-ISOLATION-017-SLICE-2.5` (registry rationale schema extension) | **carry-forward from Slice 2 GO -004** (added 2026-05-02 S326) | Codex GO at `bridge/gtkb-isolation-017-slice2-registry-isolation-004.md` §"Carry-forward condition": "Slice 2.5 rationale/migration-note work must be recorded after Slice 2 is VERIFIED, as promised in the proposal, so the deferred scoping acceptance items remain visible before final GTKB-ISOLATION-017 closeout." **Scope:** extend `OwnershipMeta` in `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` with an optional `notes: str = ""` field; update the loader (`_extract_ownership_block`), the TOML rows (`templates/managed-artifacts.toml` ~36 file-class rows), the `_to_ownership_record()` projection in `ownership.py`, and schema validation. After landing, T2 (rationale discipline: every gt-kb-managed/gt-kb-scaffolded record has non-empty notes) and T3 (migration-note discipline: ownership flips require paired notes citing prior value) become implementable and would be added in this same slice. Per `gtkb-isolation-017-slice2-registry-isolation-003.md` §"Replacement To `-001` Schema Survey table" — these were deferred from Slice 2 because FILE-class records currently project to `OwnershipRecord(notes="")` and `OwnershipMeta` has no notes field. **Sequencing:** non-blocking parallel to Slices 3-8; should land before GTKB-ISOLATION-017 closeout so the original Phase 9 acceptance items (per-entry rationale + migration-note discipline from scoping `-003` lines 84, 87) are not dropped on the floor. **Composition:** owns its own bridge thread; standard NEW → review → GO → impl → post-impl → VERIFIED cycle. Estimated envelope: ~80 LOC source (schema field + loader + projection + validation) + ~120 LOC tests (T2 + T3 + 2-3 schema invariants) + per-row TOML notes additions (rationale capture for ~36 rows). | Next: file scoping bridge `bridge/gtkb-isolation-017-slice2-5-rationale-schema-extension-001.md` after Slice 2 VERIFIED. Owner pre-approval via work_list autonomous-execution clause; standard bridge cycle applies. |
| 27 | `GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH` | **owner-directed 2026-05-02 S326; source-of-truth migration proposed; not yet filed** | Owner clarified that the current backlog is not adequately formal. This item supersedes/absorbs the markdown-linter direction in `GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1` and the snapshot-only harvest direction in `GTKB-GOV-004` where those would preserve fragmentation. Required direction: implement a canonical append-only/versioned MemBase `backlog_items` table with unique backlog item name, unique sub-project name, creation/update timestamps, long-form relevance/intent description, related deliberation query/relations, specifications known at creation time, sequential implementation-order priority, bridge threads, dependencies, acceptance/regression visibility, completion evidence, and status lifecycle. `memory/work_list.md` becomes generated view or temporary compatibility surface, not the canonical source. Sequencing: high priority after the active `GTKB-ISOLATION-017` -> `GTKB-ISOLATION-018` -> `GTKB-ISOLATION-019` critical path unless owner explicitly elevates. | Next: file `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-001.md` before implementation. Proposal must include schema DDL, migration plan from current `memory/work_list.md`, generated-view behavior, CLI/doctor/dashboard/startup integration, bridge citation behavior, ordering/reorder semantics, and regression tests proving no backlog items are lost or split across sources. |
| 31 | `GTKB-ISOLATION-017-SLICE-5.5` (overlay refresh + disposability + chroma-regen API) | **owner-directed 2026-05-03 S328; deferred to follow-on slice via scoping-revision DELIB** | Owner-approved partial deferral per `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE` v1 (formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-03-isolation-017-slice5-overlay-scope.json`). Originally bound to Slice 5 by scoping bridge `-003` lines 143-145; partially revised via this DELIB. **Stale-detection (1 of 3) ships in Slice 5 REVISED-1** as `test_overlay_stale_detection.py` wrapping Slice 1 check #9. **Refresh + disposability (2 of 3) deferred here** because the underlying user-facing chroma-regeneration API does not exist in `groundtruth-kb/src/` (probe at S328 returned 0 matches for `def.*chroma_regen` / `def.*reindex` outside the rehearsal-driver lane at `scripts/rehearse/_chromadb_regen.py`). **Sequencing:** deferred beyond v0.7.0-rc1 unless owner elevates at Slice 8 acceptance-gate time per the cited DELIB. **Composition:** ships (a) `groundtruth_kb.project.chroma.regenerate(target)` library API or `gt project chroma regenerate` CLI command wrapping the rehearsal-lane logic for adopter use; (b) `test_overlay_refresh.py` exercising the regen API on a clean adopter; (c) `test_overlay_disposability.py` exercising delete-cache → regenerate → state-equivalence. Estimated envelope: ~150 LOC source + ~150 LOC tests. | Next when unblocked or elevated: file scoping bridge `bridge/gtkb-isolation-017-slice-5-5-overlay-tests-001.md` upstream (chroma-regen API lives in `groundtruth-kb/src/`). Standard NEW → review → GO → impl → post-impl → VERIFIED bridge cycle. |
| 30 | `GTKB-STARTUP-REFRACTOR-001` (Consolidate role startup and glossary loading) | **owner-directed 2026-05-02 S328 P1; deferred under feature freeze** | Owner-directed P1 backlog item per S328 message: "Completed the advisory review and wrote the report here: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STARTUP-PROCEDURE-REFRACTOR-ADVISORY-2026-05-02-23-52.md`." Advisory authored by Loyal Opposition (Codex). **Eight key findings from the advisory:** (1) Generated startup service still does not surface the new glossary-load requirement; (2) Review-mode/control-map bootstrap files are stale; (3) `.claude/settings.local.json` carries legacy paths, broad write permissions, and a literal credential-bearing command; (4) Startup rules are duplicated across too many surfaces; (5) Loyal Opposition bridge-processing approval language conflicts with standing authorization; (6) Prime Builder needs a compact startup overlay, not Codex-branded bootstrap reuse; (7) Skills/commands/plugins need a role-capability manifest; (8) Glossary review should proceed one term at a time. **Authority:** advisory report at the cited path (gitignored per CODEX-INSIGHT-DROPBOX convention; verified `git diff --check` clean per owner). **Sequencing:** P1 priority within the post-ISOLATION-017 queue. Currently deferred under the work_list TOP feature freeze ("No new governance scope work until ISOLATION-017 Slice 8 VERIFIED") — startup-procedure refactor is governance scope. Owner may elevate above the freeze if release-path judgment shifts; the cited finding (3) about credential exposure in `settings.local.json` may justify earlier elevation. **Coupling:** coordinate with `GTKB-SYSTEMS-TERMINOLOGY-MAP-001` so startup refactor does not create a second, competing list of routine systems/tools. | Next when unblocked or elevated: (1) read the full advisory report; (2) file scoping bridge `bridge/gtkb-startup-refractor-001-001.md` consolidating the 8 findings into per-finding remediation slices; (3) per finding (8), structure glossary review as one-term-at-a-time owner-decision packets; (4) per `GTKB-SYSTEMS-TERMINOLOGY-MAP-001`, consume the canonical artifact/interface map when building startup tool/system disclosure; (5) per finding (3), credential scrub in `.claude/settings.local.json` may require an immediate hotfix bridge if exposure is judged release-blocking. Standard NEW → review → GO → impl → post-impl → VERIFIED bridge cycle for each remediation slice. |
| 29 | `GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING` | **CLOSED 2026-05-04 S331 by Sub-slice A of GTKB-GOV-AUQ-ENFORCEMENT-STACK** | Closed by `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-007.md` (Codex GO at -008). Implementation: (a) negative lookbehind `(?<!["` + chr(96) + `])` added to all 7 prose patterns to suppress quoted/backtick-bounded literals; (b) `awaiting_input` and `standing_by_for` split into `_q` (interrogative) and `_first_person` (active-wait) variants so factual status statements without `?` or 1st-person construct no longer match; (c) `PROSE_FALSE_POSITIVE_GUARDS` extended with self-reference + bridge-metadata suppressors; (d) `_scan_prose_decisions()` modified for per-match local-window guard scope; (e) `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` env override removed from `.claude/settings.local.json`; (f) 17 new tests in `groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py` covering all 7 patterns + guard scope + DECISION-0001/0002 quoted-FP corpus. | Done; remove this row at next wrap. |
| 28 | `GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL` | **owner-directed 2026-05-02 S328; deferred under feature freeze; DELIB captured** | Owner directive captured verbatim at `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` (groundtruth.db, formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-02-role-intent-sentinel-delib.json`). Triggered by S328 session-open role-confusion latency: Prime Builder confirmed `prime-builder` role only after owner asked, despite the canonical record being durable in `harness-state/claude/operating-role.md`. **Proposed pattern:** non-authoritative role-intent sentinel as HTML-comment block at the top of `bridge/INDEX.md`, mirroring the canonical harness-state/<harness>/operating-role.md durable records. Sentinel is read at session start (which already reads bridge/INDEX.md per CLAUDE.md "Session Start: Bridge Index Scan") + mechanically verified against canonical files; disagreement fails startup loud; sentinel never overrides canonical. **Owner-stated 5-rule contract** (verbatim from directive): (1) read bridge/INDEX.md sentinel; (2) read both harness-local role files; (3) fail startup if sentinel disagrees with either source file; (4) require disclosure to say which source was used; (5) never allow sentinel to override harness-local durable record. **Design pattern observation:** checksum-sentinel pattern — mirror of canonical state placed at high-traffic read point with mechanical agree-or-fail verification (cf. DNS SOA serial mirrored at top of every record). Load-bearing rule is rule 5; without it the sentinel becomes a competing authority. **Owner-stated risk if implemented poorly** (verbatim): "the bridge index becomes overloaded as both queue and role-control plane, and agents may start trusting a stale header over the actual role file." **Sequencing:** **DEFERRED under freeze** per work_list TOP directive ("No new governance scope work until ISOLATION-017 Slice 8 VERIFIED"); this proposal is governance-scope (role-control plane + startup contract). Owner may elevate above freeze if release-critical judgment changes; the current S328 session-open incident was not release-blocking. | Next when unblocked or elevated: (1) file scoping bridge `bridge/gtkb-bridge-index-role-intent-sentinel-001.md` proposing the 5-rule mechanical-check contract + tests covering disagreement-fails-startup and rule-5 invariant (sentinel cannot override canonical); (2) Slice 1 — sentinel HTML-comment block at top of bridge/INDEX.md + manual maintenance contract documented in CLAUDE.md "Session Start" section; (3) Slice 2 — mechanical startup check in `scripts/session_self_initialization.py` reading sentinel + both canonical files + failing-loud on disagreement, emitting cited-source line in disclosure; (4) Slice 3 — doctor check `_check_bridge_index_role_sentinel` for ongoing drift detection, integrate into release-readiness. No spec promotion at archive time; spec promotion (e.g., new GOV/DCL pair governing the sentinel contract) requires owner-visible approval per `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` at implementation-bridge filing time. |
| 32 | `GTKB-AI-ASSISTED-DELIVERY-MATURITY-MODEL` | **owner-directed 2026-05-03 S330; advisory captured; not yet filed** | Owner asked Loyal Opposition to formalize the revised Claude Code maturity-model discussion as a deliberation/advisory for Prime Builder while avoiding sunk-cost bias. Advisory report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AI-ASSISTED-DELIVERY-MATURITY-MODEL-ADVISORY-2026-05-03-11-35.md`. The proposed model reframes maturity as layered delivery capability: prompting, project memory, task protocols, specs/evals, hooks/guards, orchestration, and governance/release evidence. **Risk:** GT-KB may over-invest in orchestration or role ceremony without proving that lower layers reliably improve production delivery outcomes. **Sequencing:** discussion/advisory track; no implementation until Prime Builder/owner decide whether this should become a GT-KB evaluation lens, roadmap input, or no-op. | Next: Prime Builder reviews the advisory, comments on whether it should become a formal deliberation/roadmap input, and either files a bridge proposal for a lightweight maturity-evaluation artifact or records an explicit no-op/supersession decision. |
| 33 | `GTKB-ENV-INVENTORY-001` (Harness and development environment inventory) | **owner-directed 2026-05-03 S330; advisory captured; backlog addition approved** | Owner directed that GT-KB should know and publish its baseline harness/development environment for release and should mechanically enforce updating the inventory artifact when creating the installable package. Advisory report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-DEV-ENVIRONMENT-INVENTORY-ADVISORY-2026-05-03-11-53.md`. Scope includes OS version, harness versions, tool/plugin/skill/hook/MCP capability inventory, release-safe public baseline, private redacted local inventory, role-by-harness compatibility matrix, and release-gate enforcement. **Related:** coordinates with `GTKB-STARTUP-REFRACTOR-001` finding (7) and `GTKB-SYSTEMS-TERMINOLOGY-MAP-001`, but is distinct because it inventories environment/capability facts rather than term resolution. | Next when unblocked or elevated: file `bridge/gtkb-env-inventory-001-001.md` proposing the canonical inventory artifact schema, collection command, redaction policy, generated release-baseline output, startup/dashboard visibility, and release-gate tests proving the inventory is current before packaging. |
| 43 | `GTKB-ENV-INVENTORY-DRIFT-CONTROL-001` (Inventory baseline drift control for protected artifacts) | **owner-directed 2026-05-06; follow-on to `GTKB-ENV-INVENTORY-001`; backlog addition and implementation proposal requested** | Owner confirmed the inventory is intended to support change-control drift identification: regenerate or verify inventory, compare against the committed baseline, evaluate confirmed changes, and flag unconfirmed drift for further work, documentation review, or application compatibility tests. Scope is a mechanical protected-artifact registry plus normalized inventory-diff enforcement for checkin/release gates. Per-CRUD enforcement may provide early warnings where hooks exist, but the hard source of truth should be checkin/CI/release diff enforcement because not every artifact mutation flows through a single CRUD service. **Coupling:** depends on the public/private inventory split from `GTKB-ENV-INVENTORY-001`; overlaps AUQ/policy-gate work only at action-gate integration points and should not become a general-purpose owner-decision framework. | Next: Loyal Opposition review of `bridge/gtkb-env-inventory-drift-control-001-001.md`. If `GO`, implement a protected-artifact registry, normalized drift checker, pre-commit/checkin and release-gate integration, and tests proving protected artifact changes cannot bypass an inventory baseline update or explicit drift classification. |
| 44 | `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001` (Apply ADR/DCL logic as clause-level review tests) | **owner-elevated top priority 2026-05-06; Loyal Opposition advisory captured; not yet filed as bridge proposal** | Owner directed that agents should determine which ADR/DCL records could apply to a proposal, then apply each one-by-one as a test of the implementation proposal and later verification evidence. Advisory report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/ADR-DCL-CLAUSE-TEST-ENFORCEMENT-ADVISORY-2026-05-06.md`. Current bridge preflight checks required citation coverage from `config/governance/spec-applicability.toml`, but it does not parse every ADR/DCL into enforceable clauses or prove semantic satisfaction. Proposed direction: add a clause model for ADR/DCLs, deterministic applicability discovery, `must_apply` / `may_apply` classification, a Loyal Opposition clause-test matrix for `GO`, and executed clause evidence for `VERIFIED`. This also records the pattern that Mike can work with Loyal Opposition to explore alternatives and have the results preserved as deliberations, advisory reports, and backlog items for Prime Builder. | Next: Prime Builder reads the advisory and files `bridge/gtkb-adr-dcl-clause-test-enforcement-001-001.md` proposing the clause schema/registry, candidate discovery command, verdict-template changes, preflight or companion checker, high-risk ADR/DCL fixture set, and tests proving missing applicable clause coverage prevents `GO`/`VERIFIED` without explicit owner waiver. |
| 34 | `GTKB-SYSTEMS-TERMINOLOGY-MAP-001` (Canonical artifact/interface names and startup operating surface map) | **implemented 2026-05-06; post-implementation report filed at `bridge/gtkb-systems-terminology-map-001-003.md`; awaiting Loyal Opposition `VERIFIED` or `NO-GO`** | Owner identified recurring agent confusion around terms that name specific systems or artifacts, especially ambiguous terms like "backlog." Existing backlog coverage is partial: `GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH` handles backlog consolidation, `GTKB-STARTUP-REFRACTOR-001` handles startup mechanics, and `GTKB-ENV-INVENTORY-001` handles harness/dev-environment inventory. Implementation adds a canonical map of routine GT-KB artifacts/interfaces, their accepted alternate names, authority, locations, access methods, mutation permissions, generated-vs-authoritative status, startup/dashboard visibility, and deterministic resolver. **First reconciliation case:** the map resolves the current "backlog" contradiction between `memory/work_list.md`, future MemBase `backlog_items`, MemBase `work_items`, `bridge/INDEX.md`, and dashboard/startup summaries. | Next: Loyal Opposition review of `bridge/gtkb-systems-terminology-map-001-003.md`. If `VERIFIED`, commit the implementation; if `NO-GO`, revise the implementation report or code as directed. |
| 39 | `GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001` (External resource identity registry and confusion audit) | **implemented 2026-05-06; post-implementation report filed at `bridge/gtkb-resource-reference-disambiguation-001-003.md`; awaiting Loyal Opposition `VERIFIED` or `NO-GO`** | Owner directed that all external resources be mapped to URLs and/or identities so AI agents reliably interpret user input and historical references, avoiding duplicate or erroneous resources becoming entangled. Codex Loyal Opposition created seed registry `.claude/rules/project-resource-aliases.toml`, companion `memory/project_external_resource_registry.md`, and advisory report `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/RESOURCE-REFERENCE-CONFUSION-CANDIDATES-2026-05-04.md`. Implementation promoted the governed registry to `config/agent-control/project-resource-aliases.toml`, retained the `.claude/rules/` file as a pointer, added deterministic resolution/drift/CI-evidence checks, and surfaced compact registry health through operating-state/dashboard. **Sequencing:** now waiting for Loyal Opposition verification before commit/drop. **Coupling:** overlaps `GTKB-SYSTEMS-TERMINOLOGY-MAP-001`, `GTKB-ENV-INVENTORY-001`, startup refactor, release-readiness gates, and resource URL/identity doctor checks. | Next: Loyal Opposition review of `bridge/gtkb-resource-reference-disambiguation-001-003.md`. If `VERIFIED`, commit the implementation; if `NO-GO`, revise the implementation report or code as directed. |
| 35 | `AGENT-RED-RUFF-CLEANUP-001` (Application-side ruff resolution; Agent Red product code) | **revised proposal filed 2026-05-06 at `bridge/agent-red-ruff-cleanup-001-003.md`; awaiting Loyal Opposition `GO` or `NO-GO`** | Slice 8's B2 (full-repo ruff resolution) was narrowed to `groundtruth-kb/` only because the ruff baseline probe found 1,943 issues in Agent Red product code (`tests/`: 1,076; `scripts/`: 824; `src/`: 15; misc: 28) versus 29 in `groundtruth-kb/`. Per the operating-model platform/application distinction, Agent Red application cleanup belongs to Agent Red's own release-hardening arc, not v0.7.0-rc1's GT-KB platform release. The revised proposal addresses Loyal Opposition NO-GO findings by adding `Owner Decisions / Input` and narrowing this current bridge item to GT-KB read-only planning/baseline work only. **Distribution by rule (top 10):** I001 (886, unsorted-imports, auto-fixable), UP017 (264, datetime-timezone-utc, auto-fixable), F541 (241, f-string-missing-placeholders, auto-fixable), F401 (104, unused-import, auto-fixable), SIM117 (88, multiple-with-statements, auto-fixable), E402 (87, module-import-not-at-top-of-file, manual), B007 (55, unused-loop-control-variable, manual), UP015 (45, redundant-open-modes, auto-fixable), F841 (36, unused-variable, manual), E401 (22, multiple-imports-on-one-line, auto-fixable). 1,653 of 1,943 (85%) auto-fixable; 290 require manual judgment. **Sequencing:** live Agent Red source cleanup remains blocked until Mike explicitly scopes a session to Agent Red or provides the concrete Agent Red repository target. | Next: Loyal Opposition review of `bridge/agent-red-ruff-cleanup-001-003.md`. If `GO`, implement only a GT-KB read-only planning/baseline artifact; do not run formatters or tests in Agent Red source. |
| 37 | `GTKB-CI-COVERAGE-FOR-PLATFORM-001` (Add CI coverage for `groundtruth-kb/tests/`) | **deferred from Slice 8.5 -002 F2 disposition per `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER` (2026-05-03 S330); targeted for v0.7.0 GA** | Slice 8.5 surfaced that `python-tests.yml` runs Agent Red product tests (`tests/unit`, `tests/multi_tenant`, etc.) and is path-filtered to `src/**` + `tests/**`; it does NOT run `groundtruth-kb/tests/`. Owner waived python-tests.yml as a required-green workflow for v0.7.0-rc1 (rc1 is GT-KB platform-only; Agent Red product test coverage is not under test). For v0.7.0 GA, GT-KB platform tests should have CI coverage so future GT-KB-only commits get green CI evidence. **Two implementation options:** (A) extend `release-candidate-gate.yml` to add a `groundtruth-kb-tests` job that runs `cd groundtruth-kb && python -m pytest tests/`; path filter `groundtruth-kb/**` would need to be added (it currently triggers via `scripts/**` only when the verifier is touched); (B) create a new `groundtruth-kb-tests.yml` workflow with path filter `groundtruth-kb/**` and a dedicated pytest job. Option A is smaller change; Option B is cleaner long-term separation. **Sequencing:** v0.7.0 GA target; not blocking v0.7.0-rc1 tag (Slice 8.5 owner waiver covers). Owner may elevate timing if GT-KB-only commits become routine before GA. **Risk:** Low. Pure CI-extension; no source impact. **Coupling:** related to row 36 (pip-install adopter UX) — both are GA-deferred CI/UX improvements for the GT-KB platform. | Next when picked up: file `bridge/gtkb-ci-coverage-for-platform-001-001.md` proposing Option A or B + workflow YAML diff + verification that `groundtruth-kb/tests/` runs green in CI on a GT-KB-only commit. After Codex GO + impl + VERIFIED, the python-tests.yml waiver in `DELIB-S330-...-PYTHON-TESTS-WAIVER` can be lifted (the new workflow becomes the required-green for GT-KB-only commits). |
| 38 | `GTKB-EVALUATION-MODULE-RESTORATION-001` (Restore or refactor evaluation/ module references) | **deferred from Slice 8.6 Phase 3-G disposition per `DELIB-S330-SLICE-8-6-PHASE-3-G-EVALUATION-MODULE-WAIVER` (2026-05-04 S330)** | At S320 commit `c9fc7216` (Phase 1 isolation cleanup), the `evaluation/` module at repo root was deleted as part of stale-dir cleanup. Two performance baseline tests in `tests/performance/test_concurrent_tenants.py` still import from `evaluation.pilots.quality_pilot`: `test_perf_03_golden_dataset_loads_under_100ms` + `test_perf_04_quality_pilot_evaluation_under_500ms`. Both fail with `ModuleNotFoundError: No module named 'evaluation'`. Latent failure since S320; surfaced in Slice 8.6 Phase 3-G when the cumulative commit chain re-triggered Python Tests workflow (path filter matched `tests/**`). Both tests now `@pytest.mark.skip(reason="waived per DELIB-...")` to unblock Slice 8.6 acceptance. **Two implementation options:** (A) restore the `evaluation/` module from git history (commit `c9fc7216` parent); inspect what was deleted; restore only the parts needed by these 2 tests; (B) rewrite the 2 tests to mock or inline the dataset/pilot logic (avoid restoring deleted infrastructure). Option B aligns with the S320 isolation intent (evaluation/ was deleted because it was app-non-specific or stale); Option A reverts that decision. Owner choice required. | Next when picked up: file `bridge/gtkb-evaluation-module-restoration-001-001.md` proposing Option A or B; if A, scope-bound restoration of only what tests need + verification; if B, rewrite tests + remove skip markers + waiver retirement. After Codex GO + impl + VERIFIED, the `DELIB-S330-...-EVALUATION-MODULE-WAIVER` retires and tests run green in Python Tests integrations shard. |
| 36 | `GTKB-PIP-INSTALL-ADOPTER-UX-001` (Simplify `gt project init` UX for pip-installed wheels) | **deferred from Slice 8 -008 NO-GO disposition per `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK` (2026-05-03 S330); targeted for v0.7.0 GA** | Slice 8 -008 NO-GO surfaced a real product UX gap: under Slice 4 isolation enforcement, an adopter who runs `pip install groundtruth-kb` and then `gt project init MyApp` cannot succeed. The reason: (a) `_GT_KB_HOST_ROOT` is computed from `Path(scaffold.py).resolve().parents[4]` which for an installed wheel resolves to the venv root (a meaningless path for an adopter wanting to scaffold a project elsewhere); (b) `_resolve_gt_kb_host_root` requires `--gt-kb-root` to equal the install-derived `_GT_KB_HOST_ROOT`, so adopters cannot override it; (c) `_validate_application_target` requires the target's parent to equal `<host_root>/applications`. The working command shape for rc1 is awkward: discover host_root via subprocess, mkdir `<host_root>/applications/<name>`, then `gt project init <name> --gt-kb-root <host_root> --dir <host_root>/applications/<name>`. **Proposed fix for v0.7.0 GA:** modify `scaffold.py:41` `_GT_KB_HOST_ROOT` derivation to detect editable-vs-installed (heuristic: `"site-packages" in Path(__file__).resolve().parts`); for installed wheels, default `_GT_KB_HOST_ROOT` to CWD or accept any `--gt-kb-root` without the strict-equality check. Editable installs keep the strict-equality check (preserves the existing `E:/GT-KB`-rooted contract). New CLI shapes to consider: `gt project init MyApp --here` (use CWD as host_root) or `gt project init MyApp --target <abs-path>` (place anywhere with no host_root). **Sequencing:** v0.7.0 GA target; not blocking v0.7.0-rc1 tag (the rc ships with the awkward but documented working command shape). Owner may elevate above the GA timeline if rc adopter feedback signals UX is too friction-heavy. **Risk:** Modifying `_GT_KB_HOST_ROOT` derivation touches Slice 4 (VERIFIED) source; needs careful test coverage to ensure editable-install behavior is preserved. The clean-adopter test suite in Slice 5 must pass against the new behavior; tests in `groundtruth-kb/tests/` that monkeypatch `_GT_KB_HOST_ROOT` must continue to work (e.g., `test_scaffold_provider_templates::test_cli_default_providers_succeed`). | Next when picked up: file `bridge/gtkb-pip-install-adopter-ux-001-001.md` proposing the editable-vs-installed detection heuristic + relaxed `_resolve_gt_kb_host_root` for installed wheels + new CLI shapes (`--here` / `--target`) + updated announcement/release-notes documenting the simpler UX. After Codex GO + impl + VERIFIED, the announcement's "rc1 limitation" note can be removed. Slice 5 clean-adopter test suite must extend with installed-wheel coverage to prevent regression. |
| 40 | `GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001` (Anchor-only in-source citation conventions + orphan-citation doctor invariant) | **owner-directed 2026-05-04 S332; backlog addition explicitly requested ("get to it later"); not yet filed** | Owner asked Prime Builder for a proposal on whether to embed richer provenance/intent knowledge in source comments given ChromaDB-backed semantic search availability for the Deliberation Archive. Prime Builder's recommendation (this session): **anchor-only in source** (stable refs: `# Enforces: <SPEC-ID> v<N>`, `# See bridge/<thread>-<NNN>.md for approved scope`, `# Source: DELIB-<ID>`) with **rationale + history living in DA records** where ChromaDB indexes them. Rationale: comments aren't currently in ChromaDB unless harvested into DA, so rich in-source rationale becomes a parallel un-indexed shadow with maintenance burden and cite-rot risk. Anchors-only gives bidirectional discoverability (ChromaDB can find DELIBs from code paths and code paths from DELIBs) without duplication. **Proposed implementation:** (1) document the anchor-only convention in CLAUDE.md or a new `.claude/rules/in-source-provenance.md`; (2) add a `gt project doctor` invariant `_check_in_source_citation_freshness` that scans tracked source for `DELIB-NNNN` and `bridge/<thread>-NNN.md` references and verifies each cited record exists in MemBase / on disk; orphan citations get flagged. **Sequencing:** non-blocking; not on release path; owner explicitly deferred ("get to it later"). **Coupling:** complements `GTKB-SYSTEMS-TERMINOLOGY-MAP-001` (canonical artifact names) and `.claude/rules/deliberation-protocol.md` line 81 (citation format rule). | Next when picked up: file `bridge/gtkb-in-source-provenance-anchors-001-001.md` proposing the convention rule + doctor invariant + a one-time backfill scan reporting any current orphan citations across the codebase. After Codex GO + impl + VERIFIED, the convention is documented and the invariant prevents regression. |
| 41 | `GTKB-OPS-CURRENT-STATE-MONITORING-001` (Deterministic `gt status` / dashboard / startup operating-state reporting) | **Codex advisory delivered 2026-05-04 S332 as bridge NO-GO `gtkb-ops-current-state-monitoring-advisory-2026-05-04-001.md`; Loyal-Opposition advisory report at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-OPERATING-STATE-MONITORING-ADVISORY-2026-05-04.md`; not yet filed as implementation proposal** | Codex Loyal Opposition observation: GT-KB lacks a deterministic current-operating-state surface for the components owner expects to see at startup and on demand: ChromaDB, SQLite/MemBase, dashboard runtime, smart-poller/bridge, hooks, startup/governance state. Status is currently assembled by agents from scattered files, doctor output, process lists, dashboard refresh state, bridge state, memory rows — exactly the kind of repetitive operational reconstruction that should be code per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`. Existing component probes exist (e.g., `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1192-1208` smart-poller activation paths + 60-second freshness threshold; doctor.py:1211-1348 retrieval/chromadb checks) but aren't unified into an operating-state surface. **Codex's NO-GO is intentional:** it's a visible bridge action telling Prime to file a normal implementation proposal, not implementation approval. **Proposed scope:** (1) `gt status` CLI emitting a single canonical operating-state object (JSON or markdown) covering all 6 component classes; (2) dashboard integration of the same operating-state object; (3) startup disclosure surface using the same data (avoid duplicate per-surface assembly). **Sequencing:** non-blocking for v0.7.0-rc1; aligns with `GTKB-DASHBOARD-002` Slice 2.3 integration work and `GTKB-STARTUP-ENHANCEMENTS` action-tray surface. Owner may elevate priority if startup or dashboard observability becomes a release blocker. | Next when picked up: read full advisory at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-OPERATING-STATE-MONITORING-ADVISORY-2026-05-04.md`; file `bridge/gtkb-ops-current-state-monitoring-001-001.md` proposing the canonical operating-state schema + 6-component probe assembly + `gt status` CLI + dashboard/startup integration + tests. After Codex GO + impl + VERIFIED, the bridge advisory at `gtkb-ops-current-state-monitoring-advisory-2026-05-04` can be retired (its NO-GO purpose was to surface the gap, not block work). |
| 42 | `GTKB-AUQ-POLICY-GATES-001` (Central deterministic AUQ policy gate with thin hook/CLI/dashboard adapters) | **Codex advisory delivered 2026-05-04 S332 as bridge NO-GO `gtkb-auq-policy-gate-backlog-advisory-2026-05-04-001.md`; Loyal-Opposition advisory report at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AUQ-HOOK-POLICY-GATE-ADVISORY-2026-05-04.md`; not yet filed as implementation proposal** | Codex Loyal Opposition observation framed by S332 owner directives: (a) "AskUserQuestion is valuable because it opens a dedicated Claude Chrome UI dialog that is hard to miss"; (b) "consider wider use of hooks plus AskUserQuestion for commit, push, tests, build/deploy to staging, production deploy, operating-state probes, requirements updates, and other tracked actions"; (c) "consider hooks that prevent accidental GT-KB artifact changes while working in a GT-KB-hosted application scope, such as Agent Red"; (d) "identify lower-token or easier-to-maintain alternatives." **Codex recommendation:** do NOT scatter AUQ-backed action gating across bespoke per-action hooks; build a central deterministic policy gate (`gt policy check --action <action> --scope <scope> --paths <paths> --json`) with canonical outcomes ALLOW/WARN/ASK/DENY (per `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` lifecycle pattern); thin per-action hook/CLI/dashboard adapters call the same policy engine. Initial action classes: commit, push, test, build, deploy-staging, deploy-production, status/probe, requirements/specification update, GT-KB platform writes while active scope is application. **Lower-cost controls also recommended for consideration:** structural read-only boundaries or installed-package consumption for GT-KB platform code during application-scope sessions; Git branch protection + required reviews; deployment environment approvals for production; `gt` command wrappers for commit/push/deploy/spec-update/status; thin hooks calling the same policy engine; short-lived approval receipts to prevent repeated AUQ prompts for one already-approved action. **Constraint:** do not use LLM/API classifiers for this backlog item (per S332 NO-LLM directive). **Sequencing:** non-blocking for current release path; per-action gating implementations should wait for this central policy gate to land. **Coupling:** complements Sub-slice F's release-metric gates (which add release-candidate-gate enforcement; AUQ-POLICY-GATES adds per-action gating breadth); references `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` and `DELIB-0878` (isolation authority-matrix planning). | Next when picked up: read full advisory at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AUQ-HOOK-POLICY-GATE-ADVISORY-2026-05-04.md`; file `bridge/gtkb-auq-policy-gates-001-001.md` proposing the policy registry schema, active-scope model, path-ownership mapping, approval-receipt format, first hook/wrapper adapters (likely starting with the commit and push action classes), and tests for ALLOW/WARN/ASK/DENY outcomes + Agent Red application-scope protection. After Codex GO + impl + VERIFIED, the bridge advisory at `gtkb-auq-policy-gate-backlog-advisory-2026-05-04` can be retired. |

**Completed in S308 (2026-04-25), removed from active table:**

- `GTKB-ISOLATION-015` Slice 2 — **CORRECTED 2026-04-25 later in S308:** prior INDEX claim of VERIFIED at `-006` was based on phantom-INDEX entries for files that never existed; source-level verification (per Codex `gtkb-isolation-016-phase8-rehearsal-implementation-004` F4) confirmed the implementation never landed. Reconciled at `bridge/gtkb-isolation-015-slice2-work-subject-set-002` (re-opened as not-implemented). Slice 2 typed `work_subject.set` / `work_subject.rollback` control-plane operations remain a future work item with `-001` as the specification basis. Does NOT block ISOLATION-016 Phase 8 rehearsal (per `-016-impl-005` §1.2 — sub-scripts don't call typed control-plane API).
- `GTKB-DASHBOARD-002` Slice 2.1 (visibility) — VERIFIED at `gtkb-dashboard-industry-alignment-slice2a-visibility-008` (closed terminal).
- `GTKB-DORA-001` — VERIFIED at `gtkb-dora-telemetry-foundation-008` (closed terminal; unblocks DORA-001b).
- `gtkb-slice2b-metrics-index-reconciliation` — VERIFIED at `-008` (INDEX hygiene; closed terminal).
- `gtkb-root-directory-migration-post-verify` — VERIFIED at `-019` (closed terminal).
- `halt-os-pollers-token-regression` — VERIFIED at `-002` (operational change record; closed terminal).
- `canonical-deploy-pipeline-scaling-enforcement` (WI-3031 closure) — VERIFIED at `-012` (canonical-path scaling enforcement; commits `417f187b` + `db1a63fd`; KB record updated to v4 resolved; LO log row marked Resolved 2026-04-25 (S308)). Production runtime validation pending next release window.

Standing governance items (`GTKB-GOV-001` through `GTKB-GOV-010`, minus
`-007` PAUSED and `-009` VERIFIED) and `GTKB-CORE-001` / `GTKB-MASS-001`
remain below. They are not mechanically sequenced against the items above
until `GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1` lands the structured
field block with typed `depends_on`.

**Known tracking-freshness caveat:** "TOP" as a priority value is
currently overloaded across ~10 entries below (many are historical artifacts
from earlier sessions). The 5-row table above reflects the current actionable
ordering; the file-wide priority text is not trustworthy until
`GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1` mechanically validates it.

---

## Completed During Current Session

### GTKB-GOV-000 — DONE — Implement strict formal artifact approval gate with scoped auto-approval mode

**Priority:** TOP. Owner decision `DELIB-0835` and formal records `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, `ADR-ARTIFACT-FORMALIZATION-GATE-001`, and `DCL-ARTIFACT-APPROVAL-HOOK-001` require GT-KB artifact formalization to bias toward strict review, full native-format display, approval or acknowledgement evidence, and rich auditability.

**Outcome:** implemented a tracked `PreToolUse` hook at `.claude/hooks/formal-artifact-approval-gate.py`, registered it in `.claude/settings.json`, added manual approval and scoped auto-approval packet validation, and wired `tests/hooks/test_formal_artifact_approval_gate.py` into `scripts/release_candidate_gate.py`.

**Regression visibility:** `tests/hooks/test_formal_artifact_approval_gate.py` covers blocked unapproved writes, approved writes, scoped auto-approval writes, and rejection of auto-approval flows that omit transcript capture. `tests/scripts/test_groundtruth_governance_adoption.py` verifies the hook registration, MemBase records, work-list record, and release-candidate gate wiring.

**Verification:** formal records promoted to `verified` after implementation. Approval packet: `.groundtruth/formal-artifact-approvals/2026-04-20-strict-gov-enforcement-verified.json`.

### GTKB-GOV-000A — DONE — Add Codex hook parity package and Windows-aware verifier

**Priority:** TOP follow-on to `GTKB-GOV-000`. Owner accepted the Codex runtime limitation that hooks are currently disabled on Windows, while directing that strict GOV enforcement still be made mechanically active to the extent possible for Codex.

**Outcome:** added tracked Codex hook intent at `.codex/config.toml` and `.codex/hooks.json`, registering the same formal artifact approval `PreToolUse` gate for future/non-Windows Codex hook runtimes. Added `scripts/check_codex_hook_parity.py` as the mechanically active Windows fallback verifier.

**Regression visibility:** `tests/scripts/test_codex_hook_parity.py` verifies the Codex package and documents the Windows runtime limitation. `tests/scripts/test_groundtruth_governance_adoption.py` verifies the package is present, not git-ignored, and wired into the release-candidate gate. `scripts/release_candidate_gate.py` now runs `check_codex_hook_parity.py` before the governance pytest lane.

**Decision capture:** owner acknowledgement recorded as `DELIB-0836`. Approval packet: `.groundtruth/formal-artifact-approvals/2026-04-20-codex-hook-parity-decision.json`.

### GTKB-GOV-000B — DONE — Audit and formalize session decisions across artifacts

**Priority:** TOP follow-on to owner request. Owner asked to ensure all decisions, directives, and principles in this session were identified and applied to their respective artifacts.

**Outcome:** added `DELIB-0837` and MemBase records `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`, `GOV-GTKB-ADOPTION-ENFORCEMENT-001`, `GOV-ACTING-PRIME-BUILDER-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`, `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`, `GOV-AGENT-RED-GTKB-CONFORMANCE-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, and `GOV-SESSION-FORMALIZATION-AUDIT-001`.

**Regression visibility:** `tests/scripts/test_groundtruth_governance_adoption.py` verifies the new MemBase records, the DELIB-to-spec mapping, the audit entry, and rule references.

**Approval packet:** `.groundtruth/formal-artifact-approvals/2026-04-20-session-formalization-audit-batch.json`.

### GTKB-GOV-000C — DONE — Formalize standing backlog as governed cross-session work authority

**Priority:** TOP follow-on to owner approval. Owner approved formalizing the standing backlog and asked whether the formalized artifact will be treated in the same way specifications are.

**Outcome:** added `DELIB-0838` and MemBase records `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001`, and `DCL-STANDING-BACKLOG-SCHEMA-001`.

**Clarification:** the standing backlog governance contract is treated like other formal GT-KB specifications: represented in MemBase, linked to DA, cited in rules, regression-tested, and release-gate visible. Individual backlog entries remain queue/work items unless separately promoted to GOV, SPEC, PB, ADR, DCL, or another formal artifact type.

**Regression visibility:** `tests/scripts/test_groundtruth_governance_adoption.py` verifies the standing backlog records, the `DELIB-0838` decision, rule references, and work-list continuity evidence.

**Approval packet:** `.groundtruth/formal-artifact-approvals/2026-04-20-standing-backlog-formalization.json`.

### GTKB-GOV-000D - DONE - Formalize artifact-oriented development governance

**Priority:** TOP follow-on to owner approval. Owner directive 2026-04-22: default system behavior should be oriented toward artifacts and plans, with the AI biased toward capturing deliberations, adding planned work to the standing backlog, treating agreed plans as artifacts, and starting sessions by examining artifact state.

**Outcome:** added `DELIB-0874` and MemBase records `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`. Updated `independent-progress-assessments/CODEX-STANDING-PRIORITIES.md` with a session-loaded Artifact-Oriented Governance directive covering capture thresholds, lifecycle states, and non-intrusive confirmation flows.

**Clarification:** artifact-oriented governance is a default interpretation stance, not permission to mutate formal artifacts without approval. Brainstorming remains lightweight until it becomes a decision, plan, requirement, risk, procedure, review finding, or accepted future work. Formal GOV, SPEC, PB, ADR, DCL, and Deliberation Archive mutations still require applicable approval evidence.

**Regression visibility:** `tests/scripts/test_groundtruth_governance_adoption.py` verifies the new MemBase records, `DELIB-0874`, the approval packet, the standing-priorities directive, and this work-list continuity evidence.

**Approval packet:** `.groundtruth/formal-artifact-approvals/2026-04-22-artifact-oriented-governance.json`.

### GTKB-GOV-011 - DONE - Implement session self-initialization dashboard, startup disclosure, and proactive wrap-up

**Priority:** TOP. Owner directive `DELIB-0840` and records `GOV-SESSION-SELF-INITIALIZATION-001`, `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`, `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`, and `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` required fresh sessions to self-initialize with explicit role, governance, dashboard, priority, and token-budget context. Owner directive `DELIB-0841` and records `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001`, `PB-SESSION-WRAP-UP-PROACTIVE-001`, and `DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001` added proactive session wrap-up guidance and priority engagement.

**Outcome:** implemented `scripts/session_self_initialization.py`, which generates a startup model, live local dashboard (`docs/gtkb-dashboard/index.html`), dashboard data (`docs/gtkb-dashboard/dashboard-data.json`), startup report, proactive wrap-up report, and bounded time-series KPI history (`memory/gtkb-dashboard-history.json`). `.claude/settings.json` now registers `SessionStart` and `Stop` lifecycle hooks. `.codex/hooks.json` carries matching Codex hook intent, with Windows runtime limitations covered by `scripts/check_codex_hook_parity.py`. The startup report presents the role being assumed, enabled skills, plug-ins, directives, hooks, governance stance, live project dashboard link, three top priority user actions, and token-budget reduction options. The proactive wrap-up report draws attention to priorities across project dimensions and points to `.claude/skills/kb-session-wrap/SKILL.md` without performing mutating wrap-up operations automatically.

**Regression visibility:** `tests/scripts/test_session_self_initialization.py` verifies startup disclosure text, dashboard-link availability, KPI inventory, top-three action selection, wrap-up reporting, and token-budget/reduction-option reporting. `tests/scripts/test_codex_hook_parity.py`, `tests/scripts/test_groundtruth_governance_adoption.py`, and `tests/scripts/test_release_candidate_gate.py` verify lifecycle hook intent and release-gate wiring. Approval packets: `.groundtruth/formal-artifact-approvals/2026-04-20-session-lifecycle-engagement-principle.json` and `.groundtruth/formal-artifact-approvals/2026-04-20-gtkb-gov-011-implementation-verification.json`.

### AR-DASH-001 — DONE — Correct dashboard scope to Agent Red product state

**Priority:** TOP. Owner clarification 2026-04-20: the dashboard should show the Agent Red project, with GT-KB treated retroactively as pre-existing implementation infrastructure used to implement Agent Red.

**Outcome:** updated `scripts/session_self_initialization.py` so the generated dashboard is titled "Agent Red Project Dashboard", carries `agent_red_v1` scope metadata, filters primary KPI counts through an Agent Red scope classifier, excludes GT-KB framework/upstream work from primary dashboard metrics, and reports GT-KB only in a subordinate "Implementation Infrastructure" section. Historical Agent Red project rows are backfilled from `groundtruth.db` version history with `scope_confidence="agent_red_inferred"`; current live rows use `scope_confidence="agent_red_current_heuristic"`. Mixed-scope pre-existing dashboard history rows are no longer reused.

**Historical harvest:** `memory/gtkb-dashboard-history.json` now contains Agent Red-scoped historical rows from `2026-02-26` through the current session. The rendered dashboard currently exposes 56 session points and 54 calendar-day points. Historical rows intentionally leave unavailable operational metrics as `None` rather than inventing drift, release-blocker, or bridge-contention history.

**Regression visibility:** `tests/scripts/test_session_self_initialization.py` asserts the Agent Red title, scope metadata, historical backfill rows, infrastructure/product separation, and exclusion of upstream GT-KB dashboard priorities. `tests/scripts/test_groundtruth_governance_adoption.py` continues to verify dashboard artifact presence and release-gate wiring.

**Verification:** `python -m pytest tests\scripts\test_session_self_initialization.py -q --tb=short` passed. `python -m pytest tests\scripts\test_groundtruth_governance_adoption.py -q --tb=short` passed with one unrelated ChromaDB deprecation warning. Browser runtime verification found 6 tiles, 5 signals, 8 sparklines, 2 composite lines, 160 heatmap cells, 56 session points, 54 calendar-day points, and 0 page errors.

**Formal artifact note:** no DA/GOV/SPEC/PB/ADR/DCL records were created or mutated in this implementation pass. The owner clarification is enforced in code, tests, dashboard data, and this standing-backlog record; formal canonical promotion remains available as a separate approval-gated follow-up if desired.

### GTKB-GOV-005 - DONE - Reconcile live bridge GO/NO-GO entries into standing backlog dispositions

**Priority:** TOP. Standing backlog source audit found six latest bridge entries with `GO` or `NO-GO` status in `bridge/INDEX.md`.

**Outcome:** reconciled every live bridge entry into an explicit standing-backlog disposition without mutating the file-bridge audit trail:

- `gtkb-azure-cicd-gates` `GO` is assigned to `GTKB-GOV-009` for execution or owner-approved supersession/deferment in the `groundtruth-kb` checkout.
- `agent-red-bridge-dispatcher-deferral-enforcement` `GO` is scope-only and is superseded by the follow-on implementation thread tracked by `GTKB-GOV-008`; it does not authorize direct implementation.
- `agent-red-bridge-dispatcher-deferral-enforcement-implementation` `NO-GO` is assigned to `GTKB-GOV-008` for a revised implementation bridge covering shared parser status recognition, guard tests, generated-wrapper verification, and owner-decision gates.
- `commercial-readiness-spec-1831-startup-wiring` `NO-GO` is assigned to `GTKB-GOV-007` for a revised bridge that seeds the alert-engine/provider-admin rule store or formally revises the spec.
- `commercial-readiness-spec-verification` `NO-GO` is assigned to `GTKB-GOV-007` for a revised SPEC-1832 bridge covering post-auth middleware 403 audit, SPEC-1837 archival semantics, and exact post-apply KB assertions.
- `commercial-readiness-spec-1833-ready-propagation` `NO-GO` is assigned to `GTKB-GOV-007` for a revised bridge requiring exact HTTP 503 readiness behavior, cache-isolated route tests, and no premature `verified` promotion while concurrency remains unresolved.

**Evidence report:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STANDING-BACKLOG-BRIDGE-DISPOSITIONS-2026-04-20.md`.

**Regression visibility:** `scripts/audit_standing_backlog_sources.py` still reports the live bridge entries by design; child backlog items `GTKB-GOV-007`, `GTKB-GOV-008`, and `GTKB-GOV-009` preserve actionability until the underlying bridge threads are revised, executed, deferred, or superseded.

### GTKB-GOV-006 - DONE - Close Agent Red release-readiness blocker list

**Priority:** TOP. `memory/release-readiness.md` listed governed release blockers that had to be closed, explicitly deferred with owner approval, or superseded before a production GO.

**Outcome:** owner-disposition blockers for credential lifecycle, secret-history purge, and release-branch provenance were closed. The commercial durability scope question was resolved as in-scope, then implemented with durable commercial-state persistence and secure tenant backup/restore support for Shopify, Stripe, integration framework state, and action-executor HITL state.

**Regression visibility:** `scripts/release_candidate_gate.py` now includes the commercial durability tests. Local non-deploying release gate passed with frontend skipped: `python scripts/release_candidate_gate.py --skip-frontend`.

### GTKB-GOV-012 - DONE - Enforce Prime Builder / Loyal Opposition proposal and verification gates across GT-KB applications

**Priority:** TOP for the 2026-04-22 Prime Builder session. Owner directive 2026-04-22 required the established Prime Builder / Loyal Opposition development pattern to be mechanically enforced or strongly encouraged for all applications developed with GT-KB.

**Outcome:** the portable file-bridge proposal/gate slice completed the governed bridge lifecycle: proposal `bridge/gtkb-proposal-verification-gates-001.md`, Loyal Opposition `GO` in `bridge/gtkb-proposal-verification-gates-002.md`, post-implementation reports in `bridge/gtkb-proposal-verification-gates-003.md` and `bridge/gtkb-proposal-verification-gates-005.md`, a `NO-GO` in `bridge/gtkb-proposal-verification-gates-004.md`, and final `VERIFIED` in `bridge/gtkb-proposal-verification-gates-006.md`.

**Post-verification spec-status review:** `gt bridge spec-review --scope protocol` now surfaces the affected governance records `GOV-GTKB-ADOPTION-ENFORCEMENT-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`, `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`, and `GOV-AGENT-RED-GTKB-CONFORMANCE-001`. Existing MemBase and regression-test evidence show those records are already `verified`; no formal GOV/SPEC mutation was made in this backlog cleanup pass.

**Evidence report:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-GOV-012-POST-VERIFIED-STATUS-REVIEW-2026-04-22.md`.

**Residual gate visibility:** `gt bridge gate --require-verified --scope protocol --json` still fails on older protocol entries with latest non-verified states. Current notable continuation items include `gtkb-mass-adoption-first-commit-package` awaiting renewed Loyal Opposition review and `gtkb-core-spec-intake` at scope GO. `gtkb-azure-cicd-gates` is now `VERIFIED` at `bridge/gtkb-azure-cicd-gates-010.md`, and `gtkb-core-spec-intake-phase3b-answer` is also `VERIFIED`. These are not regressions in `GTKB-GOV-012`; the remaining non-verified entries are bridge-continuation work items for `GTKB-MASS-001` and `GTKB-CORE-001`.

## Active Items

**Owner directive 2026-04-23:** treat the overall application/GT-KB isolation
program as the current standing-backlog priority. Until `GTKB-ISOLATION-019`
is complete or the owner explicitly pauses or reprioritizes the program,
non-isolation items below are deferred except for bridge or governance work
that directly unblocks the isolation program.

### GTKB-ISOLATION-010 - DONE - Execute Phase 7 foundation slice: work-subject state and resolved-root guardrails

**Status:** DONE 2026-04-23 (S305). **VERIFIED** at
`bridge/gtkb-work-subject-root-enforcement-implementation-020.md`. Superseded
by `GTKB-ISOLATION-015` which continues Phase 7 integration beyond the
foundation slice.

**Priority (historical):** TOP. This was the first concrete execution slice
already entered on the live bridge in
`bridge/gtkb-work-subject-root-enforcement-implementation-001.md`,
and it should lead the queue because later environment, service, control-plane,
overlay, and migration work need stable work-subject state, root
classification, and startup/hook language first.

**Required outcome:** obtain bridge GO, implement, verify, and Loyal
Opposition-verify the narrow Phase 7 foundation slice: canonical
`.claude/session/work-subject.json` state, one-window legacy migration and
alias support, resolved-root classification for application/current-repo
bridge-governance/GT-KB product targets, subject-aware mutation guardrails, and
startup/hook/report language changes from `focus` to `work subject`.

**Regression visibility:** targeted checks in
`tests/hooks/test_workstream_focus.py`,
`tests/scripts/test_session_self_initialization.py`, and
`tests/scripts/test_codex_hook_parity.py`, followed by broader `tests/hooks/`
and `tests/scripts/` lanes once the focused slice is green.

### GTKB-ISOLATION-011 - DONE - Implement Phase 3 environment boundary baseline

**Status:** DONE 2026-04-23 (S305). **VERIFIED**; Windows drive-letter
compose-bind fix landed via REVISED-1. See
`bridge/gtkb-environment-boundary-baseline-implementation-*` thread.

**Priority (historical):** TOP after `GTKB-ISOLATION-010`.

**Bridge status:** originally proposal filed in
`bridge/gtkb-environment-boundary-baseline-implementation-001.md`;
subsequently GO'd, implemented, and VERIFIED through the REVISED cycle.

**Required outcome:** submit, obtain GO for, and land the first Phase 3
execution slice: static environment policy checker, root identity probe, safe
devcontainer/Codespaces defaults, Docker context hardening, CI subject-scope
audit, dependency-mode reporting, and bounded escape-hatch schema.

**Regression visibility:** tests must reject broad mounts, Docker socket usage,
privileged containers, GT-KB product credentials in app lanes, root-escape
writes, and unlabeled product-release claims from app CI.

### GTKB-ISOLATION-012 - DONE - Implement Phase 4 scoped GT-KB service boundary baseline

**Status:** DONE 2026-04-23 (S305). **VERIFIED** at
`bridge/gtkb-scoped-service-boundary-baseline-implementation-010.md`
(narrowed to single `dashboard.summary.read` op after 4 NO-GO rounds).

**Priority (historical):** TOP after `GTKB-ISOLATION-011`.

**Required outcome:** submit, obtain GO for, and land the first Phase 4
execution slice: scoped operation schema, app-scoped GT-KB client,
service-side GOV guard reuse, read-only dashboard summary path, DA/MemBase
app-scope layer, governed release/deployment request flow, offline/stale
protocol, and doctor/preflight checks that remove raw GT-KB DB/root access from
ordinary app flows.

**Regression visibility:** tests must prove app-subject sessions cannot perform
product-scope writes, cannot emit combined app/product green claims, and cannot
fall back silently to raw DB/root authority.

### GTKB-ISOLATION-013 - DONE - Implement Phase 5 control-plane registry and safe projection baseline

**Status:** DONE 2026-04-23 (S305). **VERIFIED** — Phase 5 first slice
landed (three-operation typed registry). Later typed
`work_subject.set` handler still open under `GTKB-ISOLATION-015` Slice 2.

**Priority (historical):** TOP after `GTKB-ISOLATION-012`.

**Required outcome:** submit, obtain GO for, and land the first Phase 5
execution slice: typed operation registry, dry-run/diff/audit/rollback
foundation, app-root allowlisted `dashboard.refresh`, bounded Markdown
operations, projection preview/apply staging, harness topology registry,
role-slot-aware bridge/control records, and pause/resume/restart request
records.

**Regression visibility:** tests must reject arbitrary path/script execution,
path traversal, unmanaged projection changes, stale counterpart topology, and
bridge writes from the wrong role slot.

### GTKB-ISOLATION-014 - DONE - Implement Phase 6 overlay and snapshot baseline

**Status:** DONE 2026-04-23 (S305). **VERIFIED** at
`bridge/gtkb-session-overlay-baseline-implementation-006.md` (required an
ImportError-not-ModuleNotFoundError fix for direct-script SessionStart).

**Priority (historical):** TOP after `GTKB-ISOLATION-013`.

**Required outcome:** submit, obtain GO for, and land the first Phase 6
execution slice: overlay manifest library, overlay builder, startup/dashboard
visibility, scanner exclusions, projection preview overlay integration,
promotion dry-run/apply through the typed registry, and retention cleanup
confined to validated overlay roots.

**Regression visibility:** tests must prove overlays are non-authoritative,
source-hashed, stale-detecting, excluded from canonical scanners by default,
and unable to copy credentials or raw `groundtruth.db` into session context.

### GTKB-ISOLATION-015 - Complete full Phase 7 work-subject/root enforcement (Slice 1 VERIFIED; Slice 2 remaining)

**Status:** **Slice 1 VERIFIED** 2026-04-24 (S306) at
`bridge/gtkb-isolation-015-phase7-full-integration-016.md`. **Slice 2
NOT IMPLEMENTED** — prior tracking claimed Slice 2 was implemented 2026-04-24 (S307)
and VERIFIED at phantom `-006`, but source-level verification 2026-04-25 (S308)
per Codex `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-004.md` F4
confirmed the implementation never landed in this checkout (control_plane_registry.py
exposes only 3 ops with no `work_subject.set/rollback`; no source files for
`work_subject_*`; no git history). Slice 2 thread re-opened as not-implemented
at `bridge/gtkb-isolation-015-slice2-work-subject-set-002.md`. `GTKB-ISOLATION-015`
closes only when Slice 2 typed control-plane operations are genuinely implemented
in a future session — `-001` of that thread remains the specification basis.

**Priority:** Future work item. Slice 1 already VERIFIED at `gtkb-isolation-015-phase7-full-integration-016`; Slice 2 typed control-plane operations remain not-implemented per the `gtkb-isolation-015-slice2-work-subject-set-002` reconciliation. **Does NOT unblock `GTKB-ISOLATION-016`** — Phase 8 rehearsal is already actionable on Slice 1 alone (per `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-005.md` §1.2; rehearsal sub-scripts don't call typed control-plane API). This WI closes only when Slice 2 is genuinely implemented in a future session.

**Required outcome:** after the Phase 3 through Phase 6 execution slices land,
submit and execute the remaining Phase 7 integration work: subject-labeled
startup/dashboard/readiness/test outputs, typed control-plane
subject/mode/session controls, overlay-aware but non-authoritative context
handling, bridge live-state writer/validator safety, Codex/Claude parity
checks, and upstream GT-KB delivery requirements for clean adopters.

**Regression visibility:** tests must prove subject-labeled outputs, live
`bridge/INDEX.md` fresh-read authority, invalid transition rejection, stale
counterpart detection, and split application vs GT-KB verification lanes.

**Slice split (established at bridge `gtkb-isolation-015-phase7-full-integration-007` REVISED-3, GO at `-008`):**

- **Slice 1 (Agent Red Tooling) — delivered via this bridge:** §A
  subject-labeled startup / readiness / test outputs, §B bridge live-state
  writer/validator (`scripts/gtkb_bridge_writer.py`), §C overlay-aware
  startup status, §E multi-harness counterpart-state detection. Post-impl
  report filed as `bridge/gtkb-isolation-015-phase7-full-integration-009.md`.
- **Slice 2 (Typed control-plane handler) — NOT IMPLEMENTED, future work:**
  §D typed `work_subject.set` control-plane handler with input schema,
  timing semantics, dry-run, apply, audit, and rollback. **Specification:**
  `bridge/gtkb-isolation-015-slice2-work-subject-set-001.md` (the only
  on-disk version of that thread; see the `-002` reconciliation for
  full context on the prior phantom-INDEX VERIFIED that was retracted).
  When Slice 2 is genuinely implemented and Codex VERIFIES it in a
  future session, `GTKB-ISOLATION-015` will close at that point — NOT
  earlier, and NOT against the retracted phantom `-006`.
- **§F (Upstream GT-KB clean-adopter delivery) — routed to
  `GTKB-ISOLATION-017`:** AGENTS.md template, hook templates, and
  `gt project init/upgrade/doctor` packaging are delivered through the
  existing Phase 9 adopter-packaging backlog item. No new bridge or WI
  required.

**Execution note:** the completed Phase 1 through Phase 7 planning records
remain below as the governing design baseline for the execution queue above.

### GTKB-GOV-OWNER-DECISION-SURFACING - Mechanical surfacing of pending owner decisions (Agent Red-local first)

**Priority:** TOP. Filed 2026-04-25 (S308) per owner directive ("yields immediate benefit"). Implementation proposal at `bridge/gtkb-gov-owner-decision-surfacing-slice1-001.md`; awaits Codex GO.

**Problem statement:** During long interactive sessions, owner-decision asks get lost in message flow. Three failure modes observed in S308:

1. **In-prose decision burial:** Prime writes "Want me to X or Y?" in a paragraph; owner reads past it; no UI affordance distinguishes it from informational prose.
2. **Late chain-discovery:** A multi-section proposal flags 7 decisions in §3; owner doesn't realize each is a hard gate; Prime "stands by" without owner awareness.
3. **Cross-session loss:** Pending decisions live in transient chat, not in any durable surface that SessionStart hook reads.

The existing `AskUserQuestion` tool fixes #1 *only when Prime remembers to use it*. Nothing prevents prose reversion. Nothing surfaces pending state across context-switches or sessions.

**Required outcome:** durable `memory/pending-owner-decisions.md` file (YAML-frontmatter list), `.claude/hooks/owner-decision-tracker.py` hook with three modes (Stop / SessionStart / UserPromptSubmit), settings.json registration, regression tests in release-candidate gate. Stop mode scans for AskUserQuestion + prose anti-patterns; SessionStart mode displays unresolved decisions in startup disclosure; UserPromptSubmit mode emits gentle nudge if pending decisions exist and owner message doesn't reference them.

**Routing:** Agent Red-local first (per `.claude/hooks/formal-artifact-approval-gate.py` precedent). Hook contract may be promoted upstream to `groundtruth-kb` if/when it proves out, mirroring the GTKB-GOV-PROPOSAL-STANDARDS upstream-routing pattern.

**Regression visibility:** test file in release-candidate gate covers AskUserQuestion detection, prose anti-pattern detection, file-format validation, SessionStart surfacing, UserPromptSubmit nudging, resolved-decisions move-to-history.

**Dependencies:** none beyond existing hook infrastructure. Uses the same Stop/SessionStart/UserPromptSubmit hook events already registered in `.claude/settings.json`.

**Out of scope (Slice 1):** prose-pattern detection refinement (regex precision will iterate based on false-positive rate); dashboard tile for pending decisions (separate future slice); upstream promotion of the hook (depends on Slice 1 proving the contract).

### GTKB-STARTUP-ENHANCEMENTS - Session-start redesign: from collect-render-emit to curated priming

**Priority:** medium-high. **Filed 2026-04-25 (S309).** **Revised 2026-04-25 (S309)** with architectural vision after owner directive expanding scope from incremental enhancement to a redesign aiming to reduce complexity + cost while making startup more useful and project-oriented. **Scope:** "Startup enhancements" per owner.

**Six Priming Objectives (owner directive):**

1. Prime collaboration protocol (bridge + Implementation Proposal → Review → Implementation Report → Verify cycle)
2. Prime canonical glossary (system terms; GT-KB / IDP / adopter / harness / role)
3. Prime active code-quality and artifact-rigor ADRs (currently load-bearing, not full historical set)
4. Prime correct user-interaction affordances (when AskUserQuestion required; spec/backlog-change ceremony; visible decision surfacing)
5. Present project-relevant prioritized options biased toward boilerplate work that fills known/anticipated gaps in project specifications
6. Present order-of-work planning choices with status of ongoing projects

**Mission:** inform → affirm procedures → guide. Right answers, right time. Orderly, iterative, comprehensive.

**Source evidence:** S309 conversation evaluating session-start architecture (token consumption, hooks, project-state pipeline, priority-task surfacing, LO/PB branching, reliability contract). Concrete diagnoses: ~28-34K token prelude with ~40% redundancy; 8 rule files with overlapping content; MEMORY.md silently truncated past 24.4KB ceiling; 13-option focus menu is a flat catalogue with no spec-gap bias; two parallel rendering pipelines (Codex JSON contract vs Claude raw markdown); forward-compat dead wrappers in `.codex/hooks.json`; owner-decision-tracker reactive only with documented false-positive class.

**Target architecture: Six Primers + Project Snapshot + Action Tray**

| Surface | Purpose | Token budget |
|---|---|---|
| P1 Bridge protocol primer | proposal → review → impl → verify cycle, statuses, when bridge is/isn't required | ~400 |
| P2 Canonical glossary primer | GT-KB / IDP / adopter / harness / role / Prime Builder / Loyal Opposition | ~300 |
| P3 Active-ADR primer | KB-derived: specs with `is_session_priming=True` flag (owner-curated seed list) | ~600 |
| P4 Interaction-affordances primer | when AskUserQuestion required; spec-change / backlog-change ceremony; visible-decision surfacing | ~500 |
| P5 Role-conditional primer (PB or LO) | role-specific authority + restrictions; consolidates 3 current rule files | ~400 |
| P6 Wrap-up triggers primer | accepted wrap-up commands; first-prompt-discard semantics | ~150 |
| **Six-primer subtotal** | | **~2,350** |
| Project Snapshot | top 5 in-flight slices status; outstanding owner decisions; KPI deltas vs last session | ~500 |
| Action Tray | 3 ordered work proposals with `id`, `title`, `unblocks`, `blocked-by`, `spec-gap status`, `suggested ceremony`. Replaces the 13-option focus catalogue. | ~600 |
| Trimmed MEMORY.md | one-line index entries (down from ~15K) | ~6,000 |
| CLAUDE.md (dedup'd) | governance core; references primers by ID | ~3,500 |
| AGENTS.md (dedup'd) | Codex equivalent; references primers by ID | ~2,500 |
| **TOTAL** | | **~15,500 (50% reduction from ~30K)** |

**Owner-chosen architectural decisions (2026-04-25 S309):**

- **Rule-file consolidation: FULL.** Merge `bridge-essential.md` + `file-bridge-protocol.md` + `codex-review-gate.md` into one bridge primer. Merge `prime-builder-role.md` + `acting-prime-builder.md` + `loyal-opposition.md` into one role-conditional primer. Net: 8 rule files → 3. External references to the old paths are accepted breakage; will catch via release-gate test.
- **Starting phase: P1 quick wins.** Lowest risk, fastest token recovery (~9K), proves the iterative-slice model.

**Phased delivery (each phase = one bridge):**

| Phase | What lands | Token impact | Risk |
|---|---|---|---|
| **P1 Quick wins** *(starting here)* | Trim `MEMORY.md` to one-line index entries; atomic dashboard write (`os.replace` from `.tmp`); `MEMORY.md` size ceiling test in release-gate; fix Codex `owner-decision-tracker-ups.cmd` wrapper (or remove unreferenced entry). All 4 sub-items independent. | −9K tokens | low |
| **P2 Claude startup-freshness contract** | Port Codex `_valid_session_start_payload()` to Claude side; explicit fallback-context generator on validation failure. | reliability win | low |
| **P3 Six-primer registry** | New `scripts/session_primers.py` with primer registry + by-id query API + per-primer token-budget tests. Primers cached by content hash. | restructure (no net change yet) | medium |
| **P4 Migrate rule files into primer registry** | Full consolidation per owner decision: 8 rule files → 3 (bridge, role-conditional, interaction). CLAUDE.md + AGENTS.md reference primers by ID. | −5K tokens | medium |
| **P5 Active-ADR primer** | KB schema: add `is_session_priming` boolean to specs; primer queries it. Owner curates initial set (seed: ADR-CODEX-HOOK-PARITY-FALLBACK-001, ADR-ARTIFACT-FORMALIZATION-GATE-001, ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001, ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 + the new code-quality CQ rules once GO'd). | quality-positive | medium |
| **P6 Action tray with spec-gap bias** | Replace 13-option focus menu with 3-option dependency-aware tray. New collector: `specs WHERE status='specified' AND id NOT IN (implemented_by query)` to surface up to 2 spec gaps. Structured `depends_on` chain rendered. | −2K tokens; quality-positive | medium |
| **P7 Decision-tracker false-positive guard tightening** | **PARTIALLY CLOSED 2026-05-04 S331.** Immediate-prefix quoted/backtick-literal portion (DECISION-0001/0002 closure) closed by Sub-slice A of GTKB-GOV-AUQ-ENFORCEMENT-STACK (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-007.md`, Codex GO at -008) via negative lookbehind `(?<!["` + chr(96) + `])` on all 7 prose patterns. Code-fence-aware structural portion (multi-line ``` blocks) deferred to named follow-up `bridge/gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04-001.md` (to be filed AFTER Sub-slice A VERIFIED). Row remains active until follow-up VERIFIED. | reliability | low |
| **P8 Cache primers by content hash** | Skip regeneration when source files unchanged. | recover ~2K tok on no-op starts | low |

**Net at completion: ~17K tokens recovered (28-34K → 11-17K). 50%+ reduction.**

**Items retired (explicit deletions to reduce complexity):**

- `.claude/rules/bridge-essential.md` (content → bridge primer)
- `.claude/rules/file-bridge-protocol.md` (content → bridge primer)
- `.claude/rules/codex-review-gate.md` (content → bridge primer)
- `.claude/rules/prime-builder-role.md` + `acting-prime-builder.md` + `loyal-opposition.md` (content → role-conditional primer)
- The 13-option focus catalogue in [`_session_focus_options()`](scripts/session_self_initialization.py:2854) (replaced by 3-option action tray)
- Forward-compat Codex wrappers that never fire (`owner-decision-tracker-ups.cmd` and any others discovered)
- Duplicate glossary entries across CLAUDE.md / AGENTS.md / docs (single primer becomes source of truth)

**Items preserved exactly as-is:**

- Bridge protocol itself (this is about *priming*, not changing the protocol)
- File-bridge audit trail and INDEX.md
- Hook architecture (consolidating outputs, not which hooks run)
- Owner-decision-tracker (P7 tightens; doesn't replace)
- KB / MemBase / Deliberation Archive (P5 adds one boolean flag; otherwise unchanged)

**Live false-positive evidence (S309):** The prose-anti-pattern scan flagged literal text *"prose anti-patterns (\"want me to X or Y?\") and logs them"* from the S309 evaluation report itself, then again from a doc-paragraph in the redesign-plan response. Stored as DECISION-0001 and DECISION-0002 with `detected_via: prose:offering_or_choice`. Motivates P7 quotation/code-fence-aware guard tightening.

**Routing:** Agent Red-local for all phases. Cross-harness primer-registry pattern may evolve to upstream `groundtruth-kb` after proven on Agent Red.

**Regression visibility:** each phase lands tests in `scripts/release_candidate_gate.py`. Token-reduction phases add `tests/scripts/test_session_self_initialization.py` budget assertions per primer.

**Dependencies:** P3 is prerequisite for P4 (rule migration into registry) + P5 (ADR primer in registry) + P6 (action tray rendering). P1, P2, P7, P8 are independent of each other and of the P3+ chain.

**Out of scope:** changing the bridge protocol; changing the hook event model; replacing the in-memory model build with an external service; harness-specific UI beyond what the hook contract supports.

**Acceptance:** when P1 ships VERIFIED, fresh-session prelude drops by ~9K and three latent bugs (atomic write, ceiling test, Codex wrapper) close. When P3-P6 ship VERIFIED, the architectural vision is realized: priming displaces catalogue; spec-gap bias surfaces; project-orientation replaces flat option list. **P1 VERIFIED 2026-04-25 (S309)** at `bridge/gtkb-startup-enhancements-p1-006.md`; ~10,400 tokens recovered (slightly above the 9K estimate). P2-P8 remain as future bridges.

### GTKB-WRAPUP-ENHANCEMENTS - Session-end scanner suite for the five wrap-up goals

**Priority:** medium-high. **Filed 2026-04-25 (S309)** per owner directive expanding session wrap-up from "Stop hook writes a silent report" to "five-scanner suite achieving five explicit goals." **Scope:** session wrap-up effectiveness. Coupled with `GTKB-STARTUP-ENHANCEMENTS` via S4 → P6 handoff doc (continuation guide consumed by next session's action tray).

**Five Wrap-Up Goals (owner directive):**

1. **Record knowledge / decisions / directives** that emerged during the session but weren't captured at the time. Today: relies on Prime remembering to file feedback-memory entries; misses inline directives ("from now on...", "always...", "never...") and factual claims that diverge from MEMORY.md/KB.
2. **Identify cross-artifact contradictions** while context is fresh. Today: phantom-INDEX bug class has recurred 3+ times in S308/S309 (proposal-standards -020, code-quality-baseline -003 phantom feedbacks, etc.) and only Codex catches them via manual inspection during bridge review.
3. **Consume usable context** to close in-flight work cheaply. Today: in-flight artifacts (half-filed proposals, identified-but-untracked bugs, post-impl reports awaiting filing) often drop on the floor.
4. **Describe what next session should anticipate** per topic. Today: bridge INDEX is a status feed not a topic browser; owner walks threads manually.
5. **Surface hygiene / maintenance candidates** for owner-chosen focus. Today: drift accumulates between sessions (untracked bridge files, stale INDEX references, MEMORY.md growth, etc.) with no proactive scan.

**Mission:** make session wrap-up systematic instead of ad-hoc; close the gap between hook-driven file-write and chat-surfaced findings; produce machine-readable handoff that the next session's startup pipeline can consume.

**Source evidence:** S309 conversation evaluating session-wrap-up architecture against the 5 owner goals. Concrete diagnoses: wrap-up report writes silently to disk with no chat-surface injection; no transcript scanner at wrap time (owner-decision-tracker only catches AskUserQuestion + 5 prose patterns); no cross-artifact consistency checker (Codex catches phantom-INDEX manually); no in-flight inventory (Prime reliance on memory); no per-topic continuation guide (only flat 13-option focus menu); no hygiene scan (S308-era untracked files caught only by chance during S309 bridge scans).

**Target architecture: 5-Scanner Suite (Tier B of two-tier wrap-up)**

| Scanner | Goal | Reads | Produces |
|---|---|---|---|
| **S1 Synthesis** | 1 | session transcript snapshot, MEMORY.md, KB | candidate `feedback_*.md` / MEMORY.md updates surfaced for owner confirmation; never auto-mutates per `PB-ARTIFACT-APPROVAL-001` |
| **S2 Cross-artifact consistency** | 2 | bridge/INDEX.md, bridge/*.md, work_list.md, MEMORY.md, groundtruth.db | drift report (file-existence checks, INDEX↔file alignment, backlog status alignment, MEMORY.md numbers vs KB) with severity tiers + remediation suggestions |
| **S3 Loose-ends inventory** | 3 | session transcript, git status, bridge state | actionable closures with effort estimates; owner picks which to chase before session ends |
| **S4 Continuation guide** | 4 | bridge/INDEX.md (terminal-vs-active), work_list.md, pending-owner-decisions.md | per-topic markdown blocks at `docs/gtkb-dashboard/session-handoff.md`: state, last activity, next step, blocking decisions/dependencies — consumed by next session's startup-disclosure (P3+ of GTKB-STARTUP-ENHANCEMENTS) |
| **S5 Hygiene** | 5 | filesystem, git, KB | "Hygiene Candidates" with severity tiers (P0 audit-trail / P1 drift / P2 housekeeping): untracked bridge files, stale INDEX references, MEMORY.md size, backup file age, unstaged mods, branches with stale tracking |

**Two-tier execution model:**

| Tier | Trigger | Components | Time budget |
|---|---|---|---|
| **A (FAST)** | Stop hook (every session end) | Transcript snapshot to `memory/session-snapshots/{session-id}.jsonl`; capture session-end timestamp + commit-range; lifecycle-guard update (existing); owner-decision-tracker stop-mode (existing) | <5s |
| **B (SLOW)** | `/kb-session-wrap` skill or wrap-up trigger phrase (owner-invoked) | The 5 scanners run sequentially; outputs land in `session-wrapup-report.md` AND inject as additionalContext for the wrap turn AND produce machine-readable sidecar files for next session | unbounded |

**Owner-chosen architectural decisions (2026-04-25 S309):**

- **Trigger model: on-demand /wrap only.** Stop hook stays at fast tier (transcript snapshot + lifecycle guard + decision-tracker). Five scanners run on owner-invoked `/wrap` or wrap-up phrase. Avoids 15s-Stop timeout pressure; lets scanners be thorough; matches existing skill pattern.
- **Item structure: separate work item, coordinated phases.** This work item is parallel to GTKB-STARTUP-ENHANCEMENTS, not absorbed into it. Both items independently trackable; clear ownership of start vs end of session lifecycle. Coordination via the W3↔P6 handoff doc.

**Phased delivery (each phase = one bridge):**

| Phase | Scanner | Notes |
|---|---|---|
| **W0** Transcript-snapshot precursor | (Stop-hook fast tier addition) | Tiny precursor: extends `.claude/hooks/owner-decision-tracker.py` Stop mode (or adds new hook) to copy transcript JSONL into `memory/session-snapshots/{session-id}.jsonl` for later scanner consumption. Required for W4+W5; cheap to build. |
| **W1** S5 Hygiene scan | filesystem + git + KB | Closes hygiene gaps S308/S309 caught by chance: untracked bridge files, stale INDEX, MEMORY.md ceiling, backup age, unstaged mods. |
| **W2** S2 Cross-artifact consistency check | static state | Closes phantom-INDEX defect class. Bridge file existence + INDEX alignment + backlog status alignment + MEMORY.md numbers. |
| **W3** S4 Continuation guide | bridge INDEX + work_list + pending decisions | Auto-generates `docs/gtkb-dashboard/session-handoff.md`. Consumed by GTKB-STARTUP-ENHANCEMENTS P6 action tray. |
| **W4** S3 Loose-ends inventory | session transcript + git + bridge | Walks edit/file-write history; identifies in-flight artifacts (bridge proposals not filed, post-impl reports overdue, identified follow-ups not filed). |
| **W5** S1 Synthesis scanner | session transcript + MEMORY.md + KB | Pattern-matching for owner directives, inline decisions, factual divergence, phantom-citation candidates. Quotation-aware + code-fence-aware from day 1 (don't repeat the owner-decision-tracker false-positive class — see DECISION-0001/0002/0005 lessons). |

**Suggested batching:**

- **Slice 1 (highest-value foundation):** W0 + W1 + W2 — transcript-snapshot precursor + hygiene + consistency. Smallest read-only scanners; closes the recurring drift classes; foundation for later transcript-walking scanners.
- **Slice 2 (handoff doc):** W3 — feeds GTKB-STARTUP-ENHANCEMENTS P6 action tray. Depends on W2 (uses drift findings to populate "blocking decisions/dependencies").
- **Slice 3 (transcript-walking pair):** W4 + W5 — both consume W0's transcript snapshot. Pattern-precision work; can ship incrementally.

**Coupling to GTKB-STARTUP-ENHANCEMENTS:**

| Surface | Producer (wrap-up) | Consumer (startup) |
|---|---|---|
| `docs/gtkb-dashboard/session-handoff.md` | W3 | P6 action tray |
| `memory/pending-owner-decisions.md` | existing tracker | existing render_report integration |
| Hygiene-candidates JSON sidecar | W1 | startup disclosure surface (new section) |
| Drift-report sidecar | W2 | startup disclosure surface (new section) |
| `memory/session-snapshots/*.jsonl` | W0 | available for any future cross-session scanner |

W3 is effectively the prerequisite of P6. Joint sequencing matters: W3 should ship before P6 so P6 has something to consume.

**Routing:** Agent Red-local for all phases. Cross-harness scanner-suite pattern may evolve to upstream `groundtruth-kb` after proven on Agent Red (same pattern as GTKB-GOV-OWNER-DECISION-SURFACING).

**Regression visibility:** each phase lands tests in `scripts/release_candidate_gate.py`. W2 + W5 add precision-tracking tests (false-positive rate budgets) per the lesson learned from owner-decision-tracker FP class.

**Dependencies:** W0 prerequisite for W4 + W5. W2 prerequisite for W3 (drift findings feed continuation entries). W1 + W2 + W3 are otherwise independent of each other.

**Out of scope:** auto-mutating KB/MEMORY.md/feedback files (synthesis scanner produces *candidates*, owner confirms); replacing the existing `/kb-session-wrap` skill (this extends it; doesn't replace); changing the bridge protocol or hook event model.

**Acceptance:** when Slice 1 ships VERIFIED, every wrap-up surfaces hygiene + consistency findings without owner needing to remember to scan. When Slice 2 ships VERIFIED, next session inherits a per-topic continuation guide. When Slice 3 ships VERIFIED, all 5 owner goals are mechanically supported.

### GTKB-GOV-CODE-QUALITY-BASELINE - Default code-quality checklist for all GT-KB adopter project proposals (upstream-routed)

**Priority:** TOP. Filed 2026-04-25 (S308) per owner directive. Slice 1
governance design at `bridge/gtkb-gov-code-quality-baseline-slice1-001.md`;
awaits Codex GO before Slice 2 implementation begins.

**Problem statement:** GT-KB adopter projects today rely on per-author
discipline + per-reviewer judgment for code quality. Owner directives
(`feedback_no_hardcoded_paths.md`, `feedback_pedagogical_comments_standard.md`)
have surfaced repeatedly in S307–S308 because individual authors don't
consistently apply the same rules. Without a default-on baseline,
quality coverage is inconsistent across adopter projects and across
proposal authors.

**Required outcome (Slice 1 design, defined in the bridge proposal):**
specify a stable rule-ID baseline (`CQ-SECRETS-001`, `CQ-PATHS-001`,
`CQ-CONSTANTS-001`, `CQ-DOCS-001`, `CQ-COMPLEXITY-001`, `CQ-TESTS-001`,
`CQ-LOGGING-001`, `CQ-SECURITY-001`, `CQ-VERIFICATION-001`); define
default-on applicability with per-rule N/A or owner-suspension via the
waiver lifecycle (six-field shape: rule_id, scope, reason,
owner_approval_evidence, expiry_or_review_condition, compensating_control_or_accepted_risk);
require every implementation proposal to carry a Code Quality Baseline
table; require LO reviews to evaluate the table; route mechanical
enforcement upstream as an extension to `hook.bridge-proposal-standards`
plus a Windows-aware fallback verifier; ground rules in ISO/IEC 25010,
OWASP Secure Coding Practices, SEI CERT, Twelve-Factor App, and
language-specific style guides as informing references rather than
direct law.

**Required outcome (Slice 2 implementation, post-Slice-1-GO):** insert
the four formal artifact records (`GOV-CODE-QUALITY-BASELINE-001`,
`ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001`,
`SPEC-CODE-QUALITY-CHECKLIST-001`,
`DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001`) under the
formal-artifact-approval-gate; extend the upstream
`hook.bridge-proposal-standards` to enforce the table; add
`scripts/check_code_quality_baseline_parity.py` as the Codex/Windows
fallback; add tests for missing-table, invalid-rule-ID,
unsupported-N/A, expired-waiver, and compliant-proposal cases.

**Routing:** upstream-routed. Slice 2 implementation lands in
`groundtruth-kb`; Agent Red adopts via `gt project upgrade` after
upstream VERIFIED. Same routing pattern as `GTKB-GOV-PROPOSAL-STANDARDS`
and `GTKB-GOV-DA-ENFORCEMENT`.

**Regression visibility:** the proposal-standards hook gains the
table-presence + per-row-well-formedness check; the fallback verifier
runs in the release-candidate gate. Tests in
`tests/scripts/test_code_quality_baseline_parity.py` (Slice 2 file
name, TBD precise location) cover all 5 enforcement cases.

**Dependencies:** depends on `GTKB-GOV-PROPOSAL-STANDARDS` Slice 1
hook extensibility (already GO'd at slice1-020 upstream). No other
local prerequisite.

**Out of scope (Slice 1):** no formal artifact records inserted; no
hook code; no tests; no Code Quality Baseline tables backfilled into
in-flight proposals (applies prospectively only).

### GTKB-GOV-DA-ENFORCEMENT - Mechanical enforcement of Deliberation Archive citation discipline (re-routed to upstream)

**Priority:** passive tracking behind upstream
`gtkb-da-governance-completeness-implementation` (in `groundtruth-kb`
repo). Owner-directed 2026-04-24 during the S306 DA-effectiveness audit.

**Problem statement:** `.claude/rules/deliberation-protocol.md` mandates
Prime Builder pre-proposal DELIB search + citation in a `## Prior
Deliberations` section, pre-review DELIB search by Loyal Opposition, and
immediate archival of owner decisions as `source_type=owner_conversation`.
Audit evidence (S306, 2026-04-24): 0 of 7 Prime proposals in this session
cited DELIBs; only 1 `owner_conversation` DELIB captured despite ≥3 owner
decisions; only 12% of DELIBs have `work_item_id` linkage and 18% have
`spec_id` linkage. The protocol lives in a read-on-demand rules file with
no mechanical enforcement.

**Routing decision (2026-04-24, bridge `gtkb-gov-da-enforcement-slice1`
`-002` NO-GO + `-003` REVISED-1):** the initially proposed Agent
Red-local pre-commit hook (`.claude/hooks/require-prior-deliberations.py`)
was withdrawn because:

1. Pre-commit enforcement fires too late — the bridge INDEX entry makes
   a proposal reviewable BEFORE any commit step, so commit-time gates
   miss the hot-loop. The correct surface is author-time
   `UserPromptSubmit`.
2. GT-KB already has the canonical enforcement artifacts reserved under
   `gtkb-da-governance-completeness-implementation`: `delib-preflight-gate.py`
   stub at `templates/hooks/`, registry entries in
   `templates/managed-artifacts.toml` with settings registrations on
   `UserPromptSubmit` + `PostToolUse`, scaffold tests in
   `tests/test_scaffold_settings.py`. Prior bridge decision
   `agent-red-session-wrap-automation-004.md` rules this work must route
   through that thread to avoid duplicate authority.
3. The proposed wiring file (`scripts/pre_commit/run_quality_guardrails.py`)
   does not exist in either Agent Red or groundtruth-kb.

**Required outcome:** implementation is owned upstream. Agent Red
receives the enforcement through GT-KB scaffold + upgrade, not via a
local hook. When the upstream thread
`gtkb-da-governance-completeness-implementation` VERIFIED, Agent Red
runs `gt project upgrade` (or equivalent) to pull the hooks, which then
fire on this repo's `UserPromptSubmit` / `PostToolUse` events per the
managed-artifacts.toml registrations.

**Interim Agent Red override:** none planned by default. If the owner
decides an interim local override is needed before upstream lands, it
would be filed as a new bridge proposal (candidate approach: extend the
existing `.claude/hooks/formal-artifact-approval-gate.py` which already
runs on `UserPromptSubmit`). Not scheduled at time of this entry.

**Tracking (updated 2026-04-24 per bridge `-008` NO-GO F1):** upstream
`gtkb-da-governance-completeness-implementation-016` **GO recorded
2026-04-18** (no blocking findings), per `release-notes-0.6.1.md:140` and
`.implementation-log-gtkb-da-governance-completeness.md:3-5` in the
`groundtruth-kb` repo. Implementation is **active on `main`** (prior
checks were on `feature/ownership-matrix` but the work has since advanced
to `main` with additional landing commits per
`.implementation-log-gtkb-da-governance-completeness.md:691-710,2548-2556`);
implementation surface is still outstanding. Agent Red is **awaiting
upstream implementation completion + VERIFIED**, not awaiting the GO.

**Regression visibility (deferred to upstream):** upstream scaffold
tests already assert the hook presence. Post-upgrade Agent Red sessions
will see DELIB search/citation enforcement on `UserPromptSubmit` and
owner-decision archival on `PostToolUse`.

### GTKB-DASHBOARD-001 - DONE - Dashboard industry-alignment Slice 1

**Status:** **VERIFIED** 2026-04-24 (S306) at
`bridge/gtkb-dashboard-industry-alignment-slice1-008.md`. Filed,
implemented, reviewed, and closed in a single session. Unblocks
`GTKB-DASHBOARD-002`.

**Priority (historical):** filed + implemented 2026-04-24 on owner
direction after the S306 dashboard review.

**Required outcome:** three-item slice delivered per bridge
`gtkb-dashboard-industry-alignment-slice1-006` GO:

1. Progressive-enhancement landing page at `docs/gtkb-dashboard/index.html`
   with fetch-driven KPI snapshot + age badge + explicit open-live button;
   no auto-redirect. Dark-mode fallback via `prefers-color-scheme`.
2. Per-panel freshness secondary value (target `F`) on every stat panel
   except "Refresh Age" itself, sourced from the existing
   `SELECT ... FROM refresh_runs` pattern already used by the generator.
3. Alert-rule skeleton under
   `docs/gtkb-dashboard/grafana/provisioning/alerting/` anchored to
   authoritative `current_metrics` keys (`release_blockers`,
   `ci_testing_failing`) and the `refresh_runs` freshness SQL. Validator
   test asserts exact literals and runs a live refresh fixture to prove
   the keys are actually emitted by the pipeline.

**Regression visibility:** `tests/scripts/test_gtkb_dashboard_grafana.py`
4 panel tests; `tests/scripts/test_gtkb_dashboard_alerting.py` 7 tests
covering structure, exact-literal anchoring, schema-anchored SQL, and
live-emission proof.

**Slice 2/3 follow-ons:** filed if approved — bridge swimlane panel,
work-subject selector, coverage/security/CI panels, alert-notifier
wiring (Slice 2); SLO/error-budget, flow metrics, PR/branch health,
incident/MTTR (pending `gtkb-dora-telemetry-foundation`), remote
exposure, WCAG audit (Slice 3).

### GTKB-DASHBOARD-002 - Dashboard industry-alignment Slice 2 (scoped into 2.1 / 2.2 / 2.3)

**Priority:** after `GTKB-DASHBOARD-001` VERIFIED. Scoping proposal
`bridge/gtkb-dashboard-industry-alignment-slice2-001.md` GO'd at `-002.md`
on 2026-04-24. Sub-slice breakdown below is the approved scope; each
sub-slice ships as its own implementation bridge.

**Approved sub-slice breakdown (from `slice2-001.md` §2, GO'd at `slice2-002.md`):**

- **Slice 2.1 — Visibility (no new data ingest).** Thread:
  `gtkb-dashboard-industry-alignment-slice2a-visibility`. Deliverables:
  bridge-state swimlane panel (per-thread latest status + age-in-state)
  and work-subject selector (Application vs GT-KB scope toggle). Status:
  **ready** — no external dependencies, reuses Slice 1 refresh pipeline.
- **Slice 2.2 — Metrics ingest (new data sources).** Thread:
  `gtkb-dashboard-industry-alignment-slice2b-metrics`. Deliverables:
  coverage trend panel (line + branch, over time) and security posture
  panel (open CVEs via Dependabot / pip-audit / Docker Scout). Status:
  **ready** — parallel to 2.1, independent schema change. GO condition
  from `slice2-002.md` Finding 2: implementation bridge must pin
  authoritative fetch/persist paths (no assumption of local `.coverage`
  or `coverage.xml`; explicit Dependabot-vs-pip-audit authority; Scout
  auth/source or deferred).
- **Slice 2.3 — External integration.** Thread:
  `gtkb-dashboard-industry-alignment-slice2c-integration`. Deliverables:
  CI workflow embed (GitHub Actions latest-runs) and alert-routing
  notifier wiring (email / Slack / Teams). Status: **blocked on owner
  notifier-default decision** (`slice2-001.md` §5.5). GO condition from
  `slice2-002.md` Finding 2: implementation bridge must justify any new
  `ci_runs` persistence against the existing `testing_service_integrations`
  / GitHub-run model already persisted by
  `scripts/session_self_initialization.py:1786-2053` and
  `scripts/gtkb_dashboard/refresh_dashboard_db.py:519-568`.

**Sequencing:** 2.1 and 2.2 can ship in either order or in parallel. 2.3
waits on owner notifier choice; 2.3 does not block 2.1 or 2.2.

**Regression visibility (per sub-slice bridge):** each extends
`tests/scripts/test_gtkb_dashboard_grafana.py` and
`tests/scripts/test_gtkb_dashboard_alerting.py` with pinned assertions
against authoritative pipeline outputs; 2.2 carries a schema-migration
non-regression test; 2.3 carries contract tests against the Grafana
alerting API fixtures. Each sub-slice bridge declares its own full
verification matrix at filing time.

### GTKB-DASHBOARD-003 - Dashboard industry-alignment Slice 3 (SLO, flow metrics, PR health, incident/MTTR, remote exposure, WCAG)

**Priority:** after `GTKB-DASHBOARD-002` VERIFIED and after
`GTKB-DORA-001` lands the prerequisite telemetry.

**Required outcome:** SLO / error-budget model with burn-rate alerts; flow
metrics with WIP aging; branch / PR health panel; incident / on-call /
MTTA / MTTR panel (depends on `incidents` table from `GTKB-DORA-001`);
remote read-only dashboard exposure path (snapshot URL or auth gateway);
WCAG 2.1 AA accessibility audit applying the same bar the app's CI already
gates.

**Regression visibility:** SLO burn-rate alert fires against fixture data;
flow metrics recomputed from live refresh history; PR panel reads GitHub
Actions / GraphQL; incident panel schema + backfill tests;
`tests/scripts/test_gtkb_dashboard_alerting.py` extended for notifier
contract; a11y audit reported against declared WCAG 2.1 AA criteria.

### GTKB-DORA-001 - DORA telemetry foundation (deployable_change + rollback/hotfix linkage + incidents table)

**Priority:** blocks any honest DORA panel (`GTKB-DORA-002`). Filed as
follow-on to the Slice 1 NO-GO `-002` Finding 3 (current
`delivery_timeline_events` has 3 production rows, 0 with commit linkage,
no rollback/hotfix linkage, no incidents table — DORA four keys cannot be
computed without fabricating semantics).

**Required outcome:** extend `scripts/gtkb_dashboard/schema.sql` with a
`deployable_change` identity column on `delivery_timeline_events` linking
commits to deployments; add rollback / hotfix linkage columns marking which
prior deploy a rollback targets; add an `incidents` table with
detect / mitigate / close timestamps and incident-to-deploy linkage;
extend `scripts/gtkb_dashboard/refresh_dashboard_db.py` to populate the new
columns; backfill existing events where possible.

**Regression visibility:** schema migration test; refresh-pipeline test
emits the new columns for sample events; fixture tests for each of the
four DORA keys' input shapes (deployment frequency, lead time, change
failure rate, MTTR) so downstream `GTKB-DORA-002` can compute honestly.

### GTKB-DORA-002 - DORA four-keys panels (consumer of GTKB-DORA-001)

**Priority:** after `GTKB-DORA-001` VERIFIED. Strictly no DORA panels
before the telemetry foundation lands.

**Required outcome:** four stat panels computing deployment frequency
(last 30d), lead time for changes (median, last 30 deploys), change
failure rate (% requiring hotfix or rollback within 24h, last 90d), and
MTTR (median incident-detect to incident-close, last 90d). Nulls with
annotations where data is insufficient; no fabrication.

**Regression visibility:** extends `test_gtkb_dashboard_grafana.py` with
pinned assertions for the four panels; fixture-refresh against a seeded
telemetry DB confirms each query returns the expected shape.

### GTKB-DASHBOARD-RETENTION - Dashboard history retention policy (contingent)

**Priority:** contingent — only filed if `MAX_HISTORY=200` at
`scripts/gtkb_dashboard/refresh_dashboard_db.py:346-349` ever proves
insufficient for a diagnostic or review workflow. Currently bounds history
to ~10 hours at the 3-minute snapshot cadence, which suffices for all
observed use cases.

**Required outcome (if triggered):** add env-configurable
`GTKB_DASHBOARD_HISTORY_MAX_ROWS` and optional time-based
`GTKB_DASHBOARD_HISTORY_RETENTION_DAYS` expiry in `_append_snapshot`;
preserve the row cap as the primary bound; document the new env knobs in
`docs/gtkb-dashboard/grafana/README.md`.

**Regression visibility:** boundary test proves snapshots within the
retention window are preserved exactly and older ones are removed.

### GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH - Canonical backlog table and generated backlog views (upstream-routed)

**Priority:** owner-directed 2026-05-02. High priority after the active
`GTKB-ISOLATION-017` -> `GTKB-ISOLATION-018` -> `GTKB-ISOLATION-019`
critical path unless owner explicitly elevates it. This item supersedes and
absorbs the markdown-schema-linter direction in
`GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1`; linter/citation hooks should be
reframed as compatibility checks around the canonical table, not as the
primary backlog source of truth.

**Problem statement:** the backlog is currently spread across
`memory/work_list.md`, MemBase `work_items`, `backlog_snapshots`, bridge
threads, generated dashboard/startup reports, and audit scripts. The markdown
file is human-readable but not a sufficient source-of-truth database: its
ordering is not mechanically enforced, dates and dependencies are mostly prose,
and items can be buried, duplicated, or lost when follow-ons are recorded in
parent narratives.

**Required canonical table direction:** add an append-only/versioned MemBase
`backlog_items` table and `current_backlog_items` view. The proposal should
define exact DDL, but the row model must include at least:

- `id`, `version`, `backlog_item_name`, `subproject_name`
- `implementation_order` as the presumed sequential backlog position
- `status` lifecycle for proposed/active/blocked/in-progress/verified/
  superseded/deferred states
- `created_at`, `updated_at`, `created_by`, `updated_by`, `change_reason`
- long-form `description` capturing the work item's relevance and intent
- `source_owner_directive` or source-reference fields when owner direction
  created the item
- `source_deliberation_query` plus relation rows or JSON fields for
  deliberations known at creation time
- `related_spec_ids_at_creation`, explicitly historical and not an exhaustive
  applicability claim at implementation-review time
- `related_bridge_threads`, `depends_on_backlog_items`,
  `blocks_backlog_items`, `acceptance_summary`, `regression_visibility`,
  `completion_evidence`, `supersedes`, and `superseded_by`

**Required behavior (during migration window):** `memory/work_list.md` becomes a
transitional generated view. Startup, dashboard, bridge citation checks,
standing-backlog harvest, and doctor/readiness checks must read the canonical
`backlog_items` table. Manual markdown backlog edits should either be rejected,
ignored as non-authoritative, or surfaced as drift until migrated through the
structured backlog writer.

**Migration-completion gate (Slice 7-prime):** Per S337 owner directive
(`DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`), at the conclusion
of the migration this file is deleted. The post-completion steady state is
"MemBase only" — no markdown view persists. Slice 7-prime physically removes
`memory/work_list.md` after parent-thread Slices 2-6 land. The deletion gate
verifies: (a) no row content remains in the file (the generator emits zero
work-item entries because all rows are in `backlog_items`); (b) all consumers
(startup, dashboard, doctor, harness scripts) read from MemBase; (c) the file's
deletion does not break any currently-active hook or rule.

**Migration scope:** migrate active and candidate rows from
`memory/work_list.md` into `backlog_items`, preserving sequential order,
existing status prose, known bridge references, known deliberations, and known
spec references. Existing `work_items` and `backlog_snapshots` should remain
historical/related artifacts unless the proposal explicitly proves a safe
unification path.

**Regression visibility:** tests must prove unique active
`backlog_item_name`, stable append-only version history, deterministic
`implementation_order`, no duplicate active item names, no unresolved
dependency references, no lost migrated rows, generated markdown parity for
the active table, dashboard/startup visibility, bridge citation resolution
against the table, and doctor failure when actionable backlog state exists
only in markdown.

**Next step:** file
`bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-001.md` before any source
changes. The proposal must explicitly reconcile this item with
`GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1`, `GTKB-GOV-004`, and `GTKB-GOV-010` so
the backlog-governance program has one source-of-truth path.

### GTKB-AI-ASSISTED-DELIVERY-MATURITY-MODEL - AI-assisted delivery maturity model advisory

**Priority:** owner-directed 2026-05-03. Advisory/discussion track; do not
start implementation unless Prime Builder and owner decide the model should
become a roadmap, evaluation, or governance artifact.

**Source:** Loyal Opposition advisory report at
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AI-ASSISTED-DELIVERY-MATURITY-MODEL-ADVISORY-2026-05-03-11-35.md`.
The report originated from the review of a public Claude Code maturity-model
discussion and subsequent owner request to formalize the revised model for
Prime Builder comment while avoiding sunk-cost bias.

**Problem statement:** GT-KB should not assume that deeper harness usage,
multi-agent orchestration, or more governance ceremony automatically improves
software delivery. The proposed maturity model separates lower-level prompting
and memory practices from higher-level task protocols, specs/evals,
hooks/guards, orchestration, and release-evidence governance.

**Required outcome:** Prime Builder should review the advisory and decide
whether to treat the model as (a) a no-op external comparison, (b) a lightweight
evaluation lens for GT-KB release/readiness work, or (c) a formal roadmap input
that should produce a governed artifact. Any implementation proposal must
define observable delivery outcomes and avoid treating GT-KB's current design
as presumptively correct.

**Regression visibility:** if promoted beyond advisory status, tests or review
checklists must prove the model is used as an evaluation aid, not as a
self-justifying maturity score.

**Next step:** Prime Builder reviews the advisory and files a bridge proposal
only if it recommends formalizing the model into a durable artifact.

### GTKB-ENV-INVENTORY-001 - Harness and development environment inventory

**Priority:** owner-directed 2026-05-03. High priority for release-baseline
transparency after the active isolation/release path unless owner elevates it
as release-critical.

**Source:** Loyal Opposition advisory report at
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-DEV-ENVIRONMENT-INVENTORY-ADVISORY-2026-05-03-11-53.md`.

**Problem statement:** GT-KB cannot give users a reproducible baseline or make
release packaging mechanical if it does not inventory the actual host,
harness, tool, skill, plugin, hook, MCP, and command environment in which GT-KB
is developed and verified. Harness configuration differences are outside the
GT-KB installable package, but they can materially affect Prime Builder and
Loyal Opposition performance.

**Required outcome:** create a canonical harness/development-environment
inventory artifact with a release-safe public view and a private/local redacted
view. The artifact should cover OS/version details, shell/runtime/tool
versions, Codex and Claude Code versions where discoverable, available skills,
plugins, MCP servers, hooks, command surfaces, settings files, and role-by-
harness compatibility notes. The release process must mechanically require the
inventory to be present and current before an installable package is created.

**Regression visibility:** add a collection command and tests/doctor checks
that fail when the inventory artifact is missing, stale, unredacted where it
should be public-safe, or omitted from release-readiness evidence.

**Next step:** file `bridge/gtkb-env-inventory-001-001.md` with schema,
redaction, startup/dashboard exposure, and release-gate integration.

### GTKB-ENV-INVENTORY-DRIFT-CONTROL-001 - Inventory baseline drift control for protected artifacts

**Priority:** owner-directed 2026-05-06. Follow-on to
`GTKB-ENV-INVENTORY-001`; not a replacement for the baseline inventory work.

**Source:** owner discussion on using inventory for change-control drift
identification, including verifying inventory, evaluating confirmed changes,
and flagging unconfirmed changes for further work, documentation review, or
application compatibility tests.

**Problem statement:** `GTKB-ENV-INVENTORY-001` makes the inventory present,
fresh, redacted, and release-visible, but it does not by itself prove whether a
protected artifact changed without a corresponding inventory baseline update or
explicit drift classification. GT-KB needs a deterministic check that turns the
inventory into a useful change-control sensor instead of a stale snapshot.

**Required outcome:** define a protected-artifact registry and a normalized
inventory-diff gate. The gate should fail checkin/release paths when protected
artifact changes are not accompanied by an accepted inventory-baseline update
or a documented drift classification. Drift classifications should route
changes to accepted baseline update, documentation review, application
compatibility tests, further implementation work, local-only notice, or release
blocker.

**Enforcement stance:** per-CRUD enforcement is feasible only as best-effort
early warning where a mutation flows through a known GT-KB command, hook, or
service. The hard control should be checkin/CI/release-gate diff enforcement,
because manual edits, generated files, Git operations, and external tool edits
do not share one CRUD interception point.

**Regression visibility:** tests should prove that normalized inventory diffing
ignores volatile fields, detects material protected-artifact drift, rejects a
protected artifact change without an inventory update or explicit
classification, preserves public/private redaction boundaries, and keeps
unknown or unsupported optional-tool states non-fatal unless policy marks them
blocking.

**Next step:** file `bridge/gtkb-env-inventory-drift-control-001-001.md` with
scope, target paths, proposed registry schema, checkin/release-gate integration,
and specification-derived tests.

### GTKB-SYSTEMS-TERMINOLOGY-MAP-001 - Canonical artifact/interface names and startup operating surface map

**Priority:** owner-directed 2026-05-03. High priority for agent reliability
after the active isolation/release path unless owner elevates it as
release-critical. Coordinates with `GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH`,
`GTKB-STARTUP-REFRACTOR-001`, and `GTKB-ENV-INVENTORY-001`.

**Problem statement:** agents sometimes fail to recognize that owner terms
refer to specific GT-KB systems or artifacts. Ambiguous words such as
"backlog" can mean a general concept, the current `memory/work_list.md`
artifact, future MemBase `backlog_items`, bridge-derived queue state, or a
dashboard/startup summary. Similar ambiguity exists for glossary, memory,
MemBase, Deliberation Archive, dashboard, bridge, skills, hooks, plugins, role
records, scratch pads, release-readiness surfaces, and doctor/release gates.

**Required outcome:** extend the glossary and startup surfaces with a canonical
artifact/interface map. Each routine system entry should define canonical name,
accepted alternate names, discouraged or forbidden aliases, concept-vs-artifact
distinction, authoritative path/table/API, read method, mutation method, role
permissions, generated-vs-authoritative status, startup visibility, harness
caveats, and verification method.

**First reconciliation case:** resolve the current backlog terminology defect:
the operating-model artifact still identifies `memory/work_list.md` as the
canonical backlog implementation while the glossary describes a future
MemBase-backed `backlog_items` model with `memory/work_list.md` as generated
view. The item should make the present transitional authority and target
authority explicit.

**Regression visibility:** doctor/startup tests must prove common owner terms
such as "backlog", "glossary", "memory", "dashboard", "bridge",
"deliberation", "skill", "hook", and "role record" resolve to the expected
artifact/interface and do not silently fall back to stale/generated summaries
when an authoritative source exists.

**Next step:** file `bridge/gtkb-systems-terminology-map-001.md` proposing the
glossary extensions, startup "GT-KB Systems and Tools" section, doctor checks,
and integration sequence with backlog source-of-truth and startup refactor.

### GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001 - External resource identity registry and confusion audit

**Priority:** owner-directed 2026-05-04 S331. Captured directly to the backlog
as input to further deliberation. Do not advance into implementation during the
v0.7.0-rc1 release path unless owner explicitly elevates it.

**Problem statement:** agents have mistaken specific owner references for
abstract/general references or have bound GT-KB work to the wrong external
resource. The confirmed case is "the GitHub" / "repo" / "repository": the
GroundTruth-KB project repository is
`https://github.com/Remaker-Digital/groundtruth-kb`, while stale Agent Red repo
bindings have appeared in release/CI discussion. Similar ambiguity risk exists
for CI/GitHub Actions, README badges/wiki/issues links, Azure subscription and
production references, SonarCloud quality-gate identity, PyPI/package identity,
project/application/platform wording, KB/MemBase naming, docs/wiki/issues
surfaces, and upstream/local source references.

**Evidence already captured:** Codex Loyal Opposition created the advisory
report
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/RESOURCE-REFERENCE-CONFUSION-CANDIDATES-2026-05-04.md`,
the seed machine-readable registry `.claude/rules/project-resource-aliases.toml`,
and the human-readable companion
`memory/project_external_resource_registry.md`. The report should be treated as
input evidence for the formal deliberation, not as the final governed design.

**Required outcome candidate:** decide whether GT-KB should promote the seed
resource-alias registry into a governed artifact that maps casual owner terms
and historical references to canonical URLs, identities, authority, confidence,
and verification methods. The deliberation should also decide how startup,
doctor checks, release gates, bridge proposal review, and README/package
metadata should consume the registry.

**Regression visibility:** likely checks include validating that common terms
such as "the GitHub", "the repo", "CI", "SonarCloud", "PyPI", "docs site",
"wiki", and "issues" resolve to the intended GT-KB resources; scanning bridge
and release artifacts for unqualified external-resource references; and failing
release readiness when canonical project URLs or resource identities drift.

**Next step:** conduct a formal deliberation using the Codex advisory report as
input; decide whether to promote the registry, which resource identities are
canonical or still unknown, and how to repair stale Agent Red-bound GT-KB
release references without disturbing the active rc1 path.

### GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1 - Backlog schema linter + bridge→backlog citation gate (upstream-routed)

**Supersession note (2026-05-02):** this slice should not proceed as a
markdown-first linter design. Its useful pieces -- bridge citation enforcement,
schema validation, and drift detection -- should be folded into
`GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH` against the canonical `backlog_items`
table. Retain this section as historical scoping evidence until the new bridge
proposal formally resolves or rewrites the slice plan.

**Priority:** file after the current S306 governance bundle
(`GTKB-GOV-PROPOSAL-STANDARDS` + `GTKB-GOV-DA-ENFORCEMENT`) has at least
Slice 1 VERIFIED. Owner-approved 2026-04-24 after the S306
DA-effectiveness + backlog-usage audit.

**Problem statement (from S306 audit):**

| Weak-use pattern observed | Evidence |
|---|---|
| Bridge filed before backlog entry exists | `gtkb-gov-da-enforcement-slice1-001` cited `GTKB-GOV-DA-ENFORCEMENT (new standing-backlog item)` — entry was created *in the same commit*, not before. |
| Follow-on items buried in parent prose | Slice 2/3/4 of DASHBOARD-001 and PROPOSAL-STANDARDS existed only in parent-entry narrative until owner asked; 8 items promoted to top-level this session. |
| State never transitions automatically | `GTKB-ISOLATION-015` stayed "in flight" through 16 bridge rounds with no automatic state change. |
| DONE entries accumulate | ~40% of `work_list.md` is DONE at time of filing. |
| Dependencies aspirational | "after GTKB-DORA-001" is prose; nothing refuses work that violates the order. |

**Required outcome (upstream, as new managed hook family parallel to
`hook.bridge-proposal-standards`):**

- `hook.backlog-cite-gate` — pre-commit + `PreToolUse(Write,Edit)` hook:
  every `bridge/*-001.md` NEW file must carry a `**Work item:** <ID>`
  line; `<ID>` must exist in `work_list.md` **before** the commit lands
  (not in the same commit). Escape hatch: `[backlog-exempt: <reason>]`
  commit-message tag with audit-log write.
- `hook.backlog-schema-linter` — pre-commit hook validating every
  `work_list.md` entry has required fields (`status`, `priority`,
  `filed`, `last_changed`) with enum values, unique IDs, and resolvable
  `depends_on` references. Rejects commits that introduce drift.
- Structured field block per entry (to enable A3 validation): consistent
  5-field header after the entry title.
- `work_list.md` split into active + `work_list_done.md` archive so
  session-start only loads active entries.
- Top-of-file TOC table listing `| ID | Status | Priority | Title |
  Depends on |` for all active items, auto-regenerated on edit.

**Regression visibility (deferred to upstream):** upstream scaffold
tests assert hook presence; upstream hook tests cover citation-gate
behavior (existing-ID pass, new-same-commit-ID rejected, exempt tag
permitted with audit-log side effect) and schema-linter behavior
(missing field, wrong enum, unresolved `depends_on`, duplicate ID).

### GTKB-GOV-BACKLOG-DISCIPLINE-SLICE2 - Backlog state automation + ordering-freshness enforcement (upstream-routed)

**Priority:** file after `GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1` VERIFIED.

**Required outcome (upstream):**

- `hook.backlog-last-changed` — `PostToolUse(Write,Edit)` on
  `work_list.md`: if an entry body changed but `last_changed` did not,
  auto-update it. Agents don't have to remember.
- Bridge state transition automation: when a bridge post-impl `NEW` file
  is filed referencing a backlog entry, auto-set entry
  `status: awaiting-verification`. When the thread reaches `VERIFIED`,
  auto-set `status: done` and move the entry to `work_list_done.md`.
  Implementation: script run by the same session-start / bridge-poller
  path that does other bridge maintenance.
- Dependency-violation warning: when a bridge `NEW` proposal references
  an entry whose `depends_on` is not yet `done`, surface a warning (not
  a block). Prevents silent ordering mistakes.
- **Ordering-freshness validation (added per owner S306 direction):**
  - Session-start / pre-commit check flags any entry whose `status` is
    `in-flight` or `ready` but whose latest referenced bridge thread
    has since reached `VERIFIED`. Caught the stale "TOP after Phase 3
    VERIFIED" state for `GTKB-ISOLATION-011` through `-014` and the
    "in flight" state on `GTKB-DASHBOARD-001` in the S306 audit. Would
    have prevented ~10 minutes of manual hygiene.
  - Flags entries whose `priority:` text still says "TOP after X" when
    X is now `done`. Auto-suggest rewrite (still blocks commit pending
    human confirm — never silently rewrites priority text).
  - Flags "TOP" overload: if more than N entries carry priority=`TOP`
    simultaneously, warn and require the author to resolve sub-ordering
    before committing.
  - Regenerates the top-of-file "Next Actionable Items" table on commit
    (sorted by typed priority + dependency graph). Drift between the
    table and the structured field blocks fails the commit.

**Regression visibility (deferred to upstream):** upstream regression
that seeds entries with mis-transitioned states and asserts the
automation corrects them; dependency-violation warning fires on a
fixture where a parent is in-flight; ordering-freshness validator fires
on a fixture where a status=`in-flight` entry's bridge thread has reached
`VERIFIED`; TOP-overload warning fires when `N+1` entries carry
`priority=TOP`; next-actions table is regenerated deterministically from
the structured field blocks.

### GTKB-GOV-PROPOSAL-STANDARDS - Mechanical enforcement of proposal structure (upstream-routed)

**Priority:** parallel to upstream
`gtkb-da-governance-completeness-implementation`; adoption follows next
`gt project upgrade` after upstream VERIFIED. Filed 2026-04-24 after
applying the routing lesson from the withdrawn `GTKB-GOV-DA-ENFORCEMENT`
slice.

**Problem statement:** 11 of 14 NO-GO findings this S306 session would
have been caught by mechanical checks on proposal structure — missing
scope boundaries, TBD cells in Verification Matrix, unverified test
claims, wrong follow-on WI IDs, non-existent path names, forked
enforcement families. None of `.claude/rules/file-bridge-protocol.md` or
the observed structure (Verification Matrix / Files Touched /
Out-of-Scope / Decision-Needed / Cross-NO-GO Discipline / Test Evidence)
is mechanically enforced. A documentation-only rule does not survive
high-velocity proposal drafting.

**Routing decision (2026-04-24, filed bridge
`gtkb-gov-proposal-standards-slice1-001`):** implementation owned
upstream in `groundtruth-kb` as a new managed artifact
`hook.bridge-proposal-standards`, paralleling the existing
`hook.bridge-compliance-gate`, `hook.delib-preflight-gate`, and
`hook.owner-decision-capture` family. Agent Red does not own any new
hook file; it receives enforcement through `gt project upgrade` when
upstream VERIFIED.

**Adoption contract (REVISED-9 GO'd at
`bridge/gtkb-gov-proposal-standards-slice1-020.md` on 2026-04-24):**

- **Event model:** two separate managed-hook registrations — (1)
  `PreToolUse` on `Write` as the authoritative pre-block for new-file
  authoring, validating `tool_input.content` directly; (2) `PostToolUse`
  on `Edit` as the authoritative final-state gate for edits, reading
  post-edit disk content via `_resolve_edit_path(file_path, cwd)` which
  resolves relative `tool_input.file_path` against payload `cwd`
  (mirrors `templates/hooks/delib-search-tracker.py:215,330`). Absolute
  paths pass through unchanged. Advisory `UserPromptSubmit` hook is a
  separate non-authoritative file.
- **Body-status-token rule:** forward-looking MUST in
  `templates/rules/file-bridge-protocol.md` — newly authored
  `bridge/<slug>-NNN.md` files begin their body with exactly one of
  `NEW`/`REVISED`/`GO`/`NO-GO`/`VERIFIED`. Files whose current first
  body line is non-canonical are grandfathered (hook `emit_pass` with
  diagnostic); heading-first or blank-first-line new-file writes BLOCK.
- **Post-impl discriminator:** metadata-driven via
  `parse_bridge_metadata(content).bridge_kind == "implementation_report"`
  → requires `## Test Evidence` section containing a fenced pytest
  block matching `\d+\s+passed`. Closes the -014 F1 loophole where a
  later `Edit` could add `bridge_kind: implementation_report` without
  adding the evidence section.
- **Output-builder addition:** new `emit_block_post(reason: str) -> None`
  helper in `src/groundtruth_kb/governance/output.py` emitting
  `{"decision": "block", "reason": ...}` (PostToolUse structured block
  shape, distinct from `emit_deny`'s PreToolUse
  `hookSpecificOutput.permissionDecision="deny"` shape). Preserves the
  canonical "no hook constructs raw JSON dicts directly" rule.
- **Bypass:** env var `GTKB_PROPOSAL_STANDARDS_BYPASS=<reason>` OR
  content marker `<!-- bridge-standards-exempt: <reason> -->` in the
  first 100 lines; audit log at
  `.claude/audit/proposal-standards-bypass.log`. Applies to both Write
  and PostToolUse(Edit) block paths.
- **Windows `.codex` fallback parity:** standalone
  `scripts/check_bridge_proposal_standards.py` accepting
  `--event write --path <target>` or
  `--event edit --path <target> [--cwd <cwd>]`; shares the
  `_resolve_edit_path` helper with the hook. 22-fixture parity test
  (16 Write + 6 PostToolUse(Edit), including the two new
  `cwd`-resolution fixtures added in REVISED-9 per -018 F2).
- **Zero shared-parser drift:** the hook consumes `parse_bridge_metadata`,
  `BRIDGE_KINDS`, `_blocking_metadata_violations` read-only; only
  `governance/output.py` is mutated upstream, and only additively
  (new function, no signature change to existing helpers).

**Follow-on slices (filed after Slice 1 VERIFIED):**

- `gtkb-gov-proposal-standards-slice2` — test-claim re-run verifier
  (parses claimed pytest output blocks in post-impl reports and re-runs
  the same commands, failing when real output diverges).
- `gtkb-gov-proposal-standards-slice3` — work-item-ID collision gate
  (cross-references proposed follow-on WI IDs against `work_list.md` to
  prevent routing to an already-assigned slot, e.g. Phase 7 `-006`
  caught routing §D to -016 which was already Phase 8).
- `gtkb-gov-proposal-standards-slice4` — `/gtkb-propose` skill that
  scaffolds a compliant proposal from a slug + scope dimensions,
  running `search_deliberations()` and injecting DELIB-IDs before the
  author writes any prose.

**Tracking:** awaiting upstream `groundtruth-kb` bridge filing + GO /
VERIFIED on the new hook artifact.

**Regression visibility (deferred to upstream):** upstream scaffold
tests will assert hook presence; upstream hook tests will cover the
section-requirement table enumerated in the Slice 1 proposal.

### GTKB-GOV-PROPOSAL-STANDARDS-SLICE2 - Test-claim re-run verifier

**Priority:** filed after `GTKB-GOV-PROPOSAL-STANDARDS` Slice 1 VERIFIED.

**Required outcome:** extend the upstream `hook.bridge-proposal-standards`
family with a verifier that parses claimed `pytest` output blocks in
post-implementation reports and re-runs the same commands in a fixture
environment, failing the pre-commit gate when the real output diverges
from the claimed output. Would have caught Phase 7 `-009`'s "44 tests
pass" stale claim (live was "7 failed, 16 passed").

**Regression visibility:** upstream regression that seeds a stale claim
and asserts the verifier rejects it.

### GTKB-GOV-PROPOSAL-STANDARDS-SLICE3 - Work-item-ID collision gate

**Priority:** filed after `GTKB-GOV-PROPOSAL-STANDARDS` Slice 1 VERIFIED.

**Required outcome:** pre-review hook that cross-references any
`GTKB-ISOLATION-NNN` / `GTKB-DASHBOARD-NNN` / `GTKB-GOV-NNN` mention
in a proposal against `memory/work_list.md` entries. Flags collisions
where a proposal routes deferred work to an ID already assigned to a
different item. Would have caught Phase 7 `-005`'s routing of §D to
`GTKB-ISOLATION-016` (already Phase 8 execution).

**Regression visibility:** test that a proposal citing an already-assigned
ID triggers the gate; aligned routing passes.

### GTKB-GOV-PROPOSAL-STANDARDS-SLICE4 - /gtkb-propose scaffolding skill

**Priority:** filed after `GTKB-GOV-PROPOSAL-STANDARDS` Slice 1 VERIFIED.
Lower priority than Slices 2-3 since it is convenience rather than
enforcement.

**Required outcome:** interactive skill `/gtkb-propose` that walks Prime
through a compliant proposal scaffold — slug + work-item name + slice
number + optional scope dimensions. Runs `search_deliberations()` and
injects relevant DELIB-IDs into a `## Prior Deliberations` stub.
Pre-populates all required sections with TODO placeholders. Emits a
self-review checklist before finalizing the file. Adopts upstream via
GT-KB skill scaffold.

**Regression visibility:** skill invocation test seeded with fixtures;
output file matches the required-section contract enforced by
`hook.bridge-proposal-standards`.

### GTKB-ISOLATION-001 - DONE - Create detailed Phase 1 plan: artifact authority and dependency matrix

**Priority:** TOP. Owner directive 2026-04-22: application-subject sessions must be unable by default to alter GT-KB product artifacts, while GT-KB-subject sessions may retain broader access where needed. This is the first planning phase in the application/GT-KB isolation program.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`. Completed plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md`. Deliberation capture: `DELIB-0878`.

**Outcome:** completed the detailed Phase 1 authority matrix plan. The plan defines the durable matrix schema, conventional and GT-KB authority categories, a preliminary Agent Red authority matrix, owner-decision-pending rows, implementation steps, verification mapping, risk mitigations, and dependencies into Phases 2-9.

**Required outcome:** create a detailed implementation plan for the authority matrix that classifies each GT-KB/App dependency as parent GT-KB product artifact, scoped GT-KB service, application-local governed state, session overlay, dashboard/control-plane operation, or host/container/development-environment boundary. The plan must include path/capability ownership, subject labels, owner-decision-pending legacy exceptions, and recommended authority for bridge, backlog, release-readiness, tests, DA, MemBase, hooks, rules, skills, dashboard, overlays, containers, dev environments, and CI. Apply the industry-alignment critique in the plan source: prefer conventional names, least privilege, workspace trust, generated configuration, controller reconciliation, provenance, and subject-scoped CI over novel GT-KB-only terminology.

**Regression visibility:** evidence gathered from upstream GT-KB ownership resolver/classify-tree output, `groundtruth.toml`, `tools/knowledge-db/groundtruth.toml`, `.claude/settings.json`, `.codex/hooks.json`, `.env.example`, `docker-compose.yml`, `.github/workflows/*`, `requirements-local.txt`, `requirements-test.txt`, `scripts/workstream_focus.py`, `scripts/session_self_initialization.py`, `tests/hooks/test_workstream_focus.py`, and `tests/scripts/test_groundtruth_governance_adoption.py`. This phase was planning only and did not move application or GT-KB files.

### GTKB-ISOLATION-002 - DONE - Create detailed Phase 2 plan: project root and repository topology

**Priority:** TOP after `GTKB-ISOLATION-001`. Owner proposed GT-KB root `E:\Development\GroundTruth-KB\` and application root `E:\Development\GroundTruth-KB\Applications\Agent_Red\`, with ordinary downstream users opening only the application project.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`. Completed plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-002-PHASE2-ROOT-TOPOLOGY-PLAN-2026-04-22.md`. Deliberation capture: `DELIB-0879`.

**Outcome:** completed the detailed Phase 2 topology plan. The plan recommends separate GT-KB and application repositories with package/service consumption, permits a common parent folder only as a workspace container, rejects monorepo/submodule defaults, defines Codex/Claude/VS Code/CI/git/worktree policy, specifies root-boundary verification tests, and defines the non-destructive Agent Red migration rehearsal shape.

**Required outcome:** create a detailed implementation plan comparing parent-plus-subdirectory, separate repositories, monorepo-with-root-enforcement, and package-only GT-KB consumption. The plan must specify Codex/Claude project configuration, git/worktree/submodule policy, hard-boundary verification, migration staging, and rollback.

**Regression visibility:** evidence confirms Agent Red and GT-KB are already separate Git repositories, while Agent Red still contains GT-KB governed/runtime surfaces. The plan explicitly states that Codex/Claude project selection is not a security sandbox and later phases must test local harness, path traversal, dependency mode, git boundary, and CI boundary behavior.

### GTKB-ISOLATION-003 - DONE - Create detailed Phase 3 plan: host, container, and development environment isolation

**Priority:** TOP after `GTKB-ISOLATION-002`.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`. Completed plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-003-PHASE3-ENVIRONMENT-ISOLATION-PLAN-2026-04-23.md`.

**Outcome:** completed the detailed Phase 3 environment isolation plan. The plan defines application-subject, GT-KB-subject, and migration-rehearsal environment authority profiles; covers local harnesses, IDE/workspace trust, devcontainers, Codespaces, Docker/Compose, CI, deployment tooling, secrets, dependency mode, and owner-approved escape hatches; identifies current Agent Red evidence and risk points; and defines a verification matrix for local harness, devcontainer, Docker/Compose, and CI boundaries.

**Required outcome:** create a detailed implementation plan for isolating application-subject development environments from GT-KB product artifacts across local harnesses, dev containers, remote development environments, Docker/Compose, CI, and deployment tooling. Cover filesystem read/write boundaries, application-only project roots, devcontainer/Codespaces lifecycle commands and mounts, workspace trust, container hardening, app-scoped secrets, CI working directories, read-only dependency mounts, and explicit owner-approved escape hatches.

**Regression visibility:** application-subject environments must not receive parent GT-KB write access by default. The plan must explicitly test local harness, dev container, Docker/Compose, and CI boundaries, and must forbid privileged containers, Docker socket mounts, broad host bind mounts, and GT-KB product/admin secrets unless a later owner decision grants a scoped exception.

### GTKB-ISOLATION-004 - DONE - Create detailed Phase 4 plan: scoped GT-KB service boundary

**Priority:** TOP after `GTKB-ISOLATION-003`.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`. Completed plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-004-PHASE4-SCOPED-SERVICE-BOUNDARY-PLAN-2026-04-23.md`.

**Outcome:** completed the detailed Phase 4 scoped service boundary plan. The plan rejects raw all-powerful database/root authority for ordinary application sessions; defines typed scoped operations for dashboard reads, Deliberation Archive, MemBase, bridge, release/deployment requests, credentials, upgrade/scaffold requests, and offline/degraded mode; requires service-side GOV enforcement independent of harness hooks; and defines a verification matrix proving application sessions cannot mutate product records or combine application and GT-KB product readiness claims.

**Required outcome:** create a detailed implementation plan for scoped GT-KB services that application sessions can use without broad parent-root or raw database authority. Cover dashboard reads, app-scoped Deliberation Archive append/query, app-scoped MemBase operations, release/deployment requests, credential scope, offline/degraded mode, and service-side GOV enforcement.

**Regression visibility:** the plan must reject raw all-powerful database connection strings for ordinary app sessions unless a later owner decision explicitly accepts that risk.

### GTKB-ISOLATION-005 - DONE - Create detailed Phase 5 plan: dashboard control plane and programmatic operations

**Priority:** TOP after `GTKB-ISOLATION-004`.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`. Completed plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-005-PHASE5-DASHBOARD-CONTROL-PLANE-PLAN-2026-04-23.md`.

**Outcome:** completed the detailed Phase 5 dashboard control-plane plan. The plan defines a typed operation registry, app-root path and capability allowlists, scoped Markdown operations, deterministic projection of behavior-defining Markdown into subject-specific AI-facing files, durable mode and work-subject flows, harness topology and bridge role-slot requirements, session pause/resume/restart-request controls, dry-run/diff/audit/rollback behavior, authentication and authorization scopes, and GOV/formal-approval boundaries.

**Required outcome:** create a detailed implementation plan for GT-KB dashboard/web control-plane operations that can act on application-local files without granting ordinary application sessions broad GT-KB product authority. Cover typed operation registry, app-root path allowlists, selected Markdown add/remove/scan/normalize tools, minimal executable projection of behavior-defining Markdown into subject-specific AI-facing startup files, durable mode toggle flow, harness topology registry, Prime Builder/Loyal Opposition bridge role slots, work-subject toggles, pause/resume/restart AI session controls, dry-run/diff preview, audit logs, rollback records, authentication, and GOV/formal-approval boundaries.

**Regression visibility:** application-subject sessions must not be able to use the dashboard/control plane to mutate GT-KB product artifacts. Arbitrary path inputs and arbitrary script execution must be denied by default; mode and session-control changes must declare whether they apply immediately or only to the next session. Projection scripts must be product-controlled, reproducible from canonical policy sources, source-hashed, audited, and tested to reduce startup conditional context without deleting mandatory subject/root/GOV enforcement text. The plan must explicitly avoid using projection to remove ordinary AI judgment from application work. Mode/projection operations must not proceed until the target harness, project root, bridge role slot, and single-harness versus dual-harness topology are resolved.

### GTKB-ISOLATION-006 - DONE - Create detailed Phase 6 plan: session overlay and snapshot mechanism

**Priority:** TOP after `GTKB-ISOLATION-005`.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`. Completed plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-006-PHASE6-SESSION-OVERLAY-SNAPSHOT-PLAN-2026-04-23.md`.

**Outcome:** completed the detailed Phase 6 session overlay and snapshot plan. The plan defines copy-only non-authoritative overlays, an app-local overlay root and manifest schema, copy eligibility and denied sources, refresh and stale-detection semantics, promotion-only writeback, generated-projection relationships, canonical-versus-overlay scanner behavior, retention cleanup, implementation slices, and tests proving overlays are non-authoritative and cannot be mistaken for canonical GT-KB product records.

**Required outcome:** create a detailed implementation plan for copy-only session overlays. The plan must define which artifacts may be copied, where overlays live, when refresh occurs, how source hashes and authority metadata are recorded, how stale overlays are detected, and how proposed changes are promoted instead of silently written back to GT-KB.

**Regression visibility:** include tests proving overlays are non-authoritative, no parent artifact is moved, stale snapshots are flagged, and copied artifacts cannot be mistaken for canonical GT-KB product records.

### GTKB-ISOLATION-007 - DONE - Create detailed Phase 7 plan: work subject and root enforcement

**Priority:** TOP after `GTKB-ISOLATION-006`.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`, proposal `bridge/gtkb-session-work-subject-001.md`, revised planning bridge `bridge/gtkb-session-work-subject-003.md`, and Loyal Opposition GO `bridge/gtkb-session-work-subject-004.md`. Completed plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md`.

**Outcome:** completed the detailed Phase 7 work-subject and root-enforcement plan after Phases 3 through 6 were completed. The plan separates operating role, work subject, root, and bridge role slot; defines durable app-local subject state and command precedence; integrates resolved-root mutation guardrails, startup/dashboard scoping, readiness/test scoping, hook parity, Phase 5 control-plane operations, Phase 6 overlay status, multi-harness role awareness, and upstream GT-KB packaging requirements. It remains planning only; implementation still requires a later concrete bridge-approved implementation proposal or explicit owner supersession.

**Required outcome:** create a detailed implementation plan integrating `work subject application` and `work subject GT-KB` with root-boundary checks, startup priority scoping, release-readiness scoping, test scoping, mutation guardrails, hook parity, dashboard/control-plane session controls, durable mode projection, multi-harness role awareness, generated subject-specific AI-facing startup instruction files, and deterministic bridge index handling. The bridge portion must include a scripted writer/validator that fresh-reads live `bridge/INDEX.md`, rejects cached or stale bridge state, validates role/status transitions, computes the next bridge file number from live index plus disk, writes the response file before inserting the status line, preserves the audit trail, and verifies post-write live state. The plan may revise the existing work-subject bridge proposal after root/service/control-plane/overlay requirements are clear.

**Regression visibility:** application-subject sessions must block or warn before mutating GT-KB product paths; readiness and test reports must label the active subject and must not combine application and GT-KB green claims. Bridge implementation tests must cover stale index rejection, next-number calculation, invalid transition rejection, existing-file collision, concurrent index change, and post-write live-state verification.

### GTKB-ISOLATION-008 - DONE - Create detailed Phase 8 plan: Agent Red migration rehearsal

**Priority:** TOP after `GTKB-ISOLATION-015`.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`. Completed plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md`.

**Authorization:** `bridge/gtkb-isolation-phases-8-9-planning-scope-004.md` (GO).

**Outcome:** completed the detailed Phase 8 Agent Red migration rehearsal plan. The plan defines a zero-destructive rehearsal that emits preview artifacts (dry-run inventory, path-rewrite map, CI command inventory, bridge/backlog/release-readiness split previews, production-effects map, rollback manifest) into the target child root without mutating the legacy mixed root, production deployments, or the GT-KB product root. It treats every one of the 16 mixed-state surfaces from the inventory Interdependency Classification table with a named action (move, copy, split, stay, regenerate, deprecate), Phase 1 authority classification, transformation recipe, rollback behavior, and post-migration verification. Surface 11 (`.claude/hooks/workstream-focus.py`) is recorded as already retired/absent per the GO informational note. The plan binds all seven inventory-required coverage items and the four inventory-required exit criteria to concrete rehearsal artifacts and acceptance checks. It remains planning only; actual rehearsal execution is `GTKB-ISOLATION-016` and requires its own implementation bridge.

**Required outcome:** create a detailed implementation plan for a non-destructive Agent Red extraction/migration rehearsal from the legacy mixed root into the selected application root. Include path rewrites, imports, CI/test command updates, dashboard/DB path handling, bridge/backlog split, production deployment effects, and rollback.

**Regression visibility:** require dry-run inventory and verification before any move. No destructive cleanup or production-affecting change is authorized by this planning item.

### GTKB-ISOLATION-009 - DONE - Create detailed Phase 9 plan: downstream adopter packaging and validation

**Priority:** TOP after `GTKB-ISOLATION-008`.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md`. Completed plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md`.

**Authorization:** `bridge/gtkb-isolation-phases-8-9-planning-scope-004.md` (GO).

**Outcome:** completed the detailed Phase 9 downstream adopter packaging and validation plan. The plan binds adopter tooling to the approved entrypoints `gt project init` and `gt project upgrade` (no standalone `gt application scaffold` entrypoint), centers the managed artifact registry as the declarative source of truth for adopter-owned vs product-owned artifacts, expands `gt project doctor`/preflight checks to detect isolation violations (including a negative-presence check for the retired `.claude/hooks/workstream-focus.py`), specifies a clean-adopter test suite under GT-KB `tests/adopter/` with outside-in assertions driven by the registry, specifies documentation and example projects under GT-KB `docs/` and `examples/`, and binds every inventory-required coverage and exit criterion to a concrete deliverable and acceptance check. Open decisions for the implementation bridge include mandatory-vs-opt-in isolation for existing adopters, which GT-KB release ships the tooling, and whether Agent Red becomes a minimized Phase 9 example. It remains planning only; actual productization is `GTKB-ISOLATION-017` and requires its own implementation bridge.

**Required outcome:** create a detailed implementation plan for making the isolation model a GT-KB product capability. Cover `gt project init`, `gt project upgrade`, managed artifact registry changes, `gt project doctor`/preflight checks, clean-adopter tests, application-only project-root documentation, and examples.

**Regression visibility:** clean adopters must default to application subject, must not expose GT-KB product artifacts for mutation from app-only roots, and must retain functioning app-local governance state.

### GTKB-ISOLATION-016 - Execute non-destructive Agent Red migration rehearsal

**Priority:** TOP. Unblocked once Phase 7 Slice 1 VERIFIED (which it is at
`gtkb-isolation-015-phase7-full-integration-016`); does NOT require Slice 2
typed control-plane operations per `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-005.md`
§1.2 (rehearsal sub-scripts walk filesystem and emit previews; none call
`work_subject.set/rollback`). Slice 2 was previously listed as a prerequisite
based on phantom-INDEX VERIFIED at `-006`; that claim was retracted at
`bridge/gtkb-isolation-015-slice2-work-subject-set-002.md` after S308
source-level verification confirmed Slice 2 implementation is absent.

**Required outcome:** after the Phase 8 and Phase 9 plans are complete, run the
approved non-destructive rehearsal from the legacy mixed root into the selected
child application root, emit dry-run inventory and path rewrites, prove split
bridge/backlog/dashboard/DB handling, preserve rollback/removal records, and
verify Agent Red behavior from the child directory without mutating GT-KB
product root or production environments.

**Regression visibility:** rehearsal stays zero-destructive by default. Verify
application-only CI/test/startup/dashboard lanes separately from GT-KB product
lanes and capture exact pre/post path maps.

### GTKB-ISOLATION-017 - Implement downstream adopter packaging and clean-adopter validation

**Priority:** TOP after `GTKB-ISOLATION-016`.

**Required outcome:** land the Phase 9 productization work: `gt project init`
and `gt project upgrade` defaults for application subject, managed artifact
registry updates, doctor/preflight isolation checks, clean-adopter fixtures,
application-only project-root documentation, and examples that preserve
app-local governance state while denying GT-KB product mutations from app-only
roots.

**Regression visibility:** clean-adopter tests must prove safe defaults,
functioning app-local governed state, isolated bridge/readiness/test labeling,
and upgrade/rollback behavior from a clean project root.

### GTKB-ISOLATION-018 - Execute Agent Red child-directory cutover

**Priority:** TOP after `GTKB-ISOLATION-017`.

**Required outcome:** after successful rehearsal evidence and the required owner
approval for the migration window, perform the actual Agent Red extraction into
the selected child application root, rewrite runtime/config/test/CI/deployment
paths, split mixed-root bridge/backlog/state surfaces appropriately, preserve
rollback, and leave the legacy mixed-root path either frozen or clearly
decommissioned.

**Regression visibility:** final cutover evidence must show the app root
operates without default GT-KB product write authority, the GT-KB product root
remains independently runnable, and no production deployment effect occurs
without separate approval.

### GTKB-ISOLATION-019 - Close the isolation program with final verification and backlog cleanup

**Priority:** TOP after `GTKB-ISOLATION-018`.

**Required outcome:** prove the program complete end to end: application-only
sessions default to the child root and application subject, GT-KB product
artifacts remain outside ordinary app mutation scope, clean-adopter packaging
works, remaining mixed-root debts are either removed or explicitly deferred, and
non-isolation backlog items can resume with the new root/service/control-plane/
overlay defaults in place.

**Regression visibility:** run and record separated application and GT-KB
verification lanes, clean-adopter validation, cutover smoke checks, and a
standing-backlog audit that confirms no missing isolation follow-on items
remain.

### GTKB-MASS-001 - Execute GT-KB mass-adoption readiness plan

**Priority:** deferred behind the isolation-program queue by owner directive
2026-04-23. Owner directive 2026-04-20 still stands for GT-KB mass adoption,
but the later owner directive makes completion of the overall application/GT-KB
isolation program the standing priority until `GTKB-ISOLATION-019` is complete
or the owner explicitly reprioritizes this item.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-MASS-ADOPTION-READINESS-PLAN-2026-04-20.md`.

**Required outcome:** make GT-KB ready for scoped commit, review-branch push, merge, and mass adoption by executing the ordered readiness program:

1. classify dirty worktree paths and isolate the first commit scope,
2. run the next fresh-session startup acceptance test,
3. close or owner-disposition release blockers,
4. apply or defer GT-KB scaffold/adoption drift,
5. repair failing or stale testing/tool integrations,
6. run clean-adopter install/startup/dashboard/upgrade/rollback tests,
7. push only scoped evidence-backed commits,
8. merge only after required CI and owner decisions are green or formally deferred.

**Next-session acceptance gate:** test session startup first. A fresh session must present role/governance context, a usable dashboard link, directly actionable session-focus choices, Agent Red dashboard scope with GT-KB as infrastructure, top-of-page dated delivery timeline, and tool-integration remediation guidance before substantive work begins. The startup must not present the invalid `app://-/index.html?hostId=local` dashboard link.

**Regression visibility:** use `tests/scripts/test_session_self_initialization.py`, `tests/scripts/test_groundtruth_governance_adoption.py`, `tests/scripts/test_release_candidate_gate.py`, `scripts/release_candidate_gate.py`, browser verification of `docs/gtkb-dashboard/index.html`, and the clean-adopter test matrix described in the plan report. Keep this item at the top until the plan report's commit/merge/push and mass-adoption criteria are satisfied or explicitly superseded.

### GTKB-CORE-001 - Make core application specification intake default GT-KB behavior

**Priority:** TOP. Owner directive 2026-04-22: use Agent Red specifications as the worked example for a reusable baseline set of requirements that should exist for any similar application, then ensure GT-KB repeatedly prompts for missing input and clarity after initialization until those core specifications are created. Once the core specifications are complete, prompting must cease.

**Current default confirmation:** this is **not mechanically the current GT-KB default behavior yet**. Current GT-KB `gt project init` accepts scaffold options but does not ask the core application specification questions by default; `ScaffoldOptions.spec_scaffold` defaults to `None`; `scaffold_project()` only inserts generated specs when an explicit spec scaffold config is supplied. This backlog item records the approved target behavior, not an already-shipped default.

**Plan source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CORE-SPEC-BASELINE-EVALUATION-2026-04-22.md` and `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CORE-SPEC-INTAKE-IMPLEMENTATION-PLAN-2026-04-22.md`.

**Phase 0 approval evidence:** Owner approved proceeding on 2026-04-22 after the Phase 0 bridge proposal `bridge/gtkb-core-spec-intake-001.md` was filed. Approval packet: `.groundtruth/formal-artifact-approvals/2026-04-22-core-spec-intake-phase0.json`. MemBase formalization: `DELIB-0875`, `SPEC-CORE-INTAKE-001`, `SPEC-CORE-INTAKE-002`, `ADR-CORE-INTAKE-001`, and `DCL-CORE-INTAKE-001`. Current formal status is `specified`; this records the approved target and compatibility policy, not completed implementation.

**Required outcome:** GT-KB provides a persisted core application specification intake loop that is active for newly initialized projects by default, with an explicit opt-out for automation or unusual cases. The loop must ask one missing core-spec question at a time, capture answers with owner-stated provenance or confirmation-needed status, continue across sessions while required slots remain missing/inferred/unclear, and stop once every required slot is owner-stated or explicitly not applicable.

**Baseline slots:** product identity, application type, tenancy/provider administration, user/role model, data classification, compliance obligations, security posture, reliability/SLO posture, external integrations, AI usage, operational/release path, and explicit non-goals.

**Multi-session execution plan:**

1. Phase 0 - Governance and compatibility: propose/approve formal SPEC/ADR/DCL records, settle default-vs-opt-in policy, and preserve backward-compatibility constraints.
2. Phase 1 - Core slot catalog: add stable package-level slot definitions, handles, prompt text, required fields, and not-applicable semantics.
3. Phase 2 - Completion evaluator: inspect persisted MemBase evidence and return each slot as `missing`, `inferred`, `needs_clarity`, `stated`, or `not_applicable`.
4. Phase 3 - CLI surface: add deterministic `gt core-specs status`, `gt core-specs next-question`, and answer/intake flow suitable for tests and hooks.
5. Phase 4 - Integration: wire `gt project init`, `gt project doctor`, session-start hooks, and dashboard/startup reports to surface the next missing core-spec question without blocking concrete owner tasks.
6. Phase 5 - Documentation and adoption evidence: update CLI/bootstrap/user-journey docs, run clean-adopter tests, preserve existing scaffold tests, and record final default-behavior evidence.

**Regression visibility:** upstream GT-KB tests must prove fresh projects start incomplete, owner-stated answers stop prompting per slot, explicit not-applicable stops prompting per slot, inferred candidates do not stop prompting, all-complete state suppresses prompting, existing minimal/full scaffold behavior is not accidentally broken, and non-interactive automation has a no-prompt path. Agent Red release-gate visibility should include a standing backlog/dashboard signal until GT-KB upstream implementation and clean-adopter verification are complete.

### GTKB-GOV-001 — Complete Agent Red Tier A managed-skill adoption apply

**Priority:** TOP. Owner directive 2026-04-19: adopt and enforce, to the extent possible, all GroundTruth-KB governance specifications, skills, subsystems, and integrations available to Agent Red.

**Required outcome:** finish the pending `gtkb-skills-tier-a-adoption-apply` thread or supersede it with an owner-approved direct apply record. Confirm all GroundTruth-KB v0.6.1 Tier A managed hooks, rules, skills, settings registrations, and gitignore exceptions are either adopted, explicitly rejected with rationale, or recorded as project-owned overlays.

**Regression visibility:** keep `tests/scripts/test_groundtruth_governance_adoption.py` in the release-candidate gate and extend it for every newly adopted managed artifact.

### GTKB-GOV-002 — Promote Agent Red release-candidate gate into the GT-KB managed skill/doctor model

**Priority:** TOP. Candidate skill identified during release-readiness hardening: `.claude/skills/release-candidate-gate/SKILL.md` now exists locally for Agent Red, but it is not yet an upstream GroundTruth-KB managed skill or doctor/readiness plugin.

**Required outcome:** add an upstream GT-KB bridge/work item for a reusable release-candidate gate skill or doctor check that downstream adopters can install through the managed artifact registry. It should cover security scans, dependency audit, targeted regression suites, frontend builds, DA/MemBase update evidence, and Python-version proof.

**Regression visibility:** upstream GT-KB tests should prove scaffold/install/upgrade behavior; Agent Red tests should prove the local gate remains wired into CI.

### GTKB-GOV-003 — Add an Agent Red governance-adoption doctor check

**Priority:** TOP. Candidate integration identified during this pass: Agent Red can verify GT-KB adoption through tests, but there is no first-class `gt project doctor` or plugin-style command that reports adopter drift across `groundtruth.toml`, `.claude` hooks/rules/skills, workflow gates, and KnowledgeDB gate plugins.

**Required outcome:** implement or request an upstream GT-KB doctor/readiness check for adopter drift, including managed-vs-project-owned dispositions and local-only settings such as `.claude/settings.local.json`.

**Regression visibility:** add fixture-based GT-KB tests for drift detection and keep Agent Red's release gate invoking the local adoption test until the upstream doctor is available.

### GTKB-GOV-004 — Complete MemBase work-item harvest into standing backlog snapshots

**Priority:** TOP. Standing backlog source audit found `groundtruth.db` still has 1994 open work items, 14 new, 4 in_progress, 8 unresolved, 1 blocked, 17 specified, 1 created, and 1 deferred work item. These cannot be pasted wholesale into `memory/work_list.md` without making the backlog unusable, but they must be reconciled into backlog snapshots or a structured GT-KB work queue.

**Required outcome:** classify non-terminal MemBase work items into active release blockers, grouped backlog snapshots, obsolete/superseded rows, or separately governed work streams. Start with P0/P1 rows and reconcile `WI-1515`, `WI-1567` through `WI-1569`, `WI-1637`, and `WI-3026` through `WI-3027` explicitly.

**Regression visibility:** keep `scripts/audit_standing_backlog_sources.py` and `tests/scripts/test_standing_backlog_harvest.py` in the release-candidate gate until an upstream GT-KB doctor/check replaces them.

### GTKB-GOV-007 - Revise commercial readiness NO-GO tracks for SPEC-1831, SPEC-1832, and SPEC-1833

**Priority:** Stale PAUSED tag (2026-04-18) lifted 2026-05-07 S332 per `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING`. New disposition required: revise the underlying commercial-readiness NO-GO bridge threads, retire them, or reclassify. Tracked as a separate decision; this entry is no longer paused indefinitely.

**Required outcome:** file or obtain revised bridge proposals that satisfy the latest NO-GO findings, then implement only after GO. Preserve owner-decision and KB-promotion discipline.

**Regression visibility:** bridge entries remain visible through `scripts/audit_standing_backlog_sources.py`; affected tests must cover the revised route, middleware, retention, and alert-engine contracts.

### GTKB-GOV-008 — Repair bridge dispatcher deferral enforcement

**Priority:** TOP. Live bridge dispatcher deferral enforcement implementation is NO-GO because the shared freshness parser still ignores `DEFERRED`, status recognition is duplicated across parser paths, generated-wrapper handling conflicts with ignored output policy, and owner-only mute authority decisions are not recorded.

**Required outcome:** revise the implementation bridge to update shared parser/guard logic, parity-test scanner status vocabularies, verify generated wrapper regeneration without committing ignored outputs, and record explicit owner decisions for option selection/status name/mute authority or keep those behind an owner-decision gate.

**Regression visibility:** PowerShell bridge-automation tests must prove muted/deferred entries suppress dispatch for `NEW`, `REVISED`, `GO`, and `NO-GO` snapshots without suppressing unrelated entries.

### GTKB-GOV-009 — Await GT-KB Azure CI/CD gates verification

**Priority:** TOP. `gtkb-azure-cicd-gates` is latest `VERIFIED` at `bridge/gtkb-azure-cicd-gates-010.md` after Prime Builder fixed the D4 scaffold-only Azure CI/CD generated-doc defect. The generated federated-identity setup guide now instructs environment-subject credentials for `staging-plan`, `staging`, `production-plan`, and `production`, and the regression test proves `refs/tags/v*` is absent from the explicit credential guide.

**Required outcome:** the D4 Azure CI/CD bridge thread is now verified at `bridge/gtkb-azure-cicd-gates-010.md`. Ordinary staging of the broader first-commit package remains gated on fresh Loyal Opposition review of the latest `gtkb-mass-adoption-first-commit-package` package artifact; do not stage upstream Azure CI/CD changes as a standalone package outside that coordinated review.

**Regression visibility:** upstream GT-KB tests now cover template path equality, no-overwrite behavior, OIDC input/env contract, environment usage, production environment-subject federated-identity guidance, absence of `refs/tags/v*` in the explicit credential guide, and actionlint workflow validation.

### GTKB-GOV-010 — Maintain standing backlog harvest audit as release-gate input

**Priority:** TOP. The standing backlog cannot be considered fully populated without a repeatable harvest check over bridge status, MemBase work items, release-readiness blockers, and independent progress artifacts.

**Required outcome:** keep `scripts/audit_standing_backlog_sources.py`, `tests/scripts/test_standing_backlog_harvest.py`, and `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STANDING-BACKLOG-HARVEST-2026-04-20.md` current until GT-KB provides a first-class standing-backlog doctor. Future sessions should update the harvest report or supersede it with a structured snapshot when source counts change materially.

**Regression visibility:** release-candidate gate runs the standing backlog harvest test.

### GTKB-GOV-010-FOLLOWUP-OBSERVATIONS-S342 - Stale paths and brittle assertions in standing-backlog harvest surface

**Priority:** Batchable hygiene window. Three observations surfaced during S342 (2026-05-11) GTKB-GOV-010 evidence refresh work. All three are editorial / test-hygiene fixes; none are P0 release blockers. Surfaced per the owner directive 2026-05-11: "if you notice an issue which should be fixed or an opportunity for a useful enhancement that will help us work more effectively in the future, please add it to the backlog as an item for future implementation consideration."

**Required outcome:** address as a single hygiene-sweep proposal once GTKB-GOV-010-HARVEST-REFRESH-2026-05-11 has been verified (so the tests/work_list.md edits don't churn the harvest baseline mid-review).

1. **Stale `tests/scripts/...` path reference in this file.** GTKB-GOV-010 entry (above, line 1696) cites `tests/scripts/test_standing_backlog_harvest.py` but the file moved to `platform_tests/scripts/test_standing_backlog_harvest.py` in commit `a641f622` (refactor(tests): rename tests/ to platform_tests/). The same stale path appears in `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STANDING-BACKLOG-HARVEST-2026-04-23-AZURE-VERIFIED.md` line 80 and `STANDING-BACKLOG-HARVEST-2026-04-23-PRE-REV4-FILING.md` lines 35, 112, 169. Editorial fix; can be batched into a single sweep that updates all live references while preserving the historical snapshots as evidence.

2. **Brittle hardcoded count assertion in `platform_tests/scripts/test_standing_backlog_harvest.py` line 131: `assert "1994 open" in work_list`.** This snapshot count is from the 2026-04-20 baseline and assumes work_list.md continues to include the original 2026-04-20 harvest paragraph verbatim. Any sweep that consolidates harvest references in work_list.md could break the test. The test could be refactored to assert the GTKB-GOV-010 directive is present without the brittle count, OR to assert "GTKB-GOV-010" is referenced and the audit script + first harvest snapshot are cited, decoupling the assertion from a specific historical number.

3. **Test references the "current" harvest snapshot by exact filename** (`platform_tests/scripts/test_standing_backlog_harvest.py` lines 99-104, `STANDING-BACKLOG-HARVEST-2026-04-23-AZURE-VERIFIED.md`). Each routine snapshot refresh under GTKB-GOV-010 either drifts the "current" reference or pins it. Consider replacing the exact-filename match with a directory-glob "most recent dated snapshot" lookup so future refreshes are additive without test churn. This is the architectural fix that GTKB-GOV-010's "first-class standing-backlog doctor" eventually replaces; until then, the glob pattern reduces ongoing churn cost.

**Regression visibility:** the GTKB-GOV-010 harvest test should continue to pass after item-1 and item-2 are addressed. Item-3 requires a test refactor with verification that the new lookup correctly identifies the latest snapshot.

**Cross-references:**

- Source observations: bridge `bridge/gtkb-gov-010-harvest-refresh-2026-05-11-001.md` (S342 NEW) - the OOSO section enumerates the same observations as the proposal's record.
- Aligned with `GTKB-SESSION-FRICTION-OBSERVATIONS-S341` (above, item 3 - clause-preflight detector regex coverage too narrow on canonical phrases): the same regex-fragility class.

### GTKB-SESSION-FRICTION-OBSERVATIONS-S341 — Operational frictions surfaced during S341 parallel-Prime session

**Priority:** Batchable hygiene window. Six operational frictions observed during S341 (2026-05-11) parallel-Prime-session work that collectively impeded smooth bridge/INDEX cycles and protected-artifact writes. Surfaced per the Deterministic Services Principle (`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`); each item is independently small but the aggregate friction is expensive at high session throughput, especially during concurrent Prime activity (≥ 2 active Claude sessions interleaving INDEX edits + bridge filings).

**Required outcome:** prioritize items 1-3 as bridge-tracked fixes (each gets its own NEW proposal); batch 4-6 as a hook-friction-cleanup omnibus or file individually as discovered prioritization allows. None of these are P0 release blockers; all are acceleration / governance-loop tightening leverage.

1. **GT-KB INDEX edit race during concurrent Prime sessions.** When two Prime harness sessions are concurrently active (S341 demonstrated this throughout — see commits `eabfc12a` and `0f1328d2` for cross-attribution patterns), `bridge/INDEX.md` is modified between Prime's `Read` and `Edit` tool cycles, causing 6+ Edit-tool failures across the session that required Read/retry sequences. Mitigation: file a `gt bridge index add-entry --thread <slug> --status <NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN> --file <path>` deterministic-service CLI per the Deterministic Services Principle. The CLI handles file locking, appends correctly under concurrency, and provides idempotent semantics (re-running with the same args is a no-op). Aligns with `GTKB-ARTIFACT-RECORDER-CLI` shape but for bridge INDEX. Estimated AI surface reduction ~70% per INDEX operation (currently ~5-7 tool calls per entry; CLI reduces to 1 call).

2. **Narrative-artifact-approval-gate env-var injection gap.** The Claude PreToolUse hook (`.claude/hooks/narrative-artifact-approval-gate.py`) reads packet ref from `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` env var or `tool_input.narrative_artifact_approval_packet` field. Neither is reachable from Claude's Write/Edit tool calls: the Write tool schema doesn't expose the extra field; Bash-set env vars don't propagate to Claude's tool subprocess (Claude Code spawns the hook subprocess inheriting its own env, not the Bash subshell's env). The current workaround is Python+Bash bypass (compute sha256, create packet, write protected file via `Path(...).write_text()`), which the pre-commit hook validates as defense-in-depth. Mitigation: either (a) extend Write tool schema with optional `narrative_artifact_approval_packet` parameter that the hook detects via `tool_input.narrative_artifact_approval_packet`, or (b) formally document the Python bypass pattern in `config/governance/narrative-artifact-approval.toml` comments + add a `gt narrative-artifact write --path <p> --packet <ref>` helper that wraps the bypass cleanly. Hit at least 3 times in S341 (bridge-essential.md, peer-solution-advisory-loop.md, and earlier sessions per commit message references).

3. **Clause-preflight detector regex coverage too narrow on canonical phrases.** `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` detector matches `(?i)(?:specification[- ]derived\s+verification|spec[- ]to[- ]test|python -m pytest|pytest|ruff|test_.+\.py)` but does NOT match `Spec-Derived Test Plan` (a heading style used in multiple recent proposals, including `gtkb-single-harness-bridge-dispatcher-001` REVISED-3 and REVISED-4). Caused 1 spurious blocking-gap NO-GO during S341 single-harness REVISED-5 filing; resolved by adding the literal phrase `Specification-Derived Verification / spec-to-test mapping` to the section heading. Mitigation: either (a) broaden the regex to include the `Spec[- ]Derived Test Plan` heading style, OR (b) maintain a canonical-phrase list in `config/governance/adr-dcl-clauses.toml` comments that proposal authors can reference, OR (c) update the bridge-proposal template to use one of the matched phrases by default.

4. **Destructive-gate over-broad on `git restore --staged .claude/...`.** The destructive-gate pattern `\bgit\s+restore\s+--staged\s+\..` blocks unstaging of dotfile-paths even though `git restore --staged <file>` is a no-op for working-tree content (only removes the file from the staging area; the file's content remains on disk). Compare to genuinely destructive `git reset --hard`, `git rm --cached`, `git clean -fd`. Mitigation: narrow the pattern to genuinely destructive verbs (e.g., `git\s+(reset\s+--hard|rm\s+--cached|clean\s+-fd|push\s+--force)` for the destructive set), or add an explicit allowlist for `git restore --staged` with a comment noting it is staging-only.

5. **Pending-owner-decisions tracker accumulation.** The owner-decision-tracker hook adds entries to `memory/pending-owner-decisions.md` for prose-detected decision-asks. Stale "should I continue?" entries accumulate when the owner has given general continuation directives that don't use the exact `clear pending` or `resolve DECISION-NNNN: <answer>` syntax. By S341 mid-session, 3 stale entries (`DECISION-0524`, `-0527`, `-0528`) were sitting in the pending list, all answered by the owner's general continuation directives over multiple turns. Mitigation: heuristic auto-cleanup when the owner issues a directive that explicitly continues all pending work (e.g., "continue", "proceed", "please act on the remaining queue"), OR a Claude-side helper that emits `clear pending` to the tracker after the owner has affirmed continuation, OR a tracker-side TTL that auto-expires "should I continue?" entries after N session-turns of continuation.

6. **CRLF/LF sha256 fragility in approval-packet workflow.** When `git` is configured with `core.autocrlf` or similar line-ending normalization (Windows default), the staged-blob sha256 (the value the pre-commit hook checks) differs from the working-tree-file sha256. The approval-packet workflow requires the staged-blob hash; computing it requires `git show :<path>` rather than reading the file directly via `Path(...).read_bytes()`. Caught and worked around in S341 (the bridge-essential.md packet correctly computed from the staged blob). Mitigation: document this gotcha in `config/governance/narrative-artifact-approval.toml` packet-generation comments, OR provide a `gt narrative-artifact gen-packet --path <path>` helper that always computes from the staged blob and constructs the JSON packet with the matching content+hash atomically.

**Regression visibility:** any future deterministic-service CLI for bridge INDEX should ship with concurrent-access tests; clause-preflight regex changes should ship with positive/negative sample tests (e.g., `Spec-Derived Test Plan` heading should match); pending-owner-decision auto-cleanup should ship with idempotency tests; packet generation helpers should ship with line-ending-normalization tests on Windows + POSIX hosts.

**Cross-references:**

- Source observations: S341 session work captured in commits `a20cc3c3` (peer-solution-advisory-loop procedure) and `b4fa274a` (single-harness REVISED-5).
- Aligned with: `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, `.claude/rules/acting-prime-builder.md` § Deterministic Services Principle, and the existing `GTKB-ARTIFACT-RECORDER-CLI` scoping bridge (`bridge/gtkb-artifact-recorder-cli-003.md` REVISED-2, Codex GO at `-004`) which establishes the deterministic-service shape pattern.


### ℹ️ DA-gov dispatch loop — escalation OBSOLETE (resolved by owner action 2026-04-18)

**Spawn-5 escalation (A/B/C) is obsolete.** The owner has effectively chosen
Option B implicitly: GT-KB is now on `main` and `gtkb-da-governance-completeness-implementation-016`
is in active iterative implementation per the fast-iterate posture
(`memory/feedback_iterate_fast_on_main.md`, S300). Two commits have already
landed:

- **`4e54c0b`** — §B.1 refactor (event-aware structured-merge planner/apply via
  shared `_compute_target_event_list` helper).
- **`f5b0051`** — Phase 2: 5 governance hook stubs + 9 registry records
  (registry expanded 42→51, including the 4 new `settings-hook-registration`
  rows that opt into BOTH upgrade enforcement AND doctor enforcement per §A
  of `-015`).

**Remaining work** (per the f5b0051 commit message + `-015` §-numbering):
real hook logic, doctor integration (§B.3/§B.4), §B.2 13+1 test cases
(especially cases 12/13 interleaved-unmanaged), and Phases 1-10 specs/tests
(redaction routing, source-ref validation, LO-report backfill, transcript
extractor, owner-decision capture full impl, GOV-09 capture, backfill
framework, session wrap gate, dogfooding). Approximately 100+ new tests
across ~10 test files; ~8-12 follow-up commits expected.

**Capped-spawn behavior:** the auto-poller will continue to dispatch the
GO until `-017 NEW` (post-impl report) lands. Future capped spawns should
append abbreviated entries to `groundtruth-kb/.implementation-log-gtkb-da-governance-completeness.md`
(spawn-54 entry has the corrected state baseline) and not attempt next-slice
implementation work — the owner's iterative landings on main handle the
cohesive multi-file slices naturally.

Full corrected status chain: see spawn-54 entry in
`groundtruth-kb/.implementation-log-gtkb-da-governance-completeness.md`.

### Forward-work ordering reference (GO'd 2026-04-17)

**Authoritative ordering:** `bridge/post-phase-a-prioritization-003.md` (plan) + `-004.md` (Codex GO).
The plan is the ordering reference for all post-Phase-A work. Each numbered item still requires
its own bridge proposal and review cycle per `.claude/rules/codex-review-gate.md`.

**Tier 1 (immediate, visible to CTO, blocks downstream):**
1. **A1 — `gtkb-bridge-spawn-revalidation`** (small; spawn pre-execution INDEX revalidation guard).
2. **B1 — Agent Red CTO cleanup** (20 commits ahead, CI red on SonarCloud, 19 dirty files to classify).
3. **C1 — `gtkb-managed-artifact-registry`** (closes live Gap 2.8; blocks C2-C8 only; NOT a dependency of D1/D2).

**Tier 2 (parallelizable after Tier 1):**
4. **C2 — `gtkb-upgrade-pre-flight-checks`** (requires C1).
5. **D1 + D2 — Azure spec scaffold + ADR template activation** (independent of C1; can run parallel with C1 — owner priority choice).
6. **E1 — `gtkb-skills-tier-a-adoption-001`** (Agent Red adoption of Tier A deliverables).

**Tier 3 (dependency-gated):** C3+C4, D3+D4, F2 (POR 16.D orphan test), F4 (SPEC-1831/1832/1833 verify), B4 (`wiki/Scaling-Analysis.md` hygiene).

**Tier 4 (planned/deferred):** F1 (POR 14, blocked on carrier), C5-C8, D5→D6→D7, F3 (POR 16.E), B2, B3.

**Tier 5 (long-term):** F6 (Zero-Knowledge Phase 4).

**Codex conditions to carry forward (from `-004.md`):**
- **A1 child bridge must:** (a) make revalidation rule role-specific (Codex = NEW/REVISED match; Prime = GO/NO-GO match); (b) NOT treat `NO-GO` as terminal for Prime (Prime on NO-GO writes REVISED — see `.claude/rules/file-bridge-protocol.md:60-63`); (c) identify live wrapper set explicitly (including whether `*-noconsole.generated.ps1` files are source-of-truth, deployment artifacts, or both); (d) include an integration test that mutates `bridge/INDEX.md` between snapshot selection and spawn execution and proves the stale spawn aborts without modifying any bridge file.
- **B4 child bridge must:** stay scoped as documentation-hygiene around `wiki/Scaling-Analysis.md`; must NOT reopen WI-3171 implementation scope unless new evidence shows a live scaling mismatch.
- **If Prime ever proposes C2 before C1** despite the matrix, that is an explicit owner override of the registry-first recommendation, not a default technical plan.

**Owner override still open:** whether D1+D2 should be pulled into Tier 1 alongside A1+B1+C1 for an Azure-focused CTO demonstration. Default plan recommends Tier 2 placement; owner may elevate.

### Owner-directed backlog addition (2026-04-17): Claude Design GUI exploration

**Priority placement:** Deferred until the current active priorities above are complete or explicitly paused by owner. Once the current priority stack is clear, focus on taking best advantage of Claude Design for Agent Red GUI work.

**Proposed bridge/workstream name:** `agent-red-claude-design-gui-refresh-intake`

**Initial scope (exploration and process design, not implementation):**
- Define how Agent Red's current GUI can be captured for Claude Design using screenshots, route inventory, component inventory, state inventory, design-token notes, and selected source-context directories.
- Define the Claude Design project brief and context package for improving Agent Red GUIs.
- Define the design handoff packet format: exported prototype/HTML/PDF/PPTX/screenshots, component inventory, state matrix, responsive behavior, accessibility notes, open owner decisions, and Claude Code handoff boundaries.
- Define how GT-KB should register design artifacts, visual specs, ADRs, acceptance criteria, and review evidence.
- Define automated GUI verification requirements for Claude Design-derived work: Playwright screenshots, visual baselines, review gallery, axe/accessibility checks, keyboard navigation, semantic DOM assertions, and state-matrix coverage.
- Define Loyal Opposition review gates so Claude Design output becomes binding only after export, GT-KB registration, bridge review, and visual/a11y verification.

**Explicit non-scope until later GO:** no GUI redesign implementation, no production UI changes, no direct Claude Design to production handoff, and no bypass of Prime/Codex bridge review.

### CTO readiness (Agent Red full cleanup)
**GT-KB CI fix (4C regression) ✅ VERIFIED + PUSHED.** Bridge `gtkb-4c-ci-regression-fix-004`. Commit `a3fa4d2` on GT-KB main. All 6 GitHub CI workflows green.

**SMS OTP hardening ✅ VERIFIED (not pushed).** Bridge `agent-red-sms-otp-hardening-008`. Commit `468ec1c7` on develop. 4 files: `src/chat/identity_preprocessor.py`, `src/multi_tenant/widget_otp_verification.py`, `tests/chat/test_identity_preprocessor.py`, `tests/unit/test_widget_otp_verification.py`. 77 target tests pass, 3 `assert_awaited_once()` guards. Provisioning display-name rewrite split to future separate bridge (Codex-002 flagged tenant-isolation risk with cross-partition `STARTSWITH` query).

**Agent Red remaining CTO-prep work** (not yet scoped into bridge proposals):
- 16 commits on develop ahead of origin (includes `468ec1c7` SMS hardening)
- Dirty worktree beyond 4 SMS files (docs, bridge/*, memory, groundtruth.db, ~480 files)
- CI failing on develop at GitHub (last push was several commits back)
- Deferred provisioning display-name rewrite (`src/integrations/provisioning.py` + 2 test files, needs tenant-isolation review)
- Wiki currency review (Codex flagged as stale relative to current April work)

### GT-KB Operational Skills Tier A (Phase A scope GO'd 2026-04-17)
**Status:** Scope GO at bridge `gtkb-operational-skills-tier-a-004`. Scope-level post-implementation tracking report filed at `-005` (NEW, S299) — all six authorized bridges filed in dependency order, G1-G5 review gates propagated, verdict requested. 6 implementation bridges tracked separately. Phase A targets `groundtruth-kb` v0.6.0 — 1 canonical module + 1 PreToolUse hook + 3 skills + 1 metrics collector.

Six implementation bridges (strict dependency order per GO Condition 3):
1. **`gtkb-credential-patterns-canonical`** — **✅ VERIFIED S298** at `-010`. Commit `862045d` on GT-KB main (local, not pushed): 6 files, +1442/-63, tests 969→1074 (+105), ruff/mypy --strict/full-suite all pass. Non-blocking audit caveat from Codex: fixture has set-equality with pre-migration source but not order-equality (subagent reordered PII entries to end). Recommended non-blocking follow-up: either restore order or document content-set comparison basis. #1 is done; #2, #4 in revision; #3, #5 blocked.
2. **`gtkb-hook-scanner-safe-writer`** — **✅ VERIFIED S298** at `-012`. Two commits on GT-KB main: `b5e5c6c` (original delivery, 7 files +1619/-25) + `37a88cc` (post-impl fix per `-010` NO-GO: same-version missing-file repair via `_plan_missing_managed_files`, pattern_description formally non-contractual in schema v1, full-repo ruff format). 1114 tests pass total (+40 from Tier A #2), mypy --strict clean, ruff check + format clean on full repo. 3 proposal NO-GO cycles (002/004/006) → REVISED-1/-2/-3 → GO at -008. Post-impl VERIFY took 2 rounds (-010 NO-GO + -012 VERIFIED). Unblocks #3, #5. Non-disruptive-upgrade primitive `_plan_missing_managed_files` now available for skills (#4) and future managed-file classes.
3. **`gtkb-skill-bridge-propose`** — **✅ VERIFIED S298** at `-008`. Commit `0a60054` on GT-KB main: 9 files, +1274/-1, tests 1134→1161 (+27), mypy --strict/ruff/full-suite all pass. 2 NO-GO cycles (002/004) → REVISED-1/-2 → GO at -006 → committed → VERIFIED at -008. Autonomous -001 draft; Prime took over on -003 REVISED after #4 VERIFIED. Pattern: skill helper does credential-only scan + overlap-safe redact (outermost-label merging via `_normalize_hit_intervals`) + atomic INDEX update with 2-attempt retry; no Force bypass path (helper-based writes are outside scanner-safe-writer's Write-tool scope, documented). Unblocks #5 mutation-gate pattern.
4. **`gtkb-skill-decision-capture`** — **✅ VERIFIED S298** at `-012` (no findings). Commit `d9325c9` on GT-KB main: 9 files, +821/-7, tests 1114→1134 (+20), ruff/mypy --strict/full-suite all pass. Wheel contents verified: both skill files ship. 4 proposal NO-GO cycles (002/004/006/008) + 4 REVISED (003/005/007/009) → GO at -010 → committed → VERIFIED. `_MANAGED_SKILLS` pattern established; skills + doctor integration + non-disruptive upgrade path now operational. Unblocks #3 skill-bridge-propose.
5. **`gtkb-skill-spec-intake`** — `/gtkb-spec-intake` skill with confirm-before-mutate contract. Blocked on #3 (mutation-gate pattern).
6. **`gtkb-phase-a-metrics-collector`** — `scripts/collect_phase_a_metrics.py` + fixtures. Consumes `.claude/hooks/scanner-safe-writer.log` JSONL schema v1 from #2. Can parallel #3-5; deferred to last so collector sees real bridge data.

GO review gates from `-004` that each implementation bridge must satisfy:
- **G1** (High, #1): derive credential-pattern inventory from source, not from proposal counts.
- **G2** (High, first skill bridge): make skill scaffold and adopter installation explicit (skills packaged + copied like hooks).
- **G3** (Medium, all): treat GO as authorizing **six** (not five) implementation bridges; normalize counts in reports.
- **G4** (Medium, #5): use valid deliberation outcome (`deferred` exists today; `pending_confirmation` requires schema/API migration).
- **G5** (Medium, #2+#6): scanner-deny record schema must be a stable interface agreed between hook and collector.

Follow-up bridge after v0.6.0 ships: `gtkb-skills-tier-a-adoption-001` (Agent Red adoption of the five deliverables).

### POR Steps 16.D-16.E — Spec hygiene remediation (16.A/B/C complete)
**Status:** 16.A/16.B/16.C all COMPLETE + VERIFIED (umbrella at `por-step16c-implemented-untested-remediation-004`, 2026-04-17). Remaining: **16.D** orphan test rationalization (~10,440 tests, largest sub-phase), **16.E** exit verification (untested-spec count ≤ 6 + orphan-test count ≤ 100).

### Zero-Knowledge Architecture (Phase 4, longer-term)
4 specs (SPEC-1843/1844/1644/1840), 5 implementation phases, ~6-8 sessions. Prerequisites: POR Step 16 substantially complete.

### Minor GT-KB fixes (investigated 2026-04-17 — both resolved/non-issues)
- ~~delib-search-tracker UserPromptSubmit docstring mismatch~~ — **RESOLVED**: scaffold.py:332 correctly registers under `PostToolUse`, matching the docstring. Stale note.
- ~~settings.local.json flat hook format~~ — **NON-ISSUE**: template is permissions-only; all hooks go through `_write_settings_json()` with proper nested format. Comment at scaffold.py:277 ("settings.local.json with bridge hooks") is cosmetic misnomer but has no functional impact. Not worth bridge-proposal cycle.

## Completed

### S301 ✓

- [ ] **E1 Tier A adoption — Apply phase (δ+ε)** — IN FLIGHT at S301 wrap. Thread: `gtkb-skills-tier-a-adoption-apply-001..007`. 3 NO-GO cycles; REVISED-3 at `-007` awaiting Codex review as of 08:24:34 PDT. Pattern across NO-GOs: AR's deny-default `.gitignore` keeps colliding with GT-KB's tracked-artifacts assumption; REVISED-3 adds §A.2 gitignore exceptions for all 28 registry paths + §A.2.5 evidence proof (git check-ignore must return NOT-IGNORED for all 19 A1 paths + receipt probe) + §B.0 resolve_receipt_mode must return tracked (hard gates). Owner decisions (2026-04-18) pinned into the bridge: clean-tree = δ3 side-branch `e1-apply` via `git worktree add`; per-file-skip = (a) copy-aside+restore; A2 dispositions = 6 adopt-overwrite + 3 reject-keep-local. No Agent Red source writes until Codex GO on the implementation bridge.
- [x] **E1 Tier A adoption — Prepare phase (α+β+γ)** — VERIFIED at `gtkb-skills-tier-a-adoption-prepare-008`. Agent Red is now a formal GT-KB adopter: `groundtruth.toml` committed at `d4db57cd` on develop (profile=dual-agent, scaffold_version=0.6.1, cloud_provider=azure). Full reconciliation table produced with 32 rows classified: 23 A1-adopt (19 missing managed files via dry-run + 3 settings-merge + 1 gitignore-append), **9 A2-conflict** requiring owner disposition before Apply (5 hooks + 4 rules that exist in Agent Red but diverge from the 0.6.1 registry templates), 0 A3-reject. Proposed A2 dispositions: 6 `adopt-overwrite` (credential-scan, spec-classifier, bridge-essential, deliberation-protocol, file-bridge-protocol, loyal-opposition — registry is canonical source) + 3 `reject-keep-local` (assertion-check, destructive-gate, scheduler — AR-specific customizations; scheduler flagged for potential future GT-KB registry refinement as bridge-automation-not-governance). Prepare scope was scope-GO'd at `-002` with 6 resolutions + 4 findings; implementation bridge went through TWO NO-GO/REVISED cycles before GO at `-006` (NO-GOs caught: filename collision, missed existing-file drift reconciliation, PowerShell-incompatible command). Live §B.6 output at draft time confirmed Codex's -002 F2 temp-dir simulation: the 9 file-diverge rows would have been invisible without the explicit all-FileArtifact pass. Implementation commit `d4db57cd`; thread version count 8 (001 NEW + 002 NO-GO + 003 REV-1 + 004 NO-GO + 005 REV-2 + 006 GO + 007 NEW + 008 VERIFIED). Apply bridge (δ+ε) is the next phase, awaiting owner decisions on clean-tree strategy (recommended δ3 side-branch) + apply-mechanism for 3 `reject-keep-local` rows (no per-file skip flag exists in `gt project upgrade --apply`).
- [x] **GT-KB C2 upgrade pre-flight checks (Area 5)** — VERIFIED at `gtkb-upgrade-pre-flight-checks-implementation-004` with zero blocking findings. Commit `94f8495` on GT-KB main (pushed). 6 files, +992/-10: new `src/groundtruth_kb/project/preflight.py` module, new `enumerate_scaffold_outputs` pure API in `scaffold.py`, new `MalformedSettingsError` exception + `_has_malformed_settings_skip` helper + `_NON_MUTATING_ACTION_KINDS` frozenset in `upgrade.py`, typed `warning` + `informational` action Literal extension, CLI filter for non-mutating rows + `--ignore-inflight-bridges` flag + exit code 4 for malformed settings. Implements Area 5.2 (bridge in-flight awareness) + 5.3 (halt-before-write on malformed settings.json) + 5.6 (scaffold coverage delta report). 29 new tests (`tests/test_preflight_checks.py`) covering all 5 Codex conditions (C1 structural filter at CLI layer, C2 halt-before-git ordering, C3 latest-status-only parsing with older-under-terminal regression, C4 pure read-only enumerator with byte-snapshot proof, C5 CLI labels + flag wiring). Explicitly deferred: Area 5.1 branch/unpushed policy checks + 5.5 profile change detection. Excluded: Area 6 settings-merge (separate future bridge). Bridge thread: 4 versions total (scope -001 NEW → -002 GO; impl -001 NEW → -002 GO → post-impl -003 NEW → -004 VERIFIED). Full suite: 1385 → 1414 tests. Non-blocking Codex note: direct `execute_upgrade([warning])` library calls still run git preconditions before `_apply_file_actions` (structural fix is CLI-layer per approved design; not a documented library API contract).
- [x] **GT-KB rollback-receipts Phase 3 — `execute_upgrade` payload-branch-and-merge + receipt** — VERIFIED at bridge `gtkb-rollback-receipts-016` (zero blocking findings). Commit `4bc4bb5` on GT-KB main, pushed. 5 files, +693/-13. Adds `_require_git_repo` + `_require_clean_tree` preflight, short-lived `gt-upgrade-payload-<id>` branch, `git merge --no-ff` producing real merge commit, post-merge receipt write (tracked mode creates separate receipt commit at HEAD; HEAD~1 is merge commit). Removes `.bak` backup writes per `-014` condition 5. Adds 3 new exception types (`NotAGitRepositoryError`, `DirtyWorkingTreeError`, `MergeFailedError`) with CLI error wrapping in `project_upgrade`. 7 new Phase 3 integration tests: not-git-repo, dirty-tree, tracked-end-to-end (topology + all 9 receipt fields), revert-m1-reverts-only-payload (proves the rollback primitive), filesystem-end-to-end, no-bak-invariant, noop-payload-skips-receipt. Wrapped 15 existing `execute_upgrade` call sites in 4 test files with `_setup_git_for_upgrade` helper (11 via concurrent gov-completeness commit `d630b20` which adopted my helper). Full suite: 1356 passed (was 1209 at S300 wrap); mypy --strict clean; ruff clean. Phase 4 post-impl report filed at `-015`; VERIFIED at `-016`. Thread fully closed: 16 versions, 7 NO-GOs, 1 GO, 1 VERIFIED. Breaking change: `gt project upgrade --apply` now requires a clean git work tree.

### S297 ✓

- [x] **Agent Red SMS OTP hardening** — VERIFIED at bridge `agent-red-sms-otp-hardening-008`. Commit `468ec1c7` on develop. 4 files (2 src + 2 tests), 77 target tests pass with 3 `assert_awaited_once()` guards. Fixes silent-failure bug where `_send_sms()` returning False was silently treated as success. Bridge iterations: 8 versions (1 NEW + 1 NO-GO proposal, 1 REVISED, 1 GO, 1 NEW post-impl, 1 NO-GO post-impl, 1 REVISED post-impl, VERIFIED).
- [x] **GT-KB CI regression fix (4C)** — VERIFIED at bridge `gtkb-4c-ci-regression-fix-004`. Commit `a3fa4d2` on GT-KB main, pushed to GitHub. Added empty `tests/__init__.py` for `from tests._print_guard` import resolution on Linux CI. All 6 GT-KB CI workflows green (Docs Check, Docs, Docstring Coverage, CI, SonarCloud, CodeQL, Security).
- [x] **POR Step 16.C — Implemented-untested remediation (4 streams)** — VERIFIED at bridge `por-step16c-implemented-untested-remediation-004`. All 4 sub-streams VERIFIED: Stream A (151 α') at -010, Stream B (4 ζ') at -006, Stream C (4 β') at -004, Stream D (34 γ'+δ') at -010. 193-spec reconciliation: 151+4+4+34=193 ✓. Classifier transition: 193→38. 38 hygiene WIs (WI-3185..WI-3218, WI-3221..WI-3224). 122 A1 test updates + 68 test inserts (A3 49, B 18, C 1). 0 spec-status mutations. DELIB-0714 archives consolidated results.
- [x] **POR Step 16.B — Methodology review** — VERIFIED at `por-step16b-methodology-review-006`. 193 implemented-untested requirements partitioned into 5 categories via `classify_16b_candidates.py` (α' 151, β' 4, γ' 19, δ' 15, ζ' 4). Option B (multi-stream remediation) chosen per DELIB-0713.
- [x] **POR Step 16.A — Verified spec closure** — VERIFIED at bridge `por-step16a-verified-spec-closure-010`. Invariant passes (0 violations with owner-approved SPEC-GTKB-SCOPE exception), 7 hygiene WIs open, DELIB-0711 archived, 1686/1686 assertions pass. 10 bridge versions (3 proposal NO-GO + GO + 2 verification NO-GO + VERIFIED).
- [x] **GT-KB Phase 4C — Structured logging migration** — Committed `b1c3359` on GT-KB main. 12 files, +582/-123. New `_logging.py` with split-level defaults (CLI=WARNING, bridge=INFO), `_setup_bridge_logging()` with no-raise fallback, shared `tests/_print_guard.py` (single source of truth for CI + pytest). 989 → 988 tests (+19). Bonus: fixed latent COV_CORE_* Windows mypy crash in `test_public_api_type_checks.py`. Bridge `gtkb-phase4c-structured-logging-016` VERIFIED (4 proposal NO-GO + GO + 2 post-impl NO-GO + VERIFIED).
- [x] **GT-KB Phase 4D — Broad exception governance** — Committed `23cdf09` on GT-KB main. 9 files, +176/-34. Narrowed 2 sites (db.py IntegrityError, launcher.py Windows), removed 1 redundant handler (launcher.py Unix), annotated 21 non-reraising broad catches with `# intentional-catch:` markers. New `tests/test_exception_markers.py` AST-based CI gate (4 tests). Final inventory: 28 handlers (7 exempt re-raise + 21 annotated + 0 unmarked). Bridge `gtkb-phase4d-broad-exception-review-008` VERIFIED.

### S295 ✓

- [x] **GT-KB Phase 4B.8 — Line coverage 54% → 70.04% + branch gate** — 3 commits on GT-KB main: `0e15b90` (174 new tests across 11 files + CI `--cov-fail-under=70` gate + CHANGELOG), `9d68b23` (mypy subprocess env cleanup for latent COV_CORE_* pytest-cov crash on Windows, exit 3221225477 STATUS_ACCESS_VIOLATION — surfaced during 4B.8 full-suite run), `bfdd226` (ruff format blank line caught by post-impl NO-GO). Bridge thread `gtkb-phase4b8-line-coverage-001` → `-014 VERIFIED` (5 NO-GO rounds + 1 post-impl NO-GO, each revealing a different inventory or verification gap: combined-vs-stmt math, hallucinated API names, `| head -25` truncation, cached context.py inventory, incomplete AST import-hygiene check, missing ruff format blank line). **First headless spawn hit the 15-minute timeout** writing 174 tests at 82 turns and was killed mid-verification; Prime Opus completed verification in a live session (no timeout) and diagnosed the mypy-under-coverage crash as a bonus. Final global metrics: combined 70.04%, statements 73.28%, branches 61.16%. Suite: 640 → 814. phase-4b-plan.md updated in `cea14c4`.
- [x] **GT-KB Phase 4B.7 — Residual `mypy --strict` errors (39 → 0)** — commit `f59dad4` on GT-KB main. Closed 39 errors across 5 files (`bridge/poller.py` 17, `bridge/worker.py` 10, `intake.py` 7, `bridge/runtime.py` 4, `bridge/context.py` 1) via six fix patterns (A: `sys.platform` file-lock imports + `_fh: BinaryIO \| None` narrowing; B: `**cast(Any, popen_kwargs)` at 3 subprocess sites; C: None guard + error-dict at 7 intake sites; D: two TypedDict summary accumulators + `cast(dict[str, Any], summary)` returns; E: misc runtime/context narrowing; F: `event_batch: dict[str, Any]` forward decl at `worker.py:581`). Added `tests/test_full_tree_type_checks.py` (638→640 tests) and direct `mypy --strict` CI workflow step. Bridge thread `gtkb-phase4b7-residual-mypy-strict-001` → `-010 VERIFIED` (7 Prime revisions, 3 NO-GO rounds, 1 autonomous headless Sonnet implementation at 82 turns / 9.3 min, 1 Prime commit). Prime Builder discovered Pattern D misdiagnosis (config dict vs summary accumulators) in `-002` and Pattern A/D mypy non-compliance (`os.name` not narrowed, TypedDict not implicitly widened) in `-004` — every subsequent pattern was empirically `mypy --strict` verified before proposal. Methodology lesson captured: never propose a fix pattern without running it through mypy against a standalone snippet first.
- [x] **GT-KB phase-4b-plan.md updated** — commit `ff6988b` on GT-KB main. 4B.7 moved from "In flight" to "Done" table with commit SHA `f59dad4`.
- [x] **Bridge infrastructure permanent fix** — commit `94392a1b` on develop. Rewrote `.gitignore` blanket excludes to content-level with `!`-negations; tracked `.claude/hooks/poller-freshness.py` (hardened worktree-safe, fail-loud), `.claude/settings.json` (project-level `UserPromptSubmit` hook registration), `.claude/rules/bridge-essential.md` (top-priority mandate), and 9 PowerShell + 2 VBS scheduled-task scripts under `independent-progress-assessments/bridge-automation/`. Closes S290-S292 silent-outage window and S294 worktree-blindness root cause. 15 files, +2048/-2.
- [x] **Monitor timestamp enhancement** — commit `5eb0421e` on develop. Prepended local-time `[HH:mm:ss]` to each line emitted by `watch-bridge-scan.ps1`, derived from each status file's own `updatedAtUtc` via `.ToLocalTime()`.
- [x] **Phase 4B plan tracking** — commit `8dafc62` on GT-KB main. Created `docs/reports/phase-4b-plan.md` enumerating sub-rounds 4B.1-4B.6 (Done), 4B.7 (In Flight), 4B.8/4B.9/4C/4D (Proposed) with change protocol.
- [x] **POR Step 16 added** — commit `bb41a59e` on develop. Added post-production spec hygiene remediation step to `docs/plans/PLAN-OF-RECORD-production-readiness.md` (5 phases, exit criteria).
- [x] **Plan artifacts reconciled** — commit `9b8d57fd` on develop. POR file header bumped v3 → v4, Version 6 → 7, target v1.98.91 → v1.98.92 ACHIEVED; work_list.md brought current from S289 to S295 with all missing sub-round history.
- [x] **MEMORY.md refresh** — updated Current Status + added S295 Recent Sessions entry (user auto-memory, not committed to git).

### S292 ✓ (deferred from earlier)

- [x] **Codex autonomous verification batch** — VERIFIED 3 of 4 in-flight items: `poller-emergency-repair` (S291 audit trail), `s291-phase1.5-verified-spec-audit` (98 target specs), `poller-batch-size-cap` (S291 Claude-side cap). `test-artifact-integrity-investigation` NO-GO'd at -004, REVISED -005 autonomously.

### S291 ✓

- [x] **GT-KB Phase 4B.6** — CI enforcement gates (mypy --strict workflow step + per-file coverage gates db.py 68% / cli.py 68% / config.py 80% / gates.py 92% + docstring ratchet 50→51). Commit `31d2c39` on GT-KB main.
- [x] **Spec hygiene S291 batch** — `spec-hygiene-untested-verified-008` VERIFIED (9 backend/widget/pricing specs), `spec-hygiene-spa-investigation-008` + `spec-hygiene-spa-remediation-006` VERIFIED (10 SPA Control Plane specs), Phase 1.5 categorization VERIFIED (98 phantom-evidence specs identified).
- [x] **Claude poller emergency repair** — fixed `$MAX_ITEMS_PER_SPAWN:` one-line PowerShell syntax error that caused 6-hour silent outage. Direct foreground edit.
- [x] **Observability mirror** — `Write-ScanStatus` function + `claude-scan-status.json` at 6 hook points to match `codex-scan-status.json` schema.

### S290 ✓

- [x] **GT-KB v0.4.0 shipped to PyPI** — commit `993f31b` via self-gating `publish.yml` workflow.
- [x] **GT-KB Phase 4A audit baseline** — 10 files committed, baseline metrics published at `docs/reports/v0.4-baseline/SUMMARY.md`. Target commit `83312a0`.
- [x] **GT-KB Phase 4B.1** — config defensiveness (`GTConfigError` wrapping `FileNotFoundError` + `TOMLDecodeError`). Commit `2510f1d`.
- [x] **GT-KB Phase 4B-housekeeping** — Anthropic API-key redaction + `__main__.py` + 4 exit-code tables + `actions/checkout@v4→v6` across 8 workflows. Commit `b41ab8f`.
- [x] **GT-KB Phase 4B.2** — medium defensiveness (PermissionError wrap + missing-section warning + unknown-keys warning). First autonomous headless Sonnet session. Commit `249cdd4`.
- [x] **GT-KB Phase 4B.3** — 27 `KnowledgeDB` + `GateRegistry` public API docstrings to 100% + regression guard. Commit `8151ed2`.
- [x] **GT-KB Phase 4B.4** — mypy --strict public API: 48 errors closed in `db.py` (42), `config.py` (3), `cli.py` (8); insert/update return types widened to `dict[str, Any] | None`; regression guard `tests/test_public_api_type_checks.py`.
- [x] **Poller repair epic** — OAuth token cascade diagnosed + persistent token fix + 90-min → 15-min spawn timeout + Windows toast notifications + file-lock bug fix.

### S289 ✓

## Owner Actions Pending

- [x] Create Chromatic project at chromatic.com + set CHROMATIC_PROJECT_TOKEN GitHub secret (WI-3165) — DONE S285

## Completed (S289)

- [x] **GT-KB Phase 4: F6 Spec Scaffold + F8 Provenance Reconciliation + assertions depth guard** — committed `87e7bd7` on `groundtruth-kb` main, VERIFIED at `bridge/gtkb-phase4-implementation-012.md`
  - F6: new `spec_scaffold.py` (scaffold_specs, SpecScaffoldConfig, ScaffoldReport); `ScaffoldOptions.spec_scaffold` optional integration into `scaffold_project()`; `gt scaffold specs` CLI; 10 tests
  - F8: new `reconciliation.py` (ReconciliationReport + 5 detectors: orphaned_assertions, stale_specs, authority_conflicts, duplicate_specs, expired_provisionals); `gt kb reconcile` CLI with per-detector flags + `--all`; 28 tests (27 detector + 1 CLI smoke)
  - Shared: `_extract_assertion_targets()` gained `depth: int = 0` kwarg with `_MAX_COMPOSITION_DEPTH` guard; 1 regression test in `test_impact.py`
  - Totals: 561 → 600 tests pass, ruff clean, docs CLI coverage clean
  - Review cycle: 5 Prime revisions (v1-v5), 4 Codex NO-GOs, GO at -010, NEW post-impl at -011, VERIFIED at -012
  - Phase 4 completes the entire 8-feature GT-KB Spec Pipeline (F1-F8) started in S286 — the spec pipeline is now fully functional
- [x] **INDEX.md retirement patch (S289 mid-session)** — retired 9 stale/subsumed GT-KB spec-pipeline entries (gtkb-f1f8-cross-check, gtkb-spec-pipeline-f1..f8) from `bridge/INDEX.md` to stop the Prime Builder OS poller from re-firing headless `claude.exe` every 3 minutes on already-completed GO entries. Bridge files remain on disk.
- [x] **Poller autonomy memory** — saved `feedback_poller_autonomy.md` capturing owner directive: "If the poller is working, leave it alone" — mitigate race concerns with fast writes, not shutdown.

## Completed (S285)

- [x] WI-3168 — Migrate knowledge.db to groundtruth.db at repo root (8b9a1def, 11 Codex review rounds, VERIFIED -026)
- [x] WI-3142 — Credential scan narrowing — KB resolved (committed S281)
- [x] WI-3165 — Chromatic CI activation — KB resolved, CI green, 14 snapshots (committed S281 + cb3f2af5)
- [x] WI-3166 — Axe-core CI — KB resolved (committed S282)
- [x] WI-3167 — Playwright baselines — KB resolved (committed S282)
- [x] WI-3169 — Wiki path audit, 6 pages updated (wiki ce2cde8)
- [x] WI-3170 — Transport governance import fix (ae6a6f02)

## Completed (S284)

- [x] GT-kb docs completion — ALL PHASES COMPLETE, Codex VERIFIED (016), committed (0fe21c9), tagged v0.3.0

## Completed (S283)

- [x] Deliberation Archive C3 — Session-wrap harvest script (705 deliberations, 55 bridge threads created)
- [x] Deliberation Archive C4 — Health metrics script + /check-deliberations skill (5 metrics, PASS/WARN/FAIL)
- [x] Deliberation Archive C5 — WI-3159 collision repair + WI-3169 + DOC-DELIB-COMPLETION
- [x] NO-GO fix: test_deliberation_search.py (16 tests, 10/10 known-answer, 100% top-3)
- [x] NO-GO fix: GT-kb v0.2.1 text_match contract test (69/69 pass)
- [x] Requirements updated to GT-kb v0.2.1
