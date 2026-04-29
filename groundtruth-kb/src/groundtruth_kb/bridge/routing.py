# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Smart-poller routing: classify transitions for downstream invoker (P3).

Per ``bridge/gtkb-bridge-poller-p1-detector-003.md`` section 3.5, routing
produces three per-transition outcomes (``ROUTABLE``,
``UNROUTABLE_FILE_MISSING``, ``UNROUTABLE_BOOTSTRAP``) and tags each routable
transition with an inferred authorship/recipient pair derived from the
status enum.

Out of scope for this module: parsing (see detector.py),
diff/checkpoint (see checkpoint.py), audit emission (see audit.py),
P3 invoker (gated on P2.5 spike per umbrella -007).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from groundtruth_kb.bridge.checkpoint import Transition

# Status vocabulary mapping: which agent authored a status transition.
# - NEW / REVISED are Prime Builder authoring acts.
# - GO / NO-GO / VERIFIED are Loyal Opposition (Codex) authoring acts.
_PRIME_STATUSES = frozenset({"NEW", "REVISED"})
_CODEX_STATUSES = frozenset({"GO", "NO-GO", "VERIFIED"})


class Agent(StrEnum):
    PRIME = "prime"
    CODEX = "codex"


class TransitionOutcome(StrEnum):
    ROUTABLE = "routable"
    UNROUTABLE_FILE_MISSING = "unroutable_file_missing"
    UNROUTABLE_BOOTSTRAP = "unroutable_bootstrap"


@dataclass(frozen=True)
class RoutedTransition:
    """A transition tagged with its routing outcome and recipient (when routable)."""

    transition: Transition
    outcome: TransitionOutcome
    authored_by: Agent | None  # author of the to_status, or None when unknown
    recipient: Agent | None  # agent the invoker should hand off to, or None when unroutable
    detail: str = ""


def _author_from_status(status: str) -> Agent | None:
    if status in _PRIME_STATUSES:
        return Agent.PRIME
    if status in _CODEX_STATUSES:
        return Agent.CODEX
    return None


def _recipient_for(author: Agent | None) -> Agent | None:
    if author is Agent.PRIME:
        return Agent.CODEX
    if author is Agent.CODEX:
        return Agent.PRIME
    return None


def route_transitions(transitions: tuple[Transition, ...], *, project_root: Path) -> tuple[RoutedTransition, ...]:
    """Classify each transition into a routing outcome.

    Args:
        transitions: transitions emitted by ``diff_against_checkpoint``.
        project_root: project root for ``to_file`` existence validation.

    Returns:
        A RoutedTransition for each input transition, in the same order.
    """
    out: list[RoutedTransition] = []
    for t in transitions:
        author = _author_from_status(t.to_status)
        target_path = project_root / t.to_file
        if not target_path.is_file():
            out.append(
                RoutedTransition(
                    transition=t,
                    outcome=TransitionOutcome.UNROUTABLE_FILE_MISSING,
                    authored_by=author,
                    recipient=None,
                    detail=f"Current top file missing on disk: {t.to_file}",
                )
            )
            continue
        recipient = _recipient_for(author)
        if recipient is None:
            out.append(
                RoutedTransition(
                    transition=t,
                    outcome=TransitionOutcome.UNROUTABLE_FILE_MISSING,
                    authored_by=author,
                    recipient=None,
                    detail=(f"Unknown status '{t.to_status}'; cannot infer authorship or recipient."),
                )
            )
            continue
        out.append(
            RoutedTransition(
                transition=t,
                outcome=TransitionOutcome.ROUTABLE,
                authored_by=author,
                recipient=recipient,
                detail="",
            )
        )
    return tuple(out)


def synthesize_bootstrap_outcomes(
    document_count: int,
) -> tuple[RoutedTransition, ...]:
    """Emit zero RoutedTransitions and rely on caller to record a bootstrap audit event.

    Per design section 3.7, bootstrap mode emits zero routable transitions.
    This helper exists so callers can express the intent symmetrically with
    non-bootstrap calls (return ``()`` directly is also acceptable, but this
    encodes the design semantics in code for reviewer clarity).

    Args:
        document_count: count of documents seen at bootstrap time, recorded by
            the audit layer in the bootstrap event.
    """
    _ = document_count  # currently unused; see audit.py for bootstrap event payload
    return ()
