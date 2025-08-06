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
    save_cookie: Annotated[bool, Option("-save", "-save-cookie",help="保存浏览器Cookie到本地")] = True,

    *,
    prefix: Annotated[Path, Option(file_okay=False, writable=True)] = Path.home()  # noqa: B008
    / "thu-learn",
    semesters: Annotated[list[str], Option("-s", "--semester")] = [  # noqa: B006
        "2023-2024-1"
    ],
    courses: Annotated[list[str], Option("-c", "--course")] = [],  # noqa: B006
    document: Annotated[bool, Option()] = True,
    homework: Annotated[bool, Option()] = True,
    jobs: Annotated[int, Option("-j", "--jobs")] = 8,
    language: Annotated[Language, Option("-l", "--language")] = Language.ENGLISH,
    log_level: Annotated[LogLevel, Option(envvar="LOG_LEVEL")] = LogLevel.INFO,
) -> None:
    logging.getLogger().setLevel(log_level)
    learn: Learn = Learn(language=language)
    # 尝试加载cookie文件
    try:
        with open("cookies.txt", "r") as f:
            cookies = {}
            for line in f:
                name, value = line.strip().split("=", 1)
                cookies[name] = value
            learn.client.cookies.update(cookies)
    #如果 cookies.txt 文件不存在，则使用浏览器登录
    except FileNotFoundError:
        learn.login()
        if save_cookie:
            try:
                with open("cookies.txt", "w") as f:
                    for name, value in learn.client.cookies.items():
                        f.write(f"{name}={value}\n")
                print("✅ Cookie已保存到 cookies.txt")
            except Exception as e:
                print(f"⚠️ 保存cookie失败: {e}")
    # else:
    #     # 使用传统的用户名密码登录
    #     if not username:
    #         username = login.username() or typer.prompt(text="Username")
    #     if not password:
    #         password = login.password() or typer.prompt(text="Password", hide_input=True)
    #     print("使用用户名密码登录...")
    # learn.login(username=username, password=password)
    
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
