# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.project.doctor — workstation readiness checks."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.project import doctor as doctor_module
from groundtruth_kb.project.doctor import (
    DoctorReport,
    ToolCheck,
    _check_git,
    _check_groundtruth_toml,
    _check_python,
    _check_settings_hook_registration_drift,
    _derive_paired_hook_id,
    run_doctor,
)
from groundtruth_kb.project.managed_registry import (
    SettingsHookRegistration,
    find_artifact_by_id,
)

# ---------------------------------------------------------------------------
# _check_python
# ---------------------------------------------------------------------------


def test_check_python_passes() -> None:
    """_check_python() returns pass since Python 3.11+ is running."""
    result = _check_python()
    assert isinstance(result, ToolCheck)
    assert result.name == "Python"
    assert result.found is True
    # Must be running 3.11+ in test env (pyproject.toml requires python_requires >= "3.11")
    assert result.status == "pass"


# ---------------------------------------------------------------------------
# _check_harness_metadata_freshness
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# _check_git
# ---------------------------------------------------------------------------


def test_check_git_returns_tool_check() -> None:
    """_check_git() returns a ToolCheck (git is expected to be present in CI)."""
    result = _check_git()
    assert isinstance(result, ToolCheck)
    assert result.name == "Git"


# ---------------------------------------------------------------------------
# _check_groundtruth_toml
# ---------------------------------------------------------------------------


def test_check_groundtruth_toml_missing(tmp_path: Path) -> None:
    """_check_groundtruth_toml() with missing file → fail."""
    result = _check_groundtruth_toml(tmp_path)
    assert result.status == "fail"
    assert result.found is False


def test_check_groundtruth_toml_valid(tmp_path: Path) -> None:
    """_check_groundtruth_toml() with valid file → pass."""
    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text("[groundtruth]\ndb_path = 'groundtruth.db'\n", encoding="utf-8")
    result = _check_groundtruth_toml(tmp_path)
    assert result.status == "pass"
    assert result.found is True


def test_check_groundtruth_toml_invalid(tmp_path: Path) -> None:
    """_check_groundtruth_toml() with invalid TOML → fail."""
    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text("this is not = valid toml [\n", encoding="utf-8")
    result = _check_groundtruth_toml(tmp_path)
    assert result.status == "fail"


# ---------------------------------------------------------------------------
# Retired local-store checks (owner ruling D31, 2026-09-19)
# ---------------------------------------------------------------------------


