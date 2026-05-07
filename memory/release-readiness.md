# Release Readiness — v0.7.0-rc1 Path (S327 owner direction)

Last updated: 2026-05-06 (S333)

## Active Release Target: v0.7.0-rc1

**Owner directive 2026-05-02 (S327, end-of-session):** the next release opportunity is AFTER `GTKB-ISOLATION-017` closes. Goal: **complete clean-adopter productization**. Recorded as `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION`. Version choice `v0.7.0-rc1` (not `0.6.2` — too small a label for clean-adopter productization).

## ISOLATION-017 Status as of S327 close

| Slice | Description | Status |
|---|---|---|
| 1 | Doctor checks for isolation invariants | VERIFIED |
| 2 | Registry isolation | VERIFIED |
| 2.5 | Rationale/migration-note schema extension | VERIFIED |
| 3 | `gt project init` defaults + host-root binding | VERIFIED *(S327 commit `bdf154b3`)* |
| **4** | **`gt project upgrade` isolation + migration/rollback** | **NEXT** |
| 5 | Clean-adopter test suite + fixtures | After Slice 4 |
| 6 | Docs for application/product isolation + migration | Parallel after Slice 5 |
| 7 | Examples | Parallel after Slice 5 |
| 8 | Release-version gate + closeout | Final |

## Release-Hardening Blockers (address during Slice 8 closeout)

- **Dirty worktree** — RESOLVED 2026-05-02 S327 (commit `44ecb46f`); 5 commits landed; tree clean.
- **`ruff check .`** — red across full repo. Governance hardening verified ruff-clean only on touched files. Slice 8 scope: full-repo ruff resolution.
- **`pytest` full sweep** — timed out locally. Slice 8 scope: scope/parallelize slow lanes for CI feasibility.
- **Package version** — `groundtruth-kb/pyproject.toml` still produces `0.6.1`. Slice 8 scope: bump to `0.7.0-rc1`.
- **Release notes** — most recent at `release-notes-0.6.1.md`. Slice 8 scope: write `release-notes-0.7.0-rc1.md`.
- **Wheel/sdist + install smoke** — Slice 8 scope: verify `pip install groundtruth-kb==0.7.0rc1` produces a working `gt project init`.
- **Clean-adopter proof** — Slice 5's deliverable; Slice 8 verifies acceptance.
- **CI green** — Slice 8 scope: GitHub Actions full sweep + release-candidate-gate.yml workflow green.
- **Bridge terminal state** — Slice 8 scope: all ISOLATION-017 Slices VERIFIED; standing-Backlog/Primer/Disambiguation deferred status documented.

## Feature Freeze

Per S327 owner direction: NO new governance scope work until Slice 8 VERIFIED. The three governance programs landed in S327 (Backlog DB, Term Primer, Term Disambiguation) wait for the post-release window. Slice 1 deliverables are durable (committed at `5da729f8`) but Slices 2+ do not advance.

## ISOLATION-017-CLOSEOUT (S330)

Last updated: 2026-05-03 (S330)

Slice 8 disposition resolved per `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE`: split into Slice 8 (release artifacts) + Slice 8.5 (CI-green capture). Authorizing bridge: `bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-005.md` (REVISED-2; Codex GO at `-006`).

### Blocker outcomes (Slice 8)

| Blocker | Outcome | Evidence |
|---|---|---|
| B1 — Version bump | DONE | `groundtruth-kb/src/groundtruth_kb/__init__.py` line 16 → `__version__ = "0.7.0rc1"`. Verified via `python -c "import groundtruth_kb; assert groundtruth_kb.__version__ == '0.7.0rc1'"`. |
| B2 — Ruff resolution | DONE (NARROWED) | `ruff check groundtruth-kb/` exits 0. Scope narrowed to `groundtruth-kb/` package per `DELIB-S330-ISOLATION-017-SLICE8-B2-RUFF-SCOPE-CHOICE` (1,943 Agent Red product-code issues deferred to a separate Agent Red work item, not release-blocking for this rc). |
| B3 — Pytest feasibility | DONE (GREEN) | `python -m pytest groundtruth-kb/tests/ -q` runs to completion in ~620s; all tests PASS. 13 stale-baseline + behavioral failures fixed in this slice per `DELIB-S330-ISOLATION-017-SLICE8-PYTEST-FIX-SCOPE-CHOICE`. Per-lane runtime breakdown documented in `release-notes-0.7.0-rc1.md`. |
| B4 — Release notes file | DONE | `groundtruth-kb/release-notes-0.7.0-rc1.md` (~170 LOC) authored mirroring `release-notes-0.6.1.md` structure. Cross-references Slice 8.5 follow-on. |
| B5 — Wheel/sdist install smoke | DONE | `scripts/_verify_slice8_closeout.py` `check_b5_wheel_smoke` runs full smoke: (a) `python -m build --wheel --sdist` from `groundtruth-kb/` produces `groundtruth_kb-0.7.0rc1-*.whl` + `groundtruth_kb-0.7.0rc1.tar.gz`; (b) `pip install` the wheel into a fresh tmp venv; (c) `gt --version` reports `0.7.0rc1`; (d) `gt project init SmokeApp --gt-kb-root <discovered_host_root> --dir <discovered_host_root>/applications/SmokeApp --profile local-only --no-include-ci --no-seed-example` succeeds; (e) scaffolded `groundtruth.toml` confirmed under target. The `--gt-kb-root` is discovered at runtime via `from groundtruth_kb.project.scaffold import _GT_KB_HOST_ROOT` per `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK` — the original `-005` plan's `gt project init <tmp>/test-app --profile local-only` command shape did NOT work for installed wheels under Slice 4 isolation. Pip-install adopter UX simplification tracked at row 36 (`GTKB-PIP-INSTALL-ADOPTER-UX-001`); not blocking for this rc. |
| B6 — CI-green evidence | **GREEN (transient de facto evidence)** | Slice 8.5 captured the five required GitHub Actions workflows for `Remaker-Digital/agent-red-customer-engagement` `develop@98b7eab19812ed995d1e606d1d9854a7da803dab`; all completed with conclusion `success`. This uses the transient exception in `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` and does not authorize the rc tag until canonical migration and canonical CI binding are complete. Verifier: `python scripts/verify_slice8_5_ci_green.py`. |
| B7 — Bridge terminal state | DONE | All 8 ISOLATION-017 slice bridges VERIFIED: Slice 1 (doctor checks), Slice 2 (registry isolation), Slice 2.5 (rationale schema), Slice 3 (init defaults), Slice 4 (upgrade), Slice 5 (clean-adopter tests), Slice 6 (docs), Slice 7 (examples). This Slice 8 closes via the post-impl REPORT. Standing-Backlog DB / Term Primer / Term Disambiguation Slice 1s landed in S327; Slices 2-7 deferred per `Feature Freeze` block above (lifts at v0.7.0-rc1 tag). |

