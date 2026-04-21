# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
GroundTruth KB - D4 Azure CI/CD Scaffold.

Generates 12 GitHub Actions CI/CD skeleton files via ``gt scaffold cicd
--profile azure-enterprise``. Scaffold is one-shot and adopter-owned:
existing files are skipped (never overwritten). Dry-run mode is the default
(per D1/D2/D3 pattern); ``--apply`` writes to disk.

Authoritative source: bridge/gtkb-azure-cicd-gates-006.md GO.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = [
    "CicdScaffoldConfig",
    "CicdScaffoldReport",
    "scaffold_azure_cicd",
]


@dataclass(frozen=True)
class CicdScaffoldConfig:
    """Configuration for a CI/CD scaffold run.

    Attributes:
        profile: Currently only 'azure-enterprise' is supported. Future
            cloud-provider profiles (AWS, GCP) may be added later.
        target_dir: Root directory where the scaffold tree is written.
            Paths in each descriptor are interpreted relative to this root.
    """

    profile: str = "azure-enterprise"
    target_dir: Path = field(default_factory=lambda: Path("."))


@dataclass(frozen=True)
class CicdScaffoldReport:
    """Output of a ``scaffold_azure_cicd()`` call.

    Attributes:
        generated: List of ``{"target_path": str}`` entries that were (or would be)
            written.
        skipped: List of ``{"target_path": str, "reason": str}`` entries for files
            that already exist and were preserved.
        dry_run: True when the report came from a dry-run (no files written).
    """

    generated: list[dict[str, Any]] = field(default_factory=list)
    skipped: list[dict[str, Any]] = field(default_factory=list)
    dry_run: bool = True


def scaffold_azure_cicd(
    config: CicdScaffoldConfig,
    *,
    dry_run: bool = True,
) -> CicdScaffoldReport:
    """Generate 12 GitHub Actions CI/CD skeleton files for the given profile.

    By default (``dry_run=True``) nothing is written to disk - the return
    value is a ``CicdScaffoldReport`` showing which paths would be written
    and which would be skipped due to pre-existing files.

    When ``dry_run=False``, each descriptor whose target path does not
    already exist is written to disk. Existing files are preserved
    (scaffold is one-shot and adopter-owned; never overwrites).

    Args:
        config: Scaffold configuration (profile, target_dir).
        dry_run: If True (default), no files are written.

    Returns:
        CicdScaffoldReport with ``generated`` and ``skipped`` entries.

    Raises:
        ValueError: If ``config.profile`` is not 'azure-enterprise'.
    """
    if config.profile != "azure-enterprise":
        raise ValueError(f"Unsupported profile {config.profile!r}. Only 'azure-enterprise' is supported at D4.")

    # Late import keeps _azure_cicd_templates optional for non-azure callers.
    from groundtruth_kb._azure_cicd_templates import azure_cicd_templates

    generated: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    root = config.target_dir

    for descriptor in azure_cicd_templates():
        target_path = descriptor["target_path"]
        content = descriptor["content"]
        full_path = root / target_path

        if full_path.exists():
            skipped.append({"target_path": target_path, "reason": "file already exists"})
            continue

        if dry_run:
            generated.append({"target_path": target_path})
            continue

        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        generated.append({"target_path": target_path})

    return CicdScaffoldReport(
        generated=generated,
        skipped=skipped,
        dry_run=dry_run,
    )
