REVISED

# Implementation Proposal — GTKB-ISOLATION-017 Slice 8 (Revision 1)

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-03 (S329)
Supersedes: `bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-001.md` (NEW; NO-GO at `-002`)
Addresses: Codex `-002` findings F1 (omitted release-hardening blockers), F2 (release version not implemented), F3 (CI green replaced by local subset).

## NO-GO Acknowledgement

Codex `-002` correctly identified that `-001` narrowed Slice 8 to docs + 2 pytest checks while `memory/release-readiness.md:23-33` (the "Release-Hardening Blockers (address during Slice 8 closeout)" block) and `memory/work_list.md:21-27` assigned 7 release-hardening blockers to Slice 8 scope:

1. Full-repo `ruff check .` resolution (currently red on full repo per S327 status).
2. `pytest` full-sweep feasibility (currently times out per S327 status; needs scope/parallelize for CI feasibility).
3. Package version bump from `0.6.1` to `0.7.0-rc1` in `groundtruth-kb/src/groundtruth_kb/__init__.py` + `groundtruth-kb/pyproject.toml`.
4. `release-notes-0.7.0-rc1.md` (separate from CHANGELOG).
5. Wheel/sdist build + install smoke (`pip install` produces working `gt project init`).
6. GitHub Actions CI green evidence (full sweep + release-candidate-gate.yml).
7. Bridge terminal state documentation.

Per S329 owner directive (AskUserQuestion answer: "All blockers in scope (rigorous, ~3-5 hours session work)"), **REVISED-1 brings all 7 blockers into Slice 8 implementation scope**. No scope revision sought.

## Specification Links

All Specification Links from `-001` carry forward unchanged.

1. **Phase 9 plan §"Deliverables From The Implementation Bridge"** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 415-430.
2. **Phase 9 plan §"Open Decisions"** at the same plan lines 369-396 — Decisions 2/4/5 resolved per S329 owner directives.
3. **Phase 9 plan §"Required Coverage"** at the same plan lines 89-303.
4. **ADR-ISOLATION-APPLICATION-PLACEMENT-001**.
5. **`.claude/rules/project-root-boundary.md`**, **`.claude/rules/file-bridge-protocol.md`**, **`.claude/rules/codex-review-gate.md`**.
6. **Scoping carry-forward** at `bridge/gtkb-isolation-017-scoping-003.md` lines 186-202 + `-004` GO.
7. **GOV-09**, **GOV-19**, **GOV-20**.
8. **Prior Slice GOs:** Slice 1 `-012`, Slice 2 `-008`, Slice 2.5 `-008`, Slice 3 `-014`, Slice 4 `-012`, Slice 5 `-006`, Slice 6 `-004`, Slice 7 `-004` — all VERIFIED.
9. **NEW per F1 fix — Release-readiness blockers source:**
    - `memory/release-readiness.md:23-33` — "Release-Hardening Blockers (address during Slice 8 closeout)".
    - `memory/work_list.md:21-27` — Slice 8 scope statement + release-hardening enumeration.
10. **Existing surfaces modified per the 7 blockers:**
    - `groundtruth-kb/src/groundtruth_kb/__init__.py` — version bump (per Codex F2).
    - `groundtruth-kb/pyproject.toml` — version bump.
    - `groundtruth-kb/CHANGELOG.md` — release-notes entry.
    - `groundtruth-kb/release-notes-0.7.0-rc1.md` (new) — separate per release-readiness:29.
    - `groundtruth-kb/docs/announcements/v0.7.0-rc1.md` (new).
    - `memory/release-readiness.md` — `ISOLATION-017-CLOSEOUT` block.
    - Source files / test files / config files modified as part of full-repo ruff resolution + pytest feasibility (touched files determined by actual ruff/pytest output during implementation).
11. **Prior Deliberations:**
    - `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` — establishes v0.7.0-rc1 as release target.
    - S329 owner directives resolving Decisions 2/4/5 + the all-blockers-in-scope authorization.
    - `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE` v1 — Slice 5.5 deferral cited in announcement.

## Scope (REVISED-1)

### In-scope — full release-hardening + closeout

**Hardening blockers (per F1 fix — newly in scope):**

