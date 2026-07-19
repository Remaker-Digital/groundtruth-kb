REVISED
::init gtkb lo
::open build

# WI-5446: Switch Ollama/D headless reviewer model to DeepSeek V4 Flash cloud route

bridge_kind: prime_proposal
Document: gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch
Version: 003
Responds to: bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-002.md
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-17 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2d31ebb3-7f0c-4987-94a1-d56cd7a388ed
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-DIRECT-CLOUD-HARNESS-WI5446-DEEPSEEK-FLASH-20260717
Project: PROJECT-GTKB-OLLAMA-DIRECT-CLOUD-HARNESS
Work Item: WI-5446

target_paths: [".api-harness/routing.toml", "config/dispatcher/rules.toml", "platform_tests/scripts/test_verify_ollama_dispatch.py", "groundtruth-kb/tests/test_doctor_ollama.py"]

implementation_scope: config
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Response to NO-GO (-002)

The `-002` NO-GO (author A, loyal-opposition, independent session context) was
correct: `-001` declared a mutation surface exceeding the cited PAUTH's
`allowed_mutation_classes: [config, source, test]`. Specifically, `-001` listed
`harness-state/harness-registry.json` (operation-time class `runtime_state`) and
`groundtruth.db` (`metadata`) as `target_paths` and set `kb_mutation_in_scope:
true`, none of which that PAUTH grants.

This REVISED adopts the reviewer's **Path 2 (narrow the declared scope)**, which
is the honest and correct disposition because the registry and dispatcher-label
changes occur ONLY through governed CLIs that are exempt from the
implementation-start gate and produce no direct edits to those paths:

- D's headless argv `--model` repoint is applied via `gt harness
  set-invocation-surface` (governed harness-writer transaction) — the same
  governed path used for this session's B -> Sonnet-5 argv swap. It is not a
  direct edit of `harness-state/harness-registry.json`.
- D's dispatcher model label is applied via `gt bridge dispatch config set-model`
  (governed dispatcher-control transaction), which writes the declared
  `config`-class target `config/dispatcher/rules.toml`.
- No direct `groundtruth.db` edit occurs; any MemBase effect is append-only
  through governed CLIs, not a declared target edit.

Accordingly:
- `target_paths` is reduced to the files edited directly: `.api-harness/routing.toml`
  and `config/dispatcher/rules.toml` (`config`) plus
  `platform_tests/scripts/test_verify_ollama_dispatch.py` and
  `groundtruth-kb/tests/test_doctor_ollama.py` (`test`) — all within the current
  PAUTH's `{config, test}` families. `harness-state/harness-registry.json` and
  `groundtruth.db` are removed.
- `kb_mutation_in_scope` is set to `false`.
- The stray `### Helper-suggested candidates` placeholder flagged [P3] is removed
  from `## Prior Deliberations`.

