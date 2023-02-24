import html
import urllib.parse
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from bs4 import BeautifulSoup, Tag
from requests import Response

from . import typing as t
from . import urls, utils
from .constants import BS_FEATURES

if TYPE_CHECKING:
    from .helper import Helper


def parse_course_info(raw: dict) -> t.CourseInfo:
    return t.CourseInfo(
        id=raw["wlkcid"],  # 网络课程 ID
        name=raw["kcm"],  # 课程名
        english_name=raw["ywkcm"],  # 英文课程名
        course_number=raw["kch"],  # 课程号
        course_index=int(raw["kxh"]),  # 课序号
    )


def parse_file(
    raw: dict,
    file_clazz: dict[str, str],
    course_id: str,
    course_type: t.CourseType = t.CourseType.STUDENT,
) -> t.File:
    return t.File(
        id=raw["wjid"],  # 文件 ID
        raw_size=raw["wjdx"],  # 文件大小
        title=html.unescape(raw["bt"]),  # 标题
        upload_time=datetime.strptime(raw["scsj"], "%Y-%m-%d %H:%M"),  # 上传时间
        download_url=urls.to_url(
            urls.learn_file_download(
                file_id=raw["wjid"],  # 文件 ID
                course_id=course_id,
                course_type=course_type,
            )
        ),
        file_type=raw["wjlx"],  # 文件类型
        file_clazz=file_clazz[raw["kjflid"]],  # 课件分类 ID
    )


def parse_homework(raw: dict, status: t.HomeworkStatus, helper: "Helper") -> t.Homework:
    detail: t.HomeworkDetail = parse_homework_detail(
        course_id=raw["wlkcid"],  # 网络课程 ID
        homework_id=raw["zyid"],  # 作业 ID
        student_homework_id=raw["xszyid"],  # 学生作业 ID
        helper=helper,
    )

    return t.Homework(
        id=raw["zyid"],  # 作业 ID
        student_homework_id=raw["xszyid"],  # 学生作业 ID
        number=int(raw["wz"]),  #
        title=html.unescape(raw["bt"]),  #  标题
        starts_time=utils.from_timestamp(raw.get("kssj")),  # 开始时间
        deadline=utils.from_timestamp(raw.get("jzsj")),  # 截止时间
        submit_time=utils.from_timestamp(raw.get("scsj")),  # 上传时间
        grade=raw.get("cj", ""),  # 成绩
        grader_name=raw.get("jsm", ""),  # 教师名
        grade_time=utils.from_timestamp(raw.get("pysj")),  # 批阅时间
        grade_content=raw.get("pynr", ""),  # 批阅内容
        **utils.dataclass_as_dict_shallow(status),
        **utils.dataclass_as_dict_shallow(detail),
    )


def parse_homework_detail(
    course_id: str, homework_id: str, student_homework_id: str, helper: "Helper"
) -> t.HomeworkDetail:
    resp: Response = helper.fetch_with_token(
        request=urls.learn_homework_detail(
            course_id=course_id,
            homework_id=homework_id,
            student_homework_id=student_homework_id,
        )
    )
    soup: BeautifulSoup = BeautifulSoup(resp.text, features=BS_FEATURES)

    c55s: list[Tag] = soup.select("div.list.calendar.clearfix > div.fl.right > div.c55")
    file_divs: list[Tag] = soup.select("div.list.fujian.clearfix")
    boxbox: Tag = soup.select("div.boxbox")[1]
    right: Tag = boxbox.select("div.right")[2]

    description: str = html.unescape(c55s[0].get_text().strip())
    answer_content: str = html.unescape(c55s[1].get_text().strip())
    submitted_content: str = html.unescape(right.get_text().strip())

    return t.HomeworkDetail(
        description=description,
        attachment=parse_homework_file(file_div=file_divs[0]),
        answer_content=answer_content,
        answer_attachment=parse_homework_file(file_div=file_divs[1]),
        submitted_content=submitted_content,
        submitted_attachment=parse_homework_file(file_div=file_divs[2]),
        grade_attachment=parse_homework_file(file_div=file_divs[3]),
    )


def parse_homework_file(file_div: Tag) -> Optional[t.RemoteFile]:
    ftitle = file_div.select_one(".ftitle") or file_div.select_one(".fl")
    assert ftitle
    file_node = ftitle.select_one("a")
    if not file_node:
        return None

    href = file_node["href"]
    assert isinstance(href, str)
    parse_result = urllib.parse.urlparse(href)
    query = urllib.parse.parse_qs(parse_result.query)
    return t.RemoteFile(
        id=query["fileId"][0],
        name=file_node.get_text(),
        download_url=urls.make_url(path=query["downloadUrl"][0]),
    )
