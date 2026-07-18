REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; governed proposal revision

bridge_kind: prime_proposal
Document: gtkb-wi5445-active-template-hook-failclosed-parity
Version: 003
Responds to: bridge/gtkb-wi5445-active-template-hook-failclosed-parity-002.md
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5445
target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_bridge_compliance_gate_disposition.py", "platform_tests/hooks/test_bridge_compliance_gate_envelope_head.py"]
implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# Revised Implementation Proposal - Bidirectional Bridge Hook Convergence

## First-Line Role Eligibility Check

PASS. Session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a` is transcript-defined
Prime Builder and holds the exact draft claim for this latest `NO-GO` thread.
`REVISED` is role-correct and grants no implementation authority.

## Revision Claim

Version 002 independently confirmed the fail-closed applicability gap but
rejected version 001 because its one-way template-to-active overwrite would
delete the independently VERIFIED artifact-head envelope gate from the active
hook. It also found that the proposal named only one of thirteen failing tests.

This revision accepts every finding and proposes bidirectional convergence:

1. Port the template's stricter applicability-preflight result handling into
   the active hook.
2. Port the active hook's VERIFIED artifact-head envelope validation into the
   packaged template.
3. Normalize both completed hook files to identical LF bytes only after their
   semantic union is present.
4. Update the disposition-gate synthetic proposal fixture for the current
   artifact-head and live-membership contracts.
5. Exercise envelope behavior against both active and template hooks.

No gate is removed or weakened.

## Current Baseline

All four declared targets are clean relative to current HEAD.
`gtkb-wi5307-shared-enforcement-baseline-disposition`, the sibling overlap
named by version 002, is terminal `VERIFIED` at version 018.

| Target | Current SHA-256 |
| --- | --- |
| `.claude/hooks/bridge-compliance-gate.py` | `f7fa1157af12ab578a5b4dd374a18c679ba48b0d235cb9957a8da65681b87fa2` |
| `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` | `85955f6fbcc88d6078107a63a23dbcb807a6547856f648246bf82e9cb008e16f` |
| `platform_tests/scripts/test_bridge_compliance_gate_disposition.py` | `4447c4dfef41266337bac10dadd1bd89392cc86546ce9926f20c4d6c929f9e10` |
| `platform_tests/hooks/test_bridge_compliance_gate_envelope_head.py` | `1a3c2a461103324dfeb8e772972c091f72d9351e20961538a6412685e700fa97` |

An EOL-insensitive comparison shows two legitimate committed deltas:

- active-only artifact-head imports, validator helper, and denial call;
- template-only `preflight_passed is False` / `blocking_errors` handling and
  structured preflight diagnostic.

The current disposition module reports `13 failed, 26 passed`; twelve
behavioral cases stop on stale synthetic metadata/envelope state and one is raw
byte inequality. The current active envelope module reports `5 passed`.

## Requirement Sufficiency

Existing requirements sufficient. Version 002 gives the exact correction
design and newly applicable envelope specifications. The active project PAUTH
permits source and test mutation without a per-work-item restriction while
preserving independent GO, exact claim, implementation-start, testing,
verification, and focused finalization gates.

## Proposed Change

### Active and template hooks

- Preserve every existing gate.
- Apply the template's fail-closed applicability result handling to the active
  hook:
  - `preflight_passed is False` blocks;
  - nonempty `missing_required_specs` blocks;
  - nonempty `blocking_errors` blocks;
  - the diagnostic preserves both collections in stable JSON.
- Apply the active hook's artifact-head behavior to the template:
  - import `BridgeEnvelopeError` and `validate_bridge_envelope_head` with the
    current fail-soft fallback;
  - preserve `_bridge_envelope_head_deny_reason`;
  - invoke it at the same point in `_deny_reason_for_content`.
- After both semantic deltas are present, format both files and write identical
  LF bytes. The completed raw SHA-256 values must match.

### Disposition test

- Give synthetic `NEW` implementation proposals the exact head:
  `NEW`, `::init gtkb lo`, `::open build`.
- Isolate `_wi_project_membership_gap` only inside the local `_deny` helper,
  restoring the original callable in `finally`, so live MemBase state cannot
  preempt tests whose subject is the disposition gate.
- Add a focused restoration regression if the module does not already prove
  restoration after an exception.
- Preserve all existing predicate and exclusion coverage.

### Envelope test

- Parameterize loading across the active hook and packaged template.
- Run all five existing envelope cases against both copies.
- Preserve the rule that a valid envelope may reach a later unrelated check;
  only an artifact-head denial is forbidden in that case.

## Cross-Harness Disposition

- **Claude Code / active workspace hook:** `.claude/hooks/bridge-compliance-gate.py`
  retains the VERIFIED artifact-head gate, gains the stricter fail-closed
  applicability semantics, and becomes byte-identical to the packaged source.
- **Codex / governed writer audit:** the writer continues auditing through the
  same bridge-compliance implementation and therefore observes the identical
  artifact-head, applicability, disposition, and project-linkage semantics;
  no Codex-specific bypass or weaker path is introduced.
- **Packaged adopters and generated harness surfaces:** the template carries
  the same semantic union and raw bytes as the active hook, so new activations
  cannot omit either verified gate.
- **Antigravity, Ollama, OpenRouter, and Alibaba dispatched review paths:**
  bridge artifacts written for their review are evaluated against the same
  canonical bridge envelope and compliance contract; no harness-specific
  waiver, dispatch-eligibility change, or routing mutation is requested.

Behavioral and byte parity are required for every applicable surface. No typed
waiver is requested or implied.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5445; bridge/gtkb-wi5445-active-template-hook-failclosed-parity-002.md; bridge/gtkb-envelope-protocol-slice-b-bridge-writer-envelope-head-006.md; bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-018.md",
  "canonical_authority": "DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001; ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001; DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001",
  "primary_route": "python -m pytest platform_tests/scripts/test_bridge_compliance_gate_disposition.py platform_tests/hooks/test_bridge_compliance_gate_envelope_head.py -q --tb=short",
  "before_behavior": "The active and template hooks each carry one stricter committed gate that the other lacks, and stale synthetic fixtures prevent focused parity tests from reaching their subject behavior.",
  "after_behavior": "Both hook copies carry the semantic union as identical raw bytes, disposition fixtures satisfy current envelope and membership contracts, and envelope behavior is exercised symmetrically.",
  "self_descriptive_naming": "Existing validator, preflight, disposition, and envelope names are preserved; fixture helpers state their isolated purpose.",
  "obsolete_guidance_disposition": "The rejected one-way overwrite is superseded by bidirectional semantic convergence; no historical bridge artifact is rewritten.",
  "history_preservation": "Both independently governed source deltas, their bridge chains, current tests, and prior hash evidence remain queryable.",
  "baseline": {
    "active_sha256": "f7fa1157af12ab578a5b4dd374a18c679ba48b0d235cb9957a8da65681b87fa2",
    "template_sha256": "85955f6fbcc88d6078107a63a23dbcb807a6547856f648246bf82e9cb008e16f",
    "disposition_result": "13 failed, 26 passed",
    "envelope_result": "5 passed",
    "targets_clean": true
  },
  "expected_result": {
    "hook_raw_bytes_identical": true,
    "preflight_fail_closed_in_both": true,
    "envelope_fail_closed_in_both": true,
    "disposition_failures": 0,
    "envelope_failures": 0
  },
  "rollback": {
    "instructions": "Before finalization, restore only the four targets to the recorded current-HEAD hashes if any acceptance check fails.",
    "verification": "Re-run target hashes, focused suites, and Git status; preserve unrelated work and append-only bridge history."
  },
  "hard_invariants": [
    "no existing gate is removed or weakened",
    "active and template hook raw bytes are identical at completion",
    "artifact-head enforcement exists in both copies",
    "preflight false and blocking errors fail closed in both copies",
    "test-only membership substitution is always restored",
    "no dispatcher, TAFE, harness, database, credential, release, deployment, or unrelated mutation"
  ],
  "fail_closed_conditions": [
    "any target differs from its recorded baseline before implementation-start",
    "latest status is not fresh GO",
    "implementation-start does not authorize all four exact targets",
    "either semantic delta is missing from either hook",
    "raw hook hashes differ after implementation",
    "any focused test fails",
    "any unrelated path appears in the candidate"
  ],
  "essential_context_preservation": "Preserve the VERIFIED envelope gate, stricter applicability handling, disposition contract, active/template raw parity, exact current hashes, sibling terminal evidence, and independent verification requirement."
}
```

