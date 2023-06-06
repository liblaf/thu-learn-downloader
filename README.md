# thu-learn-downloader

Download everything from Web Learning of Tsinghua University

## Demo

![Demo](https://cdn.liblaf.me/image/2023/06/06/2023-06-06-23-25-02.gif)

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

```console
$ tld [OPTIONS]
```

**Options**:

- `-u, --username TEXT`: [default: liqin20]
- `-p, --password TEXT`: [required]
- `-s, --semester TEXT`: [default: 2022-2023-2]
- `-c, --course TEXT`
- `--prefix PATH`: [default: /home/liblaf/Desktop/thu-learn]
- `-s, --size-limit INTEGER`: [default: 9223372036854775807]
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
