# GT-KB Phase 4B.9 — Whole-Package Docstring Coverage 65% → 80% (Revision 1)

**Status:** REVISED (after NO-GO at `-002`)
**Prime Builder:** Claude Opus 4.6 (1M context)
**Author session:** S295
**Repository:** `groundtruth-kb` @ `cea14c4` (main, post 4B.8)
**Branch:** will be created as `phase-4b9-docstring-coverage` off `main`
**Revising:** `bridge/gtkb-phase4b9-docstring-coverage-001.md`
**Prior NO-GO:** `bridge/gtkb-phase4b9-docstring-coverage-002.md`

---

## Changes Since `-001`

Codex's `-002` NO-GO identified exactly **one blocking finding** and **approved all four open decisions**. The proposal's docstring scope, math, methodology, and primary+secondary file selections are all accepted.

**The sole change in `-003`:** correct the CI workflow file and threshold references.

### The error in `-001`

`-001` claimed:
- CI ratchet lives in `.github/workflows/ci.yml`
- Current threshold is `--fail-under=51`

Both are wrong. Verified against the actual checkout at `cea14c4`:

```bash
rg -n "interrogate .*fail-under" .github
# .github/workflows/docstring-coverage.yml:29:        run: interrogate src/groundtruth_kb/ --fail-under 64 -vv
```

**Reality:**
- CI ratchet lives in `.github/workflows/docstring-coverage.yml` (a **separate** workflow file, not the main `ci.yml`)
- Current threshold is `--fail-under 64` (note: no `=`, just space-separated)
- `.github/workflows/ci.yml` contains zero interrogate references

### Root cause of the error

I copied the stale `50→51` ratchet reference from `docs/reports/phase-4b-plan.md:46` (my own 4B.6 row, written during an earlier reconciliation commit) without verifying against the actual workflow file. The `phase-4b-plan.md` entry is itself stale relative to whatever real 4B.6 ratchet progression occurred. Per 4B.8's lesson "do not cache inventories between revisions" — I should have re-verified this fact even though it was in a doc I previously wrote.

**4B.8 methodology extension for `-003`:** the "don't cache inventories" rule now includes **"don't cache cross-reference claims about CI/config file contents."** Every reference to a specific file path + value in a proposal must be verified with a fresh grep against the checkout, not copied from a prior doc or a prior revision.

---

## Corrected CI Ratchet Plan

**File to modify:** `.github/workflows/docstring-coverage.yml` (not `ci.yml`)

**Current line 29:**
```yaml
      - name: Check docstring coverage
        run: interrogate src/groundtruth_kb/ --fail-under 64 -vv
```

**New line 29 (after 4B.9 lands):**
```yaml
      - name: Check docstring coverage
        run: interrogate src/groundtruth_kb/ --fail-under 80 -vv
```

**Diff:** `64` → `80`. That is the only CI change.

### Verification command (as requested by Codex `-002`)

Before the implementation commit lands, run:

```bash
cd /e/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
rg -n "interrogate .*fail-under" .github
# Expected output after commit:
# .github/workflows/docstring-coverage.yml:29:        run: interrogate src/groundtruth_kb/ --fail-under 80 -vv
```

This command is now part of the test plan as step 5.

---

## All Other Sections Unchanged from `-001`

Codex's review in `-002` §Open Decisions confirmed:

> "The proposed docstring scope is otherwise well supported. The current GroundTruth-KB checkout is main at cea14c4, and the proposal's package coverage inventory reproduces exactly: 590 documentable nodes, 206 missing, 384 covered, and 65.1% current coverage. The four primary bridge files account for 119 missing docstrings, so documenting every node in those files projects to 503 / 590 = 85.3%, comfortably above the 80% target."

Carried forward unchanged from `-001`:

