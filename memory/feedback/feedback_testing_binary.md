---
name: Binary pass/fail — no SKIP status
description: Tests are proof. Unproven goals are presumed unmet. There is no SKIP or WARN — only PASS and FAIL.
type: feedback
---

Tests are proof. A goal we have not proven we meet is presumed unmet.

- **PASS** = proven
- **FAIL** = not proven (ran and failed, OR did not run at all)
- There is no SKIP or WARN status. Absence of confirmation of a PASS is always a FAIL (negative bias in testing).

**Why:** A test that "should run but didn't" is not a neutral outcome — it's a failure to verify. Treating it as anything other than FAIL creates a semantic gap where unverified goals silently pass through release gates.

**How to apply:** Never introduce a third status (SKIP, WARN, UNKNOWN, N/A) in test or pipeline tooling. If a check cannot be executed in the current context, it is FAIL with a reason. If a check is genuinely irrelevant (not just unable to run), remove it entirely rather than skipping it.

The historical SKIP convention exists because legacy testing frameworks couldn't dynamically compose test suites for their execution context. Our toolchain has no such limitation — we control suite composition, so irrelevant tests are excluded, not skipped.
