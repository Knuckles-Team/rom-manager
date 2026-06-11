"""RomM Firmware resource mixin (CONCEPT:ROM-003)."""

from typing import Any

from rom_manager.romm.api.api_client_base import RommApiBase


class RommApiFirmware(RommApiBase):
    def list_firmware(self, platform_id: int | None = None) -> Any:
        """List firmware, optionally scoped to a platform."""
        return self._get("/api/firmware", params={"platform_id": platform_id})

    def get_firmware_identifiers(self) -> Any:
        """Get lightweight identifiers for all firmware."""
        return self._get("/api/firmware/identifiers")

    def get_firmware(self, id: int) -> Any:
        """Get a single firmware record by id."""
        return self._get(f"/api/firmware/{id}")

    def add_firmware(self, platform_id: int, file_path: str) -> Any:
        """Upload a firmware file for a platform (multipart)."""
        with open(file_path, "rb") as fh:
            return self._post(
                "/api/firmware",
                params={"platform_id": platform_id},
                files={"files": fh},
            )

    def delete_firmware(
        self, firmware: list[int], delete_from_fs: list[int] | None = None
    ) -> Any:
        """Delete one or more firmware records (optionally from the filesystem too)."""
        return self._post(
            "/api/firmware/delete",
            json={"firmware": firmware, "delete_from_fs": delete_from_fs or []},
        )

    def get_firmware_content(self, id: int, file_name: str, dest: str) -> Any:
        """Download a firmware file, streamed to ``dest``."""
        resp = self._get(f"/api/firmware/{id}/content/{file_name}", stream=True)
        return self._stream_to_path(resp, dest)

    def head_firmware_content(self, id: int, file_name: str) -> Any:
        """HEAD a firmware file (size/existence) without downloading."""
        resp = self._head(f"/api/firmware/{id}/content/{file_name}")
        return {"status_code": resp.status_code, "headers": dict(resp.headers)}
