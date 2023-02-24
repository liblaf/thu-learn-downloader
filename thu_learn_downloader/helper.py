import urllib.parse

from bs4 import BeautifulSoup, Tag
from requests import Request, Response, Session

from . import parser
from . import typing as t
from . import urls
from .constants import BS_FEATURES


class Helper(Session):
    def fetch(self, request: Request) -> Response:
        match request.method:
            case "GET":
                return self.get(url=request.url, params=request.params)
            case "POST":
                return self.post(url=request.url, data=request.data)
            case _:
                raise NotImplemented()

    def login(self, username: str, password: str) -> bool:
        resp: Response = self.get(url=urls.make_url())
        soup: BeautifulSoup = BeautifulSoup(markup=resp.text, features=BS_FEATURES)
        login_form = soup.select_one(selector="#loginForm")
        assert isinstance(login_form, Tag)
        action = login_form["action"]
        assert isinstance(action, str)

        resp: Response = self.fetch(
            request=urls.id_login(action=action, username=username, password=password)
        )
        soup: BeautifulSoup = BeautifulSoup(markup=resp.text, features=BS_FEATURES)
        a = soup.select_one(selector="a")
        assert isinstance(a, Tag)
        href = a["href"]
        assert isinstance(href, str)
        parse_result: urllib.parse.ParseResult = urllib.parse.urlparse(url=href)
        query = urllib.parse.parse_qs(qs=parse_result.query)
        status, ticket = query["status"][0], query["ticket"][0]

        _ = self.get(url=href)

        _ = self.fetch(urls.learn_auth_roam(ticket=ticket))

        _ = self.fetch(urls.learn_student_course_list_page())

        return status == "SUCCESS"

    @property
    def token(self) -> str:
        return self.cookies.get(name="XSRF-TOKEN")

    def fetch_with_token(self, request: Request, *args, **kwargs) -> Response:
        assert isinstance(request.params, dict)
        request.params["_csrf"] = self.token
        return self.fetch(request=request, *args, **kwargs)

    def get_semester_id_list(self) -> list[str]:
        resp: Response = self.fetch_with_token(request=urls.learn_semester_list())
        return list(filter(None, resp.json()))

    def get_course_list(
        self, semester_id: str, course_type: t.CourseType = t.CourseType.STUDENT
    ) -> list[t.CourseInfo]:
        resp: Response = self.fetch_with_token(
            urls.learn_course_list(semester=semester_id, course_type=course_type)
        )
        results = resp.json()["resultList"] or list()
        return list(map(parser.parse_course_info, results))

    def get_file_list(
        self, course_id: str, course_type: t.CourseType = t.CourseType.STUDENT
    ) -> list[t.File]:
        resp: Response = self.fetch_with_token(
            urls.learn_file_clazz(course_id=course_id)
        )
        file_clazz: dict[str, str] = dict()
        rows = resp.json()["object"]["rows"]
        for row in rows:
            file_clazz[row["kjflid"]] = row["bt"]  # 课件分类 ID, 标题

        resp: Response = self.fetch_with_token(
            urls.learn_file_list(course_id=course_id, course_type=course_type)
        )
        json = resp.json()

        if "resultsList" in json["object"]:
            results = json["object"]["resultsList"]
        else:
            results = json["object"]

        return list(
            map(
                parser.parse_file,
                results,
                [file_clazz] * len(results),
                [course_id] * len(results),
                [course_type] * len(results),
            )
        )

    def get_homework_list(
        self, course_id: str, course_type: t.CourseType = t.CourseType.STUDENT
    ) -> list[t.Homework]:
        assert course_type == t.CourseType.STUDENT
        works: list[t.Homework] = [
            *self.get_homework_list_at_url(
                req=urls.learn_homework_list_new(course_id=course_id),
                status=t.HomeworkStatus(submitted=False, graded=False),
            ),
            *self.get_homework_list_at_url(
                req=urls.learn_homework_list_submitted(course_id=course_id),
                status=t.HomeworkStatus(submitted=True, graded=False),
            ),
            *self.get_homework_list_at_url(
                req=urls.learn_homework_list_graded(course_id=course_id),
                status=t.HomeworkStatus(submitted=True, graded=False),
            ),
        ]
        return works

    def get_homework_list_at_url(
        self, req: Request, status: t.HomeworkStatus
    ) -> list[t.Homework]:
        resp: Response = self.fetch_with_token(request=req)
        json = resp.json()
        res = json["object"]["aaData"] or list()
        return list(
            map(
                parser.parse_homework,
                res,
                [status] * len(res),
                [self] * len(res),
            )
        )
