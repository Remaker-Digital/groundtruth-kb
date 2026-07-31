ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 9f51b71b-00e7-4e37-9455-fd15d0b19e63
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Advisory - The Mandatory VERIFIED-Finalization Command Is Documented At A Path That Does Not Exist, And Every Committed Verdict Records That Non-Existent Path As Evidence

bridge_kind: governance_advisory
Document: gtkb-lo-verify-helper-path-drift-and-verdict-concurrency-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC

## Source

Observed directly by this reviewer on 2026-07-28 during a scheduled Loyal
Opposition run that filed terminal `VERIFIED` at
`bridge/gtkb-wi5659-protected-commit-finalizer-reconciliation-v2-006.md`
(commit `4efcb0ee2`). Every observation below is a file-system fact or a
command result produced by this repository's own tooling.

This advisory is scoped to **path drift in the finalization surface** and to a
**concurrency gap in terminal-verdict authoring**. It deliberately does not
restate the two-gate discoverability problem already filed at
`bridge/gtkb-lo-terminal-verdict-authoring-friction-advisory-001.md`, nor the
interrupted-transaction defect already filed at
`bridge/gtkb-lo-verified-finalization-interrupted-transaction-recovery-advisory-001.md`.
C4 below adds only a recurrence datapoint to the latter.

## Classification Slot

`adapt`. The corrective work is small, mechanical, and well-bounded, but the
choice of enforcement mechanism (lint versus test versus doctor check) is a
design decision that belongs to Prime Builder rather than being prescribed here.

## Claim

### C1 (P2). The mandatory VERIFIED-finalization command is documented at a path that does not exist

**Observation.** Four normative rule files instruct Loyal Opposition to finalize
`VERIFIED` verdicts by invoking
`.claude/skills/verify/helpers/write_verdict.py`. That file does not exist. The
real helper is at `.claude/skills/gtkb-verify/helpers/write_verdict.py`.

**Evidence.** Executed in this session:

1. `.claude/rules/file-bridge-protocol.md:178` - the Mandatory VERIFIED
   Commit-Finalization Gate's canonical command block cites
   `.claude/skills/verify/helpers/write_verdict.py`.
2. `.claude/rules/loyal-opposition.md:160` - the VERIFIED Commit Finalization
   section cites the same non-existent path.
3. `.claude/rules/codex-review-gate.md:130` - the "Record `VERIFIED` only
   through the atomic finalization helper" instruction cites it again.
4. `.claude/rules/auto-finalization-sweep.md:62` - the sweep's eligibility
   contract cites `.claude/skills/verify/helpers/write_verdict.py`
   `validate_verified_body()`.
5. Running the documented command verbatim fails:
   `can't open file 'E:\\GT-KB\\.claude\\skills\\verify\\helpers\\write_verdict.py': [Errno 2] No such file or directory`.
6. `find .claude/skills -name "write_verdict*"` returns exactly
   `.claude/skills/gtkb-verify/helpers/write_verdict.py` (plus its
   `__pycache__` artifact). The Codex projection at
   `.codex/skills/gtkb-verify/helpers/write_verdict.py` mirrors the same
   corrected directory name.

**Deficiency rationale.** This is rename drift: the skill directory was renamed
`verify` to `gtkb-verify` as part of the canonical `gtkb-*` skill-naming
convention, and the four rule files that hard-code the invocation were not
updated with it. The repository even ships a `gtkb-skill-rollout` skill whose
stated purpose is "renaming or adding canonical skills, including rename-map
update, adapter regeneration, and stale-dir cleanup" - so the rename procedure
exists, but nothing in it reaches normative rule text.

The severity is P2 rather than P3 because these four files are not
documentation-of-convenience. `file-bridge-protocol.md` and `codex-review-gate.md`
are the *mandatory gate* definitions: they are the authority that makes
commit-backed finalization obligatory. A reviewer following the mandatory rule
literally hits `ENOENT` on the single most governance-critical command in the
repository, and must then guess or search to find the real path. That is a
fail-to-ambiguity on a fail-closed surface.

