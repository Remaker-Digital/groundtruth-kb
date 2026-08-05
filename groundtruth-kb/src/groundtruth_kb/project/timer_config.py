"""Single resolution path for invariant-coupled governance timers.

WI-5742 Layer A. Authority: ``DELIB-202667722`` (timer and throttle governance
with relaxed-first defaults and one resolution path), ``WI-5806``
(invariant-coupled timers externalized together), and
``GOV-ENV-LOCAL-AUTHORITY-001`` (the env-local layer of the precedence below).

Resolution precedence, highest first:

1. env-local override -- ``GTKB_PROTECTED_COMMIT_EVALUATION_BOUND_SECONDS`` and
   ``GTKB_BRIDGE_PUBLICATION_CAPABILITY_TTL_SECONDS``.
2. ``config/governance/protected-commit-timers.toml``.
3. the relaxed in-code fallback constants below, used only when the config
   surface is absent.

The coupled invariant
---------------------

The protected-commit evaluation bound and the bridge-publication capability TTL
are an invariant-coupled pair::

    evaluation_bound_seconds < bridge_publication_capability_ttl_seconds

A gate bound that could reach or exceed the capability TTL is the structural
precondition for publication stranding: a slow-but-passing gate outlives the
capability minted for the publication it gates, the parent commit dies, and a
terminal ``VERIFIED`` verdict is left file-only with no backing commit.
:func:`resolve_protected_commit_timers` refuses to return such a pair, which
makes the precondition unrepresentable in configuration rather than merely
discouraged.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "FALLBACK_BRIDGE_PUBLICATION_CAPABILITY_TTL_SECONDS",
    "FALLBACK_PROTECTED_COMMIT_EVALUATION_BOUND_SECONDS",
    "PROTECTED_COMMIT_TIMERS_RELATIVE_PATH",
    "ProtectedCommitTimers",
    "TimerConfigError",
    "resolve_protected_commit_timers",
]


class TimerConfigError(RuntimeError):
    """Raised when timer configuration is unreadable, malformed, or violates the coupled invariant."""


PROTECTED_COMMIT_TIMERS_RELATIVE_PATH = Path("config") / "governance" / "protected-commit-timers.toml"

# Relaxed-first in-code fallbacks (DELIB-202667722). These are the ONLY timer
# literals this module introduces, and they apply solely when the configuration
# surface above is absent. They satisfy the coupled invariant by construction.
FALLBACK_PROTECTED_COMMIT_EVALUATION_BOUND_SECONDS = 90
FALLBACK_BRIDGE_PUBLICATION_CAPABILITY_TTL_SECONDS = 120

# Mirrors the hard rejection in ``mint_bridge_publication_capability``: a TTL
# above this ceiling would be accepted in configuration but rejected at mint
# time, so the accessor enforces the same ceiling to keep configuration and
# runtime in agreement.
_CAPABILITY_TTL_CEILING_SECONDS = 800

_BOUND_ENV_VAR = "GTKB_PROTECTED_COMMIT_EVALUATION_BOUND_SECONDS"
_TTL_ENV_VAR = "GTKB_BRIDGE_PUBLICATION_CAPABILITY_TTL_SECONDS"


@dataclass(frozen=True)
class ProtectedCommitTimers:
    """A validated, invariant-coupled protected-commit timer pair."""

    evaluation_bound_seconds: int
    bridge_publication_capability_ttl_seconds: int
    source: str

    @property
    def margin_seconds(self) -> int:
        """Headroom between the gate bound and the capability TTL it must fit inside."""
        return self.bridge_publication_capability_ttl_seconds - self.evaluation_bound_seconds


def _coerce_positive_int(value: object, *, field: str, origin: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise TimerConfigError(f"{origin}: {field} must be an integer number of seconds, got {value!r}")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise TimerConfigError(f"{origin}: {field} must be an integer number of seconds, got {value!r}") from exc
    if parsed < 1:
        raise TimerConfigError(f"{origin}: {field} must be >= 1 second, got {parsed}")
    return parsed


def _read_config_file(config_path: Path) -> tuple[object | None, object | None, str] | None:
    if not config_path.is_file():
        return None
    try:
        document = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise TimerConfigError(f"{config_path}: protected-commit timer configuration is unreadable: {exc}") from exc
    section = document.get("protected_commit")
    if not isinstance(section, dict):
        raise TimerConfigError(f"{config_path}: missing required [protected_commit] table")
    return (
        section.get("evaluation_bound_seconds"),
        section.get("bridge_publication_capability_ttl_seconds"),
        str(config_path),
    )


def resolve_protected_commit_timers(project_root: Path | None = None) -> ProtectedCommitTimers:
    """Resolve the validated protected-commit timer pair.

    Raises :class:`TimerConfigError` when configuration is malformed, when a
    value is out of its tolerance bounds, or when the resolved pair violates the
    coupled invariant ``evaluation_bound_seconds < capability_ttl_seconds``.
    Callers that must not fail open are expected to let this propagate.
    """
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[4]
    config_path = root / PROTECTED_COMMIT_TIMERS_RELATIVE_PATH

    file_values = _read_config_file(config_path)
    if file_values is None:
        raw_bound: object | None = None
        raw_ttl: object | None = None
        origins = ["in-code relaxed fallback"]
    else:
        raw_bound, raw_ttl, file_origin = file_values
        origins = [file_origin]

    env_bound = os.environ.get(_BOUND_ENV_VAR)
    if env_bound is not None and env_bound.strip():
        raw_bound = env_bound.strip()
        origins.append(f"env:{_BOUND_ENV_VAR}")
    env_ttl = os.environ.get(_TTL_ENV_VAR)
    if env_ttl is not None and env_ttl.strip():
        raw_ttl = env_ttl.strip()
        origins.append(f"env:{_TTL_ENV_VAR}")

    source = " -> ".join(origins)

    bound = (
        FALLBACK_PROTECTED_COMMIT_EVALUATION_BOUND_SECONDS
        if raw_bound is None
        else _coerce_positive_int(raw_bound, field="evaluation_bound_seconds", origin=source)
    )
    ttl = (
        FALLBACK_BRIDGE_PUBLICATION_CAPABILITY_TTL_SECONDS
        if raw_ttl is None
        else _coerce_positive_int(raw_ttl, field="bridge_publication_capability_ttl_seconds", origin=source)
    )

    if ttl > _CAPABILITY_TTL_CEILING_SECONDS:
        raise TimerConfigError(
            f"{source}: bridge_publication_capability_ttl_seconds={ttl} exceeds the "
            f"{_CAPABILITY_TTL_CEILING_SECONDS}s ceiling enforced at capability mint time"
        )
    if bound >= ttl:
        raise TimerConfigError(
            f"{source}: evaluation_bound_seconds={bound} must be strictly less than "
            f"bridge_publication_capability_ttl_seconds={ttl}. A gate bound that can reach the "
            f"capability TTL is the structural precondition for publication stranding "
            f"(a slow-but-passing gate outliving the capability minted for the publication it gates)."
        )

    return ProtectedCommitTimers(
        evaluation_bound_seconds=bound,
        bridge_publication_capability_ttl_seconds=ttl,
        source=source,
    )