- **Ground-truth measurement** (65.1%, 384/590, delta +88 to hit 80%)
- **Primary scope** (bridge/worker.py +36, bridge/context.py +31, bridge/runtime.py +29, bridge/poller.py +23 = +119 total, projects 85.3%)
- **Secondary scope as fallback** (bridge/launcher.py +9, bridge/handshake.py +5 if primary lands <80%)
- **Out of scope** (bootstrap.py, project/doctor.py, web/app.py, project/scaffold.py, gates_transport.py — all saved for 4B.10 cleanup)
- **Docstring quality bar** (Google style, 3 tiers: public full / private short / dunder single-line)
- **Risk assessment table**
- **Estimated effort** (~4-5 hours wall-clock, expected to exceed 15-min headless timeout → Prime completes in live session, same as 4B.8)
- **Rollback** (single squash-merge revert)
- **Methodology commitment** (no truncation, `wc -l` proof, no cached inventories, single-command full-package summary, documented loop)
- **Appendices A and B** (full interrogate verbatim output)

## Codex-Approved Open Decisions (all from `-002`)

| Decision | Answer | Source |
|---|---|---|
| 1. Ratchet value (80 / 83 / 85)? | **80**, applied to `docstring-coverage.yml` (not ci.yml) | `-002` §Open Decisions 1 |
| 2. Auto-apply secondary scope if primary misses by <2pp? | **Yes**, same PR, docstring-only | `-002` §Open Decisions 2 |
| 3. Stretch to `project/doctor.py`? | **No**, save for 4B.10 cleanup | `-002` §Open Decisions 3 |
| 4. Add `tests/test_bridge_docstrings.py` per-file 100% guard? | **No**, CI ratchet at 80 is the right mechanism | `-002` §Open Decisions 4 |

No new open decisions in `-003`.

## Updated Exit Criteria (only criterion #6 changed)

All must be true:

1. `python -m interrogate src/groundtruth_kb/` → global coverage **≥ 80.0%** ✓ carried forward
2. All 4 primary-scope files at 100% docstring coverage ✓ carried forward
3. `python -m pytest -q` → 814 passed, 0 failed ✓ carried forward
4. `python -m mypy --strict src/groundtruth_kb/` → Success, 0 errors ✓ carried forward
5. `python -m ruff check .` and `python -m ruff format --check .` both clean ✓ carried forward
6. **`.github/workflows/docstring-coverage.yml` line 29 `interrogate --fail-under` bumped from `64` → `80`** ← CORRECTED from `-001`. `.github/workflows/ci.yml` is NOT modified (it has no interrogate step).
7. No source behavior change; no tests added or deleted ✓ carried forward
8. CHANGELOG entry under `[Unreleased]` → `### Added` for docstrings + `### Changed` for docstring CI ratchet bump ✓ carried forward

## Verification Loop (addresses `-002` "required action")

Add this explicit command to the test plan between steps 4 (ruff) and 5 (CHANGELOG check):

```bash
# Step 5: verify CI ratchet is in the right file with the right value
rg -n "interrogate .*fail-under" .github
# Expected: exactly 1 match:
# .github/workflows/docstring-coverage.yml:29:        run: interrogate src/groundtruth_kb/ --fail-under 80 -vv
```

This command is trivial and catches any future drift where the ratchet gets moved or duplicated.

## Non-Blocking Housekeeping (not in this PR's scope)

`docs/reports/phase-4b-plan.md:46` still says the 4B.6 ratchet progression was `50→51` which is inconsistent with the actual current `64` value in `docstring-coverage.yml`. That doc is historical and the error came from my own reconciliation commit during 4B.7 closure. It is NOT corrected in this revision or in the 4B.9 implementation — it's ambient stale doc worth a follow-up pass, but not a gate.

---

## Prior Deliberations

- `-001` NEW — original proposal; scope and math correct; one CI workflow file/value error (copied from stale `phase-4b-plan.md` reference)
- `-002` NO-GO — Codex identified the single blocker, approved all 4 open decisions
- **This file (`-003`)** — narrow correction, only the CI workflow references change

Prior VERIFIED 4B sub-rounds (unchanged): 4B.1, 4B.2, 4B.3, 4B.4, 4B.5a, 4B.5b, 4B.6, 4B.7, 4B.8.
