import logging
from pathlib import Path
from typing import Annotated

import typer
from typer import Option, Typer

from .client.client import Language
from .client.learn import Learn
from .common.logging import LogLevel
from .download.downloader import Downloader
from .download.selector import Selector
from .login import auto as login

app: Typer = Typer(name="tld")


@app.command()
def main(
    username: Annotated[str, Option("-u", "--username")] = "",
    password: Annotated[str, Option("-p", "--password")] = "",
    *,
    prefix: Annotated[Path, Option(file_okay=False, writable=True)] = Path.home()
    / "thu-learn",
    semesters: Annotated[list[str], Option("-s", "--semester")] = ["2023-2024-1"],
    courses: Annotated[list[str], Option("-c", "--course")] = [],
    document: Annotated[bool, Option()] = True,
    homework: Annotated[bool, Option()] = True,
    jobs: Annotated[int, Option("-j", "--jobs")] = 8,
    language: Annotated[Language, Option("-l", "--language")] = Language.ENGLISH,
    log_level: Annotated[LogLevel, Option(envvar="LOG_LEVEL")] = LogLevel.INFO,
) -> None:
    logging.getLogger().setLevel(log_level)
    username = username or login.username() or typer.prompt(text="Username")
    password = (
        password or login.password() or typer.prompt(text="Password", hide_input=True)
    )
    learn: Learn = Learn(language=language)
    learn.login(username=username, password=password)
    with Downloader(
        prefix=prefix,
        selector=Selector(
            semesters=semesters,
            courses=courses,
            document=document,
            homework=homework,
        ),
        jobs=jobs,
    ) as downloader:
        downloader.sync_semesters(semesters=learn.semesters)


if __name__ == "__main__":
    app()
