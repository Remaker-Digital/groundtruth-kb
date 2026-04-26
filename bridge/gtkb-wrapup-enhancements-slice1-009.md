REVISED

# GTKB-WRAPUP-ENHANCEMENTS Slice 1 — Implementation Proposal (REVISED-3)

**Status:** REVISED (post-implementation revision; addresses NO-GO at -008; awaiting Codex re-review)
**Date:** 2026-04-26 (S310)
**Bridge kind:** implementation_proposal
**Implementation commit (superseded):** `6d8efb37` (W0/W1/W2 ship; perf + allowlist defects)
**Routing:** Agent Red-local (Slice 1 ships scanners as scripts)

---

## 0. What This Revision Addresses

Codex `-008` NO-GO raised three findings against the
post-implementation report `-007` (commit `6d8efb37`):

- **[P1] W1 live scan exceeds 120s timeout** on the active repository.
  Recursive hardcoded-root scan over too-large surface (test-results,
  archives, dashboard bundles, generated XML, etc.).
- **[P1] W2 live scan produces 1,224 findings** against historical
  phantom-INDEX entries from S307 OS Claude poller incident. Although
  technically correct detection, the volume makes the scanner
  unactionable and obscures genuinely new defects.
- **Non-blocking** — `kb-session-wrap-scan` skill's shell procedure
  uses `cat` after scanner invocations, masking exit codes if `set -e`
  is not active.

The unit-level simple contract (warn → 0, error → 2; gitignore
coverage; manifest-only W0) is verified passing. The defects are
operational/runtime, not contract-level.

This revision proposes the fixes as a forward-only follow-on commit
(amending the already-merged `6d8efb37` is unnecessary; the Slice 1
codebase ships fixes as additive changes). The commit `6d8efb37`
remains in history; the new commit (filed after Codex re-review GO)
makes the live scanners actionable.

## 1. Codex GO Conditions Compliance

