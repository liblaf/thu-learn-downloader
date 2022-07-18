import dataclasses
import datetime
import enum
import os
import urllib.parse


@dataclasses.dataclass
class URL:
    scheme: str = "https"
    netloc: str = ""
    path: str = ""
    params: str = ""
    query: str | dict[str, str | list[str]] | list[tuple[str, str | list[str]]] = ""
    fragment: str = ""

    def __str__(self) -> str:
        return urllib.parse.urlunparse(self.astuple())

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


@dataclasses.dataclass
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


@dataclasses.dataclass
class SemesterInfo:
    id: str
    start_date: datetime.datetime
    end_date: datetime.datetime
    start_year: int
    end_year: int
    type: SemesterType


class CourseType(enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"


@dataclasses.dataclass
class CourseInfo:
    id: str = None
    name: str = None
    english_name: str = None
    time_and_location: list[str] = None
    url: str = None
    teacher_name: str = None
    teacher_number: str = None
    course_number: str = None
    course_index: int = None
    course_type: CourseType = None


@dataclasses.dataclass
class RemoteFile:
    id: str
    name: str
    download_url: str
    preview_url: str
    size: str


@dataclasses.dataclass
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
    attachment: RemoteFile = None


@dataclasses.dataclass
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


@dataclasses.dataclass
class HomeworkStatus:
    submitted: bool = None
    graded: bool = None


@dataclasses.dataclass
class HomeworkDetail:
    description: str = None
    attachment: RemoteFile = None  # attachment from teacher
    answer_content: str = None  # answer from teacher
    answer_attachment: RemoteFile = None
    submitted_content: str = None  # submitted content from student
    submitted_attachment: RemoteFile = None
    grade_attachment: RemoteFile = None  # grade from teacher


@dataclasses.dataclass
class Homework(HomeworkStatus, HomeworkDetail):
    # status
    # submitted: bool
    # graded: bool

    # homework
    id: str = None
    student_homework_id: str = None
    title: str = None
    deadline: datetime.datetime = None
    url: str = None
    submit_url: str = None
    submit_time: datetime.datetime = None
    grade: int = None
    grade_level: str = None  # some homework has levels but not grades, like A/B/.../F
    grade_time: datetime.datetime = None
    grader_name: str = None
    grade_content: str = None

    # detail
    # description: str = None
    # attachment: RemoteFile = None  # attachment from teacher
    # answer_content: str = None  # answer from teacher
    # answer_attachment: RemoteFile = None
    # submitted_content: str = None  # submitted content from student
    # submitted_attachment: RemoteFile = None
    # grade_attachment: RemoteFile = None  # grade from teacher


@dataclasses.dataclass
class Discussion:
    # base
    id: str
    title: str
    publisher_name: str
    publish_date: datetime.datetime
    last_replier_name: str
    last_reply_time: datetime.datetime
    visit_count: int
    reply_count: int

    # discussion
    url: str
    board_id: str


@dataclasses.dataclass
class Question:
    # discussion base
    id: str
    title: str
    publisher_name: str
    publish_date: datetime.datetime
    last_replier_name: str
    last_reply_time: datetime.datetime
    visit_count: int
    reply_count: int

    # question
    url: str
    question: str


@dataclasses.dataclass
class CalendarEvent:
    location: str
    status: str
    start_time: str
    end_time: str
    date: str
    course_name: str
