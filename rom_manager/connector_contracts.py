"""Surface contracts: tool use, links, data locations and business roles."""

from scion_sdk.surface_contracts import (
    BusinessRole,
    DataLocation,
    Refusal,
    SurfaceLink,
    ToolStep,
    ToolUseContract,
)

CONTRACTS = (
    ToolUseContract(
        "rom-manager-manage-pipeline",
        (
            ToolStep(
                "rom_manager_convert",
                params=(
                    "clean_origin_files",
                    "cpu_count",
                    "directory",
                    "force",
                    "iso_type",
                    "verbose",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
            ToolStep(
                "rom_manager_process_directory",
                params=(
                    "clean_origin_files",
                    "cpu_count",
                    "directory",
                    "force",
                    "iso_type",
                    "verbose",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
            ToolStep(
                "rom_manager_process_file",
                params=(
                    "file",
                    "force",
                    "iso_type",
                    "verbose",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "rom-manager-manage-files",
        (
            ToolStep(
                "rom_manager_list_files",
                params=(
                    "directory",
                    "extensions",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "rom_manager_generate_cue",
                params=(
                    "directory",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "rom_manager_rename_by_game_code",
                params=(
                    "file",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "rom-manager-inspect-game-code",
        (
            ToolStep(
                "rom_manager_list_game_codes",
                params=(
                    "prefix",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "rom_manager_lookup_game_code",
                params=(
                    "code",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "rom-manager-manage-ingest",
        (
            ToolStep(
                "rom_ingest_collections",
                params=(
                    "updated_after",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "rom_ingest_platforms",
                params=(
                    "updated_after",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "rom_ingest_roms",
                params=(
                    "collection_id",
                    "limit",
                    "offset",
                    "platform_ids",
                    "search_term",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "rom-manager-inspect-feed",
        (
            ToolStep(
                "romm_export_gamelist",
                params=(
                    "local_export",
                    "platform_ids",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_fpkgi_feed",
                params=(
                    "platform_slug",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_kekatsu_feed",
                params=(
                    "platform_slug",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_pkgi_ps3_feed",
                params=(
                    "content_type",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_pkgi_psp_feed",
                params=(
                    "content_type",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_pkgi_psvita_feed",
                params=(
                    "content_type",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_pkgj_psp_dlc_feed",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_pkgj_psp_games_feed",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_pkgj_psvita_dlc_feed",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_pkgj_psvita_games_feed",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_pkgj_psx_games_feed",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_tinfoil_feed",
                params=(
                    "slug",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_webrcade_feed",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "rom-manager-manage-save",
        (
            ToolStep(
                "romm_download_save",
                params=(
                    "dest",
                    "device_id",
                    "id",
                    "optimistic",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_save",
                params=(
                    "device_id",
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_save_identifiers",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_saves_summary",
                params=(
                    "rom_id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_list_saves",
                params=(
                    "device_id",
                    "platform_id",
                    "rom_id",
                    "slot",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_add_save",
                params=(
                    "autocleanup",
                    "autocleanup_limit",
                    "device_id",
                    "emulator",
                    "file_path",
                    "overwrite",
                    "rom_id",
                    "slot",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_confirm_save_download",
                params=(
                    "id",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_track_save",
                params=(
                    "id",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_untrack_save",
                params=(
                    "id",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_update_save",
                params=(
                    "id",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_delete_saves",
                params=(
                    "confirm",
                    "saves",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "rom-manager-manage-screenshot",
        (
            ToolStep(
                "romm_add_screenshot",
                params=(
                    "file_path",
                    "rom_id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "rom-manager-manage-state",
        (
            ToolStep(
                "romm_get_state",
                params=(
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_state_identifiers",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_list_states",
                params=(
                    "platform_id",
                    "rom_id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_add_state",
                params=(
                    "emulator",
                    "file_path",
                    "rom_id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_update_state",
                params=(
                    "id",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_delete_states",
                params=(
                    "confirm",
                    "states",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "rom-manager-manage-note",
        (
            ToolStep(
                "romm_get_rom_note_identifiers",
                params=(
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_list_rom_notes",
                params=(
                    "id",
                    "public_only",
                    "search",
                    "tags",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_create_rom_note",
                params=(
                    "id",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_update_rom_note",
                params=(
                    "id",
                    "note_id",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_delete_rom_note",
                params=(
                    "confirm",
                    "id",
                    "note_id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "rom-manager-manage-device",
        (
            ToolStep(
                "romm_get_device",
                params=(
                    "device_id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_list_devices",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_list_netplay_rooms",
                params=(
                    "game_id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_register_device",
                params=(
                    "body",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_update_device",
                params=(
                    "device_id",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_delete_device",
                params=(
                    "confirm",
                    "device_id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "rom-manager-manage-achievement",
        (
            ToolStep(
                "romm_refresh_retro_achievements",
                params=(
                    "id",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "rom-manager-manage-collection",
        (
            ToolStep(
                "romm_get_collection",
                params=(
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_collection_identifiers",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_smart_collection",
                params=(
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_smart_collection_identifiers",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_virtual_collection",
                params=(
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_virtual_collection_identifiers",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_list_collections",
                params=(
                    "updated_after",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_list_smart_collections",
                params=(
                    "updated_after",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_list_virtual_collections",
                params=(
                    "limit",
                    "type",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_add_collection",
                params=(
                    "data",
                    "is_favorite",
                    "is_public",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_add_smart_collection",
                params=(
                    "data",
                    "is_public",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_update_collection",
                params=(
                    "data",
                    "id",
                    "is_public",
                    "remove_cover",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_update_smart_collection",
                params=(
                    "data",
                    "id",
                    "is_public",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_delete_collection",
                params=(
                    "confirm",
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
            ToolStep(
                "romm_delete_smart_collection",
                params=(
                    "confirm",
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "rom-manager-manage-firmware",
        (
            ToolStep(
                "romm_get_firmware",
                params=(
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_firmware_content",
                params=(
                    "dest",
                    "file_name",
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_firmware_identifiers",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_head_firmware_content",
                params=(
                    "file_name",
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_list_firmware",
                params=(
                    "platform_id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_add_firmware",
                params=(
                    "file_path",
                    "platform_id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_delete_firmware",
                params=(
                    "confirm",
                    "delete_from_fs",
                    "firmware",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "rom-manager-manage-platform",
        (
            ToolStep(
                "romm_get_platform",
                params=(
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_platform_identifiers",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_supported_platforms",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_list_platforms",
                params=(
                    "updated_after",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_add_platform",
                params=(
                    "body",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_add_platform_binding",
                params=(
                    "body",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_add_platform_version",
                params=(
                    "body",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_create_setup_platforms",
                params=(
                    "platforms",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_update_platform",
                params=(
                    "id",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_delete_platform",
                params=(
                    "confirm",
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
            ToolStep(
                "romm_delete_platform_binding",
                params=(
                    "confirm",
                    "fs_slug",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
            ToolStep(
                "romm_delete_platform_version",
                params=(
                    "confirm",
                    "fs_slug",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "rom-manager-manage-rom",
        (
            ToolStep(
                "romm_download_roms",
                params=(
                    "dest",
                    "filename",
                    "rom_ids",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_rom",
                params=(
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_rom_by_hash",
                params=(
                    "crc_hash",
                    "md5_hash",
                    "ra_hash",
                    "sha1_hash",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_rom_by_metadata_provider",
                params=(
                    "flashpoint_id",
                    "hasheous_id",
                    "igdb_id",
                    "launchbox_id",
                    "moby_id",
                    "params_json",
                    "ra_id",
                    "ss_id",
                    "tgdb_id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_rom_content",
                params=(
                    "dest",
                    "file_ids",
                    "file_name",
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_rom_filters",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_rom_identifiers",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_romfile",
                params=(
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_romfile_content",
                params=(
                    "dest",
                    "file_name",
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_head_rom_content",
                params=(
                    "file_ids",
                    "file_name",
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_list_roms",
                params=(
                    "collection_id",
                    "favorite",
                    "limit",
                    "offset",
                    "order_by",
                    "order_dir",
                    "params_json",
                    "platform_ids",
                    "search_term",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_search_cover",
                params=(
                    "search_term",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_search_roms",
                params=(
                    "rom_id",
                    "search_by",
                    "search_term",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_add_rom",
                params=(
                    "file_path",
                    "filename",
                    "platform",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_add_rom_manuals",
                params=(
                    "file_path",
                    "filename",
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_update_rom",
                params=(
                    "data",
                    "id",
                    "remove_cover",
                    "unmatch_metadata",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_update_rom_user",
                params=(
                    "id",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_delete_rom_manuals",
                params=(
                    "confirm",
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
            ToolStep(
                "romm_delete_roms",
                params=(
                    "confirm",
                    "delete_from_fs",
                    "roms",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "rom-manager-manage-account",
        (
            ToolStep(
                "romm_get_current_user",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_user",
                params=(
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_user_identifiers",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_list_users",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_add_user",
                params=(
                    "body",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_create_invite_link",
                params=(
                    "role",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_register_user_from_invite",
                params=(
                    "body",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_update_user",
                params=(
                    "data",
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_delete_user",
                params=(
                    "confirm",
                    "id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "rom-manager-manage-auth",
        (
            ToolStep(
                "romm_create_token",
                params=(
                    "password",
                    "scopes",
                    "username",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_forgot_password",
                params=(
                    "body",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_login",
                params=(
                    "body",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_login_via_openid",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_logout",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_oauth_openid",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_reset_password",
                params=(
                    "body",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "rom-manager-manage-server",
        (
            ToolStep(
                "romm_get_config",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_raw_asset",
                params=(
                    "dest",
                    "path",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_setup_library",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_head_raw_asset",
                params=(
                    "path",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_heartbeat",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_metadata_heartbeat",
                params=(
                    "source",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_stats",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_add_exclusion",
                params=(
                    "body",
                    "params_json",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_delete_exclusion",
                params=(
                    "confirm",
                    "exclusion_type",
                    "exclusion_value",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                    Refusal("CONFIRMATION_REQUIRED", "the caller has not confirmed the destructive call"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "rom-manager-manage-task",
        (
            ToolStep(
                "romm_get_task",
                params=(
                    "task_id",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_get_tasks_status",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_list_tasks",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("NOT_FOUND", "the requested record does not exist"),
                ),
            ),
            ToolStep(
                "romm_run_all_tasks",
                params=(),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
            ToolStep(
                "romm_run_task",
                params=(
                    "task_name",
                ),
                result=(
                    "result",
                ),
                refusals=(
                    Refusal("ACCESS_DENIED", "the credential lacks access to the operation"),
                    Refusal("INVALID_ARGUMENT", "the upstream system rejects the input"),
                ),
            ),
        ),
    ),
)

LINKS = (
    SurfaceLink(
        "rom-manager-manage-pipeline",
        tools=(
            "rom_manager_convert",
            "rom_manager_process_directory",
            "rom_manager_process_file",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-conversion-technician",
        ),
        skills=(
            "rom-manager-conversion-pipeline",
        ),
    ),
    SurfaceLink(
        "rom-manager-manage-files",
        tools=(
            "rom_manager_generate_cue",
            "rom_manager_list_files",
            "rom_manager_rename_by_game_code",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-conversion-technician",
        ),
        skills=(
            "rom-manager-conversion-pipeline",
        ),
    ),
    SurfaceLink(
        "rom-manager-inspect-game-code",
        tools=(
            "rom_manager_list_game_codes",
            "rom_manager_lookup_game_code",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-conversion-technician",
        ),
        skills=(
            "rom-manager-code-registry",
        ),
    ),
    SurfaceLink(
        "rom-manager-manage-ingest",
        tools=(
            "rom_ingest_collections",
            "rom_ingest_platforms",
            "rom_ingest_roms",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-library-curator",
        ),
        skills=(
            "rom-manager-library-sync",
        ),
    ),
    SurfaceLink(
        "rom-manager-inspect-feed",
        tools=(
            "romm_export_gamelist",
            "romm_fpkgi_feed",
            "romm_kekatsu_feed",
            "romm_pkgi_ps3_feed",
            "romm_pkgi_psp_feed",
            "romm_pkgi_psvita_feed",
            "romm_pkgj_psp_dlc_feed",
            "romm_pkgj_psp_games_feed",
            "romm_pkgj_psvita_dlc_feed",
            "romm_pkgj_psvita_games_feed",
            "romm_pkgj_psx_games_feed",
            "romm_tinfoil_feed",
            "romm_webrcade_feed",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-catalog-publisher",
        ),
        skills=(
            "rom-manager-catalog-feeds",
        ),
    ),
    SurfaceLink(
        "rom-manager-manage-save",
        tools=(
            "romm_add_save",
            "romm_confirm_save_download",
            "romm_delete_saves",
            "romm_download_save",
            "romm_get_save",
            "romm_get_save_identifiers",
            "romm_get_saves_summary",
            "romm_list_saves",
            "romm_track_save",
            "romm_untrack_save",
            "romm_update_save",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-player-support",
        ),
        skills=(
            "rom-manager-player-assets",
        ),
    ),
    SurfaceLink(
        "rom-manager-manage-screenshot",
        tools=(
            "romm_add_screenshot",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-player-support",
        ),
        skills=(
            "rom-manager-player-assets",
        ),
    ),
    SurfaceLink(
        "rom-manager-manage-state",
        tools=(
            "romm_add_state",
            "romm_delete_states",
            "romm_get_state",
            "romm_get_state_identifiers",
            "romm_list_states",
            "romm_update_state",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-player-support",
        ),
        skills=(
            "rom-manager-player-assets",
        ),
    ),
    SurfaceLink(
        "rom-manager-manage-note",
        tools=(
            "romm_create_rom_note",
            "romm_delete_rom_note",
            "romm_get_rom_note_identifiers",
            "romm_list_rom_notes",
            "romm_update_rom_note",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-player-support",
        ),
        skills=(
            "rom-manager-player-assets",
        ),
    ),
    SurfaceLink(
        "rom-manager-manage-device",
        tools=(
            "romm_delete_device",
            "romm_get_device",
            "romm_list_devices",
            "romm_list_netplay_rooms",
            "romm_register_device",
            "romm_update_device",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-player-support",
        ),
        skills=(
            "rom-manager-player-assets",
        ),
    ),
    SurfaceLink(
        "rom-manager-manage-achievement",
        tools=(
            "romm_refresh_retro_achievements",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-player-support",
        ),
        skills=(
            "rom-manager-player-assets",
        ),
    ),
    SurfaceLink(
        "rom-manager-manage-collection",
        tools=(
            "romm_add_collection",
            "romm_add_smart_collection",
            "romm_delete_collection",
            "romm_delete_smart_collection",
            "romm_get_collection",
            "romm_get_collection_identifiers",
            "romm_get_smart_collection",
            "romm_get_smart_collection_identifiers",
            "romm_get_virtual_collection",
            "romm_get_virtual_collection_identifiers",
            "romm_list_collections",
            "romm_list_smart_collections",
            "romm_list_virtual_collections",
            "romm_update_collection",
            "romm_update_smart_collection",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-library-curator",
        ),
        skills=(
            "rom-manager-library-catalog",
        ),
    ),
    SurfaceLink(
        "rom-manager-manage-firmware",
        tools=(
            "romm_add_firmware",
            "romm_delete_firmware",
            "romm_get_firmware",
            "romm_get_firmware_content",
            "romm_get_firmware_identifiers",
            "romm_head_firmware_content",
            "romm_list_firmware",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-library-curator",
        ),
        skills=(
            "rom-manager-library-catalog",
        ),
    ),
    SurfaceLink(
        "rom-manager-manage-platform",
        tools=(
            "romm_add_platform",
            "romm_add_platform_binding",
            "romm_add_platform_version",
            "romm_create_setup_platforms",
            "romm_delete_platform",
            "romm_delete_platform_binding",
            "romm_delete_platform_version",
            "romm_get_platform",
            "romm_get_platform_identifiers",
            "romm_get_supported_platforms",
            "romm_list_platforms",
            "romm_update_platform",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-library-curator",
        ),
        skills=(
            "rom-manager-library-catalog",
        ),
    ),
    SurfaceLink(
        "rom-manager-manage-rom",
        tools=(
            "romm_add_rom",
            "romm_add_rom_manuals",
            "romm_delete_rom_manuals",
            "romm_delete_roms",
            "romm_download_roms",
            "romm_get_rom",
            "romm_get_rom_by_hash",
            "romm_get_rom_by_metadata_provider",
            "romm_get_rom_content",
            "romm_get_rom_filters",
            "romm_get_rom_identifiers",
            "romm_get_romfile",
            "romm_get_romfile_content",
            "romm_head_rom_content",
            "romm_list_roms",
            "romm_search_cover",
            "romm_search_roms",
            "romm_update_rom",
            "romm_update_rom_user",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-library-curator",
        ),
        skills=(
            "rom-manager-library-catalog",
        ),
    ),
    SurfaceLink(
        "rom-manager-manage-account",
        tools=(
            "romm_add_user",
            "romm_create_invite_link",
            "romm_delete_user",
            "romm_get_current_user",
            "romm_get_user",
            "romm_get_user_identifiers",
            "romm_list_users",
            "romm_register_user_from_invite",
            "romm_update_user",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-player-support",
        ),
        skills=(
            "rom-manager-accounts",
        ),
    ),
    SurfaceLink(
        "rom-manager-manage-auth",
        tools=(
            "romm_create_token",
            "romm_forgot_password",
            "romm_login",
            "romm_login_via_openid",
            "romm_logout",
            "romm_oauth_openid",
            "romm_reset_password",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-player-support",
        ),
        skills=(
            "rom-manager-accounts",
        ),
    ),
    SurfaceLink(
        "rom-manager-manage-server",
        tools=(
            "romm_add_exclusion",
            "romm_delete_exclusion",
            "romm_get_config",
            "romm_get_raw_asset",
            "romm_get_setup_library",
            "romm_head_raw_asset",
            "romm_heartbeat",
            "romm_metadata_heartbeat",
            "romm_stats",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-platform-administrator",
        ),
        skills=(
            "rom-manager-server-administration",
        ),
    ),
    SurfaceLink(
        "rom-manager-manage-task",
        tools=(
            "romm_get_task",
            "romm_get_tasks_status",
            "romm_list_tasks",
            "romm_run_all_tasks",
            "romm_run_task",
        ),
        prompts=(
            "librarian_specialist",
            "rom-manager-platform-administrator",
        ),
        skills=(
            "rom-manager-server-administration",
        ),
    ),
    SurfaceLink(
        "rom-manager-conversion",
        tools=(
            "rom_manager_convert",
            "rom_manager_process_file",
        ),
        prompts=(
            "librarian_specialist",
        ),
        skills=(
            "rom-manager-conversion",
        ),
    ),
    SurfaceLink(
        "rom-manager-game-codes",
        tools=(
            "rom_manager_list_game_codes",
            "rom_manager_lookup_game_code",
        ),
        prompts=(
            "librarian_specialist",
        ),
        skills=(
            "rom-manager-game-codes",
        ),
    ),
    SurfaceLink(
        "rom-manager-library-sync",
        tools=(
            "rom_ingest_collections",
            "rom_ingest_platforms",
            "rom_ingest_roms",
        ),
        prompts=(
            "librarian_specialist",
        ),
        skills=(
            "rom-manager-library-sync",
        ),
    ),
    SurfaceLink(
        "rom-manager-operations",
        tools=(
            "rom_manager_list_files",
            "romm_heartbeat",
            "romm_list_roms",
        ),
        prompts=(
            "librarian_specialist",
        ),
        skills=(
            "rom-manager-operations",
        ),
    ),
)

LOCATIONS = (
    DataLocation(
        "rom-games",
        (
            "Game",
        ),
        "ROMM_HOST",
        "romm_list_roms",
    ),
    DataLocation(
        "rom-platforms",
        (
            "GameSystem",
        ),
        "ROMM_HOST",
        "romm_list_platforms",
    ),
    DataLocation(
        "rom-collections",
        (
            "GameCollection",
        ),
        "ROMM_HOST",
        "romm_list_collections",
    ),
    DataLocation(
        "rom-saves",
        (
            "GameSave",
        ),
        "ROMM_HOST",
        "romm_list_saves",
    ),
    DataLocation(
        "rom-states",
        (
            "GameState",
        ),
        "ROMM_HOST",
        "romm_list_states",
    ),
    DataLocation(
        "rom-firmware",
        (
            "Firmware",
        ),
        "ROMM_HOST",
        "romm_list_firmware",
    ),
)

ROLES = (
    BusinessRole(
        "conversion technician",
        tasks=(
            "rom-manager-inspect-game-code",
            "rom-manager-manage-files",
            "rom-manager-manage-pipeline",
        ),
    ),
    BusinessRole(
        "library curator",
        tasks=(
            "rom-manager-manage-collection",
            "rom-manager-manage-firmware",
            "rom-manager-manage-ingest",
            "rom-manager-manage-platform",
            "rom-manager-manage-rom",
        ),
    ),
    BusinessRole(
        "player support",
        tasks=(
            "rom-manager-manage-account",
            "rom-manager-manage-achievement",
            "rom-manager-manage-auth",
            "rom-manager-manage-device",
            "rom-manager-manage-note",
            "rom-manager-manage-save",
            "rom-manager-manage-screenshot",
            "rom-manager-manage-state",
        ),
    ),
    BusinessRole(
        "catalog publisher",
        tasks=(
            "rom-manager-inspect-feed",
        ),
    ),
    BusinessRole(
        "platform administrator",
        tasks=(
            "rom-manager-manage-server",
            "rom-manager-manage-task",
        ),
    ),
)
