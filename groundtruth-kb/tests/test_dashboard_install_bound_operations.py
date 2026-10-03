"""Isolated bounded installer tests; all download/process seams are mocked.

No test operates installed GT services or uses a real network download.
"""

from __future__ import annotations

import hashlib
import io
import json
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from groundtruth_kb import dashboard

pytestmark = pytest.mark.skipif(
    sys.platform != "win32", reason="Supported installer uses Windows no-clobber directory rename"
)


def _deadline(seconds=30):
    due = time.monotonic() + seconds
    return lambda: due


def _paths(root):
    runtime = root / "runtime"
    return dashboard.DashboardPaths(
        project_root=root,
        db_path=runtime / "dashboard.sqlite",
        runtime_root=runtime,
        grafana_home=root / ".groundtruth" / "tools" / "grafana",
        provisioning_dir=runtime / "provisioning",
        dashboards_dir=runtime / "dashboards",
        logs_dir=runtime / "logs",
        launch_record=runtime / "launch.json",
    )


def _mock_release(monkeypatch):
    calls = []

    def download(stage, check, deadline):
        check("installation.publish")
        home = stage / "release"
        (home / "bin").mkdir(parents=True)
        (home / "conf").mkdir()
        (home / "bin" / "grafana.exe").write_bytes(b"pinned-release-binary")
        (home / "conf" / "defaults.ini").write_bytes(b"pinned-defaults")
        calls.append("download")
        return home

    def install_plugin(home, check, deadline, *, on_quiescent=None):
        check("installation.publish", "process.start")
        plugin = home / "data" / "plugins" / dashboard.SQLITE_PLUGIN_ID
        plugin.mkdir(parents=True)
        (plugin / "plugin.json").write_text(
            json.dumps(
                {
                    "id": dashboard.SQLITE_PLUGIN_ID,
                    "info": {"version": dashboard.SQLITE_PLUGIN_VERSION},
                }
            ),
            encoding="utf-8",
        )
        (plugin / "module.js").write_bytes(b"pinned-plugin")
        check("process.stop")
        calls.append("plugin")
        if on_quiescent is not None:
            on_quiescent()

    def verify(binary, plugin, *, check=None, deadline=None, **kwargs):
        check("installation.publish", "process.start")
        check("process.stop")
        calls.append("verified-and-stopped")
        return {
            "id": dashboard.SQLITE_PLUGIN_ID,
            "version": dashboard.SQLITE_PLUGIN_VERSION,
            "files_sha256": dashboard._plugin_file_identities(plugin),
            "signature": {"signature": "valid", "signatureType": "community", "signatureOrg": "frser"},
            "verifier_version": dashboard.GRAFANA_VERSION,
            "verifier_binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
            "verified_at": "2026-10-02T00:00:00+00:00",
        }

    monkeypatch.setattr(dashboard, "_bounded_download_grafana", download)
    monkeypatch.setattr(dashboard, "_bounded_install_sqlite_plugin", install_plugin)
    monkeypatch.setattr(dashboard, "_verify_sqlite_plugin", verify)
    return calls


def _callbacks(paths, *, deny=None, on_ready=None):
    effects = []
    observers = []
    due = [time.monotonic() + 600]

    def before(operation, targets, actual, phase):
        assert operation == "dashboard.install" and targets == ["service:dashboard"]
        assert phase in {"preflight", "forward", "rollback"}
        assert all(set(effect) == {"target", "effect"} for effect in actual)
        assert all(effect["target"] == "service:dashboard" for effect in actual)
        effects.append((phase, [effect["effect"] for effect in actual]))
        if deny:
            deny(actual, phase)

    def bind(observer):
        observers.append(observer)
        assert observer()["installation"] == {"predicate": "pinned_grafana_sqlite", "verified": False}

    def ready():
        value = observers[0]()
        assert value["states"] == {}
        assert value["observed_controller_paths"] == {"service:dashboard": str(paths.grafana_home)}
        assert value["installation"] == {"predicate": "pinned_grafana_sqlite", "verified": True}
        if on_ready:
            on_ready(due)

    return (
        {
            "config_path": paths.project_root / "groundtruth.toml",
            "before_effect": before,
            "on_observer": bind,
            "ready": ready,
            "deadline": lambda: due[0],
        },
        effects,
        observers,
    )


def test_cold_publication_follows_verified_stopped_stage_and_observes_final_path(tmp_path, monkeypatch):
    paths = _paths(tmp_path)
    calls = _mock_release(monkeypatch)
    callbacks, effects, _ = _callbacks(paths)
    result = dashboard.install_grafana(paths, **callbacks)
    assert result == paths.grafana_home / "bin" / "grafana.exe"
    assert calls == ["download", "plugin", "verified-and-stopped"]
    value = json.loads((paths.grafana_home / "installed.json").read_text(encoding="utf-8"))
    assert value["grafana_binary"] == str(result)
    assert value["archive_verified_by_this_install"] is True
    assert effects[0] == ("preflight", [])
    assert any("process.start" in actual for _, actual in effects)
    assert any("process.stop" in actual for _, actual in effects)
    assert any("installation.remove" in actual for _, actual in effects)
    assert not list(tmp_path.glob(".grafana-install-*"))


