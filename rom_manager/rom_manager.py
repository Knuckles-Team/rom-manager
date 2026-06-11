#!/usr/bin/env python
"""ROM Manager orchestrator (the conversion pipeline entry point).

CONCEPT:ROM-001 — ROM Conversion. :class:`RomManager` is the orchestrator that
composes the focused responsibility layers (:mod:`rom_manager.archives`,
:mod:`rom_manager.conversion`, :mod:`rom_manager.naming`). Domain logic that
previously lived inline in this god-module now lives in those modules; this file
keeps the public ``RomManager`` / ``rom_manager()`` API stable while delegating.
"""

import getopt
import logging
import os
import platform
import random
import shutil
import string
import sys
import time
from functools import partial
from multiprocessing import Pool

from tqdm import tqdm

from rom_manager import archives, conversion
from rom_manager.archives import ARCHIVE_FORMATS
from rom_manager.conversion import Converter

# Re-exported for backwards compatibility (was a module-level import here).
from rom_manager.game_codes import psx_codes  # noqa: F401,E402
from rom_manager.naming import map_game_code_name
from rom_manager.version import __author__, __credits__, __version__


class RomManager:
    """Orchestrates the extract -> rename -> convert -> cleanup ROM pipeline.

    CONCEPT:ROM-001 — composes the archive, naming, and conversion layers; the
    per-method behaviour is preserved exactly from the original monolith.
    """

    logging.getLogger("patoolib").setLevel(logging.WARNING)

    def __init__(self):
        """Initialise pipeline defaults and supported extensions (CONCEPT:ROM-001)."""
        self.logger_name = "rom_manager"
        self.logger = logging.getLogger(self.logger_name)
        self.logger.disabled = True
        self.logger_level = logging.WARNING
        # Configure a handler for the logger (outputting to console)
        handler = logging.StreamHandler()
        self.logger_format = "%(levelname)s: %(message)s - %(asctime)s"
        self.log_formater = logging.Formatter(self.logger_format)
        handler.setFormatter(self.log_formater)
        self.logger.addHandler(handler)
        self.iso_type = "chd"
        self.generative_types: tuple[str, ...] = (".bin", ".m3u")
        self.rvz_types: tuple[str, ...] = (".wbfs", ".iso")
        self.chd_types: tuple[str, ...] = (".iso", ".cue", ".gdi")
        self.archive_formats = ARCHIVE_FORMATS
        self.supported_extensions = (
            self.archive_formats
            + self.chd_types
            + self.generative_types
            + self.rvz_types
        )
        self.verbose = False
        self.force = False
        self.clean_origin_files = False
        self.directory = os.path.curdir
        # DI seam: the external-binary runner used by the conversion layer.
        # Tests may override this to avoid requiring chdman/dolphin-tool.
        self._runner = None

    def process_parallel(self, cpu_count) -> list:
        """Convert every supported ROM under ``self.directory`` in parallel.

        CONCEPT:ROM-001 — discovers candidate files and fans
        :meth:`process_file` out across a process pool.
        """
        if self.verbose:
            self.logger.disabled = False
            self.logger.setLevel(logging.DEBUG)
            self.logger_level = logging.DEBUG
            self.logger.debug("Logger level: %s", self.logger.level)
        if not cpu_count:
            cpu_count = int((os.cpu_count() or 2) / 2 + 2)
        files = self.get_files(
            directory=self.directory, extensions=self.supported_extensions
        )
        if cpu_count > len(files):
            cpu_count = len(files)
        print(f"Parallel CPU(s) Engaged: {cpu_count}\nProcessing...\n")
        self.logger.info(f"Total Files: {len(files)}\nFiles: {files}")
        partial_process_file = partial(
            self.process_file,
            logger_name=f"{self.logger_name}",
            logger_level=self.logger_level,
            logger_format=self.logger_format,
        )
        with Pool(
            processes=cpu_count,
            initializer=self.init_logger,
            initargs=(self.logger_name, self.logger_level, self.logger_format),
        ) as pool:
            result_list_tqdm = list(
                tqdm(pool.imap(partial_process_file, files), total=len(files))
            )

        return result_list_tqdm

    def init_logger(self, logger_name, logger_level, logger_format):
        # Initialize logger in each worker process
        logger_name = f"{logger_name}-{''.join(random.choices(string.ascii_letters + string.digits, k=5))}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logger_level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(logger_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def process_file(self, file, logger_name, logger_level, logger_format):
        """Run one ROM through extract -> rename -> convert -> cleanup.

        CONCEPT:ROM-001 — the per-file conversion pipeline: extracts archives,
        normalises the name (CONCEPT:ROM-002), then converts to CHD/RVZ.
        """
        logger = logging.getLogger(logger_name)
        logger.setLevel(logger_level)
        formatter = logging.Formatter(logger_format)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        archive_file = None
        logger.debug("Logger level: %s", logger.level)
        # Create directory if game is in top folder

        logger.info("Detecting parent directory")
        if os.path.dirname(file) == self.directory:
            game_directory = os.path.join(
                os.path.dirname(file), os.path.splitext(os.path.basename(file))[0]
            )
            logger.info(f"Creating parent directory for: {file}\n{game_directory}")
            os.makedirs(game_directory, exist_ok=True)
        else:
            game_directory = os.path.dirname(file)

        # Extract if archive is found
        if file.lower().endswith(self.archive_formats):
            archive_file = file
            self.process_archive(archive=archive_file, archive_directory=game_directory)
            files = self.get_files(directory=game_directory, extensions=self.chd_types)
            file = files[0]
        elif file.lower().endswith(self.chd_types):
            logger.info("ISO/GDI/Cue file found")
            new_file_path = os.path.join(str(game_directory), os.path.basename(file))
            try:
                shutil.move(f"{file}", f"{new_file_path}")
                file = new_file_path
            except Exception as e:
                logger.error(
                    f"Error moving ISO/GDI/Cue file: {file} to {new_file_path}\n"
                    f"Error: {e}"
                )
        elif file.lower().endswith(self.generative_types):
            new_file_path = os.path.join(str(game_directory), os.path.basename(file))
            try:
                shutil.move(f"{file}", f"{new_file_path}")
            except Exception as e:
                logger.error(
                    f"Error moving file: {file} to {new_file_path}\nError: {e}"
                )
            logger.info("Generating any missing .cue file(s)")
            file = self.cue_file_generator(directory=game_directory)

        # Update the names of ROMs with the included ROM Code mapping
        file = self.map_game_code_name(file=file, logger=logger)

        # Set ISO type conversion
        if self.iso_type == "chd":
            rvz_types_list = list(self.rvz_types)
            rvz_types_list.remove(".iso")
            self.rvz_types = tuple(rvz_types_list)
        elif self.iso_type == "rvz":
            chd_types_list = list(self.chd_types)
            chd_types_list.remove(".iso")
            self.chd_types = tuple(chd_types_list)

        # Build + run the conversion command via the conversion layer.
        _, extension = os.path.splitext(file)
        is_rvz = extension.lower().endswith(self.rvz_types)
        new_ext = ".rvz" if is_rvz else ".chd"
        converted_file = f"{os.path.splitext(os.path.basename(file))[0]}{new_ext}"
        converted_file_directory = os.path.dirname(file)
        converted_file_path = os.path.join(converted_file_directory, converted_file)
        converter = Converter(
            force=self.force, verbose=self.verbose, runner=self._runner
        )
        converter.convert(
            file=file,
            converted_file_path=converted_file_path,
            is_rvz=is_rvz,
            logger=logger,
        )

        if archive_file:
            self.cleanup_extracted_files(
                game_directory, converted_file_path, logger=logger
            )

        # Cleanup
        if self.clean_origin_files:
            self.cleanup_origin_files(
                game_directory=game_directory,
                converted_file_path=converted_file_path,
                archive_file=archive_file,
            )

    @staticmethod
    def map_game_code_name(file, logger=None) -> str:
        """Rename a ROM by its embedded game code (CONCEPT:ROM-002).

        Delegates to :func:`rom_manager.naming.map_game_code_name`; kept as a
        static method for public-API compatibility.
        """
        return map_game_code_name(file=file, logger=logger)

    def cleanup_origin_files(
        self, game_directory, converted_file_path, archive_file=None
    ):
        """Delete the original archive + extracted dir post-conversion (CONCEPT:ROM-001)."""
        self.logger.info(f"Deleting original file {archive_file}...")
        self.cleanup_archive(archive_file, logger=self.logger)
        self.cleanup_extracted_files(
            game_directory=game_directory,
            converted_file_path=converted_file_path,
            logger=self.logger,
        )

    @staticmethod
    def cleanup_archive(archive_file=None, logger=None):
        # Cleanup original files
        logger.info(f"Deleting original file {archive_file}...")
        if archive_file and os.path.exists(str(archive_file)):
            os.remove(archive_file)
            logger.info(f"The original file {archive_file} has been deleted.")
        else:
            logger.info(f"The original file {archive_file} does not exist.")

    @staticmethod
    def cleanup_extracted_files(
        game_directory=None, converted_file_path=None, logger=None
    ):
        """Move the converted file up and remove the extraction dir (CONCEPT:ROM-001)."""
        if game_directory and os.path.exists(game_directory):
            logger.info(f"Cleaning {game_directory}...")
            parent_directory = os.path.dirname(os.path.dirname(converted_file_path))
            new_file_path = os.path.join(
                parent_directory, os.path.basename(converted_file_path)
            )
            try:
                shutil.move(f"{converted_file_path}", f"{new_file_path}")
                shutil.rmtree(game_directory)
            except Exception as e:
                logger.error(
                    f"Error moving file: {converted_file_path} to {new_file_path}\n"
                    f"Error: {e}"
                )

            logger.info(f"Finished cleaning {game_directory}")

    def run_command(self, command, verbose=False, logger=None):
        """Run an external conversion command (delegates to the runner seam)."""
        runner = self._runner or conversion.run_command
        return runner(command=command, verbose=verbose, logger=logger)

    def process_archive(self, archive, archive_directory):
        """Extract an archive and backfill cue sheets (CONCEPT:ROM-001).

        Delegates to :func:`rom_manager.archives.extract_archive`.
        """
        archives.extract_archive(
            archive=archive,
            archive_directory=archive_directory,
            verbose=self.verbose,
            logger=self.logger,
        )

    @staticmethod
    def pad_leading_zero(number) -> str:
        """Zero-pad a track index (delegates to the archives layer)."""
        return archives.pad_leading_zero(number)

    def cue_file_generator(self, directory) -> str:
        """Generate a ``.cue`` sheet from ``.bin`` tracks (CONCEPT:ROM-001).

        Delegates to :func:`rom_manager.archives.cue_file_generator`.
        """
        return archives.cue_file_generator(directory=directory, logger=self.logger)

    @staticmethod
    def get_files(directory, extensions) -> list[str]:
        """List files under ``directory`` matching ``extensions`` (delegates)."""
        return archives.get_files(directory=directory, extensions=extensions)


