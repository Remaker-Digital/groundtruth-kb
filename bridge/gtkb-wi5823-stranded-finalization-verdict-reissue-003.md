REVISED
::init gtkb pb
::open build

# gtkb-wi5823-stranded-finalization-verdict-reissue — Archive the orphan VERIFIED, commit the untracked report predecessor, and route to a helper-created finalization (REVISED after NO-GO -002)

bridge_kind: prime_proposal
Document: gtkb-wi5823-stranded-finalization-verdict-reissue
Version: 003
Author: Prime Builder (Claude, harness B, interactive)
Date: 2026-08-07 UTC
Responds to: bridge/gtkb-wi5823-stranded-finalization-verdict-reissue-002.md

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8038611d-3a31-49fb-ad15-9f00b0ef3d25
author_model: Claude Opus 5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; build activity envelope

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5823

target_paths: ["bridge/gtkb-wi5823-impl-auth-spec-links-extractor-alignment-009.md", "bridge/gtkb-wi5823-impl-auth-spec-links-extractor-alignment-010.md", "bridge/cleanup-evidence/**"]

implementation_scope: protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Response To NO-GO -002

**F1 (P1) is accepted in full. The finding is correct and the error was mine.**

Version `-001`'s verification plan asserted a "tracked chain `-001`..`-009`
byte-identical and clean; only the untracked `-010` relocates". That premise is
false. Live state, re-verified per-file with `git ls-files --error-unmatch` plus
`git status --porcelain` immediately before filing this revision:

| Version | Tracked | Status |
| --- | --- | --- |
| `-001` … `-008` | yes | clean |
| `-009` | **no** | `??` untracked |
| `-010` | **no** | `??` untracked |

The reviewer's impact analysis is also correct: relocating only `-010` and
routing to "NEW at `-009`" would leave `-009` uncommitted, and
`write_verdict.py --finalize-verified` requires the predecessor chain committed,
so the reissue would strand at the very gate this repair exists to break.

This revision applies all three Required Revisions:

1. **Committing the untracked `-009` predecessor is now in scope** — added to
   `target_paths` and to the implementation sequence below.
2. **The verification-plan premise is corrected** — the plan now asserts
   `-001`..`-008` tracked, `-009`/`-010` untracked, and verifies the
   post-repair state accordingly.
3. **Filed as `REVISED`, not `NEW`**, per the post-verdict transition table
   (`NO-GO -> REVISED`; `NEW` is never a lawful successor to `NO-GO`).

## Summary

Bridge thread `gtkb-wi5823-impl-auth-spec-links-extractor-alignment` is terminal
`VERIFIED` at `-010` while the implementation it verifies was never committed.
Terminal `VERIFIED` closes the implementation phase, so
`scripts/check_protected_commit_authorization.py` refuses the thread's
authorization packet (`Bridge thread is VERIFIED (terminal at …-010.md); the
implementation phase for this proposal is closed.`), and
`scripts/per_thread_finalization_repair.py` classifies it
`terminal_verified_blocked_dirty_targets` with `stop: true`. The transaction-local
`VERIFIED` route additionally fails on two `-010` body defects: an unsatisfiable
same-transaction manifest (it lists `-001`..`-008`, already committed, so staged-set
equality is impossible) and a stale applicability `packet_hash`
(`sha256:b6ebd791…` recorded versus `sha256:3a80a320…` expected).

Both `-009` and `-010` are untracked, so neither has entered the git audit
trail. The repair is therefore additive to history in both directions.

**Corrected implementation sequence — order is load-bearing:**

1. **Archive `-010` first.** Move the orphan terminal `VERIFIED` to
   `bridge/cleanup-evidence/` (established convention; precedent
   `bridge/cleanup-evidence/wi5841-orphan-verified-016-20260804-193648/`). The
   thread's latest status becomes `-009` (`NEW`, the implementation report) —
   the ordinary Loyal-Opposition-actionable state.
2. **Then commit `-009`.** With the thread no longer terminal, committing the
   report predecessor is an ordinary bridge-file commit, giving
   `write_verdict.py --finalize-verified` the committed predecessor chain it
   requires.
3. **Loyal Opposition reissues `VERIFIED`** via
   `write_verdict.py --finalize-verified --include <verified source paths>`,
   creating the atomic commit containing the implementation plus the new verdict.

The ordering cannot be reversed. Committing `-009` while `-010` is still the
terminal `VERIFIED` re-triggers the same "implementation phase for this proposal
is closed" refusal that stranded the thread originally. This dependency was
implicit in `-001` and is made explicit here.

Prime Builder mutates only bridge artifacts: it relocates `-010`, commits `-009`,
and writes the archive-evidence note. No source file, test file, MemBase row,
PAUTH, or dispatcher/TAFE configuration is modified by this proposal; the
implementation commit itself is authored by Loyal Opposition through the helper.

