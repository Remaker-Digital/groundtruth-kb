REVISED

# Implementation Proposal - Phase-1 Ollama Verification and Doctor Check (Child 3, REVISED-2)

bridge_kind: prime_proposal
Document: gtkb-ollama-integration-phase-1-verification
Version: 005 (REVISED; addresses NO-GO at -004)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-05 UTC

author_identity: Claude Code
author_harness_id: B
author_session_context_id: cb8d1960-2984-4042-b76d-6a869cd0e16a
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: claude-code; interactive; Prime Builder; /loop dynamic
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Work Item: WI-4322
work_item_ids: [WI-4322, WI-4323]

Recommended commit type: feat

target_paths: ["scripts/verify_ollama_dispatch.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_ollama.py", "platform_tests/scripts/test_verify_ollama_dispatch.py"]

## Summary

This is Child 3 of the Phase-1 Ollama integration umbrella (GO at
`bridge/gtkb-ollama-integration-phase-1-004.md`). It delivers two verification
surfaces preserving the owner-approved acceptance scope from DELIB-20260663 and
the active PAUTH.

REVISED-2 to address Codex NO-GO at -004:
- **F1 (P1):** Live E2E now uses `run_tool_loop` (the actual shim tool-calling
  path) instead of raw `call_ollama_chat` without tools. Bridge filing proof now
  exercises the real `dispatch_tool_call("Write", ...)` code path with guard
  pipeline in a disposable fixture workspace, not dry-run.
- **F2 (P1):** Doctor registry consistency now covers all four stores (harness
  identities, harness registry, capability registry, routing TOML) with
  cross-store consistency checks.

1. **WI-4322** — `scripts/verify_ollama_dispatch.py`: an E2E verification
   script with two operational modes:
   - **Live mode** (default when Ollama is reachable): invokes the actual shim
     `run_tool_loop` with tool schemas enabled, verifies at least one GT-KB tool
     call round-trip, exercises bridge filing via the real Write dispatch path
     in a fixture workspace, validates author metadata, and runs ruff/pytest.
   - **Guard-only mode** (fallback when Ollama is unreachable): exercises the
     guard-adapter pipeline with mocked model responses to verify destructive
     Bash denial, formal-artifact mutation denial, and out-of-root rejection.
   Guard-only fixtures are additive evidence, not replacements for live E2E.

2. **WI-4323** — `groundtruth-kb/src/groundtruth_kb/project/doctor.py`:
   `_check_ollama_harness` doctor check producing a four-store inventory with
   four-layer verification:
   - **Layer 1 (routing parse):** `.ollama/routing.toml` present and parseable.
   - **Layer 2 (four-store registry consistency):** All four stores agree:
     `harness-state/harness-identities.json` has `ollama` → id `D`;
     `harness-state/harness-registry.json` has id `D` with name `ollama`,
     type `ollama`, status `registered`, role `[]`;
     `config/agent-control/harness-capability-registry.toml` has
     `[harnesses.ollama]` with Phase-1 capability-floor keys;
     `.ollama/routing.toml` exists and its models are consistent with
     the registered harness identity.
   - **Layer 3 (reachability):** Ollama endpoint responds to `/api/tags`.
   - **Layer 4 (advertised-model verification):** Models declared in
     routing TOML are actually advertised by the local Ollama server.

## Revision Notes (REVISED-2 -005 vs -003)

### F1 fix — actual shim tool loop for E2E

The `-003` live mode sent `call_ollama_chat` without tool definitions (proving
only that the HTTP endpoint can answer chat requests) and used dry-run /
structure-only bridge checks. The `-005` design:

