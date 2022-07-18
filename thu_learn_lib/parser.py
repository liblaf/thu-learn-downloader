import datetime
import urllib.parse

import bs4

from . import ty
from . import urls


def parse_course_info(
    course: dict,
    course_type: ty.CourseType = ty.CourseType.STUDENT,
):
    # url = urls.learn_course_time_location(course["wlkcid"])
    # response = self.get_with_token(url)
    return ty.CourseInfo(
        id=course["wlkcid"],
        name=course["kcm"],
        english_name=course["ywkcm"],
        # time_and_location=response.json(),
        url=str(urls.learn_course_url(course["wlkcid"], course_type)),
        teacher_name=course["jsm"]
        if course["jsm"]
        else "",  # teacher can not fetch this
        teacher_number=course["jsh"],
        course_number=course["kch"],
        course_index=int(
            course["kxh"]
        ),  # course["kxh"] could be string (teacher mode) or number (student mode)
        course_type=course_type,
    )


def parse_file(
    file: dict,
    course_id: str,
    clazz: dict[str, str],
    course_type: ty.CourseType = ty.CourseType.STUDENT,
) -> ty.File:
    title: str = file["bt"]
    download_url: str = urls.learn_file_download(
        file_id=file["wjid"] if course_type == ty.CourseType.STUDENT else file["id"],
        course_type=course_type,
        course_id=course_id,
    )
    preview_url = None
    return ty.File(
        id=file["wjid"],  # 文件 ID
        title=file["bt"],  # 标题
        description=file["ms"],  # 描述
        raw_size=file["wjdx"],  # 文件大小
        size=file["fileSize"],
        upload_time=datetime.datetime.strptime(file["scsj"], r"%Y-%m-%d %H:%M"),  # 上传时间
        download_url=str(download_url),
        preview_url=str(preview_url),
        is_new=file["isNew"],
        marked_important=file["sfqd"] == 1,  # 是否强调
        visit_count=file["llcs"] or 0,  # 浏览次数
        download_count=file["xzcs"] or 0,  # 下载次数
        file_type=file["wjlx"],  # 文件类型
        remote_file=ty.RemoteFile(
            id=file["wjid"],  # 文件 ID
            name=title,
            download_url=str(download_url),
            preview_url=str(preview_url),
            size=file["fileSize"],
        ),
        clazz=clazz[file["kjflid"]],  # 课件分类 ID
    )


def parse_homework_file(div: bs4.element.Tag) -> ty.RemoteFile:
    ftitle: bs4.element.Tag = div.find(
        name="span",
        attrs={
            "class": "ftitle",
        },
    ) or div.find(
        name="span",
        attrs={
            "class",
            "ft",
        },
    )
    if not ftitle:
        return None
    a: bs4.element.Tag = ftitle.find(name="a")
    size: bs4.element.Tag = div.find(
        name="span",
        attrs={
            "class": "color_999",
        },
    )
    size: str = size.getText()
    params = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(a["href"]).query))
    attachment_id = params["fileId"]
    download_url = ty.URL(
        netloc=urls.LEARN_PREFIX.netloc,
        path=params["downloadUrl"] if "downloadUrl" in params else a["href"],
    )
    return ty.RemoteFile(
        id=attachment_id,
        name=a.getText(),
        download_url=download_url,
        preview_url=None,
        size=size.strip(),
    )
