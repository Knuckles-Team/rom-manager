#!/usr/bin/env python
"""Archive extraction and ``.cue`` sheet generation.

CONCEPT:ROM-001 — ROM Conversion (pre-processing stage). Owns the archive
responsibilities split out of the former ``rom_manager`` god-module: detecting
supported archive formats, extracting them (via the optional ``patool`` native
extra), and synthesising missing ``.cue`` sheets from ``.bin`` tracks.
"""

import glob
import logging
import os

# Supported archive container formats (extraction inputs).
ARCHIVE_FORMATS: tuple[str, ...] = (
    ".7z",
    ".zip",
    ".tar.gz",
    ".gz",
    ".gzip",
    ".bz2",
    ".bzip2",
    ".rar",
    ".tar",
)

_NULL_LOGGER = logging.getLogger("rom_manager.archives")
_NULL_LOGGER.addHandler(logging.NullHandler())


def is_archive(file: str) -> bool:
    """Return ``True`` if ``file`` has a supported archive extension."""
    return file.lower().endswith(ARCHIVE_FORMATS)


def get_files(directory, extensions) -> list[str]:
    """Recursively list files under ``directory`` matching ``extensions``."""
    matching_files = []
    for root, _dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                matching_files.append(os.path.join(root, file))
    return matching_files


def pad_leading_zero(number) -> str:
    """Zero-pad ``number`` to a two-character track index (e.g. ``2`` -> ``02``)."""
    padded = "0" + str(number)
    return padded[-2:]


def cue_file_generator(directory, logger=None) -> str:
    """Generate a ``.cue`` sheet from the ``.bin`` tracks in ``directory``.

    CONCEPT:ROM-001 — emits a standard CD cue sheet (track 01 ``MODE2/2352``,
    subsequent tracks ``AUDIO``) so ``chdman`` can ingest multi-track ``.bin``
    images. Returns the path to the (existing or newly written) cue file.
    """
    file_names = get_files(directory=directory, extensions=[".bin"])
    first_file = file_names.pop(0)
    first_file = os.path.basename(first_file)
    sheet = (
        f'FILE "{first_file}" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n'
    )
    track_counter = 2
    for file_name in file_names:
        sheet += (
            f'FILE "{file_name}" BINARY\n'
            f"  TRACK {pad_leading_zero(track_counter)} AUDIO\n"
            f"    INDEX 00 00:00:00\n"
            f"    INDEX 01 00:02:00\n"
        )
        track_counter += 1
    cue_file_path = os.path.join(
        directory, f"{os.path.splitext(os.path.basename(first_file))[0]}.cue"
    )
    if not os.path.exists(cue_file_path):
        with open(cue_file_path, "w") as cue_file:
            cue_file.write(sheet)
    return cue_file_path


def extract_archive(archive, archive_directory, verbose=False, logger=None) -> None:
    """Extract ``archive`` into ``archive_directory`` and backfill cue sheets.

    CONCEPT:ROM-001 — the archive pre-processing stage of the conversion
    pipeline. ``patool`` is imported lazily so the core package installs without
    native extras; install with ``rom-manager[native]`` for extraction.
    """
    log = logger or _NULL_LOGGER
    try:
        import patoolib as patool
    except ImportError as e:  # pragma: no cover - optional native dependency
        raise ImportError(
            "Archive extraction requires the 'patool' library. "
            "Install the native extras with: pip install 'rom-manager[native]'"
        ) from e

    log.info(f"Extracting {archive} to {archive_directory}...")
    verbosity = 1 if verbose else -1
    try:
        patool.extract_archive(archive, outdir=archive_directory, verbosity=verbosity)
    except patool.util.PatoolError as e:
        log.info(f"Unable to extract: {archive}\nError: {e}")

    log.info(f"Finished extracting {archive} to {archive_directory}")
    log.info("Generating any missing cue file(s)")
    if glob.glob(os.path.join(str(archive_directory), "*.bin")) and not glob.glob(
        os.path.join(str(archive_directory), "*.cue")
    ):
        cue_file_generator(archive_directory, logger=log)
    log.info("Finished generating missing cue file(s)")
