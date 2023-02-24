import urllib.parse
from urllib.parse import ParseResult

from requests import Request

from . import typing as t

MAX_SIZE = 200
LEARN_PREFIX = "learn.tsinghua.edu.cn"


def make_url(scheme: str = "https", netloc: str = LEARN_PREFIX, path: str = "") -> str:
    return ParseResult(
        scheme=scheme, netloc=netloc, path=path, params="", query="", fragment=""
    ).geturl()


def make_req(
    method: str = "GET",
    url: str = make_url(),
    data: dict = dict(),
    params: dict = dict(),
) -> Request:
    return Request(method=method, url=url, data=data, params=params)


def to_url(request: Request) -> str:
    parse_result: urllib.parse.ParseResult = urllib.parse.urlparse(url=request.url)
    parse_result = urllib.parse.ParseResult(
        scheme=parse_result.scheme,
        netloc=parse_result.netloc,
        path=parse_result.path,
        params=parse_result.params,
        query=urllib.parse.urlencode(query=request.params),
        fragment=parse_result.fragment,
    )
    return urllib.parse.urlunparse(parse_result)


def id_login(action: str, username: str, password: str) -> Request:
    return make_req(
        method="POST",
        url=action,
        data={"i_user": username, "i_pass": password, "atOnce": True},
    )


def learn_auth_roam(ticket: str) -> Request:
    return make_req(
        url=make_url(path="/b/j_spring_security_thauth_roaming_entry"),
        params={"ticket": ticket},
    )


def learn_student_course_list_page() -> Request:
    return make_req(url=make_url(path="/f/wlxt/index/course/student/"))


def learn_semester_list() -> Request:
    return make_req(url=make_url(path="/b/wlxt/kc/v_wlkc_xs_xktjb_coassb/queryxnxq"))


def learn_course_list(
    semester: str, course_type: t.CourseType = t.CourseType.STUDENT
) -> Request:
    match course_type:
        case t.CourseType.STUDENT:
            return make_req(
                url=make_url(
                    path=f"/b/wlxt/kc/v_wlkc_xs_xkb_kcb_extend/student/loadCourseBySemesterId/{semester}"
                )
            )
        case t.CourseType.TEACHER:
            raise NotImplementedError()


def learn_file_list(
    course_id: str, course_type: t.CourseType = t.CourseType.STUDENT
) -> Request:
    match course_type:
        case t.CourseType.STUDENT:
            return make_req(
                url=make_url(
                    path="/b/wlxt/kj/wlkc_kjxxb/student/kjxxbByWlkcidAndSizeForStudent"
                ),
                params={"wlkcid": course_id, "size": MAX_SIZE},
            )
        case t.CourseType.TEACHER:
            raise NotImplementedError()


def learn_file_clazz(course_id: str) -> Request:
    return make_req(
        url=make_url(path="/b/wlxt/kj/wlkc_kjflb/student/pageList"),
        params={"wlkcid": course_id},
    )


def learn_file_download(
    file_id: str,
    course_id: str,
    course_type: t.CourseType = t.CourseType.STUDENT,
) -> Request:
    match course_type:
        case t.CourseType.STUDENT:
            return make_req(
                url=make_url(path="/b/wlxt/kj/wlkc_kjxxb/student/downloadFile"),
                params={"sfgk": 0, "wjid": file_id},
            )
        case t.CourseType.TEACHER:
            raise NotImplementedError()


def learn_homework_list_new(course_id: str) -> Request:
    return make_req(
        url=make_url(path="/b/wlxt/kczy/zy/student/index/zyListWj"),
        params={"wlkcid": course_id, "size": MAX_SIZE},
    )


def learn_homework_list_submitted(course_id: str) -> Request:
    return make_req(
        url=make_url(path="/b/wlxt/kczy/zy/student/index/zyListYjwg"),
        params={"wlkcid": course_id, "size": MAX_SIZE},
    )


def learn_homework_list_graded(course_id: str) -> Request:
    return make_req(
        url=make_url(path="/b/wlxt/kczy/zy/student/index/zyListYpg"),
        params={"wlkcid": course_id, "size": MAX_SIZE},
    )


def learn_homework_detail(
    course_id: str, homework_id: str, student_homework_id: str
) -> Request:
    return make_req(
        url=make_url(path="/f/wlxt/kczy/zy/student/viewCj"),
        params={
            "wlkcid": course_id,
            "zyid": homework_id,
            "xszyid": student_homework_id,
        },
    )
