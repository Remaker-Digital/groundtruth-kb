"""Credential-free client for the configured GT-KB authority endpoint."""

from __future__ import annotations

from typing import Any
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
    def redirect_request(self, req, fp, code, msg, headers, newurl):
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
        try:
            with self._opener.open(request, timeout=self.timeout) as response:
                payload = response.read()
        except HTTPError as error:
            try:
                result = parse_json_bytes(error.read())
                if not isinstance(result, dict):
                    raise ValueError("not an error object")
                result = result.get("error", result)
            except Exception:  # intentional-catch: an unreadable error body collapses to the HTTP status
                raise AuthorityClientError("authority_error", f"Authority returned HTTP {error.code}") from error
            raise AuthorityClientError(
                result.get("code", "authority_error"),
                result.get("message", "Authority refused this operation"),
                details=result.get("details"),
            ) from error
        except (URLError, OSError, TimeoutError) as error:
            raise AuthorityClientError(
                "authority_unavailable",
                "The configured authority is unavailable. Restore the service and read current state before retrying.",
            ) from error
        try:
            return parse_json_bytes(payload)
        except Exception as error:  # intentional-catch: malformed canonical JSON is reported as invalid_response
            raise AuthorityClientError("invalid_response", "Authority returned invalid canonical JSON") from error
