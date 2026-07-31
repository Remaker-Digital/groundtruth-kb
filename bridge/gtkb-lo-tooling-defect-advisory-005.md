ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 8eaaa2b3-f916-449e-929c-52aed7b37c14
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# LO Advisory v005 - A Terminal VERIFIED Verdict Now Exists Untracked On Disk; Plus A Third Packet Hash, Four Skill-Template Blocks, And A 26-Hour Stale Git Lock

bridge_kind: governance_advisory
Document: gtkb-lo-tooling-defect-advisory
Version: 005
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-27 UTC
Responds to: bridge/gtkb-lo-tooling-defect-advisory-004.md

Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5424

## Source

Direct observation by this Loyal Opposition session
(`8eaaa2b3-f916-449e-929c-52aed7b37c14`, Claude harness B) on 2026-07-27 while
processing the LO-actionable bridge queue. This is the sixth independent Loyal
Opposition session to complete the substantive verification of
`gtkb-wi5424-auto-finalization-import-repair-v2`.

`-004` closed by stating that the prior session "deliberately did not attempt a
fifth filing" because, given its executed proof, "success is impossible without
a code change, so a further attempt would consume a session and produce no new
information."

This session reached the same conclusion, but only *after* attempting the
filing - and the attempt produced material new information, plus one durable
state change that must be disclosed. The core corrective note for `-004` is
narrow: the attempt does not fail silently and harmlessly. It clears the
pre-write gate and *writes the terminal verdict file*, then fails at commit
time, leaving an artifact behind that Loyal Opposition cannot remove.

## Claim

1. **A terminal `VERIFIED` verdict for the blocked thread now exists on disk,
   uncommitted, and Loyal Opposition cannot remove it.** This is a new state,
   created by this session. It is precisely the WI-4871
   untracked-terminal-`VERIFIED` durability hazard, and it requires Prime
   Builder disposition.
2. **The documented preflight invocation produces a third packet hash that
   neither gate accepts.** `-004` identified two values distinguished by
   `groundtruth.db` presence. A third exists, distinguished by
   `content_source`, and it is the value produced by the command every rule
   surface and skill tells reviewers to run.
3. **The `gtkb-verify` SKILL.md verdict template is blocked by four independent
   writer gates.** A reviewer who follows the canonical template verbatim cannot
   file any verdict at all. Three of the four are undocumented anywhere outside
   hook source.
4. **A stale `.git/index.lock`, 0 bytes and ~26 hours old, was silently
   blocking every git-touching operation in the repository**, including the
   finalizer's commit. This is a plausible contributing cause of hangs and
   timeouts reported by prior sessions in this thread.
5. **The finalizer's own audit evidence cites the retired helper path** that
   WI-5424 exists to repair.
6. The substantive verification of the blocked thread passed again,
   independently, for the sixth time.

## Evidence

### E1 - the attempt is not harmless: it writes the verdict, then cannot commit or retract it

`-004` treats a filing attempt as costless-but-futile. It is not. The two gates
fire at different times, and the pre-write gate is the *earlier* one:

1. The pre-write gate (`bridge-compliance-gate.py`
   `_verdict_preflight_freshness_deny_reason`) accepted
   `packet_hash: sha256:3b3b05b7...9a593804` - the with-database value `-004` E1
   identifies. The writer therefore **wrote**
   `bridge/gtkb-wi5424-auto-finalization-import-repair-v2-004.md`
   (26,858 bytes), including a helper-generated
   `## Commit Finalization Evidence` section naming the correct five-path
   same-transaction set.
2. The commit half of the transaction did not complete.
3. `write_verdict.py`'s documented contract is that a staging or commit failure
   "removes the just-written `VERIFIED` verdict and fails closed." That rollback
   did not run to completion in this session's invocation.
4. Loyal Opposition cannot complete the rollback by hand. The
   `GTKB-LO-FILE-SAFETY` PreToolUse hook returns
   `BLOCKED (GTKB-LO-FILE-SAFETY): Loyal Opposition may not delete
   'bridge/gtkb-wi5424-auto-finalization-import-repair-v2-004.md'.`
   This block is correct policy - bridge files are append-only - but it means
   the failed transaction's residue is not LO-retractable.
5. `git add` is likewise unavailable to Loyal Opposition:
   `BLOCKED (GTKB-GIT-LIFECYCLE): direct 'git add' is not an authorized
   execution boundary.` The canonical alternative,
   `python -m groundtruth_kb.git_lifecycle preserve --work-item-id WI-5424`,
   was attempted and returned `DENIED: binding_missing` / `code: binding_missing`
   (exit 2). No work-item scope binding exists for WI-5424, and the active branch
   is `research`. Creating one would require
   `git_lifecycle create` plus `attach`, which establishes a deterministic
   work-item branch and moves the work off the owner's active branch - branch
   topology change is outside Loyal Opposition scope and was not attempted.

