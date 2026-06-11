"""RomM REST API base client.

CONCEPT:ROM-003 — RomM (https://romm.app) remote-library integration. This is the
session/auth/transport layer shared by every resource mixin. It mirrors the house
pattern (``servicenow-api``) — a ``requests.Session`` with header-based auth and a
small set of verb helpers — but is deliberately network-free at construction so the
mixins stay unit-testable.

Authentication (RomM supports both):
- **Basic** — ``Authorization: Basic base64(username:password)`` (default; no expiry).
- **OAuth2 password grant** — ``POST /api/token`` mints a 15-minute ``access_token``
  and a 2-week ``refresh_token``; a 401 triggers a single transparent refresh+retry.
- **Bearer token** — a pre-minted ``access_token`` passed directly.
"""

from base64 import b64encode
from typing import Any

import requests
import urllib3
from agent_utilities.base_utilities import get_logger
from agent_utilities.core.exceptions import (
    AuthError,
    MissingParameterError,
    UnauthorizedError,
)

logger = get_logger(__name__)

# Full read+write scope set RomM advertises; requested when minting OAuth tokens so
# the access token is not narrower than the user's role allows.
DEFAULT_SCOPES = (
    "me.read me.write roms.read roms.write roms.user.read roms.user.write "
    "platforms.read platforms.write assets.read assets.write firmware.read "
    "firmware.write collections.read collections.write users.read users.write "
    "tasks.run"
)


class RommApiBase:
    """Session + auth + verb helpers for the RomM API (CONCEPT:ROM-003)."""

    def __init__(
        self,
        url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
        scopes: str | None = None,
        auth_mode: str | None = "basic",
        verify: bool = True,
        proxies: dict | None = None,
        timeout: int = 60,
    ) -> None:
        """Configure the client; no network call is made here (CONCEPT:ROM-003)."""
        if not url:
            raise MissingParameterError
        self.base_url = url.rstrip("/")
        self.url = f"{self.base_url}/api"
        self.username = username
        self.password = password
        self.auth_mode = (auth_mode or "basic").lower()
        self.scopes = scopes if scopes is not None else DEFAULT_SCOPES
        self.verify = verify
        self.proxies = proxies
        self.timeout = timeout
        self.token = token
        self.refresh_token: str | None = None
        self._session = requests.Session()

        if verify is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if token:
            self.auth_mode = "oauth"
            self.auth_headers = {"Authorization": f"Bearer {token}"}
        elif self.auth_mode == "oauth" and username and password:
            self._mint_token()
        elif username and password:
            user_pass = b64encode(f"{username}:{password}".encode()).decode()
            self.auth_headers = {"Authorization": f"Basic {user_pass}"}
        else:
            raise MissingParameterError

    # --- auth -------------------------------------------------------------
    def _mint_token(self) -> None:
        """Exchange username/password for an OAuth access/refresh token pair."""
        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }
        if self.scopes:
            data["scope"] = self.scopes
        resp = self._session.post(
            url=f"{self.url}/token",
            data=data,
            verify=self.verify,
            proxies=self.proxies,
            timeout=self.timeout,
        )
        if resp.status_code in (401, 403):
            raise AuthError
        resp.raise_for_status()
        payload = resp.json()
        self.token = payload["access_token"]
        self.refresh_token = payload.get("refresh_token")
        self.auth_headers = {"Authorization": f"Bearer {self.token}"}

    def _refresh(self) -> None:
        """Mint a fresh access token from the stored refresh token."""
        if not self.refresh_token:
            self._mint_token()
            return
        resp = self._session.post(
            url=f"{self.url}/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            },
            verify=self.verify,
            proxies=self.proxies,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        payload = resp.json()
        self.token = payload["access_token"]
        self.refresh_token = payload.get("refresh_token", self.refresh_token)
        self.auth_headers = {"Authorization": f"Bearer {self.token}"}

    # --- transport --------------------------------------------------------
    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json: Any = None,
        data: Any = None,
        files: Any = None,
        headers: dict | None = None,
        stream: bool = False,
        raw: bool = False,
        _retried: bool = False,
    ) -> Any:
        """Issue an authed request and return parsed JSON (or the raw response).

        ``params`` with ``None`` values are dropped. On a 401 under OAuth, the
        token is refreshed once and the call retried. ``raw=True`` (or
        ``stream=True``) returns the :class:`requests.Response` untouched — used
        for binary download/content endpoints.
        """
        if params:
            params = {k: v for k, v in params.items() if v is not None}
        req_headers = dict(self.auth_headers)
        if headers:
            req_headers.update(headers)
        resp = self._session.request(
            method=method.upper(),
            url=f"{self.base_url}{path}",
            params=params,
            json=json,
            data=data,
            files=files,
            headers=req_headers,
            verify=self.verify,
            proxies=self.proxies,
            stream=stream,
            timeout=self.timeout,
        )
        if (
            resp.status_code == 401
            and self.auth_mode == "oauth"
            and not _retried
            and (self.refresh_token or (self.username and self.password))
        ):
            self._refresh()
            return self._request(
                method,
                path,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=headers,
                stream=stream,
                raw=raw,
                _retried=True,
            )
        if resp.status_code == 401:
            raise AuthError
        if resp.status_code == 403:
            raise UnauthorizedError
        resp.raise_for_status()
        if raw or stream:
            return resp
        if not resp.content:
            return {"status_code": resp.status_code}
        try:
            return resp.json()
        except ValueError:
            return {"status_code": resp.status_code, "text": resp.text}

    def _get(self, path: str, **kw: Any) -> Any:
        return self._request("GET", path, **kw)

    def _post(self, path: str, **kw: Any) -> Any:
        return self._request("POST", path, **kw)

    def _put(self, path: str, **kw: Any) -> Any:
        return self._request("PUT", path, **kw)

    def _delete(self, path: str, **kw: Any) -> Any:
        return self._request("DELETE", path, **kw)

    def _head(self, path: str, **kw: Any) -> Any:
        return self._request("HEAD", path, raw=True, **kw)

    @staticmethod
    def _stream_to_path(resp: requests.Response, dest: str) -> dict[str, Any]:
        """Write a streamed binary response to ``dest`` and report bytes written."""
        written = 0
        with open(dest, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=1 << 16):
                if chunk:
                    fh.write(chunk)
                    written += len(chunk)
        return {"path": dest, "bytes": written, "status_code": resp.status_code}
