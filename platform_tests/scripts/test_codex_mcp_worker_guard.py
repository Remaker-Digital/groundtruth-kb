from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from scripts import codex_mcp_worker_guard as guard

NOW = datetime(2026, 6, 23, 20, 0, tzinfo=UTC)


def _record(
    pid: int,
    ppid: int | None,
    command_line: str,
    *,
    name: str = "node.exe",
    age_seconds: int = 900,
) -> guard.ProcessRecord:
    return guard.ProcessRecord(
        pid=pid,
        ppid=ppid,
        name=name,
        command_line=command_line,
        created_at=NOW - timedelta(seconds=age_seconds),
    )


def test_classifier_detects_detached_known_playwright_and_context7_workers() -> None:
    records = [
        _record(101, 9001, r"C:\nodejs\node.exe npx -y @playwright/mcp"),
        _record(102, 9002, r"C:\nodejs\node.exe npx -y @upstash/context7-mcp"),
    ]

    report = guard.classify_processes(records, now=NOW, min_age_seconds=300)

    assert report["known_mcp_worker_count"] == 2
    assert {worker["family"] for worker in report["stale_workers"]} == {"playwright", "context7"}
    assert {worker["reason"] for worker in report["stale_workers"]} == {"parent_process_not_running"}
    assert report["suspect_workers"] == []
    assert report["live_workers"] == []


def test_classifier_excludes_live_mcp_workers_with_codex_parent_chain() -> None:
    records = [
        guard.ProcessRecord(
            pid=10,
            ppid=1,
            name="Codex.exe",
            command_line=r"C:\Users\example\AppData\Local\Programs\Codex\Codex.exe",
            created_at=NOW - timedelta(minutes=20),
        ),
        guard.ProcessRecord(
            pid=11,
            ppid=10,
            name="cmd.exe",
            command_line="cmd /d /s /c launch mcp",
            created_at=NOW - timedelta(minutes=19),
        ),
        _record(103, 11, r"C:\nodejs\node.exe npx -y @playwright/mcp", age_seconds=800),
    ]

    report = guard.classify_processes(records, now=NOW, min_age_seconds=300)

    assert report["stale_workers"] == []
    assert report["suspect_workers"] == []
    assert len(report["live_workers"]) == 1
    assert report["live_workers"][0]["reason"] == "codex_parent_chain_running"


def test_classifier_excludes_unrelated_node_processes() -> None:
    records = [
        _record(201, 9001, r"C:\nodejs\node.exe server.js"),
        _record(202, 9002, r"C:\nodejs\node.exe webpack --watch"),
    ]

    report = guard.classify_processes(records, now=NOW, min_age_seconds=300)

    assert report["known_mcp_worker_count"] == 0
    assert report["unrelated_node_count"] == 2
    assert report["stale_workers"] == []


def test_classifier_treats_known_worker_with_running_parent_as_attached() -> None:
    records = [
        guard.ProcessRecord(
            pid=20,
            ppid=1,
            name="npx.cmd",
            command_line="npx -y @upstash/context7-mcp",
            created_at=NOW - timedelta(minutes=20),
        ),
        _record(203, 20, r"C:\nodejs\node.exe npx -y @upstash/context7-mcp"),
    ]

    report = guard.classify_processes(records, now=NOW, min_age_seconds=300)

    assert report["stale_workers"] == []
    assert report["suspect_workers"] == []
    assert len(report["live_workers"]) == 1
    assert report["live_workers"][0]["state"] == "attached"
    assert report["live_workers"][0]["reason"] == "parent_process_running"


def test_cleanup_dry_run_never_invokes_terminator() -> None:
    report = guard.classify_processes(
        [_record(301, 9001, r"C:\nodejs\node.exe npx -y @playwright/mcp")],
        now=NOW,
        min_age_seconds=300,
    )
    calls: list[int] = []

    cleanup = guard.cleanup_stale_workers(report, dry_run=True, terminator=lambda pid: calls.append(pid) or (True, ""))

    assert calls == []
    assert cleanup["dry_run"] is True
    assert [worker["pid"] for worker in cleanup["planned"]] == [301]
    assert cleanup["terminated"] == []


def test_cleanup_yes_targets_only_stale_workers() -> None:
    records = [
        _record(401, 9001, r"C:\nodejs\node.exe npx -y @playwright/mcp"),
        _record(402, 9002, r"C:\nodejs\node.exe npx -y @playwright/mcp", age_seconds=20),
    ]
    report = guard.classify_processes(records, now=NOW, min_age_seconds=300)
    calls: list[int] = []

    cleanup = guard.cleanup_stale_workers(
        report,
        dry_run=False,
        terminator=lambda pid: calls.append(pid) or (True, "terminated"),
    )

    assert calls == [401]
    assert [row["pid"] for row in cleanup["terminated"]] == [401]
    assert [row["pid"] for row in cleanup["planned"]] == [401]
    assert [row["pid"] for row in report["suspect_workers"]] == [402]


def test_cleanup_mode_requires_explicit_dry_run_or_yes() -> None:
    with pytest.raises(SystemExit) as exc:
        guard.run(["--cleanup"], collector=list)

    assert exc.value.code == 2
