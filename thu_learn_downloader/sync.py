import os
import shutil
import sys
import typing

import omegaconf
import rich.console
import rich.progress

from . import readme, types, utils
from .downloader import Downloader
from .helper import LearnHelper


def sync_all(
    helper: LearnHelper,
    downloader: Downloader,
    config: omegaconf.DictConfig,
    console: rich.console.Console = rich.console.Console(),
    overall_progress: rich.progress.Progress = rich.progress.Progress(),
    semesters_task_id: rich.progress.TaskID = rich.progress.TaskID(0),
    courses_task_id: rich.progress.TaskID = rich.progress.TaskID(1),
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
    helper: LearnHelper,
    downloader: Downloader,
    semester_id: str,
    config: omegaconf.DictConfig,
    console: rich.console.Console = rich.console.Console(),
    overall_progress: rich.progress.Progress = rich.progress.Progress(),
    courses_task_id: rich.progress.TaskID = rich.progress.TaskID(1),
):
    courses = helper.get_course_list(semester_id=semester_id)
    if config.get("courses"):
        courses = [
            course
            for course in courses
            if (
                (course.name in config["courses"])
                or (course.english_name in config["courses"])
            )
        ]
    overall_progress.update(
        task_id=courses_task_id,
        description=f"{semester_id[:-2]} {utils.parse_semester_type(int(semester_id[-1])).value}",
    )
    for course in overall_progress.track(
        courses, task_id=courses_task_id, description=semester_id
    ):
        sync_course(
            helper=helper,
            downloader=downloader,
            course=course,
            config=config,
            console=console,
        )


def sync_course(
    helper: LearnHelper,
    downloader: Downloader,
    course: types.CourseInfo,
    config: omegaconf.DictConfig,
    console: rich.console.Console = rich.console.Console(),
):
    sync_files(
        helper=helper,
        downloader=downloader,
        course=course,
        config=config,
        console=console,
    )
    sync_works(
        helper=helper,
        downloader=downloader,
        course=course,
        config=config,
        console=console,
    )


def sync_files(
    helper: LearnHelper,
    downloader: Downloader,
    course: types.CourseInfo,
    config: omegaconf.DictConfig,
    console: rich.console.Console = rich.console.Console(),
):
    prefix = config.get(
        key="prefix", default_value=os.path.join(os.getcwd(), "thu-learn")
    )
    file_size_limit = config.get(key="file_size_limit") or sys.maxsize
    files = helper.get_file_list(course_id=course.id, course_type=course.course_type)
    for file in files:
        if file.raw_size >= file_size_limit:
            console.log(
                f"Skip {file.remote_file.name} of size {file.size}",
                style="bold bright_yellow",
            )
            continue
        downloader.schedule_download(
            url=file.remote_file.download_url,
            file=os.path.join(
                prefix,
                utils.slugify(course.english_name),
                "docs",
                utils.slugify(file.clazz),
                utils.slugify(f"{file.remote_file.name}.{file.file_type}"),
            ),
            raw_size=file.raw_size,
            upload_time=file.upload_time,
            session=helper,
            description=f"[bold bright_green]{course.name} > {file.remote_file.name}",
            console=console,
        )


def sync_works(
    helper: LearnHelper,
    downloader: Downloader,
    course: types.CourseInfo,
    config: omegaconf.DictConfig,
    console: rich.console.Console = rich.console.Console(),
):
    prefix = config.get(
        key="prefix", default_value=os.path.join(os.getcwd(), "thu-learn")
    )
    works = helper.get_homework_list(
        course_id=course.id, course_type=course.course_type
    )
    for work in works:
        sync_work_detail(course=course, work=work, config=config, console=console)

        def sync_attach(
            attachment: typing.Optional[types.RemoteFile],
            attachment_type: typing.Literal["attach"]
            | typing.Literal["ans"]
            | typing.Literal["submit"]
            | typing.Literal["comment"],
        ) -> None:
            sync_work_attachment(
                helper=helper,
                downloader=downloader,
                course=course,
                work=work,
                attachment=attachment,
                attachment_type=attachment_type,
                config=config,
                console=console,
            )

        sync_attach(work.attachment, "attach")
        sync_attach(work.answer_attachment, "ans")
        sync_attach(work.submitted_attachment, "submit")
        sync_attach(work.grade_attachment, "comment")


def sync_work_detail(
    course: types.CourseInfo,
    work: types.Homework,
    config: omegaconf.DictConfig,
    console: rich.console.Console = rich.console.Console(),
):
    prefix = config.get(
        key="prefix", default_value=os.path.join(os.getcwd(), "thu-learn")
    )
    file = os.path.join(
        prefix,
        utils.slugify(course.english_name),
        "work",
        utils.slugify(work.title),
        "README.md",
    )
    os.makedirs(name=os.path.dirname(file), exist_ok=True)
    with open(file=file, mode="w") as fp:
        fp.write(readme.dump_work(work))
    if shutil.which(cmd="prettier"):
        os.system(f"prettier --write {file} > /dev/null")


def sync_work_attachment(
    helper: LearnHelper,
    downloader: Downloader,
    course: types.CourseInfo,
    work: types.Homework,
    attachment: typing.Optional[types.RemoteFile],
    attachment_type: typing.Literal["attach"]
    | typing.Literal["ans"]
    | typing.Literal["submit"]
    | typing.Literal["comment"],
    config: omegaconf.DictConfig,
    console: rich.console.Console = rich.console.Console(),
) -> None:
    prefix = config.get(
        key="prefix", default_value=os.path.join(os.getcwd(), "thu-learn")
    )
    if attachment:
        title = attachment.name
        for p in ["attach", "ans", "submit", "comment"]:
            title = title.removeprefix(p + "-")
        title = attachment_type + "-" + title
        upload_time = None
        if attachment_type == "submit":
            upload_time = work.submit_time
        elif attachment_type == "comment":
            upload_time = work.grade_time
        else:
            upload_time = None
        downloader.schedule_download(
            url=attachment.download_url,
            file=os.path.join(
                prefix,
                utils.slugify(course.english_name),
                "work",
                utils.slugify(work.title),
                utils.slugify(title),
            ),
            upload_time=upload_time,
            session=helper,
            console=console,
            description=f"[bold bright_blue]{course.name} > {title}",
        )