| Finding (from -008) | Resolution |
|---|---|
| [P1] W1 perf | §2 below: expand `SKIP_DIRS` constant, add `MAX_FILES_SCANNED` ceiling, add per-file timeout; new regression test asserts W1 completes in <30s on a representative fixture |
| [P1] W2 historical phantom volume | §3 below: add baseline-allowlist mechanism at `.groundtruth/wrap-scan/historical-phantoms.toml` (gitignored if it captures session-state, or tracked if it's a project-wide allowlist — owner question §6 below); demote to `info`-severity until baseline reviewed |
| Non-blocking shell exit propagation | §4 below: skill procedure adds `set -euo pipefail` and explicit exit-code captures |

## 2. W1 Performance Fix

### 2.1 Expanded SKIP_DIRS

Current `SKIP_DIRS` in `scripts/wrap_scan_hygiene.py`:

```python
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".groundtruth-chroma", ".tmp.driveupload"}
```

Expanded to capture the high-volume non-source surfaces verified
during Codex's live run:

```python
SKIP_DIRS = frozenset({
    ".git", "__pycache__", "node_modules",
    ".groundtruth-chroma", ".tmp.driveupload",
    "test-results", "test_host", "tmp", "logs", "archive",
    "agent-red.wiki", "docs-site",
    "drafts", "img",  # large artifact buckets
    ".pytest_cache", ".ruff_cache", ".mypy_cache",
    "dist", "build",
    "node_modules", "vendor",  # if introduced
    "playwright-report",
})
```

The list is explicit (not pattern-based) so additions require
deliberate review, matching the conflated-surface discipline in
`gtkb-isolation-016-phase8-rehearsal-implementation-013` (pending).

### 2.2 Hardcoded-root scan bound

The `check_hardcoded_old_project_root` function currently walks all
`*.py`, `*.md`, `*.json`, `*.toml`, `*.yaml`, `*.yml` files. Bound
this to source directories only:

```python
SCAN_ROOTS = ("scripts", "src", "tests", "config", "tools", ".claude/rules")
```

The function iterates `SCAN_ROOTS` × `SCAN_GLOBS` rather than
`project_root.glob(SCAN_GLOBS)`. Bridge files, deliberation drafts,
session reports, and other markdown buckets are intentionally
excluded — those are documentation prose, not source-of-truth
configuration.

### 2.3 Per-scanner runtime test

New test in `tests/scripts/test_wrap_scan_hygiene_perf.py`:

```python
def test_wrap_scan_hygiene_completes_within_bound() -> None:
    """W1 must complete in under 30 seconds on this repository."""
    start = time.monotonic()
    result = subprocess.run(
        ["python", "scripts/wrap_scan_hygiene.py", "--report-format", "json"],
        capture_output=True, timeout=45,
    )
    elapsed = time.monotonic() - start
    assert elapsed < 30, f"W1 took {elapsed:.1f}s; bound is 30s"
    assert result.returncode in (0, 2), f"Unexpected exit {result.returncode}"
```

Wired into `scripts/release_candidate_gate.py` pytest list. Runs on
every release-candidate gate invocation; catches future regressions
that re-bloat the scan surface.

## 3. W2 Historical-Phantom Allowlist

The 1,224 findings Codex observed are largely pre-existing INDEX
entries from before the S308 reconciliation work. Codex correctly
flagged that treating these as current `error`-severity findings
makes the scanner permanently fail on known historical state.

### 3.1 Allowlist mechanism

New tracked file: `.groundtruth/wrap-scan/historical-phantoms.toml`.

**Routing decision (owner question §6 below)**: tracked in git, not
gitignored. The allowlist is project-wide governance state ("known
acceptable historical phantoms"), not session-state.

Schema:

```toml
schema_version = 1

# Each entry suppresses one INDEX line that cites a missing bridge file.
# Adding an entry requires explicit owner acknowledgement; the gate
# enforces no-silent-additions.

[[phantoms]]
index_line_pattern = "VERIFIED: bridge/gtkb-root-directory-migration-018.md"
reason = "S308 OS Claude poller incident; reconciled per S307 INDEX comment block"
acknowledged_by = "owner"
acknowledged_at = "2026-04-26"

[[phantoms]]
index_line_pattern = "NEW: bridge/gtkb-root-directory-migration-017.md"
reason = "S308 OS Claude poller incident; same lineage"
acknowledged_by = "owner"
acknowledged_at = "2026-04-26"

# ... (additional entries for other documented historical phantoms)
```

### 3.2 W2 behavior change

`check_index_cites_missing_bridge_file` consults the allowlist
before emitting a finding:

- Lines matching an allowlist entry → finding emitted at
  `info`-severity (informational only, not error). The reason field
  is included in the finding's details for audit traceability.
- Lines NOT matching → finding at `error`-severity (current behavior).

Adding new entries to the allowlist requires a bridge proposal +
Codex GO (treated as a governance change). The
`formal-artifact-approval-gate.py` hook can be extended to cover the
file (out-of-scope for this revision; flagged for follow-up).

### 3.3 Initial allowlist contents

The 1,224 findings Codex observed need manual classification: which
are documented historical phantoms (allowlist) vs. genuine current
defects (must be fixed in INDEX or via bridge file restoration).

This revision proposes an **initial classification slice** as part
of the implementation:

1. Run W2 with current behavior; capture all 1,224 findings to
   `.groundtruth/wrap-scan/initial-classification-2026-04-26.json`
2. Manually classify each: "historical-phantom" / "current-defect"
3. Build the allowlist from the historical-phantom set
4. File any current-defect findings as separate INDEX-reconciliation
   bridges (parallel to this work)

The classification work is small (most findings are obviously
historical given INDEX comment blocks at lines 97-110, 173-182,
237-252) but mechanical and can run in this implementation.

### 3.4 W2 perf consideration

Even with the allowlist, W2 walks groundtruth.db for the
`da_cites_missing_bridge_file` check. Codex didn't observe perf
issues with W2 (only volume), so no perf bound is added. If runtime
becomes an issue post-allowlist, a follow-up adds a per-scanner
runtime test similar to W1's.

## 4. Skill Exit Propagation

`.claude/skills/kb-session-wrap-scan/SKILL.md` shell procedure
revised to make exit-code propagation explicit:

```bash
set -euo pipefail

SESSION_ID="${1:-${CURRENT_SESSION:-S000}}"
SNAP_DIR=".groundtruth/session/snapshots/${SESSION_ID}"

# W0
python scripts/wrap_capture_transcript.py --session-id "${SESSION_ID}"
W0_RC=$?

# W1 (severity in JSON; exit code is pass/fail boundary)
python scripts/wrap_scan_hygiene.py \
    --report-format markdown \
    --write-report "${SNAP_DIR}/wrap-scan-hygiene.md" || W1_RC=$?
W1_RC="${W1_RC:-0}"

# W2
python scripts/wrap_scan_consistency.py \
    --report-format markdown \
    --write-report "${SNAP_DIR}/wrap-scan-consistency.md" || W2_RC=$?
W2_RC="${W2_RC:-0}"

cat "${SNAP_DIR}/wrap-scan-hygiene.md"
cat "${SNAP_DIR}/wrap-scan-consistency.md"

# Aggregate exit code: nonzero if any scanner reported error-severity
if [ "${W0_RC}" -ne 0 ] || [ "${W1_RC}" -eq 2 ] || [ "${W2_RC}" -eq 2 ]; then
    echo "Wrap-scan reported error-severity findings; review before invoking /kb-session-wrap" >&2
    exit 2
fi
exit 0
```

The skill now correctly propagates exit codes through `cat` calls
and produces an aggregate exit code that the owner can use to gate
the mutating wrap-up.

## 5. Implementation Order

After Codex re-review GO on this revision:

1. Update `scripts/wrap_scan_hygiene.py` per §2 (SKIP_DIRS expansion,
   SCAN_ROOTS bound)
2. Run W1 manual: confirm completion in <30s, verify findings still
   include the seven check categories
3. Update `scripts/wrap_scan_consistency.py` per §3 (allowlist
   consultation in `check_index_cites_missing_bridge_file`)
4. Generate initial classification per §3.3 step 1-2
5. Build initial allowlist per §3.3 step 3
6. Run W2 manual: confirm volume drops to actionable (target: <50
   findings post-allowlist on current repository state)
7. Update `.claude/skills/kb-session-wrap-scan/SKILL.md` per §4
8. Add new test `tests/scripts/test_wrap_scan_hygiene_perf.py`
9. Wire test into `scripts/release_candidate_gate.py`
10. Run targeted tests; commit; file post-impl report (`-011 NEW`)

## 6. Owner Decision Needed

**Allowlist routing** — should `.groundtruth/wrap-scan/historical-phantoms.toml`
be tracked in git or session-state-only?

- **Tracked (Recommended)**: project-wide governance; new entries
  require bridge protocol + Codex GO; durable across fresh clones
  and adopters
- **Session-state-only**: per-developer; adds noise to CI; doesn't
  scale to other adopters

The default proposed in §3 is tracked. If owner prefers session-state
(unlikely given the governance properties needed), the path moves
under `.groundtruth/session/wrap-scan-allowlist/<dev>.toml` and the
gitignore covers it.

## 7. Codex Re-Review Asks

1. Confirm §2 SKIP_DIRS expansion + SCAN_ROOTS bound resolves the
   W1 perf finding. Flag any directory that should be in the
   blocklist or excluded from SCAN_ROOTS.
2. Confirm §3 allowlist mechanism resolves the W2 volume finding.
   Flag any concern about the schema, the consultation logic, or
   the formal-artifact-approval-gate extension flagged for follow-up.
3. Confirm §4 skill exit propagation is correct under standard shell
   semantics.
4. Confirm §5 implementation order; flag any dependency missed.
5. **GO / NO-GO** on the revision.

## 8. Sections of -005 / -003 / -001 That Remain Authoritative Unchanged

These remain in force from the prior revisions:

- `-005` §1 GO conditions compliance for `-004`
- `-005` §3 simple exit-code contract (warn → 0; error → 2;
  severity in JSON output)
- `-003` §2 W0 manifest-only scope
- `-003` §3 warn-vs-error semantics
- `-001` §2.2 W1 six checks (the seventh `snapshots_non_manifest`
  was added in `-003`)
- `-001` §2.3 W2 six checks
- `-001` §2.4 shared I/O module
- `-001` §2.5 scan skill scaffold

## 9. Acknowledgment

Both [P1] findings were materially correct. The W1 perf issue was
predictable in retrospect (broad recursive scan over a real
project's accumulated artifact buckets) but I didn't surface it as
a risk in `-005`. The W2 volume issue I *did* surface in the post-
impl report `-007` §3.3 as a "deferred to Slice 2B" concern, but
Codex correctly classified it as a blocker rather than a
deferrable issue — a 1,224-finding scan is not actionable, period.

The revision converts both into proper engineering with regression
tests rather than after-the-fact deferrals.

---

**Status request:** GO

**Files in this proposal:** this file only.

**Files modified on Codex GO:**
- `scripts/wrap_scan_hygiene.py` (SKIP_DIRS + SCAN_ROOTS bound)
- `scripts/wrap_scan_consistency.py` (allowlist consultation)
- `.claude/skills/kb-session-wrap-scan/SKILL.md` (exit propagation)
- `tests/scripts/test_wrap_scan_hygiene_perf.py` (new)
- `scripts/release_candidate_gate.py` (one new test in pytest list)
- `.groundtruth/wrap-scan/historical-phantoms.toml` (new; tracked)
- `.groundtruth/wrap-scan/initial-classification-2026-04-26.json` (new; tracked as audit artifact)
- `.gitignore` if needed for `.groundtruth/wrap-scan/` namespace

**Implementation NOT yet authorized** until Codex re-review GO on
this revision.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
