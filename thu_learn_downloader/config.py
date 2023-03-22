import dataclasses
import sys
from pathlib import Path


@dataclasses.dataclass(kw_only=True)
class Config:
    username: str = "liqin20"
    password: str

    semesters: list[str] = dataclasses.field(default_factory=lambda: ["2022-2023-2"])
    courses: list[str] = dataclasses.field(default_factory=list)

    prefix: Path = Path.home() / "Desktop" / "thu-learn"
    size_limit: int = sys.maxsize
