REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; governed bridge revision; no direct harness contact
author_metadata_source: explicit_interactive_session_metadata

# Revised Implementation Proposal - Rebase WI-5216 Provider Verdict Denial-Loop Recovery

bridge_kind: prime_proposal
Document: gtkb-wi5216-provider-verdict-denial-loop-recovery
Version: 005
Responds to: bridge/gtkb-wi5216-provider-verdict-denial-loop-recovery-004.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5216

target_paths: ["scripts/cloud_harness_base.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_ollama_harness.py"]

implementation_scope: source | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

## Revision Claim

This revision answers version 004 by replacing the operation-time-invalid
WI-specific PAUTH with the active registered-vocabulary project authorization,
removing the now-terminal WI-5211 and WI-5254 blockers, and rebasing the work on
the current provider-recovery implementation.

The bounded publisher-only state machine proposed in version 001 is now present
in committed cloud and Ollama baselines through later governed provider work.
The remaining WI-5216 behavior is narrower: an existing raw Write, Edit, or
Bash bridge-verdict mutation denial must move the affected LO route into that
bounded publisher-only state without weakening the denial or accepting prose as
completion.

Current working-tree bytes contain a partial cloud candidate for that trigger
and its focused test, commingled with unrelated WI-5471 and WI-5495 changes.
The Ollama equivalent is not present. Those bytes remain quarantined candidate
evidence. This revision adopts no source or test byte and authorizes no
implementation start while any exact-target predecessor remains nonterminal.

## Response To Version 004

### F1 - Stale Authorization

Resolved for proposal purposes. This revision cites
`PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE`, version 2.
It is active, has no per-work-item inclusion restriction, allows bridge,
metadata, source, test, configuration, documentation, runtime-state, and
governance-evidence mutations, and uses only registered forbidden-operation
names.

The invalid narrow authorization
`PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5216-VERDICT-LOOP-RECOVERY-20260712`
is historical evidence only and is not relied upon by this revision. WI-5232
therefore does not need to mutate or replace that narrow record before WI-5216
can proceed.

### F1 - Parent And Preflight Dependencies

- WI-5211 is terminal VERIFIED at
  `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md`.
- WI-5254 is terminal VERIFIED at
  `bridge/gtkb-wi5254-pauth-amendment-packet-preflight-008.md`.
- WI-5178 remains a separate operation-time enforcement program. It does not
  block this revised proposal because the active project-scope PAUTH already
  passed a governed claim/start/implementation/verification lifecycle for
  WI-5211. Any actual WI-5216 implementation start must still pass the current
  schema-v3 operation-time gate; this revision does not waive or predict it.

### Current-State Rebase

The committed cloud and Ollama loops already provide:

- publisher-only recovery with a fixed three-turn bound;
- refusal of final prose while a required verdict remains unpublished;
- canonical PublishBridgeVerdict delegation;
- bounded failed-publisher diagnostics; and
- raw bridge mutation guards.

WI-5216 no longer needs to implement that complete state machine from scratch.
It needs only the missing semantic transition from a canonical raw bridge
mutation denial into the existing recovery state, with equivalent cloud/F and
Ollama/D behavior.

## Exact Overlap And Execution Order

The four target files are shared by active provider-reliability work. The
required serial order is:

1. WI-5471 tool-call argument parse resilience reaches terminal independent
   verification and focused finalization.
2. WI-5495 F/OpenRouter publisher recovery tool-choice forcing reaches terminal
   independent verification and focused finalization.
3. WI-5545 per-assigned-document provider completion reaches terminal
   independent verification and focused finalization.
4. WI-5542 D/Ollama publisher-envelope recovery reaches terminal independent
   verification and focused finalization.
5. WI-5216 re-reads the resulting committed baseline, refreshes exact hashes
   and target ownership, and either adopts a still-required narrow trigger or
   files a no-mutation closure if the predecessors already satisfy TEST-11370.

No WI-5216 claim or implementation-start packet may be acquired before steps 1
through 4 are terminal. No current dirty source or test byte may be staged,
committed, or attributed to WI-5216 under this revision.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5216 and linked TEST-11370 define the
remaining semantic transition and bounded acceptance contract. The active
project PAUTH, terminal WI-5211 publisher capability, current provider-recovery
specifications, and the serialized predecessor list above provide a complete
review boundary. No new owner decision, dispatcher change, provider route
change, or runtime allowance change is required.

## In-Root Placement Evidence

All four declared target paths are inside `E:/GT-KB`. All evidence cited by
this revision is canonical and in-root.

