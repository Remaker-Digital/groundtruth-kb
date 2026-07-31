REVISED
::init gtkb lo
::open build

# WI-5294: Emit the complete non-impairment schema in proposal generators

bridge_kind: prime_proposal
Document: gtkb-wi5294-proposal-generator-nonimpairment-schema
Version: 003
Date: 2026-07-18 UTC
Responds to NO-GO: bridge/gtkb-wi5294-proposal-generator-nonimpairment-schema-002.md
Revises: bridge/gtkb-wi5294-proposal-generator-nonimpairment-schema-001.md

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined Prime Builder role; build activity envelope; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5294
Related Work Items: WI-5420, WI-5458, WI-5488

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py", "groundtruth-kb/tests/test_cli_bridge_propose.py"]

implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

## Revision Claim

The sole NO-GO finding is now mechanically resolved. WI-5420 is terminal
VERIFIED at `bridge/gtkb-wi5420-canonical-parity-disposition-cli-008.md`,
focused commit `bb539c8148ed8c4477c65c5fd0f7aa2841d6adc0` is an ancestor of
current HEAD `64897bd7692aa28e899fdd038a27c628be65683b`, and the three shared
WI-5294 targets plus its fourth test target are clean. This
revision rebases the original non-impairment schema proposal onto that
committed baseline and explicitly composes its new section after WI-5420's
conditional `## Cross-Harness Disposition` block and before
`## Specification-Derived Verification Plan`.

No source, test, dispatcher, TAFE, harness, runtime, Git, deployment, release,
or credential mutation was performed for this revision.

## Requirement Sufficiency

Existing requirements remain sufficient.
`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` defines the required structured
disposition and the canonical bridge compliance gate enforces it. WI-5420
changed only the committed baseline and insertion context; it did not resolve
the missing non-impairment schema. No new policy, role, queue, or artifact
authority is required.

## Findings Addressed

### F1 (P0, blocking) - Peer Implementation Report Conflict

Resolved:

1. WI-5420 is latest `VERIFIED` at v008.
2. Focused commit `bb539c8148ed8c4477c65c5fd0f7aa2841d6adc0` remains an
   ancestor of current HEAD `64897bd7692aa28e899fdd038a27c628be65683b` and
   contains the complete WI-5420 bridge chain and three shared targets.
3. All four WI-5294 targets are clean at the following current-HEAD SHA-256
   preimages:
   - `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py`:
     `e634d1d2036eb77c5d25f02f45300d9b2cb854de74793d1c1b339ef1755adca9`
   - `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`:
     `a264066ceb32e20a8086b82992c2363aea8a5e364028a62e339e77d75383890c`
   - `platform_tests/groundtruth_kb/test_cli_bridge_propose.py`:
     `a8982154061c7beb8562de8befdd42df5bedc849057730b1d24b1704d0d5c179`
   - `groundtruth-kb/tests/test_cli_bridge_propose.py`:
     `87f824ec30f259de58fbbb2b21f3081779bfd83c3fb3976f431b2ec1d6840a0b`
4. Both focused test modules pass `35/35` on the committed baseline. Ruff
   check passes and Ruff format reports all four files already formatted.
5. The revised implementation plan preserves WI-5420's conditional
   cross-harness section and inserts the non-impairment section at the
   separately tested canonical location.

## In-Root Placement Evidence

All four targets are GT-KB platform source/test files inside `E:/GT-KB`.
No application, external, credential, dispatcher, TAFE, harness-state, or
bridge-history target is in scope.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - defines the structured
  disposition and fail-closed field contract.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - generated proposals
  must be mechanically evaluable before filing.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the governed writer remains the only live
  publication route.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, WI,
  related work, and exact targets remain explicit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - all relevant
  governing specifications are linked.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent VERIFIED
  requires executed tests derived from these requirements.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - active project PAUTH does
  not replace GO, claim, start, report, or verification gates.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - operation-time authority must
  match the exact four-file proposal.
