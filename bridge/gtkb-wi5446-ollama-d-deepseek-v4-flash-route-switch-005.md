NEW
::init gtkb lo
::open build

# WI-5446 Implementation Report: Ollama/D switched to DeepSeek V4 Flash cloud route

bridge_kind: prime_proposal
Document: gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch
Version: 005 (post-implementation report; responds to GO -004)
Responds to: bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-004.md
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
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implemented the GO'd (-004) DeepSeek V4 Flash route switch for the Ollama harness
(identity D) under the implementation-start packet acquired from -004
(`packet_hash: sha256:9d5b75351ed82b2bad41400ba25cc06ea3dc68c29d6a1bfa71f3a90d749d0d95`).
D now dispatches on `deepseek-v4-flash-cloud -> deepseek-v4-flash:cloud`
(provider `ollama`) with the full loyal-opposition tool set. All direct edits
stayed inside the declared `{config, test}` target_paths; the registry argv and
dispatcher-label changes were applied only through governed CLIs exempt from the
implementation-start gate, exactly as the GO's Implementation Guidance directed.

The readiness probe initially reported `ready: false` because the new cloud tag
was not yet registered on the local Ollama daemon (`/api/tags` did not list
`deepseek-v4-flash:cloud`). This is the exact pre-file failure class the GO told
me to catch. Registering the tag via the daemon's `/api/pull` (owner directive:
"make Ollama fully functional and dispatchable with DeepSeek V4 Flash, ASAP")
returned `{"status":"success"}` and flipped the probe to `ready: true`. The full
live guard-pipeline then passed 7/7.

## Changes Implemented

1. **`.api-harness/routing.toml`** (`config`, direct edit): added
   `[models.deepseek-v4-flash-cloud]` (`model_id = "deepseek-v4-flash:cloud"`,
   `provider = "ollama"`, `tool_calling_supported = true`, full
   `allowed_tools = [Read, Write, Edit, Grep, Glob, Bash]`) and repointed
   `[routing.ollama].default_model` plus the three `[routing.ollama.skills]`
   routes (`bridge-review` / `verification` / `implementation`) to
   `deepseek-v4-flash-cloud`. The `kimi-k2-7-code-cloud` and
   `deepseek-v4-pro-cloud` route definitions are retained (route selection
   changed, definitions preserved).

2. **D registry headless argv** (governed CLI, NOT a direct edit of
   `harness-state/harness-registry.json`): repointed `--model` from
   `kimi-k2-7-code-cloud` to `deepseek-v4-flash-cloud` via
   `gt harness set-invocation-surface --harness D --surface headless`,
   preserving `--skill bridge-review`, `max_items: 1`, role, lifecycle status,
   dispatch eligibility, and prompt transport.

3. **Dispatcher model label for D** (governed CLI writing the declared
   `config`-class target `config/dispatcher/rules.toml`): set to
   `deepseek-v4-flash-cloud` via `gt bridge dispatch config set-model D`.
   Confirmed at `[budget.harnesses.D] model = "deepseek-v4-flash-cloud"`.

4. **`platform_tests/scripts/test_verify_ollama_dispatch.py`** (`test`, direct
   edit): renamed + rewrote the route-identity test to
   `test_default_ollama_bridge_review_route_uses_deepseek_v4_flash_cloud`. The
   fixture now defines `deepseek-v4-flash-cloud` as the default and skill routes
   while retaining `kimi-k2-7-code-cloud` and both DeepSeek Pro entries as
   non-default models (guarding against provider/route confusion); assertions
   expect `route.key == "deepseek-v4-flash-cloud"` and
   `route.model_id == "deepseek-v4-flash:cloud"`.

5. **Ollama daemon model registration** (enablement; owner-directed ops on the
   local daemon, not a git-tracked artifact): `POST /api/pull` for
   `deepseek-v4-flash:cloud` -> `{"status":"success"}`. This registered the cloud
   tag so D can serve it; it is the step that made the switch functional.

### Declared target that required no edit (disclosed)

