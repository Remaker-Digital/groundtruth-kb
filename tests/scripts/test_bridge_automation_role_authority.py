"""Regression checks for automated bridge-scan role authority.

The Codex scanner performs Loyal Opposition review work. The Claude scanner
performs Prime Builder continuation work. Both must make that effective role
explicit and refuse to launch if the durable operating-role record disagrees.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BRIDGE_AUTOMATION = REPO_ROOT / "independent-progress-assessments" / "bridge-automation"


def test_common_bridge_scan_role_authority_guard_exists() -> None:
    common = (BRIDGE_AUTOMATION / "bridge-scan-common.ps1").read_text(encoding="utf-8")

    assert "function Test-BridgeScanRoleAuthority" in common
    assert ".claude\\rules\\operating-role.md" in common
    assert "ROLE-AUTHORITY-BLOCKED" in common
    assert "active_role:" in common
    assert "Allowed      = $false" in common
    assert "Allowed      = $true" in common


def test_common_bridge_status_helpers_cover_maintenance_states() -> None:
    common = (BRIDGE_AUTOMATION / "bridge-scan-common.ps1").read_text(encoding="utf-8")

    assert "function Get-BridgeStatusPattern" in common
    assert "function Get-BridgeEntries" in common
    assert "function Get-ActionableBridgeEntries" in common
    assert "PAUSED" in common
    assert "RETIRED" in common


def test_codex_review_scanner_requires_loyal_opposition_authority() -> None:
    scanner = (BRIDGE_AUTOMATION / "codex-file-bridge-scan.ps1").read_text(encoding="utf-8")

    assert "Test-BridgeScanRoleAuthority" in scanner
    assert '-ExpectedRole "loyal-opposition"' in scanner
    assert 'ScannerName "Codex automated Loyal Opposition bridge review scan"' in scanner
    assert "paused (role authority blocked)" in scanner
    assert "Effective role: Loyal Opposition" in scanner
    assert "Required durable role at spawn time: active_role:" in scanner
    assert "Observed durable role at spawn time: active_role:" in scanner
    assert "Before writing any review result, re-read `.claude/rules/operating-role.md`." in scanner
    assert "report `ROLE-AUTHORITY-BLOCKED`. Do not issue GO, NO-GO, or VERIFIED." in scanner
    assert "Every review file you create must include a `## Role Authority` section" in scanner
    assert "Do not claim `Reviewer: Codex Loyal" in scanner
    assert 'Get-ActionableBridgeEntries -Entries $entries -QueueOwner "LoyalOpposition"' in scanner


def test_claude_prime_scanner_requires_prime_builder_authority() -> None:
    scanner = (BRIDGE_AUTOMATION / "claude-file-bridge-scan.ps1").read_text(encoding="utf-8")

    assert "Test-BridgeScanRoleAuthority" in scanner
    assert '-ExpectedRole "prime-builder"' in scanner
    assert 'ScannerName "Claude automated Prime Builder bridge continuation scan"' in scanner
    assert "paused (role authority blocked)" in scanner
    assert "Effective role: Prime Builder" in scanner
    assert "Required durable role at spawn time: active_role:" in scanner
    assert "Observed durable role at spawn time: active_role:" in scanner
    assert "Before writing any implementation result, re-read `.claude/rules/operating-role.md`." in scanner
    assert "report `ROLE-AUTHORITY-BLOCKED`. Do not implement, revise, or file bridge" in scanner
    assert 'Get-ActionableBridgeEntries -Entries $entries -QueueOwner "PrimeBuilder"' in scanner
