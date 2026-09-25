"""Exercise the ordinary CLI, normal Git hooks and live native authority together."""

from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

from platform_tests.groundtruth_kb.bridge_fixtures import bridge as bridge
from platform_tests.groundtruth_kb.finalization_fixtures import base, git, integration, invoke, real_index
from platform_tests.groundtruth_kb.finalization_fixtures import commit_environment as commit_environment
from platform_tests.groundtruth_kb.native_fixtures import native as native

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]

# The arrival oracle (N-28): the reference callback must reach the stalled authority within this window. Owner decision
# D60 (2026-09-25) widened it from 10 s to 20 s. The callback follows about 56 sequential Git launches, and this host's
# process creation intermittently slows about fourfold, which put two installed runs' arrivals past 10 s. The product's
# five-second callback deadline and every assertion are unchanged. B86 records the observed wait against the window on
# every execution, so a pass also measures its margin.
ARRIVAL_WINDOW_SECONDS = 20


def pending_invocation_report(pending, submitted_at, wait_seconds=15):
    """Describe the pending CLI invocation for an arrival-failure message (N-28 capture); never raises."""
    try:
        result = pending.result(timeout=wait_seconds)
    except TimeoutError:
        return (
            f"the pending CLI invocation was still running {time.monotonic() - submitted_at:.1f}s after submission "
            f"(no result within a further {wait_seconds}s)"
        )
    except Exception as exc:  # the message must describe the invocation, never replace the arrival failure
        return f"the pending CLI invocation raised {exc!r} {time.monotonic() - submitted_at:.1f}s after submission"
    return (
        f"the pending CLI invocation finished {time.monotonic() - submitted_at:.1f}s after submission with "
        f"exit_code={result.exit_code!r} exception={result.exception!r} output={result.output!r}"
    )


@pytest.mark.parametrize("effect", ["refuse", "content", "mode", "foreign", "unstaged-content"])
def test_normal_hooks_refuse_before_head_and_preserve_foreign_index(commit_environment, effect):
    client, root, parent, checkout, hooks, config, message = commit_environment
    foreign = checkout / "foreign_tracked.txt"
    foreign.write_text("Independent staged work\n", encoding="utf-8")
    git(checkout, "add", "--", foreign.name)
    foreign.write_text("Independent unstaged work\n", encoding="utf-8")
    before = real_index(checkout).read_bytes()
    hook_name = "commit-msg" if effect in {"mode", "foreign"} else "pre-commit"
    commands = {
        "refuse": "echo qualification-refusal >&2\nexit 17\n",
        "content": "printf 'unreviewed = 9\\n' > code.py\ngit add -- code.py\n",
        "mode": "git update-index --chmod=+x -- code.py\n",
        "foreign": "git add -- foreign_tracked.txt\n",
        "unstaged-content": "printf 'unreviewed = 9\\n' > code.py\n",
    }
    hook = hooks / hook_name
    hook.write_text("#!/bin/sh\nset -e\n" + commands[effect], encoding="utf-8", newline="\n")
    hook.chmod(0o755)
    result = invoke(config, message)
    assert result.exit_code != 0, result.output
    assert not list(checkout.glob(".gtkb-index-*"))
    assert not list(real_index(checkout).parent.glob("gtkb-commit-*"))
    expected = {
        "refuse": "qualification-refusal",
        "content": "exact reviewed bytes",
        "mode": "hook changed the index",
        "foreign": "hook changed the index",
        "unstaged-content": "context files changed",
    }[effect]
    # A string message survives pytest's repr elision, so a refusal's diagnostic details stay in the evidence.
    assert expected in result.output, f"{result.output}\nexception: {result.exception!r}"
    assert base(checkout) == base(integration(root)) == parent
    assert real_index(checkout).read_bytes() == before
    assert foreign.read_text() == "Independent unstaged work\n"
    assert git(checkout, "show", ":foreign_tracked.txt").stdout == "Independent staged work\n"
    assert client.get("/v1/projects/PROJECT-1").json()["project"]["status"] == "active"
    assert len(client.get("/v1/bridge/queue", params={"role": "lo"}).json()["eligible"]) == 2


@pytest.mark.parametrize("commit_environment", [False, True], indirect=True, ids=["content", "mode-and-content"])
def test_successful_normal_commit_excludes_and_preserves_foreign_staging(
    commit_environment,
):
    client, root, parent, checkout, hooks, config, message = commit_environment
    foreign = checkout / "foreign_tracked.txt"
    foreign.write_text("Independent staged work\n", encoding="utf-8")
    git(checkout, "add", "--", foreign.name)
    foreign.write_text("Independent unstaged work\n", encoding="utf-8")
    for name in ("pre-commit", "commit-msg"):
        hook = hooks / name
        hook.write_text(
            f"#!/bin/sh\nprintf '{name}\\n' >> hook-order.txt\n",
            encoding="utf-8",
            newline="\n",
        )
        hook.chmod(0o755)
    result = invoke(config, message)
    assert result.exit_code == 0, f"{result.output}\nexception: {result.exception!r}"
    assert not list(checkout.glob(".gtkb-index-*"))
    assert not list(real_index(checkout).parent.glob("gtkb-commit-*"))
    assert client.get("/v1/projects/PROJECT-1").json()["project"]["status"] == "verified"
    assert base(checkout) == base(integration(root)) != parent
    assert git(checkout, "show", "--format=", "--name-only", "HEAD").stdout.splitlines() == ["code.py", "second.py"]
    assert git(checkout, "diff", "--cached", "--name-only").stdout.strip() == "foreign_tracked.txt"
    assert git(checkout, "show", ":foreign_tracked.txt").stdout == "Independent staged work\n"
    assert foreign.read_text() == "Independent unstaged work\n"
    assert (checkout / "hook-order.txt").read_text().splitlines() == [
        "pre-commit",
        "commit-msg",
    ]