def get_operating_system() -> str | None:
    """Best-effort host OS detection (CONCEPT:ROM-001 install guidance)."""
    operating_system = None
    system = platform.system()
    release = platform.release()
    version = platform.version()
    if "ubuntu" in str(version).lower() or "smp" in str(version).lower():
        operating_system = "Ubuntu"
    elif "windows" in str(system).lower() and ("10" in release or "11" in release):
        operating_system = "Windows"
    return operating_system


def get_directory_size(directory) -> tuple[int, float, float, float]:
    """Sum file sizes under ``directory`` as (bytes, KB, MB, GB).

    CONCEPT:ROM-001 — used to report storage saved by conversion.
    """
    total_size = 0
    for dirpath, _dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    size_in_bytes = total_size
    size_in_kb = size_in_bytes / 1024
    size_in_mb = size_in_kb / 1024
    size_in_gb = size_in_mb / 1024
    return size_in_bytes, size_in_kb, size_in_mb, size_in_gb


def installation_instructions():
    """Print OS-specific install steps for the external conversion binaries.

    CONCEPT:ROM-001 — chdman (mame-tools) and dolphin-tool guidance.
    """
    if get_operating_system() == "Windows":
        print(
            "Install for Windows:\n"
            "1) Navigate to https://github.com/mamedev/mame/releases\n"
            "2) Install mame_...64bit.exe if you have a 64-bit machine or mame.exe if you have a 32-bit machine\n"
            "3) Extract to C:\\mame-tools\n"
            "4) Add C:\\mame-tools to System Environment Variable PATH\n"
        )
    if get_operating_system() == "Ubuntu":
        print("Install for Ubuntu:\n1) apt install mame-tools\n")
    print(
        "For wbfs support, please install dolphin-tool here: \n"
        "https://github.com/dolphin-emu/dolphin#dolphintool-usage\n"
    )


