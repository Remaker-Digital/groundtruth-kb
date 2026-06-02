REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-gtkb-pb-2026-06-02
author_model: GPT-5 Codex
author_model_version: 2026-06-02
author_model_configuration: reasoning=high

bridge_kind: implementation_proposal
Document: gtkb-bridge-citation-freshness-test-restoration
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-3267
target_paths: ["platform_tests/scripts/test_bridge_citation_freshness_preflight.py", "scripts/bridge_citation_freshness_preflight.py", "groundtruth.db"]

# Implementation Proposal: Citation Freshness Test Restoration

## Summary

Close the remaining WI-3267 gap by restoring focused regression coverage for `scripts/bridge_citation_freshness_preflight.py`, repairing the preflight script only if restored tests expose a source defect, and then reconciling the WI-3267 backlog row after verified test evidence exists.

The implementation component already reached VERIFIED on `gtkb-bridge-citation-freshness-preflight`; the open issue is that the approved regression test file is absent from the live tree. This proposal restores that coverage and prevents backlog closure from relying only on historical bridge status.

## Prior Deliberations

- `DELIB-S367-PAUTH-BRIDGE-PROTOCOL-RELIABILITY-AMENDMENT-WORK-INTENT` authorizes the active bridge protocol reliability PAUTH cited above; formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-28-pauth-bridge-protocol-reliability-amendment-work-intent.json` records that authorization evidence.
- The bridge thread `gtkb-bridge-citation-freshness-preflight` is live VERIFIED at `bridge/gtkb-bridge-citation-freshness-preflight-006.md` and provides the historical implementation and verification trail for WI-3267.
- WI-3267 records the original owner directive from S341 to add useful enhancements that help future bridge work, specifically stale cross-thread citation detection.

## Owner Decisions / Input

- Mike's current-session directive on 2026-06-02 asks Prime Builder to continue until all listed items are completed. This proposal still requires normal Loyal Opposition GO before protected implementation edits.
- The cited project authorization supplies bounded owner-approval evidence for bridge protocol reliability work; formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-28-pauth-bridge-protocol-reliability-amendment-work-intent.json` is the explicit approval packet for the bounded backlog-resolution component. It does not bypass bridge GO, target path scope, implementation-start packets, implementation reports, or Loyal Opposition verification.

## Specification Links

- `.claude/rules/file-bridge-protocol.md` governs bridge lifecycle, INDEX authority, target paths, implementation reports, and verification evidence.
- `.claude/rules/codex-review-gate.md` requires Loyal Opposition GO before implementation and spec-derived verification evidence after implementation.
- `.claude/rules/project-root-boundary.md` keeps all live GT-KB artifacts under `E:\GT-KB`.
- `.claude/rules/operating-model.md` supplies canonical meanings for work item, implementation proposal, implementation report, verification, and backlog closure.
- `GOV-FILE-BRIDGE-AUTHORITY-001` governs bridge authority and queue state.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` governs Codex helper fallback behavior for bridge governance paths.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` governs stale-source avoidance and live authority checks, directly matching citation freshness behavior.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` requires the project authorization, project, and work item metadata lines in this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` requires complete implementation proposal spec linkage and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` requires implementation-report evidence to map linked specs to executed tests.
- `GOV-STANDING-BACKLOG-001` supports closing WI-3267 only after durable verified completion evidence is present.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` supports linking the historical VERIFIED thread, restored tests, implementation report, and backlog resolution as one durable artifact chain.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` supports explicit open to verified to resolved lifecycle transitions for this item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` supports preserving concrete implementation and decision evidence as durable artifacts.

## Requirement Sufficiency

