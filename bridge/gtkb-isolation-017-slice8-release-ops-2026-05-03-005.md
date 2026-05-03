REVISED

# Implementation Proposal — GTKB-ISOLATION-017 Slice 8 (Revision 2)

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-03 (S330)
Supersedes: `bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-003.md` (REVISED-1; NO-GO at `-004`)
Addresses: Codex `-004` findings F1 (B6 CI-green evidence violates bridge-VERIFIED-then-commit ordering) and F2 (acceptance gate permitted partial CI status).
Disposition authority: `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE` (formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-03-isolation-017-slice8-disposition.json`).

## NO-GO Acknowledgement

Codex `-004` correctly identified two blocking issues in REVISED-1:

- **F1 (lifecycle ordering):** B6 required pushing the Slice 8 implementation commit to develop BEFORE Codex could review the post-implementation report and record VERIFIED. This contradicts `CLAUDE.md:76` ("All post-implementation reports MUST be reviewed by Codex before committing") and `memory/work_list.md:4` ("propose via bridge → wait for Codex GO → implement → post-impl report → wait for Codex VERIFIED → commit"). Approving REVISED-1 would have created an unstated lifecycle exception.
- **F2 (partial CI acceptance):** REVISED-1's B6 scope permitted the post-impl report to cite the GitHub Actions run URL "with current status" (running/queued/skipped/cancelled/failing), with a follow-on capture commit updating it once CI completed. This permitted partial CI evidence to satisfy a release-hardening blocker that `memory/release-readiness.md:32` requires be green.

Codex `-004` offered three acceptable shapes for F1 resolution: (1) split implementation from CI-green capture into separate bridge threads; (2) owner-approved governed exception for pre-VERIFIED push; (3) draft PR / non-final branch CI path.

Per S330 owner directive (AskUserQuestion header "Slice 8 path"; answer: "Split: Slice 8 + Slice 8.5 (Recommended)"; archived at `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE`), **REVISED-2 implements the split**: Slice 8 ships release artifacts without CI evidence and reaches VERIFIED + commit; **B6 (CI-green evidence) is deferred to a separate Slice 8.5 bridge thread** filed after Slice 8 commit lands. Slice 8.5 gates `v0.7.0-rc1` tag authorization. F2 dissolves because Slice 8 no longer carries CI evidence at all; Slice 8.5's gate will require final green status (no partial CI acceptance) because it is filed AFTER the Slice 8 commit exists for CI to run against.

## Specification Links

Specification Links from `-003` carry forward unchanged. New citation added per F1+F2 fix:

1. **Phase 9 plan §"Deliverables From The Implementation Bridge"** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 415-430.
2. **Phase 9 plan §"Open Decisions"** at the same plan lines 369-396 — Decisions 2/4/5 resolved per S329 owner directives.
3. **Phase 9 plan §"Required Coverage"** at the same plan lines 89-303.
4. **ADR-ISOLATION-APPLICATION-PLACEMENT-001**.
5. **`.claude/rules/project-root-boundary.md`**, **`.claude/rules/file-bridge-protocol.md`**, **`.claude/rules/codex-review-gate.md`**.
6. **Scoping carry-forward** at `bridge/gtkb-isolation-017-scoping-003.md` lines 186-202 + `-004` GO.
7. **GOV-09**, **GOV-19**, **GOV-20**, **GOV-ARTIFACT-APPROVAL-001**.
8. **Prior Slice GOs:** Slice 1 `-012`, Slice 2 `-008`, Slice 2.5 `-008`, Slice 3 `-014`, Slice 4 `-012`, Slice 5 `-006`, Slice 6 `-004`, Slice 7 `-004` — all VERIFIED.
9. **Release-readiness blockers source:**
    - `memory/release-readiness.md:23-33` — "Release-Hardening Blockers (address during Slice 8 closeout)".
    - `memory/work_list.md` row 5 (Slice 8) — split disposition recorded.
10. **Existing surfaces modified by Slice 8 (B6 surface deferred to Slice 8.5):**
    - `groundtruth-kb/src/groundtruth_kb/__init__.py` — version bump (B1).
    - `groundtruth-kb/pyproject.toml` — version bump (B1).
    - `groundtruth-kb/CHANGELOG.md` — release-notes entry.
    - `groundtruth-kb/release-notes-0.7.0-rc1.md` (new) — separate per release-readiness:29 (B4).
    - `groundtruth-kb/docs/announcements/v0.7.0-rc1.md` (new).
    - `memory/release-readiness.md` — `ISOLATION-017-CLOSEOUT` block (B7); B6 row carries explicit "deferred to Slice 8.5 — see `bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md`" status.
    - Source files / test files / config files modified as part of full-repo ruff resolution + pytest feasibility (touched files determined by actual ruff/pytest output during implementation; B2/B3).
11. **Prior Deliberations:**
    - `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` — establishes v0.7.0-rc1 as release target.
    - S329 owner directives resolving Decisions 2/4/5 + the all-blockers-in-scope authorization.
    - `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE` v1 — Slice 5.5 deferral cited in announcement.
    - **`DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE` (NEW; this REVISED-2's supersession authority)** — split into Slice 8 + Slice 8.5 per Codex F1 path 1.

## Scope (REVISED-2)

### In-scope — release artifacts + closeout (no CI evidence)

The B-number cross-references with `-003` are preserved. **B6 (CI-green evidence) is explicitly out-of-scope for Slice 8 and deferred to Slice 8.5** — see "Deferred to Slice 8.5" below.

- **B1 — Version bump.** `groundtruth-kb/src/groundtruth_kb/__init__.py` line 16 `__version__ = "0.6.1"` → `__version__ = "0.7.0rc1"` (PEP 440 normalized form; tag is `v0.7.0-rc1`). `groundtruth-kb/pyproject.toml` `version` field synchronized.
- **B2 — Full-repo ruff resolution.** Probe `ruff check .` from repo root + `ruff format --check .` ; fix what's fixable in scope; for issues outside Slice 8 reasonable scope (e.g., issues in unrelated subsystems), surface explicitly with a deferral plan or scope-down request.
- **B3 — Full pytest feasibility.** Run `python -m pytest groundtruth-kb/tests/` to completion; document the runtime; identify any genuine timeouts vs slow-but-completing lanes. Document in `release-notes-0.7.0-rc1.md` and `release-readiness.md`. (Slice 5 cross-test run completed in 586s — full-suite completion is achievable; "timeout" in S327 status may have been a tighter local limit.)
- **B4 — `release-notes-0.7.0-rc1.md` separate file.** New file at `groundtruth-kb/release-notes-0.7.0-rc1.md` mirroring the format of `release-notes-0.6.1.md`. Contains release notes prose + summary of B1/B2/B3/B4/B5/B7 outcomes + explicit "Slice 8.5 follow-on captures CI-green evidence and gates v0.7.0-rc1 tag authorization" cross-reference. ~150 LOC.
- **B5 — Wheel/sdist + install smoke.** Run `python -m build` (wheel + sdist) from `groundtruth-kb/`. Install built wheel into a tmp env; run `gt --version` (must show 0.7.0rc1) + `gt project init <tmp>/test-app --profile local-only` (must succeed); document the smoke result.
- **B7 — Bridge terminal state documentation.** All 7 ISOLATION-017 slice bridges are VERIFIED; release-readiness `ISOLATION-017-CLOSEOUT` block names each bridge ID. Standing-Backlog/Primer/Disambiguation deferred-status documented per S327 directive (already in release-readiness:33; this slice cites + retains that wording). The CLOSEOUT block also records B6 as "deferred to Slice 8.5 — see `bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md`".

**Closeout artifacts (carry forward from `-003`):**

- `groundtruth-kb/CHANGELOG.md` — `[0.7.0-rc1] - 2026-05-03` entry under `[Unreleased]`, ~80 LOC. Entry cross-references the Slice 8.5 follow-on.
- `groundtruth-kb/docs/announcements/v0.7.0-rc1.md` (new) — standalone announcement, ~150 LOC. Announcement notes Slice 8.5 as the gating step before tag.
- `memory/release-readiness.md` — `ISOLATION-017-CLOSEOUT` block + B1/B2/B3/B4/B5/B7 outcome table + explicit B6 "deferred to Slice 8.5" row, ~50 LOC change.
- `scripts/_verify_slice8_closeout.py` (new) — composite gate verifier covering B1/B2/B3/B4/B5/B7 outcomes (B6 explicitly skipped with "deferred to Slice 8.5" message), ~150 LOC.
- `IPR-SLICE8-RELEASE-OPS-001` + `CVR-SLICE8-RELEASE-OPS-001` + umbrella IPR/CVR for the program — embedded in post-impl REPORT.

**Total estimated:** 4-6 modified files (version bump + CHANGELOG + release-readiness + ruff fixes) + 4 new files (release-notes-0.7.0-rc1.md + announcement + verification script + bridge proposal) + ~700 LOC across all artifacts.

### Deferred to Slice 8.5 (explicit, owner-approved per DELIB-S330)

**B6 — GitHub Actions CI-green evidence.** Filed AFTER Slice 8 reaches VERIFIED + commit lands as a new bridge thread `bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md`. Slice 8.5 captures the GitHub Actions run URL on the Slice 8 commit, names the workflows that ran, and asserts final green status (no partial-CI acceptance). Slice 8.5 gates `v0.7.0-rc1` tag authorization. Slice 8.5 may also amend `memory/release-readiness.md` to make the B6 → Slice 8.5 mapping explicit at the release-readiness contract level.

### Version tag (separate operator step, NOT in this commit)

Per `-003`'s constraint, carried forward unchanged. The `git tag -a v0.7.0-rc1` operation does not authorize until BOTH Slice 8 and Slice 8.5 are VERIFIED.

### Out-of-scope (carried forward from `-003`)

- GA tagging (v0.7.0); Slice 5.5 (overlay refresh + disposability); PyPI publication; modifying Slices 1-7 surfaces; customer email / blog post.

## Implementation Plan (REVISED-2)

Sequenced for incremental verification. Step 12 (B6 push) from `-003` is removed; Slice 8.5 will own it.

1. **Probe baseline state** — run `ruff check .` + `python -m pytest groundtruth-kb/tests/ -q` from repo root + `groundtruth-kb/` respectively; capture current state. (~5 min)

2. **B1 version bump** — modify `__init__.py` + `pyproject.toml`; verify with `python -c "import groundtruth_kb; print(groundtruth_kb.__version__)"`. (~5 min)

3. **B4 `release-notes-0.7.0-rc1.md`** — author. Includes explicit "Slice 8.5 follow-on captures CI-green evidence and gates v0.7.0-rc1 tag authorization" cross-reference. (~20 min)

4. **CHANGELOG entry** — add `## [0.7.0-rc1] - 2026-05-03` block; cross-reference release-notes file + Slice 8.5 follow-on. (~10 min)

5. **Standalone announcement** — author at `docs/announcements/v0.7.0-rc1.md`. Notes Slice 8.5 as gating step. (~30 min)

6. **B2 ruff resolution** — fix the issues from baseline probe; if scope balloons, surface explicitly. (~30-60 min depending on probe outcome)

7. **B5 wheel/sdist build smoke** — `python -m build`; install in tmp env; smoke `gt --version` + `gt project init`. (~30-60 min)

8. **B3 pytest feasibility documentation** — record full-sweep runtime + lane breakdown in release-notes-0.7.0-rc1.md. (~15 min after baseline run completes)

9. **B7 release-readiness `ISOLATION-017-CLOSEOUT` block** — append to `memory/release-readiness.md`; includes B6 "deferred to Slice 8.5" row. (~15 min)

10. **`scripts/_verify_slice8_closeout.py`** — composite gate verifier covering B1/B2/B3/B4/B5/B7 (B6 emits explicit "deferred to Slice 8.5 — see `bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md`" message and skips). (~30 min)

11. **Run composite gate verifier** — confirm B1/B2/B3/B4/B5/B7 all PASS; B6 reports "deferred to Slice 8.5" (intentional). (~5 min)

12. **Author IPR + CVR + umbrella IPR + umbrella CVR** — embedded in post-impl REPORT. Cite `DELIB-S330` as Slice 8 disposition authority + cite the planned Slice 8.5 thread as B6 follow-on. (~30 min)

13. **File post-impl REPORT** as `bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-006.md` (or next available version) with NEW status. After Codex VERIFIED + commit, file `bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md` to capture B6 evidence.

## Test Plan (spec-to-test mapping per F1+F2 fixes)

| Blocker | Verification (Slice 8) |
|---|---|
| B1 version bump | `python -c "import groundtruth_kb; print(groundtruth_kb.__version__)"` outputs `0.7.0rc1`; `pyproject.toml` `version` field equals `0.7.0rc1` |
| B2 full-repo ruff | `ruff check .` from repo root exits 0 (or surfaces an in-scope deferral with explicit exclusions) |
| B3 full pytest feasibility | `python -m pytest groundtruth-kb/tests/ -q` runs to completion (no infinite loop / hang); runtime + per-lane breakdown documented in release-notes-0.7.0-rc1.md |
| B4 release-notes-0.7.0-rc1.md | File exists at `groundtruth-kb/release-notes-0.7.0-rc1.md`; structure mirrors `release-notes-0.6.1.md`; cites all 7 ISOLATION-017 slices + Slice 8.5 cross-reference |
| B5 wheel/sdist install smoke | `python -m build` succeeds; `pip install dist/*.whl` in tmp env succeeds; `gt --version` reports 0.7.0rc1; `gt project init <tmp>/test-app --profile local-only` succeeds |
| ~~B6 CI green evidence~~ | **Out-of-scope for Slice 8 per DELIB-S330; deferred to Slice 8.5.** Slice 8 verification asserts B6 is documented as deferred (see B7 below). |
| B7 bridge terminal state | release-readiness `ISOLATION-017-CLOSEOUT` block names all 7 VERIFIED bridge IDs (Slices 1, 2, 2.5, 3, 4, 5, 6, 7) + cites the standing-Backlog/Primer/Disambiguation deferred status + records B6 as "deferred to Slice 8.5 — see `bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md`" |
| Decision 2 (v0.7.0-rc1) | B1 + CHANGELOG + announcement + release-readiness all cite v0.7.0-rc1; tag authorization explicitly conditional on Slice 8.5 |
| Decision 4 (4 publicity surfaces, together) | CHANGELOG + announcement + release-notes-0.7.0-rc1.md + cross-references to docs chapter + cross-references to examples |
| Decision 5 (composite acceptance gate) | `scripts/_verify_slice8_closeout.py` runs B1/B2/B3/B4/B5/B7 + the original 3 checks; all PASS; B6 reports deferred |
| DELIB-S330 disposition fidelity | Slice 8 scope contains no push/CI-trigger step; `_verify_slice8_closeout.py` does NOT execute or attempt to verify CI; release-notes + announcement + CLOSEOUT all explicitly cite Slice 8.5 as the B6 follow-on |

Verification commands:

```bash
# From E:\GT-KB
python scripts/_verify_slice8_closeout.py

# From E:\GT-KB\groundtruth-kb (per the verification script's invocation)
python -c "import groundtruth_kb; assert groundtruth_kb.__version__ == '0.7.0rc1'"
ruff check .
python -m pytest tests/ -q --tb=short
python -m build
```

## Acceptance Criteria (REVISED-2)

This REVISED-2 is GO-able when Codex confirms:

1. Specification Links cover all governing artifacts including `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE` as the supersession authority for the split.
2. **B6 (CI-green evidence) is explicitly out-of-scope** with the deferral target named (`bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md`).
3. The 6 in-scope blockers (B1, B2, B3, B4, B5, B7) cover all release-hardening work that does NOT require post-commit CI evidence.
4. The 4 closeout artifacts (CHANGELOG, announcement, release-readiness field, verification script) all explicitly cite the Slice 8.5 follow-on.
5. The verification script `_verify_slice8_closeout.py` covers B1/B2/B3/B4/B5/B7 + the original 3 checks; B6 is intentionally reported as deferred (does NOT block PASS).
6. The release-readiness `ISOLATION-017-CLOSEOUT` block records B6 as "deferred to Slice 8.5" with the bridge thread name cited.
7. No step in the implementation plan pushes a commit, triggers CI, or otherwise mutates remote repository state.
8. The post-impl REPORT plan includes filing `bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md` AFTER Slice 8 commit lands as the B6 follow-on.
9. Estimated envelope ~700 LOC across all artifacts; substantial implementation work expected.
10. Owner-approved disposition cited (S330 AskUserQuestion answer "Split: Slice 8 + Slice 8.5 (Recommended)" archived as `DELIB-S330`).

## Risk / Rollback (REVISED-2)

`-003` Risk 4 (CI takes longer than session) is removed by the split — Slice 8 no longer waits on CI.

**Risk 1 — Ruff resolution scope balloons.** If `ruff check .` baseline reveals hundreds of issues across unrelated subsystems, fixing them all in Slice 8 creates massive scope creep. **Mitigation:** baseline probe in step 1 surfaces the count + scope; if >100 issues outside Slice 8 reasonable scope (e.g., in deeply unrelated areas like Agent Red product code), surface as a sub-decision via AskUserQuestion before continuing.

**Risk 2 — Pytest full-sweep timeout reproduction.** If the full pytest hangs or fails in ways that block CI feasibility, the rc release blocks at Slice 8.5 even if Slice 8 itself ships clean. **Mitigation:** baseline probe documents the actual current state; if hanging behavior reproduces, file a sub-bridge to scope/parallelize before continuing Slice 8 (since Slice 8.5 will need the test suite to run cleanly in CI).

**Risk 3 — Wheel build smoke environment drift.** Building + installing in a tmp env may surface `pip install` issues unrelated to Slice 8. **Mitigation:** smoke captures the failure mode; if it's a packaging defect rather than a Slice 8 defect, file a sub-bridge.

**Risk 4 — Slice 8.5 surfaces a CI failure that requires changing Slice 8 surfaces.** If GHA finds a defect in code shipped in the Slice 8 commit (e.g., test that passes locally but fails in CI), Slice 8.5 cannot achieve final green without a Slice 8 follow-up. **Mitigation:** Slice 8.5 may file a remediation bridge as a follow-on; if the remediation is small (test fix, config tweak), it lands as a normal Slice 8 follow-up commit before Slice 8.5 can record VERIFIED. The split does not eliminate this risk but does name it cleanly.

**Rollback path:** Slice 8 ships docs + a verification script + 1 release-readiness field + 1 CHANGELOG entry + 1 release-notes file + 1 announcement + version bumps + ruff fixes. Reversible via `git revert` of the implementation commit; no production impact possible (pre-tag, pre-publish; Slice 8.5 has not yet authorized the tag).

## Decision Needed From Owner

**None at REVISED-2 time.** The disposition decision was resolved at S330 via AskUserQuestion answer cited in §"NO-GO Acknowledgement" and archived as `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE`. Sub-decisions (e.g., ruff scope balloon, pytest timeout) will be surfaced via AskUserQuestion at probe time only if they materially change scope.

## Open Items

- The `python -m groundtruth_kb.cli deliberations search --query "ISOLATION-017 release closeout"` probe will run as part of Codex review's Prior Deliberations check; should now surface `DELIB-S330` (inserted S330).
- The version tag (`git tag -a v0.7.0-rc1`) remains a separate post-VERIFIED operator step **and is gated on Slice 8.5 VERIFIED**, not just Slice 8 VERIFIED.
- Slice 8.5 (`bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md`) will be filed AFTER Slice 8 commit lands; not yet drafted.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