The project and PAUTH names retain their canonical historical identifiers.
They do not assert the existence of a harness G. The active scope is the A
Prime Builder and D/F provider-recovery workflow.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CLOUD-HARNESS-TEMPLATE-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202666173` - owner direction to complete genuine governed fleet proof
  and correct every discovered defect.
- `DELIB-202666274` - project-scope repair authorization preserving bridge,
  claim, implementation-start, independent verification, and separate
  mechanical-operation gates.
- `bridge/gtkb-wi5216-provider-verdict-denial-loop-recovery-001.md` through
  `-004.md` - original proposal, superseded GO, Prime NO-ACTION, and corrected
  NO-GO.
- `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md` - terminal
  D/F governed publisher capability.
- `bridge/gtkb-wi5254-pauth-amendment-packet-preflight-008.md` - terminal
  fail-earlier PAUTH amendment preflight.
- `bridge/gtkb-wi5471-toolcall-arg-parse-resilience-005.md` - current
  hunk-isolated parse-resilience report awaiting independent verdict.
- `bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-008.md` - current
  F-only tool-choice revision awaiting independent verdict.
- `bridge/gtkb-wi5545-per-document-provider-completion-002.md` - current GO
  sequenced after WI-5471 and WI-5495.
- `bridge/gtkb-wi5542-ollama-publisher-envelope-recovery-001.md` - current D
  recovery proposal sequenced after WI-5545.

## Owner Decisions / Input

No new owner decision is required.

`DELIB-202666274` is the owner decision recorded by the active project-scope
PAUTH. It authorizes source/test repair while preserving exact bridge GO,
matching claim, schema-v3 implementation-start, independent verification, and
separate Git-finalization gates. This revision grants no direct harness
contact, dispatcher or TAFE mutation, credential action, cleanup, push,
deployment, release, or unrelated mutation.

## Proposed Scope

After all four predecessors are terminal and exact target bytes are reconciled:

1. Classify only a denial produced by the existing canonical raw bridge
   mutation guard for Write, Edit, or Bash on an LO bridge-review or
   verification route.
2. Preserve the exact denial as model-visible tool history.
3. Move the route into the existing bounded publisher-only recovery state for
   its next provider turn.
4. Keep the provider responsible for authoring the verdict and complete body;
   the canonical publisher remains the sole writer.
5. Apply equivalent behavior to shared cloud/F and standalone Ollama/D loops.
6. Do not trigger recovery for native-hook denials, timeouts, ordinary failed
   bridge reads, non-bridge guarded mutations, or arbitrary commands that
   merely contain the text `bridge/`.
7. If predecessor work already implements equivalent behavior, make no source
   mutation; prove TEST-11370 against the committed baseline and file an honest
   no-mutation implementation report.

## Cross-Harness Disposition

- A/Codex remains Prime Builder only; no LO role or provider-loop behavior is
  added to A.
- D/Ollama receives the standalone semantic transition only if WI-5542 does
  not already satisfy it.
- F/OpenRouter inherits the shared-cloud semantic transition only if WI-5495
  and WI-5545 do not already satisfy it.
- B, C, E, and H receive no role, route, eligibility, cap, provider, or runtime
  change.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-202666173; DELIB-202666274; WI-5216; TEST-11370",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "provider run_tool_loop to canonical PublishBridgeVerdict recovery",
  "before_behavior": "A provider can vary denied raw bridge mutation attempts and consume the full turn allowance without entering the existing governed publisher recovery state.",
  "after_behavior": "A canonical raw bridge mutation denial on an LO route enters the existing bounded governed publisher recovery state while unrelated failures and ordinary tool use remain unchanged.",
  "self_descriptive_naming": "The WI-5216 scope names denial-loop recovery, provider family, canonical publisher transition, and exact predecessor order.",
  "obsolete_guidance_disposition": "The original five-file from-scratch state-machine scope and invalid WI-specific PAUTH are superseded by this current-baseline revision.",
  "history_preservation": "The numbered bridge chain, TEST-11370, terminal predecessor verdicts, and future exact implementation report remain append-only and queryable.",
  "baseline": {
    "recovery_turn_bound": 3,
    "raw_guard_preserved": true,
    "provider_families": 2,
    "dispatcher_topology_mutations": 0
  },
  "expected_result": {
    "recovery_turn_bound": 3,
    "raw_guard_preserved": true,
    "provider_families": 2,
    "dispatcher_topology_mutations": 0,
    "full_budget_denial_loops": 0
  },
  "rollback": {
    "instructions": "Revert only independently reviewed WI-5216 source and test hunks.",
    "verification": "Rerun TEST-11370 mappings and the affected cloud and Ollama suites."
  },
  "hard_invariants": [
    "canonical raw bridge mutation guards remain fail closed",
    "PublishBridgeVerdict remains the sole numbered verdict writer",
    "A remains Prime Builder only",
    "D and F allowances and assigned roles remain unchanged",
    "no foreign predecessor byte is attributed to WI-5216"
  ],
  "fail_closed_conditions": [
    "any exact-target predecessor is nonterminal",
    "the live GO, claim, or schema-v3 implementation-start packet is missing",
    "target hashes or ownership differ from the reviewed baseline",
    "the trigger cannot distinguish canonical raw bridge denial from an unrelated error",
    "TEST-11370 or an affected provider suite fails"
  ],
  "essential_context_preservation": "The provider-authored verdict body, assigned bridge document, trusted session and model provenance, raw denial result, full runtime allowances, and numbered bridge history remain observable."
}
```

