NEW

# WI-5453 - Make Antigravity readiness import correctly in daemon context

bridge_kind: prime_proposal
Document: gtkb-wi5453-antigravity-readiness-import
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5.5 Codex
author_model_version: 5.5
author_model_configuration: OpenAI Codex desktop interactive; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5453-ANTIGRAVITY-READINESS-IMPORT-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5453

target_paths: ["scripts/verify_antigravity_dispatch.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The live dispatcher reliability ledger recorded
`2026-07-17T13:05:00+00:00-antigravity-dispatch-readiness` as not launched:
`Failed to evaluate dispatch readiness for harness type 'antigravity': No
module named 'scripts.dispatcher_runtime'`. The daemon loads
`scripts/dispatcher_runtime.py` by file under the private module name
`_dispatcher_runtime_for_daemon`, and that runtime imports the Antigravity
verifier as a top-level script module. The verifier then assumes package-style
`scripts.*` imports. Existing tests start with the project root importable and
therefore miss the production loading mismatch.

Make the verifier resolve the already-loaded canonical dispatcher runtime and
projection reader by their exact in-root source-file identity before attempting
a package import. This reuses the daemon's existing module object, prevents a
second dispatcher runtime state from being initialized, remains compatible with
direct CLI and package-based test imports, and does not touch the shared dirty
`scripts/dispatcher_runtime.py` target.

An isolated reproduction matching the daemon loader confirmed both sides of the
defect. With an unoccupied local `scripts` package, verifier import succeeds by
loading a second runtime and
`verify.DispatchTarget is daemon_runtime.DispatchTarget` is false. With the
`scripts` namespace already occupied, the import fails with the exact live
`ModuleNotFoundError`. A fallback import alone is therefore insufficient; exact
reuse and duplicate detection are acceptance requirements.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - an active harness readiness adapter
  must load reliably through the real dispatcher integration context and
  preserve its readiness checks.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - Antigravity readiness remains a
  service of the one canonical dispatcher runtime, not a duplicate runtime or
  alternate launch path.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the repair preserves daemon-owned target
  selection and the existing generic verifier import boundary.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - C must not be disabled as the
  remedy; the change is import-only and does not alter routing or provider use.
- `GOV-WORK-TREE-HYGIENE-001` - the two clean targets remain isolated from
  current foreign `dispatcher_runtime.py` changes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation requires independent GO,
  exact claim, implementation-start authorization, report, verification, and
  focused finalization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  binds the two exact targets to concrete governing requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project,
  WI-5453, and target paths are explicit and mechanically checkable.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the PAUTH permits only this
  source/test correction after all remaining operation-time gates pass.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must
  reproduce daemon-style file loading in an isolated process and prove module
  identity reuse without contacting Antigravity.
- `GOV-STANDING-BACKLOG-001` - WI-5453 and linked `TEST-11556` preserve the
  observed failure and its acceptance contract.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the dispatch failure, work item,
  test, proposal, module-identity evidence, and final commit remain traceable.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the isolated subprocess transcript
  is durable proof of the real integration context rather than an inferred
  package-import result.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - capture, proposal, implementation,
  verification, dispatch re-proof, and closure remain distinct states.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - Mike authorized
  bounded PAUTH carriers and governed proposal lifecycles for newly discovered
  fleet defects while preserving every later gate.
- `WI-5217` - earlier Antigravity prompt-transport work; this proposal does not
  change argv or stdin behavior.
- `WI-5362` - covers phase-one parity entrypoint import shadowing, not the
  verifier/daemon module-identity mismatch observed here.
- `2026-07-17T13:05:00+00:00-antigravity-dispatch-readiness` - canonical
  dispatcher reliability evidence for the current import failure.

## Owner Decisions / Input

`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes this
bounded PAUTH and proposal lifecycle.
`PAUTH-DISPATCHER-BLACK-BOX-WI5453-ANTIGRAVITY-READINESS-IMPORT-20260717` is
active and includes WI-5453 plus the governing specifications. No new owner
decision is required for review. Direct harness contact, eligibility changes,
or live dispatcher activation remain outside this PAUTH.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-HARNESS-ONBOARDING-CONTRACT-001`,
`SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, and
`ADR-DISPATCHER-ARCHITECTURE-001` define the canonical readiness path.
WI-5453 and linked `TEST-11556` provide the exact daemon-context import and
single-module-identity acceptance conditions.

## Proposed Implementation

1. In `scripts/verify_antigravity_dispatch.py`, add a small resolver that:
   - accepts an exact expected source path and required attribute names;
   - scans loaded modules for a `__file__` that resolves to that exact in-root
     source path;
   - returns the single matching module only when all required attributes are
     present;
   - fails explicitly if multiple distinct loaded objects claim the same
     dispatcher runtime source;
   - performs the existing package-style import only when no canonical module
     is already loaded, then verifies the imported file identity.
2. Resolve `dispatcher_runtime.py` through that helper and bind
   `DispatchTarget` plus `_harness_command` from the returned module. In daemon
   context this must reuse `_dispatcher_runtime_for_daemon`; it must not import
   `scripts.dispatcher_runtime` or `dispatcher_runtime` a second time.
3. Resolve `harness_projection_reader.py` with the same exact-file rule and
   bind `load_harness_projection`. Preserve all current readiness, command,
   evidence, redaction, no-window, and verdict-anchor behavior.
4. Add an isolated-process test that starts outside the project root, exposes
   only the canonical script/package paths, loads `dispatcher_runtime.py` under
   the daemon's private module name, imports the Antigravity verifier as a
   top-level module, and asserts exact class/function identity reuse.
5. Add package-import and duplicate-module fail-closed tests. Stub every
   provider/process boundary so the suite cannot invoke `agy`, a model, a
   worker, or any live dispatch surface.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION; PAUTH-DISPATCHER-BLACK-BOX-WI5453-ANTIGRAVITY-READINESS-IMPORT-20260717; WI-5453; TEST-11556",
  "canonical_authority": "GOV-HARNESS-ONBOARDING-CONTRACT-001; SPEC-CENTRALIZED-DISPATCH-SERVICE-001; ADR-DISPATCHER-ARCHITECTURE-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "Reuse the already-loaded project-owned module whose exact source file is scripts/dispatcher_runtime.py; use package import only when no canonical runtime is loaded, as in direct CLI or package tests.",
  "before_behavior": "The daemon loads dispatcher_runtime by file under a private module name, then the top-level Antigravity verifier assumes scripts.dispatcher_runtime is importable and readiness fails before evaluation.",
  "after_behavior": "The verifier reuses the daemon's exact loaded runtime module, package-style invocations remain compatible, and readiness reaches the existing evaluation logic with one runtime state.",
  "self_descriptive_naming": "resolve_loaded_project_module, expected_source_path, required_attributes, and duplicate_module_identity describe the boundary directly.",
  "obsolete_guidance_disposition": "Package-qualified scripts.* imports are not assumed to be valid in daemon top-level loading context. Generic fallback that silently loads a second dispatcher runtime is prohibited.",
  "history_preservation": "The dispatch failure, PAUTH, bridge chain, linked test, isolated-process transcript, exact target hashes, and focused finalization remain auditable.",
  "baseline": {
    "runtime_module_name": "_dispatcher_runtime_for_daemon",
    "verifier_module_name": "verify_antigravity_dispatch",
    "failing_import": "scripts.dispatcher_runtime",
    "live_failure_reason": "antigravity_dispatch_not_ready"
  },
  "expected_result": {
    "daemon_context": "reuses _dispatcher_runtime_for_daemon by exact source-file identity",
    "package_context": "imports and reuses scripts.dispatcher_runtime",
    "duplicate_context": "fails closed with a deterministic identity diagnostic",
    "readiness_semantics": "unchanged after imports succeed"
  },
  "rollback": {
    "instructions": "Revert only the two declared targets through one governed focused transaction.",
    "verification": "Rerun the focused verifier tests and confirm no dispatcher, TAFE, worker, eligibility, routing, claim, lease, or provider state changed."
  },
  "hard_invariants": [
    "Codex A remains Prime Builder only and never publishes a Loyal Opposition verdict.",
    "Antigravity C is not disabled or made ineligible as remediation.",
    "The daemon's already-loaded dispatcher runtime module is reused rather than initialized twice.",
    "No Antigravity executable, provider, worker, claim, lease, TAFE document, dispatcher configuration, eligibility, routing, or runtime state is contacted or mutated by tests.",
    "scripts/dispatcher_runtime.py and all foreign dirty targets remain byte-for-byte untouched.",
    "All resolved project module paths remain within E:\\GT-KB."
  ],
  "fail_closed_conditions": [
    "The expected project source path is missing, unreadable, or outside E:\\GT-KB.",
    "Multiple distinct loaded module objects resolve to scripts/dispatcher_runtime.py.",
    "A resolved module lacks DispatchTarget or _harness_command.",
    "The projection reader lacks load_harness_projection.",
    "A fallback package import resolves to a different source file.",
    "Either clean target changes after implementation-start hashing."
  ],
  "essential_context_preservation": "Readiness evidence retains harness identity, registry-projected command, role, no-window behavior, verifier checks, sanitized diagnostics, exact runtime module name and source path, and whether the module was reused or imported."
}
```

## Spec-Derived Verification Plan

| Specification / invariant | Verification | Expected result |
| --- | --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`; `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verify_antigravity_dispatch.py -q --tb=short` | Daemon-style top-level loading and package-style loading both reach the existing readiness logic without import failure. |
| Single runtime identity | Isolated `python -I` subprocess loads `dispatcher_runtime.py` as `_dispatcher_runtime_for_daemon`, then imports the verifier with a foreign cwd and asserts object identity. | `verify.DispatchTarget is runtime.DispatchTarget` and `verify._harness_command is runtime._harness_command`; no second runtime module is loaded. |
| Fail-closed duplicate/shadow behavior | Focused fixtures pre-load conflicting modules and package shadows, then exercise the resolver. | Exact source identity wins over package name; duplicate exact-source module objects produce a stable explicit failure. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; `GOV-WORK-TREE-HYGIENE-001` | Snapshot subprocess/provider mocks and exact Git status for both targets before and after focused tests. | No provider or harness process launches; no TAFE, dispatcher, worker, lease, claim, eligibility, routing, runtime, or foreign file bytes change. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the focused suite, existing source-entrypoint migration test, Ruff check/format check for the two targets, both proposal preflights, phantom-spec validation, and `git diff --check`. | All checks pass; applicability reports no missing specs or blocking errors; clause preflight reports zero blocking gaps; only authorized target bytes differ. |
| Live black-box acceptance after terminal finalization | Read-only canonical dispatcher report/health after the ordinary daemon loads the committed generation and naturally evaluates C readiness. | No `No module named 'scripts.dispatcher_runtime'` or `antigravity_dispatch_not_ready` import finding appears. Any genuine provider readiness result remains independently visible. |

## Risk / Rollback

Risk is moderate: resolving the wrong module could duplicate global dispatcher
state, while swallowing an import error could falsely mark C ready. The resolver
therefore uses exact canonical file identity, required attributes, and
fail-closed duplicate detection. It never catches unrelated import failures and
does not alter readiness outcomes after successful binding.

Rollback is a focused revert of the two declared targets. The change performs no
live dispatch, provider call, eligibility update, daemon restart, TAFE mutation,
deployment, or release.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5453-antigravity-readiness-import`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(harness):` because the change restores the existing Antigravity readiness
adapter under the canonical daemon loading context.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
