"""Real authority-process loss after Git commit, before canonical confirmation."""

import json
import os
import shlex
import socket
import subprocess
import sys
import time

import pytest
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError

from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_authority_service import put
from platform_tests.groundtruth_kb.test_native_bridge import bridge as bridge
from platform_tests.groundtruth_kb.test_native_commit_boundary import (
    commit_environment as commit_environment,
)
from platform_tests.groundtruth_kb.test_native_commit_boundary import (
    invoke,
    real_index,
)
from platform_tests.groundtruth_kb.test_native_project_finalization import base, git, integration, post

pytestmark = [pytest.mark.integration, pytest.mark.timeout(150)]


def kill_child_tree(process):
    if process.poll() is not None:
        return
    if os.name == "nt":
        stopped = subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            capture_output=True,
            timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    else:
        import signal

        os.killpg(process.pid, signal.SIGKILL)
    # A short-lived shell child may exit during taskkill's tree enumeration;
    # its exit code then reports that race even though the target was killed.
    # Assert the captured authority process really terminated, not the utility's
    # success text. A surviving authority is a failed interruption test.
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        pytest.fail("Owned child survived termination: " + repr(stopped if os.name == "nt" else process.pid))


def test_killed_authority_after_git_commit_recovers_once_in_a_fresh_context(commit_environment, tmp_path):
    client, root, parent, checkout, hooks, _, message = commit_environment
    main = integration(root)
    foreign = checkout / "foreign_tracked.txt"
    foreign.write_text("Independent staged bytes\n", encoding="utf-8")
    git(checkout, "add", "--", foreign.name)
    foreign.write_text("Independent unstaged bytes\n", encoding="utf-8")
    index_before = real_index(checkout).read_bytes()
    marker = tmp_path / "after-commit"
    release = tmp_path / "release-post-commit"
    hook = hooks / "post-commit"
    hook.write_text(
        "#!/bin/sh\nprintf ready > " + shlex.quote(marker.as_posix()) + "\n"
        "while [ ! -f " + shlex.quote(release.as_posix()) + " ]; do sleep 0.05; done\n",
        encoding="utf-8",
        newline="\n",
    )
    hook.chmod(0o755)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    server_config = tmp_path / "recovery-server.toml"
    server_config.write_text(
        "[groundtruth]\nproject_root="
        + json.dumps(main.as_posix())
        + "\n[postgresql]\nservice="
        + json.dumps(os.environ["GTKB_TEST_POSTGRES_SERVICE"])
        + "\n",
        encoding="utf-8",
    )
    client_config = tmp_path / "recovery-client.toml"
    client_config.write_text("[groundtruth]\nauthority_url=" + json.dumps(url) + "\n", encoding="utf-8")
    env = dict(os.environ)
    env.pop("GT_AUTHORITY_URL", None)
    env.pop("GT_PROJECT_ROOT", None)
    client_env = {k: v for k, v in env.items() if not k.startswith(("PG", "GT_POSTGRES_"))}
    flags = {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0)}
    if os.name != "nt":
        flags["start_new_session"] = True
    client_args = [sys.executable, "-m", "groundtruth_kb", "--config", str(client_config)]

    def cli(*args):
        result = subprocess.run(
            [*client_args, *args],
            cwd=main,
            env=client_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=45,
            **flags,
        )
        assert result.returncode == 0, (result.stdout, result.stderr)
        return json.loads(result.stdout)

    def start(stream):
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "groundtruth_kb",
                "--config",
                str(server_config),
                "service",
                "serve",
                "--port",
                str(port),
            ],
            cwd=main,
            env=env,
            stdout=stream,
            stderr=stream,
            **flags,
        )
        deadline = time.monotonic() + 20
        while process.poll() is None and time.monotonic() < deadline:
            try:
                AuthorityClient(url, timeout=1).request("GET", "/v1/status")
                return process
            except AuthorityClientError:
                time.sleep(0.05)
        kill_child_tree(process)
        pytest.fail("Disposable authority did not start")

    service = worker = None
    with (tmp_path / "recovery-service.log").open("wb") as log:
        try:
            service = start(log)
            worker = subprocess.Popen(
                [
                    *client_args,
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
                cwd=main,
                env=client_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                **flags,
            )
            deadline = time.monotonic() + 40
            while not marker.exists() and worker.poll() is None and time.monotonic() < deadline:
                time.sleep(0.05)
            assert marker.exists(), worker.communicate(timeout=5)
            candidate = base(checkout)
            assert candidate != parent and base(main) == parent
            kill_child_tree(service)
            assert service.returncode != 0
            worker.communicate(timeout=15)
            assert worker.returncode != 0
            assert client.get("/v1/projects/PROJECT-1").json()["project"]["status"] == "active"
            assert real_index(checkout).read_bytes() == index_before
            service = start(log)
            bound = cli(
                "session", "bind", "--native-context-id", "fresh-recovery", "--init-keyword", "::init gtkb lo", "--json"
            )
            fresh_path = main / ".worktrees" / bound["session_context_id"]
            assert not fresh_path.exists()
            arguments = ["PROJECT-1", "--native-context-id", "fresh-recovery", "--expected-version", "1"]
            prepared = cli("projects", "prepare-commit", *arguments, "--json")
            assert prepared["status"] == "ready_to_confirm", prepared
            assert prepared["commit_id"] == candidate
            result = cli("projects", "commit", *arguments, "--message-file", str(message), "--json")
            assert result["status"] == "confirmed" and result["commit_id"] == candidate
            repeated = cli("projects", "commit", *arguments, "--message-file", str(message), "--json")
            assert repeated["status"] == "already_confirmed" and repeated["commit_id"] == candidate
            assert base(main) == candidate
            assert git(main, "rev-list", "--count", parent + "..HEAD").stdout.strip() == "1"
            assert not fresh_path.exists()
            assert real_index(checkout).read_bytes() == index_before
            assert foreign.read_text() == "Independent unstaged bytes\n"
            assert git(checkout, "show", ":foreign_tracked.txt").stdout == "Independent staged bytes\n"
            for number in (1, 2):
                state = client.get(f"/v1/bridge/chain-{number}/show").json()["attempt"]
                assert state["disposition"] == "committed" and state["terminal_commit"] == candidate
        finally:
            release.touch()
            if service is not None:
                kill_child_tree(service)
            if worker is not None and worker.poll() is None:
                kill_child_tree(worker)


def test_index_housekeeping_failure_keeps_the_completed_git_fact(commit_environment):
    client, root, parent, checkout, hooks, config, message = commit_environment
    index_before = real_index(checkout).read_bytes()
    foreign_lock = real_index(checkout).with_name("index.lock")
    hook = hooks / "post-commit"
    hook.write_text(
        "#!/bin/sh\nprintf 'foreign lock' > " + shlex.quote(foreign_lock.as_posix()) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    hook.chmod(0o755)
    try:
        result = invoke(config, message)
        assert result.exit_code == 0, result.output
        body = json.loads(result.output)
        assert body["status"] == "confirmed" and "index_busy_after_commit" in body["checkout_notice"]
        assert base(integration(root)) == base(checkout) != parent
        assert real_index(checkout).read_bytes() == index_before
        assert foreign_lock.read_text() == "foreign lock"
        assert client.get("/v1/projects/PROJECT-1").json()["project"]["status"] == "verified"
    finally:
        foreign_lock.unlink(missing_ok=True)


def test_ambiguous_reviewed_git_candidates_refuse_without_changing_any_checkout(commit_environment):
    _, root, parent, checkout, _, _, _ = commit_environment
    # Both objects match reviewed bytes but are distinct possible Git facts.
    git(checkout, "add", "--", "code.py", "second.py")
    tree = git(checkout, "write-tree").stdout.strip()
    ids = []
    for number in (1, 2):
        candidate = git(
            checkout, "commit-tree", tree, "-p", parent, "-m", f"Candidate {number} (WI-1) (WI-2)"
        ).stdout.strip()
        git(checkout, "update-ref", f"refs/heads/session/recovery-{number}", candidate)
        ids.append(candidate)
    client = commit_environment[0]
    result = post(client, "prepare-commit")
    assert result.status_code == 422 and result.json()["error"]["code"] == "ambiguous_project_commit", result.text
    assert base(checkout) == base(integration(root)) == parent
    assert len(set(ids)) == 2


def test_changed_formal_intent_cannot_abandon_an_unconfirmed_reviewed_git_commit(commit_environment):
    client, root, parent, checkout, _, _, _ = commit_environment
    git(checkout, "add", "--", "code.py", "second.py")
    git(checkout, "commit", "-m", "Complete reviewed work (WI-1) (WI-2)")
    candidate = base(checkout)
    changed = put(client, "specifications", "SPEC-1", {"description": "New material intent"}, expected_version=1)
    assert changed.status_code == 200, changed.text
    for number in (1, 2):
        response = client.post(
            f"/v1/bridge/chain-{number}/abandon",
            json={
                "native_context_id": "lo3",
                "expected_version": 4,
                "reason": "Formal intent materially changed after verification",
            },
        )
        assert response.status_code == 422 and response.json()["error"]["code"] == "git_reconciliation_required", (
            response.text
        )
        state = client.get(f"/v1/bridge/chain-{number}/show").json()["attempt"]
        assert state["disposition"] == "active" and state["head_status"] == "VERIFIED"
    assert base(checkout) == candidate and base(integration(root)) == parent
