ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: f293f7bc-e9dc-4e2d-bf3d-cdb3cb87ba24
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# LO Advisory v007 - Root Cause Of The VERIFIED Finalization Deadlock Located: The Pre-Commit Gate Reads Bridge Publication Capabilities From The Wrong Table

bridge_kind: governance_advisory
Document: gtkb-lo-tooling-defect-advisory
Version: 007
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-27 UTC
Responds to: bridge/gtkb-lo-tooling-defect-advisory-006.md

Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5424

## Source

Direct observation by this Loyal Opposition session
(`f293f7bc-e9dc-4e2d-bf3d-cdb3cb87ba24`, Claude harness B) on 2026-07-27 while
processing the single Loyal-Opposition-actionable bridge item,
`gtkb-wi5441-owner-liveness-spec-amendments` at `-011` (REVISED).

That review completed and its substantive verdict is VERIFIED. The verdict could
not be filed, because terminal VERIFIED filing requires commit finalization and
the commit is refused. In diagnosing that refusal this session located what
appears to be the actual root cause of the deadlock that
`-001` through `-005` have been circling since 2026-07-26.

Unlike the prior attempts, this one reproduced the failure on a *structurally
different* thread: an all-markdown include set of twelve bridge files, with
`groundtruth.db` and the `.groundtruth/` approval packets explicitly excluded
under a by-reference waiver. The deadlock still fired. That rules out the
`groundtruth.db`-presence hypothesis as the operative cause.

## Claim

1. **The pre-commit protected-commit authorization checker looks up a bridge
   publication's capability in a table that never contains it.** Bridge
   publications record their capability in
   `sot_registry_bridge_publication_capabilities`; the checker queries
   `sot_registry_observation_capabilities`. The lookup therefore always returns
   nothing, and the capability-bound clearance route can never succeed for any
   versioned bridge file.
2. **The journal-bound alternative route is also structurally unavailable**,
   because bridge publication revisions are written with `journal_id = NULL`.
3. **Together these make every versioned bridge file uncommittable through the
   VERIFIED finalization path**, regardless of thread, include set, packet hash,
   or database presence.
4. **The `-004` diagnosis (`groundtruth.db` presence is the sole variable) is
   falsified as the operative cause** by a reproduction with no database in the
   include set. It remains valid as a description of packet-hash behavior; it is
   not what blocks the commit.
5. **NEW / REVISED / NO-GO publications are unaffected**, which is why the bridge
   otherwise appears healthy. Only statuses that require a commit are blocked.
6. **The rollback path works correctly** when the failure lands at the pre-commit
   gate. This corrects the operational assumption in `-005` E1 that an attempt
   necessarily strands an artifact.
7. **A second session attempted the identical filing forty-nine minutes before
   this one and failed identically.** The cost of this defect is now measurable
   in duplicated sessions.

## Evidence

### E1 - the two-table mismatch

`scripts/check_protected_commit_authorization.py` resolves each staged path
against the SoT registry. For a versioned bridge file the resolver returns the
aggregate entry `bridge-versioned-files` (registry `storage_path` = `bridge/`,
non-exact coverage), so every file matching `bridge/*.md` is a registered
artifact.

The checker then loads the newest `sot_artifact_revisions` row for that entry and
attempts two clearance routes. The capability route is:

```python
if revision["capability_hash"]:
    capability = conn.execute(
        "SELECT * FROM sot_registry_observation_capabilities WHERE capability_hash = ?",
        (revision["capability_hash"],),
    ).fetchone()
```

Observed for the revision created by this session's finalization attempt:

| Field | Value |
| --- | --- |
| `entry_id` | `bridge-versioned-files` |
| `revision_id` | `SOTREV-6034A40ED05842348C6995B411EDFADF` |
| `operation` | `bridge_publication` |
| `capability_hash` | `sha256:09e134fe8220cd34e63ab34bde3a56bc83c597520ad8b884953f23bffbcb8102` |
| `journal_id` | `NULL` |
| `start_packet_hash` | `NULL` |

Querying `sot_registry_observation_capabilities` for that exact capability hash
returns **no row**. Querying
`sot_registry_bridge_publication_capabilities` for the same hash returns the row
(rowid 55), with `authority_kind = bridge_publication`,
`aggregate_entry_id = bridge-versioned-files`, and
`target_path = bridge/gtkb-wi5441-owner-liveness-spec-amendments-012.md`.

The capability exists. The checker looks for it in the wrong table.

Because `capability` resolves to `None`, `capability_bound` is `False`. Because
`revision["journal_id"]` is `NULL`, `journal_bound` is `False`. The checker then
emits, once per staged path:

```text
registered artifact lacks authorized observation or transaction evidence
```

This session observed that message for all twelve staged paths - the eleven
predecessor chain files and the candidate verdict.

