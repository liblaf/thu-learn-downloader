import functools
import urllib.parse
from collections.abc import Sequence
from urllib.parse import ParseResult

from bs4 import BeautifulSoup, Tag
from requests import Response

from thu_learn_downloader.common.typing import cast

from . import url
from .client import Client, Language
from .semester import Semester


class Learn:
    client: Client

    def __init__(self, language: Language = Language.ENGLISH, *args, **kwargs) -> None:
        self.client = Client(language=language, *args, **kwargs)

    def login(self, username: str, password: str) -> None:
        response: Response = self.client.get(url=url.make_url())
        soup: BeautifulSoup = BeautifulSoup(
            markup=response.text, features="html.parser"
        )
        login_form: Tag = cast(Tag, soup.select_one(selector="#loginForm"))
        action: str = cast(str, login_form["action"])
        response: Response = self.client.post(
            url=action, data={"i_user": username, "i_pass": password, "atOnce": True}
        )
        soup: BeautifulSoup = BeautifulSoup(
            markup=response.text, features="html.parser"
        )
        a: Tag = cast(Tag, soup.select_one(selector="a"))
        href: str = cast(str, a["href"])
        parse_result: ParseResult = urllib.parse.urlparse(url=href)
        query: dict[str, list[str]] = urllib.parse.parse_qs(qs=parse_result.query)
        status, ticket = query["status"][0], query["ticket"][0]
        self.client.get(url=href)
        self.client.get(
            url=url.make_url(path="/b/j_spring_security_thauth_roaming_entry"),
            params={"ticket": ticket},
        )
        self.client.get(url=url.make_url(path="/f/wlxt/index/course/student/"))
        assert status == "SUCCESS"

    @functools.cached_property
    def semesters(self) -> Sequence[Semester]:
        return [
            Semester(client=self.client, id=result)
            for result in self.client.get_with_token(
                url=url.make_url(path="/b/wlxt/kc/v_wlkc_xs_xktjb_coassb/queryxnxq")
            ).json()
        ]
