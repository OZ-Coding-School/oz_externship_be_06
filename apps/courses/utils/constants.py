from enum import Enum


class ErrorMessages(str, Enum):
    UNAUTHORIZED = "자격 인증 데이터가 제공되지 않았습니다."
    FORBIDDEN = "이 리소스를 조회할 권한이 없습니다."
    ADMIN_FORBIDDEN = "권한이 없습니다."
    COURSE_NOT_FOUND = "과정을 찾을 수 없습니다."
    COHORT_NOT_FOUND = "기수를 찾을 수 없습니다."
    SUBJECT_NOT_FOUND = "과목을 찾을 수 없습니다."
