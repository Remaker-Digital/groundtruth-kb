# 3. Testing

Tests are the verification layer of the GroundTruth method. Every test is linked to a specification and must produce an unambiguous pass or fail result.

## Test forms

A test can take several forms depending on what it verifies:

**Logical assertion.** A concrete, machine-checkable condition: "the configuration file exports a `rate_limit` field", "the authentication middleware is registered before route handlers", "no API key appears in the client bundle."

**User story.** A verifiable process described from the user's perspective: "A customer visits the product page, adds an item to the cart, proceeds to checkout, and receives an order confirmation email within 60 seconds."

**Abstract description.** A measurement, pseudocode, or behavioral description that specifies the desired outcome without prescribing how to test it: "Response latency at the 95th percentile must be below 500ms under 100 concurrent requests."

All three forms are valid. The key requirement is **unambiguous outcome** — someone (human or automated) must be able to determine pass or fail without subjective judgment.

## Test lifecycle

Tests are versioned alongside the specifications they verify. When a specification changes, the linked tests should be reviewed and updated to match.

Test results are recorded in the knowledge database:

- `last_result`: the most recent outcome (`pass`, `fail`, `not_proven`, `skipped`)
- `last_executed_at`: when the test was last run
- `test_file`: path to the executable test file (for automated tests)

## Linking tests to specifications

Every test has a required `spec_id` field connecting it to the specification it verifies. This linkage is the backbone of traceability:

- **Spec → Tests**: "What tests verify this requirement?"
- **Test → Spec**: "Which requirement does this test prove?"
- **Coverage gaps**: "Which specifications have no linked tests?"

Governance rule GOV-12 requires that creating a work item triggers creating linked tests. This prevents specifications from accumulating without verification.

## Outside-in testing

GroundTruth favors **outside-in testing** (GOV-19): tests should exercise the system's surfaces and observable behaviors, not its internal implementation details.

- **Preferred**: call the API endpoint and verify the response
- **Preferred**: render the UI component and check the output
- **Preferred**: send a message through the pipeline and verify delivery
- **Supplemental**: unit tests for complex internal logic

The reasoning: outside-in tests survive refactoring. If you restructure the internals but the API still returns the correct response, outside-in tests pass. Implementation-coupled tests break on every refactor, creating maintenance burden without catching real defects.

## Test plans and phases

For larger projects, tests are organized into **test plans** with ordered **phases**. Each phase groups related tests and defines a gate criterion — what must pass before the next phase can begin.

Example structure:

```
PLAN-001: Release Verification
  Phase 1: Contract tests (API schema validation)
  Phase 2: Smoke tests (critical path health checks)
  Phase 3: End-to-end tests (full user workflows)
  Phase 4: Performance tests (load and latency)
  Phase 5: Production gate (deployment readiness)
```

Phases execute in order. A failure in Phase 2 blocks Phase 3 — there is no value in running end-to-end tests if the API contracts are broken.

## Test coverage mapping

The `test_coverage` table provides a secondary mapping between specifications and executable test files. Where the `spec_id` on a test record is the primary link, coverage mappings capture:

- Which test file covers which spec
- Which test class and function within the file
- A confidence level (`high`, `medium`, `low`)
- The reason for the mapping (e.g., "tests the rate limit enforcement logic")

This is useful for large codebases where a single test file may cover multiple specs, or where the mapping is not obvious from the test name.

## When tests fail

A failing test triggers a diagnostic workflow:

1. **Is the specification correct?** The business need may have changed. If so, update the spec first (GOV-05: fix the spec before fixing the implementation).
2. **Is the test correct?** The test may be over-specified or testing the wrong thing. If so, update the test — but only with owner approval for tests on defect/regression work items (GOV-15).
3. **Is the implementation correct?** If the spec and test are right, the code has a defect. Create a work item to track the fix.

The rule is: **never silence a failing test without understanding why it fails.** Governance rule GOV-07 requires that test failures are recorded as work items and fixed in separate sessions — not patched inline during testing.
