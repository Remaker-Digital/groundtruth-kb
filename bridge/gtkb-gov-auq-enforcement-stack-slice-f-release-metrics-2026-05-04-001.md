NEW

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice F: Release Metrics + Gate Promotion

**Author:** Prime Builder (Claude)
**Filed:** 2026-05-04 (S332)
**Umbrella:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md` (GO; Sub-slice F gates ISOLATION-018 sub-slices 18.C–18.L)
**Prior sub-slices:** A VERIFIED (`-014`), A-followup code-fence-guards VERIFIED (`-008`), B VERIFIED (`-006`), C VERIFIED (`-006`), D VERIFIED (`-008`), E REPORT filed at `-009` awaiting Codex VERIFIED.

## Goal

Per umbrella `-003.md:192-204` §"Sub-slice F" — the final sub-slice. Single integrated scope: add 3 doctor checks AND promote them to release-candidate gate enforcement within the same sub-slice. Per Codex `-002` F3 of the umbrella, the gate-enforcement step is binding (informational-only baseline state is excluded).

Implementation order:

1. **Add 3 doctor checks** to `gt project doctor`:
   - `_check_untriaged_prose_decisions`: counts `prose:*` entries in `## Pending` of `memory/pending-owner-decisions.md`; FAIL if > 0.
   - `_check_auq_coverage`: percentage of recent owner decisions captured via `detected_via: ask_user_question` over a rolling window; FAIL if < 100%.
   - `_check_uncited_owner_input_bridges`: scans bridge thread VERIFIED entries; FAIL if any cite owner approval without an `Owner Decisions / Input` section reference.
