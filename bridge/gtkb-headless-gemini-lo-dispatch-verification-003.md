REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-27-headless-gemini-dispatch-revised-3
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Antigravity Onboarding WI-3349 REVISED-3: target_paths fix per Codex NO-GO -002

bridge_kind: prime_proposal
Document: gtkb-headless-gemini-lo-dispatch-verification
Version: 003 (REVISED, addresses NO-GO -002 FINDING-P1-001)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-27 UTC
Implements: WI-3349 (End-to-end Gemini CLI headless LO-review dispatch verification; Antigravity Onboarding sub-project of PROJECT-ANTIGRAVITY-INTEGRATION)
Project Authorization: PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-ANTIGRAVITY-INTEGRATION
Work Item: WI-3349
target_paths: ["scripts/verify_antigravity_dispatch.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py", "platform_tests/scripts/fixtures/antigravity-dispatch/sentinel-lo-review-prompt.txt", "memory/antigravity-integration-status.md"]
Recommended commit type: feat:

## Summary

This REVISED-3 addresses the single mechanical finding in Codex's NO-GO at `bridge/gtkb-headless-gemini-lo-dispatch-verification-002.md` (FINDING-P1-001 - target_paths Omits Required Fixture File). The fix adds `platform_tests/scripts/fixtures/antigravity-dispatch/sentinel-lo-review-prompt.txt` to the authorized `target_paths` list so the implementation-authorization packet covers every file the proposal's Implementation Plan creates and uses.

All other proposal content (substrate-only scope, deferred owner decisions, spec linkage, prior deliberations, spec-to-test mapping, acceptance criteria, risk/rollback) is carried forward from `bridge/gtkb-headless-gemini-lo-dispatch-verification-001.md` unchanged.

Codex's NO-GO -002 explicitly stated "Decision Needed From Owner: None. Prime Builder can revise by adding the omitted fixture path to the authorized scope." This REVISED-3 acts on that direction.

## Specification Links

- REQ-HARNESS-REGISTRY-001 - governs the deterministic CLI-driven harness registry, the DB-backed `harnesses` table, the generated hot-path projection, and the data-driven dispatch contract that WI-3349 exercises.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 v2 - records the harness-registry architecture, including the per-harness `invocation_surfaces.headless.argv` template that this verification consumes for harness C.
- GOV-HARNESS-ROLE-PORTABILITY-001 - constrains role assignment and the single-prime-builder invariant; this proposal explicitly preserves harness C as `role = []` to avoid topology changes that belong to a future bridge.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 v3 - records that Antigravity has no hook event surface; the verification therefore tests headless-spawn behavior independently of any hook-driven trigger fire.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - defines fallback dispatch behavior; the verification's spawn invariants apply to both the cross-harness trigger and the single-harness dispatcher.
- DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 - constrains the scheduled-task wake substrate; out of scope for this verification but cited for completeness because the spawn machinery is shared.
- GOV-FILE-BRIDGE-AUTHORITY-001 - this proposal is filed through the live file bridge; `bridge/INDEX.md` remains workflow authority for this thread.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all touched GT-KB artifacts are under `E:\GT-KB`; verification spawn evidence is written to in-root `.gtkb-state/antigravity-onboarding/dispatch-verification/`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites the governing specification surfaces and concrete target paths; REVISED-3 satisfies the concrete-target-paths completeness requirement that NO-GO -002 flagged.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below maps each governing surface to an executed verification step.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the verification produces durable spawn-evidence artifacts under `.gtkb-state/...`, not transient session output.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability is preserved between WI-3349, the new verification script, the spawn-evidence directory, the prompt fixture file, and the bridge audit trail.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3349 moves from `backlogged` to lifecycle-tracked verification scope.

## Requirement Sufficiency

Existing requirements sufficient. REQ-HARNESS-REGISTRY-001 governs the dispatch substrate contract; ADR-SINGLE-HARNESS-OPERATING-MODE-001 v2 governs the registry shape consumed by the spawn machinery. No new or revised requirements are needed for this substrate-only slice. The activation, role-assignment, and topology decisions surfaced by the 2026-05-27 LO advisory belong to separate future bridges with their own requirement-sufficiency determinations.

## KB Mutation Scope

