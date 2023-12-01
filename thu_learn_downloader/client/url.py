import urllib.parse
from collections.abc import Mapping
from typing import Optional
from urllib.parse import SplitResult

SCHEME: str = "https"
NETLOC: str = "learn.tsinghua.edu.cn"


def make_url(
    scheme: str = SCHEME,
    netloc: str = NETLOC,
    path: str = "",
    query: Optional[Mapping] = None,
    fragment="",
) -> str:
    query = query or {}
    return urllib.parse.urlunsplit(
        SplitResult(
            scheme=scheme,
            netloc=netloc,
            path=path,
            query=urllib.parse.urlencode(query),
            fragment=fragment,
        )
    )


LEARN_PREFIX: str = make_url()
