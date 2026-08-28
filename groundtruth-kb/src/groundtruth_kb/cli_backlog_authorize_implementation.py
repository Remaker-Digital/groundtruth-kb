"""Fail-closed compatibility shim for ``gt backlog authorize-implementation``.

Per-work-item implementation authorization is retired. Project authorization
belongs to the exact execution project, while work-item execution scope is
represented by project membership. The command remains registered so existing
operator invocations receive deterministic recovery guidance instead of an
unknown-command error, but every operational invocation fails before request
validation, owner-decision capture, database access, dry-run postimage
construction, or project-authorization mutation.

Authority: WI-6066 and the independently approved source-bearing proposal
``gtkb-wi6066-retire-per-wi-authorize-implementation``.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from dataclasses import dataclass

from groundtruth_kb.config import GTConfig

RETIRED_AUTHORIZATION_MESSAGE = (
    "Per-work-item implementation authorization is retired. "
    "Use `gt projects authorize` to manage the current authorization for the exact execution project."
)


class AuthorizeImplementationError(Exception):
    """Raised when ``gt backlog authorize-implementation`` cannot safely proceed."""


@dataclass(frozen=True)
class AuthorizeImplementationRequest:
    """Validated request for one ``gt backlog authorize-implementation`` invocation.

    Exactly one owner-decision authority path must be supplied: an existing
    ``owner_decision`` (an owner-authority deliberation id) XOR fresh AUQ
    evidence (``auq_id`` + ``auq_answer`` + ``decision_content_file``).
    """

    work_item_id: str
    owner_decision: str | None
    auq_id: str | None
    auq_answer: str | None
    decision_content_file: str | None
    decision_title: str | None
    decision_summary: str | None
    project_id: str | None
    include_spec_ids: tuple[str, ...]
    allowed_mutation_classes: tuple[str, ...]
    forbidden_operations: tuple[str, ...]
    authorization_id: str | None
    authorization_name: str | None
    scope_summary: str | None
    change_reason: str
    session_id: str | None
    dry_run: bool


def authorize_implementation(config: GTConfig, request: AuthorizeImplementationRequest) -> dict[str, object]:
    """Reject the retired per-work-item authorization path before side effects."""
    del config, request
    raise AuthorizeImplementationError(RETIRED_AUTHORIZATION_MESSAGE)