def test_fully_pinned_existing_installation_is_unchanged_and_still_independently_verified(tmp_path, monkeypatch):
    paths = _paths(tmp_path)
    calls = _mock_release(monkeypatch)
    callbacks, _, _ = _callbacks(paths)
    result = dashboard.install_grafana(paths, **callbacks)
    before = dashboard._installation_tree_identity(paths.grafana_home)
    observation = (paths.grafana_home / "installed.json").read_bytes()
    calls.clear()
    callbacks, _, _ = _callbacks(paths)
    assert dashboard.install_grafana(paths, **callbacks) == result
    assert calls == ["download", "verified-and-stopped"]
    assert dashboard._installation_tree_identity(paths.grafana_home) == before
    assert (paths.grafana_home / "installed.json").read_bytes() == observation
    assert not list(tmp_path.glob(".grafana-install-*"))


@pytest.mark.parametrize(
    "change",
    [
        lambda home: (home / "conf" / "defaults.ini").write_bytes(b"changed-defaults"),
        lambda home: (home / "unexpected.txt").write_bytes(b"unrequested-file"),
    ],
)
def test_existing_release_divergence_is_refused_without_destination_write(tmp_path, monkeypatch, change):
    paths = _paths(tmp_path)
    calls = _mock_release(monkeypatch)
    callbacks, _, _ = _callbacks(paths)
    dashboard.install_grafana(paths, **callbacks)
    change(paths.grafana_home)
    before = dashboard._installation_tree_identity(paths.grafana_home)
    calls.clear()
    callbacks, _, _ = _callbacks(paths)
    with pytest.raises((ValueError, RuntimeError), match="release_differs_from_pin"):
        dashboard.install_grafana(paths, **callbacks)
    assert dashboard._installation_tree_identity(paths.grafana_home) == before
    assert "plugin" not in calls and "verified-and-stopped" not in calls


def test_unproved_existing_installation_is_refused_before_staging(tmp_path, monkeypatch):
    paths = _paths(tmp_path)
    paths.grafana_home.mkdir(parents=True)
    (paths.grafana_home / "foreign.txt").write_bytes(b"preserve")
    calls = _mock_release(monkeypatch)
    callbacks, effects, _ = _callbacks(paths)
    before = dashboard._installation_tree_identity(paths.grafana_home)
    with pytest.raises(ValueError, match="not_pinned"):
        dashboard.install_grafana(paths, **callbacks)
    assert not calls and not effects
    assert dashboard._installation_tree_identity(paths.grafana_home) == before
    assert not list(tmp_path.glob(".grafana-install-*"))


@pytest.mark.parametrize("option", ["skip_download", "skip_plugin"])
def test_bound_skip_options_are_refused_before_staging(tmp_path, monkeypatch, option):
    paths = _paths(tmp_path)
    calls = _mock_release(monkeypatch)
    callbacks, effects, _ = _callbacks(paths)
    with pytest.raises(ValueError, match="skip_options_unsupported"):
        dashboard.install_grafana(paths, **callbacks, **{option: True})
    assert not calls and not effects and not paths.grafana_home.exists()


def test_custom_destination_and_partial_callbacks_are_refused_before_effect(tmp_path, monkeypatch):
    paths = _paths(tmp_path)
    calls = _mock_release(monkeypatch)
    callbacks, effects, _ = _callbacks(paths)
    callbacks.pop("ready")
    with pytest.raises(ValueError, match="complete_callbacks"):
        dashboard.install_grafana(paths, **callbacks)
    custom = dashboard.DashboardPaths(**{**paths.__dict__, "grafana_home": tmp_path / "custom"})
    callbacks, effects, _ = _callbacks(custom)
    with pytest.raises(ValueError, match="standard_destination"):
        dashboard.install_grafana(custom, **callbacks)
    assert not calls and not effects


def test_refused_initial_scope_has_no_staging_or_publication(tmp_path, monkeypatch):
    paths = _paths(tmp_path)
    calls = _mock_release(monkeypatch)

    def refuse(_actual, _phase):
        raise RuntimeError("native_scope_refused")

    callbacks, _, _ = _callbacks(paths, deny=refuse)
    with pytest.raises(RuntimeError, match="native_scope_refused"):
        dashboard.install_grafana(paths, **callbacks)
    assert not calls and not paths.grafana_home.exists()
    assert not list(tmp_path.glob(".grafana-install-*"))


