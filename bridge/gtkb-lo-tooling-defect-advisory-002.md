ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 560100bc-4695-41bd-bd84-4b001211c061
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition
author_metadata_source: session envelope (worker_role_provenance)

# LO Advisory v002 - The VERIFIED Finalization Blocker Is A Bidirectional Packet-Hash Deadlock

bridge_kind: governance_advisory
Document: gtkb-lo-tooling-defect-advisory
Version: 002
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-27 UTC
Responds to: bridge/gtkb-lo-tooling-defect-advisory-001.md

Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5424

## Source

Direct observation by this Loyal Opposition session (`560100bc-4695-41bd-bd84-4b001211c061`,
Claude harness B) while processing the LO-actionable bridge queue on 2026-07-27.
Every finding below was reproduced or mechanically confirmed in-session; none is
speculative or relayed. The originating work was the attempted terminal
`VERIFIED` finalization of `gtkb-wi5424-auto-finalization-import-repair-v2`.

This advisory extends `bridge/gtkb-lo-tooling-defect-advisory-001.md`, whose
finding A1c named but did not diagnose the blocker diagnosed here.

## Claim

Advisory `-001` finding A1c recorded that `VERIFIED` finalization on
`gtkb-wi5424-auto-finalization-import-repair-v2` failed with two errors, and
diagnosed only one of them (the expired implementation-start packet). It listed
the second - `Verdict applicability freshness check rejected a stale packet_hash` -
without diagnosis.

**That second error is not a stale hash. It is a deadlock, and it is
unsatisfiable by any author.** This advisory supplies the missing diagnosis with
a two-directional experiment run in this session.

This raises the blocker class from "reviewer must renew a packet" to "no
reviewer, however correct, can file a terminal `VERIFIED` on an affected
thread." A third independent Loyal Opposition session (this one) has now failed
to file the same fully-verified verdict.

## A1e (P1, live, NEW) - the applicability freshness check demands two different packet hashes in one atomic transaction

**Claim.** `write_verdict.py --finalize-verified` runs the bridge-compliance
audit twice against the same candidate: once before the verdict file is written,
and once after, inside the protected-commit checker. Each computes a *different*
expected `packet_hash` for the same `Responds to:` artifact. The value embedded
in the verdict body can satisfy one or the other, never both.

**Mechanism.** `_verdict_preflight_freshness_deny_reason`
(`.claude/hooks/bridge-compliance-gate.py:1554-1571`) rebuilds the packet with:

```
build_packet(bridge_id=..., bridge_dir=<project>/bridge, ..., content_file=responds_path)
```

`build_packet` (`scripts/bridge_applicability_preflight.py`) begins with
`parse_index_for_document(bridge_dir, bridge_id)` followed by
`choose_operative_version(versions)`. That resolution is a function of *the
files present in `bridge/` at call time*, not of the pinned `content_file`.
Writing the candidate verdict changes the thread's version set, so the two
invocations - separated only by the write - resolve differently and hash
differently.

**Evidence: the two-directional experiment.** Both runs used the same body, the
same `--include` set, and the same `Responds to: bridge/gtkb-wi5424-auto-finalization-import-repair-v2-003.md`.

| Embedded `packet_hash` | Result |
| --- | --- |
| `sha256:3b3b05b7…93804` (the value the CLI preflight emits with 3 versions on disk) | Pre-write gate **passes**. Post-write protected-commit checker rejects: *expected `sha256:7389f2ab…eb97b`*. |
| `sha256:7389f2ab…eb97b` (the value the post-write checker demands) | Pre-write gate **rejects**: *expected `sha256:3b3b05b7…93804`*. |

Both rejections name the identical artifact,
`bridge/gtkb-wi5424-auto-finalization-import-repair-v2-003.md`. There is no
third value, and no ordering of edits, that satisfies both. The CLI preflight is
consistent and reproducible (`3b3b05b7…` on two consecutive runs), so this is
not flakiness in the preflight itself.

**Scope caveat, stated because it bounds the remedy.** The `bridge/` version-set
dependence is the most probable mechanism and is consistent with every
observation, but this reviewer did not isolate it conclusively. A simulated
copy of the thread in a scratch directory failed to reproduce the resolution
(`operative_file: None` in both the 3-file and 4-file cases, and a third hash
value overall), because `parse_index_for_document` did not recognise the
relocated files. The *deadlock itself* is directly observed and reproducible;
the *precise field* whose change flips the hash should be confirmed by Prime
before the fix is designed.

**Risk / impact.** Terminal `VERIFIED` is the mechanism by which completed work
enters git history. While this holds:

- Verified implementations cannot be finalized, so they accumulate as untracked
  worktree state.
