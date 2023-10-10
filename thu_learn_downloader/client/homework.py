import html
import shutil
import subprocess
import urllib.parse
from collections.abc import Sequence
from datetime import datetime
from enum import StrEnum
from subprocess import CompletedProcess
from typing import Any, Optional, Self
from urllib.parse import SplitResult

from bs4 import BeautifulSoup, Tag
from pydantic import Field
from requests import Response

from thu_learn_downloader.common.typing import cast

from . import url
from .client import Client
from .model import BaseModel

MARKDOWN_TEMPLATE: str = """## {title}

### Contents and Requirements

- Starts: {start_time}
- Deadline: {deadline}

#### Description

{description}

#### ANS

{answer_content}

### My coursework submitted

- Date: {submit_time}

#### Content

{submitted_content}

### Instructors' comments

- By: {grader_name}
- Date: {grade_time}
- Grade: {grade}

#### Comment

{grade_content}
"""


class AttachmentType(StrEnum):
    ANSWER = "answer"
    ATTACHMENT = "attach"
    COMMENT = "comment"
    SUBMITTED = "submit"


class Attachment(BaseModel):
    id: str
    download_url: str
    name: str
    type_: AttachmentType


class Homework(BaseModel):
    client: Client = Field(exclude=True)
    id: str = Field(alias="zyid")
    answer_attachment: Optional[Attachment]
    answer_content: str
    attachment: Optional[Attachment]
    deadline: datetime = Field(alias="jzsj")
    description: str
    grade_attachment: Optional[Attachment]
    grade_content: str = Field("", alias="pynr")
    grade_time: Optional[datetime] = Field(alias="pysj")
    grade: Optional[int | str] = Field(alias="cj")
    grader_name: str = Field("", alias="jsm")
    number: int = Field(alias="wz")
    start_time: datetime = Field(alias="kssj")
    submit_time: Optional[datetime] = Field(alias="scsj")
    submitted_attachment: Optional[Attachment]
    submitted_content: str
    title: str = Field(alias="bt")

    @staticmethod
    def parse_homework_file(
        file_div: Tag, type_: AttachmentType
    ) -> Optional[Attachment]:
        fl: Optional[Tag] = file_div.select_one(".txt.fl")
        if fl is None:
            return None
        file_node: Optional[Tag] = fl.select_one("a")
        if file_node is None:
            return None

        href: str = cast(str, file_node["href"])
        assert isinstance(href, str)
        split_result: SplitResult = urllib.parse.urlsplit(href)
        query: dict[str, list[str]] = urllib.parse.parse_qs(split_result.query)
        return Attachment(
            id=query["fileId"][0],
            download_url=url.make_url(path=query["downloadUrl"][0]),
            name=file_node.get_text(),
            type_=type_,
        )

    @classmethod
    def from_json(cls, client: Client, json: dict[str, Any]) -> Self:
        response: Response = client.get_with_token(
            url=url.make_url(
                path="/f/wlxt/kczy/zy/student/viewCj",
                query={
                    "wlkcid": json["wlkcid"],
                    "xszyid": json["xszyid"],
                    "zyid": json["zyid"],
                },
            )
        )
        soup: BeautifulSoup = BeautifulSoup(response.text, features="html.parser")
        c55s: list[Tag] = soup.select(
            "div.list.calendar.clearfix > div.fl.right > div.c55"
        )
        file_divs: list[Tag] = soup.select("div.list.fujian.clearfix")
        boxbox: Tag = soup.select("div.boxbox")[1]
        right: Tag = boxbox.select("div.right")[2]
        description: str = html.unescape(c55s[0].get_text().strip())
        answer_content: str = html.unescape(c55s[1].get_text().strip())
        submitted_content: str = html.unescape(right.get_text().strip())
        json["bt"] = html.unescape(json["bt"]).strip()
        return cls(
            **json,
            client=client,
            description=description,
            attachment=cls.parse_homework_file(
                file_div=file_divs[0], type_=AttachmentType.ATTACHMENT
            ),
            answer_content=answer_content,
            answer_attachment=cls.parse_homework_file(
                file_div=file_divs[1], type_=AttachmentType.ANSWER
            ),
            submitted_content=submitted_content,
            submitted_attachment=cls.parse_homework_file(
                file_div=file_divs[2], type_=AttachmentType.SUBMITTED
            ),
            grade_attachment=cls.parse_homework_file(
                file_div=file_divs[3], type_=AttachmentType.COMMENT
            ),
        )

    @property
    def attachments(self) -> Sequence[Attachment]:
        attachments: Sequence[Attachment] = []
        if self.attachment:
            attachments.append(self.attachment)
        if self.submitted_attachment:
            attachments.append(self.submitted_attachment)
        if self.grade_attachment:
            attachments.append(self.grade_attachment)
        if self.answer_attachment:
            attachments.append(self.answer_attachment)
        return attachments

    @property
    def markdown(self) -> str:
        def format_value(value: Any) -> str:
            if not value:
                return ""
            if isinstance(value, datetime):
                return value.strftime("%Y-%m-%d %H:%M:%S")
            return str(value)

        result: str = MARKDOWN_TEMPLATE.format_map(
            {key: format_value(value) for key, value in self.model_dump().items()}
        )
        if shutil.which("prettier"):
            process: CompletedProcess = subprocess.run(
                args=["prettier", "--parser=markdown"],
                capture_output=True,
                input=result,
                text=True,
            )
            result = process.stdout
        return result
