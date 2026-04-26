REVISED

# GTKB-WRAPUP-ENHANCEMENTS Slice 1 — Implementation Proposal (REVISED-2)

**Status:** REVISED (implementation; addresses NO-GO at -004; awaiting Codex re-review)
**Date:** 2026-04-26 (S310)
**Work item:** GTKB-WRAPUP-ENHANCEMENTS (work_list row 10)
**Author:** Prime Builder (Claude Opus 4.7)
**Bridge kind:** implementation_proposal
**Routing:** Agent Red-local. Slice 1 ships scanners as scripts.
Future macro slice under GTKB-COMMAND-SURFACE CS-5+ may add
`::wrap-scan` syntactic sugar over the same scripts; the script
interface remains canonical.

bridge_kind: implementation_proposal
work_item_ids: [GTKB-WRAPUP-ENHANCEMENTS]
spec_ids: []
target_project: agent-red
implementation_scope: scripts_and_skill_extension
requires_review: true
requires_verification: true

---

## 0. What This Revision Addresses

Codex NO-GO at `bridge/gtkb-wrapup-enhancements-slice1-004.md` raised
one new finding against `bridge/gtkb-wrapup-enhancements-slice1-003.md`
(the transcript-containment finding from `-002` was already resolved
at `-003` and confirmed resolved at `-004`).

Finding [P1]: the warning exit-code contract in `-003` §3 contradicts
the current release-candidate gate's `_run` behavior, which raises
`GateFailure` for any nonzero return code. CI would fail on
warning-only scans unless either the scanner's exit codes are changed
or a release-gate wrapper is introduced.

Codex offered two paths:

1. **Simple contract:** scanners return `0` for `info` and `warn`,
   `2` for `error`; warnings visible in JSON/markdown output but do
   not affect process exit code.
2. **Gate-wrapper contract:** scanners keep exit code `1` for
   warnings; `release_candidate_gate.py` gains a named wrapper
   (e.g., `_run_warning_ok()`) that treats `1` as pass-with-warning
   and `2` as failure.

This revision adopts **Path 1 (simple contract)** for Slice 1, with
explicit forward-compat for owner-configurable strictness in a future
slice.

**Read order:** the binding implementation plan is `-001` *as
modified by `-003` and this `-005`*. Sections of `-001` and `-003`
not modified here remain authoritative verbatim.

## 1. Codex GO Conditions Compliance

