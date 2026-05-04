# Counterpart Review Gate — Mandatory Pre-Implementation Review

This rule auto-loads via `.claude/rules/` convention and is TRACKED in git.

## The Rule

**No implementation without Loyal Opposition review when the bridge is active. No exceptions.**

Before Prime Builder executes ANY of the following actions, a bridge proposal
MUST exist with Loyal Opposition GO status:

1. Writing or modifying source code files
2. Promoting, reverting, or changing spec statuses in the KB
3. Creating, resolving, or modifying work items in the KB
4. Modifying configuration files
5. Running deployment scripts
6. Any action that changes the state of either repository

The bridge proposal is not valid unless it includes a `Specification Links`
section that cites every relevant governing specification. Loyal Opposition must
NO-GO any implementation proposal that omits relevant specifications or treats
the links as placeholder/TBD content.

Loyal Opposition MUST reject all implementation proposals that are not linked to
specifications. Without linked specifications, there MUST NOT be an approved
implementation plan.

## What Counts as "Implementation"

- Code changes (new files, edits, deletions)
- KB mutations (insert_spec, update_spec, insert_test, resolve_work_item, etc.)
- Configuration changes (groundtruth.toml, settings.json, CI workflows)
- Deployment operations (build, push, deploy)
- Git operations that change history (merge, rebase, tag)

## What Does NOT Require a Bridge Proposal

- Read-only exploration (grep, read, glob, git log)
- Running existing tests (pytest, ruff, mypy)
- Reading KB state (queries, list_specs, get_spec)
- Drafting bridge proposals themselves
- Updating MEMORY.md (session state, not canonical knowledge)
- Emergency bridge infrastructure repair (per bridge-essential.md)

## Enforcement

If Prime Builder catches itself about to implement without a GO:
1. STOP immediately
2. Draft a bridge proposal describing the intended change
3. Submit to bridge/INDEX.md as NEW
4. Wait for Loyal Opposition GO before proceeding

If Loyal Opposition is reviewing an implementation proposal:
1. Confirm the proposal links all relevant specifications.
2. Confirm the proposed tests are derived from those linked specifications.
3. Run `python scripts/bridge_applicability_preflight.py --bridge-id <document-name>`.
4. Include the generated `Applicability Preflight` section in any `GO` verdict.
5. Issue `NO-GO` if any required applicable specification is missing or if the
   test mapping is missing or incomplete.

If Loyal Opposition is verifying an implementation:
1. Carry forward the proposal's linked specifications.
2. Confirm tests derived from those specifications were created or identified.
3. Confirm those tests were executed against the implementation.
4. Run `python scripts/bridge_applicability_preflight.py --bridge-id <document-name>`.
5. Include the generated `Applicability Preflight` section in any `VERIFIED`
   verdict.
6. Issue `NO-GO` instead of `VERIFIED` for any untested linked specification
   unless an explicit owner waiver is documented.

This applies even when:
- The change "seems too small to review"
- The owner has given pre-approval on a work list
- The tests are already passing
- The change is "just a KB status promotion"

Pre-approval on the work list means "you may proceed through the bridge
protocol autonomously" — it does NOT mean "skip the bridge protocol."

## Rationale

Session S296 incident: SPEC-1834 was promoted to verified without a bridge
proposal. The change was correct (64 tests passing) but the governance gap
was real — no audit trail, no independent verification, no opportunity to catch
errors. The bridge protocol exists to prevent exactly this class of silent drift.

## © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
