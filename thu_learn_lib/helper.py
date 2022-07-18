import datetime
import typing
import urllib.parse

import bs4
import requests
import requests.adapters

from . import ty
from . import urls
from . import parser


class LearnHelper(requests.Session):
    username: str
    password: str

    def __init__(self, username: str, password: str) -> None:
        super().__init__()
        self.username = username
        self.password = password

        self.mount(
            prefix="https://",
            adapter=requests.adapters.HTTPAdapter(
                max_retries=5,
            ),
        )

    @property
    def token(self) -> str:
        return self.cookies.get(name="XSRF-TOKEN", default="")

    def get_with_token(self, url: ty.URL) -> requests.Response:
        if url.query:
            url.query["_csrf"] = self.token
        else:
            url.query = {
                "_csrf": self.token,
            }
        return self.get(url)

    def login(self) -> bool:
        response = self.get(urls.LEARN_PREFIX)
        soup = bs4.BeautifulSoup(response.text, features="html.parser")
        form = soup.find(
            name="form", attrs={"class": "w", "id": "loginForm", "method": "post"}
        )

        payload = urls.id_login_form_data(
            username=self.username,
            password=self.password,
        ).query
        response = self.post(url=form["action"], data=payload)
        soup = bs4.BeautifulSoup(response.text, features="html.parser")
        a = soup.find(name="a")
        href = a["href"]
        parse_result: urllib.parse.ParseResult = urllib.parse.urlparse(url=href)
        query = urllib.parse.parse_qs(qs=parse_result.query)
        self.status = query["status"][0]
        self.ticket = query["ticket"][0]

        response = self.get(a["href"])

        url = urls.learn_auth_roam(ticket=self.ticket)
        response = self.get(url)

        url = urls.learn_student_course_list_page()
        response = self.get(url)

        print(f"User {self.username} login {self.status}!")

        return self.status == "SUCCESS"

    def logout(self) -> None:
        url = urls.learn_logout()
        response = self.post(url)

    def get_semester_id_list(self) -> list[str]:
        url = urls.learn_semester_list()
        response = self.get_with_token(url)
        json = response.json()
        return list(filter(bool, json))

    def get_current_semester(self) -> ty.SemesterInfo:
        url = urls.learn_current_semester()
        response = self.get_with_token(url)
        json = response.json()
        result = json["result"]
        return ty.SemesterInfo(
            id=result["id"],
            start_date=datetime.datetime.strptime(result["kssj"], r"%Y-%m-%d").date(),
            end_date=datetime.datetime.strptime(result["jssj"], r"%Y-%m-%d").date(),
            start_year=int(result["xnxq"][0:4]),
            end_year=int(result["xnxq"][5:9]),
            type=int(result["xnxq"][10:]),
        )

    def get_course_list(
        self,
        semester_id: str,
        course_type: ty.CourseType = ty.CourseType.STUDENT,
    ) -> list[ty.CourseInfo]:
        url = urls.learn_course_list(semester_id, course_type)
        response = self.get_with_token(url)
        json = response.json()
        result = json["resultList"]
        courses = list(
            map(
                parser.parse_course_info,
                result,
                [course_type] * len(result),
            )
        )
        return courses

    def get_file_list(
        self,
        course_id: str,
        course_type: ty.CourseType = ty.CourseType.STUDENT,
    ) -> list[ty.File]:
        url = urls.learn_file_classify(
            course_id=course_id,
        )
        response = self.get_with_token(url)
        json = response.json()
        records = json["object"]["rows"]
        clazz = {}
        for record in records:
            clazz[record["kjflid"]] = record["bt"]  # 课件分类 ID, 标题

        url = urls.learn_file_list(
            course_id=course_id,
            course_type=course_type,
        )
        response = self.get_with_token(url)
        json = response.json()
        result = []
        if course_type == ty.CourseType.STUDENT:
            result = json["object"]
        else:  # teacher
            result = json["object"]["resultList"]

        files = list(
            map(
                parser.parse_file,
                result,
                [course_id] * len(result),
                [clazz] * len(result),
                [course_type] * len(result),
            )
        )
        return files

    def get_homework_list(
        self, course_id: str, course_type: ty.CourseType = ty.CourseType.STUDENT
    ) -> list[ty.Homework]:
        result = []
        url = urls.learn_homework_list_new(course_id=course_id)
        result += self.get_homework_list_at_url(
            url=url,
            status=ty.HomeworkStatus(submitted=False, graded=False),
        )
        url = urls.learn_homework_list_submitted(course_id=course_id)
        result += self.get_homework_list_at_url(
            url=url,
            status=ty.HomeworkStatus(submitted=True, graded=False),
        )
        url = urls.learn_homework_list_graded(course_id=course_id)
        result += self.get_homework_list_at_url(
            url=url,
            status=ty.HomeworkStatus(submitted=True, graded=True),
        )

        return result

    def get_homework_list_at_url(
        self, url: ty.URL, status: ty.HomeworkStatus
    ) -> list[ty.Homework]:
        response = self.get_with_token(url)
        json = response.json()

        result = json["object"]["aaData"]

        def mapper(work: dict) -> ty.Homework:
            detail = self.parse_homework_detail(
                course_id=work["wlkcid"],  # 课程 ID
                homework_id=work["zyid"],  # 作业 ID
                student_homework_id=work["xszyid"],  # 学生作业 ID
            )

            return ty.Homework(
                id=work["zyid"],  # 作业 ID
                student_homework_id=work["xszyid"],  # 学生作业 ID
                title=work["bt"],  # 标题
                url=str(
                    urls.learn_homework_detail(
                        course_id=work["wlkcid"],  # 课程 ID
                        homework_id=work["zyid"],  # 作业 ID
                        student_homework_id=work["xszyid"],  # 学生作业 ID
                    )
                ),
                deadline=datetime.datetime.fromtimestamp(work["jzsj"] / 1000.0)
                if work["jzsj"]
                else None,  # 截止时间
                submit_url=urls.learn_homework_submit(
                    work["wlkcid"], work["xszyid"]  # 课程 ID, 学生作业 ID
                ),
                submit_time=datetime.datetime.fromtimestamp(work["scsj"] / 1000.0)
                if work["scsj"]
                else None,  # 上传时间
                grade=work["cj"],  # 成绩
                grader_name=work["jsm"],  # 教师名
                grade_content=work["pynr"],  # 批阅内容
                grade_time=datetime.datetime.fromtimestamp(work["pysj"] / 1000.0)
                if work["pysj"]
                else None,  # 批阅时间
                submitted=status.submitted,
                graded=status.graded,
                description=detail.description,
                answer_content=detail.answer_content,
                submitted_content=detail.submitted_content,
                attachment=detail.attachment,
                answer_attachment=detail.answer_attachment,
                submitted_attachment=detail.submitted_attachment,
                grade_attachment=detail.grade_attachment,
            )

        return list(map(mapper, result))

    def parse_homework_detail(
        self, course_id: str, homework_id: str, student_homework_id: str
    ) -> ty.HomeworkDetail:
        url = urls.learn_homework_detail(
            course_id=course_id,
            homework_id=homework_id,
            student_homework_id=student_homework_id,
        )
        response = self.get_with_token(url)
        text = response.text
        soup = bs4.BeautifulSoup(markup=text, features="html.parser")

        div_list_calendar_clearfix: typing.Iterable[bs4.element.Tag] = soup.find_all(
            name="div", attrs={"class": "list calendar clearfix"}
        )
        div_fl_right: list[bs4.element.Tag] = sum(
            [
                div.find_all(
                    name="div",
                    attrs={
                        "class": "fl right",
                    },
                )
                for div in div_list_calendar_clearfix
            ],
            [],
        )
        div_c55: list[bs4.element.Tag] = sum(
            [
                div.find_all(
                    name="div",
                    attrs={
                        "class": "c55",
                    },
                )
                for div in div_fl_right
            ],
            [],
        )
        description: str = div_c55[0].getText()
        answer_content: str = div_c55[1].getText()
        div_box: typing.Iterable[bs4.element.Tag] = soup.find_all(
            name="div",
            attrs={
                "class": "boxbox",
            },
        )
        div_box: bs4.element.Tag = div_box[1]
        div_right: typing.Iterable[bs4.element.Tag] = div_box.find_all(
            name="div",
            attrs={
                "class": "right",
            },
        )
        submitted_content: str = div_right[2].getText()

        div_list_fujian_clearfix: typing.Iterable[bs4.element.Tag] = soup.find_all(
            name="div",
            attrs={
                "class": "list fujian clearfix",
            },
        )
        return ty.HomeworkDetail(
            description=description.strip(),
            answer_content=answer_content.strip(),
            submitted_content=submitted_content.strip(),
            attachment=parser.parse_homework_file(div_list_fujian_clearfix[0])
            if len(div_list_fujian_clearfix) > 0
            else None,
            answer_attachment=parser.parse_homework_file(div_list_fujian_clearfix[1])
            if len(div_list_fujian_clearfix) > 1
            else None,
            submitted_attachment=parser.parse_homework_file(div_list_fujian_clearfix[2])
            if len(div_list_fujian_clearfix) > 2
            else None,
            grade_attachment=parser.parse_homework_file(div_list_fujian_clearfix[3])
            if len(div_list_fujian_clearfix) > 3
            else None,
        )
