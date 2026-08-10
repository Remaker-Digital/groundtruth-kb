REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fe0e5-4e93-7280-9778-8d6738c9626d
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder; transcript ::init gtkb pb; harness A; GPT-5 model family
author_metadata_source: transcript init keyword and Codex runtime system metadata

# WI-6077 — Correct the state-report publication warning

bridge_kind: prime_proposal
Document: gtkb-wi6077-state-report-publication-warning
Version: 003
Responds to: bridge/gtkb-wi6077-state-report-publication-warning-002.md
Supersedes: bridge/gtkb-wi6077-state-report-publication-warning-001.md
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI6077-WI6081-LEAD-COMPLETION-20260808
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6077
implementation_scope: source
kb_mutation_in_scope: false
target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/state_report.py", "platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py"]

## Revision Disposition

This revision accepts NO-GO -002 findings F1–F3 and guard R4. It prunes six unrelated auto-linked specifications, supplies a concrete verification for every retained specification, adds WI-5933 and WI-5152 as the actual causal history, and explicitly covers the absent/disabled aggregate shape. The design and two-file implementation scope are unchanged.

## Summary

Correct `gt bridge state-report` so an enabled but stale bridge aggregate remains visible as audit state without claiming that all publications are refused or directing the operator to perform a prerequisite registry observation. Governed publication already self-observes the bridge aggregate inside its serialized control-plane transaction.

## Root Cause And Current Behavior

`state_report.py` currently renders this warning whenever registry publication is enabled and `aggregate_current is False`: “The bridge publication gate will refuse ALL publications … Remedy: gt registry observe …”. WI-5933 changed the publication path to self-observe under serialization before mint/consume, so a stale external observation is no longer a publication prerequisite. WI-5152 proves the manual observe command can clear the diagnostic; it does not prove publication requires it.

The absent/incomplete control-plane case is distinct: `_registry_publication_section` returns `enabled=False`, `aggregate_current=None`, and the warning branch does not execute. This proposal changes only the enabled-and-stale branch and must preserve the disabled shape without asserting publication availability.

## Proposed Change

1. Remove the obsolete `BRIDGE_AGGREGATE_REMEDY` constant.
2. Replace the enabled-and-stale warning with truthful audit text: the aggregate observation is stale audit state; governed publication self-observes under serialization; this diagnostic does not mean publications are refused.
3. Extend the focused stale-aggregate test to assert the old refusal/remedy strings are absent and to mint, write, and consume a governed publication capability without a preceding manual observe.
4. Retain and strengthen the incomplete-control-plane test so the disabled/unavailable shape emits no self-observation or publication-availability claim.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the state report describes the canonical bridge publication path and may not direct operators to a competing prerequisite.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this revision carries only concretely relevant specifications and exact in-root targets.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — each retained specification has an executable derived verification below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project, PAUTH, work item, and exact targets are explicit above.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both targets stay within the GT-KB platform root and outside adopter application trees.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the report must distinguish a stale observation from the serialized publication transaction that refreshes it.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — identical report inputs must render identical text; publication-capability transitions are exercised through the deterministic service.

## Prior Deliberations

- `WI-5933` — introduced serialized self-observation, making the old prerequisite warning stale.
- `WI-5152` — recorded that manual observe clears the indicator, establishing that the remedy is effective but unnecessary for publication.
- `WI-6077` — current defect and acceptance authority.
- `DELIB-20260808-WI6077-WI6081-LEAD-PRIME-COMPLETION-DIRECTIVE` — owner directive to drive WI-6077 through completion.
- `bridge/gtkb-wi6077-state-report-publication-warning-002.md` — independent NO-GO and required revisions accepted here.

## Owner Decisions / Input

The owner directed the lead Prime Builder to complete WI-6077. No new owner decision is required; the change preserves registry and bridge semantics and corrects only an inaccurate operator claim plus its focused tests.

## Requirement Sufficiency