**Recommended action.** Update the four rule-file citations to
`.claude/skills/gtkb-verify/helpers/write_verdict.py`. Because these are
protected narrative artifacts, the edit requires per-file
formal-artifact-approval packets per `GOV-ARTIFACT-APPROVAL-001` and
`DCL-ARTIFACT-APPROVAL-HOOK-001`.

### C2 (P2). The finalization helper hard-codes the non-existent path into every verdict it writes

**Observation.** The helper does not merely suffer from stale documentation
elsewhere; it stamps the wrong path into the machine-generated evidence section
of every `VERIFIED` verdict it produces.

**Evidence.**

- `.claude/skills/gtkb-verify/helpers/write_verdict.py:1009` emits the literal
  string:
  `"- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`\n"`
- The `## Commit Finalization Evidence` section of this session's own terminal
  verdict, `bridge/gtkb-wi5659-protected-commit-finalizer-reconciliation-v2-006.md`,
  therefore carries that non-existent path, and it is now immutable in commit
  `4efcb0ee2`.

**Deficiency rationale.** This converts a documentation defect into an
**evidence-integrity** defect. The `Commit Finalization Evidence` block exists
to let a future auditor reproduce how a terminal verdict was created. It names
a tool that cannot be run. Because the string is generated rather than authored,
the defect is uniform across every verdict finalized since the rename, and it is
append-only - already-committed verdicts cannot be corrected, only superseded by
accurate future ones. Every additional day of drift adds more permanently
inaccurate audit records.

This is also the reason C1 is unlikely to be noticed and fixed incidentally: the
helper works fine when invoked at its real path, so the only signal is a reader
following the citation, and that reader is by construction in the middle of a
governance-critical transaction and motivated to work around rather than report.

**Recommended action.** Correct the literal at
`.claude/skills/gtkb-verify/helpers/write_verdict.py:1009`. Prefer deriving the
string from the module's own resolved location rather than re-hard-coding it, so
the next rename cannot reintroduce the drift. Regenerate the `.codex/` adapter.

### C3 (P2). Nothing prevents two Loyal Opposition sessions from concurrently reaching terminal-verdict authoring on the same thread

**Observation.** During this run, a second Loyal Opposition session context
independently authored and committed a terminal `VERIFIED` verdict on a thread
this session had already scanned as actionable and had begun verifying. Neither
session held a work-intent claim on that slug at any point.

**Evidence.**

1. At run start, `gt bridge state-report` listed
   `gtkb-wi5706-wi5441-finalization-scope-repair` as LO-actionable, `NEW` at
   `-003`. A directory listing at that moment showed versions `001` through
   `003` only.
2. This session performed full independent evidence re-execution against report
   `-003` and authored a complete `-004` verdict body.
3. On submitting it, the finalization helper refused:
   `VERIFIED finalization requires a post-implementation report latest status of NEW, REVISED, or NO-ACTION; got VERIFIED at bridge/gtkb-wi5706-wi5441-finalization-scope-repair-004.md.`
4. That `-004` file had appeared mid-run, authored by
   `author_session_context_id: 6a29f0bd-92ac-4c8f-abdf-912a0dd69c86`
   (`Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo`),
   and was subsequently committed as `31d4a6d46`.
5. `python scripts/bridge_claim_cli.py status <slug>` returned `null` for both
   that slug and the other actionable slug - no holder at any point.

**Deficiency rationale.** `.claude/rules/file-bridge-protocol.md` § Mandatory
Pre-Drafting Claim Step requires a work-intent claim before substantive drafting
on any bridge thread, and states that the bridge-compliance-gate `PreToolUse`
Write hook enforces it. That enforcement does not reach the governed
finalization path: `write_verdict.py --finalize-verified` writes through
`write_bridge_file` (`write_bytes`), which bypasses the `PreToolUse` Write hook -
the same bypass that `_assert_verdict_review_independence` exists to compensate
for. Review independence was re-enforced at the helper layer; the claim
requirement was not.

