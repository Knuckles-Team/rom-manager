"""RomM Screenshots resource mixin (CONCEPT:ROM-003)."""

from typing import Any

from rom_manager.romm.api.api_client_base import RommApiBase


class RommApiScreenshots(RommApiBase):
    def add_screenshot(self, rom_id: int, file_path: str) -> Any:
        """Upload a screenshot for a ROM (multipart)."""
        with open(file_path, "rb") as fh:
            return self._post(
                "/api/screenshots",
                params={"rom_id": rom_id},
                files={"screenshotFile": fh},
            )
