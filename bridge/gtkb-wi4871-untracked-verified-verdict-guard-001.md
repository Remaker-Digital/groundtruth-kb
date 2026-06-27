NEW

# Doctor guard: flag terminal-VERIFIED bridge threads whose verdict files are untracked in git (hook-less-harness finalization-bypass durability gap)

bridge_kind: prime_proposal
Document: gtkb-wi4871-untracked-verified-verdict-guard
Version: 001
Author: Prime Builder (harness B / claude)
Date: 2026-06-27 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: a0db7838-e5c0-4090-a4e0-68158f676275
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: interactive-prime-builder

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-RELIABILITY-GOVERNANCE-HARDENING-BATCH-WI-4457-4458-4871
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4871

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_doctor_untracked_verified_verdicts.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Add an additive, fail-soft `WARN` doctor check that flags terminal-`VERIFIED`
bridge threads whose verdict file is untracked in git — making the hook-less
harness finalization-bypass durability gap visible at session start.

**The gap.** The Mandatory VERIFIED Commit-Finalization Gate
(`.claude/rules/file-bridge-protocol.md`) requires a `VERIFIED` verdict to enter
git history in the same local commit as the verified work, via the Claude-side
helper `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`. A
hook-less harness (Cursor / harness E) writes the terminal `VERIFIED` verdict
file but does NOT run that finalization helper, so VERIFIED verdicts and their
verified implementations accumulate *untracked* in the working tree until a
manual `git` sweep. Evidence cited at WI-4871 capture (2026-06-27): WI-4665
VERIFIED-but-uncommitted 3h+, WI-4667 28min, 49 untracked bridge files across
many threads; commit `99aa43550` is a *manual* sweep finalizing Cursor-LO
verdicts — proving the pattern is real and only partially covered.

**Durability risk.** VERIFIED state living only in the working tree means a
checkout, reset, or mis-scoped sweep can silently discard hours of verified
work. There is currently no automated signal: verified absent against live code
2026-06-27 — `doctor.py` has no check for untracked terminal-VERIFIED verdicts
or finalization sweep.

**Scope chosen (lowest-risk slice).** WI-4871 offers three options: (1) make
hook-less finalization create the durable commit; (2) an automated
finalization-commit sweeper; (3) a doctor/guard that flags terminal-VERIFIED
threads whose verdict files are untracked. This proposal implements **option
(3)** — detection only — because it is additive, non-mutating, reversible, and
immediately reduces the durability risk by converting silent untracked-VERIFIED
state into a visible session-start advisory. Options (1) and (2) auto-mutate git
on a harness's behalf (higher risk, harness-specific) and are deferred as
possible follow-on slices; this detection guard is a prerequisite signal for
either.