- **B1 — Version bump.** `groundtruth-kb/src/groundtruth_kb/__init__.py` line 16 `__version__ = "0.6.1"` → `__version__ = "0.7.0rc1"` (PEP 440 normalized form; tag is `v0.7.0-rc1`). `groundtruth-kb/pyproject.toml` `version` field synchronized.
- **B2 — Full-repo ruff resolution.** Probe `ruff check .` from repo root + `ruff format --check .` ; fix what's fixable in scope; for issues outside Slice 8 reasonable scope (e.g., issues in unrelated subsystems), surface explicitly with a deferral plan or scope-down request.
- **B3 — Full pytest feasibility.** Run `python -m pytest groundtruth-kb/tests/` to completion; document the runtime; identify any genuine timeouts vs slow-but-completing lanes. For CI feasibility: capture which lanes need parallelization vs which complete cleanly. Document in `release-notes-0.7.0-rc1.md` and `release-readiness.md`. (Note: my Slice 5 cross-test run completed in 586s — full-suite completion is achievable; "timeout" in S327 status may have been a tighter local limit.)
- **B4 — `release-notes-0.7.0-rc1.md` separate file.** New file at `groundtruth-kb/release-notes-0.7.0-rc1.md` mirroring the format of `release-notes-0.6.1.md`. Contains release notes prose + summary of B1-B7 evidence. ~150 LOC.
- **B5 — Wheel/sdist + install smoke.** Run `python -m build` (wheel + sdist) from `groundtruth-kb/`. Install built wheel into a tmp env; run `gt --version` (must show 0.7.0rc1) + `gt project init <tmp>/test-app --profile local-only` (must succeed); document the smoke result.
- **B6 — CI green evidence.** Push the Slice 8 implementation commit to develop; capture the GitHub Actions run URL; document the workflows that ran + their exit status. (May be partial in-session if CI takes >5 min; the post-impl REPORT documents the run URL with current status, and a follow-on capture commit updates the REPORT once CI completes.)
- **B7 — Bridge terminal state documentation.** All 7 ISOLATION-017 slice bridges are VERIFIED; release-readiness `ISOLATION-017-CLOSEOUT` block names each bridge ID. Standing-Backlog/Primer/Disambiguation deferred-status documented per S327 directive (already in release-readiness:33; this slice cites + retains that wording).

**Closeout artifacts (carry forward from `-001`):**

- `groundtruth-kb/CHANGELOG.md` — `[0.7.0-rc1] - 2026-05-03` entry under `[Unreleased]`, ~80 LOC.
- `groundtruth-kb/docs/announcements/v0.7.0-rc1.md` (new) — standalone announcement, ~150 LOC.
- `memory/release-readiness.md` — `ISOLATION-017-CLOSEOUT` block + B1-B7 outcome table, ~50 LOC change.
- `scripts/_verify_slice8_closeout.py` (new) — composite gate verifier covering all 7 blockers' outcomes, ~150 LOC (expanded from `-001`'s ~80 LOC).
- `IPR-SLICE8-RELEASE-OPS-001` + `CVR-SLICE8-RELEASE-OPS-001` + umbrella IPR/CVR for the program — embedded in post-impl REPORT.

**Total estimated:** 4-6 modified files (version bump + CHANGELOG + release-readiness + ruff fixes) + 4 new files (release-notes-0.7.0-rc1.md + announcement + verification script + bridge proposal) + ~700 LOC across all artifacts.

### Version tag (separate operator step, NOT in this commit)

Per `-001`'s constraint, carried forward unchanged.

### Out-of-scope (carried forward from `-001`)

- GA tagging (v0.7.0); Slice 5.5 (overlay refresh + disposability); PyPI publication; modifying Slices 1-7 surfaces; customer email / blog post.

## Implementation Plan (REVISED-1)

Sequenced for incremental verification:

1. **Probe baseline state** — run `ruff check .` + `python -m pytest groundtruth-kb/tests/ -q` from repo root + `groundtruth-kb/` respectively; capture current state. (~5 min)

2. **B1 version bump** — modify `__init__.py` + `pyproject.toml`; verify with `python -c "import groundtruth_kb; print(groundtruth_kb.__version__)"`. (~5 min)

3. **B4 `release-notes-0.7.0-rc1.md`** — author. (~20 min)

4. **CHANGELOG entry** — add `## [0.7.0-rc1] - 2026-05-03` block; cross-reference release-notes file. (~10 min)

5. **Standalone announcement** — author at `docs/announcements/v0.7.0-rc1.md`. (~30 min)

6. **B2 ruff resolution** — fix the issues from baseline probe; if scope balloons, surface explicitly. (~30-60 min depending on probe outcome)

7. **B5 wheel/sdist build smoke** — `python -m build`; install in tmp env; smoke `gt --version` + `gt project init`. (~30-60 min)

8. **B3 pytest feasibility documentation** — record full-sweep runtime + lane breakdown in release-notes-0.7.0-rc1.md. (~15 min after baseline run completes)

9. **B7 release-readiness `ISOLATION-017-CLOSEOUT` block** — append to `memory/release-readiness.md`. (~15 min)

10. **`scripts/_verify_slice8_closeout.py`** — composite gate verifier covering B1-B7. (~30 min)

11. **Run composite gate verifier** — confirm all 7 blockers report PASS. (~5 min)

12. **B6 CI green evidence** — captured POST-push as part of post-impl REPORT or follow-on commit. The REVISED-1 verification command for B6 is "documented run URL + workflow exit status"; the in-session post-impl REPORT will cite the run URL with current status; a follow-on may update once CI completes.

13. **Author IPR + CVR + umbrella IPR + umbrella CVR** — embedded in post-impl REPORT. (~30 min)

## Test Plan (spec-to-test mapping per F1+F2+F3 fixes)

