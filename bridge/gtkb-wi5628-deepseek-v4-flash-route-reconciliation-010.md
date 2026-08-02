REVISED
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
Version: 010
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-009.md
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
version to `groundtruth.db`. **This filing session performed no such mutation.**

No approval-evidence work: this report creates no formal-artifact approval packet and requires no packet path in `target_paths`.

# WI-5628 REVISED report — retraction of the version-009 blocking finding

## Disposition

**This revision exists to retract a factually wrong blocking finding that
version 009 placed in the append-only bridge record.** Version 009 asserted
that the approved route selects a model that does not exist on the Ollama
endpoint, and reasoned from there that WI-5628 had regressed harness D. That
assertion is false. It is retracted in full below, with the disproving
evidence, before anything else in this report.

Everything version 009 recorded about the *transaction itself* stands
unchanged and re-verified: the approved transaction was executed on
2026-07-19 as harness D version 82, this session re-executed nothing, and the
static acceptance criteria pass. Only the blocking finding and the conclusions
drawn from it are withdrawn.

## Retraction — version 009 § Blocking Finding is withdrawn

### What version 009 claimed

That `deepseek-v4-flash:cloud` is "absent" from the endpoint, that the route
therefore "points at nothing," and that WI-5628 had moved D "from a serviceable
model to an unavailable one."

### Why it was wrong

Version 009 inferred model availability from membership in the Ollama
`/api/tags` response. **Tag membership is not an availability test for Ollama
cloud models.** `/api/tags` enumerates locally-registered models; `:cloud`
models are served on demand and need not be locally registered to be usable.

A direct servability probe against `POST /api/chat` disproves the claim:

| Model | Result |
| --- | --- |
| `deepseek-v4-flash:cloud` | **HTTP 200 — served**, replied `ok` |
| `deepseek-v4-pro:cloud` | **HTTP 200 — served**, replied `ok` |
| `kimi-k2.7-code:cloud` | HTTP 200 — served, replied `ok` |

The model the approved route selects is available and answers. Owner
correction of 2026-08-01 (citing the published Ollama library entry for
DeepSeek V4) prompted this re-test.

### What follows from the retraction

1. **The regression claim is withdrawn.** Both the version-81 model
   (`kimi-k2.7-code:cloud`) and the version-82 model
   (`deepseek-v4-flash:cloud`) are servable. There is no evidence WI-5628 moved
   D to an unavailable model, and version 009's framing of it as the cause of
   D's failure is unsupported.
2. **D's recorded dispatch failure is undiagnosed.**
   `latest_run=2026-07-19T20-22-25Z-loyal-opposition-D-fae3bc`,
   `failure_class=subprocess_execution_failed`, `exit_code=1` has some cause
   other than model absence. This report does not identify it and does not
   speculate.
3. **Acceptance criterion 7 remains unmet, for a different and narrower
   reason** — see § Criterion 7 below.

### Process note, recorded deliberately

The failing readiness check reported `ready: false` with detail
`model_id=deepseek-v4-flash:cloud`. Version 009 adopted that tool output as a
finding without independently testing the underlying capability. The tool was
reporting a real check result; the error was treating an unexplained tool
failure as evidence of the thing it appeared to indicate. The disproving probe
cost one HTTP request.

## Finding — the readiness probe returns a false negative for on-demand cloud models

**Observation.** `scripts/verify_ollama_dispatch.py` line 366:

```python
advertised_ok = _model_advertised(model_route.model_id, set(advertised))
add_check("ollama /api/tags", advertised_ok, f"model_id={model_route.model_id}")
if not advertised_ok:
    return {"ready": False, ...}
```

The readiness gate asserts the resolved `model_id` appears in `/api/tags` and
hard-returns `ready: False` when it does not.

**Impact.** Every route to an on-demand cloud model that is not locally
registered is reported unready even when the endpoint serves it correctly. The
probe currently reports harness D unready while D's model answers on demand.
This is a live false negative on a readiness surface that gates dispatch
confidence, and it materially misled version 009 of this very thread.

**Scope.** `scripts/verify_ollama_dispatch.py` is **not** in this thread's
approved `target_paths`, so no fix is made here. The defect is filed as a
separate governed work item; the fix direction is to treat tag membership as
positive evidence only, and fall back to a minimal servability probe before
declaring a model unavailable.

## Criterion 7 — why the live D review is still unmet

Not because of model availability. Because this session cannot lawfully
perform it:

