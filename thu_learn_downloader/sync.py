import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from omegaconf import DictConfig
from rich.console import Console
from rich.progress import Progress, TaskID

from . import typing as t
from . import utils
from .constants import (
    DEFAULT_PREFIX,
    DOCUMENT_STYLE,
    HOMEWORK_STYLE,
    SKIPPED_PREFIX,
    SUCCESS_PREFIX,
)
from .downloader import Downloader
from .helper import Helper


def sync_all(
    helper: Helper,
    downloader: Downloader,
    config: DictConfig,
    *,
    console: Console = Console(),
    overall_progress: Progress = Progress(),
    semesters_task_id: TaskID = TaskID(0),
    courses_task_id: TaskID = TaskID(1),
) -> None:
    semesters = config.get("semesters") or helper.get_semester_id_list()

    for semester in overall_progress.track(
        semesters, task_id=semesters_task_id, description="Semesters"
    ):
        sync_semester(
            helper=helper,
            downloader=downloader,
            semester_id=semester,
            config=config,
            console=console,
            overall_progress=overall_progress,
            courses_task_id=courses_task_id,
        )


def sync_semester(
    helper: Helper,
    downloader: Downloader,
    config: DictConfig,
    semester_id: str,
    *,
    console: Console = Console(),
    overall_progress: Progress = Progress(),
    courses_task_id: TaskID = TaskID(1),
) -> None:
    courses: list[t.CourseInfo] = helper.get_course_list(semester_id=semester_id)

    if config.get("courses"):
        courses = [
            course
            for course in courses
            if course.name in config["courses"]
            or course.english_name in config["courses"]
        ]

    overall_progress.update(
        task_id=courses_task_id, description=utils.format_semester_id(semester_id)
    )
    for course in overall_progress.track(courses, task_id=courses_task_id):
        sync_course(
            helper=helper,
            downloader=downloader,
            config=config,
            course=course,
            console=console,
        )


def sync_course(
    helper: Helper,
    downloader: Downloader,
    config: DictConfig,
    course: t.CourseInfo,
    *,
    console: Console = Console(),
) -> None:
    sync_files(
        helper=helper,
        downloader=downloader,
        config=config,
        course=course,
        console=console,
    )
    sync_homeworks(
        helper=helper,
        downloader=downloader,
        config=config,
        course=course,
        console=console,
    )


def sync_files(
    helper: Helper,
    downloader: Downloader,
    config: DictConfig,
    course: t.CourseInfo,
    *,
    console: Console = Console(),
) -> None:
    prefix: Path = Path(
        config.get(key="prefix", default_value=DEFAULT_PREFIX)
    ).expanduser()
    size_limit: int = config.get(key="size_limit", default_value=sys.maxsize)

    files: list[t.File] = helper.get_file_list(course_id=course.id)
    files: list[t.File] = sorted(files, key=lambda f: f.id)

    for i, f in enumerate(files):
        filename: str = utils.format_doc_filename(title=f.title, file_type=f.file_type)
        filename: str = f"{i:02d}-{filename}"
        if f.raw_size > size_limit:
            console.log(
                SKIPPED_PREFIX,
                utils.describe_doc_file(
                    course_name=course.english_name, filename=filename
                ),
                "size limit exceeded",
                style=DOCUMENT_STYLE,
            )
            continue

        downloader.schedule_download(
            url=f.download_url,
            output=prefix / course.english_name / "docs" / f.file_clazz / filename,
            session=helper,
            raw_size=f.raw_size,
            upload_time=f.upload_time,
            console=console,
            style=DOCUMENT_STYLE,
            description=utils.describe_doc_file(
                course_name=course.english_name, filename=filename
            ),
        )


def sync_homeworks(
    helper: Helper,
    downloader: Downloader,
    config: DictConfig,
    course: t.CourseInfo,
    *,
    console: Console = Console(),
) -> None:
    homeworks = helper.get_homework_list(course_id=course.id)

    for hw in homeworks:
        sync_homework_detail(
            helper=helper,
            downloader=downloader,
            config=config,
            course=course,
            hw=hw,
            console=console,
        )
        sync_homework_attachments(
            helper=helper,
            downloader=downloader,
            config=config,
            course=course,
            hw=hw,
            console=console,
        )


def sync_homework_detail(
    helper: Helper,
    downloader: Downloader,
    config: DictConfig,
    course: t.CourseInfo,
    hw: t.Homework,
    *,
    console: Console = Console(),
) -> None:
    prefix: Path = Path(
        config.get(key="prefix", default_value=DEFAULT_PREFIX)
    ).expanduser()
    title: str = f"{hw.number:02d}-{hw.title}"
    filepath: Path = prefix / course.english_name / "work" / title / "README.md"
    os.makedirs(filepath.parent, exist_ok=True)
    with open(file=filepath, mode="w") as fp:
        fp.write(utils.format_homework_readme(hw=hw))
        fp.flush()
    if shutil.which("prettier"):
        subprocess.run(args=["prettier", "--write", filepath], capture_output=True)
    console.log(
        SUCCESS_PREFIX,
        course.english_name,
        ">",
        title,
        style=HOMEWORK_STYLE,
    )


def sync_homework_attachments(
    helper: Helper,
    downloader: Downloader,
    config: DictConfig,
    course: t.CourseInfo,
    hw: t.Homework,
    *,
    console: Console = Console(),
) -> None:
    sync_homework_attachment(
        helper=helper,
        downloader=downloader,
        config=config,
        course=course,
        hw=hw,
        attach=hw.attachment,
        attach_type="attach",
        console=console,
    )
    sync_homework_attachment(
        helper=helper,
        downloader=downloader,
        config=config,
        course=course,
        hw=hw,
        attach=hw.answer_attachment,
        attach_type="ans",
        console=console,
    )
    sync_homework_attachment(
        helper=helper,
        downloader=downloader,
        config=config,
        course=course,
        hw=hw,
        attach=hw.submitted_attachment,
        attach_type="submit",
        console=console,
    )
    sync_homework_attachment(
        helper=helper,
        downloader=downloader,
        config=config,
        course=course,
        hw=hw,
        attach=hw.grade_attachment,
        attach_type="comment",
        console=console,
    )


def sync_homework_attachment(
    helper: Helper,
    downloader: Downloader,
    config: DictConfig,
    course: t.CourseInfo,
    hw: t.Homework,
    attach: Optional[t.RemoteFile],
    attach_type: str,
    *,
    console: Console = Console(),
) -> None:
    if not attach:
        return
    prefix: Path = Path(
        config.get(key="prefix", default_value=DEFAULT_PREFIX)
    ).expanduser()
    title: str = f"{hw.number:02d}-{hw.title}"
    filename: str = utils.remove_attachment_prefix(attach.name)
    filename: str = f"{attach_type}-{filename}"
    filepath: Path = prefix / course.english_name / "work" / title / filename
    upload_time: Optional[datetime] = None
    match attach_type:
        case "attach":
            upload_time = hw.starts_time
        case "ans":
            pass
        case "submit":
            upload_time = hw.submit_time
        case "comment":
            upload_time = hw.grade_time
    downloader.schedule_download(
        url=attach.download_url,
        output=filepath,
        session=helper,
        upload_time=upload_time,
        console=console,
        style=HOMEWORK_STYLE,
        description=utils.describe_work_file(
            course_name=course.english_name, hw_title=title, filename=filename
        ),
    )
