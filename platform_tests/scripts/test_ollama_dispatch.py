from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import ollama_harness
from scripts import verify_ollama_dispatch as verify

OLLAMA_MODEL_ID = "fixture-review:current"
# c123 (batch design WP2 2.1): D's corrected registration (step 3). It binds with --init, carries the bridge target and
# names exactly one --model; it has no role skill and no role-named tag. The routing default is another row, so a
# route check that resolved the default instead of the registered --model would fail these tests.
D_MODEL_ROUTE = "deepseek-v4-flash-cloud"
D_ARGV = [
    "groundtruth-kb/.venv/Scripts/python.exe",
    "scripts/ollama_harness.py",
    "--init",
    "{{INIT_LINE}}",
    "--bridge-document",
    "{{DOCUMENT}}",
    "--bridge-version",
    "{{VERSION}}",
    "--report",
    "{{REPORT}}",
    "-p",
    "{{PROMPT}}",
    "--model",
    D_MODEL_ROUTE,
]
OLLAMA_SURFACES = {"dispatch": {"dispatch_tags": ["low-cost"]}, "headless": {"argv": D_ARGV}}


def _ollama_record(
    *,
    status: str = "registered",
    surfaces: dict | None = None,
    event_driven_hooks: bool = True,
) -> dict:
    # c123 (batch design WP2 2.1): a registration names no role, so the record carries no role field.
    return {
        "id": "D",
        "harness_name": "ollama",
        "harness_type": "ollama",
        "status": status,
        "event_driven_hooks": event_driven_hooks,
        "invocation_surfaces": OLLAMA_SURFACES if surfaces is None else surfaces,
    }


def _write_routing(root: Path, *, allowed_tools: list[str] | None = None) -> None:
    if allowed_tools is None:
        allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
    (root / ollama_harness.ROUTING_CONFIG_PATH.parent).mkdir(parents=True, exist_ok=True)
    tools_literal = json.dumps(allowed_tools)
    (root / ollama_harness.ROUTING_CONFIG_PATH).write_text(
        "schema_version = 1\n"
        "\n"
        "[models.fixture-default]\n"
        'model_id = "fixture-default:current"\n'
        "tool_calling_supported = true\n"
        'allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]\n'
        "\n"
        f"[models.{D_MODEL_ROUTE}]\n"
        f'model_id = "{OLLAMA_MODEL_ID}"\n'
        "tool_calling_supported = true\n"
        f"allowed_tools = {tools_literal}\n"
        "\n"
        "[routing.ollama]\n"
        'default_model = "fixture-default"\n',
        encoding="utf-8",
    )


def _write_project(root: Path, native_harness_record, *, allowed_tools: list[str] | None = None) -> Path:
    (root / "groundtruth.toml").write_text('[project]\nproject_name = "fixture"\n', encoding="utf-8")
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    (root / "scripts" / "ollama_harness.py").write_text("# fixture shim\n", encoding="utf-8")
    native_harness_record(root, _ollama_record())
    _write_routing(root, allowed_tools=allowed_tools)
    return root


def test_readiness_passes_with_mocked_tags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, native_harness_record
) -> None:
    root = _write_project(tmp_path, native_harness_record)
    monkeypatch.setattr(verify, "call_ollama_tags", lambda endpoint, timeout: {OLLAMA_MODEL_ID})
    monkeypatch.setattr(verify, "evaluate_ollama_autostart", lambda **_kwargs: {"checked": True, "configured": True})
    result = verify.evaluate_readiness(root)
    assert result["probe_passed"] is True
    assert result["route_key"] == D_MODEL_ROUTE


def test_readiness_fails_closed_when_daemon_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, native_harness_record
) -> None:
    root = _write_project(tmp_path, native_harness_record)
    monkeypatch.setattr(
        verify,
        "evaluate_ollama_autostart",
        lambda **_kwargs: {"checked": True, "configured": False, "warning": "missing"},
    )

    def _raise_unavailable(endpoint: str, timeout: float) -> set[str]:
        raise verify.OllamaHarnessError("Ollama /api/tags unavailable")

    monkeypatch.setattr(verify, "call_ollama_tags", _raise_unavailable)
    result = verify.evaluate_readiness(root)
    assert result["probe_passed"] is False
    assert result["checks"][-1]["name"] == "ollama /api/tags"
    assert result["checks"][-1]["passed"] is False


