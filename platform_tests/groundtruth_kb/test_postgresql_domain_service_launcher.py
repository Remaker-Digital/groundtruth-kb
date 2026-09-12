"""The unattended domain-service launcher composes the service command with the credential environment confined to
that process, drops every inherited override that could redirect the database connection, contains the service tree
in a kill-on-close job before the service can execute (no job: nothing is started; the service is created suspended,
placed in the job, then resumed; a service that cannot be contained is ended while still suspended, leaving no
descendant), and never prints credential values. The PowerShell readiness probe treats failed probes as expected and
never aborts its loop, in Windows PowerShell 5.1 as in PowerShell 7. Test cleanup ends only a listener proven to be
this test's own service and leaves a foreign listener alone. The composition, refusal, containment, descendant,
foreign-listener and probe-timeout tests run everywhere; the launch-to-readiness and delayed-readiness tests start
the service through the launcher against the disposable PostgreSQL installation (GTKB_RUN_POSTGRES_INTEGRATION=1)
with a deliberately polluted parent environment. Scheduled startup itself is established at registration on the
owner's workstation, not here."""

from __future__ import annotations

import configparser
import ctypes
import importlib.util
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

import pytest

ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = ROOT / "infrastructure" / "postgresql" / "domain_service_launcher.py"
READINESS = ROOT / "infrastructure" / "postgresql" / "domain-service-readiness.ps1"
SHELLS = [shell for shell in (shutil.which("powershell.exe"), shutil.which("pwsh")) if shell]
WINDOWS_ONLY = pytest.mark.skipif(os.name != "nt", reason="job containment is a Windows mechanism")

# A stand-in service that, once it runs, records that it ran and starts a real descendant.
SPAWNER = (
    "import pathlib, subprocess, sys, time\n"
    "marker, record = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])\n"
    "marker.write_text('ran', encoding='utf-8')\n"
    "grandchild = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(300)'])\n"
    "record.write_text(str(grandchild.pid), encoding='utf-8')\n"
    "time.sleep(300)\n"
)


def _load():
    spec = importlib.util.spec_from_file_location("domain_service_launcher", LAUNCHER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _operator_config(root: Path, service: str) -> Path:
    config = root / "infrastructure" / "postgresql" / "operator-config.toml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(
        f'[groundtruth]\nproject_root = "{root.as_posix()}"\n\n[postgresql]\nservice = "{service}"\n', encoding="utf-8"
    )
    return config


def _free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def _port_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.5):
            return True
    except OSError:
        return False


def _wait_port_closed(port: int, seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if not _port_open(port):
            return True
        time.sleep(0.5)
    return not _port_open(port)


def _powershell(command: str) -> str:
    return subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    ).stdout


def _listener_owner(port: int) -> tuple[int | None, str]:
    """Return (pid, command line) of the process listening on the loopback port, re-identified through the OS."""
    if os.name != "nt":
        return None, ""
    text = _powershell(
        f"$c = Get-NetTCPConnection -State Listen -LocalPort {port} -LocalAddress 127.0.0.1 "
        "-ErrorAction SilentlyContinue | Select-Object -First 1; if ($c) { "
        '$p = Get-CimInstance Win32_Process -Filter "ProcessId = $($c.OwningProcess)"; '
        "[pscustomobject]@{pid=$c.OwningProcess; cmd=$p.CommandLine} | ConvertTo-Json -Compress }"
    ).strip()
    if not text:
        return None, ""
    data = json.loads(text.splitlines()[-1])
    return int(data["pid"]), str(data.get("cmd") or "")


def _end_own_listener(port: int, operator_config: Path) -> str:
    """Safety net only: end the listener on the port if, and only if, its command line proves it is this test's
    service (it names this test's operator config, which lives under the test's own temporary root)."""
    pid, command = _listener_owner(port)
    if pid is None:
        return "no listener"
    if "service serve" not in command or str(operator_config) not in command:
        return f"listener {pid} is not this test's service; left alone"
    subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True, timeout=60)
    return f"ended {pid}"


def _children_of(pid: int) -> list[int]:
    """Processes whose parent is the given process, re-identified through the OS."""
    out = _powershell(
        f"Get-CimInstance Win32_Process -Filter 'ParentProcessId = {pid}' | ForEach-Object {{ $_.ProcessId }}"
    )
    return [int(token) for token in out.split()]


def _process_handle(pid: int, access: int) -> int | None:
    handle = ctypes.windll.kernel32.OpenProcess(access, False, pid)
    return int(handle) if handle else None


