"""The commit callback's deadline: the measured default and the setting that replaces it (owner decision 2026-09-29)."""

from __future__ import annotations

import pytest
from groundtruth_kb.project.native_commit import (
    COMMIT_CALLBACK_TIMEOUT_SECONDS,
    COMMIT_CALLBACK_TIMEOUT_VARIABLE,
    ProjectCommitError,
    commit_callback_timeout,
)


def test_the_default_deadline_is_the_measured_fifty_seconds(monkeypatch):
    monkeypatch.delenv(COMMIT_CALLBACK_TIMEOUT_VARIABLE, raising=False)
    assert COMMIT_CALLBACK_TIMEOUT_VARIABLE == "GT_PROJECT_COMMIT_CALLBACK_TIMEOUT_SECONDS"
    assert COMMIT_CALLBACK_TIMEOUT_SECONDS == 50.0
    assert commit_callback_timeout() == 50.0


@pytest.mark.parametrize("raw", ["", "   "])
def test_a_blank_setting_keeps_the_default(monkeypatch, raw):
    monkeypatch.setenv(COMMIT_CALLBACK_TIMEOUT_VARIABLE, raw)
    assert commit_callback_timeout() == 50.0


@pytest.mark.parametrize(("raw", "expected"), [("5", 5.0), ("0.5", 0.5), ("120", 120.0), (" 75 ", 75.0)])
def test_a_positive_setting_is_the_deadline(monkeypatch, raw, expected):
    monkeypatch.setenv(COMMIT_CALLBACK_TIMEOUT_VARIABLE, raw)
    assert commit_callback_timeout() == expected


@pytest.mark.parametrize("raw", ["abc", "0", "-1", "nan", "inf", "-inf", "5s"])
def test_an_invalid_setting_refuses_the_commit(monkeypatch, raw):
    monkeypatch.setenv(COMMIT_CALLBACK_TIMEOUT_VARIABLE, raw)
    with pytest.raises(
        ProjectCommitError, match="^invalid_callback_timeout: GT_PROJECT_COMMIT_CALLBACK_TIMEOUT_SECONDS "
    ):
        commit_callback_timeout()