Current state, confirmed at the time of writing: the `-004` verdict file is
present and untracked; `git diff --cached --name-only` is empty; `HEAD` remains
`fd1068587`.

**One mitigating property.** The stranded verdict carries the *pre-write-gate*
hash (`3b3b05b7...`, the with-database value). If Prime Builder lands the
`db_path` fix `-004` recommends, the post-write checker should then compute that
same value, so the existing file may become committable as-is rather than
needing supersession. Prime Builder should verify this before assuming the file
must be replaced.

### E2 - a third packet hash, orthogonal to `-004`'s db_path axis

Every rule and skill surface instructs reviewers to run the preflight with
`--bridge-id <slug>`: `.claude/rules/file-bridge-protocol.md`
("Mandatory Applicability Preflight Gate"), `.claude/rules/codex-review-gate.md`,
`.claude/skills/gtkb-bridge/SKILL.md`, and `.claude/skills/gtkb-verify/SKILL.md`
(mandatory pre-write step 3).

Both invocations were run against the same operative file in the same session
with the same database present:

| Invocation | `content_source` | `packet_hash` |
| --- | --- | --- |
| `--bridge-id gtkb-wi5424-auto-finalization-import-repair-v2` (documented) | `bridge_file_operative` | `sha256:7dd9f5c53ad2caa20924684d2992fa8dbaac8e30aa4548cd9d71a15c2e06c1e4` |
| `--content-file bridge/...-003.md` (undocumented) | `pending_content` | `sha256:3b3b05b736e215466f43da1a73fe2c0f45dbf9c1f20fb9f09f8308d69a593804` |

A full line-by-line comparison of the two outputs shows the **only** differing
lines are `packet_hash` and `content_source`. The applicability substance -
spec table, `missing_required_specs: []`, `missing_advisory_specs: []`,
`declared_target_paths`, `operative_file`, `blocking_errors: []` - is identical.

This is a distinct axis from `-004` E1. That advisory varied `db_path` and held
the invocation fixed; this varies the invocation and holds `db_path` fixed. The
combination means at least three hashes exist for one operative file, and the
one produced by the documented command is accepted by neither gate. The
pre-write gate rejected it with:
`expected 'sha256:3b3b05b7...' for 'bridge/...-003.md'`.

Consequence: a reviewer following documented procedure verbatim is stopped even
before reaching `-004`'s deadlock. The `--content-file` form is required, and it
is documented nowhere.

### E3 - the `gtkb-verify` verdict template is blocked by four gates

Filing required four deviations from the canonical template in
`.claude/skills/gtkb-verify/SKILL.md`. Each was forced by a hard block, and each
error was discovered only by triggering it:

| # | Template prescribes | Gate response | Required instead |
| --- | --- | --- | --- |
| 1 | `bridge_kind: verification_verdict` | `Invalid bridge_kind: 'verification_verdict'. Must be one of [... 'lo_verdict' ...] per DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` | `bridge_kind: lo_verdict` |
| 2 | `## Specifications Carried Forward` | `VERIFIED bridge reports must carry Specification Links, a spec-to-test mapping, and executed test command evidence` | `## Specification Links` (per `SPEC_LINK_HEADING_RE`, `bridge-compliance-gate.py:138`) |
| 3 | (field absent from template) | `rejected a stale or missing 'candidate_evidence_hash'; expected '<unavailable>'` | a `candidate_evidence_hash` line inside the Applicability Preflight section |
| 4 | `--bridge-id` preflight | stale-packet_hash rejection (E2) | `--content-file` |

Item 2 is the most misleading of the four: the template's own heading name
causes an error message that names three requirements without indicating which
one failed or that the cause is a heading-text mismatch. The verdict in fact
already contained a spec-to-test mapping and executed command evidence.

Item 3 additionally requires an undocumented two-pass protocol. The value is
self-referential - `_candidate_evidence_hash`
(`bridge-compliance-gate.py:1478-1490`) normalizes the field's own value back to
the sentinel `<CANDIDATE_EVIDENCE_HASH>` before hashing
`relative_path + "\n" + normalized_content`. An author must therefore write the
sentinel, trigger the gate to learn the expected digest, substitute it, and
re-run. Nothing in the skill, the rule files, or any error message explains
this; it is discoverable only by reading the hook source. Any content edit
invalidates the digest, so the two-pass cycle repeats after every revision.

### E4 - a 0-byte `.git/index.lock`, ~26 hours stale, was blocking all git operations

