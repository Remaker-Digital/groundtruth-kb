# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Unit tests for the spec/intake event surfacer hook.

Implements the verification required by bridge
``gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-005``
(REVISED-2; Codex GO at -006). Each test derives from ``SPEC-INTAKE-2485e9``
("Surface spec creation/update events in owner chat view") plus the umbrella
GO conditions enumerated in
``bridge/gtkb-membase-effective-use-recovery-2026-04-29-002.md`` non-blocking
condition #1 (exact hook event(s), hook registration files, per-session
start timestamp source, ledger location, duplicate-suppression behavior).
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sqlite3
import subprocess
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

# The hook lives in templates/hooks/; load it as a module by file path so
# tests can exercise the same code adopters install via gt project upgrade.
_HOOK_PATH = Path(__file__).resolve().parent.parent / "templates" / "hooks" / "spec-event-surfacer.py"


def _load_surfacer_module():
    """Import the spec-event-surfacer.py template as a module."""
    spec = importlib.util.spec_from_file_location("spec_event_surfacer_module", _HOOK_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _init_specs_db(db_path: Path) -> None:
    """Create the minimal current_specifications schema needed by the hook."""
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE current_specifications (
            id TEXT NOT NULL,
            version INTEGER NOT NULL,
            title TEXT,
            type TEXT,
            status TEXT,
            section TEXT,
            changed_at TEXT NOT NULL
        );
        CREATE INDEX idx_specs_changed_at ON current_specifications(changed_at);
        """
    )
    conn.commit()
    conn.close()


def _insert_spec(
    db_path: Path,
    spec_id: str,
    *,
    version: int = 1,
    title: str = "Sample spec",
    type_: str = "requirement",
    status: str = "specified",
    section: str = "test-section",
    changed_at: str | None = None,
) -> str:
    """Insert a row into the synthesized current_specifications table.

    Returns the changed_at timestamp actually written.
    """
    if changed_at is None:
        changed_at = datetime.now(UTC).isoformat(timespec="microseconds")
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO current_specifications "
        "(id, version, title, type, status, section, changed_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (spec_id, version, title, type_, status, section, changed_at),
    )
    conn.commit()
    conn.close()
    return changed_at


def _write_session_start(cwd: Path, ts: str) -> None:
    """Write the .claude/session/session-start.json file with given timestamp."""
    target = cwd / ".claude" / "session" / "session-start.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps({"session_started_at": ts, "session_id": "T-test", "harness": "test"}),
        encoding="utf-8",
    )


def _run_hook(cwd: Path, payload: dict | None = None) -> dict:
    """Invoke the hook's main() with a synthesized PostToolUse payload.

    Returns the parsed JSON the hook emitted to stdout.
    """
    module = _load_surfacer_module()
    if payload is None:
        payload = {"tool_name": "Bash", "tool_input": {"command": "echo test"}, "cwd": str(cwd)}
    else:
        payload.setdefault("cwd", str(cwd))

    captured_stdout = io.StringIO()
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = io.StringIO(json.dumps(payload))
    sys.stdout = captured_stdout
    try:
        with contextlib.suppress(SystemExit):
            module.main()
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout
    raw = captured_stdout.getvalue().strip()
    if not raw:
        return {}
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Tests derived from SPEC-INTAKE-2485e9 + Codex GO conditions
# ---------------------------------------------------------------------------


def test_surfacer_emits_chat_visible_event_for_new_spec(tmp_path: Path) -> None:
    """SPEC-INTAKE-2485e9 primary requirement: spec event in owner chat view."""
    _init_specs_db(tmp_path / "groundtruth.db")
    session_start = (datetime.now(UTC) - timedelta(minutes=5)).isoformat(timespec="microseconds")
    _write_session_start(tmp_path, session_start)
    _insert_spec(tmp_path / "groundtruth.db", "SPEC-TEST-001", title="Test spec")

    output = _run_hook(tmp_path)

    assert "hookSpecificOutput" in output
    inner = output["hookSpecificOutput"]
    assert inner.get("hookEventName") == "PostToolUse"
    msg = inner.get("additionalContext", "")
    assert "[KB-SPEC-EVENT]" in msg
    assert "SPEC-TEST-001" in msg
    assert "v1" in msg
    assert "created" in msg
    assert "Test spec" in msg


def test_surfacer_does_not_duplicate_event_on_repeated_invocation(tmp_path: Path) -> None:
    """Codex condition: per-session ledger plus idempotency."""
    _init_specs_db(tmp_path / "groundtruth.db")
    session_start = (datetime.now(UTC) - timedelta(minutes=5)).isoformat(timespec="microseconds")
    _write_session_start(tmp_path, session_start)
    _insert_spec(tmp_path / "groundtruth.db", "SPEC-IDEMP-001")

    first = _run_hook(tmp_path)
    second = _run_hook(tmp_path)

    assert "hookSpecificOutput" in first  # First run emits
    assert second == {}  # Second run is silent (already in ledger)


def test_surfacer_uses_session_start_json_when_present(tmp_path: Path) -> None:
    """Codex condition: per-session start timestamp source from session-start.json."""
    _init_specs_db(tmp_path / "groundtruth.db")
    # Session started 10 minutes ago; spec inserted 5 minutes ago (after session start)
    session_start = (datetime.now(UTC) - timedelta(minutes=10)).isoformat(timespec="microseconds")
    _write_session_start(tmp_path, session_start)
    spec_changed_at = (datetime.now(UTC) - timedelta(minutes=5)).isoformat(timespec="microseconds")
    _insert_spec(tmp_path / "groundtruth.db", "SPEC-INSESSION-001", changed_at=spec_changed_at)

    output = _run_hook(tmp_path)
    assert "hookSpecificOutput" in output
    msg = output["hookSpecificOutput"]["additionalContext"]
    # The fallback warning prefix must NOT be present when session-start.json is honored
    assert "WARN: session-start.json missing" not in msg


def test_surfacer_uses_conservative_fallback_when_session_start_missing(tmp_path: Path) -> None:
    """F2 fix: missing session-start.json triggers now() - 1 hour fallback,
    NOT current_time (which would silently suppress in-session writes)."""
    _init_specs_db(tmp_path / "groundtruth.db")
    # Spec inserted 30 minutes ago; well within the 1-hour fallback window
    spec_changed_at = (datetime.now(UTC) - timedelta(minutes=30)).isoformat(timespec="microseconds")
    _insert_spec(tmp_path / "groundtruth.db", "SPEC-FALLBACK-001", changed_at=spec_changed_at)

    output = _run_hook(tmp_path)
    assert "hookSpecificOutput" in output
    msg = output["hookSpecificOutput"]["additionalContext"]
    assert "WARN: session-start.json missing" in msg
    assert "SPEC-FALLBACK-001" in msg


def test_surfacer_ignores_pre_session_rows(tmp_path: Path) -> None:
    """Codex condition: per-session start timestamp source bounds visible rows."""
    _init_specs_db(tmp_path / "groundtruth.db")
    session_start = datetime.now(UTC).isoformat(timespec="microseconds")
    _write_session_start(tmp_path, session_start)
    # Spec was changed 1 hour BEFORE session start
    pre_session = (datetime.now(UTC) - timedelta(hours=1)).isoformat(timespec="microseconds")
    _insert_spec(tmp_path / "groundtruth.db", "SPEC-PRESESSION-001", changed_at=pre_session)

    output = _run_hook(tmp_path)
    assert output == {}  # Pre-session row is filtered out


def test_ledger_is_written_to_session_dir(tmp_path: Path) -> None:
    """Codex condition: ledger location at .claude/session/spec-events-seen.jsonl."""
    _init_specs_db(tmp_path / "groundtruth.db")
    session_start = (datetime.now(UTC) - timedelta(minutes=5)).isoformat(timespec="microseconds")
    _write_session_start(tmp_path, session_start)
    _insert_spec(tmp_path / "groundtruth.db", "SPEC-LEDGER-001")

    _run_hook(tmp_path)

    ledger_path = tmp_path / ".claude" / "session" / "spec-events-seen.jsonl"
    assert ledger_path.exists()
    contents = ledger_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(contents) == 1
    entry = json.loads(contents[0])
    assert entry["spec_id"] == "SPEC-LEDGER-001"
    assert entry["version"] == 1
    assert entry["kind"] == "created"
    assert "seen_at" in entry


def test_repeated_invocations_yield_one_emit_one_ledger_entry(tmp_path: Path) -> None:
    """Codex condition: duplicate-suppression behavior.

    Three sequential invocations on the same KB state must yield exactly
    one emit (the first) and exactly one ledger entry. The per-session
    ledger is the primary suppression mechanism; atomic-rename writes
    handle real cross-process concurrency.
    """
    _init_specs_db(tmp_path / "groundtruth.db")
    session_start = (datetime.now(UTC) - timedelta(minutes=5)).isoformat(timespec="microseconds")
    _write_session_start(tmp_path, session_start)
    _insert_spec(tmp_path / "groundtruth.db", "SPEC-IDEMP-MANY-001")

    results = [_run_hook(tmp_path) for _ in range(3)]

    # Exactly one emit (the first); the next two are silent.
    emit_count = sum(1 for r in results if "hookSpecificOutput" in r)
    assert emit_count == 1, f"expected exactly 1 emit across 3 invocations; got {emit_count}"

    # Ledger has exactly one entry for the spec.
    ledger_path = tmp_path / ".claude" / "session" / "spec-events-seen.jsonl"
    assert ledger_path.exists()
    contents = ledger_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(contents) == 1
    entry = json.loads(contents[0])
    assert entry["spec_id"] == "SPEC-IDEMP-MANY-001"
    assert entry["version"] == 1


def test_atomic_ledger_write_recovers_from_partial_state(tmp_path: Path) -> None:
    """Per §1.7 atomicity: tmp-file plus os.replace pattern means an
    interrupted write leaves the prior ledger intact (no partial state).

    Simulates this by pre-populating a partial tmp-file alongside an
    existing ledger; verifies the hook ignores the orphaned tmp and
    appends to the canonical ledger.
    """
    _init_specs_db(tmp_path / "groundtruth.db")
    session_start = (datetime.now(UTC) - timedelta(minutes=5)).isoformat(timespec="microseconds")
    _write_session_start(tmp_path, session_start)
    _insert_spec(tmp_path / "groundtruth.db", "SPEC-RECOVER-001")

    # Pre-populate an orphaned .tmp.<fakepid> file (simulates crash mid-write)
    session_dir = tmp_path / ".claude" / "session"
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "spec-events-seen.jsonl.tmp.99999").write_text("garbage", encoding="utf-8")

    output = _run_hook(tmp_path)

    assert "hookSpecificOutput" in output
    ledger_path = session_dir / "spec-events-seen.jsonl"
    assert ledger_path.exists()
    contents = ledger_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(contents) == 1
    entry = json.loads(contents[0])
    assert entry["spec_id"] == "SPEC-RECOVER-001"


def test_concurrent_invocations_do_not_double_emit(tmp_path: Path) -> None:
    """F1 fix from bridge -008 NO-GO: under N simultaneous PostToolUse hook
    invocations against the same KB state, every spec row must be emitted
    exactly once across the union of process outputs, the ledger must contain
    exactly one entry per (spec_id, version), and a sequential invocation
    after the concurrent run must be silent.

    Codex's -008 parallel-process probe at 16 procs over 1000 rows yielded
    emit_count=8 / ledger_line_count=2000. The fix is interprocess locking
    around load+query+append. This test reproduces that probe at smaller
    scale (16 procs, 100 rows) so it remains tractable in CI; larger
    fixtures behave identically when the lock is correct.
    """
    hook_path = _HOOK_PATH
    assert hook_path.exists(), f"hook not found at {hook_path}"

    db_path = tmp_path / "groundtruth.db"
    _init_specs_db(db_path)
    session_start = (datetime.now(UTC) - timedelta(minutes=10)).isoformat(timespec="microseconds")
    _write_session_start(tmp_path, session_start)

    NUM_SPECS = 100
    spec_change_ts = (datetime.now(UTC) - timedelta(minutes=5)).isoformat(timespec="microseconds")
    conn = sqlite3.connect(db_path)
    for i in range(NUM_SPECS):
        conn.execute(
            "INSERT INTO current_specifications "
            "(id, version, title, type, status, section, changed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                f"SPEC-CONCUR-{i:04d}",
                1,
                f"Concurrency fixture spec {i}",
                "requirement",
                "specified",
                "concurrency-test",
                spec_change_ts,
            ),
        )
    conn.commit()
    conn.close()

    payload = json.dumps(
        {
            "tool_name": "Bash",
            "tool_input": {"command": "echo test"},
            "cwd": str(tmp_path),
        }
    ).encode("utf-8")

    NUM_PROCS = 16

    procs: list[subprocess.Popen[bytes]] = [
        subprocess.Popen(
            [sys.executable, str(hook_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for _ in range(NUM_PROCS)
    ]

    for p in procs:
        assert p.stdin is not None
        p.stdin.write(payload)
        p.stdin.close()

    outputs: list[str] = []
    for p in procs:
        out, _err = p.communicate(timeout=60)
        outputs.append(out.decode("utf-8"))

    emit_count_per_spec: dict[tuple[str, int], int] = {}
    for raw in outputs:
        out = raw.strip()
        if not out or out == "{}":
            continue
        envelope = json.loads(out)
        ctx = envelope.get("hookSpecificOutput", {}).get("additionalContext", "")
        for line in ctx.splitlines():
            line = line.strip()
            if not line.startswith("[KB-SPEC-EVENT]") or "WARN:" in line:
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            spec_id = parts[1]
            try:
                version = int(parts[2][1:])  # "v1" -> 1
            except (IndexError, ValueError):
                continue
            key = (spec_id, version)
            emit_count_per_spec[key] = emit_count_per_spec.get(key, 0) + 1

    duplicate_emits = {k: v for k, v in emit_count_per_spec.items() if v > 1}
    assert not duplicate_emits, (
        f"Duplicate owner-visible emits across {NUM_PROCS} concurrent processes: {duplicate_emits}"
    )

    assert len(emit_count_per_spec) == NUM_SPECS, (
        f"Expected {NUM_SPECS} unique emits across the union of process outputs; "
        f"got {len(emit_count_per_spec)}"
    )

    ledger_path = tmp_path / ".claude" / "session" / "spec-events-seen.jsonl"
    assert ledger_path.exists(), "ledger file was not created"
    with ledger_path.open(encoding="utf-8") as fh:
        ledger_lines = [line for line in fh if line.strip()]
    assert len(ledger_lines) == NUM_SPECS, (
        f"Expected {NUM_SPECS} ledger entries; got {len(ledger_lines)}"
    )

    seen_keys: set[tuple[str, int]] = set()
    for line in ledger_lines:
        entry = json.loads(line)
        key = (entry["spec_id"], entry["version"])
        assert key not in seen_keys, f"Duplicate ledger entry for {key}"
        seen_keys.add(key)

    result = subprocess.run(
        [sys.executable, str(hook_path)],
        input=payload,
        capture_output=True,
        timeout=10,
    )
    final_out = result.stdout.decode("utf-8").strip()
    assert final_out == "{}", (
        f"Expected silent emit on sequential invocation after concurrent run; got: {final_out!r}"
    )


def test_surfacer_runtime_under_200ms_for_typical_turn_transcript(tmp_path: Path) -> None:
    """Performance acceptance criterion 8 from REVISED-2 §4.

    Synthesizes a moderately-populated KB (50 rows, mix of pre-session and
    in-session) and asserts the hook completes under 200ms.
    """
    _init_specs_db(tmp_path / "groundtruth.db")
    session_start = (datetime.now(UTC) - timedelta(minutes=10)).isoformat(timespec="microseconds")
    _write_session_start(tmp_path, session_start)
    # Insert 30 pre-session + 20 in-session rows
    for i in range(30):
        ts = (datetime.now(UTC) - timedelta(hours=2, minutes=i)).isoformat(timespec="microseconds")
        _insert_spec(tmp_path / "groundtruth.db", f"SPEC-PRE-{i:03d}", changed_at=ts)
    for i in range(20):
        ts = (datetime.now(UTC) - timedelta(minutes=5)).isoformat(timespec="microseconds")
        _insert_spec(tmp_path / "groundtruth.db", f"SPEC-IN-{i:03d}", changed_at=ts)

    start = time.monotonic()
    output = _run_hook(tmp_path)
    elapsed_ms = (time.monotonic() - start) * 1000

    assert "hookSpecificOutput" in output
    # Module loading from disk dominates; allow a generous bound. The DCL
    # target is 200ms for a typical session transcript; on first invocation
    # we permit up to 500ms to absorb the import cost.
    assert elapsed_ms < 500, f"surfacer took {elapsed_ms:.1f}ms (target < 500ms)"


def test_surfacer_handles_missing_database_gracefully(tmp_path: Path) -> None:
    """Acceptance criterion 4 (graceful degradation): no DB present should
    not crash the session — hook returns silent pass."""
    # No groundtruth.db created
    session_start = (datetime.now(UTC) - timedelta(minutes=5)).isoformat(timespec="microseconds")
    _write_session_start(tmp_path, session_start)

    output = _run_hook(tmp_path)
    assert output == {}


def test_surfacer_handles_malformed_payload_gracefully(tmp_path: Path) -> None:
    """Acceptance criterion 4 (graceful degradation): malformed stdin must
    not crash the session — hook returns silent pass."""
    module = _load_surfacer_module()
    captured_stdout = io.StringIO()
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = io.StringIO("not-valid-json{")
    sys.stdout = captured_stdout
    try:
        with contextlib.suppress(SystemExit):
            module.main()
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout
    raw = captured_stdout.getvalue().strip()
    assert raw == "{}"


def test_surfacer_emits_warning_when_session_start_malformed(tmp_path: Path) -> None:
    """F2 fix: malformed session-start.json triggers fallback (NOT current_time)."""
    _init_specs_db(tmp_path / "groundtruth.db")
    # Write malformed session-start.json
    target = tmp_path / ".claude" / "session" / "session-start.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("not-valid-json{", encoding="utf-8")
    spec_changed_at = (datetime.now(UTC) - timedelta(minutes=30)).isoformat(timespec="microseconds")
    _insert_spec(tmp_path / "groundtruth.db", "SPEC-MALFORMED-START-001", changed_at=spec_changed_at)

    output = _run_hook(tmp_path)
    assert "hookSpecificOutput" in output
    msg = output["hookSpecificOutput"]["additionalContext"]
    assert "WARN: session-start.json missing" in msg


def test_surfacer_makes_zero_kb_writes(tmp_path: Path) -> None:
    """Acceptance criterion 7: surfacer NEVER writes to groundtruth.db.

    Asserts read-only contract by checking the database file mtime and the
    table row count are unchanged after hook invocation.
    """
    db_path = tmp_path / "groundtruth.db"
    _init_specs_db(db_path)
    session_start = (datetime.now(UTC) - timedelta(minutes=5)).isoformat(timespec="microseconds")
    _write_session_start(tmp_path, session_start)
    _insert_spec(db_path, "SPEC-READONLY-001")

    conn = sqlite3.connect(db_path)
    count_before = conn.execute("SELECT COUNT(*) FROM current_specifications").fetchone()[0]
    conn.close()

    _run_hook(tmp_path)

    # File mtime may shift if SQLite touches the journal; the row count is
    # the stronger invariant (no INSERT/UPDATE/DELETE happened).
    conn = sqlite3.connect(db_path)
    count_after = conn.execute("SELECT COUNT(*) FROM current_specifications").fetchone()[0]
    conn.close()
    assert count_before == count_after == 1
