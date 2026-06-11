"""RomM Platforms resource mixin (CONCEPT:ROM-003)."""

from typing import Any

from rom_manager.romm.api.api_client_base import RommApiBase


class RommApiPlatforms(RommApiBase):
    def list_platforms(self, updated_after: str | None = None) -> Any:
        """List configured platforms."""
        return self._get("/api/platforms", params={"updated_after": updated_after})

    def get_supported_platforms(self) -> Any:
        """List all platforms RomM knows how to support."""
        return self._get("/api/platforms/supported")

    def get_platform_identifiers(self) -> Any:
        """Get lightweight identifiers for all platforms."""
        return self._get("/api/platforms/identifiers")

    def get_platform(self, id: int) -> Any:
        """Get a single platform by id."""
        return self._get(f"/api/platforms/{id}")

    def add_platform(self, **body: Any) -> Any:
        """Create a new platform."""
        return self._post("/api/platforms", json=body)

    def update_platform(self, id: int, **body: Any) -> Any:
        """Update an existing platform."""
        return self._put(f"/api/platforms/{id}", json=body)

    def delete_platform(self, id: int) -> Any:
        """Delete a platform by id."""
        return self._delete(f"/api/platforms/{id}")