- `ADR-CROSS-HARNESS-PARITY-001` - shared CLI behavior must remain equivalent
  for supported interactive harness users.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - this proposal carries an
  explicit cross-harness disposition and preserves WI-5420's generated
  section.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changes remain in-root.
- `GOV-WORK-TREE-HYGIENE-001` - fresh clean preimages and exact-path
  finalization must preserve unrelated work.
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202666274` - owner-authorized Authority Foundations project scope
  while preserving independent bridge and implementation gates.
- `DELIB-S334-BOUNDED-KNOWLEDGE-COMPLEXITY-OWNER-DECISION` - authoring
  surfaces should expose bounded required context instead of revealing hidden
  schema only through failed writes.
- `DELIB-2708` - proposal scaffold and live helper behavior must remain
  aligned.
- `bridge/gtkb-wi5294-proposal-generator-nonimpairment-schema-002.md` - the
  sole peer-conflict NO-GO this revision resolves.
- `bridge/gtkb-wi5420-canonical-parity-disposition-cli-008.md` - terminal
  committed shared-target predecessor and current baseline.

## Owner Decisions / Input

No new owner decision is required. `DELIB-202666274` is the owner basis for
active project-scoped
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE`.
That authorization permits source and test work but preserves independent GO,
exact claim, schema-v3 implementation start, implementation report,
independent VERIFIED, and focused finalization.

The dispatcher-configuration troubleshooter hold remains binding. WI-5294
does not target dispatcher or TAFE configuration, runtime state, routing,
eligibility, workers, leases, or daemons.

## Scope Changes

The four target paths and functional outcome are unchanged from v001. The
revision changes only:

- the clean baseline hashes after terminal WI-5420;
- explicit sequencing after WI-5420 and before dependents WI-5458/WI-5488;
- the section-order requirement needed to compose with WI-5420's conditional
  cross-harness disposition; and
- current test and lint baseline evidence.

## Proposed Scope

1. Add one canonical non-impairment disposition builder or schema
   representation shared by the two proposal-generation paths without
   weakening the compliance gate.
2. Make `gt bridge file-implementation-proposal` emit exactly one fenced JSON
   object containing `schema_version: 1`, `applicability`, and every canonical
   required field with concrete request-derived values.
3. Make `gt bridge propose --kind implementation` seed the same complete
   field set with explicit author-fill placeholders in its non-dispatchable
   draft.
4. In `proposal_filing._build_content`, preserve WI-5420's optional
   `cross_harness_section` and emit the non-impairment section after it and
   before `## Specification-Derived Verification Plan`.
5. Add tests comparing both generated surfaces to the canonical field
   contract, checking exact section order with and without cross-harness
   dispositions, proving complete live content passes audit, and proving
   incomplete/placeholder content remains blocked.
6. Preserve project linkage, specification loading, requirement sufficiency,
   prior deliberations, owner decisions, credential scan, author metadata,
   applicability, clause, collision, and no-index publication behavior.

Out of scope:

- Modification of `.claude/hooks/bridge-compliance-gate.py` or relaxation of
  any compliance rule.
- Dispatcher or TAFE configuration/runtime, harness settings, routing,
  eligibility, workers, leases, providers, or live process control.
- Bridge history rewrite, MemBase mutation during implementation, caches,
  alternate queues/indexes, staging, push, deployment, release, credentials,
  destructive cleanup, or unrelated files.

## Cross-Harness Disposition

- Harness A (Codex), B (Claude Code), C (Antigravity), and E (Cursor):
  applicable as supported interactive consumers of the shared governed
  `gt bridge` CLI. They receive the same generated schema and section order;
  no harness-specific source projection is introduced.
- Harness D (Ollama), F (OpenRouter), and H (Alibaba): not implementation
  targets. Provider workers consume governed dispatch packets and do not own
  these interactive proposal-generator files.