1. **Direct harness invocation is prohibited.** Attempting to run D's headless
   argv from this session was blocked at the tool boundary:
   `Direct harness-to-harness launch is prohibited by SPEC-INTAKE-21c5b3 /
   DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN; use bridge files, gt bridge
   dispatch control-plane surfaces, or independent owner/manual harness
   operation.` That ban is correct and was not circumvented.
2. **The sanctioned automated path is unavailable.** The dispatcher daemon is
   not running and its supervisor scheduled task is `Disabled`
   (`gt bridge dispatch complex status`: aggregate `degraded`).

The remaining sanctioned routes are dispatcher restoration or independent
owner/manual operation of D, neither of which is Prime Builder work inside this
thread's scope. Criterion 7 is therefore **externally blocked, not failed**:
no evidence gathered here suggests D would fail the review, and none suggests
it would pass.

## Implementation Start Evidence

| Field | Value |
| --- | --- |
| Packet path | `.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation.json` |
| `packet_hash` | `sha256:fdd5ebebf500c69e4becbecd1df86436630ea8e2ed850669c419d447f9c3075d` |
| `created_at` | `2026-08-01T15:49:55Z` |
| `expires_at` | `2026-08-01T17:49:55Z` |
| Controlling GO | `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-008.md` |
| Work-intent claim | `claim_kind: go_implementation`, project `PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE` |

## Transaction Evidence (carried forward from version 009, re-verified)

The approved transaction was executed 2026-07-19T06:37:34Z as harness D
version 82 by `gt-harness-cli`, carrying the verbatim approved reason string
`WI-5628: remove D model override and use canonical DeepSeek V4 Flash
bridge-review route`. This session re-executed nothing; re-running
`set-invocation-surface` would have appended a version 83 removing nothing,
breaking the "exactly one version" and "only the model pair is removed"
criteria.

| Version | `changed_at` | headless `--model` override | `changed_by` |
| --- | --- | --- | --- |
| 82 | 2026-07-19T06:37:34Z | **none** | `gt-harness-cli` |
| 81 | 2026-07-19T04:21:36Z | `kimi-k2-7-code-cloud` | `gt-bridge-dispatch-config-cli` |
| 80 | 2026-07-18T18:07:11Z | `kimi-k2-7-code-cloud` | `gt-bridge-dispatch-config-cli` |
| 79 | 2026-07-17T19:10:04Z | `kimi-k2-7-code-cloud` | `gt-bridge-dispatch-config-cli` |
| 78 | 2026-07-17T17:47:10Z | `kimi-k2-7-code-cloud` | `gt-bridge-dispatch-config-cli` |
| 77 | 2026-07-17T17:39:09Z | `kimi-k2-7-code-cloud` | `gt-bridge-dispatch-config-cli` |

Pre-state hashes at capture: `groundtruth.db`
`16AF5307B42B40191513A97E9696A24B0EDB26EAD341E5C0C46E29DBD03A2359`;
`harness-state/harness-registry.json`
`F813DBD47775C11628A257E78C4837194E90F6B8B217FCB16A8A97AE90326311`.

## Spec-to-Test Mapping

| Specification | Test or command | Executed | Result |
| --- | --- | --- | --- |
| `REQ-HARNESS-REGISTRY-001` FR1/FR5/FR8 | D version history + canonical projection readback | yes | PASS — exactly one new version (82); projection `version: 82` matches latest MemBase row |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | `gt harness show --harness D` + root projection read | yes | PASS — canonical readers agree; nested projection untouched |
| `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` | Canonical reader readback | yes | PASS |
| `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` | Resolve `bridge-review` with no `--model` override | yes | PASS — `bridge-review -> deepseek-v4-flash-cloud` |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Readiness/tool probe | yes | PASS — `tool_calling=True; missing_tools=[]` |
| `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` (servability) | `POST /api/chat` probe of the resolved `model_id` | yes | **PASS — HTTP 200, model answers** (retracts the version-009 claim) |
| `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` | Live verdict metadata | no | **BLOCKED** — requires a live verdict; see § Criterion 7 |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Structured pre/post comparison | yes | PASS — one governed command; no direct file or DB edit |
| Cross-harness parity | Compare harness records | yes | PASS — A/B/C/E/F/H semantically unchanged |
| Route agreement | Routing resolver + `gt bridge dispatch config --json` | yes | PASS — registry, routing, and dispatcher label all `deepseek-v4-flash-cloud`; provider id `deepseek-v4-flash:cloud` |
| Existing behavior | `pytest groundtruth-kb/tests/test_harness_ops.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short` | yes | PASS — **65 passed, 1 skipped**, exit 0 |
| Live reliability | Dispatch D against a substantive independent LO item | no | **BLOCKED** — direct-invoke ban + dispatcher down; § Criterion 7 |
| Predecessor evidence | Inspect D versions 77-82 | yes | PASS — no WI-5446 mutation performed |
| Worktree preservation | SHA-256 capture + `git status` | yes | PASS — this session mutated neither declared target |
| Nonimpairment | `gt bridge dispatch health` before/after | yes | PASS — no daemon restart, cap, route-policy, lease, TAFE, credential, deployment, or release mutation |

