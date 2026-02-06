from typing import Any, Type

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, parsers, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.posts.constants.comment_const import CommentErrorMessage
from apps.posts.exceptions.comment_exceptions import CommentNotFoundException
from apps.posts.models.post import Post
from apps.posts.models.post_comment import PostComment
from apps.posts.serializers.comment_serializers import PostCommentCreateSerializer
from apps.posts.views.comment.comment_base_view import CommentBaseView


class PostCommentCreateAPIView(CommentBaseView, generics.CreateAPIView[PostComment]):
    """
    댓글 생성 API
    - POST /api/posts/<post_id>/comments/
    - 인증 필요 (IsAuthenticated)
    - 정상: 201 + detail 메시지
    - 실패: 400/401/404 + error_detail
    """

    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]
    permission_classes = [IsAuthenticated]

    def _get_post(self) -> Post:
        post_id = self.kwargs.get("post_id")
        try:
            return Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise CommentNotFoundException()

    def get_serializer_class(self) -> Type[serializers.Serializer[PostComment]]:
        return PostCommentCreateSerializer

    def get_serializer_context(self) -> dict[str, Any]:
        ctx = super().get_serializer_context()
        ctx["post"] = self._get_post()
        return ctx

    @extend_schema(
        tags=["Comments"],
        summary="커뮤니티 게시글 댓글 작성 API",
        request=PostCommentCreateSerializer,
        responses={
            201: inline_serializer(name="PostCommentCreate201", fields={"detail": serializers.CharField()}),
            400: inline_serializer(name="PostCommentCreate400", fields={"error_detail": serializers.DictField()}),
            401: inline_serializer(name="PostCommentCreate401", fields={"error_detail": serializers.CharField()}),
            404: inline_serializer(name="PostCommentCreate404", fields={"error_detail": serializers.CharField()}),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        댓글 생성 (POST)
        - 인증 필요, 미인증 시 401
        - 존재하지 않는 게시글이면 404
        - 유효성 오류 시 400
        - 정상 등록 시 201
        """
        try:
            # post_id로 게시글 객체 조회 (없으면 예외)
            post = self._get_post()
        except CommentNotFoundException as e:
            # 게시글이 없을 때 404 반환
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
        serializer = PostCommentCreateSerializer(
            data=request.data,
            context={**self.get_serializer_context(), "request": request, "post": post},
        )
        if not serializer.is_valid():
            # 유효성 검사 실패 시 400
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        # 실제 DB에 댓글 저장
        serializer.save(author=request.user, post=post)
        return Response({"detail": "댓글이 등록되었습니다."}, status=status.HTTP_201_CREATED)