def test_readiness_warns_when_autostart_missing_but_daemon_ready(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, native_harness_record
) -> None:
    root = _write_project(tmp_path, native_harness_record)
    monkeypatch.setattr(verify, "call_ollama_tags", lambda endpoint, timeout: {OLLAMA_MODEL_ID})
    monkeypatch.setattr(
        verify,
        "evaluate_ollama_autostart",
        lambda **_kwargs: {
            "checked": True,
            "configured": False,
            "warning": "No Windows scheduled task or service matching Ollama was detected.",
        },
    )

    result = verify.evaluate_readiness(root)

    assert result["probe_passed"] is True
    assert result["autostart"]["configured"] is False
    assert result["warnings"] == [
        {
            "name": "ollama autostart",
            "detail": "No Windows scheduled task or service matching Ollama was detected.",
        }
    ]


def test_readiness_fails_when_required_review_tool_missing(tmp_path: Path, native_harness_record) -> None:
    root = _write_project(tmp_path, native_harness_record, allowed_tools=["Read", "Glob"])
    result = verify.evaluate_readiness(root, require_daemon=False)
    assert result["probe_passed"] is False
    detail = result["checks"][-1]["detail"]
    for tool in ("Bash", "Edit", "Grep", "Write"):
        assert tool in detail


@pytest.mark.parametrize(
    "requested,advertised,expected",
    [
        ("fixture", {"fixture:latest"}, True),
        ("fixture:latest", {"fixture"}, True),
        ("fixture", {"fixture:other"}, False),
        ("fixture:cloud", {"fixture:cloud"}, True),
        ("fixture:cloud", {"fixture:cloud:extra"}, False),
        ("namespace/fixture", {"namespace/fixture:latest"}, True),
        ("fixture", set(), False),
    ],
)
def test_advertised_model_matches_exact_tag_or_default_latest(requested, advertised, expected):
    assert verify._model_advertised(requested, advertised) is expected


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["fixture", None],
        ["fixture", ""],
        # c123 (batch design WP2 2.1): a foreign shim fails even with an otherwise valid argv; the skill forms moved
        # to the role test below.
        ["python", "foreign/scripts/ollama_harness.py", "--model", D_MODEL_ROUTE],
    ],
)
def test_malformed_launch_record_prevents_host_and_provider_checks(tmp_path, monkeypatch, native_harness_record, argv):
    root = _write_project(tmp_path, native_harness_record)
    native_harness_record(root, _ollama_record(surfaces={"headless": {"argv": argv}}))

    def forbidden(*args, **kwargs):
        pytest.fail("Invalid launch metadata must not start host/provider checks")

    monkeypatch.setattr(verify, "call_ollama_tags", forbidden)
    monkeypatch.setattr(verify, "evaluate_ollama_autostart", forbidden)
    assert verify.evaluate_readiness(root)["probe_passed"] is False


def test_the_corrected_d_registration_passes_the_argv_and_route_checks(tmp_path, monkeypatch, native_harness_record):
    """c123 (batch design WP2 2.1): the readiness check renders D's template and resolves its one --model."""
    assert " ".join(D_ARGV) == (
        "groundtruth-kb/.venv/Scripts/python.exe scripts/ollama_harness.py --init {{INIT_LINE}} "
        "--bridge-document {{DOCUMENT}} --bridge-version {{VERSION}} --report {{REPORT}} -p {{PROMPT}} "
        "--model deepseek-v4-flash-cloud"
    )
    root = _write_project(tmp_path, native_harness_record)
    monkeypatch.setattr(verify, "evaluate_ollama_autostart", lambda **kwargs: {"checked": False, "configured": None})

    result = verify.evaluate_readiness(root, require_daemon=False)

    assert [(check["name"], check["passed"]) for check in result["checks"]] == [
        ("native headless argv", True),
        ("shim present", True),
        ("routing model route", True),
    ]
    assert (result["route_key"], result["model_id"]) == (D_MODEL_ROUTE, OLLAMA_MODEL_ID)
    assert result["probe_passed"] is True


