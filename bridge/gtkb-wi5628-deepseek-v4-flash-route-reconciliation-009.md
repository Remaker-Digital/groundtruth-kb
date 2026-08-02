NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f89ba0ce-8697-4a2b-91a5-0018de0b1f28
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; transcript-resolved role prime-builder via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: implementation_report
Document: gtkb-wi5628-deepseek-v4-flash-route-reconciliation
Version: 009
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-008.md
Controlling GO: bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-008.md

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5628
Related Work Items: WI-5446, WI-5849

target_paths: ["groundtruth.db", "harness-state/harness-registry.json"]
implementation_scope: configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
dispatcher_or_tafe_mutation_in_scope: false

KB mutation in scope: the approved transaction appends one harness-registry
version to `groundtruth.db`. **This filing session performed no such mutation** —
see § Disposition. No MemBase write, insert, edit, or lifecycle change was made
by session `f89ba0ce-8697-4a2b-91a5-0018de0b1f28`.

No approval-evidence work: this report creates no formal-artifact approval packet and requires no packet path in `target_paths`.

# WI-5628 implementation report — transaction already executed; live route is non-functional

## Disposition

**The approved transaction was already executed on 2026-07-19. This session
re-executed nothing.** This report supplies the post-implementation evidence
that was never filed: the chain has sat at `GO`-008 with no report since.

Pre-state capture (transaction step 2, mandated by the approved proposal)
established that harness D version 82 already carries the exact approved
outcome. Re-running `gt harness set-invocation-surface` would have appended a
**version 83 that removes nothing**, breaking two acceptance criteria at once:
"one canonical transaction appends **one** D harness version" and "only D's
explicit headless model pair is removed." The step-2 capture is what prevented
that; it is recorded here because it is the load-bearing reason this report
contains no new transaction.

**The reconciliation is internally correct and externally non-functional.**
Every static acceptance criterion verifies. The final criterion — one
substantive live D review exiting `0` with a published verdict — is **not met
and cannot presently be met**, because the model the approved route selects
does not exist on the Ollama endpoint. Evidence in § Blocking Finding.

## Filing Provenance

| Activity | Session |
| --- | --- |
| Approved transaction (harness D v82, 2026-07-19T06:37:34Z) | `gt-harness-cli`; originating session not recorded in the row |
| Work-intent claim, implementation-start packet, verification, and this filing | `f89ba0ce-8697-4a2b-91a5-0018de0b1f28` |

Review independence is measured against `f89ba0ce-8697-4a2b-91a5-0018de0b1f28`,
the author session of this artifact.

## Implementation Start Evidence

| Field | Value |
| --- | --- |
| Packet path | `.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation.json` |
| `packet_hash` | `sha256:fdd5ebebf500c69e4becbecd1df86436630ea8e2ed850669c419d447f9c3075d` |
| `created_at` | `2026-08-01T15:49:55Z` |
| `expires_at` | `2026-08-01T17:49:55Z` |
| Controlling GO | `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-008.md` |
| Packet `latest_status` at mint | `GO` |
| Work-intent claim | `claim_kind: go_implementation`, project `PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE` |

The packet authorizes both declared targets. Neither was mutated by this
session; the packet evidences authorized implementation *scope*, and the
verification below is what was actually performed under it.

## Pre-State Capture (approved transaction step 2)

| Item | Value at capture |
| --- | --- |
| D MemBase row | version 82, `changed_at 2026-07-19T06:37:34+00:00`, `changed_by gt-harness-cli` |
| D `change_reason` | `WI-5628: remove D model override and use canonical DeepSeek V4 Flash bridge-review route` |
| D headless argv | `[... "scripts/ollama_harness.py", "-p", "{{PROMPT}}", "--skill", "bridge-review"]` — no `--model` pair |
| `groundtruth.db` SHA-256 | `16AF5307B42B40191513A97E9696A24B0EDB26EAD341E5C0C46E29DBD03A2359` |
| `harness-state/harness-registry.json` SHA-256 | `F813DBD47775C11628A257E78C4837194E90F6B8B217FCB16A8A97AE90326311` |
| Git attribution | `harness-state/harness-registry.json` modified in worktree by foreign concurrent sessions; `groundtruth.db` not listed as modified at capture |

The `change_reason` on version 82 is the **verbatim reason string** specified in
the approved proposal's step 5 command. That, plus the argv shape, is what
establishes the transaction as already executed rather than merely similar.

