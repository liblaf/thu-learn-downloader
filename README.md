# THU Web Learning Downloader

Download everything from Web Learning of Tsinghua University

[![Build Status](https://img.shields.io/github/actions/workflow/status/liblaf/thu-learn-downloader/ci.yaml)](https://github.com/liblaf/thu-learn-downloader/actions/workflows/ci.yaml)
[![Python Version](https://img.shields.io/pypi/pyversions/thu-learn-downloader)](https://pypi.org/project/thu-learn-downloader/)
[![PyPI](https://img.shields.io/pypi/v/thu-learn-downloader)](https://pypi.org/project/thu-learn-downloader/)

## Demo

![Demo](https://github.com/liblaf/thu-learn-downloader/raw/assets/demo.png)

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

- `-u, --username TEXT`
- `-p, --password TEXT`
- `--prefix DIRECTORY`: [default: $HOME/thu-learn]
- `-s, --semester TEXT`: [default: 2023-2024-1]
- `-c, --course TEXT`
- `--document / --no-document`: [default: document]
- `--homework / --no-homework`: [default: homework]
- `-j, --jobs INTEGER`: [default: 8]
- `-l, --language [en|zh]`: [default: en]
- `--log-level [NOTSET|DEBUG|INFO|WARNING|ERROR|CRITICAL]`: [env var: LOG_LEVEL; default: INFO]
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
