from __future__ import annotations

from typing import TYPE_CHECKING

from thu_learn_downloader.api._base import ApiBase

if TYPE_CHECKING:
    import httpx


class SemesterMixin(ApiBase):
    async def get_semester_id_list(self) -> list[str]:
        resp: httpx.Response = await self.get_with_csrf(
            "/b/wlxt/kc/v_wlkc_xs_xktjb_coassb/queryxnxq"
        )
        return [semester_id for semester_id in resp.json() if semester_id]

    async def get_current_semester(self) -> str:
        resp: httpx.Response = await self.get_with_csrf(
            "/b/kc/zhjw_v_code_xnxq/getCurrentAndNextSemester"
        )
        return resp.json()["result"]["id"]