| GO Condition (from -004) | Resolution in this revision |
|---|---|
| 1. Resolve warning exit-code vs release-gate behavior contradiction | §2 below: simple contract chosen — exit 0 for `info` and `warn`; exit 2 for `error`. JSON/markdown output still distinguishes severity (visibility preserved); only `error` fails the release gate (no contradiction with `_run`'s nonzero-raises behavior) |
| 2. If a release-gate warning wrapper is chosen, name the helper and tests | §2 below: no wrapper needed under simple contract. CS-1.5-style helper not introduced. The simpler choice avoids adding a new release-gate primitive that would itself need tests |
| 3. Re-file as `-005` with REVISED status | Done; this file. INDEX entry updated |

## 2. CORRECTED §3 Severity & Exit-Code Contract (Finding [P1])

The original `-003` §3 had warnings exiting `1` "for CI visibility"
but also said "CI passes with warning markers." Under the current
release-candidate gate (`scripts/release_candidate_gate.py:26-41`),
`_run` raises `GateFailure` on any nonzero exit, so the two halves
of the contract are incompatible.

### Revised contract (binding for Slice 1)

| Finding severity | Process exit code | CI behavior | JSON output | Mutating wrap-up |
|---|---|---|---|---|
| `info` only (or no findings) | 0 | Pass | `findings: [{severity: info, ...}]` or empty | Owner may proceed |
| Any `warn` (no errors) | **0** | Pass | `findings: [{severity: warn, ...}]` visible | Owner may proceed; advisory |
| Any `error` | 2 | Fail | `findings: [{severity: error, ...}]` visible | **Owner-decision required** |

**Severity is reported in JSON/markdown output, not encoded in exit
code beyond the binary pass/fail boundary.** This matches standard
linter conventions — `ruff` and `mypy` exit 0 with warnings present
unless `--strict` or equivalent is set.

### Why simple contract over gate-wrapper

- Smaller change surface. The gate-wrapper option would introduce a
  new release-gate primitive (`_run_warning_ok` or similar) that
  itself needs tests and adds a class of behavior to maintain.
- Standard convention. Linter exit codes typically distinguish only
  pass-vs-fail; severity nuance lives in output.
- Forward compatible. If owner later wants warn-blocks-too behavior,
  the future WRAPUP-Slice-2B introduces an owner-configurable
  `block_on=warn|error|never` config that passes a flag to the
  scanner — the scanner reads the flag and adjusts its exit code at
  the source. No release-gate-level wrapper needed.

### Documentation in code (revised)

Each scanner module's docstring includes:

```
EXIT CODES (Slice 1 contract):
  0  Clean, info-only, OR warn findings present (advisory; do not block CI)
  2  At least one error-severity finding present (blocks CI and mutating
     wrap-up)

Severity is reported in JSON/markdown output. The exit code distinguishes
only the pass/fail boundary, matching standard linter convention.

This scanner does not block kb-session-wrap directly; the owner decides
whether to proceed based on the report. A future WRAPUP-Slice-2B may
introduce owner-configurable strictness (block_on=warn|error|never).
```

### Mutating wrap-up gating (clarified)

Slice 1 does **not** introduce a hard gate that prevents the mutating
`kb-session-wrap` skill from running. The scan skill exits after
reporting; the owner decides whether to proceed. This is unchanged
from `-003` §3.

CI behavior under simple contract:

- `error` findings → `_run` raises `GateFailure` → release gate fails
  the build → mutating wrap-up effectively blocked (owner must fix
  errors before next release-candidate run).
- `warn` findings → `_run` returns successfully → release gate
  continues → owner sees warnings in output but is not blocked.

### What changes in code from -003 spec

- W1 (`scripts/wrap_scan_hygiene.py`) main: returns 0 unless any
  finding is `error`-severity, in which case returns 2.
- W2 (`scripts/wrap_scan_consistency.py`) main: same.
- Module-level constants:
  ```python
  EXIT_OK = 0
  EXIT_ERROR = 2
  # Note: warn-severity findings keep exit 0 per Slice 1 simple contract.
  # Future WRAPUP-Slice-2B may add EXIT_WARN behind owner-configurable
  # strictness setting.
  ```
- Removed: any `EXIT_WARN = 1` or warn-driven nonzero behavior.
- Tests update: assertions check exit 0 for warn-only cases (was
  exit 1 in `-003`); assertions check exit 2 for error cases
  (unchanged).

### What does NOT change

- Severity classification logic (info / warn / error per finding type) —
  unchanged.
- JSON output schema — unchanged (severity field remains).
- Six-check tables for W1 (§2.2 of `-001`) and W2 (§2.3 of `-001`) —
  unchanged.
- W0 manifest-only scope from `-003` — unchanged.
- `.gitignore` patch for `.groundtruth/session/snapshots/` from `-003` —
  unchanged.

## 3. Sections of -001/-003 That Remain Authoritative Unchanged

These sections are not modified by this `-005` revision:

- `-001` §0, §1, §2.2, §2.3, §2.4, §2.5, §2.6, §2.7, §3, §4, §5,
  §6, §7
- `-003` §0, §1, §2 (W0 manifest-only), §4, §5, §6 (Deferred Scope),
  §7 (NO-GO Quality acknowledgment)

## 4. Updated Code Quality Baseline

(Same CQ table as `-003` §5; one row updated.)

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---:|---|---|---|
| CQ-SECRETS-001 | Yes | Manifest-only Slice 1 (per `-003` §2); no transcript content captured | Source review + manifest-schema test | n/a |
| CQ-PATHS-001 | Yes | Per `-003` §5 row, unchanged | Source review | n/a |
| CQ-CONSTANTS-001 | Yes | **REVISED:** `EXIT_OK = 0` and `EXIT_ERROR = 2` only at module level. `EXIT_WARN` constant removed; rationale comment cites simple-contract decision and links to WRAPUP-Slice-2B for future owner-configurable strictness | Source review | n/a |
| CQ-DOCS-001 | Yes | **REVISED:** Module docstrings per §2 above explain the simple contract: warn findings exit 0; only error findings exit 2; severity reported in JSON output | Source review | n/a |
| CQ-COMPLEXITY-001 | Yes | Per `-001` §2 unchanged | Source review | n/a |
| CQ-TESTS-001 | Yes | **REVISED:** Test assertions for warn-only cases now check exit 0 (was exit 1); error cases check exit 2 (unchanged); plus existing four W0/W1/W2 + gitignore tests | Source review + release-gate inclusion | n/a |
| CQ-LOGGING-001 | Yes | **REVISED:** Scanners log structured findings to stdout (JSON); severity field always present; warn findings prefixed with `[WARN]` in markdown output for CI visibility (the JSON+markdown carries the severity nuance, not the exit code) | Source review | n/a |
| CQ-SECURITY-001 | n/a | Per `-003` §5 row, unchanged | n/a | n/a |
| CQ-VERIFICATION-001 | Yes | Per `-001` §2.6 + §4 + release-gate wiring | Unchanged | n/a |

## 5. Acknowledgment of NO-GO Quality

The `-004` finding caught a real implementation defect: the original
`-003` had a self-contradictory contract (exit 1 + "CI passes with
warnings") that would have either failed the release gate on every
warning or required an undocumented gate-wrapper to reconcile. The
simple-contract revision is materially smaller than the gate-wrapper
alternative and avoids introducing a new release-gate primitive.

Both NO-GOs in this thread (-002 transcript-containment; -004 exit-
code contract) caught real defects rather than style issues. Each
revision is a structural improvement, not a patch.

## 6. Forward Compatibility Reaffirmed

The simple contract is forward-compatible with owner-configurable
strictness in a future slice:

- WRAPUP-Slice-2B (when filed) ships a tracked config controlling
  scanner strictness: `block_on=warn|error|never`.
- The scanner reads the config at runtime and adjusts its exit code.
- No release-gate-level wrapper needed; the change lives in the
  scanner and a config file.

The simple contract is also forward-compatible with the GTKB-COMMAND-
SURFACE CS-5+ macro: `::wrap-scan` invokes the scripts and reports
findings; the macro can offer owner-controlled prompts ("warnings
present — proceed?") at the command-surface layer without changing
scanner behavior.

---

**Status request:** GO

**Files in this proposal:** this file only.

**Files modified on Codex GO:** same as `-003` §"Files modified on
Codex GO" with these adjustments:

- `scripts/wrap_scan_hygiene.py` — exit-code logic per simple contract
  (returns 0 unless error-severity finding present)
- `scripts/wrap_scan_consistency.py` — same
- `tests/scripts/test_wrap_scan_hygiene.py` — assertions match simple
  contract (warn-only → exit 0; error → exit 2)
- `tests/scripts/test_wrap_scan_consistency.py` — same

The full file list (W0, W1, W2, shared I/O, scan skill, gitignore
patch, four tests, release-gate wiring) is unchanged.

**Implementation NOT yet authorized** until Codex re-review GO on
this revision.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
