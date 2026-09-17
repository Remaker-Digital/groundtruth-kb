# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-5804 timer/threshold/concurrency inventory extractor tests.

The extractor is deterministic, read-only over inputs, and re-runnable. Tests
exercise the production payload function and the rendered artifact without
mutating any live runtime value.
"""

from __future__ import annotations

import hashlib
import tomllib
from pathlib import Path

import pytest

import scripts.timer_inventory as ti


@pytest.fixture
def fixture_root(tmp_path: Path) -> Path:
    """A synthetic GT-KB-like tree with production + test surfaces."""
    (tmp_path / "groundtruth.toml").write_text('[project]\nname = "fx"\n', encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "groundtruth-kb" / "src" / "groundtruth_kb").mkdir(parents=True)
    (tmp_path / "config" / "governance").mkdir(parents=True)
    (tmp_path / "config/governance/operational-controls.toml").write_text(
        "schema_version=2\ncontrols=[]\ninvariants=[]\n", encoding="utf-8"
    )
    (tmp_path / "platform_tests" / "scripts").mkdir(parents=True)
    return tmp_path


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_deterministic_byte_output(fixture_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(fixture_root / "scripts" / "a.py", "MAX_RETRIES = 3\nTIMEOUT_SECONDS = 10\n")
    monkeypatch.setattr(ti, "_git_head_sha", lambda *a: "deadbeef")
    payload1 = ti.build_inventory(fixture_root)
    payload2 = ti.build_inventory(fixture_root)
    t1 = ti.render_toml(payload1)
    t2 = ti.render_toml(payload2)
    assert hashlib.sha256(t1.encode()).digest() == hashlib.sha256(t2.encode()).digest()


def test_stable_ordering_and_identities(fixture_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(fixture_root / "scripts" / "b.py", "B_TIMEOUT = 20\n")
    _write(fixture_root / "scripts" / "a.py", "A_TIMEOUT = 10\n")
    monkeypatch.setattr(ti, "_git_head_sha", lambda *a: "deadbeef")
    payload = ti.build_inventory(fixture_root)
    identities = [record["identity"] for record in payload["records"]]
    assert identities == sorted(identities)
    # Both production records found with distinct identities.
    assert len(identities) == 2
    assert any("B_TIMEOUT" in ident for ident in identities)
    assert any("A_TIMEOUT" in ident for ident in identities)


def test_control_class_coverage(fixture_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    content = (
        "TIMEOUT_SECONDS = 10\n"
        "TTL_SECONDS = 30\n"
        "GRACE_WINDOW = 5\n"
        "MAX_RETRIES = 3\n"
        "RETRY_INTERVAL = 2\n"
        "BACKOFF_SECONDS = 1\n"
        "RATE_LIMIT = 100\n"
        "THRESHOLD_COUNT = 50\n"
        "CONCURRENCY_LIMIT = 4\n"
    )
    _write(fixture_root / "scripts" / "c.py", content)
    monkeypatch.setattr(ti, "_git_head_sha", lambda *a: "deadbeef")
    payload = ti.build_inventory(fixture_root)
    classes = {record["control_class"] for record in payload["records"]}
    for expected in (
        "timeout",
        "ttl",
        "grace",
        "retry_count",
        "retry_interval",
        "backoff",
        "rate_limit",
        "threshold",
        "concurrency_limit",
    ):
        assert expected in classes, f"missing control class {expected}"


def test_production_test_separation(fixture_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(fixture_root / "scripts" / "prod.py", "TIMEOUT_SECONDS = 10\n")
    _write(fixture_root / "platform_tests" / "scripts" / "t.py", "TIMEOUT_SECONDS = 99\n")
    monkeypatch.setattr(ti, "_git_head_sha", lambda *a: "deadbeef")
    payload = ti.build_inventory(fixture_root)
    assert payload["summary"]["production_record_count"] == 1
    assert payload["summary"]["test_record_count"] == 1
    assert all(r["surface"] == "production" for r in payload["records"])
    assert all(r["surface"] == "test" for r in payload["test_records"])


def test_schema_conformance(fixture_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(fixture_root / "scripts" / "d.py", "TIMEOUT_SECONDS = 10\n")
    monkeypatch.setattr(ti, "_git_head_sha", lambda *a: "deadbeef")
    payload = ti.build_inventory(fixture_root)
    assert payload["schema_version"] == 2
    assert payload["extraction_spec"]["version"] == ti.EXTRACTION_SPEC_VERSION
    assert "extraction_spec_digest" in payload
    record = payload["records"][0]
    for field in (
        "identity",
        "file",
        "line",
        "symbol",
        "value",
        "unit",
        "control_class",
        "category",
        "scope",
        "value_form",
        "current_authority",
        "hard_coded",
        "centralization_candidate",
        "migration_priority",
        "classification",
        "right_censored",
        "coupling",
    ):
        assert field in record, f"missing schema field {field}"


def test_right_censor_and_evidence_fields_present(fixture_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(fixture_root / "scripts" / "e.py", "TIMEOUT_SECONDS = 10\n")
    monkeypatch.setattr(ti, "_git_head_sha", lambda *a: "deadbeef")
    payload = ti.build_inventory(fixture_root)
    for record in payload["records"]:
        assert "right_censored" in record
        assert "failure_count" in record
        assert "success_count" in record
        assert "censor_count" in record
        assert "observed_failure_evidence" in record


def test_unclassified_or_ambiguous_visible(fixture_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(fixture_root / "scripts" / "f.py", "FOO_BAR = 7\nTIMEOUT_SECONDS = 10\n")
    monkeypatch.setattr(ti, "_git_head_sha", lambda *a: "deadbeef")
    payload = ti.build_inventory(fixture_root)
    # An unrecognised name cannot prove a numeric value is non-operational.
    assert payload["summary"]["production_record_count"] == 2
    assert payload["summary"]["unclassified_or_ambiguous_count"] == 1
    assert next(r for r in payload["records"] if r["symbol"] == "FOO_BAR")["classification"] == "unclassified_numeric"


def test_write_confinement_and_no_runtime_mutation(fixture_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(fixture_root / "scripts" / "g.py", "TIMEOUT_SECONDS = 10\n")
    monkeypatch.setattr(ti, "_git_head_sha", lambda *a: "deadbeef")
    # Snapshot all scanned files before.
    before: dict[str, bytes] = {}
    for path in list(fixture_root.rglob("*.py")) + list(fixture_root.rglob("*.toml")):
        before[str(path.relative_to(fixture_root))] = path.read_bytes()

    payload = ti.build_inventory(fixture_root)
    rendered = ti.render_toml(payload)
    artifact = fixture_root / ti.GENERATED_ARTIFACT_REL
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(rendered, encoding="utf-8")

    # After extraction, no source/config input changed.
    after: dict[str, bytes] = {}
    for path in list(fixture_root.rglob("*.py")) + list(fixture_root.rglob("*.toml")):
        rel = str(path.relative_to(fixture_root))
        if rel == str(ti.GENERATED_ARTIFACT_REL):
            continue
        after[rel] = path.read_bytes()
    assert before == after
    # Only the declared artifact was written.
    assert artifact.is_file()


@pytest.mark.parametrize("commit", [None, "deadbeef"])
@pytest.mark.parametrize("with_record", [False, True])
def test_rendered_inventory_parses_with_optional_values_and_empty_records(
    fixture_root: Path, monkeypatch: pytest.MonkeyPatch, commit: str | None, with_record: bool
) -> None:
    if with_record:
        _write(fixture_root / "scripts" / "timer.py", "TIMEOUT_SECONDS = 10\n")
    monkeypatch.setattr(ti, "_git_head_sha", lambda *a: commit)
    payload = ti.build_inventory(fixture_root)
    evidence = 'quoted "observation"\nwith a \\ path and unicode: \u03bb'
    if with_record:
        payload["records"][0]["observed_failure_evidence"] = evidence

    parsed = tomllib.loads(ti.render_toml(payload))

    assert parsed["metadata"].get("generating_commit") == commit
    assert parsed["summary"]["production_record_count"] == int(with_record)
    assert len(parsed["records"]) == int(with_record)
    if with_record:
        record = parsed["records"][0]
        assert record["value"] == "10"
        assert "failure_count" not in record
        assert "right_censored" not in record
        assert record["coupling"] == []
        assert "relaxed_first_candidate" not in record
        assert record["observed_failure_evidence"] == evidence
    else:
        assert parsed["records"] == []


def test_cli_write_then_check_does_not_inventory_generated_output(
    fixture_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write(fixture_root / "scripts" / "poll_run.py", "TIMEOUT_SECONDS = 10\n")
    monkeypatch.setattr(ti, "_git_head_sha", lambda *a: "deadbeef")
    arguments = ["--project-root", str(fixture_root)]

    assert ti.main([*arguments, "--write"]) == 0
    artifact = fixture_root / ti.GENERATED_ARTIFACT_REL
    first = artifact.read_bytes()
    assert ti.main([*arguments, "--check"]) == 0
    assert ti.main([*arguments, "--write"]) == 0
    assert artifact.read_bytes() == first
    records = ti.build_inventory(fixture_root)["records"]
    assert len(records) == 1
    assert records[0]["file"] == "scripts/poll_run.py"


def _live_catalog(root: Path) -> str:
    from groundtruth_kb.project.operational_control_config import CATALOG_RELATIVE_PATH

    catalog = Path(__file__).parents[2] / CATALOG_RELATIVE_PATH
    text = catalog.read_text(encoding="utf-8")
    (root / CATALOG_RELATIVE_PATH).write_text(text, encoding="utf-8")
    return text


def test_live_typed_values_and_all_consumer_keys_are_reported(fixture_root: Path) -> None:
    from groundtruth_kb.project.operational_control_config import CATALOG_RELATIVE_PATH

    source_text = _live_catalog(fixture_root)
    _write(
        fixture_root / "scripts" / "consumer.py",
        'wait = control_value(values, "registry.lock.acquire_seconds", unit="seconds")\n',
    )
    inventory = ti.build_inventory(fixture_root)
    values = [r for r in inventory["records"] if r["classification"] == "canonical_value"]
    assert len(values) == len(tomllib.loads(source_text)["controls"])
    assert {r["control_id"]: r["value"] for r in values} == {
        row["id"]: row["value"] for row in tomllib.loads(source_text)["controls"]
    }
    assert all(r["current_authority"] == CATALOG_RELATIVE_PATH.as_posix() for r in values)
    references = [r for r in inventory["records"] if r["classification"] == "control_reference"]
    assert [r["control_id"] for r in references] == ["registry.lock.acquire_seconds"]
    assert all(r["centralization_candidate"] == CATALOG_RELATIVE_PATH.as_posix() for r in inventory["records"])
    assert all("owning_work_item" not in r for r in inventory["records"])
    assert inventory["coverage"]["semantic_completeness"] == "unproven"


def test_python_ast_reports_every_assignment_defaults_and_renamed_values(fixture_root: Path) -> None:
    _write(
        fixture_root / "scripts" / "timing.py",
        """TIMEOUT = 1; RETRIES = 2
