from __future__ import annotations

from typing import TYPE_CHECKING, Any

import thu_learn_downloader.api.types as t
from thu_learn_downloader.api._base import ApiBase

if TYPE_CHECKING:
    import httpx


class CourseMixin(ApiBase):
    async def get_course_list(self, semester_id: str) -> list[t.CourseInfo]:
        resp: httpx.Response = await self.get_with_csrf(
            f"/b/wlxt/kc/v_wlkc_xs_xkb_kcb_extend/student/loadCourseBySemesterId/{semester_id}/{self.lang}"
        )
        json: Any = resp.json()
        return [t.CourseInfo(**obj) for obj in json["resultList"]]
