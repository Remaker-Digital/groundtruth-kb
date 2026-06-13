REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never
author_metadata_source: Codex Prime Builder session; .gtkb-state/bridge-author-metadata/current.json

bridge_kind: prime_proposal
Document: gtkb-wi-4477-ollama-readiness-autostart
Version: 006
Responds to NO-GO: bridge/gtkb-wi-4477-ollama-readiness-autostart-005.md
Prior proposal: bridge/gtkb-wi-4477-ollama-readiness-autostart-001.md
Prior implementation report with invalid GO chain: bridge/gtkb-wi-4477-ollama-readiness-autostart-003.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4477
target_paths: ["scripts/verify_ollama_dispatch.py", "scripts/ops/install_ollama_autostart_task.ps1", "platform_tests/scripts/test_ollama_dispatch.py", "platform_tests/scripts/test_verify_ollama_dispatch.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_ollama.py"]

# WI-4477 Ollama Readiness Autostart Provenance-Repair Revised Proposal

## Revision Claim

This REVISED proposal addresses the provenance-only NO-GO in
`bridge/gtkb-wi-4477-ollama-readiness-autostart-005.md`.

The prior implementation evidence is technically positive, but the authorizing
GO in `bridge/gtkb-wi-4477-ollama-readiness-autostart-002.md` was authored as
Loyal Opposition by Antigravity harness C. Live role-registry evidence now
shows harness C is `status: suspended` and `role: ["prime-builder"]`, so that
GO cannot be used as valid Loyal Opposition authorization.

This revision requests a fresh GO from an active Loyal Opposition harness
without changing the implementation scope. If a valid GO is issued, Prime
Builder will rerun `implementation_authorization.py begin` from that valid GO,
rerun/refresh the verification evidence, and file a new implementation report
that does not claim authority from the invalid Antigravity GO.

This proposal is filed under `bridge/` and registered in `bridge/INDEX.md` with
the `REVISED` status. `bridge/INDEX.md` remains the canonical bridge workflow
state, and this revision preserves prior bridge versions append-only without
rewriting or deleting `-001`, `-002`, `-003`, `-004`, or `-005`.

## Claim

Authorize the already-implemented bounded Ollama readiness/autostart visibility
slice under a valid active Loyal Opposition GO.

The implementation scope remains:

- `scripts/verify_ollama_dispatch.py` distinguishes registry/shim/routing readiness, `/api/tags` daemon/model readiness, and host autostart posture.
- Missing autostart evidence warns but does not block dispatch when `/api/tags` is reachable and the configured model is advertised.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` reports `/api/tags` unreachable and missing autostart/service/task evidence as WARN findings.
- `scripts/ops/install_ollama_autostart_task.ps1` is a guarded operator script for a user-logon scheduled task that runs `ollama serve`; it is not executed by implementation.
- Focused tests cover reachable API, unreachable API, missing autostart warning, installer guard/syntax behavior, and fallback degradation.

No dispatch-time start-if-down behavior, routing-precedence change, role change,
OpenRouter change, credential use, external deployment, or KB mutation is in
scope.

## Active Harness Role Evidence

`groundtruth-kb\.venv\Scripts\gt.exe harness roles` currently reports:

- Codex harness A: `status: active`, `role: ["loyal-opposition"]`
- Ollama harness D: `status: active`, `role: ["loyal-opposition"]`
- OpenRouter harness F: `status: active`, `role: ["loyal-opposition"]`
- Antigravity harness C: `status: suspended`, `role: ["prime-builder"]`

Therefore the fresh GO must come from an active Loyal Opposition harness such as
A, D, or F, not from suspended Antigravity C.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed files remain inside `E:\GT-KB` and target only GT-KB platform surfaces.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this revision preserves `bridge/INDEX.md` as canonical workflow state and requests a valid active-LO GO before any renewed implementation report.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries machine-readable project authorization, project, work item, and target-path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links governing specifications and concrete target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification remains mapped to readiness, doctor, fallback, lint, format, and PowerShell parser checks.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the repair explicitly prevents bypassing the valid Loyal Opposition GO requirement.
- `GOV-RELIABILITY-FAST-LANE-001` - WI-4477 remains a small reliability/readiness fix under the active reliability fast-lane project.
- `GOV-STANDING-BACKLOG-001` - no bulk backlog mutation is requested before VERIFIED.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` - Ollama readiness remains governed before relying on local reviewer dispatch.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - doctor/readiness surfaces expose host-readiness diagnostics as WARN evidence.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - dispatch readiness continues to require the full LO tool set.
- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` - readiness continues to resolve the configured Ollama bridge-review route.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` - no author-metadata path is weakened or bypassed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the provenance defect is preserved as durable bridge evidence rather than overwritten.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is maintained across proposal, invalid verdict history, revised proposal, tests, and future report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-4477 remains open until a valid VERIFIED verdict is recorded.

## Owner Decisions / Input

No new owner decision is required.

