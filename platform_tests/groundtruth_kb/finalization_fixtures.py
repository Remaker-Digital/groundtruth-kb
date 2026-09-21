"""Shared helpers of the project finalization and commit qualification (c102, Q-3, owner ruling D23).

Moved verbatim from ``test_native_project_finalization.py`` (``git``, ``base``, ``integration``,
``verify``, ``post``, ``two_members``, ``commit_product``) and ``test_native_commit_boundary.py``
(the ``commit_environment`` fixture, ``invoke``, ``real_index``) so that no test module imports
another test module. Not collected; defines no test.
"""

from __future__ import annotations

import json
import socket
import subprocess
import threading
import time
from pathlib import Path

import pytest
import uvicorn
from click.testing import CliRunner
from groundtruth_kb.cli import main

from platform_tests.groundtruth_kb.bridge_fixtures import authored, claim, deliver
from platform_tests.groundtruth_kb.native_fixtures import put, work_fields


def git(root, *args, check=True):
    result = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Qualification",
            "-c",
            "user.email=qualification@example.invalid",
            *args,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if check:
        assert result.returncode == 0, result.stderr
    return result


def base(root):
    return git(root, "rev-parse", "HEAD").stdout.strip()


def integration(root):
    return Path(git(root, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()).parent


def verify(client, contexts, root, number, path, **proposal_fields):
    document = f"chain-{number}"
    work = f"WI-{number}"
    deliver(
        client,
        contexts,
        document,
        "pb1",
        1,
        "NEW",
        work_item_id=work,
        target_paths=json.dumps([path]),
        **proposal_fields,
    )
    deliver(client, contexts, document, "lo1", 2, "GO", work_item_id=work)
    reserved = claim(client, document, "pb2", 2, "READY", work_item_id=work)
    assert reserved.status_code == 200, reserved.text
    fence = {"native_context_id": "pb2", "fence": reserved.json()["fence"]}
    opened = client.post(f"/v1/bridge/{document}/worktree", json=fence)
    assert opened.status_code == 200, opened.text
    checkout = opened.json()
    (Path(checkout["path"]) / path).write_text(f"result = {number + 1}\n", encoding="utf-8")
    published = client.post(
        f"/v1/bridge/{document}/publish-work", json={**fence, "expected_artifacts": checkout["artifact_preimages"]}
    )
    assert published.status_code == 200, published.text
    assert (root / path).read_text() == f"result = {number + 1}\n"
    assert (integration(root) / path).read_text() != f"result = {number + 1}\n"
    ready = client.post(
        f"/v1/bridge/{document}/deliver",
        json={**fence, "content": authored(contexts["pb2"], document, 3, "READY", **{"Work Item": work})},
    )
    assert ready.status_code == 200, ready.text
    artifacts = client.get(f"/v1/bridge/{document}/artifacts").json()
    deliver(
        client, contexts, document, "lo2", 4, "VERIFIED", work_item_id=work, verified_artifacts=json.dumps(artifacts)
    )


def post(client, action, **body):
    return client.post(
        f"/v1/projects/PROJECT-1/{action}",
        json={
            "native_context_id": "lo3",
            "expected_version": 1,
            **body,
        },
    )


def two_members(bridge):
    _, client, contexts, root = bridge
    parent = base(root)
    assert (
        put(client, "work-items", "WI-2", work_fields(title="Second artifact"), project_id="PROJECT-1").status_code
        == 200
    )
    verify(client, contexts, root, 1, "code.py")
    assert post(client, "prepare-commit").json()["error"]["code"] == "project_not_fully_verified"
    verify(client, contexts, root, 2, "second.py")
    return client, contexts, root, parent


def commit_product(root):
    git(root, "add", "--", "code.py", "second.py", "tests/test_effect.py")
    git(root, "commit", "-m", "Complete the qualified project (WI-1) (WI-2)")
    return git(root, "rev-parse", "HEAD").stdout.strip()


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
