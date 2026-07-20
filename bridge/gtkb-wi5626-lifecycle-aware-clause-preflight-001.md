NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f77f8-0931-75e2-a78d-7dea7037f743
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Resolve the lifecycle artifact in clause preflight

bridge_kind: prime_proposal
Document: gtkb-wi5626-lifecycle-aware-clause-preflight
Version: 001
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5626

target_paths: ["scripts/adr_dcl_clause_preflight.py", "platform_tests/scripts/test_adr_dcl_clause_preflight.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

Make `adr_dcl_clause_preflight.py --bridge-id <slug>` resolve the bridge
artifact whose clauses are being evaluated, rather than blindly selecting the
highest numbered file. When the latest canonical version is a Prime-authored
`NEW`, `REVISED`, or `NO-ACTION` entry, that file is operative. When the latest
version is an LO-authored `GO`, `NO-GO`, or `VERIFIED` verdict, the operative
content is the newest preceding `NEW` or `REVISED` artifact. If the lifecycle
cannot be resolved, the mandatory preflight continues to fail closed.

This corrects the reproduced Dispatcher Next implementation-start failure:
the approved foundation proposal passes clause preflight when supplied through
`--content-file`, but the same thread fails through `--bridge-id` because the
current implementation evaluates the short GO verdict instead of the proposal
that GO authorizes.

## Requirement Sufficiency

Existing requirements sufficient.

`GOV-FILE-BRIDGE-AUTHORITY-001`,
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` already require lifecycle
authority to be derived from the canonical numbered bridge chain and require
the relevant proposal/report evidence to be mechanically evaluated. The
owner-authorized Dispatcher Next program records the defect as `WI-5626` /
`TEST-11671`; no new formal requirement is needed for this bounded resolver
repair.

## In-Root Placement Evidence

Both targets are inside `E:\GT-KB`: `scripts/adr_dcl_clause_preflight.py` and
`platform_tests/scripts/test_adr_dcl_clause_preflight.py`.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION; WI-5626; bridge/gtkb-dispatcher-next-foundation-spike-001.md through -003.md",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "Canonical numbered bridge chain, lifecycle-aware operative artifact resolution, mandatory clause evaluation, implementation-start authorization, implementation report, and independent Loyal Opposition verification.",
  "before_behavior": "The clause preflight always selects the numerically latest bridge file, so an LO verdict is evaluated as if it were the approved implementation proposal and can create false blocking gaps.",
  "after_behavior": "The preflight selects current Prime content directly or the newest preceding NEW/REVISED artifact behind a terminal LO verdict, and fails closed when no evaluable lifecycle artifact exists.",
  "self_descriptive_naming": "Resolver helpers and tests name operative lifecycle artifact selection rather than generic latest-file selection.",
  "obsolete_guidance_disposition": "The docstring and report label are updated so top-of-stack is no longer described as synonymous with operative content.",
  "history_preservation": "No numbered bridge artifact, work-item version, project authorization, or preflight report is rewritten.",
  "baseline": {
    "foundation_thread": "NEW proposal passes explicit content-file preflight; subsequent GO/NO-ACTION chain causes bridge-id mode to inspect the wrong file",
    "implementation_targets": "two clean files"
  },
  "expected_result": {
    "proposal_go_chain": "bridge-id mode evaluates the proposal",
    "implementation_report_verified_chain": "bridge-id mode evaluates the newest preceding NEW report",
    "runtime_effect": "no dispatcher restart, configuration, route, cap, lease, TAFE, credential, deployment, release, or Git mutation"
  },
  "rollback": {
    "instructions": "Before VERIFIED, revert only the two scoped files and file a revised implementation report. After VERIFIED, use a governed follow-on correction.",
    "verification": "Rerun the focused clause-preflight tests and the live foundation bridge-id/content-file equivalence check."
  },
  "hard_invariants": [
    "Explicit --content-file remains authoritative and unchanged.",
    "Exact canonical numbered thread files are the only implicit candidates.",
    "Unresolvable or malformed lifecycle chains fail closed.",
    "No implementation occurs without independent GO, exact claim, and implementation-start authorization."
  ],
  "fail_closed_conditions": [
    "No canonical versioned files exist.",
    "The latest verdict has no preceding NEW or REVISED artifact.",
    "A candidate file is unreadable or has no canonical status.",
    "Clause evidence remains absent from the resolved artifact."
  ],
  "essential_context_preservation": "Preserve WI-5626, TEST-11671, the owner program deliberation, the malformed-status evidence tracked by WI-5625, and the exact six-target boundary of the foundation spike."
}
```

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - lifecycle authority comes from one exact canonical numbered thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation-start checks must evaluate the approved proposal's specification evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification checks must evaluate the implementation report carrying spec-derived evidence.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - a NO-ACTION correction remains directly evaluable while pending LO disposition.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal cites exact PAUTH, project, work item, and targets.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the repair must not restart or reconfigure the live dispatcher.
- `GOV-WORK-TREE-HYGIENE-001` - preserve unrelated dirty files and modify only the two clean targets.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex self-enforces GO, claim, and implementation-start gates.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the reproduced defect, work item, test, repair, and verification remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this derived defect follows an explicit proposal through VERIFIED terminal state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect is preserved in MemBase rather than transient session context.
- `GOV-STANDING-BACKLOG-001` - any further authority-selection discrepancy becomes governed derived work.

## Owner Decisions / Input

`DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` directs the Master
Prime Builder to implement the isolated program and drive constituent,
derived, and upstream-dependent work to VERIFIED or another governed terminal
state while preserving independent review and implementation-start gates. No
additional owner input is required for this repair.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - owner-approved isolated Dispatcher Next program and terminal-closure mandate.

## Proposed Scope

1. Replace `find_operative_file`'s latest-number selection with an exact
   canonical-thread resolver that reads each version's first status line.
2. Return the latest file directly for `NEW`, `REVISED`, and `NO-ACTION`.
3. For latest `GO`, `NO-GO`, or `VERIFIED`, return the newest preceding
   `NEW` or `REVISED` file.
4. Return no operative file for an unresolvable lifecycle, preserving the
   existing exit-5 fail-closed behavior.
5. Preserve explicit `--content-file` behavior without alteration.
6. Add focused regression tests for proposal/GO, report/VERIFIED,
   NO-ACTION, malformed/unresolvable, exact-thread, and explicit-content modes.

## Specification-Derived Verification

| Requirement | Test or command | Acceptance predicate |
| --- | --- | --- |
| Proposal authorization | New fixture `NEW proposal -> GO verdict` | `--bridge-id` evaluates the NEW proposal and returns the same result as `--content-file <proposal>`. |
| Corrected verdict chain | New fixture `NEW -> malformed historical verdict -> NO-ACTION -> GO` | Resolver skips malformed content, evaluates the original NEW proposal, and does not evaluate the correction or GO body as implementation evidence. |
| Verification lifecycle | New fixture `NEW proposal -> GO -> NEW implementation report -> VERIFIED` | Resolver evaluates the newest NEW implementation report. |
| Direct Prime action | New fixtures with latest `REVISED` and latest `NO-ACTION` | Latest Prime artifact is evaluated directly. |
| Fail closed | Latest verdict without preceding `NEW`/`REVISED`, unreadable/malformed chain, and missing thread | Exit `5`; report says no operative lifecycle artifact was found. |
| Exact thread | Prefix-sibling fixture | A sibling slug cannot influence selection. |
| Explicit override | Existing content-file tests | `--content-file` behavior remains unchanged and authoritative. |
| Focused regression | `python -m pytest platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short` | Exit 0. |
| Static quality | `python -m ruff check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py` | Exit 0. |
| Formatting | `python -m ruff format --check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py` | Exit 0. |
| Live defect proof | Run clause preflight on the Dispatcher Next foundation thread by `--bridge-id` and by explicit proposal `--content-file` | Both select/evaluate `bridge/gtkb-dispatcher-next-foundation-spike-001.md` and return the same gate result. |
| Live nonimpairment | `gt bridge dispatch health --json` before and after | Daemon remains running; no restart, config, cap, route, lease, or TAFE mutation. |

## Acceptance Criteria

- `--bridge-id` evaluates the lifecycle-bearing Prime artifact, not a later LO
  verdict body.
- `NEW`/`REVISED`/`NO-ACTION` latest content remains directly evaluable.
- `GO`/`NO-GO`/`VERIFIED` latest content resolves to the newest preceding
  `NEW` or `REVISED`.
- Explicit `--content-file` remains unchanged.
- Missing, malformed, or unresolvable chains fail closed.
- Prefix siblings cannot affect resolution.
- Only the two declared target files change.
- The live dispatcher is not restarted, reconfigured, or cut over.

## Risks and Rollback

- Risk: a thread can contain multiple `NEW` phases. Mitigation: select the
  newest preceding `NEW`/`REVISED`, which correctly distinguishes an
  implementation report from its earlier proposal.
- Risk: historical malformed verdict files may be encountered. Mitigation:
  only canonical status-bearing versions participate; malformed versions are
  ignored and an otherwise unresolvable chain fails closed.
- Risk: changing implicit resolution affects both proposal and verification
  preflights. Mitigation: cover both lifecycle shapes plus all existing focused
  tests; explicit content-file mode remains an escape hatch with exact caller
  authority.
- Rollback: revert the two scoped files. The current explicit `--content-file`
  invocation remains available while a revised repair is reviewed.
