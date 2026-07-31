ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 8acf3d52-8dbb-4759-a1b7-41424e4c6cb6
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled Loyal Opposition worker; envelope-resolved loyal-opposition role; test activity
author_metadata_source: session envelope (worker_role_provenance)

# LO Advisory - VERIFIED-finalization toolchain drift and blind spots - 001

bridge_kind: governance_advisory
Document: gtkb-lo-verified-finalization-toolchain-drift-advisory
Version: 001
Date: 2026-07-29 UTC
Author: Loyal Opposition (claude, harness B)

## Purpose

This advisory records defects found **outside the scope** of the six bridge
items processed in this Loyal Opposition run. None of them is attributable to
the threads under review; all were surfaced incidentally while exercising the
verdict-authoring and VERIFIED-finalization toolchain end to end.

This advisory is not implementation approval. It tasks Prime Builder with
owner-grilling and, where adopted, a normal scoped implementation proposal.

## Source

Loyal Opposition scheduled worker run, 2026-07-29, session context
`8acf3d52-8dbb-4759-a1b7-41424e4c6cb6`. Findings were surfaced incidentally while
processing six LO-actionable bridge items and exercising the verdict-authoring
and VERIFIED-finalization toolchain end to end. Primary evidence surfaces:
`platform_tests/scripts/test_lo_verified_commit_atomicity.py`,
`platform_tests/skills/test_auto_retire_actuation_helper_parity.py`,
`.claude/skills/gtkb-verify/helpers/write_verdict.py`,
`.claude/hooks/bridge-compliance-gate.py`,
`config/governance/lo-file-safety.toml`, and the three tracked copies of the
finalization helper.

## Claim

The VERIFIED-finalization toolchain carries seven defects that are invisible to
the bridge gates themselves. Two are P1: the regression suite guarding
finalization atomicity is entirely red and asserting nothing (A1), and the
VERIFIED compliance gate is unsatisfiable by honest means for bridge-only
evidence carriers, creating verification deadlock and pressure toward fabricated
test evidence (A7). Three are P2/P3 tooling-ergonomics and drift defects that
push reviewers toward dropping mandatory governance sections (A2), record a
retired helper path as provenance in every verdict written (A3), and leave a
stale divergent copy of the finalization helper tracked in the repository (A4).
Two are P3/P4 hygiene items in the Loyal Opposition file-safety surface (A5, A6).

## Owner Decision Needed

Yes - four decisions, enumerated under
`## Required Prime Builder Owner-Grilling Gate` below. None is blocking on this
advisory's filing; all are required before any derived implementation proposal
may be filed.

## Recommended Prime Action

File scoped implementation proposals for A1, A2, A3, A4, A5 and A7 after
completing the owner-grilling gate. Recommended sequencing: A1 and A7 first
(both P1; A7 unblocks a thread that is currently stuck non-terminal), then A3
and A4 with the skill-rename sweep, then A2 and A5. Capture A6 as a backlog item
without immediate work.

## Classification Slot

`adapt` - the recommendations are adopted in substance but must be adapted to
GT-KB's existing scope boundaries: A1 and A3 belong inside the
`GTKB-SKILL-RENAME-REFERENCE-SWEEP` umbrella rather than a new workstream, and
A7's remedy must be conditioned on bridge-only `target_paths` rather than
implemented as a general relaxation of the VERIFIED evidence gate.

## Findings

### [P1] A1 - The LO VERIFIED commit-atomicity suite is entirely red and providing zero signal

**Observation.** Two test modules still import the **pre-rename** bare
`skills/verify/` helper path and fail wholesale:

- `platform_tests/scripts/test_lo_verified_commit_atomicity.py:19` -
  `CURSOR_VERIFY_HELPER_PATH = REPO_ROOT / ".cursor" / "skills" / "verify" / "helpers" / "write_verdict.py"`
- `platform_tests/skills/test_auto_retire_actuation_helper_parity.py:19` -
  `"cursor": REPO_ROOT / ".cursor" / "skills" / "verify" / "helpers" / "write_verdict.py"`

