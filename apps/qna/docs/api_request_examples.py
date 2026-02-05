from drf_spectacular.utils import OpenApiExample


class QueryParameterExamples:
    """
    Query Parameter에 대한 예시
    """

    # --- Questions ---
    QUESTION_LIST = OpenApiExample(
        name="질문 목록 조회 query parameter 예시",
        value={
            "page": 1,
            "size": 10,
            "search_keyword": "django",
            "category_id": 12,
            "answer_status": "answered",
            "sort": "latest",
        },
        request_only=True,
    )

    # --- Admin ---
    ADMIN_CATEGORY_LIST = OpenApiExample(
        name="어드민 카테고리 목록 조회 query parameter 예시",
        value={"page": 1, "size": 20, "search_keyword": "Django", "category_type": "small"},
        request_only=True,
    )

    ADMIN_QUESTION_LIST = OpenApiExample(
        name="어드민 질의응답 목록 조회 query parameter 예시",
        value={
            "page": 1,
            "size": 20,
            "search_keyword": "ORM",
            "category_id": 12,
            "answer_status": "Y",
            "sort": "latest",
        },
        request_only=True,
    )


class RequestBodyExamples:
    """
    Request Body에 대한 예시
    """

    # --- Questions ---
    QUESTION_CREATE = OpenApiExample(
        name="질문 등록 request body 예시",
        value={
            "title": "새 질문 제목",
            "content": "새 질문 내용",
            "category_id": 1,
        },
        request_only=True,
    )

    QUESTION_UPDATE = OpenApiExample(
        name="질문 수정 request body 예시",
        value={
            "title": "질문 제목 수정",
            "content": "질문 수정하기\n\n예시 내용 수정:\n```python\npost.comment_set.all()\n```",
            "category_id": 1,
        },
        request_only=True,
    )

    # --- Answers ---
    ANSWER_CREATE = OpenApiExample(
        name="답변 등록 request body 예시",
        value={
            "content": "Django ORM 역참조는 `related_name`을 사용하여 접근할 수 있습니다.\n\n```python\npost.comment_set.all()\n```",
            "image_urls": ["https://cdn.ozcodingschool.com/qna/answer_img_1001.png"],
        },
        request_only=True,
    )

    ANSWER_UPDATE = OpenApiExample(
        name="답변 수정 request body 예시",
        value={
            "content": "Django ORM에서 `related_name`을 설정하면 역참조가 가능합니다.\n\n예시:\n```python\npost.comment_set.all()\n```",
            "image_urls": ["https://cdn.ozcodingschool.com/qna/answer_img_1001.png"],
        },
        request_only=True,
    )

    ANSWER_COMMENT_CREATE = OpenApiExample(
        name="답변 댓글 등록 request body 예시",
        value={"content": "관련 예제 코드도 공유해주실 수 있나요?"},
        request_only=True,
    )

    PRESIGNED_URL = OpenApiExample(
        name="Presigned URL 발급 request body 예시",
        value={"file_name": "error_screenshot.png"},
        request_only=True,
    )

    # --- admin ---
    ADMIN_CATEGORY_CREATE = OpenApiExample(
        name="어드민 카테고리 등록 request body 예시",
        value={"category_type": "large", "name": "백엔드", "parent_id": None},
        request_only=True,
    )
