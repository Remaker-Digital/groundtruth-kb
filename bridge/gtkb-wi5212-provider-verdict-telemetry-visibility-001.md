NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; build activity; full GT-KB governance

# WI-5212 Defect-Fix Proposal - Record Governed Provider Verdict Tools In Dispatch Telemetry

bridge_kind: prime_proposal
Document: gtkb-wi5212-provider-verdict-telemetry-visibility
Version: 001
Date: 2026-07-12 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5212-TELEMETRY-ALLOWLIST-20260712
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5212
target_paths: ["groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py", "platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py"]

## Claim

Add `PublishBridgeVerdict` to the canonical shim-dispatch telemetry tool-name
allowlist and lock the privacy boundary with focused tests. Provider-backed
verdict publication attempts and successes will then contribute exact name and
count evidence without serializing arguments, document paths, verdict text,
tool results, prompts, messages, or provider bodies.

No envelope field, schema version, dispatch route, harness allowance, stop
reason, role authority, or outcome contract changes.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001`
already requires truthful canonical tool-name accounting and prohibits tool
arguments, results, prompts, messages, provider bodies, credentials, and
environment values from the persisted envelope. WI-5212 applies that existing
contract to the newly governed `PublishBridgeVerdict` name; it creates no new
telemetry field, policy, or authority boundary.

## Defect / Reproduction

`groundtruth_kb.shim_dispatch_telemetry.CANONICAL_TOOL_NAMES` currently contains
only `Read`, `Write`, `Edit`, `Grep`, `Glob`, and `Bash`. WI-5210 introduced the
governed high-level `PublishBridgeVerdict` provider tool. Genuine Alibaba H run
`2026-07-12T12-54-40Z-loyal-opposition-H-7d8f71` invoked that route, but the
telemetry observer filtered its name out before incrementing the per-turn and
aggregate counters. The omission made a governed publication attempt invisible
even though the telemetry schema is explicitly intended to provide truthful
tool-usage evidence.

The defect is deterministic: pass `PublishBridgeVerdict` alongside a known
tool name to `ShimDispatchTelemetryObserver.record_turn`; the known name is
counted and the governed verdict tool is silently discarded.

## In-Root Placement Evidence

Both target paths are inside `E:\GT-KB`. No adopter application, runtime JSON,
lease, lock, routing, credential, or deployment path is in scope.

## Specification Links

- `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` - owns canonical tool-name
  accounting and the strict prohibited-content privacy contract.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - genuine provider proof requires
  truthful operational evidence, including governed publication attempts.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` - the shared cloud provider route emits the
  tool name consumed by this common telemetry observer.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - telemetry remains observational and
  cannot alter centralized dispatch selection or outcomes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires the proposal, GO, report, and
  independent verdict lifecycle used for this protected change.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - require the concrete
  specification, project, work-item, PAUTH, and target-path linkage above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed
  name/count and privacy regressions before VERIFIED.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserve the live H observation as a
  separately governed defect and focused patch.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `GOV-STANDING-BACKLOG-001` -
  keep the change in GT-KB platform scope and bind it to existing WI-5212 /
  TEST-11366 rather than duplicate work.

## Prior Deliberations

- `DELIB-202666173` - owner directive to correct every defect discovered during
  genuine A/B/C/D/F/H proof.
- `DELIB-202666136`, `DELIB-202666133`, `DELIB-202666134`, and
  `DELIB-202666135` - independent WI-5173 telemetry reviews establishing the
  canonical-name, privacy, and observational-failure boundaries.
- `bridge/gtkb-wi5210-provider-lo-governed-verdict-publication-006.md` -
  VERIFIED introduction of the governed provider verdict tool whose telemetry
  name is currently omitted.

## Owner Decisions / Input

- `DELIB-202666173` authorizes correction of every defect found during the
  active six-harness proof cycle.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5212-TELEMETRY-ALLOWLIST-20260712`
  is the bounded implementation authorization. It forbids payload capture,
  allowance changes, runtime-state edits, routing, credentials, deployment,
  and unrelated work.
- No new owner decision is required.

## Proposed Scope

1. Add the exact string `PublishBridgeVerdict` to
   `CANONICAL_TOOL_NAMES`. Do not alter observer structure, envelope fields,
   schema version, size bounds, or serialization.
2. Extend the focused telemetry test to include repeated
   `PublishBridgeVerdict` calls and assert exact total/by-name counts.
3. Supply sensitive-looking tool arguments and verdict content only as inputs
   to the observer-facing test seam, then assert none appears in the serialized
   envelope. The telemetry implementation must continue receiving/storing only
   allowlisted names, never payloads.
4. Keep all original six canonical tool names and unknown-name filtering
   behavior unchanged.

## Cross-Harness Disposition

| Harness | Disposition |
| --- | --- |
| Codex A | No runtime tool-route change; A benefits only when reading shared telemetry. |
| Claude Code B | No runtime tool-route change; native Claude verdict publication remains outside shim telemetry. |
| Antigravity C | No runtime tool-route change. |
| Ollama D | Shared telemetry will count the name once WI-5211 projects governed publication to D. |
| OpenRouter F | Shared telemetry will count the name once WI-5211 projects governed publication to F. |
| Alibaba H | Immediate affected producer; genuine H runs already emit `PublishBridgeVerdict`. |

No harness-specific waiver is required. D/F/H retain 600 turns, 900-second
operations, 28,800-second sessions, and 29,400-second worker lifetimes.

## Specification-Derived Verification Plan

| Requirement | Automated evidence |
| --- | --- |
| Canonical name/count truthfulness | Record turns containing `PublishBridgeVerdict` plus original names; assert exact per-name and total counts. |
| Privacy | Serialize the envelope and assert tool arguments, paths, verdict content, prompts, and provider bodies are absent. |
| Compatibility | Assert all original six names remain countable and unknown names remain filtered. |
| Schema/outcome stability | Assert schema identifier and surrounding telemetry envelope remain unchanged; run the existing focused telemetry suite. |
| Quality | Run Ruff check and Ruff format check on both changed Python files. |

Commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py
```

## Acceptance Criteria

- `PublishBridgeVerdict` contributes exact telemetry counts.
- Original canonical names and unknown-name filtering remain unchanged.
- No argument, path, verdict content, prompt/message, result, provider body,
  credential, or environment value enters persisted telemetry.
- Schema, dispatch outcome, bridge behavior, routing, and generous allowances
  remain unchanged.
- Focused tests and both Ruff gates pass.
- Independent Loyal Opposition returns VERIFIED and creates one focused commit.

## Risks / Rollback

The risk is accidentally broadening telemetry from names to payloads. The
implementation is limited to one allowlist constant, and the regression scans
the serialized envelope for prohibited content. Rollback removes the single
name and its tests; no migration, dispatcher change, or runtime cleanup is
required. Bridge history remains append-only.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py`
- `platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py`

## Recommended Commit Type

`fix`

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
