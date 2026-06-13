NEW

# Windows Spawn No-Window Flag for Bridge-Dispatch Subprocesses

bridge_kind: implementation_proposal
Document: gtkb-wi-4529-windows-spawn-no-window-creationflags
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-13 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 310b54b9-81d9-4fe5-b68e-f3340e9d9c42
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: Claude Code interactive; Prime Builder durable role; autonomous Prime Builder loop cycle 1

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4529-WINDOWS-SUBPROCESS-CREATE-NO-WINDOW
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4529

target_paths: ["scripts/run_with_status.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "platform_tests/scripts/test_run_with_status.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

On 2026-06-13 the owner directly observed empty `C:\Python314\python.exe`
console windows accumulating on screen during normal autonomous swarm
activity. Diagnosis identified the cause: `scripts/run_with_status.py` line 67
wraps every dispatched harness command via `subprocess.Popen(cmd_args, ...)`
without passing `creationflags`. On Windows, this allocates a console window
per child for the duration of the wrapped process — and because the wrapped
processes redirect stdout/stderr to dispatch-run log files, the windows are
visually empty. The cross-harness trigger's own outer Popen sites
(`scripts/cross_harness_bridge_trigger.py:1398, 2488`) already pass
`creationflags=CREATE_NO_WINDOW|CREATE_NEW_PROCESS_GROUP` on Windows, so the
trigger itself is silent — but the wrapper it spawns is not, and the wrapper
is what carries the harness through its entire run.

This proposal adds the same Windows-only `creationflags` discipline to the
wrapper and to the inner `subprocess.run(...)` sites in the harness shims
that execute worker-side tool calls (Bash / external commands) during a
dispatched run.

Two changes:

1. **Primary fix (single defect).** In `scripts/run_with_status.py`,
   construct a `creationflags` value mirroring the cross-harness trigger's
   pattern: on `os.name == "nt"`,
   `creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)`;
   on non-Windows, `creationflags = 0`. Pass `creationflags=creationflags`
   to the `subprocess.Popen(...)` call at line 67. This eliminates the
   wrapped harness's console window for the entire duration of a
   dispatched run.

2. **Defense in depth (inner harness tool-call subprocess sites).** In
   `scripts/ollama_harness.py` (lines ~452 and ~697) and
   `scripts/openrouter_harness.py` (lines ~416 and ~665) — the
   `subprocess.run(...)` call sites that execute worker-side tool calls
   (Bash commands the LLM emits during a review) — apply the same
   Windows-conditional `creationflags`. These would only flash windows
   when the dispatched harness itself runs a Windows-CLI tool call, but
   the discipline matches the wrapper and prevents future regressions.

Together: every subprocess in the bridge-dispatch path (trigger → wrapper →
harness → tool calls) consistently passes the no-window flag on Windows.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge dispatch is the canonical bridge
  protocol surface; this proposal hardens the dispatch substrate's UX
  hygiene without changing dispatch semantics.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal
  cites all relevant governing specs (this list).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project, WI, and
  PAUTH metadata are present in the body header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan
  below maps each linked spec to a derived test.
- `REQ-HARNESS-REGISTRY-001` — the dispatched harnesses (D ollama, F
  openrouter) launch through `invocation_surfaces.argv` values from the
  registry; this proposal does not change the registry or the argv values,
  only the Windows creationflags applied to the wrapping subprocess.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — Windows-conditional behavior derives
  from a fresh `os.name` check at spawn time (clause c: fresh canonical
  reads at the moment of decision).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — preserves the artifact graph:
  WI-4529 → DELIB-20263188 → PAUTH-...-WI-4529-WINDOWS-SUBPROCESS-CREATE-NO-WINDOW
  → this bridge proposal → derived tests → eventual VERIFIED record.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — this proposal participates in the
  bridge thread lifecycle (NEW → GO → implementation report → VERIFIED)
  and the WI-4529 lifecycle (candidate → active → resolved).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — owner decision captured via chat
  authorization → DELIB → PAUTH → bridge proposal, with the WI created
  and the project authorization triple validated before scaffold.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changed paths
  (`scripts/run_with_status.py`, `scripts/ollama_harness.py`,
  `scripts/openrouter_harness.py`,
  `platform_tests/scripts/test_run_with_status.py`) are inside `E:\GT-KB`;
  no change to `applications/` or the application-placement boundary.

## Prior Deliberations

- `DELIB-20263188` (recorded this session, 2026-06-13) — owner_conversation
  / owner_decision capturing the owner's explicit chat authorization to
  capture and address WI-4529. Direct authorization basis for this
  proposal.

A deliberation search was run as part of the mandatory pre-propose sweep
("Windows dispatch subprocess console window CREATE_NO_WINDOW pythonw flash")
and returned no matches; no other prior deliberations bear on the
Windows-console-window UX defect or on subprocess.Popen creationflags
discipline at the bridge-dispatch substrate. The scaffold seeded five
unrelated `DELIB-S*` candidates by glossary similarity (proposal-standards,
skill-modernization, impl-auth verification-heading, Codex Windows hook
parity); on inspection none bear on Windows subprocess creationflags
discipline. They are pruned here rather than carried as decorative
citations.

## Owner Decisions / Input

This proposal depends on owner approval. The authorizing evidence:

- `OWNER-CHAT-2026-06-13-WI4529` (chat exchange this session, 2026-06-13):
  owner observed empty `C:\Python314\python.exe` console windows
  accumulating during active swarm activity, requested diagnosis, and on
  the question "Want me to capture this as a backlog item right now?"
  responded "Yes." This is the owner-decision capture that backs the
  WI-4529 creation and the bounded PAUTH minted from it.

Both the observation and the capture authorization are recorded durably
in `DELIB-20263188` (source_type `owner_conversation`, outcome
`owner_decision`, work_item_id `WI-4529`). No further owner decision is
required to file this proposal; LO review is the next gate.

## Requirement Sufficiency

Existing requirements sufficient. The behavior this proposal adds is
governed by the cited specs:

- `REQ-HARNESS-REGISTRY-001` defines the dispatched harness surface; this
  proposal does not change registry semantics, only the wrapper's UX
  behavior on Windows.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` clause (c) authorizes pre-action
  decisions from fresh canonical state — here, `os.name == "nt"` is the
  canonical platform check.
- The cross-harness trigger's existing `creationflags` pattern at
  `scripts/cross_harness_bridge_trigger.py:1392-1404` is the in-tree
  precedent this proposal applies consistently to the wrapper and the
  harness shim inner subprocesses.

No new requirement or specification is needed before implementation.

## Spec-Derived Verification Plan

One new pytest, plus the standard code-quality gates on changed files.
Reuse the project venv interpreter for reproducible evidence.

| Linked spec | Derived test / verification | Expected result |
|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` + `REQ-HARNESS-REGISTRY-001` (the wrapper's spawn decision derives from fresh `os.name` and the registry-defined argv vector) | New test in `platform_tests/scripts/test_run_with_status.py`: `test_popen_uses_create_no_window_on_windows_via_monkeypatch`. Monkeypatch `os.name = "nt"` and `subprocess.Popen` with a recording stub; invoke `run_with_status.main([status_file, "python", "--version"])` against a synthetic status file. | Assert the recording stub captured `creationflags` containing `CREATE_NO_WINDOW` (`0x08000000`) when `os.name == "nt"`. Companion negative-case test asserts `creationflags == 0` when `os.name != "nt"`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` + `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` + `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` + `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` (this proposal/report carries the citations through) | Bridge applicability preflight + clause preflight on this slug; preserved in the implementation report. | `preflight_passed: true`, `missing_required_specs: []`; clause preflight exit 0, `Blocking gaps: 0`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (all changed paths in-root) | `git diff --stat` review in the implementation report. | All paths under `E:\GT-KB`; none under `applications/`. |
| All changed-file Python conformance | `groundtruth-kb/.venv/Scripts/ruff.exe check <changed.py>` and `... ruff format --check <changed.py>` on each of the four target_paths. | Exit 0 for both on every changed file. |

Test execution commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_run_with_status.py -q --no-header
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/run_with_status.py scripts/ollama_harness.py scripts/openrouter_harness.py platform_tests/scripts/test_run_with_status.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/run_with_status.py scripts/ollama_harness.py scripts/openrouter_harness.py platform_tests/scripts/test_run_with_status.py
```

## Risk / Rollback

**Risk surface.** The wrapper is used by every dispatched harness run, so a
regression here would break every dispatch. Mitigations:

- The change is the *standard* in-tree `creationflags` pattern already
  used by the cross-harness trigger at the outer Popen sites
  (`cross_harness_bridge_trigger.py:1392-1404`); this proposal applies the
  same pattern to the wrapper. There is no design novelty.
- Non-Windows behavior is unchanged: `creationflags = 0` is the
  pre-existing default for `subprocess.Popen` on non-Windows platforms;
  passing `0` explicitly is a no-op.
- Windows behavior change is purely cosmetic (suppress console window);
  the wrapped process's stdin/stdout/stderr handling is unchanged, the
  exit code propagation is unchanged, and the dispatch-run log files are
  unchanged.
- The change is bounded to ~3-5 lines per call site (4 sites total) and
  is covered by a Windows-monkeypatch unit test.
- The inner harness shim subprocess sites (defense-in-depth) only affect
  tool-call execution within a dispatched LO worker; even an outright bug
  there would only surface during a worker's Bash tool call, not on the
  trigger hot path.

**Rollback.** Revert the changes to the four target files. No schema, no
MemBase, no state migration. The pre-existing `subprocess.Popen(...)`
behavior returns immediately. Rollback is a single-commit revert.

Related but out of scope: `WI-4525` (dispatch-interpreter doctor check;
in-flight by another session, dispatch-launchability scope), `WI-4526`
(trigger-CLI lock contention; data-only race). No conflict; this proposal
adds `creationflags` arguments, those are orthogonal subjects.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the
top of the `gtkb-wi-4529-windows-spawn-no-window-creationflags` document
list in `bridge/INDEX.md`; no prior version is deleted or rewritten
(append-only). `bridge/INDEX.md` remains the canonical workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`fix:` — corrects a latent Windows UX defect in the dispatch wrapper (the
wrapper was always missing the `creationflags` argument that the outer
trigger already had); not a new capability surface (the discipline already
exists at the trigger level), not a refactor (behavior changes from
"console window flashes" to "no console window"). Defense-in-depth
additions to the harness shims are part of the same fix surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
