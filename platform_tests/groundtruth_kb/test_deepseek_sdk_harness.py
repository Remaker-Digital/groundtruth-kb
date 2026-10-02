"""DeepSeek SDK harness: launcher contract without the runtime, and the installed runtime's actual native tools
against the live CLI claim (opt-in: GTKB_RUN_DEEPSEEK_SDK=1 with GTKB_DEEPSEEK_SDK_DIR holding runtime-env)."""

from __future__ import annotations

import importlib.util
import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from platform_tests.groundtruth_kb.bridge_fixtures import bridge as bridge
from platform_tests.groundtruth_kb.bridge_fixtures import claim, deliver
from platform_tests.groundtruth_kb.native_fixtures import FLAGS, _serve_authority
from platform_tests.groundtruth_kb.native_fixtures import native as native

ROOT = Path(__file__).resolve().parents[2]
SDK_SOURCE = ROOT / "infrastructure" / "deepseek-sdk"
pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]

DRIVER = """import { readFileSync, writeFileSync } from 'node:fs';
export const name = 'gtkb-qualification-driver';
export const inject = ['tools', 'agents'];
export function apply(ctx) {
  const cases = JSON.parse(readFileSync(process.env.GTKB_QUALIFICATION_CASES, 'utf8'));
  const output = process.env.GTKB_QUALIFICATION_OUTPUT;
  ctx.on('tools/pre-execute', async () => ({kind: 'allow'}));
  ctx.effect(() => {
    let ticks = 0;
    const timer = setInterval(() => {
      const schemas = ctx.tools.schemas();
      if (!['pwsh', 'str_replace_editor'].every(n => schemas.some(x => x.name === n))) {
        if (++ticks < 100) return;
        clearInterval(timer);
        writeFileSync(output, JSON.stringify({error: 'Native tools failed to load', schemas}));
        return;
      }
      clearInterval(timer);
      (async () => {
        const handle = await ctx.agents.create({sessionId: 'qualification-sdk-session',
          agentOptions: {provider: 'deepseek-official', model: 'qualification-no-network'}});
        const results = [];
        for (const item of cases) {
          const result = await ctx.tools.execute({callId: item.id, name: item.tool, arguments: item.arguments,
            agent: handle.agent, signal: new AbortController().signal});
          results.push({id: item.id, isError: result.isError === true});
        }
        await handle.dispose();
        writeFileSync(output, JSON.stringify({results}));
      })().catch(error => writeFileSync(output, JSON.stringify({error: String(error)})));
    }, 100);
    return () => clearInterval(timer);
  });
}
"""

WORKER = """from deepseek_harness.client import HarnessClient, HarnessConfig
import json, os, sys, time
from pathlib import Path
config = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
with HarnessClient(HarnessConfig(dsh_bin=config['runtime'], profile=config['profile'], patches=tuple(config['patches']),
        dsh_home=config['home'], cwd=config['cwd'], initialize_timeout_seconds=60, request_timeout_seconds=60,
        shutdown_timeout_seconds=10)) as client:
    client.initialize(cwd=config['cwd'], provider='deepseek-official', model='qualification-no-network')
    deadline = time.monotonic() + 120
    while not Path(os.environ['GTKB_QUALIFICATION_OUTPUT']).exists():
        if time.monotonic() > deadline:
            raise SystemExit('driver timed out')
        time.sleep(0.1)
"""


