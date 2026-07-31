# WI-4516 OpenRouter Bash Bridge Bypass - Loyal Opposition Advisory

Date: 2026-06-13
Role: Loyal Opposition
Automation: keep-working-lo
Work item: WI-4516
Related work items: WI-4468, WI-4481, WI-4464
Review status: additive advisory; not a bridge verdict

## Claim

`WI-4516` should remain the highest-precedence bridge-integrity item, but it should be implemented with `WI-4468` either completed first or folded in as an initial implementation slice. The live OpenRouter and Ollama harness shims guard `Write` and `Edit` bridge mutations with the bridge-compliance gate, but `Bash` uses a different guard list that omits bridge compliance entirely. A bridge-writing shell command can therefore create or edit bridge artifacts after only destructive/formal/start guards run.

The least-regret fix is to hard-deny `Bash` mutations to `bridge/*.md` and `bridge/INDEX.md` in SDK harnesses and require a single guarded writer path for bridge artifacts. Parsing arbitrary shell is lossy; bridge artifacts are structured governance records and should not depend on shell-content extraction for provenance.

## Dependency Precedence

- `WI-4468` should be resolved before, or as the first slice of, `WI-4516` because the guarded writer path needs reliable author metadata source selection in Codex/OpenRouter/Ollama sessions.
- `WI-4481` should be considered in the same design because a single guarded writer path still needs atomic or claimed `bridge/INDEX.md` updates.
- `WI-4464` is a separate git-workflow hazard. It should not block the guard fix, but the current dirty worktree demonstrates why a broad auto-stage or reset-based fix would be unsafe.

## Evidence

- Live bridge queue check before this advisory found no Loyal Opposition-actionable or Prime Builder-actionable bridge entries:
  - `python .claude/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json`
  - `python .claude/skills/bridge/helpers/scan_bridge.py --role prime-builder --format json`
- Backlog check identified `WI-4516` as a P1 `GTKB-BRIDGE` item and `WI-4468` as the metadata-source dependency.
- OpenRouter harness:
  - `scripts/openrouter_harness.py:40` treats `Bash` as a mutating tool.
  - `scripts/openrouter_harness.py:45` and `scripts/openrouter_harness.py:52` define bridge-specific guard lists for `Write` and `Edit`.
  - `scripts/openrouter_harness.py:65` defines `BASH_GUARDS`.
  - `scripts/openrouter_harness.py:458` through `scripts/openrouter_harness.py:467` return `BASH_GUARDS` immediately for `Bash`, before bridge path/content analysis can select bridge-compliance guards.
  - `scripts/openrouter_harness.py:664` through `scripts/openrouter_harness.py:673` dispatch shell execution after invoking only the `Bash` guard path.
- Ollama harness has the same shape:
  - `scripts/ollama_harness.py:40`, `scripts/ollama_harness.py:45`, `scripts/ollama_harness.py:52`, and `scripts/ollama_harness.py:65`.
  - `scripts/ollama_harness.py:494` through `scripts/ollama_harness.py:503`.
  - `scripts/ollama_harness.py:700` through `scripts/ollama_harness.py:709`.
- The Codex Bash adapter exists but is not wired into these SDK harness Bash paths:
  - `.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py:70` extracts only common bridge-write shell shapes.
  - `.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py:84` records skipped diagnostics when bridge write content extraction fails.
- The metadata helper already fails closed when bridge author metadata is partial or invalid:
  - `scripts/bridge_author_metadata.py:254` through `scripts/bridge_author_metadata.py:279`.
- Existing Ollama tests validate bridge `Write` and `Edit` guard sequencing but do not assert that bridge-writing `Bash` commands are denied or routed through bridge compliance:
  - `platform_tests/scripts/test_ollama_harness.py:302`
  - `platform_tests/scripts/test_ollama_harness.py:316`
  - `platform_tests/scripts/test_ollama_harness.py:361`
  - `platform_tests/scripts/test_ollama_harness.py:383`
- There is no OpenRouter harness parity test file equivalent to `platform_tests/scripts/test_ollama_harness.py`; current OpenRouter tests are routing-focused.