def test_failed_final_verification_removes_only_captured_publication(tmp_path, monkeypatch):
    paths = _paths(tmp_path)
    _mock_release(monkeypatch)

    def reject(_due):
        raise RuntimeError("declared_result_refused")

    callbacks, effects, _ = _callbacks(paths, on_ready=reject)
    with pytest.raises(RuntimeError, match="declared_result_refused"):
        dashboard.install_grafana(paths, **callbacks)
    assert not paths.grafana_home.exists()
    assert not list(tmp_path.glob(".grafana-install-*"))
    assert ("rollback", ["installation.remove"]) in effects


def test_changed_published_postimage_is_preserved_as_residual(tmp_path, monkeypatch):
    paths = _paths(tmp_path)
    _mock_release(monkeypatch)

    def reject(_due):
        (paths.grafana_home / "foreign.txt").write_bytes(b"foreign")
        raise RuntimeError("declared_result_refused")

    callbacks, _, _ = _callbacks(paths, on_ready=reject)
    with pytest.raises(RuntimeError, match="cleanup_postimage_changed"):
        dashboard.install_grafana(paths, **callbacks)
    assert (paths.grafana_home / "foreign.txt").read_bytes() == b"foreign"
    assert (paths.grafana_home / "installed.json").is_file()


def test_expired_inverse_keeps_truthful_published_residual(tmp_path, monkeypatch):
    paths = _paths(tmp_path)
    _mock_release(monkeypatch)
    callbacks, _, _ = _callbacks(paths, on_ready=lambda due: due.__setitem__(0, time.monotonic() - 1))
    with pytest.raises(RuntimeError, match="grafana_installation_residual"):
        dashboard.install_grafana(paths, **callbacks)
    assert paths.grafana_home.is_dir()
    assert (paths.grafana_home / "installed.json").is_file()


def test_cleanup_rechecks_postimage_after_permission_callback(tmp_path):
    owned = tmp_path / "owned"
    owned.mkdir()
    (owned / "file.txt").write_bytes(b"owned")
    captured = dashboard._installation_tree_identity(owned)

    def change(*_effects, **_options):
        (owned / "foreign.txt").write_bytes(b"foreign")

    with pytest.raises(RuntimeError, match="postimage_changed"):
        dashboard._bounded_installation_remove(owned, captured, change, _deadline(10), phase="rollback")
    assert (owned / "foreign.txt").is_file()


def test_denied_process_inverse_confirms_intrinsic_owned_teardown_and_returns_failure(tmp_path, monkeypatch):
    owned = tmp_path / "process-temp"
    owned.mkdir()
    captured = dashboard._installation_tree_identity(owned)
    members = [91]
    closed = []
    stops = []
    process = SimpleNamespace(pid=91, poll=lambda: None if members else 0, wait=lambda **_kwargs: 0)
    monkeypatch.setattr(dashboard, "_job_member_pids", lambda _job: list(members))

    def stopped(job, name, **options):
        assert job == 19 and name == "owned-job" and options == {"timeout": 15}
        stops.append(job)
        members.clear()
        return []

    monkeypatch.setattr(dashboard, "_stop_job", stopped)
    monkeypatch.setattr(dashboard, "_close_handle", lambda job: closed.append(job))

    def refuse(*_effects, **_options):
        raise RuntimeError("native_inverse_refused")

    result = dashboard._bounded_installation_process_end(
        process,
        19,
        "owned-job",
        (owned, captured),
        refuse,
        _deadline(10),
        phase="rollback",
    )
    assert isinstance(result, RuntimeError) and str(result) == "native_inverse_refused"
    assert stops == [19] and closed == [19] and not members
    assert owned.is_dir()  # Refusal grants no file removal or successful operation.


@pytest.mark.parametrize("identity", [None, {"pid": 91, "created_at": "now", "executable": "C:/foreign.exe"}])
def test_suspended_process_requires_positive_exact_identity_before_resume(tmp_path, monkeypatch, identity):
    executable = tmp_path / "grafana.exe"
    executable.write_bytes(b"pinned")
    process = SimpleNamespace(pid=91)
    monkeypatch.setattr(dashboard.job_containment, "create_job", lambda *_args, **_kwargs: 19)
    monkeypatch.setattr(dashboard, "_process_identity", lambda _pid: identity)
    monkeypatch.setattr(dashboard, "_job_member_pids", lambda _job: [])
    monkeypatch.setattr(dashboard, "_close_handle", lambda _job: None)
    monkeypatch.setattr(
        dashboard, "_resume_primary_thread", lambda _process: pytest.fail("unidentified process resumed")
    )

    def contained(_args, _env, _job, *, resume, **_kwargs):
        assert resume(process) is False
        raise dashboard.job_containment.ContainmentError("ended before it ran")

    monkeypatch.setattr(dashboard.job_containment, "start_contained", contained)
    with (
        (tmp_path / "process.log").open("wb") as log,
        pytest.raises(dashboard.job_containment.ContainmentError, match="ended before it ran"),
    ):
        dashboard._bounded_installation_process(
            [str(executable)], tmp_path, log, lambda *_args, **_kwargs: None, _deadline(10)
        )


