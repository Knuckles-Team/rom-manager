#!/usr/bin/env python
# coding: utf-8

import os
import sys
import getopt
import platform
import subprocess
import patoolib
import shutil


class RomManager:
    def __init__(self):
        self.silent = False
        self.chd_commands = []
        self.directory = os.path.curdir
        self.supported_types = [".iso", ".cue", ".gdi"]
        self.archive_formats = ['7z', 'zip', 'tar.gz', 'gz', 'gzip', 'bz2', 'bzip2', 'rar', 'tar']
        self.extracted_directories = []

    def process_archives(self):
        for archive in get_files(directory=self.directory, extensions=self.archive_formats):
            archive_directory = os.path.splitext(os.path.basename(archive))[0]
            print(f"Extracting {archive} to {archive_directory}...")
            os.makedirs(archive_directory, exist_ok=True)
            patoolib.extract_archive(archive, outdir=archive_directory)
            self.extracted_directories.append(archive_directory)
            print(f"Finished Extracting {archive} to {archive_directory}")

    def cleanup_extracted_archives(self):
        for extracted_directory in self.extracted_directories:
            print(f"Cleaning {extracted_directory}...")
            shutil.rmtree(extracted_directory)
            print(f"Finished Cleaning {extracted_directory}")

    def build_commands(self):
        for file in get_files(directory=self.directory, extensions=self.supported_types):
            chd_file = f"{os.path.splitext(os.path.basename(file))[0]}.chd"
            chd_file_directory = os.path.dirname(file)
            chd_file_path = f"{chd_file_directory}/{chd_file}"
            self.chd_commands.append(['chdman', 'createcd', '-i', f'"{file}"', '-o', f'"{chd_file_path}"'])

    def batch_run_commands(self):
        if self.chd_commands:
            for chd_command in self.chd_commands:
                print(f"Running Command: {chd_command}...")
                result = self.run_command(chd_command)
                if result:
                    print(result.returncode, result.stdout, result.stderr)
                print(f"Finished Running Command: {chd_command}")

    def run_command(self, command):
        result = None
        try:
            if self.silent:
                result = subprocess.run(command, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
            else:
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        universal_newlines=True)
        except subprocess.CalledProcessError as e:
            print(e.output)
        return result


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
    print(f"Usage: \n"
          f"-h | --help      [ See usage for script ]\n"
          f"-d | --directory [ Directory to process ROMs ]\n"
          f"-s | --silent    [ Suppress output messages ]\n"
          f"\n"
          f"rom-manager --directory 'C:/Users/default/Games/'")
    installation_instructions()


def rom_manager(argv):
    directory = ""
    silent = False

    try:
        opts, args = getopt.getopt(argv, "hd:m:s", ["help", "directory=", "silent"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--directory"):
            directory = arg
        elif opt in ("-s", "--silent"):
            silent = True

    roms_manager = RomManager()
    roms_manager.silent = silent
    roms_manager.directory = directory
    roms_manager.process_archives()
    roms_manager.build_commands()
    roms_manager.batch_run_commands()
    roms_manager.cleanup_extracted_archives()


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
