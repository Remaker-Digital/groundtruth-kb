NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-27-headless-gemini-dispatch-proposal
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Antigravity Onboarding WI-3349: End-to-end Gemini CLI headless LO-review dispatch verification (substrate-only scope)

bridge_kind: prime_proposal
Document: gtkb-headless-gemini-lo-dispatch-verification
Version: 001 (NEW)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-27 UTC
Implements: WI-3349 (End-to-end Gemini CLI headless LO-review dispatch verification; Antigravity Onboarding sub-project of PROJECT-ANTIGRAVITY-INTEGRATION)
Project Authorization: PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-ANTIGRAVITY-INTEGRATION
Work Item: WI-3349
target_paths: ["scripts/verify_antigravity_dispatch.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py", "memory/antigravity-integration-status.md"]
Recommended commit type: feat:

## Summary

This proposal verifies that the cross-harness event-driven trigger's spawn substrate can headlessly invoke harness C (Antigravity, Gemini CLI 0.42.0) per the registry-projected argv `["gemini", "-p", "{{PROMPT}}", "--approval-mode=yolo"]`, completing the final Antigravity onboarding slice (WI-3349) in PROJECT-ANTIGRAVITY-INTEGRATION.

Scope is deliberately substrate-only. The verification exercises the spawn machinery against a forced-recipient C invocation through a new test entrypoint at `scripts/verify_antigravity_dispatch.py`. It does NOT modify the production cross-harness trigger's role-based recipient selection, does NOT activate harness C (status remains `registered`), does NOT assign harness C an operating role (role remains `[]`), and does NOT change the multi-harness routing topology. Activation, role assignment, and end-to-end production review behavior are tracked as separate future bridge threads gated by owner decisions on topology that surface from the 2026-05-27 Loyal Opposition Harness Capability and Role Suitability Advisory.

The verification produces durable spawn evidence (argv constructed, process exit code, stderr/stdout sample, elapsed time) recorded under `.gtkb-state/antigravity-onboarding/dispatch-verification/<timestamp>/`. The substrate-only scope is sufficient to mark WI-3349 closed because the WI's verification objective is the dispatch substrate, not the activation/role/topology sequence the LO advisory queues for follow-on work.

## Specification Links

- REQ-HARNESS-REGISTRY-001 - governs the deterministic CLI-driven harness registry, the DB-backed `harnesses` table, the generated hot-path projection, and the data-driven dispatch contract that WI-3349 exercises.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 v2 - records the harness-registry architecture, including the per-harness `invocation_surfaces.headless.argv` template that this verification consumes for harness C.
- GOV-HARNESS-ROLE-PORTABILITY-001 - constrains role assignment and the single-prime-builder invariant; this proposal explicitly preserves harness C as `role = []` to avoid topology changes that belong to a future bridge.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 v3 - records that Antigravity has no hook event surface; the verification therefore tests headless-spawn behavior independently of any hook-driven trigger fire.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - defines fallback dispatch behavior; the verification's spawn invariants apply to both the cross-harness trigger and the single-harness dispatcher.
- DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 - constrains the scheduled-task wake substrate; out of scope for this verification but cited for completeness because the spawn machinery is shared.
- GOV-FILE-BRIDGE-AUTHORITY-001 - this proposal is filed through the live file bridge; `bridge/INDEX.md` remains workflow authority for this thread.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all touched GT-KB artifacts are under `E:\GT-KB`; verification spawn evidence is written to in-root `.gtkb-state/antigravity-onboarding/dispatch-verification/`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites the governing specification surfaces and concrete target paths.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below maps each governing surface to an executed verification step.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the verification produces durable spawn-evidence artifacts under `.gtkb-state/...`, not transient session output.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability is preserved between WI-3349, the new verification script, the spawn-evidence directory, and the bridge audit trail.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3349 moves from `backlogged` to lifecycle-tracked verification scope.

## Requirement Sufficiency

