"""Starter specifications for one execution project through the native authority.

The minimal profile generates the governance and infrastructure templates
(four specifications); the full profile adds AI-component and compliance
templates (six). Generated records carry ``authority = "inferred"``: they are
review candidates an owner promotes explicitly, never core-intake answers and
never a substitute for the owner's stated requirements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.spec_quality import score_spec_quality
from groundtruth_kb.spec_scaffold import SpecScaffoldConfig, starter_templates

PROFILES: tuple[str, ...] = ("minimal", "full")


@dataclass(frozen=True)
class NativeScaffoldReport:
    """Outcome of one starter-specification preview or application."""

    project_id: str
    profile: str
    dry_run: bool
    generated: list[dict[str, Any]] = field(default_factory=list)
    skipped: list[dict[str, Any]] = field(default_factory=list)
    quality_summary: dict[str, int] = field(default_factory=dict)
    low_quality_warnings: list[dict[str, Any]] = field(default_factory=list)

    @property
    def canonical_writes(self) -> int:
        return 0 if self.dry_run else len(self.generated)

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "profile": self.profile,
            "dry_run": self.dry_run,
            "generated": self.generated,
            "skipped": self.skipped,
            "quality_summary": self.quality_summary,
            "low_quality_warnings": self.low_quality_warnings,
            "canonical_writes": self.canonical_writes,
        }


def scaffold_config(profile: str) -> SpecScaffoldConfig:
    if profile not in PROFILES:
        raise ValueError("Select the minimal or full starter specification profile")
    return SpecScaffoldConfig(profile=profile)


def starter_specification_id(project_id: str, template_id: str) -> str:
    """One authority holds many projects; template identities are project-qualified."""
    return f"{template_id}:{project_id}"


def _project(client: AuthorityClient, project_id: str) -> dict[str, Any]:
    project = client.request("GET", "/v1/projects/" + quote(project_id, safe=""))["project"]
    if project.get("kind") != "project":
        raise AuthorityClientError("not_execution_project", "Starter specifications belong to an execution project")
    reference = project.get("repository_ref")
    if not isinstance(reference, str) or not reference:
        raise AuthorityClientError("repository_unresolved", "Reconcile the project's repository first")
    return dict(project)


def _application_scope(project: dict[str, Any]) -> str:
    return "gtkb_platform" if project["repository_ref"] == "platform" else str(project["repository_ref"])


def _project_specifications(client: AuthorityClient, project_id: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    after = None
    while True:
        page = client.request("GET", "/v1/specifications", query={"scope": project_id, "limit": 1000, "after": after})
        records.extend(page["records"])
        following = page["next_after"]
        if following is None:
            return records
        if following == after:
            raise AuthorityClientError("invalid_response", "The specification cursor did not advance")
        after = following


def planned_specifications(project: dict[str, Any], config: SpecScaffoldConfig) -> list[dict[str, Any]]:
    """Render the template catalog for the selected project without reading or writing."""
    project_id = str(project["id"])
    rendered = []
    for template in starter_templates(config):
        handle = f"scaffold:{project_id}:{template['handle']}"
        rendered.append(
            {
                "id": starter_specification_id(project_id, str(template["id"])),
                "template_id": template["id"],
                "fields": {
                    "title": template["title"],
                    "description": template.get("description"),
                    "status": "active",
                    "type": template.get("type", "requirement"),
                    "scope": project_id,
                    "section": template.get("section"),
                    "handle": handle,
                    "tags": ["spec-scaffold", f"project:{project_id}", f"scaffold-scope:{template.get('scope')}"],
                    "assertions": template.get("assertions"),
                    "authority": "inferred",
                    "testability": template.get("testability"),
                    "application_scope": _application_scope(project),
                },
            }
        )
    return rendered


def scaffold_specs(
    client: AuthorityClient,
    project_id: str,
    config: SpecScaffoldConfig,
    *,
    dry_run: bool = True,
    actor: str = "scaffold-generator",
    reason: str = "Generated starter specification",
) -> NativeScaffoldReport:
    """Preview or write the starter set; existing handles in the project are skipped."""
    if config.profile not in PROFILES:
        raise ValueError("Select the minimal or full starter specification profile")
    project = _project(client, project_id)
    existing = _project_specifications(client, project_id)
    present = {row.get("handle"): row for row in existing if row.get("status") == "active" and row.get("handle")}
    report = NativeScaffoldReport(
        project_id=project_id,
        profile=config.profile,
        dry_run=dry_run,
        quality_summary={"gold": 0, "silver": 0, "bronze": 0, "needs-work": 0},
    )
    for planned in planned_specifications(project, config):
        fields = planned["fields"]
        current = present.get(fields["handle"])
        if current is not None:
            report.skipped.append(
                {
                    "id": current["id"],
                    "handle": fields["handle"],
                    "reason": "An active specification already holds this handle",
                }
            )
            continue
        if dry_run:
            entry = {**fields, "id": planned["id"], "version": 1}
        else:
            path = "/v1/specifications/" + quote(planned["id"], safe="")
            try:
                occupied = client.request("GET", path)
            except AuthorityClientError as error:
                if error.code != "not_found":
                    raise
                occupied = None
            if occupied is not None:
                report.skipped.append(
                    {"id": planned["id"], "handle": fields["handle"], "reason": "The identity is already in use"}
                )
                continue
            written = client.request(
                "PUT", path, body={"expected_version": 0, "actor": actor, "reason": reason, "fields": fields}
            )
            if client.request("GET", path) != written:
                raise AuthorityClientError("readback_changed", "The starter specification changed before readback")
            entry = dict(written)
        quality = score_spec_quality(entry)
        entry["quality"] = quality
        tier = str(quality.get("tier", "needs-work"))
        report.quality_summary[tier] = report.quality_summary.get(tier, 0) + 1
        if tier in ("bronze", "needs-work"):
            report.low_quality_warnings.append({"id": entry["id"], "tier": tier, "score": quality.get("overall")})
        report.generated.append(entry)
    return report