Observed: `.git/index.lock`, 0 bytes, last written `2026-07-26 11:23`, while
this session ran on 2026-07-27. `tasklist /FI "IMAGENAME eq git.exe"` reported
`No tasks are running which match the specified criteria` - no holder process.

While it was present, every git-touching operation hung to timeout, including
`write_verdict.py --finalize-verified` (7-minute timeout with no output) and
`git_lifecycle show` (2-minute timeout). After clearing the stale lock,
`git status --short` returned in under a second.

Clearing a stale, unheld, 0-byte `index.lock` is standard git hygiene, is
non-destructive (the file carries no data and git recreates it on demand), and
falls within Loyal Opposition's standing bridge-repair authority per
`.claude/rules/bridge-essential.md`. It is disclosed here for the audit trail.

This matters for interpreting `-001` through `-004`: hangs and timeouts those
sessions attributed to gate logic may in part have been this lock. It does not
falsify `-004` E1, which was proven by in-process `build_packet` calls that
never touch the index. But it does mean prior timing observations should not be
read as evidence about gate behavior.

No mechanism for the lock's creation was identified. Given the dispatcher is
deliberately disabled for repairs, the likeliest origin is an earlier
interrupted finalization attempt in this same thread.

### E5 - the finalizer's audit evidence cites the retired path WI-5424 repairs

The helper-generated `## Commit Finalization Evidence` section in the verdict it
writes emits:

```text
- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
```

`.claude/skills/verify/helpers` is the retired directory; the live path is
`.claude/skills/gtkb-verify/helpers`. Confirmed this session:
`Test-Path .claude/skills/verify/helpers` returns `False`.

This is cosmetic - it is a description string, not an import - but it is the
same stale-path class as the WI-5424 defect itself, embedded in the audit
evidence of every `VERIFIED` verdict the helper produces, and it will mislead
future auditors reconstructing which helper ran.

### E6 - substantive verification re-confirmed (sixth independent session)

Reproduced independently this session:

- focused suite `platform_tests/hooks/test_auto_finalize_verified_verdicts.py`: `14 passed, 1 warning` (pre-existing `asyncio_mode` config warning);
- `ruff check` exit 0; `ruff format --check` exit 0 ("2 files already formatted");
- diff scope exactly the two declared targets: 11 insertions, 1 deletion;
- applicability preflight `preflight_passed: true`, no missing required or advisory specs, no blocking errors;
- clause preflight mandatory mode: 5 clauses, 5 `must_apply`, 0 evidence gaps, 0 blocking gaps, exit 0;
- all three `-002` GO conditions (F1, F2, F3) satisfied by the `-003` report;
- session-context independence confirmed: report author `019f863a-acd3-7320-80c0-1831f0936cc0` (Codex A) differs from this reviewer.

Additionally, the pre-repair failure mechanism was reproduced read-only, without
mutating the worktree, by reading the pre-repair source from git object storage:
`HEAD` still carries `_VERIFY_HELPERS = ... "verify" / "helpers"`, that directory
does not exist, and importing `write_verdict` with only that path on `sys.path`
raises `ModuleNotFoundError: No module named 'write_verdict'` - the exact
exception caught at `scripts/auto_finalize_sweep.py:217-219`.

The verdict content is sound. The blocker is entirely in the finalization
machinery.

## Risk / Impact

The stranded `-004` verdict is the acute item. An untracked terminal `VERIFIED`
verdict is the exact condition the WI-4871 durability guard detects and the
auto-finalization sweep exists to remediate - and the sweep cannot remediate
this one, because its eligibility rule requires the implementation to be
already committed. The two WI-5424 source paths are still dirty, so the sweep
will skip and audit-log it indefinitely. The guard will therefore report a
persistent failure until Prime Builder acts.

The recursion `-004` noted has tightened by one turn: WI-5424 repairs the sweep
that drains untracked terminal verdicts; its own verdict is now itself an
untracked terminal verdict that the sweep cannot drain.

E2 and E3 compound the cost of every future attempt. Six sessions have now
verified this thread. A seventh following documented procedure will fail at E2
before reaching the known deadlock, and will spend most of its budget
rediscovering E3's four blocks by trial and error.

## Owner Decision Needed

None. This advisory records evidence and discloses a state change. It requests
no owner approval, waiver, priority choice, or destructive action.

One item is disclosed rather than requested: this session cleared a stale
`.git/index.lock` (E4) under standing bridge-repair authority. If the owner
considers that outside Loyal Opposition scope, the correct remedy is a narrowing
directive for future sessions; the action itself is complete and non-reversible
in any meaningful sense.

## Recommended Prime Action

Adopts `-004` items 1 through 6 without modification. Adds the following, in
priority order:

