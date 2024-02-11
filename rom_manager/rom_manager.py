#!/usr/bin/env python
# coding: utf-8

import os
import sys
import getopt
import platform
import subprocess
import patoolib
import glob
import shutil
import re
from multiprocessing import Pool
try:
    from version import __version__, __author__, __credits__
    from game_codes import psx_codes
except Exception:
    from rom_manager.version import __version__, __author__, __credits__
    from rom_manager.game_codes import psx_codes


class RomManager:
    def __init__(self):
        self.silent = False
        self.chd_commands = []
        self.directory = os.path.curdir
        self.supported_types = [".iso", ".cue", ".gdi"]
        self.archive_formats = ['7z', 'zip', 'tar.gz', 'gz', 'gzip', 'bz2', 'bzip2', 'rar', 'tar']
        self.extracted_directories = []
        self.processed_files = []

    def parallel_process_archives(self, cpu_count=None):
        if not cpu_count:
            cpu_count = os.cpu_count()
        pool = Pool(processes=cpu_count)
        try:
            files = self.get_files(directory=self.directory, extensions=self.archive_formats)
            pool.map(self.process_archive, files)
        finally:
            pool.close()
            pool.join()
        print("Extracting All Archives Complete!")
        self.processed_files = files
        for file in files:
            extracted_directory = os.path.join(os.path.dirname(file), os.path.splitext(os.path.basename(file))[0])
            self.extracted_directories.append(extracted_directory)

    def cleanup(self, deep_clean=False):
        for extracted_directory in self.extracted_directories:
            print(f"Cleaning {extracted_directory}...")
            for file_path in self.get_files(directory=extracted_directory, extensions=[".chd"]):
                parent_directory = os.path.dirname(os.path.dirname(file_path))
                new_file_path = os.path.join(parent_directory, os.path.basename(file_path))
                shutil.move(f"{file_path}", f"{new_file_path}")
            shutil.rmtree(extracted_directory)
            print(f"Finished Cleaning {extracted_directory}")

        if deep_clean:
            for file in self.processed_files:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"The file {file} has been deleted.")
                else:
                    print(f"The file {file} does not exist.")

    def build_commands(self, force=False):
        for file in self.get_files(directory=self.directory, extensions=self.supported_types):
            for key, value in psx_codes.items():
                if key in os.path.basename(file):
                    # filename = os.path.splitext(os.path.basename(file))[0]
                    file_path = os.path.dirname(file)
                    file_extension = os.path.splitext(file)[1]
                    cleaned_value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', value)
                    new_file = os.path.join(file_path, f"{cleaned_value} - {key}{file_extension}")
                    if file != new_file:
                        os.rename(file, new_file)
                        file = new_file
                    print(f"The string contains the key: {key}")
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

    def process_archive(self, archive):
        archive_directory = os.path.join(os.path.dirname(archive), os.path.splitext(os.path.basename(archive))[0])
        print(f"Extracting {archive} to {archive_directory}...")
        os.makedirs(archive_directory, exist_ok=True)
        try:
            patoolib.extract_archive(archive, outdir=archive_directory)
        except patoolib.util.PatoolError as e:
            print(f"Unable to extract: {archive}\nError: {e}")

        print(f"Finished Extracting {archive} to {archive_directory}")
        print("Generating any missing cue file(s)")
        if (glob.glob(os.path.join(str(archive_directory), "*.bin"))
                and not glob.glob(os.path.join(str(archive_directory), "*.cue"))):
            self.cue_file_generator(archive_directory)

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
    deep_clean = False

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
            deep_clean = True

    roms_manager = RomManager()
    roms_manager.silent = silent
    roms_manager.directory = directory
    roms_manager.parallel_process_archives(cpu_count=cpu_count)
    roms_manager.build_commands(force=force)
    roms_manager.parallel_run_commands(cpu_count=cpu_count)
    roms_manager.cleanup(deep_clean=deep_clean)


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
