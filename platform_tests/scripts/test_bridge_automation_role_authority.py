"""Regression checks for automated bridge-scan role authority.

The Codex scanner performs Loyal Opposition review work. The Claude scanner
performs Prime Builder continuation work. Both must make that effective role
explicit and refuse to launch if the single role assignment map disagrees.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BRIDGE_AUTOMATION = REPO_ROOT / "archive" / "os-poller-2026-04-25"


def test_common_bridge_scan_role_authority_guard_exists() -> None:
    common = (BRIDGE_AUTOMATION / "bridge-scan-common.ps1").read_text(encoding="utf-8")

    assert "function Test-BridgeScanRoleAuthority" in common
    assert "function Get-BridgeScanHarnessId" in common
    assert "harness-state\\harness-identities.json" in common
    assert "harness-state\\harness-registry.json" in common
    assert "ConvertFrom-Json" in common
    assert "ROLE-AUTHORITY-BLOCKED" in common
    assert "Allowed      = $false" in common
    assert "Allowed      = $true" in common


def test_common_bridge_snapshot_helpers_are_available() -> None:
    common = (BRIDGE_AUTOMATION / "bridge-scan-common.ps1").read_text(encoding="utf-8")

    assert "function Get-IndexEntryTopVersion" in common
    assert "function Test-SnapshotStillFresh" in common
    assert "function Invoke-GuardedLaunch" in common
    assert "SNAPSHOT-STALE" in common


def test_codex_review_scanner_requires_loyal_opposition_authority() -> None:
    scanner = (BRIDGE_AUTOMATION / "codex-file-bridge-scan.ps1").read_text(encoding="utf-8")

    assert "Test-BridgeScanRoleAuthority" in scanner
    assert '$HarnessName = "codex"' in scanner
    assert "Get-BridgeScanHarnessId" in scanner
    assert '$HarnessId = "A"' not in scanner
    assert '-ExpectedRole "loyal-opposition"' in scanner
    assert 'ScannerName "Codex automated Loyal Opposition bridge review scan"' in scanner
    assert "paused (role authority blocked)" in scanner
    assert "Effective role: Loyal Opposition" in scanner
    assert "Role map source: harness-state/harness-registry.json" in scanner
    assert "Required durable role at spawn time: harness" in scanner
    assert "Observed durable role at spawn time: harness" in scanner
    assert "Before writing any review result, re-read `harness-state/harness-registry.json`." in scanner
    assert "report `ROLE-AUTHORITY-BLOCKED`. Do not issue GO, NO-GO, or VERIFIED." in scanner
    assert "Every review file you create must include a `## Role Authority` section" in scanner


def test_claude_prime_scanner_requires_prime_builder_authority() -> None:
    scanner = (BRIDGE_AUTOMATION / "claude-file-bridge-scan.ps1").read_text(encoding="utf-8")

    assert "Test-BridgeScanRoleAuthority" in scanner
    assert '$HarnessName = "claude"' in scanner
    assert "Get-BridgeScanHarnessId" in scanner
    assert '$HarnessId = "B"' not in scanner
    assert '-ExpectedRole "prime-builder"' in scanner
    assert 'ScannerName "Claude automated Prime Builder bridge continuation scan"' in scanner
    assert "paused (role authority blocked)" in scanner
    assert "Effective role: Prime Builder" in scanner
    assert "Role map source: harness-state/harness-registry.json" in scanner
    assert "Required durable role at spawn time: harness" in scanner
    assert "Observed durable role at spawn time: harness" in scanner
    assert "Before writing any implementation result, re-read `harness-state/harness-registry.json`." in scanner
    assert "report `ROLE-AUTHORITY-BLOCKED`." in scanner
    assert "Do not implement, revise, or file bridge updates." in scanner
