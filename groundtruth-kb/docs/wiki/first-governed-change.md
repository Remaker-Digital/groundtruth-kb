# First governed change

**Status:** Conceptual first pass; command-by-command customer tutorial pending qualification
**Reviewed:** 2026-09-26

A first governed change should teach the real lifecycle without asking a new
user to understand the entire platform.

## Required starting state

- The installation passes [Verify installation](Verify-Installation).
- The application and its Git repository are registered through the supported
  route.
- The owner selected the project and work item.
- The work item belongs to exactly one project.
- The project is authorized before a new implementation proposal is filed.
- Applicable formal requirements and an executable linked test exist.

## Workflow

1. **Read current context.** Read the work item, project, requirements, test,
   dependencies, and current bridge head from the live service.
2. **Propose.** Prime Builder authors a `NEW` proposal that states exact target
   paths and test targets.
3. **Review.** A separate Loyal Opposition context evaluates the proposal and
   authors `GO` or `NO-GO`.
4. **Implement.** After `GO`, Prime Builder claims the exact next artifact,
   changes only the reviewed scope, and runs the stated tests.
5. **Report.** Prime Builder authors a `READY` implementation report with exact
   evidence.
6. **Verify.** Loyal Opposition independently checks the final bytes and tests,
   then authors `VERIFIED` or `NOT-READY`.
7. **Finalize.** When all project work items are verified in final form, Loyal
   Opposition commits the complete verified project cohort.

## Success criterion

The tutorial is successful only when a new evaluator can observe the current
requirement, the linked executable test, independent review, exact final bytes,
and the resulting Git fact. A generated report or green dashboard alone is not
success.

The fully executable sample and screenshots remain a priority documentation gap.
They must be built against the supported installer and release rather than
invented from historical commands.
