GO – gtkb-wi5272-ordinary-worker-prompt-skill-contract v005 (REVISED proposal)
::init gtkb pb
::open test

author_identity: OpenRouter F
author_harness_id: F
author_session_context_id: 2026-07-18T16-31-38Z-loyal-opposition-F-6063fd
author_model: deepseek/deepseek-v4-flash
author_model_version: deepseek-v4-flash
author_model_configuration: OpenRouter endpoint=https://openrouter.ai/api/v1; route=openrouter-cloud-default; requested_model=moonshotai/kimi-k2.7-code; model_source=response.model; account_override=true

Bridge document: bridge/gtkb-wi5272-ordinary-worker-prompt-skill-contract-005.md
Bridge kind: prime_proposal (REVISED)
Responds to: bridge/gtkb-wi5272-ordinary-worker-prompt-skill-contract-004.md
Revises: bridge/gtkb-wi5272-ordinary-worker-prompt-skill-contract-001.md

Work-intent claim: rowid 33035, session 6863e929-50d6-4dc2-8bd0-6f2295e0f562 (other harness held at review time; claim evidence consulted per protocol)

## Preflight Results

### Bridge Applicability Preflight

Command: `"E:/GT-KB/groundtruth-kb/.venv/Scripts/python.exe" scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5272-ordinary-worker-prompt-skill-contract`

- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- declared_target_paths: 22 targets match Files Expected To Change section
- content_source: bridge_file_operative (bridge/gtkb-wi5272-ordinary-worker-prompt-skill-contract-005.md)

### ADR/DCL Clause Preflight

Command: `"E:/GT-KB/groundtruth-kb/.venv/Scripts/python.exe" scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5272-ordinary-worker-prompt-skill-contract`

- Clauses evaluated: 5
- must_apply: 3, may_apply: 2
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory — PASS (exit 0)

## Review Findings

1. **Foundation F1 resolved.** The five governing foundation records (DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001, DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001, DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001, DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001, ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001) are now version 2, status=specified, with passing assertions. Foundation v034 is VERIFIED and committed at 6262862c8852d4d94530a4074a3047f921e7164e.

2. **Foundation F2 resolved.** The foundation-first owner decision (DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST) is explicitly carried.

3. **Foundation F3 resolved.** Fresh filing-time checks of foundation state are required at implementation-start, and the proposal documents this requirement.

4. **Predecessor barriers are correctly stated.** WI-5270 and WI-5271 must both be terminal and focused-finalized before implementation begins. WI-5464 is the correction/re-evaluation path for WI-5270 v004. The dirty `.codex/skills/MANIFEST.json` state is identified as a blocking condition.

5. **Activity envelope requirement is correctly stated.** Implementation must start in an initialized `ops` activity envelope; ordinary or build envelope states fail closed.

6. **Dispatcher hold preserved.** The dispatcher-configuration troubleshooter hold (DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD) is honored; no dispatcher config/runtime mutation is authorized.

7. **Specification linkage is complete.** All 24 specification IDs cited are appropriate for the scope of prompt/rule/skill/config startup guidance and the attendant test targets.

8. **Cross-harness disposition is present and covers the four dispatchable harnesses plus headless providers.** Shared-surface parity is correctly scoped.

9. **Hard implementation-start gates are clearly documented** and include all ten necessary conditions for safe entry.

## Substantive Quality Assessment

This revision is a substantive, well-structured, and diligently corrected proposal. Every v004 blocking condition is addressed: the foundation is now real and evaluated, the foundation-first decision is cited, and filing-time checks are mandated. The predecessor-dependency chain, activity-envelope requirement, and dispatcher-hold preservation are explicit and unambiguous. The 22-target scope is consistent with the work item's prompt/rule/skill/config purpose, and the cross-harness disposition is appropriate.

The proposal does not claim to authorize current implementation — it correctly identifies that WI-5270 and WI-5271 must be terminal first, and that an `ops` envelope is required. This is honest scoping.

## Verdict

**GO** — The proposal is approved for independent review. It may proceed to the implementation queue once all hard gates (WI-5270 terminal + focused-finalized, WI-5271 terminal + focused-finalized, clean manifest resolution, ops envelope, fresh claim/start/authorization) are satisfied.

Evidence files consulted:
- bridge/gtkb-wi5272-ordinary-worker-prompt-skill-contract-005.md (operative)
- bridge/gtkb-wi5272-ordinary-worker-prompt-skill-contract-004.md (prior)
- bridge/gtkb-dispatcher-black-box-spec-foundation-034.md (foundation commit evidence)
- harness-state/harness-registry.json (role authority)
- harness-state/harness-identities.json (identity resolution)