NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 75cea783-a1f3-4f8b-b834-cca62d92299c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal

# gtkb-phase-y-loop-probe — PHASE-Y synthetic throwaway probe to exercise the live dispatcher-daemon PB/LO loop end-to-end

Document: gtkb-phase-y-loop-probe
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-27 UTC
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4879
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-PHASE-Y-SYNTHETIC-LOOP-PROBE
Recommended commit type: test

target_paths: ["groundtruth-kb/src/groundtruth_kb/_phase_y_loop_probe.py", "groundtruth-kb/tests/test_phase_y_loop_probe.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This is a deliberately trivial, self-contained, zero-owner-decision synthetic probe whose sole purpose is to be driven through the now-live dispatcher-daemon bridge loop end-to-end (PB files NEW, the daemon dispatches Cursor-E Loyal Opposition review to GO, a headless Prime Builder worker implements and files the post-implementation report, Cursor-E verifies to VERIFIED and commits). It is the PHASE-Y acceptance test for the dispatcher daemon as the live spawn authority per `DELIB-20266272`. The artifacts are throwaway and carry no production behavior; they are safe to retire after the loop demonstration.

### Implementation (precise, unambiguous)

Add one new module `groundtruth-kb/src/groundtruth_kb/_phase_y_loop_probe.py` containing a module docstring that marks it a throwaway PHASE-Y daemon-loop probe (filed under WI-4879 / `DELIB-20266272`), a `from __future__ import annotations` line, and exactly one pure function `phase_y_probe_sum(a: int, b: int) -> int` whose body is `return a + b` with a short docstring. No imports beyond `__future__`; no side effects; no I/O.

Add one new test module `groundtruth-kb/tests/test_phase_y_loop_probe.py` that imports the function via `from groundtruth_kb._phase_y_loop_probe import phase_y_probe_sum` and asserts three cases: `phase_y_probe_sum(2, 3) == 5`, `phase_y_probe_sum(0, 0) == 0`, and `phase_y_probe_sum(-4, 1) == -3`.

The implementation is fully determined by this specification; there is no design latitude. A correct implementation is unambiguous and trivially verifiable.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this proposal is filed as the next numbered bridge file (`bridge/gtkb-phase-y-loop-probe-001.md`) in the append-only versioned bridge chain, and the implementation report and verdict will follow as later numbered versions of this thread.
- `ADR-DISPATCHER-ARCHITECTURE-001` — the dispatcher architecture decision this go-live probe exercises; the probe is the acceptance test for the dispatcher daemon as live spawn authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: this section cites the governing specs and the tests are mapped below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: WI-4879 + PROJECT-GTKB-DISPATCHER-RELIABILITY + active PAUTH metadata are present in the header block.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: the function behavior maps to the derived tests in the verification plan below.
- `GOV-STANDING-BACKLOG-001` — WI-4879 is an authorized standing-backlog item under the active project authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the probe is captured as durable artifacts (WI-4879, this bridge thread, the derived test) rather than transient chat work.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the work is tracked as a network of durable artifacts (work item, bridge thread, test) per the artifact-oriented development decision.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — the throwaway artifacts carry an explicit lifecycle disposition (safe to retire after the loop demonstration); their creation is a backlog/work-item-triggered artifact event.

## Prior Deliberations

- `DELIB-20266272` — Owner AUQ (S20260627): "Full daemon go-live (goal as written)"; explicitly authorizes filing a synthetic throwaway proposal (trivially correct, zero owner decision) and driving it through the live daemon-driven PB/LO loop end-to-end as the acceptance test. This proposal is that synthetic probe.
- `DELIB-20266203` — the autonomous-loop plan (7 grilled decisions): Q5 GO-first-pass synthetic, Q6 tight single-thread cap=1 + kill-switch armed, Q7 bounded cost. This probe is designed to satisfy Q5 (trivially correct).
- `DELIB-20266208` — owner reprioritization that fixed WI-4862 first so a headless session can self-finalize commits, a precondition for the daemon-driven loop's VERIFIED+commit step.

## Owner Decisions / Input

Implementation-authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-PHASE-Y-SYNTHETIC-LOOP-PROBE` (active; includes WI-4879 + ADR-DISPATCHER-ARCHITECTURE-001; allowed mutations: source, test; cites `DELIB-20266272`). The owner selected "Full daemon go-live (goal as written)" via AskUserQuestion (S20260627, archived as `DELIB-20266272`), which authorizes filing exactly this kind of synthetic throwaway proposal and driving it through the live daemon loop with zero owner interaction between initiation and completion. No further owner decision is required for this probe; the probe is trivially correct by construction (Q5).

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement is `DELIB-20266272`'s directive to drive a synthetic throwaway proposal through the live daemon-driven loop end-to-end as the PHASE-Y acceptance test. No new or revised requirement is needed; this proposal supplies the synthetic unit of work that requirement calls for.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| `DELIB-20266272` acceptance: a synthetic correct unit of work | `test_phase_y_probe_sum` (new) | `phase_y_probe_sum(2, 3) == 5`, `phase_y_probe_sum(0, 0) == 0`, `phase_y_probe_sum(-4, 1) == -3` all hold. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `test_phase_y_probe_sum` (new) | the derived test executes against the implemented module and passes. |
| Code quality | `ruff check` + `ruff format --check` | both pass on the two new files. |

Commands (pre-report): targeted `pytest` over `groundtruth-kb/tests/test_phase_y_loop_probe.py` via the repo venv; `ruff check` AND `ruff format --check` on the two changed files.

## Risk / Rollback

- **Risk:** essentially none — the module is a side-effect-free pure function with no callers in production code; nothing imports it except its own test.
- **Isolation:** `target_paths` is restricted to the two new files; no existing file is modified.
- **Rollback:** single-commit revert deletes both files. No KB mutation (`kb_mutation_in_scope: false`); the append-only bridge history is untouched. The throwaway artifacts may be retired in a later cleanup.

## Recommended Commit Type

`test` — adds a new test module plus the trivial pure-function fixture it exercises; no production capability surface is introduced.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
