#!/usr/bin/env python
# coding: utf-8

import os
import sys
import getopt
import platform
import subprocess
import patoolib
import shutil
from multiprocessing import Pool
try:
    from version import __version__, __author__, __credits__
except Exception:
    from rom_manager.version import __version__, __author__, __credits__


class RomManager:
    def __init__(self):
        self.silent = False
        self.chd_commands = []
        self.directory = os.path.curdir
        self.supported_types = [".iso", ".cue", ".gdi"]
        self.archive_formats = ['7z', 'zip', 'tar.gz', 'gz', 'gzip', 'bz2', 'bzip2', 'rar', 'tar']
        self.extracted_directories = []

    def parallel_process_archives(self, cpu_count=None):
        if not cpu_count:
            cpu_count = os.cpu_count()
        pool = Pool(processes=cpu_count)
        try:
            pool.map(self.process_archive, get_files(directory=self.directory, extensions=self.archive_formats))
        finally:
            pool.close()
            pool.join()
        print("Extracting All Archives Complete!")

    def process_archive(self, archive):
        archive_directory = os.path.dirname(archive)
        print(f"Extracting {archive} to {archive_directory}...")
        os.makedirs(archive_directory, exist_ok=True)
        try:
            patoolib.extract_archive(archive, outdir=archive_directory)
        except patoolib.util.PatoolError as e:
            print(f"Unable to extract: {archive}\nError: {e}")
        self.extracted_directories.append(archive_directory)
        print(f"Finished Extracting {archive} to {archive_directory}")

    def cleanup_extracted_archives(self):
        for extracted_directory in self.extracted_directories:
            print(f"Cleaning {extracted_directory}...")
            shutil.rmtree(extracted_directory)
            print(f"Finished Cleaning {extracted_directory}")

    def build_commands(self, force=False):
        for file in get_files(directory=self.directory, extensions=self.supported_types):
            chd_file = f"{os.path.splitext(os.path.basename(file))[0]}.chd"
            chd_file_directory = os.path.dirname(file)
            chd_file_path = os.path.join(chd_file_directory, chd_file)
            chd_command = ['chdman', 'createcd', '-i', f"{file}", '-o', f"{chd_file_path}"]
            if force:
                chd_command.append('-f')
            self.chd_commands.append(chd_command)

    def parallel_run_commands(self, cpu_count=None):
        if not cpu_count:
            cpu_count = os.cpu_count()
        pool = Pool(processes=cpu_count)
        print(f"COMMANDS: {self.chd_commands}")
        try:
            pool.map(self.run_command, self.chd_commands)
        finally:
            pool.close()
            pool.join()
        print("Converting All Files Complete!")

    def run_command(self, command):
        try:
            if self.silent:
                result = subprocess.run(command, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
            else:
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        universal_newlines=True)
            print(result.returncode, result.stdout, result.stderr)
        except subprocess.CalledProcessError as e:
            print(e.output)


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
          f"-h | --help      [ See usage for script ]\n"
          f"-c | --cpu-count [ Limit max number of CPUs to use for parallel processing ]\n"
          f"-d | --directory [ Directory to process ROMs ]\n"
          f"-f | --force     [ Force overwrite of existing CHD files ]\n"
          f"-s | --silent    [ Suppress output messages ]\n"
          f"\n"
          f"Example: \n"
          f"rom-manager --directory 'C:/Users/default/Games/'\n")
    installation_instructions()


def rom_manager(argv):
    cpu_count = None
    directory = ""
    silent = False
    force = False

    try:
        opts, args = getopt.getopt(argv, "hc:d:fs", ["help", "cpu-count=", "directory=", "force", "silent"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-c", "--cpu-count"):
            cpu_count = arg
        elif opt in ("-d", "--directory"):
            directory = arg
        elif opt in ("-f", "--force"):
            force = True
        elif opt in ("-s", "--silent"):
            silent = True

    roms_manager = RomManager()
    roms_manager.silent = silent
    roms_manager.directory = directory
    roms_manager.parallel_process_archives(cpu_count=cpu_count)
    roms_manager.build_commands(force=force)
    roms_manager.parallel_run_commands(cpu_count=cpu_count)
    roms_manager.cleanup_extracted_archives()


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(2)
    rom_manager(sys.argv[1:])


if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     usage()
    #     sys.exit(2)
    # rom_manager(sys.argv[1:])
    import csv

    csv_file = "ps2_codes.csv"

    # Initialize an empty dictionary
    data_dict = {}

    with open(csv_file, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            key, value = row
            keys = key.split("\n")
            value = value.replace("\xa0", "")
            for k in keys:
                data_dict[k] = value



    print(data_dict)
    import json
    with open('ps2_codes.json', 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=2)

