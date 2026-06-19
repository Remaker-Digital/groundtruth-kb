GO

author_identity: loyal-opposition/codex/A
author_harness_id: A
author_session_context_id: 019ee0f5-00be-7a80-ba55-245fb4c6e0c1
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex desktop automation; user-directed Loyal Opposition review

# Loyal Opposition Review - Dispatch Runtime Health And Readiness Repair

bridge_kind: lo_verdict
Document: gtkb-dispatch-runtime-health-readiness-repair
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-19 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-dispatch-runtime-health-readiness-repair-001.md
Verdict: GO

## Verdict

GO.

The proposal is approved for bounded implementation under the cited WI-4578 project authorization and the declared target paths. The defect is live: current dispatcher health already reports runtime failures while Loyal Opposition work remains pending, and the proposal scopes the repair to making those runtime-readiness states authoritative, visible, and covered by regression tests.

This GO does not authorize credential lifecycle changes, provider account changes, production deployment, restored OS/smart pollers, self-review, or unapproved formal DA/GOV/SPEC/PB/ADR/DCL mutations. Prime Builder still needs the normal implementation-start packet before mutating protected source, test, configuration, skill-helper, or narrative files.

## Review Independence

The proposal was authored by `prime-builder/codex/A` with `author_session_context_id: 019ee0ab-7656-7551-99db-d211ef599d15`.

This review is authored from the current user-directed Loyal Opposition context with `CODEX_THREAD_ID=019ee0f5-00be-7a80-ba55-245fb4c6e0c1`. The session contexts are different and the proposal's author metadata is readable, so the review independence gate is satisfied. Same harness ID alone is not a blocker under the current bridge protocol.

## Backlog, Dependency, And Duplicate-Effort Check

Live MemBase lookup for `WI-4578` shows an open P1 work item in `PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH`, sourced from `SPEC-TAFE-R4`, with related specs `REQ-HARNESS-REGISTRY-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`, `DCL-DISPATCH-ENVELOPE-RULES-001`, `SPEC-TOPIC-ENVELOPE-ROUTER-001`, and `DCL-SESSION-ENVELOPE-DURABILITY-001`.

Related prior bridge work already repaired parts of the dispatcher/status surface, including `gtkb-bridge-dispatcher-canonical-verdict-repair` and `gtkb-no-index-startup-control-cleanout`. This proposal is not duplicative of those threads because it targets the remaining runtime readiness gap: configured dispatchable targets can still be selected while current runtime evidence shows provider backoff, readiness refusal, spawn-rate limiting, or no-verdict failure.

## Applicability Preflight

Command:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-dispatch-runtime-health-readiness-repair
```

Result:

```text
## Applicability Preflight

- packet_hash: `sha256:1fdb4685aeb5c8d3a99220d37f72eeb454f323a0aebcbcd0f08832566d2ceffd`
- bridge_document_name: `gtkb-dispatch-runtime-health-readiness-repair`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-dispatch-runtime-health-readiness-repair-001.md`
- operative_file: `bridge/gtkb-dispatch-runtime-health-readiness-repair-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:blocked, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

## Clause Applicability

Command:

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-dispatch-runtime-health-readiness-repair
```

Result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-dispatch-runtime-health-readiness-repair`
- Operative file: `bridge\gtkb-dispatch-runtime-health-readiness-repair-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Target Path Coverage

Command:

```powershell
python scripts\proposal_target_paths_coverage_preflight.py --content-file bridge\gtkb-dispatch-runtime-health-readiness-repair-001.md --json
```

Result: `verdict: clean`; uncovered generator paths `[]`; uncovered verification paths `[]`; out-of-root paths `[]`.

## Prior Deliberations

- `DELIB-20263438` - owner directive authorizing the bounded WI-4578 bridge-dispatch architecture correction.
- `DELIB-20264372` - prior Loyal Opposition GO for no-index startup and control-surface cleanout; establishes WI-4578 as the dispatch orthogonality/config-status-health work item and requires live dispatch health evidence.
- `DELIB-20264023` - prior NO-GO for dispatch orthogonality config/status CLI because a spec-derived focused dispatcher regression failed.
- `DELIB-20265273` - related Loyal Opposition review noting live dispatcher health was red while approving a narrower diagnostic fixture correction.
- `DELIB-20265026` - prior GO for Ollama provider failure fallback and backoff, adjacent to this proposal's runtime readiness/backoff surface.
- `DELIB-20263189` - owner authorization for dispatch/bridge reliability specs.

## Review Findings

No blocking findings.

### Confirmation C1 - The proposal targets a live failure class

Observation: live `gt bridge dispatch health --json` currently exits nonzero with `health_status: FAIL`. Findings include `loyal-opposition last_result=unchanged with pending_count=3`, `loyal-opposition:C last_result=unchanged with pending_count=3`, and `loyal-opposition:F last_result=provider_failure_backoff_active with pending_count=3`. The live `.gtkb-state/bridge-poller/dispatch-state.json` also records skipped Ollama readiness, OpenRouter provider backoff/process termination, and Antigravity spawn-rate limiting.

Impact: the proposal is not speculative. Loyal Opposition work is pending while the dispatch runtime is degraded, and the current status/health surface is the correct place to make that condition explicit and testable.

Required implementation evidence: the implementation report must include fresh `gt bridge dispatch status --json`, `gt bridge dispatch health --json`, and dispatch-state excerpts. If runtime health remains red for provider/account reasons after the code repair, the report must label that as residual operational blocker rather than claiming the dispatcher is fully healthy.

### Confirmation C2 - Target paths and test mapping are sufficient for the proposed scope

Observation: target-path coverage is clean. The proposal includes the status/health implementation file, the cross-harness dispatcher, the two harness adapters whose failure classes are cited, the manual scan helper, dispatcher rules, and focused regression tests for dispatch config, trigger behavior, Ollama, and OpenRouter.

Impact: Prime Builder can implement the proposed runtime-readiness behavior without needing to mutate undeclared source paths. The scan-helper path covers the manual scan discrepancy explicitly called out in the proposal.

Required implementation evidence: final diff review must remain inside the declared paths. If implementation discovers that another source path is required, Prime Builder must revise the proposal instead of expanding scope silently.

### Confirmation C3 - Stricter health is the correct product behavior, not a regression

Observation: the proposal explicitly accepts that health may become stricter and surface dispatch degradation more often. That matches `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `DCL-DISPATCH-ENVELOPE-RULES-001`, and the prior dispatch-health NO-GO history: false-green health is worse than a visible red operational blocker.

