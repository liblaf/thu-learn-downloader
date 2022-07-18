import slugify as slug

from . import ty


def slugify(text: str) -> str:
    return ".".join(
        [
            slug.slugify(text=segment, word_boundary=True, allow_unicode=True)
            for segment in text.split(".")
        ]
    )


def parse_semester_type(n: int) -> ty.SemesterType:
    if n == 1:
        return ty.SemesterType.FALL
    elif n == 2:
        return ty.SemesterType.SPRING
    elif n == 3:
        return ty.SemesterType.SUMMER
    else:
        return ty.SemesterType.UNKNOWN


CONTENT_TYPE_MK_MAP: dict[ty.ContentType, str] = {
    ty.ContentType.NOTIFICATION: "kcgg",  # 课程公告
    ty.ContentType.FILE: "kcwj",  # 课程文件
    ty.ContentType.HOMEWORK: "kczy",  # 课程作业
    ty.ContentType.DISCUSSION: "",
    ty.ContentType.QUESTION: "",
}


def get_mk_from_type(type: ty.ContentType) -> str:
    return "mk_" + CONTENT_TYPE_MK_MAP.get(type, "UNKNOWN")
