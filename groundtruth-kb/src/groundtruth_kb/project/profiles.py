# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Profile definitions and registry for project scaffolding."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectProfile:
    """A project scaffold profile defining which layers to include."""

    name: str
    display_name: str
    description: str
    includes_bridge: bool
    includes_docker: bool
    includes_cloud: bool
    includes_ci: bool
    template_sets: tuple[str, ...]


PROFILES: dict[str, ProjectProfile] = {
    "local-only": ProjectProfile(
        name="local-only",
        display_name="Local Only",
        description=("Minimal application files and native authority configuration; no containers or cloud stubs."),
        includes_bridge=False,
        includes_docker=False,
        includes_cloud=False,
        includes_ci=False,
        template_sets=("base",),
    ),
    "dual-agent": ProjectProfile(
        name="dual-agent",
        display_name="Dual Agent",
        description=("Application development files with standard CI. Agent roles are explicit context input."),
        includes_bridge=True,
        includes_docker=False,
        includes_cloud=False,
        includes_ci=False,
        template_sets=("base", "dual-agent"),
    ),
    "dual-agent-webapp": ProjectProfile(
        name="dual-agent-webapp",
        display_name="Dual Agent Web App",
        description=(
            "Application development files, container templates and full CI/CD workflows. "
            "Agent roles and deployment choices remain explicit."
        ),
        includes_bridge=True,
        includes_docker=True,
        includes_cloud=True,
        includes_ci=True,
        template_sets=("base", "dual-agent", "webapp"),
    ),
}


def get_profile(name: str) -> ProjectProfile:
    """Return a profile by name, or raise ValueError."""
    if name not in PROFILES:
        valid = ", ".join(sorted(PROFILES))
        raise ValueError(f"Unknown profile {name!r}. Valid profiles: {valid}")
    return PROFILES[name]


def list_profiles() -> list[ProjectProfile]:
    """Return all profiles in stable order."""
    return [PROFILES[k] for k in ("local-only", "dual-agent", "dual-agent-webapp")]
