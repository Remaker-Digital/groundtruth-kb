"""Data contracts for deterministic GT-KB Git lifecycle operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class OperationDenied(RuntimeError):
    """A fail-closed lifecycle denial with a stable machine-readable code."""

    def __init__(self, code: str, message: str, **details: Any) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = dict(sorted(details.items()))

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": "DENIED",
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


@dataclass(frozen=True)
class OperationResult:
    """Stable observable result returned by successful lifecycle operations."""

    operation: str
    code: str
    work_item_id: str
    branch: str
    commit_sha: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": "PASS",
            "operation": self.operation,
            "code": self.code,
            "work_item_id": self.work_item_id,
            "branch": self.branch,
            "details": dict(sorted(self.details.items())),
        }
        if self.commit_sha is not None:
            payload["commit_sha"] = self.commit_sha
        return payload


@dataclass(frozen=True)
class PromotionEvidence:
    """Reference to a service-issued, append-only promotion receipt."""

    bundle_path: str
    bundle_sha256: str

    @property
    def receipt_path(self) -> str:
        return self.bundle_path

    @property
    def receipt_sha256(self) -> str:
        return self.bundle_sha256

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle_path": self.bundle_path,
            "bundle_sha256": self.bundle_sha256,
        }
