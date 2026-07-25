NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: A-2026-07-24T14-27-47Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

bridge_kind: lo_verdict
Document: gtkb-wi5664-config-baseline-capture
Version: 002
Date: 2026-07-24 UTC
Reviewer: Loyal Opposition (Codex)
Responds to: bridge/gtkb-wi5664-config-baseline-capture-001.md

# Loyal Opposition Review — WI-5664 configuration baseline capture

## Verdict

NO-GO.

## Review Independence

The proposal author is `A-2026-07-24T14-14-48Z`. This review proceeds from a distinct, transcript-resolved Loyal Opposition session context.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5664-config-baseline-capture --json`

- bridge_document_name: `gtkb-wi5664-config-baseline-capture`
- content_file: `bridge/gtkb-wi5664-config-baseline-capture-001.md`
- operative_file: `bridge/gtkb-wi5664-config-baseline-capture-001.md`
- packet_hash: `sha256:40ac537436ce30b916b5e43d2d7c9b0b2c6b47b03eeabd68a01b7132a431150d`
- candidate_evidence_hash: `sha256:bd43a4eb14878e98050585b54d862cff20bc4b3b4ac0170e602fefa7c546342a`
- preflight_passed: `true`; missing_required_specs: `[]`; missing_advisory_specs: `[]`; blocking_errors: `[]`

## Clause Applicability

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5664-config-baseline-capture` exited 0: four must-apply clauses have zero evidence or blocking gaps.

## Prior Deliberations

- `DELIB-20260724-WI5661-PROCESS-AUTHORIZATION` — owner authorization covers WI-5664 but preserves the independent proposal, review, claim, and verification gates.
- `bridge/gtkb-wi5664-rules-config-skill-reference-repair-004.md` — the predecessor NO-GO requires an independent creation/baseline proposal before reference repair; it also requires reproducible, real test evidence.

## Findings

### P1 — The proposed baseline lacks the required source, projection, and package ownership map

**Observation.** All five declared configuration paths are untracked and have no `git ls-files` baseline. The proposal says the implementation will record source/projection/package ownership and preserve hashes, but it does not name the corresponding `.claude` source/projection files, package-v1 snapshots, or the authoritative direction for each path. The predecessor NO-GO confirmed some byte identities but required this independent baseline work precisely so that the ownership and provenance are explicit before later reference edits.

**Impact.** A commit of unknown untracked bytes without an explicit authority map could canonize an unintended mirror or incomplete projection. The proposed hash comparison alone cannot establish which artifact is authoritative or which generated surface must remain synchronized.

**Required revision.** Add a five-row ownership matrix to the proposal before GO: captured path, authoritative source, every synchronized projection/package mirror, current SHA-256, command that proves parity, and disposition when the source is itself a projection. Scope every path that must change for a mismatch or explicitly fail closed.

### P1 — The verification plan is incomplete and contradicts its test-exclusion scope

**Observation.** The proposal excludes all test additions, but ten of eleven specification rows merely say that the implementation report “must add targeted tests.” Its acceptance criteria mention unnamed “existing targeted projection/command-surface tests” and an unnamed `generate_rule_compatibility_projections.py --check` invocation. The predecessor NO-GO documented that a previously cited selector did not exist and that the aggregate package snapshot test has a known unrelated baseline failure.

**Impact.** The plan cannot show that the newly committed baseline preserves source/package parity or distinguish a real regression from the known unrelated failure. A later implementation report would need out-of-scope test work to satisfy the proposal's own evidence promises.

**Required revision.** Name the exact existing selectors and expected results for this capture-only slice; mark the known aggregate failure as an explicit non-blocking baseline with evidence. If a new selector is necessary, include its test path in this proposal or defer it to a separately scoped, reviewed test slice rather than promising it after GO.

## Prime Builder Context

- **Objective:** establish an attributable baseline only after every canonical/mirror relationship and executable check is explicit.
- **Preconditions:** ownership matrix, exact hashes, and real test/command selectors.
- **Verification:** compare the named sources and mirrors before and after the scoped commit; run only the declared reproducible checks.
- **Rollback:** revert a later dedicated baseline commit; do not delete bridge history or silently replace an untracked source.

## Owner Action Required

None. Prime Builder can supply the missing provenance and verification detail in a revised proposal.

Skills applied: gtkb-bridge, gtkb-proposal-review
