NEW

# Implementation Proposal - WI-4365 prompt-submit surface classification

bridge_kind: prime_proposal
Document: gtkb-wi4365-prompt-submit-surface-classification
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-06-29 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: auto-builder-2026-06-29T010846Z
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-SIGNAL-QUALITY-BRIDGE-SIGNAL-QUALITY-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-BRIDGE-SIGNAL-QUALITY
Work Item: WI-4365

target_paths: ["independent-progress-assessments/CODEX-INSIGHT-DROPBOX/WI-4365-PROMPT-SUBMIT-SURFACE-CLASSIFICATION.md"]

implementation_scope: classification report
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal implements `WI-4365` as a report-only bridge signal-quality classification. The implementation will produce a deterministic classification artifact for the known Claude/Codex prompt-submit surface differences named by the originating Loyal Opposition finding: `owner-decision-tracker`, `bridge-axis-2-surface`, `glossary-expansion`, and the cancelled prompt-submit hook surfaces that create noisy operator signal.

The implementation will not modify hook source, harness configuration, tests, MemBase, specifications, ADR, DCL, GOV, or bridge protocol files. It will read live in-root hook/config/test surfaces, classify each difference as intentional asymmetry, parity gap, or noisy surface needing removal/delay/justification, and name the concrete follow-up action for each finding.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - This report is proposed through the append-only file bridge, with `NEW` as the Prime Builder status and Loyal Opposition review required before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The proposal carries project, work item, project authorization, and JSON `target_paths` metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The proposal identifies the governing specs and maps them to verification evidence before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The verification plan derives checks from the linked specs and from the work item's acceptance criteria.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The classification will preserve a durable in-root report rather than leaving the cross-harness finding in transient chat or scratch memory.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The report turns an accepted review finding into an explicit artifact with classification, impact, and follow-up.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The work crosses the threshold from observation to accepted future work and therefore needs an artifact lifecycle outcome.
- `GOV-STANDING-BACKLOG-001` - Any follow-up implementation work discovered by the classification will be reported as a concrete backlog or bridge candidate instead of being mutated directly.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - The classification is specifically about when Codex should use parity, fallback, or intentional non-parity for hook behavior.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - The report will compare Claude and Codex prompt-submit surfaces and distinguish justified asymmetry from parity gaps.
- `GOV-SESSION-SELF-INITIALIZATION-001` - Prompt-submit hooks affect session startup and owner-facing session behavior; classification must protect required initialization semantics.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - The noisy/cancelled hook portion of the work must consider startup and prompt-submit cost/signal impact.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner-decision capture and AUQ routing are named surfaces in the finding; the report must identify whether their current harness coverage is sufficient.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The report target is an in-root GT-KB assessment artifact and does not create or depend on external project state.

## Prior Deliberations

