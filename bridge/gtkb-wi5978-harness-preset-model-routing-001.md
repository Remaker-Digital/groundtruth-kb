NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 3ae0d151-b62c-4e1d-a0e6-486f3a0fbb8b
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder

bridge_kind: prime_proposal
Document: gtkb-wi5978-harness-preset-model-routing
Version: 001
Date: 2026-08-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE-AUTHORIZE-WI-5978-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5978

target_paths: [".api-harness/routing.toml", "harness-state/harness-registry.json", "platform_tests/scripts/test_api_harness_preset_routing.py"]
implementation_scope: route_goose_and_openrouter_to_owner_designated_gtkb_presets
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

**No KB mutation.** No MemBase write; `groundtruth.db` unchanged.
**No approval-evidence work.** No formal-artifact-approval packet created.
**No activation.** No harness is activated, resumed, or made dispatchable; the
legacy TAFE dispatcher stays disabled and its scheduled task is untouched.

# WI-5978 - Route Goose (G) and OpenRouter (F) to their owner-designated GT-KB presets

## Summary

Per owner directive, the Goose and OpenRouter harnesses are to run on
owner-created GT-KB model presets. This proposal repoints both model routes.

Each harness gets its **own** preset, not a shared one. The owner originally
named a single preset for both; review of the live preset showed its system
prompt is Goose-specific and actively contradicts the OpenRouter shim, and the
owner then created dedicated OpenRouter presets. Both presets pin the same
model (DeepSeek V4 Flash 0731) and identical provider preferences and
parameters, so this is one model outcome delivered through two harness-correct
prompts.

| Harness | Preset identifier | Preset title |
|---|---|---|
| G goose | `@preset/gtkb-v4f` | GroundTruth-KnowledgeBase-V4F |
| F openrouter | `@preset/gtkb-openrouter-deepseek-v4-flash` | GT-KB OpenRouter DeepSeek V4 Flash 0731 |

## Live Anchor Evidence (owner-supplied preset pages, verified 2026-08-07)

Both presets are workspace `default`, status **Active**, model **DeepSeek:
DeepSeek V4 Flash 0731**, provider Custom, with identical provider preferences
(`{"sort": {"by": "price", "partition": null}, "allow_fallbacks": true}`) and
identical parameters (`{"top_p": 0.95, "reasoning": {"enabled": true,
"max_tokens": 1048576}, "temperature": 1}`). Neither configures OpenRouter
server-side tools, which is correct: GT-KB supplies tool schemas client-side in
the request payload.

- **G** - `@preset/gtkb-v4f`, system prompt headed "GT-KB Worker - Goose Desktop
  Harness G", asserting "Harness identity: G (Goose desktop)".
- **F** - `@preset/gtkb-openrouter-deepseek-v4-flash`, system prompt headed
  "GT-KB Worker - OpenRouter Harness F", asserting "Harness identity: F
  (OpenRouter). You are running through `scripts/openrouter_harness.py`."

### Workspace preset list (owner-supplied, verified 2026-08-07)

The owner's OpenRouter workspace lists exactly **4 presets, all Active**:

| Preset | Identifier | Version | Used by this proposal |
|---|---|---|---|
| GT-KB OpenRouter DeepSeek V4 Flash 0731 | `@preset/gtkb-...-flash` | v1 | **yes** - harness F |
| GroundTruth-KnowledgeBase-V4F | `@preset/gtkb-v4f` | v2 | **yes** - harness G |
| GroundTruth-KnowledgeBase-K3 (Moonshot AI Kimi K3) | `@preset/gtkb-k3` | v4 | no |
| GroundTruth-KnowledgeBase-PRO (Opus 4.8-level coding) | `@preset/gtkb-pro` | v10 | no |

Two facts follow. First, both identifiers this proposal writes are present and
Active, so neither route points at a non-existent preset. Second, the earlier
sibling `@preset/gt-kb-openrouter-harness-deepdeek-v4-flash` is **absent from
the list** - the owner deleted it rather than merely superseding it. Acceptance
criterion 7 (that identifier appears nowhere in the change) therefore guards
against writing a route to a preset that no longer exists.

`@preset/gtkb-k3` and `@preset/gtkb-pro` exist but are **not** referenced by
this proposal; no route is added for them. They are noted only so the reviewer
knows the preset family is larger than the two routes changed here.

### The drift this resolves

