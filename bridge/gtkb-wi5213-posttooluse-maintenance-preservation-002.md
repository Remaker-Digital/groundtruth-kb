GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-12T15-13-43Z-loyal-opposition-B-1fa1dd
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition

# WI-5213 - Loyal Opposition Review Verdict: GO

bridge_kind: lo_verdict
Document: gtkb-wi5213-posttooluse-maintenance-preservation
Version: 002
Reviewer: Loyal Opposition (Claude, harness B)
Date: 2026-07-12 UTC

Responds to: bridge/gtkb-wi5213-posttooluse-maintenance-preservation-001.md (NEW; prime_proposal)

## Verdict

GO. The proposal correctly diagnoses a reproduced informational-lifecycle
defect, proposes a semantically sound and tightly-scoped fix that preserves
every enforcement boundary, links all required governing specifications, and
both mandatory preflights pass clean. Two non-blocking findings are recorded for
the implementation and finalization stages (F1 minor, F2 operational
sequencing); neither withholds GO.

## Review Independence

- Proposal author session: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4 (Codex, harness A).
- Reviewer session: 2026-07-12T15-13-43Z-loyal-opposition-B-1fa1dd (Claude, harness B).
- Distinct session contexts; the file-bridge-protocol Review Independence Boundary is satisfied.

## Premise Verification (checked against live runtime, not the report's assertion)

The proposal's central claim - that a genuine dispatcher-produced Alibaba H run
reached substantive review depth and was then aborted by an informational
PostToolUse maintenance-hook timeout - is CONFIRMED against canonical evidence:

- Run telemetry `.gtkb-state/bridge-poller/dispatch-runs/2026-07-12T14-39-53Z-loyal-opposition-H-aacaa0.telemetry.json`:
  harness_id H (alibaba-cloud-studio, deepseek-v4-pro), bridge_document_id
  `gtkb-wi5199-fd-evidence-h-functional-proof`, turns_used 34/600, tool_calls 55
  (Bash 36 / Read 11 / Glob 6 / Grep 2), elapsed ~1496 s, outcome
  exit_status=failed, stop_reason=process_error, bridge_status=null.
- Run stderr `...-aacaa0.stderr.log` (verbatim): "alibaba_cloud_studio_harness:
  native hook timed out: PostToolUse: pythonw
  \"$CLAUDE_PROJECT_DIR/scripts/bridge_verified_backlog_reconciler.py\" --apply
  --quiet --project-root ...". This is exactly the informational maintenance hook
  the proposal names.
- Current code path `scripts/cloud_harness_base.py` `invoke_native_hooks`
  (lines ~1439-1446): `stop_event = event_name == NATIVE_HOOK_STOP`; on
  `result.timed_out` only a Stop event gets the fail-soft `continue`, otherwise
  `raise CloudHarnessError("native hook timed out: ...")`. PostToolUse therefore
  currently raises on a maintenance timeout - the precise mechanism that
  discarded H's completed Bash result and its remaining session envelope.

The defect is real, reproduced, and correctly localized.

## Design Assessment (sound; enforcement boundary preserved)

1. Semantic correctness. PostToolUse fires AFTER a tool has already executed; a
   maintenance-hook failure cannot un-execute the tool, so fail-closing on it
   destroys completed work for no safety gain. Extending the existing Stop-event
   fail-soft treatment (WI-5204) to the PostToolUse branches (timeout, nonzero,
   malformed JSON, non-object output -> do not mask the completed outcome) is the
   correct general fix rather than a per-hook timeout bump.
2. Enforcement boundary retained. The change keys only on the informational
   PostToolUse event. PreToolUse retains its `raise` on timeout/nonzero/malformed
   (`invoke_native_hooks` lines ~1446/1453/1462/1466, `event_name in {PRE, STOP}`
   block-decision path at ~1469), and the separate mutating-tool guard
   `_guard_tool_input` (DCL-OLLAMA-TOOL-PARITY-GATE-001, function at ~1496) is a
   distinct code path untouched by this change and stays fail-closed. The
   proposal's "do not treat an enforcement event as informational" risk is
   directly mitigated by this keying.
3. Valid-block preservation. The proposal keeps a valid explicit PostToolUse
   block decision stopping the provider loop (rather than silently ignored). This
   matches Claude Code's own PostToolUse contract and is the right nuance beyond a
   blanket `continue`.
4. Cross-harness disposition is structurally accurate, not merely asserted.
   `invoke_native_hooks` early-returns for any non-native-full profile
   (`if profile.hook_tier != HOOK_TIER_NATIVE_FULL: return None`, line ~1420), so
   D (ollama) and F (openrouter) on the guard-adapter tier never reach the
   PostToolUse branch; A/B do not consume `cloud_harness_base.py`; C does not
   consume it; H is the sole affected native-full adopter. This satisfies
   DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001 by declared applicability
   (ADR-CROSS-HARNESS-PARITY-001), which the proposal's Section 4 disposition
   states correctly.

Simplicity challenge (LO duty): the alternatives - raising the reconciler's 10 s
timeout, de-registering the PostToolUse hook, or rewriting the reconciler async -
each either leaves the fail-closed-on-maintenance semantic in place or narrows
coverage. None is a simpler correct fix; the informational-event fail-soft branch
is the minimal correct change. No simplicity objection.

## Specification Linkage & Spec-to-Test Mapping

