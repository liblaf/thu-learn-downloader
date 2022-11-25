import concurrent.futures
import datetime
import os
import time
import typing

import requests
import rich.console
import rich.progress


def download_once(
    url: str,
    file: str,
    raw_size: typing.Optional[int] = 0,
    upload_time: typing.Optional[datetime.datetime] = None,
    session: typing.Optional[requests.Session] = None,
    console: rich.console.Console = rich.console.Console(),
    progress: rich.progress.Progress = rich.progress.Progress(),
    task_id: rich.progress.TaskID = rich.progress.TaskID(0),
) -> bool:
    res = (session or requests).get(url=url, stream=True)
    raw_size = int(res.headers.get("Content-Length", 0)) or raw_size
    if os.path.exists(file):
        if os.path.getsize(file) == raw_size:
            if upload_time:
                mtime = os.path.getmtime(filename=file)
                mtime = datetime.datetime.fromtimestamp(mtime)
                if mtime >= upload_time:
                    return False
    os.makedirs(name=os.path.dirname(file), exist_ok=True)
    progress.reset(task_id=task_id, total=raw_size)
    with open(file=file, mode="wb") as fp:
        progress.start_task(task_id=task_id)
        for chunk in res.iter_content(chunk_size=1024 * 1024):
            bytes_written = fp.write(chunk)
            progress.advance(task_id=task_id, advance=bytes_written)
        if not raw_size:
            progress.update(task_id=task_id, total=fp.tell())
    if upload_time:
        mtime = int(upload_time.timestamp())
        os.utime(path=file, times=(mtime, mtime))
    return True


def download(
    url: str,
    file: str,
    raw_size: typing.Optional[int] = None,
    upload_time: typing.Optional[datetime.datetime] = None,
    session: typing.Optional[requests.Session] = None,
    console: rich.console.Console = rich.console.Console(),
    progress: rich.progress.Progress = rich.progress.Progress(),
    task_id: rich.progress.TaskID = rich.progress.TaskID(0),
    max_retries: int = 4,
) -> None:
    for i in range(max_retries + 1):
        try:
            if i:
                console.log(
                    f"Retry {i}: {progress.tasks[task_id].description}",
                    style="bold bright_blue",
                )
            ret = download_once(
                url=url,
                file=file,
                raw_size=raw_size,
                upload_time=upload_time,
                session=session,
                console=console,
                progress=progress,
                task_id=task_id,
            )
        except:
            console.log(
                f"Download Failed: {progress.tasks[task_id].description}",
                style="bold bright_red",
            )
        else:
            if ret:
                console.log(
                    f"Download Success: {progress.tasks[task_id].description}",
                    style="bold bright_green",
                )
            else:
                console.log(
                    f"Download Skipped: {progress.tasks[task_id].description}",
                    style="dim",
                )
            progress.update(task_id=task_id, visible=False)
            return


class Downloader:
    pool: concurrent.futures.Executor
    progress: rich.progress.Progress

    def __init__(self) -> None:
        self.pool = concurrent.futures.ThreadPoolExecutor()
        self.progress = rich.progress.Progress(
            rich.progress.TextColumn(
                text_format="{task.description}", style="bold blue"
            ),
            rich.progress.BarColumn(),
            rich.progress.DownloadColumn(),
            rich.progress.TaskProgressColumn(),
            rich.progress.TransferSpeedColumn(),
            rich.progress.TimeRemainingColumn(),
        )

    def schedule_download(
        self,
        url: str,
        file: str,
        raw_size: typing.Optional[int] = None,
        upload_time: typing.Optional[datetime.datetime] = None,
        session: typing.Optional[requests.Session] = None,
        console: rich.console.Console = rich.console.Console(),
        description: typing.Optional[str] = None,
        max_retries: int = 4,
    ):
        while True:
            running_tasks = 0
            for task in self.progress.tasks:
                if task.visible:
                    running_tasks += 1
            if running_tasks < 16:
                break
            else:
                time.sleep(1)

        task_id = self.progress.add_task(
            description=description or file, start=False, total=raw_size
        )
        self.pool.submit(
            download,
            url=url,
            file=file,
            raw_size=raw_size,
            upload_time=upload_time,
            session=session,
            console=console,
            progress=self.progress,
            task_id=task_id,
            max_retries=max_retries,
        )
