NEW

# Implementation Proposal - Startup Refractor First Finding: Glossary-Load Surface (GTKB-STARTUP-REFRACTOR-001)

bridge_kind: implementation_proposal
Document: gtkb-startup-refractor-glossary-load-surface
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH
Project: PROJECT-GTKB-SESSION-LIFECYCLE-UX
Work Item: GTKB-STARTUP-REFRACTOR-001

target_paths: ["scripts/session_self_initialization.py", "groundtruth-kb/src/groundtruth_kb/startup/glossary_load.py", "tests/scripts/test_startup_glossary_load.py"]

This NEW proposal addresses the first key finding from `STARTUP-PROCEDURE-REFRACTOR-ADVISORY-2026-05-02-23-52.md`: "Generated startup service still does not surface the new glossary-load requirement." Other findings are deferred to follow-on slices.

## Claim

Add an explicit glossary-load step to the startup service that loads `.claude/rules/canonical-terminology.md` content into the rendered startup payload, so role-assigned harnesses receive the canonical vocabulary in their session initialization without separately reading the file.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` - startup self-initialization.
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` - glossary as DA read surface.
- `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` - glossary citation contract.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-SESSION-LIFECYCLE-UX authorization including this WI.
- 2026-05-02 S328: original advisory from Codex (STARTUP-PROCEDURE-REFRACTOR-ADVISORY).

## Requirement Sufficiency

Existing requirements sufficient. Advisory finding #1 explicitly specifies the gap.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI, first-of-8 findings only; member of PROJECT-GTKB-SESSION-LIFECYCLE-UX per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 (loader) + IP-2 (integration) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Glossary loader module

`groundtruth-kb/src/groundtruth_kb/startup/glossary_load.py`:
- Function `load_glossary_for_startup(project_root: Path) -> dict[str, Any]` reads `.claude/rules/canonical-terminology.md` and returns structured representation: term name -> {definition, source, implementation_pointer}.
- Caches result for in-session reuse.

### IP-2: Startup-payload integration

In `scripts/session_self_initialization.py`, add a `Glossary` section to the rendered startup payload:
- Section lists canonical term names + 1-line definitions.
- Full content available via lookup in the structured representation.

### IP-3: Tests

Tests verify: loader output schema, startup payload includes Glossary section, missing-glossary handled gracefully.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Loader extracts canonical terms | `test_loader_extracts_terms` |
| Loader handles missing file gracefully | `test_loader_handles_missing_file` |
| Startup payload includes Glossary section | `test_startup_payload_has_glossary_section` |
| Term lookup returns full content | `test_term_lookup_returns_full_content` |
| Caching avoids re-reads | `test_loader_caches_within_session` |

Run: `python -m pytest tests/scripts/test_startup_glossary_load.py -v`.

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; 5 tests PASS.
- Both preflights PASS.
- Subsequent advisory findings (2-8) tracked for follow-on slices.

## Risks / Rollback

- Risk: glossary load adds startup latency. Mitigation: ~5kb file, sub-ms read.
- Rollback: revert IP-2 integration; loader stays as standalone module.

## Recommended Commit Type

`feat` - startup surface enhancement. ~80 LOC + tests.
