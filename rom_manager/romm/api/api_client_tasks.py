"""RomM Tasks resource mixin (CONCEPT:ROM-003)."""

from typing import Any

from rom_manager.romm.api.api_client_base import RommApiBase


class RommApiTasks(RommApiBase):
    def list_tasks(self) -> Any:
        """List the available background tasks."""
        return self._get("/api/tasks")

    def get_tasks_status(self) -> Any:
        """Get the status of all background tasks."""
        return self._get("/api/tasks/status")

    def get_task(self, task_id: str) -> Any:
        """Get a single task run by id."""
        return self._get(f"/api/tasks/{task_id}")

    def run_all_tasks(self) -> Any:
        """Trigger a run of all scheduled tasks."""
        return self._post("/api/tasks/run")

    def run_task(self, task_name: str) -> Any:
        """Trigger a run of a single named task (e.g. 'scan')."""
        return self._post(f"/api/tasks/run/{task_name}")
