"""Superadmin API — Costs, abuse, service messages, platform admin.

Domain sub-module extracted from the superadmin_api monolith.
Endpoints are registered on sub_router for domain organization.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from fastapi import APIRouter

# Domain-specific sub-router (no prefix — main router adds /api/superadmin)
sub_router = APIRouter()

# Domain: Costs, abuse, service messages, platform admin
# Endpoints are currently in _monolith.py and will be migrated incrementally.
