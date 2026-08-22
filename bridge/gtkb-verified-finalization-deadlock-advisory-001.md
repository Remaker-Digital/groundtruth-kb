ADVISORY
::init gtkb pb
::open build

author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: f177a9d9-5f1e-4aee-9f9b-01381b39c668
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Loyal Opposition; transcript-defined ::init gtkb lo; owner-manual dispatch

bridge_kind: governance_advisory
Document: gtkb-verified-finalization-deadlock-advisory
Version: 001
Author: loyal-opposition/claude/B
Date: 2026-08-22T07:20:00Z

Project: Completion Integrity
Work Item: WI-6726
Related Work Items: WI-6530, WI-5230, WI-5953, WI-6535, WI-5158, WI-5159, WI-6542, WI-4978, WI-5431, WI-6138, WI-6609

target_paths: []
implementation_scope: none
requires_review: false
requires_verification: false

# ADVISORY - VERIFIED finalization is unreachable, and the protected-path corollary is untracked

This ADVISORY is owner-visible informational input. It is not dispatchable, never assigned, and
not implementation approval. It is readable by any agent in any role.

## Source

Owner-directed worktree cleanup, 2026-08-22, Loyal Opposition session
`f177a9d9-5f1e-4aee-9f9b-01381b39c668`. The owner directed "Remove the lock and clean up the
work-tree" after a 43-hour stale `.git/index.lock` was found blocking all commits. The lock was
removed (`git_lock_health: PASS`, three lock files cleared). Clearing the lock restored
`git commit`; it did NOT restore governed finalization. Those are different capabilities and only
the first was broken by the lock. Attempting the approved finalization surfaced the findings below.

Prior deliberations consulted: `WI-6726` (Completion Integrity, P0) states the F1 deadlock; this
advisory supplies live reproduction evidence and adds untracked consequences. `WI-6530` is the
decision that untracked `bridge/`; not disputed here. `WI-5230` and `WI-5953` are the same failure
class, observed here as concrete residue. `DELIB-202666332` authorizes exact VERIFIED finalization
to reach a clean worktree; that authorization cannot currently be exercised for any multi-version
thread. Governing authority: `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-STANDING-BACKLOG-001`.

## Claim

### F1 - [P0] Governed VERIFIED finalization cannot complete for any multi-version thread

Evidence. `bridge/` is git-ignored at `.gitignore:622`. `git ls-files bridge/` returns 0 tracked
files against 2,295 `bridge/*.md` on disk. `scripts/skill-helpers/gtkb-verify/write_verdict.py:447`
(`_assert_predecessor_chain_committed`) requires every predecessor `bridge/<slug>-NNN.md` to be
either inside the transaction or git-tracked-and-clean; it calls
`git ls-files --error-unmatch -- <path>` and records a problem on non-zero return. For an ignored
path that call always returns non-zero, so every predecessor raises `VerifiedFinalizationError`.

Risk and impact. Neither contributing decision is wrong alone. Untracking `bridge/` is defensible
object-store hygiene (2,295 append-only files; cf. WI-5431 and WI-6138 on `develop` being
unpushable). Requiring a committed predecessor chain is defensible audit discipline. Composed,
they make the protocol's terminal state unreachable. Because the file-bridge protocol makes the
work-product commit the point at which a work item becomes terminal, no work item can be retired
through the governed path - the mechanism by which the 847-path drift in F5 accumulated.

Recommended action. Three candidate resolutions, each a distinct owner decision: (1) track a
bounded slice of `bridge/` (for example only status-bearing files for non-terminal threads);
(2) relax `_assert_predecessor_chain_committed` to accept an ignored-but-present predecessor,
substituting on-disk chain integrity plus a content hash for git-tracked-ness; (3) move bridge
chain custody out of git entirely (MemBase-backed, per DATABASE MIGRATION) and delete the
assertion as vestigial. Option 2 is the smallest reversible change and preserves both original
decisions' intent - the assertion's real purpose is chain integrity, and git-tracked-ness was only
ever a proxy for it. Option 1 reintroduces the bloat WI-6530 removed. Option 3 is correct
long-term but is gated behind an entire migration program and cannot unblock the current worktree.