No PAUTH amendment is required. The model choice, motivation, and owner
authorization (`DELIB-202666767`) are unchanged and were verified positive by the
reviewer. The commit-type recommendation (`chore`) is retained per the reviewer's
non-blocking note.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.api-harness/routing.toml`,
`config/dispatcher/rules.toml`, `platform_tests/scripts/test_verify_ollama_dispatch.py`,
and `groundtruth-kb/tests/test_doctor_ollama.py`. No `applications/`, Agent Red,
or out-of-root path is created, read as a live dependency, updated, verified, or
required by this change, per `.claude/rules/project-root-boundary.md` and
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Summary

Switch the Ollama harness (identity D) headless reviewer model from the current
kimi route (`kimi-k2-7-code-cloud` -> `kimi-k2.7-code:cloud`) to a new DeepSeek V4
Flash cloud route (`deepseek-v4-flash-cloud` -> `deepseek-v4-flash:cloud`,
provider `ollama`). This is a bounded model-selection change of the same class as
the completed `WI-5047` kimi switch: add the route entry to
`.api-harness/routing.toml`, repoint the `[routing.ollama]` default and skill
routes, repoint D's registry headless argv `--model` (via governed CLI), update
the dispatcher model label for D (via governed CLI), and adjust focused
route-identity tests. No other harness, credential, eligibility, account, or
provider is touched.

Motivation is defect `WI-5446`: on D's first post-re-enable dispatch this session
(2026-07-17 `...loyal-opposition-D-92bf29`), D authored a VERIFIED verdict body
that the governance guard hard-blocked for missing Specification Links /
spec-to-test mapping / executed-test evidence
(`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`); publisher recovery exhausted
4 attempts and the run ended in `no_progress_loop` with no verdict. D's 2026-07-15
window corroborates (~17% verdict success on complex threads). Same-hour
counter-evidence isolates the cause to the kimi model specifically: harness C
(also a low-cost cloud reviewer) produced 3/3 clean verdicts including a compliant
VERIFIED on `gtkb-wi5248` — the exact verdict class D failed. DeepSeek V4 Flash
is a strong reasoning model (MoE, ~13b activated) at low per-token cost, chosen
from the live Ollama cloud catalog against the owner criteria "strong reviewer,
still relatively inexpensive" to raise D's structured-verdict-authoring quality
while preserving the Ollama subscription budget.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires role-correct bridge filing and independent review of this route change.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires concrete specification links in this proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the project authorization, project, work item, and target-path metadata carried above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires spec-derived verification evidence before terminal VERIFIED of the implementation report.
- `GOV-STANDING-BACKLOG-001` — `WI-5446` is the backlog authority for this change.
- `ADR-CROSS-HARNESS-PARITY-001` — harness behavior and owner-visible model identity must remain truthful and consistent across dispatch surfaces after the swap.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — governs centralized headless bridge dispatch and selected-target behavior for D.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` — dispatcher state/config for D must be inspected and changed through governed control/status surfaces.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — requires the bounded PAUTH cited above before implementation.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — D must retain the capability floor (full tool set, fail-closed guards) after the model swap.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — keeps this platform harness configuration out of adopter application scope.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — captures the model-selection decision and supersession as durable linked artifacts rather than transient chat.

## Prior Deliberations

- `DELIB-202666767` — the owner decision authorizing this swap to DeepSeek V4 Flash via the governed bridge path (the trigger for this proposal).
- `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` — the prior owner decision that switched D to the current kimi route; superseded by `DELIB-202666767` for future D dispatch, retained as historical context.
- `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD` — the earlier owner decision that pinned D to DeepSeek V4 Pro; historical. This proposal returns D to the DeepSeek family but at the cheaper flash tier, not pro.
- `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-001.md` (GO `DELIB-202665813`) — the immediate precedent: the same class of D route switch (kimi), whose target_paths, verification plan, and rollback this proposal mirrors. Its PAUTH granted the broader `generated_projection` / `membase_record` / `governance_evidence` classes; this REVISED instead narrows scope (Path 2) rather than amending the PAUTH.
- `WI-5446` — the tracked defect (D/kimi non-compliant verdict bodies) this swap remediates; carries the same-hour C-VERIFIED counter-evidence isolating the cause to the kimi model.

## Owner Decisions / Input

- `DELIB-202666767` — owner decision (AskUserQuestion-backed) to swap D's reviewer model to DeepSeek V4 Flash via the governed bridge path.
  - AUQ `AUQ-D-MODEL-CHOICE-2026-07-17`: owner directed choosing a strong-yet-inexpensive Ollama cloud model.
  - AUQ `AUQ-D-MODEL-DEPLOY-2026-07-17`: owner selected "deepseek-v4-flash via bridge".
- `PAUTH-PROJECT-GTKB-OLLAMA-DIRECT-CLOUD-HARNESS-WI5446-DEEPSEEK-FLASH-20260717` — active bounded authorization for `WI-5446` covering config/source/test mutation classes. This REVISED's declared target_paths are all within `{config, test}`.

## Requirement Sufficiency

Existing requirements sufficient. The owner decision `DELIB-202666767`, the
active PAUTH, `WI-5446`, and the cited governing specs
(`ADR-CROSS-HARNESS-PARITY-001`, `GOV-HARNESS-ONBOARDING-CONTRACT-001`,
`SPEC-CENTRALIZED-DISPATCH-SERVICE-001`) fully bound the change. No new or revised
requirement is needed; this is a model-selection change within an existing,
verified harness integration.

