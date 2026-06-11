"""RomM ROMs resource mixin (CONCEPT:ROM-003).

Full CRUD plus search-by-hash/metadata-provider, downloads, file content,
manuals, and per-ROM notes/user-properties.
"""

from typing import Any

from rom_manager.romm.api.api_client_base import RommApiBase


class RommApiRoms(RommApiBase):
    def list_roms(self, **filters: Any) -> Any:
        """List ROMs with search/filter/sort/pagination query params.

        Accepts any ``GET /api/roms`` query param verbatim, e.g. ``search_term``,
        ``platform_ids``, ``collection_id``, ``favorite``, ``order_by``,
        ``order_dir``, ``limit``, ``offset``.
        """
        return self._get("/api/roms", params=filters)

    def get_rom(self, id: int) -> Any:
        """Get a single ROM by id."""
        return self._get(f"/api/roms/{id}")

    def get_rom_by_hash(
        self,
        crc_hash: str | None = None,
        md5_hash: str | None = None,
        sha1_hash: str | None = None,
        ra_hash: str | None = None,
    ) -> Any:
        """Look up a ROM by CRC/MD5/SHA1/RetroAchievements hash."""
        return self._get(
            "/api/roms/by-hash",
            params={
                "crc_hash": crc_hash,
                "md5_hash": md5_hash,
                "sha1_hash": sha1_hash,
                "ra_hash": ra_hash,
            },
        )

    def get_rom_by_metadata_provider(self, **provider_ids: Any) -> Any:
        """Look up a ROM by an external provider id (igdb_id, moby_id, ss_id, ...)."""
        return self._get("/api/roms/by-metadata-provider", params=provider_ids)

    def get_rom_filters(self) -> Any:
        """Get the available filter values for the ROM collection."""
        return self._get("/api/roms/filters")

    def get_rom_identifiers(self) -> Any:
        """Get lightweight identifiers for all ROMs."""
        return self._get("/api/roms/identifiers")

    def get_romfile(self, id: int) -> Any:
        """Get metadata for a single ROM file by id."""
        return self._get(f"/api/roms/files/{id}")

    def add_rom(self, platform: str, filename: str, file_path: str) -> Any:
        """Upload a new ROM file to a platform (streamed raw upload)."""
        with open(file_path, "rb") as fh:
            return self._post(
                "/api/roms",
                data=fh,
                headers={
                    "x-upload-platform": str(platform),
                    "x-upload-filename": filename,
                },
            )

    def update_rom(
        self,
        id: int,
        data: dict | None = None,
        remove_cover: bool | None = None,
        unmatch_metadata: bool | None = None,
    ) -> Any:
        """Update a ROM's editable fields (multipart form)."""
        return self._put(
            f"/api/roms/{id}",
            params={"remove_cover": remove_cover, "unmatch_metadata": unmatch_metadata},
            data=data or {},
        )

    def delete_roms(
        self, roms: list[int], delete_from_fs: list[int] | None = None
    ) -> Any:
        """Delete one or more ROMs (optionally from the filesystem too)."""
        return self._post(
            "/api/roms/delete",
            json={"roms": roms, "delete_from_fs": delete_from_fs or []},
        )

    def download_roms(
        self, rom_ids: list[int], dest: str, filename: str | None = None
    ) -> Any:
        """Download one or more ROMs as an archive, streamed to ``dest``."""
        resp = self._get(
            "/api/roms/download",
            params={"rom_ids": rom_ids, "filename": filename},
            stream=True,
        )
        return self._stream_to_path(resp, dest)

    def get_rom_content(
        self, id: int, file_name: str, dest: str, file_ids: list[int] | None = None
    ) -> Any:
        """Download a ROM's content/file, streamed to ``dest``."""
        resp = self._get(
            f"/api/roms/{id}/content/{file_name}",
            params={"file_ids": file_ids},
            stream=True,
        )
        return self._stream_to_path(resp, dest)

    def head_rom_content(
        self, id: int, file_name: str, file_ids: list[int] | None = None
    ) -> Any:
        """HEAD a ROM's content (size/existence) without downloading."""
        resp = self._head(
            f"/api/roms/{id}/content/{file_name}", params={"file_ids": file_ids}
        )
        return {"status_code": resp.status_code, "headers": dict(resp.headers)}

    # --- manuals ----------------------------------------------------------
    def add_rom_manuals(self, id: int, filename: str, file_path: str) -> Any:
        """Upload a manual for a ROM (streamed raw upload)."""
        with open(file_path, "rb") as fh:
            return self._post(
                f"/api/roms/{id}/manuals",
                data=fh,
                headers={"x-upload-filename": filename},
            )

    def delete_rom_manuals(self, id: int) -> Any:
        """Delete the manuals attached to a ROM."""
        return self._delete(f"/api/roms/{id}/manuals")

    # --- notes ------------------------------------------------------------
    def list_rom_notes(
        self,
        id: int,
        public_only: bool | None = None,
        search: str | None = None,
        tags: str | None = None,
    ) -> Any:
        """List notes attached to a ROM."""
        return self._get(
            f"/api/roms/{id}/notes",
            params={"public_only": public_only, "search": search, "tags": tags},
        )

    def get_rom_note_identifiers(self, id: int) -> Any:
        """Get lightweight identifiers for a ROM's notes."""
        return self._get(f"/api/roms/{id}/notes/identifiers")

    def create_rom_note(self, id: int, **body: Any) -> Any:
        """Create a note on a ROM."""
        return self._post(f"/api/roms/{id}/notes", json=body)

    def update_rom_note(self, id: int, note_id: int, **body: Any) -> Any:
        """Update an existing ROM note."""
        return self._put(f"/api/roms/{id}/notes/{note_id}", json=body)

    def delete_rom_note(self, id: int, note_id: int) -> Any:
        """Delete a ROM note."""
        return self._delete(f"/api/roms/{id}/notes/{note_id}")

    # --- user properties --------------------------------------------------
    def update_rom_user(self, id: int, **body: Any) -> Any:
        """Update per-user ROM properties (rating, status, play-count, ...)."""
        return self._put(f"/api/roms/{id}/props", json=body)
