"""Shared DEFECT work item creation for the deployment automation (WI-7860, owner ruling D17).

``create_defect`` records a DEFECT work item through the configured native authority and
nowhere else: an ``AuthorityClient`` on the platform's ``authority_url`` (the ``[groundtruth]``
table of the ``groundtruth.toml`` beside this ``scripts`` directory, or ``GT_AUTHORITY_URL``),
a client-chosen ``WI-NNNN`` identifier (the highest numeric work-item id on the authority plus
one, read across every listing page because no allocation route exists), a compare-and-swap
create (``expected_version`` 0) under ``PROJECT-GTKB-NATIVE-APPLICATION-LIFECYCLE`` with the
caller's explicit actor and reason, and an exact readback of the accepted record. The native
writer requires a complete evidence pair, so each pipeline cites its governing specification
and its own executable test (``source_spec_id``, ``source_test_id``).

Every failure raises ``DefectReportError`` whose ``code`` names the cause:
``authority_url_required`` or ``authority_configuration_invalid`` (nothing usable is
configured), ``authority_unavailable``, the authority's own refusal envelope
(``project_required``, ``work_evidence_required``, ``inactive_evidence``,
``executable_test_required``, ``test_phase_required``, ``cas_conflict`` once the bounded
identifier retries are spent, ...), ``invalid_response`` or ``readback_mismatch``. Nothing is
warned past, nothing returns None and nothing falls back to a local database.

Usage:
    from scripts._defect_reporter import create_defect

    wi_id = create_defect(
        title="Deploy pipeline failure: Phase 7 (ACR Docker Build)",
        description="Build failed with exit code 1...",
        source_spec_id="SPEC-1615",
        source_test_id="TEST-2941",
        actor="deploy-pipeline",
        reason="Automated deploy pipeline (SPEC-1615) failed Phase 7 (ACR Docker Build) for staging v1.99.0",
    )

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.config import GTConfig, GTConfigError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFECT_PROJECT_ID = "PROJECT-GTKB-NATIVE-APPLICATION-LIFECYCLE"
"""Execution project of automation-created defect work items (owner ruling D17, 2026-09-17)."""
DEFECT_ORIGIN = "defect"
DEFAULT_COMPONENT = "infrastructure_automation"
ID_ALLOCATION_ATTEMPTS = 5
"""Bounded retries when another writer takes the chosen identifier between the read and the create."""
PAGE_LIMIT = 1000
_WORK_ITEM_ID = re.compile(r"^WI-(\d+)$")


class DefectReportError(RuntimeError):
    """A defect work item was not recorded; ``code`` names the refusal, transport failure or mismatch."""

    def __init__(self, code: str, message: str, *, details: object = None) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.details = details


def authority_client(config_path: Path | None = None) -> AuthorityClient:
    """Client for the platform's configured authority; a missing ``authority_url`` is an error, not a fallback."""
    path = PROJECT_ROOT / "groundtruth.toml" if config_path is None else config_path
    try:
        config = GTConfig.load(config_path=path, discover=False)
    except (GTConfigError, OSError, ValueError) as error:
        raise DefectReportError("authority_configuration_invalid", f"{path}: {error}") from error
    if not config.authority_url:
        raise DefectReportError(
            "authority_url_required",
            f"{path} selects no authority_url and GT_AUTHORITY_URL is unset; "
            "defect work items are recorded only through the native authority",
        )
    return AuthorityClient(config.authority_url)


def next_work_item_id(client: AuthorityClient) -> str:
    """The highest numeric ``WI-NNNN`` identifier on the authority plus one, read from every listing page."""
    highest = 0
    after: str | None = None
    while True:
        page = client.request("GET", "/v1/work-items", query={"after": after, "limit": PAGE_LIMIT})
        records = page.get("records") if isinstance(page, dict) else None
        if not isinstance(records, list):
            raise DefectReportError("invalid_response", "The work-item listing did not return a records page")
        for record in records:
            match = _WORK_ITEM_ID.match(str(record.get("id", ""))) if isinstance(record, dict) else None
            if match:
                highest = max(highest, int(match.group(1)))
        after = page.get("next_after")
        if not isinstance(after, str) or not after:
            return f"WI-{highest + 1:04d}"


