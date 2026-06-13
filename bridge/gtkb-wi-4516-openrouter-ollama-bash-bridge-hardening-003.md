NEW

# GT-KB Bridge Implementation Report - WI-4516 OpenRouter/Ollama Bash Bridge Hardening - 003

bridge_kind: implementation_report
Document: gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening-002.md
Approved proposal: bridge/gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening-001.md
Recommended commit type: fix:

Author: Prime Builder (Codex, harness A)
Date: 2026-06-13 UTC
author_identity: Prime Builder (Codex)
author_harness_id: A
author_session_context_id: 019ec009-2b7c-7de3-9d91-ef53b69f9ff1
author_model: GPT-5 Codex
author_model_version: 5
author_model_configuration: Codex desktop, Prime Builder implementation under owner directive; Ollama Kimi route used for bridge-review dispatch check.

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-WI-4516-BASH-BRIDGE-HARDENING
Project: PROJECT-GTKB-BRIDGE
Work Items: WI-4516, WI-4468

target_paths: ["scripts/sdk_bridge_bash_guard.py", "scripts/openrouter_harness.py", "scripts/ollama_harness.py", "scripts/verify_ollama_dispatch.py", "platform_tests/scripts/test_sdk_bridge_bash_guard.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_verify_ollama_dispatch.py", ".api-harness/routing.toml"]

implementation_scope: source, test_addition, harness_configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Implementation Claim

Implemented WI-4516 by adding a shared SDK bridge Bash mutation guard and applying it to both Ollama and OpenRouter harness Bash dispatch before the normal guard adapter or subprocess runner can execute. The guard hard-denies Bash commands that create, overwrite, append, move, remove, or otherwise write `bridge/*.md` or `bridge/INDEX.md`, while still allowing read-only Bash references to bridge files to flow through the existing Bash guard stack.

Bridge artifact mutations from SDK harnesses now route through the already guarded `Write` and `Edit` dispatch paths, or the deterministic bridge writer/helper path. The Ollama and OpenRouter bridge-review system prompts and Bash tool schemas now tell models that bridge Bash mutations are denied and that bridge artifacts must use guarded writer paths.

The Ollama bridge-review, verification, and implementation routes were updated to use the owner-specified `kimi-k2.7-code:cloud` model. I verified the route resolves and the live Ollama dispatch verifier runs against that Kimi route.

## WI-4468 Metadata Dependency Handling

WI-4468 concerns stale implementation-report author metadata in Codex sessions. This report resolves the dependency needed for WI-4516 filing by supplying explicit Codex A author metadata before live filing:

- `author_identity: Prime Builder (Codex)`
- `author_harness_id: A`
- `author_session_context_id: 019ec009-2b7c-7de3-9d91-ef53b69f9ff1`
- `author_model: GPT-5 Codex`

