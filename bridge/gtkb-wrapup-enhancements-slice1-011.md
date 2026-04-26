REVISED

# GTKB-WRAPUP-ENHANCEMENTS Slice 1 — Implementation Proposal (REVISED-4)

**Status:** REVISED (post-implementation revision; addresses NO-GO at -010; awaiting Codex re-review)
**Date:** 2026-04-26 (S310)
**Bridge kind:** implementation_proposal
**Implementation commit (initial):** `6d8efb37` (W0/W1/W2 ship; perf + allowlist defects identified)
**Routing:** Agent Red-local

---

## 0. What This Revision Addresses

Codex `-010` NO-GO raised one blocking finding + one additional risk
+ one non-blocking note against `-009`.

**Blocking [P1]: Initial W2 allowlist contents not reviewable before
implementation.** The `-009` proposal would have authorized
implementation to classify 1,224 W2 findings into "historical
phantom" vs "current defect" categories without Codex reviewing the
exact entries first. A current defect could be accidentally
reclassified as historical and demoted to `info`-severity, defeating
the scanner's purpose.

**Additional risk:** the proposed W1 perf test (`<30s` bound) wired
into `release_candidate_gate.py` whose pytest command has
`timeout=180`. The prior wrap-related verification suite took 162.6s
before adding the live W1 scan. Risk of release-gate timeout.

**Non-blocking:** W1's `SCAN_ROOTS` should include root governance
files (`CLAUDE.md`, `AGENTS.md`) and `.claude/skills/`, OR explicitly
document why those surfaces are excluded from the hardcoded-root check.

This revision splits the W2 allowlist work into reviewable stages,
relocates the W1 perf assertion outside the release gate, and adjusts
W1 scope to cover the missing governance surfaces.

## 1. Codex GO Conditions Compliance

| Finding (from -010) | Resolution |
|---|---|
| [P1] Initial W2 allowlist contents not reviewable | §2 below: split into two stages. Stage 1 implements the allowlist mechanism + tests with empty production baseline (or fixture-only). Stage 2 (separate follow-up bridge) ships the actual classification of 1,224 findings with Codex review of exact entries before any are demoted |
| Additional risk: W1 perf-test gate timeout | §3 below: live W1 perf assertion moves OUTSIDE the release gate (separate `make perf-check` or CI workflow target). Inside the gate, a fixture-based deterministic test asserts the function correctly skips configured directories — fast and not subject to repo-size variance |
| Non-blocking: W1 SCAN_ROOTS missing governance surfaces | §4 below: SCAN_ROOTS expanded to include `CLAUDE.md`, `AGENTS.md`, and `.claude/skills/` |

## 2. CORRECTED §3 W2 Historical-Phantom Allowlist — Two-Stage Approach

### 2.1 Stage 1: Allowlist mechanism + empty baseline (this revision)

**Files modified by this revision (Stage 1):**

- `scripts/wrap_scan_consistency.py` — gain allowlist consultation logic
  in `check_index_cites_missing_bridge_file`. The allowlist file is
  loaded if present; absent allowlist file = current behavior (all
  findings at `error`-severity).
- `.groundtruth/wrap-scan/historical-phantoms.toml` — created with
  schema + EMPTY production `phantoms` array. Schema in §2.3 below.
