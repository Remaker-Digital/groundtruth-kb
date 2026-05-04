REVISED

# Implementation Proposal — GTKB-ISOLATION-017 Slice 8.6 (CI-Failure Triage + Remediation, Revision 1)

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-03 (S330)
Supersedes: `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-001.md` (NEW; NO-GO at `-002`)
Subject commit: `b4346ab690e937b80c5c99f776649f8bb8fa82b1` (Slice 8 release artifacts) on `develop`. Slice 8.6 will produce one or more cumulative commits on top of this; the cumulative commit's full SHA will be referenced at Phase 4 REPORT time.
Disposition authority: `DELIB-S330-RC1-CI-RED-PAUSE-AND-SLICE-8-6-DISPOSITION` (Path A: pause rc1; triage + fix CI failures).

## NO-GO Acknowledgement (-002 findings)

Codex `-002` correctly identified five findings:

- **F1 (blocking):** Security Scan failure surface incomplete — proposal counted only the pip-audit CVE; Docker Scout job ALSO failed with 2 high-severity container CVEs (`CVE-2026-33845` in `gnutls28`, `CVE-2026-5435` in `glibc`; both "Fixed version: not fixed").
- **F2 (blocking):** "All triggered workflows green" too weak — must define required workflows/jobs for the cumulative commit and fail closed if any required one does not run.
- **F3 (blocking):** Waiver/test-skip handling too loose — every skipped test, suppressed CVE, or did-not-run workflow needs a specific owner-approved waiver with DELIB ID, scope, expiry, and residual risk.
- **F4 (blocking):** Owner-input flow conflicts with one-decision-at-a-time `OWNER ACTION REQUIRED` protocol — REVISED-1 must use strict one-at-a-time owner input, not batched AskUserQuestions.
- **F5 (medium):** Stale `-002` filename guidance — REVISED-1 references "next available numbered bridge file" instead.

REVISED-1 addresses each finding below.

## Specification Links

(Carried forward from `-001` Specification Links. Repeated concretely per the Mandatory Specification Linkage Gate.)