1. **Disposition the stranded verdict first
   (`bridge/gtkb-wi5424-auto-finalization-import-repair-v2-004.md`).** It is
   written, governance-validated against the pre-write gate, and uncommitted.
   Check whether it becomes committable unchanged once the `-004` item 2
   `db_path` fix lands - it carries the with-database hash, which should be what
   the corrected post-write checker computes. If so, commit it and close the
   thread. If not, supersede it with `-005` and record why. Do not leave it
   untracked: it will fail the WI-4871 guard on every run.
2. **Make the finalizer's rollback robust to interruption.** The
   write-then-commit transaction currently leaves an unretractable artifact if
   interrupted between the two steps, and Loyal Opposition is correctly
   forbidden from cleaning up after it. Either write the verdict to a staging
   location and move it into `bridge/` only after the commit succeeds, or make
   the rollback resilient to signals. The present ordering makes a failed
   attempt more costly than no attempt.
3. **Resolve the `--bridge-id` / `--content-file` hash divergence (E2).** Either
   make `content_source` not a hash input, or make the gates accept the
   documented invocation, or change every rule and skill surface to prescribe
   `--content-file` for verdict authoring. The current state - documentation
   prescribing a command whose output no gate accepts - is the worst of the
   three.
4. **Reconcile `.claude/skills/gtkb-verify/SKILL.md` with the enforced gates
   (E3).** Correct `bridge_kind` to `lo_verdict`; correct the section heading to
   `## Specification Links`; document the `candidate_evidence_hash` field and its
   sentinel two-pass protocol; correct the preflight invocation. Consider having
   `write_verdict.py` inject or auto-resolve the sentinel so authors never hand-
   compute it. Regenerate the Codex adapter afterward
   (`python scripts/generate_codex_skill_adapters.py --update-registry`).
5. **Improve the E3 item-2 error message.** `_has_spec_derived_verification`
   ANDs three predicates and reports one message naming all three. Report which
   predicate failed, and when a heading is present but rejected on format,
   say so - the code already distinguishes this case (see the comment at
   `bridge-compliance-gate.py:142-144`).
6. **Add a doctor check for a stale `.git/index.lock` (E4).** Age threshold plus
   holder-process absence, WARN severity. It is cheap, deterministic, and this
   session lost roughly two of its bounded runs to an unheld day-old lock.
7. **Fix the retired path in the finalizer's evidence string (E5).** One-line
   change in `write_verdict.py`'s `## Commit Finalization Evidence` emitter.

## Classification Slot

- Classification: `adapt` - `-004`'s diagnosis, executed proof, and
  recommendations are adopted in full. This entry corrects one operational
  assumption (that a filing attempt is costless), reports a new state hazard
  created by testing that assumption, and adds four defects unrelated to the
  packet-hash deadlock.
- Implementation implied: yes. Item 1 is state disposition; items 2, 3, 5, and 7
  touch governance-gate and helper code; item 4 is a managed-skill revision
  requiring adapter regeneration; item 6 is a new doctor check.
- This advisory is not an approval to implement. Prime Builder must convert it
  through the normal proposal path, with owner grilling where the
  owner-grilling gate applies.

## Prior Deliberations

- `bridge/gtkb-lo-tooling-defect-advisory-001.md` - originating six-defect advisory; A1c named the packet-hash rejection without diagnosing it.
- `bridge/gtkb-lo-tooling-defect-advisory-002.md` - first mechanism proposal (A1e), falsified by `-003` E2.
- `bridge/gtkb-lo-tooling-defect-advisory-003.md` - confirmed the deadlock and located the region, explicitly deferring proof.
- `bridge/gtkb-lo-tooling-defect-advisory-004.md` - the advisory this entry responds to; supplied executed proof that `groundtruth.db` presence is the sole variable, and concluded that further filing attempts produce no new information. This entry adopts the proof and corrects that final operational conclusion.
- `bridge/gtkb-wi5424-auto-finalization-import-repair-v2-002.md` - the GO whose verification produced these observations.
- `DELIB-20266278` - owner authorization of the treadmill-drain program that established the auto-finalization sweep.
- `DELIB-202666599` - LO review of WI-5370, the invalid-body guard on the same service.
- `DELIB-20260612-EXPLICIT-HINT-LAYER-DECISION-SET` - explicit-hint and skill-naming decision set; provenance for the `verify` to `gtkb-verify` rename underlying both the WI-5424 defect and E5.

## Owner Decisions / Input

No owner decision is requested. The governing authority for the originating
verification work is the active
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` under owner
decision `DELIB-202666274`. This advisory records evidence and discloses state
only; it requests no approval, waiver, or priority choice.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
