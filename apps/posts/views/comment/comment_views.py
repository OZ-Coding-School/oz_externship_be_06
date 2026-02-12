from typing import Any

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, parsers, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.exceptions.comment_exceptions import CommentNotFoundException
from apps.posts.models import PostComment
from apps.posts.models.post import Post
from apps.posts.selectors.comment_selectors import CommentSelector
from apps.posts.serializers.comment_serializers import (
    PostCommentCreateSerializer,
    PostCommentListSerializer,
    PostCommentUpdateSerializer,
)
from apps.posts.services.comment.comment_create_services import create_comment
from apps.posts.services.comment.comment_delete_services import delete_comment
from apps.posts.services.comment.comment_nickname_services import (
    generate_comment_nickname,
)
from apps.posts.services.comment.comment_update_services import update_comment
from apps.posts.utils.pagination import PostPagination
from apps.posts.views.comment.comment_mixins import CommentExceptionHandlerMixin


# 댓글 작성(생성) View
class PostCommentCreateAPIView(CommentExceptionHandlerMixin, generics.CreateAPIView[PostComment]):
    """
    댓글 생성 API
    - POST /api/posts/<post_id>/comments/
    - 인증 필요 (IsAuthenticated)
    - 정상: 201 + detail 메시지
    - 실패: 400/401/404 + error_detail
    """

    serializer_class = PostCommentCreateSerializer
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Comments"],
        summary="커뮤니티 게시글 댓글 작성 API",
        request=PostCommentCreateSerializer,
        responses={
            201: inline_serializer(name="PostCommentCreate201", fields={"detail": serializers.CharField()}),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            post = Post.objects.get(id=kwargs["post_id"])
        except Post.DoesNotExist:
            raise CommentNotFoundException()

        # 데이터 검증
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 비즈니스 로직 실행 (댓글생성)
        create_comment(
            author=request.user,
            post=post,
            content=serializer.validated_data["content"],
        )

        # 응답반환
        return Response({"detail": "댓글이 등록되었습니다."}, status=status.HTTP_201_CREATED)

    # 댓글 상세조회 View


class PostCommentDetailAPIView(CommentExceptionHandlerMixin, generics.RetrieveAPIView[PostComment]):
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
    serializer_class = PostCommentListSerializer

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
        comment = CommentSelector.get_comment_by_id(comment_id)

        if not comment:
            # Mixin에서 잡아서 404 응답 반환
            raise CommentNotFoundException()

        if comment.post_id != post_id:
            raise CommentNotFoundException()

        serializer = self.get_serializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 댓글 수정 (update) View


class PostCommentUpdateAPIView(CommentExceptionHandlerMixin, generics.UpdateAPIView[PostComment]):
    """
    댓글 수정 API
    - PUT /api/posts/<post_id>/comments/<comment_id>/
    - 인증 + 작성자 권한 필요
    - 정상: 200 + 수정된 댓글 정보
    - 실패: 400/401/403/404 + error_detail
    - 문서화: drf-spectacular @extend_schema 사용
    """

    serializer_class = PostCommentUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]

    @extend_schema(
        tags=["Comments"],
        summary="댓글 수정 API",
        responses={
            200: inline_serializer(
                name="PostCommentUpdateResponse",
                fields={
                    "id": serializers.IntegerField(),
                    "content": serializers.CharField(),
                    "updated_at": serializers.DateTimeField(),
                },
            ),
        },
    )
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        댓글 수정 (PUT)
        - 인증 필요, 미인증 시 401
        - 작성자만 수정 가능, 아니면 403
        - 존재하지 않는 댓글이면 404
        - 유효성 오류 시 400
        - 정상 수정 시 200
        """

        comment_id = int(kwargs["comment_id"])
        comment = CommentSelector.get_comment_by_id(comment_id)

        if not comment:
            raise CommentNotFoundException()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_comment = update_comment(
            user=request.user,
            comment=comment,
            content=serializer.validated_data["content"],
        )

        return Response(
            {
                "id": updated_comment.id,
                "content": updated_comment.content,
                "updated_at": updated_comment.updated_at,
            },
            status=status.HTTP_200_OK,
        )

    # 댓글 삭제(delete) View


class PostCommentDeleteAPIView(CommentExceptionHandlerMixin, generics.DestroyAPIView[PostComment]):
    """
    댓글 삭제 API
    - DELETE /api/posts/<post_id>/comments/<comment_id>/
    - 인증 + 작성자 권한 필요
    - 정상: 200 + detail 메시지
    - 실패: 401/403/404 + error_detail
    - 문서화: drf-spectacular @extend_schema 사용
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Comments"],
        summary="댓글 삭제 API",
        responses={
            200: inline_serializer(name="PostCommentDelete200", fields={"detail": serializers.CharField()}),
        },
    )
    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        댓글 삭제 (DELETE)
        - 인증 필요, 미인증 시 401
        - 작성자만 삭제 가능, 아니면 403
        - 존재하지 않는 댓글이면 404
        - 정상 삭제 시 200
        """

        # comment_id로 댓글 객체 조회
        comment_id = int(kwargs["comment_id"])
        comment = CommentSelector.get_comment_by_id(comment_id)

        if not comment:
            # 예외처리는 Mixin에서 404 응답 반환
            raise CommentNotFoundException()

        # 삭제 서비스 실행
        delete_comment(request.user, comment)

        return Response({"detail": "댓글이 삭제되었습니다."}, status=status.HTTP_200_OK)

    # 랜덤 닉네임 생성


class CommentRandomNicknameAPIView(APIView):
    """
    댓글용 랜덤 닉네임을 반환하는 API
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Comments"],
        summary="댓글용 랜덤 닉네임 생성 API",
        description="댓글 작성 시 사용할 랜덤 닉네임을 생성하여 반환합니다.",
        responses={
            200: inline_serializer(name="CommentNicknameResponse", fields={"nickname": serializers.CharField()})
        },
    )
    def get(self, request: Request) -> Response:
        nickname = generate_comment_nickname()
        return Response({"nickname": nickname})


class PostCommentListAPIView(CommentExceptionHandlerMixin, generics.ListAPIView[PostComment]):
    """
    댓글 목록 조회 API
    GET /api/posts/<post_id>/comments/
    """

    pagination_class = PostPagination
    serializer_class = PostCommentListSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]

    def get_queryset(self) -> QuerySet[PostComment]:
        post_id = int(self.kwargs["post_id"])

        # 1. 게시글 존재 여부 확인
        if not PostComment.objects.filter(post_id=post_id).exists():
            raise CommentNotFoundException()

        # 2. 해당 게시글 댓글 목록 반환 -> Selector 활용
        return PostComment.objects.filter(post_id=post_id).order_by("-created_at")

    @extend_schema(
        operation_id="v1_post_comments_list",
        tags=["Comments"],
        summary="커뮤니티 게시글 댓글 목록 조회 API",
        responses={
            200: inline_serializer(
                name="PostCommentListPaginatedResponse",
                fields={
                    "count": serializers.IntegerField(),
                    "next": serializers.CharField(allow_null=True),
                    "previous": serializers.CharField(allow_null=True),
                    "results": PostCommentListSerializer(many=True),
                },
            ),
            404: inline_serializer(name="PostCommentList404", fields={"error_detail": serializers.CharField()}),
        },
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        댓글 목록 조회 (GET)
        게시글 유무에 따라 에러 반환 (Mixin)
        """
        return super().get(request, *args, **kwargs)