Existing requirements sufficient. WI-3267 and the verified historical bridge thread define the behavior to preserve: parse cross-thread bridge version references, compare them against live `bridge/INDEX.md`, emit stale-version warnings with cleanup hints, and provide reviewer-facing markdown output. No new requirement is needed before restoring tests.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Keep fixtures synthetic and credential-free. | Helper compliance audit and focused pytest. | |
| CQ-PATHS-001 | Yes | Keep restored test and optional source repair under in-root target paths. | Applicability preflight plus targeted tests. | |
| CQ-COMPLEXITY-001 | Yes | Restore focused tests around the existing CLI instead of redesigning the preflight. | Focused pytest coverage. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing status labels, warning keys, and bridge version parsing conventions. | Pytest assertions against output schema. | |
| CQ-SECURITY-001 | Yes | Avoid credential-shaped fixture values and external network calls. | Credential scan through helper and local-only pytest. | |
| CQ-DOCS-001 | Yes | Preserve reviewer-facing markdown behavior with tests rather than adding prose-only docs. | Markdown section assertions. | |
| CQ-TESTS-001 | Yes | Restore regression tests for fresh citations, stale citations, missing slugs, self-reference, JSON schema, markdown output, and advisory exit code. | `python -m pytest platform_tests/scripts/test_bridge_citation_freshness_preflight.py -q --tb=short`. | |
| CQ-LOGGING-001 | Yes | Preserve current CLI output and warning payload semantics. | Output schema and markdown assertions. | |
| CQ-VERIFICATION-001 | Yes | Run targeted pytest, ruff check, ruff format, and the live citation freshness preflight before filing the implementation report. | Commands listed in the verification plan. | |

## Scope

In scope:

- Restore `platform_tests/scripts/test_bridge_citation_freshness_preflight.py` with focused test cases for the verified citation-freshness behavior.
- Repair `scripts/bridge_citation_freshness_preflight.py` only if the restored tests expose a genuine source defect.
- Run the restored test file and the live CLI against the verified citation freshness bridge thread.
- Resolve WI-3267 in MemBase only after implementation-report verification evidence supports closure.

Out of scope:

- Redesigning bridge applicability preflight.
- Changing `bridge/INDEX.md` parsing semantics outside the citation freshness preflight.
- Broad bridge proposal template changes.
- Closing unrelated citation or stale-source work items.

## Acceptance Criteria

- `platform_tests/scripts/test_bridge_citation_freshness_preflight.py` exists in the live tree.
- Tests cover matching latest version with no warning, stale version warning, multiple warnings, missing referenced slug handling, self-reference suppression, JSON output schema, reviewer-facing markdown output, cleanup hint payload fields, and advisory zero exit code.
- The restored tests pass against the live script.
- The live command `python scripts/bridge_citation_freshness_preflight.py --bridge-id gtkb-bridge-citation-freshness-preflight` exits successfully and reports no stale self-reference defect.
- WI-3267 is resolved only after the post-implementation report receives Loyal Opposition VERIFIED.

## Specification-Derived Verification Plan

- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`: run `python -m pytest platform_tests/scripts/test_bridge_citation_freshness_preflight.py -q --tb=short` to prove stale and fresh live-state citation behavior.
- `GOV-FILE-BRIDGE-AUTHORITY-001` and `.claude/rules/file-bridge-protocol.md`: run `python scripts/bridge_citation_freshness_preflight.py --bridge-id gtkb-bridge-citation-freshness-preflight` against the live bridge INDEX thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-citation-freshness-test-restoration` after filing and include the packet in the implementation report.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: include all commands and observed results in the post-implementation report.
- Code quality: run `python -m ruff check scripts/bridge_citation_freshness_preflight.py platform_tests/scripts/test_bridge_citation_freshness_preflight.py`.
- Formatting: run `python -m ruff format --check scripts/bridge_citation_freshness_preflight.py platform_tests/scripts/test_bridge_citation_freshness_preflight.py`.

## Pre-Filing Preflight

- Manual catch-22 check performed before filing: proposal text cites the cross-cutting bridge governance specs, source-of-truth freshness spec, artifact-oriented governance specs, project-linkage specs, standing backlog spec, formal-artifact-approval evidence, and bridge authority spec triggered by the named target paths and proposal content.
- REVISED-2 was filed because the live clause preflight for NEW-1 reported a `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` evidence gap for the backlog-resolution target; this version cites the formal approval packet behind the active PAUTH.
- The Codex helper will run `.claude/hooks/bridge-compliance-gate.py --audit-only` against this in-memory content before writing `bridge/gtkb-bridge-citation-freshness-test-restoration-001.md`.
- After filing, Prime Builder will run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-citation-freshness-test-restoration`, `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-citation-freshness-test-restoration`, and `python scripts/bridge_citation_freshness_preflight.py --bridge-id gtkb-bridge-citation-freshness-test-restoration` and will revise if any blocking gap appears.

## Risk And Rollback

Risk: restored tests may reveal that the verified script drifted after prior verification. Mitigation: the proposal includes the source script target path for a narrow repair if the tests expose a genuine source defect.

Rollback: revert the restored test file and any narrow source repair from the implementation commit. The bridge audit chain remains append-only; any filed implementation report or LO verdict remains as historical evidence.
