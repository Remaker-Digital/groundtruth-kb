import shutil
from pathlib import Path

from groundtruth_kb.isolation.doctor_verdicts import evaluate_isolation_state
from groundtruth_kb.isolation.occupancy_detector import detect_occupancy


def write_registry(tmp_path: Path, apps: dict):
    reg_dir = tmp_path / "applications"
    reg_dir.mkdir(parents=True, exist_ok=True)
    reg_file = reg_dir / "registry.toml"
    content = "[applications]\n"
    for app_name, _app_data in apps.items():
        content += f"{app_name} = {{ slot = '{app_name}' }}\n"
    reg_file.write_text(content, encoding="utf-8")


def test_non_marker_blocks_register(tmp_path):
    foo_dir = tmp_path / "applications" / "foo"
    foo_dir.mkdir(parents=True, exist_ok=True)
    env_file = foo_dir / ".env.local"
    env_file.write_text("SOME_KEY=value", encoding="utf-8")

    status = detect_occupancy(tmp_path, "foo")
    assert status["occupied"] is True
    assert status["trigger"] == "non_allowlisted_content"
    assert ".env.local" in status["non_allowlisted_files"]


def test_allowlisted_readme_succeeds(tmp_path):
    foo_dir = tmp_path / "applications" / "foo"
    foo_dir.mkdir(parents=True, exist_ok=True)
    readme = foo_dir / "README.md"
    readme.write_text("<!-- gtkb-application-slot-cleanup-marker -->\nThis slot is cleaned up.", encoding="utf-8")

    status = detect_occupancy(tmp_path, "foo")
    assert status["occupied"] is False


def test_non_allowlisted_readme_blocks_register(tmp_path):
    foo_dir = tmp_path / "applications" / "foo"
    foo_dir.mkdir(parents=True, exist_ok=True)
    readme = foo_dir / "README.md"
    readme.write_text("Arbitrary documentation without marker.", encoding="utf-8")

    status = detect_occupancy(tmp_path, "foo")
    assert status["occupied"] is True
    assert status["trigger"] == "non_allowlisted_content"


def test_registry_only_conflict(tmp_path):
    write_registry(tmp_path, {"foo": {}})

    status = detect_occupancy(tmp_path, "foo")
    assert status["occupied"] is True
    assert status["trigger"] == "registry_entry"
    assert status["details"] == "Registry entry exists but no application directory"


def test_doctor_verdict_matrix(tmp_path):
    res = evaluate_isolation_state(tmp_path)
    assert len(res["verdicts"]) == 0

    foo_dir = tmp_path / "applications" / "foo"
    foo_dir.mkdir(parents=True, exist_ok=True)
    (foo_dir / "src").mkdir(parents=True, exist_ok=True)

    bar_dir = tmp_path / "applications" / "bar"
    bar_dir.mkdir(parents=True, exist_ok=True)
    (bar_dir / "src").mkdir(parents=True, exist_ok=True)

    res = evaluate_isolation_state(tmp_path)
    assert any(v["severity"] == "P0" and "Multi-slot occupancy" in v["verdict"] for v in res["verdicts"])

    shutil.rmtree(bar_dir)

    json_marker = foo_dir / ".gtkb-app-isolation.json"
    json_marker.write_text("invalid json {", encoding="utf-8")
    res = evaluate_isolation_state(tmp_path)
    assert any(v["severity"] == "P1" and "Malformed markers" in v["verdict"] for v in res["verdicts"])

    json_marker.write_text('{"application": "Agent_Red"}', encoding="utf-8")
    res = evaluate_isolation_state(tmp_path)
    assert any(v["severity"] == "P1" and "Mismatched markers" in v["verdict"] for v in res["verdicts"])

    json_marker.write_text('{"application": "foo"}', encoding="utf-8")
    res = evaluate_isolation_state(tmp_path)
    assert any(v["severity"] == "P1" and "Partial slot registration" in v["verdict"] for v in res["verdicts"])