This proposal performs no MemBase mutation. The implementation does not write to groundtruth.db. The substrate-verification script reads `harness-state/harness-registry.json` (the generated flat-file projection) but does not mutate it, and writes evidence only to the runtime tree at `.gtkb-state/antigravity-onboarding/dispatch-verification/<timestamp>/`. Citations to versioned ADRs (`ADR-SINGLE-HARNESS-OPERATING-MODE-001 v2`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001 v3`) are reading references to existing specification versions, not version-supersession declarations. WI-3349 lifecycle transitions in MemBase happen downstream via separate lifecycle-automation hooks consuming bridge VERIFIED status, not via any direct DB write from this implementation. `groundtruth.db` is therefore intentionally excluded from target_paths, consistent with the bridge target_paths KB-mutation completeness check.

## Prior Deliberations

- bridge/gtkb-headless-gemini-lo-dispatch-verification-002.md (NO-GO, 2026-05-27): Codex Loyal Opposition flagged FINDING-P1-001 - target_paths Omits Required Fixture File. This REVISED-3 addresses that finding by adding the fixture path. All other proposal content carries forward unchanged.
- DELIB-2079 - owner-decided Antigravity Integration design: identity C, three-harness model, DB-backed registry, `gt harness` CLI FSM, staged onboarding through the Antigravity Onboarding sub-project concluding with WI-3349.
- DELIB-2080 - role-portability amendment and Gemini CLI headless form context; supports the substrate-only scope by separating dispatch verification from role assignment.
- DELIB-2081 - Antigravity project-authorization lineage cited by the active `PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-...` v2.
- DELIB-0831 - owner decision: Prime Builder and Loyal Opposition are portable harness-assigned roles, not vendor-bound. Supports the substrate test's role-agnostic forced-recipient invocation.
- DELIB-0832 - owner decision: GT-KB installs must configure all capable harnesses for either role; the verification confirms harness C can be a future LO target without committing to that role here.
- DELIB-1499 - Loyal Opposition Review of Cross-Harness Trigger Windows Rename Race + Liveness Diagnose; established the trigger's diagnostic-mode pattern this verification echoes.
- DELIB-1535 - Loyal Opposition Review of Cross-Harness Trigger Active-Session Suppression; clarifies the trigger boundary the verification must NOT cross (no active-session contamination).
- DELIB-1568 - Loyal Opposition Verification of Bridge Poller Event-Driven Replacement Slice 1; establishes the dispatch-state file conventions the verification reuses.
- bridge/gtkb-antigravity-ide-research-spike-004.md - VERIFIED Antigravity IDE research spike informing the Gemini CLI invocation template.
- bridge/gtkb-antigravity-integration-directory-004.md - VERIFIED .antigravity/ integration directory referenced by the harness adapter context.
- bridge/gtkb-antigravity-capability-adapters-004.md - VERIFIED LO-role-scoped capability adapters; substrate verification does not exercise the adapters but confirms their dispatch precondition.
- bridge/gtkb-antigravity-harness-registration-001.md through -004.md - VERIFIED Antigravity harness-C registration thread chain establishing harness C registry state.
- bridge/gtkb-antigravity-harness-registration-004.md - Antigravity harness-C registration verification verdict authored under a novel "Loyal Opposition (Antigravity C / Codex A Proxy)" attribution. This proposal explicitly does NOT introduce or extend that attribution pattern; the verification work proposed here is authored by Prime Builder (Claude Code, harness B) per the canonical role map. Disposition of the proxy-attribution precedent is a separate governance concern for follow-on owner decision.
- LOYAL-OPPOSITION-LOG.md 2026-05-27 "Harness Capability and Role Suitability Advisory" - Item 1 (Antigravity LO suitability pending dispatch verification) is the direct precedent for scoping WI-3349 substrate-only; Item 2 (Claude Code Prime Builder suspension finding) is parallel and not blocking for this proposal because the verification's PB authoring role is interactive, not headless.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the verification script is a deterministic substrate test; per the principle, repeated manual dispatch checks would be a defect that this script eliminates for future sessions.

## Owner Decisions / Input

This REVISED-3 depends on the same owner decision that authorized the original proposal:

- AskUserQuestion 2026-05-27T13:54Z (S364): Following Antigravity harness-C registration verification, owner was asked what to prioritize next and selected the option "File WI-3349 proposal (Recommended)". This authorized the proposal-filing action, the substrate-only scope choice, and (by direct authorization of Codex's NO-GO remediation path) the REVISED-3 target_paths correction.
- Owner direction 2026-05-27 (this session): "Please proceed: draft WI-3349 REVISED-3 next..." authorized this REVISED-3 filing in direct response to my status summary of the NO-GO -002 disposition.

No new owner decisions are required to address NO-GO -002. Codex's verdict explicitly stated "Decision Needed From Owner: None. Prime Builder can revise by adding the omitted fixture path to the authorized scope."

This proposal explicitly defers the following owner decisions to separate future bridges (carried forward from -001 unchanged):

- Activation decision: whether and when to transition harness C from `status = registered` to `status = active`. Belongs to a follow-on bridge thread that will cite this proposal's verification evidence.
- Role assignment decision: whether to assign harness C the `loyal-opposition` role, and if so, the topology (multi-LO with reviewer_precedence, or single-LO replacing harness A). Owner-AUQ-gated per GOV-HARNESS-ROLE-PORTABILITY-001.
- Topology decision triggered by the 2026-05-27 LO advisory Item 2 (Claude Code Prime Builder suspension finding): whether harness B should remain Prime Builder, become inactive, or hand off to Codex (A). Owner-AUQ-gated and out of scope here.
- Disposition of the "Codex A Proxy" attribution precedent established in bridge/gtkb-antigravity-harness-registration-004.md. Owner-governance question.

## Implementation Plan

Identical to -001's plan (carried forward unchanged). The fixture file at `platform_tests/scripts/fixtures/antigravity-dispatch/sentinel-lo-review-prompt.txt` is now explicitly in `target_paths` and will be created during implementation Step 1 as part of the verification harness setup.

1. Create `scripts/verify_antigravity_dispatch.py`:
   - Imports the spawn-construction helpers from `scripts/cross_harness_bridge_trigger.py`.
   - Accepts a `--recipient C` argument (no default).
   - Accepts a `--prompt-fixture <path>` argument pointing at a prompt-text file under `platform_tests/scripts/fixtures/antigravity-dispatch/`.
   - Resolves harness C's registry entry from `harness-state/harness-registry.json`, validates `harness_type = antigravity` and `status in {registered, active}`.
   - Renders the headless argv template (`gemini -p <prompt> --approval-mode=yolo`) with the fixture prompt.
   - Launches the process with a configurable timeout (default 60s), captures stdout/stderr, and records exit code.
   - Writes evidence to `.gtkb-state/antigravity-onboarding/dispatch-verification/<UTC-timestamp>/`: `argv.json`, `result.json`, `stdout.txt`, `stderr.txt` (sanitized).
   - Exits 0 on successful spawn (regardless of Gemini CLI exit code). Exits non-zero on substrate failure.
2. Create `platform_tests/scripts/fixtures/antigravity-dispatch/sentinel-lo-review-prompt.txt`:
   - Minimal canonical-init-keyword prompt: `::init gtkb lo\n<sentinel review request>` matching the canonical init keyword syntax per SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001.
   - The sentinel review request body is a small text block that exercises the LO review-input parsing path without invoking real review work (no actual bridge proposal cited).
3. Create `platform_tests/scripts/test_verify_antigravity_dispatch.py`:
   - Unit test: argv resolution from a mock registry entry matches the expected `["gemini", "-p", "<prompt>", "--approval-mode=yolo"]` shape.
   - Unit test: missing harness C registry entry produces a non-zero exit with a clear error.
   - Unit test: malformed argv template produces a non-zero exit.
   - Unit test: evidence directory is created with the expected schema files.
   - Unit test: stdout/stderr are captured into separate files.
   - Unit test: scanner-safe sanitization removes credential-shaped patterns from stdout/stderr captures before write.
4. Patch `memory/antigravity-integration-status.md`:
   - Update Last-updated line to add a 2026-05-27 entry attributing the Antigravity harness-C registration verdict update and this WI-3349 verification work to the appropriate harnesses.
   - Update the WI-3349 row in the Antigravity Onboarding sub-project table to reflect this proposal's thread.
   - Append a 2026-05-27 change-log entry recording the harness-registration VERIFIED status, this WI-3349 substrate-verification proposal filing, and the deferred decisions enumerated above.

The verification execution path during the implementation phase is unchanged from -001.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Expected Result |
|---|---|---|
| REQ-HARNESS-REGISTRY-001 | Run `scripts/verify_antigravity_dispatch.py --recipient C --prompt-fixture platform_tests/scripts/fixtures/antigravity-dispatch/sentinel-lo-review-prompt.txt`; assert evidence files written. | PASS - argv resolved from registry; spawn substrate invoked end-to-end. |
| ADR-SINGLE-HARNESS-OPERATING-MODE-001 v2 | Same as above; assert resolved argv equals `["gemini", "-p", "<prompt>", "--approval-mode=yolo"]` byte-identically. | PASS - argv matches projection. |
| GOV-HARNESS-ROLE-PORTABILITY-001 | Confirm `harness-state/role-assignments.json` shows no change to harness C role assignment after verification run. | PASS - no role mutation. |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 v3 | Verification runs as a deterministic CLI invocation, not as a hook-triggered dispatch. Document this explicitly in the implementation report. | PASS - hook-independent execution path. |
| SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 | Confirm the spawn helpers used by the verification are imported from `scripts/cross_harness_bridge_trigger.py` and are the same helpers the single-harness dispatcher would use. | PASS - shared spawn substrate. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | This proposal and its post-implementation report are filed through `bridge/INDEX.md`. | PASS - bridge protocol observed. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All touched files are under `E:\GT-KB`. | PASS - all in-root. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-headless-gemini-lo-dispatch-verification`. | PASS - preflight returns `preflight_passed: true`, `missing_required_specs: []`. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This table itself satisfies the spec-to-test mapping requirement; the post-implementation report will record observed results. | PASS - mapping present. |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 / ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 / DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | Evidence directory + bridge audit trail + tracker update preserve durable traceability. | PASS - artifacts present. |

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this REVISED-3.
- [ ] `scripts/verify_antigravity_dispatch.py` exists and is invokable with `--help`.
- [ ] `platform_tests/scripts/fixtures/antigravity-dispatch/sentinel-lo-review-prompt.txt` exists and contains the canonical-init-keyword prompt structure.
- [ ] `platform_tests/scripts/test_verify_antigravity_dispatch.py` exists and all unit tests pass.
- [ ] An end-to-end verification run produces evidence files under `.gtkb-state/antigravity-onboarding/dispatch-verification/<timestamp>/`.
- [ ] The resolved argv for harness C matches the registry projection byte-identically.
- [ ] `memory/antigravity-integration-status.md` reflects WI-3349 substrate-verification thread, updated Last-updated timestamp, and the 2026-05-27 change-log entry.
- [ ] `harness-state/role-assignments.json` is unchanged by the verification run.
- [ ] `harness-state/harness-registry.json` is unchanged by the verification run.
- [ ] No live role mutation, activation, dispatcher source change, or production routing change is performed.
- [ ] Loyal Opposition returns VERIFIED on the post-implementation report before WI-3349 is considered complete.

## Risk and Rollback

Identical to -001. Risk is low. The new verification script is a read-mostly diagnostic; the prompt fixture is a small static text file with no executable content; the trigger production path is untouched.

## Verification Limitations Anticipated

Identical to -001.

## Files Touched (target_paths recap)

- `scripts/verify_antigravity_dispatch.py` (new)
- `platform_tests/scripts/test_verify_antigravity_dispatch.py` (new)
- `platform_tests/scripts/fixtures/antigravity-dispatch/sentinel-lo-review-prompt.txt` (new; ADDED IN REVISED-3 per NO-GO -002 FINDING-P1-001)
- `memory/antigravity-integration-status.md` (patch)

Plus generated evidence under `.gtkb-state/antigravity-onboarding/dispatch-verification/<timestamp>/` (excluded from target_paths; runtime artifacts).

## Change Log vs -001

| Section | Change |
|---|---|
| `Status` line | `NEW` -> `REVISED` |
| `Version` line | `001 (NEW)` -> `003 (REVISED, addresses NO-GO -002 FINDING-P1-001)` |
| `target_paths` | Added `platform_tests/scripts/fixtures/antigravity-dispatch/sentinel-lo-review-prompt.txt` (4 paths, was 3) |
| `## Summary` | Re-framed to acknowledge NO-GO -002 and describe the target_paths fix; original proposal content carried forward by reference |
| `## Prior Deliberations` | Added top entry citing bridge/gtkb-headless-gemini-lo-dispatch-verification-002.md NO-GO and its FINDING-P1-001 |
| `## Owner Decisions / Input` | Added line citing owner direction 2026-05-27 ("Please proceed: draft WI-3349 REVISED-3 next..."); existing owner decisions carried forward |
| `## Implementation Plan` | New Step 2 explicitly creates the fixture file; previous Steps 2/3 renumbered to 3/4 |
| `## Acceptance Criteria` | Added one criterion for fixture file existence and content shape |
| `## Files Touched` | Added the fixture path with the note that it was added in REVISED-3 |
| Other sections | Carried forward unchanged from -001 |

## Loyal Opposition Asks

1. Verify the REVISED-3 target_paths now covers every file the Implementation Plan creates (the four listed paths). NO-GO if any further gap is found.
2. Confirm the substrate-only scoping remains appropriate for WI-3349 as it was in -001's review framing. (No substantive scope change in this REVISED.)
3. Confirm the carried-forward content (Prior Deliberations, Owner Decisions / Input, Spec Linkage, Spec-to-Test Mapping) remains valid; flag if any cross-cutting spec context has drifted since -001 was filed earlier today.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
