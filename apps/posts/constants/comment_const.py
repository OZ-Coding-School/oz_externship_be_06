class CommentErrorMessage:
    """
    댓글 도메인 에러 메시지 상수
    """

    # 400 Bad Request
    FIELD_REQUIRED = "이 필드는 필수 항목입니다."
    CONTENT_EMPTY = "댓글 내용은 비어 있을 수 없습니다."

    # 401 Unauthorized
    UNAUTHORIZED = "자격 인증 데이터가 제공되지 않았습니다."

    # 403 Forbidden
    FORBIDDEN = "댓글에 대한 권한이 없습니다."

    # 404 Not Found
    COMMENT_NOT_FOUND = "해당 댓글을 찾을 수 없습니다."

    # 500 Internal Server Error
    SERVER_ERROR = "댓글 처리 중 서버 오류가 발생했습니다."


class CommentSuccessMessage:
    """
    댓글 도메인 성공 메시지 상수
    """

    COMMENT_CREATE_SUCCESS = "댓글이 성공적으로 등록되었습니다."
    COMMENT_UPDATE_SUCCESS = "댓글이 성공적으로 수정되었습니다."
    COMMENT_DELETE_SUCCESS = "댓글이 성공적으로 삭제되었습니다."
