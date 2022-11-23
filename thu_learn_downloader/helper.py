import datetime
import typing
import urllib.parse

import bs4
import requests
import requests.adapters

from . import parser, types, urls


class LearnHelper(requests.Session):
    username: str
    password: str
    status: str = ""

    def __init__(self, username: str, password: str) -> None:
        super().__init__()
        self.username = username
        self.password = password
        self.mount(
            prefix="https://",
            adapter=requests.adapters.HTTPAdapter(
                max_retries=4,
            ),
        )

    @property
    def token(self) -> str:
        return self.cookies.get(name="XSRF-TOKEN", default="")

    def get_with_token(self, url: types.URL) -> requests.Response:
        if url.query:
            assert isinstance(url.query, dict)
            url.query["_csrf"] = self.token
        else:
            url.query = {
                "_csrf": self.token,
            }
        return self.get(url.str())

    def login(self) -> bool:
        response: requests.Response = self.get(urls.LEARN_PREFIX.str())
        soup = bs4.BeautifulSoup(response.text, features="html.parser")
        form = typing.cast(bs4.Tag, soup.select_one("#loginForm"))
        action = typing.cast(str, form["action"])
        payload = urls.id_login_form_data(
            username=self.username,
            password=self.password,
        ).query
        response = self.post(url=action, data=payload)
        soup = bs4.BeautifulSoup(response.text, features="html.parser")
        a = typing.cast(bs4.Tag, soup.select_one("a"))
        href = typing.cast(str, a["href"])
        parse_result = urllib.parse.urlparse(url=href)
        query = urllib.parse.parse_qs(qs=parse_result.query)
        self.status = query["status"][0]
        self.ticket = query["ticket"][0]

        response = self.get(href)

        url = urls.learn_auth_roam(ticket=self.ticket)
        response = self.get(url.str())

        url = urls.learn_student_course_list_page()
        response = self.get(url.str())

        return self.status == "SUCCESS"

    def logout(self) -> None:
        url = urls.learn_logout()
        response = self.post(url.str())

    def get_semester_id_list(self) -> list[str]:
        url = urls.learn_semester_list()
        response = self.get_with_token(url)
        json = response.json()
        return [semester_id for semester_id in json if semester_id]

    def get_current_semester(self) -> types.SemesterInfo:
        url = urls.learn_current_semester()
        response = self.get_with_token(url)
        json = response.json()
        result = json["result"]
        return types.SemesterInfo(
            id=result["id"],
            start_date=datetime.datetime.strptime(result["kssj"], r"%Y-%m-%d").date(),
            end_date=datetime.datetime.strptime(result["jssj"], r"%Y-%m-%d").date(),
            start_year=int(result["xnxq"][0:4]),
            end_year=int(result["xnxq"][5:9]),
            type=typing.cast(types.SemesterType, int(result["xnxq"][10:])),
        )

    def get_course_list(
        self,
        semester_id: str,
        course_type: types.CourseType = types.CourseType.STUDENT,
    ) -> list[types.CourseInfo]:
        url = urls.learn_course_list(semester_id, course_type)
        response = self.get_with_token(url)
        json = response.json()
        result = json["resultList"]
        courses = [
            parser.parse_course_info(course=course, course_type=course_type)
            for course in result
        ]
        return courses

    def get_file_list(
        self,
        course_id: str,
        course_type: types.CourseType = types.CourseType.STUDENT,
    ) -> list[types.File]:
        url = urls.learn_file_classify(course_id=course_id)
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
        if course_type == types.CourseType.STUDENT:
            result = json["object"]
        else:  # teacher
            result = json["object"]["resultList"]

        files = [
            parser.parse_file(
                file=file, course_id=course_id, clazz=clazz, course_type=course_type
            )
            for file in result
        ]
        return files

    def get_homework_list(
        self, course_id: str, course_type: types.CourseType = types.CourseType.STUDENT
    ) -> list[types.Homework]:
        result = []
        url = urls.learn_homework_list_new(course_id=course_id)
        result += self.get_homework_list_at_url(
            url=url,
            status=types.HomeworkStatus(submitted=False, graded=False),
        )
        url = urls.learn_homework_list_submitted(course_id=course_id)
        result += self.get_homework_list_at_url(
            url=url,
            status=types.HomeworkStatus(submitted=True, graded=False),
        )
        url = urls.learn_homework_list_graded(course_id=course_id)
        result += self.get_homework_list_at_url(
            url=url,
            status=types.HomeworkStatus(submitted=True, graded=True),
        )

        return result

    def get_homework_list_at_url(
        self, url: types.URL, status: types.HomeworkStatus
    ) -> list[types.Homework]:
        response = self.get_with_token(url)
        json = response.json()

        result = json["object"]["aaData"]

        def parse_homework(work: dict) -> types.Homework:
            detail = self.parse_homework_detail(
                course_id=work["wlkcid"],  # 课程 ID
                homework_id=work["zyid"],  # 作业 ID
                student_homework_id=work["xszyid"],  # 学生作业 ID
            )

            return types.Homework(
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
                ).str(),
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

        return [parse_homework(work) for work in result]

    def parse_homework_detail(
        self, course_id: str, homework_id: str, student_homework_id: str
    ) -> types.HomeworkDetail:
        url = urls.learn_homework_detail(
            course_id=course_id,
            homework_id=homework_id,
            student_homework_id=student_homework_id,
        )
        response = self.get_with_token(url)
        soup = bs4.BeautifulSoup(markup=response.text, features="html.parser")
        boxboxs = soup.select(".boxbox")
        (
            contents_and_requirements,
            my_coursework_submitted,
            instructors_comments,
        ) = boxboxs

        div_c55s = contents_and_requirements.select(
            "div.list.calendar.clearfix > div.fl.right > div.c55"
        )
        description = div_c55s[0].get_text()
        answer_content = div_c55s[1].get_text()

        submitted_content = my_coursework_submitted.select("div.list > div.right")[
            2
        ].get_text()

        grade_content = typing.cast(
            bs4.Tag, instructors_comments.select_one("div.list.description > div.right")
        ).get_text()

        div_list_fujian_clearfix = soup.select("div.list.fujian.clearfix")

        return types.HomeworkDetail(
            description=description.strip(),
            answer_content=answer_content.strip(),
            submitted_content=submitted_content.strip(),
            grade_content=grade_content.strip(),
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