### Append-only history proving the transition

| Version | `changed_at` | headless `--model` override | `changed_by` |
| --- | --- | --- | --- |
| 82 | 2026-07-19T06:37:34Z | **none** | `gt-harness-cli` |
| 81 | 2026-07-19T04:21:36Z | `kimi-k2-7-code-cloud` | `gt-bridge-dispatch-config-cli` |
| 80 | 2026-07-18T18:07:11Z | `kimi-k2-7-code-cloud` | `gt-bridge-dispatch-config-cli` |
| 79 | 2026-07-17T19:10:04Z | `kimi-k2-7-code-cloud` | `gt-bridge-dispatch-config-cli` |
| 78 | 2026-07-17T17:47:10Z | `kimi-k2-7-code-cloud` | `gt-bridge-dispatch-config-cli` |
| 77 | 2026-07-17T17:39:09Z | `kimi-k2-7-code-cloud` | `gt-bridge-dispatch-config-cli` |

Exactly one version (82) removes the override. This confirms the approved
"exactly one new D version" outcome was achieved, and confirms the v007
proposal's finding that no D row ever contained a Flash model pair — the route
resolves from configuration, not from the registry, which is the approved design.

## Blocking Finding — the approved route selects a model that does not exist

**Observation.** The Ollama endpoint is healthy and returns five models:

```text
kimi-k2.7-code:cloud
kimi-k2.6:cloud
qwen3-coder-next:cloud
qwen3.6:latest
gemma4:latest
```

`deepseek-v4-flash:cloud` is **absent**. So is `deepseek-v4-pro:cloud`. Four
`:cloud` models are present, so this is not a general false negative on
cloud-suffixed routes — the DeepSeek cloud models specifically are not
provisioned on this endpoint.

**Mechanism.** With the model override removed (the approved outcome),
`--skill bridge-review` resolves through `.api-harness/routing.toml`
(`[routing.ollama.skills] bridge-review = "deepseek-v4-flash-cloud"`) to
`model_id = "deepseek-v4-flash:cloud"`. That identifier is then requested from
an endpoint that does not serve it.

**Regression relationship.** Version 81 routed D to `kimi-k2-7-code-cloud` →
`kimi-k2.7-code:cloud`, which **is** present on the endpoint. Version 82 routed
it to a model that is not. D's recorded dispatch failure
(`latest_run=2026-07-19T20-22-25Z-loyal-opposition-D-fae3bc`,
`failure_class=subprocess_execution_failed`, `exit_code=1`) is dated **after**
the version-82 change at 06:37Z. The evidence is therefore consistent with
WI-5628 having moved D from a serviceable model to an unavailable one. This
report does not assert that D was verified working before v82 — no such
evidence was found either way — only that v81's model is present on the
endpoint today and v82's is not.

**Consequence for the acceptance criteria.** The criterion "one substantive
live D review exits `0` and publishes a valid independent verdict" is not
merely untested; it is **not presently satisfiable**. Owner direction
(AskUserQuestion, 2026-08-01) was to file this report with the blocker
disclosed rather than spend provider tokens reproducing a known failure or
unilaterally re-targeting the route.

**Scope note.** Remedying this is outside WI-5628's approved scope. It is
either an environment/entitlement action (provision `deepseek-v4-flash:cloud`
on the endpoint) or a route change (re-target the skill), and the approved
proposal explicitly forbids routing-TOML edits. Loyal Opposition should rule on
which path applies.

## Spec-to-Test Mapping

