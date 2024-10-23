from __future__ import annotations

import hishel
import httpx

import thu_learn_downloader.api.types as t


async def raise_for_status(resp: httpx.Response) -> None:
    if 200 <= resp.status_code < 400:
        return
    resp.raise_for_status()


class ApiBase(hishel.AsyncCacheClient):
    lang: t.Language = t.Language.EN

    def __init__(self) -> None:
        super().__init__(
            follow_redirects=True,
            event_hooks={"response": [raise_for_status]},
            base_url="https://learn.tsinghua.edu.cn",
            transport=httpx.AsyncHTTPTransport(retries=3),
        )

    @property
    def token(self) -> str:
        return self.cookies["XSRF-TOKEN"]

    async def get_with_csrf(
        self,
        url: httpx.URL | str,
        *,
        params: httpx._types.QueryParamTypes | None = None,
    ) -> httpx.Response:
        params: httpx.QueryParams = httpx.QueryParams(params)
        params = params.set("_csrf", self.token)
        return await self.get(url, params=params)