No parity waiver is requested. WI-5420's generated cross-harness section is
preserved as an input to the new deterministic section-order tests.

## Specification-Derived Verification Plan

| Requirement | Executable verification | Required result |
|---|---|---|
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Compare live and draft output with the canonical required-field set; run compliance audit on complete and incomplete variants. | Complete live content passes; missing, malformed, empty, duplicate, or placeholder fields fail closed. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Parse generated JSON and execute candidate preflights without manual field discovery. | Deterministic parse and preflight results. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Generate with and without WI-5420 cross-harness dispositions and assert section order. | Cross-harness section, when present, precedes non-impairment; verification plan follows non-impairment. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run existing proposal CLI/write-order tests. | Governed writer and file-first/no-index publication semantics remain unchanged. |
| Project/spec linkage authorities | Assert PAUTH, Project, Work Item, target paths, requirements, specs, deliberations, and owner sections. | Every governed section remains present and concrete. |
| Lifecycle authorities | Exercise dry-run, non-dispatchable draft, and live publication fixtures. | Dry-run writes nothing; draft writes runtime state only; live writes only after all gates pass. |
| `GOV-WORK-TREE-HYGIENE-001` | Recheck exact target hashes/status, `git diff --check`, and focused finalizer scope. | Only approved WI-5294 hunks and bridge chain enter finalization. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run both focused modules, Ruff check/format, py_compile, both bridge preflights, and independent LO rerun. | Every mapped command passes before VERIFIED. |

Required commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_cli_bridge_propose.py groundtruth-kb/tests/test_cli_bridge_propose.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py groundtruth-kb/tests/test_cli_bridge_propose.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py groundtruth-kb/tests/test_cli_bridge_propose.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py groundtruth-kb/tests/test_cli_bridge_propose.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5294-proposal-generator-nonimpairment-schema
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5294-proposal-generator-nonimpairment-schema
```

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5294; DELIB-202666274; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE; terminal WI-5420 v008",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 plus the canonical bridge compliance schema and governed proposal generators",
  "primary_route": "gt bridge file-implementation-proposal for dispatchable proposals and gt bridge propose for non-dispatchable drafts",
  "before_behavior": "the committed generators support WI-5420 cross-harness dispositions but omit the structured non-impairment disposition, so applicable live filings fail only after otherwise successful preflights and drafts conceal the complete field contract",
  "after_behavior": "live generation emits one concrete schema-valid disposition and draft generation exposes every required field with explicit placeholders while preserving WI-5420 section ordering and every existing gate",
  "self_descriptive_naming": "builder helpers and tests use nonimpairment_disposition terminology and exact canonical field names",
  "obsolete_guidance_disposition": "incomplete free-form scaffold guidance is replaced in the two canonical generator paths; no alternate proposal writer or schema authority is created",
  "history_preservation": "existing bridge files remain append-only and the WI-5294 numbered chain preserves proposal, NO-GO, revision, report, and verdict states",
  "baseline": {
    "head": "64897bd7692aa28e899fdd038a27c628be65683b",
    "target_state": "all four targets clean at declared SHA-256 preimages",
    "focused_tests": "35 passed with one pre-existing pytest configuration warning",
    "quality": "Ruff check passed and four files already formatted",
    "existing_capability": "conditional cross-harness disposition generation from terminal WI-5420"
  },
  "expected_result": {
    "dispatchable": "complete generated cross-cutting proposal passes the in-memory compliance audit and files exactly once",
    "draft": "draft contains schema_version plus every mandatory field and remains visibly incomplete until author judgment replaces placeholders",
    "ordering": "cross-harness section when present, then non-impairment disposition, then specification-derived verification plan",
    "gate": "missing, malformed, duplicate, empty, or placeholder disposition values continue to fail closed",
    "runtime_mutation": "zero dispatcher, TAFE, harness, routing, worker, lease, daemon, provider, or cache mutation"
  },
  "rollback": {
    "instructions": "under separate authority, revert only the focused WI-5294 source and test hunks",
    "verification": "rerun both focused modules, Ruff, py_compile, exact-target diff check, and both bridge preflights"
  },
  "hard_invariants": [
    "no bridge compliance rule is relaxed",
    "no proposal files before credential, author, applicability, clause, collision, project-linkage, and compliance checks pass",
    "WI-5420 cross-harness disposition behavior and section order remain supported",
    "draft placeholders never become filing-valid values",
    "no dispatcher/TAFE configuration/runtime, harness state, provider, credential, deployment, release, push, or unrelated worktree state is mutated"
  ],
  "fail_closed_conditions": [
    "canonical required-field set cannot be loaded or represented",
    "generated live values are empty, placeholders, malformed JSON, duplicate, or schema-version incompatible",
    "cross-harness and non-impairment section order is ambiguous or incorrect",
    "candidate or live applicability, clause, collision, project-linkage, or compliance checks fail",
    "exact target preimages drift before claim/start",
    "independent GO, matching claim, schema-v3 start, tests, VERIFIED, or focused finalization is absent"
  ],
  "essential_context_preservation": "generated proposals retain project authorization, work-item and related-work linkage, target paths, requirement sufficiency, specification links, prior deliberations, owner decisions, cross-harness disposition, verification mapping, acceptance criteria, risks, rollback, and file scope"
}
```

