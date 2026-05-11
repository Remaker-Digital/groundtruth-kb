# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
Shared Pydantic base model for API DTOs.

All API response/request models that use camelCase JSON serialization
should inherit from CamelCaseModel instead of BaseModel directly.
This eliminates repeated ConfigDict boilerplate across API modules.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelCaseModel(BaseModel):
    """Base model for API DTOs with camelCase alias generation."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
