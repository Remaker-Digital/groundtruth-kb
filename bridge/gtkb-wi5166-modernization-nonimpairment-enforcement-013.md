REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f69a3-25dd-75e1-83d6-8c4aa29fb912
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined role; owner-directed revision worker

# Revised Implementation Proposal - WI-5166 First Non-Impairment Enforcement Slice

bridge_kind: prime_proposal
Document: gtkb-wi5166-modernization-nonimpairment-enforcement
Version: 013
Responds to: bridge/gtkb-wi5166-modernization-nonimpairment-enforcement-012.md
Revises: bridge/gtkb-wi5166-modernization-nonimpairment-enforcement-007.md
Date: 2026-07-17 UTC
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5166
target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "scripts/check_modernization_nonimpairment.py", "platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py", "platform_tests/scripts/test_modernization_nonimpairment.py"]

## Revision Claim

This revision selects the least-change correction endorsed by version 011 and
required by version 012. It preserves the bounded first WI-5166 enforcement
slice and changes only the parity and focused-test acceptance model: parity is
AST and behavioral equality of the named non-impairment semantic nodes and the
`NONIMPAIRMENT_GOV_ID`-conditioned denial branch, not whole-file byte identity.
The two pre-existing applicability-preflight whole-file differences remain
foreign, accepted, and excluded. The focused test fixture may be isolated from
the unrelated live project-membership gate so the non-impairment behavior is
tested directly.

This remains the first bounded WI-5166 slice, not completion of WI-5166. A GO,
claim, successful implementation-start packet, implementation report, and
independent VERIFIED remain mandatory. No implementation target is mutated by
this revision.

## Requirement Sufficiency

Existing requirements sufficient. Version 012 identifies an internal
technical contradiction and explicitly offers the semantic-parity correction;
version 011 demonstrates the bounded fixture-isolation repair. Neither change
alters product policy, adds a target, expands the PAUTH, or claims completion.
No new owner decision is needed.

The original five-target envelope, deterministic report-only evaluator,
structured proposal gate, first-slice non-completion boundary, foreign-hunk
exclusions, remaining-work obligations, and independent verification contract
remain authoritative except where this revision expressly replaces whole-file
byte identity with semantic-node and behavior equality.

## In-Root Placement Evidence

All five targets are within `E:\GT-KB`. No external path, adopter-application
path, credential surface, deployment surface, or alternate bridge runtime is
introduced.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-STANDING-BACKLOG-001`

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-NONIMPAIRMENT-GOV-FORMALIZATION-RESULT`
  establishes the four modernization non-impairment enforcement obligations.
- `DELIB-202666274` authorizes the modernization program at project scope while
  preserving bridge, claim/start, verification, and mechanical finalization
  gates.
- `DELIB-202666217` establishes that report-only evaluators remain
  non-activating evidence.
- `DELIB-202666232` establishes exact hunk-patch finalization discipline for
  mixed-ownership files.
- `DELIB-202665664` requires evidence freshness and exact-byte provenance.
- `DELIB-20265396` records prior bridge-compliance active/template parity. This
  revision preserves semantic parity for the owned non-impairment behavior while
  expressly accepting unrelated pre-existing whole-file differences.
- Versions 001 through 012 of this thread form the append-only proposal,
  review, dependency, executability, and correction history for this revision.

## Owner Decisions / Input

No new owner decision is required or inferred. The active project PAUTH and
the deliberations above authorize this bounded first slice. Version 012
expressly permits the least-change semantic-parity correction, and version 011
supplies reproducible evidence for the test-fixture isolation. Git commit,
push, release, deployment, credential lifecycle, destructive cleanup, history
rewrite, and unrelated project work remain outside authority.

## Findings Addressed

### [P1] Whole-file parity contradicts foreign-hunk exclusion

Accepted. Replace every whole-file byte-identity acceptance statement from
versions 001, 003, and 007 with this narrower contract:

1. The four named `NONIMPAIRMENT_*` constant assignments are AST-equivalent.
2. `_nonimpairment_value_is_concrete` and
   `_nonimpairment_disposition_gap` are AST-equivalent.
3. The `NONIMPAIRMENT_GOV_ID`-conditioned denial branch in
   `_deny_reason_for_content` is AST-equivalent and behaviorally equivalent.
4. Focused valid, missing, malformed, duplicate, incomplete, and placeholder
   cases produce the same accept/deny behavior and stable diagnostic semantics
   through both hook copies.

The active and template files are not required to be byte-identical. Their two
pre-existing applicability-preflight differences are accepted as excluded
baseline variance: the template additionally checks `blocking_errors`, and its
denial diagnostic reports the complete preflight packet. Neither difference
may be adopted, removed, reformatted, staged, attributed, or finalized by this
slice.

### [P1] Focused fixture is intercepted by unrelated project membership

Accepted. The focused hook-test fixture may receive the minimum deterministic
isolation needed to exercise the named non-impairment branch without being
intercepted by the unrelated live project-membership gate. The isolation must
be confined to
`platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py`, must
not weaken production membership enforcement, and must not alter the active or
template hook's project-membership behavior. Evidence must show that the same
focused suite moves from the observed 16 passed / 4 membership-intercepted
failures to 20 passed.

## Proposed Scope

### IP-1 - Deterministic report-only evaluator

Adopt `scripts/check_modernization_nonimpairment.py` as the deterministic,
non-activating evaluator for baseline, result, rollback, and hard-invariant
evidence. It remains report-only and performs no activation, routing,
dispatcher, harness, Git, database, credential, or external-system mutation.

### IP-2 - Structured proposal gate with semantic parity

Adopt only the named non-impairment nodes in both hook copies: the four
`NONIMPAIRMENT_*` constants, the two helper functions, and the
`NONIMPAIRMENT_GOV_ID`-conditioned denial branch. Require AST and behavioral
equality of those nodes. Preserve all bytes and semantics of the excluded
applicability-preflight differences and all other foreign hunks.

### IP-3 - Focused regressions and fixture isolation

Adopt the two focused test modules, including the minimum test-only fixture
isolation required to bypass the unrelated membership prerequisite and reach
the non-impairment branch. Correct only bounded Ruff/format findings in owned
content. No production membership gate or unrelated test behavior may change.

### IP-4 - Exact evidence and finalization boundary

Record pre/post SHA-256 for all five targets, AST extracts or a deterministic
AST comparison for each named node, focused behavioral results through each
hook copy, the exact fixture-isolation diff, Ruff results, and a patch manifest.
The manifest may select only the named hook nodes, the bounded test fixture,
and the three whole candidate files. Any later finalizer requires independent
VERIFIED and separate exact mechanical authority.

## Exact Target And Foreign-Hunk Boundary

The implementation envelope remains exactly:

1. `.claude/hooks/bridge-compliance-gate.py`
2. `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
3. `scripts/check_modernization_nonimpairment.py`
4. `platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py`
5. `platform_tests/scripts/test_modernization_nonimpairment.py`

Within the two hook files, this slice owns only the named non-impairment AST
nodes and conditioned denial branch. The `_run_pending_applicability_preflight`
`blocking_errors` difference, complete-packet versus `missing_required_specs`
diagnostic difference, line-ending state, and every other foreign hunk remain
excluded. Whole-file hook replacement, formatting, staging, or finalization is
prohibited.

## Remaining WI-5166 Scope (Out Of This Slice)

1. Wire the evaluator into verification and closure so missing hard-invariant
   evidence mechanically blocks both gates under GOV MUST (c).
2. Implement the thirteen-suite hard-invariant orchestrator spanning bridge,
   dispatcher, role, project, backlog, Git, skill, CLI, startup, activity,
   assertion, doctor, and governance regressions.
3. Complete superseded-worker-loading enforcement under GOV MUST (d),
   separately owned by WI-5154, then integrate its evidence into WI-5166
   closure.
4. Only after those obligations are independently verified may WI-5166 be
   considered for resolution.

This revision and any later VERIFIED for this slice must not resolve, close, or
otherwise represent completion of WI-5166.

## Cross-Harness Disposition

All supported harnesses continue through the shared governed bridge filing
path. Semantic parity of the owned non-impairment nodes gives each harness the
same proposal-disposition behavior while preserving unrelated active/template
applicability-preflight evolution.

| Harness | Disposition | Rationale |
| --- | --- | --- |
| Claude Code | behavioral parity | The active hook enforces the owned semantic nodes. |
| Codex | behavioral parity | Governed Codex filing invokes the shared active compliance path. |
| Cursor | behavioral parity | Cursor-authored proposals use the shared bridge filing path. |
| Antigravity | behavioral parity | Antigravity-authored proposals use the shared bridge filing path. |
| Ollama | behavioral parity | Headless work remains bound to shared bridge artifacts and validation. |
| OpenRouter | behavioral parity | Provider-backed work remains bound to shared bridge artifacts and validation. |
| Alibaba | behavioral parity | Provider-backed work remains bound to shared bridge artifacts and validation. |
| Packaged adopters | behavioral parity | The packaged hook carries AST- and behavior-equivalent owned non-impairment nodes; unrelated applicability-preflight variance remains accepted. |

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5166 and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "canonical_authority": "The governed specification and project PAUTH remain authoritative; this first slice is enforcement evidence, not WI-5166 closure.",
  "primary_route": "Authors use the governed proposal scaffold and bridge filing CLI; shared gate behavior validates structured evidence.",
  "before_behavior": "Applicable modernization proposals could omit or partially populate non-impairment evidence.",
  "after_behavior": "Applicable proposals carry concrete structured evidence; both hook copies enforce AST- and behavior-equivalent non-impairment logic while unrelated applicability-preflight differences remain outside this slice.",
  "self_descriptive_naming": "The disposition heading and named NONIMPAIRMENT semantic nodes state their enforcement purpose.",
  "obsolete_guidance_disposition": "Whole-file byte identity is superseded for this slice by semantic-node and behavioral equality; prose-only or partial disposition guidance remains superseded by the structured contract.",
  "history_preservation": "Prior bridge history and excluded foreign hook hunks remain unchanged; only exact owned hunks are eligible for later finalization.",
  "baseline": "Exact target hashes, named AST nodes, focused behavior, and excluded applicability-preflight differences are recorded before implementation.",
  "expected_result": "Twenty focused tests pass through bounded fixture isolation, owned hook nodes are AST- and behavior-equivalent, and WI-5166 remains open.",
  "rollback": "Revert only the named non-impairment hook nodes, bounded test-fixture isolation, and three candidate files through separately governed exact mechanics.",
  "hard_invariants": ["no bridge bypass", "no foreign-hunk absorption", "no production membership-gate weakening", "no activation or routing mutation", "WI-5166 remains open", "independent VERIFIED before slice completion"],
  "fail_closed_conditions": ["missing or malformed disposition", "placeholder values", "owned AST-node mismatch", "focused behavioral mismatch", "baseline hash drift", "foreign applicability-preflight hunk selected", "attempt to close WI-5166 from this slice"],
  "essential_context_preservation": "Project, work item, specification, deliberation, target-byte, semantic-node, fixture-isolation, foreign-ownership, and remaining-scope evidence remain explicit."
}
```

## Candidate Preflights

Before live filing, the governed `revise_bridge.py file` helper must run both
candidate-content gates against these exact completed bytes:

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5166-modernization-nonimpairment-enforcement --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5166-modernization-nonimpairment-enforcement-013.md`
   must report `preflight_passed: true`, `missing_required_specs: []`,
   `missing_advisory_specs: []`, and `blocking_errors: []`.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5166-modernization-nonimpairment-enforcement --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5166-modernization-nonimpairment-enforcement-013.md`
   must exit 0 with zero mandatory blocking gaps.

Version 011 records that both live-thread preflights passed before this
revision. The helper's candidate-byte results are authoritative for filing.