Executing both modules yields `8 failed, 1 passed, 29 errors`. The failures are
not Cursor-specific - they hit `claude` and `codex` too:

```
FileNotFoundError: 'E:\GT-KB\.claude\skills\verify\helpers\write_verdict.py'
FileNotFoundError: 'E:\GT-KB\.codex\skills\verify\helpers\write_verdict.py'
FileNotFoundError: 'E:\GT-KB\.cursor\skills\verify\helpers\write_verdict.py'
```

**Deficiency rationale.** These suites guard the atomicity of the VERIFIED
commit transaction - the exact mechanism that makes a terminal verdict durable
rather than file-only. They are currently incapable of detecting a regression in
that mechanism. This is a silent false-green class: the modules exist, are
collected, and appear in coverage inventories, but assert nothing because they
abort at import.

**Why this matters now.** `.claude/rules/auto-finalization-sweep.md` and the
`gtkb-lo-verified-finalization-interrupted-transaction-recovery-advisory-001`
family document live defects in precisely this path. Losing regression coverage
over the finalizer while known finalizer defects are open is the worst possible
time for it.

**Proposed action.** Repair both modules' helper-path literals to the renamed
`gtkb-verify` surface, under the existing skill-rename sweep. Confirm a sibling
work item in the `WI-5662..WI-5668` range explicitly owns them; if none does,
file one. Do not close the `GTKB-SKILL-RENAME-REFERENCE-SWEEP` umbrella until
these land.

**Option rationale.** Repairing the literals is preferred over quarantining the
modules: the assertions themselves are sound and were passing before the rename,
so the defect is purely referential. Deleting or skipping them would convert a
detectable false-green into an undetectable coverage hole.

### [P2] A2 - The mandatory Applicability Preflight section is structurally incompatible with the VERIFIED finalization helper

**Observation.** Two governed requirements collide:

1. `.claude/rules/file-bridge-protocol.md` § Mandatory Applicability Preflight
   Gate requires the `## Applicability Preflight` section in every `GO` and
   `VERIFIED` verdict.
2. `.claude/hooks/bridge-compliance-gate.py:1493-1517`
   (`_verdict_preflight_freshness_deny_reason`) fires **only when** that section
   is present, and then demands a `candidate_evidence_hash` computed over the
   final normalized bytes of the verdict file.
3. `.claude/skills/gtkb-verify/helpers/write_verdict.py:1002-1014`
   (`_append_commit_finalization_evidence`) **appends** a
   `## Commit Finalization Evidence` section to the body *before* calling
   `write_bridge_file`.

**Deficiency rationale.** A reviewer who authors a compliant VERIFIED body -
including the mandated preflight section - and computes the hash over the
reviewed body will have that hash invalidated by the helper's own append. The
gate then rejects the write. The only way through is to notice that the append
is skipped when the body already contains a `## Commit Finalization Evidence`
section (line 1003), hand-author that section, and only then compute the hash.
That workaround is undocumented in the rule, the skill, and the helper's
`--help`.

**Impact.** Reviewers hit an opaque
`expected <unavailable>` / hash-mismatch error with no guidance toward the
cause. The likely failure mode under time pressure is to omit the preflight
section entirely - which silently drops a mandatory governance gate from
terminal verdicts. That is a governance-weakening incentive created purely by
tooling ergonomics.

**Proposed action.** Make the helper compute and inject `candidate_evidence_hash`
itself, after all body mutations and immediately before `write_bridge_file`. It
already owns the final bytes and the target path - the two inputs
`_candidate_evidence_hash` needs. Reviewers would then author the preflight
section with the sentinel and the helper would resolve it.

**Option rationale.** Preferred over documenting the workaround, because
documentation does not remove the incentive to drop the section, and preferred
over relaxing the freshness check, which exists for a good reason (it binds a
verdict body to its own file path and content, preventing verdict-body reuse
across threads).

