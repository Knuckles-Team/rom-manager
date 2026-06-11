"""RomM Users resource mixin (CONCEPT:ROM-003)."""

from typing import Any

from rom_manager.romm.api.api_client_base import RommApiBase


class RommApiUsers(RommApiBase):
    def list_users(self) -> Any:
        """List all users (admin)."""
        return self._get("/api/users")

    def get_user_identifiers(self) -> Any:
        """Get lightweight identifiers for all users."""
        return self._get("/api/users/identifiers")

    def get_current_user(self) -> Any:
        """Get the authenticated user's profile."""
        return self._get("/api/users/me")

    def get_user(self, id: int) -> Any:
        """Get a single user by id."""
        return self._get(f"/api/users/{id}")

    def add_user(self, **body: Any) -> Any:
        """Create a new user (admin)."""
        return self._post("/api/users", json=body)

    def update_user(self, id: int, data: dict | None = None) -> Any:
        """Update a user (form-encoded)."""
        return self._put(f"/api/users/{id}", data=data or {})

    def delete_user(self, id: int) -> Any:
        """Delete a user by id (admin)."""
        return self._delete(f"/api/users/{id}")

    def create_invite_link(self, role: str) -> Any:
        """Create an invite link for a given role (admin)."""
        return self._post("/api/users/invite-link", params={"role": role})

    def register_user_from_invite(self, **body: Any) -> Any:
        """Register a new user from an invite token."""
        return self._post("/api/users/register", json=body)

    def refresh_retro_achievements(self, id: int, **body: Any) -> Any:
        """Refresh a user's RetroAchievements data."""
        return self._post(f"/api/users/{id}/ra/refresh", json=body or {})
