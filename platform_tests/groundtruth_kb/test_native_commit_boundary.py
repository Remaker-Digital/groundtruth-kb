"""Exercise the ordinary CLI, normal Git hooks and live native authority together."""

from __future__ import annotations

import socket
import threading
import time
from pathlib import Path

import pytest
import uvicorn
from click.testing import CliRunner
from groundtruth_kb.cli import main

from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_bridge import bridge as bridge
from platform_tests.groundtruth_kb.test_native_project_finalization import (
    base,
    git,
    integration,
    post,
    two_members,
)

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


@pytest.fixture
def commit_environment(bridge, tmp_path, monkeypatch, request):
    git(bridge[3], "config", "core.filemode", "false")
    if getattr(request, "param", False):
        git(bridge[3], "update-index", "--chmod=+x", "--", "code.py")
    client, contexts, root, parent = two_members(bridge)

    def assert_review(where):
        for number in (1, 2):
            current = client.get(f"/v1/bridge/chain-{number}/artifacts").json()
            reviewed = client.get(f"/v1/bridge/chain-{number}/show").json()["attempt"]["verified_artifacts"]
            assert current == reviewed, (where, current, reviewed)

    assert_review("after verification")
    main_root = integration(root)
    hooks = main_root / ".githooks"
    hooks.mkdir()
    reference = hooks / "reference-transaction"
    reference.write_text(
        '#!/bin/sh\nif [ -n "$GTKB_PROJECT_COMMIT_PROJECT" ]; then\n'
        'exec "$GTKB_PROJECT_COMMIT_PYTHON" -m groundtruth_kb.project.native_commit "$@"\nfi\nexit 0\n',
        encoding="utf-8",
        newline="\n",
    )
    reference.chmod(0o755)
    git(main_root, "config", "core.hooksPath", ".githooks")
    prepared = post(client, "prepare-commit").json()
    assert prepared["status"] == "ready_to_commit", prepared
    checkout = Path(prepared["checkout"]["path"])
    assert_review("after preparation")
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(client.app, host="127.0.0.1", port=port, log_level="error"))
        worker = threading.Thread(target=lambda: server.run(sockets=[listener]), daemon=True)
        worker.start()
        deadline = time.monotonic() + 10
        while not server.started and worker.is_alive() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert server.started
        config = tmp_path / "commit-client.toml"
        config.write_text(
            f'[groundtruth]\nauthority_url="http://127.0.0.1:{port}"\n',
            encoding="utf-8",
        )
        message = tmp_path / "commit-message.txt"
        message.write_text(
            "Complete the independently reviewed product (WI-1) (WI-2)\n",
            encoding="utf-8",
        )
        assert_review("after server startup")
        monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
        try:
            for number in (1, 2):
                current = client.get(f"/v1/bridge/chain-{number}/artifacts").json()
                reviewed = client.get(f"/v1/bridge/chain-{number}/show").json()["attempt"]["verified_artifacts"]
                assert current == reviewed, (current, reviewed)
            yield client, root, parent, checkout, hooks, config, message
        finally:
            server.should_exit = True
            worker.join(10)
            assert not worker.is_alive()


def invoke(config, message):
    return CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "projects",
            "commit",
            "PROJECT-1",
            "--native-context-id",
            "lo3",
            "--expected-version",
            "1",
            "--message-file",
            str(message),
            "--json",
        ],
    )


def real_index(root):
    return Path(git(root, "rev-parse", "--path-format=absolute", "--git-path", "index").stdout.strip())


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
                if not received.wait(10):
                    # N-28: an arrival failure alone does not say what the CLI did. Release the never-contacted
                    # authority, give the invocation a bounded chance to finish and carry its outcome in the
                    # failure message. The oracle (arrival within 10 s) is unchanged.
                    release.set()
                    pytest.fail(
                        "Reference callback did not contact the stalled authority within 10s; "
                        + pending_invocation_report(pending, submitted_at)
                    )
                assert lock.is_file(), "Git must hold the selected branch lock during its prepared callback"
                assert base(checkout) == parent
                result = pending.result(timeout=10)
                stalled_seconds = time.monotonic() - requests[0][2]
            finally:
                release.set()
        assert result.exit_code != 0 and "configured authority is unavailable" in result.output, result.output
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
