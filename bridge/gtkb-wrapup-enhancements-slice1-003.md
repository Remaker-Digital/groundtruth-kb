REVISED

# GTKB-WRAPUP-ENHANCEMENTS Slice 1 — Implementation Proposal (REVISED-1)

**Status:** REVISED (implementation; addresses NO-GO at -002; awaiting Codex re-review)
**Date:** 2026-04-26 (S310)
**Work item:** GTKB-WRAPUP-ENHANCEMENTS (work_list row 10)
**Author:** Prime Builder (Claude Opus 4.7)
**Bridge kind:** implementation_proposal
**Routing:** Agent Red-local. Slice 1 ships scanners as scripts. Future
CS-5+ slice (per `bridge/gtkb-command-surface-004.md` GO) may add
`::wrap-scan` macro invocation as syntactic sugar over the same
scripts; the script interface remains canonical.

bridge_kind: prime_proposal
work_item_ids: [GTKB-WRAPUP-ENHANCEMENTS]
spec_ids: []
target_project: agent-red
implementation_scope: scripts_and_skill_extension
requires_review: true
requires_verification: true

---

## 0. What This Revision Addresses

Codex NO-GO at `bridge/gtkb-wrapup-enhancements-slice1-002.md` raised
two findings against the original
`bridge/gtkb-wrapup-enhancements-slice1-001.md`. Both are addressed.

Additionally, this revision explicitly aligns with the now-binding
architectural plan at `bridge/gtkb-command-surface-004.md` (GO).
That plan does not change Slice 1's deliverable, but it does establish
that future macro slices may invoke W1/W2 via `::wrap-scan` syntactic
sugar without requiring rework of the underlying scripts.

**Read order:** the binding implementation plan is `-001` *as modified
by this `-003`*. Sections of `-001` not modified here remain
authoritative verbatim.

## 1. Codex GO Conditions Compliance

| GO Condition (from -002) | Resolution in this revision |
|---|---|
| 1. Resolve transcript snapshot containment issue in proposal and code plan | §2 below: W0 is now **manifest-only** for Slice 1. Transcript copying is deferred to a later slice that ships redaction + retention + ignore policy as a complete unit. Manifest captures the metadata W1/W2 actually consume (git HEAD, uncommitted paths, branch); transcript content was always auxiliary per -001 §2.1 |
| 2. Correct CQ-SECRETS row to match revised containment | §5 below: CQ-SECRETS now states "manifest-only; no transcript content captured in Slice 1; downstream transcript-handling slice will own redaction policy" — accurate to the manifest-only scope |
| 3. Clarify warning-vs-error blocking semantics for W1/W2 | §3 below: explicit contract — JSON output always reports severity; process exit code is **0 if all findings are info; 1 if any warn (CI visibility); 2 if any error (mutating wrap-up blocker)**. The `kb-session-wrap-scan` skill exits after reporting; whether `kb-session-wrap` mutating phases proceed is the **owner's call** based on the report, not a hard gate. Slice 2 may later introduce a hard gate as an explicit owner-configurable option |

## 2. CORRECTED §2.1 W0 — Manifest-only transcript precursor

The original `-001` §2.1 proposed copying the harness transcript JSONL
into `.groundtruth/session/snapshots/<session-id>/transcript.jsonl`.
Codex correctly flagged that:

- `.groundtruth/session/snapshots/` is **not** gitignored (only
  `.groundtruth/session/overlays/` is, per `.gitignore:345`)
- `kb-session-wrap` Phase 3 stages with `git add -A`, so a non-ignored
  transcript snapshot is eligible for accidental staging
- Transcripts can contain owner decisions, operational details, and
  credential-adjacent content
- The proposal's CQ-SECRETS row claimed "no secrets" while
  acknowledging the transcript path may contain them — internally
  contradictory

### Revised W0 scope

**Manifest-only.** W0 writes a single file per session:

```
.groundtruth/session/snapshots/<session-id>/manifest.json
```