def usage():
    """Print the CLI usage banner (CONCEPT:ROM-001)."""
    print(
        f"ROM Manager: Convert Game ROMs to Compressed Hunks of Data (CHD) file format or RVZ format.\n"
        f"Backup your ROMs before working with this tool!\n"
        f"Version: {__version__}\n"
        f"\n"
        f"Usage: \n"
        f"-h | --help       [ See usage for script ]\n"
        f"-c | --cpu-count  [ Limit max number of CPUs to use for parallel processing ]\n"
        f"-d | --directory  [ Directory to process ROMs ]\n"
        f'-i | --iso        [ Choose how to convert ISO file(s). Options are "rvz" or "chd" ]\n'
        f"-f | --force      [ Force overwrite of existing .chd files ]\n"
        f"-v | --verbose    [ Display all output messages ]\n"
        f"-x | --delete     [ Delete original files after processing ]\n"
        f"\n"
        f"Example: \n"
        f'rom-manager --directory "C:/Users/default/Games/"\n'
        f"\n"
        f"RomM web library (CONCEPT:ROM-003):\n"
        f"  rom-manager <resource> <action> [args]   (resources: roms, platforms,\n"
        f"  collections, saves, states, firmware, users, tasks, search, stats, ...)\n"
        f"  e.g. rom-manager roms list --platform_ids 7   |   rom-manager stats\n"
        f"  Set ROMM_URL and ROMM_USERNAME/ROMM_PASSWORD (or ROMM_TOKEN).\n"
        f"\n"
    )
    installation_instructions()
    print(f"Author: {__author__}\nCredits: {__credits__}\n")


