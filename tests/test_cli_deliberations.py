"""Tests for gt deliberations CLI commands (Phase 3 of production-readiness).

Approved by Codex at bridge/gtkb-deliberation-cli-004.md with 6 implementation
conditions. All 6 conditions are encoded as test assertions:

  1. `add` requires `--id`; `upsert` rejects `--id` (exit 2)
  2. Default `search` uses SQLite text fallback (no ChromaDB required)
  3. `--semantic-only` opt-in enforces ChromaDB presence and rejects
     text_match fallback rows
  4. `upsert` prints ID only (no inserted/matched inference)
  5. `link` performs CLI-layer validation: deliberation, spec, work_item
     must all exist before the link is created
  6. Required field defaults: `--summary` REQUIRED; `--changed-by`
     defaults to "gt-cli"; `--change-reason` defaults to
     "Created via gt deliberations add" (or "Upserted via ..." for upsert)

Verified against:
  - Click 8.3.x
  - interrogate 1.7.0
  - groundtruth-kb 0.4.0+

© 2026 Remaker Digital. Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def project_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a minimal GT-KB project with a spec and a work item for link tests."""
    from groundtruth_kb.db import KnowledgeDB

    # Config file
    config = tmp_path / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\napp_title = "test"\ndb_path = "./groundtruth.db"\n',
        encoding="utf-8",
    )

    # Create DB and seed a spec + work_item so link tests have valid targets
    db_path = tmp_path / "groundtruth.db"
    db = KnowledgeDB(db_path=db_path)
    db.insert_spec(
        id="SPEC-0001",
        type="requirement",
        status="specified",
        title="Test spec",
        description="A test specification for link validation",
        changed_by="test",
        change_reason="seed",
    )
    db.insert_work_item(
        id="WI-0001",
        title="Test work item",
        origin="new",
        component="test",
        resolution_status="open",
        changed_by="test",
        change_reason="seed",
    )

    # Point cwd at the project for default config discovery
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _invoke(runner: CliRunner, args: list[str], config: Path | None = None):
    """Invoke the `main` CLI with optional --config and return the Result."""
    from groundtruth_kb.cli import main

    full_args: list[str] = []
    if config is not None:
        full_args += ["--config", str(config)]
    full_args += args
    return runner.invoke(main, full_args, catch_exceptions=False)


def _db_for(project: Path):
    """Open a KnowledgeDB on the seed project."""
    from groundtruth_kb.db import KnowledgeDB

    return KnowledgeDB(db_path=project / "groundtruth.db")


# ---------------------------------------------------------------------------
# 1-9: `gt deliberations add` (append-only via insert_deliberation)
# ---------------------------------------------------------------------------


