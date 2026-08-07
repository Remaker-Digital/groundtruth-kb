NEW
::init gtkb pb
::open build

# gtkb-wi5823-stranded-finalization-verdict-reissue — Archive the orphan WI-5823 VERIFIED verdict and route the thread back to a helper-created finalization

bridge_kind: prime_proposal
Document: gtkb-wi5823-stranded-finalization-verdict-reissue
Version: 001
Author: Prime Builder (Claude, harness B, interactive)
Date: 2026-08-07 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8038611d-3a31-49fb-ad15-9f00b0ef3d25
author_model: Claude Opus 5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; build activity envelope

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5823

target_paths: ["bridge/gtkb-wi5823-impl-auth-spec-links-extractor-alignment-010.md", "bridge/cleanup-evidence/**"]

implementation_scope: protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Bridge thread `gtkb-wi5823-impl-auth-spec-links-extractor-alignment` is terminal
`VERIFIED` at `-010`, but the implementation it verifies was never committed. The
`-010` verdict was authored without the atomic finalization commit that the
Mandatory VERIFIED Commit-Finalization Gate requires, so the thread reached a
terminal state while its target paths stayed dirty. That produces a closed loop
no existing surface can break:

- `scripts/check_protected_commit_authorization.py` refuses the thread's
  implementation-authorization packet with `Bridge thread is VERIFIED (terminal
  at bridge/gtkb-wi5823-impl-auth-spec-links-extractor-alignment-010.md); the
  implementation phase for this proposal is closed.`
- `scripts/per_thread_finalization_repair.py` classifies the thread
  `terminal_verified_blocked_dirty_targets` with `stop: true`, reason
  `implementation/report target paths are still dirty or untracked`, and its
  runbook forbids finalizing any class other than
  `terminal_verified_repair_candidate`.
- The WI-4837 post-`VERIFIED` clearance
  (`finalization_target_paths_for_verified`) does not apply: it feeds the
  implementation-start gate, and its own docstring states `_validate_packet`
  behavior is intentionally unchanged, so terminal `VERIFIED` remains terminal
  for ordinary packets at pre-commit time.

The remaining sanctioned route the pre-commit gate names — transaction-local
`VERIFIED` evidence — fails on two defects that are properties of the `-010`
body itself and cannot be fixed by staging differently:

