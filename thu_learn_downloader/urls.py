from . import types, utils

LEARN_PREFIX = types.URL(netloc="learn.tsinghua.edu.cn")
REGISTRAR_PREFIX = types.URL(netloc="zhjw.cic.tsinghua.edu.cn")


MAX_SIZE = 200


def id_login() -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path="/do/off/ui/auth/login/post/bb5df85216504820be7bba2b0ae1535b/0",
        query="/login.do",
    )


def id_login_form_data(username: str, password: str) -> types.URL:
    return types.URL(
        query={
            "i_user": username,
            "i_pass": password,
            "atOnce": "true",
        },
    )


def learn_auth_roam(ticket: str) -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path="/b/j_spring_security_thauth_roaming_entry",
        query={
            "ticket": ticket,
        },
    )


def learn_logout() -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path="/f/j_spring_security_logout",
    )


def learn_student_course_list_page() -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path="/f/wlxt/index/course/student/",
    )


def learn_semester_list() -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path="/b/wlxt/kc/v_wlkc_xs_xktjb_coassb/queryxnxq",
    )


def learn_current_semester() -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path="/b/kc/zhjw_v_code_xnxq/getCurrentAndNextSemester",
    )


def learn_course_list(semester: str, course_type: types.CourseType) -> types.URL:
    if course_type == types.CourseType.STUDENT:
        return types.URL(
            netloc=LEARN_PREFIX.netloc,
            path=f"/b/wlxt/kc/v_wlkc_xs_xkb_kcb_extend/student/loadCourseBySemesterId/{semester}",
        )
    else:
        return types.URL(
            netloc=LEARN_PREFIX.netloc,
            path=f"/b/kc/v_wlkc_kcb/queryAsorCoCourseList/{semester}/0",
        )


def learn_course_url(course_id: str, course_type: str) -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path=f"/f/wlxt/index/course/{course_type}/course",
        query={
            "wlkcid": course_id,
        },
    )


def learn_course_time_location(course_id: str) -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path="/b/kc/v_wlkc_xk_sjddb/detail",
        query={
            "id": course_id,
        },
    )


def learn_teacher_course_url(course_id: str) -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path="/f/wlxt/index/course/teacher/course",
        query={
            "wlkcid": course_id,
        },
    )


def learn_file_list(course_id: str, course_type: types.CourseType) -> types.URL:
    if course_type == types.CourseType.STUDENT:
        return types.URL(
            netloc=LEARN_PREFIX.netloc,
            path="/b/wlxt/kj/wlkc_kjxxb/student/kjxxbByWlkcidAndSizeForStudent",
            query={
                "wlkcid": course_id,
                "size": MAX_SIZE,
            },
        )
    else:
        return types.URL(
            netloc=LEARN_PREFIX.netloc,
            path="/b/wlxt/kj/v_kjxxb_wjwjb/teacher/queryByWlkcid",
            query={
                "wlkcid": course_id,
                "size": MAX_SIZE,
            },
        )


def learn_file_classify(course_id: str) -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path="/b/wlxt/kj/wlkc_kjflb/student/pageList",
        query={
            "wlkcid": course_id,
        },
    )


def learn_file_download(file_id: str, course_type: str, course_id: str) -> types.URL:
    if course_type == types.CourseType.STUDENT:
        return types.URL(
            netloc=LEARN_PREFIX.netloc,
            path="/b/wlxt/kj/wlkc_kjxxb/student/downloadFile",
            query={
                "sfgk": 0,
                "wjid": file_id,
            },
        )
    else:
        return types.URL(
            netloc=LEARN_PREFIX.netloc,
            path="/f/wlxt/kj/wlkc_kjxxb/teacher/beforeView",
            query={
                "id": file_id,
                "wlkcid": course_id,
            },
        )


def learn_file_preview(
    type: types.ContentType,
    file_id: str,
    course_type: types.CourseType,
    first_page_only: bool = False,
) -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path=f"/f/wlxt/kc/wj_wjb/{course_type}/beforePlay",
        query={
            "wjid": file_id,
            "mk": utils.get_mk_from_type(type),
            "browser": -1,
            "sfgk": 0,
            "pageType": "first" if first_page_only else "all",
        },
    )


def learn_notification_list(course_id: str, course_type: types.CourseType) -> types.URL:
    if course_type == types.CourseType.STUDENT:
        return types.URL(
            netloc=LEARN_PREFIX.netloc,
            path="/b/wlxt/kcgg/wlkc_ggb/student/kcggListXs",
            query={
                "wlkcid": course_id,
                "size": MAX_SIZE,
            },
        )
    else:
        return types.URL(
            netloc=LEARN_PREFIX.netloc,
            path="/b/wlxt/kcgg/wlkc_ggb/teacher/kcggList",
            query={
                "wlkcid": course_id,
                "size": MAX_SIZE,
            },
        )


