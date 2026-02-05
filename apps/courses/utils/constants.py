from enum import Enum


class ErrorMessages(str, Enum):
    UNAUTHORIZED = "자격 인증 데이터가 제공되지 않았습니다."
    FORBIDDEN = "이 리소스를 조회할 권한이 없습니다."
    ADMIN_FORBIDDEN = "권한이 없습니다."
    COURSE_NOT_FOUND = "과정을 찾을 수 없습니다."
    COHORT_NOT_FOUND = "기수를 찾을 수 없습니다."
    SUBJECT_NOT_FOUND = "과목을 찾을 수 없습니다."
    # 과목 생성 관련
    INVALID_SUBJECT_CREATE = "유효하지 않은 과목 생성 요청입니다."
    SUBJECT_CREATE_FORBIDDEN = "과목 생성 권한이 없습니다."
    SUBJECT_ALREADY_EXISTS = "동일한 이름의 과목이 이미 존재합니다."
