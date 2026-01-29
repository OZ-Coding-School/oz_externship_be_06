from enum import Enum


class ErrorMessages(str, Enum):

    # --- 400 Bad Request (Invalid Inputs) ---
    INVALID_REQUEST = "유효하지 않은 요청입니다."
    INVALID_QUESTION_CREATE = "유효하지 않은 질문 등록 요청입니다."
    INVALID_QUESTION_LIST = "유효하지 않은 목록 조회 요청입니다."  # 목록 > 질문 목록
    INVALID_QUESTION_DETAIL = "유효하지 않은 질문 상세 조회 요청입니다."
    INVALID_QUESTION_UPDATE = "유효하지 않은 질문 수정 요청입니다."
    INVALID_ANSWER_CREATE = "유효하지 않은 답변 등록 요청입니다."
    INVALID_ANSWER_UPDATE = "유효하지 않은 답변 수정 요청입니다."
    INVALID_ANSWER_ADOPT = "유효하지 않은 답변 채택 요청입니다."
    INVALID_AI_REQUEST = "유효하지 않은 데이터 요청입니다."
    INVALID_COMMENT_LENGTH = "댓글 내용은 1~500자 사이로 입력해야 합니다."
    UNSUPPORTED_FILE_FORMAT = "지원하지 않는 파일 형식입니다."

    # --- 401 Unauthorized (Authentication Required) ---
    UNAUTHORIZED_QUESTION_CREATE = "로그인한 수강생만 질문을 등록할 수 있습니다."
    UNAUTHORIZED_QUESTION_UPDATE = "로그인한 사용자만 질문을 수정할 수 있습니다."
    UNAUTHORIZED_ANSWER_CREATE = "로그인한 사용자만 답변을 작성할 수 있습니다."
    UNAUTHORIZED_ANSWER_UPDATE = "로그인한 사용자만 답변을 수정할 수 있습니다."
    UNAUTHORIZED_ANSWER_ADOPT = "로그인한 사용자만 답변을 채택할 수 있습니다."
    UNAUTHORIZED_COMMENT_CREATE = "로그인한 사용자만 댓글을 작성할 수 있습니다."
    UNAUTHORIZED_AI_REQUEST = "로그인한 사용자만 요청할 수 있습니다."

    # --- 403 Forbidden (Permission Denied) ---
    FORBIDDEN_QUESTION_CREATE = "질문 등록 권한이 없습니다."
    FORBIDDEN_QUESTION_UPDATE = "본인이 작성한 질문만 수정할 수 있습니다."
    FORBIDDEN_ANSWER_CREATE = "답변 작성 권한이 없습니다."
    FORBIDDEN_ANSWER_UPDATE = "본인이 작성한 답변만 수정할 수 있습니다."
    FORBIDDEN_ANSWER_ADOPT = "본인이 작성한 질문의 답변만 채택할 수 있습니다."
    FORBIDDEN_COMMENT_CREATE = "댓글 작성 권한이 없습니다."
    FORBIDDEN_AI_REQUEST = "AI 답변 생성 권한이 없습니다."

    # --- 404 Not Found (Resource Missing) ---
    NOT_FOUND_QUESTION = "해당 질문을 찾을 수 없습니다."
    NOT_FOUND_QUESTION_LIST = "조회 가능한 질문이 존재하지 않습니다."
    NOT_FOUND_ANSWER = "해당 답변을 찾을 수 없습니다."
    NOT_FOUND_QUESTION_OR_ANSWER = "해당 질문 또는 답변을 찾을 수 없습니다."
    NOT_FOUND_AI_QUESTION = "질문 데이터를 찾을 수 없습니다."

    # --- 409 Conflict (Business Logic Collision) ---
    ALREADY_EXISTS_AI_ANSWER = "이미 AI가 답변을 생성했습니다."
    ALREADY_EXISTS_ADOPTED_ANSWER = "이미 채택된 답변이 존재합니다."
