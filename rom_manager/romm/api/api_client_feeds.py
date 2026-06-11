"""RomM Feeds resource mixin (CONCEPT:ROM-003).

Integration feeds for external frontends (WebRcade, Tinfoil, PKGi, PKGj, fpkgi,
Kekatsu). Each returns the feed document as JSON (or text when not JSON).
"""

from typing import Any

from rom_manager.romm.api.api_client_base import RommApiBase


class RommApiFeeds(RommApiBase):
    def webrcade_feed(self) -> Any:
        """WebRcade platforms feed."""
        return self._get("/api/feeds/webrcade")

    def tinfoil_feed(self, slug: str | None = None) -> Any:
        """Tinfoil index feed (Nintendo Switch)."""
        return self._get("/api/feeds/tinfoil", params={"slug": slug})

    def fpkgi_feed(self, platform_slug: str) -> Any:
        """fpkgi feed for a platform slug (PS4)."""
        return self._get(f"/api/feeds/fpkgi/{platform_slug}")

    def kekatsu_feed(self, platform_slug: str) -> Any:
        """Kekatsu DS feed for a platform slug."""
        return self._get(f"/api/feeds/kekatsu/{platform_slug}")

    def pkgi_ps3_feed(self, content_type: str) -> Any:
        """PKGi PS3 feed for a content type (e.g. 'games', 'dlc')."""
        return self._get(f"/api/feeds/pkgi/ps3/{content_type}")

    def pkgi_psp_feed(self, content_type: str) -> Any:
        """PKGi PSP feed for a content type."""
        return self._get(f"/api/feeds/pkgi/psp/{content_type}")

    def pkgi_psvita_feed(self, content_type: str) -> Any:
        """PKGi PS Vita feed for a content type."""
        return self._get(f"/api/feeds/pkgi/psvita/{content_type}")

    def pkgj_psp_dlc_feed(self) -> Any:
        """PKGj PSP DLC feed."""
        return self._get("/api/feeds/pkgj/psp/dlc")

    def pkgj_psp_games_feed(self) -> Any:
        """PKGj PSP games feed."""
        return self._get("/api/feeds/pkgj/psp/games")

    def pkgj_psvita_dlc_feed(self) -> Any:
        """PKGj PS Vita DLC feed."""
        return self._get("/api/feeds/pkgj/psvita/dlc")

    def pkgj_psvita_games_feed(self) -> Any:
        """PKGj PS Vita games feed."""
        return self._get("/api/feeds/pkgj/psvita/games")

    def pkgj_psx_games_feed(self) -> Any:
        """PKGj PSX games feed."""
        return self._get("/api/feeds/pkgj/psx/games")
