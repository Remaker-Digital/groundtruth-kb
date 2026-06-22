"""Tests for bridge embedded-evidence verification."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "bridge_verify_embedded_evidence.py"
CLAUSES_CONFIG = REPO_ROOT / "config" / "governance" / "adr-dcl-clauses.toml"


spec = importlib.util.spec_from_file_location("bridge_verify_embedded_evidence", SCRIPT_PATH)
assert spec is not None
verify = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["bridge_verify_embedded_evidence"] = verify
spec.loader.exec_module(verify)


def _write_source(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _bridge_content(
    *,
    bridge_id: str = "embedded-evidence",
    appendix_filename: str = "example.py",
    appendix_body: str = "print('ok')\n",
    target_path: str = "scripts/example.py",
    extra: str = "",
) -> str:
    return (
        "NEW\n\n"
        f"Document: {bridge_id}\n\n"
        f'target_paths: ["{target_path}"]\n\n'
        "## Implementation Evidence\n\n"
        f"### Appendix A1 - {appendix_filename}\n\n"
        "```python\n"
        f"{appendix_body}"
        "```\n"
        f"{extra}"
    )


def _write_bridge_chain(
    root: Path,
    *,
    bridge_id: str = "chain-thread",
    appendix_body: str = "print('ok')\n",
) -> None:
    bridge_dir = root / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    (bridge_dir / f"{bridge_id}-001.md").write_text(
        (
            "NEW\n\n"
            f"Document: {bridge_id}\n\n"
            'target_paths: ["scripts/example.py"]\n\n'
            "## Proposal\n\n"
            "Approved implementation scope.\n"
        ),
        encoding="utf-8",
    )
    (bridge_dir / f"{bridge_id}-002.md").write_text(
        f"GO\n\nDocument: {bridge_id}\n\n## Verdict\n\nGO.\n",
        encoding="utf-8",
    )
    (bridge_dir / f"{bridge_id}-003.md").write_text(
        (
            "NEW\n"
            "bridge_kind: implementation_report\n\n"
            f"Document: {bridge_id}\n\n"
            "## Implementation Evidence\n\n"
            "### Appendix A1 - example.py\n\n"
            "```python\n"
            f"{appendix_body}"
            "```\n"
        ),
        encoding="utf-8",
    )


def test_pass_when_appendix_matches_source(tmp_path: Path) -> None:
    _write_source(tmp_path, "scripts/example.py", "print('ok')\n")
    pending = tmp_path / "pending.md"
    pending.write_text(_bridge_content(), encoding="utf-8")

    report = verify.build_report(
        bridge_id="embedded-evidence",
        bridge_dir=tmp_path / "bridge",
        clauses_config=CLAUSES_CONFIG,
        content_file=pending,
    )

    assert report["passed"] is True
    assert report["summary"]["appendix_failures"] == 0
    assert report["appendices"][0]["status"] == "match"


def test_bridge_id_mode_resolves_report_appendix_against_proposal_targets(tmp_path: Path) -> None:
    _write_source(tmp_path, "scripts/example.py", "print('ok')\n")
    _write_bridge_chain(tmp_path)

    report = verify.build_report(
        bridge_id="chain-thread",
        bridge_dir=tmp_path / "bridge",
        clauses_config=CLAUSES_CONFIG,
    )

    assert report["passed"] is True
    assert report["operative_version"]["path"] == "bridge/chain-thread-003.md"
    assert report["target_path_source"] == {
        "mode": "approved_proposal",
        "path": "bridge/chain-thread-001.md",
    }
    assert report["target_paths"] == ["scripts/example.py"]
    assert report["appendices"][0]["status"] == "match"


def test_bridge_id_mode_fails_chain_resolved_appendix_hash_mismatch(tmp_path: Path) -> None:
    _write_source(tmp_path, "scripts/example.py", "print('source')\n")
    _write_bridge_chain(tmp_path, appendix_body="print('embedded')\n")

    report = verify.build_report(
        bridge_id="chain-thread",
        bridge_dir=tmp_path / "bridge",
        clauses_config=CLAUSES_CONFIG,
    )

    assert report["passed"] is False
    assert report["target_paths"] == ["scripts/example.py"]
    assert report["appendices"][0]["status"] == "mismatch"


def test_fail_on_appendix_hash_mismatch(tmp_path: Path) -> None:
    _write_source(tmp_path, "scripts/example.py", "print('source')\n")
    pending = tmp_path / "pending.md"
    pending.write_text(_bridge_content(appendix_body="print('embedded')\n"), encoding="utf-8")

    report = verify.build_report(
        bridge_id="embedded-evidence",
        bridge_dir=tmp_path / "bridge",
        clauses_config=CLAUSES_CONFIG,
        content_file=pending,
    )

    assert report["passed"] is False
    assert report["appendices"][0]["match"] is False
    assert report["appendices"][0]["status"] == "mismatch"


def test_fail_on_unresolved_appendix_filename(tmp_path: Path) -> None:
    _write_source(tmp_path, "scripts/example.py", "print('ok')\n")
    pending = tmp_path / "pending.md"
    pending.write_text(_bridge_content(appendix_filename="other.py"), encoding="utf-8")

    report = verify.build_report(
        bridge_id="embedded-evidence",
        bridge_dir=tmp_path / "bridge",
        clauses_config=CLAUSES_CONFIG,
        content_file=pending,
    )

    assert report["passed"] is False
    assert report["appendices"][0]["status"] == "unresolved"


def test_fail_on_root_boundary_pattern(tmp_path: Path) -> None:
    _write_source(tmp_path, "scripts/example.py", "print('ok')\n")
    pending = tmp_path / "pending.md"
    pending.write_text(
        _bridge_content(extra="\nOperator scratch path: C:\\Users\\micha\\scratch\\out.md\n"),
        encoding="utf-8",
    )

    report = verify.build_report(
        bridge_id="embedded-evidence",
        bridge_dir=tmp_path / "bridge",
        clauses_config=CLAUSES_CONFIG,
        content_file=pending,
    )

    assert report["passed"] is False
    assert report["summary"]["root_boundary_failures"] == 1
    assert report["root_boundary"]["lines"][0]["line"] > 0


def test_disclosure_exempt_span_not_flagged(tmp_path: Path) -> None:
    _write_source(tmp_path, "scripts/example.py", "print('ok')\n")
    pending = tmp_path / "pending.md"
    pending.write_text(
        _bridge_content(
            extra=(
                "\n<!-- in-root-disclosure -->\n"
                "Operator scratch path: C:\\Users\\micha\\scratch\\out.md\n"
                "<!-- /in-root-disclosure -->\n"
            )
        ),
        encoding="utf-8",
    )

    report = verify.build_report(
        bridge_id="embedded-evidence",
        bridge_dir=tmp_path / "bridge",
        clauses_config=CLAUSES_CONFIG,
        content_file=pending,
    )

    assert report["passed"] is True
    assert report["summary"]["root_boundary_failures"] == 0


def test_crlf_embedded_body_normalized_before_hash(tmp_path: Path) -> None:
    _write_source(tmp_path, "scripts/example.py", "print('ok')\nprint('done')\n")
    pending = tmp_path / "pending.md"
    pending.write_text(
        _bridge_content(appendix_body="print('ok')\r\nprint('done')\r\n"),
        encoding="utf-8",
        newline="",
    )

    report = verify.build_report(
        bridge_id="embedded-evidence",
        bridge_dir=tmp_path / "bridge",
        clauses_config=CLAUSES_CONFIG,
        content_file=pending,
    )

    assert report["passed"] is True
    assert report["appendices"][0]["match"] is True


def test_content_file_mode_resolves_without_bridge_dir(tmp_path: Path) -> None:
    _write_source(tmp_path, "scripts/example.py", "print('ok')\n")
    pending = tmp_path / "draft.md"
    pending.write_text(_bridge_content(bridge_id="draft-thread"), encoding="utf-8")

    rc = verify.main(["--content-file", str(pending), "--json"])

    assert rc == 0


def test_cli_command_forwards_to_helper(tmp_path: Path) -> None:
    from groundtruth_kb.cli import main

    _write_source(tmp_path, "scripts/example.py", "print('ok')\n")
    pending = tmp_path / "draft.md"
    pending.write_text(_bridge_content(bridge_id="draft-thread"), encoding="utf-8")

    result = CliRunner().invoke(
        main,
        ["bridge", "verify-embedded-evidence", "--content-file", str(pending), "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["bridge_id"] == "draft-thread"
    assert payload["passed"] is True
