NEW

# Post-Implementation Report - WI-5003 Opus Floor And C Stdin Dispatch

bridge_kind: implementation_report
Document: gtkb-wi5003-opus-floor-c-stdin-dispatch
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-07-03 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-03T23-19-41Z-prime-builder-A-a9de87
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex auto-dispatch; approval_policy=never; workspace-write

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5003-OPUS-FLOOR-C-STDIN
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5003

target_paths: ["scripts/dispatcher_runtime.py", ".api-harness/routing.toml", "harness-state/harness-registry.json", "groundtruth.db", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py", "platform_tests/scripts/test_verify_ollama_dispatch.py"]

implementation_scope: source, configuration, harness-registry, kb-state, tests
requires_verification: true
kb_mutation_in_scope: true

---

## Implementation Claim

Implemented the WI-5003 GO scope for `bridge/gtkb-wi5003-opus-floor-c-stdin-dispatch-002.md`:

- Harness C's governed registry headless surface now preserves `agy --print`, `--print-timeout 30m`, `--model "Gemini 3.5 Flash (High)"`, permission, and project-root arguments while adding `stdin: true` and `prompt_transport: "stdin"` so dispatcher runtime removes the full bridge prompt from child argv and passes it through `run_with_status.py --stdin`.
- Dispatcher worker lifetime defaults now define `OPUS_CLASS_WORKER_LIFETIME_FLOOR_SECONDS = 3600`; Loyal Opposition role fallback and B/C/D harness defaults use that floor unless an explicit positive harness env override is present. Prime Builder A remains at the existing 5400-second implementation default.
- Ollama/API routing now keeps `deepseek-v4-pro-cloud` as the explicit route and raises `[routing.ollama].timeout_seconds` from 1800 to 3600; the harness derives a 3660-second session timeout from that route timeout.
- Focused tests now cover the unprofiled Loyal Opposition floor, C-specific lifetime default, D-specific lifetime default, C stdin prompt stripping from child argv, Antigravity fixture stdin metadata, and the D route timeout/session-timeout contract.

This report covers only the authorized WI-5003 target paths listed above. The worktree contains many unrelated dirty files from other in-progress bridge threads; those are outside this implementation report.

## Implementation Authorization Evidence

- Implementation-start authorization command: `.\groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi5003-opus-floor-c-stdin-dispatch`
- Authorization packet: `.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5003-opus-floor-c-stdin-dispatch.json`
- Authorization packet hash: `sha256:d924455b42379309613558d3f38357d1b9551c6095ab312768eb8ebfbcadb6b3`
- Work-intent claim command: `.\groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-wi5003-opus-floor-c-stdin-dispatch`
- Work-intent claim rowid: `29773`
- Work-intent session id: `2026-07-03T23-19-41Z-prime-builder-A-a9de87`

The requested role-reader command `.\groundtruth-kb\.venv\Scripts\gt.exe harness roles` could not run because this checkout's project venv currently has no `gt.exe` console script. I verified durable identity from `harness-state/harness-identities.json`, read `harness-state/harness-registry.json`, and used `.\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli ...` for governed harness and dispatcher CLI transactions. No ambient bare `python` or bare `gt` command was used.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher-owned headless routing must select runnable targets and compose launch commands that can actually start under the configured OS/process boundary.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatch metadata must carry coherent lifetime/profile/elapsed evidence for later hung/failure analysis.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the fix belongs in dispatcher runtime/configured invocation surfaces, not ad hoc harness-to-harness fallback.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - the owner has prohibited direct harness interaction; the remedy must keep automation behind dispatcher control-plane state and registry surfaces.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - proposal, GO, implementation report, and verification must use the current bridge numbered-file chain and dispatcher-backed state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries forward the proposal's governing specification links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project id, work item id, and target paths are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps each governing requirement to executed verification evidence.
- `GOV-STANDING-BACKLOG-001` - WI-5003 remains the canonical backlog work item for this defect fix.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the operational finding and owner timer refinement remain preserved in durable backlog, decision, bridge, source, and test artifacts.

## Prior Deliberations

- `DELIB-20260703-DISPATCH-OPUS-FLOOR-20RUN-REFINEMENT` - owner decision: use an Opus-class dispatch window for every harness/profile until 20 profile-specific example runs and quality/elapsed-time analysis support a lower 95%-confidence threshold.
- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES` - prior owner direction to start with generous allowances until telemetry exists.
- `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS` - prior owner direction to decide hung/failure status from harness/model/config elapsed-time evidence.
- `bridge/gtkb-wi4986-model-aware-dispatch-timers-006.md` - verified model-aware timer baseline that WI-5003 refines upward for C/D/LO defaults.
- `bridge/gtkb-wi4977-headless-dispatch-stability-008.md` - verified dispatcher stabilization precedent.
- `bridge/gtkb-wi4991-headless-ineligible-dispatch-suppression-004.md` - verified adjacent dispatcher-selection safety work.

## Owner Decisions / Input

- `DELIB-20260703-DISPATCH-OPUS-FLOOR-20RUN-REFINEMENT` authorizes the Opus-class floor and the 20-run/95%-confidence refinement rule.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5003-OPUS-FLOOR-C-STDIN` authorizes bounded source, test, configuration, harness-registry, KB-state, and bridge work for WI-5003. It forbids direct harness-to-harness launch, credential mutation, and production deployment.

## Files Changed

- `scripts/dispatcher_runtime.py` - adds `OPUS_CLASS_WORKER_LIFETIME_FLOOR_SECONDS`, raises LO fallback to 3600, adds C and D 3600-second harness defaults, and keeps prompt-via-stdin dispatch behavior covered by focused tests.
- `.api-harness/routing.toml` - raises Ollama route timeout to 3600 while preserving `deepseek-v4-pro-cloud`.
- `harness-state/harness-registry.json` - regenerated projection from the governed harness transaction; C is active/dispatchable, uses `agy --print`, and marks stdin prompt transport.
- `groundtruth.db` - governed harness transaction persisted C headless surface version 33.
- `platform_tests/scripts/test_dispatcher_runtime.py` - covers the Opus floor, C/D lifetime defaults, env override behavior, and C stdin prompt stripping from child argv.
- `platform_tests/scripts/test_verify_antigravity_dispatch.py` - aligns Antigravity fixture records with the `agy` CLI and stdin metadata already present in the current test surface.
- `platform_tests/scripts/test_verify_ollama_dispatch.py` - asserts the 3600-second D route timeout and 3660-second derived session timeout.

Recommended commit type: `fix`

## Spec-To-Test Mapping

| Specification / Requirement | Verification Evidence |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `test_antigravity_stdin_dispatch_removes_prompt_from_child_argv` confirms C's dispatch prompt is written to a `--stdin` file and omitted from the child argv while ordinary `agy` flags and `{{PROJECT_ROOT}}` substitution remain. Harness C registry read confirms the live surface carries `stdin: true` and `prompt_transport: "stdin"`. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | `test_worker_lifetime_profile_uses_opus_floor_for_unprofiled_lo` and the parameterized lifetime wrapper test confirm fallback/default lifetimes and metadata sources for B/C/D/A. Existing timeout telemetry tests continue to verify recorded lifetime/elapsed fields. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Runtime changes stay in dispatcher runtime, harness registry transaction, and routing config. No direct harness-to-harness launch path or standby fallback was added. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Focused tests execute command construction through dispatcher/runtime helper surfaces only; this implementation did not add direct harness invocation from another harness. |
| `DELIB-20260703-DISPATCH-OPUS-FLOOR-20RUN-REFINEMENT` | Runtime constant and tests pin a 3600-second Opus-class floor for LO/unprofiled/C/D dispatch until a future 20-run evidence analysis justifies refinement. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report includes exact commands, observed results, and mapping from governing requirements to verification evidence. |

## Verification Commands And Observed Results

Initial focused pytest attempt:

```text
.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_verify_antigravity_dispatch.py platform_tests\scripts\test_verify_ollama_dispatch.py -q --tb=short
```

Observed result: failed before meaningful code assertions because pytest could not access `C:\Users\micha\AppData\Local\Temp\pytest-of-micha` (`PermissionError: [WinError 5] Access is denied`). I reran with an in-workspace basetemp.

Passing focused pytest run:

```text
.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_verify_antigravity_dispatch.py platform_tests\scripts\test_verify_ollama_dispatch.py -q --tb=short --basetemp .harness-tmp\pytest-wi5003
```

Observed result: `190 passed, 1 skipped, 2 warnings in 17.72s`. Warnings were unrelated config/cache warnings: unknown `asyncio_mode` and inability to create an existing `.pytest_cache\v\cache\nodeids` path.

Lint:

```text
.\groundtruth-kb\.venv\Scripts\ruff.exe check scripts\dispatcher_runtime.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_verify_antigravity_dispatch.py platform_tests\scripts\test_verify_ollama_dispatch.py
```

Observed result: `All checks passed!`

Format:

```text
.\groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts\dispatcher_runtime.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_verify_antigravity_dispatch.py platform_tests\scripts\test_verify_ollama_dispatch.py
```

Observed result: `4 files already formatted`.

Harness C registry read:

```text
.\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli harness show --harness C
```

Observed result: C rowid `180`, version `33`, status `active`, role `["loyal-opposition"]`, headless argv `["agy", "--print", "{{PROMPT}}", "--print-timeout", "30m", "--model", "Gemini 3.5 Flash (High)", "--dangerously-skip-permissions", "--add-dir", "{{PROJECT_ROOT}}"]`, `stdin: true`, `prompt_transport: "stdin"`, `can_receive_dispatch: true`.

Harness D registry read:

```text
.\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli harness show --harness D
```

Observed result: D remains status `active`, role `["loyal-opposition"]`, and headless argv keeps explicit `--model deepseek-v4-pro-cloud`.

Dispatcher status read:

```text
.\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch status --json
```

Observed result: `health_status: "PASS"`, `consistency_findings: []`, `health_findings: []`; C is active and dispatchable. The status read also shows one Prime Builder work-intent-held runtime row for this active WI-5003 dispatch session, which is expected while this report is being filed.

## Telemetry Commands For Future 20-Run Refinement

Use these exact local inspection commands before proposing any future reduction below the Opus-class floor:

```text
.\groundtruth-kb\.venv\Scripts\python.exe -c 'import sqlite3; con=sqlite3.connect("groundtruth.db"); print(con.execute("select target, count(*) as runs, min(created_at), max(created_at) from dispatch_events where target in (''loyal-opposition:B'', ''loyal-opposition:C'', ''loyal-opposition:D'') group by target order by target").fetchall())'
```

```text
.\groundtruth-kb\.venv\Scripts\python.exe -c 'import json, pathlib; p=pathlib.Path(".gtkb-state/bridge-poller/dispatch-failures.jsonl"); rows=[json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]; print([{"dispatch_id": r.get("dispatch_id"), "recipient": r.get("recipient"), "model": r.get("worker_lifetime_model_hint"), "elapsed": r.get("elapsed_seconds"), "lifetime": r.get("worker_lifetime_seconds"), "reason": r.get("reason") or r.get("failure_class")} for r in rows if r.get("recipient") in {"loyal-opposition:B","loyal-opposition:C","loyal-opposition:D"}][-20:])'
```

The refinement standard remains: do not lower a harness/model/config profile below 3600 seconds until there are at least 20 profile-specific example runs plus quality/elapsed-time analysis supporting a lower threshold at 95% confidence.

## Acceptance Criteria Status

- C prompt transport via stdin: satisfied by governed C registry update and focused runtime test.
- C registry projection and MemBase harness record agree: satisfied by `harness set-invocation-surface` transaction and `harness show --harness C` read.
- C, D, and generic Loyal Opposition lifetimes are not below Opus-class floor: satisfied by runtime defaults and tests.
- D/Ollama keeps explicit DeepSeek V4 Pro cloud route and route/session timeout is not below floor: satisfied by routing config and test.
- Dispatch metadata remains rich enough for future 20-run refinement: satisfied by unchanged metadata recording plus explicit telemetry commands above.
- No direct harness-to-harness fallback, credential mutation, production deployment, or broad dispatcher redesign was added.

## Risks / Follow-Up

- The live C CLI was not launched by this Prime dispatch because direct harness-to-harness launch is prohibited in this context. The GO verdict already recorded independent `agy --print` stdin behavior evidence; this implementation verifies dispatcher command composition mechanically.
- This checkout lacks `groundtruth-kb\.venv\Scripts\gt.exe`; I used project-venv `python.exe -m groundtruth_kb.cli` for governed CLI reads and mutation. A separate existing bridge thread appears to track the gt shim issue; this report does not broaden WI-5003 scope to repair that shim.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
