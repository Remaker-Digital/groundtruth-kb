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
import subprocess
import sys
from pathlib import Path

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
    ("EC Private Key", re.compile(r"-----BEGIN EC PRIVATE KEY-----"), "high"),
    ("OpenSSH Private Key", re.compile(r"-----BEGIN OPENSSH PRIVATE KEY-----"), "high"),
    ("PGP Private Key", re.compile(r"-----BEGIN PGP PRIVATE KEY BLOCK-----"), "high"),
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

# File extensions to scan (text files only)
TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".md",
    ".txt",
    ".cfg",
    ".ini",
    ".env",
    ".sh",
    ".bash",
    ".ps1",
    ".bat",
    ".cmd",
    ".html",
    ".htm",
    ".css",
    ".scss",
    ".xml",
    ".sql",
    ".graphql",
    ".dockerfile",
    ".tf",
    ".hcl",
    ".rs",
    ".go",
    ".java",
    ".kt",
    ".rb",
    ".php",
    ".cs",
    ".swift",
    ".m",
    ".h",
    ".hpp",
    ".c",
    ".cpp",
    ".vue",
    ".svelte",
    ".astro",
    ".toml",
    ".lock",
}

# Directories/files to skip
SKIP_PATHS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".tox",
    "dist",
    "build",
    ".eggs",
    "*.egg-info",
}


def get_tracked_files() -> list[str]:
    """Get list of git-tracked files."""
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip().split("\n")


def get_staged_files() -> list[str]:
    """Get list of staged files (for pre-commit hook)."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    files = result.stdout.strip().split("\n")
    return [f for f in files if f]


def is_text_file(path: str) -> bool:
    """Check if a file should be scanned based on extension."""
    p = Path(path)
    # Check skip paths
    parts = p.parts
    for skip in SKIP_PATHS:
        if skip in parts:
            return False
    # Check extension
    suffix = p.suffix.lower()
    name_lower = p.name.lower()
    if suffix in TEXT_EXTENSIONS:
        return True
    # Files without extension but known text types
    if name_lower in (
        "dockerfile",
        "makefile",
        "procfile",
        ".env",
        ".gitignore",
        ".dockerignore",
        ".gitattributes",
        "gemfile",
        "rakefile",
    ):
        return True
    return False


def scan_file(filepath: str, project_root: Path) -> list[dict]:
    """Scan a single file for secret patterns."""
    findings = []
    full_path = project_root / filepath

    try:
        with open(full_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except (OSError, PermissionError):
        return findings

    lines = content.split("\n")

    for pattern_name, pattern, severity in PATTERNS:
        for line_num, line in enumerate(lines, 1):
            if pattern.search(line):
                # Skip if line is in a comment that looks like documentation/example
                stripped = line.strip()
                if any(
                    marker in stripped.lower()
                    for marker in [
                        "example:",
                        "placeholder",
                        "todo:",
                        "fixme:",
                        "your-",
                        "xxx",
                        "redacted",
                        "sample",
                        "template",
                        "<your",
                        "{{your",
                        "${your",
                    ]
                ):
                    continue
                # Skip regex pattern definitions (they contain secret-like strings but are patterns, not secrets)
                if "re.compile" in line or "regex" in line.lower():
                    continue
                # Redact the actual match for the report
                match = pattern.search(line)
                redacted = line[: max(0, match.start())] + "<REDACTED>" + line[match.end() :]
                findings.append(
                    {
                        "file": filepath,
                        "line": line_num,
                        "pattern": pattern_name,
                        "severity": severity,
                        "context": redacted.strip()[:120],
                    }
                )

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan for secrets in code")
    parser.add_argument("--staged", action="store_true", help="Scan only staged files (pre-commit mode)")
    args = parser.parse_args()

    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    project_root = Path(__file__).resolve().parent.parent

    if args.staged:
        files_to_scan = get_staged_files()
        print(f"Scanning {len(files_to_scan)} staged files...")
    else:
        files_to_scan = get_tracked_files()
        print(f"Scanning {len(files_to_scan)} tracked files...")

    all_findings = []
    scanned = 0

    for filepath in files_to_scan:
        if not filepath or not is_text_file(filepath):
            continue
        scanned += 1
        findings = scan_file(filepath, project_root)
        all_findings.extend(findings)

    print(f"Scanned {scanned} text files")
    print(f"Found {len(all_findings)} potential secret(s)")
    print()

    # Sort by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    all_findings.sort(key=lambda f: (severity_order.get(f["severity"], 9), f["file"], f["line"]))

    for finding in all_findings:
        sev = finding["severity"].upper()
        print(f"[{sev:6s}] {finding['file']}:{finding['line']}")
        print(f"         Pattern: {finding['pattern']}")
        print(f"         Context: {finding['context']}")
        print()

    # Output JSON summary
    summary_path = project_root / ".tmp" / "secrets_scan.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "total_findings": len(all_findings),
                "high": sum(1 for f in all_findings if f["severity"] == "high"),
                "medium": sum(1 for f in all_findings if f["severity"] == "medium"),
                "low": sum(1 for f in all_findings if f["severity"] == "low"),
                "findings": all_findings,
            },
            f,
            indent=2,
        )
    print(f"JSON summary: {summary_path}")

    return 0 if not any(f["severity"] == "high" for f in all_findings) else 1


if __name__ == "__main__":
    sys.exit(main())
