# thu-learn-downloader

Download everything from Web Learning of Tsinghua University

## Demo

![Demo](https://res.cloudinary.com/liblaf/image/upload/v1679497703/2023/03/22/20230322-1679497699.gif)

The resulting file structure looks like:

```
thu-learn
└── Quantum Mechanics(1)
   ├── docs
   │  └── 电子教案
   │     ├── 01-0量子力学介绍1.pdf
   │     └── 04-0量子力学介绍2.pdf
   └── work
      └── 01-第一周作业
         ├── attach-第一周作业.pdf
         ├── submit-第一周作业.pdf
         └── README.md
```

## Usage

**Usage**:

```shell-session
$ tld [OPTIONS]
```

**Options**:

- `-u, --username TEXT`: [default: liqin20]
- `-p, --password TEXT`
- `-s, --semester TEXT`: [default: 2022-2023-2]
- `-c, --course TEXT`
- `--prefix PATH`: [default: /home/liblaf/Desktop/thu-learn]
- `-s, --size-limit INTEGER`: [default: 9223372036854775807]
- `--install-completion`: Install completion for the current shell.
- `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
- `--help`: Show this message and exit.

## Features

- fast concurrent download
- pretty TUI powered by [rich](https://github.com/Textualize/rich)
- auto set `mtime` of downloaded files according to timestamp of remote file
- auto skip download when local file is newer
- dump homework details into `README.md` in each homework folder
- pretty markdown files powered by [prettier](https://prettier.io) (require `prettier` installed)

## Installation

- download pre-built binary form [GitHub Releases](https://github.com/liblaf/thu-learn-downloader/releases)
- `pip install thu-learn-downloader`
- `pipx install thu-learn-downloader`
