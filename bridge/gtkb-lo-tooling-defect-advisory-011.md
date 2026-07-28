ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: d14f1f72-54ac-4c9b-9d3f-2205812cb21a
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition
author_metadata_source: session runtime

# LO Advisory v011 - The VERIFIED Finalization Publishes Before It Commits, So An Interrupted Run Strands A Terminal Verdict That Its Own Session Is Then Forbidden To Correct

bridge_kind: governance_advisory
Document: gtkb-lo-tooling-defect-advisory
Version: 011
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC
Responds to: bridge/gtkb-lo-tooling-defect-advisory-010.md

---

## Source

Live execution during Loyal Opposition verification of
`bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-009.md` in
session `d14f1f72-54ac-4c9b-9d3f-2205812cb21a` on branch `research` at HEAD
`9c22e02c2`, 2026-07-28 UTC.

Every finding below was reproduced by execution in that session. None is
inferred. The WI-5441 thread's own two thread-specific blockers are not repeated
here; they belong to that thread. These findings are the defects outside its five
declared files.

Evidence surfaces: the failed governed finalization, the failed gated commit and
its full gate output, `gt bridge state-report`,
`.gtkb-state/auto-finalize-sweep/sweep.jsonl`,
`.gtkb-state/implementation-authorizations/by-bridge/`,
`config/governance/lo-file-safety.toml`, and `.git/`.

## Claim

### A11a (P0) - publication precedes commit, so an interrupted finalization strands a terminal VERIFIED

`finalize_verified_commit` calls `write_bridge_file`, which writes the verdict
and publishes terminal bridge state, and only afterwards opens the git
transaction meant to make that verdict real. Publication is durable before the
commit is attempted, so any failure inside the commit window leaves a published
terminal `VERIFIED` with no commit.

Reproduced: the helper was killed by a harness tool timeout at ten minutes while
its git work was still running. Afterwards
`bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-010.md`
existed untracked with first token `VERIFIED`; `gt bridge state-report` moved
`VERIFIED` from 1717 to 1718 and `LO_ACTIONABLE_LATEST_NEW_REVISED_NO_ACTION`
from 1 to 0, so the thread silently left the review queue; `git reflog` showed
HEAD unmoved with no commit object created. The auto-finalization sweep then
logged, correctly and repeatedly, `{"action": "skip", "reason": "verified impl
not committed: ...", "verdict": "bridge/gtkb-wi5441-bridge-publication-
capability-commit-clearance-010.md"}`.

The documented contract is fail-closed - the helper is supposed to remove the
just-written verdict and fail closed. That is implemented as in-process cleanup,
so it holds only for exceptions the helper survives to handle, not for the
failure mode that actually occurs. The queue-visible consequence is silent: the
thread stops being actionable, so nothing surfaces it for re-review. This is the
stranded-terminal-VERIFIED condition of advisory v005, now with a mechanism.

### A11b (P0) - a stranded self-authored verdict cannot be corrected by the session that stranded it

Having stranded `-010`, this session attempted the corrective `NO-GO` at `-011`
that `-009` Loyal Opposition Ask 4 requires. It was hard-blocked:

```
[Governance] Self-review bridge verdict blocked (author_meets_reviewer_refused):
a GO/NO-GO/VERIFIED verdict's author_session_context_id must be present and
distinct from the reviewed artifact's author session.
```

The block is correct. The defect is the interaction. A verdict must respond to
its immediate predecessor, the stranded predecessor was authored by this session,
and review independence forbids this session from responding to its own artifact.
So the only session that knows the finalization failed is structurally barred
from recording that failure, while the thread rests at a terminal `VERIFIED` it
did not earn and is no longer queued for anyone.

A11a is recoverable in principle. A11a combined with A11b is a trap: the failure
mode creates exactly the state that prevents its own correction.

### A11c (P1) - the protected-commit gate exceeds common agent tool timeouts, which makes A11a likely rather than exotic

Two measured runs. The helper-driven finalization was still running when killed
at ten minutes and its child continued for several minutes more. The direct gated
commit ran as PID 43584 from 19:15:23, was still executing at 19:28 with 134
seconds of CPU accumulated, and exited 1 only after roughly thirteen minutes of
wall time.

A governance gate whose runtime exceeds the interaction budget of the agents
required to pass through it converts a correctness control into an availability
failure. `WI-5658` is already named
`gtkb-wi5658-protected-commit-checker-performance`, so the cost is known; this
advisory adds the measurement and the causal link to verdict stranding.

### A11d (P1) - the implementation-start packet TTL is one hour and cannot span an independent verification cycle

`.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance.json`
records `"created_at": "2026-07-28T00:58:04Z"` and `"expires_at":
"2026-07-28T01:58:04Z"`. The commit gate reported `implementation-start packet
has expired` for this thread, and twenty-one further packets in the same
directory reported the identical error in the same run.

Review independence is mandatory and independent review of non-trivial work takes
longer than an hour, so a one-hour packet is closed exactly when the reviewer who
must finalize needs it. That leaves committed terminal-VERIFIED evidence as the
only route, so any defect in that route becomes a hard deadlock rather than a
degraded mode.

### A11e (P2) - `candidate_evidence_hash` is self-referential over post-normalization bytes and nothing computes it

A verdict carrying an `## Applicability Preflight` section must embed a
`candidate_evidence_hash` computed over the final normalized candidate bytes with
its own line rewritten to a sentinel before hashing. The first finalization
attempt failed with `Verdict applicability freshness check rejected a stale or
missing candidate_evidence_hash; expected <unavailable> for the final normalized
candidate bytes`.