renamed = -3
def poll(deadline=4, *, max_items=5):
    sleep(6)
    call(timeout=7, retry_count=8)
    mapping = {"interval": "9"}
    return Decimal("0.25")
""",
    )
    rows = ti.build_inventory(fixture_root)["records"]
    assert len(rows) == 10
    assert {r["symbol"]: r["value"] for r in rows} == {
        "TIMEOUT": "1",
        "RETRIES": "2",
        "renamed": "-3",
        "deadline": "4",
        "max_items": "5",
        "sleep": "6",
        "timeout": "7",
        "retry_count": "8",
        "interval": "9",
        "Decimal": "0.25",
    }
    assert next(r for r in rows if r["symbol"] == "renamed")["classification"] == "unclassified_numeric"
    assert len({r["identity"] for r in rows}) == len(rows)


@pytest.mark.parametrize(
    "relative",
    [
        ".harness-baseline-configuration/rules/poll.md",
        ".githooks/pre-commit",
        "groundtruth-kb/templates/poll.sh.j2",
        "infrastructure/install.ps1",
        "applications/sample/start.mjs",
        "config/service.yaml",
        ".github/workflows/check.yml",
        "docs/operations.md",
        "README.md",
    ],
)
def test_declared_source_surfaces_are_visible(fixture_root: Path, relative: str) -> None:
    _write(fixture_root / relative, "wait_timeout = 42\nWait at least 7 seconds before retry.\n")
    inventory = ti.build_inventory(fixture_root)
    rows = [r for r in inventory["records"] if r["file"] == relative]
    assert {(r["value"], r["unit"]) for r in rows} == {("42", "seconds"), ("7", "seconds")}
    assert relative in {r["path"] for r in inventory["coverage"]["scanned_files"]}


@pytest.mark.parametrize(
    "extension,text",
    [("toml", '[service]\ntimeout="12.5"\ncount=3\n'), ("json", '{"service":{"timeout":"12.5","count":3}}')],
)
def test_structured_values_keep_field_path_and_unknown_units(fixture_root: Path, extension: str, text: str) -> None:
    _write(fixture_root / "config" / f"service.{extension}", text)
    rows = ti.build_inventory(fixture_root)["records"]
    assert {(r["symbol"], r["value"]) for r in rows} == {("service.timeout", "12.5"), ("service.count", "3")}
    assert next(r for r in rows if r["symbol"] == "service.count")["unit"] is None


@pytest.mark.parametrize(
    "problem", ["read", "encoding", "python_syntax", "toml_syntax", "missing_catalog", "invalid_catalog"]
)
def test_incomplete_inputs_return_diagnostics_and_nonzero_cli(
    fixture_root: Path, monkeypatch: pytest.MonkeyPatch, capsys, problem: str
) -> None:
    source = fixture_root / "scripts" / "poll.py"
    _write(source, "TIMEOUT=1\n")
    if problem == "read":
        original = Path.read_bytes

        def read_bytes(path):
            if path == source:
                raise PermissionError("private error must not be shown")
            return original(path)

        monkeypatch.setattr(Path, "read_bytes", read_bytes)
    elif problem == "encoding":
        source.write_bytes(b"\xff")
    elif problem == "python_syntax":
        source.write_text("timeout = (\n", encoding="utf-8")
    elif problem == "toml_syntax":
        _write(fixture_root / "config" / "broken.toml", "timeout = [\n")
    elif problem == "missing_catalog":
        (fixture_root / "config/governance/operational-controls.toml").unlink()
    elif problem == "invalid_catalog":
        (fixture_root / "config/governance/operational-controls.toml").write_text(
            "schema_version = 99\n", encoding="utf-8"
        )
    result = ti.build_inventory(fixture_root)
    assert result["coverage"]["status"] == "partial"
    assert result["coverage"]["diagnostics"]
    assert ti.main(["--project-root", str(fixture_root), "--json"]) == 1
    assert "private error must not be shown" not in capsys.readouterr().out


def _manifest(root: Path, paths: list[str]) -> None:
    import json

    _write(
        root / ".codex/.projection-manifest.json",
        json.dumps(
            {
                "engine": "scripts/harness_projection/project_harness.py",
                "baseline_root": ".harness-baseline-configuration",
                "harness": "codex",
                "paths": paths,
            }
        ),
    )


def test_projection_scan_reads_declared_files_and_preserves_private_harness_state(
    fixture_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _manifest(fixture_root, [".codex/rules/poll.md"])
    _write(fixture_root / ".codex/rules/poll.md", "poll_timeout=9\n")
    private = fixture_root / ".codex/sessions/private.json"
    _write(private, '{"password":"do not inspect","timeout":999}')
    original = Path.read_bytes

    def read_bytes(path):
        assert path != private
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    payload = ti.build_inventory(fixture_root)
    assert [(r["file"], r["value"]) for r in payload["derived_records"]] == [(".codex/rules/poll.md", "9")]
    assert payload["records"] == []
    parsed = tomllib.loads(ti.render_toml(payload))
    assert parsed["derived_records"][0]["value"] == "9"
    assert "do not inspect" not in str(payload)


@pytest.mark.parametrize(
    "path",
    [
        "../foreign.py",
        ".codex/../../foreign.py",
        ".codex/sessions",
        ".codex/dir",
        ".codex/unsafe\\file.py",
        "C:/foreign.py",
    ],
)
def test_malformed_or_directory_projection_entries_never_expand_the_scan(fixture_root: Path, path: str) -> None:
    _write(fixture_root / ".codex/dir/hidden.py", "TIMEOUT=888\n")
    _write(fixture_root / ".codex/sessions/private.py", "TIMEOUT=999\n")
    _manifest(fixture_root, [path])
    payload = ti.build_inventory(fixture_root)
    assert not payload["derived_records"]
    assert all(
        r["value"] not in {"888", "999"}
        for group in ("records", "test_records", "derived_records")
        for r in payload[group]
    )
    assert payload["coverage"]["diagnostics"] or any(
        r["reason"] == "private_or_runtime_boundary" for r in payload["coverage"]["excluded_paths"]
    )


def test_foreign_runtime_and_secret_paths_are_excluded_before_read(
    fixture_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    relatives = [
        "scripts/.worktrees/foreign/code.py",
        "infrastructure/credentials/pg_service.conf",
        "applications/sample/.venv/config.py",
        "config/.env.local",
        "config/access-token.json",
    ]
    for relative in relatives:
        _write(fixture_root / relative, "TIMEOUT=777\n")
    original = Path.read_bytes

    def read_bytes(path):
        assert path.relative_to(fixture_root).as_posix() not in relatives
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    payload = ti.build_inventory(fixture_root)
    assert not payload["records"]
    assert all(
        r["value"] not in {"777"} for group in ("records", "test_records", "derived_records") for r in payload[group]
    )
    assert len(
        [r for r in payload["coverage"]["excluded_paths"] if r["reason"] == "private_or_runtime_boundary"]
    ) == len(relatives)


def test_actual_linked_directory_is_never_read(
    fixture_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import os
    import subprocess

    outside = tmp_path.parent / (tmp_path.name + "-outside")
    outside.mkdir()
    private = outside / "hidden.py"
    private.write_text("TIMEOUT=777\n", encoding="utf-8")
    link = fixture_root / "scripts/linked"
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)], check=True, capture_output=True)
    else:
        link.symlink_to(outside, target_is_directory=True)
    payload = ti.build_inventory(fixture_root)
    assert payload["coverage"]["status"] == "partial"
    assert any(d["code"] == "redirected_path" for d in payload["coverage"]["diagnostics"])
    assert not payload["records"]
    assert private.read_text(encoding="utf-8") == "TIMEOUT=777\n"


def test_current_catalog_change_is_visible(fixture_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    original = ti.load_operational_control_catalog

    def changed(root):
        catalog = original(root)
        with (root / ti.CATALOG_RELATIVE_PATH).open("a", encoding="utf-8") as stream:
            stream.write("\n# owner edited during scan\n")
        return catalog

    monkeypatch.setattr(ti, "load_operational_control_catalog", changed)
    payload = ti.build_inventory(fixture_root)
    assert any(d["code"] == "catalog_changed" for d in payload["coverage"]["diagnostics"])
    assert payload["coverage"]["status"] == "partial"


def test_unknown_control_reference_and_measurement_absence_stay_explicit(fixture_root: Path) -> None:
    _write(
        fixture_root / "scripts/poll.py",
        'wait=control_value(values,"registry.lock.unknown_timeout",unit="seconds")\nTIMEOUT=12\n',
    )
    payload = ti.build_inventory(fixture_root)
    assert payload["summary"]["unclassified_or_ambiguous_count"] == 1
    assert any(r["classification"] == "unresolved_reference" for r in payload["records"])
    for row in payload["records"]:
        assert row["failure_count"] is row["success_count"] is row["censor_count"] is row["right_censored"] is None
    parsed = tomllib.loads(ti.render_toml(payload))
    assert all("failure_count" not in row and "right_censored" not in row for row in parsed["records"])


def test_regeneration_reports_all_surfaces_and_preserves_source_bytes(
    fixture_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write(fixture_root / "scripts/poll.py", "TIMEOUT=5\n")
    _write(fixture_root / "tests/poll.py", "TIMEOUT=9\n")
    _manifest(fixture_root, [".codex/rules/poll.md"])
    _write(fixture_root / ".codex/rules/poll.md", "timeout=8\n")
    monkeypatch.setattr(ti, "_git_head_sha", lambda *args: "deadbeef")
    before = {p.relative_to(fixture_root).as_posix(): p.read_bytes() for p in fixture_root.rglob("*") if p.is_file()}
    assert ti.main(["--project-root", str(fixture_root), "--write"]) == 0
    artifact = fixture_root / ti.GENERATED_ARTIFACT_REL
    first = artifact.read_bytes()
    assert ti.main(["--project-root", str(fixture_root), "--check"]) == 0
    assert ti.main(["--project-root", str(fixture_root), "--write"]) == 0
    assert artifact.read_bytes() == first
    parsed = tomllib.loads(first.decode("utf-8"))
    assert [r["value"] for r in parsed["records"]] == ["5"]
    assert [r["value"] for r in parsed["test_records"]] == ["9"]
    assert [r["value"] for r in parsed["derived_records"]] == ["8"]
    assert all((fixture_root / path).read_bytes() == content for path, content in before.items())


def test_output_parent_junction_refuses_without_writing_outside(fixture_root: Path, tmp_path: Path) -> None:
    import os
    import subprocess

    outside = tmp_path.parent / (tmp_path.name + "-output")
    outside.mkdir()
    protected = outside / "timer-inventory.toml"
    protected.write_text("owner bytes", encoding="utf-8")
    parent = fixture_root / "config/governance"
    assert parent.resolve().is_relative_to(fixture_root.resolve())
    parent.rename(fixture_root / "saved-control-fixture")
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(parent), str(outside)], check=True, capture_output=True)
    else:
        parent.symlink_to(outside, target_is_directory=True)
    assert ti.main(["--project-root", str(fixture_root), "--write"]) == 1
    assert protected.read_text(encoding="utf-8") == "owner bytes"
    assert sorted(p.name for p in outside.iterdir()) == ["timer-inventory.toml"]


def test_profile_selected_nested_projection_outputs_are_scanned(fixture_root: Path) -> None:
    import json

    _write(
        fixture_root / "scripts/harness_projection/profiles.toml",
        '[harnesses.fixture]\nconfig_dir=".api-harness/fixture"\n',
    )
    _write(
        fixture_root / ".api-harness/fixture/.projection-manifest.json",
        json.dumps(
            {
                "engine": "scripts/harness_projection/project_harness.py",
                "baseline_root": ".harness-baseline-configuration",
                "paths": [".api-harness/fixture/rules/poll.md"],
            }
        ),
    )
    _write(fixture_root / ".api-harness/fixture/rules/poll.md", "timeout=3\n")
    payload = ti.build_inventory(fixture_root)
    assert payload["coverage"]["status"] == "declared_inputs_read"
    assert [(r["file"], r["value"]) for r in payload["derived_records"]] == [
        (".api-harness/fixture/rules/poll.md", "3")
    ]


def test_application_data_documents_and_conversations_are_not_read(
    fixture_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    relatives = [
        "applications/sample/docs/owner-messages-all.json",
        "applications/sample/docs/extraction.json",
        "docs/conversation-history.md",
    ]
    for rel in relatives:
        _write(fixture_root / rel, "TIMEOUT=789\n")
    original = Path.read_bytes

    def read_bytes(path):
        assert path.relative_to(fixture_root).as_posix() not in relatives
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    payload = ti.build_inventory(fixture_root)
    assert not payload["records"]
    assert all(
        r["value"] not in {"789"} for group in ("records", "test_records", "derived_records") for r in payload[group]
    )
    assert all(any(r["path"] == rel for r in payload["coverage"]["excluded_paths"]) for rel in relatives)


def test_application_bundles_are_separate_derived_observations(fixture_root: Path) -> None:
    _write(fixture_root / "applications/sample/src/poll.js", "timeout=4\n")
    _write(fixture_root / "applications/sample/dist/poll.js", "timeout=4\n")
    payload = ti.build_inventory(fixture_root)
    assert [r["file"] for r in payload["records"]] == ["applications/sample/src/poll.js"]
    assert [r["file"] for r in payload["derived_records"]] == ["applications/sample/dist/poll.js"]


def test_python_labels_never_echo_string_call_arguments_and_unicode_offsets_are_exact(fixture_root: Path) -> None:
    _write(fixture_root / "scripts/poll.py", 'client("private connection text").sleep(15)\nλ = 2; timeout = -3\n')
    payload = ti.build_inventory(fixture_root)
    assert "private connection text" not in str(payload)
    assert {(r["symbol"], r["value"]) for r in payload["records"]} == {
        ("client().sleep", "15"),
        ("λ", "2"),
        ("timeout", "-3"),
    }


def _probe_fixture(root: Path, value: str = "0.25") -> None:
    import tomlkit

    _live_catalog(root)
    path = root / ti.CATALOG_RELATIVE_PATH
    document = tomlkit.parse(path.read_text(encoding="utf-8"))
    row = next(r for r in document["controls"] if r["id"] == "inventory.git_probe_seconds")
    row["value"] = value
    path.write_bytes(tomlkit.dumps(document).encode("utf-8"))
    (root / ".git").mkdir()


def test_git_probe_receives_configured_bound_and_same_operation_snapshot(
    fixture_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import subprocess

    import tomlkit
    from groundtruth_kb.project.operational_control_config import set_operational_controls

    _probe_fixture(fixture_root)
    path = fixture_root / ti.CATALOG_RELATIVE_PATH
    document = tomlkit.parse(path.read_text(encoding="utf-8"))
    row = next(r for r in document["controls"] if r["id"] == "inventory.git_probe_seconds")
    row["value"] = "0.5"
    proposed = tomlkit.dumps(document).encode("utf-8")
    calls = []

    def probe(argv, **options):
        calls.append((argv, options["timeout"]))
        if len(calls) == 1:
            snapshot = ti.load_operational_control_catalog(fixture_root)
            set_operational_controls(fixture_root, proposed, expected_sha256=snapshot.catalog_sha256)
        return subprocess.CompletedProcess(argv, 0, stdout="a" * 40 + "\n", stderr="")

    monkeypatch.setattr(ti.subprocess, "run", probe)
    first = ti.build_inventory(fixture_root)
    second = ti.build_inventory(fixture_root)
    assert [timeout for _argv, timeout in calls] == [0.25, 0.5]
    assert all(
        argv == ["git", "--no-optional-locks", "-C", str(fixture_root), "rev-parse", "HEAD"] for argv, _ in calls
    )
    assert first["generating_commit"] == second["generating_commit"] == "a" * 40
    assert any(d["code"] == "catalog_changed" for d in first["coverage"]["diagnostics"])
    assert second["coverage"]["status"] == "declared_inputs_read"


@pytest.mark.parametrize(
    "problem", ["missing_key", "missing_catalog", "malformed", "unit", "kind", "inactive", "binding", "negative"]
)
def test_git_probe_bad_control_refuses_before_launch(
    fixture_root: Path, monkeypatch: pytest.MonkeyPatch, problem: str
) -> None:
    import tomlkit

    _probe_fixture(fixture_root)
    path = fixture_root / ti.CATALOG_RELATIVE_PATH
    document = tomlkit.parse(path.read_text(encoding="utf-8"))
    row = next(r for r in document["controls"] if r["id"] == "inventory.git_probe_seconds")
    if problem == "missing_key":
        document["controls"] = [r for r in document["controls"] if r["id"] != "inventory.git_probe_seconds"]
    elif problem == "unit":
        row["unit"] = "count"
    elif problem == "kind":
        row["numeric_kind"] = "integer"
        row["minimum"] = "1"
        row["value"] = "2"
    elif problem == "inactive":
        row["migration_state"] = "candidate"
    elif problem == "binding":
        row["consumers"] = ["other.consumer"]
    elif problem == "negative":
        row["minimum"] = "-1"
        row["value"] = "-0.5"
    path.write_bytes(tomlkit.dumps(document).encode("utf-8"))
    if problem == "missing_catalog":
        path.unlink()
    elif problem == "malformed":
        path.write_text("bad = [", encoding="utf-8")
    before = path.read_bytes() if path.exists() else None

    def forbidden(*args, **kwargs):
        raise AssertionError("Invalid control must refuse before creating a process")

    monkeypatch.setattr(ti.subprocess, "run", forbidden)
    payload = ti.build_inventory(fixture_root)
    assert payload["generating_commit"] is None
    assert payload["coverage"]["status"] == "partial"
    assert any(d["code"] == "git_metadata_unavailable" for d in payload["coverage"]["diagnostics"])
    assert (path.read_bytes() if path.exists() else None) == before


@pytest.mark.parametrize("problem", ["timeout", "failure", "invalid_revision", "missing_executable"])
def test_git_metadata_failure_is_visible_without_fabricated_revision(
    fixture_root: Path, monkeypatch: pytest.MonkeyPatch, capsys, problem: str
) -> None:
    import subprocess

    _probe_fixture(fixture_root)

    def probe(argv, **options):
        assert options["timeout"] == 0.25
        if problem == "timeout":
            raise subprocess.TimeoutExpired(argv, options["timeout"])
        if problem == "missing_executable":
            raise FileNotFoundError("private path must not be displayed")
        return subprocess.CompletedProcess(
            argv,
            1 if problem == "failure" else 0,
            stdout="invalid revision",
            stderr="private stderr must not be displayed",
        )

    monkeypatch.setattr(ti.subprocess, "run", probe)
    payload = ti.build_inventory(fixture_root)
    assert payload["generating_commit"] is None
    assert payload["coverage"]["status"] == "partial"
    assert any(d["code"] == "git_metadata_unavailable" for d in payload["coverage"]["diagnostics"])
    assert ti.main(["--project-root", str(fixture_root), "--json"]) == 1
    output = capsys.readouterr().out
    assert "private path" not in output and "private stderr" not in output


def test_absent_git_metadata_does_not_launch_or_require_probe_control(
    fixture_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*args, **kwargs):
        raise AssertionError("A root without Git metadata must not launch a probe")

    monkeypatch.setattr(ti.subprocess, "run", forbidden)
    payload = ti.build_inventory(fixture_root)
    assert payload["generating_commit"] is None
    assert payload["coverage"]["status"] == "declared_inputs_read"


def test_stalled_probe_is_terminated_by_the_configured_fixture_bound(
    fixture_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import subprocess
    import sys
    import time

    _probe_fixture(fixture_root, "0.05")
    real_run = subprocess.run

    def stalled(argv, **options):
        assert options["timeout"] == 0.05
        return real_run([sys.executable, "-P", "-c", "import time; time.sleep(2)"], **options)

    monkeypatch.setattr(ti.subprocess, "run", stalled)
    started = time.monotonic()
    payload = ti.build_inventory(fixture_root)
    elapsed = time.monotonic() - started
    assert elapsed < 5
    assert payload["generating_commit"] is None
    assert any(
        d["code"] == "git_metadata_unavailable" and d["detail"] == "TimeoutExpired"
        for d in payload["coverage"]["diagnostics"]
    )
