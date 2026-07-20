GO
::init gtkb pb
::open test
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata via nodeRepl.requestMeta plus current owner transcript role assignment

# Loyal Opposition Proposal Review - GO - WI-5629 Corrected Malformed Verdict Chain

bridge_kind: lo_verdict
Document: gtkb-wi5629-corrected-malformed-verdict-chain
Version: 002
Responds to: bridge/gtkb-wi5629-corrected-malformed-verdict-chain-001.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5629
Recommended commit type: fix:

## Verdict

GO. Version 001 is the right repair shape for the live WI-5617 implementation-start blocker and for the dependent WI-5626 clause-preflight consumer. It does not make malformed bridge content authoritative. It defines one exact, append-only correction-chain traversal: strict Prime proposal, one LO-verdict-shaped malformed historical publication, strict Prime `NO-ACTION` responding to that malformed file, then strict corrected LO verdict responding to the `NO-ACTION`.

The proposal is deliberately narrower than blanket malformed-history skipping. It rejects malformed Prime content, incomplete or pending correction chains, duplicate/intervening versions, cross-thread links, wrong document, wrong strict author role on the correction files, unreadable files, and malformed replacement verdicts. That is the necessary line: the bridge can recover from a specifically rejected malformed LO verdict without reactivating stale Prime bytes.

## First-Line Role Eligibility Check

PASS. This interactive session is explicitly operating as Loyal Opposition by owner instruction in the current chat. `GO` is a Loyal Opposition verdict status under `GOV-FILE-BRIDGE-AUTHORITY-001`, and version 001 is latest `NEW`, which is Loyal-Opposition-actionable.

## Review Independence

PASS. Version 001 was authored by Prime Builder session `019f77f8-0931-75e2-a78d-7dea7037f743`. This verdict is authored by Loyal Opposition session `019f7815-a565-78d3-a599-dec8388086ff`. The session contexts differ, so this is not same-session self-review.

## Applicability Preflight

- packet_hash: `sha256:151ff64949275e7af481220c3ca0881783f8ce52069b70888bee6d51ecb6b571`
- bridge_document_name: `gtkb-wi5629-corrected-malformed-verdict-chain`
- declared_target_paths: ["platform_tests/scripts/test_bridge_lifecycle_resolver.py", "platform_tests/scripts/test_implementation_authorization.py", "scripts/bridge_lifecycle_resolver.py", "scripts/implementation_authorization.py"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-001.md`
- operative_file: `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
candidate_evidence_hash: `sha256:cf9f664fe0a1c0babe07f4c138ea33ee73ec9b251af1db823a77b098a078c208`

## Clause Applicability

- Bridge id: `gtkb-wi5629-corrected-malformed-verdict-chain`
- Operative file: `bridge\gtkb-wi5629-corrected-malformed-verdict-chain-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- evidence gaps in must_apply clauses: 0
- blocking gaps: 0
- Mode: mandatory Slice 2 gate

| Clause | Spec | Applicability | Evidence found | Enforcement |
|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking |

## Evidence Reviewed

- Live failure reproduced: `python scripts/implementation_authorization.py begin --bridge-id gtkb-dispatcher-next-foundation-spike --session-id 019f77f8-0931-75e2-a78d-7dea7037f743 --no-write` returns `Bridge file has unrecognized status line: bridge/gtkb-dispatcher-next-foundation-spike-002.md: 'GO ... Proposal Approved With Observations'`.
- Live WI-5617 chain is the exact motivating shape: `bridge/gtkb-dispatcher-next-foundation-spike-001.md` NEW, `-002.md` malformed decorated GO, `-003.md` Prime `NO-ACTION` responding to `-002.md`, and `-004.md` corrected strict GO responding to `-003.md`.
- Current `scripts/implementation_authorization.py` confirms the blocker: `_bridge_file_status` rejects any first non-blank line not exactly matching the canonical status regex, and `bridge_entry_from_versioned_files` reads every exact version before constructing `BridgeEntry` (`scripts/implementation_authorization.py:315`, `scripts/implementation_authorization.py:331`).
- `.claude/rules/file-bridge-protocol.md` defines `NO-ACTION` as a Prime-authored response to a non-compliant LO verdict that routes back to LO for a corrected verdict; WI-5629 uses that route rather than inventing a second correction channel.
- `gt backlog show WI-5629 --history --json` shows WI-5629 is P0/open, derived from this implementation-start blocker, and tied to source spec `GOV-FILE-BRIDGE-AUTHORITY-001`.
- `gt tests show TEST-11674 --json` requires the happy-path corrected chain plus denial for malformed files without both exact `Responds to` links, pending `NO-ACTION`, non-GO correction, wrong document, ambiguous correction, and malformed latest state.
- `gt projects show PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE --json` shows PAUTH v4 is active, includes WI-5629, permits source/test work only after the ordinary independent GO, exact claim, and implementation-start gates, and forbids push, release, deployment, credential lifecycle, destructive cleanup, history rewrite, and external-system mutation.
- Target state check shows only `platform_tests/scripts/test_implementation_authorization.py` is already dirty; version 001 identifies those 53 foreign lines as WI-5382-owned and requires operation-time hash/diff attribution before mutation.

## Implementation Boundary

Prime Builder may implement only the declared four-target scope. The new shared resolver must remain the single lifecycle authority for this exception and must preserve the existing `BridgeEntry` API used by implementation authorization, target-path preflight, and finalization clearance.

For the malformed vN+1 file itself, this GO approves the proposal's stated proof model: use the first token only to classify it as LO-verdict-shaped (`GO`, `NO-GO`, or `VERIFIED`), then require the strict vN+2 Prime `NO-ACTION` and strict vN+3 LO replacement verdict to carry the document, role, and `Responds to` proof. Do not require canonical `author_identity: loyal-opposition/...` on the malformed file itself, because the live historical provider file carries provider-flavored identity metadata even though it was the LO publication being corrected.

## Specification-Derived Verification Expectations

At implementation verification time, the report must show:

- resolver fixtures for ordinary strict chains, the exact `NEW -> malformed GO -> NO-ACTION -> GO` correction chain, and every negative predicate named in TEST-11674;
- public `implementation_authorization.py begin` plus finalized packet coverage against an isolated corrected chain;
- preservation of WI-5382 named/current packet ordering and denial-no-write behavior;
- focused work-intent malformed/quarantine tests still passing;
- targeted ruff check and format-check for the four declared targets;
- a live WI-5617 no-write or governed start proof showing the foundation thread now resolves through corrected v004, reports quarantined v002, and selects proposal v001 without weakening PAUTH or claim checks.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - owner authorization for the isolated Dispatcher Next program and its derived/upstream-dependent repairs.
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS` - authority behind Prime-authored `NO-ACTION` verdict-correction routing.
- `DELIB-20265221` - owner priority behind the malformed-status quarantine precedent verified in `bridge/gtkb-dispatch-malformed-status-token-quarantine-004.md`.

## Owner Decisions / Input

No new owner decision is required. The owner-approved Dispatcher Next program and PAUTH v4 already include WI-5629 while retaining the independent GO, work-intent claim, implementation-start, verification, activation, and release gates.

## Residual Risk

The residual risk is implementation overbreadth. The verification bar must reject any solution that silently skips malformed history outside the exact adjacent correction chain, accepts malformed Prime content, treats pending `NO-ACTION` as implementation authority, rewrites historical bridge files, or lets the live WI-5617 chain pass without explicit quarantine diagnostics.
