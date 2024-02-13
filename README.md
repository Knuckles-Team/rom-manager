# ROM Manager

![PyPI - Version](https://img.shields.io/pypi/v/rom-manager)
![PyPI - Downloads](https://img.shields.io/pypi/dd/rom-manager)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/rom-manager)
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/rom-manager)
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/rom-manager)
![PyPI - License](https://img.shields.io/pypi/l/rom-manager)
![GitHub](https://img.shields.io/github/license/Knuckles-Team/rom-manager)

![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/rom-manager)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/rom-manager)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/Knuckles-Team/rom-manager)
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/rom-manager)

![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/rom-manager)
![GitHub language count](https://img.shields.io/github/languages/count/Knuckles-Team/rom-manager)
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/rom-manager)
![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/Knuckles-Team/rom-manager)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/rom-manager)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/rom-manager)

*Version: 0.0.21*

Convert Game ROMs to Compressed Hunks of Data (CHD) file format or RVZ file format

Automatically generate missing .cue files for your .bin files!

#### Why?

CHD (“Compressed Hunks of Data”) files are compressed data files that can be used on most CD-based systems. 
They are in a lossless compression format, meaning that they perfectly preserve all game data while reducing file sizes. 
CHDs were originally developed for MAME to compress CD-based arcade games, 
but now they are compatible with a variety emulators and CD-based consoles.

RVZ files are compressed also compressed files, but they are built for Dolphin Emulator specifically

### Supports:
- Sony PlayStation
- Sony PlayStation 2
- Sony PSP
- Sega CD
- Sega Saturn
- Sega Dreamcast
- NEC TurboGrafx-CD (PC Engine CD)
- Neo Geo CD
- Panasonic 3DO
- Amiga CD32
- Philips CD-I
- Nintendo Wii
- Nintendo GameCube

### Archive Types Extracted:
- 7z
- rar
- zip
- tar.gz
- tar
- gz
- gzip
- bzip2
- bz2

### File Types Scanned:
- cue
- iso
- gdi
- wbfs
- bin

<details>
  <summary><b>Usage:</b></summary>

| Short Flag | Long Flag   | Description                                             |
|------------|-------------|---------------------------------------------------------|
| -h         | --help      | See Usage                                               |
| -c         | --cpu-count | Limit max number of CPUs to use for parallel processing |
| -d         | --directory | Directory to scan for ROMs                              |
| -x         | --delete    | Delete the original files                               |
| -f         | --force     | Force overwrite of existing CHD files                   |
| -v         | --verbose   | Print all debug information                             |

</details>

<details>
  <summary><b>Example:</b></summary>

```bash
rom-manager --directory "C:/Users/default/Games/"
```

</details>

<details>
  <summary><b>Installation Instructions:</b></summary>

Install Python Package

```bash
python -m pip install rom-manager
```

</details>

<details>
  <summary><b>Repository Owners:</b></summary>


<img width="100%" height="180em" src="https://github-readme-stats.vercel.app/api?username=Knucklessg1&show_icons=true&hide_border=true&&count_private=true&include_all_commits=true" />

![GitHub followers](https://img.shields.io/github/followers/Knucklessg1)
![GitHub User's stars](https://img.shields.io/github/stars/Knucklessg1)
</details>