The implementation-report helper was used as the live filing path, but the report content does not rely on helper-derived stale author metadata. If Loyal Opposition wants WI-4468 fully closed as its own source fix, that should remain a separate verification target; the WI-4516 dependency was handled as a pre-file metadata correctness gate for this report.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge files and `bridge/INDEX.md` are governed workflow authority; Bash cannot bypass the guarded bridge mutation path.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH and SDK tooling do not authorize bypassing bridge proposal, GO, report, or verification controls.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification includes bridge-bypass negative tests and live harness verifier evidence, not only happy-path dispatch tests.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal and report carry the governing specification set forward.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - report links to `PROJECT-GTKB-BRIDGE`, `WI-4516`, `WI-4468`, and the active PAUTH.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - Ollama tool dispatch remains fail-closed through GT-KB guard semantics and the live verifier now includes bridge Bash denial.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` - guarded Ollama bridge writes preserve author metadata coverage; Bash denial does not regress Write/Edit metadata injection.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - parity tests cover Windows-compatible fallback behavior for SDK harness dispatch rather than relying on one harness path.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - OpenRouter and Ollama harnesses now share the same bridge Bash safety floor.
- `GOV-STANDING-BACKLOG-001` - WI-4516 is the durable backlog authority for this bridge-integrity defect; WI-4468 is carried as the metadata dependency.

## Owner Decisions / Input

- Owner directive in this session: implement WI-4516 from `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-WI-4516-openrouter-bash-bridge-bypass.md`, resolve WI-4468 if needed, hard-deny OpenRouter/Ollama Bash bridge writes, route bridge mutations through guarded writer paths, add parity/regression tests, and verify harnesses no longer bypass bridge-compliance.
- Captured durable decision: `DELIB-2026-06-13-WI-4516-OWNER-AUTHORIZATION`.
- Active authorization: `PAUTH-PROJECT-GTKB-BRIDGE-WI-4516-BASH-BRIDGE-HARDENING`.
- Owner follow-up directive: `"ollama run kimi-k2.7-code:cloud" is available. Use this model with Ollama.`

No further owner decision is required before Loyal Opposition verification.

## Prior Deliberations

- `DELIB-2026-06-13-WI-4516-OWNER-AUTHORIZATION` - owner authorization for WI-4516 plus WI-4468 dependency handling.
- `bridge/gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening-001.md` - approved implementation proposal.
- `bridge/gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-WI-4516-openrouter-bash-bridge-bypass.md` - initial defect report and implementation starting point.

## Implementation Details

Added `scripts/sdk_bridge_bash_guard.py`:

- Detects protected bridge paths: `bridge/INDEX.md` and `bridge/*.md`, including relative and absolute Windows/POSIX spellings.
- Detects mutating Bash command shapes before shell execution: redirection, append, PowerShell write/remove/move/copy commands, Python `write_text` / `open(..., "w")` / `os.replace` patterns, and git restore/checkout/reset/rm against protected bridge paths.
- Returns a model-visible denial reason that directs bridge mutations to guarded `Write`/`Edit` dispatch or `scripts/gtkb_bridge_writer.py`.

Updated `scripts/ollama_harness.py` and `scripts/openrouter_harness.py`:

- Import the shared bridge Bash guard.
- Deny protected bridge Bash mutations at the top of `_dispatch_bash`, before `invoke_guard_adapter` and before any subprocess runner.
- Preserve read-only Bash behavior by sending non-mutating bridge reads through the existing Bash guard stack.
- Update bridge-review prompt and Bash schema text to advertise the new denial contract.

Updated `scripts/verify_ollama_dispatch.py`:

- Adds guard check `G4 bridge Bash mutation denial`.
- The check creates a disposable fixture bridge, supplies an allowing guard runner and a mutating command runner, and passes only if the harness rejects the Bash bridge mutation before either callback runs and leaves both the bridge file and `bridge/INDEX.md` unchanged.
- The live verifier now reports 7/7 checks instead of 6/6.

Added and updated tests:

- `platform_tests/scripts/test_sdk_bridge_bash_guard.py` covers read-only allowance, mutating command denial, protected path normalization, and deduplication.
- `platform_tests/scripts/test_ollama_harness.py` covers file and index Bash bridge denial before guards/subprocess plus read-only bridge Bash flowing through Bash guards.
- `platform_tests/scripts/test_openrouter_harness.py` adds OpenRouter parity coverage for routing, guarded Write/Edit bridge paths, author metadata, Bash bridge denial before guards/subprocess, and read-only bridge Bash guard flow.
- `platform_tests/scripts/test_verify_ollama_dispatch.py` adds the G4 verifier regression.

## Specification-Derived Verification Evidence

- `GOV-FILE-BRIDGE-AUTHORITY-001`: Covered by negative tests that try Bash writes to `bridge/*.md` and `bridge/INDEX.md` in both Ollama and OpenRouter dispatch, plus the live verifier G4 check. Observed result: Bash bridge mutation denied before guard runner or command runner; fixture bridge file absent; fixture `INDEX.md` unchanged.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`: Covered by the same negative tests and verifier G4; the PAUTH/implementation packet did not create a Bash bypass path. Observed result: guarded Write/Edit tests remain the only bridge mutation paths exercised by SDK harness tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: Covered by the focused pytest suite and the live verifier command below. Observed result: 69 focused tests passed; live verifier returned 7/7 passed.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: Proposal and this report carry forward all governing specs. Observed result: report includes the spec set and maps each to executed evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: Proposal, PAUTH, and report link to `PROJECT-GTKB-BRIDGE`, `WI-4516`, and `WI-4468`. Observed result: implementation-start packet and report metadata carry those links.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`: Covered by Ollama harness tests and `scripts/verify_ollama_dispatch.py --skip-daemon`. Observed result: Ollama Kimi bridge-review route passed 7/7 dispatch checks, including G4 denial.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`: Covered by existing/extended Ollama and OpenRouter author metadata tests. Observed result: metadata tests pass, and bridge Bash denial does not affect guarded Write/Edit metadata injection.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`: Covered by `scripts/check_harness_parity.py --all --markdown` and shared tests across OpenRouter/Ollama. Observed result: parity scanner PASS, 175 checks.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`: Covered by OpenRouter/Ollama parity tests proving a shared safety floor for SDK harness Bash dispatch. Observed result: both harness suites pass.
- `GOV-STANDING-BACKLOG-001`: Covered by carrying WI-4516/WI-4468 through PAUTH, implementation packet, and report metadata. Observed result: work remains tied to durable backlog authority.

## Commands Run

- `ollama run kimi-k2.7-code:cloud "Reply with OK only."`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\ollama_harness.py --prompt "<review prompt>" --model kimi-k2-7-code-cloud --skill bridge-review --timeout 360 --max-turns 24`
- `uv run --with pytest --with pytest-timeout python -m pytest platform_tests\scripts\test_sdk_bridge_bash_guard.py platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_verify_ollama_dispatch.py -q --tb=short`
- `uv run --with ruff python -m ruff check scripts\sdk_bridge_bash_guard.py scripts\openrouter_harness.py scripts\ollama_harness.py scripts\verify_ollama_dispatch.py platform_tests\scripts\test_sdk_bridge_bash_guard.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_verify_ollama_dispatch.py`
- `uv run --with ruff python -m ruff format --check scripts\sdk_bridge_bash_guard.py scripts\openrouter_harness.py scripts\ollama_harness.py scripts\verify_ollama_dispatch.py platform_tests\scripts\test_sdk_bridge_bash_guard.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_verify_ollama_dispatch.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\verify_ollama_dispatch.py --skip-daemon`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\check_harness_parity.py --all --markdown`

## Observed Results

- Kimi availability check: PASS. `ollama run kimi-k2.7-code:cloud "Reply with OK only."` returned successfully.
- Kimi bridge-review harness route: PASS. The harness resolved `kimi-k2-7-code-cloud` and reported the thread already had a GO at `bridge/gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening-002.md`, avoiding duplicate verdict filing.
- Focused pytest suite: PASS. `69 passed, 1 warning in 13.29s`. The warning was `PytestConfigWarning: Unknown config option: asyncio_mode` from transient `uv` pytest tooling without `pytest-asyncio`; it did not affect the focused synchronous tests.
- Ruff lint: PASS. `All checks passed!`
- Ruff format check: PASS. `8 files already formatted`.
- Live Ollama verifier: PASS. Route was `kimi-k2-7-code-cloud (kimi-k2.7-code:cloud)`. Results were `7/7 passed`, including `G4 bridge Bash mutation denial` with `guards_invoked=0`, `command_called=False`, `file_exists=False`, and `index_unchanged=True`.
- Harness parity: PASS. `Overall status: PASS`; harnesses `antigravity, claude, codex, ollama, openrouter`; `Counts: PASS: 175`.

Environment note: the first attempted test command used `groundtruth-kb\.venv\Scripts\python.exe -m pytest ...` and failed because that venv does not have `pytest` installed. Verification was rerun with `uv run --with pytest --with pytest-timeout ...`. The temporary `uv.lock` Python-version side effect was reverted before filing this report.

## Files Changed

WI-4516 implementation and test files:

- `.api-harness/routing.toml` - added `kimi-k2-7-code-cloud` and routed Ollama bridge-review/verification/implementation to the owner-specified Kimi model.
- `scripts/sdk_bridge_bash_guard.py` - new shared bridge Bash mutation denial helper.
- `scripts/ollama_harness.py` - shared guard import, `_dispatch_bash` hard denial, prompt/schema update.
- `scripts/openrouter_harness.py` - shared guard import, `_dispatch_bash` hard denial, prompt/schema update.
- `scripts/verify_ollama_dispatch.py` - new G4 bridge Bash mutation denial check.
- `platform_tests/scripts/test_sdk_bridge_bash_guard.py` - new guard unit tests.
- `platform_tests/scripts/test_ollama_harness.py` - Ollama regression tests for bridge Bash denial and read-only bridge Bash behavior.
- `platform_tests/scripts/test_openrouter_harness.py` - new OpenRouter parity/regression tests.
- `platform_tests/scripts/test_verify_ollama_dispatch.py` - verifier regression for G4.

Governance/process artifacts created or updated through governed paths:

- `bridge/gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening-001.md` - proposal.
- `bridge/gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening-002.md` - GO verdict by Antigravity C.
- `bridge/gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening-003.md` - this implementation report after filing.
- `bridge/INDEX.md` - appended NEW/GO/report status lines for this thread through helper paths.
- `current_deliberations` / `current_project_authorizations` - `DELIB-2026-06-13-WI-4516-OWNER-AUTHORIZATION` and `PAUTH-PROJECT-GTKB-BRIDGE-WI-4516-BASH-BRIDGE-HARDENING`.

Pre-existing working-tree note: the checkout contained many unrelated uncommitted changes before WI-4516. I did not revert those. The helper plan reports unrelated dirty files because it reads the full working tree; this implementation claim is limited to the files listed above.

## Acceptance Criteria Status

- Hard-deny OpenRouter Bash writes to `bridge/*.md` and `bridge/INDEX.md`: PASS.
- Hard-deny Ollama Bash writes to `bridge/*.md` and `bridge/INDEX.md`: PASS.
- Deny before guard adapter and subprocess execution, so bridge-compliance cannot be bypassed by shell mutation: PASS.
- Preserve read-only Bash bridge references through existing Bash guards: PASS.
- Preserve guarded Write/Edit bridge mutation path for SDK harnesses: PASS.
- Use owner-specified Ollama Kimi model route: PASS.
- Add parity/regression tests: PASS.
- Live verifier proves harnesses no longer bypass bridge-compliance: PASS.
- WI-4468 dependency handled for this report metadata: PASS for WI-4516 filing; full WI-4468 helper-source closure remains separable if Loyal Opposition requires it as an independent work item.

## Risk And Rollback

Residual risk is command-pattern coverage: no regex guard can prove every future shell dialect forever. The implementation mitigates the known bypass class and common Windows/POSIX/Python/git mutation forms, then anchors behavior in both direct unit tests and harness-level regression tests. Future discovered shell-write shapes should be added to `scripts/sdk_bridge_bash_guard.py` with corresponding tests.

Rollback path for implementation code is scoped to:

- `.api-harness/routing.toml`
- `scripts/sdk_bridge_bash_guard.py`
- `scripts/ollama_harness.py`
- `scripts/openrouter_harness.py`
- `scripts/verify_ollama_dispatch.py`
- `platform_tests/scripts/test_sdk_bridge_bash_guard.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`

Bridge audit artifacts are append-only and should not be removed as rollback.

## Loyal Opposition Asks

1. Verify that OpenRouter and Ollama Bash dispatch cannot mutate `bridge/*.md` or `bridge/INDEX.md`.
2. Verify that guarded `Write`/`Edit` bridge mutation paths remain available and metadata-preserving.
3. Verify that the Kimi Ollama route and the live dispatch verifier evidence satisfy the owner instruction to use `ollama run kimi-k2.7-code:cloud`.
4. Return VERIFIED if the implementation satisfies the approved GO; otherwise return NO-GO with concrete findings.