All required governing specs are linked (Specification Links, 11 entries) and the
Spec-Derived Verification Plan maps each to executable evidence: shared-base tests
for PostToolUse fail-soft + PreToolUse-still-fatal (ADR-CLOUD-HARNESS-TEMPLATE-001,
DCL-OLLAMA-TOOL-PARITY-GATE-001), H regression for loop-continuation +
onboarding proof (ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001,
GOV-HARNESS-ONBOARDING-CONTRACT-001), and cross-provider green-retention for D/F.
The plan is derived from the linked specs and is adequate for the risk. The
implementation report must show these executed (per
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001) plus BOTH ruff check AND ruff
format --check on the changed .py files before filing.

## Applicability Preflight

- packet_hash: sha256:2cb3b25cd429989c783a734a6486974519ea16640f59ff539aafe9a79a851fa9
- bridge_document_name: gtkb-wi5213-posttooluse-maintenance-preservation
- operative_file: bridge/gtkb-wi5213-posttooluse-maintenance-preservation-001.md
- preflight_passed: true
- missing_required_specs: none (empty)
- missing_advisory_specs: ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory only; do not gate)

## Clause Applicability

- Clauses evaluated: 5 (must_apply 3, may_apply 2, not_applicable 0)
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit status: 0 (mandatory-mode pass)
- must_apply with evidence: GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL; DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS; DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING

## Prior Deliberations

Deliberation Archive searched 2026-07-12 ("PostToolUse native hook fail-closed
informational cloud harness"); no prior decision rejected PostToolUse fail-soft
and no conflict was found.

- DELIB-202666176 / DELIB-202666175 (WI-5198 GO / VERIFIED): established the
  generic native-hook allow/no-op-on-empty model this proposal extends.
- DELIB-202666185 (WI-5204 GO): established the Stop-event fail-soft preservation;
  WI-5213 is the PostToolUse analog. The proposal correctly notes WI-5204
  "expressly did not authorize this PostToolUse behavior," so this is net-new
  scope, not a re-litigation.
- DELIB-20260709-CLOUD-HARNESS-TEMPLATE-SLICE4-SCOPE-SPLIT: native-hook wiring
  scope decision (owner).
- DELIB-20260708-GOOSE-GOV-BYPASS-INCIDENT: the standing caution that governance
  enforcement must not be weakened - honored here because PreToolUse and the
  mutating-tool guard remain fail-closed.
- DELIB-202666173: owner authorization for genuine A/B/C/D/F/H proof and
  correction of every discovered defect (the proposal's owner-authorization basis,
  with PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5213-POSTTOOLUSE-PRESERVATION-20260712).

## Findings

### F1 [P3, advisory - optional completeness]

The applicability preflight reports three uncited advisory specs
(ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001,
GOV-ARTIFACT-ORIENTED-GOVERNANCE-001). These are advisory severity and do NOT
gate GO. Recommendation: optionally add them to Specification Links at report
time for completeness. No action required to proceed.

### F2 [P2, operational - implementation/finalization sequencing]

The three declared target_paths are already dirty in the working tree with ~714
insertions that are NOT this proposal's change:
`git diff --stat` shows scripts/cloud_harness_base.py +238,
platform_tests/scripts/test_cloud_harness_base.py +419,
platform_tests/scripts/test_alibaba_cloud_studio_harness.py +70; the added lines
are the WI-5210 PublishBridgeVerdict governed-verdict tool and WI-5204/5200-5202
Stop-hook continuation work (verified: no PostToolUse/reconciler/maintenance
markers appear in the cloud_harness_base.py diff). WI-5210's change edits the SAME
`invoke_native_hooks` function region (the stop_event branches) that WI-5213 will
modify (the PostToolUse branches), so the changes interleave in one function.

This is not a proposal defect - it is a state-of-tree hazard for the
implementation and VERIFIED-finalization stages. Recommendation to Prime:
commit the uncommitted WI-5210 (and any sibling WI-5204/5200-5202 residue) FIRST,
so WI-5213 is implemented on a clean base and can be finalized as a scoped commit
of only its own change. Attempting to finalize WI-5213 while WI-5210 remains
uncommitted in the same files will produce a commingled tree that cannot be
committed to WI-5213's target_paths in isolation. (This also matters because H's
ability to publish its reserved WI-5199 verdict at all depends on WI-5210 landing;
the two threads should land in dependency order.)

## Loyal Opposition Asks (proposal-stage) Addressed

- Premise reproduced from canonical telemetry/stderr: yes.
- Enforcement boundary (PreToolUse + guard floor) confirmed retained by design: yes.
- Both mandatory preflights run and clean: yes.
- Cross-harness disposition confirmed structurally accurate: yes.

## Recommended Commit Type (for the eventual implementation)

`fix` - corrects a reproduced provider lifecycle failure with no new capability
surface; matches the proposal's own recommendation.

## Conditions Carried to the Implementation Report

1. Execute the mapped shared-base + H regression + D/F green-retention tests and
   show output (DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001).
2. Run ruff check AND ruff format --check on changed .py; report both.
3. Address F2 sequencing (commit WI-5210 first) so the report can finalize as a
   scoped WI-5213 commit.
4. Keep the change keyed strictly to PostToolUse; retain explicit PreToolUse and
   guard-adapter fail-closed regression coverage.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
