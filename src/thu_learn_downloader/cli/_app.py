import asyncio
import logging
from typing import Annotated

import rich
import rich.logging
import typer

import thu_learn_downloader as tld

app: typer.Typer = typer.Typer()


@app.command()
def main(
    username: Annotated[
        str | None, typer.Option("-u", "--user", envvar="TLD_USER")
    ] = None,
    password: Annotated[
        str | None, typer.Option("-p", "--pass", envvar=["TLD_PASS"])
    ] = None,
) -> None:
    logging.basicConfig(
        level=logging.DEBUG, handlers=[rich.logging.RichHandler(level=logging.DEBUG)]
    )
    assert username
    assert password
    asyncio.run(tld.cli.main(username, password))
