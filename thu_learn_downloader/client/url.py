import urllib.parse
from urllib.parse import SplitResult

SCHEME: str = "https"
NETLOC: str = "learn.tsinghua.edu.cn"


def make_url(
    scheme: str = SCHEME,
    netloc: str = NETLOC,
    path: str = "",
    query: dict = {},
    fragment="",
) -> str:
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
