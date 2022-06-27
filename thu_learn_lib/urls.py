import dataclasses

from . import ty as types
from . import utils


LEARN_PREFIX = "https://learn.tsinghua.edu.cn"
REGISTRAR_PREFIX = "https://zhjw.cic.tsinghua.edu.cn"


MAX_SIZE = 200


@dataclasses.dataclass
class URL:
    url: str = None
    params: dict = None

    def __str__(self) -> str:
        if self.params:
            return (
                self.url
                + "?"
                + "&".join([f"{key}={value}" for key, value in self.params.items()])
            )


def id_login() -> URL:
    return URL(
        url="https://id.tsinghua.edu.cn/do/off/ui/auth/login/post/bb5df85216504820be7bba2b0ae1535b/0?/login.do"
    )


def id_login_form_data(username: str, password: str) -> URL:
    credential = {}
    credential["i_user"] = username
    credential["i_pass"] = password
    credential["atOnce"] = True
    return URL(params=credential)


def learn_auth_roam(ticket: str) -> URL:
    return URL(
        url=f"{LEARN_PREFIX}/b/j_spring_security_thauth_roaming_entry",
        params={"ticket": ticket},
    )


def learn_logout() -> URL:
    return URL(url=f"{LEARN_PREFIX}/f/j_spring_security_logout")


def learn_student_course_list_page() -> URL:
    return URL(url=f"{LEARN_PREFIX}/f/wlxt/index/course/student/")


def learn_semester_list() -> URL:
    return URL(url=f"{LEARN_PREFIX}/b/wlxt/kc/v_wlkc_xs_xktjb_coassb/queryxnxq")


def learn_current_semester() -> URL:
    return URL(url=f"{LEARN_PREFIX}/b/kc/zhjw_v_code_xnxq/getCurrentAndNextSemester")


def learn_course_list(semester: str, course_type: types.CourseType) -> URL:
    if course_type == types.CourseType.STUDENT:
        return URL(
            url=f"{LEARN_PREFIX}/b/wlxt/kc/v_wlkc_xs_xkb_kcb_extend/student/loadCourseBySemesterId/{semester}"
        )
    else:
        return URL(
            url=f"{LEARN_PREFIX}/b/kc/v_wlkc_kcb/queryAsorCoCourseList/{semester}/0"
        )


def learn_course_url(course_id: str, course_type: str) -> URL:
    return URL(
        url=f"{LEARN_PREFIX}/f/wlxt/index/course/{course_type}/course",
        params={"wlkcid": course_id},
    )


def learn_course_time_location(course_id: str) -> URL:
    return URL(
        url=f"{LEARN_PREFIX}/b/kc/v_wlkc_xk_sjddb/detail", params={"id": course_id}
    )


def learn_teacher_course_url(course_id: str) -> URL:
    return URL(
        url=f"{LEARN_PREFIX}/f/wlxt/index/course/teacher/course",
        params={"wlkcid": course_id},
    )


def learn_file_list(course_id: str, course_type: types.CourseType) -> URL:
    if course_type == types.CourseType.STUDENT:
        return URL(
            url=f"{LEARN_PREFIX}/b/wlxt/kj/wlkc_kjxxb/student/kjxxbByWlkcidAndSizeForStudent",
            params={"wlkcid": course_id, "size": MAX_SIZE},
        )
    else:
        return URL(
            url=f"{LEARN_PREFIX}/b/wlxt/kj/v_kjxxb_wjwjb/teacher/queryByWlkcid",
            params={"wlkcid": course_id, "size": MAX_SIZE},
        )


def learn_file_classify(course_id: str) -> URL:
    return URL(
        url=f"{LEARN_PREFIX}/b/wlxt/kj/wlkc_kjflb/student/pageList",
        params={"wlkcid": course_id},
    )


def learn_file_download(file_id: str, course_type: str, course_id: str) -> URL:
    if course_type == types.CourseType.STUDENT:
        return URL(
            url=f"{LEARN_PREFIX}/b/wlxt/kj/wlkc_kjxxb/student/downloadFile",
            params={"sfgk": 0, "wjid": file_id},
        )
    else:
        return URL(
            url=f"{LEARN_PREFIX}/f/wlxt/kj/wlkc_kjxxb/teacher/beforeView",
            params={"id": file_id, "wlkcid": course_id},
        )


def learn_file_preview(
    type: types.ContentType,
    file_id: str,
    course_type: types.CourseType,
    first_page_only: bool = False,
) -> URL:
    return URL(
        url=f"{LEARN_PREFIX}/f/wlxt/kc/wj_wjb/{course_type}/beforePlay",
        params={
            "wjid": file_id,
            "mk": utils.get_mk_from_type(type),
            "browser": -1,
            "sfgk": 0,
            "pageType": "first" if first_page_only else "all",
        },
    )


def learn_notification_list(course_id: str, course_type: types.CourseType) -> URL:
    if course_type == types.CourseType.STUDENT:
        return URL(
            url=f"{LEARN_PREFIX}/b/wlxt/kcgg/wlkc_ggb/student/kcggListXs",
            params={"wlkcid": course_id, "size": MAX_SIZE},
        )
    else:
        return URL(
            url=f"{LEARN_PREFIX}/b/wlxt/kcgg/wlkc_ggb/teacher/kcggList",
            params={"wlkcid": course_id, "size": MAX_SIZE},
        )


