NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 8cd56f34-2ccb-41c3-86e3-e099620f487d
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m

# Detect non-canonical verdict-shaped orphan bridge files (deterministic audit)

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4621

target_paths: ["scripts/audit_orphan_verdict_files.py", "platform_tests/scripts/test_audit_orphan_verdict_files.py"]

## Summary

WI-4621 (P2, defect, component `bridge-dispatch`). A concurrent Gemini/Antigravity
Loyal Opposition run wrote a GO-verdict-shaped Markdown file named
`gtkb-sweep-commit-pycache-prefix-001-VERDICT-20260616T160700.md`, but
`show_thread_bridge` still reports the thread `gtkb-sweep-commit-pycache-prefix`
as latest `NEW`: the verdict was never filed as the next numbered bridge version
(`<slug>-NNN.md`) and never published to live bridge state, so it silently
orphaned. A verdict that does not advance the thread's lifecycle is invisible to
the protocol — the worst kind of bridge integrity failure.

This proposal adds a deterministic, read-only audit that makes such
non-canonical verdict-shaped orphan files **visible failures** instead of silent
orphans.

## Problem

The bridge protocol's canonical file form is `bridge/<slug>-NNN.md` with a
zero-padded numeric version and a status token on the first non-blank line (per
`.claude/rules/file-bridge-protocol.md` § File Naming + § Body Status-Token
Rule). A reviewer verdict only advances a thread when it is filed as the next
numbered version AND published to live dispatcher/TAFE state. A verdict-shaped
file written outside the governed path — e.g. with a timestamped, non-numbered
name like `...-001-VERDICT-<timestamp>.md` — carries `GO`/`NO-GO`/`VERIFIED`
content but is structurally invisible: the thread still reads as `NEW`, and the
orphan file is never reconciled. Nothing currently surfaces this class of orphan.

## Proposed fix (standalone deterministic detector; conflict-free)

Add `scripts/audit_orphan_verdict_files.py` — a read-only, deterministic audit.
It is a NEW standalone script (it does not modify `scan_bridge.py`,
`show_thread_bridge.py`, `implementation_authorization.py`, or any dispatch
core), so it composes cleanly with concurrent bridge-dispatch work.

Behavior:

1. Enumerate `bridge/*.md`.
2. Classify each file as **canonical-named** iff its name matches the canonical
   pattern `^<slug>-\d{3,}\.md$` (slug + dash + zero-padded numeric version), per
   the file-bridge-protocol File Naming rule. The greedy slug segment correctly
   handles slugs that themselves contain digits (e.g.
   `...-retirement-001-013.md`).
3. Read the first non-blank line and classify the file as **verdict-shaped** iff
   that line is a canonical reviewer-verdict status token (`GO`, `NO-GO`, or
   `VERIFIED`), reusing the same status-token recognition the bridge surfaces use
   (the canonical token set from `.claude/rules/file-bridge-protocol.md` § Body
   Status-Token Rule).
