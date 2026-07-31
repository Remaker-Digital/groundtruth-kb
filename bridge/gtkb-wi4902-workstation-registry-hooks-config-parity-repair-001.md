NEW

# WI-4902 — Workstation Registry, Hook, and Configuration Parity Repair

bridge_kind: prime_proposal
Document: gtkb-wi4902-workstation-registry-hooks-config-parity-repair
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-07 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3d4b-288e-7ef0-9904-0264a4880d24
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; approval_policy=never; filesystem unrestricted; network enabled

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4902

target_paths: [".codex/hooks.json", ".codex/gtkb-hooks/run_py_no_window.py", "scripts/parity_discovery_diff.py", "platform_tests/scripts/test_parity_discovery_diff.py", "groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py", "scripts/dispatcher_runtime.py", "platform_tests/scripts/test_external_harness_exec_boundary.py", ".claude/rules/file-bridge-protocol.md", ".claude/rules/bridge-essential.md", "groundtruth-kb/templates/rules/file-bridge-protocol.md", "groundtruth-kb/templates/rules/bridge-essential.md", ".groundtruth/formal-artifact-approvals/*.json", "config/registry/sot-artifacts.toml", "groundtruth.db", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_check_sot_registry_completeness.py", "config/agent-control/harness-model-pin-confirmations.toml", "config/agent-control/harness-capability-registry.toml"]

implementation_scope: source, test, hook_config, registry_projection, narrative_template_parity, governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This proposal authorizes a scoped repair for the workstation registry, hook, and configuration parity defects surfaced by `gt project doctor --dir . --json`, `scripts/parity_discovery_diff.py --project-root . --markdown`, and focused regression tests on 2026-07-07. The failing surfaces are related but not identical: Codex hook discovery reports 21 Claude-only hook asymmetries, `.codex/hooks.json` does not explicitly expose `spec-classifier.py` under `UserPromptSubmit`, `scripts/dispatcher_runtime.py` still uses literal `git` subprocess invocations, managed bridge rule files drift from their managed templates, the SoT registry projection is missing two TOML records and misclassifies three active non-file/runtime paths as unresolved, and active dispatch model pins lack explicit owner-confirmation metadata.

The implementation must preserve the current harness roles, dispatcher eligibility, provider credentials, model route identities, and bridge lifecycle state. It must distinguish real missing runtime behavior from scanner false negatives: Codex already routes many named hooks through `.codex/gtkb-hooks/run_py_no_window.py` batches, so parity repair may require discovery expansion and registry aliasing rather than blindly duplicating hooks. Model-pin confirmation metadata must not be fabricated; it may be written only after Mike explicitly reconfirms the exact active pins and the implementation records durable owner-decision evidence.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — all target paths are protected source, hook, config, rule, template, database, or governance-evidence surfaces and require numbered bridge review before mutation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all source, config, hook, rule, database, and approval-evidence edits remain inside the GT-KB project root and must not depend on out-of-root live artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the proposal identifies the parity, registry, bridge, and project-governance specifications constraining this repair.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this implementation proposal carries the Phase 2 PAUTH, project id, work item id, and inline-JSON `target_paths`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the implementation report must map each repaired defect to executed parity, doctor, and focused regression checks.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the active Phase 2 project authorization allows bounded parity repair only after bridge `GO` and implementation-start authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the Phase 2 PAUTH explicitly does not bypass the bridge, work-intent claim, implementation report, or verification gates.
- `GOV-STANDING-BACKLOG-001` — the work is a regression cleanup against WI-4902's acceptance that feasible skill, hook, command, and prompt surfaces pass parity or carry typed waivers.
- `ADR-CROSS-HARNESS-PARITY-001` — hook, command, registry, and provider-harness parity must remain semantically truthful across active harnesses.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — parity commands must fail on real unwaived asymmetry while avoiding false positives for equivalent batch/wrapper routes.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — harness hook/config/model surfaces must remain explicit, auditable, and tied to current harness records.
- `GOV-PLATFORM-SOT-REGISTRY-001` — SoT registry repairs must preserve the registry as the platform source of truth for SoT artifact records.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` — registry rows and doctor checks must distinguish required storage paths from valid non-file/runtime storage identifiers.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` — TOML registry rows and the MemBase `sot_artifacts` projection must be brought back into parity through the governed sync path.
- `GOV-ARTIFACT-APPROVAL-001` — live narrative rule-file edits, if any, require formal/narrative artifact approval evidence in addition to bridge GO.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Codex hook parity may be satisfied through governed fallback wrappers or batch routes when native hook semantics differ.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the defect report, owner direction, proposal, implementation report, owner-pin confirmation evidence, and verification verdict remain durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the repair preserves traceability from observed workstation drift to proposal, implementation evidence, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the doctor/parity failures are converted into a governed repair proposal instead of an untracked direct configuration edit.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` — owner directive authorizing bounded Harness Parity Phase 2 implementation, while preserving bridge-governed protected mutations.
- `bridge/gtkb-wi4902-harness-projection-parity-registry` — prior WI-4902 implementation thread that established the hook/skill/command projection parity baseline now showing regression drift.
- `bridge/gtkb-wi4905-codex-hook-release-parity-restore-004.md` — verified Codex hook release-parity restoration thread; current findings are follow-on drift, not permission to bypass review.
- `DELIB-1558` / `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-002.md` — prior review finding that hook-registration proposals must target actual authority surfaces and valid Codex hook contracts rather than nonexistent static settings templates.
- `bridge/gtkb-wi5049-headless-sweep-git-and-audit-guard-repair-004.md` — verified no-window/audit repair context that made literal subprocess launch issues visible in follow-on scans.
- `bridge/gtkb-wi5062-service-sot-retry-reset-004.md` — recent service/SoT watchdog evidence confirming scheduled-task storage identifiers are live runtime authority surfaces, not ordinary filesystem paths.
- Deliberation search for `WI-4902 workstation registry hooks config parity spec-classifier model pin SoT registry` returned mostly historical review/backfill and hook-registration context; the operative current evidence is the 2026-07-07 doctor/parity outputs cited in this proposal.

## Owner Decisions / Input

Mike directed Prime Builder in this session to diagnose and fix the workstation registry, hook, and configuration parity issues listed in the prompt. The active project authorization is `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29`, which covers WI-4902-style harness projection parity work but still requires bridge `GO`, work-intent claim, implementation-start packet, implementation report, and Loyal Opposition verification.

Model-pin confirmation remains owner-decision-bound. This proposal may authorize the code/config surface that stores confirmations, but the implementation must not add confirmation rows for `C/antigravity=Gemini 3.5 Flash (High)`, `D/ollama=kimi-k2-7-code-cloud`, or `F/openrouter=(unspecified)` unless Mike explicitly confirms those exact pins and the confirmation is captured as durable owner-decision evidence.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4902 requires feasible skill, hook, command, and prompt surfaces to pass parity, with typed waivers for impossible deviations. The SoT registry and projection parity specifications already require TOML/MemBase parity. The active model-pin doctor check already defines the owner-confirmation behavior; the missing ingredient is explicit owner confirmation, not a new requirement.

## Current Diagnostic Evidence

- `groundtruth-kb/.venv/Scripts/python.exe scripts/parity_discovery_diff.py --project-root . --markdown` exits non-zero with `Overall status: ASYMMETRY` and 21 unwaived Claude-only hook findings including `hook:credential-scan`, `hook:destructive-gate`, `hook:lo-file-safety-gate`, `hook:spec-classifier`, and `hook:workstream-focus`.
- `.codex/gtkb-hooks/run_py_no_window.py` already includes many of those surfaces in batches, including `spec-classifier.py` in `user-prompt-submit`; therefore the repair must decide whether to expose direct config entries, expand batch discovery, update registry aliases, or combine those without double-running hooks.
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py -q --tb=short --no-header` fails only `test_hook_registered_in_codex_hooks_json`, reporting `spec-classifier.py not registered under UserPromptSubmit in E:\GT-KB\.codex\hooks.json`.
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_doctor_registry_parity.py -q --tb=short --no-header` fails managed-artifact parity for `rules/file-bridge-protocol.md` versus `.claude/rules/file-bridge-protocol.md` and reports additional live-file drift for `.claude/hooks/assertion-check.py`, `.claude/hooks/spec-event-surfacer.py`, and `.claude/rules/file-bridge-protocol.md`.
- `groundtruth-kb/.venv/Scripts/gt.exe registry diff --json` reports `toml_count: 27`, `projection_count: 25`, and missing projection records `dispatcher-storm-watchdog-task` and `dispatcher-supervisor-task`.
- `groundtruth-kb/.venv/Scripts/gt.exe project doctor --dir . --json` reports SoT completeness warning: 27 SoT records, TOML/MemBase parity drift for those two ids, and three active records with unresolved storage paths: `bridge-work-intent-claims`, `dispatcher-supervisor-task`, and `dispatcher-storm-watchdog-task`.
- The same doctor run reports external harness exec boundary failure in `scripts/dispatcher_runtime.py`: three literal `git` command findings that are not registered harness commands.
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_external_harness_exec_boundary.py -q --tb=short --no-header` currently passes, proving the existing focused test does not catch the live `dispatcher_runtime.py` literal `git` violation and should be strengthened if the implementation changes that behavior.
- `groundtruth-kb/.venv/Scripts/gt.exe project doctor --dir . --json` reports three model-pin warnings: missing owner confirmation for `C/antigravity=Gemini 3.5 Flash (High)`, `D/ollama=kimi-k2-7-code-cloud`, and `F/openrouter=(unspecified)`.

## Cross-Harness Disposition

- `claude` — native hook-config harness for the compared hook axis. The implementation must preserve existing `.claude/settings.json` semantics and must not remove native Claude hook coverage while reconciling template drift.
- `codex` — fallback/batch hook-config harness for the compared hook axis. The implementation must make Codex hook capability coverage discoverable through `.codex/hooks.json`, `.codex/gtkb-hooks/run_py_no_window.py`, and `config/agent-control/harness-capability-registry.toml` without double-running equivalent hooks.
- `cursor` — not in the `parity_discovery_diff.py` hook-config population because the current discovery axis is Claude/Codex hook config only. Cursor parity remains covered by Phase 2 readiness/discovery surfaces outside this proposal unless a focused check proves a Cursor regression.
- `antigravity` — no native repo-local hook config participates in this hook axis. Antigravity remains governed by dispatch/readiness probes and model-pin confirmation, not by Claude/Codex hook discovery.
- `ollama` — provider harness with compact-provider envelope mode and no native event-firing hook surface. This proposal does not alter Ollama routing or credentials; only owner-confirmed model-pin metadata may be added.
- `openrouter` — provider harness with compact-provider envelope mode and no native event-firing hook surface. This proposal does not alter OpenRouter routing or credentials; only owner-confirmed model-pin metadata may be added.
- No broad owner waiver is requested. Any remaining non-equivalence after implementation must either be proven out of the hook-config axis, represented by existing typed waivers, or left visible as a real parity finding.

## Proposed Implementation Scope

1. Repair Codex hook parity by making `spec-classifier.py` discoverable under `.codex/hooks.json` `UserPromptSubmit` without double-running it, and by teaching `scripts/parity_discovery_diff.py` to expand Codex `run_py_no_window --batch <name>` entries into their concrete hook surfaces.
2. Update `config/agent-control/harness-capability-registry.toml` only as needed to map Codex fallback/batch surfaces to canonical hook capability ids, so raw aliases do not create false unregistered asymmetries.
3. Replace `scripts/dispatcher_runtime.py` literal `git` executable resolution with the registered or governed command-resolution path accepted by the External Harness Executable Resolution Exception, and add/adjust focused tests so this exact regression is caught.
4. Reconcile managed rule/template parity for `.claude/rules/file-bridge-protocol.md` and `.claude/rules/bridge-essential.md` by determining the authoritative side, updating the stale side only, and producing formal/narrative artifact approval evidence before any live narrative rule-file edit.
5. Sync the SoT TOML registry to the MemBase projection through `gt registry sync` after GO, and either create/validate valid runtime storage paths or adjust the doctor classification so `windows-scheduled-task:*` and other approved runtime identifiers are not treated as unresolved filesystem paths.
6. Add model-pin confirmation rows only after Mike explicitly confirms the exact active pins; otherwise leave the doctor warning visible and report the owner-confirmation blocker rather than inventing evidence.

## Out Of Scope

- No credential lifecycle changes, provider key rotation, or secret-value inspection.
- No dispatcher role, status, eligibility, reviewer precedence, or model-route identity changes.
- No production deployment, GitHub settings mutation, or destructive worktree cleanup.
- No broad rewrite of all managed hook drift beyond the requested bridge-rule/template and parity-discovery surfaces unless a focused test proves the additional drift must be touched to make the requested checks pass.
- No suppression of real parity gaps through broad waivers; any remaining impossible harness gap must be typed and evidence-backed.

## Spec-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | After `GO`, run `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4902-workstation-registry-hooks-config-parity-repair` and confirm the packet covers only the approved target paths. |
| `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run `groundtruth-kb/.venv/Scripts/python.exe scripts/parity_discovery_diff.py --project-root . --markdown`; expected result: PASS or only explicitly typed/waived residual findings, with no false asymmetries for hooks that Codex actually runs through batch/fallback routes. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Run `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py platform_tests/scripts/test_parity_discovery_diff.py -q --tb=short --no-header`; expected result: pass. |
| External Harness Executable Resolution Exception under `.claude/rules/project-root-boundary.md` | Run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_external_harness_exec_boundary.py -q --tb=short --no-header` and `groundtruth-kb/.venv/Scripts/gt.exe project doctor --dir . --json`; expected result: no `scripts/dispatcher_runtime.py` literal `git` boundary finding. |
| `GOV-ARTIFACT-APPROVAL-001` and managed-artifact parity | Run `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_doctor_registry_parity.py -q --tb=short --no-header`; expected result: no drift for `.claude/rules/file-bridge-protocol.md` or `.claude/rules/bridge-essential.md`. If live rule files are edited, include the formal/narrative approval packet evidence in the implementation report. |
| `GOV-PLATFORM-SOT-REGISTRY-001`, `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`, `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Run `groundtruth-kb/.venv/Scripts/gt.exe registry diff --json`, `groundtruth-kb/.venv/Scripts/gt.exe registry validate --json`, and `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_sot_registry_completeness.py -q --tb=short --no-header`; expected result: TOML/projection parity and no false unresolved-storage warnings for valid runtime identifiers. |
| Model-pin owner-confirmation behavior | Run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_harness_model_pin_reconfirmation.py -q --tb=short --no-header` and `groundtruth-kb/.venv/Scripts/gt.exe project doctor --dir . --json`; expected result: if Mike confirmed the pins, doctor no longer reports the three warnings and the confirmation file cites durable evidence; if Mike did not confirm, the implementation report explicitly leaves this item blocked by owner input. |
| Overall workstation readiness surface | Run `groundtruth-kb/.venv/Scripts/gt.exe project doctor --dir . --json`; expected result: the specific requested failures are resolved or explicitly owner-blocked, with unrelated pre-existing doctor failures left visible and itemized. |

## Risk / Rollback

The main risk is over-correcting semantic parity into duplicate hook execution. The implementation must verify that adding explicit Codex visibility for `spec-classifier.py` does not run the classifier twice on the same prompt. The second risk is choosing the wrong side of a managed rule/template drift; implementation must compare live rule intent and template content before changing either side. Rollback is a single revert of the implementation commit plus, if `gt registry sync` mutates `groundtruth.db`, restoring the pre-sync database blob from git.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4902-workstation-registry-hooks-config-parity-repair`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
