from apps.exams.models import ExamDeployment


def is_exam_active(deployment: ExamDeployment) -> bool:
    return deployment.status == ExamDeployment.StatusChoices.ACTIVATED