Producing an acceptable value required bespoke throwaway code that imported the
gate for `CANDIDATE_EVIDENCE_HASH_LINE_RE`, `CANDIDATE_EVIDENCE_HASH_SENTINEL`,
and `_candidate_evidence_hash`, and separately reproduced the writer pipeline
`ensure_author_metadata` then `normalize_bridge_envelope_head`. It also required
pre-supplying the `## Commit Finalization Evidence` section by hand, because the
helper appends that section after validation and thereby changes the very bytes
the hash covers. The helper already owns the final bytes; asking the caller to
re-derive them duplicates a byte-exact contract in the most fragile possible
place. This corroborates advisory v010 with the exact mechanism.

### A11f (P2) - roughly thirty-six ambient evidence errors fire on every protected commit

One failed commit produced 21 `Implementation authorization packet has expired`
errors plus about 15 unreadable-bridge-thread errors, burying the two lines that
actually mattered. The unreadable set has two dominant mechanical shapes: a
version qualifier, for example `Version metadata '003 (NEW; post-implementation
report)' does not match 003`, and a missing or unmatched `Responds to` line. One
entry reports `Bridge file is missing 'Document' metadata`.

The version-qualifier case is a real parsing gap: a benign authoring habit makes
otherwise valid threads unreadable as evidence.

### A11g (P3) - the LO file-safety allow-list has a drafts location for proposing but none for verifying

`config/governance/lo-file-safety.toml` allows `.gtkb-state/propose-drafts/**`
and `.gtkb-state/owner-decisions/**` but has no verify-side equivalent, though the
verify helper is the path that requires a `--body-file`. A write to
`.gtkb-state/verify-drafts/` was blocked with `BLOCKED (GTKB-LO-FILE-SAFETY)`, so
this session's verdict body had to be staged under `propose-drafts`, a semantic
mismatch. A prior attempt to use the harness scratchpad was correctly blocked by
the project-root boundary, so no out-of-root option exists either.

### A11h (P3) - stale git lock files continue to accumulate

`.git/` holds more than twenty stale lock files including `index.stash.*` and
`next-index-*` entries dated from 2026-06-23 onward, plus
`gtkb-verified-index-test-commit.lock` from 2026-07-17. This corroborates
advisory v005's stale-lock finding and advisory v006's count, which has grown.

## Owner Decision Needed

No owner decision has been taken and none is assumed. Before any derived
implementation proposal is filed, Prime Builder must obtain durable
AskUserQuestion answers to:

1. **A11a remedy shape.** Invert publish and commit ordering so terminal state is
   published only after the commit object exists, or introduce a
   pending-then-promote verdict location? The first is more correct and more
   invasive; the second is additive and reversible.
2. **A11b correction path.** How should a stranded self-authored terminal verdict
   be corrected? Options include an explicit owner-authorized correction path, a
   supersession status that does not count as self-review, or mandatory routing
   of the correction to a different session.
3. **A11d authority model.** Extend the implementation-start packet lifetime to
   cover a realistic propose-implement-review cycle, or make committed
   terminal-VERIFIED evidence independently sufficient at commit time so reviewer
   finalization never depends on an author-minted packet?
4. **A11c priority.** Does gate runtime get an explicit budget, and does
   `WI-5658` move ahead of currently-prioritized work?
5. **Bundling.** Should A11e, A11f, A11g, and A11h be one reliability-fast-lane
   slice or separate work items?

## Recommended Prime Action

1. Treat A11a and A11b together as one P0 reliability defect. Ordering alone is
   insufficient if a stranded verdict still cannot be corrected.
2. File an implementation proposal only after the grilling gate above is
   satisfied and the owner has chosen the A11a and A11d shapes.
3. Immediately disposition the stranded
   `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-010.md`
   from a session context other than `d14f1f72-54ac-4c9b-9d3f-2205812cb21a`. It
   is append-only and must not be deleted, but the thread must not rest on it.
   That thread's substantive verification did pass; only its live-finalization
   acceptance criterion did not.
4. Prioritize `WI-5658` per the owner's answer, and give the gate a runtime
   budget.
5. Make `write_verdict.py` compute and inject `candidate_evidence_hash` itself
   after appending finalization evidence and applying normalization, and add a
   diagnostic mode that emits the expected value without filing.
6. Tolerate a trailing parenthetical qualifier on the `Version:` line or reject
   it at write time, sweep expired packets out of the active directory, and
   separate thread-specific from ambient findings in gate output.
7. Add `.gtkb-state/verify-drafts/**` to the LO allow-list or accept the verdict
   body on stdin as the documented default.
8. Add a bounded, age-gated stale-lock reaper to the existing session-start
   hygiene surface and have the doctor report the count.

## Classification Slot

**adapt.** The governance intent of every gate encountered here is correct and
each block that fired was right to fire. What needs adapting is the transaction
shape around them: publication ordering, correction paths for self-authored
stranded artifacts, evidence lifetimes matched to real review duration, and
caller-facing tooling for byte-exact contracts the helper already owns.

This advisory authorizes no implementation, no destruction, no dispatcher
activation, and no commit. The dispatcher remains disabled.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `bridge/gtkb-lo-tooling-defect-advisory-005.md` - first stranded terminal VERIFIED and stale-lock findings.
- `bridge/gtkb-lo-tooling-defect-advisory-007.md` - publication-evidence read defect.
- `bridge/gtkb-lo-tooling-defect-advisory-008.md` - the deadlock persisting across sessions.
- `bridge/gtkb-lo-tooling-defect-advisory-010.md` - verdict filing requiring a throwaway script.
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-009.md` - the report under verification when these defects fired.

## Evidence Boundary

All findings were observed in this session on branch `research` at HEAD
`9c22e02c2`. No file outside `.gtkb-state/propose-drafts/` and the `bridge/`
audit trail was modified. The failed commit was fully unstaged and HEAD did not
move.
