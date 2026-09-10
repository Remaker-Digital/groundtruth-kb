"""Provider-local configuration and host diagnostics preserve native authority boundaries."""

from __future__ import annotations

import io
import sys
import urllib.error

import pytest

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.project import doctor


@pytest.fixture(autouse=True)
def no_legacy_authority(monkeypatch):
    def refuse(*args, **kwargs):
        pytest.fail("Provider diagnostics must not consult SQLite or legacy harness state")

    monkeypatch.setattr("sqlite3.connect", refuse)
    monkeypatch.setattr("groundtruth_kb.harness_projection.read_roles", refuse)
    monkeypatch.setattr("groundtruth_kb.harness_projection.read_identity", refuse)
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    monkeypatch.delenv("GTKB_DOCTOR_OLLAMA_SKIP_PROBE", raising=False)
    monkeypatch.delenv("GTKB_DOCTOR_OLLAMA_SKIP_HOST_READINESS", raising=False)


def routing(root, provider="ollama", content=None):
    path = root / ".api-harness" / provider / "routing.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        content
        or (
            'schema_version=1\n[models.fixture]\nmodel_id="model:tag"\n'
            f'provider="{provider}"\ntool_calling_supported=true\n'
            'allowed_tools=["Read","Write","Edit","Grep","Glob","Bash"]\n'
            f'[routing.{provider}]\ndefault_model="fixture"\n'
        ),
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize("provider", ["ollama", "openrouter", "alibaba-cloud-studio"])
def test_provider_routing_reads_own_projection_and_preserves_foreign_bytes(tmp_path, provider):
    routing(tmp_path, provider)
    poisoned = tmp_path / ".api-harness/routing.toml"
    poisoned.write_bytes(b"unreadable old shared catalog \xff")
    peer = tmp_path / ".claude/settings.json"
    peer.parent.mkdir()
    peer.write_bytes(b"unreadable peer configuration \xff")
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    timestamps = {p: p.stat().st_mtime_ns for p in before}
    result = doctor._check_provider_routing(tmp_path, provider)
    assert result.status == "pass", result.message
    assert "qualification are separate" in result.message
    assert doctor._check_provider_routing(tmp_path, provider) == result
    assert {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before
    assert {p: p.stat().st_mtime_ns for p in before} == timestamps
    assert not (tmp_path / "groundtruth.db").exists()
    assert not (tmp_path / "harness-state").exists()


@pytest.mark.parametrize("provider", ["ollama", "openrouter", "alibaba-cloud-studio"])
def test_absent_provider_is_inapplicable_but_partial_installation_is_unverified(tmp_path, provider):
    assert doctor._check_provider_routing(tmp_path, provider).status == "info"
    (tmp_path / ".api-harness" / provider).mkdir(parents=True)
    result = doctor._check_provider_routing(tmp_path, provider)
    assert result.status == "warning" and "missing" in result.message


@pytest.mark.parametrize(
    "change",
    [
        "syntax",
        "schema",
        "no_models",
        "foreign_provider",
        "missing_id",
        "no_tools",
        "unknown_tool",
        "not_tool_calling",
        "missing_default",
        "peer_routing",
    ],
)
def test_invalid_provider_routing_is_not_a_pass(tmp_path, change):
    path = routing(tmp_path)
    text = path.read_text()
    replacements = {
        "syntax": ("schema_version=1", "[unclosed"),
        "schema": ("schema_version=1", "schema_version=2"),
        "no_models": ("[models.fixture]", "[other.fixture]"),
        "foreign_provider": ('provider="ollama"', 'provider="peer"'),
        "missing_id": ('model_id="model:tag"', 'model_id=""'),
        "no_tools": ('allowed_tools=["Read","Write","Edit","Grep","Glob","Bash"]', "allowed_tools=[]"),
        "unknown_tool": ('"Bash"', '"UnknownTool"'),
        "not_tool_calling": ("tool_calling_supported=true", "tool_calling_supported=false"),
        "missing_default": ('default_model="fixture"', 'default_model="missing"'),
        "peer_routing": ('default_model="fixture"', 'default_model="fixture"\n[routing.peer]\ndefault_model="fixture"'),
    }
    path.write_text(text.replace(*replacements[change]), encoding="utf-8")
    result = doctor._check_provider_routing(tmp_path, "ollama")
    assert result.status == "fail", result.message


@pytest.fixture
def local_host(tmp_path, monkeypatch):
    routing(tmp_path)
    (tmp_path / "groundtruth.toml").write_text('[groundtruth]\nauthority_url="http://127.0.0.1:12345"\n')
    installation = {
        "id": "ANY-ID",
        "harness_name": "ollama",
        "status": "active",
        "invocation_surfaces": {"headless": {"argv": [sys.executable, "scripts/ollama_harness.py"]}},
    }
    calls = []

    def request(self, method, path, **kwargs):
        calls.append((method, path, kwargs))
        return {"records": [installation], "next_after": None}

    monkeypatch.setattr(AuthorityClient, "request", request)
    monkeypatch.setattr(doctor, "_ollama_windows_autostart_finding", lambda: None)
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **kw: io.BytesIO(b'{"models":[{"name":"model:tag"}]}'))
    return tmp_path, installation, calls


