# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Harness invocation surfaces: the placeholder contract and the role-free rule (c123; batch design WP2 2.1, G1).

A harness registration's ``invocation_surfaces`` say how the dispatcher starts a harness: each surface's ``argv`` is a
template whose placeholders the dispatcher fills. Roles never live there. A context's role comes from the init line it
is bound with (``::init gtkb pb`` or ``::init gtkb lo``), and no harness, model, queue or launch argument can supply a
missing role (the session-bootstrap rule).

The contract:

- A launcher that binds the context itself (the API harnesses F, D and H, and the DeepSeek SDK) carries
  ``--init {{INIT_LINE}}``.
- For every other host, the dispatcher puts the exact init line as the first line of ``{{PROMPT}}``.
- ``{{DOCUMENT}}`` and ``{{VERSION}}`` carry the dispatched bridge item and the version the context must deliver.

``render`` fills a template and refuses an unknown or unfilled placeholder. ``surface_findings`` lists what a
registration must not carry; the authority refuses a write that has any finding, before anything is written.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from groundtruth_kb.bridge.vocabulary import ROLE_NAMES

PLACEHOLDERS = frozenset({"PROMPT", "PROJECT_ROOT", "INIT_LINE", "DOCUMENT", "VERSION", "TASK_FILE", "REPORT"})
"""Exactly the placeholders the nine registrations use (c121's installed rows)."""

ROLE_ROUTE_KEYS = frozenset({"bridge-review", "verification", "implementation"})
"""The retired role routes, which selected a role through a launch argument."""

SAMPLE_VALUES = {
    "PROMPT": "Reply with READY only.",
    "INIT_LINE": "::init gtkb lo",
    "DOCUMENT": "readiness-probe",
    "VERSION": "1",
    "TASK_FILE": "readiness-task.md",
    "REPORT": "readiness-report.json",
}
"""Values for every placeholder but PROJECT_ROOT, to check a template as the dispatcher would render it."""

FINDING_ROLE_KEY = "role_key"
FINDING_ROLE_VALUE = "role_value"
FINDING_INIT_MARKER = "init_marker_in_argv"
FINDING_SKILL_SELECTOR = "skill_selector"
FINDING_UNKNOWN_PLACEHOLDER = "unknown_placeholder"
ROLE_FINDINGS = frozenset({FINDING_ROLE_KEY, FINDING_ROLE_VALUE, FINDING_INIT_MARKER, FINDING_SKILL_SELECTOR})

_PLACEHOLDER = re.compile(r"\{\{([^{}]*)\}\}")
_ROLE_WORDS = frozenset(word.casefold() for pair in ROLE_NAMES.items() for word in pair) | ROLE_ROUTE_KEYS


class InvocationError(ValueError):
    """A template names a placeholder outside the contract, or one the caller did not fill."""


@dataclass(frozen=True)
class SurfaceFinding:
    """One thing a registration must not carry: its code, where it is, and the offending text."""

    code: str
    path: str
    value: str


def sample_values(project_root: str) -> dict[str, str]:
    """SAMPLE_VALUES with the selected project root, which fills every placeholder of the contract."""
    return {**SAMPLE_VALUES, "PROJECT_ROOT": project_root}


def placeholders_in(text: str) -> set[str]:
    """The placeholder names one template token uses."""
    return set(_PLACEHOLDER.findall(text))


def render(argv: Sequence[str], values: Mapping[str, str]) -> list[str]:
    """Fill every placeholder in ``argv`` from ``values``; refuse an unknown or an unfilled one."""
    rendered: list[str] = []
    for token in argv:
        names = placeholders_in(token)
        unknown = sorted(names - PLACEHOLDERS)
        if unknown:
            raise InvocationError(f"unknown invocation placeholder: {', '.join(unknown)}")
        missing = sorted(name for name in names if not isinstance(values.get(name), str))
        if missing:
            raise InvocationError(f"unfilled invocation placeholder: {', '.join(missing)}")
        rendered.append(_PLACEHOLDER.sub(lambda match: values[match.group(1)], token))
    return rendered


def _walk(value: Any, path: str) -> Iterator[tuple[str, Any, str | None]]:
    """Every node with its path and the key that holds it."""
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            yield child_path, child, str(key)
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def surface_findings(invocation_surfaces: Mapping[str, Any] | None) -> list[SurfaceFinding]:
    """What ``invocation_surfaces`` must not carry: a role key, a role value, an init marker, a skill selector or an
    unknown placeholder. Empty for a role-free registration."""
    findings: list[SurfaceFinding] = []
    for path, node, key in _walk(invocation_surfaces or {}, ""):
        if key is not None and key.casefold() in {"role", "roles"}:
            findings.append(SurfaceFinding(FINDING_ROLE_KEY, path, key))
        if key not in {"argv", "dispatch_tags"} or not isinstance(node, list):
            continue
        for index, item in enumerate(node):
            if not isinstance(item, str):
                continue
            where = f"{path}[{index}]"
            if item.strip().casefold() in _ROLE_WORDS:
                findings.append(SurfaceFinding(FINDING_ROLE_VALUE, where, item))
            if key != "argv":
                continue
            if item.lstrip().startswith("::init"):
                findings.append(SurfaceFinding(FINDING_INIT_MARKER, where, item))
            if item == "--skill" or item.startswith("--skill="):
                findings.append(SurfaceFinding(FINDING_SKILL_SELECTOR, where, item))
            for name in sorted(placeholders_in(item) - PLACEHOLDERS):
                findings.append(SurfaceFinding(FINDING_UNKNOWN_PLACEHOLDER, where, f"{{{{{name}}}}}"))
    return findings
