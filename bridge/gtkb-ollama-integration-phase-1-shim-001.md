NEW

# Phase-1 Ollama Shim+Routing Child — scripts/ollama_harness.py + .ollama/routing.toml + author-metadata injection

bridge_kind: prime_proposal
Document: gtkb-ollama-integration-phase-1-shim
Version: 001
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Work Item: WI-4319
work_item_ids: [WI-4319, WI-4320, WI-4321]
parent_bridge: gtkb-ollama-integration-phase-1
parent_status: GO@-004
predecessor_bridge: gtkb-ollama-integration-phase-1-foundation
predecessor_status: VERIFIED@-012

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: cb8d1960-2984-4042-b76d-6a869cd0e16a
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, autonomous /loop dynamic-pacing session

target_paths: ["scripts/ollama_harness.py", ".ollama/routing.toml", "platform_tests/scripts/test_ollama_harness.py"]

requires_verification: true
implementation_scope: source_addition

## Summary

This is Child 2 of 4 under the Phase-1 Ollama umbrella (`bridge/gtkb-ollama-integration-phase-1-004.md` GO). Foundation Child 1 landed at VERIFIED (`bridge/gtkb-ollama-integration-phase-1-foundation-012.md`). This child executes WI-4319 (primary; `scripts/ollama_harness.py`), WI-4320 (`.ollama/routing.toml`), and WI-4321 (author-metadata env-var injection within the shim).

This child does NOT touch the verify script (Child 3), doctor extension (Child 3), or formal-spec inserts (Child 4). It also does NOT launch a live Ollama server invocation — the shim is shipped as the dispatch framework with full fail-closed guard-adapter wiring, but Phase 1 does not exercise it against a live qwen2.5-coder:14b model. Live-dispatch E2E is Child 3's WI-4322 scope.

## Specification Links