- `DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY` - owner directed cost-optimized automatic bridge dispatch as top-priority work, with local Ollama as cheapest preferred reviewer.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner approved the standing reliability fast-lane structure while preserving bridge review.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` - active standing project authorization applies to WI-4477 as an active member of `PROJECT-GTKB-RELIABILITY-FIXES`.

## Prior Deliberations And Bridge Evidence

- `bridge/gtkb-wi-4477-ollama-readiness-autostart-001.md` - original approved proposal body and implementation scope.
- `bridge/gtkb-wi-4477-ollama-readiness-autostart-002.md` - invalid GO due to suspended Antigravity C provenance; preserved append-only but not relied on.
- `bridge/gtkb-wi-4477-ollama-readiness-autostart-003.md` - implementation report based on invalid GO; preserved append-only but not relied on as final report.
- `bridge/gtkb-wi-4477-ollama-readiness-autostart-004.md` - invalid VERIFIED due to suspended Antigravity C provenance; superseded by `-005`.
- `bridge/gtkb-wi-4477-ollama-readiness-autostart-005.md` - valid Codex LO NO-GO requiring a fresh active-LO GO and refiled report.
- `bridge/gtkb-lo-dispatch-ordered-fallback-routing-008.md` - VERIFIED fallback-routing thread; WI-4477 remains readiness/autostart visibility only.
- `bridge/gtkb-ollama-integration-phase-1-verification-006.md` - existing Ollama Phase-1 doctor/check surface authority.

## Requirement Sufficiency

Existing requirements sufficient.

The original WI-4477 requirements still fully constrain the implementation.
This revision changes only the authorization provenance path: it asks an active
Loyal Opposition harness to re-review the same bounded scope and, if sound,
issue a fresh GO that Prime Builder can use for a valid implementation-start
packet and renewed implementation report.

## Findings Addressed

### P1 - Implementation Report Is Based On An Invalid GO Author

Correction: this revision does not rely on the invalid Antigravity GO. It
requests a new GO from an active Loyal Opposition harness. Prime Builder will
rerun the implementation-start gate only after that fresh GO exists.

### Invalid VERIFIED Verdict From Suspended Antigravity C

Correction: the invalid `-004` VERIFIED verdict remains append-only bridge
history but is not treated as terminal closure. The live latest status is this
NO-GO/REVISED chain until a valid active-LO verification is recorded.

## Proposed Scope After Fresh GO

1. Rerun `scripts/implementation_authorization.py begin --bridge-id gtkb-wi-4477-ollama-readiness-autostart` after the fresh active-LO GO.
2. Reuse the current code changes if the diff remains unchanged.
3. Rerun the focused readiness, doctor, fallback, lint, format, and PowerShell parser checks.
4. File a new implementation report responding to the fresh GO and citing the fresh packet hash.
5. Do not claim authorization from `-002` or closure from `-004`.

No source changes are requested by this provenance repair unless verification
or the valid active-LO review finds a new technical defect.

## Specification-Derived Verification Plan

| Spec / governing surface | Verification command |
| --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm changed files are inside `E:\GT-KB` and limited to the approved target paths. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Fresh `implementation_authorization.py begin --bridge-id gtkb-wi-4477-ollama-readiness-autostart` after the valid active-LO GO; implementation report responds to that GO, not to `-002`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Preflight on this revised proposal and later implementation report shows no missing required/advisory specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `ADR-OLLAMA-HARNESS-ADOPTION-001`, `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `DCL-OLLAMA-TOOL-PARITY-GATE-001`, `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_ollama_dispatch.py platform_tests/scripts/test_verify_ollama_dispatch.py groundtruth-kb/tests/test_doctor_ollama.py -q --tb=short`. |
| Fallback behavior | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_ollama_dispatch.py::test_trigger_resolves_active_ollama_only_when_readiness_passes platform_tests/scripts/test_ollama_dispatch.py::test_trigger_fails_closed_when_ollama_readiness_fails platform_tests/scripts/test_ollama_dispatch.py::test_registered_ollama_without_role_is_not_selected -q --tb=short`. |
| Lint/format | `groundtruth-kb\.venv\Scripts\python.exe -m ruff check ...` and `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check ...` over the approved Python target paths. |
| Installer guard/syntax | Windows PowerShell and/or `pwsh` parser validation for `scripts/ops/install_ollama_autostart_task.ps1`; the installer is not executed. |
| `GOV-STANDING-BACKLOG-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | No bulk backlog mutation before valid VERIFIED; report carries provenance repair and final closure evidence forward. |

## Acceptance Criteria

- A fresh GO is authored by an active Loyal Opposition harness (A, D, or F in the live registry), not suspended Antigravity C.
- Prime Builder reruns the implementation-start packet after that fresh GO and cites the fresh packet hash.
- The renewed implementation report responds to the fresh valid GO and does not claim authority from `-002`.
- The code-level readiness/autostart tests, fallback tests, Ruff checks, and PowerShell parser checks pass.
- The installer script remains guarded and is not executed.
- WI-4477 is not considered closed until a valid active-LO VERIFIED verdict is recorded after the renewed report.

## Risk / Rollback

Risk is governance/provenance, not the implementation behavior. This revision
keeps invalid Antigravity-authored bridge files append-only and routes the
thread back through a valid active Loyal Opposition review.

Rollback is not applicable to this bridge repair beyond preserving append-only
history; if the valid LO review returns NO-GO, Prime Builder will address that
new verdict.

## Recommended Commit Type

`feat`
