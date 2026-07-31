ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: ca24f22d-78d0-467d-9e40-4a38df278538
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session-envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Advisory - VERIFIED Finalization Has No Resume Path, So An Interrupted Transaction Strands A Published Terminal Verdict And Requires Owner Intervention

bridge_kind: governance_advisory
Document: gtkb-lo-verified-finalization-interrupted-transaction-recovery-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC

## Source

Observed directly by this reviewer on 2026-07-28 while filing the terminal
`VERIFIED` verdict for `gtkb-wi5441-global-registry-membership-reconciliation`
at `-020`, during a scheduled Loyal Opposition run. Every observation below was
produced by executing the governed tooling in this repository.

The owner had to intervene manually to resolve the resulting state. Commit
`f9e85829e`, authored by the owner, carries the body: *"WI-5441 is terminal
VERIFIED at -020 but the verdict and its 5 implementation files are uncommitted,
and no role-based or automated path can resolve it."* That is the defect this
advisory describes, stated by the owner.

**This advisory also retires one claim of a sibling advisory.** See C0.

## Claim

### C0 (P1, RESOLVED - retire the prior claim)

**`bridge/gtkb-lo-verified-finalization-packet-freshness-advisory-001.md` C1 no
longer reproduces and should be closed.**

That advisory (2026-07-27) claimed that *"a source-bearing terminal `VERIFIED`
finalization cannot be filed"* because the `packet_hash` anchor was validated
against two different repository states, with *"no reviewer-side workaround."*

This session filed exactly such a finalization - five implementation paths plus
seven bridge paths - and the `packet_hash` anchor was accepted by both the
pre-write audit and the write. The remedy appears to be commit `1c82158e8`,
*"fix(bridge): reproducible verdict freshness and exact-row publication routing
(WI-5441)"*. Two further sub-claims also failed to reproduce:

- **C3 does not reproduce.** The bare `--bridge-id` form and the
  `--content-file <operative-file>` form returned the *identical*
  `packet_hash: sha256:c93343285e5b764a13bdb37fa22ded05041ca4fd0a637276f5f236723156de29`.
  Only `content_source` differed (`bridge_file_operative` vs `pending_content`).
- **C2 is confirmed but is by design, not a defect.** The
  `candidate_evidence_hash` anchor genuinely cannot be computed before the
  write. However, `CANDIDATE_EVIDENCE_HASH_LINE_RE`
  (`bridge-compliance-gate.py:200-204`) explicitly accepts a
  `<CANDIDATE_EVIDENCE_HASH>` sentinel, and `_candidate_evidence_hash`
  (`:1478-1490`) normalizes that line to the sentinel before hashing. The
  intended flow is therefore two-pass: file with the sentinel, read the expected
  value from the rejection, substitute, re-file. Substituting does not perturb
  the hash. **This works and is not a blocker - it is undocumented.** The
  `gtkb-bridge` and `gtkb-verify` skills describe neither the anchor nor the
  two-pass flow.

Prime Builder should disposition the prior advisory as substantially resolved
rather than schedule C1 work.

### C1 (P1). An interrupted finalization leaves a published terminal verdict with no resume path

`finalize_verified_commit` (`write_verdict.py:1134-1230`) performs, in order:
version resolution, body validation, `write_bridge_file` (which **publishes to
canonical bridge state and consumes a publication capability**), then temporary-
index staging and `git commit`. The commit phase re-runs the full bridge
compliance audit through `.githooks/pre-commit` and is slow.

If the process is interrupted **after** publication but **before** commit, the
result is:

- canonical bridge state reports `latest_status: VERIFIED` at the new version;
- the verdict file exists on disk, **untracked**;
- the implementation paths remain uncommitted;
- the publication capability row is `capability_state: consumed`.

Observed this session at row 101 of
`sot_registry_bridge_publication_capabilities`: `document_name`
`gtkb-wi5441-global-registry-membership-reconciliation`, `version 20`,
`status VERIFIED`, `consumed_at 2026-07-28T15:36:38Z`,
`revision_id SOTREV-44524FC9C1D44C44A3EFAB5BB3EB9653`. `HEAD` was unchanged at
`f3e353db6` and `git status` showed `-020` untracked.

**No recovery path exists for this state:**

1. **Re-running the helper does not resume.** `_assert_verification_ready`
   resolves the next version from the live chain. With `-020` on disk it would
   compute `021`, writing a duplicate terminal verdict rather than completing
   the pending transaction. There is no `--resume` or `--finalize-only` mode.
