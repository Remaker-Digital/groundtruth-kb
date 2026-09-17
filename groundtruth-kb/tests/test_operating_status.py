"""`gt status`: compact read-only operating status from fresh native reads (O-7 R25).

Carries the retained duties of the SQLite-era operating-state cases: the CLI JSON and the startup text come from one
collector; the envelope names its components; a historical startup report never certifies anything; an unavailable
dependency is reported as UNKNOWN with its cause rather than crashing; the module has no LLM or network dependency
beyond the configured authority. The `dashboard` component states the project dashboard link from configuration
and local derived-view files without contacting anything (SPEC-PROJECT-DASHBOARD-KPI-LINK-001, owner ruling D4).
"""

from __future__ import annotations

import inspect
import json

import pytest

from groundtruth_kb import operating_status
from groundtruth_kb.config import GTConfig
from groundtruth_kb.dashboard_link import grafana_dashboard_url, refresh_service_url
from groundtruth_kb.operating_status import collect_operating_status, format_startup_operating_status

pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]


def test_status_cli_json_and_startup_use_same_collector(native_application) -> None:
    result = native_application.invoke("status", "--startup", "--json")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema_version"] == 1 and payload["startup"] is True and payload["certifies_context"] is False
    assert {component["name"] for component in payload["components"]} == {
        "authority",
        "project",
        "bridge",
        "registry",
        "formal",
        "session",
        "dashboard",
    }
    authority = next(component for component in payload["components"] if component["name"] == "authority")
    assert authority["status"] == "PASS" and authority["evidence"]["ready"] is True
    project = next(component for component in payload["components"] if component["name"] == "project")
    assert project["evidence"]["applications"] == ["Alpha", "Beta"]
    session = next(component for component in payload["components"] if component["name"] == "session")
    assert session["status"] == "UNKNOWN" and "nothing is inferred" in session["detail"]
    dashboard = next(component for component in payload["components"] if component["name"] == "dashboard")
    assert dashboard["status"] == "PASS" and dashboard["detail"] == f"{grafana_dashboard_url()} (not contacted)"
    config = GTConfig.load(config_path=native_application.config, discover=False)
    rendered = format_startup_operating_status(collect_operating_status(config, startup=True))
    assert "Operating State" in rendered and str(native_application.host.resolve()) in rendered
    assert "not certified" in rendered and f"- dashboard: PASS - {grafana_dashboard_url()} (not contacted)" in rendered


@pytest.mark.parametrize("report_content", [None, "", "# Startup: PASS\nAll previous inputs were current.\n"])
def test_startup_status_cannot_certify_context_from_a_historical_report(native_application, report_content) -> None:
    if report_content is not None:
        report = native_application.host / "docs" / "gtkb-dashboard" / "session-startup-report.md"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(report_content, encoding="utf-8")
    result = native_application.invoke("status", "--startup", "--json")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert "startup" not in {component["name"] for component in payload["components"]}
    assert payload["certifies_context"] is False
    assert "session-startup-report.md" not in result.output


def test_bound_context_is_reported_only_when_named(native_application) -> None:
    binding = native_application.client.request(
        "POST", "/v1/sessions/bind", body={"native_context_id": "status-ctx", "init_command": "::init gtkb pb"}
    )["binding"]
    result = native_application.invoke(
        "status", "--native-context-id", "status-ctx", "--component", "session", "--json"
    )
    assert result.exit_code == 0, result.output
    session = json.loads(result.output)["components"][0]
    assert (
        session["status"] == "PASS"
        and session["evidence"]["binding"]["session_context_id"] == binding["session_context_id"]
    )
    assert session["evidence"]["binding"]["role"] == binding["role"]


