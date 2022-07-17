import os
from tqdm import tqdm


from thu_learn_lib import LearnHelper
from thu_learn_lib import ty as types
from thu_learn_lib.utils import slugify


class Downloader(LearnHelper):
    prefix: str = ""
    file_size_limit: int = None # MB
    sync_docs: bool = True
    sync_work: bool = True
    sync_submit: bool = True

    def __init__(
        self,
        prefix: str = "",
        file_size_limit: int = None,
        sync_docs: bool = True,
        sync_work: bool = True,
        sync_submit: bool = True,
    ) -> None:
        super().__init__()
        if prefix:
            self.prefix = prefix
        else:
            self.prefix = os.path.join(os.getcwd(), slugify("learn"))
        self.file_size_limit = file_size_limit
        self.sync_docs = sync_docs
        self.sync_work = sync_work
        self.sync_submit = sync_submit

    def Download(self, url: str, prefix: str, filename: str) -> bool:
        os.makedirs(prefix, exist_ok=True)
        response = self.get(url=url, stream=True)
        file_size = int(response.headers.get("content-length", 0))
        if self.file_size_limit:
            if file_size > self.file_size_limit * 1024 * 1024:
                print(f"Skipping file {filename}")
                return False
        filename = slugify(filename)
        chunk_size = 8192  # 8KB
        with tqdm(
            desc=filename,
            total=file_size,
            unit="B",
            ascii=True,
            unit_scale=True,
            dynamic_ncols=True,
        ) as bar:
            with open(os.path.join(prefix, filename), "wb") as file:
                for chunck in response.iter_content(chunk_size):
                    file.write(chunck)
                    bar.update(len(chunck))
        return True

    def SyncSemester(
        self, semester_id: str, course_type: types.CourseType = types.CourseType.STUDENT
    ) -> bool:
        print(f"Syncing Semester {semester_id} ......")
        course_list = self.get_course_list(
            semester_id=semester_id, course_type=course_type
        )
        for course in course_list:
            self.SyncCourse(
                course=course, semester_id=semester_id,
            )

    def SyncCourse(self, course: types.CourseInfo, semester_id: str) -> bool:
        file_list = self.get_file_list(
            course_id=course.id, course_type=course.course_type
        )
        print(
            f"Syncing Course {course.course_number} {course.name} {course.english_name} ......"
        )
        if self.sync_docs:
            for file in file_list:
                self.SyncFile(file, semester_id=semester_id, course=course)
        if self.sync_work:
            homework_list = self.get_homework_list(course_id=course.id)
            for homework in homework_list:
                self.SyncHomework(
                    homework=homework, semester_id=semester_id, course=course
                )

    def SyncFile(
        self, file: types.File, semester_id: str, course: types.CourseInfo
    ) -> bool:
        prefix = os.path.join(
            self.prefix,
            slugify(course.english_name),
            slugify("documents"),
            slugify(file.clazz),
        )
        filename = slugify(file.title) + slugify(
            f".{file.file_type}" if file.file_type else ""
        )
        self.Download(url=file.download_url, prefix=prefix, filename=filename)
        return True

    def SyncHomework(
        self, homework: types.Homework, semester_id: str, course: types.CourseInfo
    ) -> bool:
        prefix = os.path.join(
            self.prefix,
            slugify(course.english_name),
            slugify("work"),
            slugify(homework.title),
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
            filename = slugify(
                f"attach-{homework.title}{os.path.splitext(homework.attachment.name)[-1]}"
            )
            self.Download(
                url=homework.attachment.download_url, prefix=prefix, filename=filename,
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
            filename = slugify(
                f"ans-{homework.title}{os.path.splitext(homework.answer_attachment.name)[-1]}"
            )
            self.Download(
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
                filename = slugify(
                    f"submit-{homework.title}{os.path.splitext(homework.submitted_attachment.name)[-1]}"
                )
                self.Download(
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
                filename = slugify(
                    f"comment-{homework.title}{os.path.splitext(homework.grade_attachment.name)[-1]}"
                )
                self.Download(
                    url=homework.grade_attachment.download_url,
                    prefix=prefix,
                    filename=filename,
                )
                lines.append(f"### Attach.")
                lines.append(f"")
                lines.append(f"[{homework.grade_attachment.name}]({filename})")
                lines.append(f"")
        lines = [line + "\n" for line in lines]
        filename = slugify("README.md")
        with open(os.path.join(prefix, filename), "w") as file:
            file.writelines(lines)