| Blocker | Verification |
|---|---|
| B1 version bump | `python -c "import groundtruth_kb; print(groundtruth_kb.__version__)"` outputs `0.7.0rc1`; `pyproject.toml` `version` field equals `0.7.0rc1` |
| B2 full-repo ruff | `ruff check .` from repo root exits 0 (or surfaces an in-scope deferral with explicit exclusions) |
| B3 full pytest feasibility | `python -m pytest groundtruth-kb/tests/ -q` runs to completion (no infinite loop / hang); runtime + per-lane breakdown documented in release-notes-0.7.0-rc1.md |
| B4 release-notes-0.7.0-rc1.md | File exists at `groundtruth-kb/release-notes-0.7.0-rc1.md`; structure mirrors `release-notes-0.6.1.md`; cites all 7 ISOLATION-017 slices |
| B5 wheel/sdist install smoke | `python -m build` succeeds; `pip install dist/*.whl` in tmp env succeeds; `gt --version` reports 0.7.0rc1; `gt project init <tmp>/test-app --profile local-only` succeeds |
| B6 CI green evidence | post-impl REPORT cites GitHub Actions run URL on the Slice 8 commit + lists which workflows ran + exit status. Captured post-push. |
| B7 bridge terminal state | release-readiness `ISOLATION-017-CLOSEOUT` block names all 7 VERIFIED bridge IDs (Slices 1, 2, 2.5, 3, 4, 5, 6, 7) + cites the standing-Backlog/Primer/Disambiguation deferred status |
| Decision 2 (v0.7.0-rc1) | B1 + CHANGELOG + announcement + release-readiness all cite v0.7.0-rc1 |
| Decision 4 (4 publicity surfaces, together) | CHANGELOG + announcement + release-notes-0.7.0-rc1.md + cross-references to docs chapter + cross-references to examples |
| Decision 5 (composite acceptance gate) | `scripts/_verify_slice8_closeout.py` runs B1-B7 + the original 3 checks; all PASS |

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

## Acceptance Criteria (REVISED-1)

This REVISED-1 is GO-able when Codex confirms:

1. Specification Links cover all governing artifacts including the release-readiness blocker references at lines 23-33 (per F1 fix).
2. All 7 release-hardening blockers (B1-B7) are in implementation scope per §"Scope".
3. Version bump is part of the implementation plan, not just documentation (per F2 fix).
4. CI green evidence is part of the verification contract, captured post-push (per F3 fix).
5. The 4 closeout artifacts (CHANGELOG, announcement, release-readiness field, verification script) are retained from `-001`.
6. The verification script covers B1-B7 + the original 3 checks.
7. Estimated envelope ~700 LOC across all artifacts; substantial implementation work expected.
8. Owner-approved scope authorization cited (S329 AskUserQuestion answer "All blockers in scope (rigorous)").

## Risk / Rollback (REVISED-1)

**Risk 1 — Ruff resolution scope balloons.** If `ruff check .` baseline reveals hundreds of issues across unrelated subsystems, fixing them all in Slice 8 creates massive scope creep. **Mitigation:** baseline probe in step 1 surfaces the count + scope; if >100 issues outside Slice 8 reasonable scope (e.g., in deeply unrelated areas like Agent Red product code), surface as a sub-decision via AskUserQuestion before continuing.

**Risk 2 — Pytest full-sweep timeout reproduction.** If the full pytest hangs or fails in ways that block CI, the rc release blocks. **Mitigation:** baseline probe documents the actual current state; if hanging behavior reproduces, file a sub-bridge to scope/parallelize before continuing Slice 8.

**Risk 3 — Wheel build smoke environment drift.** Building + installing in a tmp env may surface `pip install` issues unrelated to Slice 8. **Mitigation:** smoke captures the failure mode; if it's a packaging defect rather than a Slice 8 defect, file a sub-bridge.

**Risk 4 — CI takes longer than session.** GHA runs may take 10-30+ minutes. **Mitigation:** REVISED-1 explicitly documents B6 as captured post-push with possible follow-on update once CI completes; this is acceptable per the post-impl pattern.

**Rollback path:** Slice 8 ships docs + a verification script + 1 release-readiness field + 1 CHANGELOG entry + 1 release-notes file + 1 announcement + version bumps + ruff fixes. Reversible via `git revert` of the implementation commit; no production impact possible (pre-tag, pre-publish).

## Decision Needed From Owner

**None at REVISED-1 time.** The all-blockers-in-scope decision was resolved at S329 via AskUserQuestion answer cited in §"NO-GO Acknowledgement". Sub-decisions (e.g., ruff scope balloon, pytest timeout) will be surfaced via AskUserQuestion at probe time only if they materially change scope.

## Open Items

- The `python -m groundtruth_kb.cli deliberations search --query "ISOLATION-017 release closeout"` probe will run as part of Codex review's Prior Deliberations check.
- The version tag (`git tag -a v0.7.0-rc1`) remains a separate post-VERIFIED operator step.
- B6 (CI green evidence) may be partial in-session per Risk 4 mitigation; post-impl REPORT will document current status.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
