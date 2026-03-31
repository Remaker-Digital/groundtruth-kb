# 1. Method Overview

GroundTruth is an engineering discipline layer for teams building AI-powered systems. It provides traceable specifications, automated assertions, and structured governance so that what was decided, why it was decided, and whether the implementation still matches are always answerable questions.

## The problem

AI systems change fast. Models improve, prompts get rewritten, integrations shift, and business requirements evolve — often within the same week. Without discipline, teams lose track of:

- What the system is *supposed* to do (requirements drift)
- Why a particular design was chosen (decision amnesia)
- Whether the current code still matches the agreed behavior (silent regression)
- What was tested and what was not (coverage gaps)

GroundTruth addresses this by making **specifications the source of truth** — not the code, not the documentation, not the team's collective memory.

## Three interdependent artifacts

Every GroundTruth project maintains three artifact types that reinforce each other:

```
Specifications ←→ Tests ←→ Implementation
```

**Specifications** describe what the system must do. They function as a decision log — recording what was agreed and why — not as a build specification dictating how to construct the system. A good specification is as stable as the business need it captures.

**Tests** verify that the implementation meets the specifications. Each test is linked to a specification and must produce an unambiguous pass or fail result. Tests can be logical assertions, user stories, or abstract descriptions.

**Implementation** is the code and configuration that realizes the specifications. It is described by specifications and verified by tests.

When any one of these changes, the other two must be checked:

- Spec changes → do the tests still cover the requirement? Does the implementation still match?
- Test failures → is the spec wrong, the test wrong, or the implementation wrong?
- Code changes → do the specs still describe the new behavior? Do the tests still pass?

## Core workflow

The standard GroundTruth workflow moves from agreement to verification in seven steps:

1. **Specify** — The owner describes what the system must do. Record as specifications in the knowledge database.
2. **Identify gaps** — Compare specs against the current implementation. Create work items for each gap.
3. **Create tests** — For each work item, create tests that will prove the gap is closed. Link each test to its specification.
4. **Prioritize** — Add work items to a backlog. The backlog ordering determines implementation sequence.
5. **Implement** — Write the code that satisfies the specifications.
6. **Verify** — Run the tests. Each must produce a clear pass or fail.
7. **Close or iterate** — If tests pass, the work item is resolved. If they fail, diagnose: fix the spec, fix the test, or fix the implementation.

This is not a waterfall process. Steps overlap and repeat. The key discipline is that specifications come *before* implementation, not after — and that every change flows through this cycle.

## The knowledge database

All artifacts live in an append-only SQLite database. The term "append-only" means:

- Every change creates a **new version** of the record
- Previous versions are never modified or deleted
- The full history of every specification, test, and work item is preserved

This design serves two purposes: **auditability** (you can always answer "what did we agree on March 15?") and **safety** (no accidental data loss from a bad update).

The database stores nine artifact types:

| Artifact | Purpose |
|----------|---------|
| Specifications | What the system must do |
| Tests | How to verify specifications are met |
| Test plans | Organized phases of test execution |
| Work items | Gaps between specs and implementation |
| Backlog snapshots | Prioritized work queues at a point in time |
| Operational procedures | Runbooks and operational checklists |
| Documents | Session records, plans, analysis |
| Environment config | Infrastructure and deployment settings |
| Testable elements | UI components and observable behaviors |

## Governance model

Governance specifications (prefixed `GOV-`) define the rules of the method itself. They are machine-readable — each carries assertions that can be automatically checked. Examples:

- **GOV-01 (Spec-first)**: Specifications must be created or updated before implementation code is written.
- **GOV-03 (Test clarity)**: Every test must produce an unambiguous pass or fail result.
- **GOV-12 (WI triggers tests)**: Creating a work item must be followed by creating linked tests.

Governance gates enforce rules at lifecycle transitions. The two built-in gates are: ADR/DCL specs must have assertions before reaching "implemented", and defect/regression work items require owner approval before resolution. Projects can add their own enforcement gates as plugins — for example, requiring executable test evidence before a spec can reach "verified" status. Gates are pluggable and configured per-project (see [Adoption](09-adoption.md)).

## Assertions

Assertions are automated checks that run against the codebase and verify that specifications are still satisfied. Each assertion is a pattern match:

- **grep**: Does a file contain a required pattern? (e.g., "the config file must export a rate limit")
- **glob**: Does a required file exist? (e.g., "tests/test_auth.py must exist")
- **grep_absent**: Is a forbidden pattern absent? (e.g., "no hardcoded API keys in source")

Assertions can be run on demand with `gt assert` or invoked from scripts. Projects may also configure them to run at session start or before builds via hooks. Failing assertions on "implemented" or "verified" specifications indicate regressions — something that was working no longer is.

## Dual-agent collaboration

GroundTruth supports a two-agent workflow where responsibilities are separated:

**Prime Builder** creates, implements, and maintains artifacts. This agent proposes specifications, writes code, runs tests, and keeps the system internally consistent. Prime Builder is responsible for the *how*.

**Loyal Opposition** inspects, critiques, and analyzes. This agent reviews plans, code, and configuration for correctness, security, and completeness. Loyal Opposition produces evidence-based reports and does not implement changes. It is responsible for *whether the how is good enough*.

The separation ensures that the agent building the system is not the same agent evaluating it. This catches blind spots, overconfidence, and scope creep. For details, see the Dual-Agent Collaboration guide (coming in a future update).

## Session discipline

Work is organized into numbered sessions (`S1`, `S2`, ..., `S240`). Each session:

- Has a clear objective stated at the start
- Produces artifacts recorded in the knowledge database
- Ends with a structured wrap-up: what was done, what changed, what's next

Every fifth session is an **audit session** with additional hygiene steps — checking for stale work items, verifying spec coverage, and pruning operational records.

Session discipline prevents context loss across conversations and ensures that any team member (human or AI) can pick up where the last session left off. For details, see the Session Discipline guide (coming in a future update).

## What GroundTruth is NOT

- **Not a project manager.** It does not assign tasks to people or track timelines. It tracks *what the system must do* and *whether it does it*.
- **Not a CI/CD pipeline.** It does not build, deploy, or run your application. It integrates with your pipeline via assertions and governance gates.
- **Not a test runner.** It does not execute pytest or jest. It *records* test results and *enforces* that tests exist and pass before specifications can be promoted.
- **Not a replacement for code review.** The Loyal Opposition pattern complements human review; it does not replace the judgment of experienced engineers.
- **Not prescriptive about architecture.** It governs the *process* of making and verifying decisions, not the technical choices themselves. You can use GroundTruth with any language, framework, or cloud provider.