@pytest.mark.parametrize(
    "surfaces",
    [
        pytest.param({**OLLAMA_SURFACES, "headless": {"argv": [*D_ARGV, "--skill", "bridge-review"]}}, id="skill"),
        pytest.param({**OLLAMA_SURFACES, "headless": {"argv": [*D_ARGV, "--skill=verification"]}}, id="skill_equals"),
        pytest.param(
            {**OLLAMA_SURFACES, "dispatch": {"dispatch_tags": ["low-cost", "loyal-opposition"]}}, id="role_tag"
        ),
        pytest.param({**OLLAMA_SURFACES, "headless": {"argv": [*D_ARGV, "::init gtkb lo"]}}, id="init_marker"),
        pytest.param({**OLLAMA_SURFACES, "headless": {"argv": D_ARGV[:-2]}}, id="no_model"),
        pytest.param(
            {**OLLAMA_SURFACES, "headless": {"argv": [*D_ARGV, "--model", "fixture-default"]}}, id="two_models"
        ),
        pytest.param({**OLLAMA_SURFACES, "headless": {"argv": [*D_ARGV[:-2], "--model="]}}, id="empty_model"),
        pytest.param({**OLLAMA_SURFACES, "headless": {"argv": [*D_ARGV[:-1], "{{ROLE}}"]}}, id="unknown_placeholder"),
    ],
)
def test_a_registration_naming_a_role_or_not_exactly_one_model_fails_the_argv_check(
    tmp_path, monkeypatch, native_harness_record, surfaces
):
    """c123 (batch design WP2 2.1): a role skill, a role tag or a model count other than one fails the argv check."""
    root = _write_project(tmp_path, native_harness_record)
    native_harness_record(root, _ollama_record(surfaces=surfaces))

    def forbidden(*args, **kwargs):
        pytest.fail("A refused registration must not reach the routing, host or provider checks")

    monkeypatch.setattr(verify, "load_routing_config", forbidden)
    monkeypatch.setattr(verify, "call_ollama_tags", forbidden)
    monkeypatch.setattr(verify, "evaluate_ollama_autostart", forbidden)

    result = verify.evaluate_readiness(root)

    assert result["probe_passed"] is False
    assert [(check["name"], check["passed"]) for check in result["checks"]] == [
        ("native headless argv", False),
        ("shim present", True),
    ]


def test_a_registered_model_that_does_not_resolve_fails_the_route_check(tmp_path, monkeypatch, native_harness_record):
    root = _write_project(tmp_path, native_harness_record)
    surfaces = {**OLLAMA_SURFACES, "headless": {"argv": [*D_ARGV[:-1], "unrouted-fixture-route"]}}
    native_harness_record(root, _ollama_record(surfaces=surfaces))

    def forbidden(*args, **kwargs):
        pytest.fail("An unresolved route must not reach the host or provider checks")

    monkeypatch.setattr(verify, "call_ollama_tags", forbidden)
    monkeypatch.setattr(verify, "evaluate_ollama_autostart", forbidden)

    result = verify.evaluate_readiness(root)

    assert result["probe_passed"] is False
    assert result["checks"][-1]["name"] == "routing model route"
    assert result["checks"][-1]["passed"] is False
    assert "route_key" not in result


def test_omitted_daemon_check_is_explicitly_unqualified(tmp_path, monkeypatch, native_harness_record):
    root = _write_project(tmp_path, native_harness_record)
    monkeypatch.setattr(verify, "evaluate_ollama_autostart", lambda **kwargs: {"checked": False, "configured": None})
    report = verify.evaluate_readiness(root, require_daemon=False)
    assert report["probe_passed"] is True
    assert report["probe_scope"] == "installation_and_routing"
    assert report["model_execution"] == report["harness_qualification"] == "unqualified"
    assert "argv" not in report and "ready" not in report
    assert not any(c["name"] == "ollama /api/tags" for c in report["checks"])