def rom_manager(argv=None):
    """CLI entry point: parse args and run the conversion pipeline.

    CONCEPT:ROM-001 — parses CLI options, configures a :class:`RomManager`, runs
    :meth:`RomManager.process_parallel`, and reports the storage delta.
    """
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        usage()
        sys.exit(2)

    # Unified CLI (CONCEPT:ROM-003): route RomM web-library subcommands and the
    # explicit 'convert' alias. Bare conversion flags (-d/-c/-i/-f/-v/-x) keep
    # the legacy on-disk converter behaviour below.
    romm_commands = frozenset(
        {
            "roms",
            "platforms",
            "collections",
            "saves",
            "states",
            "screenshots",
            "firmware",
            "users",
            "tasks",
            "search",
            "config",
            "feeds",
            "devices",
            "system",
            "stats",
            "heartbeat",
            "login",
            "logout",
            "auth",
        }
    )
    if argv[0] == "convert":
        argv = argv[1:]
        if not argv:
            usage()
            sys.exit(2)
    elif argv[0] in romm_commands:
        from rom_manager.romm.cli import run_romm_cli

        sys.exit(run_romm_cli(argv))

    cpu_count = None
    directory = ""
    iso_type = "chd"
    verbose = False
    force = False
    clean_origin_files = False

    try:
        opts, args = getopt.getopt(
            argv,
            "hc:d:fvx",
            ["help", "cpu-count=", "directory=", "force", "verbose", "delete"],
        )
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-c", "--cpu-count"):
            if 0 < int(arg) <= (os.cpu_count() or 1):
                cpu_count = int(arg)
        elif opt in ("-d", "--directory"):
            directory = arg
        elif opt in ("-f", "--force"):
            force = True
        elif opt in ("-i", "--iso"):
            if arg.lower() in ["rvz", "chd"]:
                iso_type = arg
            else:
                usage()
                sys.exit()
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-x", "--delete"):
            clean_origin_files = True
    roms_manager = RomManager()
    roms_manager.verbose = verbose
    roms_manager.force = force
    roms_manager.directory = directory
    roms_manager.clean_origin_files = clean_origin_files
    roms_manager.iso_type = iso_type
    before_size = get_directory_size(directory=directory)
    start_time = time.time()
    roms_manager.process_parallel(cpu_count=cpu_count)
    end_time = time.time()
    after_size = get_directory_size(directory=directory)
    elapsed_time_seconds = end_time - start_time
    hours = int(elapsed_time_seconds / 3600)
    minutes = int((elapsed_time_seconds % 3600) / 60)
    seconds = elapsed_time_seconds % 60
    time_message = ""
    if hours > 0:
        time_message = f"{hours} hours, "
    time_message = f"{time_message}{minutes} minutes, {seconds:.2f} seconds"
    print(
        f"Directory size before: {before_size[3]:.2f} GB\n"
        f"Directory size after: {after_size[3]:.2f} GB\n"
        f"Storage delta: {before_size[3] - after_size[3]:.2f} GB\n"
        f"Total time taken: {time_message}"
    )


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(2)
    rom_manager(sys.argv[1:])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(2)
    rom_manager(sys.argv[1:])
