from apps.exams.models.exam_submissions import ExamSubmission
from apps.users.models import User


class StudentNotFoundError(Exception):
    """학생을 찾을 수 없을 때 발생."""


# 학생의 과목별 점수 조회
def get_student_scores(student_id: int) -> list[dict[str, str | int]]:
    try:
        student = User.objects.get(id=student_id, role=User.Role.STUDENT)
    except User.DoesNotExist as exc:
        raise StudentNotFoundError from exc

    submissions = (
        ExamSubmission.objects.filter(submitter=student)
        .select_related("deployment__exam__subject")
        .order_by("deployment__exam__subject__title")
    )

    return [
        {
            "subject": submission.deployment.exam.subject.title,
            "score": submission.score if submission.score else 0,
        }
        for submission in submissions
    ]