`.api-harness/routing.toml` declares Goose's model as `deepseek-v4-pro`
(`[models.goose-deepseek-v4-pro]`). But every bridge verdict Goose authored on
2026-08-06/07 reports `author_model: DeepSeek V4 Flash 0731` /
`model_version: deepseek-v4-flash-0731` - see
`bridge/gtkb-wi5933-slice-b-resolver-fail-closed-008.md` and
`bridge/gtkb-inactive-harness-requirement-deferral-002.md`.

Both presets pin DeepSeek V4 Flash 0731, matching what Goose actually reports.
**The config was stale, not the harness.** This change makes the configuration
state what is already true, which is why it is a `fix:`.

WI-5628 in this same project ("Reconcile harness D to the canonical DeepSeek V4
Flash review route") is the identical defect on another harness, so routing
drift is systemic rather than isolated.

### Current routing (to be repointed)

- `[routing.goose]` `default_model = "goose-deepseek-v4-pro"`; `[routing.goose.skills]`
  maps `bridge-review`, `verification`, `implementation` all to that key.
  `[models.goose-deepseek-v4-pro]` sets no `omit_payload_model`, so it defaults
  `False` (`scripts/cloud_harness_base.py:274`) and the model IS sent.
- `[routing.openrouter]` `default_model = "openrouter-cloud-default"`; same three
  skill routes. `[models.openrouter-cloud-default]` sets
  **`omit_payload_model = true`** - see the trap below.
- Harness registry `headless` argv carries the routing KEY, not the model_id:
  G -> `scripts/goose_harness.py -p {{PROMPT}} --skill bridge-review --model goose-deepseek-v4-pro`;
  F -> `scripts/openrouter_harness.py -p {{PROMPT}} --model openrouter-cloud-default --skill bridge-review --max-turns 200 --timeout 60 --session-timeout 5400`.

## The `omit_payload_model` Trap (primary technical risk)

`scripts/cloud_harness_base.py:1009-1018`:

```python
payload: dict[str, Any] = {"messages": messages, "stream": False}
if not model_route.omit_payload_model:
    payload["model"] = model_route.model_id
```

`[models.openrouter-cloud-default]` currently sets `omit_payload_model = true`,
so `payload["model"]` is **never sent**. OpenRouter preset selection works
precisely by sending the preset identifier as the model field.

An OpenRouter preset entry that inherits that flag would be **silently inert**:
the config would read correctly, tooling would report the preset as configured,
and the harness would quietly run whatever the key or endpoint implies. The
failure would be invisible at every surface an operator inspects.

The new OpenRouter entry therefore sets `omit_payload_model = false`
explicitly, and C4 pins that with a dedicated regression assertion. Goose is
unaffected (its entry omits the flag), and the new Goose entry likewise omits
it.

## Proposed Change

### C1 - add two preset model routes

```toml
[models.gtkb-v4f-goose]
model_id = "@preset/gtkb-v4f"
provider = "goose"
tool_calling_supported = true
allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]

[models.gtkb-v4f-openrouter]
model_id = "@preset/gtkb-openrouter-deepseek-v4-flash"
provider = "openrouter"
tool_calling_supported = true
allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
omit_payload_model = false
```

Two entries because the schema binds `provider` per model entry, and because the
two harnesses now use different preset identifiers. `allowed_tools` is carried
forward byte-identically from each harness's current entry, so tool parity is
unchanged by this proposal.

### C2 - repoint both providers' routing

`[routing.goose]` `default_model` and all three `[routing.goose.skills]` routes
-> `gtkb-v4f-goose`. `[routing.openrouter]` and its three skill routes ->
`gtkb-v4f-openrouter`.

### C3 - repoint both headless argv values

Through the governed harness registry CLI, never a raw registry edit. Only the
`--model` element changes; every other argv element is preserved
byte-identically. This honors
`DELIB-20260702-DISPATCH-SELECTED-MODEL-ROUTE-LAUNCH-OVERRIDE` (the selected
model route must be passed at launch and honored by the harness).

### C4 - new test module

`platform_tests/scripts/test_api_harness_preset_routing.py` asserting:

1. Goose's `default_model` and all three skill routes resolve to a model entry
   whose `model_id` is `@preset/gtkb-v4f`.
2. OpenRouter's `default_model` and all three skill routes resolve to a model
   entry whose `model_id` is `@preset/gtkb-openrouter-deepseek-v4-flash`.
3. **Inertness guard:** no `openrouter`-provider model entry whose `model_id`
   begins with `@preset/` sets `omit_payload_model = true`.
4. Both headless argv values name the preset routing keys, and every non-model
   argv element is unchanged.
5. `allowed_tools` per harness is unchanged.

### Out of scope

`[models.goose-deepseek-v4-pro]` and `[models.openrouter-cloud-default]` are
left defined but unreferenced (Open Question 1). The suspended D and H routes,
harness activation, and dispatcher enablement are untouched.

## Open Questions For The Reviewer

1. **Unreferenced legacy routes and the lane matrix.**
   `DELIB-20260702-DISPATCH-LANE-MATRIX-MODEL-ROUTE-POPULATION` records that the
   lane matrix includes **all configured non-retired model routes per harness**.
   The routing schema has no `retired` or `enabled` flag (grep-verified), so
   leaving the two superseded entries defined may keep them selectable even
   though nothing references them. This proposal keeps them because rollback is
   then a repoint rather than a re-creation. If the reviewer reads that
   deliberation as requiring removal, that is a two-entry deletion and this
   should be NO-GO'd for a REVISED that deletes them.
2. **Preset resolution is asserted, not verified.** That each harness resolves
   its preset identifier is owner-supplied fact; it depends on provider
   configuration not inspectable from inside GT-KB. The verification plan probes
   it at runtime rather than assuming it. The drift evidence is strong
   corroboration for Goose (it already reports the preset's model) but is not
   proof of identifier resolution, and there is no equivalent corroboration for
   OpenRouter.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority for this thread.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - discharged by the PAUTH
  binding above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - discharged here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification plan maps each
  acceptance criterion to a test.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - WI-5978 bound to
  PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE.
- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` - the `.api-harness/routing.toml` schema
  contract this change conforms to.
- `GOV-HARNESS-ROLE-PORTABILITY-001` and `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`
  - harness capability configuration.
- `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` -
  cross-harness disposition below.
- `DCL-SESSION-ROLE-RESOLUTION-001` - role resolution; cited for Follow-On 2.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all targets in-root.
- `.claude/rules/project-root-boundary.md` - in-root containment.

## Prior Deliberations

Search executed 2026-08-07:
`gt deliberations search "harness model routing preset dispatch availability openrouter goose" --limit 6`.

- `DELIB-20260702-DISPATCH-SELECTED-MODEL-ROUTE-LAUNCH-OVERRIDE` - the selected
  model route must be passed at launch and honored. C3 keeps the route in the
  launch argv, satisfying this directly.
- `DELIB-20260702-DISPATCH-LANE-MATRIX-MODEL-ROUTE-POPULATION` - lane matrix
  includes all configured non-retired routes; raised as Open Question 1.
- `DELIB-S422-OR-REGISTRY-INTEGRATION` - OpenRouter registered as a single
  harness `openrouter` (ID F). This proposal changes its model route only, not
  its registry identity.
- `DELIB-202668161` - owner AUQ 2026-08-01: full manual PB+LO harness parity,
  Goose promoted to first-class peer. Consistent with the owner driving Goose
  and Claude Code manually.
- `DELIB-202667096` / `DELIB-202667098` - Goose FSM Phase 1 GO and the Goose
  activation/role-parity NO-GO; boundary evidence that harness activation is
  governed separately from model routing. This proposal activates nothing.
- `DELIB-20260806011900` - the owner decision recorded for this work item (see
  below).

## Owner Decisions / Input

- **Owner directive 2026-08-07 (verbatim, stated twice):** "the Goose harness
  should be/is using the model `@preset/gtkb-v4f`. This is a preset we have
  created specifically for GT-KB. This is also the model preset that the
  OpenRouter harness should be using. Both Goose and OpenRouter will be
  available for dispatch once this model change is made." Scoped by the owner to
  Dispatcher Next only.
- **Owner AUQ 2026-08-07 (preset vs harness F):** presented with evidence that
  `@preset/gtkb-v4f`'s system prompt asserts harness G, forbids claiming harness
  F and the OpenRouter shim, and forbids reading `harness-registry.json` for
  role - all contradicted by the shim's own prompt - the owner selected
  **"Second preset for OpenRouter"** rather than sharing one preset.
- **Owner supplied two OpenRouter presets 2026-08-07**, then **AUQ 2026-08-07
  (F preset selection):** the owner selected
  **`@preset/gtkb-openrouter-deepseek-v4-flash`** as canonical. The sibling
  `@preset/gt-kb-openrouter-harness-deepdeek-v4-flash` (whose identifier
  contained a `deepdeek` misspelling) has since been **deleted** by the owner -
  it is absent from the workspace preset list supplied 2026-08-07 - so it is not
  merely superseded but no longer resolvable, and is not referenced here.
- **Owner supplied the workspace preset list 2026-08-07**, confirming both
  identifiers written by this proposal are present and Active.
- **`DELIB-20260806011900`** - the recorded owner-decision deliberation from
  `AUQ-20260807-GTKB-V4F-PRESET-ROUTING`, which authorized WI-5978 into
  implementation scope under the PAUTH cited above (allows `configuration`,
  `runtime_state`, `test`; forbids `credential_lifecycle`,
  `production_deployment`, `release`, `git_push`). Full decision body at
  `.gtkb-state/owner-decisions/AUQ-20260807-GTKB-V4F-PRESET-ROUTING.md`.
- **Owner directive 2026-08-07:** "I am driving Goose and Claude Code manually
  until Dispatcher Next is ready for testing." Configuration only; no activation
  requested.
- **Owner directive 2026-08-07:** "The legacy TAFE/dispatcher should remain
  disabled." No dispatcher enablement is proposed; the disabled
  `GTKB-DispatcherDaemon` scheduled task is untouched.
- No new owner decision is requested by this proposal.

## Requirement Sufficiency

**Existing requirements sufficient.** The owner directives and the two AUQ
decisions above, plus the two 2026-07-02 dispatch-routing deliberations, define
the required outcome. No new or revised requirement is implied and none is
proposed.

## Specification-Derived Verification Plan

| Requirement | Test / command | Required observed behavior |
|---|---|---|
| C1/C2 Goose routing | new module, goose case | Goose `default_model` and all three skill routes resolve to `model_id == "@preset/gtkb-v4f"`. |
| C1/C2 OpenRouter routing | new module, openrouter case | OpenRouter `default_model` and all three skill routes resolve to `model_id == "@preset/gtkb-openrouter-deepseek-v4-flash"`. |
| **Inertness guard** | new module, `omit_payload_model` case | No `openrouter`-provider entry with a `@preset/` `model_id` sets `omit_payload_model = true`, so `_openai_build_payload` sends `payload["model"]`. |
| C3 argv | new module, argv case | Both headless argv values carry the preset routing keys; all other argv elements byte-identical to pre-change. |
| Tool parity unchanged | new module, `allowed_tools` case | Both harnesses' `allowed_tools` match the pre-change sets. |
| Superseded preset unreferenced | new module, negative case | The string `gt-kb-openrouter-harness-deepdeek-v4-flash` appears nowhere in `.api-harness/routing.toml` or the registry argv. |
| Schema still valid | `gt project doctor` routing checks | No new `.api-harness/routing.toml` warnings. |
| Presets actually resolve (Open Q2) | runtime probe of each harness on its preset route | Each harness starts and reports a model consistent with DeepSeek V4 Flash 0731; any WI-5897-class local-tag readiness failure is surfaced explicitly rather than as a bare not-ready. |
| Code quality (both gates) | `ruff check` and `ruff format --check` on the new test module | Both pass; separate gates. |

## Acceptance Criteria

1. Only the three declared `target_paths` change.
2. Goose resolves to `@preset/gtkb-v4f` on `default_model` and all three skill
   routes.
3. OpenRouter resolves to `@preset/gtkb-openrouter-deepseek-v4-flash` on
   `default_model` and all three skill routes.
4. The OpenRouter preset entry does **not** set `omit_payload_model = true`.
5. Both headless argv values are updated through the governed harness registry
   CLI, never a raw registry edit, and differ from their pre-change values only
   in the `--model` element.
6. `allowed_tools` is unchanged for both harnesses.
7. The superseded `deepdeek` preset identifier appears nowhere in the change.
8. The new test module passes; no other test module regresses.
9. Both ruff gates pass on the new test module.
10. No harness is activated, resumed, or made dispatchable; the legacy
    dispatcher stays disabled and its scheduled task is untouched.
11. No KB row, TAFE/dispatcher state, formal artifact, credential, deployment, or
    external system is mutated; no commit is created by Prime Builder.

## Risk and Rollback

- **Highest risk: silent inertness** on the OpenRouter path via
  `omit_payload_model`, addressed by C1 and acceptance criterion 4 and pinned by
  a dedicated test.
- **Risk: preset unresolvable by a harness.** With the model sent, an
  unresolvable preset fails at launch rather than degrading silently - which is
  exactly what the inertness guard preserves.
- **Risk: lane-matrix retention of legacy routes** - Open Question 1.
- **Risk: readiness probe rejects preset identifiers.** WI-5897 (open, same
  project) reports not-ready for on-demand cloud models by asserting local tag
  membership; a `@preset/...` identifier is not a local tag, so dispatch
  availability may remain blocked after this lands. WI-5978 records WI-5897 as a
  dependency; this proposal does not claim to deliver dispatch-availability by
  itself.
- **Rollback:** revert `routing.toml` and re-run the two invocation-surface
  updates with the previous argv. No data migration, no schema change; the
  superseded entries remain present precisely so rollback is a repoint rather
  than a re-creation.

## Follow-On (not in this scope)

1. **Residual Goose reference in both OpenRouter presets.** Both F presets
   retain the line "3. The Goose-level system prompt, which owns tool mechanics"
   from the Goose template. For harness F this should reference the OpenRouter
   shim. Cosmetic but confusing to an F worker reasoning about its own
   precedence order. Owner-side preset edit; not a GT-KB change.
2. **Role-source contradiction between preset and shim.** Both F presets say
   "Never read dispatcher or TAFE configuration (... `harness-state/harness-registry.json`)
   to infer your role", while the shim's own prompt
   (`scripts/openrouter_harness.py:261`) instructs the model to use
   `harness-state/harness-registry.json` through the canonical role reader as
   the role source. Per `DCL-SESSION-ROLE-RESOLUTION-001` a dispatched worker
   receives `::init gtkb <role>` and the init keyword is authoritative, which
   suggests the **preset** is correct and the shim line is stale. Narrower than
   the identity conflict the owner already resolved, but it should be reconciled
   in one direction rather than left contradictory.
3. **WI-5897 readiness probe** must accept preset identifiers before either
   harness can be called dispatch-available.
4. **Routing-vs-reality drift class.** WI-5628 (harness D) and the Goose drift
   documented here are the same defect. A check comparing each harness's
   configured `model_id` against the model its artifacts actually report would
   catch the class rather than its instances.

## Cross-Harness Disposition

Per `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`:

- **G goose** and **F openrouter**: both move onto owner-designated presets
  pinning the same model with identical provider preferences and parameters.
  Different preset identifiers are **required** parity, not divergence: each
  preset's system prompt asserts its own harness identity, and sharing one would
  give a worker a false identity (the conflict the owner resolved by AUQ).
- **A codex / B claude / C antigravity / E cursor**: unaffected; they do not use
  `.api-harness/routing.toml` model routes.
- **D ollama / H alibaba-cloud-studio**: suspended per owner directive
  2026-08-07; their routing entries are untouched.
- No harness-surface hook or skill files in `target_paths`; no projections to
  regenerate; no typed waiver requested.

## Bridge Chain Discipline

This artifact is filed as
`bridge/gtkb-wi5978-harness-preset-model-routing-001.md`, the first numbered
file of a new thread, written through the governed bridge writer. The numbered
bridge files under `bridge/` are canonical and append-only: this proposal
deletes no bridge file and rewrites no prior version. Threads cited as evidence
(`bridge/gtkb-wi5933-slice-b-resolver-fail-closed-008.md`,
`bridge/gtkb-inactive-harness-requirement-deferral-002.md`) are read-only
citations.

## Root Boundary Compliance

All artifacts are in-root under `E:/GT-KB`. All three declared targets are
in-root platform paths and this bridge file resides under `E:/GT-KB/bridge/`. No
`applications/` path is touched.

## Recommended Commit Type

`fix:` - the Goose routing config declares a model the harness is not running,
and the OpenRouter route does not send its model at all. This makes both
configurations state what the owner designated. No new capability surface is
added.

## DISARM - Implementation

This file requests review only. It grants no protected-edit, claim, start,
finalization, or cleanup authority. Implementation requires a Loyal Opposition
`GO`, a fresh work-intent claim, and an implementation-start authorization
packet created from that `GO`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
