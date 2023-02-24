import os
import os.path
import time
from concurrent.futures import Executor, ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.style import Style, StyleType

from .constants import (
    CHUNK_SIZE,
    FAILURE_PREFIX,
    MAX_ACTIVE_TASKS,
    RETRY_PREFIX,
    SKIPPED_PREFIX,
    SUCCESS_PREFIX,
)


def download_once(
    url: str,
    output: str | Path,
    session: Optional[requests.Session],
    raw_size: Optional[int] = None,
    upload_time: Optional[datetime] = None,
    progress: Progress = Progress(),
    task_id: TaskID = TaskID(0),
) -> bool:
    output = Path(output)

    resp: requests.Response = (session or requests).get(url=url, stream=True)
    raw_size = int(resp.headers.get("Content-Length", 0)) or raw_size

    if upload_time and os.path.exists(output) and os.path.getsize(output) == raw_size:
        mtime: float = os.path.getmtime(output)
        if mtime >= upload_time.timestamp():
            return False

    os.makedirs(output.parent, exist_ok=True)
    progress.reset(task_id=task_id, total=raw_size)
    with open(file=output, mode="wb") as fp:
        progress.start_task(task_id=task_id)
        for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
            bytes_written = fp.write(chunk)
            progress.advance(task_id=task_id, advance=bytes_written)
        if not raw_size:
            progress.update(task_id=task_id, total=fp.tell())

    if upload_time:
        mtime: float = upload_time.timestamp()
        os.utime(path=output, times=(mtime, mtime))

    return True


def download(
    url: str,
    output: str | Path,
    session: Optional[requests.Session],
    raw_size: Optional[int] = None,
    upload_time: Optional[datetime] = None,
    progress: Progress = Progress(),
    task_id: TaskID = TaskID(0),
    *,
    description: str = "",
    max_retries: int = 4,
    console: Console = Console(),
    style: StyleType = Style(color="bright_cyan", bold=True),
) -> None:
    if not description:
        description = progress.tasks[task_id].description
    style = style if isinstance(style, Style) else Style.parse(style)
    for i in range(max_retries + 1):
        try:
            if i:
                console.log(
                    RETRY_PREFIX,
                    i,
                    description,
                    style=style + Style(color="bright_yellow"),
                )
            rtn: bool = download_once(
                url=url,
                output=output,
                session=session,
                raw_size=raw_size,
                upload_time=upload_time,
                progress=progress,
                task_id=task_id,
            )
        except:
            console.log(
                FAILURE_PREFIX,
                description,
                style=style + Style(color="bright_red"),
            )
        else:
            if rtn:
                console.log(SUCCESS_PREFIX, description, style=style)
            else:
                console.log(
                    SKIPPED_PREFIX,
                    description,
                    style=style + Style(dim=True),
                )
            break
    progress.update(task_id=task_id, visible=False)


class Downloader:
    pool: Executor
    progress: Progress

    def __init__(self) -> None:
        self.pool = ThreadPoolExecutor()
        self.progress = Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            TransferSpeedColumn(),
        )

    def schedule_download(
        self,
        url: str,
        output: str | Path,
        session: Optional[requests.Session],
        raw_size: Optional[int] = None,
        upload_time: Optional[datetime] = None,
        # progress: Progress = Progress(),
        # task_id: TaskID = TaskID(0),
        max_retries: int = 4,
        console: Console = Console(),
        style: StyleType = Style(color="bright_cyan", bold=True),
        *,
        description: str,
    ) -> None:
        while True:
            num_visible_tasks: int = len(
                list(filter(lambda task: task.visible, self.progress.tasks))
            )
            if num_visible_tasks < MAX_ACTIVE_TASKS:
                break
            else:
                time.sleep(1)
        if not isinstance(style, Style):
            style = Style.parse(style)
        task_id: TaskID = self.progress.add_task(
            description=style.render(description), start=False, total=raw_size
        )
        self.pool.submit(
            download,
            url=url,
            output=output,
            session=session,
            raw_size=raw_size,
            upload_time=upload_time,
            progress=self.progress,
            task_id=task_id,
            description=description,
            max_retries=max_retries,
            console=console,
            style=style,
        )