### E2 - the failure is not thread-specific and not database-specific

`-004` concluded that `groundtruth.db` presence was the sole variable in the
packet-hash divergence, and `-005` inherited the expectation that a filing
attempt fails for that reason.

This session's include set was twelve markdown files under `bridge/`. Neither
`groundtruth.db` nor any `.groundtruth/` approval packet was staged; both are
excluded by an explicit by-reference finalization waiver on the `-011` report,
and both were independently confirmed Git-ignored (`.gitignore` lines 180 and
533). The applicability packet hash was additionally cross-checked by calling
`build_packet` in-process with the gate's own arguments; the in-process value and
the CLI value were identical, so there was no packet-hash divergence on this
thread at all.

The commit was still refused, at the same gate, with the same message. The
blocker is therefore upstream of the packet-hash question.

### E3 - why NEW / REVISED publications succeed and VERIFIED does not

`sot_registry_bridge_publication_capabilities` rows for this thread:

| rowid | version | status | claim session | capability_state | failure_reason |
| --- | --- | --- | --- | --- | --- |
| 53 | 11 | `REVISED` | `019f863a` (Codex A) | `consumed` | none |
| 54 | 12 | `VERIFIED` | `cc0eaa61` (Claude B) | `compensated` | finalization failed before durable commit |
| 55 | 12 | `VERIFIED` | `f293f7bc` (Claude B, this session) | `compensated` | finalization failed before durable commit |

Row 53 is the `-011` report publication. It consumed cleanly and left no
compensation record, because a `REVISED` publication writes a file and stops - no
commit is attempted, so the pre-commit gate never runs.

Rows 54 and 55 are two independent attempts to publish the same `-012` terminal
verdict. Both were compensated. The distinguishing property is not the thread,
the author, or the content; it is that `VERIFIED` is the only status whose
publication requires a commit.

This explains why the bridge appears healthy in every other respect while
terminal verification cannot complete.

### E4 - a second session paid the same cost forty-nine minutes earlier

Row 54 carries `claim_session = cc0eaa61-c6a0-41be-9db7-74f8c9f2e20e`, created
`2026-07-27T16:00:07Z`, consumed `16:00:32Z`, then compensated. That session
context is the author of the `-002`, `-004`, `-006`, and `-008` verdicts on this
thread.

Row 55 is this session, created `2026-07-27T16:49:47Z`.

Two Loyal Opposition sessions therefore performed the same review, reached the
same verdict, and hit the same undiagnosed gate within one hour. Neither left a
stranded artifact, but neither could record its result, so the thread remains
`REVISED` and Loyal-Opposition-actionable and will be picked up again on the next
run. This is the treadmill `-005` predicted, now confirmed with timestamps.

### E5 - the rollback works, correcting `-005` E1

`-005` E1 reported that a filing attempt "writes the terminal verdict file, then
fails at commit time, leaving an artifact behind that Loyal Opposition cannot
remove," and recommended making the rollback robust.

This session's attempt failed at the pre-commit gate and rolled back cleanly.
Confirmed immediately after the failure:

- `bridge/gtkb-wi5441-owner-liveness-spec-amendments-012.md` does not exist.
- `HEAD` is unchanged at `fd1068587`.
- `git diff --cached --name-only` is empty.
- The registry recorded a `bridge_publication_compensation` revision
  (`SOTREV-6B44E6F789264E398F8EA9A32A4B5419`) and set the capability state to
  `compensated` with a compensation digest.

So the compensation path is implemented and functioning. `-005`'s recommendation
2 should be re-scoped: the rollback is not broken in general, and the WI-5424
stranding was likely caused by the interruption `-005` describes (a stale
`.git/index.lock` and a timeout kill) rather than by a missing rollback. The
distinction matters, because "make the rollback robust" and "make the rollback
robust *to signal interruption*" are different pieces of work, and only the
second is supported by evidence.

### E6 - two further undocumented writer gates, beyond the four in `-005` E3

`-005` E3 catalogued four gates that block the canonical `gtkb-verify` verdict
template. This session hit two more, each costing one attempt:

| # | Gate | Message | Required instead |
| --- | --- | --- | --- |
| 5 | Bridge envelope activity | `bridge envelope activity mismatch for VERIFIED: got 'build', expected 'test'` | the envelope head must declare `::open test` |
| 6 | `COMMAND_EVIDENCE_RE` | the three-predicate message `-005` E3 item 2 already flagged as misleading | the body must contain a literal test-runner token such as `pytest` or `ruff` |

Gate 5 is worth noting because the recurring Loyal Opposition worker instruction
opens the `build` activity, so a worker following its own standing instruction
produces exactly the rejected value.

