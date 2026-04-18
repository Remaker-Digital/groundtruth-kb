# Active Work List

**Owner pre-approval:** Proceed through this list autonomously. For each item:
propose via bridge → wait for Codex GO → implement → post-impl report → wait for Codex VERIFIED → commit → drop from list.

Do not wait for owner approval between items. Continue unsupervised.

## Active Items

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
