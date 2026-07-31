ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 84f97bc5-39a5-4126-bfa9-5afd34d25a63
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled loyal-opposition-worker; transcript-resolved Loyal Opposition role; test activity
author_metadata_source: session envelope (worker_role_provenance)

# VERIFIED Finalization Invocation Drift, Stale Repository Lock, and Missing Terminal-State Assertion

bridge_kind: governance_advisory
Document: gtkb-lo-finalization-invocation-drift-and-stale-lock-advisory
Version: 001
Author: loyal-opposition/claude (harness B, session 84f97bc5-39a5-4126-bfa9-5afd34d25a63)
Date: 2026-07-29 UTC

## Source

Discovered while processing six Loyal Opposition-actionable bridge items in a
single scheduled review run on 2026-07-29. None of the findings below is
attributable to any of the six reports reviewed, and none was held against them.
They are recorded here for governed Prime Builder intake.

Threads that surfaced the evidence:

- `bridge/gtkb-wi5661-hunk-provenance-bridge-evidence-carrier-010.md` (VERIFIED)
  - findings F2 and F3 in that verdict.
- `bridge/gtkb-wi5688-terminal-finalization-recovery-002.md` (NO-GO) - findings
  F4 and F5, and the mechanism determination section.
- `bridge/gtkb-wi5664-config-baseline-capture-quarantine-002.md` (NO-GO) -
  finding F5.

## Claim

Six defects in the VERIFIED-finalization surface and its surrounding tooling.
Together they explain a recurring incident class, terminal `VERIFIED` bridge
state with no accompanying commit, that has now consumed at least four separate
work items (WI-4682, WI-4723, WI-5345, WI-5688) without the root cause being
named.

### C1 - P1: the documented finalization command points at a path that does not exist

`.claude/skills/verify/` does not exist in this checkout. The live helper is at
`.claude/skills/gtkb-verify/helpers/write_verdict.py`. The nonexistent path is
prescribed by four canonical rule surfaces:

- `.claude/rules/file-bridge-protocol.md` line 178
- `.claude/rules/loyal-opposition.md` line 160
- `.claude/rules/codex-review-gate.md` line 130
- `.claude/rules/auto-finalization-sweep.md` line 62

It is also emitted by the helper's own evidence generator at
`write_verdict.py` line 1009, so every helper-generated Commit Finalization
Evidence block advertises a path that cannot be invoked. At least one one-off
wrapper, `.claude/skills/gtkb-verify/helpers/file_no_go_verdict_wi5445.py`
line 26, resolves a body path through the same stale directory.

Impact: a reviewer following the documented command verbatim gets a
file-not-found. The nearest wrong turn from there is to hand-author the terminal
verdict, which is exactly the artifact class WI-5688 is quarantining. This is the
most economical explanation for hand-authored terminal verdicts appearing in the
chain.

Evidence that this actually happened at least once:
`bridge/gtkb-wi5688-doctor-crash-fastlane-006.md` line 257 carries a Commit
Finalization Evidence block whose helper path is `gtkb-verify`, whereas the
generator emits `verify`. The generator is a no-op when the section already
exists, so it cannot have produced that text. The section was hand-authored, and
the whole fastlane chain is untracked with no commit in history.

### C2 - P1: a stale repository lock silently blocks all finalization, with no detector

During this run the finalizer failed with
`fatal: Unable to create 'E:/GT-KB/.git/index.lock': File exists` after its five
bounded retries. Inspection found a zero-byte `.git/index.lock` created at
`2026-07-29T13:14:57Z` with no `git` process alive, roughly two hours and
forty-seven minutes stale, predating the reviewer session that hit it.

Every finalization attempt repository-wide would have failed for that entire
window. Nothing surfaced the condition. There is no doctor check for a stale
`.git/index.lock`, and the failure is only visible to whoever happens to attempt
a finalization and read a stack trace.

The good news, and it should be recorded plainly: integrity held. On that
failure the helper wrote no terminal verdict, moved no HEAD, and left the chain
untracked. Fail-closed behaved exactly as specified. After the stale lock was
cleared under standing bridge-repair authority, the same invocation produced a
clean atomic commit, `e9052e9c4`. The defect is availability, not integrity.

### C3 - P2: no machine-checkable assertion that a terminal VERIFIED has a commit

The Mandatory VERIFIED Commit-Finalization Gate is rule-authority text only. A
MemBase query for finalization or commit-gate specifications returns one row,
`SPEC-DSI-COMMIT-GATE-001` at status `specified`, and no
`DCL-VERIFIED-FINALIZATION-*` design constraint exists.

Consequence: a hand-authored terminal `VERIFIED` satisfies every mechanical
bridge gate, because no gate asserts that a terminal verdict is accompanied by a
commit containing it. The untracked-terminal durability guard detects the
condition after the fact; nothing prevents authoring it. C1 supplies the motive
and C3 supplies the opportunity.

### C4 - P2: the two code branches that can retain a terminal file are both untested

`platform_tests/skills/test_verified_finalization_validation_hardening.py`
covers fail-closed on an untracked predecessor chain and asserts no verdict is
left behind. It does not cover:

- `write_verdict.py` lines 1231 to 1249, where the commit succeeded but a
  subsequent HEAD rollback failed and the verdict is deliberately retained for
  diagnosis; and
- `scripts/gtkb_bridge_writer.py` lines 987 to 993, where a lost pending
  publication context retains the file rather than deleting it.

These are the only paths that can leave a terminal file without matching clean
state, and neither has regression coverage.

### C5 - P2: no first-class publish surface for GO and NO-GO verdicts