### Slice 8.5 CI-green evidence (transient exception)

Authority: `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` permits Slice 8.6 and Slice 8.5 artifacts to cite de facto Agent Red CI evidence from `Remaker-Digital/agent-red-customer-engagement` while canonical migration is pending. The exception is evidence-scoped only; it does not authorize `v0.7.0-rc1`.

Verified on 2026-05-06 with `gh run view <run-id> --repo Remaker-Digital/agent-red-customer-engagement --json databaseId,workflowName,headBranch,event,headSha,conclusion,status,url,createdAt,updatedAt`.

| Workflow | Repository | Branch | Event | Head SHA | Run ID | URL | Conclusion | Authority |
|---|---|---|---|---|---|---|---|---|
| Lint | Remaker-Digital/agent-red-customer-engagement | develop | push | 98b7eab19812ed995d1e606d1d9854a7da803dab | 25296718957 | https://github.com/Remaker-Digital/agent-red-customer-engagement/actions/runs/25296718957 | success | DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE |
| Release Candidate Gate | Remaker-Digital/agent-red-customer-engagement | develop | push | 98b7eab19812ed995d1e606d1d9854a7da803dab | 25296719002 | https://github.com/Remaker-Digital/agent-red-customer-engagement/actions/runs/25296719002 | success | DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE |
| SonarCloud | Remaker-Digital/agent-red-customer-engagement | develop | push | 98b7eab19812ed995d1e606d1d9854a7da803dab | 25296718961 | https://github.com/Remaker-Digital/agent-red-customer-engagement/actions/runs/25296718961 | success | DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE |
| Security Scan | Remaker-Digital/agent-red-customer-engagement | develop | push | 98b7eab19812ed995d1e606d1d9854a7da803dab | 25296718958 | https://github.com/Remaker-Digital/agent-red-customer-engagement/actions/runs/25296718958 | success | DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE |
| Python Tests | Remaker-Digital/agent-red-customer-engagement | develop | push | 98b7eab19812ed995d1e606d1d9854a7da803dab | 25296718963 | https://github.com/Remaker-Digital/agent-red-customer-engagement/actions/runs/25296718963 | success | DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE |

### Tag authorization gate

`git tag -a v0.7.0-rc1` does NOT authorize until ALL:

1. Slice 8 (this thread) is VERIFIED + committed.
2. Slice 8.5 (`bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md`) is VERIFIED.
3. Canonical Agent Red migration is VERIFIED and equivalent canonical CI is captured from the canonical repository.

`v0.7.0-rc1 remains unauthorized` pending canonical migration and canonical CI. Until all gates close, the rc has not been published; release-notes and announcement are author-ready but not authoritative.

### Owner sub-decisions archived (S330)

