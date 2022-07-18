import dataclasses
import os

import tqdm
import tqdm.contrib
import tqdm.contrib.concurrent

import thu_learn_lib
import thu_learn_lib.ty
import thu_learn_lib.utils


@dataclasses.dataclass
class DownloadTask:
    session: "Downloader"
    url: str
    filename: str
    prefix: str = "."


class Downloader:
    helper: thu_learn_lib.LearnHelper
    prefix: str
    file_size_limit: float = None  # MB
    sync_docs: bool = True
    sync_work: bool = True
    sync_submit: bool = True
    download_tasks: list[DownloadTask] = None

    def __init__(
        self,
        username: str,
        password: str,
        prefix: str = "thu-learn",
        file_size_limit: float = None,
        sync_docs: bool = True,
        sync_work: bool = True,
        sync_submit: bool = True,
    ) -> None:
        self.helper = thu_learn_lib.LearnHelper(
            username=username,
            password=password,
        )
        self.prefix = prefix
        self.file_size_limit = file_size_limit
        self.sync_docs = sync_docs
        self.sync_work = sync_work
        self.sync_submit = sync_submit

        assert self.helper.login()

    @staticmethod
    def download(
        self: "Downloader",
        url: str,
        filename: str,
        prefix: str = ".",
        position: int = 0,
    ) -> bool:
        response = self.helper.get(url=url, stream=True)
        file_size = int(response.headers.get("content-length", 0))
        if self.file_size_limit:
            if file_size > self.file_size_limit * 1024 * 1024:
                print(f"Skip file {filename}")
                return False
        filename = thu_learn_lib.utils.slugify(filename)
        path = os.path.join(prefix, filename)
        if os.path.exists(path):
            if os.path.getsize(path) == file_size:
                # print(f"file {filename} is already synced")
                return True
        os.makedirs(prefix, exist_ok=True)
        chunk_size = 8192  # 8KB
        try:
            with open(
                file=os.path.join(prefix, filename),
                mode="wb",
            ) as file:
                list(
                    tqdm.contrib.tmap(
                        file.write,
                        response.iter_content(chunk_size),
                        desc=f"{position - 6} {filename}",
                        total=file_size,
                        leave=False,
                        unit="B",
                        unit_scale=True,
                        dynamic_ncols=True,
                        position=position,
                    )
                )
                pass
        except KeyboardInterrupt:
            raise KeyboardInterrupt()
        except:
            return False
        return True

    @staticmethod
    def retry_download(
        task: DownloadTask,
        position: int = 0,
        max_retries: int = 5,
    ) -> bool:
        for i in range(max_retries):
            if Downloader.download(
                self=task.session,
                url=task.url,
                filename=task.filename,
                prefix=task.prefix,
                position=position,
            ):
                return True
        print(f"Failed to download file {task.filename}")
        return False

    def schedule_download(
        self,
        url: str,
        filename: str,
        prefix: str = ".",
    ) -> None:
        if not self.download_tasks:
            self.download_tasks = []
        self.download_tasks.append(
            DownloadTask(
                session=self,
                url=url,
                filename=filename,
                prefix=prefix,
            )
        )

    def finish_download(self, desc: str = "download") -> bool:
        if self.download_tasks:
            success = all(
                tqdm.contrib.concurrent.process_map(
                    Downloader.retry_download,
                    self.download_tasks,
                    range(6, 6 + len(self.download_tasks)),
                    desc=desc,
                    leave=False,
                    dynamic_ncols=True,
                    position=4,
                )
            )
            self.download_tasks.clear()
            return success
        else:
            return True

    def sync_semester(
        self,
        semester_id: str,
        course_type: thu_learn_lib.ty.CourseType = thu_learn_lib.ty.CourseType.STUDENT,
    ) -> bool:
        course_list = self.helper.get_course_list(
            semester_id=semester_id,
            course_type=course_type,
        )
        for course in tqdm.tqdm(
            iterable=course_list,
            desc=semester_id,
            leave=False,
            dynamic_ncols=True,
            position=2,
        ):
            self.sync_course(course=course, semester_id=semester_id)

    def sync_course(
        self,
        course: thu_learn_lib.ty.CourseInfo,
        semester_id: str,
    ) -> bool:
        file_list = self.helper.get_file_list(
            course_id=course.id,
            course_type=course.course_type,
        )
        # print(
        #     f"Syncing Course {course.course_number} {course.name} {course.english_name} ......"
        # )
        if self.sync_docs:
            pass
        if self.sync_docs:
            for file in file_list:
                self.sync_file(file, semester_id=semester_id, course=course)
            self.finish_download(desc=course.english_name)
        if self.sync_work:
            homework_list = self.helper.get_homework_list(course_id=course.id)
            for homework in homework_list:
                self.sync_homework(
                    homework=homework, semester_id=semester_id, course=course
                )
            self.finish_download(desc=course.english_name)

    def sync_file(
        self,
        file: thu_learn_lib.ty.File,
        semester_id: str,
        course: thu_learn_lib.ty.CourseInfo,
    ) -> bool:
        prefix = os.path.join(
            self.prefix,
            thu_learn_lib.utils.slugify(course.english_name),
            thu_learn_lib.utils.slugify("documents"),
            thu_learn_lib.utils.slugify(file.clazz),
        )
        filename = (
            thu_learn_lib.utils.slugify(file.title)
            + f".{thu_learn_lib.utils.slugify(file.file_type)}"
            if file.file_type
            else ""
        )
        self.schedule_download(
            url=file.download_url,
            filename=filename,
            prefix=prefix,
        )
        return True

    def sync_homework(
        self,
        homework: thu_learn_lib.ty.Homework,
        semester_id: str,
        course: thu_learn_lib.ty.CourseInfo,
    ) -> bool:
        prefix = os.path.join(
            thu_learn_lib.utils.slugify(self.prefix),
            thu_learn_lib.utils.slugify(course.english_name),
            thu_learn_lib.utils.slugify("work"),
            thu_learn_lib.utils.slugify(homework.title),
        )
        os.makedirs(prefix, exist_ok=True)
        lines = []
        lines.append(f"## Contents and Requirements")
        lines.append(f"")
        lines.append(f"### Title")
        lines.append(f"")
        lines.append(f"{homework.title}")
        lines.append(f"")
        lines.append(f"### Description")
        lines.append(f"")
        lines.append(f"{homework.description}")
        lines.append(f"")
        if homework.attachment:
            filename = thu_learn_lib.utils.slugify(
                f"attach-{homework.title}{os.path.splitext(homework.attachment.name)[-1]}"
            )
            self.schedule_download(
                url=homework.attachment.download_url,
                prefix=prefix,
                filename=filename,
            )
            lines.append(f"### Attach.")
            lines.append(f"")
            lines.append(f"[{homework.attachment.name}]({filename})")
            lines.append(f"")
        lines.append(f"### ANS")
        lines.append(f"")
        lines.append(f"{homework.answer_content}")
        lines.append(f"")
        if homework.answer_attachment:
            filename = thu_learn_lib.utils.slugify(
                f"ans-{homework.title}{os.path.splitext(homework.answer_attachment.name)[-1]}"
            )
            self.schedule_download(
                url=homework.answer_attachment.download_url,
                prefix=prefix,
                filename=filename,
            )
            lines.append(f"### Attach.")
            lines.append(f"")
            lines.append(f"[{homework.answer_attachment.name}]({filename})")
            lines.append(f"")
        lines.append(f"### Deadline (GMT+8)")
        lines.append(f"")
        lines.append(f"{homework.deadline.isoformat() if homework.deadline else None}")
        lines.append(f"")
        if self.sync_submit:
            lines.append(f"## My coursework submitted")
            lines.append(f"")
            lines.append(f"### Content")
            lines.append(f"")
            lines.append(f"{homework.submitted_content}")
            lines.append(f"")
            if homework.submitted_attachment:
                filename = thu_learn_lib.utils.slugify(
                    f"submit-{homework.title}{os.path.splitext(homework.submitted_attachment.name)[-1]}"
                )
                self.schedule_download(
                    url=homework.submitted_attachment.download_url,
                    prefix=prefix,
                    filename=filename,
                )
                lines.append(f"### Attach.")
                lines.append(f"")
                lines.append(f"[{homework.submitted_attachment.name}]({filename})")
                lines.append(f"")
            lines.append(f"## Instructors' comments")
            lines.append(f"")
            lines.append(f"### By")
            lines.append(f"")
            lines.append(f"{homework.grader_name}")
            lines.append(f"")
            lines.append(f"### Date")
            lines.append(f"")
            lines.append(
                f"{homework.grade_time.isoformat() if homework.grade_time else None}"
            )
            lines.append(f"")
            lines.append(f"### Grade")
            lines.append(f"")
            lines.append(f"{homework.grade}")
            lines.append(f"")
            lines.append(f"### Comment")
            lines.append(f"")
            lines.append(f"{homework.grade_content}")
            lines.append(f"")
            if homework.grade_attachment:
                filename = thu_learn_lib.utils.slugify(
                    f"comment-{homework.title}{os.path.splitext(homework.grade_attachment.name)[-1]}"
                )
                self.schedule_download(
                    url=homework.grade_attachment.download_url,
                    prefix=prefix,
                    filename=filename,
                )
                lines.append(f"### Attach.")
                lines.append(f"")
                lines.append(f"[{homework.grade_attachment.name}]({filename})")
                lines.append(f"")
        lines = [line + "\n" for line in lines]
        filename = thu_learn_lib.utils.slugify("README.md")
        with open(os.path.join(prefix, filename), "w") as file:
            file.writelines(lines)
