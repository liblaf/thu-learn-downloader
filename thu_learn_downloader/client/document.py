from datetime import datetime

from pydantic import Field

from . import url
from .client import Client
from .model import BaseModel


class DocumentClass(BaseModel):
    client: Client = Field(exclude=True)
    id: str = Field(alias="kjflid")
    title: str = Field(alias="bt")


class Document(BaseModel):
    client: Client = Field(exclude=True)
    id: str = Field(alias="wjid")
    class_id: str = Field(alias="kjflid")
    file_type: str = Field(alias="wjlx")
    size: int = Field(alias="wjdx")
    title: str = Field(alias="bt")
    upload_time: datetime = Field(alias="scsj")

    @property
    def download_url(self) -> str:
        return url.make_url(
            path="/b/wlxt/kj/wlkc_kjxxb/student/downloadFile",
            query={"sfgk": 0, "wjid": self.id},
        )
