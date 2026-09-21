"""Real PostgreSQL/HTTP/CLI delivery through controlled provider transports.

The model responses and other hook verdicts are fixtures; the implementation
gate and commands execute the actual
CLI in separate processes. Four fresh contexts exercise binding, interruption,
scoped implementation, actual executable tests, independent verification and one
complete-project commit under cp1252 child-process stdio. This does not qualify
provider intelligence, installed
remaining hook correctness or dispatcher activation.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError

from platform_tests.groundtruth_kb.bridge_fixtures import authored, deliver
from platform_tests.groundtruth_kb.bridge_fixtures import bridge as bridge
from platform_tests.groundtruth_kb.native_fixtures import _serve_authority, seed_startup_sources
from platform_tests.groundtruth_kb.native_fixtures import native as native
from platform_tests.scripts.provider_fixtures import (
    PROVIDERS,
    _response,
    create_provider_guard_fixtures,
    native_id_from_payload,
)
from scripts import ollama_harness as ollama

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


@pytest.mark.parametrize("provider", PROVIDERS)
def test_provider_initializes_each_subject_and_role_without_a_bridge_assignment(provider, bridge, tmp_path):
    _service, client, _, _ = bridge
    runtime = create_provider_guard_fixtures(provider, tmp_path)
    seed_startup_sources(client, tmp_path)
    before = client.get("/v1/bridge/state-report").json()
    before.pop("observed_at")
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    process, _ = _serve_authority(tmp_path, port)
    url = f"http://127.0.0.1:{port}"
    config = tmp_path / "client.toml"
    config.write_text(
        f'[groundtruth]\nproject_root="."\nauthority_url="{url}"\ndb_path="must-not-open.db"\n', encoding="utf-8"
    )
    sentinel = tmp_path / "must-not-open.db"
    sentinel.write_bytes(b"No SQLite initialization or fallback.")
    prefix = [sys.executable, "-m", "groundtruth_kb", "--config", str(config)]
    identifiers = set()
    try:
        for subject, role in (("gtkb", "pb"), ("gtkb", "lo"), ("application", "pb"), ("application", "lo")):
            marker = f"::init {subject} {role}"
            prompt = f"First input: café.\r\n{marker}\r\n::open deliberation\r\nRead the immutable binding."
            observed = {"turns": 0, "native_id": None, "argv": None, "results": [], "codes": []}

            def chat(*args, prompt=prompt, observed=observed, subject=subject, role=role):
                payload = args[-2]
                assert [m["content"] for m in payload["messages"] if m["role"] == "user"][0] == prompt
                context_id = native_id_from_payload(payload)
                if observed["native_id"] is None:
                    observed["native_id"] = context_id
                assert context_id == observed["native_id"]
                turn = observed["turns"]
                observed["turns"] += 1
                if turn == 6:
                    assert "session_init_conflict" in json.dumps(payload)
                    assert "host_observations" in json.dumps(payload)
                    return _response(provider, content="Current binding read; conflicting rebind refused.")
                if turn == 5:
                    args = ["context", "session", "--native-context-id", context_id, "--json"]
                elif turn in (2, 4):
                    args = ["session", "show", "--native-context-id", context_id, "--json"]
                else:
                    supplied = prompt if turn < 2 else f"::init {subject} {'lo' if role == 'pb' else 'pb'}"
                    args = ["session", "bind", "--native-context-id", context_id, "--init-keyword", supplied, "--json"]
                observed["argv"] = [*prefix, *args]
                return _response(
                    provider, tool="Bash", arguments={"command": subprocess.list2cmdline(observed["argv"])}
                )

            def runner(command, cwd, env, timeout, observed=observed):
                assert command == subprocess.list2cmdline(observed["argv"])
                assert env["GTKB_NATIVE_CONTEXT_ID"] == observed["native_id"]
                assert "GTKB_AUTHOR_SESSION_CONTEXT_ID" not in env
                client_env = {k: v for k, v in env.items() if not k.startswith(("PG", "GT_POSTGRES_"))}
                client_env.pop("GT_AUTHORITY_URL", None)
                client_env["PYTHONIOENCODING"] = "utf-8"
                completed = subprocess.run(
                    observed["argv"],
                    cwd=cwd,
                    env=client_env,
                    capture_output=True,
                    encoding="utf-8",
                    timeout=min(timeout, 20),
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
                observed["codes"].append(completed.returncode)
                if completed.returncode == 0:
                    observed["results"].append(json.loads(completed.stdout))
                else:
                    assert "session_init_conflict" in completed.stderr, (completed.stdout, completed.stderr)
                    assert '"observed_markers"' in completed.stderr and "gt session show" in completed.stderr
                    observed["results"].append(None)
                return completed

            args = [
                prompt,
                provider.ModelRoute("fixture", "fixture-model", "v1", True, ("Bash",)),
                "https://fixture.invalid",
            ]
            if provider is not ollama:
                args.append("fixture-key")
            args.extend([7, tmp_path])
            result = provider.run_tool_loop(
                *args,
                chat_func=chat,
                command_runner=runner,
                guard_runner=lambda *_: runtime.GuardExecutionResult(0, "{}"),
            )
            assert result == "Current binding read; conflicting rebind refused."
            assert observed["codes"][:3] == [0, 0, 0] and observed["codes"][3] != 0
            assert observed["codes"][4] == 0
            assert observed["codes"][5] == 0
            assert observed["results"][0]["status"] == "init_requested"
            assert observed["results"][1]["status"] == "already_initialized_idempotent"
            binding = observed["results"][0]["binding"]
            assert binding == observed["results"][1]["binding"] == observed["results"][2] == observed["results"][4]
            assert binding["subject"] == subject
            assert binding["role"] == {"pb": "prime-builder", "lo": "loyal-opposition"}[role]
            assert binding["native_context_id"] == observed["native_id"]
            assert observed["results"][5]["binding"] == binding
            assert all(v["status"] == "unavailable" for v in observed["results"][5]["host_observations"].values())
            assert observed["native_id"] not in identifiers
            identifiers.add(observed["native_id"])
            after = client.get("/v1/bridge/state-report").json()
            after.pop("observed_at")
            assert after == before
            assert sentinel.read_bytes() == b"No SQLite initialization or fallback."
        assert len(identifiers) == 4
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)


def test_explicit_init_cli_reports_missing_invalid_and_conflicting_markers(bridge, tmp_path):
    _service, client, contexts, _ = bridge
    before = client.get("/v1/bridge/state-report").json()
    before.pop("observed_at")
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    process, server_env = _serve_authority(tmp_path, port)
    config = tmp_path / "init-client.toml"
    config.write_text(
        f'[groundtruth]\nproject_root="."\nauthority_url="http://127.0.0.1:{port}"\ndb_path="init-sentinel.db"\n',
        encoding="utf-8",
    )
    sentinel = tmp_path / "init-sentinel.db"
    sentinel.write_bytes(b"Binding diagnostics must not open SQLite.")
    client_env = {k: v for k, v in server_env.items() if not k.startswith(("PG", "GT_POSTGRES_"))}

    def cli(*arguments):
        return subprocess.run(
            [sys.executable, "-m", "groundtruth_kb", "--config", str(config), *arguments],
            cwd=tmp_path,
            env=client_env,
            capture_output=True,
            encoding="utf-8",
            timeout=20,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

    try:
        for prompt, code in (
            ("An ordinary owner request.", "no_init_marker"),
            ("::init gtkb pb # private-owner-content", "invalid_init_marker"),
            ("::init gtkb pb\r\n::init gtkb lo", "session_init_conflict"),
            ("::init application pb\n::init gtkb pb", "session_init_conflict"),
        ):
            result = cli(
                "session", "bind", "--native-context-id", "fresh-cli-refusal", "--init-keyword", prompt, "--json"
            )
            assert result.returncode != 0 and not result.stdout
            assert code in result.stderr and '"observed_markers"' in result.stderr
            assert '"invalid_marker_line_numbers"' in result.stderr and "gt session show" in result.stderr
            assert "private-owner-content" not in result.stderr
            read = cli("session", "show", "--native-context-id", "fresh-cli-refusal", "--json")
            assert read.returncode != 0 and "no_session_binding" in read.stderr
        conflict = cli("session", "bind", "--native-context-id", "pb1", "--init-keyword", "::init gtkb lo", "--json")
        assert conflict.returncode != 0 and "session_init_conflict" in conflict.stderr
        assert '"::init gtkb lo"' in conflict.stderr and "gt session show" in conflict.stderr
        read = cli("session", "show", "--native-context-id", "pb1", "--json")
        assert read.returncode == 0 and json.loads(read.stdout) == contexts["pb1"]
        after = client.get("/v1/bridge/state-report").json()
        after.pop("observed_at")
        assert after == before
        assert sentinel.read_bytes() == b"Binding diagnostics must not open SQLite."
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)


@pytest.mark.parametrize("provider", PROVIDERS)
def test_provider_binds_claims_authors_and_delivers_through_separate_cli(provider, bridge, tmp_path, monkeypatch):
    service, client, contexts, _work_root = bridge
    document = "provider-native-cli"
    deliver(client, contexts, document, "pb1", 1, "NEW")
    runtime = create_provider_guard_fixtures(provider, tmp_path)
    # Exercise the current normal commit boundary in this disposable repository.
    # The real reference hook calls back into the same live authority service.
    hooks = tmp_path / ".githooks"
    hooks.mkdir()
    reference = hooks / "reference-transaction"
    reference.write_bytes((Path(__file__).resolve().parents[2] / ".githooks/reference-transaction").read_bytes())
    reference.chmod(0o755)
    subprocess.run(["git", "-C", str(tmp_path), "config", "core.hooksPath", ".githooks"], check=True)
    # An unrelated legacy variable must not cause a second role-binding write.
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", "invalid-legacy-value")
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "unrelated-dispatch")
    monkeypatch.setenv("GTKB_NATIVE_CONTEXT_ID", "inherited-context")
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", "inherited-binding")
    native_id = None
    sentinel = tmp_path / "must-not-open.db"
    sentinel.write_bytes(b"SQLite must not be opened by this provider workload.")
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    server_config = tmp_path / "server.toml"
    server_config.write_text(
        '[groundtruth]\nproject_root="."\n[postgresql]\nservice="' + os.environ["GTKB_TEST_POSTGRES_SERVICE"] + '"\n',
        encoding="utf-8",
    )
    client_config = tmp_path / "client.toml"
    client_config.write_text(
        f'[groundtruth]\nauthority_url="{url}"\ndb_path="must-not-open.db"\nproject_root="."\n',
        encoding="utf-8",
    )
    server_env = os.environ.copy()
    server_env.pop("GT_AUTHORITY_URL", None)
    server_env["GT_PROJECT_ROOT"] = str(tmp_path)
    server_env["GT_DB_PATH"] = str(sentinel)
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    prefix = [sys.executable, "-m", "groundtruth_kb", "--config", str(client_config)]
    state = {"calls": [], "results": [], "argv": [], "authored": None, "binding": None, "fence": None}
    message_path = None
    completion_version = 2
    completion_checks = []

    def process_response(argv):
        state["argv"] = argv
        return _response(provider, tool="Bash", arguments={"command": subprocess.list2cmdline(argv)})

    def command_response(*args):
        return process_response([*prefix, *args])

    def command_runner(command, cwd, env, timeout):
        check_argv = [
            sys.executable,
            "-m",
            "groundtruth_kb",
            "bridge",
            "check-delivery",
            document,
            "--version",
            str(completion_version),
            "--native-context-id",
            native_id,
            "--json",
        ]
        is_completion = command == subprocess.list2cmdline(check_argv)
        if not is_completion:
            assert command == subprocess.list2cmdline(state["argv"])
        argv = check_argv if is_completion else state["argv"]
        assert env["GTKB_NATIVE_CONTEXT_ID"] == native_id
        assert "GTKB_AUTHOR_SESSION_CONTEXT_ID" not in env
        client_env = {key: value for key, value in env.items() if not key.startswith(("PG", "GT_POSTGRES_"))}
        client_env.pop("GT_AUTHORITY_URL", None)
        if is_completion:
            client_env["GT_AUTHORITY_URL"] = url
        # Exercise the Windows encoding failure independently of the test
        # runner's UTF-8 environment. The CLI must supply its UTF-8 contract.
        client_env["PYTHONIOENCODING"] = "cp1252"
        client_env["PYTHONUTF8"] = "0"
        client_env["GT_PROJECT_ROOT"] = str(tmp_path)
        client_env["GT_DB_PATH"] = str(sentinel)
        completed = subprocess.run(
            argv,
            cwd=cwd,
            env=client_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=min(timeout, 30),
            creationflags=flags,
        )
        if is_completion:
            completion_checks.append(
                (native_id, completion_version, completed.returncode, completed.stdout, completed.stderr)
            )
        else:
            assert completed.returncode == 0, (completed.stdout, completed.stderr)
            state["results"].append(json.loads(completed.stdout))
        return completed

    real_effect_checks = []

    def guards(_path, payload, env, _timeout):
        assert payload["session_id"] == env["GTKB_NATIVE_CONTEXT_ID"] == native_id
        if _path.name == "implementation_start_gate.py":
            guard_env = {key: value for key, value in env.items() if not key.startswith(("PG", "GT_POSTGRES_"))}
            guard_env.update(GT_AUTHORITY_URL=url, GT_PROJECT_ROOT=str(tmp_path), GT_DB_PATH=str(sentinel))
            completed = subprocess.run(
                [sys.executable, str(Path(__file__).resolve().parents[2] / "scripts/implementation_start_gate.py")],
                input=json.dumps(payload),
                cwd=tmp_path,
                env=guard_env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=20,
                creationflags=flags,
            )
            real_effect_checks.append((payload["tool_name"], completed.returncode, completed.stdout))
            assert completed.returncode == 0, completed.stderr
            assert json.loads(completed.stdout) == {}, completed.stdout
            return runtime.GuardExecutionResult(completed.returncode, completed.stdout)
        return runtime.GuardExecutionResult(0, "{}")

    def chat(*args):
        nonlocal native_id, message_path
        payload = args[-2]
        state["calls"].append(payload)
        step = len(state["calls"])
        assert {tool.get("name") or tool["function"]["name"] for tool in payload["tools"]} == {"Write", "Bash"}
        if step == 1:
            native_id = native_id_from_payload(payload)
            unbound = client.get("/v1/sessions/binding", params={"native_context_id": native_id})
            assert unbound.status_code == 422
            assert unbound.json()["error"]["code"] == "no_session_binding"
            return command_response(
                "session", "bind", "--native-context-id", native_id, "--init-keyword", "::init gtkb lo", "--json"
            )
        if step == 2:
            assert state["results"][-1]["status"] == "init_requested"
            state["binding"] = state["results"][-1]["binding"]
            assert state["binding"]["session_context_id"] != native_id
            message_path = "scratchpad/" + state["binding"]["session_context_id"] + "/reply.md"
            return command_response(
                "bridge",
                "claim",
                document,
                "--work-item-id",
                "WI-1",
                "--native-context-id",
                native_id,
                "--expected-version",
                "1",
                "--status",
                "GO",
                "--request-id",
                "provider-go",
                "--json",
            )
        if step == 3:
            state["fence"] = state["results"][-1]["fence"]
            state["authored"] = authored(state["binding"], document, 2, "GO")
            return _response(provider, tool="Write", arguments={"path": message_path, "content": state["authored"]})
        if step == 4:
            assert (tmp_path / message_path).read_bytes() == state["authored"].encode("utf-8")
            return command_response(
                "bridge",
                "deliver",
                document,
                "--native-context-id",
                native_id,
                "--fence",
                str(state["fence"]),
                "--content-file",
                message_path,
                "--json",
            )
        if step == 5:
            return command_response("bridge", "show", document, "--content", "--json")
        assert step == 6
        assert state["results"][-1]["messages"][-1]["content"] == state["authored"]
        return _response(provider, content="GO delivered and read back through the native CLI.")

    with (tmp_path / "service.log").open("wb") as log:
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
            cwd=tmp_path,
            env=server_env,
            stdout=log,
            stderr=log,
            creationflags=flags,
        )
        try:
            deadline = time.monotonic() + 30
            http = AuthorityClient(url, timeout=1)
            while True:
                try:
                    http.request("GET", "/v1/status")
                    break
                except AuthorityClientError:
                    if process.poll() is not None or time.monotonic() >= deadline:
                        pytest.fail("Disposable native service did not start; inspect service.log")
                    time.sleep(0.1)
            route = provider.ModelRoute("fixture", "fixture-model", "v1", True, ("Write", "Bash"))
            args = ["::init gtkb lo\n::open build\nReview the assigned proposal", route, "https://fixture.invalid"]
            if provider is not ollama:
                args.append("fixture-key")
            args.extend([8, tmp_path])
            result = provider.run_tool_loop(
                *args,
                skill="bridge-review",
                bridge_document=document,
                bridge_version=2,
                chat_func=chat,
                guard_runner=guards,
                command_runner=command_runner,
            )
            assert result == "GO delivered and read back through the native CLI."
            assert len(state["results"]) == 4
            assert len(state["calls"]) == 6
            current = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
            assert current["messages"][-1]["content"] == state["authored"]
            binding = client.get("/v1/sessions/binding", params={"native_context_id": native_id})
            assert binding.json() == state["binding"]
            assert all(native_id_from_payload(payload) == native_id for payload in state["calls"])

            # The successor receives only its assigned document and exact init.
            # It reconstructs the next action from CLI reads in a fresh loop.
            first_native_id, first_binding = native_id, state["binding"]
            state = {"calls": [], "results": [], "argv": [], "binding": None, "fence": None}
            native_id = None

            def successor_chat(*args):
                nonlocal native_id
                payload = args[-2]
                state["calls"].append(payload)
                step = len(state["calls"])
                if step == 1:
                    native_id = native_id_from_payload(payload)
                    return command_response(
                        "session",
                        "bind",
                        "--native-context-id",
                        native_id,
                        "--init-keyword",
                        "::init gtkb pb",
                        "--json",
                    )
                assert native_id_from_payload(payload) == native_id
                if step == 2:
                    assert state["results"][-1]["status"] == "init_requested"
                    state["binding"] = state["results"][-1]["binding"]
                    return command_response("bridge", "show", document, "--content", "--json")
                if step == 3:
                    observed = state["results"][-1]
                    assert observed["messages"][-1]["status"] == "GO"
                    assert observed["messages"][-1]["content"].startswith("::init gtkb pb")
                    return command_response(
                        "bridge",
                        "claim",
                        document,
                        "--work-item-id",
                        observed["attempt"]["work_item_id"],
                        "--native-context-id",
                        native_id,
                        "--expected-version",
                        str(observed["attempt"]["head_version"]),
                        "--status",
                        "READY",
                        "--request-id",
                        "successor-ready",
                        "--json",
                    )
                if step == 4:
                    state["fence"] = state["results"][-1]["fence"]
                    return command_response(
                        "bridge",
                        "release",
                        document,
                        "--native-context-id",
                        native_id,
                        "--fence",
                        str(state["fence"]),
                        "--json",
                    )
                assert step == 5 and state["results"][-1]["status"] == "released"
                return _response(provider, content="Next artifact claimed and released through the CLI.")

            args[0] = (
                "::init gtkb pb\n::open build\nRead the assigned document and claim then release its next artifact."
            )
            args[1] = provider.ModelRoute("fixture", "fixture-model", "v1", True, ("Bash",))
            completion_version = 3
            with pytest.raises(RuntimeError, match="bridge_delivery_incomplete") as incomplete:
                provider.run_tool_loop(
                    *args,
                    bridge_document=document,
                    bridge_version=3,
                    chat_func=successor_chat,
                    guard_runner=guards,
                    command_runner=command_runner,
                )
            assert incomplete.value.code == "bridge_delivery_incomplete"
            assert native_id != first_native_id
            assert state["binding"]["session_context_id"] != first_binding["session_context_id"]
            assert state["binding"]["role"] == "prime-builder"
            assert first_binding["role"] == "loyal-opposition"
            current = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
            assert current["attempt"]["head_version"] == 2
            assert len(state["results"]) == 4 and len(state["calls"]) == 5
            # Two more independent contexts finish the work. They receive the
            # assigned document/init only; all bindings, claims, paths, reviewed
            # bytes and project versions come from their own CLI operations.
            seen_contexts = {first_native_id, native_id}
            original_head = subprocess.check_output(
                ["git", "-C", str(tmp_path), "rev-parse", "HEAD"], text=True
            ).strip()
            executable_test = (
                "import json, runpy\nfrom pathlib import Path\n"
                "value = runpy.run_path(str(Path(__file__).parents[1] / 'code.py'))['value']\n"
                "assert value == 2, value\nprint(json.dumps({'verified_value': value}))\n"
            )

            def completion_steps(role):
                status = "READY" if role == "pb" else "VERIFIED"
                yield command_response(
                    "session",
                    "bind",
                    "--native-context-id",
                    native_id,
                    "--init-keyword",
                    f"::init gtkb {role}",
                    "--json",
                )
                assert state["results"][-1]["status"] == "init_requested"
                state["binding"] = state["results"][-1]["binding"]
                scratch = "scratchpad/" + state["binding"]["session_context_id"]
                yield command_response("bridge", "show", document, "--content", "--json")
                observed = state["results"][-1]
                assert observed["messages"][-1]["status"] == ("GO" if role == "pb" else "READY")
                project = observed["attempt"]["project_id"]
                work_item = observed["attempt"]["work_item_id"]
                version = observed["attempt"]["head_version"]
                yield command_response(
                    "bridge",
                    "claim",
                    document,
                    "--work-item-id",
                    work_item,
                    "--native-context-id",
                    native_id,
                    "--expected-version",
                    str(version),
                    "--status",
                    status,
                    "--request-id",
                    status.lower() + "-completion",
                    "--json",
                )
                state["fence"] = state["results"][-1]["fence"]
                fence_options = ["--native-context-id", native_id, "--fence", str(state["fence"])]
                yield command_response("bridge", "worktree", document, *fence_options, "--json")
                checkout = state["results"][-1]
                work_path = Path(checkout["path"])
                assert work_path.is_relative_to(tmp_path)
                relative = work_path.relative_to(tmp_path).as_posix()
                yield command_response("bridge", "check", document, *fence_options, "--json")
                if role == "pb":
                    yield _response(
                        provider, tool="Write", arguments={"path": relative + "/code.py", "content": "value = 2\n"}
                    )
                    yield _response(
                        provider,
                        tool="Write",
                        arguments={"path": relative + "/tests/test_effect.py", "content": executable_test},
                    )
                else:
                    yield _response(provider, tool="Read", arguments={"path": relative + "/code.py"})
                    yield _response(provider, tool="Read", arguments={"path": relative + "/tests/test_effect.py"})
                yield process_response([sys.executable, str(work_path / "tests/test_effect.py")])
                assert state["results"][-1] == {"verified_value": 2}
                if role == "pb":
                    preimages = scratch + "/preimages.json"
                    yield _response(
                        provider,
                        tool="Write",
                        arguments={"path": preimages, "content": json.dumps(checkout["artifact_preimages"])},
                    )
                    yield command_response(
                        "bridge", "publish-work", document, *fence_options, "--preimages-file", preimages, "--json"
                    )
                    assert state["results"][-1]["status"] == "published"
                    evidence = {}
                else:
                    yield command_response("bridge", "artifacts", document, "--json")
                    evidence = {"verified_artifacts": json.dumps(state["results"][-1])}
                content = authored(
                    state["binding"],
                    document,
                    version + 1,
                    status,
                    **{"Project": project, "Work Item": work_item, **evidence},
                )
                message = scratch + "/result.md"
                yield _response(provider, tool="Write", arguments={"path": message, "content": content})
                yield command_response(
                    "bridge", "deliver", document, *fence_options, "--content-file", message, "--json"
                )
                yield command_response("bridge", "show", document, "--content", "--json")
                assert state["results"][-1]["messages"][-1]["content"] == content
                assert (
                    subprocess.check_output(["git", "-C", str(tmp_path), "rev-parse", "HEAD"], text=True).strip()
                    == original_head
                )
                if role == "lo":
                    yield command_response("projects", "show", project, "--json")
                    project_version = state["results"][-1]["project"]["version"]
                    commit_message = scratch + "/commit.txt"
                    yield _response(
                        provider,
                        tool="Write",
                        arguments={
                            "path": commit_message,
                            "content": f"fix: complete the qualified project ({work_item})\n",
                        },
                    )
                    yield command_response(
                        "projects",
                        "commit",
                        project,
                        "--native-context-id",
                        native_id,
                        "--expected-version",
                        str(project_version),
                        "--message-file",
                        commit_message,
                        "--json",
                    )
                    assert state["results"][-1]["status"] == "confirmed"
                    yield command_response("bridge", "show", document, "--content", "--json")
                    terminal = state["results"][-1]
                    assert terminal["attempt"]["disposition"] == "committed"
                    assert "messages" not in terminal
                yield _response(provider, content=status + " completed through the CLI.")

            for role in ("pb", "lo"):
                state = {"calls": [], "results": [], "argv": [], "binding": None, "fence": None}
                native_id = None
                steps = completion_steps(role)

                def completion_chat(*chat_args, context_state=state, context_steps=steps):
                    nonlocal native_id
                    payload = chat_args[-2]
                    context_state["calls"].append(payload)
                    if native_id is None:
                        native_id = native_id_from_payload(payload)
                    assert native_id_from_payload(payload) == native_id
                    return next(context_steps)

                completion_args = [
                    f"::init gtkb {role}\n::open build\nComplete the next response for {document} using current CLI state.",
                    provider.ModelRoute("fixture", "fixture-model", "v1", True, ("Read", "Write", "Bash")),
                    "https://fixture.invalid",
                ]
                if provider is not ollama:
                    completion_args.append("fixture-key")
                completion_args.extend([24, tmp_path])
                completion_version = 3 if role == "pb" else 4
                result = provider.run_tool_loop(
                    *completion_args,
                    bridge_document=document,
                    bridge_version=completion_version,
                    chat_func=completion_chat,
                    guard_runner=guards,
                    command_runner=command_runner,
                )
                assert result == ("READY" if role == "pb" else "VERIFIED") + " completed through the CLI."
                assert native_id not in seen_contexts
                seen_contexts.add(native_id)

            assert [check[2] for check in completion_checks] == [0, 1, 0, 0], completion_checks
            assert len({check[0] for check in completion_checks}) == 4
            committed = subprocess.check_output(["git", "-C", str(tmp_path), "rev-parse", "HEAD"], text=True).strip()
            assert committed != original_head
            assert (
                subprocess.check_output(
                    ["git", "-C", str(tmp_path), "rev-list", "--count", original_head + ".." + committed], text=True
                ).strip()
                == "1"
            )
            assert set(
                subprocess.check_output(
                    ["git", "-C", str(tmp_path), "show", "--format=", "--name-only", committed], text=True
                ).splitlines()
            ) == {"code.py", "tests/test_effect.py"}
            assert (tmp_path / "code.py").read_text(encoding="utf-8") == "value = 2\n"
            assert client.get("/v1/projects/PROJECT-1").json()["project"]["status"] == "verified"
            assert not (tmp_path / "bridge").exists()
            assert sentinel.read_bytes() == b"SQLite must not be opened by this provider workload."
            assert any(tool == "Write" for tool, _code, _output in real_effect_checks)
            assert any(tool == "Bash" for tool, _code, _output in real_effect_checks)
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