- **L1 (tool-loop round-trip):** Calls `run_tool_loop(prompt=<fixture>,
  model_route=<from routing.toml>, endpoint=<live>, max_turns=3,
  project_root=Path("E:/GT-KB"))` with a deterministic prompt designed to
  trigger a `Read` tool call (e.g., "Read the file `.ollama/routing.toml` and
  return its content verbatim."). Asserts the response contains routing TOML
  content (e.g., `qwen-coder-14b`). This proves: schema building, model
  receives tool schemas, model issues a tool call, `dispatch_tool_call`
  dispatches Read, content returns through the tool message, model produces
  final text.

- **L2 (author metadata):** After the tool loop, verifies that `ModelMetadata`
  was constructed with the correct `model_id` and `model_version` from the
  routing TOML. The `run_tool_loop` function constructs metadata internally at
  line 634 and passes it to every `dispatch_tool_call`. The verification script
  captures the metadata by wrapping the chat function to inspect the payload's
  `model` field, then checks it matches the routing TOML's configured model.

- **L3 (bridge filing proof via Write dispatch):** Creates a disposable fixture
  workspace (temp directory with a `bridge/` subdirectory and a minimal
  `bridge/INDEX.md`). Calls `dispatch_tool_call("Write",
  {"file_path": "<fixture_root>/bridge/gtkb-ollama-e2e-fixture-001.md",
  "content": "<valid NEW bridge body>"}, model_metadata,
  Path("<fixture_root>"))` — this exercises the exact `_dispatch_write` code
  path including `run_guard_pipeline` (credential scan, bridge compliance gate).
  Asserts: file was created, first non-blank line is `NEW`, no guard rejection.
  Then adds a `Document:` + `NEW:` entry to the fixture INDEX.md and runs
  `bridge_applicability_preflight.py` against the fixture workspace (passing
  `--project-root <fixture_root>` if supported, or by validating the written
  file structure matches bridge protocol format). Cleanup: removes temp
  directory. **No production bridge/INDEX.md is modified.**

- **L4 (code quality):** ruff check + ruff format --check on all target_paths
  files, plus `pytest platform_tests/scripts/test_verify_ollama_dispatch.py -q`.

### F2 fix — four-store registry consistency in doctor

The `-003` doctor design checked only routing-vs-D presence. The `-005` design
verifies all four stores and their cross-store consistency:

1. **Identities store:** `harness-state/harness-identities.json` must contain
   `"ollama"` key with `"id": "D"`. Missing or wrong id → WARN.
2. **Registry store:** `harness-state/harness-registry.json` must contain a
   harness entry with `id: "D"`, `harness_name: "ollama"`,
   `harness_type: "ollama"`, `status: "registered"`, `role: []`. Mismatched
   status/role/type → WARN with specific drift description.
3. **Capability store:** `config/agent-control/harness-capability-registry.toml`
   must contain `[harnesses.ollama]` with the four Phase-1 capability-floor keys
   (`bridge_compliance_gate_respect`, `root_boundary_respect`,
   `author_metadata_env_var_setting`, `destructive_gate_delegation`). Missing
   section or missing keys → WARN.
4. **Routing store:** `.ollama/routing.toml` must exist and contain at least one
   model with `tool_calling_supported = true`. Missing or unparseable → WARN.
5. **Cross-store consistency:** If any store has Ollama registered but another
   store is missing the corresponding entry → WARN with specific drift.
6. **Advertised-model check (Layer 4, reachability-gated):** When Ollama is
   reachable, verify that models configured in routing TOML appear in
   `/api/tags`. Missing model → WARN.

## Guard-Only Mode (unchanged from -003)

When Ollama is unreachable, the script falls back to guard-only mode:

- **G1 (destructive Bash denial):** Exercises `dispatch_tool_call("Bash",
  {"command": "rm -rf /"}, ...)` with the guard pipeline → expects rejection.
- **G2 (formal-artifact denial):** Exercises Write to a formal-artifact path
  → expects guard rejection.
- **G3 (out-of-root denial):** Exercises Read/Write to a path outside
  `E:\GT-KB` → expects rejection.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge index authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — mandatory spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — root-boundary compliance.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — harness onboarding capability-floor contract.
- `GOV-STANDING-BACKLOG-001` — WI-4322/WI-4323 standing backlog.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project authorization.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements are
`GOV-HARNESS-ONBOARDING-CONTRACT-001` (Layer 3 capability floor),
`ADR-ISOLATION-APPLICATION-PLACEMENT-001` (root boundary), and the owner
decisions in `DELIB-20260663` (AUQ#9 E2E scope, AUQ#10 doctor scope). No
new or revised requirement is needed.

## Specification-Derived Verification Plan

| Spec / Acceptance Item | Test | Expected |
|---|---|---|
| WI-4322: tool-loop round-trip through shim | `test_live_tool_loop_round_trip` (calls `run_tool_loop` with Read-triggering prompt; mock chat returns tool_call for Read then final text) | Response contains routing TOML content |
| WI-4322: author metadata from routing TOML | `test_live_author_metadata_correct` (inspects ModelMetadata model_id against routing TOML) | `model_id` matches routing TOML configured model |
| WI-4322: bridge filing via Write dispatch | `test_live_bridge_filing_via_dispatch` (calls `dispatch_tool_call("Write", ...)` in fixture workspace, verifies file created with NEW first line) | File written, guard pipeline passed, first line is NEW |
| WI-4322: ruff + pytest sanity | `test_code_quality_gates` | ruff check + ruff format --check clean on target files |
| WI-4323: identity store check | `test_doctor_ollama_identity_present` / `test_doctor_ollama_identity_mismatch` | PASS when ollama→D; WARN when ollama→E or missing |
| WI-4323: registry store check | `test_doctor_ollama_registry_role_status` | PASS when D/registered/[]; WARN on drift |
| WI-4323: capability store check | `test_doctor_ollama_capability_present` / `test_doctor_ollama_capability_missing` | PASS when [harnesses.ollama] has 4 keys; WARN when missing |
| WI-4323: routing store check | `test_doctor_ollama_routing_present` / `test_doctor_ollama_routing_missing` | PASS when parseable with tool_calling model; WARN when missing |
| WI-4323: cross-store consistency | `test_doctor_ollama_cross_store_drift` | WARN when identities has ollama but routing missing, or vice versa |
| WI-4323: advertised-model verification | `test_doctor_ollama_model_advertised` / `test_doctor_ollama_model_absent` | PASS when /api/tags includes configured model; WARN when absent |
| Guard-only: destructive Bash denial | `test_guard_destructive_bash_denied` | Guard pipeline rejects `rm -rf /` |
| Guard-only: formal-artifact denial | `test_guard_formal_artifact_denied` | Guard pipeline rejects Write to protected path |
| Guard-only: out-of-root denial | `test_guard_out_of_root_denied` | Guard pipeline rejects out-of-root Read/Write |
| Lint + format | `ruff check` + `ruff format --check` on all target files | Clean |
| Full pytest regression | `pytest platform_tests/scripts/test_verify_ollama_dispatch.py groundtruth-kb/tests/test_doctor_ollama.py -q` | All pass |

## Owner Decisions / Input

The proposal operates within existing owner decisions and project authorization:

- **`DELIB-20260663`** — 12-AUQ owner decision pass. AUQ#9 selected "round-trip
  + bridge filing + ruff/pytest" for E2E scope. AUQ#10 selected "reachability +
  advertised models + registry consistency" for doctor scope.
- **PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE**
  — active project authorization including WI-4322 and WI-4323.

No additional owner decision is required.

## Prior Deliberations

- `DELIB-20260663` — owner 12-AUQ decision pass defining E2E scope (AUQ#9) and
  doctor scope (AUQ#10). AUQ#9 explicitly selected "round-trip + bridge filing +
  ruff/pytest". AUQ#10 explicitly selected "reachability + advertised models +
  registry consistency" and frames registry consistency as drift across
  identities, registry, capability registry, and routing TOML.
- `DELIB-20260680` — parent umbrella NO-GO requiring guard-adapter contract.
- `bridge/gtkb-ollama-integration-phase-1-004.md` — parent umbrella GO.
- `bridge/gtkb-ollama-integration-phase-1-shim-012.md` — Child 2 VERIFIED;
  leaves live round-trip for Child 3.
- `bridge/gtkb-ollama-integration-phase-1-verification-002.md` — prior NO-GO
  requiring tool round-trip, bridge filing, author metadata, advertised-model,
  registry consistency.
- `bridge/gtkb-ollama-integration-phase-1-verification-004.md` — latest NO-GO
  requiring actual shim tool loop (not raw chat), fixture bridge filing (not
  dry-run), and four-store registry consistency.
- No retrieved deliberation rejects the shim tool-loop or four-store approaches.

## Risk and Rollback

**Risk:** Low — all four target_paths are new files or additive doctor checks.
The verification script is read-only against production state (fixture workspace
for bridge filing). The doctor check is purely diagnostic (no mutations).

**Rollback:** Revert the single commit. No production state is modified by the
verification script's fixture operations.

## Notes for Loyal Opposition

The key changes from -003:
1. L1 now invokes `run_tool_loop` from `scripts/ollama_harness.py` instead of
   `call_ollama_chat`. The mock chat function in tests simulates a tool_call
   response for Read, then a final text response — proving the full loop path.
2. L3 now calls `dispatch_tool_call("Write", ...)` against a temp directory
   fixture root, exercising the real `_dispatch_write` including
   `run_guard_pipeline`. No production INDEX.md is touched.
3. Doctor `_check_ollama_harness` now verifies all four stores: identities (has
   ollama→D), registry (D/ollama/registered/[]), capability registry
   ([harnesses.ollama] with 4 Phase-1 keys), and routing TOML (parseable with
   tool-calling model). Cross-store drift detection fires when any store is
   inconsistent with the others.
4. Tests in `groundtruth-kb/tests/test_doctor_ollama.py` now cover: identity
   present/mismatch, registry role/status drift, capability present/missing,
   routing present/missing, cross-store drift, advertised-model present/absent.

The implementation-start packet will be minted from this thread's GO before
editing any target file.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
