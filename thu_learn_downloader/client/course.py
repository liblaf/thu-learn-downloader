from collections.abc import Sequence
from typing import Any

from pydantic import Field
from requests import Response

from . import url
from .client import MAX_SIZE, Client
from .document import Document, DocumentClass
from .homework import Homework
from .model import BaseModel


class Course(BaseModel):
    client: Client = Field(exclude=True)
    id: str = Field(alias="wlkcid")
    chinese_name: str = Field(alias="kcm")
    course_number: str = Field(alias="kch")
    english_name: str = Field(alias="ywkcm")
    name: str = Field(alias="zywkcm")
    teacher_name: str = Field(alias="jsm")
    teacher_number: str = Field(alias="jsh")

    @property
    def document_classes(self) -> Sequence[DocumentClass]:
        return [
            DocumentClass(client=self.client, **result)
            for result in self.client.get_with_token(
                url=url.make_url(path="/b/wlxt/kj/wlkc_kjflb/student/pageList"),
                params={"wlkcid": self.id},
            ).json()["object"]["rows"]
        ]

    @property
    def documents(self) -> Sequence[Document]:
        documents: Sequence[Document] = [
            Document(client=self.client, **result)
            for result in self.client.get_with_token(
                url=url.make_url(
                    path="/b/wlxt/kj/wlkc_kjxxb/student/kjxxbByWlkcidAndSizeForStudent"
                ),
                params={"wlkcid": self.id, "size": MAX_SIZE},
            ).json()["object"]
        ]
        documents.sort(key=lambda document: document.title)
        documents.sort(key=lambda document: document.upload_time)
        return documents

    @property
    def homeworks(self) -> Sequence[Homework]:
        return [
            *self._homeworks_at_url(
                url=url.make_url(
                    path="/b/wlxt/kczy/zy/student/index/zyListWj",
                    query={"wlkcid": self.id, "size": MAX_SIZE},
                ),
            ),
            *self._homeworks_at_url(
                url=url.make_url(
                    path="/b/wlxt/kczy/zy/student/index/zyListYjwg",
                    query={"wlkcid": self.id, "size": MAX_SIZE},
                ),
            ),
            *self._homeworks_at_url(
                url=url.make_url(
                    path="/b/wlxt/kczy/zy/student/index/zyListYpg",
                    query={"wlkcid": self.id, "size": MAX_SIZE},
                ),
            ),
        ]

    def _homeworks_at_url(self, url: str) -> Sequence[Homework]:
        resp: Response = self.client.get_with_token(url=url)
        json: dict[str, Any] = resp.json()
        results: Sequence[dict[str, Any]] = json["object"]["aaData"] or []
        return [
            Homework.from_json(client=self.client, json=result) for result in results
        ]