`groundtruth-kb/tests/test_doctor_ollama.py` was declared in `target_paths` but
required **no change**. Its `kimi-k2-7-code-cloud` usage is a self-contained
WI-4700 stale-*local*-narrative fixture (writes its own routing.toml to
`tmp_path`) and a `fresh_marker` keyword, not a production-default-route
assertion. The full test file (17 tests) passes unchanged after the switch,
confirming the model swap does not affect the doctor's local-vs-cloud freshness
check. Declaring it was conservative scope; leaving it unedited is the honest
outcome. `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (out of scope)
uses the literal `kimi-k2-7-code-cloud` only as one of several `fresh_marker`
keywords (alongside `cloud-backed`, `current route`, `cloud-routed`), so the
switch does not break it either.

### Narrative currency follow-up (out of scope, captured)

`.claude/rules/canonical-terminology.md` and `.claude/rules/operating-model.md`
still describe D's "current route" as `kimi-k2-7-code-cloud`. Those are protected
narrative artifacts outside this proposal's `target_paths` and require separate
narrative-artifact approval; their WI-4700 doctor check remains green (they retain
generic cloud-fresh markers). Captured as a backlog follow-up rather than silently
expanded into this scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — role-correct bridge filing and independent verification of this route change.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete specification links carried forward.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project authorization / project / work item / target-path metadata carried above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived verification evidence provided below before terminal VERIFIED.
- `GOV-STANDING-BACKLOG-001` — `WI-5446` is the backlog authority.
- `ADR-CROSS-HARNESS-PARITY-001` — D's owner-visible model identity is consistent across argv, route resolver, and dispatcher label after the swap.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` / `SPEC-DISPATCHER-CONTROL-SURFACE-001` — dispatcher state/config for D inspected and changed through governed control/status surfaces.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — bounded PAUTH + implementation-start packet from the -004 GO.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — D retains the capability floor (full tool set, fail-closed guards) after the swap.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — no `applications/` or Agent Red file changed.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — decision + supersession captured as durable linked artifacts.

## Requirement Sufficiency

Existing requirements sufficient. The owner decision `DELIB-202666767`, the active
PAUTH, `WI-5446`, and the cited governing specs fully bound the change. No new or
revised requirement was needed; this is a model-selection change within an
existing, verified harness integration.

## Spec-to-Test Mapping (with observed results)

| Specification | Verification | Result |
| --- | --- | --- |
| `ADR-CROSS-HARNESS-PARITY-001` / `GOV-HARNESS-ONBOARDING-CONTRACT-001` | `scripts/verify_ollama_dispatch.py --readiness-only --json` | **PASS** — `ready: true`; checks: registry argv PASS, shim present PASS, routing skill route `bridge-review->deepseek-v4-flash-cloud; tool_calling=True; missing_tools=[]` PASS, `ollama /api/tags model_id=deepseek-v4-flash:cloud` PASS; `required_tools=[Read,Write,Edit,Grep,Glob,Bash]`. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` (full guard floor) | `scripts/verify_ollama_dispatch.py` (full live mode) | **PASS 7/7** — L1 tool-loop round-trip (calls=2, schemas=True, content_match=True); L2 author metadata (`metadata.model_id=deepseek-v4-flash:cloud` == route); L3 bridge filing via Write dispatch (file_created, first_line_is_NEW); G1 destructive-Bash denial; G2 formal-artifact denial; G3 out-of-root denial; G4 bridge-Bash mutation denial. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest test_verify_ollama_dispatch.py::...deepseek_v4_flash_cloud ...::...full_lo_tool_set groundtruth-kb/tests/test_doctor_ollama.py -q` | **PASS** — 19 passed, 0 failed. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` / `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `gt bridge dispatch status --json` + `gt bridge dispatch health --json` | **PASS** — D `can_receive_dispatch: true`, `role: [loyal-opposition]`, `model: deepseek-v4-flash-cloud`; daemon `aggregate_status: healthy`, `active_substrate: dispatcher_daemon`. |
| Code quality (per bridge protocol pre-file gates) | `ruff check` + `ruff format --check` on the edited test file | **PASS** — check: "All checks passed!"; format: "1 file already formatted". |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target-path inspection | **PASS** — all edits in-root; no `applications/` / Agent Red path touched. |