- `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE` — split into Slice 8 + Slice 8.5 per Codex F1 path 1.
- `DELIB-S330-ISOLATION-017-SLICE8-B2-RUFF-SCOPE-CHOICE` — narrowed B2 to `groundtruth-kb/` package only (1,943 Agent Red issues deferred).
- `DELIB-S330-ISOLATION-017-SLICE8-PYTEST-FIX-SCOPE-CHOICE` — added 13 pytest-baseline fixes to Slice 8 scope (within `-005` Risk 2 anticipated mitigation).
- `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK` — Slice 8 -008 NO-GO disposition; Path A (narrow fix + rc1 install-UX limitation acknowledgement; row 36 added).
- `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER` — Slice 8.5 -002 F2 disposition; python-tests.yml waived for GT-KB-only commits; row 37 added.
- `DELIB-S330-RC1-CI-RED-PAUSE-AND-SLICE-8-6-DISPOSITION` — RC1 CI-red discovery; pause Slice 8.5; Slice 8.6 fix-thread filed.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` — transient exception permitting de facto CI evidence for Slice 8.6 and Slice 8.5 while canonical migration remains pending; does not authorize `v0.7.0-rc1`.

## ISOLATION-017-CLOSEOUT-CI-TRIAGE (Slice 8.6 Phase 1)

**Last updated:** 2026-05-03 (S330 Phase 1 initial draft).
**Authority:** `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-003.md` REVISED-1 (Codex GO at `-004`).
**Scope:** 43 catalog entries from Slice 8 commit `b4346ab690e937b80c5c99f776649f8bb8fa82b1` CI runs (RC Gate `25290378334` + Security Scan `25290378337`).

### Initial classification

Categories: `fix-required` (real defect; remediation is a code/config fix), `waivable-for-rc1` (testable invariant whose enforcement defers to v0.7.0 GA with documented residual risk; requires DELIB), `environmental` (failure due to CI environment not project code), `awaiting-owner-decision` (truly ambiguous; one-at-a-time OWNER ACTION REQUIRED per F4), `awaiting-investigation` (need code probe before classification).

#### Release Candidate Gate failures (41)

`tests/scripts/test_groundtruth_governance_adoption.py` (17):

| # | Test | Initial Classification | Rationale | DELIB |
|---|---|---|---|---|
| 1 | `test_artifact_oriented_governance_records_are_in_membase` | `fix-required` | Test asserts `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` exists in MemBase; the spec record SHOULD exist (referenced in S327 work_list). Insert via `insert_spec` under formal-artifact-approval gate. | — |
| 2 | `test_artifact_oriented_governance_decision_is_archived` | `fix-required` | Test asserts the parent DELIB exists. Insert. | — |
| 3 | `test_bridge_authority_decision_is_archived` | `fix-required` | DELIB missing; insert. | — |
| 4 | `test_bridge_authority_governance_records_are_in_membase` | `fix-required` | GOV record missing; insert. | — |
| 5 | `test_codex_hook_limitation_decision_is_archived` | `fix-required` | DELIB missing; insert. | — |
| 6 | `test_core_spec_intake_phase0_decision_is_archived` | `fix-required` | DELIB missing; insert. | — |
| 7 | `test_core_spec_intake_phase0_records_are_in_membase` | `fix-required` | `SPEC-CORE-INTAKE-001` missing; insert. | — |
| 8 | `test_formal_artifact_approval_records_are_in_membase` | `fix-required` | `GOV-ARTIFACT-APPROVAL-001` missing; insert (the GOV that mandates the formal-artifact-approval gate Slice 8 used 5 times). | — |
| 9 | `test_groundtruth_governance_artifacts_are_present_and_not_ignored` | `waivable-for-rc1` | Tests that `docs/gtkb-dashboard/dashboard-data.json` + `memory/gtkb-dashboard-history.json` exist. Dashboard files are deferred per row 30 (`GTKB-DASHBOARD-002`) to v0.7.0 GA. Waiver scope = those 2 files; expiry = v0.7.0 GA (or row 30 completion); residual risk = adopters can't see the dashboard until then. | (to be archived) |
| 10 | `test_session_formalization_audit_is_archived` | `fix-required` | DELIB missing; insert. | — |
| 11 | `test_session_governance_principles_have_membase_records` | `fix-required` | `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` missing; insert. | — |
| 12 | `test_session_lifecycle_engagement_decisions_are_archived` | `fix-required` | DELIB missing; insert. | — |
| 13 | `test_session_lifecycle_engagement_records_are_in_membase` | `fix-required` | `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` missing; insert. | — |
| 14 | `test_session_self_initialization_decision_is_archived` | `fix-required` | DELIB missing; insert. | — |
| 15 | `test_session_self_initialization_records_are_in_membase` | `fix-required` | `GOV-SESSION-SELF-INITIALIZATION-001` missing; insert. | — |
| 16 | `test_standing_backlog_decision_is_archived` | `fix-required` | DELIB missing; insert. | — |
| 17 | `test_standing_backlog_is_formalized_as_governed_artifact` | `fix-required` | `GOV-STANDING-BACKLOG-001` missing; insert. | — |

`tests/scripts/test_memory_md_ceiling.py` (1):

| # | Test | Initial Classification | Rationale | DELIB |
|---|---|---|---|---|
| 18 | `test_memory_md_under_ceiling` | `fix-required` | Owner directive S330 (`DELIB-S330-SLICE-8-6-ROW-18-MEMORY-MD-TRIM-CHOICE`): trim MEMORY.md to <25KB per CLAUDE.md hook format. Phase 2 trim consolidates verbose multi-line entries into single-line hooks; detailed content moves to topic files in `memory/*.md`. | `DELIB-S330-SLICE-8-6-ROW-18-MEMORY-MD-TRIM-CHOICE` |

`tests/scripts/test_rehearse_isolation.py` (5):

| # | Test | Initial Classification | Rationale | DELIB |
|---|---|---|---|---|
| 19 | `test_execute_flag_enables_real_run` | `fix-required` | Driver returns exit 1 instead of 0; likely cascade from M2 path issue (#21). Investigate + fix together. | — |
| 20 | `test_run_summary_not_written_when_all_lanes_skipped` | `fix-required` | Same cascade. | — |
| 21 | `test_output_dir_override_in_sandbox_accepted` | `fix-required` | M2 path validation hardcodes Windows-style paths; rejects `/home/runner/work/...` Linux runner paths. Update regex to be platform-agnostic. | — |
| 22 | `test_output_dir_override_non_allowlisted_rejected` | `fix-required` | Regex pattern mismatch; same root cause as #21. | — |
| 23 | `test_run_summary_written_when_lane_returns_ok` | `fix-required` | Same cascade as #19. | — |

`tests/scripts/test_session_self_initialization.py` (13):

| # | Test | Initial Classification | Rationale | DELIB |
|---|---|---|---|---|
| 24 | `test_dashboard_and_report_are_written_with_time_series_kpi` | `fix-required` (BLOCKED on cross-cutting groundtruth.db CI gap) | **PROBED S330 Phase 1.** CI failure at line 850: `assert any(row["scope_confidence"] == "gtkb_inferred" for row in dashboard_data["history"])`. Root cause: `dashboard_data["history"]` is empty/lacks `gtkb_inferred` rows in CI. The `_inferred_history` function (`scripts/session_self_initialization.py:2890`) derives those rows from `groundtruth.db` version history. CI has no `groundtruth.db` (gitignored per `23a54af3` 2026-04-24 owner decision). Test PASSES locally where `groundtruth.db` is populated. Sub-classification: **same root cause as cross-cutting CI groundtruth.db gap (see §"Cross-cutting Phase 1.5 finding" below)**. | — |
| 25 | `test_emit_startup_service_payload_returns_full_codex_session_start_contract` | `fix-required` (BLOCKED on cross-cutting groundtruth.db CI gap) | **PROBED S330 Phase 1.** CI failure at line 1024: `assert freshness["validation"]["startup_payload_fresh"] is True`. Root cause: `_startup_freshness_metadata` (`scripts/session_self_initialization.py:5151-5157`) requires 5 local sources to be `present`; one of them is `groundtruth.db`. CI has no `groundtruth.db`, so `required_local_sources_ok = False` → `startup_payload_fresh = False`. Test PASSES locally where `groundtruth.db` is populated. Sub-classification: **same root cause as #24 + the cross-cutting gap below**. | — |
| 26-33 | 8× `test_smart_poller_section_*` | `fix-required` (root cause: stale CI dependency pin, NOT renamed function) | **PROBED S330 Phase 1.** All 8 fail with `AttributeError: module 'groundtruth_kb.project.doctor' has no attribute '_check_smart_bridge_poller'. Did you mean: '_check_bridge_poller'?`. The function DOES exist locally at `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1465`, added at commit `931157f2`. Root cause: `requirements-test.txt` pins `groundtruth-kb @ git+https://...@v0.6.1`. v0.6.1 predates `_check_smart_bridge_poller` (added post-S320). CI installs v0.6.1, tests target the local checkout's expected API surface. **Fix:** update `requirements-test.txt` to install `-e ./groundtruth-kb[search]` (use local source). Single dependency-pin fix unblocks all 8. | — |
| 34 | `test_smart_poller_section_diagnostic_supersedes_notification` (9th `_check_smart_bridge_poller`) | `fix-required` (same root cause as #26-33) | Same dependency-pin fix unblocks. | — |
| 35 | `test_startup_model_contains_role_governance_and_kpi_inventory` | `fix-required` | `KeyError: 'raw_current_total'` — startup model missing a KPI key; add it. | — |
| 36 | `test_top_priority_actions_come_from_standing_backlog` | `fix-required` (test-baseline drift) | **PROBED S330 Phase 1.** Local repro: `assert action_ids == ["GTKB-GOV-010"]` fails because `action_ids = ['GTKB-ENV-INVENTORY-001', 'GTKB-SYSTEMS-TERMINOLOGY-MAP-001', 'GTKB-GOV-010']`. Root cause: standing backlog has gained `GTKB-ENV-INVENTORY-001` and `GTKB-SYSTEMS-TERMINOLOGY-MAP-001` as active items above `GTKB-GOV-010`; production code returns top-3 (`scripts/session_self_initialization.py:934`). Test was written when `GTKB-GOV-010` was the sole top-priority. **Fix options:** (a) loosen test to `assert "GTKB-GOV-010" in action_ids` and `assert len(action_ids) <= 3`; (b) update the asserted list to match current backlog top-3; (c) reorder backlog. Recommend (a) — robust against future backlog evolution. NOT related to my S330 Slice 8 row 36/37 (`GTKB-PIP-INSTALL-ADOPTER-UX-001` / `GTKB-CI-COVERAGE-FOR-PLATFORM-001`); those IDs don't appear here. | — |

`tests/scripts/test_standing_backlog_harvest.py` (3):

| # | Test | Initial Classification | Rationale | DELIB |
|---|---|---|---|---|
| 37 | `test_standing_backlog_audit_finds_current_actionable_bridge_entries` | `fix-required` | Harvest tooling missing entry; investigate harvest logic. | — |
| 38 | `test_standing_backlog_audit_summarizes_membase_work_items_and_release_blockers` | `fix-required` | `KeyError: 'open'` — harvest summary missing 'open' key. | — |
| 39 | `test_standing_backlog_harvest_decision_is_archived` | `fix-required` | DELIB missing; insert. | — |

`tests/scripts/test_wrap_scan_hygiene_skip_dirs.py` (2):

| # | Test | Initial Classification | Rationale | DELIB |
|---|---|---|---|---|
| 40 | `test_scan_includes_claude_skills` | `fix-required` | `.claude/skills/` not in `SCAN_ROOTS`; extend scanner. | — |
| 41 | `test_scan_includes_scripts_dir` | `fix-required` | `scripts/` not in `SCAN_ROOTS`; extend scanner (probably same fix as #40). | — |

#### Security Scan failures (2)

| # | Job | Initial Classification | Rationale | DELIB |
|---|---|---|---|---|
| 42 | `Dependency Audit` (pip-audit) | `environmental` | Owner directive S330 (`DELIB-S330-SLICE-8-6-ROW-42-PIP-CVE-CHOICE`): pin pip in CI to a pre-CVE version. Phase 2: modify `.github/workflows/security-scan.yml` to pin pip BEFORE pip-audit runs; fallback to `--ignore-vuln CVE-2026-3219` if no safe version exists. May need to apply pin to other workflows that use pip-audit downstream. | `DELIB-S330-SLICE-8-6-ROW-42-PIP-CVE-CHOICE` |
| 43 | `Docker Scout (container CVEs)` | `waivable-for-rc1` | Owner directive S330 (`DELIB-S330-SLICE-8-6-ROW-43-DOCKER-SCOUT-WAIVER`): waive 2 specific CVE IDs (`CVE-2026-33845` gnutls28, `CVE-2026-5435` glibc). Scope: those 2 CVE IDs only; does not waive future CVEs. Expiry: base-image rebuild (soft v0.7.0 GA; hard v0.8.0). Residual risk: production-deployment hardening covers exposure. New backlog row at GA: `GTKB-DOCKER-SCOUT-CVE-WAIVER-EXPIRY-001`. | `DELIB-S330-SLICE-8-6-ROW-43-DOCKER-SCOUT-WAIVER` |

### Updated summary (post-Phase-1 probes S330)

- `fix-required`: 39 (16 governance_adoption + 5 rehearse_isolation + 10 session_self_init `_check_smart_bridge_poller`/KeyError + 1 row 24 + 1 row 25 + 1 row 36 + 3 standing_backlog_harvest + 2 wrap_scan_hygiene)
- `waivable-for-rc1`: 1 (governance_adoption dashboard files; rationale tied to row 30)
- `awaiting-investigation`: 0 (all 3 probes complete; rows 24/25/36 reclassified `fix-required`)
- **`awaiting-owner-decision`**: 3 (rows 18, 42, 43 — already DELIB-archived per S330 entries above)
- Total: 39 + 1 + 0 + 3 = 43 ✓

### Cross-cutting Phase 1.5 finding (S330): 19 rows blocked on CI groundtruth.db gap

**Discovery:** Phase 1 probes of rows 24, 25 revealed the same root cause that affects rows 1-17 (governance_adoption tests, except row 9 dashboard waiver): `groundtruth.db` was untracked from git per owner decision 2026-04-24 (commit `23a54af3` "chore: untrack groundtruth.db"). The CI workflow `release-candidate-gate.yml` does NOT seed `groundtruth.db` before running pytest. Empty/missing `groundtruth.db` → 19 tests fail in CI but pass locally:

- Rows 1-8, 10-17 (16 governance_adoption tests asserting `GOV-*`, `SPEC-*`, `DELIB-*` records exist via `KnowledgeDB(REPO_ROOT / "groundtruth.db").get_spec(...)`)
- Row 24 (`dashboard_data["history"]` derived from db version history)
- Row 25 (`startup_payload_fresh` requires `groundtruth.db` as one of 5 mandatory local sources)

**Original triage gap:** Catalog rows 1-17 classified as "fix-required: insert via `insert_spec` under formal-artifact-approval gate". Inserting records into the local (gitignored) `groundtruth.db` is **necessary but not sufficient** — CI cannot see those records.

**Strategy options requiring owner decision:**

- **Option A — CI seed step (recommended):** Add a `python scripts/seed_ci_membase.py` step in `release-candidate-gate.yml` BEFORE `release_candidate_gate.py`. Seed script reads canonical content from `.claude/rules/`, `AGENTS.md`, etc., and inserts the 16+ required records via `db.insert_spec()` / `db.insert_deliberation()`. Records derive from existing rule files (single source of truth preserved). Cost: ~1 new script + 1 workflow step.
- **Option B — Test-level fixtures:** Refactor 19 tests to scaffold their own `tmp_path/groundtruth.db` with required records via fixtures. Decouples tests from `REPO_ROOT/groundtruth.db`. Cost: ~19 test refactorings + 1 shared fixture module.
- **Option C — Minimal seed db fixture:** Create `tests/fixtures/groundtruth-seed.db` (small, tracked) with only the records the tests assert. Tests copy it to `REPO_ROOT/groundtruth.db` if not present. Cost: ~1 fixture file + 1 conftest step. Risk: fixture drift from production schema migrations.
- **Option D — Track minimal records-only db (rejected by owner Apr 24):** Reverts the 23a54af3 decision. Not recommended.

This decision is **escalated to owner via OWNER ACTION REQUIRED** before Phase 2 implementation begins for the 19 affected rows. Other 24 rows (smart-poller pin, M2 regex, scan-roots, harvest, security-scan) can proceed in parallel.

**Owner decision S330 (Phase 1.5):** Selected **Option A — CI seed script**. Decision archived as `DELIB-S330-SLICE-8-6-PHASE-1-5-CI-DB-SEED-CHOICE` (formal MemBase insertion deferred to Phase 4 REPORT). Implementation plan: (1) Write `scripts/seed_ci_membase.py` that reads canonical content from `.claude/rules/*.md` and other source-of-truth files, then calls `db.insert_spec()` / `db.insert_deliberation()` for the required 16+ records. (2) Add a workflow step to `.github/workflows/release-candidate-gate.yml` that runs the seed script BEFORE `release_candidate_gate.py`. (3) Records inserted locally first to confirm test pass; then CI workflow updated. (4) Records to seed are derived from the catalog rows 1-8, 10-17 (16 records) plus implicitly any other records referenced by rows 24, 25 once db has any populated history. Single source of truth preserved (rule files); CI converges with local environment.

### Phase 1 next steps

Per Slice 8.6 -003 REVISED-1 §"Owner-Input Protocol (F4 fix — one decision at a time)":

1. **Surface the FIRST `awaiting-owner-decision` row** via `OWNER ACTION REQUIRED` block (single question; stop turn). Order: row 18 (memory_md_ceiling) — the simplest decision, affects only documentation hygiene.
2. After owner answers + DELIB archived, surface the 2nd: row 42 (Dependency Audit pip CVE).
3. After owner answers + DELIB archived, surface the 3rd: row 43 (Docker Scout container CVEs).
4. After all 3 owner decisions captured, probe the 3 `awaiting-investigation` rows; classify based on probe results (no owner involvement unless investigation reveals additional ambiguity).
5. Phase 1 closes; Phase 2 (per-row fix/waive implementation) begins.



Original content below preserved as historical evidence for traceability.

Last updated: 2026-04-21 18:25 America/Los_Angeles

## Current State

Agent Red is in release-readiness recovery after a production-readiness inspection found P0/P1 blockers. The current repository head is `main@c372eef`, a release-evidence documentation commit. The latest full code candidate remains `main@e01e8ac` with green GitHub Actions evidence for Lint, Python Tests, Release Candidate Gate, SonarCloud, and Security Scan; `main@c372eef` also has green SonarCloud evidence and a fresh local non-deploying release-candidate gate pass.

- tracked generated production manifest with plaintext credentials,
- fail-open standalone admin behavior when deployed without an admin password,
- static fallback signing secrets reaching production if env vars are absent,
- commercial integration state durability and secure per-tenant restore have
  local implementation and non-deploying release-gate evidence.

## Completed Recovery Work

- Removed `scripts/deploy/production-gateway-generated.yaml` from the working tree.
- Ignored future generated production gateway YAML.
- Updated `scripts/deploy/restore-production-gateway.ps1` to write `_production-gateway-generated.local.yaml`.
- Added production startup guard in `src/app/lifecycle.py` requiring deployed environments to provide required admin, signing, public URL, and CORS settings.
- Hardened `src/app/standalone_auth.py` so staging/production do not allow passwordless admin access.
- Added `tests/security/test_production_config_guard.py`.
- Added `scripts/release_candidate_gate.py`.
- Added `.github/workflows/release-candidate-gate.yml`.
- Changed `.github/workflows/python-tests.yml` so full Python shards run on `develop` pushes.
- Changed `.github/workflows/security-scan.yml` so Semgrep scans outside `src/` and Docker Scout logs into ACR before building.
- Changed `.github/workflows/security-scan.yml` so Docker Scout uses scan-only ACR credentials and separate Docker Hub authentication secrets.
- Reduced the production Docker image vulnerability surface by removing the curl healthcheck dependency, upgrading Debian packages during build, and switching the healthcheck to Python stdlib.
- Added `pyOpenSSL>=26.0.0` to resolve dependency audit CVEs.
- Added Bandit config for the Cosmos-query B608 heuristic and verified Bandit medium/high gate passes.
- Added `.claude/skills/release-candidate-gate/SKILL.md` to make the non-deploying release gate an explicit local operator skill.
- Made `.claude` governance hooks, rules, and skills visible to git instead of leaving them hidden by the blanket `.claude/*` ignore.
- Added `GTKB-GOV-001`, `GTKB-GOV-002`, and `GTKB-GOV-003` to the top of `memory/work_list.md` for pending Tier A apply completion, release-gate skill upstreaming, and governance-adoption doctor work.
- Enabled the upstream GT-KB managed skills `gtkb-decision-capture`, `gtkb-bridge-propose`, and `gtkb-spec-intake` with their helper scripts.
- Added `.claude/rules/acting-prime-builder.md` so GT-KB Prime Builder skill labels map explicitly to Codex while the owner-directed acting-Prime exception is active.

## Regression Coverage

Observable regression coverage now includes:

- `tests/security/test_production_config_guard.py` for deployed startup config fail-closed behavior.
- `tests/scripts/test_release_candidate_gate.py` for release-gate manifest containment and Python-version checks.
- `scripts/release_candidate_gate.py` for local and CI release-candidate checks.
- `.github/workflows/release-candidate-gate.yml` for Python 3.12 security/config checks plus Windows frontend builds and widget tests.
- `.github/workflows/python-tests.yml` on `develop` pushes for full shard/coverage signal.
- `tests/scripts/test_groundtruth_governance_adoption.py` for GroundTruth adopter config, KnowledgeDB gate plugin config, governance hook/rule/skill presence, gitignore visibility, release workflow lanes, and work-queue ordering.
- The governance adoption test now also requires the three upstream GT-KB managed skills and the local acting-Prime role mapping rule.
- `python scripts\release_candidate_gate.py --skip-frontend` passed locally under Python 3.14 with Ruff E/F, import cycles, Bandit, pip-audit, and 147 targeted tests.
- `python scripts\release_candidate_gate.py` passed locally under Python 3.14 with secret manifest containment, Ruff E/F, import cycles, Bandit, pip-audit, Codex hook parity, and 186 targeted tests.
- `tests/test_host/test_build_contract.py::TestConfigurationDriftAcrossLayers::test_production_dockerfile_avoids_curl_healthcheck_dependency` verifies the production Dockerfile does not depend on curl for healthchecks.

## 2026-04-20 Risk Register Remediation Pass

Claim: Production GO remains blocked. The risk-register remediation target is not
to claim release readiness prematurely; it is to close, explicitly defer, or
supersede every blocker with governed evidence.

Historical evidence from that pass:

- Local branch was `main` at `869f867a` after the SonarCloud trigger, dependency, and organization-key fixes.
- The last green code candidate at that point was `main@869f867a`.
- Remote branch divergence: `origin/main...origin/develop` reports 23 commits
  unique to `main` and 0 commits unique to `develop`; `develop` no longer has
  unreconciled release-candidate commits ahead of `main`, but the branch-policy
  decision for future release provenance still needs owner/project disposition.
- Generated manifest containment: `scripts/deploy/production-gateway-generated.yaml`
  does not exist in the working tree, remains tracked, and is staged as a
  pending deletion in local git status.
- Generated local restore output is ignored by
  `.gitignore` via `scripts/deploy/_production-gateway-generated*.yaml`.
- Correct GitHub project confirmed by owner:
  `Remaker-Digital/agent-red-customer-engagement`.
- Local `.env.local` now identifies `AGENT_RED_GITHUB_REPO` as
  `Remaker-Digital/agent-red-customer-engagement` and
  `GROUND_TRUTH_GITHUB_REPO` as `Remaker-Digital/groundtruth-kb`.
- The local git remote and dashboard GitHub Actions links must remain aligned
  to `Remaker-Digital/agent-red-customer-engagement`.
- Correct-project repository secrets visible through
  `gh secret list --repo Remaker-Digital/agent-red-customer-engagement` include
  `SONAR_TOKEN`, last updated 2026-04-10T03:57:11Z, plus scan-only
  `ACR_SCOUT_USERNAME` and `ACR_SCOUT_PASSWORD`, last updated 2026-04-21.
  Docker Hub credentials for the Docker Scout GitHub Action are not currently
  configured.
- Correct-project workflow inventory now includes active `SonarCloud` and
  `Security Scan` workflows in
  `Remaker-Digital/agent-red-customer-engagement`.
- GitHub Actions evidence for the current candidate `main@869f867a` is green
  for Release Candidate Gate, Python Tests, Lint, and SonarCloud. Release
  Candidate Gate included the Python 3.12 release gate and Windows
  frontend/widget gate. The runs were created 2026-04-21T13:59:04Z and
  completed by 2026-04-21T14:07:58Z.
- Security Scan on `main@869f867a` failed in the Docker Scout job before image
  scanning because `ACR_USERNAME` was not configured as a repository secret.
  Semgrep SAST, Bandit, and pip-audit jobs passed in the same run. The
  workflow has since been changed to use scan-only `ACR_SCOUT_USERNAME` and
  `ACR_SCOUT_PASSWORD` secrets for Docker Scout ACR login.
- Docker Scout is connected to `acragentredeastus.azurecr.io` through the
  Docker Scout Azure Container Registry integration using an Azure-created
  read-only registry token.
- Security Scan on `main@e3a4000b` advanced past scan-only secret validation,
  ACR login, and local image build, then failed in `docker/scout-action@v1`
  with `no credential found for "https://index.docker.io/v1/"`. The workflow
  now requires separate Docker Scout Hub credentials before running Scout:
  `DOCKER_SCOUT_HUB_USER` and `DOCKER_SCOUT_HUB_PAT`.
- SonarCloud release evidence is now cleared for the exact candidate:
  `.github/workflows/sonarcloud.yml` runs on `main` and manual dispatch,
  filters the known native dependency from CI install, validates
  `SONAR_TOKEN`, and uses the discoverable Sonar organization key
  `mike-remakerdigital`.
- Prior SonarCloud and Security Scan failures harvested from any
  non-authoritative repository are no longer release evidence for Agent Red.
- Local non-deploying release candidate gate passed after the wrapped-blocker
  parser fix: `python scripts/release_candidate_gate.py --skip-frontend`
  completed Ruff E/F, import-cycle detection, Bandit, pip-audit, Codex hook
  parity, and 183 targeted tests.

Blocker disposition:

- Credential lifecycle for values exposed in the deleted generated manifest is
  owner-managed outside Codex scope. Codex must not ask Mike to rotate keys; when
  credentials change, Mike will update `env.local`, and Codex may consume,
  validate, or upload those values only when the task requires it and Mike has
  authorized that use.
- Owner must decide whether git history requires secret purging: still
  owner-gated. Do not close without an explicit owner decision.
- GitHub SonarCloud must pass with valid `SONAR_TOKEN` and project
  configuration: cleared for `main@869f867a`.
- GitHub Security Scan must pass with valid Docker Scout credentials: was still
  blocked in this pass. `ACR_SCOUT_USERNAME` and `ACR_SCOUT_PASSWORD` were configured, but
  `docker/scout-action@v1` also required Docker Hub authentication through
  `DOCKER_SCOUT_HUB_USER` and `DOCKER_SCOUT_HUB_PAT`. This blocker was later
  cleared in the 2026-04-21 Docker Scout clearance pass below.
- `main` and `develop` release provenance: operational divergence is cleared
  for the current candidate (`develop` is 0 commits ahead of `main`), but the
  release-branch policy still needs owner/project disposition.
- Full Python 3.12 CI on the current candidate commit: cleared for
  `main@869f867a` by green Release Candidate Gate and Python Tests runs.
- Commercial durability launch scope must be decided for
  Shopify/Stripe/action-executor in-memory paths: still owner/product-scope
  gated.

Recommended next actions:

- Prime Builder: do not request credential rotation. Treat credential lifecycle
  as owner-managed outside Codex scope; when Mike updates `env.local`, consume,
  validate, or upload the updated values only when the task requires it and Mike
  has authorized that use.
- Owner: decide whether repository history must be purged for the exposed
  manifest.
- Prime Builder: keep local remote, dashboard GitHub Actions evidence, and
  generated startup reports aligned to
  `Remaker-Digital/agent-red-customer-engagement`.
- Repo admin: configure valid `DOCKER_SCOUT_HUB_USER` and
  `DOCKER_SCOUT_HUB_PAT` repository secrets for Docker Scout Hub
  authentication, then rerun Security Scan on the exact candidate. Completed
  in the 2026-04-21 Docker Scout clearance pass below.
- Owner/project: decide the release-branch policy now that `develop` has no
  commits ahead of `main` and `main` is 23 commits ahead of `develop`.

## 2026-04-21 Docker Scout Clearance Pass

Claim: The GitHub Security Scan release blocker is cleared for the latest full code candidate.

Current evidence:

- Latest full code candidate: `main@e01e8ac154675ca29a80a4cdfd0a9056dd00307c`.
- GitHub Actions on `main@e01e8ac` are green for Lint, Python Tests, Release Candidate Gate, SonarCloud, and Security Scan.
- Security Scan run `24731909565` completed successfully on `main@e01e8ac` after Docker Scout ACR and Docker Hub credentials were configured.
- Docker Scout ACR credentials are present as repository secrets `ACR_SCOUT_USERNAME` and `ACR_SCOUT_PASSWORD`.
- Docker Hub credentials are present as repository secrets `DOCKER_SCOUT_HUB_USER` and `DOCKER_SCOUT_HUB_PAT`.
- Security Scan run `24731386383` previously proved Docker Scout authentication was working but failed on high CVEs in Debian packages pulled into the production image.
- Commit `e01e8ac` removed the curl healthcheck dependency, upgraded Debian packages during image build, and switched the production healthcheck to Python stdlib.
- Local targeted regression passed: `python -m pytest tests\test_host\test_build_contract.py::TestConfigurationDriftAcrossLayers::test_production_dockerfile_avoids_curl_healthcheck_dependency tests\multi_tenant\test_s175_scaling_680.py::TestUvicornWorkers::test_dockerfile_has_four_workers tests\multi_tenant\test_s175_scaling_680.py::TestLifecycleIntegration::test_dockerfile_has_tini_entrypoint -q --tb=short`.
- Local governance regression passed: `python -m pytest tests\scripts\test_groundtruth_governance_adoption.py -q --tb=short`.
- Standing backlog harvest regression passed: `python -m pytest tests\scripts\test_standing_backlog_harvest.py -q --tb=short`.
- Standing backlog source audit now reports only owner/project-gated release blockers after the Security Scan blocker is removed from this record.

Blocker disposition:

- GitHub Security Scan must pass with valid Docker Scout credentials: cleared for `main@e01e8ac` by run `24731909565`.
- Credential lifecycle for values exposed in the deleted generated manifest is owner-managed outside Codex scope. Codex must not ask Mike to rotate keys; when credentials change, Mike will update `env.local`, and Codex may consume, validate, or upload those values only when the task requires it and Mike has authorized that use.
- Owner must decide whether git history requires secret purging: still owner-gated. Do not close without an explicit owner decision.
- `main` and `develop` release provenance: operational divergence is cleared for the current candidate, but the release-branch policy still needs owner/project disposition.
- Commercial integration state for Shopify, Stripe, and action-executor paths
  must be durably persisted per tenancy and recoverable from a durable, secure
  tenant backup.

## 2026-04-21 GTKB-GOV-006 Evidence Freshness Pass

Claim: The release-readiness blocker list is current as of `main@c372eef`; production GO remains blocked only by owner/project decisions.

Current evidence:

- Current repository head: `main@c372eef04f854b6216afc16ca88eae9485b34ccc`.
- Commit `c372eef` modifies only `memory/release-readiness.md` relative to its parent and records green Security Scan evidence.
- GitHub Actions on `main@c372eef` show SonarCloud run `24732405946` completed successfully.
- GitHub Actions on `main@e01e8ac` show Lint run `24731899661`, Python Tests run `24731899611`, Release Candidate Gate run `24731899768`, SonarCloud run `24731899451`, and Security Scan run `24731909565` completed successfully.
- Branch divergence from `git rev-list --left-right --count origin/main...origin/develop` is `29 0`: `origin/main` is 29 commits ahead of `origin/develop`; `origin/develop` has no commits ahead of `origin/main`.
- Standing backlog source audit reports four remaining release blockers, matching the list below.
- Local non-deploying release-candidate gate passed on the checked-out tree: `python scripts/release_candidate_gate.py --skip-frontend`. The gate completed secret manifest containment, Ruff E/F, import-cycle detection, Bandit, pip-audit, Codex hook parity, and 185 targeted tests.

Blocker disposition:

- Credential lifecycle for values exposed in the deleted generated manifest remains owner-managed outside Codex scope. Codex must not ask Mike to rotate keys.
- Secret-history purge remains owner-gated. Do not close without an explicit owner decision.
- Release-branch provenance policy remains owner/project-gated. Operational divergence is known and bounded (`develop` is 0 commits ahead of `main`), but the durable policy decision is still open.
- Commercial durability launch scope remains owner/product-scope gated for Shopify/Stripe/action-executor in-memory paths.

## 2026-04-21 Option 3 Release Blocker Verification Pass

Claim: The selected release-blocker focus did not uncover a current technical gate failure; production GO remains blocked by the four governed owner/project disposition items below.

Current evidence:

- Checked-out branch: `main`.
- Current repository head: `main@c372eef04f854b6216afc16ca88eae9485b34ccc`.
- Branch divergence from `git rev-list --left-right --count origin/main...origin/develop` remains `29 0`: `origin/main` is 29 commits ahead of `origin/develop`; `origin/develop` has no commits ahead of `origin/main`.
- Local non-deploying release-candidate gate passed on the checked-out tree: `python scripts/release_candidate_gate.py`. The gate completed secret manifest containment, Ruff E/F, import-cycle detection, Bandit medium/high scan, pip-audit, Codex hook parity, and 185 targeted tests.
- Standing backlog source audit passed and reports exactly four release blockers, matching the remaining blocker list below: `python scripts/audit_standing_backlog_sources.py`.
- GitHub Actions evidence from `gh run list --repo Remaker-Digital/agent-red-customer-engagement --branch main --limit 10` shows the latest `main` runs still green for SonarCloud on `main@c372eef`, plus Security Scan, Lint, Release Candidate Gate, Python Tests, and SonarCloud on the latest full code candidate `main@e01e8ac`.

Blocker disposition:

- Credential lifecycle for values exposed in the deleted generated manifest remains owner-managed outside Codex scope. Codex must not ask Mike to rotate keys.
- Secret-history purge remains owner-gated. Do not close without an explicit owner decision.
- Release-branch provenance policy remains owner/project-gated. Operational divergence is known and bounded (`develop` is 0 commits ahead of `main`), but the durable policy decision is still open.
- Commercial durability launch scope remains owner/product-scope gated for Shopify/Stripe/action-executor in-memory paths.

## 2026-04-21 Resolve Release Blockers Freshness Pass

Claim: The requested release-blocker resolution pass found no remaining local
technical gate failure. The remaining blockers are now limited to the governed
owner/project disposition items below.

Current evidence:

- Checked-out branch: `main`.
- Current repository head: `main@c372eef04f854b6216afc16ca88eae9485b34ccc`.
- Branch divergence from `git rev-list --left-right --count origin/main...origin/develop` remains `29 0`: `origin/main` is 29 commits ahead of `origin/develop`; `origin/develop` has no commits ahead of `origin/main`.
- GitHub Actions evidence from `gh run list --repo Remaker-Digital/agent-red-customer-engagement --branch main --limit 15` remains green for SonarCloud on `main@c372eef`, plus Security Scan, Lint, Release Candidate Gate, Python Tests, and SonarCloud on latest full code candidate `main@e01e8ac`.
- Local release gate passed: `python scripts/release_candidate_gate.py`. The gate completed secret manifest containment, Ruff E/F, import-cycle detection, Bandit medium/high scan, pip-audit, Codex hook parity, and 186 targeted tests.
- Standing backlog source audit passed: `python scripts/audit_standing_backlog_sources.py`. It reports four release blockers, matching the remaining blocker list below.

Blocker disposition:

- Credential lifecycle for values exposed in the deleted generated manifest remains owner-managed outside Codex scope. Codex must not ask Mike to rotate keys.
- Secret-history purge remains owner-gated. Do not close without an explicit owner decision.
- Release-branch provenance policy remains owner/project-gated. Operational divergence is known and bounded (`develop` is 0 commits ahead of `main`), but the durable policy decision is still open.
- Commercial durability launch scope remains owner/product-scope gated for Shopify/Stripe/action-executor in-memory paths.

## Remaining Release Blockers

None as of the 2026-04-21 commercial durability implementation pass.

## 2026-04-21 Owner Credential Lifecycle Disposition

Claim: The credential lifecycle blocker is closed by owner disposition.

Evidence:

- Owner replied `Close` to the credential lifecycle disposition question.
- The standing directive remains unchanged: credential lifecycle is
  owner-managed outside Codex scope, and Codex must not ask Mike to rotate keys.

Blocker disposition:

- Credential lifecycle for values exposed in the deleted generated manifest:
  closed by owner disposition.
- Active release blocker list now contains three remaining owner/project
  disposition items: secret-history purge, release-branch provenance policy, and
  commercial durability launch scope.

## 2026-04-21 Owner Secret-History Purge Disposition

Claim: The secret-history purge blocker is closed by owner disposition.

Evidence:

- Owner replied `Close` to the secret-history purge disposition question.

Blocker disposition:

- Git history purge for the exposed generated manifest: closed by owner
  disposition.
- Active release blocker list now contains two remaining owner/project
  disposition items: release-branch provenance policy and commercial durability
  launch scope.

## 2026-04-21 Owner Release-Branch Provenance Disposition

Claim: The release-branch provenance blocker is closed by owner disposition.

Evidence:

- Owner replied `Close` to the release-branch provenance policy disposition
  question.
- Current recorded branch evidence remains `origin/main...origin/develop` at
  `29 0`: `origin/develop` has no commits ahead of `origin/main`.

Blocker disposition:

- Release-branch provenance policy for `main`/`develop`: closed by owner
  disposition.
- Active release blocker list now contains one remaining owner/product-scope
  disposition item: commercial durability launch scope.

## 2026-04-21 Owner Commercial Durability Scope Decision

Claim: Commercial durability is in launch scope and remains release-blocking
until implemented and verified.

Evidence:

- Owner stated that integration state for each tenancy must be durable.
- Owner stated that it must be possible to fully restore the configuration of a
  tenancy from a durable, secure backup.

Blocker disposition:

- The commercial durability launch-scope question is resolved: Shopify,
  Stripe, and action-executor commercial integration state durability is in
  scope.
- The active release blocker is now implementation and verification of durable
  per-tenant state plus secure restore, not an owner-decision question.

## 2026-04-21 Commercial Durability Implementation Pass

Claim: The commercial durability release blocker is cleared by local
implementation and non-deploying release-gate evidence.

Evidence:

- Added Cosmos schema containers for durable commercial runtime state and
  encrypted commercial-state backups: `commercial_state` and
  `commercial_state_backups`.
- Added `src/integrations/commercial_state_store.py` with Cosmos-backed
  staging/production persistence, explicit local/test in-memory storage, and
  encrypted tenant backup/restore operations.
- Rewired the integration framework admin API sync state, event logs, and HITL
  configuration through the commercial state store.
- Rewired `ActionExecutor` pending actions, HITL overrides, and audit entries
  through the commercial state store so pending approval state survives executor
  recreation.
- Rewired Stripe usage counters, Stripe pack balances, Shopify subscription
  state, and Stripe webhook reset/pack-credit flows through the commercial state
  store.
- Added release-gate regression coverage for commercial state backup/restore,
  integration schema, action executor persistence, admin integration framework
  state, Stripe consumption, Shopify billing, and Stripe webhooks.
- Local focused regression passed: `python -m pytest
  tests/integrations/test_action_executor.py
  tests/integrations/test_admin_integration_framework_api.py
  tests/integrations/test_usage_consumption.py
  tests/integrations/test_shopify_billing.py
  tests/unit/test_shopify_billing.py tests/unit/test_stripe_webhooks.py
  tests/integrations/test_commercial_state_store.py
  tests/integrations/test_cosmos_schema_extensions.py
  tests/scripts/test_standing_backlog_harvest.py -q --tb=short`.
- Local non-deploying release gate passed with frontend skipped: `python
  scripts/release_candidate_gate.py --skip-frontend`. The gate completed secret
  manifest containment, Ruff E/F, import-cycle detection, Bandit medium/high,
  pip-audit, Codex hook parity, and 362 targeted tests.

Blocker disposition:

- Commercial integration state durability and secure tenant restore: cleared by
  implementation and local release-gate evidence.
- Active release blocker list is empty as of this pass.

## Governance Notes

- Relevant prior deliberations searched and cited in the 2026-04-19 insight report: `DELIB-0560`, `DELIB-0565`, `DELIB-0602`, `DELIB-0603`.
- Current KnowledgeDB records: `DOC-release-readiness-recovery` v2 and `DOC-groundtruth-governance-adoption-2026-04-19` v1.
- Current Deliberation Archive record: `DELIB-0829` v1 for the owner governance-adoption directive and implementation evidence.
- Current role-governance decision: `DELIB-0830` v1 records the owner directive that Loyal Opposition/Codex assumes the acting Prime Builder role while canonical Prime Builder is unavailable.
- Current role-portability principle: any capable AI harness may assume Prime Builder or Loyal Opposition when assigned by the owner; the assigned harness must enable that role's skills, plugins, hooks, directives, and responsibilities to the extent possible, and when the bridge is available the counterpart is always Loyal Opposition.
- Current GT-KB installation principle: when GT-KB is installed, the project must be fully configured for Prime Builder; if multiple capable harnesses are installed, configuration should be prepared for all of them so the owner can assign Prime Builder and the non-Prime bridge participant assumes Loyal Opposition.
- Owner approval to continue and modify all necessary files was received in-session.
- This topic should be updated again after GitHub CI, owner-managed credential-state changes, and branch reconciliation are complete.
- The release-candidate gate now treats governance adoption as part of production readiness, not a separate manual checklist.
