"""RomM Collections resource mixin (CONCEPT:ROM-003).

Covers regular, smart, and virtual collections.
"""

from typing import Any

from rom_manager.romm.api.api_client_base import RommApiBase


class RommApiCollections(RommApiBase):
    # --- regular collections ---------------------------------------------
    def list_collections(self, updated_after: str | None = None) -> Any:
        """List collections."""
        return self._get("/api/collections", params={"updated_after": updated_after})

    def get_collection_identifiers(self) -> Any:
        """Get lightweight identifiers for all collections."""
        return self._get("/api/collections/identifiers")

    def get_collection(self, id: int) -> Any:
        """Get a single collection by id."""
        return self._get(f"/api/collections/{id}")

    def add_collection(
        self,
        data: dict | None = None,
        is_public: bool | None = None,
        is_favorite: bool | None = None,
    ) -> Any:
        """Create a collection (multipart form)."""
        return self._post(
            "/api/collections",
            params={"is_public": is_public, "is_favorite": is_favorite},
            data=data or {},
        )

    def update_collection(
        self,
        id: int,
        data: dict | None = None,
        remove_cover: bool | None = None,
        is_public: bool | None = None,
    ) -> Any:
        """Update a collection (multipart form)."""
        return self._put(
            f"/api/collections/{id}",
            params={"remove_cover": remove_cover, "is_public": is_public},
            data=data or {},
        )

    def delete_collection(self, id: int) -> Any:
        """Delete a collection by id."""
        return self._delete(f"/api/collections/{id}")

    # --- smart collections ------------------------------------------------
    def list_smart_collections(self, updated_after: str | None = None) -> Any:
        """List smart (rule-based) collections."""
        return self._get(
            "/api/collections/smart", params={"updated_after": updated_after}
        )

    def get_smart_collection_identifiers(self) -> Any:
        """Get lightweight identifiers for all smart collections."""
        return self._get("/api/collections/smart/identifiers")

    def get_smart_collection(self, id: int) -> Any:
        """Get a single smart collection by id."""
        return self._get(f"/api/collections/smart/{id}")

    def add_smart_collection(
        self, data: dict | None = None, is_public: bool | None = None
    ) -> Any:
        """Create a smart collection."""
        return self._post(
            "/api/collections/smart",
            params={"is_public": is_public},
            json=data or {},
        )

    def update_smart_collection(
        self, id: int, data: dict | None = None, is_public: bool | None = None
    ) -> Any:
        """Update a smart collection."""
        return self._put(
            f"/api/collections/smart/{id}",
            params={"is_public": is_public},
            json=data or {},
        )

    def delete_smart_collection(self, id: int) -> Any:
        """Delete a smart collection by id."""
        return self._delete(f"/api/collections/smart/{id}")

    # --- virtual collections ----------------------------------------------
    def list_virtual_collections(self, type: str, limit: int | None = None) -> Any:
        """List virtual collections of a given type (e.g. 'collection', 'franchise')."""
        return self._get(
            "/api/collections/virtual", params={"type": type, "limit": limit}
        )

    def get_virtual_collection_identifiers(self) -> Any:
        """Get lightweight identifiers for all virtual collections."""
        return self._get("/api/collections/virtual/identifiers")

    def get_virtual_collection(self, id: str) -> Any:
        """Get a single virtual collection by id."""
        return self._get(f"/api/collections/virtual/{id}")
