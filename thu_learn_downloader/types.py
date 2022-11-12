import dataclasses
import datetime
import enum
import os
import typing
import urllib.parse


@dataclasses.dataclass(kw_only=True)
class URL:
    scheme: str = "https"
    netloc: str = ""
    path: str = ""
    params: str = ""
    query: str | dict | list = ""
    fragment: str = ""

    def __str__(self) -> str:
        return urllib.parse.urlunparse(self.astuple())

    def str(self) -> str:
        return str(self)

    def astuple(self) -> urllib.parse.ParseResult:
        return urllib.parse.ParseResult(
            scheme=self.scheme,
            netloc=self.netloc,
            path=os.path.join(self.path) if isinstance(self.path, list) else self.path,
            params=self.params,
            query=self.query
            if isinstance(self.query, str)
            else urllib.parse.urlencode(self.query, doseq=True),
            fragment=self.fragment,
        )


@dataclasses.dataclass(kw_only=True)
class Credential:
    username: str
    password: str


class FailReason(enum.Enum):
    NO_CREDENTIAL = "no credential provided"
    ERROR_FETCH_FROM_ID = "could not fetch ticket from id.tsinghua.edu.cn"
    BAD_CREDENTIAL = "bad credential"
    ERROR_ROAMING = "could not roam to learn.tsinghua.edu.cn"
    NOT_LOGGED_IN = "not logged in or login timeout"
    NOT_IMPLEMENTED = "not implemented"
    INVALID_RESPONSE = "invalid response"
    UNEXPECTED_STATUS = "unexpected status"


@dataclasses.dataclass(kw_only=True)
class APIError:
    reason: FailReason
    extra = None


class SemesterType(enum.Enum):
    FALL = "Autumn Term"
    SPRING = "Spring Term"
    SUMMER = "Summer Term"
    UNKNOWN = ""


class ContentType(enum.Enum):
    NOTIFICATION = "notification"
    FILE = "file"
    HOMEWORK = "homework"
    DISCUSSION = "discussion"
    QUESTION = "question"


@dataclasses.dataclass(kw_only=True)
class SemesterInfo:
    id: str
    start_date: datetime.date
    end_date: datetime.date
    start_year: int
    end_year: int
    type: SemesterType


class CourseType(enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"


@dataclasses.dataclass(kw_only=True)
class CourseInfo:
    id: str
    name: str
    english_name: str
    time_and_location: typing.Optional[list[str]] = None
    url: str
    teacher_name: str
    teacher_number: str
    course_number: str
    course_index: int
    course_type: CourseType


@dataclasses.dataclass(kw_only=True)
class RemoteFile:
    id: str
    name: str
    download_url: str
    preview_url: typing.Optional[str] = None
    size: str


@dataclasses.dataclass(kw_only=True)
class Notification:
    id: str
    title: str
    content: str
    has_read: bool
    url: str
    marked_important: bool
    publish_time: datetime.datetime
    publisher: str

    # notification detail
    attachment: typing.Optional[RemoteFile] = None


@dataclasses.dataclass(kw_only=True)
class File:
    id: str
    raw_size: int  # size in byte
    size: str  # inaccurate size description (like '1M')
    title: str
    description: str
    upload_time: datetime.datetime
    download_url: str  # for teachers, this url will not initiate download directly
    preview_url: str  # preview is not supported on all types of files, check before use
    is_new: bool
    marked_important: bool
    visit_count: int
    download_count: int
    file_type: str
    remote_file: RemoteFile  # for compatibility

    clazz: str


@dataclasses.dataclass(kw_only=True)
class HomeworkStatus:
    submitted: bool
    graded: bool


@dataclasses.dataclass(kw_only=True)
class HomeworkDetail:
    description: typing.Optional[str] = None
    attachment: typing.Optional[RemoteFile] = None  # attachment from teacher
    answer_content: typing.Optional[str] = None  # answer from teacher
    answer_attachment: typing.Optional[RemoteFile] = None
    submitted_content: typing.Optional[str] = None  # submitted content from student
    submitted_attachment: typing.Optional[RemoteFile] = None
    grade_content: typing.Optional[str] = None
    grade_attachment: typing.Optional[RemoteFile] = None  # grade from teacher


@dataclasses.dataclass(kw_only=True)
class Homework(HomeworkStatus, HomeworkDetail):
    id: str
    student_homework_id: str
    title: str
    deadline: typing.Optional[datetime.datetime]
    url: str
    submit_url: str
    submit_time: typing.Optional[datetime.datetime] = None
    grade: typing.Optional[int] = None
    # some homework has levels but not grades, like A/B/.../F
    grade_level: typing.Optional[str] = None
    grade_time: typing.Optional[datetime.datetime] = None
    grader_name: typing.Optional[str] = None


@dataclasses.dataclass(kw_only=True)
class DiscussionBase:
    id: str
    title: str
    publisher_name: str
    publish_date: datetime.datetime
    last_replier_name: str
    last_reply_time: datetime.datetime
    visit_count: int
    reply_count: int


@dataclasses.dataclass(kw_only=True)
class Discussion(DiscussionBase):
    url: str
    board_id: str


@dataclasses.dataclass(kw_only=True)
class Question(DiscussionBase):
    url: str
    question: str


Content = Notification | File | Homework | Discussion | Question


@dataclasses.dataclass(kw_only=True)
class CalendarEvent:
    location: str
    status: str
    start_time: str
    end_time: str
    date: str
    course_name: str
