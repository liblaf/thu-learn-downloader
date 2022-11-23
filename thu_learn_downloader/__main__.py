import os
import sys

import hydra
import omegaconf
import rich.console
import rich.live
import rich.panel
import rich.progress
import rich.table

from thu_learn_downloader import sync
from thu_learn_downloader.downloader import Downloader
from thu_learn_downloader.helper import LearnHelper


@hydra.main(config_path=os.getcwd(), config_name="config.yaml", version_base="1.2")
def main(config: omegaconf.DictConfig) -> int:
    helper = LearnHelper(
        username=config.get("username"), password=config.get("password")
    )
    downloader = Downloader()
    overall_progress = rich.progress.Progress(
        rich.progress.TextColumn("{task.description}", style="bold bright_blue"),
        rich.progress.BarColumn(),
        rich.progress.MofNCompleteColumn(),
        rich.progress.TimeElapsedColumn(),
    )
    semesters_task_id = overall_progress.add_task(description="Semesters")
    courses_task_id = overall_progress.add_task(description="Courses")
    progress_group = rich.console.Group(
        rich.panel.Panel(overall_progress),
        rich.panel.Panel(downloader.progress),
    )

    with rich.live.Live(progress_group) as live:
        with downloader.pool:
            try:
                helper.login()
            except:
                live.console.log(
                    f"Login as {helper.username} {helper.status or 'FAILED'}",
                    style="bold bright_red",
                )
            else:
                live.console.log(
                    f"Login as {helper.username} {helper.status}",
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

    return 0


if __name__ == "__main__":
    sys.exit(main())
