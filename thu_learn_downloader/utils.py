import slugify as slug

from . import types


def slugify(text: str) -> str:
    return ".".join(
        [
            slug.slugify(text=segment, word_boundary=True, allow_unicode=True)
            for segment in text.split(".")
        ]
    )


def parse_semester_type(n: int) -> types.SemesterType:
    if n == 1:
        return types.SemesterType.FALL
    elif n == 2:
        return types.SemesterType.SPRING
    elif n == 3:
        return types.SemesterType.SUMMER
    else:
        return types.SemesterType.UNKNOWN


CONTENT_TYPE_MK_MAP: dict[types.ContentType, str] = {
    types.ContentType.NOTIFICATION: "kcgg",  # 课程公告
    types.ContentType.FILE: "kcwj",  # 课程文件
    types.ContentType.HOMEWORK: "kczy",  # 课程作业
    types.ContentType.DISCUSSION: "",
    types.ContentType.QUESTION: "",
}


def get_mk_from_type(type: types.ContentType) -> str:
    return "mk_" + CONTENT_TYPE_MK_MAP.get(type, "UNKNOWN")
