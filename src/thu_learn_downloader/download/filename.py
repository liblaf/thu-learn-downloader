import re
from pathlib import Path

from thu_learn_downloader.client.course import Course
from thu_learn_downloader.client.document import Document, DocumentClass
from thu_learn_downloader.client.homework import Attachment, Homework
from thu_learn_downloader.client.semester import Semester


def sanitize_filename(filename: str) -> str:
    """输入： 文件名
    输出： 清理无效字符后的文件名，避免程序出错
    """
    # 定义Windows不允许的字符
    invalid_chars = r'[<>:"|?*\\]'

    # 替换无效字符为下划线
    filename = re.sub(invalid_chars, "_", filename)

    # 移除控制字符（ASCII 0-31）
    filename = re.sub(r"[\x00-\x1f]", "", filename)

    # 移除开头和结尾的空格和点号
    filename = filename.strip(" .")

    # 如果文件名为空或只包含无效字符，使用默认名称
    if not filename:
        filename = "untitled"

    return filename


def document(
    prefix: Path,
    semester: Semester,
    course: Course,
    document_class: DocumentClass,
    document: Document,
    index: int,
) -> Path:
    # 清理文件名中的无效字符
    course_name = sanitize_filename(course.name)
    doc_class_title = sanitize_filename(document_class.title)
    doc_title = sanitize_filename(document.title)

    filename: Path = (
        prefix
        / semester.id
        / course_name
        / "docs"
        / doc_class_title
        / f"{index:02d}-{doc_title}"
    )
    if document.file_type:
        filename = filename.with_suffix("." + document.file_type)
    return filename


def homework(
    prefix: Path, semester: Semester, course: Course, homework: Homework
) -> Path:
    # 清理文件名中的无效字符
    course_name = sanitize_filename(course.name)
    homework_title = sanitize_filename(homework.title)

    return (
        prefix
        / semester.id
        / course_name
        / "work"
        / f"{homework.number:02d}-{homework_title}"
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
    filename = filename.with_stem(
        f"{homework.number:02d}-{homework.title}-{attachment.type_}".replace(
            "/", "-slash-"
        )
    )
    return (
        prefix
        / semester.id
        / course.name
        / "work"
        / f"{homework.number:02d}-{homework.title}".replace("/", "-slash-")
        / filename
    )