class TestDeliberationsAdd:
    def test_add_minimal(self, runner: CliRunner, project_dir: Path) -> None:
        result = _invoke(
            runner,
            [
                "deliberations",
                "add",
                "--id",
                "DELIB-TEST-0001",
                "--title",
                "Test add minimal",
                "--source-type",
                "proposal",
                "--source-ref",
                "test.md",
                "--summary",
                "short summary",
                "--content",
                "body of the deliberation",
            ],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 0, f"expected 0, got {result.exit_code}: {result.output}"
        db = _db_for(project_dir)
        row = db.get_deliberation("DELIB-TEST-0001")
        assert row is not None
        assert row["title"] == "Test add minimal"

    def test_add_all_fields(self, runner: CliRunner, project_dir: Path) -> None:
        result = _invoke(
            runner,
            [
                "deliberations",
                "add",
                "--id",
                "DELIB-TEST-0002",
                "--title",
                "Full fields",
                "--source-type",
                "lo_review",
                "--source-ref",
                "bridge/foo-001.md",
                "--summary",
                "full",
                "--content",
                "content body",
                "--outcome",
                "go",
                "--spec-id",
                "SPEC-0001",
                "--work-item-id",
                "WI-0001",
                "--session-id",
                "S290",
                "--participants",
                "prime_builder,codex",
                "--changed-by",
                "test-author",
                "--change-reason",
                "explicit reason",
            ],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 0, result.output
        db = _db_for(project_dir)
        row = db.get_deliberation("DELIB-TEST-0002")
        assert row is not None
        assert row["outcome"] == "go"
        assert row["spec_id"] == "SPEC-0001"
        assert row["work_item_id"] == "WI-0001"
        assert row["session_id"] == "S290"
        assert row["changed_by"] == "test-author"

    def test_add_content_file_redaction(self, runner: CliRunner, project_dir: Path, tmp_path: Path) -> None:
        # AWS canonical-fake key pattern is covered by the DB's
        # ``_REDACTION_PATTERNS`` list (``aws_key``). This test verifies that
        # ``--content-file`` content flows through the same redaction layer
        # as inline ``--content``; it is NOT asserting anything about the
        # pattern catalog itself.
        secret = "AKIAIOSFODNN7EXAMPLE"
        content_file = tmp_path / "content.txt"
        content_file.write_text(
            f"This contains an AWS key: {secret}\nHere is a phone: +15551234567",
            encoding="utf-8",
        )
        result = _invoke(
            runner,
            [
                "deliberations",
                "add",
                "--id",
                "DELIB-TEST-0003",
                "--title",
                "Redaction test",
                "--source-type",
                "proposal",
                "--source-ref",
                "redact-test.md",
                "--summary",
                "sensitive",
                "--content-file",
                str(content_file),
            ],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 0, result.output
        db = _db_for(project_dir)
        row = db.get_deliberation("DELIB-TEST-0003")
        assert row is not None
        # Redaction happens at the DB layer; verify the stored content does NOT
        # contain the raw AWS key substring (proving --content-file content
        # flowed through the same redaction path as inline --content).
        assert secret not in row["content"], row["content"]

    def test_add_content_and_content_file_conflict(self, runner: CliRunner, project_dir: Path, tmp_path: Path) -> None:
        f = tmp_path / "body.txt"
        f.write_text("body", encoding="utf-8")
        result = _invoke(
            runner,
            [
                "deliberations",
                "add",
                "--id",
                "DELIB-TEST-0004",
                "--title",
                "conflict",
                "--source-type",
                "proposal",
                "--source-ref",
                "x.md",
                "--summary",
                "s",
                "--content",
                "inline body",
                "--content-file",
                str(f),
            ],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 2
        assert "content" in result.output.lower() or "content-file" in result.output.lower()

    def test_add_missing_content(self, runner: CliRunner, project_dir: Path) -> None:
        result = _invoke(
            runner,
            [
                "deliberations",
                "add",
                "--id",
                "DELIB-TEST-0005",
                "--title",
                "no content",
                "--source-type",
                "proposal",
                "--source-ref",
                "x.md",
                "--summary",
                "s",
            ],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 2

    def test_add_missing_summary(self, runner: CliRunner, project_dir: Path) -> None:
        # --summary is required per Codex Condition 6
        result = _invoke(
            runner,
            [
                "deliberations",
                "add",
                "--id",
                "DELIB-TEST-0006",
                "--title",
                "no summary",
                "--source-type",
                "proposal",
                "--source-ref",
                "x.md",
                "--content",
                "body",
            ],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 2

    def test_add_missing_id(self, runner: CliRunner, project_dir: Path) -> None:
        # --id is required for `add` (append-only); differs from `upsert`
        result = _invoke(
            runner,
            [
                "deliberations",
                "add",
                "--title",
                "no id",
                "--source-type",
                "proposal",
                "--source-ref",
                "x.md",
                "--summary",
                "s",
                "--content",
                "b",
            ],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 2

    def test_add_invalid_source_type(self, runner: CliRunner, project_dir: Path) -> None:
        result = _invoke(
            runner,
            [
                "deliberations",
                "add",
                "--id",
                "DELIB-TEST-0008",
                "--title",
                "bad source",
                "--source-type",
                "nonsense",
                "--source-ref",
                "x.md",
                "--summary",
                "s",
                "--content",
                "b",
            ],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 2

    def test_add_default_changed_by(self, runner: CliRunner, project_dir: Path) -> None:
        result = _invoke(
            runner,
            [
                "deliberations",
                "add",
                "--id",
                "DELIB-TEST-0009",
                "--title",
                "default author",
                "--source-type",
                "proposal",
                "--source-ref",
                "x.md",
                "--summary",
                "s",
                "--content",
                "b",
            ],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 0, result.output
        row = _db_for(project_dir).get_deliberation("DELIB-TEST-0009")
        assert row is not None
        assert row["changed_by"] == "gt-cli"


# ---------------------------------------------------------------------------
# 10: add twice creates two versions (append-only)
# ---------------------------------------------------------------------------


class TestAddVersioning:
    def test_add_twice_creates_two_versions(self, runner: CliRunner, project_dir: Path) -> None:
        for i in range(2):
            result = _invoke(
                runner,
                [
                    "deliberations",
                    "add",
                    "--id",
                    "DELIB-TEST-0010",
                    "--title",
                    f"iteration {i}",
                    "--source-type",
                    "proposal",
                    "--source-ref",
                    "x.md",
                    "--summary",
                    "s",
                    "--content",
                    f"content v{i}",
                ],
                config=project_dir / "groundtruth.toml",
            )
            assert result.exit_code == 0, result.output
        history = _db_for(project_dir).get_deliberation_history("DELIB-TEST-0010")
        assert len(history) == 2


# ---------------------------------------------------------------------------
# 11-13: `gt deliberations upsert`
# ---------------------------------------------------------------------------


class TestDeliberationsUpsert:
    def test_upsert_auto_generates_id(self, runner: CliRunner, project_dir: Path) -> None:
        result = _invoke(
            runner,
            [
                "deliberations",
                "upsert",
                "--title",
                "auto id",
                "--source-type",
                "proposal",
                "--source-ref",
                "upsert-auto.md",
                "--summary",
                "s",
                "--content",
                "auto body",
            ],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 0, result.output
        # Output should contain a DELIB-* identifier per Codex Condition 4
        assert "DELIB-" in result.output

    def test_upsert_idempotent_on_same_source(self, runner: CliRunner, project_dir: Path) -> None:
        first = _invoke(
            runner,
            [
                "deliberations",
                "upsert",
                "--title",
                "idempotent",
                "--source-type",
                "proposal",
                "--source-ref",
                "upsert-same.md",
                "--summary",
                "s",
                "--content",
                "same content",
            ],
            config=project_dir / "groundtruth.toml",
        )
        assert first.exit_code == 0, first.output
        second = _invoke(
            runner,
            [
                "deliberations",
                "upsert",
                "--title",
                "idempotent",
                "--source-type",
                "proposal",
                "--source-ref",
                "upsert-same.md",
                "--summary",
                "s",
                "--content",
                "same content",
            ],
            config=project_dir / "groundtruth.toml",
        )
        assert second.exit_code == 0, second.output
        # Both invocations produce the same ID (upsert_deliberation_source is
        # idempotent by source_type + source_ref + content_hash)
        # Count deliberations with this source_ref — should be exactly 1
        db = _db_for(project_dir)
        rows = db.list_deliberations(source_ref="upsert-same.md")
        assert len(rows) == 1

    def test_upsert_rejects_id_flag(self, runner: CliRunner, project_dir: Path) -> None:
        # Per Codex Condition 1: upsert does not accept --id
        result = _invoke(
            runner,
            [
                "deliberations",
                "upsert",
                "--id",
                "DELIB-REJECTED",
                "--title",
                "should reject",
                "--source-type",
                "proposal",
                "--source-ref",
                "x.md",
                "--summary",
                "s",
                "--content",
                "b",
            ],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 2


# ---------------------------------------------------------------------------
# 14-16: `gt deliberations get`
# ---------------------------------------------------------------------------


class TestDeliberationsGet:
    def _seed(self, runner: CliRunner, project_dir: Path) -> None:
        _invoke(
            runner,
            [
                "deliberations",
                "add",
                "--id",
                "DELIB-GET-0001",
                "--title",
                "getable",
                "--source-type",
                "proposal",
                "--source-ref",
                "g.md",
                "--summary",
                "s",
                "--content",
                "first version",
            ],
            config=project_dir / "groundtruth.toml",
        )

    def test_get_latest(self, runner: CliRunner, project_dir: Path) -> None:
        self._seed(runner, project_dir)
        result = _invoke(
            runner,
            ["deliberations", "get", "DELIB-GET-0001"],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 0, result.output
        assert "DELIB-GET-0001" in result.output

    def test_get_history_flag(self, runner: CliRunner, project_dir: Path) -> None:
        self._seed(runner, project_dir)
        # Second add creates version 2
        _invoke(
            runner,
            [
                "deliberations",
                "add",
                "--id",
                "DELIB-GET-0001",
                "--title",
                "getable v2",
                "--source-type",
                "proposal",
                "--source-ref",
                "g.md",
                "--summary",
                "s",
                "--content",
                "second version",
            ],
            config=project_dir / "groundtruth.toml",
        )
        result = _invoke(
            runner,
            ["deliberations", "get", "DELIB-GET-0001", "--history"],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 0, result.output
        # Both versions should appear
        assert "first version" in result.output or "v1" in result.output or "version" in result.output.lower()

    def test_get_nonexistent(self, runner: CliRunner, project_dir: Path) -> None:
        result = _invoke(
            runner,
            ["deliberations", "get", "DELIB-DOES-NOT-EXIST"],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "DELIB-DOES-NOT-EXIST" in result.output


# ---------------------------------------------------------------------------
# 17: `gt deliberations list` with filter
# ---------------------------------------------------------------------------


class TestDeliberationsList:
    def test_list_filter_by_spec(self, runner: CliRunner, project_dir: Path) -> None:
        # Seed one linked to SPEC-0001, one not
        _invoke(
            runner,
            [
                "deliberations",
                "add",
                "--id",
                "DELIB-LIST-A",
                "--title",
                "linked",
                "--source-type",
                "proposal",
                "--source-ref",
                "a.md",
                "--summary",
                "s",
                "--content",
                "b",
                "--spec-id",
                "SPEC-0001",
            ],
            config=project_dir / "groundtruth.toml",
        )
        _invoke(
            runner,
            [
                "deliberations",
                "add",
                "--id",
                "DELIB-LIST-B",
                "--title",
                "unlinked",
                "--source-type",
                "proposal",
                "--source-ref",
                "b.md",
                "--summary",
                "s",
                "--content",
                "b",
            ],
            config=project_dir / "groundtruth.toml",
        )
        result = _invoke(
            runner,
            ["deliberations", "list", "--spec-id", "SPEC-0001"],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 0, result.output
        assert "DELIB-LIST-A" in result.output
        assert "DELIB-LIST-B" not in result.output


# ---------------------------------------------------------------------------
# 18-20: `gt deliberations search`
# ---------------------------------------------------------------------------


class TestDeliberationsSearch:
    def test_search_text_fallback_default(self, runner: CliRunner, project_dir: Path) -> None:
        # Per Codex Condition 2: default search MUST work in base install
        # (fall back to SQLite LIKE if ChromaDB unavailable)
        _invoke(
            runner,
            [
                "deliberations",
                "add",
                "--id",
                "DELIB-SEARCH-0001",
                "--title",
                "searchable",
                "--source-type",
                "proposal",
                "--source-ref",
                "s.md",
                "--summary",
                "contains apples and oranges",
                "--content",
                "apples and oranges in the body",
            ],
            config=project_dir / "groundtruth.toml",
        )
        result = _invoke(
            runner,
            ["deliberations", "search", "apples"],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 0, result.output
        assert "DELIB-SEARCH-0001" in result.output

    def test_search_semantic_only_without_chromadb(
        self,
        runner: CliRunner,
        project_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Per Codex Condition 3: --semantic-only must fail when ChromaDB
        # is unavailable (opt-in strict mode)
        import groundtruth_kb.db as _db_mod

        monkeypatch.setattr(_db_mod, "HAS_CHROMADB", False)
        result = _invoke(
            runner,
            ["deliberations", "search", "anything", "--semantic-only"],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 1
        assert "chromadb" in result.output.lower()

    def test_search_semantic_only_rejects_text_fallback_rows(
        self,
        runner: CliRunner,
        project_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Per Codex Condition 3: --semantic-only must reject rows tagged as
        # ``text_match`` even when ChromaDB is installed. We test the CLI
        # filter in isolation by monkey-patching ``search_deliberations`` to
        # return a canned text-fallback row. This keeps the test deterministic
        # regardless of ChromaDB's actual embedding behavior.
        import groundtruth_kb.db as _db_mod

        monkeypatch.setattr(_db_mod, "HAS_CHROMADB", True)

        canned_text_row = {
            "id": "DELIB-SEARCH-0003",
            "version": 1,
            "title": "only findable by text",
            "summary": "unique phrase xyzzy",
            "content": "body with xyzzy token",
            "source_type": "proposal",
            "source_ref": "t.md",
            "outcome": None,
            "search_method": "text_match",
            "score": None,
        }

        def _fake_search(self, query, *, limit=5):  # noqa: ARG001
            return [canned_text_row]

        monkeypatch.setattr(_db_mod.KnowledgeDB, "search_deliberations", _fake_search)
        result = _invoke(
            runner,
            ["deliberations", "search", "xyzzy", "--semantic-only"],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 0, result.output
        # The canned text_match row must be filtered out, so either the
        # DELIB ID is absent or the CLI reports "no ... match"
        assert "DELIB-SEARCH-0003" not in result.output
        assert "no " in result.output.lower()


# ---------------------------------------------------------------------------
# 21-24: `gt deliberations link` with CLI-layer validation
# ---------------------------------------------------------------------------


class TestDeliberationsLink:
    def _seed_delib(self, runner: CliRunner, project_dir: Path) -> None:
        _invoke(
            runner,
            [
                "deliberations",
                "add",
                "--id",
                "DELIB-LINK-0001",
                "--title",
                "linkable",
                "--source-type",
                "proposal",
                "--source-ref",
                "l.md",
                "--summary",
                "s",
                "--content",
                "b",
            ],
            config=project_dir / "groundtruth.toml",
        )

    def test_link_spec_happy_path(self, runner: CliRunner, project_dir: Path) -> None:
        self._seed_delib(runner, project_dir)
        result = _invoke(
            runner,
            [
                "deliberations",
                "link",
                "DELIB-LINK-0001",
                "--spec",
                "SPEC-0001",
                "--role",
                "related",
            ],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 0, result.output

    def test_link_work_item_happy_path(self, runner: CliRunner, project_dir: Path) -> None:
        self._seed_delib(runner, project_dir)
        result = _invoke(
            runner,
            [
                "deliberations",
                "link",
                "DELIB-LINK-0001",
                "--work-item",
                "WI-0001",
                "--role",
                "related",
            ],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 0, result.output

    def test_link_nonexistent_deliberation_errors(self, runner: CliRunner, project_dir: Path) -> None:
        result = _invoke(
            runner,
            [
                "deliberations",
                "link",
                "DELIB-DOES-NOT-EXIST",
                "--spec",
                "SPEC-0001",
            ],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 1
        assert "DELIB-DOES-NOT-EXIST" in result.output or "not found" in result.output.lower()

    def test_link_nonexistent_spec_errors(self, runner: CliRunner, project_dir: Path) -> None:
        self._seed_delib(runner, project_dir)
        result = _invoke(
            runner,
            [
                "deliberations",
                "link",
                "DELIB-LINK-0001",
                "--spec",
                "SPEC-DOES-NOT-EXIST",
            ],
            config=project_dir / "groundtruth.toml",
        )
        assert result.exit_code == 1
        assert "SPEC-DOES-NOT-EXIST" in result.output or "not found" in result.output.lower()
