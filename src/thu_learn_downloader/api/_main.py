from __future__ import annotations

from thu_learn_downloader.api._course import CourseMixin
from thu_learn_downloader.api._login import LoginMixin
from thu_learn_downloader.api._semester import SemesterMixin


class Learn2018Api(LoginMixin, SemesterMixin, CourseMixin): ...