1. **Unsatisfiable manifest equality.** `-010`'s `## Commit Finalization
   Evidence` declares a same-transaction set of all thirteen chain paths,
   including `-001` through `-008`, which are already committed at
   `629fead8c`'s ancestry. Git cannot stage an unchanged tracked file, so the
   gate's staged-set equality check can never hold. Observed gate output:
   `same-transaction manifest does not equal the staged path set; extra=[...-001.md ... -008.md]`.
2. **Stale applicability packet hash.** `-010` records
   `packet_hash: sha256:b6ebd791b317d5f1fdbf01cb36bd32ffab67685f75ab596ca6e51e8ed30d7159`;
   the gate's freshness check expects
   `sha256:3a80a320ceaefa20f1aa851a6325341fb2f328c1cf20a9674a4f1cc1aa2118be`
   for `-009`, and rejects the verdict as stale.

This proposal applies the remedy the per-thread finalization runbook prescribes
for a terminal `VERIFIED` body that fails the finalizer's validation floor:
route through a bounded archive repair and have Loyal Opposition reissue
`VERIFIED` through `write_verdict.py --finalize-verified` with a helper-valid
body.

The decisive enabling fact is that `-010` is **untracked**. It has never entered
the git audit trail, so archiving it removes nothing from history. Once `-010`
is archived, the thread's latest status reverts to `-009` (`NEW`, the
implementation report), which is exactly the Loyal-Opposition-actionable state
the ordinary protocol handles. Loyal Opposition then issues `VERIFIED` through
the finalization helper, which creates the atomic commit containing the verified
implementation paths plus the new verdict — closing the thread correctly instead
of leaving it terminal-but-unfinalized.

Scope is deliberately narrow. Prime Builder mutates exactly two things: it moves
`bridge/gtkb-wi5823-impl-auth-spec-links-extractor-alignment-010.md` into
`bridge/cleanup-evidence/`, and it writes the accompanying archive-evidence note.
No source file, test file, MemBase row, PAUTH, dispatcher/TAFE configuration, or
tracked bridge file is modified by this proposal. The eventual finalization
commit is authored by Loyal Opposition through the helper, not by Prime Builder.

**Precedent.** The archive convention already exists in-tree:
`bridge/cleanup-evidence/wi5841-orphan-verified-016-20260804-193648/` is a prior
orphan-`VERIFIED` archive of the same shape, surfaced by the finalization repair
planner. This proposal follows that established directory pattern.

**Implementation state already validated (this session, read-only).** The
wi5823 implementation is correct and ready; only its finalization is stranded.
Evidence reproduced against live state:

- Focused suite `platform_tests/scripts/test_implementation_authorization_spec_links_grammar.py`:
  23 passed, 1 xfailed — an exact match to the `-010` verdict's recorded claim.
- `ruff check` clean; `ruff format --check` reports both files already formatted.
- The diff to `scripts/implementation_authorization.py` is purely additive:
  409 insertions, 0 deletions across 5 hunks, all new amendment-API symbols
  (`create_proposal_amendment`, `_amendment_equivalence`, `load_proposal_amendment`,
  and helpers). No duplicate top-level definitions exist in the module, so no
  existing symbol is shadowed and the `cross_claim_path_collision_reason` /
  `peer_report_dirty_path_collision_reason` logic that peer threads depend on is
  provably unmodified.
- Six failures in `test_implementation_start_gate.py`,
  `test_work_intent_auto_extend.py`, and
  `test_worker_packet_authorization_envelope.py` were confirmed **pre-existing**
  by reverting `scripts/implementation_authorization.py` to `HEAD` and re-running:
  identical `6 failed, 213 passed` in both runs. They are not regressions from
  WI-5823 and are out of scope here.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs the bridge audit trail and the
  append-only numbered chain. The archive step is bounded specifically because
  `-010` is untracked and therefore not yet part of that trail; the tracked
  chain `-001` through `-009` is left byte-identical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this
  proposal to cite every governing specification; satisfied by this section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the
  project/PAUTH/work-item triple; supplied in the header and validated read-only
  against MemBase by `scripts/gtkb_propose_scaffold.py`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the defect being repaired
  is precisely a `VERIFIED` verdict that did not carry a helper-valid,
  commit-backed evidence body; the remedy restores helper-created finalization.
- `GOV-WORK-TREE-HYGIENE-001` — the thread is one of five in
  `terminal_verified_blocked_dirty_targets`; this repair reduces stranded
  worktree state through a governed path rather than a broad sweep.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation proceeds only
  under the cited active PAUTH plus a live bridge `GO` and an
  implementation-start packet.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — this proposal is not an
  implementation-restart path and claims no bypass; it requires independent `GO`
  before any mutation.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — every state claim above derives from
  fresh canonical reads (`gt bridge show`, `git status`, live planner and gate
  runs), not cached summaries.

## Prior Deliberations

- `DELIB-202665982` — *VERIFIED — WI-4837 post-VERIFIED Prime-side finalization
  staging clearance*. Establishes the existing post-`VERIFIED` clearance and,
  critically, bounds it: the clearance serves the implementation-start gate and
  leaves `_validate_packet` unchanged. This proposal builds on that boundary
  rather than contradicting it — it does not extend the clearance, it restores
  the thread to a state the ordinary protocol already handles.
- `DELIB-WI4837-AUTOMATIC-PARITY-20260707` — the owner decision selecting
  automatic parity over per-instance waivers for finalization clearance. This
  proposal seeks no per-instance waiver, consistent with that decision.
- `bridge/gtkb-wi5823-impl-auth-spec-links-extractor-alignment-001.md` through
  `-010.md` — the full thread chain, read in order before drafting.
- `bridge/gtkb-wi5178-governed-predecessor-closure-008.md` — the peer-collision
  `NO-GO` precedent on the same module. Relevant because it confirms
  `scripts/implementation_authorization.py` is contested shared infrastructure;
  this proposal touches no source and so adds no new collision.
- `WI-5995` — *Self-invalidating authorization*, opened for the wi5664 case
  where a recovery transaction detached the project membership its own PAUTH
  required. WI-5823 is a second instance of that class: reaching `VERIFIED`
  closed the implementation phase its own finalization commit depended on. This
  proposal is the instance remedy; the class remedy remains WI-5995's scope and
  is explicitly **not** claimed here.

## Owner Decisions / Input

This proposal depends on owner approval and cites the AUQ-only owner-decision
rule. The authorizing `AskUserQuestion` evidence, all captured in session
`8038611d-3a31-49fb-ad15-9f00b0ef3d25` on 2026-08-07:

1. *"Which workstream should this session take first?"* → **"Finalize wi5823
   first"**. Authorized the finalization work and its scoped commit.
2. *"wi5823 can't be finalized without governed repair. How should I proceed?"*
   → **"Check existing repair tooling first"**. Directed the read-only
   investigation that produced the planner classification and the WI-4837
   clearance boundary finding recorded above.
3. *"Existing tooling refuses wi5823 and routes to 'file a new bridge
   proposal.' What should I do with the remaining session?"* → **"File the new
   wi5823 bridge proposal"**. Directly authorizes filing this proposal.

No further owner decision is required to review this proposal. Owner approval
for the archive mutation itself is carried by the active PAUTH plus the
independent `GO` this proposal requests.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised requirement is needed
before implementation. The governing requirements are
`GOV-FILE-BRIDGE-AUTHORITY-001` (audit-trail and chain authority),
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (helper-created,
commit-backed `VERIFIED` evidence), `GOV-WORK-TREE-HYGIENE-001` (governed
reduction of stranded worktree state), and
`GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` with
`PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` (authorization chain). The
per-thread finalization repair runbook at
`docs/procedures/per-thread-finalization-repair.md` already prescribes this
remedy for a terminal `VERIFIED` body that fails the finalizer's validation
floor; this proposal applies an existing procedure rather than defining new
policy.

## Spec-Derived Verification Plan

| Linked specification | Verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `git status --short -- bridge/gtkb-wi5823-impl-auth-spec-links-extractor-alignment-001.md ... -009.md` before and after the archive | tracked chain `-001`..`-009` byte-identical and clean; only the untracked `-010` relocates |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge show gtkb-wi5823-impl-auth-spec-links-extractor-alignment` after the archive | latest status is `NEW` at `-009` (Loyal-Opposition-actionable), not `VERIFIED` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Loyal Opposition reissues via `python .claude/skills/gtkb-verify/helpers/write_verdict.py --slug gtkb-wi5823-impl-auth-spec-links-extractor-alignment --body-file <reviewed-body> --finalize-verified --no-prepopulate --commit-message "<type(scope): subject>" --include <verified-paths>` | helper creates the atomic commit; `git log` shows one commit containing the verified paths plus the new verdict |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_authorization_spec_links_grammar.py -q --no-header` | 23 passed, 1 xfailed (unchanged from the `-010` claim) |
| `GOV-WORK-TREE-HYGIENE-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/per_thread_finalization_repair.py --format markdown` before and after | `gtkb-wi5823-impl-auth-spec-links-extractor-alignment` leaves the `terminal_verified_blocked_dirty_targets` class; `terminal_verified_blocked_dirty_targets` count drops from 5 to 4 |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5823-stranded-finalization-verdict-reissue` after `GO` | `authorized: true` scoped to the two declared `target_paths` only |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | re-run `gt bridge state-report` and the applicability preflight immediately before acting | live state matches the claims in this proposal at action time |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5823-stranded-finalization-verdict-reissue` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5823-stranded-finalization-verdict-reissue` | `preflight_passed: true`, `missing_required_specs: []`, blocking gaps `0` |

