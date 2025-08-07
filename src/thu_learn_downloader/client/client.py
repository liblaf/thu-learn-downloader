from collections.abc import Mapping
from enum import StrEnum
from typing import Any

from requests import Response, Session

MAX_SIZE: int = 200


class Language(StrEnum):
    ENGLISH = "en"
    CHINESE = "zh"


class Client(Session):
    language: Language

    def __init__(self, language: Language = Language.ENGLISH, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.language = language

    def get_with_token(
        self, url: str, params: Mapping[str, Any] | None = None
    ) -> Response:
        params = params or {}
        return self.get(url=url, params={**params, "_csrf": self.token})

    @property
    def token(self) -> str:
        try:
            token = self.cookies.get("XSRF-TOKEN")
            if token is None:
                raise KeyError("XSRF-TOKEN not found in cookies")
            return token
        except KeyError as e:
            print(f"无法获取CSRF token: {e}")
            print(f"当前cookies: {list(self.cookies.keys())}")
            raise Exception("登录状态可能已失效，请重新登录") from e