def test_owner_no_hook_route_retains_existing_skip_behavior(tmp_path, monkeypatch):
    paths = _paths(tmp_path)
    binary = paths.grafana_home / "bin" / "grafana.exe"
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"owner-selected-existing")
    (paths.grafana_home / "conf").mkdir()
    (paths.grafana_home / "conf" / "defaults.ini").write_bytes(b"owner-defaults")
    monkeypatch.setattr(
        dashboard, "_download_grafana_windows", lambda _home: pytest.fail("owner skip download ignored")
    )
    monkeypatch.setattr(dashboard, "_install_sqlite_plugin", lambda _home: pytest.fail("owner skip plugin ignored"))
    assert dashboard.install_grafana(paths, skip_download=True, skip_plugin=True) == binary
    observation = json.loads((paths.grafana_home / "installed.json").read_text(encoding="utf-8"))
    assert observation["plugin_install_skipped"] is True
    assert observation["plugin_verification"] == "absent_unverified"


def _release_archive():
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz") as archive:
        for name, content in (
            ("grafana-13.2.1/bin/grafana.exe", b"fixture-pinned-binary"),
            ("grafana-13.2.1/conf/defaults.ini", b"fixture-pinned-defaults"),
        ):
            member = tarfile.TarInfo(name)
            member.size = len(content)
            archive.addfile(member, io.BytesIO(content))
    return output.getvalue()


def test_real_staging_downloader_verifies_archive_and_checks_materialization(tmp_path, monkeypatch):
    archive = _release_archive()
    monkeypatch.setattr(dashboard, "GRAFANA_ARCHIVE_SHA256", hashlib.sha256(archive).hexdigest())
    monkeypatch.setattr(dashboard.urllib.request, "urlopen", lambda *_args, **_kwargs: io.BytesIO(archive))
    checks = []
    home = dashboard._bounded_download_grafana(
        tmp_path,
        lambda *effects, **_kwargs: checks.append(effects),
        _deadline(10),
    )
    assert home.is_relative_to(tmp_path)
    assert dashboard.find_grafana_server(home).read_bytes() == b"fixture-pinned-binary"
    assert (home / "conf" / "defaults.ini").read_bytes() == b"fixture-pinned-defaults"
    assert checks == [("installation.publish",), ("installation.publish",)]


def test_real_staging_downloader_rejects_wrong_pin_before_extraction(tmp_path, monkeypatch):
    archive = _release_archive()
    monkeypatch.setattr(dashboard.urllib.request, "urlopen", lambda *_args, **_kwargs: io.BytesIO(archive))
    with pytest.raises(ValueError, match="checksum"):
        dashboard._bounded_download_grafana(tmp_path, lambda *_args, **_kwargs: None, _deadline(10))
    assert (tmp_path / "release.tar.gz").is_file()
    assert not (tmp_path / "extracted").exists()