def test_retired_store_checks_are_absent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Owner ruling D31 (2026-09-19): the SQLite 'Knowledge DB', 'Deliberation search backend' and
    'DA harvest coverage' checks read the retired local store. They are retired with carried duties
    (the disposable cache contract of ``gt project chroma regenerate`` / isolation:chroma-regeneratable;
    harvest inclusion pinned by TEST-12711 and TEST-12712 on
    ``platform_tests/groundtruth_kb/test_close_wrap_contract.py``), so the doctor neither defines nor
    wires them, keeps no SQLite helper, and a bridge-profile report carries no check by their names."""
    for name in (
        "_check_db_schema",
        "_check_deliberation_search_backend",
        "_check_da_harvest_coverage",
        "_connect_readonly_sqlite",
        "_decode_tafe_json",
        "_active_authorized_work_item_ids",
        "DA_HARVEST_COVERAGE_WARN_THRESHOLD",
        "DA_HARVEST_COVERAGE_ERROR_THRESHOLD",
    ):
        assert not hasattr(doctor_module, name), name
    source = inspect.getsource(run_doctor)
    assert "checks.append(_check_authority_readiness(target))" in source
    for name in ("_check_db_schema", "_check_deliberation_search_backend", "_check_da_harvest_coverage"):
        assert name not in source, name
    module_source = Path(doctor_module.__file__).read_text(encoding="utf-8")
    assert "sqlite3" not in module_source
    assert "KnowledgeDB" not in module_source
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    (tmp_path / "groundtruth.toml").write_text("[groundtruth]\ndb_path = 'groundtruth.db'\n", encoding="utf-8")
    report = run_doctor(tmp_path, "dual-agent")
    names = [check.name for check in report.checks]
    for retired in ("Knowledge DB", "Deliberation search backend", "DA harvest coverage"):
        assert retired not in names, names


def test_run_doctor_has_no_registered_hooks_tracked_check(tmp_path: Path) -> None:
    """Owner ruling D14 (2026-09-17): the rendered harness roots, ``.claude/`` included, are
    gitignored and untracked, so the WI-4457 ``registered hooks git-tracked`` check would WARN
    on every healthy checkout. It is retired: the doctor neither defines nor wires it, and a
    bridge-profile report carries no check by that name."""
    import groundtruth_kb.project.doctor as doctor_module

    assert not hasattr(doctor_module, "_check_registered_hooks_tracked")
    assert "_check_registered_hooks_tracked" not in inspect.getsource(run_doctor)
    (tmp_path / "groundtruth.toml").write_text("[groundtruth]\ndb_path = 'groundtruth.db'\n", encoding="utf-8")
    report = run_doctor(tmp_path, "dual-agent")
    assert "registered hooks git-tracked" not in [check.name for check in report.checks]


# ---------------------------------------------------------------------------
# _check_hooks
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# _check_rules
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# _check_settings_classifiers
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# DoctorReport
# ---------------------------------------------------------------------------


def test_doctor_report_overall_fail_if_required_fails() -> None:
    """DoctorReport.overall = 'fail' if any required check fails."""
    checks = [
        ToolCheck(name="A", required=True, found=False, status="fail"),
        ToolCheck(name="B", required=False, found=True, status="pass"),
    ]
    report = DoctorReport(checks=checks)
    assert report.overall == "fail"


def test_doctor_report_overall_warning() -> None:
    """DoctorReport.overall = 'warning' if warnings but no required fails."""
    checks = [
        ToolCheck(name="A", required=False, found=True, status="warning"),
        ToolCheck(name="B", required=True, found=True, status="pass"),
    ]
    report = DoctorReport(checks=checks)
    assert report.overall == "warning"


def test_doctor_report_overall_pass() -> None:
    """DoctorReport.overall = 'pass' if all checks pass."""
    checks = [
        ToolCheck(name="A", required=True, found=True, status="pass"),
        ToolCheck(name="B", required=False, found=True, status="pass"),
    ]
    report = DoctorReport(checks=checks)
    assert report.overall == "pass"


# ---------------------------------------------------------------------------
# run_doctor
# ---------------------------------------------------------------------------


def test_run_doctor_local_only_minimal_project(tmp_path: Path) -> None:
    """run_doctor() runs without error on a minimal local-only project dir."""
    # Create minimal project structure
    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text("[groundtruth]\ndb_path = 'groundtruth.db'\n", encoding="utf-8")

    report = run_doctor(tmp_path, "local-only")
    assert isinstance(report, DoctorReport)
    assert report.profile == "local-only"
    assert len(report.checks) > 0


def test_run_doctor_does_not_fail_without_groundtruth_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """GOV-19 target (TEST-11199 v3, owner ruling D31, 2026-09-19): ``gt doctor`` must not FAIL without
    ``groundtruth.db``. On a local-only project without a store and without a configured authority the
    retired 'Knowledge DB' check is absent, no check fails because the store is missing, SQLite is never
    opened and no store is created, and native readiness is reported as unverified (warning, found False).
    Per-check assertions only: ``report.overall`` on a bare directory still fails on the unrelated
    hooks/rules checks."""
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text("[groundtruth]\ndb_path = 'groundtruth.db'\n", encoding="utf-8")

    def refuse(*args, **kwargs):
        pytest.fail("run_doctor must not open SQLite")

    monkeypatch.setattr("sqlite3.connect", refuse)

    report = run_doctor(tmp_path, "local-only")

    names = [check.name for check in report.checks]
    assert "Knowledge DB" not in names
    assert not (tmp_path / "groundtruth.db").exists()
    store_failures = [check for check in report.checks if check.status == "fail" and "groundtruth.db" in check.message]
    assert store_failures == [], [(check.name, check.message) for check in store_failures]
    readiness = next(check for check in report.checks if check.name == "Authority readiness")
    assert readiness.status == "warning"
    assert readiness.found is False


# ---------------------------------------------------------------------------
# _check_authority_readiness — GET /v1/status readiness probe (owner ruling D31, 2026-09-19)
# ---------------------------------------------------------------------------


AUTHORITY_URL = "http://127.0.0.1:12345"
SENTINEL = b"Never opened by a doctor check"


@pytest.fixture
def storeless_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A project whose sentinel ``groundtruth.db`` keeps its bytes and whose SQLite is refused."""
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    sentinel = tmp_path / "groundtruth.db"
    sentinel.write_bytes(SENTINEL)

    def refuse(*args, **kwargs):
        pytest.fail("Doctor checks cannot open SQLite")

    monkeypatch.setattr("sqlite3.connect", refuse)
    yield tmp_path
    assert sentinel.read_bytes() == SENTINEL


@pytest.fixture
def configured_authority(storeless_project: Path) -> Path:
    """The storeless project with ``authority_url`` configured; no socket is ever opened."""
    (storeless_project / "groundtruth.toml").write_text(
        f'[groundtruth]\nauthority_url="{AUTHORITY_URL}"\n', encoding="utf-8"
    )
    return storeless_project


