# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Focused tests for batched range secret scanning."""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

import pytest
from groundtruth_kb.secrets import scanner
from groundtruth_kb.secrets.allowlist import Allowlist, AllowlistEntry
from groundtruth_kb.secrets.patterns import PatternEntry, Severity

TEST_PATTERN = PatternEntry(
    name="synthetic_range_token",
    severity=Severity.CANDIDATE_HIGH,
    pattern=re.compile(r"\bGTKB_TEST_RANGE_PATTERN_[A-Za-z0-9_-]{8,}\b"),
    description="Synthetic range scanner token",
)
TEST_VALUE = "GTKB_TEST_RANGE_PATTERN_" + ("x" * 8)


def test_scan_range_batches_unique_blobs_and_preserves_path_semantics(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    paths = [
        "tests/allowed.txt",
        "src/unique.txt",
        "src/duplicate.txt",
        "deleted.txt",
        ".tmp-cache/ignored.txt",
        "src/nonblob.txt",
        "src/binary.dat",
    ]
    tree = [
        ("blob-shared", "src/duplicate.txt"),
        ("blob-ignored", ".tmp-cache/ignored.txt"),
        ("blob-binary", "src/binary.dat"),
        ("blob-shared", "tests/allowed.txt"),
        ("blob-unique", "src/unique.txt"),
    ]
    contents = {
        "blob-shared": f"first line\n{TEST_VALUE}\n".encode(),
        "blob-unique": f"{TEST_VALUE}\n".encode(),
        "blob-binary": b"\x00binary",
    }
    calls: dict[str, object] = {"tree": 0, "batch": 0}

    def fake_git_lines(_repo_root: Path, args: list[str]) -> list[str]:
        assert args == ["diff", "--name-only", "--diff-filter=ACM", "base..head"]
        return paths

    def fake_tree_blobs(_repo_root: Path, ref_name: str) -> Iterable[tuple[str, str]]:
        assert ref_name == "head"
        calls["tree"] = int(calls["tree"]) + 1
        yield from tree

    def fake_blob_contents(_repo_root: Path, blob_ids: Iterable[str]) -> Iterable[tuple[str, bytes]]:
        requested = list(blob_ids)
        calls["batch"] = int(calls["batch"]) + 1
        calls["blob_ids"] = requested
        for blob_id in requested:
            yield blob_id, contents[blob_id]

    monkeypatch.setattr(scanner, "_git_lines", fake_git_lines)
    monkeypatch.setattr(scanner, "_git_tree_blobs", fake_tree_blobs)
    monkeypatch.setattr(scanner, "_iter_blob_contents", fake_blob_contents)
    monkeypatch.setattr(
        scanner,
        "_run_git",
        lambda *_args, **_kwargs: pytest.fail("scan_range must not issue per-path git show calls"),
    )

    allowlist = Allowlist(
        entries=(
            AllowlistEntry(
                value=TEST_VALUE,
                path="tests/allowed.txt",
                justification="Path-sensitive scanner test",
            ),
        )
    )
    result = scanner.scan_range(
        "base..head",
        repo_root=tmp_path,
        patterns=(TEST_PATTERN,),
        allowlist=allowlist,
    )

    assert calls == {
        "tree": 1,
        "batch": 1,
        "blob_ids": ["blob-shared", "blob-unique", "blob-binary"],
    }
    assert result.paths_scanned == 3
    assert [finding.path for finding in result.findings] == ["src/unique.txt", "src/duplicate.txt"]
    assert [finding.line for finding in result.findings] == [1, 2]
    assert all(finding.provider_class == TEST_PATTERN.name for finding in result.findings)
    assert all(finding.severity == Severity.CANDIDATE_HIGH for finding in result.findings)
    assert all(finding.fingerprint_prefix for finding in result.findings)
    assert TEST_VALUE not in str(result.to_json_dict())


@pytest.mark.parametrize("failing_helper", ["diff", "tree", "batch"])
def test_scan_range_fails_closed_for_git_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    failing_helper: str,
) -> None:
    def fake_git_lines(_repo_root: Path, _args: list[str]) -> list[str]:
        if failing_helper == "diff":
            raise scanner.GitScanError("diff failed")
        return ["src/file.txt"]

    def fake_tree_blobs(_repo_root: Path, _ref_name: str) -> Iterable[tuple[str, str]]:
        if failing_helper == "tree":
            raise scanner.GitScanError("tree failed")
        yield "blob-id", "src/file.txt"

    def fake_blob_contents(_repo_root: Path, _blob_ids: Iterable[str]) -> Iterable[tuple[str, bytes]]:
        if failing_helper == "batch":
            raise scanner.GitScanError("batch failed")
        yield "blob-id", b"plain text"

    monkeypatch.setattr(scanner, "_git_lines", fake_git_lines)
    monkeypatch.setattr(scanner, "_git_tree_blobs", fake_tree_blobs)
    monkeypatch.setattr(scanner, "_iter_blob_contents", fake_blob_contents)

    with pytest.raises(scanner.GitScanError, match=f"{failing_helper} failed"):
        scanner.scan_range("base..head", repo_root=tmp_path, patterns=(TEST_PATTERN,))


def test_scan_range_fails_closed_when_batch_omits_a_requested_blob(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(scanner, "_git_lines", lambda *_args: ["src/file.txt"])
    monkeypatch.setattr(scanner, "_git_tree_blobs", lambda *_args: iter([("blob-id", "src/file.txt")]))
    monkeypatch.setattr(scanner, "_iter_blob_contents", lambda *_args: iter(()))

    with pytest.raises(scanner.GitScanError, match="returned no content for: blob-id"):
        scanner.scan_range("base..head", repo_root=tmp_path, patterns=(TEST_PATTERN,))
