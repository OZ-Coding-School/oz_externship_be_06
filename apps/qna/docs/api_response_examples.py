from drf_spectacular.utils import OpenApiExample

from apps.qna.constants import ErrorMessages


class SuccessResponseExamples:
    """
    성공 응답(200, 201)에 대한 예시 데이터 모음
    """

    # --- Questions ---
    QUESTION_CREATE = OpenApiExample(
        name="질문 등록 성공 response body 예시",
        value={"message": "질문이 성공적으로 등록되었습니다.", "question_id": 10501},
        response_only=True,
    )

    QUESTION_LIST = OpenApiExample(
        name="질문 목록조회 성공 response body 예시",
        value={
            "count": 152,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 10501,
                    "category": {"id": 12, "depth": 2, "names": ["백엔드", "Django", "ORM"]},
                    "author": {
                        "id": 211,
                        "nickname": "오즈 백엔드 15기 김동석",
                        "profile_image_url": "https://cdn.ozcodingschool.com/profiles/user_123.png",
                    },
                    "title": "Django ORM 역참조는 어떻게 사용하나요?",
                    "content_preview": "ForeignKey에 related_name을 지정하면...",
                    "answer_count": 3,
                    "view_count": 87,
                    "created_at": "2025-03-01 10:03:21",
                    "thumbnail_img_url": "https://cdn.ozcodingschool.com/qna/thumb_10501_01.png",
                }
            ],
        },
        response_only=True,
    )

    QUESTION_CATEGORY_LIST = OpenApiExample(
        name="카테고리 목록 조회 성공 response body 예시",
        value={
            "categories": [
                {
                    "id": 1,
                    "name": "백엔드",
                    "depth": 0,
                    "subcategories": [
                        {
                            "id": 5,
                            "name": "Django",
                            "depth": 1,
                            "subcategories": [
                                {"id": 12, "name": "ORM", "depth": 2, "subcategories": []},
                                {"id": 13, "name": "DRF", "depth": 2, "subcategories": []},
                            ],
                        },
                        {"id": 6, "name": "Python", "depth": 1, "subcategories": []},
                    ],
                },
                {
                    "id": 2,
                    "name": "프론트엔드",
                    "depth": 0,
                    "subcategories": [{"id": 8, "name": "React", "depth": 1, "subcategories": []}],
                },
            ]
        },
        response_only=True,
    )

    QUESTION_DETAIL = OpenApiExample(
        name="질문 상세 조회 성공 response body 예시",
        value={
            "id": 10501,
            "title": "Django에서 ForeignKey 역참조는 어떻게 하나요?",
            "content": "Django 모델에서 related_name을 지정했을 때",
            "category": {"id": 12, "depth": 2, "names": ["백엔드", "Django", "ORM"]},
            "images": [{"id": 3, "img_url": "https://cdn.ozcodingschool.com/qna/img_20250301_101530.png"}],
            "view_count": 88,
            "created_at": "2025-03-01 10:25:33",
            "author": {"id": 211, "nickname": "나일론동서크", "profile_image_url": None},
            "answers": [
                {
                    "id": "31429",
                    "content": "답변 content",
                    "created_at": "2025-03-02 10:33:33",
                    "is_adopted": False,
                    "author": {"id": "33", "nickname": "소민 조교님", "profile_image_url": None},
                    "comments": [
                        {
                            "id": "14231",
                            "content": "댓글 content",
                            "created_at": "2025-03-05 10:33:33",
                            "author": {"id": "324120", "nickname": "이준 조교님", "profile_image_url": None},
                        }
                    ],
                }
            ],
        },
        response_only=True,
    )

    QUESTION_UPDATE = OpenApiExample(
        name="질문 수정 성공 response body 예시",
        value={"question_id": 10501, "updated_at": "2025-03-02 14:14:22"},
        response_only=True,
    )

    # --- Answers ---
    ANSWER_CREATE = OpenApiExample(
        name="답변 등록 성공 response body 예시",
        value={"answer_id": 801, "question_id": 10501, "author_id": 211, "created_at": "2025-03-02 11:43:20"},
        response_only=True,
    )

    ANSWER_UPDATE = OpenApiExample(
        name="답변 수정 성공 response body 예시",
        value={"answer_id": 801, "updated_at": "2025-03-02 15:22:41"},
        response_only=True,
    )

    ANSWER_ADOPT = OpenApiExample(
        name="답변 채택 성공 response body 예시",
        value={"question_id": 10501, "answer_id": 801, "is_adopted": True},
        response_only=True,
    )

    AI_GEN_ANSWER = OpenApiExample(
        name="AI 답변 생성 성공 response body 예시",
        value={
            "id": 8751,
            "question_id": 10221,
            "output": "리스트는 수정 가능한 자료구조이며, 튜플은 수정이 불가능한 자료구조입니다. 리스트는 [], 튜플은 () 를 사용합니다.",
            "using_model": "gemini-2.5-pro",
            "created_at": "2025-03-01 14:20:33",
        },
        response_only=True,
    )

    ANSWER_COMMENT_CREATE = OpenApiExample(
        name="답변 댓글 등록 성공 response body 예시",
        value={"comment_id": 91001, "answer_id": 801, "author_id": 211, "created_at": "2025-03-02 16:30:18"},
        response_only=True,
    )

    PRESIGNED_URL = OpenApiExample(
        name="Presigned URL 발급 성공 response body 예시",
        value={
            "presigned_url": "https://my-bucket.s3.ap-northeast-2.amazonaws.com/uploads/images/questions/uuid.png?AWSAccessKeyId=...&Signature=...",
            "img_url": "https://my-bucket.s3.ap-northeast-2.amazonaws.com/uploads/images/questions/uuid.png",
            "key": "uploads/images/questions/uuid.png",
        },
        response_only=True,
    )

    # --- Admin ---
    ADMIN_CATEGORY_CREATE = OpenApiExample(
        name="어드민 카테고리 등록 성공 response body 예시",
        value={
            "category_id": 55,
            "name": "FastAPI",
            "category_type": "small",
            "parent_id": 12,
            "created_at": "2025-03-03 14:11:22",
        },
        response_only=True,
    )

    ADMIN_CATEGORY_LIST = OpenApiExample(
        name="어드민 카테고리 목록 조회 성공 response body 예시",
        value={
            "page": 1,
            "size": 20,
            "total_count": 54,
            "categories": [
                {
                    "category_id": 12,
                    "name": "Django",
                    "category_type": "small",
                    "parent_category": "웹 프레임워크",
                    "child_categories": [],
                    "created_at": "2025-03-03 14:11:22",
                    "updated_at": "2025-03-03 15:21:09",
                },
                {
                    "category_id": 5,
                    "name": "웹 프레임워크",
                    "category_type": "medium",
                    "parent_category": "백엔드",
                    "child_categories": ["Django", "FastAPI", "Spring Boot"],
                    "created_at": "2025-02-15 10:17:42",
                    "updated_at": "2025-03-02 21:01:10",
                },
            ],
        },
        response_only=True,
    )

    ADMIN_QUESTION_LIST = OpenApiExample(
        name="어드민 질의응답 목록 조회 성공 response body 예시",
        value={
            "page": 1,
            "size": 20,
            "total_count": 233,
            "questions": [
                {
                    "question_id": 10501,
                    "title": "Django ORM 역참조는 어떻게 사용하나요?",
                    "category_path": "백엔드 > 웹프레임워크 > Django",
                    "content_preview": "ForeignKey에 related_name을 지정하면 역참조가 가능합니다...",
                    "nickname": "한율_회장",
                    "view_count": 132,
                    "has_answer": True,
                    "created_at": "2025-03-01 10:03:21",
                    "updated_at": "2025-03-02 11:20:10",
                }
            ],
        },
        response_only=True,
    )

    ADMIN_QUESTION_DETAIL = OpenApiExample(
        name="어드민 질의응답 상세 조회 성공 response body 예시",
        value={
            "question_id": 10501,
            "title": "Django ORM 역참조는 어떻게 사용하나요?",
            "content": "ForeignKey에 related_name을 지정하면 역참조가 가능합니다...",
            "images": ["https://cdn.ozcodingschool.com/qna/img_10501_01.png"],
            "author": {
                "profile_img_url": "https://cdn.ozcodingschool.com/profiles/user_123.png",
                "nickname": "한율_회장",
                "course_generation": "초격차 백엔드 14기",
            },
            "view_count": 134,
            "has_answer": True,
            "created_at": "2025-03-01 10:03:21",
            "updated_at": "2025-03-02 11:20:10",
            "answers": [
                {
                    "answer_id": 801,
                    "author": {
                        "profile_img_url": "https://cdn.ozcodingschool.com/profiles/user_ta.png",
                        "nickname": "PythonKing",
                        "role_title": "초격차 백엔드 14기 조교",
                        "course_generation": "초격차 백엔드 14기",
                    },
                    "content": "post.comment_set.all() 로 접근하면 됩니다.",
                    "is_adopted": True,
                    "created_at": "2025-03-02 12:10:11",
                    "updated_at": "2025-03-02 12:40:08",
                }
            ],
        },
        response_only=True,
    )

    ADMIN_QUESTION_DELETE = OpenApiExample(
        name="어드민 질의응답 삭제 성공 response body 예시",
        value={"question_id": 10501, "deleted_answer_count": 12, "deleted_comment_count": 45},
        response_only=True,
    )

    ADMIN_ANSWER_DELETE = OpenApiExample(
        name="어드민 답변 삭제 성공 응답 예시",
        value={"answer_id": 801, "deleted_comment_count": 9},
        response_only=True,
    )