The observable consequence is wasted duplicated verification work: two
independent Loyal Opposition sessions each performed a full evidence
re-execution of the same implementation report. In this instance the waste was
bounded and the outcome was correct, because `_assert_verification_ready` fails
closed when the latest status is already terminal. That is genuine
defense-in-depth and it worked. But it is a *late* defense - it fires after the
expensive work is complete, not before it starts, which is exactly the
value-versus-cost failure mode `bridge-essential.md` records as the lesson of the
retired pollers: gate the expensive action behind a cheap deterministic check.

Note also that this session *did* acquire a claim voluntarily before authoring
the second verdict, and the CLI accepted it with `acting_role: loyal-opposition`
- so the claim registry already supports Loyal Opposition holders. The gap is
that acquiring one is optional on this path, not that the mechanism is missing.

**Recommended action.** Require and verify a work-intent claim inside
`finalize_verified_commit` before the verdict body is written, mirroring how
`_assert_verdict_review_independence` re-enforces the independence rule at the
helper layer. Fail closed with a message naming the competing holder. A cheaper
interim measure is to make the scan surfaces (`gt bridge state-report` and the
scheduled-worker path) claim before beginning verification rather than before
writing.

### C4 (P3, recurrence datapoint only). The finalize transaction exceeded a two-minute wall clock and left a terminal verdict mid-transaction when interrupted

**Observation.** This session's `--finalize-verified` invocation exceeded a
two-minute tool timeout. At the moment of interruption, the `-006` verdict file
existed on disk, the canonical bridge state already reported the thread as
terminal (it had left the LO-actionable list), and `git status` still showed the
whole chain untracked.

**Evidence.** After the interruption, `git status --short` listed
`bridge/gtkb-wi5659-protected-commit-finalizer-reconciliation-v2-001..006` as
untracked while `gt bridge state-report` no longer listed the slug as
LO-actionable. Re-running `scripts/auto_finalize_sweep.py` resolved the state to
commit `4efcb0ee2` carrying exactly the six chain files and nothing else.

**Deficiency rationale.** The helper's documented contract is that if commit
creation fails it removes the just-written verdict and fails closed. That
rollback is implemented in an `except` handler, so it cannot run when the
process is killed rather than raising. The window between "verdict written and
state published" and "commit created" is therefore not crash-safe, and the
window is wide enough to matter: the transaction runs the protected-commit
authorization checker, whose cost is the subject of WI-5659 itself.

This is the failure mode already filed at
`bridge/gtkb-lo-verified-finalization-interrupted-transaction-recovery-advisory-001.md`.
It is recorded here only as a fresh recurrence datapoint with a measured wall
clock, and as evidence that `auto_finalize_sweep.py` is an effective recovery
path for this specific shape. No separate remediation is proposed.

## Owner Decision Needed

Three decisions, listed in the Required Prime Builder Owner-Grilling Gate
below and summarized here: (1) the enforcement mechanism and severity for a
guard that keeps rule-text helper invocations resolvable on disk; (2) whether
the finalization claim requirement hard-blocks immediately or warns during a
transition window; (3) the disposition of already-committed verdict evidence
lines that name the non-existent helper path. None is required to accept this
advisory; all three are required before a derived implementation proposal can
be filed as NEW.

## Recommended Prime Action

Run the owner-grilling gate below, then file a single NEW implementation
proposal covering C1 and C2 together (they are one rename-drift defect in two
surfaces) and, if the owner approves it, a separate proposal for C3, whose
behavior change to the governed finalization path warrants its own review
cycle. C4 needs no action here; it is a recurrence datapoint for an existing
advisory. Do not treat this advisory as implementation approval.

## Prime Builder Implementation Context

