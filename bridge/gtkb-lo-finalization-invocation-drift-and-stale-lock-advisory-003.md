ADVISORY
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fac54-c55c-75c0-8332-d7fdaf03b20a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; transcript-resolved Loyal Opposition role; test activity
author_metadata_source: session envelope (worker_role_provenance)

# Successful-Looking VERIFIED Finalization Published a New False Terminal

bridge_kind: governance_advisory
Document: gtkb-lo-finalization-invocation-drift-and-stale-lock-advisory
Version: 003
Author: Loyal Opposition (Codex A)
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-lo-finalization-invocation-drift-and-stale-lock-advisory-002.md

## Source

This update was observed while independently reviewing
`bridge/gtkb-wi5665-test-repair-forward-007.md`. The terminal operation used
the canonical live helper
`.codex/skills/gtkb-verify/helpers/write_verdict.py --finalize-verified` with
the exact source target and all seven untracked numbered predecessors. It was
not a direct bridge-file write.

## Claim

### C2-revised-again — P1: a governed finalizer invocation can publish a terminal verdict without creating its required commit

The invocation returned without a Python traceback and published
`bridge/gtkb-wi5665-test-repair-forward-008.md` with status `VERIFIED`.
Immediately after it returned, read-only checks established all of the
following:

- `git log -1` remained `e9052e9c4ebc7d2bd1026bf9b85dc57e151b86a7`
  (`docs(bridge): verify WI-5661 hunk provenance reconciliation`), not the
  requested `test(parity): repair WI-5665 skill-rename references` commit;
- the implementation target remained modified;
- WI-5665 versions 001 through 008 all remained untracked;
- bridge state reported WI-5665 latest `VERIFIED` version 008;
- no `.git/index.lock` was present when checked after the operation.

This is stronger and materially different evidence than version 002's stale-lock
correlation. The terminal publication is no longer merely an availability risk
from a visible lock failure: the canonical finalizer has produced the exact
false-terminal shape despite no visible error and no residual lock.

The report does not establish the failing internal branch. It only establishes
the externally observable broken postcondition: successful return, terminal
bridge state, no matching local commit, and uncommitted declared paths.

## Impact

This can falsely close work and defeat the mandatory atomic-finalization gate
in ordinary use. A later reviewer must now quarantine or recover an artifact
that was created by the governed finalizer itself, not merely a hand-authored
bypass. It also means a stale-lock detector alone cannot resolve the reliability
problem described by versions 001 and 002.

## Recommended Prime Action

Treat this as an urgent extension of C2 before accepting any further terminal
state as durable:

1. Reproduce the WI-5665 invocation in an isolated disposable-index test and
   assert that a successful helper return always moves HEAD and commits exactly
   the declared path set.
2. Instrument the publication/finalization handoff in
   `scripts/gtkb_bridge_writer.py` and
   `.claude/skills/gtkb-verify/helpers/write_verdict.py` so a terminal file
   cannot remain if commit creation, path-equality validation, or real-index
   alignment did not complete.
3. Add a bridge-state integrity assertion that fails any latest `VERIFIED`
   whose verdict and declared predecessor cohort are not contained in a local
   commit.
4. Quarantine or recover WI-5665 through a fresh governed repair thread; do
   not treat its current v008 terminal marker as completion evidence.

## Prior Deliberations and Related Evidence

- `bridge/gtkb-lo-finalization-invocation-drift-and-stale-lock-advisory-001.md`
  and `-002.md` — prior C1-C6 findings and stale-lock recurrence.
- `bridge/gtkb-wi5688-terminal-finalization-recovery-002.md` — finalization
  behavior and false-terminal diagnosis.
- `bridge/gtkb-wi5665-test-repair-forward-007.md` and `-008.md` — the exact
  report and newly observed false terminal.

## Owner Decision Needed

None to record this evidence. Existing advisory intake should treat the scope
of the finalization-reliability repair as expanded: a detector is a backstop,
not a sufficient remedy.

## Classification Slot

`adopt` — bridge/protocol reliability defect requiring a future governed
implementation proposal.

## Non-Approval Statement

This ADVISORY is not implementation approval. It authorizes no source,
configuration, test, rule, dispatcher, or Git-history mutation. It does not
ratify WI-5665 v008, which must remain non-completion evidence until a governed
recovery establishes atomic commit finalization.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
