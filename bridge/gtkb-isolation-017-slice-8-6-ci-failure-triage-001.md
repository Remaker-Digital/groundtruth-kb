NEW

# Implementation Proposal — GTKB-ISOLATION-017 Slice 8.6 (CI-Failure Triage + Remediation)

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-03 (S330)
Subject commit: `b4346ab690e937b80c5c99f776649f8bb8fa82b1` (Slice 8 release artifacts) on `develop` at `https://github.com/Remaker-Digital/agent-red-customer-engagement.git` — currently the head of develop.
Disposition authority: `DELIB-S330-RC1-CI-RED-PAUSE-AND-SLICE-8-6-DISPOSITION` (Path A: pause rc1; Slice 8.5 parked; this Slice 8.6 thread triages + fixes the pre-existing CI failures surfaced by Slice 8.5's CI probe).

## Summary

Slice 8.5's CI probe (Codex `-002` review + Prime's S330 follow-up via `gh run list --commit b4346ab690e937b80c5c99f776649f8bb8fa82b1`) revealed CI is RED on 2 of 4 triggered workflows for the Slice 8 commit:

- `Lint`: success
- **`Release Candidate Gate`: failure** (41 tests failed, 719 passed)
- `SonarCloud`: success
- **`Security Scan`: failure** (pip-audit found pip 26.0.1 itself has CVE-2026-3219, no fix version)

These 42 failures all **predate Slice 8** — none are Slice 8 regressions. Prior slices (1-7) committed without CI-green gates. Slice 8.5 was the first sub-thread to actually probe live CI. Per `DELIB-S330-RC1-CI-RED-PAUSE-AND-SLICE-8-6-DISPOSITION`, this Slice 8.6 thread triages + fixes the failures so v0.7.0-rc1 can ship against green CI.

**Scope is methodology + commit:** Slice 8.6 ships (a) a per-failure triage table classifying each failure as `fix-required` / `waivable-for-rc1` / `environmental`, (b) the actual fixes for `fix-required` items, (c) waiver DELIBs for `waivable-for-rc1` items, (d) environmental remediation (likely pin pip version in CI workflows). Implementation produces a fix commit (or commits) on `develop` that brings all 4 triggered workflows to green status.

After Slice 8.6 VERIFIED + commit lands, Slice 8.5 `-003` REVISED-1 is filed against the cumulative commit (Slice 8 + Slice 8.6) with the F1+F2+F3 fixes Codex `-002` already named.

## Specification Links

1. **`DELIB-S330-RC1-CI-RED-PAUSE-AND-SLICE-8-6-DISPOSITION`** — owner directive establishing this thread; defines the Phase 1-4 lifecycle.
2. **`DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE`** — parent split disposition; Slice 8.5 is the CI-capture thread; Slice 8.6 is a sibling sub-thread for fix work surfaced during 8.5 capture.
3. **`bridge/gtkb-isolation-017-slice-8-5-ci-green-002.md`** — Codex NO-GO that surfaced the live CI state.
4. **`bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-005.md` Risk 4** — anticipated this scenario: "If CI fails on `b4346ab6`, that surfaces as a Slice 8.6 sub-thread (or Slice 8 follow-up commit) — Slice 8.5 itself does NOT remediate failures, only captures the green outcome or surfaces the failure to owner."
5. **`memory/release-readiness.md:32`** — "GitHub Actions full sweep + release-candidate-gate.yml workflow green"; the gate this Slice 8.6 brings the commit into compliance with.
6. **`.claude/rules/file-bridge-protocol.md`** — Mandatory Specification Linkage Gate; Mandatory Specification-Derived Verification Gate.
7. **`.claude/rules/codex-review-gate.md`** — pre-implementation review gate.
8. **`.claude/rules/project-root-boundary.md`** — all active GT-KB files within `E:\GT-KB`.
9. **`.github/workflows/release-candidate-gate.yml`** + **`.github/workflows/security-scan.yml`** — the two failing workflow surfaces; the test files referenced in the failures live under `tests/scripts/`, `tests/security/`, `tests/multi_tenant/`, `tests/unit/`, `tests/hooks/`, `tests/integrations/`.
10. **Failure evidence:**
    - `gh run view 25290378334 --log-failed` → 41 RC Gate failures.
    - `gh run view 25290378337 --log-failed` → pip-audit pip CVE.
11. **Prior Deliberations:**
    - `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` — establishes v0.7.0-rc1 as release target.
    - `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE` — parent split disposition.
    - `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK` — pip-install adopter UX limitation acknowledgement.
    - `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER` — python-tests.yml waiver for Slice 8.5.
    - `DELIB-S330-RC1-CI-RED-PAUSE-AND-SLICE-8-6-DISPOSITION` — this thread's parent.

## Scope (Slice 8.6)

### Phase 1 — Triage (catalog + classify)

For each of 42 failures, produce a row in `memory/release-readiness.md` `ISOLATION-017-CLOSEOUT-CI-TRIAGE` block (new sub-section under the existing CLOSEOUT block):

