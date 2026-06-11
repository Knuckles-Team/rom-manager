"""RomM System/auth/misc resource mixin (CONCEPT:ROM-003).

Heartbeat, stats, netplay, gamelist export, raw-asset streaming, session
login/logout, OAuth token, OpenID, and password-reset endpoints.
"""

from typing import Any

from rom_manager.romm.api.api_client_base import RommApiBase


class RommApiSystem(RommApiBase):
    # --- health / stats ---------------------------------------------------
    def heartbeat(self) -> Any:
        """Get the server heartbeat (public)."""
        return self._get("/api/heartbeat")

    def metadata_heartbeat(self, source: str) -> Any:
        """Get the heartbeat for a metadata source (igdb, moby, ss, ...)."""
        return self._get(f"/api/heartbeat/metadata/{source}")

    def stats(self) -> Any:
        """Get system statistics (counts, filesystem size, ...)."""
        return self._get("/api/stats")

    def list_netplay_rooms(self, game_id: str) -> Any:
        """List active netplay rooms for a game."""
        return self._get("/api/netplay/list", params={"game_id": game_id})

    def export_gamelist(
        self, platform_ids: list[int], local_export: bool | None = None
    ) -> Any:
        """Export an EmulationStation-style gamelist for platforms."""
        return self._post(
            "/api/gamelist/export",
            params={"platform_ids": platform_ids, "local_export": local_export},
        )

    # --- raw assets / romfile content ------------------------------------
    def get_raw_asset(self, path: str, dest: str) -> Any:
        """Download a raw asset by path, streamed to ``dest``."""
        resp = self._get(f"/api/raw/assets/{path}", stream=True)
        return self._stream_to_path(resp, dest)

    def head_raw_asset(self, path: str) -> Any:
        """HEAD a raw asset (size/existence) without downloading."""
        resp = self._head(f"/api/raw/assets/{path}")
        return {"status_code": resp.status_code, "headers": dict(resp.headers)}

    def get_romfile_content(self, id: int, file_name: str, dest: str) -> Any:
        """Download a ROM file's content by id, streamed to ``dest``."""
        resp = self._get(f"/api/romsfiles/{id}/content/{file_name}", stream=True)
        return self._stream_to_path(resp, dest)

    # --- auth / session ---------------------------------------------------
    def login(self, **body: Any) -> Any:
        """Create a session using the configured credentials."""
        return self._post("/api/login", json=body or None)

    def login_via_openid(self) -> Any:
        """Begin the OpenID login flow (returns a redirect document)."""
        return self._get("/api/login/openid")

    def logout(self) -> Any:
        """Invalidate the current session."""
        return self._post("/api/logout")

    def create_token(
        self, username: str, password: str, scopes: str | None = None
    ) -> Any:
        """Mint an OAuth2 access/refresh token pair (password grant)."""
        data = {"grant_type": "password", "username": username, "password": password}
        if scopes:
            data["scope"] = scopes
        return self._post("/api/token", data=data)

    def oauth_openid(self) -> Any:
        """Complete the OpenID OAuth callback."""
        return self._get("/api/oauth/openid")

    def forgot_password(self, **body: Any) -> Any:
        """Request a password reset email."""
        return self._post("/api/forgot-password", json=body)

    def reset_password(self, **body: Any) -> Any:
        """Reset a password using a reset token."""
        return self._post("/api/reset-password", json=body)
