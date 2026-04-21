NO-GO

# GT-KB Phase 4C Structured Logging Migration - Loyal Opposition Review

**Review date:** 2026-04-16
**Reviewed proposal:** `bridge/gtkb-phase4c-structured-logging-001.md`
**Target checkout:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target HEAD verified:** `8efcbb1`

## Verdict

NO-GO until the proposal is revised. The stdlib logging direction is sound, but the current proposal has two release-blocking issues:

1. The proposed CI `print()` guard is not baseline-clean and would fail on existing intentional protocol output.
2. The proposed logging configuration is only wired through `gt`, while the bridge modules being migrated are also direct module entry points and background services.

The proposal also misstates the scan-status boundary and uses an exit criterion that is not supported by the proposed log sites.

## Prior Deliberations

No DELIB IDs were found for this exact structured-logging migration topic. A repo search in Agent Red for `structured logging migration groundtruth-kb bridge poller worker`, `Phase 4C`, `_append_log`, and `GROUNDTRUTH_LOG_LEVEL` found prior bridge and planning context, but not an archived deliberation ID for this proposal.

Relevant non-DELIB context:

- `groundtruth-kb/docs/reports/v0.4-baseline/logging.md:78-109` recommends introducing `logging.getLogger(__name__)` in bridge/db paths and explicitly says the replacement should write to the same log file path.
- `groundtruth-kb/docs/reports/phase-4b-plan.md:23-30` lists logging infrastructure as 0 logging uses in `src/`, with Phase 4C as the proposed coverage.

## Evidence Checked

- `git rev-parse --short HEAD` in `groundtruth-kb` returned `8efcbb1`, matching the proposal.
- `rg -n "^import logging|^from logging" src/groundtruth_kb -g "*.py"` found 0 logging imports.
- `rg -n "def _append_log|_append_log\(" src/groundtruth_kb/bridge/poller.py src/groundtruth_kb/bridge/worker.py` found 18 poller matches and 18 worker matches including the helper definitions.
- `rg -n "^\s*print\(" src/groundtruth_kb -g "*.py"` found 23 existing `print()` sites outside `__main__.py`.

## Findings

### Finding 1 - Proposed CI print guard would fail immediately

**Severity:** High

The proposed CI guard:

```bash
grep -rn "^\s*print(" src/groundtruth_kb/ --include="*.py" \
  | grep -v "__main__.py" \
  | grep -v "# print-ok"
```

would match current, intentional `print()` sites. Evidence from `rg -n "^\s*print\(" src/groundtruth_kb -g "*.py"`:

- `src/groundtruth_kb/governance/output.py:18`, `:32`, `:55`, `:70` emit structured Claude hook JSON/stdout. The file docstring at `src/groundtruth_kb/governance/output.py:2-5` says all hooks use this module to emit structured JSON output to stdout.
- `src/groundtruth_kb/bridge/launcher.py:290`, `:292`, `:304`, `:306`, `:335`, `:337`, `:355`, `:357` emit JSON or `{}` for hook/launcher interop.
- `src/groundtruth_kb/bridge/handshake.py:142-174` emits JSON and human-readable handshake results.
- `src/groundtruth_kb/bridge/poller.py:459` emits argument validation to stderr and `src/groundtruth_kb/bridge/poller.py:552` emits once-mode JSON.
- `src/groundtruth_kb/bridge/runtime.py:1642` emits the direct module error when MCP is absent.

This conflicts with the proposal's own "No changes to hook output" scope. It also means the CI gate would fail before it detects any newly introduced print call.

**Required action:** Replace the grep guard with a baseline-clean policy. Acceptable options:

- Use an AST-based test with an explicit allowlist for protocol-output modules and line/function categories.
- Annotate existing intentional print sites with a documented `# print-ok` convention as part of the proposal, including hook/bridge protocol rationale.
- Scope the CI guard only to modules where bare print is actually prohibited, and add a test proving the guard passes the current baseline before implementation.

### Finding 2 - Bridge logging configuration will not reach direct bridge entry points

**Severity:** High

The proposal adds `configure_logging()` and calls it from `src/groundtruth_kb/cli.py`, but the modules being migrated are not only reached through the `gt` console script.

Evidence:

- `pyproject.toml:54-55` defines only `gt = "groundtruth_kb.cli:main"`.
- `src/groundtruth_kb/bridge/launcher.py:115-119` and `:162-165` launch the resident worker with `-m groundtruth_kb.bridge.worker`.
- `src/groundtruth_kb/bridge/worker.py:1010-1018` has its own `main()` that parses args and calls `run()` directly.
- `src/groundtruth_kb/bridge/poller.py:688-693` has its own direct `main()`.
- `src/groundtruth_kb/bridge/launcher.py:144-148` starts the Windows worker hidden with `Start-Process`; there is no stdout/stderr redirection in that fallback path.

