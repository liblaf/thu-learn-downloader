# thu-learn-downloader

Download everything from Web Learning of Tsinghua University

## Demo

![Demo](https://res.cloudinary.com/liblaf/image/upload/v1677213088/2023/02/24/20230224-1677213085.gif)

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

## Features

- fast concurrent download
- pretty TUI powered by [rich](https://github.com/Textualize/rich)
- auto set `mtime` of downloaded files according to timestamp of remote file
- auto skip download when local file is newer
- dump homework details into `README.md` in each homework folder
- pretty markdown files powered by [prettier](https://prettier.io) (require `prettier` installed)

## Usage

### Pre-built Binary

1. Download pre-built binary from [releases](https://github.com/liblaf/thu-learn-downloader/releases).
2. Prepare a `config.yaml` like [config.yaml](https://github.com/liblaf/thu-learn-downloader/blob/main/config.yaml).
3. Run `thu-learn-downloader password="***"` and wait for the sync to finish.

### pip

```shell
pip install thu-learn-downloader
python -m thu_learn_downloader username="***" password="***"
```