## Specification-Derived Verification Plan

| ID | Requirement | Verification | Passing evidence |
| --- | --- | --- | --- |
| SV-1 | Structured disposition is deterministic and fail-closed. | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py -q --tb=short` | 20 passed; valid payloads pass and absent, malformed, duplicate, incomplete, and placeholder cases fail with stable diagnostics. |
| SV-2 | Fixture isolation reaches the owned branch without weakening membership enforcement. | Inspect the exact diff for `platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py`, then run SV-1. | Only test-fixture construction is isolated; neither production hook's project-membership logic changes; the four formerly intercepted cases pass. |
| SV-3 | The report-only evaluator enforces frozen evidence without mutation. | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_nonimpairment.py -q --tb=short` | Complete evidence passes; missing or impaired invariants fail; no state mutation occurs. |
| SV-4 | Owned hook semantics match. | Deterministically parse both hooks and compare AST dumps for the four constants, two helpers, and conditioned denial branch with location attributes excluded. | Every named node is present once and compares equal. |
| SV-5 | Owned hook behavior matches. | Run the focused valid and denial-case matrix through each hook copy. | Both copies return equivalent accept/deny outcomes and stable non-impairment diagnostics. |
| SV-6 | Foreign applicability-preflight variance is preserved. | `git diff --no-index -- .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py` plus semantic patch inspection. | Differences are limited to the two accepted pre-existing applicability-preflight hunks; neither is selected by the WI-5166 patch manifest. |
| SV-7 | Python quality gates pass. | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check` and `-m ruff format --check` over the exact five targets. | Both commands exit 0. |
| SV-8 | Exact scope and non-completion remain auditable. | Record pre/post SHA-256, exact changed hunks, and implementation-report statements. | Only five targets are named; foreign hunks are excluded; report says WI-5166 remains open with all remaining obligations listed. |
| SV-9 | Independent verification governs completion. | Loyal Opposition independently reruns SV-1 through SV-8 from the reported bytes. | A separate-session VERIFIED names exact commands, outcomes, hashes, semantic boundaries, and remaining work. |

## Acceptance Criteria

- The implementation changes exactly the five listed targets and no others.
- The evaluator remains deterministic, report-only, and non-activating.
- The four named constants, two helper functions, and conditioned denial branch
  are AST-equivalent and behaviorally equivalent across active and template
  hooks.
- Whole-file byte identity is not required; the two excluded pre-existing
  applicability-preflight differences remain present and unattributed.
- The bounded test-only fixture isolation produces 20 passing focused tests
  without weakening production project-membership enforcement.
- Ruff check and format check pass over all five targets.
- No whole-file hook staging, replacement, formatting, or finalization occurs.
- The implementation report carries exact hashes, semantic and behavioral
  evidence, the fixture-isolation diff, foreign-hunk exclusions, and the full
  remaining-work list.
- A VERIFIED verdict closes only this first slice and must not resolve or
  represent completion of WI-5166.
- Fresh GO, exact claim, successful implementation-start packet, independent
  VERIFIED, and separate Git-finalization authority remain mandatory.

## Risk And Rollback

The primary risk is accidentally treating semantic parity as permission to
normalize or absorb unrelated hook differences. The exact AST-node allowlist,
behavior matrix, and excluded-diff check fail closed on that risk. A second
risk is implementing fixture isolation by weakening production membership
enforcement; the isolation is test-only and verification rejects any production
membership change. A third risk is later misrepresenting this bounded slice as
WI-5166 completion; the remaining-work and non-closure assertions remain hard
acceptance requirements.

Rollback removes only the named non-impairment nodes, the bounded focused-test
fixture isolation, and the three candidate files through a separately governed
exact patch. It must preserve both excluded applicability-preflight differences,
all unrelated edits, bridge history, and project state. No whole-file restore,
destructive cleanup, broad staging, commit, push, release, deployment, or
history rewrite is authorized here.

## Recommended Commit Type

`feat`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
