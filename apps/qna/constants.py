from enum import Enum


class ErrorMessages(str, Enum):
    """
    QnA 서비스 전역에서 사용되는 에러 메시지 상수
    """

    # --- 400 Bad Request (Invalid Inputs) ---
    DEFAULT_400 = "400 유효하지 않은 요청"
    INVALID_QUESTION_CREATE = "유효하지 않은 질문 등록 요청입니다."
    INVALID_QUESTION_LIST = "유효하지 않은 질문 목록 조회 요청입니다."
    INVALID_QUESTION_CATEGORY_LIST = "유효하지 않은 카테고리 목록 조회 요청입니다."
    INVALID_QUESTION_DETAIL = "유효하지 않은 질문 상세 조회 요청입니다."
    INVALID_QUESTION_UPDATE = "유효하지 않은 질문 수정 요청입니다."
    INVALID_ANSWER_CREATE = "유효하지 않은 답변 등록 요청입니다."
    INVALID_ANSWER_UPDATE = "유효하지 않은 답변 수정 요청입니다."
    INVALID_ANSWER_ADOPT = "유효하지 않은 답변 채택 요청입니다."
    INVALID_AI_REQUEST = "유효하지 않은 데이터 요청입니다."
    INVALID_COMMENT_LENGTH_LIMIT = "댓글 내용은 500자 이내로 입력해야 합니다."
    INVALID_COMMENT_BLANK = "댓글 내용을 입력해주세요."
    # 400 - Admin
    INVALID_ADMIN_CATEGORY_CREATE = "카테고리 종류와 이름은 필수 입력값입니다."
    INVALID_ADMIN_CATEGORY_LIST = "유효하지 않은 목록 조회 요청입니다."
    INVALID_ADMIN_CATEGORY_DELETE = "유효하지 않은 카테고리 삭제 요청입니다."
    INVALID_ADMIN_QUESTION_LIST = "유효하지 않은 목록 조회 요청입니다."
    INVALID_ADMIN_QUESTION_DETAIL = "유효하지 않은 상세 조회 요청입니다."
    INVALID_ADMIN_QUESTION_DELETE = "유효하지 않은 삭제 요청입니다."
    INVALID_ADMIN_ANSWER_DELETE = "유효하지 않은 답변 삭제 요청입니다."
    # 400 - Presigned URL & S3
    UNSUPPORTED_FILE_FORMAT = "지원하지 않는 파일 형식입니다."
    INVALID_UPLOAD_DOMAIN = "유효하지 않은 업로드 도메인입니다."

    # --- 401 Unauthorized (Authentication Required) ---
    DEFAULT_401 = "401 로그인이 필요함"
    UNAUTHORIZED_QUESTION_CREATE = "로그인한 수강생만 질문을 등록할 수 있습니다."
    UNAUTHORIZED_QUESTION_UPDATE = "로그인한 사용자만 질문을 수정할 수 있습니다."
    UNAUTHORIZED_ANSWER_CREATE = "로그인한 사용자만 답변을 작성할 수 있습니다."
    UNAUTHORIZED_ANSWER_UPDATE = "로그인한 사용자만 답변을 수정할 수 있습니다."
    UNAUTHORIZED_ANSWER_ADOPT = "로그인한 사용자만 답변을 채택할 수 있습니다."
    UNAUTHORIZED_COMMENT_CREATE = "로그인한 사용자만 댓글을 작성할 수 있습니다."
    UNAUTHORIZED_AI_REQUEST = "로그인한 사용자만 요청할 수 있습니다."
    # 401 - Admin
    UNAUTHORIZED_ADMIN_CATEGORY_CREATE = "로그인이 필요합니다."
    UNAUTHORIZED_ADMIN_CATEGORY_LIST = "로그인이 필요합니다."
    UNAUTHORIZED_ADMIN_CATEGORY_DELETE = "로그인이 필요합니다."
    UNAUTHORIZED_ADMIN_QUESTION_LIST = "로그인이 필요합니다."
    UNAUTHORIZED_ADMIN_QUESTION_DETAIL = "로그인이 필요합니다."
    UNAUTHORIZED_ADMIN_QUESTION_DELETE = "로그인이 필요합니다."
    UNAUTHORIZED_ADMIN_ANSWER_DELETE = "로그인이 필요합니다."

    # --- 403 Forbidden (Permission Denied) ---
    DEFAULT_403 = "403 권한이 없음"
    FORBIDDEN_QUESTION_CREATE = "질문 등록 권한이 없습니다."
    FORBIDDEN_QUESTION_UPDATE = "본인이 작성한 질문만 수정할 수 있습니다."
    FORBIDDEN_ANSWER_CREATE = "답변 작성 권한이 없습니다."
    FORBIDDEN_ANSWER_UPDATE = "본인이 작성한 답변만 수정할 수 있습니다."
    FORBIDDEN_ANSWER_ADOPT = "본인이 작성한 질문의 답변만 채택할 수 있습니다."
    FORBIDDEN_COMMENT_CREATE = "댓글 작성 권한이 없습니다."
    FORBIDDEN_AI_REQUEST = "AI 답변 생성 권한이 없습니다."
    # 403 - Admin
    FORBIDDEN_ADMIN_CATEGORY_CREATE = "카테고리 등록 권한이 없습니다."
    FORBIDDEN_ADMIN_CATEGORY_LIST = "카테고리 목록 조회 권한이 없습니다."
    FORBIDDEN_ADMIN_CATEGORY_DELETE = "카테고리 삭제 권한이 없습니다."
    FORBIDDEN_ADMIN_QUESTION_LIST = "질의응답 목록 조회 권한이 없습니다."
    FORBIDDEN_ADMIN_QUESTION_DETAIL = "질의응답 상세 조회 권한이 없습니다."
    FORBIDDEN_ADMIN_QUESTION_DELETE = "질의응답 삭제 권한이 없습니다."
    FORBIDDEN_ADMIN_ANSWER_DELETE = "답변 삭제 권한이 없습니다."

    # --- 404 Not Found (Resource Missing) ---
    DEFAULT_404 = "404 찾을 수 없음"
    NOT_FOUND_CATEGORY = "해당 카테고리를 찾을 수 없습니다."
    NOT_FOUND_QUESTION = "해당 질문을 찾을 수 없습니다."
    NOT_FOUND_QUESTION_LIST = "조회 가능한 질문이 존재하지 않습니다."
    NOT_FOUND_ANSWER = "해당 답변을 찾을 수 없습니다."
    NOT_FOUND_QUESTION_OR_ANSWER = "해당 질문 또는 답변을 찾을 수 없습니다."
    NOT_FOUND_AI_QUESTION = "질문 데이터를 찾을 수 없습니다."
    # 404 - Admin
    NOT_FOUND_ADMIN_CATEGORY = "해당 카테고리를 찾을 수 없습니다."
    NOT_FOUND_ADMIN_CATEGORY_PARENT = "부모 카테고리를 찾을 수 없습니다."
    NOT_FOUND_ADMIN_QUESTION_DETAIL = "해당 질문을 찾을 수 없습니다."
    NOT_FOUND_ADMIN_QUESTION = "삭제할 질문을 찾을 수 없습니다."
    NOT_FOUND_ADMIN_ANSWER = "삭제할 답변을 찾을 수 없습니다."

    # --- 409 Conflict (Business Logic Collision) ---
    DEFAULT_409 = "409 충돌"
    CONFLICT_AI_GEN_ANSWER = "이미 AI가 답변을 생성했습니다."
    CONFLICT_ANSWER_ADOPT = "이미 채택된 답변이 존재합니다."
    # 409 - Admin
    CONFLICT_ADMIN_CATEGORY_NAME = "동일한 이름의 카테고리가 이미 존재합니다."
    CONFLICT_ADMIN_DEFAULT_CATEGORY_DELETE = "기본 카테고리는 삭제할 수 없습니다."

    # --- 500 Internal Server Error & Unexpected (System) ---
    DEFAULT_500 = "500 Internal Server Error"
    PRESIGNED_URL_GENERATION_ERROR = "파일 업로드 URL 생성 중 오류가 발생했습니다."
    S3_CONNECTION_ERROR = "이미지 서버 연결에 실패했습니다."
    SYSTEM_ERROR = "데이터 처리 중 오류가 발생했습니다."
    DATABASE_ERROR = "데이터베이스 연결 중 오류가 발생했습니다."
    FAILED_AI_GEN_ANSWER = "AI 답변 생성 중 일시적인 오류가 발생했습니다."
