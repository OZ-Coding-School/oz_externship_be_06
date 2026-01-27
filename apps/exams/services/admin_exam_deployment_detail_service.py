from typing import Any

from apps.courses.models.cohort_students import CohortStudent
from apps.exams.models import ExamDeployment


class ExamDeploymentDetailNotFoundError(Exception):
    """배포 상세 조회 대상이 없을 때 발생."""


def get_exam_deployment_detail(deployment_id: int) -> dict[str, Any]:
    deployment = (
        ExamDeployment.objects.select_related("exam__subject", "cohort__course").filter(id=deployment_id).first()
    )
    if not deployment:
        raise ExamDeploymentDetailNotFoundError

    submitted_count = deployment.submissions.values("submitter_id").distinct().count()
    total_students = CohortStudent.objects.filter(cohort_id=deployment.cohort_id).count()
    not_submitted_count = max(total_students - submitted_count, 0)

    course = deployment.cohort.course
    cohort_display = f"{course.name} {deployment.cohort.number}기"
    questions = deployment.questions_snapshot_json
    if not isinstance(questions, list):
        questions = []

    return {
        "id": deployment.id,
        "access_code": deployment.access_code,
        "cohort": {
            "id": deployment.cohort.id,
            "number": deployment.cohort.number,
            "display": cohort_display,
            "course": {"id": course.id, "name": course.name, "tag": course.tag},
        },
        "submit_count": submitted_count,
        "not_submitted_count": not_submitted_count,
        "duration_time": deployment.duration_time,
        "open_at": deployment.open_at,
        "close_at": deployment.close_at,
        "created_at": deployment.created_at,
        "exam": {
            "id": deployment.exam.id,
            "title": deployment.exam.title,
            "thumbnail_img_url": deployment.exam.thumbnail_img_url,
            "questions": questions,
        },
        "subject": {
            "id": deployment.exam.subject.id,
            "name": deployment.exam.subject.title,
        },
    }
