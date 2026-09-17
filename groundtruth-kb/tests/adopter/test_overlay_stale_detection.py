"""Doctor check 9: an existing cache is a derivation of the configured authority, never of a local store."""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.project.doctor_isolation import run_isolation_checks


def _check(adopter: Path, host: Path):
    checks = {check.name: check for check in run_isolation_checks(adopter, "dual-agent", product_root=host.parent)}
    return checks["isolation:chroma-regeneratable"]


def test_stale_chroma_without_configured_authority_emits_warning(clean_adopter) -> None:
    adopter, host = clean_adopter
    (adopter / ".groundtruth-chroma").mkdir()
    config = adopter / "groundtruth.toml"
    config.write_text(config.read_text(encoding="utf-8").replace("authority_url", "retired_url"), encoding="utf-8")
    check = _check(adopter, host)
    assert check.status == "warning" and "authority_url" in check.message


def test_chroma_with_configured_authority_passes(clean_adopter) -> None:
    adopter, host = clean_adopter
    (adopter / ".groundtruth-chroma").mkdir()
    check = _check(adopter, host)
    assert check.status == "pass" and "regeneratable from the configured authority" in check.message
    assert not list(adopter.rglob("groundtruth.db"))


def test_absent_cache_is_never_a_defect(clean_adopter) -> None:
    adopter, host = clean_adopter
    assert _check(adopter, host).status == "pass"