def test_existing_verifier_confirms_contained_process_end_before_temp_removal(tmp_path, monkeypatch):
    home = tmp_path / "grafana"
    (home / "bin").mkdir(parents=True)
    (home / "conf").mkdir()
    binary = home / "bin" / "grafana.exe"
    binary.write_bytes(b"fixture-binary")
    (home / "conf" / "defaults.ini").write_bytes(b"fixture-defaults")
    plugin = home / "data" / "plugins" / dashboard.SQLITE_PLUGIN_ID
    plugin.mkdir(parents=True)
    (plugin / "plugin.json").write_text(
        json.dumps(
            {
                "id": dashboard.SQLITE_PLUGIN_ID,
                "info": {"version": dashboard.SQLITE_PLUGIN_VERSION},
            }
        ),
        encoding="utf-8",
    )
    checks = []
    members = [91]
    closed = []
    process = SimpleNamespace(pid=91, poll=lambda: None if members else 0, wait=lambda **_kwargs: 0)

    def launched(_args, _home, _log, check, _deadline, **_kwargs):
        check("installation.publish", "process.start")
        temporary = Path(_log.name).parent / "process-temp-owned"
        temporary.mkdir()
        return process, 19, "invocation-verifier", (temporary, dashboard._installation_tree_identity(temporary))

    monkeypatch.setattr(dashboard, "_bounded_installation_process", launched)
    monkeypatch.setattr(dashboard, "_job_member_pids", lambda _job: list(members))

    def stop(_job, _name, **_kwargs):
        assert checks[-1] == (("process.stop",), "forward")
        assert list(home.glob("plugin-verification-*"))
        members.clear()
        return []

    monkeypatch.setattr(dashboard, "_stop_job", stop)
    monkeypatch.setattr(dashboard, "_close_handle", lambda _job: closed.append(_job))
    monkeypatch.setattr(
        dashboard,
        "_process_identity",
        lambda _pid: {
            "pid": 91,
            "created_at": "2026-10-02T00:00:00+00:00",
            "executable": str(binary),
        },
    )

    class Probe:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            pass

        def bind(self, address):
            assert address == ("127.0.0.1", 0)

        def getsockname(self):
            return ("127.0.0.1", 19491)

    monkeypatch.setattr(dashboard.socket, "socket", Probe)

    class Opener:
        def open(self, request, **_kwargs):
            value = (
                {"database": "ok", "version": dashboard.GRAFANA_VERSION}
                if request.full_url.endswith("/api/health")
                else {
                    "id": dashboard.SQLITE_PLUGIN_ID,
                    "info": {"version": dashboard.SQLITE_PLUGIN_VERSION},
                    "signature": "valid",
                    "signatureType": "community",
                    "signatureOrg": "frser",
                }
            )
            return io.BytesIO(json.dumps(value).encode())

    monkeypatch.setattr(dashboard.urllib.request, "build_opener", lambda *_args: Opener())

    def check(*effects, phase="forward"):
        checks.append((effects, phase))

    before = dashboard._plugin_file_identities(plugin)
    result = dashboard._verify_sqlite_plugin(binary, plugin, check=check, deadline=_deadline(30))
    assert result["verifier_version"] == dashboard.GRAFANA_VERSION
    assert result["files_sha256"] == before and dashboard._plugin_file_identities(plugin) == before
    assert not members and closed == [19]
    assert not list(home.glob("plugin-verification-*"))
    stop_index = checks.index((("process.stop",), "forward"))
    assert any(effects == ("installation.remove",) for effects, _phase in checks[stop_index + 1 :])


def test_destination_appearing_at_publication_is_never_clobbered(tmp_path, monkeypatch):
    paths = _paths(tmp_path)
    _mock_release(monkeypatch)
    appeared = []

    def foreign_destination(actual, phase):
        if (
            phase == "forward"
            and any(item["effect"] == "installation.publish" for item in actual)
            and paths.grafana_home.parent.exists()
            and not paths.grafana_home.exists()
            and list(tmp_path.glob(".grafana-install-*/release/installed.json"))
        ):
            paths.grafana_home.mkdir()
            (paths.grafana_home / "foreign.txt").write_bytes(b"foreign")
            appeared.append(True)

    callbacks, _, _ = _callbacks(paths, deny=foreign_destination)
    with pytest.raises(RuntimeError, match="destination_appeared"):
        dashboard.install_grafana(paths, **callbacks)
    assert appeared == [True]
    assert (paths.grafana_home / "foreign.txt").read_bytes() == b"foreign"
    assert not (paths.grafana_home / "installed.json").exists()


def test_unconfirmed_verifier_job_blocks_publication_and_keeps_named_stage(tmp_path, monkeypatch):
    paths = _paths(tmp_path)
    _mock_release(monkeypatch)

    def unconfirmed(binary, plugin, *, check, deadline, **_kwargs):
        check("installation.publish", "process.start")
        (binary.parent.parent / "plugin-verification-live").mkdir()
        raise RuntimeError("grafana_verifier_cleanup_unconfirmed: job=owned-verifier; pid=91")

    monkeypatch.setattr(dashboard, "_verify_sqlite_plugin", unconfirmed)
    callbacks, _, _ = _callbacks(paths)
    with pytest.raises(RuntimeError, match="grafana_verifier_cleanup_unconfirmed"):
        dashboard.install_grafana(paths, **callbacks)
    assert not paths.grafana_home.exists()
    assert list(tmp_path.glob(".grafana-install-*/release/plugin-verification-live"))


