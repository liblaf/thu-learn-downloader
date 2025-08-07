from collections.abc import Sequence

from pydantic import Field

from . import url
from .client import Client
from .course import Course
from .model import BaseModel


class Semester(BaseModel):
    client: Client = Field(exclude=True)
    id: str

    @property
    def courses(self) -> Sequence[Course]:
        return [
            Course(client=self.client, **result)
            for result in self.client.get_with_token(
                url=url.make_url(
                    path=f"/b/wlxt/kc/v_wlkc_xs_xkb_kcb_extend/student/loadCourseBySemesterId/{self.id}/{self.client.language}"
                )
            ).json()["resultList"]
        ]