def _in_job(pid: int, job: int) -> bool:
    handle = _process_handle(pid, 0x1000)  # PROCESS_QUERY_LIMITED_INFORMATION
    assert handle, f"process {pid} cannot be opened"
    result = ctypes.c_int(0)
    try:
        assert ctypes.windll.kernel32.IsProcessInJob(handle, job, ctypes.byref(result))
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)
    return bool(result.value)


def _wait_pid_gone(pid: int, seconds: float) -> bool:
    handle = _process_handle(pid, 0x00100000)  # SYNCHRONIZE
    if handle is None:
        return True
    try:
        return ctypes.windll.kernel32.WaitForSingleObject(handle, int(seconds * 1000)) == 0
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)


def _wait_for(path: Path, seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if path.exists() and path.read_text(encoding="utf-8").strip():
            return True
        time.sleep(0.2)
    return False


def _spawner(tmp_path: Path) -> tuple[list[str], Path, Path]:
    marker, record = tmp_path / "ran.txt", tmp_path / "grandchild-pid.txt"
    return [sys.executable, "-c", SPAWNER, str(marker), str(record)], marker, record


def test_build_confines_the_credential_environment_to_the_service_process(tmp_path, monkeypatch):
    module = _load()
    monkeypatch.setenv("PGPASSWORD", "must-not-leak")
    monkeypatch.setenv("PGSERVICEFILE", "E:/elsewhere/pg_service.conf")
    monkeypatch.setenv("GT_AUTHORITY_URL", "http://127.0.0.1:1")
    monkeypatch.setenv("UNRELATED", "kept")
    argv, environment, log = module.build(tmp_path, 8765, None)
    assert argv[1:] == [
        "-m",
        "groundtruth_kb",
        "--config",
        str(tmp_path / "infrastructure/postgresql/operator-config.toml"),
        "service",
        "serve",
        "--port",
        "8765",
    ]
    assert environment["PGSERVICEFILE"] == str(tmp_path / "infrastructure/postgresql/credentials/pg_service.conf")
    assert "PGPASSWORD" not in environment
    assert "GT_AUTHORITY_URL" not in environment
    assert environment["UNRELATED"] == "kept"
    assert environment["GT_PROJECT_ROOT"] == str(tmp_path)
    assert log == tmp_path / "infrastructure/postgresql/logs/domain-service.log"


def test_inherited_postgres_overrides_cannot_redirect_the_operator_config_service(tmp_path, monkeypatch):
    """The configuration loader maps GT_POSTGRES_* onto the [postgresql] section; the launcher drops them all."""
    from groundtruth_kb.config import GTConfig

    module = _load()
    operator = _operator_config(tmp_path, "gtkb_authority")
    monkeypatch.setenv("GT_POSTGRES_SERVICE", "redirected_elsewhere")
    monkeypatch.setenv("GT_POSTGRES_CONNECT_TIMEOUT_SECONDS", "1")
    monkeypatch.setenv("GT_POSTGRES_LOCK_TIMEOUT_MS", "1")
    monkeypatch.setenv("GT_POSTGRES_STATEMENT_TIMEOUT_MS", "1")
    # Without the launcher the parent's override wins: this is the redirection the launcher must prevent.
    assert GTConfig.load(operator, discover=False).postgresql.service == "redirected_elsewhere"
    _argv, environment, _log = module.build(tmp_path, 8765, operator)
    assert not [key for key in environment if key.startswith("GT_POSTGRES_")]
    with pytest.MonkeyPatch.context() as service_process:
        for key in list(os.environ):
            if key.startswith(("GT_", "PG")):
                service_process.delenv(key, raising=False)
        for key, value in environment.items():
            service_process.setenv(key, value)
        selected = GTConfig.load(operator, discover=False).postgresql
    assert selected.service == "gtkb_authority"
    assert (selected.connect_timeout_seconds, selected.lock_timeout_ms, selected.statement_timeout_ms) == (
        10,
        5000,
        30000,
    )


def test_build_accepts_an_explicit_operator_config_and_port(tmp_path):
    module = _load()
    config = tmp_path / "operator.toml"
    argv, _environment, _log = module.build(tmp_path, 9001, config)
    assert argv[3:5] == ["--config", str(config)]
    assert argv[-2:] == ["--port", "9001"]


def test_print_command_shows_no_credential_values(tmp_path, monkeypatch):
    monkeypatch.setenv("PGPASSWORD", "must-not-leak")
    completed = subprocess.run(
        [sys.executable, str(LAUNCHER), "--root", str(tmp_path), "--print-command"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    assert "must-not-leak" not in completed.stdout + completed.stderr
    assert "service serve --port 8765" in completed.stdout
    assert "PGSERVICEFILE" in completed.stdout  # the key is named, the value is not


def test_missing_credential_file_refuses_before_starting_anything(tmp_path):
    completed = subprocess.run(
        [sys.executable, str(LAUNCHER), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    assert completed.returncode == 2
    assert "credential file missing" in completed.stderr
    assert not (tmp_path / "infrastructure/postgresql/logs/domain-service.log").exists()


@WINDOWS_ONLY
def test_no_job_object_refuses_before_anything_is_started(tmp_path):
    """When no kill-on-close job can be created the launcher exits 3 without attempting to start the service: the
    argv names an executable that does not exist, so any start attempt would have raised."""
    module = _load()
    log = tmp_path / "logs" / "domain-service.log"
    assignments: list[object] = []
    code = module.serve(
        ["no-such-domain-service-executable-" + uuid4().hex],
        dict(os.environ),
        log,
        1,
        job_factory=lambda: None,
        assign=lambda job, process: assignments.append(process) or True,
    )
    assert code == module.EXIT_UNCONTAINED == 3
    assert not assignments
    text = log.read_text(encoding="utf-8")
    assert "refused: job object unavailable; nothing started" in text
    assert "contained by a kill-on-close job" not in text


@WINDOWS_ONLY
@pytest.mark.parametrize("failure", ["assignment_refused", "resume_failed"])
def test_uncontainable_service_is_ended_before_it_can_run_or_spawn_a_descendant(tmp_path, failure):
    """The service is created suspended; if it cannot be placed in the job or resumed it is ended while still
    suspended. The stand-in service would record that it ran and start a real descendant; neither happens."""
    module = _load()
    log = tmp_path / "logs" / "domain-service.log"
    argv, marker, record = _spawner(tmp_path)
    started: list[subprocess.Popen] = []

    def assign(job, process):
        started.append(process)
        return failure != "assignment_refused" and module._assign(job, process)

    resume = (lambda process: False) if failure == "resume_failed" else module._resume
    code = module.serve(argv, dict(os.environ), log, 1, assign=assign, resume=resume)
    assert code == module.EXIT_UNCONTAINED == 3
    assert started and started[0].poll() is not None, "the uncontainable service must be ended"
    assert not marker.exists(), "the service ran before containment was established"
    assert not record.exists(), "the service started a descendant"
    assert _children_of(started[0].pid) == []
    text = log.read_text(encoding="utf-8")
    assert "ended before it ran" in text
    assert "contained by a kill-on-close job" not in text


@WINDOWS_ONLY
def test_contained_service_and_its_real_descendant_end_when_the_job_closes(tmp_path):
    """Containment precedes execution: the service's own descendant is born inside the job, and closing the job's
    last handle (what the launcher's exit does) ends both the service and the descendant."""
    module = _load()
    argv, marker, record = _spawner(tmp_path)
    job = module._kill_on_close_job()
    assert job
    process = module._start_contained(argv, dict(os.environ), job, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    grandchild = None
    try:
        assert _wait_for(record, 30), "the contained service did not run or did not start its descendant"
        assert marker.exists()
        grandchild = int(record.read_text(encoding="utf-8"))
        assert process.poll() is None and _wait_pid_gone(grandchild, 0) is False
        assert _in_job(process.pid, job) and _in_job(grandchild, job), "the descendant was born outside the job"
        ctypes.windll.kernel32.CloseHandle(job)
        job = None
        assert process.wait(timeout=15) is not None
        assert _wait_pid_gone(grandchild, 15), "the descendant survived the job"
    finally:
        module._end(process)
        if grandchild is not None and not _wait_pid_gone(grandchild, 0):
            subprocess.run(["taskkill", "/F", "/PID", str(grandchild)], capture_output=True, timeout=60)
        if job:
            ctypes.windll.kernel32.CloseHandle(job)


@pytest.mark.skipif(os.name != "nt", reason="the safety net re-identifies listeners through Windows")
def test_cleanup_safety_net_leaves_a_foreign_listener_alone(tmp_path):
    """The safety net ends a listener only when its command line proves it is this test's service."""
    foreign = subprocess.Popen(
        [
            sys.executable,
            "-c",
            "import socket, sys, time\n"
            "s = socket.socket(); s.bind(('127.0.0.1', 0)); s.listen()\n"
            "print(s.getsockname()[1], flush=True)\n"
            "time.sleep(120)\n",
        ],
        stdout=subprocess.PIPE,
        text=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    try:
        port = int(foreign.stdout.readline().strip())
        assert _port_open(port)
        verdict = _end_own_listener(port, _operator_config(tmp_path, "gtkb_authority"))
        assert "left alone" in verdict, verdict
        assert foreign.poll() is None, "a foreign listener must never be ended by the safety net"
        assert _port_open(port)
    finally:
        if foreign.poll() is None:
            foreign.kill()
            foreign.wait(timeout=15)


def _probe_command(python: str, operator: Path, port: int, seconds: int, interval: int) -> str:
    # $ErrorActionPreference = 'Stop' reproduces the caller's setting under which a redirected native stderr raised
    # NativeCommandError in Windows PowerShell 5.1 and aborted the loop on its first failed probe.
    return (
        "$ErrorActionPreference = 'Stop'; "
        f". '{READINESS}'; "
        f"$r = Wait-GtkbDomainServiceReady -ProbeInterpreter '{python}' -OperatorConfig '{operator}' "
        f"-Port {port} -Seconds {seconds} -IntervalSeconds {interval}; "
        "[pscustomobject]@{ready=$r.Ready; attempts=$r.Attempts; last=$r.LastOutput} | ConvertTo-Json -Compress"
    )


def _shell_argv(shell: str, command: str) -> list[str]:
    return [shell, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", command]


def _probe_env() -> dict[str, str]:
    import groundtruth_kb

    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(groundtruth_kb.__file__).resolve().parent.parent)
    env["PYTHONIOENCODING"] = "utf-8"
    return env


@pytest.mark.skipif(not SHELLS, reason="no PowerShell available")
@pytest.mark.parametrize("shell", SHELLS, ids=[Path(shell).stem for shell in SHELLS])
def test_readiness_probe_times_out_without_aborting_the_loop(shell, tmp_path):
    operator = _operator_config(tmp_path, "gtkb_authority")
    port = _free_port()
    completed = subprocess.run(
        _shell_argv(shell, _probe_command(sys.executable, operator, port, 5, 1)),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        env=_probe_env(),
    )
    # The loop must run to its deadline: a terminating NativeCommandError would end the shell with a non-zero exit
    # code, an error on stderr and no JSON result line.
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "NativeCommandError" not in completed.stderr
    result = json.loads(completed.stdout.strip().splitlines()[-1])
    assert result["ready"] is False
    assert "NativeCommandError" not in result["last"], result  # captured native stderr is kept as message text only
    assert result["attempts"] >= 2, result
    assert "No authority_url" not in result["last"], result  # the probe supplies the loopback endpoint itself


class _Prepared:
    def __init__(self, tmp_path: Path, monkeypatch) -> None:
        if os.environ.get("GTKB_RUN_POSTGRES_INTEGRATION") != "1":
            pytest.fail("Explicitly select a disposable PostgreSQL installation")
        self.source_service = os.environ.get("GTKB_TEST_POSTGRES_SERVICE")
        source_file = os.environ.get("PGSERVICEFILE")
        if not self.source_service or not source_file:
            pytest.fail("GTKB_TEST_POSTGRES_SERVICE and PGSERVICEFILE are required")
        import psycopg
        from groundtruth_kb.config import PostgreSQLConfig
        from groundtruth_kb.postgres_kernel import PostgresKernel
        from psycopg import sql

        self.psycopg, self.sql = psycopg, sql
        self.schema = f"gtkb_test_{uuid4().hex}"
        with psycopg.connect(service=self.source_service, autocommit=True) as connection:
            connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema)))
        monkeypatch.setenv("PGOPTIONS", f"-c search_path={self.schema}")
        PostgresKernel(PostgreSQLConfig(service=self.source_service)).initialize()
        monkeypatch.delenv("PGOPTIONS")
        # A credential file of the launcher's own: the disposable service entry, renamed, selecting the test schema.
        parser = configparser.ConfigParser(interpolation=None)
        parser.optionxform = str
        parser.read(source_file, encoding="utf-8")
        self.entry = dict(parser[self.source_service])
        self.entry["options"] = f"-c search_path={self.schema}"
        credentials = tmp_path / "infrastructure" / "postgresql" / "credentials" / "pg_service.conf"
        credentials.parent.mkdir(parents=True)
        credentials.write_text(
            "[gtkb_authority_test]\n" + "".join(f"{k}={v}\n" for k, v in self.entry.items()), encoding="utf-8"
        )
        self.operator = _operator_config(tmp_path, "gtkb_authority_test")
        self.port = _free_port()
        self.root = tmp_path
        self.log = tmp_path / "infrastructure" / "postgresql" / "logs" / "domain-service.log"
        self.source_file = source_file
        self.process: subprocess.Popen | None = None

    def launch(self) -> subprocess.Popen:
        polluted = _probe_env()
        polluted.pop("PGOPTIONS", None)
        polluted.update(
            GT_POSTGRES_SERVICE="no_such_service_entry",  # would break the start if the launcher let it through
            GT_AUTHORITY_URL="http://127.0.0.1:1",
            PGSERVICEFILE=self.source_file,
        )
        self.process = subprocess.Popen(
            [
                sys.executable,
                str(LAUNCHER),
                "--root",
                str(self.root),
                "--port",
                str(self.port),
                "--config",
                str(self.operator),
            ],
            cwd=self.root,
            env=polluted,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return self.process

    def await_status(self) -> dict:
        from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError

        assert self.process is not None
        client = AuthorityClient(f"http://127.0.0.1:{self.port}", timeout=2)
        deadline = time.monotonic() + 60
        while True:
            try:
                return client.request("GET", "/v1/status")
            except AuthorityClientError:
                if self.process.poll() is not None or time.monotonic() > deadline:
                    _out, err = self.process.communicate(timeout=10)
                    pytest.fail(
                        f"launcher exited or timed out: {self.process.returncode} {err.decode('utf-8', 'replace')[-800:]}"
                    )
                time.sleep(0.5)

    def finish(self) -> None:
        """End the launcher only; the job object must take the service tree with it. Then drop the schema."""
        listener_gone = True
        safety = ""
        try:
            if self.process is not None:
                if self.process.poll() is None:
                    self.process.terminate()
                try:
                    self.process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=15)
                listener_gone = _wait_port_closed(self.port, 20)
                if not listener_gone:
                    safety = _end_own_listener(self.port, self.operator)  # ends only a listener proven to be ours
                    _wait_port_closed(self.port, 20)
        finally:
            with self.psycopg.connect(service=self.source_service, autocommit=True) as connection:
                connection.execute(self.sql.SQL("DROP SCHEMA {} CASCADE").format(self.sql.Identifier(self.schema)))
        assert listener_gone, f"the listener on 127.0.0.1:{self.port} survived the launcher ({safety})"
        assert not _port_open(self.port)


@pytest.mark.integration
@pytest.mark.timeout(240)
def test_launcher_starts_the_service_to_readiness_and_ends_its_tree_with_the_launcher(tmp_path, monkeypatch):
    """Start the service through the launcher against the disposable installation, read its status back, then end
    the launcher alone and require the listener to disappear with it."""
    prepared = _Prepared(tmp_path, monkeypatch)
    try:
        prepared.launch()
        status = prepared.await_status()
        assert status, status
        text = prepared.log.read_text(encoding="utf-8")
        assert "starting domain service on 127.0.0.1:" in text
        if os.name == "nt":
            assert "contained by a kill-on-close job before it ran" in text
        secret = prepared.entry.get("password")
        if secret:
            assert secret not in text
    finally:
        prepared.finish()


@pytest.mark.integration
@pytest.mark.timeout(240)
@pytest.mark.skipif(not SHELLS, reason="no PowerShell available")
@pytest.mark.parametrize("shell", SHELLS, ids=[Path(shell).stem for shell in SHELLS])
def test_readiness_probe_waits_through_delayed_readiness(shell, tmp_path, monkeypatch):
    """The probe starts before the service exists, sees refused probes, and reports ready once the service answers."""
    prepared = _Prepared(tmp_path, monkeypatch)
    probe = None
    try:
        probe = subprocess.Popen(
            _shell_argv(shell, _probe_command(sys.executable, prepared.operator, prepared.port, 90, 1)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            env=_probe_env(),
        )
        time.sleep(3)  # at least two refused probes before the service exists
        prepared.launch()
        out, err = probe.communicate(timeout=150)
        assert probe.returncode == 0, out + err
        assert "NativeCommandError" not in err
        result = json.loads(out.strip().splitlines()[-1])
        assert result["ready"] is True, result
        assert result["attempts"] >= 2, result
    finally:
        if probe is not None and probe.poll() is None:
            probe.kill()
        prepared.finish()
