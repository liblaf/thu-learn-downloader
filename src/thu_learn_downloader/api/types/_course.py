import enum
from typing import Annotated

import pydantic


class CourseType(enum.StrEnum):
    STUDENT = "student"
    TERCHER = "teacher"


class CourseInfo(pydantic.BaseModel):
    id: Annotated[str, pydantic.Field(validation_alias="wlkcid")]
    name: Annotated[str, pydantic.Field(validation_alias="zywkcm")]
    chinese_name: Annotated[str, pydantic.Field(validation_alias="kcm")]
    english_name: Annotated[str, pydantic.Field(validation_alias="ywkcm")]
    # time_and_location: Never
    # url: Never
    teacher_name: Annotated[str, pydantic.Field(validation_alias="jsm")] = ""
    teacher_number: Annotated[str, pydantic.Field(validation_alias="jsh")]
    course_number: Annotated[str, pydantic.Field(validation_alias="kch")]
    course_index: Annotated[int, pydantic.Field(validation_alias="kxh")]
    # course_type: CourseType