- `DELIB-20260605-GLOSSARY-CLI-SCAN-DELTA-APPROVAL` - Owner approval to convert the glossary/CLI scan findings into governed backlog and bridge proposals. This proposal is the WI-4365 conversion for the prompt-submit surface finding.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-04-GLOSSARY-CLI-SCAN-DELTA.md` - Source Loyal Opposition report. Observation 4 identified the Claude/Codex prompt-submit differences and requested classification into intentional difference, parity gap, or noisy surface removal/delay/justification.

## Owner Decisions / Input

No new owner decision is required before this proposal. The work item and the active project authorization already approve a bounded classification artifact under `PROJECT-GTKB-BRIDGE-SIGNAL-QUALITY`. The proposed implementation is report-only and avoids formal KB mutation or protected hook/config/source changes.

## Requirement Sufficiency

Existing requirements are sufficient. `WI-4365` defines the acceptance criterion for a classification artifact that names each prompt-submit difference, its class, operator impact, and follow-up action. The linked artifact-governance, bridge-authority, hook-parity, and cross-harness parity specifications define the process and verification surface.

## Proposed Scope

The implementation will create `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/WI-4365-PROMPT-SUBMIT-SURFACE-CLASSIFICATION.md` with:

- A source inventory covering Claude and Codex prompt-submit hook registrations, relevant capability registry/system-interface entries, and focused hook parity tests.
- A classification matrix for each named surface: `owner-decision-tracker`, `bridge-axis-2-surface`, `glossary-expansion`, cancelled prompt-submit hook behavior, and any adjacent prompt-submit surface discovered while validating those named items.
- For each row: evidence path, current Claude behavior, current Codex behavior, classification, owner/operator impact, and follow-up action.
- Explicit treatment of accepted asymmetries versus parity gaps, with no direct hook/config mutation.
- Concrete follow-up recommendations that can become later bridge proposals or backlog candidates if implementation is needed.

## Out of Scope

- Editing `.claude/settings.json`, `.codex/hooks.json`, `.claude/hooks/`, `.codex/gtkb-hooks/`, source, tests, MemBase, ADR, DCL, GOV, SPEC, PAUTH, or project records.
- Creating formal work items directly from this implementation. Follow-up candidates will be named for later governed capture.
- Treating automation memory, cached startup reports, copied bridge excerpts, or stale queue artifacts as authority.

## Cross-Harness Disposition

This proposal is explicitly cross-harness in subject matter but report-only in implementation. The classification must evaluate Claude and Codex surfaces from live in-root files and must not assume equality from harness identity, vendor identity, automation memory, or prior chat summaries. Any accepted asymmetry must cite the in-root registry or rule surface that makes it intentional; otherwise it remains a parity gap or noisy surface candidate.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected Result |
| --- | --- | --- |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4365-prompt-submit-surface-classification-001.md --bridge-id gtkb-wi4365-prompt-submit-surface-classification` | Proposal metadata, project linkage, work item linkage, PAUTH, and target paths are accepted. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4365-prompt-submit-surface-classification-001.md --bridge-id gtkb-wi4365-prompt-submit-surface-classification` | No blocking ADR/DCL clause gaps. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` and `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Report includes a Claude-vs-Codex prompt-submit matrix with cited evidence from `.claude/settings.json`, `.codex/hooks.json`, `config/agent-control/harness-capability-registry.toml`, `config/agent-control/system-interface-map.toml`, and focused parity tests. | Every named prompt-submit surface has classification, impact, and follow-up. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Inspect the report artifact. | The finding is preserved as a durable in-root assessment artifact and not left in scratch memory. |
| `GOV-STANDING-BACKLOG-001` | Inspect the report recommendations. | Follow-up implementation work is named as candidate work for governed capture, not directly mutated. |
| `GOV-SESSION-SELF-INITIALIZATION-001`, `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`, and `SPEC-AUQ-POLICY-ENGINE-001` | Report rows for owner-decision/AUQ, AXIS 2, glossary expansion, and cancelled hook behavior cite their session-startup or owner-action impact. | The report explains whether each prompt-submit behavior supports required startup/owner-action semantics or creates noise/cost. |
| Hook parity evidence for the report rows | `python -m pytest platform_tests/scripts/test_codex_hook_parity.py platform_tests/hooks/test_owner_decision_tracker.py platform_tests/hooks/test_glossary_expansion.py platform_tests/scripts/test_bridge_axis_2_surface.py -q --tb=short` | Targeted hook parity and surface tests pass or any failure is explained as out of scope before implementation report filing. |

## Acceptance Criteria

- The report exists at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/WI-4365-PROMPT-SUBMIT-SURFACE-CLASSIFICATION.md`.
- The report classifies each named prompt-submit difference and any directly adjacent discovered surface.
- Each classification row includes evidence path, Claude behavior, Codex behavior, classification, owner/operator impact, and follow-up action.
- Accepted asymmetries cite live in-root authority.
- Parity gaps and noisy surfaces are recorded as follow-up recommendations, not directly implemented.
- Bridge applicability and ADR/DCL clause preflights pass for the filed proposal and for the completed report when applicable.

## Risk / Rollback

Risk is low because the implementation is additive and report-only. The main risk is misclassifying a cross-harness difference without citing live authority; verification mitigates that by requiring path-cited evidence for each row. Rollback is deletion of the single proposed report artifact before commit, or a follow-up bridge revision if Loyal Opposition finds a classification gap after filing.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4365-prompt-submit-surface-classification`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`docs:` because the approved implementation output is an assessment/classification report, not source behavior.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