### [P3] A3 - The finalization helper emits a retired skill path in every verdict it writes

**Observation.** `.claude/skills/gtkb-verify/helpers/write_verdict.py:1009`
hardcodes:

```
"- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`\n"
```

`.claude/skills/verify/` does not exist; the live surface is
`.claude/skills/gtkb-verify/`.

**Deficiency rationale.** Every VERIFIED verdict finalized by the helper records
a non-existent path as its provenance evidence. This is self-inflicted audit
drift: the artifact that exists to prove how the commit was made cites a tool
that cannot be found. It also seeds the retired literal into new files, working
against the sweep that is trying to remove it.

**Proposed action.** Correct the literal to the `gtkb-verify` path. Fold into the
`GTKB-SKILL-RENAME-REFERENCE-SWEEP` scope alongside A1; `WI-5662` already covers
"stale skill-rename refs in canonical SKILL.md docs and helper docstrings/hints"
and this is the same class at a higher-consequence site.

### [P3] A4 - A tracked, stale, divergent copy of the finalization helper exists under `.goose`

**Observation.** Three real git-tracked copies of `write_verdict.py` exist.
`.claude` and `.codex` are byte-identical
(`sha256 E687612B9C8FEE862F091DB93859E6C90C88E3964B269724C6148BDB812C71E0`);
`.goose/skills/gtkb-verify/helpers/write_verdict.py` differs
(`549E12E6B8CB2F998C36D06B51DA8AC98A013ED2D6D5EE766ABAE66535AF5EC2`, 1344 vs
1355 lines).

The `.goose` copy is an **older revision**: it still defines
`_cleanup_failed_verdict()` (which unlinks the verdict) instead of
`_cleanup_failed_staging()`, and it entirely lacks the
`finalize_pending_bridge_publication` / `rollback_pending_bridge_publication`
governed-publication path.

**Deficiency rationale.** A stale tracked copy of the finalization helper that
lacks the pending-publication rollback path is a live correctness hazard if any
session loads it, and nothing in the repo currently asserts it is in sync. The
`skill.verify` capability has no `[capabilities.goose]` entry, and Goose holds
`prime-builder`, so the capability is not formally required for it - which is
why this is P3 rather than P2, and also why the divergence has gone unnoticed.

**Proposed action.** Either add `"goose"` to the `HELPER_COPIES` parity fixture
in `platform_tests/skills/test_verified_finalization_validation_hardening.py`
(which would restore that test function's name to truth and catch future
divergence mechanically), or explicitly retire the `.goose` copy. Note that
`bridge/gtkb-skill-rename-cursor-goose-parity-002.md` Finding 2 already
dispositions the missing Goose manifest as ADOPT, so this is adjacent to
accepted work.

### [P3] A5 - The Loyal Opposition file-safety allow-list has no path for LO verdict drafting

**Observation.** `config/governance/lo-file-safety.toml` permits LO writes to
exactly three surfaces: `memory/MEMORY.md`, `.gtkb-state/propose-drafts/**`, and
`.gtkb-state/owner-decisions/**`. Authoring a verdict requires staging body text
somewhere before handing it to the governed writer, and the only viable location
is `.gtkb-state/propose-drafts/**` - a surface whose name denotes Prime Builder
*proposal* drafts, not Loyal Opposition *verdict* drafts.

**Deficiency rationale.** Verdict drafts and proposal drafts are different
artifact classes with different authors and different lifecycles; commingling
them in one directory degrades the audit trail and makes per-class retention or
cleanup policy impossible to express. It also makes the allow-list read as
though LO is not expected to draft at all.

**Impact.** Low operationally, non-trivial for hygiene: this run deposited four
verdict bodies into a proposal-drafts directory because no verdict-drafts
directory is permitted.

**Proposed action.** Add `.gtkb-state/verdict-drafts/**` to `allow_patterns` and
point the verify skill at it. Small, additive, and removes a standing
class-confusion.

### [P4] A6 - The LO file-safety Bash heuristic over-matches on read-only commands

**Observation.** During this run the `GTKB-LO-FILE-SAFETY` PreToolUse hook
blocked read-only shell invocations, including a heredoc used to stage a
read-only analysis script (`unresolved or opaque shell mutation target`), and -
per a parallel review session - a `python -c` containing `encoding='utf-8'`
classified as a "shell mutation to 'utf-8'", and a `for f in bridge/*.md` loop
classified as an opaque mutation target.

**Deficiency rationale.** The mutation heuristic matches on command *text*
patterns rather than resolved targets, so read-only Python string literals and
shell loop variables trigger it. The gate is correctly fail-closed, so the cost
is friction rather than risk - but repeated false positives train agents to
route around the hook, which is the failure mode that matters.

**Proposed action.** Tighten the heuristic to ignore quoted-literal and
loop-variable contexts, or add an explicit read-only-invocation allowance for
`python -c` with no redirect. Low priority; capture for backlog rather than
immediate work.

### [P1] A7 - A bridge-only evidence carrier cannot be VERIFIED without fabricating test-command evidence

**Observation.** `.claude/hooks/bridge-compliance-gate.py:2131` hard-blocks any
`VERIFIED` verdict for which `_has_spec_derived_verification` is false
(`:1047-1052`). That predicate requires all three of: concrete Specification
Links, a spec-to-test heading, and `COMMAND_EVIDENCE_RE` (`:174-177`), which
matches only:

```
python -m pytest | pytest | ruff | npm test | pnpm test | uv run | make test
```

**Deficiency rationale.** Some bridge threads are legitimately **bridge-only
evidence carriers**: they mutate no source, test, or configuration byte, and
their `target_paths` contain only `bridge/*.md`. `gtkb-wi5661-hunk-provenance-bridge-evidence-carrier`
is exactly this shape - its declared `target_paths` is a single bridge file, and
its verification consists of git-provenance and preflight evidence, not test
execution. There is no test to run, because nothing testable changed.

For such a thread the gate is **unsatisfiable by honest means**. The reviewer's
only routes are (a) leave the thread permanently unverifiable, or (b) cite a
test-runner command that was not actually run for this change. Route (b) is
evidence fabrication and directly contradicts
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, the very specification the
gate cites as its authority.

**Evidence.** This run attempted the WI-5661 finalization three times. The first
two failures were genuine authoring gaps I corrected (a missing
`Recommended commit type:` token, then a missing `## Specification Links`
section). The third failed on this predicate with a fully compliant body: seven
concrete spec links, a seven-row spec-to-test mapping with `Executed: yes` on
every row, a `## Commands Executed` section recording the exact git and preflight
invocations run, and a clean applicability preflight. The verdict was not filed,
and the thread remains `REVISED`.

**Impact.** Bridge-only carriers - a pattern the protocol otherwise endorses, and
which `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` encourages via by-reference
composition - cannot reach terminal state. They accumulate as permanently
non-terminal threads, which is precisely the untracked-VERIFIED backlog condition
`.claude/rules/auto-finalization-sweep.md` exists to drain. The gate designed to
guarantee verification quality is, for this thread class, producing verification
deadlock and creating pressure toward fabricated evidence.

**Proposed action.** Extend `_has_spec_derived_verification` so that a verdict
whose reviewed report declares only `bridge/**` target paths satisfies the
command-evidence limb with governed non-test evidence - the applicability and
clause preflight invocations, plus `git show` / `git diff-tree` provenance
commands - rather than a test-runner token. Gate the exemption on the operative
report's declared `target_paths` being bridge-only, so it cannot be claimed by a
thread that touches source.

**Option rationale.** Preferred over adding the preflight scripts to
`COMMAND_EVIDENCE_RE`, which would let any thread satisfy the test-evidence limb
by running a preflight - materially weakening the gate for source-changing work.
Preferred over a per-thread owner waiver, which converts a recurring structural
mismatch into recurring owner toil, contrary to the Deterministic Services
Principle. The `target_paths`-conditioned exemption keeps the strong requirement
exactly where it earns its keep.

## Required Prime Builder Owner-Grilling Gate

### Implementation implied

**Yes** for A1, A2, A3, A4, and A5 - each requires source or configuration
changes. **No** for A6, which is a backlog-capture recommendation only.

### Grill-the-owner questions

Prime Builder must obtain durable `AskUserQuestion`-recorded answers to:

1. **Sequencing.** A1 (red finalization-atomicity suite) is the highest-value
   item and is already in the skill-rename sweep's natural scope. Should it be
   folded into an existing `WI-5662..WI-5668` sibling, or does the owner want a
   dedicated work item so it is not blocked behind the umbrella?
2. **A2 ownership.** Fixing the hash/append collision touches the verify
   helper - a governance-critical surface. Does the owner want the helper to
   own hash injection (recommended), or prefer the workaround documented in
   `.claude/rules/file-bridge-protocol.md` and the verify skill instead?
3. **A4 disposition.** Should the `.goose` helper copy be brought into parity
   and asserted by the fixture, or retired outright? These have different
   long-term maintenance costs and the answer depends on whether Goose is
   expected to hold a Loyal Opposition role in future.
4. **A5 scope.** Is a new `.gtkb-state/verdict-drafts/**` allow-list entry
   acceptable, or does the owner prefer LO verdict drafts remain commingled
   under `propose-drafts`?
5. **A7 remedy shape.** Should the VERIFIED command-evidence limb accept
   governed non-test evidence when the reviewed report's `target_paths` are
   bridge-only (recommended), or does the owner prefer bridge-only carriers be
   dispositioned by some other terminal route entirely - for example
   `WITHDRAWN` with recorded rationale - so the VERIFIED gate stays uniformly
   test-backed?

### Required durable owner decisions

Before any implementation proposal derived from this advisory is filed:

- A decision on A1 sequencing and work-item ownership.
- A decision on A2's remedy shape (helper-owned hash injection vs documentation).
- A disposition for the `.goose` helper copy.
- Approval (or rejection) of the new LO allow-list surface in A5.
- A decision on A7's remedy shape, since it governs whether bridge-only carriers
  can reach terminal VERIFIED at all.

## Prior Deliberations

- `DELIB-202667104` - LO Review: Cursor fallback and Goose manifest parity gaps.
  Directly adjacent; already dispositions the missing Goose manifest as ADOPT.
- `DELIB-202666065` - Loyal Opposition GO verdict, WI-5112 hunk-scoped VERIFIED
  finalization. Prior governance of the finalization transaction this advisory
  concerns.
- `DELIB-20265963` - WI-4750 implementation report, auto-retire verify-helper
  parity regression. Prior instance of the same helper-parity class as A4.
- `DELIB-202667193` and `DELIB-202667194` - GTKB Skill-Rename Reference Sweep
  owner decisions. Establish the sweep scope A1 and A3 belong to, and the
  exact-byte isolation constraint that prevents folding them into in-flight
  slices.
- `bridge/gtkb-lo-verified-finalization-interrupted-transaction-recovery-advisory-001.md`
  and `bridge/gtkb-lo-verify-helper-path-drift-and-verdict-concurrency-advisory-001.md`
  - existing advisories in this family; this advisory adds the red-suite (A1)
  and hash/append-collision (A2) findings, which those do not cover.

## Owner Decisions / Input

No owner decision has been made on any finding in this advisory. It is filed as
`ADVISORY` precisely so the owner-grilling gate above runs before any
implementation proposal exists. Per
`GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`, advisory capture is not
implementation approval and this document confers no authority to change source.

## Owner Action Required

None immediately. This advisory is Prime-Builder-actionable for interactive
disposition, not owner-blocking. The owner-grilling gate above is the point at
which owner input is required, and it is Prime Builder's responsibility to
initiate it.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
