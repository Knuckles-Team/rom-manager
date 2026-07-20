#!/usr/bin/env python
"""Bounded archive extraction and ``.cue`` sheet generation."""

from __future__ import annotations

import bz2
import glob
import gzip
import logging
import os
import shutil
import stat
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import BinaryIO

# Archive names recognized by callers. Extraction itself intentionally supports
# only formats whose complete member table can be validated before materializing
# any bytes. External 7z/RAR tools are not a safe trust boundary.
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

_SAFE_CONTAINER_FORMATS = (".zip", ".tar", ".tar.gz", ".gz", ".gzip", ".bz2", ".bzip2")
_MAX_MEMBERS_DEFAULT = 10_000
_MAX_UNCOMPRESSED_BYTES_DEFAULT = 32 * 1024 * 1024 * 1024
_MAX_COMPRESSION_RATIO_DEFAULT = 1_000
_COPY_CHUNK = 1024 * 1024

_NULL_LOGGER = logging.getLogger("rom_manager.archives")
_NULL_LOGGER.addHandler(logging.NullHandler())


class ArchiveSafetyError(ValueError):
    """Raised before unsafe or unbounded archive content is materialized."""


def _positive_env_int(name: str, default: int) -> int:
    try:
        value = int(os.environ.get(name, str(default)))
    except ValueError as exc:
        raise ArchiveSafetyError(f"{name} must be a positive integer") from exc
    if value <= 0:
        raise ArchiveSafetyError(f"{name} must be a positive integer")
    return value


def _limits() -> tuple[int, int, int]:
    return (
        _positive_env_int("ROM_MANAGER_ARCHIVE_MAX_MEMBERS", _MAX_MEMBERS_DEFAULT),
        _positive_env_int(
            "ROM_MANAGER_ARCHIVE_MAX_UNCOMPRESSED_BYTES",
            _MAX_UNCOMPRESSED_BYTES_DEFAULT,
        ),
        _positive_env_int(
            "ROM_MANAGER_ARCHIVE_MAX_COMPRESSION_RATIO",
            _MAX_COMPRESSION_RATIO_DEFAULT,
        ),
    )


def _safe_member_path(name: str) -> Path:
    if not name or "\x00" in name:
        raise ArchiveSafetyError("Archive contains an invalid member name")
    normalized = name.replace("\\", "/").rstrip("/")
    posix = PurePosixPath(normalized)
    windows = PureWindowsPath(normalized)
    if (
        not normalized
        or posix.is_absolute()
        or windows.is_absolute()
        or windows.drive
        or any(part in {"", ".", ".."} for part in posix.parts)
    ):
        raise ArchiveSafetyError("Archive member escapes the extraction root")
    return Path(*posix.parts)


def _register_member(relative: Path, seen: set[str]) -> None:
    portable = relative.as_posix()
    folded = portable.casefold()
    if folded in seen:
        raise ArchiveSafetyError("Archive contains duplicate member paths")
    seen.add(folded)


def _copy_bounded(source: BinaryIO, target: Path, maximum: int) -> int:
    written = 0
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as output:
        while True:
            chunk = source.read(min(_COPY_CHUNK, maximum - written + 1))
            if not chunk:
                break
            written += len(chunk)
            if written > maximum:
                raise ArchiveSafetyError("Archive member exceeds declared size limit")
            output.write(chunk)
    return written


def _extract_zip(archive: Path, staging: Path) -> None:
    max_members, max_bytes, max_ratio = _limits()
    seen: set[str] = set()
    total = 0
    with zipfile.ZipFile(archive) as container:
        members = container.infolist()
        if len(members) > max_members:
            raise ArchiveSafetyError("Archive member count limit exceeded")
        validated: list[tuple[zipfile.ZipInfo, Path]] = []
        for member in members:
            relative = _safe_member_path(member.filename)
            _register_member(relative, seen)
            unix_mode = (member.external_attr >> 16) & 0xFFFF
            file_type = stat.S_IFMT(unix_mode)
            if file_type == stat.S_IFLNK:
                raise ArchiveSafetyError("Archive links are not permitted")
            if file_type and file_type not in {stat.S_IFREG, stat.S_IFDIR}:
                raise ArchiveSafetyError("Archive special files are not permitted")
            if not member.is_dir():
                total += member.file_size
                if total > max_bytes:
                    raise ArchiveSafetyError("Archive uncompressed size limit exceeded")
                if member.file_size and (
                    not member.compress_size
                    or member.file_size / member.compress_size > max_ratio
                ):
                    raise ArchiveSafetyError("Archive compression ratio limit exceeded")
            validated.append((member, relative))

        for member, relative in validated:
            target = staging / relative
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            with container.open(member, "r") as source:
                written = _copy_bounded(source, target, member.file_size)
            if written != member.file_size:
                raise ArchiveSafetyError("Archive member size did not match metadata")


