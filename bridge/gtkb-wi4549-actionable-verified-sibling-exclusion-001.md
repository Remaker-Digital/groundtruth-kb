NEW
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 200d3406-e5ef-442f-9c6a-d034d4acfa47
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory; mode=auto
author_metadata_source: interactive-prime-filing

# WI-4549: Suppress GO proposal threads with a VERIFIED implementation sibling from the prime-actionable surface

Project Authorization: PAUTH-WI-4549-ACTIONABLE-VERIFIED-SIBLING-EXCLUSION
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4549
target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/notify.py", "groundtruth-kb/tests/test_bridge_notify.py"]

## Summary

`compute_actionable_pending` (`groundtruth-kb/src/groundtruth_kb/bridge/notify.py`)
classifies a bridge thread as prime-actionable whenever its top status is `GO`
or `NO-GO`. A recurring false-queue defect (WI-4549) is that umbrella/proposal
threads terminate at `GO` permanently while their implementation work completes
on a separate `-implementation` sibling thread that reaches `VERIFIED`. The
parent `GO` thread then pollutes the prime-actionable surface (~87 entries
observed this session, most already completed via a VERIFIED sibling), forcing
per-session re-audit.

This proposal adds a deterministic, parse-only suppression — a direct parallel
to the existing `_scoping_terminal_with_successor` exclusion — that drops a
thread from the actionable surface when a sibling thread named
`<slug>-implementation` exists at `VERIFIED`.

## Problem (verified against live code)

`compute_actionable_pending` already suppresses one sibling class:
`_scoping_terminal_with_successor` (notify.py ~L286) drops a `-scoping` thread
once its de-suffixed successor exists (WI-3442 + classifier-fix GO -002). The
owner's item-2 case is the symmetric pattern: a proposal thread `<slug>` at `GO`
whose `<slug>-implementation` sibling has reached `VERIFIED`. The `-implementation`
suffix convention is in active use (e.g., `gtkb-project-boundary-and-upgrade-hardening`
and `gtkb-project-boundary-and-upgrade-hardening-implementation`).

Today such a `GO` parent is surfaced as prime-actionable even though its work is
demonstrably complete, because `compute_actionable_pending` keys purely on the
parent thread's own top status and never consults the sibling.

## Proposed change

1. Add a deterministic helper in `notify.py`, mirroring
   `_scoping_terminal_with_successor`:

   ```python
   _IMPLEMENTATION_SUFFIX = "-implementation"

   def _has_verified_implementation_sibling(doc_name, parse_result):
       """Return True if '<doc_name>-implementation' exists at VERIFIED."""
       sibling_name = doc_name + _IMPLEMENTATION_SUFFIX
       for d in parse_result.documents:
           if d.name == sibling_name and d.versions:
               if str(d.versions[0].status.value) == "VERIFIED":
                   return True
       return False
   ```

2. In `compute_actionable_pending`, immediately after the existing
   `_scoping_terminal_with_successor` suppression, add:

   ```python
   if _has_verified_implementation_sibling(doc.name, parse_result):
       continue
   ```

The change is parse-only and deterministic (same `parse_result` + same on-disk
file presence -> same output), preserving the function's documented Audit-only /
checkpoint-free contract. It does not touch dispatch routing, `_derive_dispatchable`,
or any protocol status semantics.

## Specification Links

- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` (v2) — bridge dispatch spawns headless
  instances when actionable work appears; correctly excluding completed work from
  the actionable surface directly serves this ADR's owner-out-of-loop intent.
- `.claude/rules/file-bridge-protocol.md` — actionable-status semantics; `VERIFIED`
  is terminal and non-actionable. This proposal extends "completed work is not
  actionable" to a proposal thread whose implementation sibling is `VERIFIED`.
- `WI-4549` — governing work item (false-queue: GO umbrella/proposal threads
  pollute the prime-actionable surface).
- `WI-3442` (scoping-terminal successor exclusion) and `WI-3276` (WITHDRAWN-status
  exclusion) — direct precedent for parse-only actionable-surface suppression
  implemented under the same principle without a new spec.

Cross-cutting bridge-governance specs (mandatory):

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  every relevant governing specification (concrete links, no TBD placeholders).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied by the spec-to-test
  mapping in the Verification Plan section above.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal is filed through the governed
  append-only numbered bridge-file chain (`bridge/<slug>-NNN.md`), which is the
  canonical bridge-state surface; no aggregate queue artifact is relied upon.

Cross-cutting artifact-governance specs (advisory):

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifact-network framing.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented development decision.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle triggers (this change
  is a reliability fix to an existing module, not a new artifact-lifecycle surface).

## Requirement Sufficiency

Existing requirements sufficient. The fix operationalizes the established
principle that completed work is non-actionable (`.claude/rules/file-bridge-protocol.md`
actionable-status semantics; `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`) and follows
the exact precedent of `_scoping_terminal_with_successor` (WI-3442), which was
implemented as a parse-only actionable-surface refinement without introducing a
new specification. No new or revised requirement is required before implementation.

## Verification Plan (spec-derived tests)

New tests in `groundtruth-kb/tests/test_bridge_notify.py`, executed with
`groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_bridge_notify.py`:

| Requirement clause | Test |
|---|---|
| GO thread with `-implementation` sibling at VERIFIED is excluded from `actionable_for_prime` | `test_go_thread_with_verified_implementation_sibling_suppressed` |
| GO thread whose `-implementation` sibling is NOT yet VERIFIED (NEW/GO) remains actionable | `test_go_thread_with_unverified_implementation_sibling_still_actionable` |
| GO thread with no `-implementation` sibling remains actionable (no over-suppression) | `test_go_thread_without_sibling_unaffected` |
| Existing scoping-terminal and WITHDRAWN/VERIFIED/DEFERRED exclusions unchanged (regression) | existing `test_bridge_notify.py` suite passes |

## Prior Deliberations

- `DELIB-20266109` — owner authorization (AUQ S473) for this proposal setup:
  attach WI-4549 to PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY and mint the covering
  PAUTH.
- `WI-3442` + `bridge/gtkb-axis-2-scoping-terminal-classifier-fix-002` — the
  scoping-terminal successor exclusion this proposal is modeled on.
- `WI-3276` — WITHDRAWN-status exclusion in an actionable-audit script (sibling
  pattern of "exclude terminal/done from actionable").
- `bridge/smart-poller-kind-aware-routing-2026-04-30-009` (REVISED-4) — the
  kind-aware classification governing `compute_actionable_pending` /
  `_derive_dispatchable`; this proposal does not alter it.

## Owner Decisions / Input

This proposal's setup is authorized by owner AskUserQuestion evidence (session
S473), captured as `DELIB-20266109` (`source_type=owner_conversation`,
`outcome=owner_decision`):

- AUQ: "Authorize the item-2 proposal setup so I can draft + file the NEW bridge
  proposal (LO reviews; no implementation by me)?"
- Owner answer: "Authorize — BRIDGE-PROTOCOL-RELIABILITY".

The owner authorized attaching WI-4549 to PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
and minting the covering PAUTH so this NEW proposal can be filed. Implementation
remains gated behind Loyal Opposition `GO` and an implementation-start packet; no
implementation is requested by this proposal.

## Risk / Rollback

- Risk: over-suppression if a `<slug>-implementation` thread reaches VERIFIED
  while genuine residual work remains on the parent `<slug>` thread. Mitigation:
  the suffix match is exact and the VERIFIED check is strict; the parent thread
  remains fully inspectable via `gt bridge show <slug>` and re-surfaces if a new
  actionable version is appended after the sibling's VERIFIED.
- Rollback: revert the single `continue` guard and helper in `notify.py` plus the
  added tests; no schema, state, or protocol migration is involved.

## Acceptance Criteria

1. A GO proposal thread with a `-implementation` sibling at VERIFIED no longer
   appears in `actionable_for_prime`.
2. Threads without such a sibling are unaffected (no over-suppression).
3. The full `test_bridge_notify.py` suite passes (no regression to existing
   scoping-terminal / WITHDRAWN / VERIFIED / DEFERRED exclusions).
4. `ruff check` and `ruff format --check` pass on both changed files.

## Recommended Commit Type

`fix:` — repairs a false-queue defect in the prime-actionable surface; no new
capability surface (a deterministic refinement of existing actionable classification).