New `_check_*` function in `doctor.py`: scan `bridge/*.md`; for each thread whose
latest versioned file's first non-blank line is `VERIFIED`, assert that verdict
file is present in `git ls-files`. Emit one `WARN` per untracked terminal-VERIFIED
verdict, naming the thread + file, with finalization/`git add` remediation
guidance. Fail-soft (`WARN`, never `FAIL`) so a transient mid-finalization state
never blocks `doctor`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the Mandatory VERIFIED Commit-Finalization
  Gate is bridge authority; this guard detects violations of that gate by the
  hook-less verdict-write path, preserving the audit-trail invariant that
  terminal VERIFIED state lives in git history.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the guard is the
  session-start advisory layer of defense-in-depth for the finalization
  requirement, complementing the Claude-side write-time finalization helper.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — triggered because target paths
  touch `groundtruth-kb/src/groundtruth_kb/project/**`. **In-root output
  declaration:** all generated artifacts — the new check code in `doctor.py`, the
  new test, and this bridge file under `E:\GT-KB\bridge\` — are in-root under
  `E:\GT-KB`. The check reads only in-root inputs (`bridge/` and `git ls-files`
  output) and declares no out-of-root output paths; the root/`applications/`
  boundary is honored.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage metadata
  is present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan below
  derives a test from the acceptance.
- `GOV-STANDING-BACKLOG-001` — WI-4871 is the standing-backlog work authority.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — converts a silent
  durability risk into a durable, visible advisory artifact.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — touching the doctor surface
  triggers the additive-test lifecycle obligation, satisfied below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — governs artifact-first
  treatment of the finalization-integrity surface.

## Prior Deliberations

- WI-4871 capture evidence (2026-06-27): WI-4665 / WI-4667 VERIFIED-but-uncommitted
  accumulation; commit `99aa43550` (manual Cursor-LO verdict finalization sweep)
  as proof the pattern is real and partial.
- WI-4680 (VERIFIED commit-finalization atomicity) and the
  `PAUTH-WI-4680-VERIFIED-COMMIT-ATOMICITY` authorization — the atomicity work on
  the Claude-side helper. This guard detects the case where that atomic path is
  *bypassed* (hook-less harness), so it complements rather than duplicates
  WI-4680.
- WI-4837 (Prime-side finalization-recovery gate-blocked) and WI-4749
  (verdict-evidence-anchor guard for the Antigravity hook-less verdict path) —
  the recovery side and the sibling hook-less-harness verdict concern; this
  proposal is the detection prerequisite for both.
- `DELIB-20266267` (owner AUQ 2026-06-27) — bounded authorization admitting
  WI-4871 (with WI-4457, WI-4458) under
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`.

## Owner Decisions / Input

- `DELIB-20266267` — owner AUQ answer "Bundle under bridge-reliability"
  (2026-06-27) admitted WI-4871 for bounded implementation under
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` via
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-RELIABILITY-GOVERNANCE-HARDENING-BATCH-WI-4457-4458-4871`.
- Owner directive this session (2026-06-27): author NEW proposals for the
  genuinely-open reliability/durability work items. No further owner decision is
  required to file; implementation still requires LO `GO` + the
  implementation-start packet.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement is the Mandatory
VERIFIED Commit-Finalization Gate under `GOV-FILE-BRIDGE-AUTHORITY-001` (terminal
VERIFIED state must enter git history) plus
`GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` (mechanical
enforcement). WI-4871 states the precise acceptance (option (3): a fail-soft
detection guard). No new or revised specification is required before
implementation.

## Spec-Derived Verification Plan

New test `platform_tests/scripts/test_doctor_untracked_verified_verdicts.py`:

- **Untracked terminal-VERIFIED verdict → WARN.** Fixture: a `bridge/<slug>-NNN.md`
  whose first non-blank line is `VERIFIED` and which is NOT in `git ls-files`;
  assert the check returns a `WARN` naming the thread + file. (Verifies
  `GOV-FILE-BRIDGE-AUTHORITY-001` finalization-gate enforcement + WI-4871
  acceptance.)
- **Tracked terminal-VERIFIED verdict → no WARN.** Fixture where the VERIFIED
  verdict is tracked; assert no finding. (Guards against false positives.)
- **Non-VERIFIED untracked file → no WARN.** A NEW/REVISED untracked draft must
  NOT trigger the check (only terminal VERIFIED is in scope).
- **Fail-soft severity.** Assert the finding severity is `WARN`, never `FAIL`.

Command (repo venv for reproducible evidence):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_doctor_untracked_verified_verdicts.py -q --no-header
```

## Risk / Rollback

- **Risk surface:** additive `WARN`-only check; no change to existing checks or
  to the finalization helper. Principal risk is a transient false-positive during
  the brief window between a verdict write and its finalization commit; mitigated
  by `WARN` (non-blocking) severity. The check reads `git ls-files` and `bridge/`
  only.
- **Rollback:** single-commit revert of the new `_check_*` function (and its
  registration in the doctor check list) plus the new test file.

## Recommended Commit Type

`feat` — net-new doctor guard + regression test (new detection capability).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
