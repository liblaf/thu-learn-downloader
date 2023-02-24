import dataclasses
from datetime import datetime
from typing import Any, Optional

from . import typing as t
from .constants import HOMEWORK_README, SEASONS


def format_semester_id(semester_id: str) -> str:
    years: str = semester_id[:-2]
    season: t.SemesterSeason = SEASONS[int(semester_id[-1:])]
    return f"{years} {season.value}"


def format_doc_filename(title: str, file_type: str) -> str:
    if file_type:
        return f"{title}.{file_type}"
    else:
        return title


def describe_doc_file(course_name: str, filename: str) -> str:
    return f"{course_name} > {filename}"


def describe_work_file(course_name: str, hw_title: str, filename: str) -> str:
    return f"{course_name} > {hw_title} > {filename}"


def from_timestamp(t: Optional[float]) -> Optional[datetime]:
    if not t:
        return None
    return datetime.fromtimestamp(t / 1000.0)


def dataclass_as_dict_shallow(obj: Any) -> dict[str, Any]:
    return dict(
        (field.name, getattr(obj, field.name)) for field in dataclasses.fields(obj)
    )


def remove_attachment_prefix(name: str) -> str:
    prefixes: list[str] = ["attach", "ans", "submit", "comment", "-"]
    while name.startswith(tuple(prefixes)):
        for p in prefixes:
            name = name.removeprefix(p)
    return name


def format_homework_readme(hw: t.Homework) -> str:
    return HOMEWORK_README.format(
        title=hw.title,
        starts=str(hw.starts_time or ""),
        deadline=str(hw.deadline or ""),
        description=hw.description or "",
        ans=hw.answer_content or "",
        submit_time=str(hw.submit_time or ""),
        submit_content=hw.submitted_content or "",
        grader_name=hw.grader_name or "",
        grade_time=str(hw.grade_time or ""),
        grade=hw.grade,
        comment=hw.grade_content,
    )
