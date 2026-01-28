from enum import Enum


class ExamStatus(str, Enum):
    CLOSED = "closed"
    ACTIVATED = "activated"


class ErrorMessages(str, Enum):
    # 400
    INVALID_CHECK_CODE_REQUEST = "응시 코드가 일치하지 않습니다."
    INVALID_EXAM_SESSION = "유효하지 않은 시험 응시 세션입니다."
    INVALID_EXAM_CREATE_REQUEST = "유효하지 않은 시험 생성 요청입니다."
    INVALID_EXAM_LIST_REQUEST = "유효하지 않은 조회 요청입니다."
    INVALID_EXAM_UPDATE_REQUEST = "유효하지 않은 요청 데이터입니다."
    INVALID_EXAM_DELETE_REQUEST = "유효하지 않은 요청입니다."
    INVALID_QUESTION_CREATE_REQUEST = "유효하지 않은 문제 등록 데이터입니다."
    INVALID_QUESTION_UPDATE_REQUEST = "유효하지 않은 문제 수정 데이터입니다."
    INVALID_QUESTION_DELETE_REQUEST = "유효하지 않은 문제 삭제 요청입니다."
    INVALID_DEPLOYMENT_CREATE_REQUEST = "유효하지 않은 배포 생성 요청입니다."
    INVALID_DEPLOYMENT_DETAIL_REQUEST = "유효하지 않은 배포 상세 조회 요청입니다."
    INVALID_DEPLOYMENT_UPDATE_REQUEST = "유효하지 않은 배포 수정 요청입니다."
    INVALID_DEPLOYMENT_STATUS_REQUEST = "유효하지 않은 배포 상태 요청입니다."
    INVALID_DEPLOYMENT_DELETE_REQUEST = "유효하지 않은 배포 삭제 요청입니다."
    INVALID_SUBMISSION_LIST_REQUEST = "유효하지 않은 조회 요청입니다."
    INVALID_SUBMISSION_DETAIL_REQUEST = "유효하지 않은 상세 조회 요청입니다."
    INVALID_SUBMISSION_DELETE_REQUEST = "유효하지 않은 응시 내역 삭제 요청입니다."

    # 401
    UNAUTHORIZED = "자격 인증 데이터가 제공되지 않았습니다."

    # 403
    FORBIDDEN = "권한이 없습니다."
    NO_EXAM_STAFF_PERMISSION = "쪽지시험 관리 권한이 없습니다."
    NO_EXAM_LIST_PERMISSION = "쪽지시험 목록 조회 권한이 없습니다."
    NO_EXAM_CREATE_PERMISSION = "쪽지시험 생성 권한이 없습니다."
    NO_EXAM_UPDATE_PERMISSION = "쪽지시험 수정 권한이 없습니다."
    NO_EXAM_DELETE_PERMISSION = "쪽지시험 삭제 권한이 없습니다."
    NO_QUESTION_CREATE_PERMISSION = "쪽지시험 문제 등록 권한이 없습니다."
    NO_QUESTION_UPDATE_PERMISSION = "쪽지시험 문제 수정 권한이 없습니다."
    NO_QUESTION_DELETE_PERMISSION = "쪽지시험 문제 삭제 권한이 없습니다."
    NO_DEPLOYMENT_CREATE_PERMISSION = "쪽지시험 배포 생성 권한이 없습니다."
    NO_DEPLOYMENT_DETAIL_PERMISSION = "쪽지시험 배포 상세 조회 권한이 없습니다."
    NO_DEPLOYMENT_LIST_PERMISSION = "쪽지시험 배포 목록 조회 권한이 없습니다."
    NO_DEPLOYMENT_UPDATE_PERMISSION = "쪽지시험 배포 수정 권한이 없습니다."
    NO_DEPLOYMENT_STATUS_PERMISSION = "쪽지시험 배포 상태 변경 권한이 없습니다."
    NO_DEPLOYMENT_DELETE_PERMISSION = "배포 삭제 권한이 없습니다."
    NO_SUBMISSION_LIST_PERMISSION = "쪽지시험 응시 내역 조회 권한이 없습니다."
    NO_SUBMISSION_DETAIL_PERMISSION = "쪽지시험 응시 상세 조회 권한이 없습니다."
    NO_SUBMISSION_DELETE_PERMISSION = "쪽지시험 응시 내역 삭제 권한이 없습니다."
    NO_EXAM_TAKE_PERMISSION = "시험에 응시할 권한이 없습니다."

    # 404
    EXAM_NOT_FOUND = "해당 시험 정보를 찾을 수 없습니다."
    EXAM_ADMIN_NOT_FOUND = "해당 쪽지시험 정보를 찾을 수 없습니다."
    EXAM_UPDATE_NOT_FOUND = "수정할 쪽지시험 정보를 찾을 수 없습니다."
    EXAM_DELETE_NOT_FOUND = "삭제하려는 쪽지시험 정보를 찾을 수 없습니다."
    SUBJECT_NOT_FOUND = "해당 과목 정보를 찾을 수 없습니다."
    QUESTION_NOT_FOUND = "삭제할 문제 정보를 찾을 수 없습니다."
    QUESTION_UPDATE_NOT_FOUND = "수정하려는 문제 정보를 찾을 수 없습니다."
    DEPLOYMENT_NOT_FOUND = "해당 배포 정보를 찾을 수 없습니다."
    DEPLOYMENT_TARGET_NOT_FOUND = "배포 대상 과정-기수 또는 시험 정보를 찾을 수 없습니다."
    DEPLOYMENT_UPDATE_NOT_FOUND = "수정할 배포 정보를 찾을 수 없습니다."
    DEPLOYMENT_DELETE_NOT_FOUND = "삭제할 배포 정보를 찾을 수 없습니다."
    SUBMISSION_LIST_NOT_FOUND = "조회된 응시 내역이 없습니다."
    SUBMISSION_DETAIL_NOT_FOUND = "해당 응시 내역을 찾을 수 없습니다."
    USER_NOT_FOUND = "사용자 정보를 찾을 수 없습니다."

    # 409
    EXAM_CONFLICT = "동일한 이름의 시험이 이미 존재합니다."
    EXAM_UPDATE_CONFLICT = "동일한 이름의 쪽지시험이 이미 존재합니다."
    EXAM_DELETE_CONFLICT = "쪽지시험 삭제 중 충돌이 발생했습니다."
    QUESTION_CREATE_CONFLICT = "해당 쪽지시험에 등록 가능한 문제 수 또는 총 배점을 초과했습니다."
    QUESTION_UPDATE_CONFLICT = "시험 문제 수 제한 또는 총 배점을 초과하여 문제를 수정할 수 없습니다."
    QUESTION_DELETE_CONFLICT = "쪽지시험 문제 삭제 처리 중 충돌이 발생했습니다."
    DUPLICATE_DEPLOYMENT = "동일한 조건의 배포가 이미 존재합니다."
    DEPLOYMENT_CONFLICT = "배포 상태 변경 중 충돌이 발생했습니다."
    DEPLOYMENT_DELETE_CONFLICT = "배포 삭제 처리 중 충돌이 발생했습니다."
    SUBMISSION_ALREADY_SUBMITTED = "이미 제출된 시험입니다."
    SUBMISSION_DELETE_CONFLICT = "응시 내역 삭제 처리 중 충돌이 발생했습니다."

    # 410
    EXAM_CLOSED = "시험이 종료되었습니다."
    EXAM_ALREADY_CLOSED = "시험이 이미 종료되었습니다."

    # 423
    EXAM_NOT_AVAILABLE = "아직 응시할 수 없습니다."