## Commands Executed

```
# routing.toml: Edit tool (add flash-cloud model; repoint ollama default + skills)
gt harness set-invocation-surface --harness D --surface headless --value-json <d-headless.json>
gt bridge dispatch config set-model D --model deepseek-v4-flash-cloud --json
# test_verify_ollama_dispatch.py: Edit tool (rename + rewrite route-identity test)
POST http://localhost:11434/api/pull {"name":"deepseek-v4-flash:cloud"}  -> {"status":"success"}
python scripts/verify_ollama_dispatch.py --readiness-only --json          -> ready: true
python -m pytest <route-identity + tool-set + test_doctor_ollama.py> -q   -> 19 passed
python -m ruff check / ruff format --check <test_verify_ollama_dispatch.py> -> RC 0 / RC 0
python scripts/verify_ollama_dispatch.py --json                            -> 7/7 ALL CHECKS PASSED
gt bridge dispatch status --json ; gt bridge dispatch health --json        -> D flash-eligible; daemon healthy
```

## Owner Decisions / Input

- `DELIB-202666767` — owner decision (AskUserQuestion-backed) to swap D's reviewer
  model to DeepSeek V4 Flash via the governed bridge path.
- Owner directive (2026-07-17): "OpenRouter/Ollama must be made fully functional
  and dispatchable with DeepSeek V4 Flash, ASAP." Authorizes the enablement pull
  (change #5) and D dispatch readiness.
- Owner AUQ (2026-07-17): "You GO wi5446-003 in your LO session." GO landed at
  `-004` from an independent session context (`82426707-...`, `::init gtkb lo`),
  distinct from this Prime session (`2d31ebb3-...`).
- `PAUTH-PROJECT-GTKB-OLLAMA-DIRECT-CLOUD-HARNESS-WI5446-DEEPSEEK-FLASH-20260717`
  — active bounded authorization; all direct target_paths within `{config, test}`.

## Prior Deliberations

- `DELIB-202666767` — owner decision authorizing this swap (the trigger); GO-verified positive.
- `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` — prior kimi switch; superseded for future D dispatch, retained as history.
- `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD` — earlier DeepSeek V4 Pro pin; this returns D to the DeepSeek family at the cheaper flash tier.
- `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-001.md` — mirrored precedent (same route-switch class); this thread narrowed scope (Path 2) instead of amending the PAUTH.
- `bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-004.md` — the GO whose Implementation Guidance (readiness-before-file, governed-CLI-only registry/label, ruff both gates) this report followed.
- `WI-5446` — the tracked defect (D/kimi non-compliant verdict bodies) this swap remediates.

## Risk / Rollback

Provider/route confusion was the principal risk and is handled: the Ollama
`deepseek-v4-flash:cloud` route (provider `ollama`, key `deepseek-v4-flash-cloud`)
is distinct from the untouched OpenRouter `deepseek-v4-flash` entry (provider
`openrouter`). Readiness `ready: true` and the L2 author-metadata check confirm
the live route resolves to `deepseek-v4-flash:cloud`.

Rollback is a single-commit revert restoring routing.toml to
`kimi-k2-7-code-cloud`, plus the governed reverse transactions for D's argv and
dispatcher label. Bridge files, deliberations, work items, and PAUTH records are
append-only and are not deleted by rollback. The registered `deepseek-v4-flash:cloud`
daemon tag may remain (idle registration, no dispatch cost) or be removed
separately.

## Recommended Commit Type

`chore` — a config-only route-selection change (routing.toml route entry +
governed registry-argv/dispatcher-label transactions + a focused test-fixture
update), no new capability surface and no source-behavior change, consistent with
the approved proposal (-003/-004) and the `WI-5047` route-switch precedent. The
git-tracked diff is `.api-harness/routing.toml` and
`platform_tests/scripts/test_verify_ollama_dispatch.py` only.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
