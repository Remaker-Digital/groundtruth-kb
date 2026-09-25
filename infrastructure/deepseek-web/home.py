"""GT-KB Home service: start, stop, inspect and open the DeepSeek Harness Web UI as GT-KB's Home (owner rulings D54, D58, D59).

The Home server is the pinned DeepSeek Harness Web UI (install.py) on 127.0.0.1 only, composed from the pinned profile
manifest (release.json) and GT-KB's one committed configuration file, gtkb-home.patch.yml: the OpenRouter preset route,
the GT-KB Home effect guard, the GT-KB Home plugin (branding, attribution, controls) and the disabled upstream brand.

start  verifies the installation, writes the profile manifest into the Home state folder, proves the composed
       configuration contains every GT-KB row (--dump-config), starts the server detached with a minimal environment,
       and waits for the guard's and the plugin's activation lines and the ready line; otherwise it stops what it
       started and fails. The OpenRouter credential is loaded by name through GT-KB's .env.local loader and placed only
       in the server's environment. The sign-in line goes to a user-private URL file, never to the log.
stop   asks the server to run its own teardown through the plugin's loopback control route (per-start secret), then
       ends the positively identified process tree if it has not exited.
status reports the run record, process identity, liveness and whether a model credential was supplied.
url    prints the sign-in URL (the launch token is single-server and loopback-only).

Home state (sessions, the browser-cookie secret, run records) lives in a user-private folder outside the repository:
%LOCALAPPDATA%/GT-KB/home by default, or --state / GTKB_HOME_STATE. Each start and stop outcome is also appended to
logs/home-launcher.log there, because the logon task runs this script under pythonw.exe, whose output reaches nobody.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import secrets
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parents[1]
PROFILE = "gtkb"
PORT = 3080
READY_TIMEOUT_SECONDS = 90
STOP_TIMEOUT_SECONDS = 10
ACTIVATION_LINES = ("gtkb-home-effect-guard active", "gtkb-home active")
REQUIRED_ROWS = ("gtkb-home-effect-guard", "gtkb-home", "llm-pi-ai", "agent-default-model")
DISABLED_ROWS = ("ui-brand-official", "llm-deepseek")
CREDENTIAL_NAME = "GTKB_OPENROUTER_API_KEY"
ENV_ALLOWLIST = (
    "SYSTEMROOT",
    "WINDIR",
    "TEMP",
    "TMP",
    "USERPROFILE",
    "APPDATA",
    "LOCALAPPDATA",
    "PROGRAMDATA",
    "COMSPEC",
    "PATHEXT",
    "HOMEDRIVE",
    "HOMEPATH",
    "USERNAME",
    "COMPUTERNAME",
    "NUMBER_OF_PROCESSORS",
    "PROCESSOR_ARCHITECTURE",
    "OS",
    "PATH",
)


class HomeError(RuntimeError):
    pass


def state_folder(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    configured = os.environ.get("GTKB_HOME_STATE")
    if configured:
        return Path(configured)
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    return Path(base) / "GT-KB" / "home"


def launcher_script() -> Path:
    return SOURCE / "node_modules" / "@deepseek-ai" / "dsh" / "lib" / "bin.js"


def node_executable() -> str:
    from shutil import which

    found = which("node")
    if not found:
        raise HomeError("Node.js is not on PATH")
    return found


def verify_installation() -> dict:
    release = json.loads((SOURCE / "release.json").read_text(encoding="utf-8"))
    installed_path = SOURCE / "installed.json"
    if not installed_path.is_file() or not launcher_script().is_file():
        raise HomeError("The Home server is not installed; run infrastructure/deepseek-web/install.py")
    installed = json.loads(installed_path.read_text(encoding="utf-8"))
    if installed.get("lockfile_sha256") != release["lockfile_sha256"] or installed.get("version") != release["version"]:
        raise HomeError("The installed Home server differs from the pinned release; reinstall it")
    return release


def write_profile_manifest(state: Path, release: dict) -> Path:
    """GT-KB owns this profile: its manifest is always the pinned one (patchReload 'startup', the 0.1.2-rc.1 workaround)."""
    folder = state / "profiles" / PROFILE
    folder.mkdir(parents=True, exist_ok=True)
    manifest = folder / "package.json"
    content = (
        json.dumps(
            {
                "name": f"dsh-profile-{PROFILE}",
                "private": True,
                "dependencies": {},
                "dsh": {"profile": release["profile_manifest"]},
            },
            indent=2,
        )
        + "\n"
    )
    if not manifest.is_file() or manifest.read_text(encoding="utf-8") != content:
        manifest.write_text(content, encoding="utf-8")
    return manifest


def credential() -> dict[str, str]:
    value = os.environ.get(CREDENTIAL_NAME, "")
    if not value:
        spec = importlib.util.spec_from_file_location("gtkb_env_loader", ROOT / "scripts" / "_env.py")
        if spec is not None and spec.loader is not None:
            loader = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(loader)
            value = loader.load_env_local(check_only=True).get(CREDENTIAL_NAME, "")
    return {CREDENTIAL_NAME: value} if value else {}


def base_environment(state: Path) -> dict[str, str]:
    env = {name: os.environ[name] for name in ENV_ALLOWLIST if name in os.environ}
    env.update(
        DSH_HOME=str(state),
        GTKB_HOME_STATE=str(state),  # `gt services status` run from the Home page reads this same Home
        DSH_TELEMETRY_DISABLED="1",
        DSH_PERMISSION_MODE="workspace-write",
        GTKB_GUARD_PYTHON=str(ROOT / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"),
        GTKB_GUARD_GATE=str(ROOT / "scripts" / "implementation_start_gate.py"),
        GT_PROJECT_ROOT=str(ROOT),
        GTKB_HOME_ROOT=str(ROOT),
    )
    return env


def server_command(node: str, port: int = PORT) -> list[str]:
    return [
        node,
        str(launcher_script()),
        "--profile",
        PROFILE,
        "--patch",
        str(SOURCE / "gtkb-home.patch.yml"),
        "--no-open",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
    ]


def prove_composition(node: str, env: dict[str, str]) -> None:
    """Refuse unless the composed configuration contains every GT-KB row and the upstream brand and provider are off."""
    dump = subprocess.run(
        [*server_command(node)[:6], "--dump-config"],
        env=env,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    if dump.returncode != 0:
        raise HomeError(f"The Home configuration does not compose: {dump.stderr.strip()[-1500:]}")
    rows = set(re.findall(r"^- id: (\S+)", dump.stdout, re.MULTILINE))
    missing = [row for row in REQUIRED_ROWS if row not in rows]
    if missing:
        raise HomeError(f"The composed Home configuration lacks required rows: {missing}")
    for row in DISABLED_ROWS:
        found = re.search(rf"^- id: {re.escape(row)}\n((?:  .*\n)*)", dump.stdout, re.MULTILINE)
        if found is None or not re.search(r"^  disabled: true$", found.group(1), re.MULTILINE):
            raise HomeError(f"The upstream row {row} is not disabled in the composed Home configuration")


def run_record_path(state: Path) -> Path:
    return state / "run" / "home-run.json"


def process_identity(pid: int) -> dict | None:
    probe = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            f"$p = Get-CimInstance Win32_Process -Filter 'ProcessId={int(pid)}'; if ($p) {{ @{{exe=$p.ExecutablePath; "
            f"cmd=$p.CommandLine; created=$p.CreationDate.ToUniversalTime().ToString('o')}} | ConvertTo-Json -Compress }}",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    text = probe.stdout.strip()
    return json.loads(text) if text else None


def ours(record: dict) -> bool:
    identity = process_identity(record["pid"])
    return (
        bool(identity)
        and identity.get("created") == record["created"]
        and "--profile" in (identity.get("cmd") or "")
        and str(launcher_script()) in (identity.get("cmd") or "")
        and (identity.get("exe") or "").lower().endswith("node.exe")
    )


def start(state: Path, port: int = PORT) -> dict:
    record_path = run_record_path(state)
    if record_path.is_file():
        record = json.loads(record_path.read_text(encoding="utf-8"))
        if ours(record):
            return {"started": False, "already_running": True, "pid": record["pid"]}
    release = verify_installation()
    write_profile_manifest(state, release)
    node = node_executable()
    env = base_environment(state)
    prove_composition(node, env)
    supplied = credential()
    credential_supplied = bool(supplied)
    control = secrets.token_urlsafe(32)
    run_dir = state / "run"
    logs = state / "logs"
    run_dir.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    url_file = run_dir / "home-url.txt"
    log_file = logs / f"home-{datetime.now().strftime('%Y%m%dT%H%M%S')}.log"
    url_file.unlink(missing_ok=True)
    flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
    with url_file.open("wb") as stdout, log_file.open("wb") as stderr:
        process = subprocess.Popen(
            server_command(node, port),
            cwd=ROOT,
            env={**env, **supplied, "GTKB_HOME_CONTROL_SECRET": control},
            stdout=stdout,
            stderr=stderr,
            stdin=subprocess.DEVNULL,
            creationflags=flags,
        )
    del supplied
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS
    ready = False
    while time.monotonic() < deadline:
        time.sleep(1)
        lines = log_file.read_text(encoding="utf-8", errors="replace")
        url = re.search(
            r"http://127\.0\.0\.1:\d+/\?token=[A-Za-z0-9_-]+", url_file.read_text(encoding="utf-8", errors="replace")
        )
        if url and all(line in lines for line in ACTIVATION_LINES):
            ready = True
            break
        if process.poll() is not None:
            break
    identity = process_identity(process.pid)
    if not ready or identity is None:
        if process.poll() is None:
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
        tail = log_file.read_text(encoding="utf-8", errors="replace")[-1500:]
        raise HomeError(f"The Home server did not prove readiness (guard, plugin and ready line): {tail}")
    record = {
        "pid": process.pid,
        "created": identity["created"],
        "started_at": datetime.now(UTC).isoformat(),
        "port": port,
        "control": control,
        "url_file": str(url_file),
        "log_file": str(log_file),
        "credential_supplied": credential_supplied,
    }
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return {"started": True, "pid": process.pid, "log": str(log_file), "credential_supplied": credential_supplied}


def stop(state: Path) -> dict:
    record_path = run_record_path(state)
    if not record_path.is_file():
        return {"stopped": False, "reason": "no run record"}
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if not ours(record):
        record_path.unlink(missing_ok=True)
        return {"stopped": False, "reason": "the recorded process is not running"}
    graceful = False
    request = urllib.request.Request(
        f"http://127.0.0.1:{record['port']}/gtkb-home/control/shutdown",
        method="POST",
        headers={"x-gtkb-control": record["control"]},
        data=b"",
    )
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request, timeout=5) as response:
            graceful = response.status == 202
    except (urllib.error.URLError, OSError):
        graceful = False
    deadline = time.monotonic() + STOP_TIMEOUT_SECONDS
    while graceful and time.monotonic() < deadline and process_identity(record["pid"]) is not None:
        time.sleep(0.5)
    forced = False
    if ours(record):
        subprocess.run(["taskkill", "/PID", str(record["pid"]), "/T", "/F"], capture_output=True)
        forced = True
    record_path.unlink(missing_ok=True)
    return {"stopped": True, "graceful": graceful and not forced, "forced": forced, "pid": record["pid"]}


def status(state: Path) -> dict:
    record_path = run_record_path(state)
    if not record_path.is_file():
        return {"running": False}
    record = json.loads(record_path.read_text(encoding="utf-8"))
    running = ours(record)
    live = False
    if running:
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(f"http://127.0.0.1:{record['port']}/favicon.svg", timeout=5) as response:
                live = response.status == 200
        except (urllib.error.URLError, OSError):
            live = False
    return {
        "running": running,
        "live": live,
        "pid": record["pid"],
        "port": record["port"],
        "started_at": record["started_at"],
        "credential_supplied": record.get("credential_supplied"),
        "log": record["log_file"],
    }


def url(state: Path) -> str:
    record_path = run_record_path(state)
    if not record_path.is_file():
        raise HomeError("The Home server is not running; start it with: gt home start")
    record = json.loads(record_path.read_text(encoding="utf-8"))
    found = re.search(
        r"http://127\.0\.0\.1:\d+/\?token=[A-Za-z0-9_-]+", Path(record["url_file"]).read_text(encoding="utf-8")
    )
    if found is None or not ours(record):
        raise HomeError("The Home server is not running; start it with: gt home start")
    return found.group(0)


def launcher_log(state: Path, entry: dict) -> None:
    """Append a start or stop outcome: under the logon task's pythonw.exe, printed output reaches nobody."""
    try:
        logs = state / "logs"
        logs.mkdir(parents=True, exist_ok=True)
        with (logs / "home-launcher.log").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"at": datetime.now(UTC).isoformat(), **entry}) + "\n")
    except OSError:
        pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", choices=("start", "stop", "status", "url"))
    parser.add_argument(
        "--state", type=Path, default=None, help="Home state folder (default %%LOCALAPPDATA%%/GT-KB/home)"
    )
    parser.add_argument("--port", type=int, default=PORT, help="Loopback port for start (default %(default)s)")
    args = parser.parse_args(argv)
    state = state_folder(args.state)
    try:
        if args.action == "url":
            print(url(state))
            return 0
        result = (
            start(state, args.port) if args.action == "start" else {"stop": stop, "status": status}[args.action](state)
        )
    except (HomeError, OSError, subprocess.SubprocessError, json.JSONDecodeError, KeyError) as error:
        outcome = {"action": args.action, "ok": False, "error": str(error)}
        if args.action in ("start", "stop"):
            launcher_log(state, outcome)
        print(json.dumps(outcome))
        return 1
    outcome = {"action": args.action, "ok": True, **result}
    if args.action in ("start", "stop"):
        launcher_log(state, outcome)
    print(json.dumps(outcome, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
