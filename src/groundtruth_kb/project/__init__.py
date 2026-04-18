# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Project scaffold, profiles, doctor, and upgrade — Layers 2 & 3."""

from groundtruth_kb.project.managed_registry import (
    DivergencePolicyEnum,
    OwnershipEnum,
    OwnershipMeta,
    UpgradePolicyEnum,
)
from groundtruth_kb.project.manifest import ProjectManifest, read_manifest, write_manifest
from groundtruth_kb.project.ownership import (
    ClassificationRow,
    OwnershipRecord,
    OwnershipResolver,
    render_classification_report_json,
    render_classification_report_markdown,
)
from groundtruth_kb.project.profiles import PROFILES, ProjectProfile, get_profile, list_profiles

__all__ = [
    "PROFILES",
    "ClassificationRow",
    "DivergencePolicyEnum",
    "OwnershipEnum",
    "OwnershipMeta",
    "OwnershipRecord",
    "OwnershipResolver",
    "ProjectManifest",
    "ProjectProfile",
    "UpgradePolicyEnum",
    "get_profile",
    "list_profiles",
    "read_manifest",
    "render_classification_report_json",
    "render_classification_report_markdown",
    "write_manifest",
]
