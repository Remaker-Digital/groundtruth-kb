NEW
::init gtkb pb
::open build
author_identity: goose
author_harness_id: G
author_session_context_id: G-2026-08-07T14-51-23Z
author_model: deepseek-v4-flash-0731
author_model_version: 0731
author_model_configuration: gtkb-v4f-goose


# gtkb-openrouter-harness-role-sot-probative-purge — Remove the probative operating-role.md prohibition from the openrouter harness role-source guidance

bridge_kind: prime_proposal
Document: gtkb-openrouter-harness-role-sot-probative-purge
Version: 001
Date: 2026-08-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-6017

target_paths: ["scripts/openrouter_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`scripts/openrouter_harness.py` builds the system prompt for harness F (OpenRouter)
when it operates as Loyal Opposition. At lines 261-262 that prompt currently reads:

> Use harness-state/harness-registry.json through the canonical role reader as the role source
> of truth. Do not treat harness-local operating-role.md files as live role authority.

The second sentence is probative language (a prohibition that names its target).
Per the owner purge-before-probative standing directive (DELIB-20260806011917), a
prohibition that names its target teaches the thing being suppressed and grows the
surface it was meant to shrink; probative language is a last resort. The positive
directive — "Use harness-state/harness-registry.json through the canonical role reader
as the role source of truth" — states the correct rule positively and in isolation, so
the probative clause can be removed at the source.

This change deletes the probative clause (line 262) and keeps the positive directive
(line 261). It is a source-only purge of a harness system-prompt string.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-6017` that removes the
probative "Do not treat harness-local operating-role.md files as live role authority."
clause from the openrouter harness system-prompt guidance, keeping the positive
canonical role-reader directive. Bridge review, implementation-start, and independent
verification gates remain intact.

## Requirement Sufficiency

Existing requirements are sufficient. The owner standing directive
(DELIB-20260806011917) and the active project authorization define the implementation
boundary; no new requirement is required before implementation.

## In-Root Placement Evidence

The target path is inside `E:\GT-KB`: `scripts/openrouter_harness.py`.

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` - governs role source-of-truth resolution; the retained positive directive directs the canonical role reader as the role source of truth.
- `DELIB-20260806011917` - owner purge-before-probative standing directive; the authoritative basis for removing the probative clause at the source.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge-mediated implementation and verification honor the file bridge authority model.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification is derived from the linked specifications and executed against the implementation.

## Prior Deliberations

- `DELIB-20260806011917` - owner standing directive: purge before probative language (authority for this change).

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730` - active project authorization covering `WI-6017`.
- Owner directive 2026-08-07: apply the purge-before-probative principle to `openrouter_harness.py:261`.

## Proposed Scope

- Remove the probative clause "Do not treat harness-local operating-role.md files as live role authority." from the openrouter harness system-prompt guidance in `scripts/openrouter_harness.py` (line 262).
- Retain the positive directive "Use harness-state/harness-registry.json through the canonical role reader as the role source of truth." (line 261).
- Add or update a regression test in the openrouter harness test suite asserting the prompt contains the positive role-reader directive and does not contain the probative operating-role.md prohibition.
- No change to role resolution behavior, harness registry reads, or any other harness surface.

## Intuitiveness / Non-Impairment Disposition

This is a narrow, intuitive source purge consistent with the owner purge-before-probative
principle: the positive role-source directive remains, and the probative prohibition is
removed. It does not change how the harness resolves its role (the canonical role reader
remains the instructed source of truth). No guidance is retired beyond the probative
clause. The numbered bridge chain remains append-only.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Add a regression test in the openrouter harness suite asserting the prompt carries the canonical role-reader directive and omits the probative operating-role.md prohibition; run the suite. |
| `DELIB-20260806011917` | Confirm the probative clause is absent from the built prompt and the positive directive remains. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights on the filed proposal and implementation report. |

## Acceptance Criteria

- The openrouter harness system prompt contains the positive directive "Use harness-state/harness-registry.json through the canonical role reader as the role source of truth." and does not contain "Do not treat harness-local operating-role.md files as live role authority."
- The openrouter harness test suite passes with the added regression test.
- No role-resolution behavior or other harness surface changes.

## Risks / Rollback

Risk is low. The change removes a single probative sentence from a harness system-prompt
string. The primary risk is that some consumer relied on the prohibition text itself;
the retained positive directive already instructs the canonical role reader as the
source of truth, so behavior is preserved. Rollback is a revert of the source and test
changes; bridge files and project authorization records are append-only and must not be
deleted by rollback.

## Files Expected To Change

- `scripts/openrouter_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py` (regression test)

## Recommended Commit Type

`refactor`

---

When you are finished working, close your session envelope by invoking ::wrap.
