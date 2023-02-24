from pathlib import Path

from rich.style import Style

from . import typing as t

BS_FEATURES = "html.parser"
CHUNK_SIZE = 1024 * 1024
DEFAULT_PREFIX = Path.home() / "Desktop" / "thu-learn"
MAX_ACTIVE_TASKS = 16


FAILURE_PREFIX = "[reverse] FAILURE [/]"
RETRY_PREFIX = "[reverse] RETRY [/]"
SKIPPED_PREFIX = "[reverse] SKIPPED [/]"
SUCCESS_PREFIX = "[reverse] SUCCESS [/]"
HOMEWORK_README = """## {title}

### Contents and Requirements

- Starts : {starts}
- Deadline : {deadline}

#### Description

{description}

#### ANS

{ans}

### My coursework submitted

- Date : {submit_time}

#### Content

{submit_content}

### Instructors' comments

- By : {grader_name}
- Date : {grade_time}
- Grade : {grade}

#### Comment

{comment}
"""


SEASONS: dict[int, t.SemesterSeason] = {
    1: t.SemesterSeason.FALL,
    2: t.SemesterSeason.SPRING,
    3: t.SemesterSeason.SUMMER,
}


DOCUMENT_STYLE = Style(color="bright_magenta")
HOMEWORK_STYLE = Style(color="bright_cyan")
