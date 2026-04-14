# Logging and Output Usage Inventory (Phase 4A)

Generated 2026-04-14 against `groundtruth-kb` commit `993f31b8d42ac272b9716c191527b599d08ba632`.

Source:
```
grep -rn "import logging|logger *=|click\.echo|^\s*print(" src/groundtruth_kb/
```

## Baseline totals

| Pattern | Count | Classification |
|---|---:|---|
| `click.echo` | 111 | User-facing CLI output (correct) |
| `print(...)` | 19 | Mixed (see below) |
| `import logging` | **0** | **Not used anywhere in `src/`** |
| `logger = logging.getLogger(...)` | **0** | **Not used anywhere in `src/`** |
| **Total output sites** | **130** | |

**Headline finding: groundtruth-kb uses no Python `logging` module anywhere in `src/`.** All output is either `click.echo` (via Click, correct for CLI user output) or bare `print()`.

This is a measurement observation, not a defect. A small single-purpose CLI tool can legitimately forgo `logging` in favor of `click.echo` for user output. However, Phase 4B should decide whether diagnostic logging (for background services like the bridge poller) is needed.

## click.echo distribution

All 111 `click.echo` sites are in **`cli.py`**. They are all user-facing CLI command output — exactly where `click.echo` belongs (it handles Click's output redirection, testing, and Unicode encoding).

No classification action needed for `click.echo` sites. They are the "right" pattern for their purpose.

## print() site classification

All 19 bare `print()` sites are in the `bridge/` subpackage (plus one in `bridge/runtime.py`).

### Category A — machine-readable JSON output (13 sites)

These are `print(json.dumps(...))` or `print("{}")` patterns that emit structured JSON to stdout. They are correct for a CLI tool whose stdout is being piped to another tool (the bridge workflow).

| File:Line | Pattern |
|---|---|
| `bridge/handshake.py:141` | `print(json.dumps(failure))` |
| `bridge/handshake.py:144` | `print(json.dumps(send_result, indent=2))` |
| `bridge/handshake.py:161` | `print(json.dumps(success))` |
| `bridge/handshake.py:170` | `print(json.dumps(timeout))` |
| `bridge/launcher.py:287` | `print(json.dumps(payload))` |
| `bridge/launcher.py:289` | `print("{}")` (empty response) |
| `bridge/launcher.py:301` | `print(json.dumps(payload))` |
| `bridge/launcher.py:303` | `print("{}")` |
| `bridge/launcher.py:332` | `print(json.dumps(payload))` |
| `bridge/launcher.py:334` | `print("{}")` |
| `bridge/launcher.py:352` | `print(json.dumps(payload))` |
| `bridge/launcher.py:354` | `print("{}")` |
| `bridge/poller.py:478` | Multi-line `print(` — needs context check |

**Classification:** safe usage. Converting these to `click.echo` would be a no-op (click.echo just wraps click's output handling). No change recommended.

### Category B — human-readable prose (5 sites)

These print human-readable strings to stdout.

| File:Line | Pattern |
|---|---|
| `bridge/handshake.py:143` | `print(failure["error"])` |
| `bridge/handshake.py:163` | `print(f"Prime operating-state reply received: {success['reply_summary']}")` |
| `bridge/handshake.py:172` | `print(timeout["error"])` |
| `bridge/handshake.py:173` | `print(f"Bridge thread: {thread_id}")` |
| `bridge/runtime.py:1455` | `print("MCP (FastMCP) is not installed. Install 'mcp' package for MCP server support.")` |

**Classification:** mostly fine, but inconsistent with the `cli.py` convention of `click.echo`. The runtime.py:1455 line is a user-facing help message for a missing optional dependency — arguably should be on stderr with an exit path, not a plain print. Phase 4B should decide.

### Category C — stderr errors (1 site)

| File:Line | Pattern |
|---|---|
| `bridge/poller.py:386` | `print("bridge_poller: agent must be 'codex' or 'prime'", file=sys.stderr)` |

**Classification:** correct. Argument validation error to stderr is the right pattern.

## Absence of diagnostic logging

The **zero `import logging`** finding is significant:

- **CLI commands** (111 echo sites): appropriate — Click handles its own output.
- **Bridge runtime** (`bridge/poller.py`, `bridge/launcher.py`, `bridge/worker.py`, `bridge/runtime.py`): these run as long-lived background services. They currently write to log files via `_append_log(log_file, ...)` helper (seen in the exception audit), but they have NO `logging.getLogger(__name__)` integration.
- **Database layer** (`db.py`): zero logging. Transactions silently succeed or rollback on exception. No audit trail of writes beyond the KB's own append-only versioning.
- **ChromaDB path** (`db.py` deliberation search): zero logging when falling back from semantic → text match. Users don't see which path ran unless they inspect the returned `search_method` field.

**Phase 4B recommendation:** Consider introducing `logging.getLogger(__name__)` for diagnostic output in:
1. Bridge runtime modules — so operators can see what the poller and worker are doing when run in the background
2. Database commit/rollback paths — so transaction failures leave a diagnostic record even when rollback succeeds
3. ChromaDB fallback path — so users debugging search results can see which backend ran

The existing `_append_log` helper can be replaced with a `logging.getLogger("groundtruth_kb.bridge.poller")` call that writes to the same log file path.

**Phase 4B non-recommendation:** Do NOT convert the 111 `cli.py` `click.echo` calls to `logging`. Click output is the right pattern for CLI user interaction.

## Proposed Phase 4B logging conventions

1. **User-facing output** (CLI result, prompts, error messages the user should read): `click.echo(...)` — keep current pattern, no changes.
2. **Diagnostic output** (what the background service is doing, when it ran, what it saw): `logging.getLogger(__name__).info(...)` / `.debug(...)` / `.error(...)`.
3. **Debug prints** (the 13 JSON payload prints that exist for bridge CLI interop): these are machine-readable protocol output. Leave as `print(json.dumps(...))`, document as a protocol contract.
4. **Stderr errors** (argument validation, unrecoverable failures): `click.echo(..., err=True)` if in a Click command; `print(..., file=sys.stderr)` if not.

## Phase 4B implementation scope estimate

- Add `logging.getLogger(__name__)` to `bridge/poller.py`, `bridge/worker.py`, `bridge/launcher.py`, `bridge/runtime.py`, `bridge/handshake.py`, `db.py`: **6 files**.
- Replace `_append_log` calls with structured logging: **~15 sites** (from the exception audit).
- Add `GROUNDTRUTH_LOG_LEVEL` env var support to `config.py`: **1 new config field**.
- Document the logging convention in `docs/method/`: **1 new section**.
- Tests: verify that logging output is captured and reasonable: **~3 new tests**.

Estimated effort: **1 bridge round** for the refactor + 1 for the conventions doc.

## Non-blocking observation

The `bridge/runtime.py:1455` optional-dependency warning (`"MCP (FastMCP) is not installed. ..."`) uses bare `print()` with no stderr marker and no exit code signalling. A user discovering it will just see the message blended into normal output. Phase 4B should move this to `click.echo(..., err=True)` or the new logging path.

---

*Generated as part of the Phase 4A measurement-only audit baseline.*
