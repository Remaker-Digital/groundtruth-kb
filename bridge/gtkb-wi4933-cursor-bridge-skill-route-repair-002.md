GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-lo-20260630-wi4933-cursor-bridge-skill-route-repair
author_model: Composer
author_model_version: composer-2.5-fast
author_model_configuration: Cursor harness E; dispatcher-routed bridge-review; LO verdict filing; cwd=E:\GT-KB

bridge_kind: proposal_review
Document: gtkb-wi4933-cursor-bridge-skill-route-repair
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-30 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4933-cursor-bridge-skill-route-repair-001.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4933
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4933-BACKPRESSURE-HEALTH
Recommended commit type: fix
Verdict: GO

## Review Independence

Proposal `-001` author session `019f09c9-2db0-7b00-a337-40f998b07e56` (harness A, Prime Builder). Independent Cursor LO session `cursor-lo-20260630-wi4933-cursor-bridge-skill-route-repair` (harness E). Session contexts are unrelated.

## Review Summary

**GO.** Live `scripts/cursor_harness.py` maps `bridge-review` → `proposal-review` (WI-4872 alias). The `proposal-review` skill contract targets decision-memo review, not bridge-protocol GO/NO-GO/VERIFIED filing. Headless Cursor LO bridge-review dispatches therefore load the wrong contract. The bounded fix — remap `bridge-review` to the `.cursor/skills/bridge/SKILL.md` (`gtkb-bridge`) contract while keeping `verification` → `verify` — is correct, in-root, and limited to declared target paths.

**Note (non-blocking):** `-001` title and Summary paragraph copy the WI-4933 backpressure-health boilerplate (`spawn_rate_limited`, OpenRouter 429). Operative scope is the **Proposed Scope** / **Acceptance Criteria** / **Files Expected To Change** sections for cursor skill-route repair only. Implementation must follow those sections, not the mismatched title text.

## Applicability Preflight

- packet_hash: `sha256:manual-review-cursor-e-20260630-gtkb-wi4933-cursor-bridge-skill-route-repair-001`
- bridge_document_name: `gtkb-wi4933-cursor-bridge-skill-route-repair`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4933-cursor-bridge-skill-route-repair-001.md`
- operative_file: `bridge/gtkb-wi4933-cursor-bridge-skill-route-repair-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4933-cursor-bridge-skill-route-repair`
- Operative file: `bridge/gtkb-wi4933-cursor-bridge-skill-route-repair-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

## Target Path Scope

All declared paths are in-root under `E:\GT-KB`:

- `scripts/cursor_harness.py` — `_SKILL_ROUTE_ALIASES` and `_skill_system_prompt` resolution.
- `platform_tests/scripts/test_cursor_harness.py` — WI-4872 alias tests must be updated to assert `gtkb-bridge` / bridge-protocol contract, not `proposal-review`.

Scope excludes dispatcher runtime, OpenRouter/Ollama harnesses, health classification, and harness-registry changes.

## Findings

No blocking findings. Two implementation notes:

1. **Alias target directory name:** Skill directory is `bridge` (frontmatter name `gtkb-bridge`). Alias value must be `"bridge"` so `_skill_system_prompt` resolves `.cursor/skills/bridge/SKILL.md`.
2. **WI-4872 supersession:** Prior GO `gtkb-wi4872-cursor-harness-lo-skill-route-alias-002` intentionally chose `proposal-review` to stop fail-closed misses. That unblocked dispatch startup but not bridge verdict filing. Implementation report should cite WI-4872 as superseded alias target for `bridge-review` only.

## Required Conditions

1. `_SKILL_ROUTE_ALIASES["bridge-review"]` must resolve to `"bridge"` (not `proposal-review`, not `gtkb-bridge` as a path segment).
2. `verification` → `verify` alias unchanged; unknown routes still raise `CursorHarnessError`.
3. Update `test_skill_route_alias_bridge_review_resolves` (and any related assertions) to require bridge-protocol / `gtkb-bridge` content, not `proposal-review`.
4. Preserve WI-4881 fail-closed zero-stdout guard for `LOYAL_OPPOSITION_BRIDGE_SKILLS`; add or update focused test if alias change affects prompt assembly.
5. Do not expand scope to backpressure-health, OpenRouter 429 handling, or `scripts/dispatcher_runtime.py` under this GO.

## Spec-derived Verification Expectations

| Spec | Expectation at VERIFIED |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Focused Cursor harness tests prove `bridge-review` prompt embeds the bridge protocol contract (`gtkb-bridge`) required for GO/NO-GO/VERIFIED filing. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Tests preserve fail-closed behavior when bridge skills produce no stdout. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Role-correct numbered bridge filing for implementation report and verification stages. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report maps updated tests to the above specs with executed command evidence. |

## Prior Deliberations

- `DELIB-20266507` — Authorize WI-4933 dispatcher backpressure health classification repair (program authorization cited by `-001`).
- `DELIB-20266209` — Owner AUQ authorizing WI-4872 cursor_harness alias fix (superseded alias target for `bridge-review`).
- `bridge/gtkb-wi4872-cursor-harness-lo-skill-route-alias-002.md` — prior GO establishing `proposal-review` alias; this thread corrects that target.
- `bridge/gtkb-wi4881-headless-cursor-lo-dispatch-verdicts-004.md` — VERIFIED zero-stdout fail-closed guard for bridge skills (must not regress).

## Verdict

**GO.** Proceed with implementation per `-001` **Proposed Scope**, subject to Required Conditions above.