def test_owned_copy_uses_one_native_phase_check_despite_files_and_chunks(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    for index in range(4):
        (source / f"file-{index}.bin").write_bytes(b"content" * 350000)
    checks = []
    target = tmp_path / "copy"
    dashboard._bounded_installation_copy(source, target, lambda *effects: checks.append(effects), _deadline(30))
    assert checks == [("installation.publish",)]
    assert dashboard._plugin_file_identities(source) == dashboard._plugin_file_identities(target)


def test_deadline_crossing_final_cleanup_scan_refuses_before_removal(tmp_path, monkeypatch):
    owned = tmp_path / "owned"
    owned.mkdir()
    (owned / "file.bin").write_bytes(b"owned")
    original = dashboard._installation_tree_identity
    captured = original(owned)
    due = [time.monotonic() + 30]
    scans = []
    checks = []

    def slow_scan(root):
        result = original(root)
        scans.append(root)
        if len(scans) == 2:
            due[0] = time.monotonic() - 1
        return result

    monkeypatch.setattr(dashboard, "_installation_tree_identity", slow_scan)
    monkeypatch.setattr(
        dashboard.shutil, "rmtree", lambda *_args, **_kwargs: pytest.fail("expired cleanup mutated files")
    )
    with pytest.raises(RuntimeError, match="deadline_expired"):
        dashboard._bounded_installation_remove(
            owned, captured, lambda *effects, **_kwargs: checks.append(effects), lambda: due[0], phase="rollback"
        )
    assert checks == [("installation.remove",)] and len(scans) == 2
    assert (owned / "file.bin").read_bytes() == b"owned"


def test_deadline_crossing_final_publication_scan_refuses_before_rename(tmp_path, monkeypatch):
    paths = _paths(tmp_path)
    _mock_release(monkeypatch)
    callbacks, _effects, _ = _callbacks(paths)
    due = [time.monotonic() + 30]
    callbacks["deadline"] = lambda: due[0]
    original = dashboard._installation_tree_identity
    candidates = []

    def slow_scan(root):
        result = original(root)
        if root.name == "release":
            candidates.append(root)
            if len(candidates) == 2:
                due[0] = time.monotonic() - 1
        return result

    monkeypatch.setattr(dashboard, "_installation_tree_identity", slow_scan)
    with pytest.raises(RuntimeError, match="deadline_expired"):
        dashboard.install_grafana(paths, **callbacks)
    assert len(candidates) == 2
    assert not paths.grafana_home.exists()
    assert list(tmp_path.glob(".grafana-install-*/release/installed.json"))


def test_extended_executable_path_and_dos_identity_match_same_physical_file(tmp_path, monkeypatch):
    executable = tmp_path / "grafana.exe"
    executable.write_bytes(b"pinned")
    extended = "\\\\?\\" + str(executable)
    identity = {"pid": 91, "created_at": "132000000000000000", "executable": str(executable)}
    process = SimpleNamespace(pid=91, poll=lambda: 0, wait=lambda **_kwargs: 0)
    checks = []
    resumed = []
    jobs = []

    def create(name, *, inheritable):
        assert inheritable is False
        jobs.append(name)
        return 19

    monkeypatch.setattr(dashboard.job_containment, "create_job", create)
    monkeypatch.setattr(dashboard, "_process_identity", lambda _pid: dict(identity))
    monkeypatch.setattr(dashboard, "_job_member_pids", lambda _job: [])
    monkeypatch.setattr(dashboard, "_close_handle", lambda _job: None)
    monkeypatch.setattr(dashboard, "_resume_primary_thread", lambda value: resumed.append(value.pid) or True)

    def contained(args, env, _job, *, resume, inherit_job, **_kwargs):
        assert args == [extended] and inherit_job is False
        assert Path(env["TEMP"]).is_relative_to(tmp_path) and env["TMP"] == env["TEMP"]
        assert "process-temp-" in env["TEMP"]
        assert resume(process) is True
        return process

    monkeypatch.setattr(dashboard.job_containment, "start_contained", contained)
    with (tmp_path / "process.log").open("wb") as log:
        result = dashboard._bounded_installation_process(
            [extended],
            tmp_path,
            log,
            lambda *effects, **_kwargs: checks.append(effects),
            _deadline(30),
            env={"TEMP": "C:/outside", "TMP": "C:/outside"},
        )
    assert len(jobs) == 1 and resumed == [91]
    assert checks == [("installation.publish", "process.start"), ("installation.publish", "process.start")]
    assert (
        dashboard._bounded_installation_process_end(
            result[0],
            result[1],
            result[2],
            result[3],
            lambda *_args, **_kwargs: None,
            _deadline(30),
            phase="forward",
        )
        is None
    )
    assert not result[3][0].exists()


def test_deadline_crossing_final_process_identity_read_refuses_resume(tmp_path, monkeypatch):
    executable = tmp_path / "grafana.exe"
    executable.write_bytes(b"pinned")
    identity = {"pid": 91, "created_at": "132000000000000000", "executable": str(executable)}
    due = [time.monotonic() + 30]
    reads = []
    checks = []
    closed = []
    process = SimpleNamespace(pid=91)

    def observed(_pid):
        reads.append(_pid)
        if len(reads) == 2:
            due[0] = time.monotonic() - 1
        return dict(identity)

    monkeypatch.setattr(dashboard, "_process_identity", observed)
    monkeypatch.setattr(dashboard.job_containment, "create_job", lambda *_args, **_kwargs: 19)
    monkeypatch.setattr(dashboard, "_job_member_pids", lambda _job: [])
    monkeypatch.setattr(dashboard, "_close_handle", lambda job: closed.append(job))
    monkeypatch.setattr(dashboard, "_resume_primary_thread", lambda _process: pytest.fail("expired child resumed"))

    def contained(_args, _env, _job, *, resume, **_kwargs):
        assert resume(process) is False
        raise dashboard.job_containment.ContainmentError("ended before it ran")

    monkeypatch.setattr(dashboard.job_containment, "start_contained", contained)
    with (
        (tmp_path / "process.log").open("wb") as log,
        pytest.raises(dashboard.job_containment.ContainmentError, match="ended before it ran"),
    ):
        dashboard._bounded_installation_process(
            [str(executable)],
            tmp_path,
            log,
            lambda *effects, **_kwargs: checks.append(effects),
            lambda: due[0],
        )
    assert reads == [91, 91] and len(checks) == 2 and closed == [19]


def test_failed_intrinsic_teardown_closes_only_owned_job_and_reports_residual(tmp_path, monkeypatch):
    owned = tmp_path / "process-temp"
    owned.mkdir()
    captured = dashboard._installation_tree_identity(owned)
    closed = []
    process = SimpleNamespace(
        pid=91, poll=lambda: None, wait=lambda **_kwargs: pytest.fail("unconfirmed stop was accepted")
    )
    monkeypatch.setattr(dashboard, "_job_member_pids", lambda _job: [91])

    def failed(job, name, **_kwargs):
        assert job == 19 and name == "owned-job"
        raise RuntimeError("intrinsic_termination_unconfirmed")

    monkeypatch.setattr(dashboard, "_stop_job", failed)
    monkeypatch.setattr(dashboard, "_close_handle", lambda job: closed.append(job))
    with pytest.raises(
        RuntimeError, match="cleanup_unconfirmed.*job=owned-job.*pid=91.*intrinsic_termination_unconfirmed"
    ):
        dashboard._bounded_installation_process_end(
            process,
            19,
            "owned-job",
            (owned, captured),
            lambda *_args, **_kwargs: None,
            _deadline(-1),
            phase="rollback",
        )
    assert closed == [19] and owned.is_dir()


def _mock_quiescent_phase_process(monkeypatch, *, wait_code=0, plugin_partial=False, changed_release=False):
    members = [91]
    closed = []
    image = [None]

    def launched(_args, home, log, check, _deadline, **_kwargs):
        image[0] = _args[0]
        check("installation.publish", "process.start")
        if plugin_partial:
            plugin = home / "data" / "plugins" / dashboard.SQLITE_PLUGIN_ID
            plugin.mkdir()
            (plugin / "partial-download.bin").write_bytes(b"phase-owned partial output")
        if changed_release:
            (home / "conf" / "defaults.ini").write_bytes(b"foreign release change")
        temporary = Path(log.name).parent / "process-temp-owned"
        temporary.mkdir()
        initial = dashboard._installation_tree_identity(temporary)
        (temporary / "download.tmp").write_bytes(b"phase-owned temporary output")

        def waited(**_kwargs):
            members.clear()
            return wait_code

        process = SimpleNamespace(pid=91, poll=lambda: None if members else wait_code, wait=waited)
        return process, 19, "phase-owned-job", (temporary, initial)

    monkeypatch.setattr(dashboard, "_bounded_installation_process", launched)
    monkeypatch.setattr(dashboard, "_job_member_pids", lambda _job: list(members))

    def stopped(job, name, **_kwargs):
        assert job == 19 and name == "phase-owned-job"
        members.clear()
        return []

    monkeypatch.setattr(dashboard, "_stop_job", stopped)
    monkeypatch.setattr(dashboard, "_close_handle", lambda job: closed.append(job))
    monkeypatch.setattr(
        dashboard,
        "_process_identity",
        lambda pid: {
            "pid": pid,
            "created_at": "132000000000000000",
            "executable": image[0],
        },
    )
    return members, closed


def test_nonzero_plugin_exit_with_confirmed_quiescence_removes_own_stage(tmp_path, monkeypatch):
    real_plugin = dashboard._bounded_install_sqlite_plugin
    paths = _paths(tmp_path)
    _mock_release(monkeypatch)
    monkeypatch.setattr(dashboard, "_bounded_install_sqlite_plugin", real_plugin)
    members, closed = _mock_quiescent_phase_process(monkeypatch, wait_code=7, plugin_partial=True)
    callbacks, effects, _ = _callbacks(paths)
    with pytest.raises(subprocess.CalledProcessError) as error:
        dashboard.install_grafana(paths, **callbacks)
    assert error.value.returncode == 7
    assert closed == [19] and not members
    assert not paths.grafana_home.exists()
    assert not list(tmp_path.glob(".grafana-install-*"))
    assert ("rollback", ["installation.remove"]) in effects


def test_failed_plugin_quiescence_capture_preserves_changed_prior_release(tmp_path, monkeypatch):
    real_plugin = dashboard._bounded_install_sqlite_plugin
    paths = _paths(tmp_path)
    _mock_release(monkeypatch)
    monkeypatch.setattr(dashboard, "_bounded_install_sqlite_plugin", real_plugin)
    members, closed = _mock_quiescent_phase_process(
        monkeypatch,
        wait_code=7,
        plugin_partial=True,
        changed_release=True,
    )
    callbacks, _, _ = _callbacks(paths)
    with pytest.raises(RuntimeError, match="phase_preimage_changed"):
        dashboard.install_grafana(paths, **callbacks)
    assert closed == [19] and not members and not paths.grafana_home.exists()
    remaining = list(tmp_path.glob(".grafana-install-*/release/conf/defaults.ini"))
    assert len(remaining) == 1 and remaining[0].read_bytes() == b"foreign release change"


def test_safe_verifier_failure_with_confirmed_teardown_removes_own_stage(tmp_path, monkeypatch):
    real_verify = dashboard._verify_sqlite_plugin
    paths = _paths(tmp_path)
    _mock_release(monkeypatch)
    monkeypatch.setattr(dashboard, "_verify_sqlite_plugin", real_verify)
    members, closed = _mock_quiescent_phase_process(monkeypatch)

    class Probe:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            pass

        def bind(self, address):
            assert address == ("127.0.0.1", 0)

        def getsockname(self):
            return ("127.0.0.1", 19491)

    monkeypatch.setattr(dashboard.socket, "socket", Probe)

    class Opener:
        def open(self, request, **_kwargs):
            assert request.full_url.endswith("/api/health")
            return io.BytesIO(json.dumps({"database": "ok", "version": "unapproved-runtime-version"}).encode())

    monkeypatch.setattr(dashboard.urllib.request, "build_opener", lambda *_args: Opener())
    callbacks, effects, _ = _callbacks(paths)
    with pytest.raises(ValueError, match="verifier_version_differs_from_pin"):
        dashboard.install_grafana(paths, **callbacks)
    assert closed == [19] and not members and not paths.grafana_home.exists()
    assert not list(tmp_path.glob(".grafana-install-*"))
    assert ("rollback", ["process.stop"]) in effects
    assert ("rollback", ["installation.remove"]) in effects


def test_refused_plugin_temp_cleanup_never_recaptures_after_confirmed_end(tmp_path, monkeypatch):
    real_plugin = dashboard._bounded_install_sqlite_plugin
    paths = _paths(tmp_path)
    _mock_release(monkeypatch)
    monkeypatch.setattr(dashboard, "_bounded_install_sqlite_plugin", real_plugin)
    members, closed = _mock_quiescent_phase_process(monkeypatch, wait_code=7, plugin_partial=True)

    def refused(actual, phase):
        if any(effect["effect"] == "installation.remove" for effect in actual):
            raise RuntimeError("current_inverse_refused")

    callbacks, _, _ = _callbacks(paths, deny=refused)
    with pytest.raises(RuntimeError, match="current_inverse_refused"):
        dashboard.install_grafana(paths, **callbacks)
    assert closed == [19] and not members and not paths.grafana_home.exists()
    assert list(tmp_path.glob(".grafana-install-*/release/data/plugins/*/partial-download.bin"))


def test_plugin_quiescence_callback_observes_closed_flushed_log(tmp_path, monkeypatch):
    home = tmp_path / "release"
    (home / "bin").mkdir(parents=True)
    (home / "bin" / "grafana.exe").write_bytes(b"pinned-release-binary")
    (home / "conf").mkdir()
    (home / "conf" / "defaults.ini").write_bytes(b"pinned-defaults")
    members, closed_jobs = _mock_quiescent_phase_process(monkeypatch, wait_code=7, plugin_partial=True)
    launch = dashboard._bounded_installation_process
    logs = []
    output = b"buffered owned plugin output\n"

    def buffered_launch(args, selected_home, log, check, deadline, **kwargs):
        logs.append(log)
        log.write(output)
        assert not log.closed
        return launch(args, selected_home, log, check, deadline, **kwargs)

    monkeypatch.setattr(dashboard, "_bounded_installation_process", buffered_launch)
    captured = []

    def quiescent():
        assert logs[0].closed
        assert (home / "plugin-install.log").read_bytes() == output
        captured.append(dashboard._installation_tree_identity(home))

    with pytest.raises(subprocess.CalledProcessError) as error:
        dashboard._bounded_install_sqlite_plugin(
            home,
            lambda *_effects, **_kwargs: None,
            _deadline(),
            on_quiescent=quiescent,
        )
    assert error.value.returncode == 7
    assert len(captured) == 1 and closed_jobs == [19] and not members
    assert not list(home.glob("process-temp-*"))