| Failure | Test path | Category | Disposition | Rationale | Owner-decision needed? |
|---|---|---|---|---|---|

Classification rubric:

- **`fix-required`** — the test asserts a real invariant the project should satisfy. Examples (likely): missing MemBase governance records (the spec records SHOULD exist; their absence is the defect), `wrap_scan_hygiene_skip_dirs` (real scanner gap), `standing_backlog_harvest` (real harvest gap).
- **`waivable-for-rc1`** — the test asserts a contract that's reasonable to defer to v0.7.0 GA. Examples (likely): MEMORY.md size ceiling (cosmetic; no functional impact; current 90KB is from active session work), dashboard files (feature gap; v0.7.0 GA scope per `GTKB-DASHBOARD-002`).
- **`environmental`** — the test fails due to CI environment, not code. Examples (likely): `rehearse_isolation` M2 path validation (regex hardcodes Windows paths; Linux runner paths fail), pip CVE (no fix version available).

Owner-decision-needed flag is set when the disposition isn't obviously one category. Each owner decision becomes a sub-DELIB.

### Phase 2 — Implement fixes/waivers

For each `fix-required` row: implement the fix. Insert missing MemBase records as appropriate-typed specs; trim MEMORY.md (likely move large content to topic files); fix `wrap_scan_hygiene_skip_dirs` to include `scripts/` + `.claude/skills/`; fix `standing_backlog_harvest`'s `KeyError 'open'` and missing-entries logic.

For each `waivable-for-rc1` row: archive a waiver DELIB explaining why; if the test needs to skip in this rc, mark with `@pytest.mark.skip(reason="waived per DELIB-...")` OR document the failure in release-notes as a known rc1 limitation.

For each `environmental` row: address at the CI environment level (e.g., pin pip in workflow YAML to a CVE-free version; fix the M2 path regex to accept Linux paths). May require modifying `.github/workflows/*.yml` files.

### Phase 3 — Re-push + observe CI green

Commit fixes/waivers as one or more cohesive commits. Push to `develop`. Use `gh run list --branch develop --commit <new-cumulative-sha> --json conclusion,name,event,headSha,headBranch,workflowName` (full SHA per Codex `-002` F1) to observe CI runs. Required: every triggered workflow reaches `conclusion = success`.

### Phase 4 — Post-impl REPORT

File `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-002.md` (or next available version) NEW. Embed:

- The Phase 1 triage table (final form, all 42 rows resolved).
- For each `fix-required` row: the fix commit reference + line-level evidence.
- For each `waivable-for-rc1` row: the waiver DELIB ID + rationale.
- For each `environmental` row: the CI-side change (e.g., workflow YAML diff) + rationale.
- The `gh run list` output for the cumulative commit showing all triggered workflows green.
- A spec-to-test mapping derived from the linked specifications + per-failure resolutions.

Owner approves cumulative commit message. Codex VERIFIED required before tag authorization can proceed.

### Out-of-scope

- v0.7.0-rc1 tag creation (gated on Slice 8.5 VERIFIED, which is gated on Slice 8.6 VERIFIED + commit + Slice 8.5 -003 REVISED-1 + Codex GO + Slice 8.5 implementation + post-impl REPORT + Codex VERIFIED).
- PyPI publication (separate post-tag operator step).
- Modifying source in response to NEW CI failures discovered during Slice 8.6 implementation. Sub-failures discovered during fix work are tracked as Slice 8.6.x sub-threads or treated as part of the same fix.
- Coverage of `groundtruth-kb/tests/` in CI (deferred to v0.7.0 GA per the planned row 37 from `DELIB-S330-...-PYTHON-TESTS-WAIVER`).

## Implementation Plan

1. **Phase 1: Triage probe** (~1-2 sessions of work)
   - Run `gh run view 25290378334 --log-failed` and `gh run view 25290378337 --log-failed` to get the full failure list.
   - For each of 42 failures, investigate the test code + expected invariant + current state. Classify into the rubric.
   - Emit the triage table as a draft into `memory/release-readiness.md` `ISOLATION-017-CLOSEOUT-CI-TRIAGE` block.
   - For each `owner-decision-needed` row, surface via AskUserQuestion + archive a sub-DELIB.

2. **Phase 2: Implement fixes** (~3-5 sessions of work depending on triage outcomes)
   - For each `fix-required` row: probe → propose minimal fix → implement → re-run failing test locally to confirm green.
   - For each `waivable-for-rc1` row: archive waiver DELIB; mark test skipped if needed.
   - For each `environmental` row: modify CI workflow YAML or pin dependency version.
   - Each fix lands as a small commit with clear scope; fixes are not bundled to enable per-fix Codex review if needed.

3. **Phase 3: Re-push + observe CI** (~1 session)
   - Push the fix commit(s) to `develop`.
   - Poll CI until all triggered workflows reach terminal status.
   - Verify all are green; if any fail, sub-decision via AskUserQuestion (re-run, fix-fix, waive).

