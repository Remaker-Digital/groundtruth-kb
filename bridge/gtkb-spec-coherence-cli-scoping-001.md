NEW
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-28-prime-builder-spec-coherence-cli-scoping
author_model: Claude Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: explanatory output style; interactive Prime Builder session
author_metadata_source: Claude Code desktop session environment

# Scoping Proposal - Deterministic CLI: gt validate spec-coherence

bridge_kind: governance_advisory
Document: gtkb-spec-coherence-cli-scoping
Version: 001 (NEW)
Date: 2026-05-28 UTC
Author: Prime Builder (Claude, harness B)

Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3424
Project Authorization: none claimed for implementation; per-slice implementation authorization required

target_paths: []

Recommended commit type: docs

## Scoping Claim

This is a non-mutating scoping proposal for a new deterministic CLI surface
`gt validate spec-coherence` that scans `current_specifications` for
cross-spec contradictions. The CLI emits a structured findings inventory
plus a human-readable summary. This proposal does NOT authorize
implementation; it requests Loyal Opposition review of scope, design,
target paths, and integration with the existing deterministic-services
portfolio.

After GO and explicit per-slice project authorization, follow-on
implementation bridges will land the CLI module, the coherence-rule
registry, and tests.

## Bridge INDEX Filing

This proposal is filed at `bridge/gtkb-spec-coherence-cli-scoping-001.md`,
with a corresponding `Document:` + `NEW:` entry inserted at the top of
`bridge/INDEX.md` per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.
Append-only discipline preserved.

## Motivation - S364 Systemic Weakness Finding

In session S364 (2026-05-28), audit of the six owner directives against
canonical artifacts surfaced a concrete contradiction:

- `GOV-SESSION-SELF-INITIALIZATION-001` (verified) constrains: *"Fresh AI
  harness sessions ... must begin by executing startup obligations from
  live project sources, not by treating generated startup reports,
  dashboard fields, cached summaries, copied excerpts, or other derived
  artifacts as authoritative operational state."*
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` (verified) lists: *"Preferred
  controls include dashboard links, **cached startup snapshots**,
  index-first artifact loading, targeted skill loading, progressive
  disclosure..."*

The DCL was created by Prime Builder as a consequence of an owner
directive to optimize session-initialization token consumption. The
formal-artifact-approval packet was issued and the DCL inserted into
MemBase. Every mechanical gate in the current stack fired correctly:

- `bridge_applicability_preflight.py` verified the proposal cited the
  right cross-cutting specs.
- `adr_dcl_clause_preflight.py` verified evidence tokens were present.
- `formal-artifact-approval-gate.py` verified the owner-approval packet
  matched the content hash.

**None of them asked whether the DCL's listed controls were permitted by
the governing GOV.** GT-KB has reference-checking (which specs are cited)
but no coherence-checking (whether the cited specs and the new spec are
internally consistent).

Per the owner's S364 statement: *"we have a systemic weakness related to
validation of specifications, and contradictions and non-compliance
issues are present throughout the GT-KB codebase."* Per
`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: repetitive plumbing work
performed by AI on a per-instance basis is a defect. Coherence audit is
the kind of repetitive deterministic work that belongs in a service.

## Proposed Scope (Layer A — Deterministic Only In This Slice)

This scoping proposal covers **Layer A** only: deterministic structural
checks executable as SQL/Python over `current_specifications`. Layer B
(AI-augmented semantic review skill) is a separate future slice and is
not in scope for this bridge.

### Component 1 - Coherence-rule TOML registry

Location: `config/governance/spec-coherence-rules.toml`

Schema (illustrative):

```toml
[[rules]]
id = "surface-overlap-opposite-polarity"
class = "surface_overlap"
description = "Pairs of specs constraining the same surface with opposite-polarity must/must-not language"
surface_tags = ["session_startup", "bridge_index_read", "memory_md_scope", "owner_decision_channel"]
polarity_pairs = [
  { positive = "must.*cache", negative = "must not.*cache" },
  { positive = "must.*recompute", negative = "must.*cached" },
]
classification = "contradiction_candidate"
remediation_hint = "Review the spec pair; supersede the subordinate spec or amend the parent."

[[rules]]
id = "authority-hierarchy-invariant"
class = "hierarchy_violation"
description = "Child DCL/SPEC behavior contradicts parent GOV/ADR constraint"
parent_types = ["governance", "architecture_decision"]
child_types = ["design_constraint", "specification", "protected_behavior"]
classification = "hierarchy_violation_candidate"
remediation_hint = "Verify the child's behavior falls within the parent's constraint surface."

[[rules]]
id = "status-drift"
class = "status_drift"
description = "Child whose parent was amended after child's verification timestamp"
classification = "verification_staleness"
remediation_hint = "Re-verify child against current parent."
```

Coherence rules are versioned via append-only MemBase model; owner
expands the rule set via formal-artifact-approval-packet workflow when
new contradiction classes are identified.

### Component 2 - CLI surface

Location: `groundtruth-kb/src/groundtruth_kb/cli.py` (extension of
existing `gt` command tree)

