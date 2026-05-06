# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Fixture-only allowlist — exact value + exact path matching only.

Anchored: SPEC-SEC-ALLOWLIST-001 v1 (S333).

Allowlist entries live at ``tests/secrets/fixtures/allowlist.toml`` (tracked).
Each entry carries ``value`` (exact, case-sensitive), ``path`` (exact relative
path under ``tests/``), and ``justification`` (free text). The scanner allows
a finding only when both ``value`` and ``path`` match an entry exactly. Any
allowlist entry whose path is outside ``tests/`` is rejected on load.

Per the Codex ``-002`` F1 fix on bridge/gtkb-sec-redaction-commit-gate-001-002.md,
fixture values must NOT be provider-shaped contiguous committed text — use
runtime assembly or synthetic ``GTKB_TEST_*_PATTERN_*`` markers (see
groundtruth_kb.secrets.patterns.TEST_SYNTHETIC_PATTERNS).
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

_TESTS_PREFIX = "tests/"


@dataclass(frozen=True)
class AllowlistEntry:
    value: str
    path: str
    justification: str


class AllowlistLoadError(ValueError):
    """Raised when the allowlist file is structurally invalid or contains a non-test path."""


@dataclass(frozen=True)
class Allowlist:
    entries: tuple[AllowlistEntry, ...]

    def matches(self, value: str, path: str) -> bool:
        normalized_path = path.replace("\\", "/")
        return any(entry.value == value and entry.path == normalized_path for entry in self.entries)

    @classmethod
    def empty(cls) -> Allowlist:
        return cls(entries=())

    @classmethod
    def load(cls, allowlist_path: Path) -> Allowlist:
        if not allowlist_path.is_file():
            return cls.empty()
        raw = tomllib.loads(allowlist_path.read_text(encoding="utf-8"))
        rows = raw.get("entries") or []
        if not isinstance(rows, list):
            raise AllowlistLoadError("allowlist.toml: 'entries' must be a list")
        parsed: list[AllowlistEntry] = []
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise AllowlistLoadError(f"allowlist.toml entries[{index}]: must be a table")
            value = row.get("value")
            path = row.get("path")
            justification = row.get("justification", "")
            if not isinstance(value, str) or not value:
                raise AllowlistLoadError(f"allowlist.toml entries[{index}]: missing 'value'")
            if not isinstance(path, str) or not path:
                raise AllowlistLoadError(f"allowlist.toml entries[{index}]: missing 'path'")
            normalized_path = path.replace("\\", "/")
            if not normalized_path.startswith(_TESTS_PREFIX):
                raise AllowlistLoadError(
                    f"allowlist.toml entries[{index}]: production-path entries are prohibited "
                    f"(path={path!r}); allowlist values may only sit under {_TESTS_PREFIX!r}."
                )
            parsed.append(
                AllowlistEntry(
                    value=value,
                    path=normalized_path,
                    justification=str(justification),
                )
            )
        return cls(entries=tuple(parsed))
