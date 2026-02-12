from __future__ import annotations

from apps.qna.utils.model_types import User


def get_course_generation(user: User) -> str:
    """
    유저의 role에 따라 과정-기수 문자열을 반환

    - STUDENT: cohort_students → 최신 cohort → "{course.name} {cohort.number}기"
    - TA: assisted_cohorts → 최신 cohort → "{course.name} {cohort.number}기"
    - LC, OM, ADMIN: ""
    """
    role = str(getattr(user, "role", ""))

    if role == "STUDENT":
        cohort_student = (
            getattr(user, "cohort_students").select_related("cohort__course").order_by("-created_at").first()
        )
        if cohort_student:
            cohort = cohort_student.cohort
            return f"{cohort.course.name} {cohort.number}기"
        return ""

    if role == "TA":
        ta = getattr(user, "assisted_cohorts").select_related("cohort__course").order_by("-created_at").first()
        if ta:
            cohort = ta.cohort
            return f"{cohort.course.name} {cohort.number}기"
        return ""

    return ""


def get_role_title(user: User) -> str:
    """
    유저의 role에 따라 직함 문자열을 반환

    - STUDENT: ""
    - TA: "{course_generation} 조교"
    - LC: "러닝 코치"
    - OM: "교육 운영 매니저"
    - ADMIN: "관리자"
    """
    role = str(getattr(user, "role", ""))

    if role == "STUDENT":
        return ""

    if role == "TA":
        course_generation = get_course_generation(user)
        return f"{course_generation} 조교" if course_generation else "조교"

    if role == "LC":
        return "러닝 코치"

    if role == "OM":
        return "교육 운영 매니저"

    if role == "ADMIN":
        return "관리자"

    return ""