2. **The auto-finalization sweep does not apply.**
   `.claude/rules/auto-finalization-sweep.md` requires that the responded-to
   report's `target_paths` all be *clean* in `git status`. Here five
   implementation paths are dirty by construction, because committing them is
   the very step that did not happen. The sweep is scoped to bridge-file-only
   finalization and explicitly never stages source.
3. **Direct staging did not work.** `git add -- <exact include set>` returned
   exit 0 and staged nothing (`git diff --cached --name-only` empty), consistent
   with the git-lifecycle boundary the sibling advisory reported.
4. **This state is precisely what the protocol forbids.**
   `.claude/rules/file-bridge-protocol.md` § Mandatory VERIFIED
   Commit-Finalization Gate: Loyal Opposition *"MUST NOT leave a terminal
   `VERIFIED` bridge file in the worktree unless the same local transaction
   creates the git commit."* The helper enforces this by removing the verdict
   and failing closed **on its own error paths** - but an external interruption
   bypasses that cleanup entirely, and the publication has already been
   consumed, so removing the file would then desynchronize canonical state from
   the file chain.

The consequence is that the reviewer role cannot self-heal. The owner resolved
it by hand at `f9e85829e`.

### C2 (P2). Finalization wall-clock exceeds practical caller bounds, and the cost is unbounded and undisclosed

The successful publication took roughly 30 seconds
(`created_at 15:36:09` -> `consumed_at 15:36:38`). The commit phase then ran
past a 9-minute caller bound without completing. The helper emits no progress
output, so a caller cannot distinguish "slow" from "hung," and the documented
skill surfaces state no expected duration.

This interacts badly with C1: the longer the commit phase runs, the more likely
an interruption lands in exactly the window that produces the unrecoverable
state. It also compounds the sibling advisory's C6 (*a timed-out finalization
can hide a successful commit*) - the two failure modes are adjacent and a caller
must check actual repository state after any timeout rather than trust the exit
code. This reviewer did so, which is how the stranded state was identified
rather than compounded by a re-file.

### C3 (P3). The interrupted transaction leaked a temporary index into the repository

`_create_temporary_index` (`write_verdict.py:1196`) creates a scratch git index
under a `.gtkb-index-<suffix>/` directory in the project root. On interruption
its cleanup did not run, leaving `.gtkb-index-hl705ij2/index` (2,510,618 bytes)
in the worktree as an untracked file.

Because it is untracked and unignored, the owner's unblocking sweep captured it:
`.gtkb-index-hl705ij2/index` is now **tracked in `f9e85829e`**, and `git status`
currently reports it as deleted-from-worktree. A 2.4 MB git index object is now
part of repository history and of the registry's observable file domain.

Two independent fixes apply: add `.gtkb-index-*/` to `.gitignore` so debris can
never be swept into a commit, and place the scratch index under `.gtkb-state/`
(already ignored) rather than the project root.

## Owner Decision Needed

**None from this advisory.**

Every claim is a mechanical defect with an objective reproduction, not a
governance choice. C0 is a retraction of prior claims based on new evidence; C1
and C2 are tooling repairs; C3 is hygiene. Prime Builder may need owner input
when scoping the C1 remedy, and the disposition of the now-tracked
`.gtkb-index-hl705ij2/index` is an owner call because removing it from tracking
is a deletion.

## Recommended Prime Action

File a scoped implementation proposal for **C1 first**, after the owner-grilling
gate below. Candidate remedies, in rough order of preference:

1. **Make finalization resumable.** Detect a `consumed` publication capability
   whose `target_path` is untracked and whose commit did not land, and offer
   `--finalize-only` that stages and commits the recorded include set for the
   already-published version instead of computing a new one. This is the
   narrowest fix and directly matches the observed state.
2. **Reorder the transaction so publication is last.** Stage and prepare the
   commit first, publish to canonical state only once the commit succeeds. This
   removes the vulnerable window entirely rather than adding recovery for it.
3. **Widen the auto-finalization sweep** to cover published-but-uncommitted
   terminal verdicts whose implementation paths are dirty, gated on a matching
   `consumed` capability row. Weaker than 1 or 2, because the sweep is
   deliberately scoped to never stage source.

**Supporting, independently useful:**

- Document the `candidate_evidence_hash` two-pass sentinel flow in the
  `gtkb-bridge` and `gtkb-verify` skills (C0/C2 of the sibling advisory). It is
  currently discoverable only by reading the hook source or by trial rejection.
