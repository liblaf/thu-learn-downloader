from . import types

WORK_README = """## {title}

### Contents and Requirements

#### Description

{description}

#### ANS

{ans}

#### Deadline

{deadline}

### My coursework submitted

#### Date

{submit_time}

#### Content

{submit_content}

### Instructors' comments

#### By

{grader_name}

#### Date

{grade_time}

#### Grade

{grade}

#### Comment

{comment}
"""


def dump_work(work: types.Homework) -> str:
    return WORK_README.format(
        title=work.title,
        description=work.description or "",
        ans=work.answer_content or "",
        deadline=str(work.deadline or ""),
        submit_time=str(work.submit_time or ""),
        submit_content=work.submitted_content or "",
        grader_name=work.grader_name or "",
        grade_time=str(work.grade_time or ""),
        grade=work.grade or work.grade_level or "",
        comment=work.grade_content,
    )