`--finalize-verified` covers VERIFIED. There is no equivalent CLI for GO or
NO-GO. Reviewers hand-roll per-thread wrapper scripts, and nine have accumulated
in `.claude/skills/gtkb-verify/helpers/`: `file_go_verdict_wi5438.py`,
`file_go_verdict_wi5518.py`, `file_no_go_verdict_wi5343.py`,
`file_no_go_verdict_wi5445.py`, `write_bridge_5171.py`,
`write_bridge_gtkb_retire_ipa_refs_006.py`, `write_bridge_wi5555_wi5556_002.py`,
`writer_script.py`, and `write_verdict.py`.

Each is a per-incident copy of the same three-line call to `write_bridge_file`.
They are untested, they drift (one already carries the C1 stale path), and they
accumulate permanently in a governed skill directory. This is a deterministic
services candidate: the substantive reviewer contribution is the verdict body,
not the plumbing.

### C6 - P2: candidate_evidence_hash has no forward computation path

Every GO, NO-GO, and VERIFIED verdict must embed a `candidate_evidence_hash`
computed over the final normalized candidate bytes with the hash line itself
sentinel-substituted. No tool emits it. `bridge_applicability_preflight.py` does
not compute it, and there is no flag that does.

The only available workflow is to submit a verdict with a wrong hash, read the
expected value out of the rejection message, paste it back, and resubmit. Worse,
because the hash covers the whole body, any subsequent edit invalidates it and
forces another deliberate-failure round trip. This run required four such cycles
on a single verdict.

The check itself is sound and worth keeping; it binds the verdict to its exact
content. What is missing is a way to satisfy it without provoking an error.

## Owner Decision Needed

None to record this advisory. Two decisions arise only if Prime Builder converts
it:

1. Scope. C1 and C2 are cheap and independently valuable. C3, C4, C5, and C6 are
   larger and could be a small project rather than one work item. The owner
   should choose whether to take the pair now and defer the rest, or scope the
   whole set together.
2. C1 touches four protected `.claude/rules/*.md` narrative surfaces, so it needs
   formal-artifact approval packets per `GOV-ARTIFACT-APPROVAL-001` regardless of
   how the rest is scoped.

## Recommended Prime Action

File a normal implementation proposal covering at least C1 and C2, after the
owner-grilling gate below. Suggested shape:

- C1: correct the helper path in the four rule surfaces, in `write_verdict.py`
  line 1009, and in the affected wrapper. Add a deterministic check that every
  documented helper path in `.claude/rules/*.md` resolves on disk, so this class
  cannot silently recur.
- C2: add a doctor check for a stale `.git/index.lock`, defined as lock present
  with no live `git` process beyond a threshold age. Report it at startup rather
  than leaving discovery to whoever next attempts a finalization.
- C3: promote the commit-finalization gate to a DCL with a machine-checkable
  assertion binding terminal `VERIFIED` to a commit containing it.
- C4: add regression coverage for the two retention branches.
- C5: replace the one-off wrappers with a single governed
  `gt bridge publish-verdict` surface, then retire the nine accumulated scripts.
- C6: add a `--emit-candidate-evidence-hash` mode, or have the verdict helper
  compute and inject the hash before submission.

Do not treat this advisory as implementation approval. It is future-work
initiation only.

## Required Prime Builder Owner-Grilling Gate

### Implementation implied

Yes. C1 modifies four protected narrative surfaces plus helper source. C2 adds a
doctor check. C3 creates a new DCL. C4 adds tests. C5 adds a CLI surface and
retires nine files. C6 adds a helper mode.

### Grill-the-owner questions

Prime Builder must obtain durable `AskUserQuestion` answers to:

1. Scope split. Take C1 and C2 now as a bounded reliability fix, or scope all six
   as a project? C1 and C2 alone plausibly close the recurring incident class.
2. C5 retirement policy. Should the nine one-off wrapper scripts be deleted once
   a governed publish surface exists, or retained as historical provenance? They
   sit in a governed skill directory and the removal rule requires explicit owner
   approval.
3. C3 enforcement mode. Should the new terminal-state DCL be advisory first, or
   blocking immediately? Blocking immediately will fail closed on any existing
   hand-authored terminal verdict still in the chain, which may require a sweep
   before it can be turned on.

### Required durable owner decisions

Before any derived implementation proposal is filed:

- the scope decision from question 1;
- the retirement disposition from question 2, since it is a removal;
- the enforcement mode and sequencing from question 3.

## Classification Slot

`adopt`.

The findings are concrete, independently reproducible, and inside GT-KB's own
reliability surface. C1 and C2 in particular are cheap, low-risk, and address a
class that has already consumed four work items. Recommended disposition is
adopt, with the scope split left to the owner per the gate above.

## Evidence Commands

```text
Test-Path .claude\skills\verify
Test-Path .claude\skills\gtkb-verify\helpers\write_verdict.py
Select-String -Path .claude\rules\*.md -Pattern 'skills/verify/helpers/write_verdict' -SimpleMatch
Select-String -Path .claude\skills\gtkb-verify\helpers\write_verdict.py -Pattern 'Finalization helper:'
Select-String -Path bridge\gtkb-wi5688-doctor-crash-fastlane-006.md -Pattern 'write_verdict.py'
git status --porcelain -- bridge/gtkb-wi5688-doctor-crash-fastlane-*.md
Get-Item .git\index.lock
Get-Process -Name git
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/skills/test_verified_finalization_validation_hardening.py platform_tests/scripts/test_bridge_lifecycle_resolver.py -q
```

The pytest run reported 81 passed with one pre-existing
`PytestConfigWarning: Unknown config option: asyncio_mode`.

## Owner Action Required

None to record this advisory. See Owner Decision Needed for the decisions that
arise on conversion.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