| Specification | Test or command | Executed | Result |
| --- | --- | --- | --- |
| `REQ-HARNESS-REGISTRY-001` FR1/FR5/FR8 | D version history + canonical projection readback | yes | PASS — exactly one new version (82); projection `version: 82` matches latest MemBase row; invocation remains data-driven |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | `gt harness show --harness D` + root projection read | yes | PASS — both canonical readers agree; nested projection neither read nor written as authority |
| `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` | Canonical reader readback | yes | PASS — no committed-JSON reader introduced by this work |
| `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` | Resolve `bridge-review` with no `--model` override | yes | PASS — readiness probe reports `bridge-review->deepseek-v4-flash-cloud` |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Readiness/tool probe | yes | PASS — `tool_calling=True; missing_tools=[]` |
| `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` | Live verdict metadata | **no** | **BLOCKED** — requires a live verdict; model absent (§ Blocking Finding) |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Structured pre/post comparison | yes | PASS — one governed command (v82, `changed_by gt-harness-cli`); no direct file or DB edit |
| Cross-harness parity | Compare harness records | yes | PASS — A/B/C/E/F/H records semantically unchanged; D identity is truthful to its configuration |
| Route agreement | Routing resolver + `gt bridge dispatch config --json` | yes | PASS — registry, routing, and dispatcher label all say `deepseek-v4-flash-cloud`; provider id `deepseek-v4-flash:cloud` |
| Existing behavior | `pytest groundtruth-kb/tests/test_harness_ops.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short` | yes | PASS — **65 passed, 1 skipped**, exit 0 |
| Live reliability | Dispatch D against a substantive independent LO item | **no** | **BLOCKED** — § Blocking Finding; `ready: false`, `/api/tags` lacks the model |
| Predecessor evidence | Inspect D versions 77-82 | yes | PASS — history table above; no WI-5446 mutation performed |
| Worktree preservation | SHA-256 capture + `git status` | yes | PASS — this session mutated neither declared target |
| Nonimpairment | `gt bridge dispatch health` before/after | yes | PASS for WI-5628 — no daemon restart, cap, route-policy, lease, TAFE, credential, deployment, or release mutation. See § Adjacent Owner-Authorized Action |

## Commands Executed

```text
gt harness show --harness D
gt bridge dispatch config --json
gt bridge dispatch health
groundtruth-kb/.venv/Scripts/python.exe scripts/verify_ollama_dispatch.py --readiness-only --recipient D --json
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_harness_ops.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short
git status --short -- groundtruth.db harness-state/harness-registry.json
```

Endpoint model enumeration was read from `http://localhost:11434/api/tags`
(HTTP 200, five models, listed in § Blocking Finding).

## Adjacent Owner-Authorized Action — disclosed, not part of WI-5628

During verification, `gt bridge dispatch health` reported
`git_lock_health: FAIL — E:\GT-KB\.git\index.lock has existed for 24881.1s`.
The lock was confirmed stale by the check's own stated precondition: an
exclusive open succeeded (no holder), the file was 0 bytes, and no
index-writing git process existed. On explicit owner authorization
(AskUserQuestion, 2026-08-01) the stale lock was removed; health moved
`FAIL -> WARN` with `git_lock_health: PASS`.

This is disclosed because it changed a health reading cited in this report. It
is **not** WI-5628 work, touched no declared target, and mutated no governed
artifact. The recurring cause is tracked as `WI-5849`.

## Acceptance Criteria Check

| # | Criterion | Result |
| --- | --- | --- |
| 1 | Exact GO, claim, and implementation-start packet authorize both real targets | met |
| 2 | One canonical transaction appends one D harness version and regenerates the root projection | met (v82) |
| 3 | Only D's explicit headless model pair is removed plus append-only provenance | met |
| 4 | Root readers, Ollama resolver, provider ID, and dispatcher label agree on DeepSeek V4 Flash | met |
| 5 | Nested projection and all non-D harness records remain untouched | met |
| 6 | Focused tests pass | met (65 passed, 1 skipped) |
| 7 | One substantive live D review exits 0 and publishes a valid independent verdict | **NOT MET — not presently satisfiable** |
| 8 | WI-5446 remains unchanged by this scope | met |
| 9 | No daemon restart or unrelated dispatcher mutation occurs | met |

Eight of nine met. Criterion 7 is blocked by an external precondition, not by a
defect in the transaction.

## Requirement Sufficiency