def _status_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "reachable": True,
        "ready": True,
        "missing_tables": [],
        "unexpected_tables": [],
        "forbidden_tables": [],
        "forbidden_columns": [],
        "schema_catalog_matches": True,
        "schema_version": 1,
        "postgresql_major_version": 18,
    }
    payload.update(overrides)
    return payload


def _serve_status(monkeypatch: pytest.MonkeyPatch, payload: object, calls: list | None = None) -> None:
    """Serve ``GET /v1/status`` from a dict (or raise it when it is an exception); refuse anything else."""

    def request(self, method, path, *, body=None, query=None):
        if calls is not None:
            calls.append((method, path))
        assert method == "GET" and path == "/v1/status" and body is None, (method, path)
        if isinstance(payload, BaseException):
            raise payload
        return payload

    monkeypatch.setattr(AuthorityClient, "request", request)


def _refuse_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(*args, **kwargs):
        pytest.fail("No authority may be contacted when none is configured")

    monkeypatch.setattr(AuthorityClient, "request", refuse)


@pytest.mark.parametrize("config", ["[groundtruth]\ndb_path = 'groundtruth.db'\n", None], ids=["no-url", "no-toml"])
def test_authority_readiness_not_configured_is_warning(
    storeless_project: Path, monkeypatch: pytest.MonkeyPatch, config: str | None
) -> None:
    if config is not None:
        (storeless_project / "groundtruth.toml").write_text(config, encoding="utf-8")
    _refuse_requests(monkeypatch)

    result = doctor_module._check_authority_readiness(storeless_project)

    assert result.name == "Authority readiness"
    assert result.required is True
    assert result.status == "warning"
    assert result.found is False
    assert "No authority_url is configured" in result.message