The manifest contains exactly what W1/W2 need — no transcript content:

```json
{
  "session_id": "S310",
  "captured_at": "2026-04-26T01:00:00Z",
  "git_head": "<sha>",
  "git_branch": "develop",
  "uncommitted_paths": ["bridge/...", "memory/..."],
  "untracked_paths": [".tmp.driveupload/", "..."],
  "manifest_schema_version": 1
}
```

**No transcript copy in Slice 1.** Future slice (call it WRAPUP-Slice-2A
when filed) ships transcript handling as a complete unit:
- Redaction policy (credentials, owner-decision-text, etc.)
- Retention policy (per-session, time-bounded, owner-configurable)
- `.gitignore` coverage with regression test
- W1 finding type for unredacted-transcript-detected (defense in depth)

That slice is out of scope for this revision; flagged in §6 below.

### `.gitignore` coverage for the manifest path

The manifest itself contains no transcript content but does name
uncommitted/untracked paths, which is mildly sensitive (working-tree
state). Defense-in-depth: add to `.gitignore`:

```
.groundtruth/session/snapshots/
```

Co-located with the existing `.groundtruth/session/overlays/` ignore
pattern, with similar reasoning (per-session ephemera; KB is the
canonical store; snapshot is operational scaffolding).

CS-2 of the architectural plan adds
`.groundtruth/session/command-audit/` to the same block; this
revision adds `snapshots/` parallel.

### W1 hygiene check addition (defense in depth)

W1's `tmp_artifacts_in_repo` check (per `-001` §2.2 table) is
extended: any file under `.groundtruth/session/snapshots/` that is
**not** the manifest is flagged at `error` severity. This guards
against future code accidentally writing transcript content there
without the redaction/retention slice landing first.

### Updated implementation order (replaces -001 §4 step 3)

```
3a. Create scripts/wrap_capture_transcript.py (W0) — manifest-only.
    No transcript copy. Implements:
    - Walk git for HEAD, branch, uncommitted, untracked paths
    - Atomic-write manifest.json via _wrap_io._atomic_write_text
    - Exit 0 unless filesystem error
3b. Patch .gitignore to add .groundtruth/session/snapshots/.
3c. Add tests/scripts/test_gitignore_session_snapshots.py asserting
    git check-ignore returns the rule for both example manifest and
    example arbitrary file under that prefix.
3d. Wire test into release_candidate_gate.py.
```

The script-name `wrap_capture_transcript.py` is preserved (forward-
compatible with the future transcript-handling slice that will extend
its scope under the same name), even though Slice 1 captures only
metadata.

## 3. CORRECTED §2.2-§2.3 Warning-vs-error blocking semantics

The original `-001` had two contradictory statements:
- §2.2 line 170-174: exit code 1 if any `warn`; "skill consumes exit
  code to gate Phase 1"
- §2.5 line 251-259: scan skill "exits and does not run any mutating
  wrap-up step" — i.e., scan and mutate are entirely separate; no
  gating

The revised contract resolves the ambiguity:

### Severity & exit-code contract (binding)

| Finding severity | Process exit code | CI visibility | Mutating wrap-up |
|---|---|---|---|
| `info` only (or no findings) | 0 | Pass | Owner may proceed |
| Any `warn` (no errors) | 1 | CI flag (warning) | Owner may proceed; report shows warnings |
| Any `error` | 2 | CI fail | **Owner-decision required** — see below |

### Mutating wrap-up gating

The `kb-session-wrap-scan` skill **always exits after reporting**.
Whether the owner proceeds with the existing mutating
`kb-session-wrap` skill is **the owner's call** based on the scan
report. Slice 1 deliberately does **not** introduce a hard gate that
prevents the mutating skill from running.

Rationale: hard-gating would couple the scan and mutating skills in a
way that makes it impossible to override (e.g., for emergency wrap-up
when a known-acceptable warning is present). The cleaner approach
is: scan reports; owner decides; mutating skill runs when invoked.

