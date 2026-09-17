"""Credential-free client for the configured GT-KB authority endpoint."""

from __future__ import annotations

import time
from http.client import HTTPMessage
from typing import IO, Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from groundtruth_kb.config import validate_authority_url
from groundtruth_kb.postgres_kernel import canonical_json_bytes, parse_json_bytes


class AuthorityClientError(Exception):
    def __init__(self, code: str, message: str, *, details: object = None) -> None:
        super().__init__(message)
        self.code = code
        self.details = details


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(
        self, req: Request, fp: IO[bytes], code: int, msg: str, headers: HTTPMessage, newurl: str
    ) -> None:
        return None


class AuthorityClient:
    """A failed request never falls back to a local database or retries a write."""

    def __init__(self, url: str, *, timeout: float = 40) -> None:
        self.url = validate_authority_url(url)
        self.timeout = timeout
        self._opener = build_opener(ProxyHandler({}), _NoRedirect())

    def request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
    ) -> Any:
        if not path.startswith("/v1/") or "?" in path or "#" in path:
            raise AuthorityClientError("invalid_path", "A typed authority path is required")
        endpoint = self.url + path
        if query:
            endpoint += "?" + urlencode({key: value for key, value in query.items() if value is not None})
        request = Request(
            endpoint,
            method=method,
            data=canonical_json_bytes(body) if body is not None else None,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
        started = time.monotonic()
        try:
            with self._opener.open(request, timeout=self.timeout) as response:
                payload = response.read()
        except HTTPError as error:
            try:
                result = parse_json_bytes(error.read())
                if not isinstance(result, dict):
                    raise ValueError("not an error object")
                result = result.get("error", result)
                if not isinstance(result, dict):
                    raise ValueError("not an error object")
                code = result.get("code", "authority_error")
                message = result.get("message", "Authority refused this operation")
                if not isinstance(code, str) or not isinstance(message, str):
                    raise ValueError("invalid error fields")
            except Exception:  # intentional-catch: an unreadable error body collapses to the HTTP status
                raise AuthorityClientError("authority_error", f"Authority returned HTTP {error.code}") from error
            raise AuthorityClientError(
                code,
                message,
                details=result.get("details"),
            ) from error
        except (URLError, OSError, TimeoutError) as error:
            # Name the cause and the timing so a refusal can be explained afterwards
            # (a refused socket differs from an expired timeout); no retry, no
            # widened timeout.
            reason = getattr(error, "reason", None)
            raise AuthorityClientError(
                "authority_unavailable",
                "The configured authority is unavailable. Restore the service and read current state before retrying.",
                details={
                    "cause": type(reason if isinstance(reason, BaseException) else error).__name__,
                    "cause_message": str(reason if reason is not None else error)[:200],
                    "elapsed_seconds": round(time.monotonic() - started, 3),
                    "timeout_seconds": self.timeout,
                    "method": method,
                    "path": path,
                },
            ) from error
        try:
            return parse_json_bytes(payload)
        except Exception as error:  # intentional-catch: malformed canonical JSON is reported as invalid_response
            raise AuthorityClientError("invalid_response", "Authority returned invalid canonical JSON") from error