4. **Flag** any file that is verdict-shaped AND NOT canonical-named: it is a
   non-canonical verdict-shaped orphan (the WI's exact failure class). Report
   `{path, first_line_status, reason}` for each.
5. Emit a `## Orphan Verdict Files` Markdown section and a `--json` form. Exit
   non-zero when any orphan is found (a visible failure suitable for a wrap-up /
   doctor / CI surface); exit `0` and report an empty list when none are found.

Scope boundary: this slice delivers the **detector** ("noncanonical
verdict-shaped files become visible failures"). A write-time *guard* that forces
all reviewer verdicts through the governed bridge path (the WI's alternative
"guard" clause) is intentionally deferred as a separate, higher-risk follow-on
(it would touch PreToolUse write interception); the detector is the deterministic,
low-risk core that surfaces both existing and future orphans.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — verdicts advance a thread only when filed as
  the next numbered version through the governed path; this audit surfaces
  verdict-shaped files that violate that authority model.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived verification.
- `.claude/rules/file-bridge-protocol.md` § File Naming + § Body Status-Token
  Rule — the canonical filename pattern and first-line status-token contract this
  detector enforces.
- `.claude/rules/codex-review-gate.md` — reviewer verdicts (GO/NO-GO/VERIFIED)
  are the artifacts this audit classifies.
- `.claude/rules/project-root-boundary.md` — both target paths are in-root.
- (advisory) `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Prior Deliberations

- Deliberation search (`gt deliberations search "orphan verdict file
  non-canonical bridge version governed path reviewer verdict"`) returned no
  on-topic prior decision (nearest matches — DELIB-20261587, DELIB-20261590,
  DELIB-20261595 — concern unrelated legacy-GOV cleanup, owner-decision-tracker
  restoration, and gate-friction hygiene).
- The canonical filename and body-status-token contracts this detector enforces
  are established by `GTKB-GOV-PROPOSAL-STANDARDS` Slice 1 (the Body
  Status-Token Rule in `.claude/rules/file-bridge-protocol.md`); this audit is a
  read-only consumer of those contracts, not a change to them.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-20261768` — seed=search; bridge_thread; Bridge thread: gtkb-work-tree-hygiene-slice-a-detector (4 versions, VERIFIED)
- DA: `DELIB-20262098` — seed=search; bridge_thread; Bridge thread: gtkb-da-enforcement-completion-slice1-decompose (11 versions, ORP
- DA: `DELIB-20261942` — seed=search; bridge_thread; Bridge thread: gtkb-verify-verdict-author-skill-slice-1 (4 versions, VERIFIED)
- DA: `DELIB-2818` — seed=search; bridge_thread; Bridge thread: gtkb-da-enforcement-completion-slice1-decompose (11 versions, VER
- DA: `DELIB-1198` — seed=search; bridge_thread; Bridge thread: gtkb-hook-scanner-safe-writer (12 versions, ORPHAN)

## Requirement Sufficiency

Existing requirements are sufficient. The canonical bridge file-naming and
first-line-status-token contracts (`.claude/rules/file-bridge-protocol.md`) and
the bridge authority model (`GOV-FILE-BRIDGE-AUTHORITY-001`) already define what
a canonical filed verdict is; WI-4621 prescribes surfacing non-canonical
verdict-shaped orphans as visible failures. No new or revised requirement is
needed before implementation.

## Spec-Derived Verification Plan

Spec-to-test mapping — each clause maps to a test in
`platform_tests/scripts/test_audit_orphan_verdict_files.py`:

- Orphan detection (WI's exact case):
  `test_flags_timestamped_verdict_shaped_orphan` writes a fixture
  `bridge/<slug>-001-VERDICT-20260616T160700.md` with first line `GO` and asserts
  the audit flags it (non-empty orphan list; exit non-zero).
- Canonical verdict not flagged:
  `test_canonical_numbered_verdict_not_flagged` writes `bridge/<slug>-002.md`
  with first line `GO` and asserts it is NOT in the orphan list.
- Non-verdict non-canonical file not flagged:
  `test_non_verdict_noncanonical_file_not_flagged` writes a non-canonical-named
  file whose first line is `NEW` (a proposal-shaped, not verdict-shaped, file)
  and asserts it is NOT flagged (the audit targets verdict-shaped orphans only).
- Slug-with-digits robustness:
  `test_canonical_slug_containing_digits_not_flagged` writes
  `bridge/<slug>-001-013.md` (slug ending in `-001`, version `013`) with first
  line `VERIFIED` and asserts it is NOT flagged.
- Empty/clean tree:
  `test_no_orphans_reports_empty_and_exit_zero` asserts a fixture bridge dir with
  only canonical files yields an empty orphan list and exit `0`.
- JSON output shape:
  `test_json_output_lists_orphans` asserts `--json` emits a machine-readable list
  of `{path, first_line_status}` entries.

Commands (resolved against the GT-KB venv interpreter, which carries `ruff`):

    .venv/Scripts/python.exe -m pytest platform_tests/scripts/test_audit_orphan_verdict_files.py -q
    .venv/Scripts/python.exe -m ruff check scripts/audit_orphan_verdict_files.py platform_tests/scripts/test_audit_orphan_verdict_files.py
    .venv/Scripts/python.exe -m ruff format --check scripts/audit_orphan_verdict_files.py platform_tests/scripts/test_audit_orphan_verdict_files.py

Expected: all tests pass; `ruff check` and `ruff format --check` clean on both
changed files.

## Acceptance Criteria

1. A verdict-shaped file (first non-blank line `GO`/`NO-GO`/`VERIFIED`) whose
   name does not match the canonical `<slug>-NNN.md` pattern is reported as an
   orphan and produces a non-zero exit.
2. Canonical numbered verdict files and non-verdict files are not flagged.
3. The audit is read-only (no bridge/MemBase/git mutation; it never renames,
   deletes, or rewrites any file).
4. `--json` provides machine-readable output for wrap-up / CI consumption.
5. `ruff check` and `ruff format --check` clean on both changed files.

## Risk and Rollback

- Risk: LOW. New, read-only, standalone audit script plus its test; it mutates
  nothing and touches no dispatch core. The only risk is a mis-classification
  (false positive/negative); the test suite pins the canonical-vs-orphan and
  verdict-vs-non-verdict boundaries.
- Blast radius: two new files. No change to `scan_bridge.py`,
  `show_thread_bridge.py`, `implementation_authorization.py`, hooks, or dispatch
  state — conflict-free with concurrent bridge-dispatch work.
- Rollback: delete the two new files; no state, schema, or behavior change
  remains.

## Owner Decisions / Input

None required. Implementation authority derives from the active,
owner-decision-backed project authorization
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` (owner
decision `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`). WI-4621 is an
unimplemented work item in PROJECT-GTKB-MAY29-HYGIENE, and the WI text prescribes
the behavior. No AskUserQuestion decision is needed.

## Recommended Commit Type

`feat:` — adds a new read-only audit capability (a net-new script + test).
