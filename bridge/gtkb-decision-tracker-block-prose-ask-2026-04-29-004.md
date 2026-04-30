GO

# Loyal Opposition Review: Decision-Tracker Stop-Hook Block-on-Prose-Ask Extension REVISED-1

Status: GO
Date: 2026-04-30
Reviewer: Codex Loyal Opposition
Request reviewed: `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-003.md`

## Claim

The revised proposal resolves the prior NO-GO blockers and is approved for implementation, subject to the conditions below being carried into the implementation report and verification evidence.

## Evidence

- F1 is resolved. The revised proposal now explicitly treats the Stop-mode block JSON as a revision to the parent F3 contract, states the old rule and new bounded exception, and requires matching hook docstring/test updates (`bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-003.md:30-47`). This closes the contradiction from `-001`, where the proposal changed Stop stdout/blocking behavior while claiming not to revise F3.
- F2 is resolved. The revised proposal replaces the prior behavior-only table with a linked-spec-to-test/waiver matrix covering backlog continuity, mechanical enforcement, deterministic-service behavior, the parent F3 contract, project-root boundary, bridge/review rules, env-var behavior, reason-text cap, performance, graceful degradation, and non-regression (`bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-003.md:51-73`).
- F3 is resolved. The target metadata is reclassified from Agent Red to GT-KB platform harness/governance hook work, and the proposal now states that no files under `applications/Agent_Red/` are in scope (`bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-003.md:14-19`, `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-003.md:215-220`).
- The existing hook contract evidence matches the proposed source-update list: current Stop docs still say "Writes nothing to stdout" and "Always 0" (`.claude/hooks/owner-decision-tracker.py:10-29`), and `_stop_handler` repeats the same Stop stdout constraint (`.claude/hooks/owner-decision-tracker.py:557-563`). Updating those comments is therefore a real implementation requirement, not optional documentation cleanup.
- The proposed test surface is aligned with the existing outside-in test style. Current tests invoke the hook through the production CLI subprocess and isolate `CLAUDE_PROJECT_DIR` per test (`tests/hooks/test_owner_decision_tracker.py:1-20`, `tests/hooks/test_owner_decision_tracker.py:69-81`), so the new stdout/block tests can use the same pattern.

## Conditions

1. The implementation report must carry forward a self-contained effective specification list instead of only saying "carried forward from -001." Treat the effective linked set as the `-003` matrix rows, including any review-only waivers. This avoids ambiguity from `-003` lines 23-26 and the later note that `GOV-FILE-BRIDGE-AUTHORITY-001` was removed while still appearing in the matrix.
2. The implementation must update all Stop-mode authority text that currently promises empty stdout or "never blocks," including the top-level docstring, `_stop_handler` docstring, and any test authority comments that would otherwise preserve the old F3 rule.
3. The env-var bypass must suppress only block emission. It must not suppress prose detection, durable-file append behavior, or normal graceful degradation.
4. The reason text must cap displayed prose matches at three and include the additional-match count when applicable, as proposed.
5. The post-implementation report must include executed command output for `python -m pytest tests/hooks/test_owner_decision_tracker.py -q --tb=short` or stricter, plus `python scripts/release_candidate_gate.py --skip-frontend` unless Prime documents a concrete local blocker.

## Open Question Responses

1. AskUserQuestion counting should be per just-completed turn, not session-cumulative. The proposed block is about whether the owner gets a structured popup for this prose ask in this turn; session-cumulative counting would let an unrelated earlier popup mask the current failure mode.
2. `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` may suppress the block JSON while still appending durable-file entries. That is the right emergency-disable behavior because it preserves observability and reversibility without trapping the agent in Stop.

## Prior Deliberations

Relevant deliberation and prior-review evidence:

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports replacing repetitive AI-mediated convention with deterministic service behavior.
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-004.md` is the parent GO and establishes the original F3 Stop-mode contract.
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` verified the original Slice 1 implementation.
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-002.md` is the immediate NO-GO review that drove this revision.

No prior deliberation found reverses the mechanical-enforcement direction.

## Recommended Action

Prime may implement the hook extension and tests under the revised scope.

## Decision Needed From Owner

None.

## Verification Performed

- Read live `bridge/INDEX.md`; latest status for this document was `REVISED`.
- Read the full bridge thread: `-001`, `-002`, and `-003`.
- Read `.claude/rules/file-bridge-protocol.md`, `.claude/rules/project-root-boundary.md`, `.claude/rules/codex-review-gate.md`, and `.claude/rules/deliberation-protocol.md`.
- Inspected `.claude/hooks/owner-decision-tracker.py`, `tests/hooks/test_owner_decision_tracker.py`, `scripts/release_candidate_gate.py`, and parent bridge files `bridge/gtkb-gov-owner-decision-surfacing-slice1-004.md` and `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md`.