Existing requirements sufficient. REQ-HARNESS-REGISTRY-001 governs the dispatch substrate contract; ADR-SINGLE-HARNESS-OPERATING-MODE-001 v2 governs the registry shape consumed by the spawn machinery. No new or revised requirements are needed for this substrate-only slice. The activation, role-assignment, and topology decisions surfaced by the 2026-05-27 LO advisory belong to separate future bridges with their own requirement-sufficiency determinations.

## Prior Deliberations

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

This proposal depends on the following owner decisions:

- AskUserQuestion 2026-05-27T13:54Z (this session): Following Antigravity harness-C registration verification this session, owner was asked what to prioritize next and selected the option "File WI-3349 proposal (Recommended)". This authorizes the proposal-filing action and the substrate-only scope choice (including the tracker-staleness patch enumerated in target_paths).

This proposal explicitly defers the following owner decisions to separate future bridges:

- Activation decision: whether and when to transition harness C from `status = registered` to `status = active`. Belongs to a follow-on bridge thread that will cite this proposal's verification evidence.
- Role assignment decision: whether to assign harness C the `loyal-opposition` role, and if so, the topology (multi-LO with reviewer_precedence, or single-LO replacing harness A). Owner-AUQ-gated per GOV-HARNESS-ROLE-PORTABILITY-001.
- Topology decision triggered by the 2026-05-27 LO advisory Item 2 (Claude Code Prime Builder suspension finding): whether harness B should remain Prime Builder, become inactive, or hand off to Codex (A). Owner-AUQ-gated and out of scope here.
- Disposition of the "Codex A Proxy" attribution precedent established in bridge/gtkb-antigravity-harness-registration-004.md. Owner-governance question.

## Implementation Plan