### F2 - [P0] Untracked corollary: protected paths are permanently unstageable

Evidence. The inventory-drift gate (`scripts/check_dev_environment_inventory_drift.py`, via
`.githooks/pre-commit --staged --allow-review-evidence`) admits a protected path only when
co-staged bridge evidence is present (`review_evidence_present`); the protected set is declared in
`config/governance/protected-artifact-inventory-drift.toml`. A git-ignored file cannot be staged,
so no protected path can satisfy the gate. In the current worktree this is 97 paths, including
every `.claude/hooks/*.py`, every `.claude/rules/*.md`, `AGENTS.md`, and `CLAUDE.md`.

Risk and impact. Strictly stronger than WI-6726 and apparently untracked. WI-6726 says terminal
verdicts cannot be written. F2 says the most governance-critical file class in the repository -
the hooks and rules that constitute the enforcement surface itself - cannot be committed at all
through the governed path, regardless of verdict state. Enforcement-machinery changes therefore
accumulate as untracked working-tree state, the unversioned-cross-session-deploy risk WI-6535
describes.

Recommended action. Register as a new work item under Completion Integrity, blocked on F1; any F1
option that restores stage-ability of bridge evidence resolves F2 as a consequence. If F1 option 3
is chosen, the inventory-drift gate needs a non-git evidence predicate. F2 should not be folded
into WI-6726: a fix that unblocks verdict writing without restoring co-stageable evidence would
close WI-6726 while leaving F2 live.

### F3 - [P1] Governance gates fail closed on read-only operations

Evidence. (1) `implementation-start-gate` blocked a read-only analysis - a Python program that
reads git status and bridge files and prints to stdout, mutating nothing - with
`matched <unknown-mutating-target> ... Implementation authorization packet has expired`. The
identical program shape succeeded earlier in the same session while a packet was live, then failed
closed once it expired. The trigger is invocation form: heredoc-to-stdin is unclassifiable,
whereas `python -c` classifies and passes. The same gate also blocked a heredoc write to a
git-ignored in-root scratch path under `.gtkb-state/`. (2) `GTKB-GIT-LIFECYCLE` blocked
`git branch --list` and `git for-each-ref` - read-only ref enumeration.

Risk and impact. Both gates exist to constrain effects. Blocking read-only inspection does not
reduce risk; it obstructs the Loyal Opposition investigation methodology that
`.claude/rules/loyal-opposition.md` explicitly authorizes. The `<unknown-mutating-target>`
classification is the unclassified-mutation-class failure named in the canonical glossary: when the
classifier cannot classify, it fails closed even for provably non-mutating commands. The cost is
asymmetric - a reviewer who cannot enumerate refs cannot verify branch topology claims, so the gate
degrades review quality in the name of protecting effects the review was never going to cause.

Recommended action. Add read-only verb allow-listing to both gates: for the git-lifecycle boundary
permit `git branch --list`, `git for-each-ref`, `git show-ref`, and `git log` on refs; for the
implementation-start gate, classify stdin-delivered interpreter invocations rather than treating
them as unknown, or narrow the fail-closed default to commands with observable write verbs.
Allow-listing named read-only verbs is preferable to relaxing the fail-closed default, which would
weaken the gate for genuinely unclassifiable mutations. Relates to WI-6542.

### F4 - [P2] The sweep-commit skill documents an unexecutable command

Evidence. The `gtkb-sweep-commit` skill step 3 documents
`git_lifecycle create --work-item-id <WI-NNNN> --title "<title>" --project-branch <branch>`.
`GitLifecycleService._validate_branch_name` in
`groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py` is called with
`expected_prefix="project/"` for the project branch. Passing `develop` returns
`DENIED: branch_name_invalid`. Observed directly this session for `WI-6609`.