## Specification-Derived Verification Plan

| Governing requirement | Executable verification | Required result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Fresh live applicability and clause preflights; independent GO; exact claim and schema-v3 implementation-start validation after predecessor closure. | No missing specs or blocking gaps; no protected work starts from this revision alone. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` and TEST-11370 | Focused cloud and Ollama tests for denied raw bridge mutation, publisher-only next turn, successful canonical publication, and bounded refusal. | Both provider families recover or fail bounded without weakening the raw guard. |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` | Run the complete cloud-base and OpenRouter focused suites. | F inherits the shared behavior; no adapter-specific duplicate implementation. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Run the complete Ollama focused suite. | D has equivalent outcomes through its provider-appropriate recovery path. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Existing trusted publisher metadata tests plus recovered publication fixtures. | Dispatcher session and provider model provenance remain trusted and unchanged. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Static allowance checks and existing lifetime regressions. | 600 turns, 900-second operations, 60-minute model/session, 29,400-second worker lifetime, and 29,700-second leases are unchanged. |
| `GOV-WORK-TREE-HYGIENE-001` | Exact target status, hashes, diff inventory, predecessor ownership, Ruff check, Ruff format check, compile checks, and focused finalization review. | No foreign WI-5471, WI-5495, WI-5545, or WI-5542 byte is attributed to WI-5216. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | After deterministic closure, fresh substantive governed D and F dispatches through canonical TAFE/bridge routing. | Each target-authored run publishes a substantive governed verdict, or a new distinct failure is captured as a separate hygiene work item. |

## Acceptance Criteria

1. TEST-11370 is executed and mapped to exact cloud and Ollama tests.
2. A canonical raw bridge mutation denial remains denied and visible.
3. The next affected turn enters only the existing bounded governed-publisher
   recovery path.
4. Prose, malformed calls, unknown tools, and publisher failures cannot count
   as bridge completion.
5. Noncanonical or incidental errors do not falsely trigger recovery.
6. No runtime allowance, dispatchability, role, route, cap, TAFE state, lease,
   live worker, or dispatcher configuration changes.
7. WI-5471, WI-5495, WI-5545, and WI-5542 are terminal before any WI-5216
   protected implementation.
8. Independent LO verification and focused finalization include only reviewed
   WI-5216 bytes and canonical bridge evidence.
9. Fresh substantive D and F dispatcher-produced work succeeds before the
   final 60-item acceptance sequence begins.

## Pre-Filing Preflight Subsection

The governed filing helper must run the candidate applicability and mandatory
clause preflights against the exact final bytes and refuse publication unless:

- `preflight_passed: true`;
- `missing_required_specs: []`;
- `missing_advisory_specs: []`; and
- the mandatory clause gate exits 0 with zero blocking gaps.

## Risks And Rollback

The main risk is false recovery activation from an arbitrary error containing a
bridge path. The implementation must bind the transition to the canonical raw
bridge mutation denial class, not to a broad `ERROR` plus substring test.

The second risk is adopting commingled provider-loop bytes. The serial
predecessor order, fresh hash inventory, and no-start rule prevent that.

Rollback reverts only independently reviewed WI-5216 source/test hunks. It must
not reset, clean, stash, rewrite, or disturb unrelated worktree state. Bridge
and MemBase evidence remain append-only.

## Files Expected To Change

Only after predecessor closure and only if TEST-11370 remains unsatisfied:

- `scripts/cloud_harness_base.py`
- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_ollama_harness.py`

No file mutation is performed by filing this revision.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