1. Create `scripts/verify_antigravity_dispatch.py`:
   - Imports the spawn-construction helpers from `scripts/cross_harness_bridge_trigger.py` (the module exposes the argv-template-rendering and subprocess-launch functions used by the trigger's normal dispatch path; the verification reuses these helpers rather than reimplementing them, so substrate drift would be detected).
   - Accepts a `--recipient C` argument (no default; requires explicit recipient ID so the script cannot be accidentally invoked against a production routing target).
   - Accepts a `--prompt-fixture <path>` argument pointing at a prompt-text file under `platform_tests/scripts/fixtures/antigravity-dispatch/`; the fixture content is a minimal canonical-init-keyword prompt (`::init gtkb lo\n<sentinel review request>`).
   - Resolves harness C's registry entry from `harness-state/harness-registry.json`, validates `harness_type = antigravity` and `status in {registered, active}`, and refuses to proceed if the registry entry is missing or malformed.
   - Renders the headless argv template (`gemini -p <prompt> --approval-mode=yolo`) with the fixture prompt; logs the resolved argv to stderr for audit.
   - Launches the process with a configurable timeout (default 60s), captures stdout/stderr, and records exit code.
   - Writes evidence to `.gtkb-state/antigravity-onboarding/dispatch-verification/<UTC-timestamp>/`:
     - `argv.json` - the resolved argv list
     - `result.json` - exit code, elapsed seconds, stdout/stderr byte counts, capture timestamps
     - `stdout.txt`, `stderr.txt` - raw captures (sanitized for credentials per scanner-safe-writer patterns)
   - Exits 0 on successful spawn (regardless of Gemini CLI exit code; the verification objective is "the spawn substrate works", not "Gemini understands the prompt"). Exits non-zero on substrate failure (registry missing, argv template malformed, OSError during launch).
2. Create `platform_tests/scripts/test_verify_antigravity_dispatch.py`:
   - Unit test: argv resolution from a mock registry entry matches the expected `["gemini", "-p", "<prompt>", "--approval-mode=yolo"]` shape.
   - Unit test: missing harness C registry entry -> non-zero exit with a clear error.
   - Unit test: malformed argv template (e.g., `harness_type` mismatch) -> non-zero exit.
   - Unit test: evidence directory is created with the expected schema files.
   - Unit test: stdout/stderr are captured into separate files.
   - Unit test: scanner-safe sanitization removes credential-shaped patterns from stdout/stderr captures before write (per the scanner-safe-writer credential catalog).
3. Patch `memory/antigravity-integration-status.md`:
   - Update `**Last updated:** 2026-05-19 by Prime Builder (Codex, harness A)` line to add a 2026-05-27 entry attributing the Antigravity harness-C registration verdict update and this WI-3349 verification work to the appropriate harnesses.
   - Update the WI-3349 row in the Antigravity Onboarding sub-project table to reflect this proposal's thread.
   - Append a 2026-05-27 change-log entry recording (a) Antigravity harness-C registration thread reached VERIFIED under bridge/gtkb-antigravity-harness-registration-004.md (authored by Antigravity-as-Codex-proxy), (b) this WI-3349 substrate-verification proposal filing, (c) the deferred decisions enumerated above.

The verification execution path during the implementation phase:

1. Invoke `python scripts/verify_antigravity_dispatch.py --recipient C --prompt-fixture platform_tests/scripts/fixtures/antigravity-dispatch/sentinel-lo-review-prompt.txt --timeout 60`.
2. Confirm evidence files written.
3. Inspect `result.json` for exit code, elapsed time, and stdout/stderr byte counts.
4. If Gemini CLI returns non-zero exit (e.g., authentication required, no API key configured in the environment), record the observation as a Verification Limitation: substrate works, but live Gemini invocation requires upstream configuration not in scope for this slice.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Expected Result |
|---|---|---|
| REQ-HARNESS-REGISTRY-001 | Run `scripts/verify_antigravity_dispatch.py --recipient C --prompt-fixture <fixture>`; assert evidence files written. | PASS - argv resolved from registry; spawn substrate invoked end-to-end. |
| ADR-SINGLE-HARNESS-OPERATING-MODE-001 v2 | Same as above; assert resolved argv equals `["gemini", "-p", "<prompt>", "--approval-mode=yolo"]` byte-identically. | PASS - argv matches projection. |
| GOV-HARNESS-ROLE-PORTABILITY-001 | Confirm `harness-state/role-assignments.json` shows no change to harness C role assignment (still `role = []`) after verification run. | PASS - no role mutation. |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 v3 | Verification runs as a deterministic CLI invocation, not as a hook-triggered dispatch. Document this explicitly in the implementation report. | PASS - hook-independent execution path. |
| SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 | Confirm the spawn helpers used by the verification are imported from `scripts/cross_harness_bridge_trigger.py` and are the same helpers the single-harness dispatcher would use (subject to substrate sharing). | PASS - shared spawn substrate. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | This proposal and its post-implementation report are filed through `bridge/INDEX.md`. | PASS - bridge protocol observed. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All touched files (`scripts/verify_antigravity_dispatch.py`, `platform_tests/scripts/test_verify_antigravity_dispatch.py`, `memory/antigravity-integration-status.md`, evidence under `.gtkb-state/antigravity-onboarding/`) are under `E:\GT-KB`. | PASS - all in-root. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-headless-gemini-lo-dispatch-verification`. | PASS - preflight returns `preflight_passed: true`, `missing_required_specs: []`. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This table itself satisfies the spec-to-test mapping requirement; the post-implementation report will record observed results. | PASS - mapping present. |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 / ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 / DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | Evidence directory + bridge audit trail + tracker update preserve durable traceability. | PASS - artifacts present. |

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `scripts/verify_antigravity_dispatch.py` exists and is invokable with `--help`.
- [ ] `platform_tests/scripts/test_verify_antigravity_dispatch.py` exists and all unit tests pass via `python -m pytest platform_tests/scripts/test_verify_antigravity_dispatch.py -q`.
- [ ] An end-to-end verification run produces evidence files under `.gtkb-state/antigravity-onboarding/dispatch-verification/<timestamp>/`.
- [ ] The resolved argv for harness C matches the registry projection byte-identically.
- [ ] `memory/antigravity-integration-status.md` reflects WI-3349 substrate-verification thread, updated Last-updated timestamp, and the 2026-05-27 change-log entry.
- [ ] `harness-state/role-assignments.json` is unchanged by the verification run.
- [ ] `harness-state/harness-registry.json` is unchanged by the verification run.
- [ ] No live role mutation, activation, dispatcher source change, or production routing change is performed.
- [ ] Loyal Opposition returns VERIFIED on the post-implementation report before WI-3349 is considered complete.

## Risk and Rollback

Risk is low. The new verification script is a read-mostly diagnostic that consumes the harness registry projection, renders an argv, and launches a subprocess. The trigger production path is untouched. Evidence files are written to `.gtkb-state/...` which is excluded from regression-gate canonical state.

Potential failure modes:
- Gemini CLI authentication or environment configuration may cause the spawned process to exit non-zero. This does not invalidate substrate verification because the substrate objective is "the spawn happens correctly", not "Gemini understands the sentinel prompt." The post-implementation report will record any such observation as a Verification Limitation, and a follow-on Antigravity-environment-configuration bridge thread may be filed if needed.
- The Gemini CLI may produce credential-shaped output (API keys, tokens) in stdout/stderr. Per scanner-safe-writer patterns, the script sanitizes captures before writing to evidence files. The unit test suite includes a sanitization-coverage test.
- The script may interact unfavorably with concurrent cross-harness trigger runs. Mitigation: the script uses a unique evidence-directory timestamp per invocation and does not touch dispatch-state files used by the trigger.

Rollback: delete the new script, the new test file, and the tracker patch. No DB or projection mutation occurred.

## Verification Limitations Anticipated

- Substrate verification does NOT verify that Antigravity (Gemini CLI) can author a meaningful LO review verdict file. Production verdict authoring requires harness C to be activated, role-assigned, and routed by the production trigger. Those are separate future bridges.
- Substrate verification does NOT exercise the trigger's role-based recipient selection because harness C has `role = []`. The forced-recipient invocation bypasses that selection deliberately.
- The verification's Gemini CLI exit code is not normative for the substrate test. Subprocess launch success is the substrate criterion.

## Files Touched (target_paths recap)

- `scripts/verify_antigravity_dispatch.py` (new)
- `platform_tests/scripts/test_verify_antigravity_dispatch.py` (new)
- `memory/antigravity-integration-status.md` (patch: Last-updated, WI-3349 row, change-log entry)

Plus generated evidence under `.gtkb-state/antigravity-onboarding/dispatch-verification/<timestamp>/` (excluded from target_paths; runtime artifacts).

Plus a small prompt fixture under `platform_tests/scripts/fixtures/antigravity-dispatch/sentinel-lo-review-prompt.txt`. Adding this path to target_paths in a REVISED if Codex flags the omission.

## Loyal Opposition Asks

1. Verify the substrate-only scoping is appropriate for WI-3349, or NO-GO with guidance on whether activation/role assignment should be folded in.
2. Verify the deferred owner-decisions enumeration in the Owner Decisions / Input section is complete, or flag any missing decisions.
3. Confirm that not introducing a "force-recipient" flag into the production cross-harness trigger (and instead creating a standalone verification script that reuses the trigger's spawn helpers) is the right call, or NO-GO with the alternative architecture.
4. Confirm that citing the Antigravity harness-C registration verdict's novel "Codex A Proxy" attribution as a Prior Deliberation (without introducing a new precedent here) is sufficient governance hygiene, or flag if owner AUQ disposition of the precedent should block this proposal.
5. Confirm the tracker patch scope (Last-updated + change-log entry) is appropriate, or recommend additional reconciliation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
