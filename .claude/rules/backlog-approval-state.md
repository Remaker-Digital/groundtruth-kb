# Backlog Approval State Rule

## Purpose

MemBase work items must separate owner approval evidence from ordinary backlog presence. A work item can be tracked, prioritized, or reviewed without becoming implementation-approved.

## Canonical States

- `unapproved`: no durable owner or bridge evidence authorizes implementation.
- `auq_required`: owner intent is referenced, but the required AskUserQuestion or equivalent durable decision evidence is missing.
- `auq_resolved`: durable owner decision evidence exists, but implementation has not been separately authorized.
- `bridge_authorized`: the latest applicable bridge review is GO and the GO cites the work item or implementation scope.
- `implementation_authorized`: implementation may proceed because durable owner evidence or a bridge GO has satisfied the approval gate.

## Transition Rule

Backlog creation, grooming, ordering, and review do not by themselves grant implementation authority. Moving a non-terminal work item to `implementation_authorized` requires one of these evidence paths:

1. AskUserQuestion or equivalent durable owner-decision evidence that explicitly approves the implementation scope.
2. A current bridge GO verdict that cites the work item or the implementation scope.

## Backfill Rule

Legacy work items with no approval_state must be backfilled deterministically:

- `WI-3271` is `auq_resolved` because it has known durable owner-decision evidence.
- Work items whose related bridge thread is latest `VERIFIED` are `implementation_authorized`.
- Work items whose related bridge thread is latest `GO` are `bridge_authorized`.
- Work items with source owner directive text and related deliberation evidence are `auq_resolved`.
- Work items with source owner directive text but no durable deliberation evidence are `auq_required`.
- All other active work items are `unapproved`.

## Enforcement

The approval-state gate must be deterministic and testable. Scripts or hooks that promote work to implementation authority must reject unknown states and must fail closed when required evidence cannot be found.
