REVISED

# Implementation Proposal - Bridge Citation Freshness Preflight (WI-3267)

bridge_kind: implementation_proposal
Document: gtkb-bridge-citation-freshness-preflight
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-3267

target_paths: ["scripts/bridge_citation_freshness_preflight.py", "platform_tests/scripts/test_bridge_citation_freshness_preflight.py"]

This REVISED proposal (`-003`) addresses the `-002` NO-GO on the WI-3267 citation-freshness preflight. It adds a preflight that warns when a bridge proposal cites another bridge thread by version that has since been superseded. Per WI-3267, `gtkb-advisory-report-protocol-extension-001` cited `gtkb-bridge-advisory-status-001` as 'REVISED-3 at -007' but it was already NO-GO at -008 by review time, triggering an F1 NO-GO; this preflight catches that class of staleness before review.

## Revision Notes

The `-002` NO-GO raised two findings. Both are addressed in `-003`:

- **F1 (P1 governance drift) - test path outside the active platform test lane.** Addressed. `target_paths` and the verification command are repointed from `tests/scripts/test_bridge_citation_freshness_preflight.py` to `platform_tests/scripts/test_bridge_citation_freshness_preflight.py`. `pyproject.toml` `testpaths` is `platform_tests` and `applications/Agent_Red/tests`, and `.github/workflows/groundtruth-kb-tests.yml` runs `python -m pytest platform_tests/ -q --tb=short`, so the test now lives in the lane the platform pytest run and CI exercise (sibling existing file `platform_tests/scripts/test_bridge_applicability_preflight.py`).
- **F2 (P2 capability overclaim) - proposal omitted part of WI-3267's acceptance surface.** Addressed. WI-3267's acceptance text reads: "Slice 1 acceptance: detector handles N=2 fixture cases (workflow-contract-adr vs runtime thread) + emits cleanup hint + reviewer-facing markdown section that Codex can cite." The `## Proposed Scope` section now requires (a) a reviewer-facing cleanup / suggested-update hint in every stale-citation warning payload, and (b) a reviewer-citeable markdown section. The `## Specification-Derived Verification Plan` adds explicit tests pinning the two named N=2 fixture cases (the workflow-contract-ADR citation case and the runtime-thread citation case) and the citeable markdown section.

No scope change beyond the F1/F2 corrections: the change remains a single new advisory preflight script plus its regression tests.

## Claim

A new preflight scans bridge proposal content for cross-thread version citations (regex patterns `bridge/<slug>-NNN.md` and `<status>-N at -NNN` near `<slug>` references), looks up each cited slug in `bridge/INDEX.md` to determine the current latest version, and warns when the cited version is not the latest. Each stale-citation warning carries the latest version (the suggested updated citation) and a reviewer-facing cleanup hint. The preflight emits a reviewer-citeable `Citation Freshness` markdown section and exits 0 (advisory, non-blocking).

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` is canonical bridge workflow state; this preflight reads INDEX as the authority for current latest version.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cross-cutting constraint requiring this proposal to cite every relevant governing specification; citation-freshness checking extends the linkage discipline to cross-thread version references.
- `SPEC-AUQ-POLICY-ENGINE-001` - the preflight is part of the deterministic preflight / policy-engine surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root-only placement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cross-cutting constraint requiring the post-implementation VERIFIED step to rest on executed spec-derived tests; the verification plan maps every linked spec to a test.
- `GOV-STANDING-BACKLOG-001` - WI-3267 is a tracked standing-backlog work item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, bridge thread, the new script, and linked specs form the artifact graph for this work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the observed stale-citation defect triggered WI-3267 which triggers this implementation proposal and its tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; this fix is captured as governed work (WI-3267) with a bridge artifact and spec-derived tests.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - records the owner decision authorizing the project grouping `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` that includes WI-3267.
- `DELIB-1878` - records the related `gtkb-bridge-advisory-status-001` thread (latest status NO-GO), the exact stale cross-thread citation problem this WI is intended to reduce.

No prior deliberation rejected a citation-freshness preflight; this is the first proposal to add one.

## Owner Decisions / Input

This proposal depends on owner approval and is authorized by:

- 2026-05-14 UTC, S350+: owner approved the `GTKB-BRIDGE-PROTOCOL-RELIABILITY` project authorization including WI-3267, captured as the AskUserQuestion decision archived in `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` (formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`). Implementation proceeds autonomously through the bridge protocol under that project authorization; no new per-fix owner decision is required.

## Requirement Sufficiency

