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
import logging
import time
import random
import string
from multiprocessing import Pool
from tqdm import tqdm
from functools import partial

try:
    from version import __version__, __author__, __credits__
    from game_codes import psx_codes
except ImportError:
    from rom_manager.version import __version__, __author__, __credits__
    from rom_manager.game_codes import psx_codes


class RomManager:
    logging.getLogger('patoolib').setLevel(logging.WARNING)

    def __init__(self):
        self.logger_name = "rom_manager"
        self.logger = logging.getLogger(self.logger_name)
        self.logger.disabled = True
        self.logger_level = logging.WARNING
        # Configure a handler for the logger (outputting to console)
        handler = logging.StreamHandler()
        self.logger_format = '%(levelname)s: %(message)s - %(asctime)s'
        self.log_formater = logging.Formatter(self.logger_format)
        handler.setFormatter(self.log_formater)
        self.logger.addHandler(handler)
        self.iso_type = 'chd'
        self.generative_types = ('.bin', '.m3u')
        self.rvz_types = ('.wbfs', '.iso')
        self.chd_types = ('.iso', '.cue', '.gdi')
        self.archive_formats = ('.7z', '.zip', '.tar.gz', '.gz', '.gzip', '.bz2', '.bzip2', '.rar', '.tar')
        self.supported_extensions = self.archive_formats + self.chd_types + self.generative_types + self.rvz_types
        self.verbose = False
        self.force = False
        self.clean_origin_files = False
        self.directory = os.path.curdir

    def process_parallel(self, cpu_count):
        if self.verbose:
            self.logger.disabled = False
            self.logger.setLevel(logging.DEBUG)
            self.logger_level = logging.DEBUG
            print("Logger level:", self.logger.level)  # Debugging statement
        if not cpu_count:
            cpu_count = int(os.cpu_count() / 2 + 2)
        files = self.get_files(directory=self.directory, extensions=self.supported_extensions)
        if cpu_count > len(files):
            cpu_count = len(files)
        print(f"Parallel CPU(s) Engaged: {cpu_count}\nProcessing...\n")
        self.logger.info(f"Total Files: {len(files)}\nFiles: {files}")
        partial_process_file = partial(self.process_file, logger_name=f'{self.logger_name}',
                                       logger_level=self.logger_level,
                                       logger_format=self.logger_format)
        with Pool(processes=cpu_count, initializer=self.init_logger,
                  initargs=(self.logger_name, self.logger_level, self.logger_format)) as pool:
            result_list_tqdm = list(tqdm(pool.imap(partial_process_file, files), total=len(files)))

        return result_list_tqdm

    def init_logger(self, logger_name, logger_level, logger_format):
        # Initialize logger in each worker process
        logger_name = f'{logger_name}-{"".join(random.choices(string.ascii_letters + string.digits, k=5))}'
        logger = logging.getLogger(logger_name)
        logger.setLevel(logger_level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(logger_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def process_file(self, file, logger_name, logger_level, logger_format):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logger_level)
        formatter = logging.Formatter(logger_format)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        archive_file = None
        print("\nLogger level:", self.logger.level)  # Debugging statement
        # Create directory if game is in top folder

        logger.info('Detecting parent directory')
        if os.path.dirname(file) == self.directory:
            game_directory = os.path.join(os.path.dirname(file), os.path.splitext(os.path.basename(file))[0])
            logger.info(f'Creating parent directory for: {file}\n{game_directory}')
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
            logger.info('ISO/GDI/Cue file found')
            new_file_path = os.path.join(str(game_directory), os.path.basename(file))
            try:
                shutil.move(f'{file}', f'{new_file_path}')
                file = new_file_path
            except Exception as e:
                logger.error(f"Error moving ISO/GDI/Cue file: {file} to {new_file_path}\n"
                             f"Error: {e}")
        elif file.lower().endswith(self.generative_types):
            new_file_path = os.path.join(str(game_directory), os.path.basename(file))
            try:
                shutil.move(f'{file}', f'{new_file_path}')
            except Exception as e:
                logger.error(f"Error moving file: {file} to {new_file_path}\n"
                             f"Error: {e}")
            logger.info('Generating any missing .cue file(s)')
            file = self.cue_file_generator(directory=game_directory)

        # Update the names of ROMs with the included ROM Code mapping
        file = self.map_game_code_name(file=file, logger=logger)

        # Set ISO type conversion
        if self.iso_type == 'chd':
            rvz_types_list = list(self.rvz_types)
            rvz_types_list.remove('.iso')
            self.rvz_types = tuple(rvz_types_list)
        elif self.iso_type == 'rvz':
            chd_types_list = list(self.chd_types)
            chd_types_list.remove('.iso')
            self.chd_types = tuple(chd_types_list)

        # Build the conversion command
        _, extension = os.path.splitext(file)
        chd_create_type = "createdvd"
        if extension.lower().endswith("cue"):
            chd_create_type = "createcd"
        if extension.lower().endswith(self.rvz_types):
            converted_file = f'{os.path.splitext(os.path.basename(file))[0]}.rvz'
            converted_file_directory = os.path.dirname(file)
            converted_file_path = os.path.join(converted_file_directory, converted_file)
            convert_command = ['dolphin-tool', 'convert', '-i', f'{file}', '-o', f'{converted_file_path}', '-l', '22']
        else:
            converted_file = f'{os.path.splitext(os.path.basename(file))[0]}.chd'
            converted_file_directory = os.path.dirname(file)
            converted_file_path = os.path.join(converted_file_directory, converted_file)
            convert_command = ['chdman', chd_create_type, '-i', f'{file}', '-o', f'{converted_file_path}']
            if self.force:
                convert_command.append('-f')

        logger.info(f"Command to run: {convert_command}")

        # Run the chdman command
        if os.path.exists(converted_file_path):
            logger.warning(f'Game already exists in .chd format: {converted_file_path}')
        else:
            self.run_command(command=convert_command, verbose=self.verbose, logger=logger)

        if archive_file:
            self.cleanup_extracted_files(game_directory, converted_file_path, logger=logger)

        # Cleanup
        if self.clean_origin_files:
            self.cleanup_origin_files(game_directory=game_directory,
                                      converted_file_path=converted_file_path,
                                      archive_file=archive_file)

    @staticmethod
    def map_game_code_name(file, logger=None):
        logger.info('Scanning the filename for known ROM codes')
        for key, value in psx_codes.items():
            if key in os.path.basename(file):
                file_path = os.path.dirname(file)
                file_extension = os.path.splitext(file)[1]
                cleaned_value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', value)
                new_file = os.path.join(file_path, f'{cleaned_value} - {key}{file_extension}')
                if file != new_file and not os.path.exists(new_file):
                    os.rename(file, new_file)
                    file = new_file
                logger.info(f'The string contains the key: {key}')
        return file

    def cleanup_origin_files(self, game_directory, converted_file_path, archive_file=None):
        # Cleanup original files
        self.logger.info(f'Deleting original file {archive_file}...')
        self.cleanup_archive(archive_file, logger=self.logger)
        self.cleanup_extracted_files(game_directory=game_directory, converted_file_path=converted_file_path,
                                     logger=self.logger)

    @staticmethod
    def cleanup_archive(archive_file=None, logger=None):
        # Cleanup original files
        logger.info(f'Deleting original file {archive_file}...')
        if archive_file and os.path.exists(str(archive_file)):
            os.remove(archive_file)
            logger.info(f'The original file {archive_file} has been deleted.')
        else:
            logger.info(f'The original file {archive_file} does not exist.')

    @staticmethod
    def cleanup_extracted_files(game_directory=None, converted_file_path=None, logger=None):
        # Cleanup any extracted directories
        if game_directory and os.path.exists(game_directory):
            logger.info(f'Cleaning {game_directory}...')
            parent_directory = os.path.dirname(os.path.dirname(converted_file_path))
            new_file_path = os.path.join(parent_directory, os.path.basename(converted_file_path))
            try:
                shutil.move(f'{converted_file_path}', f'{new_file_path}')
                shutil.rmtree(game_directory)
            except Exception as e:
                logger.error(f"Error moving file: {converted_file_path} to {new_file_path}\n"
                             f"Error: {e}")

            logger.info(f'Finished cleaning {game_directory}')

    @staticmethod
    def run_command(command, verbose=False, logger=None):
        try:
            if verbose is False:
                result = subprocess.run(command, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
            else:
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        universal_newlines=True)
            logger.info(result.returncode, result.stdout, result.stderr)
        except subprocess.CalledProcessError as e:
            logger.warning(e.output)

    def process_archive(self, archive, archive_directory):
        self.logger.info(f'Extracting {archive} to {archive_directory}...')
        if self.verbose:
            verbose = 1
        else:
            verbose = -1
        try:
            patool.extract_archive(archive, outdir=archive_directory, verbosity=verbose)
        except patool.util.PatoolError as e:
            self.logger.info(f'Unable to extract: {archive}\nError: {e}')

        self.logger.info(f'Finished extracting {archive} to {archive_directory}')
        self.logger.info('Generating any missing cue file(s)')
        if (glob.glob(os.path.join(str(archive_directory), '*.bin'))
                and not glob.glob(os.path.join(str(archive_directory), '*.cue'))):
            self.cue_file_generator(archive_directory)
        self.logger.info('Finished generating missing cue file(s)')

    @staticmethod
    def pad_leading_zero(number):
        padded = '0' + str(number)
        return padded[-2:]

    def cue_file_generator(self, directory):
        file_names = self.get_files(directory=directory, extensions=['.bin'])
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
        cue_file_path = os.path.join(directory, f'{os.path.splitext(os.path.basename(first_file))[0]}.cue')
        if not os.path.exists(cue_file_path):
            with open(cue_file_path, 'w') as cue_file:
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
    if 'ubuntu' in str(version).lower() or 'smp' in str(version).lower():
        operating_system = 'Ubuntu'
    elif 'windows' in str(system).lower() and ('10' in release or '11' in release):
        operating_system = 'Windows'
    return operating_system


def get_directory_size(directory):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    size_in_bytes = total_size
    size_in_kb = size_in_bytes / 1024
    size_in_mb = size_in_kb / 1024
    size_in_gb = size_in_mb / 1024
    return size_in_bytes, size_in_kb, size_in_mb, size_in_gb


def installation_instructions():
    if get_operating_system() == 'Windows':
        print(f'Install for Windows:\n'
              f'1) Navigate to https://github.com/mamedev/mame/releases\n'
              f'2) Install mame_...64bit.exe if you have a 64-bit machine or mame.exe if you have a 32-bit machine\n'
              f'3) Extract to C:\\mame-tools\n'
              f'4) Add C:\\mame-tools to System Environment Variable PATH\n')
    if get_operating_system() == 'Ubuntu':
        print('Install for Ubuntu:\n'
              '1) apt install mame-tools\n')
    print('For wbfs support, please install dolphin-tool here: \n'
          'https://github.com/dolphin-emu/dolphin#dolphintool-usage\n')


def usage():
    print(f'ROM Manager: Convert Game ROMs to Compressed Hunks of Data (CHD) file format or RVZ format.\n'
          f'Backup your ROMs before working with this tool!\n'
          f'Version: {__version__}\n'
          f'\n'
          f'Usage: \n'
          f'-h | --help       [ See usage for script ]\n'
          f'-c | --cpu-count  [ Limit max number of CPUs to use for parallel processing ]\n'
          f'-d | --directory  [ Directory to process ROMs ]\n'
          f'-i | --iso        [ Choose how to convert ISO file(s). Options are "rvz" or "chd" ]\n'
          f'-f | --force      [ Force overwrite of existing .chd files ]\n'
          f'-v | --verbose    [ Display all output messages ]\n'
          f'-x | --delete     [ Delete original files after processing ]\n'
          f'\n'
          f'Example: \n'
          f'rom-manager --directory "C:/Users/default/Games/"\n'
          f'\n')
    installation_instructions()
    print(f'Author: {__author__}\n'
          f'Credits: {__credits__}\n')


def rom_manager(argv):
    cpu_count = None
    directory = ''
    iso_type = 'chd'
    verbose = False
    force = False
    clean_origin_files = False

    try:
        opts, args = getopt.getopt(argv, 'hc:d:fvx', ['help', 'cpu-count=', 'directory=', 'force', 'verbose',
                                                      'delete'])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt in ('-c', '--cpu-count'):
            if 0 < int(arg) <= os.cpu_count():
                cpu_count = int(arg)
        elif opt in ('-d', '--directory'):
            directory = arg
        elif opt in ('-f', '--force'):
            force = True
        elif opt in ('-i', '--iso'):
            if arg.lower() in ['rvz', 'chd']:
                iso_type = arg
            else:
                usage()
                sys.exit()
        elif opt in ('-v', '--verbose'):
            verbose = True
        elif opt in ('-x', '--delete'):
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
    print(f'Directory size before: {before_size[3]:.2f} GB\n'
          f'Directory size after: {after_size[3]:.2f} GB\n'
          f'Storage delta: {before_size[3] - after_size[3]:.2f} GB\n'
          f'Total time taken: {time_message}')


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(2)
    rom_manager(sys.argv[1:])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        sys.exit(2)
    rom_manager(sys.argv[1:])