Impact: this GO authorizes fail-loud health/status behavior for pending work when selected/fallback LO targets are unavailable or recently failed. It does not authorize muting the provider failures or changing credentials/accounts to make the health command pass.

Required implementation evidence: tests must cover at least readiness failure, provider backoff, spawn-rate limiting or all-target-blocked/fallback exhaustion, no-verdict/dead-process evidence, and archived-row exclusion or separate labeling.

## Scope Conditions

- Keep the implementation inside the declared target paths.
- Do not restore the retired OS poller or retired smart poller.
- Do not perform provider credential lifecycle work, provider account changes, production deployment, or external service mutation.
- Preserve historical/archived bridge visibility while separating archived/excluded rows from live actionable rows.
- Keep runtime failure evidence non-secret and deterministic.
- Preserve the current bridge protocol: dispatcher/TAFE state plus status-bearing numbered files remain authoritative.

## Required Implementation Evidence

Prime Builder's post-implementation report must include:

- implementation-start packet for this GO and the declared target paths;
- spec-to-test mapping for every linked specification in `-001`;
- focused tests for dispatch config/status health, cross-harness runtime/fallback state, Ollama readiness/failure classification, OpenRouter provider/backoff/no-verdict handling, and manual scan/archive-aware alignment;
- separate `ruff check` and `ruff format --check` results for changed Python files;
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatch-runtime-health-readiness-repair`;
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dispatch-runtime-health-readiness-repair`;
- fresh `gt bridge dispatch status --json`, `gt bridge dispatch health --json`, and relevant dispatch-state evidence;
- a residual-risk section for any provider/account/runtime blocker that remains after code repair.

## Commands Executed

```powershell
python .claude/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-dispatch-runtime-health-readiness-repair --format json --preview-lines 240
Get-Content -Raw bridge/gtkb-dispatch-runtime-health-readiness-repair-001.md
python scripts\bridge_claim_cli.py status gtkb-dispatch-runtime-health-readiness-repair
python -m groundtruth_kb.cli backlog list --id WI-4578 --json
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-dispatch-runtime-health-readiness-repair
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-dispatch-runtime-health-readiness-repair
python -m groundtruth_kb.cli deliberations search "WI-4578 dispatch runtime health readiness repair bridge dispatch" --limit 10 --json
python .claude\skills\verify\helpers\write_verdict.py --slug gtkb-dispatch-runtime-health-readiness-repair --body-file .gtkb-state\bridge-verdict-drafts\gtkb-dispatch-runtime-health-readiness-repair-002-body.md
python -m groundtruth_kb.cli bridge dispatch status --json
python -m groundtruth_kb.cli bridge dispatch health --json
python scripts\proposal_target_paths_coverage_preflight.py --content-file bridge\gtkb-dispatch-runtime-health-readiness-repair-001.md --json
Get-Content -Raw .gtkb-state\bridge-poller\dispatch-state.json
rg -n "dispatch health|health_status|selected_by_role|bridge dispatch|dispatch status|def .*health|def .*status|archive|archived|blocked_non_activatable|scan_bridge" groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py scripts/cross_harness_bridge_trigger.py .claude/skills/bridge/helpers/scan_bridge.py scripts/ollama_harness.py scripts/openrouter_harness.py config/dispatcher/rules.toml platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py
```

## Final Decision

GO. The proposal passes the mandatory bridge gates, cites the governing dispatch and bridge specifications, has clean target-path coverage, is tied to open P1 WI-4578, and addresses a live dispatcher runtime-readiness defect without asking to mutate credentials, provider accounts, production deployment state, or retired poller infrastructure.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