Existing requirements sufficient. WI-3267's description specifies the preflight, the observed-defect motivation, the N=2 fixture cases, the cleanup hint, and the reviewer-facing markdown section. No new or revised requirement or specification is created by this work; it implements an already-tracked work item against existing bridge-protocol specifications.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-WI new-tool change. It is not a bulk backlog operation: it performs no batch resolve, promote, or retire of work items or specifications. References to "work item", "backlog", and "standing backlog" describe the single work item WI-3267 and its governed filing path only. The applicable evidence pattern is a single-WI tooling implementation proposal with formal-artifact-approval discipline preserved unchanged; the review-packet inventory is IP-1 + IP-2 in this single thread.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow state. The `-003` REVISED line is inserted at the top of the `gtkb-bridge-citation-freshness-preflight` document block in `bridge/INDEX.md`; no INDEX entry is removed or rewritten. The new preflight READS `bridge/INDEX.md` as the authority for current latest version and does not mutate it.

## Proposed Scope

### IP-1: Citation freshness preflight script

`scripts/bridge_citation_freshness_preflight.py`:

CLI: `python scripts/bridge_citation_freshness_preflight.py --bridge-id <id>`.

Logic:

1. Resolve and read the proposal at `bridge/<bridge-id>-NNN.md` (the latest version, consistent with how the existing applicability preflight resolves the operative file).
2. Extract all cross-thread citation patterns from the proposal body:
   - `bridge/<slug>-NNN.md` - a full bridge path with an explicit version.
   - `(?:NEW|REVISED|GO|NO-GO|VERIFIED)(?:-\d+)? at -(\d+)` - a status-with-version reference appearing near a `<slug>` reference.
   Self-references (citations whose `<slug>` equals `<bridge-id>`) are excluded so a proposal does not flag its own version chain.
3. For each cited `(slug, version)`, look up the slug's `Document:` block in `bridge/INDEX.md` and determine its current latest (top-of-block) version.
4. **Stale-citation warning payload (F2).** When the cited version is not the latest, emit a warning entry in the output JSON. Each warning entry carries:
   - `cited_slug` - the cited bridge slug.
   - `cited_version` - the version the proposal cited.
   - `latest_version` - the current latest version per `bridge/INDEX.md` (this IS the suggested updated citation).
   - `latest_status` - the current latest status per `bridge/INDEX.md` (e.g. `NO-GO`, `VERIFIED`), so the reviewer sees whether the cited thread changed verdict.
   - `severity` - `"warn"` (advisory).
   - `cleanup_hint` - a reviewer-facing actionable string, e.g. `"Citation of bridge/<slug>-<cited_version>.md is stale; bridge/<slug>-<latest_version>.md is the current latest version (status <latest_status>). Update the citation or document why the historical version is intentionally cited."`.
5. **Reviewer-citeable markdown section (F2).** Render the warnings as a markdown table inside a `## Citation Freshness` section with a stable, citeable heading. When there are no stale citations, the section states `No stale cross-thread citations detected.` so a reviewer can cite a clean result.
6. The preflight always exits 0 (advisory, non-blocking) per the WI's advisory intent; reviewer judgment decides whether a flagged historical citation is intentional.

### IP-2: Tests (platform_tests lane)

Tests are added under `platform_tests/scripts/test_bridge_citation_freshness_preflight.py`.

The two named WI-3267 fixture cases are pinned explicitly:

- **Fixture case A - workflow-contract-ADR citation.** A fixture proposal cites a slug whose `Document:` block in a fixture INDEX represents a workflow-contract / ADR-style thread, with the cited version one behind the latest. The test asserts a stale warning with the correct `latest_version`, `latest_status`, and `cleanup_hint`.
- **Fixture case B - runtime-thread citation.** A fixture proposal cites a slug whose `Document:` block represents a runtime (implementation) thread, again with the cited version behind the latest. The test asserts the corresponding stale warning.

## Specification-Derived Verification Plan

Each linked specification maps to at least one test.