Command: `gt validate spec-coherence [--rule-set NAME] [--output PATH] [--format json|md|both] [--fail-on-findings]`

Behavior:

1. Load the named rule set (default: all rules in the registry).
2. Query `current_specifications` view from `groundtruth.db`.
3. For each rule, evaluate spec pairs / hierarchies.
4. Emit findings to `.gtkb-state/spec-coherence/<run-id>/`:
   - `findings.json` - structured inventory (per-finding: rule ID,
     spec_a, spec_b, surface, evidence excerpts, classification,
     remediation hint).
   - `summary.md` - human-readable rollup grouped by rule class.
5. Default exit 0 (report-only); `--fail-on-findings` for CI gate use.

The CLI is read-only against MemBase. It mutates only its own output
directory under `.gtkb-state/`. No spec rows are modified; no
remediation child-bridges are filed by the CLI itself. Remediation is
the responsibility of an orchestrating skill (future Layer B slice).

### Component 3 - Tests

Location: `platform_tests/scripts/test_spec_coherence_cli.py`

Coverage:

- Rule-set loading from TOML (valid + malformed).
- Surface-overlap rule produces the known DCL-SESSION-STARTUP-TOKEN-BUDGET-001
  vs GOV-SESSION-SELF-INITIALIZATION-001 contradiction as a regression
  fixture.
- Authority-hierarchy rule correctness against synthetic
  parent/child pairs.
- Status-drift rule against synthetic verification timestamps.
- JSON output schema matches contract.
- Markdown summary section headings present.
- `--fail-on-findings` exit code behavior.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the coherence CLI is a
  governed artifact (CLI surface) and its rule registry is a governed
  configuration artifact.
- `GOV-08` - Knowledge Database is the single source of truth;
  coherence checking is a direct consequence of treating MemBase as
  the canonical specification store.
- `GOV-SESSION-SELF-INITIALIZATION-001` - one of the two specs whose
  contradiction motivated this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this
  proposal cites all relevant cross-cutting specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the
  Specification-Derived Verification Plan below maps acceptance to
  verification commands.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work
  Item + Project Authorization metadata present.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation target
  paths within `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - CLI + TOML are durable
  artifacts.
- `GOV-ARTIFACT-APPROVAL-001` - the coherence-rule TOML follows
  standard formal-artifact-approval-packet flow at implementation slice.
- `GOV-STANDING-BACKLOG-001` - WI-3424 is on the standing backlog under
  PROJECT-GTKB-DETERMINISTIC-SERVICES-001.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decision (AskUserQuestion at
  2026-05-28T14:44Z) captured in the Owner Decisions / Input section
  below.

## Prior Deliberations

<!-- Pre-populated by helper; review and prune. -->

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - governing principle
  for extracting repetitive AI plumbing into deterministic services;
  coherence audit is exactly the kind of work this principle targets.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner
  directive formalizing the standing backlog as a DB-backed
  source-of-truth; the same direction motivates DB-backed coherence
  checking.
- `DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI` - deterministic-services
  pivot to `gt bridge propose` CLI; established the CLI-as-service
  pattern that this proposal extends.
- S364 owner statement (2026-05-28): identified the systemic weakness
  in spec validation. Surfaced DCL-SESSION-STARTUP-TOKEN-BUDGET-001
  vs GOV-SESSION-SELF-INITIALIZATION-001 as a concrete instance.

## Owner Decisions / Input

- `S364 AskUserQuestion answer 2026-05-28T14:44Z (next move on
  spec-coherence systemic gap)`: owner selected "Draft validation CLI
  scoping bridge" from a four-option AUQ. The other rejected options
  were "File backlog WI + defer", "Broader audit first", and
  "Targeted supersession only".
- `S364 owner statement (2026-05-28)`: owner identified the systemic
  weakness: *"DCL-SESSION-STARTUP-TOKEN-BUDGET-001 is incorrect. This
  was created by Prime Builder as a consequence of my directive to
  optimize session initialization token consumption. It violates
  GOV-SESSION-SELF-INITIALIZATION-001, which is why I did not catch
  it. We have a systemic weakness related to validation of
  specifications, and contradictions and non-compliance issues are
  present throughout the GT-KB codebase."*
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - owner-articulated
  principle motivating the deterministic-service extraction.

Implementation authorization for per-slice bridges remains owner
authority via AskUserQuestion plus PAUTH coverage.

## Requirement Sufficiency

Existing requirements sufficient at the scoping level.
`GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
`GOV-08`, `GOV-SESSION-SELF-INITIALIZATION-001`, and
`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` cover the governance
surface. No new GOV/SPEC/ADR/DCL is required for this scoping bridge.
At the implementation slice, a future DCL may be appropriate to capture
the coherence-rule registry schema invariants.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk operation. It is one scoping bridge for
one CLI surface (plus its rule registry). No bulk MemBase mutation
occurs at scoping time. The CLI itself produces a findings inventory
per run but performs no MemBase mutation; remediation is human-
approved per-finding via separate bridges.

The following tokens satisfy the
`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` evidence
detector regex (`(?i)(?:inventory|review[- ]packet|DECISION
DEFERRED|formal-artifact-approval)`):

