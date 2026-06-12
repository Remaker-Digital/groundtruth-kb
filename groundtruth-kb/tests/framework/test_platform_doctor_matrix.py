import json

from click.testing import CliRunner

from groundtruth_kb.cli import main


def test_doctor_reports_clean_isolation(tmp_path):
    runner = CliRunner()
    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text("[groundtruth]\ndb_path = './groundtruth.db'\nproject_root = '.'\n", encoding="utf-8")

    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(db_path=tmp_path / "groundtruth.db")
    db.close()

    result = runner.invoke(main, ["--config", str(toml_path), "project", "doctor", "--dir", str(tmp_path), "--json"])
    data = json.loads(result.output)
    names = [c["name"] for c in data["checks"]]
    assert "isolation:application-registry" in names


def test_doctor_reports_occupancy_matrix(tmp_path):
    runner = CliRunner()
    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text("[groundtruth]\ndb_path = './groundtruth.db'\nproject_root = '.'\n", encoding="utf-8")

    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(db_path=tmp_path / "groundtruth.db")
    db.close()

    apps_dir = tmp_path / "applications"
    (apps_dir / "foo" / "src").mkdir(parents=True, exist_ok=True)
    (apps_dir / "bar" / "src").mkdir(parents=True, exist_ok=True)

    result = runner.invoke(main, ["--config", str(toml_path), "project", "doctor", "--dir", str(tmp_path)])
    assert result.exit_code != 0
    assert "Multi-slot occupancy" in result.output
    assert "P0" in result.output