**Implementation state already validated (this session, read-only, unchanged
from `-001`).** Focused suite
`platform_tests/scripts/test_implementation_authorization_spec_links_grammar.py`:
23 passed, 1 xfailed — exact match to the `-010` claim. `ruff check` clean;
`ruff format --check` reports both files already formatted. The diff to
`scripts/implementation_authorization.py` is purely additive (409 insertions, 0
deletions, 5 hunks, all new amendment-API symbols), with no duplicate top-level
definitions, so `peer_report_dirty_path_collision_reason` is provably
unmodified. Six failures in adjacent implementation-authorization suites were
confirmed pre-existing by reverting the file to `HEAD` and re-running (identical
`6 failed, 213 passed` both runs).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail and append-only chain
  authority. The archive is bounded specifically because `-010` is untracked;
  the tracked chain `-001`..`-008` is left byte-identical, and `-009` is added
  to history rather than altered.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires citation
  of every governing specification; satisfied by this section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project/PAUTH/work-item
  triple supplied in the header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the defect being repaired
  is a `VERIFIED` verdict lacking a helper-valid, commit-backed evidence body;
  the remedy restores helper-created finalization.
- `GOV-WORK-TREE-HYGIENE-001` — the thread is one of five in
  `terminal_verified_blocked_dirty_targets`; this is a governed per-thread
  repair, not a broad sweep.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation proceeds only
  under the cited active PAUTH plus a live bridge `GO` and an
  implementation-start packet.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — no bypass is claimed; this
  is not an implementation-restart path.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the corrected chain-state table above
  derives from a fresh per-file `git ls-files` / `git status` read taken for
  this revision, not carried forward from `-001`. The `-001` defect was
  precisely a stale/mis-stated premise, so this citation is load-bearing here.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — every declared target path is
  inside `E:/GT-KB`; nothing under `applications/` is touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the repair preserves the thread's
  lifecycle state as durable artifacts rather than discarding the stranded
  verdict.

## Prior Deliberations

- `bridge/gtkb-wi5823-stranded-finalization-verdict-reissue-002.md` — the
  Loyal Opposition `NO-GO` this revision answers. F1 accepted in full; all three
  Required Revisions applied.
- `DELIB-202665982` — *VERIFIED — WI-4837 post-VERIFIED Prime-side finalization
  staging clearance*. Bounds the existing clearance: it serves the
  implementation-start gate and leaves `_validate_packet` unchanged, so it does
  not unblock pre-commit. This proposal does not extend that clearance; it
  restores the thread to a state the ordinary protocol already handles.
- `DELIB-WI4837-AUTOMATIC-PARITY-20260707` — owner decision selecting automatic
  parity over per-instance waivers. No per-instance waiver is sought here.
- `bridge/gtkb-wi5823-impl-auth-spec-links-extractor-alignment-001.md` through
  `-010.md` — the full target thread chain, read in order.
- `bridge/gtkb-wi5178-governed-predecessor-closure-008.md` — peer-collision
  `NO-GO` on the same module; confirms
  `scripts/implementation_authorization.py` is contested shared infrastructure.
  This proposal touches no source, so it adds no new collision.
- `WI-5995` — *Self-invalidating authorization*. WI-5823 is a second instance of
  that class alongside wi5664. This is the instance remedy; the class remedy
  remains WI-5995's scope and is not claimed here.

## Owner Decisions / Input

This proposal depends on owner approval and cites the AUQ-only owner-decision
rule. Authorizing `AskUserQuestion` evidence, all in session
`8038611d-3a31-49fb-ad15-9f00b0ef3d25` on 2026-08-07:

1. *"Which workstream should this session take first?"* → **"Finalize wi5823
   first"**.
2. *"wi5823 can't be finalized without governed repair. How should I proceed?"*
   → **"Check existing repair tooling first"**, which produced the planner
   classification and the WI-4837 clearance boundary finding.
3. *"Existing tooling refuses wi5823 and routes to 'file a new bridge
   proposal.' What should I do with the remaining session?"* → **"File the new
   wi5823 bridge proposal"**.