## Specification Links

- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001`
- `DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-202666274` authorizes the project while preserving exact operation
  and verification gates.
- `DELIB-202666384` records the earlier WI-5166 parity review context.
- `bridge/gtkb-wi5445-active-template-hook-failclosed-parity-001.md` is the
  rejected stale one-way proposal.
- `bridge/gtkb-wi5445-active-template-hook-failclosed-parity-002.md` is the
  independent NO-GO and exact bidirectional correction request.
- `bridge/gtkb-envelope-protocol-slice-b-bridge-writer-envelope-head-006.md`
  proves the active envelope behavior is independently VERIFIED.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-018.md` proves
  the named sibling overlap is terminal.
- `bridge/gtkb-wi4672-bridge-compliance-gate-template-parity-004.md` is the
  historical raw-parity precedent.

## Owner Decisions / Input

No new owner decision is required. The revision follows the exact technical
correction requested by version 002 and preserves both previously governed
behaviors. It authorizes no dispatcher configuration or runtime mutation.

## Specification-Derived Verification

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Raw active/template parity | Compare bytes and SHA-256 after implementation | Exact identity. |
| Fail-closed preflight semantics | Existing and focused synthetic preflight cases against both hooks | False preflight or blocking errors deny in both. |
| Artifact-head semantics | Parameterized envelope module | Ten cases pass, five per hook. |
| Disposition semantics | Complete disposition module | Thirty-nine cases pass, zero fail. |
| Gate preservation | Run bridge hard-block, requirement-sufficiency, and project-metadata focused suites | No regression. |
| Source/test quality | Ruff check and format check on all four targets; py_compile on Python targets | All pass. |
| Scope isolation | Target-only Git diff/status, hashes, and `git diff --check` | No unrelated path or hunk. |

