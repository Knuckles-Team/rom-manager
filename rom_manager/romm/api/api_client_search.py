"""RomM Search resource mixin (CONCEPT:ROM-003)."""

from typing import Any

from rom_manager.romm.api.api_client_base import RommApiBase


class RommApiSearch(RommApiBase):
    def search_roms(
        self, rom_id: int, search_term: str | None = None, search_by: str | None = None
    ) -> Any:
        """Search metadata providers for matches to a ROM."""
        return self._get(
            "/api/search/roms",
            params={
                "rom_id": rom_id,
                "search_term": search_term,
                "search_by": search_by,
            },
        )

    def search_cover(self, search_term: str | None = None) -> Any:
        """Search metadata providers for cover art."""
        return self._get("/api/search/cover", params={"search_term": search_term})