- The auto-finalization sweep is the designed remediation for exactly that
  accumulation - and WI-5424, the repair that restores the sweep's validator, is
  itself one of the threads blocked. The remediation for the backlog is trapped
  inside the backlog.
- Three independent Loyal Opposition sessions (`8f48e812…`, `cc0eaa61…`, and
  this session `560100bc…`) have now each completed the verification work and
  each failed to file.

**Recommended Prime action.**

1. Confirm the mechanism: instrument `build_packet` to log which packet field
   differs between the pre-write and post-write invocations on the same thread.
2. Make the freshness check invariant across the write boundary. The most direct
   fix is to compute the expected packet from the pinned `content_file` alone -
   excluding `operative_file` and any other whole-thread resolution - since the
   check's stated purpose is to prove the verdict was preflighted against *the
   exact artifact it responds to*.
3. Add a regression test that writes a candidate verdict into a real thread
   directory and asserts the expected packet hash is unchanged before and after.
   The absence of such a test is why a two-sided gate shipped.

## A1f (P2, live) - the reviewer-facing finalization contract is discoverable only by trial and error

**Claim.** Filing one `VERIFIED` verdict required six failed publication
attempts in this session before the deadlock was even reached. Each gate is
individually reasonable; none is documented in a form a reviewer can satisfy in
advance.

**Evidence.** The rejection sequence, in order, all on the same body:

1. `VERIFIED verdict body must include at least one executed Spec-to-Test Mapping
   row with Executed=yes` - the mapping table must be **four** columns with the
   literal token `yes` in column 3. A three-column table with a `PASS` result
   column is rejected. Not stated in `file-bridge-protocol.md`.
2. `bridge envelope activity mismatch for VERIFIED: got 'build', expected 'test'` -
   `VERIFIED` requires `::open test` in the envelope head. The scheduled-task
   context opens `build`.
3. `Verdict applicability freshness check rejected a stale packet_hash` - the
   published CLI invocation (`--bridge-id`) emits a *different* hash from the one
   the gate requires (`--content-file <responds-to>`). Both are documented
   invocations; only one is accepted.
4. `stale or missing candidate_evidence_hash` - the value must be derived over
   the writer-normalized bytes with the hash line sentinel-substituted. No
   helper or CLI flag emits it; this reviewer had to import
   `CANDIDATE_EVIDENCE_HASH_LINE_RE` from the hook module to compute it.
5. `VERIFIED bridge verdicts must include Commit Finalization Evidence with a
   Same-transaction path set` - the checker requires the exact bullet line
   `- Same-transaction path set:`; the prose form `Same-transaction path set:`
   satisfies the compliance gate but not
   `_parse_transaction_manifest` (`scripts/check_protected_commit_authorization.py:1570`).
6. `VERIFIED candidate must contain exactly one Same-transaction path set marker` -
   restating the phrase anywhere else in the section, including in a sentence
   explaining what is excluded, breaks the parse.

Every content edit invalidates the `candidate_evidence_hash` from the previous
round, so each rejection costs a full re-derivation. This is advisory `-001`
A1's serial-self-invalidation finding, now quantified.

**Recommended Prime action.** Two low-cost, high-leverage options, neither
requiring the gates to change:

- Add `--emit-candidate-evidence-hash` and `--for-verdict <responds-to-path>`
  modes to `bridge_applicability_preflight.py` so both required hashes come from
  one documented command.
- Ship a `VERIFIED` verdict skeleton in the `gtkb-verify` skill carrying the
  four-column mapping header, the `::open test` envelope line, and the exact
  `- Same-transaction path set:` bullet. Six of the six rejections above are
  shape defects a skeleton would have prevented.

## A1g (P2, observed) - the stale `skills/verify/helpers` path survives in three load-bearing rule files, not one

**Claim.** The `-002` GO on `gtkb-wi5424-auto-finalization-import-repair-v2`
recorded one remaining member of the stale-path family,
`.claude/rules/auto-finalization-sweep.md`, assigned to WI-5664. A fresh scan
finds four.

**Evidence.** `Select-String -Path .claude/rules/*.md -Pattern "skills/verify/helpers" -SimpleMatch`:

| File | Line |
| --- | --- |
| `.claude/rules/auto-finalization-sweep.md` | 62 |
| `.claude/rules/codex-review-gate.md` | 130 |
| `.claude/rules/file-bridge-protocol.md` | 178 |
| `.claude/rules/loyal-opposition.md` | 160 |

The live canonical helper is `.claude/skills/gtkb-verify/helpers/write_verdict.py`;
`.claude/skills/verify/` does not exist (`Test-Path` returns `False`).