## Acceptance Criteria

1. The live proposal generator emits one complete schema-valid
   non-impairment disposition for applicable work.
2. The non-dispatchable draft generator exposes every canonical field with
   explicit author-fill placeholders.
3. Missing, malformed, empty, duplicate, and placeholder live values remain
   blocked by the same compliance authority.
4. With WI-5420 dispositions, section order is cross-harness,
   non-impairment, then verification plan; without them, non-impairment
   directly precedes verification.
5. Project, PAUTH, WI, target, spec, requirement, deliberation, owner,
   credential, applicability, clause, collision, and publication behavior
   remains green.
6. Both focused modules, Ruff, format, py_compile, diff check, applicability,
   clause, independent VERIFIED, and focused finalization pass.
7. No dispatcher/TAFE configuration/runtime, harness state, bridge-history
   rewrite, MemBase implementation mutation, staging, push, deployment,
   release, credential, or unrelated file change occurs.

## Pre-Filing Preflight

Candidate-content preflights executed before live filing:

- `scripts/bridge_applicability_preflight.py --content-file`: PASS,
  `preflight_passed: true`, `missing_required_specs: []`,
  `missing_advisory_specs: []`, `blocking_errors: []`, packet
  `sha256:ffccbf346693e7a96b2239d43057afec6574f4a401f197101c1b593e06a51fbf`.
- `scripts/adr_dcl_clause_preflight.py --content-file`: PASS, five clauses
  evaluated, four `must_apply`, zero mandatory evidence gaps, and zero
  blocking gaps.
- Live filing remains subject to helper-mediated credential,
  author-provenance, project-linkage, related-work collision,
  cross-harness-disposition, non-impairment, and publication-admission gates.

## Risk And Rollback

The primary risk is schema drift between the compliance gate and generators;
tests compare exact fields and execute the same audit path. The second risk is
misordering the new block around WI-5420's optional cross-harness section;
both present and absent cases are asserted.

Rollback requires separate authority and reverts only the focused WI-5294
source/test hunks. The numbered bridge chain and verdict history remain
append-only. No dispatcher, TAFE, runtime, carrier, or Git history rollback is
part of this work.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py`
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`
- `platform_tests/groundtruth_kb/test_cli_bridge_propose.py`
- `groundtruth-kb/tests/test_cli_bridge_propose.py`

## Recommended Commit Type

`fix(bridge)`: expose complete non-impairment schema in governed proposal
generators.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