def _launcher():
    spec = importlib.util.spec_from_file_location("deepseek_sdk_harness", SDK_SOURCE / "harness.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _runtime_dir() -> Path:
    if os.environ.get("GTKB_RUN_DEEPSEEK_SDK") != "1":
        pytest.skip("Set GTKB_RUN_DEEPSEEK_SDK=1 to exercise the installed DeepSeek runtime")
    directory = Path(os.environ.get("GTKB_DEEPSEEK_SDK_DIR", ""))
    if not (directory / "runtime-env").is_dir():
        pytest.skip("GTKB_DEEPSEEK_SDK_DIR must name a directory holding the installed runtime-env")
    return directory


def test_installation_verification_refuses_missing_and_mismatched_identity(tmp_path):
    launcher = _launcher()
    (tmp_path / "release.json").write_bytes((SDK_SOURCE / "release.json").read_bytes())
    with pytest.raises(launcher.LauncherError) as missing:
        launcher.verify_installation(tmp_path)
    assert missing.value.code == launcher.EXIT_INSTALLATION_INVALID
    release = json.loads((tmp_path / "release.json").read_text(encoding="utf-8"))
    executable = tmp_path / "runtime-env" / release["runtime"]["executable"]
    executable.parent.mkdir(parents=True)
    executable.write_bytes(b"not the pinned runtime")
    (tmp_path / "installed.json").write_text(
        json.dumps(
            {"sdk_sha256": release["sdk"]["sha256"], "executable_sha256": release["runtime"]["executable_sha256"]}
        ),
        encoding="utf-8",
    )
    with pytest.raises(launcher.LauncherError) as drifted:
        launcher.verify_installation(tmp_path)
    assert drifted.value.code == launcher.EXIT_INSTALLATION_INVALID
    assert "differs from the pinned identity" in str(drifted.value)


def test_binding_and_delivery_failures_are_typed_and_never_reported_as_success():
    launcher = _launcher()

    def refusing(arguments):
        raise launcher.LauncherError(launcher.EXIT_STARTUP_FAILED, "gt refused: " + " ".join(arguments[:2]))

    with pytest.raises(launcher.LauncherError) as bind_error:
        launcher.bind_context(refusing, "deepseek-sdk-x", "::init gtkb lo")
    assert bind_error.value.code == launcher.EXIT_BIND_FAILED
    with pytest.raises(launcher.LauncherError) as empty:
        launcher.bind_context(lambda arguments: {}, "deepseek-sdk-x", "::init gtkb lo")
    assert empty.value.code == launcher.EXIT_BIND_FAILED
    with pytest.raises(launcher.LauncherError) as incomplete:
        launcher.check_delivery(refusing, "doc", 2, "deepseek-sdk-x")
    assert incomplete.value.code == launcher.EXIT_DELIVERY_INCOMPLETE
    delivered = launcher.check_delivery(lambda arguments: {"status": "delivered", "version": 2}, "doc", 2, "x")
    assert delivered["status"] == "delivered"


@pytest.mark.parametrize("status", ["init_requested", "already_initialized_idempotent"])
def test_sdk_binding_consumer_accepts_both_native_success_outcomes(status):
    launcher = _launcher()
    binding = {
        "native_context_id": "deepseek-sdk-result",
        "session_context_id": "SENV-result",
        "subject": "gtkb",
        "role": "loyal-opposition",
        "created_at": "2026-09-12T00:00:00+00:00",
        "minimum_idempotency_identity": "immutable-idempotency",
    }
    calls = []

    def cli(arguments):
        calls.append(arguments)
        return {"status": status, "binding": binding}

    assert launcher.bind_context(cli, "deepseek-sdk-result", "::init gtkb lo") == binding
    assert calls == [
        ["session", "bind", "--native-context-id", "deepseek-sdk-result", "--init-keyword", "::init gtkb lo"]
    ]
    assert "status" not in binding


@pytest.mark.parametrize(
    "result",
    [
        None,
        [],
        {"session_context_id": "SENV-flat", "role": "loyal-opposition", "native_context_id": "deepseek-sdk-result"},
        {"status": "no_init_marker", "binding": {}},
        {"status": "invented-success", "binding": {}},
        {"status": "init_requested", "binding": None},
        {"status": "init_requested", "binding": []},
        {"status": "init_requested", "binding": {"session_context_id": "SENV-x", "role": "loyal-opposition"}},
        {
            "status": "already_initialized_idempotent",
            "binding": {
                "native_context_id": "another-context",
                "session_context_id": "SENV-x",
                "role": "loyal-opposition",
            },
        },
    ],
)
def test_sdk_binding_consumer_refuses_unusable_results_and_other_contexts(result):
    launcher = _launcher()
    with pytest.raises(launcher.LauncherError) as refusal:
        launcher.bind_context(lambda arguments: result, "deepseek-sdk-result", "::init gtkb lo")
    assert refusal.value.code == launcher.EXIT_BIND_FAILED


def test_prompt_carries_the_neutral_baseline_binding_facts_and_task(tmp_path):
    launcher = _launcher()
    (tmp_path / "AGENTS.md").write_text("# GT-KB session instructions\nRead current state.\n", encoding="utf-8")
    binding = {"native_context_id": "deepseek-sdk-1", "session_context_id": "sc-1", "role": "loyal-opposition"}
    prompt = launcher.build_prompt(tmp_path, binding, "Review the proposal.\n", "doc-1", 2)
    assert prompt.startswith("# GT-KB session instructions")
    for fact in (
        "deepseek-sdk-1",
        "sc-1",
        "loyal-opposition",
        "doc-1",
        "version 2",
        "check-delivery",
        "Review the proposal.",
    ):
        assert fact in prompt
    assert "DEEPSEEK_API_KEY" not in prompt


def _run_cases(sdk_dir, launcher, *, home, cwd, context, url, root, cases, base_env):
    """Start the installed runtime once with the batch guard and a test driver, execute the cases, return decisions."""
    release = json.loads((sdk_dir / "release.json").read_text(encoding="utf-8"))
    runtime = sdk_dir / "runtime-env" / release["runtime"]["executable"]
    python = sdk_dir / "runtime-env" / "Scripts" / "python.exe"
    home.mkdir(parents=True)
    driver = home / "driver.mjs"
    driver.write_text(DRIVER, encoding="utf-8", newline="\n")
    (home / "driver.patch.yml").write_text(
        "- insert:\n    - id: gtkb-qualification-driver\n      name: " + json.dumps(driver.as_uri()) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    worker = home / "worker.py"
    worker.write_text(WORKER, encoding="utf-8", newline="\n")
    (home / "cases.json").write_text(json.dumps(cases), encoding="utf-8")
    config = {
        "runtime": str(runtime),
        "profile": release["profile"],
        "patches": [str(launcher.write_patch(home)), str(home / "driver.patch.yml")],
        "home": str(home / "dsh-home"),
        "cwd": str(cwd),
    }
    (home / "config.json").write_text(json.dumps(config), encoding="utf-8")
    env = {k: v for k, v in base_env.items() if not k.startswith(("PG", "GT_POSTGRES_"))}
    for key in list(env):
        if any(token in key.upper() for token in ("API_KEY", "TOKEN", "SECRET", "PASSWORD")):
            env.pop(key)
    guard_log = home / "guard-decisions.jsonl"
    env.update(
        PYTHONIOENCODING="utf-8",
        DEEPSEEK_API_KEY="qualification-not-a-real-key",
        DEEPSEEK_BASE_URL="http://127.0.0.1:1",
        GT_AUTHORITY_URL=url,
        GT_PROJECT_ROOT=str(root),
        GTKB_NATIVE_CONTEXT_ID=context,
        GTKB_GUARD_PYTHON=sys.executable,
        GTKB_GUARD_GATE=str(root / "scripts" / "implementation_start_gate.py"),
        GTKB_GUARD_CWD=str(cwd),
        GTKB_GUARD_LOG=str(guard_log),
        GTKB_QUALIFICATION_CASES=str(home / "cases.json"),
        GTKB_QUALIFICATION_OUTPUT=str(home / "output.json"),
    )
    completed = subprocess.run(
        [str(python), str(worker), str(home / "config.json")],
        cwd=cwd,
        env=env,
        capture_output=True,
        timeout=150,
        creationflags=FLAGS,
    )
    assert completed.returncode == 0, completed.stderr.decode(errors="replace")[-3000:]
    output = json.loads((home / "output.json").read_text(encoding="utf-8"))
    assert "error" not in output, output
    decisions = [json.loads(line) for line in guard_log.read_text(encoding="utf-8").splitlines()]
    assert [r["id"] for r in output["results"]] == [c["id"] for c in cases]
    assert len(decisions) == len(cases), decisions
    return output["results"], decisions


def test_installed_runtime_tools_follow_the_live_cli_claim_and_refuse_foreign_effects(bridge, tmp_path):
    sdk_dir = _runtime_dir()
    launcher = _launcher()
    _service, client, contexts, _work_root = bridge
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    for name in ("implementation_start_gate.py",):
        (scripts / name).write_bytes((ROOT / "scripts" / name).read_bytes())
    document = "deepseek-sdk-effects"
    deliver(client, contexts, document, "pb1", 1, "NEW")
    deliver(client, contexts, document, "lo1", 2, "GO")
    reservation = claim(client, document, "pb2", 2, "READY").json()
    opened = client.post(
        f"/v1/bridge/{document}/worktree", json={"native_context_id": "pb2", "fence": reservation["fence"]}
    )
    assert opened.status_code == 200, opened.text
    checkout = tmp_path / ".worktrees" / contexts["pb2"]["session_context_id"]
    before = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    scratch = tmp_path / "scratchpad" / contexts["pb2"]["session_context_id"]
    other_scratch = tmp_path / "scratchpad" / contexts["lo2"]["session_context_id"]
    for folder in (scratch, other_scratch, checkout / "bridge"):
        folder.mkdir(parents=True, exist_ok=True)
    foreign = checkout / "foreign_tracked.txt"
    protected = {path: path.read_bytes() for path in (foreign, tmp_path / "code.py")}
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    url = f"http://127.0.0.1:{port}"

    def edit(case_id, path, old, new, allowed):
        return {
            "id": case_id,
            "tool": "str_replace_editor",
            "arguments": {"command": "str_replace", "path": str(path), "old_str": old, "new_str": new},
            "allowed": allowed,
        }

    def create(case_id, path, allowed):
        return {
            "id": case_id,
            "tool": "str_replace_editor",
            "arguments": {"command": "create", "path": str(path), "file_text": "qualification note"},
            "allowed": allowed,
        }

    def pwsh(case_id, path, content, allowed):
        command = "Set-Content -LiteralPath '" + str(path).replace("'", "''") + "' -Value '" + content + "'"
        return {"id": case_id, "tool": "pwsh", "arguments": {"command": command}, "allowed": allowed}

    launches = [
        (
            "pb2",
            url,
            [
                edit("editor-claimed", checkout / "code.py", "value = 1", "value = 2", True),
                edit("editor-foreign", foreign, "Original unrelated content", "forbidden", False),
                edit("editor-root", tmp_path / "code.py", "value = 1", "forbidden", False),
                create("scratch-own", scratch / "note.md", True),
                create("scratch-foreign", other_scratch / "note.md", False),
                create("bridge-raw", checkout / "bridge/new.md", False),
                pwsh("pwsh-foreign", foreign, "forbidden", False),
                pwsh("pwsh-claimed", checkout / "code.py", "value = 3", True),
            ],
        ),
        ("unknown", url, [edit("editor-unbound", checkout / "code.py", "value = 3", "forbidden", False)]),
        ("lo2", url, [edit("editor-wrong-context", checkout / "code.py", "value = 3", "forbidden", False)]),
        (
            "pb2",
            "http://127.0.0.1:1",
            [edit("editor-authority-unavailable", checkout / "code.py", "value = 3", "x", False)],
        ),
    ]
    process, env = _serve_authority(tmp_path, port)
    try:
        for index, (context, authority, cases) in enumerate(launches):
            results, decisions = _run_cases(
                sdk_dir,
                launcher,
                home=tmp_path / f"launch-{index}",
                cwd=checkout,
                context=context,
                url=authority,
                root=tmp_path,
                cases=cases,
                base_env=env,
            )
            for case, result, decision in zip(cases, results, decisions, strict=True):
                assert decision["allowed"] is case["allowed"], (case["id"], decision)
                assert result["isError"] is not case["allowed"], (case["id"], result)
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=15)
    assert (checkout / "code.py").read_text().strip() == "value = 3"
    assert (scratch / "note.md").read_text() == "qualification note"
    assert not (other_scratch / "note.md").exists()
    assert not (checkout / "bridge/new.md").exists()
    assert all(path.read_bytes() == content for path, content in protected.items())
    assert client.get(f"/v1/bridge/{document}/show?include_content=true").json() == before


def test_a_missing_sdk_module_is_a_typed_startup_failure_with_a_report(tmp_path, monkeypatch):
    """Under an interpreter without the SDK the launcher exits 2 with a content-free report instead of a traceback."""
    launcher = _launcher()
    monkeypatch.setattr(launcher.importlib.util, "find_spec", lambda name: None)
    task = tmp_path / "task.md"
    task.write_text("task", encoding="utf-8")
    report = tmp_path / "report.json"
    code = launcher.main(
        [
            "--root",
            str(tmp_path),
            "--init",
            "::init gtkb lo",
            "--document",
            "doc-1",
            "--version",
            "1",
            "--task-file",
            str(task),
            "--report",
            str(report),
        ]
    )
    assert code == launcher.EXIT_STARTUP_FAILED
    written = json.loads(report.read_text(encoding="utf-8"))
    assert written["exit_code"] == 2 and "runtime-env" in written["error"]


def test_default_invocation_places_the_runtime_home_in_the_bound_contexts_scratch_directory(tmp_path, monkeypatch):
    """Without --home the runtime home is this context's own scratch directory under the root, never `.gtkb-state`
    (a runtime-residue location the native effect gate does not grant and the commit gates never stage)."""
    launcher = _launcher()
    captured: dict[str, object] = {}

    def fake_cli(arguments):
        if arguments[:2] == ["session", "bind"]:
            native = arguments[arguments.index("--native-context-id") + 1]
            return {
                "status": "init_requested",
                "binding": {
                    "session_context_id": "SC-default-home",
                    "role": "loyal-opposition",
                    "native_context_id": native,
                },
            }
        raise AssertionError(arguments)

    def fake_run_session(installation, **kwargs):
        captured.update(kwargs)
        return {"finish_reason": None, "events": 0, "turn": "none"}

    monkeypatch.setattr(launcher.importlib.util, "find_spec", lambda name: object())  # the SDK is importable here
    monkeypatch.setattr(launcher, "verify_installation", lambda source=None: {"executable": tmp_path / "dsh.exe"})
    monkeypatch.setattr(launcher, "cli_runner", lambda root, config, environment: fake_cli)
    monkeypatch.setattr(launcher, "run_session", fake_run_session)
    task = tmp_path / "task.md"
    task.write_text("qualification task", encoding="utf-8")
    report = tmp_path / "report.json"
    code = launcher.main(
        [
            "--root",
            str(tmp_path),
            "--init",
            "::init gtkb lo",
            "--document",
            "doc-1",
            "--version",
            "1",
            "--task-file",
            str(task),
            "--no-prompt",
            "--report",
            str(report),
        ]
    )
    assert code == launcher.EXIT_DELIVERED
    native_context_id = json.loads(report.read_text(encoding="utf-8"))["native_context_id"]
    expected = tmp_path.resolve() / "scratchpad" / "SC-default-home" / "deepseek-sdk" / native_context_id
    assert captured["home"] == expected
    assert captured["home"] == launcher.default_home(tmp_path.resolve(), "SC-default-home", native_context_id)
    assert ".gtkb-state" not in str(captured["home"])
    assert ".gtkb-state" not in (SDK_SOURCE / "harness.py").read_text(encoding="utf-8").replace(
        "such as `.gtkb-state`", ""
    )


SDK_GUARD_HARNESS = r"""
import { pathToFileURL } from 'node:url';
const [modulePath] = process.argv.slice(2);
const guard = await import(pathToFileURL(modulePath).href);
let check;
guard.apply({ tools: { guard: (fn) => { check = fn; } } });
const view = (path) => ({ name: 'str_replace_editor', arguments: { command: 'view', path } });
const results = {
  credentialView: check(view('infrastructure/postgresql/credentials/pg_service.conf')) ?? null,
  passwordFileView: check(view('E:/elsewhere/admin.pgpass')) ?? null,
  envFileView: check(view('.env.local')) ?? null,
  ordinaryView: check(view('README.md')) ?? null,
  exampleView: check(view('.env.example')) ?? null,
  envListing: check({ name: 'pwsh', arguments: { command: 'Get-ChildItem Env:PG*' } }) ?? null,
};
console.log(JSON.stringify(results));
"""


def test_editor_views_reach_the_real_gate_which_refuses_credential_material(tmp_path):
    """c117: the SDK guard sends every editor view to the shared gate as a read; the gate refuses credential material
    before any binding or authority check and allows every other read. Runs the guard module under plain Node with
    the real gate script and this interpreter; no runtime, authority or network is involved."""
    import shutil

    node = shutil.which("node")
    assert node, "the DeepSeek SDK guard requires Node.js on PATH"
    harness = tmp_path / "sdk-guard-harness.mjs"
    harness.write_text(SDK_GUARD_HARNESS, encoding="utf-8")
    log = tmp_path / "guard-decisions.jsonl"
    env = {
        **os.environ,
        "GTKB_GUARD_PYTHON": sys.executable,
        "GTKB_GUARD_GATE": str(ROOT / "scripts" / "implementation_start_gate.py"),
        "GT_PROJECT_ROOT": str(tmp_path),
        "GTKB_GUARD_CWD": str(tmp_path),
        "GTKB_NATIVE_CONTEXT_ID": "deepseek-sdk-guard-view-test",
        "GTKB_GUARD_LOG": str(log),
    }
    done = subprocess.run(
        [node, str(harness), str(SDK_SOURCE / "gtkb_guard.mjs")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=240,
        env=env,
        cwd=tmp_path,
        creationflags=FLAGS,
    )
    assert done.returncode == 0, done.stderr[-2000:]
    results = json.loads(done.stdout.strip().splitlines()[-1])
    for key in ("credentialView", "passwordFileView", "envFileView"):
        assert "credential material" in results[key], (key, results[key])
    assert "environment listing" in results["envListing"]
    assert results["ordinaryView"] is None and results["exampleView"] is None, "every other read passes"
    decisions = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    assert [d["tool"] for d in decisions] == ["str_replace_editor"] * 5 + ["pwsh"], "every view reached the gate"
    assert [d["allowed"] for d in decisions] == [False, False, False, True, True, False]


# c123 (owner decision A6): the sdk-minimal profile mounts the pwsh tool from @deepseek-ai/dsh-tool-pwsh-persistent, whose
# shell keeps its working directory across calls, while the guard reports a fixed cwd; the guard marks that tool's
# payloads "persistent_shell": true, and the gate refuses a change of directory the session keeps.
SDK_GUARD_CASES_HARNESS = r"""
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
const [modulePath, casesPath] = process.argv.slice(2);
const guard = await import(pathToFileURL(modulePath).href);
let check;
guard.apply({ tools: { guard: (fn) => { check = fn; } } });
const cases = JSON.parse(readFileSync(casesPath, 'utf8'));
console.log(JSON.stringify(cases.map((item) => check(item) ?? null)));
"""

RECORDING_GATE = """import json, os, sys
payload = json.load(sys.stdin)
with open(os.environ["GTKB_GUARD_RECORD"], "a", encoding="utf-8") as record:
    record.write(json.dumps(payload) + "\\n")
print("{}")
"""


def _run_guard_cases(tmp_path, gate: Path, cases: list[dict], **extra_env: str) -> list:
    import shutil

    node = shutil.which("node")
    assert node, "the DeepSeek SDK guard requires Node.js on PATH"
    harness = tmp_path / "sdk-guard-cases.mjs"
    harness.write_text(SDK_GUARD_CASES_HARNESS, encoding="utf-8")
    cases_file = tmp_path / "sdk-guard-cases.json"
    cases_file.write_text(json.dumps(cases), encoding="utf-8")
    env = {
        **os.environ,
        "GTKB_GUARD_PYTHON": sys.executable,
        "GTKB_GUARD_GATE": str(gate),
        "GT_PROJECT_ROOT": str(tmp_path),
        "GTKB_GUARD_CWD": str(tmp_path),
        "GTKB_NATIVE_CONTEXT_ID": "deepseek-sdk-guard-persistent-test",
        **extra_env,
    }
    done = subprocess.run(
        [node, str(harness), str(SDK_SOURCE / "gtkb_guard.mjs"), str(cases_file)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=240,
        env=env,
        cwd=tmp_path,
        creationflags=FLAGS,
    )
    assert done.returncode == 0, done.stderr[-2000:]
    return json.loads(done.stdout.strip().splitlines()[-1])


def test_the_guard_marks_only_the_persistent_pwsh_tools_payloads(tmp_path):
    """The pwsh tool's payload carries "persistent_shell": true; the editor's payloads do not (c123, A6). A recording
    gate stands in for the shared gate; no runtime, authority or network is involved."""
    gate = tmp_path / "recording_gate.py"
    gate.write_text(RECORDING_GATE, encoding="utf-8")
    record = tmp_path / "payloads.jsonl"
    cases = [
        {"name": "pwsh", "arguments": {"command": "Get-Location"}},
        {"name": "str_replace_editor", "arguments": {"command": "view", "path": "README.md"}},
        {"name": "str_replace_editor", "arguments": {"command": "create", "path": "note.md", "file_text": "x"}},
    ]

    assert _run_guard_cases(tmp_path, gate, cases, GTKB_GUARD_RECORD=str(record)) == [None, None, None]

    payloads = [json.loads(line) for line in record.read_text(encoding="utf-8").splitlines()]
    assert [payload["tool_name"] for payload in payloads] == ["Bash", "Read", "Write"]
    assert payloads[0]["persistent_shell"] is True
    assert all("persistent_shell" not in payload for payload in payloads[1:])


def test_the_real_gate_refuses_a_change_of_directory_from_the_persistent_pwsh_tool(tmp_path):
    """The shared gate refuses the marked payload's Set-Location before any binding or authority check, and allows a
    change of directory handed to a child shell and an ordinary read (c123, A6)."""
    cases = [
        {"name": "pwsh", "arguments": {"command": "Set-Location sub"}},
        {"name": "pwsh", "arguments": {"command": 'pwsh -NoProfile -Command "Set-Location sub; Get-Location"'}},
        {"name": "pwsh", "arguments": {"command": "Get-Location"}},
    ]

    results = _run_guard_cases(tmp_path, ROOT / "scripts" / "implementation_start_gate.py", cases)

    assert results[0].startswith("persistent_shell_directory_change: "), results
    assert "-LiteralPath" in results[0]
    assert results[1:] == [None, None]