Required pre-report commands:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_compliance_gate_disposition.py platform_tests/hooks/test_bridge_compliance_gate_envelope_head.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py -q --tb=short
groundtruth-kb\.venv\Scripts\ruff.exe check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/scripts/test_bridge_compliance_gate_disposition.py platform_tests/hooks/test_bridge_compliance_gate_envelope_head.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/scripts/test_bridge_compliance_gate_disposition.py platform_tests/hooks/test_bridge_compliance_gate_envelope_head.py
git diff --check -- .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/scripts/test_bridge_compliance_gate_disposition.py platform_tests/hooks/test_bridge_compliance_gate_envelope_head.py
```

## Acceptance Criteria

1. Both hook copies contain the complete semantic union and have identical raw
   bytes.
2. All 39 disposition tests and all 10 parameterized envelope tests pass.
3. Adjacent hard-block, requirement-sufficiency, and project-metadata suites
   pass.
4. No gate is removed, bypassed, reordered to weaken enforcement, or hidden by
   a test-only patch.
5. Only the four exact clean targets are changed and independently verified.

## Pre-Filing Preflight Evidence

The applicability and mandatory ADR/DCL clause preflights are executed against
this exact completed candidate immediately before filing. Filing is permitted
only with `preflight_passed: true`, no missing required or advisory
specifications, no blocking errors, and zero blocking clause gaps.

## Implementation Boundary

No protected mutation may begin from this `REVISED` filing. Prime Builder must
first receive fresh independent `GO`, acquire the exact implementation claim,
and obtain a successful implementation-start packet for all four targets.
Independent post-implementation `VERIFIED` and focused finalization remain
mandatory. No dispatcher configuration change is authorized.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
