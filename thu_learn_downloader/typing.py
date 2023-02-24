import dataclasses
from datetime import datetime
from enum import StrEnum
from typing import Optional


class CourseType(StrEnum):
    STUDENT = "student"
    TEACHER = "teacher"


class SemesterSeason(StrEnum):
    FALL = "Autumn Term"
    SPRING = "Spring Term"
    SUMMER = "Summer Term"


@dataclasses.dataclass(kw_only=True)
class CourseInfo:
    id: str  # 网络课程 ID - wlkcid
    name: str  # 课程名 - kcm
    english_name: str  # 英文课程名 - ywkcm
    course_number: str  # 课程号 - kcm
    course_index: int  # 课序号 - kxh


@dataclasses.dataclass(kw_only=True)
class RemoteFile:
    id: str
    name: str
    download_url: str


@dataclasses.dataclass(kw_only=True)
class File:
    id: str  # 文件 ID - wjid
    raw_size: int  # 文件大小 - wjdx
    title: str  # 标题 - bt
    upload_time: datetime  # 上传时间 - scsj
    download_url: str
    file_type: str  # 文件类型 - wjlx
    file_clazz: str  # 课件分类 ID - kjflid


@dataclasses.dataclass(kw_only=True)
class HomeworkStatus:
    submitted: bool
    graded: bool


@dataclasses.dataclass(kw_only=True)
class HomeworkDetail:
    description: str = ""
    attachment: Optional[RemoteFile] = None
    answer_content: str = ""
    answer_attachment: Optional[RemoteFile] = None
    submitted_content: str = ""
    submitted_attachment: Optional[RemoteFile] = None
    # grade_content: str = ""  # 批阅内容 - pynr
    grade_attachment: Optional[RemoteFile] = None


@dataclasses.dataclass(kw_only=True)
class Homework(HomeworkStatus, HomeworkDetail):
    id: str  # 作业 ID - zyid
    student_homework_id: str  # 学生作业 ID - xszyid
    number: int  # - wz
    title: str  # 标题 - bt
    starts_time: Optional[datetime] = None  # 开始时间 - kssj
    deadline: Optional[datetime] = None  # 截止时间 - jzsj
    submit_time: Optional[datetime] = None  # 上传时间 - scsj
    grade: str = ""  # 成绩 - cj
    grade_time: Optional[datetime] = None  # 批阅时间 - pysj
    grader_name: str = ""  # 教师名 - jsm
    grade_content: str = ""  # 批阅内容 - pynr