- Emit progress output during the commit phase and state an expected duration,
  so callers can set bounds instead of guessing (C2).
- Add `.gtkb-index-*/` to `.gitignore` and relocate the scratch index under
  `.gtkb-state/` (C3).
- Disposition
  `bridge/gtkb-lo-verified-finalization-packet-freshness-advisory-001.md` as
  substantially resolved per C0, so its P1 does not continue to read as an open
  blocker on all terminal finalization.

### Option rationale

Rejected: *raise caller timeouts and otherwise leave the design alone.* This
narrows the window without closing it, and the failure mode is
unrecoverable-without-owner rather than merely inconvenient. Cost of the bad
outcome is too high relative to the cost of the fix.

Rejected: *have the helper delete the verdict file on any interruption.* Once
the publication capability is `consumed`, canonical bridge state already reports
the new terminal version. Deleting the file would desynchronize state from the
file chain - strictly worse than the stranded state, and a violation of bridge
append-only discipline.

Preferred: remedy 2 if the publication ordering can be inverted safely, since it
removes the failure class; otherwise remedy 1, which is small, targeted, and
matches the evidence exactly.

### Required Prime Builder Owner-Grilling Gate

**Implementation implied:** Yes - changes to `write_verdict.py`, possibly
`gtkb_bridge_writer.py` publication ordering, `.gitignore`, and two skill
surfaces.

**Grill-the-owner questions.** Prime Builder must obtain durable
`AskUserQuestion`-recorded answers to:

1. **Remedy shape.** Resume-after-interrupt (remedy 1), reorder so publication
   is last (remedy 2), or widen the sweep (remedy 3)? Remedy 2 is the deeper fix
   and the larger change.
2. **Capability semantics under reorder.** If publication moves after commit,
   what consumes the capability if the commit succeeds but publication then
   fails? The failure window moves rather than disappearing, and the owner
   should choose which side carries it.
3. **Index-debris disposition.** Should `.gtkb-index-hl705ij2/index`, now
   tracked at `f9e85829e`, be removed from tracking? That is a deletion and
   needs explicit authorization per the removal rule.
4. **Sweep scope.** Should the auto-finalization sweep ever be permitted to
   stage source paths, or must that boundary hold absolutely? Today it is
   absolute, which is why it could not help here.

**Required durable owner decisions** before an implementation proposal may be
filed: the remedy shape (Q1), the capability-ordering semantics if Q1 selects
remedy 2 (Q2), an explicit separate authorization for the deletion in Q3, and
the sweep-boundary posture (Q4).

## Prior Deliberations

Searched `gt deliberations search` on verdict finalization, bridge publication,
and commit-clearance terms, and read every bridge artifact cited below directly.

- `bridge/gtkb-lo-verified-finalization-packet-freshness-advisory-001.md` -
  **directly load-bearing.** Its C1/C3 are retired by C0 above; its C2 is
  reclassified as an undocumented-but-working design; its C6 is corroborated and
  extended by C2 above.
- `bridge/gtkb-lo-advisory-verdict-filing-governed-cli-gap-001.md` - independent
  corroboration this session: `gt bridge --help` still exposes no `file-verdict`
  subcommand. That advisory's claim stands unchanged.
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-020.md` - the
  terminal verdict whose filing produced this evidence. Its content digest
  matches the publication capability's `content_digest` exactly, so the stranded
  transaction did not corrupt the artifact.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - governs any deletion arising
  from Q3; deletion is explicitly not proposed here.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - filed under its operational
  mandate to surface repetition and friction rather than absorb it silently.
- `GOV-FILE-BRIDGE-AUTHORITY-001` and `.claude/rules/file-bridge-protocol.md`
  § Mandatory VERIFIED Commit-Finalization Gate - the invariant the stranded
  state violates.

No existing work item covers finalization interruption recovery.

## Classification Slot

`adapt`.

The defects are reproducible and the remedies are GT-KB-native repairs to
existing surfaces rather than adoption of any external pattern. C1 requires a
design choice among three options, so the disposition is `adapt` rather than
`adopt`.

## Non-Approval Semantics

This advisory is not implementation approval and creates no implementation
authority. It recommends that Prime Builder conduct the owner-grilling pass
above, capture the resulting decisions, and only then file a normal `NEW`
implementation proposal citing this advisory as its source. Nothing here
authorizes source, configuration, hook, CLI, rule, history, or file-deletion
mutation.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
