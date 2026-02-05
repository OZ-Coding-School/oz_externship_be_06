from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import parsers, serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from apps.posts.constants.comment_const import CommentErrorMessage
from apps.posts.exceptions.comment_exceptions import CommentNotFoundException
from apps.posts.models.post_comment import PostComment
from apps.posts.selectors.comment_selectors import CommentSelector
from apps.posts.serializers.comment_serializers import PostCommentListSerializer
from apps.posts.views.comment.comment_base_view import CommentBaseView


class PostCommentDetailAPIView(CommentBaseView):
    """
    댓글 상세 조회 API
    - GET /api/posts/<post_id>/comments/<comment_id>/ (posts:post-comment-update)
    - 누구나 접근 가능 (AllowAny)
    - 정상: 200 + 댓글 상세 정보 반환
    - 실패: 404 + error_detail (댓글 미존재, post_id 불일치)
    - 문서화: drf-spectacular @extend_schema 사용
    """

    permission_classes = [AllowAny]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]

    @extend_schema(
        tags=["Comments"],
        summary="댓글 상세 조회 API",
        description="댓글 ID(comment_id)로 특정 게시글(post_id)의 댓글 상세 정보를 조회합니다. 존재하지 않거나 게시글과 매칭되지 않으면 404 반환.",
        responses={
            200: PostCommentListSerializer(),
            404: inline_serializer(
                name="PostCommentDetail404",
                fields={"error_detail": serializers.CharField()},
            ),
        },
    )
    def get(self, request: Request, post_id: int, comment_id: int, *args: object, **kwargs: object) -> Response:
        """
        댓글 상세 조회 (GET)
        - 작성자/비작성자/비로그인 모두 접근 가능
        - 존재하지 않는 댓글/게시글이면 404 + error_detail
        - 정상 시 댓글 상세 정보 반환
        """
        try:
            # comment_id로 댓글 객체 조회 (존재하지 않으면 예외)
            comment = CommentSelector.get_comment_by_id(comment_id)
        except CommentNotFoundException as e:
            # 댓글이 없을 때 404 반환
            return Response(
                {
                    "error_detail": (
                        e.detail["error_detail"]
                        if isinstance(e.detail, dict) and "error_detail" in e.detail
                        else e.detail
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        # post_id와 comment.post_id가 일치하는지 체크 (데이터 무결성)
        if comment.post_id != post_id:
            return Response(
                {"error_detail": CommentErrorMessage.COMMENT_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        # 정상: 댓글 상세 정보 반환
        serializer = PostCommentListSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)
