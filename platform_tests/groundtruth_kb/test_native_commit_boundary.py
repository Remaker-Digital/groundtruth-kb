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
    assert expected in result.output, (result.output, result.exception)
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
    assert result.exit_code == 0, (result.output, result.exception)
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