class ErrorResponseExamples:
    """
    에러 응답(400, 401, 403, 404, 409)에 대한 예시 데이터 모음
    """

    # --- QUESTION_CREATE ---
    QUESTION_CREATE_400 = OpenApiExample(
        name="질문 등록 실패 response body 예시 - 잘못된 요청",
        value={"error_detail": ErrorMessages.INVALID_QUESTION_CREATE.value},
        response_only=True,
    )
    QUESTION_CREATE_401 = OpenApiExample(
        name="질문 등록 실패 response body 예시 - 인증 실패",
        value={"error_detail": ErrorMessages.UNAUTHORIZED_QUESTION_CREATE.value},
        response_only=True,
    )
    QUESTION_CREATE_403 = OpenApiExample(
        name="질문 등록 실패 response body 예시 - 권한 없음",
        value={"error_detail": ErrorMessages.FORBIDDEN_QUESTION_CREATE.value},
        response_only=True,
    )

    # --- QUESTION_LIST ---
    QUESTION_LIST_400 = OpenApiExample(
        name="질문 목록 조회 실패 response body 예시 - 잘못된 요청",
        value={"error_detail": ErrorMessages.INVALID_QUESTION_LIST.value},
        response_only=True,
    )
    QUESTION_LIST_404 = OpenApiExample(
        name="질문 목록 조회 실패 response body 예시 - 데이터 없음",
        value={"error_detail": ErrorMessages.NOT_FOUND_QUESTION_LIST.value},
        response_only=True,
    )
    #  ---QUESTION_CATEGORY_LIST ---
    QUESTION_CATEGORY_LIST_400 = OpenApiExample(
        name="카테고리 목록 조회 실패 response body 예시 - 잘못된 요청",
        value={"error_detail": ErrorMessages.INVALID_QUESTION_CATEGORY_LIST.value},
        response_only=True,
    )
    # --- QUESTION_DETAIL ---
    QUESTION_DETAIL_400 = OpenApiExample(
        name="질문 상세 조회 실패 response body 예시 - 잘못된 요청",
        value={"error_detail": ErrorMessages.INVALID_QUESTION_DETAIL.value},
        response_only=True,
    )
    QUESTION_DETAIL_404 = OpenApiExample(
        name="질문 상세 조회 실패 response body 예시 - 데이터 없음",
        value={"error_detail": ErrorMessages.NOT_FOUND_QUESTION.value},
        response_only=True,
    )

    # --- QUESTION_UPDATE ---
    QUESTION_UPDATE_400 = OpenApiExample(
        name="질문 수정 실패 response body 예시 - 잘못된 요청",
        value={"error_detail": ErrorMessages.INVALID_QUESTION_UPDATE.value},
        response_only=True,
    )
    QUESTION_UPDATE_401 = OpenApiExample(
        name="질문 수정 실패 response body 예시 - 인증 실패",
        value={"error_detail": ErrorMessages.UNAUTHORIZED_QUESTION_UPDATE.value},
        response_only=True,
    )
    QUESTION_UPDATE_403 = OpenApiExample(
        name="질문 수정 실패 response body 예시 - 권한 없음",
        value={"error_detail": ErrorMessages.FORBIDDEN_QUESTION_UPDATE.value},
        response_only=True,
    )
    QUESTION_UPDATE_404 = OpenApiExample(
        name="질문 수정 실패 response body 예시 - 데이터 없음",
        value={"error_detail": ErrorMessages.NOT_FOUND_QUESTION.value},
        response_only=True,
    )

    # --- ANSWER_CREATE ---
    ANSWER_CREATE_400 = OpenApiExample(
        name="답변 등록 실패 response body 예시 - 잘못된 요청",
        value={"error_detail": ErrorMessages.INVALID_ANSWER_CREATE.value},
        response_only=True,
    )
    ANSWER_CREATE_401 = OpenApiExample(
        name="답변 등록 실패 response body 예시 - 인증 실패",
        value={"error_detail": ErrorMessages.UNAUTHORIZED_ANSWER_CREATE.value},
        response_only=True,
    )
    ANSWER_CREATE_403 = OpenApiExample(
        name="답변 등록 실패 response body 예시 - 권한 없음",
        value={"error_detail": ErrorMessages.FORBIDDEN_ANSWER_CREATE.value},
        response_only=True,
    )
    ANSWER_CREATE_404 = OpenApiExample(
        name="답변 등록 실패 response body 예시 - 질문 찾을 수 없음",
        value={"error_detail": ErrorMessages.NOT_FOUND_QUESTION.value},
        response_only=True,
    )

    # --- ANSWER_UPDATE ---
    ANSWER_UPDATE_400 = OpenApiExample(
        name="답변 수정 실패 response body 예시 - 잘못된 요청",
        value={"error_detail": ErrorMessages.INVALID_ANSWER_UPDATE.value},
        response_only=True,
    )
    ANSWER_UPDATE_401 = OpenApiExample(
        name="답변 수정 실패 response body 예시 - 인증 실패",
        value={"error_detail": ErrorMessages.UNAUTHORIZED_ANSWER_UPDATE.value},
        response_only=True,
    )
    ANSWER_UPDATE_403 = OpenApiExample(
        name="답변 수정 실패 response body 예시 - 권한 없음",
        value={"error_detail": ErrorMessages.FORBIDDEN_ANSWER_UPDATE.value},
        response_only=True,
    )
    ANSWER_UPDATE_404 = OpenApiExample(
        name="답변 수정 실패 response body 예시 - 데이터 없음",
        value={"error_detail": ErrorMessages.NOT_FOUND_ANSWER.value},
        response_only=True,
    )

    # --- ANSWER_ADOPT ---
    ANSWER_ADOPT_400 = OpenApiExample(
        name="답변 채택 실패 response body 예시 - 잘못된 요청",
        value={"error_detail": ErrorMessages.INVALID_ANSWER_ADOPT.value},
        response_only=True,
    )
    ANSWER_ADOPT_401 = OpenApiExample(
        name="답변 채택 실패 response body 예시 - 인증 실패",
        value={"error_detail": ErrorMessages.UNAUTHORIZED_ANSWER_ADOPT.value},
        response_only=True,
    )
    ANSWER_ADOPT_403 = OpenApiExample(
        name="답변 채택 실패 response body 예시 - 권한 없음",
        value={"error_detail": ErrorMessages.FORBIDDEN_ANSWER_ADOPT.value},
        response_only=True,
    )
    ANSWER_ADOPT_404 = OpenApiExample(
        name="답변 채택 실패 response body 예시 - 리소스 찾을 수 없음",
        value={"error_detail": ErrorMessages.NOT_FOUND_QUESTION_OR_ANSWER.value},
        response_only=True,
    )
    ANSWER_ADOPT_409 = OpenApiExample(
        name="답변 채택 실패 response body 예시 - 이미 채택됨",
        value={"error_detail": ErrorMessages.CONFLICT_ANSWER_ADOPT.value},
        response_only=True,
    )

    # --- AI_ANSWER_GENERATE ---
    AI_GEN_ANSWER_400 = OpenApiExample(
        name="AI 답변 생성 실패 response body 예시 - 잘못된 요청",
        value={"error_detail": ErrorMessages.INVALID_AI_REQUEST.value},
        response_only=True,
    )
    AI_GEN_ANSWER_401 = OpenApiExample(
        name="AI 답변 생성 실패 response body 예시 - 인증 실패",
        value={"error_detail": ErrorMessages.UNAUTHORIZED_AI_REQUEST.value},
        response_only=True,
    )
    AI_GEN_ANSWER_403 = OpenApiExample(
        name="AI 답변 생성 실패 response body 예시 - 권한 없음",
        value={"error_detail": ErrorMessages.FORBIDDEN_AI_REQUEST.value},
        response_only=True,
    )
    AI_GEN_ANSWER_404 = OpenApiExample(
        name="AI 답변 생성 실패 response body 예시 - 데이터 없음",
        value={"error_detail": ErrorMessages.NOT_FOUND_AI_QUESTION.value},
        response_only=True,
    )
    AI_GEN_ANSWER_409 = OpenApiExample(
        name="AI 답변 생성 실패 response body 예시 - 이미 생성됨",
        value={"error_detail": ErrorMessages.CONFLICT_AI_GEN_ANSWER.value},
        response_only=True,
    )

    # --- ANSWER_COMMENT_CREATE ---
    ANSWER_COMMENT_CREATE_400 = OpenApiExample(
        name="답변 댓글 등록 실패 response body 예시 - 글자 수 초과",
        value={"error_detail": ErrorMessages.INVALID_COMMENT_LENGTH.value},
        response_only=True,
    )
    ANSWER_COMMENT_CREATE_401 = OpenApiExample(
        name="답변 댓글 등록 실패 response body 예시 - 인증 실패",
        value={"error_detail": ErrorMessages.UNAUTHORIZED_COMMENT_CREATE.value},
        response_only=True,
    )
    ANSWER_COMMENT_CREATE_403 = OpenApiExample(
        name="답변 댓글 등록 실패 response body 예시 - 권한 없음",
        value={"error_detail": ErrorMessages.FORBIDDEN_COMMENT_CREATE.value},
        response_only=True,
    )
    ANSWER_COMMENT_CREATE_404 = OpenApiExample(
        name="답변 댓글 등록 실패 response body 예시 - 답변 찾을 수 없음",
        value={"error_detail": ErrorMessages.NOT_FOUND_ANSWER.value},
        response_only=True,
    )

    # --- PRESIGNED_URL ---
    PRESIGNED_URL_400 = OpenApiExample(
        name="Presigned URL 발급 실패 response body 예시 - 잘못된 요청",
        value={"error_detail": ErrorMessages.UNSUPPORTED_FILE_FORMAT.value},
        response_only=True,
    )

    # --- ADMIN_CATEGORY_CREATE ---
    ADMIN_CATEGORY_CREATE_400 = OpenApiExample(
        name="어드민 카테고리 등록 실패 response body 예시 - 잘못된 요청",
        value={"error_detail": ErrorMessages.INVALID_ADMIN_CATEGORY_CREATE.value},
        response_only=True,
    )
    ADMIN_CATEGORY_CREATE_401 = OpenApiExample(
        name="어드민 카테고리 등록 실패 response body 예시 - 인증 실패",
        value={"error_detail": ErrorMessages.UNAUTHORIZED_ADMIN_CATEGORY_CREATE.value},
        response_only=True,
    )
    ADMIN_CATEGORY_CREATE_403 = OpenApiExample(
        name="어드민 카테고리 등록 실패 response body 예시 - 권한 없음",
        value={"error_detail": ErrorMessages.FORBIDDEN_ADMIN_CATEGORY_CREATE.value},
        response_only=True,
    )
    ADMIN_CATEGORY_CREATE_404 = OpenApiExample(
        name="어드민 카테고리 등록 실패 response body 예시 - 부모 미존재",
        value={"error_detail": ErrorMessages.NOT_FOUND_ADMIN_CATEGORY_PARENT.value},
        response_only=True,
    )
    ADMIN_CATEGORY_CREATE_409 = OpenApiExample(
        name="어드민 카테고리 등록 실패 response body 예시 - 이름 중복",
        value={"error_detail": ErrorMessages.CONFLICT_ADMIN_CATEGORY_NAME.value},
        response_only=True,
    )

    # --- ADMIN_CATEGORY_LIST ---
    ADMIN_CATEGORY_LIST_400 = OpenApiExample(
        name="어드민 카테고리 목록 조회 실패 response body 예시 - 잘못된 요청",
        value={"error_detail": ErrorMessages.INVALID_ADMIN_CATEGORY_LIST.value},
        response_only=True,
    )
    ADMIN_CATEGORY_LIST_401 = OpenApiExample(
        name="어드민 카테고리 목록 조회 실패 response body 예시 - 인증 실패",
        value={"error_detail": ErrorMessages.UNAUTHORIZED_ADMIN_CATEGORY_LIST.value},
        response_only=True,
    )
    ADMIN_CATEGORY_LIST_403 = OpenApiExample(
        name="어드민 카테고리 목록 조회 실패 response body 예시 - 권한 없음",
        value={"error_detail": ErrorMessages.FORBIDDEN_ADMIN_CATEGORY_LIST.value},
        response_only=True,
    )

    # --- ADMIN_QUESTION_LIST ---
    ADMIN_QUESTION_LIST_400 = OpenApiExample(
        name="어드민 질의응답 목록 조회 실패 response body 예시 - 잘못된 요청",
        value={"error_detail": ErrorMessages.INVALID_ADMIN_QUESTION_LIST.value},
        response_only=True,
    )
    ADMIN_QUESTION_LIST_401 = OpenApiExample(
        name="어드민 질의응답 목록 조회 실패 response body 예시 - 인증 실패",
        value={"error_detail": ErrorMessages.UNAUTHORIZED_ADMIN_QUESTION_LIST.value},
        response_only=True,
    )
    ADMIN_QUESTION_LIST_403 = OpenApiExample(
        name="어드민 질의응답 목록 조회 실패 response body 예시 - 권한 없음",
        value={"error_detail": ErrorMessages.FORBIDDEN_ADMIN_QUESTION_LIST.value},
        response_only=True,
    )

    # --- ADMIN_QUESTION_DETAIL ---
    ADMIN_QUESTION_DETAIL_400 = OpenApiExample(
        name="어드민 질의응답 상세 조회 실패 response body 예시 - 잘못된 요청",
        value={"error_detail": ErrorMessages.INVALID_ADMIN_QUESTION_DETAIL.value},
        response_only=True,
    )
    ADMIN_QUESTION_DETAIL_401 = OpenApiExample(
        name="어드민 질의응답 상세 조회 실패 response body 예시 - 인증 실패",
        value={"error_detail": ErrorMessages.UNAUTHORIZED_ADMIN_QUESTION_DETAIL.value},
        response_only=True,
    )
    ADMIN_QUESTION_DETAIL_403 = OpenApiExample(
        name="어드민 질의응답 상세 조회 실패 response body 예시 - 권한 없음",
        value={"error_detail": ErrorMessages.FORBIDDEN_ADMIN_QUESTION_DETAIL.value},
        response_only=True,
    )
    ADMIN_QUESTION_DETAIL_404 = OpenApiExample(
        name="어드민 질의응답 상세 조회 실패 response body 예시 - 데이터 없음",
        value={"error_detail": ErrorMessages.NOT_FOUND_QUESTION.value},
        response_only=True,
    )

    # --- ADMIN_QUESTION_DELETE ---
    ADMIN_QUESTION_DELETE_400 = OpenApiExample(
        name="어드민 질의응답 삭제 실패 response body 예시 - 잘못된 요청",
        value={"error_detail": ErrorMessages.INVALID_ADMIN_QUESTION_DELETE.value},
        response_only=True,
    )
    ADMIN_QUESTION_DELETE_401 = OpenApiExample(
        name="어드민 질의응답 삭제 실패 response body 예시 - 인증 실패",
        value={"error_detail": ErrorMessages.UNAUTHORIZED_ADMIN_QUESTION_DELETE.value},
        response_only=True,
    )
    ADMIN_QUESTION_DELETE_403 = OpenApiExample(
        name="어드민 질의응답 삭제 실패 response body 예시 - 권한 없음",
        value={"error_detail": ErrorMessages.FORBIDDEN_ADMIN_QUESTION_DELETE.value},
        response_only=True,
    )
    ADMIN_QUESTION_DELETE_404 = OpenApiExample(
        name="어드민 질의응답 삭제 실패 response body 예시 - 데이터 없음",
        value={"error_detail": ErrorMessages.NOT_FOUND_ADMIN_QUESTION.value},
        response_only=True,
    )

    # --- ADMIN_ANSWER_DELETE ---
    ADMIN_ANSWER_DELETE_400 = OpenApiExample(
        name="어드민 답변 삭제 실패 응답 예시 - 잘못된 요청",
        value={"error_detail": ErrorMessages.INVALID_ADMIN_ANSWER_DELETE.value},
        response_only=True,
    )
    ADMIN_ANSWER_DELETE_401 = OpenApiExample(
        name="어드민 답변 삭제 실패 응답 예시 - 인증 실패",
        value={"error_detail": ErrorMessages.UNAUTHORIZED_ADMIN_ANSWER_DELETE.value},
        response_only=True,
    )
    ADMIN_ANSWER_DELETE_403 = OpenApiExample(
        name="어드민 답변 삭제 실패 응답 예시 - 권한 없음",
        value={"error_detail": ErrorMessages.FORBIDDEN_ADMIN_ANSWER_DELETE.value},
        response_only=True,
    )
    ADMIN_ANSWER_DELETE_404 = OpenApiExample(
        name="어드민 답변 삭제 실패 응답 예시 - 데이터 없음",
        value={"error_detail": ErrorMessages.NOT_FOUND_ADMIN_ANSWER.value},
        response_only=True,
    )
