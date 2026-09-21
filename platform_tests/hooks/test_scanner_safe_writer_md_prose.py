"""W0.3 item 2: scanner-safe-writer `bash_password_flag_p` md-prose exemption.

The `-p` flag pattern must not fire on `.md` prose; it fires on password-bearing
command syntax (a command whose `-p` takes the password, or a quoted `-p` value)
whatever the value looks like. Two-layer defense is preserved: real
credential-shaped values still block via the general catalog.

Authority: bridge/gtkb-w0-gate-false-positive-repair-001.md item 2 (GO at -002);
GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, _ROOT / rel)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_SSW = _load("scanner_safe_writer_under_test", ".harness-baseline-configuration/hooks/scanner-safe-writer.py")


def _names(content: str) -> list[str]:
    return [h[0] for h in _SSW._scan_content(content)]


def test_p_flag_plain_prose_allowed() -> None:
    # `-p port` / `-p version` style prose: no secret-shaped value -> ALLOW.
    assert "bash_password_flag_p" not in _names("-p port forward the traffic ")


def test_p_flag_in_password_command_syntax_blocks_whatever_the_value() -> None:
    # Observer finding 3 (2026-09-11): the value's length or composition never decides.
    assert "bash_password_flag_p" in _names("sshpass -p 'orchidlake' ssh host ")
    assert "bash_password_flag_p" in _names("sshpass -p 'abc' ssh host ")
    assert "bash_password_flag_p" in _names("mysql -p hunter2 db ")
    assert "bash_password_flag_p" in _names("mysqldump -pS3 --all-databases ")
    assert "bash_password_flag_p" in _names('run it with -p "s3cret" once ')


def test_p_flag_option_syntax_of_other_commands_allowed() -> None:
    assert "bash_password_flag_p" not in _names("mkdir -p build/out && cd build ")
    assert "bash_password_flag_p" not in _names("docker run -p 8080:80 image ")
    assert "bash_password_flag_p" not in _names("psql -p 5432 -h host db ")
    assert "bash_password_flag_p" not in _names("-p mypassword123 ")


def test_real_credential_value_blocks() -> None:
    # Two-layer defense preserved: a real credential-shaped value in md BLOCKs.
    assert _names(
        "the key is " + "AKIA" + "IOSFODNN7EXAMPLE "
    )  # AWS documentation example key, split so the scanned source never carries it