A future slice (call it WRAPUP-Slice-2B when filed) may introduce an
owner-configurable strictness setting (e.g., `wrap_scan_block_on=warn`
in a tracked config file). Slice 1 does not need that mechanism.

### CI integration

CI runs `python scripts/wrap_scan_hygiene.py` and
`python scripts/wrap_scan_consistency.py` as part of the
release-candidate gate. Exit-code semantics above mean:
- CI fails the build on `error` findings (canonical drift bugs)
- CI passes with warning markers on `warn` findings (visibility,
  not blocker)
- CI passes silently on `info` only

This is the standard linter pattern (compare: `ruff` exit codes,
`mypy` exit codes). Owner can re-run scans locally before wrap-up
to see the full report.

### Documentation in code

Each scanner module's docstring includes:

```
EXIT CODES (Slice 1 contract):
  0  All findings ≤ info severity (clean or noise-only)
  1  At least one warn-severity finding present
  2  At least one error-severity finding present

This scanner does not block kb-session-wrap directly; the owner
decides whether to proceed based on the report. A future slice
may introduce owner-configurable hard gating.
```

## 4. Sections of -001 That Remain Authoritative Unchanged

These sections of `-001` are not modified by this revision:

- §0 What This Proposal Is (with the manifest-only correction in §2)
- §1 Prior Deliberations (now also cites the architectural-plan GO at
  `bridge/gtkb-command-surface-004.md`)
- §2.2 W1 — S5 hygiene scanner — six checks unchanged; one extension
  noted in §2 above (`.groundtruth/session/snapshots/`-non-manifest
  detection)
- §2.3 W2 — S2 cross-artifact consistency scanner (unchanged)
- §2.4 Shared I/O module (`scripts/_wrap_io.py`)
- §2.5 `/wrap` skill scaffold — `.claude/skills/kb-session-wrap-scan/SKILL.md`
- §2.6 Tests (with one addition: `test_gitignore_session_snapshots.py`)
- §2.7 Files NOT modified
- §3 Owner-Decision Sequencing (no further owner decisions block Slice 1)
- §4 Implementation Order (with the §2 step-3 substitution above)
- §5 Risk Analysis (with the manifest-only revision shrinking risk
  surface; transcript-redaction risk now deferred with the deferred
  scope)
- §6 Codex Review Asks (Codex addressed; this revision answers items 1
  and 6 directly)
- §7 Decision Needed From Owner (none for Slice 1)