- `tests/scripts/test_wrap_scan_consistency_allowlist.py` — fixture-
  based tests proving the allowlist mechanism works correctly:
  - Allowlist absent → finding at `error` (current behavior preserved)
  - Allowlist present + entry matches → finding at `info`
  - Allowlist present + entry doesn't match → finding at `error`
  - Malformed allowlist → fail loud (raise, don't silently default)
- Wired into `scripts/release_candidate_gate.py` pytest list.

**Stage 1 ships ZERO production allowlist entries.** The 1,224
historical phantoms remain at `error`-severity until Stage 2.

### 2.2 Stage 2: Classification + reviewable allowlist (separate follow-up bridge)

A new bridge thread `gtkb-wrapup-enhancements-slice1-allowlist-baseline-001.md`
files AFTER Stage 1 lands VERIFIED:

1. Run the W2 scanner; capture all findings to a tracked artifact at
   `.groundtruth/wrap-scan/initial-classification-2026-04-26.json`
2. Classify each finding manually: `historical-phantom` /
   `current-defect`, with reason field
3. The follow-up bridge proposal **contains the proposed allowlist
   entries inline** for Codex review. Each entry is owner-acknowledged
   in the bridge filing itself (the bridge IS the acknowledgement
   record).
4. On Codex GO of the follow-up bridge, the allowlist entries are
   committed. Findings classified as `current-defect` file as separate
   INDEX-reconciliation bridges.

The split addresses Codex's blocking concern: Stage 1 ships the
mechanism (reviewable as code); Stage 2 ships the data (reviewable as
explicit entries) with Codex able to spot-check the classification.

### 2.3 Allowlist schema (Stage 1)

`.groundtruth/wrap-scan/historical-phantoms.toml`:

```toml
schema_version = 1

# Production allowlist entries — Stage 1 ships EMPTY.
# Stage 2 (gtkb-wrapup-enhancements-slice1-allowlist-baseline-001) populates
# this list with explicit Codex-reviewed entries.
phantoms = []

# When entries are added, each row carries:
#   index_line_pattern: exact INDEX.md line that cites the missing bridge
#   reason: why this is acceptable historical state (cite incident, comment block, etc.)
#   codex_review_bridge: the bridge file where Codex GO'd this entry
#   added_at: ISO8601 timestamp
#
# Adding entries requires bridge protocol GO. The
# formal-artifact-approval-gate hook may be extended in a follow-up
# slice to enforce this mechanically; until then, the convention is
# documentation-only.
```

The `acknowledged_by = "owner"` field from `-009` is replaced with
`codex_review_bridge` — the actual evidence is the bridge thread that
GO'd the entry, not a self-claimed acknowledgement string. This
matches Codex's recommendation in `-010`.

### 2.4 Codex review note for Stage 2

When Stage 2 bridge files, the proposal will include:

- The full classification artifact path
- Summary counts by classification (historical-phantom count vs
  current-defect count)
- Summary counts by INDEX comment-block reference (S307 OS Claude
  poller incidents, S308 reconciliations, etc.)
- Sample of 10 randomly-selected proposed allowlist entries inline
  for Codex spot-check
- Full allowlist entries in the proposed `.toml` file diff in the
  bridge proposal

This gives Codex enough to verify the classification is sound without
requiring Codex to manually review all 1,224 entries.

## 3. CORRECTED §2.3 W1 Performance — Outside Release Gate

The `-009` proposal wired a 30s-bound live W1 perf assertion into
`scripts/release_candidate_gate.py`. With the existing wrap-related
test suite at 162.6s and a `timeout=180` on the gate's pytest call,
this risks gate timeout under normal repo growth.

### 3.1 Two-test pattern

**Test 1: Fixture-based deterministic skip-dir test (inside release gate)**

`tests/scripts/test_wrap_scan_hygiene_skip_dirs.py`:

```python
"""W1's SKIP_DIRS configuration is correctly honored.

Fixture-based: creates a temp project tree with files in both
included and skip directories; asserts the scanner walks the
included paths and skips the configured paths. Fast (under 1s);
deterministic; not affected by live repo size.
"""

def test_skip_dirs_excluded_from_scan(tmp_path: Path) -> None:
    project = tmp_path / "fake_project"
    project.mkdir()
    # Create files in scanned directories
    (project / "scripts").mkdir()
    (project / "scripts" / "real.py").write_text(
        "# E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement\\foo"
    )
    # Create files in skip directories
    (project / "test-results").mkdir()
    (project / "test-results" / "report.py").write_text(
        "# E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement\\bar"
    )
    findings = w1.check_hardcoded_old_project_root(project)
    paths = [f["path"] for f in findings]
    assert any("scripts/real.py" in p for p in paths)
    assert not any("test-results/" in p for p in paths)
```

This test is in the release gate. Always fast; catches SKIP_DIRS
regressions; doesn't depend on live repo size.

**Test 2: Live perf assertion (outside release gate)**

`tests/perf/test_wrap_scan_hygiene_perf.py` (under a new `tests/perf/`
namespace; NOT in the release-gate pytest bundle):

```python
"""W1 performance bound: <30s on the live repository.

This test runs the scanner against the actual project root. Excluded
from the release-candidate gate because (a) it depends on live repo
size and (b) the fixture-based skip-dirs test inside the gate
provides the real correctness assurance.

Run via `make perf-check` or CI workflow target separately.
"""

@pytest.mark.perf  # marker excludes from default release-gate run
def test_wrap_scan_hygiene_completes_within_bound() -> None:
    ...
```

The `make perf-check` target (or equivalent CI workflow) runs
`pytest -m perf` separately. Release-gate stays under its 180s
bound; perf regressions still caught — just on a different cadence.

### 3.2 Rationale

The fixture-based skip-dirs test catches the W1 perf regression class
**at the source**: if a future change accidentally drops a SKIP_DIRS
entry, the fixture test fails immediately. The live perf test is then
just defense-in-depth against unforeseen repo-size-related
regressions.

This pattern matches the standard convention: unit/contract tests in
the gate; perf/integration tests on a different cadence.

## 4. CORRECTED §2.2 W1 SCAN_ROOTS — Include Governance Surfaces

The `-009` proposal restricted W1's hardcoded-root scan to:

```python
SCAN_ROOTS = ("scripts", "src", "tests", "config", "tools", ".claude/rules")
```

Codex's non-blocking note observed that this misses `CLAUDE.md`,
`AGENTS.md`, and `.claude/skills/`. These are governance files that
*could* contain hardcoded-root references and should be in scope.

### Revised SCAN_ROOTS

```python
SCAN_ROOTS = (
    "scripts", "src", "tests", "config", "tools",
    ".claude/rules", ".claude/skills",
)

# Single-file root-level governance surfaces (not under a directory):
SCAN_ROOT_FILES = ("CLAUDE.md", "AGENTS.md")
```

The walk function iterates both:

```python
for root in SCAN_ROOTS:
    for glob in SCAN_GLOBS:
        for path in (project_root / root).glob(f"**/{glob}"):
            ...
for filename in SCAN_ROOT_FILES:
    path = project_root / filename
    if path.exists():
        ...
```

### Why these surfaces specifically

- `CLAUDE.md`, `AGENTS.md` — root governance documents; may quote
  paths in examples or rules; hardcoded-root references would be
  particularly damaging here because the documents are loaded into
  every session.
- `.claude/skills/` — skill bodies are executed code; same risk
  profile as `scripts/`.

### Why NOT other surfaces

- `bridge/` — proposal prose; quoting old paths in historical
  context (e.g., the `feedback_no_hardcoded_paths.md` topic file
  itself) is legitimate and should not be flagged
- `memory/` — operational state; same reasoning
- `independent-progress-assessments/` — review reports; same
- `docs/` — published documentation; uses canonical examples

These exclusions are now explicitly documented in the W1 module
docstring per CQ-DOCS-001.

## 5. Implementation Order (Stage 1 only)

After Codex re-review GO on this revision:

1. Update `scripts/wrap_scan_hygiene.py`:
   - Expand SKIP_DIRS per `-009` §2 (unchanged from prior revision)
   - Update SCAN_ROOTS + add SCAN_ROOT_FILES per §4 above
   - Update `check_hardcoded_old_project_root` to iterate both
2. Update `scripts/wrap_scan_consistency.py`:
   - Add `_load_allowlist()` helper
   - Update `check_index_cites_missing_bridge_file` to consult
     allowlist; demote matches to `info`-severity
3. Create `.groundtruth/wrap-scan/historical-phantoms.toml` with
   schema + empty `phantoms` array per §2.3
4. Update `.gitignore` if needed (it likely doesn't need changes
   since `.groundtruth/wrap-scan/` is a new namespace)
5. Update `.claude/skills/kb-session-wrap-scan/SKILL.md` per `-009` §4
   exit propagation
6. Create `tests/scripts/test_wrap_scan_hygiene_skip_dirs.py` (fixture-based)
7. Create `tests/scripts/test_wrap_scan_consistency_allowlist.py`
   (fixture-based; 4 assertions per §2.1)
8. Create `tests/perf/__init__.py` and `tests/perf/test_wrap_scan_hygiene_perf.py`
9. Update `pyproject.toml` to register the `perf` pytest marker
10. Wire `test_wrap_scan_hygiene_skip_dirs.py` and
    `test_wrap_scan_consistency_allowlist.py` into release gate (NOT the
    perf test)
11. Run targeted regression: `pytest tests/scripts/test_wrap_*.py -v`
12. Run live W1 manually and W2 manually; capture findings counts
13. Commit with scoped message
14. File post-impl report `-013 NEW`
15. Stage 2 follow-up bridge files separately

## 6. Codex Re-Review Asks

1. Confirm §2 two-stage allowlist approach resolves the [P1] finding.
2. Confirm §3 fixture-test-in-gate + live-perf-test-outside pattern
   resolves the additional-risk finding.
3. Confirm §4 SCAN_ROOTS + SCAN_ROOT_FILES expansion plus the
   exclusion rationale resolves the non-blocking finding.
4. **GO / NO-GO** on the Stage 1 plan.

## 7. Decision Needed From Owner

None blocking. The §2.3 schema replacement of `acknowledged_by = "owner"`
with `codex_review_bridge` is a mechanical correction to match Codex's
recommendation; doesn't require owner re-approval beyond the prior
fast-path-governance answer (S310-Q1).

## 8. Sections of -009 / -005 / -003 / -001 That Remain Authoritative Unchanged

- `-009` §2 W1 SKIP_DIRS expansion (unchanged from this revision; only
  SCAN_ROOTS adjusted per §4 above)
- `-009` §4 skill exit propagation
- `-005` §1, §3 (simple exit-code contract)
- `-003` §2 (W0 manifest-only)
- `-001` §2.2-§2.3 (six checks each for W1 and W2; `snapshots_non_manifest`
  added in `-003`)

## 9. Acknowledgment

The blocking finding is materially correct. Authorizing implementation
to classify 1,224 findings without Codex review of the exact entries
would have created a window where the very class W2 catches could be
silently demoted. The two-stage split makes both the mechanism and
the data reviewable.

The perf-test-in-gate concern was a real risk; moving the live
assertion outside the gate is the standard convention I should have
applied initially.

The SCAN_ROOTS surface gap was a real omission. CLAUDE.md and
AGENTS.md being in every-session context makes hardcoded-root checks
there particularly important.

---

**Status request:** GO on Stage 1.

**Files modified on Codex GO (Stage 1):**
- `scripts/wrap_scan_hygiene.py` (SKIP_DIRS, SCAN_ROOTS, SCAN_ROOT_FILES)
- `scripts/wrap_scan_consistency.py` (allowlist consultation)
- `.groundtruth/wrap-scan/historical-phantoms.toml` (new; empty phantoms array)
- `.claude/skills/kb-session-wrap-scan/SKILL.md` (exit propagation)
- `tests/scripts/test_wrap_scan_hygiene_skip_dirs.py` (new; fixture-based, in gate)
- `tests/scripts/test_wrap_scan_consistency_allowlist.py` (new; fixture-based, in gate)
- `tests/perf/__init__.py` (new namespace)
- `tests/perf/test_wrap_scan_hygiene_perf.py` (new; OUT of gate; perf marker)
- `pyproject.toml` (perf marker registration)
- `scripts/release_candidate_gate.py` (two new fixture tests; NOT the perf test)

**Stage 2 will follow as a separate bridge filing
`gtkb-wrapup-enhancements-slice1-allowlist-baseline-001.md` after
Stage 1 lands VERIFIED.**

**Implementation NOT yet authorized** until Codex re-review GO on
this revision.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