Risk and impact. The skill is the documented procedure for the exact task the owner requested, and
its central command cannot execute as written. A reader following it reaches a denial with no
guidance toward the `project/` to `work-item/` to promote topology the service requires - a
topology whose implementation is itself open work (WI-5158, WI-5159).

Recommended action. Correct the skill's example to a `project/*` branch and add a precondition
noting that the governed branch topology must exist before finalization; or, if the topology is not
yet in force, state which fallback boundary is authorized.

### F5 - Evidence: worktree ownership census (read-only)

854 changed paths measured against all 589 bridge threads. Two independent ownership models were
computed and they disagree by 3.7x, which is itself a finding:

| Model | Basis | Finalizable |
|---|---|---|
| Mention-based | `sweep_commit_helpers._body_cites_protected_path` | 74 paths / 12 threads |
| Scope-based | `implementation_authorization.extract_target_paths` | 20 paths / 10 threads |
| Conservative intersection | neither model contests | 3 paths / 2 threads |

The divergence has two causes. (a) Mention matching is a text match, so a verdict stating that
`fixture_index.json` remains outside the declared change set is counted as ownership when it is in
fact an explicit exclusion (observed in
`bridge/gtkb-wi6746-complexity-metrics-benchmark-004.md`). (b) Only 264 of 589 threads declare
machine-readable `target_paths` at all, so the scope model is blind to 325 threads and its
"unowned" bucket is unreliable.

Census under the scope model: 449 paths contested by live non-terminal threads, 20 VERIFIED-only
uncontested, 2 other-terminal, 376 unowned. Under either model the majority of the worktree is
in-flight work owned by other work items and must be left in place.

Two threads are clear under every model, were verified this session, and are ready to finalize the
moment F1 is resolved:

- `gtkb-wi6609-membase-connect-time-migration-guard` - `groundtruth-kb/tests/test_db_busy_timeout.py`.
  Its implementation shipped at commit `35c8f8235`; only the spec-derived test is uncommitted. A
  live instance of the WI-5230 class.
- `gtkb-wi6739-state-location-default-deny` - `state_location_registry.py` and
  `test_doctor_state_location_registry.py`.

Verification executed against both scopes: `ruff check` (all passed), `ruff format --check`
(3 files already formatted), `pytest` (20 passed in 2.62s), secret scan (0 findings).

### F6 - [P2] The artifact-head envelope gate applies responder-role semantics to ADVISORY

Evidence. Writing this advisory with `::init gtkb lo` on line 2 was hard-blocked with "bridge
envelope responder-role mismatch for ADVISORY: got 'lo', expected 'pb'" (cited authority:
`ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001`, `DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001`).

Risk and impact. `.claude/rules/file-bridge-protocol.md` defines ADVISORY as "owner-visible
informational input, never assigned or dispatched. Not Prime-actionable and not
Loyal-Opposition-actionable," and non-dispatchable for headless runs. An ADVISORY therefore has no
responder role. Owner confirmation, 2026-08-22: advisories are available to any agent in any role
and are not dispatchable. A gate that requires a specific responder-role token on a
non-dispatchable, unassigned artifact, and reports deviation as a "responder-role mismatch,"
asserts a routing semantic the protocol denies. The practical risk is that agents adopt the gate's
framing over the rule's - which happened in this session - and begin treating advisories as
Prime-assigned work, pushing owner-visible informational input into an actionable queue. The
required `## Recommended Prime Action` section in the ADVISORY template carries the same framing.

Recommended action. Either drop the role token requirement for ADVISORY, or retain the token for
parser uniformity while renaming the check, its failure text, and the template section so none of
them describe a responder or an assignment. Renaming is lower-risk and preserves parser
uniformity; either way the misleading wording should not survive, per the
purge-before-probative-language principle in `.claude/rules/prime-builder.md`.

### F7 - [P2] The documented LO advisory bridge_kind is rejected by the taxonomy enum

