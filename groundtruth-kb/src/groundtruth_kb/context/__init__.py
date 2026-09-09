"""Literal resource selection; current task content is supplied by the native authority."""

from groundtruth_kb.context.resource_routing import (
    ResourceRoutingError,
    canonical_resource_contract,
    resolve_resource_selection,
    validate_resource_contract,
)

__all__ = [
    "ResourceRoutingError",
    "canonical_resource_contract",
    "resolve_resource_selection",
    "validate_resource_contract",
]
