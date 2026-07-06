NEW

# gtkb-wi5050-openrouter-author-model-provenance-actual-model — Stamp OpenRouter author-model provenance from the actual served model, not the static routing id

bridge_kind: prime_proposal
Document: gtkb-wi5050-openrouter-author-model-provenance-actual-model
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-06 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 66422d1e-3091-47fa-a848-f5468485ec45
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5050

target_paths: ["scripts/openrouter_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`scripts/openrouter_harness.py` `set_author_metadata_env` stamps
`GTKB_AUTHOR_MODEL` (and `_VERSION`, `_CONFIGURATION`) from the **static routing
`model_id`** (`deepseek/deepseek-v4-pro`) resolved from `.api-harness/routing.toml`,
and even labels `GTKB_AUTHOR_MODEL_CONFIGURATION` `routing=static`. But OpenRouter
overrides the invoker-specified model with **Kimi K2.7 Code** at the account/proxy
layer (owner-confirmed 2026-07-06). Every bridge/document artifact authored by the
OpenRouter (F) harness therefore records a **false author model**, which violates
`GOV-DOCUMENT-AUTHOR-PROVENANCE-001` (author-provenance accuracy). This was
surfaced as the non-blocking provenance caveat in the WI-5048 OpenRouter/F
PB-activation proposal; the owner directed that it be corrected.

**Fix.** The `/chat/completions` response JSON already exposes the served model in
its top-level `"model"` field (the response object is available in
`run_tool_loop`, e.g. alongside `response.get("choices")`). Capture
`response["model"]` from the first completion response and thread it into the
`ModelMetadata` / author-metadata path so `set_author_metadata_env` stamps the
**actual** served model (and a `_CONFIGURATION` that records the account-level
override) before any guarded-tool subprocess writes author metadata. The static
routing `model_id` is retained only as the request payload model and as a
fallback when the response omits `model`.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — the Document Artifact Author Provenance
  Contract that this defect violates and this fix restores: author metadata must
  reflect the actual authoring model.
- `GOV-RELIABILITY-FAST-LANE-001` — small correctness defect fix eligible for the
  reliability fast-lane; filed under the project's standing authorization.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — author metadata is part of the bridge
  audit-trail record produced by the harness.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — proposal carries
  Project + Work Item + Project Authorization linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan
  derives checks from the linked provenance spec.
- `GOV-STANDING-BACKLOG-001` — WI-5050 is the governing backlog authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — owner directive captured as
  a durable WI + bridge artifact chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — artifact-oriented stance
  for the WI/proposal chain.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — lifecycle trigger for the
  owner-directed defect capture.

## Prior Deliberations

- `DELIB-OPENROUTER-F-PB-ACTIVATION-20260706` — the WI-5048 owner-decision record
  where this provenance divergence was surfaced as a caveat and the owner
  directed its correction. This proposal is that correction.
- `DELIB-20261032` (Document Artifact Author Provenance Gap Advisory) — prior
  advisory on author-provenance gaps; this fix closes one such gap for the
  OpenRouter harness.
- `DELIB-HARNESS-OPS-PROPOSALS-REQUIRE-UNIVERSAL-AUTHOR-METADATA-20260702` —
  owner-confirmed that artifacts must carry accurate author metadata regardless of
  author nature; a false model id defeats that intent.
- `DELIB-20263483` (WI-4522 Author Identity Env Alias Defect) — prior author-metadata
  env defect in the same stamping path; same class of provenance-accuracy repair.
- `PROJECT-HARNESS-EQUIVALENCE-PHASE-3` (model-identity divergence;
  `bridge/harness-equivalence-phase-3-umbrella-001.md`, gap-02 harness-model-config-truth)
  — documents the OpenRouter UI/headless/provenance model-identity divergence this
  fix addresses at the provenance surface.

## Owner Decisions / Input

This fix is directed by the owner and authorized under the reliability fast-lane:

- **Owner directive (this session, 2026-07-06):** on the OpenRouter shim stamping
  `GTKB_AUTHOR_MODEL` from the routing row (`deepseek-v4-pro`) while Kimi actually
  runs — "This is an error that should be corrected."
- **Model-behavior fact (owner-confirmed):** OpenRouter overrides the invoker
  model with Kimi K2.7 Code at the account/proxy layer.
- **Authorization:** `GOV-RELIABILITY-FAST-LANE-001` via
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (covers WI-5050 by active project
  membership; owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`).

No further owner decision is required to review this proposal.

## Requirement Sufficiency

**Existing requirements sufficient.** `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` already
requires author metadata to reflect the actual authoring model. This proposal
brings the OpenRouter harness into compliance with that existing requirement; no
new or revised requirement is needed.

## Spec-Derived Verification Plan

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` → unit test: given a completion response
  whose `"model"` differs from the requested routing id, `set_author_metadata_env`
  (as driven by `run_tool_loop`) stamps `GTKB_AUTHOR_MODEL` = the response model,
  and `GTKB_AUTHOR_MODEL_CONFIGURATION` records the account-level override rather
  than `routing=static`. Add to
  `platform_tests/scripts/test_openrouter_harness.py`; run
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_openrouter_harness.py -q --no-header` → green.
- Fallback behavior → unit test: when the response omits `"model"`, the harness
  falls back to the routing `model_id` (no regression to today's behavior).
- **Empirical confirmation gate (implementation-time):** confirm a live OpenRouter
  `/chat/completions` response's `"model"` field reports the actual served model
  (Kimi) and does not merely echo the requested id. If OpenRouter echoes the
  requested id, the implementation must instead source the effective model from a
  config-declared `effective_model` field (documented in the report) — the unit
  tests above cover both source paths.
- Code quality → `ruff check` and `ruff format --check` on
  `scripts/openrouter_harness.py` → clean.

## Risk / Rollback

- **Low-to-moderate risk.** The change is confined to author-metadata sourcing in
  one harness; it does not alter routing, request payloads, tool dispatch, or the
  guarded-write safety path. The main uncertainty is whether `response["model"]`
  reflects the override (Kimi) or echoes the request (deepseek) — resolved by the
  empirical confirmation gate above, with a config-declared fallback if needed.
- **Provenance-only scope.** Only the OpenRouter harness has the account-override
  divergence; Ollama/Cursor stamp their actually-routed model, so this fix is
  intentionally OpenRouter-scoped.
- **Rollback.** Single revert of the `scripts/openrouter_harness.py` change
  restores the prior (static) stamping; no data/state migration.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5050-openrouter-author-model-provenance-actual-model`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — corrects a false author-model provenance record; no new capability
surface is added.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
