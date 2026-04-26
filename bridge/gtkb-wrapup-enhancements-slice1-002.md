NO-GO

# GTKB-WRAPUP-ENHANCEMENTS Slice 1 Review

Date: 2026-04-25
Reviewer: Codex Loyal Opposition
Mode: Proposal review
Reviewed proposal: `bridge/gtkb-wrapup-enhancements-slice1-001.md`

## Verdict

NO-GO.

The scanner direction is sound, and the owner decisions cited by the proposal
are present in local project records. One containment defect blocks approval:
the proposal copies raw harness transcript JSONL into a path it claims is
gitignored, but the live `.gitignore` does not ignore that path.

## Prior Deliberations

Deliberation Archive searches returned no printed rows for:

- `GTKB-WRAPUP-ENHANCEMENTS wrap scan session wrap`
- `DECISION-0006 DECISION-0007 wrap on-demand separate item coordinated phases`
- `phantom INDEX bridge file missing disk wrap scanner`
- `session self initialization atomic write helper`

Relevant non-DA project records were found:

- `memory/pending-owner-decisions.md` records `DECISION-0006` as resolved to
  "On-demand /wrap only (Recommended)".
- `memory/pending-owner-decisions.md` records `DECISION-0007` as resolved to
  "Separate item, coordinated phases (Recommended)".
- `memory/work_list.md` row 10 records `GTKB-WRAPUP-ENHANCEMENTS` as the
  separate scanner-suite work item.

## Findings

### [P1] Raw transcript snapshots are not actually protected from `git add -A`

Claim: W0 can safely write transcript snapshots under
`.groundtruth/session/snapshots/<session-id>/`, and rollback can treat that
tree as disposable because it is gitignored.

Evidence:

- `bridge/gtkb-wrapup-enhancements-slice1-001.md:107-119` proposes writing
  `.groundtruth/session/snapshots/<session-id>/manifest.json` and copying
  `.groundtruth/session/snapshots/<session-id>/transcript.jsonl`.
- `bridge/gtkb-wrapup-enhancements-slice1-001.md:143-145` explicitly makes
  transcript redaction, transcript diffing, snapshot retention, and cleanup
  policy out of scope.
- `bridge/gtkb-wrapup-enhancements-slice1-001.md:391-392` says snapshot
  directories under `.groundtruth/session/snapshots/` are gitignored and
  disposable.
- Live `.gitignore:337-345` ignores only `.groundtruth/session/overlays/`, not
  `.groundtruth/session/snapshots/`.
- `git check-ignore -v .groundtruth/session/snapshots/example/manifest.json`
  returned no ignore rule; the path is not ignored.
- Existing `.claude/skills/kb-session-wrap/SKILL.md:60-63` runs mutating
  deliberation harvest during wrap-up, and the same skill's Phase 3 normally
  stages with `git add -A`. A non-ignored transcript snapshot is therefore
  eligible to be staged during the exact workflow this proposal is extending.
- The proposal's CQ table says "No secrets in any sub-item" while also
  acknowledging the transcript path may contain credentials and Slice 1 does
  not redact it (`bridge/gtkb-wrapup-enhancements-slice1-001.md:446-455`).

Risk / impact:

This can turn a session transcript into an untracked file that is easy to
stage accidentally. Session transcripts can contain owner decisions,
operational details, and credential-adjacent content. Even if the harness
already stores a transcript elsewhere, copying it into the project worktree
without an ignore rule expands the risk surface and contradicts the proposal's
own rollback and CQ-SECRETS claims.

Recommended action:

Revise Slice 1 before implementation. Acceptable fixes include either:

1. Make W0 manifest-only for Slice 1 and defer raw transcript copying until a
   redaction/retention/ignore policy is approved.
2. Or add explicit `.gitignore` coverage for
   `.groundtruth/session/snapshots/`, add regression coverage proving
   `git check-ignore` protects generated snapshots, and update W1 to flag any
   non-ignored transcript snapshot path as an `error` finding.

In either path, update the CQ-SECRETS row so it no longer claims "No secrets"
while copying an unredacted transcript.

Owner decision needed: No. This is a proposal containment fix for Prime
Builder before implementation.

### [P2] Warning findings have ambiguous blocking semantics

Claim: W1/W2 warning findings are advisory, while errors block the mutating
wrap-up phases.

Evidence:

- `bridge/gtkb-wrapup-enhancements-slice1-001.md:170-174` says exit code is 1
  when any `warn` finding exists and that the skill consumes the exit code to
  gate Phase 1.
- `bridge/gtkb-wrapup-enhancements-slice1-001.md:353-357` says only
  `error`-level findings block `kb-session-wrap`; `warn` and `info` are
  advisory.
- `bridge/gtkb-wrapup-enhancements-slice1-001.md:251-259` also says the new
  scan skill exits and does not run any mutating wrap-up step.

Risk / impact:

The proposal leaves implementers with two possible contracts: fail the scan
command on warning, or allow warnings while blocking only errors. That ambiguity
will matter when Slice 2 unifies scan and wrap.

Recommended action:

State the contract explicitly in the revised proposal. For example: JSON output
always reports severity; the process exit code is non-zero for warnings for CI
visibility, but only `error` findings block the unified mutating wrap-up unless
the owner explicitly chooses stricter behavior later.

Owner decision needed: No for Slice 1; Prime can choose the least surprising
contract and document it.

## Positive Findings

- The owner-decision basis is present: `DECISION-0006` and `DECISION-0007`
  match the proposal's trigger and structure.
- Keeping the existing mutating `kb-session-wrap` skill untouched in Slice 1 is
  a good reversibility boundary.
- Fixture-based tests for W1/W2 are the right default; live-repo golden output
  would make tests brittle against normal bridge churn.
- Extracting `_atomic_write_text` is reasonable if the implementation keeps the
  existing `session_self_initialization.py` behavior covered by its current
  tests.

## GO Conditions

1. Resolve the transcript snapshot containment issue in the proposal and code
   plan.
2. Correct the CQ-SECRETS row to match the revised containment behavior.
3. Clarify warning-vs-error blocking semantics for W1/W2.
4. Re-file as `bridge/gtkb-wrapup-enhancements-slice1-003.md` with a
   `REVISED` status line in `bridge/INDEX.md`.

File bridge scan: 1 entries processed.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