def _identifier_taken(client: AuthorityClient, work_item_id: str) -> bool:
    """Whether a refused create collided with a record that now exists under the chosen identifier."""
    try:
        client.request("GET", f"/v1/work-items/{work_item_id}")
    except AuthorityClientError as error:
        return error.code != "not_found"
    return True


def _verify_readback(
    work_item_id: str,
    accepted: Any,
    readback: Any,
    fields: dict[str, Any],
    *,
    actor: str,
    reason: str,
) -> None:
    """The record read back must equal the accepted record and carry every submitted field under the ruled project."""
    accepted_row = accepted.get("work_item") if isinstance(accepted, dict) else None
    row = readback.get("work_item") if isinstance(readback, dict) else None
    membership = readback.get("membership") if isinstance(readback, dict) else None
    if not isinstance(row, dict) or not isinstance(membership, dict) or row != accepted_row:
        raise DefectReportError(
            "readback_mismatch",
            f"{work_item_id} read back differently from the accepted record",
            details={"id": work_item_id},
        )
    expected = {
        **fields,
        "id": work_item_id,
        "version": 1,
        "changed_by": actor,
        "change_reason": reason,
        "resolution_status": "open",
        "stage": "created",
    }
    differing = sorted(key for key, value in expected.items() if row.get(key) != value)
    if differing or membership.get("project_id") != DEFECT_PROJECT_ID or membership.get("status") != "active":
        raise DefectReportError(
            "readback_mismatch",
            f"{work_item_id} was not recorded as submitted",
            details={
                "id": work_item_id,
                "fields": differing,
                "project_id": membership.get("project_id"),
                "membership_status": membership.get("status"),
            },
        )


def create_defect(
    *,
    title: str,
    description: str,
    source_spec_id: str,
    source_test_id: str,
    actor: str,
    reason: str,
    component: str = DEFAULT_COMPONENT,
    client: AuthorityClient | None = None,
) -> str:
    """Record one DEFECT work item on the native authority and return its identifier.

    ``source_spec_id`` is the pipeline's governing specification and ``source_test_id`` the
    pipeline's own executable test (the native writer refuses creation without both, and
    refuses retired specifications, tests without a ``test_file`` and tests outside an active
    test-plan phase). ``actor`` and ``reason`` become the record's ``changed_by`` and
    ``change_reason``. Every failure raises ``DefectReportError``; nothing is warned past.
    """
    authority = client if client is not None else authority_client()
    fields: dict[str, Any] = {
        "title": title,
        "description": description,
        "component": component,
        "origin": DEFECT_ORIGIN,
        "source_spec_id": source_spec_id,
        "source_test_id": source_test_id,
    }
    body = {"expected_version": 0, "actor": actor, "reason": reason, "project_id": DEFECT_PROJECT_ID, "fields": fields}
    try:
        for attempt in range(1, ID_ALLOCATION_ATTEMPTS + 1):
            work_item_id = next_work_item_id(authority)
            try:
                accepted = authority.request("PUT", f"/v1/work-items/{work_item_id}", body=body)
            except AuthorityClientError:
                if attempt < ID_ALLOCATION_ATTEMPTS and _identifier_taken(authority, work_item_id):
                    continue  # another writer created this identifier after the listing was read; choose again
                raise
            break
        readback = authority.request("GET", f"/v1/work-items/{work_item_id}")
    except AuthorityClientError as error:
        raise DefectReportError(error.code, str(error), details=error.details) from error
    _verify_readback(work_item_id, accepted, readback, fields, actor=actor, reason=reason)
    return work_item_id
