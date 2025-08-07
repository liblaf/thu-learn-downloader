from collections.abc import Sequence
from typing import Any

from pydantic import Field
from requests import Response

from . import url
from .client import MAX_SIZE, Client
from .document import Document, DocumentClass
from .homework import Homework
from .model import BaseModel

# 全局变量用于收集课程问题信息
_course_issues = {
    "missing_documents": [],
    "missing_document_classes": [],
    "missing_homeworks": [],
}


def get_course_issues():
    """获取课程问题汇总"""
    return _course_issues.copy()


def clear_course_issues():
    """清空课程问题记录"""
    global _course_issues
    _course_issues = {
        "missing_documents": [],
        "missing_document_classes": [],
        "missing_homeworks": [],
    }


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
        # 异常处理，记录问题
        try:
            response = self.client.get_with_token(
                url=url.make_url(path="/b/wlxt/kj/wlkc_kjflb/student/pageList"),
                params={"wlkcid": self.id},
            )
            json_data = response.json()["object"]["rows"]

            return [
                DocumentClass(client=self.client, **result)
                for result in response.json()["object"]["rows"]
            ]

        except Exception as e:
            _course_issues["missing_document_classes"].append(
                {"course": self.name, "course_id": self.id, "reason": f"异常: {e!s}"}
            )
            return []

    @property
    def documents(self) -> Sequence[Document]:
        try:
            response = self.client.get_with_token(
                url=url.make_url(
                    path="/b/wlxt/kj/wlkc_kjxxb/student/kjxxbByWlkcidAndSizeForStudent"
                ),
                params={"wlkcid": self.id, "size": MAX_SIZE},
            )
            documents: Sequence[Document] = [
                Document(client=self.client, **result)
                for result in response.json()["object"]
            ]
            documents.sort(key=lambda document: document.title)
            documents.sort(key=lambda document: document.upload_time)
            return documents

        except Exception as e:
            _course_issues["missing_documents"].append(
                {"course": self.name, "course_id": self.id, "reason": f"异常: {e!s}"}
            )
            return []

    @property
    def homeworks(self) -> Sequence[Homework]:
        all_homeworks = [
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

        # 如果所有作业API都没有返回数据，记录该课程
        if not all_homeworks:
            _course_issues["missing_homeworks"].append(
                {"course": self.name, "course_id": self.id, "reason": "该课程无作业"}
            )

        return all_homeworks

    def _homeworks_at_url(self, url: str) -> Sequence[Homework]:
        try:
            resp: Response = self.client.get_with_token(url=url)

            # 检查响应状态
            if resp.status_code != 200:
                # 作业API失败时，只在所有作业API都失败时才记录
                return []

            # 尝试解析JSON
            json_data: dict[str, Any] = resp.json()
            if json_data is None:
                return []

            # 检查数据结构
            if "object" not in json_data:
                return []

            if "aaData" not in json_data["object"]:
                return []

            results: Sequence[dict[str, Any]] = json_data["object"]["aaData"] or []
            return [
                Homework.from_json(client=self.client, json=result)
                for result in results
            ]

        except Exception:
            return []