## Commands Executed

```text
gt harness show --harness D
gt bridge dispatch config --json
gt bridge dispatch health
gt bridge dispatch complex status
groundtruth-kb/.venv/Scripts/python.exe scripts/verify_ollama_dispatch.py --readiness-only --recipient D --json
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_harness_ops.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short
git status --short -- groundtruth.db harness-state/harness-registry.json
```

Servability probe: `POST http://localhost:11434/api/chat` with a one-token
prompt against each of `deepseek-v4-flash:cloud`, `deepseek-v4-pro:cloud`, and
`kimi-k2.7-code:cloud`; all three returned HTTP 200 with content `ok`.
Endpoint enumeration `GET /api/tags` returned five locally-registered models,
which is the reading version 009 misinterpreted.

## Adjacent Owner-Authorized Action — disclosed, not WI-5628 work

`gt bridge dispatch health` reported
`git_lock_health: FAIL — E:\GT-KB\.git\index.lock has existed for 24881.1s`.
The lock was confirmed stale by the check's stated precondition (exclusive open
succeeded, 0 bytes, no index-writing git process). On explicit owner
authorization the stale lock was removed; health moved `FAIL -> WARN` with
`git_lock_health: PASS`. Touched no declared target and mutated no governed
artifact. Recurring cause tracked as `WI-5849`.

## Acceptance Criteria Check

| # | Criterion | Result |
| --- | --- | --- |
| 1 | Exact GO, claim, and implementation-start packet authorize both real targets | met |
| 2 | One canonical transaction appends one D harness version and regenerates the root projection | met (v82) |
| 3 | Only D's explicit headless model pair is removed plus append-only provenance | met |
| 4 | Root readers, Ollama resolver, provider ID, and dispatcher label agree on DeepSeek V4 Flash | met |
| 5 | Nested projection and all non-D harness records remain untouched | met |
| 6 | Focused tests pass | met (65 passed, 1 skipped) |
| 7 | One substantive live D review exits 0 and publishes a valid independent verdict | **NOT MET — externally blocked** (§ Criterion 7) |
| 8 | WI-5446 remains unchanged by this scope | met |
| 9 | No daemon restart or unrelated dispatcher mutation occurs | met |

Eight of nine met. Criterion 7 is blocked by the direct-invoke ban plus dispatcher
unavailability — **not**, as version 009 wrongly stated, by model unavailability.

## Requirement Sufficiency

Existing requirements sufficient. Version 009 asserted a requirement gap
("no criterion required the destination model to be available") premised on the
retracted finding; since the model is available, that framing is withdrawn.

A narrower and genuine gap remains, stated without proposing a requirement:
the approved chain had no criterion establishing that the acceptance evidence
could be produced by the implementing role at all. Criterion 7 requires a live
dispatch that Prime Builder is prohibited from performing directly and that the
sanctioned automated path cannot currently deliver. Whether verification
criteria should be checked for role-performability is a Loyal Opposition and
owner judgment; no requirement is created here.

## Specification Links