def learn_notification_detail(
    course_id: str, notification_id: str, course_type: types.CourseType
) -> types.URL:
    if course_type == types.CourseType.STUDENT:
        return types.URL(
            netloc=LEARN_PREFIX.netloc,
            path="/f/wlxt/kcgg/wlkc_ggb/student/beforeViewXs",
            query={
                "wlkcid": course_id,
                "id": notification_id,
            },
        )
    else:
        return types.URL(
            netloc=LEARN_PREFIX.netloc,
            path="/f/wlxt/kcgg/wlkc_ggb/teacher/beforeViewJs",
            query={
                "wlkcid": course_id,
                "id": notification_id,
            },
        )


def learn_notification_edit(course_type: types.CourseType) -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path=f"/b/wlxt/kcgg/wlkc_ggb/{course_type}/editKcgg",
    )


def learn_homework_list_source(course_id: str) -> list[dict]:
    return [
        {
            "url": learn_homework_list_new(course_id),
            "status": types.HomeworkStatus(submitted=False, graded=False),
        },
        {
            "url": learn_homework_list_submitted(course_id),
            "status": types.HomeworkStatus(submitted=True, graded=False),
        },
        {
            "url": learn_homework_list_graded(course_id),
            "status": types.HomeworkStatus(submitted=True, graded=True),
        },
    ]


def learn_homework_list_new(course_id: str) -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path="/b/wlxt/kczy/zy/student/index/zyListWj",
        query={
            "wlkcid": course_id,
            "size": MAX_SIZE,
        },
    )


def learn_homework_list_submitted(course_id: str) -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path="/b/wlxt/kczy/zy/student/index/zyListYjwg",
        query={
            "wlkcid": course_id,
            "size": MAX_SIZE,
        },
    )


def learn_homework_list_graded(course_id: str) -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path="/b/wlxt/kczy/zy/student/index/zyListYpg",
        query={
            "wlkcid": course_id,
            "size": MAX_SIZE,
        },
    )


def learn_homework_detail(
    course_id: str, homework_id: str, student_homework_id: str
) -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path="/f/wlxt/kczy/zy/student/viewCj",
        query={
            "wlkcid": course_id,
            "zyid": homework_id,
            "xszyid": student_homework_id,
        },
    )


def learn_homework_download(course_id: str, attachment_id: str) -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path=f"/b/wlxt/kczy/zy/student/downloadFile/{course_id}/{attachment_id}",
    )


def learn_homework_submit(course_id: str, student_homework_id: str) -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path="/f/wlxt/kczy/zy/student/tijiao",
        query={
            "wlkcid": course_id,
            "xszyid": student_homework_id,
        },
    )


def learn_discussion_list(course_id: str, course_type: types.CourseType) -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path=f"/b/wlxt/bbs/bbs_tltb/{course_type}/kctlList",
        query={
            "wlkcid": course_id,
            "size": MAX_SIZE,
        },
    )


def learn_discussion_detail(
    course_id: str,
    board_id: str,
    discussion_id: str,
    course_type: types.CourseType,
    tab_id=1,
) -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path=f"/f/wlxt/bbs/bbs_tltb/{course_type}/viewTlById",
        query={
            "wlkcid": course_id,
            "id": discussion_id,
            "tabbh": tab_id,
            "bqid": board_id,
        },
    )


def learn_question_list_answered(
    course_id: str, course_type: types.CourseType
) -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path=f"/b/wlxt/bbs/bbs_tltb/{course_type}/kcdyList",
        query={
            "wlkcid": course_id,
            "size": MAX_SIZE,
        },
    )


def learn_question_detail(
    course_id: str, question_id: str, course_type: types.CourseType
) -> types.URL:
    if course_type == types.CourseType.STUDENT:
        return types.URL(
            netloc=LEARN_PREFIX.netloc,
            path="/f/wlxt/bbs/bbs_kcdy/student/viewDyById",
            query={
                "wlkcid": course_id,
                "id": question_id,
            },
        )
    else:
        return types.URL(
            netloc=LEARN_PREFIX.netloc,
            path="/f/wlxt/bbs/bbs_kcdy/teacher/beforeEditDy",
            query={
                "wlkcid": course_id,
                "id": question_id,
            },
        )


def registrar_ticket_form_data() -> types.URL:
    return types.URL(
        query={
            "appId": "ALL_ZHJW",
        },
    )


def registrar_ticket() -> types.URL:
    return types.URL(
        netloc=LEARN_PREFIX.netloc,
        path="/b/wlxt/common/auth/gnt",
    )


def registrar_auth(ticket: str) -> types.URL:
    return types.URL(
        netloc=REGISTRAR_PREFIX.netloc,
        path="/j_acegi_login.do",
        query={
            "url": "/",
            "ticket": ticket,
        },
    )


def registrar_calendar(
    start_date: str,
    end_date: str,
    graduate: bool = False,
    callback_name: str = "unknown",
) -> types.URL:
    return types.URL(
        netloc=REGISTRAR_PREFIX.netloc,
        path="/jxmh_out.do",
        query={
            "m": ("yjs" if graduate else "bks") + "_jxrl_all",
            "p_start_date": start_date,
            "p_end_date": end_date,
            "jsoncallback": callback_name,
        },
    )
