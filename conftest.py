"""Root pytest configuration for GroundTruth-KB.

Per-session pytest basetemp isolation (WI-3469). When the caller did not supply
an explicit ``--basetemp``, this hook roots pytest's temporary directories at a
per-process-unique leaf under the in-root ``.pytest-tmp/`` parent. The PID makes
parallel sessions (separate OS processes) land in disjoint subtrees; a short
random token guards against PID reuse across sequential runs within the same
parent. This eliminates the parallel-session ACL contamination that forced the
S377 broad-pytest verification waiver
(``DELIB-S377-SLICE7PRIME-PYTEST-CONTAMINATION-WAIVER``).

The hook defers entirely to an explicit ``--basetemp`` when one is supplied, so
every existing ad-hoc ``--basetemp=<in-root>`` invocation in current automation
behaves exactly as before.

This conftest is configuration-only: it defines no fixtures, markers, or
collection hooks, so it cannot change which tests run or how they assert. It is
intentionally minimal and imports no application code, consistent with the
shielding pattern at ``platform_tests/scripts/conftest.py``.

Authority: ``bridge/gtkb-pytest-basetemp-session-isolation-002.md`` (GO); WI-3469;
``PAUTH-WI-3469-PYTEST-BASETEMP-ISOLATION-001`` under ``PROJECT-GTKB-MAY29-HYGIENE``.
The in-root ``.pytest-tmp/`` parent is already git-ignored (``.gitignore`` line 79,
``.pytest-*/``).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import os
from pathlib import Path

# Name of the in-root parent under which per-session basetemp leaves are rooted.
# Already covered by the ``.pytest-*/`` ignore in .gitignore.
PYTEST_TMP_PARENT_NAME = ".pytest-tmp"


def _session_basetemp_leaf(project_root: Path) -> Path:
    """Return a per-process-unique basetemp leaf under the in-root parent.

    The leaf is ``<project_root>/.pytest-tmp/session-<pid>-<token>``. The PID
    disjoins parallel sessions (separate processes); the random token guards
    against PID reuse across sequential runs within the same parent.
    """
    parent = project_root / PYTEST_TMP_PARENT_NAME
    token = os.urandom(3).hex()
    return parent / f"session-{os.getpid()}-{token}"


def pytest_configure(config) -> None:
    """Root basetemp at a per-session leaf when no explicit ``--basetemp`` was given.

    No-op when the caller supplied ``--basetemp`` (``config.option.basetemp``
    truthy), preserving every existing ad-hoc ``--basetemp`` invocation.

    The per-session leaf is created eagerly so that an unwritable in-root parent
    — e.g. a ``.pytest-tmp/`` left ACL-contaminated by a prior crashed run —
    raises here (at configure time) and is caught, leaving pytest's default
    basetemp in place. Creating only the parent and deferring leaf creation to
    pytest would instead surface the ``PermissionError`` later during fixture
    setup, which is strictly worse: a hard failure rather than a graceful
    fallback. Failures are swallowed defensively because a root conftest that
    raised in ``pytest_configure`` would break the entire suite, and basetemp
    isolation is an availability convenience, not a correctness gate.
    """
    try:
        existing = getattr(getattr(config, "option", None), "basetemp", None)
        if existing:
            return
        project_root = Path(__file__).resolve().parent
        leaf = _session_basetemp_leaf(project_root)
        # Create the leaf itself (parents=True also creates the in-root parent
        # when absent). If the parent is unwritable this raises and we fall back.
        leaf.mkdir(parents=True, exist_ok=True)
        config.option.basetemp = str(leaf)
    except OSError:
        # Leave pytest's default basetemp in place rather than break collection.
        return
