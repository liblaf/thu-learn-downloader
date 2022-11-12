# thu-learn-downloader

Auto download files from thu-learn

## Demo

See Screen Recording at [demo.webm](https://drive.liblaf.top/github/thu-learn-downloader/demo.webm).

The resulting file structure looks like:

```
thu-learn
└── engineering-mechanics-for-civil-engineering
   ├── docs
   │  ├── 作业与思考题
   │  │  └── 第三周部分作业及思考题.pdf
   │  ├── 电子教案
   │  │  └── 第13讲-杆件拉伸和压缩.pdf
   │  └── 课外阅读
   │     └── 基于月面原位资源的月球基地建造技术.pdf
   └── work
      ├── 期中考试
      │  └── README.md
      └── 第2周作业
         ├── attach-第2周作业.docx
         ├── comment-2020012872-李钦-6544.pdf
         ├── README.md
         └── submit-第2周作业.pdf
```

## Features

- pretty TUI powered by [rich](https://github.com/Textualize/rich)
- auto set `mtime` of downloaded files according to timestamp of remote file
- auto skip download when local file is newer
- dump homework details into `README.md` in each homework folder
- pretty markdown files powered by [prettier](https://prettier.io) (require `prettier` installed)

## Usage

1. Download pre-built binary from [releases](https://github.com/liblaf/thu-learn-downloader/releases).
2. Prepare a `config.yaml` like [config.yaml](https://github.com/liblaf/thu-learn-downloader/blob/main/config.yaml).
3. Run `thu-learn-downloader password="***"` and wait for the sync to finish.