## Spec-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `ADR-CROSS-HARNESS-PARITY-001` | Assert D headless argv, `scripts.ollama_harness` route resolver output, and dispatcher status all name `deepseek-v4-flash-cloud` / `deepseek-v4-flash:cloud` consistently, with provider `ollama` and the full bridge tool set: `groundtruth-kb/.venv/Scripts/python.exe scripts/verify_ollama_dispatch.py --readiness-only --json` (expect `ready: true`, `model_id=deepseek-v4-flash:cloud`, `missing_tools: []`). |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` / `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `gt bridge dispatch config --json` and `gt bridge dispatch status --json` report D model label `deepseek-v4-flash-cloud` with no topology drift (D remains loyal-opposition, dispatchable state unchanged by this proposal). |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/verify_ollama_dispatch.py` (full live mode) passes its guard-pipeline checks (destructive Bash, formal-artifact, out-of-root, bridge-mutation all denied) on the new route. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verify_ollama_dispatch.py groundtruth-kb/tests/test_doctor_ollama.py -q --no-header` passes with route-identity assertions updated to the DeepSeek V4 Flash route. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start authorization is acquired for `WI-5446` from this proposal's GO; direct edits stay within the listed `target_paths` (all `{config, test}`); registry/dispatcher changes use governed CLIs exempt from the implementation-start gate. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Applicability and clause preflights pass on this proposal and on the implementation report; GO + work-intent claim cited. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm no `applications/` or Agent Red files change. |

## Proposed Scope

1. Add `[models.deepseek-v4-flash-cloud]` to `.api-harness/routing.toml`:
   `model_id = "deepseek-v4-flash:cloud"`, `provider = "ollama"`,
   `tool_calling_supported = true`, full `allowed_tools` set
   (Read/Write/Edit/Grep/Glob/Bash), matching the existing ollama cloud entries.
2. Repoint `[routing.ollama].default_model` and the `[routing.ollama.skills]`
   `bridge-review` / `verification` / `implementation` routes to
   `deepseek-v4-flash-cloud`.
3. Repoint D's registry headless argv `--model` from `kimi-k2-7-code-cloud` to
   `deepseek-v4-flash-cloud` via the governed `gt harness set-invocation-surface`
   transaction (NOT a direct edit of `harness-state/harness-registry.json`; that
   path is therefore not a declared target), preserving role, lifecycle status,
   reviewer precedence, dispatch eligibility, prompt transport, `--skill
   bridge-review`, and `max_items`.
4. Update the dispatcher model label for D to `deepseek-v4-flash-cloud` via the
   governed `gt bridge dispatch config set-model` transaction (which writes the
   declared `config`-class target `config/dispatcher/rules.toml`).
5. Update focused route-identity tests/fixtures to expect the DeepSeek V4 Flash
   route while still guarding against provider/route confusion.
6. Do not remove the `kimi-k2-7-code-cloud` or `deepseek-v4-pro-cloud` route
   definitions; this proposal only changes D's active route selection.

## Out Of Scope

- Credential lifecycle, key rotation, Ollama account settings, external provider
  access/purchase, or production deployment.
- Any change to another harness's model, eligibility, role, or precedence
  (E/H remain budget-disabled; B/C unchanged).
- Deletion of historical route/deliberation/bridge evidence.
- Any `applications/` or Agent Red file.

## Risk / Rollback

Risk is moderate: the change mutates live harness routing and owner-visible
dispatcher metadata. The principal risk is provider/route confusion — the Ollama
cloud route `deepseek-v4-flash:cloud` must not be conflated with the OpenRouter
`deepseek-v4-flash` entry (provider `openrouter`), which remains untouched. A
secondary risk is that DeepSeek V4 Flash does not resolve on the Ollama cloud
endpoint; the readiness probe in the verification plan catches this before the
report is filed.

Rollback is a single-commit revert restoring D's active route selection, headless
argv, and dispatcher label to `kimi-k2-7-code-cloud` / `kimi-k2.7-code:cloud`
through the same governed config and harness-writer paths. Bridge files,
deliberations, work items, and PAUTH records are append-only audit artifacts and
must not be deleted by rollback.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`chore` — a config-only route-selection change (routing.toml entry + governed
registry-argv/dispatcher-label transactions + focused test fixtures), no new
capability surface and no source-behavior change, consistent with the `WI-5047`
route-switch precedent.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
