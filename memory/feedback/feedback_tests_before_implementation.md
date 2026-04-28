---
name: Tests before implementation — mandatory
description: Tests MUST be produced BEFORE implementation code. No exceptions. This is the development order, not optional.
type: feedback
---

Tests are ALWAYS required. They must be produced BEFORE the implementation work.

**Why:** The owner observed that Phase 2 and Phase 3 implementation proceeded without any test creation. ARIA attributes, focus traps, locale replacements, quality scorer wiring, and alert integration were all implemented with no automated verification beyond typecheck. This violates GOV-12 (WI triggers tests), GOV-18 (assertion quality), and the project's test-first development culture.

**How to apply:**
- In the 6-step development cycle, tests are part of Step 2 (implementation plan) and Step 4 (implementation)
- The implementation plan MUST include test deliverables with specific test descriptions
- During implementation, write tests FIRST, verify they fail, THEN write the implementation code
- Test types required per change category:
  - Backend Python changes: unit tests in tests/ directory
  - Widget component changes: component assertions (ARIA attributes, locale usage, focus behavior)
  - API changes: contract tests
  - Alert/quality infrastructure: integration tests
- The Codex plan review (Step 3) should verify test deliverables are present and sufficient
- The Codex implementation review (Step 5) should verify tests exist and pass
- Never commit implementation code without accompanying tests
- Tests follow the same 6-step development cycle as implementation: investigate, plan, Codex plan review, write tests, Codex implementation review, commit
- Submit all test code to Codex for review before committing — tests are treated identically to functional code
