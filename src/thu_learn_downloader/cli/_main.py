from __future__ import annotations

import thu_learn_downloader.api.types as t
from thu_learn_downloader.api import Learn2018Api


async def main(username: str, password: str) -> None:
    ic(username, password)
    api: Learn2018Api = Learn2018Api()
    await api.login(username, password)
    ic(await api.get_semester_id_list())
    ic(await api.get_current_semester())
    ic(await api.get_course_list("2024-2025-1"))
