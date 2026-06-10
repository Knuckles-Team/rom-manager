#!/usr/bin/env python
"""Conversion command construction and the external-binary runner seam.

CONCEPT:ROM-001 — ROM Conversion. Builds the ``chdman`` / ``dolphin-tool``
command lines and runs them. The subprocess call is isolated behind
:func:`run_command` (and the ``runner`` parameter on :class:`Converter`) so the
conversion logic has a clean dependency-injection seam: tests can substitute a
fake runner instead of requiring the real external binaries.
"""

import logging
import os
import subprocess
from collections.abc import Callable, Sequence

_NULL_LOGGER = logging.getLogger("rom_manager.conversion")
_NULL_LOGGER.addHandler(logging.NullHandler())

# A runner takes (command, verbose, logger) and executes it.
Runner = Callable[..., None]


def run_command(command, verbose=False, logger=None) -> None:
    """Execute an external conversion ``command`` (the real runner seam).

    CONCEPT:ROM-001 — wraps ``subprocess.run`` with fixed argv and
    ``shell=False``. This is the default :class:`Converter` runner; tests inject
    a fake to avoid requiring ``chdman``/``dolphin-tool``.
    """
    log = logger or _NULL_LOGGER
    try:
        result: subprocess.CompletedProcess
        if verbose is False:
            with open(os.devnull, "wb") as devnull:
                result = subprocess.run(  # nosec B603 - fixed external ROM tool argv, shell=False
                    command,
                    stdout=devnull,
                    stderr=devnull,
                    check=True,
                )
        else:
            result = subprocess.run(  # nosec B603 - fixed external ROM tool argv, shell=False
                command,
                capture_output=True,
                text=True,
                check=True,
            )
        log.info(
            "Command exited with %s\nstdout: %s\nstderr: %s",
            result.returncode,
            result.stdout,
            result.stderr,
        )
    except subprocess.CalledProcessError as e:
        log.warning("Command failed: %s\n%s", command, e.output)


def build_convert_command(
    file: str,
    converted_file_path: str,
    is_rvz: bool,
    force: bool = False,
) -> Sequence[str]:
    """Build the ``chdman``/``dolphin-tool`` argv for converting ``file``.

    CONCEPT:ROM-001 — selects ``dolphin-tool convert`` (RVZ) for WBFS/ISO
    targets, otherwise ``chdman createcd`` for ``.cue`` inputs and
    ``chdman createdvd`` for everything else (appending ``-f`` when ``force``).
    """
    _, extension = os.path.splitext(file)
    if is_rvz:
        return [
            "dolphin-tool",
            "convert",
            "-i",
            f"{file}",
            "-o",
            f"{converted_file_path}",
            "-l",
            "22",
        ]
    chd_create_type = "createdvd"
    if extension.lower().endswith("cue"):
        chd_create_type = "createcd"
    command = [
        "chdman",
        chd_create_type,
        "-i",
        f"{file}",
        "-o",
        f"{converted_file_path}",
    ]
    if force:
        command.append("-f")
    return command


class Converter:
    """Builds and executes ROM conversion commands.

    CONCEPT:ROM-001 — composed by :class:`~rom_manager.rom_manager.RomManager`.
    The ``runner`` callable is injectable (defaults to :func:`run_command`) to
    decouple command construction from the external-binary side effect.
    """

    def __init__(
        self,
        force: bool = False,
        verbose: bool = False,
        runner: Runner | None = None,
    ) -> None:
        self.force = force
        self.verbose = verbose
        self._runner: Runner = runner or run_command

    def convert(
        self,
        file: str,
        converted_file_path: str,
        is_rvz: bool,
        logger=None,
    ) -> Sequence[str]:
        """Build and run the conversion command for ``file``.

        CONCEPT:ROM-001 — skips conversion (warns) if the output already exists;
        otherwise dispatches the built command through the injected runner.
        Returns the command that was (or would have been) executed.
        """
        log = logger or _NULL_LOGGER
        command = build_convert_command(
            file=file,
            converted_file_path=converted_file_path,
            is_rvz=is_rvz,
            force=self.force,
        )
        log.info(f"Command to run: {command}")
        if os.path.exists(converted_file_path):
            log.warning(
                f"Game already exists in converted format: {converted_file_path}"
            )
        else:
            self._runner(command=command, verbose=self.verbose, logger=log)
        return command
