from pathlib import Path

from thu_learn_downloader.client.course import Course
from thu_learn_downloader.client.document import Document, DocumentClass
from thu_learn_downloader.client.homework import Attachment, Homework
from thu_learn_downloader.client.semester import Semester


def document(
    prefix: Path,
    semester: Semester,
    course: Course,
    document_class: DocumentClass,
    document: Document,
    index: int,
) -> Path:
    filename: Path = (
        prefix
        / semester.id
        / course.name
        / "docs"
        / document_class.title
        / f"{index:02d}-{document.title}"
    )
    if document.file_type:
        filename = filename.with_suffix("." + document.file_type)
    return filename


def homework(
    prefix: Path, semester: Semester, course: Course, homework: Homework
) -> Path:
    return (
        prefix
        / semester.id
        / course.name
        / "work"
        / f"{homework.number:02d}-{homework.title}"
        / "README.md"
    )


def attachment(
    prefix: Path,
    semester: Semester,
    course: Course,
    homework: Homework,
    attachment: Attachment,
) -> Path:
    filename: Path = Path(attachment.name)
    filename = filename.with_stem(f"{attachment.type_}-{homework.title}")
    return (
        prefix
        / semester.id
        / course.name
        / "work"
        / f"{homework.number:02d}-{homework.title}"
        / filename
    )