def learn_notification_detail(
    course_id: str, notification_id: str, course_type: types.CourseType
) -> URL:
    if course_type == types.CourseType.STUDENT:
        return URL(
            url=f"{LEARN_PREFIX}/f/wlxt/kcgg/wlkc_ggb/student/beforeViewXs",
            params={"wlkcid": course_id, "id": notification_id},
        )
    else:
        return URL(
            url=f"{LEARN_PREFIX}/f/wlxt/kcgg/wlkc_ggb/teacher/beforeViewJs",
            params={"wlkcid": course_id, "id": notification_id},
        )


def learn_notification_edit(course_type: types.CourseType) -> URL:
    return URL(url=f"{LEARN_PREFIX}/b/wlxt/kcgg/wlkc_ggb/{course_type}/editKcgg")


def learn_homework_list_source(course_id: str) -> dict[str]:
    return [
        {
            "url": learn_homework_list_new(course_id),
            "status": {"submitted": False, "graded": False,},
        },
        {
            "url": learn_homework_list_submitted(course_id),
            "status": {"submitted": True, "graded": False,},
        },
        {
            "url": learn_homework_list_graded(course_id),
            "status": {"submitted": True, "graded": True,},
        },
    ]


def learn_homework_list_new(course_id: str) -> URL:
    return URL(
        url=f"{LEARN_PREFIX}/b/wlxt/kczy/zy/student/index/zyListWj",
        params={"wlkcid": course_id, "size": MAX_SIZE},
    )


def learn_homework_list_submitted(course_id: str) -> URL:
    return URL(
        url=f"{LEARN_PREFIX}/b/wlxt/kczy/zy/student/index/zyListYjwg",
        params={"wlkcid": course_id, "size": MAX_SIZE},
    )


def learn_homework_list_graded(course_id: str) -> URL:
    return URL(
        url=f"{LEARN_PREFIX}/b/wlxt/kczy/zy/student/index/zyListYpg",
        params={"wlkcid": course_id, "size": MAX_SIZE},
    )


def learn_homework_detail(
    course_id: str, homework_id: str, student_homework_id: str
) -> URL:
    return URL(
        url=f"{LEARN_PREFIX}/f/wlxt/kczy/zy/student/viewCj",
        params={
            "wlkcid": course_id,
            "zyid": homework_id,
            "xszyid": student_homework_id,
        },
    )


def learn_homework_download(course_id: str, attachment_id: str) -> URL:
    return URL(
        url=f"{LEARN_PREFIX}/b/wlxt/kczy/zy/student/downloadFile/{course_id}/{attachment_id}"
    )


def learn_homework_submit(course_id: str, student_homework_id: str) -> URL:
    return URL(
        url=f"{LEARN_PREFIX}/f/wlxt/kczy/zy/student/tijiao",
        params={"wlkcid": course_id, "xszyid": student_homework_id},
    )


def learn_discussion_list(course_id: str, course_type: types.CourseType) -> URL:
    return URL(
        url=f"{LEARN_PREFIX}/b/wlxt/bbs/bbs_tltb/{course_type}/kctlList",
        params={"wlkcid": course_id, "size": MAX_SIZE},
    )


def learn_discussion_detail(
    course_id: str,
    board_id: str,
    discussion_id: str,
    course_type: types.CourseType,
    tab_id=1,
) -> URL:
    return URL(
        url=f"{LEARN_PREFIX}/f/wlxt/bbs/bbs_tltb/{course_type}/viewTlById",
        params={
            "wlkcid": course_id,
            "id": discussion_id,
            "tabbh": tab_id,
            "bqid": board_id,
        },
    )


def learn_question_list_answered(course_id: str, course_type: types.CourseType) -> URL:
    return URL(
        url=f"{LEARN_PREFIX}/b/wlxt/bbs/bbs_tltb/{course_type}/kcdyList",
        params={"wlkcid": course_id, "size": MAX_SIZE},
    )


def learn_question_detail(
    course_id: str, question_id: str, course_type: types.CourseType
) -> URL:
    if course_type == types.CourseType.STUDENT:
        return URL(
            url=f"{LEARN_PREFIX}/f/wlxt/bbs/bbs_kcdy/student/viewDyById",
            params={"wlkcid": course_id, "id": question_id},
        )
    else:
        return URL(
            url=f"{LEARN_PREFIX}/f/wlxt/bbs/bbs_kcdy/teacher/beforeEditDy",
            params={"wlkcid": course_id, "id": question_id},
        )


def registrar_ticket_form_data() -> URL:
    return URL(params={"appId": "ALL_ZHJW"})


def registrar_ticket() -> URL:
    return URL(url=f"{LEARN_PREFIX}/b/wlxt/common/auth/gnt")


def registrar_auth(ticket: str) -> URL:
    return URL(
        url=f"{REGISTRAR_PREFIX}/j_acegi_login.do",
        params={"url": "/", "ticket": ticket},
    )


def registrar_calendar(
    start_date: str, end_date: str, graduate: bool = False, callback_name="unknown"
) -> URL:
    return URL(
        url=f"{REGISTRAR_PREFIX}/jxmh_out.do",
        params={
            "m": ("yjs" if graduate else "bks") + "_jxrl_all",
            "p_start_date": start_date,
            "p_end_date": end_date,
            "jsoncallback": callback_name,
        },
    )
