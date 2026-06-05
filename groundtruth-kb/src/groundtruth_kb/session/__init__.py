"""
GroundTruth KB session-services package.

Houses deterministic services that operate on the per-harness session-envelope
records produced by the wrap procedure (per WI-4293 / WI-4294 / WI-4299).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from groundtruth_kb.session.envelope import (
    EnvelopeError,
    close_session,
    close_topic,
    ensure_current,
    load_current,
    open_session,
    open_topic,
)
from groundtruth_kb.session.handoff import HandoffError, generate
from groundtruth_kb.session.wrap import is_canonical_wrap_trigger, run_wrap

__all__ = [
    "EnvelopeError",
    "HandoffError",
    "close_session",
    "close_topic",
    "ensure_current",
    "generate",
    "is_canonical_wrap_trigger",
    "load_current",
    "open_session",
    "open_topic",
    "run_wrap",
]
