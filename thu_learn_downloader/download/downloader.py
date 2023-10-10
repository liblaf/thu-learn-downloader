import logging
import os
from collections.abc import Sequence
from concurrent.futures import Executor, ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Optional, Self

import dateutil.parser
import tenacity
from requests import Response
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    MofNCompleteColumn,
    Progress,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.style import Style, StyleType

from thu_learn_downloader.client.client import Client
from thu_learn_downloader.client.course import Course
from thu_learn_downloader.client.document import Document, DocumentClass
from thu_learn_downloader.client.homework import Attachment, Homework
from thu_learn_downloader.client.semester import Semester

from . import description, filename, style
from .selector import Selector


class Downloader:
    prefix: Path
    selector: Selector

    executor: Executor

    live: Live
    semesters_task_id: TaskID
    courses_task_id: TaskID
    documents_task_id: TaskID

    def __init__(
        self,
        prefix: Path = Path.home() / "thu-learn",
        selector: Selector = Selector(),
        jobs: int = 8,
    ) -> None:
        self.prefix = prefix
        self.selector = selector
        self.executor = ThreadPoolExecutor(max_workers=jobs)

        self.progress_prepare = Progress(
            TextColumn("{task.description}", style="bold bright_blue"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
        )
        self.progress_download = Progress(
            TextColumn("{task.description}", style="bold"),
            BarColumn(),
            DownloadColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            TransferSpeedColumn(),
        )
        self.semesters_task_id = self.progress_prepare.add_task(description="Semesters")
        self.courses_task_id = self.progress_prepare.add_task(description="Courses")
        self.documents_task_id = self.progress_prepare.add_task(description="Documents")
        self.live = Live(
            Group(
                Panel(self.progress_download, height=jobs + 2),
                Panel(self.progress_prepare),
            )
        )

    def __enter__(self) -> Self:
        self.live.__enter__()
        self.executor.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.executor.__exit__(exc_type, exc_val, exc_tb)
        self.live.__exit__(exc_type, exc_val, exc_tb)

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(max_attempt_number=4),
        before_sleep=tenacity.before_sleep_log(logging.getLogger(), logging.DEBUG),
    )
    def download(
        self,
        client: Client,
        url: str,
        output: Path,
        *,
        task_id: TaskID,
    ) -> None:
        self.progress_download.update(task_id=task_id, visible=True)
        response: Response = client.get(url=url, stream=True)
        os.makedirs(name=output.parent, exist_ok=True)
        with output.open(mode="wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                bytes_written: int = file.write(chunk)
                self.progress_download.advance(task_id=task_id, advance=bytes_written)
        self.progress_download.update(task_id=task_id, visible=False)

    def do_sync_file(
        self,
        client: Client,
        url: str,
        output: Path,
        description: str,
        *,
        remote_size: Optional[int] = None,
        remote_time: Optional[datetime] = None,
        style: StyleType = Style(),
    ) -> None:
        if remote_size is None or remote_time is None:
            response: Response = client.get(url=url, stream=True)
            if remote_size is None:
                try:
                    remote_size = int(response.headers["Content-Length"])
                except:
                    remote_size = None
            if remote_time is None:
                try:
                    remote_time = dateutil.parser.parse(response.headers["Date"])
                except:
                    remote_time = None
        if remote_size is not None:
            if output.exists() and output.stat().st_size == remote_size:
                if not isinstance(style, Style):
                    style = Style.parse(style)
                self.live.console.log(
                    "[reverse] SKIPPED [/]", description, style=style + Style(dim=True)
                )
                return
        task_id: TaskID = self.progress_download.add_task(
            description=description, total=remote_size
        )
        self.download(client=client, url=url, output=output, task_id=task_id)
        if remote_time:
            os.utime(
                path=output, times=(remote_time.timestamp(), remote_time.timestamp())
            )
        self.live.console.log("[reverse] SUCCESS [/]", description, style=style)

    def sync_file(
        self,
        client: Client,
        url: str,
        output: Path,
        description: str,
        *,
        remote_size: Optional[int] = None,
        remote_time: Optional[datetime] = None,
        style: StyleType = Style(),
    ) -> None:
        self.executor.submit(
            self.do_sync_file,
            client=client,
            url=url,
            output=output,
            description=description,
            remote_size=remote_size,
            remote_time=remote_time,
            style=style,
        )

    def sync_semesters(self, semesters: Sequence[Semester]) -> None:
        if self.selector.semesters:
            semesters = [
                semester
                for semester in semesters
                if semester.id in self.selector.semesters
            ]
        self.progress_prepare.reset(task_id=self.semesters_task_id)
        for semester in self.progress_prepare.track(
            sequence=semesters,
            total=len(semesters),
            task_id=self.semesters_task_id,
            description="Semesters",
        ):
            self.sync_semester(semester=semester)

    def sync_semester(self, semester: Semester) -> None:
        self.sync_courses(semester=semester, courses=semester.courses)

    def sync_courses(self, semester: Semester, courses: Sequence[Course]) -> None:
        if self.selector.courses:
            courses = [
                course for course in courses if course.id in self.selector.courses
            ]
        self.progress_prepare.reset(task_id=self.courses_task_id)
        for course in self.progress_prepare.track(
            sequence=courses,
            total=len(courses),
            task_id=self.courses_task_id,
            description="Courses",
        ):
            self.sync_course(semester=semester, course=course)

    def sync_course(self, semester: Semester, course: Course) -> None:
        if self.selector.document:
            self.sync_documents(
                semester=semester,
                course=course,
                document_classes=course.document_classes,
                documents=course.documents,
            )
        if self.selector.homework:
            self.sync_homeworks(
                semester=semester, course=course, homeworks=course.homeworks
            )

    def sync_documents(
        self,
        semester: Semester,
        course: Course,
        document_classes: Sequence[DocumentClass],
        documents: Sequence[Document],
    ) -> None:
        document_class_map: dict[str, DocumentClass] = {
            document_class.id: document_class for document_class in document_classes
        }
        self.progress_prepare.reset(task_id=self.documents_task_id)
        for index, document in enumerate(
            self.progress_prepare.track(
                sequence=documents,
                total=len(documents),
                task_id=self.documents_task_id,
                description="Documents",
            )
        ):
            self.sync_document(
                semester=semester,
                course=course,
                document_class=document_class_map[document.class_id],
                document=document,
                index=index,
            )

    def sync_document(
        self,
        semester: Semester,
        course: Course,
        document_class: DocumentClass,
        document: Document,
        index: int,
    ) -> None:
        self.sync_file(
            client=document.client,
            url=document.download_url,
            output=filename.document(
                prefix=self.prefix,
                semester=semester,
                course=course,
                document_class=document_class,
                document=document,
                index=index,
            ),
            description=description.document(
                semester=semester,
                course=course,
                document_class=document_class,
                document=document,
                index=index,
            ),
            remote_size=document.size,
            remote_time=document.upload_time,
            style=style.DOCUMENT,
        )

    def sync_homeworks(
        self, semester: Semester, course: Course, homeworks: Sequence[Homework]
    ) -> None:
        self.progress_prepare.reset(task_id=self.documents_task_id)
        for homework in self.progress_prepare.track(
            sequence=homeworks,
            total=len(homeworks),
            task_id=self.documents_task_id,
            description="Homeworks",
        ):
            self.sync_homework(semester=semester, course=course, homework=homework)

    def sync_homework(
        self, semester: Semester, course: Course, homework: Homework
    ) -> None:
        readme_path: Path = filename.homework(
            prefix=self.prefix, semester=semester, course=course, homework=homework
        )
        os.makedirs(readme_path.parent, exist_ok=True)
        readme_path.write_text(homework.markdown)
        for attachment in homework.attachments:
            self.sync_file(
                client=homework.client,
                url=attachment.download_url,
                output=filename.attachment(
                    prefix=self.prefix,
                    semester=semester,
                    course=course,
                    homework=homework,
                    attachment=attachment,
                ),
                description=description.attachment(
                    semester=semester,
                    course=course,
                    homework=homework,
                    attachment=attachment,
                ),
                style=style.HOMEWORK,
            )