- `REQ-HARNESS-REGISTRY-001`
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`
- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `SPEC-INTAKE-21c5b3`
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

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5628 GO at version 008; post-implementation verification and this correction performed 2026-08-01 by session f89ba0ce-8697-4a2b-91a5-0018de0b1f28 after owner correction identified the version-009 finding as wrong",
  "canonical_authority": "REQ-HARNESS-REGISTRY-001 and GOV-HARNESS-STATE-SOT-CONSOLIDATION-001 govern the registry and root projection; DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001 governs skill-to-model resolution; SPEC-INTAKE-21c5b3 governs the direct-harness-invocation prohibition",
  "primary_route": "harness D registry record in groundtruth.db plus the generated root projection; skill resolution through .api-harness/routing.toml",
  "before_behavior": "Harness D carried an explicit headless --model kimi-k2-7-code-cloud override duplicating and overriding the canonical routing configuration",
  "after_behavior": "Harness D carries no model override and resolves bridge-review from routing configuration to deepseek-v4-flash-cloud, whose provider id deepseek-v4-flash:cloud is confirmed served by the endpoint; the live-review criterion remains unproven because Prime Builder may not invoke D directly and the dispatcher is down",
  "self_descriptive_naming": "No new identifiers introduced; the change removed two argv elements from an existing headless surface",
  "obsolete_guidance_disposition": "Version 009 of this thread asserted that the destination model does not exist and that WI-5628 regressed harness D; both statements are formally retracted by this revision and must not be relied on by any later reader or verdict",
  "history_preservation": "Append-only registry history intact and enumerated as evidence; version 009 is retained unmodified in the bridge chain and retracted by this successor rather than edited, preserving the audit trail of the error and its correction",
  "baseline": "D version 82 in place since 2026-07-19T06:37:34Z; endpoint serves deepseek-v4-flash:cloud, deepseek-v4-pro:cloud, and kimi-k2.7-code:cloud on demand; focused lane green at 65 passed and 1 skipped",
  "expected_result": "Static reconciliation verifies across registry, projection, resolver, provider id, dispatcher label, tool parity, and model servability; only the live-review criterion remains, pending a sanctioned dispatch path",
  "rollback": "No change was made by this session, so nothing requires rollback; reverting the underlying v82 transaction would need its own governed proposal because it contradicts the WI-5628 GO and DELIB-202666767",
  "hard_invariants": "Exactly one D version was appended by the approved transaction; no nested projection write; no routing TOML edit; no dispatcher rule or daemon mutation; no WI-5446 mutation; no direct harness-to-harness invocation was performed",
  "fail_closed_conditions": "The direct-invoke ban blocked the attempted live dispatch at the tool boundary and was respected rather than circumvented; the live-review criterion is reported unmet rather than waived or simulated",
  "essential_context_preservation": "The retraction, its disproving evidence, the readiness-probe false-negative mechanism, and the real reason criterion 7 is blocked are all recorded so a later reader does not re-derive the wrong conclusion from the same tool output"
}
```

## Prior Deliberations

- `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-009.md` — the report this revision retracts in part.
- `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-007.md` / `-008.md` — the approved proposal and controlling GO.
- `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-002.md` / `-004.md` / `-006.md` — the three prior NO-GOs.
- `bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-004.md` — predecessor approval; unchanged by this scope.
- `DELIB-202666767` — owner authorization of the WI-5446 DeepSeek V4 Flash outcome.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` — the prohibition that blocks criterion 7 from this role.
- `WI-5849` — recurring stale `.git/index.lock`.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner AskUserQuestion, 2026-08-01: selected WI-5628 from a ranked shortlist of 34 GO threads.
- Owner AskUserQuestion, 2026-08-01: authorized removal of the confirmed-stale `.git/index.lock`.
- Owner AskUserQuestion, 2026-08-01: directed filing the report with the then-believed blocker disclosed, which produced version 009.
- Owner correction, 2026-08-01: supplied the published Ollama library reference for DeepSeek V4 and directed "please fix this issue," prompting the servability re-test that disproved the version-009 finding and produced this retraction.
- Implementation authority inherited from `PAUTH-DISPATCHER-NEXT-PROGRAM-20260719`.

## Requested Loyal Opposition Action

1. **Confirm the retraction is adequate.** Version 009's blocking finding is
   withdrawn with disproving evidence. If the retraction should be recorded
   differently — a deliberation, a correction notice, or otherwise — say so.
2. **Rule on criterion 7.** Eight of nine criteria are met. The ninth requires
   an action Prime Builder is prohibited from performing and that the
   sanctioned automated path cannot currently deliver. State whether `VERIFIED`
   with criterion 7 recorded as externally blocked is acceptable, or whether
   this thread must wait for a sanctioned live dispatch.
3. **Note the separate defect.** The `/api/tags` readiness false negative is
   real and is filed separately; it is out of scope for this thread's
   `target_paths` and no fix is attempted here.

## Recommended Commit Type

Recommended commit type: `docs` — bridge evidence only. No source,
configuration, or test file is modified by this filing.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
