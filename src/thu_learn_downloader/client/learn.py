import functools
from collections.abc import Sequence

from . import url
from .client import Client, Language
from .semester import Semester


class Learn:
    client: Client

    def __init__(self, language: Language = Language.ENGLISH, *args, **kwargs) -> None:
        self.client = Client(language, *args, **kwargs)

    """使用浏览器进行统一用户登录"""

    def login(self) -> None:
        from ..login.browser import login_with_browser

        try:
            cookies = login_with_browser()

            # 将cookies设置到client中
            for name, value in cookies.items():
                self.client.cookies[name] = value

            # 验证登录是否成功，尝试访问课程页面
            response = self.client.get(
                url=url.make_url(path="/f/wlxt/index/course/student/")
            )
            if response.status_code == 200:
                print("浏览器登录成功！")
            else:
                raise Exception("登录验证失败，请重试")

        except Exception as e:
            print(f"浏览器登录失败: {e}")

    # def login(self, username: str = None, password: str = None) -> None:
    #     """
    #     登录方法
    #     如果提供了用户名和密码，使用传统登录方式（保留兼容性）
    #     否则使用浏览器登录方式
    #     """
    #     if username and password:
    #         # 使用传统的用户名密码登录方式
    #         self._login_with_credentials(username, password)
    #     else:
    #         # 使用新的浏览器登录方式
    #         self.login_with_browser()

    # def _login_with_credentials(self, username: str, password: str) -> None:
    #     """传统的用户名密码登录方式（保留作为备用）"""
    #     response: Response = self.client.get(url=url.make_url())
    #     soup: BeautifulSoup = BeautifulSoup(
    #         markup=response.text, features="html.parser"
    #     )
    #     login_form: Tag = cast(Tag, soup.select_one(selector="#loginForm"))
    #     action: str = cast(str, login_form["action"])
    #     response: Response = self.client.post(
    #         url=action, data={"i_user": username, "i_pass": password, "atOnce": True}
    #     )
    #     soup: BeautifulSoup = BeautifulSoup(
    #         markup=response.text, features="html.parser"
    #     )
    #     a: Tag = cast(Tag, soup.select_one(selector="a"))
    #     href: str = cast(str, a["href"])
    #     parse_result: ParseResult = urllib.parse.urlparse(url=href)
    #     query: dict[str, list[str]] = urllib.parse.parse_qs(qs=parse_result.query)
    #     status, ticket = query["status"][0], query["ticket"][0]
    #     self.client.get(url=href)
    #     self.client.get(
    #         url=url.make_url(path="/b/j_spring_security_thauth_roaming_entry"),
    #         params={"ticket": ticket},
    #     )
    #     self.client.get(url=url.make_url(path="/f/wlxt/index/course/student/"))
    #     assert status == "SUCCESS"

    @functools.cached_property
    def semesters(self) -> Sequence[Semester]:
        return [
            Semester(client=self.client, id=result)
            for result in self.client.get_with_token(
                url=url.make_url(path="/b/wlxt/kc/v_wlkc_xs_xktjb_coassb/queryxnxq")
            ).json()
        ]
