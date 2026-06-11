"""RomM Devices resource mixin (CONCEPT:ROM-003)."""

from typing import Any

from rom_manager.romm.api.api_client_base import RommApiBase


class RommApiDevices(RommApiBase):
    def list_devices(self) -> Any:
        """List registered devices."""
        return self._get("/api/devices")

    def get_device(self, device_id: int) -> Any:
        """Get a single device by id."""
        return self._get(f"/api/devices/{device_id}")

    def register_device(self, **body: Any) -> Any:
        """Register a new device."""
        return self._post("/api/devices", json=body)

    def update_device(self, device_id: int, **body: Any) -> Any:
        """Update a registered device."""
        return self._put(f"/api/devices/{device_id}", json=body)

    def delete_device(self, device_id: int) -> Any:
        """Delete a device by id."""
        return self._delete(f"/api/devices/{device_id}")
