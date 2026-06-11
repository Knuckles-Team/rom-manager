"""RomM States (emulator save-states) resource mixin (CONCEPT:ROM-003)."""

from typing import Any

from rom_manager.romm.api.api_client_base import RommApiBase


class RommApiStates(RommApiBase):
    def list_states(
        self, rom_id: int | None = None, platform_id: int | None = None
    ) -> Any:
        """List emulator save-states, optionally scoped to a ROM/platform."""
        return self._get(
            "/api/states", params={"rom_id": rom_id, "platform_id": platform_id}
        )

    def get_state_identifiers(self) -> Any:
        """Get lightweight identifiers for all states."""
        return self._get("/api/states/identifiers")

    def get_state(self, id: int) -> Any:
        """Get a single state by id."""
        return self._get(f"/api/states/{id}")

    def add_state(
        self, rom_id: int, file_path: str, emulator: str | None = None
    ) -> Any:
        """Upload an emulator save-state for a ROM (multipart)."""
        with open(file_path, "rb") as fh:
            return self._post(
                "/api/states",
                params={"rom_id": rom_id, "emulator": emulator},
                files={"stateFile": fh},
            )

    def update_state(self, id: int, **body: Any) -> Any:
        """Update a state's metadata."""
        return self._put(f"/api/states/{id}", json=body or None)

    def delete_states(self, states: list[int]) -> Any:
        """Delete one or more states by id."""
        return self._post("/api/states/delete", json={"states": states})