## Risk / Rollback

**Risk surface.** Small and bounded. The only mutated artifacts are one
untracked bridge file and a new archive directory under
`bridge/cleanup-evidence/`. No source, test, configuration, MemBase, PAUTH,
dispatcher, or tracked bridge file is touched, so no peer thread's target
envelope is disturbed — relevant because
`bridge/gtkb-wi5178-governed-predecessor-closure-008.md` shows several live
threads already contending over `scripts/implementation_authorization.py`.

**Principal risk.** Relocating `-010` moves the thread from terminal back to
`NEW` at `-009`, returning it to the Loyal Opposition actionable queue. If
Loyal Opposition does not subsequently reissue `VERIFIED`, the thread is
in-flight rather than falsely terminal. That is a strictly more accurate
representation of reality than the current state — the implementation genuinely
is unverified-in-git — but it does mean the thread reappears as open review
work, and dispatch may route it to an LO harness.

**Secondary risk.** If another session concurrently writes to this thread while
the archive is in progress, the chain could gain a version unexpectedly. Mitigated
by the mandatory work-intent claim and by re-reading `gt bridge show` immediately
before acting.

**Rollback.** Single-commit rollback: `git revert <sha>` restores the archive
directory state, and `-010` is restored from `bridge/cleanup-evidence/` to its
original path. Because `-010` is untracked at proposal time, the archive commit
is purely additive to history and nothing is lost in either direction. No
database, dispatcher, or PAUTH state changes, so there is no non-git rollback
component.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5823-stranded-finalization-verdict-reissue`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — this repairs a broken finalization state (a terminal `VERIFIED` verdict
with no backing commit) rather than adding capability. The diff relocates one
untracked file and adds archive evidence; no new module, script, or interface is
introduced, so `feat:` would overstate it, and `chore:` would understate a
governance-state repair.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
