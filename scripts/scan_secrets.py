#!/usr/bin/env python3
"""Scan git-tracked files for potential secrets/credentials.

Patterns checked:
- AWS access keys (AKIA...)
- Azure connection strings
- Private keys (PEM headers)
- Generic password/secret assignments
- API keys/tokens in common formats
- SMTP passwords
- Database URIs with embedded credentials
- GitHub tokens (ghp_, gho_, ghu_, ghs_, ghr_)
- Bearer tokens
- Shared access signatures (SAS)

Synthetic allowlist (config/governance/secret-scan-allowlist.toml):
- A known synthetic finding (CI dummy value, redaction test fixture, runtime-generated
  token, placeholder) is attested there by exact identity: the repository path plus the
  SHA-256 of the flagged line's exact text. A finding with that identity is reported under
  ``allowlisted`` with the disposition "allowlisted (synthetic)", its identity and the
  entry's rationale, and does not fail the gate.
- Any byte change to an attested line changes its identity: the finding is reported again
  and the entry is reported under ``stale_allowlist``, which fails the gate until the entry
  is corrected or removed. Nobody can hide behind an entry whose line no longer exists.
- ``--staged`` reads the allowlist from the index (the version being committed) and
  evaluates only entries for staged paths; the tracked scan reads the working tree and
  evaluates every entry. A missing allowlist is empty; a malformed one fails the gate.
- Every other finding is reported exactly as before; candidate-high findings fail the gate.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

from groundtruth_kb.secrets import Finding, GitScanError, ScanResult, Severity, scan_staged, scan_tracked
from groundtruth_kb.secrets.patterns import PatternEntry

ALLOWLIST_PATH = "config/governance/secret-scan-allowlist.toml"
ALLOWLIST_SCHEMA_VERSION = 1
ALLOWLISTED_DISPOSITION = "allowlisted (synthetic)"
_ENTRY_KEYS = frozenset({"path", "line_sha256", "rationale"})
_SHA256_HEX = re.compile(r"[0-9a-f]{64}")

# Patterns: (name, regex, severity)
# severity: "high" = almost certainly a secret, "medium" = likely, "low" = suspicious
PATTERNS = [
    # Cloud provider keys
    ("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}", re.IGNORECASE), "high"),
    # AWS Secret Key: require assignment context to avoid false positives on git SHAs, hashes, etc.
    (
        "AWS Secret Key",
        re.compile(
            r'(?:aws_secret_access_key|secret_access_key)\s*[=:]\s*["\']?[A-Za-z0-9/+=]{40}["\']?', re.IGNORECASE
        ),
        "high",
    ),
    (
        "Azure Connection String",
        re.compile(r"(DefaultEndpointsProtocol|AccountName|AccountKey|SharedAccessSignature)=", re.IGNORECASE),
        "medium",
    ),
    ("Azure Account Key", re.compile(r"AccountKey=[A-Za-z0-9+/=]{40,}", re.IGNORECASE), "high"),
    ("Azure SAS Token", re.compile(r"[?&]sv=20\d\d-\d\d-\d\d&", re.IGNORECASE), "medium"),
    # Private keys
    ("RSA Private Key", re.compile(r"-----BEGIN (RSA )?PRIVATE KEY-----"), "high"),
    ("EC Private Key", re.compile(r"-----BEGIN " + r"EC PRIVATE KEY-----"), "high"),
    ("OpenSSH Private Key", re.compile(r"-----BEGIN " + r"OPENSSH PRIVATE KEY-----"), "high"),
    ("PGP Private Key", re.compile(r"-----BEGIN " + r"PGP PRIVATE KEY BLOCK-----"), "high"),
    ("Certificate", re.compile(r"-----BEGIN CERTIFICATE-----"), "low"),
    # GitHub tokens
    ("GitHub Token", re.compile(r"gh[poushr]_[A-Za-z0-9_]{36,}"), "high"),
    ("GitHub PAT (classic)", re.compile(r"[0-9a-f]{40}.*github", re.IGNORECASE), "medium"),
    # Generic secret patterns
    (
        "Password Assignment",
        re.compile(r'(?:password|passwd|pwd)\s*[=:]\s*["\']?[^\s"\'$]{8,}', re.IGNORECASE),
        "medium",
    ),
    (
        "Secret Key Assignment",
        re.compile(
            r'(?:secret|api[_-]?key|access[_-]?key|auth[_-]?token)\s*[=:]\s*["\']?[A-Za-z0-9+/=_-]{16,}', re.IGNORECASE
        ),
        "medium",
    ),
    ("Bearer Token", re.compile(r"Bearer\s+[A-Za-z0-9._\-]{20,}", re.IGNORECASE), "medium"),
    ("SMTP Password", re.compile(r"SMTP[_-]?(?:PASSWORD|PASS|PWD)\s*[=:]\s*\S+", re.IGNORECASE), "medium"),
    (
        "Connection String w/ Password",
        re.compile(r"(?:postgresql|mysql|mongodb|redis)://[^\s]*:[^\s@]*@[^\s]*", re.IGNORECASE),
        "high",
    ),
    # Titan email (known project credential)
    ("Titan SMTP Credential", re.compile(r"(?:titan|smtp\.titan)\.(?:email|com).*password", re.IGNORECASE), "high"),
    # Azure Cosmos/Redis keys
    ("Cosmos Primary Key", re.compile(r"[A-Za-z0-9+/=]{88}=="), "low"),
    # Common env var leaks in code
    (
        "Hardcoded env secret",
        re.compile(r'(?:os\.environ|getenv)\s*\(\s*["\'](?:SECRET|PASSWORD|TOKEN|KEY|CREDENTIAL)', re.IGNORECASE),
        "low",
    ),
]


class AllowlistError(ValueError):
    """The synthetic allowlist is malformed or unreadable; the gate fails closed."""


@dataclass(frozen=True)
class SyntheticEntry:
    """One attested synthetic line: exact path, exact line identity, and why it is synthetic."""

    path: str
    line_sha256: str
    rationale: str


def parse_allowlist(text: str) -> dict[tuple[str, str], SyntheticEntry]:
    """Parse the allowlist TOML; every entry must carry a valid path, identity and rationale."""
    try:
        raw = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise AllowlistError(f"{ALLOWLIST_PATH}: not valid TOML") from error
    if raw.get("schema_version") != ALLOWLIST_SCHEMA_VERSION:
        raise AllowlistError(f"{ALLOWLIST_PATH}: schema_version must be {ALLOWLIST_SCHEMA_VERSION}")
    rows = raw.get("entries", [])
    if not isinstance(rows, list):
        raise AllowlistError(f"{ALLOWLIST_PATH}: 'entries' must be an array of tables")
    entries: dict[tuple[str, str], SyntheticEntry] = {}
    for index, row in enumerate(rows):
        where = f"{ALLOWLIST_PATH} entries[{index}]"
        if not isinstance(row, dict):
            raise AllowlistError(f"{where}: must be a table")
        unknown = sorted(set(row) - _ENTRY_KEYS)
        if unknown:
            raise AllowlistError(f"{where}: unknown keys {unknown}")
        path, digest, rationale = row.get("path"), row.get("line_sha256"), row.get("rationale")
        if (
            not isinstance(path, str)
            or not path
            or path != path.strip()
            or "\\" in path
            or path.startswith("/")
            or ".." in path.split("/")
        ):
            raise AllowlistError(f"{where}: 'path' must be a relative POSIX repository path")
        if not isinstance(digest, str) or not _SHA256_HEX.fullmatch(digest):
            raise AllowlistError(f"{where}: 'line_sha256' must be 64 lowercase hex characters")
        if not isinstance(rationale, str) or not rationale.strip():
            raise AllowlistError(f"{where}: 'rationale' must say why the line is synthetic")
        key = (path, digest)
        if key in entries:
            raise AllowlistError(f"{where}: duplicates an earlier entry for {path}")
        entries[key] = SyntheticEntry(path=path, line_sha256=digest, rationale=rationale.strip())
    return entries


def _index_text(repo_root: Path, relative_posix: str) -> str | None:
    """Return the stage-0 index blob of ``relative_posix`` as text, or None when the index has no entry."""

    def git_bytes(args: list[str]) -> bytes:
        try:
            completed = subprocess.run(
                ["git", "--no-optional-locks", "--no-replace-objects", *args],
                cwd=repo_root,
                capture_output=True,
                timeout=30,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise GitScanError("staged_scan_unavailable: Git could not read the index") from error
        if completed.returncode:
            # Git diagnostics may contain filenames or values. Never echo them.
            raise GitScanError("staged_scan_unavailable: Git refused the index read")
        return completed.stdout

    records = git_bytes(["ls-files", "--stage", "-z", "--", relative_posix]).split(b"\0")
    listing = [record for record in records if record]
    if not listing:
        return None
    if len(listing) != 1:
        raise AllowlistError(f"{relative_posix}: the index holds an unmerged or ambiguous entry")
    metadata, _tab, listed_path = listing[0].partition(b"\t")
    fields = metadata.decode("ascii", errors="replace").split()
    if len(fields) != 3 or fields[2] != "0" or listed_path.decode("utf-8", errors="replace") != relative_posix:
        raise AllowlistError(f"{relative_posix}: the index holds an unmerged or ambiguous entry")
    if fields[0] not in {"100644", "100755"}:
        raise AllowlistError(f"{relative_posix}: the index entry is not a regular file")
    try:
        return git_bytes(["cat-file", "blob", fields[1]]).decode("utf-8")
    except UnicodeDecodeError as error:
        raise AllowlistError(f"{relative_posix}: the index blob is not UTF-8 text") from error


def load_allowlist(repo_root: Path, *, staged: bool) -> tuple[dict[tuple[str, str], SyntheticEntry], str]:
    """Load the allowlist that governs this scan and say where it came from.

    ``--staged`` reads the index blob, the version that the commit will carry, so an
    unstaged working-tree edit of the allowlist has no effect on the gate. The tracked scan
    reads the working tree. An absent allowlist is empty.
    """
    if staged:
        text = _index_text(repo_root, ALLOWLIST_PATH)
        source = "index"
    else:
        target = repo_root / ALLOWLIST_PATH
        source = "working-tree"
        try:
            text = target.read_text(encoding="utf-8") if target.is_file() else None
        except UnicodeDecodeError as error:
            raise AllowlistError(f"{ALLOWLIST_PATH}: not UTF-8 text") from error
    return (parse_allowlist(text) if text is not None else {}), source


def apply_allowlist(
    result: ScanResult,
    entries: dict[tuple[str, str], SyntheticEntry],
    *,
    staged: bool,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Split ``result.findings`` into live findings (kept) and allowlisted ones; list stale entries.

    An entry is stale when its path was scanned and no finding on that path carries the
    attested line identity (the line changed, moved to another file, or no longer matches a
    pattern). In ``--staged`` mode an entry whose path is not staged is out of scope; the
    tracked scan also reports an entry whose path is not a scanned tracked text file.
    """
    matched: set[tuple[str, str]] = set()
    remaining: list[Finding] = []
    allowlisted: list[dict[str, object]] = []
    for finding in result.findings:
        entry = entries.get((finding.path, finding.line_sha256 or ""))
        if entry is None:
            remaining.append(finding)
            continue
        matched.add((entry.path, entry.line_sha256))
        allowlisted.append(
            {
                "provider_class": finding.provider_class,
                "severity": finding.severity.value,
                "path": finding.path,
                "line": finding.line,
                "fingerprint_prefix": finding.fingerprint_prefix,
                "description": finding.description,
                "disposition": ALLOWLISTED_DISPOSITION,
                "line_sha256": entry.line_sha256,
                "rationale": entry.rationale,
            }
        )
    scanned = set(result.scanned_paths)
    stale: list[dict[str, object]] = []
    for key, entry in entries.items():
        if key in matched:
            continue
        if entry.path in scanned:
            reason = (
                "no finding on this path carries the attested line identity: the line's bytes changed "
                "or it no longer matches a pattern; correct or remove the entry"
            )
        elif staged:
            continue
        else:
            reason = "the path is not a scanned tracked text file; remove the entry"
        stale.append(
            {"path": entry.path, "line_sha256": entry.line_sha256, "rationale": entry.rationale, "reason": reason}
        )
    result.findings = remaining
    return allowlisted, stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan Git work without exposing credential values")
    parser.add_argument("--staged", action="store_true", help="Read exact changed index blobs")
    args = parser.parse_args(argv)
    patterns = tuple(
        PatternEntry(
            name=name,
            pattern=pattern,
            severity=Severity.CANDIDATE_HIGH if severity == "high" else Severity.CANDIDATE_MEDIUM,
            description=name,
        )
        for name, pattern, severity in PATTERNS
    )
    try:
        entries, allowlist_source = load_allowlist(Path.cwd(), staged=args.staged)
        scan = scan_staged if args.staged else scan_tracked
        result = scan(repo_root=Path.cwd(), patterns=patterns)
    except (GitScanError, OSError):
        # No raw Git stderr or file context: either can contain a credential.
        print(json.dumps({"status": "error", "reason": "secret_scan_unavailable"}), file=sys.stderr)
        return 2
    except AllowlistError as error:
        # The message names the allowlist path and entry index only, never scanned content.
        print(
            json.dumps({"status": "error", "reason": "secret_scan_allowlist_invalid", "detail": str(error)}),
            file=sys.stderr,
        )
        return 2
    allowlisted, stale = apply_allowlist(result, entries, staged=args.staged)
    failed = result.has_findings_at_or_above((Severity.CANDIDATE_HIGH,)) or bool(stale)
    report = {
        "status": "fail" if failed else "pass",
        **result.to_json_dict(),
        "allowlist_path": ALLOWLIST_PATH,
        "allowlist_source": allowlist_source,
        "allowlisted_count": len(allowlisted),
        "allowlisted": allowlisted,
        "stale_allowlist_count": len(stale),
        "stale_allowlist": stale,
    }
    print(json.dumps(report, ensure_ascii=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
