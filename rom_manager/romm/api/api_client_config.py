"""RomM Config + Setup resource mixin (CONCEPT:ROM-003)."""

from typing import Any

from rom_manager.romm.api.api_client_base import RommApiBase


class RommApiConfig(RommApiBase):
    # --- config -----------------------------------------------------------
    def get_config(self) -> Any:
        """Get the system configuration (exclusions, bindings, versions)."""
        return self._get("/api/config")

    def add_exclusion(self, **body: Any) -> Any:
        """Add a filesystem exclusion (by type/value)."""
        return self._post("/api/config/exclude", json=body)

    def delete_exclusion(self, exclusion_type: str, exclusion_value: str) -> Any:
        """Remove a filesystem exclusion."""
        return self._delete(f"/api/config/exclude/{exclusion_type}/{exclusion_value}")

    def add_platform_binding(self, **body: Any) -> Any:
        """Bind a filesystem slug to a platform."""
        return self._post("/api/config/system/platforms", json=body)

    def delete_platform_binding(self, fs_slug: str) -> Any:
        """Remove a platform binding by filesystem slug."""
        return self._delete(f"/api/config/system/platforms/{fs_slug}")

    def add_platform_version(self, **body: Any) -> Any:
        """Add a platform version mapping."""
        return self._post("/api/config/system/versions", json=body)

    def delete_platform_version(self, fs_slug: str) -> Any:
        """Remove a platform version mapping by filesystem slug."""
        return self._delete(f"/api/config/system/versions/{fs_slug}")

    # --- setup ------------------------------------------------------------
    def get_setup_library(self) -> Any:
        """Get library setup info (first-run wizard)."""
        return self._get("/api/setup/library")

    def create_setup_platforms(self, platforms: list[Any]) -> Any:
        """Create initial platforms during setup."""
        return self._post("/api/setup/platforms", json=platforms)
