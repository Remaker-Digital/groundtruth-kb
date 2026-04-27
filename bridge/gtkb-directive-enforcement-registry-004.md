GO

# Codex Review - GTKB Directive Enforcement Registry REVISED-1

**Status:** GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed document:** `bridge/gtkb-directive-enforcement-registry-003.md`

## Claim

The revised directive-enforcement registry proposal addresses the architectural
blockers from `bridge/gtkb-directive-enforcement-registry-002.md` and is
approved as a scope-of-program plan.

## Findings

### F1 - Harness-neutral registry scope is now correct

The canonical registry moves to `.gtkb/directive-registry.json`, with Claude,
Codex, and CI/session-audit adapters reading the same registry. This resolves
the prior Claude-specific ownership defect.

### F2 - Coverage is now stated honestly

The proposal replaces "bypass-resistant" language with a coverage matrix by
harness and tool class. The explicit acknowledgment that headless Codex and
Windows hook parity remain weaker surfaces is important and should remain in
future phase proposals.

### F3 - Non-negotiable runtime override removed

The proposal now forbids runtime overrides for `non_negotiable: true`
directives. Any relaxation requires formal rule/registry change, which is the
right safety posture for directives such as the root-boundary rule.

### F4 - Bash and read semantics are good enough for scope approval

The parse-explicit-target, dangerous-pattern block, manifest-gated cleanup, and
fail-closed write-like command model is a defensible starting point. The
three-mode read model also preserves required audit/migration reads while
blocking outside-root live dependencies.

## Execution Conditions

- P1 and P2 must land together or in the same review bundle; a registry without
  adapters is not an enforcement mechanism.
- Codex adapter work must include tests that reflect current Windows hook
  limitations and must not claim stronger coverage than demonstrated.
- The first registry entries must include `DIR-ROOT-BOUNDARY-001`; any
  proposal that excludes it is out of scope for this GO.
- Runtime overrides must remain unavailable for `non_negotiable: true`.

## Decision

GO for the directive-enforcement registry program as revised in
`bridge/gtkb-directive-enforcement-registry-003.md`, subject to the execution
conditions above.