4. **Phase 4: Post-impl REPORT** (~1 session)
   - File the post-impl REPORT with full triage table, fix evidence, CI-green run inventory.
   - Codex VERIFIED required before unblocking Slice 8.5.

**Total estimated:** 6-9 sessions of work. Owner explicitly accepted this in selecting Path A.

## Test Plan

| Acceptance Criterion | Verification | Expected Result |
|---|---|---|
| Phase 1 triage table complete | `memory/release-readiness.md` `ISOLATION-017-CLOSEOUT-CI-TRIAGE` block contains 42 rows; every row has Category + Disposition fields filled | PASS — 42/42 rows classified |
| All `fix-required` rows have implemented fixes | Local re-run of the originally-failing tests passes | PASS for each row |
| All `waivable-for-rc1` rows have waiver DELIBs | KB query for waiver DELIB IDs returns rows with `outcome='owner_decision'` | PASS for each row |
| All `environmental` rows have CI-side remediation | Workflow YAML diff shows the change; CI re-run shows the failure resolved | PASS for each row |
| CI green on cumulative commit | `gh run list --branch develop --commit <cumulative-sha> --json conclusion --jq '.[].conclusion'` returns all `success` (no `failure`/`cancelled`/`timed_out`/`action_required`) | PASS — all triggered workflows green |
| Release Candidate Gate passes | inspect run inventory; `Release Candidate Gate` workflow has `conclusion = success` | PASS |
| Security Scan passes | inspect run inventory; `Security Scan` workflow has `conclusion = success` | PASS (assumes pip is upgraded or CVE waived) |

## Acceptance Criteria

This proposal is GO-able when Codex confirms:

1. Specification Links cover the disposition DELIB + the bridge thread's parent context + the CI failure evidence.
2. The triage rubric (`fix-required` / `waivable-for-rc1` / `environmental`) is well-defined; the methodology produces a categorized + actionable per-failure plan.
3. Phase 2 ships per-row fixes/waivers, not bundled changes; Codex retains review authority on substantive sub-fixes.
4. Phase 3's CI-green gate uses the full SHA per Codex `-002` F1 (no short-SHA queries).
5. Phase 4's post-impl REPORT will include the full triage table + per-row evidence + cumulative CI run inventory.
6. Out-of-scope items (tag, PyPI, GA-deferred work) remain explicitly excluded.

## Risk / Rollback

**Risk 1 — Triage produces > 5 owner-decision-needed rows** (significant decision-fatigue load). **Mitigation:** group by category; present batched AskUserQuestions where possible (multi-select for category-level decisions); surface only genuinely ambiguous cases.

**Risk 2 — `fix-required` items uncover deeper architectural gaps** (e.g., the missing MemBase governance records may signal that the GOV-* spec series was never fully promoted from "specified" to "implemented"). **Mitigation:** if a fix-required row reveals scope > 1 small commit, file as a Slice 8.6.x sub-thread (e.g., Slice 8.6.1 = MemBase governance record promotion).

**Risk 3 — Environmental fixes cascade** (pinning pip may break other CI jobs that depend on pip's current version). **Mitigation:** test environmental fixes incrementally; observe CI after each environmental change.

**Risk 4 — New CI failures surface during fix work** (regression introduced by Slice 8.6 itself). **Mitigation:** each fix commit re-runs the local-pytest equivalent before push; CI delta is observed per push.

**Risk 5 — pip CVE has no fix version** (Security Scan stays red even after pip upgrade attempt). **Mitigation:** if no upgrade path exists, explicitly waive the pip CVE per a sub-DELIB (acknowledge: pip itself has the CVE; no upgrade resolves; CI environment limitation; not a project dependency vulnerability).

**Rollback path:** if Slice 8.6 produces fixes that destabilize develop, revert the fix commit(s) via `git revert`. Slice 8 commit `b4346ab6` itself is unchanged by Slice 8.6 (only follow-on commits add to it). Slice 8.5 remains parked until a viable Slice 8.6 lands.

## Decision Needed From Owner

**None at proposal-filing time.** Sub-decisions (per-failure waiver-or-fix) surface during Phase 1 triage via AskUserQuestion as `owner-decision-needed` rows are encountered.

## Open Items

- The full failure list will be probed at Phase 1 implementation start (full `gh run view --log-failed` output not embedded in this proposal because the 42 failures span multiple test files; the proposal commits to producing the catalog as Phase 1's deliverable).
- The scope expansion vs original `DELIB-S330-DISPOSITION-CHOICE` (which framed Slice 8 as the closeout slice with Slice 8.5 as the only follow-on) is acknowledged via the new `DELIB-S330-RC1-CI-RED-PAUSE-AND-SLICE-8-6-DISPOSITION`.
- After Slice 8.6 VERIFIED + commit lands, Slice 8.5 `-003` REVISED-1 will need to update its referenced commit hash from `b4346ab6` to the cumulative Slice 8 + Slice 8.6 commit hash.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