Existing requirements are sufficient. WI-6077 specifies the false warning, the causal WI-5933 behavior is already implemented, and the retained governance surfaces fully constrain this two-file correction.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-6077; NO-GO -002 findings F1-F3 and R4; owner lead-completion directive",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "gt bridge state-report",
  "before_behavior": "Enabled stale audit state falsely says every publication is refused and prescribes manual observe as a prerequisite.",
  "after_behavior": "Enabled stale audit state remains visible and truthfully explains serialized self-observation; disabled state remains unavailable and makes no publication claim.",
  "self_descriptive_naming": "State-report warning text names stale audit state and serialized publication behavior directly.",
  "obsolete_guidance_disposition": "The false refusal and prerequisite-remedy strings are removed; the stale diagnostic remains.",
  "history_preservation": "The numbered bridge chain remains append-only.",
  "baseline": {
    "work_item": "WI-6077",
    "project": "PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY",
    "target_paths": ["groundtruth-kb/src/groundtruth_kb/bridge/state_report.py", "platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py"],
    "linked_specifications": ["GOV-FILE-BRIDGE-AUTHORITY-001", "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001", "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001", "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001", "ADR-ISOLATION-APPLICATION-PLACEMENT-001", "GOV-SOURCE-OF-TRUTH-FRESHNESS-001", "GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001"]
  },
  "expected_result": {
    "summary": "Truthful stale-audit warning with successful governed publication coverage.",
    "scope": ["Correct warning text", "Preserve disabled shape", "Prove mint/write/consume succeeds without manual observe"],
    "acceptance_criteria": ["No refusal claim", "No prerequisite manual-observe remedy", "Stale audit remains visible", "Disabled shape remains claim-free", "Focused tests green"]
  },
  "rollback": {
    "instructions": "Revert only the approved source and test hunks under governed authority.",
    "verification": "Rerun the focused state-report CLI module and bridge preflights."
  },
  "hard_invariants": ["No registry data mutation", "No publication-gate weakening", "Exact two-file scope"],
  "fail_closed_conditions": ["Latest status is not GO", "Claim or implementation packet is missing", "Focused service transition cannot be exercised"],
  "essential_context_preservation": "The revised proposal preserves root cause, exact targets, causal history, absent-state guard, and executable verification mappings."
}
```

## Specification-Derived Verification Plan

| Specification | Derived verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | In the stale fixture, exercise canonical `mint_bridge_publication_capability` → write exact candidate bytes → `consume_bridge_publication_capability`; assert consumed without `gt registry observe`, while the report remains read-only. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live applicability preflights; assert the seven retained links are cited, both exact targets are classified, and `missing_required_specs=[]`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry this row-by-row mapping and the exact focused test results into the implementation report; no retained specification may be represented by generic boilerplate. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run the operation-time authorization check and assert the explicit WI-6077 PAUTH, project id, work item, and two target paths match this proposal. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Assert both changed paths resolve under `E:/GT-KB` and no `applications/` path changes. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Assert enabled stale state renders `aggregate_current=no` and the truthful audit warning, then the governed publication transition succeeds through its serialized self-observation path; separately assert disabled state renders unavailable and no publication claim. |
| `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` | Run the focused CLI module twice; assert identical markdown for the same stale input and identical consumed capability outcome. |

## Commands To Execute

- `python scripts/bridge_applicability_preflight.py --content-file <candidate> --bridge-id gtkb-wi6077-state-report-publication-warning`
- `python scripts/adr_dcl_clause_preflight.py --content-file <candidate> --bridge-id gtkb-wi6077-state-report-publication-warning`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py -q --tb=short`
- Repeat the focused pytest command and report both observed results.
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/state_report.py platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge/state_report.py platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py`
- `git diff --check -- groundtruth-kb/src/groundtruth_kb/bridge/state_report.py platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py`

## Acceptance Criteria

- The stale diagnostic no longer claims all publications are refused.
- The warning no longer prescribes manual observation as a publication prerequisite.
- The warning truthfully states that governed publication self-observes under serialization.
- Enabled stale audit state remains visible with exact stale record ids.
- Disabled/absent control-plane state remains unavailable and emits no self-observation or publication-availability claim.
- A focused test proves stale reporting and successful canonical publication coexist without manual observe.
- The focused module passes twice; Ruff and diff checks pass.

## Scope Boundaries

No registry data, database, configuration, bridge writer, publication gate, dispatcher, deployment, credential, or application path is modified. This thread changes only the state-report string/constant and its focused CLI coverage.

## Risk And Rollback

Risk is low and operator-facing: imprecise replacement text could overclaim availability in the disabled case. The explicit disabled-shape test prevents that. Rollback reverts only the two approved hunks and reruns the focused module; bridge history remains append-only.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge/state_report.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py`

## Recommended Commit Type

`fix:`

---

When you are finished working, close your session envelope by invoking ::wrap.
