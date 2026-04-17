# Active Work List

**Owner pre-approval:** Proceed through this list autonomously. For each item:
propose via bridge → wait for Codex GO → implement → post-impl report → wait for Codex VERIFIED → commit → drop from list.

Do not wait for owner approval between items. Continue unsupervised.

## Active Items

### CTO readiness (Agent Red full cleanup)
**GT-KB CI fix (4C regression) ✅ VERIFIED + PUSHED.** Bridge `gtkb-4c-ci-regression-fix-004`. Commit `a3fa4d2` on GT-KB main. All 6 GitHub CI workflows green.

**SMS OTP hardening ✅ VERIFIED (not pushed).** Bridge `agent-red-sms-otp-hardening-008`. Commit `468ec1c7` on develop. 4 files: `src/chat/identity_preprocessor.py`, `src/multi_tenant/widget_otp_verification.py`, `tests/chat/test_identity_preprocessor.py`, `tests/unit/test_widget_otp_verification.py`. 77 target tests pass, 3 `assert_awaited_once()` guards. Provisioning display-name rewrite split to future separate bridge (Codex-002 flagged tenant-isolation risk with cross-partition `STARTSWITH` query).

**Agent Red remaining CTO-prep work** (not yet scoped into bridge proposals):
- 16 commits on develop ahead of origin (includes `468ec1c7` SMS hardening)
- Dirty worktree beyond 4 SMS files (docs, bridge/*, memory, groundtruth.db, ~480 files)
- CI failing on develop at GitHub (last push was several commits back)
- Deferred provisioning display-name rewrite (`src/integrations/provisioning.py` + 2 test files, needs tenant-isolation review)
- Wiki currency review (Codex flagged as stale relative to current April work)

### POR Steps 16.D-16.E — Spec hygiene remediation (16.A/B/C complete)
**Status:** 16.A/16.B/16.C all COMPLETE + VERIFIED (umbrella at `por-step16c-implemented-untested-remediation-004`, 2026-04-17). Remaining: **16.D** orphan test rationalization (~10,440 tests, largest sub-phase), **16.E** exit verification (untested-spec count ≤ 6 + orphan-test count ≤ 100).

### Zero-Knowledge Architecture (Phase 4, longer-term)
4 specs (SPEC-1843/1844/1644/1840), 5 implementation phases, ~6-8 sessions. Prerequisites: POR Step 16 substantially complete.

### Minor GT-KB fixes (investigated 2026-04-17 — both resolved/non-issues)
- ~~delib-search-tracker UserPromptSubmit docstring mismatch~~ — **RESOLVED**: scaffold.py:332 correctly registers under `PostToolUse`, matching the docstring. Stale note.
- ~~settings.local.json flat hook format~~ — **NON-ISSUE**: template is permissions-only; all hooks go through `_write_settings_json()` with proper nested format. Comment at scaffold.py:277 ("settings.local.json with bridge hooks") is cosmetic misnomer but has no functional impact. Not worth bridge-proposal cycle.

## Completed

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
