NO-GO
author_identity: loyal-opposition/codex/A
author_harness_id: A
author_session_context_id: codex-gtkb-lo-2026-06-06-dispatcher-config-cli
author_model: GPT-5 Codex
author_model_version: 2026-06-06
author_model_configuration: reasoning=high

# NO-GO: Dispatcher Config CLI Whole-Candidate Validation

## Reviewed Proposal

- `bridge/gtkb-dispatcher-config-cli-whole-candidate-validation-001.md`
- Latest `bridge/INDEX.md` status at review time: `NEW`

## Decision

NO-GO for procedural authorship only.

The proposal content is mechanically well-formed and the implementation direction matches the owner clarification, but the proposal was authored by the active Loyal Opposition harness (`loyal-opposition/codex/A`). Per the file bridge protocol, implementation proposals are Prime Builder artifacts and GO/NO-GO review is the Loyal Opposition handoff. A cannot fairly author this `NEW` proposal and then issue GO on it.

Mike selected the `B` path after being offered: "B adopt/review path" versus "A emergency exception." Therefore the next correct step is a Prime Builder revision/adoption, not a Loyal Opposition self-GO.

## Findings

### F1 (P1): Prime Builder adoption required before GO

Evidence:

- `bridge/gtkb-dispatcher-config-cli-whole-candidate-validation-001.md` records `author_identity: loyal-opposition/codex/A`.
- `.claude/rules/file-bridge-protocol.md` assigns `NEW` and `REVISED` proposal status to Prime, and assigns `GO` / `NO-GO` review status to Loyal Opposition.
- Owner reply on 2026-06-06 selected the `B` path, meaning Prime Builder B should adopt/revise rather than A using an emergency self-review exception.

Impact:

- If A self-GOs this proposal, the implementation would bypass the independent Prime Builder / Loyal Opposition review model that the bridge is designed to preserve.
- Protected source edits remain correctly blocked by `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` until a GO exists on a Prime-authored or Prime-adopted proposal.

Required action:

- Prime Builder B should file `bridge/gtkb-dispatcher-config-cli-whole-candidate-validation-003.md` as `REVISED`.
- B may adopt the `-001` technical content substantially as-is, but the revised file must carry Prime Builder authorship metadata and should keep the same or refined target paths, specification links, Code Quality Baseline, acceptance criteria, and verification plan.
- After B files the `REVISED` version, Loyal Opposition A can review it for GO/NO-GO on the implementation merits.

## Clean Mechanical Checks Observed

The `-001` proposal passed the two mechanical checks run during this review:

- `python scripts/check_code_quality_baseline_parity.py bridge/gtkb-dispatcher-config-cli-whole-candidate-validation-001.md`
  - Result: `Code Quality Baseline parity clean`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatcher-config-cli-whole-candidate-validation`
  - `packet_hash`: `sha256:945f65d6d3aaaea2d264ad1b3339157e289707a2ac7431d17844cd50883f9f20`
  - `missing_required_specs`: `[]`
  - `missing_advisory_specs`: `[]`

These clean checks are advisory context for B's adoption. They do not override F1.

## Recommendation

Prime Builder B should adopt this as a `REVISED` proposal with PB authorship and then let Loyal Opposition A review it normally. The likely implementation remains: remove role/topology auto-selection from `gt mode set-role`, `gt harness set-role`, and the legacy `scripts/harness_roles.py` set-role path; validate the whole candidate dispatcher configuration before durable writes; reject invalid candidate updates.
