#!/usr/bin/env python
# coding: utf-8

import os
import sys
import getopt
import platform
import subprocess
import patoolib as patool
import glob
import shutil
import re
from multiprocessing import Pool

try:
    from version import __version__, __author__, __credits__
    from game_codes import psx_codes
except ImportError:
    from rom_manager.version import __version__, __author__, __credits__
    from rom_manager.game_codes import psx_codes


class RomManager:
    def __init__(self):
        self.silent = False
        self.force = False
        self.clean_origin_files = False
        self.directory = os.path.curdir
        self.generative_types = (".bin", ".m3u")
        self.supported_types = (".iso", ".cue", ".gdi")
        self.archive_formats = ('7z', 'zip', 'tar.gz', 'gz', 'gzip', 'bz2', 'bzip2', 'rar', 'tar')

    def process_parallel(self, cpu_count=None):
        if not cpu_count:
            cpu_count = os.cpu_count()
        pool = Pool(processes=cpu_count)
        try:
            process_extensions = self.archive_formats + self.supported_types + self.generative_types
            files = self.get_files(directory=self.directory, extensions=process_extensions)
            pool.map(self.process_file, files)
        finally:
            pool.close()
            pool.join()
        print("Conversion of all files complete!")

    def process_file(self, file=None):
        archive_file = None
        if not file:
            return

        # Create directory if game is in top folder
        if os.path.dirname(file) == self.directory:
            game_directory = os.path.join(os.path.dirname(file), os.path.splitext(os.path.basename(file))[0])
            os.makedirs(game_directory, exist_ok=True)
        else:
            game_directory = os.path.dirname(file)

        # Extract if archive is found
        if file.lower().endswith(self.archive_formats):
            archive_file = file
            self.process_archive(archive=archive_file, archive_directory=game_directory)
            files = self.get_files(directory=game_directory, extensions=self.supported_types)
            file = files[0]
        elif file.lower().endswith(self.supported_types):
            print("ISO/GDI/Cue file found")
            new_file_path = os.path.join(str(game_directory), os.path.basename(file))
            shutil.move(f"{file}", f"{new_file_path}")
            file = new_file_path
        elif file.lower().endswith(self.generative_types):
            new_file_path = os.path.join(str(game_directory), os.path.basename(file))
            shutil.move(f"{file}", f"{new_file_path}")
            print("Generating any missing .cue file(s)")
            file = self.cue_file_generator(directory=game_directory)

        # Update the names of ROMs with the included ROM Code mapping
        file = self.map_game_code_name(file=file)

        # Build the chdman command
        chd_file = f"{os.path.splitext(os.path.basename(file))[0]}.chd"
        chd_file_directory = os.path.dirname(file)
        chd_file_path = os.path.join(chd_file_directory, chd_file)
        chd_command = ['chdman', 'createcd', '-i', f"{file}", '-o', f"{chd_file_path}"]
        if self.force:
            chd_command.append('-f')

        # Run the chdman command
        if os.path.exists(chd_file_path):
            print(f"Game already exists in .chd format: {chd_file_path}")
        else:
            print(f"Running chdman: {chd_command}...")
            self.run_command(command=chd_command, silent=self.silent)

        if archive_file:
            self.cleanup_extracted_files(game_directory, chd_file_path)

        # Cleanup
        if self.clean_origin_files:
            self.cleanup_origin_files(game_directory=game_directory,
                                      chd_file_path=chd_file_path,
                                      archive_file=archive_file)

    @staticmethod
    def map_game_code_name(file):
        print("Scanning the filename for known ROM codes")
        for key, value in psx_codes.items():
            if key in os.path.basename(file):
                file_path = os.path.dirname(file)
                file_extension = os.path.splitext(file)[1]
                cleaned_value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', value)
                new_file = os.path.join(file_path, f"{cleaned_value} - {key}{file_extension}")
                if file != new_file and not os.path.exists(new_file):
                    os.rename(file, new_file)
                    file = new_file
                print(f"The string contains the key: {key}")
        return file

    def cleanup_origin_files(self, game_directory, chd_file_path, archive_file=None):
        # Cleanup original files
        print(f"Deleting original file {archive_file}...")
        self.cleanup_archive(archive_file)
        self.cleanup_extracted_files(game_directory=game_directory, chd_file_path=chd_file_path)

    @staticmethod
    def cleanup_archive(archive_file=None):
        # Cleanup original files
        print(f"Deleting original file {archive_file}...")
        if archive_file and os.path.exists(str(archive_file)):
            os.remove(archive_file)
            print(f"The original file {archive_file} has been deleted.")
        else:
            print(f"The original file {archive_file} does not exist.")

    @staticmethod
    def cleanup_extracted_files(game_directory=None, chd_file_path=None):
        # Cleanup any extracted directories
        if game_directory and os.path.exists(game_directory):
            print(f"Cleaning {game_directory}...")
            parent_directory = os.path.dirname(os.path.dirname(chd_file_path))
            new_file_path = os.path.join(parent_directory, os.path.basename(chd_file_path))
            shutil.move(f"{chd_file_path}", f"{new_file_path}")
            shutil.rmtree(game_directory)
            print(f"Finished cleaning {game_directory}")

    @staticmethod
    def run_command(command, silent=False):
        try:
            if silent:
                result = subprocess.run(command, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
            else:
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        universal_newlines=True)
            print(result.returncode, result.stdout, result.stderr)
        except subprocess.CalledProcessError as e:
            print(e.output)

    def process_archive(self, archive, archive_directory):
        print(f"Extracting {archive} to {archive_directory}...")
        try:
            patool.extract_archive(archive, outdir=archive_directory)
        except patool.util.PatoolError as e:
            print(f"Unable to extract: {archive}\nError: {e}")

        print(f"Finished extracting {archive} to {archive_directory}")
        print("Generating any missing cue file(s)")
        if (glob.glob(os.path.join(str(archive_directory), "*.bin"))
                and not glob.glob(os.path.join(str(archive_directory), "*.cue"))):
            self.cue_file_generator(archive_directory)
        print("Finished generating missing cue file(s)")

    @staticmethod
    def pad_leading_zero(number):
        padded = "0" + str(number)
        return padded[-2:]

    def cue_file_generator(self, directory):
        file_names = self.get_files(directory=directory, extensions=[".bin"])
        first_file = file_names.pop(0)
        first_file = os.path.basename(first_file)
        sheet = (f'FILE "{first_file}" BINARY\n'
                 f'  TRACK 01 MODE2/2352\n'
                 f'    INDEX 01 00:00:00\n')
        track_counter = 2
        for file_name in file_names:
            sheet += (f'FILE "{file_name}" BINARY\n'
                      f'  TRACK {self.pad_leading_zero(track_counter)} AUDIO\n'
                      f'    INDEX 00 00:00:00\n'
                      f'    INDEX 01 00:02:00\n')
            track_counter += 1
        cue_file_path = os.path.join(directory, f"{os.path.splitext(os.path.basename(first_file))[0]}.cue")
        with open(cue_file_path, "w") as cue_file:
            cue_file.write(sheet)
        return cue_file_path

    @staticmethod
    def get_files(directory, extensions):
        matching_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    matching_files.append(os.path.join(root, file))
        return matching_files


