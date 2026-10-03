"""Foreground Dashboard lifecycle tests with no sockets, workers or host effects."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from groundtruth_kb import dashboard_service as service
from groundtruth_kb import job_containment


@pytest.fixture
def foreground(monkeypatch, tmp_path):
    events: list[Any] = []
    workers: list[Any] = []
    servers: list[Any] = []
    config = SimpleNamespace(project_root=tmp_path / "Installed project")
    selected = tmp_path / "Owner's settings" / "groundtruth.toml"
    settings = {
        "residual_worker": False,
        "refresh_error": None,
        "after_start": None,
        "close_error": None,
        "startup_hung": False,
        "clock": 100.0,
    }
    identity = {"pid": service.os.getpid(), "created_at": "observed-creation", "executable": "python.exe"}
    monkeypatch.setattr(job_containment, "process_identity", lambda pid: dict(identity))
    monkeypatch.setattr(service, "time", SimpleNamespace(monotonic=lambda: settings["clock"]))

    class Event:
        def __init__(self):
            self.value = False

        def set(self):
            self.value = True

        def is_set(self):
            return self.value

        def wait(self, timeout):
            # The mocked worker stops after its startup call; startup polling
            # still waits for the actual completion signal from _run_scheduler.
            if settings["startup_hung"] and not self.value and timeout < 60:
                settings["clock"] = 201.0
            return self.value or timeout >= 60

    class Thread:
        def __init__(self, *, target, args, kwargs=None, daemon):
            self.target, self.args, self.kwargs = target, args, kwargs or {}
            self.alive = False
            workers.append(self)

        def start(self):
            events.append("scheduler.start")
            self.alive = True
            if not settings["startup_hung"]:
                self.target(*self.args, **self.kwargs)
            if settings["after_start"] is not None:
                settings["after_start"](self.args[0])

        def is_alive(self):
            return self.alive

        def join(self, *, timeout):
            events.append("scheduler.join")
            self.alive = settings["residual_worker"]

    class Socket:
        def __init__(self, address):
            self.address, self.closed = address, False

        def fileno(self):
            return -1 if self.closed else 42

        def getsockname(self):
            return self.address

    class Server:
        def __init__(self, address, handler):
            events.append("listener.bind")
            self.socket = Socket(address)
            self.handler = handler
            self.server_port = address[1]
            self.daemon_threads = True
            self.block_on_close = True
            servers.append(self)

        def server_close(self):
            events.append("listener.close")
            self.socket.closed = True
            if settings["close_error"] is not None:
                raise settings["close_error"]

        def handle_request(self):
            events.append("listener.request")
            assert self.daemon_threads is False and self.block_on_close is True
            assert self.handler.timeout == 10
            # Runtime already admitted: later expiry does not stop this server.
            settings["clock"] = 1000.0
            raise KeyboardInterrupt

        def serve_forever(self):
            events.append("owner.serve_forever")
            raise KeyboardInterrupt

    def initialize(*args, **kwargs):
        events.append("startup.refresh")
        if settings["refresh_error"] is not None:
            raise RuntimeError(settings["refresh_error"])
        return {"status": "completed", "record_counts": {"refresh_runs": 1}}

    monkeypatch.setattr(service.threading, "Event", Event)
    monkeypatch.setattr(service.threading, "Thread", Thread)
    monkeypatch.setattr(service, "ThreadingHTTPServer", Server)
    monkeypatch.setattr(service, "initialize_dashboard", initialize)
    args = (config, config.project_root / "display.sqlite", config.project_root / "runtime")
    return SimpleNamespace(
        events=events,
        settings=settings,
        workers=workers,
        servers=servers,
        args=args,
        selected=selected,
        observer=None,
        before=None,
        ready=None,
    )


def _hooks(foreground):
    def on_observer(observe):
        foreground.observer = observe
        foreground.events.append("observer")
        assert not observe()["states"]["service:dashboard"]["running"]

    def before(operation, targets, effects, phase):
        foreground.events.append("admission")
        foreground.before = (operation, targets, effects, phase)
        assert foreground.events == ["observer", "admission"]

    def ready():
        foreground.events.append("ready")
        foreground.ready = foreground.observer()
        assert foreground.ready["states"]["service:dashboard"]["ready"]

    return {"before_effect": before, "on_observer": on_observer, "ready": ready, "deadline": lambda: 200.0}


def test_bounded_serve_admits_own_foreground_and_verifies_first_refresh(foreground):
    result = service.run_service(*foreground.args, config_path=foreground.selected, **_hooks(foreground))

    assert foreground.before == (
        "dashboard.serve",
        ["service:dashboard"],
        [{"target": "service:dashboard", "effect": "service.start"}],
        "forward",
    )
    assert foreground.events == [
        "observer",
        "admission",
        "listener.bind",
        "scheduler.start",
        "startup.refresh",
        "ready",
        "listener.request",
        "listener.close",
        "scheduler.join",
    ]
    observed = foreground.ready
    assert observed["installation_root"] == str(foreground.args[0].project_root.resolve())
    assert observed["config_path"] == str(foreground.selected.resolve())
    assert observed["observed_controller_paths"] == {"service:dashboard": str(Path(service.sys.executable).resolve())}
    assert observed["health"]["dashboard_db"] == str(foreground.args[1].resolve())
    assert observed["health"]["runtime_root"] == str(foreground.args[2].resolve())
    assert observed["health"]["config_path"] == str(foreground.selected.resolve())
    assert observed["health"]["interval_seconds"] == 3600
    assert observed["health"]["grafana_port"] == 8767
    assert observed["listener"] == {"host": "127.0.0.1", "port": 8766, "bound": True, "closed": False}
    assert result["ok"] and result["ready"] and result["stopped"]
    assert result["server_closed"] and result["scheduler_exited"]
    assert result["request_handlers_exited"]
    assert foreground.servers[0].handler.timeout == 10
    assert not result["final"]["states"]["service:dashboard"]["running"]


@pytest.mark.parametrize("returns_false", [False, True])
def test_admission_denial_precedes_bind_and_worker_start(foreground, returns_false):
    hooks = _hooks(foreground)

    def deny(*args):
        foreground.events.append("admission.denied")
        if returns_false:
            return False
        raise RuntimeError("canonical bound denied")

    hooks["before_effect"] = deny
    result = service.run_service(*foreground.args, config_path=foreground.selected, **hooks)

    assert not result["ok"] and not result["ready"]
    assert result["stopped"] and result["server_closed"] and result["scheduler_exited"]
    assert foreground.events == ["observer", "admission.denied"]
    assert not foreground.servers and not foreground.workers


def test_failed_first_refresh_signals_completion_and_cleans_own_resources(foreground):
    foreground.settings["refresh_error"] = "native observation unavailable"
    result = service.run_service(*foreground.args, config_path=foreground.selected, **_hooks(foreground))

    assert not result["ok"] and not result["ready"]
    assert "native observation unavailable" in result["detail"]
    assert result["stopped"] and result["scheduler_exited"]
    assert foreground.workers[0].kwargs["startup_done"].is_set()
    assert "ready" not in foreground.events and "listener.request" not in foreground.events
    assert foreground.events[-2:] == ["listener.close", "scheduler.join"]


def test_declared_readiness_denial_is_failed_start_with_owned_cleanup(foreground):
    hooks = _hooks(foreground)

    def deny_ready():
        foreground.events.append("ready.denied")
        raise RuntimeError("declared verification denied")

    hooks["ready"] = deny_ready
    result = service.run_service(*foreground.args, config_path=foreground.selected, **hooks)

    assert not result["ok"] and not result["ready"]
    assert result["stopped"]
    assert "declared verification denied" in result["detail"]
    assert "listener.request" not in foreground.events


def test_live_startup_health_must_match_the_selected_configuration(foreground):
    foreground.settings["after_start"] = lambda state: setattr(state, "grafana_port", 3300)
    result = service.run_service(*foreground.args, config_path=foreground.selected, **_hooks(foreground))

    assert not result["ok"] and not result["ready"]
    assert result["stopped"]
    assert "ready" not in foreground.events


def test_nonexited_scheduler_is_reported_even_after_owned_listener_closes(foreground):
    foreground.settings["residual_worker"] = True
    result = service.run_service(*foreground.args, config_path=foreground.selected, **_hooks(foreground))

    assert result["ready"] and result["server_closed"]
    assert not result["ok"] and not result["stopped"] and not result["scheduler_exited"]
    assert result["phase"] == "cleanup"
    assert result["final"]["states"]["service:dashboard"]["running"]
    assert not result["final"]["states"]["service:dashboard"]["ready"]


@pytest.mark.parametrize("close_error", [RuntimeError("handler join failed"), KeyboardInterrupt()])
def test_failed_or_interrupted_close_does_not_claim_handler_exit(foreground, close_error):
    foreground.settings["close_error"] = close_error
    result = service.run_service(*foreground.args, config_path=foreground.selected, **_hooks(foreground))

    assert result["ready"] and result["server_closed"] and result["scheduler_exited"]
    assert not result["ok"] and not result["stopped"] and not result["request_handlers_exited"]
    assert result["phase"] == "cleanup"
    assert result["final"]["states"]["service:dashboard"]["running"]
    assert not result["final"]["request_handlers_exited"]
    assert foreground.events[-1] == "scheduler.join"


def test_expired_startup_admission_cleans_listener_and_reports_live_worker(foreground):
    foreground.settings["startup_hung"] = True
    foreground.settings["residual_worker"] = True
    result = service.run_service(*foreground.args, config_path=foreground.selected, **_hooks(foreground))

    assert not foreground.workers[0].kwargs["startup_done"].is_set()
    assert not result["ok"] and not result["ready"] and not result["stopped"]
    assert "startup_admission_expired" in result["detail"]
    assert result["server_closed"] and result["request_handlers_exited"]
    assert not result["scheduler_exited"]
    assert "ready" not in foreground.events and "listener.request" not in foreground.events
    assert foreground.events[-2:] == ["listener.close", "scheduler.join"]


@pytest.mark.parametrize("deadline", [None, float("inf"), True, 100.0])
def test_missing_invalid_or_expired_admission_deadline_refuses_before_bind(foreground, deadline):
    hooks = _hooks(foreground)
    hooks["deadline"] = lambda: deadline
    result = service.run_service(*foreground.args, config_path=foreground.selected, **hooks)

    assert not result["ok"] and not result["ready"]
    assert result["stopped"]
    assert foreground.events == ["observer", "admission"]


def test_partial_hooks_refuse_without_falling_into_owner_behavior(foreground):
    with pytest.raises(ValueError, match="requires_before_effect_observer_ready_and_deadline"):
        service.run_service(*foreground.args, config_path=foreground.selected, before_effect=lambda *args: None)
    assert foreground.events == []


def test_owner_no_hooks_preserves_serve_forever_and_none_result(foreground, monkeypatch):
    def no_identity_probe(pid):
        pytest.fail("Owner invocation unexpectedly used bounded process identity")

    monkeypatch.setattr(job_containment, "process_identity", no_identity_probe)
    result = service.run_service(*foreground.args, config_path=foreground.selected)

    assert result is None
    assert foreground.servers[0].handler.timeout is None
    assert foreground.events == [
        "listener.bind",
        "scheduler.start",
        "startup.refresh",
        "owner.serve_forever",
        "listener.close",
        "scheduler.join",
    ]
