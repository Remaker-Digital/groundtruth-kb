"""Tests for WI-4707: .env.local auth credential injection into dispatch spawn env.

Spec-to-test mapping:
  GOV-ENV-LOCAL-AUTHORITY-001  -> test_token_injected_when_absent_from_os_environ
  Setdefault semantics         -> test_os_environ_value_not_overridden
  Allowlist scoping            -> test_non_allowlisted_key_not_injected
  Robustness (missing file)    -> test_missing_env_local_is_noop
  No credential logging        -> test_no_credential_values_in_source

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPTS_DIR = str(Path(__file__).resolve().parents[2] / "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from _env import load_env_local  # noqa: E402
from cross_harness_bridge_trigger import DISPATCH_AUTH_ENV_KEYS  # noqa: E402


def _inject_dispatch_auth(env: dict[str, str], env_file: Path) -> dict[str, str]:
    """Replicate the WI-4707 injection block from _spawn_harness for testing.

    Takes a copy of the env dict and a path to a .env.local file, applies the
    same allowlist + setdefault logic that lives in _spawn_harness, and returns
    the (possibly mutated) env dict.  A missing / unreadable env_file is a
    safe no-op per the defensive try/except in production.
    """
    try:
        env_local_values = load_env_local(check_only=True, env_file=env_file)
        for auth_key in DISPATCH_AUTH_ENV_KEYS:
            val = env_local_values.get(auth_key, "")
            if val and not env.get(auth_key):
                env[auth_key] = val
    except Exception:  # noqa: BLE001
        pass
    return env


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestDispatchAuthInjection:
    def test_token_injected_when_absent_from_os_environ(self, tmp_path: Path) -> None:
        """GOV-ENV-LOCAL-AUTHORITY-001: durable token in .env.local reaches spawn env."""
        env_file = tmp_path / ".env.local"
        env_file.write_text("CLAUDE_CODE_OAUTH_TOKEN=tok-from-env-local\n", encoding="utf-8")

        spawn_env: dict[str, str] = {}
        result = _inject_dispatch_auth(spawn_env, env_file)

        assert result.get("CLAUDE_CODE_OAUTH_TOKEN") == "tok-from-env-local"

    def test_os_environ_value_not_overridden(self, tmp_path: Path) -> None:
        """Setdefault: existing env value must never be overridden by .env.local."""
        env_file = tmp_path / ".env.local"
        env_file.write_text("CLAUDE_CODE_OAUTH_TOKEN=tok-from-env-local\n", encoding="utf-8")

        spawn_env: dict[str, str] = {"CLAUDE_CODE_OAUTH_TOKEN": "tok-from-os-environ"}
        result = _inject_dispatch_auth(spawn_env, env_file)

        assert result["CLAUDE_CODE_OAUTH_TOKEN"] == "tok-from-os-environ"

    def test_non_allowlisted_key_not_injected(self, tmp_path: Path) -> None:
        """Allowlist scoping: .env.local keys outside DISPATCH_AUTH_ENV_KEYS are never injected."""
        env_file = tmp_path / ".env.local"
        env_file.write_text(
            "CLAUDE_CODE_OAUTH_TOKEN=tok-ok\nMY_SECRET_DB_PASSWORD=super-secret\nANOTHER_SECRET=also-secret\n",
            encoding="utf-8",
        )

        spawn_env: dict[str, str] = {}
        result = _inject_dispatch_auth(spawn_env, env_file)

        assert "MY_SECRET_DB_PASSWORD" not in result
        assert "ANOTHER_SECRET" not in result
        # the allowlisted key is still injected
        assert result.get("CLAUDE_CODE_OAUTH_TOKEN") == "tok-ok"

    def test_missing_env_local_is_noop(self, tmp_path: Path) -> None:
        """Robustness: absent .env.local must not raise; spawn env is returned unchanged."""
        env_file = tmp_path / ".env.local"  # does NOT exist

        spawn_env: dict[str, str] = {"EXISTING_KEY": "existing-value"}
        result = _inject_dispatch_auth(spawn_env, env_file)

        assert result == {"EXISTING_KEY": "existing-value"}

    def test_all_allowlisted_keys_injected(self, tmp_path: Path) -> None:
        """All three DISPATCH_AUTH_ENV_KEYS are injected when present in .env.local."""
        env_file = tmp_path / ".env.local"
        lines = "\n".join(f"{k}=value-for-{k}" for k in DISPATCH_AUTH_ENV_KEYS)
        env_file.write_text(lines + "\n", encoding="utf-8")

        spawn_env: dict[str, str] = {}
        result = _inject_dispatch_auth(spawn_env, env_file)

        for key in DISPATCH_AUTH_ENV_KEYS:
            assert result.get(key) == f"value-for-{key}", f"missing injection for {key}"

    def test_empty_value_in_env_local_not_injected(self, tmp_path: Path) -> None:
        """A key present in .env.local with an empty value is treated as absent."""
        env_file = tmp_path / ".env.local"
        env_file.write_text("CLAUDE_CODE_OAUTH_TOKEN=\n", encoding="utf-8")

        spawn_env: dict[str, str] = {}
        result = _inject_dispatch_auth(spawn_env, env_file)

        # empty string value → not injected (falsy guard `if val`)
        assert "CLAUDE_CODE_OAUTH_TOKEN" not in result


class TestNoCredentialLogging:
    """GOV-ENV-LOCAL-AUTHORITY-001 / implementation constraint: credential values must never
    appear in logging calls within the injection code path."""

    _SOURCE_FILE = Path(__file__).resolve().parents[2] / "scripts" / "cross_harness_bridge_trigger.py"

    def _extract_injection_block_lines(self) -> list[str]:
        """Return the source lines of the WI-4707 injection block."""
        source = self._SOURCE_FILE.read_text(encoding="utf-8")
        lines = source.splitlines()
        # Find the WI-4707 comment that marks the block start
        start = next(
            (i for i, ln in enumerate(lines) if "WI-4707" in ln and "inject .env.local" in ln),
            None,
        )
        assert start is not None, "WI-4707 injection block not found in source"
        # Collect lines until we hit the next non-indented line after the block
        block: list[str] = []
        for ln in lines[start:]:
            if ln.strip() == "" or ln.startswith("    "):
                block.append(ln)
            else:
                break
        return block

    def test_no_credential_values_in_source(self) -> None:
        """Credential VALUES must not be passed to any logging call in the injection block."""
        block_lines = self._extract_injection_block_lines()
        block_text = "\n".join(block_lines)

        # Patterns that would log credential values (not just key names)
        log_value_patterns = [
            r"\blog(?:ger)?\.(?:debug|info|warning|error|critical)\s*\([^)]*_val\b",
            r"\bprint\s*\([^)]*_val\b",
            r"\bsys\.stdout\.write\s*\([^)]*_val\b",
        ]
        for pattern in log_value_patterns:
            match = re.search(pattern, block_text)
            assert match is None, f"Credential value appears in log call matching {pattern!r}: {match.group()!r}"