Evidence. `.claude/rules/canonical-terminology.md` (glossary entry "Loyal Opposition advisory") and
`.claude/rules/peer-solution-advisory-loop.md` both specify `bridge_kind: loyal_opposition_advisory`.
Filing with that value raised "Invalid bridge_kind: 'loyal_opposition_advisory'. Must be one of
['governance_advisory', 'governance_review', 'implementation_proposal', 'implementation_report',
'index_reconciliation', 'lo_verdict', 'operational_state_change', 'prime_proposal'] per
`DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`." This advisory was filed as `governance_advisory` instead.

Risk and impact. Two always-loaded canonical rule surfaces instruct authors to use a value the
enforcing DCL rejects. An author following the glossary is hard-blocked, and the block text does
not indicate which enum member corresponds to an LO advisory. The glossary is designated the
primary agent-side read path for prior-decision consultation under
`GOV-GLOSSARY-AS-DA-READ-SURFACE-001`, so a wrong value there has outsized reach.

Recommended action. Decide which surface is authoritative and purge the other value: either add
`loyal_opposition_advisory` to `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`, or correct both rule surfaces
to `governance_advisory`. The second is likely correct, since `governance_advisory` is the value
already in use by filed advisories, and it is the smaller change.

## Owner Decision Needed

Per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`, the following must be recorded via AskUserQuestion
before any derived implementation proposal is filed. Implementation is implied: F1 requires
changing `.gitignore`, `_assert_predecessor_chain_committed`, or bridge custody; F2 requires a new
work item plus a gate predicate change; F3 requires gate allow-lists; F4 requires a skill
correction; F6 requires an envelope-gate change; F7 requires a rule or enum correction.

1. Which F1 option is authorized - bounded bridge tracking, relaxed assertion with content-hash
   chain integrity, or deferral to the DATABASE MIGRATION program? The third leaves finalization
   blocked for the duration of that program; is that acceptable?
2. Should F2 be a new work item under Completion Integrity, or folded into WI-6726? Folding risks
   closing WI-6726 while the protected-path consequence stays live.
3. Should finalization be blocked on the governed branch topology (WI-5158, WI-5159), or is a
   documented interim boundary authorized so verified work can drain meanwhile?
4. F3, F6, and F7 change enforcement-gate scope, wording, and vocabulary. Are those authorized, and
   should they land before or after F1?

Required durable owner decisions: the F1 resolution option with rationale; the F2 tracking
disposition; whether interim finalization is authorized ahead of WI-5158 and WI-5159; authorization
to narrow implementation-start-gate and git-lifecycle scope for read-only verbs; authorization to
change or rename the ADVISORY envelope responder-role check and the advisory bridge_kind vocabulary.

No owner approval is requested by this advisory itself.

## Recommended Prime Action

This section is named by the ADVISORY template; see F6 on that naming. It recommends and assigns
nothing - the advisory remains non-dispatchable and unassigned.

After the owner-grilling gate is satisfied, a session holding the Prime Builder role should file a
normal NEW implementation proposal converting F1 only. F2 depends on F1's chosen option and should
follow it. F3, F4, F6, and F7 are independently actionable and need not wait. The two verified
threads named in F5 should be finalized as the first exercise of whatever F1 fix lands, since they
are already verified and their scopes are clean.

## Classification Slot

- F1: adopt
- F2: adopt
- F3: adapt
- F4: adapt
- F5: evidence only, no classification
- F6: adapt
- F7: adapt

## Owner Decisions / Input

- 2026-08-22, AskUserQuestion: owner directed "Remove the lock and clean up the work-tree", then
  selected "Finalize all 12 VERIFIED threads" and "File an ADVISORY bridge entry". The lock removal
  completed (`git_lock_health: PASS`). Finalization could not be completed for the reasons in F1
  and F4; this advisory reports that outcome rather than reducing the approved scope silently.
- 2026-08-22, owner correction in transcript: ADVISORY entries are available to any agent in any
  role and are not dispatchable. Recorded as F6.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
