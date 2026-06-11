"""RomM Saves resource mixin (CONCEPT:ROM-003)."""

from typing import Any

from rom_manager.romm.api.api_client_base import RommApiBase


class RommApiSaves(RommApiBase):
    def list_saves(
        self,
        rom_id: int | None = None,
        platform_id: int | None = None,
        device_id: int | None = None,
        slot: int | None = None,
    ) -> Any:
        """List save files, optionally scoped to a ROM/platform/device/slot."""
        return self._get(
            "/api/saves",
            params={
                "rom_id": rom_id,
                "platform_id": platform_id,
                "device_id": device_id,
                "slot": slot,
            },
        )

    def get_save_identifiers(self) -> Any:
        """Get lightweight identifiers for all saves."""
        return self._get("/api/saves/identifiers")

    def get_saves_summary(self, rom_id: int) -> Any:
        """Get a per-ROM saves summary."""
        return self._get("/api/saves/summary", params={"rom_id": rom_id})

    def get_save(self, id: int, device_id: int | None = None) -> Any:
        """Get a single save by id."""
        return self._get(f"/api/saves/{id}", params={"device_id": device_id})

    def add_save(
        self,
        rom_id: int,
        file_path: str,
        emulator: str | None = None,
        slot: int | None = None,
        device_id: int | None = None,
        overwrite: bool | None = None,
        autocleanup: bool | None = None,
        autocleanup_limit: int | None = None,
    ) -> Any:
        """Upload a save file for a ROM (multipart)."""
        with open(file_path, "rb") as fh:
            return self._post(
                "/api/saves",
                params={
                    "rom_id": rom_id,
                    "emulator": emulator,
                    "slot": slot,
                    "device_id": device_id,
                    "overwrite": overwrite,
                    "autocleanup": autocleanup,
                    "autocleanup_limit": autocleanup_limit,
                },
                files={"saveFile": fh},
            )

    def update_save(self, id: int, **body: Any) -> Any:
        """Update a save's metadata."""
        return self._put(f"/api/saves/{id}", json=body or None)

    def delete_saves(self, saves: list[int]) -> Any:
        """Delete one or more saves by id."""
        return self._post("/api/saves/delete", json={"saves": saves})

    def download_save(
        self,
        id: int,
        dest: str,
        device_id: int | None = None,
        optimistic: bool | None = None,
    ) -> Any:
        """Download a save file, streamed to ``dest``."""
        resp = self._get(
            f"/api/saves/{id}/content",
            params={"device_id": device_id, "optimistic": optimistic},
            stream=True,
        )
        return self._stream_to_path(resp, dest)

    def confirm_save_download(self, id: int, **body: Any) -> Any:
        """Confirm a save was downloaded by a device."""
        return self._post(f"/api/saves/{id}/downloaded", json=body or {})

    def track_save(self, id: int, **body: Any) -> Any:
        """Mark a save as tracked for a device."""
        return self._post(f"/api/saves/{id}/track", json=body or {})

    def untrack_save(self, id: int, **body: Any) -> Any:
        """Stop tracking a save for a device."""
        return self._post(f"/api/saves/{id}/untrack", json=body or {})
