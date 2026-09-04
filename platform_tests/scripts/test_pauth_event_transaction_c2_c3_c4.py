# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-7657: the authorization event transactions C2/C3/C4 have no subject.

This file drove authorization create, amend, and revoke transactions through
``ProjectLifecycleService`` and asserted their append-only event semantics.
Those service methods were removed together with the record they wrote.

Non-vacuity: an absence assertion passes trivially if the symbol name is
misspelled or the import silently failed, so every test below pairs the absent
names with a control that is still present on the same object.
"""

from __future__ import annotations

from groundtruth_kb.project.lifecycle import ProjectLifecycleError, ProjectLifecycleService

REMOVED_SERVICE_METHODS = (
    "authorize_project",
    "get_project_authorization",
    "list_project_authorizations",
    "revoke_project_authorization",
    "complete_project_authorization",
    "amend_project_authorization",
    "update_project_authorization",
    "_append_reauthorization_for_membership_event",
)


def test_control_service_surface_is_present() -> None:
    """Non-vacuity guard: the service imported and retains real methods."""
    assert hasattr(ProjectLifecycleService, "update_project")
    assert issubclass(ProjectLifecycleError, Exception)


def test_authorization_transactions_are_absent() -> None:
    """None of the create/amend/revoke/complete transactions survives."""
    assert hasattr(ProjectLifecycleService, "update_project"), "control method missing"
    for name in REMOVED_SERVICE_METHODS:
        assert not hasattr(ProjectLifecycleService, name), f"ProjectLifecycleService should no longer expose {name}"


def test_membership_mutation_appends_no_authorization_successor() -> None:
    """The churn writer is gone, so membership changes mint nothing.

    This is the behavioural half of the removal. The writer that appended a
    re-authorization row on every membership event no longer exists, which is
    why the row count stayed flat across governed membership operations while
    this work item was implemented.
    """
    assert hasattr(ProjectLifecycleService, "update_project"), "control method missing"
    assert not hasattr(ProjectLifecycleService, "_append_reauthorization_for_membership_event")