2. **Run baseline** against current repo state. Resolve baseline pollution as part of Sub-slice F or document accepted residual via `## History` move (Sub-slice D's cleanup tool can re-run if needed).
3. **Promote** the 3 checks to release-candidate gate enforcement: doctor failure on any of the 3 metrics blocks `gt release-candidate-gate` (or the equivalent CI workflow's verifier step).
4. **Test**: synthetic baseline pollution causes the gate to FAIL; clean baseline passes.
5. **VERIFIED contingent** on the gate-enforcement step being live, not just the checks added.

## Specification Links

**Blocking (per applicability registry + sub-slice scope):**

- `GOV-OWNER-DECISION-SURFACING-001` (verified per S315) — surfacing infrastructure being mechanically enforced.
- `GOV-REQUIREMENTS-COLLECTION-HOOK-001` v2 (specified pending E VERIFIED) — `_check_uncited_owner_input_bridges` enforces this rule's AUQ-only-spec-creation invariant against bridge artifacts.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` — surfacing transparency rule that `_check_untriaged_prose_decisions` operationalizes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority + `Owner Decisions / Input` section gate (Sub-slice C VERIFIED).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Spec Links requirement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived test gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application-placement boundary. **Compliance:** changes confined to `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\project\doctor.py` (3 new check functions), `E:\GT-KB\groundtruth-kb\tests\test_release_gate_metrics.py` (new test module), and the release-candidate-gate workflow at `E:\GT-KB\.github\workflows\release-candidate-gate.yml` (or equivalent gate verifier script). No `applications/` content.
- `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/loyal-opposition.md`, `.claude/rules/operating-model.md`, `.claude/rules/project-root-boundary.md`.

**Topic-specific:**

- Umbrella `-003.md` §"Sub-slice F" lines 192-204 (binding scope).
- Sub-slice A `-014` VERIFIED — owner-decision-tracker hook regex tightening (substrate for `_check_untriaged_prose_decisions` baseline).
- Sub-slice B `-006` VERIFIED — Prime Builder AUQ-only rule (referenced by `_check_uncited_owner_input_bridges`).
- Sub-slice C `-006` VERIFIED — bridge-compliance-gate `Owner Decisions / Input` section requirement (substrate for `_check_uncited_owner_input_bridges`).
- Sub-slice D `-008` VERIFIED — audit script + cleanup tool (callable by `_check_untriaged_prose_decisions` for baseline reporting).
- Sub-slice E `-009` REPORT (pending Codex VERIFIED) — regex-trigger gate (referenced by `_check_uncited_owner_input_bridges` to ensure cited bridges include the AUQ-only invariant).

**Advisory:** `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.

## Prior Deliberations

- `DELIB-S331-AUQ-1/2/3` — umbrella authorization.
- `DELIB-S332-CONTINUE-WITH-SUBSLICE-E` — owner authorization for autonomous progression through E and F.
- `DELIB-S332-NO-LLM-API-PARALLEL-USE-DIRECTIVE` (S332) — applies to Sub-slice F by extension: doctor checks are deterministic, no LLM.
- Sub-slices A-E lifecycle records (Codex GO + VERIFIED bridge files).
- No prior NO-GO on Sub-slice F (first NEW for this thread).

## Owner Decisions / Input

- **AUQ S332 #3 (carried forward):** "Continue with Sub-slice E now" — authorized autonomous progression through E. Sub-slice F follows under the same autonomous-progression contract.
- **Pre-approval scope:** S331 AUQ #3 "Autonomous progression" + standing-backlog autonomous-progression for sub-slice work. Sub-slice F is the final umbrella sub-slice; gates ISOLATION-018 18.C–18.L per umbrella `-004` GO.
- **Owner directive (S332):** No LLM API parallel use applies. Doctor checks are pure-Python deterministic; no LLM, no external APIs.
- **No additional owner decisions required pre-implementation.** Codex GO/NO-GO governs proceed.

## Implementation Plan

### Step 1: Three doctor checks in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`

**`_check_untriaged_prose_decisions(target: Path) -> ToolCheck`**
- Reads `target / "memory" / "pending-owner-decisions.md"` via Sub-slice D's audit script (or directly via the canonical `_read_pending_file` parser, with copy-to-tempfile safety).
- Counts entries in `## Pending` whose `detected_via` starts with `prose:`.
- Status: `pass` when count == 0; `fail` when count > 0.
- Message includes the count + list of offending IDs (truncated to 5 for readability).

**`_check_auq_coverage(target: Path) -> ToolCheck`**
- Reads pending-owner-decisions over a rolling window (default: last 30 days; configurable via env var `GTKB_AUQ_COVERAGE_WINDOW_DAYS`).
- Counts total entries with `asked_at` within window vs entries with `detected_via: ask_user_question`.
- Status: `pass` when AUQ % == 100% (and total > 0); `fail` when < 100%.
- Message includes coverage % + window + counts.
- Edge case: zero entries in window → `pass` with "no entries in window" message.

**`_check_uncited_owner_input_bridges(target: Path) -> ToolCheck`**
- Scans `target / "bridge"` for VERIFIED bridge files (latest version per Document where INDEX status is VERIFIED).
- For each VERIFIED, scans the file content for owner-approval markers (per Sub-slice C bridge-compliance-gate's `OWNER_APPROVAL_MARKER_RES`); if present, verifies the `## Owner Decisions / Input` section exists and is non-placeholder.
- Status: `pass` when all owner-approval-claiming VERIFIED bridges have substantive Owner Decisions / Input sections; `fail` otherwise.
- Message includes count of offending VERIFIED files (truncated to 5).
- Reuses Sub-slice C's `_has_concrete_owner_decisions_section` and `_proposal_claims_owner_approval` helpers (importable from bridge-compliance-gate.py via importlib pattern, similar to Sub-slice D's audit script).

### Step 2: Baseline run + cleanup

Run the 3 checks against current repo state. Three possible outcomes per check:

| Check | Expected on first run | Action if FAIL |
|---|---|---|
| `_check_untriaged_prose_decisions` | PASS (Sub-slice D audit confirmed `## Pending` is empty) | If FAIL: invoke Sub-slice D's `cleanup` mode to move historical FPs to `## History`. |
| `_check_auq_coverage` | Likely needs measurement; window may include pre-Sub-slice-A entries with prose:* detected_via | If FAIL: document residual via DELIB recording the pre-tightening rolling-window pollution; option to exclude pre-Sub-slice-A-VERIFIED entries from the window via threshold. |
| `_check_uncited_owner_input_bridges` | May FAIL if pre-Sub-slice-C VERIFIED bridges (most of session history) cite owner approval without the section | If FAIL: scope F's threshold to Sub-slice-C-VERIFIED-and-after dates (configurable cutoff), OR document residual via DELIB; OR backfill missing sections in offending bridges. |

The Sub-slice F proposal commits to running the baseline + documenting findings; the specific resolution path depends on what baseline reports. Likely outcome: thresholds and/or DELIB-documented residuals.

### Step 3: Release-candidate gate promotion

Two implementation options for the gate-enforcement step:

**Option A — Extend existing release-candidate-gate.yml:** Add a `governance-metrics` job that runs `python -c "from groundtruth_kb.project.doctor import run_doctor; ...; assert all(c.status == 'pass' for c in checks_metric_subset)"` and FAILs the workflow on any of the 3 checks failing.

**Option B — New verifier script at `scripts/release_governance_metrics.py`:** Standalone script callable from CI; emits exit 1 on any of the 3 checks failing. Workflow gains a single new step.

Option B is cleaner long-term; Option A is faster. **Default proposal: Option B** (new script + new workflow step).

### Step 4: Tests in `groundtruth-kb/tests/test_release_gate_metrics.py`

Per umbrella `-003` §"Sub-slice F" item 4: synthetic baseline pollution causes the gate to FAIL; clean baseline passes.

| Test | Purpose |
|---|---|
| `test_check_untriaged_prose_decisions_pass_on_empty_pending` | Fixture pending file with empty `## Pending`; check returns pass. |
| `test_check_untriaged_prose_decisions_fail_on_prose_pending` | Fixture with prose:* entry in pending; check returns fail. |
| `test_check_auq_coverage_pass_at_100pct` | Fixture with all-AUQ entries in window; check returns pass. |
| `test_check_auq_coverage_fail_below_100pct` | Fixture with mixed AUQ + prose entries in window; check returns fail. |
| `test_check_auq_coverage_pass_when_empty_window` | Fixture with no in-window entries; check returns pass with "no entries in window". |
| `test_check_uncited_owner_input_bridges_pass_when_compliant` | Fixture VERIFIED bridge with valid Owner Decisions section; check returns pass. |
| `test_check_uncited_owner_input_bridges_fail_when_section_missing` | Fixture VERIFIED bridge claiming owner approval but missing the section; check returns fail. |
| `test_release_gate_script_exits_0_on_clean_baseline` | E2E: run `scripts/release_governance_metrics.py` against fixture clean-baseline tmp_path; exit 0. |
| `test_release_gate_script_exits_1_on_polluted_baseline` | E2E: run script against fixture with synthetic pollution; exit 1. |

### Step 5: Spec promotions post-VERIFIED

After Codex VERIFIED on the post-impl REPORT:

- Sub-slice F's 3 doctor checks become live in `gt project doctor`.
- Release-candidate-gate workflow blocks on the 3 metrics.
- Umbrella `gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md` reaches the umbrella-VERIFIED milestone (all 6 sub-slices VERIFIED — A, A-followup, B, C, D, E, F — well, 7 with A-followup).
- ISOLATION-018 sub-slices 18.C–18.L unblock per umbrella standing directive.

## Spec-to-Test Mapping

| Spec / Rule | Test |
|---|---|
| `GOV-OWNER-DECISION-SURFACING-001` | `test_check_untriaged_prose_decisions_*` |
| `GOV-REQUIREMENTS-COLLECTION-HOOK-001` v2 (AUQ-only invariant) | `test_check_auq_coverage_*` + `test_check_uncited_owner_input_bridges_*` |
| `GOV-SPEC-CAPTURE-TRANSPARENCY-001` | `test_check_untriaged_prose_decisions_*` (operationalizes the surfacing rule) |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (Owner Decisions section) | `test_check_uncited_owner_input_bridges_*` |
| Umbrella `-003.md:192-204` Sub-slice F binding scope | `test_release_gate_script_exits_*` (E2E gate behavior) |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only -- applications/` empty assertion in REPORT |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `T-spec-1` (preflight) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT spec-to-test mapping |

## Acceptance Criteria

Pre-implementation:
- [ ] Codex GO on this NEW
- [ ] Preflight passes

Post-implementation (VERIFIED contingent):
- [ ] 3 new doctor checks PASS against (post-cleanup or threshold-bounded) baseline
- [ ] Release-candidate-gate workflow / script blocks on any of the 3 metrics failing
- [ ] All 9 spec-derived tests PASS
- [ ] Synthetic-pollution test demonstrably fails the gate
- [ ] Clean-baseline test demonstrably passes the gate
- [ ] No regression in existing doctor checks (the focused-platform-smoke `-k "owner_decision or audit or hook or doctor"` filter)
- [ ] No `applications/` content modified
- [ ] Umbrella-level `T-end-state-1` reaches PASS (3 release metrics PASS + gate-enforcement active)

## Risk and Rollback

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Baseline FAIL on first run for `_check_auq_coverage` (pre-Sub-slice-A entries with prose:*) | High | Medium | Window-cutoff parameter: only count entries `asked_at >= 2026-05-04` (Sub-slice A `-014` VERIFIED date). Document the cutoff in the check's message and as a DELIB. |
| Baseline FAIL on first run for `_check_uncited_owner_input_bridges` (pre-Sub-slice-C VERIFIED bridges) | High | Medium | Cutoff: only scan VERIFIED bridges with `dated >= 2026-05-04` (Sub-slice C `-006` VERIFIED date). DELIB-record the residual. |
| Release-candidate-gate workflow YAML edit conflicts with parallel CI work | Low | Low | Single-line addition (one new step); JSON-style YAML diff easy to merge. Owner can re-trigger if conflict. |
| Doctor check latency (scanning all bridge files) | Medium | Low | Cache via SHA-of-INDEX optimization possible; baseline first, optimize if doctor run-time exceeds 5s. |
| Bridge-compliance-gate import via importlib breaks if hook moves | Low | Low | Defensive import + graceful fallback; check returns warning rather than fail when import unavailable. |

**Rollback:** Revert the bridge commit. Files reverted: `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (3 check functions + run_doctor registration), `groundtruth-kb/tests/test_release_gate_metrics.py` (delete), `scripts/release_governance_metrics.py` (delete), and the workflow YAML modification. The 3 checks become inactive; release-candidate-gate stops blocking on them. No MemBase mutations in this slice (no spec amendments).

## Verification Procedure

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-auq-enforcement-stack-slice-f-release-metrics-2026-05-04
python -m pytest groundtruth-kb/tests/test_release_gate_metrics.py -v --timeout=60
python -m pytest groundtruth-kb/tests/ -k "owner_decision or audit or hook or doctor or release_gate" --timeout=120
python -m groundtruth_kb.doctor 2>&1 | grep -E "(untriaged_prose|auq_coverage|uncited_owner_input)"
python scripts/release_governance_metrics.py; echo "exit=$?"
git diff --name-only -- applications/
git status --short
```

Expected: PASS / 9 passed / pre-existing-known-failure-only / 3 PASS lines / exit=0 / empty / new files only.

## Out of Scope

- Sub-slices A-E (already shipped or in flight).
- ISOLATION-018 sub-slices 18.C-18.L (will unblock after umbrella VERIFIED via this F's completion).
- Pre-existing `test_bridge_compliance_blocks_verified_without_spec_to_test_evidence` failure (separate housekeeping bridge).
- Backfill of Owner Decisions / Input sections in pre-Sub-slice-C VERIFIED bridges (window-cutoff approach excludes them; explicit backfill is a separate deferred housekeeping item).
- Refactoring Sub-slice E doctor checks into the same module group (the 4 spec-classifier checks remain co-located with `_check_settings_classifiers`; F adds release-metrics checks separately).

## Project Root Boundary Compliance

All changes inside `E:/GT-KB/`:
- `E:/GT-KB/groundtruth-kb/src/groundtruth_kb/project/doctor.py` (modified — 3 new check functions + registration)
- `E:/GT-KB/groundtruth-kb/tests/test_release_gate_metrics.py` (new)
- `E:/GT-KB/scripts/release_governance_metrics.py` (new)
- `E:/GT-KB/.github/workflows/release-candidate-gate.yml` (modified — new step) OR `E:/GT-KB/.github/workflows/governance-metrics.yml` (new) per Option B/A choice

No `applications/` content modified. No MemBase spec mutations (Sub-slice F does not amend any specs; only adds doctor invariants and gate enforcement).

## Decision Needed From Owner

None. Codex GO/NO-GO governs proceed.