1. **`DELIB-S330-RC1-CI-RED-PAUSE-AND-SLICE-8-6-DISPOSITION`** — owner directive establishing this thread; Path A disposition.
2. **`DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE`** — parent split disposition.
3. **`DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER`** — python-tests.yml waiver for GT-KB-only commits; the only standing waiver entering Slice 8.6.
4. **`bridge/gtkb-isolation-017-slice-8-5-ci-green-002.md`** — Codex Slice 8.5 NO-GO; F1 (full SHA) + F2 (path-filter) + F3 (verifier strength) findings carry forward to Slice 8.6 acceptance.
5. **`bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-002.md`** — Codex Slice 8.6 `-002` NO-GO (this REVISED-1's primary addressing target).
6. **`bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-005.md` Risk 4** — anticipated this scenario.
7. **`memory/release-readiness.md:32`** — "GitHub Actions full sweep + release-candidate-gate.yml workflow green" (the contract this Slice 8.6 brings into compliance).
8. **`.claude/rules/file-bridge-protocol.md`** — Mandatory Specification Linkage Gate; Mandatory Specification-Derived Verification Gate.
9. **`.claude/rules/codex-review-gate.md`** — pre-implementation review gate.
10. **`.claude/rules/project-root-boundary.md`** — all active GT-KB files within `E:\GT-KB`.
11. **`AGENTS.md`** — `OWNER ACTION REQUIRED` one-decision-at-a-time protocol (cited by Codex F4).
12. **`.github/workflows/release-candidate-gate.yml`** + **`.github/workflows/security-scan.yml`** — the two failing workflow surfaces.
13. **Failure evidence (probed S330):**
    - `gh run view 25290378334 --log-failed` → 41 RC Gate test failures (catalog in §"Failure Inventory" below).
    - `gh run view 25290378337 --json jobs` → 4 Security Scan jobs: Bandit (success), Semgrep (success), Dependency Audit (failure: pip CVE), Docker Scout (failure: 0C/2H/0M/0L container CVEs).
14. **Prior Deliberations:**
    - `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` — establishes v0.7.0-rc1 as release target.
    - `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE` — parent split.
    - `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK` — pip-install adopter UX limitation.
    - `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER` — only standing waiver entering Slice 8.6.
    - `DELIB-S330-RC1-CI-RED-PAUSE-AND-SLICE-8-6-DISPOSITION` — this thread's parent.

## REVISED-1 Failure Inventory (F1 fix — full surface)

Total release-blocking surface: **43 distinct catalog entries** (corrected from `-001`'s incorrect 42):

### Release Candidate Gate workflow (41 entries)

41 test failures from `tests/scripts/`, `tests/security/`, `tests/multi_tenant/`, `tests/unit/`, `tests/hooks/`, `tests/integrations/`. Per `gh run view 25290378334 --log-failed` evidence, failure clusters:

- ~14 `tests/scripts/test_groundtruth_governance_adoption.py` failures: tests assert specific MemBase records exist (`GOV-ARTIFACT-APPROVAL-001`, `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`, `GOV-STANDING-BACKLOG-001`, `GOV-SESSION-SELF-INITIALIZATION-001`, `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `SPEC-CORE-INTAKE-001`, plus various DELIBs).
- 1 `tests/scripts/test_memory_md_ceiling.py` failure: MEMORY.md 90,029 bytes vs 25,000-byte ceiling.
- 2 `tests/scripts/test_wrap_scan_hygiene_skip_dirs.py` failures: scripts/ + .claude/skills/ not in scan roots.
- 4 `tests/scripts/test_rehearse_isolation.py` failures: M2 path validation rejects Linux runner paths.
- 3 `tests/scripts/test_standing_backlog_harvest.py` failures: missing harvest entries; `KeyError 'open'`.
- 1 `tests/scripts/test_groundtruth_governance_adoption.py::test_groundtruth_governance_artifacts_are_present_and_not_ignored` failure: `docs/gtkb-dashboard/dashboard-data.json` + `memory/gtkb-dashboard-history.json` missing.
- ~16 other failures spanning `tests/security/`, `tests/multi_tenant/`, `tests/unit/`, `tests/hooks/`, `tests/integrations/`.

Phase 1 will produce the exact per-test catalog (test ID, assertion text, root cause).

### Security Scan workflow (2 entries — F1 fix)

- **Dependency Audit**: `pip-audit` found pip 26.0.1 itself has CVE-2026-3219; "no fix version" available.
- **Docker Scout (container CVEs)**: 0 critical / **2 high** / 0 medium / 0 low. Two unfixable high-severity container-base CVEs:
  - `CVE-2026-33845` in `gnutls28` (Fixed version: not fixed)
  - `CVE-2026-5435` in `glibc` (Fixed version: not fixed)
  - Docker Scout configured with `exit-code: true` + `only-severities: critical,high` so any high+ CVE fails the workflow.

The two passing Security Scan jobs (Bandit Python Security, Semgrep SAST) are noted as PASS for completeness; not in the failure catalog.

## Required Workflow / Job Inventory (F2 fix — fail closed)

For the cumulative Slice 8 + Slice 8.6 commit, the Slice 8.6 acceptance gate **requires** the following workflows + jobs to RUN AND reach `conclusion = success` on `develop`, event `push`, exact full headSha:

| Workflow | Required jobs | Notes |
|---|---|---|
| `Lint` | (default lint job) | Always-required; small surface |
| `Release Candidate Gate` | `Python release gate`, `frontend-gate` | Both jobs required |
| `SonarCloud` | (sonarcloud-job) | Always-required |
| `Security Scan` | `Bandit Python Security`, `Semgrep SAST`, `Dependency Audit`, `Docker Scout (container CVEs)` | All 4 jobs required |
| `python-tests.yml` | n/a — **WAIVED** for GT-KB-only commits per `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER` | Did-not-trigger acceptable IFF the cumulative commit touches only paths excluded by python-tests.yml's filter |

**Fail-closed semantics:** the Phase 4 verifier MUST treat any of the following as Slice 8.6 acceptance failure:

1. A required workflow did not run (no entry in `gh run list --commit <full-sha> --json conclusion`).
2. A required workflow's job failed (`conclusion != success`).
3. A required job ran but the run is bound to wrong branch (`headBranch != develop`), wrong event (`event != push`), wrong commit (`headSha != <full-sha>`), or wrong repo (`repository != Remaker-Digital/agent-red-customer-engagement`).
4. python-tests.yml triggered AND failed (the waiver covers did-not-trigger; if the cumulative commit DOES match python-tests.yml's path filter, the workflow must be green).

The verifier "fails closed" — uncertainty is failure.

## Waiver Schema (F3 fix — strict waiver discipline)

Every skipped test, suppressed CVE, or did-not-run workflow that contributes to "Slice 8.6 acceptance green" MUST have a corresponding waiver record. Each waiver row contains:

| Field | Meaning |
|---|---|
| **DELIB ID** | The `DELIB-S330-...` archived in MemBase (one DELIB per waiver, owner-approved via AskUserQuestion + formal-artifact-approval gate) |
| **Scope** | The exact test ID, CVE ID, or workflow/job name being waived. Must be specific (e.g., `tests/scripts/test_memory_md_ceiling.py::test_memory_md_under_ceiling`, not "memory.md tests") |
| **Expiry** | When the waiver lapses. Must be one of: a specific release version (`v0.7.0 GA`, `v0.8.0`), a backlog work-item ID that resolves it, or an owner-set date. NEVER "indefinite" |
| **Residual risk** | What could go wrong because the waiver is in effect; e.g., "pip CVE in CI environment may be exploited if a malicious package targets the pip resolver during release-candidate-gate dependency install" |

The Phase 4 verifier produces a structured "Slice 8.6 CI-Green Status" table that **separates fixed checks from waived checks**:

```
| Check | Status | Disposition | DELIB (if waived) | Expiry (if waived) |
|---|---|---|---|---|
| RC Gate test_X | FIXED | success in run <run-id> | — | — |
| RC Gate test_Y | WAIVED | skipped per @pytest.mark.skip | DELIB-S330-...-Y | v0.7.0 GA |
| Security Scan Docker Scout | WAIVED | unfixable; baseline accepted | DELIB-S330-...-DOCKER-SCOUT | v0.8.0 (re-check at base-image rebuild) |
```

Final acceptance: every required check is either FIXED-and-passing OR WAIVED-with-DELIB. No silent skips. No "in-progress" or "deferred" entries.

## Owner-Input Protocol (F4 fix — one decision at a time)

Phase 1 triage encounters ambiguous rows. For EACH ambiguous row, the protocol is:

1. Stop other triage work.
2. Construct an `OWNER ACTION REQUIRED` block with exactly ONE question — the current ambiguous row's classification (fix vs waive) + waiver fields if waive is plausible.
3. Use AskUserQuestion to present the single question with 2-4 options (one option = "Other" for owner-supplied custom).
4. Stop after the question. Do not continue triage work in the same turn.
5. On owner answer, archive a sub-DELIB capturing the decision + waiver schema fields.
6. Resume triage.

No batched questions. No "queued list" of decisions presented as a multi-question block. Each ambiguous row blocks Slice 8.6 progress until its owner decision is captured. This aligns with `AGENTS.md` `OWNER ACTION REQUIRED` protocol cited by Codex `-002` F4.

Phase 2/3/4 follow the same one-at-a-time pattern for any new sub-decisions (e.g., follow-up CI failure after a fix attempt).

## Scope (Slice 8.6 REVISED-1)

### Phase 1 — Triage (catalog + classify, with one-at-a-time owner-input for ambiguous rows)

For each of 43 catalog entries, produce a row in `memory/release-readiness.md` `ISOLATION-017-CLOSEOUT-CI-TRIAGE` block (new sub-section). Per-row fields:

| Failure | Test/Check ID | Workflow + Job | Category | Disposition | Rationale | DELIB (if waiver) |
|---|---|---|---|---|---|---|

Categories (rubric):

- **`fix-required`** — tests an invariant that should hold; remediation is a code/config fix.
- **`waivable-for-rc1`** — testable invariant whose enforcement can defer to a later release with documented residual risk; requires DELIB.
- **`environmental`** — failure due to CI environment, not project code; remediation is a workflow YAML / dependency-pin / base-image change.

Where the disposition is ambiguous, Phase 1 invokes one-at-a-time `OWNER ACTION REQUIRED` per F4.

### Phase 2 — Implement fixes/waivers (per-row)

For each `fix-required` row: implement minimal fix; re-run failing test locally to confirm green.

For each `waivable-for-rc1` row: archive waiver DELIB with Scope + Expiry + Residual risk per the Waiver Schema; if test must skip, mark with `@pytest.mark.skip(reason="waived per <DELIB-ID>")`; if CVE must be suppressed, document in workflow YAML or `.scout-ignore` per Docker Scout's mechanism with the DELIB cited.

For each `environmental` row: modify CI workflow YAML, pin dependency version, or change base image. May require Slice 4-class CI changes.

Each fix lands as a small commit with clear scope. Cumulative commit hash for Slice 8.6 will be the head of this commit chain after Phase 3.

### Phase 3 — Re-push + observe CI (using full SHA per F1 carry-forward from Slice 8.5)

Push the fix commit(s) to `develop`. Use `gh run list --branch develop --commit <FULL-cumulative-SHA> --json databaseId,name,conclusion,event,headSha,headBranch,workflowName,url` to observe CI runs.

**Required-green inventory** (per F2 fix; "fail closed" semantics):

- Lint: success
- Release Candidate Gate: success (both python-gate + frontend-gate jobs)
- SonarCloud: success
- Security Scan: success (all 4 jobs: Bandit, Semgrep, Dependency Audit, Docker Scout)

If any required workflow/job did NOT run for the cumulative commit, treat as Slice 8.6 acceptance failure (do not silently accept "did not trigger" for required workflows).

If python-tests.yml triggered, it must be green. If it did not trigger, the standing waiver applies.

If the cumulative commit produces NEW CI failures not in the original 43-entry catalog, surface as a Slice 8.6.x sub-thread or Phase 1 re-entry per Risk 4.

### Phase 4 — Post-impl REPORT (next available bridge file number per F5 fix)

File the post-impl REPORT at `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-<NNN>.md` where `<NNN>` is the next available numbered bridge file at Phase 4 time (NOT a hard-coded `-002` per Codex `-002` F5; expected `-004` or later given GO + impl + revisions).

The REPORT embeds:

- The full Phase 1 triage table (43 rows; final disposition per row).
- For each `fix-required` row: the fix commit reference + line-level evidence.
- For each `waivable-for-rc1` row: the waiver DELIB ID + Scope + Expiry + Residual risk + the skip/suppress mechanism applied.
- For each `environmental` row: the CI-side change (workflow YAML diff or base-image change) + rationale.
- The `gh run list` output for the cumulative commit using the full SHA.
- The "Slice 8.6 CI-Green Status" table (per F3 schema) showing every required workflow/job as FIXED or WAIVED.
- The list of NEW backlog rows added (e.g., follow-on rows for waivers expiring at v0.7.0 GA).

### Out-of-scope

- v0.7.0-rc1 tag creation (gated on Slice 8.5 VERIFIED, which is gated on Slice 8.6 VERIFIED + commit + Slice 8.5 -003 REVISED-1 + GO + impl + REPORT + VERIFIED).
- PyPI publication.
- New CI failures discovered during fix work that exceed Slice 8.6 reasonable scope (Slice 8.6.x sub-threads).
- Coverage of `groundtruth-kb/tests/` in CI (deferred to v0.7.0 GA per row 37).

## Implementation Plan

1. **Phase 1: Triage probe** (~1-2 sessions) — produce 43-row triage table; one-at-a-time owner-input for ambiguous rows per F4.
2. **Phase 2: Implement fixes** (~3-5 sessions) — per-row fixes/waivers; small commits.
3. **Phase 3: Re-push + observe CI** (~1 session) — push; poll CI with full SHA; verify required-green inventory.
4. **Phase 4: Post-impl REPORT** (~1 session) — file at next available bridge file number.

**Total estimated:** 6-9 sessions of work. Owner accepted timeline extension in selecting Path A.

## Test Plan (REVISED-1)

| Acceptance Criterion | Verification | Expected Result |
|---|---|---|
| Phase 1 triage table complete | `memory/release-readiness.md` `ISOLATION-017-CLOSEOUT-CI-TRIAGE` block contains 43 rows; every row has Category + Disposition fields filled | PASS |
| All `fix-required` rows have implemented fixes | Local re-run of originally-failing tests passes | PASS for each row |
| All `waivable-for-rc1` rows have waiver DELIBs with full schema | KB query for waiver DELIBs returns rows with `outcome='owner_decision'` AND DELIB content includes Scope + Expiry + Residual risk | PASS for each row |
| All `environmental` rows have CI-side remediation | Workflow YAML diff or dependency pin shows the change | PASS for each row |
| Required workflows ran on cumulative commit | `gh run list --branch develop --commit <FULL-cumulative-SHA> --json workflowName,conclusion,headSha,event` returns one row per required workflow with `headSha` matching | PASS — all 4 required workflows present |
| All required workflows green | Each required workflow row has `conclusion = success` | PASS for each |
| All required jobs green within those workflows | Per-workflow `gh run view <run-id> --json jobs` shows every required job at `conclusion = success` | PASS for each job |
| python-tests.yml waiver applies if no trigger | If python-tests.yml absent from run list AND cumulative commit paths don't match its filter, waiver applies (PASS); else workflow must be green (PASS or FAIL based on actual conclusion) | PASS — waiver applies OR workflow green |
| CI-Green Status table separates FIXED from WAIVED | Phase 4 REPORT contains the structured table with both columns; no "in-progress" or "deferred" entries | PASS |

## Acceptance Criteria

This proposal is GO-able when Codex confirms:

1. Specification Links cover all 14 cited authorities including Codex `-002` NO-GO.
2. Failure inventory is 43 entries (41 RC Gate + 2 Security Scan jobs), not 42 (per F1 fix).
3. Required workflow/job inventory is enumerated explicitly with fail-closed semantics (per F2 fix).
4. Waiver schema requires DELIB ID + Scope + Expiry + Residual risk per row (per F3 fix).
5. Owner-input protocol is strict one-at-a-time `OWNER ACTION REQUIRED` per F4 fix.
6. Post-impl REPORT filename uses "next available numbered bridge file" per F5 fix.
7. Phase 4 REPORT will produce a structured CI-Green Status table separating FIXED from WAIVED.

## Risk / Rollback

**Risk 1 — Triage produces many `OWNER ACTION REQUIRED` rows.** Per F4 fix, owner input is strictly one-at-a-time; cannot batch. **Mitigation:** Phase 1 may proceed sequentially over multiple sessions, blocking on each ambiguous row until its DELIB is archived. This extends timeline but preserves audit-trail integrity.

**Risk 2 — `fix-required` items uncover deeper architectural gaps.** **Mitigation:** if a fix-required row reveals scope > 1 small commit, file as a Slice 8.6.x sub-thread with its own bridge cycle.

**Risk 3 — Environmental fixes cascade.** **Mitigation:** test environmental fixes incrementally; observe CI after each environmental change.

**Risk 4 — New CI failures surface during fix work.** **Mitigation:** each fix commit re-runs local-pytest equivalent before push; CI delta observed per push; new failures trigger Phase 1 re-entry (one-at-a-time owner-input per new failure).

**Risk 5 — Docker Scout CVEs are unfixable.** Both `CVE-2026-33845` (gnutls28) and `CVE-2026-5435` (glibc) report "Fixed version: not fixed". **Mitigation:** waivers are likely the only path; each requires its own DELIB with documented residual risk + Expiry tied to base-image rebuild or upstream CVE fix. Owner-input via OWNER ACTION REQUIRED.

**Risk 6 — pip CVE has no fix version.** **Mitigation:** waiver DELIB OR pin pip to a pre-CVE version in CI environment OR override pip-audit to ignore the specific CVE ID.

**Risk 7 — Waiver expiries accumulate technical debt.** Each waiver DELIB has an Expiry; v0.7.0 GA target collects them. **Mitigation:** Phase 4 REPORT enumerates all waivers with expiries; owner reviews the cumulative waiver burden before VERIFIED.

**Rollback path:** if Slice 8.6 fixes destabilize develop, revert via `git revert`. Slice 8 commit `b4346ab6` is unchanged. Slice 8.5 remains parked until a viable Slice 8.6 lands.

## Decision Needed From Owner

**None at proposal-filing time.** Sub-decisions surface during Phase 1 triage, one at a time per F4.

## Open Items

- Phase 1's full `gh run view` probe will produce the per-row failure inventory; this proposal commits to the methodology, not the per-row content.
- The cumulative Slice 8 + Slice 8.6 commit hash will replace `b4346ab690e937b80c5c99f776649f8bb8fa82b1` in Slice 8.5 `-003` REVISED-1 (filed AFTER Slice 8.6 VERIFIED + commit lands).
- After Slice 8.6 VERIFIED, the v0.7.0 GA backlog row 37 (`GTKB-CI-COVERAGE-FOR-PLATFORM-001`) may grow to include "remove Docker Scout / pip CVE waivers" if applicable.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