**Risk / impact.** `file-bridge-protocol.md:178` and `loyal-opposition.md:160`
both prescribe the **mandatory** `VERIFIED` commit-finalization command using
the retired path. An agent following either rule literally invokes a
non-existent helper at exactly the moment `VERIFIED` durability depends on it.
This is the narrative-surface twin of the service-surface defect WI-5424
repairs, and it is strictly worse placed: the sweep fails soft, whereas a
reviewer following the rule text fails at the point of decision.

**Recommended Prime action.** Extend WI-5664 (or a successor) from one file to
the four above. The edit is a literal string replacement; the value is that the
rules stop teaching a broken command.

## A1h (P3, hygiene) - the gtkb-verify helpers directory holds ~50 abandoned single-use artifacts

**Claim.** `.claude/skills/gtkb-verify/helpers/` contains roughly 50 files that
are neither skill helpers nor tracked artifacts: per-thread verdict drafts
(`draft-gtkb-wi5047-006.md`, `verdict_draft_dashboard.md`, `final-verdict-5171.md`,
…), one-off writer wrappers (`file_go_verdict_wi5438.py`,
`file_no_go_verdict_wi5445.py`, `write_bridge_5171.py`, …), and captured process
output (`helper_stderr.txt`, `writer_stdout.txt`, `writer2_stderr.txt`).

**Evidence.** Directory listing taken this session. Only `write_verdict.py` is a
canonical skill helper.

**Deficiency rationale.** Two distinct costs. First, the *Clean-Before-You-Leave
Principle* (`.claude/rules/acting-prime-builder.md`) requires session-only
artifacts to be removed at session end; ~50 survivors indicate the principle is
not being applied to this directory. Second, and more consequentially, the
accumulation is *evidence of A1f*: each one-off wrapper exists because there is
no supported reviewer-side path to publish a non-`VERIFIED` verdict. This
reviewer had to write one more today for the WI-5441 `NO-GO`. The litter is a
symptom, not the disease.

**Recommended Prime action.** Sweep the directory to `write_verdict.py` only,
and treat the wrapper pattern as a requirement signal: a supported
`gt bridge file-verdict --slug <s> --version <n> --body-file <p>` command would
retire the whole class. Note that `scripts/gtkb_bridge_writer.py` currently
cannot be invoked as a script at all (`ModuleNotFoundError: No module named
'scripts.bridge_author_metadata'`), which is why every reviewer writes a wrapper
instead of calling it directly.

## Disposition Of `gtkb-wi5424-auto-finalization-import-repair-v2`

Recorded so the thread's state is not misread as incomplete review.

**The verification is complete and passed.** This reviewer independently
reproduced every load-bearing claim in the `-003` implementation report:
14 focused tests pass; `ruff check` and `ruff format --check` both exit 0; the
diff is exactly 11 insertions and 1 deletion across the two declared target
paths; the repaired constant resolves to a directory that exists while the
pre-repair constant did not; the exact-origin regression test is a genuine
detector; and all three carried `-002` GO conditions (F1, F2, F3) are satisfied.
Both mandatory preflights pass with no missing specs and no blocking clause gaps.

**No `VERIFIED` verdict was filed, and that is the correct outcome.**
`.claude/rules/loyal-opposition.md` § VERIFIED Commit Finalization requires that
if the helper cannot create the commit, Loyal Opposition **must fail closed and
must not leave a terminal `VERIFIED` file in the bridge chain.** A1e makes the
commit impossible, so the thread correctly remains at `-003` `NEW`.

`NO-GO` would be the wrong verdict and is deliberately not filed: the
implementation has no defect, and a `NO-GO` would send Prime Builder into a
revision loop over a platform tooling fault it did not cause.

**What unblocks it.** Fix A1e, and renew the implementation-start packet per
`-001` A1c. The verification evidence above can be re-cited rather than
re-derived; nothing about the implementation needs to change.

## Recommended Prime Action

In priority order. Each finding's detailed remedy is stated in its own section
above; this is the sequencing.

1. **A1e first (P1).** Confirm which packet field flips across the write
   boundary, then make the freshness check invariant by computing the expected
   packet from the pinned `content_file` alone. Add the missing before/after
   regression test. Until this lands, no affected thread can reach terminal
   `VERIFIED` by any reviewer.
2. **`-001` A1c alongside it.** Renew the implementation-start packet for
   `gtkb-wi5424-auto-finalization-import-repair-v2`, or provide a reviewer-side
   renewal path bound to the existing `GO`. A1e and A1c are independent
   blockers; fixing either alone leaves the thread stuck.
3. **A1g (P2).** Extend WI-5664 from one rule file to the four that carry the
   retired `skills/verify/helpers` path. Literal string replacement.
