"""Run rollback control flow offline; every external operation is a shell substitute."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import httpx
import pytest

from scripts.windows_subprocess import no_window_subprocess_kwargs

ROOT = Path(__file__).resolve().parents[2]
REGRESSION = ROOT / "applications/Agent_Red/tests/regression/test_upgrade_regression.py"
REGRESSION_CONFTEST = ROOT / "applications/Agent_Red/tests/regression/conftest.py"
PASS = '<testsuites><testsuite><testcase name="pass"/></testsuite></testsuites>'
WRAPPER = r"""
function Record-Call($name, $arguments) {
    $row = @{ name=$name; arguments=@($arguments); cwd=(Get-Location).Path }
    [IO.File]::AppendAllText($env:CASE_TRACE, (ConvertTo-Json $row -Compress) + "`n")
}
function global:az {
    $a = @($args | ForEach-Object { [string]$_ })
    Record-Call 'az' $a
    $global:LASTEXITCODE = 0
    switch -Wildcard (($a | Select-Object -First 3) -join ' ') {
        'acr repository show-tags' { 'v1'; return }
        'containerapp update *' {
            if ($env:CASE_NAME -eq 'update-failed') { $global:LASTEXITCODE = 9 }
            'rollback-revision'; return
        }
        'containerapp show *' {
            $state = @{ latest='rollback-revision'; ready='rollback-revision'; image='acragentredeastus.azurecr.io/api-gateway:v1' }
            if ($env:CASE_NAME -eq 'changed-revision') { $state.latest = 'other' }
            if ($env:CASE_NAME -eq 'changed-image-case') { $state.image = $state.image.Replace(':v', ':V') }
            ConvertTo-Json $state -Compress; return
        }
        'containerapp revision list' {
            if ($env:CASE_NAME -eq 'absent-revision') { '["old-a","old-b"]' }
            else { '["old-a","rollback-revision","old-b"]' }
            return
        }
        'containerapp revision deactivate' {
            if ($env:CASE_NAME -eq 'deactivation-failed') { $global:LASTEXITCODE = 9 }
            return
        }
        default { throw "Unexpected az command: $($a -join ' ')" }
    }
}
function global:python {
    $a = @($args | ForEach-Object { [string]$_ })
    Record-Call 'python' $a
    $reports = @($a | Where-Object { $_ -like '--junitxml=*' })
    if ($reports.Count -ne 1) { throw 'Missing unique report path' }
    if ($env:CASE_NAME -ne 'missing-report') {
        [IO.File]::WriteAllText($reports[0].Substring(11), [string]$env:CASE_XML)
    }
    $global:LASTEXITCODE = if ($env:CASE_NAME -eq 'pytest-failed') { 2 } else { 0 }
}
function global:Invoke-WebRequest {
    [CmdletBinding()]
    param([string]$Uri, [int]$TimeoutSec, [switch]$UseBasicParsing)
    Record-Call 'http' @($Uri)
    if ($Uri -ne 'https://rollback.invalid/health') { throw "Unexpected URL: $Uri" }
    if ($env:CASE_NAME -eq 'unhealthy') { throw 'Offline health failure' }
    [pscustomobject]@{ StatusCode=200 }
}
function global:Start-Sleep { param([int]$Seconds) }
try { & $env:CASE_SCRIPT -Version 'v1'; exit $LASTEXITCODE }
catch { Write-Error $_; exit 99 }
"""


def run_rollback(tmp_path, case, report=PASS):
    shell = shutil.which("powershell") or shutil.which("pwsh")
    if shell is None:
        pytest.skip("PowerShell is required for rollback control-flow tests")
    script = tmp_path / "scripts/deploy/rollback.ps1"
    script.parent.mkdir(parents=True)
    script.write_bytes((ROOT / "scripts/deploy/rollback.ps1").read_bytes())
    app = tmp_path / "applications/Agent_Red"
    regression = app / "tests/regression/test_upgrade_regression.py"
    regression.parent.mkdir(parents=True)
    if case != "missing-regression":
        regression.write_text("# Not executed\n", encoding="utf-8")
    if case != "missing-config":
        (tmp_path / "pyproject.toml").write_text("[tool.pytest.ini_options]\n", encoding="utf-8")
    wrapper, trace = tmp_path / "invoke.ps1", tmp_path / "calls.jsonl"
    wrapper.write_text(WRAPPER, encoding="utf-8-sig")
    env = {
        k: os.environ[k]
        for k in ("SystemRoot", "WINDIR", "COMSPEC", "TEMP", "TMP", "USERPROFILE", "PSModulePath")
        if k in os.environ
    }
    env.update(
        PATH="",
        PROD_URL="https://rollback.invalid",
        CASE_SCRIPT=str(script),
        CASE_TRACE=str(trace),
        CASE_NAME=case,
        CASE_XML=report,
    )
    args = [shell, "-NoLogo", "-NoProfile", "-NonInteractive"]
    if Path(shell).name.lower() == "powershell.exe":
        args += ["-ExecutionPolicy", "Bypass"]
    result = subprocess.run(
        [*args, "-File", str(wrapper)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=20,
        **no_window_subprocess_kwargs(),
    )
    calls = [json.loads(line) for line in trace.read_text(encoding="utf-8-sig").splitlines()] if trace.exists() else []
    return result, calls, app


def deactivations(calls):
    return [
        call["arguments"][call["arguments"].index("--revision") + 1]
        for call in calls
        if call["name"] == "az" and call["arguments"][:3] == ["containerapp", "revision", "deactivate"]
    ]


def test_rollback_preserves_captured_revision_and_runs_application_regression(tmp_path):
    result, calls, app = run_rollback(tmp_path, "success")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ROLLBACK COMPLETE" in result.stdout
    assert deactivations(calls) == ["old-a", "old-b"]
    run = next(call for call in calls if call["name"] == "python")
    assert run["arguments"][:3] == ["-m", "pytest", "-c"]
    assert Path(run["arguments"][3]) == tmp_path / "pyproject.toml"
    assert Path(run["arguments"][4]) == app / "tests/regression/test_upgrade_regression.py"
    assert Path(run["cwd"]) == app
    assert not list(app.glob(".rollback-regression-*.xml"))


@pytest.mark.parametrize(
    "case,report",
    [
        ("missing-regression", PASS),
        ("missing-config", PASS),
        ("update-failed", PASS),
        ("unhealthy", PASS),
        ("pytest-failed", PASS),
        ("missing-report", ""),
        ("empty-report", ""),
        ("malformed-report", "<testsuites>"),
        ("zero-cases", "<testsuites/>"),
        ("all-skipped", "<testsuites><testsuite><testcase><skipped/></testcase></testsuite></testsuites>"),
        ("mixed-skipped", PASS.replace("</testsuite>", '<testcase name="required"><skipped/></testcase></testsuite>')),
        ("failure-report", PASS.replace('<testcase name="pass"/>', "<testcase><failure/></testcase>")),
        ("error-report", PASS.replace('<testcase name="pass"/>', "<testcase><error/></testcase>")),
        ("changed-revision", PASS),
        ("changed-image-case", PASS),
        ("absent-revision", PASS),
        ("deactivation-failed", PASS),
    ],
)
def test_rollback_failure_stops_cleanup_and_success_claim(tmp_path, case, report):
    result, calls, app = run_rollback(tmp_path, case, report)
    assert result.returncode != 0, result.stdout + result.stderr
    assert "ROLLBACK COMPLETE" not in result.stdout + result.stderr
    if case not in {"missing-regression", "missing-config"}:
        assert calls, result.stdout + result.stderr
    assert deactivations(calls) == (["old-a"] if case == "deactivation-failed" else [])
    if case in {"missing-regression", "missing-config"}:
        assert calls == []
    if case in {"update-failed", "unhealthy"}:
        assert not any(call["name"] == "python" for call in calls)
    assert not list(app.glob(".rollback-regression-*.xml"))


# ---------------------------------------------------------------------------
# The Tier 0 assertions the rollback relies on, exercised offline against the
# ACTUAL regression methods with synthetic responses (no live endpoint).
# ---------------------------------------------------------------------------


def tier0_module():
    spec = importlib.util.spec_from_file_location("agent_red_upgrade_regression", REGRESSION)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class RecordingClient:
    """Answer each request with the next synthetic response and record what the check asked for."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def _answer(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        assert self.responses, f"unexpected {method} {path}"
        return self.responses.pop(0)

    def get(self, path, **kwargs):
        return self._answer("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self._answer("POST", path, **kwargs)


def response(status, json=None, *, content=None, headers=None):
    request = httpx.Request("GET", "https://rollback.invalid/")
    return httpx.Response(status, json=json, content=content, headers=headers, request=request)


def html(title, status=200):
    return response(
        status,
        content=f"<!doctype html><html><head><title>{title}</title></head></html>".encode(),
        headers={"content-type": "text/html; charset=utf-8"},
    )


READY = {
    "status": "ready",
    "agntcy_sdk": {"transport_active": True, "active_tier": "nats"},
    "cosmos_db": {"status": "healthy"},
    "circuit_breakers": {
        "healthy": False,
        "any_open": False,
        "services": {"stripe": {"state": "closed"}, "cosmos": {"state": "half_open"}},
    },
}
HEALTH = {"status": "healthy", "version": "1.0.0", "product_version": "1.1.0"}
CONVERSATION = {
    "conversation_id": "conv-1",
    "stream_url": "/api/chat/stream/conv-1",
    "ws_url": "/ws/conv-1",
    "created_at": "2026-09-20T00:00:00Z",
}
OPENAPI = {"openapi": "3.1.0", "info": {"title": "Agent Red"}, "paths": {"/health": {}, "/ready": {}}}
CHECKOUT_REFUSAL = {
    "detail": [
        {"type": "missing", "loc": ["body", "tier"], "msg": "Field required"},
        {"type": "missing", "loc": ["body", "interval"], "msg": "Field required"},
    ]
}
WIDGET_HEADERS = {"X-Widget-Key": "offline"}


def nested(base, **changes):
    result = json.loads(json.dumps(base))
    for path, value in changes.items():
        target = result
        *parents, leaf = path.split("__")
        for key in parents:
            target = target[key]
        target[leaf] = value
    return result


def outcome(check, client, *fixtures):
    try:
        check(client, *fixtures)
    except Exception as error:  # a failing Tier 0 check may raise assertion, key or type errors
        return error
    return None


TIER0_CASES = [
    ("t0_01 pass", "TestTier0Health", "test_t0_01_health_endpoint_returns_200", [response(200, HEALTH)], True),
    (
        "t0_01 blank version",
        "TestTier0Health",
        "test_t0_01_health_endpoint_returns_200",
        [response(200, {"status": "healthy", "version": ""})],
        False,
    ),
    ("t0_02 pass", "TestTier0Health", "test_t0_02_ready_endpoint_returns_200", [response(200, READY)], True),
    (
        "t0_02 503 not ready",
        "TestTier0Health",
        "test_t0_02_ready_endpoint_returns_200",
        [response(503, nested(READY, status="not_ready", agntcy_sdk__transport_active=False))],
        False,
    ),
    (
        "t0_02 inactive transport",
        "TestTier0Health",
        "test_t0_02_ready_endpoint_returns_200",
        [response(200, nested(READY, agntcy_sdk__transport_active=False))],
        False,
    ),
    (
        "t0_02 unhealthy cosmos",
        "TestTier0Health",
        "test_t0_02_ready_endpoint_returns_200",
        [response(200, nested(READY, cosmos_db__status="unhealthy"))],
        False,
    ),
    (
        "t0_02 fallback cosmos",
        "TestTier0Health",
        "test_t0_02_ready_endpoint_returns_200",
        [response(200, nested(READY, cosmos_db__status="healthy_fallback", agntcy_sdk__active_tier="slim"))],
        True,
    ),
    (
        "t0_03 pass with half_open",
        "TestTier0Health",
        "test_t0_03_circuit_breakers_not_open",
        [response(200, READY)],
        True,
    ),
    (
        "t0_03 open breaker",
        "TestTier0Health",
        "test_t0_03_circuit_breakers_not_open",
        [
            response(
                200,
                nested(
                    READY, circuit_breakers__any_open=True, circuit_breakers__services={"stripe": {"state": "open"}}
                ),
            )
        ],
        False,
    ),
    (
        "t0_03 open state under stale flag",
        "TestTier0Health",
        "test_t0_03_circuit_breakers_not_open",
        [response(200, nested(READY, circuit_breakers__services={"stripe": {"state": "open"}}))],
        False,
    ),
    (
        "t0_03 no breakers",
        "TestTier0Health",
        "test_t0_03_circuit_breakers_not_open",
        [response(200, nested(READY, circuit_breakers__services={}))],
        False,
    ),
    (
        "t0_03 flat legacy structure",
        "TestTier0Health",
        "test_t0_03_circuit_breakers_not_open",
        [response(200, nested(READY, circuit_breakers={"stripe": "OPEN"}))],
        False,
    ),
    (
        "t0_04 pass",
        "TestTier0Health",
        "test_t0_04_api_version_header",
        [response(200, HEALTH, headers={"x-api-version": "1.0.0"})],
        True,
    ),
    ("t0_04 missing header", "TestTier0Health", "test_t0_04_api_version_header", [response(200, HEALTH)], False),
    (
        "t0_04 mismatched header",
        "TestTier0Health",
        "test_t0_04_api_version_header",
        [response(200, HEALTH, headers={"x-api-version": "0.9.0"})],
        False,
    ),
    (
        "t0_05 pass",
        "TestTier0Health",
        "test_t0_05_security_headers_present",
        [response(200, HEALTH, headers={"x-content-type-options": "nosniff"})],
        True,
    ),
    (
        "t0_05 error with header",
        "TestTier0Health",
        "test_t0_05_security_headers_present",
        [response(500, {"detail": "boom"}, headers={"x-content-type-options": "nosniff"})],
        False,
    ),
    (
        "t0_06 pass",
        "TestTier0Auth",
        "test_t0_06_protected_endpoints_require_auth",
        [response(401, {}), response(403, {}), response(401, {}), response(401, {})],
        True,
    ),
    (
        "t0_06 open endpoint",
        "TestTier0Auth",
        "test_t0_06_protected_endpoints_require_auth",
        [response(401, {}), response(200, {}), response(401, {}), response(401, {})],
        False,
    ),
    (
        "t0_07 pass",
        "TestTier0Auth",
        "test_t0_07_public_endpoints_accessible",
        [response(200, HEALTH), response(200, READY)],
        True,
    ),
    (
        "t0_07 not ready",
        "TestTier0Auth",
        "test_t0_07_public_endpoints_accessible",
        [response(200, HEALTH), response(503, nested(READY, status="not_ready"))],
        False,
    ),
    ("t0_08 pass", "TestTier0Auth", "test_t0_08_widget_key_auth_works", [response(201, CONVERSATION)], True),
    (
        "t0_08 503",
        "TestTier0Auth",
        "test_t0_08_widget_key_auth_works",
        [response(503, {"detail": "Chat service not initialized"})],
        False,
    ),
    (
        "t0_08 500",
        "TestTier0Auth",
        "test_t0_08_widget_key_auth_works",
        [response(500, {"detail": "Internal Server Error"})],
        False,
    ),
    (
        "t0_08 200 not created",
        "TestTier0Auth",
        "test_t0_08_widget_key_auth_works",
        [response(200, CONVERSATION)],
        False,
    ),
    (
        "t0_08 missing stream_url",
        "TestTier0Auth",
        "test_t0_08_widget_key_auth_works",
        [response(201, nested(CONVERSATION, stream_url=""))],
        False,
    ),
    ("t0_09 pass 401", "TestTier0Auth", "test_t0_09_invalid_auth_rejected", [response(401, {})], True),
    ("t0_09 pass 403", "TestTier0Auth", "test_t0_09_invalid_auth_rejected", [response(403, {})], True),
    ("t0_09 accepted", "TestTier0Auth", "test_t0_09_invalid_auth_rejected", [response(200, {})], False),
    (
        "t0_10 invalid signature",
        "TestTier0Auth",
        "test_t0_10_webhook_endpoint_reachable",
        [response(400, {"detail": "Invalid signature."})],
        True,
    ),
    (
        "t0_10 invalid payload",
        "TestTier0Auth",
        "test_t0_10_webhook_endpoint_reachable",
        [response(400, {"detail": "Invalid payload."})],
        True,
    ),
    (
        "t0_10 ip allowlist",
        "TestTier0Auth",
        "test_t0_10_webhook_endpoint_reachable",
        [response(403, {"detail": "Webhook source IP not in allowlist."})],
        True,
    ),
    (
        "t0_10 secret not configured",
        "TestTier0Auth",
        "test_t0_10_webhook_endpoint_reachable",
        [response(500, {"detail": "Webhook secret not configured."})],
        False,
    ),
    (
        "t0_10 foreign 401",
        "TestTier0Auth",
        "test_t0_10_webhook_endpoint_reachable",
        [response(401, {"detail": "Unauthorized"})],
        False,
    ),
    (
        "t0_10 foreign 400",
        "TestTier0Auth",
        "test_t0_10_webhook_endpoint_reachable",
        [response(400, {"detail": "Bad Request"})],
        False,
    ),
    (
        "t0_11 pass",
        "TestTier0StaticAssets",
        "test_t0_11_widget_js_served",
        [
            response(
                200,
                content=b"(function(){" + b"x" * 2000 + b"})();",
                headers={"content-type": "application/javascript; charset=utf-8"},
            )
        ],
        True,
    ),
    (
        "t0_11 html masquerade",
        "TestTier0StaticAssets",
        "test_t0_11_widget_js_served",
        [
            response(
                200,
                content=b"<!doctype html><html>" + b"x" * 2000 + b"</html>",
                headers={"content-type": "text/html; charset=utf-8"},
            )
        ],
        False,
    ),
    (
        "t0_11 html as javascript",
        "TestTier0StaticAssets",
        "test_t0_11_widget_js_served",
        [
            response(
                200,
                content=b"<!doctype html><html>" + b"x" * 2000 + b"</html>",
                headers={"content-type": "application/javascript"},
            )
        ],
        False,
    ),
    (
        "t0_11 tiny",
        "TestTier0StaticAssets",
        "test_t0_11_widget_js_served",
        [response(200, content=b"var x=1;", headers={"content-type": "application/javascript"})],
        False,
    ),
    (
        "t0_12 sign in",
        "TestTier0StaticAssets",
        "test_t0_12_standalone_admin_login_page",
        [html("Agent Red — Sign In")],
        True,
    ),
    (
        "t0_12 admin",
        "TestTier0StaticAssets",
        "test_t0_12_standalone_admin_login_page",
        [html("Agent Red — Admin")],
        True,
    ),
    (
        "t0_12 other page",
        "TestTier0StaticAssets",
        "test_t0_12_standalone_admin_login_page",
        [html("Agent Red — Invalid Link")],
        False,
    ),
    ("t0_13 admin", "TestTier0StaticAssets", "test_t0_13_shopify_admin_served", [html("Agent Red — Admin")], True),
    (
        "t0_13 sign in is not the shopify admin",
        "TestTier0StaticAssets",
        "test_t0_13_shopify_admin_served",
        [html("Agent Red — Sign In")],
        False,
    ),
    (
        "t0_13b provider",
        "TestTier0StaticAssets",
        "test_t0_13b_provider_admin_served",
        [html("Agent Red — Service Provider Console")],
        True,
    ),
    (
        "t0_13b admin is not the provider console",
        "TestTier0StaticAssets",
        "test_t0_13b_provider_admin_served",
        [html("Agent Red — Admin")],
        False,
    ),
    ("t0_14 pass", "TestTier0StaticAssets", "test_t0_14_openapi_schema_accessible", [response(200, OPENAPI)], True),
    (
        "t0_14 no application paths",
        "TestTier0StaticAssets",
        "test_t0_14_openapi_schema_accessible",
        [response(200, nested(OPENAPI, paths={}))],
        False,
    ),
    ("t0_14 html", "TestTier0StaticAssets", "test_t0_14_openapi_schema_accessible", [html("Agent Red — Admin")], False),
    (
        "t0_15 not found",
        "TestTier0TenantLookup",
        "test_t0_15_tenant_lookup_endpoint",
        [response(200, {"found": False})],
        True,
    ),
    (
        "t0_15 found",
        "TestTier0TenantLookup",
        "test_t0_15_tenant_lookup_endpoint",
        [response(200, {"found": True, "tenant_id": "tenant-1"})],
        True,
    ),
    (
        "t0_15 404",
        "TestTier0TenantLookup",
        "test_t0_15_tenant_lookup_endpoint",
        [response(404, {"detail": "Not Found"})],
        False,
    ),
    (
        "t0_15 found without tenant",
        "TestTier0TenantLookup",
        "test_t0_15_tenant_lookup_endpoint",
        [response(200, {"found": True, "tenant_id": None})],
        False,
    ),
    (
        "t0_16 pass",
        "TestTier0TenantLookup",
        "test_t0_16_tenant_lookup_returns_json",
        [response(200, {"found": False})],
        True,
    ),
    (
        "t0_16 non-200 is not a pass",
        "TestTier0TenantLookup",
        "test_t0_16_tenant_lookup_returns_json",
        [response(500, {"detail": "boom"})],
        False,
    ),
    (
        "t0_16 non-boolean found",
        "TestTier0TenantLookup",
        "test_t0_16_tenant_lookup_returns_json",
        [response(200, {"found": "yes"})],
        False,
    ),
    (
        "t0_17 pass",
        "TestTier0TenantLookup",
        "test_t0_17_checkout_endpoint_reachable",
        [response(422, CHECKOUT_REFUSAL)],
        True,
    ),
    (
        "t0_17 session created",
        "TestTier0TenantLookup",
        "test_t0_17_checkout_endpoint_reachable",
        [response(200, {"checkout_url": "https://checkout.stripe.invalid/s", "session_id": "cs_test"})],
        False,
    ),
    (
        "t0_17 partial validation",
        "TestTier0TenantLookup",
        "test_t0_17_checkout_endpoint_reachable",
        [response(422, {"detail": CHECKOUT_REFUSAL["detail"][:1]})],
        False,
    ),
    (
        "t0_17 500",
        "TestTier0TenantLookup",
        "test_t0_17_checkout_endpoint_reachable",
        [response(500, {"detail": "boom"})],
        False,
    ),
]


@pytest.mark.parametrize("label,class_name,method,responses,passes", TIER0_CASES, ids=[c[0] for c in TIER0_CASES])
def test_tier0_assertions_accept_only_a_working_deployment(label, class_name, method, responses, passes):
    module = tier0_module()
    check = getattr(getattr(module, class_name)(), method)
    client = RecordingClient(*responses)
    fixtures = (WIDGET_HEADERS,) if method == "test_t0_08_widget_key_auth_works" else ()
    error = outcome(check, client, *fixtures)
    if passes:
        assert error is None, f"{label}: {error!r}"
        assert not client.responses, f"{label}: {len(client.responses)} synthetic responses were never consumed"
    else:
        assert error is not None, f"{label}: a non-working deployment was accepted"


def test_tier0_checkout_probe_sends_a_deliberately_invalid_body():
    module = tier0_module()
    client = RecordingClient(response(422, CHECKOUT_REFUSAL))
    module.TestTier0TenantLookup().test_t0_17_checkout_endpoint_reachable(client)
    assert client.calls == [("POST", "/api/checkout/session", {"json": {}})]


def test_tier0_webhook_probe_posts_an_unsigned_payload():
    module = tier0_module()
    client = RecordingClient(response(400, {"detail": "Invalid signature."}))
    module.TestTier0Auth().test_t0_10_webhook_endpoint_reachable(client)
    ((method, path, kwargs),) = client.calls
    assert (method, path, kwargs["content"]) == ("POST", "/api/webhooks/stripe", b"{}")
    assert "stripe-signature" not in {k.lower() for k in kwargs["headers"]}


def test_regression_conftest_selects_the_application_env_file(tmp_path):
    """The copied conftest loads <application root>/.env.local; inherited values keep precedence."""
    conftest = tmp_path / "applications/Agent_Red/tests/regression/conftest.py"
    conftest.parent.mkdir(parents=True)
    conftest.write_bytes(REGRESSION_CONFTEST.read_bytes())
    (tmp_path / "applications/Agent_Red/.env.local").write_text(
        "ROLLBACK_OFFLINE_PROBE=application\nROLLBACK_OFFLINE_INHERITED=file\n", encoding="utf-8"
    )
    (tmp_path / ".env.local").write_text("ROLLBACK_OFFLINE_PROBE=platform\n", encoding="utf-8")
    program = (
        "import json, os, runpy, sys\n"
        f"runpy.run_path({str(conftest)!r}, run_name='regression_conftest')\n"
        "print(json.dumps({k: os.environ.get(k) for k in ('ROLLBACK_OFFLINE_PROBE', 'ROLLBACK_OFFLINE_INHERITED')}))\n"
    )
    env = {k: v for k, v in os.environ.items() if not k.startswith(("ROLLBACK_OFFLINE_", "PROD_URL"))}
    env.update(PYTHONPATH=str(ROOT), PYTHONDONTWRITEBYTECODE="1", ROLLBACK_OFFLINE_INHERITED="inherited")
    result = subprocess.run(
        [sys.executable, "-P", "-c", program],
        cwd=conftest.parent,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        **no_window_subprocess_kwargs(),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout.strip().splitlines()[-1]) == {
        "ROLLBACK_OFFLINE_PROBE": "application",
        "ROLLBACK_OFFLINE_INHERITED": "inherited",
    }