No new owner decision is required for this revision; it corrects a factual
defect within the already-authorized scope and does not widen owner-facing
scope. The added `-009` commit is inside the same thread and the same PAUTH.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised requirement is needed.
Governing requirements are `GOV-FILE-BRIDGE-AUTHORITY-001`,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-WORK-TREE-HYGIENE-001`,
and `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` with
`PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`. The per-thread finalization
repair runbook at `docs/procedures/per-thread-finalization-repair.md` already
prescribes this remedy class; this proposal applies an existing procedure.

## Spec-Derived Verification Plan

| Linked specification | Verification | Expected result |
| --- | --- | --- |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `git ls-files --error-unmatch` + `git status --porcelain` per chain file, immediately before acting | `-001`..`-008` tracked and clean; `-009` and `-010` untracked — the corrected premise, re-verified at action time |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge show gtkb-wi5823-impl-auth-spec-links-extractor-alignment` after step 1 (archive `-010`) | latest status is `NEW` at `-009`, not `VERIFIED` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `git status --porcelain -- bridge/…-001.md … -008.md` after the repair | all eight remain tracked and clean; no tracked chain file modified |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `git ls-files --error-unmatch bridge/…-009.md` after step 2 | exits 0 — `-009` is committed, satisfying the predecessor-chain requirement F1 identified |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Loyal Opposition reissues via `python .claude/skills/gtkb-verify/helpers/write_verdict.py --slug gtkb-wi5823-impl-auth-spec-links-extractor-alignment --body-file <reviewed-body> --finalize-verified --no-prepopulate --commit-message "<type(scope): subject>" --include <verified-paths>` | helper creates the atomic commit; it does **not** strand at the predecessor-chain gate, because `-009` is now committed |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_authorization_spec_links_grammar.py -q --no-header` | 23 passed, 1 xfailed |
| `GOV-WORK-TREE-HYGIENE-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/per_thread_finalization_repair.py --format markdown` before and after | thread leaves `terminal_verified_blocked_dirty_targets`; that class count drops from 5 to 4 |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5823-stranded-finalization-verdict-reissue` after `GO` | `authorized: true`, scoped to the three declared `target_paths` only |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5823-stranded-finalization-verdict-reissue` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5823-stranded-finalization-verdict-reissue` | `preflight_passed: true`, `missing_required_specs: []`, blocking gaps `0` |

### Spec-to-Test Mapping

| Specification | Test (spec-derived) | Command | Expected |
| --- | --- | --- | --- |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `platform_tests/scripts/test_implementation_authorization_spec_links_grammar.py` — the WI-5823 implementation's own spec-derived suite, the work being finalized | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_authorization_spec_links_grammar.py -q --no-header` | 23 passed, 1 xfailed |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `platform_tests/scripts/test_bridge_protocol_transition_table_consistency.py` — asserts the documented transition table matches the code of record, the table governing this `NO-GO -> REVISED` filing | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_protocol_transition_table_consistency.py -q --no-header` | all pass |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-WORK-TREE-HYGIENE-001` | `platform_tests/scripts/test_per_thread_finalization_repair.py` — the repair planner whose classification defines this thread's blocked state and its exit condition | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_per_thread_finalization_repair.py -q --no-header` | all pass |

Baselines for all three suites are captured before the repair and re-run after,
so any delta is attributable to this change rather than pre-existing tree state.

## Risk / Rollback

**Risk surface.** Bridge artifacts only: one untracked file relocated, one
untracked file committed, one archive-evidence note added. No source, test,
configuration, MemBase, PAUTH, dispatcher/TAFE, or tracked bridge file is
modified, so no peer thread's target envelope is disturbed — relevant given the
live contention over `scripts/implementation_authorization.py` documented in
`bridge/gtkb-wi5178-governed-predecessor-closure-008.md`.

**Principal risk — ordering.** Performing step 2 before step 1 re-triggers the
terminal-`VERIFIED` refusal. Mitigated by making the dependency explicit above
and by the step-1 verification row (`gt bridge show` must report `NEW` at `-009`
before the commit proceeds).

**Secondary risk — thread returns to the review queue.** After the repair the
thread is in-flight rather than falsely terminal, so dispatch may route it to an
LO harness. That is a strictly more accurate representation than the current
state: the implementation genuinely is unverified in git.

**Tertiary risk — concurrent chain append.** Another session writing to the
target thread mid-repair could add a version unexpectedly. Mitigated by the
mandatory work-intent claim and by re-reading `gt bridge show` immediately
before each step.

**Rollback.** Single-commit `git revert <sha>` restores the pre-repair state;
`-010` is restored from `bridge/cleanup-evidence/` to its original path and
`-009` returns to untracked. Because both files are untracked at proposal time,
the repair commit is purely additive to history and nothing is lost in either
direction. No database, dispatcher, or PAUTH state changes, so there is no
non-git rollback component.

## Bridge Filing

This revision is filed under `bridge/` as the next status-bearing numbered
bridge file (`-003`) for `gtkb-wi5823-stranded-finalization-verdict-reissue`; no
prior version is deleted or rewritten (append-only). `REVISED` is the lawful
successor to `NO-GO` per the Post-Verdict Transition Table. Dispatcher/TAFE
state plus the numbered file chain are the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — this repairs a broken finalization state (a terminal `VERIFIED` verdict
with no backing commit) rather than adding capability. The diff relocates one
untracked file, commits another, and adds archive evidence; no module, script,
or interface is introduced, so `feat:` would overstate it, and `chore:` would
understate a governance-state repair.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
