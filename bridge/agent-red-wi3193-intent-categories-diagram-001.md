NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: harness-state registry plus current Codex runtime

# Implementation Proposal - WI-3193 Intent Categories Diagram Legibility Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3193-intent-categories-diagram
Version: 001 (NEW)
Date: 2026-06-23 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3193

target_paths: ["applications/Agent_Red/docs-site/docs/getting-started/how-it-works.md", "applications/Agent_Red/docs-site/docs-inventory.yml", "applications/Agent_Red/tests/multi_tenant/test_how_it_works_spec1741.py"]

## Claim

WI-3193 can be implemented as a narrow documentation-source and test-coverage change for `SPEC-1741`.

The current `applications/Agent_Red/docs-site/docs/getting-started/how-it-works.md` intent classifier section already uses a Mermaid `flowchart TB` block rather than a `mindmap`, but the 18-class intent diagram has no explicit node styling. That leaves the SPEC-1741 legibility requirement untested and vulnerable to regression. The docs inventory also still describes this section as a "mindmap diagram", which should be corrected when the source diagram is made explicitly styled.

This proposal authorizes only:

- add explicit Mermaid `classDef`/`class` styling to the intent-category flowchart so every leaf intent node uses a light pastel background and dark text, with the order-related nodes specifically covered;
- update `docs-inventory.yml` wording from the obsolete mindmap description to the styled flowchart description; and
- add deterministic pytest coverage that parses the source markdown and inventory entry.

This proposal does not authorize runtime code, generated static HTML, credentials, deployment state, formal GT-KB artifacts, or project membership changes. If generated static docs need a broader refresh, that should remain separate from this WI and from the already-open related documentation-static gaps.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1741` directly states the required behavior: the 17 customer-facing intent categories diagram in `how-it-works.md` must use explicitly styled flowchart nodes instead of Mermaid mindmap auto-coloring, and all leaf nodes must use light pastel backgrounds with dark text. It also identifies the source path. No new requirement or owner clarification is needed before implementation.

## In-Root Placement Evidence

All target paths are under the GT-KB root and Agent Red application subtree:

- `E:\GT-KB\applications\Agent_Red\docs-site\docs\getting-started\how-it-works.md`
- `E:\GT-KB\applications\Agent_Red\docs-site\docs-inventory.yml`
- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_how_it_works_spec1741.py`

## Specification Links

- `SPEC-1741` - Direct target requirement for the intent categories diagram: flowchart instead of mindmap auto-coloring, light pastel backgrounds, dark text, and Orders-branch legibility.
- `SPEC-0803` - Documentation diagram requirement; the implementation keeps the diagram in Mermaid and makes its styling deterministic.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the docs-source artifact and docs inventory are the surfaces under test.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native pytest evidence must validate the documentation artifact rather than rely on manual inspection.
- `GOV-12` - Work-item remediation must create test evidence.
- `GOV-13` - Test visibility/phase governance; repository-native pytest mappings are live spec-to-test evidence under the current FAB-11 amendment.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, GO, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies the baseline Python lint and formatting checks to the new test file.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority, role eligibility, and numbered append-only bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this proposal to cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires implementation verification to map linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms Agent Red application artifacts live under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this proposal uses the existing authorized WI and does not add project scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use the governed bridge helper path and explicit preflight evidence rather than assuming hook parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this implementation proposal as a lifecycle artifact for the work item.

## Owner Decisions / Input

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside the snapshot-bound project member `WI-3193`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- _No WI-specific prior bridge deliberation: `gt bridge threads --wi WI-3193 --json` returned `match_count: 0` before this NEW proposal._

## Proposed Scope

1. In `applications/Agent_Red/docs-site/docs/getting-started/how-it-works.md`, update only the intent-classifier Mermaid block:
   - keep `flowchart TB`;
   - avoid `mindmap`;
   - add explicit `classDef` definitions with light pastel fills and dark text;
   - assign every leaf intent node (`C1` through `C17` and `A1`) to a styled class;
   - ensure order-related leaf nodes such as `order_status`, `return_request`, `exchange_request`, `refund_request`, and `shipping_inquiry` are assigned to a light-background/dark-text class.
2. In `applications/Agent_Red/docs-site/docs-inventory.yml`, update the Intent Classification explanation note so it no longer says "mindmap diagram" and instead reflects the styled flowchart diagram.
3. Add `applications/Agent_Red/tests/multi_tenant/test_how_it_works_spec1741.py`:
   - parse the source markdown;
   - isolate the Mermaid block following the intent-classifier paragraph;
   - assert it is a flowchart and not a mindmap;
   - assert every leaf intent node is present and class-assigned;
   - assert every used leaf class has a light pastel fill and dark text;
   - assert the Orders-related leaf nodes are styled by a dark-text class;
   - assert the docs inventory no longer uses the stale mindmap wording.

## Pre-Filing Preflight Evidence

Applicability preflight:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3193-intent-categories-diagram-001.md --json
```

Observed:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `packet_hash: sha256:8962b2ac41addd9f8ce60d597ee94d392ff33671abb4712923a65b0da9e5b269`
- warning only: parser harvested bare `tests/multi_tenant/test_how_it_works_spec1741.py` from command text; declared target paths remain in-root under `applications/Agent_Red/`.

Clause preflight:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3193-intent-categories-diagram-001.md
```

Observed:

- clauses evaluated: `5`
- must_apply: `4`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1741` | New pytest parses `how-it-works.md` and verifies the intent diagram is `flowchart TB`, contains no `mindmap`, has all leaf intent nodes, assigns all leaf nodes to explicit classes, and uses dark text on light pastel fills, including order-related nodes. |
| `SPEC-0803` | New pytest verifies the diagram remains inside a Mermaid fenced block rather than being replaced by prose-only documentation. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against the new deterministic docs test file. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3193-intent-categories-diagram`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check` and `ruff format --check` on the new test file. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/multi_tenant/test_how_it_works_spec1741.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/multi_tenant/test_how_it_works_spec1741.py
python -m ruff format --check applications/Agent_Red/tests/multi_tenant/test_how_it_works_spec1741.py
```

## Acceptance Criteria

- PASS when the intent diagram source is a Mermaid flowchart, not a Mermaid mindmap.
- PASS when every leaf intent node has an explicit class assignment.
- PASS when every leaf class used by the intent nodes declares a light pastel `fill` and dark `color`.
- PASS when the order-related intent nodes are covered by the dark-text/light-background styling checks.
- PASS when `docs-inventory.yml` no longer describes the intent classification explanation as a mindmap.
- PASS when the targeted pytest and ruff commands all pass.
- PASS when no runtime code, generated static HTML, credentials, deployment state, formal artifacts, project membership, or new WIs are changed.

## Risks / Rollback

Risk is low. The implementation changes one docs-source Mermaid block, one docs inventory note, and one focused pytest file. Mermaid class definitions are stable source text and do not invoke network, browser, credentials, or deployment behavior during tests.

Rollback is to revert the WI-3193 hunks in `how-it-works.md` and `docs-inventory.yml`, and delete `test_how_it_works_spec1741.py`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/docs-site/docs/getting-started/how-it-works.md`
- `applications/Agent_Red/docs-site/docs-inventory.yml`
- `applications/Agent_Red/tests/multi_tenant/test_how_it_works_spec1741.py`

## Recommended Commit Type

`test:`