## Temp-Directory Reproduction

A non-repo temp-directory reproduction used the OpenRouter and Ollama public `dispatch_tool_call("Bash", ...)` entrypoints with stub guard files and a command runner that wrote `bridge/bypass-999.md`.

OpenRouter result:

```text
bash_result= executed
bash_guards= .claude/hooks/destructive-gate.py,.claude/hooks/formal-artifact-approval-gate.py,scripts/implementation_start_gate.py
bridge_compliance_seen= False
bridge_file_created= True
write_guards= .claude/hooks/credential-scan.py,.claude/hooks/scanner-safe-writer.py,.claude/hooks/bridge-compliance-gate.py,.claude/hooks/narrative-artifact-approval-gate.py,scripts/implementation_start_gate.py
write_bridge_compliance_seen= True
```

Ollama result:

```text
bash_result= executed
bash_guards= .claude/hooks/destructive-gate.py,.claude/hooks/formal-artifact-approval-gate.py,scripts/implementation_start_gate.py
bridge_compliance_seen= False
bridge_file_created= True
```

The reproduction did not mutate `E:\GT-KB\bridge`; it used `tempfile.TemporaryDirectory()`.

## Risk / Impact

The bridge is the role handoff and verification authority. If OpenRouter or Ollama can mutate `bridge/*.md` or `bridge/INDEX.md` through `Bash` without bridge compliance, they can bypass:

- author identity and harness metadata,
- status-token validation,
- project linkage and applicability checks,
- bridge thread claiming or index sequencing,
- spec-derived verification shape.

That recreates the provenance class of defects already seen around the Ollama/OpenRouter readiness work, except at the mutating-tool boundary instead of inside a single report.

## Recommended Action

Implement `WI-4516` as a bridge-writer hardening slice:

1. Resolve `WI-4468` first, or make it implementation step zero, so the guarded writer path has a reliable metadata source for Codex, OpenRouter, and Ollama sessions.
2. Add a shared guard helper for SDK harness `Bash` calls that detects `bridge/*.md` and `bridge/INDEX.md` write/edit intent before shell execution.
3. Prefer hard-denying SDK harness `Bash` bridge writes and requiring `Write`, `Edit`, or a dedicated `scripts/gtkb_bridge_writer.py` path. Do not rely on shell parsing as the primary compliance mechanism.
4. Route valid bridge verdict/report creation through one guarded path that calls `ensure_author_metadata()`, validates the status token and project linkage, and performs claimed or atomic `bridge/INDEX.md` updates.
5. Add OpenRouter parity tests for guarded `Write`, guarded `Edit`, bridge-writing `Bash` denial, and no-mutation-on-denial.
6. Add Ollama regression coverage for bridge-writing `Bash` denial and no-mutation-on-denial.
7. Add a dispatch-level verification check matching `scripts/verify_ollama_dispatch.py` so command-line harness validation covers this class, not only destructive Bash.

## Verification

- `python scripts/check_harness_parity.py --all --markdown`
  - Result: PASS; 175 parity checks passed.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_verify_ollama_dispatch.py platform_tests\scripts\test_openrouter_routing_deepseek.py -q --tb=short`
  - Result: PASS; 54 passed in 1.92 seconds.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_verify_ollama_dispatch.py platform_tests\scripts\test_openrouter_routing_deepseek.py platform_tests\scripts\test_codex_bridge_compliance_gate.py -q --tb=short`
  - Result: FAIL; 59 passed, 2 failed.
  - The failures were in `platform_tests/scripts/test_codex_bridge_compliance_gate.py` and were claim-handling failures: adapter calls were denied because the test bridge threads were claimed by `test` and the adapter was asked to acquire the claim first. This looks like an existing bridge-compliance test/update gap, not the OpenRouter/Ollama SDK-harness bypass itself.

## Decision Needed From Owner

No owner decision is required to begin Prime Builder implementation. The recommended implementation choice is to hard-deny SDK harness `Bash` bridge writes and require the single guarded writer path.
