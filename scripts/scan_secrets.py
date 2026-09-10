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
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from groundtruth_kb.secrets import GitScanError, Severity, scan_staged, scan_tracked
from groundtruth_kb.secrets.patterns import PatternEntry

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
        scan = scan_staged if args.staged else scan_tracked
        result = scan(repo_root=Path.cwd(), patterns=patterns)
    except (GitScanError, OSError):
        # No raw Git stderr or file context: either can contain a credential.
        print(json.dumps({"status": "error", "reason": "secret_scan_unavailable"}), file=sys.stderr)
        return 2
    failed = result.has_findings_at_or_above((Severity.CANDIDATE_HIGH,))
    print(json.dumps({"status": "fail" if failed else "pass", **result.to_json_dict()}, ensure_ascii=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