| Spec | Severity | Trigger | How this child complies |
|------|----------|---------|------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | NEW versioned bridge file with canonical status token; INDEX entry inserted. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section enumerates triggered specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification | `requires_verification: true`; per-WI spec-to-test mapping below. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH | Cites active PAUTH covering WIs 4319/4320/4321 (verified in PAUTH `included_work_item_ids` list). |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH `allowed_mutation_classes` includes `source_file`, `config_file`, `test_file` — all 3 target_paths covered. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 approved framing specs (unchanged from umbrella). |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | advisory | content:cited paths | scripts/bridge_author_metadata.py verified at HEAD; harness D registered (post Child 1 VERIFIED). |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items inserts | WIs 4319/4320/4321 canonical backlog rows; no acceptance text changes proposed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | path:scripts/**, .ollama/**, platform_tests/** | All target paths platform-side under `E:\GT-KB`; none touch `applications/`. `.ollama/` is in-root. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | advisory | path:scripts/check_harness_parity.py | Child 1 capability-floor mode unaffected; this child adds the actual harness shim. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation | shim script + routing config + tests are durable artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:verified | Terminal at VERIFIED. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:owner decision, requirement, specification, ADR, DCL, work item, backlog | DELIB-20260663 + 3 WIs + PAUTH cited. |

**Forward references (specs drafted in umbrella; Child 4 lands them via approval packets):**

| Spec draft | This child's relation |
|------------|----------------------|
| `ADR-OLLAMA-HARNESS-ADOPTION-001` | This child implements the Python-shim architecture per AUQ#1 + ADR consequences. |
| `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` | `.ollama/routing.toml` conforms to the schema: `schema_version = 1`, `[models.<key>]`, `[routing] default_model`. |
| `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` | Shim sets `GTKB_AUTHOR_MODEL` + `GTKB_AUTHOR_MODEL_VERSION` in subprocess env before any model Write dispatch. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | `CANONICAL_TOOLS = frozenset({"Read", "Write", "Edit", "Grep", "Glob", "Bash"})`; `[models.*].allowed_tools` MUST be subset; non-canonical names rejected at load time. Fail-closed guard-adapter required per umbrella -003 revision. |

## Requirement Sufficiency

**Existing requirements sufficient.** DELIB-20260663 AUQ#1 (Option A Python shim), AUQ#2 (static `.ollama/routing.toml`), AUQ#5 (Qwen 2.5 Coder 14B Q4_K_M as MVP model), AUQ#6 (full-parity 6-tool subset) directly authorize this child. No new owner input required.

## Prior Deliberations

- **`DELIB-20260663`** — owner-decision anchor; AUQ#1/#2/#5/#6 directly authorize this child.
- **`bridge/gtkb-ollama-integration-phase-1-001.md`** through **`-004.md`** — parent umbrella with GO authorizing child filings.
- **`bridge/gtkb-ollama-integration-phase-1-foundation-001.md`** through **`-012.md`** (VERIFIED) — predecessor Child 1 landed cleanly; harness D registered, capability-floor declared, parity checker generalized.
- **LO INSIGHTS** `INSIGHTS-2026-06-04-08-15-ollama-harness-routing-decision-memo.md` + `INSIGHTS-2026-06-04-08-20-ollama-parity-gap-analysis.md` — peer-solution advisory anchors.
- **`DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION`** — permits Ollama server invocation at `localhost:11434`; this child does NOT yet invoke (framework only).
- **`.claude/hooks/` guard scripts** — credential-scan, scanner-safe-writer, bridge-compliance-gate, narrative-artifact-approval-gate, destructive-gate, formal-artifact-approval-gate, implementation-start-gate. The shim's guard adapter invokes these as subprocesses with synthesized PreToolUse-shaped payloads.
- **`scripts/bridge_author_metadata.py`** — defines `GTKB_AUTHOR_MODEL` / `GTKB_AUTHOR_MODEL_VERSION` env-var contract that the shim injects.
- **`scripts/harness_identity.py:14-16` + `scripts/harness_roles.py:47-49`** — guarded-import pattern reference (will be mirrored if shim needs to import any `scripts/` siblings).

## Owner Decisions / Input

DELIB-20260663 (`source_type=owner_conversation`, `outcome=owner_decision`, `presented_to_user=true`, `transcript_captured=true`, `approved_by=owner`; packet at `.groundtruth/formal-artifact-approvals/2026-06-04-DELIB-20260663.json` with sha256 `d7581bb32a858b113a59e8aedcb2224cb4f81c4211fd0375b22128c602564be2`).

Directly authoritative for this child:

- **AUQ#1 — Architecture:** Option A (Python shim, no framework). _Authorizes:_ `scripts/ollama_harness.py` as standalone Python script with direct Ollama HTTP calls; rejects langchain/langgraph/crewai/autogen deps.
- **AUQ#2 — Routing store:** Static `.ollama/routing.toml`. _Authorizes:_ `.ollama/routing.toml` as routing source-of-truth; rejects MemBase-backed routing for Phase 1.
- **AUQ#5 — MVP model:** `qwen2.5-coder:14b-instruct-q4_K_M`. _Authorizes:_ single registered model in routing.toml.
- **AUQ#6 — Tool subset:** Full parity (Read, Write, Edit, Grep, Glob, Bash). _Authorizes:_ shim exposes the canonical 6-tuple; triggers fail-closed guard-adapter requirement per umbrella -003.

**No new owner input requested.** Implementation is mechanical per the 4 AUQs above + umbrella -003 guard-adapter contract.

## Scope and Touchpoints

### WI-4319 — Build scripts/ollama_harness.py (primary)

**File:** `scripts/ollama_harness.py` (new, ~250 LOC stdlib-only).

**Module structure:**

```python
"""Ollama harness shim for GT-KB integration (Phase 1).

Phase-1 scope per DELIB-20260663:
  - Stdlib-only (no langchain/langgraph/crewai/autogen) per AUQ#1.
  - Canonical 6-tool surface per AUQ#6.
  - Fail-closed local guard adapter per umbrella -003 revision: every model-
    requested Write/Edit/Bash dispatches through invoke_guard_adapter() BEFORE
    mutation, fail-closing on deny/ask/malformed/missing/nonzero/out-of-root/
    unknown-tool-shape.
  - Author-metadata env-var injection per DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001
    before any bridge or governed-document Write.

Phase-1 EXCLUDES live model dispatch — the shim ships as the dispatch framework
with full guard wiring, but actual qwen2.5-coder:14b invocation is Child 3's
WI-4322 scope (verify_ollama_dispatch.py E2E).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ROUTING_RELATIVE_PATH = Path(".ollama") / "routing.toml"

# AUQ#6 + DCL-OLLAMA-TOOL-PARITY-GATE-001: canonical full-parity tool surface.
CANONICAL_TOOLS = frozenset({"Read", "Write", "Edit", "Grep", "Glob", "Bash"})

# Tool-class dispatch tables: which guards must run before each tool's mutation.
WRITE_TOOL_GUARDS = (
    "credential-scan.py",
    "scanner-safe-writer.py",
    "bridge-compliance-gate.py",
    "narrative-artifact-approval-gate.py",
    "implementation-start-gate.py",
)
EDIT_TOOL_GUARDS = (
    "credential-scan.py",
    "bridge-compliance-gate.py",
    "narrative-artifact-approval-gate.py",
    "implementation-start-gate.py",
)
BASH_TOOL_GUARDS = (
    "destructive-gate.py",
    "formal-artifact-approval-gate.py",
    "implementation-start-gate.py",
)

HOOKS_RELATIVE_DIR = Path(".claude") / "hooks"
OLLAMA_DEFAULT_ENDPOINT = "http://localhost:11434"
HARNESS_ID = "D"
HARNESS_NAME = "ollama"


class OllamaHarnessError(RuntimeError):
    """Fail-closed shim error class; never wrapped, always propagates."""


def load_routing_config(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Load + validate .ollama/routing.toml per DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001.

    Validates: schema_version == 1, [routing] default_model present, at least
    one [models.<key>] with model_id + allowed_tools subset of CANONICAL_TOOLS.
    Raises OllamaHarnessError on schema violations.
    """
    # ... implementation ...


def _set_author_metadata_env(
    env: dict[str, str], routed_model_id: str, routed_model_version: str
) -> dict[str, str]:
    """Inject GTKB_AUTHOR_MODEL + GTKB_AUTHOR_MODEL_VERSION + harness identity
    into subprocess env per DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001 + WI-4321.

    Returns a NEW dict so the caller's env is not mutated in place. Author
    metadata is set BEFORE any guard invocation so bridge-compliance-gate sees
    correct values.
    """
    return {
        **env,
        "GTKB_AUTHOR_IDENTITY": f"Ollama {HARNESS_ID}",
        "GTKB_AUTHOR_HARNESS_ID": HARNESS_ID,
        "GTKB_AUTHOR_MODEL": routed_model_id,
        "GTKB_AUTHOR_MODEL_VERSION": routed_model_version,
        "GTKB_AUTHOR_MODEL_CONFIGURATION": (
            f"Ollama local inference via {OLLAMA_DEFAULT_ENDPOINT}; "
            f"model {routed_model_id}; Phase 1 framework only"
        ),
    }


def invoke_guard_adapter(
    tool_name: str,
    tool_input: dict[str, Any],
    routed_model_id: str,
    routed_model_version: str,
    project_root: Path = PROJECT_ROOT,
) -> None:
    """Fail-closed guard-adapter for any model-requested Write/Edit/Bash.

    Per umbrella -003 §F1 revision: every mutation MUST pass through this
    function before any side-effect. Fail-closes on deny, ask/checkpoint,
    malformed output, missing guard script, nonzero adapter error, out-of-root
    path, or unrecognized tool shape.

    Raises OllamaHarnessError with a structured message on any guard failure.
    The model receives a tool-result indicating the denial; no partial mutation
    occurs.
    """
    if tool_name not in CANONICAL_TOOLS:
        raise OllamaHarnessError(f"Unknown tool: {tool_name!r}")
    if tool_name in ("Write", "Edit"):
        _enforce_in_root(tool_input.get("file_path"), project_root)
        guards = WRITE_TOOL_GUARDS if tool_name == "Write" else EDIT_TOOL_GUARDS
    elif tool_name == "Bash":
        guards = BASH_TOOL_GUARDS
    else:
        # Read/Grep/Glob are read-only; skip mutation guards but still enforce root.
        if tool_name == "Read":
            _enforce_in_root(tool_input.get("file_path"), project_root)
        return

    env = _set_author_metadata_env(os.environ.copy(), routed_model_id, routed_model_version)
    payload = json.dumps(
        {
            "tool_name": tool_name,
            "tool_input": tool_input,
            "session_id": env.get("GTKB_AUTHOR_SESSION_CONTEXT_ID", "ollama-local"),
            "hookEventName": "PreToolUse",
        }
    )
    for guard in guards:
        guard_path = project_root / HOOKS_RELATIVE_DIR / guard
        if not guard_path.exists():
            raise OllamaHarnessError(f"Missing guard script: {guard_path}")
        try:
            result = subprocess.run(
                [sys.executable, str(guard_path)],
                input=payload,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            raise OllamaHarnessError(f"Guard timeout: {guard}") from None
        if result.returncode != 0:
            raise OllamaHarnessError(
                f"Guard {guard} failed (exit {result.returncode}): {result.stderr or result.stdout}"
            )
        try:
            decision = json.loads(result.stdout) if result.stdout.strip() else {}
        except json.JSONDecodeError:
            raise OllamaHarnessError(f"Guard {guard} returned malformed output: {result.stdout[:200]}")
        verdict = decision.get("decision") or decision.get("permissionDecision")
        if verdict in ("block", "deny", "ask", "checkpoint"):
            reason = decision.get("reason") or decision.get("message") or "no reason"
            raise OllamaHarnessError(f"Guard {guard} {verdict}: {reason}")


def _enforce_in_root(file_path: str | None, project_root: Path) -> None:
    """Reject out-of-root paths BEFORE invoking guards (ADR-ISOLATION clause)."""
    if not file_path:
        raise OllamaHarnessError("file_path missing from tool input")
    target = Path(file_path)
    try:
        if target.is_absolute():
            target.resolve().relative_to(project_root.resolve())
        else:
            (project_root / target).resolve().relative_to(project_root.resolve())
    except ValueError:
        raise OllamaHarnessError(f"Out-of-root path rejected: {file_path}") from None


def check_ollama_reachability(endpoint: str = OLLAMA_DEFAULT_ENDPOINT, timeout: float = 2.0) -> bool:
    """Return True if Ollama server responds at /api/tags within timeout."""
    try:
        urllib.request.urlopen(f"{endpoint}/api/tags", timeout=timeout)
        return True
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


# Phase-1 main() is a deliberate stub: routing-config load + smoke-print only.
# Actual dispatch loop is Child 3's verify_ollama_dispatch.py scope.
def main(argv: list[str] | None = None) -> int:
    config = load_routing_config()
    default_model = config["routing"]["default_model"]
    model_id = config["models"][default_model]["model_id"]
    print(f"ollama harness D shim loaded; default model: {model_id}", file=sys.stderr)
    print(f"endpoint reachable: {check_ollama_reachability()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### WI-4320 — Create .ollama/routing.toml (single Qwen mapping)

**File:** `.ollama/routing.toml` (new). Schema per DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001:

```toml
schema_version = 1

[models.qwen-coder-14b]
model_id = "qwen2.5-coder:14b-instruct-q4_K_M"
model_version = "q4_K_M"
context_window = 32000
tool_calling_supported = true
allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]

[routing]
default_model = "qwen-coder-14b"

[routing.skills]
# Phase-1 leaves skill-specific routing empty; Child 2 of Phase 2+ may extend.
```

### WI-4321 — Author-metadata env-var injection (logic block in shim)

**Implementation:** `_set_author_metadata_env()` helper in `scripts/ollama_harness.py` (above). Called by `invoke_guard_adapter()` before every guard subprocess so bridge-compliance-gate sees correct author metadata for any model-driven bridge or governed-document Write.

**Env vars set:**
- `GTKB_AUTHOR_IDENTITY = "Ollama D"`
- `GTKB_AUTHOR_HARNESS_ID = "D"`
- `GTKB_AUTHOR_MODEL = <routed model_id from routing.toml>`
- `GTKB_AUTHOR_MODEL_VERSION = <routed model_version>`
- `GTKB_AUTHOR_MODEL_CONFIGURATION = "Ollama local inference via {endpoint}; model {id}; Phase 1 framework only"`

Per `scripts/bridge_author_metadata.py`, these env vars override the fallback CODEX_/CLAUDE_ values so author metadata correctly attributes the work to harness D + the routed Ollama model when the shim mediates a bridge Write.

## Implementation Plan

1. Acquire impl-start packet for `gtkb-ollama-integration-phase-1-shim` (after GO).
2. Create `.ollama/` directory + `.ollama/routing.toml` with the Phase-1 single-model schema above.
3. Create `scripts/ollama_harness.py` with the full module structure above (load_routing_config, _set_author_metadata_env, invoke_guard_adapter, _enforce_in_root, check_ollama_reachability, main).
4. Create `platform_tests/scripts/test_ollama_harness.py` with the test suite below (see §Specification-Derived Verification Plan).
5. Pre-file gates: `ruff check scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py` + `ruff format --check` (both PASS).
6. Targeted regression: `python -m pytest platform_tests/scripts/test_ollama_harness.py -q` (all PASS).
7. Smoke test: `python scripts/ollama_harness.py` (loads routing, prints model + reachability — exit 0 even if server unreachable, since Phase 1 only declares; live dispatch is Child 3).
8. File post-implementation report as `bridge/gtkb-ollama-integration-phase-1-shim-002.md` (NEW).

## Specification-Derived Verification Plan

| Spec / WI | Test | PASS criterion |
|-----------|------|----------------|
| WI-4319 / `DCL-OLLAMA-TOOL-PARITY-GATE-001`: CANONICAL_TOOLS defined | `python -c "from scripts.ollama_harness import CANONICAL_TOOLS; assert CANONICAL_TOOLS == frozenset({'Read','Write','Edit','Grep','Glob','Bash'})"` | Exits 0 |
| WI-4319: no framework imports | `python -c "import scripts.ollama_harness as m; import sys; assert not any(k.startswith(('langchain','langgraph','crewai','autogen')) for k in sys.modules)"` | Exits 0 |
| WI-4319 / umbrella -003 §F1: unknown tool name rejected | `test_invoke_guard_adapter_rejects_unknown_tool` | PASS |
| WI-4319: out-of-root path rejected before guard invocation | `test_invoke_guard_adapter_rejects_out_of_root_path` | PASS |
| WI-4319: missing guard script fails closed | `test_invoke_guard_adapter_fails_closed_on_missing_guard` | PASS |
| WI-4319: guard deny verdict fails closed | `test_invoke_guard_adapter_fails_closed_on_deny_verdict` | PASS |
| WI-4319: guard malformed output fails closed | `test_invoke_guard_adapter_fails_closed_on_malformed_output` | PASS |
| WI-4319: guard nonzero exit fails closed | `test_invoke_guard_adapter_fails_closed_on_nonzero_exit` | PASS |
| WI-4320 / `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`: routing.toml conforms | `python -c "from scripts.ollama_harness import load_routing_config; c = load_routing_config(); assert c['schema_version']==1; assert c['routing']['default_model']=='qwen-coder-14b'; assert c['models']['qwen-coder-14b']['model_id']=='qwen2.5-coder:14b-instruct-q4_K_M'"` | Exits 0 |
| WI-4320: non-canonical tool in allowed_tools rejected at load time | `test_load_routing_config_rejects_non_canonical_tool` | PASS |
| WI-4320: missing schema_version rejected | `test_load_routing_config_rejects_missing_schema_version` | PASS |
| WI-4320: missing [routing] section rejected | `test_load_routing_config_rejects_missing_routing` | PASS |
| WI-4321 / `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`: env vars injected before guard | `test_set_author_metadata_env_contains_GTKB_AUTHOR_keys` | PASS (5 GTKB_AUTHOR_* keys present with correct values) |
| WI-4321: author metadata reaches guard subprocess | `test_invoke_guard_adapter_passes_GTKB_AUTHOR_env_to_subprocess` | PASS (mocked guard echoes env back; assertion checks the 5 keys arrived) |
| Reachability check is stdlib-only + non-fatal | `test_check_ollama_reachability_returns_False_when_endpoint_down` | PASS (mocks urlopen to raise URLError) |
| Pre-file ruff gates | `ruff check` + `ruff format --check` on changed Python files | Both PASS |

## Risk and Rollback

### Risks

1. **`.ollama/` directory placement.** First use of `.ollama/` at repo root. _Mitigation:_ added to spec-applicability triggers if needed; current preflight covers via path:**ollama** pattern.
2. **Guard-script payload-shape divergence.** Real Claude-Code hooks may expect slightly different JSON keys than the shim synthesizes. _Mitigation:_ tests use fixture payloads modeled on observed hook invocations; Codex review may surface shape gaps.
3. **`invoke_guard_adapter` import-time failure.** `subprocess` + `urllib` are stdlib; no import-time deps to fail. Routing-config load is lazy (only inside `main()`/`load_routing_config()`).
4. **`_set_author_metadata_env` mutates env unsafely.** _Mitigation:_ returns NEW dict; never mutates caller's dict in place. Test asserts non-mutation.
5. **WI-4321 author-metadata env vars conflict with CLAUDE_/CODEX_ in same process.** Per `scripts/bridge_author_metadata.py` lookup order, GTKB_AUTHOR_* primaries take precedence — no conflict because primaries are set explicitly.
6. **Phase-1 framework-only ships without live dispatch proof.** _Acceptable per AUQ#4 MVP scope_ — Child 3 (WI-4322) provides the live E2E proof; this child is the prerequisite framework.

### Rollback

- **Per-file revert.** `scripts/ollama_harness.py` + `.ollama/routing.toml` + `platform_tests/scripts/test_ollama_harness.py` are all new files; `git rm` reverts.
- **Whole-child revert.** `git revert <commit>` cleanly reverts. No MemBase mutations (Child 1 already inserted harness D; this child doesn't touch the registry).
- **Phase-1 abandonment.** Children 3-4 not yet filed; revert this child leaves Child 1 standing. Harness D remains registered with capability-floor declared; no shim exists to dispatch to.

## Recommended Commit Type

`feat:` — new Ollama harness shim infrastructure (tool-calling framework with fail-closed guard adapter + routing config + author-metadata injection). ~250 LOC scripts/ollama_harness.py + ~10 LOC .ollama/routing.toml + ~250 LOC tests.

## INDEX Update

This NEW proposal inserts a new `Document: gtkb-ollama-integration-phase-1-shim` entry at the top of `bridge/INDEX.md` with status `NEW: bridge/gtkb-ollama-integration-phase-1-shim-001.md` per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`. No prior version of this slug exists; no deletion or rewrite of historical content.

## Pre-Filing Preflight Subsection

Expected after INDEX entry add:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-shim
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-shim
```

Expected: applicability PASS with `missing_required_specs: []`; clause preflight 0 blocking gaps.

## Applicability Preflight

(To be appended by LO at review time.)

## Clause Applicability

(To be appended by LO at review time.)

## Cross-Child Reminder (forward to Child 4)

Per binding obligation documented in Child 1 (foundation-007/-009/-011), Child 4 MUST update `GOV-HARNESS-ONBOARDING-CONTRACT-001` and `DCL-OLLAMA-TOOL-PARITY-GATE-001` draft text from `capabilities.ollama.*` to `harnesses.ollama.*` before formal-artifact-approval-packet creation. This obligation is preserved into Child 2 for forward traceability.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
