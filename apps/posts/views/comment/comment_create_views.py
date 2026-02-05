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


class PostCommentCreateAPIView(generics.CreateAPIView[PostComment]):
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
        if not request.user or not request.user.is_authenticated:
            return Response({"error_detail": CommentErrorMessage.UNAUTHORIZED}, status=401)
        try:
            post = self._get_post()
        except CommentNotFoundException as e:
            return Response({"error_detail": str(e.detail)}, status=404)
        serializer = PostCommentCreateSerializer(
            data=request.data,
            context={**self.get_serializer_context(), "request": request, "post": post},
        )
        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=400)
        return Response({"detail": "댓글이 등록되었습니다."}, status=status.HTTP_201_CREATED)
