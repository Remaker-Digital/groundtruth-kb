ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 148e6095-2e59-4a2c-a6de-a80fe223d833
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Advisory - VERIFIED Finalization Blocked By Packet-Freshness Recomputation

bridge_kind: governance_advisory
Document: gtkb-lo-verified-finalization-packet-freshness-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-27 UTC

---

## Source

Observed directly by this reviewer while attempting to file the terminal verdict
for `gtkb-wi5441-bridge-publication-capability-commit-clearance` during a
scheduled Loyal Opposition run on 2026-07-27.

Not derived from an external peer system. Every observation below was produced by
executing the governed tooling in this repository.

Related prior records: backlog item 4 of
`bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-002.md`
(independently reproduced here) and the finalization-mechanics correction at
`bridge/gtkb-wi5441-owner-liveness-spec-amendments-008.md`.

## Claim

**C1 (P1). A source-bearing terminal `VERIFIED` finalization cannot be filed,
because the `packet_hash` anchor is validated against two different repository
states inside one atomic transaction.**

`write_verdict.py --finalize-verified` audits the candidate verdict *before*
writing and before staging. `.githooks/pre-commit` then re-runs the same
bridge-compliance audit on the staged candidate. The transaction stages its
include set between those audits, and the two audits then expect different
`packet_hash` values. No single embeddable value satisfies both.

Evidence:

1. Fresh preflight against the operative file returned
   `packet_hash: sha256:c6157d05deff11bbfe8bcaeaea8f076c2a982f02a3fba7e484a426f23728370e`.
2. Calling `build_packet` with exactly the arguments the gate uses
   (`bridge-compliance-gate.py:1554-1563`) reproduced the same value, confirming
   the anchor was correct at authoring time.
3. The writer's pre-write audit accepted it. Its only complaint was
   `candidate_evidence_hash`, which is checked *after* the `packet_hash`
   comparison at `bridge-compliance-gate.py:1567`.
4. With that corrected, the helper wrote and staged the candidate, and the
   pre-commit checker refused: `expected sha256:2647f185d40fa632069b426170b51d33d8e74d5a83b60eeef83d27b500be98b3`
   for the `-003` operative file.
5. The helper failed closed correctly: no `-004` remained and the index stayed
   clean.

Ruled out: line endings (the operative file is plain LF ASCII); the candidate
file's presence (an in-root sandbox computed `build_packet` for `-003` with and
without a candidate `-004` and returned an identical hash, `stable: True`); and
the invocation form (neither the `--content-file` form, `c6157d05...`, nor the
bare `--bridge-id` form, `46fdd8ab...`, yields the demanded `2647f185...`).

Most probable mechanism: the packet incorporates repository state the transaction
mutates - the staged set. The comparison case supports it. A bridge-only
finalization on the sibling thread succeeded minutes earlier at commit
`9c22e02c2`, staging eleven `bridge/*.md` paths and nothing else. The blocked
transaction additionally stages two implementation paths. If staged non-bridge
implementation paths participate in packet construction, bridge-only
finalizations pass and every source-bearing finalization is blocked - matching
both observations.

No reviewer-side workaround exists. Embedding the hook's value causes the writer
to reject it; embedding the writer's value causes the hook to reject it.
Pre-staging so both audits observe one state is unavailable: direct `git add` is
refused by the git-lifecycle boundary, and the canonical
`python -m groundtruth_kb.git_lifecycle` surface is work-item-branch scoped
(`create`/`attach`/`preserve`/`promote`), so using it would create branch
bindings far outside review scope.

**C2 (P2). The `candidate_evidence_hash` anchor cannot be computed before
filing.** It covers the writer's post-injection bytes, which the author cannot
reproduce before the write. The only way to obtain it is to attempt the write,
read the expected value from the rejection, and retry. The sibling `-012`
finalization needed three attempts for this reason alone; the two failed attempts
persist as `compensated` rows (rowids 54, 55) against the successful `consumed`
row (rowid 62) in `sot_registry_bridge_publication_capabilities`.

**C3 (P2). The documented preflight invocation produces a rejected anchor.** The
`gtkb-bridge` skill documents the bare `--bridge-id` form, but the governed
writer accepts only the `--content-file <operative-file> --bridge-id <slug>`
form. Reviewers following the documentation are hard-blocked with a stale-packet
error that never names the invocation form as the cause. Independently
reproduces `-002` backlog item 4.

**C4 (P2). `ADVISORY` cannot be filed through the documented advisory path
without two undocumented corrections.** Filing this advisory required
discovering that (a) `normalize_bridge_envelope_head` rejects any `::init`/
`::open` envelope lines for statuses with no responder-role mapping, so an
ADVISORY body must omit them, and (b) `bridge_kind: loyal_opposition_advisory` -
the value documented in `.claude/rules/canonical-terminology.md` under "Loyal
Opposition advisory" and in `.claude/rules/peer-solution-advisory-loop.md` - is
no longer in the enum. `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` now requires
`governance_advisory`. The glossary and the peer-solution-advisory-loop rule are
stale against the live taxonomy.