Existing requirements sufficient for the transaction as approved. However, the
blocking finding exposes a requirement gap the approved proposal did not cover:
**no criterion required the destination model to be available on the endpoint
before re-targeting a harness route.** A route can satisfy every registry,
projection, resolver, and label check and still select a model that cannot be
served. Whether to close that gap with a new requirement is a Loyal Opposition
and owner judgment, and no requirement is created by this report.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5628 GO at bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-008.md; post-implementation verification performed 2026-08-01 by session f89ba0ce-8697-4a2b-91a5-0018de0b1f28",
  "canonical_authority": "REQ-HARNESS-REGISTRY-001 and GOV-HARNESS-STATE-SOT-CONSOLIDATION-001 govern the registry and its root projection; DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001 governs skill-to-model resolution",
  "primary_route": "harness D registry record in groundtruth.db plus the generated root projection harness-state/harness-registry.json; skill resolution through .api-harness/routing.toml",
  "before_behavior": "Harness D carried an explicit headless --model kimi-k2-7-code-cloud override that duplicated and overrode the canonical routing configuration",
  "after_behavior": "Harness D carries no model override and resolves bridge-review from routing configuration to deepseek-v4-flash-cloud; the resolved provider id deepseek-v4-flash:cloud is not served by the endpoint, so D is presently non-functional as a dispatch target",
  "self_descriptive_naming": "No new identifiers introduced; the change is the removal of two argv elements from an existing headless surface",
  "obsolete_guidance_disposition": "The v007 proposal recorded that WI-5446 claimed a registry transaction the append-only history does not substantiate; this report preserves that conflict as audit evidence and performs no WI-5446 mutation",
  "history_preservation": "Append-only registry history intact; versions 77 through 82 are enumerated in this report as evidence rather than altered, and this session appended no version",
  "baseline": "D version 82 in place since 2026-07-19T06:37:34Z; endpoint serving five models excluding deepseek-v4-flash:cloud; focused lane green at 65 passed and 1 skipped",
  "expected_result": "Static reconciliation verifies across registry, projection, resolver, provider id, dispatcher label, and tool parity; the live-review criterion fails until the destination model is provisioned or the route is re-targeted under a separate governed change",
  "rollback": "Reverting requires a new governed set-invocation-surface transaction restoring the explicit model pair; no file revert applies because the authoritative state is an append-only MemBase row, and any such revert needs its own proposal since it contradicts the WI-5628 GO and DELIB-202666767",
  "hard_invariants": "Exactly one D version was appended by the approved transaction; no nested projection write; no routing TOML edit; no dispatcher rule or daemon mutation; no WI-5446 work-item mutation",
  "fail_closed_conditions": "The readiness probe reports ready=false and exits 1 when the resolved model is absent from the endpoint, so the unavailability is surfaced rather than silently retried; the live-review criterion is reported unmet rather than waived",
  "essential_context_preservation": "The report preserves the v81-to-v82 model-override transition, the endpoint model enumeration, and the timing relationship to D's recorded dispatch failure, so a later reader can reconstruct why D is non-functional without re-deriving it"
}
```

## Specification Links

- `REQ-HARNESS-REGISTRY-001`
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`
- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-007.md` — the approved proposal whose step-2 pre-state capture prevented a redundant v83.
- `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-008.md` — the controlling GO.
- `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-002.md` / `-004.md` / `-006.md` — the three prior NO-GOs, none of which tested destination-model availability.
- `bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-004.md` — the predecessor approval; unchanged by this scope.
- `DELIB-202666767` — owner authorization of the WI-5446 DeepSeek V4 Flash outcome.
- `WI-5849` — recurring stale `.git/index.lock`, the cause of the adjacent health FAIL disclosed above.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner AskUserQuestion, 2026-08-01: selected WI-5628 from a ranked shortlist of 34 GO threads as the next Prime Builder work item.
- Owner AskUserQuestion, 2026-08-01: authorized removing the confirmed-stale `.git/index.lock` (disclosed above as an adjacent action, not WI-5628 work).
- Owner AskUserQuestion, 2026-08-01: presented with the blocking finding and the option to run the live test, re-target the route, or investigate provisioning, the owner selected **"File the report with the blocker disclosed"** — file the static evidence and let Loyal Opposition rule. That answer is the authority for filing with criterion 7 unmet.
- Implementation authority inherited from `PAUTH-DISPATCHER-NEXT-PROGRAM-20260719` cited in the header.

## Requested Loyal Opposition Action

Rule on whether the eight met criteria justify `VERIFIED` with criterion 7
recorded as externally blocked, or whether `NO-GO` is correct until D is
functional. Two points are offered specifically:

1. **Disposition of the unavailable model.** Provisioning
   `deepseek-v4-flash:cloud` and re-targeting the skill route are both outside
   this thread's approved scope. Please state which path WI-5628 should take
   and whether it belongs in this thread or a successor.
2. **The requirement gap.** No criterion in the approved chain required the
   destination model to be servable. If that should become a durable
   requirement for harness-route changes, it needs its own governed capture.

## Recommended Commit Type

Recommended commit type: `docs` — this filing adds bridge evidence only. The
underlying registry change was an append-only MemBase transaction executed in a
prior session and is not carried by this report's paths; no source,
configuration, or test file is modified by this filing.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
