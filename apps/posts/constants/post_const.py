class PostErrorMessage:
    """
    커뮤니티 도메인 에러 메시지 상수
    """

    # 400 Bad Request
    FIELD_REQUIRED = "이 필드는 필수 항목입니다."
    ALREADY_LIKED = "이미 좋아요를 누른 게시물입니다."

    # 401 Unauthorized
    UNAUTHORIZED = "자격 인증 데이터가 제공되지 않았습니다."

    # 403 Forbidden
    FORBIDDEN = "권한이 없습니다."

    # 404 Not Found
    POST_NOT_FOUND_WITH_TARGET = "해당 게시글을 찾을 수 없습니다."
    POST_NOT_FOUND = "게시글을 찾을 수 없습니다."
    COMMENT_NOT_FOUND = "해당 댓글을 찾을 수 없습니다."
    LIKE_NOT_FOUND = "좋아요 기록을 찾을 수 없습니다."

    # 500 Internal Server Error (추가)
    SERVER_ERROR = "서버에서 알 수 없는 오류가 발생했습니다."


class PostSuccessMessage:
    """
    커뮤니티 도메인 성공 메시지 상수
    """

    POST_CREATE_SUCCESS = "게시글이 성공적으로 등록되었습니다."
    POST_DELETE_SUCCESS = "게시글이 삭제되었습니다."
