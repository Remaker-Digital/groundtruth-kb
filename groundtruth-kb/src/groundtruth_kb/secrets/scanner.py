# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Core scanner for redacted secret detection.

Anchored specifications:
- SPEC-SEC-SCAN-PROVIDER-COVERAGE-001
- SPEC-SEC-SCAN-REDACTION-001
- SPEC-SEC-SCANNER-CLI-001
- SPEC-SEC-ALLOWLIST-001

The scanner never returns raw matched values. Every finding carries only a
provider class, path, line, description, severity, and short SHA-256 fingerprint.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from groundtruth_kb.secrets.allowlist import Allowlist
from groundtruth_kb.secrets.patterns import PRODUCTION_PATTERNS, PatternEntry, Severity
from groundtruth_kb.secrets.redaction import fingerprint


@dataclass(frozen=True)
class Finding:
    provider_class: str
    severity: Severity
    path: str
    line: int
    fingerprint_prefix: str
    description: str
    ref: str | None = None
    object_id: str | None = None


@dataclass
class ScanResult:
    findings: list[Finding] = field(default_factory=list)
    paths_scanned: int = 0
    mode: str = "paths"

    @property
    def fail_on_severities(self) -> list[Severity]:
        return [f.severity for f in self.findings]

    def has_findings_at_or_above(self, threshold: tuple[Severity, ...]) -> bool:
        threshold_set = set(threshold)
        return any(f.severity in threshold_set for f in self.findings)

    def to_json_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "paths_scanned": self.paths_scanned,
            "finding_count": len(self.findings),
            "findings": [
                {
                    "provider_class": finding.provider_class,
                    "severity": finding.severity.value,
                    "path": finding.path,
                    "line": finding.line,
                    "fingerprint_prefix": finding.fingerprint_prefix,
                    "description": finding.description,
                    **({"ref": finding.ref} if finding.ref else {}),
                    **({"object_id": finding.object_id} if finding.object_id else {}),
                }
                for finding in self.findings
            ],
        }


class GitScanError(RuntimeError):
    """Raised when a git-backed scan cannot enumerate target content."""


_BINARY_SAMPLE_SIZE = 4096
_SKIP_DIR_PARTS = {
    ".git",
    ".hg",
    ".svn",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
}
_SKIP_PREFIXES = (
    ".tmp-",
    "memory/grafana/",
    "tools/grafana/",
    "admin/standalone/node_modules/",
    "admin/shopify/node_modules/",
    "widget/node_modules/",
)


