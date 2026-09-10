"""Execute the declared shared gate against real PostgreSQL through the CLI.

The selected registration command, adapter, gate and package execute as child
processes. This qualifies this gate, not every other hook or the vendor host.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import groundtruth_kb
import pytest
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError

from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_bridge import bridge as bridge
from platform_tests.groundtruth_kb.test_native_bridge import claim, deliver
from scripts.check_harness_parity import _commands, _load_projector, _references_script, _registration_events

ROOT = Path(__file__).resolve().parents[2]
pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


@pytest.mark.parametrize(
    "harness", ["claude", "cursor", "goose", "alibaba-cloud-studio", "openrouter", "ollama", "antigravity", "codex"]
)
def test_declared_gate_checks_live_checkout_scope_and_preserves_foreign_work(harness, bridge, tmp_path):
    _service, client, contexts, _work_root = bridge
    engine = _load_projector(ROOT)
    profile = engine.load_profiles()["harnesses"][harness]
    plan = engine.build_plan(harness)
    assert not plan.gaps, plan.gaps
    registration = json.loads(plan.writes[profile["hooks_json_path"]])
    event = profile["hook_events"]["pre_tool_use"]
    commands = [
        command
        for command in _commands(_registration_events(profile, registration)[event])
        if _references_script(command, "scripts/implementation_start_gate.py", profile["project_dir_var"])
    ]
    assert len(commands) == 1
    assert "worktree-scope-gate.py" not in plan.writes[profile["hooks_json_path"]]
    assert "bridge-compliance-gate.py" not in plan.writes[profile["hooks_json_path"]]
    if harness == "claude":
        for tool in ("Write", "Edit"):
            selected = [
                command
                for group in registration["hooks"][event]
                if re.fullmatch(group.get("matcher", ".*"), tool)
                for command in _commands(group)
                if _references_script(command, "scripts/implementation_start_gate.py", profile["project_dir_var"])
            ]
            assert selected == commands, f"{tool} must select the native enforcement command exactly once"

    # Materialize the selected runtime inputs without editing a production projection.
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    for name in (
        "implementation_start_gate.py",
        "controlled_artifact_paths.py",
        "cursor_hook_adapter.py",
        "antigravity_hook_adapter.py",
        "codex_hook_adapter.py",
        "lo_file_safety_payloads.py",
    ):
        shutil.copyfile(ROOT / "scripts" / name, scripts / name)
    runtime = tmp_path / "groundtruth-kb/.venv"
    runtime.parent.mkdir()
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(runtime), sys.prefix], check=True, capture_output=True)
    else:
        pytest.fail("These declared interpreter profiles currently require Windows qualification")

    sentinel = tmp_path / "must-not-open.db"
    sentinel.write_bytes(b"No SQLite fallback")
    document = "projected-effect"
    deliver(client, contexts, document, "pb1", 1, "NEW")
    deliver(client, contexts, document, "lo1", 2, "GO")
    reservation = claim(client, document, "pb2", 2, "READY").json()
    fence = {"native_context_id": "pb2", "fence": reservation["fence"]}
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    config = tmp_path / "server.toml"
    config.write_text(
        '[groundtruth]\nproject_root="."\n[postgresql]\nservice="' + os.environ["GTKB_TEST_POSTGRES_SERVICE"] + '"\n',
        encoding="utf-8",
    )
    server_env = dict(os.environ)
    server_env.pop("GT_AUTHORITY_URL", None)
    server_env.update(
        GT_PROJECT_ROOT=str(tmp_path), PYTHONPATH=str(Path(groundtruth_kb.__file__).resolve().parent.parent)
    )
    env = {k: v for k, v in server_env.items() if not k.startswith(("PG", "GT_POSTGRES_"))}
    env.pop("RUFF_OUTPUT_FILE", None)
    env.update(
        GT_AUTHORITY_URL=url,
        GTKB_PROJECT_ROOT=str(tmp_path),
        GTKB_NATIVE_CONTEXT_ID="pb2",
        GT_DB_PATH=str(sentinel),
        PYTHONIOENCODING="utf-8",
    )
    env[profile["project_dir_var"]] = str(tmp_path)
    expanded = commands[0].replace("$" + profile["project_dir_var"], str(tmp_path))
    argv = [part.strip('"') for part in shlex.split(expanded, posix=False)]
    # The hosts run relative commands from the project directory. Windows
    # CreateProcess does not use subprocess cwd to resolve the executable.
    if harness == "codex":
        argv[0] = shutil.which(argv[0])
        assert argv[0], "The declared Windows PowerShell launcher must exist"
    elif not Path(argv[0]).is_absolute():
        argv[0] = str(tmp_path / argv[0])
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    def check(path=None, *, context="pb2", tool="Write", allowed=False, command=None, cwd=None):
        payload = {
            "cwd": str(cwd or tmp_path),
            "project_root": str(tmp_path),
            "session_id": context,
            "tool_name": tool,
            "tool_input": {"file_path": str(path), "content": "never written by the gate"},
        }
        if command:
            payload["tool_name"] = "Bash"
            payload["tool_input"] = {"command": command}
        if harness == "codex" and not command:
            operation = "Delete" if tool == "Delete" else "Update"
            patch = f"*** Begin Patch\n*** {operation} File: {path}\n"
            if operation == "Update":
                patch += "@@\n-old\n+new\n"
            payload["tool_name"] = "apply_patch"
            payload["tool_input"] = {"command": patch + "*** End Patch\n"}
        if harness == "antigravity":
            if command:
                call = {"name": "run_command", "args": {"CommandLine": command, "Cwd": str(tmp_path)}}
            elif tool == "Edit":
                call = {
                    "name": "replace_file_content",
                    "args": {
                        "TargetFile": str(path),
                        "TargetContent": "old",
                        "ReplacementContent": "new",
                    },
                }
            elif tool == "MultiEdit":
                call = {
                    "name": "multi_replace_file_content",
                    "args": {
                        "TargetFile": str(path),
                        "ReplacementChunks": [{"TargetContent": "old", "ReplacementContent": "new"}],
                    },
                }
            else:
                call = {"name": "write_to_file", "args": {"TargetFile": str(path), "CodeContent": "never written"}}
            payload = {"conversationId": context, "workspacePaths": [str(tmp_path)], "toolCall": call}
        completed = subprocess.run(
            argv,
            input=json.dumps(payload),
            cwd=tmp_path,
            env={**env, "GTKB_NATIVE_CONTEXT_ID": context},
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=20,
            creationflags=flags,
        )
        assert completed.returncode in {0, 2}, completed.stderr
        result = json.loads(completed.stdout)
        if harness == "antigravity":
            assert completed.returncode == 0, result
            assert result["decision"] == ("allow" if allowed else "deny"), result
        elif harness == "cursor":
            assert completed.returncode == (0 if allowed else 2), result
            assert result["permission"] == ("allow" if allowed else "deny"), result
        elif allowed:
            assert result == {}, result
        else:
            assert result["hookSpecificOutput"]["permissionDecision"] == "deny", result
        return result

    process = None
    try:
        with (tmp_path / "service.log").open("wb") as log:
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "groundtruth_kb",
                    "--config",
                    str(config),
                    "service",
                    "serve",
                    "--port",
                    str(port),
                ],
                cwd=tmp_path,
                env=server_env,
                stdout=log,
                stderr=log,
                creationflags=flags,
            )
            http = AuthorityClient(url, timeout=1)
            deadline = time.monotonic() + 25
            while True:
                try:
                    http.request("GET", "/v1/status")
                    break
                except AuthorityClientError:
                    if process.poll() is not None or time.monotonic() > deadline:
                        pytest.fail("The isolated authority failed to start")
                    time.sleep(0.1)
            checkout = tmp_path / ".worktrees" / contexts["pb2"]["session_context_id"]
            check(checkout / "code.py")
            opened = client.post(f"/v1/bridge/{document}/worktree", json=fence)
            assert opened.status_code == 200, opened.text
            before = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
            protected = [checkout / "code.py", tmp_path / "code.py", checkout / "foreign_tracked.txt"]
            preimages = {path: path.read_bytes() for path in protected}
            check(checkout / "code.py", allowed=True)
            check(checkout / "code.py", tool="Edit", allowed=True)
            check(checkout / "code.py", tool="MultiEdit", allowed=True)
            # Bridge messages are authored in this context's scratch space and
            # delivered by the CLI. Neither a new raw file nor an overwrite is
            # an ordinary implementation effect, regardless of its prose.
            raw_bridge = checkout / "bridge"
            raw_bridge.mkdir()
            existing_message = raw_bridge / "foreign-001.md"
            existing_message.write_bytes(b"foreign bridge history\r\n")
            check(raw_bridge / "new-001.md")
            check(existing_message, tool="Edit")
            assert not (raw_bridge / "new-001.md").exists()
            assert existing_message.read_bytes() == b"foreign bridge history\r\n"
            if harness == "codex":
                check("code.py", tool="Edit", cwd=checkout, allowed=True)
                check("foreign_tracked.txt", tool="Edit", cwd=checkout)
            if harness != "antigravity":
                check(checkout / "code.py", tool="Delete", allowed=True)
            check(tmp_path / "code.py")
            check(checkout / "foreign_tracked.txt")
            check(checkout / "code.py", context="lo2")
            check(checkout / "code.py", context="")
            check(tmp_path / "scratchpad" / contexts["pb2"]["session_context_id"] / "note.md", allowed=True)
            check(tmp_path / "scratchpad" / contexts["lo2"]["session_context_id"] / "note.md")

            # Check actual Ruff invocations at the rendered PreToolUse boundary.
            # The hook only verifies; the approved process performs the mutation.
            def ruff_command(*args):
                return subprocess.list2cmdline([sys.executable, "-m", "ruff", *map(str, args)])

            check(command=ruff_command("check", "--fix", checkout / "foreign_tracked.txt"))
            check(command=ruff_command("format", tmp_path / "code.py"))
            check(command=ruff_command("check", "--fix", checkout / "code.py"), context="")
            check(
                command=ruff_command(
                    "check", "--diff", "--output-file", checkout / "foreign_tracked.txt", checkout / "code.py"
                )
            )
            check(
                command=ruff_command("check", "--no-fix", "--no-fix-only", checkout / "code.py"),
                # The native Antigravity envelope always requires its supplied
                # conversation identity, even for a read-only tool call.
                context="pb2" if harness in {"antigravity", "codex"} else "",
                allowed=True,
            )
            code = checkout / "code.py"
            code.write_bytes(b"value=1\n")
            check(command=ruff_command("format", code), allowed=True)
            formatted = subprocess.run(
                [sys.executable, "-m", "ruff", "format", "--isolated", "--no-cache", str(code)],
                cwd=tmp_path,
                env=env,
                capture_output=True,
                timeout=10,
                creationflags=flags,
            )
            assert formatted.returncode == 0, formatted.stderr
            assert code.read_bytes() == b"value = 1\n"
            preimages[code] = b"value = 1\n"  # Only the explicitly allowed effect changed.
            assert client.get(f"/v1/bridge/{document}/show?include_content=true").json() == before
            assert client.post(f"/v1/bridge/{document}/check", json=fence).status_code == 200
            process.terminate()
            process.wait(timeout=10)
            check(checkout / "code.py")  # Authority outage must refuse.
            check(command=ruff_command("check", "--fix", checkout / "code.py"))
            assert {path: path.read_bytes() for path in protected} == preimages
            assert sentinel.read_bytes() == b"No SQLite fallback"
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
        assert runtime.parent.resolve() == (tmp_path / "groundtruth-kb").resolve()
        if runtime.is_dir():
            os.rmdir(runtime)  # Remove only the fixture junction, never its target.