def get_operating_system():
    operating_system = None
    system = platform.system()
    release = platform.release()
    version = platform.version()
    if "ubuntu" in str(version).lower() or "smp" in str(version).lower():
        operating_system = "Ubuntu"
    elif "windows" in str(system).lower() and ("10" in release or "11" in release):
        operating_system = "Windows"
    return operating_system


def installation_instructions():
    if get_operating_system() == "Windows":
        print(f"Install for Windows:\n"
              f"1) Navigate to https://github.com/mamedev/mame/releases\n"
              f"2) Install mame_...64bit.exe if you have a 64-bit machine or mame.exe if you have a 32-bit machine\n"
              f"3) Extract to C:\\mame-tools\n"
              f"4) Add C:\\mame-tools to System Environment Variable PATH\n")
    if get_operating_system() == "Ubuntu":
        print("Install for Ubuntu:\n"
              "1) apt install mame-tools\n")


def usage():
    print(f'ROM Manager: Convert Game ROMs to Compressed Hunks of Data (CHD) file format\n'
          f'Version: {__version__}\n'
          f'Author: {__author__}\n'
          f'Credits: {__credits__}\n'
          f"\n"
          f"Usage: \n"
          f"-h | --help       [ See usage for script ]\n"
          f"-c | --cpu-count  [ Limit max number of CPUs to use for parallel processing ]\n"
          f"-d | --directory  [ Directory to process ROMs ]\n"
          f"-f | --force      [ Force overwrite of existing CHD files ]\n"
          f"-s | --silent     [ Suppress output messages ]\n"
          f"-x | --delete     [ Delete original files after processing ]\n"
          f"\n"
          f"Example: \n"
          f"rom-manager --directory 'C:/Users/default/Games/'\n")
    installation_instructions()


def rom_manager(argv):
    cpu_count = None
    directory = ""
    silent = False
    force = False
    clean_origin_files = False

    try:
        opts, args = getopt.getopt(argv, "hc:d:fsx", ["help", "cpu-count=", "directory=", "force", "silent",
                                                      "delete"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-c", "--cpu-count"):
            if 0 < int(arg) <= os.cpu_count():
                cpu_count = int(arg)
        elif opt in ("-d", "--directory"):
            directory = arg
        elif opt in ("-f", "--force"):
            force = True
        elif opt in ("-s", "--silent"):
            silent = True
        elif opt in ("-x", "--delete"):
            clean_origin_files = True

    roms_manager = RomManager()
    roms_manager.silent = silent
    roms_manager.force = force
    roms_manager.directory = directory
    roms_manager.clean_origin_files = clean_origin_files
    roms_manager.process_parallel(cpu_count=cpu_count)
    # roms_manager.parallel_process_archives(cpu_count=cpu_count)
    # roms_manager.build_commands(force=force)
    # roms_manager.parallel_run_commands(cpu_count=cpu_count)
    # roms_manager.cleanup(deep_clean=deep_clean)


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

    # import csv
    #
    # csv_file = "ps1_codes.csv"
    #
    # # Initialize an empty dictionary
    # data_dict = {}
    #
    # with open(csv_file, "r") as file:
    #     reader = csv.reader(file)
    #     for row in reader:
    #         key, value = row
    #         keys = key.split("\n")
    #         value = value.replace("\xa0", "")
    #         for k in keys:
    #             data_dict[k] = value
    #
    #
    #
    # print(data_dict)
    # import json
    # with open('ps1_codes.json', 'w', encoding='utf-8') as f:
    #     json.dump(data_dict, f, ensure_ascii=False, indent=2)
    #
