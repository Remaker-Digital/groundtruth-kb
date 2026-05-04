NEW

# Implementation Proposal — GTKB-ISOLATION-017 Slice 8.5 (CI-Green Capture)

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-03 (S330)
Subject commit: `b4346ab6` (gtkb-isolation-017: Slice 8 release artifacts VERIFIED (REVISED-2)) on `develop` at `https://github.com/Remaker-Digital/agent-red-customer-engagement.git`
Disposition authority: `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE` — "Split into Slice 8 + Slice 8.5; Slice 8.5 captures CI-green evidence on the Slice 8 commit; gates `v0.7.0-rc1` tag authorization."

## Summary

Slice 8 reached VERIFIED at `bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-012.md` and was committed + pushed at `b4346ab6` (S330, 2026-05-03). Per the disposition DELIB, this Slice 8.5 thread captures GitHub Actions CI-green evidence on that commit before `v0.7.0-rc1` tag is authorized.

**Scope is intentionally narrow:** observe CI runs triggered by the push of `b4346ab6` to `develop`; assert all release-relevant workflows reach final green status; record the run URLs as durable evidence; update `memory/release-readiness.md` `ISOLATION-017-CLOSEOUT` block's B6 row from "DEFERRED to Slice 8.5" to "GREEN @ <run-url>".

This thread does NOT modify any source. It is observational + evidence-recording only.

## Specification Links

1. **`DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE`** — establishes Slice 8.5 as the dedicated CI-green capture thread; explicitly bounds Slice 8.5 to "captures GitHub Actions run URL on Slice 8 commit + asserts final green status (no partial-CI acceptance); gates `v0.7.0-rc1` tag authorization."
2. **`memory/release-readiness.md:32`** — "GitHub Actions full sweep + release-candidate-gate.yml workflow green" required during the release-readiness CLOSEOUT.
3. **`memory/release-readiness.md` §"ISOLATION-017-CLOSEOUT" B6 row** — currently records B6 as "DEFERRED to Slice 8.5"; this Slice 8.5 thread updates that row with concrete CI-run-URL evidence at acceptance time.
4. **`memory/release-readiness.md` §"Tag authorization gate"** — `git tag -a v0.7.0-rc1` does not authorize until BOTH Slice 8 AND Slice 8.5 are VERIFIED.
5. **`.claude/rules/file-bridge-protocol.md`** — Mandatory Specification Linkage Gate; Mandatory Specification-Derived Verification Gate.
6. **`.claude/rules/codex-review-gate.md`** — pre-implementation review gate.
7. **`.claude/rules/project-root-boundary.md`** — all active GT-KB files within `E:\GT-KB`.
8. **Slice 8 commit `b4346ab6`** at `bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-012.md` VERIFIED — the commit CI must run against.
9. **Prior Deliberations:**
    - `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` — establishes v0.7.0-rc1 as release target.
    - `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE` — split disposition (parent of this thread).
    - `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK` — acknowledged rc1 install-UX limitation; Slice 8.5 does not address this (deferred to v0.7.0 GA per row 36).
10. **Project-relevant CI workflows** (`.github/workflows/`):
    - `lint.yml` — repository-wide lint sweep.
    - `python-tests.yml` — pytest sweep.
    - `release-candidate-gate.yml` — release-candidate gate (release-readiness:32 named).
    - `security-scan.yml` — security scan.
    - `sonarcloud.yml` — SonarCloud quality gate.
    - `accessibility.yml`, `build-agent-containers.yml`, `build-api-gateway.yml`, `build-slim-gateway.yml`, `build-test-host.yml`, `chromatic.yml`, `deploy-docs.yml`, `docs-quality.yml`, `visual-regression.yml` — additional product/build/docs workflows that may or may not trigger on this commit (Agent Red product code paths may not be touched).

## Scope (Slice 8.5)

### In-scope

- **CI run discovery:** identify every GitHub Actions workflow run triggered by push of `b4346ab6` to `develop`. Use `gh run list --branch develop --commit b4346ab6 --json databaseId,name,status,conclusion,url`.
- **Status assertion:** every workflow that ran must reach `conclusion = success`. No `failure`, `cancelled`, `timed_out`, or `action_required`.
- **Skip semantics:** workflows that did NOT trigger on this commit (e.g., path-filtered workflows that only run when specific paths change) are recorded as "did not trigger" and are not failures. The Slice 8.5 acceptance gate distinguishes "ran + green" from "did not run" from "ran + not-green"; only the third is a failure.
- **Evidence capture:** record run URLs in `memory/release-readiness.md` `ISOLATION-017-CLOSEOUT` B6 row, replacing "DEFERRED to Slice 8.5" with a tabular summary (workflow name, run ID, conclusion, URL).
- **Verifier extension:** add a `check_b6_ci_green` function to `scripts/_verify_slice8_closeout.py` (or a sibling script) that asserts B6 is documented as GREEN with run URLs. The existing `check_b6_deferred_to_slice_8_5` is replaced/superseded; the composite gate's B6 row reports PASS instead of DEFERRED.

### Out-of-scope

- Modifying source code in response to CI failures. If CI fails on `b4346ab6`, that surfaces as a Slice 8.6 sub-thread (or Slice 8 follow-up commit) — Slice 8.5 itself does NOT remediate failures, only captures the green outcome or surfaces the failure to owner.
- Triggering re-runs of failed workflows. If a workflow fails for transient reasons (infra issue), owner decides whether to re-run or accept.
- v0.7.0-rc1 tag creation. Tag is owner-authorized post-Slice-8.5-VERIFIED; Slice 8.5 only signals readiness.
- PyPI publication. Separate post-tag operator step.

