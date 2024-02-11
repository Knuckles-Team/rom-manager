#!/usr/bin/env python
# coding: utf-8

import os
import sys
import getopt
import platform
import subprocess


class RomManager:
    def __init__(self):
        self.system = platform.system()
        self.release = platform.release()
        self.version = platform.version()
        self.operating_system = None
        self.result = None
        self.silent = False
        self.get_operating_system()
        self.chd_command = [['python', '-m', 'pip', 'install', '--upgrade', 'pip']]

    def get_operating_system(self):
        if "ubuntu" in str(self.version).lower() or "smp" in str(self.version).lower():
            self.operating_system = "Ubuntu"
        elif "windows" in str(self.system).lower() and ("10" in self.release or "11" in self.release):
            self.operating_system = "Windows"
        return self.operating_system

    def build_command(self):
        if self.chd_command:
            for install_single_python_module_command in self.chd_command:
                self.run_command(install_single_python_module_command)
                print(self.result.returncode, self.result.stdout, self.result.stderr)

    def run_command(self, command):
        try:
            if self.silent:
                self.result = subprocess.run(command, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
            else:
                print("Running Command: ", command)
                self.result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                             universal_newlines=True)
        except subprocess.CalledProcessError as e:
            print(e.output)


def usage():
    print(f"Usage: \n"
          f"-h | --help [ See usage for script ]\n"
          f"-f | --file [ Subtitle File ]\n"
          f"-m | --mode [ \"+\"/\"-\" ]\n"
          f"-t | --time [ Time in seconds to shift ]\n"
          f"\n"
          f"subshift --file Engrish.srt --mode + --time 5\n")


def installation_instructions():
    print(f"Install for Windows:"
          f"1) Navigate to https://github.com/mamedev/mame/releases"
          f"2) Install mame_...64bit.exe if you have a 64-bit machine or mame.exe if you have a 32-bit machine"
          f"3) Extract to C:\\mame-tools"
          f"4) Add C:\\mame-tools to System Environment Variable PATH")

    print("Install for Ubuntu:"
          "1) apt install mame-tools")


def rom_manager(argv):
    file = ""
    mode = "+"
    time = 5
    # Parse args
    try:
        opts, args = getopt.getopt(argv, "hf:m:t:", ["help", "file=", "mode=", "time="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-f", "--file"):
            file = arg
        elif opt in ("-m", "--mode"):
            mode = arg
            if str(mode) != "+" and str(mode) != "-":
                usage()
                sys.exit(2)
        elif opt in ("-t", "--time"):
            time = arg


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