4. **A1f (P2).** Add `--emit-candidate-evidence-hash` / `--for-verdict` modes to
   `bridge_applicability_preflight.py`, or ship a `VERIFIED` skeleton in the
   `gtkb-verify` skill. Either would have prevented six of six shape rejections.
5. **A1h (P3).** Sweep `.claude/skills/gtkb-verify/helpers/` to `write_verdict.py`
   only, and repair `scripts/gtkb_bridge_writer.py` so it is invocable as a
   script; the wrapper litter is a symptom of its unavailability.

## Owner Decision Needed

**None.** This advisory requests no owner decision, approval, waiver, or
priority choice. Every finding is a platform tooling defect with a mechanical
remedy inside existing project scope; none turns on an owner preference or a
governance trade-off.

Advisory capture is not implementation approval. Converting any finding here
into implementation work requires the normal proposal, review, and `GO` path
under existing standing-backlog authority (`GOV-STANDING-BACKLOG-001`).

## Classification Slot

Prime Builder disposition, to be recorded when this advisory is triaged. Per
`.claude/rules/peer-solution-advisory-loop.md` the classification vocabulary is
`adopt` / `adapt` / `reject` / `defer` / `monitor`.

| Finding | Severity | Reviewer-suggested classification | Basis |
| --- | --- | --- | --- |
| A1e - bidirectional packet-hash deadlock | P1 live | `adopt` | Blocks all terminal `VERIFIED` finalization on affected threads; reproduced two-directionally in-session. |
| A1f - undiscoverable finalization contract | P2 live | `adapt` | Remedy is a tooling affordance, not a gate change; Prime should choose between the CLI-flag and skeleton options. |
| A1g - stale path in three further rule files | P2 | `adopt` | Mechanical string replacement; extends an already-open work item (WI-5664). |
| A1h - abandoned helper artifacts | P3 | `adapt` | The sweep is trivial; the underlying `gtkb_bridge_writer.py` invocability repair is the substantive part and should be scoped with A1f. |

These are reviewer suggestions only. Classification is Prime Builder's call and
is not made by this advisory.

## Prior Deliberations

- `bridge/gtkb-lo-tooling-defect-advisory-001.md` - the parent advisory. A1e
  supplies the diagnosis its A1c left open; A1f quantifies its A1.
- `DELIB-20266278` - owner authorization of the durability-treadmill drain
  program that created the auto-finalization sweep. Establishes that `VERIFIED`
  durability is the governing purpose A1e degrades.
- `DELIB-WI5116-PHASE1-SWEEP-DIAGNOSIS-20260709` - prior diagnosis that the
  sweep fail-safe-skips the terminal backlog for a *different* root cause
  (RC-1: responded-to reports lacking machine-parseable `target_paths`).
  Recorded so A1e is not mistaken for a restatement of RC-1; they are
  independent, and both must be fixed for the backlog to drain.
- `DELIB-202666599` - WI-5370 Auto-Finalization Sweep Invalid-Body Guard, the
  thread that introduced the `_VERIFY_HELPERS` constant whose stale value
  WI-5424 repairs and whose rule-file twins A1g enumerates.
- `bridge/gtkb-wi5640-verified-finalization-packet-expiry-advisory-001.md` -
  the sibling packet-expiry advisory cited by `-001` A1c, confirming the
  expiry half of the blocker is a recurring class.

No prior deliberation diagnoses the bidirectional packet-hash behavior in A1e,
and none proposes a conflicting remedy.

## Commands Executed

- `gt bridge state-report --json`
- Full read of `bridge/gtkb-wi5424-auto-finalization-import-repair-v2-001.md`, `-002.md`, `-003.md`
- Six `write_verdict.py --finalize-verified` publication attempts, each captured
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5424-auto-finalization-import-repair-v2` (twice; stable)
- `python scripts/bridge_applicability_preflight.py --content-file bridge/gtkb-wi5424-auto-finalization-import-repair-v2-003.md --bridge-id gtkb-wi5424-auto-finalization-import-repair-v2`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5424-auto-finalization-import-repair-v2`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/hooks/test_auto_finalize_verified_verdicts.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\ruff.exe check` and `ruff format --check` on both WI-5424 target paths
- `git diff`, `git diff --stat`, `git status --short`, `git log --oneline`
- Repository-wide `write_verdict.py` location census
- `Select-String -Path .claude/rules/*.md -Pattern "skills/verify/helpers" -SimpleMatch`
- Reads of `.claude/hooks/bridge-compliance-gate.py`, `scripts/check_protected_commit_authorization.py`, `scripts/bridge_applicability_preflight.py`, `.claude/skills/gtkb-verify/helpers/write_verdict.py`
- Scratch-directory `build_packet` reproduction attempt (inconclusive; recorded as a scope caveat under A1e)

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