## Implementation Plan

1. **Wait for CI completion.** Push of `b4346ab6` triggered CI ~12:5x UTC; typical full-sweep runtime is 10-30 min depending on workflow. Poll `gh run list --commit b4346ab6 --json status,conclusion` until all in-flight runs reach a terminal `conclusion`.

2. **Capture run inventory.** For each workflow that ran on `b4346ab6`, record: workflow name, run ID, conclusion, URL. Output as a markdown table.

3. **Assert acceptance.** Every triggered workflow must have `conclusion = success`. Any other terminal conclusion is a Slice 8.5 acceptance failure.

4. **Update release-readiness B6 row.** Replace the "DEFERRED to Slice 8.5" rationale string with the captured run table. Cite the Slice 8.5 bridge thread for traceability.

5. **Extend `_verify_slice8_closeout.py`** (or write a sibling `_verify_slice8_5_ci_green.py`): add a `check_b6_ci_green` function that greps `release-readiness.md` for the captured run table + asserts each row is green. Composite gate output then reports `[PASS]   B6   CI-green evidence captured` instead of `[DEFER]`.

6. **Run extended composite gate** to confirm B6 transitions from DEFER → PASS. Capture the verbatim output.

7. **File post-implementation report** as `bridge/gtkb-isolation-017-slice-8-5-ci-green-002.md` (or next available version) with NEW status. Embed the run table + verifier output + composite gate output.

8. **Codex VERIFIED** on the post-impl REPORT.

9. **Owner authorizes** `git tag -a v0.7.0-rc1 b4346ab6 -m "..."` (NOT in this Slice 8.5 scope; scheduled post-VERIFIED).

## Test Plan

| Acceptance Criterion | Verification | Expected Result |
|---|---|---|
| All triggered workflows green | `gh run list --branch develop --commit b4346ab6 --json conclusion --jq '.[].conclusion'` | every line is `success` (no `failure`/`cancelled`/`timed_out`/`action_required`) |
| `release-candidate-gate.yml` triggered + green | inspect run inventory; `release-candidate-gate` workflow has `conclusion = success` | PASS — release-readiness.md:32 satisfied |
| `python-tests.yml` triggered + green | inspect run inventory | PASS — pytest sweep on commit was clean |
| `lint.yml` triggered + green | inspect run inventory | PASS — repo-wide lint clean |
| Run-URL evidence captured in `release-readiness.md` | grep B6 row for `https://github.com/.../actions/runs/` | URLs present + conclusion noted per workflow |
| `_verify_slice8_closeout.py` (extended) reports B6 PASS | composite gate output: `[PASS]   B6` (was `[DEFER]`) | exit 0; 9 PASS, 0 DEFERRED, 0 FAIL |

## Acceptance Criteria

This proposal is GO-able when Codex confirms:

1. Specification Links cover all governing artifacts (the disposition DELIB, release-readiness B6 row, the Slice 8 commit, and the bridge protocol gates).
2. Scope is bounded to evidence capture + B6 row update + verifier extension; no source modification, no remediation logic.
3. The acceptance test asserts FINAL green status on every triggered workflow (no partial-CI acceptance).
4. The "did not trigger" semantics are correctly distinguished from failures.
5. Post-impl REPORT will embed the run table + verifier output + composite gate output.

## Risk / Rollback

**Risk 1 — CI fails on `b4346ab6`.** A test that passed locally fails in CI (environment delta). **Mitigation:** Slice 8.5 surfaces the failure to owner via AskUserQuestion; resolution is either a Slice 8 follow-up commit (file as Slice 8.6) or owner waiver; v0.7.0-rc1 tag remains gated until resolution.

**Risk 2 — Release-candidate-gate.yml doesn't trigger** (e.g., path-filtered to skip when only `groundtruth-kb/` changes). **Mitigation:** if release-candidate-gate is path-filtered out, Slice 8.5 surfaces this as a sub-decision: either (a) accept the gate skipping for this rc (rc1 is a `groundtruth-kb/`-only release), or (b) push an empty trigger commit, or (c) modify the workflow to always run on `develop` pushes. Owner decides at probe time.

**Risk 3 — CI takes longer than session.** GHA full sweep may exceed session window. **Mitigation:** Slice 8.5 implementation step 1 explicitly polls; Codex review at post-impl REPORT time validates final state. The bridge thread can pause between push and post-impl REPORT.

**Risk 4 — Transient CI failure (infra).** A workflow fails due to network/runner issue, not code defect. **Mitigation:** owner decides whether to re-run via `gh run rerun <run-id>` or surface as Slice 8.6 if the failure is reproducible.

**Rollback path:** Slice 8.5 ships only documentation updates (B6 row text) + a verifier extension. No code change to revert. If Slice 8.5 surfaces a real CI failure, the rollback is owner choice between (a) revert `b4346ab6` (substantial), (b) file Slice 8.6 with a fix-commit (recommended), or (c) waiver.

## Decision Needed From Owner

**None at proposal-filing time.** Sub-decisions surface at probe time per Risk 2/4.

## Open Items

- Initial `gh run list --commit b4346ab6` query will execute as part of Codex's review (Codex routinely checks the named commit's CI state) OR at Prime's implementation step 1.
- The verifier extension is a small (~30-50 LOC) addition to `_verify_slice8_closeout.py`; alternatively it can live as a sibling `scripts/_verify_slice8_5_ci_green.py` if the owner prefers separation.
- Post-impl REPORT will be filed as the next bridge version after CI completes + B6 row update lands.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
