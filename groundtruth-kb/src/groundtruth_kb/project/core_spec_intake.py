"""Core application intake derived from current native specifications."""

from __future__ import annotations

import os
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal
from urllib.parse import quote

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError

CompletionSource = Literal["owner_stated", "not_applicable"]


@dataclass(frozen=True)
class CoreSpecSlot:
    """One required core application specification slot."""

    name: str
    label: str
    prompt: str


BASELINE_SLOTS: tuple[CoreSpecSlot, ...] = (
    CoreSpecSlot(
        "product_identity",
        "Product identity",
        "What product or application are we building, and what should it be called?",
    ),
    CoreSpecSlot("application_type", "Application type", "What kind of application is it?"),
    CoreSpecSlot("tenancy", "Tenancy", "Who owns, hosts, and uses each deployment instance?"),
    CoreSpecSlot("users_roles", "Users and roles", "Who are the user roles and what can each role do?"),
    CoreSpecSlot(
        "data_classification", "Data classification", "What data classes will the application store or process?"
    ),
    CoreSpecSlot("compliance", "Compliance", "Which compliance, audit, or policy obligations apply?"),
    CoreSpecSlot("security_posture", "Security posture", "What authentication, authorization, and threat model apply?"),
    CoreSpecSlot(
        "reliability_posture", "Reliability posture", "What availability, durability, and recovery expectations apply?"
    ),
    CoreSpecSlot(
        "external_integrations", "External integrations", "Which external services, APIs, or systems are in scope?"
    ),
    CoreSpecSlot("ai_usage", "AI usage", "How, if at all, will AI models or AI assistance be used?"),
    CoreSpecSlot(
        "operational_release_path",
        "Operational and release path",
        "How will the application be built, tested, released, deployed, and operated?",
    ),
    CoreSpecSlot(
        "first_release_non_goals", "First-release non-goals", "What is explicitly out of scope for the first release?"
    ),
)


def slot_names() -> tuple[str, ...]:
    return tuple(slot.name for slot in BASELINE_SLOTS)


def slot_spec_id(project_id: str, slot: str) -> str:
    """A proposed record identity; existing answers are resolved by canonical fields."""
    _slot_for_name(slot)
    ident = f"SPEC-CORE-INTAKE-{project_id}:{slot}"
    if len(ident) > 256 or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]*", ident) is None:
        raise ValueError("Supply a valid shorter specification ID for this project and slot")
    return ident


def _slot_for_name(name: str) -> CoreSpecSlot:
    for slot in BASELINE_SLOTS:
        if slot.name == name:
            return slot
    raise ValueError(f"Unknown core specification slot: {name}")


def _project(client: AuthorityClient, project_id: str) -> dict[str, Any]:
    project = client.request("GET", "/v1/projects/" + quote(project_id, safe=""))["project"]
    if project["kind"] != "project":
        raise AuthorityClientError("not_execution_project", "A program has no application intake")
    if not project.get("repository_ref"):
        raise AuthorityClientError("repository_unresolved", "Reconcile the project's repository before intake")
    return dict(project)


def _application_scope(project: dict[str, Any]) -> str:
    return "gtkb_platform" if project["repository_ref"] == "platform" else str(project["repository_ref"])


def _records(client: AuthorityClient, project_id: str) -> list[dict[str, Any]]:
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


def _belongs(record: dict[str, Any], project_id: str, slot: str) -> bool:
    tags = set(record.get("tags") or [])
    tagged = {"core-spec-intake", f"project:{project_id}", f"slot:{slot}"}.issubset(tags)
    handled = record.get("handle") == f"core-spec-intake:{project_id}:{slot}"
    return record.get("scope") == project_id and (tagged or handled)


def _source(record: dict[str, Any]) -> CompletionSource | None:
    tags = set(record.get("tags") or [])
    present = {tag.removeprefix("source:") for tag in tags if tag.startswith("source:")}
    if record.get("authority") != "stated":
        return None
    if present in (set(), {"owner_stated"}):
        return "owner_stated"
    return "not_applicable" if present == {"not_applicable"} else None