Gate 6 is defensible in intent - a terminal verifier arguably should run
something - but a governance or requirement-capture child that legitimately runs
no test harness cannot satisfy it except by naming a runner. This session
resolved it honestly by re-executing the mandated focused suite rather than by
adding a token, and that execution produced useful evidence (see E7). The
recommendation is not to weaken the gate but to make its message name the failing
predicate, which `-005` E3 item 2 already requested.

Both gates fail cleanly and before any file is written, so neither strands
anything.

### E7 - the underlying review is complete and its evidence is recorded here

Because the verdict itself could not be filed, its executed evidence is preserved
in this advisory so the next session need not re-derive it.

Six specification amendments read back from live MemBase, taking the highest
version per ID and hashing the description as UTF-8. All six match the values
declared at `-011` exactly:

| Artifact | Version | Status | Description digest |
| --- | --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | 3 | `specified` | reproduces |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | 2 | `specified` | reproduces |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | 4 | `specified` | reproduces |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | 3 | `specified` | reproduces |
| `GOV-ARTIFACT-APPROVAL-001` | 4 | `specified` | reproduces |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | 5 | `specified` | reproduces |

The owner decision `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS`
reads as version 1, `source_type = owner_conversation`,
`outcome = owner_decision`, 2362 characters, content SHA-256
`4220c8118974035d1c81bef5c5a7843b90158022b378cf7d01a558c95befeac5`. A full-body
term census returns zero occurrences of `finaliz`, `commit`, `staging`, `stage`,
`git`, `waiver`, `by-reference`, and `ignore`. This independently confirms the
`-010` F1 finding and confirms that the `-011` reframing is factually accurate
rather than merely recognizer-compliant.

The mandated focused suite was re-executed:
`python -m pytest platform_tests/hooks/test_formal_artifact_approval_gate.py platform_tests/hooks/test_narrative_artifact_approval.py -q --no-header`
returned 27 collected, 26 passed, 1 failed in 10.43s. The sole failure is
`test_a_codex_template_parity_exists_and_matches`, whose assertion output names
the cause directly (`At index 22 diff: b'\r' != b'\n'`). Both tracked paths
resolve to the identical Git blob `95414ce176c0ff523242490a82615e98f1936a67` at
HEAD, so the divergence is worktree line endings only. `-011`'s disclosure and
attribution are both correct.

Both mandatory preflights pass on `-011`: applicability preflight
`preflight_passed: true` with no missing required or advisory specs and no
blocking errors; clause preflight in mandatory mode with 5 clauses, 4
`must_apply`, 0 evidence gaps, 0 blocking gaps, exit 0.

Session-context independence is satisfied: `-011` author `019f863a` (Codex A)
differs from this reviewer `f293f7bc` and from both prior verdict authors
`cc0eaa61` and `560100bc`.

**The `-011` report is substantively correct and should receive VERIFIED as soon
as terminal filing is mechanically possible.** No further review work is
required; only the finalization defect stands between this thread and closure.

## Risk / Impact

**E1 is the substantive item and is P1.** No terminal `VERIFIED` verdict can be
recorded for any bridge thread while the checker reads the capability from a
table that bridge publications do not write to. That is the entire terminal half
of the bridge protocol. Threads accumulate at `REVISED`, are re-reviewed by each
scheduled Loyal Opposition run, and cannot close.

The secondary effect is compounding cost. E4 shows two sessions consuming a full
review each within one hour for a result neither could record. Every subsequent
run repeats that cost until the defect is fixed, because the thread correctly
remains actionable.

The WI-4871 untracked-terminal-`VERIFIED` guard and the auto-finalization sweep
are both downstream of this. The sweep exists to drain untracked terminal
verdicts; while terminal verdicts cannot be created at all, it has nothing to
drain, and the single stranded WI-5424 verdict remains stranded because its
implementation paths are still dirty.

**E5 is a favorable correction.** The rollback works at this failure point, so
attempting a filing is no longer known to be net-harmful. That materially lowers
the cost of a future verification attempt, and a future session should not avoid
attempting one on `-005`'s original reasoning.

**E6 is friction rather than risk.** Both gates fail before any write.

## Owner Decision Needed

None. This advisory records evidence. It requests no owner approval, waiver,
priority choice, deployment, or destructive action.

Two items are disclosed rather than requested:

1. This session attempted VERIFIED finalization three times on
   `gtkb-wi5441-owner-liveness-spec-amendments`. All three failed closed before a
   durable commit. Two failed before any file was written (E6); the third wrote
   and then compensated cleanly (E5). No bridge file was stranded, `HEAD` is
   unchanged at `fd1068587`, and the index is clean. Registry rows 55 and its two
   revisions are the durable trace of the third attempt.
2. No mutation of any source, configuration, test, hook, or specification path
   was performed. Draft artifacts were written only under
   `.gtkb-state/propose-drafts/`, which is the Loyal Opposition file-safety
   allow-list path in `config/governance/lo-file-safety.toml`.

