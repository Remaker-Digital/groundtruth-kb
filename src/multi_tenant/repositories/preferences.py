"""
Preferences repository — preferences collection (versioned config).

Save → Activate model: DRAFT, ACTIVE, PREVIOUS states.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any

from src.multi_tenant.cosmos_schema import (
    COLLECTION_PREFERENCES,
    PreferencesDocument,
)
from src.multi_tenant.repositories.base import DocumentNotFoundError, TenantScopedRepository


class PreferencesRepository(TenantScopedRepository):
    """Repository for the preferences collection (versioned config).

    Save → Activate model:
        - get_active()   reads the live config (chat pipeline, widget)
        - get_draft()    reads the draft config (admin UI edits)
        - get_previous() reads the previous activation (for Restore)
        - get_current()  backward-compat alias for get_active()
    """

    # SPEC-1843 / WI-1627: Fields encrypted at rest with tenant DEK
    # Per architecture plan section 4.1.3: merchant business config
    _encryption_fields = frozenset({
        "custom_instructions", "return_policy", "shipping_info",
        "webhook_urls", "notification_settings",
    })

    def __init__(self) -> None:
        super().__init__(COLLECTION_PREFERENCES)

    # ---- Save → Activate state queries ----

    async def get_active(self, tenant_id: str) -> dict[str, Any] | None:
        """Get the currently activated preferences (config_state='active').

        Backward-compatible: also matches old documents with
        ``is_current=true`` that predate the config_state field.
        """
        results = await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE (c.config_state = 'active' "
                "       OR (c.is_current = true "
                "           AND NOT IS_DEFINED(c.config_state))) "
                "ORDER BY c.version DESC"
            ),
            max_items=1,
        )
        return results[0] if results else None

    async def get_draft(self, tenant_id: str) -> dict[str, Any] | None:
        """Get the current draft preferences (config_state='draft')."""
        results = await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.config_state = 'draft' "
                "ORDER BY c.version DESC"
            ),
            max_items=1,
        )
        return results[0] if results else None

    async def get_previous(self, tenant_id: str) -> dict[str, Any] | None:
        """Get the previous activation snapshot (config_state='previous')."""
        results = await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.config_state = 'previous' "
                "ORDER BY c.version DESC"
            ),
            max_items=1,
        )
        return results[0] if results else None

    async def get_current(self, tenant_id: str) -> dict[str, Any] | None:
        """Get the current (active) preferences version.

        Backward-compatible alias for ``get_active()``.  All existing
        callers (pipeline, widget, test mode removal) continue to work.
        """
        return await self.get_active(tenant_id)

    async def create_version(
        self, tenant_id: str, preferences: PreferencesDocument,
    ) -> dict[str, Any]:
        """Create a new preferences version and mark it current.

        Marks the previous version as non-current first.
        """
        # Mark previous version as non-current
        current = await self.get_current(tenant_id)
        if current:
            await self.patch(
                tenant_id=tenant_id,
                document_id=current["id"],
                operations=[{"op": "set", "path": "/is_current", "value": False}],
            )

        return await self.create(tenant_id, preferences)

    async def get_version(
        self, tenant_id: str, version: int,
    ) -> dict[str, Any] | None:
        """Get a specific preferences version."""
        results = await self.query(
            tenant_id=tenant_id,
            query_text="SELECT * FROM c WHERE c.version = @version",
            parameters=[{"name": "@version", "value": version}],
            max_items=1,
        )
        return results[0] if results else None

    async def list_versions(
        self, tenant_id: str, max_items: int = 20,
    ) -> list[dict[str, Any]]:
        """List all preference versions, newest first."""
        return await self.query(
            tenant_id=tenant_id,
            query_text="SELECT * FROM c ORDER BY c.version DESC",
            max_items=max_items,
        )

    async def list_named(
        self, tenant_id: str,
    ) -> list[dict[str, Any]]:
        """List all preference versions that have a config_name."""
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.config_name != null "
                "ORDER BY c.version DESC"
            ),
            max_items=50,
        )

    async def get_by_name(
        self, tenant_id: str, config_name: str,
    ) -> dict[str, Any] | None:
        """Get a preference version by config_name."""
        results = await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.config_name = @config_name "
                "ORDER BY c.version DESC"
            ),
            parameters=[{"name": "@config_name", "value": config_name}],
            max_items=1,
        )
        return results[0] if results else None

    # ---- Named widget appearance queries (C4) ----

    async def list_named_appearances(
        self, tenant_id: str,
    ) -> list[dict[str, Any]]:
        """List all preference versions that have an appearance_name."""
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.appearance_name != null "
                "ORDER BY c.version DESC"
            ),
            max_items=50,
        )

    async def get_by_appearance_name(
        self, tenant_id: str, appearance_name: str,
    ) -> dict[str, Any] | None:
        """Get a preference version by appearance_name."""
        results = await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.appearance_name = @appearance_name "
                "ORDER BY c.version DESC"
            ),
            parameters=[{"name": "@appearance_name", "value": appearance_name}],
            max_items=1,
        )
        return results[0] if results else None

    # ---- Quick Action Prompt methods (WI #226-229) ----
    #
    # Quick action CRUD operates on the DRAFT document under the
    # Save → Activate model.  If no draft exists, reads from active
    # for display purposes.  Write operations target the draft.

    async def _get_draft_or_active(self, tenant_id: str) -> dict[str, Any] | None:
        """Get draft if it exists, otherwise active.  For quick action reads."""
        draft = await self.get_draft(tenant_id)
        if draft is not None:
            return draft
        return await self.get_active(tenant_id)

    async def get_quick_actions(self, tenant_id: str) -> list[dict[str, Any]]:
        """Get all quick action prompts for a tenant.

        Reads from draft (if exists) or active preferences document.
        """
        doc = await self._get_draft_or_active(tenant_id)
        if not doc:
            return []
        return doc.get("quick_actions", [])

    async def get_quick_actions_active(self, tenant_id: str) -> list[dict[str, Any]]:
        """Get quick actions from the ACTIVE config only (for widget serving)."""
        active = await self.get_active(tenant_id)
        if not active:
            return []
        return active.get("quick_actions", [])

    async def upsert_quick_action(
        self, tenant_id: str, action: dict[str, Any],
    ) -> dict[str, Any]:
        """Create or update a quick action in the draft preferences.

        Uses read-modify-write on the quick_actions array within the
        draft document. If no draft exists, patches the active document's
        quick_actions as a draft edit — the ActivationService is responsible
        for creating the full draft document before this is called.
        """
        target = await self.get_draft(tenant_id)
        if not target:
            target = await self.get_active(tenant_id)
        if not target:
            raise DocumentNotFoundError(
                self._collection_name, "draft_or_active", tenant_id,
            )

        actions: list[dict[str, Any]] = target.get("quick_actions", [])

        # Find and replace existing, or append new
        found = False
        for i, existing in enumerate(actions):
            if existing.get("id") == action["id"]:
                actions[i] = action
                found = True
                break
        if not found:
            actions.append(action)

        await self.patch(
            tenant_id=tenant_id,
            document_id=target["id"],
            operations=[{"op": "set", "path": "/quick_actions", "value": actions}],
        )
        return action

    async def delete_quick_action(
        self, tenant_id: str, action_id: str,
    ) -> bool:
        """Remove a quick action from the draft preferences.

        Also removes any page assignment references to this action ID.
        Returns True if the action was found and removed.
        """
        target = await self.get_draft(tenant_id)
        if not target:
            target = await self.get_active(tenant_id)
        if not target:
            return False

        actions: list[dict[str, Any]] = target.get("quick_actions", [])
        original_len = len(actions)
        actions = [a for a in actions if a.get("id") != action_id]

        if len(actions) == original_len:
            return False  # Not found

        # Also clean up assignments referencing this action
        assignments: list[dict[str, Any]] = target.get(
            "quick_action_assignments", [],
        )
        for assignment in assignments:
            if assignment.get("slot_1_action_id") == action_id:
                assignment["slot_1_action_id"] = None
            if assignment.get("slot_2_action_id") == action_id:
                assignment["slot_2_action_id"] = None

        await self.patch(
            tenant_id=tenant_id,
            document_id=target["id"],
            operations=[
                {"op": "set", "path": "/quick_actions", "value": actions},
                {"op": "set", "path": "/quick_action_assignments", "value": assignments},
            ],
        )
        return True

    async def get_page_assignments(
        self, tenant_id: str,
    ) -> list[dict[str, Any]]:
        """Get all page-to-quick-action assignments for a tenant."""
        doc = await self._get_draft_or_active(tenant_id)
        if not doc:
            return []
        return doc.get("quick_action_assignments", [])

    async def get_page_assignments_active(
        self, tenant_id: str,
    ) -> list[dict[str, Any]]:
        """Get page assignments from the ACTIVE config only (for widget serving)."""
        active = await self.get_active(tenant_id)
        if not active:
            return []
        return active.get("quick_action_assignments", [])

    async def upsert_page_assignment(
        self, tenant_id: str, assignment: dict[str, Any],
    ) -> dict[str, Any]:
        """Create or update a page assignment in the draft preferences.

        Matches on page_type + page_handle combination. If a matching
        assignment exists, replaces it; otherwise appends.
        """
        target = await self.get_draft(tenant_id)
        if not target:
            target = await self.get_active(tenant_id)
        if not target:
            raise DocumentNotFoundError(
                self._collection_name, "draft_or_active", tenant_id,
            )

        assignments: list[dict[str, Any]] = target.get(
            "quick_action_assignments", [],
        )

        # Find and replace existing (match on page_type + page_handle)
        found = False
        for i, existing in enumerate(assignments):
            if (
                existing.get("page_type") == assignment["page_type"]
                and existing.get("page_handle") == assignment.get("page_handle")
            ):
                assignments[i] = assignment
                found = True
                break
        if not found:
            assignments.append(assignment)

        await self.patch(
            tenant_id=tenant_id,
            document_id=target["id"],
            operations=[
                {"op": "set", "path": "/quick_action_assignments", "value": assignments},
            ],
        )
        return assignment

    async def delete_page_assignment(
        self, tenant_id: str, page_type: str, page_handle: str | None = None,
    ) -> bool:
        """Remove a page assignment from draft. Returns True if found and removed."""
        target = await self.get_draft(tenant_id)
        if not target:
            target = await self.get_active(tenant_id)
        if not target:
            return False

        assignments: list[dict[str, Any]] = target.get(
            "quick_action_assignments", [],
        )
        original_len = len(assignments)
        assignments = [
            a for a in assignments
            if not (
                a.get("page_type") == page_type
                and a.get("page_handle") == page_handle
            )
        ]

        if len(assignments) == original_len:
            return False

        await self.patch(
            tenant_id=tenant_id,
            document_id=target["id"],
            operations=[
                {"op": "set", "path": "/quick_action_assignments", "value": assignments},
            ],
        )
        return True