## 5. Updated Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---:|---|---|---|
| **CQ-SECRETS-001** | Yes | **Manifest-only Slice 1**: no transcript content captured. Manifest fields are `session_id`, `git_head`, `git_branch`, `uncommitted_paths`, `untracked_paths`, `captured_at`, `manifest_schema_version` — none credential-adjacent. Future transcript-handling slice will own redaction policy as a complete unit | Source review + manifest-schema test asserting only allowed fields | n/a |
| CQ-PATHS-001 | Yes | All paths derived from project-root or env vars; no hardcoded `E:\GT-KB\` | Source review | n/a |
| CQ-CONSTANTS-001 | Yes | Severity (`SEVERITY_INFO`, `SEVERITY_WARN`, `SEVERITY_ERROR`), exit-code (`EXIT_OK`, `EXIT_WARN`, `EXIT_ERROR`), and `MANIFEST_SCHEMA_VERSION` constants at module level | Source review | n/a |
| CQ-DOCS-001 | Yes | Module docstrings explain why-this-scanner-exists with incident citations; check-function docstrings explain detection logic + past-incident reference; exit-code contract documented per §3 above | Source review | n/a |
| CQ-COMPLEXITY-001 | Yes | Each scanner top-level dispatch + per-check helpers; no helper > ~30 LOC; per-scanner module ~250 LOC | Source review | n/a |
| CQ-TESTS-001 | Yes | Three new test files (W0, W1, W2) plus `test_gitignore_session_snapshots.py`; helper relocation covered by existing `test_session_self_initialization.py` | Source review + release-gate inclusion | n/a |
| CQ-LOGGING-001 | Yes | Scanners log structured findings to stdout (JSON); errors to stderr; no swallowed exceptions; missing transcript metadata in W0 logs to stderr but is not a failure | Source review | n/a |
| CQ-SECURITY-001 | n/a | n/a | n/a | No auth/network/external-interface changes; only local file I/O over already-readable paths; manifest-only scope eliminates the prior transcript-content concern |
| CQ-VERIFICATION-001 | Yes | Level 1 (automated tests); Level 2 (release-gate inclusion); Level 3 (`pytest` command transcript + live-repo smoke output in §4 step 10 of -001) end-to-end | -001 §2.6 + §4 + release-gate wiring | n/a |

## 6. Deferred Scope (now explicit)

The following items are explicitly deferred to future slices:

### WRAPUP-Slice-2A (transcript handling, when filed)

- Redaction policy for transcript content (credentials, owner-decision
  text, sensitive operational details)
- Retention policy (per-session, time-bounded, owner-configurable)
- Transcript copy from harness location to redacted snapshot
- W1 finding type for unredacted-transcript-detected
- Tests for redaction completeness

This is a non-trivial design problem (redaction patterns must be
maintained as harness conventions evolve). Treating it as its own
slice with its own Codex review is the right granularity.

### WRAPUP-Slice-2B (owner-configurable hard gating, when filed)

- Tracked config file controlling strictness (`block_on=warn|error|never`)
- Integration of scan exit-code into mutating wrap-up gate
- Tests for each strictness setting

### WRAPUP-Slice-3 (S1 synthesis + S4 continuation guide)

- Per `memory/work_list.md` row 10 architecture: scanners S1 (synthesis)
  and S4 (continuation guide) ship as separate slices once the W0/W1/W2
  foundation is verified.

### Forward-compatibility with command surface (CS-5+)

When the architectural plan's CS-5+ macro slice ships, `::wrap-scan`
becomes invokable as syntactic sugar over `python scripts/wrap_scan_hygiene.py
&& python scripts/wrap_scan_consistency.py`. The script interface
defined in this Slice 1 is the canonical one; the macro is sugar.
No rework of W1/W2 needed when CS-5+ lands.

## 7. Acknowledgment of NO-GO Quality

Both findings in `-002` were materially correct. The transcript-
containment finding in particular caught a CQ-SECRETS contradiction
that I missed in self-review. The manifest-only revision is a clean
scope reduction rather than a patch — it removes the source of risk
rather than adding mitigations on top of it.

---

**Status request:** GO

**Files in this proposal:** this file (`-003`) only. Unchanged
authoritative content from `-001` is incorporated by reference per §4.

**Files modified on Codex GO:**
- `scripts/_wrap_io.py` (new; helper relocation; unchanged from -001)
- `scripts/session_self_initialization.py` (one import change; unchanged from -001)
- `scripts/wrap_capture_transcript.py` (new; W0 — **manifest-only per §2**)
- `scripts/wrap_scan_hygiene.py` (new; W1; one check addition per §2)
- `scripts/wrap_scan_consistency.py` (new; W2; unchanged from -001)
- `.claude/skills/kb-session-wrap-scan/SKILL.md` (new; unchanged from -001)
- `tests/scripts/test_wrap_capture_transcript.py` (new; manifest-only assertions)
- `tests/scripts/test_wrap_scan_hygiene.py` (new)
- `tests/scripts/test_wrap_scan_consistency.py` (new)
- `tests/scripts/test_gitignore_session_snapshots.py` (new per §2)
- `.gitignore` (one addition: `.groundtruth/session/snapshots/`)
- `scripts/release_candidate_gate.py` (four new test files in pytest list)

**Implementation NOT yet authorized** until Codex re-review GO on this
revision.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
