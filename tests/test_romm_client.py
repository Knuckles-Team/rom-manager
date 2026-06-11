"""RomM client transport/auth tests (CONCEPT:ROM-003).

All network is faked — the base client never touches the wire in these tests.
"""

import pytest

from rom_manager.romm.api import RommApi
from rom_manager.romm.api.api_client_base import RommApiBase


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, content=b"{}", headers=None):
        self.status_code = status_code
        self._json = json_data if json_data is not None else {}
        self.content = content
        self.headers = headers or {}

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise AssertionError(f"unexpected raise_for_status {self.status_code}")

    def iter_content(self, chunk_size=1):
        for i in range(0, len(self.content), chunk_size):
            yield self.content[i : i + chunk_size]


class FakeSession:
    """Returns queued responses in order; records every call."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def _next(self, method, url, **kw):
        self.calls.append({"method": method, "url": url, **kw})
        return self._responses.pop(0)

    def request(self, method, url, **kw):
        return self._next(method, url, **kw)

    def post(self, url, **kw):
        return self._next("POST", url, **kw)

    def get(self, url, **kw):
        return self._next("GET", url, **kw)


@pytest.mark.concept("ROM-003")
def test_basic_auth_header_no_network():
    client = RommApi(url="http://romm.test", username="u", password="p")
    assert client.auth_headers["Authorization"].startswith("Basic ")
    # Constructing a Basic client makes no HTTP call.
    assert client.url == "http://romm.test/api"


@pytest.mark.concept("ROM-003")
def test_missing_url_raises():
    from agent_utilities.core.exceptions import MissingParameterError

    with pytest.raises(MissingParameterError):
        RommApiBase(url=None)


@pytest.mark.concept("ROM-003")
def test_get_builds_correct_url_and_params():
    client = RommApi(url="http://romm.test", username="u", password="p")
    session = FakeSession([FakeResponse(json_data={"roms": []})])
    setattr(client, "_session", session)
    out = client.list_roms(platform_ids=7, limit=50, unused=None)
    assert out == {"roms": []}
    call = session.calls[0]
    assert call["method"] == "GET"
    assert call["url"] == "http://romm.test/api/roms"
    # None-valued params are stripped.
    assert call["params"] == {"platform_ids": 7, "limit": 50}


@pytest.mark.concept("ROM-003")
def test_post_json_body():
    client = RommApi(url="http://romm.test", username="u", password="p")
    session = FakeSession([FakeResponse(json_data={"id": 3})])
    setattr(client, "_session", session)
    out = client.delete_roms(roms=[1, 2])
    assert out == {"id": 3}
    call = session.calls[0]
    assert call["method"] == "POST"
    assert call["url"] == "http://romm.test/api/roms/delete"
    assert call["json"] == {"roms": [1, 2], "delete_from_fs": []}


@pytest.mark.concept("ROM-003")
def test_oauth_mint_and_refresh_on_401(monkeypatch):
    # Queue: token mint, a 401, a refresh mint, then the real 200 result.
    session = FakeSession(
        [
            FakeResponse(json_data={"access_token": "a1", "refresh_token": "r1"}),
            FakeResponse(status_code=401, content=b""),
            FakeResponse(json_data={"access_token": "a2", "refresh_token": "r2"}),
            FakeResponse(json_data={"ok": True}),
        ]
    )
    monkeypatch.setattr(
        "rom_manager.romm.api.api_client_base.requests.Session", lambda: session
    )
    client = RommApi(
        url="http://romm.test", username="u", password="p", auth_mode="oauth"
    )
    assert client.token == "a1"
    out = client.stats()
    assert out == {"ok": True}
    # Token was refreshed after the 401 and the call retried.
    assert client.token == "a2"
    assert client.auth_headers["Authorization"] == "Bearer a2"


@pytest.mark.concept("ROM-003")
def test_unauthorized_maps_to_exception():
    from agent_utilities.core.exceptions import UnauthorizedError

    client = RommApi(url="http://romm.test", username="u", password="p")
    setattr(client, "_session", FakeSession([FakeResponse(status_code=403, content=b"")]))
    with pytest.raises(UnauthorizedError):
        client.list_platforms()
