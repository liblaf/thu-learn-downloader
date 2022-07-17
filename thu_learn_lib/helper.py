import urllib
import bs4
import datetime
import re
import requests


from . import ty as types
from . import urls


class LearnHelper(requests.Session):
    def __init__(self) -> None:
        super().__init__()

    @property
    def token(self) -> str:
        return self.cookies["XSRF-TOKEN"] if "XSRF-TOKEN" in self.cookies else None

    def get_with_token(self, url: str, params: dict = None) -> requests.Response:
        if params is None:
            params = {"_csrf": self.token}
        else:
            params["_csrf"] = self.token
        return self.get(url=url, params=params)

    def login(self, username: str, password: str) -> bool:
        response = self.get(urls.LEARN_PREFIX)
        soup = bs4.BeautifulSoup(response.text, features="html.parser")
        form = soup.find(
            name="form", attrs={"class": "w", "id": "loginForm", "method": "post"}
        )

        payload = urls.id_login_form_data(username=username, password=password).params
        response = self.post(url=form["action"], data=payload)
        soup = bs4.BeautifulSoup(response.text, features="html.parser")
        a = soup.find(name="a")
        pattern = rf"{urls.LEARN_PREFIX}/f/login.do\?status=(\w*)&ticket=(\w*)"
        match = re.match(pattern=pattern, string=a["href"])
        self.success = match.group(1) == "SUCCESS"
        self.ticket = match.group(2)

        response = self.get(a["href"])
        soup = bs4.BeautifulSoup(response.text, features="html.parser")
        script = soup.find(name="script", type="text/javaScript")
        pattern = r"\s*window.location=\"/b/j_spring_security_thauth_roaming_entry\?ticket=(\w*)\";\s*"
        match = re.match(pattern=pattern, string=script.text)
        self.ticket = match.group(1)

        request = urls.learn_auth_roam(ticket=self.ticket)
        response = self.get(url=request.url, params=request.params)

        request = urls.learn_student_course_list_page()
        response = self.get(url=request.url, params=request.params)

        print(
            f"User {username} login successfully"
            if self.success
            else f"User {username} login failed!"
        )
        return self.success

    def logout(self) -> None:
        request = urls.learn_logout()
        response = self.post(url=request.url)

    def get_semester_id_list(self) -> list:
        request = urls.learn_semester_list()
        response = self.get_with_token(url=request.url, params=request.params)
        json = response.json()
        return [x for x in json if x]

    def get_current_semester(self) -> types.SemesterInfo:
        request = urls.learn_current_semester()
        response = self.get_with_token(url=request.url, params=request.params)
        json = response.json()
        result = json["result"]
        return types.SemesterInfo(
            id=result["id"],
            start_date=datetime.datetime.strptime(result["kssj"], r"%Y-%m-%d").date(),
            end_date=datetime.datetime.strptime(result["jssj"], r"%Y-%m-%d").date(),
            start_year=int(result["xnxq"][0:4]),
            end_year=int(result["xnxq"][5:9]),
            type=int(result["xnxq"][10:]),
        )

    def get_course_list(
        self, semester_id: str, course_type: types.CourseType = types.CourseType.STUDENT
    ) -> list[types.CourseInfo]:
        request = urls.learn_course_list(semester_id, course_type)
        response = self.get_with_token(url=request.url, params=request.params)
        json = response.json()
        result = json["resultList"]

        def mapper(course: dict):
            request = urls.learn_course_time_location(course["wlkcid"])
            response = self.get_with_token(request.url, request.params)
            return types.CourseInfo(
                id=course["wlkcid"],
                name=course["kcm"],
                english_name=course["ywkcm"],
                time_and_location=response.json(),
                url=str(urls.learn_course_url(course["wlkcid"], course_type)),
                teacher_name=course["jsm"]
                if course["jsm"]
                else "",  # teacher can not fetch this
                teacher_number=course["jsh"],
                course_number=course["kch"],
                course_index=int(
                    course["kxh"]
                ),  # course["kxh"] could be string (teacher mode) or number (student mode)
                course_type=course_type,
            )

        courses = list(map(mapper, result))
        return courses

    def get_file_list(
        self, course_id: str, course_type: types.CourseType = types.CourseType.STUDENT
    ) -> list[types.File]:
        request = urls.learn_file_classify(course_id=course_id)
        response = self.get_with_token(url=request.url, params=request.params)
        json = response.json()
        records = json["object"]["rows"]
        clazz = {}
        for record in records:
            clazz[record["kjflid"]] = record["bt"]  # 课件分类 ID, 标题

        request = urls.learn_file_list(course_id=course_id, course_type=course_type)
        response = self.get_with_token(request.url, request.params)
        json = response.json()
        result = []
        if course_type == types.CourseType.STUDENT:
            result = json["object"]
        else:  # teacher
            result = json["object"]["resultList"]

        def mapper(file: dict) -> types.File:
            title: str = file["bt"]
            download_url: str = urls.learn_file_download(
                file_id=file["wjid"]
                if course_type == types.CourseType.STUDENT
                else file["id"],
                course_type=course_type,
                course_id=course_id,
            )
            preview_url = None
            return types.File(
                id=file["wjid"],  # 文件 ID
                title=file["bt"],  # 标题
                description=file["ms"],  # 描述
                raw_size=file["wjdx"],  # 文件大小
                size=file["fileSize"],
                upload_time=datetime.datetime.strptime(
                    file["scsj"], r"%Y-%m-%d %H:%M"
                ),  # 上传时间
                download_url=str(download_url),
                preview_url=str(preview_url),
                is_new=file["isNew"],
                marked_important=file["sfqd"] == 1,  # 是否强调
                visit_count=file["llcs"] or 0,  # 浏览次数
                download_count=file["xzcs"] or 0,  # 下载次数
                file_type=file["wjlx"],  # 文件类型
                remote_file=types.RemoteFile(
                    id=file["wjid"],  # 文件 ID
                    name=title,
                    download_url=str(download_url),
                    preview_url=str(preview_url),
                    size=file["fileSize"],
                ),
                clazz=clazz[file["kjflid"]],  # 课件分类 ID
            )

        return list(map(mapper, result))

    def get_homework_list(
        self, course_id: str, course_type: types.CourseType = types.CourseType.STUDENT
    ) -> list[types.Homework]:
        result = []
        request = urls.learn_homework_list_new(course_id=course_id)
        result += self.get_homework_list_at_url(
            request=request, status=types.HomeworkStatus(submitted=False, graded=False)
        )
        request = urls.learn_homework_list_submitted(course_id=course_id)
        result += self.get_homework_list_at_url(
            request=request, status=types.HomeworkStatus(submitted=True, graded=False)
        )
        request = urls.learn_homework_list_graded(course_id=course_id)
        result += self.get_homework_list_at_url(
            request=request, status=types.HomeworkStatus(submitted=True, graded=True)
        )

        return result

    def get_homework_list_at_url(
        self, request: urls.URL, status: types.HomeworkStatus
    ) -> list[types.Homework]:
        response = self.get_with_token(url=request.url, params=request.params)
        json = response.json()

        result = json["object"]["aaData"]

        def mapper(work: dict) -> types.Homework:
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
    ) -> types.HomeworkDetail:
        request = urls.learn_homework_detail(
            course_id=course_id,
            homework_id=homework_id,
            student_homework_id=student_homework_id,
        )
        response = self.get_with_token(request.url, request.params)
        text = response.text
        soup = bs4.BeautifulSoup(markup=text, features="html.parser")

        div_list_calendar_clearfix = soup.find_all(
            name="div", attrs={"class": "list calendar clearfix"}
        )
        div_fl_right = sum(
            [
                div.find_all(name="div", attrs={"class": "fl right"})
                for div in div_list_calendar_clearfix
            ],
            [],
        )
        div_c55 = sum(
            [div.find_all(name="div", attrs={"class": "c55"}) for div in div_fl_right],
            [],
        )
        description = div_c55[0].getText()
        answer_content = div_c55[1].getText()
        div_box = soup.find_all(name="div", attrs={"class": "boxbox"})
        div_box = div_box[1]
        div_right = div_box.find_all(name="div", attrs={"class": "right"})
        submitted_content = div_right = div_right[2].getText()

        div_list_fujian_clearfix = soup.find_all(
            name="div", attrs={"class": "list fujian clearfix"}
        )
        return types.HomeworkDetail(
            description=description.strip(),
            answer_content=answer_content.strip(),
            submitted_content=submitted_content.strip(),
            attachment=self.parse_homework_file(div_list_fujian_clearfix[0])
            if len(div_list_fujian_clearfix) > 0
            else None,
            answer_attachment=self.parse_homework_file(div_list_fujian_clearfix[1])
            if len(div_list_fujian_clearfix) > 1
            else None,
            submitted_attachment=self.parse_homework_file(div_list_fujian_clearfix[2])
            if len(div_list_fujian_clearfix) > 2
            else None,
            grade_attachment=self.parse_homework_file(div_list_fujian_clearfix[3])
            if len(div_list_fujian_clearfix) > 3
            else None,
        )

    def parse_homework_file(self, div) -> types.RemoteFile:
        ftitle = div.find(name="span", attrs={"class": "ftitle"}) or div.find(
            name="span", attrs={"class", "ft"}
        )
        if not ftitle:
            return None
        a = ftitle.find(name="a")
        size = div.find(name="span", attrs={"class": "color_999"})
        size = size.getText()
        params = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(a["href"]).query))
        attachment_id = params["fileId"]
        download_url = urls.LEARN_PREFIX + (
            params["downloadUrl"] if "downloadUrl" in params else a["href"]
        )
        return types.RemoteFile(
            id=attachment_id,
            name=a.getText(),
            download_url=download_url,
            preview_url=None,
            size=size.strip(),
        )
