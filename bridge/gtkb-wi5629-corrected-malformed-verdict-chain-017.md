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

# Implementation Report - WI-5629 PAUTH Packet Integration

bridge_kind: implementation_report
Document: gtkb-wi5629-corrected-malformed-verdict-chain
Version: 017
Responds to: bridge/gtkb-wi5629-corrected-malformed-verdict-chain-016.md
Approved proposal: bridge/gtkb-wi5629-corrected-malformed-verdict-chain-015.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5629

target_paths: ["scripts/bridge_lifecycle_resolver.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_bridge_lifecycle_resolver.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Implementation Claim

The bounded operation-time project-authorization integration approved by
version 016 is implemented inside the existing four-file WI-5629 boundary.

The implementation now:

1. decodes the complete current PAUTH envelope without treating malformed JSON
   list bytes as empty authority;
2. evaluates exact proposal targets and `implementation_packet_create` before
   packet issuance;
3. binds normalized envelope, target classifications, operations, decisions,
   evaluator identity/version/hash, and taxonomy version/hash into the packet;
4. re-evaluates current PAUTH, evaluator, taxonomy, target, and requested
   operation state at implementation start and packet load;
5. rejects protected source/test/configuration start targets when no PAUTH is
   present;
6. preserves bootstrap authority, metadata-only legacy load behavior, exact
   claim authority, and schema-v3 named-before-current packet ordering.

This report does not claim terminal readiness. The PAUTH integration and its
full test matrix pass, but a fresh live foundation read proves the corrected
malformed-chain resolver cannot yet progress beyond corrected GO into a
post-implementation report and NO-GO. That remaining resolver gap is recorded
below for independent disposition and a fresh governed revision.

## Files Changed

- `scripts/bridge_lifecycle_resolver.py`
- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`
- `platform_tests/scripts/test_implementation_authorization.py`

Final SHA256:

- `scripts/bridge_lifecycle_resolver.py`:
  `0AEE86CFA377CAEDEDA7D57914891C63A2415F766FD4D93003EC8FBFC95C6854`
- `scripts/implementation_authorization.py`:
  `A13B6CDE9DEA029996E8E8B724C20BB71168C074078835894733BA55DDF07371`
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`:
  `539894A7B406C3D9E76A43B7252F593BA93A75CAAC5C38E40A04D8F786E504A4`
- `platform_tests/scripts/test_implementation_authorization.py`:
  `D7C3597096175694F2DD442894954E6C5BF301F95A805E07E6EC152D3A4F18CB`

Read-only dependencies remained byte-identical:

- evaluator:
  `5EAB50B26F0EAC3E99C1670007983D7DFFF071B758D062B215FBDDBF3379A9CA`
- taxonomy:
  `E726688AC19484CB1105EC4965C53F3F1CC4E6198E28F71D66D79838878387D8`

## Implementation Start Evidence

Fresh exact claim:

- row: `33570`
- session: `019f77f8-0931-75e2-a78d-7dea7037f743`
- acquired: `2026-07-19T14:09:04Z`
- claim kind: `go_implementation`
- target bridge: `gtkb-wi5629-corrected-malformed-verdict-chain`

Fresh schema-v3 implementation-start packet:

- finalized: `2026-07-19T14:09:50Z`
- packet hash:
  `sha256:cb3de2a78cf4daec636a8231a35bd0a1a541485154a868ed1bd6e5a4e9a495df`
- normalized PAUTH envelope hash:
  `194E95A1B99DFD0B9238A0373769FAE29E1032DC13603F4177B5EE4F9755120D`
- evaluator SHA256:
  `5EAB50B26F0EAC3E99C1670007983D7DFFF071B758D062B215FBDDBF3379A9CA`
- taxonomy SHA256:
  `E726688AC19484CB1105EC4965C53F3F1CC4E6198E28F71D66D79838878387D8`
- create decision: `allowed`
- start decision: `allowed`
- exact classifications:
  two `source` targets and two `test` targets.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

`DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` directs completion
of Dispatcher Next and all derived prerequisites under independent review.
Active PAUTH version 4 covers WI-5629 and the exact four targets. No waiver is
requested. The remaining resolver gap must return through normal review.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-011.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-014.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-015.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-016.md`
- `bridge/gtkb-wi5178-operation-time-authority-enforcement-012.md`
- `bridge/gtkb-wi5178-governed-predecessor-closure-008.md`

## Specification-Derived Verification Results

| Requirement | Executed command | Observed result |
| --- | --- | --- |
| Exact malformed-chain resolver | `python -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py -q --tb=short --timeout=120` | PASS: 36 passed |
| Complete implementation authorization | `python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short --timeout=120` | PASS: 161 passed in 1069.52s |
| Work-intent nonimpairment | `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short --timeout=120` | PASS: 34 passed |
| Canonical evaluator nonimpairment | `python -m pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py -q --tb=short --timeout=120` | PASS: 13 passed |
| Expanded operation-time cluster | Three no-PAUTH cases, active PAUTH envelope, class denial, forbidden operation, envelope drift, taxonomy drift, evaluator drift, malformed envelope | PASS: 10 passed |
| Static quality | `ruff check` on four targets | PASS |
| Formatting | `ruff format --check` on four targets | PASS |
| Syntax | `py_compile` on four targets | PASS |
| Live WI-5629 start | Fresh claim plus `implementation_authorization.py begin` | PASS: schema-v3 packet with bound create/start decisions |
| Live foundation progression | `bridge_entry(..., "gtkb-dispatcher-next-foundation-spike")` | FAIL: `MALFORMED_CORRECTION_INVALID_TAIL` after corrected GO v004 plus report v005 and NO-GO v006 |

The first authorization-wide run produced 160 passed and one fixture failure:
the schema-v3 positive CLI fixture had no root-bound taxonomy or PAUTH. The
fixture was corrected to seed canonical PAUTH/taxonomy state, passed 1/1
fresh, and the complete 161-test rerun then passed in one run. The rerun wrote
JUnit evidence at
`.gtkb-state/wi5629-implementation-authorization-rerun.junit.xml`; the command
result above is the durable report evidence, while `.gtkb-state` remains
runtime support only.

## Remaining Finding

### F1 - P0 - Corrected malformed chains cannot progress after corrected GO

Observation: the public foundation chain is:

```text
NEW v001
-> malformed decorated GO v002
-> strict NO-ACTION v003
-> strict corrected GO v004
-> implementation report NEW v005
-> verification NO-GO v006
```

The resolver currently limits a malformed correction tail to exactly one
NO-ACTION and at most one corrected LO verdict. A fresh read fails:

```text
MALFORMED_CORRECTION_INVALID_TAIL:
Malformed correction requires exactly one NO-ACTION and at most one corrected
LO verdict, with no later versions
```

Impact: a corrected GO can authorize its first implementation, but the same
thread becomes unreadable as soon as the normal report/verification lifecycle
continues. WI-5617 cannot be re-finalized, and the public resolver does not yet
meet the operation-neutral lifecycle contract required by versions 011 and
016.

Required revision: extend only the public resolver and its existing WI-5629
tests to validate the strict lifecycle after the corrected verdict. Preserve
the single exact quarantined malformed file and all missing, wrong-link,
cross-thread, wrong-role, wrong-document, gap, duplicate, non-adjacent, and
multiply malformed denials. Expose the corrected proposal/GO pair while the
post-GO report is resumable, and expose the correct report/verdict relationship
for terminal consumers.

Separate compatibility boundaries remain separate:

- WI-5636 owns exact historical `Responds to GO:` compatibility after WI-5629.
- WI-5637 owns decorated `Version:` compatibility after WI-5629 and WI-5636.

This report does not absorb either slice.

## Acceptance Status

- Operation-time PAUTH integration: PASS.
- Five originally reproduced operation-time failures: PASS.
- Three additional missing-PAUTH fail-open cases: PASS.
- Evaluator/taxonomy/envelope drift and malformed-carrier denial: PASS.
- Resolver, authorization, work-intent, evaluator, Ruff, format, compile:
  PASS.
- Live corrected-chain progression beyond corrected GO: FAIL.
- Terminal WI-5629 readiness: NOT CLAIMED.
- Dispatcher, provider, harness, Git, credential, deployment, release, and
  external-system mutation: NONE.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "before_behavior": "Packets copied only basic PAUTH metadata and live corrected chains became unreadable after normal post-GO progression.",
  "after_behavior": "Packets now bind and re-evaluate exact PAUTH, evaluator, taxonomy, targets, operations, and decisions; post-corrected-GO lifecycle progression remains for the next governed resolver revision.",
  "history_preservation": "All numbered bridge files and foreign source bytes remain unchanged; no history is rewritten.",
  "nonimpairment": "No dispatcher configuration/runtime, provider, harness, Git/index/ref, credential, deployment, release, or external-system mutation occurred.",
  "rollback": "Under fresh GO, claim, and start authority, reverse only WI-5629 hunks in the four declared targets and rerun the reported matrix.",
  "fail_closed_conditions": [
    "Any PAUTH, evaluator, taxonomy, target, operation, or packet evidence is missing, malformed, denied, or drifted.",
    "Any corrected history is ambiguous, unlinked, wrong-role, wrong-document, non-adjacent, duplicated, or multiply malformed.",
    "Any future change requires a target outside the four-file WI-5629 boundary."
  ]
}
```

## Risks And Rollback

Risk is limited to shared authorization-reader behavior. The passing full
authorization, work-intent, and evaluator matrices bound that risk. The
remaining lifecycle issue fails closed before protected effect.

Before terminal verification, rollback requires a fresh governed claim/start
and restores only the WI-5629 hunks in its four declared targets. Preserve the
read-only evaluator, taxonomy, all numbered bridge history, WI-5636, WI-5637,
and foreign worktree bytes.

Recommended commit type: `fix`