def test_prepare_preserves_a_foreign_index_value_at_a_reviewed_path(commit_environment):
    _, root, parent, checkout, _, config, message = commit_environment
    working = (checkout / "code.py").read_bytes()
    (checkout / "code.py").write_text("Staged elsewhere; not the reviewed content\n", encoding="utf-8")
    git(checkout, "add", "--", "code.py")
    (checkout / "code.py").write_bytes(working)
    index = real_index(checkout).read_bytes()
    result = invoke(config, message)
    assert result.exit_code != 0 and "checkout_has_local_work" in result.output, result.output
    assert base(checkout) == base(integration(root)) == parent
    assert real_index(checkout).read_bytes() == index
    assert (checkout / "code.py").read_bytes() == working


def test_redirected_hooks_cannot_skip_required_normal_hooks(commit_environment):
    _, root, parent, checkout, hooks, config, message = commit_environment
    redirected = hooks.parent / "unrelated-hooks"
    redirected.mkdir()
    git(checkout, "config", "core.hooksPath", str(redirected))
    index = real_index(checkout).read_bytes()
    result = invoke(config, message)
    assert result.exit_code != 0 and "hooks_redirected" in result.output, result.output
    assert base(checkout) == base(integration(root)) == parent
    assert real_index(checkout).read_bytes() == index


def test_stalled_commit_callback_releases_reference_lock_without_advancing_head(commit_environment, record_property):
    import json
    from concurrent.futures import ThreadPoolExecutor
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    client, root, parent, checkout, hooks, config, message = commit_environment
    foreign = checkout / "foreign_tracked.txt"
    foreign.write_text("foreign staged work\n", encoding="utf-8")
    git(checkout, "add", "--", foreign.name)
    foreign.write_bytes(b"foreign unstaged work\x00")
    index_before = real_index(checkout).read_bytes()
    received = threading.Event()
    release = threading.Event()
    requests = []

    class StalledAuthority(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            requests.append((self.path, body, time.monotonic()))
            received.set()
            release.wait(20)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), StalledAuthority)
    server.daemon_threads = True
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    hook = hooks / "reference-transaction"
    hook.write_text(
        '#!/bin/sh\nif [ -n "$GTKB_PROJECT_COMMIT_PROJECT" ]; then\n'
        f'export GTKB_PROJECT_COMMIT_AUTHORITY="http://127.0.0.1:{server.server_port}"\n'
        'exec "$GTKB_PROJECT_COMMIT_PYTHON" -m groundtruth_kb.project.native_commit "$@"\nfi\nexit 0\n',
        encoding="utf-8",
        newline="\n",
    )
    hook.chmod(0o755)
    branch = git(checkout, "symbolic-ref", "HEAD").stdout.strip()
    lock = Path(git(checkout, "rev-parse", "--path-format=absolute", "--git-path", branch + ".lock").stdout.strip())
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            submitted_at = time.monotonic()
            pending = pool.submit(invoke, config, message)
            try:
                if not received.wait(ARRIVAL_WINDOW_SECONDS):
                    # N-28: an arrival failure alone does not say what the CLI did. Release the never-contacted
                    # authority, give the invocation a bounded chance to finish and carry its outcome in the
                    # failure message. The oracle is arrival within ARRIVAL_WINDOW_SECONDS (D60).
                    release.set()
                    report = pending_invocation_report(pending, submitted_at)
                    late = [round(row[2] - submitted_at, 3) for row in requests]
                    record_property("callback_arrival_window_seconds", ARRIVAL_WINDOW_SECONDS)
                    record_property("callback_arrival_seconds", late[0] if late else None)
                    pytest.fail(
                        f"Reference callback did not contact the stalled authority within {ARRIVAL_WINDOW_SECONDS}s; "
                        + report
                        + (f"; the callback arrived {late[0]}s after submission" if late else "; no callback arrived")
                    )
                record_property("callback_arrival_window_seconds", ARRIVAL_WINDOW_SECONDS)
                record_property("callback_arrival_seconds", round(requests[0][2] - submitted_at, 3))
                assert lock.is_file(), "Git must hold the selected branch lock during its prepared callback"
                assert base(checkout) == parent
                result = pending.result(timeout=10)
                stalled_seconds = time.monotonic() - requests[0][2]
            finally:
                release.set()
        assert result.exit_code != 0 and "configured authority is unavailable" in result.output, result.output
        assert not list(checkout.glob(".gtkb-index-*"))
        assert not list(real_index(checkout).parent.glob("gtkb-commit-*"))
        assert 4 <= stalled_seconds < 10
        assert not lock.exists()
        assert len(requests) == 1
        path, body, _ = requests[0]
        assert path == "/v1/projects/PROJECT-1/check-commit"
        assert body["expected_parent"] == parent and body["native_context_id"] == "lo3"
        assert body["commit_id"] != parent and body["index_tree"]
        assert base(checkout) == base(integration(root)) == parent
        assert real_index(checkout).read_bytes() == index_before
        assert foreign.read_bytes() == b"foreign unstaged work\x00"
        assert git(checkout, "show", ":foreign_tracked.txt").stdout == "foreign staged work\n"
        assert client.get("/v1/projects/PROJECT-1").json()["project"]["status"] == "active"
        record_property("callback_stall_seconds", stalled_seconds)
        record_property("reference_lock_observed_and_released", True)
    finally:
        release.set()
        server.shutdown()
        server.server_close()
        worker.join(5)
        assert not worker.is_alive()