| Element | Detail |
| --- | --- |
| Objective | Eliminate the `verify` versus `gtkb-verify` path drift in normative rules and in generated verdict evidence; close the claim gap on the governed finalization path. |
| Preconditions | None blocking. C1 and C2 are independent of C3 and can land separately. |
| Evidence paths | `.claude/rules/file-bridge-protocol.md:178`; `.claude/rules/loyal-opposition.md:160`; `.claude/rules/codex-review-gate.md:130`; `.claude/rules/auto-finalization-sweep.md:62`; `.claude/skills/gtkb-verify/helpers/write_verdict.py:1009`; `scripts/bridge_claim_cli.py`. |
| File touchpoints | The four rule files (approval packets required); the helper literal; the `.codex/` adapter regeneration; `finalize_verified_commit` for C3. |
| Implementation sequence | (1) Correct the helper literal, preferably by deriving it from the module path. (2) Correct the four rule citations under approval packets. (3) Add a mechanical check that rule-text helper invocations resolve on disk. (4) Separately, add the claim requirement to `finalize_verified_commit`. |
| Verification steps | Assert that every `.py` path cited inside a fenced command block in `.claude/rules/*.md` exists on disk. Assert the helper's generated `Commit Finalization Evidence` line names an existing file. For C3, assert that finalization fails closed when a competing holder exists. |
| Rollback notes | All four changes are additive text or single-literal corrections; revert is a straight inverse edit. No data migration. |
| Open decisions | Whether the C1/C2 guard is a pytest assertion, a doctor check, or a lint; and whether C3's claim requirement should hard-block or warn during a transition window. |

## Required Prime Builder Owner-Grilling Gate

### Implementation implied

Yes. C1 and C2 require edits to four protected narrative artifacts and to one
source file. C3 requires a behavior change in the governed finalization path.

### Grill-the-owner questions

Prime Builder must obtain durable AskUserQuestion-recorded answers to:

1. Should the C1/C2 guard be a mechanical check (and if so, pytest, doctor, or
   lint), or is a one-time correction sufficient given that the rename is
   already complete?
2. Should C3's claim requirement hard-block terminal finalization immediately,
   or warn first? A hard block on a fail-closed path risks blocking legitimate
   verdicts if a stale claim is held; a warning risks continued duplicated work.
3. Are the already-committed verdicts carrying the inaccurate
   `Commit Finalization Evidence` path acceptable as historical record under
   append-only discipline, or does the owner want a superseding correction
   record?

### Required durable owner decisions

- Enforcement mechanism and severity for the helper-path guard.
- Hard-block versus warn for the finalization claim requirement.
- Disposition of the existing inaccurate committed evidence lines.

## Owner Decisions / Input

None yet. This advisory records reviewer findings and does not itself authorize
implementation. Per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`, the `adapt`
classification requires Prime Builder to run the owner-grilling gate above and
land the resulting AskUserQuestion evidence in any derived implementation
proposal's mandatory `## Owner Decisions / Input` section before that proposal is
filed as `NEW`.

## Prior Deliberations

- `bridge/gtkb-lo-terminal-verdict-authoring-friction-advisory-001.md` -
  companion advisory on verdict-authoring discoverability, including the
  `candidate_evidence_hash` two-pass sentinel flow and the 13 one-off verdict
  wrapper scripts. C1 and C2 here are a distinct defect class: that advisory
  cites the correct `gtkb-verify` path throughout, so the path drift is not
  covered by it.
- `bridge/gtkb-lo-verified-finalization-interrupted-transaction-recovery-advisory-001.md` -
  the interrupted-transaction defect. C4 above is a recurrence datapoint for it.
- `.claude/rules/auto-finalization-sweep.md` and `WI-4871` - the untracked
  terminal-VERIFIED durability guard and its remediating sweep, which resolved
  the C4 recurrence in this session.
- `bridge/gtkb-wi5659-protected-commit-finalizer-reconciliation-v2-006.md` -
  this session's terminal verdict, whose own generated evidence section carries
  the C2 defect.

## Skills applied

- `gtkb-advisory-proposal`
- `gtkb-lo-opportunity-radar`
