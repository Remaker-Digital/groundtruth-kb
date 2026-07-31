NEW

# gtkb-wi5405-portability-fixture-read-guard (Slice 1) - Permit only isolated portability fixture roots

bridge_kind: prime_proposal
Document: gtkb-wi5405-portability-fixture-read-guard
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-desktop-019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: interactive desktop Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5405

target_paths: ["platform_tests/scripts/test_modernization_agent_red_portability.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair the source-host read classifier in both standalone subprocess programs
embedded by the frozen Agent Red portability acceptance test. When pytest uses
its canonical in-root basetemp, the relocated host and the isolated wheel
environment are legitimate independent fixture roots but are also lexical
children of `GTKB_SOURCE_ROOT`. The current audit hook therefore denies the
fixture before Agent Red can run.

In both `_RUNTIME_PROBE` and `_MIGRATION_DRIVER`, normalize a closed allow set
containing only `GTKB_RELOCATED_HOST` and the active interpreter's
`sys.prefix`. Classify a path as denied source-host access only when it is under
`GTKB_SOURCE_ROOT` and outside both exact allow roots. Pass
`GTKB_RELOCATED_HOST` to the migration driver as well as the runtime probe.
Before installing each audit hook, assert that the two allow roots are not
denied and that the GT-KB root plus `groundtruth-kb/src` remain denied.

The forced in-root lifecycle node currently fails in 16.52 seconds on a denied
read of the relocated Agent Red directory. This one-file repair must preserve
the prior WI-5392 portability fixture and WI-5381 self-containment behavior,
all install/upgrade/rollback evidence, and the prohibition on any source
checkout import or read.

## Specification Links

- `ADR-APPLICATION-ISOLATION-CONTRACT-001` - defines Agent Red as a portable,
  application-scoped execution context with lifecycle authority independent of
  the GT-KB platform checkout.
- `DCL-APP-ROOT-MINIMIZATION-001` - requires the relocated application root to
  contain only justified application runtime surfaces.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` - requires Agent Red to consume GT-KB
  through supported platform boundaries.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001`,
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, and
  `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` - require every fixture byte
  to remain in-root while preserving the platform/application partition.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO before the
  protected test changes and independent VERIFIED before completion.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires the
  classifier repair and verification plan to trace to all governing isolation
  contracts.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires explicit
  PAUTH, project, work-item, target-path, and slice linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent
  execution of the exact frozen portability lane and forced-in-root node.
- `GOV-STANDING-BACKLOG-001` - governs WI-5405 as durable hygiene work.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - prohibits weakening the
  source-read guard, lifecycle assertions, or application isolation.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires reproducible,
  current evidence for the generated probes and their exact allow set.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - require traceable proposal,
  implementation, verification, and completion artifacts.

## Prior Deliberations

- `DELIB-20265219` ratified the Agent Red Readiness Program after the isolation
  census.
- `DELIB-20265220` approved Phase 1 scoping.
- `DELIB-20265227` selected the application-isolation ADR plus app-root
  minimization DCL foundation. This proposal preserves that execution-context
  boundary while correcting a test classifier that conflates host ancestry
  with source dependency.

## Owner Decisions / Input

No new owner decision is required. The owner authorized the modernization
program and directed every discovered flaw to a hygiene work item while work
continues. Active authority is
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`.
Implementation remains gated on independent GO plus matching work-intent and
implementation-start authority.

## Requirement Sufficiency

Existing requirements sufficient. The application-isolation contracts require
both an independent relocated lifecycle and denial of source-checkout
dependencies. Exact allow roots for the isolated fixture and interpreter
satisfy both without changing policy.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5405 forced in-root Agent Red lifecycle reproduction",
  "canonical_authority": "ADR-APPLICATION-ISOLATION-CONTRACT-001 plus the GT-KB root-containment family",
  "primary_route": "the frozen Agent Red clean-install, upgrade, rollback, and relocated-runtime acceptance",
  "before_behavior": "the read guard denies every lexical child of E:/GT-KB, including the exact relocated host and isolated installed-wheel environment created by the test",
  "after_behavior": "the guard permits only GTKB_RELOCATED_HOST and sys.prefix while denying every other path under GTKB_SOURCE_ROOT",
  "self_descriptive_naming": "allowed_fixture_roots and under_source distinguish the closed fixture allow set from denied checkout paths",
  "obsolete_guidance_disposition": "no guidance changes; generated probe semantics are corrected in place",
  "history_preservation": "WI-5405 records the exact denied relocated path and forced-in-root failure before implementation",
  "baseline": "the lifecycle node fails before Agent Red import on a source-host dependency denied error for the relocated application root",
  "expected_result": "all 72 frozen Agent Red portability tests pass and the isolated lifecycle node also passes with an explicit in-root basetemp",
  "rollback": "restore the prior embedded probe strings and migration environment entry in one governed test-only transaction",
  "hard_invariants": [
    "GTKB_SOURCE_ROOT and its groundtruth-kb/src subtree remain denied",
    "only the exact relocated host and active sys.prefix subtrees are allowed inside the source-root ancestry",
    "the package origin remains inside the isolated interpreter environment",
    "the Agent Red origin remains inside the relocated application root",
    "clean install, candidate upgrade, adopter migration, rollback, and post-rollback runtime all execute",
    "database bytes and rows survive migration and rollback",
    "the original Agent Red application marker remains unchanged",
    "the relocated repository ends clean",
    "no production source, dispatcher, TAFE, harness, or database state changes"
  ],
  "fail_closed_conditions": [
    "the allow set includes E:/GT-KB, .pytest-tmp generally, or any prefix broader than the two exact roots",
    "runtime and migration classifiers diverge",
    "source-root or checkout-source negative assertions do not hold",
    "any existing lifecycle or isolation assertion is removed or weakened",
    "the exact frozen lane or forced-in-root node fails",
    "platform_tests/scripts/test_rehearse_isolation.py dirt is absorbed"
  ],
  "essential_context_preservation": "prior wheel fixture, candidate build, no-index installation, source audit hook, app-root validators, migration receipts, commit evidence, rollback equality, and external-path scans remain intact"
}
```

## Spec-Derived Verification Plan

1. Frozen portability acceptance:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_agent_red_portability.py platform_tests/scripts/test_rehearse_isolation.py -q --tb=short
```

Expected: `72 passed`.

2. Explicit in-root lifecycle proof:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_agent_red_portability.py::test_agent_red_survives_relocation_and_has_an_independent_lifecycle -q --tb=short --basetemp=E:/GT-KB/.pytest-tmp/wi5405-verification
```

Expected: `1 passed`. Evidence must show package origin under `sys.prefix`,
Agent Red origin under `GTKB_RELOCATED_HOST`, and both source-negative
classifier assertions preserved in each embedded probe.

3. Static and exact scope:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_modernization_agent_red_portability.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_modernization_agent_red_portability.py
git diff --check -- platform_tests/scripts/test_modernization_agent_red_portability.py
git diff -- platform_tests/scripts/test_modernization_agent_red_portability.py
```

Expected: all checks pass. The diff is limited to symmetric embedded
classifier changes, explicit assertions, and the migration environment's
`GTKB_RELOCATED_HOST`; no whole-file adoption or neighboring test dirt.

4. Bridge and artifact lifecycle:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5405-portability-fixture-read-guard --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5405-portability-fixture-read-guard
```

Expected: no missing required/advisory specifications and zero blocking clause
gaps, followed by independent Loyal Opposition verification.

## Risk / Rollback

The main risk is accidentally creating a broad exemption that hides real source
reads. The implementation must normalize and compare exact roots, assert the
negative source cases inside both subprocesses, and pass both the isolated node
and full portability lane. Rollback restores only the embedded test programs
and their one environment field.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5405-portability-fixture-read-guard`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test` - the repair is confined to generated acceptance probes in one test file.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