def test_unavailable_authority_is_reported_not_inferred(tmp_path, runner) -> None:
    (tmp_path / "groundtruth.toml").write_text(
        '[groundtruth]\nproject_root="' + tmp_path.as_posix() + '"\nauthority_url="http://127.0.0.1:9"\n',
        encoding="utf-8",
    )
    from groundtruth_kb.cli import main

    result = runner.invoke(main, ["--config", str(tmp_path / "groundtruth.toml"), "status", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["overall_status"] == "UNKNOWN"
    for name in ("authority", "bridge", "formal"):
        component = next(c for c in payload["components"] if c["name"] == name)
        assert component["status"] == "UNKNOWN" and "authority unavailable" in component["detail"]
        assert component["evidence"]["code"] == "authority_unavailable"
    registry = next(c for c in payload["components"] if c["name"] == "registry")
    assert registry["status"] == "UNKNOWN" and "no declared registry" in registry["detail"]


class _StatusClient:
    """A client whose only route is the authority status payload under test."""

    def __init__(self, payload: object) -> None:
        self.payload = payload

    def request(self, method: str, path: str, **_: object) -> object:
        assert (method, path) == ("GET", "/v1/authority/status")
        return self.payload


@pytest.mark.parametrize(
    ("payload", "expected", "fragment"),
    [
        (
            {"status": "pass", "ambiguities": [], "source_issues": [], "validation_issues": [], "records": 3},
            "PASS",
            "no ambiguities",
        ),
        (
            {
                "status": "fail",
                "ambiguities": [],
                "source_issues": [{"id": "OTHER", "source_authority": "SPEC-2", "status": "retired"}],
                "validation_issues": [],
            },
            "FAIL",
            "1 source issues",
        ),
        (
            {"status": "fail", "ambiguities": [], "source_issues": [], "validation_issues": [{"id": "OTHER"}]},
            "FAIL",
            "1 validation issues",
        ),
        (
            {"status": "pass", "ambiguities": [{"subject": "project"}], "source_issues": [], "validation_issues": []},
            "FAIL",
            "1 ambiguities",
        ),
        ({"status": "fail", "ambiguities": [], "source_issues": [], "validation_issues": []}, "FAIL", "without listed"),
        ({"ambiguities": [], "source_defects": []}, "UNKNOWN", "not the native contract"),
        ({"status": "pass", "ambiguities": 0, "source_issues": [], "validation_issues": []}, "UNKNOWN", "not the"),
        (["pass"], "UNKNOWN", "not the native contract"),
    ],
)
def test_formal_component_follows_the_authority_status_contract(payload, expected, fragment) -> None:
    status, detail, route, evidence = operating_status._formal(_StatusClient(payload))
    assert status == expected and fragment in detail and route == "GET /v1/authority/status"
    assert "records" not in evidence


def test_a_retired_formal_source_cannot_display_pass(native_application) -> None:
    """The service's own failing state (a term whose formal source is retired) is FAIL through the public CLI."""
    client = native_application.client
    for domain, record_id, fields in (
        ("specifications", "SPEC-1", {"title": "Required effect", "description": "Preserve work", "status": "active"}),
        ("specifications", "SPEC-2", {"title": "Other meaning", "status": "active"}),
    ):
        client.request(
            "PUT",
            f"/v1/{domain}/{record_id}",
            body={"expected_version": 0, "actor": "qualification", "reason": "Seed", "fields": fields},
        )
    for record_id, term, source in (("PROJECT", "project", "SPEC-1"), ("OTHER", "other", "SPEC-2")):
        client.request(
            "PUT",
            f"/v1/terms/{record_id}",
            body={
                "expected_version": 0,
                "actor": "qualification",
                "reason": "Seed",
                "fields": {
                    "canonical_term": term,
                    "definition": f"The {term} concept.",
                    "scope": "platform",
                    "authority_level": "platform_core",
                    "source_authority": source,
                    "accepted_synonyms": [],
                    "lifecycle_status": "active",
                },
            },
        )
    healthy = json.loads(native_application.invoke("status", "--component", "formal", "--json").output)
    assert healthy["components"][0]["status"] == "PASS" and healthy["overall_status"] == "PASS"
    client.request(
        "PUT",
        "/v1/specifications/SPEC-2",
        body={"expected_version": 1, "actor": "qualification", "reason": "Retire", "fields": {"status": "retired"}},
    )
    failing = json.loads(native_application.invoke("status", "--component", "formal", "--json").output)
    component = failing["components"][0]
    assert component["status"] == "FAIL" and failing["overall_status"] != "PASS"
    assert component["evidence"]["source_issues"] == [
        {"id": "OTHER", "source_authority": "SPEC-2", "status": "retired"}
    ]
    text = native_application.invoke("status", "--component", "formal").output
    assert "FAIL" in text and "source issues" in text


def test_unknown_component_is_a_usage_error(native_application) -> None:
    result = native_application.invoke("status", "--component", "nonexistent")
    assert result.exit_code == 2 and "unknown status component" in result.output


def test_operating_status_module_has_no_llm_or_network_dependency() -> None:
    source = inspect.getsource(operating_status)
    for forbidden in (
        "openai",
        "anthropic",
        "requests.",
        "httpx",
        "socket",
        "urllib.request",
        "sqlite3",
        "KnowledgeDB",
    ):
        assert forbidden not in source, forbidden


class _RefusingClient:
    """A client whose every request fails the test: the component under test must make none."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.url = "http://127.0.0.1:9"

    def request(self, method: str, path: str, **_: object) -> object:
        raise AssertionError(f"the dashboard component must not contact the authority ({method} {path})")


def _coordination_counts(service) -> tuple[int, int]:
    """(session bindings, history rows) read from the disposable kernel; the dashboard component changes neither."""
    from psycopg import sql

    counts = []
    with service.kernel.transaction(read_only=True) as tx:
        for table in ("session_init_bindings", "record_history"):
            tx.cursor.execute(
                sql.SQL("SELECT count(*) AS n FROM {}.{}").format(sql.Identifier(tx.schema), sql.Identifier(table))
            )
            counts.append(tx.cursor.fetchone()["n"])
    return counts[0], counts[1]


def test_dashboard_component_states_the_configured_link_without_contact(native_application, monkeypatch) -> None:
    """The link is the `gt dashboard start` derivation; the derived view is evidence; nothing is requested or bound."""
    service = native_application.item["service"]
    before = _coordination_counts(service)
    result = native_application.invoke("status", "--component", "dashboard", "--json")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    component = payload["components"][0]
    link = grafana_dashboard_url()
    assert link == "http://127.0.0.1:3000/d/groundtruth-kb-dashboard/groundtruth-kb-dashboard"
    assert component["status"] == "PASS" and payload["overall_status"] == "PASS"
    assert component["detail"] == f"{link} (not contacted)"
    runtime_root = native_application.host.resolve() / ".groundtruth" / "dashboard"
    assert component["evidence"] == {
        "configured": True,
        "grafana_url": link,
        "refresh_url": refresh_service_url(),
        "runtime_root": str(runtime_root),
        "runtime_root_present": False,
        "landing_page_present": False,
        "grafana_dashboard_present": False,
        "last_refresh": None,
        "last_refresh_basis": "no dashboard-data.json under the runtime root",
        "contacted": False,
    }
    from groundtruth_kb import get_templates_dir
    from groundtruth_kb.dashboard import resolve_dashboard_paths

    config = GTConfig.load(config_path=native_application.config, discover=False)
    assert str(resolve_dashboard_paths(config).runtime_root) == component["evidence"]["runtime_root"]
    assert link in (get_templates_dir() / "dashboard" / "index.html").read_text(encoding="utf-8")
    runtime_root.mkdir(parents=True)
    (runtime_root / "index.html").write_text("<!doctype html>\n", encoding="utf-8")
    (runtime_root / "grafana" / "dashboards").mkdir(parents=True)
    (runtime_root / "grafana" / "dashboards" / "gtkb-dashboard.json").write_text("{}\n", encoding="utf-8")
    (runtime_root / "dashboard-data.json").write_text(
        json.dumps(
            {
                "status": "partial",
                "started_at": "2026-09-16T10:00:00+00:00",
                "generated_at": "2026-09-16T10:00:05+00:00",
                "metrics": {"backlog_active_items": 1},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(operating_status, "AuthorityClient", _RefusingClient)
    evidence = collect_operating_status(config, components=("dashboard",)).components[0].evidence
    assert evidence["runtime_root_present"] and evidence["landing_page_present"]
    assert evidence["grafana_dashboard_present"] and evidence["contacted"] is False
    assert evidence["last_refresh"] == "2026-09-16T10:00:05+00:00"
    assert evidence["last_refresh_basis"] == "dashboard-data.json generated_at"
    assert _coordination_counts(service) == before and before[0] == 0


def test_dashboard_component_is_unknown_without_a_selected_configuration(tmp_path, runner, monkeypatch) -> None:
    """No groundtruth.toml at the project root: no dashboard is configured there, and the reason is the detail."""
    monkeypatch.setattr(operating_status, "AuthorityClient", _RefusingClient)
    for root in (tmp_path / "missing", tmp_path):
        config = GTConfig(project_root=root, authority_url="http://127.0.0.1:9")
        report = collect_operating_status(config, components=("dashboard",))
        component = report.components[0]
        assert component.status == "UNKNOWN" and report.overall_status == "UNKNOWN"
        assert "no dashboard is configured" in component.detail and "groundtruth.toml is absent" in component.detail
        assert component.evidence == {
            "configured": False,
            "selected_configuration": str(root.resolve() / "groundtruth.toml"),
            "contacted": False,
        }
    project = tmp_path / "project"
    project.mkdir()
    selected = tmp_path / "elsewhere" / "groundtruth.toml"
    selected.parent.mkdir()
    selected.write_text('[groundtruth]\nproject_root="' + project.as_posix() + '"\n', encoding="utf-8")
    from groundtruth_kb.cli import main

    result = runner.invoke(main, ["--config", str(selected), "status", "--component", "dashboard", "--json"])
    assert result.exit_code == 0, result.output
    component = json.loads(result.output)["components"][0]
    assert component["status"] == "UNKNOWN" and "groundtruth.toml is absent" in component["detail"]


@pytest.mark.parametrize(
    ("page_json", "basis"),
    [
        ("not json", "dashboard-data.json is unreadable or malformed; nothing is inferred from it"),
        ("[1, 2]", "dashboard-data.json records no refresh timestamp"),
        (
            json.dumps({"status": "unavailable", "started_at": None, "generated_at": None, "metrics": {}}),
            "dashboard-data.json records no refresh timestamp",
        ),
        (
            json.dumps({"generated_at": "yesterday"}),
            "dashboard-data.json records a malformed refresh timestamp; nothing is inferred from it",
        ),
    ],
)
def test_dashboard_refresh_timestamp_is_stated_only_from_a_well_formed_page_json(tmp_path, page_json, basis) -> None:
    (tmp_path / "groundtruth.toml").write_text(
        '[groundtruth]\nproject_root="' + tmp_path.as_posix() + '"\n', encoding="utf-8"
    )
    runtime_root = tmp_path / ".groundtruth" / "dashboard"
    runtime_root.mkdir(parents=True)
    (runtime_root / "dashboard-data.json").write_text(page_json, encoding="utf-8")
    component = collect_operating_status(GTConfig(project_root=tmp_path), components=("dashboard",)).components[0]
    assert component.status == "PASS" and component.evidence["runtime_root_present"] is True
    assert component.evidence["last_refresh"] is None and component.evidence["last_refresh_basis"] == basis


def test_dashboard_link_is_displayed_at_startup(native_application) -> None:
    link = grafana_dashboard_url()
    startup = native_application.invoke("status", "--startup")
    assert startup.exit_code == 0, startup.output
    assert f"- dashboard: PASS - {link} (not contacted)" in startup.output
    text = native_application.invoke("status")
    assert text.exit_code == 0 and f"- PASS dashboard: {link} (not contacted)" in text.output
    payload = json.loads(native_application.invoke("status", "--startup", "--json").output)
    assert [component["name"] for component in payload["components"]] == list(operating_status.COMPONENTS)
    dashboard = next(component for component in payload["components"] if component["name"] == "dashboard")
    assert dashboard["evidence"]["grafana_url"] == link and dashboard["evidence"]["contacted"] is False
