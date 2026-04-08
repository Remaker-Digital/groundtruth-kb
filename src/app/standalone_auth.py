"""
Standalone Admin SPA — production merchant admin (password-gated).

Password gate: merchants enter a password, receive a session cookie, and
access the full admin dashboard.  The password is set via the
ADMIN_PREVIEW_PASSWORD environment variable on the Container App.

After passing the password gate, merchants sign in with their API key
inside the SPA for tenant-scoped access to all admin features.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import hmac as _hmac
import logging
import os
import pathlib
import secrets as _secrets
import time as _time

import argon2

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from starlette.responses import Response as StarletteResponse
from starlette.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level state (importable by tests)
# ---------------------------------------------------------------------------

_admin_standalone_dist = pathlib.Path(__file__).resolve().parent.parent.parent / "admin" / "standalone" / "dist"
_ADMIN_INITIAL_PASSWORD = os.environ.get("ADMIN_PREVIEW_PASSWORD", "")
_ADMIN_RESET_EMAIL = os.environ.get("ADMIN_RESET_EMAIL", "").strip().lower()
_ADMIN_COOKIE_NAME = "agentred_admin"
_CSRF_COOKIE_NAME = "agentred_csrf"
_MIN_PASSWORD_LENGTH = 12

# Argon2id password hashing (SPEC-1688)
_ph = argon2.PasswordHasher(type=argon2.Type.ID)


def _hash_password(password: str) -> str:
    """Hash a password using Argon2id."""
    return _ph.hash(password)


def _verify_password(password: str) -> bool:
    """Verify a password against the stored Argon2id hash."""
    if not _admin_password_hash:
        return False
    try:
        return _ph.verify(_admin_password_hash, password)
    except argon2.exceptions.VerifyMismatchError:
        return False


_admin_password_hash: str = _hash_password(_ADMIN_INITIAL_PASSWORD) if _ADMIN_INITIAL_PASSWORD else ""
# Immutable HMAC key for reset tokens -- derived deterministically from the env var
# password so all replicas agree.  Uses SHA-256 (not Argon2) because this needs
# to be deterministic and fast (signing key, not password storage).
_ADMIN_HMAC_KEY: str = (
    hashlib.sha256(f"agentred-admin:{_ADMIN_INITIAL_PASSWORD}".encode()).hexdigest() if _ADMIN_INITIAL_PASSWORD else ""
)

# Session secret for signing session tokens (SPEC-1689).
# If ADMIN_SESSION_SECRET env var is set, use it (consistent across replicas).
# Otherwise derive deterministically from the password so multi-replica deployments
# all agree on the signing key.
_SESSION_SECRET: str = os.environ.get("ADMIN_SESSION_SECRET", "") or (
    _hmac.new(b"agentred-session", _ADMIN_INITIAL_PASSWORD.encode(), "sha256").hexdigest()
    if _ADMIN_INITIAL_PASSWORD
    else _secrets.token_hex(32)
)


def _generate_session_token(ttl: int = 86400 * 7) -> str:
    """Create an HMAC-signed session token valid for *ttl* seconds (default 7 days)."""
    nonce = _secrets.token_urlsafe(24)
    expiry = str(int(_time.time() + ttl))
    payload = f"{nonce}.{expiry}"
    sig = _hmac.new(_SESSION_SECRET.encode(), payload.encode(), "sha256").hexdigest()
    return f"{payload}.{sig}"


def _validate_session_token(token: str) -> bool:
    """Validate an HMAC-signed session token (signature + expiry)."""
    if not token:
        return False
    parts = token.split(".")
    if len(parts) != 3:
        return False
    nonce, expiry_str, sig = parts
    payload = f"{nonce}.{expiry_str}"
    expected = _hmac.new(_SESSION_SECRET.encode(), payload.encode(), "sha256").hexdigest()
    if not _hmac.compare_digest(sig, expected):
        return False
    try:
        if _time.time() > float(expiry_str):
            return False
    except ValueError:
        return False
    return True


def _generate_csrf_token() -> str:
    """Generate a cryptographically random CSRF token (double-submit cookie pattern)."""
    return _secrets.token_urlsafe(32)


def _validate_csrf_token(form_token: str, cookie_token: str) -> bool:
    """Validate CSRF token: compare form field with cookie value."""
    if not form_token or not cookie_token:
        return False
    return _hmac.compare_digest(form_token, cookie_token)


# Password reset tokens -- HMAC-signed so any replica can validate without shared state.
# Token format: "<nonce>.<expiry_ts>.<hmac_hex>"
# Signed with _ADMIN_HMAC_KEY (deterministic across replicas from env var).

_admin_used_reset_nonces: set[str] = set()  # best-effort single-use per replica

_STANDALONE_SHARED_STYLES = """
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0a0a0a; color: #e0e0e0; font-family: Inter, system-ui, sans-serif;
         display: flex; align-items: center; justify-content: center; min-height: 100vh; }
  .card { background: #1f1f1f; border: 1px solid #272727; border-radius: 12px;
          padding: 40px; max-width: 400px; width: 100%; text-align: center; }
  h1 { font-size: 20px; margin-bottom: 4px; color: #f5f5f5; }
  .subtitle { font-size: 14px; color: #a0a0a0; margin-bottom: 24px; }
  label { display: block; font-size: 13px; font-weight: 500; color: #a0a0a0;
          margin-bottom: 6px; text-align: left; }
  input { width: 100%; padding: 10px 14px; border: 1px solid #272727; border-radius: 8px;
          background: #141414; color: #e0e0e0; font-size: 14px; margin-bottom: 12px;
          outline: none; }
  input:focus { border-color: #ff3621; }
  button[type="submit"] { width: 100%; padding: 10px; border: none; border-radius: 8px;
           background: #ff3621; color: #fff; font-size: 14px; font-weight: 600;
           cursor: pointer; margin-top: 4px; }
  button[type="submit"]:hover { background: #e62e1a; }
  .error { color: #ff6b6b; font-size: 13px; margin-bottom: 12px; display: none; }
  .success { color: #4caf50; font-size: 13px; margin-bottom: 12px; display: none; }
  .link { color: #ff3621; font-size: 13px; text-decoration: none; cursor: pointer;
          display: inline-block; margin-top: 16px; }
  .link:hover { text-decoration: underline; }
  .logo { margin-bottom: 16px; display: block; margin-left: auto; margin-right: auto; }
"""

_LOGO_DATA_URI = (
    "data:image/svg+xml;base64,"
    "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjxzdmcKICAgaWQ9IkxheWVyXzIi"
    "CiAgIHZpZXdCb3g9IjAgMCA1MjAuMDAwMDIgMTI4IgogICB2ZXJzaW9uPSIxLjEiCiAgIHdpZHRoPSI1MjAiCiAgIGhlaWdodD0i"
    "MTI4IgogICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgIHhtbG5zOnN2Zz0iaHR0cDovL3d3dy53My5vcmcv"
    "MjAwMC9zdmciPgogIDxkZWZzCiAgICAgaWQ9ImRlZnMxIj4KICAgIDxzdHlsZQogICAgICAgaWQ9InN0eWxlMSI+LmNscy0xe2Zp"
    "bGw6I2ZmZjt9LmNscy0ye2ZpbGw6bm9uZTt9LmNscy0ze2ZpbGw6I2ZmMzYyMTt9PC9zdHlsZT4KICA8L2RlZnM+CiAgPHJlY3QK"
    "ICAgICBjbGFzcz0iY2xzLTIiCiAgICAgd2lkdGg9IjEyOC40NDQ2NCIKICAgICBoZWlnaHQ9IjEyOCIKICAgICBpZD0icmVjdDEi"
    "CiAgICAgeD0iMCIKICAgICB5PSIwIgogICAgIHN0eWxlPSJzdHJva2Utd2lkdGg6MS4zODk0OSIgLz4KICA8cmVjdAogICAgIGNs"
    "YXNzPSJjbHMtMyIKICAgICB4PSIxLjEzOTM4MzMiCiAgICAgeT0iMS4zMjY5NjkxIgogICAgIHdpZHRoPSIxMjYuMjc3MDIiCiAg"
    "ICAgaGVpZ2h0PSIxMjUuMzQ2MDYiCiAgICAgaWQ9InJlY3QyIgogICAgIHN0eWxlPSJzdHJva2Utd2lkdGg6MS4zODk0OSIgLz4K"
    "ICA8cGF0aAogICAgIGNsYXNzPSJjbHMtMSIKICAgICBkPSJtIDUwLjA5ODEzLDQzLjM2NjA0NSBoIDExLjg4MDE1NiB2IDcuMjM5"
    "MjUzIGggMC4xODA2MzQgYyAyLjI1MDk3NywtNS4zMDc4NTkgNy41NTg4MzYsLTguMzc4NjM2IDEzLjUwNTg2MSwtOC4zNzg2MzYg"
    "MS42MjU3MDYsMCAyLjQzMTYxMSwwLjIzNjIxMyAyLjc5Mjg3OSwwLjMxOTU4MyB2IDEyLjE1ODA1NCBjIC0xLjE2NzE3MywtMC40"
    "MDI5NTMgLTIuNjEyMjQ1LC0wLjU2OTY5MiAtNC4wNTczMTYsLTAuNTY5NjkyIC03LjM3ODIwMiwwIC0xMS42OTk1MjIsNC43NTIw"
    "NjIgLTExLjY5OTUyMiwxMS4yNjg3NzkgViA4NS43NzMzMzggSCA1MC4wOTgxMyB2IC00Mi40MjExODggMCB6IgogICAgIGlkPSJw"
    "YXRoMyIKICAgICBzdHlsZT0ic3Ryb2tlLXdpZHRoOjEuMzg5NDkiIC8+CiAgPGcKICAgICBpZD0iZzE0IgogICAgIHRyYW5zZm9y"
    "bT0idHJhbnNsYXRlKDAuMDYyNTI0OTcpIj4KICAgIDxwYXRoCiAgICAgICBjbGFzcz0iY2xzLTEiCiAgICAgICBkPSJNIDI0LjYw"
    "NzkwMiw4OS41NTk3MDIgViA3My40NTU0OTEgYyAwLC0zLjg2Mjc4OCAtMy45NDYxNTcsLTQuOTg4Mjc2IC03LjQwNTk5MiwtNS4y"
    "MzgzODUgdiAtOC40NDgxMSBjIDMuNDU5ODM1LC0wLjA4MzM3IDcuNDA1OTkyLC0xLjIwODg1OCA3LjQwNTk5MiwtNC42Njg2OTMg"
    "ViAzOC41MjM2NjQgYyAwLC02LjYwMDA4NiA1Ljg3NzU1LC0xMS40MzU1MTggMTEuOTA3OTQ1LC0xMS40MzU1MTggaCA2LjkxOTY3"
    "IHYgOS45NzY1NTEgaCAtMy42OTYwNDkgYyAtMy4yOTMwOTUsMCAtNC4wOTkwMDEsMS44NDgwMjUgLTQuMDk5MDAxLDQuNjY4Njkz"
    "IHYgMTQuMDA2MDc4IGMgMCw1Ljc5NDE4MiAtNC41ODUzMjMsNy43MjU1NzUgLTguMjExODk3LDguMjExODk4IHYgMC4xNjY3Mzgg"
    "YyAyLjgyMDY2OSwwLjQ4NjMyMyA4LjEyODUyOCwxLjkzMTM5NCA4LjIxMTg5Nyw4LjYxNDg1MSB2IDEzLjYwMzEyNiBjIDAsMi44"
    "MjA2NjggMC44MDU5MDYsNC42Njg2OTMgNC4wOTkwMDEsNC42Njg2OTMgaCAzLjY5NjA0OSB2IDkuOTA3MDc2IGggLTYuOTE5Njcg"
    "YyAtNi4wMzAzOTUsMCAtMTEuOTA3OTQ1LC00Ljc1MjA2MiAtMTEuOTA3OTQ1LC0xMS4zNTIxNDggeiIKICAgICAgIGlkPSJwYXRo"
    "MiIKICAgICAgIHN0eWxlPSJzdHJva2Utd2lkdGg6MS4zODk0OSIgLz4KICAgIDxwYXRoCiAgICAgICBjbGFzcz0iY2xzLTEiCiAg"
    "ICAgICBkPSJtIDg0Ljk5NTIyLDkxLjAwNDc3MSBoIDMuNjI2NTczIGMgMy4zNzY0NjYsMCA0LjE4MjM3MSwtMS44NDgwMjQgNC4x"
    "ODIzNzEsLTQuNjY4NjkyIFYgNzIuNzMyOTUzIGMgMCwtNi42ODM0NTYgNS4zMDc4NTksLTguMTI4NTI4IDguMTI4NTI2LC04LjYx"
    "NDg1IFYgNjMuOTUxMzY0IEMgOTcuMzg5NDg3LDYzLjQ2NTA0MiA5Mi44MDQxNjQsNjEuNTMzNjQ4IDkyLjgwNDE2NCw1NS43Mzk0"
    "NjcgViA0MS43MzMzODkgYyAwLC0yLjgyMDY2OSAtMC44MDU5MDUsLTQuNjY4NjkzIC00LjE4MjM3MSwtNC42Njg2OTMgSCA4NC45"
    "OTUyMiB2IC05Ljk3NjU1MiBoIDYuOTE5NjY5IGMgNi4wMzAzOTUsMCAxMS45MDc5NDEsNC44MzU0MzIgMTEuOTA3OTQxLDExLjQz"
    "NTUxOCB2IDE2LjU3NjYzOSBjIDAsMy40NTk4MzUgMy45NDYxNiw0LjU4NTMyMyA3LjQwNiw0LjY2ODY5MyB2IDguNDQ4MTEgYyAt"
    "My41NDMyMSwwLjIzNjIxNCAtNy40MDYsMS4zNjE3MDIgLTcuNDA2LDUuMjM4Mzg1IFYgODkuNTU5NyBjIDAsNi42MDAwODYgLTUu"
    "ODc3NTQ2LDExLjM1MjE1IC0xMS45MDc5NDEsMTEuMzUyMTUgSCA4NC45OTUyMiBaIgogICAgICAgaWQ9InBhdGg0IgogICAgICAg"
    "c3R5bGU9InN0cm9rZS13aWR0aDoxLjM4OTQ5IiAvPgogIDwvZz4KICA8ZwogICAgIGlkPSJnMTMiCiAgICAgdHJhbnNmb3JtPSJ0"
    "cmFuc2xhdGUoMCwtMC40MzA3MzkpIj4KICAgIDxwYXRoCiAgICAgICBjbGFzcz0iY2xzLTEiCiAgICAgICBkPSJtIDE2Ny41MzEw"
    "NCw2NS4xNjcxNyBjIDAsLTkuNjcwODY0IDYuNzI1MTQsLTE2LjkzNzkwNiAxNS43MTUxNSwtMTYuOTM3OTA2IDQuNzY1OTYsMCA4"
    "LjQ0ODExLDIuMTM5ODE3IDEwLjI4MjI0LDQuODM1NDMyIGggMC4wNTU2IHYgLTMuOTczOTQ3IGggOC41NTkyNyB2IDMyLjIzNjIx"
    "MiBoIC04LjA3Mjk1IHYgLTQuNDA0Njg5IGggLTAuMTI1MDUgYyAtMS43MDkwOCwyLjg3NjI0OCAtNS44Nzc1NSw1LjI2NjE3NCAt"
    "MTAuODI0MTQsNS4yNjYxNzQgLTguNjg0MzMsMCAtMTUuNjA0LC03LjE1NTg4MyAtMTUuNjA0LC0xNy4wMDczODEgeiBtIDE3LjU0"
    "OTI4LDkuNDIwNzU1IGMgNS4xNDExMiwwIDguNjg0MzMsLTQuMTU0NTgxIDguNjg0MzMsLTkuMzY1MTc1IDAsLTUuMjEwNTk1IC0z"
    "LjU0MzIxLC05LjM2NTE3NiAtOC42ODQzMywtOS4zNjUxNzYgLTUuMTQxMTIsMCAtOC42ODQzMiw0LjA0MzQyMiAtOC42ODQzMiw5"
    "LjM2NTE3NiAwLDUuMzIxNzU0IDMuNTQzMiw5LjM2NTE3NSA4LjY4NDMyLDkuMzY1MTc1IHoiCiAgICAgICBpZD0icGF0aDUiCiAg"
    "ICAgICBzdHlsZT0ic3Ryb2tlLXdpZHRoOjEuMzg5NDkiIC8+CiAgICA8cGF0aAogICAgICAgY2xhc3M9ImNscy0xIgogICAgICAg"
    "ZD0ibSAyMTIuMzAwNDcsODkuMDI0NzQ2IDMuNjY4MjYsLTUuMjY2MTc0IGMgMS45NTkxOCwyLjA4NDIzOCA1LjE5NjcsMy40MTgx"
    "NSA5LjI0MDEyLDMuNDE4MTUgNC43NjU5NSwwIDkuMzY1MTcsLTIuMTM5ODE4IDkuMzY1MTcsLTcuODkyMzE0IHYgLTIuMzg5OTI2"
    "IGggLTAuMTI1MDUgYyAtMS43MDkwOCwyLjg3NjI0OCAtNS44Nzc1NSw1LjI2NjE3NCAtMTAuODI0MTQsNS4yNjYxNzQgLTguNjg0"
    "MzMsMCAtMTUuNjA0LC03LjE1NTg4MyAtMTUuNjA0LC0xNy4wMDczODEgMCwtOS44NTE0OTcgNi43MjUxNCwtMTYuOTM3OTA2IDE1"
    "LjcxNTE2LC0xNi45Mzc5MDYgNC43NjU5NSwwIDguNDQ4MTEsMi4xMzk4MTcgMTAuMjgyMjQsNC44MzU0MzIgaCAwLjA1NTYgdiAt"
    "My45NzM5NDcgaCA4LjU1OTI3IHYgMjkuMTA5ODU1IGMgMCw5LjU0NTgxIC01LjYyNzQ1LDE1LjIyODgzMSAtMTYuNzU3MjgsMTUu"
    "MjI4ODMxIC02LjExMzc2LDAgLTExLjA3NDI1LC0xLjcwOTA3NSAtMTMuNTc1MzMsLTQuNDA0Njg5IHogbSAxMy4yNjk2NSwtMTQu"
    "NDM2ODIxIGMgNS4xNDExMiwwIDguNjg0MzIsLTQuMTU0NTgxIDguNjg0MzIsLTkuMzY1MTc1IDAsLTUuMjEwNTk1IC0zLjU0MzIs"
    "LTkuMzY1MTc2IC04LjY4NDMyLC05LjM2NTE3NiAtNS4xNDExMiwwIC04LjY4NDMzLDQuMDQzNDIyIC04LjY4NDMzLDkuMzY1MTc2"
    "IDAsNS4zMjE3NTQgMy41NDMyMSw5LjM2NTE3NSA4LjY4NDMzLDkuMzY1MTc1IHoiCiAgICAgICBpZD0icGF0aDYiCiAgICAgICBz"
    "dHlsZT0ic3Ryb2tlLXdpZHRoOjEuMzg5NDkiIC8+CiAgICA8cGF0aAogICAgICAgY2xhc3M9ImNscy0xIgogICAgICAgZD0ibSAy"
    "NDguNTEwNjMsNjUuMjIyNzUgYyAwLC05Ljc4MjAyMyA3LjEwMDMsLTE3LjAwNzM4MSAxNi43NTcyNywtMTcuMDA3MzgxIDguNjg0"
    "MzIsMCAxNi43MDE2OSw1Ljc1MjQ5NiAxNi43MDE2OSwxOS4xNDcxOTggdiAwLjQzMDc0MyBoIC0yNC41OTQwMSBjIDAuOTE3MDcs"
    "NC45NjA0ODYgNC4wOTkwMSw3LjAzMDgyOSA4LjA3Mjk1LDcuMDMwODI5IDIuOTMxODMsMCA1Ljc1MjUsLTEuMTY3MTczIDcuNTMx"
    "MDUsLTMuNTQzMjA1IGwgNi40MTk0NSw0LjM0OTExIGMgLTIuNzUxMTksMy4zNjI1NzEgLTYuODUwMTksNi41NDQ1MDcgLTEzLjk1"
    "MDUsNi41NDQ1MDcgLTkuNzI2NDQsMCAtMTYuOTM3OSwtNy4xNTU4ODMgLTE2LjkzNzksLTE2LjkzNzkwNiB6IG0gMjQuMjE4ODQs"
    "LTMuMjM3NTE2IGMgLTAuNjExMzgsLTQuMDQzNDIyIC0zLjM2MjU3LC02LjYwMDA4NyAtNy41MzEwNSwtNi42MDAwODcgLTMuNjEy"
    "NjcsMCAtNi45NzUyNSwyLjAxNDc2MyAtNy44MjI4NCw2LjYwMDA4NyB6IgogICAgICAgaWQ9InBhdGg3IgogICAgICAgc3R5bGU9"
    "InN0cm9rZS13aWR0aDoxLjM4OTQ5IiAvPgogICAgPHBhdGgKICAgICAgIGNsYXNzPSJjbHMtMSIKICAgICAgIGQ9Im0gMjg3Ljgz"
    "MzI1LDQ5LjA3Njg1NCBoIDguMDcyOTUgdiA0LjI3OTYzNSBoIDAuMTI1MDUgYyAxLjk1OTE4LC0yLjc1MTE5NCA0Ljk2MDQ5LC01"
    "LjAxNjA2NiAxMC4wODc3MSwtNS4wMTYwNjYgOC4xOTgsMCAxMi4xNzE5NSw1LjI2NjE3NSAxMi4xNzE5NSwxMy41MTk3NTYgdiAx"
    "OS40NTI4ODcgaCAtOC41NTkyNyBWIDY0LjE4MDYzMSBjIDAsLTQuNjU0Nzk4IC0xLjQ3Mjg2LC03Ljk0Nzg5NCAtNi4yMzg4Miwt"
    "Ny45NDc4OTQgLTQuNzY1OTYsMCAtNy4xMDAzLDMuMzA2OTkxIC03LjEwMDMsOC4wMTczNjggdiAxNy4wNjI5NjEgaCAtOC41NTky"
    "NyB6IgogICAgICAgaWQ9InBhdGg4IgogICAgICAgc3R5bGU9InN0cm9rZS13aWR0aDoxLjM4OTQ5IiAvPgogICAgPHBhdGgKICAg"
    "ICAgIGNsYXNzPSJjbHMtMSIKICAgICAgIGQ9Ik0gMzI3Ljk0Nzg4LDczLjcyNjQ0IFYgNTYuMjg4MzE3IGggLTUuMTQxMTIgdiAt"
    "Ny4yMTE0NjMgaCA1LjE0MTEyIHYgLTkuMzY1MTc1IGggOC41NTkyNyB2IDkuMzY1MTc1IGggNy4xMDAzIHYgNy4yMTE0NjMgaCAt"
    "Ny4xMDAzIHYgMTYuMDIwODQxIGMgMCwyLjAxNDc2NCAxLjQwMzM5LDIuNTAxMDg2IDMuMzA2OTksMi41MDEwODYgMS40NzI4Niww"
    "IDIuOTMxODMsLTAuMzA1Njg4IDQuMDQzNDIsLTAuNTU1Nzk3IHYgNy4wMzA4MjkgYyAtMS40MDMzOSwwLjMwNTY4OCAtNC4xNTQ1"
    "OCwwLjYxMTM3NyAtNi4yMzg4MiwwLjYxMTM3NyAtNS4xNDExMiwwIC05LjY3MDg2LC0xLjgzNDEzIC05LjY3MDg2LC04LjE5ODAw"
    "MyB6IgogICAgICAgaWQ9InBhdGg5IgogICAgICAgc3R5bGU9InN0cm9rZS13aWR0aDoxLjM4OTQ5IiAvPgogICAgPHBhdGgKICAg"
    "ICAgIGNsYXNzPSJjbHMtMyIKICAgICAgIGQ9Im0gMzQ3LjUyNTgyLDg1LjM0MjU5MiBoIDI3LjcwNjQ3IHYgNS4wMTYwNjYgaCAt"
    "MjcuNzA2NDcgeiIKICAgICAgIGlkPSJwYXRoMTAiCiAgICAgICBzdHlsZT0iZmlsbDojZmZmZmZmO2ZpbGwtb3BhY2l0eToxO3N0"
    "cm9rZS13aWR0aDoxLjM4OTQ5IiAvPgogICAgPHBhdGgKICAgICAgIGNsYXNzPSJjbHMtMyIKICAgICAgIGQ9Im0gMzgwLjk4NDc4"
    "LDQ5LjA3Njg1NCBoIDguMDcyOTUgdiA1LjUwMjM4OCBoIDAuMTI1MDYgYyAxLjUyODQ0LC00LjA0MzQyMiA1LjE0MTEyLC02LjM2"
    "Mzg3MyA5LjE3MDY0LC02LjM2Mzg3MyAxLjA5NzcsMCAxLjY1MzUsMC4xODA2MzQgMS45MDM2MSwwLjI1MDEwOCB2IDkuMjQwMTIy"
    "IGMgLTAuNzkyMDEsLTAuMzA1Njg5IC0xLjc3ODU1LC0wLjQzMDc0MyAtMi43NTEyLC0wLjQzMDc0MyAtNS4wMTYwNiwwIC03Ljk0"
    "Nzg5LDMuNjEyNjc5IC03Ljk0Nzg5LDguNTU5MjcgdiAxNS40Nzg5NCBoIC04LjU1OTI3IFYgNDkuMDc2ODU0IFoiCiAgICAgICBp"
    "ZD0icGF0aDExIgogICAgICAgc3R5bGU9InN0cm9rZS13aWR0aDoxLjM4OTQ5IiAvPgogICAgPHBhdGgKICAgICAgIGNsYXNzPSJj"
    "bHMtMyIKICAgICAgIGQ9Im0gNDAyLjgxMzcsNjUuMjIyNzUgYyAwLC05Ljc4MjAyMyA3LjEwMDMxLC0xNy4wMDczODEgMTYuNzU3"
    "MjcsLTE3LjAwNzM4MSA4LjY4NDMzLDAgMTYuNzAxNyw1Ljc1MjQ5NiAxNi43MDE3LDE5LjE0NzE5OCB2IDAuNDMwNzQzIGggLTI0"
    "LjU5NDAxIGMgMC45MTcwNiw0Ljk2MDQ4NiA0LjA5OSw3LjAzMDgyOSA4LjA3Mjk1LDcuMDMwODI5IDIuOTMxODMsMCA1Ljc1MjQ5"
    "LC0xLjE2NzE3MyA3LjUzMTA0LC0zLjU0MzIwNSBsIDYuNDE5NDYsNC4zNDkxMSBjIC0yLjc1MTIsMy4zNjI1NzEgLTYuODUwMiw2"
    "LjU0NDUwNyAtMTMuOTUwNSw2LjU0NDUwNyAtOS43MjY0NSwwIC0xNi45Mzc5MSwtNy4xNTU4ODMgLTE2LjkzNzkxLC0xNi45Mzc5"
    "MDYgeiBtIDI0LjIzMjc0LC0zLjIzNzUxNiBjIC0wLjYxMTM4LC00LjA0MzQyMiAtMy4zNjI1NywtNi42MDAwODcgLTcuNTMxMDUs"
    "LTYuNjAwMDg3IC0zLjYxMjY3LDAgLTYuOTc1MjQsMi4wMTQ3NjMgLTcuODIyODMsNi42MDAwODcgeiIKICAgICAgIGlkPSJwYXRo"
    "MTIiCiAgICAgICBzdHlsZT0ic3Ryb2tlLXdpZHRoOjEuMzg5NDkiIC8+CiAgICA8cGF0aAogICAgICAgY2xhc3M9ImNscy0zIgog"
    "ICAgICAgZD0ibSA0NDAuMzE2MDksNjUuMTY3MTcgYyAwLC05LjY3MDg2NCA2LjcyNTE0LC0xNi45Mzc5MDYgMTUuNzE1MTUsLTE2"
    "LjkzNzkwNiA0Ljc2NTk2LDAgOC40MzQyMiwyLjEzOTgxNyAxMC4yODIyNCw0LjgzNTQzMiBoIDAuMDU1NiBWIDM1LjQ0NTkzOCBo"
    "IDguNTU5MjcgdiA0NS44ODEwMjMgaCAtOC4wNzI5NSB2IC00LjQwNDY4OSBoIC0wLjEyNTA1IGMgLTEuNzA5MDgsMi44NzYyNDgg"
    "LTUuODc3NTUsNS4yNjYxNzQgLTEwLjgyNDE0LDUuMjY2MTc0IC04LjY4NDMzLDAgLTE1LjYwNCwtNy4xNTU4ODMgLTE1LjYwNCwt"
    "MTcuMDA3MzgxIHogbSAxNy41NDkyOCw5LjQyMDc1NSBjIDUuMTQxMTIsMCA4LjY4NDMzLC00LjE1NDU4MSA4LjY4NDMzLC05LjM2"
    "NTE3NSAwLC01LjIxMDU5NSAtMy41NDMyMSwtOS4zNjUxNzYgLTguNjg0MzMsLTkuMzY1MTc2IC01LjE0MTEyLDAgLTguNjg0MzIs"
    "NC4wNDM0MjIgLTguNjg0MzIsOS4zNjUxNzYgMCw1LjMyMTc1NCAzLjU0MzIsOS4zNjUxNzUgOC42ODQzMiw5LjM2NTE3NSB6Igog"
    "ICAgICAgaWQ9InBhdGgxMyIKICAgICAgIHN0eWxlPSJzdHJva2Utd2lkdGg6MS4zODk0OSIgLz4KICA8L2c+Cjwvc3ZnPgo="
)

_STANDALONE_FORGOT_LINK = (
    '  <a href="/admin/standalone/_forgot-password" class="link">Forgot your password?</a>'
    if _ADMIN_RESET_EMAIL
    else ""
)
_STANDALONE_LOGIN_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Agent Red — Sign In</title>
<style>{_STANDALONE_SHARED_STYLES}</style>
</head>
<body>
<div class="card">
  <img src="{_LOGO_DATA_URI}" alt="Agent Red" width="200" height="49" class="logo" />
  <p class="subtitle">Customer Experience Admin</p>
  <div class="error" id="err">Incorrect password. Please try again.</div>
  <form method="POST" action="/admin/standalone/_auth">
    <input type="hidden" name="csrf_token" value="{{{{csrf_token}}}}"/>
    <label for="pw">Password</label>
    <input id="pw" type="password" name="password" placeholder="Enter your password" autofocus required/>
    <button type="submit">Sign In</button>
  </form>
{_STANDALONE_FORGOT_LINK}
</div>
</body>
</html>"""

_STANDALONE_FORGOT_PW_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Agent Red — Forgot Password</title>
<style>{_STANDALONE_SHARED_STYLES}</style>
</head>
<body>
<div class="card">
  <img src="{_LOGO_DATA_URI}" alt="Agent Red" width="200" height="49" class="logo" />
  <h1>Forgot password</h1>
  <p class="subtitle">Enter your email address and we'll send you a link to reset your password.</p>
  <div class="error" id="err">Please enter a valid email address.</div>
  <form method="POST" action="/admin/standalone/_forgot-password">
    <input type="hidden" name="csrf_token" value="{{{{csrf_token}}}}"/>
    <label for="email">Email address</label>
    <input id="email" type="email" name="email" placeholder="you@company.com" autofocus required/>
    <button type="submit">Send reset link</button>
  </form>
  <a href="/admin/standalone/" class="link">Back to sign in</a>
</div>
</body>
</html>"""

_STANDALONE_FORGOT_PW_SENT_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Agent Red — Check Your Email</title>
<style>{_STANDALONE_SHARED_STYLES}</style>
</head>
<body>
<div class="card">
  <img src="{_LOGO_DATA_URI}" alt="Agent Red" width="200" height="49" class="logo" />
  <div style="font-size:32px;margin-bottom:12px;">&#9993;</div>
  <h1>Check your email</h1>
  <p class="subtitle">If that email matches our records,
  we've sent a password reset link. The link expires in 15 minutes.</p>
  <p style="font-size:13px;color:#a0a0a0;line-height:1.5;margin-top:12px;">
    Don't see it? Check your spam folder.
  </p>
  <a href="/admin/standalone/" class="link">Back to sign in</a>
</div>
</body>
</html>"""

_STANDALONE_RESET_PW_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Agent Red — Set New Password</title>
<style>{_STANDALONE_SHARED_STYLES}</style>
</head>
<body>
<div class="card">
  <img src="{_LOGO_DATA_URI}" alt="Agent Red" width="200" height="49" class="logo" />
  <h1>Set new password</h1>
  <p class="subtitle">Choose a new password for admin access.</p>
  <div class="error" id="err">Passwords do not match.</div>
  <div class="success" id="ok">Password changed successfully!</div>
  <form method="POST" action="/admin/standalone/_reset-password">
    <input type="hidden" name="token" value="{{{{token}}}}"/>
    <input type="hidden" name="csrf_token" value="{{{{csrf_token}}}}"/>
    <label for="new">New password</label>
    <input id="new" type="password" name="new_password" placeholder="New password" autofocus required minlength="12"/>
    <label for="confirm">Confirm new password</label>
    <input id="confirm" type="password" name="confirm_password"
      placeholder="Confirm new password" required minlength="12"/>
    <button type="submit">Set password</button>
  </form>
  <a href="/admin/standalone/" class="link">Back to sign in</a>
</div>
</body>
</html>"""

_STANDALONE_RESET_INVALID_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Agent Red — Invalid Link</title>
<style>{_STANDALONE_SHARED_STYLES}</style>
</head>
<body>
<div class="card">
  <img src="{_LOGO_DATA_URI}" alt="Agent Red" width="200" height="49" class="logo" />
  <h1>Invalid or expired link</h1>
  <p class="subtitle">This password reset link is no longer valid. It may have expired or already been used.</p>
  <a href="/admin/standalone/_forgot-password" class="link">Request a new link</a>
</div>
</body>
</html>"""


def _render_login_html(csrf_token: str | None = None, error: str | None = None) -> str:
    """Render the login page HTML with a fresh CSRF token (SPEC-1690)."""
    if csrf_token is None:
        csrf_token = _generate_csrf_token()
    html = _STANDALONE_LOGIN_HTML.replace("{{csrf_token}}", csrf_token)
    if error:
        html = html.replace(
            "Incorrect password. Please try again.",
            error,
        ).replace(
            'class="error" id="err"',
            'class="error" id="err" style="display:block"',
        )
    return html


def _render_forgot_pw_html(csrf_token: str | None = None, error: str | None = None) -> str:
    """Render the forgot-password page HTML with a fresh CSRF token."""
    if csrf_token is None:
        csrf_token = _generate_csrf_token()
    html = _STANDALONE_FORGOT_PW_HTML.replace("{{csrf_token}}", csrf_token)
    if error:
        html = html.replace(
            "Please enter a valid email address.",
            error,
        ).replace(
            'class="error" id="err"',
            'class="error" id="err" style="display:block"',
        )
    return html


def _render_reset_pw_html(
    token: str,
    csrf_token: str | None = None,
    error: str | None = None,
) -> str:
    """Render the reset-password page HTML with CSRF token and reset token."""
    if csrf_token is None:
        csrf_token = _generate_csrf_token()
    html = _STANDALONE_RESET_PW_HTML.replace("{{token}}", token).replace(
        "{{csrf_token}}",
        csrf_token,
    )
    if error:
        html = html.replace(
            "Passwords do not match.",
            error,
        ).replace(
            'class="error" id="err"',
            'class="error" id="err" style="display:block"',
        )
    return html


def _generate_reset_token(ttl: int = 900) -> str:
    """Create an HMAC-signed reset token valid for *ttl* seconds.

    Format: ``<nonce>.<expiry_ts>.<hmac_hex>``
    Signed with ``_ADMIN_HMAC_KEY`` (immutable, derived from env var) so any
    replica can validate — even after an in-memory password change.
    """
    nonce = _secrets.token_urlsafe(16)
    expiry = str(int(_time.time() + ttl))
    payload = f"{nonce}.{expiry}"
    sig = _hmac.new(
        _ADMIN_HMAC_KEY.encode(),
        payload.encode(),
        "sha256",
    ).hexdigest()
    return f"{payload}.{sig}"


def _validate_reset_token(token: str) -> bool:
    """Validate an HMAC-signed reset token.

    Checks signature, expiry, and best-effort single-use nonce tracking.
    Uses ``_ADMIN_HMAC_KEY`` (immutable) so validation works on any replica.
    """
    if not token or not _ADMIN_HMAC_KEY:
        return False
    parts = token.split(".")
    if len(parts) != 3:
        return False
    nonce, expiry_str, sig = parts
    # Recompute HMAC
    payload = f"{nonce}.{expiry_str}"
    expected = _hmac.new(
        _ADMIN_HMAC_KEY.encode(),
        payload.encode(),
        "sha256",
    ).hexdigest()
    if not _hmac.compare_digest(sig, expected):
        return False
    # Check expiry
    try:
        if _time.time() > float(expiry_str):
            return False
    except ValueError:
        return False
    # Best-effort single-use check (per-replica)
    if nonce in _admin_used_reset_nonces:
        return False
    return True


def _send_admin_password_changed_email(to_email: str, forgot_password_url: str) -> bool:
    """Send a confirmation email after a successful password reset.

    Security best practice: notify the admin that their password was changed,
    and provide a self-service recovery link in case they did not initiate it.
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    smtp_host = os.environ.get("SMTP_HOST", "")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USERNAME", "")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    sender = os.environ.get("SMTP_FROM_ADDRESS", "noreply@agentred.com")

    if not smtp_host:
        logger.warning("SMTP_HOST not configured — cannot send password changed confirmation email")
        return False

    subject = "Your Agent Red Admin Password Has Been Reset"

    html_body = f"""\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/></head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:Inter,system-ui,sans-serif;">
<div style="max-width:560px;margin:40px auto;padding:40px;
background:#1f1f1f;border-radius:12px;border:1px solid #272727;">
  <div style="text-align:center;margin-bottom:24px;">
    <h1 style="margin:0;font-size:20px;color:#F5F5F5;">Agent Red</h1>
    <p style="margin:4px 0 0;font-size:14px;color:#A0A0A0;">Customer Experience</p>
  </div>
  <h2 style="margin:0 0 16px;font-size:16px;color:#F5F5F5;">Password Reset Successful</h2>
  <p style="margin:0 0 16px;font-size:14px;color:#E0E0E0;line-height:1.6;">
    Your admin password has been reset successfully. You are now signed in.
  </p>
  <hr style="border:none;border-top:1px solid #272727;margin:24px 0;" />
  <div style="background:#2a1a1a;border:1px solid #4a2020;border-radius:8px;padding:16px;margin:0 0 16px;">
    <p style="margin:0 0 8px;font-size:13px;color:#ff6b6b;font-weight:600;">
      Did not make this change?
    </p>
    <p style="margin:0 0 12px;font-size:13px;color:#A0A0A0;line-height:1.5;">
      If you did not reset your password, someone may have access to your account.
      Reset your password immediately to secure your account.
    </p>
    <a href="{forgot_password_url}"
      style="display:inline-block;padding:10px 24px;
      background:#ff3621;color:#ffffff;font-size:13px;
      font-weight:600;text-decoration:none;border-radius:6px;">
      Reset Password
    </a>
  </div>
  <hr style="border:none;border-top:1px solid #272727;margin:24px 0;" />
  <p style="margin:0;font-size:11px;color:#787878;text-align:center;">
    Agent Red Customer Experience &mdash; A product of Remaker Digital
  </p>
</div>
</body>
</html>"""

    plain_body = (
        f"Agent Red Admin Password Reset Successful\n\n"
        f"Your admin password has been reset successfully. You are now signed in.\n\n"
        f"If you did not reset your password, someone may have access to your account.\n"
        f"Reset your password immediately: {forgot_password_url}\n"
    )

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"Agent Red <{sender}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(plain_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10.0) as server:
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10.0) as server:
                server.ehlo()
                if smtp_port != 25:
                    server.starttls()
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)

        logger.info("Admin password changed confirmation email sent to %s", to_email)
        return True

    except Exception:
        logger.exception("Failed to send admin password changed confirmation email to %s", to_email)
        return False


def _send_admin_reset_email(to_email: str, reset_url: str) -> bool:
    """Send a password reset email via SMTP.

    Reuses the same SMTP env vars as admin_apikey_api.py.
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    smtp_host = os.environ.get("SMTP_HOST", "")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USERNAME", "")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    sender = os.environ.get("SMTP_FROM_ADDRESS", "noreply@agentred.com")

    if not smtp_host:
        logger.warning("SMTP_HOST not configured — cannot send password reset email")
        return False

    subject = "Reset Your Agent Red Admin Password"

    html_body = f"""\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/></head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:Inter,system-ui,sans-serif;">
<div style="max-width:560px;margin:40px auto;padding:40px;
background:#1f1f1f;border-radius:12px;border:1px solid #272727;">
  <div style="text-align:center;margin-bottom:24px;">
    <h1 style="margin:0;font-size:20px;color:#F5F5F5;">Agent Red</h1>
    <p style="margin:4px 0 0;font-size:14px;color:#A0A0A0;">Customer Experience</p>
  </div>
  <h2 style="margin:0 0 16px;font-size:16px;color:#F5F5F5;">Password Reset</h2>
  <p style="margin:0 0 16px;font-size:14px;color:#E0E0E0;line-height:1.6;">
    We received a request to reset the admin password. Click the button below to choose a new password.
  </p>
  <div style="text-align:center;margin:24px 0;">
    <a href="{reset_url}"
      style="display:inline-block;padding:12px 32px;
      background:#ff3621;color:#ffffff;font-size:14px;
      font-weight:600;text-decoration:none;border-radius:8px;">
      Reset Password
    </a>
  </div>
  <p style="margin:16px 0 0;font-size:13px;color:#A0A0A0;line-height:1.5;">
    This link expires in 15 minutes. If you did not request this, you can safely ignore this email.
  </p>
  <hr style="border:none;border-top:1px solid #272727;margin:24px 0;" />
  <p style="margin:0 0 8px;font-size:13px;color:#A0A0A0;line-height:1.5;">
    If the button doesn't work, copy and paste this link into your browser:
  </p>
  <p style="margin:0;font-family:'JetBrains Mono',monospace;font-size:11px;color:#787878;word-break:break-all;">
    {reset_url}
  </p>
  <hr style="border:none;border-top:1px solid #272727;margin:24px 0;" />
  <p style="margin:0;font-size:11px;color:#787878;text-align:center;">
    Agent Red Customer Experience &mdash; A product of Remaker Digital
  </p>
</div>
</body>
</html>"""

    plain_body = (
        f"Agent Red Admin Password Reset\n\n"
        f"We received a request to reset the admin password.\n\n"
        f"Click this link to choose a new password:\n{reset_url}\n\n"
        f"This link expires in 15 minutes.\n"
        f"If you did not request this, you can safely ignore this email.\n"
    )

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"Agent Red <{sender}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(plain_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10.0) as server:
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10.0) as server:
                server.ehlo()
                if smtp_port != 25:
                    server.starttls()
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)

        logger.info("Admin password reset email sent to %s", to_email)
        return True

    except Exception:
        logger.exception("Failed to send admin password reset email to %s", to_email)
        return False


# ---------------------------------------------------------------------------
# mount_standalone_admin() — called by main.py to register routes on the app
# ---------------------------------------------------------------------------


def mount_standalone_admin(app: FastAPI) -> None:
    """Mount the standalone admin SPA routes on the given FastAPI application.

    Registers password-gated routes for the merchant admin dashboard,
    including login, forgot-password, reset-password flows, and static
    file serving from the Vite build output.
    """
    if _admin_standalone_dist.is_dir():

        def _check_admin_cookie(request: Request) -> bool:
            """Return True if the request has a valid admin session cookie."""
            if not _admin_password_hash:
                # No password configured — allow all access
                return True
            cookie = request.cookies.get(_ADMIN_COOKIE_NAME, "")
            return _validate_session_token(cookie)

        @app.post("/admin/standalone/_auth", include_in_schema=False)
        async def _admin_standalone_auth(request: Request) -> StarletteResponse:
            """Validate the admin password and set a session cookie (SPEC-1688/1689/1690)."""
            form = await request.form()
            password = str(form.get("password", ""))
            form_csrf = str(form.get("csrf_token", ""))
            cookie_csrf = request.cookies.get(_CSRF_COOKIE_NAME, "")

            # CSRF validation (SPEC-1690)
            if not _validate_csrf_token(form_csrf, cookie_csrf):
                csrf = _generate_csrf_token()
                response = HTMLResponse(
                    content=_render_login_html(csrf_token=csrf, error="Invalid request. Please try again."),
                    status_code=403,
                    headers=_NO_CACHE_HEADERS,
                )
                response.set_cookie(_CSRF_COOKIE_NAME, csrf, httponly=True, secure=True, samesite="lax", max_age=3600)
                return response

            # Argon2id password verification (SPEC-1688)
            if _verify_password(password):
                token = _generate_session_token()
                response = StarletteResponse(
                    status_code=303,
                    headers={"location": "/admin/standalone/"},
                )
                response.set_cookie(
                    _ADMIN_COOKIE_NAME,
                    token,
                    httponly=True,
                    secure=True,
                    samesite="lax",
                    max_age=86400 * 7,  # 7 days
                )
                response.delete_cookie(_CSRF_COOKIE_NAME)
                return response

            # Wrong password — re-render login with fresh CSRF token
            csrf = _generate_csrf_token()
            response = HTMLResponse(
                content=_render_login_html(csrf_token=csrf),
                status_code=403,
                headers=_NO_CACHE_HEADERS,
            )
            response.set_cookie(_CSRF_COOKIE_NAME, csrf, httponly=True, secure=True, samesite="lax", max_age=3600)
            return response

        # ---- Forgot password flow (email-based reset) --------------------------

        @app.get("/admin/standalone/_forgot-password", include_in_schema=False)
        async def _admin_forgot_password_form(request: Request) -> StarletteResponse:
            """Show the forgot password form (enter email) with CSRF token."""
            csrf = _generate_csrf_token()
            response = HTMLResponse(content=_render_forgot_pw_html(csrf_token=csrf))
            response.set_cookie(_CSRF_COOKIE_NAME, csrf, httponly=True, secure=True, samesite="lax", max_age=3600)
            return response

        @app.post("/admin/standalone/_forgot-password", include_in_schema=False)
        async def _admin_forgot_password(request: Request) -> StarletteResponse:
            """Process forgot-password: validate CSRF + email, send reset link."""
            form = await request.form()
            email = str(form.get("email", "")).strip().lower()
            form_csrf = str(form.get("csrf_token", ""))
            cookie_csrf = request.cookies.get(_CSRF_COOKIE_NAME, "")

            # CSRF validation (SPEC-1690)
            if not _validate_csrf_token(form_csrf, cookie_csrf):
                csrf = _generate_csrf_token()
                response = HTMLResponse(
                    content=_render_forgot_pw_html(csrf_token=csrf, error="Invalid request. Please try again."),
                    status_code=403,
                )
                response.set_cookie(_CSRF_COOKIE_NAME, csrf, httponly=True, secure=True, samesite="lax", max_age=3600)
                return response

            # Rate limit: 3 requests per 5 min per IP (SPEC-1691: shared backend)
            from src.multi_tenant.security_hardening import get_rate_limit_backend

            client_ip = request.client.host if request.client else "unknown"
            if get_rate_limit_backend().is_limited(
                f"admin_reset:{client_ip}",
                max_requests=3,
                window_seconds=300,
            ):
                csrf = _generate_csrf_token()
                response = HTMLResponse(
                    content=_render_forgot_pw_html(
                        csrf_token=csrf,
                        error="Too many requests. Please wait a few minutes and try again.",
                    ),
                    status_code=429,
                )
                response.set_cookie(_CSRF_COOKIE_NAME, csrf, httponly=True, secure=True, samesite="lax", max_age=3600)
                return response

            # Validate email format
            if not email or "@" not in email:
                csrf = _generate_csrf_token()
                response = HTMLResponse(
                    content=_render_forgot_pw_html(csrf_token=csrf),
                    status_code=400,
                )
                response.set_cookie(_CSRF_COOKIE_NAME, csrf, httponly=True, secure=True, samesite="lax", max_age=3600)
                return response

            # Check if email matches the configured reset email
            if _ADMIN_RESET_EMAIL and email == _ADMIN_RESET_EMAIL:
                # Generate HMAC-signed token (any replica can validate)
                reset_token = _generate_reset_token(ttl=900)

                # Build reset URL
                scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
                host = request.headers.get("host", request.url.netloc)
                reset_url = f"{scheme}://{host}/admin/standalone/_reset-password?token={reset_token}"

                import asyncio

                await asyncio.to_thread(_send_admin_reset_email, email, reset_url)  # SPEC-1622: non-blocking SMTP

            # Always return success page (prevents email enumeration)
            return HTMLResponse(content=_STANDALONE_FORGOT_PW_SENT_HTML)

        @app.get("/admin/standalone/_reset-password", include_in_schema=False)
        async def _admin_reset_password_form(request: Request) -> StarletteResponse:
            """Show the set-new-password form if the token is valid (with CSRF)."""
            token = request.query_params.get("token", "")
            if not _validate_reset_token(token):
                return HTMLResponse(content=_STANDALONE_RESET_INVALID_HTML, status_code=400)
            csrf = _generate_csrf_token()
            response = HTMLResponse(content=_render_reset_pw_html(token=token, csrf_token=csrf))
            response.set_cookie(_CSRF_COOKIE_NAME, csrf, httponly=True, secure=True, samesite="lax", max_age=3600)
            return response

        @app.post("/admin/standalone/_reset-password", include_in_schema=False)
        async def _admin_reset_password(request: Request) -> StarletteResponse:
            """Process password reset: validate CSRF + token, auto-login (SPEC-1690/1691)."""

            form = await request.form()
            token = str(form.get("token", ""))
            new_pw = str(form.get("new_password", ""))
            confirm = str(form.get("confirm_password", ""))
            form_csrf = str(form.get("csrf_token", ""))
            cookie_csrf = request.cookies.get(_CSRF_COOKIE_NAME, "")

            # CSRF validation (SPEC-1690)
            if not _validate_csrf_token(form_csrf, cookie_csrf):
                return HTMLResponse(content=_STANDALONE_RESET_INVALID_HTML, status_code=400)

            # Validate token
            if not _validate_reset_token(token):
                return HTMLResponse(content=_STANDALONE_RESET_INVALID_HTML, status_code=400)

            # Validate passwords match
            if new_pw != confirm:
                csrf = _generate_csrf_token()
                response = HTMLResponse(
                    content=_render_reset_pw_html(token=token, csrf_token=csrf),
                    status_code=400,
                )
                response.set_cookie(_CSRF_COOKIE_NAME, csrf, httponly=True, secure=True, samesite="lax", max_age=3600)
                return response

            # Validate minimum length (SPEC-1691)
            if len(new_pw) < _MIN_PASSWORD_LENGTH:
                csrf = _generate_csrf_token()
                response = HTMLResponse(
                    content=_render_reset_pw_html(
                        token=token,
                        csrf_token=csrf,
                        error=f"Password must be at least {_MIN_PASSWORD_LENGTH} characters.",
                    ),
                    status_code=400,
                )
                response.set_cookie(_CSRF_COOKIE_NAME, csrf, httponly=True, secure=True, samesite="lax", max_age=3600)
                return response

            # Multi-replica safety: Do NOT change the password in-memory.
            # With minReplicas > 1, an in-memory password change only affects
            # THIS replica — the other replica(s) keep the env var password,
            # causing 50% login failures and cookie mismatches.
            #
            # Instead: auto-login the user by setting an opaque session token
            # (HMAC-signed, validated on any replica) and redirect to the admin
            # dashboard.  The user gets a 7-day authenticated session.
            #
            # To change the actual admin password, update the ADMIN_PREVIEW_PASSWORD
            # env var on the Container App (triggers rolling restart of all replicas).

            # Mark nonce as used (best-effort single-use per replica)
            nonce = token.split(".")[0] if "." in token else ""
            if nonce:
                _admin_used_reset_nonces.add(nonce)

            logger.info("Admin password reset: auto-login via session token")

            # Send password-changed confirmation email (non-blocking best-effort).
            # Includes a "Reset Password" recovery link in case the admin did not
            # initiate this change (security best practice, WI #203 UX review).
            if _ADMIN_RESET_EMAIL:
                scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
                host = request.headers.get("host", request.url.hostname or "localhost")
                forgot_url = f"{scheme}://{host}/admin/standalone/_forgot-password"
                import asyncio

                await asyncio.to_thread(
                    _send_admin_password_changed_email, _ADMIN_RESET_EMAIL, forgot_url
                )  # SPEC-1622: non-blocking SMTP

            # Auto-login: set opaque session token and redirect to admin dashboard.
            session_token = _generate_session_token()
            response = StarletteResponse(
                status_code=303,
                headers={"location": "/admin/standalone/"},
            )
            response.set_cookie(
                _ADMIN_COOKIE_NAME,
                session_token,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=86400 * 7,  # 7 days
            )
            response.delete_cookie(_CSRF_COOKIE_NAME)
            return response

        # IMPORTANT: Register explicit root routes BEFORE the StaticFiles mount.
        # Starlette evaluates routes in registration order; if the mount were first,
        # it could shadow the root path.  The assets mount only claims
        # /admin/standalone/assets/* and does NOT interfere with other sub-paths.

        # Cache-control headers for HTML pages: must revalidate on every load
        # so that new deployments with updated Vite hashed assets are picked up
        # immediately.  Hashed assets (/assets/*) are served by StaticFiles with
        # long-lived caching (content hash in filename = immutable).
        _NO_CACHE_HEADERS = {"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache"}

        @app.get("/admin/standalone/", include_in_schema=False)
        async def _admin_standalone_index_slash(request: Request) -> StarletteResponse:
            """Serve the standalone admin SPA root with trailing slash (password-gated)."""
            if not _check_admin_cookie(request):
                csrf = _generate_csrf_token()
                response = HTMLResponse(content=_render_login_html(csrf_token=csrf), headers=_NO_CACHE_HEADERS)
                response.set_cookie(_CSRF_COOKIE_NAME, csrf, httponly=True, secure=True, samesite="lax", max_age=3600)
                return response
            return FileResponse(str(_admin_standalone_dist / "index.html"), headers=_NO_CACHE_HEADERS)

        @app.get("/admin/standalone", include_in_schema=False)
        async def _admin_standalone_index(request: Request) -> StarletteResponse:
            """Serve the standalone admin SPA root (password-gated)."""
            if not _check_admin_cookie(request):
                csrf = _generate_csrf_token()
                response = HTMLResponse(content=_render_login_html(csrf_token=csrf), headers=_NO_CACHE_HEADERS)
                response.set_cookie(_CSRF_COOKIE_NAME, csrf, httponly=True, secure=True, samesite="lax", max_age=3600)
                return response
            return FileResponse(str(_admin_standalone_dist / "index.html"), headers=_NO_CACHE_HEADERS)

        # Serve static assets (JS, CSS, sourcemaps) from the Vite build output
        app.mount(
            "/admin/standalone/assets",
            StaticFiles(directory=str(_admin_standalone_dist / "assets")),
            name="admin-standalone-assets",
        )

        @app.get("/admin/standalone/{full_path:path}", include_in_schema=False)
        async def _admin_standalone_spa(request: Request, full_path: str) -> StarletteResponse:
            """Catch-all route for the standalone admin SPA (password-gated).

            If full_path matches a real file in dist/ (e.g. icon-master.svg),
            serve that file directly.  Otherwise fall through to index.html
            for SPA client-side routing.
            """
            if not _check_admin_cookie(request):
                csrf = _generate_csrf_token()
                response = HTMLResponse(content=_render_login_html(csrf_token=csrf), headers=_NO_CACHE_HEADERS)
                response.set_cookie(_CSRF_COOKIE_NAME, csrf, httponly=True, secure=True, samesite="lax", max_age=3600)
                return response
            # Serve real static files (SVG, PNG, etc.) from dist root
            candidate = _admin_standalone_dist / full_path
            if candidate.is_file() and ".." not in full_path:
                return FileResponse(str(candidate))
            return FileResponse(str(_admin_standalone_dist / "index.html"), headers=_NO_CACHE_HEADERS)

        logger.info(
            "Standalone admin SPA mounted at /admin/standalone%s",
            " (password-gated)" if _admin_password_hash else " (NO PASSWORD — open access)",
        )
    else:
        logger.warning(
            "Standalone admin SPA dist directory not found at %s — standalone admin will not be available",
            _admin_standalone_dist,
        )
