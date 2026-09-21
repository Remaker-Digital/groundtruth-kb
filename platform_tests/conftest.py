"""Isolate platform tests from the invoking host's harness environment."""

from __future__ import annotations

import pytest


def _harness_marker_env_vars() -> tuple[str, ...]:
    """Every environment variable that can select an acting harness.

    The retired session-envelope resolver used to supply this list; the literal
    set below is now the single source and must be extended with any new
    harness-native session variable.
    """
    return tuple(
        sorted(
            {
                "GTKB_HARNESS_NAME",
                "GTKB_HARNESS_ID",
                "GTKB_SESSION_ID",
                "ANTIGRAVITY_SESSION_ID",
                "CLAUDE_CODE_SESSION_ID",
                "CLAUDECODE",
                "CODEX_THREAD_ID",
                "CURSOR_CONVERSATION_ID",
                "GOOSE_SESSION_ID",
            }
        )
    )


_HARNESS_SESSION_ENV_VARS = _harness_marker_env_vars()


@pytest.fixture(autouse=True)
def _hermetic_harness_environment(monkeypatch):
    """Clear ambient harness session variables before every test.

    WI-7119 replaced the hardcoded ``--harness-name`` default of "codex" with
    resolution from whichever harness-native session variable the host set. Tests
    that intend a specific harness set their own variable, but previously also
    inherited the developer's session variable, so a test intending codex could
    resolve whichever harness the test-runner happened to be running under.

    That inheritance was always latent in these tests; the constant default merely
    hid it. No test asserts on an ambient (unset-by-test) harness variable, so
    clearing them makes each test state its own harness, which is what they
    already intended. Tests still set their own variables in the test body, which
    runs after this fixture.
    """
    for env_var in _HARNESS_SESSION_ENV_VARS:
        monkeypatch.delenv(env_var, raising=False)
