from __future__ import annotations

from typing import TYPE_CHECKING

import bs4
import yarl

from thu_learn_downloader.api._base import ApiBase

if TYPE_CHECKING:
    import httpx


class LoginMixin(ApiBase):
    async def login(self, username: str, password: str) -> None:
        resp: httpx.Response = await self.post(
            "https://id.tsinghua.edu.cn/do/off/ui/auth/login/post/bb5df85216504820be7bba2b0ae1535b/0?/login.do",
            data={"i_user": username, "i_pass": password, "atOnce": True},
        )
        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(resp.text, "html.parser")
        a: bs4.Tag = soup.select_one("a")  # pyright: ignore [reportAssignmentType]
        url: yarl.URL = yarl.URL(a["href"])  # pyright: ignore [reportArgumentType]
        status: str = url.query["status"]
        assert status == "SUCCESS"
        ticket: str = url.query["ticket"]
        resp = await self.get(
            "/b/j_spring_security_thauth_roaming_entry", params={"ticket": ticket}
        )
        resp = await self.get_with_csrf("/f/wlxt/index/course/student/")