If `_append_log()` calls are replaced with `_log.info()` but logging is configured only by `gt`, bridge direct runs can lose INFO diagnostics. In the hidden Windows fallback path, default stderr logging is especially risky because there may be no visible or persisted stderr sink.

This also conflicts with the Phase 4A baseline recommendation at `docs/reports/v0.4-baseline/logging.md:92`: "The existing `_append_log` helper can be replaced with a `logging.getLogger("groundtruth_kb.bridge.poller")` call that writes to the same log file path."

**Required action:** Revise the proposal to define logging setup for every executable path affected by the migration:

- `gt` CLI entry point.
- `python -m groundtruth_kb.bridge.poller`.
- `python -m groundtruth_kb.bridge.worker`.
- `python -m groundtruth_kb.bridge.launcher` if it adds diagnostics.
- Any hook/protocol entry point if logging is added there.

The revision must also state whether bridge diagnostics continue writing to the current per-project files (`.claude/hooks/.bridge-poller-{agent}.log` and `.claude/hooks/.{agent}-bridge-worker.log`) or move to stderr. If they move to stderr, the proposal must update scheduler/launcher contracts and tests to prove logs are still observable in Windows hidden/background operation.

### Finding 3 - Scan-status boundary is misstated

**Severity:** Medium

The proposal says: "The `_append_log()` calls that write to scan-status files (claude-scan-status.json, codex-scan-status.json) are NOT migrated." In the target checkout, `_append_log()` does not write those scan-status files.

Evidence:

- `src/groundtruth_kb/bridge/poller.py:145-153` appends text lines to the path passed in.
- `src/groundtruth_kb/bridge/poller.py:469` sets that path to `.claude/hooks/.bridge-poller-{agent}.log`.
- `src/groundtruth_kb/bridge/worker.py:98-100` defines the worker log path as `.claude/hooks/.{agent}-bridge-worker.log`.
- `src/groundtruth_kb/bridge/worker.py:123-135` appends text lines to that worker log.
- `src/groundtruth_kb/project/doctor.py:545-568` reads scan-status JSON from `independent-progress-assessments/bridge-automation/logs/{agent}-scan-status.json`; that is a separate file-bridge liveness contract.

The migration boundary should be stated in terms of exact files and helper functions, not "scan-status `_append_log()` calls" that do not exist in the target code.

**Required action:** Correct the proposal's scope language. Explicitly preserve state/status JSON writers/readers such as poller state JSON, worker health JSON, and doctor scan-status readers, while migrating only human-readable diagnostic lines.

### Finding 4 - Exit criterion 6 is not supported by the proposed log sites

**Severity:** Medium

Exit criterion 6 says `GROUNDTRUTH_LOG_LEVEL=DEBUG gt project doctor` should produce diagnostic output on stderr. The proposal's concrete new log sites are bridge modules and `db.py` fallback/migration paths. `gt project doctor` does not instantiate `KnowledgeDB` or call the bridge poller/worker paths.

Evidence:

- `src/groundtruth_kb/project/doctor.py:742-788` builds checks by calling system/project check helpers.
- `src/groundtruth_kb/project/doctor.py:266-279` checks the SQLite DB schema with `sqlite3` directly, not through `KnowledgeDB`.
- The proposed bridge logging sites are direct background-service paths, not `gt project doctor` paths.

Unless the revision adds intentional doctor-level logging, this exit criterion can pass through the logging configuration path but still emit no diagnostic log records.

**Required action:** Either add explicit doctor diagnostics and tests for them, or replace the exit criterion with commands that exercise the proposed log sites, for example:

- a bridge poller/worker direct-entry smoke with `GROUNDTRUTH_LOG_LEVEL=DEBUG`;
- a ChromaDB fallback search test that asserts a warning record via `caplog`;
- a migration test that asserts INFO records when logging is configured to INFO/DEBUG.

## Conditions For GO

1. Revise the CI print guard so it passes the current baseline and preserves intentional protocol stdout.
2. Define logging configuration for every affected entry point, not only `gt`.
3. Preserve or explicitly replace the existing bridge diagnostic sink with tested operator-visible behavior.
4. Correct the scan-status scope language and list the exact state/status files that remain unchanged.
5. Replace or implement the `gt project doctor` debug-output exit criterion.
6. Include focused tests for configuration, direct bridge entry logging, ChromaDB fallback warning, migration INFO logging, and baseline-clean no-bare-print enforcement.

## Owner Decision Needed

No owner decision is needed on the direction of using stdlib logging. A Prime revision is needed to choose the bridge diagnostic sink: keep the current per-project log files via logging file handlers, or formally move diagnostics to stderr and update scheduler/launcher contracts accordingly.
