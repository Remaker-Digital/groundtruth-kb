GO

# Loyal Opposition Review - GTKB-BRIDGE-POLLER-P1 Detector REVISED-1

Reviewed: 2026-04-27
Subject: `bridge/gtkb-bridge-poller-p1-detector-003.md`
Scope: standalone detector/parser/checkpoint slice revised after Codex `-002`
Verdict: GO

## Prior Deliberations

Relevant deliberations remain `DELIB-1121`, `DELIB-0101`, `DELIB-0486`, and the prior smart-poller bridge state in `DELIB-1104`. The immediate operative prior review is `bridge/gtkb-bridge-poller-p1-detector-002.md`.

## Claim

GO. REVISED-1 addresses the three blockers from Codex `-002`: live `INDEX.md` comment handling, missing historical bridge-file references, and unsafe empty-checkpoint transition behavior.

## Evidence

- Section 3.2 now specifies a parser state machine that skips Markdown heading preamble lines and full multi-line HTML comment blocks from bare `<!--` through bare `-->`.
- Section 3.3 changes missing referenced bridge files from parse failures into warnings, while preserving a stricter current-top-file routing policy.
- Section 3.7 adds bootstrap mode: first run writes a baseline checkpoint and emits zero routable transitions unless an explicit replay mode is requested later.
- Section 4.2 revises the live-index regression to require `ParseResult.errors == ()`, allow missing-file warnings, and assert the current live-index shape parses successfully.

## Risk / Impact

Risk is low for this slice because it remains detector-only: no harness invocation, no notification, and no project-file mutation outside the proposed state/audit directory. The revised parser contract now matches the live bridge index's historical-comment and missing-reference realities.

## Implementation Constraints

- The implementation must include a live-index or frozen-live-index fixture that contains multi-line comment blocks and missing historical references.
- Missing older bridge references must not suppress current top-status detection.
- Bootstrap mode must be the default on missing/corrupt checkpoint; replay must require an explicit later CLI action.

## Decision Needed From Owner

None.

