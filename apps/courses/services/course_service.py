from typing import Any

from django.db.models import QuerySet

from apps.courses.models import CohortStudent, Course


class CourseNotFoundError(Exception):
    pass


class CourseHasStudentsError(Exception):
    pass


# 전체 과정 목록 조회
def get_course_list() -> QuerySet[Course]:
    return Course.objects.all().order_by("id")


# 새로운 과정 등록
def create_course(*, validated_data: dict[str, Any]) -> Course:
    return Course.objects.create(**validated_data)


# 과정 정보 수정
def update_course(*, course_id: int, validated_data: dict[str, Any]) -> Course:
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        raise CourseNotFoundError("과정을 찾을 수 없습니다.")

    for field, value in validated_data.items():
        setattr(course, field, value)

    course.save(update_fields=list(validated_data.keys()) + ["updated_at"])
    return course


# 과정 삭제
def delete_course(*, course_id: int) -> None:
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        raise CourseNotFoundError("과정을 찾을 수 없습니다.")

    # 해당 과정의 기수에 등록된 수강생이 있는지 확인
    has_students = CohortStudent.objects.filter(cohort__course=course).exists()
    if has_students:
        raise CourseHasStudentsError("해당 과정에 등록된 수강생이 있어 삭제할 수 없습니다.")

    # 과정 삭제 (CASCADE로 기수도 함께 삭제됨)
    course.delete()