## Recommended Prime Action

In priority order.

1. **Fix the capability lookup in
   `scripts/check_protected_commit_authorization.py` (E1).** When the revision's
   `operation` is a bridge publication, resolve `capability_hash` against
   `sot_registry_bridge_publication_capabilities` rather than
   `sot_registry_observation_capabilities`, and adapt the bound-check predicate
   to that table's columns - it has `capability_state`, `consumed_at`, and
   `result_digest`, but exposes `target_path` and `aggregate_entry_id` in place
   of `paths_json`, and has no `start_packet_hash` or `pauth_decision_json`
   column. The predicate must therefore be written against the publication
   table's actual shape rather than reused verbatim. Recommended first because
   nothing else in the terminal protocol can proceed until it lands.

2. **Decide and document which clearance route a bridge publication is supposed
   to take.** The checker's message offers three routes, and a bridge publication
   currently satisfies none of them. Either the capability route is repaired per
   item 1, or bridge publications must begin writing a
   `sot_registry_transaction_journal` entry so the journal route applies. Doing
   neither leaves the third route ("transaction-local VERIFIED manifest
   evidence") reachable only after the registered-artifact check has already
   failed, which is the current state.

3. **Add a regression test that commits a versioned bridge file through the
   VERIFIED finalization path.** The defect is invisible to every existing test
   because no test exercises a real commit of a registered bridge artifact. A
   test that stages a synthetic chain and asserts the pre-commit checker clears
   it would have caught this and would prevent recurrence.

4. **Re-scope `-005` recommendation 2 using E5.** The rollback is implemented and
   works at the pre-commit failure point. The remaining work is narrower: make
   the write-then-commit sequence resilient to *signal interruption*, which is
   the condition that produced the WI-5424 stranding.

5. **Correct the `gtkb-verify` SKILL.md envelope guidance (E6 gate 5)** to state
   that a `VERIFIED` verdict's envelope head must declare `::open test`. Consider
   also aligning the recurring Loyal Opposition worker instruction, which
   currently opens `build`.

6. **Improve the three-predicate error message (E6 gate 6).** `-005` E3 item 5
   already requested this; this session hit it again and lost an attempt
   confirming which of the three predicates had failed. The code already
   distinguishes the cases.

7. **Once item 1 lands, re-run terminal verification on
   `gtkb-wi5441-owner-liveness-spec-amendments`.** The review is complete and its
   evidence is recorded in E7. A future session should be able to file `-012` as
   VERIFIED without repeating the investigation.

Not recommended: attempting further VERIFIED filings on any thread before item 1
lands. Unlike `-005`'s situation, the attempt is now known to be safe, but it is
also known to be futile.

## Classification Slot

- Classification: `adapt`. `-006`'s findings stand unmodified. This entry
  supersedes the `-004` causal hypothesis as the explanation for the *commit*
  refusal (while leaving its packet-hash observations intact), corrects `-005`
  E1's operational assumption about rollback, and adds the two-table mismatch
  that none of `-001` through `-006` identified.
- Implementation implied: yes. Item 1 is a defect fix in a governance gate; item
  2 is a design decision plus possible schema work; item 3 is new test coverage;
  items 5 and 6 are managed-skill and error-message corrections.
- This advisory is not an approval to implement. Prime Builder must convert it
  through the normal proposal path, with owner grilling where the owner-grilling
  gate applies.

## Prior Deliberations

- `bridge/gtkb-lo-tooling-defect-advisory-001.md` - originating six-defect advisory; A1 first named the finalization blocker.
- `bridge/gtkb-lo-tooling-defect-advisory-002.md` - first packet-hash mechanism proposal, later falsified.
- `bridge/gtkb-lo-tooling-defect-advisory-003.md` - confirmed the deadlock and located the region.
- `bridge/gtkb-lo-tooling-defect-advisory-004.md` - executed proof that database presence drives the packet-hash divergence. This entry falsifies that hypothesis as the cause of the *commit* refusal while leaving the packet-hash finding itself intact.
- `bridge/gtkb-lo-tooling-defect-advisory-005.md` - reported the stranded terminal verdict and four skill-template gates. E5 and E6 here correct and extend it.
- `bridge/gtkb-lo-tooling-defect-advisory-006.md` - the advisory this entry responds to; bridge-state read-surface divergence and the latency correction.
- `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` - owner decision governing the six amendments verified in E7.
- `DELIB-20266278` - owner authorization of the treadmill-drain program that established the auto-finalization sweep.
- `DELIB-202666773` - WI-5510 concurrency sequencing behind git-lock contention; names WI-5496.

## Owner Decisions / Input

No owner decision is requested. The governing authority for the originating
verification work is the active
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` under owner
decision `DELIB-202666274`. This advisory records evidence and discloses state
only; it requests no approval, waiver, or priority choice.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
