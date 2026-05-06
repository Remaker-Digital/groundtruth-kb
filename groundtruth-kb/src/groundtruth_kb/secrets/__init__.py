# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Shared deterministic secret scanner used by git hooks, CI, doctor, and incident response.

Authority: bridge/gtkb-sec-redaction-commit-gate-001-004.md (Codex GO).

Anchored specifications (S333, MemBase v1):
- SPEC-SEC-SCAN-PROVIDER-COVERAGE-001: pattern coverage for the 17 initial provider classes.
- SPEC-SEC-SCAN-REDACTION-001: raw secret values never appear in scanner output.
- SPEC-SEC-SCANNER-CLI-001: ``gt secrets scan`` CLI surface (defined in groundtruth_kb.cli).
- SPEC-SEC-ALLOWLIST-001: fixture-only allowlist with exact value + path matching.

The public CLI exposes staged, range, path, tracked-file, and all-local-refs
checks through ``gt secrets scan``.
"""

from groundtruth_kb.secrets.allowlist import Allowlist, AllowlistEntry, AllowlistLoadError
from groundtruth_kb.secrets.patterns import PRODUCTION_PATTERNS, TEST_SYNTHETIC_PATTERNS, Severity
from groundtruth_kb.secrets.redaction import fingerprint, redact_for_output
from groundtruth_kb.secrets.scanner import (
    Finding,
    GitScanError,
    ScanResult,
    scan_all_refs,
    scan_paths,
    scan_range,
    scan_staged,
    scan_tracked,
    write_json_report,
)

__all__ = [
    "PRODUCTION_PATTERNS",
    "TEST_SYNTHETIC_PATTERNS",
    "Severity",
    "fingerprint",
    "redact_for_output",
    "Allowlist",
    "AllowlistEntry",
    "AllowlistLoadError",
    "Finding",
    "GitScanError",
    "ScanResult",
    "scan_all_refs",
    "scan_paths",
    "scan_range",
    "scan_staged",
    "scan_tracked",
    "write_json_report",
]