def _extract_tar(archive: Path, staging: Path) -> None:
    max_members, max_bytes, _ = _limits()
    seen: set[str] = set()
    total = 0
    with tarfile.open(archive, mode="r:*") as container:
        members = container.getmembers()
        if len(members) > max_members:
            raise ArchiveSafetyError("Archive member count limit exceeded")
        validated: list[tuple[tarfile.TarInfo, Path]] = []
        for member in members:
            relative = _safe_member_path(member.name)
            _register_member(relative, seen)
            if not (member.isdir() or member.isreg()) or member.sparse is not None:
                raise ArchiveSafetyError("Archive links and special files are not permitted")
            if member.isreg():
                total += member.size
                if total > max_bytes:
                    raise ArchiveSafetyError("Archive uncompressed size limit exceeded")
            validated.append((member, relative))

        for member, relative in validated:
            target = staging / relative
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            source = container.extractfile(member)
            if source is None:
                raise ArchiveSafetyError("Archive member could not be read")
            with source:
                written = _copy_bounded(source, target, member.size)
            if written != member.size:
                raise ArchiveSafetyError("Archive member size did not match metadata")


def _extract_single_stream(archive: Path, staging: Path, *, kind: str) -> None:
    _, max_bytes, max_ratio = _limits()
    suffixes = {"gzip": (".gz", ".gzip"), "bzip2": (".bz2", ".bzip2")}[kind]
    output_name = archive.name
    for suffix in suffixes:
        if output_name.lower().endswith(suffix):
            output_name = output_name[: -len(suffix)]
            break
    relative = _safe_member_path(output_name or "decompressed.bin")
    compressed_size = max(archive.stat().st_size, 1)
    opener = gzip.open if kind == "gzip" else bz2.open
    stream_limit = min(max_bytes, compressed_size * max_ratio)
    with opener(archive, "rb") as source:
        written = _copy_bounded(source, staging / relative, stream_limit)
    if written / compressed_size > max_ratio:
        raise ArchiveSafetyError("Archive compression ratio limit exceeded")


def _commit_staging(staging: Path, destination: Path) -> None:
    children = list(staging.iterdir())
    for child in children:
        target = destination / child.name
        if target.exists() or target.is_symlink():
            raise ArchiveSafetyError("Archive would overwrite an existing path")
    for child in children:
        shutil.move(str(child), str(destination / child.name))


def is_archive(file: str) -> bool:
    """Return ``True`` if ``file`` has a recognized archive extension."""
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
    """Zero-pad ``number`` to a two-character track index."""
    padded = "0" + str(number)
    return padded[-2:]


def cue_file_generator(directory, logger=None) -> str:
    """Generate a ``.cue`` sheet from the ``.bin`` tracks in ``directory``."""
    file_names = get_files(directory=directory, extensions=[".bin"])
    if not file_names:
        raise ValueError("No BIN tracks were found")
    first_file = os.path.basename(file_names.pop(0))
    sheet = (
        f'FILE "{first_file}" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n'
    )
    track_counter = 2
    for file_name in file_names:
        # Cue sheets should never persist host filesystem locations.
        file_name = os.path.basename(file_name)
        sheet += (
            f'FILE "{file_name}" BINARY\n'
            f"  TRACK {pad_leading_zero(track_counter)} AUDIO\n"
            "    INDEX 00 00:00:00\n"
            "    INDEX 01 00:02:00\n"
        )
        track_counter += 1
    cue_file_path = os.path.join(
        directory, f"{os.path.splitext(first_file)[0]}.cue"
    )
    if not os.path.exists(cue_file_path):
        with open(cue_file_path, "x", encoding="utf-8") as cue_file:
            cue_file.write(sheet)
    return cue_file_path


def extract_archive(archive, archive_directory, verbose=False, logger=None) -> None:
    """Safely extract a bounded archive into ``archive_directory``.

    ZIP and TAR member tables are fully validated before extraction. Gzip and
    bzip2 streams are bounded while decompressing. RAR/7z are rejected because
    the optional external extractor cannot guarantee pre-extraction path safety.
    """
    del verbose  # retained for API compatibility
    log = logger or _NULL_LOGGER
    source_input = Path(archive).expanduser()
    if source_input.is_symlink():
        raise ArchiveSafetyError("Archive must be a regular file")
    source = source_input.resolve(strict=True)
    if not source.is_file():
        raise ArchiveSafetyError("Archive must be a regular file")
    destination_input = Path(archive_directory).expanduser()
    if destination_input.is_symlink():
        raise ArchiveSafetyError("Extraction destination must be a regular directory")
    destination_input.mkdir(parents=True, exist_ok=True)
    destination = destination_input.resolve(strict=True)
    if not destination.is_dir():
        raise ArchiveSafetyError("Extraction destination must be a regular directory")

    lower_name = source.name.lower()
    if not lower_name.endswith(_SAFE_CONTAINER_FORMATS):
        raise ArchiveSafetyError(
            "This archive format cannot be extracted with prevalidated member safety"
        )

    log.info("Extracting a validated archive")
    with tempfile.TemporaryDirectory(
        prefix=".rom-extract-", dir=destination.parent
    ) as temp_dir:
        staging = Path(temp_dir)
        if lower_name.endswith(".zip"):
            _extract_zip(source, staging)
        elif lower_name.endswith((".tar", ".tar.gz")):
            _extract_tar(source, staging)
        elif lower_name.endswith((".gz", ".gzip")):
            _extract_single_stream(source, staging, kind="gzip")
        else:
            _extract_single_stream(source, staging, kind="bzip2")
        _commit_staging(staging, destination)

    log.info("Validated archive extraction complete")
    if glob.glob(os.path.join(str(destination), "*.bin")) and not glob.glob(
        os.path.join(str(destination), "*.cue")
    ):
        cue_file_generator(destination, logger=log)