def intake_status(client: AuthorityClient, project_id: str) -> dict[str, Any]:
    """Read current project and specification facts without storing progress."""
    project = _project(client, project_id)
    records = _records(client, project_id)
    slots = []
    for slot in BASELINE_SLOTS:
        candidates = [row for row in records if _belongs(row, project_id, slot.name) and row["status"] == "active"]
        if len(candidates) > 1:
            raise AuthorityClientError(
                "ambiguous_core_spec",
                "Reconcile duplicate active specification slots",
                details={"slot": slot.name, "ids": [row["id"] for row in candidates]},
            )
        current = candidates[0] if candidates else None
        source = _source(current) if current else None
        complete = bool(
            current
            and source
            and current.get("application_scope") == _application_scope(project)
            and (source == "not_applicable" or str(current.get("description") or "").strip())
        )
        slots.append(
            {
                "name": slot.name,
                "label": slot.label,
                "prompt": slot.prompt,
                "complete": complete,
                "completion_spec_id": current["id"] if complete and current else None,
                "spec_id": current["id"] if current else None,
                "version": current["version"] if current else 0,
                "source": source if complete else None,
            }
        )
    missing = next((row["name"] for row in slots if not row["complete"]), None)
    return {
        "project": project,
        "complete": missing is None,
        "completed_slots": sum(row["complete"] for row in slots),
        "total_slots": len(slots),
        "next_slot": missing,
        "slots": slots,
    }


def slot_statuses(client: AuthorityClient, project_id: str) -> tuple[dict[str, Any], ...]:
    return tuple(intake_status(client, project_id)["slots"])


def next_missing_slot(client: AuthorityClient, project_id: str) -> str | None:
    value = intake_status(client, project_id)["next_slot"]
    return str(value) if value is not None else None


def next_question(client: AuthorityClient, project_id: str) -> dict[str, Any] | None:
    return next((row for row in intake_status(client, project_id)["slots"] if not row["complete"]), None)


def is_complete(client: AuthorityClient, project_id: str) -> bool:
    return next_missing_slot(client, project_id) is None


def mark_slot_complete(
    client: AuthorityClient,
    project_id: str,
    slot: str,
    value: str,
    source: CompletionSource = "owner_stated",
    *,
    expected_version: int,
    actor: str,
    reason: str,
    spec_id: str | None = None,
) -> dict[str, Any]:
    """Apply an explicit answer directly through the existing specification CAS writer."""
    definition = _slot_for_name(slot)
    if source not in ("owner_stated", "not_applicable"):
        raise ValueError("Only an explicit owner-stated answer or not-applicable response completes a slot")
    if source == "owner_stated" and not value.strip():
        raise ValueError("An owner-stated answer must be nonempty")
    if not actor.strip() or not reason.strip() or isinstance(expected_version, bool) or expected_version < 0:
        raise ValueError("Actor, reason and a nonnegative expected version are required")
    state = intake_status(client, project_id)
    selected = next(row for row in state["slots"] if row["name"] == slot)
    ident = spec_id or selected["spec_id"] or slot_spec_id(project_id, slot)
    if selected["spec_id"] is not None and selected["spec_id"] != ident:
        raise AuthorityClientError("ambiguous_core_spec", "Update the existing active slot specification")
    path = "/v1/specifications/" + quote(ident, safe="")
    try:
        current = client.request("GET", path)
    except AuthorityClientError as error:
        if error.code != "not_found":
            raise
        current = None
    if current is not None and not _belongs(current, project_id, slot):
        raise AuthorityClientError("core_spec_identity_conflict", "That specification belongs to another subject")
    tags = [tag for tag in (current.get("tags") or []) if not tag.startswith("source:")] if current else []
    for tag in ("core-spec-intake", f"project:{project_id}", f"slot:{slot}", f"source:{source}"):
        if tag not in tags:
            tags.append(tag)
    fields = {
        "title": current["title"] if current else f"Core specification: {definition.label}",
        "description": value.strip() or "Not applicable.",
        "status": "active",
        "type": "requirement",
        "scope": project_id,
        "section": "Core Spec Intake",
        "handle": f"core-spec-intake:{project_id}:{slot}",
        "tags": tags,
        "authority": "stated",
        "application_scope": _application_scope(state["project"]),
    }
    result = client.request(
        "PUT", path, body={"expected_version": expected_version, "actor": actor, "reason": reason, "fields": fields}
    )
    if client.request("GET", path) != result:
        raise AuthorityClientError(
            "readback_changed", "The answer was written but changed before readback; inspect current state"
        )
    return dict(result)


def intake_enabled(target: Path) -> bool:
    """Read explicit opt-out configuration; no files or session flags are written."""
    option = os.environ.get("GTKB_CORE_SPEC_INTAKE_OPT_OUT", "").lower()
    if option in {"1", "true", "yes"}:
        return False
    if option not in {"", "0", "false", "no"}:
        raise ValueError("GTKB_CORE_SPEC_INTAKE_OPT_OUT must be true or false")
    path = target / "groundtruth.toml"
    if not path.exists():
        return True
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    section = data.get("core_spec_intake", {})
    if not isinstance(section, dict) or not isinstance(section.get("enabled", True), bool):
        raise ValueError("core_spec_intake.enabled must be a boolean")
    return section.get("enabled", True) is True