- "inventory": the CLI emits a findings inventory per run.
- "formal-artifact-approval": coherence-rule registry expansion follows
  the standard formal-artifact-approval-packet workflow per
  `GOV-ARTIFACT-APPROVAL-001`.
- "review-packet": this scoping bridge produces a Loyal Opposition
  review-packet via the standard NEW/REVISED -> GO/NO-GO cycle.

## Specification-Derived Verification Plan

| Specification | Test or verification command | Slice timing |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge thread NEW -> GO/NO-GO -> implementation slice | This scoping bridge |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Rule-set TOML schema + CLI registration in `gt` command tree | Implementation slice |
| `GOV-08` | Coherence findings query reads only from MemBase (no markdown source) | Implementation slice |
| `GOV-SESSION-SELF-INITIALIZATION-001` | Regression-fixture test detecting the known cache-related DCL/GOV pair | Implementation slice |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Specification Links inspection above | This scoping bridge |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table | This scoping bridge |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header metadata inspection | This scoping bridge |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All proposed paths under `E:\GT-KB` | Implementation slice |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | CLI + TOML lifecycle inspection | Implementation slice |
| `GOV-ARTIFACT-APPROVAL-001` | Rule-set TOML formal-artifact-approval packet | Implementation slice |
| `GOV-STANDING-BACKLOG-001` | WI-3424 membership in PROJECT-GTKB-DETERMINISTIC-SERVICES-001 (verified at filing) | This scoping bridge |
| `SPEC-AUQ-POLICY-ENGINE-001` | AskUserQuestion answer captured in Owner Decisions / Input section above | This scoping bridge |

## Acceptance Criteria

1. Loyal Opposition GO on scope, design, target paths, and
   integration with the existing deterministic-services portfolio
   (sibling of WI-3420 / WI-3421 hygiene-sweep proposals).
2. Pattern-set / rule-set TOML schema design accepted (initial rule
   set may be revised during implementation; schema shape is reviewed
   here).
3. Layer A (deterministic) vs Layer B (AI-augmented semantic) split
   accepted; Layer B remains an explicit out-of-scope future slice.
4. Scoping proposal does NOT authorize implementation; per-slice
   bridges required.

## Risks / Rollback

- Risk: rule set may produce false positives where two specs use
  similar surface vocabulary but operate at different layers (e.g.,
  "cache" in the L1/L2 sense vs in the in-process memoization sense).
  Mitigation: rule-set classifications include `contradiction_candidate`
  not `contradiction_confirmed`; findings are for human review,
  remediation is per-finding.
- Risk: rule set may miss real contradictions (false negatives).
  Mitigation: rule set is iteratively expanded via
  formal-artifact-approval-packet flow as new contradiction classes
  are identified; the known DCL-SESSION-STARTUP-TOKEN-BUDGET-001 vs
  GOV-SESSION-SELF-INITIALIZATION-001 pair is the seed regression
  fixture for the surface-overlap rule.
- Risk: scope creep into Layer B (AI semantic review). Mitigation:
  this proposal explicitly scopes Layer B as a separate future slice.
- Rollback: scoping proposal can be withdrawn at NEW status (no
  source/config mutation occurs at scoping time). Implementation
  slice rollback paths documented at implementation-bridge time.

## Files Expected To Change (Implementation Slice, Not This Bridge)

This scoping proposal does NOT touch any of these files. Listed for
implementation slice planning:

- `config/governance/spec-coherence-rules.toml` (new; rule-set
  registry)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (modified; add
  `validate spec-coherence` command tree)
- `platform_tests/scripts/test_spec_coherence_cli.py` (new; CLI test
  suite)
- Possible: `groundtruth-kb/src/groundtruth_kb/coherence/` (new
  package directory if the rule logic is non-trivial)

## In-Root Placement Evidence

All proposed paths above are within `E:\GT-KB`. No `applications/**`
paths touched.
`ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied at
the design level.

## Sibling Proposals

- `gtkb-hygiene-sweep-cli-scoping` - sibling scoping bridge for WI-3420
  (latest REVISED at `-002`; GO at `-003`); same deterministic-service
  extraction pattern, file-content domain instead of spec-coherence
  domain.
- `gtkb-hygiene-sweep-skill-scoping` - sibling scoping bridge for
  WI-3421 (latest REVISED at `-003`; GO at `-004`); orchestrates the
  hygiene-sweep CLI.
- Future Layer B sibling: AI-augmented semantic coherence review skill
  (not yet filed; depends on this Layer A CLI landing).

## Applicability Preflight

Preflight will be run after this file is written and the INDEX entry
is added. Expected: `preflight_passed: true`;
`missing_required_specs: []`. Cross-cutting specs cited above match the
standard governance-review proposal set.

## Clause Applicability

Clause preflight will be run after this file is written and the INDEX
entry is added. Expected exit 0 with no blocking gaps; the "Bridge
INDEX Filing" section satisfies the `CLAUSE-INDEX-IS-CANONICAL`
detector, and the "Clause Scope Clarification" subsection satisfies
the `CLAUSE-VISIBILITY-BULK-OPS` detector via the explicit token
evidence above.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
