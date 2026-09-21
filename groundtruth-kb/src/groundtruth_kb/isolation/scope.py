"""Application-scope selection shared by scope-aware readers.

A scope names one classification of current records: ``gtkb_platform`` or
``application:<name>``. Readers that evaluate or index records for one
selected root derive the scope from that root's ``application.toml`` marker
(an application root) or fall back to the platform scope; an explicit
selection overrides the marker. Selection grants nothing and validates only
the form of the scope text; catalog membership is the authority's concern
when a record is written.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

PLATFORM_SCOPE = "gtkb_platform"
APPLICATION_SCOPE_PREFIX = "application:"
APPLICATION_MARKER = "application.toml"


class ApplicationScopeError(ValueError):
    """The scope text or the root's application marker cannot select a scope."""

    code = "invalid_application_scope"


def explicit_application_scope(scope: str) -> str:
    """Return the explicitly selected scope after checking its form."""
    if scope != PLATFORM_SCOPE and not scope.startswith(APPLICATION_SCOPE_PREFIX):
        raise ApplicationScopeError("application_scope must be gtkb_platform or application:<catalog name>")
    if scope != PLATFORM_SCOPE and not scope.removeprefix(APPLICATION_SCOPE_PREFIX):
        raise ApplicationScopeError("application_scope must name the application after application:")
    return scope


def marker_application_scope(root: Path) -> str | None:
    """The scope named by ``<root>/application.toml``; None when the root carries no marker."""
    marker = root / APPLICATION_MARKER
    if not marker.is_file():
        return None
    try:
        payload = tomllib.loads(marker.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise ApplicationScopeError(f"{APPLICATION_MARKER} cannot be read: {error}") from error
    nested = payload.get("application", {})
    name = nested.get("name") if isinstance(nested, dict) else None
    if not isinstance(name, str) or not name:
        raise ApplicationScopeError("application.toml must name the registered application")
    return APPLICATION_SCOPE_PREFIX + name


def default_application_scope(root: Path) -> str:
    """Marker-derived scope for the selected root, else the platform scope."""
    return marker_application_scope(root) or PLATFORM_SCOPE


def select_application_scope(root: Path, explicit: str | None) -> str:
    """The explicit scope when given, otherwise the root's default scope."""
    if explicit is not None:
        return explicit_application_scope(explicit)
    return default_application_scope(root)