def test_local_model_and_host_readiness_uses_current_installation_without_fixed_identity(local_host):
    root, _, calls = local_host
    result = doctor._check_ollama_harness(root)
    assert result.status == "pass", result.message
    assert "actual agent execution is unverified" in result.message
    assert calls[0][:2] == ("GET", "/v1/harnesses")
    assert not (root / "groundtruth.db").exists()


@pytest.mark.parametrize("body", [b'{"models":[]}', b"[]", b'{"models":[null]}', b"not JSON", b"\xff"])
def test_missing_or_malformed_local_model_inventory_is_unverified(local_host, monkeypatch, body):
    root, _, _ = local_host
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **kw: io.BytesIO(body))
    result = doctor._check_ollama_harness(root)
    assert result.status == "warning", result.message


def test_unreachable_model_inventory_is_not_silently_skipped(local_host, monkeypatch):
    def unavailable(*args, **kwargs):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr("urllib.request.urlopen", unavailable)
    result = doctor._check_ollama_harness(local_host[0])
    assert result.status == "warning" and "unavailable" in result.message


@pytest.mark.parametrize(
    "endpoint", ["https://remote.invalid", "http://owner:secret@localhost:11434", "http://localhost:invalid", ""]
)
def test_nonlocal_or_invalid_endpoint_never_substitutes_local_host(local_host, monkeypatch, endpoint):
    root, installation, _ = local_host
    installation["invocation_surfaces"]["headless"]["argv"] += ["--endpoint", endpoint]

    def refuse(*args, **kwargs):
        pytest.fail("No request or local autostart probe is allowed for this endpoint")

    monkeypatch.setattr("urllib.request.urlopen", refuse)
    monkeypatch.setattr(doctor, "_ollama_windows_autostart_finding", refuse)
    result = doctor._check_ollama_harness(root)
    assert result.status in {"fail", "warning"} and "secret" not in result.message


@pytest.mark.parametrize("setting", ["GTKB_DOCTOR_OLLAMA_SKIP_PROBE", "GTKB_DOCTOR_OLLAMA_SKIP_HOST_READINESS"])
def test_skipped_readiness_probe_cannot_report_pass(local_host, monkeypatch, setting):
    monkeypatch.setenv(setting, "1")
    result = doctor._check_ollama_harness(local_host[0])
    assert result.status == "warning" and "skipped" in result.message.lower()


def test_unavailable_canonical_metadata_does_not_use_files_or_open_sqlite(local_host, monkeypatch):
    def unavailable(*args, **kwargs):
        raise AuthorityClientError("authority_unavailable", "Service unavailable")

    monkeypatch.setattr(AuthorityClient, "request", unavailable)
    result = doctor._check_ollama_harness(local_host[0])
    assert result.status == "warning" and "metadata unavailable" in result.message


def test_missing_autostart_is_a_diagnostic_without_starting_services(local_host, monkeypatch):
    monkeypatch.setattr(doctor, "_ollama_windows_autostart_finding", lambda: "Ollama autostart not detected")
    result = doctor._check_ollama_harness(local_host[0])
    assert result.status == "warning" and "autostart not detected" in result.message


def test_windows_autostart_probe_is_hidden_read_only_and_noninteractive(monkeypatch):
    monkeypatch.setattr(doctor.sys, "platform", "win32")
    monkeypatch.setattr(doctor.shutil, "which", lambda name: "powershell.exe")
    calls = []

    def run(args, **kwargs):
        calls.append((args, kwargs))
        return doctor.subprocess.CompletedProcess(args, 0, '{"scheduled_tasks":[],"services":[]}', "")

    monkeypatch.setattr(doctor.subprocess, "run", run)
    assert "autostart not detected" in doctor._ollama_windows_autostart_finding()
    args, kwargs = calls[0]
    assert "-NonInteractive" in args and kwargs["stdin"] == doctor.subprocess.DEVNULL
    assert "Get-ScheduledTask" in args[-1] and "Get-Service" in args[-1]
    assert "Start-" not in args[-1] and "Register-" not in args[-1]
    if doctor.os.name == "nt":
        assert kwargs["creationflags"] == doctor.subprocess.CREATE_NO_WINDOW