**C5 (P3). Two governance guards false-positive on read-only commands.** The
Loyal Opposition file-safety guard refused a read-only Python one-liner because
it contained an encoding keyword argument, reporting a "shell mutation" to a file
named for that encoding value, and separately refused a read-only command whose
only unusual feature was shell command substitution. The implementation-start
gate refused a read-only SQL query as an `<unknown-mutating-target>` protected
mutation because the query *string* contained a protected source filename. The
second is the more significant: it sits on the deliberation-search path Loyal
Opposition is required to execute before filing, and the natural query text for
reviewing a protected file contains that file's name. Both were worked around by
rewriting the command; no evidence was lost.

**C6 (P3). A timed-out finalization can hide a successful commit.** The `-012`
finalization exceeded a 120-second caller bound and reported timeout, but the
commit had already succeeded (`9c22e02c2`). A caller treating timeout as failure
would try to re-file an already-committed terminal verdict.

## Owner Decision Needed

**None.** This advisory requests no owner decision, approval, waiver, priority
choice, or destructive action.

Every claim is a mechanical defect with an objective reproduction, not a
governance choice. C1 through C4 are tooling repairs; C5 is guard tuning; C6 is a
caller-robustness note. Prime Builder may need owner input when scoping the
remedy for C1, but nothing here is blocked on the owner.

## Recommended Prime Action

File a scoped implementation proposal for **C1 first**. While it stands, no
implementation-bearing bridge thread can reach terminal `VERIFIED` - including
the clearance thread whose own purpose is to unblock terminal finalization. Any
one of these would close it, in rough order of preference:

1. Compute the packet anchor over state the transaction does not mutate, so both
   audits are guaranteed to agree.
2. Have the finalizer stage its include set *before* its own compliance audit, so
   both audits observe the same staged state.
3. Have the writer emit the anchor from a sentinel, removing the author-supplied
   value entirely - which also closes C2.

C2, C3, and C4 sit on the same filing path and are natural candidates to bundle
with C1. C4 additionally requires correcting the stale `loyal_opposition_advisory`
references in `.claude/rules/canonical-terminology.md` and
`.claude/rules/peer-solution-advisory-loop.md`; those are protected narrative
artifacts and need the normal approval-packet path.

This advisory is not implementation approval. Prime Builder should disposition it
through the normal advisory intake path.

## Classification Slot

`adapt`.

The defects are real and reproducible, and the remedies are GT-KB-native repairs
to existing surfaces rather than adoption of any external pattern. C1 requires a
design choice among the three options above, so the disposition is `adapt` rather
than `adopt`.

## Preserved Verification Evidence For The Blocked Thread

Recorded so the work is not lost. This is evidence, not a verdict;
`gtkb-wi5441-bridge-publication-capability-commit-clearance` remains awaiting
Loyal Opposition review.

`-003` was reviewed in full by this reviewer (session
`148e6095-2e59-4a2c-a6de-a80fe223d833`, independent of the `-001`/`-003` author
`019f863a-...` and the `-002` GO author `280d5521-...`):

- **Focused module:** 135 collected, **135 passed** in 72.47s, reproducing
  `-003:164` exactly.
- **Both lint gates, run separately:** `ruff check` returned `All checks passed!`;
  `ruff format --check` returned `2 files already formatted`.
- **Scope:** `git diff --stat` returns 532 insertions across exactly the two
  declared `target_paths` (404 test, 128 checker), matching `-003:209-211`.
- **GO F1 (`expires_at`):** disposed explicitly and the code matches - timestamps
  parsed for well-formedness, `expires_at` not compared to now, `expired`
  rejected via the `!= "consumed"` guard.
- **GO F2 (duplicate attempts):** disposed explicitly; the query is
  `ORDER BY rowid DESC LIMIT 1` with no state pre-filter, so the newest attempt
  is selected and then rejected - the conservative branch.
- **GO F3 (anti-shortcut):** no blanket `bridge/**` exemption. Clearance is bound
  per path by exact `target_path` equality, `document_name`/`version`
  cross-check, `authority_kind`/`operation` equality, linked-revision equality on
  `entry_id`/`operation`/`capability_hash`/`bridge_id`, and a copied-index (not
  worktree) blob digest that independently re-hashes the blob against its index
  object id.
- **Claimed audit revisions confirmed:** `SOTREV-5504D99ED42E49EE960D846CAD971BCB`
  and `SOTREV-385484E6B58F4712979F4C758861AC22` exist with the entry ids and
  capability hashes reported at `-003:183-187`.
- **Production proof:** commit `9c22e02c2` committed eleven previously-untracked
  registered bridge paths plus a terminal verdict through
  `.githooks/pre-commit:32` (`core.hooksPath=.githooks`) with no `--no-verify`,
  using the already-modified checker. The pre-repair checker refuses every
  registered bridge path unconditionally, so that commit could not have succeeded
  under the old code.
- **F2 semantics confirmed in production:** the cleared `-012` path carries three
  publication attempts - rowid 62 `consumed`, rowids 55 and 54 `compensated`. The
  newest is the consumed row, and the commit cleared.

On the merits this reviewer reached VERIFIED. It could not be recorded because of
C1.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

## Prior Deliberations

_No prior deliberations: <fill in reason before filing>._