def _is_probably_text(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            sample = handle.read(_BINARY_SAMPLE_SIZE)
    except OSError:
        return False
    return b"\x00" not in sample


def _is_probably_text_bytes(content: bytes) -> bool:
    return b"\x00" not in content[:_BINARY_SAMPLE_SIZE]


def _should_skip_relative_path(relative_posix: str) -> bool:
    parts = set(relative_posix.split("/"))
    if parts & _SKIP_DIR_PARTS:
        return True
    return any(relative_posix.startswith(prefix) for prefix in _SKIP_PREFIXES)


def _iter_files(paths: Iterable[Path], *, repo_root: Path) -> Iterable[Path]:
    def walk(directory: Path) -> Iterable[Path]:
        try:
            children = list(directory.iterdir())
        except OSError:
            return
        for child in children:
            relative_posix = _relative_posix(child.resolve(), repo_root)
            if child.is_dir():
                if _should_skip_relative_path(relative_posix + "/"):
                    continue
                yield from walk(child)
            elif child.is_file():
                yield child

    for entry in paths:
        if not entry.is_absolute():
            entry = repo_root / entry
        if entry.is_file():
            yield entry
        elif entry.is_dir():
            yield from walk(entry)


def _relative_posix(path: Path, repo_root: Path) -> str:
    try:
        relative = path.relative_to(repo_root)
    except ValueError:
        relative = path
    return str(relative).replace("\\", "/")


def _scan_text(
    text: str,
    *,
    relative_posix: str,
    patterns: tuple[PatternEntry, ...],
    allowlist: Allowlist,
) -> list[Finding]:
    findings: list[Finding] = []
    for line_index, line in enumerate(text.splitlines(), start=1):
        for entry in patterns:
            for match in entry.pattern.finditer(line):
                matched_value = match.group(0)
                if allowlist.matches(matched_value, relative_posix):
                    continue
                findings.append(
                    Finding(
                        provider_class=entry.name,
                        severity=entry.severity,
                        path=relative_posix,
                        line=line_index,
                        fingerprint_prefix=fingerprint(matched_value),
                        description=entry.description,
                    )
                )
    return findings


def scan_paths(
    paths: Iterable[Path],
    *,
    repo_root: Path,
    patterns: tuple[PatternEntry, ...] = PRODUCTION_PATTERNS,
    allowlist: Allowlist | None = None,
    mode: str = "paths",
) -> ScanResult:
    """Scan filesystem paths and return redacted findings."""
    repo_root = repo_root.resolve()
    allowlist = allowlist or Allowlist.empty()
    result = ScanResult(mode=mode)
    for absolute in _iter_files((Path(p) for p in paths), repo_root=repo_root):
        if not _is_probably_text(absolute):
            continue
        relative_posix = _relative_posix(absolute.resolve(), repo_root)
        if _should_skip_relative_path(relative_posix):
            continue
        result.paths_scanned += 1
        try:
            text = absolute.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        result.findings.extend(_scan_text(text, relative_posix=relative_posix, patterns=patterns, allowlist=allowlist))
    return result


def _run_git(repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=30,
    )


def _iter_blob_contents(repo_root: Path, blob_ids: Iterable[str]) -> Iterable[tuple[str, bytes]]:
    process = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        cwd=repo_root,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.stdin is None or process.stdout is None:
        raise GitScanError("failed to start git cat-file --batch")
    try:
        for blob_id in blob_ids:
            process.stdin.write(f"{blob_id}\n".encode("ascii"))
            process.stdin.flush()
            header = process.stdout.readline().decode("utf-8", errors="replace").strip()
            header_parts = header.split()
            if len(header_parts) < 3 or header_parts[1] != "blob":
                raise GitScanError(f"unexpected git cat-file header for {blob_id}: {header}")
            try:
                blob_size = int(header_parts[2])
            except ValueError as exc:
                raise GitScanError(f"unexpected git cat-file size for {blob_id}: {header}") from exc
            content = process.stdout.read(blob_size)
            process.stdout.read(1)
            yield blob_id, content
    finally:
        if process.stdin:
            process.stdin.close()
        stderr = process.stderr.read().decode("utf-8", errors="replace").strip() if process.stderr else ""
        return_code = process.wait(timeout=30)
        if return_code != 0:
            raise GitScanError(stderr or "git cat-file --batch failed")


def _git_lines(repo_root: Path, args: list[str]) -> list[str]:
    result = _run_git(repo_root, args)
    if result.returncode != 0:
        raise GitScanError(result.stderr.strip() or "git command failed")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def scan_staged(
    *,
    repo_root: Path,
    patterns: tuple[PatternEntry, ...] = PRODUCTION_PATTERNS,
    allowlist: Allowlist | None = None,
) -> ScanResult:
    """Scan staged ACM blobs from the git index."""
    repo_root = repo_root.resolve()
    allowlist = allowlist or Allowlist.empty()
    result = ScanResult(mode="staged")
    paths = _git_lines(repo_root, ["diff", "--cached", "--name-only", "--diff-filter=ACM"])
    for relative_posix in paths:
        if _should_skip_relative_path(relative_posix):
            continue
        blob = _run_git(repo_root, ["show", f":{relative_posix}"])
        if blob.returncode != 0:
            continue
        result.paths_scanned += 1
        result.findings.extend(
            _scan_text(blob.stdout, relative_posix=relative_posix, patterns=patterns, allowlist=allowlist)
        )
    return result


def scan_range(
    range_spec: str,
    *,
    repo_root: Path,
    patterns: tuple[PatternEntry, ...] = PRODUCTION_PATTERNS,
    allowlist: Allowlist | None = None,
) -> ScanResult:
    """Scan ACM blobs changed in ``base..head`` using head-side blob content."""
    repo_root = repo_root.resolve()
    allowlist = allowlist or Allowlist.empty()
    if ".." not in range_spec:
        raise GitScanError("--range must use <base>..<head> syntax")
    base_ref, head_ref = range_spec.split("..", 1)
    if not base_ref or not head_ref:
        raise GitScanError("--range must use <base>..<head> syntax")
    result = ScanResult(mode="range")
    paths = _git_lines(repo_root, ["diff", "--name-only", "--diff-filter=ACM", range_spec])
    for relative_posix in paths:
        if _should_skip_relative_path(relative_posix):
            continue
        blob = _run_git(repo_root, ["show", f"{head_ref}:{relative_posix}"])
        if blob.returncode != 0:
            continue
        result.paths_scanned += 1
        result.findings.extend(
            _scan_text(blob.stdout, relative_posix=relative_posix, patterns=patterns, allowlist=allowlist)
        )
    return result


def scan_tracked(
    *,
    repo_root: Path,
    patterns: tuple[PatternEntry, ...] = PRODUCTION_PATTERNS,
    allowlist: Allowlist | None = None,
    mode: str = "tracked",
) -> ScanResult:
    """Scan tracked working-tree files only."""
    repo_root = repo_root.resolve()
    paths = [repo_root / line for line in _git_lines(repo_root, ["ls-files"])]
    return scan_paths(paths, repo_root=repo_root, patterns=patterns, allowlist=allowlist, mode=mode)


def _git_ref_names(repo_root: Path) -> list[str]:
    return _git_lines(repo_root, ["for-each-ref", "--format=%(refname)"])


def _git_tree_blobs(repo_root: Path, ref_name: str) -> Iterable[tuple[str, str]]:
    result = _run_git(repo_root, ["ls-tree", "-r", "-z", "--full-tree", ref_name])
    if result.returncode != 0:
        raise GitScanError(result.stderr.strip() or f"git ls-tree failed for {ref_name}")
    for record in result.stdout.split("\0"):
        if not record:
            continue
        try:
            metadata, relative_posix = record.split("\t", 1)
        except ValueError:
            continue
        metadata_parts = metadata.split()
        if len(metadata_parts) < 3 or metadata_parts[1] != "blob":
            continue
        yield metadata_parts[2], relative_posix


def scan_all_refs(
    *,
    repo_root: Path,
    patterns: tuple[PatternEntry, ...] = PRODUCTION_PATTERNS,
    allowlist: Allowlist | None = None,
) -> ScanResult:
    """Scan blobs reachable from locally known refs without exposing raw values.

    This is a local incident-response inventory. It enumerates refs already
    present in the repository, including fetched remote-tracking refs, and does
    not fetch, push, rewrite, delete, or otherwise mutate remotes.
    """
    repo_root = repo_root.resolve()
    allowlist = allowlist or Allowlist.empty()
    result = ScanResult(mode="all-refs")
    blob_targets: dict[str, tuple[str, str]] = {}
    for ref_name in _git_ref_names(repo_root):
        for blob_id, relative_posix in _git_tree_blobs(repo_root, ref_name):
            if _should_skip_relative_path(relative_posix):
                continue
            if blob_id in blob_targets:
                continue
            blob_targets[blob_id] = (ref_name, relative_posix)
    for blob_id, blob_content in _iter_blob_contents(repo_root, blob_targets):
        if not _is_probably_text_bytes(blob_content):
            continue
        ref_name, relative_posix = blob_targets[blob_id]
        result.paths_scanned += 1
        text = blob_content.decode("utf-8", errors="replace")
        findings = _scan_text(
            text,
            relative_posix=relative_posix,
            patterns=patterns,
            allowlist=allowlist,
        )
        result.findings.extend(
            Finding(
                provider_class=finding.provider_class,
                severity=finding.severity,
                path=finding.path,
                line=finding.line,
                fingerprint_prefix=finding.fingerprint_prefix,
                description=finding.description,
                ref=ref_name,
                object_id=blob_id,
            )
            for finding in findings
        )
    return result


def write_json_report(result: ScanResult, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result.to_json_dict(), indent=2, sort_keys=True), encoding="utf-8")