| Behavior / Spec coverage | Test | Covers |
|---|---|---|
| A citation whose version equals the INDEX latest produces no warning | `test_matching_version_no_warning` | `GOV-FILE-BRIDGE-AUTHORITY-001` |
| A citation whose version is behind the INDEX latest produces a stale warning | `test_stale_version_warning` | `GOV-FILE-BRIDGE-AUTHORITY-001` |
| A proposal with multiple stale citations produces one warning per citation | `test_multi_citation_warnings` | `GOV-FILE-BRIDGE-AUTHORITY-001` |
| A citation to a slug absent from `bridge/INDEX.md` is reported gracefully (no crash) | `test_slug_not_in_index_handled` | `GOV-FILE-BRIDGE-AUTHORITY-001` |
| WI-3267 fixture case A - workflow-contract-ADR citation produces the expected stale warning | `test_wi3267_fixture_workflow_contract_adr_citation` | WI-3267 acceptance, `GOV-STANDING-BACKLOG-001` |
| WI-3267 fixture case B - runtime-thread citation produces the expected stale warning | `test_wi3267_fixture_runtime_thread_citation` | WI-3267 acceptance, `GOV-STANDING-BACKLOG-001` |
| Each stale-citation warning payload carries `latest_version` (suggested updated citation) and a reviewer-facing `cleanup_hint` | `test_warning_payload_includes_latest_version_and_cleanup_hint` | WI-3267 acceptance, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |
| The preflight emits a stable, reviewer-citeable `## Citation Freshness` markdown section (both the stale-warnings case and the clean case) | `test_citeable_markdown_section_emitted` | WI-3267 acceptance, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` |
| A proposal does not flag citations of its own version chain (self-reference exclusion) | `test_self_reference_not_flagged` | `GOV-FILE-BRIDGE-AUTHORITY-001` |
| JSON output conforms to the documented schema | `test_json_output_schema` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |
| The preflight exits 0 (advisory, non-blocking) | `test_exit_code_advisory_zero` | WI-3267 acceptance |
| In-root placement: no target path is outside `E:\GT-KB` | covered by `target_paths` enumeration above | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` |
| Proposal cites all governing specs; this is a tracked WI | covered by `## Specification Links` and the WI-3267 metadata above | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` |

Verification command:

```
python -m pytest platform_tests/scripts/test_bridge_citation_freshness_preflight.py -q --tb=short
python -m ruff check scripts/bridge_citation_freshness_preflight.py
```

## Files Expected To Change

- `scripts/bridge_citation_freshness_preflight.py` - new advisory preflight script implementing IP-1.
- `platform_tests/scripts/test_bridge_citation_freshness_preflight.py` - new test file holding the verification-plan tests, including the two named WI-3267 fixture cases.

## Acceptance Criteria

- IP-1 and IP-2 landed; all tests in the verification plan PASS via the platform test lane.
- Both bridge preflights PASS on `-003`.
- Every stale-citation warning carries `latest_version` (the suggested updated citation), `latest_status`, and a reviewer-facing `cleanup_hint`.
- The preflight emits a stable, reviewer-citeable `## Citation Freshness` markdown section.
- The two named WI-3267 fixture cases (workflow-contract-ADR, runtime-thread) are covered by explicit passing tests.
- The preflight exits 0 (advisory, non-blocking).
- `ruff check` is clean on the new script.

## Risks / Rollback

- Risk: citations sometimes intentionally reference historical versions (e.g. "NO-GO at -002" when describing prior revision history). Mitigation: severity is advisory, not blocking; the `cleanup_hint` explicitly tells the reviewer to update or document the intentional historical citation; the self-reference exclusion avoids the most common false positive.
- Risk: the regex could mis-extract a non-citation token. Mitigation: the patterns are anchored to the `bridge/<slug>-NNN.md` path form and the status-with-version form; tests pin both extraction patterns.
- Rollback: remove `scripts/bridge_citation_freshness_preflight.py` and its test file; nothing else depends on the new script.

## Recommended Commit Type

`feat:` - new advisory preflight tool (net-new capability surface) plus tests.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this `-003` content after the `bridge/INDEX.md` `REVISED` entry was added; outputs are embedded in the `## Applicability Preflight` and `## Clause Applicability` sections below.

## Review Questions for Loyal Opposition

1. Is the `cleanup_hint` wording actionable enough for a reviewer, or should it propose an exact replacement line?
2. Are the two fixture cases (workflow-contract-ADR vs runtime-thread) the right interpretation of WI-3267's "N=2 fixture cases"?
3. Should the self-reference exclusion be configurable?

## Applicability Preflight

- packet_hash: `sha256:2a7202b539c27f039e0baa2da1cf2da8eabb628c58a7a7375ce91dd0154fa0bf`
- bridge_document_name: `gtkb-bridge-citation-freshness-preflight`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-citation-freshness-preflight-003.md`
- operative_file: `bridge/gtkb-bridge-citation-freshness-preflight-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-bridge-citation-freshness-preflight`
- Operative file: `bridge\gtkb-bridge-citation-freshness-preflight-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Clause preflight exit code: 0 (pass; zero blocking gaps).

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
