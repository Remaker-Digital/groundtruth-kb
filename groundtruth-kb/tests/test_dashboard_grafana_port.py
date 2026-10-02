"""The dashboard's Grafana port default is 8767 on every surface that names it, and never 3000.

Port 3000 is left to other local developer tools (owner decision 2026-10-02: Cursor uses it). The package constant
is the one source; the CLI options, the refresh service, the template and the setup steps follow it.
"""

from __future__ import annotations

import inspect

from groundtruth_kb import dashboard, dashboard_link, dashboard_service, get_templates_dir
from groundtruth_kb.cli_authority import dashboard_group


def test_package_default_grafana_port_is_8767() -> None:
    assert dashboard_link.DEFAULT_GRAFANA_PORT == 8767
    assert dashboard.DEFAULT_GRAFANA_PORT == dashboard_link.DEFAULT_GRAFANA_PORT
    assert dashboard_link.grafana_dashboard_url() == (
        "http://127.0.0.1:8767/d/groundtruth-kb-dashboard/groundtruth-kb-dashboard"
    )


def test_dashboard_cli_commands_default_to_the_package_port() -> None:
    for name in ("start", "serve"):
        options = {param.name: param for param in dashboard_group.commands[name].params}
        assert options["grafana_port"].default == dashboard_link.DEFAULT_GRAFANA_PORT, name


def test_refresh_service_defaults_to_the_package_port(tmp_path, monkeypatch) -> None:
    default = dashboard_link.DEFAULT_GRAFANA_PORT
    assert inspect.signature(dashboard_service.RefreshState.__init__).parameters["grafana_port"].default == default
    assert inspect.signature(dashboard_service.run_service).parameters["grafana_port"].default == default
    for name in ("GTKB_DASHBOARD_DB", "GTKB_DASHBOARD_RUNTIME_ROOT", "GTKB_DASHBOARD_REFRESH_PORT"):
        monkeypatch.delenv(name, raising=False)
    (tmp_path / "groundtruth.toml").write_text("[groundtruth]\n", encoding="utf-8")
    seen: dict[str, object] = {}
    monkeypatch.setattr(dashboard_service, "run_service", lambda *args, **kwargs: seen.update(kwargs))
    assert dashboard_service.main(["--project-root", str(tmp_path)]) == 0
    assert seen["grafana_port"] == default


def test_dashboard_surfaces_name_the_package_port() -> None:
    template = (get_templates_dir() / "dashboard" / "index.html").read_text(encoding="utf-8")
    assert "127.0.0.1:8767" in template
    assert "127.0.0.1:3000" not in template
    local = next(step for step in dashboard.SETUP_STEPS if step["link_label"] == "Local Grafana")
    assert local["link_url"] == "http://127.0.0.1:8767/"
