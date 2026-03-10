"""Superadmin API — Incidents, alerts, MFA.

Domain sub-module extracted from the superadmin_api monolith.
Endpoints are registered on sub_router for domain organization.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from fastapi import APIRouter

# Domain-specific sub-router (no prefix — main router adds /api/superadmin)
sub_router = APIRouter()

# Domain: Incidents, alerts, MFA
# Endpoints are currently in _monolith.py and will be migrated incrementally.
