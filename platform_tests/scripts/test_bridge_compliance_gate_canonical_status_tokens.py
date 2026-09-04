"""The compliance gate must accept every canonical status token (WI-7675).

Canon section 6 fixes the bridge vocabulary at ten. The gate's
`BRIDGE_STATUS_TOKENS` tuple is what decides which of them may appear in an
artifact head, and it was missing both report-phase tokens. A GO'd work item
therefore had no lawful head for its implementation report: `READY` was
refused, while `NEW` and `REVISED` were accepted but produce a `GO -> NEW` or
`GO -> REVISED` pair that the lifecycle resolver rejects.

The same tuple already carries the scar of this class. Its `VERDICT-REJECTED`
entry was added by WI-7045 under emergency-bootstrap authority for exactly the
same reason, recorded in a comment there: "no token was writable and the Prime
verdict-rejection route was inoperable."

This asserts the gate against the single vocabulary source rather than against
a hand-written list, so the two cannot drift apart again.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.bridge.vocabulary import CANONICAL_STATUSES  # noqa: E402

BASELINE_GATE = PROJECT_ROOT / ".harness-baseline-configuration" / "hooks" / "bridge-compliance-gate.py"


def _load_gate():
    spec = importlib.util.spec_from_file_location("_gate_under_test", BASELINE_GATE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gate_accepts_every_canonical_status() -> None:
    """No canonical status may be unwritable."""
    gate = _load_gate()
    accepted = set(gate.BRIDGE_STATUS_TOKENS)
    missing = sorted(CANONICAL_STATUSES - accepted)
    assert missing == [], (
        f"The compliance gate refuses canonical status token(s) {missing}. A status "
        "canon requires but the writer rejects leaves the corresponding lifecycle "
        "step with no lawful head, which is how WI-7045 and WI-7675 both arose."
    )


def test_longer_tokens_precede_their_prefixes_in_the_tuple() -> None:
    """Declaration order is load-bearing, not cosmetic.

    The tuple also builds `BRIDGE_FILE_STATUS_RE` by joining it into an
    alternation. Python alternation is first-match, so a token listed before a
    longer token it prefixes would truncate every match of the longer one.
    """
    gate = _load_gate()
    tokens = list(gate.BRIDGE_STATUS_TOKENS)
    for index, token in enumerate(tokens):
        for later in tokens[index + 1 :]:
            assert not later.startswith(token), (
                f"{token!r} precedes {later!r}, which it prefixes: the derived "
                f"alternation would truncate every {later!r} head to {token!r}."
            )


def test_status_regex_resolves_each_canonical_token_whole() -> None:
    gate = _load_gate()
    for status in sorted(CANONICAL_STATUSES):
        assert gate.BRIDGE_FILE_STATUS_RE.match(status), (
            f"{status} does not resolve through BRIDGE_FILE_STATUS_RE, so a file "
            "already on disk bearing it would have an unresolvable status."
        )


def test_refusal_message_is_derived_from_the_constant() -> None:
    """The diagnostic must not restate the list.

    The hardcoded message omitted VERDICT-REJECTED for the entire life of the
    WI-7045 repair, so an author reading the refusal was told a token was
    invalid when the gate in fact accepted it.
    """
    source = BASELINE_GATE.read_text(encoding="utf-8")
    assert "', '.join(BRIDGE_STATUS_TOKENS)" in source, (
        "The head-token refusal message must interpolate BRIDGE_STATUS_TOKENS "
        "rather than restate it, or it will drift from the constant again."
    )
    assert "NO-GO, VERIFIED, NO-ACTION, ADVISORY, DEFERRED, WITHDRAWN" not in source, (
        "The superseded hardcoded token list is still present in the message."
    )
