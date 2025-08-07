import logging
from pathlib import Path
from typing import Annotated

from typer import Option, Typer

from .client.client import Language
from .client.learn import Learn
from .common.logging import LogLevel
from .download.downloader import Downloader
from .download.selector import Selector

app: Typer = Typer(name="tld")


@app.command()
def main(
    username: Annotated[str, Option("-u", "--username")] = "",
    password: Annotated[str, Option("-p", "--password")] = "",
    save_cookie: Annotated[
        bool, Option("-save", "-save-cookie", help="保存浏览器Cookie到本地")
    ] = True,
    all_years: Annotated[
        str,
        Option(
            "-all",
            "--all-years",
            help="下载指定年份范围内的所有课程，格式: 入学年-毕业年 (如: 2021-2025)",
        ),
    ] = "",
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

    # 处理年份范围参数
    if all_years:
        try:
            start_year, end_year = map(int, all_years.split("-"))
            if start_year >= end_year:
                raise ValueError("入学年份必须小于毕业年份")

            print(f"📅 生成学期范围: {start_year} 年入学 - {end_year} 年毕业")

            # 生成所有学期
            generated_semesters = []
            for year in range(start_year, end_year):
                # 每学年有两个学期：秋季学期 (1) 和春季学期 (2)
                generated_semesters.append(f"{year}-{year + 1}-1")  # 秋季学期
                generated_semesters.append(f"{year}-{year + 1}-2")  # 春季学期

            # 覆盖原有的学期设置
            semesters = generated_semesters
            print("📚 将下载以下学期的课程:")
            for sem in semesters:
                print(f"   • {sem}")
            print(f"   共 {len(semesters)} 个学期")

        except ValueError as e:
            if "invalid literal" in str(e):
                print(f"❌ 年份范围格式错误: {all_years}")
                print("   正确格式: 入学年-毕业年 (例如: 2021-2025)")
            else:
                print(f"❌ 年份范围参数错误: {e}")
            return
        except Exception as e:
            print(f"❌ 解析年份范围时发生错误: {e}")
            return
    learn: Learn = Learn(language=language)
    # 尝试加载cookie文件
    try:
        with open("cookies.txt") as f:
            cookies = {}
            for line in f:
                name, value = line.strip().split("=", 1)
                cookies[name] = value
            learn.client.cookies.update(cookies)
    # 如果 cookies.txt 文件不存在，则使用浏览器登录
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

    # 显示课程问题汇总
    from .client.course import get_course_issues

    issues = get_course_issues()

    # 统计并显示问题汇总
    total_issues = sum(len(issue_list) for issue_list in issues.values())
    if total_issues > 0:
        print("\n" + "=" * 60)
        print("📋 课程内容缺失汇总报告")
        print("=" * 60)

        if issues["missing_document_classes"]:
            print(
                f"\n📂 缺少文档分类的课程 ({len(issues['missing_document_classes'])}门):"
            )
            for issue in issues["missing_document_classes"]:
                print(f"   • {issue['course']} - {issue['reason']}")

        if issues["missing_documents"]:
            print(f"\n📄 缺少文档的课程 ({len(issues['missing_documents'])}门):")
            for issue in issues["missing_documents"]:
                print(f"   • {issue['course']} - {issue['reason']}")

        if issues["missing_homeworks"]:
            print(f"\n📝 缺少作业的课程 ({len(issues['missing_homeworks'])}门):")
            for issue in issues["missing_homeworks"]:
                print(f"   • {issue['course']} - {issue['reason']}")

        print(f"\n💡 提示: 共有 {total_issues} 门课程存在内容缺失情况")
        print("   这可能是因为老师还未上传相关内容，或者该课程确实没有相应内容。")
        print("=" * 60)
    else:
        print("\n✅ 所有课程内容获取正常！")


if __name__ == "__main__":
    app()
