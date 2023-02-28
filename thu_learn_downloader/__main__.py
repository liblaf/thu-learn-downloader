import os

import hydra
from omegaconf import DictConfig
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)

from . import sync
from .constants import MAX_ACTIVE_TASKS, SUCCESS_PREFIX
from .downloader import Downloader
from .helper import Helper


@hydra.main(config_path=os.getcwd(), config_name="config.yaml", version_base="1.3")
def main(config: DictConfig) -> None:
    helper = Helper()
    downloader = Downloader()
    overall_progress = Progress(
        TextColumn("{task.description}", style="bold bright_blue"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    )
    semesters_task_id = overall_progress.add_task(description="Semesters")
    courses_task_id = overall_progress.add_task(description="Courses")
    progress_group = Group(
        Panel(downloader.progress, height=MAX_ACTIVE_TASKS + 2),
        Panel(overall_progress),
    )

    username: str = config.get("username")
    password: str = config.get("password")
    with Live(progress_group) as live:
        with downloader.pool:
            try:
                helper.login(username=username, password=password)
            except:
                live.console.log(
                    f"Login as {username} FAILED",
                    style="bold bright_red",
                )
            else:
                live.console.log(
                    SUCCESS_PREFIX,
                    f"Login as {username} SUCCESS",
                    style="bold bright_green",
                )
                sync.sync_all(
                    helper=helper,
                    downloader=downloader,
                    config=config,
                    console=live.console,
                    overall_progress=overall_progress,
                    semesters_task_id=semesters_task_id,
                    courses_task_id=courses_task_id,
                )


if __name__ == "__main__":
    main()