def test_timed_out_real_callback_finishes_before_recovery(commit_environment, monkeypatch, record_property):
    from concurrent.futures import ThreadPoolExecutor

    from groundtruth_kb.postgres_kernel import PostgresKernelError
    from groundtruth_kb.project.native_finalization import NativeProjectFinalization

    client, root, parent, checkout, _hooks, config, message = commit_environment
    foreign = checkout / "foreign_tracked.txt"
    foreign.write_text("foreign staged work\n", encoding="utf-8")
    git(checkout, "add", "--", foreign.name)
    foreign.write_bytes(b"foreign unstaged work\x00")
    index_before = real_index(checkout).read_bytes()
    branch = git(checkout, "symbolic-ref", "HEAD").stdout.strip()
    lock = Path(git(checkout, "rev-parse", "--path-format=absolute", "--git-path", branch + ".lock").stdout.strip())
    entered, release, finished = threading.Event(), threading.Event(), threading.Event()
    captured, results, recovery = {}, [], []
    check = NativeProjectFinalization._check_commit_locked
    project = NativeProjectFinalization._project

    def delayed(self, tx, project_id, request):
        captured.update(
            tx=tx, thread=threading.get_ident(), callback=self._commit_callbacks[project_id], request=request
        )
        entered.set()
        try:
            assert release.wait(20), "test failed to release the real callback"
            result = check(self, tx, project_id, request)
            results.append(result)
            return result
        finally:
            finished.set()

    def observe_recovery(self, tx, project_id, request, **kwargs):
        if tx is captured.get("tx") and threading.get_ident() != captured.get("thread"):
            recovery.append((finished.is_set(), project_id not in self._commit_callbacks))
        return project(self, tx, project_id, request, **kwargs)

    monkeypatch.setattr(NativeProjectFinalization, "_check_commit_locked", delayed)
    monkeypatch.setattr(NativeProjectFinalization, "_project", observe_recovery)
    with ThreadPoolExecutor(max_workers=1) as pool:
        submitted_at = time.monotonic()
        pending = pool.submit(invoke, config, message)
        try:
            arrived = entered.wait(40)
            # B86: the observed wait against this test's own (unchanged) arrival window, on every execution.
            record_property("callback_arrival_window_seconds", 40)
            record_property("callback_arrival_seconds", round(time.monotonic() - submitted_at, 3) if arrived else None)
            assert arrived, "the real commit callback did not arrive"
            assert lock.is_file(), "Git must hold its selected reference lock during the callback"
            deadline = time.monotonic() + 10
            while lock.exists() and time.monotonic() < deadline:
                time.sleep(0.05)
            assert not lock.exists(), "the client deadline did not release Git's reference lock"
            assert not finished.is_set()
            assert not pending.done()
            assert recovery == [], "recovery used the shared transaction before the real callback finished"
        finally:
            release.set()
        result = pending.result(timeout=40)
    assert result.exit_code != 0, result.output
    assert "fresh_verification_required" in result.output and "commit_not_confirmed" in result.output
    assert "timed out" in result.output
    assert len(results) == 1 and results[0]["status"] == "ready_to_update_reference"
    assert recovery and all(after_finish and retired for after_finish, retired in recovery)
    assert base(checkout) == base(integration(root)) == parent
    assert real_index(checkout).read_bytes() == index_before
    assert foreign.read_bytes() == b"foreign unstaged work\x00"
    assert git(checkout, "show", ":foreign_tracked.txt").stdout == "foreign staged work\n"
    assert client.get("/v1/projects/PROJECT-1").json()["project"]["status"] == "active"
    assert len(client.get("/v1/bridge/queue", params={"role": "lo"}).json()["eligible"]) == 2
    access_count = len(recovery)
    with pytest.raises(PostgresKernelError) as error:
        captured["callback"](captured["request"])
    assert error.value.code == "commit_not_in_progress"
    assert len(results) == 1 and len(recovery) == access_count
