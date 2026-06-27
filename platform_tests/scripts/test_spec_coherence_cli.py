"""Spec-derived tests for the WI-3424 ``gt validate spec-coherence`` CLI."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402
from groundtruth_kb.coherence import (  # noqa: E402
    CoherenceRuleError,
    emit_json,
    emit_markdown,
    load_rules,
    load_specs_from_db,
    make_result,
    run_all,
)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_rules(root: Path) -> Path:
    rules = root / "config" / "governance" / "spec-coherence-rules.toml"
    rules.parent.mkdir(parents=True)
    rules.write_text(
        r"""
[[rules]]
id = "surface-overlap-opposite-polarity"
class = "surface_overlap"
description = "surface overlap"
surface_tags = ["cached_startup_snapshot_authority"]
classification = "contradiction_candidate"
remediation_hint = "clarify authority"

[[rules.polarity_pairs]]
positive = "\\blive\\s+(?:project\\s+)?sources\\b"
negative = "\\bcached\\s+startup\\s+snapshots\\b|\\bcached\\s+summaries\\b"

[[rules]]
id = "authority-hierarchy-invariant"
class = "hierarchy_violation"
description = "hierarchy"
parent_types = ["governance"]
child_types = ["design_constraint"]
polarity_pairs = [
  { positive = "\\bmust\\s+use\\b", negative = "\\bmust\\s+not\\s+use\\b" },
]
classification = "hierarchy_violation_candidate"
remediation_hint = "revise child"

[[rules]]
id = "status-drift"
class = "status_drift"
description = "drift"
classification = "verification_staleness"
remediation_hint = "reverify child"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return rules


def _write_project(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text('[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n', encoding="utf-8")
    rules = _write_rules(root)
    return root, config, rules


def _create_specs_db(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE current_specifications (
                id TEXT PRIMARY KEY,
                version TEXT,
                title TEXT,
                description TEXT,
                tags TEXT,
                status TEXT,
                type TEXT,
                authority TEXT,
                constraints TEXT,
                affected_by TEXT,
                implementation_verified_at TEXT,
                changed_at TEXT,
                parent TEXT
            )
            """
        )
        rows = [
            (
                "DCL-SESSION-STARTUP-TOKEN-BUDGET-001",
                "1",
                "Token budget cache",
                "Startup may rely on cached startup snapshots for summaries.",
                '["cached_startup_snapshot_authority"]',
                "specified",
                "design_constraint",
                "",
                "",
                "",
                None,
                "2026-01-01T00:00:00Z",
                "GOV-SESSION-SELF-INITIALIZATION-001",
            ),
            (
                "GOV-SESSION-SELF-INITIALIZATION-001",
                "1",
                "Startup freshness",
                "Startup must use live project sources and must not use cached summaries as authority.",
                '["cached_startup_snapshot_authority"]',
                "specified",
                "governance",
                "",
                "",
                "",
                None,
                "2026-02-01T00:00:00Z",
                None,
            ),
            (
                "GOV-PARENT-001",
                "1",
                "Parent",
                "The platform must not use archived roots.",
                "[]",
                "specified",
                "governance",
                "",
                "",
                "",
                None,
                "2026-03-01T00:00:00Z",
                None,
            ),
            (
                "DCL-CHILD-001",
                "1",
                "Child",
                "The child must use archived roots.",
                "[]",
                "verified",
                "design_constraint",
                "",
                "",
                "",
                "2026-02-01T00:00:00Z",
                "2026-02-01T00:00:00Z",
                "GOV-PARENT-001",
            ),
        ]
        conn.executemany(
            """
            INSERT INTO current_specifications (
                id, version, title, description, tags, status, type, authority,
                constraints, affected_by, implementation_verified_at, changed_at, parent
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()
    finally:
        conn.close()


def test_load_rules_valid_and_filter(tmp_path: Path) -> None:
    root, _config, rules_path = _write_project(tmp_path)
    _ = root
    rules = load_rules(rules_path)
    assert [rule.id for rule in rules] == [
        "surface-overlap-opposite-polarity",
        "authority-hierarchy-invariant",
        "status-drift",
    ]
    assert [rule.id for rule in load_rules(rules_path, name="status-drift")] == ["status-drift"]


def test_load_rules_malformed_registry_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.toml"
    bad.write_text("[[rules]]\nclass = 'surface_overlap'\n", encoding="utf-8")
    with pytest.raises(CoherenceRuleError, match="missing 'id'"):
        load_rules(bad)


def test_run_all_detects_surface_hierarchy_and_status_drift(tmp_path: Path) -> None:
    root, _config, rules_path = _write_project(tmp_path)
    db_path = root / "groundtruth.db"
    _create_specs_db(db_path)
    specs = load_specs_from_db(db_path)
    findings = run_all(specs, load_rules(rules_path))
    by_rule = {finding.rule_id for finding in findings}
    assert "surface-overlap-opposite-polarity" in by_rule
    assert "authority-hierarchy-invariant" in by_rule
    assert "status-drift" in by_rule
    surface = next(f for f in findings if f.rule_id == "surface-overlap-opposite-polarity")
    assert {
        surface.spec_a,
        surface.spec_b,
    } == {"DCL-SESSION-STARTUP-TOKEN-BUDGET-001", "GOV-SESSION-SELF-INITIALIZATION-001"}


def test_emit_json_and_markdown_schema(tmp_path: Path) -> None:
    root, _config, rules_path = _write_project(tmp_path)
    db_path = root / "groundtruth.db"
    _create_specs_db(db_path)
    rules = load_rules(rules_path)
    specs = load_specs_from_db(db_path)
    result = make_result(
        db_path=db_path, rule_set_path=rules_path, specs=specs, rules=rules, findings=run_all(specs, rules)
    )
    out_json = tmp_path / "findings.json"
    out_md = tmp_path / "summary.md"

    emit_json(result, out_json)
    emit_markdown(result, out_md)

    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["finding_count"] == len(payload["findings"])
    assert {"rule_id", "spec_a", "spec_b", "surface", "evidence_excerpts", "classification", "remediation_hint"} <= set(
        payload["findings"][0]
    )
    markdown = out_md.read_text(encoding="utf-8")
    assert "## surface_overlap" in markdown
    assert "## hierarchy_violation" in markdown
    assert "## status_drift" in markdown


def test_cli_runs_writes_outputs_and_fail_on_findings(tmp_path: Path) -> None:
    root, config, _rules_path = _write_project(tmp_path)
    _create_specs_db(root / "groundtruth.db")
    out = tmp_path / "out"

    runner = CliRunner()
    result = runner.invoke(main, ["--config", str(config), "validate", "spec-coherence", "--output", str(out)])
    assert result.exit_code == 0, result.output
    assert (out / "findings.json").exists()
    assert (out / "summary.md").exists()
    assert "spec coherence:" in result.output

    result_fail = runner.invoke(
        main,
        [
            "--config",
            str(config),
            "validate",
            "spec-coherence",
            "--output",
            str(tmp_path / "out2"),
            "--fail-on-findings",
        ],
    )
    assert result_fail.exit_code == 5


def test_cli_json_only_and_read_only_db(tmp_path: Path) -> None:
    root, config, _rules_path = _write_project(tmp_path)
    db_path = root / "groundtruth.db"
    _create_specs_db(db_path)
    before = _hash(db_path)
    out = tmp_path / "json-only"

    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "validate",
            "spec-coherence",
            "--output",
            str(out),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0, result.output
    assert (out / "findings.json").exists()
    assert not (out / "summary.md").exists()
    assert before == _hash(db_path), "gt validate spec-coherence mutated the fixture DB"
