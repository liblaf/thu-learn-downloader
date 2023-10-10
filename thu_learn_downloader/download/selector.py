from collections.abc import Sequence

from pydantic import BaseModel


class Selector(BaseModel):
    semesters: Sequence[str] = []
    courses: Sequence[str] = []
    document: bool = True
    homework: bool = True