def test_authority_readiness_unreachable_is_fail(configured_authority: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _serve_status(monkeypatch, AuthorityClientError("authority_unavailable", "Service unavailable"))

    result = doctor_module._check_authority_readiness(configured_authority)

    assert result.name == "Authority readiness"
    assert result.required is True
    assert result.status == "fail"
    assert result.found is False
    assert result.message.startswith(f"Authority {AUTHORITY_URL} unreachable: authority_unavailable")


def test_authority_readiness_ready_is_pass(configured_authority: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list = []
    _serve_status(monkeypatch, _status_payload(), calls)

    result = doctor_module._check_authority_readiness(configured_authority)

    assert result.name == "Authority readiness"
    assert result.required is True
    assert result.status == "pass"
    assert result.found is True
    assert result.message.startswith(f"Authority {AUTHORITY_URL} ready (schema 1")
    assert "PostgreSQL 18" in result.message
    assert calls == [("GET", "/v1/status")]


def test_authority_readiness_not_ready_is_fail(configured_authority: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _serve_status(
        monkeypatch,
        _status_payload(ready=False, missing_tables=["work_items"], schema_catalog_matches=False),
    )

    result = doctor_module._check_authority_readiness(configured_authority)

    assert result.required is True
    assert result.status == "fail"
    assert result.found is True
    assert result.message.startswith(f"Authority {AUTHORITY_URL} not ready")
    assert "missing_tables=" in result.message
    assert "work_items" in result.message


@pytest.mark.parametrize(
    "payload",
    [["not", "a", "dict"], {"schema_version": 1}, {"ready": "yes"}],
    ids=["list", "no-ready-key", "non-boolean-ready"],
)
def test_authority_readiness_invalid_payload_is_fail(
    configured_authority: Path, monkeypatch: pytest.MonkeyPatch, payload: object
) -> None:
    _serve_status(monkeypatch, payload)

    result = doctor_module._check_authority_readiness(configured_authority)

    assert result.required is True
    assert result.status == "fail"
    assert result.found is True
    assert "invalid status payload" in result.message


# ---------------------------------------------------------------------------
# _check_settings_hook_registration_drift — §B.3 generalized composite check
# Covers gtkb-da-governance-completeness-implementation-015 §B.4 cases 1-5
# plus a back-compat assertion preserving the legacy scanner-safe-writer name.
# ---------------------------------------------------------------------------


def _write_settings_hooks(target: Path, hooks: dict[str, list[dict[str, object]]]) -> None:
    """Write ``.claude/settings.json`` with the given hooks map."""
    settings_dir = target / ".claude"
    settings_dir.mkdir(parents=True, exist_ok=True)
    (settings_dir / "settings.json").write_text(json.dumps({"hooks": hooks}, indent=2) + "\n", encoding="utf-8")


def _touch_hook_file(target: Path, filename: str) -> None:
    """Create an empty authored ``.harness-baseline-configuration/hooks/<filename>`` so the liveness probe passes."""
    hooks_dir = target / ".harness-baseline-configuration" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    (hooks_dir / filename).write_text("# stub\n", encoding="utf-8")


def _hook_entry(filename: str) -> dict[str, object]:
    """Return a canonical hook entry shape referencing the given hook file."""
    return {"hooks": [{"type": "command", "command": f"python .harness-baseline-configuration/hooks/{filename}"}]}


def _get_registration(reg_id: str) -> SettingsHookRegistration:
    """Resolve a registry record as a SettingsHookRegistration (or fail)."""
    record = find_artifact_by_id(reg_id)
    assert isinstance(record, SettingsHookRegistration)
    return record


def test_derive_paired_hook_id_strips_prefix_and_event_suffix() -> None:
    """``_derive_paired_hook_id`` yields the paired ``hook.<short>`` id."""
    assert (
        _derive_paired_hook_id("settings.hook.gov09-capture.userpromptsubmit", "userpromptsubmit")
        == "hook.gov09-capture"
    )
    assert (
        _derive_paired_hook_id("settings.hook.scanner-safe-writer.pretooluse", "pretooluse")
        == "hook.scanner-safe-writer"
    )


def test_settings_hook_registration_present_and_registered_is_pass(tmp_path: Path) -> None:
    """A retained managed command in its declared event passes registration inspection."""
    reg = _get_registration("settings.hook.scanner-safe-writer.pretooluse")
    _touch_hook_file(tmp_path, reg.hook_filename)
    _write_settings_hooks(tmp_path, {reg.event: [_hook_entry(reg.hook_filename)]})
    result = _check_settings_hook_registration_drift(tmp_path, "dual-agent", reg)
    assert result.status == "pass"
    assert reg.event in result.message


def test_run_doctor_local_only_omits_new_settings_checks(tmp_path: Path) -> None:
    """§B.4 case 5 (integration): on ``local-only`` profile the 4 new
    ``settings:`` checks do NOT appear in the report (gated by
    ``p.includes_bridge`` AND by ``doctor_required_profiles`` filter)."""
    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text("[groundtruth]\ndb_path = 'groundtruth.db'\n", encoding="utf-8")
    report = run_doctor(tmp_path, "local-only")
    settings_check_names = [c.name for c in report.checks if c.name.startswith("settings:")]
    assert settings_check_names == [], (
        f"local-only profile must not emit any settings:* checks; got {settings_check_names}"
    )


def test_run_doctor_dual_agent_retains_scanner_safe_writer_check(tmp_path: Path) -> None:
    """§B.4 back-compat assertion: the existing ``scanner-safe-writer`` doctor
    check name is still present in the report for bridge profiles."""
    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text("[groundtruth]\ndb_path = 'groundtruth.db'\n", encoding="utf-8")
    report = run_doctor(tmp_path, "dual-agent")
    names = [c.name for c in report.checks]
    assert "scanner-safe-writer" in names, f"scanner-safe-writer must remain as a distinct check name; got {names}"


@pytest.mark.parametrize(
    "name", ["_check_authority_readiness", "_check_application_scope_alignment", "_check_standing_backlog_health"]
)
def test_native_reader_honors_environment_without_toml(tmp_path, monkeypatch, name):
    monkeypatch.setenv("GT_AUTHORITY_URL", AUTHORITY_URL)
    calls = []

    def request(self, method, path, *, body=None, query=None):
        calls.append(path)
        assert self.url == AUTHORITY_URL and method == "GET" and body is None
        if path == "/v1/status":
            return _status_payload()
        if path == "/v1/bridge/state-report":
            return {"attempts": []}
        return {"records": [], "next_after": None}

    monkeypatch.setattr(AuthorityClient, "request", request)
    result = getattr(doctor_module, name)(tmp_path)
    assert result.status == "pass", result.message
    assert calls
    assert not (tmp_path / "groundtruth.toml").exists()


@pytest.mark.parametrize(
    "name", ["_check_authority_readiness", "_check_application_scope_alignment", "_check_standing_backlog_health"]
)
@pytest.mark.parametrize("bad_config", ["invalid-toml", "directory", "unreadable"])
def test_native_reader_configuration_error_is_failure(tmp_path, monkeypatch, name, bad_config):
    from groundtruth_kb.config import GTConfig, GTConfigError

    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    config = tmp_path / "groundtruth.toml"
    if bad_config == "directory":
        config.mkdir()
    elif bad_config == "invalid-toml":
        config.write_text("[groundtruth\n", encoding="utf-8")
    else:
        config.write_text("[groundtruth]\n", encoding="utf-8")

        def unreadable(*args, **kwargs):
            raise GTConfigError("Cannot read config: permission denied")

        monkeypatch.setattr(GTConfig, "load", unreadable)
    _refuse_requests(monkeypatch)
    result = getattr(doctor_module, name)(tmp_path)
    assert result.status == "fail", result.message
    assert "configuration invalid" in result.message.lower()
    assert "No authority_url is configured" not in result.message
