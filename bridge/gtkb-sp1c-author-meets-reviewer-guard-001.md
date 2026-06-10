NEW
author_identity: Prime Builder
author_harness_id: B
author_session_context_id: session-mq5ki8hp
author_model: Claude Sonnet 4
author_model_version: 4
author_model_configuration: Prime Builder session-scoped bridge work

bridge_id: gtkb-sp1c-author-meets-reviewer-guard
bridge_kind: prime_proposal

# SP-1c: Author-Meets-Reviewer Guard

## Status
- **Priority:** P2 (Medium)
- **Effort:** Small (1 day)
- **Blocked by:** SP-1a

## Background
LO investigation found no enforcement preventing harness from reviewing own proposals. Could cause infinite loops and violates role definition.

## Specification Links
- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-REVIEW-IMPARTIALITY-001
- DCL-BRIDGE-ENVELOPE-REQUIREMENTS-001

## Target Paths
- scripts/cross_harness_bridge_trigger.py (add validation)

## Implementation
1. Extract author_harness_id from proposal metadata
2. Validate: if author == reviewer, raise DispatchError
3. Config file: .claude/config/bridge-routing.json
4. Hard error (not advisory)

## LO Review Criteria
- [ ] Metadata parsed
- [ ] Self-review raises error
- [ ] Config file exists
- [ ] Code passes ruff
- [ ] Tests: routing to different reviewer succeeds, routing to self fails
